# Gameplay Success-Response Contract Ownership Implementation Plan

**Intent:** Give Adventure and Challenge success responses honest domain owners and generated-aware frontend projections instead of one mixed `common.openapi` module plus freehand feature response contracts.
**Current Behavior:** `backend/common/openapi.py` owns the five Adventure/Challenge response serializers even though runtime payloads are assembled in the two feature domains. The Adventure payload emits an undocumented duplicate top-level `passed` key in addition to canonical `is_passed`. The Challenge payload always emits `story`, but `ChallengeRunResponseSerializer` omits it. Both run serializers mark many always-present nullable fields optional. `RuntimeStepResponseSerializer` marks always-present terminal fields optional and cannot describe Challenge command `evaluation_result`. Generated OpenAPI repeats those gaps. The two feature type modules contain no generated-schema reference, while their APIs pass fifteen explicit response overrides to `apiOperationRequest`—fourteen non-null handwritten response types plus the generated-compatible destroy `null`.
**Expected Outcome:** `adventures.openapi` and `challenges.openapi` own their schema-only response serializers; `common.openapi` retains only genuinely shared response helpers, including the exact common terminal-step base and run-status schema field. Runtime payload assembly and every response key remain unchanged in the existing payload modules. Adventure documents both the existing top-level `is_passed` and `passed` keys; Challenge documents its always-present nullable `story`; always-present top-level fields are required in OpenAPI; the Challenge command step documents `evaluation_result`; the Adventure command run is an explicit full-run-or-partial-patch union; and the Challenge command run uses a named update component rather than an anonymous dictionary. Generated OpenAPI/TypeScript project those contracts. Adventure/Challenge wire response types compose the generated components and retain only explicit nested domain refinements, rather than redeclaring the whole wire response from scratch. Because the Challenge query cache also stores optimistic local terminal steps that are not HTTP responses, an explicit client-state step union may differ only by the absence of `visualization_snapshot`; full-response API wrappers must use the exact generated-derived `ChallengeRunResponse`, while the existing `ChallengeRun` cache model composes it and owns only that local-step distinction. Existing gameplay screens, commands, workspace mutations, cache behavior, routes, rewards, and persistence behavior remain unchanged.
**Target-Perspective Output:** A maintainer following an Adventure or Challenge success response reaches the feature payload builder, the same feature's OpenAPI module, its generated component/operation, and a generated-derived frontend type. Authenticated run reads, workspace mutations, and verified command submissions return byte-equivalent learner-visible response shapes and the same state transitions. Generated clients see the existing Adventure `passed` alias, the real Challenge `story`, correct requiredness, the Adventure full/partial command-run branches, and the Challenge command-step evaluation field.
**Truth Owner:** `adventures.payloads` and `challenges.payloads` remain the executable value owners. New `adventures.openapi` and `challenges.openapi` modules own domain response schemas. `common.openapi.RuntimeStepResponseSerializer` and `GameplayRunStatusField` own only the genuinely shared step/status primitives. Committed OpenAPI and `apiTypes.ts` are generated projections. Feature `types.ts` modules may refine opaque nested JSON fields but must compose their domain `ApiSchemas` components and may not own a second complete top-level wire shape. The Challenge cache's optimistic/local step union is a client-state contract and must never be used as an API response override.
**Contract Boundary:** Existing domain payload builder -> feature APIView response -> feature-owned schema annotation -> generated OpenAPI component/operation -> generated-derived feature type -> existing query/cache/UI consumer. No runtime response adapter or compatibility DTO is introduced.
**Cutover:** Create the two domain OpenAPI modules; move the five domain response serializers out of `common.openapi`; keep class/component names stable where their semantics stay stable; add an explicit Adventure partial-run component and full/partial union, plus domain-specific Challenge run-update and command-step components; make the common terminal-step base exact; switch view imports directly; add missing properties/requiredness without changing payload behavior; regenerate both API artifacts; convert the five feature response/run declarations and shared `TerminalStep` to generated-derived definitions; remove an explicit API response override only when generated operation inference is proven equivalent; then extend the canonical Gameplay architecture policy to reject common-owned/domain-shadow response serializers, schema regressions, freehand top-level response declarations, opaque command-run shapes, and unapproved API response overrides.
**Displaced Path:** Adventure/Challenge response serializer classes in `backend/common/openapi.py`; the undocumented Adventure `passed` and Challenge `story` fields; optional OpenAPI fields that runtime always emits; opaque Adventure/Challenge command `run` shapes and the Challenge step schema gap; and standalone complete `AdventureRun`, `AdventureLevelLibraryResponse`, `AdventureCommandResponse`, `ChallengeRun`, `ChallengeCommandResponse`, and `TerminalStep` wire declarations. `backend/adventures/serializers.py` remains deleted and must not be recreated or used as a response facade.
**Value Density:** High. This bounded read/response-path slice removes mixed-domain schema ownership, fixes observable generated-contract lies, eliminates full top-level TypeScript redeclarations, makes command response fields discoverable to clients, and makes the prior shared request-contract work symmetrical without touching gameplay algorithms.
**Acceptance Evidence:** Real authenticated Adventure and Challenge GET/workspace/command success traces, including Adventure partial/full command branches and Challenge started/terminal updates; exact envelope, nested `run`, and nested `step` key comparison against feature-owned serializers; post-response serializer validation; before/after database-state evidence for run status, counters, repository state, persisted step, completion/reward/progress records, and workspace mutation state; explicit preservation of Adventure `is_passed` and `passed`; explicit presence/nullability of Challenge `story`; exact OpenAPI properties/required lists, union branches, and operation references; generated TypeScript component/operation inspection; compile-time generated composition of feature types; focused gameplay/API/frontend tests; architecture-guard mutation tests for every displaced path; full proportional frontend/backend gates; protected-region and dirty-worktree preservation replay; and POST/correctness/maintainability/final verification.
**Evidence Lane:** Pre-cutover real endpoint/schema/type capture -> backend domain-owner and authenticated response tests -> generator output inspection -> frontend type/build/consumer tests -> architecture mutation/live checks -> full quality gates -> strict preservation replay -> independent reviews.
**Kill Criteria:** Exactly one definition of each gameplay response serializer in its canonical domain OpenAPI owner; no Adventure/Challenge response serializer or facade remains in `common.openapi`, `adventures.serializers`, `challenges.serializers`, or another backend module; `backend/adventures/serializers.py` stays absent; runtime and documented run top-level keys agree without payload behavior changes; Adventure retains required `is_passed` and `passed`; Challenge has required nullable `story`; every runtime-always-present run/command field is required in OpenAPI; Challenge command step contains `evaluation_result`; Adventure command `run` is a named generated full-run-or-partial-patch union and Challenge command `run` references the named update component with exact per-field presence/nullability; generated artifacts are reproducible generator output; the exact wire response types and shared terminal step visibly compose the expected `ApiSchemas` components with only the exact allowlisted refinements instead of redeclaring complete wire objects; both Challenge full-response API wrappers use `ChallengeRunResponse`, never the client-state `ChallengeRun`; the Challenge client-step union permits only the explicit missing-`visualization_snapshot` optimistic branch; no compatibility alias, re-export facade, response-normalization adapter, broad/keyof omission, primitive omission, `Partial`/`Record` wire overlay, generated/manual intersection that widens a wire shape, or unapproved freehand response override is introduced; payload builders, services, models, routes, request serializers, command verification, state transitions, cache behavior, UI behavior, rewards, migrations, protected mutable-target regions, and unrelated dirty bytes are unchanged. Stop the slice rather than ship if protected-region replay fails, drf-spectacular collapses the Adventure union to an open object, emits relevant warnings, or real branch/state traces contradict the proposed requiredness or preservation contract.
**Architecture Slice:** Gameplay success-response ownership and top-level/schema exactness only. Deep exact typing of repository snapshots, visualization payloads, battle-stage objects, books, scenario context, and every nested presenter dictionary; payload-builder rearchitecture; API client runtime validation; service consolidation; optimistic-cache redesign; and UI/component work are explicitly deferred.
**Plan Review Gate:** Requires PRE review before preservation capture or implementation.

