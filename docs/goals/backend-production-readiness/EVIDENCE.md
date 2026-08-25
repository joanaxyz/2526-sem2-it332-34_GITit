# Backend Architecture and Production Readiness Evidence

Captured on 2026-07-20 from the repository worktree described by `PLAN.md`.

## Implemented contract

- Authoring visibility now has two persisted states: `private` and `public`.
- The forward authoring migration converts legacy `store` rows to `public` before the new database check is installed.
- Public discovery and launch authorization agree after that cutover.
- Ledger entries cannot have a zero amount.
- A streak's longest value cannot be below its current value, and streak mutation locks the player's row in an atomic transaction.
- Command-step attempts start at one, counted increments are binary, and the cumulative count includes the current increment.
- Existing run budget, star, system-slug, and exactly-one-runtime-target constraints have direct integrity coverage.
- Persisted adventure/challenge variant slugs are explicitly bounded to 160 characters, matching authored case IDs; bulk curriculum construction validates the persisted model contract before writing.
- Adventure start locks only the owning run row when nullable related rows are hydrated, which is valid on PostgreSQL and avoids `FOR UPDATE` on the nullable side of an outer join.
- Data-repair migrations commit their normalization before PostgreSQL installs the new checks, avoiding pending foreign-key trigger events on legacy upgrades.
- The production Django pin is 6.0.7 and both Python locks were regenerated.
- Frontend lockfile tarballs resolve through the public npm registry; 28 environment-private gateway URLs were removed.
- CI uses the supported Node 24 generations of the official checkout, setup-python, and setup-node actions.

## Acceptance evidence

| Gate | Result |
| --- | --- |
| Backend full suite (SQLite baseline) | `1779 passed in 2285.30s`; total coverage `84%` |
| Production integration suite | PostgreSQL 16.14 + Redis 8.8.0: `1780 passed, 95 warnings in 7542.00s`; total coverage `84%`; the later migration split changed sequencing only, not the exercised final schema contract |
| Clean PostgreSQL migration | Pass from zero through all committed migrations; `seed_curriculum` completed with 2,056 generated cases and migration drift reported `No changes detected` |
| Post-review migration sequencing | Current graph reapplied from zero on PostgreSQL 16.14; all 9 focused legacy-upgrade, slug-boundary, and nullable-join lock regressions passed in `255.08s` |
| PostgreSQL schema inspection | Pass: 14 named domain checks, partial system-content unique index, and both persisted variant slug columns at `varchar(160)` |
| Redis integration | Pass: Django cache set/get/delete round-trip against the configured Redis backend |
| Focused migration and integrity coverage | Included in the green full suite; migration modules present during that run report `100%` statement coverage, and the later `progress.0004` step is exercised by the green post-review PostgreSQL run |
| Backend Ruff | Pass |
| Repository script Ruff | Pass using the exact CI invocation |
| Django system check | Pass, zero issues |
| Migration drift | Pass, `No changes detected` |
| Production deploy configuration | PostgreSQL production configuration valid; Django deploy check reports zero issues |
| Fast architecture/contract guards | Pass, including 2,056 generated curriculum cases, API contract, API type adoption, documentation, CI manifest, and tracked-artifact guard |
| Python production dependency audit | Pass, no known vulnerabilities |
| Python development dependency audit | Pass, no known vulnerabilities |
| Frontend clean install | Pass in an isolated directory, 348 packages installed from the committed manifests |
| Frontend lint and dead-code scan | Pass |
| Frontend tests | 57 files and 414 tests passed |
| Frontend production build | Pass, 2,639 modules transformed |
| Frontend dependency audit | Pass, zero vulnerabilities |
| Generated target replay | Pass, 2,056 solutions current |
| Diff hygiene | `git diff --check` pass; no private package-gateway URL or active `VISIBILITY_STORE` path remains |

The existing local database was inspected without mutation before the migrations were written. It had no duplicate system slugs, invalid published runtime targets, invalid adventure/challenge command budgets, or star values above three.

## Review gates

### POST alignment review

- Intent and target perspective are preserved: legacy store-visible content remains discoverable and launchable as public content.
- Django models plus committed migrations remain the only persisted-schema truth owner.
- Services own mutation and locking; selectors own reads; no duplicate compatibility path remains.
- The displaced store-visibility path is removed from active runtime code.
- The supply-chain fixes are narrow consequences of the production gates and are recorded in the amended plan.

### Correctness review

- Data normalization runs before each new constraint that has a safe canonical repair.
- PostgreSQL-sensitive repair migrations are non-atomic so normalization commits before `ALTER TABLE`; the progress checks are split across consecutive migrations so a later constraint failure cannot leave an earlier unrecorded constraint behind.
- Migration tests exercise the immediate prior schema state and the current runtime contract.
- Direct ORM writes prove the database, rather than serializer-only validation, rejects impossible values.
- Bulk variant construction now validates field lengths before `bulk_create`, keeping SQLite and PostgreSQL behavior aligned.
- Adventure transitions use `select_for_update(of=("self",))`, preserving row serialization without attempting to lock nullable joined tables.
- Recompilation remains compatible with the exactly-one-target constraint because the old runtime is removed before replacement.
- The locked Rolldown native binary that could not be overwritten while user-owned Vite servers were active matched the clean-install binary byte-for-byte; the ignored workspace dependency tree was restored and all frontend gates reran successfully.

### Maintainability review

- No new service layer, selector layer, compatibility alias, or duplicate source of truth was introduced.
- Constraint names are explicit and stable.
- The 160-character variant slug contract reuses the existing authored `case_id` bound rather than introducing a second naming limit.
- Forward migrations preserve historical data where semantics are unambiguous and use no-op reversals rather than pretending a lossy cutover is reversible.
- Unrelated dirty worktree changes were preserved.

## Production integration proof

A disposable loopback-only PostgreSQL 16.14 server and Redis 8.8.0 server were provisioned from hash-verified portable distributions. The PostgreSQL database was migrated from zero, seeded, inspected directly for installed constraints and column bounds, and exercised by the exact CI coverage command. Django also completed a real Redis cache round-trip. The services shut down cleanly and their workspace data was removed after evidence capture.

The full PostgreSQL run exposed and verified fixes for three portability defects that SQLite did not reveal: an implicit 50-character slug column, a nullable outer join under `FOR UPDATE`, and atomic data-repair migrations with pending foreign-key trigger events. The final production integration suite passed all 1,780 tests. The 95 warnings were the expected absent local `staticfiles/` directory and sandbox-denied pytest cache writes; the separate production deploy guard passed with zero Django system-check issues.
