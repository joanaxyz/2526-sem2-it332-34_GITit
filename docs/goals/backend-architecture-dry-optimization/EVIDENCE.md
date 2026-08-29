# Backend Architecture and DRY Optimization Evidence

## Outcome

The backend now has explicit owners for the persistence and runtime behaviors in this goal. Dead progress persistence and ambiguous challenge-run aliases are removed, repeated transactional/runtime implementations are consolidated, maintained runtime imports are acyclic, maintained Python formatting is enforced, and the production dependency set has no known vulnerabilities.

The terminal single-worker PostgreSQL/Redis integration lane is green. All planned acceptance lanes are complete.

## POST Alignment Review

- **Intent:** Aligned. The implementation removes dead or ambiguous state and consolidates behavioral owners without changing HTTP contracts.
- **Truth owners:** Aligned. Migrations own durable shape; `RepositoryStateNormalizer` owns repository lookup; common run helpers own workspace mutation and active-run deletion; curriculum owns chapter reward policy; the wallet remains the currency ledger.
- **Contract boundary:** Aligned. Focused API and service tests preserve payloads, messages, row locking, status checks, and transaction behavior.
- **Cutover:** Aligned. Every old caller was moved before its model alias, service module, selector layer, or chest module was deleted.
- **Displaced paths:** Aligned. The live-reference audit reports zero matches and the architecture guard prevents deleted module paths from returning.
- **Kill criteria:** Aligned. Historical migrations and curriculum data ledgers were not reformatted or hand-edited, public API contracts remain current, and no fallback implementation remains.
- **Scope variance:** The exact clone audit exposed additional copies of scalar-list coercion, head lookup, and operation metadata. These were removed because they were directly within the approved single-owner/DRY intent. No broader redesign was introduced.

## Persistence and Migration Evidence

- Added `progress.0005_remove_studentprogress`; no historical migration was rewritten.
- Clean PostgreSQL 16.14 migration from zero completed through `progress.0005`.
- Upgrade-path proof migrated an existing schema back to `progress.0004`, inserted a legacy `StudentProgress` row, migrated forward, and confirmed `to_regclass('public.progress_studentprogress')` returned `NULL`.
- The committed migration test creates legacy streak, zero-value ledger, and student-progress rows; it proves normalization migrations run and the dead table is absent at the latest state.
- `python manage.py makemigrations --check --dry-run` reported `No changes detected`.
- A focused PostgreSQL migration test followed by a transactional streak test passed (`2 passed`), proving the migration test restores the latest schema and Django teardown can flush it.

## Architecture and DRY Evidence

- Maintained runtime modules analyzed: **208**.
- Maintained runtime import edges analyzed: **419**.
- Strongly connected runtime components: **0**.
- Live displaced-reference matches outside tests, migrations, seed data, and goal history: **0**.
- Exact normalized nontrivial production clone groups: **0**.
- The architecture guard's synthetic SCC test passes and the real guard reports `Architecture boundaries look clean.`
- Generated curriculum replay collected **2,056** variant solutions and reported the committed target file current.

## Focused Correctness Evidence

- Initial model-focused lane: `15 passed`.
- Combined account/challenge/adventure/workspace/evaluation/curriculum lane: `75 passed` after correcting the preserved list-shaped chest schedule contract.
- Common/evaluation/simulator/practice lane: `38 passed`.
- Django system check: zero issues.
- Django deployment check with production PostgreSQL settings: zero issues.
- Redis 8.8.0 loopback round trip through Django cache: set/get/delete succeeded.
- Clean curriculum seed on PostgreSQL: **2,056** cases, structurally consistent.
- API contract and fast repository quality gates: current and green.

## Quality and Supply-Chain Evidence

- Backend: `ruff check .` and `ruff format --check .` pass.
- Ruff lint covers migrations and curriculum ledgers; only formatting excludes those immutable/data-heavy paths. The format check reports **319** maintained backend files formatted.
- Repository scripts: Ruff lint and format checks pass with `backend/ruff.toml`.
- The script format check reports **64** files formatted.
- `git diff --check` passes; only Git line-ending notices were emitted.
- Production requirements: `pip-audit` reports no known vulnerabilities.
- Development/CI requirements: `pip-audit` reports no known vulnerabilities.
- Installed environment: `pip check` reports no broken requirements.

## Integration Evidence

- A six-worker PostgreSQL/Redis run executed all **1,786** test bodies successfully. Its sole error occurred during teardown because the existing migration test still targeted `progress.0004`; the test left the intentionally deleted historical table present, so PostgreSQL correctly rejected a later flush through its foreign key. The test now targets `progress.0005` and the focused teardown reproduction passes.
- Terminal exact single-worker PostgreSQL/Redis suite: **1,786 passed**, **116 warnings**, **84% coverage**, in **4,457.96 seconds (1:14:17)** on Python 3.13.7.
- The warnings are test-environment notices: a missing collected-static output directory, an undersized dummy JWT key used by the completed local command, and a sandbox-denied pytest cache path. The committed CI dummy keys are now at least 32 bytes, and the production deploy check has no warnings or issues.

## Correctness Review

No blocking correctness finding remains in the completed lanes. The shared workspace service locks and reloads the concrete persisted run before mutation, preserves domain-specific ended messages, writes only normalized repository state, and returns the locked instance. Adventure responses now explicitly copy that returned state into their separately hydrated payload object, eliminating a stale-response path. Shared discard logic preserves atomic locking and started-only deletion. Challenge evaluation receives the canonical variant explicitly and no longer relies on compatibility aliases or an unused previous state.

## Maintainability Review

No blocking maintainability finding remains. The change reduces truth owners and deleted files rather than adding compatibility layers. Package initializers remain export-only, the cycle/displaced-path rules are executable, CI now enforces the chosen format scope, and exact behavioral-clone scanning is clean. Some modules are necessarily substantial because they contain authored education data or command-family verification logic; size alone was not treated as duplication, and no speculative abstraction was introduced without a shared invariant.

## Target-Perspective Verification

A maintainer can now locate each touched rule at one owner, run the repository quality command to reject architecture or formatting regressions, migrate an existing PostgreSQL database without retaining dead state, replay all authored curriculum targets, and audit both production and development dependencies. Target-perspective acceptance passes with the terminal production-equivalent integration lane complete.
