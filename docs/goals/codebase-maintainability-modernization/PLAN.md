# Codebase Maintainability Modernization — Slice 1 Implementation Plan

**Intent:** Advance the broad maintainability goal through the smallest complete high-value slice: remove cross-story private imports from the advanced curriculum source graph and give reusable fixture/form-drill mechanics neutral owners.
**Current Behavior:** The fast repository guards are green, but `v3_skyline_form_drills.py` imports private constants, fixtures, and builders from the 3,017-line Frost story ledger; Frost imports private `_state` from `v3_advanced_workflows.py`; and `challenge_specs/v3_story_challenges.py` imports private `_state`, `_render`, and `_requirements` from that authored adventure ledger. Importing one story or challenge therefore depends on unrelated authored ledgers.
**Expected Outcome:** Three neutral support modules own reusable mechanics. Cross-mode advanced workflow state/requirement/render primitives live at the shared source root, form-drill constants/fixtures/builders no longer live in Frost, shared advanced challenge difficulty/scenario/variant mechanics no longer live in `v3_story_challenges`, and no authored `v3_*` adventure or challenge ledger imports reusable private mechanics from another authored ledger. Intentional public content edges for `LEVELS` and `INCIDENTS` remain because composers and challenges derive authored content from those catalogs. Curriculum content and generated targets remain identical.
**Target-Perspective Output:** A curriculum maintainer can inspect an ownership table, open the source-root neutral module to change cross-mode advanced repository fixtures, open the Adventure form support to change form-drill mechanics, open Challenge support to change shared challenge construction, and edit story-specific content without inheriting another ledger's private implementation. The evidence identifies intentional public content edges separately from reusable mechanics, and a source-wide AST test rejects private cross-ledger imports and bypass forms.
**Truth Owner:** `backend/curriculum/seed_data/source/advanced_story_support.py` owns `build_advanced_story_state`, `build_advanced_story_requirements`, and `render_advanced_story_command` plus their private commit/metadata builders. `adventure_level_specs/form_drill_support.py` owns public form-drill constants, clean/broken fixture builders, variant builders, evaluation builders, recursive placeholder rendering, and required-command checks. `challenge_specs/advanced_challenge_support.py` owns `ADVANCED_CHALLENGE_DIFFICULTY`, `build_advanced_challenge_variant`, and `advanced_challenge_scenario_copy` plus their private command-family/difficulty helpers. Authored modules retain `LEVELS`, `INCIDENTS`, story-specific fixtures, narratives, and scenario data.
**Contract Boundary:** `ADVENTURE_LEVELS` and challenge composition order, slugs, variants, repository states, evaluation specs, generated target bytes, public seed-data exports, database schema, API contracts, and UI behavior remain unchanged. Only internal source ownership and imports change.
**Cutover:** Create the source-root advanced support, Adventure form support, and Challenge advanced support; atomically repoint every caller; delete the moved definitions from their authored ledgers and delete the temporary Adventure-owned `adventure_level_specs/advanced_story_support.py` path. Former owners must call support through public or module-qualified names so their displaced attributes disappear. Skyline may retain local aliases for the public form-support contract because it was never an owner and exports only `LEVELS`; authored owner modules must not re-export displaced helpers.
**Displaced Path:** No authored `v3_*` module may import a private symbol from another `v3_*` module. Cross-ledger/composer imports may consume only explicit public content exports: `LEVELS`, `INCIDENTS`, `V3_CHALLENGES`, or `V3_FORM_CHALLENGES`. Normal module imports, package-relative module imports, and wildcard imports of `v3_*` ledgers are rejected because they can bypass the public-content boundary. Neutral support modules may not import any `v3_*` authored ledger, and `adventure_level_specs/advanced_story_support.py` must be absent.
**Value Density:** This removes three concrete wrong-owner dependency directions spanning the largest curriculum source modules without changing runtime, schema, API, or generated data, and establishes a durable ownership assertion before larger decomposition work.
**Acceptance Evidence:** Exact before/after import edges and line counts; an ownership/maintainer-inspection table; static rejection of displaced and bypass imports; canonical equality of the six affected composed content catalogs against `HEAD`; focused curriculum tests; Ruff; `generate_targets --check`; unchanged generated-target SHA-256; and the fast repository quality suite.
**Evidence Lane:** Baseline hash/metrics -> neutral-owner cutover -> static ownership test -> focused curriculum tests -> Ruff -> generated-target check/hash -> fast quality gates -> final diff and maintainer-inspection evidence.
**Kill Criteria:** Zero private `v3_* -> v3_*` imports; zero module/wildcard bypass imports of authored ledgers; zero `v3_*` imports from neutral support; no displaced binding on former owners (`v3_advanced_workflows`: `_base_commits`, `_metadata`, `_state`, `_requirements`, `_render`; Frost: `CORE_TAGS`, `STATUS`, `GRAPH`, `_clean`, `_broken`, `_dv`, `_read_eval`, `_req`, `_render_value`, `_required_check`; `v3_story_challenges`: `_DIFFICULTY`, `_family`, `_difficulty_extra`, `_scenario_copy`, `_advanced_variant`); no `LEVELS`, `INCIDENTS`, or authored scenario ledger in support modules; old Adventure-owned advanced support path absent; unchanged composed catalogs and generated-target SHA-256; no generated file, migration, API, or asset edit.
**Architecture Slice:** Human-authored curriculum source only: cross-mode advanced support at the shared source root, mode-specific Adventure form and Challenge construction support inside their mode packages, authored ledgers above those helpers, and existing composers/generated artifacts unchanged.
**Plan Review Gate:** Requires PRE review before execution.

