# Authentication Browser-State Trust Boundary — Slice 10 Evidence

## Outcome

Browser-originated authentication state now crosses one explicit runtime boundary. Stored users and cross-tab messages are validated against the generated `User` projection, legacy records are canonicalized, malformed storage clears stale auth, malformed channel traffic is ignored, and browser API failures cannot abort in-memory auth actions.

Cross-tab and refreshed tokens are now synchronization hints rather than identity assertions. Receiving a token-bearing message or beginning the refresh-confirmation path clears `user`, which keeps protected children hidden until `/auth/me/` succeeds. The resulting identity is installed through `confirmAuthSession`, a semantic non-broadcasting transition, so two tabs converge without confirmation echo. Backend security, generated contracts, HTTP retry control flow, rendering, routes, and permissions are unchanged.

## Ownership and cutover

- Compile-time user truth remains `ApiSchemas['User']` through `shared/auth/types.ts`.
- Runtime browser-data truth now lives in `shared/auth/authSessionBoundary.ts`.
- `useAuth.ts` delegates canonicalization, persistence, legacy cleanup, transport validation, and subscriptions to that boundary.
- Existing store actions remain source-compatible. New `beginAuthConfirmation` and `confirmAuthSession` transitions are used only by `Protected.tsx`; automatic HTTP retry retains the existing `setAccessToken` behavior.
- `Protected.tsx` changed only at its auth-store import, the refreshed-token transition, and the two post-`/auth/me/` transitions. Query enabling, refresh/me ordering, loading, redirect, and render behavior are byte-identical.
- Three persistence/storage-event cases moved out of `httpClient.test.ts`; that suite now contains five HTTP-focused cases. Its stale non-contract `tier` fixture field was removed.
- No compatibility wrapper, parallel user DTO, generic preference-storage dependency, architecture-checker rule, or persisted access-token path was added.

## Target-perspective behavior

The deterministic store integration lane proves the approved event matrix from an already authenticated state:

- A legacy stored user without `is_staff` and with an unknown field hydrates as exact `{id, username, email, is_staff:false}`, rewrites storage canonically, and removes the legacy token key.
- Empty/whitespace-token sessions and partial-user channel messages leave the active identity/token unchanged.
- A canonical or migratable stored-user event clears the memory-only token, installs the canonical cache, and rewrites storage.
- Stored-user removal, malformed JSON, and invalid-but-parseable user shapes each clear both token and user; invalid storage is removed.
- A valid session channel message installs its token with `user:null` and does not persist the channel user.
- A valid access-token message installs the original credential string with `user:null` and writes no token to storage.
- Beginning refresh confirmation atomically installs the refreshed token with `user:null` before the pending `/auth/me/` promise can expose protected children.
- Backend confirmation installs/persists the canonical user without emitting another channel message.
- A clear-session message clears memory and stored user data.
- Throwing storage and channel implementations do not prevent `setSession`, `setAccessToken`, or `clearSession` from completing their in-memory transitions.

## Real-browser two-page trace

The agent-browser QA skill drove two same-origin Chromium 149 tabs against the final Vite-loaded auth modules and native `localStorage` / `StorageEvent` / `BroadcastChannel`. The component lane separately held the real `Protected` query's `/auth/me/` promise pending and then rejected it; the two-page lane isolated native ordering, transport, quiescence, and browser-API failure behavior.

Observed native ordering and convergence:

1. Sender `setSession` persisted one exact canonical user and no access-token key. Native storage/channel ordering left the receiver at `{accessToken:null,cachedUser}`, the ordering that exposed the late stale-user risk.
2. The receiver called the final `beginAuthConfirmation`. It immediately became `{refreshPendingToken,user:null}` and emitted one access-token message; the sender received the same `{token,user:null}` transition.
3. Both pages remained in that unverified state for a full one-second window. Neither recovered the cached identity, and each monitor observed exactly one message.
4. Each page then installed the simulated backend-confirmed identity through `confirmAuthSession`. After another one-second window, both remained confirmed and both message counts remained exactly one, proving confirmation emits no echo.
5. Two malformed channel messages (whitespace token with forged staff user; valid token with partial user) were observed by both monitors, bringing their raw counts to three, but neither store changed.
6. With real `Storage.prototype` writes/removals and `BroadcastChannel.prototype.postMessage` temporarily throwing, one page's `setSession` still installed `{offlineToken,canonicalUser}` in memory; the peer remained unchanged.
7. After restoring the browser APIs, logout added exactly one clear message. Both tabs ended `{accessToken:null,user:null}`, both storage keys were absent, and both counts remained stable at four after a final one-second window.

The run confirms actual cross-mechanism ordering can vary, every refreshed/channel token invalidates cached identity before confirmation, and successful confirmation traffic is bounded and reaches a quiescent state.

## Verification matrix

| Lane | Result |
|---|---|
| Initial PRE plan review | `PASS` after explicit storage-vs-channel transition semantics and whitespace-token rules |
| Correctness amendment PRE | `PASS` after finite-integer, no-echo confirmation, browser-quiescence, and preservation amendments |
| Pre-confirmation render amendment PRE | `PASS`; preserves HTTP retry semantics and closes the stale-user render window |
| Focused boundary/store/Protected/HTTP tests | 4 files, 31 tests passed in 32.64s |
| Protected pending/rejected confirmation test | Passed; refreshed token pairs with `user:null`, loading remains visible, rejection redirects to login, child never renders |
| Real same-origin two-page Chromium trace | Passed all seven ordering/refresh/malformed/failure/logout/quiescence steps |
| Full frontend tests | 70 files, 488 tests passed in 321.66s |
| TypeScript/Vite production build | Passed; 2,657 modules transformed |
| ESLint | Passed, full frontend and focused target invocation |
| Knip dead-code check | Passed |
| Architecture algorithm tests | 37 passed in 39.93s |
| Live architecture checker | `Architecture boundaries look clean.` |
| Generated API currency | Current |
| Frontend generated API usage/type adoption | Both passed |
| Documentation currency | Passed |
| Fast repository quality gates | All passed, including 2,056 generated curriculum cases |
| Diff hygiene | `git diff --check` passed; only existing line-ending notices were emitted |

Focused terminal command:

```text
npm test -- --run src/shared/auth/authSessionBoundary.test.ts src/shared/auth/useAuth.test.ts src/shared/api/httpClient.test.ts src/app/Protected.test.tsx
Test Files  4 passed (4)
Tests       31 passed (31)
Duration    32.64s
```

Full frontend command:

```text
npm test
Test Files  70 passed (70)
Tests       488 passed (488)
Duration    321.66s
```

Repository enforcement:

```text
python -m pytest backend/common/tests/test_architecture_guard_algorithms.py -q
37 passed

python scripts/checks/check_architecture_boundaries.py
Architecture boundaries look clean.

python scripts/check_quality_gates.py
All fast quality gates passed.
```

## Kill-criteria evidence

Production search for auth browser I/O reports only `authSessionBoundary.ts`. The equivalent search against `useAuth.ts` returns no matches for auth keys, `localStorage`, `JSON.parse`, `BroadcastChannel`, `event.data`, or `message.user`.

Additional searches report:

- exactly one definition each for `beginAuthConfirmation` and `confirmAuthSession`, plus the one intended begin call and two intended confirm calls in `Protected`;
- no persistence/storage-key assertion remains in `httpClient.test.ts`;
- no `persistentState`, preferences, or challenge-cache import exists under shared auth;
- no handwritten `User` type was introduced;
- no generated, backend, production HTTP client, architecture-checker, or architecture-test change occurred;
- only the boundary module contains the three auth browser constants and raw browser operations.

The boundary publishes only messages that re-pass its runtime decoder. Session/access-token messages require `token.trim().length > 0` and preserve the original valid token. Canonical user construction uses finite-integer IDs and `satisfies User`, so a generated required-field change fails compilation instead of silently creating a stale decoder contract.

