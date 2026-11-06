"""Decision-level proof: equivalent solutions pass, meaningful old recipes fail."""

import copy
import json
import os
from functools import cache
from pathlib import Path
from types import SimpleNamespace

import pytest

from common.git.client_command_execution import ClientCommandExecutionService
from curriculum.management.commands.seed_curriculum import Command
from curriculum.seed_data.source.scenario_fixtures import extension_case
from curriculum.seed_data.source.transfer_checkpoints import TRANSFER_CHECKPOINTS
from curriculum.services.solution_replay import replay_solutions
from curriculum.services.techniques import record_verified_techniques
from evaluation.completion import CompletionEvaluationContext, PracticeCompletionEvaluator

MANUAL = "manual-transfer-stale-index-v2"
TOOL = "mergetool-transfer-clean-guide-v2"
PICK = "cherry-transfer-mixed-commit-v2"
RECOVER = "reflog-transfer-two-destinations-v2"
REVERT = "revert-transfer-returned-regression-v2"
REBASE = "rebase-transfer-invoices-v2"


def scenarios():
    rows = {}

    def add(name, case_id, passed, commands=None, edits=None):
        case = extension_case(case_id)
        rows[name] = {
            "case_id": case_id,
            "expected": passed,
            "case": case,
            "commands": commands if commands is not None else case["solution_commands"],
            "edits": edits
            if edits is not None
            else copy.deepcopy(case["solution_workspace_files"]),
        }

    for case in TRANSFER_CHECKPOINTS.values():
        add(case["case_id"] + ":reference", case["case_id"], True)
    add("manual:equivalent", MANUAL, True, ["git add -- src/checkout.py", "git commit --no-edit"])
    add("manual:auto-stage-equivalent", MANUAL, True, ["git commit -a --no-edit"])
    add("manual:stale-index", MANUAL, False, ["git commit --no-edit"])
    add(
        "manual:discard-correction",
        MANUAL,
        False,
        ["git restore src/checkout.py", "git commit --no-edit"],
    )
    tool_edits = extension_case(TOOL)["solution_workspace_files"]
    add(
        "tool:equivalent",
        TOOL,
        True,
        ["git merge feature/queued-mail", "git mergetool", "git add .", "git commit --no-edit"],
    )
    add(
        "tool:conflicts-only",
        TOOL,
        False,
        ["git merge feature/queued-mail", "git mergetool", "git commit --no-edit"],
        [tool_edits[0]],
    )
    add(
        "tool:unstaged-guide",
        TOOL,
        False,
        ["git merge feature/queued-mail", "git mergetool", "git commit --no-edit"],
    )
    manual_edits = [{**edit, "after_command_index": 1} for edit in tool_edits]
    add(
        "tool:manual-only",
        TOOL,
        False,
        [
            "git merge feature/queued-mail",
            "git add config/retry.ini docs/usage.txt",
            "git commit --no-edit",
        ],
        manual_edits,
    )
    add(
        "pick:equivalent",
        PICK,
        True,
        ["git cherry-pick -n c2", "git add .", 'git commit -m "Backport CSV delimiter fix"'],
    )
    add(
        "pick:whole-bundle",
        PICK,
        False,
        ["git cherry-pick --no-commit c2", 'git commit -m "Backport CSV delimiter fix"'],
        [],
    )
    add(
        "pick:unstaged-policy",
        PICK,
        False,
        ["git cherry-pick --no-commit c2", 'git commit -m "Backport CSV delimiter fix"'],
    )
    add(
        "pick:manual-copy-without-pick",
        PICK,
        False,
        ["git add src/export.py", 'git commit -m "Backport CSV delimiter fix"'],
        [
            {
                "mode": "write",
                "path": "src/export.py",
                "content": "delimiter = ';'",
                "after_command_index": 0,
            }
        ],
    )
    add(
        "recovery:equivalent",
        RECOVER,
        True,
        ["git branch recovery/report-redesign c3", "git merge c2"],
    )
    add(
        "recovery:single-destination", RECOVER, False, ["git switch -c recovery/report-redesign c2"]
    )
    add(
        "recovery:redesign-on-main",
        RECOVER,
        False,
        ["git branch recovery/report-redesign c3", "git merge c3"],
    )
    add("revert:equivalent", REVERT, True, ["git show c5", "git revert c5", "git push origin main"])
    add("revert:old-already-undone-fault", REVERT, False, ["git revert c2", "git push"])
    add("revert:wrong-guide", REVERT, False, ["git revert c6", "git push"])
    add(
        "rebase:equivalent",
        REBASE,
        True,
        [
            "git rebase --abort",
            "git reset --hard c6",
            "git rebase --onto main spike/heatmap feature/invoices",
            "git push --force-with-lease",
        ],
    )
    add(
        "rebase:lost-commit",
        REBASE,
        False,
        [
            "git rebase --abort",
            "git rebase --onto main spike/heatmap feature/invoices",
            "git push --force-with-lease origin feature/invoices",
        ],
    )
    add(
        "rebase:wrong-boundary",
        REBASE,
        False,
        [
            "git rebase --abort",
            "git reset --hard c6",
            "git rebase main",
            "git push --force-with-lease origin feature/invoices",
        ],
    )
    for flag in ("--force", "--force --force-with-lease", "-f --force-with-lease"):
        add(
            "rebase:unsafe:" + flag,
            REBASE,
            False,
            [
                "git rebase --abort",
                "git reset --hard c6",
                "git rebase --onto main spike/heatmap feature/invoices",
                f"git push {flag} origin feature/invoices",
            ],
        )
    add("rebase:stale-lease", REBASE, False)
    stale = rows["rebase:stale-lease"]
    stale["case"] = copy.deepcopy(stale["case"])
    initial = stale["case"]["initial_state"]
    for state in (initial, initial["rebase_state"]["abort_state"]):
        if not any(c["id"] == "c9" for c in state["commits"]):
            tree = next(c["tree"] for c in state["commits"] if c["id"] == "c6")
            state["commits"].append(
                {
                    "id": "c9",
                    "message": "Teammate update after last fetch",
                    "parents": ["c6"],
                    "tree": {**tree, "src/teammate.py": "keep-this-work"},
                }
            )
        state["remote_updates"] = {"origin/feature/invoices": "c9"}
    return rows


