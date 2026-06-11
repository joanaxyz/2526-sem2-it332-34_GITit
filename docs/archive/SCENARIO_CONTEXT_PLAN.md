# Scenario Context v3 — strict schema + adventure-only objective field

## Problem
`scenario_context` is a free-form JSONField, so the frontend can't predict what it gets.
`repository.current_state` text ("app.py is staged.") duplicates what the learner already sees
live in ProjectStructurePanel / LiveDagPanel (verified: those panels render `RepositorySnapshot`,
never the text list). `constraints`/`process_notes` are never authored; `process_notes` is never
rendered. The objective checklist lives inside scenario_context but is adventure-only, forcing the
frontend to merge per-command `objective_checks` patches *back into* scenario_context.

## Decision
1. **Strict flat v3 schema, same for both modes** — seed/model fully controls what the frontend shows:
   ```json
   {"schema_version": 3, "story": "…", "task": "…",
    "details": [{"label": "Required commit message", "value": "Update greeting"}],
    "constraints": ["…"]}
   ```
   - `details` = promoted `required_details` ("key facts": commit message, branch name), rendered in **both** adventure and challenge (hard challenges hide the target state, so details are how the learner knows the required message/branch).
   - **Dropped**: `brief`/`repository.current_state` (redundant with live panels), `process_notes`, the whole `objective` sub-object.
2. **Objective checklist becomes a dedicated field**: `AdventureProblem.objective_checks` JSONField (authored `[{label, requirement}]`, server-only). Problem-only — no variant/ChallengeLevel field. Payloads emit live `objective_checks: [{label, satisfied}]` as a top-level attempt field on both the full and per-command paths; frontend stops merging checks into scenario_context.

## Backend steps

### 1. Normalizer — `backend/practice/context.py`
- Rewrite `_normalize_v2` → `_normalize_v3`: whitelist-only output `{schema_version: 3, story (fallback_story if empty), task, details[], constraints[]}`; keep `_drop_empty`, `_details`, `_text` helpers.
- `normalize()`: if `schema_version != 3` → hard fallback `{schema_version: 3, story: fallback_story}`.
- Keep `LEAKY_KEYS` stripping (defense-in-depth). Delete `brief`/`repository`/`objective`/`process_notes` handling and the checks-injection comment.

### 2. Models — `backend/adventures/models.py`
- Add `objective_checks = models.JSONField(default=list, blank=True)` to `AdventureProblem` (next to `scenario_context`, ~line 49). No change to ChallengeLevel or variants.

### 3. Migration — fold into `backend/adventures/migrations/0001_initial.py`
- Add `('objective_checks', models.JSONField(blank=True, default=list))` to the AdventureProblem CreateModel block (project convention: pre-launch, recreate dev DB + reseed; no forward migration).

### 4. Builder — `backend/practice/builders.py`
- `_validate_objective_checks`: change signature to take the checks list (`build()` passes `getattr(problem, "objective_checks", []) or []`) and validate each against **this variant's** `target_state`/`initial_state`/`solution_commands` (pairing is required: checks are authored on the problem, target_state lives on the variant). No-op for ChallengeLevel (no field).
- Add seed-time strictness in `build()`: rejected rendered `scenario_context_template` if non-empty and (`schema_version != 3` or any top-level key outside `{schema_version, story, task, details, constraints}`) → `ProblemVariantBuildError`. Empty `{}` template (the only case today) keeps the minimal fallback path.
- Keep the solution-command-leak substring guard unchanged.

### 5. Adventure serializer — `backend/adventures/serializers.py`
- `_live_objective_checks`: read `attempt.adventure_problem.objective_checks` instead of `raw_context["objective"]["checks"]`.
- `attempt_payload`: delete the `context.setdefault("objective", {})["checks"] = live_checks` re-injection; add sibling key `"objective_checks": _live_objective_checks(attempt) or []` next to `"scenario_context"`.
- `adventure_command_payload` (~line 215) already emits `objective_checks` under `current_attempt` — unchanged; both paths now expose checks at the attempt level.

### 6. Challenge serializer — `backend/challenges/serializers.py`
- `_scenario_context` unchanged (now returns v3 automatically). No objective handling existed.

