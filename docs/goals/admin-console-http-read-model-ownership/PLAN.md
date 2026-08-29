# Admin Console HTTP and Read-Model Ownership — Slice 2 Implementation Plan

**Intent:** Advance the active codebase-maintainability goal by replacing the admin console's 627-line mixed HTTP/query module with domain-focused HTTP adapters and selector-owned read models.
**Current Behavior:** `backend/adminconsole/views.py` owns all 15 API views and performs 32 ORM/query/aggregation operations for overview, users, transactions, curriculum, content, analytics, moderation, and settings. Existing selectors mostly format individual rows, so maintainers must search the HTTP module to find read behavior. Two dead helpers remain in that module.
**Expected Outcome:** `adminconsole.views` becomes a package with a thin compatibility export surface and six focused domain modules. Every read query and response read-model assembly moves to an exact selector owner. HTTP modules retain only permissions, schema decorators, serializer validation, service orchestration, status codes, and `Response` construction. Existing routes, names, request validation, response shapes, permissions, writes, OpenAPI output, and database behavior remain unchanged.
**Target-Perspective Output:** A maintainer can answer where to change each dashboard/user/economy/curriculum/content/moderation/settings read without inspecting HTTP code; each endpoint has one obvious view module and one read owner; `adminconsole.views.Admin*APIView` imports continue to work; the flat path cannot return; and an architecture guard rejects persistence/query ownership in the new HTTP package.
**Truth Owner:** `selectors/overview.py` owns overview aggregates/activity; `selectors/analytics.py` owns run/completion/story analytics; `selectors/users.py` owns user lookup/list/detail payloads; `selectors/economy.py` owns transactions and wallet response payloads; `selectors/curriculum.py` owns story/chapter lookup and list/detail payloads; `selectors/content.py` owns official-content and moderation queries/payloads; `selectors/settings.py` owns resolved settings queries and flag payloads. `adminconsole/curriculum_options.py` owns the world-option contract shared by curriculum reads and writes. `adminconsole/flags.py` retains only the canonical flag registry and runtime `feature_enabled` behavior. Existing services remain the sole write/business-action owners. Domain view modules own HTTP adaptation, including exact DRF `NotFound` responses.
**Contract Boundary:** The 15 existing view class names, every `/api/admin/` route and URL name, HTTP methods/statuses, serializers, permissions, service behavior, response keys/values/order, pagination caps, query filters, OpenAPI schema, migrations, database schema, frontend generated clients, and non-admin runtime modules are unchanged.
**Cutover:** Build selectors first, then create the `adminconsole/views/` package with all callers pointing at the new selectors and existing services. Preserve the public import surface through `views/__init__.py`. Delete `adminconsole/views.py` in the same cutover. Delete `_as_bool` and `_safe_int`; replace the two live lookup helpers with selector `find_*` functions that return a model or `None`, while focused views retain the exact DRF `NotFound` messages. Move `resolved_feature_flags` and `flag_payload` into `selectors/settings.py`; do not leave a shim file or duplicate read/query path.
**Displaced Path:** `backend/adminconsole/views.py` must be absent and registered in `DISPLACED_BACKEND_PATHS`. Files under `backend/adminconsole/views/` may not import model modules, `django.db`, `django.contrib.auth`, `adminconsole.flags`, `progress.selectors`, or `progress.wallet`, and may not access ORM managers. Selector modules may not import `rest_framework`, `Response`, `APIView`, or any view module. `views/__init__.py` may contain only imports and `__all__` exports and must remain under the existing thin-package limit. `resolved_feature_flags` must be absent from `flags.py`, `flag_payload` must be absent from `selectors/content.py`, and curriculum selectors must not load the write-service package to obtain shared options.
**Value Density:** This removes one of the largest remaining backend HTTP modules, relocates every embedded read path to the repository's established selector layer, improves discoverability across all 15 staff endpoints, and adds a durable layer rule without changing product behavior.
**Acceptance Evidence:** Before/after module and query-reference metrics; complete endpoint and selector-contract tables; all 10 admin GET endpoints exercised through DRF's API client; deterministic integration assertions for user, transaction, curriculum, and official-content filter/order/count/limit semantics; 21 existing admin/guard tests plus new route, query-semantics, and architecture assertions; unchanged full OpenAPI SHA-256 `9A0653EC16B6746A32A4ACC7C83B10003EF2B6A226E7ED64E67F1E50CF735789`; current generated API contract; no runtime import cycle; Django check; Ruff; fast quality gates; and a maintainer inspection table.
**Evidence Lane:** Baseline tests/metrics/OpenAPI hash -> selector extraction -> atomic view-package cutover -> boundary guard -> all-read-route API test -> focused tests/Ruff -> OpenAPI byte comparison -> API contract/Django/import-cycle/quality gates -> evidence artifact -> POST review and independent verification.
**Kill Criteria:** Zero ORM manager accesses and zero forbidden persistence imports under `adminconsole/views/`; zero REST-framework or view imports under `adminconsole/selectors/`; zero implementation in `views/__init__.py`; old flat path absent and guarded; `resolved_feature_flags` absent from `flags.py`; `flag_payload` absent from `selectors/content.py`; all 15 public classes importable from `adminconsole.views`; all 15 routes resolve to the same class names and methods; all 10 GET endpoints return the preserved top-level shapes; user/transaction/story/chapter/content filters, ordering, counts, eligibility, and limits proven; all focused and repository fast gates pass; OpenAPI bytes/hash unchanged; no migration, generated API client, frontend, asset, or unrelated source edit.
**Architecture Slice:** `backend/adminconsole` HTTP/read ownership only. Existing serializers and write services stay in place; the database and external API remain unchanged.
**Plan Review Gate:** Requires PRE review before execution.

