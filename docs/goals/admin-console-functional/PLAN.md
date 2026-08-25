# Functional Admin Console Implementation Plan

**Intent:** Turn the existing staff-only admin scaffold into a safe, durable, end-to-end control plane for the domains the current product actually supports.
**Current Behavior:** Staff authentication and coarse `/api/admin/*` authorization work, but the SPA advertises two removed destinations, curriculum edits are overwritten by ordinary seeding, newly created stories publish incomplete metadata immediately, staff-authored “official” content compiles into hidden UGC chapters, feature flags have no consumer, challenge activity is absent from analytics, mutations accept malformed values and can lock out the acting administrator, and admin contracts/tests are largely anonymous or absent.
**Expected Outcome:** Every advertised admin destination resolves; staff can safely manage users, coins, durable story/chapter metadata, official content, moderation, runtime settings, and analytics; deployment seeding preserves admin-owned values and staff-published official content; mutations are validated, idempotent where retries matter, and audited; non-staff access is rejected server-side; and generated API types plus automated/browser evidence cover the complete journey.
**Target-Perspective Output:** A staff operator can sign in, open every admin section, make a change, see success or a specific error, reload/reseed without losing durable admin-owned state, and observe the corresponding learner-visible effect. A learner cannot call admin APIs and sees only published, render-ready stories/content. A maintainer can inspect an actor-attributed audit trail and generated contract.
**Truth Owner:** Django models own persisted admin state and row-level management ownership; admin services own validated transitions and audit records; seed data owns every field of rows still marked seed-managed; the admin owns every field of an official Story/Chapter row after that row transfers to admin management; the content compiler owns hidden runtime chapters and official runtime materialization; frontend registries own visual assets; `adminconsole.flags` owns supported runtime flag definitions/defaults; generated OpenAPI owns the HTTP contract.
**Contract Boundary:** Admin APIs accept validated named payloads and return named read models; admin-owned curriculum fields survive normal seeding; seed-owned rows remain updateable from source; official content must target an explicit official chapter; build-time assets and companion definitions are not runtime-admin data.
**Cutover:** Add explicit row-level management ownership: Stories use `seed` or `admin`; Chapters use `seed`, `admin`, or `runtime` for compiler-owned hidden UGC rows. Any admin mutation of an official row transfers the complete row to admin ownership, after which ordinary seeding skips every mutable field on that row; untouched seed-owned rows continue to receive every source update. Add an explicit official runtime chapter to staff-authored content. Remove the displaced Assets and Shop admin links instead of resurrecting deleted runtime asset/listing systems.
**Displaced Path:** Dead `/admin/assets` and `/admin/shop` links, silent seed overwrites of admin-managed fields, hidden `ugc-*` compilation for content explicitly created as official, anonymous request objects, permissive boolean/integer coercion, random per-retry economy keys, self-demotion/self-disable, and unconsumed arbitrary feature flags do not remain as alternate paths.
**Value Density:** The slice fixes every currently exposed admin route and its highest-risk data transitions without rebuilding the intentionally removed asset system or moving build-time visual registries into the database.
**Acceptance Evidence:** Focused migration/seed tests, complete admin API tests, authoring compiler tests, shop flag tests, generated-contract guards, frontend admin route/API/component tests, production build, and a staff-versus-learner browser journey with database assertions.
**Evidence Lane:** Model/migration tests -> seed durability -> focused API/service tests -> authoring runtime tests -> generated contract checks -> frontend unit/build checks -> live browser journey -> final scoped diff review.
**Kill Criteria:** No admin navigation points at an undefined route; no ordinary seed run overwrites an admin-owned story/chapter or unpublishes staff-compiled official runtime; no staff content is called official without an explicit official chapter; no unsafe self-lockout path remains; no retry duplicates a coin ledger entry; no admin operation remains an anonymous generated JSON contract; no claim of full functionality is made without target-perspective browser evidence.
**Architecture Slice:** `AdminLayout`/admin pages -> typed admin API -> `adminconsole` serializers/services/views -> User, Wallet/Ledger, Story/Chapter, ContentDefinition/runtime, FeatureFlag/AuditLog -> learner shop/story/content selectors; seed commands and compiler are the two cutover integration points.
**Plan Review Gate:** Requires PRE review before execution.

## Architecture Map

### Files to create

