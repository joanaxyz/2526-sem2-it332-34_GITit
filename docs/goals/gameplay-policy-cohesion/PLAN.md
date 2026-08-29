# Gameplay Policy Cohesion — Slice 15 Implementation Plan

**Intent:** Restore the architecture guard's verified cohesion invariant after the Slice 14 success-response policy grew `contracts/gameplay.py` from 477 to 1,696 lines. A policy maintainer should be able to find request ownership, backend/OpenAPI response ownership, and frontend generated-response enforcement in one focused module each.

**Current State:** `scripts/checks/architecture_guard/contracts/gameplay.py` combines two independent policy families. Lines 118–476 and the checker at line 1,641 enforce mutation-request ownership. Lines 477–913 enforce backend/OpenAPI success-response ownership. Lines 914–1,640 enforce TypeScript success-response ownership, and the response filesystem checker begins at line 1,670. The combined module exceeds the prior architecture-policy slice's explicit 900-line maximum, its docstring describes only mutation ownership, and its 697-line test file mixes both corpora.

**Expected End State:**

- `contracts/gameplay.py` owns only mutation-request constants, pure violations, and its filesystem checker and returns to approximately its verified 477-line shape.
- `contracts/gameplay_response.py` owns backend/OpenAPI response constants, concern-scoped backend/OpenAPI input locations, violations, and the complete response filesystem checker.
- `contracts/gameplay_response_frontend.py` owns only TypeScript success-response analysis and its concern-scoped frontend input locations.
- `test_gameplay_policy.py` owns only the six mutation tests; `test_gameplay_response_policy.py` owns the five existing response tests.
- Every policy/analysis module is below 900 physical lines. The canonical executable imports the two public checkers from their canonical owners and invokes mutation immediately before response, exactly as it does now.

**Target-Person Output:** An architecture-policy maintainer can answer “where do I change request ownership?”, “where do I change backend/OpenAPI response exactness?”, and “where do I change frontend generated-response enforcement?” by opening one focused file for each concern. They can run the same public command and receive byte-equivalent stdout, stderr, ordered violations, and exit status.

**Truth Owners:**

| Concern | Canonical owner |
|---|---|
| Shared gameplay request serializers, generated request components, request-body adapters, and request checker | `scripts/checks/architecture_guard/contracts/gameplay.py` |
| Domain response serializers, exact OpenAPI response schemas/operations, response-scoped generated-schema/backend-view locations, and complete response checker | `scripts/checks/architecture_guard/contracts/gameplay_response.py` |
| Generated-derived TypeScript response aliases, overlay/refinement rules, direct API-return rules, anti-facade analysis, and response-scoped frontend API/shared-command locations | `scripts/checks/architecture_guard/contracts/gameplay_response_frontend.py` |
| Request synthetic mutation corpus | `backend/common/tests/architecture_guard/test_gameplay_policy.py` |
| Response synthetic mutation corpus | `backend/common/tests/architecture_guard/test_gameplay_response_policy.py` |
| Aggregate check order, rendering, stdout/stderr, and exit status | `scripts/checks/check_architecture_boundaries.py` |

**Contract Boundary:** Both public checker functions return an ordered `list[str]`. `scripts/checks/check_architecture_boundaries.py` expands those lists into the existing aggregate, renders the same success/failure text on the same stream, and returns the same exit status. Pure analyzers continue to accept the same `dict[str, str]` or OpenAPI dictionary inputs and return the same ordered violations.

**Read Path:** Backend/frontend source plus committed OpenAPI → canonical request or response pure analyzer → canonical filesystem checker → adjacent aggregate calls in `check_architecture_boundaries.main()` → unchanged CLI output and status. There is no repository write path; all checks remain read-only.

**Cutover Strategy:** Capture the current combined module and tests as the pre-cutover source of truth, then atomically move definitions. Preserve function bodies exactly except for four declared response-scoped constant substitutions. Cut the executable's response import over to `gameplay_response.py` and cut response tests over to their new module. Preserve the mutation module's historical manifest-facing symbols and normalized function ASTs. Do not leave response re-exports, proxy imports, competing constants, reverse imports, or test forwarding behind.

The four values used by both concerns stay historically canonical for mutation in `gameplay.py`, while response modules receive deliberately concern-local boundary declarations that may diverge later as policy scope changes:

| Historical mutation name | Response-scoped name | Response owner |
|---|---|---|
| `GAMEPLAY_GENERATED_OPENAPI` | `GAMEPLAY_RESPONSE_GENERATED_OPENAPI` | `gameplay_response.py` |
| `GAMEPLAY_BACKEND_VIEWS` | `GAMEPLAY_RESPONSE_BACKEND_VIEWS` | `gameplay_response.py` |
| `GAMEPLAY_FRONTEND_APIS` | `GAMEPLAY_RESPONSE_FRONTEND_APIS` | `gameplay_response_frontend.py` |
| `GAMEPLAY_SHARED_COMMAND_TYPES` | `GAMEPLAY_RESPONSE_SHARED_COMMAND_TYPES` | `gameplay_response_frontend.py` |

