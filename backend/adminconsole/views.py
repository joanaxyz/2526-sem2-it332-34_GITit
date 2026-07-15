"""Staff-only admin console REST endpoints.

The platform's data-management surface for staff: a dashboard, user management,
and the GitCoin economy. Asset + shop-listing management reuse the existing
assets/shop endpoints (also staff-gated). Every view here is gated by
:class:`common.permissions.IsStaff`.
"""

from __future__ import annotations

from datetime import timedelta

from django.contrib.auth import get_user_model
from django.db.models import Count, Sum
from django.utils import timezone
from drf_spectacular.utils import OpenApiTypes, extend_schema
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from adminconsole.models import FeatureFlag
from adminconsole.selectors import (
    chapter_payload,
    content_payload,
    flag_payload,
    story_payload,
    user_brief,
    user_detail,
)
from adminconsole.services import AdminEconomyService, story_difficulty, story_prerequisite
from adventures.models import AdventureRun
from authoring.models import STATUS_PUBLISHED as CONTENT_PUBLISHED
from authoring.models import ContentDefinition
from common.constants import PLAN_SIGNUP_GRANT
from common.permissions import IsStaff
from curriculum.models import Chapter, Story
from players.services import get_or_create_player
from progress.models import CoinTransaction, Wallet
from progress.selectors import total_adventure_level_completions, total_challenge_trial_completions
from progress.wallet import WalletService

User = get_user_model()


class AdminOverviewAPIView(APIView):
    permission_classes = [IsStaff]

    @extend_schema(responses={200: OpenApiTypes.OBJECT})
    def get(self, request):
        now = timezone.now()
        week_ago = now - timedelta(days=7)
        month_ago = now - timedelta(days=30)

        total_users = User.objects.count()

        coins_in_circulation = Wallet.objects.aggregate(total=Sum("balance"))["total"] or 0
        spent = (
            CoinTransaction.objects.filter(amount__lt=0).aggregate(total=Sum("amount"))["total"] or 0
        )
        return Response(
            {
                "users": {
                    "total": total_users,
                    "new_7d": User.objects.filter(date_joined__gte=week_ago).count(),
                    "new_30d": User.objects.filter(date_joined__gte=month_ago).count(),
                },
                "economy": {
                    "coins_in_circulation": coins_in_circulation,
                    "coins_spent": abs(spent),
                    "signup_grant": PLAN_SIGNUP_GRANT,
                },
                "recent_signups": [
                    user_brief(u)
                    for u in User.objects.order_by("-date_joined")[:5]
                ],
                "recent_purchases": [
                    {
                        "user_id": t.player.user_id,
                        "amount": t.amount,
                        "reason": t.reason,
                        "created_at": t.created_at,
                    }
                    for t in CoinTransaction.objects.filter(reason__in=["shop_purchase", "cosmetic_purchase"])
                    .select_related("player")
                    .order_by("-id")[:5]
                ],
            }
        )


class AdminUserListAPIView(APIView):
    permission_classes = [IsStaff]

    @extend_schema(responses={200: OpenApiTypes.OBJECT})
    def get(self, request):
        queryset = User.objects.all().order_by("-date_joined")
        query = (request.query_params.get("q") or "").strip()
        if query:
            from django.db.models import Q

            queryset = queryset.filter(Q(username__icontains=query) | Q(email__icontains=query))
        return Response({"results": [user_brief(u) for u in queryset[:100]]})


class AdminUserDetailAPIView(APIView):
    permission_classes = [IsStaff]

    @extend_schema(responses={200: OpenApiTypes.OBJECT})
    def get(self, request, user_id: int):
        return Response(user_detail(_get_user_or_404(user_id)))


