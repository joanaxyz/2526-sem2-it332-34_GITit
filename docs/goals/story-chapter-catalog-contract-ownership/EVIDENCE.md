# Evidence: Story and Chapter Catalog Contract Ownership

## Outcome

Slice 8 establishes one exact, generated contract path for the Story and Chapter catalog endpoints without changing runtime values, routes, selectors, access rules, completion arithmetic, or consumers.

The final path is:

`Curriculum serializer methods -> named Curriculum response serializers -> existing views -> committed OpenAPI -> generated TypeScript operations -> derived Story Map aliases -> unchanged Story Map/Shop consumers`

The displaced path is gone:

- no open JSON object for the four catalog nested values;
- no optional stable Story/Chapter response fields;
- no handwritten `Story`, `LearningChapter`, `ChapterLevelMetric`, or `ChestReward` response shape;
- no custom response generic for `stories_list` or `chapters_list`;
- no compatibility adapter or second catalog contract owner.

## Exact Contract

### Story

Required keys:

```text
completed, difficulty, id, is_published, lock_reason, locked, owned,
prerequisite_story, price, slug, sort_order, summary, title, world_slug
```

`prerequisite_story` is nullable; when present it is exactly `{slug, title, completed}`. `difficulty` remains the existing `DifficultyEnum`.

### ChapterList

Required keys:

```text
adventure_level_count, challenge_count, chest_schedule, command_skill_count,
description, id, is_playable, level_completion, lock_reason, locked, number,
slug, sort_order, story, title
```

Nested shapes:

- `story`: nullable exact `{id, slug, title, world_slug}`;
- `level_completion`: exact `{value, numerator, denominator}`;
- `chest_schedule`: array of exact `{threshold, coins}` rows.

## Direct Runtime Evidence

A fresh migrated test database, authenticated `APIClient`, real routes, existing views/selectors, and the production serializers produced HTTP 200 for both endpoints.

`GET /api/stories/` proved:

- exact 14-key rows;
- `prerequisite_story: null` for the root story;
- typed prerequisite `{slug: "foundation", title: "Foundation", completed: false}` for the sequel;
- stable default/model fields remained present and values remained unchanged.

`GET /api/chapters/?story=summit` proved:

- exact 15-key row and existing query filtering;
- typed story `{id: 2, slug: "summit", title: "Summit", world_slug: "frostbound-citadel"}`;
- completion `{value: 0.0, numerator: 0, denominator: 0}`;
- chest schedule `[{25,25}, {50,60}, {75,100}, {100,150}]` by threshold/coins;
- existing lock state and count calculations remained on the real path.

Focused endpoint tests also compare route output with `StorySerializer`/`ChapterListSerializer` output and enforce exact key sets.
A direct response-serializer case covers the declared `ChapterList.story: null` branch, which cannot appear through the current published catalog selector because that selector intentionally requires `story__is_published=True`.

## Backend Ownership

`backend/curriculum/serializers.py` now owns six response serializers:

- `StoryPrerequisiteSerializer`
- `StorySerializer`
- `ChapterStorySerializer`
- `ChapterLevelCompletionSerializer`
- `ChapterChestRewardSerializer`
- `ChapterListSerializer`

The two top-level serializers are explicitly response-only. Their existing `get_*` methods remain the value owners. `extend_schema_field` binds each method-returned nested value to its named serializer; no view, selector, service, model, migration, or route changed.

## Generated Projection

The repository generator produced these exact TypeScript projections:

```ts
"Story": {
  "completed": boolean;
  "difficulty": ApiSchemas["DifficultyEnum"];
  "id": number;
  "is_published": boolean;
  "lock_reason": string;
  "locked": boolean;
  "owned": boolean;
  "prerequisite_story": ApiSchemas["StoryPrerequisite"] | null;
  "price": number;
  "slug": string;
  "sort_order": number;
  "summary": string;
  "title": string;
  "world_slug": string;
}
"StoryPrerequisite": { "completed": boolean; "slug": string; "title": string }
"ChapterChestReward": { "coins": number; "threshold": number }
"ChapterLevelCompletion": { "denominator": number; "numerator": number; "value": number }
"ChapterStory": { "id": number; "slug": string; "title": string; "world_slug": string }
"ChapterList": {
  "adventure_level_count": number;
  "challenge_count": number;
  "chest_schedule": Array<ApiSchemas["ChapterChestReward"]>;
  "command_skill_count": number;
  "description": string;
  "id": number;
  "is_playable": boolean;
  "level_completion": ApiSchemas["ChapterLevelCompletion"];
  "lock_reason": string;
  "locked": boolean;
  "number": number;
  "slug": string;
  "sort_order": number;
  "story": ApiSchemas["ChapterStory"] | null;
  "title": string;
}
```

Operation responses remain canonical arrays:

```ts
chapters_list: Array<ApiSchemas["ChapterList"]>
stories_list: Array<ApiSchemas["Story"]>
```

The generator-attribution audit reconstructs the pre-slice catalog schema from the HEAD Story/Chapter components and the current prior-slice projections. The Slice 8 semantic delta is only:

- changed existing components: `Story`, `ChapterList`;
- new components: `StoryPrerequisite`, `ChapterStory`, `ChapterLevelCompletion`, `ChapterChestReward`;
- changed paths/operations: none.

`python scripts/check_api_contract.py` confirms both committed generated files are current.

## Frontend Ownership

`frontend/src/features/story-map/types.ts` now derives only the catalog aliases:

```ts
export type Story = ApiSchemas['Story']
export type LearningChapter = ApiSchemas['ChapterList']
```

Unrelated chapter overview/book/gameplay DTOs remain intentionally unchanged and out of scope.

`storyMapApi` now returns the generated operations directly:

```ts
apiOperationRequest('stories_list', '/stories/')
apiOperationRequest('chapters_list', `/chapters/${query}`)
```

The chapter overview/book calls retain their separate manual response types because those contracts are explicit non-goals for a later slice.

## Durability

The shared architecture checker now enforces:

- one exact Curriculum serializer family, including field constructor signatures;
- exact schema decorators for method-returned nested values;
- no catalog serializer shadows in other production backend modules;
- exact Story/LearningChapter generated aliases and deletion of helper DTOs;
- no secondary frontend Story/LearningChapter owner;
- exact direct operation method bodies and no custom response generic;
- no secondary root/refinement/full-shape catalog DTO, including imported or relative aliases and field supersets;
- no duplicate catalog operation wrapper, raw catalog endpoint client, URL alias, or exported `storyMapApi` response adapter;
- bounded Python/TypeScript provenance follows canonical imports, relative imports, assignments, serializer subclasses, object/member destructuring, separate export lists, re-exports, and default exports;
- exact OpenAPI properties, required sets, nested references, nullability, and operation array schemas.

Five new synthetic tests reject wrong serializer fields/decorators, structurally copied or aliased backend/frontend shadows, generated/manual refinements, response overrides, duplicate operation/endpoint wrappers, indirect/exported adapters, optional/open schemas, and wrong operation shapes. Negative probes explicitly allow ordinary services/policies, filter/prop/view-model types, React Query/Suspense Query/options consumers, and the real Story Map page. The complete algorithm lane is 31 passing tests, and the live repository checker is clean.

## Verification Matrix

| Gate | Result |
|---|---|
| Focused catalog endpoint tests | 3 passed |
| Catalog + story access + three-story regression lane | 15 passed in 127.04s |
| Architecture algorithms | 31 passed; terminal combined catalog/guard rerun was 34 passed in 30.31s |
| Live architecture checker | clean |
| Full frontend Vitest suite | 67 files / 465 tests passed |
| Focused Story Map utility tests | 1 file / 5 tests passed |
| Production TypeScript/Vite build | passed; 2,656 modules transformed |
| ESLint | passed |
| Knip/dead-code scan | passed |
| API contract current | passed |
| API wrapper usage | passed |
| Generated type adoption | passed |
| Ruff on all Slice 8 Python | passed |
| Django system check | 0 issues |
| CSS architecture | passed via fast-quality lane |
| Fast quality gates | all 10 passed |
| Documentation current | passed after review/evidence edits |
| Diff hygiene | passed with only disclosed pre-existing CRLF warnings |

The repository-wide backend suite was not repeated: the immediately preceding broad attempt exceeded ten minutes. This read-only boundary instead has direct real-route evidence, focused exact-contract tests, the seeded 15-test regression lane, Django/Ruff checks, generated parity, full frontend coverage, and preservation proof.

## Preservation Audit

The `PRE_SLICE_BASELINE.md` manifest reparses to 111 entries.

- Strict ordinary entries: 107 checked, 0 mismatches.
- Protected Curriculum views/selectors/services/models, generator implementation, and HTTP client retain their exact baseline hashes.
- Generated deltas are generator-attributable only to the two catalog components plus four named nested components; operations do not change.
- Shared guard files are additive under the minimal/patience diff algorithm, which avoids Myers misalignment across repeated checker functions:
  - checker: `3399 + / 2 -` versus baseline `2336 + / 2 -`;
  - algorithm tests: `1424 + / 0 -` versus baseline `1120 + / 0 -`.
- Default Myers numstat misaligns repeated function bodies in the expanded checker and reports spurious move-like deletions; `--minimal` and `--patience` both preserve the frozen deletion count of `2` and produce a clean diff.

Current task-file hashes after review-driven hardening:

| Path | Non-empty lines | SHA-256 |
|---|---:|---|
| `backend/curriculum/serializers.py` | 127 | `58153FD96108F8C40C02E6521CCB192C2AA5D1B7EA2C84CA5BFA07A068F3E0C8` |
| `backend/curriculum/tests/test_catalog_contract_api.py` | 173 | `62B1F58A81389DAE7EE3FF0D62E316002630CA55B7F631DB2AA2A8ABCE9AE2C7` |
| `frontend/src/features/story-map/types.ts` | 51 | `49A0E195772D0617B064E086465C97D34F7581C9B737BCC51A0D0AA64739F0E1` |
| `frontend/src/features/story-map/api/storyMapApi.ts` | 24 | `1C20E9F67925C3ADA9076989C2646A6B004B7065AA4568CDB60FC729460617E8` |
| generated `openapi.json` | 5,734 | `2D1CDFC6DDA94F695C318E90A313FC802595DB5EAB168AF9952020874092B471` |
| generated `apiTypes.ts` | 490 | `34909CE955174E2AD6611641F9819AA2A0E98CBDD5CEC0B7F7C7A88EA6F37631` |
| architecture checker | 3,511 | `AD281BA54E6D093E9C3A85F53D59D60BB9A46758B731FD3F5F5B14F4AC6507EB` |
| architecture algorithm tests | 1,317 | `71DEF72B7078A774080A98553F5126D9A470F744594D955751B029DF1EA06CE5` |

## Review Closure

| Gate | Verdict | Findings |
|---|---|---|
| Krypton POST plan review | ALIGNED | No blocker/major; nullable serializer coverage and line-count labeling fixed |
| Correctness review | PASS | No blocker/major; evidence metadata/pending-gate wording and nullable serializer coverage fixed |
| Maintainability review | PASS | Initial and follow-up alias/provenance findings fixed; final review found no blocker, major, or concrete minor |
| Independent final verifier | PASS | No blocker/major/minor; independently reproduced tests, generated attribution, preservation, hashes, and contract gates |
