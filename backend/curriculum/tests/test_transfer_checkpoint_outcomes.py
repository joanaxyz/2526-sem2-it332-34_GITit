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
INDEX = "restore-transfer-contaminated-index-v2"
NAMING = "naming-transfer-preserve-before-cleanup"


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
    add(
        "index:equivalent",
        INDEX,
        True,
        [
            "git reset HEAD -- src/api.py",
            "git add --patch src/api.py",
            "git restore tmp/output.txt",
            'git commit -m "Fix request totals"',
        ],
    )
    add(
        "index:already-staged-patch",
        INDEX,
        False,
        [
            "git add -p src/api.py",
            "git restore tmp/output.txt",
            'git commit -m "Fix request totals"',
        ],
    )
    add(
        "index:whole-source",
        INDEX,
        False,
        [
            "git restore --staged src/api.py",
            "git add src/api.py",
            "git restore tmp/output.txt",
            'git commit -m "Fix request totals"',
        ],
    )
    add(
        "index:lost-experiment",
        INDEX,
        False,
        [
            "git restore --staged src/api.py",
            "git add -p src/api.py",
            "git restore src/api.py",
            "git restore tmp/output.txt",
            'git commit -m "Fix request totals"',
        ],
    )
    add("naming:equivalent", NAMING, True, ["git branch -m fix/parser", "git branch -d fix/merged"])
    add(
        "index:unrelated-file-committed",
        INDEX,
        False,
        [
            "git restore --staged src/api.py",
            "git add -p src/api.py",
            "git restore tmp/output.txt",
            "git add notes/unapproved.txt",
            'git commit -m "Fix request totals"',
        ],
        [
            {
                "mode": "write",
                "path": "notes/unapproved.txt",
                "content": "unrelated draft",
                "after_command_index": 0,
            }
        ],
    )
    add(
        "naming:restart-from-main",
        NAMING,
        False,
        [
            "git switch main",
            "git branch -D scratch",
            "git switch -c fix/parser",
            "git branch -d fix/merged",
        ],
    )
    add(
        "naming:delete-active",
        NAMING,
        False,
        [
            "git switch -c fix/parser",
            "git branch -d scratch",
            "git branch -d fix/merged",
            "git branch -D feature/active",
        ],
    )
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
        "index:unrelated-file-committed": "branch_tip_commit",
        "index:already-staged-patch": "branch_tip_commit",
        "index:lost-experiment": "partial_hunks_left_in_working_tree",
        "naming:restart-from-main": "branch_points_to",
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


@pytest.mark.django_db
def test_unrelated_file_cannot_complete_the_tightened_checkpoint_via_learner_api(django_user_model):
    from django.core.management import call_command
    from rest_framework.test import APIClient

    from adventures.models import AdventureLevelTier, AdventureLevelTierProgress
    from adventures.services import AdventureLevelTierRunService
    from players.services import get_or_create_player
    from progress.models import AdventureLevelTierCompletion, CoinTransaction, KpiCheckpoint

    call_command("seed_curriculum", verbosity=0)
    user = django_user_model.objects.create_user(username="unrelated-file-probe")
    learner = get_or_create_player(user)
    tier = AdventureLevelTier.objects.get(
        adventure_level__slug="unstaging-and-discarding-changes", difficulty="hard"
    )
    AdventureLevelTierCompletion.objects.create(player=learner, tier=tier)
    AdventureLevelTierProgress.objects.create(player=learner, tier=tier, exposure_complete=True)
    run = AdventureLevelTierRunService().start_run(
        player=learner, tier=tier, source_entry_point="level_page", transfer=True
    )
    assert run.selected_variant.slug == INDEX
    client = APIClient()
    client.force_authenticate(user=user)
    response = client.post(
        f"/api/adventure-tier-runs/{run.id}/files/",
        {"path": "notes/unapproved.txt", "content": "unrelated draft"},
        format="json",
    )
    assert response.status_code == 200, response.content
    _, _, replays = replayed_routes()
    steps = []
    for step in replays["index:unrelated-file-committed"]["steps"]:
        run.refresh_from_db()
        response = client.post(
            f"/api/adventure-tier-runs/{run.id}/submit-command/",
            {
                "command": step["command"],
                "execution": {
                    **step["execution"],
                    "cwd": step["cwd"],
                    "client_run_revision": run.total_attempts,
                },
            },
            format="json",
        )
        assert response.status_code == 200, response.content
        steps.append(
            {
                "command": step["command"],
                "status": response.json()["run"]["status"],
                "result": response.json()["step"]["result_category"],
            }
        )
    run.refresh_from_db()
    point = KpiCheckpoint.objects.get(player=learner, tier=tier, kind="transfer")
    rewarded = CoinTransaction.objects.filter(
        player=learner, award_key=f"transfer:{tier.id}"
    ).exists()
    assert run.status == "started" and point.ended_at is None and point.passed is None
    assert not rewarded
    if destination := os.environ.get("TIGHTENING_API_NEGATIVE_EVIDENCE_PATH"):
        Path(destination).write_text(
            json.dumps(
                {
                    "variant": run.selected_variant.slug,
                    "reference_hash": point.ref_hash,
                    "steps": steps,
                    "status": run.status,
                    "first_result": point.passed,
                    "reward_awarded": rewarded,
                    "unrelated_file_committed": True,
                    "completion_rejected": True,
                },
                indent=2,
            ),
            encoding="utf-8",
        )


