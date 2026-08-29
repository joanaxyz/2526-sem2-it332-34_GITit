"""Admin console read-route and selector contract tests."""

import pytest
from rest_framework.test import APIClient

from adminconsole.tests.helpers import make_user
from players.services import get_or_create_player


@pytest.mark.django_db
def test_staff_can_read_every_admin_get_contract(django_user_model):
    staff = make_user(django_user_model, "read-contract-admin", is_staff=True)
    client = APIClient()
    client.force_authenticate(user=staff)

    expected_keys = {
        "/api/admin/overview/": {
            "users",
            "economy",
            "recent_signups",
            "recent_purchases",
            "recent_admin_actions",
        },
        "/api/admin/users/": {"results"},
        f"/api/admin/users/{staff.id}/": {
            "id",
            "username",
            "email",
            "is_staff",
            "is_active",
            "date_joined",
            "last_login",
            "wallet",
            "entitlement_count",
        },
        "/api/admin/economy/transactions/": {"results"},
        "/api/admin/stories/": {"results", "world_options"},
        "/api/admin/chapters/": {"results"},
        "/api/admin/content/": {"results"},
        "/api/admin/analytics/": {
            "runs",
            "completions",
            "active_learners_30d",
            "per_story",
        },
        "/api/admin/moderation/": {"content"},
        "/api/admin/settings/": {"feature_flags"},
    }

    for path, keys in expected_keys.items():
        response = client.get(path)
        assert response.status_code == 200, path
        assert set(response.json()) == keys, path


@pytest.mark.django_db
def test_admin_user_list_preserves_filter_order_and_cap(django_user_model):
    from datetime import timedelta

    from django.utils import timezone

    from adminconsole.selectors import admin_user_list_payload

    staff = make_user(django_user_model, "user-list-admin", is_staff=True)
    now = timezone.now()
    django_user_model.objects.filter(pk=staff.pk).update(date_joined=now - timedelta(days=1))
    users = [
        django_user_model(
            username=f"batch-{index:03d}",
            email=f"batch-{index:03d}@example.com",
        )
        for index in range(101)
    ]
    django_user_model.objects.bulk_create(users)
    for index, user in enumerate(users):
        user.date_joined = now + timedelta(minutes=index)
    django_user_model.objects.bulk_update(users, ["date_joined"])
    email_match = make_user(django_user_model, "mail-only-match")
    django_user_model.objects.filter(pk=email_match.pk).update(
        username="unrelated-username",
        email="Needle@Example.com",
        date_joined=now - timedelta(days=2),
    )

    client = APIClient()
    client.force_authenticate(user=staff)

    listed = client.get("/api/admin/users/").json()["results"]
    filtered = client.get("/api/admin/users/", {"q": "batch-00"}).json()["results"]
    email_filtered = client.get("/api/admin/users/", {"q": "needle"}).json()["results"]
    direct_over_limit = admin_user_list_payload(limit=10_000)["results"]

    assert len(listed) == 100
    assert [row["username"] for row in listed] == [
        f"batch-{index:03d}" for index in range(100, 0, -1)
    ]
    assert [row["username"] for row in filtered] == [
        f"batch-{index:03d}" for index in range(9, -1, -1)
    ]
    assert [row["username"] for row in email_filtered] == ["unrelated-username"]
    assert [row["id"] for row in direct_over_limit] == [row["id"] for row in listed]
    assert admin_user_list_payload(limit=-1) == {"results": []}


@pytest.mark.django_db
def test_admin_transactions_preserve_user_filter_id_order_and_cap(django_user_model):
    from adminconsole.selectors import admin_transaction_list_payload
    from progress.models import CoinTransaction

    staff = make_user(django_user_model, "transaction-list-admin", is_staff=True)
    target = make_user(django_user_model, "transaction-target")
    other = make_user(django_user_model, "transaction-other")
    target_player = get_or_create_player(target)
    other_player = get_or_create_player(other)
    transactions = CoinTransaction.objects.bulk_create(
        [
            CoinTransaction(
                player=target_player,
                amount=index + 1,
                reason="query-contract",
                award_key=f"target-{index}",
            )
            for index in range(201)
        ]
    )
    CoinTransaction.objects.create(
        player=other_player,
        amount=1,
        reason="query-contract",
        award_key="other",
    )
    client = APIClient()
    client.force_authenticate(user=staff)

    results = client.get(
        "/api/admin/economy/transactions/",
        {"user_id": target.id},
    ).json()["results"]
    direct_over_limit = admin_transaction_list_payload(
        user_id=target.id,
        limit=10_000,
    )["results"]

    assert len(results) == 200
    assert {row["user_id"] for row in results} == {target.id}
    assert [row["id"] for row in results] == [
        transaction.id for transaction in reversed(transactions[1:])
    ]
    assert [row["id"] for row in direct_over_limit] == [row["id"] for row in results]


