# Repository Foundations Ledger Decomposition — Slice 16 Implementation Plan

**Intent:** Make the authored Repository Foundations curriculum navigable and maintainable by concept. A curriculum maintainer should be able to find cloning, configuration and ignore rules, founding workflows, or a drill family without searching through one 2,887-line literal, while all published curriculum data remains identical.

**Current Behavior:** One clean 2,887-line module owns all 17 ordered levels and 76 waves, and its stable export feeds the blueprint catalog, seeding, public wrappers, and generated targets.

**Expected Outcome:** Seven concept-owned leaf ledgers below 700 lines feed one stable public composer below 50 lines, with exact data/order/generated equivalence and an explicit fast topology gate.

**Target-Perspective Output:** A maintainer opens one named concept file for content and sees the complete publication order in the tiny composer; a reviewer runs one dedicated layout command plus existing curriculum gates.

**Truth Owner:** Each leaf owns its literal level dictionaries, the stable composer owns cross-leaf order and `ADVENTURE_LEVELS`, and the dedicated curriculum source-layout checker owns enforcement of that topology.

**Contract Boundary:** `curriculum.seed_data.source.blueprint.adventure_repository_foundations.ADVENTURE_LEVELS`, `BLUEPRINT_ADVENTURE_LEVELS["repository-foundations"]`, all list/object projections, and generated target bytes remain stable.

**Cutover:** Mechanically move captured dictionary source blocks into the seven leaves, adjust only helper-import depth, and replace the monolith atomically with the ordered composer.

**Displaced Path:** The inline 17-level literal leaves the stable composer completely; no duplicate, fallback, facade, registry, or alternate public assembly path remains.

**Value Density:** Replace one 2,887-line mixed-concern owner with seven focused ledgers below 700 lines, one composer below 50 lines, and one focused architectural regression check.

**Acceptance Evidence:** Replay per-level AST/source hashes, canonical runtime JSON/order/counts, stable/public projections, generated target bytes, controlled topology mutations, exact command results, and strict whole-worktree preservation.

**Evidence Lane:** CLI/data-flow lane: static source-layout checks, imported curriculum object equivalence, generated-target currency, focused/full pytest suites, fast gate aggregation, diff hygiene, and manifest replay.

**Risk if Wrong:** A dropped, duplicated, or reordered dictionary can silently change learner progression or target generation; a weak cutover can leave competing curriculum truth paths that drift later.

**Kill Criteria:** The old literal is gone; each slug has exactly one declared leaf owner; imports and size ceilings match the architecture map; stable/public/generated outputs are exact; unrelated and dirty paths are untouched.

**Architecture Slice:** Only the clean Repository Foundations composer, its new concept package/test/checker, the clean fast-gate registry, the stale authored-source README, and goal-local evidence artifacts may change.

**Plan Review Gate:** Requires PRE review before execution.

**Current State:** `backend/curriculum/seed_data/source/blueprint/adventure_repository_foundations.py` is a clean 2,887-line authored module containing one `ADVENTURE_LEVELS` list with 17 ordered level dictionaries and 76 waves. It is the largest clean authored source ledger. Its stable import feeds `source/blueprint/__init__.py`, the `repository-foundations` blueprint catalog entry, public catalog wrappers, seeding, and committed generated targets. `source/README.md` still describes this directory as a future migration landing zone even though authored source is already canonical.

**Expected End State:**

- The stable module `source.blueprint.adventure_repository_foundations` is a composer of no more than 50 physical lines and remains the sole public owner of `ADVENTURE_LEVELS`.
- Seven concept modules under `source/blueprint/repository_foundations/` each own one `LEVELS` literal and are no more than 700 physical lines:
  - `fresh_starts.py`: `start-a-repository` through `practice-fresh-starts`.
  - `history_and_status.py`: `read-history` through `status-at-a-glance`.
  - `cloning.py`: `copy-a-project` through `clone-drills`.
  - `configuration.py`: `configure-identity-and-aliases` and `ignore-noise`.
  - `founding_workflows.py`: `founding-workflows`.
  - `fresh_start_drills.py`: `fresh-start-drills`.
  - `inspection_drills.py`: `inspection-drills`.
- The composer imports those seven lists in the order above and flattens them once into the existing `ADVENTURE_LEVELS` export. Leaf modules import only the shared `_wave` helper and do not import one another or the composer.
- A dedicated `scripts/checks/check_curriculum_source_layout.py` command enforces the exact topology, ownership, slug allocation, ordering, and size ceilings through a pure, synthetic-testable validator, and the existing fast-gate aggregate invokes it explicitly.
- `source/README.md` describes the current authored-source and generated-output ownership truthfully.

