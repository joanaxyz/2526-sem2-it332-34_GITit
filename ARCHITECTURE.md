# Architecture Notes

This file is the root-level architecture guide for GIT it!. Current architecture and contributor rules live in the root markdown files. Keep temporary planning notes and supporting artifacts local and out of the source repository.

## Domain Glossary

Use these terms in product copy, code names, tests, and seed data:

- `Story` — a learning path.
- `Chapter` — a section inside a story.
- `Lesson` — short conceptual reading attached to a chapter.
- `Adventure` — guided practice made of ordered levels.
- `Tier` — the Easy, Medium, or Hard difficulty of an adventure level, made of ordered scenarios.
- `Scenario` — one stage of a tier; each run of it serves one of its variants.
- `Challenge` — independent assessment practice.
- `Challenge Gate` — a module's closing challenge: a workflow testing what the module taught.
- `Trial` — an easy, medium, or hard scenario inside a challenge.
- `Drill` — optional recall practice attached to an adventure level (Squire's Drill).
- `Level map` — the visual chapter navigation surface.
- `Story world` — a site/map visual bundle.
- `Companion` — a player-side battle/avatar cosmetic.
- `GitCoin` — the reward currency.

Deprecated labels from earlier refactors must not appear in active code or current documentation. Current URLs live in `frontend/src/shared/navigation/routes.ts`; obsolete aliases and their redirect handlers have been removed.

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

Shared run workspace mutations and active-run deletion live in common helpers so
Adventure and Challenge do not maintain parallel locking/status implementations.
Domain services keep orchestration and public terminology; shared helpers own the
transactional primitive.

Apps with business logic use a service package entrypoint, not a flat service module. Service and selector package `__init__.py` files are public export surfaces only; implementation belongs in named modules such as `runs.py`, `commands.py`, `history.py`, `state_requirements.py`, or `core.py`. The architecture guard fails oversized service/selector package initializers so implementation cannot drift back into `__init__.py`.

Large visual/runtime surfaces must decompose by role before they become feature god files:

```txt
Component.tsx                  composition + prop wiring only
component-name/                focused child views and pure helpers
shared/battle/effects/...      playback cores split by DOM helpers, layer playback, companion playback, monster playback
```

`seed_curriculum` owns the module levels and their tiers (`MODULE_LEVELS`). Scenario content comes from the committed banks `backend/curriculum/seed_data/scenario_bank.json` and `scenario_bank_extension.json`; the extension bank's Markdown, repository fixtures, and the Challenge Gate composition live under `backend/curriculum/seed_data/source/`. Generated artifacts remain under `backend/curriculum/seed_data/generated/` and must not be hand-edited.


## Command Execution Boundary

### Learning tutor boundary

The `tutoring` backend app owns two independent tutors behind authenticated
`POST /api/tutoring/chat/`. Both write free-text replies (Gemini, then Groq) from a
system prompt and the conversation so far: the client sends both sides of recent
turns, so follow-ups and clarifications refer to earlier answers.

- **Home** is a general Git and GIT it! platform tutor. It is not tied to the command guide.
- **Workspace** help belongs to the open command guide: it explains that guide's
  usage form, and the run's public task is context.

Scenario retrieval is the gate (RAG over public seed fields only). Every learner turn
in the conversation is checked lexically and against the committed semantic index.
Lexical matching reads inline code as plain words, so a task copied from the rendered
brief matches as well as its Markdown source. A pasted task is a match; close wording
or a close semantic score is a match only when the turn also names something
particular to that scenario (a multi-word name its brief marks as code and few briefs
share, such as `research-log`), because general questions score as close. Home does
not discuss a match: it replies with a fixed message that asking about scenarios is
not allowed there, without calling a provider, and leaves that turn and its reply out
of later turns so the next question stands alone. A close but unnamed, uncertain or
unavailable lookup switches Home into scenario protection instead: teach the ideas,
use placeholders, never solve or walk through the task; such a turn keeps later turns
protected. Workspace help (the command guide's Ask Git-It) is never declined and
always protected. Protected replies pass the answer guard
(`tutoring/services/answer_guard.py`): the matched scenarios' and the run's answer
fields stay server-side and are never prompted. A reply that names a
task value, writes it into a command, or covers the solution's command sequence is
regenerated once with a stricter instruction, then replaced by a fixed teaching
message. Validated replies are cached by prompt digest. Provider attempts use
bounded time and cached rate-limit cooldowns over one pooled keep-alive client per
process. An attempt still silent after a short hedge delay keeps running while the
next model starts; the first usable reply wins and passes the same guard, and the
outrun model sits out briefly. The committed semantic index is cached locally; see
[index regeneration](backend/tutoring/data/README.md).

Workspace chat requires an owned run and a server-signed safe guide context.
Guide payloads generalize prospective changes and omit exact command examples;
completion tokens contain a context digest instead of evaluation data. Internal
lesson identity remains stable; literal-bearing outward IDs are opaque.
Verified terminal feedback, command accounting and rewards retain their owners.

`frontend/src/shared/tutoring/` owns reusable chat presentation (light Markdown:
paragraphs, code, lists, inline marks) and bounded, sign-in-scoped in-memory
conversations. A Home reply declining a scenario carries a short caption. HomeLayout composes the floating chat launcher
across Dashboard, Modules and Shop. The command guide owns the lifetime of a
separate fixed chat window, rendered outside its card with a portal. Both surfaces
use the earlier Ask Blue header portrait, message bubbles, suggested questions,
composer and footer. The panel has responsive viewport bounds and normal transcript
scrolling, without dragging, manual resizing or stored geometry. The external
portrait launcher retains the visible "Ask Git-It" label and appears when collapsed.
The decorative mascot preference does not disable help controls.

General chat uses the mascot portrait and the "Ask Git-It" floating launcher.
The separate roaming learning mascot continues offering earned Git tips while
chat is open; the reader's own mascot-hiding preference remains respected.

Both tutor surfaces offer bundled FAQS with reviewed general Git explanations.
Network failures and unavailable provider replies show a recovery panel in Chat,
with an explicit Retry and access to saved explanations. Rate-limit responses carry
an optional reason and retry interval; the countdown is shared across tutor windows
within a sign-in session and never automatically sends a question. Drafts survive closing the window within
the sign-in session; only completed exchanges enter conversation history. New replies
follow the transcript only when the learner is near its bottom.
Recognition, generation and a guarded rewrite share a 30-second backend budget;
the browser cancels stalled chat requests after 40 seconds and ignores late replies.

`tutoring/services/platform_knowledge.py` supplies reviewed public platform facts and
live published chapter names, including for recent-topic follow-ups. It does not read
learner scores, scenario answers or evaluator data. Facts enter the system prompt and
its cache digest after Home's scenario-decline gate; existing answer guards still apply.

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

Completion is graded on the resulting repository state, never on the commands typed. The transition check above keeps that state honest; the scenario's `state_requirements` then decide whether it is solved, so any Git route that reaches the same state passes. Published curriculum scenarios use no typed-command rules (`required_command`, `required_command_sequence`) and no records of how an operation ran (`operation_metadata_*`); `curriculum/tests/test_scenario_bank_content.py` enforces it. Where a wrong route would reach the right state only because the simulator is more lenient than Git, the simulator is fixed instead. For that reason both engines:

- record where `init` or `clone` put the repository (`repository_root`);
- reject a push that would drop the server's commits, and a lease push once the server moved after the last fetch;
- write Git's `checkout: moving from X to Y` HEAD reflog entry on every switch.

### Workspace Terminal Shell

The terminal also runs a small shell (`frontend/src/shared/git/simulator/shell/`): `pwd ls cd tree cat echo clear` are read-only diagnostics, and `touch mkdir rmdir rm mv cp` plus `echo`/`cat` with `>`/`>>` change the working copy. Shell commands never spend the command budget. File-changing ones are replayed by `backend/common/git/shell_commands.py` from the persisted state through the same `workspace_files` helpers as the Project Files endpoints; the backend's replay, not the browser's `next_state`, becomes the run state.

- The working directory belongs to the terminal, not the repository: it is stored per run on the frontend (`level-runtime/terminalCwd.ts`) and sent as `execution.cwd`. It never enters `repository_state`, so `cd` cannot affect evaluation such as `repository_state_unchanged`.
- Git reads pathspecs relative to that directory. `gitPathspecs.ts` and `backend/common/git/git_pathspecs.py` rewrite them to project-root paths before simulation and transition verification, including the folder `git init` and `git clone` create a repository in.
- Folders with no files live in the optional `directories` list of `repository_state` (omitted when empty). Git ignores them; the Project Files tree shows them, and it hides deleted files unless they are conflicted. A folder emptied by deleting its last file stays on disk.

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

Critical runtime operations must use named response components, not anonymous `object` schemas. The contract guard currently enforces this for challenge runs, adventure runs, shop cosmetics, wallet, dashboard, stats, skills, and command-form preview endpoints.

Frontend runtime wrappers are guarded by:

```bash
python scripts/check_frontend_api_usage.py
python scripts/check_api_type_adoption.py
```

### Performance metrics

`GET /api/progress/performance/` returns Arcane Spire Modules 1–4 mastery metrics.
`MetricsService._performance_summary_for_runs()` is the response owner and delegates
arithmetic to `progress/services/mastery_metrics.py`. Dashboard KPI fields use the
same owner. Ordinary run/session totals and the Stats finish-rate diagnostic remain
activity measures. Replay and transfer runs do not create practice mastery credit;
CAR alone reads replays.

The five official KPIs, targets, formulas, Let definitions, reference-validation
commands and fixed-cohort evaluation workflow are documented in
[KPI_METHODOLOGY.md](KPI_METHODOLOGY.md). SCR/HLCR count unique required tiers;
CAR averages each scenario's command efficiency against a validated reference on
the learner's latest clear of content they had not cleared before (replays
included), with `car_first` from each scenario's first such clear as its learner-facing starting point; ARC
counts unsuccessful attempts before mastery; RTA preserves the first result on
reserved unseen transfer checkpoints in Modules 3–4. The supplementary Retry
Success Rate counts concluded recovery retries after actual unsuccessful attempts.
Its deprecated `rtr` response alias has no current UI consumer.

`KpiCheckpoint` preserves assessment evidence separately from mutable best-star
completion pointers. Runs snapshot validated reference counts and content hashes.
`KpiExposure` records every presentation, including discarded empty launches;
legacy incomplete exposure histories cannot establish transfer novelty. Explicit
transfer starts use the existing access-checked tier-start route, bypass practice
reward/mastery mutation, and hide answer scaffolding.

Learner, Admin aggregate and Admin per-player reads share formulas. Admin excludes
staff and averages participant scores; date filters select Manila-time starts,
with assessment outcomes after the range end excluded. Formal studies have fixed
assignments, requirements, references, module weights and cutoff, and freeze their
report through `kpi_study`. They include unattempted assignments at cutoff and
report unavailable evidence separately.

`RateMetric.value` is authoritative. Mean CAR uses a fractional numerator of summed
percentage points. Cohort rates carry `unit: participants`; sample metadata reports
coverage. Null/no observations is distinct from measured zero. Module responses
include CAR. Learner comparisons are descriptive; Admin retains approved objective
overrides, including Module 4 HLCR ≥65% and ARC ≤3.

`features/performance/utils/performanceKpis.ts` owns shared display-only labels,
formulas, explanations, evidence units, targets and formatting. There is no
standalone Performance route: Home Progress's `HomeResultsPanel()` fetches on
demand and passes the ready response to `LearnerPerformanceInstrument`.

### Home Overview composition

Home opens on Profile. The `view` search parameter selects `profile`, `progress`, or `skills`; saved `results` links resolve to Progress. `HomeHubView` owns that URL state and the category switcher.

| Owner | Responsibility |
| --- | --- |
| `HomeStatsView.tsx` | Builds the pure model once and composes the active Progress or Skills bands |
| `home-stats/homeStatsModel.ts` | Derives activity, active-curriculum context, skills, and achievements; no performance KPI model |
| `home-hub/homeViews.ts` | Category catalog and legacy alias resolution |
| `home-hub/HomeViewSwitcher.tsx` | Accessible category dropdown |
| `home-stats/HomeProgressPanel.tsx` | Activity and active-curriculum finish-rate context; activity window control |
| `home-stats/HomeResultsPanel.tsx` | No-prop query boundary for the performance instrument; recoverable loading/error states |
| `performance/components/LearnerPerformanceInstrument.tsx` | Ready-data presentation; local measure selection, descriptive module comparison, native calculation disclosure |
| `home-stats/HomeSkillsPanel.tsx` and `HomeAchievementGallery.tsx` | Skills display and achievement filtering from narrow model slices |

Activity Week/Month/Year affects only the activity request. KPI selection changes local presentation and issues no request. The instrument uses existing dark observatory tokens, meaningful goal traces, earned light, visible evidence, and reduced-motion transitions.

`check_architecture_boundaries.py` enforces one-way composition, the no-prop results boundary, shared KPI semantics, no learner-to-Admin import, no mixed Home/Stats KPI fallback, and deletion of the old record tiles and four-chart module path.

## StoryWorld System

Story worlds are the site/map visual bundles. Their names and visual tokens are semantic. Current story-world (theme) metadata lives under `frontend/src/shared/cosmetics/themes/` and is registered through `frontend/src/shared/cosmetics/registry.ts`.

Rules:

- Do not register a story world until it has a real name, assets, and backend/shop semantics.
- Companions are independent from story worlds.
- Story-world CSS uses semantic tokens such as `--theme-primary-rgb`, `--theme-secondary-rgb`, `--theme-accent-rgb`, `--theme-surface-rgb`, `--theme-glow-rgb`, and `--level-map-bg`.
- CSS files stay split and reviewable; `scripts/check_css_architecture.py` enforces file-size and legacy-reference limits.

## Squire's Drill

Squire's Drill is the rung between reading a chapter and typing at a live
prompt: short recall practice on exactly the commands one adventure level
will ask for. It is optional, gates nothing, and pays no currency.

Drill content is **seed data, not runtime composition**. `manage.py
seed_drills` derives it once and writes rows; runtime reads those rows.

Ownership:

- `backend/drills/services/composer.py` derives every question from
  authored curriculum data, and runs at **seed time only**. Nothing is
  hand-authored per level: cards come from the level's `CommandForm` rows
  (`usage_form` / `label`), and the ordering finale from a scenario variant's
  `solution_commands`. Pass a shared `DrillCatalog` when composing many
  levels so the published command list is read once per run.
- Distractors are always other real command forms, siblings of the same
  command first, so a wrong answer can be explained with authored text.
- When a level has no `command_forms` wired, the composer recovers them by
  resolving the level's authored solution commands through
  `curriculum.library_preview.command_preview_syntax_for_command` and
  matching the published catalog. This keeps a database seeded before that
  wiring existed from producing an empty drill.
- `backend/drills/services/seeding.py` upserts `LevelDrill` /
  `LevelDrillCard` per level, keyed on `(drill, form_key)` so a reseed
  rewrites in place and drops only cards the level no longer teaches.
  `seed_drills` runs last in `seed_all`, after the curriculum, legacy
  modules, and command library it derives from.
- `backend/drills/selectors/content.py` is the only runtime read path.
  `drillable_level_ids` answers "does this level have a drill" from the
  same rows the drill page reads, so the level map and the page cannot
  disagree; the map embeds it as `drill` on each adventure summary.
- `drills.models.DrillRun` checkpoints the in-progress queue after every
  answer so a refresh resumes mid-drill. The stored state is client-owned
  and bounded by `DrillRunStateSerializer`, then intersected with the
  level's seeded card keys — a resumed queue decides which questions
  appear, so unknown keys are dropped rather than trusted.
- `drills.models.DrillProgress` stores per-(player, level) history. The
  client grades itself and reports the session because there is no reward
  to forge; the backend clamps the counts and intersects reported weak
  spots with the level's seeded card keys. A session only counts as a
  clear when every card topped its ladder — running out of attempts ends
  the queue but does not earn the mark.
- The frontend feature is `frontend/src/features/drills`. The queue,
  ladder, rehydration, and grading rules are pure modules under `utils/`
  with tests; entry lives in the story map's level callout.

A fresh install must run `seed_drills` (or `seed_all`) before any drill
appears. That is deliberate: content lives in rows, so an unseeded
database honestly has none rather than synthesising it per request.

## Adventure Tiers and Challenge Gates

- Each `AdventureLevel` has Easy, Medium, and Hard `AdventureLevelTier`s. A tier holds ordered `AdventureLevelTierScenario`s, and each scenario holds ordered variants.
- `seed_data/source/scenario_plan/` owns placement: each level's scenarios per tier, in play order, with their roles and variants. `seed_curriculum` upserts them by slug and unpublishes the scenarios and variants it no longer names; runs keep their rows.
- An `AdventureLevelTierRun` is one attempt at one scenario. One solve clears a scenario; `AdventureLevelTierProgress.cleared_scenario_slugs` records the cleared scenarios, and the tier completes (`AdventureLevelTierCompletion`) once every published scenario is cleared. Starting a tier plays the next uncleared scenario, and a retry rotates variants within that scenario; replay cycles through the scenarios (`adventures/tier_scenarios.py`, `services/tier_runs.py`, `services/tier_variants.py`). A solve on a scenario that a reseed unpublished clears the learner's next uncleared scenario.
- A tier's stars are the lowest of its scenarios' best stars. A run's star budget comes from its variant, falling back to the scenario's (`services/tier_budget.py`).
- Each scenario clear credits mastery to the published forms the clearing run's commands used (`tutoring.services.forms.forms_used_by`). Mastery never opens or closes a command guide.
- `adventures/rewards.py` owns the GitCoin ladder: Easy 25, Medium 35, Hard 50 once per tier, and 50/75/100 for Challenge Gate trials, all through idempotent wallet keys. The one-time cutover commands `award_missing_tier_rewards` and `map_partial_tier_progress` backfill rewards and partial progress (`deploy/CURRICULUM_SCENARIOS_RESEED.md`).
- A level counts as passed on the map and in chapter progress once its Easy tier is complete. Chapter completion counts each published level once plus each published gate trial.
- `seed_curriculum` seeds one Challenge Gate per module from `source/challenge_gates.py`: Easy, Medium, and Hard trials with two variants each. The gate opens once every required level of the module has completed all three tiers (`chapter_tiers_cleared`); inside it, Medium waits for the Easy trial and Hard for Medium. Challenge runs play in the same workspace as adventure tiers (`frontend/src/shared/level/workspace/`): battle stage, terminal, Live and Expected diagrams.
## Generated Curriculum Targets

`backend/curriculum/seed_data/generated/generated_targets.py` is committed generated output. It exists so normal curriculum seeding can compare repository states without replaying every authored solution at runtime.

`generated_trajectories.py` comes from the same replay. For every solution command it stores fingerprints of the repository in front of that command (`simulator/trajectory.py`), seeded onto each variant as `solution_trajectory`. Fingerprints describe repository meaning (trees, ancestry, refs, index, working tree, conflicts, stash, in-progress operations), not generated commit ids or `last_*` bookkeeping; an `exact` strength also covers file contents and commit messages, a `coarse` strength does not.

Rules:

- Humans edit `MODULE_LEVELS` in `seed_curriculum`, the scenario Markdown compiled by `scripts/curriculum/import_revised_scenarios.py`, and the scenario plan, fixtures and gate composition under `backend/curriculum/seed_data/source/`.
- `generate_targets` replays every module case and extension scenario, and fails unless the backend transition verifier accepts each replayed command (`solution_replay.verify_backend_transitions`), so a published answer key can always be submitted live.
- Humans do not edit files under `backend/curriculum/seed_data/generated/` directly.
- After changing a variant initial state, solution commands, or workspace-file edits, run `cd backend && python manage.py generate_targets`. It rewrites both generated targets and trajectories. Seeding counts each published tier variant's KPI command reference from its trajectory, so references never go stale after a reseed.
- `scripts/check_seed_targets.py` is the cheap structural guard.
- `scripts/check_generated_targets_current.py` is the full replay guard and requires `frontend/node_modules`. CI runs it in a dedicated Python + Node job.

## Command Introductions

`backend/tutoring` teaches around the learner's next move (`tutoring/services/planner.py`). The planner locates the learner's repository on the variant's `solution_trajectory` (learner history resolves routes that revisit a state), takes the next non-diagnostic solution command, and resolves it to one command form: scenario forms first, then the published catalog, else a shape derived from the command. Lesson identity is the form's syntax (`form:<usage>`), so the same syntax is one lesson across seeds. Back-to-back path-only steps that one command can do together (`git add a` then `git add b`) are offered as that command (`git add a b`); interactive modes never merge. One-or-more forms (`<path>...`) are separate lessons. Off-route repositories get nothing.

A move teaches two ways:

- **Command guide** — anchored to the form's home: the first published scenario, in play order, whose solution teaches it (`tutoring.CommandGuideHome`, rebuilt by `seed_curriculum` through `tutoring/services/homes.py`; one home per form, and every variant of the home teaches it). The guide opens only in its home, until the learner completes it there; running the command elsewhere or solving with it does not retire it, so playing levels out of order never uses a guide up. Elsewhere, a form whose guide is unfinished gets `guide_elsewhere`: a read-only copy of the guide and where its home is. Each guide carries a part-by-part reading of its syntax (`tutoring/services/anatomy.py`) and the change it makes, with `action` and `subjects` so the client can draw a before/after diagram.
- **Tips** — techniques (`tutoring/services/techniques.py`: several paths, `.`, path patterns, `--`, `HEAD~n`, `a..b`, remote-tracking branches, `@{upstream}`..., keyed `technique:<name>` and recognised by command shape only) and plain-language concepts chosen from what the move changes (`tutoring/services/concepts.py`, keyed `concept:<name>`). Neither belongs to a scenario: tips come with their move every time it comes up, with nothing stored per player. "Got it" puts a tip away for the rest of that run only.

Completed guides are `PlayerCommandIntroduction` rows. Tier runs expose `tutor` (the open guide), `command_guides` (the scenario's completed guides, to read again), `guide_elsewhere` and `tips` (`tutoring/payloads.py`); transfer runs teach nothing. Acknowledgement goes through `POST /api/adventure-tier-runs/{id}/introduction/complete/`, which returns the same teaching fields.

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
- current route destinations and removal of obsolete aliases
- shop theme/companion display separation
- auth refresh race behavior
- battle outcome behavior derived from `command_outcome`
- shared level-runtime helpers used by both Challenge and Adventure command sessions, including exit-command detection and completion-animation gating

## Compatibility

Retired URL aliases have no router registrations or redirect handlers. Navigation uses the current route definitions directly. Historical database identifiers and migrations remain stable; they do not define alternate product routes or seed commands.

## CI Guards

- `scripts/check_legacy_terms.py` blocks removed vocabulary from active code and root markdown.
- `scripts/check_architecture_boundaries.py` preserves the public architecture-check command while `scripts/checks/check_architecture_boundaries.py` owns orchestration, ordering, rendering, and the remaining workflow/general rules. Reusable source analysis and focused Catalog, Auth, Progress, Gameplay request, and Gameplay response policies live under `scripts/checks/architecture_guard/`; policy modules may depend on repository/source-analysis helpers but never on the executable or another domain policy, and the Gameplay response backend/OpenAPI owner depends one-way on its focused frontend analyzer.
- The architecture guard blocks forbidden imports, maintained backend runtime import cycles, restored displaced backend paths, contract-owner drift, oversized service/selector package initializers, oversized production frontend modules, and oversized public seed-data modules.
- `scripts/check_css_architecture.py` keeps CSS split into reviewable files and blocks legacy product references.
- `scripts/check_api_contract.py` proves committed OpenAPI JSON and generated TypeScript endpoint/request/response types are current.
- `scripts/check_frontend_api_usage.py` keeps runtime API wrappers on the generated contract helper.
- `scripts/check_api_type_adoption.py` keeps runtime API wrapper types composed from generated schemas.
- `scripts/check_seed_targets.py` keeps committed target keys and repository-state shapes consistent with authored variants.
- `scripts/check_generated_targets_current.py` replays authored solutions through the real simulator and verifies generated targets are current.
- `scripts/check_documentation_current.py` keeps root documentation current and limits `/docs` to scoped goal artifacts.
- `scripts/check_ci_quality_gates.py` proves the CI workflow and package scripts still run the required guards.
- `scripts/check_quality_gates.py` runs the fast repository guards from one local command.
- `scripts/check_django_deploy.py` runs Django deployment checks with production-like required settings.

Ruff lint and format checks are both blocking in CI. Formatting covers maintained
backend runtime/tests and repository scripts. Historical Django migrations and
curriculum data ledgers are excluded from formatting to preserve immutable schema
history and reviewable authored content; they remain covered by lint and their
dedicated migration, structural, seed, and replay guards.


Repository artifact guard: `python scripts/check_repository_artifacts.py`.


## Source packaging

Use `python scripts/clean_repository_artifacts.py` before packaging and `python scripts/package_source_zip.py <output.zip>` when sharing the project. The packager excludes cache/build artifacts such as `__pycache__`, `.pytest_cache`, `node_modules`, and `dist`.

## Committed Migration Policy

Django migrations are versioned schema history. Every model change must include its generated migration so a clean checkout can reproduce the schema without inventing environment-specific history.

Rules:

- Keep `migrations/__init__.py` so Django still recognizes each migration package.
- Generate migrations during development and commit them with the model change.
- Run `python manage.py makemigrations --check --dry-run` in CI to detect drift.
- Apply the committed migrations with `python manage.py migrate --noinput`; deployments must never generate new migrations.

## Curriculum Selector Decomposition

`backend/curriculum/selectors/__init__.py` is the compatibility export surface.
It imports implementation directly from named read-model modules, without a
second `core.py` export layer:

- `stories.py` for story/chapter locks and completion checks.
- `progress_counts.py` for chapter completion numerator/denominator maps.
- `content.py` for chapter content page/overview payload assembly.

Chapter completion reward policy and orchestration live in
`backend/curriculum/services/chests.py`; the progress wallet remains the durable
currency-ledger owner.
`GET /api/chapters/{id}/chests/` reports eligibility from persisted completion
and collection from credited wallet keys. `POST` to the same endpoint opens an
earned milestone by threshold and recovers an unpaid reward through the same
idempotent wallet key used by automatic completion payouts. The map displays
closed, available, and opened chest assets from this server state.
- `command_skills.py` for command-skill query and learned-spellbook rows.
- `book.py` for Chapter Book payloads.
- `challenge_queries.py` for challenge query shape.
- `adventure_access.py`, `challenge_access.py`, and `access_helpers.py` for user-specific access state.

New selectors should go into the narrow module that owns their query/payload responsibility, not back into `core.py`.