## Architecture Map

### Endpoint ownership after cutover

| Endpoint classes | URL paths | HTTP module | Read/query owner | Write owner |
|---|---|---|---|---|
| `AdminOverviewAPIView`, `AdminAnalyticsAPIView` | `overview/`, `analytics/` | `views/dashboard.py` | `selectors/overview.py`, `selectors/analytics.py` | None |
| `AdminUserListAPIView`, `AdminUserDetailAPIView`, `AdminUserActionAPIView` | `users/`, `users/<user_id>/`, `users/<user_id>/actions/` | `views/users.py` | `selectors/users.py` | existing `AdminUserActionService`, `AdminEconomyService` |
| `AdminTransactionListAPIView`, `AdminEconomyAdjustAPIView` | `economy/transactions/`, `economy/adjust/` | `views/economy.py` | `selectors/economy.py`, `selectors/users.py` | existing `AdminEconomyService` |
| `AdminStoryListCreateAPIView`, `AdminStoryDetailAPIView`, `AdminChapterListAPIView`, `AdminChapterDetailAPIView` | `stories/`, `stories/<story_id>/`, `chapters/`, `chapters/<chapter_id>/` | `views/curriculum.py` | `selectors/curriculum.py` | existing `AdminCurriculumService` |
| `AdminContentListAPIView`, `AdminModerationListAPIView`, `AdminModerationUnpublishAPIView` | `content/`, `moderation/`, `moderation/unpublish/` | `views/content.py` | `selectors/content.py` | existing `unpublish_moderation_content` |
| `AdminSettingsAPIView` | `settings/` | `views/settings.py` | `selectors/settings.py` | existing `update_feature_flag` |

### Exact selector contracts