## Outcome Contract

### Exact top-level run responses

- Adventure run keys after cutover: `id`, `status`, `replay`, `stars`, `library_opened`, `is_passed`, `selected_level`, `next_level`, `story`, `chapter_id`, `battle_stage`, `current_level_index`, `total_levels`, `current_wave`, `total_waves`, `passed`, `mastery`, `completed_at`, `current_attempt`, `results`, and `progress`.
- The existing top-level Adventure `passed` alias is preserved and documented alongside canonical `is_passed`; `mastery.passed` remains a distinct nested mastery fact used by the outcome UI. Alias cleanup would be a separate compatibility change, not a schema-ownership refactor.
- Challenge run keys after cutover: `id`, `replay`, `stars`, `status`, `failure_reason`, `completed_at`, `challenge`, `scenario_context`, `chapter`, `story`, `battle_stage`, `difficulty`, `reward_coins`, `variant`, `mastery_progress`, `policy`, `counts`, `scaffolding`, `repository_state`, `visualization`, `expected_state`, `steps`, `next_difficulty`, `sibling_levels`, and `completion`.
- Every listed key is emitted on every full run payload. Nullable values remain nullable but are not optional in generated clients.

### Exact command envelopes

- Adventure command keys remain `run`, `solved`, `stdout`, `stderr`, `exit_code`, `terminal_output`, `command_classification`, `step`, and `command_outcome`; all are required.
- Challenge command keys remain `run`, `command_outcome`, `stdout`, `stderr`, `exit_code`, `command_family`, `diagnostic_metadata`, and `step`; all are emitted and therefore required.
- The shared runtime step base is exactly required `id`, `command_text`, `terminal_output`, and `result_category`.
- Challenge run-history steps add required `command_classification`, `contextual_feedback`, `visualization_snapshot`, and `created_at`.
- Challenge command steps additionally require `evaluation_result`.
- Challenge command `run` is the existing conditional update shape: required `id`, `replay`, `stars`, `status`, `failure_reason`, `completed_at`, `counts`, `repository_state`, and `visualization`. The four transition-only fields are absent while `status == 'started'`; when present, `mastery_progress` is non-null, `sibling_levels` is a non-null list, while `completion` and `next_difficulty` may each be null. Optional presence and nullable value are distinct and must be emitted that way in OpenAPI and TypeScript.
- Adventure command `run` is the explicit union `AdventureRunResponse | AdventureRunPatchResponse`. The partial component has exactly required `partial`, `id`, `status`, and `current_attempt`, with `partial` constrained to literal `true`; `current_attempt` is a required object in that branch. The union must survive generated OpenAPI and TypeScript without becoming an open dictionary.

