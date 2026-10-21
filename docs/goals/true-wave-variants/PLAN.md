# True Wave Variants Implementation Plan

**Intent:** A wave is one problem, and its variants are copies of that problem. Every new command form or argument kind the curriculum introduces gets its own command guide, at the moment it first appears. Everything a tier teaches with a guide comes back unguided before the tier ends.

**Current Behavior:**
- **Variants are chosen by topic.** The only wave rule is a floor (`test_debuts_happen_before_hard_and_in_every_variant_of_the_wave`): every variant must use what the wave debuts. Nothing stops a variant from adding more, so siblings differ in URL scheme, pathspec kind, ref kind, step count and starting repository.
- **Level 1.1 never teaches plain `git init`.** Easy Wave 1 opens with `git init -b main`, so the learner's first guide is `git init -b <branch> [<directory>]`.
- **The guide teaches per form** (`form:<usage>` keys, `tutoring/services/forms.py:98`), but some new things are never guided:
  - Optional parts bundled in brackets, such as `[<directory>]` or `[<start-point>]`.
  - Argument kinds with no technique detector, such as an SSH URL, a target folder for `init`, or a commit start point.
  - A second new thing in the same command. The planner shows one lesson per step (`tutoring/services/planner.py:_next_lesson`).
- **Debuts often never come back within their tier.** 36 of 45 debut waves are never reused unguided later in the same tier, and 20 of 63 tiers end on a debut. The existing "comes back later" rule is satisfied by a harder tier or a later level. Easy is always open, while Medium unlocks per level only after Easy (`adventures/services/tier_runs.py:330`), so that later recall isn't guaranteed to happen soon, or at all.

**Expected Outcome:**
- Every wave passes a tiered variant-shape check.
- Every level's Easy Wave 1 uses only its declared canonical form.
- Every part a debut wave introduces is the guide the planner shows for that wave, with at most one new lesson per command step.
- Every guided part reappears unguided later in the same tier.
- Level 1.1 Easy goes `git init` → `git init -b <branch>` → `git init -b <branch> <dir>` (the target-folder guide), then recalls.

**Target-Perspective Output:**
- A learner opens 1.1 Easy and the guide shows `git init`.
- Each later wave shows a guide for exactly the one new thing it adds.
- Before the tier ends, they meet a wave that uses what they were taught, with no guide at all.
- Retrying any wave gives a new story around the same problem.

**Truth Owner:**
- `backend/curriculum/seed_data/source/wave_plan/` owns placement and the per-level canonical forms.
- `backend/tutoring/services/techniques.py` owns which argument kinds are teachable lessons. The shape check and the planner both read it.
- The banks own the scenario text.

**Contract Boundary:**
- `WaveSpec` and its variant IDs, as consumed by `seed_curriculum`.
- The planner's lesson set (forms plus techniques), as consumed by the command response.
- No API schema change: technique guides already use the existing guide payload.

**Cutover:** One branch. The checks land together with the re-placement and the new techniques that make them pass. There is no allowlist or xfail.

**Displaced Path:**
- The floor-only variant rule (WAVE_MAP.md rule 3, CONTENT_AUTHORING_GUIDE.md rule 6 and wave grammar rule 2) becomes a floor plus a ceiling.
- WAVE_MAP.md rule 2's "plain `git init` at Hard" clause is deleted.
- Rule 4 ("comes back later") gains a same-tier recall requirement. The cross-tier rule stays.

**Value Density:** High. About 11 waves re-placed and three or four technique detectors added. Closing recall waves are added where reordering can't provide recall.

**Acceptance Evidence:**
- The new shape, guided-debut and recall tests pass, along with the existing wave invariant and tutoring suites.
- The seed is idempotent, and generated targets are current.
- A dogfood playthrough of 1.1 Easy shows one guide per new thing and an unguided closing wave.

**Evidence Lane:** pytest (`curriculum/tests/`, `tutoring/tests/`), `scripts/check_seed_targets.py`, `scripts/check_generated_targets_current.py`, the common checks in CLAUDE.md, and a browser run of 1.1 Easy.

