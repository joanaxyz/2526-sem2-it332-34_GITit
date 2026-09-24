"""Module 4 revert/rebase variants: distinct retries and strict grading.

Two layers:

* Always-on checks (normal pytest job): the seeded variant set, retirement of
  the old duplicate keys, the committed target states passing the stricter
  grading, and the content rule that no two variants in a Module 3-4 wave share
  both initial_state and target_state.
* Replay checks (need Node and frontend/node_modules; CI runs them in the
  generated-targets job): every correct, wrong and alternative solution is
  replayed through the real TypeScript simulator and the end state is scored by
  the backend evaluator.
"""

import json
import shutil
import subprocess
from pathlib import Path
from types import SimpleNamespace

import pytest
from django.core.management import call_command

from adventures.models import AdventureLevelTierRun, AdventureLevelTierWaveVariant
from common.constants import SESSION_STATUS_COMPLETED
from curriculum.management.commands.seed_legacy_modules import (
    DIFFICULTY_MAX_COUNTED_COMMANDS,
    MODULE_4_REBASE_CASES,
    MODULE_4_RETIRED_CASE_IDS,
    MODULE_4_REVERT_CASES,
    ev,
)
from evaluation.completion import CompletionEvaluationContext, PracticeCompletionEvaluator
from players.services import get_or_create_player

BACKEND = Path(__file__).resolve().parents[2]
FRONTEND = BACKEND.parent / "frontend"
TIER_TARGETS = BACKEND / "tier_targets.json"
LEGACY_STORY = "git-it-legacy"

LEVEL_BY_TABLE = {
    "reversing-pushed-commits-safely": MODULE_4_REVERT_CASES,
    "completing-rebase-recovery-sequences": MODULE_4_REBASE_CASES,
}
CASES = {
    case["case_id"]: (level, tier, case)
    for level, table in LEVEL_BY_TABLE.items()
    for tier, tier_cases in table.items()
    for case in tier_cases
}

# One plausible mistake per variant. Revert: undo the wrong commit, rewrite
# shared history, or forget to publish. Rebase: merge main in instead.
WRONG_SOLUTIONS = {
    "re6": ["git reset --hard c2", "git push --force"],
    "re7": ["git revert c2"],
    "re8": ["git reset --hard c3", "git push --force"],
    "rm6": ["git revert c3", "git push"],
    "rm7": ["git revert c3", "git push"],
    "rm8": ["git revert c4", "git push"],
    "rh6": ["git revert c3", "git push"],
    "rh7": ["git revert c3", "git push"],
    "rh8": ["git reset --hard c2", "git push --force"],
    **{key: ["git merge main"] for key in CASES if key[:2] in {"be", "bm", "bh"}},
}

# Other valid routes the grading must accept.
ALTERNATIVE_SOLUTIONS = {
    "re7": ["git revert HEAD", "git push"],
    "re8": ["git revert --no-edit c4", "git push origin main"],
    "rm7": ["git revert HEAD~1", "git push"],
    "rm8": ["git log --oneline", "git show c3", "git revert c3", "git push origin main"],
    "rh7": ["git revert --no-edit HEAD~1", "git push origin main"],
    "be7": ["git rebase main feature/search-filters"],
    "bm8": ["git switch main", "git switch feature/i18n", "git rebase main"],
    "bh8": ["git status", "git rebase main"],
}


def _evaluate(case: dict, state: dict, commands: list[str]):
    """Score a state with the same spec builder and evaluator the runtime uses."""
    variant = SimpleNamespace(
        id=None,
        semantic_key="",
        initial_state=case["initial_state"],
        evaluation_spec=ev(case["state_requirements"], required=case.get("required_commands", [])),
        target_state={},
    )
    return PracticeCompletionEvaluator().evaluate(
        CompletionEvaluationContext(variant=variant, next_state=state, executed_commands=commands)
    )


def _committed_targets() -> dict:
    return json.loads(TIER_TARGETS.read_text(encoding="utf-8"))


