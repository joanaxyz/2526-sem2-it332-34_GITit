"""Learner-facing content for the revised 265-scenario legacy bank."""

from __future__ import annotations

import json
from functools import cache
from pathlib import Path
from typing import Any


CONTENT_PATH = Path(__file__).with_name("revised_legacy_scenarios.json")


@cache
def revised_legacy_scenarios() -> dict[str, dict[str, Any]]:
    """Return revised content keyed by the stable legacy case ID.

    The source bank replaces a few exercises with new source IDs. Until their
    simulator specs and generated targets are replaced, those entries stay
    aligned to the existing stable seed slots. ``source_case_id`` records the
    authored ID so that cutover remains explicit instead of being lost in a
    positional import.
    """
    return json.loads(CONTENT_PATH.read_text(encoding="utf-8"))


def revised_legacy_scenario(case_id: str) -> dict[str, Any]:
    try:
        return revised_legacy_scenarios()[case_id]
    except KeyError as exc:
        raise KeyError(f"No revised learner-facing content for legacy case {case_id!r}.") from exc
