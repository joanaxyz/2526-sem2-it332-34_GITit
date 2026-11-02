# Stats Summary Contract Ownership Implementation Plan

**Intent:** Make the authenticated Stats summary response one honest backend-to-frontend contract instead of allowing runtime JSON, OpenAPI, generated TypeScript, and a handwritten frontend intersection to describe different payloads.

**Current Behavior:** `MetricsService.stats_summary()` returns `skill_profile`, `activity_trend`, and `headline`. The schema-only `StatsSummaryResponseSerializer` in `common/openapi.py` instead advertises `skill_profile`, `activity`, `headlines`, and optional `totals`; generated OpenAPI and `ApiSchemas['StatsSummaryResponse']` faithfully repeat that false shape. `statsApi.ts` then intersects the generated response with a separately handwritten `StatsSummary`, so TypeScript accepts both incompatible shapes while `httpClient` merely casts the actual JSON. All in-repository runtime consumers and fixtures use the service's singular/current names. `progress/serializers.py` is an unused, incomplete progress-contract path while the active Dashboard and Stats response contracts live in `common`; Wallet also lives there because Shop response schemas nest it.

**Expected Outcome:** `progress/serializers.py` owns the Dashboard and Stats response contracts, replacing its stale unused path. Its Stats contract precisely describes the existing service payload and nested fields. Generated OpenAPI and TypeScript expose `activity_trend` and `headline` only. Feature-level Stats types are indexed aliases derived from `ApiSchemas['StatsSummaryResponse']`; `statsApi.summary()` uses the operation's generated response directly, with no custom response override or intersection. The shared Wallet response contract remains in `common/openapi.py` because Shop schemas nest it. The authenticated endpoint's runtime JSON and learner-visible Home output remain unchanged.

**Target-Perspective Output:** A frontend consumer can inspect `progress_stats_retrieve`, use its generated response type, and receive the same exact keys and nested values from an authenticated `/api/progress/stats/` request without handwritten refinements. A learner loading Home continues to see the same skill, activity, headline, KPI, profile, and achievement values because the runtime service payload is not renamed or adapted.

**Truth Owner:** `MetricsService.stats_summary()` remains the executable value owner. `progress/serializers.py` becomes the sole documented Stats and Dashboard response-contract owner; the shared Wallet/Shop contract stays in `common`. The committed OpenAPI and `apiTypes.ts` are generated projections of the Stats backend contract. `features/stats/types.ts` may export derived aliases only; it does not own a second response shape.

**Contract Boundary:** `GET /api/progress/stats/` returns exactly `{ skill_profile, activity_trend, headline }`. `skill_profile` contains `{ key, label, hint, value, command }`; `activity_trend` contains `{ date, levels_completed, commands_run }`; `headline` contains the ten current fields, with typed `finish_rate`, `boss_floors`, and `comebacks` objects. `StatsSummaryResponseSerializer`, `ApiSchemas['StatsSummaryResponse']`, `ApiResponseBody<'progress_stats_retrieve'>`, `StatsSummary`, and `statsApi.summary()` must describe that same structure without intersection, cast override, alias key, or compatibility DTO.

**Cutover:** Move the active Dashboard and Stats response serializers from `common/openapi.py` into the already-existing Progress serializer module; replace its unused incomplete dashboard serializer. Keep Wallet in `common` to avoid a reverse `common -> progress` dependency from the Shop response family. Expand the Stats serializer into precise nested serializers, update the Progress view imports, regenerate OpenAPI/types, derive frontend Stats aliases from the generated response, and remove `StatsSummaryResult` plus the custom response generic. The service, route, and JSON field names do not change.

**Displaced Path:** Remove `StatsSummaryResponseSerializer`, `DashboardSummaryResponseSerializer`, and the unused `RateMetricSerializer` from `common/openapi.py`; remove the stale `DashboardSummarySerializer`; remove OpenAPI-only `activity`/`headlines`/`totals`; remove the handwritten Stats response object and the `ApiSchemas & StatsSummary` intersection. Keep the shared `WalletSummaryResponseSerializer` canonical in `common`; do not duplicate it in Progress. Do not retain aliases or a transitional dual Stats schema.

**Value Density:** High. One small boundary cut removes a real runtime/schema lie, eliminates a duplicate TypeScript truth path, activates an existing domain-owner module, improves generated nested types, and adds direct authenticated contract evidence without changing product behavior.

