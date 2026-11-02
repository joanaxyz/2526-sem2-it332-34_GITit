# Home Overview Ownership and CSS Cutover Implementation Plan

**Intent:** Make the Home Overview an explicit composition of focused, testable owners and remove the legacy CSS paths that still look current despite having no runtime consumer.

**Current Behavior:** `HomeStatsView.tsx` is a 339-line component that owns story navigation, formatting, skill-profile transformation, heatmap construction, progress/KPI derivation, achievement derivation, achievement filter state, and all Overview markup. It has no direct component test. The loaded Home stylesheet also imports `stats-actions.css` and `achievements.css`; together they contain 389 lines of legacy `.home-stats-*`, `.home-activity-*`, and `.home-award-*` rules with no runtime markup owner, plus duplicated live responsive overrides.

**Expected Outcome:** `HomeStatsView` becomes a small composition/Continue-CTA root. `homeStatsModel` is the pure owner of cross-summary fallback and presentation derivation, `HomeStatsDashboard` owns progress/activity/KPI rendering, and `HomeAchievementGallery` owns achievement filtering/card rendering. The public `HomeStatsView({ home, stats })` contract and rendered DOM/class contract remain stable. Live responsive rules have one canonical owner; legacy CSS files/selectors and the dead `latestAchievement` helper are deleted.

**Target-Perspective Output:** A learner sees the same rich and empty Overview at desktop, breakpoint, and mobile widths; Continue Story still navigates correctly; mastery, activity, progress, KPI, and achievement values are unchanged; achievement filters remain operable and accessible; and no horizontal overflow or console/page error is introduced.

**Truth Owner:** Backend Home/Stats summaries remain authoritative data contracts; `deriveAchievements` remains the achievement ledger; `storyPath` remains the navigation contract. Within Home Overview, `HomeStatsView` owns composition and the story CTA, `homeStatsModel` owns pure view-model construction, `HomeStatsDashboard` owns progress/activity/KPI rendering, and `HomeAchievementGallery` owns achievement filter state and rendering. `stats-layout.css`, `stats-achievements.css`, `stats-responsive.css`, and `continue-card.css` are the only Overview CSS owners.

**Contract Boundary:** `HomeStatsView` retains exactly the `home: HomeSummary` and `stats: StatsSummary` props used by `HomeHubView`. It builds one immutable `HomeStatsModel`. The exact render contracts are `HomeStatsDashboard({ dashboard }: { dashboard: HomeStatsDashboardModel })` and `HomeAchievementGallery({ achievements }: { achievements: Achievement[] })`; no raw summary/query result, API client, router state, mutable form state, render prop, spread object, or fixture seam crosses either child boundary.

**Cutover:** Add direct behavior/model tests, create the pure model and two render owners, then atomically replace embedded Overview logic in `HomeStatsView`. Move the base achievement-card rules out of the misleading `stats-responsive.css` file into `stats-achievements.css`; retain live breakpoint rules in `stats-responsive.css` with the same cascade order; remove legacy imports, delete `stats-actions.css` and `achievements.css`, and remove `latestAchievement` plus its self-only test.

**Displaced Path:** The monolithic implementation in `HomeStatsView`, the imported legacy CSS files, every unused `.home-stats-*`/`.home-activity-*`/`.home-award-*` selector, duplicate live breakpoint ownership, and the obsolete `latestAchievement` hero-banner stand-in are removed rather than retained as compatibility paths.

**Value Density:** This single surface cut removes a mixed 339-line component, adds the first direct Overview/model coverage, retires a 389-line legacy CSS path, deletes a self-referential dead helper, fixes a misleading responsive-style owner, and adds a durable role guard without changing backend/API contracts or visual design.

**Acceptance Evidence:** Direct rich/empty/filter/heatmap/link/accessibility tests and pure model tests; architecture rejection of displaced imports, markers, oversized roles, reverse dependencies, dead helper, and legacy CSS; pre/post browser screenshots at 1440x900 and 390x844; computed-style/cascade parity in bands straddling every live breakpoint; filter/reset and keyboard interaction traces; exact same-origin request counts; clean console/page errors; full frontend, build, lint, dead-code, API, documentation, architecture, and quality gates; protected-path hashes; and PRE/POST/correctness/maintainability/verifier outcomes.

