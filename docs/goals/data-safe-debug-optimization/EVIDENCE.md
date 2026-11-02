# Data-safe debugging and optimization evidence

## Data boundary

All backend test invocations explicitly select `config.test_settings`, SQLite `:memory:`, local-memory cache, and local-memory email. No existing database was opened for writes, migrated, reseeded, or reset. No live API or deployment was used. The existing untracked red companion asset directory was left alone.

Before/after SHA-256 comparisons of `db.sqlite3` and `backend/db.sqlite3` both returned `Unchanged: True`. The initial hash snapshot is a local ignored verification artifact at `.tmp/debug-optimize-db-before.json`.

## Concrete behavior evidence

- **Drill reentry:** render the actual page and session hook in StrictMode with a shared QueryClient and mocked HTTP. Answer one question, leave while PUT is pending, and return. The page stays loading until PUT and a fresh GET finish, then shows `Answered 1` at the `complete` rung. Exactly one checkpoint is sent.
- **Intermediate checkpoints:** queue two saves, leave, and return. The first successful save updates cached resume to one answer, but the new session remains loading. Only after the second save and final GET does it show `Answered 2` at the `forge` rung.
- **Drill ordering:** delay the first save, finish, restart, and answer again. Observed request order is `save:1`, `save:2`, `report`, `discard`, `save:1`. The final stored fixture has one completed session and a new resumable queue with one answer. Completion without restart leaves no resumable checkpoint.
- **Queued drill after sign-out:** sign out while a second checkpoint waits behind the first. The second API call is never sent.
- **Run cache ownership:** 17 focused checks cover challenge/tier bootstraps and BroadcastChannel/storage updates. Account B cannot hydrate A's run; unidentified legacy messages are ignored; old-generation listeners and writers cannot publish after handoff; same-account token rotation continues to work; unrelated storage remains present.
- **HTTP/session boundary:** 56 focused checks include a delayed A purchase returning 401 after B signs in: exactly one purchase request is observed, with no replay. Late successful responses and delayed body parsing are rejected. Logout and old refresh results leave B's credentials intact. Foreign-account, malformed, and missing-identity refresh tokens are rejected before installation or purchase replay.
- **Mutation execution:** old-client mutations held in asynchronous `onMutate` send zero writes after account handoff, including when an observer replaces their options while waiting. New clients have none of the old account's query data. A late navigation logout does not clear a newer session.
- **History rollback:** for challenge, adventure, and tier history owners, a rolled-back `git commit -m phantom` leaves no cache entry. Reusing the attempt number for an invalid command yields empty persisted history. Nested savepoint rollback drops only its callback. Successful commit publishes the original snapshot; subsequent cache reads make zero queries.
- **Learner stats:** an authenticated fixture GET to `/api/progress/stats/` returns six own commands and 50% accuracy across all three parent relations. Four recent commands appear in week/month/year trends. Another player's commands do not contribute.
- **Stats query count:** mixed-star completions retain four completed levels and two perfect clears. The completion headline calculation uses two SQL queries, previously four. This is a measured query-count reduction, not a production latency benchmark.

## Supporting validation

- Initial full frontend suite: 117 files, 781 tests passed.
- Drill lifecycle regression suite: six tests passed after the intermediate-checkpoint review correction.
- Backend focused suite: 22 passed, including 15 transaction cases and four new stats cases. Replaying original HEAD method bodies in an isolated process made all 19 new regressions fail, including the previous four-query count.
- Final backend integration rerun: 28 passed (history, stats, stats contract, auth architecture policy); Ruff passed. The temporary architecture-guard failure is resolved without changing its policy.
- Additional existing gameplay runtime tests: 25 passed.
- Initial production build, frontend lint, backend Ruff, and all fast repository quality gates passed.
- Full backend run: 2,526 passed, two failures. One was the temporarily changed HTTP refresh helper spelling tripping the architecture guard; it is addressed during integration. The other is the existing Arcane curriculum preservation checksum mismatch, reproduced independently with the untouched curriculum files.

Auth regressions: seven files, 56 tests passed; focused ESLint passed. Run-cache regressions: two files, 17 tests passed; focused ESLint passed. A test-only TypeScript parameter-property syntax mismatch was corrected before final build validation.

Final integration build (`tsc -b` plus Vite), complete frontend ESLint, dead-code lint, and all repository fast quality gates passed. Generated API contracts remain current and unchanged.

The final full frontend run exposed one older command-introduction test that attempted to persist account-owned bootstrap state without a signed-in fixture. Its setup now establishes the authenticated learner the real page requires; all six tests in that file passed on rerun. No runtime relaxation was made.

Full frontend results: **821 passed, one failed, 822 total across 120 files** in 422.17 seconds. The sole failure was that fixture, already corrected and verified by its six-test rerun. Final ESLint and TypeScript checks after that correction also passed. The whole suite was not repeated after this test-only setup change. The persisted JSON report is `.tmp/debug-optimize-frontend-results.json`, with verbose stdout/stderr alongside it.

All implementation tasks and final review gates are complete. The only unresolved check is the independently reproduced, untouched curriculum checksum mismatch below.

Independent POST correctness and maintainability review found no remaining blockers after the mutation execution guard, account-scoped cache, refreshed-token identity check, and drill entry-latch corrections. Persisted-user/refresh-cookie identity mismatch conservatively requires signing in again.

## Known limitation

`curriculum/tests/test_arcane_curriculum_preservation.py` independently fails for the existing adventure and challenge authored-content hashes. This work does not modify curriculum data or repin preservation hashes merely to make the test pass. That mismatch needs its own content-history review.