**Acceptance Evidence:** Capture a real authenticated request/response trace against an isolated migrated test database showing HTTP 200, exact top-level keys, 14 typed activity points, exact headline keys, absence of `activity`/`headlines`/`totals`, and successful validation by the documented Stats serializer. Show the committed OpenAPI component has the same exact properties and `progress_stats_retrieve` resolves to it. Show generated TypeScript has the precise nested response, the feature aliases derive from it, and the runtime API wrapper has no response override. Supporting evidence includes focused/full tests, TypeScript build, API-current checks, architecture guards, and a preservation audit.

**Evidence Lane:** Authenticated DRF `APIClient` request through the real URL/view/service on a fresh in-memory migrated database; committed OpenAPI/generated-type inspection; frontend build and focused Home/Stats consumer tests. No design fixture is accepted as proof of the HTTP contract.

**Kill Criteria:** One executable service payload, one Progress-owned documented response contract, and one generated frontend response shape. Exact Stats keys are `skill_profile`, `activity_trend`, and `headline`. No `activity`, `headlines`, or `totals` property remains in `StatsSummaryResponse`; no Stats response object literal remains in `features/stats/types.ts`; no `StatsSummaryResult`, generated/manual intersection, custom `TResponse`, runtime adapter, compatibility alias, or second Stats serializer exists. `MetricsService.stats_summary`, the URL, and visible Home behavior remain unchanged. The architecture guard makes these conditions durable.

**Non-goals:** Renaming the working runtime payload to match the false schema; changing metrics arithmetic/query behavior; making the Dashboard summary schema fully precise; moving the shared Wallet/Shop response family; repairing the separate handwritten Home summary intersection; adding general runtime JSON validation to `httpClient`; reorganizing every serializer in `common/openapi.py`; changing routes, permissions, database models/migrations, UI markup, copy, CSS, or design fixtures.

**Risk if Wrong:** A schema-only correction can still silently widen or make fields optional, generated artifacts can be stale, moving serializers can break schema imports, or an apparently convenient compatibility intersection can preserve the lie. External clients generated from the old schema may see a compile-time change, but those documented fields never existed at runtime; adding aliases would create a second unsupported contract rather than compatibility.

**Architecture Slice:** Progress service payload -> Progress-owned response serializer -> `StatsSummaryAPIView` OpenAPI component -> committed OpenAPI -> generated operation response -> derived feature aliases -> Home consumers.

**Plan Review Gate:** Requires PRE review before execution.

## Current Architecture Map

| Concern | Current path | Required owner after cutover |
|---|---|---|
| Executable Stats values | `backend/progress/services/metrics.py::MetricsService.stats_summary` | unchanged |
| Progress HTTP adaptation | `backend/progress/views.py::StatsSummaryAPIView` | unchanged view, Progress-owned import |
| Documented Stats response | `backend/common/openapi.py::StatsSummaryResponseSerializer` | `backend/progress/serializers.py` |
| Generated schema | `frontend/src/shared/api/generated/openapi.json` | generated from Progress serializer |
| Generated operation/type | `frontend/src/shared/api/generated/apiTypes.ts` | generated from OpenAPI |
| Feature Stats type | handwritten `frontend/src/features/stats/types.ts` | derived indexed aliases only |
| Runtime request | overridden `frontend/src/features/stats/api/statsApi.ts` | generated operation response directly |
| Product read path | `HomePage -> statsApi.summary -> HomeHubView -> Profile/Overview` | unchanged |
| Existing contract guard | API current/usage/type-adoption checks | retained plus Stats ownership guard |

## Exact Response Contract

| Object | Required fields | Types/constraints |
|---|---|---|
| Stats summary | `skill_profile`, `activity_trend`, `headline` | no additional compatibility top-level fields |
| Skill axis | `key`, `label`, `hint`, `value`, `command` | strings; `value` is number or null |
| Trend point | `date`, `levels_completed`, `commands_run` | ISO date string and integers |
| Rate metric | `value`, `numerator`, `denominator` | number/null plus integers |
| Scoped count | `value`, `scope` | integer plus string |
| Headline | `levels_completed`, `finish_rate`, `accuracy`, `boss_floors`, `comebacks`, `perfect_clears`, `day_streak`, `longest_streak`, `gitcoins`, `commands_run` | exact nested contracts; `accuracy` number or null |

## Files to Create

- `backend/progress/tests/test_stats_summary_api.py`
- `docs/goals/stats-summary-contract-ownership/PRE_SLICE_BASELINE.md`
- `docs/goals/stats-summary-contract-ownership/EVIDENCE.md`

## Files to Modify

