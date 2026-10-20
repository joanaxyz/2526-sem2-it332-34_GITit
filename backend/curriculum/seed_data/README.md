# Curriculum seed data

`seed_curriculum` seeds the current Arcane Spire Module 0-4 curriculum: each
level's difficulty tiers, their ordered waves and variants, and each module's
Challenge Gate. It writes only the tier and gate models.
`scenario_bank.json` owns the main authored scenario contract and
`scenario_bank_waves.json` the extension scenarios (extra wave variants and
gate trials), both compiled from `source/*.md` by
`scripts/curriculum/import_revised_scenarios.py`. `scenario_bank.py` reads both
banks. `scenario_runtime.py` joins the main bank to the canonical command's
cases, and `source/scenario_fixtures/` joins each extension scenario to its
repository fixture. `source/wave_plan/` places every scenario in its level,
tier and wave, in play order; gate composition lives in
`source/challenge_gates.py`. The stable story/chapter/level scaffold is owned
by the canonical command.

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