- `backend/adminconsole/serializers.py` for named request/response contracts and strict validation.
- `backend/adminconsole/flags.py` as the canonical supported-flag registry with explicit absence semantics.
- `backend/adminconsole/services/actions.py` for actor-attributed audit writes and safe user mutations.
- `backend/adminconsole/migrations/0002_adminactionlog.py`.
- `backend/curriculum/migrations/0003_story_chapter_management_source.py`.
- `backend/authoring/migrations/0005_contentdefinition_official_chapter.py`.
- Focused backend migration/seed tests in the nearest existing app test modules.
- `frontend/src/features/admin/adminSections.ts` as the single admin route/navigation registry.
- `frontend/src/features/admin/api/adminApi.test.ts`.
- `frontend/src/features/admin/components/AdminLayout.test.tsx`.
- `frontend/src/features/admin/utils/errors.ts` and its focused test if error parsing is non-trivial.
- This goal package under `docs/goals/admin-console-functional/`.

### Files to modify

- `backend/adminconsole/models.py`, selectors, services, `views.py`, `urls.py`, and `tests/test_admin_api.py`.
- `backend/curriculum/models.py`.
- `backend/curriculum/management/commands/seed_curriculum_structure.py`.
- `backend/curriculum/management/commands/seed_curriculum_challenges.py`.
- Existing curriculum seed/idempotency tests.
- `backend/authoring/models.py`, `services/core.py`, `compiler.py`, selectors/payloads, and focused authoring/compiler tests.
- `backend/shop/views.py`, `backend/shop/selectors/payload.py`, and shop tests for the supported runtime purchase flag.
- `backend/config/urls.py` only if live same-origin verification proves the Django-admin/SPA-admin path collision is real in the deployed topology.
- `frontend/src/app/router.tsx`.
- `frontend/src/features/admin/api/adminApi.ts`.
- All active pages under `frontend/src/features/admin/pages/` and `components/AdminLayout.tsx`.
- `frontend/src/shared/api/queryKeys.ts` as needed for paginated/refreshed admin data.
- `frontend/src/features/shop/types.ts`, shop page/display logic, and tests for the runtime purchase flag.
- API contract generation/check scripts only to include admin in the existing named-schema/type-adoption gate.
- Generated OpenAPI/TypeScript artifacts only via the supported generator.

### Files to avoid

- Removed `backend/assets` and old listing/tower/subscription systems.
- `frontend/public/cosmetics/` and frontend visual registries as runtime admin persistence.
- Unrelated dirty curriculum prose, battle assets, dogfood output, reference captures, and repository-wide formatting.
- Existing migration history; all schema changes are forward-only.
- Generated API files by hand.

### Source of truth

- Persisted admin-owned story/chapter configuration: the complete `curriculum.Story` or `curriculum.Chapter` row when `management_source="admin"`.
- Source-controlled defaults for untouched rows: every mutable field on curriculum rows with `management_source="seed"`.
- Official authored runtime: `ContentDefinition.official_chapter` plus `ContentRuntimeCompiler`.
- Visual renderability: frontend story-world/companion registries; admin may select only world slugs already represented by the current story catalog.
- Admin audit: `adminconsole.AdminActionLog`.
- HTTP contract: DRF serializers -> generated OpenAPI -> generated TypeScript.

### Read path

Admin pages -> admin API read models -> Django querysets/selectors -> database. Learner verification reads the same Story/Chapter, compiled runtime, shop catalog, wallet, and public-content rows through normal learner APIs.

### Write path

Admin form -> named serializer -> domain service inside `transaction.atomic` -> model update + `AdminActionLog` -> query invalidation -> learner selector/API.

### Contract boundary

- Only staff can mutate admin resources.
- Story/chapter writes are strict, non-negative, and durable.
- A new story starts as a draft and uses a known semantic world slug before publication.
- Official content requires a staff actor and explicit official chapter.
- A client request id makes coin adjustments idempotent.
- A staff actor cannot demote or deactivate themself.
- Moderation can mutate only rows that qualify for the moderation queue.
- The supported `shop-purchases` flag has a demonstrable learner-visible effect.

### Integration points

- Account login/bootstrap and `is_staff`.
- Wallet locking/idempotent ledger writes.
- Curriculum seeding/upsert/unpublish cleanup.
- Authoring validation/publish/compiler and seed cleanup of compiled rows.
- Shop catalog/purchase behavior.
- OpenAPI generation and frontend request wrappers.
- React Query invalidation and auth refresh.

### Migration/cutover

- Existing Story and Chapter rows default to `seed`; admin mutations flip the specific row to `admin`.
- Normal seed upserts update only seed-managed rows and never blanket-unpublish admin-managed rows.
- Existing ContentDefinition rows get `official_chapter=NULL`; only new/explicitly assigned staff content uses the official path.
- Existing feature flag rows remain readable, but the admin UI exposes supported runtime flags rather than promising arbitrary behavior.

