---
name: domain-refactor
description: Plan + key findings for the Storey/CommandAdventure/Challenge domain-model refactor
metadata:
  type: project
---

Major domain-model refactor planned (audit in `docs/refactor-plan.md`, written 2026-06-07). Old language (module/lesson/drill/workflow scenario/ProblemVariant/PracticeSession) → new (Storey/CommandAdventure/AdventureProblem/AdventureVariant/Challenge/ChallengeLevel/ChallengeVariant/runs). Not yet implemented.

Non-obvious findings from inspecting the real code:
- The whole domain lives in `backend/scenarios/models.py` (both command-learning and scenario sides + the session engine), NOT spread across apps.
- **CommandAdventure does not exist as a model** — it is synthesized per-module at request time via `learning/curriculum_v2/adventures.py` (hardcoded dict) + `command_drill_adventure_summary_payload` in `scenarios/selectors.py`.
- Corrected mapping (user accepted): `CommandDrill → AdventureProblem` (leaf objective), and `CommandAdventure` is a NEW container. CommandTopic→CommandSkill, CommandUsage→CommandForm become taxonomy tags, not parents.
- There is NO Run→Attempt→Step hierarchy: one flat `PracticeSession` (one problem+variant) → `StepLog`+`CommandLog`. `AdventureRun` (multi-problem straight session) and adventure mastery scoring (correctness/efficiency/independence, bands 70/85/95) are net-new.
- `module→storey` rename is already half-done on branch `refactor/auth` (Storey* views/aliases coexist with module ones). "Tower" is the UI metaphor only.
- Decisions locked: destructive DB reset (schema is all `0001_initial`); deliver as docs file.

Increment 1 IMPLEMENTED + green (2026-06-07): models renamed in place (Storey/ConceptPage/CommandSkill/CommandForm/AdventureProblem/Challenge/ChallengeLevel/CommandStep/PracticeRun/ProblemCompletion); real `CommandAdventure` model added; `ProblemVariant` split into `AdventureVariant`+`ChallengeVariant` via abstract `VariantBase`; `PracticeKind` values now command_adventure/challenge; clean `/api/runs/`, `/api/storeys/` routes added (old mounts kept as aliases); frontend contract synced. Backend 205 tests + frontend 102 tests pass; migrations reset; `seed_curriculum_v2 --validate` green on clean sqlite.

IMPORTANT: dev `.env` `DATABASE_URL` points at a REMOTE Supabase Postgres. The destructive migration reset was applied only to local sqlite + test DB; Supabase still has the OLD schema and its migration table records `0001_initial` as applied, so `migrate` is a no-op there. Migrating/resetting Supabase needs explicit user confirmation.

Increment 2 IMPLEMENTED + green (216 backend tests): CommandAdventure mastery system. New: `scenarios/scoring.py` (AdventureScoringService: correctness 60/efficiency 25/independence 15, bands 70/85/95, mastery gain), models AdventureRun + AdventureProblemAttempt (CommandStep got nullable `attempt` FK, session now nullable), `scenarios/adventure_runs.py` (AdventureRunService + AdventureCommandService, separate from challenge flow, reuse only simulator+evaluator), adventure_serializers.py + adventure_views.py, routes /api/command-adventures/{slug}/runs/ + /api/adventure-runs/{id}/{submit-command,use-hint,finish}/. AdventureProblem gained ideal_counted_commands + is_required. Tests: scenarios/tests/test_adventure_runs.py (scoring + orchestration + full HTTP loop). User said DON'T COMMIT YET.

Increment 3 IMPLEMENTED + green (frontend 106 tests, tsc clean): `features/command-adventures/` (types, api/commandAdventuresApi, hooks/useAdventureRun, components/AdventureSession + AdventureResult, pages/CommandAdventurePage); route `/command-adventures/:adventureSlug` under PracticeLayout; queryKeys.adventureRun. Adventure mastery now playable end-to-end (BE+FE). Tests: AdventureResult.test.tsx + commandAdventuresApi.test.ts.

Increment 4 IMPLEMENTED + green (BE 217, FE 106): HintSet + ScaffoldPolicy on VariantBase (migration 0003, both variant types). use-hint serves next authored hint (generic fallback) returning {run,hint,hint_number}; builder/seed pass hint_set_template/scaffold_policy_template; attempt serializer exposes available_hints + scaffold_policy flags but forces expected_state off (no leak); FE shows hint inline.

Still deferred: move min/max/ideal_counted_commands onto variant; ChallengeRun rename + /api/challenge-runs/; physical app split + FE folder/component renames. Status section in `docs/refactor-plan.md`. NOT committed (user said don't commit yet).

See [[MEMORY]] index.
