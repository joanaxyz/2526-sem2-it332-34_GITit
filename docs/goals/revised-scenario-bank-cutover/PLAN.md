# Revised Scenario Bank Cutover Implementation Plan

**Intent:** Make the seeded Runebound Turret curriculum faithfully implement the attached 265-scenario revised bank, including learner-facing copy, canonical solution routes, replacement variants, command budgets, conflict-edit workflows, and grading state.
**Current Behavior:** The seed overlays only labels, narrative fragments, real-world context, tasks, and required file values onto the archived scenarios. It deliberately keeps old case IDs, old initial states, old solution commands, old evaluation rules, and old generated targets for 21 replacement scenarios; it also omits the authored objective checklist and expected result from the learner contract.
**Expected Outcome:** All 265 published legacy variants use the document's Variant ID and authored content, replay the document's Answer Key through the real simulator, expose the document's checklist and expected result, and evaluate the requested end state. Replaced scenarios are newly seeded and displaced variants are unpublished without deleting historical runs.
**Target-Perspective Output:** A learner opening any Runebound Turret tier sees that selected variant's exact story, starting point, real-world context, task, checklist, required resolved-file content, and expected result; following the authored Answer Key reaches completion within that scenario's stated command budget.
**Truth Owner:** `backend/curriculum/seed_data/revised_legacy_scenarios.json`, generated from the supplied Markdown by `scripts/curriculum/import_revised_scenarios.py`, owns the revised authored contract. Runtime-only repository fixtures and machine evaluation overrides live in `backend/curriculum/seed_data/revised_legacy_runtime.py`.
**Contract Boundary:** `seed_legacy_modules.py` joins canonical scenario metadata to runtime fixture/evaluation data and persists `AdventureLevelTierWaveVariant`; `generate_targets` replays its canonical solution commands through the frontend Git engine; tier-run payload normalization carries only learner-facing fields to the UI.
**Cutover:** Replace positional stable-slot aliases with the document's 265 Variant IDs, seed new rows for the 21 replacement IDs, unpublish every no-longer-authored variant in each affected wave, and regenerate target states and solution trajectories from canonical commands.
**Displaced Path:** The learner-only overlay keyed by archived case IDs and the 21 old published variants are displaced. The archived 13,000-line fixture remains a fallback source only for unchanged runtime states until it is separately retired; it no longer owns revised IDs, commands, budgets, or learner content.
**Value Density:** One canonical import and one runtime adaptation boundary update all 265 scenarios; focused runtime overrides cover only genuinely replaced exercises.
**Acceptance Evidence:** A seeded database contains exactly 265 published revised Variant IDs with document-accurate metadata and budgets; canonical replay generates targets for every ID; every generated target passes its evaluation spec; representative browser-facing payload/UI tests prove starting point, checklist, required file content, and expected result are visible without staff-only text.
**Evidence Lane:** Parser/contract tests, seed integration tests, simulator unit tests, full target regeneration/check, evaluator replay audit, and focused frontend tests.
**Kill Criteria:** No published variant retains one of the 21 displaced IDs; no `source_case_id` alias maps a revised scenario onto an old runtime exercise; no seed path may source revised solution commands or learner text from the archived case literal when canonical data exists.
**Architecture Slice:** Canonical document import -> revised JSON -> runtime case adaptation -> legacy seed writer -> generated targets/trajectories -> tier-run payload -> tier workspace. Git command execution and workspace edits are the simulator boundary.
**Plan Review Gate:** Requires PRE review before execution.

## Architecture Map

**Files to create:**

- `scripts/curriculum/import_revised_scenarios.py`
- `backend/curriculum/seed_data/revised_legacy_runtime.py`
- focused backend/frontend regression tests as needed

**Files to modify:**

