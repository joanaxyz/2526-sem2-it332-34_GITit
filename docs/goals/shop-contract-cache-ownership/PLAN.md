# Shop Contract and Cache Ownership — Slice 11 Implementation Plan

**Intent:** Give shop request/response contracts, frontend catalog access, and post-purchase cache convergence one explicit owner so every consumer sees the same generated shape and a successful purchase is reflected immediately without compensating reads.
**Current Behavior:** Shop serializers live in `common/openapi.py`; `unlocks_story` is documented as an untyped dictionary; `active_companion` is incorrectly optional in the generated contract; runtime story listings leak three undocumented top-level fields; and `ShopPurchaseAPIView` documents but bypasses its request serializer. The frontend overrides the generated response with handwritten DTOs whose difficulty union permits `expert` but omits the backend's valid `intermediate`, exposes a feature-owned API to other features, repeats presentation mapping across a feature boundary, loads the same query key through a raw partial `apiRequest`, reconstructs the wallet query instead of using its owner hook, and discards the authoritative purchase response in favor of two refetches.
**Expected Outcome:** The shop app owns exact runtime and OpenAPI serializers; generated TypeScript is the only frontend wire contract; a shared shop boundary owns API calls, catalog query options, and the cross-feature display projection; every full and partial catalog consumer shares that contract; non-string purchase fields are rejected before DRF coercion as controlled 400 responses; and purchase success cancels older reads before atomically installing the returned catalog and wallet snapshots.
**Target-Perspective Output:** A player buys a first companion once and immediately sees the new balance, owned/equipped state, loadout readiness, and navigation wallet state without waiting for catalog or wallet refetches. A reload returns the same state from backend truth. Invalid structured payloads produce a client error rather than a server exception, while insufficient funds, feature flags, idempotency, prices, entitlements, and equip behavior remain unchanged.
**Truth Owner:** `shop.catalog` owns purchasable metadata; `shop.models` owns entitlements/loadout; `progress.wallet.WalletService` owns the ledger; `shop.selectors.shop_payload` owns catalog assembly; new `shop.serializers` owns the exact HTTP request/response projection at runtime and in OpenAPI; generated `ApiSchemas`/operation types own the frontend wire contract; and new `shared/shop` modules own frontend access, query identity, and cross-feature presentation projection.
**Contract Boundary:** Backend catalog/service/model truth -> `shop_payload` -> `shop.serializers` runtime projection/OpenAPI -> generated TypeScript operation -> shared shop API/query options -> Shop, Home Loadout, and player-loadout consumers. Purchase writes return `{owned,wallet,shop}` and cross into the two existing query caches only after relevant in-flight reads are cancelled.
**Cutover:** Move every shop-specific serializer from `common.openapi` to `shop.serializers`, make the nested story unlock and required-nullable companion state exact, validate request data in both mutation views, serialize all shop responses through that owner, stop listing undocumented story metadata at the item top level, regenerate both contract artifacts, replace the feature-owned API/handwritten types with generated aliases under `shared/shop`, move cross-feature presentation logic to that shared boundary, route all catalog queries through one operation-aware query-options factory, use the canonical wallet hook, and replace post-purchase invalidation with cancel-then-install cache convergence.
**Displaced Path:** Shop serializer classes in `common.openapi`, the feature shop API wrapper/test, `features/shop/types.ts`, the partial handwritten `ShopCatalogResponse` and raw request in `usePlayerLoadout`, catalog query-function duplication, Home's imports from the Shop feature, story metadata duplicated at the item top level, the ShopPage wallet query reconstruction, and post-purchase catalog/wallet invalidation are deleted. No compatibility facade remains.
**Value Density:** This one vertical slice fixes a real generated/manual contract contradiction, removes three frontend truth paths and a cross-feature dependency, moves backend schemas to their domain owner, closes malformed-input 500 risk, and eliminates two network reads plus a stale post-purchase UI window while preserving transactional commerce behavior.
**Acceptance Evidence:** Exact backend request/response API tests; regenerated schema inspection and import smoke proof; compile-time generated-type adoption; a ShopPage integration test that begins stale background catalog/wallet reads before purchase, proves both reads are cancelled, resolves them after success, and shows the Shop UI, wallet hook, and player-loadout hook remain atomically converged with no post-POST GET or mixed snapshot; a real-browser purchase/navigation/reload trace against deterministic API routes; focused and full backend/frontend gates; static displaced-path searches; and dirty-worktree hash replay.
**Evidence Lane:** Backend response-key and malformed-payload cases -> generated contract diff -> shared API/presentation/query tests -> ShopPage cache-convergence integration -> same-origin browser trace -> focused/full suites -> API/architecture/quality gates -> preservation replay -> POST/correctness/maintainability/verifier reviews.
**Kill Criteria:** No shop serializer remains in or is re-exported by `common.openapi`; no handwritten frontend shop response object type remains; generated `unlocks_story` is a named exact schema whose difficulty includes `intermediate` and excludes `expert`; `active_companion` is required and nullable; story items expose no undocumented top-level world/difficulty/prerequisite fields; no raw or secondary `/shop/catalog/` request exists outside the shared shop API owner; no non-Shop feature imports from `features/shop`; all catalog observers share `queryKeys.shopCatalog` and the generated operation; ShopPage does not reconstruct the wallet query; purchase success performs no cache invalidation/refetch, renders no mixed old/new catalog-wallet snapshot, and cannot be overwritten when cancelled stale GET promises resolve later; number, boolean, list, object, and null mutation fields fail before string coercion with controlled 400 responses and no service/data mutation; the browser proves immediate Shop and navigation-wallet convergence, then reloads against post-purchase backend-route truth and reproduces balance/ownership/active state; no pricing, feature-flag, ledger, entitlement, idempotency, equip, reward, route, or visual behavior changes; no manual generated-file edit; and no unrelated dirty-worktree byte changes.
**Architecture Slice:** Shop HTTP contracts, frontend shop access/presentation ownership, and purchase-to-cache convergence only. Commerce transaction rules, wallet implementation, database models/migrations, authentication, catalog content/pricing, feature flags, reward flows, navigation structure, visual components/styles, and unrelated architecture-checker algorithms are frozen.
**Plan Review Gate:** Requires PRE review before baseline capture or implementation.

