# Overview and Admin Performance Consolidation — Implementation Plan

**Plan title:** Overview and Admin Performance Consolidation

**Intent:** Turn Home > Overview into the single place where a learner understands outcome performance, move diagnostic metrics into staff-only Admin analytics, remove the misleading “Recommended next step” banner, remove Performance as a competing global destination, and give the Admin shell/analytics page a production-quality responsive visual system.

**Current behavior:** `HomeStatsView` opens with a large static CTA that only branches on whether a companion exists; it does not calculate a recommended or next level. Overview then shows a four-item KPI strip assembled from the broader Dashboard/Stats summaries. A separate `/performance` page fetches the server-owned Runebound performance summary and presents five aggregate KPI cards plus expandable module rows. Performance is exposed in both desktop and mobile global navigation.

**Expected outcome:** The CTA and old Overview KPI strip are replaced by one full-width learner Performance lens at the top of Overview. A two-option segmented control lets the learner compare Scenario completion and Hard completion; the selected aggregate value, evidence counts, plain-language definition, and Modules 1–4 chart update locally from one fetched response. Command processability (currently named CAR), Retry transfer, and Average retries are removed from learner UI and shown as global, staff-only Runebound diagnostics in Admin > Analytics. Admin analytics gains a crisp responsive hierarchy, semantic data bars, accessible tables, purposeful empty/loading/error states, and a consistent shell/navigation treatment. Existing mastery, activity, story progress, and achievements remain below. Performance disappears from global navigation, and saved `/performance` links redirect to Overview.

**Target-perspective output:** A learner lands on Overview, immediately understands completion quality, switches between overall and hard-mode completion with keyboard or pointer, reads the exact numerator/denominator, compares Modules 1–4 without another request, and can distinguish a measured zero from “no attempts yet.” The learner no longer sees implementation-oriented processability/retry diagnostics, the generic story CTA, or a separate Performance tab. A staff member opens Admin > Analytics and sees the diagnostic metrics in an operational context with clear definitions, denominators, module comparisons, and a substantially cleaner responsive layout.

**Truth owner:** `MetricsService` remains the sole formula owner for Runebound SCR, CAR, HLCR, RTR, and ARC. The existing player-scoped `GET /api/progress/performance/` continues to power Overview. A new all-player summary method must reuse the same internal aggregation path and feed the staff-only `GET /api/admin/analytics/` response; the Admin selector must not copy formulas. Home/Stats summaries remain authoritative only for mastery, activity, story progress, and achievements and must not be relabeled as Runebound performance.

**Contract boundary:** `GET /api/progress/performance/` keeps its existing player-scoped response byte-for-byte. `MetricsService` gains one shared queryset-driven aggregation implementation and an all-player entry point; `AdminAnalyticsResponse` gains `runebound_performance: PerformanceSummaryResponse` behind the existing `IsStaff` permission. Generated API types are regenerated, never hand-edited. `HomePage` owns the player performance query but does not add it to the page-wide loading/error gate. It maps React Query into one exact `HomePerformanceState`: `{ status: 'loading' }`, `{ status: 'error'; message: string; retrying: boolean; onRetry: () => void }`, or `{ status: 'ready'; data: PerformanceSummary }`. That state passes unchanged through `HomeHubView` and `HomeStatsView`; `HomePerformanceInsights` receives only that state and renders only SCR/HLCR. Admin analytics owns its existing query and consumes the new aggregate field. No frontend owns or re-derives KPI formulas.

**Cutover:** First characterize player and Admin analytics contracts. Extract one shared Runebound aggregation path and extend only the staff analytics response. Then add the typed learner lens and Admin diagnostics. In the same UI cutover, remove the CTA and its onboarding step, remove the old mixed-scope KPI strip/model fields, remove the Performance nav item, redirect `/performance` to `/home?tab=overview&metric=scr`, delete the displaced Performance page/test/styles, and import the new Admin stylesheet. Do not ship duplicate formulas or a state where both the standalone page and Overview remain current-looking.

**Displaced path:** Delete `PerformancePage.tsx`, its page test, `performance.css`, and `continue-card.css`; remove the global Performance nav item and its icon/import; remove the CTA markup/classes/onboarding target; remove the old `.home-overview-kpi-row` render path and its mixed Dashboard/Stats KPI model. Retain `features/performance/api`, `features/performance/types.ts`, `queryKeys.performanceSummary`, and `PERFORMANCE_ROUTE` only as live data/compatibility contracts.

