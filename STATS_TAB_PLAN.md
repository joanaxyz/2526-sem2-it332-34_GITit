# Plan — Replace "Performance" with a gamified "Stats" tab + Dashboard refactor

## Goal
Retire the jargon-heavy Performance tab (SCR/CAR/HLCR/RTA/ARC acronyms) and ship a friendly, gamified **Stats** tab built around:
- a **Skill Profile radar** (6 axes of "what kind of git user you are"),
- a **friendly Activity trend** chart ("how much you did" over time),
- **plain-language KPI cards**.

Then refactor the **Dashboard** into a gamified "home hub" (it predates gamification), with a clean split:
- **Dashboard = hub** (continue, streak, coins, recent, next goal)
- **Stats = depth** (radar + trend + KPI cards)

Decisions locked with the user: radar axes = **skill qualities**; charts = **custom SVG** (no new dep); page split = **hub vs depth**.

---

## KPI analysis (what to measure, remove, reframe)

### Remove / stop surfacing as headline
- **Acronyms** SCR, CAR, HLCR, RTA, ARC as user-facing labels — internal only.
- **ARC (avg retry count)** as a headline number: "lower is better" reads backwards on a chart. Reframe as the inverse "first-try" signal or demote to a tooltip.
- `ModulePerformanceCard` per-storey bar wall — overlaps the Tower page; drop from the headline (keep raw storey_kpis available for an optional drill-down).

### Terminology — "Quest" as the unit noun (UI only, no model renames)
The metric SCR ("Scenario Completion Rate") names an entity users never see, and "scenario" is already taken in code: `Challenge` *is* the workflow scenario (`ChallengeLevel.scenario` / `ChallengeRun.workflow_scenario` FKs, `related_name="workflow_scenarios"`), and `scenario_context` is the per-task brief. **Do not rename `AdventureProblem` / `ChallengeLevel`** — it would overload `scenario` and force a costly migration across ~24 files for worse naming.

Instead, adopt **"Quest"** as the single user-facing noun for "one solvable git task" (an `AdventureProblem` or `ChallengeLevel`), at the label/copy layer only. DB models, fields, and FKs stay exactly as they are. All friendly labels below use "Quest"; SCR is dropped from the UI in favor of **Quests Completed / Finish Rate**.

### Keep, but rename to friendly language
| Internal | Friendly label | Meaning shown to user |
|---|---|---|
| scr / completion | **Quests Completed** (count) + **Finish Rate** (%) | how many runs you finished — adventures + challenges |
| car (+ adventure correctness) | **Accuracy** | how clean your commands are — now blends both modes |
| hlcr | **Boss Floors Cleared** | hard challenges beaten (challenge-only by nature; labeled as such) |
| rta | **Comebacks** | retries you turned into wins (challenge-only by nature; labeled as such) |
| first_attempt_stars | **Perfect Clears** ⭐ | solved first try — adventures + challenges |
| streak | **Day Streak** 🔥 | consecutive active days |
| wallet/coins | **GitCoins Earned** | from CoinTransaction ledger |
| command count | **Commands Run** | total git commands executed |

### Stated goal — balance adventures and challenges in the metrics
Today the headline KPIs are **challenge-weighted**; adventures barely register despite producing rich per-attempt scores that are currently unused:
- **Includes adventures:** raw counts, Finish Rate (`scr`), Perfect Clears (`first_attempt_stars`), streak.
- **Challenge-only (adventures excluded):** Accuracy (`car`, only records with a `challenge_run`), Boss Floors (`hlcr`, a `ChallengeLevel.difficulty` concept), Comebacks (`rta`, `ChallengeRun`-only fields), retry trends, and the entire per-storey breakdown.
- **Misleading:** `arc` divides challenge-only retries by the *combined* completed count.

`AdventureProblemAttempt` already records `correctness_score`, `efficiency_score`, `independence_score`, `mastery_gain`, `hint_count`, `command_count`/`counted_command_count`, and `AdventureMastery.strength` — none of it reaches the user. **The Stats endpoint is where adventures become first-class.** Every axis below blends both session types wherever the data exists, and `headline` numbers are labeled by source so neither mode is silently dropped.

