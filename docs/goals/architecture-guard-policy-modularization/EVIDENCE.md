# Architecture Guard Policy Modularization — Evidence

## Outcome

Slice 13 replaces the 5,367-line architecture-policy monolith with a 1,679-line executable plus focused repository, Python-analysis, TypeScript-analysis, Catalog, Auth, Progress, and Gameplay owners.

The executable still owns the public CLI, aggregate order, rendering, remaining workflow/general policies, and exit status. Domain policies import only repository and source-analysis helpers. No policy imports the executable or another policy module. No compatibility re-export or test namespace proxy remains.

No backend/frontend product file, generated API artifact, public wrapper, CI invocation, migration, data file, or asset changed in this slice.

## Changed artifacts

- Modified `scripts/checks/check_architecture_boundaries.py` into the stable orchestrator.
- Added `scripts/checks/architecture_guard/repository.py`, `python_analysis.py`, and `typescript_analysis.py`.
- Added isolated `contracts/catalog.py`, `auth.py`, `progress.py`, and `gameplay.py` owners.
- Split the 1,877-line algorithm test into a 394-line core/workflow test and focused policy tests.
- Added pre/post exact ordered-violation and complete 118-symbol equivalence checks.
- Added focused direct tests for every reusable Python helper and every TypeScript parser family.
- Updated `ARCHITECTURE.md` and `scripts/README.md` with the one-way ownership rule.

## Target-perspective CLI evidence

### Direct executable from repository root

Command: `python scripts/checks/check_architecture_boundaries.py`

- Pre-cutover: exit 0, stdout `Architecture boundaries look clean.\r\n`, stderr empty.
- Post-cutover: exit 0, stdout `Architecture boundaries look clean.\r\n`, stderr empty.

### Preserved compatibility wrapper from the CI working directory

Working directory: `frontend`

Command: `python ../scripts/check_architecture_boundaries.py`

- Pre-cutover: exit 0, stdout `Architecture boundaries look clean.\r\n`, stderr empty.
- Post-cutover: exit 0, stdout `Architecture boundaries look clean.\r\n`, stderr empty.

### Direct executable from the backend working directory

Working directory: `backend`

Command: `python ../scripts/checks/check_architecture_boundaries.py`

- Post-cutover: exit 0, stdout `Architecture boundaries look clean.\r\n`, stderr empty.

### Controlled failure rendering

All aggregate checks were temporarily replaced in memory, one check returned two deterministic rows, and every global was restored in `finally`. No repository file was created or changed.

- Pre/post exit: 1.
- Pre/post stdout: empty.
- Pre/post stderr: exact match.

```text
Architecture boundary violations found:
  fixture/one.py: deterministic first violation
  fixture/two.ts: deterministic second violation

Rules: shared cannot import features; non-page feature modules cannot import pages; backend runtime code cannot inspect frontend source/assets or form import cycles; feature folders and backend service/common layers must keep the normalized shape; Dashboard summary API contract ownership must stay generated through Home shims; Stats summary API contract ownership must stay generated and one-way; Auth success contracts must stay account-owned, generated, and one-way; gameplay mutation request contracts must stay shared, generated, and one-way; Home Overview workflow ownership must stay one-way; content editor and Home Hub workflow ownership must stay one-way; displaced architecture paths must stay deleted.
```

The five extracted policy calls remain separately visible in their original relative order: Stats, Dashboard, Auth, Catalog, Gameplay.

## Structural cutover evidence

| File | Lines | Top-level functions |
|---|---:|---:|
| `scripts/checks/check_architecture_boundaries.py` | 1,679 | 37 |
| `architecture_guard/repository.py` | 40 | 2 |
| `architecture_guard/python_analysis.py` | 200 | 8 |
| `architecture_guard/typescript_analysis.py` | 889 | 32 |
| `architecture_guard/contracts/catalog.py` | 773 | 9 |
| `architecture_guard/contracts/auth.py` | 810 | 7 |
| `architecture_guard/contracts/progress.py` | 826 | 10 |
| `architecture_guard/contracts/gameplay.py` | 477 | 4 |

Static AST census found 118 moved symbols, 118 unique names, and exactly one definition for every name across the executable and package. Searches found no domain constants/implementations left in the executable, no policy-to-policy or policy-to-executable import, and no `runpy`, `_guard_namespace`, `namespace[...]`, `vars(module)`, compatibility dictionary, or import proxy in architecture-guard tests.

The executable bootstrap uses private `_REPOSITORY_IMPORT_ROOT`; canonical `ROOT` exists only in `repository.py`. Direct execution, wrapper execution, and backend pytest imports all succeeded in their real working directories.

## Test preservation and equivalence

Pre-cutover command from `backend`:

`python -m pytest common/tests/test_architecture_guard_algorithms.py -q`

Result: 43 passed in 32.48s.

Post-cutover command from `backend`:

