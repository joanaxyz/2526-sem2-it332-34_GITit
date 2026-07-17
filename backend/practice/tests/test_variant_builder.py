from adventures.models import AdventureLevel, AdventureWave
from challenges.models import ChallengeLevel, ChallengeTrial
from common.constants import RESULT_TARGET_MATCHED
from evaluation.compiler import compile_evaluation_spec
from evaluation.engine import EvaluationEngine
from practice.services.builders import StaticLevelVariantBuilder
from testing.runtime_factories import create_test_chapter, unique_suffix


def _outcome_only_template(case_id: str) -> tuple[dict, dict]:
    return (
        {
            "slug": "outcome-only",
            "slug_template": "{{case_id}}",
            "initial_state_template": {"repository_initialized": False},
            "target_state_template": {"repository_initialized": True},
            "solution_commands_template": ["git init"],
            "evaluation_spec_template": {
                "state_requirements": {"repository_initialized": True},
                "completion_policy": {"mode": "rules"},
            },
        },
        {"case_id": case_id},
    )


def test_builder_keeps_ordinary_adventures_and_challenges_outcome_based(db):
    suffix = unique_suffix()
    _, chapter = create_test_chapter(suffix=f"builder-{suffix}")
    adventure_level = AdventureLevel.objects.create(
        chapter=chapter,
        slug=f"adventure-{suffix}",
        title="Outcome Adventure",
    )
    adventure_wave = AdventureWave.objects.create(
        level=adventure_level,
        slug=f"wave-{suffix}",
        title="Outcome Wave",
    )
    challenge_level = ChallengeLevel.objects.create(
        chapter=chapter,
        slug=f"challenge-{suffix}",
        title="Outcome Challenge",
    )
    challenge_trial = ChallengeTrial.objects.create(
        challenge_level=challenge_level,
        difficulty=ChallengeTrial.Difficulty.EASY,
    )
    builder = StaticLevelVariantBuilder()

    for index, level in enumerate((adventure_wave, challenge_trial), start=1):
        template, case = _outcome_only_template(f"outcome-{index}-{suffix}")
        variant = builder.build(level=level, template=template, case=case, index=index)
        serialized_spec = str(variant.evaluation_spec)
        assert "required_command_sequence" not in serialized_spec

        outcome = EvaluationEngine().evaluate(
            spec=compile_evaluation_spec(variant.evaluation_spec),
            next_state=variant.target_state,
            initial_state=variant.initial_state,
            executed_commands=["git status"],
        )
        assert outcome.result_category == RESULT_TARGET_MATCHED
