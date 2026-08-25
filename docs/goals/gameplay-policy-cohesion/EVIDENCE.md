# Slice 15 Evidence — Gameplay Policy Cohesion

Date: 2026-08-21 (Asia/Manila)

## Result

The regrown Gameplay architecture policy is now split into three focused owners without changing any rule, diagnostic, ordering, public command behavior, product file, or generated artifact:

| Owner | Responsibility | Lines |
|---|---|---:|
| `scripts/checks/architecture_guard/contracts/gameplay.py` | Mutation-request ownership and live request checker | 477 |
| `scripts/checks/architecture_guard/contracts/gameplay_response.py` | Backend/OpenAPI success-response ownership and live response checker | 507 |
| `scripts/checks/architecture_guard/contracts/gameplay_response_frontend.py` | TypeScript generated-response enforcement and anti-facade analysis | 767 |

All three are below the previously approved 900-line policy-module ceiling. The old 1,696-line combined owner contains no response definition or re-export. The six request tests remain in `test_gameplay_policy.py`; the five response tests now live in `test_gameplay_response_policy.py`.

This closes only the bounded Slice 15 cohesion cutover. The broad codebase-modernization goal remains active.

## Ownership and cutover

The executable imports `check_gameplay_mutation_contract_ownership` directly from `contracts.gameplay` and `check_gameplay_response_contract_ownership` directly from `contracts.gameplay_response`. Their aggregate positions remain adjacent and ordered request then response (indices 13 and 14 in the `main()` check-call census).

`gameplay_response.py` depends one-way on `gameplay_response_frontend.py`. Neither response module imports `gameplay.py`; the frontend analyzer does not import the backend/OpenAPI response owner; no policy module imports the executable. Static definition census found 20 policy functions with one definition each and zero response functions in `gameplay.py`.

Four locations used by both concerns are explicit concern-local boundary declarations. Their resolved values are exact at cutover and no response module aliases/imports the historical request symbols:

| Response-scoped declaration | Exact resolved value |
|---|---|
| `GAMEPLAY_RESPONSE_GENERATED_OPENAPI` | `frontend/src/shared/api/generated/openapi.json` |
| `GAMEPLAY_RESPONSE_BACKEND_VIEWS` | `backend/adventures/views.py`, `backend/challenges/views.py` |
| `GAMEPLAY_RESPONSE_FRONTEND_APIS` | Adventure and Challenge run API modules |
| `GAMEPLAY_RESPONSE_SHARED_COMMAND_TYPES` | `frontend/src/shared/level/types.ts` |

The canonical test modules import and use the response-scoped symbols directly. After maintainability review, obsolete generic aliases were removed from the response test module; its pre-cutover function-AST replay applies the same fixed four-name normalization used for the moved response policy functions.

## Exact contract replay

The pre-cutover capture records 38 top-level Gameplay policy symbols. Every function replays its normalized AST SHA-256 exactly; every constant retains its stable resolved value. The only normalization maps the four approved response-scoped names back to their historical names in these four functions:

- `gameplay_response_backend_violations`
- `gameplay_response_openapi_violations`
- `gameplay_response_frontend_violations`
- `check_gameplay_response_contract_ownership`

Result:

```text
manifest_replay PASS
baseline_symbols 38
module_lines gameplay=477 response=507 frontend=767
mapped_values exact 4/4
```

The earlier architecture-policy slice's permanent 118-symbol manifest and golden policy equivalence remain byte-unchanged and pass:

```text
pytest -q \
  backend/common/tests/architecture_guard/test_symbol_manifest_equivalence.py \
  backend/common/tests/architecture_guard/test_policy_equivalence.py
..                                                                       [100%]
2 passed
```

## Test and ordered-diagnostic replay

The baseline fingerprints all 11 test functions and 58 assertions. After the split, each test exists once in its canonical module with the same normalized function AST and assertion count. Request tests replay directly; response tests first normalize the four canonical response-scoped location names to their historical names.

Instrumentation replayed every pure-analyzer and live-checker invocation made by the corpus:

```text
ordered_trace_replay PASS 75 75
```

That comparison is over each exact ordered `list[str]`, not only whether a test raised. Both live checkers remain `[]`.

Focused and complete results:

```text
pytest -q \
  backend/common/tests/architecture_guard/test_gameplay_policy.py \
  backend/common/tests/architecture_guard/test_gameplay_response_policy.py
...........                                                              [100%]
11 passed

pytest -q backend/common/tests/architecture_guard
.................................................                        [100%]
49 passed
```

## Public CLI evidence

The live precondition and postcondition are the captured dirty worktree with both checkers returning `[]`. The direct command runs from the repository root; the compatibility wrapper runs from `frontend`, matching the real package-script context.

Both post-cutover captures match their baseline exit code, stdout bytes, and stderr bytes exactly:

```text
direct_checker byte_parity PASS
compatibility_wrapper byte_parity PASS
exit_code 0
stdout b'Architecture boundaries look clean.\r\n'
stderr b''
```

A controlled failure fixture replaced all aggregate checks with empty results except the response checker, which returned two ordered rows. It produced exit 1, empty stdout, and exactly one `controlled-first` row before exactly one `controlled-second` row on stderr beneath the existing failure heading and rules text:

```text
controlled_failure PASS
```

## Reproducible custom evidence

The maintainability review identified that the first evidence draft recorded custom replay labels without a durable consumer. The reviewer fix adds one goal-local, standard-library verifier that consumes both manifests and the baseline directly:

```text
python docs/goals/gameplay-policy-cohesion/verify_evidence.py
symbol_manifest_replay PASS (38 symbols, 4 scoped-name normalizations)
test_manifest_replay PASS (11 tests, 58 assertions)
ordered_trace_replay PASS (75 calls)
cli_parity_replay PASS (direct, wrapper, controlled failure)
preservation_replay PASS (1808 strict files, 0 staged files)
Slice 15 evidence replay passed.
```

The verifier is the canonical command for the custom structure, behavior, CLI, and dirty-worktree evidence in this document. It also enforces the exact allowed definition set and owner for all three modules; rejects obsolete response-test aliases, duplicate or extra unique functions/constants, Gameplay-to-response re-exports, response-to-mutation imports, and frontend-to-orchestrator imports; and rejects modules at or above 900 lines, non-adjacent Gameplay checker calls, unapproved repository-visible paths, and changes outside the exact orchestrator/documentation normalizations.

Correctness and maintainability review found and proved verifier gaps in two passes. After occurrence-preserving definition census and shared `Import`/`ImportFrom` target analysis (including module-less relative imports), all isolated temp-copy mutations are rejected:

```text
extra_unique_definition REJECTED
response_reexport REJECTED
duplicate_response_constant REJECTED
plain_response_to_mutation_import REJECTED
relative_gameplay_to_response_import REJECTED
```

The verifier sets `sys.dont_write_bytecode = True` before any repository module import/load. A before/after size/mtime/SHA census of all 4,537 existing repository bytecode caches around the full verifier command proved zero additions, removals, or changes:

```text
bytecode_cache_replay PASS files 4537 added 0 removed 0 changed 0
```

## Quality gates

```text
ruff check <Slice 15 Python targets>
All checks passed!

python scripts/checks/check_documentation_current.py
Root documentation is current and /docs is limited to scoped goals.

python scripts/checks/check_ci_quality_gates.py
CI quality gate manifest is complete.

git diff --check
PASS (two pre-existing line-ending warnings only)

python scripts/checks/check_quality_gates.py
No forbidden legacy product vocabulary found in active code.
Architecture boundaries look clean.
CSS architecture looks clean.
Generated curriculum targets are consistent (2056 cases).
Generated API contract is current.
Frontend runtime API wrappers use the generated API contract helper.
Runtime API wrapper types compose the generated API contract.
Root documentation is current and /docs is limited to scoped goals.
CI quality gate manifest is complete.
No generated/cache artifacts are tracked by Git.
All fast quality gates passed.
```

## Dirty-worktree preservation

The baseline captures every repository-visible existing path outside the exact mutable allowlist, four dirty mutable size/SHA fingerprints, approved absences, the exact executable import preimage, the exact `ARCHITECTURE.md` CI-guard bullet, immutable plan artifacts, and both generated manifests. The maintainability fix renamed the inaccurate `mutable_preimages` field to `mutable_fingerprints` and records `verify_evidence.py` as a reviewer-approved addition; the original baseline SHA and the corrected SHA are both recorded below.

Final reviewer-fixed replay:

```text
preservation_replay PASS
strict_visible_byte_exact 1808
current_existing_visible 1819
unapproved_existing 0
orchestrator changes import-only under exact normalization
ARCHITECTURE.md changes one captured bullet only under exact normalization
staged_files 0
```

All product/runtime and generated files are within the strict byte-exact set. No file was staged, committed, discarded, restored, or normalized outside the approved paths.

## Artifact hashes

| Artifact | SHA-256 |
|---|---|
| `gameplay.py` | `11BC0068865142C4F5130E9D7EF40CB4081AD158591C6E3FDA24D1287310E07C` |
| `gameplay_response.py` | `1D83B11B84018034B04BB373992930A077793FB48EC42D188F31DF3583EEBA65` |
| `gameplay_response_frontend.py` | `13851723AFC89694716742486AF7121ABAB4034409A6FF4AD082BF903B54AC50` |
| request policy tests | `482C33555A0A3C6A0516D1334C4454488EC0D9398834F0359629AFD559F6D59A` |
| response policy tests | `DD14663BB7DDA1E4BE28B4F2DD369496DE430FF368167F57ED7A804260B8F331` |
| pre-slice baseline, original capture | `53A3FC6987EB30D30ADF8CBB2A42AF1582DE342A55EEC7AC9E7E5FDCF753B5EA` |
| pre-slice baseline, reviewer-corrected field/addition record | `229708840F3FECF176F9A6019691A12C82A79FB573EDDD49DDE0A6B0EB9A1BAB` |
| symbol manifest | `38E57962CF7DE0ED0BFA9153049F921349A5DBCDE1A1375DC1F6FEE74B35F93C` |
| test manifest | `BD04F21F13E34491DE8A5E748568156E3F981F898CE3A0A946C102D88799E5C7` |
| reproducible evidence verifier | `B5B8CCE50750539EC7132AD2BEE43918BA2FD04FA60DC0614C85AAEA0D00A5F9` |

## Review status

- PRE plan review: `aligned`, with no remaining findings after the concern-scoped constant and preservation amendments.
- POST alignment review: `aligned`, no findings on the final hardened state.
- Correctness review: `PASS`, no findings on the final hardened state. Earlier verifier-only loopholes covering extra/duplicate definitions, incomplete import-form analysis, re-exports, and bytecode writes were fixed and mutation-proven before the final rerun.
- Maintainability review: `PASS`, no findings on the final hardened state. Earlier response-test vocabulary, reproducibility, duplicate-definition, and import-analysis findings were fixed before the final rerun.
- Final verification: `FINAL_VERIFIED`. The independent verifier reran the canonical evidence command, 11 focused tests, 49 complete architecture-guard tests, both CLI entrypoints, all five mutation probes, artifact-hash checks, preservation coverage, and the staged-file census.
