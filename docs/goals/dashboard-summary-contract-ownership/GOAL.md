# Goal: Dashboard/Home Summary Contract Ownership

Use Krypton Execution to execute `docs/goals/dashboard-summary-contract-ownership/PLAN.md`.

Core rules:
- Treat `PLAN.md` as the source plan.
- Preserve intent, ownership, exact contract, cutover, evidence, and kill criteria.
- Keep `MetricsService.dashboard_summary()`, its route, and runtime values unchanged.
- Reuse the existing `RateMetricSerializer` without changing completed Stats semantics.
- Generate OpenAPI and TypeScript; never hand-edit generated artifacts.
- Delete loose/manual/intersection paths rather than adding compatibility aliases.
- Capture authenticated empty and populated real-endpoint evidence with raw wire assertions.
- Preserve the dirty worktree and every earlier architecture guard additively.
- Say `implemented but unproven` if direct real-path evidence cannot be captured.