### New — the Stats identity (Skill Profile radar, 6 axes, 0–100)
All derivable from existing data; each axis **blends adventures + challenges**:
1. **Accuracy** — challenges: `command_accuracy_rate`; adventures: avg `AdventureProblemAttempt.correctness_score`. Combine (weighted by attempt/session count).
2. **Efficiency** — adventures: avg `AdventureProblemAttempt.efficiency_score`; challenges: `counted_action_total` vs `minimum_counted_for_session` → per-session efficiency %. Combine.
3. **Independence** — adventures: avg `AdventureProblemAttempt.independence_score` (100 − 25×hints). Challenges have no hints today → adventure-driven, but counted only when adventure attempts exist (no fake 100s).
4. **Consistency** — derived from streak + active-day ratio over recent window (already mode-agnostic).
5. **Mastery** — adventures: avg `AdventureMastery.strength / required_successful_attempts` over introduced problems; challenges: cleared-levels ÷ attempted-levels. Combine across both ladders.
6. **Coverage** — problems completed ÷ total available across **both** adventure problems and challenge levels (breadth of curriculum touched).

> Implementation note: each axis computes a value per session type and merges them weighted by volume, returning `null` only when *neither* mode has data — so a user who only does adventures still gets a full, non-zero radar.

### New — Activity trend (friendly, easy to read)
Daily series over last ~14–30 days: **problems completed per day** (primary line) with **commands run** as a secondary/area, plus a "this week vs last week" delta caption. Source: `ProblemCompletion.completed_at`, `CommandStep.created_at`, optional `CoinTransaction.created_at`.

---

## Backend changes

**New endpoint:** `GET /api/progress/stats/` → `StatsSummaryAPIView`.
- `backend/progress/services.py`: add `MetricsService.stats_summary(user)` returning:
  - `skill_profile`: `[{key, label, value}]` for the 6 axes (0–100, `null` when no data).
  - `activity_trend`: `[{date, problems_completed, commands_run}]` for last N days (zero-filled).
  - `headline`: friendly KPI block — `quests_completed`, `finish_rate`, `accuracy`, `boss_floors`, `comebacks`, `perfect_clears`, `day_streak`, `gitcoins`, `commands_run`. Mode-specific metrics (`boss_floors`, `comebacks`) carry a `scope: "challenge"` flag so the UI can frame them honestly rather than implying they cover adventures.
  - Reuse existing `_rate` / `_average_percent` helpers. **Add adventure aggregates** over `AdventureProblemAttempt` (correctness/efficiency/independence/mastery_gain, hint/command counts) and `AdventureMastery.strength`; merge with challenge aggregates per axis weighted by volume. `commands_run` sums `CommandStep` across both `session` (challenge) and `attempt` (adventure) links; coins via `Wallet`/`CoinTransaction`.
  - **Fix `arc` dilution:** if retained anywhere, compute its denominator from challenge-completed only (or drop it per the radar reframe), so adventures no longer skew it.
- `backend/progress/views.py`: add `StatsSummaryAPIView` (mirror `DashboardSummaryAPIView`).
- `backend/progress/urls.py`: register `stats/`.
- Tests: `backend/progress/tests/test_stats.py` — empty-user (nulls/zeros), populated-user (axes in range, trend zero-filling), idempotent with existing dashboard endpoint.

Keep `/api/progress/dashboard/` intact (Dashboard hub still consumes counts/streak/coins).

## Frontend changes