- `backend/curriculum/seed_data/revised_legacy_scenarios.json`
- `backend/curriculum/seed_data/revised_legacy_scenarios.py`
- `backend/curriculum/management/commands/seed_legacy_modules.py`
- `backend/curriculum/seed_data/generated/generated_targets.py`
- `backend/curriculum/seed_data/generated/generated_trajectories.py`
- tier-run context/budget plumbing and the mirrored Python/TypeScript workspace-file behavior
- frontend Git command handlers for revised conflict workflows
- tier scenario context types, normalization, objectives, and story presentation

**Files to avoid:**

- unrelated Arcane Spire/Frostbound/Neon authored curriculum
- historical run rows and destructive data migrations
- hand-editing generated target or trajectory payloads

**Source of truth:** Revised JSON generated from the supplied Markdown; focused runtime overrides only where prose cannot encode a deterministic repository fixture.
**Read path:** Revised JSON and runtime adapter are imported by `seed_legacy_modules.py` and `generate_targets.py`; seeded variants feed run selection, payloads, and evaluation.
**Write path:** Import script writes canonical JSON; seed command uses idempotent `update_or_create` and unpublishes displaced rows; target generation writes committed generated artifacts.
**Contract boundary:** Canonical metadata is document-shaped; runtime cases are simulator-shaped; `seed_legacy_modules.py` is the explicit join.
**Integration points:** Variant selection, tier-run budget snapshots, scenario context normalization, workspace file saves, frontend simulator command replay, evaluation rules, and target generation.
**Migration/cutover:** No destructive schema migration. New IDs create new variant rows; old rows are unpublished to preserve protected historical references.
**Displaced path:** Archived IDs/commands/content are fallback-only and cannot override canonical revised fields.
**Acceptance evidence gate:** The seed/replay/evaluation audit must pass for all 265 revised IDs before completion.

## Tasks

### 1. Import the complete authored contract

**Files:** `scripts/curriculum/import_revised_scenarios.py`, `backend/curriculum/seed_data/revised_legacy_scenarios.json`, `backend/curriculum/seed_data/revised_legacy_scenarios.py`, parser tests.
**Allowed scope:** Parse the 265 scenario sections and their learner/staff blocks deterministically; preserve code-block content and command order; reject duplicates or missing required sections.
**Expected output:** JSON keyed directly by document Variant ID with scenario number, difficulty, title, story, starting point, context, task, required files, checklist, expected result, answer commands, alternatives, evaluation text, and min/max counted commands.
**Verification:** Run importer in `--check` mode and parser/contract tests.
**Acceptance evidence:** Counts are 265 / 99 / 82 / 84, IDs are unique, and selected scenarios round-trip exact Markdown values.
**Parallel:** No; this defines the contract used by later tasks.

### 2. Cut revised IDs and commands into the seed

**Files:** `backend/curriculum/seed_data/revised_legacy_runtime.py`, `backend/curriculum/management/commands/seed_legacy_modules.py`, seed tests.
**Allowed scope:** Adapt archived fixture states by scenario number, replace all canonical fields, author deterministic overrides for 21 replacement scenarios, set per-variant budgets, and unpublish displaced IDs.
**Expected output:** `LEGACY_MODULE_LEVELS` exposes exactly the revised IDs and canonical solution commands; persisted variants use canonical learner context and backend-only runtime/evaluation data.
**Verification:** Seed idempotency and revised-bank integration tests.
**Acceptance evidence:** Exactly 265 revised variants are published after two seed runs; all displaced IDs are unpublished; no alias IDs remain.
**Parallel:** No; depends on task 1.

### 3. Complete simulator support required by canonical routes

**Files:** TypeScript Git simulator commands/workspace files, mirrored backend workspace-file implementation, focused tests.
**Allowed scope:** Merge-tool saves stage selected conflicts, conflicted cherry-picks can start/continue/abort, stopped rebases can continue remaining commits or abort, and no unrelated command semantics change.
**Expected output:** Revised Answer Key routes are processable exactly as authored.
**Verification:** Targeted Vitest and backend workspace-file tests.
**Acceptance evidence:** The revised mergetool, cherry-pick-conflict, rebase-abort, and rebase-continue scenario replays succeed.
**Parallel:** Can overlap task 2 only after fixture shapes are fixed; integration proof remains serial.

