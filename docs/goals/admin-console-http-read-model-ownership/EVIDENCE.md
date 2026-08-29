# Admin Console HTTP and Read-Model Ownership — Slice 2 Evidence

## Outcome

The admin console now has one read owner per domain and focused HTTP adapters. The old `backend/adminconsole/views.py` implementation is absent. `adminconsole.views` still exports the same 15 API-view class names, so the unchanged URL module and external API contract keep their existing surface.

## Before and after

| Measure | Before | After |
|---|---:|---:|
| HTTP implementation shape | one 627-line `views.py` | six focused modules, 416 implementation lines total |
| Public HTTP exports | implicit classes in flat module | 35-line package initializer with the same 15 classes |
| ORM/query/aggregation references in HTTP layer | 32 | 0 |
| Selector implementation modules | 3 | 7 |
| Selector package lines including exports | 121 | 517 |
| Largest focused HTTP module | 627 lines | 122 lines (`views/curriculum.py`) |
| External URL module edits | n/a | 0 |
| Full OpenAPI bytes | 89,360 | 89,360, byte-for-byte equal |

The selector growth is the intended ownership transfer: the overview and analytics aggregates, list queries, lookup reads, response read models, and settings resolution now live outside HTTP adaptation rather than being duplicated.

## Maintainer ownership map

| Change needed | Truth owner | HTTP consumer |
|---|---|---|
| Overview counts, economy totals, recent activity | `adminconsole/selectors/overview.py` | `views/dashboard.py` |
| Run/completion/active-learner/story analytics | `adminconsole/selectors/analytics.py` | `views/dashboard.py` |
| User lookup, search/list, detail payload | `adminconsole/selectors/users.py` | `views/users.py`, `views/economy.py` |
| Transaction list and adjustment response | `adminconsole/selectors/economy.py` | `views/economy.py` |
| Story/chapter lookup, order, counts, payloads | `adminconsole/selectors/curriculum.py` | `views/curriculum.py` |
| Supported story-world option contract | `adminconsole/curriculum_options.py` | curriculum selector and write service |
| Official-content eligibility and moderation queue | `adminconsole/selectors/content.py` | `views/content.py` |
| Settings resolution and flag response payload | `adminconsole/selectors/settings.py` | `views/settings.py` |
| User/economy/curriculum/moderation/settings writes | existing `adminconsole/services/*` | focused domain views |
| Flag registry and runtime enablement decision | `adminconsole/flags.py` | runtime flag consumers |

HTTP absence remains HTTP-owned: selector `find_*` functions return a model or `None`; domain views translate `None` into the preserved `User not found.`, `Story not found.`, `Chapter not found.`, or `Moderation item not found.` DRF response.

## Target-perspective request/response evidence

`test_staff_can_read_every_admin_get_contract` authenticated a real DRF `APIClient` as staff and traversed URL resolution, permission handling, the focused view, selector, and response renderer for all 10 GET paths. Every request returned HTTP 200 with these exact top-level contracts:

| Request | Response keys |
|---|---|
| `GET /api/admin/overview/` | `users`, `economy`, `recent_signups`, `recent_purchases`, `recent_admin_actions` |
| `GET /api/admin/users/` | `results` |
| `GET /api/admin/users/<id>/` | `id`, `username`, `email`, `is_staff`, `is_active`, `date_joined`, `last_login`, `wallet`, `entitlement_count` |
| `GET /api/admin/economy/transactions/` | `results` |
| `GET /api/admin/stories/` | `results`, `world_options` |
| `GET /api/admin/chapters/` | `results` |
| `GET /api/admin/content/` | `results` |
| `GET /api/admin/analytics/` | `runs`, `completions`, `active_learners_30d`, `per_story` |
| `GET /api/admin/moderation/` | `content` |
| `GET /api/admin/settings/` | `feature_flags` |

Deterministic fixture-backed API requests additionally proved:

- Users: case-insensitive username and email search, descending `date_joined`, exactly the newest 100 of 101 matching rows, and selector-side clamping of an over-limit caller.
- Transactions: `user_id` isolation, descending transaction ID, exactly the newest 200 of 201 matching rows, and selector-side clamping of an over-limit caller.
- Curriculum: story `sort_order,id` ordering including a tied sort order, per-story chapter counts, canonical world-option order from the neutral option owner, prerequisite payload resolution in exactly two selector queries (stories plus chapter counts), chapter story isolation, and chapter `sort_order,number` ordering including a tied sort order.
- Official/moderated content: owner-null/staff eligibility, rejection of non-staff ownership and missing official chapters, kind filtering, descending `updated_at`, and selector-side 200 caps proven against 201 eligible rows for both lists.
- Existing behavior coverage still proves overview spend rules, permissions, idempotent audited writes, self-lockout prevention, curriculum invariants, settings, moderation, and analytics values.

