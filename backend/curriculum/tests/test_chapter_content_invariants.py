from django.core.management import call_command

from adventures.models import (
    AdventureLevel,
    AdventureWave,
    AdventureWaveVariant,
)
from challenges.models import ChallengeLevel, ChallengeTrial, ChallengeTrialVariant
from curriculum.models import Chapter, ChapterLesson, CommandForm
from curriculum.seed_data.blueprint_overlay import (
    BLUEPRINT_ADVENTURE_LEVELS,
    BLUEPRINT_CHALLENGE_SPECS,
)
from curriculum.seed_data.challenges import CHALLENGES
from curriculum.seed_data.chapters import (
    ARCANE_SPIRE_CHAPTERS,
    PLAYABLE_CHAPTERS,
    REFERENCE_CHAPTERS,
)

OLD_COPY_DETAIL_LABELS = {
    "Practice focus",
    "Starting state",
    "Required moves",
    "Blueprint ledger",
}
OLD_COPY_PHRASES = [
    "Blueprint scenario",
    "Complete the requested Git workflow",
    "blueprint challenge",
    "without checklist scaffolding",
    "This is the easy version",
    "This is the medium version",
    "This is the hard version",
    "Chapter focus:",
    "Start:",
    "Target:",
]


def test_seed_creates_chapter_owned_adventure_and_challenge_levels(db):
    call_command("seed_curriculum")

    playable_chapters = Chapter.objects.filter(
        slug__in=[spec["slug"] for spec in ARCANE_SPIRE_CHAPTERS]
    )
    for chapter in playable_chapters:
        assert chapter.is_playable is True
        assert AdventureLevel.objects.filter(chapter=chapter, is_published=True).exists()
        assert ChallengeLevel.objects.filter(chapter=chapter, is_published=True).exists()

    advanced_chapters = Chapter.objects.filter(
        slug__in=[spec["slug"] for spec in REFERENCE_CHAPTERS]
    )
    for chapter in advanced_chapters:
        assert chapter.is_playable is True
        assert ChapterLesson.objects.filter(chapter=chapter, is_published=True).count() >= 3
        levels = AdventureLevel.objects.filter(chapter=chapter, is_published=True)
        assert levels.count() >= 3
        assert CommandForm.objects.filter(adventure_levels__in=levels, is_published=True).exists()
        # A chapter can carry several challenge levels; each keeps the full
        # easy/medium/hard tier with strategy-distinct variants.
        challenge_levels = list(ChallengeLevel.objects.filter(chapter=chapter, is_published=True))
        assert len(challenge_levels) >= 2
        for challenge in challenge_levels:
            trials = challenge.trials.filter(is_published=True)
            assert set(trials.values_list("difficulty", flat=True)) == {"easy", "medium", "hard"}
            assert all(trial.variants.filter(is_published=True).count() >= 4 for trial in trials)



def test_seed_uses_authored_wave_plans_beyond_chapter_one(db):
    """The seeded level and wave order per chapter is exactly the blueprint
    ledger: each chapter's sources in ADVENTURE_SOURCES order, each source's
    level groups in ledger order, each level's waves in ledger order. Nothing
    outside the ledger is published."""
    from curriculum.seed_data.adventures import ADVENTURE_SOURCES

    call_command("seed_curriculum")

    official_chapter_slugs = [
        spec["slug"]
        for spec in ARCANE_SPIRE_CHAPTERS
        if any(
            source["slug"] in BLUEPRINT_ADVENTURE_LEVELS
            for source in ADVENTURE_SOURCES.get(spec["slug"], [])
        )
    ]
    for chapter_slug in official_chapter_slugs:
        expected_levels = [
            level
            for source in ADVENTURE_SOURCES.get(chapter_slug, [])
            for level in BLUEPRINT_ADVENTURE_LEVELS.get(source["slug"], [])
        ]
        assert expected_levels, f"{chapter_slug} has no blueprint levels"
        seeded_levels = list(
            AdventureLevel.objects.filter(
                chapter__slug=chapter_slug,
                is_published=True,
            ).order_by("sort_order", "id")
        )
        assert [level.slug for level in seeded_levels] == [
            level["slug"] for level in expected_levels
        ]
        for seeded, expected in zip(seeded_levels, expected_levels, strict=True):
            assert list(
                seeded.waves.filter(is_published=True)
                .order_by("sort_order", "id")
                .values_list("slug", flat=True)
            ) == [wave["slug"] for wave in expected["waves"]]


