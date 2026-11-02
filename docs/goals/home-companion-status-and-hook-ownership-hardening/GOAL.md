# Goal: Truthful Home Companion Status and Alias-Safe Hook Ownership

Use Krypton Execution to execute
`docs/goals/home-companion-status-and-hook-ownership-hardening/PLAN.md`.

Core rules:
- Treat `PLAN.md` as the source plan.
- Preserve intent, ownership, contract, cutover, evidence, and kill criteria.
- Do not pass React Query state or the raw `PlayerLoadout` result into Home leaf components.
- Do not show an absent-companion CTA until the loadout read has succeeded.
- Reject aliased direct imports of Home integration hooks outside their named owners.
- Capture loading, error, empty, and ready behavior from the target perspective.
- Say `implemented but unproven` if that evidence cannot be captured.
