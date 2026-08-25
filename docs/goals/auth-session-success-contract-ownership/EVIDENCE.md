# Evidence: Authentication and Session Success-Contract Ownership

## Outcome

Slice 9 establishes one exact, generated success-contract path for authentication and session endpoints without changing runtime values, errors, status codes, cookies, token/session behavior, permissions, throttles, routes, services, models, or UI flows.

The final path is:

`Accounts response serializers -> existing Accounts views -> committed OpenAPI -> generated TypeScript operation responses -> authApi/httpClient -> existing Zustand/UI consumers`

The displaced path is gone:

- no auth response serializer remains in `common.openapi`;
- no nested auth user is an open dictionary/`JsonValue`;
- no handwritten `User`, `AuthResponse`, or auth response-repair alias remains;
- no public auth operation passes a custom response generic;
- the single circularity-safe raw refresh request derives its result from the generated refresh operation;
- no compatibility shim or second backend/frontend contract owner remains.

## Exact Contract

```text
User = {id, username, email, is_staff}
RegisterResponse = {user: User}
SessionResponse = {access, user: User}
AccessTokenResponse = {access}
DetailResponse = {detail}
logout/revoke-all = 204 with no body
```

Operation ownership is exact:

| Operation | Success contract |
|---|---|
| register | `201 RegisterResponse` |
| login | `200 SessionResponse` |
| logout | `204`, no body |
| refresh | `200 AccessTokenResponse` |
| me | `200 User` |
| password-reset request | `200 DetailResponse` |
| password-reset confirm | `200 DetailResponse` |
| password change | `200 SessionResponse` |
| revoke other sessions | `200 DetailResponse` |
| revoke all sessions | `204`, no body |

The canonical post-slice auth schema snapshot SHA-256 is `CFF4689790CE2F61330E7013F3F28800A2AE3EA688351C8CAE2C741E36BB0BBB`.

## Direct Runtime Evidence

The focused contract lane uses real DRF routes, trusted-web-client headers, the production views/services/serializers, and fresh pytest databases.

- Register returns exactly `{user}` and the nested user exactly matches `UserSerializer`.
- Login returns exactly `{access, user}`, emits the configured refresh cookie, and preserves the exact user projection.
- `me` returns exactly the four user fields.
- Password change returns exactly a new session response and invalidates the prior access token.
- Refresh returns exactly `{access}`, rotates the refresh cookie, creates the replacement session, revokes the previous session, and preserves the invalid-refresh `401 {detail: "Session expired."}` path without a response cookie mutation.
- Password-reset request returns the exact generic detail response.
- Password-reset confirm uses a real Django reset token and asserts the exact `200 {detail: "Password reset successfully. You can now sign in."}` response.
- Revoke-others returns the exact detail family.
- Logout and revoke-all return `204`/null and clear the configured refresh cookie.

The focused file has 4 passing tests. The complete `backend/accounts/tests` lane has 26 passing tests, including password security, lockout/throttling, cookie, token-version, and session regressions.

## Backend Ownership and Preservation

`backend/accounts/serializers.py` now owns the exact five-class family:

- `UserSerializer`
- `RegisterResponseSerializer`
- `SessionResponseSerializer`
- `AccessTokenResponseSerializer`
- `DetailResponseSerializer`

`accounts.views` only changed serializer imports and three response annotation references. An AST replay against the clean pre-slice file proves all 16 class security assignments and all 10 HTTP method bodies are unchanged. The recorded pre-slice security and method-body semantic hashes remain `63D8BF3084C94BFEBD18D1B1CC21973A2C8297CCDE476B8CCD0C61183E2FE720` and `855AF6CFB04D3FBFA1A76046AC684BEBD4BD33E856FC3503AC73C7617C0574B9`.

`backend/common/openapi.py` deleted only `DetailResponseSerializer`, `AccessTokenResponseSerializer`, `AuthUserResponseSerializer`, and `LoginResponseSerializer`. Its deterministic post-deletion result is exactly 7,733 bytes, 143 non-empty lines, SHA-256 `26B1D55DD56173270786C8368D4DFDB727365B82D5EFB39C8A1C605901B42313`.

