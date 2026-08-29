# Backend Architecture and Production Readiness Implementation Plan

**Intent:** Make the persisted backend domain coherent, remove obsolete model states, protect reward/progress data under concurrent production traffic, and prove the repository against its production gates.
**Current Behavior:** The service/selector architecture and deployment checks are established and currently pass, and an in-progress cleanup already adds important run, scoring, authoring-runtime, and uniqueness constraints. However, authoring still exposes the obsolete `store` visibility after content sales were removed, so content can be listed as available but rejected at launch. A few same-row invariants remain service-only, and streak updates are not serialized.
**Expected Outcome:** Every persisted authoring visibility has one supported meaning; historical store-visible content remains available through an explicit data cutover; ledger, streak, and command-step rows reject impossible values; streak updates serialize per player; model changes have committed migrations; dependency locks use portable public sources; and CI-equivalent backend, architecture, dependency, frontend, and build checks pass.
**Target-Perspective Output:** A deployer can apply the committed migration graph to PostgreSQL and run the repository quality gates without generating schema changes or finding dependency vulnerabilities. A player continues to see and launch formerly store-visible published content, and concurrent completions cannot silently lose streak progress.
**Truth Owner:** Django models and committed migrations own persisted invariants; application services own valid state transitions and concurrency; selectors own public read visibility; CI and repository check scripts own production acceptance.
**Contract Boundary:** Any state accepted by a service must be representable under the database constraints, and any persisted authoring visibility returned by a public selector must be launchable by the same access policy.
**Cutover:** Convert all persisted `ContentDefinition.visibility="store"` rows to `"public"`, then remove `store` from the model and selector contract. Add constraints through forward-only Django migrations and keep existing service APIs stable.
**Displaced Path:** `VISIBILITY_STORE`, store-inclusive authoring selectors, service-only ledger/streak/command-step invariants, and redundant indexes do not remain as alternate paths.
**Value Density:** The slice closes a user-visible authorization mismatch and protects high-value progress/reward records without redesigning APIs or broad application layers.
**Acceptance Evidence:** The implementing maintainer inspects a clean migration plan, production configuration check, dependency audit, complete backend test result, architecture/contract guard results, frontend tests/build, and a focused migration test proving store-visible content is preserved as public and launchable.
**Evidence Lane:** Focused model/service tests, migration drift and clean-database checks, full backend suite with coverage, repository guards, dependency audits, frontend checks, then final diff and worktree-scope review.
**Kill Criteria:** No `store` authoring visibility remains in active code or persisted rows after migration; no environment-private dependency URL remains in a committed lockfile; no new duplicate source of truth is introduced; no model change lacks a migration and direct integrity test; no production-ready claim is made if PostgreSQL migration or dependency evidence cannot be captured.
**Architecture Slice:** Authoring services write `ContentDefinition`; authoring selectors expose public content; shop access authorizes launch; progress services write streak and ledger rows; command services write `CommandStep`; Django models/migrations enforce durable invariants; CI scripts verify the assembled system.
**Plan Review Gate:** Requires PRE review before execution.

## Architecture Map

### Files to create

- `backend/authoring/migrations/0004_*.py` for the store-to-public data cutover and authoring constraints.
- `backend/practice/migrations/0002_*.py` for command-step integrity constraints.
- `backend/progress/migrations/0003_*.py` and `0004_*.py` for repair-first ledger and streak integrity constraints.
- `backend/adventures/migrations/0005_*.py` and `backend/challenges/migrations/0004_*.py` for the persisted variant slug bound discovered by PostgreSQL verification.
- A focused migration test only if the existing integrity test module cannot prove the data cutover safely.
- This goal package under `docs/goals/backend-production-readiness/`.

### Files to modify

