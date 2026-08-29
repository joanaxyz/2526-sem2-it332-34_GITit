from __future__ import annotations

import copy

from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import PermissionDenied, ValidationError

from authoring.compiler import ContentRuntimeCompiler
from authoring.models import (
    STATUS_PUBLISHED,
    STATUS_TESTABLE,
    AuthoringChapter,
    ContentDefinition,
)
from authoring.validators import ContentDefinitionValidator


class AuthoringChapterService:
    _FIELDS = (
        "slug",
        "title",
        "summary",
        "sort_order",
    )

    def assert_owner(self, *, user, chapter: AuthoringChapter) -> None:
        if not getattr(user, "is_staff", False) and chapter.owner_id != getattr(user, "id", None):
            raise PermissionDenied("You do not own this chapter.")

    @transaction.atomic
    def create(self, *, user, data: dict) -> AuthoringChapter:
        fields = {key: data[key] for key in self._FIELDS if key in data}
        fields.setdefault("title", "New chapter")
        fields.setdefault(
            "slug", _unique_chapter_slug(user=user, base=fields.get("slug") or fields["title"])
        )
        if "sort_order" not in fields:
            fields["sort_order"] = AuthoringChapter.objects.filter(owner=user).count()
        chapter = AuthoringChapter(owner=user, **fields)
        chapter.full_clean()
        chapter.save()
        return chapter

    @transaction.atomic
    def update(self, *, user, chapter: AuthoringChapter, data: dict) -> AuthoringChapter:
        self.assert_owner(user=user, chapter=chapter)
        for field in self._FIELDS:
            if field in data:
                setattr(chapter, field, data[field])
        chapter.full_clean()
        chapter.save()
        return chapter

    @transaction.atomic
    def delete(self, *, user, chapter: AuthoringChapter) -> None:
        self.assert_owner(user=user, chapter=chapter)
        chapter.delete()  # content.chapter FK is SET_NULL, so content survives orphaned


