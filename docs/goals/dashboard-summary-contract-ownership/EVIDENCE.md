# Dashboard/Home Summary Contract Ownership Evidence

Captured on 2026-08-10 after executing `PLAN.md` with Krypton Execution.

## Outcome

The authenticated Dashboard/Home summary now has one exact backend-to-frontend contract. The unchanged runtime payload, Progress-owned serializers, committed OpenAPI, generated TypeScript, shared frontend type, Home feature re-export shims, and request wrapper all describe the same nine required fields:

```text
kpis + chapter_kpis + counts + completed_story_slug + completed_stories
+ streak + perfect_clears + mastery + retry_trends
```

The former loose dictionaries, object-shaped `retry_trends`, optional completion slug, handwritten `HomeSummary`, `HomeSummaryResult` intersection, and custom response generic are removed. `MetricsService.dashboard_summary()`, the URL/view, operation ID, Home production UI, rank and achievement behavior, persistence, and learner-visible values were not changed.

## Ownership Cutover

| Concern | Result |
|---|---|
| Executable values | `backend/progress/services/metrics.py::MetricsService.dashboard_summary` remains unchanged |
| Response contract | exact Dashboard serializer family in `backend/progress/serializers.py` |
| OpenAPI and TypeScript | regenerated from the backend serializer contract |
| Shared frontend type | `HomeSummary = ApiSchemas['DashboardSummaryResponse']` |
| Runtime request | returns `progress_dashboard_retrieve` directly with no response override |
| Home integration | existing type/API shims remain exact re-exports and byte-identical |

## Authenticated Real-Path Evidence

A disposable migrated test database was created, DRF `APIClient` authenticated real users, and the real `/api/progress/dashboard/` URL/view/service path was requested. Both raw payloads were then validated with `DashboardSummaryResponseSerializer`. The standalone client used Django's standard `testserver` host override; the database was torn down after the probe.

Empty user:

```json
{
  "http_status": 200,
  "serializer_valid": true,
  "chapter_kpis": {},
  "completed_stories": [],
  "completed_story_slug": null,
  "counts": {
    "abandoned": 0,
    "completed": 0,
    "failed": 0,
    "started": 0
  },
  "kpis": {
    "arc": { "denominator": 0, "numerator": 0, "value": null },
    "hlcr": { "denominator": 0, "numerator": 0, "value": null },
    "scr": { "denominator": 0, "numerator": 0, "value": null }
  },
  "mastery": 0,
  "perfect_clears": 0,
  "retry_trends": [],
  "streak": { "current": 0, "last_completed_on": null, "longest": 0 }
}
```

Representative user seeded through the real challenge-run factory with one completed run, one failed retry, and a persisted streak:

```json
{
  "http_status": 200,
  "serializer_valid": true,
  "chapter_kpis": {
    "920001": {
      "arc": { "denominator": 1, "numerator": 0, "value": 0.0 },
      "hlcr": { "denominator": 0, "numerator": 0, "value": null },
      "scr": { "denominator": 2, "numerator": 1, "value": 50.0 }
    }
  },
  "counts": {
    "abandoned": 0,
    "completed": 1,
    "failed": 1,
    "started": 2
  },
  "retry_trends": [
    {
      "attempts": 2,
      "label": "1 retry runs",
      "level_title": "Stage README Challenge",
      "retries": 1
    }
  ],
  "streak": {
    "current": 3,
    "last_completed_on": "2026-08-09",
    "longest": 5
  }
}
```

The endpoint tests additionally assert every raw top-level and nested key, primitive/list/object type, ISO date, required completion key, dynamic chapter key, and retry row before serializer validation. A payload missing `completed_story_slug` and using `{}` for `retry_trends` is rejected.

## Exact Generated Contract

The committed OpenAPI response has exactly the nine properties and requires all nine. Its important structural fragments are:

```text
kpis                 -> DashboardKpiSet
chapter_kpis         -> object with DashboardKpiSet additionalProperties
counts               -> DashboardCounts
completed_story_slug -> required nullable string
completed_stories    -> required array<string>
streak               -> DashboardStreak with nullable date
perfect_clears       -> integer
mastery              -> number/double
retry_trends         -> array<DashboardRetryTrend>
```

Nested generated components are exact:

| Component | Required fields |
|---|---|
| `DashboardKpiSet` | `arc`, `hlcr`, `scr`, each a `RateMetric` reference |
| `DashboardCounts` | `abandoned`, `completed`, `failed`, `started` integers |
| `DashboardStreak` | `current`, `longest`, nullable date `last_completed_on` |
| `DashboardRetryTrend` | `attempts`, `label`, `level_title`, `retries` |
| `RateMetric` | `denominator`, `numerator`, nullable numeric `value` |

The operation response is exactly `#/components/schemas/DashboardSummaryResponse`. Generated TypeScript exposes `chapter_kpis` as `{ [key: string]: DashboardKpiSet }`, both completion fields as required, and `retry_trends` as `Array<DashboardRetryTrend>`.

The runtime frontend ownership files now reduce to:

```ts
export type HomeSummary = ApiSchemas['DashboardSummaryResponse']
```

```ts
summary() {
  return apiOperationRequest(
    'progress_dashboard_retrieve',
    '/progress/dashboard/',
  )
}
```

## Durable Architecture Enforcement

The architecture checker now rejects:

- loose, optional, extra, secondary, or wrongly constructed Dashboard serializers;
- object-shaped retry trends, untyped dynamic chapter values, wrong primitives, date/nullability/array drift, or a wrong operation response reference in OpenAPI;
- a handwritten `HomeSummary`, extra aliases/interfaces, `HomeSummaryResult`, response intersections, custom response generics, or adapters;
- shadow Dashboard serializer declarations or assignments in production backend modules;
- any local type/API ownership or wrapping behavior in the two real Home feature shims;
- alternate canonical-module import bindings, exported method references, destructured or bracket-access forwarding, neutral-name transformed returns, continuation-aware nested/multiline and iterative multi-step data flow through control-flow blocks, exported object-owned loaders, secondary endpoint modules, and Home/Dashboard-named backend shadow serializers, while allowing ordinary non-returning or unrelated-return consumers.

Five new algorithm tests exercise displaced serializer, OpenAPI, alternate-import, parallel-export, secondary-module, adapter, and feature-shim bypasses. The Dashboard live checker now explicitly replays the exact Progress serializer family and production backend/frontend shadow scans. All 26 architecture-guard tests pass, including the 21 pre-existing Stats and architecture tests, and the live checker passes.

## Verification Matrix

| Gate | Result |
|---|---|
| Authenticated empty and seeded HTTP/serializer probe | both HTTP 200; both serializers valid |
| Dashboard endpoint contract tests | 2 passed |
| Progress backend package | 14 passed |
| Architecture guard algorithms | 26 passed |
| Focused Home model/achievement/views lane | 4 files / 22 tests passed |
| Full frontend suite | 67 files / 465 tests passed |
| Full ESLint | passed |
| Knip dead-code analysis | passed |
| TypeScript + Vite production build | passed; 2,656 modules transformed |
| Ruff on changed Python/guard files | passed |
| Django system check | passed, 0 issues |
| Generated API contract current | passed |
| Frontend API wrapper usage | passed |
| Generated API type adoption | passed |
| Architecture boundary checker | passed |
| CSS architecture checker | passed |
| Consolidated fast-quality suite | all 10 gates passed |
| `git diff --check` | passed; only pre-existing CRLF conversion warnings |

The consolidated fast-quality suite also verified forbidden legacy vocabulary, 2,056 generated curriculum cases, documentation currency, the CI gate manifest, and absence of tracked generated/cache artifacts.

### Rerunnable Command Ledger

Commands use repository root `C:\Users\Joana\Documents\GIT-IT` unless a different working directory is shown.