### Displaced path

Remove dead assets/shop navigation and stale asset-tag/plan wording. Keep the learner Shop route and code-defined catalogs; story pricing remains editable through Curriculum. Do not add a second asset or companion catalog.

### Acceptance evidence gate

The goal is complete only when:

1. Focused backend tests prove authorization, strict validation, self-lockout protection, idempotent coin writes, audit attribution, moderation scoping, challenge+adventure analytics, and runtime flags.
2. A seed-durability test mutates a Story/Chapter through admin, reruns the standard seed command, and proves the values survive while untouched seed-managed rows still update from specs.
3. A staff-created official definition compiles into its explicit published chapter, remains published after standard seeding, and is learner-visible.
4. Generated admin operations have named types and frontend wrappers consume them.
5. Frontend tests prove every navigation entry maps to a route and mutation errors are visible.
6. Browser evidence covers staff and learner contexts, reloads, and every advertised admin destination.

## Task 1: Establish row-level curriculum ownership and seed cutover

**Exact files:** `backend/curriculum/models.py`, `backend/curriculum/migrations/0003_story_chapter_management_source.py`, `backend/curriculum/management/commands/seed_curriculum_structure.py`, the seed cleanup modules that can retire compiled rows, and focused curriculum seed/migration tests.

**Expected output:**

- Existing official rows migrate to `management_source="seed"`; existing `ugc-*` chapters migrate to `runtime`.
- Admin-created rows are `admin`; any later admin edit transfers the complete row to `admin`.
- Standard seeding wholly skips admin-owned rows, including blanket-retirement updates.
- Seed-owned controls still receive all source-defined field changes.
- Seed cleanup excludes official compiled runtime rows by source relationship, not by a broad slug heuristic.

**Verification:** `python manage.py makemigrations --check --dry-run` plus focused migration and seed idempotency/durability tests.

**Acceptance evidence:** An admin-owned Story and Chapter retain every edited field after reseeding, while a seed-owned control row is restored to the current source spec.

**Parallel:** No. This establishes ownership before admin writes build on it.

## Task 2: Add named serializers, audit infrastructure, and safe user actions

**Exact files:** `backend/adminconsole/models.py`, `backend/adminconsole/migrations/0002_adminactionlog.py`, `backend/adminconsole/serializers.py`, `backend/adminconsole/services/actions.py`, `backend/adminconsole/selectors/users.py`, the user endpoints in `backend/adminconsole/views.py`, and focused admin tests.

**Expected output:**

- Named serializers reject malformed booleans, ids, slugs, and unsupported actions.
- User detail reads do not create Player rows.
- The acting staff user cannot demote or deactivate themself.
- Material user changes record actor, target, before, and after in `AdminActionLog`.
- User list/search/detail/action endpoints have complete authorization and malformed-input coverage.

**Verification:** Focused admin user API tests, including non-staff denial, self-lockout attempts, audit assertions, and a read-only detail assertion.

**Acceptance evidence:** A staff actor safely changes another user and can inspect an attributed audit row; malformed/self-lockout requests leave state unchanged.

**Parallel:** No. The audit/serializer primitives are reused by later mutations.

## Task 3: Complete durable Story and Chapter CRUD

**Exact files:** Curriculum serializers/services/views/selectors in `backend/adminconsole`, `backend/adminconsole/urls.py`, `backend/adminconsole/tests/test_admin_api.py`, `frontend/src/features/admin/api/adminApi.ts`, `AdminCurriculumPage.tsx`, and focused frontend tests.

**Expected output:**

- New stories start draft-only with complete validated metadata and a known existing semantic world slug.
- Staff can edit every supported Story field and create/edit every supported Chapter field.
- Duplicate slugs/numbers, negative values, invalid prerequisites, and cycles return specific 400 responses.
- Each mutation transfers the complete row to admin ownership and writes an audit event.
- The UI displays row ownership and retains form state until success.

**Verification:** Story/chapter create-update-conflict-cycle API tests, a seed durability test via real admin endpoints, and focused frontend form/error tests.

**Acceptance evidence:** Staff creates a draft Story plus Chapter, publishes deliberately, reloads, reseeds, and sees the same values; a learner sees it only after publication.

**Parallel:** No. It consumes Tasks 1-2.

## Task 4: Make official content actually official