**Target-Person Output:** A curriculum maintainer finds clone exercises directly in `cloning.py`, identity/alias/ignore content directly in `configuration.py`, and the complete publication order in a composer short enough to inspect at a glance. A reviewer runs the dedicated source-layout check for topology drift and the unchanged seed-target check for authored/generated drift.

**Truth Owners:**

| Concern | Canonical owner |
|---|---|
| Literal level dictionaries and waves for one concept group | The corresponding `repository_foundations/*.py` leaf |
| Cross-group order and stable `ADVENTURE_LEVELS` export | `adventure_repository_foundations.py` |
| `repository-foundations` catalog key and cross-adventure order | Existing `source/blueprint/__init__.py` |
| Wave construction | Existing `source/blueprint/helpers.py` |
| Generated target serialization | Existing generator and `seed_data/generated/generated_targets.py` |
| Repository Foundations source-layout enforcement | `scripts/checks/check_curriculum_source_layout.py` |

**Contract Boundary:** The public import path, export name and list shape remain `curriculum.seed_data.source.blueprint.adventure_repository_foundations.ADVENTURE_LEVELS`. The `BLUEPRINT_ADVENTURE_LEVELS["repository-foundations"]` entry, level slug sequence, wave sequence, dictionaries, runtime objects, public catalog projections, and generated target bytes remain identical.

**Read Path:** Seven canonical leaf lists → stable ordered composer → unchanged blueprint adventure map → unchanged generated/public curriculum layers and seed commands. The dedicated layout validator statically reads the composer and leaf package; the existing seed-target validator continues, unchanged, to import authored catalogs and compare them with generated cases.

**Cutover Strategy:** Capture the clean monolith as the source of truth, including exact source segments and normalized data fingerprints for every level. Mechanically move the 17 existing dictionary source blocks, without rewriting their content, into the seven declared leaf lists. Change only the helper import depth required by the new package. Replace the monolith with the stable ordered composer in the same cutover. Add no compatibility facade, duplicate literal, fallback, registry, or alternate public path.

**Displaced Path:** The inline 17-level literal leaves `adventure_repository_foundations.py` completely. After cutover, that file owns ordering and the public export only; literal level dictionaries exist exactly once in their declared leaf modules.

**Value Density:** One 2,887-line mixed-concern ledger becomes seven discoverable concept ledgers below 700 lines and one composer below 50 lines. The change adds a durable architectural guard while keeping product data byte-equivalent.

**Evidence Contract:**

- A complete visible-worktree baseline records status, existence, bytes, and SHA-256 for every path outside the mutable allowlist, plus exact preimages or absence for every allowed implementation path.
- The original module's file SHA-256, normalized imported JSON SHA-256, 17-level/76-wave counts, ordered level slugs, ordered per-level wave slugs, and normalized AST/source-segment SHA-256 for every level dictionary replay after cutover.
- The stable module export, blueprint map entry, generated/public catalog projections, and generated target file bytes/SHA-256 replay exactly.
- The direct `scripts/checks/check_seed_targets.py` command preserves its success stdout, stderr, and exit status. The new source-layout command has its own stable success contract, and synthetic mutations prove its validator rejects wrong modules, ownership, order, slug allocation, dependencies, and size ceilings.
- The expensive `scripts/checks/check_generated_targets_current.py` guard confirms committed targets remain current when dependencies are available.
- Focused layout tests, relevant curriculum invariant/routing tests, the complete curriculum test suite, fast quality gates, generated-target currency, and `git diff --check` pass.
- A goal-local verifier reproduces content, topology, test, command, and preservation evidence after implementation and after review fixes.
- Strict preservation replay proves no product, generated, dirty, unrelated, or prior-goal path changed.

**Kill Criteria:**

- The composer is at most 50 physical lines, contains no `_wave` call and no inline level dictionary, imports all seven canonical leaf lists exactly once in canonical order, and defines `ADVENTURE_LEVELS` exactly once.
- Exactly the seven planned leaf modules plus a docstring-only package `__init__.py` exist. Every leaf is at most 700 lines, defines exactly one `LEVELS` list, imports only `..helpers._wave`, and has no leaf-to-leaf, composer, or reverse dependency.
- Each of the 17 expected level slugs exists exactly once in its declared leaf; no level or wave content, order, type, or value changes.
- The stable import/export, blueprint map key, 17-level/76-wave counts, public projections, seed-target check output, and generated target bytes remain unchanged.
- The original monolithic literal does not remain as a facade, fallback, duplicate, commented copy, or dead path.
- No other blueprint ledger, dirty curriculum path, generated artifact, backend/frontend runtime, migration, API contract, database schema, asset, dependency/lockfile, CI wiring, or prior-goal artifact changes.
- Strict dirty-worktree preservation passes and no file is staged, committed, discarded, or normalized outside the approved paths.

