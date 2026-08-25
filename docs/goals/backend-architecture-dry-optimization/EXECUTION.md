# Execution Contract and Task Board

## Contract restatement

- **Goal:** An optimal, clean backend model/module design with one owner per durable behavior and mechanically enforced DRY/architecture standards.
- **Plan path:** `docs/goals/backend-architecture-dry-optimization/PLAN.md`
- **Intent:** Remove dead/ambiguous model state, real runtime cycles, and meaningful duplicate implementations without changing public behavior.
- **Truth owner:** Models/migrations for persistence; relation metadata for variant construction; repository normalizer, shared workspace/run helpers, named curriculum selectors/services, wallet ledger, and architecture/format guards for their respective rules.
- **Contract boundary:** Stable HTTP/service behavior outside the internal canonical-name cutovers; row locks, status checks, transactions, and error messages remain intact.
- **Cutover:** Move callers first, delete old path second, prove focused behavior, then turn on blocking guards.
- **Displaced path:** `StudentProgress`; challenge relation aliases; private commit lookups; duplicated workspace/discard implementations; selector `core.py`; recursive terminal registry import; hard-coded practice app imports.
- **Acceptance evidence:** Zero maintained runtime cycles and targeted clones, forward migration proof, focused behavior proof, Ruff lint/format, clean PostgreSQL migration, Redis, and full PostgreSQL/Redis suite.
- **Kill criteria:** No fallback duplicate remains, no public API drift, no historical/generated rewrite, and no production/optimal claim without the final integration lane.
- **Forbidden moves:** Editing historical migrations or generated curriculum; abstracting trivial controller similarity; broad frontend/content changes; hiding an unavailable evidence lane; staging, committing, or resetting unrelated user changes.

## Ordered board

### Task A — Executable architecture baseline

- **Owner:** Main agent
- **Input:** Current import/clone audit and architecture guard
- **Files allowed:** Architecture guard/tests, `ARCHITECTURE.md`
- **Files forbidden:** Runtime behavior outside the plan
- **Output:** Runtime-cycle and displaced-path rules with accurate documentation
- **Evidence:** Failing-before/passing-after static audit
- **Depends on:** Approved PRE review
- **Parallel safe:** No

### Task B — Persistence and canonical model cutover

- **Owner:** Main agent
- **Input:** `StudentProgress` reference audit and challenge alias callers
- **Files allowed:** Progress/accounts/challenge/evaluation/profile files and focused tests
- **Files forbidden:** Historical migrations
- **Output:** New removal migration and canonical `selected_variant` callers
- **Evidence:** Reference audit, focused tests, migration proof
- **Depends on:** Task A baseline definition
- **Parallel safe:** No

### Task C — Shared behavior owners

- **Owner:** Main agent
- **Input:** Exact clone findings
- **Files allowed:** Normalizer callers, common workspace/run helpers, adventure/challenge callers/tests
- **Files forbidden:** Public API schemas
- **Output:** One implementation per repository lookup, workspace mutation, and started-run discard
- **Evidence:** Focused endpoint/service tests and clone audit
- **Depends on:** Task B canonical names
- **Parallel safe:** No

### Task D — Dependency cutover

- **Owner:** Main agent
- **Input:** Two runtime cycles and practice hard-coded imports
- **Files allowed:** Curriculum selectors/services/terminal registry, progress chest displacement, practice builder/tests
- **Files forbidden:** Authored/generated curriculum data
- **Output:** Zero maintained runtime cycles and metadata-owned variant discovery
- **Evidence:** Focused tests, import smoke, architecture guard
- **Depends on:** Task C
- **Parallel safe:** No

### Task E — Formatting and CI enforcement

- **Owner:** Main agent
- **Input:** Stable semantic diff and formatter baseline
- **Files allowed:** Ruff config, maintained Python, scripts, CI/meta-guard, docs
- **Files forbidden:** Historical migrations and generated curriculum
- **Output:** Green enforced lint/format scopes
- **Evidence:** Ruff and CI meta-guard outputs, scoped diff review
- **Depends on:** Tasks B–D
- **Parallel safe:** No

### Task F — Production-equivalent evidence and final reviews

- **Owner:** Main agent
- **Input:** Completed semantic and mechanical cutovers
- **Files allowed:** Evidence artifact and narrowly attributable fixes
- **Files forbidden:** Unplanned redesign
- **Output:** POST, correctness, maintainability, and verifier evidence
- **Evidence:** Quality gates, clean PostgreSQL migration, Redis, full integration suite, exact static counts
- **Depends on:** Tasks A–E
- **Parallel safe:** No
