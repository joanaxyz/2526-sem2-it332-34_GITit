# Legacy Adventure Plan Ownership Retirement — Slice 17 Implementation Plan

**Intent:** Remove runtime-inert and misleading curriculum plan owners so authors and maintainers see one canonical foundational source, one canonical advanced-drill source, and one fail-closed public composition path.

**Current Behavior:** `backend/curriculum/seed_data/adventures.py` defines 35 wave-plan literals, then silently overwrites 16 foundational values with `BLUEPRINT_ADVENTURE_LEVELS`. A second `ADVENTURE_LEVEL_PLAN["repository-foundations"]` fallback is unreachable for grouping but remains exported, documented, and iterated by the seed writer even though its 11 reuse usages add nothing to the canonical 159-form set. The unused `source/ch1/` package still claims monoliths drive seeding.

**Expected Outcome:** The 16 foundational plans come only from `BLUEPRINT_ADVENTURE_LEVELS`; an explicit 16-key public-order projection owns their unchanged published sequence while retaining every blueprint value by object identity; one private advanced-drill mapping owns the exact 19 active advanced plans; and a deterministic disjoint-merge helper rejects collisions before composing the unchanged 35-key `ADVENTURE_WAVE_PLANS`. `ADVENTURE_LEVEL_PLAN`, its exports/consumer loop, and the stale Chapter 1 scaffold disappear. Author guidance and source-package documentation point to current owners, and the fast curriculum source-layout gate prevents regression.

**Target-Perspective Output:** A curriculum author can identify the correct foundational or advanced plan owner directly from the authoring guide and code, without encountering a second current-looking plan. A reviewer sees the complete composition contract in one small block and can prove that a duplicate key raises instead of silently replacing data.

**Truth Owner:** `source/blueprint/` owns foundational adventure levels and waves; `_FOUNDATIONAL_ADVENTURE_ORDER` in `adventures.py` owns only the stable public order of those 16 blueprint keys; the private advanced-drill mapping owns only the 19 active Frost/Skyline drill groupings; the disjoint merge owns the stable public `ADVENTURE_WAVE_PLANS`; canonical non-blocked `ADVENTURE_LEVELS` plus `ENGINE_SUPPORTED_REFERENCE_FORMS` own the seed writer's supported form set.

**Contract Boundary:** `curriculum.seed_data.adventures.ADVENTURE_WAVE_PLANS` retains the exact 35 keys, insertion order, values, object identity for all 16 blueprint values, 95 levels, and 437 waves. `ADVENTURE_LEVELS`, `SPEC_BY_SLUG`, `ADVENTURE_SOURCES`, the 159 supported forms, seeded rows, and generated targets remain identical. Removing the unused internal `ADVENTURE_LEVEL_PLAN` import/export is an intentional contract retirement after proving no live consumer requires it.

**Cutover:** Capture the current resolved runtime, exact public key sequence, and the 19 active source literals. Mechanically move only those 19 source blocks into a narrowly named private mapping, delete all 16 shadowed literals and the post-construction overlay, project blueprint values through the frozen 16-key public order after exact-set validation, and compose foundational then advanced plans through a helper that checks intersections before every merge. Atomically remove the unreachable fallback constant, compatibility imports/exports, redundant writer loop, stale docs, and unused migration package.

**Displaced Path:** The 16 foundational literals in `adventures.py`, `ADVENTURE_WAVE_PLANS.update(BLUEPRINT_ADVENTURE_LEVELS)`, `ADVENTURE_LEVEL_PLAN`, all of its re-exports and consumer loop, and `source/ch1/` are deleted without aliases, empty compatibility objects, fallback lookups, or replacement scaffolds.

**Value Density:** Remove roughly 350 lines of dead/false ownership and five compatibility hops while adding one small fail-closed composition primitive and one focused durable policy corpus. The public runtime data remains exact.

