# Plan — Unify the Adventure & Challenge command terminal (latency + reuse)

## Problem (what the user actually hit)

The `TerminalPanel`/`CommandInput` **components are already shared**. What diverged is the
**data flow that feeds them**, and that single divergence causes *both* symptoms the user noticed:

| | Challenge (good) | Adventure (slow/divergent) |
|---|---|---|
| Source of `lines` | derived from `run.steps` in the react-query cache (`terminalLinesFromRun`) | ephemeral component `useState` in `AdventureSession` |
| On submit | `onMutate` inserts an **optimistic "Pending" step** → instant `cmd` + `...` | echoes the input line only, **waits for the round-trip** for output |
| Persistence | survives refresh (cache/bootstrap) | lost on refresh |
| Backend payload | serializes step history | **never serializes steps** (though `CommandStep.attempt` FK + `related_name="steps"` exists) |

So: "challenge feels faster" = the optimistic pending placeholder. "Terminal looks different while
running" = challenge shows a `...` pending line, adventure shows nothing. Same root cause. Fixing it
the right way (cache-derived lines + shared optimistic util) also removes the duplication.

Backend latency is **not** the cause — adventure's backend is lighter and its payload slimmer.

## Approach (decisive)

Make adventure adopt challenge's cache-derived + optimistic-pending model, sharing the *pure*
pieces only. **Do not** build a generic submission hook; **do not** merge the backend command
services in this PR.

Phases 1–4 are one PR. Phase 5 is an explicit follow-up.

---

### Phase 1 — Backend: serialize adventure steps + symmetric submit response (no migration)

`CommandStep.attempt` FK already exists, so this is serialization only.

