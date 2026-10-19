# Learner Progress KPI Instrument Implementation Plan

**Intent:** Turn Home > Progress into a learner-friendly, visually memorable reading of the same Runebound KPI calculations used by Admin, while keeping recent activity and the broader all-play finish-rate context intact.

**Current Behavior:** Progress shows a recent-activity chart and a citadel labelled as runs finished across all stories and challenges. Its lower "Your record" band mixes `home.kpis.hlcr`, `home.kpis.arc`, and `stats.headline.accuracy`, then separately fetches `/api/progress/performance/` only for four module charts. That hides SCR, CAR, and RTA; presents retry-success instead of RTA in the module comparison; mixes broader Home/Stats scopes with Runebound Modules 1-4; and does not expose the targets, evidence counts, or learner meaning behind the Admin KPIs. KPI targets and evidence wording are also repeated across Admin files, so adding another learner copy would create a fourth drift path.

**Expected Outcome:** Progress keeps its activity window and the broader all-play finish-rate citadel, relabelled so it cannot be mistaken for curriculum completion. The lower band becomes one Runebound performance instrument powered entirely by the existing player-scoped performance response. It presents SCR, CAR, HLCR, ARC, and RTA in plain learner language with supportive states (`On track`, `Keep practicing`, `Not measured yet`), exact target and evidence context, plus retry-success as a clearly supplementary recovery signal. A selected metric reveals the honest Modules 1-4 comparison where that metric exists. The surface feels like a premium arcane observatory: an etched signal rail, responsive light trace, rune-like icon treatment, and earned glow, with no generic KPI-card grid, no decorative noise, no blocked interaction, and a complete reduced-motion path.

**Target-Perspective Output:** A learner opens Progress and can answer, without knowing KPI acronyms: Am I finishing the runs I start? Are my commands being accepted? Can I clear hard runs? How much retrying does a clear take? Can I transfer what I learned to a changed retry? They see what each value is based on, which goal it is compared with, why an empty RTA is not a failure, and which module needs practice. Admin sees the same values and thresholds as before.

**Truth Owner:** `backend/progress/services/metrics.py::MetricsService._performance_summary_for_runs()` remains the sole executable formula and scope owner. `MetricsService.performance_summary(player=...)` remains the player-scoped read, while Admin aggregate and per-player paths continue to call the same implementation. `GET /api/progress/performance/` and `PerformanceSummaryResponse` remain the contract boundary. One new frontend performance definition module owns display-only formula/explanation copy, target, direction, formatting, scope, learner label, and evidence semantics; Home and Admin consume it rather than copying those constants. Display formula strings describe the server calculation but never compute it.

**Contract Boundary:** The existing generated `PerformanceSummaryResponse` crosses unchanged through `performanceApi.summary()` and `useModulePerformance()`. `HomeResultsPanel()` owns exactly one query instance plus its loading, error, retry, and retrying states; it passes only a ready `PerformanceSummary` to `LearnerPerformanceInstrument`. `HomeStatsModel.results` is removed, and `HomeStatsView` renders `<HomeResultsPanel />` with no props. No component calculates SCR, CAR, HLCR, ARC, RTA, or retry-success. Activity Week/Month/Year continues to change only `activity_trend`; it never filters or refetches the all-time performance response. The Admin date-range contract remains staff-only and unchanged.

**Cutover:** First freeze the dirty tree and prove learner/Admin formula parity. Then introduce the shared frontend KPI definitions and cut every Admin target/evidence consumer to them. Build and test the learner instrument against the generated performance type. Atomically replace the mixed-scope Home record model/tiles and four simultaneous module charts with the new instrument, update scope copy and preview fixtures, remove dead selectors/utilities, and update the architecture guard. Finish with responsive browser evidence and a POST review.

**Displaced Path:** Remove `HomeResultsModel` and its derivation from `homeStatsModel`; remove the old three-tile `.home-overview-kpi-row`; remove the current module-column presentation that exposes SCR/HLCR/retry-success/ARC as four equal charts and omits RTA/CAR; move Admin-owned `kpiEvidence` into the shared performance domain and delete its old file; remove hard-coded overall KPI target maps from `LearnerKpiPanel` and `AdminAnalyticsPage`. Keep `HomeResultsPanel` as the Progress-band query/composition owner, not as a compatibility renderer. `docs/goals/overview-performance-consolidation/PLAN.md` remains historical and unexecuted; this plan supersedes its learner-metric exclusions and must be the only plan executed for this request.

