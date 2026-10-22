"""Run `python -m testing.regenerate_kpi_routes` from backend/ after engine changes."""

import json
import os
from pathlib import Path

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.test_settings")
django.setup()

from curriculum.services.solution_replay import replay_solutions  # noqa: E402

path = Path(__file__).parent / "fixtures/kpi_routes.json"
data = json.loads(path.read_text(encoding="utf-8"))
data["targets"], data["replays"] = replay_solutions(data["cases"])
data["generated_by"] = "python -m testing.regenerate_kpi_routes (real browser Git engine)"
path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