- **`backend/adventures/serializers.py`**
  - In `adventure_run_payload`, prefetch steps for the current attempt:
    `run.attempts.select_related("adventure_problem", "selected_variant").prefetch_related("steps")`.
  - In `attempt_payload`, add a `steps` list (only the started attempt is serialized through here):
    ```python
    "steps": [
        {"id": s.id, "command_text": s.command_text,
         "terminal_output": s.terminal_output, "result_category": s.result_category}
        for s in attempt.steps.all()  # ordered by pk (default); add .order_by("id") to be explicit
    ],
    ```
  - Leave the slim `adventure_command_payload` **without** steps — the client manages steps via the
    optimistic insert + the response `step` (mirrors challenge's `command_run_payload`).
- **`backend/adventures/services.py`** — `AdventureCommandService.submit` already creates `step`;
  add it to the returned dict (`"step": step`).
- **`backend/adventures/views.py`** — `AdventureRunSubmitCommandAPIView` returns a `step` object
  symmetric to challenge:
  ```python
  "step": {"id": result["step"].id, "command_text": result["step"].command_text,
           "terminal_output": result["step"].terminal_output,
           "result_category": result["step"].result_category},
  ```
  (Keep the existing flat `terminal_output/stdout/stderr/exit_code/solved` for back-compat.)

Backend serialization stays **local** (a 6-line dict is not worth a shared helper — per the
"don't over-abstract" call).

### Phase 2 — Frontend shared utilities (the real reuse)

New file **`frontend/src/shared/practice/terminalSteps.ts`** — move the pure logic currently
private to `useChallengeCommandSubmission`/`useChallengeRun`:

- `terminalLinesFromSteps(steps: TerminalStep[]): TerminalLine[]` — generalize `terminalLinesFromRun`.
  **Replicate challenge's exact mapping** so both terminals are byte-identical:
  - `result_category === 'TargetMatched'` → `success`
  - `result_category === 'Error'` (client error step) → `warning`
  - `result_category === 'Pending'` → `output`, text `...`
  - else (`TargetNotYetMatched` / `Unprocessable` / `Invalid`) → `output`
- `createPendingStep`, `createErrorStep`, `nextEphemeralStepId`, `isEphemeralStep`, `stripEphemeralSteps`.

**`frontend/src/shared/practice/types.ts`** — add a minimal `TerminalStep`
(`{ id, command_text, terminal_output, result_category }`) that both `ChallengeStepLog` and the new
`AdventureStepLog` satisfy.

**`frontend/src/features/challenges/hooks/useChallengeRun.ts` + `useChallengeCommandSubmission.ts`**
— re-import the moved helpers from `shared/practice/terminalSteps`. No behavior change.

### Phase 3 — Adventure migration (delivers BOTH user goals)

- **`frontend/src/features/command-adventures/types.ts`** — add `AdventureStepLog`; add
  `steps: AdventureStepLog[]` to `AdventureAttempt`; add `step` to `AdventureCommandResponse`.
- **New `frontend/src/features/command-adventures/hooks/useAdventureCommandSubmission.ts`**
  (mirrors `useChallengeCommandSubmission`, writing into `current_attempt.steps`):
  - `onMutate`: insert `createPendingStep` into `cached.current_attempt.steps` (after
    `stripEphemeralSteps`); `cancelQueries`.
  - `onSuccess`: **always `stripEphemeralSteps` first**, then merge — slim patch via the existing
    `mergeCommandRun`/`mergeAttempt` (which preserves `steps`), or replace outright on a full-run
    transition (next attempt arrives with empty steps), appending the real `response.step`.
  - `onError`: swap pending → `createErrorStep`.
- **`frontend/src/features/command-adventures/hooks/useAdventureRun.ts`** — return cache-derived
  `lines` (`terminalLinesFromSteps(run.current_attempt?.steps ?? [])`); keep `useHint`/`finishRun`.
- **`frontend/src/features/command-adventures/components/AdventureSession.tsx`** — delete the local
  `lines` useState, the `lineId` ref, and `handleSubmit`'s manual line pushing; consume `lines` from
  the hook and `useAdventureCommandSubmission`. Keep a slimmed `useEffect` that resets **only the
  hint** on `attemptId` change (terminal reset now happens for free via per-attempt cache steps).

### Phase 4 — Tests

- **Frontend (high value, low cost):** `terminalSteps.test.ts` — pending → `...`, error → warning,
  TargetMatched → success, TargetNotYetMatched/Unprocessable → output. Optional: an adventure
  optimistic-submission test (pending appears on submit, replaced on success, error on reject).
- **Backend:** extend `backend/adventures/tests/test_adventure_runs.py` — assert
  `current_attempt.steps` is present/ordered in the run payload and that submit returns a `step`
  object. Challenge tests should pass unchanged (Phase 2 is a no-op refactor for them).

### Phase 5 — (Follow-up PR, OUT OF SCOPE) backend de-dup

Extract `_execute_command_step(owner, command) -> {step, result, next_state}` (clone → normalize →
process → classify → create `CommandStep` + `CommandLog`) shared by `AdventureCommandService.submit`
and `CommandProcessingService.submit_command`. ~40 lines saved, zero API/serializer change. Kept
separate to avoid a regression blast radius across learning-progress code.

---

## Risks & how each is handled (from design pressure-test)

- **R1 — pending step lost on slim-patch merge.** `mergeAttempt` spreads `...prev` and overwrites
  only `counts/repository_state/scenario_context`, so `steps` survives — but make it explicit:
  always `stripEphemeralSteps` in `onSuccess` before writing any server step list (don't rely on
  spread order).
- **R2 — solve transition clears the success line.** Today the `attemptId`-change `useEffect`
  already clears local lines on solve, so cache-derived lines are at parity (at most a 1-frame
  difference). **Verify** before/after on solve; only if it regresses, retain the outgoing final
  step in a short-lived local var until `attemptId` changes. Do **not** redesign the solve flow.
- **R3 — ephemeral id collisions.** The module-level monotonic counter is safe within a run
  (decreasing ids never repeat) and across features (different query keys never share an array).
- **R4 — color change.** Adventure git-errors (`Unprocessable`/`Invalid`) become plain `output`
  instead of amber, matching challenge exactly (the goal). Acceptable/intentional; if warnings are
  wanted later, map `Unprocessable|Invalid → warning` in the shared util for **both**.

## Why not the lighter alternatives

- *Pending placeholder only (≈10 lines, no backend):* fixes the feel + look but leaves the
  ephemeral-state divergence, no refresh persistence, and the duplication the user explicitly
  called out. Rejected as the "best route," but it's the safe fallback if scope must shrink.
- *Generic `useOptimisticCommandSubmission` hook:* over-abstraction — five divergent axes; it would
  be the two hooks disassembled behind an adapter contract. Rejected.

## Files to change

Backend: `adventures/serializers.py`, `adventures/services.py`, `adventures/views.py`,
`adventures/tests/test_adventure_runs.py`.
Frontend: `shared/practice/terminalSteps.ts` (new), `shared/practice/types.ts`,
`features/challenges/hooks/useChallengeRun.ts`, `features/challenges/hooks/useChallengeCommandSubmission.ts`,
`features/command-adventures/types.ts`,
`features/command-adventures/hooks/useAdventureRun.ts`,
`features/command-adventures/hooks/useAdventureCommandSubmission.ts` (new),
`features/command-adventures/components/AdventureSession.tsx`,
`shared/practice/terminalSteps.test.ts` (new).

## Verification

1. **Backend tests:** `pytest backend/adventures backend/challenges` (serializer/view + lifecycle green).
2. **Frontend tests:** `npm test` (or `vitest`) in `frontend/` — new `terminalSteps` test + existing suites.
3. **Manual (run the app):**
   - Adventure: submit a command → terminal shows `cmd` + `...` **instantly**, identical to challenge.
   - Refresh mid-attempt → terminal history **persists** (new capability).
   - Open a challenge run side-by-side → running-state visuals are pixel-identical.
   - Solve a problem → next problem opens with a clean terminal (parity check for R2).
   - Submit a bogus command → error line renders (warning) without breaking the cache.