**Exact files:** `backend/authoring/models.py`, `backend/authoring/migrations/0005_contentdefinition_official_chapter.py`, `backend/authoring/services/core.py`, `backend/authoring/compiler.py`, authoring payloads/tests, admin content serializers/views/tests, `AdminContentPage.tsx`, and focused frontend tests.

**Expected output:**

- Staff creates official content against an explicit curriculum chapter.
- The existing editor edits the definition; publish compiles into that chapter.
- Runtime slugs cannot collide with seed or other official content.
- Standard seeding does not unpublish or detach compiled official rows.
- Player-authored content keeps the existing hidden UGC/playtest path.

**Verification:** Focused authoring API/compiler/admin tests, then a standard curriculum seed followed by runtime visibility assertions.

**Acceptance evidence:** A learner reads/launches the published staff-authored level from the selected official chapter after reseeding; a normal author’s content still stays out of official curriculum.

**Parallel:** No. It depends on Task 1 ownership and seed cutover.

## Task 5: Make economy adjustments retry-safe and attributable

**Exact files:** `backend/adminconsole/services/economy.py`, economy serializers/views/tests, `frontend/src/features/admin/api/adminApi.ts`, `AdminUsersPage.tsx`, `AdminEconomyPage.tsx`, and focused frontend/API tests.

**Expected output:**

- Coin adjustments require a client request id reused by auth-refresh retries.
- The id maps to the ledger award key and creates at most one ledger row across retries.
- Successful first application writes one actor-attributed audit event with before/after balance; a duplicate writes none.
- UI requires a reason, preserves values on error, and renders specific failures.

**Verification:** Duplicate-request, insufficient-balance, malformed-number, audit, and focused frontend request-id/error tests.

**Acceptance evidence:** Replaying the same adjustment produces exactly one ledger row, one audit row, and one learner wallet change.

**Parallel:** No. It consumes Task 2 audit infrastructure.

## Task 6: Replace placebo settings with a supported runtime flag

**Exact files:** `backend/adminconsole/flags.py`, feature-flag model/selectors/serializers/views, `backend/shop/views.py`, `backend/shop/selectors/payload.py`, shop/admin tests, `AdminSettingsPage.tsx`, learner shop types/page/display logic, and focused frontend tests.

**Expected output:**

- `adminconsole.flags.SUPPORTED_FLAGS` is the only accepted key registry.
- `shop-purchases` has explicit absence semantics: no database row means enabled, preserving fresh and upgraded deployments without a bootstrap race.
- An existing supported row overrides the default; unsupported persisted rows are ignored and unsupported writes return 400.
- Catalog responses expose purchase availability and learner UI disables purchase clearly when off.
- Toggle writes an audit event.

**Verification:** Fresh-database default-on, existing-row off/on, unsupported-key, learner purchase-blocked/enabled, and frontend UI tests.

**Acceptance evidence:** Staff toggles the supported setting and a learner immediately sees purchasing disabled/enabled, including after reload.

**Parallel:** No. It shares admin serializers/audit and shop contract generation.

## Task 7: Complete dashboard and analytics truth

**Exact files:** Admin overview/analytics views/selectors/serializers/tests, `AdminDashboardPage.tsx`, `AdminAnalyticsPage.tsx`, and focused frontend tests.

**Expected output:**

- Shop spending counts only shop purchase debits; admin deductions are labeled separately.
- Dashboard renders signup grant, recent purchases, and recent admin actions.
- Analytics combines AdventureRun and ChallengeRun for status totals, passes, active learners, and per-story rows.

**Verification:** Mixed-ledger aggregate tests, an Adventure+Challenge exact fixture, and focused dashboard/analytics rendering tests.

**Acceptance evidence:** Staff sees exact database-backed totals for both run types and recent activity, with labels matching query semantics.

**Parallel:** No. It consumes audit and finalizes shared read contracts.

## Task 8: Centralize routes and finish remaining SPA mutation UX

**Exact files:** `frontend/src/features/admin/adminSections.ts`, `frontend/src/app/router.tsx`, `AdminLayout.tsx`, active admin pages, query keys, `frontend/src/features/admin/utils/errors.ts`, and focused frontend tests.

**Expected output:**

- One registry owns both sidebar entries and router children; all entries resolve.
- Removed Assets/Shop admin links do not remain.
- All mutations retain form state until success, show precise errors, confirm destructive actions, and refresh affected queries.
- User/economy/dashboard/settings/moderation copy and state reflect actual behavior.
- Mojibake in touched admin/authoring copy is removed.

