# Plan: Story and Chapter Catalog Contract Ownership

**Status:** PRE approved; execute sequentially

## Intent and Ownership

**Problem:** The real `/api/stories/` and `/api/chapters/` payloads are assembled by Curriculum serializers, but their nested method fields are documented as open JSON objects. Model defaults also make stable response fields appear optional. The frontend compensates with handwritten `Story` and `LearningChapter` object types and custom response generics. The runtime payload, OpenAPI, generated TypeScript, and consumer types therefore have multiple owners and disagree about required fields.

**Expected outcome:** `curriculum/serializers.py` becomes the complete response-contract owner for the two catalog endpoints. Named nested serializers describe prerequisite stories, chapter story references, completion metrics, and chest rewards. Generated OpenAPI and TypeScript expose every stable field as required and every nested value as typed. `features/story-map/types.ts` keeps only generated aliases for `Story` and `LearningChapter`, while its unrelated overview/runtime DTOs remain unchanged. `storyMapApi.listStories()` and `listChapters()` return their generated operation response directly. Runtime values, routes, locking behavior, ordering, and UI behavior remain unchanged.

**Target-perspective output:** A consumer can call `stories_list` or `chapters_list`, inspect the generated response type, and receive the same exact keys and values from the real endpoints without handwritten refinement or response casting.

**Truth owner:** `StorySerializer` and `ChapterListSerializer` remain the executable and documented top-level contract owners in `backend/curriculum/serializers.py`. Named serializers in that module own their nested response shapes. The committed OpenAPI and `apiTypes.ts` are generated projections. `frontend/src/features/story-map/types.ts` may export aliases derived from `ApiSchemas` but may not restate either catalog shape.

**Contract boundary:**

- `GET /api/stories/` returns an array of exact Story rows.
- `GET /api/chapters/` returns an array of exact ChapterList rows, optionally filtered by the existing `story` query parameter.
- `Story.prerequisite_story` and `ChapterList.story` are nullable typed objects.
- `ChapterList.level_completion` is required, never optional, and contains exact numeric fields.
- `ChapterList.chest_schedule` is a required array of exact reward rows.

**Cutover:** Add named nested serializers and explicit response fields in the existing Curriculum serializer module, preserving its current serializer methods and calculations. Regenerate OpenAPI and TypeScript. Replace only the handwritten catalog DTOs with generated aliases and remove only the two catalog response overrides. Add focused ownership checks and synthetic bypass tests. Do not add compatibility aliases or adapters.

**Displaced path:** Remove the open-object schemas for `Story.prerequisite_story`, `ChapterList.story`, `ChapterList.level_completion`, and `ChapterList.chest_schedule`; remove optionality drift for stable catalog fields; remove handwritten `Story`, `LearningChapter`, `ChapterLevelMetric`, and `ChestReward` response shapes; remove the custom `Story[]` and `LearningChapter[]` response generics. No alternate catalog DTO or normalization path may remain.

**Value density:** Very high. Two public read-only catalog endpoints gain exact nested contracts, Story Map and Shop consumers converge on generated types, and several schema lies disappear without changing business logic or persistence.

**Evidence lane:** Real DRF requests through `/api/stories/` and `/api/chapters/` against a small isolated database, including prerequisite and nullable cases; direct response validation; committed OpenAPI inspection; generated TypeScript inspection; focused Story Map/Shop and full frontend verification; preservation replay against the dirty worktree.

**Kill criteria:** One Curriculum-owned serializer family, one generated frontend projection, and no handwritten or overridden catalog response path. Both OpenAPI operations reference their canonical array item components. Required fields and nested schemas are exact. The runtime payload, selector calculations, routes, and visible consumer behavior do not change. Architecture checks make the cutover durable.

**Non-goals:** Chapter overview or chapter book contracts; adventure/challenge runtime responses; Shop catalog or purchase schemas; authentication contracts; selector/query rewrites; locking or completion arithmetic; model or migration changes; route changes; UI markup, copy, CSS, or design changes; cleanup of unrelated manual DTOs in `story-map/types.ts`.

**Risk if wrong:** Explicit serializer fields could accidentally alter runtime rendering, nested annotations could still generate open objects, required/nullable flags could drift, or removing response overrides could surface an unintended consumer assumption. Direct endpoint parity, exact schema assertions, TypeScript build/tests, and preservation hashes are required before closure.

## Current Architecture Map

| Concern | Current path | Required owner after cutover |
|---|---|---|
| Story values and lock state | `curriculum/serializers.py::StorySerializer` | unchanged, made explicit and exact |
| Chapter values and progress | `curriculum/serializers.py::ChapterListSerializer` | unchanged, made explicit and exact |
| Nested catalog response shapes | method return annotations/open objects | named Curriculum serializers |
| HTTP entrypoints | `curriculum/views.py::{StoryListAPIView,ChapterListAPIView}` | unchanged |
| Generated schema | committed `openapi.json` | generated from Curriculum serializers |
| Generated operation types | committed `apiTypes.ts` | generated from OpenAPI |
| Feature catalog types | handwritten objects in `story-map/types.ts` | exact `ApiSchemas` aliases |
| Runtime requests | custom response generics in `storyMapApi.ts` | generated operation responses directly |
| Consumers | Story Map pages/components/hooks and Shop story scope | unchanged |

