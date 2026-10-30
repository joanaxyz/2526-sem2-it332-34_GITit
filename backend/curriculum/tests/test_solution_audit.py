import json
import shutil
from pathlib import Path

import pytest
from django.core.management import call_command

from curriculum.services.solution_audit import published_cases
from curriculum.services.techniques import required_techniques

REPORT = Path(__file__).resolve().parents[1] / "seed_data" / "solution_audit.json"
FRONTEND = Path(__file__).resolve().parents[3] / "frontend"

needs_simulator = pytest.mark.skipif(
    shutil.which("node") is None or not (FRONTEND / "node_modules").exists(),
    reason="replay needs Node and frontend/node_modules (CI: generated-targets job)",
)


def test_audit_covers_every_published_variant_and_valid_reference():
    report = json.loads(REPORT.read_text(encoding="utf-8"))
    assert report["published"].keys() == published_cases().keys()
    assert not set(report["published"]) & set(report["unpublished"])
    for case_id, entry in report["published"].items():
        assert entry["starting_state_rejected"], case_id
        assert entry["routes"][0]["name"] == "authored"
        assert entry["routes"][0]["accepted"], case_id
        assert all(test["rejected"] for test in entry["rejected_state_tests"]), case_id
        assert entry["required_techniques"] == required_techniques(case_id)
        targets = entry["thresholds"]
        assert targets["efficient"] < targets["generous"] < targets["maximum"]


@needs_simulator
def test_audit_replays_browser_backend_and_objectives_without_drift():
    call_command("audit_solutions", check=True)
