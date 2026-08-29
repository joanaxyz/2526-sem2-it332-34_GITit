"""Staff-only admin console API: access gating + key data actions."""

import uuid

import pytest
from rest_framework.test import APIClient

from adminconsole.models import AdminActionLog
from adminconsole.tests.helpers import make_user
from players.models import Player
from players.services import get_or_create_player
from progress.wallet import WalletService


@pytest.mark.django_db
def test_overview_requires_staff(django_user_model):
    student = make_user(django_user_model, "student")
    client = APIClient()
    client.force_authenticate(user=student)
    assert client.get("/api/admin/overview/").status_code == 403


@pytest.mark.django_db
def test_staff_overview_returns_metrics(django_user_model):
    staff = make_user(django_user_model, "admin", is_staff=True)
    client = APIClient()
    client.force_authenticate(user=staff)

    response = client.get("/api/admin/overview/")
    assert response.status_code == 200
    body = response.json()
    assert set(body) >= {"users", "economy"}
    assert body["users"]["total"] >= 1


@pytest.mark.django_db
def test_overview_counts_only_shop_spend_and_lists_activity(django_user_model):
    staff = make_user(django_user_model, "admin", is_staff=True)
    target = make_user(django_user_model, "target")
    player = get_or_create_player(target)
    wallet = WalletService()
    wallet.award(player=player, amount=500, reason="test_seed", award_key="overview-seed")
    wallet.spend(
        player=player,
        amount=50,
        reason="admin_adjust",
        award_key="overview-admin-deduction",
    )
    wallet.spend(
        player=player,
        amount=100,
        reason="shop_purchase",
        award_key="overview-shop-purchase",
    )
    AdminActionLog.objects.create(
        actor=staff,
        action="user.set_active",
        target_type="auth.user",
        target_id=str(target.id),
        target_label=target.username,
    )
    client = APIClient()
    client.force_authenticate(user=staff)

    body = client.get("/api/admin/overview/").json()

    assert body["economy"]["coins_spent"] == 100
    assert body["recent_purchases"][0]["username"] == target.username
    assert body["recent_purchases"][0]["amount"] == -100
    assert body["recent_admin_actions"][0]["action"] == "user.set_active"


@pytest.mark.django_db
def test_staff_economy_adjust(django_user_model):
    staff = make_user(django_user_model, "admin", is_staff=True)
    target = make_user(django_user_model, "target")
    client = APIClient()
    client.force_authenticate(user=staff)

    response = client.post(
        "/api/admin/economy/adjust/",
        {
            "user_id": target.id,
            "amount": 250,
            "reason": "goodwill",
            "request_id": str(uuid.uuid4()),
        },
        format="json",
    )
    assert response.status_code == 200
    assert response.json()["wallet"]["balance"] == 250


@pytest.mark.django_db
def test_non_staff_cannot_adjust_coins(django_user_model):
    student = make_user(django_user_model, "student")
    target = make_user(django_user_model, "target")
    client = APIClient()
    client.force_authenticate(user=student)

    response = client.post(
        "/api/admin/economy/adjust/",
        {
            "user_id": target.id,
            "amount": 250,
            "reason": "unauthorized",
            "request_id": str(uuid.uuid4()),
        },
        format="json",
    )
    assert response.status_code == 403
    assert WalletService().summary(player=get_or_create_player(target))["balance"] == 0


@pytest.mark.django_db
def test_economy_adjust_is_idempotent_and_audited_once(django_user_model):
    from progress.models import CoinTransaction

    staff = make_user(django_user_model, "admin", is_staff=True)
    target = make_user(django_user_model, "target")
    request_id = str(uuid.uuid4())
    client = APIClient()
    client.force_authenticate(user=staff)
    payload = {
        "user_id": target.id,
        "amount": 250,
        "reason": "support_adjustment",
        "request_id": request_id,
    }

    first = client.post("/api/admin/economy/adjust/", payload, format="json")
    retry = client.post("/api/admin/economy/adjust/", payload, format="json")

    assert first.status_code == 200
    assert first.json() == {"wallet": {"balance": 250}, "applied": True}
    assert retry.status_code == 200
    assert retry.json() == {"wallet": {"balance": 250}, "applied": False}
    player = get_or_create_player(target)
    assert CoinTransaction.objects.filter(player=player).count() == 1
    log = AdminActionLog.objects.get(action="economy.adjust")
    assert log.request_id == request_id
    assert log.before == {"wallet": {"balance": 0}}
    assert log.after == {"wallet": {"balance": 250}}


