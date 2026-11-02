# Authentication Browser-State Trust Boundary — Slice 10 Implementation Plan

**Intent:** Make browser-persisted and cross-tab authentication state fail closed at one explicit runtime boundary while preserving the public store API and backend security behavior.
**Current Behavior:** `shared/auth/useAuth.ts` owns Zustand orchestration, storage keys, JSON parsing, a legacy migration, raw localStorage mutations, BroadcastChannel construction, and loosely checked message handling. Any syntactically valid stored JSON is cast to `User`; channel payload fields are trusted after checking only `type`; storage failures can abort state transitions; and persistence tests live under the HTTP client.
**Expected Outcome:** A focused auth-session boundary validates and canonicalizes every browser-originated user/message payload, safely owns persistence and channel transport, and leaves `useAuth.ts` responsible only for state transitions. Invalid browser data cannot create an identity, valid legacy user records migrate deterministically, channel tokens force backend identity confirmation, and unavailable browser facilities do not block in-memory auth changes.
**Target-Perspective Output:** A returning user either receives the same canonical cached identity and cross-tab synchronization or cleanly falls back to the existing refresh/login flow. Cross-tab token hints cannot pair with an unverified cached/channel user to bypass `/auth/me`; malformed traffic never produces a stale or privileged protected UI identity; and login, refresh, and logout keep working when storage/channel APIs throw.
**Truth Owner:** Generated `ApiSchemas['User']`, exposed through `shared/auth/types.ts`, remains the compile-time HTTP user contract. New `shared/auth/authSessionBoundary.ts` owns runtime browser-data decoding, canonicalization, the legacy stored-user migration, auth storage keys, safe storage operations, and validated BroadcastChannel transport. `useAuth.ts` owns Zustand state transitions plus semantic `beginAuthConfirmation` (token + `user:null`, broadcast) and `confirmAuthSession` (verified user, no broadcast) transitions. Backend cookies, token validation, session records, and `/auth/me/` remain authorization truth; `Protected.tsx` brackets `/auth/me/` with those transitions.
**Contract Boundary:** `localStorage` / storage events / BroadcastChannel -> `authSessionBoundary` runtime validation -> `useAuthStore` -> `Protected`, HTTP retry, navigation, and feature consumers.
**Cutover:** Atomically move all auth browser I/O and message decoding from `useAuth.ts` into the boundary module, route store reads/writes/subscriptions through that owner, add begin/no-echo-confirm transitions around the existing refresh-plus-`/auth/me/` path, use no-echo confirmation for the token-present `/auth/me/` path, and move auth persistence tests out of `httpClient.test.ts` into dedicated boundary/store tests.
**Displaced Path:** Raw `JSON.parse(...) as User`, auth key constants, storage helpers, channel message declarations, direct localStorage mutations, and `event.data` trust in `useAuth.ts` are deleted. The HTTP client no longer owns auth persistence tests. No compatibility wrapper remains.
**Value Density:** Three tightly scoped production files and focused tests close a security-sensitive runtime trust gap, separate six responsibilities from the store, add a no-echo backend-confirmation seam at two existing call sites, preserve all other callers, and avoid adding further logic to the already 4,919-line dirty architecture checker.
**Acceptance Evidence:** Dedicated decoder, persistence, construction-failure, and store/channel integration tests; a same-origin two-page real-browser trace; existing HTTP retry tests; full frontend test/build/lint/dead-code checks; repository architecture/API/quality checks; exact protected-file hashes; and dirty-worktree preservation replay.
**Evidence Lane:** Pure runtime decoding cases, storage migration/removal cases, fake-channel transitions, throwing storage/channel construction and operation cases, a real-browser two-page ordering/synchronization trace, existing auth retry regressions, full frontend gates, repository gates, then POST/correctness/maintainability/verifier reviews.
**Kill Criteria:** No raw auth JSON cast or unvalidated channel data in production; no auth storage key or direct auth localStorage access outside the production boundary owner (auth-owned tests may seed/assert raw values without declaring another production key); no persisted access token; malformed stored-user events always clear stale auth while malformed channel messages never mutate auth state; no channel/refresh token can remain paired with an unverified cached user; protected children never render between token acquisition and `/auth/me/` confirmation; each received token hint causes at most one backend confirmation and successful confirmation emits no channel echo; no storage/channel exception aborts an in-memory transition; no auth persistence test remains under the HTTP client; no backend, generated-contract, automatic HTTP-retry-control-flow, existing-store-action, or unrelated UI-rendering change; no generic preference persistence reuse; and no architecture-checker growth in this slice.
**Architecture Slice:** Browser auth cache and cross-tab synchronization only. Server auth contracts, request validation, cookies, token algorithms, refresh control flow, routes, UI rendering, permissions, and feature persistence remain behaviorally unchanged.
**Plan Review Gate:** Requires PRE review before baseline capture or implementation.