- `backend/progress/serializers.py`
- `backend/progress/views.py`
- `backend/common/openapi.py` — exact displaced Progress serializer/helper removals only
- `frontend/src/shared/api/generated/openapi.json` — generated only
- `frontend/src/shared/api/generated/apiTypes.ts` — generated only
- `frontend/src/features/stats/types.ts`
- `frontend/src/features/stats/api/statsApi.ts`
- `frontend/src/features/home/components/home-stats/homeStatsModel.test.ts` — type-fixture completeness only if the exact generated contract exposes a pre-existing omission
- `scripts/checks/check_architecture_boundaries.py` — additive Stats ownership guard only
- `backend/common/tests/test_architecture_guard_algorithms.py` — additive guard tests only
- this goal package

## Files to Avoid

- `backend/progress/services/metrics.py`
- `backend/progress/urls.py`
- `scripts/api/api_contract.py` and generator wrappers
- `frontend/src/shared/api/httpClient.ts`
- all Home production components/models, fixtures, styles, and tests other than the single conditionally allowed type-fixture correction above
- Dashboard/Home summary frontend types and API wrappers
- authentication, permissions, settings, models, and migrations
- all completed Slice 1-5 implementation/evidence files outside the additive shared guard files

## Source, Read, Write, and Integration Paths

- **Source of truth:** current `MetricsService.stats_summary()` payload semantics.
- **Read path:** authenticated `GET /api/progress/stats/` -> player resolution -> metrics service -> response -> generated operation typing -> React Query Home read -> Profile/Overview consumers.
- **Write path:** none; this endpoint is read-only and this slice changes no persisted data.
- **Contract boundary:** Progress serializer/OpenAPI component and generated `progress_stats_retrieve` response.
- **Integration points:** DRF Spectacular generation, generated TypeScript renderer, `statsApi.summary`, React Query inference, Home view/model/profile consumers.
- **Migration/cutover:** direct schema/type ownership replacement; runtime JSON remains stable.
- **Displaced path:** false schema fields, common-owned Progress serializers, stale incomplete Progress serializer, handwritten response shape, response intersection/override.
- **Acceptance evidence gate:** authenticated real endpoint JSON validates against the documented serializer and matches committed/generated properties exactly.

## Task Board

### Task 1 — Freeze the Pre-Cutover Contract and Worktree

**Owner:** Main agent

**Input:** Approved plan and current dirty worktree.

**Files allowed:** `docs/goals/stats-summary-contract-ownership/PRE_SLICE_BASELINE.md` only.

**Files forbidden:** all production, test, generated, shared guard, and prior-slice files.

**Exact scope:** Record the entire current dirty manifest with byte hashes; hash all target and protected files; record current line counts/diffs for the two additive shared guard files; capture an authenticated in-memory-database endpoint trace; record the false OpenAPI/generated properties and the passing-but-insufficient API guards. This baseline happens after PRE approval and before implementation.

**Output:** Reproducible preservation and semantic baseline.

**Verification:** Reparse the manifest and confirm its entry count; rerun the authenticated trace without editing repository state.

**Acceptance evidence:** The baseline proves the actual runtime contract and names the exact mismatch before cutover.

**Depends on:** PRE plan review.

**Parallel safe:** No.

### Task 2 — Establish Progress-Owned Response Contracts

**Owner:** Main agent

**Input:** Baseline and current service payload.

**Files allowed:** `backend/progress/serializers.py`, `backend/progress/views.py`, `backend/common/openapi.py`, `backend/progress/tests/test_stats_summary_api.py`.

**Files forbidden:** metrics service, URLs, models, migrations, settings, other domain serializers/views/tests.

**Exact scope:** Replace the unused incomplete serializer module with the active Dashboard and Stats response contracts. Preserve Dashboard schema behavior while moving ownership; retain Wallet in `common` and import it separately in the Progress view. Define exact Stats nested serializers and exact required fields. Remove only the displaced Dashboard/Stats response serializers and now-owned `RateMetricSerializer` from `common`. Add an authenticated endpoint contract test that validates the real payload and rejects the old top-level shape.

**Output:** One Progress-owned backend response contract matching real JSON.

**Verification:** `python -m pytest backend/progress/tests/test_stats_summary_api.py -q`; Ruff on changed Python; generate an OpenAPI schema to a temporary path if useful.

**Acceptance evidence:** A real authenticated response is HTTP 200, has exact keys/nested structure, has 14 trend points for an empty account, excludes old keys, and validates with `StatsSummaryResponseSerializer`.

