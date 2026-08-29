# Goal: Improve Command Latency

Use Krypton Execution to execute `docs/goals/improve-command-latency/PLAN.md`.

Core rules:

- Treat `PLAN.md` as the source plan.
- Preserve intent, ownership, contract, cutover, evidence, and kill criteria.
- Keep the current dirty gameplay/runtime/frontend files byte-for-byte unchanged unless the plan explicitly names them; this plan does not.
- Separate cold-start from steady-state measurements and use identical seeded lanes for before/after comparisons.
- Do not add a new dominant path without deleting, redirecting, demoting, or shimming the displaced path.
- Capture acceptance evidence from the learner and maintainer perspectives.
- Say `implemented but unproven` and keep the goal active if the latency threshold or visible gameplay evidence cannot be captured.