@pytest.mark.django_db
def test_user_detail_is_read_only_for_accounts_without_player(django_user_model):
    staff = make_user(django_user_model, "admin", is_staff=True)
    target = make_user(django_user_model, "target")
    client = APIClient()
    client.force_authenticate(user=staff)

    response = client.get(f"/api/admin/users/{target.id}/")

    assert response.status_code == 200
    assert response.json()["wallet"] == {"balance": 0}
    assert response.json()["entitlement_count"] == 0
    assert not Player.objects.filter(user=target).exists()


@pytest.mark.django_db
def test_staff_can_change_another_users_admin_and_active_state_with_audit(
    django_user_model,
):
    staff = make_user(django_user_model, "admin", is_staff=True)
    target = make_user(django_user_model, "target")
    client = APIClient()
    client.force_authenticate(user=staff)

    promoted = client.post(
        f"/api/admin/users/{target.id}/actions/",
        {"action": "set_staff", "value": True},
        format="json",
    )
    disabled = client.post(
        f"/api/admin/users/{target.id}/actions/",
        {"action": "set_active", "value": False},
        format="json",
    )

    assert promoted.status_code == 200
    assert disabled.status_code == 200
    target.refresh_from_db()
    assert target.is_staff is True
    assert target.is_active is False
    logs = list(AdminActionLog.objects.filter(actor=staff, target_id=str(target.id)))
    assert {log.action for log in logs} == {"user.set_staff", "user.set_active"}
    assert any(
        log.before == {"is_staff": False} and log.after == {"is_staff": True} for log in logs
    )
    assert any(
        log.before == {"is_active": True} and log.after == {"is_active": False} for log in logs
    )


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("action", "message"),
    [
        ("set_staff", "You cannot revoke your own admin access."),
        ("set_active", "You cannot disable your own account."),
    ],
)
def test_staff_cannot_lock_out_their_own_account(django_user_model, action, message):
    staff = make_user(django_user_model, "admin", is_staff=True)
    client = APIClient()
    client.force_authenticate(user=staff)

    response = client.post(
        f"/api/admin/users/{staff.id}/actions/",
        {"action": action, "value": False},
        format="json",
    )

    assert response.status_code == 400
    assert message in str(response.json()["value"])
    staff.refresh_from_db()
    assert staff.is_staff is True
    assert staff.is_active is True
    assert AdminActionLog.objects.count() == 0


@pytest.mark.django_db
def test_user_action_rejects_malformed_boolean_without_mutating(django_user_model):
    staff = make_user(django_user_model, "admin", is_staff=True)
    target = make_user(django_user_model, "target")
    client = APIClient()
    client.force_authenticate(user=staff)

    response = client.post(
        f"/api/admin/users/{target.id}/actions/",
        {"action": "set_staff", "value": "definitely"},
        format="json",
    )

    assert response.status_code == 400
    target.refresh_from_db()
    assert target.is_staff is False
    assert AdminActionLog.objects.count() == 0


@pytest.mark.django_db
def test_non_staff_cannot_read_or_mutate_admin_users(django_user_model):
    student = make_user(django_user_model, "student")
    target = make_user(django_user_model, "target")
    client = APIClient()
    client.force_authenticate(user=student)

    assert client.get("/api/admin/users/").status_code == 403
    assert client.get(f"/api/admin/users/{target.id}/").status_code == 403
    assert (
        client.post(
            f"/api/admin/users/{target.id}/actions/",
            {"action": "set_staff", "value": True},
            format="json",
        ).status_code
        == 403
    )
    target.refresh_from_db()
    assert target.is_staff is False


