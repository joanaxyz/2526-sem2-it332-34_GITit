# Backend Architecture and DRY Optimization Plan

**Intent:** Optimize the existing Django backend around explicit truth owners, remove dead or ambiguous model contracts, eliminate real dependency cycles and repeated behavioral implementations, and make cleanliness mechanically enforceable.
**Current Behavior:** The production-readiness suite is green on PostgreSQL and Redis, but the architecture audit still finds two runtime module cycles, one write-only `StudentProgress` model whose only domain field is never used, compatibility aliases on `ChallengeRun` that duplicate its persisted field names, two copies of repository commit lookup, two four-method workspace adapters, two copies of active-run deletion, and a compatibility selector module that adds an unnecessary import layer. `ARCHITECTURE.md` says cross-app coupling is guarded even though the guard does not inspect backend imports. Ruff lint is enforced, but `ruff format --check` currently reports 194 unformatted Python files because formatting scope is not defined or enforced.
**Expected Outcome:** Maintained backend runtime modules form an acyclic import graph; `StudentProgress` and its registration write are removed through a forward migration; challenge runtime code uses the canonical `selected_variant` relation; repository lookup, workspace mutation, and active-run discard each have one implementation owner; public selector APIs remain stable without a redundant `core.py`; practice variant construction derives the related variant model from Django metadata instead of importing both gameplay apps; maintained Python formatting is green and enforced; and the architecture guide matches the executable guard.
**Target-Perspective Output:** A maintainer can identify where every touched rule lives, inspect an acyclic runtime graph, run one quality command that rejects architecture regressions and unformatted maintained code, migrate an existing PostgreSQL database without data ambiguity, and execute the full production integration suite without behavioral regressions.
**Truth Owner:** Django models and forward migrations own durable shape; concrete relation metadata owns a level's variant type; `RepositoryStateNormalizer` owns commit lookup; `common.services.run_workspace` owns workspace mutation; a common run-state helper owns transactional deletion of started runs; named curriculum selector modules own read logic while `curriculum.selectors.__init__` owns only the public export surface; `curriculum.services.chests` owns chapter-progress reward orchestration while `progress.wallet` remains the currency ledger owner; the architecture guard owns runtime dependency and duplicate-path invariants.
**Contract Boundary:** Public HTTP payloads and service results remain stable, while internal callers use canonical model field names. Shared helpers accept Django model instances and preserve locking, status, error-message, and transaction semantics. Import analysis covers maintained runtime Python and excludes migrations, tests, generated/seed data, management commands, and package metadata that are not deployed request paths.
**Cutover:** Remove `StudentProgress` with a new `progress` migration after deleting the registration write. Replace all internal `ChallengeRun.variant`/`variant_id` uses with `selected_variant`/`selected_variant_id` before deleting aliases. Move callers to shared workspace/discard owners before deleting domain wrappers. Replace selector and terminal registry compatibility imports while preserving their package-level public names. Add architecture and format gates only after the tree satisfies them.
**Displaced Path:** No `StudentProgress` table/model/write, `ChallengeRun` relation aliases, private `_commit_by_id` copies, domain workspace-file service copies, duplicated discard bodies, `curriculum.selectors.core`, package-recursive terminal renderer import, or hard-coded practice imports remain as fallback paths.
**Value Density:** The slice removes persistence with no reader, collapses repeated high-risk transactional behavior, makes the dependency direction testable, and prevents the exact cleanliness defects found by the audit without redesigning public APIs or gameplay.
**Acceptance Evidence:** A migration test or migration executor evidence proves the existing schema advances through the model removal; focused account, challenge, adventure, workspace, simulator, evaluation, curriculum, and architecture tests pass; an AST audit reports zero maintained runtime cycles and zero identified exact behavioral clones; Ruff lint and scoped format checks pass; migration drift is empty; a clean PostgreSQL migration and full PostgreSQL/Redis suite pass; final diff and worktree-scope reviews show no unrelated edits.
**Evidence Lane:** Static ownership/import/clone audits, focused unit and migration tests, architecture and CI meta-guards, Ruff lint/format, Django checks and migration drift, clean PostgreSQL migration, full PostgreSQL/Redis suite with coverage, then final scoped diff review.
**Kill Criteria:** Zero dead model references, zero canonical-field aliases, zero identified exact behavioral clones, zero maintained runtime import cycles, no historical migration rewrite, no generated curriculum hand-edit, no public API contract change, no broad formatting churn outside the documented maintained-code scope, and no optimal/production claim without PostgreSQL/Redis evidence.
**Non-goals:** Frontend redesign; curriculum content reauthoring; replacing Django, PostgreSQL, Redis, the service/selector architecture, or stable API fields; abstracting trivial controller similarities without a shared rule; formatting historical migrations, generated targets, or unrelated user-owned files.
**Risk if wrong:** A relation or service cutover could break command evaluation, a shared transactional helper could weaken row-lock semantics, model deletion could strand an unknown reader, an over-broad cycle/duplicate rule could block legitimate boundaries, and bulk formatting could bury meaningful changes in a dirty worktree.

