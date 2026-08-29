import pytest
from django.db import IntegrityError, transaction

from adventures.models import AdventureRun, AdventureWave
from authoring.compiler import ContentRuntimeCompiler
from authoring.models import ContentDefinition, ContentKind, PublishedContentRuntime
from challenges.models import ChallengeRun, ChallengeTrial
from practice.models import CommandStep
from progress.models import (
    AdventureLevelCompletion,
    ChallengeTrialCompletion,
    CoinTransaction,
    StreakRecord,
)
from testing.runtime_factories import (
    create_stage_readme_adventure_run,
    create_stage_readme_challenge_run,
)

pytestmark = pytest.mark.django_db


def _assert_constraint_rejects(update) -> None:
    with pytest.raises(IntegrityError), transaction.atomic():
        update()


def test_adventure_budget_and_star_constraints(django_user_model):
    fixture = create_stage_readme_adventure_run(django_user_model)

    _assert_constraint_rejects(
        lambda: AdventureWave.objects.filter(pk=fixture.wave.pk).update(
            min_counted_commands=4,
            max_counted_commands=3,
        )
    )
    _assert_constraint_rejects(
        lambda: AdventureRun.objects.filter(pk=fixture.run.pk).update(stars=4)
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
    adventure = create_stage_readme_adventure_run(django_user_model)
    challenge = create_stage_readme_challenge_run(django_user_model)

    _assert_constraint_rejects(
        lambda: AdventureLevelCompletion.objects.create(
            player=adventure.player,
            adventure_level=adventure.level,
            adventure_run=adventure.run,
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
    StreakRecord.objects.get_or_create(player=fixture.player)

    _assert_constraint_rejects(
        lambda: StreakRecord.objects.filter(player=fixture.player).update(
            current_streak=2,
            longest_streak=1,
        )
    )
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


def test_system_content_slugs_are_unique_per_kind():
    ContentDefinition.objects.create(
        owner=None,
        kind=ContentKind.LESSON,
        slug="system-lesson",
        title="System lesson",
    )

    _assert_constraint_rejects(
        lambda: ContentDefinition.objects.create(
            owner=None,
            kind=ContentKind.LESSON,
            slug="system-lesson",
            title="Duplicate system lesson",
        )
    )


def test_unknown_content_visibility_is_rejected():
    _assert_constraint_rejects(
        lambda: ContentDefinition.objects.create(
            owner=None,
            kind=ContentKind.LESSON,
            slug="unknown-visibility",
            title="Unknown visibility",
            visibility="store",
        )
    )


def test_published_runtime_requires_exactly_one_target(django_user_model):
    owner = django_user_model.objects.create_user(username="runtime-constraint-author")
    content = ContentDefinition.objects.create(
        owner=owner,
        kind=ContentKind.LESSON,
        slug="runtime-constraint",
        title="Runtime constraint",
        definition={"pages": []},
    )
    runtime = ContentRuntimeCompiler().compile(content=content)

    _assert_constraint_rejects(
        lambda: PublishedContentRuntime.objects.filter(pk=runtime.pk).update(lesson=None)
    )


def test_compiler_can_replace_a_constrained_runtime(django_user_model):
    owner = django_user_model.objects.create_user(username="runtime-recompile-author")
    content = ContentDefinition.objects.create(
        owner=owner,
        kind=ContentKind.LESSON,
        slug="runtime-recompile",
        title="Runtime recompile",
        definition={"pages": [{"title": "First"}]},
    )
    first = ContentRuntimeCompiler().compile(content=content)
    content.definition = {"pages": [{"title": "Second"}]}
    content.save(update_fields=["definition"])

    second = ContentRuntimeCompiler().compile(content=content)

    assert second.pk != first.pk
    assert second.lesson.pages == [{"title": "Second"}]
