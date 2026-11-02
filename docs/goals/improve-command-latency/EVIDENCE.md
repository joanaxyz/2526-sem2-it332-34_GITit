# Command Latency Evidence

Captured on 2026-08-28/29 against Git HEAD `ef6ea53c48707a2210c2f40e00d1f954fa062895` in the protected dirty worktree recorded by `PRE_WORKTREE_MANIFEST.json`.

## Outcome

The Adventure transition payload now avoids sibling-content over-fetch and repeated filtered wave queries while preserving the public response contract. Under the controlled, current-contract steady-state profiler, Adventure wave-advance p95 fell by 59.69% and final-completion p95 fell by 53.12%. All three control lanes improved. The required 30% target and 10% control guardrail are satisfied.

## Controlled benchmark

The initial 15-sample pre-slice capture is retained in `PRE_SLICE_BASELINE.md`. It revealed Python GC pauses that could begin inside the timed boundary after stress-fixture creation. The tracked profiler now runs `gc.collect()` immediately before, and outside, each timed request. The exact legacy selector/payload implementation was temporarily reinstated and measured with the stabilized harness before the optimized implementation was restored. Both sides used the same database, stress catalog, frontend-shaped request payloads, fresh-run state, lane order, nearest-rank percentile rule, and 20 samples.

```powershell
cd backend
$env:COMMAND_LATENCY_SAMPLES='20'
Remove-Item Env:COMMAND_LATENCY_REVERSE_LANES -ErrorAction SilentlyContinue
python -m pytest scripts/profile_command_latency.py::test_profile_steady_state -q -s
```

| Lane | Legacy p50 / p95 (ms) | Optimized p50 / p95 (ms) | p95 change | Queries before -> after | Guardrail |
| --- | ---: | ---: | ---: | ---: | --- |
| Adventure diagnostic | 19.09 / 29.86 | 13.86 / 23.22 | -22.24% | 8 -> 8 | pass |
| Adventure wave advance | 73.24 / 99.76 | 22.15 / 40.21 | **-59.69%** | 29 -> 23 | pass (>=30%) |
| Adventure final completion | 80.01 / 107.59 | 36.20 / 50.44 | **-53.12%** | 33 -> 29 | pass (>=30%) |
| Challenge diagnostic | 12.73 / 18.63 | 12.12 / 15.51 | -16.75% | 5 -> 5 | pass |
| Challenge completion | 41.32 / 68.44 | 34.70 / 52.77 | -22.90% | 38 -> 38 | pass |

The exact JSON rows are retained in `CONTROLLED_LEGACY_RESULTS.json` and `CONTROLLED_OPTIMIZED_RESULTS.json`. They include sample counts, p50/p95/max latency, p50/p95/max query counts, response-byte distributions, and stable precondition fingerprints. Each corresponding legacy/optimized lane has the same fingerprint and response-size distribution, directly auditing equivalent starting state and unchanged wire size.

The optimized reverse-order control also passed with every lane classified warm:

| Reverse-order lane | p50 / p95 (ms) | Queries |
| --- | ---: | ---: |
| Challenge completion | 32.79 / 41.68 | 38 |
| Challenge diagnostic | 11.66 / 16.58 | 5 |
| Adventure final completion | 41.29 / 59.96 | 29 |
| Adventure wave advance | 24.81 / 38.73 | 23 |
| Adventure diagnostic | 13.93 / 19.32 | 8 |

The exact reversed rows are retained in `CONTROLLED_OPTIMIZED_REVERSE_RESULTS.json`. The original cold probes remain documented separately and are not used to claim this steady-state improvement.

## Behavior and query-shape verification

- `python -m pytest adventures/tests/test_adventure_payload_query_shape.py -q`: **3 passed**. The tests prove the level-summary selector avoids wave, variant, and command-form relations; public level refs do not trigger deferred-field queries; and hydrated published waves are reused for total/current index values.
- `python -m pytest adventures/tests/test_adventure_command_payload_integrity.py common/tests/test_gameplay_response_contract.py -q`: **6 passed, 1 failed**. All Adventure integrity assertions passed. The sole failure was the pre-existing protected Challenge full-success schema assertion expecting `battle_stage`; `backend/challenges/payloads.py` already omitted that field and was not modified by this goal.
- `python -m pytest adventures/tests challenges/tests common/tests/test_gameplay_response_contract.py -vv --durations=15`: **46 passed, 1 failed in 267.78s**. The same protected Challenge schema mismatch was the only failure; all Adventure and Challenge submit-integrity tests passed.
- Ruff check and Ruff format check passed for `backend/scripts/profile_command_latency.py`, `backend/adventures/services/selectors.py`, `backend/adventures/payloads.py`, and `backend/adventures/tests/test_adventure_payload_query_shape.py`.
- `npm test -- --run src/features/adventures/api/adventuresApi.test.ts src/features/challenges/api/challengeRunsApi.test.ts`: **2 files, 7 tests passed**.
- `npm run build`: **passed**, with 2,662 modules transformed.

