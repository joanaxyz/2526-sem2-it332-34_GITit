# Impeccable session — Tower page & Tower editor

**Date:** 2026-06-16 · **Branch:** `chore/codebase-improvements`
**Surfaces:**
- Tower page — [TowerMapPage.tsx](frontend/src/features/tower-map/pages/TowerMapPage.tsx) (`/tower`)
- Tower editor — [InTowerEditor.tsx](frontend/src/features/tower-map/editor/InTowerEditor.tsx) (`/tower?mode=edit`; the old [TowerEditorPage.tsx](frontend/src/features/tower-designs/pages/TowerEditorPage.tsx) is now just a redirect)
- Canvas/pieces — [EditorStorey.tsx](frontend/src/features/tower-designs/components/EditorStorey.tsx), [TowerStoreySection.tsx](frontend/src/features/tower-map/components/TowerStoreySection.tsx), [PieceArt.tsx](frontend/src/features/tower-map/components/PieceArt.tsx)
- Styling — [tower-map.css](frontend/src/styles/features/tower-map.css), [tower-editor.css](frontend/src/styles/features/tower-editor.css)

---

## 1. Critique (`/impeccable critique`)

**Snapshot:** `.impeccable/critique/2026-06-16T06-59-47Z__frontend-src-features-tower-map.md`
**Trend (slug `frontend-src-features-tower-map`):** 26 — first run, no prior trend.

### Design Health Score

| # | Heuristic | Score | Key Issue |
|---|-----------|-------|-----------|
| 1 | Visibility of System Status | 3 | Skeletons, dirty-count apply bar, zoom %, validation chip — but "what's saved" is muddied by the mixed save model |
| 2 | Match System / Real World | 3 | Strong in-fiction vocab + plain Git; fork/private-edit wording can still puzzle a beginner |
| 3 | User Control and Freedom | 2 | Undo/redo/Esc/Discard exist, but immediate deletes sit outside undo and exit doesn't guard staged edits |
| 4 | Consistency and Standards | 2 | Split save model (instant vs staged); Georgia serif CTA + amber-in-chrome deviate from the documented system |
| 5 | Error Prevention | 2 | Backspace/trash deletes a piece server-side instantly, no confirm, no exit guard |
| 6 | Recognition Rather Than Recall | 3 | Inspector teaches well; tower-piece clickability only signalled on hover |
| 7 | Flexibility and Efficiency | 3 | Editor is genuinely efficient (shortcuts, drag-or-click, batch apply); tower page has no shortcuts |
| 8 | Aesthetic and Minimalist Design | 3 | Beautiful and on-brand, but the page floats 5–6 fixed clusters and the command bar is dense |
| 9 | Error Recovery | 3 | Parsed API-error toasts + click-to-focus validation issues are excellent |
| 10 | Help and Documentation | 2 | Inline hints + field guide, but no first-run for the authoring flow, no in-tool help |
| **Total** | | **26/40** | **Acceptable — visually exceptional, dragged down by control/consistency/error-prevention gaps** |

### Anti-patterns verdict
**Not AI slop at the markup level — the opposite.** Living time-aware sky, progressive storey mounting + build-zone sentinel, blueprint skeleton loaders, a real staged-edit design tool, a named semantic z-index scale. Deterministic detector (`detect.mjs` over `tower-map/` + `tower-designs/`) returned `[]` (exit 0). Browser overlay NOT run — both surfaces are auth-gated SPA routes needing the Django backend + a seeded DB; findings are from source review + the deterministic scan.

> Note: the user later disagreed specifically about the **editor** (see §3) — calling its current chrome "AI slop" with too much wasted space and an everything-floats-as-overlay model. That is a layout/IA judgment the markup detector can't see, and it's now the active work.

### What's working
1. The world genuinely is the interface — selection assembles overview + preview + one action around the spire.
2. The editor's state architecture is professional-grade — staged edits, Apply/Discard, dirty count, undo/redo, optimistic refetch, semantic z-scale.
3. Motion discipline — `prefers-reduced-motion` fallbacks everywhere; clock defaults to paused under reduced motion.

### Priority issues
- **[P1] Destructive deletes are immediate, unguarded, outside undo (editor).** Backspace/Delete or trash fires `deletePiece`/`deleteArtifact` straight to the server; Ctrl+Z (staged) can't restore; no confirm. Contradicts the product's "consequence-safe" promise. → `harden`
- **[P1] Fixed side docks overlap the spire at laptop widths (tower page).** `.tower-storey-dock`/`.tower-artifact-dock` are `position:fixed`, `min-width:15.5rem`, but the gutter beside the 42rem column shrinks below that ≤~1230px; nothing repositions them until 640px. → `adapt`
- **[P1] Mixed save model erodes "what's saved" (editor).** Swap/transform/move stage; add/delete piece, place/remove artifact, add storey, rename persist instantly. The "N unsaved changes" bar counts only the staged ones. → `harden`
- **[P2] Chrome competes on the tower page.** Official view floats SkyClock + TowerControls + StoreyOverview dock + ArtifactOverview dock + action button + zoom — 5–6 fixed clusters with brittle hardcoded offsets. → `layout`
- **[P2] Off-system flourishes vs documented system.** `.tower-action-button` uses Georgia serif (only serif in an Inter/JetBrains-Mono system); the editor uses amber (`#f3d27a`) for warnings, which DESIGN.md's "One Warm Note Rule" reserves for the world and prohibits in UI chrome. → `colorize` / `typeset`