def test_seed_publishes_every_blueprint_ledger_entry(db):
    call_command("seed_curriculum")

    expected_waves = {
        wave["slug"]
        for levels in BLUEPRINT_ADVENTURE_LEVELS.values()
        for level in levels
        for wave in level["waves"]
    }
    assert expected_waves
    assert set(
        AdventureWave.objects.filter(slug__in=expected_waves, is_published=True).values_list(
            "slug", flat=True
        )
    ) == expected_waves
    assert AdventureWaveVariant.objects.filter(
        wave__slug__in=expected_waves,
        is_published=True,
    ).count() == len(expected_waves) * 2
    for context in AdventureWaveVariant.objects.filter(
        wave__slug__in=expected_waves,
        is_published=True,
    ).values_list("scenario_context", flat=True):
        assert set(context) <= {"schema_version", "story", "task", "details"}
        assert "constraints" not in context
        assert not any(
            detail.get("label") in OLD_COPY_DETAIL_LABELS
            for detail in context.get("details", [])
        )
    for phrase in OLD_COPY_PHRASES:
        assert not AdventureWave.objects.filter(
            slug__in=expected_waves,
            story__icontains=phrase,
        ).exists()
        assert not AdventureWave.objects.filter(
            slug__in=expected_waves,
            task__icontains=phrase,
        ).exists()

    assert ChallengeLevel.objects.filter(is_published=True).count() == len(CHALLENGES)
    assert ChallengeTrial.objects.filter(is_published=True).count() == len(CHALLENGES) * 3
    for phrase in OLD_COPY_PHRASES:
        assert not ChallengeTrial.objects.filter(
            story__icontains=phrase,
        ).exists()
        assert not ChallengeTrial.objects.filter(
            task__icontains=phrase,
        ).exists()

    expected_cases = {
        f"{slug[:3]}-challenge-{difficulty}{suffix}"
        for _, slug, _, _ in BLUEPRINT_CHALLENGE_SPECS
        for difficulty in ["easy", "medium", "hard"]
        for suffix in ["", "-alt"]
    }
    assert set(
        ChallengeTrialVariant.objects.filter(
            case_id__in=expected_cases, is_published=True
        ).values_list("case_id", flat=True)
    ) == expected_cases
    for context in ChallengeTrialVariant.objects.filter(
        case_id__in=expected_cases,
        is_published=True,
    ).values_list("scenario_context", flat=True):
        assert set(context) <= {"schema_version", "story", "task", "details"}
        assert "constraints" not in context
        assert context.get("details", []) == []
        assert not any(
            detail.get("label") in OLD_COPY_DETAIL_LABELS
            for detail in context.get("details", [])
        )


def test_first_wave_of_curriculum_is_playable_and_story_first(db):
    """Whatever wave a brand-new player meets first must carry a story with no
    command spoilers, an objective checklist, and an empty synthesized task."""
    call_command("seed_curriculum")

    first_level = (
        AdventureLevel.objects.filter(
            chapter__slug__in=[spec["slug"] for spec in PLAYABLE_CHAPTERS],
            is_published=True,
        )
        .order_by("chapter__sort_order", "sort_order", "id")
        .first()
    )
    assert first_level is not None
    wave = first_level.waves.filter(is_published=True).order_by("sort_order", "id").first()
    assert wave is not None
    assert wave.task == ""
    assert wave.story.strip()
    assert "git " not in wave.story.lower()
    assert wave.objective_checks
    assert wave.variants.filter(is_published=True).count() == 2


def test_init_current_folder_wave_has_stateful_story_and_objectives(db):
    call_command("seed_curriculum")

    wave = AdventureWave.objects.get(slug="ch1-adv-init-current-folder", is_published=True)
    assert wave.task == ""
    assert "README.md" in wave.story
    assert "src/app.py" in wave.story
    assert "git init" not in wave.story.lower()
    assert "git add" not in wave.story.lower()
    assert "git commit" not in wave.story.lower()
    assert [check["label"] for check in wave.objective_checks] == [
        "The current folder is now a Git repository.",
        "Both starter files are saved in the first snapshot.",
        "No starter work is left uncommitted.",
    ]

    variant = wave.variants.filter(is_published=True).first()
    assert variant is not None
    assert variant.scenario_context.get("details") == [
        {"label": "Commit message", "value": "Initial commit"}
    ]
    assert variant.evaluation_spec["state_requirements"]["latest_commit"] == {
        "branch": "main",
        "contains_paths": ["README.md", "src/app.py"],
        "message_contains": ["Initial commit"],
    }
    assert variant.evaluation_spec["state_requirements"]["working_tree_clean"] is True
    assert variant.evaluation_spec["state_requirements"]["staging_empty"] is True
