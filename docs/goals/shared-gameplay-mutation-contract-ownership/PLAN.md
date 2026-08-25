# Shared Gameplay Mutation Contract Ownership — Slice 12 Implementation Plan

**Intent:** Give the identical command-submit and workspace-file request contracts used by Adventure and Challenge runs one backend owner and one generated-contract-aware frontend path.
**Current Behavior:** `adventures.serializers` and `challenges.serializers` independently define the same command, file, path, and rename serializers; the file-create class name alone differs. Schema generation warns that the feature-local `CommandSubmitSerializer` and `WorkspaceFileRenameSerializer` identities collide, and emits parallel `WorkspaceFile`/`WorkspaceFileCreate` plus patched variants for equivalent bodies. The PATCH schemas incorrectly make `path` optional even though both views require it at runtime, while DELETE accepts `path` through query data but does not document the query parameter. The two frontend APIs repeat workspace request aliases, camel-to-snake mapping, and six request-body casts. Workspace interaction types are repeated in feature components, hooks, project-tree utilities, and simulator code, while `CommandExecutionPayload` is independently declared in both Level and Simulator modules.
**Expected Outcome:** `common.serializers` owns the exact reusable request serializers; both feature views import them directly; Adventure's displaced serializer module is deleted and Challenge keeps only its mode-specific run-start serializer. OpenAPI exposes one exact `CommandSubmit`, `WorkspaceFile`, and `WorkspaceFileRename` family, keeps `path` required for POST/PATCH/PUT, documents required DELETE query input, and emits no equivalent feature forks or identity-collision warnings. Generated TypeScript remains the frontend wire truth; one shared gameplay adapter constructs command/file bodies without endpoint casts; one neutral workspace interaction type owner serves features, project-tree UI, and the simulator; and the Level-owned command execution refinement is the sole frontend payload type.
**Target-Perspective Output:** A learner can create, edit, rename, and delete a workspace file in either Adventure or Challenge mode and submit commands exactly as before. Invalid or missing request fields produce the same controlled validation response before a run is mutated. A maintainer inspecting either flow reaches the same request serializer, generated schema, workspace input types, and wire adapter instead of parallel definitions.
**Truth Owner:** Adventure/Challenge services and payload modules retain mode behavior and response truth; `common.serializers` owns shared request validation; generated OpenAPI and `ApiSchemas` own frontend wire shapes; `shared/level/workspaceFileTypes.ts` owns cross-mode workspace interaction inputs; `shared/level/types.ts` owns the generated-compatible command execution refinement; and `shared/level-runtime/runMutationInputs.ts` is the single camelCase/domain-to-wire adapter.
**Contract Boundary:** Feature UI/hook input -> shared workspace/command type -> shared wire adapter -> generated operation body -> Adventure/Challenge view -> common serializer -> unchanged mode service -> unchanged mode response payload.
**Cutover:** Move the four shared serializer classes to `common.serializers`; point both view modules at them; delete Adventure's serializer module and the three shared Challenge classes; annotate PATCH against the required canonical file component rather than drf-spectacular's automatic partial clone; document DELETE `path` as a required query parameter; regenerate both API artifacts; consolidate frontend input/payload declarations and body construction; then add a narrow architecture rule rejecting restoration of feature-local serializers, schema forks, handwritten request aliases, duplicate command payloads, or body casts in the two gameplay APIs.
**Displaced Path:** `backend/adventures/serializers.py`; feature-local `CommandSubmitSerializer`, `WorkspaceFileCreateSerializer`, `WorkspaceFileSerializer`, `WorkspaceFilePathSerializer`, and `WorkspaceFileRenameSerializer`; `WorkspaceFileCreate`/`PatchedWorkspaceFile*` generated forks; feature-local `WorkspaceFileRequest`/`WorkspaceFileRenameRequest`; repeated `WorkspaceFileInput`/`WorkspaceFileRenameInput` plus `CreateFileInput`/`RenameFileInput` structural declarations; the Simulator copy of `CommandExecutionPayload`; and `as ApiRequestBody` in Adventure/Challenge APIs are deleted. No facade or re-export remains.
**Value Density:** This bounded write-path slice removes two live validation owners, corrects a real PATCH/DELETE documentation mismatch, eliminates current schema warnings and parallel generated types, replaces repeated frontend casts with an exact adapter, and reduces drift risk across both primary gameplay modes without changing gameplay logic or UI.
**Acceptance Evidence:** Shared serializer parity tests; real authenticated Adventure and Challenge workspace create/write/rename/delete traces; malformed/missing-field cases proving 400 and unchanged repository state; the existing command-integrity and budget suites for both modes; fresh schema generation showing one component family, required PATCH identity, required DELETE query input, and no relevant collision warnings; compile-time generated-body adoption; focused frontend adapter/API tests; static displaced-path searches; architecture-guard mutation tests; TypeScript and repository gates; and dirty-worktree hash replay.
**Evidence Lane:** Backend contract/unit cases -> real dual-mode API mutation traces -> command regression suites -> generated schema warning/reference inspection -> frontend adapter/API tests -> TypeScript/full frontend suite -> architecture/API/quality gates -> preservation replay -> POST/correctness/maintainability/final verification.
**Kill Criteria:** One backend module defines the four shared request serializers; neither feature owns or re-exports them; Adventure's serializer module is absent; Challenge's serializer module contains only the run-start input; OpenAPI has one exact command/file/rename component family, no `WorkspaceFileCreate` or patched file component, `path` remains required for both PATCH operations, both DELETE operations expose one required string query parameter, and the relevant component-name collision warnings are absent; each frontend API delegates body construction to one shared adapter and contains no handwritten workspace request alias or `as ApiRequestBody`; only one frontend `CommandExecutionPayload`, `WorkspaceFileInput`, and `WorkspaceFileRenameInput` declaration remains, with no structural `CreateFileInput`/`RenameFileInput` shadows; no gameplay service, model, command verification, response payload, cache, route, throttle, reward, UI markup/style, or simulator behavior changes; generated files are generator output only; and no unrelated dirty-worktree byte changes.
**Architecture Slice:** Shared gameplay mutation request ownership only. Response-contract exactness, Story Map/authoring contracts, service consolidation, optimistic-cache behavior, component redesign, simulator algorithms, persistence, and deployment are explicitly deferred.
**Plan Review Gate:** Requires PRE review before preservation capture or implementation.

