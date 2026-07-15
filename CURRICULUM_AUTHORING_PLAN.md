# Curriculum Authoring Plan

This plan defines how to keep the scenario curriculum maintainable as chapters grow. The detailed authoring rules live in [CONTENT_AUTHORING_GUIDE.md](CONTENT_AUTHORING_GUIDE.md).

## Goal

Each chapter should teach Git through a progression of lessons, adventures, and challenges:

1. Lessons introduce the mental model.
2. Adventures teach commands through guided scenarios.
3. Challenges assess transfer on brand-new, state-changing scenarios.

The curriculum should make learners reason about repository state instead of memorizing command strings.

## Chapter Shape

Each chapter should contain:

- short lessons attached to the chapter book
- one adventure sequence with ordered levels and waves
- one challenge with easy, medium, and hard trials
- two variants per wave/trial for anti-memorization
- generated target states for every variant

## Adventure Progression

Adventure levels should follow this rhythm:

1. First exposure: small focused wave when a command is new.
2. Workflow practice: combine introduced commands into realistic scenarios.
3. Spiral reuse: revisit earlier forms in new repository states.
4. Review: combine the chapter’s important forms before the challenge.

Single-command waves are allowed only when they introduce a new command form or isolate a concept that would otherwise be confusing.

## Challenge Progression

Each challenge should contain:

- **Easy** — smaller DAG/state transition, more scaffold.
- **Medium** — larger workflow, less scaffold.
- **Hard** — chapter-level synthesis with minimal scaffold.

Every trial must change repository state. Challenge scenarios should not duplicate adventure scenarios.

## Scenario Ledger Rule

Every scenario should be unique in at least two of these dimensions:

- narrative setup
- initial repository state
- file paths/content
- branch/ref topology
- target DAG shape

Commands can repeat freely; scenarios should not.

## Generated Target Workflow

When editing curriculum variants:

```bash
cd backend
python manage.py generate_targets
python ../scripts/check_seed_targets.py
python ../scripts/check_generated_targets_current.py
```

The cheap structural guard validates keys and repository-state containers. The full replay guard verifies that committed generated targets match the current authored scenarios and simulator behavior.

## Verification Gates

Before calling a chapter ready, run:

```bash
python scripts/check_seed_targets.py
python scripts/check_generated_targets_current.py
cd backend
python -m pytest curriculum/tests/test_objective_soundness.py curriculum/tests/test_seed_curriculum_idempotency.py -q
```

Also run the command-boundary tests when a scenario introduces simulator behavior that affects rewards:

```bash
cd backend
python -m pytest practice/tests/test_command_executor.py challenges/tests adventures/tests -q
```

## Completion Criteria

A chapter is ready when:

- lessons explain the commands needed by the practice
- adventures introduce and reuse chapter command forms
- challenge trials are new, state-changing, and difficulty-scaled
- every variant has a generated target
- backend evaluator confirms target matches
- seed and generated-target guards pass