class AdminUserActionAPIView(APIView):
    """Run a staff action on a user: grant/deduct coins, toggle staff or
    active. One action per call via the ``action`` field."""

    permission_classes = [IsStaff]

    @extend_schema(request=OpenApiTypes.OBJECT, responses={200: OpenApiTypes.OBJECT})
    def post(self, request, user_id: int):
        target = _get_user_or_404(user_id)
        action = (request.data.get("action") or "").strip()
        if action == "grant_coins":
            player = get_or_create_player(target)
            AdminEconomyService().adjust(
                player=player,
                amount=request.data.get("amount"),
                reason=request.data.get("reason"),
            )
        elif action == "set_staff":
            target.is_staff = _as_bool(request.data.get("value"))
            target.save(update_fields=["is_staff"])
        elif action == "set_active":
            target.is_active = _as_bool(request.data.get("value"))
            target.save(update_fields=["is_active"])
        else:
            raise ValidationError({"action": f"Unknown action '{action}'."})
        return Response(user_detail(target))


class AdminTransactionListAPIView(APIView):
    permission_classes = [IsStaff]

    @extend_schema(responses={200: OpenApiTypes.OBJECT})
    def get(self, request):
        queryset = CoinTransaction.objects.select_related("player__user").order_by("-id")
        user_id = request.query_params.get("user_id")
        if user_id:
            queryset = queryset.filter(player__user_id=user_id)
        return Response(
            {
                "results": [
                    {
                        "id": t.id,
                        "user_id": t.player.user_id,
                        "username": t.player.user.username,
                        "amount": t.amount,
                        "reason": t.reason,
                        "created_at": t.created_at,
                    }
                    for t in queryset[:200]
                ]
            }
        )


class AdminEconomyAdjustAPIView(APIView):
    permission_classes = [IsStaff]

    @extend_schema(request=OpenApiTypes.OBJECT, responses={200: OpenApiTypes.OBJECT})
    def post(self, request):
        target = _get_user_or_404(request.data.get("user_id"))
        player = get_or_create_player(target)
        AdminEconomyService().adjust(
            player=player,
            amount=request.data.get("amount"),
            reason=request.data.get("reason"),
        )
        return Response({"wallet": WalletService().summary(player=player)})


# --- helpers ---------------------------------------------------------------


def _get_user_or_404(user_id) -> User:
    try:
        return User.objects.get(pk=user_id)
    except (User.DoesNotExist, ValueError, TypeError) as exc:
        raise NotFound("User not found.") from exc


def _as_bool(value) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


# --- Curriculum & Stories --------------------------------------------------


class AdminStoryListCreateAPIView(APIView):
    permission_classes = [IsStaff]

    @extend_schema(responses={200: OpenApiTypes.OBJECT})
    def get(self, request):
        stories = Story.objects.all().order_by("sort_order", "id")
        counts = {
            row["story"]: row["n"]
            for row in Chapter.objects.values("story").annotate(n=Count("id"))
        }
        return Response({"results": [story_payload(s, counts.get(s.id, 0)) for s in stories]})

    @extend_schema(request=OpenApiTypes.OBJECT, responses={200: OpenApiTypes.OBJECT})
    def post(self, request):
        data = request.data
        slug = (data.get("slug") or "").strip()
        title = (data.get("title") or "").strip()
        if not slug or not title:
            raise ValidationError({"detail": "slug and title are required."})
        if Story.objects.filter(slug=slug).exists():
            raise ValidationError({"slug": "A story with this slug already exists."})
        story = Story.objects.create(
            slug=slug,
            title=title,
            summary=(data.get("summary") or "").strip(),
            price=_safe_int(data.get("price"), default=0),
            world_slug=(data.get("world_slug") or slug).strip(),
            difficulty=story_difficulty(
                data.get("difficulty"),
                default=Story.DIFFICULTY_BEGINNER,
            ),
            prerequisite_story=story_prerequisite(data.get("prerequisite_story")),
            sort_order=_safe_int(data.get("sort_order"), default=Story.objects.count() + 1),
            is_published=_as_bool(data.get("is_published")) if "is_published" in data else True,
        )
        return Response(story_payload(story, 0), status=201)


