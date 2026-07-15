# Architecture Notes

This file is the root-level architecture guide for GIT it!. `/docs` is intentionally absent; the current rules live in the root markdown files so contributors do not have to choose between duplicate documentation sources.

## Domain Glossary

Use these terms in product copy, code names, tests, and seed data:

- `Story` — a learning path.
- `Chapter` — a section inside a story.
- `Lesson` — short conceptual reading attached to a chapter.
- `Adventure` — guided practice made of ordered levels and waves.
- `Wave` — one scenario inside an adventure level.
- `Challenge` — independent assessment practice.
- `Trial` — an easy, medium, or hard scenario inside a challenge.
- `Level map` — the visual chapter navigation surface.
- `Story world` — a site/map visual bundle.
- `Companion` — a player-side battle/avatar cosmetic.
- `GitCoin` — the reward currency.

Deprecated labels from earlier refactors must not appear in active code or current documentation. Historical URL compatibility remains isolated in `frontend/src/shared/navigation/legacyRoutes.ts` and its test only.

## Layer Ownership

Backend owns:

- persistence
- account/session state
- reward and completion decisions
- command transition verification
- JSON schema validation for runtime state
- semantic slugs for sellable/equippable items
- OpenAPI response/request contracts

Frontend owns:

- route presentation
- optimistic command feedback
- animation and battle choreography
- visual asset selection
- cosmetic rendering
- generated TypeScript consumption of backend contracts

The backend may store and return semantic values such as `arcane-spire`, `blue`, or `main`. It must not inspect frontend source folders or image directories to decide domain behavior.

## Frontend Import Rules

- `shared/*` may not import `features/*`.
- `features/*` may import `shared/*`.
- Feature `pages/*` compose feature components/hooks/API.
- Feature components/hooks/utils must not import feature pages.
- Cross-feature imports should be rare and should usually move through `shared/*` if the code is truly shared.
- User-facing runtime API wrappers must call `apiOperationRequest(operationId, runtimePath, ...)`.
- API wrapper request/response types must compose generated contract types; UI-only rich domain types belong in feature `types.ts` files.

## Normalized Frontend Shape

Frontend features use this shape:

```txt
frontend/src/features/<feature>/
  api/
  components/
  hooks/
  pages/
  utils/
  types.ts
```

Feature roots stay thin: only `types.ts` and `index.ts` belong at the feature root. Implementation belongs in `api/`, `components/`, `hooks/`, `pages/`, or `utils/`.

Large visual surfaces should be decomposed into colocated subpackages instead of letting route or shared component files grow into monoliths. Examples:

```txt
frontend/src/shared/level/components/live-dag/
frontend/src/shared/level/components/project-structure/
frontend/src/shared/battle/effects/skill-effects/
frontend/src/features/authoring/components/levels-editor/
frontend/src/features/authoring/utils/authoring-model/
frontend/src/features/story-map/components/path/
```

The top-level page/component should read as composition. Rendering sections, pure graph/build helpers, animation catalogs, and form editors belong in named child modules with focused responsibilities. The architecture guard now fails non-generated, non-test frontend modules above the reviewability threshold so large files are split before they become new god components.

## Backend Rules

- Views stay thin: parse request, call service, return response.
- Business logic belongs in services/helpers with focused tests.
- Read/query helpers belong in selectors when they grow beyond simple ORM calls.
- Reward-affecting command submissions go through `common.git.client_command_execution`.
- Git transition verification goes through `common.git.command_transition_verifier`.
- Runtime JSON shapes go through `common.schemas.schema_validation`.
- Build-time generated curriculum files must include regeneration instructions.

Backend common code is split by role:

```txt
backend/common/git/       command execution, transition verification, repository state
backend/common/runtime/   cross-mode command budgeting, rule counts, and session helpers
backend/common/schemas/   runtime JSON payload validation
backend/common/services/  shared infrastructure helpers
```

Apps with business logic use a service package entrypoint, not a flat service module. Service and selector package `__init__.py` files are public export surfaces only; implementation belongs in named modules such as `runs.py`, `commands.py`, `history.py`, `state_requirements.py`, or `core.py`. The architecture guard fails oversized service/selector package initializers so implementation cannot drift back into `__init__.py`.

Large visual/runtime surfaces must decompose by role before they become feature god files:

```txt
Component.tsx                  composition + prop wiring only
component-name/                focused child views and pure helpers
shared/battle/effects/...      playback cores split by DOM helpers, layer playback, companion playback, monster playback
```

Human-authored curriculum data lives under `backend/curriculum/seed_data/source/` while the public `backend/curriculum/seed_data/*.py` modules remain thin compatibility re-exports. Generated artifacts remain under `backend/curriculum/seed_data/generated/` and must not be hand-edited. The largest scenario modules (`adventure_levels`, `challenges`, and `blueprint_overlay`) have been moved under `source/`; the next improvement is splitting those source files by chapter/module instead of leaving them as large source modules.


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

This keeps command submission responsive while preventing forged reward-affecting state.

## API Contract

The committed API contract lives in:

```txt
frontend/src/shared/api/generated/openapi.json
frontend/src/shared/api/generated/apiTypes.ts
```

Regenerate it with:

```bash
python scripts/generate_api_contract.py
```

CI rejects stale contract files with:

```bash
python scripts/check_api_contract.py
```

Critical runtime operations must use named response components, not anonymous `object` schemas. The contract guard currently enforces this for challenge runs, adventure runs, shop cosmetics, wallet, dashboard, stats, skills, payments, and command-form preview endpoints.

Frontend runtime wrappers are guarded by:

```bash
python scripts/check_frontend_api_usage.py
python scripts/check_api_type_adoption.py
```

