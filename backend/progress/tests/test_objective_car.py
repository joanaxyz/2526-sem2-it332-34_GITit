"""Per-SO CAR: the static SO-to-level mapping and its computation."""

from django.core.management import call_command
from rest_framework.test import APIClient

from adventures.models import (
    AdventureLevel,
)
from progress.objectives import SO_CAR_LEVELS
from progress.services import MetricsService

NO_DATA = {"value": None, "numerator": 0, "denominator": 0}

OFFICIAL_CAR_SOS = [
    *(f"SO 1.{n}" for n in range(1, 7)),
    *(f"SO 2.{n}" for n in range(1, 10)),
    *(f"SO 3.{n}" for n in range(1, 4)),
    *(f"SO 4.{n}" for n in range(1, 4)),
]


def test_mapping_covers_exactly_the_official_car_objectives():
    assert list(SO_CAR_LEVELS) == OFFICIAL_CAR_SOS
    for so_code, slugs in SO_CAR_LEVELS.items():
        assert slugs, so_code


def test_every_mapped_level_exists_in_seeded_legacy_content(db):
    call_command("seed_curriculum", verbosity=0)
    published = set(
        AdventureLevel.objects.filter(
            chapter__story__slug=MetricsService.PERFORMANCE_STORY_SLUG, is_published=True
        ).values_list("slug", flat=True)
    )
    mapped = {slug for slugs in SO_CAR_LEVELS.values() for slug in slugs}
    assert mapped <= published, sorted(mapped - published)


def test_per_so_car_groups_assessments_by_level_and_balances_players(db, django_user_model):
    from testing.kpi_fixtures import bundle, end, start

    player, tier, _, _ = bundle(django_user_model, required=1)
    level = tier.adventure_level
    level.slug = "resolving-conflicts-manually"
    level.save()
    end(start(player, tier), count=4)
    end(start(player, tier), count=3)  # Better replay must not replace CAR.
    objectives = MetricsService().all_player_objective_car()
    assert objectives["SO 3.1"] == {
        "value": 75,
        "numerator": 75,
        "denominator": 1,
        "unit": "participants",
    }
    assert all(rate["value"] is None for code, rate in objectives.items() if code != "SO 3.1")
    staff = django_user_model.objects.create_user(username="so-admin", is_staff=True)
    client = APIClient()
    client.force_authenticate(user=staff)
    assert client.get("/api/admin/analytics/").json()["objectives"] == objectives


def test_per_so_car_without_assessments_is_null_for_every_so(db):
    objectives = MetricsService().all_player_objective_car()
    assert set(objectives) == set(OFFICIAL_CAR_SOS)
    assert all(rate["value"] is None and rate["denominator"] == 0 for rate in objectives.values())


def test_learner_objectives_are_scoped_by_player_and_scenario_and_keep_first_assessment(
    db, django_user_model
):
    from testing.kpi_fixtures import bundle, end, start

    learner, tier, _, _ = bundle(django_user_model, username="objective-reader", required=1)
    level = tier.adventure_level
    level.slug = "resolving-conflicts-manually"
    level.save()
    end(start(learner, tier), count=4)
    end(start(learner, tier), count=3)  # Replay must not replace the 75% assessment.

    other, other_tier, _, _ = bundle(django_user_model, username="objective-other", required=1)
    other_level = other_tier.adventure_level
    other_level.slug = "using-a-merge-tool"
    other_level.save()
    end(start(other, other_tier), count=3)

    client = APIClient()
    client.force_authenticate(user=learner.user)
    response = client.get("/api/progress/performance/")
    assert response.status_code == 200
    objectives = response.json()["objectives"]
    assert set(objectives) == set(OFFICIAL_CAR_SOS)
    assert objectives["SO 3.1"] == {"value": 75, "numerator": 75, "denominator": 1}
    assert objectives["SO 3.2"] == NO_DATA  # Other learner's mastery is private.

    # Unlock the hard tier through the same prerequisite used by learners.
    from adventures.models import AdventureLevelTier
    from progress.models import AdventureLevelTierCompletion

    AdventureLevelTierCompletion.objects.create(
        player=learner,
        tier=AdventureLevelTier.objects.get(adventure_level=other_level, difficulty="medium"),
    )
    # Same learner, different mapped scenario contributes only to its own SO.
    end(start(learner, other_tier), count=3)
    objectives = client.get("/api/progress/performance/").json()["objectives"]
    assert objectives["SO 3.1"]["value"] == 75
    assert objectives["SO 3.2"]["value"] == 100
    assert objectives["SO 3.3"] == NO_DATA


def test_empty_learner_summary_includes_all_car_objectives(db, django_user_model):
    from players.services import get_or_create_player
    from progress.serializers import PerformanceSummaryResponseSerializer

    player = get_or_create_player(
        django_user_model.objects.create_user(username="empty-objectives")
    )
    summary = MetricsService().performance_summary(player=player)
    assert set(summary["objectives"]) == set(OFFICIAL_CAR_SOS)
    assert all(rate == NO_DATA for rate in summary["objectives"].values())
    serializer = PerformanceSummaryResponseSerializer(data=summary)
    assert serializer.is_valid(), serializer.errors
