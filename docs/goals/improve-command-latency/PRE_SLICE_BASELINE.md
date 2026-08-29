# Command Latency Pre-Slice Baseline

Captured on 2026-08-28 before the Task 2 Adventure selector/payload edits.

## Environment

- Git HEAD: `ef6ea53c48707a2210c2f40e00d1f954fa062895`
- Branch: `main` (behind `origin/main` by three commits at capture time)
- Worktree: dirty before this goal; protected paths/statuses/SHA-256 values are in `PRE_WORKTREE_MANIFEST.json`
- OS/shell: Windows / PowerShell
- Python: 3.13.7
- Django: 6.0.5
- pytest: 9.1.1
- Database: Django pytest SQLite database
- Samples per warm lane: 15
- Percentile rule: nearest rank, `ceil(n * fraction) - 1`; with 15 samples p95 is the maximum and is intentionally reported alongside p50
- Payload stress: 10 sibling Adventure levels x 4 waves x 3 variants, with 16 KiB variant context, created outside every timed request
- Timed boundary: authenticated `APIClient.post` wrapped by `perf_counter` and `CaptureQueriesContext`

Every mutating request used a fresh run with counters at zero and a prebuilt frontend-shaped execution payload. The profiler asserted one precondition fingerprint per lane. Setup, user/run creation, payload construction, and endpoint warm-up were outside timed regions.

## Exact commands

```powershell
cd backend
$env:COMMAND_LATENCY_SAMPLES='15'
python -m pytest scripts/profile_command_latency.py::test_profile_adventure_cold -q -s
python -m pytest scripts/profile_command_latency.py::test_profile_challenge_cold -q -s
Remove-Item Env:COMMAND_LATENCY_REVERSE_LANES -ErrorAction SilentlyContinue
python -m pytest scripts/profile_command_latency.py::test_profile_steady_state -q -s
$env:COMMAND_LATENCY_REVERSE_LANES='true'
python -m pytest scripts/profile_command_latency.py::test_profile_steady_state -q -s
```

All four invocations passed.

## Isolated cold probes

Each row came from the only request in a fresh pytest process. Cold values are reported for observability and are excluded from the optimization threshold.

| Lane | Request p50/p95/max (ms) | Queries | Response bytes |
| --- | ---: | ---: | ---: |
| Adventure final completion | 291.92 / 291.92 / 291.92 | 33 | 1,347 |
| Challenge completion | 310.51 / 310.51 / 310.51 | 38 | 2,893 |

The matching structured middleware durations were 279.97 ms for Adventure and 294.04 ms for Challenge. This confirms that separate processes assign cold cost independently instead of charging the first mode in one shared run.

## Primary warm baseline

Both endpoints received an explicit unmeasured completion request before these lanes. This forward-order run is the threshold baseline used for before/after comparison.

| Lane | Request p50 (ms) | Request p95/max (ms) | Query p50/p95/max | Response p50/p95/max (bytes) |
| --- | ---: | ---: | ---: | ---: |
| Adventure diagnostic | 15.88 | 18.37 | 8 / 8 / 8 | 1,429 / 1,431 / 1,431 |
| Adventure wave advance | 57.65 | 179.89 | 29 / 29 / 29 | 2,816 / 2,816 / 2,816 |
| Adventure final completion | 51.51 | 181.03 | 33 / 33 / 33 | 1,350 / 1,350 / 1,350 |
| Challenge diagnostic | 6.44 | 13.72 | 5 / 5 / 5 | 2,082 / 2,083 / 2,083 |
| Challenge completion | 21.61 | 27.61 | 38 / 38 / 38 | 2,896 / 2,896 / 2,896 |

Primary acceptance thresholds derived from this run:

- Adventure wave-advance p95: at most 125.92 ms (30% below 179.89 ms)
- Adventure completion p95: at most 126.72 ms (30% below 181.03 ms)
- Adventure diagnostic p95: at most 20.21 ms (10% control allowance)
- Challenge diagnostic p95: at most 15.09 ms (10% control allowance)
- Challenge completion p95: at most 30.37 ms (10% control allowance)

## Reversed warm-lane order control

All emitted rows remained `cold: false`, proving lane classification is independent of measurement order.

| Lane | Request p50 (ms) | Request p95/max (ms) | Queries |
| --- | ---: | ---: | ---: |
| Challenge completion | 22.15 | 30.71 | 38 |
| Challenge diagnostic | 6.54 | 99.93 | 5 |
| Adventure final completion | 49.80 | 178.39 | 33 |
| Adventure wave advance | 42.64 | 129.35 | 29 |
| Adventure diagnostic | 9.90 | 13.35 | 8 |

The isolated 99.93 ms Challenge diagnostic outlier demonstrates why p50 and order-control evidence are retained. Threshold claims use the declared primary forward run and an identical forward post-change run, not whichever order is more favorable.

## Controlled legacy reproducibility baseline

The first post-change rerun exposed a benchmark-harness confound: Python cyclic collection could start inside a timed request after the stress catalog and fresh-run fixtures had been created. The profiler was therefore stabilized by calling `gc.collect()` immediately before each timed request; collection remains outside the measured `perf_counter` and `CaptureQueriesContext` boundary. To keep the comparison honest, the exact legacy selector and payload behavior was temporarily restored, measured with 20 samples under the stabilized harness, and then replaced again with the planned optimization. No production behavior other than the two planned Adventure read-side changes differed between these two runs.

Both controlled forward runs used:

```powershell
cd backend
$env:COMMAND_LATENCY_SAMPLES='20'
Remove-Item Env:COMMAND_LATENCY_REVERSE_LANES -ErrorAction SilentlyContinue
python -m pytest scripts/profile_command_latency.py::test_profile_steady_state -q -s
```

| Lane | Legacy p50 (ms) | Legacy p95 (ms) | Legacy queries |
| --- | ---: | ---: | ---: |
| Adventure diagnostic | 19.09 | 29.86 | 8 |
| Adventure wave advance | 73.24 | 99.76 | 29 |
| Adventure final completion | 80.01 | 107.59 | 33 |
| Challenge diagnostic | 12.73 | 18.63 | 5 |
| Challenge completion | 41.32 | 68.44 | 38 |

These are the final retained controlled legacy results from `CONTROLLED_LEGACY_RESULTS.json`. They supersede an earlier 20-sample controlled pass whose summary was not retained with raw response-size/fingerprint metadata. The paired optimized run was captured immediately afterward, and every lane has an identical cross-process-stable precondition fingerprint and response-size distribution. This supplemental baseline, rather than either GC-affected 15-sample outlier, is the like-for-like threshold source used in `EVIDENCE.md`. It was acquired after the initial pre-slice capture only because that capture revealed the need for the controlled rerun; the chronology and result sets are retained here.

## Baseline interpretation

- Adventure transitions are the evidenced optimization target: their medians are roughly 2-9x the diagnostic/control medians and they execute 29-33 queries.
- Query count is supporting evidence only; the success threshold is request wall-time p95.
- The stale profiler's command-only bodies and single order-sensitive sample are fully displaced by the tracked current-contract harness.