**Non-Goals:** Change no curriculum copy, command, solution, objective, wave, evaluation, difficulty, identifier, or sequence. Do not redesign the generator, public catalogs, seeding, database, API, or frontend. Do not split another adventure ledger, modify the dirty V3/Frost/Skyline curriculum work, remove the unused `source/ch1/` scaffold, or edit `ARCHITECTURE.md` or the architecture-boundary guard in this slice.

## Architecture Map

```text
source/blueprint/__init__.py                         (preserved)
  └─ adventure_repository_foundations.py             (stable public composer)
       ├─ repository_foundations/fresh_starts.py      (levels 0–4)
       ├─ repository_foundations/history_and_status.py (levels 5–8)
       ├─ repository_foundations/cloning.py           (levels 9–11)
       ├─ repository_foundations/configuration.py     (levels 12–13)
       ├─ repository_foundations/founding_workflows.py (level 14)
       ├─ repository_foundations/fresh_start_drills.py (level 15)
       └─ repository_foundations/inspection_drills.py  (level 16)
              └─ ../helpers.py::_wave                 (preserved)

scripts/checks/check_curriculum_source_layout.py
  └─ static Repository Foundations layout validation

scripts/checks/check_quality_gates.py
  ├─ dedicated source-layout command
  └─ unchanged authored/generated target command
```

No leaf may import another leaf, the composer, the blueprint package initializer, generated data, or a public wrapper. The composer may import only the seven leaf `LEVELS` values. Existing consumers continue to import only the composer through the current path.

### Files to create

- `backend/curriculum/seed_data/source/blueprint/repository_foundations/__init__.py`
- The seven leaf modules named in the architecture map.
- `backend/curriculum/tests/test_repository_foundations_source_layout.py`
- `scripts/checks/check_curriculum_source_layout.py`
- `docs/goals/repository-foundations-ledger-decomposition/PRE_SLICE_BASELINE.json`
- `docs/goals/repository-foundations-ledger-decomposition/PRE_CUTOVER_CONTENT_MANIFEST.json`
- `docs/goals/repository-foundations-ledger-decomposition/verify_evidence.py`
- `docs/goals/repository-foundations-ledger-decomposition/EVIDENCE.md`

### Files to modify

- `backend/curriculum/seed_data/source/blueprint/adventure_repository_foundations.py`
- `scripts/checks/check_quality_gates.py` — add the dedicated check to `FAST_GATES` only.
- `backend/curriculum/seed_data/source/README.md`

### Files to preserve exactly

- `backend/curriculum/seed_data/source/blueprint/__init__.py`, `helpers.py`, and every other blueprint adventure ledger.
- `backend/curriculum/seed_data/blueprint_generated.py`, all public catalog and compatibility wrappers, management commands, and seed routing.
- `backend/curriculum/seed_data/generated/generated_targets.py` and every other generated artifact.
- `scripts/checks/check_seed_targets.py`, `scripts/checks/check_generated_targets_current.py`, CI wiring, dependency manifests, and lockfiles.
- The dirty `backend/curriculum/tests/test_seed_data_source_layout.py`, dirty V3/Frost/Skyline authored curriculum files, all backend/frontend runtime files, and every unrelated dirty/untracked path.
- `ARCHITECTURE.md`, the architecture-boundary guard, the unused `source/ch1/` scaffold, and every prior goal artifact.

### Precise mutable-path allowlist after baseline capture

- Existing implementation/docs paths: `backend/curriculum/seed_data/source/blueprint/adventure_repository_foundations.py`, `scripts/checks/check_quality_gates.py`, and `backend/curriculum/seed_data/source/README.md`.
- Approved absent-to-created implementation/test paths: `backend/curriculum/seed_data/source/blueprint/repository_foundations/`, `scripts/checks/check_curriculum_source_layout.py`, and `backend/curriculum/tests/test_repository_foundations_source_layout.py`.
- Approved slice artifacts: `docs/goals/repository-foundations-ledger-decomposition/GOAL.md`, `PLAN.md`, `PRE_SLICE_BASELINE.json`, `PRE_CUTOVER_CONTENT_MANIFEST.json`, `verify_evidence.py`, and `EVIDENCE.md`.
- After capture, `GOAL.md`, `PLAN.md`, both pre-cutover manifests, and their recorded metadata become immutable preservation entries. Only `verify_evidence.py` and `EVIDENCE.md` remain eligible for attributable evidence fixes.

