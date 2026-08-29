# Dashboard/Home Summary Contract Ownership Implementation Plan

**Intent:** Make the authenticated Dashboard/Home summary response one exact backend-to-frontend contract instead of allowing runtime JSON, OpenAPI, generated TypeScript, and a handwritten frontend intersection to disagree.

**Current Behavior:** `MetricsService.dashboard_summary()` returns a stable nine-field object with typed KPI, count, streak, chapter-KPI, and retry-trend structures. `DashboardSummaryResponseSerializer` broadly declares most nested objects as dictionaries, incorrectly declares the runtime retry-trend array as a dictionary, and marks `completed_story_slug` optional even though runtime always includes it. Generated OpenAPI and TypeScript repeat those declarations. `shared/progress/types.ts` independently recreates the live shape but makes both completion fields optional, and `homeSummaryApi.ts` intersects the generated response with that handwritten type while overriding the generated operation response.

**Expected Outcome:** `progress/serializers.py` precisely describes the existing Dashboard payload, reusing the completed Stats slice's `RateMetricSerializer`. Generated OpenAPI exposes exact nested components, dynamic chapter keys with typed KPI-set values, required completion fields with a nullable slug, and `retry_trends` as an array. `HomeSummary` becomes an alias of `ApiSchemas['DashboardSummaryResponse']`; `homeSummaryApi.summary()` returns the generated operation response directly. The actual Home entry shims remain exact re-exports of the shared type/API and cannot become shadow DTO or adapter owners. Runtime values, route, operation ID, Home UI, rank, achievements, fixtures' meaning, and gameplay persistence remain unchanged.

**Target-Perspective Output:** A learner loading Home receives the same KPI, rank, streak, mastery, completion, and retry values. A frontend consumer can use `progress_dashboard_retrieve` without a handwritten intersection and sees the exact same required keys and nested wire types returned by an authenticated `/api/progress/dashboard/` request.

**Truth Owner:** `MetricsService.dashboard_summary()` remains the executable value owner. `progress/serializers.py` remains the sole documented Dashboard response-contract owner. Committed OpenAPI and generated TypeScript are projections. `shared/progress/types.ts` exports a generated alias only; it owns no second response DTO.

**Contract Boundary:** `GET /api/progress/dashboard/` returns exactly `kpis`, `chapter_kpis`, `counts`, `completed_story_slug`, `completed_stories`, `streak`, `perfect_clears`, `mastery`, and `retry_trends`. KPI sets contain exact `scr`, `arc`, and `hlcr` rate metrics. Dynamic `chapter_kpis` values use that same KPI-set contract. Counts, streak, and retry rows have exact fields. Every top-level field is required; only the documented rate values and `completed_story_slug`/`last_completed_on` may be null.

**Cutover:** Add exact Dashboard nested serializers beside the existing Progress Stats serializers; replace the loose Dashboard field declarations without changing the service or view. Regenerate OpenAPI and TypeScript through the repository generator. Replace the handwritten `HomeSummary` object with a generated alias, remove `HomeSummaryResult` and the custom response generic, and add only structurally required completion fields to design-preview fixtures. Keep `features/home/types.ts` and `features/home/api/homeApi.ts` byte-identical and enforce their exact re-export-only shapes. Extend the existing Progress summary ownership guard with exact Dashboard serializer/OpenAPI/frontend/direct-return/re-export checks and synthetic bypass tests.

**Displaced Path:** Remove loose Dashboard dictionary schemas, the wrong object-shaped `retry_trends`, optional completion-field declarations, the handwritten `HomeSummary` object and nested helper types, `HomeSummaryResult`, the generated/manual intersection, and the custom response generic. Do not add aliases, adapters, compatibility DTOs, or a second Dashboard serializer.

**Value Density:** High. This corrects an actual array-versus-object API contract defect, removes the remaining Home summary duplicate truth path, reuses the exact contract infrastructure established by the Stats slice, and strengthens a widely consumed shared response without touching query or UI behavior.

**Acceptance Evidence:** Capture authenticated empty and representative non-empty real endpoint responses through the actual URL/view/service. Prove exact raw keys and wire types, a populated dynamic chapter-KPI entry, a retry-trend JSON array/row, required completion keys, serializer validation, exact committed OpenAPI fragments, generated TypeScript, derived frontend alias, and direct operation return. Supporting evidence includes Progress tests, focused rank/Home model/achievement tests, full frontend tests/build, API/architecture/quality gates, reviews, and dirty-worktree preservation.

