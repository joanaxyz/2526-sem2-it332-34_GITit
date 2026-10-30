import pytest
from django.db import IntegrityError, transaction

from adventures.models import AdventureLevelTierRun, AdventureLevelTierScenario
from challenges.models import ChallengeRun, ChallengeTrial
from practice.models import CommandStep
from progress.models import (
    AdventureLevelTierCompletion,
    ChallengeTrialCompletion,
    CoinTransaction,
)
from testing.runtime_factories import (
    create_stage_readme_challenge_run,
    create_stage_readme_tier_run,
)

pytestmark = pytest.mark.django_db


def _assert_constraint_rejects(update) -> None:
    with pytest.raises(IntegrityError), transaction.atomic():
        update()


def test_adventure_budget_and_star_constraints(django_user_model):
    fixture = create_stage_readme_tier_run(django_user_model)

    _assert_constraint_rejects(
        lambda: AdventureLevelTierScenario.objects.filter(pk=fixture.scenario.pk).update(
            min_counted_commands=4,
            max_counted_commands=3,
        )
    )
    _assert_constraint_rejects(
        lambda: AdventureLevelTierRun.objects.filter(pk=fixture.run.pk).update(stars=4)
    )


def test_challenge_budget_and_star_constraints(django_user_model):
    fixture = create_stage_readme_challenge_run(django_user_model)

    _assert_constraint_rejects(
        lambda: ChallengeTrial.objects.filter(pk=fixture.trial.pk).update(
            min_counted_commands=0,
        )
    )
    _assert_constraint_rejects(
        lambda: ChallengeRun.objects.filter(pk=fixture.run.pk).update(
            min_counted_commands=4,
            max_counted_commands=3,
        )
    )
    _assert_constraint_rejects(
        lambda: ChallengeRun.objects.filter(pk=fixture.run.pk).update(stars=4)
    )


def test_completion_stars_are_bounded(django_user_model):
    adventure = create_stage_readme_tier_run(django_user_model)
    challenge = create_stage_readme_challenge_run(django_user_model)

    _assert_constraint_rejects(
        lambda: AdventureLevelTierCompletion.objects.create(
            player=adventure.player,
            tier=adventure.tier,
            tier_run=adventure.run,
            stars=4,
        )
    )
    _assert_constraint_rejects(
        lambda: ChallengeTrialCompletion.objects.create(
            player=challenge.player,
            challenge_trial=challenge.trial,
            challenge_run=challenge.run,
            stars=4,
        )
    )


def test_progress_and_command_step_counters_are_consistent(django_user_model):
    fixture = create_stage_readme_challenge_run(django_user_model)
    _assert_constraint_rejects(
        lambda: CoinTransaction.objects.create(
            player=fixture.player,
            amount=0,
            reason="invalid_zero_value",
            award_key="invalid-zero-value",
        )
    )

    step = {
        "challenge_run": fixture.run,
        "command_text": "git status",
        "result_category": CommandStep.ResultCategory.TARGET_NOT_YET_MATCHED,
        "command_classification": CommandStep.CommandClassification.DIAGNOSTIC,
    }
    _assert_constraint_rejects(
        lambda: CommandStep.objects.create(
            **step,
            attempt_number=0,
        )
    )
    _assert_constraint_rejects(
        lambda: CommandStep.objects.create(
            **step,
            attempt_number=1,
            counted_increment=2,
            counted_total_after=2,
        )
    )
    _assert_constraint_rejects(
        lambda: CommandStep.objects.create(
            **step,
            attempt_number=1,
            counted_increment=1,
            counted_total_after=0,
        )
    )
