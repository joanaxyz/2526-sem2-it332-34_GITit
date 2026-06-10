# Command Adventure — Spaced Repetition + Mastery + Pass-Bar Scoring

Implementation plan. Turns Command Adventure from a one-pass linear walk into a
Duolingo-style **spaced-repetition mastery session** gated by a **points pass-bar**
that unlocks Challenge.

## Design decisions (locked)

- **Spacing:** encounter-based (no wall-clock). `due` when `current_encounter_index − last_seen_seq ≥ interval(strength)`, where the encounter index = count of the user's attempts in this adventure. Interval schedule (default): `{box0:1, box1:3, box2:6}`.
- **Mastery boxes:** Leitner `0..N`, `N = AdventureProblem.required_successful_attempts`. Solve(pass) → +1 (cap N); fail → −1 (demote). Mastered at box N.
- **Scheduler:** two interleaved tracks — *introduction front* (new commands, in `sort_order`, gated by prerequisites) and *review pool* (introduced-but-unmastered, resurfaced when due, weakest-first, random tie-break). Warm-up: pure sequential until introduced pool ≥ `K` (default 2).
- **Prerequisites:** explicit DAG. A command is eligible to introduce only when every prerequisite is at strength ≥ 1 (solved at least once).
- **Scoring:** `session_score = Σ (box_value × quality)` awarded **only when a box actually advances**. `box_value = 10` (flat). `quality = final_score/100` (so a passed attempt contributes 0.7–1.0). Re-solving a mastered command → 0 (no farming). Fail → 0 + demote.
- **Pass:** `total_achievable = Σ_commands (N × box_value)`; `pass_bar = 0.60 × total_achievable`; plus a **floor**: every command strength ≥ 1. `passed` when `session_score ≥ pass_bar` AND floor met → unlocks Challenge for the storey. Passing is a milestone; the user may keep practicing toward full mastery.
- **Variants:** each encounter serves the least-recently-used variant for (user, problem); **degrade gracefully** (cycle) if fewer than N exist, so the system works before all variants are authored.
- **Adventure stays minimal scaffolding** (hints only). No contextual feedback / diagrams — those remain Challenge-only.

## Reused existing fields
- `AdventureProblem.required_successful_attempts` → box count N.
- `AdventureProblem.sort_order` / `usage`/`topic` sort_order → introduction order + prereq precedence check.
- `scoring.py` `final_score` / `passed` → quality multiplier + box-advance trigger.
- `ProblemCompletion.adventure_problem` (currently unused FK) → optional per-command completion record.

---

## Workstreams & sequencing

### Phase 0 — Content (parallel, unblocks quality, not code)
Author in `backend/curriculum/curriculum_v2/drills.py`:
- **≥ N variants per drill** (most have 1 today). Required for reviews to vary; scheduler degrades gracefully until then.
- **`prerequisites`** per drill spec (list of prerequisite drill refs by `usage`+`slug`).

### Phase 1 — Models + migration (additive, non-destructive)
`backend/adventures/models.py`:
- New `AdventureMastery(user, adventure_problem, strength=0, introduced=False, last_seen_seq=0, updated_at)`, `unique_together (user, adventure_problem)`, index on `(user, adventure_problem)`.
- `AdventureProblem.prerequisites = M2M("self", symmetrical=False, blank=True, related_name="dependents")`.
- `AdventureRun`: add `session_score` (repurpose/keep `total_score`), `passed_at = DateTimeField(null=True)`.
- `CommandAdventure`: optional `pass_bar_fraction = FloatField(null=True)` (override; default constant 0.60). `BOX_VALUE`, `PASS_BAR_FRACTION`, `WARMUP_K`, `INTERVALS` as module constants.

**Migration:** all additive (new tables, nullable/defaulted fields) → a normal **`0002_*` migration** with no data loss. *(Alternative: fold into the squashed `0001_initial` + full reset to keep the one-migration-per-app convention — recommend additive `0002` to preserve the freshly-seeded data.)*

Critical files: `backend/adventures/models.py`, `backend/adventures/migrations/`.

