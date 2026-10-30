"""Executable coverage of published scenarios and candidate equivalent routes."""

from __future__ import annotations

import copy
import re
import shlex
from functools import cache

from curriculum.seed_data.scenario_bank import extension_scenario_bank, scenario_bank
from curriculum.seed_data.source.challenge_gates import CHALLENGE_GATES
from curriculum.seed_data.source.scenario_plan import MODULE_SCENARIO_PLAN


def published_cases():
    from curriculum.management.commands.seed_curriculum import MODULE_LEVELS
    from curriculum.seed_data.source.scenario_fixtures import extension_case

    pool = {
        c["case_id"]: c
        for level in MODULE_LEVELS
        for tier in level["tiers"].values()
        for c in tier["cases"]
    }
    placements = {}
    for level, tiers in MODULE_SCENARIO_PLAN.items():
        for difficulty, scenarios in tiers.items():
            for scenario in scenarios:
                for case_id in scenario.variants:
                    placements[case_id] = {
                        "surface": "story",
                        "level": level,
                        "difficulty": difficulty,
                        "scenario": scenario.slug,
                    }
    for gate in CHALLENGE_GATES.values():
        for difficulty, ids in gate["trials"].items():
            for case_id in ids:
                placements[case_id] = {
                    "surface": "challenge",
                    "level": gate["slug"],
                    "difficulty": difficulty,
                }
    return {
        key: (pool.get(key) or extension_case(key), placement)
        for key, placement in placements.items()
    }


def candidate_routes(case):
    """Conservative, single-step substitutions; acceptance is proven by replay."""
    commands = case["solution_commands"]
    files = case.get("solution_workspace_files", [])
    yield {"name": "authored", "kind": "reference", "commands": commands, "files": files}
    seen = {tuple(commands)}
    for index, command in enumerate(commands):
        try:
            parts = shlex.split(command)
        except ValueError:
            continue
        replacements = []
        if parts[:3] == ["git", "switch", "-c"]:
            replacements += [
                (["git", "checkout", "-b", *parts[3:]], "syntax"),
                (["git", "branch", *parts[3:]], "split_branch"),
            ]
        elif parts[:3] == ["git", "checkout", "-b"]:
            replacements += [(["git", "switch", "-c", *parts[3:]], "syntax")]
        elif len(parts) == 3 and parts[:2] == ["git", "switch"] and not parts[2].startswith("-"):
            replacements += [(["git", "checkout", parts[2]], "syntax")]
        elif (
            parts[:2] == ["git", "add"]
            and len(parts) == 3
            and not parts[2].startswith("-")
            and parts[2] != "."
        ):
            replacements += [(["git", "add", "--", parts[2]], "syntax")]
        elif parts[:3] == ["git", "restore", "--staged"]:
            replacements += [(["git", "reset", "HEAD", "--", *parts[3:]], "workflow")]
        elif parts[:2] == ["git", "init"]:
            for flag, equivalent in (("-b", "--initial-branch"), ("--initial-branch", "-b")):
                if flag in parts:
                    alternate = list(parts)
                    alternate[parts.index(flag)] = equivalent
                    replacements.append((alternate, "syntax"))
        # Supported long/short option forms use the same operation.
        option_pairs = {
            "add": [("-A", "--all"), ("-u", "--update"), ("-p", "--patch")],
            "branch": [("-d", "--delete"), ("-m", "--move")],
            "clone": [("-b", "--branch")],
            "commit": [("-m", "--message"), ("-a", "--all")],
            "switch": [("-c", "--create")],
            "stash": [("-u", "--include-untracked"), ("-m", "--message")],
            "push": [("-u", "--set-upstream"), ("-d", "--delete")],
        }
        if len(parts) >= 2:
            for short, long in option_pairs.get(parts[1], []):
                for source, destination in ((short, long), (long, short)):
                    if source in parts:
                        tokens = list(parts)
                        tokens[tokens.index(source)] = destination
                        replacements.append((tokens, "syntax"))
        if parts == ["git", "init"]:
            replacements.append((["git", "init", "."], "syntax"))
        if (
            len(parts) >= 3
            and parts[:2] == ["git", "add"]
            and not any(p.startswith("-") for p in parts[2:])
        ):
            replacements.append((["git", "add", "."], "workflow"))
        # Concrete commands from authored alternatives; placeholders stay prose.
        documented = authored_content(case["case_id"]).get("accepted_alternatives", [])
        for text in documented:
            for snippet in re.findall(
                r"`([^`]+)`", re.split(r"(?i)not accepted|do not accept|not equivalent", text)[0]
            ):
                if not snippet.startswith("git ") or any(
                    token in snippet for token in ("<", ">", "...", "&&", ";")
                ):
                    continue
                try:
                    tokens = shlex.split(snippet)
                except ValueError:
                    continue
                if len(commands) == 1 or (
                    len(parts) > 1 and len(tokens) > 1 and parts[1] == tokens[1]
                ):
                    replacements.append((tokens, "documented"))
        for replacement_index, (tokens, kind) in enumerate(replacements):
            replacement = [shlex.join(tokens)]
            if kind == "split_branch":
                replacement.append(shlex.join(["git", "switch", parts[3]]))
            new_commands = commands[:index] + replacement + commands[index + 1 :]
            if tuple(new_commands) in seen:
                continue
            seen.add(tuple(new_commands))
            shifted = copy.deepcopy(files)
            for edit in shifted:
                if edit.get("after_command_index", 0) > index:
                    edit["after_command_index"] += len(replacement) - 1
            yield {
                "name": f"{kind}-{index + 1}-{replacement_index + 1}",
                "kind": "workflow"
                if kind == "split_branch"
                or (
                    kind == "documented"
                    and len(parts) > 1
                    and len(tokens) > 1
                    and tokens[1] != parts[1]
                )
                else "syntax"
                if kind == "documented"
                else kind,
                "commands": new_commands,
                "files": shifted,
            }


def authored_content(case_id):
    return (scenario_bank() | extension_scenario_bank())[case_id]


def verified_route_cost(case_id):
    """Only checked-in, successfully replayed audit routes may raise the target."""
    from pathlib import Path

    path = Path(__file__).resolve().parents[1] / "seed_data" / "solution_audit.json"
    if not path.exists():
        return 0
    report = _report(path)
    entry = report.get("published", {}).get(case_id, {})
    return max(
        (route["counted_commands"] for route in entry.get("routes", []) if route["accepted"]),
        default=0,
    )


@cache
def _report(path):
    import json

    return json.loads(path.read_text(encoding="utf-8"))
