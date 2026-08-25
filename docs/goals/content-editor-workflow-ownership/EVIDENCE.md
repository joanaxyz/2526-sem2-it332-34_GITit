# Content Editor Workflow Ownership — Slice 3 Evidence

## Outcome

The 398-line route was cut over to a 112-line composition page, a 286-line route-scoped controller, a 38-line pure draft-reconciliation module, and four HTTP-free rendering regions (64–105 lines). The real protected workflow is proven against a disposable SQLite database on dedicated non-default ports. A browser-discovered backend destination-precedence bug and review-discovered draft-race defects were fixed under reviewed plan amendments.

## Deterministic workflow evidence

- Focused page/model/index run: 3 files, 25 tests passed.
- Content-editor page suite: 17 cases passed for ordinary preset create/replace/clean baseline, staff official mode and missing-destination blocking, loaded official mode, non-staff `official=1`, edit dirty/PATCH/reset, dirty Validate/Publish blocking, clean publish adoption, same-source save/publish/create-chapter race reconciliation, full-busy chapter-creation exclusion, exact internal-replace allowance followed by external-navigation prompting, stale-save no-yank-back across mode/preset navigation, confirmed-discard and unresolved-edit source materialization, clean preset chapter creation, new/loaded lesson query suppression, and raw-disclosure/error accessibility.
- Backend destination regression: explicit `{chapter: owned_id, official_chapter: null}` passed POST 201 and PATCH 200 persistence assertions; the existing non-staff non-null official destination remained 403/no-row. Focused pair: 2 passed; full authoring API file: 9 passed.
- Architecture algorithms/runtime: 7 passed. The guard canonicalizes alias-rooted and relative static/dynamic/`require` imports—including exact barrels and static template literals—then rejects page workflow imports/markers, controller object/spread forwarding, form forwarding to narrow components, impure draft-support imports, component HTTP/controller/page imports, admin-to-authoring reverse imports, line-cap drift, and loss of destination CSS ownership.

## Draft trust and race evidence

- New draft identity includes kind, requested authored/official mode, and preset chapter; same-component navigation cannot reuse a prior preset form.
- Source transitions immediately materialize either their displayed base form or a pending edit-source sentinel into owned state; confirmed discard cannot resurrect the abandoned draft even when the destination detail is unresolved and the user navigates back before it loads.
- Validate and Publish require a clean persisted revision, preventing stale validation and accidental publication of a different server revision.
- Save and Publish carry submitted source/form snapshots. Successful same-source responses adopt the server baseline while retaining any later local edit as visible dirty work.
- Create-chapter merges only its new chapter ID into the latest same-source form, or the submitted materialized form after a clean preset navigation, preserving current metadata and destination identity in both cases. The action is disabled for the controller's full busy state and the callback independently rejects concurrent invocation.
- Dirty or pending writes keep pathname/search/hash SPA transitions and `beforeunload` protection active. The guard allows only the controller's exact successful replacement location; that internal replace prompts zero times, and the next hash-only user navigation prompts normally.
- Every mutation completion compares its submitted source with the current route source. The deferred stale new-save test confirms that a user-confirmed move to a different mode/preset remains in place, retains its correct clean form, receives no stale toast/error, and is never navigated back.

## Disposable real-path session

Isolation:

- Temporary session child was created under the OS temp directory, outside both workspace roots.
- Backend `51047` and frontend `51048` were checked free and used instead of `8000`/`5173`.
- Vite used explicit `VITE_API_BASE_URL=http://127.0.0.1:51047/api`; Django used the session SQLite file plus the matching loopback CORS/CSRF origin.
- Both spawned PIDs and both readiness endpoints were checked before login.
- Unique disposable identities rendered in the authenticated Home UI before any content mutation. Auth network evidence was `POST http://127.0.0.1:51047/api/auth/login/` → 200.

Normal-author path:

- Opened `/level-editor/new/adventure?chapter=1`; the visible `Chapter` combobox selected `Codex Authored Chapter`.
- Save network: `POST /api/authoring/content-definitions/` → 201, followed by `GET /api/authoring/content-definitions/1/` → 200.
- Route replaced to `/level-editor/1`; visible status became `Saved`.
- Reload retained `/level-editor/1`, title `New adventure`, selected authored chapter, and `Saved` status.
- Changed title to `Unsaved browser draft`, attempted Home navigation, received the exact unsaved-authoring confirm, dismissed it, and remained on `/level-editor/1` with the local draft value intact.