**Verification:** Focused RTL tests for staff/non-staff shell, route registry, API calls, errors, and destructive confirmations; then frontend lint/test/build.

**Acceptance evidence:** A staff operator can complete each action without silent failure; a non-staff user is redirected client-side and remains forbidden server-side.

**Parallel:** No. The work shares the central API/types and route registry.

## Task 9: Generate and enforce admin API contracts

**Exact files:** `backend/adminconsole/serializers.py`, admin `extend_schema` declarations, `scripts/api/api_contract.py`, `scripts/checks/check_api_type_adoption.py`, `frontend/src/features/admin/api/adminApi.ts`, and generated artifacts through the supported generator.

**Expected output:**

- Every admin operation has a named request/response component.
- `adminApi` uses `apiOperationRequest` and generated operation shapes.
- Contract/type-adoption guards include admin.

**Verification:**

- `python scripts/generate_api_contract.py`
- `python scripts/check_api_contract.py`
- `python scripts/check_api_type_adoption.py`
- Focused admin API wrapper tests and frontend build.

**Acceptance evidence:** Generated TypeScript represents complete Story/Chapter fields and all mutations compile without handwritten duplicate HTTP shapes.

**Parallel:** No. Generate only after endpoint shapes settle.

## Task 10: Capture end-to-end staff and learner evidence

**Exact files:** Test fixtures/helpers only, unless a narrowly attributable integration fix is required.

**Expected output:** Full focused backend/frontend gates pass, and a browser journey proves staff versus learner behavior, live mutations, reload persistence, reseed durability, and every admin route.

**Verification:** Complete focused backend suites, frontend lint/test/build, live Django/Vite browser run with staff and learner fixtures, `git diff --check`, and scoped status review.

**Acceptance evidence:** Saved screenshots or directly observed browser state plus exact automated-test totals. If browser or reseed evidence cannot be captured, report "implemented but unproven."

**Parallel:** No. Final integration gate.

## Action-by-action acceptance evidence matrix

| Capability | Staff browser action | Learner/browser or DB effect | Persistence/audit proof |
|---|---|---|---|
| Navigation | Open every entry from the shared registry | No undefined route or blank shell | Route registry test and a loaded heading for each entry |
| Authorization | Learner opens `/admin` and calls every admin endpoint class | Client redirects; server returns 401/403 | Parametrized endpoint denial test |
| Users | Promote/demote and disable/re-enable a target | Target gains/loses admin navigation after refresh and cannot authenticate while disabled | Actor/target/before/after audit rows; self-lockout rejected |
| Economy | Submit a reasoned credit and replay the same request id | Wallet changes once | Exactly one ledger row and one audit row after replay/reload |
| Story/Chapter | Create draft, fill metadata/chapter, publish | Learner APIs show it only after publish | Reload plus ordinary reseed retains every admin-owned field |
| Official content | Create against a chapter, edit, validate, publish | Learner sees/launches runtime from that chapter, not `ugc-*` | Runtime source/FK assertion before and after ordinary reseed |
| Moderation | Confirm unpublish of queued public UGC | Public learner lookup loses it; owner still sees private draft | Audit includes actor, content, reason, and before/after |
| Settings | Toggle `shop-purchases` off then on | Learner Shop disables/enables purchase | Audit and reload persistence; fresh DB defaults on |
| Analytics | Load AdventureRun and ChallengeRun fixture | UI totals/per-story rows match fixture | API assertions cover both run models |
| Dashboard | Load mixed purchases/admin deductions and audit activity | Labels and recent rows match source reasons | Aggregate test distinguishes shop spend from admin debit |

## Non-goals

- Reintroducing runtime asset upload, database asset records, store-listing models, subscriptions, or tower editing removed by the current architecture.
- Making build-time companion prices or visual files editable without a deployment pipeline.
- Redesigning the learner Shop, story map, battle UI, or broad product visual language.
- Adding fine-grained staff roles beyond the current trusted-staff boundary.
- Deleting unrelated user-owned worktree changes or globally reformatting the repository.
- Making destructive `seed --reset` preserve runtime data; the supported ordinary seed path is the durability target.

## Risk if wrong

An incorrect seed cutover could freeze source-owned curriculum updates or still erase admin changes. Official compilation could collide with seeded runtime slugs or leak player UGC into learner progression. Audit/idempotency mistakes could double-pay coins. A runtime flag with the wrong default could disable purchases. Broad edits in the dirty worktree could obscure ownership, so every change and verification must remain inside the mapped slice.