### 4. Expose the complete learner-facing briefing

**Files:** scenario context normalizer/types, tier story/objective utilities and components, payload/frontend tests.
**Allowed scope:** Add starting point, expected result, and variant checklist labels to the learner-facing contract; keep every staff-only field filtered.
**Expected output:** Story modal and objectives card render the document's content for the selected variant; required file values remain copyable.
**Verification:** Backend context tests and focused frontend component/utility tests.
**Acceptance evidence:** Representative initialization and conflict scenarios show all required learner sections and no staff-only data.
**Parallel:** Can proceed after task 1 with disjoint frontend/context files.

### 5. Regenerate and audit every target

**Files:** generated targets and trajectories; targeted evaluation fixes in runtime overrides.
**Allowed scope:** Run the real generator, repair only canonical-route or evaluation mismatches, and keep accepted end-state behavior broad enough for documented alternatives.
**Expected output:** Fresh targets/trajectories for all revised IDs; no stale displaced IDs in generated legacy targets.
**Verification:** `python manage.py generate_targets`, `python manage.py generate_targets --check`, seed-target structural check, and all-265 evaluator replay test.
**Acceptance evidence:** 265/265 canonical solutions process successfully and 265/265 final states match their evaluation specs.
**Parallel:** No; final integration gate.

### 6. Final regression gate

**Files:** none unless a failing gate identifies a scoped defect.
**Allowed scope:** Focused backend curriculum/adventure/evaluation tests, frontend simulator and tier workspace tests, formatter/linter checks for touched files.
**Expected output:** Clean working tree diff limited to this cutover and its generated artifacts.
**Verification:** Report exact commands and outcomes.
**Acceptance evidence:** Seed, replay, evaluator, and learner-facing tests all pass; any unrun broad suite is stated explicitly.
**Parallel:** No.

## PRE Review

**Mode:** PRE
**Verdict:** aligned

- The outcome is learner-visible and measurable, not merely a JSON rewrite.
- Truth ownership separates authored document data from deterministic simulator fixtures.
- The cutover names and unpublishes displaced IDs while preserving historical rows.
- Acceptance evidence includes full canonical replay and evaluation from the learner path, stronger than static tests alone.
- The broad archived fixture is explicitly demoted rather than duplicated as another revised source of truth.

**Recommended next gate:** Execute tasks 1-5, then require the all-265 replay/evaluation audit before the final regression gate.

## POST Review

**Mode:** POST
**Verdict:** aligned

- The generated contract contains all 265 authored Variant IDs with the required 99 easy, 82 medium, and 84 hard scenarios; importer `--check` validates it directly against the supplied Markdown.
- The seed publishes exactly those 265 IDs, persists per-variant budgets and complete learner briefings, and generically unpublishes displaced rows without deleting historical data.
- The real target generator replayed 2,321 total variant solutions, and the revised-bank evaluator audit passed all 265 canonical target states.
- Focused backend regression coverage passed 34 tests; the frontend suite passed 947 tests before the final compatibility shim, its 16 directly affected tests passed after that shim, and the final production build and ESLint run passed.
- Correctness review found no unresolved mismatch between canonical commands, runtime fixtures, generated targets, evaluator rules, or learner-facing fields.
- Maintainability review confirms one authored truth owner, one explicit runtime adaptation boundary, and no remaining seed reference to the displaced `tier_targets.json` path.
- The teammate's remote briefing change was selectively incorporated as legacy payload compatibility and paragraph-preserving presentation. Its backend string-splitting contract was not adopted because explicit `starting_point` ownership supersedes it.
- The repository-wide curriculum suite contains 1,900 collected tests and was not run to completion because of its multi-hour execution profile; the scoped seed, replay, evaluator, context, budget, workspace, simulator, UI, type-check, build, lint, and Django checks are the acceptance evidence for this cutover.