**Evidence Lane:** Dirty-worktree and browser baseline -> direct Overview test harness -> atomic component cutover -> CSS owner migration and legacy deletion -> architecture guard -> focused/full/static gates -> deterministic browser comparison -> protected-state audit -> POST/correctness/maintainability/verifier reviews.

**Kill Criteria:** `HomeStatsView` at most 80 lines; `homeStatsModel` at most 160; `HomeStatsDashboard` at most 220; `HomeAchievementGallery` at most 150. One composition/CTA owner, one pure derivation owner, one dashboard render owner, and one achievement/filter render owner. No child imports Hub/Page/the composition root; model is React/router-free; render children use no React Query/API clients; only the gallery owns Overview local state; only the model calls `deriveAchievements` and owns skill/activity/mastery/fallback derivation. `stats-actions.css`, `achievements.css`, and `latestAchievement` are absent; legacy imports/selectors are absent; base achievement-card rules live in `stats-achievements.css`; `stats-responsive.css` contains breakpoint rules only. No new production fixture seam, compatibility barrel, duplicated markup path, whole-summary child prop, or CSS alias.

**Architecture Slice:** `HomePage` continues to fetch Home/Stats and passes those contracts through `HomeHubView` to the unchanged `HomeStatsView` boundary. `HomeStatsView -> {homeStatsModel, HomeStatsDashboard, HomeAchievementGallery}` is the only new direction. `homeStatsModel -> deriveAchievements` is the only achievement-derivation direction. Pure existing domain utilities remain below the focused owners. Styling flows through `home.css -> stats.css -> {stats-layout, stats-achievements, stats-responsive, continue-card}`.

**Plan Review Gate:** Requires PRE review before execution.

## Architecture map

### Files to create

- `frontend/src/features/home/components/HomeStatsView.test.tsx`
- `frontend/src/features/home/components/home-stats/homeStatsModel.ts`
- `frontend/src/features/home/components/home-stats/homeStatsModel.test.ts`
- `frontend/src/features/home/components/home-stats/HomeStatsDashboard.tsx`
- `frontend/src/features/home/components/home-stats/HomeAchievementGallery.tsx`
- `docs/goals/home-overview-ownership/PRE_SLICE_BASELINE.md`
- `docs/goals/home-overview-ownership/EVIDENCE.md`
- `docs/goals/home-overview-ownership/evidence/home-overview-desktop.png`
- `docs/goals/home-overview-ownership/evidence/home-overview-mobile.png`

### Files to modify

- `frontend/src/features/home/components/HomeStatsView.tsx`
- `frontend/src/styles/features/home.css`
- `frontend/src/styles/features/home/stats.css`
- `frontend/src/styles/features/home/stats-achievements.css`
- `frontend/src/styles/features/home/stats-responsive.css`
- `frontend/src/features/home/utils/achievements.ts`
- `frontend/src/features/home/utils/achievements.test.ts`
- `scripts/checks/check_architecture_boundaries.py`
- `backend/common/tests/test_architecture_guard_algorithms.py`

### Files to delete

- `frontend/src/styles/features/home/stats-actions.css`
- `frontend/src/styles/features/home/achievements.css`

### Files to avoid

- `frontend/src/features/home/components/HomeHubView.tsx` and its test
- `frontend/src/features/home/components/home-hub/**`
- `frontend/src/features/home/components/HomeLoadoutView.tsx`
- `frontend/src/features/home/components/HomeRankBadge.tsx`
- `frontend/src/features/home/pages/HomePage.tsx`
- `frontend/src/features/home/preview/**`
- `frontend/src/features/home/api/**`, `types.ts`, and achievement image/catalog definitions other than deleting `latestAchievement`
- `frontend/src/features/stats/**`
- `frontend/src/app/router.tsx` and `frontend/src/app/layouts/HomeLayout.tsx`
- backend, generated API contracts, query keys, shared rank/cosmetic/story/sprite/effect/wallet owners, and all Slice 1-4 artifacts outside the two additive architecture files