**Acceptance Evidence:** Replay exact AST/source fingerprints for all 19 active advanced plan values, the exact 16-key foundational order, exact ordered/sorted runtime plan fingerprints, blueprint object identity, all public curriculum projections, the 159-form supported set, seeded-row behavior, and generated target bytes. Baseline/final AST censuses prove that no executable production Python imports, exports, binds, or accesses `ADVENTURE_LEVEL_PLAN`; explicit wrapper-surface assertions prove the three retained packages no longer publish it while their supported names remain. Controlled missing/extra/reorder, duplicate-owner, and stale-consumer mutations must fail. Retain lossless structured command results bound to both immutable manifests and the settled implementation.

**Evidence Lane:** CLI/data-flow lane: deterministic runtime artifacts, source-segment manifests, management-command seed behavior, focused/full pytest, generated-target replay, dedicated layout CLI, fast gates, Ruff, active-path searches, diff hygiene, and strict whole-worktree preservation.

**Risk if Wrong:** A key-order or payload change can alter learner progression; removing the legacy reuse loop without proving redundancy can hide command forms; a non-fail-closed merge can recreate silent ownership drift; broad edits can overwrite unrelated dirty curriculum work.

**Kill Criteria:** No executable production Python or authoring guide imports, exports, binds, accesses, or recommends `ADVENTURE_LEVEL_PLAN`; all three retained wrapper/package surfaces omit it; no `source/ch1/` source files remain; no foundational key is declared by the advanced owner; no mutation/dict-unpack/union path can silently overwrite plans; foundational missing/extra/reorder mutations and duplicate-owner fixtures fail deterministically; all runtime/data/form/generated fingerprints and strict preservation replay exactly.

**Architecture Slice:** Only the clean adventure-plan composition, legacy plan exports/consumer, source-package metadata/scaffold, authoring guide, existing curriculum source-layout checker, one new focused test, and goal-local evidence artifacts may change. Dirty V3/source tests, Slice 16 ledger content, generated artifacts, runtime product layers, and unrelated work remain immutable.

**Plan Review Gate:** Requires PRE review before execution.

## Architecture Map

```text
source/blueprint/ (16 foundational value owners, preserved)
        │
        └─ adventures.py::_FOUNDATIONAL_ADVENTURE_ORDER
                │  (16-key public-order owner + exact-set projection)
                ├─ adventures.py::_merge_disjoint_adventure_wave_plans(...)
                │       └─ public ADVENTURE_WAVE_PLANS (35 ordered keys, stable)
                │
adventures.py::_ADVANCED_DRILL_WAVE_PLANS (19 active owners)
        │
        └─ adventure_levels_for() → seed writer → persisted curriculum rows

canonical non-blocked ADVENTURE_LEVELS
        + ENGINE_SUPPORTED_REFERENCE_FORMS
        └─ seed writer supported_form_keys (159, stable)

check_curriculum_source_layout.py
        ├─ Repository Foundations leaf topology (existing)
        └─ adventure-plan ownership retirement policy (new)
```

### Source of truth

| Concern | Owner |
|---|---|
| Foundational level/wave literals | Existing `backend/curriculum/seed_data/source/blueprint/` ledgers |
| Published order of the 16 foundational keys | Exact `_FOUNDATIONAL_ADVENTURE_ORDER` tuple in `backend/curriculum/seed_data/adventures.py` |
| Advanced Frost/Skyline drill grouping literals | New private mapping in `backend/curriculum/seed_data/adventures.py` |
| Collision policy, cross-family order, public `ADVENTURE_WAVE_PLANS` | Disjoint helper and one composition assignment in `adventures.py` |
| Supported command-form publication | Canonical non-blocked `ADVENTURE_LEVELS` plus `ENGINE_SUPPORTED_REFERENCE_FORMS` in the seed writer |
| Ownership enforcement | `scripts/checks/check_curriculum_source_layout.py` |
| Author instructions | `CONTENT_AUTHORING_GUIDE.md` |

### Read path

Foundational/advanced canonical owners → fail-closed public wave-plan composition → `adventure_levels_for()` normalization → seed writer/structure → database rows. Authored adventure specs and engine capability references → supported form set → command-skill publication. Generated targets continue to read canonical adventure/challenge specs independently.

