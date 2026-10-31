# Independent post-hardening audit

Date: 2026-10-31 (Asia/Manila). Base commit:
`4122bf3effeb7889299aac4d507932879de773da`.

Scope: source inspection, isolated backend/frontend checks, local Chromium media
requests, official hosting/provider documentation and read-only GitHub Actions
results. No production probes, load tests, dashboard changes, deployment, secrets,
billing, commits or pushes. Pre-existing sprite, playground, router, asset-script
and document edits are outside this audit.

## 1. Correctness and prioritized findings

The scoped architecture is technically sound for best-effort usage admission.
It does not provide exact concurrent admission, a financial cap, or proof of
deployed proxy identity. Two confirmed defects were corrected below. No Critical
or High code defect was found in the reviewed paths.

| Severity | Finding | Evidence / disposition |
| --- | --- | --- |
| Medium, fixed | Muted screen entry eagerly requested 42 possible audio files. | Original module reproduced in local Chromium with both stored channels off: 42 media requests, 7,101,996 recorded encoded body bytes (background range timings can under-report bytes). Corrected module: zero media requests while muted. |
| Low, fixed | Earlier model errors could mask a shared budget failure. | A model's 25-second 429 followed by a 3,600-second budget exhaustion returned a 25-second retry. A preceding 503 could classify exhaustion as ordinary unavailability. Budget diagnostics now take priority when no admitted attempt succeeds; provider cooldowns remain separate. |
| Medium, deployment gate | Vercel egress or an unrecognized Render proxy may aggregate anonymous users. | The helper deliberately stops at the first untrusted address. Source tests establish this behavior, not the actual deployed forwarding chain. Preserve trust restrictions and verify privately. |
| Medium, operational | Ordinary rate limits and failed-login cache counters pause during Redis failure; Free Key Value restarts lose counters. | Intentional availability policy. Enabled provider budget fails closed during cache errors; restart/flush still resets its in-memory state. Provider limits remain essential. |
| Medium, operational | Thirty learners can collectively exceed provider quotas or occupy all request threads. | Blueprint: one worker, eight threads; provider waiting is synchronous in each Django request. Thirty users are not thirty simultaneous provider slots. No capacity result is claimed. |
| Low, policy | The 200/day tutor allowance can charge requests that make no provider call. | DRF counts before validation, recognition and memo lookup, and evaluates all throttle classes even if another refuses. Keep the documented policy pending actual workshop demand. |
| Informational | Public Render access, invalid-auth traffic, distributed bots, public liveness and Django admin remain outside some application scopes. | Established limits of application throttling. No evidence of an active attack; edge rules are not assumed configured. |

## 2. Counter ownership, boundaries and student experience

The default classes run authenticated-general, scoped, then tutor-daily policies.
`AuthenticatedRateThrottle` uses user PK with no anonymous fallback. Scoped DRF
policies use user PK for authenticated requests and `get_client_ip()` otherwise.
Login explicitly forces IP even if a valid JWT is supplied. Refresh/logout/OAuth
start and callback disable JWT authentication as required for their cookie and
redirect flows. Existing authentication and permissions precede throttles;
object ownership checks still precede mutations/provider work in their handlers.
Invalid JWTs and permission denials are therefore not counted by DRF scopes.