class AdminStoryDetailAPIView(APIView):
    permission_classes = [IsStaff]

    @extend_schema(request=OpenApiTypes.OBJECT, responses={200: OpenApiTypes.OBJECT})
    def patch(self, request, story_id: int):
        story = _get_or_404(Story, story_id, "Story not found.")
        data = request.data
        if "title" in data:
            story.title = (data.get("title") or "").strip() or story.title
        if "summary" in data:
            story.summary = (data.get("summary") or "").strip()
        if "price" in data:
            story.price = _safe_int(data.get("price"), default=story.price)
        if "world_slug" in data:
            story.world_slug = (data.get("world_slug") or "").strip() or story.world_slug
        if "difficulty" in data:
            story.difficulty = story_difficulty(data.get("difficulty"), default=story.difficulty)
        if "prerequisite_story" in data:
            story.prerequisite_story = story_prerequisite(
                data.get("prerequisite_story"),
                story=story,
            )
        if "sort_order" in data:
            story.sort_order = _safe_int(data.get("sort_order"), default=story.sort_order)
        if "is_published" in data:
            story.is_published = _as_bool(data.get("is_published"))
        story.save()
        return Response(story_payload(story, story.chapters.count()))


class AdminChapterListAPIView(APIView):
    permission_classes = [IsStaff]

    @extend_schema(responses={200: OpenApiTypes.OBJECT})
    def get(self, request):
        chapters = Chapter.objects.all().order_by("sort_order", "number")
        story_id = request.query_params.get("story")
        if story_id:
            chapters = chapters.filter(story_id=story_id)
        return Response({"results": [chapter_payload(c) for c in chapters]})


class AdminChapterDetailAPIView(APIView):
    permission_classes = [IsStaff]

    @extend_schema(request=OpenApiTypes.OBJECT, responses={200: OpenApiTypes.OBJECT})
    def patch(self, request, chapter_id: int):
        chapter = _get_or_404(Chapter, chapter_id, "Chapter not found.")
        data = request.data
        if "title" in data:
            chapter.title = (data.get("title") or "").strip() or chapter.title
        if "description" in data:
            chapter.description = data.get("description") or ""
        if "is_published" in data:
            chapter.is_published = _as_bool(data.get("is_published"))
        if "is_playable" in data:
            chapter.is_playable = _as_bool(data.get("is_playable"))
        if "sort_order" in data:
            chapter.sort_order = _safe_int(data.get("sort_order"), default=chapter.sort_order)
        chapter.save()
        return Response(chapter_payload(chapter))


# --- Official content (authoring) ------------------------------------------


class AdminContentListAPIView(APIView):
    """Official content definitions: staff-authored (or owner-less) adventures,
    challenges, and lessons. Create/edit happens in the existing level editor."""

    permission_classes = [IsStaff]

    @extend_schema(responses={200: OpenApiTypes.OBJECT})
    def get(self, request):
        from django.db.models import Q

        contents = (
            ContentDefinition.objects.filter(Q(owner__isnull=True) | Q(owner__is_staff=True))
            .order_by("-updated_at")[:200]
        )
        kind = request.query_params.get("kind")
        if kind:
            contents = [c for c in contents if c.kind == kind]
        return Response({"results": [content_payload(c) for c in contents]})


# --- Analytics -------------------------------------------------------------