## StoryWorld System

Story worlds are the site/map visual bundles. Their names and visual tokens are semantic. Current story-world (theme) metadata lives under `frontend/src/shared/cosmetics/themes/` and is registered through `frontend/src/shared/cosmetics/registry.ts`.

Rules:

- Do not register a story world until it has a real name, assets, and backend/shop semantics.
- Companions are independent from story worlds.
- Story-world CSS uses semantic tokens such as `--theme-primary-rgb`, `--theme-secondary-rgb`, `--theme-accent-rgb`, `--theme-surface-rgb`, `--theme-glow-rgb`, and `--level-map-bg`.
- CSS files stay split and reviewable; `scripts/check_css_architecture.py` enforces file-size and legacy-reference limits.

## Generated Curriculum Targets

`backend/curriculum/seed_data/generated/generated_targets.py` is committed generated output. It exists so normal curriculum seeding can compare repository states without replaying every authored solution at runtime.

Rules:

- Humans edit authored source modules under `backend/curriculum/seed_data/source/` when changing shared fixtures, routing, adventure levels, challenges, and blueprint overlays. Public modules such as `seed_data/adventure_levels.py`, `seed_data/challenges.py`, and `seed_data/blueprint_overlay.py` are compatibility wrappers only.
- The large curriculum ledgers are partitioned by responsibility:
  - `source/adventure_level_specs/` composes authored adventure waves by chapter plus blueprint-generated waves.
  - `source/challenge_specs/` composes current blueprint challenges and legacy challenge batches.
  - `source/blueprint/` stores blueprint adventure ledgers in smaller adventure-family modules.
- Humans do not edit files under `backend/curriculum/seed_data/generated/` directly.
- After changing a variant initial state, solution commands, or workspace-file edits, run `cd backend && python manage.py generate_targets`.
- `scripts/check_seed_targets.py` is the cheap structural guard.
- `scripts/check_generated_targets_current.py` is the full replay guard and requires `frontend/node_modules`. CI runs it in a dedicated Python + Node job.

## Testing Strategy

Shared runtime fixtures belong in `backend/testing/*`, not copied across test files.

Backend tests must cover:

- forged command payload rejection through real API endpoints
- command-budget edge cases
- reward idempotency for challenge and adventure completion
- shop theme/companion separation
- unknown/unowned cosmetic rejection
- seed idempotency
- generated target consistency
- runtime JSON schema validation

Frontend tests must cover:

- generated-contract API wrapper behavior
- route compatibility isolation
- shop theme/companion display separation
- auth refresh race behavior
- battle outcome behavior derived from `command_outcome`
- shared level-runtime helpers used by both Challenge and Adventure command sessions, including exit-command detection and completion-animation gating

## Compatibility

Compatibility exists only for old bookmarks and must stay isolated to the route layer. It must not leak into API contracts, CSS tokens, shop data, seed data, or feature implementation.

## CI Guards

- `scripts/check_legacy_terms.py` blocks removed vocabulary from active code and root markdown.
- `scripts/check_architecture_boundaries.py` blocks forbidden imports, runtime cross-app coupling, oversized service/selector package initializers, oversized production frontend modules, stale migration files, and oversized public seed-data modules.
- `scripts/check_css_architecture.py` keeps CSS split into reviewable files and blocks legacy product references.
- `scripts/check_api_contract.py` proves committed OpenAPI JSON and generated TypeScript endpoint/request/response types are current.
- `scripts/check_frontend_api_usage.py` keeps runtime API wrappers on the generated contract helper.
- `scripts/check_api_type_adoption.py` keeps runtime API wrapper types composed from generated schemas.
- `scripts/check_seed_targets.py` keeps committed target keys and repository-state shapes consistent with authored variants.
- `scripts/check_generated_targets_current.py` replays authored solutions through the real simulator and verifies generated targets are current.
- `scripts/check_documentation_current.py` keeps root documentation current and prevents a second `/docs` source from reappearing.
- `scripts/check_ci_quality_gates.py` proves the CI workflow and package scripts still run the required guards.
- `scripts/check_quality_gates.py` runs the fast repository guards from one local command.
- `scripts/check_django_deploy.py` runs Django deployment checks with production-like required settings.


Repository artifact guard: `python scripts/check_repository_artifacts.py`.


## Source packaging

Use `python scripts/clean_repository_artifacts.py` before packaging and `python scripts/package_source_zip.py <output.zip>` when sharing the project. The packager excludes cache/build artifacts such as `__pycache__`, `.pytest_cache`, `node_modules`, and `dist`.

## Current Migration Policy

This handoff intentionally clears committed Django migration files while keeping every app's `migrations/__init__.py`. Recreate migrations from the current models with `python manage.py makemigrations` in the target environment before applying them.

Rules:

- Keep `migrations/__init__.py` so Django still recognizes each migration package.
- Do not preserve stale migration history while the schema is still being actively reshaped.
- Regenerate migrations after pulling this package and before running `migrate`.

## Curriculum Selector Decomposition

`backend/curriculum/selectors/core.py` is now a compatibility export surface. Implementation is split by read-model responsibility:

- `tracks.py` for track/chapter locks and completion checks.
- `progress_counts.py` for chapter completion numerator/denominator maps.
- `content.py` for chapter content page/overview payload assembly.
- `command_skills.py` for command-skill query and learned-spellbook rows.
- `book.py` for Chapter Book payloads.
- `challenge_queries.py` for challenge query shape.
- `adventure_access.py`, `challenge_access.py`, and `access_helpers.py` for user-specific access state.

New selectors should go into the narrow module that owns their query/payload responsibility, not back into `core.py`.