@pytest.mark.django_db
def test_staff_can_create_and_edit_story(django_user_model):
    from curriculum.models import MANAGEMENT_SOURCE_ADMIN, Chapter, Story

    staff = make_user(django_user_model, "admin", is_staff=True)
    client = APIClient()
    client.force_authenticate(user=staff)

    created = client.post(
        "/api/admin/stories/",
        {
            "slug": "new-spire",
            "title": "New Spire",
            "summary": "An admin-authored campaign.",
            "price": 125,
            "world_slug": "arcane-spire",
            "difficulty": "intermediate",
            "sort_order": 12,
        },
        format="json",
    )
    assert created.status_code == 201
    assert created.json()["is_published"] is False
    assert created.json()["management_source"] == MANAGEMENT_SOURCE_ADMIN
    story_id = created.json()["id"]

    chapter_created = client.post(
        "/api/admin/chapters/",
        {
            "story_id": story_id,
            "slug": "new-spire-foundations",
            "number": 1,
            "title": "Foundations",
            "description": "Build the foundation.",
            "is_published": True,
            "is_playable": True,
            "sort_order": 3,
            "battle_stage": {"parallax": "arcane-library"},
        },
        format="json",
    )
    assert chapter_created.status_code == 201
    assert chapter_created.json()["management_source"] == MANAGEMENT_SOURCE_ADMIN
    chapter_id = chapter_created.json()["id"]

    chapter_patched = client.patch(
        f"/api/admin/chapters/{chapter_id}/",
        {
            "number": 2,
            "title": "Reliable Foundations",
            "description": "Updated chapter.",
            "sort_order": 4,
            "battle_stage": {
                "parallax": "arcane-library",
                "landing": {"x": 0.2, "y": 0.7, "width": 0.6, "height": 0.2},
            },
        },
        format="json",
    )
    assert chapter_patched.status_code == 200

    story_patched = client.patch(
        f"/api/admin/stories/{story_id}/",
        {
            "title": "The New Spire",
            "summary": "Updated campaign.",
            "price": 150,
            "world_slug": "frostbound-citadel",
            "difficulty": "advanced",
            "sort_order": 13,
            "is_published": True,
        },
        format="json",
    )
    assert story_patched.status_code == 200
    story = Story.objects.get(id=story_id)
    chapter = Chapter.objects.get(id=chapter_id)
    assert story.is_published is True
    assert story.title == "The New Spire"
    assert story.price == 150
    assert story.management_source == MANAGEMENT_SOURCE_ADMIN
    assert chapter.number == 2
    assert chapter.title == "Reliable Foundations"
    assert chapter.battle_stage["landing"]["width"] == 0.6
    assert chapter_patched.json()["battle_stage"] == chapter.battle_stage
    assert chapter.management_source == MANAGEMENT_SOURCE_ADMIN
    assert set(AdminActionLog.objects.filter(actor=staff).values_list("action", flat=True)) == {
        "story.create",
        "story.update",
        "chapter.create",
        "chapter.update",
    }


@pytest.mark.django_db
def test_published_story_keeps_at_least_one_published_chapter(django_user_model):
    from curriculum.models import MANAGEMENT_SOURCE_ADMIN, Chapter, Story

    staff = make_user(django_user_model, "curriculum-guard", is_staff=True)
    story = Story.objects.create(
        slug="published-guard-story",
        title="Published Guard Story",
        world_slug="arcane-spire",
        is_published=True,
        management_source=MANAGEMENT_SOURCE_ADMIN,
    )
    chapter = Chapter.objects.create(
        story=story,
        slug="published-guard-chapter",
        number=1,
        title="Published Guard Chapter",
        is_published=True,
        is_playable=True,
        management_source=MANAGEMENT_SOURCE_ADMIN,
    )
    client = APIClient()
    client.force_authenticate(user=staff)

    response = client.patch(
        f"/api/admin/chapters/{chapter.id}/",
        {"is_published": False, "is_playable": False},
        format="json",
    )

    assert response.status_code == 400
    assert "is_published" in response.json()
    chapter.refresh_from_db()
    assert chapter.is_published is True
    assert chapter.is_playable is True
    assert not AdminActionLog.objects.filter(action="chapter.update").exists()


