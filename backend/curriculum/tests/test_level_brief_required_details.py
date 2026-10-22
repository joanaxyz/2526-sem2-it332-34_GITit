from django.core.management import call_command

from adventures.models import AdventureLevelTierScenarioVariant
from challenges.models import ChallengeTrialVariant
from curriculum.seed_data.spec_helpers import required_commit_message_details
from practice.services.context import ScenarioContextNormalizer


def _seeded_variants():
    """Every published tier-scenario and Challenge Gate variant of the live seed."""
    yield from AdventureLevelTierScenarioVariant.objects.filter(is_published=True)
    yield from ChallengeTrialVariant.objects.filter(is_published=True)


def _detail_values(context: dict) -> list[str]:
    return [
        detail["value"]
        for detail in context.get("details", [])
        if isinstance(detail, dict) and detail.get("value")
    ]


def test_every_evaluator_required_typed_commit_message_is_exposed(db):
    call_command("seed_curriculum", verbosity=0)
    checked = 0
    for variant in _seeded_variants():
        required = required_commit_message_details(
            variant.solution_commands, variant.evaluation_spec
        )
        if not required:
            continue
        checked += 1
        assert {detail["value"] for detail in required} <= set(
            _detail_values(variant.scenario_context)
        ), variant.slug

    assert checked > 40


def test_every_authored_copy_value_survives_context_normalization(db):
    call_command("seed_curriculum", verbosity=0)
    checked = 0
    normalizer = ScenarioContextNormalizer()
    for variant in _seeded_variants():
        authored_values = _detail_values(variant.scenario_context)
        if not authored_values:
            continue
        checked += 1
        normalized = normalizer.normalize(variant.scenario_context)
        assert _detail_values(normalized) == authored_values, variant.slug

    assert checked > 40


def test_required_message_extractor_ignores_automatic_messages_and_supports_compact_m_flag():
    evaluation = {
        "state_requirements": {"latest_commit": {"message_contains": ["Save tracked work"]}}
    }

    assert required_commit_message_details(
        ["git merge feature/ui", "git commit -am 'Save tracked work'"], evaluation
    ) == [{"label": "Commit message", "value": "Save tracked work"}]
    assert (
        required_commit_message_details(
            ["git merge feature/ui"],
            {"state_requirements": {"latest_commit": {"message_contains": ["Merge"]}}},
        )
        == []
    )