### Canonical schema identities

- `adventures.openapi.AdventureRunResponseSerializer` -> `AdventureRunResponse`.
- `adventures.openapi.AdventureRunPatchResponseSerializer` -> `AdventureRunPatchResponse`.
- The Adventure command `run` field uses a named `AdventureCommandRunResponse` union with exactly `AdventureRunResponse` and `AdventureRunPatchResponse` references; `adventures.openapi.AdventureCommandResponseSerializer` -> `AdventureCommandResponse`.
- `adventures.openapi.AdventureLevelLibraryResponseSerializer` -> `AdventureLevelLibraryResponse`.
- `common.openapi.RuntimeStepResponseSerializer` -> `RuntimeStepResponse`, containing only the exact shared four-field base.
- `challenges.openapi.ChallengeRunStepResponseSerializer` -> `ChallengeRunStepResponse` and extends the shared step fields with run-history fields; it does not advertise `evaluation_result`.
- `challenges.openapi.ChallengeCommandStepResponseSerializer` -> `ChallengeCommandStepResponse` and contains the run-history fields plus required `evaluation_result`.
- `challenges.openapi.ChallengeCommandRunResponseSerializer` -> `ChallengeCommandRunResponse`, with the exact conditional presence/nullability contract above.
- `challenges.openapi.ChallengeRunResponseSerializer` -> `ChallengeRunResponse`; `challenges.openapi.ChallengeCommandResponseSerializer` -> `ChallengeCommandResponse`.

### Generated-derived frontend types

