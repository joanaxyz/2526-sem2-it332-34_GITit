# Goal: Home Hub Cross-Tab Companion Ownership

Use Krypton Execution to execute
`docs/goals/home-hub-cross-tab-companion-ownership/PLAN.md`.

Core rules:

- Treat `PLAN.md` as the source plan.
- Preserve the no-companion Overview and Profile behavior added after the
  historical Profile-workspace cutover.
- Keep `HomeHubView` as the sole Home Hub loadout reader because companion
  presence now affects both Overview and Profile.
- Pass only narrow companion values into the persistent Profile workspace;
  never pass a hook, query, or `PlayerLoadout` object.
- Keep Profile/Rank and combat state in their existing owners.
- Update the stale architecture guard without weakening unrelated rules.
- Do not edit Home Overview implementation, shared data/navigation owners,
  styles, backend/API/generated files, or historical goal evidence.
- Capture target-perspective evidence and say `implemented but unproven` if it
  cannot be captured.
