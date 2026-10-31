# Rate limiting and hosting cost protection

Repository audit: 2026-10-31. These are source changes and operating instructions;
no deployment, dashboard inspection, firewall publication or billing change was
performed. Existing unrelated workspace edits were excluded.

Independent follow-up: [POST_HARDENING_AUDIT.md](POST_HARDENING_AUDIT.md)
records the subsequent review, focused corrections, executed checks and
remaining classroom deployment gates.

## Audit findings and protections

| Priority | Confirmed finding | Consequence and disposition |
| --- | --- | --- |
| High | DRF's default `NUM_PROXIES=None` uses the supplied X-Forwarded-For string; login used a different trusted-peer helper | A caller could rotate headers to evade anonymous scopes. All scoped throttles now delegate to `common/http.py`; no proxy trust ranges were expanded. |
| High | Login had identifier/IP failed-login lockout but no request scope | Rotating identifiers still triggered password work. Added a source-IP login scope, including when a caller supplies a valid JWT; lockout remains 5 failures/300 seconds. |
| Medium | Login lockout environment variables were declared but never exported as Django settings | Dashboard overrides were ignored by TokenService. Connected the existing variables with positive-value validation; preserved the defaults. |
| High | Most authenticated endpoints had no throttle scope | Repeated reads, reports, mutations, starts and retries could use database/CPU without admission limits. Added generous per-user general protection and a separate start/retry scope. |
| Medium | Provider calls had burst limits, cooldowns, hedging and deadlines, but no daily shared budget | Added a per-user daily tutor scope and optional global physical-attempt quota. The global quota is **disabled until an operator selects a limit**. |
| Medium | Default Redis cache ignores connection failures | Limits and failed-login lockout pause during outages. Retained availability, exception logging, dependency readiness and database-backed session revocation. Enabled provider quota uses a strict alias and pauses only external AI calls on counter failure. |
| Medium | Render is directly reachable | Vercel rules can be bypassed. Backend policies apply on both routes; no CORS/header/hostname claim is used as origin authentication. |
| Low | API rewrite caching disabled, but no explicit origin no-store policy | Added private/no-store to API responses and proxy headers, including errors and OAuth redirects. |
| Low | Mutable mascot/email/cursor assets lacked explicit cache rules and SPA exclusions | Added one-day cache policy matching other mutable assets and excluded these directories from SPA fallback. |

Confirmed existing protections: `command_submit=120/min` covers adventure and
challenge commands, workspace file operations and tutorial introductions;
`tutor_chat=12/min`; registration `60/hour`; refresh `600/hour`; password reset
request `20/hour`, confirmation `60/hour`; email verification `120/hour`, resend
`60/hour`; OAuth `120/hour` shared across start, callback and ticket exchange.
Scoped authenticated requests use user ID; anonymous scopes use trusted source
identity. Those limits were preserved.

JWT authentication already loads user/security/player together. Refresh session
rotation and revocation are database-backed, with Redis as a cache. Failed-login
counters use atomic add/incr and identifier + trusted IP, so one student's failures
do not lock out other classmates. No new database queries were added for throttles
or provider budget checks. Request JSON logs already include request ID, route,
status, duration and release; throttle events now include retry timing and view.

## Limits and ownership

`backend/config/settings.py` is authoritative. DRF windows are rolling windows;
the provider budget resets at UTC midnight (08:00 Asia/Manila).

