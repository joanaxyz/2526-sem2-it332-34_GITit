"""Replay all published references and candidate alternatives, without a database."""

import copy
import json
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from common.exceptions import BadRequest
from common.git.client_command_execution import ClientCommandExecutionService
from common.runtime.star_targets import counted_command_total
from curriculum.seed_data.scenario_bank import extension_scenario_bank, scenario_bank
from curriculum.services.solution_audit import authored_content, candidate_routes, published_cases
from curriculum.services.solution_replay import replay_solutions
from curriculum.services.techniques import required_techniques, techniques_for_command
from evaluation.services.state_based import StateBasedEvaluator

REPORT = Path(__file__).resolve().parents[2] / "seed_data" / "solution_audit.json"


class Command(BaseCommand):
    help = "Audit every published variant through the browser, backend boundary, and objective evaluator."

    def add_arguments(self, parser):
        parser.add_argument("--check", action="store_true")

    def handle(self, *args, **options):
        published = published_cases()
        candidates, specs = {}, {}
        for case_id, (case, _) in published.items():
            for route in candidate_routes(case):
                key = case_id + "::" + route["name"]
                candidates[key] = route
                specs[key] = {
                    "initial_state": case["initial_state"],
                    "solution_commands": route["commands"],
                    "workspace_files": route["files"],
                    "max_counted_commands": 100000,
                    "allow_failure": True,
                }
        targets, replays = replay_solutions(specs)
        evaluator, executor = StateBasedEvaluator(), ClientCommandExecutionService()
        entries = {}
        failures = []
        for case_id, (case, placement) in published.items():
            authored = authored_content(case_id)
            entry = {
                **placement,
                "objective": authored["task"],
                "documented_alternatives": authored.get("accepted_alternatives", []),
                "required_techniques": required_techniques(case_id),
                "routes": [],
                "rejected_approaches": ["Unchanged starting repository"],
                "starting_state_rejected": not evaluator.evaluate(
                    case["initial_state"],
                    case["state_requirements"],
                    initial_state=case["initial_state"],
                ).target_matched,
            }
            for route in candidate_routes(case):
                key = case_id + "::" + route["name"]
                replay = replays[key]
                errors = [replay["failure"]] if replay.get("failure") else []
                evidence = set()
                if not errors:
                    for step in replay["steps"]:
                        try:
                            verified = executor.from_payload(
                                repository_state=step["ready"],
                                command=step["command"],
                                execution={**step["execution"], "cwd": step["cwd"]},
                                scoring_policy_version=2,
                            )
                            if verified.state_mutated and verified.result.processed:
                                evidence.update(
                                    techniques_for_command(
                                        verified.result.normalized_command,
                                        previous_state=verified.previous_state,
                                    )
                                )
                        except BadRequest as exc:
                            errors.append(str(exc))
                            break
                outcome = evaluator.evaluate(
                    targets[key],
                    case["state_requirements"],
                    initial_state=case["initial_state"],
                    executed_commands=route["commands"],
                )
                if not outcome.target_matched:
                    errors += [rule["reason"] for rule in outcome.failed_rules]
                missing = sorted(set(entry["required_techniques"]) - evidence)
                if missing:
                    errors.append("Required technique missing: " + ", ".join(missing))
                entry["routes"].append(
                    {
                        **route,
                        "counted_commands": counted_command_total(route["commands"]),
                        "accepted": not errors,
                        "gaps": errors,
                        "status": "accepted"
                        if not errors
                        else "unsupported_or_incomplete_route"
                        if replay.get("failure")
                        else "backend_verification_gap"
                        if any("execution." in error for error in errors)
                        else "objective_or_technique_mismatch",
                    }
                )
                if route["name"] == "authored" and errors:
                    failures.append(f"{case_id}: {errors}")
            accepted = [r for r in entry["routes"] if r["accepted"] and r["name"] != "authored"]
            entry["classification"] = (
                "multiple_workflows"
                if any(r["kind"] == "workflow" for r in accepted)
                else "syntax_alternatives"
                if accepted
                else "one_verified_route"
            )
            entry["review_status"] = (
                "references, concrete documented commands and generated equivalents replayed"
            )
            entry["rejected_state_tests"] = []
            reference = targets[case_id + "::authored"]
            requirements = case["state_requirements"]
            # Exercise incorrect states only where the authored contract explicitly forbids them.
            mutations = []
            if requirements.get("head_branch"):
                wrong = copy.deepcopy(reference)
                wrong["head"] = {"type": "branch", "name": "__wrong_branch__"}
                mutations.append(("wrong_branch", wrong))
            if requirements.get("staging_empty") or any(
                r.get("type") == "staging_matches_exact_paths"
                for r in requirements.get("rules", [])
            ):
                wrong = copy.deepcopy(reference)
                wrong.setdefault("staging", {})["__unrelated__.txt"] = {
                    "status": "untracked",
                    "content": "unrelated",
                }
                mutations.append(("unrelated_staging", wrong))
            for name, wrong in mutations:
                rejected = not evaluator.evaluate(
                    wrong,
                    requirements,
                    initial_state=case["initial_state"],
                    executed_commands=case["solution_commands"],
                ).target_matched
                entry["rejected_state_tests"].append({"name": name, "rejected": rejected})
                if not rejected:
                    failures.append(f"{case_id}: invalid {name} state passes")
            accepted_routes = [r for r in entry["routes"] if r["accepted"]]
            from common.runtime.scoring_policy import thresholds

            efficient, generous, maximum = thresholds(
                max(
                    authored["minimum_counted_commands"],
                    max((r["counted_commands"] for r in accepted_routes), default=0),
                ),
                authored["maximum_counted_commands"],
            )
            entry["thresholds"] = {"efficient": efficient, "generous": generous, "maximum": maximum}
            entries[case_id] = entry
            if not entry["starting_state_rejected"]:
                failures.append(f"{case_id}: initial state passes")
        report = {
            "schema_version": 1,
            "published": entries,
            "unpublished": sorted(
                (scenario_bank().keys() | extension_scenario_bank().keys()) - published.keys()
            ),
        }
        rendered = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
        if options["check"]:
            if not REPORT.exists() or REPORT.read_text(encoding="utf-8") != rendered:
                raise CommandError("Solution audit is stale; run audit_solutions.")
        else:
            REPORT.write_text(rendered, encoding="utf-8")
        self.stdout.write(
            f"Audited {len(entries)} published variants and {len(candidates)} routes; {len(failures)} reference failures."
        )
        from collections import Counter

        classifications = Counter(e["classification"] for e in entries.values())
        rows = [
            "# Git solution audit",
            "",
            "Generated by python manage.py audit_solutions. Re-run with --check to verify drift.",
            "",
            f"Published variants: {len(entries)}. Executable routes: {len(candidates)}. Reference failures: {len(failures)}.",
            f"Classifications: {dict(sorted(classifications.items()))}. Unpublished variants: {len(report['unpublished'])}.",
            "",
            "Every accepted route passed the browser simulator, backend execution boundary, outcome rules and explicit technique requirements.",
            "The JSON companion records commands, file edits, counted costs and rejection details for every candidate.",
            "Rejected candidates include incomplete documentation snippets, task violations and unsupported forms; they are not all valid alternatives.",
            "This audit establishes verified routes, not an exhaustive list of all possible Git solutions.",
            "",
            "| Variant | Surface | Classification | Accepted / candidates | Required technique | 3 / 2 / maximum |",
            "|---|---|---|---|---|---|",
        ]
        for key, entry in entries.items():
            targets = entry["thresholds"]
            accepted_count = sum(route["accepted"] for route in entry["routes"])
            rows.append(
                f"| {key} | {entry['surface']} | {entry['classification']} | {accepted_count} / {len(entry['routes'])} | "
                + (", ".join(entry["required_techniques"]) or "Outcome only")
                + f" | {targets['efficient']} / {targets['generous']} / {targets['maximum']} |"
            )
        rows += ["", "## Unpublished variants", "", ", ".join(report["unpublished"]), ""]
        summary = "\n".join(rows)
        summary_path = Path(__file__).resolve().parents[4] / "docs" / "git-solution-audit.md"
        if options["check"]:
            if not summary_path.exists() or summary_path.read_text(encoding="utf-8") != summary:
                raise CommandError("Human-readable audit is stale; run audit_solutions.")
        else:
            summary_path.parent.mkdir(parents=True, exist_ok=True)
            summary_path.write_text(summary, encoding="utf-8")
        if failures:
            raise CommandError("\n".join(failures[:12]))
