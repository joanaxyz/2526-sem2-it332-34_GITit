from django.core.management import call_command

from adventures.models import AdventureLevel, AdventureWave, AdventureWaveVariant
from authoring.compiler import ContentRuntimeCompiler
from authoring.models import ContentDefinition, ContentKind
from challenges.models import ChallengeLevel, ChallengeTrial, ChallengeTrialVariant
from curriculum.models import (
    MANAGEMENT_SOURCE_ADMIN,
    MANAGEMENT_SOURCE_SEED,
    Chapter,
    ChapterLesson,
    CommandForm,
    CommandSkill,
    Story,
)
from curriculum.seed_data.chapters import CHAPTERS
from curriculum.seed_data.stories import STORIES


def _counts() -> dict[str, int]:
    return {
        "stories": Story.objects.count(),
        "chapters": Chapter.objects.count(),
        "lessons": ChapterLesson.objects.count(),
        "skills": CommandSkill.objects.count(),
        "forms": CommandForm.objects.count(),
        "adventure_levels": AdventureLevel.objects.count(),
        "adventure_waves": AdventureWave.objects.count(),
        "adventure_variants": AdventureWaveVariant.objects.count(),
        "challenge_levels": ChallengeLevel.objects.count(),
        "challenge_trials": ChallengeTrial.objects.count(),
        "challenge_variants": ChallengeTrialVariant.objects.count(),
    }


def _identity_snapshot() -> dict[str, list[str]]:
    return {
        "stories": list(Story.objects.order_by("slug").values_list("slug", flat=True)),
        "chapters": list(Chapter.objects.order_by("slug").values_list("slug", flat=True)),
        "adventure_levels": list(
            AdventureLevel.objects.order_by("slug").values_list("slug", flat=True)
        ),
        "adventure_waves": list(
            AdventureWave.objects.order_by("slug").values_list("slug", flat=True)
        ),
        "challenge_levels": list(
            ChallengeLevel.objects.order_by("slug").values_list("slug", flat=True)
        ),
        "challenge_variants": list(
            ChallengeTrialVariant.objects.order_by("case_id").values_list("case_id", flat=True)
        ),
    }


def test_seed_curriculum_is_idempotent_without_reset(db):
    call_command("seed_curriculum")
    first_counts = _counts()
    first_identity = _identity_snapshot()

    call_command("seed_curriculum")

    assert _counts() == first_counts
    assert _identity_snapshot() == first_identity


def test_seed_curriculum_preserves_complete_admin_owned_rows(db, django_user_model):
    call_command("seed_curriculum")

    admin_story = Story.objects.get(slug=STORIES[0]["slug"])
    admin_story.title = "Operator-owned story title"
    admin_story.summary = "Operator-owned summary"
    admin_story.price = 987
    admin_story.is_published = False
    admin_story.management_source = MANAGEMENT_SOURCE_ADMIN
    admin_story.save()

    admin_chapter = Chapter.objects.get(slug=CHAPTERS[0]["slug"])
    admin_chapter.title = "Operator-owned chapter title"
    admin_chapter.description = "Operator-owned chapter description"
    admin_chapter.is_published = False
    admin_chapter.is_playable = False
    admin_chapter.battle_stage = {"parallax": "operator-owned-stage"}
    admin_chapter.management_source = MANAGEMENT_SOURCE_ADMIN
    admin_chapter.save()

    seed_story = Story.objects.get(slug=STORIES[1]["slug"])
    seed_story.title = "temporary drift"
    seed_story.save(update_fields=["title"])
    seed_chapter = Chapter.objects.get(slug=CHAPTERS[1]["slug"])
    seed_chapter.title = "temporary drift"
    seed_chapter.save(update_fields=["title"])

    owner = django_user_model.objects.create_user(
        username="official-content-owner",
        is_staff=True,
    )
    repository_state = {
        "repository_initialized": True,
        "commits": [],
        "branches": {"main": None},
        "head": {"type": "branch", "name": "main"},
        "staging": {},
        "working_tree": {},
        "conflicts": [],
    }
    official_content = ContentDefinition.objects.create(
        owner=owner,
        kind=ContentKind.ADVENTURE,
        official_chapter=seed_chapter,
        slug="official-reseed-survivor",
        title="Official Reseed Survivor",
        command_family="git status",
        definition={
            "levels": [
                {
                    "slug": "official-reseed-level",
                    "title": "Official Reseed Level",
                    "scenario_context": {
                        "schema_version": 3,
                        "story": "Reseed",
                        "task": "Survive",
                    },
                    "initial_state": repository_state,
                    "target_state": repository_state,
                    "evaluation_spec": {"completion_policy": {"mode": "state_hash"}},
                    "solution_commands": ["git status"],
                }
            ]
        },
    )
    official_runtime = ContentRuntimeCompiler().compile(content=official_content)
    authored_skill = CommandSkill.objects.get(source_content_definition=official_content)

    admin_only_story = Story.objects.create(
        slug="operator-story",
        title="Operator Story",
        world_slug=STORIES[0]["world_slug"],
        is_published=True,
        management_source=MANAGEMENT_SOURCE_ADMIN,
    )
    admin_only_chapter = Chapter.objects.create(
        story=admin_only_story,
        slug="operator-chapter",
        number=1,
        title="Operator Chapter",
        description="Created in the admin console.",
        is_published=True,
        management_source=MANAGEMENT_SOURCE_ADMIN,
    )

    call_command("seed_curriculum")

    admin_story.refresh_from_db()
    assert admin_story.title == "Operator-owned story title"
    assert admin_story.summary == "Operator-owned summary"
    assert admin_story.price == 987
    assert admin_story.is_published is False
    assert admin_story.management_source == MANAGEMENT_SOURCE_ADMIN

    admin_chapter.refresh_from_db()
    assert admin_chapter.title == "Operator-owned chapter title"
    assert admin_chapter.description == "Operator-owned chapter description"
    assert admin_chapter.is_published is False
    assert admin_chapter.is_playable is False
    assert admin_chapter.battle_stage == {"parallax": "operator-owned-stage"}
    assert admin_chapter.management_source == MANAGEMENT_SOURCE_ADMIN

    seed_story.refresh_from_db()
    seed_chapter.refresh_from_db()
    assert seed_story.title == STORIES[1]["title"]
    assert seed_story.management_source == MANAGEMENT_SOURCE_SEED
    assert seed_chapter.title == CHAPTERS[1]["title"]
    assert seed_chapter.management_source == MANAGEMENT_SOURCE_SEED

    official_runtime.adventure.refresh_from_db()
    authored_skill.refresh_from_db()
    assert official_runtime.adventure.chapter_id == seed_chapter.id
    assert official_runtime.adventure.is_published is True
    assert authored_skill.source_content_definition_id == official_content.id
    assert authored_skill.is_published is True

    admin_only_story.refresh_from_db()
    admin_only_chapter.refresh_from_db()
    assert admin_only_story.is_published is True
    assert admin_only_chapter.is_published is True
