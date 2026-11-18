"""Verify the evidence export and frontend use the same objective definitions."""

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    OBJECTIVES = json.loads(
        (ROOT / "backend/adminconsole/services/evidence_objectives.json").read_text(
            encoding="utf-8-sig"
        )
    )
    source = (ROOT / "frontend/src/features/performance/utils/learningObjectives.ts").read_text(
        encoding="utf-8"
    )
    matches = re.findall(
        r"id: '(SO \d+\.\d+)',\s+title: '([^']+)',\s+metrics: \[([^\]]+)\]", source
    )
    assert len(matches) == len(OBJECTIVES) == 29
    for (code, title, metrics), objective in zip(matches, OBJECTIVES, strict=True):
        assert (code, title) == (objective["id"], objective["title"])
        assert [
            (k, int(t or 70), k != "arc")
            for k, t in re.findall(r"(car|hlcr|arc|rta)\((\d*)\)", metrics)
        ] == [(c["key"], c["target"], c["up"]) for c in objective["metrics"]]


if __name__ == "__main__":
    main()
    print("Evidence objective definitions match the frontend.")
