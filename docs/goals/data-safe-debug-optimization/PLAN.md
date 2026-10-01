# Data-safe Debugging and Optimization Implementation Plan

**Intent:** Fix demonstrated runtime bugs and reduce redundant work without touching existing user data.
**Current Behavior:** Delayed HTTP work can cross authentication changes; account-independent query caches survive those changes; drill resume data becomes stale; command-history cache entries survive rolled-back transactions; learner stats omit tier commands and repeat completion queries.
**Expected Outcome:** Requests and cached reads remain bound to their session, drills resume current checkpoints, rolled-back history stays invisible, and stats include the learner's tier commands with fewer queries.
**Target-Perspective Output:** Deterministic delayed-request/cache and drill lifecycle traces, isolated database rollback and learner-stats request/response fixtures, and unchanged hashes for existing database files.
**Truth Owner:** Auth store owns browser session identity; app providers own query clients; backend owns persisted drill checkpoints, command steps, and metrics.
**Contract Boundary:** Existing generated HTTP contracts and persisted schemas stay unchanged.
**Cutover:** Replace unsafe behavior in existing owners; no parallel runtime path.
**Displaced Path:** Unguarded request retries, shared account cache lifetime, stale drill resume hydration, pre-commit history publication, and incomplete/repeated stats reads.
**Value Density:** Five demonstrated bugs in a small set of shared owners; no migrations or broad refactor.
**Acceptance Evidence:** Deferred fetch proves no old-account write is replayed; a new account cannot read old cached data; drill reentry restores the saved queue; rollback leaves no phantom history; stats fixture includes only the intended player's commands; completion query count decreases; database hashes remain unchanged.
**Evidence Lane:** Hermetic frontend tests with mocked HTTP and in-memory Django fixtures, with concrete observed values recorded in EVIDENCE.md.
**Kill Criteria:** No unguarded cross-session retry remains; no transaction publishes history before commit; no new storage owner, migration, backfill, or compatibility path.
**Architecture Slice:** Auth store/HTTP client/app providers; drill hook/page; common history LRU; progress metric service and focused tests.
**Plan Review Gate:** Requires PRE review before execution.

## Data boundary

- Never open existing databases for writes, run live endpoints, migrate/seed existing data, alter credentials, or deploy.
- Backend verification explicitly uses config.test_settings, an in-memory database, locmem cache, and locmem email.
- Preserve untracked frontend/public/cosmetics/companion/red/ and all unrelated changes.
- Record local database hashes before and after verification. Schema and authored/generated curriculum data are out of scope.

## Tasks

1. **Session isolation — frontend agent.** Modify shared/auth/useAuth.ts, shared/api/httpClient.ts, app/providers.tsx and focused tests/helpers if needed. Track a stable session boundary, reject late results/retries from displaced sessions, isolate query clients on session transitions, and retain ordinary same-session refresh behavior. Test deferred writes, refresh/logout races, cache handoff, and same-session refresh. No backend or drill edits.
2. **Committed history and complete efficient stats — backend agent.** Modify common/services/lru.py, progress/services/metrics.py and focused tests. Publish immutable cache snapshots after successful commit only, including query-populated cache values; scope all stats command reads to the player's three command relations; consolidate completion counts into conditional aggregates. Demonstrate rollback/commit behavior, player isolation, tier activity, unchanged stat semantics, and reduced query counts. No schema changes. Follow the Postgres best-practices skill when changing queries.
3. **Fresh drill resume — main agent.** Modify features/drills/hooks/useDrillSession.ts, pages/DrillPage.tsx, focused helper/tests as necessary. Ensure entry uses current saved resume and completion/restart cannot restore obsolete state. Keep mutation ordering and StrictMode purity in mind; preserve public API shape. Demonstrate same-client leave/reentry, completion and restart with delayed checkpoint responses.
4. **Integration — main agent and independent reviewer.** Review all diffs for correctness/maintainability and plan alignment, run relevant targeted and full suites, lint/build and applicable repository guards, compare database hashes, record precise results and limitations.

Tasks 1–3 may run in parallel after PRE review because write scopes are disjoint. Integration depends on all three. This plan records the user's existing authorization to debug/optimize; it does not authorize production actions.

## PRE review

Ready with no blockers. Acceptance also covers account changes during response parsing and refresh backoff; pending drill writes during reentry and save/report/discard ordering; nested rollback, query-populated cache snapshots and the three history subclasses. Report query-count savings only, without inferring production PostgreSQL latency from SQLite measurements.

## Review-driven scope refinement

Session isolation also covers its existing consumers: Protected confirmation, delayed navigation logout, mutations delayed by onMutate/online readiness, and challenge/tier sessionStorage bootstrap plus cross-tab run messages. These are additional paths to the same demonstrated cross-account bug. Scope bootstrap caches/messages to the account without deleting user records or preferences. Backend agent may implement the four challenge/tier bootstrap/cache utilities and focused tests after finishing Task 2; these files are disjoint from the frontend agent's auth files. Existing unrelated curriculum checksum drift is reported without changing authored content or repinning expected hashes.

## Completion

Tasks 1–4 are complete. Independent POST correctness and maintainability review passed. See EVIDENCE.md for concrete behavior traces, exact test results, query counts, data-file hash verification, and the unrelated curriculum preservation check that remains failing.
