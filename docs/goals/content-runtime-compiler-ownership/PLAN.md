# Content Runtime Compiler Ownership Implementation Plan

**Intent:** Advance the codebase-wide maintainability goal by turning the live authoring runtime compiler from one multi-domain transaction object into a small atomic facade over explicit private persistence owners.
**Current Behavior:** `backend/authoring/compiler.py` is a 537-line, 21,635-byte class with seventeen methods. One object currently owns the transaction, signature cache, constrained runtime-pointer replacement, runtime chapter allocation, official slug policy, Adventure/Challenge/Lesson graph writes, command-form synthesis, variant normalization/persistence/retirement, and semantic identity. It writes across roughly eleven runtime model types and calls the repository simulator. Only `ContentRuntimeCompiler().compile(content=...)` is consumed outside the module; no private method is called externally.
**Expected Outcome:** `compiler.py` becomes a reviewable public transaction facade. A private `_runtime_compilation/` package gives chapter policy, Adventure projection, Challenge projection, Lesson projection, command forms, variants, and identity one owner each. The compiler import and compile result stay unchanged, all target writes remain inside one atomic transaction, and no caller, model, migration, schema, API, or frontend contract changes.
**Target-Perspective Output:** An authoring maintainer can open `compiler.py` to understand caching, transaction, dispatch, and pointer lifecycle; then open exactly one private module for the content graph being changed. They can run the architecture guard plus the runtime-compiler contract suite and see that public imports, database graph projections, no-op recompilation, replacement, and rollback are intact.
**Truth Owner:** `compiler.py` alone owns public orchestration and the atomic boundary. `chapters.py` owns runtime chapter allocation and official slug conflicts; `adventures.py`, `challenges.py`, and `lessons.py` own their target graphs; `forms.py` owns synthesized/reused command forms; `variants.py` owns normalized variant persistence and retirement; `identity.py` owns definition/semantic hashes.
**Contract Boundary:** Preserve `from authoring.compiler import ContentRuntimeCompiler`, constructor `ContentRuntimeCompiler()`, keyword-only `compile(*, content) -> PublishedContentRuntime`, exact signature caching, model graph values/order, error type/message, one-target runtime constraint, transaction rollback, publish/test-run service behavior, and all database/API/frontend contracts.
**Cutover:** First add characterization and topology mutation tests against the current monolith. Then create every private owner, redirect the unchanged facade to them, delete the displaced detail methods from the facade, and run the same characterization suite. There is no caller migration or compatibility window.
**Displaced Path:** The detail implementations in `ContentRuntimeCompiler` are removed. No second compiler class, compatibility methods, public re-export from `_runtime_compilation`, external deep import, leaf transaction, or duplicate model writer may remain.
**Value Density:** This reduces a live transactional blast radius rather than splitting another static ledger. It creates independently reviewable owners behind a one-method public boundary, avoids the already-dirty production caller, and directly protects rollback after destructive pointer/target replacement.
**Acceptance Evidence:** Frozen current-worktree fingerprints; the existing 26-test compiler-consumer baseline; canonical ID-independent graph assertions for representative Adventure, nested Challenge, and Lesson definitions; unchanged-recompile identity/count proof; changed-recompile one-pointer/one-target proof; a deliberately failing rebuild after pointer deletion proving rollback preserves the prior runtime graph; real authoring publish/test-run API coverage; topology mutations; focused and architecture tests; Ruff/format; Django check; migration drift; API/generated diff checks; fast quality gates; and complete outside-allowlist worktree preservation.
**Evidence Lane:** Dirty-worktree/compiler baseline -> characterization tests pass on the monolith -> topology guard mutation corpus -> private owners -> facade cutover and displaced-method deletion -> characterization replay -> protected/outside-manifest verifier -> focused services/model tests -> architecture/Ruff/Django/migration/API/quality gates -> independent reviews.
**Kill Criteria:** `compiler.py` at most 100 lines with exactly the public class, constructor, and atomic `compile`; exact eight-file private package; private initializer docstring-only; chapter/forms/identity functions and `VariantWriter` each have one owner; one target writer per content kind; no concrete Adventure/Challenge/Lesson graph writes in the facade; no `transaction.atomic` below the facade; no external imports from `_runtime_compilation`; no duplicate public compiler; no displaced facade methods; exact graph/identity/rollback characterization; protected files and all 402 initially dirty outside-allowlist paths unchanged; no migration, model, schema, caller, API, frontend, generated artifact, or unrelated asset edit.
**Architecture Slice:** `backend/authoring/compiler.py`, a new private runtime-compilation package, dedicated compiler characterization tests, one architecture-policy module/test, the minimal central guard registration, and this evidence package.
**Plan Review Gate:** Requires PRE review before execution.

