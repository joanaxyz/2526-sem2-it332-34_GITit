# Goal: Admin Console HTTP and Read-Model Ownership — Slice 2

Use Krypton Execution to execute `docs/goals/admin-console-http-read-model-ownership/PLAN.md`.

Core rules:
- Treat `PLAN.md` as the source plan.
- Preserve intent, ownership, contract, cutover, evidence, and kill criteria.
- Keep the existing 15-class `adminconsole.views` import surface and every external API contract unchanged.
- Delete the flat view implementation atomically; do not leave a second query path or shim file.
- Capture acceptance evidence from the target and maintainer perspectives.
- Say "implemented but unproven" if that evidence cannot be captured.