## Architecture Map

### Files to create

- `backend/curriculum/seed_data/source/advanced_story_support.py`
- `backend/curriculum/seed_data/source/adventure_level_specs/form_drill_support.py`
- `backend/curriculum/seed_data/source/challenge_specs/advanced_challenge_support.py`
- `docs/goals/codebase-maintainability-modernization/EVIDENCE.md`

### Files to modify

- `backend/curriculum/seed_data/source/adventure_level_specs/v3_advanced_workflows.py`
- `backend/curriculum/seed_data/source/adventure_level_specs/v3_frost_form_drills.py`
- `backend/curriculum/seed_data/source/adventure_level_specs/v3_skyline_form_drills.py`
- `backend/curriculum/seed_data/source/challenge_specs/v3_story_challenges.py`
- `backend/curriculum/seed_data/source/challenge_specs/v3_chapter_form_challenges.py`
- `backend/curriculum/tests/test_seed_data_source_layout.py`

### Files to avoid

- `backend/curriculum/seed_data/generated/generated_targets.py` must remain byte-for-byte unchanged.
- Other authored ledgers, public seed-data compatibility exports, historical migrations, generated API files, frontend code/assets, caches, local databases, archives, and unrelated user-owned files.

### Source of truth

- Shared advanced repository fixture truth: source-root `advanced_story_support.py`.
- Shared form-drill mechanics truth: `form_drill_support.py`.
- Shared advanced challenge construction truth: `challenge_specs/advanced_challenge_support.py`.
- Authored content truth: the existing `v3_*` adventure and challenge ledger modules.
- Composition truth: existing adventure/challenge package composers; unchanged by this slice.

### Read/write path and integration points

- Read/import path after cutover: neutral support -> authored adventure/challenge ledgers -> package composers -> public seed-data exports -> seed command.
- Generated write path remains: authored/composed specs -> frontend simulator replay -> `generated_targets.py`; this slice runs it in `--check` mode only.
- Integration points are Python imports, curriculum spec composition, challenge derivation from adventure incidents, and generated target replay. There is no database or API migration.

### Displaced-path and acceptance gate

`test_seed_data_source_layout.py` must AST-scan every `.py` file beneath `backend/curriculum/seed_data/source/`. It rejects private symbols imported between any `v3_*` ledgers, normal module imports, package-relative module imports, and wildcard imports of authored ledgers; permits only the four explicit public content exports; rejects `v3_*` imports and authored content bindings in neutral support; proves every enumerated displaced binding is absent from each former owner; and proves the temporary Adventure-owned advanced support path is absent. Focused content equality/tests and generated-target identity must then pass before the slice is accepted.

