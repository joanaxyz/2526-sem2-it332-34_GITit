"""Runtime fixtures for the planned and gate scenarios authored in ``extension_scenarios.md``.

Each module maps a Variant ID to the parts of a case the Markdown cannot own:
the starting repository, the state requirements and any required commands.
The learner-facing text and the answer key come from ``scenario_bank_extension.json``.
"""

from __future__ import annotations

from typing import Any

from curriculum.seed_data.source.scenario_fixtures.gates import FIXTURES as GATES
from curriculum.seed_data.source.scenario_fixtures.module_1 import FIXTURES as MODULE_1
from curriculum.seed_data.source.scenario_fixtures.module_2 import FIXTURES as MODULE_2
from curriculum.seed_data.source.scenario_fixtures.module_3 import FIXTURES as MODULE_3
from curriculum.seed_data.source.scenario_fixtures.module_4 import FIXTURES as MODULE_4

SCENARIO_FIXTURES: dict[str, dict[str, Any]] = {}
for _module in (MODULE_1, MODULE_2, MODULE_3, MODULE_4, GATES):
    _overlap = SCENARIO_FIXTURES.keys() & _module.keys()
    if _overlap:
        raise RuntimeError(f"Duplicate scenario fixture IDs: {sorted(_overlap)}")
    SCENARIO_FIXTURES.update(_module)


def extension_case(case_id: str) -> dict[str, Any]:
    """A seedable case for a planned or gate scenario: fixture plus authored bank entry."""
    from curriculum.seed_data.scenario_bank import extension_scenario_bank

    authored = extension_scenario_bank()[case_id]
    fixture = SCENARIO_FIXTURES[case_id]
    return {
        "case_id": case_id,
        "label": authored["label"],
        "context": authored["story"],
        "initial_state": fixture["initial_state"],
        "state_requirements": fixture["state_requirements"],
        "solution_commands": list(authored["solution_commands"]),
        "solution_workspace_files": list(authored["solution_workspace_files"]),
        "max_counted_commands": authored["maximum_counted_commands"],
    }


def extension_cases() -> dict[str, dict[str, Any]]:
    from curriculum.seed_data.scenario_bank import extension_scenario_bank

    missing = sorted(set(SCENARIO_FIXTURES) - set(extension_scenario_bank()))
    if missing:
        raise RuntimeError(f"Scenario fixtures without authored scenarios: {missing}")
    return {case_id: extension_case(case_id) for case_id in SCENARIO_FIXTURES}

