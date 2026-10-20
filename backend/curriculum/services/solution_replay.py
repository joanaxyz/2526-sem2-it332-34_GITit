"""Offline authored-route replay through the same engine used by learners."""

import json
import subprocess
import tempfile
from pathlib import Path

from django.core.management.base import CommandError

FRONTEND = Path(__file__).resolve().parents[3] / "frontend"


def replay_solutions(cases: dict) -> tuple[dict, dict]:
    with tempfile.TemporaryDirectory() as tmp:
        source, output = Path(tmp) / "cases.json", Path(tmp) / "targets.json"
        source.write_text(json.dumps(cases), encoding="utf-8")
        try:
            result = subprocess.run(
                ["node", str(FRONTEND / "scripts/generate-targets.mjs"), str(source), str(output)],
                cwd=FRONTEND,
                capture_output=True,
                text=True,
                timeout=180,
            )
        except (FileNotFoundError, subprocess.TimeoutExpired) as exc:
            raise CommandError(
                "Solution replay requires Node and installed frontend dependencies."
            ) from exc
        if result.returncode:
            raise CommandError(f"Solution replay failed:\n{result.stderr or result.stdout}")
        data = json.loads(output.read_text(encoding="utf-8"))
        return data["targets"], data["replays"]


def verify_backend_transitions(replays: dict) -> list[str]:
    """Replay each authored route through the backend's transition verifier.

    The live submit endpoint persists a command only when
    ``ClientTransitionVerifier`` reproduces the browser's next state. An
    answer key the verifier rejects is a scenario no learner can finish, so
    target generation refuses it. Returns one line per rejected step.
    """
    from common.exceptions import BadRequest
    from common.git.command_transition_verifier import ClientTransitionVerifier
    from simulator.services import RepositoryStateSimulator

    verifier = ClientTransitionVerifier()
    tools = RepositoryStateSimulator()
    rejected: list[str] = []
    for case_id, replay in sorted(replays.items()):
        steps = replay.get("steps") or []
        for index, step in enumerate(steps):
            command = str(step.get("normalized_command") or step.get("command") or "")
            if step.get("diagnostic") or not command.startswith("git "):
                continue
            after = (
                (steps[index + 1].get("before_edits") or steps[index + 1].get("ready"))
                if index + 1 < len(steps)
                else replay.get("final_before_edits") or replay.get("final")
            )
            try:
                verifier.verify(
                    command=command,
                    previous_state=tools.normalize_state(step.get("ready") or {}),
                    next_state=tools.normalize_state(after or {}),
                    command_family=str(step.get("command_family") or ""),
                    exit_code=int(step.get("exit_code") or 0),
                )
            except BadRequest as exc:
                rejected.append(f"{case_id} step {index + 1} ({command}): {exc}")
    return rejected