### Source of truth and paths

| Concern | Owner/read path | Write path |
|---|---|---|
| Home progress/KPIs | backend Home summary -> `HomePage` -> Hub -> Overview | none |
| Stats/profile/activity | backend Stats summary -> `HomePage` -> Hub -> Overview | none |
| Overview presentation DTO | `homeStatsModel(home, stats)` | none |
| Achievement ledger | model -> `deriveAchievements(home, stats)` | none |
| Achievement filter | `HomeAchievementGallery` local state | gallery buttons only |
| Continue destination | `storyPath()` | React Router navigation |
| Overview styles | four canonical files imported by `stats.css` | stylesheet cascade only |

### Integration points

- The named `HomeStatsView` export and two-prop contract remain unchanged; its render children receive only the presentation DTO slice or `Achievement[]`.
- `HomeHubView` continues conditional Overview mounting exactly as today.
- Existing fixture modules are used only by tests and design preview; production receives no fixture prop.
- Existing CSS class names remain stable so this is an ownership/cutover slice, not a redesign.

### Role enforcement matrix

| Role | Required ownership | Forbidden imports/markers |
|---|---|---|
| `HomeStatsView` | `useMemo`, `storyPath`, one `buildHomeStatsModel` call, `.home-overview-grid`, one `HomeStatsDashboard` render, one `HomeAchievementGallery` render | `useState`, `deriveAchievements`, `GitCommandIcon`, achievement icons/filter constants, skill/activity helper names, `.home-overview-stats-panel`, `.home-overview-achievements-panel`, API/query modules |
| `homeStatsModel` | `HomeSummary`/`StatsSummary` types, `deriveAchievements`, exported `HomeStatsModel`/`HomeStatsDashboardModel`, skill adaptation, 14-day activity weighting/padding, mastery/star bands, fallback/KPI derivation | React/JSX, router, icons/components, DOM/window/document, CSS class strings, hooks, API/query modules |
| `HomeStatsDashboard` | `HomeStatsDashboardModel`, formatting, `GitCommandIcon`, `SkillProfileBars`, `ActivityHeatmap`, `.home-overview-stats-panel`, progress/activity/story/KPI markup | Home/Stats summary types or raw `home`/`stats` props, `deriveAchievements`, model builder, `useState`, router/Link, achievement filter/card markers, API/query modules |
| `HomeAchievementGallery` | `Achievement[]`, `useState`, filter constants/filter-before-slice logic, `.home-overview-achievements-panel`, achievement cards/styles | Home/Stats summary types or raw `home`/`stats` props, `deriveAchievements`, model builder, router/Link, `GitCommandIcon`, skill/activity/story/KPI markers, API/query modules |
| Every child/model | one-way import below `HomeStatsView`; only named narrow props | imports of `HomeStatsView`, `HomeHubView`, `HomePage`, render props, object spreads across component boundaries, dynamic/require/template bypasses |
| CSS entry/owners | `home.css` imports `stats.css`; `stats.css` imports exactly layout, achievements, responsive, continue card; achievement base selectors live in `stats-achievements.css`; `stats-responsive.css` begins with media rules | deleted-file imports, `.home-stats-*`, `.home-stat-*`, `.home-meter-*`, old `.home-activity-*`, `.home-awards*`, `.home-award-*`, base selectors outside their owner |

## Task board

### Task 1 — Freeze preservation and target-perspective baseline

