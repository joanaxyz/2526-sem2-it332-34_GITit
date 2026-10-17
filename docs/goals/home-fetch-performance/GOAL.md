# Goal: Home Fetch Performance

Use Krypton Execution to execute `docs/goals/home-fetch-performance/PLAN.md`.

Core rules:

- Preserve all player-visible metric values and activity bucketing.
- Replace the parent-join command-step scan; do not keep it as a fallback.
- Range changes must call only the activity endpoint.
- Keep activity query keys below the stats root so existing invalidations remain correct.
- Capture query-plan, query-count, contract, test, and build evidence.