**Kill Criteria:** No allowlist, xfail or per-wave exemption for the shape, guided-debut or recall rules. No wave title is false for any of its variants. No wave slug is reused for a different problem. No argument-kind table in the tests duplicates `techniques.py`.

**Architecture Slice:** See "Architecture slice" below.

**Plan Review Gate:** Requires PRE review before execution.

---

## Decisions (2026-10-21, with the user)

1. **The threshold widens per tier.**
   - **Easy:** isomorphic. The steps are the same, and so are the options (aliases folded, so `-b` = `--initial-branch`), the argument kinds and counts, and the starting-repo shape. Only names, paths, messages and story change.
   - **Medium:** the same steps in the same order, with the same options and argument kinds. Counts of a repeated argument (2 vs 3 files) and option values (`--depth 1` vs `--depth 2`) may differ. The structural flags of the starting repo must match: repo initialized, remote present, detached, conflict, operation in progress.
   - **Hard:** the same forms and the same decision. Consecutive repeats of a form collapse, and the starting repo may differ (distractors, which candidate is right, extra branches). A Hard variant may never use a form or argument kind that the wave doesn't.
2. **Misfits get re-placed first, then unplaced.** A misfit moves to a wave it truly matches, preferably a closing recall wave (decision 5), or else goes into `UNPLACED_CASE_IDS`. Teammate-authored bank text is never edited. If a wave drops below two variants, new scenarios are authored in `wave_scenarios.md`.
3. **1.1 goes one step per wave.**
4. **Every new form or argument kind gets its own guide** (the user's follow-up). A form-changing argument kind becomes a technique lesson in `techniques.py`, so the planner teaches it with the existing "known form, new technique" path.
5. **Guided things come back unguided within the same tier** (the user's follow-up; Claude's recommendation on the mechanism):
   - **Recall is a later wave of the same tier that reuses the debuted parts with no guide**, either because a later debut builds on them (layering) or because a closing practice or compose wave combines them. A guide never repeats once completed or once the form is used, so recall is unguided by construction.
   - **Rejected: an identical sibling replayed as the recall.** That is massed repetition, and it either costs two more authored isomorphic scenarios per debut, or a recall wave that borrows the debut wave's pool (which breaks "placed exactly once" and needs runtime selection changes). A closing wave that combines the tier's forms tests recall in a slightly new context, and many current misfits are exactly those combinations (for example `clone-medium-cli-starter-folder` is folder + `-b`).
   - **Later tiers keep reusing the forms** under their wider thresholds (the existing rule 4).
   - **Open, team decision:** tiers that already hold three debuts need a fourth wave, or one debut moves to Medium. Allowing Easy and Medium tiers 4 waves, and the no-fail time budget, need the team's sign-off. A worst case of about 20 closing waves adds roughly 25 minutes to the agreed 4.9 h.

Constraints carried forward:
- The 21 levels and their commands are fixed.
- Grading stays state-only, so `git init` and `git init -b main` both pass a "repo on main" target.
- At least 2 variants per wave.

## The variant-shape contract

A variant's **shape** has two parts.

- **Answer skeleton.** The ordered non-diagnostic git steps (`DIAGNOSTIC` ones are dropped). Each step is `(family, subcommand, folded option set, multiset of argument kinds)`.
- **Start shape.** Read from `initial_state`: repo initialized, number of commits and branches, remote present (only if the answer uses a remote), detached HEAD, conflict, operation in progress, stash count, and untracked/unstaged/staged counts.

Argument kinds are classified against the variant's own `initial_state`. Kinds that change what the learner must know are technique lessons in `techniques.py`, and the check reads them from there. Examples are `ssh-url`, `target-folder`, `start-point` and the existing `several-paths`, `current-folder`, `relative-commit` and `remote-branch`. Purely structural kinds (`path:file` vs `path:dir-existing`, `ref:branch` vs `ref:commit`) live in the test helper. Option values (`-m "…"`, `-b <name>`, `--depth N`) are values, not kinds.

**Canonical first form.** Each level declares the form its Easy Wave 1 debuts. Every variant of that wave resolves to exactly that form, with no further unknown technique.

**Guided debut.** Walk the waves in default play order, carrying the set of known lessons.
- In a debut wave, every step of every variant may introduce at most one unknown lesson (a form, or a technique once the form is known).
- The union of those lessons across the wave must equal what the wave debuts. Every variant introduces the same lessons.
- A non-debut wave introduces none.

**Same-tier recall.** For every lesson a wave debuts, some later wave of the same tier uses it in every variant.

**Human review**, recorded per wave in WAVE_MAP.md:
- At Easy, every brief gives its parameters the same way (all stated, or all inferred from a convention).
- The wave title holds for every variant.

## Known misfits (rough audit, 2026-10-21; Task 1's check is authoritative)

| Wave | Misfit | Why | Proposed disposition |
|---|---|---|---|
| 1.1 Easy `track-this-folder` | — | the debut is `-b`, not plain `git init` | becomes W2. New W1 debuts `git init` with **2 new** scenarios |
| 1.1 Medium `existing-files-stay-untracked` | `init-hard-ci` | new folder vs existing folder | candidate for a 1.1 Easy closing recall wave. Otherwise unplace. **1 new** existing-folder sibling |
| 1.2 Easy `clone-a-repository` | `clone-easy-oss-ssh` | SSH vs HTTPS | SSH becomes the `ssh-url` debut at Medium `ssh-into-named-folder`. Unplace this one. **1 new** HTTPS sibling |
| 1.2 Easy `clone-a-specific-branch` | `clone-medium-cli-starter-folder` | adds a folder argument | candidate for the 1.2 Easy closing compose (folder + `-b`) |
| 1.2 Medium `shallow-history` | `clone-medium-shallow-metrics` | adds a folder argument | candidate for the 1.2 Medium closing compose. Otherwise unplace. **1 new** sibling |
| 1.2 Hard `shallow-copy-of-one-branch` | — | false positive from argument order | fix the classifier (multiset, not sequence) |
| 1.3 Easy `stage-and-commit-one-change` | `commit-easy-auth-dir` | directory vs file pathspec | unplace (3 remain) |
| 1.3 Easy `stage-several-files` | `commit-easy-initial` / `commit-med-docker` | 3 files vs 2 (Easy counts must match) | **1 new** sibling matching one. Move the other to Medium `a-two-file-change` if it matches |
| 1.5 Easy `fix-the-last-message` | `amend-hard-convention` | message inferred vs stated | unplace (4 remain) |
| 2.1 Medium `start-from-another-tip` | `bc-med-oss-develop` / `v21h-from-develop` | implicit vs explicit start point | the wave debuts the `start-point` technique. Unplace `bc-med-oss-develop`. **1 new** sibling |
| 2.1 Hard `start-from-an-older-commit` | `v21h-hotfix-c1` / `v21h-detach-save` | commit start point vs saving a detached HEAD | decide in Task 5 (the start point must not debut at Hard) |
| 2.2 Medium `build-the-name-from-the-brief` | `bn-med-oss-infer` | an unused remote in the start shape | the fingerprint ignores remotes the answer doesn't use. Re-check |
| 3.3 Easy `copy-one-commit` | `cherry-medium-login-timeout`, `cherry-medium-invoice-rounding` | two picks; branch-name ref | the two-pick one is a candidate for the 3.3 Easy closing practice. Unplace the other |
| 1.1 Hard `nested-project-folder` | `init-hard-nested-service` | branch inferred vs stated | Hard allows it if the decision is the same. Reviewer confirms |

Tiers whose debuts have no same-tier recall today (36 debut waves) are listed by Task 3's test. Most are Easy tiers of two debuts with no closing wave: 1.2, 1.6, 2.1, 2.3–2.5, 2.7–2.9, 3.3 and 4.3. Several tiers can be fixed by reordering or by moving a Medium compose down, for example 1.6 `unstage-one-discard-another` or 2.9 `retire-a-branch-everywhere`.

## Architecture slice

- **Files to create:**
  - `backend/curriculum/tests/variant_shape.py` (skeleton, structural kinds and start shape; test-only)
  - `backend/curriculum/tests/test_wave_variant_shape.py`
  - `backend/curriculum/tests/test_wave_guided_debuts.py` (guided debut and same-tier recall)
- **Files to modify:**
  - `backend/tutoring/services/techniques.py`: the `ssh-url`, `target-folder` and `start-point` detectors, with their guide copy
  - `source/wave_plan/types.py`: the `CANONICAL_FORMS` type
  - `source/wave_plan/module_{1..4}.py` and `__init__.py`
  - `source/wave_scenarios.md` and `source/scenario_fixtures/module_*.py`
  - `seed_data/scenario_runtime.py`: `UNPLACED_CASE_IDS`
  - `curriculum/tests/test_wave_plan_invariants.py`: the 2–3 wave cap, only if the team approves a 4th wave
  - `docs/goals/curriculum-waves-and-repetition/WAVE_MAP.md` + `wave-map.json`
  - `CONTENT_AUTHORING_GUIDE.md`
- **Files to avoid:**
  - `scenario_bank.json` content (teammate-authored; only regenerated through the import script)
  - everything under `generated/`
  - the evaluator, simulator and grading rules
  - `planner.py`'s selection logic (new lessons enter through techniques only)
  - frontend
- **Source of truth:** the wave plan for placement and canonical forms; `techniques.py` for teachable kinds; the banks for content.
- **Read path:** `seed_curriculum` → wave plan → `scenario_runtime` / the fixture join → published waves and variants. At runtime, `plan_introduction` → `resolve_form` → `techniques_in`.
- **Write path:** authored source → `scripts/curriculum/import_revised_scenarios.py --extension` → `python manage.py generate_targets` → `seed_curriculum`.
- **Integration points:**
  - `PlayerCommandIntroduction` keys. New technique keys are new lessons, so existing learners see them once on first use.
  - Progress rows (`cleared_wave_slugs`, `last_shown_variant`).
- **Migration/cutover:** a reseed only.
  - Waves whose problem stays the same keep their slug, and new waves get new slugs.
  - Stored `AdventureLevelTierCompletion` rows keep finished tiers finished.
  - A learner partway through a tier meets any newly inserted wave. That is accepted.
- **Acceptance evidence gate:** Task 7.

## Tasks

### Task 1: Variant-shape check (not parallel; Tasks 3–5 depend on it)
- **Scope:**
  - Write `variant_shape.py` and `test_wave_variant_shape.py`, applying the tiered rule per wave. A failure prints the groups of matching variants with their shapes, so it doubles as the audit report.
  - Add the canonical-form test.
  - Reuse `parse_command` and `ALIASES`; do not copy the alias tables.
- **Verify:** `cd backend && python -m pytest curriculum/tests/test_wave_variant_shape.py -q`. It should fail with about the table above. Confirm the 1.2 Hard false positive is gone.

### Task 2: Teachable argument kinds become technique lessons (parallel with Task 1)
- **Scope:**
  - Add `ssh-url`, `target-folder` (a positional directory for `init` and `clone`) and `start-point` (`switch -c <b> <start>` and `branch <b> <start>`) to `techniques.py`, each with a label and summary in the existing guide voice.
  - Confirm the planner offers each one once its form is known.
  - Add a tutoring test per technique: detected, offered once, and known after use.
- **Verify:** `python -m pytest tutoring/tests -q`

### Task 3: Guided-debut and same-tier recall checks (after Tasks 1 and 2)
- **Scope:** write `test_wave_guided_debuts.py`, built from the planner's own `resolve_form` and `techniques_in` with no parallel logic. It checks:
  - at most one unknown lesson per step;
  - the debut lessons are the same in every variant;
  - non-debut waves introduce nothing;
  - every debuted lesson is reused in a later wave of the same tier.
- **Output:** the authoritative list of unguided debuts and unrecalled tiers.
- **Verify:** `python -m pytest curriculum/tests/test_wave_guided_debuts.py curriculum/tests/test_wave_plan_invariants.py -q` (expected red until Tasks 4–5).

### Task 4: Rebuild 1.1 Initializing Repositories (the pattern for Task 5)
- **Scope:**
  - **Easy:**
    - W1 is new, slug `start-tracking-this-folder`, a debut of `git init`, with 2 new scenarios (an empty current folder, no branch named in the brief).
    - W2 `track-this-folder`, retitled "Choose the first branch", a debut of `-b`: `init-easy-current-empty`, `init-easy-trunk-branch`.
    - W3 `new-project-folder`, a debut of `target-folder`: `init-easy-invoice`, `init-med-oss`.
    - W3 recalls W1 and W2 by layering, but nothing in Easy recalls `target-folder`. If the team approves 4 waves, W4 is a closing practice: a new folder among other files, using `init-hard-ci` plus 1 new scenario. If not, `target-folder` debuts at Medium W1 instead, and Easy ends with a practice of `-b`.
  - **Medium:** W2 `existing-files-stay-untracked` holds `init-medium-existing-files` plus 1 new scenario.
  - Set `CANONICAL_FORMS["initializing-a-local-repository"] = "git init"`.
  - Author the new scenarios, then run the import and `generate_targets`.
- **Verify:**
  - all three new test files pass for this level
  - `python ../scripts/check_seed_targets.py`
  - `python -m pytest curriculum/tests/test_scenario_bank_content.py -q`

### Task 5: Re-place the remaining misfits and add closing recall waves (parallel by module after Task 4)
- **Scope:**
  - Work through the outputs of Tasks 1 and 3 module by module.
  - Prefer, in this order:
    1. reorder waves so a later wave reuses an earlier debut;
    2. move a matching Medium compose down;
    3. re-place a misfit into a closing wave;
    4. author new siblings.
  - Declare `CANONICAL_FORMS` for all 21 levels.
- **Verify:** the full `curriculum/tests/` suite, including the time budget and `test_seed_publishes_exactly_the_planned_waves_and_is_idempotent`.

### Task 6: Docs (alongside Task 5)
- **Scope:**
  - **WAVE_MAP.md:**
    - Rewrite rules 2–4: floor plus ceiling, guided debut, same-tier recall.
    - Add the tier threshold table and the canonical-form rule.
    - Update the affected tables, `wave-map.json`, and the headline counts and time.
  - **CONTENT_AUTHORING_GUIDE.md:** replace rule 6 and wave grammar rule 2 with a short statement of the three contracts, linking to the tests.
- **Verify:** `python scripts/check_documentation_current.py`, `python scripts/check_legacy_terms.py`

### Task 7: Acceptance
- **Scope:**
  1. Run the full `curriculum`, `adventures` and `tutoring` suites, the CLAUDE.md common checks, and `scripts/check_generated_targets_current.py`.
  2. Reseed a **local copy** of the database that has progress rows. Never drop the shared database. On that copy, confirm that a `last_shown_variant` pointing at a now-unplaced variant doesn't crash `start_run` (`adventures/services/tier_runs.py:108`). If it does, fix the selector to fall back to the wave's first variant.
  3. In the browser, play 1.1 Easy as a fresh player:
     - W1 shows the `git init` guide;
     - W2 shows `-b`;
     - W3 shows the target-folder guide;
     - the closing wave shows no guide;
     - after a failure, the retry differs in names only.
- **Output:** test output, a reseed log, and screenshots. If the browser step can't run, report "implemented but unproven".

## Non-goals and rejected options

- No level, command, slug order or grading changes.
- No edits to teammate-authored scenario text.
- No change to how the planner chooses lessons. New lessons enter only as techniques.
- **Rejected:** generating variants from one parametric template per wave. It would replace the authored banks; the shape check gives the guarantee for far less change.
- **Rejected:** recall by replaying an identical sibling of the debut wave (see decision 5).

## Risks if wrong

- **The classifier over-flags.** Waves get thinned for surface differences. Mitigation: review each flagged group in Task 1 before anything is unplaced.
- **Easy count-matching is the most borderline rule.** If it causes much churn, revisit the rule with the user. Do not exempt waves one at a time.
- **New technique guides add prompts for existing learners.** Each one shows once.
- **Without a 4th wave, some tiers can't meet same-tier recall.** That forces a debut to move to Medium, which is a team call (decision 5).
