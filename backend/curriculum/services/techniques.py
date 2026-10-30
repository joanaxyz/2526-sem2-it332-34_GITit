"""Explicit teaching requirements, matched to verified parsed operations."""

import json
import shlex
from functools import cache
from pathlib import Path


def techniques_for_command(command, *, previous_state=None):
    try:
        parts = shlex.split(command)
    except ValueError:
        return set()
    if len(parts) < 2 or parts[0] != "git":
        return set()
    family = parts[1]
    if family == "init":
        # Choosing an initial branch must happen when the repository is created.
        # Verified prior state prevents a later reinit from earning this evidence.
        if previous_state is None or previous_state.get("repository_initialized", True):
            return set()
        branch = None
        tokens = iter(parts[2:])
        for token in tokens:
            if token == "--":
                break
            if token in {"-b", "--initial-branch"}:
                branch = next(tokens, None)
            elif token.startswith("--initial-branch="):
                branch = token.split("=", 1)[1]
        return {f"init:initial-branch:{branch}"} if branch and not branch.startswith("-") else set()
    # Option values are operands, even when their text looks like a flag.
    flags = set()
    index = 2
    while index < len(parts):
        token = parts[index]
        if token == "--":
            break
        if token in {"-m", "--message", "-am"}:
            index += 2
            continue
        if token.startswith("--message=") or (token.startswith("-am") and len(token) > 3):
            index += 1
            continue
        if token.startswith("-"):
            flags.add(token)
        index += 1
    if family == "commit":
        return {"amend"} if "--amend" in flags else set()
    if family not in {"merge", "rebase", "cherry-pick", "revert"}:
        return set()
    for action in ("abort", "continue", "skip"):
        if "--" + action in flags:
            return {family + ":" + action}
    if family == "merge" and "--squash" in flags:
        return {"merge:squash"}
    return {family}


@cache
def _requirements():
    path = (
        Path(__file__).resolve().parents[1] / "seed_data" / "source" / "technique_requirements.json"
    )
    return json.loads(path.read_text(encoding="utf-8"))


def required_techniques(case_id):
    """Explicit per-variant policy; no runtime guesses from learner-facing prose."""
    return list(_requirements().get(case_id, []))


def record_verified_techniques(run, execution):
    """Called only after the client transition has passed backend verification."""
    if (
        run.scoring_policy_version < 2
        or not execution.result.processed
        or not execution.state_mutated
    ):
        return
    found = techniques_for_command(
        execution.result.normalized_command, previous_state=execution.previous_state
    )
    if found:
        run.verified_techniques = sorted(set(run.verified_techniques) | found)


def technique_label(technique):
    if technique.startswith("init:initial-branch:"):
        branch = technique.removeprefix("init:initial-branch:")
        return f"git init -b {shlex.quote(branch)}"
    if technique == "amend":
        return "git commit --amend"
    family, separator, action = technique.partition(":")
    return f"git {family} --{action}" if separator else f"git {family}"