**Evidence Lane:** Fresh migrated test database -> authenticated empty and seeded real HTTP responses -> exact raw assertions and serializer validation -> committed OpenAPI/generated TypeScript parity -> focused Home/rank consumers -> full proportional gates -> preservation replay -> POST/correctness/maintainability/independent verification.

**Kill Criteria:** One executable Dashboard payload, one Progress-owned serializer family, and one generated frontend response. `retry_trends` is an array of exact rows. `chapter_kpis` has typed dynamic values. Both completion keys are required; nullable fields remain nullable. No loose Dashboard dict field, handwritten Home summary object, `HomeSummaryResult`, response intersection, custom response generic, adapter, compatibility alias, shadow serializer/DTO, or second Dashboard contract exists. The two Home feature shims are exact re-exports and own no declarations, wrapping functions, or runtime behavior. Service, route, operation ID, Home production components, and learner-visible values remain unchanged. The architecture guard rejects every displaced bypass.

**Non-goals:** Splitting `MetricsService`; changing Dashboard arithmetic, query count, or retry-label semantics; renaming `/progress/dashboard/` or `progress_dashboard_retrieve`; changing `get_or_create_player`; changing rank/achievement/Home component behavior; moving Wallet/Shop contracts; altering Stats contract semantics; changing models, migrations, gameplay writes, CSS, markup, copy, or preview values beyond required structural completeness; adding general runtime validation to `httpClient`.

**Risk if Wrong:** Dynamic dictionary values could remain untyped; optionality could drift; serializer validation could coerce rather than prove raw wire types; generated artifacts could be stale; preview fixtures could accidentally change achievement meaning; an adapter or alias could preserve a second truth path. External generated clients will observe a stricter schema, but the corrected structure matches the response the server already returns.

**Architecture Slice:** Dashboard metrics service payload -> exact Progress serializer family -> `DashboardSummaryAPIView` OpenAPI component -> committed OpenAPI -> generated operation response -> shared generated alias/direct API -> exact Home feature re-export shims -> Home/rank/achievement consumers.

**Plan Review Gate:** Requires PRE review before implementation.

## Exact Response Contract

| Object | Required fields | Types |
|---|---|---|
| Dashboard summary | `kpis`, `chapter_kpis`, `counts`, `completed_story_slug`, `completed_stories`, `streak`, `perfect_clears`, `mastery`, `retry_trends` | exact objects/list; slug nullable |
| KPI set | `scr`, `arc`, `hlcr` | `RateMetric` references |
| Rate metric | `value`, `numerator`, `denominator` | nullable number, integer, integer |
| Chapter KPI map | dynamic chapter-number string keys | values are KPI sets |
| Counts | `started`, `completed`, `failed`, `abandoned` | integers |
| Streak | `current`, `longest`, `last_completed_on` | integers and nullable ISO date |
| Retry trend row | `level_title`, `attempts`, `retries`, `label` | string, integer, integer, string |

## Files to Create

- `backend/progress/tests/test_dashboard_summary_api.py`
- `docs/goals/dashboard-summary-contract-ownership/PRE_SLICE_BASELINE.md`
- `docs/goals/dashboard-summary-contract-ownership/EVIDENCE.md`

## Files to Modify

- `backend/progress/serializers.py`
- `frontend/src/shared/api/generated/openapi.json` — generator-only
- `frontend/src/shared/api/generated/apiTypes.ts` — generator-only
- `frontend/src/shared/progress/types.ts`
- `frontend/src/shared/progress/homeSummaryApi.ts`
- `frontend/src/features/home/preview/fixtures.ts` — required completion fields only
- `scripts/checks/check_architecture_boundaries.py` — additive Dashboard ownership enforcement
- `backend/common/tests/test_architecture_guard_algorithms.py` — additive bypass tests
- this goal package

## Files to Avoid