**Value Density:** One existing endpoint and one existing conditional query now power all learner performance signals. The redesign replaces three mixed-scope tiles and four always-visible charts with five evaluation signals, one contextual recovery signal, one selected module comparison, and one inline calculation disclosure. Eye candy is concentrated on selection, target crossing, and complete states rather than spread across the page.

**Acceptance Evidence:** Record a real non-staff learner fixture proving all `kpis` and module metrics from `performance_summary(player)` match `admin_player_performance_summary(player, ALL_TIME)`. Use the deterministic design preview for rich/empty screenshots only. Use an authenticated or request-intercepted `/home?view=progress` lane that mounts `HomePage` for loading/error/retry, one-performance-request, range-isolation, and zero-request selection evidence. Capture Progress at 1440x900, 900x900, and 390x844, including selection changes, module comparison, focus state, reduced-motion state, and no horizontal overflow. Show that changing Week/Month/Year alters only activity requests/data, selecting a KPI causes zero requests, values are visible without hover, null is never styled or announced as failure, and Admin output is unchanged. Run focused and full frontend tests, backend parity tests, lint, build, API checks, architecture checks, documentation checks, typography checks, and contrast inspection.

**Evidence Lane:** Dirty-tree manifest -> backend parity characterization -> shared definition cutover -> learner instrument unit evidence -> Home integration -> architecture guard -> focused/full gates -> responsive browser/network/accessibility evidence -> POST review.

**Kill Criteria:** Every Runebound evaluation and supplementary value comes from `/api/progress/performance/`; none comes from `home.kpis` or `stats.headline`. `HomeProgressModel.story.finishRate` remains the explicitly labelled all-play context sourced from `stats.headline.finish_rate`. Exactly one shared frontend definition owns display-only formula/explanation copy, overall targets 80/70/70/2/65, direction, format, scope, and evidence semantics. The five evaluation signals are SCR/CAR/HLCR/ARC/RTA; retry-success is labelled supplementary and never counted as a target. RTA no-data explicitly names Modules 3-4 changed retries and never says `0%` or `Needs practice`. The old `.home-overview-kpi-row`, four-chart module grid, Admin target maps, duplicated formula strings, and `features/admin/utils/kpiEvidence.ts` are absent. The performance API/schema/executable formulas, Admin date range, activity range behavior, Skills, Achievements, and Profile remain unchanged. No new KPI card grid, random particles, forced sound, confetti, or motion without `prefers-reduced-motion` exists.

**Non-goals:** Changing any KPI formula, denominator, module scope, target, replay rule, staff exclusion, or date-range rule; adding a learner KPI date picker; adding per-module CAR where the backend does not provide it; inventing a composite score; turning broader finish rate into story-map completion; changing Skills/Achievements/Profile/Loadout; changing the API schema; introducing new image assets, audio, canvas, WebGL, or a chart dependency.

**Risk if Wrong:** A frontend-derived formula or copied target can disagree with Admin. Combining the all-play finish rate with Runebound SCR without explicit scope can show two plausible but different completion values. Scoring RTA before an eligible changed retry falsely punishes beginners. Over-animating six metrics creates noise and motion sensitivity. Editing the already-dirty Home model/tests without a manifest can overwrite unrelated mastery work.

**Architecture Slice:** Existing server-owned Runebound performance response -> shared frontend KPI semantic definitions -> query-owning Home results band -> learner performance instrument -> Home Progress styles/preview/tests, with Admin consumers cut to the same target/evidence definitions and an architecture guard preventing duplicate paths.

**Plan Review Gate:** Requires PRE review before execution.

## UX and visual contract

The product scene is a learner reviewing a night-time observatory console after practice, wanting a quick, honest answer about what improved and what to practice next. The surface stays dark, restrained, and legible; the eye candy comes from meaningful light.