# ------------------------------------------------------------ always on ---


def test_each_affected_tier_has_three_new_variants_with_the_original_first():
    for level, table in LEVEL_BY_TABLE.items():
        for tier, tier_cases in table.items():
            keys = [case["case_id"] for case in tier_cases]
            assert len(keys) == 3, (level, tier, keys)
            # Variants are picked in semantic_key order, so X6 (the MVP
            # repository) stays the first pick for a first-time player.
            assert keys == sorted(keys), keys
            assert [key[-1] for key in keys] == ["6", "7", "8"]
            assert not set(keys) & MODULE_4_RETIRED_CASE_IDS


def test_x6_variants_keep_the_original_mvp_repository():
    revert_original = CASES["re6"][2]["initial_state"]
    rebase_original = CASES["be6"][2]["initial_state"]
    for key in ("rm6", "rh6"):
        assert CASES[key][2]["initial_state"] == revert_original
    for key in ("bm6", "bh6"):
        assert CASES[key][2]["initial_state"] == rebase_original
    # The MVP repositories, by their distinguishing content.
    assert [c["message"] for c in revert_original["commits"]] == [
        "Initial commit",
        "Add config module",
        "Risky config change",
        "Unrelated follow-up",
    ]
    assert rebase_original["branches"] == {"main": "c1", "feature/recovery": "c3"}


def test_every_new_variant_has_a_committed_target_state():
    targets = _committed_targets()
    assert set(CASES) <= set(targets), sorted(set(CASES) - set(targets))


@pytest.mark.parametrize("case_id", sorted(CASES))
def test_committed_target_passes_strict_grading_and_start_state_does_not(case_id):
    _, _, case = CASES[case_id]
    target = _committed_targets()[case_id]

    solved = _evaluate(case, target, case["solution_commands"])
    unsolved = _evaluate(case, case["initial_state"], [])

    assert solved.target_matched, [r.get("type") for r in solved.failed_rules]
    assert not unsolved.target_matched


def test_seed_unpublishes_retired_duplicates_and_keeps_their_runs(db, django_user_model):
    call_command("seed_legacy_modules", verbosity=0)
    wave = AdventureLevelTierWaveVariant.objects.get(
        slug="re6", wave__tier__adventure_level__chapter__story__slug=LEGACY_STORY
    ).wave
    # A production database still holds the old copies, with runs on them.
    retired = AdventureLevelTierWaveVariant.objects.create(
        wave=wave, slug="re1", label="Revert c3 safely", semantic_key="re1", case_id="re1"
    )
    player = get_or_create_player(
        django_user_model.objects.create_user(username="m4-history", password="pass12345")
    )
    run = AdventureLevelTierRun.objects.create(
        player=player,
        tier=wave.tier,
        current_wave=wave,
        selected_variant=retired,
        status=SESSION_STATUS_COMPLETED,
    )

    call_command("seed_legacy_modules", verbosity=0)

    retired.refresh_from_db()
    run.refresh_from_db()
    assert retired.is_published is False
    assert run.selected_variant_id == retired.id
    published = set(wave.variants.filter(is_published=True).values_list("slug", flat=True))
    assert published == {"re6", "re7", "re8"}


def test_seeding_keeps_committed_target_states_on_every_rerun(db):
    """Re-seeding used to write target_state={} and needed a manual import."""
    call_command("seed_legacy_modules", verbosity=0)
    call_command("seed_legacy_modules", verbosity=0)

    targets = _committed_targets()
    variants = AdventureLevelTierWaveVariant.objects.filter(
        wave__tier__adventure_level__chapter__story__slug=LEGACY_STORY
    )
    assert variants.exists()
    mismatched = [v.case_id for v in variants if v.target_state != targets.get(v.case_id)]
    assert not mismatched, mismatched


