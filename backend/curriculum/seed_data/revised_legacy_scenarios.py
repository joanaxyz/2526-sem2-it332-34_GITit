"""Canonical authored contract for the revised 265-scenario legacy bank."""

from __future__ import annotations

import json
from functools import cache
from pathlib import Path
from typing import Any


CONTENT_PATH = Path(__file__).with_name("revised_legacy_scenarios.json")


@cache
def revised_legacy_scenarios() -> dict[str, dict[str, Any]]:
    """Return the complete revised contract keyed by authored Variant ID."""
    return json.loads(CONTENT_PATH.read_text(encoding="utf-8"))


def revised_legacy_scenario(case_id: str) -> dict[str, Any]:
    try:
        return revised_legacy_scenarios()[case_id]
    except KeyError as exc:
        raise KeyError(f"No revised learner-facing content for legacy case {case_id!r}.") from exc