## Outcome Contract

### Canonical backend inputs

- `CommandSubmitSerializer`: required `command` (maximum 500 characters) plus the existing strict `ClientCommandExecutionSerializer`.
- `WorkspaceFileSerializer`: required `path` (maximum 240), optional `content` (maximum 20,000, blank allowed, whitespace preserved, default empty string).
- `WorkspaceFilePathSerializer`: required `path` (maximum 240), used for runtime DELETE query/body compatibility.
- `WorkspaceFileRenameSerializer`: required `path` and `new_path`, each maximum 240.
- `ChallengeRunStartSerializer` remains feature-owned because it has no Adventure equivalent.

### HTTP and generated-contract behavior

| Operation | Runtime source | OpenAPI request shape |
|---|---|---|
| Submit command | JSON body through shared command serializer | shared required `CommandSubmit` |
| Create file | JSON body through shared file serializer | shared `WorkspaceFile`, `path` required |
| Write file | JSON body through the same shared file serializer | reference the same required `WorkspaceFile`; do not synthesize a partial component |
| Rename file | JSON body through shared rename serializer | shared `WorkspaceFileRename`, both fields required |
| Delete file | existing body-or-query runtime compatibility through shared path serializer | required string `path` query parameter, no DELETE request body |

PATCH is being used as a write command, not a partial resource document: omitting the file identity has always failed at runtime. The schema must describe that existing rule exactly rather than inherit drf-spectacular's generic PATCH optionalization.

### Frontend ownership