### Write path

An author edits exactly one foundational blueprint ledger or the advanced drill map, runs the source-layout/seed/target gates, and regenerates targets only if actual scenario/solution data changed. No author writes through a compatibility plan.

### Integration points

- `source/adventure_level_specs/level_plan.py::adventure_levels_for`
- `management/commands/seed_curriculum_writer.py`
- public and source `adventure_levels` wrappers
- curriculum source-layout fast gate
- content authoring guide

### Deterministic composition contracts

- `_FOUNDATIONAL_ADVENTURE_ORDER` is exactly: `repository-foundations`, `stage-with-intent`, `seal-the-snapshot`, `untrack-and-undo-edits`, `create-and-move`, `detach-and-clean`, `integrate-branches`, `resolve-conflicts`, `manage-the-merge`, `step-back-safely`, `reverse-and-recover`, `shelve-work`, `transplant-commits`, `connect-and-inspect`, `integrate-upstream`, `publish-work`.
- The foundational projection rejects any missing blueprint key, extra order key, or duplicate order key with `ValueError` and the exact deterministic message `Foundational adventure order mismatch: missing=<sorted-list>, extra=<sorted-list>, duplicates=<sorted-list>`; otherwise it inserts those keys in tuple order and returns the original blueprint values without copying them.
- `_merge_disjoint_adventure_wave_plans` checks the complete accumulated key set before each update. Any overlap raises `ValueError` with the exact message `Duplicate adventure wave plan owner(s): <sorted, comma-separated keys>`; no input is partially merged before that check.
- The policy analyzer freezes the exact order tuple above. A controlled tuple reorder must fail even though its set still matches the blueprint owner.

### Files to create

- `backend/curriculum/tests/test_adventure_plan_ownership.py`
- `docs/goals/legacy-adventure-plan-ownership-retirement/PRE_SLICE_BASELINE.json`
- `docs/goals/legacy-adventure-plan-ownership-retirement/PRE_CUTOVER_PLAN_MANIFEST.json`
- `docs/goals/legacy-adventure-plan-ownership-retirement/FINAL_COMMAND_RESULTS.json`
- `docs/goals/legacy-adventure-plan-ownership-retirement/verify_evidence.py`
- `docs/goals/legacy-adventure-plan-ownership-retirement/EVIDENCE.md`

### Files to modify

- `CONTENT_AUTHORING_GUIDE.md`
- `backend/curriculum/seed_data/adventures.py`
- `backend/curriculum/seed_data/adventure_levels.py`
- `backend/curriculum/seed_data/source/__init__.py`
- `backend/curriculum/seed_data/source/adventure_levels.py`
- `backend/curriculum/seed_data/source/adventure_level_specs/__init__.py`
- `backend/curriculum/seed_data/source/adventure_level_specs/level_plan.py`
- `backend/curriculum/management/commands/seed_curriculum_writer.py`
- `scripts/checks/check_curriculum_source_layout.py`

### Files to delete

- `backend/curriculum/seed_data/source/ch1/README.md`
- `backend/curriculum/seed_data/source/ch1/__init__.py`

### Files to preserve exactly

- Dirty `backend/curriculum/seed_data/source/README.md`, `ARCHITECTURE.md`, `backend/curriculum/tests/test_seed_data_source_layout.py`, dirty V3/Frost/Skyline ledgers, and dirty `scripts/checks/check_quality_gates.py` beyond its already-present source-layout registration.
- Slice 16 Repository Foundations composer/leaves, its focused test, and all prior goal/evidence artifacts.
- All generated target/OpenAPI/TypeScript files; curriculum scenario, challenge, lesson, solution, evaluation, and command-routing data; migrations; database schema; backend/frontend runtime product code; CI/dependency/lock files; and unrelated dirty/untracked paths.

### Precise mutable-path allowlist after baseline capture