- The activity plot and all-play finish-rate citadel stay above the instrument. Copy must say that the citadel is the share of all runs started that were finished, not story-map completion.
- The Runebound instrument uses one open, hairline-separated surface. It must not be six same-sized cards.
- Five evaluation signals use plain primary labels: `Runs finished`, `Commands accepted`, `Hard runs cleared`, `Retries per finish`, and `Changed retries cleared`. Acronyms may appear only as secondary machine labels or inside the calculation disclosure.
- The supplementary signal is `Retry recovery`; it sits after the five evaluation signals under a `For context` treatment and never contributes to targets met.
- Each signal exposes value, supportive state, target, and evidence counts in text. State is never color-only.
- `Runs finished` / SCR is selected by default on first mount and after a true unmount/remount. Selecting a signal is a clear button/accordion affordance. It lights a restrained cyan trace and reveals one module comparison below; focus-visible uses the existing cyan ring. CAR explains that it is overall-only. RTA compares only Modules 3-4 and explains eligibility. The supplementary signal may compare Modules 1-4 but remains unscored.
- The overall target appears only on the aggregate signal rail. Module comparisons are descriptive and never colored or labelled as pass/fail because Module 4 has Admin-only objective overrides and the API does not provide a per-module target contract.
- A target marker and current marker may animate for 150-250ms with the project ease-out. The brightest amber glow is reserved for a newly selected signal that meets its target or an exact 100% completion. Reduced motion renders the end state immediately. No looped animation belongs in the KPI instrument.
- Loading uses a stable etched-rail skeleton; errors keep activity and the citadel usable and provide an inline Retry action; empty signals teach what activity unlocks them.
- Desktop may use a two-column label/readout rhythm with the selected module comparison alongside or below. Tablet stacks the comparison below the rail. Mobile becomes one full-width sequence with 44px targets, no clipped labels, and no hover-only information.

## Architecture map

### Files to create

- `frontend/src/features/performance/performanceKpis.ts`
- `frontend/src/features/performance/performanceKpis.test.ts`
- `frontend/src/features/performance/components/LearnerPerformanceInstrument.tsx`
- `frontend/src/features/performance/components/LearnerPerformanceInstrument.test.tsx`
- `frontend/src/features/admin/pages/AdminAnalyticsPage.test.tsx`
- `docs/goals/learner-progress-kpi-instrument/PRE_SLICE_BASELINE.md`
- `docs/goals/learner-progress-kpi-instrument/EVIDENCE.md`
- Responsive evidence images under `docs/goals/learner-progress-kpi-instrument/evidence/`

### Files to modify

- `frontend/src/features/home/components/HomeStatsView.tsx`
- `frontend/src/features/home/components/HomeStatsView.test.tsx`
- `frontend/src/features/home/components/home-stats/HomeProgressPanel.tsx`
- `frontend/src/features/home/components/home-stats/HomeResultsPanel.tsx`
- `frontend/src/features/home/components/home-stats/homeStatsModel.ts`
- `frontend/src/features/home/components/home-stats/homeStatsModel.test.ts`
- `frontend/src/features/home/components/home-hub/homeViews.ts`
- `frontend/src/features/performance/preview/fixtures.ts`
- `frontend/src/features/admin/utils/kpiCatalogue.ts`
- `frontend/src/features/admin/components/LearnerKpiPanel.tsx` and its test
- `frontend/src/features/admin/components/SupplementaryRetryRate.tsx`
- `frontend/src/features/admin/pages/AdminDashboardPage.tsx` and its test
- `frontend/src/features/admin/pages/AdminAnalyticsPage.tsx`
- `frontend/src/styles/features/home/stats-layout.css`
- `frontend/src/styles/features/home/stats-progress.css`
- `frontend/src/styles/features/home/stats-kpis.css`
- `frontend/src/styles/features/home/stats-results.css`
- `frontend/src/styles/features/home/stats-responsive.css`
- `scripts/checks/check_architecture_boundaries.py`
- `backend/common/tests/test_architecture_guard_algorithms.py`
- `backend/progress/tests/test_kpi_scope.py`
- `ARCHITECTURE.md`

### Files to delete after imports are cut over

- `frontend/src/features/admin/utils/kpiEvidence.ts`
- `frontend/src/features/admin/utils/kpiEvidence.test.ts`
- `frontend/src/features/performance/utils/moduleColumns.ts`
- `frontend/src/features/performance/utils/moduleColumns.test.ts`

### Files to avoid

