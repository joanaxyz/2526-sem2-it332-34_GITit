# Architecture Guard Policy Modularization — Slice 13 Implementation Plan

**Intent:** Turn the architecture checker into a stable CLI orchestrator backed by focused, one-way policy and source-analysis modules.

**Current Behavior:** `scripts/checks/check_architecture_boundaries.py` is 5,367 lines with 109 top-level functions. It mixes repository traversal, Python import analysis, TypeScript parsing, Content Editor/Home/AdminConsole workflow rules, Catalog/Auth/Stats/Dashboard/Gameplay contract policies, generic repository shape checks, aggregation, and CLI rendering. Its 1,877-line algorithm test loads the entire executable with `runpy` and reaches every helper through a string-keyed dictionary. The checker has demonstrably accreted from 1,704 lines before the Stats contract slice to 2,201 after it and 4,527 before the Shop slice. Every later ownership slice currently adds more unrelated policy code and tests to these same two files.

**Expected Outcome:** The executable retains the exact public command and output/exit contract but becomes a sub-2,000-line orchestrator for its remaining workflow/general rules. A small repository utility module owns path traversal, focused Python and TypeScript analysis modules own pure reusable parsing helpers, and Catalog, Auth, Progress, and Gameplay modules own their constants, analyzers, filesystem adapters, and ordered violation lists. Contract mutation tests move to four focused modules and import their canonical owners directly; the remaining algorithm test no longer uses `runpy`. There is one definition of every moved function or constant and no compatibility re-export from the executable. Clean execution still writes the logical line `Architecture boundaries look clean.\n` to stdout, writes no stderr, and exits 0; the captured Windows stream is byte-equivalent before and after cutover, including its `\r\n` translation.

**Target-Perspective Output:** CI, local quality gates, and contributors run the same commands and receive byte-equivalent success/failure rendering. A maintainer changing one contract policy opens a focused module and focused mutation test instead of a 5.3k-line cross-domain file. Adding the next gameplay response policy does not enlarge the CLI orchestrator.

**Truth Owner:** `scripts/checks/architecture_guard/repository.py` owns repository roots and deterministic file discovery; `python_analysis.py` and `typescript_analysis.py` own reusable pure source analysis; `contracts/catalog.py`, `auth.py`, `progress.py`, and `gameplay.py` own their respective contract constants and violation functions; `scripts/checks/check_architecture_boundaries.py` owns only CLI composition, remaining workflow/general rules, ordering, and rendering. Focused test modules own each policy's mutation corpus.

**Contract Boundary:** Existing wrapper/CI/local command -> `check_architecture_boundaries.main()` -> remaining local checks plus imported domain `check_*` functions in the existing order -> deterministic ordered `list[str]` -> unchanged stdout/stderr and exit status.

**Cutover:** First capture the approved dirty-worktree and pre-cutover policy outputs. Add the package skeleton and pure analysis owners; move contract constants/functions by domain with no semantic edits; point the executable at the canonical modules; move each policy's tests to a focused module and replace `runpy` access with direct imports; delete moved definitions from the executable; then update architecture documentation and replay exact-output, command, focused/full gate, and preservation evidence.

**Displaced Path:** Catalog/Auth/Progress/Gameplay constants and implementations in `check_architecture_boundaries.py`, and all contract-policy access through the test file's `_guard_namespace()`/`runpy` dictionary, are deleted. No facade, wildcard export, duplicate definition, or reverse import remains.

**Value Density:** This slice removes roughly 3,700 lines from the checker and roughly 1,300 lines from its test mirror, establishes one-way policy ownership before another contract family is added, and preserves production and generated files byte-for-byte. It reduces the review surface and collision risk of every later architecture slice without changing product behavior.

**Acceptance Evidence:** Pre/post golden ordered violation arrays for representative multi-failure Catalog/Auth/Progress/Gameplay mutation cases; pre/post AST and resolved-value fingerprints for every moved function/constant; a normalized AST inventory proving every existing test function and assertion survives only the declared namespace-to-direct-import rewrite; direct and compatibility-wrapper subprocess traces from their real working directories; byte-exact clean stdout/stderr/exit capture; a controlled in-memory failure harness with byte-exact pre/post stderr and automatic monkeypatch restoration; focused policy tests; Ruff; both checker entrypoints; CI manifest and fast quality gates; documentation guard; exact static searches for duplicate definitions/re-exports/reverse imports/proxies; line/function-count checks; protected production/generated hashes; full dirty-manifest replay; and POST/correctness/maintainability/final reviews.

**Evidence Lane:** PRE approval -> preservation and golden-output capture -> source-analysis extraction -> domain policy cutover -> focused test cutover -> differential/CLI verification -> architecture and quality gates -> preservation replay -> POST/correctness/maintainability/final verification.

