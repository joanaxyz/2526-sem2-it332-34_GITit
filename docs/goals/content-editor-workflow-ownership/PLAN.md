# Content Editor Workflow Ownership — Slice 3 Implementation Plan

**Intent:** Advance the active codebase-maintainability goal by turning the 398-line content-editor route into a composition boundary with one explicit workflow controller and focused, accessible rendering components.
**Current Behavior:** `ContentEditorPage.tsx` is two lines below the global frontend file ceiling and owns route/search parsing, staff official-mode decisions, four queries, four mutations, source-keyed draft/baseline state, dirty guarding, request-envelope construction, cache invalidation, navigation/toasts, and all destination/metadata/diagnostic markup. It has no page-level behavior tests. Generic destination layout also depends on `.author-inline-row` from the unrelated battle-stage stylesheet. On the edit route, the command-form query is enabled from the route's fallback `newKind` instead of the loaded definition kind, so editing a lesson can make an irrelevant command-form request. During the disposable real-path gate, an ordinary-author POST with the existing `official_chapter: null` request field returned 403: `_resolve_official_chapter` checks staff permission before treating a null ID as no official destination.
**Expected Outcome:** `ContentEditorPage` becomes a small loading/error/composition adapter. `useContentEditorController` is the sole in-session workflow owner. Four focused components own the header/actions, destination selection, metadata fields, and diagnostics/raw disclosure. Existing structural editors remain unchanged. Route, API, mutation, accessibility, and visual behavior stay stable while previously implicit contracts become deterministic integration tests and durable architecture rules. Draft behavior becomes trustworthy under races: new-draft identity includes destination query presets, pending writes remain navigation-guarded, post-submit edits survive successful responses as dirty work, and Validate/Publish require a clean saved revision. The controller also uses the effective loaded/new content kind so command-form data is never requested for a lesson. Backend destination selection gives precedence to a non-null authored chapter, otherwise resolves an explicitly supplied official destination; a null official destination is accepted for any authenticated author while every non-null official ID remains staff-only.
**Target-Perspective Output:** An author can create, edit, validate, and publish drafts through the same protected routes and API payloads; a staff author can attach official content through the same staff-only chapter path; dirty/saved status and unsaved navigation behavior remain trustworthy; mobile destination controls do not overflow. A maintainer can find workflow state in one hook and edit each UI region without scanning API orchestration.
**Truth Owner:** Backend authoring services remain durable access/validation/publish truth. Existing `authoringModel.ts` remains definition serialization/deserialization truth. `useContentEditorController.ts` becomes the sole route-scoped draft, query, mutation, cache, navigation, toast, and dirty-guard owner. Focused components own only their DOM/accessibility region; `ContentEditorPage` owns only loading/error boundaries and composition.
**Contract Boundary:** Preserve both `/level-editor/new/:kind` and `/level-editor/:definitionId`; `official=1` and `chapter` semantics; `ContentEditorPage` named export; existing authoring/admin API operations, request fields, cache keys, errors, toast text, replacement navigation, CSS hooks/visual ordering, and generated API types. Intentional behavior corrections are authorized: command-form reads follow the effective loaded/new content kind; new-draft state keys include destination mode/preset; Validate/Publish are disabled for dirty drafts; mutation callbacks reconcile against submitted source/form snapshots so later edits survive; pending writes remain under the unsaved-navigation guard, with successful new-save replacement navigation deferred through a controller-owned internal target; and create/update share exact destination precedence after `_validate_chapter_choice`: a non-null authored `chapter` resolves and clears official; otherwise an explicit `official_chapter` resolves (null before staff enforcement) and clears authored; an explicit null `chapter` with no official key clears both. Both-non-null validation and non-null official permission stay unchanged. No backend API/schema/serializer/migration edit is allowed. Backend runtime scope is limited to this shared destination-choice correction in `backend/authoring/services/core.py`; backend test scope is limited to its API regression plus the additive architecture test.
**Cutover:** Create and test the controller and focused components, then atomically replace the embedded workflow/markup in `ContentEditorPage.tsx`. All current callers continue importing the same page export. Delete the displaced page-owned draft helpers, API/query/mutation logic, and destination/metadata/diagnostic markup; do not add a compatibility barrel or second controller.
**Displaced Path:** `ContentEditorPage.tsx` may no longer import React Query, API clients, query keys, auth state, router workflow hooks, Sonner, the unsaved guard, or serialization utilities. It may not define `DraftState`, `sameForm`, `buildInput`, or workflow mutations. Files under `components/content-editor/` may not import API clients, React Query, auth state, query keys, toast, the controller, or the page. The hook may not import rendering components or the page. Destination wrapping may no longer depend solely on the battle-stage-owned generic row class.
**Value Density:** This removes the highest-ranked remaining feature-page hotspot, gives an untested write workflow deterministic coverage, exposes accessibility contracts, and establishes a repeatable page/controller/component boundary before the next home-hub decomposition.
**Acceptance Evidence:** Exact before/after ownership and line/import metrics; deterministic ordinary/staff/non-staff/edit/lesson/failure/raw-disclosure integration tests; exact request payload and replacement-route assertions; controller dirty/busy/guard evidence; architecture rejection of displaced imports/definitions, controller forwarding, reverse feature imports, and oversized page/components; production build/lint/dead-code/API-contract gates; real browser request/response and persisted-reload evidence against an identity-verified disposable SQLite/database-and-port session; durable desktop/mobile screenshots and overflow/keyboard checks.
**Evidence Lane:** Baseline metrics/8 utility tests/build/lint -> controller extraction -> focused components -> atomic page cutover -> architecture guard -> integration tests -> build/lint/dead/API gates -> disposable full-stack browser author/staff workflows -> screenshots/request/persistence trace -> fast repository gates -> POST/correctness/maintainability/verifier reviews.
**Kill Criteria:** Page at most 150 lines with zero forbidden workflow imports/markers; controller at most 300 lines and the only route-scoped draft/source-key state and effect owner; pure draft support at most 120 lines; each focused component at most 180 lines and HTTP-free; no duplicate request-envelope, mutation, or baseline logic; exact normal/official mutually-exclusive chapter payloads proven; null official destination accepted for a non-staff authored save while non-null official destination remains 403; new-save replacement URL and clean baseline proven; query-preset navigation materializes the correct draft identity and confirmed discard cannot resurrect an earlier draft; dirty Validate/Publish are blocked; deferred save/publish/create-chapter responses cannot overwrite post-submit edits; pending writes retain pathname/search/hash navigation protection; edit/save/publish/error draft behavior proven; accessible status/alert/raw disclosure proven; 390px destination/actions have no horizontal overflow; old CSS-only destination dependency displaced; alias, relative, barrel, quoted, and static-template import bypasses are rejected; no router/API/model/generated or backend API/schema/serializer/migration edit, and no backend runtime edit beyond the exact shared destination-choice/null-before-permission correction; full-stack saved rows reload from the disposable backend.
**Architecture Slice:** `frontend/src/features/authoring` content-editor workflow and its scoped editor-shell destination layout only. Existing structural editors, authoring model/API contracts, router, and backend remain outside the slice.
**Plan Review Gate:** Requires PRE review before execution.

