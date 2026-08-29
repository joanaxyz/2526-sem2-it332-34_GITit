import pytest
from rest_framework.test import APIClient

from adventures.models import AdventureLevel
from authoring.models import AuthoringChapter, ContentDefinition, PublishedContentRuntime
from curriculum.models import MANAGEMENT_SOURCE_ADMIN, Chapter, CommandSkill, Story


def make_user(django_user_model, username="student"):
    return django_user_model.objects.create_user(
        username=username,
        email=f"{username}@example.com",
        password="pass12345",
    )


def adventure_definition():
    return {
        "levels": [
            {
                "slug": "status-check",
                "title": "Check status",
                "initial_state": {},
                "solution_commands": ["git status"],
                "evaluation_spec": {"completion_policy": {"mode": "state_hash"}},
                "scenario_context": {"schema_version": 3, "story": "Inspect the repo."},
            }
        ]
    }


@pytest.mark.django_db
def test_user_can_create_validate_and_test_run_adventure_definition(django_user_model):
    user = make_user(django_user_model)
    client = APIClient()
    client.force_authenticate(user=user)

    response = client.post(
        "/api/authoring/content-definitions/",
        {
            "kind": "adventure",
            "slug": "my-adventure",
            "title": "My Adventure",
            "summary": "Practice status.",
            "command_family": "git status",
            "definition": adventure_definition(),
        },
        format="json",
    )

    assert response.status_code == 201
    definition_id = response.json()["id"]

    validate = client.post(f"/api/authoring/content-definitions/{definition_id}/validate/")
    assert validate.status_code == 200
    assert validate.json()["valid"] is True

    test_run = client.post(f"/api/authoring/content-definitions/{definition_id}/test-run/")
    assert test_run.status_code == 200
    assert test_run.json()["kind"] == "adventure"
    assert test_run.json()["start_path"].startswith("/adventure-levels/")

    content = ContentDefinition.objects.get(id=definition_id)
    assert content.status == "testable"
    assert PublishedContentRuntime.objects.filter(content_definition=content).exists()


@pytest.mark.django_db
def test_content_definition_requests_reject_unknown_and_malformed_fields(
    django_user_model,
):
    user = make_user(django_user_model, "strict-author")
    client = APIClient()
    client.force_authenticate(user=user)

    unknown = client.post(
        "/api/authoring/content-definitions/",
        {
            "kind": "lesson",
            "slug": "unknown-authoring-field",
            "title": "Unknown Authoring Field",
            "definition": {"pages": []},
            "publshed": True,
        },
        format="json",
    )
    malformed = client.post(
        "/api/authoring/content-definitions/",
        {
            "kind": "lesson",
            "slug": "malformed-official-chapter",
            "title": "Malformed Official Chapter",
            "official_chapter": ["not", "an", "id"],
            "definition": {"pages": []},
        },
        format="json",
    )
    wrong_shape = client.post(
        "/api/authoring/content-definitions/",
        [{"kind": "lesson"}],
        format="json",
    )

    assert unknown.status_code == 400
    assert "publshed" in unknown.json()
    assert malformed.status_code == 400
    assert "official_chapter" in malformed.json()
    assert wrong_shape.status_code == 400
    assert not ContentDefinition.objects.filter(
        slug__in={"unknown-authoring-field", "malformed-official-chapter"}
    ).exists()


@pytest.mark.django_db
def test_private_content_is_hidden_from_other_users(django_user_model):
    owner = make_user(django_user_model, "owner")
    other = make_user(django_user_model, "other")
    content = ContentDefinition.objects.create(
        owner=owner,
        kind="lesson",
        slug="private-lesson",
        title="Private ChapterLesson",
        definition={"pages": [{"title": "Only mine", "blocks": []}]},
    )
    client = APIClient()
    client.force_authenticate(user=other)

    response = client.get(f"/api/authoring/content-definitions/{content.id}/")

    assert response.status_code == 404