## Task 1: Extract neutral advanced-story fixture ownership

**Exact scope:** Create source-root `advanced_story_support.py`; move `_base_commits`, `_metadata`, `_state`, `_requirements`, and `_render` from `v3_advanced_workflows.py`; expose the public names `build_advanced_story_state`, `build_advanced_story_requirements`, and `render_advanced_story_command`; keep base-commit/metadata helpers private; import `commit`/`repo` directly from `curriculum.seed_data.spec_helpers` so the neutral module does not load Adventure composers. Repoint `v3_advanced_workflows.py`, `v3_frost_form_drills.py`, `form_drill_support.py`, and Challenge support. Delete `adventure_level_specs/advanced_story_support.py`. Do not re-export or alias the helpers as `_state`, `_render`, or `_requirements` on `v3_advanced_workflows`.
**Expected output:** Reusable advanced fixture construction is independent of every authored `v3_*` ledger. `v3_advanced_workflows.py` owns only incident types, variant/narrative/level assembly, `INCIDENTS`, and `LEVELS`.
**Verification:** The source-wide AST ownership test in Task 4 is authoritative. From `backend`, run `ruff check curriculum/seed_data/source/advanced_story_support.py curriculum/seed_data/source/adventure_level_specs/v3_advanced_workflows.py curriculum/seed_data/source/adventure_level_specs/v3_frost_form_drills.py curriculum/seed_data/source/challenge_specs/advanced_challenge_support.py curriculum/seed_data/source/challenge_specs/v3_story_challenges.py` and an isolated import smoke proving that importing `curriculum.seed_data.source.advanced_story_support` does not load any `v3_*` module.
**Acceptance evidence:** Ownership test proves the neutral module imports no `v3_*` ledger; before/after dependency table shows all three callers point at the neutral owner.
**Parallel:** No. It establishes the lower-level fixture contract used by Task 2.

## Task 2: Extract neutral form-drill ownership

**Exact scope:** Create `form_drill_support.py`; move `CORE_TAGS`, `STATUS`, `GRAPH`, `_clean`, `_broken`, `_dv`, `_read_eval`, `_req`, `_render_value`, and `_required_check` from Frost. Expose exactly `CORE_FORM_TAGS`, `STATUS_COMMAND`, `GRAPH_COMMAND`, `build_clean_form_state`, `build_broken_form_state`, `build_drill_variants`, `build_read_evaluation`, `build_requirement_evaluation`, `render_variant_value`, and `required_command_check`. Frost must use module-qualified or public names directly so all ten displaced owner bindings disappear. Skyline may import public names under existing local aliases because it was never the owner and exports only `LEVELS`. The module may depend on source-root `advanced_story_support.py` and `.common`, but no authored ledger.
**Expected output:** Frost and Skyline both consume the neutral form-drill owner; Frost retains only story-specific fixtures/helpers and authored content; Skyline has no Frost import.
**Verification (repository root):** `rg -n 'v3_frost_form_drills import' backend/curriculum/seed_data/source/adventure_level_specs/v3_skyline_form_drills.py` returns no matches; ownership/content tests in Task 4 pass.
**Acceptance evidence:** Import graph and ownership table show both story ledgers as siblings; support files define no authored ledgers.
**Parallel:** No. It depends on Task 1's neutral state builder.

## Task 3: Extract neutral advanced-challenge construction ownership

**Exact scope:** Create `challenge_specs/advanced_challenge_support.py`; move `_DIFFICULTY`, `_family`, `_difficulty_extra`, `_scenario_copy`, and `_advanced_variant` from `v3_story_challenges.py`; expose exactly `ADVANCED_CHALLENGE_DIFFICULTY`, `advanced_challenge_scenario_copy`, and `build_advanced_challenge_variant`; keep command-family/difficulty helpers private. Repoint both `v3_story_challenges.py` and `v3_chapter_form_challenges.py` to public names.
**Expected output:** Both authored challenge ledgers are sibling consumers of Challenge-owned support and share no private implementation imports. Authored challenge lists and public exports remain in their existing ledgers.
**Verification:** Source-wide AST ownership test; Ruff over the support and both callers; canonical equality for `V3_CHALLENGES` and `V3_FORM_CHALLENGES` against `HEAD`.
**Acceptance evidence:** Import graph shows no private `v3_* -> v3_*` edge and challenge catalog hashes/objects are unchanged.
**Parallel:** No. It consumes the Task 1 source-root fixture contract.