class ContentDefinitionService:
    def assert_owner(self, *, user, content: ContentDefinition) -> None:
        if not getattr(user, "is_staff", False) and content.owner_id != getattr(user, "id", None):
            raise PermissionDenied("You do not own this content definition.")

    @transaction.atomic
    def create(self, *, user, data: dict) -> ContentDefinition:
        content = ContentDefinition(owner=user, **_content_fields(data))
        _validate_chapter_choice(data)
        _apply_chapter_choice(user=user, content=content, data=data)
        if content.official_chapter_id:
            _assert_official_content_owner(content)
        content.full_clean()
        content.save()
        if content.official_chapter_id:
            _record_official_action(
                actor=user,
                action="official_content.create",
                content=content,
                after=_official_content_snapshot(content),
            )
        return content

    @transaction.atomic
    def update(self, *, user, content: ContentDefinition, data: dict) -> ContentDefinition:
        self.assert_owner(user=user, content=content)
        before = _official_content_snapshot(content)
        was_official = content.official_chapter_id is not None
        if content.status == STATUS_PUBLISHED:
            forbidden = set(data) - {"visibility"}
            if forbidden:
                raise ValidationError(
                    {
                        "status": "Published content can only change visibility or be remixed; its definition is immutable."
                    }
                )
        for field, value in _content_fields(data, partial=True).items():
            setattr(content, field, value)
        _validate_chapter_choice(data)
        _apply_chapter_choice(user=user, content=content, data=data)
        if content.official_chapter_id:
            _assert_official_content_owner(content)
        content.full_clean()
        content.save()
        if was_official or content.official_chapter_id:
            _record_official_action(
                actor=user,
                action="official_content.update",
                content=content,
                before=before,
                after=_official_content_snapshot(content),
            )
        return content

    @transaction.atomic
    def validate(self, *, user, content: ContentDefinition) -> dict:
        self.assert_owner(user=user, content=content)
        result = ContentDefinitionValidator().validate(content)
        content.validation_errors = result.errors
        if result.valid and content.status not in {STATUS_TESTABLE, STATUS_PUBLISHED}:
            content.status = STATUS_TESTABLE
            content.save(update_fields=["validation_errors", "status", "updated_at"])
        else:
            content.save(update_fields=["validation_errors", "updated_at"])
        return {"valid": result.valid, "errors": result.errors}

    @transaction.atomic
    def publish(self, *, user, content: ContentDefinition) -> ContentDefinition:
        self.assert_owner(user=user, content=content)
        before = _official_content_snapshot(content)
        if content.official_chapter_id:
            _assert_official_content_owner(content)
            _assert_publishable_official_chapter(content.official_chapter)
        result = ContentDefinitionValidator().validate(content)
        if not result.valid:
            content.validation_errors = result.errors
            content.save(update_fields=["validation_errors", "updated_at"])
            raise ValidationError({"validation_errors": result.errors})
        content.status = STATUS_PUBLISHED
        if content.official_chapter_id:
            content.visibility = "public"
        content.validation_errors = []
        content.published_at = timezone.now()
        content.save(
            update_fields=[
                "status",
                "visibility",
                "validation_errors",
                "published_at",
                "updated_at",
            ]
        )
        runtime = ContentRuntimeCompiler().compile(content=content)
        if content.official_chapter_id:
            _record_official_action(
                actor=user,
                action="official_content.publish",
                content=content,
                before=before,
                after=_official_content_snapshot(content),
                metadata={
                    "runtime_id": runtime.id,
                    "chapter_id": runtime.chapter_id,
                },
            )
        return content

    @transaction.atomic
    def test_run(self, *, user, content: ContentDefinition) -> dict:
        self.assert_owner(user=user, content=content)
        if content.official_chapter_id:
            raise ValidationError(
                {
                    "official_chapter": (
                        "Official content must be published before it enters the live curriculum."
                    )
                }
            )
        result = ContentDefinitionValidator().validate(content)
        if not result.valid:
            content.validation_errors = result.errors
            content.save(update_fields=["validation_errors", "updated_at"])
            raise ValidationError({"validation_errors": result.errors})
        if content.status != STATUS_PUBLISHED:
            content.status = STATUS_TESTABLE
            content.validation_errors = []
            content.save(update_fields=["status", "validation_errors", "updated_at"])
        runtime = ContentRuntimeCompiler().compile(content=content)
        return _runtime_entry(runtime)

    @transaction.atomic
    def remix(self, *, user, content: ContentDefinition) -> ContentDefinition:
        clone = ContentDefinition.objects.create(
            kind=content.kind,
            owner=user,
            source_definition=content,
            chapter=content.chapter
            if content.chapter_id and content.chapter.owner_id == user.id
            else None,
            visibility="private",
            status="draft",
            slug=_next_remix_slug(user=user, source=content),
            title=f"{content.title} Remix",
            summary=content.summary,
            tags=copy.deepcopy(content.tags),
            command_family=content.command_family,
            difficulty=content.difficulty,
            definition=copy.deepcopy(content.definition),
        )
        return clone


def _resolve_chapter(*, user, chapter_id) -> AuthoringChapter | None:
    if not chapter_id:
        return None
    try:
        return AuthoringChapter.objects.get(id=chapter_id, owner=user)
    except AuthoringChapter.DoesNotExist as exc:
        raise ValidationError({"chapter": "Unknown chapter."}) from exc


def _apply_chapter_choice(*, user, content: ContentDefinition, data: dict) -> None:
    authored_chapter_id = data.get("chapter")
    if authored_chapter_id is not None:
        content.chapter = _resolve_chapter(user=user, chapter_id=authored_chapter_id)
        content.official_chapter = None
    elif "official_chapter" in data:
        content.official_chapter = _resolve_official_chapter(
            user=user,
            chapter_id=data.get("official_chapter"),
        )
        content.chapter = None
    elif "chapter" in data:
        content.chapter = None
        content.official_chapter = None