- `shared/level/workspaceFileTypes.ts` exports the only `WorkspaceFileInput` and `WorkspaceFileRenameInput`, refined from the generated file/rename field types while keeping the UI-facing `newPath` name.
- `shared/level/types.ts` retains the sole `CommandExecutionPayload`, expressed as the generated client-execution shape with the richer repository snapshot refinement. Simulator construction may contain one documented assertion at its controlled JSON-state boundary; endpoint APIs may not cast request bodies.
- `shared/level-runtime/runMutationInputs.ts` owns `commandSubmitBody`, `workspaceFileBody`, and `workspaceFileRenameBody`; their return types are generated `ApiSchemas` components.
- Adventure and Challenge APIs retain their route/response wrappers but use those shared inputs and adapters.

## Architecture Map

### Files to create

- `backend/common/tests/test_gameplay_mutation_contract.py`
- `frontend/src/shared/level/workspaceFileTypes.ts`
- `frontend/src/shared/level-runtime/runMutationInputs.ts`
- `frontend/src/shared/level-runtime/runMutationInputs.test.ts`
- `docs/goals/shared-gameplay-mutation-contract-ownership/PRE_SLICE_BASELINE.md`
- `docs/goals/shared-gameplay-mutation-contract-ownership/EVIDENCE.md`

### Files to modify

- `backend/common/serializers.py`
- `backend/adventures/views.py`
- `backend/challenges/serializers.py` and `views.py`
- `backend/common/tests/test_bug_regressions.py`, import cutover only
- Generated `frontend/src/shared/api/generated/openapi.json` and `apiTypes.ts`, generator output only
- `frontend/src/shared/level/types.ts`, command payload generated refinement only
- `frontend/src/shared/git/simulator/types.ts` and `engine.ts`, remove the duplicate payload declaration and import/use the canonical refinement
- `frontend/src/shared/git/simulator/workspaceFiles.ts`, shared workspace type import only
- `frontend/src/shared/level/utils/projectFiles.ts`, `components/WorkspaceEditorOverlay.tsx`, and `components/ProjectStructurePanel.tsx`, shared workspace type imports only
- Adventure/Challenge API files and tests
- `frontend/src/features/adventures/hooks/useAdventureRun.ts` and `components/AdventureWorkspaceMain.tsx`, type imports only
- `frontend/src/features/challenges/hooks/useChallengeWorkspaceMutations.ts`, `components/ChallengeWorkspacePanels.tsx`, and `ChallengeWorkspaceMain.tsx`, type imports only
- `frontend/src/shared/level/commandExecution.ts` and `shared/level-runtime/useOptimisticGitCommand.ts`, canonical command payload import only
- `scripts/checks/check_architecture_boundaries.py` and `backend/common/tests/test_architecture_guard_algorithms.py`, one focused ownership rule and its mutation tests

### Files to delete

- `backend/adventures/serializers.py`

### Files to avoid and preserve exactly

- Adventure/Challenge models, services, payloads, selectors, routes, migrations, throttling configuration, command verification, and response serializers
- `backend/common/services/run_workspace.py`, workspace Git mutation implementation, evaluation, practice/progress/reward logic, authentication, and curriculum data
- Simulator command/state/workspace algorithms beyond type imports and the controlled command-payload state assertion
- Query keys, React Query behavior, feature page/session controllers, UI markup, styles, registries, and routing
- API generator/checker logic; generated files must be regenerated, not hand-edited
- All unrelated Slice 1–11 dirty-worktree entries

### Read/write path

`Adventure/Challenge UI -> feature hook -> feature API -> shared body adapter -> generated operation -> feature view -> common request serializer -> unchanged feature/shared service -> unchanged payload/cache consumer`

### Migration/cutover

No data or deployment migration exists. The code/schema cutover is atomic: views switch to the common owner when local serializers disappear; generator output updates after the annotations; frontend APIs adopt the shared adapter before repeated aliases/casts are removed; every internal type consumer switches before duplicate declarations are deleted.

## Task Board

### Task 1: Capture the approved preservation boundary