- `backend/progress/services/metrics.py`
- `backend/progress/views.py` and `backend/progress/urls.py`
- `backend/common/openapi.py`
- Stats response fields/semantics and `backend/progress/tests/test_stats_summary_api.py`
- `scripts/api/api_contract.py` and generator wrappers
- `frontend/src/shared/api/httpClient.ts`
- `frontend/src/features/home/types.ts` and `frontend/src/features/home/api/homeApi.ts` — protected exact re-export-only integration shims
- Home production components/models, rank/achievement implementation, styles, markup, and copy
- models, migrations, authentication, permissions, and gameplay write services
- all completed Slice 1-6 implementation/evidence files except the two additive shared guard files and already-shared generated/serializer targets

## Task Board

### Task 1 — Freeze the Pre-Cutover Contract and Worktree

**Owner:** Main agent

**Input:** PRE-aligned plan and the dirty worktree after completed Slice 6.

**Files allowed:** `docs/goals/dashboard-summary-contract-ownership/PRE_SLICE_BASELINE.md` only.

**Files forbidden:** every production, test, generated, guard, prior-goal, and integration-shim file.

**Exact scope:** Capture the entire dirty manifest with byte hashes after PRE approval and before implementation. Record target/protected hashes, exact additive shared-file line counts/numstats, authenticated empty response, false Dashboard OpenAPI/generated shape, handwritten intersection, exact hashes/content of both Home feature shims, and currently passing-but-insufficient guards. Reparse the manifest immediately. Shared serializer/generated/guard targets inherit completed Stats changes; their complete current bytes become the Slice 7 baseline and only planned additive/exact Dashboard deltas are allowed.

**Output:** Reproducible preservation and semantic baseline.

**Verification:** Reparse the manifest count/hashes and replay the authenticated empty response without repository edits.

**Acceptance evidence:** Every prior-slice byte is protected, and the array/object plus optionality drift is captured before cutover.

**Depends on:** PRE plan review.

**Parallel safe:** No.

### Task 2 — Establish the Exact Progress-Owned Dashboard Contract

**Owner:** Main agent

**Input:** Task 1 baseline and current `dashboard_summary()` payload.

**Files allowed:** `backend/progress/serializers.py`, `backend/progress/tests/test_dashboard_summary_api.py`.

**Files forbidden:** service, view, URL, common OpenAPI, models/migrations, Stats endpoint test, frontend, generated, guards, and prior evidence.

**Exact scope:** Add exact KPI-set, counts, streak, and retry-row serializers and replace only the loose fields inside `DashboardSummaryResponseSerializer`. Reuse `RateMetricSerializer` byte-for-byte. Add authenticated endpoint tests for an empty account and a representative account with two real challenge runs so chapter KPIs and retry-trend rows are populated. Assert raw JSON keys/types/date format/list shape before serializer validation. Do not change service, view, route, models, or Stats fields.

**Output:** One exact Progress-owned backend Dashboard response contract.

**Verification:** `python -m pytest backend/progress/tests/test_dashboard_summary_api.py backend/progress/tests/test_stats_summary_api.py -q`; scoped Ruff; temporary schema generation.

**Acceptance evidence:** Empty and populated real HTTP payloads validate and expose exact required/nested types, including a typed dynamic chapter entry and retry array row.

**Depends on:** Task 1.

**Parallel safe:** No.

### Task 3 — Regenerate and Remove the Frontend Duplicate Contract

**Owner:** Main agent

**Input:** Exact Task 2 serializer schema.

**Files allowed:** generated `openapi.json`, generated `apiTypes.ts`, `frontend/src/shared/progress/types.ts`, `frontend/src/shared/progress/homeSummaryApi.ts`, and `frontend/src/features/home/preview/fixtures.ts` for required completion fields only.

**Files forbidden:** generator implementation, HTTP client, Home feature shims, production consumers, rank/achievement logic/tests, Stats frontend types/API, and all other fixtures/tests.

**Exact scope:** Run the repository generator. Replace `shared/progress/types.ts` with the generated `HomeSummary` alias. Remove `HomeSummaryResult` and the custom response generic so `homeSummaryApi.summary()` returns the operation-generated response directly. Add `completed_story_slug: null` and `completed_stories: []` to preview fixtures only where the exact required contract exposes omissions, preserving preview achievement meaning. Do not hand-edit generated artifacts. Preserve the pre-existing Slice 6 portions of shared generated files exactly outside generator-attributable Dashboard component/order changes.