| Policy | Assessment for 30 students |
| --- | --- |
| General 300/min per user | Independent accounts cannot consume one another's bucket; applies in addition to narrower scopes. |
| Commands 120/min per user | Two commands/sec; includes workspace file mutations and introductions. Ordinary human practice has substantial headroom. |
| Start/retry 60/min per user | One new run/sec across adventure/challenge starts and retries. No change to attempts, pedagogy, scoring, rewards or completion. |
| Tutor 12/min + 200/day per user | Five seconds between questions on average at sustained burst capacity. 200 is 16m40s at 12/min, 3h20m at one/min, or 6h40m at one every two minutes. Rolling 24h, not midnight reset. Adequate for a typical short demonstration; potentially restrictive for an intensive all-day workshop. |
| Login 120/min per source | 30 initial password sign-ins fit with retry headroom. Five failures/300s lockout uses identifier + source, so one learner's mistakes do not lock different accounts. |
| Register 60/hour; reset request 20/hour per anonymous source | Pre-create/verify demonstration accounts. A whole class of 30 requesting reset within an hour exceeds 20 if they share a source identity. Do not weaken without measuring actual need. |
| Refresh 600/hour per source | 30 users refreshing every 15 minutes is about 120/hour with one tab each; bootstraps, reloads and multiple tabs add requests. |
| OAuth 120/hour shared source | Start + callback + ticket exchange normally cost three admissions: 30 sign-ins use 90, leaving 30 for retries/other users. Repeated whole-class OAuth sign-in within the same hour can exceed it. |
| Readiness 120/min; metadata 60/min per source | `/api/health/` and `/ready/` share readiness; docs/schema share metadata. Use unthrottled dependency-free `/api/health/live/` for Render health checks. |
| Password/security scopes | 10 password changes/hour and 30 session-management actions/hour per authenticated user; appropriate for occasional actions. |

DRF histories expire with the policy duration, prune timestamps at the boundary,
and refresh cache TTL on successful admission. A rejected request does not extend
its own full bucket, but can occupy another bucket that accepted it. `Retry-After`
and JSON `retry_after_seconds` use DRF's rounded-up maximum wait across refusing
policies; login retains its legacy `retry_after` field. Tutor preserves its
friendly error shape. Ordinary counters use non-atomic get/update/set, so races
can overshoot; this documented DRF limitation is not an exact security boundary.

## 3. Proxy interpretation and safe verification

`REMOTE_ADDR` must first parse as an IP and belong to an explicit trusted CIDR.
Only then is X-Forwarded-For walked from right to left, skipping configured proxy
addresses and choosing the first untrusted one. Malformed boundaries and entirely
trusted chains fall back to the peer. Untrusted direct peers cannot select an
identity through headers. X-Real-IP and X-Vercel-Forwarded-For are ignored.

The Blueprint trusts all RFC1918 ranges plus loopback, CGNAT `100.64.0.0/10` and
IPv6 ULA `fc00::/7`. These are broad infrastructure assumptions, not proof that a
given hop is Render. Narrow only using verified platform peer/chain information;
no CIDRs were added or changed. Never add all-public ranges or arbitrary Vercel
egress ranges simply to walk past an observed address.

