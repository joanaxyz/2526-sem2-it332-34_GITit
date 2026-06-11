# GIT it! — Codebase Quality, Architecture & NFR Improvement Plan

Audit date: 2026-06-11. Goal: clean up quality/dead code, solidify architecture & structure, and meet NFRs so 100+ concurrent users can use the site without performance degradation.

## Audit verdict (TL;DR)

The codebase is in better shape than feared — frontend is high quality (consistent feature folders, zero `any`, no console.logs, mature error handling), backend layering (views → services/selectors → models) is mostly respected, and the Postgres/pooler config is already tuned for the 200ms-RTT Supabase setup. The real gaps for 100+ users are **operational, not architectural**:

1. **No rate limiting at all** — submit-command, register, refresh are unthrottled (`backend/config/settings.py:220-227`)
2. **No logging config, no health check** — you'd run 100 users blind
3. **`backend/requirements.txt` is committed EMPTY** — deployment is unreproducible
4. **`git-it.zip` (54MB) is git-tracked** at repo root
5. **No CI** — ruff + eslint + 660 backend / ~194 frontend tests exist but are enforced nowhere
6. Per-run N+1 queries in challenge/adventure payload serializers (each extra query = +200ms on Supabase)
7. God components: `LiveDagPanel.tsx` (687 lines), `ChallengeWorkspace.tsx` (615), `StoreyPracticeHub.tsx` (577); fat payload-building serializers on the backend
8. `practice/` app has **zero tests** despite a 403-line `services.py`

False alarms ruled out during verification: `.env` files are **not** committed (no credential rotation needed); the simulator is in-memory and fast (no subprocess, no Celery needed); DB config (CONN_MAX_AGE=60, prepared-statement-off for pooler) is already correct.

## Working-tree strategy

The tree is dirty on `refactor/auth` (home redesign WIP + untracked `frontend/public/dashboard_video/`). **Do not mix cleanup into that WIP.** Commit/stash it first, then one branch per phase. Each phase is independently shippable.

---

## Phase 0 — Baselines (½ day, measure on main)

1. Query/latency baseline: `cd backend && python scripts/profile_command_latency.py` — record queries-per-request for adventure + challenge submit (the canonical NFR metric: latency ≈ query count × 200ms RTT).
2. Test baseline: `cd backend && pytest -q`; `cd frontend && npm test`.
3. Bundle baseline: `cd frontend && npm run build` — note entry chunk size.
4. Lint debt: `ruff check backend`; `cd frontend && npm run lint`.

Record all four numbers; every later phase proves itself against them.

## Phase 1 — NFR / scale blockers (2–3 days) — branch `chore/nfr-hardening`

**1a. DRF throttling** — add to `REST_FRAMEWORK` in `backend/config/settings.py:220`:
```python
"DEFAULT_THROTTLE_CLASSES": ("rest_framework.throttling.ScopedRateThrottle",),
"DEFAULT_THROTTLE_RATES": {
    "auth_register": "10/hour",
    "auth_refresh": "60/hour",
    "command_submit": "120/min",
},
```
Set `throttle_scope` on: `RegisterAPIView`/`RefreshAPIView` (`backend/accounts/views.py`), `ChallengeCommandSubmitAPIView` + `ChallengeWorkspaceFileAPIView` (`backend/challenges/views.py`), `AdventureRunSubmitCommandAPIView` + `AdventureWorkspaceFileAPIView` (`backend/adventures/views.py`). Throttle state lives in the already-required Redis cache. Add 2–3 tests asserting 429 past the limit.

**1b. Clamp the manual paginator** — `backend/curriculum/views.py:46`: `limit = min(max(limit or 8, 1), 50)`. Do **not** add a global `DEFAULT_PAGINATION_CLASS` (would change every response shape and break the frontend contract).