@pytest.mark.django_db
def test_curriculum_rejects_invalid_payloads_without_mutating(django_user_model):
    from curriculum.models import Story

    staff = make_user(django_user_model, "admin", is_staff=True)
    client = APIClient()
    client.force_authenticate(user=staff)

    unknown_world = client.post(
        "/api/admin/stories/",
        {
            "slug": "bad-world",
            "title": "Bad World",
            "world_slug": "missing-visuals",
        },
        format="json",
    )
    malformed_boolean = client.post(
        "/api/admin/stories/",
        {
            "slug": "bad-bool",
            "title": "Bad Bool",
            "world_slug": "arcane-spire",
            "is_published": "definitely",
        },
        format="json",
    )
    unknown_field = client.post(
        "/api/admin/stories/",
        {
            "slug": "stale-client",
            "title": "Stale Client",
            "world_slug": "arcane-spire",
            "publshed": True,
        },
        format="json",
    )

    assert unknown_world.status_code == 400
    assert malformed_boolean.status_code == 400
    assert unknown_field.status_code == 400
    assert "world_slug" in unknown_world.json()
    assert "is_published" in malformed_boolean.json()
    assert "publshed" in unknown_field.json()
    assert Story.objects.count() == 0
    assert AdminActionLog.objects.count() == 0


@pytest.mark.django_db
def test_seed_owned_curriculum_row_transfers_whole_row_to_admin(django_user_model):
    from curriculum.models import MANAGEMENT_SOURCE_ADMIN, Story

    staff = make_user(django_user_model, "admin", is_staff=True)
    story = Story.objects.create(
        slug="arcane-spire",
        title="The Arcane Spire",
        world_slug="arcane-spire",
    )
    client = APIClient()
    client.force_authenticate(user=staff)

    response = client.patch(
        f"/api/admin/stories/{story.id}/",
        {
            "title": "Admin Arcane Spire",
            "summary": "Admin-owned complete row.",
            "price": 25,
            "difficulty": "intermediate",
            "sort_order": 9,
        },
        format="json",
    )

    assert response.status_code == 200
    story.refresh_from_db()
    assert story.management_source == MANAGEMENT_SOURCE_ADMIN
    assert response.json()["management_source"] == MANAGEMENT_SOURCE_ADMIN


@pytest.mark.django_db
def test_staff_settings_toggle_feature_flag(django_user_model):
    from adminconsole.flags import feature_enabled

    staff = make_user(django_user_model, "admin", is_staff=True)
    client = APIClient()
    client.force_authenticate(user=staff)

    assert feature_enabled("shop-purchases") is True
    response = client.post(
        "/api/admin/settings/",
        {"key": "shop-purchases", "enabled": False},
        format="json",
    )
    assert response.status_code == 200
    assert feature_enabled("shop-purchases") is False

    settings_body = client.get("/api/admin/settings/").json()
    assert settings_body["feature_flags"] == [
        {
            "key": "shop-purchases",
            "label": "Shop purchases",
            "description": "Allow players to claim or purchase stories and companions.",
            "enabled": False,
        }
    ]
    assert AdminActionLog.objects.filter(action="feature_flag.update").count() == 1

    unsupported = client.post(
        "/api/admin/settings/",
        {"key": "invented-flag", "enabled": True},
        format="json",
    )
    wrong_shape = client.post(
        "/api/admin/settings/",
        [{}],
        format="json",
    )
    assert unsupported.status_code == 400
    assert wrong_shape.status_code == 400


@pytest.mark.django_db
def test_staff_moderation_unpublishes_content(django_user_model):
    from authoring.models import STATUS_PUBLISHED, ContentDefinition

    staff = make_user(django_user_model, "admin", is_staff=True)
    author = make_user(django_user_model, "author")
    content = ContentDefinition.objects.create(
        owner=author,
        kind="challenge",
        slug="shared-content",
        title="Shared Content",
        status=STATUS_PUBLISHED,
        visibility="public",
    )
    client = APIClient()
    client.force_authenticate(user=staff)

    listed = client.get("/api/admin/moderation/").json()
    assert any(c["id"] == content.id for c in listed["content"])

    response = client.post(
        "/api/admin/moderation/unpublish/",
        {"kind": "content", "id": content.id},
        format="json",
    )
    assert response.status_code == 200
    content.refresh_from_db()
    assert content.visibility == "private"
    assert content.status == "draft"
    log = AdminActionLog.objects.get(action="moderation.unpublish")
    assert log.actor_id == staff.id
    assert log.before == {"visibility": "public", "status": "published"}
    assert log.after == {"visibility": "private", "status": "draft"}