| Environment variable | Default | Key and purpose |
| --- | --- | --- |
| `THROTTLE_AUTHENTICATED` | `300/min` | Per authenticated user across API views; 5 requests/sec leaves 2.5x command-limit headroom for supporting reads. Anonymous traffic is excluded. |
| `THROTTLE_AUTH_LOGIN` | `120/min` | Source IP, regardless of supplied JWT; allows multiple attempts by a 30-student classroom while bounding identifier rotation. |
| `THROTTLE_AUTH_LOGOUT` | `120/min` | Anonymous source, bounds token decode/revocation traffic without limiting ordinary sign-out. |
| `THROTTLE_AUTH_PASSWORD_CHANGE` | `10/hour` | Per user; password hashing/security changes should be occasional. |
| `THROTTLE_AUTH_SECURITY` | `30/hour` | Per user, shared by revoke-other/revoke-all; account session maintenance should be occasional. |
| `THROTTLE_RUN_START` | `60/min` | Per user, shared adventure/challenge start and retry; allows one fresh run/sec. It never changes scenario retry counts, grading or repetition semantics. |
| `THROTTLE_TUTOR_CHAT` | `12/min` | Existing per-user tutor burst limit. |
| `THROTTLE_TUTOR_CHAT_DAILY` | `200/day` | Per user, rolling 24 hours; over three hours at a question/minute. Counts chat requests reaching throttles, including memo/guarded answers and requests another throttle rejects; adjust for scheduled workshops. |
| `THROTTLE_HEALTH_READY` | `120/min` | Per source, shared `/api/health/` and `/api/health/ready/`; bounds dependency probes. |
| `THROTTLE_PUBLIC_METADATA` | `60/min` | Shared public schema/docs scope, by user or source. |
| `TUTOR_PROVIDER_DAILY_LIMIT` | `0` | Disabled by default; positive integer caps actual outbound attempts globally per UTC day. |

All existing auth scopes retain their `THROTTLE_AUTH_*` settings. All other
authenticated curriculum, drill, progress, player, shop and admin-console DRF
views now receive the general limit. Drill checkpoints remain unrestricted by
the run-start scope. Cheap liveness explicitly has no dependency or throttle.
Requests rejected during authentication/permissions run before DRF throttles;
invalid-token floods, Django admin login, unknown URLs and bandwidth exhaustion
still require upstream protection. This is application usage control, not a
security-grade DoS firewall.

DRF HTTP 429 includes an integer `Retry-After` header and matching
`retry_after_seconds` JSON. Login lockout also preserves legacy `retry_after`.
Tutor retains its existing friendly error shape and uses the identical retry
value. DRF evaluates every throttle, so a policy can increment its counter even
when another policy rejects the request; these are request policies, not billed
AI-call counters. React Query already avoids retrying 429/other 4xx, retries network/5xx at
most once, uses 30-second staleness and disables focus refetch. Refresh is
single-flight with one bounded retry on 401; tutor retries require user action.

## Redis and provider failure policy

Production still requires shared Redis. Ordinary DRF throttles use the existing
default cache (`IGNORE_EXCEPTIONS=True`), socket/connect timeouts of 0.5 seconds,
and `DJANGO_REDIS_LOG_IGNORED_EXCEPTIONS=True`. Outages log `Exception ignored`;
readiness reports 503 but liveness remains 200. Login lockout and ordinary rate
limits are not enforced reliably during this outage. PostgreSQL remains session
truth, so revoked refresh tokens stay revoked. No platform-wide fail-closed
behavior or database-backed throttle fallback was introduced.

DRF history updates are not atomic: concurrent requests can exceed an ordinary
limit. This change intentionally retains DRF behavior and does not claim exact
security limits. The optional provider budget uses atomic Redis `add`/`incr`
through `provider_budget`, a separate cache alias with exceptions enabled against
the **same** Redis. It reserves before every physical HTTP attempt: recognition
embeddings, Gemini/Groq model attempts, hedged attempts, guarded rewrites and the
single stale-connection transport retry. Redis admission runs off the provider
event loop inside the existing wall-clock deadline. Failure or cancellation can
consume an allowance without sending; reservations are not refunded.

Budget failure prevents external calls and logs `tutor_provider_budget_unavailable`;
exhaustion logs `tutor_provider_budget_exhausted`. Tutor returns its established
unavailable/rate-limited response, allowing the UI to retain the question. Other
learning and authentication continue. Budget exhaustion does not place models
on provider cooldown, so increasing/disabling a quota can recover immediately.
Existing provider cooldowns, bounded response sizes, 1024 output-token ceiling,
max four Gemini models + Groq, pooled transport, RAG and answer guard remain.
Guarded replies and recognition are memoized for 24 hours; no prompt/user ID/API
key is added to quota keys or logs. Existing server-side tutor memoization is
separate from shared HTTP caching; no user-specific HTTP response is cached.