**1c. Kill per-run N+1s** — `backend/adventures/serializers.py:28-64` (`_mastery_payload` re-queries AdventureMastery; hoist to run level and pass down) and `backend/challenges/serializers.py:144,159` (`mastery_progress_payload`/`completion_payload` query per payload; extend the existing `prefetch_run_payload_context` memoization at `:39`).

**1d. Missing indexes** — `QuestCompletion(user, challenge_quest)` in `backend/progress/models.py`; `AdventureQuestAttempt(run, status)` in `backend/adventures/models.py`. Then `python manage.py makemigrations progress adventures`.

**1e. Bound `repository_state`** — `backend/challenges/models.py:119` is an unbounded JSONField; add a serialized-size guard (~256KB cap → friendly error) in the submit path. Prevents tail-latency cliffs.

**1f. The 5.7MB video** — `frontend/public/dashboard_video/upscaled-video.mp4` (still untracked): re-encode smaller via ffmpeg, use `preload="none"` and mount lazily. Decide before it gets committed; coordinate with the home-redesign WIP.

**Verify:** profiler query count ≤ baseline; throttle tests pass; load test with `hey -n 2000 -c 100` against an authenticated submit-command endpoint — p95 should stay flat at c=100 with a 429 backstop.

## Phase 2 — Dead code & repo hygiene (1 day) — branch `chore/repo-hygiene`

1. `git rm --cached git-it.zip` + gitignore. (Skip history rewrite unless re-publishing the repo publicly.)
2. Delete dead code: `backend/python` (empty file), `frontend/src/assets/hero.png` (grep for refs first), `backend/curriculum/management/commands/seed_command_library.py` (incomplete, references nonexistent `CommandLibraryEntry`).
3. Delete from disk: `debug-4ce873.log`, `debug-7b498f.log` (gitignored already).
4. `git mv` stale root plan docs (`ADVENTURE_MASTERY_PLAN.md`, `SCENARIO_CONTEXT_PLAN.md`, `STATS_TAB_PLAN.md`, `TERMINAL_REUSE_PLAN.md`) + `final-tower-design-reference.png`, `tower-preview.html` → `docs/archive/`.
5. **Pin runtime deps** — `backend/requirements.txt` is empty: from the project venv, `pip freeze`, hand-trim to direct deps (Django, DRF, simplejwt, django-redis, drf-spectacular, django-cors-headers, django-environ, psycopg, gunicorn).

**Verify:** fresh venv + `pip install -r requirements.txt` + `python manage.py check` boots; `pytest -q` and `npm test` green.

## Phase 3 — Observability baseline (1–1.5 days) — branch `chore/observability`

1. **LOGGING dict** in `backend/config/settings.py` (console handler, `DJANGO_LOG_LEVEL` env, `django.request` at ERROR).
2. **Stop silently swallowing cache failures** — `backend/accounts/services.py:55-127`: replace bare `except Exception: pass/return` with `logger.warning(..., exc_info=True)` keeping the graceful fallback. Redis failures on the token-revocation path must be visible.
3. **Health endpoint** — `common/views.py::health` checking DB + cache, wired at `api/health/`, auth- and throttle-exempt.
4. **Sentry (optional)** — `sentry_sdk.init()` guarded by `SENTRY_DSN` env; no-op when unset.

**Verify:** `curl /api/health/` → 200 `{"db":"ok","cache":"ok"}`; stop Redis → 503 + logged warning.

## Phase 4 — Architecture & maintainability (3–5 days) — branches `refactor/backend-payloads`, `refactor/frontend-components`

Backend (behavior-preserving moves; profiler query counts must not change):
1. De-dupe `get_challenge_quest()` — keep `backend/challenges/selectors.py:45`, delete the byte-identical copy at `backend/curriculum/selectors.py:448`, fix imports (watch the documented challenges⇄curriculum cycle).
2. Move payload building out of serializers: create `challenges/payloads.py` + `adventures/payloads.py`, move `challenge_run_payload` (`challenges/serializers.py:49-116`) and friends verbatim; serializers keep only input validation. Ship challenges first, then adventures.
3. Decompose `_rules_from_state_requirements` (`backend/evaluation/services.py:92-202`, 110 lines) into a requirement-type → builder-function dispatch table. **Write evaluation tests first** (see Phase 5c) so the refactor is guarded.

