from curriculum.seed_data.challenges import CHALLENGES
from curriculum.seed_data.source.adventure_level_specs import ADVENTURE_LEVELS
from curriculum.seed_data.spec_helpers import required_commit_message_details
from practice.services.context import ScenarioContextNormalizer


def _challenge_variants():
    for challenge in CHALLENGES:
        for level in challenge["levels"]:
            yield from level["variants"]


def _all_variants():
    for level in ADVENTURE_LEVELS:
        yield from level["variants"]
    yield from _challenge_variants()


def test_level_three_exposes_its_required_commit_message_in_the_brief():
    level = next(
        item for item in ADVENTURE_LEVELS if item["slug"] == "ch1-adv-commit-staged-snapshot"
    )

    for variant in level["variants"]:
        context = variant["scenario_context_template"]
        assert "commit message" in f"{context['story']} {context['task']}".lower()
        assert context["details"] == [
            {"label": "Commit message", "value": "Save staged work"}
        ]


def test_every_evaluator_required_typed_commit_message_is_exposed():
    checked = 0
    for variant in _all_variants():
        required = required_commit_message_details(
            variant.get("solution_commands_template"),
            variant.get("evaluation_spec_template"),
        )
        if not required:
            continue

        checked += 1
        context = variant["scenario_context_template"]
        copy_values = {
            detail["value"]
            for detail in context.get("details", [])
            if isinstance(detail, dict) and detail.get("value")
        }
        assert {detail["value"] for detail in required} <= copy_values
        assert "commit message" in f"{context.get('story', '')} {context.get('task', '')}".lower()

    assert checked > 800


def test_every_authored_copy_value_survives_context_normalization():
    checked = 0
    normalizer = ScenarioContextNormalizer()
    for variant in _all_variants():
        context = variant["scenario_context_template"]
        authored_values = [
            detail["value"]
            for detail in context.get("details", [])
            if isinstance(detail, dict) and detail.get("value")
        ]
        if not authored_values:
            continue

        checked += 1
        normalized = normalizer.normalize(context)
        assert [detail["value"] for detail in normalized.get("details", [])] == authored_values

    assert checked > 900


def test_required_message_extractor_ignores_automatic_messages_and_supports_compact_m_flag():
    evaluation = {
        "state_requirements": {
            "latest_commit": {"message_contains": ["Save tracked work"]}
        }
    }

    assert required_commit_message_details(
        ["git merge feature/ui", "git commit -am 'Save tracked work'"], evaluation
    ) == [{"label": "Commit message", "value": "Save tracked work"}]
    assert required_commit_message_details(
        ["git merge feature/ui"],
        {"state_requirements": {"latest_commit": {"message_contains": ["Merge"]}}},
    ) == []
