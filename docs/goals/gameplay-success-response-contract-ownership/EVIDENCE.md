# Slice 14 Evidence — Gameplay Success-Response Contract Ownership

Date: 2026-08-14 (Asia/Manila)

## Result

Adventure and Challenge success-response schemas now belong to their domains, generated OpenAPI reflects the real runtime payloads, and frontend HTTP wire types visibly compose the generated components. Runtime payload builders, services, routes, request contracts, cache algorithms, and UI behavior were not changed.

The broad modernization goal remains active; this document closes only the bounded Slice 14 cutover.

## Ownership and cutover

| Contract | Canonical owner | Generated/client projection |
|---|---|---|
| Shared terminal step and run status | `backend/common/openapi.py` | `RuntimeStepResponse`, `GameplayRunStatus`, `TerminalStep` |
| Adventure full run, patch, command union/envelope, library | `backend/adventures/openapi.py` | `AdventureRunResponse`, `AdventureRunPatchResponse`, `AdventureCommandRunResponse`, generated-derived Adventure feature types |
| Challenge full run, persisted/command steps, command update/envelope | `backend/challenges/openapi.py` | `ChallengeRunResponse`, `ChallengeRunStepResponse`, `ChallengeCommandStepResponse`, `ChallengeCommandRunResponse`, generated-derived Challenge feature types |
| Runtime values | Existing `backend/adventures/payloads.py` and `backend/challenges/payloads.py` | Unchanged byte-for-byte |

Static ownership search found each domain response class only in its canonical OpenAPI module and direct view imports. `backend/adventures/serializers.py` remains absent. The live response checker reports `PASS`.

## Authenticated runtime evidence

Command:

```text
pytest -q backend/common/tests/test_gameplay_response_contract.py
....                                                                     [100%]
4 passed in 4.77s
```

The four real authenticated tests cover:

- Adventure start, detail, and workspace success responses: the exact 21-key full-run set, including required `is_passed`, `passed`, nullable `story`, and nullable `battle_stage`; every response validates with the domain serializer and the workspace file persists.
- Adventure commands: exact envelope/run/step keys on the 4-key live patch with literal `partial: true`, the full-run wave transition, and the terminal full run. Before/after snapshots assert status, both counters, current wave, repository state, persisted-step count, level-completion count, coin-transaction count, wallet balance, and ordered run-wave statuses for all three branches.
- Challenge start, detail, workspace, and retry responses: the exact 25-key full-run set, including always-present nullable `story`; every response validates and workspace mutation persists.
- Challenge commands: exact 9-key started update with all four transition-only fields absent, and exact 13-key terminal update with those fields present. Command steps contain all 9 keys including `evaluation_result`; before/after snapshots assert status, all three counters, repository state, persisted-step count, trial/level completion counts, coin-transaction count, wallet balance, and conditional field nullability for both branches.

These key sets and state transitions match the authenticated pre-slice behavior matrix in `PRE_SLICE_BASELINE.json`.

## Generated contract evidence

| Component | Exact contract evidence |
|---|---|
| `RuntimeStepResponse` | 4 properties, all required |
| `AdventureRunResponse` | 21 properties, all required; nullable keys remain required |
| `AdventureRunPatchResponse` | exactly `partial`, `id`, `status`, `current_attempt`, all required |
| `AdventureCommandRunResponse` | exact `oneOf` full-run and patch references |
| `ChallengeRunStepResponse` | 8 properties, all required |
| `ChallengeCommandStepResponse` | 9 properties, all required, including `evaluation_result` |
| `ChallengeCommandRunResponse` | 9 required base fields; exactly 4 optional transition fields with exact nullability |
| `ChallengeRunResponse` | 25 properties, all required; `story` required and nullable |
| `GameplayRunStatus` | one named shared four-value enum |
| `PartialEnum` | boolean literal enum `[true]` |

Every start/read/retry/workspace/command operation points to its named response component. Schema generation exited 0. It reported 61 existing warning lines, including unresolved custom-authenticator warnings, and **0 response-contract warning lines** for the Slice 14 serializers/components.

Canonical regeneration was byte-reproducible:

```text
generated_reproducibility PASS
openapi.json  9FF5B5B2D44BDFF84A34FCBFFC68E3F6B779CD151D4B56FBA9625CE63A22C667
apiTypes.ts   67B87CAA9B83AD9E69F25142D4DE9524FBA2D4096F93C8A3665AAC696E7E5FC5
```

## Frontend boundary evidence

