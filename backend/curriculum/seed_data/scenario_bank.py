"""Canonical authored contract for the curriculum scenario banks.

``scenario_bank.json`` is the team's 265-scenario bank; ``apply_scenario_bank``
pairs it positionally with the archived module fixtures, so it stays exactly
that bank. ``scenario_bank_waves.json`` holds the scenarios written for the
ordered-wave curriculum and the Challenge Gates (compiled from
``source/wave_scenarios.md`` with the importer's ``--extension`` mode).
"""

from __future__ import annotations

import json
from functools import cache
from pathlib import Path
from typing import Any

CONTENT_PATH = Path(__file__).with_name("scenario_bank.json")
WAVE_CONTENT_PATH = Path(__file__).with_name("scenario_bank_waves.json")


@cache
def scenario_bank() -> dict[str, dict[str, Any]]:
    """Return the complete revised contract keyed by authored Variant ID."""
    return json.loads(CONTENT_PATH.read_text(encoding="utf-8"))


@cache
def wave_scenario_bank() -> dict[str, dict[str, Any]]:
    """Return the wave and gate scenarios keyed by authored Variant ID."""
    scenarios = json.loads(WAVE_CONTENT_PATH.read_text(encoding="utf-8"))
    shared = sorted(scenarios.keys() & scenario_bank().keys())
    if shared:
        raise RuntimeError(f"Wave scenario IDs collide with the scenario bank: {shared}")
    return scenarios


def scenario_for_case(case_id: str) -> dict[str, Any]:
    for bank in (scenario_bank(), wave_scenario_bank()):
        if case_id in bank:
            return bank[case_id]
    raise KeyError(f"No learner-facing content for curriculum case {case_id!r}.")
