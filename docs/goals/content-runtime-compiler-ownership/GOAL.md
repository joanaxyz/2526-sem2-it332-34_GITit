# Goal: Content Runtime Compiler Ownership

Use Krypton Execution to execute `docs/goals/content-runtime-compiler-ownership/PLAN.md`.

Core rules:
- Treat `PLAN.md` as the source plan.
- Preserve intent, ownership, contract, cutover, evidence, and kill criteria.
- Keep `authoring.compiler.ContentRuntimeCompiler` and `compile(*, content)` stable.
- Keep the transaction boundary on the public compiler facade.
- Do not leave persistence/detail methods or a second compiler path in the facade.
- Capture the database-graph, rollback, service-path, and dirty-worktree acceptance evidence.
- Say "implemented but unproven" if that evidence cannot be captured.