class AdminAnalyticsAPIView(APIView):
    permission_classes = [IsStaff]

    @extend_schema(responses={200: OpenApiTypes.OBJECT})
    def get(self, request):
        now = timezone.now()
        month_ago = now - timedelta(days=30)

        runs_by_status = {
            row["status"]: row["n"]
            for row in AdventureRun.objects.values("status").annotate(n=Count("id"))
        }
        total_runs = sum(runs_by_status.values())
        passed = AdventureRun.objects.filter(passed_at__isnull=False).count()
        active = (
            AdventureRun.objects.filter(started_at__gte=month_ago)
            .values("player")
            .distinct()
            .count()
        )

        per_story = []
        story_runs = {
            row["level__chapter__story_id"]: row["n"]
            for row in AdventureRun.objects.values("level__chapter__story_id").annotate(n=Count("id"))
        }
        story_passed = {
            row["level__chapter__story_id"]: row["n"]
            for row in AdventureRun.objects.filter(passed_at__isnull=False)
            .values("level__chapter__story_id")
            .annotate(n=Count("id"))
        }
        for story in Story.objects.all().order_by("sort_order", "id"):
            per_story.append(
                {
                    "slug": story.slug,
                    "title": story.title,
                    "runs": story_runs.get(story.id, 0),
                    "passed": story_passed.get(story.id, 0),
                }
            )

        return Response(
            {
                "runs": {"by_status": runs_by_status, "total": total_runs, "passed": passed},
                "completions": {
                    "adventure": total_adventure_level_completions(),
                    "challenge": total_challenge_trial_completions(),
                    "total": total_adventure_level_completions() + total_challenge_trial_completions(),
                },
                "active_learners_30d": active,
                "per_story": per_story,
            }
        )


# --- Moderation ------------------------------------------------------------


class AdminModerationListAPIView(APIView):
    """Shared player-generated content: public published content definitions."""

    permission_classes = [IsStaff]

    @extend_schema(responses={200: OpenApiTypes.OBJECT})
    def get(self, request):
        contents = (
            ContentDefinition.objects.filter(visibility="public", status=CONTENT_PUBLISHED, owner__is_staff=False)
            .select_related("owner")
            .order_by("-updated_at")[:200]
        )
        return Response(
            {
                "content": [
                    {
                        "id": c.id,
                        "kind": c.kind,
                        "title": c.title,
                        "owner": c.owner.username if c.owner else None,
                        "updated_at": c.updated_at,
                    }
                    for c in contents
                ],
            }
        )


class AdminModerationUnpublishAPIView(APIView):
    permission_classes = [IsStaff]

    @extend_schema(request=OpenApiTypes.OBJECT, responses={200: OpenApiTypes.OBJECT})
    def post(self, request):
        kind = (request.data.get("kind") or "").strip()
        item_id = request.data.get("id")
        if kind == "content":
            content = _get_or_404(ContentDefinition, item_id, "Content not found.")
            content.visibility = "private"
            content.status = "draft"
            content.save(update_fields=["visibility", "status", "updated_at"])
        else:
            raise ValidationError({"kind": "kind must be 'content'."})
        return Response({"ok": True})


# --- Settings --------------------------------------------------------------


class AdminSettingsAPIView(APIView):
    permission_classes = [IsStaff]

    @extend_schema(responses={200: OpenApiTypes.OBJECT})
    def get(self, request):
        return Response(
            {
                "feature_flags": [flag_payload(f) for f in FeatureFlag.objects.all()],
            }
        )

    @extend_schema(request=OpenApiTypes.OBJECT, responses={200: OpenApiTypes.OBJECT})
    def post(self, request):
        """Upsert + toggle a feature flag by key."""
        key = (request.data.get("key") or "").strip()
        if not key:
            raise ValidationError({"key": "A flag key is required."})
        flag, _created = FeatureFlag.objects.get_or_create(
            key=key,
            defaults={"label": (request.data.get("label") or key).strip()},
        )
        if "label" in request.data:
            flag.label = (request.data.get("label") or flag.label).strip()
        if "description" in request.data:
            flag.description = request.data.get("description") or ""
        if "enabled" in request.data:
            flag.enabled = _as_bool(request.data.get("enabled"))
        flag.save()
        return Response(flag_payload(flag))


# --- payload + small helpers -----------------------------------------------


def _get_or_404(model, pk, message):
    obj = model.objects.filter(pk=pk).first()
    if obj is None:
        raise NotFound(message)
    return obj


def _safe_int(value, *, default: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default