## Outcome Contract

### Canonical HTTP shapes

`ShopUnlockResponse` is exactly:

```text
{
  slug: string,
  title: string,
  chapter_count: integer,
  world_slug: string,
  difficulty: "beginner" | "intermediate" | "advanced",
  prerequisite_story: string | null
}
```

`ShopItemResponse` is exactly `{kind,slug,label,price,owned,active}` plus optional `unlocks_story` for story items. The three story-access fields never also appear at item top level.

`ShopResponse` is exactly `{items,active_companion,purchases_enabled}`. `active_companion` is always present and may be `null`.

`ShopPurchaseResponse` remains exactly `{owned,wallet,shop}` and `ShopEquipResponse` remains exactly `{active_companion,shop}`. The wallet response owner remains the existing shared `WalletSummaryResponseSerializer` in `common.openapi`; this slice does not relocate or duplicate it.

### Runtime transitions

| Input/transition | Backend result | Frontend result |
|---|---|---|
| Catalog read | Runtime-serialized exact `ShopResponse` | Existing `shopCatalog` cache receives generated `ShopCatalog` |
| Valid purchase | Existing transaction returns fresh wallet and catalog | Cancel catalog/wallet reads, then synchronously install both returned snapshots |
| First companion purchase | Existing service auto-equips it | Shop, Home Loadout, player-loadout gate, and wallet observers converge through shared cache keys |
| Repeat purchase | Existing idempotent transaction remains unchanged | Same authoritative snapshots replace cache; no compensating GET |
| Insufficient funds or disabled purchase | Existing controlled 4xx and no data change | Mutation error; successful caches are not overwritten |
| List/object/non-string slug payload | Request serializer rejects it | Controlled 400; no service call or data mutation |
| Equip companion | Existing service and response remain unchanged | Existing catalog cache update remains; wallet cache is untouched |

### Query contract

- `shared/shop/api/shopApi.ts` exports generated aliases, the two operation-aware calls, and the canonical catalog query-options factory.
- The default catalog freshness remains 60 seconds for Shop and Home Loadout.
- `usePlayerLoadout` keeps its existing five-minute `staleTime` and `retry:false` observer behavior by overriding only those options while retaining the canonical key, query function, and full generated response.
- `useWalletSummary` remains the only wallet query hook and keeps its current key, request, and 60-second freshness.
- Before installing a purchase response, ShopPage awaits cancellation of both query keys. It then batches the `result.shop` and `result.wallet` writes so observers cannot render a mixed snapshot; it never invalidates them on success. A cancelled older promise resolving later must remain unable to replace either snapshot.

### Backend dependency direction

- `shop.serializers` may import DRF, the canonical `Story.DIFFICULTY_CHOICES`, and the existing common wallet serializer.
- `common.openapi` must not import or re-export anything from `shop.serializers` after cutover.
- Shop and Player views import Shop request/response serializers directly from `shop.serializers`.
- Schema generation and a direct import smoke check must succeed, proving the dependency graph is acyclic.

