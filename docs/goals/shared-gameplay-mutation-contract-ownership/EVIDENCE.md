# Slice 12 Evidence: Shared Gameplay Mutation Contract Ownership

## Result

Adventure and Challenge now share one request-validation owner, one generated request-component family, one frontend workspace input owner, one command-execution payload refinement, and one body-adapter boundary. Gameplay services, models, response payloads, routes, caches, simulator algorithms, and UI behavior were preserved.

## Outcome evidence

| Outcome | Evidence |
|---|---|
| One backend request owner | `common.serializers` owns `CommandSubmitSerializer`, `WorkspaceFileSerializer`, `WorkspaceFilePathSerializer`, and `WorkspaceFileRenameSerializer`. Both feature views import all four directly. |
| Displaced feature owners removed | `backend/adventures/serializers.py` is deleted. `backend/challenges/serializers.py` retains only `ChallengeRunStartSerializer`. Static search finds the four shared classes only in `backend/common/serializers.py`. |
| Runtime parity preserved | Seventeen contract/API tests include authenticated Adventure and Challenge create -> write -> rename -> query delete plus body-compatible delete traces. Malformed POST/PATCH/PUT/DELETE/command requests return 400 in both modes and leave repository state unchanged. |
| One exact generated component family | OpenAPI contains only `CommandSubmit`, `WorkspaceFile`, and `WorkspaceFileRename` for these request shapes. There are no `WorkspaceFileCreate` or `PatchedWorkspaceFile*` components. |
| PATCH and DELETE documented exactly | Both POST and PATCH operations reference `WorkspaceFile`, whose required list is `path`; each PATCH request body is itself required. Both PUT operations reference `WorkspaceFileRename`, whose required list is `new_path,path`; both DELETE operations expose one required string query parameter named `path` with `maxLength: 240`. Runtime DELETE body-or-query compatibility remains unchanged. |
| Generated frontend wire truth | `WorkspaceFileInput` and `WorkspaceFileRenameInput` refine generated schemas in `shared/level/workspaceFileTypes.ts`. `CommandExecutionPayload` refines generated `ClientCommandExecution` in `shared/level/types.ts` while preserving a non-null client revision and richer repository state. |
| One body adapter | `shared/level-runtime/runMutationInputs.ts` owns command, file-write, and rename body construction and returns generated `ApiSchemas` components. Both gameplay APIs delegate to it and contain no `ApiRequestBody` cast. |
| Durable cutover | The architecture gate rejects restored or alternate backend owners/re-exports (including aliased imports), noncanonical runtime serializer calls, TypeScript aliases/interfaces/re-export facades, duplicate command payloads, endpoint body casts, missing per-operation shared adapter imports/calls, OpenAPI forks/reference/body-required drift, and DELETE parameter drift. Explicit negative cases prove unrelated structural types remain legal and partial endpoint delegation fails. |

## Generated contract inspection

Fresh generator output completed without a relevant component-name collision warning. The current generated artifact reports:

```text
CommandSubmit required=command,execution properties=command,execution
WorkspaceFile required=path properties=content,path
WorkspaceFileRename required=new_path,path properties=new_path,path

POST   /api/adventure-runs/{run_id}/files/ -> #/components/schemas/WorkspaceFile
PATCH  /api/adventure-runs/{run_id}/files/ -> #/components/schemas/WorkspaceFile; body required=true
PUT    /api/adventure-runs/{run_id}/files/ -> #/components/schemas/WorkspaceFileRename
DELETE /api/adventure-runs/{run_id}/files/ -> query=path; required=true; type=string; maxLength=240

POST   /api/challenge-runs/{run_id}/files/ -> #/components/schemas/WorkspaceFile
PATCH  /api/challenge-runs/{run_id}/files/ -> #/components/schemas/WorkspaceFile; body required=true
PUT    /api/challenge-runs/{run_id}/files/ -> #/components/schemas/WorkspaceFileRename
DELETE /api/challenge-runs/{run_id}/files/ -> query=path; required=true; type=string; maxLength=240

displaced components=0
```

`python scripts/check_openapi_schema.py` and the generated-contract quality gate both confirm that `openapi.json` and `apiTypes.ts` are current generator output.

## Verification

### Backend and contract