All 12 protected service/model/URL/authentication/permission/settings/generator/store/UI files retain their pre-slice hashes.

## Generated Projection and Attribution

Generated TypeScript now contains:

```ts
"User": { "email": string; "id": number; "is_staff": boolean; "username": string }
"RegisterResponse": { "user": ApiSchemas["User"] }
"SessionResponse": { "access": string; "user": ApiSchemas["User"] }
"AccessTokenResponse": { "access": string }
"DetailResponse": { "detail": string }
```

The operation-response map references those schemas directly, and logout/revoke-all map to `null`.

The attribution replay reverses only the Slice 9 auth delta in memory:

- remove `RegisterResponse` and `SessionResponse`;
- restore the old open `AuthUserResponse` and `LoginResponse` components;
- restore the three register/login/password-change operation references.

That reconstruction reproduces the pre-slice generated artifacts exactly:

| Artifact | Reconstructed bytes | Reconstructed SHA-256 |
|---|---:|---|
| `openapi.json` | 199,069 | `2D1CDFC6DDA94F695C318E90A313FC802595DB5EAB168AF9952020874092B471` |
| `apiTypes.ts` | 43,991 | `34909CE955174E2AD6611641F9819AA2A0E98CBDD5CEC0B7F7C7A88EA6F37631` |

Both match the frozen pre-slice hashes. Contract-currentness, frontend API usage, and generated-type-adoption checks all pass.

## Frontend Ownership

`shared/auth/types.ts` now contains only the generated facade:

```ts
export type User = ApiSchemas['User']
```

`authApi` retains generated request-payload aliases, but every success response is inferred directly from `apiOperationRequest`. The old `AuthResponse`, `RegisterResponse`, `RefreshResponse`, and `DetailResponse` repair aliases and all ten custom response generics are deleted.

The internal retry boundary remains circularity-safe and changes only its response type:

```ts
apiRequest<ApiResponseBody<'auth_refresh_create'>>('/auth/refresh/', ...)
```

No import from `httpClient` back to `authApi`, retry control-flow change, `useAuth` storage change, or UI-consumer change was made.

## Durability

The architecture checker now enforces:

- one exact Accounts serializer family and exact field constructor signatures;
- exact success annotations for all ten Accounts views;
- no displaced auth serializer in `common.openapi`;
- no named, inherited, assigned, or neutral-name structural backend response shadow;
- only the generated `User` frontend alias and direct operation response inference;
- no generated-response-root alias, handwritten `{access, user}` shape, custom response generic, duplicate operation wrapper, or secondary raw auth client;
- no `authApi` object/member alias, export list, named/wildcard re-export, namespace-member wrapper, exported method object, response-forwarding function/arrow, `ReturnType` response alias, or constructed auth request path;
- response-forwarding provenance remains distinct from ordinary callbacks that consume auth responses and return `void`;
- bounded static-path resolution through identifier chains, `+` concatenation, and simple template interpolation;
- the one typed internal refresh allowlist;
- exact closed OpenAPI components, nested references, operation schemas, and bodyless `204` responses.

Six focused guard tests reject wrong field owners, backend name/inheritance/assignment/structural/re-export shadows, generated/manual/`ReturnType` response aliases, direct and indirect wrappers, exported method objects, named/wildcard/namespace re-exports, literal/bound/concatenated/template auth paths, open nested schemas, and wrong operation/204 shapes. Negative probes explicitly allow nullable `AuthState`, `AuthChannelMessage`, `AuthErrorProps`, ordinary response-panel/message/result state names, response-consuming `void` callbacks, and the real `Protected`/form consumers. The complete architecture algorithm lane is 37 passing tests, and the live checker is clean.

## Verification Matrix

| Gate | Result |
|---|---|
| Focused auth contract tests | 4 passed |
| Complete Accounts/security/throttling lane | 26 passed in 17.17s |
| Architecture algorithm tests | 37 passed in 52.49s |
| Live architecture checker | clean |
| Focused HTTP client tests | 8 passed |
| Full frontend Vitest suite | 67 files / 465 tests passed in 326.42s |
| Production TypeScript/Vite build | passed; 2,656 modules transformed |
| ESLint | passed |
| Knip/dead-code scan | passed |
| API contract current | passed |
| API wrapper usage | passed |
| Generated type adoption | passed |
| Ruff on all Slice 9 Python | passed |
| Fast quality gates | all 10 passed |
| Documentation currentness | passed after evidence synchronization |
| Diff hygiene | passed with only disclosed pre-existing CRLF warnings |