def test_no_two_variants_in_a_module_3_4_wave_share_start_and_target(db):
    """A retry must be able to land on a structurally different scenario.

    TODO: extend to Modules 1-2 once their start-state-only overlaps are
    reviewed (they currently differ in target_state, so they would pass).
    """
    call_command("seed_legacy_modules", verbosity=0)
    variants = AdventureLevelTierWaveVariant.objects.filter(
        is_published=True,
        wave__tier__adventure_level__chapter__story__slug=LEGACY_STORY,
        wave__tier__adventure_level__chapter__number__in=(3, 4),
    ).select_related("wave")

    missing_targets = [v.slug for v in variants if not v.target_state]
    assert not missing_targets, f"variants without a target_state: {missing_targets}"

    seen: dict[tuple[int, str], str] = {}
    duplicates = []
    for variant in variants:
        fingerprint = json.dumps([variant.initial_state, variant.target_state], sort_keys=True)
        key = (variant.wave_id, fingerprint)
        if key in seen:
            duplicates.append((variant.wave.slug, seen[key], variant.slug))
        else:
            seen[key] = variant.slug
    assert not duplicates, duplicates


# ------------------------------------------------------ simulator replay ---

needs_simulator = pytest.mark.skipif(
    shutil.which("node") is None or not (FRONTEND / "node_modules").exists(),
    reason="replay needs Node and frontend/node_modules (CI: generated-targets job)",
)


@pytest.fixture(scope="module")
def replayed(tmp_path_factory):
    """Replay every correct, wrong and alternative route in one simulator run."""
    routes = {}
    for case_id, (_, tier, case) in CASES.items():
        budget = DIFFICULTY_MAX_COUNTED_COMMANDS[tier]
        for kind, commands in (
            ("correct", case["solution_commands"]),
            ("wrong", WRONG_SOLUTIONS[case_id]),
            ("alternative", ALTERNATIVE_SOLUTIONS.get(case_id)),
        ):
            if commands:
                routes[f"{case_id}::{kind}"] = {
                    "initial_state": case["initial_state"],
                    "solution_commands": commands,
                    "max_counted_commands": budget,
                }
    tmp = tmp_path_factory.mktemp("m4-replay")
    source, output = tmp / "routes.json", tmp / "states.json"
    source.write_text(json.dumps(routes), encoding="utf-8")
    result = subprocess.run(
        ["node", "scripts/generate-targets.mjs", str(source), str(output)],
        cwd=FRONTEND,
        capture_output=True,
        text=True,
        check=False,
    )
    # A non-zero exit means a route was rejected or ran over its budget.
    assert result.returncode == 0, result.stderr
    return json.loads(output.read_text(encoding="utf-8"))


@needs_simulator
@pytest.mark.parametrize("case_id", sorted(CASES))
def test_correct_solution_passes_and_matches_committed_target(replayed, case_id):
    _, _, case = CASES[case_id]
    state = replayed[f"{case_id}::correct"]

    outcome = _evaluate(case, state, case["solution_commands"])

    assert outcome.target_matched, [r.get("type") for r in outcome.failed_rules]
    assert state == _committed_targets()[case_id], "tier_targets.json is stale"


@needs_simulator
@pytest.mark.parametrize("case_id", sorted(CASES))
def test_wrong_solution_fails(replayed, case_id):
    _, _, case = CASES[case_id]
    commands = WRONG_SOLUTIONS[case_id]

    outcome = _evaluate(case, replayed[f"{case_id}::wrong"], commands)

    assert not outcome.target_matched, commands


@needs_simulator
@pytest.mark.parametrize("case_id", sorted(ALTERNATIVE_SOLUTIONS))
def test_alternative_valid_solution_passes(replayed, case_id):
    _, _, case = CASES[case_id]
    commands = ALTERNATIVE_SOLUTIONS[case_id]

    outcome = _evaluate(case, replayed[f"{case_id}::alternative"], commands)

    assert outcome.target_matched, (commands, [r.get("type") for r in outcome.failed_rules])