**Exact scope:** Record current `git status --short`, SHA-256/deletion state for every pre-existing dirty path, full/diff hashes for the two additive architecture files, source/style hashes, Home files-to-avoid hashes, current line counts, focused/full test baseline, and current selector inventory. Start isolated Vite on a new strict non-default port with `VITE_API_BASE_URL=/api` and exact contract-valid same-origin fixtures for `http://127.0.0.1:<port>/api/progress/wallet/`, `http://127.0.0.1:<port>/api/skills/learned/`, and `http://127.0.0.1:<port>/api/shop/catalog/`. In one fresh isolated browser session, assert each exact URL is requested once on initial Overview load and that cross-origin API request count is zero. Capture rich Overview screenshots and computed layouts in bands straddling every live breakpoint (1440, 1190, 1170, 810, 750, 530, 470, and 390 widths); viewport changes are reload-free so request counts remain one each. Capture filter/reset, exact `/stories/arcane-spire` Continue target, console, and page-error behavior. Stop only the identity-checked process/session tree.

**Allowed files:** `PLAN.md`, `GOAL.md`, `PRE_SLICE_BASELINE.md`, temporary evidence outside both workspace roots.

**Verification:** Hash/manifest replay script; baseline focused tests; browser measurements; closed-port assertion.

**Acceptance evidence:** Reproducible pre-slice manifest plus desktop/mobile screenshots and breakpoint table.

**Parallel:** No. This freezes the tree before implementation.

### Task 2 — Add a passing direct Overview characterization baseline

**Exact scope:** Render the current real named `HomeStatsView` under a memory router with the existing rich/empty Home and Stats fixtures. Freeze public props, exact Continue link, skill rows/meters, 14-cell padding/intensity semantics, honest finish-rate use, value precedence, 99-vs-100-command accuracy threshold, achievement totals/points, filter-before-eight-card slicing, All/Unlocked/Locked filtering, filter reset after unmount/remount, accessibility, empty formatting, and non-mutation of inputs. This is a passing behavior characterization baseline; do not add structure assertions or mock planned owners.

**Allowed files:** `HomeStatsView.test.tsx` only.

**Verification:** From repository root: `npm --prefix frontend test -- src/features/home/components/HomeStatsView.test.tsx src/features/home/utils/achievements.test.ts`.

**Acceptance evidence:** The direct behavior lane passes before cutover and remains green after cutover. Expected structure-rejection failures are reserved for Task 5 synthetic guard fixtures.

**Parallel:** No.

### Task 3 — Atomically cut over component ownership

**Exact scope:** Create `homeStatsModel`, `HomeStatsDashboard`, and `HomeAchievementGallery`; move existing logic/markup without changing visible copy, class names, ordering, arithmetic, data precedence, or the public `HomeStatsView` export. Keep summary objects immutable. The composition root owns `.home-overview-grid`, the Link/story path, one memoized model build, and renders both children exactly once. The pure model owns all skill/activity/mastery/fallback derivation and calls `deriveAchievements`. Dashboard owns formatting plus all progress/activity/story/KPI markup and receives exactly `dashboard={model.dashboard}`. Gallery receives exactly `achievements={model.achievements}`, and owns `useState`, filter totals/slicing, styles, and cards. Add pure model tests for weighting/padding, null handling, clamping/star bands, fallbacks, input immutability, and DTO identity.

**Allowed files:** `HomeStatsView.tsx`, `home-stats/*.ts`, `home-stats/*.tsx`, and the tests from Task 2.

**Verification:** From repository root: `npm --prefix frontend test -- src/features/home/components/HomeStatsView.test.tsx src/features/home/components/home-stats/homeStatsModel.test.ts src/features/home/utils/achievements.test.ts`; scoped ESLint; TypeScript build.

**Acceptance evidence:** Role line caps, unchanged public contract, narrow DTO/achievement-array props, one-way imports, focused behavior parity.

**Parallel:** No. The composition and all three owners cut over together.

### Task 4 — Cut over CSS ownership and delete legacy paths

**Exact scope:** Move base `.home-overview-achievement-card*` rules from `stats-responsive.css` to `stats-achievements.css`. Leave only media/breakpoint rules in `stats-responsive.css`, appending the still-live 1180/820/540 rules in the same effective cascade order. Remove imports of `stats-actions.css` and `achievements.css`; delete both files. Delete `latestAchievement` and its self-only test while preserving the 19-item achievement catalog and all runtime-used exports. Do not rename live classes or redesign values. Keep `.home-ref-grid[hidden]` in `stats-layout.css`; its ownership move is a separate Slice 4 Profile CSS task.