## Task 4: Enforce ownership and prove content identity

**Exact scope:** Extend `backend/curriculum/tests/test_seed_data_source_layout.py` with the exact displaced-import and neutral-module assertions; create `EVIDENCE.md`; make only narrowly attributable fixes in the files listed by this plan.
**Expected output:** A durable source-wide AST test rejects private cross-ledger imports and all bypass forms while explicitly allowing public `LEVELS`/`INCIDENTS` content edges. Evidence records before/after owners, import edges, module line counts, canonical content equality, maintainer inspection scenarios, commands, test counts, and the generated-target hash.
**Verification:** From `backend`: `python -m pytest curriculum/tests/test_seed_data_source_layout.py curriculum/tests/test_three_story_curriculum.py curriculum/tests/test_level_brief_required_details.py curriculum/tests/test_challenge_form_coverage.py -q`; `ruff check curriculum/seed_data/source/advanced_story_support.py curriculum/seed_data/source/adventure_level_specs/form_drill_support.py curriculum/seed_data/source/adventure_level_specs/v3_advanced_workflows.py curriculum/seed_data/source/adventure_level_specs/v3_frost_form_drills.py curriculum/seed_data/source/adventure_level_specs/v3_skyline_form_drills.py curriculum/seed_data/source/challenge_specs/advanced_challenge_support.py curriculum/seed_data/source/challenge_specs/v3_story_challenges.py curriculum/seed_data/source/challenge_specs/v3_chapter_form_challenges.py curriculum/tests/test_seed_data_source_layout.py`; `python manage.py generate_targets --check`. From repository root: canonical object/hash comparison of affected catalogs against `HEAD`; `python scripts/check_quality_gates.py`; `git diff --check`; `git diff --exit-code -- backend/curriculum/seed_data/generated/generated_targets.py`.
**Acceptance evidence:** Focused tests and all fast guards pass; all affected composed catalogs equal `HEAD`; generated target SHA-256 remains `6EE61275D1571FABD983C5602FA2D323A5DAF4B6F637FA71D3B617B0F916DF54`; the evidence table answers where a maintainer changes shared state, form mechanics, Challenge construction, Frost content, Skyline content, incident content, and challenge content; old imports and bypass forms are mechanically rejected.
**Parallel:** No. This is the terminal gate for Slice 1.

### Canonical catalog equality lane

Compare these six exact outputs: `v3_advanced_workflows.INCIDENTS`, `v3_advanced_workflows.LEVELS`, `v3_frost_form_drills.LEVELS`, `v3_skyline_form_drills.LEVELS`, `v3_story_challenges.V3_CHALLENGES`, and `v3_chapter_form_challenges.V3_FORM_CHALLENGES`.

Canonical serialization uses `json.dumps(value, sort_keys=True, separators=(",", ":"), default=...)`; the default converts dataclass instances with `dataclasses.asdict` and sets to sorted lists. Record SHA-256 for each serialized output.

Baseline isolation is an extracted temporary archive, not imports from the dirty working tree: create a temporary directory with PowerShell `New-Item`, run `git archive --format=zip --output <temp>/head.zip HEAD backend/curriculum`, expand it, and run the canonical hash snippet with working directory `<temp>/backend`. Run the identical snippet from the working-tree `backend`, compare the six name/hash maps exactly, then remove only the resolved temporary directory after verifying it lies under the system temp path. Any mismatch blocks acceptance.

## Follow-up slices (not authorized by this plan)

The broader goal remains active after Slice 1. The next candidates are the admin HTTP/read-model ownership split and the authoring/home frontend decompositions identified by the audit. Each needs its own exact architecture map, file/contract list, target-perspective evidence, and PRE review before code changes.