- `backend/progress/services/metrics.py` (already dirty and remains the protected executable truth)
- `backend/progress/serializers.py`, `backend/progress/views.py`, and `backend/progress/urls.py`
- Generated `openapi.json` and `apiTypes.ts`; the response contract does not change
- `backend/common/models.py`, current Adventure/Challenge migrations, and unrelated dirty paths
- `frontend/src/features/home/components/home-stats/HomeSkillsPanel.tsx` (already dirty and unrelated to this slice)
- Activity bucketing, skill mastery, achievement, wallet, story-map, shop, Profile, Loadout, and gameplay owners
- Admin API/selectors/serializers; Admin values already use the server truth

### Source, read, and write paths

- **Source of truth:** `MetricsService._performance_summary_for_runs()` over non-replay Runebound Modules 1-4 tier runs; RTA remains Modules 3-4 changed-variant eligible retries.
- **Learner read:** Progress mount -> `HomeResultsPanel` -> `useModulePerformance()` -> `performanceApi.summary()` -> `GET /api/progress/performance/` -> generated `PerformanceSummaryResponse` -> `LearnerPerformanceInstrument`.
- **Admin read:** Existing Admin aggregate/per-player routes -> the same MetricsService implementation. No Admin API change.
- **Activity read:** Existing Home/Stats queries remain independent. `range` affects only `activity_trend`.
- **Interaction write:** KPI selection is local presentation state only. It changes no server or URL state and issues no request.
- **Contract boundary:** Generated `PerformanceSummaryResponse` plus the shared frontend definition keyed by its KPI properties.
- **Integration points:** Home Progress composition, preview fixture cache, Admin presentation metadata, Home CSS import order, architecture guard.
- **Migration/cutover:** Shared definitions first; all consumers switch in one slice; then old Admin evidence and Home module-grid paths are deleted.
- **Evidence gate:** Backend parity trace; deterministic rich/empty visual proof from the design preview; authenticated or request-intercepted `HomePage` proof for network/loading/error/range behavior; and green architecture/API/docs/build checks.

## Task board

### Task 1A - Freeze the dirty tree

**Exact files:** Create `docs/goals/learner-progress-kpi-instrument/PRE_SLICE_BASELINE.md`; read only every file in this plan plus current dirty paths.

**Allowed scope:** Record `git status --short`, byte count, SHA-256, and diff state for every pre-existing dirty path, especially `metrics.py`, `HomeStatsView.test.tsx`, `homeStatsModel.ts`, `homeStatsModel.test.ts`, and `HomeSkillsPanel.tsx`. Capture current Progress rich/empty screenshots only as temporary artifacts outside the repository, then record their dimensions, hashes, and observations in `PRE_SLICE_BASELINE.md`; do not add those image files to the workspace. Record current request counts and architecture/test baselines. Do not write any other repository file in this task.

**Expected output:** A reproducible preservation and behavior baseline captured before any implementation or parity-test write.

**Verification:** Current `python -m pytest backend/progress/tests/test_performance_summary_api.py backend/progress/tests/test_kpi_scope.py -q`; current focused Home and Admin tests; `python scripts/checks/check_architecture_boundaries.py`.

**Acceptance evidence:** Manifest, baseline command output, and current screenshots/request trace.

**Parallel:** No; it protects all subsequent work.

### Task 1B - Add the learner/Admin parity proof

**Exact files:** Modify `backend/progress/tests/test_kpi_scope.py` only.

**Allowed scope:** Add one all-time, non-staff learner fixture proving `MetricsService.performance_summary(player=learner)` and `MetricsService.admin_player_performance_summary(player=learner, kpi_range=ALL_TIME)` return identical `kpis`, `completed_sessions`, and module data. Cover at least one measured value, one true zero, one null/no-data value, retry-success, and RTA eligibility. Do not edit `metrics.py`, serializers, views, routes, or generated contracts.

**Expected output:** An executable boundary proof that learner and per-player Admin values share one formula path.

**Verification:** `python -m pytest backend/progress/tests/test_kpi_scope.py backend/progress/tests/test_performance_summary_api.py -q`.

**Acceptance evidence:** Focused test output and the asserted parity matrix recorded in `EVIDENCE.md` during the final task.

**Parallel:** No; complete before presentation work so formula drift is ruled out first.

### Task 2 - Establish one frontend KPI semantic owner