### 7. Seeds — authored content
- `backend/curriculum/curriculum_v2/drills.py` (5 drills): convert each `scenario_context` to v3 (`story`, `task`, `details` = old `required_details`); move `objective.checks` to a new sibling spec key `objective_checks`. Drop all `current_state` lines — every one restates panel-visible state ("app.py is staged.", "main and docs-refresh both point at the latest commit.", …); fold anything genuinely useful into `story`.
- `backend/curriculum/curriculum_v2/workflows.py` (12 levels): convert to v3. No `objective_checks` (challenges never had them). Add `details` where key facts exist — especially `stage-commit-switch` levels: `Required commit message: Update greeting`, `Target branch: docs-refresh` (critical for hard level, which has no target-state reveal).
- `backend/curriculum/management/commands/seed_curriculum_v2.py`: add `"objective_checks": spec.get("objective_checks", [])` to AdventureProblem `update_or_create` defaults (~line 199). Workflows/variant sync unchanged.

### 8. Backend tests
- `backend/challenges/tests/test_challenge_curriculum.py::test_scenario_context_normalizer_strips_answers_and_evaluator_internals` (~165): rewrite for v3 — input with v3 keys + leaky keys; assert leaky strings absent, `details` preserved, no `objective` key; assert v2/unknown input hard-falls-back to `{schema_version: 3, story: fallback}`.
- `backend/adventures/tests/test_adventure_runs.py::test_objective_checklist_ticks_off_as_state_reaches_target` (~238): assert on `attempt_payload(attempt)["objective_checks"]` instead of `["scenario_context"]["objective"]["checks"]`.
- `backend/evaluation/tests/test_checklist.py`, `test_adventure_scheduler.py` (variant copy ~line 108): no changes needed.

## Frontend steps

### 9. Types — `frontend/src/shared/practice/types.ts`, `frontend/src/features/command-adventures/types.ts`
- `PracticeScenarioContext` → flat `{schema_version?, story?, task?, details?: RequiredDetail[], constraints?: string[]}`; remove `brief`/`repository`/`objective`.
- `AdventureAttempt`: add `objective_checks: ObjectiveCheck[]`. Fix the stale "schema_version 2 / brief / objective" doc comment on `AdventureScenarioContext`. `AdventureRunPatch.current_attempt.objective_checks` already exists — keep.

### 10. Normalizer — `frontend/src/shared/practice/utils/practiceContext.ts`
- `NormalizedPracticeContext` → `{story, task, details: {label,value}[], constraints: string[]}` (drop `current_state`, `checks`; rename `required_details` → `details`).
- `normalizePracticeContext`: read flat v3 keys. `hasPracticeContext`: OR over the four remaining fields. Keep `ObjectiveCheck` export (used by the checks prop).

### 11. Panel — `frontend/src/shared/practice/components/PracticeContextPanel.tsx`
- `PracticeBriefCard`: replace `showObjective` with `checks?: ObjectiveCheck[]`.
  - Remove the "Repository state" section.
  - Render `details` **always** (both modes) in its own "Key details" section (the existing `<dl>` block).
  - Render the "Objective" checklist section only when `checks?.length` (adventure passes them; challenge doesn't).
- `contextForRun` fallback → v3 shape: `{story: run.challenge.narrative, task: run.challenge.summary}`.

### 12. Adventure wiring
- `AdventureContextPanel.tsx`: pass `checks={attempt.objective_checks}` instead of `showObjective`.
- `useAdventureCommandSubmission.ts` `mergeAttempt`: stop merging into `scenario_context`; update top-level: `objective_checks: patch.objective_checks?.length ? patch.objective_checks : prev.objective_checks` (preserve prior on null/empty, matching current behavior). `scenario_context` is never touched mid-attempt.

## Edge cases
- Variant fallback: empty template → normalizer minimal v3 (`story` only); builder strictness must allow `{}`.
- Solution-leak guard: `details.value` like `docs-refresh` won't match the full solution command string check — guard stays effective and unchanged.
- Challenges with no authored context still fall back to `challenge.narrative`/`summary` via `contextForRun`.

## Verification
Backend (`backend/`):
1. Recreate dev DB (drop/recreate per project convention) → `python manage.py migrate` → `python manage.py seed_curriculum_v2` (exercises builder validation: objective_checks × each variant target_state).
2. `python manage.py test challenges.tests.test_challenge_curriculum adventures.tests.test_adventure_runs adventures.tests.test_adventure_scheduler evaluation.tests.test_checklist`

Frontend (`frontend/`):
3. `npx tsc --noEmit` — flushes out every removed `brief`/`repository`/`objective`/`current_state` reference.
4. `npm test`.

UI click-through:
5. Adventure: open the "Commit staged work" drill — brief shows story/task + Key details (Required message text), no "app.py is staged." repository-state block; Objective checklist still ticks live after `git commit`.
6. Challenge: open a `stage-commit-switch` level (hard especially) — Key details show commit message + branch; no Objective section, no Repository state section.