- `shared/level/types.ts::TerminalStep` derives from `ApiSchemas['RuntimeStepResponse']`.
- `features/adventures/types.ts` imports `ApiSchemas` and defines `AdventureRun`, `AdventureRunPatch`, `AdventureLevelLibraryResponse`, and `AdventureCommandResponse` from their corresponding generated components. The only permitted omitted/refined keys are open-JSON container fields: Adventure run `selected_level`, `next_level`, `story`, `battle_stage`, `mastery`, `current_attempt`, `results`, and `progress`; patch `current_attempt`; library `book` and `run`; command `run`, `step`, and `command_outcome`. A component-reference field may instead be refined only by a type that recursively derives from that same generated component.
- `features/challenges/types.ts` defines exact generated-derived `ChallengeRunResponse`, `ChallengeRunStepResponse`, `ChallengeRunUpdate`, and `ChallengeCommandResponse` wire types. The only permitted omitted/refined keys are Challenge run `challenge`, `scenario_context`, `chapter`, `story`, `battle_stage`, `variant`, `mastery_progress`, `policy`, `counts`, `scaffolding`, `repository_state`, `visualization`, `expected_state`, `steps`, `next_difficulty`, `sibling_levels`, and `completion`; run/command steps `visualization_snapshot`; command run `counts`, `repository_state`, `visualization`, `mastery_progress`, `completion`, `next_difficulty`, and `sibling_levels`; command envelope `run`, `command_outcome`, and `step`.
- `ChallengeRun` is explicitly a client cache model composed from `ChallengeRunResponse` whose sole divergence is `steps: ChallengeStepLog[]`. `ChallengeStepLog` is the union of exact `ChallengeRunStepResponse` and a named optimistic/local step branch that may omit only `visualization_snapshot`. The local branch cannot be imported by either Challenge API module as a response type.
- Existing nested domain types remain when they carry UI semantics that the intentionally broad generated dictionaries do not express. They are refinements, not independent wire owners.
- The guard rejects `keyof` or broad `Omit`, omission of generated primitive fields, `Partial`/`Record` response overlays, complete top-level reconstruction, widening assertions, and replacement by an unrelated generated component. Allowed refinement-key sets are explicit policy constants and are checked against the generated component properties so a new top-level field cannot be silently shadowed.
- API wrappers may name one of those generated-derived refinements as `TResponse` only where opaque nested dictionaries make the raw generated type too broad for existing consumers. The destroy call must use the generated response directly. The architecture guard rejects a custom response type that does not visibly compose the correct generated component.

## Architecture Map

| Concern | Current owner | Required owner after cutover |
|---|---|---|
| Adventure executable response values | `backend/adventures/payloads.py` | unchanged |
| Challenge executable response values | `backend/challenges/payloads.py` | unchanged |
| Adventure documented responses | `backend/common/openapi.py` | `backend/adventures/openapi.py` |
| Challenge documented responses | `backend/common/openapi.py` | `backend/challenges/openapi.py` |
| Shared terminal-step base | broad `backend/common/openapi.py` class | exact shared class in the same module |
| View/schema integration | feature views importing `common.openapi` domain classes | direct domain OpenAPI imports plus shared-only import if needed |
| Generated contract | current committed OpenAPI/types with omissions | regenerated domain projections |
| Feature wire responses | complete handwritten declarations | generated component base plus bounded nested refinements |
| Durable enforcement | request-only Gameplay guard | combined request and response ownership guard |

### Files to create

- `backend/adventures/openapi.py`
- `backend/challenges/openapi.py`
- `backend/common/tests/test_gameplay_response_contract.py`
- `docs/goals/gameplay-success-response-contract-ownership/PRE_SLICE_BASELINE.md`
- `docs/goals/gameplay-success-response-contract-ownership/PRE_SLICE_BASELINE.json`
- `docs/goals/gameplay-success-response-contract-ownership/PRE_SLICE_BASELINE_SUPPLEMENT.json`
- `docs/goals/gameplay-success-response-contract-ownership/EVIDENCE.md`

### Files to modify

