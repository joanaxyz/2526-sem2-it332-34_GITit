# Goal: Stats Summary Contract Ownership

Use Krypton Execution to execute `docs/goals/stats-summary-contract-ownership/PLAN.md`.

Core rules:
- Treat PLAN.md as the source plan.
- Preserve intent, ownership, contract, cutover, evidence, and kill criteria.
- Keep `MetricsService.stats_summary()` and its runtime payload unchanged.
- Make `progress/serializers.py` the documented Stats/Dashboard response-contract owner; keep the shared Wallet/Shop contract in `common`.
- Generate OpenAPI and TypeScript; never hand-edit generated artifacts.
- Delete the false fields, handwritten response object, and response intersection rather than adding compatibility aliases.
- Capture an authenticated real-endpoint request/response/serializer trace.
- Preserve the existing dirty worktree and all earlier architecture guards additively.
- Say `implemented but unproven` if direct endpoint evidence cannot be captured.
