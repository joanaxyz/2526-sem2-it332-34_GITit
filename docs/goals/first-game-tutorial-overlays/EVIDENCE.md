# First-Game Tutorial Overlay Evidence

Verified on 2026-08-29 against a disposable local SQLite copy and authenticated player fixture. No production database, schema, XAML, or deployment file was changed.

## Delivered behavior

- Adventure opens a four-step first-entry tour: objective, battle results, project files, terminal.
- Challenge opens an independent five-step tour: challenge brief, live repository state, optional target state, terminal, optional contextual feedback.
- Each tour presents one real target at a time with a cyan spotlight, directional connector, clickable step progress, Back, Next, a mode-specific finish action, and Skip.
- The spotlight leaves its target interactive. Optional missing targets are filtered from the progress count and sequence.
- Completion and Skip persist independently per user and per mode under versioned browser-local keys.
- Challenge presentation labels are `Scenario`, `Objective`, `Required values`, and `Mode: Challenge`; the payload contract remains `scenario_context.story`, `.task`, and `.details`.
- Each required value retains a one-click copy action. The shared terminal now has a compact Paste action that inserts at the current selection, flattens multiline text, restores focus, and never submits automatically.

## Automated verification

From `frontend`:

```text
npx vitest run \
  src/shared/level/components/LevelContextPanel.labels.test.tsx \
  src/shared/level/components/CommandInput.test.tsx \
  src/shared/level/components/GameplayWorkspaceTour.test.tsx \
  src/features/challenges/components/ChallengeWorkspaceTour.test.tsx \
  src/shared/level/utils/levelTour.test.ts \
  src/features/adventures/components/AdventureSession.test.tsx

Test Files  6 passed (6)
Tests      25 passed (25)
```

The tests cover mode/user isolation, blocked storage, first-entry Adventure mounting, sequencing, optional-target filtering, required-target gating, replaced-target rebinding, actual card-height remeasurement, clickable progress, Skip/Finish close forwarding, safe Alt+Arrow boundaries, Escape, ordinary input caret arrows, post-scroll remeasurement, focus restoration, Challenge label overrides with shared defaults preserved, and clipboard insertion/failure behavior with no submission.

```text
npm run build
✓ 2664 modules transformed
✓ built in 48.82s

npx eslint <all tutorial/refinement TSX and test files>
exit 0

git diff --check
exit 0 (one existing generated-file line-ending warning only)
```

## Browser replay

Routes exercised:

- Adventure: `/adventure-runs/1820`
- Challenge: `/challenge-runs/1`
- Viewports: `1440x1000` and `390x844`

Desktop captures:

- [Adventure first step](adventure-desktop-refined.png)
- [Challenge first step and plain-language data labels](challenge-desktop-refined.png)

Narrow-screen captures:

- [Adventure refined mobile tour](adventure-mobile-refined.png)
- [Challenge brief without target/card overlap](challenge-mobile-refined-v3.png)
- [Challenge terminal step](challenge-mobile-copy-paste.png)
- [Challenge feedback and final Start challenge action](challenge-mobile-feedback.png)

Replay observations:

- Pointer and clickable progress navigation reached every available step; all cards and controls stayed within `390x844`.
- The final actions rendered `Start adventure` and `Start challenge`.
- Plain ArrowLeft moved the real command caret while the overlay remained open; tour navigation requires Alt+Arrow, so terminal editing is not hijacked.
- `git add README.md` executed while each tour was open. Both runs remained active and exposed their resulting state/feedback.
- Clipboard acceptance status: **implemented and automated; live copy-to-Paste retrieval unproven in this headless profile**. The Challenge required-value copy button changed to `Copied`, but the browser explicitly denied Clipboard API read permission. The Paste button remained non-submitting, and the deterministic component test proves successful insertion, multiline normalization, selection replacement, caret placement, focus restoration, and the denied-permission fallback message.
- Finishing the Challenge tour and reloading the still-active route did not reopen it. Adventure and Challenge keys were independently cleared/replayed to confirm mode isolation.
- The browser error log was empty. The console contained existing React Flow node-type memoization and router POP-navigation warnings; no tutorial-specific exception appeared.

## Challenge data contract

The Challenge panel displays:

- `scenario_context.story` as **Scenario**: concise setup/context prose.
- `scenario_context.task` as **Objective**: the required repository outcome.
- `scenario_context.details` as **Required values**: exact literals such as filenames, branch names, commit messages, remotes, or paths, each with a copy action.
- Fallbacks when variant context is absent: challenge narrative becomes Scenario and challenge summary becomes Objective.
- Mode, difficulty, stars, non-zero reward, and attempts.
- Workspace data outside the brief: current project files, live repository DAG, optional expected-state DAG, terminal history, and optional contextual feedback.

The terminology change is presentation-only; no backend payload or schema migration is required.

## Preservation audit

- Canonical manifest SHA-256: `E6691816FDA80C8F238E32C669557E218FD7D9490A01F98D36AB9FC5767C37EA` (unchanged).
- Protected pre-existing entries: 63.
- Untouched entries checked byte-for-byte and by porcelain status: 61.
- Untouched mismatches: 0.
- Staged entries: 0.
- The two authorized pre-existing dirty files were compared against complete captured preimages. Their only deltas are the additive shared label/visible-detail/tour-anchor API and the Challenge-specific plain-language overrides described in the approved plan.

## Cleanup

Completed after the final audit: the browser session, local listeners, disposable SQLite database (including WAL/SHM), clipboard-permission helper, and temporary full-file preimage directory were removed. Source and pre-existing worktree changes were not deleted or staged.