## Preservation Audit

The frozen dirty manifest reparses to 119 entries.

- Strict ordinary entries: 114 checked, 0 mismatches.
- Protected entries: 12 checked, 0 mismatches.
- `common.openapi`: exact deterministic four-block deletion hash reproduced.
- Generated artifacts: exact pre-slice hashes reconstructed by reversing only auth components and three operation references.
- Shared guard files remain additive under both minimal and patience diff algorithms:
  - checker: `4480 + / 2 -` (frozen deletion count `2`);
  - algorithm tests: `1694 + / 0 -` (frozen deletion count `0`).
- `accounts.views` security assignments and HTTP method bodies remain semantically identical.
- `git diff --check` passes; it reports only pre-existing line-ending notices for a curriculum seed file and generated `apiTypes.ts`.

Current task-file hashes after POST hardening:

| Path | Non-empty lines | Bytes | SHA-256 |
|---|---:|---:|---|
| `backend/accounts/serializers.py` | 71 | 3,669 | `4C0992166F52CDAB966461ECCC3BB5D287C926C6C10DFA33E1DF43A68015480E` |
| `backend/accounts/views.py` | 195 | 8,707 | `67C8782706E7A774F4DCD3F09FD5BFB98AECBE137680EF9418F7065A65CE6517` |
| `backend/common/openapi.py` | 143 | 7,733 | `26B1D55DD56173270786C8368D4DFDB727365B82D5EFB39C8A1C605901B42313` |
| `backend/accounts/tests/test_auth_contract_api.py` | 175 | 7,669 | `079C3CEAACD9DAC4880769D82C21650868714C376430E16511D81E53F5A21739` |
| `frontend/src/shared/auth/types.ts` | 2 | 105 | `AB1711BF58E58130560D7775EA720B96743B4B02B33132CFFED5C0EFEFE2DAD4` |
| `frontend/src/shared/auth/authApi.ts` | 58 | 2,103 | `A8B39E86686A0281291AD81B3C058CB9B2A93742A63F5C39DADA9CCC1B6D97A8` |
| `frontend/src/shared/api/httpClient.ts` | 143 | 5,453 | `EA0CC2B4BBBBB7ADA9E6D3AFDAF4564769CE428A6F7F8C239D69838FBD16702C` |
| generated `openapi.json` | 5,732 | 199,009 | `11AFC8265CD0201952079F8B7F78B98AE4E2C5127E8D1B52DB349954A40E9EE8` |
| generated `apiTypes.ts` | 490 | 43,977 | `6FDAAB9D163FBDE8AFC695D84FFE3E510B814D24BDA67F280EE7EF057F89DE14` |
| architecture checker | 4,527 | 187,011 | `53814BE32D540A9C4AD360470B7E2A2359B71433B65B2141969BB80FE5ECB169` |
| architecture algorithm tests | 1,565 | 76,454 | `949FCA4E22082821D3AA8E4D334749C97262193B13C13E948B7153BB1402064F` |

## Review Closure

| Gate | Verdict | Findings |
|---|---|---|
| Krypton POST plan review | ALIGNED | Initial backend/frontend provenance gaps and missing reset-confirm body evidence were fixed; final adversarial re-review found no actionable issue |
| Correctness review | PASS | No blocker/major/minor; independently confirmed exact runtime contracts, unchanged security flow, generated mappings, type-only refresh diff, 26 Accounts tests, build, and 8 HTTP tests |
| Maintainability review | PASS | Review-driven backend structural/re-export and frontend alias/wrapper/path/false-positive probes were closed; final review found no blocker/major/minor |
| Independent final verifier | PASS | No blocker/major/minor; independently reproduced all requested tests, generated reversal, strict/protected hashes, view semantics, task hashes, and minimal/patience numstats |