**Value density:** One two-metric learner lens replaces a non-informational banner and ambiguous mixed-scope KPI strip. Three diagnostic metrics move into their appropriate staff context, the obsolete standalone page/global destination disappears, and the existing Admin analytics surface becomes substantially more legible without creating another dashboard route.

**Acceptance evidence:** Typed Overview/Admin/routing tests; unchanged player performance contract proof; new staff analytics payload and non-staff denial proof; screenshots at 1440×900, 820×900, and 390×844 for learner SCR/HLCR/empty states and desktop/mobile Admin analytics; keyboard traces for the learner toggle and Admin navigation/table; proof that learner selection issues zero additional requests; exactly one player performance request on initial Home; `/performance` redirect proof; CAR/RTR/ARC absent from learner UI and present in Admin; zero-vs-null assertions; no horizontal overflow; clean console/page errors; production build, focused/full tests, lint, regenerated API checks, architecture guard, and typography check.

**Evidence lane:** Dirty-worktree baseline -> focused behavior characterization -> typed performance-lens implementation -> atomic Overview/navigation/route deletion cutover -> architecture guard update -> focused and full static gates -> responsive browser/keyboard/network evidence -> PRE/POST review.

**Kill criteria:** No global nav item labeled Performance. `/performance` renders no standalone page and redirects to `/home?tab=overview&metric=scr`. No `home-overview-continue`, `overview-next`, `performance-page`, or `home-overview-kpi-row` runtime path remains. Learner Overview offers exactly SCR and HLCR; CAR, RTR, and ARC labels/values are absent there. Admin > Analytics shows CAR, RTR, and ARC from the staff response, with RTR/ARC module comparison and honest aggregate-only CAR. The player endpoint remains unchanged; admin formulas call the shared MetricsService aggregation path. A denominator of zero renders “No attempts yet,” while a non-null zero remains a real zero. Toggling does not refetch. Performance failure does not hide other Home surfaces. Non-staff cannot access Admin analytics. All preserved Overview and Admin sections remain operable and responsive.

**Non-goals:** Changing KPI formulas, extending per-module CAR, adding time-series data, including Module 0 in Runebound performance, redesigning non-analytics Admin content/forms, redesigning Loadout/Profile/Modules, changing story routing or companion requirements, changing achievements/mastery/activity calculations, or restoring/deleting the user-modified `docs/PERFORMANCE_KPIS.md` path.

**Risk if wrong:** Copying KPI formulas into Admin would create silent drift. Showing player-scoped values in Admin would misrepresent system health, while exposing global aggregates outside `IsStaff` would be a permission regression. Mixing Dashboard/Stats with Runebound values would show contradictions. Deleting the CTA without re-anchoring onboarding would stall the tour; deleting `/performance` without a redirect would break bookmarks. Editing dirty Home/generated files without a baseline could overwrite unrelated work.

**Architecture slice:** Shared Runebound metric aggregation, staff analytics response/read model, Admin analytics/shell styling, Home Overview presentation, onboarding target, global navigation, route compatibility, generated contract, and focused tests only.

**Plan Review Gate:** Requires PRE review before execution.

## Metric classification and visualization contract

| Key | User-facing label | Product class | Direction | Available comparison | Visualization |
| --- | --- | --- | --- | --- | --- |
| `scr` | Scenario completion | Outcome | Higher is better | Learner Overview + Admin payload | 0–100% learner module bars |
| `hlcr` | Hard completion | Difficulty outcome | Higher is better | Learner Overview + Admin payload | 0–100% learner module bars |
| `car` | Command processability | Technical input-quality diagnostic | Higher is better | Admin only; aggregate only | Admin aggregate bar with command numerator/denominator and scope note |
| `rtr` | Retry transfer | Technical recovery diagnostic | Higher is better | Admin only; overall + Modules 1–4 | Admin 0–100% module bars |
| `arc` | Average retries | Technical effort/cost diagnostic | Lower means fewer retries; do not score it as mastery | Admin only; overall + Modules 1–4 | Admin scalar module bars with exact values |

Charts must remain semantic without color: each row includes module name, exact value, and evidence text. Color is one restrained product accent; null/empty uses muted treatment. The learner uses a two-option segmented control rather than a dropdown because only two choices remain. No chart library is needed.

## Architecture map

### Files to create