## Architecture Map

### Exact ownership after cutover

| Owner | Exact responsibility | Forbidden responsibility |
|---|---|---|
| `hooks/useContentEditorController.ts` | Route/search/auth parsing; detail/chapter/official-chapter/command-form reads; source-keyed draft and saved baseline; input envelope; create/save/validate/publish mutations; cache invalidation; replace navigation; toast/error outcomes; dirty/busy/guard state | DOM regions, visual components, backend validation truth |
| `hooks/contentEditorDraftState.ts` | Pure draft identity, snapshot equality, same-source saved-response reconciliation, and same-source chapter merge helpers | React state/effects, routing, HTTP/query/auth/toast imports |
| `components/content-editor/ContentEditorHeader.tsx` | Eyebrow/title, polite status, Save/Validate/Publish controls and disabled states | API/query/auth/router logic |
| `components/content-editor/ContentDestinationSection.tsx` | Authored/official chapter label/select/help; create/manage/edit actions; explicit destination accessibility | API/query/auth logic or direct form serialization |
| `components/content-editor/ContentMetadataSection.tsx` | Controlled title/slug/summary/command-family/difficulty/tags/visibility fields | Draft baseline, API, navigation, toasts |
| `components/content-editor/ContentEditorDiagnostics.tsx` | Local form/server errors, compile summary, generated-JSON disclosure and accessibility state | Network workflow or cache ownership |
| `pages/ContentEditorPage.tsx` | Controller invocation; loading/error boundary; narrow prop wiring; existing stage/lesson/levels editor composition | Workflow state, API/query/mutation, serialization, duplicated UI regions |
| Existing `utils/authoringModel.ts` | Form defaults, definition serialization/deserialization, compile/error interpretation | Route or HTTP workflow |
| Existing APIs/backend | HTTP and durable write/validation/publish behavior | UI draft state |