### Persona red flags
- **Jordan (first-timer):** spire ringed by floating instruments; nothing at rest says "click a door" (stage titles hover-only). Authoring flow has no first-run.
- **Riley (stress tester):** Backspace deletes a piece server-side, Ctrl+Z won't restore; Exit drops staged edits silently; 1100px width → docks overlap.
- **Anxious CS student (project persona):** the immediate unguarded delete + ambiguous save state is exactly the "did I break it?" anxiety the product exists to remove.

### Minor observations
- Tower-piece clickability is hover-only; add a resting affordance.
- Pan is pointer-only on both canvases (no keyboard pan); zoom slider is labelled.
- Gizmo handles are 12px — fine for mouse, sub-44px for touch (desktop-first, acceptable).
- Eyebrows ("Tower editor", "Library", "Piece") are label→value pairs, not decorative kickers — defensible.
- StoreyOverview filler copy: "Storey overview for this Command Adventure and Challenges set." narrates itself — cut/replace.
- `.tower-action-button` leans on several `!important`.

### Questions to consider
- Should the editor be as consequence-safe as the rest of the product (nothing hits the server until Apply, full undo)?
- Does the official view need the storey-overview dock always visible, or only on selection?
- Is the serif CTA + amber warnings a deliberate identity choice to write into DESIGN.md, or drift to correct?

### User's answers to the critique
- **Priority first:** Editor safety.
- **Save model:** Unify behind Apply — nothing touches the server until Apply, with full undo.
- **Scope:** Everything (P1s + P2s + minors).

---

## 2. Follow-up message — drop-target cue (DONE)

> "There is no indicator where the artifact is being dropped — section or landing? Some visual cue, an outline of the SVG itself that follows the shape of the current section/landing it will drop to."

