# Home Fetch Performance Evidence

## Target-perspective result

- The default month still renders from the canonical full stats response and makes no second activity request.
- A non-default range fetches `/api/progress/stats/activity/` and merges only `activity_trend` plus `activity_window`; headlines and skills remain cached.
- Existing stats-root invalidations also invalidate all activity child keys.

## Database evidence

Local SQLite after `practice.0003`:

```text
SEARCH practice_commandstep USING INDEX cmdstep_player_created_idx (player_id=?)
activity queries 4
```

The pre-change plan was a full `SCAN practice_commandstep` with three parent-table lookups per row. The local activity probe was approximately 4 ms after the cutover, versus roughly 100 ms for the former full stats recomputation on the same dataset. Timings are diagnostic, not a production latency guarantee.

The migration was briefly probed against the previously configured Supabase connection, where PostgreSQL also selected an index scan. It was immediately rolled back to `practice.0002` so the deployed old writers remained compatible. After the user redirected the environment to local SQLite, `practice.0003` was applied locally and remains applied there.

## Verification

- Backend focused/ownership suite: `178 passed`.
- Earlier broad backend run: `214 passed`; its four failures were the expected pre-update architecture guard, and the corrected guard is included in the 178-pass final run.
- Frontend Home suites: `38 passed`.
- Frontend ESLint: passed.
- Backend Ruff on all changed Python: passed.
- Generated API currency, usage, and type-adoption checks: passed.
- Production frontend build: passed.
- Django migration drift check: no changes detected.

## Remaining external constraint

Render free-tier cold starts are unchanged. This implementation removes avoidable application/database work once the service is running; an always-on hosting plan is still required to eliminate platform spin-up latency.
