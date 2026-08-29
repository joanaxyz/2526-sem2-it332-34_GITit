# Command Round-Trip Latency Implementation Plan

**Intent:** Reduce the time between the frontend's immediate simulated command result and the authoritative server response that advances a wave or shows a final outcome.
**Current Behavior:** Command submissions have request-level timing and several service spans, but the tracked `backend/scripts/profile_command_latency.py` is stale: it submits command-only bodies from the retired server-execution contract, times one request per label, and mixes cold-start with steady-state work. One-off current-contract real-API probes are order-sensitive: on 2026-08-28 the first measured completion request took 491.79-692.89 ms while the warmed request took 56.27-91.90 ms. The instrumented validation, evaluation, and direct write spans accounted for only a few milliseconds, so cold-start and uninstrumented transition/payload work are currently mixed together. Adventure transition payload construction also calls `ordered_levels_for`, whose queryset prefetches every level's command forms, waves, and variant JSON even though the payload only reads level summary fields.
**Expected Outcome:** A tracked profiler reports cold-start separately from steady-state diagnostic and completion lanes for both gameplay modes. The Adventure transition response stops loading unrelated wave/variant data and reuses its already-prefetched published wave collection. With identical seeded scenarios and sample count, both the warm Adventure intermediate-wave and final-level-completion lanes have at least 30% lower request wall-time p95 than the captured pre-change baseline, their query count does not grow with unrelated waves/variants, and all diagnostic/Challenge request wall-time lanes do not regress by more than 10%.
**Target-Perspective Output:** A learner still sees instant optimistic terminal output, then receives the next Adventure wave or final outcome sooner; a maintainer can run one documented command and inspect per-lane p50, p95, response size, and SQL-query counts without editing source.
**Truth Owner:** `RequestContextMiddleware` remains the production server-duration owner. The tracked profiler owns reproducible local before/after evidence. Adventure payload/query ownership remains in `adventures.payloads` and `adventures.services.selectors`; persisted command, reward, and completion truth remains in the existing services and database rows.
**Contract Boundary:** The existing `POST /api/adventure-runs/{id}/submit-command/` and `POST /api/challenge-runs/{id}/submit-command/` request/response contracts. No JSON field, status code, optimistic-state rule, or completion/reward semantic changes.
**Cutover:** Upgrade the tracked profiler in place to the current execution-payload contract, capture a pre-change baseline, then cut Adventure progress/published-wave reads to summary-only and prefetched paths. The optimized path replaces the over-fetch immediately; there is no compatibility facade or runtime switch.
**Displaced Path:** The profiler's command-only request bodies and single cold/order-sensitive timings, plus the Adventure progress query that prefetches `command_forms`, `waves`, and `waves__variants` for summary-only output, are displaced. Duplicate profilers or a second latency truth source must not remain.
**Value Density:** The slice targets the authoritative response wait and its largest evidenced query-shape defect without changing simulator, verifier, frontend animation, API schema, or database schema.
**Acceptance Evidence:** Committed before/after profiler output from identical seeded lanes; a focused query-shape test proving unrelated variants are not selected and query count stays bounded; existing Adventure/Challenge command-integrity and response-contract tests; and a visible local browser replay of one Adventure wave transition, one Adventure completion, and one Challenge completion with matching successful server logs.
**Evidence Lane:** Local real-API wall timing plus `CaptureQueriesContext`, followed by rendered frontend interaction and request logs. Cold-start is reported but excluded from steady-state improvement claims.
**Kill Criteria:** The profiler is tracked and repeatable; each mutating sample owns a fresh equivalently staged run and prebuilt execution payload; cold Adventure and cold Challenge measurements run in separate fresh pytest processes; warm-up is explicit; sample count and percentile calculation are deterministic; no benchmark imports frontend source at runtime; `ordered_levels_for` no longer prefetches wave/variant payloads; published Adventure waves are read from the hydrated/prefetched run when present; query count is bounded as unrelated variants are added; the API wire shape and completion/reward assertions remain unchanged; both warm Adventure intermediate-wave and final-completion request wall-time p95 values improve by at least 30% or the task is reported as implemented but unproven; diagnostic and Challenge warm request wall-time p95 values do not worsen by more than 10%; no dirty file outside the allowed scope changes byte-for-byte.
**Architecture Slice:** Frontend simulator -> generated API wrapper -> submit-command view/row lock -> command service/verifier/evaluator -> run/step persistence -> Adventure/Challenge payload -> HTTP response. This slice changes only the evidence harness and Adventure read-side payload hydration.
**Plan Review Gate:** Requires PRE review before execution.

## Outcome contract

- The optimization is measured from an authenticated real API call, not a helper-only microbenchmark.
- Cold import/URL-resolution cost and warmed command-processing cost are separate lanes.
- A faster response is valid only if the exact command, repository state, progress, reward, and response contracts remain intact.
- Relative before/after evidence uses the same machine, database backend, seeded scenarios, sample count, and process-warmup procedure.