Staff official path:

- Opened `/level-editor/new/adventure?official=1&chapter=1`; the visible `Official chapter` combobox selected `Codex Official Chapter`, with no create-chapter action.
- Save network: `POST /api/authoring/content-definitions/` → 201; route replaced to `/level-editor/2?official=1`.
- Validate network: `POST /api/authoring/content-definitions/2/validate/` → 200; visible feedback was `Validation passed.`

Persisted disposable rows:

| ID | Identity | Authored chapter | Official chapter | Status | Validation errors |
|---:|---|---:|---:|---|---|
| 1 | unique normal author | 1 | null | draft | `[]` |
| 2 | unique staff author | null | 1 | testable | `[]` |

Exactly two content definitions existed. The earlier pre-fix 403 attempt created no row.

## Accessibility and responsive evidence

- Destination select exposes `aria-labelledby="content-editor-destination-label"`.
- Save state exposes `role="status"` and announced `Unsaved changes` in both captured states.
- Raw disclosure moved from `aria-expanded=false` to `true`, controlled `content-editor-generated-json`, and the controlled element existed while expanded.
- Keyboard traversal from destination was: labeled `SELECT` → `New chapter` button → `Edit chapter` link → metadata title `INPUT`.
- Desktop 1440×900: document width 1430/viewport 1440; destination width 859/859; no horizontal overflow.
- Mobile 390×844: document width 380/viewport 390; destination width 343/343; actions width 198/198; no horizontal overflow.
- Browser error collections were empty. Console contained only Vite connection and React DevTools development notices.

Durable screenshots:

- `evidence/content-editor-desktop.png` — 170,634 bytes, SHA-256 `996767C8DC6D127C9FAB5E19F61341490065EC063C7ADFFFD6F78B877153C00B`.
- `evidence/content-editor-mobile.png` — 89,213 bytes, SHA-256 `B403715D8C51FEF6F45F9B3B58ED2ACF4E8747EF6F7DA1EF85B974B8085BC29D`.

## Browser-discovered contract correction

The first normal-author real POST returned 403 with `Only staff can place content in the official curriculum.` The frontend's existing contract intentionally sends mutually exclusive fields explicitly (`chapter: id`, `official_chapter: null`). Backend create/update previously prioritized presence of the official key, checked staff before handling null, and discarded the authored destination. Under a PRE-aligned amendment, both write paths now use one destination-choice helper: a non-null authored ID wins and clears official; otherwise an explicit official value resolves and clears authored; null official returns before staff enforcement; explicit null authored alone clears both. Both-non-null validation and non-null official staff enforcement remain unchanged.

## Supporting gates

- Scoped ESLint: passed.
- Full frontend ESLint: passed.
- Dead-code (`knip`): passed.
- Production build: passed.
- API contract current, frontend API usage, and generated type adoption: passed.
- UI typography gate reports three pre-existing `text-[10px]` violations in untouched Admin Curriculum files. Each line is identical at `HEAD`; this slice did not modify those protected paths.

## Terminal integrity and full-suite evidence

- Final full Vitest run completed inside the 300-second ceiling: 64 files and 446 tests passed in 206.43 seconds with exit code 0.
- Focused final rerun after the trust amendment: 3 files and 25 tests passed.
- Production TypeScript/Vite build passed; final content-editor chunk was 39.11 kB / 10.44 kB gzip.
- Full ESLint, scoped content-editor ESLint, and `knip` passed on the final files.
- Authoring API tests passed (9); architecture algorithm tests passed (7); the live architecture checker passed.
- All fast repository quality gates passed, including CSS architecture, 2,056 generated curriculum target cases, API-contract checks, documentation currency, CI manifest, and artifact hygiene.
- `git diff --check` passed. Generated API files and every planned file-to-avoid path had an empty diff.
- Every out-of-scope Slice 1/2 file/deletion state matched `PRE_SLICE_BASELINE.md`; every recorded shared admin-console guard/test symbol remained present.
- Terminal ownership metrics: page 112 lines, controller 286 lines, pure draft support 38 lines, rendering components 64–105 lines. The page has zero displaced workflow imports or definitions.
- The disposable browser session was fully cleaned: both recorded server PID trees were stopped, its database/credentials/logs were deleted, and the verified session directory no longer exists.