### Controller return contract

`useContentEditorController()` returns one page-consumed object which the page immediately destructures; no rendering component receives that whole object:

- `form`, `setForm`, `sourceKey`, `isNew`, `isOfficialMode`.
- `chapters`, `commandFormOptions`.
- `isLoading`, `loadError`, `busy`, `isDirty`, `canUseActions`, `officialDestinationMissing`.
- `formError`, `validationErrors`.
- `save`, `validate`, `publish`, `createChapter` action callbacks.

The pure draft-support module owns `DraftState`, `sameForm`, source identity, and reconciliation algorithms. The hook owns `buildInput`, all route-scoped state/effects, saved snapshot, and every mutation. Diagnostics owns only the disclosure state and derives raw JSON from the passed form through the existing model utility.

### Files to create

- `frontend/src/features/authoring/hooks/useContentEditorController.ts`
- `frontend/src/features/authoring/hooks/contentEditorDraftState.ts`
- `frontend/src/features/authoring/components/content-editor/ContentEditorHeader.tsx`
- `frontend/src/features/authoring/components/content-editor/ContentDestinationSection.tsx`
- `frontend/src/features/authoring/components/content-editor/ContentMetadataSection.tsx`
- `frontend/src/features/authoring/components/content-editor/ContentEditorDiagnostics.tsx`
- `frontend/src/features/authoring/pages/ContentEditorPage.test.tsx`
- `docs/goals/content-editor-workflow-ownership/EVIDENCE.md`
- `docs/goals/content-editor-workflow-ownership/PRE_SLICE_BASELINE.md`
- `docs/goals/content-editor-workflow-ownership/evidence/content-editor-desktop.png`
- `docs/goals/content-editor-workflow-ownership/evidence/content-editor-mobile.png`

### Files to modify

- `frontend/src/features/authoring/pages/ContentEditorPage.tsx`
- `frontend/src/features/authoring/hooks/useUnsavedChangesGuard.ts` (only an exact allowed-next-location option for SPA transitions; `beforeunload` remains governed solely by `when`)
- `frontend/src/styles/features/authoring/editor-shell.css`
- `scripts/checks/check_architecture_boundaries.py`
- `backend/common/tests/test_architecture_guard_algorithms.py`
- `backend/authoring/services/core.py` (only the shared create/update destination-precedence correction and null-before-permission ordering)
- `backend/authoring/tests/test_authoring_api.py` (only the matching POST/PATCH regression test)

### Files to avoid

- `frontend/src/app/router.tsx`
- `frontend/src/features/authoring/api/authoringApi.ts`
- `frontend/src/features/admin/api/adminApi.ts`
- `frontend/src/features/authoring/utils/authoringModel.ts` and its partitioned helpers
- `frontend/src/features/authoring/types.ts`
- `frontend/src/shared/api/queryKeys.ts` and generated API files
- Existing `BattleStageEditor`, `LevelsEditor`, `ProblemsEditor`, `ChapterLessonPagesEditor`, and `TagsField` implementations
- Home files and broader authoring stylesheet decomposition
- Backend runtime models/views/services/migrations other than the exact named resolver correction, curriculum targets, assets, and existing Slice 1/2 work.

### Read and write paths

```text
router -> ContentEditorPage -> useContentEditorController
       -> route/search/auth -> exact React Query reads -> formFromContent
       -> source-keyed controlled draft -> focused components/existing structural editor

field change -> setForm -> controller save
             -> formToDefinition -> exact ContentDefinitionInput
             -> authoringApi create/update -> backend authoring service
             -> returned content -> saved baseline + cache invalidation + toast + replace navigation
```

Validate/publish follow the same view -> controller -> existing API -> backend path and retain server-owned validation/immutability. Official chapter reads retain the existing one-way authoring-to-admin API dependency; admin must not import authoring back.

### Exact rendering prop contracts

The page must destructure the hook result at the call site. It may not bind a controller object, forward a controller prop, or spread controller output into a component.

