# Curriculum Waves and Repetition Implementation Plan

**Intent:** Turn every adventure difficulty tier's waves from repeated draws out of one shared pool into a designed sequence. Each command form is introduced with full support, practiced right after its command guide, and revisited in later levels. The guides actually fire, every tier clear pays GitCoins, and the whole curriculum takes about as long as today.

**Current Behavior:** A tier's waves are the rounds the level map counts ("Medium ★★★ 2/2", `wave_progress`). Under the hood they are N clears (`required_successful_attempts`, 1–3) of one shared pool of 3–5 variants, and each round draws a different scenario. The rounds are interchangeable draws, not a designed sequence. In mixed pools, draw order (alphabetical by case ID) decides which form a learner practices. Each form's rounds are massed in one tier and then dropped.

On the default path, 19 command forms first appear at Medium (10) or Hard (9), where feedback or the Expected State diagram has already faded. Five forms (setup `init`/`clone` aside) are never used again after first use. Tier completion credits mastery for every form of the level's command families, which silently suppresses later guides. The guide resolver lets placeholders swallow `--abort`/`--continue`. Only the first Easy clear of a level pays GitCoins.

**Expected Outcome:** The 21 levels and the command each teaches are unchanged. Each tier holds 2–3 ordered waves (132 in total), and each wave has one role: debut, practice, compose, spiral or transfer. A run plays the learner's next uncleared wave, and the tier completes on its last wave. The level map keeps its n/n wave counter; it now counts these designed waves. Placement rules:
- No option debuts at Hard.
- Every variant in a wave uses whatever that wave debuts.
- Core workflow forms recur in at least two later waves, including one later level; specialized forms recur at a harder tier.

A learner who never fails finishes all four modules in about 4.9 hours, close to today's 4.7. Guides fire for the form the problem needs, whatever the learner cleared before. Every tier's first clear pays GitCoins on a difficulty ladder that is visible before play.

**Target-Perspective Output:** A learner opens *Pushing to a Remote · Easy* and sees "Wave 1 of 2 · Publish a branch".
1. They get the `git push` guide and clear the wave.
2. The outcome reads "Wave 1 of 2 cleared — next: Publish and track".
3. Wave 2 shows the `git push -u` guide, even for an account that cleared earlier levels.
4. They use `push -u` again unguided in Medium wave 1, and once more in Module 4.

Clearing Medium shows "+35 GitCoins", and the reward is visible on the tier before they start. Teammates see the same 21 levels, in the same order, teaching the same commands.

**Truth Owner:**
- **Placement:** a new authored wave plan, `backend/curriculum/seed_data/source/wave_plan/`. It decides level, tier, wave, order and role.
- **Learner-facing scenario content:** `backend/curriculum/seed_data/scenario_bank.json`, compiled from the team's bank Markdown plus `source/wave_scenarios.md`.
- **Repository fixtures:** the existing inline fixtures for the 265 legacy scenarios, plus `backend/curriculum/seed_data/source/scenario_fixtures/` for new IDs.
- **Per-player wave progress:** `AdventureLevelTierProgress.cleared_wave_slugs`.
- **Reward amounts:** one ladder in `backend/adventures/rewards.py`.

**Contract Boundary:** The seed writes ordered `AdventureLevelTierWave` rows, each with the level's `command_forms` and ordered variants. From there:
- `AdventureLevelTierRunService.start_run` picks the next wave and rotates variants within that wave.
- `AdventureLevelTierCommandProcessingService._complete_run` handles wave clear → tier completion → stars, mastery and rewards.
- The tier run payload carries `progress` + `next_wave` + `reward`; the level-map tier payload carries `wave_progress` + `reward`.
- Generated OpenAPI types feed TierWorkspace, TierOutcomeModal and the level map.

**Cutover:** The ordered-wave runtime treats today's shape (one wave needing N clears) as a degenerate case, so it ships first with no content change. Modules then move to the wave plan one at a time (1 → 4). Superseded single waves (`{level}-{difficulty}`) and their variant rows are unpublished, never deleted, because runs reference them through PROTECT. Existing completions are kept, and partial progress maps onto the first waves.

**Displaced Path:**
- one-wave-per-tier seeding and `required_successful_attempts` repetition
- tier-wide variant rotation, and first pick by alphabetical slug
- placement by position in `apply_scenario_bank` (kept only to join the 265 legacy fixtures)
- level forms attached by whole command family
- mastery credit for unused forms
- placeholder-matches-option resolution
- Easy-only coin award from `AdventureLevel.reward_coins`

**Value Density:** One placement owner and a contained runtime change restructure all 21 levels. Every existing scenario stays in play. Three small tutoring fixes and 11 form registrations restore guides the curriculum already relies on. One reward ladder fixes rewards everywhere at once.

**Acceptance Evidence:**
1. The wave-plan invariant suite passes on the real resolver (placement, debut, reuse and time-budget rules).
2. All 349 canonical solutions replay through the real simulator and satisfy their evaluation.
3. A disposable fresh account and a "veteran" account in the running app show the wave flow, guides and rewards above, captured per module.
4. Reseeding is idempotent and publishes exactly the planned waves and variants.
5. The KPI service reports every measure on post-cutover runs, and runs are attributable to old or new waves by slug.

**Evidence Lane:** pytest (backend unit and integration), invariant suite, `generate_targets` plus replay/evaluator audit, vitest, an agent-browser walk on disposable accounts, CI guards.

**Kill Criteria:**
- After the Module 4 cutover, no published tier wave has `required_successful_attempts > 1`, and the field is retired.
- No seed path builds a wave from a tier's case pool.
- `apply_scenario_bank` decides no placement.
- No tier variant query lacks a wave filter.
- No tier reward reads `AdventureLevel.reward_coins`.
- The one-time backfill command is deleted after the deploy that runs it.

**Architecture Slice:** wave plan + bank + fixtures → `seed_curriculum` → tier wave/variant rows → `tier_runs` / `tier_variants` / `tier_command_processing` → `tier_payloads` / `adventure_access` → OpenAPI → story-map tier UI. The tutoring planner reads wave forms.

**Plan Review Gate:** Requires PRE review before execution.

---

## 1. Fixed constraints

- **Fixed (teammates):** the 21 levels, their order and slugs, and the command each level teaches. `progress/objectives.py` keys per-SO CAR by these level slugs, so they must not change.
- **Flexible:** waves, variants, and the tier at which each command form appears.
- **Time:** the team accepted about 4.9 hours for a no-fail path through Modules 1–4 (2026-10-20). Any wave added later must be re-measured (§4).
- **Untouched:** Module 0 orientation lessons, Squire's Drill as a feature, scaffolding ladders, the star formula (`adventures/scoring.py`), and KPI formulas. Challenges were out of scope until D10–D11 added the module Challenge Gates (§14).

