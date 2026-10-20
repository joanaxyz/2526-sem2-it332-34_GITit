# Authored curriculum source

This directory is the canonical home for human-authored curriculum definitions:

- `wave_scenarios.md` — extension scenarios (extra wave variants and Challenge
  Gate trials), compiled to `../scenario_bank_waves.json` with
  `python scripts/curriculum/import_revised_scenarios.py --extension`.
- `scenario_fixtures/` — the repository fixture, evaluation rules, and answer
  key for each extension scenario, keyed by scenario ID.
- `challenge_gates.py` — each module's gate: title, narrative, and the
  scenarios behind its Easy, Medium, and Hard trials.

Ownership rules:

1. Edit hand-authored curriculum only under `seed_data/source/`.
2. Keep deterministic generated artifacts under `seed_data/generated/`.
3. Regenerate generated output through the canonical management command; never
   edit generated files by hand.
4. Keep the seed-idempotency and generated-target checks passing.