- `ContentEditorHeader`: receives only `kind`, `title`, `isNew`, `busy`, `isDirty`, `canUseActions`, `officialDestinationMissing`, and the three zero-argument action callbacks `onSave`, `onValidate`, and `onPublish`. It may not receive `form`, `setForm`, or controller/query/mutation objects.
- `ContentDestinationSection`: receives only `isOfficialMode`, chapter `{ id, title }` options, `selectedChapterId`, `createChapterDisabled`, `onDestinationChange(id | null)`, and `onCreateChapter`. The page derives `createChapterDisabled` from the controller's full `busy` state, so chapter creation cannot overlap any write. The component derives the existing manage/edit links from those scalars and may not receive `form` or `setForm`.
- `ContentMetadataSection`: receives `sourceKey`, `kind`, the seven editable scalar/list values (`title`, `slug`, `summary`, `commandFamily`, `difficulty`, `tags`, `visibility`), and field-specific callbacks (`onTitleChange`, `onSlugChange`, `onSummaryChange`, `onCommandFamilyChange`, `onDifficultyChange`, `onTagsChange`, `onVisibilityChange`). It may not receive `form` or `setForm`.
- `ContentEditorDiagnostics`: is the sole extracted rendering component intentionally receiving the full `form`, plus `formError` and `validationErrors`; it owns local raw-disclosure state and uses the existing model utilities only.
- Existing structural editors continue receiving only their current slices and change callbacks directly from the page.

### Durable boundary

Extend the architecture checker with a pure source helper and actual-tree checks that enforce page 150, controller 300, pure draft-support 120, and component 180 line ceilings; reject every forbidden import and displaced page marker; enforce the hook-to-rendering direction; keep `contentEditorDraftState.ts` free of React state/effects, sibling hooks, router, HTTP/query/auth/toast, page, and rendering dependencies; and reject API/query/auth/toast dependencies beneath `components/content-editor/`. The page rule must also reject binding `const controller = useContentEditorController()`, controller prop/spread forwarding, and passing `form`/`setForm` to Header, Destination, or Metadata. Component rules reject imports of the hook or page. A feature-direction rule rejects `features/admin -> features/authoring`, which would close the intentionally preserved `features/authoring -> features/admin/api` edge. Canonicalize alias and relative static/dynamic/`require` specifiers, including static template literals and exact barrels, before matching boundaries. Add positive synthetic tests for these import forms, controller binding/forwarding, forbidden form props, the reverse feature edge, and actual-tree clean assertions. Do not impose this exact controller pattern on unrelated pages.

### Dirty-worktree preservation contract

`PRE_SLICE_BASELINE.md` records the complete pre-Slice-3 dirty status, SHA-256 hashes for every out-of-scope dirty file, and pre-edit content/diff hashes for all four shared/additive files. Slice 3 may add to `scripts/checks/check_architecture_boundaries.py` and `backend/common/tests/test_architecture_guard_algorithms.py`; it must not revert, reformat, rename, or weaken the recorded admin-console guard hunks. The late-discovered browser blocker additionally permits only one shared destination-choice helper/call-site cutover and one matching POST/PATCH API regression in the two named authoring files. At the terminal gate, re-hash every out-of-scope path against the manifest and assert all recorded shared-file symbols/tests and both official-destination permission outcomes are still present before reviewing the Slice-3 additions.

Before the first Slice 3 implementation edit, run the manifest preflight: recompute every out-of-scope path hash/deletion state, all four shared/additive full-file hashes, and all four Git-diff hashes. Abort on any mismatch and update/re-review the baseline rather than assuming ownership. The exact same out-of-scope checks run again at the terminal gate; the shared files then use symbol/test-presence and focused regression assertions because their hashes will intentionally change additively.

## Task 1: Extract the route-scoped workflow controller