## 2. Diagnosis (evidence gathered while planning)

| # | Finding | Evidence |
|---|---|---|
| 1 | The waves the map counts (n/n) are clears of one shared pool: a single `AdventureLevelTierWave` row needing N clears (Modules 1–2: 3 Easy / 2 Medium / 2 Hard; Module 4: 2/1/1), each clear drawing a different variant. Example: Clone Easy's three waves draw `clone-easy-api-lab`, `clone-easy-corp`, `clone-easy-docs-portal`, so a first-time learner never meets `clone -b` at Easy. | `seed_curriculum.py` `_seed_tier` ("One wave per tier"); `tier_variants.py` rotation; `adventure_access.py` `wave_progress` |
| 2 | The runtime only ever plays the first published wave row, and variant rotation is tier-wide. Seeding more wave rows today would do nothing. | `tier_runs.py` `_published_wave`; `tier_variants.py` `_published_variants` / `_tried_variant_keys` filter by tier |
| 3 | First pick is the alphabetically first case ID, not the authored order. A first-time learner gets 1.2.2 (`clone-easy-api-lab`) before 1.2.1, and 2.1.4 before 2.1.1. | variants ordered by `semantic_key` (= case ID) |
| 4 | On the default path, 19 forms first appear at Medium (10) or Hard (9): e.g. `push -u` (M), `--force-with-lease` (H), `stash drop` (H), `branch -d` (H), `branch -D` (H), `git config` (H), `cherry-pick --abort` (H), `reset --hard` (H). Four more exist only in Hard pools (`merge --abort`, `cherry-pick -x`, `cherry-pick --continue`, `rebase --continue`). | resolver-based walk of all 265 scenarios |
| 5 | After first use, `git branch <name>`, `cherry-pick --no-commit`, `cherry-pick --abort`, `rebase --onto` and `reset --hard` are used 0 more times on the default path. `push -u`, `--force-with-lease`, `stash drop`, `branch -D` and `fetch --prune` get 1 more use, massed in the same tier. | same walk |
| 6 | **Guides silently suppressed.** Completing a tier credits mastery for *every* form of the level's command families. The planner then treats them as known. Verified on a seeded test database: after clearing the earlier Easy tier, a veteran account got **no guide** for `git add -p`, `git push -u`, `--force-with-lease`, `git merge --squash` or `git stash pop`; a fresh account got each one. | `tier_command_processing.py` `_credit_mastery`; `seed_curriculum.py` `_level_skill_slugs`; `tutoring/services/planner.py` `lesson_is_known` |
| 7 | **Guides swallowed or bare.** A placeholder matches an option token, so `git rebase --abort`, `git rebase --continue`, `git merge --abort` and `git cherry-pick --continue` resolve to the already-known base form and never get their own guide. A fresh install publishes only the 48 Module forms. So `git mergetool`, `git config`, `git cherry-pick -x`, `git commit --no-edit`, `git branch <name>`, `git rebase --onto` and `git reset --hard` get a guide titled only "git &lt;command&gt;", with no summary. | `tutoring/services/forms.py` `command_matches_form`; resolver probe after `seed_curriculum` + `seed_command_library` |
| 8 | **Wrong level forms.** *Using a Merge Tool* attaches only `git merge <branch>` and `git commit [-m <message>]`, never `git mergetool`, so its drill and mastery skip the level's own command. *Creating and Switching Branches* attaches `branch -d` / `-D`, which it doesn't teach. | seeded database probe |
| 9 | Placement is positional. `apply_scenario_bank` pairs the 265 bank entries to seed slots by order and requires exactly 265. | `scenario_runtime.py` |
| 10 | **Rewards.** GitCoins (25) are paid once per level, only on the first **Easy** clear. Medium and Hard pay 0, and chapter chests count Easy completions only. The tier workspace never shows a reward. | `tier_command_processing.py` (`first_level_clear`), `curriculum/selectors/progress_counts.py`, `TierStatsBar.tsx` |
| 11 | Simulator: merge and cherry-pick conflicts stop, and `git pull` reuses the merge path. `git rebase` never stops on a conflict, so continue/abort scenarios must start mid-rebase. Chaining commands inside a freshly cloned folder is unproven. | `frontend/src/shared/git/simulator/commands/merge.ts`, `remote.ts`, `revisedScenarioWorkflows.test.ts` |

## 3. Wave grammar (the rules the seed must satisfy)

Roles: **debut**, **practice**, **compose**, **spiral**, **transfer** (defined in [WAVE_MAP.md](WAVE_MAP.md)).

1. **Debut early.** A new option, subcommand or technique debuts at Easy, or at Medium for a level's advanced form. Never at Hard. A form whose parts are all already known (plain `git init`; `clone --depth … -b …`) may first appear anywhere.
2. **Debut in every variant.** Whatever a wave debuts, every variant of that wave uses it, so the guide's lesson survives any retry rotation.
3. **Guide, then independent use.** Every debut is used again later in the same level, at the same or a harder tier.
4. **Spaced reuse.** Core workflow forms (add, commit, amend, restore, switch, branch, stash, push, fetch, pull, merge) reach at least two later waves, including one later level. Specialized forms reach at least one harder tier. Each exact guide form is reused at least once. Setup forms (`init`, `clone`) are exempt.
5. **Same skill per wave.** Variants share the wave's focus. Other forms they use are already known.
6. **Shape.** 2–3 waves per tier, one clear per wave, at least 2 variants per wave. Expect 6–8 runs per level; tier command budgets stay 12/10/8.
7. **Diagnostics never debut.** `status`, `log`, `show`, `reflog` and `diff` may appear anywhere.
8. **Never repeat scenarios.** No two variants share both an initial state and a target. This extends the existing Module 3–4 test to every module.
9. **Time budget.** The no-fail path stays near today's, about 4.9 hours against 4.7, measured with the §4 model. Re-measure before adding waves.

## 4. Time budget

Measured on the default path: a learner who never fails, playing today's required clears in rotation order versus the first variant of every planned wave. Estimated time uses 1 min per run (brief and outcome), 0.4 min per typed command, 1 min per file edit, and 0.5 min per first-time guide. Retries add time to both columns roughly alike.

| | Today | This plan |
|---|---:|---:|
| Runs | 137 | 132 |
| Commands typed | 265 | 305 |
| File edits (conflicts) | 17 | 17 |
| Command guides | 43 | 48 |
| Estimated time, no failures | ~4.7 h | ~4.9 h |
| New scenarios to write | — | 84 |

| Module | Today | This plan |
|---|---:|---:|
| 1 Local Repository Foundations | ~71 min | ~70 min |
| 2 Branching and Collaboration | ~117 min | ~113 min |
| 3 Conflict Resolution | ~65 min | ~64 min |
| 4 Advanced Recovery and History | ~28 min | ~49 min |