- `backend/authoring/models.py`
- `backend/authoring/selectors/core.py`
- `backend/common/models.py`
- `backend/common/tests/test_model_integrity_constraints.py`
- `backend/practice/models.py`
- `backend/practice/services/builders.py`
- `backend/practice/tests/test_variant_builder.py`
- `backend/progress/models.py`
- `backend/progress/services/streaks.py`
- `backend/adventures/services/runs.py`
- `backend/requirements.in`, `backend/requirements.txt`, and `backend/requirements-dev.txt` when the production dependency audit identifies a remediable vulnerability.
- `frontend/package-lock.json` when clean-install evidence identifies a non-portable resolved dependency source.
- `.github/workflows/ci.yml` for supported official action runtimes and verified committed-migration policy.
- The nearest focused progress/service test module.
- Existing in-progress backend model and migration changes only where verification exposes a defect.
- Root architecture or CI documentation only if the implemented contract changes make it stale.

### Files to avoid

- Unrelated dirty frontend assets, curriculum content, reference captures, generated dogfood artifacts, and blueprint documents.
- Generated API or curriculum artifacts unless their supported freshness checks prove regeneration is required.
- Existing user-owned changes outside the named backend/goal slice.
- Historical migrations that have already shipped; new changes receive new forward migrations.

### Source of truth

- Persisted domain shape: each Django app's `models.py` plus committed migrations.
- Valid state transitions: app service packages.
- Public authored-content visibility: `authoring/selectors/core.py` coordinated with `shop/access.py`.
- Production acceptance: `.github/workflows/ci.yml` and `scripts/checks/*`.

### Read path

`ContentDefinition` -> authoring selector -> API payload -> launch access check; progress/streak/ledger and command-step rows -> selectors/metrics/payloads -> player and admin API responses.

### Write path

Authoring, run, wallet, streak, and command services -> Django ORM -> database constraints -> selector/payload read models.

### Contract boundary

- Publicly discoverable authored content must be launchable.
- Ledger entries must represent a non-zero credit or debit.
- A streak's longest value cannot be below its current value.
- A command step records exactly one parent, one command attempt, a binary counted increment, and a cumulative total that includes that increment.

### Integration points

- Authoring create/update/publish validation and public selector.
- Shop launch authorization.
- Progress completion callbacks and metrics.
- Adventure/challenge command-step writes.
- Migration graph, SQLite unit-test database, and PostgreSQL integration database.

### Migration/cutover

Use a `RunPython` operation to update `store` rows to `public` before altering choices and adding a database visibility constraint. Add new forward migrations after the existing untracked cleanup migrations. Verify both zero-state migration and migration from the immediate previous authoring state.

### Displaced path

Delete the store visibility constant, choice, validation branch, and selector inclusion. Do not retain a compatibility alias because the persisted data migration is the compatibility mechanism.

### Acceptance evidence gate

Do not complete the goal until the migration graph is drift-free, focused cutover/integrity tests pass, the full backend suite and repository guards pass, dependency audits are clean, and frontend tests/build confirm the backend contract cleanup did not break the application.

## Task 1: Preserve and verify the in-progress schema cleanup

**Allowed scope:** Existing modified backend model, compiler, selector, migration, integrity-test, architecture, and CI files only.

**Expected output:** Existing run budget/star constraints, system-content uniqueness, exactly-one published runtime target, runtime replacement behavior, and redundant-index removals remain coherent and tested.

**Verification:**

- `ruff check .` from `backend/`
- `python manage.py check`
- `python manage.py makemigrations --check --dry-run`
- `pytest -q common/tests/test_model_integrity_constraints.py common/tests/test_bug_regressions.py`

**Acceptance evidence:** Each new constraint has a direct rejection test and every index removal is covered by an equal or stronger leftmost unique index for the actual query path.

**Parallel:** No. This establishes the safe baseline in the dirty worktree.

## Task 2: Retire obsolete store visibility with a preserving cutover

**Allowed scope:** Authoring model/selector, new authoring migration, and focused tests.

**Expected output:**

- Only `private` and `public` are valid authoring visibility states.
- Existing `store` rows migrate to `public` before the database constraint is applied.
- Public discovery and launch authorization agree.
- Unknown visibility values are rejected by the database.

**Verification:**

- Focused migration test from authoring `0003` to the new migration.
- Focused model integrity test using a direct ORM write.
- Existing authoring, admin-console, and shop tests.
- `rg -n "VISIBILITY_STORE|visibility.*store" backend frontend scripts`