@pytest.mark.django_db
def test_admin_curriculum_lists_preserve_order_counts_options_and_filter(
    django_user_model,
    django_assert_num_queries,
):
    from adminconsole.curriculum_options import SUPPORTED_STORY_WORLD_SLUGS
    from adminconsole.selectors import admin_story_list_payload
    from curriculum.models import Chapter, Story

    staff = make_user(django_user_model, "curriculum-list-admin", is_staff=True)
    later_story = Story.objects.create(
        slug="later-story",
        title="Later Story",
        world_slug="arcane-spire",
        sort_order=20,
    )
    earlier_story = Story.objects.create(
        slug="earlier-story",
        title="Earlier Story",
        world_slug="frostbound-citadel",
        sort_order=10,
    )
    tied_story = Story.objects.create(
        slug="tied-story",
        title="Tied Story",
        world_slug="skyline-sanctum",
        sort_order=10,
        prerequisite_story=earlier_story,
    )
    later_chapter = Chapter.objects.create(
        story=earlier_story,
        slug="later-chapter",
        number=3,
        title="Later Chapter",
        description="",
        sort_order=20,
    )
    earlier_chapter = Chapter.objects.create(
        story=earlier_story,
        slug="earlier-chapter",
        number=2,
        title="Earlier Chapter",
        description="",
        sort_order=10,
    )
    first_tied_chapter = Chapter.objects.create(
        story=earlier_story,
        slug="first-tied-chapter",
        number=1,
        title="First Tied Chapter",
        description="",
        sort_order=10,
    )
    Chapter.objects.create(
        story=later_story,
        slug="other-story-chapter",
        number=1,
        title="Other Story Chapter",
        description="",
        sort_order=1,
    )
    client = APIClient()
    client.force_authenticate(user=staff)

    stories = client.get("/api/admin/stories/").json()
    chapters = client.get(
        "/api/admin/chapters/",
        {"story": earlier_story.id},
    ).json()["results"]
    with django_assert_num_queries(2):
        direct_stories = admin_story_list_payload()["results"]

    assert [row["id"] for row in stories["results"]] == [
        earlier_story.id,
        tied_story.id,
        later_story.id,
    ]
    assert [row["chapter_count"] for row in stories["results"]] == [3, 0, 1]
    assert direct_stories[1]["prerequisite_story"] == {
        "id": earlier_story.id,
        "slug": earlier_story.slug,
        "title": earlier_story.title,
    }
    assert stories["world_options"] == list(SUPPORTED_STORY_WORLD_SLUGS)
    assert [row["id"] for row in chapters] == [
        first_tied_chapter.id,
        earlier_chapter.id,
        later_chapter.id,
    ]
    assert {row["story_id"] for row in chapters} == {earlier_story.id}


@pytest.mark.django_db
def test_admin_official_content_preserves_eligibility_kind_order_and_cap(django_user_model):
    from datetime import timedelta

    from django.utils import timezone

    from adminconsole.selectors import (
        admin_moderation_list_payload,
        admin_official_content_list_payload,
    )
    from authoring.models import STATUS_PUBLISHED, ContentDefinition
    from curriculum.models import Chapter, Story

    staff = make_user(django_user_model, "content-list-admin", is_staff=True)
    author = make_user(django_user_model, "content-list-author")
    story = Story.objects.create(
        slug="content-list-story",
        title="Content List Story",
        world_slug="arcane-spire",
    )
    chapter = Chapter.objects.create(
        story=story,
        slug="content-list-chapter",
        number=1,
        title="Content List Chapter",
        description="",
    )
    eligible = ContentDefinition.objects.bulk_create(
        [
            ContentDefinition(
                owner=staff,
                official_chapter=chapter,
                kind="adventure",
                slug=f"official-{index}",
                title=f"Official {index}",
            )
            for index in range(201)
        ]
    )
    now = timezone.now()
    for index, content in enumerate(eligible):
        content.updated_at = now + timedelta(minutes=index)
    ContentDefinition.objects.bulk_update(eligible, ["updated_at"])
    ownerless_challenge = ContentDefinition.objects.create(
        owner=None,
        official_chapter=chapter,
        kind="challenge",
        slug="ownerless-official",
        title="Ownerless Official",
    )
    excluded_nonstaff = ContentDefinition.objects.create(
        owner=author,
        official_chapter=chapter,
        kind="adventure",
        slug="player-owned-official",
        title="Player Owned",
    )
    excluded_without_chapter = ContentDefinition.objects.create(
        owner=staff,
        kind="adventure",
        slug="staff-without-chapter",
        title="No Official Chapter",
    )
    ContentDefinition.objects.bulk_create(
        [
            ContentDefinition(
                owner=author,
                kind="lesson",
                slug=f"moderation-{index}",
                title=f"Moderation {index}",
                status=STATUS_PUBLISHED,
                visibility="public",
            )
            for index in range(201)
        ]
    )
    client = APIClient()
    client.force_authenticate(user=staff)

    adventures = client.get("/api/admin/content/", {"kind": "adventure"}).json()["results"]
    challenges = client.get("/api/admin/content/", {"kind": "challenge"}).json()["results"]
    direct_official_over_limit = admin_official_content_list_payload(
        kind="adventure",
        limit=10_000,
    )["results"]
    direct_moderation_over_limit = admin_moderation_list_payload(limit=10_000)["content"]

    assert len(adventures) == 200
    assert [row["id"] for row in adventures] == [content.id for content in reversed(eligible[1:])]
    assert excluded_nonstaff.id not in {row["id"] for row in adventures}
    assert excluded_without_chapter.id not in {row["id"] for row in adventures}
    assert [row["id"] for row in challenges] == [ownerless_challenge.id]
    assert [row["id"] for row in direct_official_over_limit] == [row["id"] for row in adventures]
    assert len(direct_moderation_over_limit) == 200