Frontend (one component per PR):
4. Split `LiveDagPanel.tsx` (687) — DAG layout/render vs panel chrome/controls; `ChallengeWorkspace.tsx` (615) — extract terminal pane, file pane, status header; `StoreyPracticeHub.tsx` (577) — **after** the `refactor/auth` redesign lands.
5. Consolidate inline shadow/gradient style objects (`AuthLayout.tsx:69,96-100`, `HomeLayout.tsx:46-53`, `HeroBanner.tsx`, `AchievementsTab.tsx`) into bespoke CSS utility classes/custom properties in `styles/globals.css` per DESIGN.md — coordinate with the WIP since several files overlap.

**Verify per step:** relevant `pytest` apps green; profiler unchanged; `npm test` + `npm run build` + manual smoke of the touched page.

## Phase 5 — Code splitting, tests & CI (2–3 days) — branch `chore/ci-and-splitting`

1. **Route-level code splitting** — `frontend/src/app/router.tsx`: lazy-load practice routes (`ChallengeRunPage`, `AdventureRunPage`, `StoreyMapPage`) so reactflow/dagre/recharts/motion leave the entry chunk; wrap in `<Suspense>`.
2. **Top-level Error Boundary** in `frontend/src/app/providers.tsx` (recovery UI instead of white screen).
3. **Close test gaps** — add `backend/practice/tests/` (CommandExecutor happy path + error categories — currently ZERO tests); thicken `evaluation` tests before the Phase 4 refactor.
4. **CI** — `.github/workflows/ci.yml`, two jobs: backend (`ruff check`, `pytest` with `config.test_settings`) and frontend (`npm ci`, lint, test, build). Finally enforces the already-configured linters.

**Verify:** entry chunk measurably smaller than Phase 0 baseline (heavy deps in route chunks); `pytest backend/practice` exists and passes; CI gates a test PR.

---

## Explicitly NOT doing (and why)

- **No Celery/async queue** — simulator is in-memory and fast; the bottleneck is DB round trips, not CPU. A broker+worker is pure ops burden at this scale.
- **No Docker requirement** — Supabase + Redis are managed; pinned requirements.txt + gunicorn + a start command covers Render/Fly/Railway. Dockerfile is optional polish.
- **No global DRF pagination class** — would break every existing response contract; clamp the one manual paginator instead.
- **No git-history rewrite** for the zip — untrack + gitignore suffices unless publishing fresh.
- **No new state libs, no styling rewrite, no payload-shape redesign** — keep zustand + react-query + bespoke CSS; move code verbatim.

## Effort summary

| Phase | Focus | Effort |
|---|---|---|
| 0 | Baselines | ½ day |
| 1 | Throttling, N+1s, indexes, payload bounds | 2–3 days |
| 2 | Dead code, zip, pin deps | 1 day |
| 3 | Logging, health check | 1–1.5 days |
| 4 | Payload modules, god components, tokens | 3–5 days |
| 5 | Code splitting, practice tests, CI | 2–3 days |

Total ≈ 2.5–3 weeks solo, each phase independently mergeable. Phases 1–3 are the "100+ users" answer; 4–5 are the maintainability answer.

## Key files

- `backend/config/settings.py` — throttles (Phase 1), LOGGING (Phase 3)
- `backend/challenges/serializers.py` — N+1 fix (1c) then payload extraction (4.2)
- `backend/scripts/profile_command_latency.py` — verification harness for every backend perf claim
- `backend/requirements.txt` — currently empty; pin in Phase 2
- `frontend/src/app/router.tsx` — code splitting (Phase 5)
