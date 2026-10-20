# GIT it! — Content Authoring Guide

This guide explains how to author curriculum content that teaches Git through scenario practice and remains compatible with backend verification, generated target states, and the frontend simulator.

## Content Types

| Type | Purpose | Shape | Completion |
|---|---|---|---|
| Lesson | Explain a concept briefly before practice | Chapter book pages | Read/progress state |
| Adventure | Teach command mastery through guided scenarios | Levels → easy/medium/hard tiers → ordered waves → variants | Every wave of the tier cleared, verified by state |
| Challenge | Assess transfer on new scenarios | Easy/medium/hard trials → variants | Whole-state evaluation |

## Authoring Principles

1. **Introduce, then compose.** First exposure to a command may be a small single-command wave. After that, prefer multi-command workflows.
2. **Repeat commands in new scenarios.** Mastery comes from revisiting command forms in different repository states, not from repeating the same story.
3. **Never repeat scenarios.** Commands repeat; narrative setup and initial repository state should not.
4. **Challenges must change repository state.** A challenge trial should visibly change commits, branches, refs, or HEAD.
5. **Author the ideal scenario.** If the simulator lacks a needed behavior, improve the simulator and verifier rather than weakening the curriculum.
6. **Variants must test the same skill.** Two variants may use different file names/story details, but they should share the same learning goal and objective shape.
7. **Grade the repository, not the route.** Every requirement describes the resulting state: commits, branches, refs, files, config, remotes, stash, reflog. Do not require typed commands or check how an operation ran; an equivalent Git route must pass. A task that ends where it started (re-running `git init`, a stash round trip) needs evidence in state, such as the reflog entry a branch switch leaves, or it cannot be graded. The objective checklist promises only what the requirements check.

## Adventure Authoring

`MODULE_LEVELS` in `backend/curriculum/management/commands/seed_curriculum.py`
defines each module level and holds the repository fixtures of the team's
scenarios. The levels and the commands each one teaches are fixed by the team;
waves, variants, and the difficulty a command form appears at may change.

**Placement** lives in the wave plan,
`backend/curriculum/seed_data/source/wave_plan/module_N.py`. For each level and
tier it lists 2–3 waves in play order. Each wave has a stable slug (learners'
progress names it), a title the learner sees, a role, and its variant IDs. The
first variant is the one a first-time learner gets, and a retry rotates within
the same wave. A run plays the learner's next uncleared wave, one solve clears
it, and the tier completes when every wave is cleared. Every level must be in
the plan; the seed refuses a level without one.

Each wave has one role:

| Role | Use |
|---|---|
| debut | First use of a form or technique. Easy, or Medium for a level's advanced form. |
| practice | The same forms in a different repository. Nothing new. |
| compose | Two or more of the level's own forms in one scenario. |
| spiral | The level's command plus forms from earlier levels, as a real workflow. |
| transfer | Hard: unfamiliar state or distractors, known forms only. |

The wave grammar (`curriculum/tests/test_wave_plan_invariants.py` checks all of
it with the real guide resolver):

1. Nothing debuts at Hard, and diagnostics (`status`, `log`, `show`, `reflog`,
   `diff`) never debut.
2. Whatever a wave debuts, every variant of it uses, so a retry never skips the
   guide's lesson. Keep a wave's variants on the same skill.
3. A debuted form comes back at a harder tier or a later level. Core workflow
   forms (add, commit, amend, restore, switch, branch, stash, push, fetch,
   pull, merge) come back in two later waves, one in a later level. Setup
   forms (`init`, `clone`) are exempt.
4. Every scenario is placed exactly once, in its own level, and no two variants
   share both a starting repository and a target.
5. A learner who never fails finishes Modules 1–4 in about 4.9 hours (the suite
   fails above 5 h). It counts 1 min per wave, 0.4 min per typed command, 1 min
   per file edit, and 0.5 min per first-time guide. Re-measure before adding
   waves.

A wave's command forms are the level forms every one of its variants' answer
keys uses, and a level's forms come from its non-spiral waves. A clear credits
the forms the learner actually typed toward mastery. A scenario placed in an
easier tier than it was written for gets that tier's command limit.

Scenarios come from two banks:

- `seed_data/scenario_bank.json`, the main bank, compiled from the revised
  Markdown scenario document with
  `python scripts/curriculum/import_revised_scenarios.py <document.md>`.
- `seed_data/scenario_bank_waves.json`, the extension bank, compiled from
  `seed_data/source/wave_scenarios.md` with the same script and `--extension`.
  Each extension scenario's repository fixture, evaluation rules, and answer
  key live in `seed_data/source/scenario_fixtures/` under the same ID. The
  importer rejects an ID or number that collides with the main bank.

Each scenario should define:

- a stable case ID
- a learner-facing title, story, and task
- an initial repository state
- solution commands (git, plus terminal shell commands such as `mkdir`, `cd`, `touch`, or `echo "x" > file` when the task is about files; replay keeps the working directory between them)
- state requirements the evaluator verifies
- a counted-command budget when the tier default does not fit