- The nine existing files listed under “Files to modify.”
- The two tracked files listed under “Files to delete.”
- The new focused test listed under “Files to create.”
- The six goal-local artifacts listed under “Files to create.”
- After capture, `GOAL.md`, `PLAN.md`, `PRE_SLICE_BASELINE.json`, and `PRE_CUTOVER_PLAN_MANIFEST.json` become immutable. `verify_evidence.py`, `FINAL_COMMAND_RESULTS.json`, and `EVIDENCE.md` may receive attributable evidence/review fixes only.

## Task Board

### Task 1: Capture preservation and plan-behavior baselines

- **Owner:** Main agent.
- **Files allowed:** New baseline/content manifests and the baseline-capable verifier only.
- **Output:** Complete visible-worktree preservation map; exact mutable preimages/deletion targets/new absences; 19 active advanced source AST/segment fingerprints; 16 displaced-key census; exact public/foundational order; ordered/sorted 35-plan runtime fingerprints; blueprint identity; 663-spec/public/source fingerprints; 29-source fingerprint; 159-form supported-set fingerprint; generated-target hash; baseline AST import/export/binding/attribute census for `ADVENTURE_LEVEL_PLAN` across executable repository Python with the checker and focused policy test declared as the only excluded policy fixtures; direct command baselines.
- **Verification command:** From repository root, `python docs/goals/legacy-adventure-plan-ownership-retirement/verify_evidence.py --phase baseline`; expected exit 0.
- **Acceptance evidence:** Both manifests replay every recorded repository/runtime/source fingerprint; finalized manifest file hashes are pinned by the settled verifier/final result record without self-hashing.
- **Parallel safe:** No. This establishes immutable preimages and must complete before any cutover.
- **Depends on:** PRE approval.

### Task 2: Cut over public wave-plan composition

- **Owner:** Main agent.
- **Files allowed:** `backend/curriculum/seed_data/adventures.py` only.
- **Output:** Exact 19 active literals move to `_ADVANCED_DRILL_WAVE_PLANS`; the frozen `_FOUNDATIONAL_ADVENTURE_ORDER` projects the exact blueprint key set into the unchanged public sequence while preserving value identity; a small deterministic helper rejects duplicate owners before merge; `ADVENTURE_WAVE_PLANS` composes the ordered blueprint projection then advanced owners once; all 16 shadowed literals and the overlay update disappear.
- **Verification command:** From repository root, `python docs/goals/legacy-adventure-plan-ownership-retirement/verify_evidence.py --phase plans`; expected exit 0.
- **Acceptance evidence:** Source AST/segments for 19 values, exact foundational/public order, runtime 35-key data/counts, blueprint object identity, `ADVENTURE_SOURCES`, public projections, and generated-target hash replay exactly; direct missing/extra/duplicate-order fixtures raise the specified foundational mismatch message and a direct duplicate-owner fixture raises `ValueError("Duplicate adventure wave plan owner(s): <sorted, comma-separated keys>")`.
- **Parallel safe:** No. It consumes Task 1 preimages and establishes the owner required by later cleanup/guard tasks.
- **Depends on:** Task 1.

### Task 3: Retire the legacy grouping/export/scaffold contract

- **Owner:** Main agent.
- **Files allowed:** Modify exactly `CONTENT_AUTHORING_GUIDE.md`, `backend/curriculum/seed_data/adventure_levels.py`, `backend/curriculum/seed_data/source/__init__.py`, `backend/curriculum/seed_data/source/adventure_levels.py`, `backend/curriculum/seed_data/source/adventure_level_specs/__init__.py`, `backend/curriculum/seed_data/source/adventure_level_specs/level_plan.py`, and `backend/curriculum/management/commands/seed_curriculum_writer.py`; delete exactly `backend/curriculum/seed_data/source/ch1/README.md` and `backend/curriculum/seed_data/source/ch1/__init__.py`.
- **Output:** `ADVENTURE_LEVEL_PLAN` definition, fallback, imports, exports, writer loop, and author-guide claim are absent; the generic no-plan fallback remains; supported forms stay exact; `source/ch1/` is deleted; source/package docs name current truth.
- **Verification command:** From repository root, `python docs/goals/legacy-adventure-plan-ownership-retirement/verify_evidence.py --phase legacy`; expected exit 0.
- **Acceptance evidence:** Final AST census finds no production import, export, binding, or attribute access for the retired symbol outside the two declared policy fixtures; `curriculum.seed_data.adventure_levels`, `curriculum.seed_data.source.adventure_levels`, and `curriculum.seed_data.source.adventure_level_specs` have no `ADVENTURE_LEVEL_PLAN` attribute or `__all__` entry while still publishing `ADVENTURE_LEVELS`, `SPEC_BY_SLUG`, and `adventure_levels_for` as applicable; supported-set count/hash is exact, stable public curriculum fingerprints replay, deletion targets are absent, and docs identify canonical owners.
- **Parallel safe:** No. These files share one contract retirement and depend on the Task 2 runtime owner.
- **Depends on:** Task 2.