## Exact Response Contract

| Object | Required fields | Constraints |
|---|---|---|
| Story | `id`, `slug`, `title`, `summary`, `price`, `sort_order`, `is_published`, `completed`, `owned`, `world_slug`, `difficulty`, `prerequisite_story`, `locked`, `lock_reason` | `difficulty` uses the existing enum; prerequisite is nullable |
| Story prerequisite | `slug`, `title`, `completed` | exact typed object |
| ChapterList | `id`, `slug`, `number`, `title`, `description`, `sort_order`, `is_playable`, `story`, `locked`, `lock_reason`, `command_skill_count`, `challenge_count`, `adventure_level_count`, `level_completion`, `chest_schedule` | story is nullable; all other fields required |
| Chapter story | `id`, `slug`, `title`, `world_slug` | exact typed object |
| Chapter completion | `value`, `numerator`, `denominator` | floating percentage plus integer counts |
| Chest reward | `threshold`, `coins` | integers |

## Files to Create

- `backend/curriculum/tests/test_catalog_contract_api.py`
- `docs/goals/story-chapter-catalog-contract-ownership/PRE_SLICE_BASELINE.md`
- `docs/goals/story-chapter-catalog-contract-ownership/EVIDENCE.md`

## Files to Modify

- `backend/curriculum/serializers.py`
- `frontend/src/shared/api/generated/openapi.json` — generated only
- `frontend/src/shared/api/generated/apiTypes.ts` — generated only
- `frontend/src/features/story-map/types.ts`
- `frontend/src/features/story-map/api/storyMapApi.ts`
- `scripts/checks/check_architecture_boundaries.py` — additive catalog ownership checks only
- `backend/common/tests/test_architecture_guard_algorithms.py` — additive guard tests only
- this goal package

## Files to Avoid

- `backend/curriculum/views.py`, selectors, services, models, migrations, and URLs
- chapter overview/book response implementation and frontend DTOs
- `frontend/src/shared/api/httpClient.ts` and API generator implementation
- Story Map/Shop production components, hooks, utilities, fixtures, styles, and copy
- `backend/common/openapi.py`
- authentication, Shop mutation, Progress, adventure, challenge, player, and admin contracts
- all prior goal packages and prior-slice implementation files outside the additive shared guard files

## Source, Read, Write, and Integration Paths

- **Source of truth:** current serializer methods and model/selector values in `curriculum/serializers.py`.
- **Read path:** public/authenticated GET -> existing Curriculum view -> existing selector/context maps -> Curriculum serializer -> JSON -> generated operation type -> React Query -> Story Map/Shop consumers.
- **Write path:** none; both endpoints and this slice are read-only.
- **Contract boundary:** named Curriculum serializers, OpenAPI components, and generated `stories_list`/`chapters_list` responses.
- **Integration points:** DRF Spectacular, repository API generator, `storyMapApi`, `useStories`, `StoryMapPage`, Story Map components, and `StoryShop`.
- **Migration/cutover:** direct contract replacement with stable runtime JSON; no compatibility period.
- **Acceptance gate:** real endpoint JSON, serializer/schema parity, generated-type adoption, consumer compilation/tests, durable guard, and dirty-worktree preservation.

## Task Board

### Task 1 — Freeze the Pre-Cutover Contract and Worktree

**Owner:** Main agent

**Allowed files:** `PRE_SLICE_BASELINE.md` only.

**Forbidden files:** all production, test, generated, shared guard, and prior-slice files.

**Scope:** After PRE approval, record the complete dirty manifest with hashes; target/protected hashes; guard line counts/numstats; real endpoint payloads for prerequisite and nullable cases; current open nested schemas and optional fields; current manual aliases and response overrides. Freeze all ordinary pre-existing manifest rows for byte-identical replay. Separately freeze the already-dirty generated OpenAPI/TypeScript files for generator-attributable catalog-only projection review, and the already-dirty architecture checker/test for additions-only review with their current deletion counts frozen.

**Output:** Reproducible semantic, manifest, protected-file, generated-projection, and additive-guard baseline.

**Verification:** Reparse the manifest, repeat the endpoint trace, and confirm no production file changed.

**Acceptance evidence:** Every pre-existing row has a hash and preservation mode; the four shared dirty targets have explicit catalog-only/additions-only review rules.

**Depends on:** PRE plan review.

**Parallel safe:** No.

### Task 2 — Establish Exact Curriculum-Owned Catalog Contracts

**Owner:** Main agent