## Outcome Contract

The canonical browser user is exactly:

```text
{ id: finite integer, username: string, email: string, is_staff: boolean }
```

- A legacy stored or channel user that is otherwise valid but omits `is_staff` migrates to `is_staff: false`.
- Unknown user fields are stripped when the canonical value is persisted or installed.
- Invalid JSON and invalid-but-parseable shapes are removed from storage and resolve to `null`.
- `session` and `access-token` messages require a string whose `trim()` has positive length; the original untrimmed token is installed so the boundary validates transport shape without silently rewriting credentials. A `session` message also requires a valid canonical user for rolling compatibility, but receivers never install or persist that channel-supplied identity. Both valid token-bearing message types set `user: null`, forcing frozen `Protected` logic through `/auth/me`. Unknown or malformed channel messages, including empty or whitespace-only tokens, are ignored.
- Only the canonical user may be stored. Access tokens remain memory-only, and the legacy access-token key is removed opportunistically.
- Browser storage/channel construction, reads, writes, removals, posts, and listener registration are best effort. Their exceptions do not abort an otherwise valid in-memory store transition.
- The public `AuthState` actions and existing consumers remain source-compatible. Separate `beginAuthConfirmation` and `confirmAuthSession` exports are used only by `Protected`: begin atomically installs the refreshed token with `user:null` and publishes the token hint; confirm installs/persists the verified identity without publishing a channel message.
- Each received token-bearing channel message may cause at most one backend confirmation in that page. Successful confirmation is never republished, so peers converge without an echo loop.

### Browser-event transition matrix

| Browser input | Store transition | External effect |
| --- | --- | --- |
| Stored-user event with canonical or migratable user | Clear the memory-only access token and install the canonical user | Rewrite the canonical user and remove the legacy token key |
| Stored-user event after removal, malformed JSON, or invalid-but-parseable shape | Clear both `accessToken` and `user` | Remove invalid user data and the legacy token key; existing `Protected` flow may refresh or redirect |
| Valid `session` channel message | Install its token and set `user: null`, forcing one `/auth/me` | Do not persist the channel-supplied user or token; successful confirmation uses `confirmAuthSession` and emits no message |
| Valid `access-token` channel message | Replace the memory token and set `user: null`, forcing one `/auth/me` | Persist no token; successful confirmation uses `confirmAuthSession` and emits no message |
| Valid `clear-session` channel message | Clear both `accessToken` and `user` | Remove stored user and legacy token |
| Malformed/unknown channel message | No state change | No persistence change |

## Architecture Map

### Files to create

- `frontend/src/shared/auth/authSessionBoundary.ts`
- `frontend/src/shared/auth/authSessionBoundary.test.ts`
- `frontend/src/shared/auth/useAuth.test.ts`
- `frontend/src/app/Protected.test.tsx`
- `docs/goals/auth-browser-state-boundary/PRE_SLICE_BASELINE.md`
- `docs/goals/auth-browser-state-boundary/EVIDENCE.md`

### Files to modify