## Architecture Map

### Files to create

- `backend/progress/migrations/0005_remove_studentprogress.py` for the forward schema cutover.
- Focused architecture-guard tests under `scripts/checks/tests/` only if the existing script-test layout supports them; otherwise keep self-tests in the guard module and exercise it through the quality gate.
- This goal package and final evidence record under `docs/goals/backend-architecture-dry-optimization/`.

### Files to modify

- `backend/accounts/services/core.py`, `backend/progress/models.py`, and focused account/model tests.
- `backend/challenges/models.py`, challenge payload/services, `backend/evaluation/completion.py`, the profiling script, and focused challenge/evaluation tests.
- `backend/simulator/services/core.py`, `backend/evaluation/services/state_helpers.py`, and focused simulator/evaluation tests.
- `backend/common/services/run_workspace.py`, adventure/challenge views and service exports, run services, and their focused tests.
- `backend/practice/services/builders.py` and variant-builder tests.
- `backend/curriculum/selectors/__init__.py`, `command_skills.py`, new `curriculum/services/chests.py`, curriculum service exports and serializers, the displaced `progress/chests.py`, terminal renderer registry, and focused curriculum/progress tests.
- `scripts/checks/check_architecture_boundaries.py`, `scripts/checks/check_ci_quality_gates.py`, `.github/workflows/ci.yml`, `backend/ruff.toml`, and `ARCHITECTURE.md`.
- Maintained backend Python files selected by the agreed Ruff scope, using mechanical formatting only after semantic changes are stable.

### Files to avoid

- Historical migrations except the new forward migration.
- `backend/curriculum/seed_data/generated/` and human-authored curriculum ledgers unless a focused behavioral test proves a required edit.
- Unrelated frontend assets, dogfood output, reference captures, caches, and pre-existing user changes.

### Read path

Models -> named selectors -> payload/view. Curriculum progress counts remain curriculum-owned; wallet writes remain progress-owned. Public package imports remain stable while compatibility implementation layers disappear.

### Write path

Account registration -> Player/Streak/Wallet only; gameplay view -> shared workspace/run primitive -> locked concrete run row; challenge command processing -> canonical selected variant -> evaluation; ORM -> database constraints and migrations.

### Integration and cutover gate

Each displaced path is removed only after its callers use the target owner. The module-cycle guard becomes blocking only after both existing cycles are eliminated. Format becomes blocking only after an explicit exclusion policy protects historical/generated files and the selected maintained scope is green.

## Task 1: Establish reproducible architecture and duplication baselines

**Exact scope:** `scripts/checks/check_architecture_boundaries.py`, its nearest tests/fixtures, `ARCHITECTURE.md`, and read-only AST audit commands.
**Output:** A deterministic maintained-runtime import graph definition; evidence for the two current cycles; a meaningful duplicate-function definition that ignores trivial wrappers/generated/history; and corrected documentation language.
**Verification:** Run the guard against a failing fixture or current pre-cutover graph, then against the final graph; repeat the normalized AST clone scan.
**Acceptance evidence:** The guard detects a deliberately represented cycle and the final repository reports zero cycles; clone output has no duplicate implementation for the targeted rules.
**Parallel:** No. This defines the contract for all later cleanup.

## Task 2: Remove dead persistence and ambiguous challenge model aliases