## Task Board

### Task 1: Capture preservation, source, behavior, and command baselines

- **Owner:** Main agent.
- **Files allowed:** The two new pre-cutover JSON artifacts and new goal-local `verify_evidence.py` only.
- **Output:** Complete visible-worktree preservation manifest; exact mutable preimages/absences; original source/module hashes and counts; per-level AST and source-segment fingerprints; imported data/order/public-projection fingerprints; generated-target hash; current seed-target command output; relevant pre-cutover test results; and the baseline-capable verifier that replays them.
- **Verification:** From repository root, run `python docs/goals/repository-foundations-ledger-decomposition/verify_evidence.py --phase baseline`; expect exit 0 and a complete replay record. Before the verifier exists, the baseline capture command recorded in `PRE_SLICE_BASELINE.json` must itself replay with exit 0.
- **Acceptance evidence:** Both manifests contain full command/cwd/exit/output metadata and replay every repository/preimage hash they record; every planned new implementation/test path is recorded absent. The verifier records each finalized manifest file SHA-256 in `EVIDENCE.md` after capture, avoiding any impossible self-hash or circular cross-hash field.
- **Parallel safety:** Sequential; cannot run in parallel with Tasks 2–4 because it establishes their immutable preimages and dirty-worktree boundary.
- **Depends on:** PRE approval.

### Task 2: Move literal ownership into seven concept ledgers

- **Owner:** Main agent.
- **Files allowed:** The original composer path and new `repository_foundations/` package only.
- **Output:** Every captured level source block exists once in its declared leaf with only the required helper-import depth adjustment; the stable composer exposes their exact flattened order.
- **Verification:** From repository root, run `python docs/goals/repository-foundations-ledger-decomposition/verify_evidence.py --phase content`; expect exit 0 with exact content, order, import-boundary, and no-duplicate assertions. The dedicated layout command is created and run in Task 3.
- **Acceptance evidence:** Per-level AST/source fingerprints, canonical JSON hash, 17/76 counts, ordered slugs/waves, stable import/map projections, module sizes, and definition/import census all replay.
- **Parallel safety:** Sequential; depends on Task 1 and shares the composer/package truth with Tasks 3–4.
- **Depends on:** Task 1.

### Task 3: Make the cutover topology durable

- **Owner:** Main agent.
- **Files allowed:** New `scripts/checks/check_curriculum_source_layout.py`, `scripts/checks/check_quality_gates.py`, and the new focused test only.
- **Output:** A pure path-injectable static validator enforces the exact package, leaf ownership, dependency direction, composer order, slug allocation, and size limits; the existing command incorporates its errors without changing clean-run output.
- **Verification:** From repository root, run `python -m pytest -q backend/curriculum/tests/test_repository_foundations_source_layout.py`; expect exit 0. Run `python scripts/checks/check_curriculum_source_layout.py`; expect exit 0 and its exact success line. Run `python scripts/checks/check_seed_targets.py`; expect exit 0 and the unchanged `Generated curriculum targets are consistent (2056 cases).` line.
- **Acceptance evidence:** Live validator result plus independent synthetic failures for missing/unexpected modules, inline composer content, wrong/repeated slugs, reordering, leaf/reverse dependencies, and oversized files; `FAST_GATES` contains the dedicated command exactly once.
- **Parallel safety:** Sequential; depends on the settled Task 2 topology and modifies the gate consumed by Task 4.
- **Depends on:** Task 2.

### Task 4: Correct authored-source documentation and prove product equivalence

- **Owner:** Main agent.
- **Files allowed:** `source/README.md`, `verify_evidence.py`, and `EVIDENCE.md`.
- **Output:** The README states the current source/generated ownership model; the verifier and evidence reproduce all content, topology, command, regression, and preservation claims.
- **Verification:** Run every command in the command/evidence matrix below from repository root; each must exit 0. The verifier must replay stable/public catalog projections, generated bytes, topology, and preservation after the commands settle.
- **Acceptance evidence:** `EVIDENCE.md` records command, cwd, exact exit, stdout/stderr digest, and result for every row plus the final manifest replay.
- **Parallel safety:** Sequential; consumes the completed cutover and guard and writes their final evidence.
- **Depends on:** Tasks 2–3.

### Task 5: Close independent review gates