| Command/lane | Result |
|---|---:|
| Shared serializer and authenticated dual-mode mutation contract tests | 17 passed in 4.18s |
| Focused regression, workspace, command-integrity, and command-budget lane | 41 passed in 59.75s |
| Full architecture-guard algorithm suite after guard hardening | 43 passed in 42.52s |
| `python manage.py check` | passed; 0 issues |
| Ruff over changed Python targets | passed |

The 41-test proportional backend lane covered `test_gameplay_mutation_contract.py`, bug regressions, shared run-workspace behavior, workspace mutation algorithms, and Adventure/Challenge command payload and budget integrity. A full backend run was not repeated because its known duration is disproportionate for this request-contract-only slice; the selected lane exercises both real HTTP paths plus the unchanged service boundary directly.

### Frontend

| Command/lane | Result |
|---|---:|
| Focused adapter/API/workspace suite | 5 files, 24 tests passed in 17.79s |
| Post-refinement adapter/API/simulator lane | 4 files, 19 tests passed in 45.88s |
| Full Vitest suite | 73 files, 492 tests passed in 260.70s |
| `npx tsc -b` | passed |
| `npm run build` | passed; 2,659 modules transformed in 101.8s |
| `npm run lint` | passed in 97.9s |
| `npm run lint:dead` | passed in 23.0s |

### Repository gates

- `python scripts/check_quality_gates.py`: all fast gates passed, including legacy vocabulary, architecture boundaries, CSS architecture, 2,056 curriculum seed cases, generated API contract, frontend API usage/type adoption, documentation currency, CI manifest, and repository artifacts.
- Direct architecture boundary check: passed.
- Direct generated OpenAPI check: passed.
- `git diff --check`: passed; Git emitted only existing line-ending normalization notices for one curriculum file and the generated TypeScript artifact.
- Static displaced-path search: the shared backend serializer classes have one declaration owner; the frontend has one `WorkspaceFileInput`, one `WorkspaceFileRenameInput`, and one `CommandExecutionPayload`; neither gameplay API contains `ApiRequestBody` or `as ApiRequestBody`.

## Preservation replay

The pre-slice manifest recorded 165 already-dirty/deleted/untracked paths. The four approved already-dirty mutable targets were excluded from strict hashing; every other entry was replayed by status, byte length, and SHA-256:

```text
manifest entries=165
strict entries=161
approved mutable dirty entries=4
strict replay errors=0

protected files=24
protected hash errors=0
```

All post-baseline changed or created paths are in the reviewed file map. `PLAN.md` and `GOAL.md` retained their exact pre-implementation hashes. No unrelated dirty-worktree path was staged, discarded, normalized, or overwritten.

## Deviations and residual risk

- drf-spectacular automatically partializes serializer schemas on PATCH and treats raw schema bodies as optional. The view therefore uses the canonical raw `WorkspaceFile` component reference plus a shared `RequiredPatchBodyAutoSchema` operation refinement in `common/schemas/openapi.py`. Direct generated-schema inspection proves both the body and `path` are required and no patched clone exists.
- Maintainability review identified that the schema refinement did not belong in the request serializer module. A focused `backend/common/schemas/openapi.py` addition was accepted as a review-attributable scope amendment, preserving the already-dirty/protected `backend/common/openapi.py` byte-for-byte while keeping schema behavior in the repository's required `common/schemas` package.
- The backend lane is proportional rather than repository-wide. Risk is bounded by real authenticated traces for both modes, the focused unchanged-service regression lane, full frontend coverage, and all configured fast repository gates.
- An earlier combined wrapper exceeded its time budget while the full frontend suite was still active. Only the wrapper's verified child processes were stopped; the full suite and every repository gate were then rerun independently to successful completion.

## Review record

- PRE plan review: approved after adding the `ProjectStructurePanel.tsx` structural input shadows to the explicit cutover map.
- POST alignment review: approved after the review-attributable schema-module amendment; no remaining findings.
- Correctness review: approved after required PATCH bodies, exact DELETE path length, and broader validation-before-mutation evidence were added.
- Maintainability review: approved after alias/re-export/alternate-owner/runtime-use mutations, structural false-positive removal, operation-specific adapter enforcement, aliased-import detection, and schema-helper cohesion were added.
- Independent final verification: `FINAL_VERIFIED`; 17/17 runtime contract tests, focused frontend/TypeScript checks, focused/live guard checks, generated-schema inspection, 161/161 strict entries, 24/24 protected hashes, and all 27 post-baseline scope paths independently confirmed.