- `frontend/src/features/home/components/home-stats/HomePerformanceInsights.tsx`
- `frontend/src/features/home/components/home-stats/HomePerformanceInsights.test.tsx`
- `frontend/src/features/home/components/home-stats/homePerformanceState.ts`
- `frontend/src/features/performance/preview/fixtures.ts`
- `frontend/src/features/home/pages/HomePage.test.tsx`
- `frontend/src/shared/navigation/AppNavigation.test.tsx`
- `frontend/src/features/admin/pages/AdminAnalyticsPage.test.tsx`
- `frontend/src/styles/features/admin.css`
- `docs/goals/overview-performance-consolidation/PRE_SLICE_BASELINE.md`
- `docs/goals/overview-performance-consolidation/EVIDENCE.md`
- Responsive evidence images under `docs/goals/overview-performance-consolidation/evidence/`

### Files to modify

- `frontend/src/features/home/pages/HomePage.tsx`
- `frontend/src/features/home/components/HomeHubView.tsx`
- `frontend/src/features/home/components/HomeHubView.test.tsx`
- `frontend/src/features/home/preview/HomePreviewPage.tsx`
- `frontend/src/features/home/components/HomeStatsView.tsx`
- `frontend/src/features/home/components/HomeStatsView.test.tsx`
- `frontend/src/features/home/components/home-stats/HomeStatsDashboard.tsx`
- `frontend/src/features/home/components/home-stats/homeStatsModel.ts`
- `frontend/src/features/home/components/home-stats/homeStatsModel.test.ts`
- `frontend/src/features/onboarding/components/HomeOnboarding.tsx`
- `frontend/src/features/onboarding/pages/OnboardingJourney.test.tsx`
- `frontend/src/features/admin/pages/AdminAnalyticsPage.tsx`
- `frontend/src/features/admin/components/AdminLayout.tsx`
- `frontend/src/features/admin/components/AdminLayout.test.tsx`
- `frontend/src/features/admin/components/adminUi.tsx`
- `frontend/src/shared/navigation/AppNavigation.tsx`
- `frontend/src/app/router.tsx`
- `frontend/src/app/router.test.tsx`
- `frontend/src/main.tsx`
- `frontend/src/styles/features/home/stats.css`
- `frontend/src/styles/features/home/stats-kpis.css`
- `frontend/src/styles/features/home/stats-responsive.css`
- `scripts/checks/check_architecture_boundaries.py`
- `backend/common/tests/test_architecture_guard_algorithms.py`
- `backend/progress/services/metrics.py`
- `backend/progress/tests/test_performance_summary_api.py`
- `backend/adminconsole/selectors/analytics.py`
- `backend/adminconsole/serializers.py`
- `backend/adminconsole/tests/test_admin_api.py`
- `backend/adminconsole/tests/test_admin_read_api.py`
- `frontend/src/shared/api/generated/apiTypes.ts` through the repository generator only
- `frontend/src/shared/api/generated/openapi.json` through the repository generator only

### Files to delete

- `frontend/src/features/performance/pages/PerformancePage.tsx`
- `frontend/src/features/performance/pages/PerformancePage.test.tsx`
- `frontend/src/styles/features/performance.css`
- `frontend/src/styles/features/home/continue-card.css`

### Files to avoid

- `backend/progress/serializers.py`, `backend/progress/views.py`, and `backend/progress/urls.py`
- `frontend/src/features/performance/api/performanceApi.ts`
- `frontend/src/features/performance/types.ts`
- `frontend/src/shared/api/queryKeys.ts`
- `frontend/src/shared/navigation/routes.ts` other than preserving the existing `PERFORMANCE_ROUTE`
- `frontend/src/features/home/components/HomeLoadoutView.tsx`, `home-hub/**`, and `HomeProfileWorkspace`
- Achievement, Stats, wallet, story-map, companion, shop, curriculum, and gameplay owners
- `docs/PERFORMANCE_KPIS.md`, which is already deleted in the user’s dirty worktree
- All unrelated dirty or untracked files

### Read/write path and integration points

- Read: `HomePage` -> `performanceApi.summary` -> `GET /api/progress/performance/` -> `MetricsService.performance_summary` -> generated `PerformanceSummaryResponse`.
- Presentation: `HomePage` maps the query to `HomePerformanceState` -> `HomeHubView` forwards the same state -> `HomeStatsView` forwards the same state -> `HomePerformanceInsights` renders it. Only the panel renders performance loading/error/retrying UI; `onRetry` calls the page-owned refetch path, and the Home shell remains available.
- Interaction write: native `<select>` -> validated `metric` URL search parameter, preserving unrelated parameters -> local rerender from the already-cached response.
- Compatibility: global navigation contains Dashboard and Modules (plus Admin when applicable); `/performance` -> replace redirect to `/home?tab=overview&metric=scr`.
- Existing Home/Stats read path continues to feed mastery, activity, story progress, and achievements only.
- Admin read: staff request -> `AdminAnalyticsAPIView` with existing `IsStaff` -> `admin_analytics_payload` -> `MetricsService.all_player_performance_summary()` -> shared queryset aggregation -> `runebound_performance` in the admin response.
- Preview/test fixtures remain typed and are never imported into production runtime code.