**Implemented (CSS-only, [tower-editor.css](frontend/src/styles/features/tower-editor.css#L1606)):** replaced the rectangular `outline` + `box-shadow` drop cue with a layered neon `drop-shadow` filter on the piece's inline `<svg>` (`.piece-svg`). The glow follows the SVG alpha silhouette, so it traces the exact **section** wall shape or **landing** belt shape under the cursor.
- Cyan + gentle `editor-drop-pulse` breathing = droppable here.
- Red, steady = rejected (reuses `editor-piece--reject`).
- Double-class selectors outrank `.editor-piece:hover` so no resting rectangle bleeds through; `prefers-reduced-motion` fallback drops the pulse.
- Works in both flows (native library drag + dragging an already-placed artifact) because it keys off the `editor-piece--drop`/`--reject` classes EditorStorey already toggles.
- **Open option (not yet built):** a resting "valid target" silhouette hint on all eligible pieces the instant a `placementDraft` is active (before hover).

---

## 3. Follow-up message — editor UI redesign (ACTIVE)

> "/impeccable — improve the UI of the tower editor. It looks like AI slop right now, there's too much space wasted, and I don't like how everything is an overlay."

**Diagnosis (from source):**
- Everything in the editor is `position: fixed` floating over the living sky: command bar (top blade), library rail (left), inspector rail (right), status line, apply pill (bottom-center), toast.
- The canvas reserves `padding-inline: var(--ite-rail-w) + 1.5rem` (~17.5rem each side) so the tower floats *between* the fixed rails — that reserved gutter is the wasted space, and the tower is squeezed into a narrow center band.
- The living-sky parallax behind the tool fights legibility. DESIGN.md's own principle is "Immersion outside, clarity inside" — the practice workspace uses a calm `workspace-bg`, not the living sky. The editor is a tool and should arguably follow the same rule.
- Glass-blur panels floating everywhere read as the generic "AI glassmorphism" look.

**Decisions (confirmed):** (1) **Docked app-shell** — solid toolbar / Library + Inspector as real grid columns / canvas as a true center region. (2) **Own full-screen route** `/tower/editor/:designId` (no longer `?mode=edit` on the tower page, no hub chrome). (3) **Plain dark background** `#080c14` (no living sky, no glass).

**Implemented (2026-06-16):**
- `router.tsx` — editor moved to its own `<Protected><Outlet/></Protected>` group, out of `HomeLayout`. `/tower/editor` and `/tower/editor/:designId` now render the editor page directly.
- `TowerEditorPage.tsx` — was a redirect; now the real page (resolves `:designId` or the personal design, exits to `/tower?view=mine`, has a no-tower empty state). Builds as its own 55 kB lazy chunk.
- `TowerMapPage.tsx` — all `?mode=edit` branches, `InTowerEditor`, `editDesignId`, `exitEdit` removed; the page is view-only again.
- `TowerControls.tsx` — routes to `/tower/editor/:id`; dropped the in-page edit-mode toggle (the `Eye`/return state).
- `InTowerEditor.tsx` — chrome restructured: `.ite-shell` grid (toolbar / `.ite-body` [library · canvas-col · inspector] / `.ite-footer`). Status line now sits in-flow atop the canvas; the floating apply pill became a solid footer (`No unsaved changes` ↔ dirty count + Discard/Apply).
- `tower-editor.css` — layout layer rewritten from `position: fixed` overlays + glass to solid grid columns on `#080c14`; canvas no longer reserves rail-width gutters; `--tower-*` accent vars re-declared on `.ite-shell` (the editor no longer inherits them from `.tower-page-shell`); responsive stacks to one column ≤1024px.
- **Verified:** `tsc -b` clean · `vitest` 161/161 · `vite build` succeeds. **Not** visually verified live (auth-gated route needing the Django backend + seeded DB).

---

## 4. Impeccable commands for this session

| Command | Purpose | Status |
|---|---|---|
| `/impeccable critique tower page and tower editor` | The review above (26/40, snapshot persisted) | Done |
| `/impeccable shape` → `/impeccable craft` | **Editor UI redesign** — overlay HUD → docked app-shell on its own route + dark bg | Done (2026-06-16) |
| `/impeccable harden` | Editor safety — unify ALL mutations behind Apply, full undo over deletes, confirm/Undo-toast on destructive removes, guard exit when `dirtyCount > 0` (the new solid footer is already the save surface this slots into) | Planned (user's #1, natural next) |
| `/impeccable distill` | Strip the editor's overlay complexity / wasted space to its essence | Planned (folds into the redesign) |
| `/impeccable adapt` | Tower-page dock overlap at 1024–1230px; responsive breakpoint/collapse | Planned |
| `/impeccable layout` | Tower-page chrome competition; consolidate the right-edge fixed stack; storey-overview dock only on selection | Planned |
| `/impeccable colorize` | Amber-in-chrome warnings vs DESIGN.md's One Warm Note Rule | Planned |
| `/impeccable typeset` | `.tower-action-button` Georgia serif decision | Planned |
| `/impeccable clarify` | StoreyOverview self-narrating copy | Planned |
| `/impeccable onboard` | Drop-target cue (partly done) + resting clickability affordance + authoring first-run | Partly done |
| `/impeccable polish` | Final pass once the above land (touch targets, keyboard pan, `!important` cleanup) | Planned (last) |

> Run order recommendation: **shape/craft the editor redesign → harden → adapt → layout → colorize → typeset → clarify → onboard → polish.**

---

## 5. Round-2 editor feedback (2026-06-16, after seeing the app-shell)

**Fixed this pass (verified `tsc -b` clean):**
- **Tower clipped** — `.tower-stage-grid--editor` was `place-items: center` + `overflow: hidden`, vertically centring a tall storey into a clip. Now `align-items: start; justify-items: center` (matches the pan transform's `center top` origin) so the storey reads from the roof down and pans.
- **Footer wasted space** — the idle "No unsaved changes" bar is gone; the footer now renders only when `dirtyCount > 0`, and it's slimmer (min-height 2.4rem).
- **Two Upload buttons** — removed the inspector empty-state Upload; the Library keeps the single canonical one (`onUploadClick` dropped from `PropertiesPanel`).

**Done (2026-06-16) — the "artifact model" refactor (#3 confusing library, #4 dropdown filter, #5 normal-by-default, #7 confusing content dropdown, #8 unfriendly issues, #9 remove count rules):**
- **Backend** — `services.py publish_errors` drops the `challenge_counts != 3` rule (keeps per-artifact: on-section + published content). `models.py ArtifactPlacement.clean()` drops the per-section caps (the ≤1 / ≤3 / one-kind rules — the real home of #9); keeps "interactables live on a section" + "content kind matches role". `ARTIFACT_ROLE_CHALLENGE` import pruned.
- **Placement always normal** — `onPlaceArtifact(pieceId, assetId, x, y)`; `EditorDragPayload`/`PlacementDraft` carry no role/content; the canvas never rejects a normal drop.
- **Library (StoragePanel)** — role chips, content `<select>`, Interactive-artifacts section, rule pills, and `SectionStatusLine` removed; one Artifacts grid + a **tag dropdown filter** (`.ite-tag-filter`); `StorageArtifactShelf` deleted.
- **Inspector promote flow** — `ArtifactInteractivePanel`: a selected normal artifact shows **Make interactive** (pick Kind + Content → PATCH `role`/`content_definition_id`); an interactive one shows Author link + **Make normal**. Inline section, no dialog (the open UX choice — resolved to inline).
- **Validation** — `editorValidation.ts` rewritten to per-artifact checks only (no `buildSectionStatuses`/section counts); `artifactDropRejectReason` keeps only "interactive lives on a section". The issues panel is now quiet unless content is genuinely missing/unpublished.
- **Also fixed this pass:** tower clipping, slimmer/conditional footer, duplicate Upload button.
- **Verified:** `tsc -b` clean · frontend `vitest` 161/161 · backend `pytest tower_designs/` 11/11 (two cap tests rewritten to assert the new permissive behavior) · `vite build` succeeds. **Not** visually verified live (auth-gated route + backend + seed).
