# Slice 11 Evidence — Shop Contract and Cache Ownership

Captured on 2026-08-12 for the approved plan in `PLAN.md`. This slice changes only the Shop HTTP contract, frontend Shop data/presentation ownership, and purchase-to-cache convergence.

## Outcome

- `shop.serializers` is the sole backend owner of the Shop request and exact response schemas. `common.openapi` retains only the shared wallet summary used by the purchase response.
- Generated OpenAPI/types are the sole frontend wire contract. The valid difficulty union is `beginner | intermediate | advanced`; `expert` is absent, `unlocks_story` is named and exact, and `active_companion` is required-nullable.
- `shared/shop/api/shopApi.ts` owns the operation-aware catalog/purchase calls and canonical query options. `shared/shop/model/shopPresentation.ts` owns registry-backed display projection. The old feature API and handwritten DTO are deleted.
- Shop, Home Loadout, AppNavigation/player loadout, and wallet observers use the same catalog/wallet query keys. Purchase success awaits both cancellations and atomically installs the server-returned Shop and wallet snapshots without invalidation or compensating GETs.
- Strict request fields reject number, boolean, list, object, and null values before DRF string coercion and before service/player mutation.

## Contract and runtime proof

Backend focused package:

```text
python -m pytest \
  shop/tests/test_shop_catalog.py shop/tests/test_shop_integrity.py \
  progress/tests/test_wallet.py players/tests \
  common/tests/test_architecture_guard_algorithms.py -q
73 passed in 66.21s

python -m pytest shop/tests/test_shop_catalog.py players/tests -q
23 passed in 7.07s
```

The focused Shop cases include exact top-level/item/nested key assertions, an `intermediate` story, all five malformed JSON value classes for both `kind` and `slug`, mocked service non-invocation, and no Player creation. A reviewer-found projection race now has a regression case: if story access disappears between listing and unlock projection, runtime serialization omits optional `unlocks_story` instead of emitting contract-invalid `null`. Existing transaction/integrity/wallet behavior was preserved in the `31 passed` replay and in the final 73-test package.

Schema/runtime checks:

```text
python manage.py spectacular --file NUL --validate
Errors: 0; existing warnings only

python scripts/generate_api_contract.py
Regeneration was byte-stable:
openapi.json  8581B1975B00F996BC5033AE5B197775416DE66402980B869A70A466521A4C50
apiTypes.ts   8ACA708EAFFB702635D1EC0E1AA76803DD4D13389616521085AF905681FED92A

python scripts/check_api_contract.py
Generated API contract is current.
```

Direct Django import smoke loaded `shop.serializers` and `common.openapi` successfully, demonstrating the dependency direction is acyclic. Shop imports the common wallet serializer; common imports or re-exports no Shop serializer.

## Frontend cache-convergence proof

```text
npm test -- --run \
  src/shared/shop/api/shopApi.test.ts \
  src/shared/shop/model/shopPresentation.test.ts \
  src/features/shop/utils/shopDisplay.test.ts \
  src/features/shop/pages/ShopPage.test.tsx

4 files passed; 8 tests passed; duration 20.95s
```

The ShopPage integration test mounts ShopPage together with real wallet and player-loadout observers. It starts stale catalog and wallet reads before POST, proves both cancel operations must finish, checks there is no mixed old/new observer snapshot, installs the purchase response, resolves the stale promises afterward, and verifies they cannot overwrite the purchased state. The request log contains no catalog or wallet GET initiated after the purchase POST.

## Real-browser trace

The app ran through Vite with a same-origin initialization-time fetch harness; application modules, React Query, Shop UI, Home layout, and navigation were unmodified. The temporary harness was deleted after the trace.

Initial Shop route (`/shop?tab=companions`):

```text
top navigation: 150 GitCoins
Shop action:     150 GitCoins | Purchase
```

After clicking Purchase:

```json
{
  "top_navigation": "0GitCoins",
  "shop_action": "Manage in Loadout",
  "requests_after_click": [
    {"method":"POST","path":"/api/shop/catalog/purchase/"}
  ]
}
```

Navigating in-app to `/settings` preserved `0 GitCoins` and initiated no request. A clean-page reload against post-purchase deterministic GET truth rendered `0 GitCoins` and `Manage in Loadout`; its request log included fresh GETs for `/api/shop/catalog/` and `/api/progress/wallet/`. This proves immediate Shop/navigation convergence without compensating reads, route-to-route cache coherence, and reload reconstruction of balance/ownership/active-companion truth.

## Full and repository checks

```text
Frontend full suite: 72 files passed; 490 tests passed; 250.19s
npm run build: passed (2,658 modules)
npm run lint: passed
npm run lint:dead: passed

python scripts/check_quality_gates.py: all fast quality gates passed
python scripts/check_frontend_api_usage.py: passed
python scripts/check_api_type_adoption.py: passed
python scripts/checks/check_architecture_boundaries.py: passed
python scripts/check_generated_targets_current.py: 2,056 cases; current
python scripts/check_documentation_current.py: passed
python scripts/check_ci_quality_gates.py: passed
python scripts/check_repository_artifacts.py: passed
git diff --check: passed (two pre-existing line-ending warnings only)
```

Ruff passes on all touched backend runtime/test files. The repository-wide Ruff gate remains red only on known pre-slice formatting/import findings in unrelated earlier-slice files; no broad formatting was applied in this dirty worktree.