- **Owner:** Main agent, with independent reviewers and verifier.
- **Files allowed:** Attributable implementation/evidence fixes within the allowlist only.
- **Output:** PRE/POST alignment, correctness, maintainability, and final-verification decisions with all actionable findings resolved and evidence metadata synchronized.
- **Verification:** From repository root, run `python docs/goals/repository-foundations-ledger-decomposition/verify_evidence.py`; expect exit 0 after every fix and immediately before final verification. Re-run any matrix row affected by a fix.
- **Acceptance evidence:** Final reviewer decisions name the settled tree; canonical verifier output and manifest metadata match it.
- **Parallel safety:** Review roles may inspect independently only after Task 4; fixes and final verification remain sequential.
- **Depends on:** Tasks 1–4.

## Command and Evidence Matrix

All commands run from `C:\Users\Joana\Documents\GIT-IT` with expected exit code 0. The evidence record captures command, working directory, exit code, stdout, and stderr (or their lossless encoded bytes plus SHA-256).

| Gate | Exact command | Acceptance evidence |
|---|---|---|
| Canonical slice verifier | `python docs/goals/repository-foundations-ledger-decomposition/verify_evidence.py` | All content, topology, command-result, generated-file, and preservation assertions pass. |
| Focused topology mutations | `python -m pytest -q backend/curriculum/tests/test_repository_foundations_source_layout.py` | Focused file passes; every declared controlled mutation is exercised. |
| Relevant curriculum behavior | `python -m pytest -q backend/curriculum/tests/test_blueprint_pedagogy_invariants.py backend/curriculum/tests/test_chapter_content_invariants.py backend/curriculum/tests/test_objective_soundness.py backend/curriculum/tests/test_seed_source_command_routing.py backend/curriculum/tests/test_arcane_curriculum_preservation.py backend/curriculum/tests/test_level_brief_required_details.py backend/curriculum/tests/test_advanced_pedagogy_invariants.py` | All selected behavior, pedagogy, preservation, brief, and routing tests pass. |
| Complete curriculum regression | `python -m pytest -q backend/curriculum/tests` | Full suite passes; any unrelated baseline failure must be reproduced pre-cutover and reported, never edited around. |
| Dedicated layout CLI | `python scripts/checks/check_curriculum_source_layout.py` | Exit 0; stdout exactly `Curriculum source layout is consistent.` plus newline; stderr empty. |
| Existing target structure | `python scripts/checks/check_seed_targets.py` | Exit 0; stdout remains `Generated curriculum targets are consistent (2056 cases).` plus newline; stderr empty. |
| Generated-target replay | `python scripts/checks/check_generated_targets_current.py` | Exit 0 and committed targets reported current; generated file bytes remain unchanged. |
| Fast aggregate | `python scripts/checks/check_quality_gates.py` | Exit 0; dedicated layout gate appears once and aggregate success is reported. |
| Diff hygiene | `git diff --check` | Exit 0 with no output. |

Tasks 1–4 are intentionally sequential. They share an immutable baseline, a single ownership cutover, gate registration, and final evidence state, so no implementation task has a disjoint write scope that is safe to execute in parallel. Read-only POST/correctness/maintainability reviewers may run concurrently only after Task 4; final verification follows any fixes.

## Forbidden Moves

- Do not edit or regenerate curriculum content, generated targets, public contracts, or unrelated source while splitting the ledger.
- Do not hand-copy and rewrite level dictionaries when exact source-block movement is possible.
- Do not add re-exports to `repository_foundations/__init__.py`, compatibility aliases, fallback literals, dynamic discovery, registries, or multiple public assembly paths.
- Do not let a leaf own cross-group order or import another leaf/composer; do not let the composer call `_wave` or contain level literals.
- Do not weaken or edit the existing seed-target validation or alter its clean stdout, stderr, exit status, or invocation. Add the dedicated source-layout command to the fast-gate registry exactly once without reordering existing gates.
- Do not modify dirty curriculum files or tests to make results pass. Record any unrelated baseline failure precisely instead.
- Do not stage, commit, discard, normalize, or otherwise alter unrelated dirty files or prior goal artifacts.

## Review Gates

1. PRE plan review before baseline capture or implementation.
2. POST alignment review after the cutover, durable guard, and evidence draft.
3. Independent correctness review focused on exact data/order/public/generated equivalence and validator behavior.
4. Independent maintainability review focused on concept boundaries, ownership, naming, dependency direction, discoverability, and absence of facades/duplication.
5. Independent final verifier after all findings, fixes, manifests, tests, and evidence metadata are synchronized.
