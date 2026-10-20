# Mastery KPI implementation evidence

Validated on 20 October 2026. The main agent owns all implementation; independent
read-only PRE, correctness, maintainability, POST and verifier reviews were used.
Final POST review found no blocker or major issue.

## Acceptance artifacts

- `evidence.json` saves the authenticated performance API response after the
  hard-tier history failure, success, failure, success, success. The final run
  submits an incorrect command and the actual three-command Git solution through
  the normal command-processing service. Reference 3 / actual 4 gives CAR 75%;
  SCR 100%, HLCR 100%, ARC 2 and first-transfer RTA 100%. A later better replay
  cannot rewrite these assessments. Learner and individual Admin results agree.
- `study-evidence.json` saves a prospective fixed manifest and cutoff report.
  Two participants with unequal activity contribute equally: CAR 87.5%, ARC 3.5,
  RTA 50%. Unattempted assignments remain in formal denominators; cutoff-crossing
  runs cannot retroactively complete a study. Repeated freeze/export is immutable.
- `reference-evidence.json` records validation of all 265 published variants with
  the real frontend Git engine and backend completion evaluator, in isolated
  in-memory SQLite. All 265 references validated; none were unscored. Reference
  counts range from 1 to 4 and are independent of star budgets.
- The mixed-module regression assigns different weights and unequal scenario
  counts to prove that fixed module weights, rather than scenario volume,
  determine participant overall scores.

## Checks

- Real-reference and policy tests: 5 passed, including unsolved-reference
  rejection, diagnostic-only policy and safe batch reservation.
- Frontend component/semantic tests: 67 passed across 9 files. A subsequent
  copy-only change was verified by 17 passing tests across 2 of those files.
- Frontend production build and ESLint on the 13 changed production modules passed.
- Architecture boundaries and all 17 architecture-guard algorithm tests passed.
- Migration drift, generated API contract, frontend API usage/type adoption,
  focused Ruff and root documentation checks are recorded in the final ledger.

The broad backend regression result and final contract/migration checks are
recorded under "Completion validation" below.

## Review repairs and ownership

First mastery has its own immutable checkpoint rather than the mutable best-star
pointer. Successful required repetitions do not increase retry penalties.
Exposure survives deleted empty practice launches. Transfer uses an explicit
start, preserves even empty abandonment as failure, and excludes stars, mastery
and rewards. Changed pending checkpoint content is missing evidence, without an
available start link. Reference hashes include the effective command limit.

The adventure run service owns transfer launch orchestration, while progress
services own checkpoint eligibility, recording and aggregation. This avoids a
runtime import cycle. The exact API contract guard was updated for decimal
numerators and the optional participant unit; contract ownership remains pinned.

The initial hash audit covered 77 pre-existing modified files. Seventy-one remain
byte-identical. Six deliberately overlapping files retain the user's changes
with scoped KPI additions: tier command processing, tier payloads, tier views,
TierOutcomeModal, TierStatusHeader and TierStartPage. A pre-existing untracked
optimistic-command test received a mock typing correction needed by the build.

## Activation and limits

The configured application database is PostgreSQL. No migrations, curriculum
reseeding, reference updates or study enrollment were applied to that database.
Tests use isolated SQLite. Run the commands in `KPI_METHODOLOGY.md` against the
intended environment to activate storage and validate references.

No existing scenario is automatically reserved as transfer content. A content
author must review a meaningful structural difference, reserve it with a written
reason, and leave ordinary practice available. Legacy histories without complete
exposure evidence or validated launch references stay unscored. Frozen-study
exports support formal evaluation; they do not establish causal learning gains.

This evidence uses the approved deterministic Django/API lane, component tests,
and real engine reference replay. It does not claim a deployed database cutover
or an end-to-end browser walkthrough.

## Completion validation (20 October 2026, second pass)

The first pass stopped before its final ledger. This pass reran every check,
repaired four defects, and adopted one definition change the user approved.

