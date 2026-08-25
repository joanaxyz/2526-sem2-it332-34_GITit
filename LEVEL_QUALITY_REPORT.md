# GIT it! level quality pass

Date: 2026-07-17

## Verdict

The previous curriculum was technically executable, but too much of the
advanced game had collapsed into command flashcards. The problem was not that
every level had a one-command solution. The problem was that 72 published map
nodes did:

| Story | Previous levels | Previous one-command levels | Share |
|---|---:|---:|---:|
| The Arcane Spire | 69 | 0 | 0.0% |
| Frostbound Citadel | 139 | 51 | 36.7% |
| Neon Backstreets | 76 | 21 | 27.6% |
| **Total** | **284** | **72** | **25.4%** |

That contradicted the product promise to replace command memorization with
practical problem-solving. A focused one-command introduction can be useful as
one beat inside a mission; it should not be presented as a complete advanced
level.

## Structural redesign

The command introductions remain available as short, focused waves so the
player can meet one new form at a time. Related waves are now grouped into
coherent two-to-four-wave field operations, such as:

- **Audit and Stage the Patch**: measure, check, then choose how to stage.
- **Map the Conflict**: inspect the merge structure and unresolved index.
- **Resolve or Retreat**: compare resolution paths with safe abort/continue
  exits.
- **Audit the Effective Behavior**: read a specific config value, compare the
  complete effective configuration, then verify repository state.
- **Inspect and Verify the Commit**: inspect a release commit before assigning
  trust to its signature.
- **Audit the Served Ref Set**: compare raw and formatted ref inventories before
  verifying the graph.

Three thin Neon chapters had no applied exercise beyond their isolated
introduction, so they gained authored four-command workflows for configuration
auditing, commit verification, and served-ref auditing.

## Resulting curriculum

| Story | Levels | Waves | Authored variants | One-command levels | Median shortest commands per level |
|---|---:|---:|---:|---:|---:|
| The Arcane Spire | 69 | 364 | 732 | 0 | 12 |
| Frostbound Citadel | 106 | 139 | 332 | 0 | 4 |
| Neon Backstreets | 65 | 79 | 230 | 0 | 7 |
| **Total** | **240** | **582** | **1,294** | **0** | **6.5** |

The map is smaller because related flashcard nodes were consolidated, not
deleted. Published waves increased from 579 to 582 and authored variants
increased from 1,288 to 1,294.

Eleven two-command levels remain intentionally. They are paired contrasts or
evidence reads—for example soft choices versus abort paths—not isolated
one-command payouts.

## Permanent quality gates

The curriculum test suite now rejects either of these advanced-story
regressions:

1. A complete published level whose shortest authored route is fewer than two
   commands.
2. An advanced field operation with more than four waves.

The existing pedagogy invariants still require a focused introductory wave for
each advanced command form. Together, these rules preserve learnability without
turning the map back into a syntax checklist.

## Verification

- Generated-target consistency: **2,056 cases current and consistent**.
- Focused curriculum and objective suite: **1,444 passed**.
- Advanced level-depth invariant: **passed**.
- Full rendered-frontend matrix: **240 / 240 levels passed** after one
  timing-sensitive submission was replayed with the hardened terminal-settle
  check.
- Accepted frontend runs: **582 / 582 complete wave sequences** and **1,805
  processable terminal commands**, with no strict-audit failures.
- Frontend regression suite: **408 / 408 tests passed**.
- Frontend production build: **passed**.
- Full backend suite: **1,761 tests passed**; its sole failure was the expected
  Arcane curriculum checksum lock after restoring four authored Project Files
  edits. The lock was repinned and its targeted test now passes.
- React completion overlays: duplicate command-form list keys were replaced
  with unique form IDs; the rendered matrix finished with no browser console
  errors.

The raw JSONL keeps both the original run 1618 timing miss and the accepted
replay run 1802. The replay submitted the same selected 10-command solution
through the visible terminal and passed an exact 3-of-3-wave audit.
