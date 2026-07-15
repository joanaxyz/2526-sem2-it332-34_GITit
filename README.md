# GIT it!

GIT it! is a scenario-driven Git learning platform. It teaches practical Git problem-solving through a simulated terminal, a live repository-state visualization, and backend-verified completion checks inside a consequence-safe practice environment.

The repository is split into two primary applications:

- `frontend/` — React + Vite single-page application.
- `backend/` — Django + Django REST Framework API, simulator/verification boundary, evaluator, curriculum seeding, rewards, and persistence.

## Current Product Vocabulary

Use these terms consistently:

- `Story` — a learning path.
- `Chapter` — a section within a story.
- `Lesson` — short conceptual reading.
- `Adventure` / `Wave` — guided battle-style practice.
- `Challenge` / `Trial` — independent state-based practice.
- `Level map` — the visual chapter navigation surface.
- `Story world` — site/map visual bundle.
- `Companion` — player-side battle/avatar cosmetic.

Compatibility for old bookmarks is isolated in `frontend/src/shared/navigation/legacyRoutes.ts`. New code should not introduce deprecated product vocabulary.

## Architecture Rules

The current source of truth is [ARCHITECTURE.md](ARCHITECTURE.md). The most important rules are:

- Backend owns persisted state, reward decisions, command integrity, schema validation, semantic slugs, and API contracts.
- Frontend owns presentation, animation, optimistic command feedback, and visual asset resolution.
- Shared frontend modules must not import feature modules.
- Feature modules may import `shared`, but non-page modules must not import feature `pages`.
- Backend runtime code must not inspect frontend source or visual assets.
- Generated data must say how it is regenerated.
- Runtime API wrappers must use the generated API contract helper.

## Frontend Structure

```txt
frontend/src/
  app/                  router, layouts, providers
  features/             product features: adventures, challenges, shop, story-map, etc.
  shared/               cross-feature API, auth, battle, cosmetics, simulator, UI utilities
  styles/               base tokens and feature CSS
```

Feature folders follow this pattern:

```txt
feature-name/
  api/
  components/
  hooks/
  pages/
  types.ts
  utils/
```

## Backend Structure

```txt
backend/
  common/               shared backend schemas, command boundary, utilities
  simulator/            simplified Git state normalization/parity helpers
  evaluation/           state-based objective evaluation
  adventures/           adventure runtime API/services/tests
  challenges/           challenge runtime API/services/tests
  practice/             practice command execution services/tests
  curriculum/           authored and generated learning content
  shop/                 cosmetics catalog, ownership, and equipment
```

Django views stay thin: parse the request, call a service, return a response. Business logic belongs in services/helpers with focused tests.

## Command Execution Boundary

Frontend command simulation remains instant for user experience. Backend verification is authoritative for persisted progress, rewards, and completion state.

```txt
user command
↓
frontend simulator gives immediate UI feedback
↓
frontend submits command + proposed next_state
↓
backend validates JSON shape and verifies the state transition
↓
backend awards or rejects persisted progress
```

## Local Development

### Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate  # Windows PowerShell/CMD
pip install -r requirements-dev.txt
python manage.py migrate
python manage.py runserver
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Validation Commands

Backend:

```bash
cd backend
ruff check .
python -m pytest -q
```

Frontend:

```bash
cd frontend
npm run api:check
npm run api:usage-check
npm run api:type-adoption-check
npm run lint
npm run lint:dead
npm test
npm run build
```

Repository-level fast guard suite:

```bash
python scripts/check_quality_gates.py
python scripts/check_repository_artifacts.py
```

Individual repository-level guards:

```bash
python scripts/check_legacy_terms.py
python scripts/check_architecture_boundaries.py
python scripts/check_css_architecture.py
python scripts/check_seed_targets.py
python scripts/check_api_contract.py
python scripts/check_frontend_api_usage.py
python scripts/check_api_type_adoption.py
python scripts/check_documentation_current.py
python scripts/check_ci_quality_gates.py
python scripts/check_django_deploy.py
```

Generated target replay check, after frontend dependencies are installed:

```bash
python scripts/check_generated_targets_current.py
```


## Packaging

Create a clean review zip without runtime/build artifacts:

```powershell
python scripts/clean_repository_artifacts.py
python scripts/check_repository_artifacts.py
python scripts/package_source_zip.py git-it-clean.zip
```