@pytest.mark.django_db
def test_staff_content_compiles_into_selected_official_chapter(django_user_model):
    from adminconsole.models import AdminActionLog

    staff = make_user(django_user_model, "staff")
    staff.is_staff = True
    staff.save(update_fields=["is_staff"])
    story = Story.objects.create(
        slug="admin-story",
        title="Admin Story",
        world_slug="arcane-spire",
        management_source=MANAGEMENT_SOURCE_ADMIN,
    )
    chapter = Chapter.objects.create(
        story=story,
        slug="admin-chapter",
        number=1,
        title="Admin Chapter",
        description="Official destination.",
        management_source=MANAGEMENT_SOURCE_ADMIN,
    )
    client = APIClient()
    client.force_authenticate(user=staff)

    created = client.post(
        "/api/authoring/content-definitions/",
        {
            "kind": "adventure",
            "slug": "official-adventure",
            "title": "Official Adventure",
            "summary": "Lives in a real chapter.",
            "command_family": "git status",
            "official_chapter": chapter.id,
            "definition": adventure_definition(),
        },
        format="json",
    )

    assert created.status_code == 201
    assert created.json()["official_chapter_id"] == chapter.id
    definition_id = created.json()["id"]
    test_run = client.post(f"/api/authoring/content-definitions/{definition_id}/test-run/")
    assert test_run.status_code == 400
    assert "official_chapter" in test_run.json()
    assert not PublishedContentRuntime.objects.filter(content_definition_id=definition_id).exists()
    updated = client.patch(
        f"/api/authoring/content-definitions/{definition_id}/",
        {"summary": "Audited official update."},
        format="json",
    )
    assert updated.status_code == 200
    published = client.post(f"/api/authoring/content-definitions/{definition_id}/publish/")
    assert published.status_code == 200

    content = ContentDefinition.objects.get(id=definition_id)
    runtime = PublishedContentRuntime.objects.get(content_definition=content)
    assert runtime.chapter_id == chapter.id
    assert runtime.adventure.chapter_id == chapter.id
    assert not Chapter.objects.filter(slug__startswith="ugc-").exists()
    assert CommandSkill.objects.filter(
        source_content_definition=content,
        is_published=True,
    ).exists()
    assert content.visibility == "public"
    assert set(AdminActionLog.objects.filter(actor=staff).values_list("action", flat=True)) == {
        "official_content.create",
        "official_content.update",
        "official_content.publish",
    }

    unassigned = ContentDefinition.objects.create(
        owner=staff,
        kind="lesson",
        slug="staff-ugc-draft",
        title="Staff UGC Draft",
    )
    official_list = client.get("/api/admin/content/").json()["results"]
    row = next(item for item in official_list if item["id"] == content.id)
    assert row["official_chapter"] == {"id": chapter.id, "title": chapter.title}
    assert all(item["id"] != unassigned.id for item in official_list)


@pytest.mark.django_db
def test_official_content_rejects_an_unpublished_destination(django_user_model):
    staff = make_user(django_user_model, "official-draft-staff")
    staff.is_staff = True
    staff.save(update_fields=["is_staff"])
    story = Story.objects.create(
        slug="draft-official-story",
        title="Draft Official Story",
        world_slug="arcane-spire",
        is_published=True,
        management_source=MANAGEMENT_SOURCE_ADMIN,
    )
    chapter = Chapter.objects.create(
        story=story,
        slug="draft-official-chapter",
        number=1,
        title="Draft Official Chapter",
        description="Not yet learner-visible.",
        is_published=False,
        is_playable=False,
        management_source=MANAGEMENT_SOURCE_ADMIN,
    )
    client = APIClient()
    client.force_authenticate(user=staff)

    response = client.post(
        "/api/authoring/content-definitions/",
        {
            "kind": "lesson",
            "slug": "premature-official-lesson",
            "title": "Premature Official Lesson",
            "official_chapter": chapter.id,
            "definition": {"pages": []},
        },
        format="json",
    )

    assert response.status_code == 400
    assert "official_chapter" in response.json()
    assert not ContentDefinition.objects.filter(slug="premature-official-lesson").exists()


