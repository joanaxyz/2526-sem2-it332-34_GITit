# Goal: Architecture Guard Policy Modularization

Make the repository architecture guard a maintainable orchestration boundary instead of a 5,367-line policy monolith.

The slice is complete when reusable Python/TypeScript source analysis and the Catalog, Auth, Progress, and Gameplay contract policies each have one focused owner; the existing checker is below 2,000 lines and only orchestrates those extracted policies alongside its remaining workflow/general rules; focused tests import canonical modules instead of a `runpy` namespace; every existing rule, violation order, message, command, stdout/stderr behavior, and exit code is preserved; and every unrelated dirty-worktree byte remains unchanged.

No backend or frontend runtime behavior, generated API contract, product policy, CI command, wrapper command, workflow invocation, migration, database state, asset, or prior goal artifact may change in this slice.