| Selector owner | Exact public function | Return/failure contract | Query semantics and consumer |
|---|---|---|---|
| `selectors/overview.py` | `admin_overview_payload(*, now=None) -> dict` | Complete overview response; no HTTP types | Counts all users; 7/30-day cutoffs; wallet sum; only negative shop/cosmetic spend; five newest signups/purchases; eight newest admin actions; overview GET |
| `selectors/analytics.py` | `admin_analytics_payload(*, now=None) -> dict` | Complete analytics response; no HTTP types | Status totals, pass definitions, distinct 30-day active players, completion totals, story order; analytics GET |
| `selectors/users.py` | `find_admin_user(user_id) -> User | None` | Returns `None` for absent/invalid IDs; never raises `NotFound` | User detail/action/economy views translate `None` to `NotFound("User not found.")` |
| `selectors/users.py` | `admin_user_list_payload(*, query="", limit=100) -> dict` | `{"results": list[dict]}` | Case-insensitive username/email filter; descending `date_joined`; cap 100; users GET |
| `selectors/users.py` | existing `user_brief(user) -> dict`, `user_detail(user) -> dict` | Preserved row/detail shapes | Overview, user detail/action |
| `selectors/economy.py` | `admin_transaction_list_payload(*, user_id=None, limit=200) -> dict` | `{"results": list[dict]}` | Optional user filter; descending transaction ID; cap 200; transactions GET |
| `selectors/economy.py` | `admin_economy_adjustment_payload(*, player, applied) -> dict` | `{"wallet": dict, "applied": bool}` | Wallet summary after adjustment; economy POST |
| `selectors/curriculum.py` | `find_admin_story(story_id) -> Story | None`, `find_admin_chapter(chapter_id) -> Chapter | None` | Model or `None`; no HTTP exceptions | Curriculum views retain exact `Story not found.` / `Chapter not found.` responses |
| `selectors/curriculum.py` | `admin_story_list_payload() -> dict` | `{"results": list[dict], "world_options": tuple}` | Story `sort_order,id`; chapter counts; existing supported-world order; stories GET |
| `selectors/curriculum.py` | `admin_story_detail_payload(story) -> dict` | Existing story shape with live chapter count | Story PATCH response |
| `selectors/curriculum.py` | `admin_chapter_list_payload(*, story_id=None) -> dict` | `{"results": list[dict]}` | Optional story filter; `sort_order,number`; chapters GET |
| `selectors/content.py` | `admin_official_content_list_payload(*, kind=None, limit=200) -> dict` | `{"results": list[dict]}` | Owner absent/staff, official chapter required, optional kind, newest update first, cap 200; content GET |
| `selectors/content.py` | `admin_moderation_list_payload(*, limit=200) -> dict` | `{"content": list[dict]}` | Public/published/non-staff-owned, newest update first, cap 200; moderation GET |
| `selectors/content.py` | `find_admin_moderation_content(item_id) -> ContentDefinition | None` | Model or `None`; no HTTP exceptions | Moderation view retains `NotFound("Moderation item not found.")` |
| `selectors/settings.py` | `admin_settings_payload() -> dict`, `flag_payload(flag) -> dict` | Settings/flag response shapes; no HTTP types | FeatureFlag overrides over `SUPPORTED_FLAGS`; settings GET/POST |

### GET contract evidence matrix

| GET path | Expected top-level keys |
|---|---|
| `/api/admin/overview/` | `users`, `economy`, `recent_signups`, `recent_purchases`, `recent_admin_actions` |
| `/api/admin/users/` | `results` |
| `/api/admin/users/<user_id>/` | `id`, `username`, `email`, `is_staff`, `is_active`, `date_joined`, `last_login`, `wallet`, `entitlement_count` |
| `/api/admin/economy/transactions/` | `results` |
| `/api/admin/stories/` | `results`, `world_options` |
| `/api/admin/chapters/` | `results` |
| `/api/admin/content/` | `results` |
| `/api/admin/analytics/` | `runs`, `completions`, `active_learners_30d`, `per_story` |
| `/api/admin/moderation/` | `content` |
| `/api/admin/settings/` | `feature_flags` |

### Files to create