@pytest.mark.django_db
def test_official_publish_rejects_runtime_slug_collision(django_user_model):
    staff = make_user(django_user_model, "official-collision-staff")
    staff.is_staff = True
    staff.save(update_fields=["is_staff"])
    story = Story.objects.create(
        slug="collision-story",
        title="Collision Story",
        world_slug="arcane-spire",
        management_source=MANAGEMENT_SOURCE_ADMIN,
    )
    chapter = Chapter.objects.create(
        story=story,
        slug="collision-chapter",
        number=1,
        title="Collision Chapter",
        description="Published destination.",
        management_source=MANAGEMENT_SOURCE_ADMIN,
    )
    AdventureLevel.objects.create(
        chapter=chapter,
        slug="status-check",
        title="Existing Level",
    )
    client = APIClient()
    client.force_authenticate(user=staff)
    created = client.post(
        "/api/authoring/content-definitions/",
        {
            "kind": "adventure",
            "slug": "colliding-official-adventure",
            "title": "Colliding Official Adventure",
            "command_family": "git status",
            "official_chapter": chapter.id,
            "definition": adventure_definition(),
        },
        format="json",
    )
    assert created.status_code == 201

    published = client.post(f"/api/authoring/content-definitions/{created.json()['id']}/publish/")

    assert published.status_code == 400
    assert "definition" in published.json()


@pytest.mark.django_db
def test_non_staff_authored_destination_wins_when_official_field_is_null(
    django_user_model,
):
    user = make_user(django_user_model)
    first = AuthoringChapter.objects.create(
        owner=user,
        slug="first-authored-chapter",
        title="First authored chapter",
    )
    second = AuthoringChapter.objects.create(
        owner=user,
        slug="second-authored-chapter",
        title="Second authored chapter",
    )
    client = APIClient()
    client.force_authenticate(user=user)

    created = client.post(
        "/api/authoring/content-definitions/",
        {
            "kind": "lesson",
            "slug": "authored-lesson",
            "title": "Authored lesson",
            "chapter": first.id,
            "official_chapter": None,
            "definition": {"pages": []},
        },
        format="json",
    )

    assert created.status_code == 201
    content = ContentDefinition.objects.get(id=created.json()["id"])
    assert content.chapter_id == first.id
    assert content.official_chapter_id is None

    updated = client.patch(
        f"/api/authoring/content-definitions/{content.id}/",
        {"chapter": second.id, "official_chapter": None},
        format="json",
    )

    assert updated.status_code == 200
    content.refresh_from_db()
    assert content.chapter_id == second.id
    assert content.official_chapter_id is None


@pytest.mark.django_db
def test_non_staff_cannot_place_content_in_official_chapter(django_user_model):
    user = make_user(django_user_model)
    story = Story.objects.create(
        slug="official-story",
        title="Official Story",
        world_slug="arcane-spire",
    )
    chapter = Chapter.objects.create(
        story=story,
        slug="official-chapter",
        number=1,
        title="Official Chapter",
        description="Staff only.",
    )
    client = APIClient()
    client.force_authenticate(user=user)

    response = client.post(
        "/api/authoring/content-definitions/",
        {
            "kind": "lesson",
            "slug": "intruding-lesson",
            "title": "Intruding Lesson",
            "official_chapter": chapter.id,
            "definition": {"pages": []},
        },
        format="json",
    )

    assert response.status_code == 403
    assert not ContentDefinition.objects.filter(slug="intruding-lesson").exists()


@pytest.mark.django_db
def test_staff_cannot_promote_player_content_into_official_curriculum(django_user_model):
    player = make_user(django_user_model, "ugc-owner")
    staff = make_user(django_user_model, "ugc-reviewer")
    staff.is_staff = True
    staff.save(update_fields=["is_staff"])
    story = Story.objects.create(
        slug="ugc-boundary-story",
        title="UGC Boundary Story",
        world_slug="arcane-spire",
        management_source=MANAGEMENT_SOURCE_ADMIN,
    )
    chapter = Chapter.objects.create(
        story=story,
        slug="ugc-boundary-chapter",
        number=1,
        title="UGC Boundary Chapter",
        description="Official destination.",
        management_source=MANAGEMENT_SOURCE_ADMIN,
    )
    content = ContentDefinition.objects.create(
        owner=player,
        kind="adventure",
        slug="player-adventure",
        title="Player Adventure",
        definition=adventure_definition(),
    )
    client = APIClient()
    client.force_authenticate(user=staff)

    response = client.patch(
        f"/api/authoring/content-definitions/{content.id}/",
        {"official_chapter": chapter.id},
        format="json",
    )

    assert response.status_code == 400
    assert "official_chapter" in response.json()
    content.refresh_from_db()
    assert content.owner_id == player.id
    assert content.official_chapter_id is None