**Exact scope:** Move current route/search/auth parsing, queries, draft/baseline state, `buildInput`, create/save/validate/publish mutations, cache invalidations, navigation/toasts, busy/dirty/guard state, and load/error outputs into `useContentEditorController.ts`; place only pure `DraftState`, equality, new-source identity, saved-response reconciliation, and chapter-merge algorithms in `contentEditorDraftState.ts`. Keep exact cache keys, messages, payload fields, and replacement URL. Derive route source identity from `content:<route-id>` for edits and from kind, requested destination mode, and preset chapter for new drafts. On every source change, clear the prior source's snapshot/error state and immediately materialize the new base form, or install an unresolved edit-source sentinel until its detail arrives, so confirmed discard and return cannot resurrect the abandoned draft. Pass source/form/mode/id snapshots as mutation variables. Every completion first compares a current-source ref with the submitted source: stale success/error may invalidate its own cache keys but may not change current draft, baseline, form error, toast, or location. For a same-source new save, set the server baseline under `content:<saved-id>` and transfer the latest materialized form to that source (server form if unchanged or still only derived from query data, otherwise the newer form dirty); publish mirrors this without changing route identity; create chapter merges into the latest stored same-source form, falling back to the submitted materialized form when clean route navigation left the stored draft on an older source. Count create-chapter as busy, reject `createChapter` invocation while any write is busy, and keep `when` true for dirty or pending writes. Extend `useUnsavedChangesGuard` with one exact allowed next SPA location: its blocker permits only that exact `pathname+search+hash`, while every other SPA transition and `beforeunload` remain guarded. Set the allowed target only after a current-source successful new save, navigate it from a normal effect after the blocker's exact allowance has registered, and clear it immediately after dispatch. Preserve query enabled conditions except for the explicit lesson correction: derive `effectiveKind = isNew ? newKind : detail.data?.kind` and enable command forms only when `effectiveKind` is known and is not `lesson`; this prevents a speculative adventure query while an edit detail is loading and skips the read for both new and loaded lessons. Keep raw JSON disclosure out of the hook. Do not change API/model utilities.
**Expected output:** One cohesive hook owns all workflow state and effects; it exposes only the documented return contract and imports no components/page.
**Verification:** Hook import/typecheck; focused page tests for queries, payloads, navigation, invalidations, dirty baseline, busy guard, and failures; ESLint.
**Acceptance evidence:** Controller ownership table and request/action trace; page has zero displaced workflow definitions after Task 3.
**Parallel:** No. Components and page depend on the frozen controller contract.

## Task 2: Extract focused accessible rendering regions

**Exact scope:** Create the four named components with explicit narrow props. Preserve class names, text, DOM order, button variants/sizes, icon hiding, field labels, links, and structural-editor placement. Preserve disabled behavior except for two trust corrections: Validate and Publish additionally require `!isDirty`, and New chapter is disabled for the controller's full `busy` state. Improve semantics without copy drift: status uses `role="status"` plus `aria-live="polite"`; error container uses `role="alert"`; raw toggle exposes `aria-expanded` and `aria-controls`; destination select has a visible label and stable id. Add `.author-destination-row` in `editor-shell.css` as the complete owner of destination layout: it defines `display`, alignment, gap, select/input flex sizing, and wrapping itself, plus its scoped mobile rule. It may coexist with `author-inline-row` temporarily for visual compatibility but must remain correct if the battle-stage selector disappears.
**Expected output:** UI regions can be maintained and tested independently; accessibility state is programmatic; no rendering component knows HTTP/query/auth state.
**Verification:** Focused Testing Library assertions; ESLint; browser keyboard/overflow checks at desktop and 390px.
**Acceptance evidence:** Accessibility role/name/state trace plus desktop/mobile screenshots with unchanged visual hierarchy and zero horizontal overflow.
**Parallel:** No. Implement sequentially so prop contracts follow Task 1 rather than duplicate state.

## Task 3: Atomically cut the page over and prove workflow behavior

**Exact scope:** Replace the current page implementation with controller invocation, loading/error handling, component wiring, and unchanged existing stage/lesson/levels editors. Add a page integration test using a memory router, isolated QueryClient, real auth store state, mocked API boundaries, and mocked heavy structural editors only.
**Expected output:** Named page export and routes remain stable; page is at most 150 lines and reads as composition.
**Verification cases:**