`python -m pytest common/tests/test_architecture_guard_algorithms.py common/tests/architecture_guard -q`

Result after review fixes: 58 passed in 30.23s.

The 43 pre-existing test names and all 216 pre-existing assertion AST fingerprints remain. Forty-one complete normalized test-function ASTs match. Two setup-only fingerprints intentionally differ:

1. The pre-capture normalizer converted the first test's dynamic lookup into the invalid no-op assignment `strongly_connected_components = strongly_connected_components`; the direct-import test removes that assignment.
2. One Auth test used dynamic `namespace[name]`. Retaining it would violate the approved proxy ban, so it now passes the six directly imported path constants to the same local reader.

Neither exception changes an assertion; the assertion mismatch count is zero. Fifteen additive tests now cover exact ordered violation arrays, every reusable Python/TypeScript analysis family, and the complete moved-symbol manifest. The ordered fixture remains Catalog 3, Auth 4, Progress 4, Gameplay 15.

## Pre-cutover symbol-manifest recovery and replay

The first manifest write was damaged by shell-output truncation: it retained 115 keys, omitted three Catalog functions, and spliced one Catalog fingerprint into `canonical_ts_module_reference`. Correctness review rejected that incomplete proof.

The exact pre-cutover checker was then recovered from Git's object store as blob `238924e3df373f952925419df0178cb998ea5634`:

- Byte length: 205,602 — exact baseline match.
- SHA-256: `a603466344e4425dc36ce807262f088eefecaa46b2a7845a2e90d1317aca31af` — exact baseline match.
- The deterministic pre-capture generator was replayed against that exact source.
- The regenerated manifest contains 118/118 keys and compares byte-for-data exactly with an independent regeneration.
- Permanent equivalence coverage replays all 72 normalized function AST fingerprints and all 46 resolved constant fingerprints from canonical direct imports.
- The current package contains all 118 planned symbols exactly once in the recorded owners.

The damaged captured manifest was 38,942 bytes with SHA-256 `c463db6d507f960e2e3d3aa713f79c29ab992f317a8fb102bbac1c8c0e083944`. The repaired manifest is 39,879 bytes with SHA-256 `db011e7f421a53f5d7bf1e83d2c00aa702027e35f07ee938e3c9daf43ca4e29a`.

## Verification matrix

| Check | Result |
|---|---|
| Focused architecture tests | 58 passed |
| Ruff on executable/package/tests | passed |
| Direct checker | passed, exact stdout/stderr/exit |
| Compatibility wrapper from `frontend` | passed, exact stdout/stderr/exit |
| Controlled failure rendering | exact pre/post match |
| `python scripts/check_documentation_current.py` | passed |
| `python scripts/check_ci_quality_gates.py` | passed |
| `python scripts/check_quality_gates.py` | all 10 fast gates passed in 151.7s |
| `git diff --check` | passed; two pre-existing line-ending warnings only |

The fast gate replay included 2,056 generated curriculum target cases, current generated API contract checks, frontend API usage/type adoption, architecture/CSS checks, documentation, CI manifest, and repository artifacts.

## Preservation replay

- Strict dirty entries: 193/194 retain their captured status, byte length, and SHA-256. The sole changed strict artifact is the reviewed repair of `PRE_CUTOVER_SYMBOL_MANIFEST.json`; its exact old and regenerated hashes are recorded above.
- Unexpected post-baseline paths outside the allowlist: none.
- Protected backend aggregate: 483 files, 15,111,237 bytes, SHA-256 `f47e3a68ab04eff466d728479eca7db9ee3cb42e05d56ed1bbdc52a8709072b0` — exact match.
- Protected frontend aggregate: 1,142 files, 414,286,178 bytes, SHA-256 `9ba3258a90d7e83a952d2f7f468caea5c10c0e2d26e9a96bfc4d51a46aa0ab7d` — exact match.
- Public wrapper, quality-gate wiring, CI workflow, committed OpenAPI, and generated TypeScript hashes: all exact matches.

## Review status

- PRE plan review: APPROVED, no P0/P1.
- POST alignment review: ALIGNED, no blocker/major/minor findings.
- Correctness review: initial P1 manifest-proof gap and follow-up evidence wording repaired; no remaining P0/P1/P2 findings.
- Maintainability review: initial P2 direct analyzer-test gap repaired with 13 focused tests; re-review passed with no remaining findings.
- Independent final verification: FINAL_VERIFIED.

## Residual risk

The guard still uses bounded regex/AST source analysis rather than full language parsers, exactly as before. This slice does not optimize the roughly 20–30 second repository-wide checker runtime and does not add the deferred gameplay success-response policy.

The recovered pre-cutover blob is currently present in the local Git object store but is not named by a repository ref, so future source-level regeneration depends on retaining that object. The corrected manifest and its permanent 118-symbol replay test are durable workspace artifacts.
