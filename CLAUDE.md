# GIT it!

Scenario-driven Git learning platform. `frontend/` is a React + Vite SPA; `backend/` is Django + DRF with command verification, evaluator, rewards, curriculum seeding, and persistence.

## Read First

- [ARCHITECTURE.md](ARCHITECTURE.md) — layer ownership, project structure, generated API contract, command boundary, theme system, testing strategy, and CI guards.
- [PRODUCT.md](PRODUCT.md) — product purpose, users, brand personality, anti-references, and design principles.
- [DESIGN.md](DESIGN.md) — visual system, tokens, colors, typography, elevation, and component specs.
- [CONTENT_AUTHORING_GUIDE.md](CONTENT_AUTHORING_GUIDE.md) — how to author adventures, challenges, variants, objectives, and generated targets.

## Non-Negotiable Rules

- Do not add deprecated product vocabulary to active code.
- Keep `/docs` absent; root markdown files are the documentation source.
- Do not make backend runtime code depend on frontend source files or assets.
- Do not hand-write user-facing runtime API response shapes in API wrappers; use generated contract types.
- Do not edit generated target states by hand; regenerate them.
- Keep command submission fast on the frontend, but authoritative on the backend.

## Common Checks

```bash
python scripts/check_legacy_terms.py
python scripts/check_architecture_boundaries.py
python scripts/check_css_architecture.py
python scripts/check_seed_targets.py
python scripts/check_api_contract.py
python scripts/check_frontend_api_usage.py
python scripts/check_api_type_adoption.py
python scripts/check_documentation_current.py
```