**Allowed files:** `home.css`, `stats.css`, `stats-achievements.css`, `stats-responsive.css`, the two CSS deletion targets, `achievements.ts`, and `achievements.test.ts`.

**Verification:** Exact old-selector and `latestAchievement` searches return empty; achievement utility tests; CSS architecture gate; production build; browser computed-style parity at all baseline widths. The deterministic matrix records `grid-template-columns` for `.home-overview-grid`, `.home-overview-achievement-grid`, `.home-overview-master-row`, `.home-overview-stat-subgrid`, `.home-overview-kpi-row`, `.home-overview-command-row`, `.home-overview-story-body`, and `.home-overview-achievement-card`, plus each selector's bounding width and document `scrollWidth/clientWidth`, at 1440, 1190, 1170, 810, 750, 530, 470, and 390 pixels.

**Acceptance evidence:** Deleted legacy files, one canonical style path, byte-for-byte property/cascade equivalence for the live Overview states.

**Parallel:** No. Cascade changes require sequential visual comparison.

### Task 5 — Install additive ownership enforcement

**Exact scope:** Add canonical alias/relative/static/dynamic/require/template-aware Home Overview role checks. Enforce required files, direction, line limits, exactly one model build and one render/import per child, model purity/sole derivation ownership, narrow child props, forbidden state/query/router/achievement/progress markers per role, no reverse imports, exact CSS owner imports, absent deleted files/helper/legacy selectors, and breakpoint-only `stats-responsive.css`. Preserve all existing architecture functions, calls, and tests.

**Allowed files:** `scripts/checks/check_architecture_boundaries.py`, `backend/common/tests/test_architecture_guard_algorithms.py`.

**Verification:** `pytest backend/common/tests/test_architecture_guard_algorithms.py -q`; live architecture checker; synthetic bypass assertions for every role and CSS cutover.

**Acceptance evidence:** Guard rejects displaced ownership and live tree passes.

**Parallel:** No. Shared additive files require preservation review.

### Task 6 — Verify, prove, and review the cutover

**Exact scope:** Run focused/full/static/architecture/quality/protected gates. Repeat the deterministic browser lane in one fresh isolated session using the same three exact same-origin fixture URLs and all reload-free baseline widths. Prove each exact API URL occurs once and cross-origin API count is zero; rich/empty values, filter counts/state/accessibility and reset, exact Continue target, 14 heatmap cells, the full computed-style matrix, no overflow, clean console/page errors, and screenshot comparison. Remove temporary helpers, close exact processes/ports, produce `EVIDENCE.md`, and request POST plan, correctness, maintainability, and verifier reviews. Report the pre-existing OpenAPI/runtime `activity`/`activity_trend` and `headlines`/`headline` drift as a separate unproven contract repair; do not claim authenticated API-path proof from fixtures.

**Verification commands:**

```text
npm --prefix frontend test -- src/features/home/components/HomeStatsView.test.tsx src/features/home/components/home-stats/homeStatsModel.test.ts src/features/home/utils/achievements.test.ts
npm --prefix frontend test
npm --prefix frontend run lint
npm --prefix frontend run lint:dead
npm --prefix frontend run build
npm --prefix frontend run quality:fast
npm --prefix frontend run ui:typography-check
python -m pytest backend/common/tests/test_architecture_guard_algorithms.py -q
python scripts/checks/check_architecture_boundaries.py
python scripts/check_css_architecture.py
python scripts/check_documentation_current.py
git diff --check
```

**Acceptance evidence:** Final screenshots, breakpoint/request/interaction traces, full gate results, preservation replay, and review verdicts. The typography command may report only the three pre-existing untouched Admin Curriculum `text-[10px]` baseline violations; any Home or new violation is a blocker.

**Parallel:** Static read-only gates may run concurrently after implementation; browser proof, cleanup, preservation audit, and reviews remain sequential.
