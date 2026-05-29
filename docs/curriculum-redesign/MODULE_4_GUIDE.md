# Module 4 — Scenario Design Guide

**Status: Implemented ✅**
**Last updated: 2026-05-29**

---

## Module Overview

**Title:** Advanced Recovery and History
**Chapters:** 7 (recovery operations)
**Lessons:** 3
**Target students:** BSIT 3rd-year, CIT-U — Modules 1–3 completion assumed

---

## SO Audit

Source of truth: *GIT it! Final Proposal* and `docs/GIT_it_Proposal.md`.

### Instructional SOs — redesign scope

| SO | Approved Description | Seed lesson slug | KPI |
|----|----------------------|------------------|-----|
| SO 4.1 | Recovering from Hard Resets | `recovering-from-hard-resets` | CAR ≥ 70% |
| SO 4.2 | Reversing Pushed Commits Safely | `reversing-pushed-commits-safely` | CAR ≥ 70% |
| SO 4.3 | Completing Rebase Recovery Sequences | `completing-rebase-recovery-sequences` | CAR ≥ 70% |

### KPI SOs — measurement only, not instructional objectives

| SO | Description | KPI | How it is measured |
|----|-------------|-----|--------------------|
| SO 4.4 | Module-level completion rate | HLCR ≥ 70% | Aggregated Hard-session completion across SO 4.1–4.3 |
| SO 4.5 | Reduced trial-and-error | ARC ≤ 2 | Average retry count across all Module 4 sessions |

**SO mapping verdict:** 3 instructional SOs, 2 KPI-only SOs. All 3 lessons map 1:1 to
approved SOs. No flagged lessons, no invented SOs.

### UI structure

Module 4 has no Guided Preview and no concept-only lessons. All 3 lessons are scenario-bearing.

| UI display | Seed sort order | Slug | SO |
|-----------|-----------------|------|----|
| Lesson 1 | 1 | `recovering-from-hard-resets` | SO 4.1 |
| Lesson 2 | 2 | `reversing-pushed-commits-safely` | SO 4.2 |
| Lesson 3 | 3 | `completing-rebase-recovery-sequences` | SO 4.3 |

---

## Curriculum Assumptions

| Item | Decision |
|------|----------|
| Modules 1–3 prerequisite | `git log`, `git status`, `git branch`, `git switch`, `git rebase`, `git push`, `git revert` are prior knowledge |
| `git reflog` | Introduced in SO 4.1 — students may have seen it as a diagnostic in Module 1 but now use it for recovery navigation |
| `git reset --hard` | Used as the action that *creates* the recovery scenario (applied in initial state) — students do not themselves run a destructive reset in practice |
| `git revert --no-edit` | Accepted solution for Medium difficulty to avoid interactive editor; evaluator does not require the flag |
| `git push -u origin main` | Accepted for Hard difficulty; semantically equivalent to `git push` where tracking is already set |
| `git rebase -i` | Used in Medium rebase scenarios — simulator models interactive rebase abstractly; the target state is the resulting clean commit graph |
| No force-push scenarios | `git push --force` is deliberately excluded — Module 4 teaches safe recovery, not destructive remote rewrites |
| Merge conflicts during rebase | Rebase scenarios are authored to be conflict-free; conflict rebase recovery is out of scope |

---

## Seed Audit

### Current implementation status

The existing `seed_module4_scenarios.py` implements all 3 lessons. Pool sizes:

| Lesson | Slug | Easy | Medium | Hard | Total |
|--------|------|------|--------|------|-------|
| L1 Hard Reset Recovery | `recover-from-hard-reset-incident` | 5 | 5 | 5 | 15 |
| L2 Revert Pushed Commit | `reverse-pushed-commit-safely` | 5 | 5 | 5 | 15 |
| L3 Rebase Recovery | `complete-rebase-recovery-sequence` | 5 | 5 | 5 | 15 |
| **Total** | | **15** | **15** | **15** | **45** |

### Pool sizing verdict

All pools have 5 Easy, 5 Medium, 5 Hard — meeting the minimum (Easy ≥ 5, Medium ≥ 4, Hard ≥ 4).
**No new variants are required.** ✅

---