- `backend/adminconsole/selectors/overview.py`
- `backend/adminconsole/selectors/analytics.py`
- `backend/adminconsole/selectors/economy.py`
- `backend/adminconsole/selectors/settings.py`
- `backend/adminconsole/curriculum_options.py`
- `backend/adminconsole/views/__init__.py`
- `backend/adminconsole/views/dashboard.py`
- `backend/adminconsole/views/users.py`
- `backend/adminconsole/views/economy.py`
- `backend/adminconsole/views/curriculum.py`
- `backend/adminconsole/views/content.py`
- `backend/adminconsole/views/settings.py`
- `backend/adminconsole/tests/helpers.py`
- `backend/adminconsole/tests/test_admin_read_api.py`
- `docs/goals/admin-console-http-read-model-ownership/EVIDENCE.md`

### Files to modify

- `backend/adminconsole/selectors/__init__.py`
- `backend/adminconsole/selectors/users.py`
- `backend/adminconsole/selectors/curriculum.py`
- `backend/adminconsole/selectors/content.py`
- `backend/adminconsole/flags.py`
- `backend/adminconsole/services/__init__.py`
- `backend/adminconsole/services/curriculum.py`
- `backend/adminconsole/tests/test_admin_api.py`
- `scripts/checks/check_architecture_boundaries.py`
- `backend/common/tests/test_architecture_guard_algorithms.py`

### File to delete

- `backend/adminconsole/views.py`

### Files to avoid

- `backend/adminconsole/urls.py` unless an import-resolution defect requires a compatibility-only edit; its public import surface should work unchanged.
- `backend/adminconsole/serializers.py`, existing write service implementations, models, flags behavior, migrations, generated API clients/contracts, frontend code/assets, curriculum generated targets, local databases, caches, archives, and unrelated user-owned files.

### Read/write path and integration points

- Read: URL resolver -> focused API view -> query serializer -> domain selector -> ORM/domain read service -> payload -> `Response`.
- Write: URL resolver -> focused API view -> request serializer -> existing domain service -> selector payload -> `Response`.
- Public Python compatibility: `adminconsole.views.__init__` exports the same 15 class names used by unchanged `adminconsole/urls.py`.
- OpenAPI integration remains the existing `extend_schema` decorators and serializers on the same class names/methods.

## Task 1: Give each admin read model an exact selector owner

**Exact scope:** Implement exactly the functions in the selector-contract table. Lookup selectors return models or `None`; views retain HTTP exceptions and exact messages. Move `resolved_feature_flags` and `flag_payload` into `selectors/settings.py`, update callers, and leave `SUPPORTED_FLAGS` plus `feature_enabled` in `flags.py`. Move `SUPPORTED_STORY_WORLD_SLUGS` to neutral `curriculum_options.py` so both the selector and write service depend downward rather than the selector importing the service package. Clamp every public selector `limit` to its documented 100/200 cap. Reuse current row builders and prefetch story prerequisites in the story-list query. Preserve filters, timestamp cutoffs, aggregate definitions, response structures, and result ordering exactly. Export the public selector contract through the thin selector initializer.
**Expected output:** All ORM and read-model assembly needed by admin views is callable from named selector modules; no selector imports REST framework, an HTTP view, or `Response`; settings has one read owner.
**Verification:** Focused selector import smoke; Ruff; existing admin API tests; compare exact source query semantics with the ownership table.
**Acceptance evidence:** Selector ownership table records each function, model inputs, ordering/filter/limit, and endpoint consumer.
**Parallel:** No. Views cut over only after selector contracts exist.

## Task 2: Atomically replace the flat HTTP module with focused view modules

**Exact scope:** Create the six domain view modules and a thin `views/__init__.py`; retain every class/decorator/serializer/status/permission and delegate reads to Task 1 selectors and writes to existing services. Keep `adminconsole/urls.py` unchanged. Delete the flat module and dead `_as_bool`/`_safe_int`; do not copy ORM/query logic into the view package.
**Expected output:** The public `adminconsole.views` imports resolve to 15 classes across six focused modules; each method reads as validation/orchestration/response glue.
**Verification:** `python manage.py check`; import all 15 classes; inspect URL resolver class names; focused admin API tests.
**Acceptance evidence:** Before/after view line/module table, public export list, and endpoint resolution table.
**Parallel:** No. This is an atomic cutover dependent on Task 1.

