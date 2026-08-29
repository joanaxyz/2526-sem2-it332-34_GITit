# Authentication and Session Success-Contract Ownership Implementation Plan

**Intent:** Give authentication/session success responses one exact backend owner and one generated frontend projection without changing security behavior.
**Current Behavior:** `accounts.views` assembles exact auth payloads, but `common.openapi` documents nested users as open dictionaries. The generated contract therefore loses the user shape, while `shared/auth/types.ts`, `authApi.ts`, and the HTTP refresh path manually repair it with handwritten DTOs and custom response generics.
**Expected Outcome:** Account-owned response serializers describe every auth success family exactly; generated OpenAPI and TypeScript carry those shapes end to end; public auth calls infer their responses directly; the circularity-safe HTTP refresh path references the generated refresh response.
**Target-Perspective Output:** An authenticated client receives the same JSON, cookies, status codes, rotation, and revocation behavior, while maintainers can trace every success response from `accounts.serializers` through generated operations without a handwritten response override.
**Truth Owner:** `backend/accounts/serializers.py` owns auth request and success-response schemas. `backend/accounts/views.py` remains the runtime assembler and security orchestration boundary. Token/cookie/session truth remains in existing account services.
**Contract Boundary:** `accounts` serializers -> account view annotations -> committed OpenAPI -> generated `ApiSchemas`/operation responses -> `shared/auth` aliases and `authApi` consumers.
**Cutover:** Move the four auth-only success serializers out of `common.openapi`, name the user-bearing responses for their actual roles, regenerate, derive the frontend user alias, delete response aliases and custom generics, and type the internal refresh retry from `ApiResponseBody<'auth_refresh_create'>`.
**Displaced Path:** Open nested-user dictionaries, common-owned auth response serializers, handwritten `User`/`AuthResponse`/response repair aliases, custom auth response generics, and the handwritten low-level `{ access: string }` refresh response are deleted rather than shimmed.
**Value Density:** Four small success families cover ten security-critical operations and remove two open-object schema lies, two manual DTO owners, ten response overrides, and one low-level duplicate shape.
**Acceptance Evidence:** Real trusted-client requests prove exact register/session/access/user/detail/null responses plus unchanged refresh-cookie/session effects; generated artifacts prove exact components and operation references; frontend compile/tests prove inferred consumer types; preservation replay proves no unrelated dirty-worktree drift.
**Evidence Lane:** Fresh database API traces and focused contract tests; full account/security regressions; HTTP retry tests; generated-contract parity/attribution; frontend build/test/lint/dead-code gates; strict hash preservation; independent review/verifier gates.
**Kill Criteria:** No auth success serializer remains in `common.openapi`; no auth nested user is open; no handwritten auth response DTO or custom response generic remains; no raw public auth client is added; the internal refresh path has exactly one explicit allowlisted role and uses the generated response; no duplicate backend/frontend contract owner survives.
**Architecture Slice:** Auth/session HTTP success contracts only. Persisted-user validation, request validation, error envelopes, token algorithms, cookies, throttles, routes, services, models, forms, navigation, and UI remain behaviorally unchanged.
**Plan Review Gate:** Requires PRE review before execution.

## Outcome Contract

The canonical success shapes are:

```text
User = {id, username, email, is_staff}
RegisterResponse = {user: User}
SessionResponse = {access, user: User}
AccessTokenResponse = {access}
DetailResponse = {detail}
logout/revoke-all = 204 / null
```

Operation ownership:

- register -> `RegisterResponse`;
- login and password change -> `SessionResponse`;
- refresh -> `AccessTokenResponse`;
- me -> `User`;
- password-reset request/confirm and revoke-others -> `DetailResponse`;
- logout and revoke-all -> `204` with no response body.

Runtime values, error responses, refresh-cookie options, lockout behavior, token rotation, session records, security-version invalidation, permissions, throttles, and status codes must not change.

## Architecture Map

### Files to create

- `backend/accounts/tests/test_auth_contract_api.py`
- `docs/goals/auth-session-success-contract-ownership/PRE_SLICE_BASELINE.md`
- `docs/goals/auth-session-success-contract-ownership/EVIDENCE.md`