- **Owner:** Main agent.
- **Files allowed:** New `PRE_SLICE_BASELINE.md` only.
- **Output:** Full dirty manifest with status/bytes/SHA-256; exact hashes for every planned existing target; absence records for additions/deletion target state; protected hashes for services, models, payloads, routes, simulator algorithms, UI/style owners, generator implementation, and prior-slice evidence.
- **Verification:** Recompute every entry before implementation and separate mutable dirty targets (generated artifacts and architecture files) from strict unrelated work.
- **Depends on:** PRE approval.

### Task 2: Establish one backend request owner and exact schema

- **Owner:** Main agent.
- **Files allowed:** Common serializers/tests, two feature view modules, Challenge serializer reduction, Adventure serializer deletion, generated artifacts through the generator, and the narrow architecture rule/tests.
- **Output:** One serializer family; direct imports; correct PATCH/DELETE documentation; no schema forks/collisions; durable displaced-path enforcement.
- **Verification:** Serializer field/default/length tests, real dual-mode workspace endpoint transitions, invalid/no-mutation cases, existing dual-mode command integrity/budget suites, schema regeneration/check, relevant warning capture, Ruff, and architecture mutation tests.
- **Acceptance evidence:** Actual authenticated requests prove both modes still mutate through their original services while invalid data stops before state changes.
- **Depends on:** Task 1.

### Task 3: Consolidate frontend mutation input and payload ownership

- **Owner:** Main agent.
- **Files allowed:** The listed shared types/adapter, Simulator type/import boundary, project-tree input imports including `ProjectStructurePanel.tsx`, feature APIs/tests, and type-only component/hook cutovers.
- **Output:** Generated-compatible command payload; one workspace input owner; one body adapter; no endpoint casts or local request aliases; no component or simulator behavior changes.
- **Verification:** Shared adapter and both API tests; simulator engine/workspace tests; TypeScript; API generated/adoption checks; static symbol/cast searches covering `WorkspaceFile*Input` and the structural `CreateFileInput`/`RenameFileInput` shadows; architecture mutation tests that restore each shadow form.
- **Acceptance evidence:** Both APIs emit byte-equivalent bodies through shared functions and compile directly against the generated operation types.
- **Depends on:** Task 2.

### Task 4: Prove preservation and close reviews

- **Owner:** Main agent.
- **Files allowed:** New `EVIDENCE.md`; approved implementation targets only for attributable fixes.
- **Output:** Backend/API/schema/frontend traces, focused/full results, schema warning audit, displaced-path searches, target diffs/hashes, strict manifest replay, review decisions, and residual-risk statement.
- **Verification:** Focused backend/frontend suites; full frontend suite; proportional backend suite; TypeScript/build/lint/Knip as configured; generated-contract, API usage/type adoption, architecture/docs/quality gates; `git diff --check`; baseline replay; POST/correctness/maintainability/final verification.
- **Acceptance evidence:** Every expected outcome and kill criterion maps to reproducible evidence rather than diff inspection alone.
- **Depends on:** Tasks 1–3.

## Forbidden Moves

- Do not alter gameplay services, state transitions, command verification, response payloads, models, migrations, routes, throttles, rewards, permissions, or caches.
- Do not change workspace or simulator algorithms, UI behavior, markup, styling, navigation, or query policies.
- Do not retain feature-local facades or re-exports for displaced serializers/types.
- Do not make runtime PATCH accept a missing path merely to match the generator; document the existing required identity instead.
- Do not remove existing DELETE body compatibility; document and preserve the frontend's query path.
- Do not hand-edit generated contract artifacts or modify generator implementation.
- Do not generalize this into response-contract, authoring, Story Map, or service-layer work.
- Do not stage, normalize, discard, or overwrite unrelated dirty work.

## Review Gates

1. PRE plan review before baseline capture or implementation.
2. POST alignment review after implementation and evidence draft.
3. Correctness review focused on runtime/schema parity, PATCH/DELETE semantics, validation-before-mutation, generated compatibility, and real dual-mode traces.
4. Maintainability review focused on one-way ownership, deleted facades, naming, import direction, adapter necessity, and durable enforcement.
5. Independent final verifier after findings and evidence metadata are synchronized.