1. `/level-editor/new/adventure?chapter=<authored-id>` loads authored chapters, presets that authored destination, sends exact `chapter: <authored-id>` plus `official_chapter: null`, replaces to `/level-editor/<id>`, and becomes clean.
2. Staff `/level-editor/new/adventure?official=1&chapter=<official-id>` uses admin chapters, presets the official destination, hides create-chapter UI, sends `chapter: null` plus `official_chapter: <official-id>`, and preserves `?official=1` on replace. A second assertion clears the selection and proves Save is blocked until a destination is chosen.
3. A loaded official edit at `/level-editor/<id>` without `official=1` derives official mode from `detail.official_chapter_id`, uses the admin query, and preserves mutually exclusive official payload fields.
4. A non-staff `/level-editor/new/adventure?official=1&chapter=<id>` never runs the admin query, never exposes official UI, and never sends an `official_chapter` value.
5. Loaded ordinary edit starts clean, field change becomes dirty and enables the guard, disables Validate/Publish, PATCH save resets the baseline, and another edit becomes dirty again.
6. Validate, publish, and API rejection preserve the draft while exposing exact accessible feedback; clean successful publish resets the baseline. Deferred save and publish responses preserve edits made after submission as dirty instead of replacing them.
7. Both `/level-editor/new/lesson` and `/level-editor/<lesson-id>` disable command-form lookup from the effective content kind and preserve the lesson editor path. The loaded edit must assert zero command-form API calls, including while detail is unresolved, as the regression proof for the pre-existing route-fallback bug.
8. Raw disclosure exposes correct expanded/control state and malformed structured input reports the current model error.
9. Same-component navigation between authored and official same-kind new URLs with different destination query presets selects the new mode/preset and starts clean. Confirmed discard from one new preset to another and return cannot resurrect the abandoned draft; dirty navigation to an unresolved edit source and back before its detail resolves cannot resurrect either source's prior draft. A deferred create-chapter response merges its chapter ID into the latest edited form.
10. Deferred save/publish/create-chapter responses preserve same-source post-submit edits. For a post-edit new save, the exact internal replacement prompts zero times, transfers the newer form to `content:<saved-id>` as dirty, and the next user navigation still prompts. If the user confirms navigation to another same-component source while new-save/save/publish/create/validate is pending, its stale completion may invalidate caches but cannot alter the new location/form/baseline/error/toast or navigate back. While any write is pending, New chapter is disabled and direct callback invocation is rejected, proving full-busy mutation exclusion.

**Acceptance evidence:** Test-captured payloads, query selection, route replacement, guard state transitions, and accessible error/disclosure states.
**Parallel:** No. Atomic integration depends on Tasks 1–2.

## Task 3a: Correct authored/official destination precedence

**Exact scope:** Replace the duplicated key-presence branches in `ContentDefinitionService.create` and `.update` with one private destination-choice helper called immediately after `_validate_chapter_choice`. If `chapter` is non-null, resolve that authored chapter and clear official. Otherwise, if `official_chapter` is present, resolve it and clear authored; `_resolve_official_chapter` returns `None` before staff enforcement only for a null ID. If only an explicit null `chapter` is present, clear both. Keep both-non-null validation unchanged. Add one API regression in `test_authoring_api.py`: a non-staff user posts their own authored chapter with both fields (`chapter: own_id`, `official_chapter: null`), receives 201, then PATCHes to a second owned chapter with the same two-field shape, receives 200, and persists the new authored ID with `official_chapter_id is None`. Keep the existing `test_non_staff_cannot_place_content_in_official_chapter` assertion at 403/no row.
**Expected output:** The frontend's preserved mutually-exclusive payload contract works for ordinary authors without weakening official-curriculum permissions.
**Verification:** Run the new POST/PATCH regression and the existing non-null permission test together, then the whole authoring API test file. Re-run the disposable ordinary-author POST before any staff workflow.
**Acceptance evidence:** Exact 201 then 200 with authored foreign-key persistence and official null, plus exact 403/no-row persistence for a non-null official destination; real browser normal-author POST and persisted reload.
**Parallel:** No. This is a plan amendment caused by real-path evidence and requires PRE alignment before the two backend files change.

## Task 4: Enforce boundaries and capture real full-stack evidence