### Files to modify

- `backend/accounts/serializers.py`
- `backend/accounts/views.py`
- `backend/common/openapi.py`
- `frontend/src/shared/auth/types.ts`
- `frontend/src/shared/auth/authApi.ts`
- `frontend/src/shared/api/httpClient.ts`
- `frontend/src/shared/api/generated/openapi.json`
- `frontend/src/shared/api/generated/apiTypes.ts`
- `scripts/checks/check_architecture_boundaries.py`
- `backend/common/tests/test_architecture_guard_algorithms.py`

### Files to avoid

- `backend/accounts/services/**`
- `backend/accounts/models.py`, migrations, URLs, authentication, settings, and permissions
- `frontend/src/shared/auth/useAuth.ts`
- `frontend/src/app/Protected.tsx`
- auth forms/error presentation, Settings, and navigation consumers
- HTTP retry algorithm/control flow beyond replacing its response type
- generator implementation and API operation helper implementation

### Source of truth

- Response schema: `backend/accounts/serializers.py`.
- Runtime assembly/security flow: `backend/accounts/views.py` plus unchanged account services.
- Browser request/response projection: generated operation types.

### Read path

`accounts.urls -> accounts.views -> account response serializer annotation -> OpenAPI -> generated operation response -> authApi/httpClient -> Zustand/UI consumers`

### Write path

Register/password/session writes continue through the existing `UserService`, `PasswordResetService`, `TokenService`, `TokenBlacklistService`, refresh-cookie helpers, and `SessionRecord` behavior. This plan does not change that path.

### Integration points

- drf-spectacular response annotations;
- deterministic API contract generator;
- `apiOperationRequest` inference;
- the circularity-safe raw refresh request inside `httpClient`;
- Zustand session consumers through the generated `User` alias.

### Migration/cutover

This is an atomic compile-time/schema cutover with no data migration. Generated component names change from misleading `AuthUserResponse`/`LoginResponse` to `RegisterResponse`/`SessionResponse`; HTTP JSON stays identical.

### Acceptance evidence gate

The slice is complete only when fresh real-route traces, exact serializers, exact generated components/operation references, direct frontend inference, HTTP refresh typing, preserved security regressions, and strict dirty-worktree replay all agree.

## Task Board

### Task 1: Capture the approved pre-slice boundary

- **Owner:** Main agent.
- **Files allowed:** New `PRE_SLICE_BASELINE.md` only.
- **Files forbidden:** All production/test/generated targets.
- **Output:** Current dirty manifest; hashes/bytes/non-empty lines for all targets; protected hashes for services/models/URLs/security settings/generator; pre-change runtime traces; pre-change OpenAPI/TypeScript lies; and these explicit shared-target modes: `common/openapi.py` may delete only the four named auth response class blocks, generated files may change only auth components/references and must reconstruct to their pre hashes when reverted, checker/tests are additions-only with current minimal/patience deletion counts frozen, clean planned targets are separately hashed, and all ordinary manifest rows remain byte-identical.
- **Verification:** Reparse the manifest and reproduce every hash.
- **Acceptance evidence:** A machine-checkable baseline distinguishing strict ordinary entries from planned mutable targets.
- **Depends on:** PRE plan approval.
- **Parallel safe:** No.

### Task 2: Establish account-owned exact success contracts

- **Owner:** Main agent.
- **Files allowed:** `backend/accounts/serializers.py`, import and `extend_schema` response-reference lines only in `backend/accounts/views.py`, `backend/common/openapi.py`, new focused auth contract test.
- **Files forbidden:** Account services/models/migrations/URLs/security configuration.
- **Output:** Exact `User`, `RegisterResponse`, `SessionResponse`, `AccessTokenResponse`, and `DetailResponse` serializers in `accounts`; view annotations import them locally; four displaced common serializers are deleted; every view class security attribute and method body outside schema decorators remains byte-identical.
- **Verification:** Focused new tests plus the complete `backend/accounts/tests` lane, including auth, password-security, and throttling tests; replay normalized view method bodies and class security attributes against the baseline.
- **Acceptance evidence:** Trusted-header real-route responses with exact key sets, serializer parity, refresh cookies, rotation/revocation, and unchanged error/status behavior.
- **Depends on:** Task 1.
- **Parallel safe:** No.

