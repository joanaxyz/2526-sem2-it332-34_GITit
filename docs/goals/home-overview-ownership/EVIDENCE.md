# Home Overview Ownership Cutover Evidence

## Outcome

Slice 5 replaced the 339-line mixed-owner `HomeStatsView` with four explicit owners while preserving the public `HomeStatsView({ home, stats })` boundary and the rendered DOM/class contract:

- `HomeStatsView.tsx` — 39-line composition and Continue-story owner.
- `homeStatsModel.ts` — 110-line React/router-free derivation owner.
- `HomeStatsDashboard.tsx` — 163-line skill, activity, story, and KPI render owner.
- `HomeAchievementGallery.tsx` — 91-line achievement totals, filter state, and card render owner.

The root memoizes one model build and passes exactly `dashboard={model.dashboard}` and `achievements={model.achievements}`. The model is the sole production caller of `deriveAchievements`; child renderers receive no raw Home/Stats summaries.

The CSS path is now `home.css -> stats.css -> {stats-layout.css, stats-achievements.css, stats-responsive.css, continue-card.css}`. Base achievement-card rules live in `stats-achievements.css`, and `stats-responsive.css` contains top-level media rules only. The 163-line `stats-actions.css`, 226-line `achievements.css`, their imports and legacy selectors, and the dead `latestAchievement` helper/self-only test are gone.

## Behavior evidence

The direct component test renders the real named Overview under a memory router. Together with pure-model and achievement-ledger tests, the focused lane proves:

- exact `/stories/arcane-spire` Continue destination;
- 12 rich/empty skill rows and null formatting;
- 14-day tail selection, left padding, `commands + levels * 4` weighting, and intensity levels;
- mastery averaging/clamping and one-to-three star bands;
- level/perfect-clear fallback precedence, honest finish-rate use, and the 99/100-command accuracy threshold;
- KPI formatting, achievement totals/points, filter-before-eight slicing, All/Unlocked/Locked state, remount reset, accessibility state, and frozen-input non-mutation.

Focused result: 3 files / 13 tests passed. Full result: 67 files / 465 tests passed.

## Browser evidence

The isolated dev server used `VITE_API_BASE_URL=/api` and contract-valid same-origin fixtures. In one fresh browser session, the initial rich Overview requested each exact URL once:

| Request | Count |
|---|---:|
| `/api/progress/wallet/` | 1 |
| `/api/skills/learned/` | 1 |
| `/api/shop/catalog/` | 1 |
| Cross-origin `/api/` requests | 0 |

All reload-free viewport changes and the Profile/Overview round trip retained those counts. The exact rich trace was:

- skills `100,95,88,82,74,68,62,55,40,30,20,0%`;
- mastery `60%`, `2 of 3` stars;
- heatmap levels `2,1,3,2,1,4,2,3,2,4,2,4,3,3`;
- story `43 / 26 / 4`, finish rate `76%`;
- KPIs `83% / 62% / 1.60 / 91%`;
- achievements `16 / 19`, `325 / 435 pts`, All `8` cards (`7/1`), Unlocked `8/8`, Locked `3/3`;
- keyboard order `All -> Unlocked -> Locked`;
- leaving Overview for Profile unmounted the gallery, and returning reset the filter to All.

The empty trace was mastery `0%`, twelve `--` skills, fourteen level-0 cells, story `0 / 0 / 0`, finish rate `0%`, four `--` KPIs, `0 / 19` unlocked, and eight visible locked cards.

Console output contained only Vite connection and React DevTools development notices. Page errors were empty. The isolated session was closed, verified Vite PID `6768` was stopped, port `51063` was confirmed free, and the temporary Vite config was deleted.

### Responsive parity

Every computed row below is identical to the pre-slice baseline. Each cell is `grid-template-columns @ rounded bounding width`; every width had `scrollWidth == clientWidth` and no horizontal overflow.

| Viewport | Overview | Achievement grid | Master row | Stat subgrid | KPI row | Command row | Story body | Achievement card |
|---:|---|---|---|---|---|---|---|---|
| 1440 | `979.859 400.219 @1393` | `366.219 @366` | `724.266 208 @946` | `448.484 485.844 @946` | `236.453 236.469 236.469 236.469 @946` | `28.797 208 391.734 51.188 @714` | `128 309.469 @453` | `53.594 194.609 92.453 @366` |
| 1190 | `1149.06 @1149` | `549.531 549.531 @1115` | `893.469 208 @1115` | `529.688 573.859 @1115` | `278.766 x4 @1115` | `28.797 208 560.938 51.188 @883` | `128 397.484 @541` | `53.594 377.922 92.453 @550` |
| 1170 | `1129.59 @1130` | `261.891 261.906 261.891 261.906 @1096` | `874 208 @1096` | `520.344 563.719 @1096` | `273.891/273.906 x4 @1096` | `28.797 208 541.469 51.188 @864` | `128 387.344 @531` | `53.594 90.281 92.453 @262` |
| 810 | `776 @776` | `363 363 @742` | `742 @742` | `742 @742` | `371 371 @742` | `32 363.203 254.234 48 @732` | `128 565.625 @710` | `53.594 191.391 92.453 @363` |
| 750 | `716 @716` | `333 333 @682` | `682 @682` | `682 @682` | `341 341 @682` | `32 335.547 234.875 48 @672` | `128 505.625 @650` | `53.594 161.391 92.453 @333` |
| 530 | `496 @496` | `466.812 @467` | `466.812 @467` | `466.812 @467` | `466.812 @467` | `28.797 365.641 48 @457` | `434.438 @434` | `53.594 295.203 92.453 @467` |
| 470 | `436 @436` | `406.812 @407` | `406.812 @407` | `406.812 @407` | `406.812 @407` | `28.797 305.641 48 @397` | `374.438 @374` | `48 344.438 @407` |
| 390 | `356 @356` | `326.812 @327` | `326.812 @327` | `326.812 @327` | `326.812 @327` | `28.797 225.641 48 @317` | `294.438 @294` | `48 264.438 @327` |