**Exact files:** Create `frontend/src/features/performance/performanceKpis.ts`, `frontend/src/features/performance/performanceKpis.test.ts`, and `frontend/src/features/admin/pages/AdminAnalyticsPage.test.tsx`; modify `frontend/src/features/admin/utils/kpiCatalogue.ts`, `frontend/src/features/admin/components/LearnerKpiPanel.tsx`, `frontend/src/features/admin/components/LearnerKpiPanel.test.tsx`, `frontend/src/features/admin/components/SupplementaryRetryRate.tsx`, `frontend/src/features/admin/pages/AdminDashboardPage.tsx`, `frontend/src/features/admin/pages/AdminDashboardPage.test.tsx`, and `frontend/src/features/admin/pages/AdminAnalyticsPage.tsx`; delete `frontend/src/features/admin/utils/kpiEvidence.ts` and `frontend/src/features/admin/utils/kpiEvidence.test.ts` after every import is cut over.

**Allowed scope:** Define the five evaluation keys and the supplementary retry-success key against generated `PerformanceKpiSet`/`RateMetric` types. Own display-only formula and plain factual explanation copy, overall target, direction, percent/decimal formatting, technical name, learner label, scope note, status derivation, and evidence wording. Derive the Admin KPI catalogue from these shared definitions, leaving only the SO structure and objective-specific overrides in Admin. Preserve Admin-visible values, targets, objective overrides, results, and DOM behavior. Replace Admin's repeated overall target maps, formula strings, and evidence imports with the shared owner. Create `AdminAnalyticsPage.test.tsx` to characterize preserved values, targets, null states, and module availability. Do not move module-specific SO target overrides out of the Admin objective catalogue.

**Expected output:** Home can consume the Admin-aligned semantics without importing from an Admin feature, and Admin has no behavior change or duplicate overall target map.

**Verification:** New utility tests for higher/lower-is-better, null/zero, evidence grammar, and supplementary no-target behavior; existing `LearnerKpiPanel`, Admin Dashboard, Admin Analytics, and evidence tests updated and green; TypeScript build.

**Acceptance evidence:** Search table showing one owner for each overall target and no imports of `features/admin` from learner code.

**Parallel:** No; the instrument depends on this contract.

### Task 3 - Build the learner performance instrument

**Exact files:** Create `frontend/src/features/performance/components/LearnerPerformanceInstrument.tsx` and `frontend/src/features/performance/components/LearnerPerformanceInstrument.test.tsx`; modify `frontend/src/features/performance/preview/fixtures.ts`; delete `frontend/src/features/performance/utils/moduleColumns.ts` and `frontend/src/features/performance/utils/moduleColumns.test.ts` after the new selected comparison is covered.

**Allowed scope:** Render five evaluation signal rows and one supplementary row from a ready `PerformanceSummary`. Own local selected-signal state only, with SCR / `Runs finished` selected by default and restored after unmount/remount. Show learner label, value, supportive state, aggregate target, direct evidence, and an inline native disclosure for acronym/formula/scope. Render one selected module comparison: SCR/HLCR/ARC across Modules 1-4, RTA across Modules 3-4, retry-success across Modules 1-4, and an honest overall-only explanation for CAR. Module values are descriptive and unscored: do not apply the overall target or Admin's SO-specific overrides to module rows. Preserve exact server values; presentation may clamp only visual track position, never displayed data. Use semantic buttons, `<details>`, progress/figure labelling, direct values, and keyboard-visible focus.

**Expected output:** A standalone, typed product component that makes the complete KPI set understandable without Admin terminology and without a card grid.

**Verification:** Component tests cover all labels/values, exact targets, lower-is-better ARC, measured zero vs null, RTA eligibility copy, supplementary exclusion, metric selection, module scopes, CAR overall-only, keyboard/focus semantics, frozen input, and no network/API import. Preview fixtures include rich met/miss/no-data states and an all-empty account.

**Acceptance evidence:** Test output plus isolated rich/empty render captures.

**Parallel:** No; it defines the final render contract.

### Task 4 - Integrate Progress and deliver purposeful eye candy