## Command Coverage Matrix

| Command | Lesson | Difficulty | Counted? |
|---------|--------|------------|----------|
| `git status` | L1, L3 | All | ❌ Diagnostic |
| `git log --oneline --graph --all` | L1, L2, L3 | All | ❌ Diagnostic |
| `git reflog` | L1 | All | ❌ Diagnostic |
| `git show <commit>` | L1 | All | ❌ Diagnostic |
| `git merge-base <b1> <b2>` | L3 | Medium, Hard | ❌ Diagnostic |
| `git rev-list --count <b1>..<b2>` | L3 | Medium, Hard | ❌ Diagnostic |
| `git reset --hard <target>` | L1 | All | ✅ Counted (recovery step) |
| `git switch -c <branch> <commit>` | L1 | All | ✅ Counted |
| `git revert <commit>` | L2 | All | ✅ Counted |
| `git revert --no-edit <commit>` | L2 | Medium | ✅ Counted |
| `git push` | L2 | All | ✅ Counted |
| `git push -u origin main` | L2 | Hard | ✅ Counted |
| `git rebase <target>` | L3 | Easy, Hard | ✅ Counted |
| `git rebase -i <target>` | L3 | Medium | ✅ Counted |

---

## Difficulty Progression Philosophy

### Cognitive load per level

| Difficulty | What the student is given | What the student must infer |
|------------|--------------------------|----------------------------|
| Easy | Explicit recovery target named, shallow reset depth (1), bad commit named directly | Which reflog entry to use |
| Medium | Deeper reset (2), bad commit buried in history, rebase uses `-i` | Which history entry corresponds to the lost tip; which commit to revert |
| Hard | Deepest reset (3), mixed interactive/non-interactive rebase, no guidance on which commit is bad | Full reasoning: read the reflog or history, identify the correct target, reconstruct the safe state |

### Module 4 specific: recovery reasoning

Module 4 adds a distinct cognitive demand: students must reason *backwards* from a broken
state to identify what was lost and how to restore it. This is different from Modules 1–3
where the starting state is clean and students move *toward* a goal. Here:

- The initial state is already broken (post-reset, or has a bad pushed commit, or has a
  diverged branch)
- The student must read evidence (reflog, log, branch graph) before acting
- Hard variants have noisier reflog trails or less obvious bad commit positions

---

## Existing Variants Inventory

### Lesson 1 — Hard Reset Recovery

5 Easy cases (`4-1-e1` through `4-1-e5`): depth=1 reset (HEAD~1), 4-commit chain,
narrative rotates across 5 incident descriptions (release dry-run, hotfix prep, handover
crunch, incident triage, QA reconciliation). Target: create `recovery-<case_id>` branch at `c3`.

5 Medium cases (`4-1-m1` through `4-1-m5`): depth=2 reset (HEAD~2), otherwise same structure.

5 Hard cases (`4-1-h1` through `4-1-h5`): depth=3 reset (HEAD~3), otherwise same structure.

**Environment:** all cases use a `release engineer / software company` framing — single
environment type across all difficulties. This is acceptable because the skill focus is
history evidence reading, not narrative variety.

### Lesson 2 — Revert Pushed Commit

5 Easy cases (`4-2-e1` through `4-2-e5`): `bad_commit="c3"` (tip commit), 4-commit chain,
`origin/main` already set to `c3`. Solution: `git revert c3` then `git push`.

5 Medium cases (`4-2-m1` through `4-2-m5`): `bad_commit="c2"` (non-tip, buried 1 commit back).
Solution: `git revert c2 --no-edit` then `git push`.

5 Hard cases (`4-2-h1` through `4-2-h5`): `bad_commit="c2"`, solution uses `git push -u origin main`.

**Environment:** all cases use a `backend developer / software company` framing.

### Lesson 3 — Rebase Recovery

5 Easy cases (`4-3-e1` through `4-3-e5`): non-interactive rebase, `feature/recovery` off `c0`,
`main` at `c1`, 2 feature commits (`c2`, `c3`). Solution: `git rebase main`.

5 Medium cases (`4-3-m1` through `4-3-m5`): interactive rebase (`-i`), same structure.
Solution: `git rebase -i main` plus integrity checks (`merge-base`, `rev-list`).