**New feature folder `frontend/src/features/stats/`:**
- `api/statsApi.ts` — `statsApi.summary()` → `GET /progress/stats/`.
- `types.ts` — `StatsSummary` (skill_profile, activity_trend, headline).
- `pages/StatsPage.tsx` — replaces PerformancePage; reuses the aurora-orb background + `animate-fade-in-up` pattern.
- `components/SkillProfileRadar.tsx` — **custom SVG** hexagon radar: gridlines, neon polygon with glow filter + gradient fill, axis labels, animated grow-in (reuse easing from `useAnimatedWidth`). Tooltip per axis in plain language.
- `components/ActivityTrendChart.tsx` — **custom SVG** line/area: gradient stroke (#00F5D4→#00B4D8), soft fill, hover dots, "X this week (▲/▼ vs last)" caption.
- `components/StatHighlightCards.tsx` — friendly KPI cards reusing `useCountUp` + glow styling (replaces `ProgressSummaryCards`).

**Routing / nav:**
- `frontend/src/app/router.tsx`: change `/performance` → `/stats` rendering `StatsPage` (keep `/performance` as `<Navigate replace to="/stats" />` for back-compat).
- `frontend/src/app/layouts/DashboardLayout.tsx` (navItems ~L28–32): rename tab `Performance`→`Stats`, route `/stats`, icon `BarChart2`→`Radar` (or `Activity`) from lucide-react.
- `frontend/src/shared/api/queryKeys.ts`: add `statsSummary`.

**Dashboard refactor (`frontend/src/features/dashboard/pages/DashboardPage.tsx`) — hub:**
- Hero **Continue / Current Track** (existing `CurrentTrackCard`, lift "Open Tower" CTA).
- **Day Streak** (`StreakCard`) + **GitCoins** mini-card (reuse wallet `GitCoinIcon`) side by side.
- **Recent quests** (`RecentActivityList`, friendlier labels).
- **Next goal** nudge card (nearest storey chest threshold / next mastery box) — light addition, optional if time-boxed.
- Remove analytical widgets that now live in Stats (`RetryTrendCard`, `FirstAttemptStars` move to Stats or are dropped from hub).

**Cleanup:**
- Delete `pages/PerformancePage.tsx`; retire/move `components/ProgressSummaryCards.tsx` and `components/ModulePerformanceCard.tsx` (delete once Stats replaces them). Keep storey_kpis drill-down only if we add an optional Stats accordion.

---

## Critical files
- Backend: `backend/progress/services.py`, `backend/progress/views.py`, `backend/progress/urls.py`, new `backend/progress/tests/test_stats.py`.
- Frontend new: `frontend/src/features/stats/{api/statsApi.ts,types.ts,pages/StatsPage.tsx,components/SkillProfileRadar.tsx,components/ActivityTrendChart.tsx,components/StatHighlightCards.tsx}`.
- Frontend edit: `app/router.tsx`, `app/layouts/DashboardLayout.tsx`, `shared/api/queryKeys.ts`, `features/dashboard/pages/DashboardPage.tsx`.
- Frontend remove/move: `features/dashboard/pages/PerformancePage.tsx`, `components/ProgressSummaryCards.tsx`, `components/ModulePerformanceCard.tsx`.

## Verification
1. **Backend:** `python backend/manage.py test progress` (new stats tests pass). Hit `GET /api/progress/stats/` for a seeded user — verify 6 axes in 0–100, zero-filled trend, friendly headline keys. **Adventure-inclusion test:** a user with *only* adventure runs (no challenges) gets a full non-zero radar (Accuracy/Efficiency/Independence/Mastery/Coverage populated), `commands_run` counts their adventure commands, and challenge-scope KPIs (`boss_floors`, `comebacks`) report empty-with-scope rather than a misleading 0%.
2. **Frontend typecheck/lint:** `npm run build` / `tsc` clean; no leftover imports of deleted components.
3. **Manual (run app):** log in → **Stats** tab renders radar (animates in), trend chart with hover, friendly KPI cards; new user shows graceful empty state (no NaN/`null` leaks). `/performance` redirects to `/stats`.
4. **Dashboard:** hub shows Continue + Streak + Coins + Recent + Next goal, matches neon/medieval theme, no duplicated analytics from Stats.
5. **Regression:** Tower + wallet badge unaffected; `dashboardSummary` query still used by hub.