@cache
def replayed_routes():
    rows = scenarios()
    targets, replays = replay_solutions(
        {
            name: {
                "initial_state": row["case"]["initial_state"],
                "solution_commands": row["commands"],
                "workspace_files": row["edits"],
                "max_counted_commands": row["case"]["max_counted_commands"],
                "allow_failure": True,
            }
            for name, row in rows.items()
        }
    )
    return rows, targets, replays


@pytest.fixture(scope="module")
def outcomes():
    rows, targets, replays = replayed_routes()
    executor = ClientCommandExecutionService()
    evaluator = PracticeCompletionEvaluator()
    evidence = {}
    for name, row in rows.items():
        replay = replays[name]
        if replay.get("failure"):
            assert name == "rebase:stale-lease" and "rejected" in replay["failure"], (
                name,
                replay["failure"],
            )
        run = SimpleNamespace(scoring_policy_version=2, verified_techniques=[])
        for step in replay["steps"]:
            execution = executor.from_payload(
                repository_state=step["ready"],
                command=step["command"],
                execution={**step["execution"], "cwd": step["cwd"]},
                scoring_policy_version=2,
            )
            record_verified_techniques(run, execution)
        variant = SimpleNamespace(**Command._variant_defaults(row["case"]))
        result = evaluator.evaluate(
            CompletionEvaluationContext(
                variant=variant,
                next_state=targets[name],
                executed_commands=row["commands"],
                required_techniques=variant.parameter_context["required_techniques"],
                verified_techniques=run.verified_techniques,
            )
        )
        initial = evaluator.evaluate(
            CompletionEvaluationContext(
                variant=variant,
                next_state=variant.initial_state,
                required_techniques=variant.parameter_context["required_techniques"],
            )
        )
        assert not initial.target_matched, name
        evidence[name] = {
            "case_id": row["case_id"],
            "commands": row["commands"],
            "expected": row["expected"],
            "passed": result.target_matched,
            "verified_techniques": run.verified_techniques,
            "failures": list(result.failed_rules),
            "task": variant.scenario_context["task"],
            "replay_failure": replay.get("failure"),
        }
    if destination := os.environ.get("RTA_EVIDENCE_PATH"):
        Path(destination).write_text(json.dumps(evidence, indent=2), encoding="utf-8")
    return evidence


@pytest.mark.parametrize("name", sorted(scenarios()))
def test_checkpoint_decision_outcomes(outcomes, name):
    row = outcomes[name]
    assert row["passed"] == row["expected"], row


