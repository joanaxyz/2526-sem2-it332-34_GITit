# First-Game Tutorial Overlays Implementation Plan

**Intent:** Help a new player understand the real gameplay loop quickly when they first enter an Adventure and when they first enter a Challenge.
**Current Behavior:** Challenge has a one-time workspace map that displays five callouts simultaneously, without sequential controls or a Skip action. Adventure has no first-entry tour. A single legacy local-storage key also lets one mode suppress the other.
**Expected Outcome:** Adventure and Challenge each auto-open one concise, independent, interactive tour. One target is spotlighted at a time with a connector arrow, short contextual copy, clickable progress, Back, Next/Finish, and an obvious Skip action. Missing optional Challenge panels are skipped safely. Challenge-facing copy uses plain product language (`Scenario`, `Objective`, `Required values`) and the terminal exposes an explicit paste affordance alongside the existing copyable required values.
**Target-Perspective Output:** A first-time player enters an actual Adventure, follows four callouts from objective to battle/project state to the command input, dismisses or completes the guide, and can immediately issue a real Git command. On their first Challenge, a separate tour explains the objective, live repository DAG, optional target DAG, command input, and optional feedback. Returning to either mode does not reopen its completed or skipped tour.
**Truth Owner:** Frontend presentation state. `shared/level/utils/levelTour.ts` owns user- and mode-scoped dismissal; the shared tour component owns active-step behavior and positioning; Adventure and Challenge wrappers own their mode-specific copy and targets.
**Contract Boundary:** Mode wrappers provide ordered `WorkspaceTourStep[]` definitions (`selector`, icon, title, concise body, preferred placement, optional flag), a visible `label`, and an optional `finishLabel` to the shared overlay. `finishLabel` defaults to `Start playing`; Challenge passes `Start challenge`. Consumers provide one close callback; both Finish and Skip persist the same mode-scoped seen state. `LevelStoryCard` accepts additive `labels?: Partial<LevelStoryCardLabels>` and `showDetailLabels?: boolean`; defaults preserve Adventure's `Story`, `Task`, `Copy details`, hidden detail-label presentation, and existing details aria-label. Challenge overrides them with `Scenario`, `Objective`, `Required values`, visible detail labels, and a Challenge-specific details aria-label.
**Cutover:** Replace the existing Challenge all-at-once renderer with a thin wrapper over the shared sequential overlay. Introduce versioned `v2` Adventure and Challenge storage keys. The legacy unscoped key is demoted and no longer controls the redesigned tour, so the new experience appears once even for users who saw the old map.
**Displaced Path:** The simultaneous five-card rendering and its duplicated geometry logic in `ChallengeWorkspaceTour.tsx` are removed. The existing Challenge mount stays in place to avoid disturbing concurrent workspace work.
**Value Density:** Four Adventure steps and four-to-five Challenge steps teach the smallest useful gameplay loop: read the goal, inspect state, act in the terminal, observe feedback.
**Acceptance Evidence:** An exact locked pre-slice manifest, targeted interaction and persistence tests, production build, desktop and `390x844` browser captures from real Adventure and Challenge workspaces, real command execution while the tour is open, keyboard/console checks, and a final byte-for-byte worktree audit.
**Evidence Lane:** Unit tests prove state/interaction contracts; native browser replay proves the visual target, connector, controls, responsive placement, and first-entry behavior from a player perspective.
**Kill Criteria:** Only one generic tour engine remains. Challenge-specific geometry/rendering is deleted, no second persistence system is introduced, no backend onboarding field/migration is added, and no tour reopens after Skip or Finish for that user and mode.
**Architecture Slice:** `levelTour.ts` -> mode wrapper -> shared portal overlay -> existing stable workspace targets. Adventure mounts after run data exists in `AdventureSession`; Challenge retains its existing mount through a compatibility wrapper.
**Plan Review Gate:** Requires PRE review before execution.

## Assumptions

- The primary “aha” moment is understanding that a real Git command changes repository state and produces visible battle/DAG feedback.
- Users range from beginners to experienced learners, so the tour is brief, optional, non-patronizing, and skippable.
- Browser-local, user-scoped persistence is appropriate for presentation-only onboarding. Cross-device synchronization is a non-goal.
- In Challenge payloads, `scenario_context.story` is scenario/setup text, `scenario_context.task` is the actionable repository objective, and `scenario_context.details` is the list of exact copyable literals. The UI must name those roles directly rather than exposing the backend field names.
- Clipboard paste inserts text at the current terminal caret and never auto-submits a command. Native Ctrl/Cmd+V remains available.

## Architecture Map

### Files to create