- `frontend/src/shared/auth/useAuth.ts`
- `frontend/src/app/Protected.tsx`, limited to importing the two semantic confirmation helpers, replacing the refresh-path `setAccessToken` with `beginAuthConfirmation`, and replacing the two post-`/auth/me/` `setSession` calls with `confirmAuthSession`
- `frontend/src/shared/api/httpClient.test.ts`, limited to deleting the three auth-persistence/storage-event tests moved to the auth-owned suite and removing the stale non-contract `tier` field from its shared user fixture

### Files to avoid and preserve exactly

- `frontend/src/shared/auth/types.ts`, `authApi.ts`
- `frontend/src/shared/api/httpClient.ts` and generated API artifacts
- Auth forms, Settings, navigation, admin UI, and all other `Protected.tsx` behavior
- `frontend/src/shared/utils/persistentState*`, preferences, challenge caches, and other persistence utilities
- Backend accounts/services/models/routes/security settings
- `scripts/checks/check_architecture_boundaries.py` and its algorithm tests
- All unrelated dirty-worktree entries from Slices 1–9

### Read path

`stored user / storage event / channel message -> authSessionBoundary decode + migration -> useAuthStore state -> existing bootstrap/UI consumers`

### Write path

`existing login/password change/logout -> useAuthStore action -> immediate in-memory transition -> safe canonical user persistence + legacy cleanup -> validated channel publish`

`received token hint or refreshed token -> begin/user:null -> Protected /auth/me -> confirmAuthSession -> canonical memory/persistence update with no channel echo`

### Integration points

- Generated `User` alias for compile-time exhaustiveness.
- Browser localStorage and `storage` events.
- Browser BroadcastChannel transport.
- Existing login/register/password-change/automatic-HTTP-refresh/logout callers through source-compatible store actions; Protected's refreshed token through `beginAuthConfirmation`; and its two `/auth/me/` successes through `confirmAuthSession`.

### Migration/cutover

No database or server migration exists. The only migration is a browser-cache normalization: a missing `is_staff` becomes `false`; unknown fields are stripped; malformed records are removed. The cutover is atomic because `useAuth.ts` stops owning browser I/O in the same change that the new boundary takes ownership.

## Task Board

### Task 1: Capture the approved pre-slice boundary

- **Owner:** Main agent.
- **Files allowed:** New `PRE_SLICE_BASELINE.md` only.
- **Output:** Full dirty manifest; bytes/non-empty-lines/SHA-256 for existing planned targets; absence records for new files; exact hashes for protected auth/API/UI/persistence/checker files; and pre-change behavioral probes documenting valid, legacy, malformed-JSON, invalid-shape, storage-event, and access-token-persistence behavior.
- **Verification:** Recompute every recorded hash and reparse the manifest before implementation.
- **Acceptance evidence:** Planned mutable targets and protected entries are mechanically distinguishable, including a frozen 4,919-line architecture checker.
- **Depends on:** PRE approval.
- **Parallel safe:** No.

### Task 2: Establish the runtime browser-state owner

- **Owner:** Main agent.
- **Files allowed:** New `authSessionBoundary.ts` and its focused test.
- **Output:** A generated-type-checked canonical user decoder; explicit legacy migration; validated channel-message decoder; safe storage/key operations; safe channel creation/post/subscription; and focused tests for every valid, legacy, malformed, extra-field, and throwing-browser-API branch.
- **Verification:** Dedicated Vitest file, TypeScript build, lint, and mutation-style negative cases for wrong primitives, arrays, partial users, fractional/non-finite/wrong-type IDs, wrong field types, empty and whitespace-only tokens, unknown message types, browser-environment construction failures, and operation exceptions. Auth-owned tests may use the boundary's exported key constants to seed/assert raw storage without duplicating literal key ownership.
- **Acceptance evidence:** All browser-originated values become canonical typed values or are rejected; no second handwritten `User` type exists.
- **Depends on:** Task 1.
- **Parallel safe:** No.