These repeated resolved path values are intentional policy-input declarations, not aliases, imports, facades, or competing response truth owners. No response module imports their historical mutation counterparts. Pre/post response function fingerprints normalize only the four names above back to their historical names before hashing.

**Displaced Path:** All response constants, response helpers, response violation functions, and `check_gameplay_response_contract_ownership` leave `contracts/gameplay.py`. All response imports and test functions leave `test_gameplay_policy.py`. The old combined ownership path must not remain as a facade.

**Value Density:** One measured 1,696-line policy module becomes three cohesive modules below the repository's already-approved 900-line ceiling. The request owner returns near its prior 477-line verified size, while every current rule and test remains present exactly once.

**Evidence Contract:**

- Pre/post normalized AST SHA-256 for every function and stable recursively normalized value SHA-256 for every constant in the current combined module. For the four affected response functions only—`gameplay_response_backend_violations`, `gameplay_response_openapi_violations`, `gameplay_response_frontend_violations`, and `check_gameplay_response_contract_ownership`—the post-cutover AST replay first applies the fixed response-name-to-historical-name map above; no other normalization is permitted.
- Exact resolved-value equality for every historical/response-scoped constant pair in the fixed map, plus proof that response modules do not import the historical mutation constants.
- Pre/post normalized AST SHA-256 and assertion counts for all 11 current Gameplay policy tests.
- Exact pre/post ordered result arrays for every current synthetic mutation test and both live filesystem checkers.
- Direct checker and compatibility-wrapper stdout, stderr, and exit-code parity on the captured live baseline worktree when both live checkers return `[]`, plus a controlled deterministic failure fixture proving ordered stderr rendering. Each capture records command, working directory, stdout bytes, stderr bytes, and exit status before and after cutover.
- Static definition/import census proving one canonical owner per symbol, no response symbol in `gameplay.py`, no facade/re-export/reverse edge, and mutation immediately before response in the aggregate.
- Line counts proving all three policy modules are below 900 lines.
- Focused Gameplay tests, complete architecture-guard tests, Ruff, architecture command from each real working directory, documentation guard, fast quality gates, and `git diff --check`.
- Strict dirty-worktree preservation replay for every path outside the precise mutable allowlist; no backend/frontend runtime or generated artifact hash change.

**Kill Criteria:**

- `contracts/gameplay.py` contains zero response-policy definitions, imports, response-scoped constants, or re-exports and remains the only owner of the pre-existing mutation symbols.
- `gameplay_response.py` and `gameplay_response_frontend.py` are each below 900 physical lines and have a one-way dependency only from response orchestration to frontend analysis.
- Every current response helper/checker and response-scoped constant has exactly one definition; the four concern-local declarations resolve exactly to their mapped historical path values without importing or aliasing the historical symbols; no compatibility facade exists in `gameplay.py`, `contracts/__init__.py`, or a test proxy.
- The prior 118-symbol architecture-policy manifest replay remains unchanged for the mutation owner, and every newly captured response symbol fingerprint replays exactly after relocation.
- All 11 pre-cutover tests and every assertion survive once in their canonical focused test module with unchanged normalized function ASTs after import relocation only.
- Exact ordered violation text, captured-live-baseline direct/wrapper output bytes, aggregate call order, and success/failure exit codes remain unchanged.
- No backend/frontend runtime, generated contract, migration, data, asset, wrapper, CI, package/lock, or prior-goal artifact changes.
- Strict preservation replay passes and no file is staged, committed, discarded, or normalized outside the approved paths.

**Non-Goals:** Change no product behavior, API schema, generated artifact, policy rule, diagnostic wording, filesystem traversal, parser algorithm, performance characteristic, or CI command. Do not split other policy modules, the main executable, curriculum ledgers, frontend components, or backend services in this slice.

## Architecture Map

```text
scripts/checks/check_architecture_boundaries.py
  ├─ contracts/gameplay.py
  │    └─ mutation request policy + public mutation checker
  └─ contracts/gameplay_response.py
       ├─ backend/OpenAPI response policy + public response checker
       └─ contracts/gameplay_response_frontend.py
            └─ pure TypeScript response-ownership analysis

backend/common/tests/architecture_guard/
  ├─ test_gameplay_policy.py
  └─ test_gameplay_response_policy.py
```