| Evidence | Command | Result |
|---|---|---|
| Authenticated Dashboard endpoints | `.\backend\.venv\Scripts\python.exe -m pytest backend/progress/tests/test_dashboard_summary_api.py -q` | 2 passed |
| Full Progress package | `.\backend\.venv\Scripts\python.exe -m pytest backend/progress/tests -q` | 14 passed |
| Architecture algorithms | `.\backend\.venv\Scripts\python.exe -m pytest backend/common/tests/test_architecture_guard_algorithms.py -q` | 26 passed |
| Live architecture | `.\backend\.venv\Scripts\python.exe scripts/checks/check_architecture_boundaries.py` | clean |
| API current/usage/adoption | run `scripts/check_api_contract.py`, `scripts/check_frontend_api_usage.py`, and `scripts/check_api_type_adoption.py` with the backend venv Python | all passed |
| Python quality | `.\backend\.venv\Scripts\ruff.exe check backend/progress/serializers.py backend/progress/tests/test_dashboard_summary_api.py scripts/checks/check_architecture_boundaries.py backend/common/tests/test_architecture_guard_algorithms.py` | passed |
| Django | `.\backend\.venv\Scripts\python.exe backend/manage.py check` | 0 issues |
| Focused Home | `npm test -- src/features/home/utils/achievements.test.ts src/features/home/components/home-stats/homeStatsModel.test.ts src/features/home/components/HomeHubView.test.tsx src/features/home/components/HomeStatsView.test.tsx` from `frontend` | 4 files / 22 tests passed |
| Full frontend | `npm test -- --run` from `frontend` | 67 files / 465 tests passed |
| Frontend static/build | `npm run lint`, `npm run lint:dead`, and `npm run build` from `frontend` | passed; 2,656 modules |
| Consolidated quality | `.\backend\.venv\Scripts\python.exe scripts/check_quality_gates.py` | all 10 gates passed |
| Diff hygiene | `git diff --check` | passed with disclosed CRLF warnings only |

The exact generated component and operation can be replayed with:

```powershell
$schema = Get-Content -Raw frontend/src/shared/api/generated/openapi.json | ConvertFrom-Json
$schema.components.schemas.DashboardSummaryResponse | ConvertTo-Json -Depth 20
$schema.paths.'/api/progress/dashboard/'.get.responses.'200'.content.'application/json'.schema | ConvertTo-Json -Depth 10
Select-String -Path frontend/src/shared/api/generated/apiTypes.ts -Pattern 'Dashboard(Counts|KpiSet|RetryTrend|Streak|SummaryResponse)|progress_dashboard_retrieve'
```

The authenticated test command above is the canonical replay for the two real HTTP traces: it creates and tears down its database, authenticates through DRF, seeds real `ChallengeRun`/`StreakRecord` rows, asserts raw JSON before serializer validation, and rejects the displaced missing-slug/object-retry shape.

### Full Backend Feasibility Note

The repository-wide backend suite was not repeated for this slice. The immediately preceding Stats contract slice ran the same broad suite with a ten-minute cap; its `pytest -q` process was still running when the cap expired and produced no terminal result. This slice therefore claims proportional backend evidence only: all 14 Progress tests, 2 direct Dashboard endpoint tests, 26 architecture algorithm tests, scoped Ruff, Django system check, current generated-contract checks, and two direct authenticated HTTP/serializer traces. No unrelated backend runtime was changed.

## Learner-Visible Preservation

The Dashboard metrics service, view, URL, operation ID, shared HTTP client, and every production Home component remain byte-identical to the pre-slice baseline. The two preview payloads gained only the now-required neutral values `completed_story_slug: null` and `completed_stories: []`; this preserves their prior achievement and story-completion meaning. The full frontend test/build matrix confirms existing Home behavior.

The protected Stats endpoint test, feature types/API, common OpenAPI helpers, generator implementation, and `RateMetricSerializer` semantics also remain unchanged and the Stats tests still pass within the 14-test Progress suite.

## Dirty-Worktree Preservation

The 103-entry pre-slice dirty manifest was reparsed at the terminal gate:

```text
Manifest rows parsed: 103
Strict unchanged rows checked: 98
Strict preservation mismatches: 0
Protected hashes checked: 11
Protected hash mismatches: 0
```

The five reviewed exclusions were the shared serializer, two generated artifacts, architecture checker, and architecture algorithm tests. Their final state is attributable to the planned Dashboard cutover:

| Path | PRE state | Final state |
|---|---|---|
| `backend/progress/serializers.py` | 59 lines / 2,094 bytes | 83 lines / 2,921 bytes |
| generated `openapi.json` | 5,555 lines / 193,547 bytes | 5,643 lines / 196,402 bytes |
| generated `apiTypes.ts` | 492 lines / 43,184 bytes | 496 lines / 43,654 bytes |
| architecture checker | 2,201 lines; `1762 + / 2 -` | 2,775 lines; `2336 + / 2 -` |
| guard algorithm tests | 798 lines; `778 + / 0 -` | 1,140 lines; `1120 + / 0 -` |

The guard-file deletion counts remain exactly `2` and `0`, so all Slice 6 rules/tests were preserved additively. The protected service, view, URL, common OpenAPI helper, generator core, HTTP client, both Home feature shims, and Stats test/types/API all retain their recorded SHA-256 hashes.

Terminal hashes for the principal Slice 7 outputs:

| Path | SHA-256 |
|---|---|
| `backend/progress/serializers.py` | `5147607F3754CBE35B0004E2140409652F4ACD7D2E0079AC708476098231D7E8` |
| `backend/progress/tests/test_dashboard_summary_api.py` | `6C790D25E7A825AD4313C419843DEC5AB700CE393F8D3B2BFDCC829891344256` |
| generated `openapi.json` | `32AD95552CA54D8CD55F33D43551A860E93DAC8803E58A863424C0540D973640` |
| generated `apiTypes.ts` | `5DA15628791B892AC1577931F2C0058160FE66AE0283B0A7C1EEC417FB8C42CF` |
| `shared/progress/types.ts` | `0DF902817A0C3FBBA46670D34A9B151E8E867BD601BDE9F663CDCA4B311F983B` |
| `shared/progress/homeSummaryApi.ts` | `696A5219C3E4881173A90C9680EA18F34797214D30B9340E1AB9AC158A810CBC` |

## Scope and External Consumer Note

No implementation deviation or scope expansion was required. The preview update was explicitly allowed for required structural completeness.

External clients generated from the former committed schema will observe a stricter compile-time response: required completion fields, typed nested objects, and an array-shaped retry trend. Those changes document the payload the endpoint already returned. No compatibility alias, dual DTO, adapter, or runtime response change was introduced.

## Review Closure

| Gate | Final verdict | Independent replay |
|---|---|---|
| POST implementation-plan review | `ALIGNED` | exact contract/cutover/scope, 14 Progress tests, 26 architecture tests, API checks, and `103 / 98 / 0` preservation |
| Correctness review | `PASS` | authenticated endpoint, serializer/OpenAPI/generated TypeScript parity, Home direct path, build, and protected hashes |
| Maintainability review | `PASS` | canonical imports, exported adapter/shadow bypass matrix, shared Progress backend ownership, ordinary-consumer allowances, and additive numstats |
| Final independent verifier | `PASS` | 2 Dashboard tests, 14 Progress tests, 26 architecture tests, 4-file/22-test Home lane, 2,656-module build, API/Ruff/Django/CSS/fast-quality gates, and terminal preservation |

Review-driven corrections strengthened only the additive architecture/evidence lane. They added canonical import and whole-file ownership checks; production frontend/backend shadow scans; an honestly named shared Progress backend validator; binding-aware exported adapter detection; balanced, continuation-aware nested statement analysis with iterative data-flow propagation; ordinary-consumer pass cases; and the rerunnable command ledger. No runtime, serializer, generated contract, frontend consumer, service, view, route, or protected shim was changed during review closure.

The final verifier's sole minor finding was this section's stale `pending` text. It is corrected here. No blocker, major, or minor finding remains.
