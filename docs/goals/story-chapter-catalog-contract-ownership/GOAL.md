# Goal: Story and Chapter Catalog Contract Ownership

Use Krypton Execution to execute `docs/goals/story-chapter-catalog-contract-ownership/PLAN.md`.

Core rules:

- Treat `PLAN.md` as the source plan.
- Preserve its intent, ownership, exact contracts, cutover, evidence lane, and kill criteria.
- Keep runtime catalog values, selectors, routes, locking rules, completion arithmetic, and consumer behavior unchanged.
- Make `backend/curriculum/serializers.py` the complete top-level and nested response-contract owner for `/api/stories/` and `/api/chapters/`.
- Generate OpenAPI and TypeScript; never hand-edit generated artifacts.
- Replace handwritten `Story` and `LearningChapter` shapes with generated aliases and remove their two response overrides without adding compatibility adapters.
- Preserve the existing dirty worktree and all earlier architecture guards additively.
- Keep chapter overview/book, Shop mutations, auth, and gameplay runtime contracts out of scope.
- Capture direct real-endpoint evidence; say `implemented but unproven` if it cannot be captured.