- `frontend/src/shared/level/components/GameplayWorkspaceTour.tsx`
- `frontend/src/shared/level/components/GameplayWorkspaceTour.test.tsx`
- `frontend/src/features/adventures/components/AdventureWorkspaceTour.tsx`
- `frontend/src/features/challenges/components/ChallengeWorkspaceTour.test.tsx`
- `frontend/src/styles/features/battle/workspace-tour.css`
- `docs/goals/first-game-tutorial-overlays/EVIDENCE.md` during verification
- Browser screenshots under `docs/goals/first-game-tutorial-overlays/`

### Files to modify

- `frontend/src/features/challenges/components/ChallengeWorkspaceTour.tsx`
- `frontend/src/features/adventures/components/AdventureSession.tsx`
- `frontend/src/features/adventures/components/AdventureWorkspaceMain.tsx`
- `frontend/src/features/adventures/components/AdventureSession.test.tsx`
- `frontend/src/shared/level/utils/levelTour.ts`
- `frontend/src/shared/level/utils/levelTour.test.ts`
- `frontend/src/styles/features/battle.css`
- `frontend/src/shared/level/components/LevelContextPanel.tsx`
- `frontend/src/features/challenges/components/ChallengeContextPanel.tsx`
- `frontend/src/shared/level/components/CommandInput.tsx`
- `frontend/src/styles/features/battle/context-panel-sections.css`
- `frontend/src/styles/features/battle/workspace-terminal.css`

### Additional files to create for the refinement

- `frontend/src/shared/level/components/LevelContextPanel.labels.test.tsx`
- `frontend/src/shared/level/components/CommandInput.test.tsx`
- `docs/goals/first-game-tutorial-overlays/REFINEMENT_BASELINE.md`

### Files to avoid

- Preserve 61 of the 63 pre-existing dirty entries byte-for-byte. The user-directed refinement explicitly authorizes narrow additive edits in the already-dirty `ChallengeContextPanel.tsx` and `LevelContextPanel.tsx`; capture their complete pre-refinement bytes and SHA-256 values before editing, then audit preimage-to-final patches as only the approved additive label API/overrides. No other pre-existing dirty path is opened.
- Especially avoid the dirty `ChallengeWorkspace.tsx`, `ChallengeWorkspacePanels.tsx`, `AdventureBattlePanel.tsx`, `BattleStage.tsx`, `LiveDagPanel.tsx`, `router.tsx`, and dirty battle workspace styles.
- Avoid backend models, APIs, schemas, migrations, generated contracts, and deployment YAML; this feature has no server or production-config requirement.

### Source of truth

- `levelTour.ts`: versioned seen state keyed by authenticated user (or guest) and `adventure | challenge`.
- Mode wrapper step arrays: copy, order, target selectors, optionality, and preferred placement.
- Shared tour props: the visible mode label and final-action label; filtered visible steps own clickable progress state.
- `LevelStoryCard` defaults own shared/Adventure terminology; `ChallengeContextPanel` owns its plain-language label overrides and `Mode: Challenge` fact.
- Existing rendered workspace DOM: target geometry.

### Read path

1. Adventure or Challenge run finishes loading.
2. Consumer reads `hasSeenLevelTour(userId, mode)`.
3. If unseen, mode wrapper supplies its step definitions.
4. Shared overlay resolves visible targets and presents the first available step.

### Write path

1. Player chooses Skip or reaches Finish.
2. Consumer calls `markLevelTourSeen(userId, mode)` and closes the overlay immediately.
3. Storage failures never crash gameplay; in-memory dismissed state prevents reopening during the current mount.

### Integration points

- Adventure: existing `AdventureSession` loaded-state render and stable Adventure workspace anchors.
- Challenge: existing `ChallengeWorkspaceTour` mount and existing `data-tour-target` anchors.
- Styling: `battle.css` imports a dedicated semantic stylesheet using current tokens and z-index scale.

### Migration/cutover

- New keys: `git-it-practice-workspace-tour:v2:<user>:adventure` and `...:challenge`.
- Old unscoped storage remains harmless but is no longer read.
- Existing Challenge component name remains as a compatibility wrapper, preventing changes to its dirty parent.

### Acceptance evidence gate

- Do not call the feature complete without visible Adventure and Challenge browser evidence.
- A build or screenshot alone is insufficient: tests must also prove mode independence, one-card sequencing, Skip/Finish persistence, missing optional targets, terminal-safe keyboard dismissal/navigation, and the exact preservation baseline.

## Task 0 — Lock the pre-slice worktree

**Allowed scope:** Read-only inspection plus `PRE_SLICE_BASELINE.md`.

**Expected output:** Record branch, HEAD, staged-entry count, protected-entry count, and the immutable manifest SHA-256 before implementation. Reuse `docs/goals/improve-command-latency/PRE_WORKTREE_MANIFEST.json`, which already contains porcelain status, staged/unstaged position, deleted-path markers, and SHA-256 for the same 63 entries; confirm every entry still matches before proceeding.