Render Free Key Value is non-persistent. The Blueprint already uses `noeviction`:
memory pressure returns write errors rather than evicting counters. Ordinary
cache writes may therefore fail open; enabled provider budget fails safely for
AI only. Restart, manual flush or an operator changing eviction policy can reset
all counters. A request-count quota does not cap dollars or tokens. Set provider
project limits/alerts too; provider billing controls remain the monetary boundary.
Do not change plans or memory policy as part of this task.

## Proxy identity and direct Render access

Trust is enabled only for configured direct-peer CIDRs. The helper walks
X-Forwarded-For from the right to the first untrusted IP; a malformed boundary or
all-trusted chain falls back to the direct peer. It ignores X-Real-IP,
X-Vercel-Forwarded-For and arbitrary client-prefix headers. Private proxy trust
does not prove any browser identity by itself.

Render's proxy chain and Vercel external rewrite chain must be verified in the
actual deployment. If the first untrusted address is a Vercel public egress,
anonymous auth scopes aggregate on that egress. General/authenticated gameplay
and tutor limits still key by user. Do not configure `0.0.0.0/0`, `::/0`, arbitrary
hop counts, or accept Vercel headers solely because they are present to remove
this aggregation. Prefer conservative aggregation over spoofable identity.
Broad private CIDRs in the existing Blueprint should be narrowed only after
confirming the platform's actual peers and keeping deploy/health access working.

Before enforcing tighter anonymous limits, capture the peer and forwarded chain
for controlled requests from two client networks through Vercel and directly to
Render. Use a temporary, access-controlled diagnostic or infrastructure logs;
do not expose a public echo endpoint or log cookies/tokens. Send a synthetic
spoofed X-Forwarded-For prefix and verify it cannot change the selected boundary.
Remove temporary diagnostic logging after checking. No production probe was run
by this audit, and browser-level identity is not claimed as verified.

The current public Render origin stays reachable. Backend scopes cannot be
bypassed simply by using its URL. CORS and `X-Git-It-Client: web` are browser/CSRF
defenses, not secret credentials. Host/Origin checks cannot authenticate a proxy.
A future origin-only gate needs coordinated server-side secret injection or a
supported private/verified proxy mechanism; never put a shared secret in Vite
variables or public vercel.json. Do not enable such a gate until OAuth callbacks,
refresh cookie routing, Render admin and health probes have a verified path.

## Manual Vercel settings (not applied)

1. Project > Firewall: inspect existing rules and ordering before changing
   anything. The repository does not reveal dashboard rules. Retain automatic
   platform DDoS protection; use Attack Challenge Mode temporarily during an
   active incident, verifying browser sign-in afterward.
2. If the current free allowance supports it, create one rule named
   `api-source-safety-net`: **Request Path starts with `/api/`**, counting key
   **IP**, **Fixed Window**, **60 seconds**, **6000 requests**, follow-up action
   **HTTP 429**. This is an initial classroom-friendly edge ceiling (roughly
   200 API requests/min x 30 classmates), not a tutor or per-account quota.
   Observe normal classroom traffic first; increase if a real legitimate peak
   exceeds it. Prefer 429 for API requests; HTML challenges can break fetch/OAuth.
3. Review the pricing/allowance dialog. Do not enable a paid feature or change
   billing plans. If Log is offered as a follow-up action, observe the proposed
   rule with Log before enforcement; otherwise compare existing traffic against
   the proposed threshold. Review Changes > Publish only after checking existing
   rules, free allowance and known classroom peaks.
4. Firewall > traffic grouping: select this rule and inspect matched/limited
   requests by path/IP. Verify a few ordinary login, refresh, tutor and command
   requests still succeed; use a preview/local reduced threshold for 429 testing,
   never flood production to reach 6000. Verify no unexpected HTML challenge.
5. Project > Usage/Observability: inspect top paths, transfer, edge requests,
   external-origin rewrite counts and errors. Set existing included usage alerts
   where available. Do not assume blocked traffic is free or a WAF caps spending.

Current Vercel docs permit declarative `routes` deny/challenge mitigation; rate
counting/monitoring is a Firewall configuration operation. This repository keeps
its supported high-level rewrites/headers and adds no unverified route rules or
new edge function. Keep the same-origin API rewrite: it preserves Strict refresh
cookies and OAuth, while avoiding a new proxy runtime. Moving API calls directly
to Render would require coordinated cookie/auth changes and still use Render.

