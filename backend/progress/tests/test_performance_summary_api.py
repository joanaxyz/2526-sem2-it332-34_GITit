from django.core.management import call_command
from django.utils import timezone
from rest_framework.test import APIClient

from adventures.models import AdventureLevelTier, AdventureLevelTierRun
from common.constants import DIFFICULTY_HARD, SESSION_STATUS_COMPLETED, SESSION_STATUS_FAILED
from players.services import get_or_create_player
from practice.models import CommandStep
from progress.models import AdventureLevelTierCompletion, KpiCheckpoint
from progress.serializers import PerformanceSummaryResponseSerializer
from progress.services import MetricsService


def test_performance_summary_uses_runebound_attempts_and_server_side_formulas(
    db, django_user_model
):
    call_command("seed_curriculum", verbosity=0)
    user = django_user_model.objects.create_user(
        username="performance-reader",
        email="performance-reader@example.com",
        password="pass12345",
    )
    player = get_or_create_player(user)
    tier = AdventureLevelTier.objects.filter(
        adventure_level__chapter__story__slug="arcane-spire",
        adventure_level__chapter__number=1,
        difficulty=DIFFICULTY_HARD,
    ).first()
    assert tier is not None
    wave = tier.waves.first()
    assert wave is not None
    variant = wave.variants.first()
    assert variant is not None

    first = AdventureLevelTierRun.objects.create(
        player=player,
        tier=tier,
        current_wave=wave,
        selected_variant=variant,
        status=SESSION_STATUS_FAILED,
        retry_index=0,
    )
    retry = AdventureLevelTierRun.objects.create(
        player=player,
        tier=tier,
        current_wave=wave,
        selected_variant=variant,
        prior_run=first,
        status=SESSION_STATUS_COMPLETED,
        retry_index=1,
    )
    CommandStep.objects.create(
        adventure_tier_run=retry,
        command_text="git status",
        result_category=CommandStep.ResultCategory.TARGET_MATCHED,
        command_classification=CommandStep.CommandClassification.DIAGNOSTIC,
        normalized_command="git status",
        was_processable=True,
        attempt_number=1,
    )
    CommandStep.objects.create(
        adventure_tier_run=retry,
        command_text="git unknown",
        result_category=CommandStep.ResultCategory.INVALID,
        command_classification=CommandStep.CommandClassification.UNPROCESSABLE,
        normalized_command="git unknown",
        was_processable=False,
        attempt_number=2,
    )

    AdventureLevelTierCompletion.objects.create(player=player, tier=tier, tier_run=retry)
    KpiCheckpoint.objects.create(
        player=player,
        tier=tier,
        kind="car",
        run=retry,
        ref_count=3,
        actual=4,
        passed=True,
        retries=1,
        ended_at=timezone.now(),
    )
    AdventureLevelTierRun.objects.filter(pk__in=[first.id, retry.id]).update(
        ended_at=timezone.now()
    )
    client = APIClient()
    client.force_authenticate(user=user)
    response = client.get("/api/progress/performance/")

    assert response.status_code == 200
    payload = response.json()
    assert PerformanceSummaryResponseSerializer(data=payload).is_valid()
    assert payload["kpis"] == {
        "scr": {"value": 100.0, "numerator": 1, "denominator": 1},
        "car": {"value": 75.0, "numerator": 75, "denominator": 1},
        "hlcr": {"value": 100.0, "numerator": 1, "denominator": 1},
        # Module 1 same-variant retry: outside RTA scope, so RTA has no data,
        # while the learner retry success rate keeps its previous value.
        "rta": {"value": None, "numerator": 0, "denominator": 0},
        "retry_success_rate": {"value": 100.0, "numerator": 1, "denominator": 1},
        "rtr": {"value": 100.0, "numerator": 1, "denominator": 1},
        "arc": {"value": 1.0, "numerator": 1, "denominator": 1},
    }
    assert payload["completed_sessions"] == 1
    assert [module["number"] for module in payload["modules"]] == [1, 2, 3, 4]
    module_one = payload["modules"][0]
    assert module_one["scr"] == payload["kpis"]["scr"]
    assert module_one["hlcr"] == payload["kpis"]["hlcr"]
    assert module_one["rta"] == payload["kpis"]["rta"]
    assert module_one["retry_success_rate"] == payload["kpis"]["retry_success_rate"]
    assert module_one["arc"] == payload["kpis"]["arc"]
    assert MetricsService().admin_player_performance_summary(player=player) == payload


def test_admin_aggregate_spans_learners_while_player_endpoint_stays_scoped(db, django_user_model):
    """The staff aggregate must widen past the requester, and only the aggregate.

    Guards the boundary the admin split depends on: one learner's endpoint keeps
    reporting that learner, while ``all_player_performance_summary`` reports the
    union of every learner's Runebound attempts.
    """

    call_command("seed_curriculum", verbosity=0)
    tier = AdventureLevelTier.objects.filter(
        adventure_level__chapter__story__slug="arcane-spire",
        adventure_level__chapter__number=1,
        difficulty=DIFFICULTY_HARD,
    ).first()
    assert tier is not None
    wave = tier.waves.first()
    variant = wave.variants.first()

    players = []
    for index, status in enumerate((SESSION_STATUS_COMPLETED, SESSION_STATUS_FAILED)):
        user = django_user_model.objects.create_user(
            username=f"aggregate-learner-{index}",
            email=f"aggregate-learner-{index}@example.com",
            password="pass12345",
        )
        player = get_or_create_player(user)
        players.append((user, player))
        AdventureLevelTierRun.objects.create(
            player=player,
            tier=tier,
            current_wave=wave,
            selected_variant=variant,
            status=status,
            retry_index=0,
        )
        if status == SESSION_STATUS_COMPLETED:
            AdventureLevelTierCompletion.objects.create(player=player, tier=tier)

    first_user, _ = players[0]
    client = APIClient()
    client.force_authenticate(user=first_user)
    scoped = client.get("/api/progress/performance/").json()

    # The completing learner sees only their own perfect record.
    assert scoped["kpis"]["scr"] == {"value": 100.0, "numerator": 1, "denominator": 1}

    # Staff see both learners' attempts in one set.
    aggregate = MetricsService().all_player_performance_summary()
    assert aggregate["kpis"]["scr"] == {
        "value": 50.0,
        "numerator": 100,
        "denominator": 2,
        "unit": "participants",
    }
    assert aggregate != scoped