### Task 3: Cut the store over and relocate owned tests

- **Owner:** Main agent.
- **Files allowed:** `useAuth.ts`, the import and three auth-transition calls in `Protected.tsx`, new `useAuth.test.ts`, new `Protected.test.tsx`, deletion-only movement of three persistence/storage-event cases from `httpClient.test.ts`, and removal of that test file's stale non-contract `tier` fixture field.
- **Output:** Store orchestration exclusively uses the boundary API; valid local actions update memory before best-effort external effects; stored-user removal/malformed/invalid events clear already-authenticated state; malformed channel messages leave already-authenticated state unchanged; valid token-bearing channel messages and Protected refresh both clear user state before `/auth/me`; `confirmAuthSession` installs verified results without publishing; dedicated integration/component tests prove hydration/migration, the full transition matrix, no pre-confirmation protected render, session/token/logout synchronization, no token persistence, bounded confirmation/no echo, and failure tolerance; HTTP retry tests retain only HTTP behavior.
- **Verification:** Dedicated store tests, a delayed/rejected-`/auth/me/` Protected component test, and existing `httpClient.test.ts`; a same-origin two-page browser trace that exercises actual storage/BroadcastChannel ordering for session, token refresh, malformed traffic, and logout, then asserts token acquisition keeps `user:null`, final state, and no further messages or `/auth/me/` calls after convergence; static search for displaced code; compile/lint/dead-code gates.
- **Acceptance evidence:** Existing store actions remain source-compatible and automatic HTTP retry behavior is unchanged; malformed browser data cannot install an identity or token; malformed stored-user events clear state; malformed channel messages do not mutate it; no channel/refresh token bypasses backend identity confirmation; protected children stay hidden during pending/rejected confirmation; and confirmation traffic reaches a bounded quiescent state.
- **Depends on:** Task 2.
- **Parallel safe:** No.

### Task 4: Prove cutover, preservation, and review closure

- **Owner:** Main agent.
- **Files allowed:** New `EVIDENCE.md`; implementation files only for attributable review fixes.
- **Output:** Test/check matrix, target-perspective browser-state traces, displaced-path searches, planned-target hashes/diffs, protected hashes, ordinary-manifest replay, and review closure.
- **Verification:** Dedicated and full frontend tests; build, ESLint, Knip; architecture/API/docs/quality checks; `git diff --check`; PRE-vs-POST preservation script; POST alignment, correctness, maintainability, and independent final verification.
- **Acceptance evidence:** Every outcome and kill criterion is reproducible from committed commands/results, with all unrelated dirty entries byte-identical.
- **Depends on:** Tasks 1–3.
- **Parallel safe:** Review lanes may run after implementation is coherent; implementation remains main-agent owned.

## Forbidden Moves

- Do not treat cached browser identity as authorization truth.
- Do not persist access tokens or introduce another browser key.
- Do not import the generic preference persistence helper into auth.
- Do not weaken the generated `User` alias or add a parallel DTO/schema type.
- Do not change `httpClient`, auth endpoints, cookies, token/session services, permissions, or other UI consumers. In `Protected.tsx`, only the import, refreshed-token transition, and two post-`/auth/me/` transition calls may change; query/render/error behavior is frozen.
- Do not extend or refactor the architecture checker in this slice.
- Do not retain raw browser-I/O helpers in `useAuth.ts` as a fallback. Auth-owned tests may seed and inspect raw values through boundary-exported key constants; this does not authorize a second production key owner.
- Do not stage, normalize, discard, or overwrite unrelated worktree changes.

## Review Gates

1. PRE plan review before Task 1 or implementation.
2. POST alignment review after the implementation and evidence draft.
3. Correctness review focused on fail-closed decoding, in-memory-first failure tolerance, legacy migration, and unchanged refresh/logout behavior.
4. Maintainability review focused on one-owner boundaries, displaced paths, type exhaustiveness, API surface size, and test ownership.
5. Independent final verifier after all findings and evidence metadata are synchronized.