## Size and value evidence

| Path | Non-empty lines | Bytes | SHA-256 |
|---|---:|---:|---|
| `useAuth.ts` | 76 | 2,662 | `BBC136D1629496E45697393E39AA7D5CAF070D7D76D99710DE5EB19F63EA0BE5` |
| `authSessionBoundary.ts` | 187 | 5,902 | `80790432D76A92FC9B32A272DD4BA17A1AF7356145C40595E80BB7A2CBDB9E86` |
| `authSessionBoundary.test.ts` | 180 | 7,255 | `67BC57C8F5F9C224A9AD9FECE25B7B6DC3F0FD985A097AA05FB3D0C046318DEF` |
| `useAuth.test.ts` | 169 | 7,680 | `A616855587CA3E7F926B7648D49D417B7C4FF1D27E8B3B9D7A3C9F4DDD5D4793` |
| `httpClient.test.ts` | 135 | 6,361 | `3790425184463DB9BC7CB344C4487BFAC48364271EF7521A6CFCF2B78B01C00A` |
| `Protected.tsx` | 43 | 1,427 | `095A6B4EE87F6B228AD36474C8165FE8D3979C65055DA78D2788A64863BAE16C` |
| `Protected.test.tsx` | 68 | 2,581 | `196D0F669570D3F171CF48A024CA3E37C19A4A5158A1002CF13B07BB9774CC36` |

Tracked target numstat is `useAuth.ts: +52/-87`, `httpClient.test.ts: +0/-28`, and `Protected.tsx: +8/-4`. The store lost 30 non-empty lines, the HTTP suite lost 20 non-empty lines, the new cohesive production owner remains below the repository's 400-line reviewability threshold, and the route guard's four-line net growth is only the formatted semantic-helper import.

## Preservation replay

- All 127 strict non-plan dirty-manifest entries reproduce their pre-slice byte counts and SHA-256 hashes: `strict_manifest_errors=0`.
- The plan retains its original pre-amendment hash in the baseline; its only later changes are the independently reviewed finite-integer, no-echo confirmation, pre-confirmation-render, real-browser, failure-construction, and preservation amendments.
- `Protected.tsx` retains its original baseline hash in the amendment record. Its final diff is exactly one formatted import replacement, one refresh-path begin replacement, and two post-`/auth/me/` confirm replacements (`+8/-4`); every query/render/error/routing byte is unchanged.
- All other protected auth/API/UI/persistence/generated/checker files reproduce their baseline hashes exactly.
- The architecture checker remains 187,011 bytes with SHA-256 `53814BE32D540A9C4AD360470B7E2A2359B71433B65B2141969BB80FE5ECB169`.
- Architecture algorithm tests remain 76,454 bytes with SHA-256 `949FCA4E22082821D3AA8E4D334749C97262193B13C13E948B7153BB1402064F`.
- Generated OpenAPI/TypeScript remain 199,009/43,977 bytes with baseline hashes `11AFC826...E9EE8` and `6FDAAB9D...DE14`.
- No unrelated entry was staged, normalized, discarded, or overwritten.

## Review closure

| Gate | Status | Notes |
|---|---|---|
| POST alignment | `ALIGNED` | Final implementation, tests, evidence, and preservation scope match the reviewed contract. |
| Correctness | `APPROVE` | No blocker, major, or minor findings; the reviewer independently replayed all 31 focused tests. |
| Maintainability | `APPROVE` | One browser-state owner, displaced paths removed, cohesive API, and behavior-owned tests; no findings. |
| Independent verifier | `VERIFIED` | Alternate independent replay found no mechanical discrepancies in target hashes, strict preservation, exact Protected scope, displaced-path searches, or the 31 focused tests. |

Residual maintainability risk: module-scoped browser subscriptions do not expose teardown for repeated hot-module initialization. Normal production initialization remains singleton-scoped; changing lifecycle ownership is deliberately deferred rather than expanding this bounded security slice.