Defects found and repaired:

- **Ranged mastery dates.** `live_records` dated mastery by
  `AdventureLevelTierCompletion.completed_at`, which `update_best_score`
  moves forward on every better replay. A tier mastered on 5 October and
  improved on 15 October read as unmastered in an Admin range ending 10
  October (SCR 0% instead of 100%). Mastery is now dated by the immutable
  first-mastery checkpoint, or the last non-replay clear for legacy rows.
- **Learner deletion.** `KpiCheckpoint.run` used `PROTECT`, so deleting a
  learner with any checkpoint raised `ProtectedError`. It is now `RESTRICT`:
  a recorded run still cannot be deleted alone, but deleting the learner
  cascades through both rows.
- **Shared-database compatibility.** The new non-null run, variant and
  progress columns had no database default, so code predating them could not
  insert rows into an already migrated shared database. They now carry
  `db_default` values (`false` / `''`).
- **Untyped samples.** `samples` was a free-form `DictField`, which generated
  `Record<string, number>` and hid a fixture missing `mastery_missing`. It is
  now `PerformanceSamplesSerializer` with required integer fields. An empty
  Admin cohort also showed "0 contributing learners" instead of the missing
  data text.

Definition change, approved by the user: a live tier enters the SCR/HLCR
denominators once it has an outcome (mastery, an ended run, or commands idle
7+ days); opened-but-untouched tiers are `in_progress_tiers`. On the shared
development database, 28 of 108 counted tiers had been opened with no command.
The pooled live SCR moves from 58/108 (53.7%) to 58/80 (72.5%), and HLCR from
6/14 to 6/11. The participant-balanced Admin values are SCR 68.3% and HLCR
50.0% across 37 learners. Formal study reports are unchanged. A crash in the
legacy ARC fallback found during this change (a datetime summed as a count) was
repaired and covered by a regression test; all 51 learners' performance and
dashboard endpoints return 200 on the development database.

The acceptance values were regenerated after these changes and are unchanged:
SCR 100, CAR 75, HLCR 100, ARC 2, RTA 100; the study report keeps CAR 87.5,
ARC 3.5 and RTA 50 (`evidence.json`, `study-evidence.json`).

Checks:

- Full backend suite (before the definition change): 2637 passed, 3 failed.
  Two failures also fail on a clean `HEAD` checkout and are unrelated:
  `test_adventure_command_response_validates_partial_and_full_branches`
  (`learned_skills`) and the architecture-guard symbol manifest test
  (`python_catalog_contract_symbols`; this work's guard edit adds a second
  stale hash, `stats_openapi_contract_violations`). The third,
  `test_staff_analytics_returns_shape`, was a KPI regression: cohort rates
  now carry `unit: participants`, and its expectation was updated.
- Affected backend suites after the definition change (progress, adventures,
  adminconsole, common, chapter unlocks): 397 passed; only the two `HEAD`
  failures above remain.
- Frontend: 1071 of 1131 tests pass. The 60 failures in 16 files are the same
  60 that fail on a clean `HEAD` checkout (mascot, workspace tours,
  orientation and skill-learning). All KPI, performance and Admin tests pass.
  `tsc -b` errors only in the untracked `waveScenarioShapes.test.ts` from
  the concurrent curriculum-waves work.
- Migration drift, generated API contract, architecture boundaries, legacy
  vocabulary, frontend API usage/type adoption, documentation, CSS and seed
  target guards pass. Ruff lint/format and ESLint pass on changed files.

Activation: `adventures 0012` and `progress 0003` are now applied to the
configured development database, whose missing columns caused the 500 errors
(`column adventures_adventureleveltierrun.is_transfer does not exist`). Every
learner and Admin KPI endpoint returns 200 there. `kpi_refs` has not been run
against it: 0 of 265 variants hold a validated reference and none is reserved
for transfer, so live CAR and RTA remain unscored until that is done.