Modules 1–3 stay about the same length: their identical repeats are replaced by distinct debut, practice, review and transfer waves. Module 4 grows the most, because today it introduces five recovery flags at Hard with almost no practice. A trimmed 93-wave variant (~3.5 h, 43 new scenarios) was evaluated on 2026-10-20 and set aside as too thin; ~4.9 h fits the team's window.

## 5. The new curriculum at a glance

The full per-wave tables, the 49 tier moves, the reuse table and the specs for all 84 new scenarios are in [WAVE_MAP.md](WAVE_MAP.md). The readable curriculum blueprint is in [blueprint/](blueprint/README.md): one file per module, with each level's outcomes, commands, waves and new scenarios. It is generated from the same data.

| Level | Waves E/M/H | Runs today → plan | New | What changes |
|---|---|---|---:|---|
| 1.1 Init | 2/2/2 | 5 → 6 | 1 | Named-folder init moves to Easy. Safe re-run gets a partner. |
| 1.2 Clone | 3/2/2 | 7 → 7 | 2 | Easy debuts URL, folder and `-b` in turn. Shallow debuts at Medium. |
| 1.3 Add + commit | 2/2/2 | 7 → 6 | 2 | Medium spiral: `init → add → commit` first snapshot. |
| 1.4 `add -p` | 2/2/2 | 7 → 6 | 4 | Hunk plus whole file (spiral). Split one file into two commits. |
| 1.5 `--amend` | 2/2/2 | 7 → 6 | 4 | Amend in one hunk (spiral, `add -p`). Fix message, then a new commit. |
| 1.6 Restore | 2/2/2 | 7 → 6 | 5 | Discard debuts at Easy. Unstage-then-commit. Module 1 capstone. |
| 2.1 Switch | 2/2/2 | 7 → 6 | 3 | `git switch <branch>` debuts at Easy, not Hard. `git branch <name>` at Medium. |
| 2.2 Naming | 2/2/2 | 7 → 6 | 4 | `branch -d` debuts at Easy, not Hard. Spiral: restore + branch + commit. |
| 2.3 Stash | 2/2/2 | 7 → 6 | 4 | `pop` debuts at Easy, `drop` at Medium (today Medium and Hard). |
| 2.4 Push | 2/2/2 | 7 → 6 | 4 | `-u` at Easy, `--force-with-lease` at Medium. Spirals: branch → commit → `push -u`; amend → lease. |
| 2.5 Fetch/pull | 2/2/2 | 7 → 6 | 4 | Pull at Easy. Spirals: pull → branch; stash → pull → pop. |
| 2.6 Reconcile | 2/2/2 | 7 → 6 | 2 | Fetch + merge debuts at Easy. Spiral: unstage, commit, pull, push. |
| 2.7 Merge | 2/2/2 | 7 → 6 | 4 | `--no-ff` at Easy. Spirals: commit → land; land → push → tidy. |
| 2.8 Squash | 2/2/2 | 7 → 6 | 4 | `branch -D` debuts at Easy, not Hard. Spirals add push and switch. |
| 2.9 Remote branches | 2/2/2 | 7 → 6 | 4 | Prune at Easy. Module 2 capstone (fetch, land, publish, retire, prune). |
| 3.1 Manual conflicts | 3/2/2 | 8 → 7 | 5 | `merge --abort` debuts at Easy, not Hard. Spiral: a pull that conflicts. |
| 3.2 Merge tool | 2/2/2 | 6 → 6 | 2 | `git config` debuts at Medium, not Hard, and reappears at Hard. |
| 3.3 Cherry-pick | 3/3/2 | 8 → 8 | 8 | `-x` and `--no-commit` at Easy; `--continue` and `--abort` at Medium. Each is reused at a harder tier. |
| 4.1 Reflog recovery | 2/2/2 | 4 → 6 | 4 | Spirals: recover → `push -u`; bookmark with `git branch <name> <commit>` → cherry-pick to main. |
| 4.2 Revert | 2/2/2 | 4 → 6 | 6 | Spirals: pull → revert; revert on a release branch; amend local, revert pushed. |
| 4.3 Rebase recovery | 3/2/3 | 4 → 8 | 8 | `--abort` and `--continue` at Easy; `--onto` and `reset --hard` at Medium. Each reused at Hard, with `--force-with-lease`. |

## 6. Runtime design: ordered waves

The learner-facing wave counter (`wave_progress`, shown as "n/n" and "N waves") keeps its shape and meaning: one wave is one round you clear. What changes is that each round is its own authored wave, with its own purpose and variants, instead of another draw from a shared pool.

**Data (two small migrations):**
- `AdventureLevelTierProgress.cleared_wave_slugs`: a JSON list of wave slugs. Slugs are authored and stable across reseeds. `successful_clears` keeps incrementing for compatibility.
- `AdventureLevelTierWaveVariant.sort_order`: ordering becomes `(sort_order, semantic_key, id)`. The seed writes the wave plan's order, so the authored first variant is the first pick.

**Start (`tier_runs.start_run`):**
- The wave is the first published wave, by `sort_order`, that is not in `cleared_wave_slugs`.
- Variant candidates, tried keys and `last_shown_variant` are all scoped to that wave. `last_shown_variant` is ignored when it belongs to another wave.
- Retry-after-failure linking is unchanged: the failed wave is still the next uncleared one.
- Replay of a completed tier cycles waves in order, starting after the wave of the learner's latest replay run, and only ever selects published variants. This displaces `_replay_variant` reopening the completion's variant.

**Solve (`tier_command_processing._complete_run`):**
- A non-replay solve adds the wave slug to `cleared_wave_slugs`.
- A wave whose `required_successful_attempts` is N needs N clears. This is today's degenerate case, kept until the Module 4 cutover.
- The tier completes when every published wave slug is cleared. Completion stars = the lowest of each wave's best stars (decision D3).
- Mastery is credited per wave clear (§7). Rewards follow the ladder (§8).

**Payloads:**
- `progress_payload` returns `{completed, total, cleared, next_wave: {index, title} | null}`, counted over published waves.
- `adventure_access` derives `wave_progress` from published waves and `cleared_wave_slugs`. Its shape is unchanged.
- `tier_run_payload` adds `wave: {index, total, title}` for the workspace header.

**Frontend:**
- TierOutcomeModal: the partial-clear copy becomes "Wave N of M cleared — next: <title>", plus the reward hint.
- TierStatsBar: shows "Wave N/M" and the tier reward.
- Level map: tier chips show the reward. `StoryAdventurePanels` already reads `wave_progress`.