## Architecture Map

### Files to create

- `backend/shop/serializers.py`
- `frontend/src/shared/shop/api/shopApi.ts`
- `frontend/src/shared/shop/api/shopApi.test.ts`
- `frontend/src/shared/shop/model/shopPresentation.ts`
- `frontend/src/shared/shop/model/shopPresentation.test.ts`
- `frontend/src/features/shop/pages/ShopPage.test.tsx`
- `docs/goals/shop-contract-cache-ownership/GOAL.md`
- `docs/goals/shop-contract-cache-ownership/PRE_SLICE_BASELINE.md`
- `docs/goals/shop-contract-cache-ownership/EVIDENCE.md`

### Files to modify

- `backend/common/openapi.py`, deletion of relocated Shop serializers only
- `backend/shop/views.py`
- `backend/players/views.py`, shop serializer imports and exact response serialization only
- `backend/shop/catalog.py`, public listing projection only
- `backend/shop/tests/test_shop_catalog.py`
- Generated `frontend/src/shared/api/generated/openapi.json` and `apiTypes.ts`, generator output only
- `frontend/src/features/shop/pages/ShopPage.tsx`
- `frontend/src/features/shop/components/CompanionShop.tsx`
- `frontend/src/features/shop/components/StoryShop.tsx`
- `frontend/src/features/shop/utils/shopDisplay.ts` and its test, feature-only actions/tabs after projection displacement
- `frontend/src/features/home/components/HomeLoadoutView.tsx`, import/query owner cutover only
- `frontend/src/shared/player-loadout/usePlayerLoadout.ts`, canonical query cutover only
- `scripts/checks/check_api_type_adoption.py` and `check_frontend_api_usage.py`, replace the displaced feature API enforcement path with the shared owner
- `scripts/checks/check_architecture_boundaries.py`, replace the displaced Shop feature data-module path with the shared Shop boundary in the existing Home Hub rule only

### Files to delete

- `frontend/src/features/shop/api/shopApi.ts`
- `frontend/src/features/shop/api/shopApi.test.ts`
- `frontend/src/features/shop/types.ts`

### Files to avoid and preserve exactly

- `backend/shop/services/**`, `models.py`, `access.py`, migrations, and prices/catalog constants
- `backend/progress/**`, `WalletService`, wallet models/migrations, and wallet response schema
- `backend/adminconsole/**`, authentication, curriculum services, reward flows, adventure/challenge services
- `frontend/src/shared/wallet/**`, `queryKeys.ts`, player-loadout API, navigation, registries, routes, styles, and visual markup outside import wiring
- Architecture-checker logic other than the one displaced module-path replacement
- All unrelated Slice 1–10 dirty-worktree entries

### Read path

`Shop/Home/player-loadout observer -> shared shop query options -> operation-aware API -> ShopAPIView -> shop_payload -> exact ShopResponseSerializer -> shared shop cache`

### Write path

`Shop action -> shared shop purchase operation -> validated ShopMutationRequest -> unchanged ShopService transaction -> exact ShopPurchaseResponse -> cancel old catalog/wallet reads -> install returned catalog/wallet snapshots -> all observers update`

### Integration points

- Existing generated API generator and contract checks.
- Existing `queryKeys.shopCatalog` and `queryKeys.wallet` identities.
- Existing `useWalletSummary` hook.
- Existing `usePlayerLoadout` projection/fallback behavior.
- Existing Home Loadout equip response cache update.
- Existing Shop and Player API routes.

### Migration/cutover

No data or deployment migration exists. Code/schema cutover is atomic: backend views switch imports/runtime serialization when the old common classes are deleted; generated artifacts update in the same task; frontend imports switch to the shared owner when old API/types files are deleted; all query readers switch before the raw partial loader disappears.

## Task Board

### Task 1: Capture the approved preservation boundary

- **Owner:** Main agent.
- **Files allowed:** New `PRE_SLICE_BASELINE.md` only.
- **Output:** Full dirty manifest with status/bytes/SHA-256; exact hashes and sizes for every planned existing target; absence records for new files; and protected hashes for services, wallet, models, query keys, registries, styles, and architecture tests.
- **Verification:** Reparse every manifest row and recompute every hash before implementation.
- **Acceptance evidence:** Planned dirty targets (`common/openapi.py`, generated artifacts, architecture checker) are mechanically separated from strict unrelated work.
- **Depends on:** PRE approval.
- **Parallel safe:** No.

### Task 2: Establish the exact backend shop contract owner