### Task 4: Make ownership retirement durable

- **Owner:** Main agent.
- **Files allowed:** `scripts/checks/check_curriculum_source_layout.py` and new `test_adventure_plan_ownership.py` only.
- **Output:** The existing fast checker aggregates the new plan-ownership policy without weakening Repository Foundations checks. Pure path-injectable analysis freezes the exact foundational tuple and rejects reordered/missing/extra/duplicate order keys, duplicate/extra/missing owners, silent merge patterns, restored legacy imports/exports/bindings/attributes/docs/scaffold, and nondeterministic collision messages. Its semantic census covers executable repository Python and explicitly excludes only the checker and focused test as self-referential policy fixtures.
- **Verification command:** From repository root, `python -m pytest -q backend/curriculum/tests/test_adventure_plan_ownership.py backend/curriculum/tests/test_repository_foundations_source_layout.py` followed by `python scripts/checks/check_curriculum_source_layout.py`; both expected exit 0 and the CLI retains exact success stdout.
- **Acceptance evidence:** Live policy is empty and every declared controlled mutation fails independently; existing 13 Repository Foundations topology cases remain green.
- **Parallel safe:** No. It verifies the settled Task 2–3 topology and shares the checker owner.
- **Depends on:** Tasks 2–3.

### Task 5: Close data-flow, preservation, and review evidence

- **Owner:** Main agent with independent POST/correctness/maintainability/final-verifier roles.
- **Files allowed:** Goal-local verifier, final command results, evidence, and attributable fixes inside the implementation allowlist only.
- **Output:** Lossless command records bound to both manifests and every settled implementation path; synchronized evidence and independent review decisions.
- **Verification command:** Run every row in the command/evidence matrix from repository root, then `python docs/goals/legacy-adventure-plan-ownership-retirement/verify_evidence.py`; all expected exit 0.
- **Acceptance evidence:** Target-person plan ownership, collision failure, data/form/seed/generated equivalence, regression outputs, review closure, strict preservation, and zero staging are reproducible.
- **Parallel safe:** POST/correctness/maintainability inspection may run concurrently only after implementation/evidence settle; fixes and final verification are sequential.
- **Depends on:** Tasks 1–4.

## Command and Evidence Matrix

All commands run from `C:\Users\Joana\Documents\GIT-IT`. `FINAL_COMMAND_RESULTS.json` retains exact command, cwd, exit, stdout/stderr bytes/digests, manifest hashes, and settled implementation fingerprints.