## Manual Render and provider settings (not applied)

1. Confirm the service remains Free, the health path is `/api/health/live/`,
   Key Value is internal-only in Singapore, and maxmemory policy remains
   `noeviction`. Monitor memory, connection errors and readiness independently;
   do not point the service health check at dependency readiness.
2. Review the explicit new `THROTTLE_*` defaults added in render.yaml before
   syncing the Blueprint. Blueprint values overwrite corresponding dashboard
   overrides; tune intentional differences in the Blueprint. Existing deployment
   hosts, credentials, proxy trust, plans and health path were not changed.
3. For an AI budget, set `TUTOR_PROVIDER_DAILY_LIMIT` to an integer derived from
   the actual provider allowance and expected classroom demand. Example sizing:
   30 learners x 30 questions/day x a measured average of 3 attempts (embedding
   and fallback included) = 2700 reservations; select headroom within the real
   allowance. `0` disables this optional quota. It is deliberately omitted from
   Blueprint env values so sync does not erase a dashboard-selected budget.
4. After a controlled deploy, check logs for `api_request_throttled`, cache
   failures and budget events; correlate request ID and release. Alert on sustained
   increases. Verify readiness with one request. Check provider project request/
   token consumption and configured hard limits. Do not run a production outage
   experiment or quota flood.
5. Verify API headers via both Vercel and Render, signed in as two test users:
   `Cache-Control: private, no-store`, no shared CDN HIT for personalized data,
   independent bodies. Cookies and Authorization must never enter shared cache.
   Check a hashed asset (`immutable`), each mutable directory (one-day cache), a
   deep SPA link, and a missing asset (404, not index.html). Check index.html
   revalidates. Verify OAuth callback, refresh and logout manually after deploy.

## Cost impact and limits

The general throttle adds one default-cache get/set pair per authenticated
request; tutor daily protection adds another pair on chat. No new database work,
service, package, billing plan, paid feature or edge function was added. Enabled
provider quota costs an atomic add and, for an existing key, increment per
physical attempt; two Django cache handles may use extra Redis connections.
Monitor free Key Value connections and memory. When disabled, quota admission
makes no cache calls. History counters and one-day tutor caches occupy memory.

Vercel still receives uncached API requests and initial static loads; cache hits
at the CDN can still consume edge request allowance and served bytes. Hashed
bundles keep one-year immutable caching; mutable assets retain one-day browser
caching with one-week stale revalidation. Images/audio are deduplicated in a
session. The follow-up audit corrected muted audio preloading: effects warm
only when enabled, and music loads only the current screen's loop when enabled.
Fully muted screen changes create no audio elements or media requests. Enabled
effects retain their existing warm-up for battle timing; enabling music later
resumes the current screen, including navigation performed while muted.

Residual risks include distributed bot/account farms, invalid-auth floods,
public liveness traffic, Django admin brute force, repeated provider attempts
after cache loss, Vercel-egress anonymous aggregation, and DRF concurrency
overshoot. Provider budgets/alerts and platform firewalls complement these
application controls; no repository change guarantees a hosting spend ceiling.

## Verification

Changed-file ownership:

| Files | Reason |
| --- | --- |
| `backend/config/settings.py`, `test_settings.py`, `integration_test_settings.py` | Configurable policies, strict provider alias, lockout env wiring and isolated test limits. |
| `backend/common/throttles.py`, `http.py` | Trusted source identity, per-user general policy and daily tutor policy; cached CIDR parsing avoids repeated parsing. |
| `backend/accounts/views.py`, `adventures/views.py`, `challenges/views.py` | Scope declarations and consistent login lockout response. No learning services changed. |
| `backend/common/api.py`, `tutoring/views.py` | Consistent retry fields/headers and correlated throttle logging. |
| `backend/common/views.py`, `config/urls.py` | Readiness/public metadata policies; cheap liveness remains available. |
| `backend/tutoring/services/budget.py`, `provider_transport.py`, `providers.py` | Optional atomic budget at every HTTP attempt; bounded off-loop admission, AI-only failure behavior, no false provider cooldown. |
| `backend/common/middleware.py`, `frontend/vercel.json` | Private API HTTP cache policy and mutable static directory routing/cache headers. |
| `frontend/src/shared/level/components/GameplayWorkspaceTourOverlay.tsx`, `GameplayWorkspaceTourSpotlight.tsx` | Follow-up validation fix: extract the unchanged spotlight rendering into a focused child component to meet the architecture size limit. |
| `backend/accounts/tests/test_throttling.py`, `common/tests/test_throttles.py`, `test_http.py`, `test_health.py`, `test_settings.py`, `test_cache_outage.py`, `test_api_cache_policy.py`, `tutoring/tests/test_budget.py`, `test_recovery.py` | Admission, authentication, identity, retry, cache and provider regressions. |
| `backend/.env.example`, `.env.development.example`, `.env.production.example`, `render.yaml` | Document and declare explicit defaults; optional global budget remains operator-selected. |
| `deploy/RATE_LIMITING.md`, `RENDER.md`, `VERCEL.md` | Audit, operating limits, manual dashboard steps and links. |