### Phase 2 — Scheduler service
New `backend/adventures/scheduler.py` (`AdventureScheduler`), adventure-local (do **not** import challenges' `VariantSelectionService`):
- `next_problem(user, adventure) -> AdventureProblem | None`:
  ```
  introduced = mastery rows with introduced=True
  pool       = introduced with strength < N           # unmastered
  new        = problems not introduced, in sort_order, whose prereqs all strength>=1
  due        = [p in pool if idx - last_seen_seq(p) >= interval(strength(p))]
  if len(introduced) < WARMUP_K and new:  return new[0]
  if due:                                  return weakest(due)   # random tie-break
  if new:                                  return new[0]
  if pool:                                 return weakest(pool)
  return None                              # all mastered → session complete
  ```
- `select_variant(user, problem)`: published variants ordered by least-recent use in this user's attempts (unused first), cycle.
- `apply_result(mastery, *, passed, solved)`: passed → strength=min(N, +1) (record box_advanced); fail (not solved) → strength=max(0, −1); always bump `last_seen_seq` to current index, set `introduced=True`.

`backend/adventures/services.py`:
- `_open_attempt`: use `scheduler.select_variant` instead of "first variant"; upsert `AdventureMastery` (introduced, last_seen_seq).
- Replace `_advance` with scheduler-driven `next_problem`; if `None` → `_finish`.
- `record_attempt_result`: after scoring, call `apply_result`, award mastery points when a box advanced, accumulate `session_score`, recompute `passed_at` (see Phase 3).

Critical files: `backend/adventures/services.py`, new `backend/adventures/scheduler.py`.

### Phase 3 — Scoring, pass-bar, Challenge unlock
`backend/adventures/scoring.py`: add `mastery_points(*, box_advanced: bool, final_score: int) -> int` = `BOX_VALUE * (final_score/100)` if `box_advanced` else 0.

`backend/adventures/services.py`:
- Maintain `run.session_score`. Drop the `_finish` averaging.
- Compute `total_achievable` and `pass_bar` for the adventure; set `run.passed_at` when `session_score ≥ pass_bar` AND floor (all commands strength ≥ 1) met.
- On first pass, write Challenge-unlock state for the storey.

**Challenge unlock wiring** — `backend/challenges/services.py` `_ensure_unlocked`:
- For `difficulty == EASY`: replace the unconditional `return` with a check that the user has **passed the storey's adventure** (`AdventureRun.objects.filter(user, command_adventure__module=level.module, passed_at__isnull=False).exists()`), *only if* the storey has a published `CommandAdventure` (else fall through / unlocked).
- MEDIUM/HARD gate unchanged.
- **This changes existing behavior** (EASY was always open) → update affected challenge tests.

Critical files: `backend/adventures/scoring.py`, `backend/adventures/services.py`, `backend/challenges/services.py`, `backend/challenges/selectors.py` (unlock display), tests.

### Phase 4 — Prerequisites + seed validation
`backend/curriculum/management/commands/seed_curriculum_v2.py`:
- `_seed_command_drills`: resolve each spec's `prerequisites` (usage+slug) to `AdventureProblem` rows and set the M2M (second pass after all drills exist).
- `_validate_command_level` / new check: prerequisite graph is **acyclic**, every prereq is **published**, **precedes** in `sort_order`, and lives in the **same adventure/module**.
- Variant-count guard in `_validate_problem_variants`: warn (or error under `--validate`) when `published_variants < required_successful_attempts`.

Critical files: `backend/curriculum/management/commands/seed_curriculum_v2.py`, `backend/curriculum/curriculum_v2/drills.py`.

### Phase 5 — Serializer / API
`backend/adventures/serializers.py` `adventure_run_payload`:
- Add `session_score`, `pass_bar`, `total_achievable`, `passed` (bool), `floor_met`.
- Add `mastery`: per-command `{slug, title, strength, mastered_bar: N, introduced}` + `commands_mastered`/`total`.
- `attempt_payload`: optionally include `encounter_kind` (`"intro"` | `"review"`) for UI framing.
- `current_problem_index`/`progress` lose meaning (problems repeat) → replace with mastery/score progress.

Critical files: `backend/adventures/serializers.py` (+ adventure views if any field is computed there).

### Phase 6 — Frontend
`frontend/src/features/command-adventures/`:
- **AdventureProgressBar.tsx**: the linear "problem 1..N nodes" model no longer fits (problems repeat). Replace with **session-score vs pass-bar** progress + **commands-mastered X/N**. Remove hardcoded `PASSING_SCORE = 70`.
- **New `AdventureMasteryPanel.tsx`**: per-command strength boxes (0..N).
- **AdventureResult**: show pass state + **"Challenge unlocked" CTA**; pass-bar marker on the score bar.
- **types.ts**: extend `AdventureRun` with `session_score`, `pass_bar`, `passed`, `mastery[]`; drop reliance on `current_problem_index`/`progress`.

Critical files: `frontend/src/features/command-adventures/components/AdventureProgressBar.tsx`, new `AdventureMasteryPanel.tsx`, `AdventureResult.tsx`, `types.ts`, `useAdventureRun.ts`.

### Phase 7 — Tests
- **Scheduler** (`backend/adventures/tests/`): warm-up order, prereq gating (command withheld until prereq solved), due/interval math, demotion-on-fail resurfaces soon, variant LRU rotation + graceful single-variant cycling, session completes when all mastered.
- **Scoring/pass-bar**: points only on box advance, no-farm on mastered, floor blocks pass, `passed_at` set at threshold.
- **Unlock integration**: passing the adventure unlocks EASY challenge; not-passed → `Locked`.
- **Seed**: prereq DAG/cycle/precedence validation; variant-count guard.
- Keep the existing 25 green; update challenge-unlock tests for the new EASY gate.

---

## Open knobs (defaults chosen; trivially tunable)
`BOX_VALUE=10`, `PASS_BAR_FRACTION=0.60`, per-command floor = box ≥ 1, `WARMUP_K=2`, `INTERVALS={0:1,1:3,2:6}`, demotion = −1 box. Session stays open after pass (ends on full mastery or user finish); optional max-length cap if sessions run long.

## Verification (end-to-end)
1. `makemigrations --check` clean; `migrate` applies `0002` with no data loss.
2. `seed_curriculum_v2 --validate` passes (prereq DAG + variant guard).
3. `pytest adventures challenges practice curriculum -q` green.
4. Manual: start an adventure → confirm sequential intro during warm-up, then interleaved reviews of weak commands, prereq-gated introductions, variant rotation, session score climbing to the pass-bar, and EASY Challenge unlocking on pass (and staying locked before).

## Risk / sequencing notes
- Scheduler degrades gracefully with 1 variant → ship Phases 1–7 independent of Phase 0 content; quality improves as variants are authored.
- The EASY-challenge gate is a deliberate product behavior change — coordinate test updates.
- Encounter index is a cheap `COUNT` per pick; fine at this scale, revisit if hot.