The three policy modules may depend on the existing repository and source-analysis helpers. `gameplay_response.py` may import frontend analysis and its frontend-owned path constants from `gameplay_response_frontend.py`. No response module may import the mutation policy; the frontend module may not import the response orchestrator; no policy module may import the executable.

### Files to create

- `scripts/checks/architecture_guard/contracts/gameplay_response.py`
- `scripts/checks/architecture_guard/contracts/gameplay_response_frontend.py`
- `backend/common/tests/architecture_guard/test_gameplay_response_policy.py`
- `docs/goals/gameplay-policy-cohesion/PRE_SLICE_BASELINE.json`
- `docs/goals/gameplay-policy-cohesion/PRE_CUTOVER_SYMBOL_MANIFEST.json`
- `docs/goals/gameplay-policy-cohesion/PRE_CUTOVER_TEST_MANIFEST.json`
- `docs/goals/gameplay-policy-cohesion/EVIDENCE.md`

### Files to modify

- `scripts/checks/architecture_guard/contracts/gameplay.py`
- `scripts/checks/check_architecture_boundaries.py` — response import source only; call site and order remain byte-identical.
- `backend/common/tests/architecture_guard/test_gameplay_policy.py`
- `ARCHITECTURE.md` — replace only the existing architecture-guard bullet under `## CI Guards` to clarify the focused Gameplay topology and one-way same-domain dependency; capture the bullet's exact preimage and require every other byte to replay unchanged.

### Files to preserve exactly

- `scripts/check_architecture_boundaries.py` and all other public wrappers.
- `scripts/checks/architecture_guard/contracts/__init__.py`, every other policy/analysis module, and `scripts/README.md`.
- `scripts/checks/check_quality_gates.py`, `scripts/checks/check_ci_quality_gates.py`, `.github/workflows/ci.yml`, and all package-script wiring.
- `backend/common/tests/architecture_guard/test_policy_equivalence.py`, `test_symbol_manifest_equivalence.py`, their manifests/fixtures, and every non-Gameplay architecture-guard test.
- All backend/frontend production/runtime files, generated OpenAPI/TypeScript artifacts, migrations, authored/generated curriculum data, assets, lockfiles, build configuration, and every prior goal artifact.
- Every unrelated dirty or untracked path present at baseline capture.

### Precise mutable-path allowlist after baseline capture

- Existing implementation/test/docs paths: `scripts/checks/architecture_guard/contracts/gameplay.py`, `scripts/checks/check_architecture_boundaries.py`, `backend/common/tests/architecture_guard/test_gameplay_policy.py`, and `ARCHITECTURE.md`.
- Approved absent-to-created implementation/test paths: `scripts/checks/architecture_guard/contracts/gameplay_response.py`, `scripts/checks/architecture_guard/contracts/gameplay_response_frontend.py`, and `backend/common/tests/architecture_guard/test_gameplay_response_policy.py`.
- Approved slice artifacts: `docs/goals/gameplay-policy-cohesion/GOAL.md`, `PLAN.md`, `PRE_SLICE_BASELINE.json`, `PRE_CUTOVER_SYMBOL_MANIFEST.json`, `PRE_CUTOVER_TEST_MANIFEST.json`, and `EVIDENCE.md`.
- After capture, `GOAL.md`, `PLAN.md`, the baseline, and both manifests become immutable preservation entries. Only `EVIDENCE.md` remains append/update eligible.

## Task Board

### Task 1: Capture preservation and behavior baselines

- **Owner:** Main agent.
- **Files allowed:** The three new pre-cutover artifacts only.
- **Output:** Complete dirty manifest with status/existence/bytes/SHA-256; exact preimages for every mutable existing file; absence records for additions; protected hashes for wrappers, wiring, all product/generated files, prior artifacts, and unrelated dirty paths; current line/function/import census; current checker/test outputs; direct/wrapper stdout/stderr/exit bytes; normalized function/constant/test fingerprints; assertion counts; and exact ordered analyzer/checker results for the existing corpus.
- **Verification:** Baseline capture is read-only outside its three artifacts. Re-run all 11 focused tests, complete architecture-guard tests, both public entrypoint contexts, symbol-manifest equivalence, and policy equivalence before implementation. Confirm all approved new implementation/test paths are absent.
- **Depends on:** PRE approval.

### Task 2: Extract the frontend response-analysis owner