**Allowed files:** `backend/curriculum/serializers.py`, `backend/curriculum/tests/test_catalog_contract_api.py`.

**Forbidden files:** Curriculum views, selectors, services, models, migrations, URLs, and every frontend/generated/shared-guard path.

**Scope:** Define named nested serializers and exact response fields while preserving every existing calculation and method result. Add real endpoint tests covering exact top-level/nested keys, enum/value types, nullable relations, required completion/chest data, query filtering, and serializer validation/parity.

**Output:** One exact Curriculum-owned Story/ChapterList serializer family with direct endpoint tests.

**Verification:** Focused catalog tests, existing curriculum story/access tests, Ruff, and temporary schema inspection.

**Acceptance evidence:** Real responses retain their pre-cutover values and expose only the documented exact keys/nested types.

**Depends on:** Task 1.

**Parallel safe:** No.

### Task 3 — Regenerate and Remove the Frontend Duplicate Contract

**Owner:** Main agent

**Allowed files:** generated OpenAPI/types, `frontend/src/features/story-map/types.ts`, `frontend/src/features/story-map/api/storyMapApi.ts`.

**Forbidden files:** generator implementation, HTTP client, overview/book DTO owners, Story Map/Shop production consumers, previews, styles, and all backend/shared-guard files.

**Scope:** Run the repository generator. Replace only `Story` and `LearningChapter` handwritten shapes with exact generated aliases. Delete their now-unused helper DTOs. Remove only the `stories_list` and `chapters_list` custom response generics. Keep overview/book DTOs and response overrides unchanged.

**Output:** Exact generated catalog projections and direct operation-response inference with no duplicate catalog DTO.

**Verification:** API-current/usage/type-adoption checks, focused Story Map/Shop tests, TypeScript/Vite build, and searches proving the displaced catalog path is gone.

**Acceptance evidence:** Generated component/operation types exactly match endpoint JSON and consumers compile without custom catalog responses.

**Depends on:** Task 2.

**Parallel safe:** No.

### Task 4 — Make Contract Ownership Durable

**Owner:** Main agent

**Allowed files:** `scripts/checks/check_architecture_boundaries.py`, `backend/common/tests/test_architecture_guard_algorithms.py`.

**Forbidden files:** every other file; existing checks/tests and their wording may not be removed or weakened.

**Scope:** Add a focused catalog check for exact backend serializer ownership/signatures, exact OpenAPI component fields/nesting/required/nullable flags and operation references, exact generated frontend aliases, direct generated operation returns, and absence of response intersections/adapters/secondary catalog DTOs. Add synthetic tests for meaningful bypasses. Preserve every earlier guard additively.

**Output:** CI-enforced one-way catalog contract ownership with synthetic bypass coverage.

**Verification:** Focused architecture algorithm tests, live checker, and shared-file preservation/numstat comparison.

**Acceptance evidence:** Synthetic bypasses fail, the live tree passes, prior guard deletions do not increase, and changes are additions-only except unavoidable surrounding-context diff lines.

**Depends on:** Task 3.

**Parallel safe:** No.

### Task 5 — Prove the Cutover and Close Reviews

**Owner:** Main agent

**Allowed files:** `EVIDENCE.md` and task files only for review-required corrections.

**Forbidden files:** unrelated files and preserved manifest rows; fixes outside the plan require a plan amendment and renewed review.

**Scope:** Capture post-cutover real endpoint traces, exact OpenAPI and TypeScript projections, no-duplicate-path searches, focused/full proportional backend and frontend gates, lint/build/API/architecture/documentation/diff gates, and preservation replay. Run POST plan, correctness, maintainability, and independent verifier reviews; fix material findings and rerun affected gates.

Preservation review must prove ordinary pre-slice manifest rows are byte-identical, generated-file deltas are generator-attributable only to the Story/Chapter catalog projection, and shared guard-file deltas are additions-only with frozen pre-slice deletion counts.

**Output:** `EVIDENCE.md` with authoritative runtime/schema/generated parity, gate output, review closure, and preservation proof.

**Verification:** Every acceptance claim links to rerunnable output. If direct endpoint evidence cannot be captured, report `implemented but unproven`.

**Acceptance evidence:** Direct catalog traces, exact committed/generated schemas, no displaced path, clean reviews, and zero unexplained drift from the pre-slice manifest.

**Depends on:** Tasks 1–4.

**Parallel safe:** No.

## Review and Stop Conditions

- Stop before implementation if PRE review finds ambiguous ownership, a dual-contract transition, incomplete endpoint evidence, or unsafe dirty-worktree overlap.
- Do not alter serializer values or selectors to satisfy a schema expectation.
- Do not add compatibility response keys, normalization adapters, new response casts, or duplicate DTOs.
- Do not hand-edit generated artifacts.
- Do not broaden the slice into chapter overview/book, Shop, auth, or gameplay contracts.
- Do not call the broad modernization goal complete after this bounded slice.