**Exact files:** Modify `frontend/src/features/home/components/HomeStatsView.tsx`, `frontend/src/features/home/components/HomeStatsView.test.tsx`, `frontend/src/features/home/components/home-stats/HomeProgressPanel.tsx`, `frontend/src/features/home/components/home-stats/HomeResultsPanel.tsx`, `frontend/src/features/home/components/home-stats/homeStatsModel.ts`, `frontend/src/features/home/components/home-stats/homeStatsModel.test.ts`, `frontend/src/features/home/components/home-hub/homeViews.ts`, `frontend/src/styles/features/home/stats-layout.css`, `frontend/src/styles/features/home/stats-progress.css`, `frontend/src/styles/features/home/stats-kpis.css`, `frontend/src/styles/features/home/stats-results.css`, and `frontend/src/styles/features/home/stats-responsive.css`.

**Allowed scope:** Make `HomeResultsPanel()` the sole `useModulePerformance()` owner; it renders stable loading and error/retry/retrying states itself and passes only ready data to `LearnerPerformanceInstrument`. Remove `HomeStatsModel.results`; `HomeStatsView` renders `<HomeResultsPanel />` with no props. Replace the mixed result-model path and old tiles/charts. Relabel the upper citadel as all-play finish rate and update the Progress switcher blurb so scopes are honest. Style the learner instrument as an open arcane signal rail using existing tokens, one cyan accent, amber earned state, muted no-data state, etched icon circles, target/current markers, and 150-250ms selection transitions. Add reduced-motion overrides, focus/hover/active/disabled states, 44px mobile targets, structural breakpoints, readable contrast, and no hover-only information. Preserve existing activity, Skills, Achievements, Profile, and the user's dirty mastery changes exactly.

**Expected output:** The real Progress tab is coherent, premium, animated with purpose, and accurate at every state and viewport.

**Verification:** Focused Home model/component/page/preview tests; CSS architecture and typography checks; search for displaced `.home-overview-kpi-row` and old chart classes; production build; deterministic browser checks at 1440x900, 900x900, and 390x844.

**Acceptance evidence:** Deterministic design-preview rich/empty screenshots; authenticated or request-intercepted `/home?view=progress` loading/error/retry and network traces through `HomePage`; keyboard trace; selected-state screenshots; reduced-motion computed-style proof; contrast notes; and zero-overflow measurements.

**Parallel:** No; dirty Home files and CSS cascade require one atomic integration owner.

### Task 5 - Harden ownership and prove the cutover

**Exact files:** Modify `scripts/checks/check_architecture_boundaries.py`, `backend/common/tests/test_architecture_guard_algorithms.py`, and `ARCHITECTURE.md`; create `docs/goals/learner-progress-kpi-instrument/EVIDENCE.md` and evidence images under `docs/goals/learner-progress-kpi-instrument/evidence/`.

**Allowed scope:** Update the Home Overview guard for a query-owning, no-prop `HomeResultsPanel` that owns loading/error/retry and delegates only ready rendering to the performance component. Require one performance query owner, one shared KPI definition owner, no `HomeStatsModel.results`, no Admin import below learner features, no duplicated overall target maps or display-formula strings, no old KPI row/module-grid path, and no unexpected Home owner. Update `ARCHITECTURE.md` to distinguish RTA from the supplementary retry-success rate, name their scopes and learner labels, and document the unchanged performance endpoint. Preserve all unrelated guard and architecture documentation. Run the integrated evidence lane and request a POST correctness/maintainability review.

**Expected output:** The old mixed-scope path and duplicate semantic definitions cannot silently return.

**Verification:** `python scripts/checks/check_architecture_boundaries.py`; `python -m pytest backend/common/tests/test_architecture_guard_algorithms.py backend/progress/tests/test_performance_summary_api.py backend/progress/tests/test_kpi_scope.py -q`; `npm --prefix frontend test`; `npm --prefix frontend run lint`; `npm --prefix frontend run lint:dead`; `npm --prefix frontend run build`; `npm --prefix frontend run api:check`; `npm --prefix frontend run api:usage-check`; `npm --prefix frontend run api:type-adoption-check`; `npm --prefix frontend run docs:check`; `npm --prefix frontend run ui:typography-check`; applicable fast-quality checks.

**Acceptance evidence:** Completed `EVIDENCE.md`, responsive images, DOM value matrix, network trace, accessibility/reduced-motion notes, dirty-tree preservation audit, and reviewer verdict.

**Parallel:** No; this is the integrated gate.
