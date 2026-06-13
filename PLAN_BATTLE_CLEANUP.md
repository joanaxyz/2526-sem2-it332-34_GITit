# Battle System — Cleanup & Architecture Pass

Branch: `chore/codebase-improvements`. Supersedes the now-stale `PLAN_BATTLE_REFACTOR.md`
(its Part 1 — sabotage removal — is already done in live code; only migration history
`0005`/`0006` and flavor `antagonist=` text remain, which we keep).

Scope confirmed with user: **include the miss-bug fix** (behavior change) and **the full
frontend ChallengeWorkspace refactor**. Do not touch the HP/damage loop semantics except
the broadened miss trigger.

---

## Guiding principles
- **One source of truth.** Collapse backend/frontend duplicated species cycles, duplicated
  LRU caches, duplicated battle-derive logic, duplicated constants.
- **Methods do one thing.** Break the 174- and 128-line submit methods so the battle turn,
  the failure decision, and the response assembly are each named and isolated.
- **Name the magic.** Replace bare literals on hot/visual paths with named constants where it
  aids reading or tuning — not a blanket sweep.
- **Behavior preserved** except the deliberate miss-trigger broadening; every existing test
  stays green and new tests pin the new behavior.

---

## Part A — Backend battle core

### A1. Fix the miss bug (behavior change)
- [battle/engine.py](backend/battle/engine.py#L85): broaden the attack trigger. Today a miss
  requires `turn.counted`; invalid/unprocessable git typos are often *not* counted, so no
  monster attacks — the main "they don't really attack" symptom. New rule: emit
  `monster_attack` (still `cause="miss"`, zero cost) when `living` and not solved and the
  command was a **git attempt that made no progress** — whether or not the budget classifier
  counted it. Keep diagnostics (`git status`/`git log`) free and silent. This needs a new
  `TurnInput` signal (e.g. `git_attempt: bool`) so the engine can distinguish a failed git
  command from non-git noise; the submit paths already know this (challenge:
  `command.strip().lower().startswith("git")` at [practice/services.py:248](backend/practice/services.py#L248)).
- [battle/engine.py](backend/battle/engine.py#L62): extract the three outcome branches into
  named private helpers — `_finishing_blow(state, living, skill)`, `_hit(living, skill)`,
  `_miss(living)` — so `resolve_turn` reads as a short dispatcher. Keep `deepcopy` immutability.
- Add tests in [battle/tests/test_engine.py](backend/battle/tests/test_engine.py): failed git
  command (not counted) → monster attacks; processed-but-no-progress → monster attacks;
  non-git noise → still silent.

### A2. De-overengineer state/constants (one source of truth)
- [battle/state.py](backend/battle/state.py#L36): drop the `zlib.crc32` `_stable_offset`
  indirection; pick species deterministically by index (`idx % len(cycle)` with a simple
  pk/slug-derived start). Keep determinism, lose the CRC ceremony.
- [battle/constants.py](backend/battle/constants.py): inline `MAX_DEFAULT_MONSTERS` and
  `BOSS_HP_PAR_BONUS` (each used once in `state.py`) **or** keep them but remove the duplicate
  `max(3, …)` floor now split across `constants.py` and `state.py` — one floor, one place.
  Fix the stale `CAUSE_MISS` "timeout is reserved" comment (no timer exists) — either drop the
  speculative `'timeout'` from the frontend `MonsterAttackCause` too, or keep both and stop
  calling it reserved.
- `_authored_roster` ([state.py:51](backend/battle/state.py#L51)): `hp:0` is silently upgraded
  to 1. Leave the floor, but it's authored-data only and currently unseeded — see A4.

### A3. Remove the submit-path duplication (DRY the two callers)
- The lazy init `if not run.battle_state: run.battle_state = initial_*()` is copy-pasted in
  [practice/services.py:273](backend/practice/services.py#L273) and
  [adventures/services.py:469](backend/adventures/services.py#L469). Add a single helper in
  [battle/state.py](backend/battle/state.py) — `ensure_battle_state(holder, quest, *, kind)` or
  two thin `ensure_*` functions — and call it from both.
- **Kill `_command_skill`** in [adventures/services.py:544](backend/adventures/services.py#L544).
  It re-parses the raw command string, diverging from the challenge path which uses the
  simulator's `command_result.command_family` ([practice/services.py:282](backend/practice/services.py#L282)).
  The adventure path already runs through `CommandExecutor`, so route the family from the
  executor result and delete the bespoke parser. Single skill source.
- Extract a shared `_apply_battle_turn(...)` (or a small `BattleTurnApplier`) used by both
  submit methods: takes the holder + computed signals, ensures state, runs `BattleEngine`,
  writes `battle_state`, returns events + a "changed" flag. Both submit methods shrink and the
  battle wiring lives in one place.

### A4. Dedup the LRU command-history cache
- [adventures/services.py:65](backend/adventures/services.py#L65) `AdventureCommandHistoryCache`
  and [challenges/services.py:88](backend/challenges/services.py#L88) `CommandHistoryCache` are
  the same `OrderedDict` LRU (`_max_entries = 512`, same evict/remember logic), differing only
  in the cache key. Extract a generic base (e.g. `backend/common/lru.py` or a base class taking
  a key function) and have both subclass it.

### A5. Shrink the submit methods (single responsibility)
- [practice/services.py:198](backend/practice/services.py#L198) `submit_command` (174 lines)
  and [adventures/services.py:413](backend/adventures/services.py#L413) `submit` (128 lines):
  after A3 extracts the battle block, also pull out (a) evaluation, (b) the failure/`update_fields`
  decision, (c) response assembly into named helpers. Target: each public method reads as a
  short orchestration. Move the two inline `from django.utils import timezone` imports
  ([practice/services.py:338,375](backend/practice/services.py#L338)) to module top. Replace the
  `_chest_check_pending` monkey-patch on the ORM instance ([practice/services.py:415](backend/practice/services.py#L415))
  with an explicit return value from `_complete_run`. Make `update_fields` a list/ordered set so
  the `sorted()` band-aid at [:345](backend/practice/services.py#L345) is unnecessary.

### A6. Constants over string literals
- [challenges/payloads.py:138-140](backend/challenges/payloads.py#L138): replace raw `"primary"`
  / `"completed"` with `ChallengeRun.Mode.PRIMARY` / the existing status constants.
- [challenges/payloads.py:18](backend/challenges/payloads.py#L18): tie `DIFFICULTY_ORDER` to the
  `DIFFICULTY_*` constants in `common.constants` instead of a free-floating list.

### A7. Seed the dead `encounter_spec` path (or drop it)
- `AdventureQuest.encounter_spec` + `_authored_roster` exist and are tested, but
  [seed_curriculum_v2.py](backend/curriculum/management/commands/seed_curriculum_v2.py#L186)
  never writes `encounter_spec` into the quest `defaults={}`, so authored adventure rosters are
  silently ignored. Decision: **wire `encounter_spec` into the seeder** (mirror how `boss_spec`
  is seeded at [:248](backend/curriculum/management/commands/seed_curriculum_v2.py#L248)) so the
  authoring path is real. Add one authored adventure encounter in
  [adventure_quests.py] as a smoke example, or leave authoring empty but functional.

### A8. Cleanup
- Delete the dead `.pyc` ghosts (`battle/__pycache__/sabotage.*`,
  `tests/__pycache__/test_sabotage.*`). Confirm `.gitignore` already excludes `__pycache__`.
- Remove the stale `PLAN_BATTLE_REFACTOR.md` (replaced by this file) and update
  `PLAN_BATTLE_REDESIGN.md` only if it still claims sabotage is live.

---

## Part B — Frontend battle modules

### B1. One species source
- [deriveBattleEvents.ts:38-40](frontend/src/shared/battle/deriveBattleEvents.ts#L38) keeps its
  own `MOB_CYCLE`/`ELITE_CYCLE`/`BOSS_CYCLE`, duplicating backend `*_SPECIES_CYCLE` and not even
  matching (backend has no elites). The client fallback only fires when `response.battle` is
  absent. Align the client cycles to the backend set and derive HP the same way the backend
  does, so a late/missing block doesn't paint a roster the backend would never produce. Add a
  single `species.ts` registry the rosters read from; keep elites only if a real authored path
  uses them.

### B2. Share the battle-derive call
- `AdventureSession.handleCommand` ([AdventureSession.tsx:94-122](frontend/src/features/command-adventures/components/AdventureSession.tsx#L94))
  and `ChallengeWorkspace.submit` ([ChallengeWorkspace.tsx:250-295](frontend/src/features/challenges/components/ChallengeWorkspace.tsx#L250))
  both do `response.battle ?? deriveBattleEvents(...)` with near-identical inputs. Extract a
  shared `resolveBattleBlock(response, director, signals)` (or a `useBattleSync` hook) so the
  two surfaces can't drift. Replace the magic string `'TargetMatched'`
  ([ChallengeWorkspace.tsx:264](frontend/src/features/challenges/components/ChallengeWorkspace.tsx#L264))
  with a shared typed constant mirroring the backend `RESULT_TARGET_MATCHED`.

### B3. Fix the fast-forward attack drop (behavior change, pairs with A1)
- [useBattleDirector.ts:201-225](frontend/src/shared/battle/hooks/useBattleDirector.ts#L201):
  the `monster_attack` step is `cosmetic: true`, so a rapid resubmit's `fastForward()` discards
  it and the mistake never shows. Split it: a **non-cosmetic snap step** (screen flash + Blue's
  flinch — instant under `fast`) that always runs, plus the **cosmetic flourish** (lunge/
  projectile) that may be dropped. The mistake is always acknowledged; only the flourish is
  skippable. Mirror the broadened miss in `deriveBattleEvents` so the fallback matches A1.

### B4. ChallengeWorkspace.tsx split (645 → focused units)
- Extract `useResizeHandle(ref, setter, clamp)` and replace the three duplicated
  `beginTerminalResize`/`beginDiagramResize`/`beginTerminalPaneResize` handlers
  ([:315-398](frontend/src/features/challenges/components/ChallengeWorkspace.tsx#L315)).
- Move `ResizeHandle` (nested at [:91](frontend/src/features/challenges/components/ChallengeWorkspace.tsx#L91))
  and the layout constants into their own module.
- Lift `submit()` and the six `useMutation`s into a `useChallengeWorkspaceActions` hook (or
  co-locate with the existing `useChallengeCommandSubmission`).
- Fix the `ContextualFeedbackPanel` double-render
  ([:539-554](frontend/src/features/challenges/components/ChallengeWorkspace.tsx#L539)): the panel
  currently renders in **both** branches, so the `false` branch still shows it. Decide intended
  behavior (always-on vs gated) and make the JSX say exactly that; remove the dangling resize
  handle when the panel is gated off.

### B5. Share the budget widget
- [AdventureCommandBudget.tsx](frontend/src/features/command-adventures/components/AdventureCommandBudget.tsx)
  and [CommandBudgetHeader.tsx](frontend/src/features/challenges/components/CommandBudgetHeader.tsx)
  are the same hover-tooltip budget widget with different field names/labels. Extract a shared
  `BudgetWidget` with the two surfaces supplying a field mapping + label. Also dedup the
  `PROJECT_FILES_OPEN_KEY` string (declared identically in `AdventureSession` and
  `ChallengeWorkspace`) into one shared constant.

### B6. Lower-risk polish (do if cheap, skip if it grows the diff)
- Memoize `prefersReducedMotion()` to one call per turn in `useBattleDirector`.
- Name the worst visual magic numbers in `effectRegistry.ts` / `BattleStage.tsx` /
  `MonsterActor.tsx` (player scales, lunge return `+360`, HP-bar `+6`) as local constants.
- Fix `mergeRepositoryState`'s redundant `length > 0` conditions
  ([useChallengeCommandSubmission.ts:124](frontend/src/features/challenges/hooks/useChallengeCommandSubmission.ts#L124)).
- `pull`/`fetch` effects aliased to `pushWave` (wrong visual direction) in `effectRegistry.ts` —
  give them a correct direction or leave a real TODO; don't silently keep the placeholder.

---

## Part C — Tests
- **Backend:** add the two broadened-miss engine tests (A1); add a persistence test that drives
  ≥2 commands through one run and asserts `battle_state` round-trips from the DB (currently
  untested); add a lazy-init test for a run that starts with `battle_state={}`. Convert the two
  battle integration files to a module-scoped seed fixture instead of per-test
  `call_command("seed_curriculum_v2")`.
- **Frontend:** add unit tests for the now-shared `deriveBattleEvents` / `resolveBattleBlock`
  (pure functions, clear branches — currently zero frontend battle tests) and for `BattleQueue`
  fast-forward keeping the non-cosmetic snap step (B3).

---

## Critical files
Backend: `backend/battle/{engine,state,constants,payloads}.py`,
`backend/practice/services.py`, `backend/adventures/services.py`,
`backend/challenges/services.py`, `backend/challenges/payloads.py`,
`backend/common/` (new shared LRU), `backend/curriculum/management/commands/seed_curriculum_v2.py`.
Frontend: `frontend/src/shared/battle/{deriveBattleEvents,types}.ts`,
`frontend/src/shared/battle/hooks/useBattleDirector.ts`,
`frontend/src/features/challenges/components/{ChallengeWorkspace,ChallengeBattleStrip,CommandBudgetHeader}.tsx`,
`frontend/src/features/command-adventures/components/{AdventureSession,AdventureBattlePanel,AdventureCommandBudget}.tsx`,
plus new shared `useResizeHandle`, `BudgetWidget`, `resolveBattleBlock`, `species.ts`.

## Verification
1. **Backend:** `cd backend && python manage.py test battle challenges adventures practice` — all
   green, including new miss/persistence tests.
2. **Migrations/seed:** no schema changes expected (sabotage column already dropped); run
   `python manage.py seed_curriculum_v2` and confirm authored `encounter_spec`/`boss_spec` seed
   without error.
3. **Frontend:** `cd frontend && npm run lint && npm run build` — clean; watch the entry-chunk
   budget (react-hooks v7: keep callback refs).
4. **/dev/battle:** click **Miss** repeatedly fast → every miss flashes + Blue flinches (snap step
   survives fast-forward). **Hit** → 1 HP chip; **Solve** → finishing blow. Resize handles and
   the budget widget behave identically on both surfaces.
5. **Real run:** start a challenge, submit a deliberately invalid git command → monster attacks;
   submit a valid-but-no-progress command → also attacks; solving lands the kill.
6. Update memory `battle-system-architecture.md`: miss trigger broadened, duplication collapsed
   (species/LRU/derive/budget-widget), submit methods decomposed, `_command_skill` removed,
   ChallengeWorkspace split.