**Kill Criteria:** The executable is below 2,000 lines; each new policy or analysis module is below 900 lines; no Catalog/Auth/Progress/Gameplay contract literal or implementation remains in the executable; no extracted module imports the executable; every moved symbol has exactly one canonical definition with the pre-cutover function-AST or resolved-constant fingerprint; the four policy test corpora import canonical modules and no architecture-guard test uses `runpy`, `_guard_namespace`, `namespace[...]`, `vars(module)`, a compatibility dictionary, or an import proxy; every pre-existing test function and assertion has the same normalized fingerprint after only declared direct-symbol rewrites; `main()` retains the five calls `check_stats_summary_contract_ownership`, `check_dashboard_summary_contract_ownership`, `check_auth_contract_ownership`, `check_catalog_contract_ownership`, and `check_gameplay_mutation_contract_ownership` in the current relative order; violation text/order and success/failure stdout/stderr/exit status are unchanged; clean stdout is the logical line `Architecture boundaries look clean.\n` and matches the pre-cutover platform bytes; both public commands and CI wiring remain unchanged; all existing architecture guard tests pass; no backend/frontend/generated product file changes; and no unrelated dirty byte changes.

**Architecture Slice:** Architecture-guard policy modularization only. New policy rules, gameplay success-response exactness, product architecture changes, lint-rule redesign, parser replacement, policy-message cleanup, concurrency, caching, and CI command changes are explicitly deferred.

**Plan Review Gate:** Requires PRE review before preservation capture or implementation.

## Outcome Contract

### Package topology and import direction

```text
scripts/checks/check_architecture_boundaries.py
  -> architecture_guard.repository
  -> architecture_guard.python_analysis
  -> architecture_guard.typescript_analysis
  -> architecture_guard.contracts.catalog
  -> architecture_guard.contracts.auth
  -> architecture_guard.contracts.progress
  -> architecture_guard.contracts.gameplay

contracts/* -> repository + analysis modules only
analysis modules -> Python standard library only
repository -> Python standard library only
```

- `architecture_guard/__init__.py` and `contracts/__init__.py` are package markers with no re-exports.
- Before importing package modules, the executable computes the bootstrap-only `_REPOSITORY_IMPORT_ROOT = Path(__file__).resolve().parents[2]` and, when absent, inserts `str(_REPOSITORY_IMPORT_ROOT)` into `sys.path`. This same bootstrap runs for direct execution and `runpy` wrapper execution, after which imports use only canonical `scripts.checks.architecture_guard...` paths and canonical `ROOT` is imported from `repository.py`. The private bootstrap name may then be deleted; it is not a second repository-root owner.
- Each affected backend architecture-guard test module computes the repository root from `__file__` and inserts it into `sys.path` before direct canonical imports. This is a narrowly scoped test bootstrap, not a proxy, dictionary, dynamic loader, or production package mutation, and it supports pytest's actual `backend` working directory.
- Extracted modules never import the executable or another domain policy module.
- Analyzer functions keep their current input/output signatures wherever possible and remain deterministic pure functions.
- Filesystem-facing `check_*` adapters retain the existing read set and append order.

### Policy ownership

| Owner | Existing responsibility moved intact |
|---|---|
| `repository.py` | `ROOT`, `FRONTEND_SRC`, `BACKEND`, suffix sets, `rel`, deterministic `iter_files` |
| `python_analysis.py` | generic class/assignment/decorator/call inspection and canonical Python-call helpers |
| `typescript_analysis.py` | module parsing, type/interface/object parsing, import/re-export resolution, alias taint/access tracing, static string resolution |
| `contracts/catalog.py` | catalog constants, backend/frontend shadow detection, source/OpenAPI/runtime ownership checks |
| `contracts/auth.py` | auth constants, serializer/view/frontend shadow detection, source/OpenAPI/runtime ownership checks |
| `contracts/progress.py` | Stats and Dashboard constants, secondary owner detection, source/OpenAPI/runtime ownership checks; exports the two existing canonical `check_stats_summary_contract_ownership` and `check_dashboard_summary_contract_ownership` functions separately |
| `contracts/gameplay.py` | mutation-request constants, backend/frontend/OpenAPI ownership checks |
| executable | AdminConsole, Content Editor, Home, import-cycle, generic shape/size/displaced-path rules, aggregate order, rendering, exit status |

The TypeScript analysis module may also absorb the pre-existing generic module helpers currently used by Content Editor/Home checks so there is one parser owner rather than a second local copy. CSS-specific and feature-specific workflow analyzers remain in the executable.

### Stable external behavior