Final focused result after the new read-contract tests were split into `test_admin_read_api.py`: `28 passed in 5.59s` for all `adminconsole/tests` plus `common/tests/test_architecture_guard_algorithms.py`. The pre-existing mixed API test module is 671 lines; the focused read-contract module is independently discoverable.

## External contract identity

Before runtime edits, the schema was generated and validated with:

```powershell
$schemaPath = Join-Path $env:TEMP 'git-it-admin-schema-before.yaml'
python manage.py spectacular --file $schemaPath --validate
Get-FileHash -Algorithm SHA256 $schemaPath
```

The baseline file was rechecked immediately before comparison. A fresh post-cutover schema had the same bytes and hash:

```text
openapi_before_hash=9A0653EC16B6746A32A4ACC7C83B10003EF2B6A226E7ED64E67F1E50CF735789
openapi_after_hash=9A0653EC16B6746A32A4ACC7C83B10003EF2B6A226E7ED64E67F1E50CF735789
openapi_bytes_equal=True
openapi_bytes=89360
```

`python scripts/check_api_contract.py` also reported `Generated API contract is current.` No generated client or contract file changed.

## Cutover and architecture evidence

- `backend/adminconsole/views.py`: absent and registered in `DISPLACED_BACKEND_PATHS`.
- `adminconsole/views/__init__.py`: 35 lines, exports exactly 15 API-view classes, contains no implementation; AST enforcement allows only imports and a literal `__all__`.
- Focused HTTP package: zero model imports, `django.db` imports, flag/query-service imports, wallet imports, or `.objects` manager access.
- Selector package: zero REST-framework or view imports.
- `resolved_feature_flags`: absent from `adminconsole/flags.py`; settings read ownership is consolidated.
- `flag_payload`: absent from `selectors/content.py`; settings payload ownership is consolidated.
- The architecture parser's positive rejection cases and the real package checks both pass, including direct, parent-package, and relative model/view imports; Django `db`/`auth` aliases; `.objects`, `_default_manager`, and `_base_manager`; and implementation placed in the view initializer.
- Public selector `limit` parameters are clamped at their documented 100/200 invariants, so internal callers cannot bypass the API cap.
- Curriculum selectors consume neutral `curriculum_options.py`, not the write-service package; prerequisite rows are loaded with the story query rather than through an inherited N+1 path.
- Runtime import-cycle detection and every other architecture boundary pass.

## Verification ledger

| Command | Result |
|---|---|
| `python -m pytest adminconsole/tests common/tests/test_architecture_guard_algorithms.py -q` | 28 passed |
| `ruff check adminconsole common/tests/test_architecture_guard_algorithms.py` | passed |
| `python manage.py check` | no issues |
| `python scripts/checks/check_architecture_boundaries.py` | clean, including import cycles and displaced paths |
| `python scripts/check_api_contract.py` | current |
| OpenAPI pre/post byte and SHA-256 comparison | identical |
| `python scripts/check_quality_gates.py` | all fast gates passed, including 2,056 generated curriculum targets |
| `git diff --check` | passed |

## Scope safety

This slice did not edit `adminconsole/urls.py`, serializers, write-service behavior, models, migrations, generated API clients/contracts, frontend code/assets, local databases, or curriculum generated targets. The curriculum write service received only the import cutover to the new neutral option owner; its validation/action logic is unchanged. The earlier Slice 1 curriculum changes remain separate uncommitted work and were preserved.

## Review status

- PRE plan review: aligned after exact selector/failure contracts, consolidated settings ownership, the 10-path matrix, deterministic list semantics, and a validated OpenAPI baseline were added.
- POST plan review: aligned with no remaining blocker, major, or minor deviation.
- Correctness review: no remaining correctness or trust findings; exact absence messages, permissions, query semantics, and OpenAPI identity were independently checked.
- Maintainability review: no remaining findings after cap ownership, neutral curriculum options, focused test split, prerequisite eager loading, and evidence metrics were corrected.
- Independent target-perspective verification: `VERIFIED`. All 10 staff GET routes returned HTTP 200 with the preserved keys and resolved to the expected relocated classes; the focused verifier lane passed 8 tests, the prerequisite payload used exactly two queries, all boundaries/15 exports/flat-path deletion were confirmed, and OpenAPI remained byte-identical.