## Visible learner replay

A disposable story, chapter, two-wave Adventure level, Challenge trial, and user were exercised through the real rendered frontend. `agent-browser` filled each visible terminal textbox and pressed Enter; its network trace recorded exactly three submit-command Fetch POSTs, all returning 200. The structured server log and rendered outcomes agree:

- Adventure intermediate submit advanced from wave 1/2 to wave 2/2 with `git add README.md` visible in the terminal. Structured request `ef29626a5d614017834f365a0acf7770` returned 200 in 4,550.53 ms. Screenshot: `NATIVE_ADVENTURE_WAVE_2.png`.
- Adventure final submit showed `Adventure cleared`, 3/3 stars, waves 2/2, and `Challenge unlocked`. Structured request `e98e2ab8e3c24deeb618361e8e805d7a` returned 200 in 6,567.38 ms. Screenshot: `NATIVE_ADVENTURE_CLEARED.png`.
- Challenge completion showed the staged `README.md`, terminal command `git add README.md`, contextual feedback that the staging area and working tree changed, 3/3 stars, and `Level complete`. Structured request `cf9e2a0497db48eeb4828f35f6fe58df` returned 200 in 8,696.60 ms. Screenshot: `NATIVE_CHALLENGE_CLEARED.png`.

Those local-server durations include the configured external development database and are end-to-end observability evidence only; they are not substituted for the isolated pytest benchmark. An earlier browser driver could not dispatch the terminal's native submit event, so its API-only fallback was not accepted as the plan's visible-interaction gate. The retained screenshots and request IDs above are from the later native textbox/Enter flow that closed that gap.

After capture, the disposable user and 25 dependent run/progress/session/loadout records were deleted. The dedicated curriculum tree deleted nine chapter descendants plus the story in dependency order; both identifying queries returned zero afterward. The browser session was closed, its saved credential profile was deleted, both local listeners were stopped, and all ten ignored native-replay server logs were removed.

## Concurrent worktree notice

At `2026-08-28T18:49:46.1930578Z`, after the final reverse-order benchmark had completed at `18:49:23Z`, `frontend/src/styles/features/battle/stage-combatants.css` acquired an unrelated four-line enemy-portrait style edit from concurrent workspace activity. The path was clean and absent from the pre-execution dirty manifest, was never an allowed goal path, and was not touched by a goal command. It is preserved untouched as user work. Its HEAD blob is `dd636446cda779860ab10fd42364ae265b5b1eca`, its concurrent blob is `24e314f14c9b4a74c5dc8a50204a3b3b4c7a97fa`, and its current SHA-256 is `8295E9994EAE427CE3E192561A43C8B612AEC0E2DB78117DB062E430D77C2B75`.

This late concurrent path is reported separately instead of being retroactively inserted into `PRE_WORKTREE_MANIFEST.json`; changing the locked pre-execution manifest would make that artifact misleading. It is the only status path outside the 63 protected entries, five allowed task files, and the goal-package prefix.

## Worktree preservation

The final verifier confirmed that all 63 entries in `PRE_WORKTREE_MANIFEST.json` retain their exact porcelain status and SHA-256. The concurrent CSS edit documented above is the sole path outside the protected entries, allowed task files, and goal-package prefix; it was independently verified as later user work and preserved untouched. The only implementation paths owned by this goal are:

- `README.md`
- `backend/scripts/profile_command_latency.py`
- `backend/adventures/services/selectors.py`
- `backend/adventures/payloads.py`
- `backend/adventures/tests/test_adventure_payload_query_shape.py`
- `docs/goals/improve-command-latency/`

No protected pre-existing mismatch or unexpected goal-created path was found.
