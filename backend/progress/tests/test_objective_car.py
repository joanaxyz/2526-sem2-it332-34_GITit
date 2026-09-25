"""Per-SO CAR: the static SO-to-level mapping and its computation."""

from django.core.management import call_command
from rest_framework.test import APIClient

from adventures.models import (
    AdventureLevel,
    AdventureLevelTier,
    AdventureLevelTierRun,
    AdventureLevelTierWave,
    AdventureLevelTierWaveVariant,
)
from common.constants import SESSION_STATUS_COMPLETED
from curriculum.models import Chapter, Story
from players.services import get_or_create_player
from practice.models import CommandStep
from progress.objectives import SO_CAR_LEVELS
from progress.services import MetricsService

NO_DATA = {"value": None, "numerator": 0, "denominator": 0}

OFFICIAL_CAR_SOS = [
    *(f"SO 1.{n}" for n in range(1, 7)),
    *(f"SO 2.{n}" for n in range(1, 10)),
    *(f"SO 3.{n}" for n in range(1, 4)),
    *(f"SO 4.{n}" for n in range(1, 4)),
]


def _tier(story, chapter_number, level_slug):
    chapter, _ = Chapter.objects.get_or_create(
        story=story,
        number=chapter_number,
        defaults={"slug": f"{story.slug}-m{chapter_number}", "title": f"Module {chapter_number}"},
    )
    level = AdventureLevel.objects.create(chapter=chapter, slug=level_slug, title=level_slug)
    tier = AdventureLevelTier.objects.create(adventure_level=level, difficulty="easy")
    wave = AdventureLevelTierWave.objects.create(tier=tier, slug=f"{story.slug}-{level_slug}")
    variant = AdventureLevelTierWaveVariant.objects.create(
        wave=wave, slug=f"{story.slug}-{level_slug}-v", label="v"
    )
    return tier, wave, variant


def _run_with_steps(player, bundle, *, processable, unprocessable, **extra):
    tier, wave, variant = bundle
    run = AdventureLevelTierRun.objects.create(
        player=player,
        tier=tier,
        current_wave=wave,
        selected_variant=variant,
        status=SESSION_STATUS_COMPLETED,
        **extra,
    )
    attempt = 0
    for ok in [True] * processable + [False] * unprocessable:
        attempt += 1
        CommandStep.objects.create(
            adventure_tier_run=run,
            command_text="git status" if ok else "git nonsense",
            normalized_command="git status" if ok else "git nonsense",
            result_category=(
                CommandStep.ResultCategory.TARGET_MATCHED
                if ok
                else CommandStep.ResultCategory.INVALID
            ),
            command_classification=(
                CommandStep.CommandClassification.DIAGNOSTIC
                if ok
                else CommandStep.CommandClassification.UNPROCESSABLE
            ),
            was_processable=ok,
            attempt_number=attempt,
        )
    return run


def test_mapping_covers_exactly_the_official_car_objectives():
    assert list(SO_CAR_LEVELS) == OFFICIAL_CAR_SOS
    for so_code, slugs in SO_CAR_LEVELS.items():
        assert slugs, so_code


def test_every_mapped_level_exists_in_seeded_legacy_content(db):
    call_command("seed_legacy_modules", verbosity=0)
    published = set(
        AdventureLevel.objects.filter(
            chapter__story__slug=MetricsService.PERFORMANCE_STORY_SLUG, is_published=True
        ).values_list("slug", flat=True)
    )
    mapped = {slug for slugs in SO_CAR_LEVELS.values() for slug in slugs}
    assert mapped <= published, sorted(mapped - published)


def test_per_so_car_groups_commands_by_mapped_level(db, django_user_model):
    legacy = Story.objects.create(slug=MetricsService.PERFORMANCE_STORY_SLUG, title="Legacy")
    other = Story.objects.create(slug="other-story", title="Other")
    init = _tier(legacy, 1, "initializing-a-local-repository")
    cherry = _tier(legacy, 3, "cherry-picking-commits")
    unmapped = _tier(legacy, 1, "inspecting-repository-state")
    other_init = _tier(other, 1, "initializing-a-local-repository-copy")

    player = get_or_create_player(
        django_user_model.objects.create_user(username="so-car", password="pass12345")
    )
    # SO 1.1: 3 processable + 1 invalid across two runs = 75%.
    _run_with_steps(player, init, processable=2, unprocessable=1)
    _run_with_steps(player, init, processable=1, unprocessable=0)
    # SO 3.3: 1 processable = 100%.
    _run_with_steps(player, cherry, processable=1, unprocessable=0)
    # Excluded: replays, an unmapped level, and another story.
    _run_with_steps(player, init, processable=0, unprocessable=5, is_replay=True)
    _run_with_steps(player, unmapped, processable=0, unprocessable=4)
    _run_with_steps(player, other_init, processable=0, unprocessable=3)

    objectives = MetricsService().all_player_objective_car()

    assert list(objectives) == OFFICIAL_CAR_SOS
    assert objectives["SO 1.1"] == {"value": 75.0, "numerator": 3, "denominator": 4}
    assert objectives["SO 3.3"] == {"value": 100.0, "numerator": 1, "denominator": 1}
    assert all(
        objectives[so] == NO_DATA for so in OFFICIAL_CAR_SOS if so not in {"SO 1.1", "SO 3.3"}
    )
    # The unmapped level still counts toward overall CAR, like before.
    overall = MetricsService().all_player_performance_summary()["kpis"]["car"]
    assert overall == {"value": 44.4, "numerator": 4, "denominator": 9}

    staff = django_user_model.objects.create_user(
        username="so-car-staff", password="pass12345", is_staff=True
    )
    client = APIClient()
    client.force_authenticate(user=staff)
    body = client.get("/api/admin/analytics/").json()
    assert body["objectives"] == objectives


def test_per_so_car_without_commands_is_null_for_every_so(db):
    Story.objects.create(slug=MetricsService.PERFORMANCE_STORY_SLUG, title="Legacy")

    objectives = MetricsService().all_player_objective_car()

    assert objectives == {so: NO_DATA for so in OFFICIAL_CAR_SOS}