- `TerminalStep` derives exactly from `ApiSchemas['RuntimeStepResponse']`.
- Adventure full/patch/library/command types use their generated components with only the approved nested JSON refinements.
- `ChallengeRunResponse` and `ChallengeRunStepResponse` are exact generated-derived HTTP types.
- `ChallengeRun` composes `ChallengeRunResponse`; its only client-cache divergence is the named optimistic step branch that may omit `visualization_snapshot`.
- Both Challenge full-response API modules use `ChallengeRunResponse`, never the client cache model.
- Adventure and Challenge discard calls use generated operation response inference directly; no handwritten `null` response override remains.

Verification:

```text
npm run api:check                 PASS
npm run api:usage-check           PASS
npm run api:type-adoption-check   PASS
npm run build                     PASS (2,659 modules transformed)
npm test -- --reporter=dot        PASS (73 files, 492 tests)
```

## Architecture durability

The response policy is additive to the preserved request policy. The prior `check_gameplay_mutation_contract_ownership` normalized AST fingerprint remains exact; the new response policy has its own checker/test and is imported and invoked by the canonical `check_architecture_boundaries.py` command used by fast gates and CI.

Synthetic mutations reject:

- displaced/common backend owners, assignment aliases, and import/re-export facades;
- missing `passed`, `story`, or `evaluation_result`;
- full/patch union collapse and wrong operation references;
- wrong requiredness or nullability for every Challenge transition-only field, plus unexpected nullability on components whose nullable set is empty;
- wrong shared status component reference;
- broad/`keyof` or primitive omissions, `Partial`/`Record` overlays, extra or trailing overlay intersections, complete reconstruction, unrelated generated bases, secondary frontend DTOs/re-exports, response-return casts/adapters/suffixes, decoy method shadowing outside the owned API object, generator-method substitutions, duplicate owned operation calls, effective object-member overrides (spread/computed/property), direct/compound/logical mutation and deletion of API objects through canonical, imported, or local aliases, forbidden namespace imports, canonical API-object re-export facades through named/star/namespace and immutable/mutable/typed/parenthesized local aliases, `Object`/`Reflect` mutation APIs, manual destroy overrides, client-state HTTP response overrides, and any second client/server step divergence; ordinary `==`/`===` comparisons remain allowed.

```text
pytest -q backend/common/tests/architecture_guard/test_gameplay_policy.py
11 passed

pytest -q backend/common/tests/architecture_guard
49 passed in 40.73s

python scripts/checks/check_architecture_boundaries.py
Architecture boundaries look clean.

gameplay_response_live_checker PASS
```

## Regression and quality gates

```text
ruff check <Slice 14 Python targets>       All checks passed
focused state/budget/workspace regressions 21 passed in 4.59s
python scripts/checks/check_quality_gates.py
All fast quality gates passed
```

The fast gate includes legacy vocabulary, architecture, CSS architecture, 2,056 generated curriculum cases, API current/usage/adoption, documentation, CI manifest, and repository-artifact checks.

## Dirty-worktree preservation

The initial baseline and the later amended three-target supplement both replay after implementation:

```text
preservation_replay PASS
strict_dirty_byte_exact                  206
strict_dirty_supplement_normalized         1
strict_protected_byte_exact               23
append_only_prefixes                       2
protected_python_files_ast_subsequence     5
protected_typescript_files_byte_exact      3
api_response_only_normalizations           2
supplement_normalizations                  3
```

Additional preservation facts:

- Both runtime payload modules retain their exact pre-slice SHA-256 values.
- The Adventure API wrapper normalizes exactly to its pre-slice bytes after restoring only the captured redundant destroy `null` generic.
- The existing Challenge run API wrapper normalizes exactly to its pre-slice bytes after replacing only `ChallengeRunResponse` with `ChallengeRun`.
- The newly discovered Challenge entry API and Adventure modal fixture normalize exactly to their original clean preimages under the approved supplement.
- The canonical architecture orchestrator normalizes exactly to its captured dirty preimage after removing only the response-checker import, invocation, and rules-text clause.
- The generator owner and 206 unrelated dirty paths are byte-exact; the one supplemented dirty orchestrator and all protected declarations remain exact under their approved normalization or ordered AST subsequences.
- No files were staged, committed, discarded, or normalized outside the approved targets.

## Review status

PRE planning and all integration-boundary/reviewer-fix amendments were independently reviewed and aligned before their newly authorized edits. POST alignment is `Aligned`; independent correctness and maintainability reruns are both `PASS` with no remaining findings. The independent closing audit returned `FINAL_VERIFIED`.