- `python scripts/checks/check_architecture_boundaries.py` remains supported.
- `python scripts/check_architecture_boundaries.py` remains the compatibility command.
- `.github/workflows/ci.yml`, `scripts/checks/check_quality_gates.py`, and `scripts/checks/check_ci_quality_gates.py` retain their current invocation strings.
- Clean output remains the logical line `Architecture boundaries look clean.\n` on stdout, with empty stderr and exit code 0; the Windows baseline records `Architecture boundaries look clean.\r\n`, and post-cutover output must match those captured bytes exactly.
- Failure rows remain ordered exactly as today, followed by the same rules summary on stderr with exit code 1.
- All checks stay read-only; no cache or generated output is introduced.
- Verification executes the direct checker from the repository root, the preserved compatibility wrapper from `frontend` (matching CI's working directory), and focused pytest from `backend` so import behavior is proven in every real context.
- `main()` continues to call Stats, Dashboard, Auth, Catalog, and Gameplay as five separately imported checks in their current relative order; `progress.py` does not add an aggregate wrapper.

## Architecture Map

### Files to create

- `scripts/checks/architecture_guard/__init__.py`
- `scripts/checks/architecture_guard/repository.py`
- `scripts/checks/architecture_guard/python_analysis.py`
- `scripts/checks/architecture_guard/typescript_analysis.py`
- `scripts/checks/architecture_guard/contracts/__init__.py`
- `scripts/checks/architecture_guard/contracts/catalog.py`
- `scripts/checks/architecture_guard/contracts/auth.py`
- `scripts/checks/architecture_guard/contracts/progress.py`
- `scripts/checks/architecture_guard/contracts/gameplay.py`
- `backend/common/tests/architecture_guard/__init__.py`
- `backend/common/tests/architecture_guard/test_catalog_policy.py`
- `backend/common/tests/architecture_guard/test_auth_policy.py`
- `backend/common/tests/architecture_guard/test_progress_policy.py`
- `backend/common/tests/architecture_guard/test_gameplay_policy.py`
- `backend/common/tests/architecture_guard/test_policy_equivalence.py`
- `backend/common/tests/architecture_guard/policy_equivalence_cases.py`
- `docs/goals/architecture-guard-policy-modularization/PRE_CUTOVER_SYMBOL_MANIFEST.json`
- `docs/goals/architecture-guard-policy-modularization/PRE_CUTOVER_TEST_MANIFEST.json`
- `docs/goals/architecture-guard-policy-modularization/PRE_SLICE_BASELINE.md`
- `docs/goals/architecture-guard-policy-modularization/EVIDENCE.md`

### Files to modify

- `scripts/checks/check_architecture_boundaries.py`
- `backend/common/tests/test_architecture_guard_algorithms.py`
- `ARCHITECTURE.md`
- `scripts/README.md`

### Files to preserve exactly

- `scripts/check_architecture_boundaries.py`
- `scripts/checks/check_quality_gates.py`
- `scripts/checks/check_ci_quality_gates.py`
- `.github/workflows/ci.yml`
- all backend and frontend production/runtime files
- generated OpenAPI and TypeScript artifacts
- migrations, data, assets, lockfiles, build configuration, and prior goal artifacts
- every unrelated dirty or untracked path present at baseline capture

### Precise mutable-path allowlist after baseline capture

- Existing files allowed to change: `scripts/checks/check_architecture_boundaries.py`, `backend/common/tests/test_architecture_guard_algorithms.py`, `ARCHITECTURE.md`, and `scripts/README.md`.
- Approved absent-to-created implementation/test paths: the `scripts/checks/architecture_guard/` package and the listed `backend/common/tests/architecture_guard/` package files only.
- Approved evidence output: new `docs/goals/architecture-guard-policy-modularization/EVIDENCE.md` only.
- `GOAL.md`, `PLAN.md`, `PRE_SLICE_BASELINE.md`, both pre-cutover JSON manifests, public wrappers/wiring, and every path outside this exact list become strict status/bytes/SHA-256 preservation entries at capture. The baseline file records its own content hash externally in the evidence replay rather than self-hashing.

## Task Board

### Task 1: Capture approved preservation and behavior baselines

- **Owner:** Main agent.
- **Files allowed:** New `PRE_SLICE_BASELINE.md`, `PRE_CUTOVER_SYMBOL_MANIFEST.json`, `PRE_CUTOVER_TEST_MANIFEST.json`, `policy_equivalence_cases.py`, and `test_policy_equivalence.py` only.
- **Output:** Complete dirty manifest with status/bytes/SHA-256; exact hashes for both already-dirty implementation targets; absence records for additions; protected hashes for public command wiring and every backend/frontend/generated path; current line/function counts; byte-separated stdout/stderr/exit capture from the clean direct and wrapper commands; golden complete ordered arrays from representative multi-violation cases for all four domains; a manifest of every moved symbol with owner, normalized function-AST SHA-256 or stable recursively normalized resolved-value SHA-256; and every existing test function with assertion count plus a normalized AST SHA-256.
- **Verification:** Re-run the current checker tests and both entrypoints before production edits. The symbol inventory covers every extracted definition, not a sample. Test normalization removes `_guard_namespace()` setup assignments and rewrites only `namespace["symbol"]` subscripts to direct `Name("symbol")` nodes before hashing; all other function AST and every `assert` node remain significant. The baseline distinguishes the exact mutable allowlist from strict preservation entries.
- **Depends on:** PRE approval.

### Task 2: Establish reusable repository and source-analysis owners

- **Owner:** Main agent.
- **Files allowed:** New package/repository/analysis modules, executable import cutover, and algorithm/equivalence tests.
- **Output:** One repository traversal owner, one Python analysis owner, one TypeScript analysis owner, direct canonical imports, no reverse edge, no duplicate helper definition.
- **Verification:** Direct helper tests, AST/static definition census, Ruff, pre/post golden arrays, complete symbol fingerprint replay, and checker entrypoints after each atomic move. The definition census permits the differently named private `_REPOSITORY_IMPORT_ROOT` bootstrap only in the executable while requiring exactly one `ROOT` definition in `repository.py`.
- **Acceptance evidence:** Every moved function has an identical normalized AST fingerprint, every moved constant has an identical stable resolved-value fingerprint, and every pure helper returns the exact pre-cutover value for the existing mutation corpus.
- **Depends on:** Task 1.

### Task 3: Move each contract policy to its domain owner

- **Owner:** Main agent.
- **Files allowed:** Four new contract modules, executable, and four focused policy test modules.
- **Output:** Catalog/Auth/Progress/Gameplay constants and all corresponding pure/filesystem violation functions exist only in their domain modules; the executable imports the five existing public checks—Stats, Dashboard, Auth, Catalog, Gameplay—and invokes them in the current relative order; policy tests import canonical functions directly.
- **Verification:** Complete existing mutation/runtime cases, golden exact ordered arrays, full test/assertion normalized-fingerprint replay, policy-module isolation search, module size checks, Ruff, and all three real working-directory contexts.
- **Acceptance evidence:** Aggregate calls appear in their original order and every controlled violation retains exact text/order.
- **Depends on:** Task 2.

### Task 4: Cut over tests, documentation, and close evidence

- **Owner:** Main agent.
- **Files allowed:** Algorithm test reduction, focused tests, `ARCHITECTURE.md`, `scripts/README.md`, new `EVIDENCE.md`, and attributable implementation fixes only.
- **Output:** No `runpy` test coupling; focused policy ownership documentation; reproducible evidence for behavior, structure, preservation, and review decisions.
- **Verification:** From repo root run the direct checker; from `frontend` run `python ../scripts/check_architecture_boundaries.py`; from `backend` run focused pytest and Ruff. Also run the CI manifest, fast quality gates, docs guard, `git diff --check`, exact proxy/duplicate/reverse-import searches, line/function census, symbol and test/assertion fingerprint replay, and strict mutable-allowlist/manifest replay. The controlled-failure harness imports `main`, monkeypatches all aggregate checks to empty except one deterministic two-row violation fixture, captures exit/stdout/stderr, and restores globals in `try/finally` (or pytest `monkeypatch` teardown), so it creates no repository file and requires no filesystem cleanup.
- **Acceptance evidence:** No product/generated file hash changes and every kill criterion maps to a command/result.
- **Depends on:** Tasks 1–3.

## Forbidden Moves

- Do not add, remove, weaken, strengthen, rename, reorder, or reword an architecture policy or violation.
- Do not combine this extraction with the discovered Gameplay success-response contract fix or any other product change.
- Do not alter backend/frontend runtime, serializers, views, services, models, payloads, hooks, components, styles, routes, caches, generated contracts, migrations, data, or assets.
- Do not change either public checker command, CI/quality-gate wiring, stdout/stderr destination, success/failure text, or exit code.
- Do not retain moved definitions or compatibility re-exports in the executable.
- Do not retain or introduce `_guard_namespace`, `namespace[...]`, `vars(module)`, compatibility dictionaries, proxy modules, dynamic test loaders, or indirect symbol lookup in architecture-guard tests.
- Do not introduce a shared domain-policy dependency, reverse import, registry metaprogramming layer, parser framework, cache, plugin system, or third-party dependency.
- Do not hand-edit or normalize unrelated dirty files, stage changes, create a commit, or rewrite prior goal artifacts.

## Review Gates

1. PRE plan review before baseline capture or implementation.
2. POST alignment review after extraction and evidence draft.
3. Correctness review focused on exact rule/message/order/CLI preservation and direct/wrapper parity.
4. Maintainability review focused on module cohesion, one-way imports, canonical test ownership, naming, and absence of facades/duplication.
5. Independent final verifier after findings and evidence metadata are synchronized.