## Task 3: Make the ownership boundary durable

**Exact scope:** Register the deleted flat path in `DISPLACED_BACKEND_PATHS`; extend thin backend package-init checking to `views`; add a high-signal admin HTTP boundary check that rejects model/persistence/query imports and ORM-manager access beneath `adminconsole/views/`; reject REST-framework/view imports in admin selectors; enforce export-only syntax in `adminconsole/views/__init__.py`; resolve direct, parent-package, and relative import aliases; add focused positive and actual-tree tests. The guard must not impose package-style views on other Django apps.
**Expected output:** Restoring the flat implementation or placing ORM work in a new admin HTTP module fails the architecture gate.
**Verification:** `python scripts/checks/check_architecture_boundaries.py`; `python -m pytest common/tests/test_architecture_guard_algorithms.py -q`; a temporary/in-memory parser case proves forbidden imports and `.objects` access are detected if the guard exposes a pure helper.
**Acceptance evidence:** Recorded clean guard output and focused test result; flat path absence.
**Parallel:** No. It codifies Task 2's final architecture.

## Task 4: Prove route, schema, and runtime identity

**Exact scope:** In focused `test_admin_read_api.py`, add one staff-authenticated API test that calls all 10 GET paths in the contract matrix and asserts the preserved top-level keys, including the separate user-detail route. Add deterministic integration tests proving: user `q` filtering, descending join order, and a selector-enforced 100 cap; transaction `user_id` filtering, descending ID order, and a selector-enforced 200 cap; story `sort_order,id`, prerequisite loading, chapter counts, and world-option order; chapter story filtering and `sort_order,number`; official-content owner/chapter eligibility, kind filtering, descending update order, and selector-enforced 200 caps for both official and moderation reads. Keep the pre-existing write/permission tests in `test_admin_api.py` and their small factory in `tests/helpers.py`. Make only narrowly attributable fixes in the planned files; create `EVIDENCE.md` with target-perspective ownership and before/after evidence.
**Expected output:** Every admin read path is exercised through URL resolution, permission handling, view adapter, selector, and query contract. The material list semantics are proven with values and ordering. Full OpenAPI bytes remain identical to a freshly validated baseline artifact.
**Verification:** The baseline was generated before runtime edits from `backend` with `$schemaPath = Join-Path $env:TEMP 'git-it-admin-schema-before.yaml'; python manage.py spectacular --file $schemaPath --validate; Get-FileHash -Algorithm SHA256 $schemaPath`, producing `9A0653EC16B6746A32A4ACC7C83B10003EF2B6A226E7ED64E67F1E50CF735789`; before using it, assert that file still exists and has that hash. From `backend`: `python -m pytest adminconsole/tests common/tests/test_architecture_guard_algorithms.py -q`; `ruff check adminconsole common/tests/test_architecture_guard_algorithms.py`; `python manage.py check`; generate OpenAPI to `%TEMP%/git-it-admin-schema-after.yaml`, compare its bytes and SHA-256 to the validated baseline. From repository root: `python scripts/check_api_contract.py`; `python scripts/checks/check_architecture_boundaries.py`; `python scripts/check_quality_gates.py`; `git diff --check`; confirm no diff under migrations, generated API clients, frontend, assets, or curriculum generated targets.
**Acceptance evidence:** Test counts and outputs; identical OpenAPI SHA-256; no import cycle/boundary errors; the 10-path response-shape matrix; deterministic filter/order/count/limit results; maintainer scenarios answering where to change overview metrics, analytics, user reads, economy reads, curriculum reads, official content, moderation, and settings.
**Parallel:** No. This is the terminal gate for Slice 2.

## Follow-up slices (not authorized by this plan)

The broad goal remains active after Slice 2. Candidate next slices include frontend authoring/home component decomposition and other oversized mixed-owner runtime modules. Each requires its own architecture map, cutover, evidence, and PRE review.