**Exact scope:** Add the scoped architecture rules/tests; create EVIDENCE.md and the two durable screenshot files; make only narrowly attributable fixes inside planned files. Before any server starts, create a unique session child beneath a newly allocated temporary directory outside the workspace, reserve/check separate free loopback backend and frontend ports that are not 8000/5173, and record both ports and every spawned PID. Start Django with explicit `DATABASE_URL=sqlite:///<session-db>`, `DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost`, `DJANGO_CORS_ALLOWED_ORIGINS=http://127.0.0.1:<frontend-port>`, `DJANGO_CSRF_TRUSTED_ORIGINS=http://127.0.0.1:<frontend-port>`, and credential/cookie development settings. Start Vite with explicit `VITE_API_BASE_URL=http://127.0.0.1:<backend-port>/api` and the dedicated frontend port. Readiness must prove both spawned PIDs are alive and responses come from the dedicated ports. Create unique disposable normal/staff accounts and minimal curriculum rows only after migration, authenticate through the UI/API, and verify the returned current-user identity equals the session's unique account before any browser mutation. Any port collision, process exit, readiness mismatch, API-base mismatch, or identity mismatch fails closed with zero mutation. In a `finally` path, stop only recorded spawned PID trees. Delete only after resolving and proving that the target is the newly-created session child outside both workspace roots; never delete a parent temp directory or any unverified path.
**Expected output:** The structural cutover cannot drift back and the real browser/API workflow proves behavior beyond mocks.
**Verification:** Run the exact commands in `Verification commands and timeout policy` below. The full Vitest suite is a bounded diagnostic: wait at most 300 seconds; if still running, terminate only the recorded spawned npm/Vitest process tree, record `TIMED_OUT_BASELINE_MATCH`, and continue because the independent pre-cutover run had the same 304-second/no-output condition. A completed nonzero run or any focused-test failure is a blocker.
**Browser evidence:** Normal-author create/save POST payload, replace URL, saved status, persisted reload, dirty navigation cancel; staff official destination/save/validate with persisted official attachment; keyboard traversal; measured document/control overflow; captured console/network errors. Save desktop 1440x900 and mobile 390x844 screenshots to the two planned `docs/goals/content-editor-workflow-ownership/evidence/` paths before deleting the disposable session; summarize request/identity/persistence traces in EVIDENCE.md. Do not use or mutate the developer's persistent database.
**Acceptance evidence:** Deterministic request/response/status/persisted-row trace from the disposable backend, screenshots, accessibility/overflow observations, boundary results, and final review verdicts. If the disposable full-stack path cannot run, report `implemented but unproven`.
**Parallel:** No. Terminal evidence/review gate.

## Verification commands and timeout policy

Run these exact commands from the named directory:

```powershell
# C:\Users\Joana\Documents\GIT-IT — mandatory preflight before implementation
$manifest = Get-Content -LiteralPath docs/goals/content-editor-workflow-ownership/PRE_SLICE_BASELINE.md
$failures = [Collections.Generic.List[string]]::new()
foreach ($line in $manifest) {
    if ($line -match '^\| `(?<path>[^`]+)` \| `(?<expected>[A-F0-9]{64}|<deleted>)` \|$') {
        $path = $Matches.path
        $expected = $Matches.expected
        if ($expected -eq '<deleted>') {
            if (Test-Path -LiteralPath $path) { $failures.Add("Expected deleted: $path") }
        } elseif (-not (Test-Path -LiteralPath $path -PathType Leaf)) {
            $failures.Add("Missing: $path")
        } elseif ((Get-FileHash -Algorithm SHA256 -LiteralPath $path).Hash -ne $expected) {
            $failures.Add("Hash mismatch: $path")
        }
    }
}
$shared = @{
    'scripts/checks/check_architecture_boundaries.py' = @('5E97126874E1D37FC3E30170E3673E8F04426F06133C979617C4D74AE51DBCAF', '1E3E117E045462B304388A8288A3677CC406E42F28D0C5214FE43FD01C468808')
    'backend/common/tests/test_architecture_guard_algorithms.py' = @('7313C14A8D26C8E736EBCDBD02272F6BCD4B2AB2B87775D36E5ECA6A56EC9FA3', '6F87404093FA11E847232B5862B2404833A03A662D203B859CE2445620552688')
    'backend/authoring/services/core.py' = @('A289001AEE3249489E2E1D6911FCB99E6CBA902DFE5A398577ED297E5BC6B12B', 'E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855')
    'backend/authoring/tests/test_authoring_api.py' = @('957B9B00E67100976AD40E19EF6BF740F37B2EA687A9B170E357B706B52DFCB7', 'E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855')
}
foreach ($entry in $shared.GetEnumerator()) {
    if ((Get-FileHash -Algorithm SHA256 -LiteralPath $entry.Key).Hash -ne $entry.Value[0]) { $failures.Add("Shared file hash mismatch: $($entry.Key)") }
    $diff = git diff -- $entry.Key | Out-String
    $bytes = [Text.Encoding]::UTF8.GetBytes($diff)
    $sha = [Security.Cryptography.SHA256]::Create()
    $diffHash = [BitConverter]::ToString($sha.ComputeHash($bytes)).Replace('-', '')
    if ($diffHash -ne $entry.Value[1]) { $failures.Add("Shared diff hash mismatch: $($entry.Key)") }
}
if ($failures.Count) { throw ($failures -join [Environment]::NewLine) }