- **Owner:** Main agent.
- **Files allowed:** `gameplay.py`, new `gameplay_response_frontend.py`, and attributable baseline/evidence tooling only.
- **Output:** TypeScript response path constants, the response-scoped `GAMEPLAY_RESPONSE_FRONTEND_APIS` and `GAMEPLAY_RESPONSE_SHARED_COMMAND_TYPES` declarations, private TypeScript helpers, and `gameplay_response_frontend_violations` exist exactly once in the focused frontend module; no mutation or backend/OpenAPI responsibility crosses with them.
- **Verification:** Exact function-AST replay after the declared constant-name normalization for `gameplay_response_frontend_violations` only, exact response-scoped/historical value equality, exact ordered mutation-corpus replay, Ruff, line-count check, import-direction census, and live response analyzer result.
- **Depends on:** Task 1.

### Task 3: Extract backend/OpenAPI response ownership and cut over orchestration

- **Owner:** Main agent.
- **Files allowed:** `gameplay.py`, new `gameplay_response.py`, and the import block of `scripts/checks/check_architecture_boundaries.py` only.
- **Output:** Backend/OpenAPI response constants, the response-scoped `GAMEPLAY_RESPONSE_GENERATED_OPENAPI` and `GAMEPLAY_RESPONSE_BACKEND_VIEWS` declarations, helpers, pure violations, and public response checker exist exactly once in their canonical module. The response owner imports its frontend analyzer one way. The executable imports mutation and response checkers from separate owners while retaining their existing adjacent call sites.
- **Verification:** Exact response symbol replay after the declared name normalization for the three affected backend/checker functions only, exact response-scoped/historical value equality, exact analyzer/checker arrays, byte-unchanged mutation historical manifest test plus green replay, static no-facade/no-reverse-import search, both entrypoints, controlled failure rendering, Ruff, and module-size checks.
- **Depends on:** Task 2.

### Task 4: Split canonical test ownership and document the topology

- **Owner:** Main agent.
- **Files allowed:** Both Gameplay test modules and only the existing architecture-guard bullet under `ARCHITECTURE.md` → `## CI Guards`.
- **Output:** Six mutation tests remain in `test_gameplay_policy.py`; five response tests live in `test_gameplay_response_policy.py`; imports point directly at canonical modules; documentation names the focused topology and allowed one-way same-domain dependency.
- **Verification:** All 11 test-function normalized AST fingerprints and assertion counts replay exactly after import relocation; no dynamic loading, proxy fixture, test re-export, or duplicate test exists; focused and complete architecture-guard suites pass.
- **Depends on:** Task 3.

### Task 5: Close regression, preservation, and review evidence

- **Owner:** Main agent.
- **Files allowed:** `EVIDENCE.md` and attributable implementation fixes approved by review.
- **Output:** Reproducible outcome, behavior, topology, quality, and preservation evidence with PRE/POST/correctness/maintainability/final-verifier decisions.
- **Verification:** Focused tests; complete architecture-guard tests; prior symbol/policy equivalence tests; Ruff; root direct checker; compatibility wrapper from `frontend`; docs guard; CI-manifest guard; fast quality gates; `git diff --check`; definition/import/module-size census; manifest replay; exact CLI parity; strict dirty-worktree preservation replay; independent reviewers; final verifier after evidence metadata is synchronized.
- **Depends on:** Tasks 1–4.

## Forbidden Moves

- Do not add, remove, weaken, strengthen, rename, reorder, or reword any architecture policy, diagnostic, or test assertion.
- Do not change product/runtime code, serializers, views, OpenAPI owners, feature types, API wrappers, generated artifacts, migrations, data, assets, or curriculum.
- Do not change filesystem traversal, failure/success rendering, stdout/stderr destinations, exit codes, public wrapper commands, CI wiring, or quality-gate wiring.
- Do not retain response re-exports or aliases from `gameplay.py` or `contracts/__init__.py`; do not add a compatibility facade, registry, plugin layer, dynamic loader, or proxy test module.
- Do not duplicate policy truth or helpers. The only permitted repeated resolved values are the four explicitly mapped concern-local policy-input declarations above; they must use the response-scoped names, must compare equal at cutover, and must not import or alias their historical mutation counterparts.
- Do not introduce a response-to-mutation dependency, create a frontend-to-response reverse edge, or import the executable from any policy module.
- Do not modify historical manifests/equivalence expectations merely to accept drift. An import-only orchestrator change must normalize exactly to its preimage when that approved import is reversed.
- Do not hand-edit, normalize, stage, commit, discard, or otherwise alter unrelated dirty files or prior goal artifacts.

## Review Gates

1. PRE plan review before baseline capture or implementation.
2. POST alignment review after extraction, test cutover, and evidence draft.
3. Independent correctness review focused on exact symbols, rules, messages, order, live checker behavior, and direct/wrapper parity.
4. Independent maintainability review focused on module cohesion, one-way imports, canonical test ownership, naming, size, and absence of facades/duplication.
5. Independent final verifier after all findings, fixes, manifests, and evidence metadata are synchronized.