**Depends on:** Task 1.

**Parallel safe:** No.

### Task 3 — Regenerate and Remove the Frontend Duplicate Contract

**Owner:** Main agent

**Input:** Correct backend serializer schema.

**Files allowed:** generated `openapi.json`, generated `apiTypes.ts`, `frontend/src/features/stats/types.ts`, `frontend/src/features/stats/api/statsApi.ts`, and—only if TypeScript proves the need—`frontend/src/features/home/components/home-stats/homeStatsModel.test.ts`.

**Files forbidden:** generator implementation, HTTP client, all Home production files/fixtures/styles, all other Home tests, and other API/type wrappers.

**Exact scope:** Run the repository generator; do not hand-edit generated files. Replace handwritten Stats response declarations with `ApiSchemas['StatsSummaryResponse']` and indexed element aliases. Remove `StatsSummaryResult`, the intersection, and the custom response generic so the operation-generated response flows directly through `statsApi.summary()`. If the stricter exact type exposes synthetic skill rows missing the runtime-required `command`, add only those missing fixture fields; do not loosen the generated contract or change test behavior.

**Output:** One generated frontend contract with derived feature aliases.

**Verification:** `python scripts/check_api_contract.py`; `npm --prefix frontend run build`; focused Home Stats tests; `rg` proves no displaced fields/intersection in the Stats boundary.

**Acceptance evidence:** Generated response properties and actual authenticated JSON agree exactly; consumers compile without a manual response override.

**Depends on:** Task 2.

**Parallel safe:** No.

### Task 4 — Make the Ownership Cutover Durable

**Owner:** Main agent

**Input:** Completed backend/generated/frontend cutover.

**Files allowed:** `scripts/checks/check_architecture_boundaries.py`, `backend/common/tests/test_architecture_guard_algorithms.py`.

**Files forbidden:** all other files; prior checks/tests may not be deleted or weakened.

**Exact scope:** Add a focused Stats contract ownership check that confirms the exact OpenAPI top-level properties, Progress serializer ownership, absence from `common`, derived-only feature types, direct generated operation response, and absence of the old/intersection/adapter paths. Add synthetic tests for each bypass. Preserve all earlier checker behavior and wording additively.

**Output:** CI-enforced one-way contract ownership.

**Verification:** focused architecture algorithm tests, live architecture checker, CSS checker, Ruff, and preservation comparison against the shared-file baseline.

**Acceptance evidence:** Synthetic bypasses fail and the live tree passes without weakening earlier architecture contracts.

**Depends on:** Task 3.

**Parallel safe:** No.

### Task 5 — Prove the Cutover and Close Reviews

**Owner:** Main agent

**Input:** Integrated cutover and PRE baseline.

**Files allowed:** `docs/goals/stats-summary-contract-ownership/EVIDENCE.md` plus task files for corrections required by review.

**Files forbidden:** unrelated/preserved files.

**Exact scope:** Capture the authenticated post-cutover request/response/serializer trace, exact committed OpenAPI properties, generated TypeScript snippet, and no-duplicate-path search. Run focused and full proportional gates: Progress contract tests, full backend suite if feasible, focused and full frontend tests, full ESLint, Knip, TypeScript/Vite build, API-current/usage/type-adoption checks, architecture/CSS checks, fast quality suite, documentation check, diff hygiene, and worktree preservation replay. Run POST plan, correctness, maintainability, and independent verifier reviews; fix material findings and rerun affected gates.

**Output:** `EVIDENCE.md` with authoritative contract and preservation proof.

**Verification:** Every recorded command is rerunnable and every acceptance claim points to direct output.

**Acceptance evidence:** A consumer-facing authenticated trace, committed schema/type parity, unchanged learner behavior evidence, no displaced path, clean reviews, and exact pre-existing-work preservation.

**Depends on:** Tasks 1-4.

**Parallel safe:** No.

## Review and Stop Conditions

- Stop before implementation if PRE review finds unclear ownership, a dual-contract transition, insufficient real-path evidence, or unsafe overlap with the dirty worktree.
- Stop and report `implemented but unproven` if an authenticated endpoint trace cannot be captured.
- Do not accept passing `api:check`, TypeScript, or unit tests alone as proof; they currently pass while the schema is false.
- Do not change the runtime service payload to satisfy the incorrect schema.
- Do not add compatibility response keys, a normalization adapter, a second DTO, or a temporary intersection.
- Do not hand-edit generated artifacts.
- Do not call the broad modernization goal complete after this bounded slice.