- **Owner:** Main agent.
- **Files allowed:** `shop/serializers.py`, the scoped common serializer deletions, Shop/Player view imports and request/response serialization, `shop/catalog.py` listing projection, and focused Shop API tests.
- **Output:** Exact nested story schema, required-nullable active companion, pre-coercion strict-string runtime validation for both mutation fields, runtime response serialization, and no duplicate top-level story metadata.
- **Verification:** Focused shop catalog/integrity tests; parameterized number/boolean/list/object/null cases proving 400 plus no service/data mutation; exact response-key assertions; direct Shop/common import smoke check; schema generation; Ruff/format checks if configured.
- **Acceptance evidence:** Real DRF requests return exact shapes and controlled 4xx behavior while transaction/integrity cases remain green.
- **Depends on:** Task 1.
- **Parallel safe:** No.

### Task 3: Regenerate and cut frontend contract/query ownership over

- **Owner:** Main agent.
- **Files allowed:** Generated artifacts via generator; new shared Shop API/presentation files and tests; deletion of old API/types; scoped imports/query calls in Shop, Home Loadout, player loadout, and Shop components/utilities; three enforcement-script path replacements.
- **Output:** Generated aliases only, one catalog operation/query function, no raw partial loader, no cross-feature Shop imports, preserved observer policies, and exact display mapping through a shared projection.
- **Verification:** API generation/current checks, TypeScript, focused API/presentation/display tests, static ownership searches, live architecture checks.
- **Acceptance evidence:** The generated contract accepts `intermediate`, has no `expert`, exposes exact nested fields, and every consumer compiles against it.
- **Depends on:** Task 2.
- **Parallel safe:** No.

### Task 4: Make purchase success cache-authoritative

- **Owner:** Main agent.
- **Files allowed:** `ShopPage.tsx` and new `ShopPage.test.tsx` only.
- **Output:** Canonical wallet hook, await-cancel-then-batched-install success transition, no invalidation, and an integration test with ShopPage plus wallet/player-loadout observers.
- **Verification:** The race test proves initial reads, explicitly starts deferred stale catalog/wallet refetches before the POST, records that both cancel operations finish, installs the purchase snapshots, resolves stale promises afterward, and still shows immediate balance/owned/active/loadout convergence with no mixed rendered snapshot and no GET initiated after the POST.
- **Acceptance evidence:** Same-origin browser trace shows immediate Shop balance/ownership and navigation-wallet update without a compensating network read, switches deterministic GET routes to post-purchase backend truth, reloads, and reproduces balance, ownership, and active companion from those reads.
- **Depends on:** Task 3.
- **Parallel safe:** No.

### Task 5: Prove cutover, preservation, and review closure

- **Owner:** Main agent.
- **Files allowed:** New `EVIDENCE.md`; implementation targets only for attributable review fixes.
- **Output:** Backend response/request traces, generated-schema evidence, frontend cache/browser trace, focused/full checks, displaced-path searches, target hashes/diffs, strict manifest replay, and all review decisions.
- **Verification:** Focused and full backend/frontend tests; build, lint, Knip; API/architecture/docs/quality gates; `git diff --check`; PRE-vs-POST replay; POST/correctness/maintainability/final verification.
- **Acceptance evidence:** Every expected outcome and kill criterion is backed by reproducible output, not only code inspection.
- **Depends on:** Tasks 1–4.
- **Parallel safe:** Review lanes only after coherent implementation; main agent retains all writes.

## Forbidden Moves

- Do not change prices, catalog membership/order, entitlement rules, first-companion auto-equip, idempotency keys, wallet balance semantics, feature flags, permissions, or error behavior outside malformed structural input.
- Do not move or duplicate the wallet serializer, wallet API, wallet hook, query keys, or shop service transaction.
- Do not retain a facade at the old feature API/types paths.
- Do not manually edit generated API artifacts; run the generator after backend truth changes.
- Do not broaden the Shop presentation move into visual redesign, component markup, styles, registries, routing, or navigation changes.
- Do not add a generic commerce abstraction or a second cache/store.
- Do not expand the architecture checker beyond replacing the displaced Shop data-module path in its existing rule.
- Do not stage, normalize, discard, or overwrite unrelated dirty work.

## Review Gates

1. PRE plan review before baseline capture or implementation.
2. POST alignment review after implementation and evidence draft.
3. Correctness review focused on serializer/runtime agreement, purchase integrity, cache race prevention, shared-query convergence, and real-path proof.
4. Maintainability review focused on single owners, deleted facades, generated aliases, import direction, query-policy clarity, and test ownership.
5. Independent final verifier after findings and evidence metadata are synchronized.
