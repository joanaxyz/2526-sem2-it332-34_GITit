# Domain-Model Refactor Plan: Storey / CommandAdventure / Challenge

> Status: **Increment 1 implemented and green** (backend 205 tests, frontend 102 tests). See "Implementation status" below.
> Decisions locked: **(1) Destructive DB reset** (dev data may be wiped — schema is all `0001_initial`). **(2) Mapping correction accepted** — `CommandDrill → AdventureProblem`, `CommandAdventure` is a **new** container.

---

## Implementation status (as of 2026-06-07)

### Done — domain vocabulary normalized, tree fully working

Backend (renamed in place within existing app packages `learning`/`scenarios` to keep the tree green; physical app split deferred):
- `LearningModule → Storey`, `FoundationTopic → ConceptPage` (`learning/models.py`).
- `CommandTopic → CommandSkill`, `CommandUsage → CommandForm`, `CommandDrill → AdventureProblem`, `WorkflowScenario → Challenge`, `WorkflowScenarioLevel → ChallengeLevel`, `StepLog → CommandStep`, `PracticeSession → PracticeRun`, `CompletionRecord → ProblemCompletion`.
- **`CommandAdventure` is now a real model** (one per Storey, `OneToOne`), seeded from the curriculum, replacing the synthetic `command_drill_adventure_for` dict.
- **`ProblemVariant` removed** → abstract `VariantBase` + concrete `AdventureVariant` (FK `adventure_problem`) and `ChallengeVariant` (FK `challenge_level`, +`command_budget`). The XOR `clean()` hack is gone.
- `PracticeRun` now carries typed `adventure_variant`/`challenge_variant` FKs with `variant`/`variant_id` convenience properties.
- `PracticeKind` values: `command_adventure` / `challenge`.
- Services, selectors, serializers, views, builders, seed command, admin, and tests updated.
- Migrations reset (fresh `0001_initial` for `learning`/`scenarios`/`progress`); `seed_curriculum_v2 --validate` passes on a clean DB (3 CommandAdventures, 5 AdventureProblems/Variants, 4 Challenges, 12 ChallengeLevels/Variants).

API (Phase 6):
- Clean top-level routes added: `GET /api/storeys/`, `/api/storeys/{id}/content/`, `/api/concept-pages/`, `/api/command-forms/{id}/preview/`, `/api/runs/` (+`/{id}/`, `/submit-command/`, `/files/`, `/abandon/`, `/finish/`, `/retry/`). Old `/api/learning/` and `/api/scenarios/` mounts kept as compatibility aliases.

Frontend (Phase 8 — contract sync):
- `practice_kind`/`problem_type` values → `command_adventure`/`challenge` (types, api, components, dashboard, tests).
- API client paths repointed to the clean routes (`/storeys/`, `/runs/...`, `/command-forms/...`, `/concept-pages/`).
- `tsc -b` clean; 102 vitest tests pass.

### Increment 2 — CommandAdventure mastery system (implemented, green)