def _resolve_official_chapter(*, user, chapter_id):
    if chapter_id is None:
        return None
    if not getattr(user, "is_staff", False):
        raise PermissionDenied("Only staff can place content in the official curriculum.")
    from curriculum.models import MANAGEMENT_SOURCE_RUNTIME, Chapter

    try:
        chapter = (
            Chapter.objects.exclude(management_source=MANAGEMENT_SOURCE_RUNTIME)
            .select_related("story")
            .get(id=chapter_id)
        )
    except Chapter.DoesNotExist as exc:
        raise ValidationError({"official_chapter": "Unknown official chapter."}) from exc
    _assert_publishable_official_chapter(chapter)
    return chapter


def _assert_publishable_official_chapter(chapter) -> None:
    if not chapter.is_published or chapter.story_id is None or not chapter.story.is_published:
        raise ValidationError(
            {
                "official_chapter": (
                    "Official content requires a published chapter in a published story."
                )
            }
        )


def _assert_official_content_owner(content: ContentDefinition) -> None:
    if content.owner_id is not None and not content.owner.is_staff:
        raise ValidationError(
            {
                "official_chapter": (
                    "Player-authored content cannot be moved into the official curriculum."
                )
            }
        )


def _official_content_snapshot(content: ContentDefinition) -> dict:
    return {
        "kind": content.kind,
        "slug": content.slug,
        "title": content.title,
        "visibility": content.visibility,
        "status": content.status,
        "official_chapter_id": content.official_chapter_id,
    }


def _record_official_action(
    *,
    actor,
    action: str,
    content: ContentDefinition,
    before: dict | None = None,
    after: dict | None = None,
    metadata: dict | None = None,
) -> None:
    from adminconsole.services.actions import record_admin_action

    record_admin_action(
        actor=actor,
        action=action,
        target=content,
        before=before,
        after=after,
        metadata=metadata,
    )


def _validate_chapter_choice(data: dict) -> None:
    if data.get("chapter") and data.get("official_chapter"):
        raise ValidationError(
            {"official_chapter": "Choose an authored chapter or an official chapter, not both."}
        )


def _unique_chapter_slug(*, user, base: str) -> str:
    from django.utils.text import slugify

    root = slugify(base) or "chapter"
    slug = root
    index = 2
    while AuthoringChapter.objects.filter(owner=user, slug=slug).exists():
        slug = f"{root}-{index}"
        index += 1
    return slug


def _content_fields(data: dict, *, partial: bool = False) -> dict:
    allowed = {
        "kind",
        "visibility",
        "slug",
        "title",
        "summary",
        "tags",
        "command_family",
        "difficulty",
        "definition",
    }
    fields = {key: data[key] for key in allowed if key in data}
    if not partial:
        fields.setdefault("summary", "")
        fields.setdefault("tags", [])
        fields.setdefault("command_family", "")
        fields.setdefault("difficulty", "")
        fields.setdefault("definition", {})
    return fields


def _runtime_entry(runtime) -> dict:
    if runtime.adventure_id:
        level = runtime.adventure
        return {
            "kind": "adventure",
            "runtime_id": runtime.adventure_id,
            "start_path": f"/adventure-levels/{level.id}" if level else None,
        }
    if runtime.challenge_id:
        level = runtime.challenge
        first_trial = (
            level.trials.filter(is_published=True).order_by("difficulty", "id").first()
            if level
            else None
        )
        return {
            "kind": "challenge",
            "runtime_id": runtime.challenge_id,
            "start_path": f"/challenge-trials/{first_trial.id}" if first_trial else None,
        }
    if runtime.lesson_id:
        return {"kind": "lesson", "runtime_id": runtime.lesson_id, "pages": runtime.lesson.pages}
    return {"kind": "unknown", "runtime_id": None}


def _next_remix_slug(*, user, source: ContentDefinition) -> str:
    base = f"{source.slug}-remix"
    slug = base
    index = 2
    while ContentDefinition.objects.filter(owner=user, kind=source.kind, slug=slug).exists():
        slug = f"{base}-{index}"
        index += 1
    return slug