@pytest.mark.django_db
def test_moderation_cannot_target_content_outside_the_queue(django_user_model):
    from authoring.models import STATUS_PUBLISHED, ContentDefinition

    staff = make_user(django_user_model, "admin", is_staff=True)
    official = ContentDefinition.objects.create(
        owner=staff,
        kind="lesson",
        slug="official-content",
        title="Official Content",
        status=STATUS_PUBLISHED,
        visibility="public",
    )
    client = APIClient()
    client.force_authenticate(user=staff)

    response = client.post(
        "/api/admin/moderation/unpublish/",
        {"kind": "content", "id": official.id},
        format="json",
    )

    assert response.status_code == 404
    official.refresh_from_db()
    assert official.status == STATUS_PUBLISHED
    assert official.visibility == "public"
    assert not AdminActionLog.objects.filter(action="moderation.unpublish").exists()


@pytest.mark.django_db
def test_staff_analytics_returns_shape(django_user_model):
    from django.utils import timezone

    from adventures.models import (
        AdventureLevel,
        AdventureRun,
        AdventureWave,
        AdventureWaveVariant,
    )
    from challenges.models import (
        ChallengeLevel,
        ChallengeRun,
        ChallengeTrial,
        ChallengeTrialVariant,
    )
    from curriculum.models import Chapter, Story

    staff = make_user(django_user_model, "admin", is_staff=True)
    player = get_or_create_player(make_user(django_user_model, "learner"))
    story = Story.objects.create(
        slug="analytics-story",
        title="Analytics Story",
        world_slug="arcane-spire",
    )
    chapter = Chapter.objects.create(
        story=story,
        slug="analytics-chapter",
        number=1,
        title="Analytics Chapter",
        description="Metrics.",
    )
    level = AdventureLevel.objects.create(
        chapter=chapter,
        slug="analytics-adventure",
        title="Analytics Adventure",
    )
    wave = AdventureWave.objects.create(level=level, slug="wave", title="Wave")
    adventure_variant = AdventureWaveVariant.objects.create(
        wave=wave,
        slug="main",
        label="Main",
    )
    AdventureRun.objects.create(
        player=player,
        level=level,
        current_wave=wave,
        selected_variant=adventure_variant,
        status=AdventureRun.Status.COMPLETED,
        passed_at=timezone.now(),
    )
    challenge_level = ChallengeLevel.objects.create(
        chapter=chapter,
        slug="analytics-challenge",
        title="Analytics Challenge",
    )
    trial = ChallengeTrial.objects.create(
        challenge_level=challenge_level,
        difficulty=ChallengeTrial.Difficulty.EASY,
    )
    challenge_variant = ChallengeTrialVariant.objects.create(
        trial=trial,
        slug="main",
        label="Main",
    )
    ChallengeRun.objects.create(
        player=player,
        challenge_trial=trial,
        selected_variant=challenge_variant,
        source_entry_point="admin-test",
        status=ChallengeRun.Status.COMPLETED,
        completed_at=timezone.now(),
    )
    client = APIClient()
    client.force_authenticate(user=staff)

    body = client.get("/api/admin/analytics/").json()
    assert set(body) >= {"runs", "completions", "active_learners_30d", "per_story"}
    assert body["runs"]["total"] == 2
    assert body["runs"]["passed"] == 2
    assert body["runs"]["adventure"]["total"] == 1
    assert body["runs"]["challenge"]["total"] == 1
    assert body["active_learners_30d"] == 1
    assert body["per_story"] == [
        {
            "slug": story.slug,
            "title": story.title,
            "runs": 2,
            "passed": 2,
            "adventure_runs": 1,
            "challenge_runs": 1,
        }
    ]