## Task board

### Task 1 — Freeze the dirty tree and characterize the contracts

**Exact files:** Create `PRE_SLICE_BASELINE.md`; read-only inspect every file named above plus `backend/progress/tests/test_performance_summary_api.py`.

**Scope:** Record `git status --short`, bytes and SHA-256 for every pre-existing dirty target, especially `HomeHubView.tsx`, `stats-layout.css`, `stats.css`, `stats-kpis.css`, generated `apiTypes.ts`, and deleted `docs/PERFORMANCE_KPIS.md`. Record current player performance and staff analytics payloads/permission results, one-request behavior, CTA destinations, onboarding step sequence, nav items, `/performance` route result, and Admin desktop/mobile layout. Preserve unrelated hunks exactly.

**Expected output:** A reproducible baseline that separates this slice from user-owned changes and freezes the no-backend/no-generated-contract boundary.

**Verification:** Focused current tests for `HomeStatsView`, `HomeHubView`, `OnboardingJourney`, `PerformancePage`, router, and backend performance summary; architecture guard baseline.

**Acceptance evidence:** Manifest plus command outputs and current desktop/mobile screenshots.

**Parallel:** No; this must precede edits.

### Task 2 — Build the typed interactive Performance lens

**Exact files:** Create `HomePerformanceInsights.tsx`, its test, `homePerformanceState.ts`, and the typed performance preview fixture.

**Scope:** Implement the two-option SCR/HLCR segmented control, validated URL state, aggregate definition/evidence, accessible module chart rows, percentage formatting, and honest null/zero behavior. Use existing design tokens, one accent, hairline grouping, clear focus, 44px touch targets, reduced-motion support, and no decorative KPI-card grid. Do not render CAR/RTR/ARC, fetch inside the component, or calculate KPI formulas.

**Expected output:** A self-contained learner presentation owner that renders the two outcome metrics from one `PerformanceSummary` and changes view without network work.

**Verification:** Component tests for default/each selection, invalid query fallback, parameter preservation, keyboard-accessible segmented controls, percentage scaling, explicit absence of CAR/RTR/ARC, four module rows, zero/null distinction, and input immutability.

**Acceptance evidence:** Focused test output and fixture-render screenshot at desktop/mobile sizes.

**Parallel:** No; the component contract establishes the integration boundary.

### Task 3 — Integrate the server-owned summary and replace the old Overview surfaces

**Exact files:** Modify `HomePage.tsx` and add its test; modify `HomeHubView.tsx`/test, `HomePreviewPage.tsx`, `HomeStatsView.tsx`/test, `HomeStatsDashboard.tsx`, `homeStatsModel.ts`/test, `stats.css`, `stats-kpis.css`, and `stats-responsive.css`.

**Scope:** Fetch `performanceApi.summary` once in `HomePage` with the existing query key/stale-time conventions; convert it to the exact `HomePerformanceState` contract, including page-owned `refetch` as `onRetry` and `isFetching` as `retrying`, and pass it through exact props without adding it to the page-wide loading/error gate. Place `HomePerformanceInsights` first and full-width in the Overview grid, with local loading, error/retry, retrying-disabled, and ready states. Remove the CTA, its `companionRequired` prop, and its companion/story branching; keep companion state in `HomeHubView` for onboarding and Loadout. Remove the old four-KPI row, its view-model fields/helpers/tests, and repurpose `stats-kpis.css` as the single style owner for the performance lens. Keep mastery, activity, story progress, achievements, and companion/loadout behavior unchanged.

**Expected output:** Overview becomes the canonical performance destination with no mixed-scope KPI duplication.

**Verification:** HomePage query/state-adaptation test; Hub/composition/model/dashboard focused tests; performance loading/error leaves the Home shell and other sections usable; retry invokes the query retry path; exactly one performance request on initial Home load; metric changes issue zero requests; deep-frozen summaries remain unmodified; responsive no-overflow checks.

**Acceptance evidence:** Rich/empty screenshots, request log, DOM value table, and preserved-section comparison.

**Parallel:** No; these dirty files and props form one atomic integration path.