`PRE_SLICE_BASELINE.json` and `PROTECTED_BASELINE.json` become immutable execution inputs immediately after PRE approval. Execution and review may read them but must not modify or regenerate them.

## Architecture map

### Files to create

- `backend/authoring/_runtime_compilation/__init__.py`
- `backend/authoring/_runtime_compilation/chapters.py`
- `backend/authoring/_runtime_compilation/adventures.py`
- `backend/authoring/_runtime_compilation/challenges.py`
- `backend/authoring/_runtime_compilation/lessons.py`
- `backend/authoring/_runtime_compilation/forms.py`
- `backend/authoring/_runtime_compilation/variants.py`
- `backend/authoring/_runtime_compilation/identity.py`
- `backend/authoring/tests/test_runtime_compiler_contract.py`
- `backend/common/tests/architecture_guard/test_authoring_compiler_policy.py`
- `scripts/checks/architecture_guard/contracts/authoring_compiler.py`
- `docs/goals/content-runtime-compiler-ownership/EVIDENCE.md`
- `docs/goals/content-runtime-compiler-ownership/PRE_SLICE_BASELINE.json`
- `docs/goals/content-runtime-compiler-ownership/PROTECTED_BASELINE.json`
- `docs/goals/content-runtime-compiler-ownership/verify_evidence.py`

### Files to modify

- `backend/authoring/compiler.py`
- `scripts/checks/check_architecture_boundaries.py` (minimal import and main-list registration only; its pre-existing dirty content is protected by normalization against the frozen pre-state)

### Files to avoid

- The dirty production caller `backend/authoring/services/core.py` and dirty API test `backend/authoring/tests/test_authoring_api.py`.
- Existing compiler consumers/tests, authoring schemas/models/validators, Adventure/Challenge/Curriculum/Simulator models and services, migrations, settings, URLs, serializers, OpenAPI, generated API types, frontend code/assets, databases, generated curriculum, and every unrelated dirty path.

### Source of truth and paths

- Source truth: `ContentDefinition` plus `ContentKind`; definitions are read through `authoring.schemas`.
- Read path: `ContentDefinition` -> schema accessors -> chapter/form lookup and simulator normalization -> private target owner.
- Write path: runtime `Chapter` -> optional `CommandSkill`/`CommandForm` -> exactly one Adventure, Challenge, or Lesson graph -> variants -> final `PublishedContentRuntime` pointer.
- Contract boundary: the unchanged public compiler class/import and one atomic compile call.
- Integration points: `ContentDefinitionService.publish/test_run`, model constraints, curriculum idempotency, official chapter writes, repository-state normalization, architecture CI guard.
- Migration/cutover: in-place facade redirection; no schema/data migration, caller change, shim, or dual route.
- Displaced path: all private detail methods currently living on `ContentRuntimeCompiler`.
- Acceptance gate: identical current-state database projections and rollback behavior plus topology/worktree proof.

## Canonical owners and caps

| File | Owns | Maximum lines |
| --- | --- | ---: |
| `compiler.py` | public class, cache check, atomic dispatch, pointer lifecycle | 100 |
| `_runtime_compilation/__init__.py` | private-package docstring only | 5 |
| `chapters.py` | chapter allocation and official slug policy | 145 |
| `adventures.py` | Adventure level/wave graph projection | 125 |
| `challenges.py` | Challenge level/trial graph projection | 160 |
| `lessons.py` | Lesson projection | 50 |
| `forms.py` | command-skill/form synthesis and form resolution | 100 |
| `variants.py` | normalized variant upsert/retirement and parent keys | 180 |
| `identity.py` | definition signature and semantic key | 50 |

Exact top-level behavior owners are `runtime_chapter` and `assert_official_runtime_slugs_available`; `compile_adventure`; `compile_challenge`; `compile_lesson`; `command_form_for_content` and `resolve_level_forms`; `VariantWriter`; and `definition_signature` plus `semantic_key`. Imported names are not ownership.

## Task 1: Characterize the transaction and add the topology policy

**Exact scope:** Add a new database contract suite that exercises Adventure, nested Challenge, and Lesson projections; canonicalizes database rows without primary keys/timestamps; covers unchanged and changed recompilation; and forces an invalid integer conversion after pointer deletion/partial target writes to prove rollback. Run it against the current monolith and record the result before moving code. Add a pure authoring-compiler policy under the existing architecture guard with temp-tree mutations for manifest/caps, duplicate compiler truth, restored facade methods, missing/duplicate owners, wrong model-import owner, leaf transactions, public package exports, and external deep imports. Register that policy with only the exact import and main-list call in the central guard.
**Expected output:** Current behavior and the destination topology both fail loudly before the move can hide a regression.
**Verification:** From repository root, run the two new test files; run `python scripts/check_architecture_boundaries.py`.
**Acceptance evidence:** Pre-cutover characterization pass, mutation diagnostic table, and normalized proof that the central guard differs from its frozen pre-state only by the planned registration.
**Parallel:** No. This establishes the execution contract.