Net-new behavior from the brief, now built backend-first (216 backend tests pass):
- **`AdventureRun` + `AdventureProblemAttempt` models** — a straight session over the adventure's ordered problems; each attempt locks its `selected_variant` and owns its `CommandStep`s (CommandStep gained a nullable `attempt` FK; `session` is now nullable).
- **`AdventureScoringService`** (`scenarios/scoring.py`) — pure, unit-tested: correctness 60 / efficiency 25 / independence 15; bands `failed`/`passed`/`strong_pass`/`mastered` at 70/85/95; per-attempt mastery gain (bare pass → partial, 95%+ → near-full); a run fails if a required problem is left unsolved.
- **`AdventureRunService` + `AdventureCommandService`** (`scenarios/adventure_runs.py`) — kept entirely separate from the challenge flow; the command service reuses only the shared simulator + evaluator engines, advances attempts, and hands off to scoring on solve/budget-exhaustion.
- **Routes** (the brief's adventure surface): `POST /api/command-adventures/{slug}/runs/`, `GET /api/adventure-runs/{id}/`, `POST .../submit-command/`, `POST .../use-hint/`, `POST .../finish/`.
- **Hints**: `use-hint` increments the attempt's `hint_count` (feeding the independence score). Persisted `HintSet` content is still TODO (see below).
- `AdventureProblem` gained `ideal_counted_commands` (drives efficiency) and `is_required` (drives run pass/fail).
- Tests: `scenarios/tests/test_adventure_runs.py` covers the scoring engine, run orchestration, and the full HTTP loop (start → submit authored solution → solved & scored, no-answer-leak guard, hint increment).

### Increment 3 — Adventure run frontend (implemented, green)

New `features/command-adventures/` (frontend 106 tests pass, tsc clean):
- `types.ts`, `api/commandAdventuresApi.ts` (start/get/submit/hint/finish on the clean routes), `hooks/useAdventureRun.ts` (react-query), `components/AdventureSession.tsx` + `components/AdventureResult.tsx`, `pages/CommandAdventurePage.tsx`.
- Route `/command-adventures/:adventureSlug` (under PracticeLayout) starts a run and renders the session: in-session progress bar, objective/task, terminal, command input (reuses the shared `CommandInput`), hint button, and a mastery result screen with per-problem bands.
- `queryKeys.adventureRun` added.
- Tests: `AdventureResult.test.tsx` (mastery %, bands) and `commandAdventuresApi.test.ts` (route contract).

The CommandAdventure mastery vertical (backend + frontend) is now playable end-to-end.

### Increment 4 — HintSet + ScaffoldPolicy on variants (implemented, green)

- `VariantBase` gained `hint_set` (ordered, non-answer-revealing) and `scaffold_policy`; both `AdventureVariant`/`ChallengeVariant` inherit them (migration `0003`). Builder + seed pass `hint_set_template`/`scaffold_policy_template` through (defaults empty).
- `use-hint` serves the **next authored hint** (non-revealing generic fallback when none authored / exhausted) and returns `{run, hint, hint_number}`; still increments `hint_count` (independence score).
- Attempt serializer exposes `available_hints` and reads `scaffold_policy` for `live_dag`/`contextual_feedback`, but **forces `expected_state` off** so adventure mode never leaks the answer. Frontend shows the revealed hint inline.
- Tests: backend authored-hint ordering + HTTP hint payload (**217 backend**); frontend hint UI (**106 frontend**, tsc clean).

### Still deferred

1. Moving `min/max/ideal_counted_commands` onto the variant (still on the problem/level).
2. **Challenge run rename** — the challenge side still uses the unified `PracticeRun`; a dedicated `ChallengeRun` (+`/api/challenge-runs/`) mirroring the adventure split.
4. **Physical app split** into `curriculum`/`adventures`/`challenges`/`practice` packages, and **frontend folder/component renames** (`features/modules`→`features/storeys`, `features/scenarios`→`features/challenges`, `TowerPage`→`StoreyMapPage`, etc.). Domain *names* (models, API, kind values, types) now match the product; the Python package names (`learning`, `scenarios`) and FE folder names are the remaining cosmetic layer.
5. Internal generic attribute names kept to limit blast radius (`PracticeRun.module`/`command_drill`/`workflow_level`, `CommandForm.usage_form`, related_names like `usages`/`drills`/`step_logs`). Not part of the API/UI contract.
6. `min/max_counted_commands` still live on `AdventureProblem`/`ChallengeLevel` (the move onto the variant + `ideal_counted_commands` is bundled with the scoring work).
7. Backend payload `item_type`/section strings (`command_drill_adventure`, `workflow_scenario`, `command_topics`) intentionally left unchanged so FE and BE stay in sync; rename them as a matched pair in a later pass.

---

## 0. Reality check — what the code actually is

The original brief assumed a structure that does not match the repo. Key facts established by inspection:

**Apps present:** `accounts`, `common`, `config`, `evaluation`, `learning`, `progress`, `retries`, `review`, `scaffolding`, `scenarios`, `simulator`.

**The whole domain lives in one app — `backend/scenarios/models.py`** — covering both command-learning and scenario domains plus the session engine. Current model graph:

```
LearningModule (learning app)
 ├─ CommandTopic ── CommandUsage ── CommandDrill ── ProblemVariant(command_drill=…)
 └─ WorkflowScenario ── WorkflowScenarioLevel ── ProblemVariant(workflow_level=…)

PracticeSession (ONE problem + ONE variant; discriminated by practice_kind)
 └─ StepLog ── CommandLog (1:1)
CompletionRecord (per problem, per user)
```

### Three structural mismatches (not cosmetic)

**A. `CommandAdventure` does not exist — it is synthesized at request time.**
`backend/learning/curriculum_v2/adventures.py` is a hardcoded dict keyed by `module.slug`; `command_drill_adventure_summary_payload` in `backend/scenarios/selectors.py` fabricates an "adventure" per module, treating each `CommandTopic` as a "level". The container the brief calls `CommandAdventure` is virtual.

**B. The brief's `CommandDrill → CommandAdventure` is wrong by the brief's own definitions (CORRECTED).**
`CommandDrill` is the leaf objective (e.g. "Stage a specific file") = the brief's `AdventureProblem`. `ProblemVariant` is its concrete case = `AdventureVariant`. `CommandAdventure` is the container = **new model**. `CommandTopic` = `CommandSkill`, `CommandUsage` = `CommandForm`, which become **taxonomy tags on `AdventureProblem`**, not structural parents.

**C. There is no Run → Attempt → Step hierarchy — just a flat `PracticeSession`.**
A `PracticeSession` = one user + one problem + one selected variant + its `StepLog`s. It maps to a single `AdventureProblemAttempt` (adventure) or a single `ChallengeRun` (challenge). The brief's `AdventureRun` (one straight session across ordered problems) and the adventure mastery scoring (correctness 60 / efficiency 25 / independence 15; bands 70/85/95) **do not exist and are net-new.** Current progress is binary `required_successful_attempts` gated by a command-accuracy threshold.

### Other shaping facts
- **`module → storey` rename is already half-done** (`StoreyListAPIView`, `published_storeys()`, `queryKeys.storeys`, `storeysApi`, `LearningModule.__str__` returns "Storey …", `/api/learning/storeys/` live with `/modules/` alias). "Tower" used only as UI metaphor — consistent with the brief.
- **`min/max_counted_commands` live on the parent** (`CommandDrill`, `WorkflowScenarioLevel`), not the variant. Brief wants them on the variant → a field *move*. `ideal_counted_commands` is new.
- **No hint system exists.** `HintSet` and `use-hint` routes are net-new. `ScaffoldPolicy` is only a computed dict in `scaffolding/services.py` keyed off difficulty, never persisted.
- Today drills reveal `expected_state`/`target_state`, contradicting the target "no expected-state reveal" for adventures.
- Schema is **young** (`scenarios`/`learning`/`progress` each only `0001_initial`) → destructive reset is realistic and chosen.
- `retries` app is **vestigial** (re-exports `VariantSelectionService`).

---

## 1. Answers to the 20 audit questions

1. **Wrong domain names:** `scenarios` (carries entire domain incl. command-learning), `learning` (`LearningModule`), `retries` (vestigial).
2. **Survive renamed:** `LearningModule→Storey`, `CommandTopic→CommandSkill`, `CommandUsage→CommandForm`, `CommandDrill→AdventureProblem`, `WorkflowScenario→Challenge`, `WorkflowScenarioLevel→ChallengeLevel`, `StepLog→CommandStep`, `FoundationTopic→ConceptPage`, `CompletionRecord→{Adventure,Challenge}Progress`, `StreakRecord`/`StudentProgress` unchanged.
3. **Split:** `ProblemVariant`→`AdventureVariant`+`ChallengeVariant`; `PracticeSession`→`AdventureProblemAttempt`+`ChallengeRun` (+ new `AdventureRun`); `CommandLog` folds into `CommandStep`.
4. **Delete:** generic `ProblemVariant`, `PracticeKind`, synthetic `command_drill_adventure_for`, `retries` app, module/scenario URL aliases (after migration).
5. **ProblemVariant → AdventureVariant:** `slug`, `label`, `initial_state`(→RepositoryState), `evaluation_spec`(→EvaluationSpec), `target_state`, `solution_commands`(internal), `semantic_key`/`structure_signature`(→`variant_signature`), `student_context`(→narrative/task), `is_published`; **+ moved** `min/max/ideal_counted_commands`; **+ new** `hint_set`, `scaffold_policy`, `visual_state_mode`. **Excludes** `expected_state_diagram`.
6. **ProblemVariant → ChallengeVariant:** all of the above **plus** `expected_state_diagram`/`expected_state_snapshot`, `command_budget`. Keeps expected-state reveal.
7. **Remove generic `ProblemVariant`?** Yes — only coupled via `problem.variants`, `PracticeSession.variant`, `StaticProblemVariantBuilder`, seed `_sync_variants`. Splitting removes the `clean()` XOR hack.
8. **Shared abstract base?** Yes — Django **abstract** `VariantBase` (no shared table) for common fields; concrete `AdventureVariant`/`ChallengeVariant` tables.
9. **Separate runs or shared `PracticeRun`?** **Separate.** Brief forbids shared progression. Share only `CommandStep` + simulator + evaluator.
10. **Prevent wrong shared scoring:** scoring in per-domain services (`AdventureScoringService`, `ChallengeCompletionService`); shared layer is strictly mechanical (parse/execute/classify/snapshot) and delegates completion via a strategy.
11. **ChallengeRun → level+variant or variant only?** **Both** `ChallengeLevel` + selected `ChallengeVariant` (mirrors current `PracticeSession`; locks variant for review, keeps cheap level/unlock queries).
12. **AdventureRun stores variants, or attempts?** **Per `AdventureProblemAttempt`** (`selected_variant`); `AdventureRun` stores only ordered cursor + aggregate score.
13. **Retry variant selection:** reuse existing `VariantSelectionService` (identity via `semantic_key`/`case_id`, prefer untried, exclude prior). Objective invariant because variants share one problem/level parent.
14. **APIs to rename:** all `/api/scenarios/*` → `/api/command-adventures/*`, `/api/adventure-runs/*`, `/api/challenges/*`, `/api/challenge-runs/*`; `/api/learning/modules/`→`/api/storeys/`. See §7.
15. **Frontend moves:** `features/modules→features/storeys`, `features/scenarios→features/challenges` (+ new `features/command-adventures`), split `features/practice`; rename query keys/types. See §6.
16. **Seed files:** `seed_curriculum_v2.py` + all `backend/learning/curriculum_v2/*` + `backend/scenarios/builders.py`.
17. **Migrations:** new per-app `0001_initial` for `curriculum`, `adventures`, `challenges`, `practice`, `progress` (destructive reset — see §8).
18. **Tests:** rename/rewrite `scenarios/tests/test_curriculum_v2.py`, `learning/tests/test_learning_api_v2.py`, evaluation/completion tests; add adventure-run/scoring tests; FE `*.test.tsx`.
19. **Acceptable temporary aliases:** URL aliases + FE export aliases (pattern already in use). Keep through Phase 8, delete Phase 9.
20. **Delete completely:** `practice_kind`, `ProblemVariant`, `command_drill`/`workflow` vocabulary, module/scenario/drill URL aliases, `retries` app, synthetic adventure dict.

---

## 2. Deliverable 1 — Target domain model

```
curriculum app
  Storey (was LearningModule)
    ├─ has one CommandAdventure              (NEW container; was synthetic)
    ├─ has many Challenges
    └─ has many ConceptPages                 (optional; from FoundationTopic / Lesson)
  CommandSkill (was CommandTopic)            taxonomy
  CommandForm  (was CommandUsage)            taxonomy, FK CommandSkill

adventures app
  CommandAdventure  (FK Storey)
    └─ has many AdventureProblems            (was CommandDrill; ordered)
         ├─ FK CommandSkill, FK CommandForm  (taxonomy tags, not parents)
         └─ has many AdventureVariants       (was ProblemVariant[command_drill])
  AdventureRun  (FK user, FK CommandAdventure)        (NEW: straight session)
    └─ has many AdventureProblemAttempts
         ├─ references one AdventureProblem
         ├─ references one selected AdventureVariant
         └─ has many CommandSteps            (was StepLog+CommandLog)

challenges app
  Challenge  (FK Storey)                     (was WorkflowScenario)
    └─ has many ChallengeLevels              (was WorkflowScenarioLevel)
         └─ has many ChallengeVariants       (was ProblemVariant[workflow_level])
  ChallengeRun  (FK user, FK ChallengeLevel, FK selected ChallengeVariant)
    └─ has many CommandSteps                 (ChallengeRun == one attempt; no ChallengeAttempt)

progress app
  StoreyProgress, AdventureMasteryProgress, ChallengeProgress   (was CompletionRecord)
  StreakRecord, StudentProgress  (unchanged)

shared engines (unchanged homes)
  simulator   → RepositoryState
  evaluation  → EvaluationSpec / EvaluationEngine
  scaffolding → HintSet, ScaffoldPolicy (now persisted on variants)
```

---

## 3. Deliverable 2 — Current → target mapping table

| Current (real code) | Target | Notes |
|---|---|---|
| `LearningModule` | `Storey` | rename already started |
| `FoundationTopic` | `ConceptPage` | only if kept as teaching content |
| `CommandTopic` | `CommandSkill` | becomes taxonomy tag, not parent |
| `CommandUsage` | `CommandForm` | taxonomy, FK to CommandSkill |
| *(synthetic `command_drill_adventure_for`)* | `CommandAdventure` | **new model**, one per Storey |
| `CommandDrill` | `AdventureProblem` | **corrected** (brief said →CommandAdventure) |
| `ProblemVariant(command_drill=…)` | `AdventureVariant` | concrete case |
| `WorkflowScenario` | `Challenge` | |
| `WorkflowScenarioLevel` | `ChallengeLevel` | |
| `ProblemVariant(workflow_level=…)` | `ChallengeVariant` | concrete case |
| generic `ProblemVariant` (+`clean()` XOR) | **removed** | split into the two above |
| *(none)* | `AdventureRun` | **new** straight-session container |
| `PracticeSession(command_drill)` | `AdventureProblemAttempt` | one problem+variant attempt |
| `PracticeSession(workflow_level)` | `ChallengeRun` | one level+variant attempt |
| `StepLog` + `CommandLog` | `CommandStep` | merge 1:1 pair |
| `CompletionRecord(command_drill)` | `AdventureMasteryProgress` | scoring becomes weighted |
| `CompletionRecord(workflow_level)` | `ChallengeProgress` | |
| `PracticeKind.command_drill` | `command_adventure` → drop discriminator | |
| `PracticeKind.workflow_scenario` | `challenge` → drop discriminator | |
| `retries` app | **deleted** | folded into selection services |
| `min/max_counted_commands` on problem | moved onto variant | +`ideal_counted_commands` (new) |
| *(none)* | `HintSet`, `ScaffoldPolicy` persisted | new fields on variants |

---

## 4. Deliverable 3 — Final backend apps & model ownership

| App | Owns | From |
|---|---|---|
| `curriculum` | `Storey`, `ConceptPage`, `CommandSkill`, `CommandForm`, seeds | merges `learning` + taxonomy out of `scenarios` |
| `adventures` | `CommandAdventure`, `AdventureProblem`, `AdventureVariant`, `AdventureRun`, `AdventureProblemAttempt`, scoring/selectors/serializers/views | from `scenarios` (command side) |
| `challenges` | `Challenge`, `ChallengeLevel`, `ChallengeVariant`, `ChallengeRun`, selectors/serializers/views | from `scenarios` (workflow side) |
| `practice` | shared `CommandStep`, `CommandProcessingService` orchestration (delegates completion/scoring) | from `scenarios.services` |
| `simulator` | `RepositoryState` engine | unchanged |
| `evaluation` | `EvaluationSpec`, `EvaluationEngine`, completion evaluator | unchanged, neutral rename |
| `scaffolding` | `HintSet`, `ScaffoldPolicy` helpers | unchanged + persistence |
| `progress` | `StoreyProgress`, `AdventureMasteryProgress`, `ChallengeProgress`, `StreakRecord` | from `CompletionRecord` + `progress` |
| `review` | review-mode entry (thin) | unchanged, drop `CommandDrill` import |
| ~~`retries`~~ | deleted | — |

Because the DB is being reset, the cross-app model "move" is simply authoring the models in their new app + fresh `0001_initial` — no `SeparateDatabaseAndState` gymnastics required. Keep `scenarios` as a temporary re-export shim only to ease import churn during Phases 3–8, then delete in Phase 9.

---

## 5. Deliverable 4 — Final frontend feature folders

| Folder | Owns | From |
|---|---|---|
| `features/storeys` | StoreyMapPage (was TowerPage), StoreyCard, storey progress, `storeysApi`, `Storey` types | `features/modules` |
| `features/command-adventures` | AdventureSession, progress bar, objective list, result screen, hint panel, adventure command input, variant-aware review, `commandAdventureApi` | new + carve from `features/practice` |
| `features/challenges` | ChallengeList, ChallengeLevelPicker, ChallengeWorkspace (was ScenarioWorkspace), LiveDagPanel, ContextualFeedbackPanel, expected-state, result/review/retry, `challengeApi` | `features/scenarios` + scenario parts of `features/practice` |
| `features/practice` | **only** shared TerminalPanel, CommandInput, state-view, project structure | keep shared bits |
| `features/progress` | shared progress widgets | unchanged |
| `features/review` | shared review banner; routes into adventure/challenge review | unchanged |
| `shared/api/queryKeys.ts` | `storey`, `commandAdventure`, `adventureProblem`, `adventureVariant`, `challenge`, `challengeLevel`, `challengeVariant` keys | rewrite |

Today `features/practice` is shared by both modes (`usePracticeSession`, `PracticeWorkspace`, scaffolding store). The split must separate *business logic* (scoring, completion, variant rotation) from *presentational* terminal/state components.

---

## 6. Deliverable 5 — File-by-file backend plan

**curriculum app (absorbs `learning`)**
- `learning/models.py`: `LearningModule→Storey`; `FoundationTopic→ConceptPage`. Move `CommandTopic→CommandSkill`, `CommandUsage→CommandForm` here.
- `learning/{selectors,serializers,views,urls}.py`: keep storey functions; drop `published_modules`/`ModuleListAPIView` aliases in Phase 9.
- `curriculum_v2/`: `modules.py→storeys.py`, `command_topics.py→command_skills.py`, `drills.py→adventure_problems.py`, `workflows.py→challenges.py`, delete `adventures.py` (replace with real `COMMAND_ADVENTURES` seed data).

**adventures app**
- `models.py`: `CommandAdventure`, `AdventureProblem` (from `CommandDrill`; `module`→`storey`), `AdventureVariant` (command branch of `ProblemVariant`), `AdventureRun`, `AdventureProblemAttempt`.
- `services.py`: carve `VariantSelectionService` + new `AdventureScoringService` (correctness/efficiency/independence, bands) + `AdventureRunService` (ordered cursor) from `scenarios/services.py`.
- `selectors/serializers/views/urls.py`: command-drill halves (`command_*` functions, `_problem_payload` drill branch).

**challenges app**
- `models.py`: `Challenge`, `ChallengeLevel` (unlock logic), `ChallengeVariant`, `ChallengeRun`.
- `services.py`: workflow halves — `_ensure_workflow_unlocked`, completion, `next_difficulty`.
- selectors/serializers/views/urls: workflow halves.

**practice app**
- `models.py`: `CommandStep` (merge `StepLog`+`CommandLog`).
- `services.py`: refactor `CommandProcessingService` to be domain-agnostic; completion/scoring via strategy from adventures/challenges.

**Shared/unchanged with edits**
- `scenarios/builders.py`: split `StaticProblemVariantBuilder` → adventure/challenge builders.
- `scenarios/{visualization,context,command_content}.py`: move to `practice`/shared.
- `evaluation/completion.py`: `PracticeCompletionEvaluator`→neutral; `CompletionEvaluationContext.session`→generic.
- `progress/{models,services}.py`: add `StoreyProgress`/`AdventureMasteryProgress`/`ChallengeProgress`; rewire `MetricsService` off `PracticeSession`.
- `scaffolding/services.py`: read `ScaffoldPolicy`/`HintSet` from variants instead of difficulty hardcode.
- `review/services.py`: drop `CommandDrill` import; route to run services.
- **Delete** `backend/retries/`.
- `config/urls.py`: add new includes; keep old aliases until Phase 9.
- `config/settings.py`: update `INSTALLED_APPS`.

---

## 7. Deliverable 6 — File-by-file frontend plan

- `app/router.tsx`: `TowerPage→StoreyMapPage`; split `/practice/:sessionId` into `/adventure-runs/:runId` and `/challenge-runs/:runId` (old paths as redirects in Phase 8).
- `features/modules/ → features/storeys/`: `ModulesPage.tsx`(TowerPage)→`StoreyMapPage.tsx`; `ModulePracticeHub→StoreyPracticeHub`; `moduleColors.ts→storeyColors.ts`; `modulesApi.ts` drop `modulesApi`/`listModules` aliases.
- `features/scenarios/ → features/challenges/`: `scenariosApi.ts` split into `challengeApi` + `commandAdventureApi`; `types.ts` split `CommandDrill*→Adventure*`, `Workflow*→Challenge*`, drop `PracticeKind`. `DifficultySelector`, `CommandBudgetHeader` → challenges.
- New `features/command-adventures/`: AdventureSession page, progress bar, objective list, result screen, hint panel; consume `AdventureRun` payloads.
- `features/practice/`: keep `TerminalPanel`, `CommandInput`, `ProjectStructurePanel`, `WorkspaceEditorOverlay`, `LiveDagPanel` as shared; move `usePracticeSession`/`useCommandSubmission`/`practiceApi`/scoring (`commandAccuracy.ts`, `scaffolding/*`) into the two feature folders.
- `shared/api/queryKeys.ts`: replace `modules`/`moduleContent`/`towers` with storey/commandAdventure/adventureProblem/adventureVariant/challenge/challengeLevel/challengeVariant keys.
- `features/dashboard/...`: `ModulePerformanceCard.tsx` + `dashboardApi.ts`/`types.ts`: `module_kpis→storey_kpis` (backend already emits both; drop alias in Phase 9).
- `styles/globals.css`: rename `.module-*`/`.scenario-*`/`.drill-*` classes.

Scope: ~18 FE files reference `module`, ~20 `scenario`, ~9 `drill`.

---

## 8. Deliverable 7 — API route migration

| Old | New |
|---|---|
| `/api/learning/storeys/` (exists), `/api/learning/modules/` (alias) | `/api/storeys/` |
| `/api/scenarios/storeys/{id}/content/?section=command_adventures` | `/api/storeys/{slug}/command-adventure/` |
| `…?section=workflow_scenarios` | `/api/storeys/{slug}/challenges/` |
| `…?section=command_topics` | `/api/command-adventures/{slug}/problems/` |
| `/api/scenarios/command-usages/{id}/preview/` | `/api/command-forms/{slug}/preview/` |
| `POST /api/scenarios/sessions/` (command_drill) | `POST /api/command-adventures/{slug}/runs/` |
| `POST /api/scenarios/sessions/` (workflow_scenario) | `POST /api/challenge-levels/{slug}/runs/` |
| `GET /api/scenarios/sessions/{id}/` | `/api/adventure-runs/{id}/` or `/api/challenge-runs/{id}/` |
| `POST …/{id}/commands/` | `…/submit-command/` |
| *(none)* | `…/use-hint/` **(new)** |
| `POST …/{id}/abandon/` + completion-on-max | `…/finish/` |
| `POST …/{id}/retry/` | `POST …/runs/` with `prior_run_id` |
| `…/{id}/files/` | `…/{id}/files/` (shared, per run namespace) |
| review via `/api/review/` | `…/{id}/review/` per run |

Keep `/api/scenarios/*` + `/api/learning/modules/` as thin alias routers through Phase 8.

---

## 9. Deliverable 8 — DB migration strategy

**Chosen: Option A — Destructive reset.** Schema is all `0001_initial`; data is seedable; dev data is disposable.

Steps:
1. Drop the dev DB / delete all app migration files.
2. Author fresh `0001_initial` per new app (`curriculum`, `adventures`, `challenges`, `practice`, `progress`).
3. `migrate`.
4. `python manage.py seed_curriculum --validate` to repopulate.

No `ProblemVariant` XOR baggage, no relabel migrations.

**Option B — Preservation (recorded, not chosen):** `SeparateDatabaseAndState` app-relabels + `RenameModel` steps + backfills (`ProblemVariant`→two tables from non-null FK; group drill `PracticeSession`s into `AdventureRun`+`AdventureProblemAttempt`; workflow sessions→`ChallengeRun` 1:1; merge `CommandLog`→`CommandStep`). Use only if data must survive.

---

## 10. Deliverable 9 — Seed data migration

- Rewrite `curriculum_v2/`: add explicit **`COMMAND_ADVENTURES`** list (one per storey, ordering its `AdventureProblem`s) replacing the synthetic dict. `drills.py→adventure_problems.py`; each problem gains `command_skill`/`command_form` refs + `ideal_counted_commands`. Move `min/max/ideal_counted_commands` and `hint_set`/`scaffold_policy` onto **variant** specs.
- `seed_curriculum_v2.py`: `_seed_modules→_seed_storeys`; add `_seed_command_adventures`; `_seed_command_drills→_seed_adventure_problems`; split `_sync_variants` into adventure/challenge builders; update `_validate_*` (drop `practice_kind` label in `_validate_variant`).
- `builders.py`: `StaticProblemVariantBuilder` → `AdventureVariantBuilder` + `ChallengeVariantBuilder`.
- Rename command `seed_curriculum_v2→seed_curriculum` (alias old name one release).

---

## 11. Deliverable 10 — Test plan

- **Rename/rewrite:** `scenarios/tests/test_curriculum_v2.py` → `adventures/tests/` + `challenges/tests/`; `learning/tests/test_learning_api_v2.py` → `curriculum/tests/`; `evaluation/tests/test_engine_v2.py` keep, neutral rename.
- **New tests:** `AdventureRun` lifecycle (ordered cursor, per-attempt variant lock, retry rotation); `AdventureScoringService` bands (72%→partial mastery, 95%→full, fail-if-required-unsolved, efficiency/independence weighting); `ChallengeRun` variant locking + review fidelity; `ChallengeLevel` unlock gating; `CommandStep` merge.
- **Simulator/evaluation tests:** unchanged — regression anchor.
- **Frontend:** `ModulePracticeHub.test.tsx→StoreyPracticeHub.test.tsx`; new AdventureSession progress-bar/objective tests; keep `LiveDagPanel`/`ProjectStructurePanel`/scaffolding tests shared.
- **CI gate:** run `seed_curriculum --validate` after each phase.

---

## 12. Deliverable 11 — Risk list

1. **Behavioral, not cosmetic:** `AdventureRun` + mastery scoring + hints are net-new — the biggest effort hides behind a "rename."
2. **Shared session engine** (`scenarios/services.py`, ~600 lines) couples both modes; splitting without regressing completion/streak/RTA metrics is the highest risk.
3. **Adventure scaffold leak:** drills currently reveal `expected_state`/`target_state`; the new policy forbids it — verify no leak after split.
4. **Half-finished module→storey rename** means two naming layers coexist; risk of creating a third name on top of an alias.
5. **Dashboard metrics** (`progress/services.py`) query `PracticeSession`/`module__number` heavily — rewire atomically with the run split or KPIs break.
6. **`required_successful_attempts` semantics differ** from the mastery model — don't drop completion gating before scoring replaces it.
7. **Frontend `usePracticeSession`** is shared; an incomplete split risks adventure UI rendering challenge scaffolds.
8. **Destructive reset** wipes any local data — acceptable per decision, but ensure no shared/staging DB is hit.

---

## 13. Deliverable 12 — Implementation phases

- **Phase 0 — Done:** reset chosen; `CommandDrill→AdventureProblem` correction accepted.
- **Phase 1 — Naming audit & compatibility map** (this doc) + freeze alias list.
- **Phase 2 — Finish `module→storey`** first (half-done) → stand up `curriculum` app (`Storey`, `CommandSkill`, `CommandForm`, `ConceptPage`).
- **Phase 3 — Backend app/model split** (`adventures`, `challenges`, `practice`), `scenarios` shim retained.
- **Phase 4 — Replace `ProblemVariant`** with `AdventureVariant`/`ChallengeVariant` (move counted-command fields, add HintSet/ScaffoldPolicy).
- **Phase 5 — Session/run split** (`AdventureRun`+`AdventureProblemAttempt`, `ChallengeRun`, `CommandStep`); rewire `progress`/metrics.
- **Phase 6 — API route split** (new routers + aliases).
- **Phase 7 — Adventure scoring/progress** (correctness/efficiency/independence, bands, mastery weighting, hints + `use-hint`).
- **Phase 8 — Frontend feature split** (`storeys`, `command-adventures`, `challenges`; shared `practice`; query keys/types/routes).
- **Phase 9 — Challenge workspace cleanup** (live DAG/contextual/expected-state under `challenges`).
- **Phase 10 — Delete legacy** (`scenarios` shim, `retries`, aliases, `PracticeKind`, synthetic adventure) + test/seed cleanup.
