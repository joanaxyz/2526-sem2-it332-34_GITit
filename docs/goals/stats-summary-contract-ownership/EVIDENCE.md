# Stats Summary Contract Ownership Evidence

Captured on 2026-08-10 after executing `PLAN.md` with Krypton Execution.

## Outcome

The authenticated Stats summary now has one documented and generated contract. Runtime JSON, the Progress-owned serializer, committed OpenAPI, generated TypeScript, feature aliases, and the API wrapper all describe exactly:

```text
skill_profile + activity_trend + headline
```

The false `activity`, `headlines`, and optional `totals` schema path is removed. The frontend no longer intersects the generated response with a handwritten response or supplies a custom response generic. `MetricsService.stats_summary()`, its route, and its response values were not changed.

## Ownership Cutover

| Concern | Result |
|---|---|
| Executable values | `backend/progress/services/metrics.py::MetricsService.stats_summary` remains unchanged |
| Stats/Dashboard response contracts | owned by `backend/progress/serializers.py` |
| Shared Wallet/Shop response contract | remains in `backend/common/openapi.py` |
| Progress view | imports Stats/Dashboard from Progress and Wallet from Common |
| OpenAPI and TypeScript | regenerated from the backend serializer contract |
| Feature aliases | indexed from `ApiSchemas['StatsSummaryResponse']` |
| Runtime request | uses `progress_stats_retrieve` directly, without a response override |

Search and architecture checks prove there is one production `StatsSummaryResponseSerializer`, one production `DashboardSummaryResponseSerializer`, no stale `DashboardSummarySerializer`, no Progress-owned Wallet duplicate, and no `StatsSummaryResult`.

## Authenticated Real-Path Evidence

An isolated test database was migrated, a real user was created, DRF `APIClient` authenticated that user, and the real `/api/progress/stats/` URL/view/service path was requested. The returned JSON was then validated by `StatsSummaryResponseSerializer` and compared with the committed OpenAPI component.

```json
{
  "http_status": 200,
  "runtime_top_level_keys": [
    "activity_trend",
    "headline",
    "skill_profile"
  ],
  "skill_row": {
    "key": "status",
    "label": "Status",
    "hint": "Inspect the working tree.",
    "value": null,
    "command": "git status"
  },
  "skill_row_keys": [
    "command",
    "hint",
    "key",
    "label",
    "value"
  ],
  "activity_points": 14,
  "activity_point_keys": [
    "commands_run",
    "date",
    "levels_completed"
  ],
  "activity_point_wire_types": {
    "date": "str",
    "levels_completed": "int",
    "commands_run": "int"
  },
  "headline_keys": [
    "accuracy",
    "boss_floors",
    "comebacks",
    "commands_run",
    "day_streak",
    "finish_rate",
    "gitcoins",
    "levels_completed",
    "longest_streak",
    "perfect_clears"
  ],
  "finish_rate": {
    "value": null,
    "numerator": 0,
    "denominator": 0
  },
  "scoped_count_keys": [
    "scope",
    "value"
  ],
  "serializer_valid": true,
  "serializer_errors": {},
  "openapi_properties": [
    "activity_trend",
    "headline",
    "skill_profile"
  ],
  "openapi_required": [
    "activity_trend",
    "headline",
    "skill_profile"
  ],
  "operation_ref": "#/components/schemas/StatsSummaryResponse",
  "displaced_keys_present": []
}
```

This is direct HTTP-boundary evidence, not a design fixture or a service-only assertion.

## Exact Generated Contract

The generated `StatsSummaryResponse` is:

```ts
"StatsSummaryResponse": {
  "activity_trend": Array<ApiSchemas["StatsTrendPoint"]>
  "headline": ApiSchemas["StatsHeadline"]
  "skill_profile": Array<ApiSchemas["StatsSkillAxis"]>
}
```

Its generated nested components are exact and required:

| Component | Fields |
|---|---|
| `StatsSkillAxis` | `command`, `hint`, `key`, `label`, `value` |
| `StatsTrendPoint` | `commands_run`, `date`, `levels_completed` |
| `RateMetric` | `denominator`, `numerator`, `value` |
| `StatsScopedCount` | `scope`, `value` |
| `StatsHeadline` | `accuracy`, `boss_floors`, `comebacks`, `commands_run`, `day_streak`, `finish_rate`, `gitcoins`, `levels_completed`, `longest_streak`, `perfect_clears` |

Feature types now contain only:

```ts
export type StatsSummary = ApiSchemas['StatsSummaryResponse']
export type SkillAxis = StatsSummary['skill_profile'][number]
export type TrendPoint = StatsSummary['activity_trend'][number]
```

## Durable Architecture Enforcement

The architecture checker now rejects:

- Stats or Dashboard response ownership in `common/openapi.py`;
- a Wallet response duplicate in Progress;
- missing, duplicate, secondary, extra, optional, or loosely typed Stats serializers;
- wrong OpenAPI primitive types, date formats, nullability, arrays, or nested references;
- stale `DashboardSummarySerializer` ownership;
- extra handwritten Stats response objects, interfaces, aliases, or intersections;
- a custom response generic, indirect return, async adapter, or displaced key in `statsApi.summary()`;
- an operation response that does not reference `StatsSummaryResponse`.

All 21 architecture-guard algorithm tests pass, including synthetic duplicate/manual-contract, shadow class/assignment/module, shadow DTO, async adapter, false-positive comment, and wrong primitive/format/nullability/array bypasses. The live architecture and CSS checkers pass.

## Verification Matrix

| Gate | Result |
|---|---|
| Focused Stats endpoint contract | 2 passed |
| Progress backend package | 12 passed |
| Architecture guard algorithms | 21 passed |
| Full frontend suite | 67 files / 465 tests passed |
| Focused Home Stats lane | 3 files / 13 tests passed |
| Full ESLint | passed |
| Knip dead-code analysis | passed |
| TypeScript + Vite production build | passed; 2,656 modules transformed |
| Ruff on changed Python and guard files | passed |
| Django system check | passed, 0 issues |
| Generated API contract current | passed |
| Frontend API wrapper usage | passed |
| Generated API type adoption | passed |
| Architecture boundary checker | passed |
| CSS architecture checker | passed |
| Documentation current | passed |
| Consolidated fast-quality suite | all 10 gates passed |
| `git diff --check` | passed; only pre-existing CRLF conversion warnings |

The consolidated fast-quality suite additionally verified legacy vocabulary, 2,056 generated curriculum target cases, the CI gate manifest, and absence of tracked generated/cache artifacts.

### Full Backend Feasibility Note

The complete repository-wide Django suite was attempted with a ten-minute cap as part of a parallel full matrix. The wrapper timed out after 604.1 seconds while its `pytest -q` process was still running and had not returned a result. The exact orphan process tree was verified and stopped. This slice therefore claims proportional backend evidence only: all 12 Progress tests, the 2 direct Stats contract tests, 21 architecture algorithm tests, Ruff, Django system check, and direct authenticated HTTP/serializer evidence. The timeout is recorded rather than represented as a pass or failure.

## Learner-Visible Preservation

The runtime service and transport remained byte-identical. The full frontend suite, focused Home Stats/model/achievement tests, and production build pass. The stricter generated contract exposed three synthetic Home Stats skill rows that omitted the runtime-required `command`; after an explicit plan amendment and PRE re-review, only those missing fixture fields were added. No Home production component, model, fixture, copy, markup, style, or behavior was changed by this slice.

## Dirty-Worktree Preservation

The 91-entry pre-slice dirty manifest was reparsed at the terminal gate.

```text
Manifest rows parsed: 91
Strict unchanged rows checked: 87
Strict preservation mismatches: 0
```

The four reviewed exclusions were:

- two additive shared architecture files;
- the amended `PLAN.md`;
- the single allowed Home model test fixture.

Approved amendment hashes:

| Path | Pre hash | Final hash |
|---|---|---|
| `PLAN.md` | `20D9791A6B76F3A158317A654C4E19EB97CD046090B4DB46F3BCA80A4C577EB0` | `2F58F9FA089BFF4FC2DEC017729699376F6FF851F74C80552027C537184388FA` |
| `homeStatsModel.test.ts` | `C1A7CBE93763534330AEA7256D5F4BBAE97A09B229BB5547FCD07C50BB26237E` | `0A138E734CE7EBF06E5471678E80CC50F126AB3F4FBE5B992B4C8DC3C243FE97` |

The shared guard diffs remained additive relative to the PRE baseline:

| Path | PRE numstat | Final numstat | PRE lines | Final lines |
|---|---|---|---:|---:|
| `scripts/checks/check_architecture_boundaries.py` | `1265 + / 2 -` | `1762 + / 2 -` | 1,704 | 2,201 |
| `backend/common/tests/test_architecture_guard_algorithms.py` | `561 + / 0 -` | `778 + / 0 -` | 581 | 798 |

Earlier guard behavior is also exercised by all 21 passing algorithm tests and the live checker. The three protected executable paths retained their exact PRE hashes:

| Path | SHA-256 |
|---|---|
| `backend/progress/services/metrics.py` | `BC10D8BFADC22F33AB0A4DE0D1692F92C49E3628F94AD2217EBD0FA843EEA38F` |
| `scripts/api/api_contract.py` | `FCF41D695D712401E5F98BC347995E89079E3DDCF132DAC6C29FBD1618B14D23` |
| `frontend/src/shared/api/httpClient.ts` | `41B94C89B7E713598002AD1D0FC627CA63CC13171338D27802A12F4DA59DF8C5` |

## Plan Deviation and External Consumer Risk

The only implementation deviation was the conditionally allowed synthetic fixture correction described above. It was added to the plan after the production build exposed the omission, then PRE-reviewed as `ALIGNED` before the edit.

External clients generated from the former committed schema will see a compile-time response change. That old schema described fields the endpoint never returned, so retaining aliases would create a second false contract rather than compatibility. No alias, transitional DTO, runtime adapter, or dual schema was introduced.

## Review Closure

The first POST plan/correctness/maintainability pass agreed that the implemented runtime/schema/type cutover was cohesive, but found major durability and evidence gaps: primitive/nullability/format/array drift, secondary serializers/manual DTOs, and an async adapter could bypass the guard; the authenticated fixture did not exercise a real skill row; and a comment could false-positive as a manual type path.

Those findings were corrected by:

- seeding a published `CommandSkill` and asserting its exact raw JSON row and wire types;
- asserting exact raw nested keys and types for trend, rate, scoped-count, and headline values;
- enforcing exact serializer constructors/options and exact OpenAPI property fragments;
- rejecting secondary Stats serializer classes or assignment aliases across production backend modules and extra feature DTO/alias/interface paths;
- requiring `statsApi.summary()` to return the generated operation call directly;
- stripping TypeScript comments before ownership checks;
- adding three synthetic regression tests covering every reported bypass.

Final review results:

| Gate | Verdict | Independent evidence |
|---|---|---|
| POST implementation-plan review | `ALIGNED` | replayed prior scalar/shadow/adapter probes, 22 focused tests, 12 Progress tests, API/current architecture checks, and preservation |
| Correctness review | `PASS` | replayed 12 Progress tests, the architecture suite, contract-current check, live checker, and wrong-type/nullability/format/array mutations |
| Maintainability review | `PASS` | verified direct-return/comment/type guards plus class/assignment aliases across production modules; 21 architecture and 2 endpoint tests passed |
| Independent verifier | `PASS` | replayed the authenticated populated-skill contract, 12 Progress tests, 21 architecture tests, 3-file/13-test Home lane, API checks, build, live architecture/CSS, diff hygiene, and 91/87/0 preservation |

No blocker, major, or minor finding remains. The intentionally naming-based backend shadow rule may require an explicit allowlist decision if a future unrelated `Stats*Serializer` is introduced; no current false positive or duplicate path exists.