**Verification:** The current comparison must report 63 protected entries, zero mismatches, and zero staged entries. Task 5 repeats the identical comparison against the same JSON bytes.

**Acceptance evidence:** `PRE_SLICE_BASELINE.md` records the verified counts and manifest hash.

**Parallel:** No; must finish before all implementation tasks.

## Task 1 — Shared persistence contract

**Allowed scope:** `levelTour.ts`, `levelTour.test.ts`.

**Expected output:** Add an exported `LevelTourMode` and optional mode parameter defaulting to `challenge` for backward compatibility. Use versioned, mode-scoped keys and preserve safe storage failure behavior.

**Verification:**

```powershell
cd frontend
npx vitest run src/shared/level/utils/levelTour.test.ts
```

**Acceptance evidence:** Tests show Adventure and Challenge are independent, user IDs are isolated, default calls map to Challenge, and blocked storage does not throw.

**Parallel:** Yes; disjoint from Task 2 until integration.

## Task 2 — Shared sequential spotlight engine

**Allowed scope:** New shared component/test and new tour stylesheet; `battle.css` import.

**Expected output:** A portal-based overlay that resolves visible steps, displays exactly one card, spotlights the live target, draws a directional connector arrow, supports Back/Next/Finish/Skip plus Alt+ArrowLeft/Alt+ArrowRight/Escape, keeps the target interactive, stays in the viewport, remeasures on DOM/resize/scroll changes, and restores prior focus on close. On step changes, an offscreen target scrolls into view with fixed-header clearance, the overlay remeasures after scrolling, and the narrow-screen card falls back below or above the target without covering it. Motion uses the existing 150–250ms easing and has a reduced-motion fallback.

**Verification:**

```powershell
cd frontend
npx vitest run src/shared/level/components/GameplayWorkspaceTour.test.tsx
```

**Acceptance evidence:** Tests prove one active card, boundary behavior, optional-target filtering, close reasons, Alt+Arrow keyboard control, plain caret arrows remaining untouched inside inputs/contenteditable controls, post-scroll remeasurement, and target highlighting cleanup.

**Parallel:** Yes; disjoint from Task 1 until integration.

## Task 3 — Mode-specific tours and mounts

**Allowed scope:** Adventure wrapper/session/workspace/test, the existing Challenge wrapper, and a focused Challenge wrapper test only.

**Expected output:**

- Adventure sequence: quest objective/context -> battle state -> project files -> exact command input.
- Challenge sequence: quest objective/context -> live DAG -> optional target DAG -> exact command input -> optional feedback.
- Adventure opens once using the Adventure key after run data is ready.
- Existing Challenge mount continues to compile unchanged through the wrapper and defaults to the Challenge key.
- Skip and Finish both mark the relevant mode seen.

**Verification:**

```powershell
cd frontend
npx vitest run src/features/adventures/components/AdventureSession.test.tsx src/shared/level/components/GameplayWorkspaceTour.test.tsx src/shared/level/utils/levelTour.test.ts
npx vitest run src/features/challenges/components/ChallengeWorkspaceTour.test.tsx
```

**Acceptance evidence:** Adventure integration shows first entry opens, dismissal persists, and the separate Challenge key remains unseen. A clean `ChallengeWorkspaceTour.test.tsx` validates ordered selectors, optional Target DAG/Feedback handling, one-card rendering, and close forwarding without touching its dirty parent.

**Parallel:** No; consumes Tasks 1 and 2.

## Task 3B — Challenge terminology and copy/paste refinement

**Allowed scope:** `ChallengeContextPanel.tsx`, additive label support in `LevelContextPanel.tsx` plus a new clean focused test file, `CommandInput.tsx` plus a new clean focused test, clean context/terminal styles, and the owned tour wrappers/engine/style.

**Expected output:**

- Challenge labels read `Scenario`, `Objective`, and `Required values`; `Mode: Challenge` replaces `Level Type: Challenge Trial`.
- Required-value labels are visible in Challenge mode and retain one-click copy buttons.
- The shared terminal prompt exposes a compact `Paste` action that inserts normalized single-line clipboard text at the caret, never submits, returns focus to the prompt, and announces success or failure accessibly.
- The tour card presents `label` visibly, uses clickable step progress across the filtered live step list, and renders `finishLabel` on the last step. Challenge passes `Start challenge`; omitted props preserve the existing finish default.
- Existing Adventure wording and copy-detail defaults remain compatible unless deliberately improved by its own wrapper copy.

**Verification:**