Run targeted suites without production services:

```powershell
cd backend
.venv/Scripts/python.exe -m pytest accounts/tests common/tests tutoring/tests adventures/tests challenges/tests drills/tests progress/tests -q
.venv/Scripts/ruff.exe check .
.venv/Scripts/ruff.exe format --check .
```

The added tests cover user independence and zero throttle DB queries, scope
layering, login/lockout/classroom headroom, spoofed/trusted/invalid proxy chains,
exact retry expiry, public probe/schema policies, no-store errors/redirects,
quota reset/concurrent admission, outage logging, retry accounting and stalled
admission cancellation. Real Redis atomic admission runs under
`config.integration_test_settings` in the existing CI integration job and skips
in the offline SQLite/LocMem suite. Local request/response evidence is stored
under ignored `.tmp/rate-limit-hardening/`; test results are recorded there and
reported separately. Local evidence does not establish deployed headers or WAF.

Local verification results (2026-10-31):

- Full backend suite: **1170 passed, 1 skipped** in 407.48 seconds, SQLite test
  settings with provider keys disabled. Existing command, retry, authentication,
  tutor/RAG/answer guard, reward and KPI tests passed. The skip is the new real
  Redis concurrency check; Redis/PostgreSQL services were unavailable locally.
- Final focused checks after review: **74 passed, 1 skipped** in 23.38 seconds;
  these include the final counter-semantics and strict-alias test corrections.
- Frontend HTTP/session tests: **17 passed**. Production TypeScript/Vite build
  passed. Follow-up tour tests: **28 passed**; targeted ESLint and production
  build passed after extracting the unchanged spotlight rendering. Tour behavior
  and styling were preserved.
- Backend Ruff lint/format, Django deployment checks and Render Blueprint guard
  passed. Generated API contract remained current; no generated payload edits.
- Fast repository gates: **10 passed** after the requested validation follow-up.
  The initial run found a pre-existing 403-line tour overlay against a 400-line
  limit. Its spotlight rendering was extracted into an 85-line child component;
  the overlay is now 354 lines, without changing markup, styles or controls.
- Acceptance transcript: **21 local checks**, comprising 19 HTTP responses and
  2 direct provider-budget checks, with synthetic users and tokens omitted.
  Ordinary API availability was captured inside the mocked quota-cache outage.
- Correctness/maintainability and PRE/POST plan review passed after correcting
  the test cache-namespace assumption and documenting DRF counter semantics.
  Initial sandbox execution could not create Windows asyncio's internal socket;
  approved local execution outside the sandbox completed those tests. No live
  service traffic, production outage tests, commits, pushes or deployments.

References checked during this audit:
[DRF throttling](https://www.django-rest-framework.org/api-guide/throttling/),
[Render Key Value](https://render.com/docs/key-value),
[Render free services](https://render.com/docs/free),
[Vercel external rewrites](https://vercel.com/docs/routing/rewrites),
[Vercel request headers](https://vercel.com/docs/headers/request-headers),
[Vercel WAF custom rules](https://vercel.com/docs/vercel-firewall/vercel-waf/custom-rules),
[Vercel rate limiting](https://vercel.com/docs/vercel-firewall/vercel-waf/rate-limiting),
[Vercel WAF usage](https://vercel.com/docs/vercel-firewall/vercel-waf/usage-and-pricing).
