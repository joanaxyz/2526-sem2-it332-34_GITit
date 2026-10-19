# Learner Progress KPI instrument — execution evidence

Date: 2026-10-19 (Asia/Manila).

## Outcome and board

- 1A: baseline captured before implementation, including hashes of pre-existing work and current screen.
- 1B: learner/Admin parity proved by a real DRF learner request and staff per-player request; measured values, measured zero, empty values, retry-success, and eligible changed retries covered.
- 2: shared display semantics now live in `features/performance/utils/performanceKpis.ts`; Admin consumes the same definitions and evidence text.
- 3: ready-data learner instrument renders five evaluation measures and supplementary retry recovery; selection is local.
- 4: no-prop Home results query owner integrated; mixed Home/Stats result model and simultaneous module chart grid removed; responsive and reduced-motion browser evidence captured.
- 5: ownership guards, algorithm tests, architecture documentation, and supporting checks complete; POST, correctness, and maintainability reviews pass. Final isolated frontend verification is recorded below.

## Deliberate adjustments from the reviewed plan

The workspace had advanced before execution: the curriculum now uses Arcane Spire and the Stats headline is scoped to that active curriculum. This work preserves the current executable service and labels the upper meter `Overall finish rate — active curriculum, all modules`; it does not restore retired story records or broaden the service's scope.

The architecture gate rejects executable feature-root modules. The shared definition and its test therefore live under `features/performance/utils/` rather than the planned feature root. The displaced mini-column renderer became unused after its sole consumer was removed, so `shared/components/charts/MiniColumnChart.tsx` and its unique selectors were also deleted. Activity's shared column styling was retained.

No server formula, endpoint, serializer, generated OpenAPI, or generated TypeScript contract was edited by this task.

## Target-perspective browser evidence

The real `/home?view=progress` route ran through `HomePage`, auth bootstrap, production API wrappers, React Query, and the actual new UI. A temporary HTTP fixture proxy on 127.0.0.1:5188 forwarded application modules to the isolated Vite server on 5187 and answered only local API requests with typed fixture data. This avoids touching the user's database. The design preview was used separately for empty-state visual evidence. Temporary proxy source is outside the repository at `C:/Users/Joana/AppData/Local/Temp/kpi-progress-fixture-server.mjs`.

The browser CLI's request-mocking command acknowledged routes without intercepting the requests in this installed version. The HTTP proxy provided an actual request/response lane instead. Offscreen controls were explicitly scrolled into view before pointer interaction.

| Check | Observed result |
| --- | --- |
| Initial performance request | Exactly one GET `/api/progress/performance/` on the real Home mount |
| Selection | Selecting ARC and CAR produced zero API requests |
| Activity range | Week and Year produced only GETs to `/api/progress/stats/activity/?window=week` and `?window=year` |
| Invariant values | SCR 75.4%, CAR 91%, HLCR 61.5%, ARC 1.60, RTA 60%, recovery 63.6% before and after range changes |
| Changed retries | Selected RTA comparison contained only M3 (33.3%, 1/3) and M4 (100%, 2/2) |
| CAR | Overall-only explanation, no fabricated module values |
| Empty account | All six measures have `data-state=empty`, em dash, and `Not measured yet`; RTA explains changed retries in Modules 3–4 |
| Loading | Four-second delayed performance response shows a stable local skeleton while activity remains usable |
| Error | A fixture 503 shows the inline Retry control while activity remains visible |
| Recovery | After restoring the fixture, Retry made one performance GET and restored the instrument |
| Keyboard | Focus first measure → Tab → Enter selected Commands accepted; the focused button had a 2px outline |
| Reduced motion | `matchMedia('(prefers-reduced-motion: reduce)')` true; orbital reading transition computed as 0.000001s under the project's global reduction rule |
| Overflow | Desktop: scrollWidth 1430 ≤ viewport 1440; tablet 900 ≤ 900; mobile 380 ≤ 390 |
| Settled tablet chart | At 900px, both activity chart wrappers, parents, and SVGs measured 876px after ResizeObserver settled; the refreshed screenshot shows the full-width plot |
| Browser errors | No page errors and no Vite error overlay in the verified ready session |

Screenshots:

- [Desktop](evidence/progress-desktop.png)
- [Tablet](evidence/progress-tablet.png)
- [Mobile full page](evidence/progress-mobile.png)
- [Mobile measures](evidence/progress-mobile-measures.png)
- [Mobile comparison](evidence/progress-mobile-comparison.png)
- [Keyboard focus and reduced motion](evidence/progress-focus-reduced-motion.png)
- [Empty changed-retry state](evidence/progress-empty.png)
- [Loading](evidence/progress-loading.png)
- [Error with activity retained](evidence/progress-error.png)

The screenshots include the existing Home shell, background, navigation, and first-companion nudge. Those components remain user-owned.

Computed text colors were foreground rgb(235,246,250), the established secondary token rgba(235,246,250,0.76), cyan rgb(0,163,255), empty-state mist rgb(117,143,159), and amber rgb(243,210,122). Against the observatory surface rgb(15,23,36), WCAG contrast ratios are respectively 16.34, 9.76 (after alpha compositing), 6.58, 5.29, and 12.25. Text state and evidence stay readable without hover or color recognition.

## Supporting verification

- Baseline: 40 focused frontend tests passed; 15 performance/scope backend tests passed.
- New focused frontend: 57 tests in seven files passed.
- After shared formatting/status consolidation: 39 Admin/performance tests passed; after the accessible-name correction, 16 Home/instrument tests passed.
- Backend parity and architecture algorithms: 33 passed after integration.
- Production TypeScript/Vite build: passed after concurrent route edits settled.
- ESLint: passed.
- Dead-code check: passed after removing the displaced mini-chart and unused type re-export.
- API contract currentness, wrapper usage, and type adoption: passed.
- Documentation currentness, CSS architecture, and Ruff on changed Python: passed.
- Displaced-path search: no old KPI row, four-chart grid, HomeResultsModel, moduleColumns, MiniColumnChart, or old Admin evidence import remains in frontend runtime code.
- Final fresh frontend run: **142 files, 997 tests passed**, using the configured isolation (`npm --prefix frontend test -- --bail=1 --reporter=verbose`, exit 0, 474.45s).
- Earlier verification attempts overlapped file moves/deletions; a non-isolated diagnostic showed cross-suite mock contamination, and a mid-edit isolated run stalled and was interrupted. The final fresh run above supersedes those attempts and passed both previously failing Admin suites without further product changes.

Two repository checks already failed before this task and still fail in unrelated files:

- Architecture size limit: `frontend/src/shared/level/components/useWorkspaceTourTransform.ts` has 423 lines.
- Typography minimum: `frontend/src/styles/features/game-outcome.css:323` has 0.6rem text.

The task-specific Home/performance ownership tests pass. These unrelated production files were not edited.

## Preservation and review

The pre-slice manifest is in `PRE_SLICE_BASELINE.md`. Existing mastery-star behavior, exact zero tier-completion semantics, Arcane Spire labels, and other user changes in overlapping Home files were preserved. Independent curriculum/route work continued during this execution; changes outside this task were neither reverted nor staged.

Protected final hashes:

- `backend/progress/services/metrics.py`: `3EBD4BAD03F4F3CE292F1E33A13045ECEB3478AA69406262FDFF626A465D8883`
- `HomeSkillsPanel.tsx`: `CF6B421FC6BB8DACDB0BB66F18F4946F0B80E0117288454E4A0C8F050395724B`
- generated `apiTypes.ts`: `DBCD7ABB8E4358FD4B7B3BF78BB96214C1E39A370042E949B82E40476573C33D`
- generated `openapi.json`: `86760C71BDF64A21A48238583B3A4D46E98997533828CB5D72B3F7BC86BBFA1F`

The service hash differs from the baseline `95A73A79EE539B75B1497175EF508F3BF7299BDB4ADAB377168B301084920C9A` because independent curriculum work advanced during this execution; this task did not edit it. `HomeSkillsPanel.tsx` and `backend/common/models.py` match their baseline hashes (the latter `A5EA601490E2D521D493DF44B57B437A653257EE9A43DDB023A1DEFBAD991314`). Generated contracts were not edited by this task.

POST review verdict: **aligned**, no findings. Correctness: **pass**. Maintainability: **pass**. Review confirmed formula/data integrity, empty states, query ownership, Admin parity, responsive behavior, accessibility, shared semantic helpers, established styling tokens, and deletion of displaced paths.

The temporary HTTP proxy and the four task-owned browser sessions were stopped after evidence capture. The Vite preview remains available at `http://127.0.0.1:5187/design-preview/home?view=progress`.