**Acceptance evidence:** A row created as published/store at the old migration state is public after migration and satisfies both discovery and launch behavior.

**Parallel:** No. The data migration must precede contract removal.

## Task 3: Enforce progress and command-step invariants

**Allowed scope:** Progress/practice models, new forward migrations, streak service, and focused tests.

**Expected output:**

- Zero-value ledger entries are rejected.
- `longest_streak >= current_streak` is enforced.
- Streak updates lock the per-player row inside a short transaction.
- Command-step attempt numbers start at one, counted increments are at most one, and cumulative counted totals cannot be lower than the current increment.

**Verification:**

- Focused integrity tests exercise direct ORM rejection.
- Progress streak tests exercise same-day idempotency and consecutive/reset behavior.
- Adventure/challenge command submission tests prove valid rows still persist.
- `python manage.py makemigrations --check --dry-run`

**Acceptance evidence:** Impossible rows fail at the database boundary while real adventure/challenge submissions and completion streak updates remain successful.

**Parallel:** No. Progress and command completion share integration tests and final migration verification.

## Task 4: Run production-readiness gates

**Allowed scope:** Verification and narrowly attributable fixes only. Any newly discovered broad issue requires a plan amendment before implementation.

**Expected output:** Green backend lint/system/deploy/migration/tests, clean dependency audit, green architecture/API/documentation/artifact guards, and green frontend lint/dead-code/tests/build/audit.

During execution, this gate exposed two directly attributable supply-chain defects: the production Django pin had known advisories, and 28 frontend tarballs were locked to an environment-private package gateway that GitHub-hosted runners cannot use. The allowed scope therefore includes upgrading the compatible Django patch release, regenerating Python locks, normalizing those tarball URLs to the public npm registry, and moving official GitHub actions to their supported Node 24 majors.

The real PostgreSQL lane exposed three directly attributable portability defects that SQLite did not surface: an implicit 50-character variant slug column for authored case IDs up to 160 characters, `FOR UPDATE` applied across a nullable outer join, and data normalization plus `ALTER TABLE` in one transaction while foreign-key trigger events were pending. The allowed scope therefore also includes aligning persisted variant slugs to the existing case-ID bound with pre-bulk validation, locking only the owning adventure-run row, and making the three repair-before-constraint migrations non-atomic so their repairs commit before constraint installation.

**Verification:**

- `python scripts/check_quality_gates.py`
- `python scripts/check_django_deploy.py`
- `pip-audit -r backend/requirements.txt`
- `pytest -q --cov=. --cov-report=term-missing --cov-report=xml` from `backend/` against PostgreSQL 16 and Redis
- Clean PostgreSQL migration from zero with the integration settings
- Direct PostgreSQL inspection of installed checks, partial indexes, and persisted field bounds
- Django Redis cache set/get/delete round-trip
- `npm run lint`, `npm run lint:dead`, `npm test`, `npm run build`, and `npm audit --audit-level=high` from `frontend/`
- An isolated `npm ci` using only the committed frontend manifests, with no environment-private URLs in `package-lock.json`.
- `git diff --check` and final scoped worktree review

**Acceptance evidence:** Record exact pass/fail totals and identify any unavailable external integration as `implemented but unproven` rather than production-ready. For this execution, PostgreSQL 16.14 and Redis 8.8.0 were provisioned locally and the exact production-integration suite passed all 1,780 tests at 84% coverage.

**Parallel:** No. Final evidence runs after the schema and service cutovers.

## Non-goals

- Global Ruff reformatting of the existing backend.
- Frontend redesign or curriculum/content reauthoring.
- Replacing Django ORM, PostgreSQL, Redis, or the current service/selector structure.
- Renaming stable public API fields or changing gameplay scoring.
- Cleaning unrelated user-owned worktree changes.

## Risk if wrong

An incorrect data cutover could hide previously discoverable content. Over-tight command-step constraints could reject valid gameplay writes. A streak lock with an oversized transaction could add contention. Broad formatting or architecture churn in the dirty worktree could overwrite unrelated user work or make the production diff unauditable.