**Exact scope:** Progress model/migration, account registration, `ChallengeRun`, its internal callers, and focused tests.
**Output:** `StudentProgress` is deleted by a committed forward migration; signup no longer creates it; all challenge code uses `selected_variant`; unused `challenge`, `trial`, `variant`, and `variant_id` aliases are removed.
**Verification:** `rg` proves no live references; account registration tests; challenge payload/run/command tests; migration drift; migration executor or clean PostgreSQL apply.
**Acceptance evidence:** Registration still creates all state actually read by the product, challenge API payloads remain unchanged, and the old table is absent after migration.
**Parallel:** No. Model and caller cutovers are atomic review units.

## Task 3: Consolidate behavioral truth owners

**Exact scope:** Repository normalizer users, shared workspace service, adventure/challenge workspace callers and exports, shared run-state helper, adventure/challenge discard callers, and focused tests.
**Output:** Commit lookup delegates to `RepositoryStateNormalizer`; one configurable workspace service owns four file mutations; one helper owns lock/status/delete semantics; domain-specific duplicate files/bodies are removed.
**Verification:** Simulator/evaluation tests; adventure/challenge workspace endpoint tests; concurrent/ended-run behavior tests; AST clone audit.
**Acceptance evidence:** Locking and domain error messages remain exact, all endpoint responses remain stable, and no old wrapper is importable or referenced.
**Parallel:** No. Shared primitives are introduced before duplicate owners are deleted.

## Task 4: Eliminate runtime import cycles and hard-coded cross-app construction

**Exact scope:** Curriculum selector exports and command-skill fallback, chapter chest orchestration boundary, terminal renderer registry, and practice variant builder.
**Output:** `curriculum.selectors.core` is removed; command-skill fallback performs its curriculum-owned query without importing adventure services; chapter chest schedule/count/orchestration moves to `curriculum.services.chests` and calls only the progress-owned wallet ledger; terminal registry imports leaf renderers directly; practice derives variant model/parent relation from Django metadata.
**Verification:** Focused curriculum/progress/practice tests; seed structural guard; architecture import-cycle guard; import smoke tests for public selector and terminal packages.
**Acceptance evidence:** Public imports are unchanged, authored variants are identical, chest awards are unchanged and idempotent, and maintained runtime cycle count is zero.
**Parallel:** No. The dependency graph must be re-measured after each ownership cutover.

## Task 5: Define and enforce maintained-code formatting

**Exact scope:** `backend/ruff.toml`, maintained backend Python selected by that policy, repository Python under `scripts/`, CI workflow, CI meta-guard, and architecture documentation.
**Output:** Ruff excludes immutable historical migrations and curriculum data ledgers from backend formatting; selected maintained runtime/tests and repository scripts are mechanically formatted; CI runs lint and format checks for both scopes and the meta-guard requires them. Data ledgers remain linted and covered by structural/seed/replay guards.
**Verification:** `ruff check .` and `ruff format --check .` from `backend`; `ruff check --config backend/ruff.toml scripts` and `ruff format --check --config backend/ruff.toml scripts` from the repository root; CI meta-guard; `git diff --check`; and a scoped diff review separating semantic from mechanical changes.
**Acceptance evidence:** Both Ruff checks are green with no historical migration or curriculum-data rewrite and CI cannot silently drop the format gate.
**Parallel:** No. Format only after semantic diffs stabilize.

## Task 6: Prove the optimized backend on production-equivalent infrastructure

**Exact scope:** Verification plus narrowly attributable fixes within this plan. Any broader redesign requires a documented amendment and another PRE review.
**Output:** Green architecture, quality, deployment, dependency, migration, and backend integration lanes; final evidence record with exact versions/counts.
**Verification:** `python scripts/check_quality_gates.py`; Django deploy check; dependency audit; migration drift; clean PostgreSQL 16 migration; Redis round trip; focused suites; full PostgreSQL/Redis pytest with coverage; final import/clone/reference audits; `git diff --check` and scoped status review.
**Acceptance evidence:** Exact pass totals, coverage, database/cache versions, cycle count, duplicate count, and migration result are recorded. Any unavailable lane is labeled unproven and blocks completion.
**Parallel:** No. This is the terminal evidence gate.
