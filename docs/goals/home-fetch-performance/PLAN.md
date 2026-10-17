# Home Fetch Performance Implementation Plan

**Intent:** Make authenticated Home loads and activity-range changes do materially less database work without changing the data players see.
**Current Behavior:** Home requests dashboard and a range-scoped full stats summary; every range change recomputes invariant headlines and skills, while command-step metrics use a three-parent `OR` join that scans the command-step table.
**Expected Outcome:** Command-step metrics use one indexed player ownership path, initial Home data remains contract-compatible, and range changes fetch only the activity series.
**Target-Perspective Output:** A player sees the same Profile, Progress, and Skills values, while Home and range changes finish with fewer queries and no command-step table scan.
**Truth Owner:** `CommandStep.player` owns denormalized immutable step ownership; `MetricsService.stats_summary` owns invariant stats plus the default activity window; `MetricsService.activity_summary` owns range-dependent activity.
**Contract Boundary:** Django progress serializers/views -> generated OpenAPI/TypeScript -> `statsApi` -> Home React Query composition.
**Cutover:** Backfill and require `CommandStep.player`, redirect `_player_steps` to it, add the activity endpoint, and redirect non-default range changes from the full stats endpoint to the activity endpoint.
**Displaced Path:** The related-parent `OR` ownership query and range-keyed full stats query are deleted.
**Value Density:** One indexed lookup replaces the growing table scan; a range change drops from the full sixteen-query stats path to the four activity aggregation queries.
**Acceptance Evidence:** Query-plan evidence shows indexed `CommandStep.player` access; focused backend API tests prove payload parity and player scoping; frontend tests prove initial summary and range-only fetch behavior; generated-contract checks and builds pass.
**Evidence Lane:** Django migrations/checks, progress/practice tests, query-count and explain probes, generated API checks, frontend unit tests and build.
**Kill Criteria:** No `_player_steps` parent-join `OR`; no Home stats key containing the selected range; no second implementation of activity bucketing; invalidating the stats root also invalidates cached activity windows.
**Architecture Slice:** Home progress reads and command-step ownership only.
**Plan Review Gate:** PRE review required before execution.

## Architecture Map

### Files to create

- `backend/practice/migrations/0003_commandstep_player.py`
- focused tests for command-step ownership and stats activity
- `docs/goals/home-fetch-performance/GOAL.md`
- `docs/goals/home-fetch-performance/PRE_REVIEW.md`

### Files to modify

- `backend/practice/models.py`
- three production command-step writers
- `backend/progress/services/metrics.py`
- `backend/progress/serializers.py`
- `backend/progress/views.py`
- `backend/progress/urls.py`
- generated OpenAPI and TypeScript contracts
- `frontend/src/features/stats/api/statsApi.ts`
- `frontend/src/shared/api/queryKeys.ts`
- `frontend/src/features/home/pages/HomePage.tsx`

### Files to avoid

- authentication/session services and contracts
- gameplay result semantics
- dashboard response shape
- component presentation and styling
- deployment plan configuration

### Source of truth and paths

- Ownership write path: gameplay command processors -> `CommandStep.player`.
- Metrics read path: `MetricsService._player_steps` -> indexed player column.
- Activity read path: `/progress/stats/activity/?window=...` -> generated client -> range child query under `statsSummary`.
- Migration/cutover: nullable add, deterministic backfill from exactly one parent, then non-null plus `(player, created_at)` index.
- Evidence gate: identical endpoint values, four-query activity endpoint, and indexed explain plan.

## Task Board

### Task 1: Make command-step ownership directly indexable

- Modify the model, three production writers, migration, and focused integrity tests.
- Preserve the existing exactly-one-parent constraint.
- Verify migration round-trip, model tests, player-scope tests, and query plan.

### Task 2: Separate range-dependent activity

- Add one serializer, service method, view, route, and API tests.
- Reuse `_activity_trend`; do not duplicate bucketing logic.
- Verify exact response shape, fallback behavior, player isolation, and four-query service cost.

### Task 3: Cut Home over to the narrow range path

- Regenerate contracts, add typed client/query key, and compose activity into the cached invariant stats response.
- Preserve previous-data behavior while a new range loads.
- Verify query invalidation, focused frontend tests, type checks, and production build.

### Task 4: Capture acceptance evidence

- Run migrations/checks, focused and contract suites, explain/query-count probes, frontend tests, and build.
- Record any unproven production-only claim explicitly.