**KPIs:** A run stays one scenario, so SCR, CAR, HLCR, ARC and RTA keep their definitions. RTA gets cleaner, because retries rotate within a single-skill wave. Pre-cutover runs reference the old `{level}-{difficulty}` wave slugs, which separates the two periods. Following the precedent in `deploy/MODULE4_VARIANT_RESEED.md`, report the periods separately. Each learner's default path has 43 Hard runs instead of 39.

## 7. Command-guide fixes

1. **Resolver:** a placeholder never matches a token that starts with `-` unless the pattern token is that option. `git rebase --abort` then resolves to its own form; `git switch -c x c1` and every current solution still resolve as before. Add a test that maps every solution command in the curriculum to its expected teaching key.
2. **Mastery credit:** credit only the published forms that the solving run's processed commands actually used (`FormGuide.used_by`), on each non-replay wave clear. Resolve them against every module's forms, so spiral reuse credits the original form. (`form_solve_targets` already counts published tier waves; no change needed there.)
3. **Level and wave forms:**
   - Level forms are the level's own-chapter forms used by its non-spiral waves. That drops `branch -d` / `-D` from *Creating and Switching Branches* and puts `git mergetool` into the merge-tool drill.
   - Each wave attaches the level's forms. Drills read wave forms too, so review waves must not pull other levels' commands into a drill.
4. **Register the 11 missing forms** in `MODULE_COMMAND_FORMS` (decision D5). They appear in the Chapter Book under their module.
   - Module 2: `git branch <branch> [<start-point>]`
   - Module 3: `git commit --no-edit`, `git mergetool`, `git merge --abort`, `git config <key> <value>`, `git cherry-pick -x <commit>`, `git cherry-pick --continue`
   - Module 4: `git rebase --onto <newbase> <upstream> [<branch>]`, `git rebase --abort`, `git rebase --continue`, `git reset --hard <commit>`

   Module 3's registered `git commit [-m <message>]` (complete-merge) never matches the authored `--no-edit` solutions. `git commit --no-edit` replaces it.

## 8. GitCoin rewards

**Ladder and payouts:**
- `backend/adventures/rewards.py` holds the ladder: `TIER_REWARD_COINS = {"easy": 25, "medium": 35, "hard": 50}` (decision D1). Easy stays at 25, so the first companion (150) arrives at the same pace.
- A tier pays once, on first completion of all its waves, and never on a replay. Waves don't pay individually ("no free dopamine", PRODUCT.md), but the outcome modal says what the remaining waves unlock.

**Award keys:** Easy keeps `adventure-level-reward:{level.id}`, so nobody is paid twice. Medium and Hard use `adventure-tier-reward:{tier.id}`.

**Display:** tier payloads (map and run) expose `reward: {coins, claimed}`. TierStatsBar and the level-map tier chip show it, and the existing "+N GitCoins" outcome line now also appears for Medium and Hard.

**Backfill:** a one-time idempotent command credits Medium/Hard completions that predate the ladder, using the same keys. Delete it after the deploy that runs it.

**Not changed here:** chapter chests still count Easy completions only (decision D8). Module 0 lessons and Squire's Drill stay unpaid by design (ARCHITECTURE.md). The shop sells only 450 coins of companions, so payouts already exceed sinks; the ladder only changes who earns them.

## 9. Architecture map

**Files to create:**
- `backend/curriculum/seed_data/source/wave_plan/` — `__init__.py` (exports `MODULE_WAVE_PLAN`), `types.py` (`WaveSpec`, roles), `module_1.py` … `module_4.py`, each under 700 lines
- `backend/curriculum/seed_data/source/scenario_fixtures/` — `module_1.py` … `module_4.py`, the runtime fixtures for new IDs
- `backend/curriculum/seed_data/source/wave_scenarios.md` — the 84 new scenarios, in the team's Markdown scenario format
- `backend/adventures/rewards.py`
- `backend/curriculum/tests/test_wave_plan_invariants.py` (the §3 rules, including the time budget), plus focused runtime, tutoring and reward tests
- `deploy/CURRICULUM_WAVES_RESEED.md` (runbook)
- adventures migrations for `cleared_wave_slugs` and variant `sort_order`