Vercel documents replacement of incoming X-Forwarded-For to resist spoofing.
Render documents using X-Forwarded-For behind its edge. Neither establishes the
exact chain received by this application's external rewrite. Aggregation is a
plausible deployment risk, not a verified incident. See the official
[Vercel request-header documentation](https://vercel.com/docs/headers/request-headers)
and [Render edge guidance](https://render.com/articles/how-render-handles-ddos-attacks).

Manual procedure, before tightening anonymous limits:

1. In access-controlled infrastructure logs or a temporary staff-only diagnostic,
   capture request ID, path, direct peer, raw forwarded chain and helper-selected
   IP for a few controlled requests. Exclude cookies, Authorization and tokens.
   Do not create a public echo endpoint.
2. Use school Wi-Fi and a separate cellular connection. Send one ordinary request
   from each through Vercel and directly to Render; compare all four chains.
3. Repeat with a synthetic X-Forwarded-For prefix, e.g. `203.0.113.77`. It must not
   change the selected verified boundary. An all-trusted or malformed chain must
   fall back, not skip an invalid address.
4. If unrelated networks still select one Vercel/Render egress IP, retain that
   conservative identity. Request precise platform guidance before changing trust.
   Confirm per-user gameplay remains independent. Remove diagnostic logging.

## 4. AI attempt accounting, quotas and the daily allowance

`provider_transport._post_json()` reserves immediately before **every** HTTP send
and again before its single stale-connection retry. Embeddings use this same
transport. Gemini models, Groq fallback, hedges and guarded rewrites also use it.
Reservations use atomic add/incr through the strict `provider_budget` alias on the
same Redis. Admission runs off the event loop within the request deadline.
Cancelled/failed admissions can consume reservations without an HTTP send;
there are intentionally no refunds. Exhausted reservations can keep incrementing
the denied counter until its expiry but cannot authorize another send.

`TUTOR_PROVIDER_DAILY_LIMIT=0` remains disabled. An enabled counter expires at
UTC midnight (08:00 Manila), independently of provider reset schedules. Cache
connection/write errors, missing counters during increment, or unusable values
block provider sends. No retry goes through an unbudgeted alternate path.
Redis restart/flush loses this request allowance, which is not a durable ledger.

These quantities must remain distinct:

- Student chat requests: subject to general, burst and daily DRF admission.
- Reply memo hits: no generation call, but recognition runs first and may need an
  embedding if its separate memo is missing. Do not promise every cache hit is
  zero provider traffic.
- Scenario refusal: a lexical match can return with zero calls; semantic
  recognition can first spend one embedding batch. Guarded text is rechecked
  before reuse, and unsafe drafts can trigger a second generation chain.
- Outbound attempts: embedding batches, generation, retries and concurrent losing
  hedges count individually even when the learner receives one reply or none.
- Tokens, money and provider quotas: not inferred from reservations. A batch can
  contain several texts, prompts vary in length, losing/cancelled calls may still
  be billable, and provider cached-token rules differ from application memo hits.

No refund scheme or provider-only per-user daily quota was added. Charging only
provider work would require reliable per-user attribution across recognition,
memo races, rewrites, fallback and hedging; it would still need the request burst
limit. The existing policy bounds handler/retrieval/cache work too. For a long
workshop, first measure per-user accepted requests, cache/guard outcomes and 429s;
adjust the existing `THROTTLE_TUTOR_CHAT_DAILY` setting only against that demand.
The request cap does not establish a 200-call or monetary allowance.

DRF admission failures are HTTP 429 with header/JSON timing. Provider or shared
budget failures retain the existing HTTP 200 chat contract with
`response_kind=unavailable`, a reason and retry timing when rate-limited. The
frontend handles both forms and keeps the question for explicit retry.

Before enabling a global budget, the operator needs the exact model IDs and
project/organization tied to each credential, available embedding/generation
RPM/RPD/TPM/TPD, reset time, current consumption by other apps, input/output token
sizes, class duration and questions/student, cache-hit rate and physical attempts
per question under healthy and fallback conditions. Gemini quotas are project
scoped; Groq quotas are organization scoped. Obtain active account values, not a
generic published free-tier table. Sources:
[Gemini limits](https://ai.google.dev/gemini-api/docs/rate-limits),
[Groq limits](https://console.groq.com/docs/rate-limits).

Sizing approach: demand = learners × planned questions/learner × measured
physical attempts/question, then choose explicit headroom compatible with actual
quotas and provider budget controls. For illustration only, 30 × 30 × 3 = 2,700
reservations before headroom; none of these usage assumptions has been measured
in this deployment. A combined daily cap cannot enforce each model's minute or
token quota, and its UTC reset need not match the provider day. Keep `0` until
those inputs are known; configure existing provider alerts/limits without
changing plans. Do not sum model quotas and assume the resulting total is safe.

## 5. Vercel protection and avoidable resource use

The Vite build remains static; `/api/*` uses the existing external rewrite with
no new Function. Both proxy configuration and Django middleware declare private
no-store API responses, including errors/redirects. External rewrite caching is
explicitly disabled. This matches current
[Vercel rewrite documentation](https://vercel.com/docs/routing/rewrites).
Same-origin cookies and OAuth routing are preserved.

The documented 6,000 requests/60s per-IP `/api/` rule is a reasonable initial
coarse classroom safety net **after observation**, not a spend or per-user cap.
It allows an average 200 API requests/minute for each of 30 classmates behind
one IP. Thirty accounts at their general maximum can reach 9,000/minute before
anonymous traffic, so 6,000 does not guarantee the full application envelope.
Fixed-window boundaries and region-local counters can allow higher totals.
Do not lower it based on conjecture or assume it is already published.

Manual Vercel setup (operator action only):

1. Project → Firewall → Configure → New Rule. Inspect existing ordering/bypasses
   and rule allowance first. Name `api-source-safety-net`.
2. Condition: Request Path starts with `/api/`. Action: Rate Limit. Strategy:
   Fixed Window; window: 60 seconds; request limit: 6,000; counting key: IP.
   Follow-up: Default (429). Do not challenge fetch requests with HTML.
3. Review the rate-limiting pricing dialog and included allowance. Proceed only
   within existing free availability; do not change plans or enable paid usage.
   Use Log first if offered, then compare normal classroom peaks before 429.
4. Review Changes → Publish only after the operator accepts that configuration.
   Firewall traffic grouping → select the rule → inspect matched/limited paths
   and IPs. Use a few normal login, refresh, tutor and command requests.
5. Test enforcement with a reduced threshold on an isolated preview/test project
   within the existing allowance, then restore it. Never generate 6,001 requests
   against production. Check for an actual HTTP 429 and absence of an HTML
   challenge. Edge responses need not have Django's JSON or retry headers.

Current docs list one Hobby rate-limit rule and region-local counting. Rule and
traffic availability must still be checked in the account. See
[Vercel WAF rate limiting](https://vercel.com/docs/vercel-firewall/vercel-waf/rate-limiting).
The rule does not protect direct Render traffic or static asset transfer.

Residual usage: API hits still consume Vercel routing and Render CPU/threads,
Supabase queries and Redis operations even when responses are not AI-generated.
CDN hits still serve bytes/edge requests. Enabled audio still warms 40 effects
for timing; narrowing them to one companion/encounter could save more but would
require encounter-aware ownership and timing verification. No speculative
refactor was added. Provider cache loss, concurrent identical misses, hedging
and guard rewrites can cause extra AI usage; their costs need actual metrics
before adding locks or reducing fallback responsiveness.

## 6. TTL and cache review

| Data | Current behavior | Assessment |
| --- | --- | --- |
| Ordinary throttle histories | Rolling duration, successful-write TTL equals policy window | Correct best-effort expiry; no TTL extension on that policy's refusal. |
| Provider attempt budget | UTC-day key, TTL until next midnight | Atomic admission with conservative expiry-race failure; not durable across Redis resets. |
| Tutor reply / recognition memo | 24 hours; reply keyed by full system/turns, recognition by corpus hash/text | Reply guard reruns before reuse; scenario corpus changes invalidate recognition. Server cache only, not a shared HTTP cache. |
| Provider cooldown | 429 Retry-After clamped 1–86,400s; transient failures 10s; slow model 120s | Separate model + credential hash keys; budget exhaustion does not poison them. |
| OAuth tickets / state | 120s single-use cache ticket; signed state max-age checked | Redis loss fails redemption safely; cache loss does not create a valid login. |
| Token revocation | Cache TTL only until refresh-token expiry | PostgreSQL sessions remain truth; cache miss/outage falls back to DB; DB uncertainty fails closed. |
| React Query | 30s freshness; no focus refetch; no automatic 4xx retry; one network/5xx retry | Account transitions create/clear separate clients; refresh is single-flight with one 401 retry; tutor retry is explicit. |
| Hashed `/assets/` | 1 year immutable | Appropriate content-addressed URLs. |
| Mutable audio/cosmetics/mascot/email/cursors | 1 day + 1 week stale-while-revalidate | Existing caching reduces repeat transfer, not a new browser's cold downloads. Replacement at the same URL can be stale; use versioned URLs when freshness is required. |
| HTML | Revalidate; deep SPA routes retained | Confirm served headers after deployment; no claim from local Vite about CDN behavior. |
| Personalized API | private, no-store at origin and proxy; rewrite caching off | No shared API HTTP caching; verify both origins after deployment. |

## 7. Changes in this follow-up

| Files | Reason |
| --- | --- |
| `frontend/src/shared/audio/battleAudio.ts` | Gate effect warm-up on preference; defer muted background construction while retaining current screen; load only active music loop and resume correctly on enable. |
| `frontend/src/shared/audio/battleAudioLoading.test.ts` | Muted request prevention, latest-screen unmute, stop-before-unmute and enabled effects warm-up. |
| `frontend/src/app/providers.test.tsx` | Explicitly prove React Query does not automatically retry HTTP 429. |
| `backend/tutoring/services/providers.py` | Preserve shared budget diagnostics over earlier unrelated model failures. |
| `backend/tutoring/tests/test_recovery.py` | Mixed 429/503 and budget-exhaustion/outage regressions. |
| `backend/tutoring/tests/test_budget.py` | UTC-midnight reservation TTL, outage recovery, expiry-race fail-closed checks and physical accounting across embeddings, fallback and overlapping hedges. |
| `backend/common/tests/test_throttles.py` | Thirty student daily-counter independence, rolling expiry and auth/permission ordering. |
| `deploy/RATE_LIMITING.md`, this report | Link follow-up evidence, correct the obsolete audio caveat, document deployment and quota decisions. |

No production rate defaults, trusted proxies, TTLs, scoring, learning services,
RAG/answer guard, architecture or provider budget enablement were changed.

## 8. Verification evidence

Local checks executed in this audit (SQLite/LocMem test settings; provider HTTP
mocked, never real AI calls):

| Check | Result |
| --- | --- |
| Backend account/common/tutor/adventure/challenge/drill/progress suite | 786 passed, 1 skipped in 438.17s. |
| Final focused throttle/budget/recovery checks | 48 passed, 1 skipped; final budget-only run also passed (13 passed, 1 skipped). |
| Full frontend Vitest run | 1,432 passed, 178 files. |
| Final frontend audio/API/session/tutor/Query focused run | 120 passed, 9 files, including new audio cases and explicit 429 retry assertion. |
| Production TypeScript/Vite build | Passed. |
| Frontend ESLint and knip | Passed. |
| Backend Ruff lint / format | Passed; all 474 formatted files checked. |
| Architecture, API contract and wrapper/type-adoption guards | Passed. |
| Documentation, CI quality manifest, Render Blueprint, runtime assets | Passed; 379 asset references checked. |
| Django production deployment/runtime configuration checks | Passed. |
| Local Chromium original/fixed media test | Original: 42 requests while muted; fixed: 0 media elements and 0 requests. Unmute: one outside loop playing at readyState 4; move to battle and enable effects: 40 effects plus two visited music elements, only inside loop playing; no browser errors. |

Initial sandboxed backend execution encountered failures/stalls and was stopped;
Windows asyncio/provider transport needs an internal socket. The focused rerun
outside the sandbox passed. A sandbox API-contract run also failed to write its
temporary schema; rerunning with `TEMP`/`TMP` under workspace `.tmp/audit-temp`
passed. These were execution-environment problems, not successful test runs.
The one focused skip requires real Redis, which was not started locally.
Container builds, migrations on fresh PostgreSQL, dependency audits and generated
target replays were not repeated locally in this follow-up.

Commands used for the main checks:

```powershell
# From backend, with TEMP/TMP set to workspace .tmp/audit-temp.
.venv/Scripts/python.exe -m pytest accounts/tests common/tests tutoring/tests adventures/tests challenges/tests drills/tests progress/tests -q --tb=short
.venv/Scripts/python.exe -m pytest common/tests/test_throttles.py tutoring/tests/test_budget.py tutoring/tests/test_recovery.py -q --tb=short
.venv/Scripts/ruff.exe check .
.venv/Scripts/ruff.exe format --check .

# From frontend.
npm test -- --reporter=dot
npm test -- --reporter=dot src/shared/audio src/shared/api src/shared/tutoring src/app/providers.test.tsx
npm run build
npm run lint
npm run lint:dead
```

The existing commit's [CI run 182](https://github.com/joanaxyz/2526-sem2-it332-34_GITit/actions/runs/41174642517)
was fetched through GitHub read-only on 2026-10-31: `quality-gates`, `frontend`,
`production-integration`, `generated-targets` and `container-images` all completed
successfully. Step results confirm dependency audits, PostgreSQL/Redis coverage,
clean migrations, generated replays and container smoke checks ran there. This
is evidence for the base commit, not CI execution of the uncommitted follow-up.
Fetched integration logs report **1,119 passed, 53 skipped, 90% coverage**; skipped
tests are not represented here as executed successes. Expected constraint-test
database errors in service logs do not make the successful CI job a failed run.

## 9. Required deployment verification

1. Confirm deployed release and actual env rates against settings/Blueprint.
   Confirm Redis is shared, internal-only, `noeviction`, and ordinary ignored
   exceptions are logged. Check readiness once; retain liveness for health checks.
2. Check the private proxy chain procedure above, including spoofed prefixes.
   Do not infer browser independence from a successful login alone.
3. Sign in as two test accounts on the same school network. Exercise a scenario,
   retry and validate commands normally; verify separate account responses.
   In a test environment, lower a scope, verify matching 429 JSON/header and
   recovery after expiry. Do not exhaust real production limits.
4. Verify OAuth callback → ticket exchange → refresh cookie → reload → logout,
   on the Vercel origin. Cookie: Secure, HttpOnly, SameSite=Strict, host-only,
   `/api/auth/`. Pre-create/verify class accounts and budget OAuth/reset traffic.
5. Fetch personalized API responses through both routes: private/no-store, no
   shared CDN HIT, independent bodies. Check a hashed asset, mutable audio,
   HTML deep link and missing static asset (404 rather than index.html).
6. DevTools Network with a fresh profile: both audio channels off, move between
   home/battle → zero audio requests. Enable music → current loop only; enable
   effects → effects warm and battle/star/button cues remain responsive.
7. Operator verifies Vercel rule/allowance and real provider quotas. If enabling
   a provider budget later, validate exhaustion/reset and Redis failure using
   mocked providers or isolated staging, not the live classroom's quota.
8. Rehearse ordinary classroom activity progressively with 2, then 5–10 users
   and the planned class under observation; no aggressive synthetic flood.
   Watch command/login/tutor latency, 429/5xx, worker memory/CPU, DB connections,
   cache errors and actual provider requests/tokens. Check existing free usage
   headroom and warm the service once before the session, without adding a
   keep-alive service. Do not increase worker/thread counts blindly.

## 10. Readiness for approximately 30 students

Application admission policies are classroom-friendly for normal gameplay and
one sign-in per student. The two corrections are focused and preserve existing
behavior. Readiness is **conditional**, not a verified 30-user capacity result:
the deployed forwarding boundary, firewall state, active provider allowances,
eight-thread configuration and ordinary classroom rehearsal remain operator
checks. Tutor traffic can use all eight request threads and queue gameplay;
provider quotas can be lower than the students' combined 360 tutor requests/min.

For a short demonstration, use prepared verified accounts, confirm dependency
health and auth flows, stagger tutor questions if quotas require it, and rehearse
the intended pattern. Free Render can sleep after idle periods and its Key Value
loses state on restart; see [Render free-instance limitations](https://render.com/docs/free).
No repository-only audit can certify live capacity or spending.