## Architecture slice

### Files to create

- `backend/adventures/tests/test_adventure_payload_query_shape.py` - bounded-query and payload-parity coverage.
- `docs/goals/improve-command-latency/PRE_SLICE_BASELINE.md` - exact baseline command, environment, lane results, and query counts.
- `docs/goals/improve-command-latency/PRE_WORKTREE_MANIFEST.json` - pre-execution Git status plus SHA-256 for every existing dirty file, with explicit deletion markers.
- `docs/goals/improve-command-latency/EVIDENCE.md` - final before/after and browser evidence.

### Files to modify

- `backend/scripts/profile_command_latency.py` - replace the stale command-only/single-sample profiler with current frontend-shaped execution payloads and repeatable lanes in the disposable test database.
- `backend/adventures/services/selectors.py` - make the level-progress selector fetch only fields consumed by the response.
- `backend/adventures/payloads.py` - reuse prefetched published waves for count/index calculations and avoid fresh filtered queries.
- `README.md` - document the single profiler workflow alongside the existing validation commands.

### Files to avoid

- All existing dirty files, especially `backend/adventures/services/commands.py`, `backend/challenges/services/command_processing.py`, `backend/common/runtime/evaluation.py`, generated OpenAPI/TypeScript, and the dirty frontend battle/DAG files.
- `backend/common/git/**`, `backend/evaluation/**`, migrations, curriculum source/targets, reward services, and API serializers.
- Production deployment configuration and the generic GET-only `scripts/load_smoke.py`.

### Source of truth

- Production duration: the `git_it.request` `duration_ms` emitted by `backend/common/middleware.py`.
- Benchmark duration/query evidence: the new profiler's authenticated APIClient calls wrapped by `perf_counter` and `CaptureQueriesContext`.
- Response semantics: existing response serializers, payload tests, and runtime integrity tests.

### Read path

1. Submit view authenticates, locks, and hydrates the run.
2. Command service validates and evaluates the frontend-proposed transition.
3. On a transition, Adventure builds a full run payload.
4. `_level_progress_payload` reads sibling level summaries; wave count/index reads the hydrated level's waves.
5. DRF serializes the unchanged response.

### Write path

CommandStep/run/completion/reward writes are observed by the profiler but are not changed in this slice.

### Contract boundary

Both submit-command endpoints and their generated schemas remain byte-shape compatible. The profiler builds payloads with `testing.frontend_execution`, the same helper used by current integrity tests.

### Integration points

- Django ORM prefetch cache on the hydrated Adventure level.
- Adventure `adventure_run_payload` and `attempt_payload` wave index/count consumers.
- Existing request middleware and structured logging.
- Existing frontend optimistic submission hook; no frontend edit is planned.

### Migration/cutover

No schema or data migration. Once tests and evidence pass, the summary-only selector and prefetched-wave reader become the only Adventure transition read path.

### Displaced path

Remove the broad prefetch from `ordered_levels_for`; do not preserve it under a new selector or facade. Replace the profiler's stale command-only request path in place; do not preserve it or add a second profiler.

### Acceptance evidence gate

Completion requires both reproducible before/after server evidence and successful visible gameplay. Unit tests or a reduced query count alone are insufficient.

## Task 1: Establish a reproducible baseline

**Allowed scope:** Tracked profiler, `README.md`, and goal evidence only.

**Files:**

- `backend/scripts/profile_command_latency.py`
- `docs/goals/improve-command-latency/PRE_SLICE_BASELINE.md`
- `README.md`

**Expected output:**

- Opt-in pytest profiler running against the disposable pytest database.
- Separate `test_profile_adventure_cold` and `test_profile_challenge_cold` nodes, each intended to run alone in a fresh pytest process so route/import order cannot assign cold cost to whichever mode happens to run first.
- Explicit unmeasured warm-up requests before the separate steady-state test node.
- Separate Adventure diagnostic, Adventure intermediate-wave advancement, Adventure final-level completion, Challenge diagnostic, and Challenge completion warm lanes using published single-command variants or focused factories whose setup occurs outside the timed region. Intermediate advancement and final completion are distinct lanes because their writes and full-payload work differ.
- Every mutating transition/completion sample uses its own fresh run with the same pre-command database state and a prebuilt frontend-shaped execution payload; no measured run is reused after mutation.
- Per-lane request wall-time sample count, p50, p95, maximum, response bytes, and SQL query count; JSON-friendly output that can be pasted unchanged into evidence. Query timings are diagnostic only and cannot satisfy the latency threshold.
- At least 15 steady-state samples per lane by default, with sample count configurable by an environment variable.
- Pre-execution manifest records the porcelain status and SHA-256 of every dirty tracked/untracked file that predates this goal; deleted paths use an explicit `null` hash. Goal-package files and the exact allowed implementation files are identified separately so final verification can distinguish planned edits from protected user work.

