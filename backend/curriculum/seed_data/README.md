# Curriculum seed data

This folder contains the authored curriculum fixtures used by `seed_curriculum`.
The source-of-truth modules are the authored seed files such as `stories.py`,
`chapters.py`, `lessons.py`, `adventure_levels.py`, and `challenges.py`.

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
