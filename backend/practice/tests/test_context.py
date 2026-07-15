from practice.services.context import ScenarioContextNormalizer


def test_scenario_context_normalizer_keeps_only_story_schema_keys():
    context = ScenarioContextNormalizer().normalize(
        {
            "schema_version": 3,
            "story": "A branch needs review.",
            "task": "Inspect the branch before changing it.",
            "details": [{"label": "Branch", "value": "feature/auth"}],
            "intro": "legacy intro",
            "constraints": ["legacy constraint"],
            "solution_commands": ["git status"],
        },
        fallback_story="Fallback story",
    )

    assert context == {
        "schema_version": 3,
        "story": "A branch needs review.",
        "task": "Inspect the branch before changing it.",
        "details": [{"label": "Branch", "value": "feature/auth"}],
    }