**Verification command:**

```powershell
cd backend
$env:COMMAND_LATENCY_SAMPLES='15'
python -m pytest scripts/profile_command_latency.py::test_profile_adventure_cold -q -s
python -m pytest scripts/profile_command_latency.py::test_profile_challenge_cold -q -s
python -m pytest scripts/profile_command_latency.py::test_profile_steady_state -q -s
```

**Acceptance evidence:** `PRE_SLICE_BASELINE.md` records the exact three commands, commit/worktree note, Python/Django/database versions, both fresh-process cold results, and every warm lane result. Each mutating sample is shown to start from an equivalent run revision/state and return the expected transition/completion response. Reversing the order of warm lanes does not change which samples are classified as warm. `PRE_WORKTREE_MANIFEST.json` is captured before any Task 2 edit.

**Parallel:** No. It establishes the truth used by all later tasks.

## Task 2: Remove Adventure transition over-fetch

**Allowed scope:** Adventure read-side selector/payload and focused tests. Do not alter command/reward writes or the wire contract.

**Files:**

- `backend/adventures/services/selectors.py`
- `backend/adventures/payloads.py`
- `backend/adventures/tests/test_adventure_payload_query_shape.py`

**Expected output:**

- `ordered_levels_for` selects only level summary fields consumed by `_level_progress_payload` and does not prefetch command forms, waves, or variants.
- One payload helper returns published waves in `(sort_order, id)` order, using the hydrated level's prefetch cache when available and issuing one narrow query otherwise.
- `adventure_run_payload` and `attempt_payload` derive total/current wave values without repeated filtered relation queries.
- Adding unrelated waves, command forms, and large variant JSON to sibling levels does not change the response or increase the measured query count.

**Verification commands:**

```powershell
cd backend
python -m pytest adventures/tests/test_adventure_payload_query_shape.py -q
python -m pytest adventures/tests/test_adventure_command_payload_integrity.py common/tests/test_gameplay_response_contract.py -q
```

**Acceptance evidence:** The focused test captures identical public payload values before/after and isolates `_level_progress_payload`/its selector under `CaptureQueriesContext`: exactly one AdventureLevel summary SELECT; no command-form through-table, AdventureWave, or AdventureWaveVariant relation query; and no later deferred-field query while converting every returned level to its public level ref. The full payload test separately proves published wave count/index use the hydrated prefetch and remain bounded.

**Parallel:** No. It follows the baseline and owns the optimization.

## Task 3: Prove latency improvement and behavior parity

**Allowed scope:** Profiler rerun, relevant existing tests, local browser session, and goal evidence. Production code changes are not allowed in this task.

**Files:**

- `docs/goals/improve-command-latency/EVIDENCE.md`

**Expected output:**

- Before/after table for every lane with identical settings.
- Both warm Adventure intermediate-wave and final-completion p95 values are at least 30% lower, or the result is explicitly `implemented but unproven` and the goal remains active for a newly evidenced hotspot.
- Adventure diagnostic and both Challenge p95 values are no more than 10% worse.
- One visible Adventure wave transition, one final Adventure completion, and one Challenge completion succeed; terminal output, authoritative advancement/outcome, and structured request duration are captured.

**Verification commands:**

```powershell
cd backend
$env:COMMAND_LATENCY_SAMPLES='15'
python -m pytest scripts/profile_command_latency.py::test_profile_steady_state -q -s
python -m pytest adventures/tests challenges/tests common/tests/test_gameplay_response_contract.py -q
```

```powershell
cd frontend
npm test -- --run src/features/adventures/api/adventuresApi.test.ts src/features/challenges/api/challengeRunsApi.test.ts
npm run build
```

**Acceptance evidence:** `EVIDENCE.md` contains commands, outputs, thresholds, relevant request IDs/durations, and the visible interaction result. A final status/hash comparison against `PRE_WORKTREE_MANIFEST.json` proves every protected pre-existing dirty file has the same status and SHA-256 (or remains deleted); any mismatch blocks completion.

**Parallel:** No. It is the final gate.

## Non-goals

- Moving authoritative command execution to the browser or trusting arbitrary client state
- Redesigning terminal, battle, DAG, or outcome UI
- Changing command budgets, evaluation rules, rewards, completion, locking, throttling, or API schemas
- Optimizing cold deployment startup or generic health/list endpoints in this slice
- Broad ORM cleanup outside the Adventure transition payload
- Editing or normalizing unrelated dirty worktree files

## Risk if wrong

An unstable microbenchmark can claim an improvement caused by warm-up order. A too-narrow payload query can trigger lazy N+1 queries or omit next-level/wave data. Reusing an unfiltered prefetch can count unpublished waves. Changing response shape or completion writes could make a faster request incorrect. Every risk is gated by SQL inspection, contract tests, and a real frontend replay.