- `backend/common/openapi.py` — remove only the five displaced domain classes and make the shared terminal-step base exact.
- `backend/adventures/views.py` and `backend/challenges/views.py` — response-schema import cutover only.
- Generated `frontend/src/shared/api/generated/openapi.json` and `apiTypes.ts` — generator output only.
- `frontend/src/shared/level/types.ts` — `TerminalStep` generated derivation only.
- `frontend/src/features/adventures/types.ts` and `frontend/src/features/challenges/types.ts` — generated-base response/run composition only.
- `frontend/src/features/adventures/api/adventuresApi.ts` — response type imports/overrides only, including removal of the redundant destroy `null` override so generated operation inference is canonical; routes, requests, bodies, and methods are frozen.
- `frontend/src/features/challenges/api/challengeRunsApi.ts` — response type imports/overrides only if exact generated compatibility makes them unnecessary; routes, requests, bodies, and methods are frozen.
- `frontend/src/features/challenges/api/challengesApi.ts` — start/retry full-response overrides must use exact `ChallengeRunResponse`, and the redundant destroy `null` override must be removed so generated operation inference is canonical; command preview/request bodies/routes/methods remain frozen.
- `frontend/src/features/adventures/components/AdventureOutcomeModal.test.tsx` — add only the captured required top-level `passed` and `battle_stage` fixture keys; assertions/rendering remain byte-exact.
- `scripts/checks/architecture_guard/contracts/gameplay.py` and `backend/common/tests/architecture_guard/test_gameplay_policy.py` — additive response ownership policy/tests only.
- `scripts/checks/check_architecture_boundaries.py` — add only the response-checker import, canonical invocation, and one response-ownership rules-text clause after supplemental byte/normalization capture; all other pre-existing bytes remain exact.
- `ARCHITECTURE.md` and `scripts/README.md` — concise ownership documentation only if required by the documentation guard.

### Files to avoid and preserve

- Adventure/Challenge services, models, selectors, URLs, migrations, permissions, throttles, request serializers, workspace service, command verification/evaluation, rewards, and progress writes.
- Both gameplay payload modules, byte-for-byte.
- `backend/adventures/serializers.py` remains absent; `backend/challenges/serializers.py` remains the run-start request owner only.
- `frontend/src/shared/api/httpClient.ts`, generator/checker implementation, query keys, hooks, caches, components, pages, routes, all UI tests except the one named Adventure fixture alignment, styles, and simulator algorithms.
- Deep shared/domain value types outside the explicit generated-base edits.
- All completed prior-slice goal packages and every unrelated dirty path.

### Read/write and integration paths

- **Read path:** authenticated GET/start/retry/workspace response -> domain payload -> APIView -> domain OpenAPI schema -> generated operation -> generated-derived feature type -> existing cache/UI.
- **Write path:** verified command/workspace request path is unchanged; only its success response documentation/type path changes.
- **Contract boundary:** domain response OpenAPI module and generated component/operation.
- **Integration points:** drf-spectacular schema generation, committed generator output, `apiOperationRequest`, existing feature run/command types, React Query inference, the gameplay architecture policy, and the canonical architecture-boundaries command used by fast gates/CI.
- **Migration/cutover:** atomic import/schema/type cutover; no data/deployment migration and no compatibility period.
- **Displaced path:** mixed common domain schemas, response/schema key drift, opaque command-run projections, and standalone top-level frontend wire declarations.
- **Acceptance evidence gate:** real authenticated JSON key sets and serializer validation must agree with committed OpenAPI/generated output before the slice can be called proven.

## Task Board

### Task 1 — Capture the approved preservation and behavior baseline

