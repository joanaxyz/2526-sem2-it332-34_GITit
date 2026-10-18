# Arcane Spire Story-Record Cutover Implementation Plan

**Intent:** Make the existing Runebound curriculum the sole active story record, rename that same record to `arcane-spire` / `The Arcane Spire`, retain its Arcane visual world, and remove the obsolete Arcane, Frostbound, and Neon database trees.
**Current Behavior:** The database contains four published `curriculum.Story` rows. `git-it-legacy` owns Runebound's 5 chapters, 21 levels, 63 tiers, and all current tier progress. Separate `arcane-spire`, `frostbound-citadel`, and `neon-backstreets` rows own 29 chapters and 240 unrelated levels. The normal `seed_all` path recreates all four records, while frontend routing and progress metrics still identify Runebound by `git-it-legacy`.
**Expected Outcome:** Story id 11 remains the curriculum and progress owner but is renamed to slug `arcane-spire`, title `The Arcane Spire`, and world `arcane-spire`. The three obsolete rows and their chapter/level/challenge/drill trees are removed. Normal seeds, routes, APIs, progress metrics, and achievements use the surviving slug and cannot recreate the retired records.
**Target-Perspective Output:** Learners see one story named The Arcane Spire, rendered with the existing Arcane assets, containing exactly the former Runebound modules and progress. No Frostbound, Neon, or second Arcane campaign appears in the story list or Progress tab.
**Truth Owner:** `seed_legacy_modules.py` remains the source of truth for the surviving 5-chapter/21-level curriculum. `curriculum.Story` remains the persisted identity owner. `world_slug="arcane-spire"` and the existing frontend story-world registry remain the visual-asset owner.
**Contract Boundary:** Canonical seed -> `Story`/`Chapter` rows -> curriculum APIs and progress queries -> frontend default story route and achievements.
**Cutover:** In one irreversible data migration, clear retired-story prerequisite links, delete the retired chapter trees and story rows, then rename the existing Runebound row in place. In the same code change, point canonical seeds and consumers at the surviving slug.
**Displaced Path:** The production `seed_all` path no longer invokes the three-story `seed_curriculum` fixture. `git-it-legacy` is removed from runtime routing, metrics, active seed constants, and current achievement logic. The retired authoring fixture may remain for isolated historical/runtime tests, but it is not a canonical or deployment seed and must refuse to overwrite a surviving Runebound-owned `arcane-spire` row.
**Value Density:** One narrow migration plus seed/consumer cutover removes three large stale database trees while preserving the only curriculum and all of its PK-linked learner progress.
**Acceptance Evidence:** Pre/post database identity and content fingerprints; migration test covering collision deletion and in-place rename; canonical-seed test proving a single story; story API, progress, routing, achievement, frontend build/lint, backend targeted suites, and migration checks.
**Evidence Lane:** Read-only production-shaped inventory -> migration unit/integration proof -> canonical seed proof -> backend API/progress regression -> frontend route/achievement regression -> current database migration and post-cutover fingerprint.
**Kill Criteria:** Exactly one active story record exists after migration and normal seeding; its id is the former Runebound id; it has 5 chapters, 21 levels, 63 tiers, and unchanged level/tier identities; all existing Runebound tier runs/progress/completions still point to those identities; no normal seed recreates Frostbound, Neon, or the displaced modern Arcane tree; no runtime `git-it-legacy` fallback remains; Arcane assets remain selected; no unrelated dirty file changes.
**Architecture Slice:** Story-record migration, canonical seeding, story/progress routing, and name/slug-facing tests only. Runebound lesson/scenario/tier content, simulator behavior, asset files, shared command library content, and retired authored source fixtures are not rewritten.
**Plan Review Gate:** Self-reviewed PRE because team-agent delegation is disabled for this task; implementation starts only after every destructive dependency and reseed path is represented below.

## Architecture Map

### Source and write paths

- Active curriculum source: `backend/curriculum/management/commands/seed_legacy_modules.py`.
- Canonical orchestration: `backend/common/management/commands/seed_all.py` and deployment startup scripts.
- Database cutover: new `backend/curriculum/migrations/0004_*.py`.
- Retired explicit fixture: `backend/curriculum/management/commands/seed_curriculum.py` and `backend/curriculum/seed_data/**`; retained only so unrelated engine fixture tests do not require a curriculum rewrite.

### Read paths

- Backend progress owner: `backend/progress/services/metrics.py` and explanatory objective docs/tests.
- Curriculum list/chapter APIs: existing selectors/views read the database and require no production branching.
- Frontend default route: `frontend/src/shared/navigation/routes.ts` and `StoryMapPage.tsx`.
- Frontend completion badge: `frontend/src/features/home/utils/achievements.ts`.

### Database dependency and deletion order

