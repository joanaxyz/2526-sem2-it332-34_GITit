# GIT it! — Content Authoring Guide

This guide explains how to author curriculum content that teaches Git through scenario practice and remains compatible with backend verification, generated target states, and the frontend simulator.

## Content Types

| Type | Purpose | Shape | Completion |
|---|---|---|---|
| Lesson | Explain a concept briefly before practice | Chapter book pages | Read/progress state |
| Adventure | Teach command mastery through guided scenarios | Levels → waves → variants | Wave objectives + verified state |
| Challenge | Assess transfer on new scenarios | Easy/medium/hard trials → variants | Whole-state evaluation |

## Authoring Principles

1. **Introduce, then compose.** First exposure to a command may be a small single-command wave. After that, prefer multi-command workflows.
2. **Repeat commands in new scenarios.** Mastery comes from revisiting command forms in different repository states, not from repeating the same story.
3. **Never repeat scenarios.** Commands repeat; narrative setup and initial repository state should not.
4. **Challenges must change repository state.** A challenge trial should visibly change commits, branches, refs, or HEAD.
5. **Author the ideal scenario.** If the simulator lacks a needed behavior, improve the simulator and verifier rather than weakening the curriculum.
6. **Variants must test the same skill.** Two variants may use different file names/story details, but they should share the same learning goal and objective shape.

## Adventure Authoring

Adventure data lives in `backend/curriculum/seed_data/adventure_levels.py`.

A wave should define:

- stable usage key
- stable slug
- learner-facing title/story/task
- two variants
- solution commands
- objective checks, when the wave is guided
- prerequisites, when order matters

A level groups waves through `ADVENTURE_LEVEL_PLAN`. Keep the plan in sync whenever adding, renaming, or removing waves.

## Challenge Authoring

Challenge data lives in `backend/curriculum/seed_data/challenges.py`.

Each challenge should have:

- easy, medium, and hard trials
- two variants per trial
- a new scenario not copied from adventures
- a repository-state transition that changes the DAG or refs
- fading scaffold from easy to hard
- evaluation specs that verify final state instead of command text alone

## Objective Checks

Guided adventure objectives should be:

- **Modular** — one visible checklist row per meaningful step.
- **Variant-safe** — do not hard-code a file/branch/commit that differs between variants.
- **End-state based** — false at the start, true only after the learner completes the step.

Avoid premature-pass checks such as `staging_empty: true` unless the initial state makes that meaningful.

## Story Briefs and Exact Values

The learner must never have to guess an arbitrary literal that evaluation requires.

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

Do not edit generated targets directly. After changing initial state, solution commands, or workspace edits, run:

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
cd backend && python -m pytest curriculum/tests/test_objective_soundness.py curriculum/tests/test_seed_curriculum_idempotency.py -q
```