- **Owner:** Main agent.
- **Files allowed:** New `PRE_SLICE_BASELINE.md` and `PRE_SLICE_BASELINE.json` only.
- **Exact scope:** Record the full dirty manifest with status/bytes/SHA-256; exact hashes for all targets and protected files; absence of both domain OpenAPI additions; protected aggregates for services/models/routes/request contracts/frontend behavior; exact raw-source and AST fingerprints for every protected declaration/statement region inside every mutable target; exact current OpenAPI component properties/required lists/operation refs; exact frontend response declarations/API overrides; and real authenticated Adventure/Challenge GET/workspace/verified-command response key and state traces. The JSON manifest must separately identify strict whole-file paths, mutable target files, protected region identifiers/hashes/lengths/order, generated-artifact semantic manifests, and approved replacement regions.
- **Protected mutable regions:** In `common/openapi.py`, fingerprint every non-gameplay serializer/helper; in both views, every non-import declaration and decorator argument; in feature type modules, every non-response top-level declaration; in both API wrappers, every path/method/query/body expression and non-response generic; in the Gameplay policy/tests, every existing symbol, ordered diagnostic, and pre-slice statement node; in architecture documentation, preserve the exact original prefix/sections outside approved appended ownership prose. For generated artifacts, compare semantic components/operations and generator reproducibility instead of requiring unchanged bytes.
- **Behavior matrix:** Capture Adventure full start/detail/file responses, an unsolved partial command, a wave-transition full command, and a terminal full command; capture Challenge full start/detail/file/retry responses plus started and terminal command updates. For every command branch record exact envelope/`run`/`step` keys and before/after run status, counters, repository state, persisted step, completion/reward/progress rows, and workspace mutation state.
- **Verification:** Parse the JSON manifest with a dedicated replay script/command, replay every whole-file and protected-region count/hash/order assertion, and rerun all pre-cutover behavior cases without repository writes beyond an isolated test database/workspace.
- **Acceptance evidence:** The baseline proves the current schema/runtime gaps, current response bytes, generated gaps, all command response branches, and unrelated-work boundary.
- **Depends on:** PRE approval.
- **Parallel safe:** No.

### Task 2 — Establish domain-owned backend response schemas

- **Owner:** Main agent.
- **Files allowed:** Two new domain OpenAPI modules, `common/openapi.py`, two feature views, and the new response contract test.
- **Exact scope:** Move the five classes without facades; create the canonical component identities named above; retain stable component names; define exact requiredness, Adventure full/partial command-run schemas, and Challenge story/update/step schemas; make the common step base exact; switch direct imports; add authenticated behavior-matrix tests that compare exact envelope/`run`/`step` keys on every Adventure partial/wave-transition/terminal and Challenge started/terminal branch, validate with the canonical serializer, and assert the recorded database/workspace state transitions.
- **Verification:** Focused response contract tests covering every behavior-matrix row; existing Adventure/Challenge command payload/budget and shared mutation tests; Ruff; temporary schema generation and warning audit.
- **Acceptance evidence:** Actual HTTP 200/201 JSON matches canonical owners and unchanged state transitions; Adventure `is_passed`, top-level `passed`, and nested `mastery.passed` remain; Adventure partial/full command branches validate separately; Challenge `story` and command evaluation data remain present.
- **Depends on:** Task 1.
- **Parallel safe:** No.

### Task 3 — Regenerate and derive frontend response projections

- **Owner:** Main agent.
- **Files allowed:** Generated API artifacts through the generator, three listed type modules, all three response API wrappers within their response-only allowance, the one Adventure fixture, and a new baseline supplement JSON before either newly discovered target is edited.
- **Exact scope:** Capture and replay the supplemental hashes/semantic regions for the previously unmapped `challengesApi.ts` and Adventure fixture before editing them. Run the canonical generator; derive terminal/run/library/command wire response types from generated components; retain only the explicit per-type refinement keys listed in the Outcome Contract; separate exact Challenge HTTP steps/full responses from the named optimistic local-step cache union; make both Challenge full-response API modules use `ChallengeRunResponse`; remove the redundant generated-compatible destroy `null` overrides from both Adventure and Challenge entry API modules; add only `passed: true` and `battle_stage: null` to the Adventure fixture; do not omit primitives, use broad/keyof omissions or Partial/Record overlays on wire types, reconstruct a complete top-level response, substitute an unrelated component, or add assertions/adapters/intersections that widen the generated wire shape.
- **Verification:** API-current/usage/type-adoption checks; TypeScript/Vite build; focused and full frontend tests; static AST/text inspection of generated composition and API generics.
- **Acceptance evidence:** Generated components/operations contain corrected fields and requiredness, and existing consumers compile/render without a second full top-level contract.
- **Depends on:** Task 2.
- **Parallel safe:** No.

### Task 4 — Make response ownership durable