The repository-wide backend `pytest -q` lane was attempted twice. The command wrapper first expired at 604 seconds while pytest was still running. A captured restart remained healthy and failure-free after more than 20 minutes but had reached only 3%, matching the timeout already documented by prior contract slices; it was then stopped safely. This slice therefore claims proportional backend evidence: 73 Shop/Player/wallet/architecture tests, all exact request/response/race cases, scoped Ruff, Django system check, schema validation, direct import smoke, and all contract/architecture gates. `python manage.py test` also completed its system check but is not the project's test runner and discovered zero tests.

## Ownership and displaced-path searches

- No runtime import remains from `features/shop/api` or `features/shop/types`; both facades are deleted.
- The only runtime literal `/shop/catalog/` is in `shared/shop/api/shopApi.ts`; other occurrences are tests or generated contract metadata.
- No handwritten Shop response object type or partial player-loadout DTO remains.
- No non-Shop feature imports a Shop feature module; Home Loadout imports the shared Shop boundary.
- Backend views import Shop serializers directly from `shop.serializers`; `common.openapi` contains no Shop class.
- Architecture, API-usage, and type-adoption checks all enforce the new shared path.

## Preservation replay

- Dirty baseline manifest: `139` entries.
- Strict ordinary entries: `134` replayed byte-for-byte with `0` errors.
- Frozen `GOAL.md` hash remains `39DEE889CBEBF1B6E54397F27F6146F1B61850A589E4D9FE8D6690AFFE9F09A4`.
- All 14 protected commerce, wallet, model, query-key, navigation, registry, and Shop-style hashes remain exact.
- Each of the three enforcement-script path changes reverses to its pre-slice SHA-256 exactly; the architecture checker has precisely the one reviewer-approved path substitution.
- Generated files were regenerated canonically and proved byte-stable on a second generator run.
- `common.openapi` changed only by removal of the relocated Shop classes plus normalization of the Shop-only blank space left by deletion. No non-Shop symbol changed during this slice.
- The reviewed serializer-name amendment (`ShopStoryUnlockResponse` to `ShopUnlockResponse`) avoided the existing schema checker's nested-name collision heuristic and changed no runtime payload.

Final key artifact hashes:

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| `backend/shop/serializers.py` | 2,120 | `06016A0A034AA5DA9820E1D4BBCD539681DE0A7C4E1DF5D9EFDAFBF318172982` |
| `backend/common/openapi.py` | 6,546 | `13E7DE38857BEB39194140BEA54D69A9B60EF21B98972398683369651557A93C` |
| `backend/shop/views.py` | 1,637 | `7E20E33E019D46B3AEC435530B91525AF1C7136B676CE16C49DA74E8114E1016` |
| `frontend/src/shared/shop/api/shopApi.ts` | 1,133 | `1B5DE86AA7D7D31AA6CE3B0602135BAEAE043D099EA91A9540C022F0235FB0E0` |
| `frontend/src/shared/shop/model/shopPresentation.ts` | 1,496 | `6E17B177FDB0DC1AC7420D5CE8A013CF26D16692C468D7BBC3144398785ED94D` |
| `frontend/src/features/shop/pages/ShopPage.tsx` | 6,035 | `9D6F511DEFFC08CADA33B541B3061FDD2D82F73D6F39B3A09CB22D57E83BE060` |
| `frontend/src/features/shop/pages/ShopPage.test.tsx` | 7,831 | `7EE83F6817F7D793482523635C7EA6C4DE75A351E8928661CE5E975316957255` |
| generated `openapi.json` | current | `8581B1975B00F996BC5033AE5B197775416DE66402980B869A70A466521A4C50` |
| generated `apiTypes.ts` | current | `8ACA708EAFFB702635D1EC0E1AA76803DD4D13389616521085AF905681FED92A` |

## Review record

- PRE plan reviewer: initially requested stronger stale-read race, strict pre-coercion validation, browser navigation/reload evidence, and explicit dependency direction. The plan was amended and returned `aligned`.
- PRE amendment reviewer: approved the semantic-neutral `ShopUnlockResponse` naming amendment.
- POST plan reviewer: `aligned`; no findings. Residual risk is the intentionally recorded full-backend-run duration, covered proportionally by the focused backend package and target-perspective evidence.
- Maintainability reviewer: `PASS`; no blocker, major, or minor findings. Ownership is one-way, displaced facades are gone, query convergence stays localized, and preservation is exact. Residual risk: the enforcement scripts scan the canonical shared owner but do not proactively forbid recreation of the deleted feature paths; current searches are clean.
- Correctness reviewer: found one P2 race where a story disappearing between the listing and access lookups could serialize `unlocks_story: null` against an object-or-omission contract. `ShopItemResponseSerializer` now removes a `None` optional projection and a real endpoint regression test covers that transition; the 73-test backend package, generated-contract checks, TypeScript, and focused frontend tests all pass after the correction.
- Independent final verifier: `VERIFIED`. Runtime/generated contract, strict mutation validation, one shared Shop boundary, cache-race behavior, browser purchase/navigation/reload evidence, fresh 73-test backend and focused frontend/TypeScript/quality gates, and `139/134/0` preservation evidence prove the target result. Residual risk remains only the explicitly incomplete repository-wide backend suite caused by its extreme duration.