### Task 4 — Add staff-owned Runebound diagnostics and polish Admin analytics

**Exact files:** Modify `backend/progress/services/metrics.py`, its performance test, `backend/adminconsole/selectors/analytics.py`, `backend/adminconsole/serializers.py`, the two Admin API test files, generated `openapi.json`/`apiTypes.ts` through the generator, `AdminAnalyticsPage.tsx`, new `AdminAnalyticsPage.test.tsx`, `AdminLayout.tsx`/test, `adminUi.tsx`, `main.tsx`, and new `admin.css`.

**Scope:** Extract the existing player performance computation behind a queryset-driven internal method without changing the player response. Add `all_player_performance_summary()` over the same story/modules/replay scope and expose it as `runebound_performance` from the already staff-protected Admin analytics endpoint. Regenerate the API contract. In Admin > Analytics, present CAR as “Command processability,” RTR as “Retry transfer,” and ARC as “Average retries,” with definitions, honest evidence counts, and module comparisons where available. Redesign the Admin shell and analytics layout with dedicated semantic classes: stronger navigation state, compact operational summary band, accessible diagnostic rows/bars, responsive table wrapper, consistent controls/focus/empty states, restrained accent use, and no repeated card-grid or decorative motion.

**Expected output:** Technical metrics are visible only in the staff analytics context, use the same formula owner as player performance, and the Admin interface is clearer and responsive across desktop/mobile.

**Verification:** Existing player performance API payload equality; new all-player aggregate test across multiple learners with replay exclusion; Admin serializer shape; staff 200 and non-staff 403; generated contract check; Admin component rich/empty tests; contrast/focus/no-overflow browser inspection.

**Acceptance evidence:** Staff/non-staff request traces, payload table showing CAR/RTR/ARC values and scopes, desktop/mobile Admin screenshots, and computed layout/contrast notes.

**Parallel:** No; shared backend truth ownership must cut over before the generated client and Admin UI.

### Task 5 — Re-anchor onboarding and retire the global Performance destination

**Exact files:** Modify `HomeOnboarding.tsx`, `OnboardingJourney.test.tsx`, `AppNavigation.tsx`, new `AppNavigation.test.tsx`, `router.tsx`, `router.test.tsx`, and `main.tsx`; delete the two Performance page files, `performance.css`, and `continue-card.css`.

**Scope:** Replace the required `overview-next` tour step with a first step anchored to the performance lens and copy that explains choosing a metric. Preserve the existing Loadout-first companion acquisition path and onboarding finish behavior. Remove Performance from the shared primary-nav array so desktop and mobile update together. Redirect the route with `replace`. Remove displaced page/style imports and files atomically.

**Expected output:** One Overview destination, no broken tour target, no dead standalone performance implementation, and bookmark-safe routing.

**Verification:** Onboarding journey sequence, both navigation surfaces, admin conditional item, redirect pathname/search, absence searches for displaced classes/imports, dead-code check, and production build.

**Acceptance evidence:** Desktop/mobile nav screenshots, completed tour trace, and redirect trace.

**Parallel:** No; route/nav/deletion is one cutover.

### Task 6 — Update durable boundaries and prove the experience

**Exact files:** Modify `check_architecture_boundaries.py` and its algorithm tests; create `EVIDENCE.md` and evidence images.

**Scope:** Amend the existing Home Overview guard to recognize the third focused render owner and the new typed prop path, forbid React Query/API ownership below `HomePage`, forbid metric formulas/duplicate KPI render paths, require the redirect and deleted paths, and preserve all unrelated guard behavior. Run focused/full gates and the browser evidence lane. Request POST correctness and maintainability review.

**Expected output:** The old banner/page/KPI duplication cannot silently return, and the new data/UI ownership is independently verifiable.

**Verification:** `python scripts/checks/check_architecture_boundaries.py`; `python -m pytest backend/common/tests/test_architecture_guard_algorithms.py backend/progress/tests/test_performance_summary_api.py -q`; `npm --prefix frontend test`; `npm --prefix frontend run lint`; `npm --prefix frontend run lint:dead`; `npm --prefix frontend run build`; `npm --prefix frontend run api:check`; `npm --prefix frontend run api:usage-check`; `npm --prefix frontend run ui:typography-check`; relevant repository fast-quality gate.

**Acceptance evidence:** Completed `EVIDENCE.md`, screenshots, keyboard/URL/network traces, clean errors, green gates, protected dirty-tree hash audit, and reviewer verdicts.

**Parallel:** No; it validates the integrated cutover and touches shared guard files.