- **Owner:** Main agent.
- **Files allowed:** Canonical Gameplay policy/test files, the canonical architecture-boundaries orchestrator within its three exact replacement regions after supplement capture, and narrowly required architecture documentation.
- **Exact scope:** Extend, do not replace, the existing Gameplay request policy. Enforce canonical domain class/component/assignment owners and references, common/displaced absence, exact OpenAPI component properties/requiredness/nullability (including explicit empty-nullable sets for every exact object component)/operation refs, the Adventure named union, the Challenge command-update conditional presence contract, generated-derived exact wire response declarations whose overlay fields equal their exact allowlisted refinement keys, `ChallengeRunResponse` use in both full-response API modules, the one-field-only client cache divergence, correct API override bases, direct generated inference for destroy responses, Adventure alias presence, Challenge story/evaluation presence, no response-return cast/intersection, and no response facade/re-export. Add synthetic mutations for every bypass, including union collapse, optional/non-null drift for each transition-only Challenge field, broad/keyof omission, primitive omission, Partial/Record wire overlay, extra overlay field, complete reconstruction, unrelated component substitution, assignment facade, response-return cast/intersection, manual destroy override, client-state response override, and an extra client/server divergence. Keep the pre-slice request checker AST exact; expose the additive response checker separately; after supplement capture, import/invoke it from the canonical architecture command and add one rules-text clause. Preserve all previous ordered violations/manifest fingerprints and all orchestrator bytes outside the three attributable additions.
- **Verification:** Focused policy mutation tests, complete architecture suite, live checker, Ruff, and prior Slice 13 symbol/equivalence replay as applicable to the changed Gameplay policy owner.
- **Acceptance evidence:** Every displaced path fails synthetically while the real tree and every earlier architecture contract remain green.
- **Depends on:** Task 3.
- **Parallel safe:** No.

### Task 5 — Prove preservation and close independent reviews

- **Owner:** Main agent.
- **Files allowed:** New `EVIDENCE.md`; approved targets only for attributable review fixes.
- **Exact scope:** Capture post-cutover authenticated behavior-matrix traces and state snapshots, serializer module ownership, generated property/required/nullability/union/operation mappings, frontend composition and allowlisted refinements, exact CLI output, focused/full tests, schema warning audit, static displaced-path search, quality gates, diff hygiene, and strict whole-file/protected-region baseline replay. Run POST plan-alignment, correctness, maintainability, and independent final verification; fix material findings and rerun affected evidence.
- **Verification:** Every acceptance item maps to direct command output or immutable fingerprint evidence.
- **Acceptance evidence:** Target-person response evidence across every conditional branch, no duplicate owners, exact generated projection, unchanged gameplay/database/workspace state transitions, preserved mutable-target regions and unrelated bytes, and FINAL_VERIFIED.
- **Depends on:** Tasks 1–4.
- **Parallel safe:** No.

## Forbidden Moves

- Do not reintroduce `backend/adventures/serializers.py` or place response contracts beside the remaining Challenge request serializer.
- Do not edit either gameplay payload module, move payload assembly into serializers, serialize runtime responses through a new adapter, or change service/payload algorithms.
- Do not change request bodies, request serializers, URLs, methods, permissions, throttles, command verification, repository mutation, completion/reward logic, cache behavior, navigation, UI markup/copy/CSS, models, migrations, or data.
- Do not deeply type every JSON dictionary merely to eliminate all frontend refinements in this slice.
- Do not retain common/domain aliases, compatibility classes, re-export facades, duplicate response DTOs, or a transitional dual contract.
- Do not hand-edit generated artifacts or modify generator implementation.
- Do not weaken or replace existing architecture policies/tests/evidence to make the new tree pass.
- Do not stage, normalize, discard, overwrite, or reformat unrelated dirty work.

## Review Gates and Stop Conditions

1. PRE plan review before baseline capture or implementation.
2. Stop before implementation if ownership, byte-exact payload preservation, Adventure full/partial union emission, Challenge conditional update shape, frontend generated-refinement allowance, or dirty-file preservation cannot be made exact.
3. Say `implemented but unproven` if real authenticated Adventure and Challenge success traces cannot be captured.
4. POST alignment review after implementation/evidence draft.
5. Correctness review focused on exact runtime/schema/generated parity, command conditional responses, and behavior/state preservation.
6. Maintainability review focused on domain ownership, no facades, bounded nested refinements, import direction, and policy durability.
7. Independent final verifier after all material findings and evidence metadata are synchronized.
8. Do not mark the broad modernization goal complete after this bounded slice.