def test_wrong_routes_fail_for_the_intended_decision(outcomes):
    for name, rule in {
        "manual:stale-index": "branch_tip_commit",
        "tool:conflicts-only": "branch_tip_commit",
        "tool:manual-only": "required_technique",
        "pick:whole-bundle": "branch_tip_commit",
        "recovery:single-destination": "branch_points_to",
        "revert:old-already-undone-fault": "branch_tip_commit",
        "rebase:lost-commit": "commit_tree_contains",
        "rebase:wrong-boundary": "commit_tree_excludes",
        "rebase:unsafe:--force --force-with-lease": "required_technique",
    }.items():
        assert rule in {r["type"] for r in outcomes[name]["failures"]}, (name, outcomes[name])


def test_a_server_move_rejects_the_lease_and_grants_no_guard_evidence(outcomes):
    row = outcomes["rebase:stale-lease"]
    assert not row["passed"]
    assert "push:force-with-lease" not in row["verified_techniques"]
    assert row["replay_failure"] and "rejected" in row["replay_failure"]


@pytest.mark.django_db
def test_learner_api_records_current_checkpoint_references(django_user_model):
    from django.core.management import call_command
    from rest_framework.test import APIClient

    from adventures.models import AdventureLevelTier, AdventureLevelTierProgress
    from adventures.services import AdventureLevelTierRunService
    from players.services import get_or_create_player
    from progress.models import AdventureLevelTierCompletion, CoinTransaction, KpiCheckpoint

    call_command("seed_curriculum", verbosity=0)
    _, _, replays = replayed_routes()
    evidence = {}
    for index, (level, spec) in enumerate(TRANSFER_CHECKPOINTS.items()):
        user = django_user_model.objects.create_user(username=f"checkpoint-api-{index}")
        learner = get_or_create_player(user)
        client = APIClient()
        client.force_authenticate(user=user)
        tier = AdventureLevelTier.objects.get(adventure_level__slug=level, difficulty="hard")
        for slug in (level, *spec.get("prerequisites", ())):
            completed = AdventureLevelTier.objects.get(
                adventure_level__slug=slug, difficulty="hard"
            )
            AdventureLevelTierCompletion.objects.create(player=learner, tier=completed)
        AdventureLevelTierProgress.objects.create(player=learner, tier=tier, exposure_complete=True)
        service = AdventureLevelTierRunService()
        run = service.start_run(
            player=learner, tier=tier, source_entry_point="level_page", transfer=True
        )
        assert run.selected_variant.slug == spec["case_id"]
        before = AdventureLevelTierCompletion.objects.filter(player=learner).count()
        response = client.get(f"/api/adventure-tier-runs/{run.id}/")
        assert response.status_code == 200, response.content
        payload = response.json()
        assert payload["transfer"] and payload["expected_state"] is None
        assert payload["command_guides"] == [] and payload["tutor"] is None
        steps = []
        for command_index, step in enumerate(replays[spec["case_id"] + ":reference"]["steps"]):
            for edit in run.selected_variant.solution_workspace_files:
                if edit["after_command_index"] == command_index:
                    response = client.patch(
                        f"/api/adventure-tier-runs/{run.id}/files/",
                        {"path": edit["path"], "content": edit["content"]},
                        format="json",
                    )
                    assert response.status_code == 200, (spec["case_id"], response.content)
            run.refresh_from_db()
            execution = {
                **step["execution"],
                "cwd": step["cwd"],
                "client_run_revision": run.total_attempts,
            }
            response = client.post(
                f"/api/adventure-tier-runs/{run.id}/submit-command/",
                {"command": step["command"], "execution": execution},
                format="json",
            )
            assert response.status_code == 200, (spec["case_id"], step["command"], response.content)
            result = response.json()
            steps.append(
                {
                    "command": step["command"],
                    "status": result["run"]["status"],
                    "result": result["step"]["result_category"],
                }
            )
        run.refresh_from_db()
        point = KpiCheckpoint.objects.get(player=learner, tier=tier, kind="transfer")
        assert run.status == "completed" and point.passed is True and point.run_id == run.id
        assert AdventureLevelTierCompletion.objects.filter(player=learner).count() == before
        assert (
            CoinTransaction.objects.get(player=learner, award_key=f"transfer:{tier.id}").amount
            == 150
        )
        evidence[spec["case_id"]] = {
            "task": payload["scenario_context"],
            "expected_state": payload["expected_state"],
            "command_guides": payload["command_guides"],
            "steps": steps,
            "status": run.status,
            "first_result": point.passed,
            "reference_hash": point.ref_hash,
            "reward": 150,
            "practice_mastery_count_unchanged": True,
        }
    if destination := os.environ.get("RTA_API_EVIDENCE_PATH"):
        Path(destination).write_text(json.dumps(evidence, indent=2), encoding="utf-8")
