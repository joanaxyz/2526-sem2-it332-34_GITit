# Battle Redesign — Adventures & Challenges

> **Execution status (2026-06-13): IMPLEMENTED** — all phases landed in one pass.
> Verified: 31 battle backend tests + full suites (backend 288 passed, the 11
> failures pre-exist this work on the branch; frontend 123 tests, tsc, eslint,
> build all green). Visual smoke-test on /dev/battle (cast sync, miss, travel).
> Outstanding: `manage.py seed_curriculum_v2` against the remote DB timed out on
> a row lock (atomic, rolled back) — rerun it to land boss/sabotage specs; exact
> per-species `footOffset`/`hpBarFraction`/cast-segment numbers are meant to be
> tuned on /dev/battle.

Turn-based battle layer over the existing command loop. Backend-authoritative HP; real boss sabotage; parallax battle stage above the terminal; Blue summons his book, floats, and casts per command; per-git-skill effects; DAG reacts to attacks and sabotage.

**Decisions locked with user:**
- Turn-based; turn limit = existing command budget (unchanged).
- **No timer in v1** (user unsure since it's turn-based). Miss = failed/invalid git command OR counted command with no new progress. The `cause` field on `monster_attack` events (`"miss"` now) is the extension point — a future timer just emits the same event with `cause: "timeout"`.
- **One player bar: the command budget IS Blue's mana** (user decision 2026-06-13, replacing separate player HP which clashed with the turn limit). Every counted command costs 1 mana; mana empty = the existing budget failure, rendered as defeat. Misses trigger monster attacks as drama (no extra resource cost). Monster/boss HP stays backend-authoritative in `battle_state`.
- Battle stage = **uppermost element of the right workspace column** on both surfaces: above the terminal (adventure) and above the DAG row (challenge). The sidebar keeps its full height beside it. Collapsible to a slim HP bar for short viewports.
- **Real backend sabotage** in v1 (boss actually mutates repository state, authored per scenario).

---

## 1. Asset reorganization (frontend/scripts/reorganize-monsters.mjs, run once)

Per monster, 4 redundant variants exist. Policy:
- **KEEP** `"<Name> with shadows"` strips (baked shadows ground actors for free) + the 100×100 projectile strips (Arrow, Magic for Priest/Wizard).
- **DELETE** plain folders, `Shadow sprites/`, `(Split Effects)/`, stray `images/` folders.
- **DELETE species**: `Armored Axeman` (redundant w/ Armored Orc), `Orc rider` (reads poorly at stage height). 18 species kept.

Final tree: `frontend/src/assets/sprites/monsters/<kebab-name>/{idle,walk,attack01,attack02,hurt,death,portrait}.png` + `monsters/projectiles/{arrow,magic-wizard,magic-priest}.png`.

Script also reads PNG IHDR widths and prints a frame-count table (`width/100`) to paste into the registry — no guessing 6f vs 8f strips.

**`frontend/src/shared/battle/monsters.ts`** registry (analogous to `characters.ts`):
```ts
type MonsterDefinition = {
  id: string; tier: 'mob' | 'elite' | 'boss'
  sprites: Record<'idle'|'walk'|'attack01'|'attack02'|'hurt'|'death', SpriteAnimation>
  attack: { kind: 'melee'; lungePx: number; hitFrame: number }
        | { kind: 'projectile'; sheet: SpriteAnimation; launchFrame: number }
  metrics: { scale: number; footOffset: number; hpBarYOffset: number }
}
```
- Adventure mobs: slime, skeleton, orc, archer (T1); soldier, swordsman, skeleton-archer, armored-orc (T2); elites: armored-skeleton, greatsword-skeleton, knight, lancer.
- Challenge bosses (scale 1.5–2×): werebear, werewolf, elite-orc, knight-templar, wizard, priest (wizard/priest = ranged bosses).

## 2. Blue: float+book stitching & cast sync

- **Build-time stitch** (`frontend/scripts/stitch-float-book.py`, Pillow): `float.png` + `book.png` are both 1280×1280 / 5×5 / 25f — whole-sheet `Image.alpha_composite` → `float_book.png`. (Two synced runtime animators would drift; stitching is free at runtime.) Per-cell paste with offset as fallback if alignment needs tuning.
- Register currently-unused sheets in `characters.ts`: `summon` (8×8/64f one-shot), `cast` (8×8/64f), `hurt` (5×5/25f one-shot), `float_book` (loop).
- **Cast↔latency sync** (cast.png at ~32fps, segments tuned on the dev playground):
  | segment | frames | role |
  |---|---|---|
  | windup | 0–23 | starts when request fires |
  | mid-loop | 24–35 loop | holds while request pending (covers 200–800ms+) |
  | release-throw | 36–47 | on response; effect spawns at segment end |
  | release-recover | 48–63 | during projectile flight → back to float_book |
  Fast responses skip the mid-loop (windup chains straight to release) so it never looks janky.

**SpriteAnimator extensions** ([SpriteAnimator.tsx](frontend/src/shared/sprites/SpriteAnimator.tsx), ~40 lines, backward-compatible): `FrameSegment {from,to,loop?}`; `setAnimation(anim, {segment?, onComplete?})` and `playSegment(segment, {onComplete?})` — the stepper clamps/wraps within the segment and reuses the existing `completeRef` plumbing.

## 3. Shared frontend battle module — `frontend/src/shared/battle/`

```
types.ts                 # BattleBlock/BattleEvent contract, stage direction types
monsters.ts              # registry (above)
battleQueue.ts           # plain sequential async-step queue with fastForward()
deriveBattleEvents.ts    # client-side event synthesis until backend block ships
hooks/useBattleDirector.ts   # lifecycle → queued choreography; exposes refs+roster state
hooks/useStagePause.ts       # IntersectionObserver + visibilitychange → pause animators
components/BattleStage.tsx   # panel: parallax + actors + HP bars + groundFooter slot; variant adventure|challenge
components/ParallaxBackdrop.tsx  # sky/clouds/ground, transform-only layers
components/PlayerActor.tsx   # summon → float_book loop → cast segments → hurt
components/MonsterActor.tsx  # idle/walk/attack/hurt/death + floating HealthBar
components/HealthBar.tsx     # scaleX-transition bar (compositor-only)
effects/effectRegistry.ts    # command family → effect (WAAPI, promise resolves at impact)
effects/effects.css
```
Plus `features/command-adventures/components/AdventureBattlePanel.tsx`, `features/challenges/components/ChallengeBattleStrip.tsx` (thin adapters), and a DEV-only `/dev/battle` playground route.

**Choreography queue**: server responds in ~200–800ms but choreography takes 2–4s, and the player can submit again mid-sequence. `BattleQueue` steps are tagged `cosmetic` (projectile flight, flinch) vs `state-snap` (HP set, death). New submission → `fastForward()`: cosmetic steps drop, state-snap steps run instantly (bars jump to authoritative values), then the new cast begins. Stage never lies about authoritative state for more than one beat.

**Lifecycle mapping**: `onCastStart(cmd)` before `mutate` → windup/mid-loop; `onResolve(battle)` plays events in order (cast release → effect → monster hurt → HP drain → death fade…); `onError()` aborts cast back to float (network error ≠ game event); `onEncounterChange(index)` (watching `current_quest_index`) → Blue runs right with parallax scroll ~1.8s, new monsters walk in, summon → float_book.

**Monster attacks**: melee species lunge with translate3d, impact at `hitFrame`; ranged species spawn their projectile sheet at `launchFrame` traveling right→left; on impact Blue plays hurt + red edge vignette + HP drain.

**Performance**: stage root `contain: layout paint style`; effects layer `contain: strict`; parallax transform-only with `will-change` toggled during travel; ≤6 concurrent animator rAF loops; `useStagePause` halts everything offscreen/hidden tab; reduced-motion snaps HP and skips travel/effects; terminal never re-renders from battle activity (refs + ≤2 state updates per command).

## 4. Backend — new `battle/` app + 5 fields, zero new per-command queries

Battle is a pure function over data the submit path already computes; the damage signal is `EvaluationOutcome.passed_rules` (repo distance-to-target), already produced by both submit paths.

**Migrations** (no new tables; all rows already loaded by `_run_with_active_attempt` / `RUN_HYDRATE_SELECT_RELATED`; writes piggyback existing `save(update_fields=[...])`):
- `adventures`: `AdventureQuestAttempt.battle_state` JSON, `AdventureQuest.encounter_spec` JSON (list).
- `challenges`: `ChallengeRun.battle_state` JSON, `ChallengeQuest.boss_spec` JSON, `ChallengeVariant.sabotage_script` JSON.

**`backend/battle/`**: `constants.py`, `state.py` (initial rosters; deterministic defaults when unauthored — e.g. `min(min_counted_commands,3)` 1-HP mobs, species cycled by `quest.sort_order`; boss max_hp = `min_counted_commands + 2`), `engine.py` (pure `BattleEngine.resolve_adventure_turn / resolve_challenge_turn: TurnInput → TurnOutcome{battle_state, events}`), `sabotage.py`, `payloads.py`, `tests/`.

**Turn rules**: diagnostics/non-git = free, no turn. Solved = finishing blow (all monsters/boss die; never a miss, never sabotage). HIT = counted+processed+`passed_rules` increased → 1 damage to front monster / the boss. MISS = failed git command or counted command with no new passing rule → one monster attacks (pure drama; the cost is the counted command itself — mana). Player defeat = existing budget exhaustion, surfaced as a `player_defeat` event. Boss max HP authored in `boss_spec` (default `min_counted_commands + 2`); regressions don't heal anyone — **HP lives on characters, the player's bar is mana** (user decisions 2026-06-13). `passed_rules` count is stored in `battle_state.passing_rules` so no re-evaluation of old states.

**Hook points**: `AdventureCommandService.submit` (after evaluate, before `attempt.save`). `CommandProcessingService.submit_command` in backend/practice/services.py (after evaluate, **before visualization** so sabotage shows in the DAG snapshot). **No new failure paths**: defeat IS the existing budget exhaustion on both surfaces (attempt fails → next quest in adventures; run fails in challenges); the engine just emits `player_defeat` when it happens.

**v1 numbers**: player mana = command budget (existing, unchanged); player attacks deal 1 damage; boss max HP authored or `min_counted_commands + 2` by default (finishing blow on solve kills regardless). Scores/mastery unaffected by battle in v1.

## 5. Sabotage engine (challenges)

Order per turn: apply player command → evaluate → if target matched: boss dies, **no sabotage** → else resolve hit/miss → if player survived (skip on defeat turn): apply sabotage → re-evaluate in memory (CPU-only) → build payload/visualization.

**Script schema** (on `ChallengeVariant.sabotage_script`):
```json
{ "schema_version": 1, "antagonist": "Riko",
  "entries": [{ "id": "stable-key",
    "trigger": {"every_n_turns": 2} | {"on": "miss"} | {"on_turn": 3},
    "max_times": 2,
    "preconditions": [{"type": "branch_exists", "branch": "main"}],
    "actions": [{"type": "commit_on_branch", "branch": "main", "message": "...", "files": {...}}],
    "narration": "Riko force-pushed over your branch again!",
    "recovery_commands": ["git reset --hard c1"] }] }
```
Mutators (all output passed through `RepositoryStateNormalizer`; commit ids prefixed `sab{n}` to avoid `c{n}` collisions): `commit_on_branch`, `dirty_working_tree`, `stage_files`, `move_branch_ref`, `create_branch`. Preconditions: `branch_exists/absent`, `commit_exists`, `working_tree_clean`. Fired-counts tracked in `battle_state.sabotage.fired`.

**Solvability**: sabotage allowed only on rules-mode specs (all challenge variants are). Seed-time validation in `--validate`: replay `solution_commands` with sabotage firing at authored worst case; if spec fails, append `recovery_commands` and require it to pass then. Authoring guidance: bump `max_counted_commands` by recovery length.

**Authoring**: additive `sabotage_script=` param on `variant()` and `boss=` on `level()` in [challenges.py](backend/curriculum/curriculum_v2/challenges.py); `encounter=` on adventure quest specs. **Hash-safe confirmed**: `StaticQuestVariantBuilder.semantic_key` (backend/practice/builders.py:233-244) hashes only quest slug + template + case_id. `antagonist` added to `ALLOWED_KEYS` in backend/practice/context.py. Two seed scripts to ship v1: "Scratch Gremlin" on `compose-clean-history` medium (scatters junk untracked files — tempts the forbidden `git add .`; orthogonal, no recovery) and "Riko" on `recover-history-safely` medium (on miss, dirties working tree + stages a panic fix; recovery = the official `git reset --hard c1`).

## 6. Response contract — `battle` block (both submit responses; initial state in run payloads, events only per-command)

```json
"battle": {
  "schema_version": 1,
  "monsters": [{"id": 0, "species": "slime", "tier": "mob", "hp": 0, "max_hp": 1, "alive": false}],
  "antagonist": "Riko",
  "events": [
    {"type": "player_attack", "skill": "commit", "target": 0, "damage": 1, "target_hp_after": 0},
    {"type": "monster_attack", "monster": 0, "cause": "miss"},
    {"type": "sabotage", "monster": 0, "narration": "...", "mutation_summary": ["staged hotfix.txt"]},
    {"type": "monster_death", "monster": 0},
    {"type": "encounter_cleared"},
    {"type": "player_defeat"}
  ]
}
```
No player HP in the block — **the player's mana bar renders from the run's existing counts** (`remaining_counted_commands` / `max_counted_commands`), which are already authoritative. Challenge boss = single `monsters` entry with `tier: "boss"` (one frontend code path). Monster HP values are `*_after` snapshots — frontend only animates toward authoritative numbers. Until the backend block ships, `deriveBattleEvents.ts` synthesizes events from `solved`/`result_category`/`objective_checks` deltas so the stage is demoable standalone.

## 7. Adventure layout integration ([AdventureSession.tsx](frontend/src/features/command-adventures/components/AdventureSession.tsx))

- Remove `<AdventureProgressBar>` from the header (lines 113–115).
- Insert `<AdventureBattlePanel className="h-44 shrink-0 max-lg:h-36" …/>` as the **first child of the right section (line 149) — the uppermost element of that column, directly above the terminal**. The sidebar keeps its full height beside it. Sky + clouds + ground; Blue left, monsters right; **progress bar renders in the panel's `groundFooter` slot, flush under the ground line** (slim `variant="battle"` restyle; mastery pips become path distance-markers). Collapsible to a slim HP-only bar (same mechanism as challenge) for short viewports.

```
┌──────────────────────────────────────────────┐
│ header (back · title · command budget)       │
├───────────────┬──────────────────────────────┤
│ brief         │ sky ☁  blue ⚔ monsters  ☁    │
│               │ ─────────── ground ───────── │
│ mastery       │ ▓▓▓▓░ progress (below gnd) ░ │
│               ├──────────────────────────────┤
│ files         │ terminal                     │
│               │                              │
│               │ hints                        │
└───────────────┴──────────────────────────────┘
```
- `onCommand` → `director.onCastStart(cmd)` then `submitCommand.mutate(cmd, { onSuccess: r => director.onResolve(r.battle ?? derive(r)), onError: director.onError })`.
- Quest advance: panel watches `current_quest_index`/`attempt.id` → run-right travel sequence to the next encounter.

## 8. Challenge layout + DAG integration ([ChallengeWorkspace.tsx](frontend/src/features/challenges/components/ChallengeWorkspace.tsx))

- `<ChallengeBattleStrip>` as the **first child of the right section (before `diagramGridRef`, line 444) — the uppermost element of that column, spanning its width above the DAG row**. The sidebar keeps its full height beside it. `workspaceGridStyle` (line 380) gains a leading row: `${battleOpen ? '10.5rem' : '2.25rem'} …` — collapsed state shows a slim HP-only bar (actors paused), persisted like other panel prefs. Single static arena (no travel), boss at 1.5–2× scale.
- **Sabotage staging**: cache lands the sabotaged snapshot immediately, so add `useDeferredSnapshot(snapshot, holdWhile)` — Current DAG (only) keeps showing the previous snapshot until the director's sabotage step releases it after the boss attack lands (safety timeout ~1.5s force-releases). Terminal/files/Target DAG stay live.
- **LiveDagPanel animation upgrades** ([LiveDagPanel.tsx](frontend/src/shared/practice/components/LiveDagPanel.tsx), ~80 lines TS + 50 CSS, no library change): snapshot diff (`usePrevious`) drives CSS classes — new-node pop-in (scale .55→1.06→1 + glow), edge draw-in (`stroke-dashoffset`), sabotage container shake + red flash on changed/removed nodes (via `sabotagePulse` prop), branch-pill slide-up on ref moves.

## 9. Effects registry (per git skill)

`effectRegistry.ts`: `command_family → BattleEffect { cast(ctx: {layer, from, to, tier}): Promise<void> }` — DOM nodes animated with WAAPI (transform/opacity only), promise resolves at impact for queue chaining. Keys: commit, add, branch, merge, rebase, push, pull, reset, stash, clone, default (cyan bolt).
- **commit — Seal of Record**: amber rune disc arcs and spins into the target, shockwave on impact.
- **merge — Converging Streams**: cyan+violet streaks on mirrored paths meet exactly at the target in a white burst.
- **push — Repulsor Wave**: three staggered chevrons sweep across; target gets a 10px knockback nudge before hurt. `pull` reuses mirrored.
- Generic `SpriteProjectile` (one mover, many skins): reuses `projectiles/*.png` hue-rotated per family (used by rebase + ranged monsters).

## 10. Build order (each phase demoable)

| Phase | Work | Demo |
|---|---|---|
| 0 | Asset reorg script + deletions; `monsters.ts`; stitch `float_book.png`; register summon/cast/hurt; `/dev/battle` playground | Any monster cycles all anims; Blue summons book |
| 1 | SpriteAnimator segment API; PlayerActor cast-latency sync (fake latency slider); HealthBar; MonsterActor | Full cast cycle synced to simulated latency |
| 2 | battleQueue + useBattleDirector + BattleStage/Parallax; `deriveBattleEvents`; AdventureBattlePanel + layout diff; travel on quest advance | Adventure fully playable as battle (client-derived events) |
| 3 | Backend: `battle/` engine + adventure migration/hook/payload; defeat-fails-attempt; frontend prefers `response.battle` | Authoritative adventure battle |
| 4 | Backend: challenge migration/hook, boss HP from rules, defeat failure; ChallengeBattleStrip + grid diff; deferred snapshot; DAG animations | Boss fights, HP real |
| 5 | Sabotage engine + seed validation + 2 authored scripts + `antagonist`; sabotage choreography → DAG shake | Scenario-coherent sabotage |
| 6 | Effects registry filled out; stage pause/perf/reduced-motion audit; collapsed strip; number tuning | Polish |

## 11. Verification

- **Backend**: new `backend/battle/tests/` (engine turn matrix, sabotage triggers/mutator normalization/`sab*` id safety, deterministic default rosters); extend `backend/challenges/tests/test_challenge_curriculum.py` (seed round-trip, solvability validation, miss→attack→HP-0 failure, sabotage visible in visualization, victory suppresses sabotage) and adventure run tests (battle block shapes, par play takes zero damage, defeat opens next attempt). Run `python backend/scripts/profile_command_latency.py` after phases 3–4 to prove zero new queries.
- **Frontend**: `/dev/battle` playground for every sprite/segment/effect; then run the app (existing practice/CI test suites + lint) and play one adventure + one challenge end-to-end — verify cast syncs to real latency, fast-forward coalescing on rapid submits, sabotage boss-attack-then-DAG-update ordering, progress bar under the ground line, collapsed strip, reduced-motion mode.

## Critical files

- frontend/src/shared/sprites/SpriteAnimator.tsx, characters.ts
- frontend/src/features/command-adventures/components/AdventureSession.tsx
- frontend/src/features/challenges/components/ChallengeWorkspace.tsx
- frontend/src/shared/practice/components/LiveDagPanel.tsx
- backend/adventures/services.py · backend/practice/services.py (submit hot paths)
- backend/practice/builders.py (frozen semantic_key — additive keys only)
- backend/curriculum/management/commands/seed_curriculum_v2.py
- backend/curriculum/curriculum_v2/challenges.py · adventure_quests.py
