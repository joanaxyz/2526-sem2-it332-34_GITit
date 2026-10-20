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