1. Resolve the survivor by `git-it-legacy`; abort if it is absent or if the slug collision is ambiguous.
2. Null retired stories' `prerequisite_story` links so the self-referential `PROTECT` relation cannot block deletion.
3. Delete chapters belonging to the existing `arcane-spire`, `frostbound-citadel`, and `neon-backstreets` rows. Their lessons, command forms, levels, waves, variants, challenges, and drills cascade. The live inventory has no player runs/completions on these trees.
4. Delete the three now-childless retired stories.
5. Update the survivor in place to slug `arcane-spire`, title `The Arcane Spire`, world `arcane-spire`, published beginner sort order zero. Never recreate or re-parent its children.

The migration is deliberately irreversible: deleted authored runtime rows cannot be reconstructed safely by a reverse migration. Recovery requires a database backup.

### Files to create

- `backend/curriculum/migrations/0004_collapse_story_records_to_arcane_spire.py`
- Focused migration/seed regression test if no existing test can express the identity-preservation contract cleanly.
- `docs/goals/arcane-spire-story-record-cutover/EVIDENCE.md`

### Files to modify

- Active seed constants/story metadata and canonical `seed_all` orchestration/tests.
- Retired seed command guard/help so it cannot overwrite the active row.
- Backend progress constant/comments/tests and active curriculum access tests.
- Frontend default route/fallback, current achievement slug, and focused tests.
- Docker startup seed command if it still bypasses `seed_all`.

### Files to preserve

- All Runebound module, lesson, level, tier, wave, variant, target-state, and solution literals.
- All files under frontend story-world asset/registry ownership; only the persisted `world_slug` selects them.
- Unrelated dirty changes, especially `backend/common/models.py`, the untracked adventures/challenges migrations, and `docs/goals/learner-progress-kpi-instrument/`.

## Task Board

### Task 1 — Freeze the destructive cutover contract

- **Files:** This plan and evidence notes only.
- **Work:** Record exact story ids/counts, dependency protections, progress counts, canonical seed callers, and dirty-worktree exclusions.
- **Verification:** Read-only Django inventory and repository searches.
- **Evidence:** Survivor id 11 owns 5 chapters/21 levels/63 tiers/166 tier runs/158 progress rows/59 tier completions; retired trees own no run or completion records in the current database.

### Task 2 — Implement the identity-preserving data migration

- **Files:** New curriculum migration and focused migration test.
- **Work:** Perform the exact dependency order above, fail loudly on unsafe ambiguity, and update the survivor rather than inserting a replacement.
- **Verification:** Migration executor or direct migration-function test covers collision, cascaded retirement, unchanged survivor PK/child PKs, and no-op-safe missing retired rows.
- **Evidence:** Pre/post fingerprints prove only name/slug/story metadata changed on the survivor.

### Task 3 — Cut canonical seeds and runtime consumers over

- **Files:** Active seed, `seed_all`, retired fixture guard, deployment startup, backend progress/runtime references, frontend route/fallback/achievement references, and their focused tests.
- **Work:** Seed only Runebound under its new identity; keep `world_slug=arcane-spire`; prevent canonical or accidental retired seeding from replacing it; update runtime consumers to `arcane-spire`.
- **Verification:** A clean seeded test database has one story and the unchanged Runebound shape. Static runtime search finds no `git-it-legacy`, Frostbound, or Neon consumer path outside migration/history fixtures.
- **Evidence:** Seed orchestration call assertions, story-access response, progress command-mastery regressions, route tests, and achievement tests.

### Task 4 — Verify and apply the cutover

- **Files:** `EVIDENCE.md`; implementation files only for attributable fixes.
- **Work:** Run targeted and relevant broader suites, migration checks, lint/build, migrate the current database, and capture the post-cutover inventory.
- **Verification:** Backend pytest suites, frontend Vitest/build/ESLint, `manage.py makemigrations --check`, `manage.py migrate`, `git diff --check`, and dirty-manifest comparison.
- **Evidence:** One surviving story with the former Runebound id and exact content/progress counts; retired slugs absent; Progress exposes only the 18 Runebound command masteries.

## PRE Self-Review

- The plan preserves identity instead of copying data, so PK-linked progress survives.
- Deletion order accounts for `Story.prerequisite_story` and `Chapter.story` using `PROTECT`; chapter descendants are verified cascade-safe in the live inventory.
- Canonical reseeding is explicitly in scope, preventing the deleted records from returning.
- The existing Arcane asset selection is preserved through `world_slug`; no bitmap or registry rewrite is authorized.
- The authored retired fixture is separated from production ownership to avoid a massive unrelated engine-test rewrite, but receives a collision guard.
- Destructive recovery is explicit: reverse migration cannot restore deleted trees; database backup is the recovery path.
- No open ownership, contract, cutover, or evidence ambiguity remains.