# C:\Users\Joana\Documents\GIT-IT\frontend
npm test -- src/features/authoring/pages/ContentEditorPage.test.tsx src/features/authoring/utils/authoringModel.test.ts src/features/authoring/utils/chapterIndex.test.ts --reporter=dot
npm exec eslint -- src/features/authoring/pages/ContentEditorPage.tsx src/features/authoring/pages/ContentEditorPage.test.tsx src/features/authoring/hooks/useContentEditorController.ts src/features/authoring/components/content-editor
npm run build
npm run lint
npm run lint:dead
npm run api:check
npm run api:usage-check
npm run api:type-adoption-check
npm run ui:typography-check

# C:\Users\Joana\Documents\GIT-IT
python -m pytest backend/authoring/tests/test_authoring_api.py -q
python -m pytest backend/common/tests/test_architecture_guard_algorithms.py -q
python scripts/checks/check_architecture_boundaries.py
python scripts/check_quality_gates.py
git diff --check
git diff --exit-code -- frontend/src/shared/api/generated
git diff --exit-code -- frontend/src/app/router.tsx frontend/src/features/authoring/api/authoringApi.ts frontend/src/features/admin/api/adminApi.ts frontend/src/features/authoring/utils/authoringModel.ts frontend/src/features/authoring/utils/authoring-model frontend/src/features/authoring/utils/authoringModel.test.ts frontend/src/features/authoring/utils/chapterIndex.ts frontend/src/features/authoring/utils/chapterIndex.test.ts frontend/src/features/authoring/types.ts frontend/src/shared/api/queryKeys.ts frontend/src/shared/api/generated frontend/src/features/authoring/components/BattleStageEditor.tsx frontend/src/features/authoring/components/LevelsEditor.tsx frontend/src/features/authoring/components/ChapterLessonPagesEditor.tsx frontend/src/features/authoring/components/TagsField.tsx frontend/src/features/authoring/components/levels-editor frontend/src/features/home frontend/src/styles/features/authoring/battle-stage-editor.css
```

Run the full-suite diagnostic from `frontend` in a hidden, separately recorded process so only its process tree can be terminated:

```powershell
$suiteLog = Join-Path ([IO.Path]::GetTempPath()) ("git-it-vitest-{0}.log" -f [guid]::NewGuid())
$suiteErr = "$suiteLog.err"
$suite = Start-Process npm.cmd -ArgumentList @('test', '--', '--reporter=dot') -WorkingDirectory (Get-Location) -WindowStyle Hidden -RedirectStandardOutput $suiteLog -RedirectStandardError $suiteErr -PassThru
if (-not $suite.WaitForExit(300000)) {
    taskkill.exe /PID $suite.Id /T /F | Out-Null
    "TIMED_OUT_BASELINE_MATCH: full Vitest suite exceeded 300 seconds; recorded PID tree terminated"
} elseif ($suite.ExitCode -ne 0) {
    throw "Full Vitest suite completed with exit code $($suite.ExitCode)."
} else {
    "Full Vitest suite passed."
}
```

After capturing the evidence, recompute every out-of-scope SHA-256 listed in `PRE_SLICE_BASELINE.md`, confirm deleted paths remain deleted, and use `rg` to assert every recorded pre-existing shared-guard symbol and test remains. Any mismatch is a blocker and must be resolved without restoring or rewriting user work wholesale.

## Baseline evidence

- `ContentEditorPage.tsx`: 398 lines; imports both API clients, React Query, auth, router workflow, query keys, model utilities, toast, and the unsaved guard.
- Focused authoring utilities: 2 files / 8 tests passed in 5.40s.
- `npm run build`: passed; baseline content-editor chunk 35.63 kB / 9.46 kB gzip.
- `npm run lint`: passed.
- Full `npm test -- --reporter=dot`: bounded pre-cutover diagnostic timed out after 304 seconds without output. This condition is recorded rather than misreported as a passing baseline.

## Follow-up slices (not authorized by this plan)

Next candidate: decompose `HomeHubView.tsx` into URL-tab composition, profile/rank panels, and sprite/showcase choreography using its real `/design-preview/home` browser route. Later candidates are `ProblemsEditor.tsx`, home stats, and large but cohesive battle/runtime modules, each with its own ownership map and evidence gate.