## Task 2: Extract private runtime-compilation owners

**Exact scope:** Move each existing detail body to its canonical private owner with only dependency-passing changes required by extraction. `VariantWriter` owns one simulator instance. Target owners use the forms functions and a passed writer. Preserve query filters, defaults, ordering, slug generation, integer conversion, fallback behavior, error messages, hash serialization, and model write order.
**Expected output:** Every persistence concern has one bounded source file and no leaf owns the transaction.
**Verification:** Characterization and existing direct compiler tests; Ruff; topology policy.
**Acceptance evidence:** Before/after method-to-owner map, exact final line counts, and no duplicate implementation search.
**Parallel:** No. The target modules share one cutover and one database graph.

## Task 3: Cut the facade over and remove displaced methods

**Exact scope:** Keep `ContentRuntimeCompiler` in `compiler.py`, preserve its zero-argument constructor and atomic keyword-only `compile`, instantiate the private variant writer, call private owners, and retain constrained runtime-pointer deletion before target replacement. Remove every displaced detail method and its now-private imports from the facade. Do not edit callers or add compatibility aliases.
**Expected output:** The public compiler explains the transaction in under 100 lines while detail writes live only in their owner modules.
**Verification:** Public import/signature smoke; topology policy; unchanged caller fingerprints; contract and focused suites.
**Acceptance evidence:** AST owner map, exact facade source shape, and unchanged caller/service behavior.
**Parallel:** No. It is the atomic cutover.

## Task 4: Prove graph identity, rollback, and repository fitness

**Exact scope:** Create a persistent verifier that pins both frozen baseline files, compares protected fingerprints and the decompressed 402-entry outside manifest, checks planned-file status/staging, normalizes the central guard registration against its pre-hash, invokes the topology policy, and reports one deterministic success line. Run the characterization suite; every existing compiler consumer suite; authoring service/API paths; architecture guard; Ruff/format; Django check; migration drift; API/generated diffs; fast gates; and final diff/staging checks.
**Expected output:** Cleaner ownership with identical authoring runtime behavior and no collateral worktree change.
**Verification:** `python docs/goals/content-runtime-compiler-ownership/verify_evidence.py`; `python -m pytest backend/authoring/tests/test_runtime_compiler_contract.py backend/authoring/tests/test_compiler_direct_runtime.py backend/authoring/tests/test_chapter_settings.py backend/authoring/tests/test_authoring_api.py backend/common/tests/test_model_integrity_constraints.py backend/common/tests/architecture_guard/test_authoring_compiler_policy.py backend/curriculum/tests/test_seed_curriculum_idempotency.py -q`; `python -m ruff check backend/authoring/compiler.py backend/authoring/_runtime_compilation backend/authoring/tests/test_runtime_compiler_contract.py backend/common/tests/architecture_guard/test_authoring_compiler_policy.py scripts/checks/architecture_guard/contracts/authoring_compiler.py scripts/checks/check_architecture_boundaries.py docs/goals/content-runtime-compiler-ownership/verify_evidence.py`; `python -m ruff format --check` over the same Python scope; `python scripts/check_architecture_boundaries.py`; from `backend`, `python manage.py check` and `python manage.py makemigrations --check --dry-run`; from root, `python scripts/check_api_contract.py`, `python scripts/check_quality_gates.py`, `git diff --check`, protected/generated diffs, and staged-path inspection.
**Acceptance evidence:** Every baseline/projection/rollback gate recorded in `EVIDENCE.md`; no planned path staged.
**Parallel:** No. This is the terminal integration proof.

## Non-goals

- Changing authoring definitions, validation, permissions, publishing policy, response payloads, or UI.
- Optimizing queries, changing model constraints, adding dependency injection, or redesigning the compile API.
- Rewriting schema accessors, simulator normalization, slug behavior, hashes, or authored content.
- Splitting unrelated large ledgers, metrics services, tests, or frontend components in this slice.

## Risk if wrong

The compiler deletes a constrained pointer and existing target rows before rebuilding. A misplaced transaction, changed write order, slug drift, variant retirement bug, or hash drift can orphan content or make publish/test-run nondeterministic. Database graph characterization and forced post-deletion rollback are blocking evidence, not optional tests.
