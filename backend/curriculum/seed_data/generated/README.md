# Generated curriculum data

This package contains generated artifacts only.

`generated_targets.py` is produced by:

```bash
cd backend
python manage.py generate_targets
```

The replay generator uses the frontend TypeScript Git simulator via
`frontend/scripts/generate-targets.mjs`, so regeneration requires both backend
Python dependencies and frontend Node dependencies.

Use this cheaper structural guard during normal backend checks:

```bash
python scripts/check_seed_targets.py
```

Use this full replay guard when validating a curriculum change end-to-end:

```bash
cd frontend && npm ci
cd ..
python scripts/check_generated_targets_current.py
```

Do not edit files in this package by hand.
