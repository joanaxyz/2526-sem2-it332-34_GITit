# Goal: Home Hub Profile Workspace Ownership

Use Krypton Execution to execute `docs/goals/home-hub-profile-workspace-ownership/PLAN.md`.

Core rules:
- Treat PLAN.md as the source plan.
- Preserve intent, ownership, contract, cutover, evidence, and kill criteria.
- Keep `HomeHubView` as the unchanged four-prop URL/backdrop composition boundary.
- Keep Profile always mounted under `hidden`; do not trade state/cache behavior for conditional rendering.
- Move Profile integration, Profile/Rank rendering, and combat/spellbook choreography to their named sole owners.
- Delete the unused generic showcase-move path and clean delayed timers on replacement/unmount.
- Do not modify Overview, Loadout, Home CSS, backend/API/generated/shared truth owners, or completed Slice 1-3 work except the two additive architecture files.
- Capture deterministic browser evidence from the real dev preview and say `implemented but unproven` if it cannot be captured.