**Files to modify:**
- `backend/curriculum/management/commands/seed_curriculum.py` (`_seed_tier`; level forms per §7.3; `MODULE_COMMAND_FORMS` per §7.4)
- `backend/curriculum/seed_data/scenario_runtime.py` (case registry; positional join limited to `LEGACY_SLOT_IDS`)
- `backend/curriculum/seed_data/scenario_bank.json` (compiled output: the team's 265 plus the 84 from `wave_scenarios.md`)
- `scripts/curriculum/import_revised_scenarios.py` (compile the team's bank Markdown plus `wave_scenarios.md`; reject ID collisions; derive counts instead of hard-coding them)
- `backend/curriculum/management/commands/generate_targets.py` (walk the registry)
- `backend/adventures/models.py`
- `backend/adventures/services/tier_runs.py`, `tier_variants.py`, `tier_command_processing.py`, `selectors.py` (`form_solve_targets`)
- `backend/adventures/tier_payloads.py`
- `backend/curriculum/selectors/adventure_access.py`
- `backend/tutoring/services/forms.py`
- generated `generated_targets.py` / `generated_trajectories.py` (regenerate only)
- `frontend/src/shared/api/generated/*` (regenerate only)
- `frontend/src/features/story-map/components/TierOutcomeModal.tsx`, `tier-workspace/TierStatsBar.tsx`, `path/StoryAdventurePanels.tsx`, and their types and tests
- root docs: `CONTENT_AUTHORING_GUIDE.md`, `CURRICULUM_AUTHORING_PLAN.md`, `ARCHITECTURE.md` (Command Introductions, Squire's Drill, rewards), `backend/curriculum/seed_data/README.md`

**Files to avoid:**
- historical migrations
- the retired multi-story fixtures (`stories.py`, `chapters.py`, `lessons.py`, `source/blueprint/`, `source/adventure_level_specs/`)
- challenge content, scaffolding ladders, star formula and KPI formulas
- hand edits under `seed_data/generated/` or `frontend/src/shared/api/generated/`

**Source of truth:** wave plan (placement), bank (content), fixtures (state), progress row (per-player waves), ladder (coins).

**Read path:** `seed_curriculum` and `generate_targets` read the plan, the bank and the fixture registry. Runtime reads only the seeded rows.

**Write path:** the seed upserts waves and variants by `(tier, slug)` and `(wave, slug)` and unpublishes displaced rows. The runtime writes progress, completion, mastery and wallet rows.

**Contract boundary:** see header. API changes go through `python scripts/generate_api_contract.py` and its guards.

**Integration points:** tutoring planner (wave forms), drills (`seed_drills` reads level and wave forms), KPI service (runs), chapter progress (Easy completions), admin console (run/variant listings).

**Migration/cutover:** per module, as in §10.

**Acceptance evidence gate:** Task 10.

## 10. Cutover and data policy

1. **Order:** Tasks 1–3 ship without content changes. Every tier is still one wave, and behavior is identical except fixed guides, registered forms, ladder rewards and correct first picks. Then Modules 1 → 4 cut over one deploy at a time. Each cutover reseeds through `seed_all` on startup (`deploy/render-api/start.sh`).
2. **Completed tiers stay complete.** New waves are playable as free play.
3. **Partial progress** (clears without a completion) maps onto the first `min(clears, waves − 1)` waves, through the one-time backfill (decision D2). It never completes a tier the learner hasn't finished.
4. **In-flight runs** on a superseded wave can still finish. A solve then counts as clearing wave 1.
5. **Historical rows:** superseded waves and variants are unpublished, never deleted.
6. **Runbook:** `deploy/CURRICULUM_WAVES_RESEED.md` records the module, its waves, the backfill invocation and the KPI period boundary, mirroring `deploy/MODULE4_VARIANT_RESEED.md`.

## 11. Tasks

### Task 0 — Simulator spike for the new scenario shapes
**Files:** frontend simulator tests only (`frontend/src/shared/git/simulator/*.test.ts`).
**Scope:** confirm each shape below, or record the gap:
- `git pull` stops on a content conflict (3.1 Medium spiral).
- `git pull` refuses when local edits overlap incoming changes; otherwise stash → pull → pop (2.5 Hard spiral) is optional and must be redesigned.
- `git init -b main` in a folder that already has files, followed by add/commit (1.3 Medium spiral).
- `git add -p` then `git add` on the same file (1.4 Hard compose).
- Starting states for a stopped merge, a stopped cherry-pick and a stopped rebase, and `push --force-with-lease` after `rebase --continue`.
- `git stash drop stash@{0}` then `pop`.

**Output:** a table of supported vs. gap, plus a fix task or redesign for each gap, before any affected scenario is written.
**Verification:** `cd frontend && npx vitest run src/shared/git/simulator`.
**Acceptance evidence:** each shape replays to the intended state.
**Parallel:** yes, with Tasks 1–2.

### Task 1 — Command-guide fixes and form registration
**Files:** `tutoring/services/forms.py`; `adventures/services/tier_command_processing.py` (`_credit_mastery` only); `adventures/services/selectors.py`; `seed_curriculum.py` (`MODULE_COMMAND_FORMS`, level form derivation); tests.
**Scope:** §7.
**Expected output:**
- After clearing *Staging and Committing* Easy, a veteran account still gets the `git add -p` guide in *Partial Staging* Easy.
- `git rebase --abort` gets its own labeled guide.
- *Using a Merge Tool* attaches `git mergetool`, and its drill can quiz it.
- The Chapter Book lists the 11 new forms under their modules.

**Verification:** `cd backend && python -m pytest tutoring/tests adventures/tests curriculum/tests drills/tests -q`, plus the new regression tests built from this plan's probes (fresh vs. veteran guide; resolver keys for every solution).
**Acceptance evidence:** the veteran-guide regression test, and a browser check on a disposable veteran account.
**Parallel:** with Tasks 0 and 2. Task 2 touches only the reward block of `tier_command_processing.py`. Integration proof comes after both.

### Task 2 — GitCoin ladder, display and backfill
**Files:** `adventures/rewards.py`; `tier_command_processing.py` (reward block); `tier_payloads.py`; `curriculum/selectors/adventure_access.py`; OpenAPI regeneration; `TierStatsBar.tsx`, `TierOutcomeModal.tsx`, `StoryAdventurePanels.tsx`; a one-time command `award_missing_tier_rewards`; tests.
**Scope:** §8.
**Expected output:** the first Medium or Hard completion pays its ladder amount once. Easy keeps its legacy key. The reward is visible before play. The backfill is idempotent.
**Verification:** `python -m pytest adventures/tests progress/tests -q`; `cd frontend && npx vitest run src/features/story-map`; `python scripts/check_api_contract.py`; `python scripts/check_api_type_adoption.py`.
**Acceptance evidence:** a disposable account clears a Medium tier, the outcome shows "+35 GitCoins", and the wallet ledger has one `adventure-tier-reward:{id}` row. A second clear adds nothing.
**Parallel:** with Tasks 0–1.

### Task 3 — Ordered-wave runtime (no content change)
**Files:** `adventures/models.py` and migrations; `tier_runs.py`; `tier_variants.py`; `tier_command_processing.py` (`_complete_run`); `tier_payloads.py`; `adventure_access.py`; OpenAPI regeneration; tier workspace UI copy; tests.
**Scope:** §6.
**Expected output:** a single-wave tier needing 3 clears behaves exactly as today. A seeded three-wave test tier walks its waves in order, rotates variants within each wave, completes on the last wave, and replays by cycling waves.
**Verification:** `python -m pytest adventures/tests common/tests curriculum/tests -q`; `python manage.py makemigrations --check --dry-run`; vitest; API contract guards.
**Acceptance evidence:** a degenerate-case equivalence test, a multi-wave walk test, and the payload contract tests.
**Parallel:** no. It runs after Tasks 1–2 because it shares `tier_command_processing.py`.

### Task 4 — Wave plan owner and seed composition
**Files:** `source/wave_plan/`; `source/scenario_fixtures/`; `source/wave_scenarios.md`; `scenario_runtime.py` (registry; `LEGACY_SLOT_IDS`); `seed_curriculum.py` (`_seed_tier` → planned waves; each wave attaches the level's forms; variant `sort_order`; unpublish displaced rows); `generate_targets.py`; `import_revised_scenarios.py`; `test_wave_plan_invariants.py`; seed tests.
**Scope:**
- A level present in the wave plan seeds planned waves. A level absent from it keeps today's single wave, as a transitional branch removed in Task 8.
- Port this plan's validator and workload measure into the invariant suite: the §3 rules, computed with the real resolver and the Task 1 fix, including the time budget.

**Expected output:** with an empty plan, the seed output is unchanged. The invariant suite runs.
**Verification:** `python -m pytest curriculum/tests -q`; `python ../scripts/check_seed_targets.py`; `python manage.py generate_targets --check`.
**Acceptance evidence:** an idempotent double seed; unchanged published counts with an empty plan.
**Parallel:** after Task 3 (needs `sort_order`).

### Tasks 5–8 — Module cutovers (Module 1 is the pilot)
For each module, in order: **5** = Module 1 (18 new), **6** = Module 2 (33), **7** = Module 3 (15), **8** = Module 4 (18).

**Files:** `wave_plan/module_N.py`; `scenario_fixtures/module_N.py`; `source/wave_scenarios.md` (the module's section); `scenario_bank.json` (recompiled); regenerated targets and trajectories; tests.
**Scope:**
- Claude writes the module's new scenarios (decision D4). They go in `source/wave_scenarios.md`, in the same Markdown sections the team's bank uses, to the full bank contract (CONTENT_AUTHORING_GUIDE.md: story, starting point, context, task, checklist, answer key, alternatives, expected result, evaluation, budgets).
- Match the bank's existing voice and recurring cast.
- The evaluation must make the taught route necessary or accept equivalents. For example, an amend wave must not be solvable by re-committing.
- The importer compiles the team's bank and this file into `scenario_bank.json`. If someone re-imports only the team's Markdown, the invariant suite fails, because placed IDs would be missing; the new scenarios can't silently disappear.
- Recommended: teammates review each module's new scenarios before that module's cutover.
- Enter the module's waves exactly as in WAVE_MAP.md. Regenerate targets.
- Task 8 also deletes the transitional single-wave branch and adds the `required_successful_attempts == 1` guard.

**Expected output:** the module's tiers show the planned waves in order, and every invariant passes.
**Verification:** `python manage.py generate_targets`; `python ../scripts/check_seed_targets.py`; `python ../scripts/check_generated_targets_current.py`; `python -m pytest curriculum/tests/test_wave_plan_invariants.py curriculum/tests/test_scenario_bank_content.py curriculum/tests/test_objective_soundness.py curriculum/tests/test_curriculum_fixture_idempotency.py -q`.
**Acceptance evidence:**
- Every canonical solution in the module replays and passes its evaluation.
- A browser walk on a disposable fresh account plays each level's Easy waves: guide shown, wave counter, next-wave copy.
- A veteran account confirms that guides still fire.

**Parallel:** authoring can be drafted in parallel, but bank edits land sequentially (one Markdown file and one compiled JSON).

### Task 9 — Cutover data, runbook and documentation
**Files:** the one-time progress backfill (partial clears → first waves; §10.3), which can share the Task 2 command; `deploy/CURRICULUM_WAVES_RESEED.md`; the root docs listed in §9; `LEVEL_CHEAT_SHEET.md`.
**Scope:**
- Update the authoring rules (wave grammar, wave plan location, variant order, time budget) and the architecture notes (ordered waves, guide resolution, level forms, reward ladder).
- `LEVEL_CHEAT_SHEET.md` still describes the retired 240-level curriculum: regenerate it from the wave plan, or remove it.

**Verification:** `python scripts/check_documentation_current.py`; `python scripts/check_legacy_terms.py`; the backfill run twice on a copy of the data with no second-run changes.
**Acceptance evidence:** the runbook dry-run on a staging copy.
**Parallel:** drafting with Tasks 5–8; finalized after Task 8.

### Task 10 — Final gate
Run everything in CLAUDE.md "Common Checks", plus:
- the backend suites touched above
- `npx vitest run` and the frontend build
- `python manage.py makemigrations --check --dry-run`
- the browser walk across all four modules on fresh and veteran accounts
- a KPI service smoke test on post-cutover runs

Report exact outcomes. Say "implemented but unproven" for anything not captured from the learner's perspective.

## 12. Decisions

Decided 2026-10-20:

| # | Decision | Outcome |
|---|---|---|
| D1 | Rewards for Medium and Hard | **Decided:** every tier pays on its first clear. Amounts Easy 25 / Medium 35 / Hard 50 (one constant, adjustable). Learners who cleared Medium/Hard before the change receive those coins once via the backfill (default kept; can be dropped) |
| D2 | Learners mid-tier at cutover | **Decided:** their clears map onto the first waves; a tier is never auto-completed |
| D3 | Tier stars once a tier has several waves | **Decided:** the lowest of each wave's best stars |
| D4 | Who writes the new scenarios | **Decided:** Claude writes them, in the team's Markdown scenario format (`source/wave_scenarios.md`), compiled by the importer; teammates review per module |
| D5 | Registering the 11 missing command forms | **Decided: yes.** They appear in the Chapter Book under their modules |
| — | Amount of repetition | **Decided:** the full plan (132 waves, ~4.9 h no-fail). A trimmed 93-wave variant was evaluated and set aside as too thin |

Still open:

| # | Decision | Recommended default |
|---|---|---|
| D6 | Registered but never practiced: `git add .`, `git add -A`, `git init --quiet`, and `git init <directory>` (every init solution passes `-b`) | Teammates choose: add a wave or drop them from the Module 1 guide |
| D7 | Is a KPI data-collection window open? | Cut over between cohorts and report the periods separately |
| D8 | Chapter chests count Easy completions only | Out of scope here. Revisit after the ladder ships |

Decided 2026-10-20 (second round, during execution):

| # | Decision | Outcome |
|---|---|---|
| D9 | Legacy cleanup | **Full removal.** That covers the pre-tier adventure runtime (`AdventureWave`, `AdventureWaveVariant`, `AdventureRun`, `AdventureRunWave`, `AdventureLevelCompletion`, their services, endpoints and frontend feature), the test-only `seed_curriculum_fixture` with its mixins and old spec sources, and their generated targets. The drop migrations are not applied to the shared dev database without asking. See §15 |
| D10 | Challenge Gate unlock | **Difficulty-matched:** a module's Easy trial unlocks once every level's Easy tier is cleared, and Medium and Hard follow the same rule. See §14 |
| D11 | Challenge Gate size | **3 trials × 2 variants per module:** 24 new workflow scenarios |
| D12 | Gate rewards | Default **Easy 50 / Medium 75 / Hard 100** GitCoins on first clear, as one adjustable constant next to the tier ladder |

## 13. Risks

- **Authoring volume** (84 scenarios, +32%). Mitigation: per-module slices with Module 1 as the pilot; Claude writes, teammates review per module (D4). Most new scenarios mirror existing fixtures.
- **Module 4 grows the most** (~28 → ~49 min no-fail). It is also where today's curriculum teaches least, so the time goes where it is needed.
- **State-based grading can't force a route.** Each new scenario's evaluation is reviewed for that (Tasks 5–8).
- **Simulator gaps** in pull conflicts and dirty-tree pulls. Task 0 runs before authoring.
- **KPI comparability** across the cutover. Old and new waves are separable by slug, and §10.6 records the boundary.
- **Free-play semantics** change from "reopen the completed variant" to "cycle waves". This is visible to returning learners, so it is called out in the runbook.

## 14. Challenge Gates (Task G)

**Problem:** Modules 1–4 have no Challenge Gate content. `seed_curriculum` creates no `ChallengeLevel`, and the only one in the dev database is UGC. Separately, `_adventure_passed()` returns True for any tier-based chapter, so a gate added as-is would be open immediately. `ChallengeTrial.reward_coins` defaults to 0.

**Design:**
- **Structure:** one `ChallengeLevel` per module chapter, slug `module-N-challenge-gate`, with three `ChallengeTrial`s (easy/medium/hard). Each trial has 2 `ChallengeTrialVariant`s.
- **What a trial asks:** each trial is a workflow scenario that combines several of the module's commands in a realistic order, not a single-command repeat.
  - Easy: 2–3 commands from early levels.
  - Medium: 4–5 commands across the module.
  - Hard: the full module in one task, with one trap the module taught (for example, a dirty tree before a pull, or a published commit that must be reverted rather than reset).
- **Unlock (D10):** for tier chapters, the trial of difficulty *d* unlocks when every required, published level in the chapter has an `AdventureLevelTierCompletion` for its *d* tier. Wave-based chapters keep today's rule until Task L removes it.
- **Rewards (D12):** a first clear pays the gate ladder once. The idempotency key follows the existing challenge completion path.
- **Content:** gate scenarios are written in the team's Markdown format, numbered `N.G.k` (the importer accepts a `G` level slot). They are compiled with the wave scenarios into `scenario_bank_waves.json`, and their fixtures live in `scenario_fixtures/gate_module_N.py`. Targets are regenerated through `generate_targets`, like every other case.
- **Seeding:** `seed_curriculum` writes the gate rows idempotently (update_or_create by slug) and unpublishes displaced trial variants instead of deleting them.

**Files:** `seed_curriculum.py` (gate block); `curriculum/selectors/adventure_access.py` (`_adventure_passed` per difficulty) and `challenge_access.py`; `challenges/services/runs.py` (unlock check); `source/wave_scenarios.md` (gate section); `source/scenario_fixtures/gate_module_*.py`; `generate_targets.py`; tests.
**Expected output:** every module path shows a Challenge Gate with three trials. Each trial is locked until the matching tiers are cleared, and its first clear pays once.
**Verification:** `python -m pytest challenges/tests curriculum/tests -q`; `python manage.py generate_targets --check`; `cd frontend && npx vitest run src/features/story-map src/features/challenges`.
**Acceptance evidence:**
- every gate solution replays and satisfies its evaluation, and the initial state does not;
- a unit test proves difficulty-matched unlocking;
- a browser walk on a disposable account: Easy tiers cleared → Easy trial opens; play it; coins credited once.

## 15. Legacy removal (Task L)

**Evidence (2026-10-20):**
- `seed_all` → `seed_curriculum` writes only `AdventureLevel → AdventureLevelTier → AdventureLevelTierWave → AdventureLevelTierWaveVariant`.
- In the dev database the legacy adventure tables are empty (0 rows each), while the tier tables hold 21/63/63/316 rows.
- The legacy path survives in three places:
  - **`seed_curriculum_fixture`:** test-only, guarded by `ALLOW_RETIRED_CURRICULUM_FIXTURE_SEED`. It and its mixins (`_writer`, `_structure`, `_challenges`, `_helpers`, `_validation`, `_commands`) seed the retired seven-chapter content; about 100 tests call it.
  - **`generate_targets`:** it replays 2,321 cases, of which 265 are live.
  - **The UGC compiler:** it writes `AdventureWave` rows for authored adventures.
- The frontend legacy feature is `features/adventures/*`, plus the routes `/adventure-levels/:levelId` and `/adventure-runs/:runId` and the dev outcome preview.
- Admin analytics still counts `AdventureRun`, so it reports zero adventure activity.

**Order:** after Task 3, because UGC levels compile to one tier with ordered waves. After Task G, because the ported tests use live gate content. Before Tasks 5–8, so the module cutovers no longer have to keep a legacy path alive.

| Step | Scope |
|---|---|
| L1 | UGC compiler → tier chain: each authored level becomes one tier with its waves in order. Port the playtest route |
| L2 | Port the tests that use `seed_curriculum_fixture` to the live seed or to tier factories (`testing/runtime_factories.py` rewritten for tiers). Delete tests whose only subject is retired content: the seven-chapter preservation hashes, the three-story curriculum and the plan-ownership checks for retired files |
| L3 | Delete the legacy adventure runtime: services `commands/history/runs/selectors`, the six endpoints, payloads and serializers, admin, `features/adventures/*` and its routes. Regenerate the OpenAPI contract and frontend types |
| L4 | Repoint the remaining readers to tier rows: drills seeding, admin analytics, `progress/selectors`, `progress_counts`, `challenges/services/runs.py` and `scripts/profile_command_latency.py` |
| L5 | Models: remove the five legacy models, and the `CommandStep` link if it targets `AdventureRun`, via migrations depending on `adventures 0012` / `progress 0003`. Write the migrations; apply them to the shared database only after asking |
| L6 | Delete the fixture seed, its mixins, the setting and every `curriculum/seed_data` module reachable only from them. `generate_targets` collects module tiers, wave scenarios and gates only; regenerate targets |
| L7 | Docs and guards: ARCHITECTURE.md, CONTENT_AUTHORING_GUIDE.md, `seed_data/README.md`, and the check scripts that list retired files |

**Kill criteria:**
- No non-migration code imports a removed model.
- `rg "seed_curriculum_fixture|AdventureRun\b|AdventureWave\b"` outside migrations returns nothing.
- `generate_targets --check` covers only live cases.

**Verification:** the full backend suite; `npx vitest run` and the build; `makemigrations --check`; every CLAUDE.md check.

## 16. Execution notes

- **Task 0 result:** all listed shapes replay (`frontend/src/shared/git/simulator/waveScenarioShapes.test.ts`). Two simulator gaps surfaced and were fixed in both the frontend engine and the backend verifier:
  - A divergent merge used to take the incoming tree wholesale, dropping files only the current branch had. A conflicted merge also deleted those files from the index. Merges are now real three-way merges.
  - A merge or pull now refuses when local edits overlap the incoming changes, as Git does.
  Targets were regenerated (44 merge cases changed). `ch7-challenge-medium` was corrected because its spec relied on the bug.
- **Storage change:** new scenarios compile from `source/wave_scenarios.md` into a separate `scenario_bank_waves.json` (importer `--extension`), because `apply_scenario_bank` pairs the team's 265 scenarios positionally. `scenario_for_case` reads both banks and asserts their IDs are disjoint.
- **Evaluator:** rules can name a first-parent ancestor (`main~1`), so a two-commit scenario can check both commits.
- **Live verifier bug (found 2026-10-20, fixed):** the backend `ClientTransitionVerifier` rejected four Hard scenarios that already exist, so no learner could finish them: `cherry-hard-export-conflict`, `cherry-hard-abort-conflict`, `cherry-hard-trace-source` and `rebase-hard-continue`.
  - Cause: it treated a cherry-pick that stops on a conflict as a failed command that must not change state. It also could not verify `cherry-pick --continue` or the `-x` note, and `rebase --continue` only handled an empty remaining list.
  - Fix: the verifier now mirrors the engine for all of these. The engine also keeps a conflicted `cherry-pick -x` note through `--continue`, as Git does.
  - Guard: `generate_targets` (and `--check`, run in CI's node job) now replays every live answer key through the backend verifier and refuses any route the backend would reject.
- **Progress (2026-10-20):**
  - Done, with tests: Task 0, Task 1 (resolver, used-form mastery credit, 11 forms, level and wave forms), Task 2 (ladder, reward display, backfill command) and Task 3 (ordered-wave runtime and migration `adventures 0013`).
  - Task G: done, with all 24 gate scenarios seeded.
  - Module 1's 18 wave scenarios are written and validated, waiting for Task 4's wave plan.
  - Task L: done in code, L1–L7. The legacy models, runtime, fixture seed and frontend feature are deleted. The drop migrations (`adventures 0014/0015`, `progress 0004`, `practice 0004`) pass on the test database and were applied to the shared database on 2026-10-20, with the user's OK (every legacy table was empty). `verify_frontend_level_sequences.py` targeted only the deleted run flow and was removed, so browser evidence uses a scripted walk (see §13). Checks on 2026-10-20: backend 896 passed / 1 failed (`test_symbol_manifest_equivalence`, catalog and KPI-session hashes, both outside this task); frontend 57 failed in 14 files against 60 in 16 files at HEAD `ba41c32`, the drop being the two deleted legacy adventure suites; `npm run build` passes.
  - Porting the star-target test to tiers showed the budget lives on the variant (`tier_budget.command_budget`). All 265 published variants can reach three stars.
  - Tasks 4–9 (2026-10-20): done in code.
    - All 21 levels seed from the wave plan: 132 waves, 349 variants, about 4.9 h no-fail (70/113/64/49 min).
    - All 85 new scenarios are written. The transitional single-wave seed branch is deleted, and `required_successful_attempts` is retired (`adventures 0016`, not applied to the shared database).
    - Added `map_partial_tier_progress`, `deploy/CURRICULUM_WAVES_RESEED.md` and a regenerated `LEVEL_CHEAT_SHEET.md`.
    - KPI studies now count a tier's published waves as its required clears.
  - **State-only grading** (user decision, 2026-10-20): published scenarios are graded on repository state only.
    - Typed-command rules and operation-record rules are gone. The team's are converted at seed time (`scenario_runtime._state_only`); mine are fixed at the source.
    - Both engines now record `repository_root`, reject unsafe pushes as Git does, and write switch entries to the HEAD reflog.
    - The 1.1 Hard "Re-run init safely" wave became "A nested project folder". `init-hard-safe-rerun` is unplaced, because re-running init leaves no state to grade (`UNPLACED_CASE_IDS`).
    - Twelve team scenarios passed in their starting state and now require state evidence: pulls land the server's commit, and stash round trips show the visit in the reflog.
  - Engine fixes found while authoring, in both engines:
    - A push now updates the pending server tip.
    - A squash merges three ways.
    - `--no-commit` picks stack on the index.
    - Four 2.8 fixtures squashed an empty commit and now author the teammate's commits.
  - Browser evidence for Tasks 1–10 is still to be captured.
  - Wave forms are the level forms *every* variant of the wave uses. Mastery targets count those waves, so a target is always reachable under used-form credit. Today's mixed pools therefore attach no forms to some waves; the cutovers fix that, because every variant of a designed wave shares its debut.
- **KPI invariants Task 3 must keep** (from the KPI session, 2026-10-20). Check them after every task with `progress/tests/test_mastery_kpis.py`, `test_kpi_scope.py`, `test_kpi_studies.py` and `test_kpi_references.py`:
  1. `mastery_metrics.live_records` dates legacy mastery by the last *non-replay* clear. It assumes every launch after an `AdventureLevelTierCompletion` exists is `is_replay=True`. Ordered waves must not create non-replay runs after completion.
  2. `checkpoints.assign_transfer`, `studies.create_study` and `_records` read the tier's *first published wave* for transfer variants and required clears. With several waves per tier, "required clears" becomes the number of waves (one clear each). Transfer variants stay reserved on the first wave.
  3. `tier_runs.start_run` keeps:
     - `retry_index = failed_attempts(...)`, computed after the prior-run discard, for non-replay starts;
     - `record_exposure(run)` on every launch;
     - `exposure_complete` on newly created progress rows;
     - the `transfer=True` branch.
     Reserved variants (`is_transfer=True`) stay out of normal selection.
  4. `tier_command_processing` calls `record_mastery(run)` only when the completion is first created and `finish_transfer` on solved or failed transfer runs. It keeps the `ref_hash` invalidation block, and transfer runs get no stars or rewards.
  5. `KpiCheckpoint.run` is RESTRICT on purpose, and the new adventure columns use `db_default`.
  6. Reseeding a variant's states, solution or budget invalidates its `ref_hash` by design, so `kpi_refs` must be rerun after every reseed (record this in the runbook).

## PRE Review

**Mode:** PRE (self-review against the krypton reviewer template; no independent reviewer was dispatched)
**Verdict:** aligned for Tasks 0–4 (D1–D5 decided). Content Tasks 5–8 start once Task 0 reports.

| Severity | Finding | Smallest correction |
|---|---|---|
| major | Several review waves depend on simulator behavior that is only partly proven (pull conflicts, dirty-tree pull refusal). | Task 0 gates the authoring of affected scenarios. Waves whose shape fails get redesigned before authoring, not after. |
| major | During Tasks 4–7, a transitional single-wave branch coexists with planned waves (a temporary duplicate path). | Kill criterion: Task 8 deletes it, and a guard fails if any published wave needs more than one clear. |
| minor | The reward amounts (D1) are a default the user hasn't tuned. | They are one constant, so they can change without restructuring. |
| minor | The time model is an estimate, not measured learner time. | Compare it with real run durations after the Module 1 pilot before cutting Modules 2–4. |
| minor | Browser evidence relies on updating `verify_frontend_level_sequences.py`, which still targets the retired three-story waves. | Fold the update into Task 5's evidence step, or use a scripted agent-browser walk for the pilot. |

Outcome, truth ownership, contract, cutover, displaced paths, evidence and kill criteria are all named. The placement map was machine-checked against the §3 rules with the real resolver and the 11 registered forms: zero violations, every guided form reused (also at exact-form level), all 265 scenarios placed once, and a no-fail path of about 4.9 hours.

**Recommended next gate:** run an independent PRE review. Then execute Tasks 0–2, with Task 1 first: it fixes a live learner-facing bug (suppressed guides) regardless of the rest.