| Gate | Exact command | Expected evidence |
|---|---|---|
| Canonical verifier | `python docs/goals/legacy-adventure-plan-ownership-retirement/verify_evidence.py` | Exit 0; every plan/data/form/command/preservation assertion passes. |
| Focused ownership/topology | `python -m pytest -q backend/curriculum/tests/test_adventure_plan_ownership.py backend/curriculum/tests/test_repository_foundations_source_layout.py` | All live and controlled mutation cases pass. |
| Focused seed/data flow | `python -m pytest -q backend/curriculum/tests/test_seed_source_command_routing.py backend/curriculum/tests/test_blueprint_pedagogy_invariants.py backend/curriculum/tests/test_chapter_content_invariants.py backend/curriculum/tests/test_seed_curriculum_idempotency.py` | Routing, pedagogy, persisted rows, idempotency, and admin-owned preservation pass. |
| Complete curriculum regression | `python -m pytest -q backend/curriculum/tests` | Full suite passes with no unrelated edit-around. |
| Dedicated layout CLI | `python scripts/checks/check_curriculum_source_layout.py` | Exit 0; stdout exactly `Curriculum source layout is consistent.` plus platform newline; stderr empty. |
| Existing target structure | `python scripts/checks/check_seed_targets.py` | Exit 0; unchanged 2,056-case success output. |
| Generated-target currency | `python scripts/checks/check_generated_targets_current.py` | Exit 0; 2,056 variants and generated targets current. |
| Fast aggregate | `python scripts/checks/check_quality_gates.py` | Exit 0; source-layout checker runs once and all fast gates pass. |
| Semantic legacy census | `python docs/goals/legacy-adventure-plan-ownership-retirement/verify_evidence.py --phase legacy` | Exit 0; AST import/export/binding/attribute census is empty across executable repository Python outside the declared checker/test policy fixtures, all three wrapper surfaces omit the retired symbol, and supported exports remain. |
| Supporting text census | `rg -n "ADVENTURE_LEVEL_PLAN|monolithic files still drive seeding" CONTENT_AUTHORING_GUIDE.md backend/curriculum --glob "*.py" --glob "*.md" --glob "!**/test_adventure_plan_ownership.py"` | Exit 1 with no matches. The authoritative semantic census is above; goal/evidence/checker policy text is intentionally outside this search. |
| Ruff | `python -m ruff check backend/curriculum/seed_data/adventures.py backend/curriculum/seed_data/adventure_levels.py backend/curriculum/seed_data/source/__init__.py backend/curriculum/seed_data/source/adventure_levels.py backend/curriculum/seed_data/source/adventure_level_specs/__init__.py backend/curriculum/seed_data/source/adventure_level_specs/level_plan.py backend/curriculum/management/commands/seed_curriculum_writer.py scripts/checks/check_curriculum_source_layout.py backend/curriculum/tests/test_adventure_plan_ownership.py` | Exit 0; all planned Python files pass. |
| Diff hygiene | `git diff --check` | Exit 0; only manifest-attributable pre-existing line-ending warnings may remain. |

Tasks 1–4 are intentionally sequential because they share immutable preimages, one runtime composition owner, one compatibility-contract retirement, and one durable checker. No implementation task has a disjoint write scope safe for parallel execution.

## Forbidden Moves

- Do not remove only one of the 16 shadowed blueprint keys or keep a partial legacy fallback.
- Do not replace `update()` with dict unpacking or union that still silently overwrites collisions.
- Do not retain `ADVENTURE_LEVEL_PLAN` as an empty/deprecated alias, re-export, import shim, documentation term, or test-only current path.
- Do not move or rewrite the 19 active advanced plan values; preserve their normalized AST and source segments exactly except unavoidable outer-container indentation/name changes declared by the manifest normalization.
- Do not change foundational blueprint ledgers, scenario specs, solutions, evaluation, ordering, command routing, generated targets, database models/migrations, public API/frontend, dirty V3 work, or prior goal artifacts.
- Do not modify dirty `source/README.md`, `test_seed_data_source_layout.py`, `check_quality_gates.py`, or `ARCHITECTURE.md` to make checks pass.
- Do not stage, commit, discard, normalize, or otherwise alter unrelated dirty/untracked paths.

## Review Gates

1. PRE plan review before baseline capture or implementation.
2. POST alignment review after cutover, contract retirement, guard, and evidence draft.
3. Independent correctness/data-integrity review focused on plan ordering/payload, supported forms, seeded rows, public/generated projections, and evidence trust.
4. Independent maintainability review focused on truth ownership, fail-closed composition, compatibility removal, docs, guard cohesion, and absence of new facades.
5. Independent final target-perspective verifier after all findings, fixes, manifests, command records, and evidence metadata are synchronized.