### Task 3: Regenerate and cut frontend response overrides

- **Owner:** Main agent.
- **Files allowed:** Generated OpenAPI/TypeScript, `shared/auth/types.ts`, `shared/auth/authApi.ts`, and the response-type line/import in `shared/api/httpClient.ts`.
- **Files forbidden:** `useAuth.ts`, `Protected.tsx`, forms, Settings/navigation, request helper/retry behavior.
- **Output:** Exact nested `User` references; `RegisterResponse`/`SessionResponse` operation projections; only generated request-payload aliases and generated `User` facade remain; all auth methods infer responses directly; internal refresh uses `ApiResponseBody<'auth_refresh_create'>`.
- **Verification:** API currency/usage/type-adoption checks, HTTP client tests, TypeScript build, focused auth UI tests or full frontend suite.
- **Acceptance evidence:** Compiler-visible inferred types at the actual Login/Register/Protected/Settings call sites with no adapter or custom response generic.
- **Depends on:** Task 2.
- **Parallel safe:** No.

### Task 4: Make one-owner enforcement durable

- **Owner:** Main agent.
- **Files allowed:** Shared architecture checker and algorithm tests, additions only under the preservation diff algorithm.
- **Files forbidden:** Existing unrelated rules/tests except reuse of generic provenance/alias helpers.
- **Output:** A compact auth ownership check enforcing canonical backend classes/fields, removal from common, exact frontend alias/API bodies, no secondary auth operation path/response owner, exact OpenAPI components and operation refs, and the single typed internal-refresh allowlist.
- **Verification:** Synthetic bypass and ordinary-consumer negative tests, all prior architecture tests, and the live checker.
- **Acceptance evidence:** Guards kill realistic alias/re-export/wrapper/raw-path bypasses while allowing `AuthState`, auth error presentation, component props, generated consumers, and the internal retry boundary.
- **Depends on:** Task 3.
- **Parallel safe:** No.

### Task 5: Prove cutover and preservation

- **Owner:** Main agent.
- **Files allowed:** New `EVIDENCE.md`; implementation files only for review fixes.
- **Files forbidden:** Unrelated worktree entries.
- **Output:** Runtime traces, generated semantic attribution, verification matrix, preservation replay, task hashes, and review closure. The replay separately proves common-file four-block deletion only, generated auth-only reconstruction, frozen minimal/patience guard deletion counts, clean-target planned deltas, protected hashes, and byte-identical ordinary manifest rows.
- **Verification:** POST plan review, correctness review, maintainability review, final verifier, docs current, diff hygiene, fast quality gates, proportional backend/frontend suites.
- **Acceptance evidence:** Independent verifier can reconstruct the pre-slice generated artifacts by reverting only auth components/references and can replay every strict/protected hash.
- **Depends on:** Tasks 1-4.
- **Parallel safe:** Reviews may run independently only after implementation is coherent; implementation remains main-agent owned.

## Forbidden Moves

- Do not change auth JSON values, errors, status codes, cookies, tokens, sessions, lockout, permissions, throttling, or routes.
- Do not import `authApi` into `httpClient` or create a circular dependency.
- Do not make `useAuth.ts` a runtime schema/migration project in this slice.
- Do not retain old DTOs as compatibility aliases.
- Do not put account-specific response truth back into `common` or a frontend component/store.
- Do not regenerate unrelated semantic contract changes.
- Do not normalize, discard, stage, or overwrite unrelated dirty-worktree changes.

## Review Gates

1. PRE plan review before Task 1 or implementation.
2. POST alignment review after implementation.
3. Correctness review focused on security behavior, response exactness, and runtime evidence.
4. Maintainability review focused on ownership, displaced paths, alias bypasses, false positives, and value density.
5. Independent final verifier after all findings and evidence metadata are synchronized.
