# Dogfood report: GIT it! level-quality matrix

| Field | Value |
|---|---|
| **Date** | 2026-07-17 |
| **App URL** | http://localhost:5173 |
| **Browser session** | `git-it-levels-quality2-20260717` |
| **Matrix run** | `git-it-levels-quality2-20260717-20260717T010909` |
| **Scope** | Submit the selected solution for every published adventure level and wave through the rendered frontend |
| **Account** | Fresh disposable QA account `qa_levels_quality2_20260717`, created through the frontend |

## Final result

| Story | Levels | Waves | Passed | Failed |
|---|---:|---:|---:|---:|
| The Arcane Spire | 69 | 364 | 69 | 0 |
| Frostbound Citadel | 106 | 139 | 106 | 0 |
| Neon Backstreets | 65 | 79 | 65 | 0 |
| **Total** | **240** | **582** | **240** | **0** |

Accepted runs contain **1,805 processable terminal commands**. Backend
rejections, incomplete authored sequences, prefix-only advances, and strict
per-run audit failures: **0**.

The matrix originally recorded one timing-sensitive driver miss at Arcane
Spire's **Patch Movement Workflows**. Run 1618 reached wave 2 after `git stash`
and `git cherry-pick c2`, but the browser driver attempted the next submission
before the rendered terminal had fully settled. The failure record and
screenshot remain in the raw evidence. After adding a rendered-input settle
check, replay run 1802 submitted the same selected 10-command solution through
the visible terminal and passed its exact 3-of-3-wave audit.

## Quality redesign

The previous map did not consist entirely of one-command levels, but too much
of the advanced curriculum did:

| Story | Previous levels | Previous one-command levels | Share |
|---|---:|---:|---:|
| The Arcane Spire | 69 | 0 | 0.0% |
| Frostbound Citadel | 139 | 51 | 36.7% |
| Neon Backstreets | 76 | 21 | 27.6% |
| **Total** | **284** | **72** | **25.4%** |

Those isolated map nodes are now waves inside coherent two-to-four-wave field
operations. The redesigned 240-level map has **zero complete one-command
levels**, while retaining the focused introductions inside larger missions.
Three thin Neon chapters also gained applied workflows for configuration
auditing, commit verification, and served-ref auditing.

Permanent curriculum gates now reject:

1. Any complete Frostbound or Neon level whose shortest authored route has
   fewer than two commands.
2. Any Frostbound or Neon field operation with more than four waves.

## Regressions fixed

- Four Arcane stash/cherry-pick workflows now perform their missing Project
  Files edits before staging, so the authored commands operate on real changes.
- The frontend driver waits for the rendered terminal mutation cycle between
  commands, preventing false misses in long sequences.
- Adventure completion overlays use unique command-form IDs as React list keys,
  eliminating duplicate-key console errors from repeated slugs such as `list`
  and `create`.
- Relative artifact paths now resolve from the workspace root even after the
  runner initializes Django from the backend directory.

## Verification

- Full frontend matrix: **240 / 240 levels**, **582 / 582 waves**.
- All accepted matrix runs re-audited directly from persisted command steps:
  **240 passed**, **0 failed**.
- Authored variants in the cheat sheet: **1,294**.
- Generated curriculum targets: **2,056 current and consistent**.
- Focused curriculum/objective suite: **1,444 passed**.
- Frontend tests: **408 / 408 passed**.
- Frontend production build: **passed**.
- Full backend suite: **1,761 passed** with one expected preservation-checksum
  failure caused by the intentional Arcane fixture repairs. After repinning the
  checksum, that targeted preservation test passed.
- Browser console after the rendered matrix: **no errors**.
- Repository whitespace validation: **passed**.

## Evidence

- [Frontend level results](frontend-level-test-results.md) contains all 240
  normalized per-level results and the replay explanation.
- `level-sequence-results.jsonl` preserves the original 240 matrix records plus
  the successful hardened replay record.
- [Matrix completion screenshot](screenshots/quality-matrix-240-completed.png)
  captures the final rendered Neon level's cleared state.
- [Hardened replay screenshot](screenshots/quality-patch-movement-replay-completed.png)
  captures the repaired Arcane workflow's visible replay-complete state.
- [All-level cheat sheet](../LEVEL_CHEAT_SHEET.md) contains every level, wave,
  distinct authored sequence, and required Project Files action.
- [Level quality report](../LEVEL_QUALITY_REPORT.md) records the before/after
  structural metrics and permanent quality gates.
