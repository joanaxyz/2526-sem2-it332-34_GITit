# Goal: Home Overview Ownership and CSS Cutover

Use Krypton Execution to execute `docs/goals/home-overview-ownership/PLAN.md`.

Core rules:

- Treat `PLAN.md` as the source plan.
- Preserve intent, ownership, contract, cutover, evidence, and kill criteria.
- Keep the public `HomeStatsView({ home, stats })` contract and visible DOM/class behavior stable.
- Cut over the pure presentation model and two focused render owners atomically; do not leave a second current-looking Overview path.
- Delete the two legacy CSS files/selectors and dead `latestAchievement` helper after preserving still-live responsive rules in the canonical owners.
- Leave the pre-existing OpenAPI/runtime Stats-key drift and misplaced Profile `[hidden]` selector for separately planned contract/ownership slices.
- Preserve all pre-existing Slice 1-4 work and avoid protected backend/API/shared/Home surfaces.
- Capture real browser screenshots, breakpoint/cascade measurements, filter/navigation traces, exact request counts, and clean-error evidence.
- Say `implemented but unproven` if target-perspective evidence cannot be captured.