A new scenario also needs its place in the wave plan. Then run, from `backend/`:

1. `python ../scripts/curriculum/import_revised_scenarios.py --extension curriculum/seed_data/source/wave_scenarios.md`
2. `python manage.py generate_targets`
3. `python -m pytest curriculum/tests/test_wave_plan_invariants.py curriculum/tests/test_scenario_bank_content.py -q`

The content suite checks every wave and gate answer key against its own
evaluation, and that the starting state does not already pass. The target state
must rule out wrong routes or accept their equivalents. For example, an amend
wave must not pass a new commit (`branch_tip_replaces_commit`).

## Challenge Authoring

Each module ends in a Challenge Gate: a workflow that tests what the module
taught. `seed_data/source/challenge_gates.py` composes each gate's title,
narrative, and the two scenarios behind each of its Easy, Medium, and Hard
trials. Gate scenarios are extension scenarios numbered `N.G.k` in
`seed_data/source/wave_scenarios.md`. A trial of a given difficulty opens once
every required level of the module has cleared its tier of that difficulty.

Each trial should have:

- two variants
- a new scenario not copied from adventures
- a workflow that combines the module's commands
- a repository-state transition that changes the DAG or refs
- evaluation specs that verify final state instead of command text alone

## Scaffolding

Support is not authored. `practice/services/scaffolding.py` owns one constant
ladder per gameplay surface, keyed by difficulty, and every surface reads its
ladder from there.

Adventure level tiers (`TIER_SCAFFOLDING_LADDER`, `supports_for_tier`):
feedback fades first, then the Expected State diagram.

| Difficulty | Live DAG | Expected State | Contextual feedback |
| --- | --- | --- | --- |
| easy | yes | yes | yes |
| medium | yes | yes | no |
| hard | yes | no | no |

Challenge trials (`SCAFFOLDING_LADDER`, `supports_for`): the Expected State
diagram fades first, then feedback.

| Difficulty | Live DAG | Expected State | Contextual feedback |
| --- | --- | --- | --- |
| easy | yes | yes | yes |
| medium | yes | no | yes |
| hard | yes | no | no |

The Expected State panel needs both the ladder flag and a populated
`target_state`, so a variant with an empty target silently loses its diagram.
Targets come from `python manage.py generate_targets` - never by hand.

## Objective Checks

Where a wave defines objective checks, they should be:

- **Modular** — one visible checklist row per meaningful step.
- **Variant-safe** — do not hard-code a file/branch/commit that differs between variants.
- **End-state based** — false at the start, true only after the learner completes the step.

Avoid premature-pass checks such as `staging_empty: true` unless the initial state makes that meaningful.

## Story Briefs and Exact Values

The learner must never have to guess an arbitrary literal that evaluation requires.

- Put the short scenario narrative in `scenario_context.story`, the one-sentence objective in `scenario_context.task`, and optional practical background in `scenario_context.real_world_context`. Empty fields are omitted from the tier story modal.
- Name each value's purpose in the story or task prose (for example, "Use the required commit message shown below").
- Put the exact copyable value in `scenario_context.details`. The workspace displays the value only; the label remains available to assistive technology and the copy button.
- Do not expose whole solution commands. Command choice remains part of the exercise; only otherwise-uninferable values such as required commit messages, URLs, branch names, and refs belong in copy details.
- Evaluated messages supplied through `git commit -m` are synchronized into copy details by the seed helpers. The authored prose must still make their role understandable.

The curriculum invariant suite audits this contract across every adventure and challenge variant.

## Generated Targets

Generated targets live in:

```txt
backend/curriculum/seed_data/generated/generated_targets.py
```

`generated_trajectories.py` sits next to it: fingerprints of the repository in front of each solution command. The command-introduction tutor uses them to find the next move a learner needs, so a solution's command order is also its teaching order. Diagnostic commands (status, log, show) in a solution are never introduced.

Do not edit generated targets or trajectories directly. After changing initial state, solution commands, or workspace edits, run:

```bash
cd backend
python manage.py generate_targets
```

Then verify:

```bash
python ../scripts/check_seed_targets.py
python ../scripts/check_generated_targets_current.py
```

The full replay check requires frontend dependencies because it runs the real TypeScript simulator.

## Simulator and Verifier Expectations

Every new supported command behavior must keep these layers aligned:

- frontend simulator
- backend repository-state normalization
- backend command transition verifier
- generated targets
- evaluator rules

Reward-affecting results must be verified by the backend before completion or GitCoins are awarded.

## Review Checklist

Before merging content changes:

```bash
python scripts/check_seed_targets.py
python scripts/check_generated_targets_current.py
cd backend && python -m pytest curriculum/tests/test_curriculum_chapter_books.py curriculum/tests/test_curriculum_seed_idempotency.py curriculum/tests/test_star_target_reachability.py curriculum/tests/test_solution_replay_guard.py challenges/tests/test_module_challenge_gates.py -q
```