5 Hard cases (`4-3-h1` through `4-3-h5`): alternating interactive/non-interactive based on
case index parity. Solution path includes all integrity checks.

**Environment:** all cases use a `feature owner / software company` framing.

---

## Critical Seed Issues

> ⚠️ **THREE BLOCKING ISSUES** in the existing seed that must be fixed before Module 4
> can be considered production-ready. Pool sizing is correct, but the seed has structural
> defects.

### Issue 1: Empty target rules for SO 4.1 and SO 4.3

```python
hard_reset_target = {}   # Line ~263 in module_four_scenarios()
rebase_target = {}       # Line ~266 in module_four_scenarios()
```

Both target rules are empty dicts. The `StateBasedEvaluator` with an empty rule set will
always return `target_matched=True` — every student command sequence completes the scenario
regardless of actual outcome.

**Required fix:** Define real target rules for both:

```python
hard_reset_target = {
    "skip_required_commands": True,
    "branch_exists": ["{{recovery_branch}}"],
    "branch_points_to": {"{{recovery_branch}}": "{{recovery_target}}"},
    "staging_empty": True,
    "working_tree_clean": True,
}

rebase_target = {
    "skip_required_commands": True,
    "head_branch": "feature/recovery",
    "staging_empty": True,
    "working_tree_clean": True,
    "conflict_free": True,
    "rules": [
        {
            "type": "branch_is_rebased_onto",
            "branch": "feature/recovery",
            "onto": "{{rebase_target}}",
        },
        {
            "type": "min_commits_on_branch",
            "branch": "feature/recovery",
            "minimum": 2,
        },
    ],
}
```

If `branch_is_rebased_onto` is not an existing rule type in the evaluator, the minimal
safe alternative is:

```python
rebase_target = {
    "skip_required_commands": True,
    "head_branch": "feature/recovery",
    "staging_empty": True,
    "working_tree_clean": True,
    "conflict_free": True,
    "min_commits_on_branch": {"feature/recovery": 2},
    "rules": [
        {
            "type": "branches_not_equal",
            "left": "feature/recovery",
            "right": "{{rebase_target}}",
        },
    ],
}
```

**Verify before implementing:** check `evaluation/services.py` `_check_rule()` for the
full list of supported rule types.

### Issue 2: Debug logging scaffold left in the seed

The `_debug_log()` function (lines 57–70) and all `# region agent log` / `_debug_log()`
calls in `handle()` and `_ensure_lesson_kind_default()` (lines ~540–808) are agent residue
from a previous investigation session. They write to `debug-f8332c.log` and import
`json`, `time`, `uuid`, `Path` solely for that purpose.

**Required fix:** Remove entirely:
- `import json`, `import time`, `import uuid`, `from pathlib import Path` (lines 5–7)
- `_debug_log()` function definition (lines 57–70)
- All `# region agent log` / `_debug_log(...)` / `# endregion` blocks in `handle()` and
  `_ensure_lesson_kind_default()`
- The entire `_ensure_lesson_kind_default()` method and its call in `handle()` (this
  method patches a DB column default at runtime — it is not a seed concern and should
  instead be a proper migration if still needed)

### Issue 3: `required_successful_attempts` not driven by scenario spec

In `handle()`:
```python
"required_successful_attempts": 2 if difficulty == DIFFICULTY_EASY else 1,
```

This is hardcoded, bypassing the `dspec` dict (which in Module 3 carries
`required_successful_attempts` via the `diff()` helper). The correct values
for Module 4 based on the curriculum doc session counts are:

| Lesson | Easy | Medium | Hard |
|--------|------|--------|------|
| L1 Hard Reset Recovery | 2 | 1 | 1 |
| L2 Revert Pushed Commit | 2 | 1 | 1 |
| L3 Rebase Recovery | 2 | 1 | 1 |

The current hardcoded logic happens to produce the correct values (2 for Easy, 1 otherwise),
but it should be driven by `dspec` for consistency with Modules 1–3. Add
`"required_successful_attempts"` to `difficulty_spec()` and wire it through.

---

## Seed Implementation Notes