```powershell
cd frontend
npx vitest run src/shared/level/components/LevelContextPanel.labels.test.tsx src/shared/level/components/CommandInput.test.tsx src/shared/level/components/GameplayWorkspaceTour.test.tsx src/features/challenges/components/ChallengeWorkspaceTour.test.tsx
```

**Acceptance evidence:** Tests prove progress buttons jump directly across the filtered visible-step list with active accessible state; paste inserts at or replaces the current selection, normalizes multiline text, restores input focus, announces success/failure, and never calls `onSubmit`; Challenge label overrides render while shared/Adventure defaults remain unchanged. A real Challenge screenshot shows the plain labels and visible copy affordances; browser replay clicks progress, shows `Start challenge`, then copies and pastes without submission.

**Parallel:** No; this is a user-directed refinement of Tasks 2 and 3.

## Task 4 — Production and accessibility verification

**Allowed scope:** Verification only, plus surgical fixes inside the owned files above.

**Expected output:** Formatting/lint cleanliness, a successful production build, no accidental generated artifacts, and responsive/keyboard-safe overlay behavior. Visual acceptance requires one neon-blue signal accent, tonal night-sky depth, an earned target glow, a clear directional connector, one true floating plaque, compact copy, visible focus states, contrast-safe text, purposeful 150–250ms transitions, and a reduced-motion alternative.

**Verification:**

```powershell
cd frontend
npm run build
npx eslint src/shared/level/components/GameplayWorkspaceTour.tsx src/features/adventures/components/AdventureWorkspaceTour.tsx src/features/challenges/components/ChallengeWorkspaceTour.tsx src/features/adventures/components/AdventureSession.tsx src/shared/level/utils/levelTour.ts
git diff --check -- frontend/src docs/goals/first-game-tutorial-overlays
```

**Acceptance evidence:** Build passes; focus-visible controls, Escape, Back/Next, Skip, reduced motion, and narrow-layout containment are verified.

**Parallel:** No.

## Task 5 — Target-perspective browser evidence and preservation audit

**Allowed scope:** Real local Adventure/Challenge replay, screenshot artifacts, `EVIDENCE.md`, and cleanup of only disposable test state.

**Expected output:** Desktop Adventure and Challenge screenshots plus a complete `390x844` traversal showing each available step, the active target, directional arrow, progress, Next, and Skip without target/card overlap. Confirm target interaction remains possible and that returning to each mode does not reopen its tour.

**Replay recipe:**

1. Root executor starts Django from `backend` with `DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost`, `DJANGO_CORS_ALLOWED_ORIGINS=http://127.0.0.1:5178`, and `DJANGO_CSRF_TRUSTED_ORIGINS=http://127.0.0.1:5178`, then runs `python manage.py runserver 127.0.0.1:8005 --noreload`.
2. Start Vite from `frontend` with `VITE_API_BASE_URL=http://127.0.0.1:8005/api` using `npm run dev -- --host 127.0.0.1 --port 5178 --strictPort`.
3. Create a disposable authenticated player and deterministic two-command Adventure and Challenge fixtures through the local Django ORM. The first known valid state-changing command must update battle/DAG state without completing the run; record all created IDs for cleanup.
4. In the browser, clear only `git-it-practice-workspace-tour:v2:<user>:adventure` and `...:challenge`.
5. Visit the real `/adventure-runs/<id>` route. Traverse all steps by pointer, then repeat at `390x844`; at the command-input step, focus the real input, prove plain ArrowLeft/ArrowRight still move the caret, enter only the first valid command, and record the resulting battle/state feedback while the run remains active.
6. Visit the real `/challenge-runs/<id>` route. Traverse all available steps by keyboard and pointer; at the command-input step execute only the first valid command and record the resulting DAG/feedback change while the run remains active.
7. Revisit each still-active route (or create a second active run of the same mode) and confirm its tour does not reopen, proving persistence independently of completion/outcome rendering. Check browser console and failed requests after each flow.
8. Capture screenshots and request/console notes in `EVIDENCE.md`. An independent UI reviewer inspects every retained screenshot against the visual contract before completion.
9. Delete the disposable user, runs, curriculum fixtures, browser profile, temporary launchers/logs, and stop both listeners.

**Verification:** Compare 61 untouched entries against the exact locked JSON manifest byte-for-byte (porcelain status, staged/unstaged position, deleted marker, and SHA-256). For `ChallengeContextPanel.tsx` and `LevelContextPanel.tsx`, compare their captured full preimages to final bytes and verify the only deltas are the approved additive Challenge label API/overrides. Confirm the manifest file itself still has SHA-256 `E6691816FDA80C8F238E32C669557E218FD7D9490A01F98D36AB9FC5767C37EA`. Only planned clean/new files may differ beyond their original state.

**Acceptance evidence:** Screenshots and notes are reviewed visually; no pre-existing user work is changed or staged.

**Parallel:** No.