@cache
def early_mastery_replays():
    from curriculum.seed_data.source.scenario_plan import MODULE_SCENARIO_PLAN
    from curriculum.tests.test_scenario_plan_invariants import _case

    ids = {INDEX, NAMING}
    for level in ("unstaging-and-discarding-changes", "branch-naming-and-housekeeping"):
        ids.update(
            case_id for spec in MODULE_SCENARIO_PLAN[level]["hard"] for case_id in spec.variants
        )
    _, replays = replay_solutions(
        {
            case_id: {
                "initial_state": _case(case_id)["initial_state"],
                "solution_commands": _case(case_id)["solution_commands"],
                "workspace_files": _case(case_id).get("solution_workspace_files", []),
                "max_counted_commands": _case(case_id).get("max_counted_commands", 20),
            }
            for case_id in ids
        }
    )
    return replays


@pytest.mark.django_db
@pytest.mark.parametrize(
    "level,first_pass",
    [
        ("unstaging-and-discarding-changes", True),
        ("branch-naming-and-housekeeping", False),
    ],
)
def test_early_learner_api_from_hard_mastery_to_preserved_transfer_result(
    django_user_model, level, first_pass
):
    from django.core.management import call_command
    from rest_framework.test import APIClient

    from adventures.models import AdventureLevelTier, AdventureLevelTierRun
    from players.services import get_or_create_player
    from progress.models import AdventureLevelTierCompletion, KpiCheckpoint

    call_command("seed_curriculum", verbosity=0)
    user = django_user_model.objects.create_user(username="early-api")
    player = get_or_create_player(user)
    from shop.models import Entitlement

    Entitlement.objects.create(player=player, kind="companion", slug="blue")
    tier = AdventureLevelTier.objects.get(adventure_level__slug=level, difficulty="hard")
    AdventureLevelTierCompletion.objects.create(
        player=player, tier=tier.adventure_level.tiers.get(difficulty="medium")
    )
    client = APIClient()
    client.force_authenticate(user=user)
    replays = early_mastery_replays()

    def launch(transfer=False):
        response = client.post(
            f"/api/adventure-level-tiers/{tier.id}/runs/",
            {"source_entry_point": "level_page", "transfer": transfer},
            format="json",
        )
        assert response.status_code == 201, response.content
        return response.json()

    def solve(payload):
        run = AdventureLevelTierRun.objects.get(pk=payload["id"])
        variant = run.selected_variant
        steps = []
        for index, step in enumerate(replays[variant.slug]["steps"]):
            for edit in variant.solution_workspace_files:
                if edit["after_command_index"] == index:
                    response = client.patch(
                        f"/api/adventure-tier-runs/{run.id}/files/",
                        {"path": edit["path"], "content": edit["content"]},
                        format="json",
                    )
                    assert response.status_code == 200, response.content
            run.refresh_from_db()
            response = client.post(
                f"/api/adventure-tier-runs/{run.id}/submit-command/",
                {
                    "command": step["command"],
                    "execution": {
                        **step["execution"],
                        "cwd": step["cwd"],
                        "client_run_revision": run.total_attempts,
                    },
                },
                format="json",
            )
            assert response.status_code == 200, (variant.slug, response.content)
            steps.append({"command": step["command"], "status": response.json()["run"]["status"]})
        run.refresh_from_db()
        assert run.status == "completed", (variant.slug, run.status)
        return {"case_id": variant.slug, "run_id": run.id, "steps": steps}

    mastery = [solve(launch()) for _ in range(tier.scenarios.filter(is_published=True).count())]
    assert AdventureLevelTierCompletion.objects.filter(player=player, tier=tier).exists()
    offered = client.get("/api/progress/performance/").json()
    assert any(point["tier_id"] == tier.id for point in offered["transfers"])
    assert offered["samples"]["transfer_pending"] == 1
    assessed = launch(True)
    assert (
        assessed["expected_state"] is None
        and assessed["command_guides"] == []
        and assessed["tutor"] is None
    )
    assert launch(True)["id"] == assessed["id"]
    if not first_pass:
        assert client.delete(f"/api/adventure-tier-runs/{assessed['id']}/").status_code == 204
    final_flow = solve(assessed if first_pass else launch(True))
    point = KpiCheckpoint.objects.get(player=player, tier=tier, kind="transfer")
    assert point.run_id == assessed["id"] and point.passed is first_pass
    report = client.get("/api/progress/performance/").json()
    module = next(
        row for row in report["modules"] if row["number"] == tier.adventure_level.chapter.number
    )
    assert module["rta"]["value"] == (100 if first_pass else 0)
    assert module["rta"]["denominator"] == 1
    assert report["samples"]["transfer_pending"] == 0
    if destination := os.environ.get("EARLY_API_FLOW_EVIDENCE_PATH"):
        path = Path(destination)
        data = json.loads(path.read_text()) if path.exists() else {}
        data[level] = {
            "mastery": mastery,
            "offered": offered,
            "assessed_task": assessed["scenario_context"],
            "expected_state": assessed["expected_state"],
            "command_guides": assessed["command_guides"],
            "transfer_completion": final_flow,
            "first_result": point.passed,
            "first_run_id": point.run_id,
            "later_practice_preserved_first_failure": not first_pass,
            "report": report,
        }
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")
