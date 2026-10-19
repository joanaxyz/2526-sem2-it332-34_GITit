"""Canonical authored contract for the current 265-scenario curriculum bank."""

from __future__ import annotations

import json
from functools import cache
from pathlib import Path
from typing import Any

CONTENT_PATH = Path(__file__).with_name("scenario_bank.json")


@cache
def scenario_bank() -> dict[str, dict[str, Any]]:
    """Return the complete revised contract keyed by authored Variant ID."""
    return json.loads(CONTENT_PATH.read_text(encoding="utf-8"))


def scenario_for_case(case_id: str) -> dict[str, Any]:
    try:
        return scenario_bank()[case_id]
    except KeyError as exc:
        raise KeyError(f"No learner-facing content for curriculum case {case_id!r}.") from exc
