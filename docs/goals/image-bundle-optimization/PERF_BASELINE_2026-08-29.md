# Performance Baseline — 2026-08-29

Captured before the Priority 1 image-bundle optimization (WebP conversion +
lazy variant loading for rank badges and battle-outcome art). This is the
"before" snapshot for that change; re-run the same commands after and diff
against this file.

**Note on location:** the request was `docs/perf-baseline-2026-08-29.md`, but
`scripts/check_documentation_current.py` restricts `docs/` to `docs/goals/*`
scoped folders (anything else there fails CI). This file lives at
`docs/goals/image-bundle-optimization/PERF_BASELINE_2026-08-29.md` instead,
following the same convention as `docs/goals/improve-command-latency/PRE_SLICE_BASELINE.md`.

## Environment

- Git HEAD: `4ec0aa39c3cee54540324130d2eaaecb308a48b9` (`main`, 5 commits ahead of `origin/main`)
- Worktree: dirty before this capture — `frontend/package-lock.json` had a pre-existing uncommitted change unrelated to this work (23 insertions / 57 deletions), left untouched
- OS/shell: Windows, Git Bash
- Python: 3.13.7 (`backend/.venv`)
- Django: 6.0.7
- pytest: 9.1.1
- Database: local SQLite (`db.sqlite3` / pytest SQLite for the profiler) — **not** representative of the production Postgres/Supabase path; treat absolute numbers as directional only
- Samples per warm lane: 15 (default)

## 1. Command-submit latency (`backend/scripts/profile_command_latency.py`)

```powershell
cd backend
$env:COMMAND_LATENCY_SAMPLES='15'
python -m pytest scripts/profile_command_latency.py::test_profile_adventure_cold -q -s
python -m pytest scripts/profile_command_latency.py::test_profile_challenge_cold -q -s
python -m pytest scripts/profile_command_latency.py::test_profile_steady_state -q -s
```

All three invocations passed.

### Isolated cold probes

One request per fresh pytest process — import/URL-resolution cost isolated from any other lane.

| Lane | Request p50/p95/max (ms) | Queries | Response bytes |
| --- | ---: | ---: | ---: |
| Adventure final completion | 587.58 / 587.58 / 587.58 | 29 | 1,347 |
| Challenge completion | 311.94 / 311.94 / 311.94 | 38 | 2,893 |

(Cold numbers include Django/pytest process start-up and first-import cost — not comparable to the warm lanes below; kept for observability only, same as the existing `PRE_SLICE_BASELINE.md` convention.)

### Warm steady-state lanes

Both endpoints received one unmeasured warm-up completion request first; these are the forward-order, single-run numbers.

| Lane | Request p50 (ms) | Request p95/max (ms) | Query p50/p95/max | Response bytes p50/p95/max |
| --- | ---: | ---: | ---: | ---: |
| Adventure diagnostic | 7.90 | 11.48 / 11.48 | 8 / 8 / 8 | 1,429 / 1,431 / 1,431 |
| Adventure wave advance | 16.51 | 21.45 / 21.45 | 23 / 23 / 23 | 2,816 / 2,816 / 2,816 |
| Adventure final completion | 21.02 | 28.85 / 28.85 | 29 / 29 / 29 | 1,350 / 1,350 / 1,350 |
| Challenge diagnostic | 6.34 | 9.93 / 9.93 | 5 / 5 / 5 | 2,082 / 2,083 / 2,083 |
| Challenge completion | 19.34 | 23.63 / 23.63 | 38 / 38 / 38 | 2,896 / 2,896 / 2,896 |

This run was **not** repeated with `COMMAND_LATENCY_REVERSE_LANES=true` or with a controlled-legacy rerun (both done for the original `improve-command-latency` goal) — this capture is a single-run reference point for the image-optimization change, which does not touch this code path at all, so no lane-order or GC-confound control was needed here.

## 2. HTTP load smoke (`scripts/load_smoke.py`)

Run against a local `manage.py runserver` (SQLite, single machine, `--noreload`), not a deployed environment — treat as a smoke check, not a capacity claim. Target path defaulted to `/api/health/ready/` (unauthenticated readiness probe).

```bash
cd backend && python manage.py runserver 127.0.0.1:8001 --noreload &
python scripts/load_smoke.py http://127.0.0.1:8001 --users 20 --duration 15 --timeout 5
python scripts/load_smoke.py http://127.0.0.1:8001 --users 100 --duration 15 --timeout 5
```

| Users | Requests | Throughput | Errors | p50 (ms) | p95 (ms) | p99 (ms) | Result |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 20 | 14,197 | 945.2 req/s | 0 (0.00%) | 19.9 | 32.1 | 48.2 | PASSED |
| 100 | 17,153 | 1,140.4 req/s | 4 (0.02%, `ConnectionRefusedError`) | 77.3 | 126.3 | 237.4 | PASSED |

Both runs passed the script's default thresholds (`--max-error-rate 0.01`, `--max-p95-ms 750`). The 4 connection-refused errors at 100 concurrent users are consistent with the local dev server's connection backlog under Git Bash/Windows, not a Django/DB issue — this is a smoke check of a health endpoint, not a gameplay-endpoint capacity test. A real capacity read (per the NFR audit's "Not Verifiable from Code" items) still requires running this against a deployed Postgres/Redis-backed environment with authenticated gameplay traffic, not local SQLite.

## Baseline interpretation

- This capture exists to diff **frontend transfer weight**, not backend query cost — the image-optimization change touches only `frontend/src/features/home/components/HomeRankBadge.tsx`, `frontend/src/shared/level/components/game-outcome/GameOutcomeModal.tsx`, and the underlying image assets. None of the numbers above are expected to move after that change; they're recorded so a future session can confirm that's still true (i.e. this change didn't accidentally regress the command-submit path).
- The frontend-side "before" number for this specific change is the `npm run build` bundle report from Phase 1: `dist/assets` = 14MB total, 13MB of it PNG. See the Phase 1 report in conversation history / commit message for the full per-file breakdown; the "after" comparison lands directly in this same goal folder once the conversion is done.
