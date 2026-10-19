# Curriculum seed data

`seed_curriculum` seeds the current Arcane Spire Module 0-4 curriculum.
`scenario_bank.json` owns its authored scenario contract, `scenario_bank.py`
reads that contract, and `scenario_runtime.py` joins it to repository fixtures.
The stable story/chapter/level scaffold is owned by the canonical command.

The retired multi-story fixtures in `stories.py`, `chapters.py`, `lessons.py`,
`adventure_levels.py`, and `challenges.py` are used by the explicitly named
`seed_curriculum_fixture` command, which is disabled outside isolated tests.

Generated artifacts are isolated under `generated/`.

`generated/generated_targets.py` is committed generated output. It exists so
normal seeding and runtime evaluation can compare learner repository states
against stable target states without replaying every solution during startup.

Regenerate it after changing any variant's `initial_state_template`,
`solution_commands_template`, or `solution_workspace_files_template`:

```bash
cd backend
python manage.py generate_targets
```

Run the cheap structural consistency check:

```bash
python ../scripts/check_seed_targets.py
```

Run the full replay freshness check after installing frontend dependencies:

```bash
cd ../frontend
npm ci
cd ..
python scripts/check_generated_targets_current.py
```

Rules:

- edit authored seed modules, not files under `generated/`;
- every variant `case_id` must have one generated target;
- generated target states must keep valid repository-state container shapes;
- the replay check must pass before merging curriculum solution changes.