**Output:** One generated frontend Dashboard contract reaching consumers through unchanged feature shims.

**Verification:** API-current check, focused TypeScript build, rank/Home model/achievement tests, and exact byte-hash comparison of both feature shims.

**Acceptance evidence:** Generated response, shared alias, direct API, and exact re-export shims form one path with no manual response definition.

**Depends on:** Task 2.

**Parallel safe:** No.

### Task 4 — Make the Dashboard Cutover Durable

**Owner:** Main agent

**Input:** Completed backend/generated/frontend cutover.

**Files allowed:** `scripts/checks/check_architecture_boundaries.py`, `backend/common/tests/test_architecture_guard_algorithms.py`.

**Files forbidden:** every other file; earlier checks/tests may not be deleted, renamed, weakened, or rewritten.

**Exact scope:** Extend the existing Progress summary architecture infrastructure, reusing its AST/type/OpenAPI helpers. Enforce exact Dashboard serializer constructors/options, exact OpenAPI properties/requiredness/primitives/nullability/date/array/dynamic-value references, the generated-only `HomeSummary` alias, direct API return, and absence of intersections/adapters/shadows. Enforce `features/home/types.ts` as the exact type re-export and `features/home/api/homeApi.ts` as the exact API re-export, with no local declaration or wrapper. Scan relevant production sources and add synthetic tests for wrong retry shape, loose/dynamic KPI values, optional completion fields, handwritten aliases/intersections, indirect adapters, and shadow declarations/wrappers in each feature shim. Preserve the full Slice 6 guard baseline additively: final numstat may increase additions but may not increase deletions, and all prior 21 algorithm tests must remain and pass.

**Output:** Durable one-way Dashboard contract ownership through the real Home import path.

**Verification:** focused architecture algorithms, live architecture/CSS checks, Ruff, and additive shared-file comparison against Task 1.

**Acceptance evidence:** Synthetic bypasses fail, live sources pass, and every earlier Stats/architecture rule remains exercised.

**Depends on:** Task 3.

**Parallel safe:** No.

### Task 5 — Prove the Cutover and Close Reviews

**Owner:** Main agent

**Input:** Integrated Tasks 1-4 and preservation baseline.

**Files allowed:** `docs/goals/dashboard-summary-contract-ownership/EVIDENCE.md`, plus only task files required for a reviewed correction.

**Files forbidden:** unrelated/prior-slice files, protected shims, services, routes, models, migrations, production Home UI, and unreviewed scope expansions.

**Exact scope:** Capture empty and representative authenticated HTTP/serializer/OpenAPI/type evidence. Run focused Dashboard/Progress tests, focused rank/Home model/achievement tests, full frontend tests/lint/Knip/build, API-current/usage/type checks, architecture/CSS/Ruff/Django/diff/fast-quality gates, full backend if feasible, and preservation replay. Strictly replay every Task 1 manifest entry except planned targets; shared serializer/generated/guard files must show only attributable Dashboard additions/replacements atop their frozen Slice 6 bytes, and both feature shims must match exact Task 1 hashes. Record any bounded timeout honestly. Run POST plan, correctness, maintainability, and independent verifier reviews; fix material findings and rerun affected gates.

**Output:** Final evidence package with direct consumer-path proof and review closure.

**Verification:** Every command/result in `EVIDENCE.md` is rerunnable; terminal hashes/counts match the baseline rules.

**Acceptance evidence:** Authenticated exact runtime/schema/type parity, unchanged Home behavior, no displaced/shadow path, clean reviews, and exact prior-work preservation.

**Depends on:** Tasks 1-4.

**Parallel safe:** No.

## Review and Stop Conditions

- Stop before implementation if PRE review finds unclear ownership, a second contract, unsafe dirty-worktree overlap, or insufficient real-path evidence.
- Report `implemented but unproven` if authenticated empty and populated HTTP responses cannot be captured.
- Do not accept generated consistency or TypeScript compilation alone; both already pass with the wrong `retry_trends` structure.
- Do not change runtime output to satisfy the false schema.
- Do not hand-edit generated files, add response adapters, or preserve the handwritten intersection.
- Do not change preview semantics while adding required structural fields.
- Do not mark the broad modernization goal complete after this slice.