### What already exists and is correct

- `MODULE_FOUR_LESSONS` — 3 entries, correct slugs and titles
- `hard_reset_case()`, `revert_case()`, `rebase_case()` helper functions
- All 45 case definitions (5E/5M/5H × 3 lessons)
- `revert_target` — has real rules (verify `new_revert_commit_exists` and
  `revert_preserves_history` are registered rule types in `evaluation/services.py`)
- Pool sizing — all lessons at 5/5/5, meets minimum
- `DIAG_PATTERNS` — correct for Module 4 diagnostic commands

### What needs changing (in priority order)

1. **Fix `hard_reset_target` and `rebase_target`** — blocking correctness issue
2. **Remove `_debug_log` scaffold** — production cleanliness
3. **Remove `_ensure_lesson_kind_default()`** — runtime DB patching belongs in migrations
4. **Add `required_successful_attempts` to `difficulty_spec()`** — consistency with other modules

### Context string requirement

Every case dict passed to the seed's case-builder helpers must include a `"context"` key
with a rich narrative paragraph. This is the same pattern established in Module 1.

**How it works in the seed:**

1. `student_context_template(kind)` (if it exists in Module 4's seed) must return
   `"story": "{{context}}"` — not a static string.

2. Each case helper call (`hard_reset_case`, `revert_case`, `rebase_case`) must accept and
   forward a `context=` keyword argument. Example:

   ```python
   hard_reset_case(
       case_id="4-1-e1",
       context=(
           "During a late-night release dry-run, your team lead ran `git reset --hard HEAD~1` "
           "to undo a bad config commit — but the commit contained critical migration SQL that "
           "still needs to ship. Recover the lost commit using the reflog."
       ),
       depth=1,
       narrative="release dry-run",
       ...
   )
   ```

3. The materializer substitutes `{{context}}` into the Scenario Brief shown to students.

**Migration checklist for the seed:**

- [ ] Update `student_context_template` kinds to return `"story": "{{context}}"`
- [ ] Add `context` parameter to `hard_reset_case()`, `revert_case()`, `rebase_case()`
- [ ] Add `context=` string to all 45 existing cases — use the narrative descriptions in
  the Existing Variants Inventory section (release dry-run, hotfix prep, handover crunch,
  incident triage, QA reconciliation for L1; adapt similarly for L2 and L3)

> **Note:** Module 4's variants use a rotating-narrative pattern (5 narratives × 3 depths
> for Lesson 1, etc.). When adding context strings, vary the framing across the 5 narrative
> slots so each case feels distinct even within the same lesson.

### `required_successful_attempts` reference

| Lesson | Easy | Medium | Hard |
|--------|------|--------|------|
| L1, L2, L3 | 2 | 1 | 1 |

### Command policy reference (already correct in seed)

| Lesson | Easy `(min, authored_max)` | Medium | Hard |
|--------|---------------------------|--------|------|
| L1 Hard Reset Recovery | `(2, 6)` | `(2, 7)` | `(2, 8)` |
| L2 Revert Pushed Commit | `(2, 4)` | `(2, 5)` | `(2, 6)` |
| L3 Rebase Recovery | `(1, 5)` | `(1, 6)` | `(1, 7)` |

Global `DIFFICULTY_MAX_COUNTED_COMMANDS` (Easy=12, Medium=10, Hard=8) overrides
`authored_max` in the seed handler — the authored max is advisory only.

---

## KPI SO Notes

**SO 4.4** (HLCR ≥ 70%): Aggregated Hard-session completion across SO 4.1–4.3 lessons.
All three lessons contribute equally since all are instructional.

**SO 4.5** (ARC ≤ 2): Average retry count per session. Module 4's recovery scenarios
are intentionally cognitively demanding — ARC monitoring is particularly important here
to detect variant pools that are systematically too hard.

**RTA (Retry Transfer Assessment)** applies from Module 3 onward — this means Module 4
retry variants must be structurally different from the first attempt, not just the same
scenario re-served. The current `hard_reset_case()`, `revert_case()`, and `rebase_case()`
generators produce structurally distinct cases (different depth, different bad commit
position, different suffix), so RTA is satisfied by the existing pool design.