The post-cutover screenshots are byte-for-byte identical to the retained pre-slice files:

| Artifact | Dimensions | Bytes | SHA-256 |
|---|---:|---:|---|
| `evidence/home-overview-desktop.png` | 1440x900 | 464,106 | `6ACFD8681FCB7ADD10E9D0AF5D53E5C4D72E66492355339841984C6E6CC94DDF` |
| `evidence/home-overview-mobile.png` | 390x844 | 142,746 | `49C820AE45906A969DE142103EA5594700210A57B96888FBB98EB99BBCF7A0BA` |

## Architecture enforcement

The additive guard enforces required files and line limits, canonical alias/relative/static/dynamic/require/template-aware imports, comment-trivia and type-only import handling, statement-boundary-safe ownership scans, one-way child direction, one model build and one render per child, narrow named child props, model purity and sole achievement derivation, role-specific forbidden markers, no compatibility owners, exact CSS entry imports, breakpoint-only responsive CSS, canonical base-selector ownership, deleted paths/helper, and absence of every legacy selector family.

Synthetic and live guard result: 14 tests passed. The live architecture and CSS checkers both pass. The synthetic lane includes behavior-equivalent model syntax, aliased/re-exported imports, side-effect imports followed by type-only imports, comment trivia after `from` and inside dynamic/`require` calls, multiline type-only clauses with comments/trailing commas, and grouped CSS-selector bypass attempts.

Shared-file preservation remained additive:

- checker diff moved from `698 + / 2 -` to `1265 + / 2 -`: 567 Slice-5 additions and no new deletion;
- guard-test diff moved from `319 + / 0 -` to `561 + / 0 -`: 242 Slice-5 additions and no deletion;
- every earlier function/test remains, all 18 `main` checks are invoked, and the live checker passes.

## Verification gates

| Gate | Result |
|---|---|
| Focused Home Overview/model/achievement tests | PASS — 3 files / 13 tests |
| Full frontend tests | PASS — 67 files / 465 tests |
| Full ESLint | PASS |
| Knip dead-code check | PASS |
| TypeScript + production Vite build | PASS — 2,656 modules |
| Fast quality suite | PASS — legacy terms, architecture, CSS, 2,056 seed targets, API contract/usage/type adoption, docs, CI manifest, artifacts |
| Architecture algorithm tests | PASS — 14 tests |
| Architecture boundary checker | PASS |
| CSS architecture checker | PASS |
| Documentation-current checker | PASS |
| `git diff --check` | PASS; only an unrelated pre-existing CRLF warning is printed |
| Typography minimum check | Expected baseline only — three untouched Admin Curriculum `text-[10px]` findings; zero Home/new findings |

## Preservation audit

- 69 of 69 non-architecture entries from the 71-entry pre-slice dirty manifest remain byte-identical; the other two are the explicitly additive architecture files.
- All 12 protected Home paths remain byte-identical.
- Protected `stats-layout.css` and `continue-card.css` retain their exact baseline hashes.
- No temporary browser config or listener remains.

## Separate known contract repair

This slice does not claim authenticated API-path proof. Runtime/backend/frontend Stats use `activity_trend` and `headline`, while the current OpenAPI/generated contract advertises `activity` and `headlines`. The design-preview fixture lane cannot prove that mismatch safe; it remains a separate contract-repair slice.

## Review outcomes

- POST plan review: **ALIGNED**, with no blocker, major, or minor findings. The reviewer confirmed the approved owner, boundary, cutover, deletion, CSS-cascade, preservation, and acceptance-evidence contracts.
- Correctness review: initial adversarial review exposed aliased imports, grouped CSS selectors, comment trivia, adjacent side-effect/type-only statements, and trailing-comma/type-only classifier edges. Each received a synthetic regression and correction. Final verdict: **PASS**, with no findings.
- Maintainability review: initial review removed brittle literal-expression locks, required the migrated cascade-order comment, and drove compact/comment-delimited import handling. Final verdict: **PASS**, with no findings. Residual risk is explicit: the import guard is a bounded regex-based classifier, so novel TypeScript syntax should arrive with a synthetic regression test.
- Independent verifier: **PASS**, with no blocker, major, or minor findings. It reran the 3-file/13-test focused UI lane, the 14-test architecture lane and live architecture/CSS checks; visually inspected and hash-checked both screenshots; replayed all 69 non-architecture manifest entries and protected hashes; confirmed displaced paths and one-way ownership; and confirmed that authenticated Stats API behavior is not overclaimed.

The verifier notes that request-count, console, and eight-width computed-layout traces are retained as detailed evidence text rather than raw machine-readable artifacts. Their credibility is corroborated by byte-identical screenshots, verbatim CSS migration, focused browser-oriented tests, and the preserved computed matrix. Its optional fresh full-suite replay exceeded a 180-second verifier timeout and was stopped cleanly; this does not contradict the recorded main execution pass of 67 files / 465 tests, which completed in 209.74 seconds.
