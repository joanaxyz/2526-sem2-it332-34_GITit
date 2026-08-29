# Goal: Backend Architecture and Production Readiness

Use Krypton Execution to execute `docs/goals/backend-production-readiness/PLAN.md`.

Core rules:
- Treat PLAN.md as the source plan.
- Preserve intent, ownership, contract, cutover, evidence, and kill criteria.
- Do not add a new dominant path without deleting, redirecting, demoting, or shimming the displaced path.
- Preserve all unrelated user-owned worktree changes.
- Capture acceptance evidence from the deployer and player perspectives.
- Say "implemented but unproven" if PostgreSQL migration or production evidence cannot be captured.
