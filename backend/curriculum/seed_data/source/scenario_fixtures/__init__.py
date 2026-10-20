"""Runtime fixtures for the wave and gate scenarios authored in ``wave_scenarios.md``.

Each module maps a Variant ID to the parts of a case the Markdown cannot own:
the starting repository, the state requirements and any required commands.
The learner-facing text and the answer key come from ``scenario_bank_waves.json``.
"""

from __future__ import annotations

from typing import Any

from curriculum.seed_data.source.scenario_fixtures.gates import FIXTURES as GATES
from curriculum.seed_data.source.scenario_fixtures.module_1 import FIXTURES as MODULE_1
from curriculum.seed_data.source.scenario_fixtures.module_2 import FIXTURES as MODULE_2
from curriculum.seed_data.source.scenario_fixtures.module_3 import FIXTURES as MODULE_3

WAVE_FIXTURES: dict[str, dict[str, Any]] = {}
for _module in (MODULE_1, MODULE_2, MODULE_3, GATES):
    _overlap = WAVE_FIXTURES.keys() & _module.keys()
    if _overlap:
        raise RuntimeError(f"Duplicate wave fixture IDs: {sorted(_overlap)}")
    WAVE_FIXTURES.update(_module)


def extension_case(case_id: str) -> dict[str, Any]:
    """A seedable case for a wave or gate scenario: fixture plus authored bank entry."""
    from curriculum.seed_data.scenario_bank import wave_scenario_bank

    authored = wave_scenario_bank()[case_id]
    fixture = WAVE_FIXTURES[case_id]
    return {
        "case_id": case_id,
        "label": authored["label"],
        "context": authored["story"],
        "initial_state": fixture["initial_state"],
        "state_requirements": fixture["state_requirements"],
        "required_commands": fixture.get("required_commands", []),
        "solution_commands": list(authored["solution_commands"]),
        "solution_workspace_files": list(authored["solution_workspace_files"]),
        "max_counted_commands": authored["maximum_counted_commands"],
    }


def extension_cases() -> dict[str, dict[str, Any]]:
    from curriculum.seed_data.scenario_bank import wave_scenario_bank

    missing = sorted(set(WAVE_FIXTURES) - set(wave_scenario_bank()))
    if missing:
        raise RuntimeError(f"Wave fixtures without authored scenarios: {missing}")
    return {case_id: extension_case(case_id) for case_id in WAVE_FIXTURES}

