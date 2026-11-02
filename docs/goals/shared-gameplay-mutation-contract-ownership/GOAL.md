# Goal: Shared Gameplay Mutation Contract Ownership

Make Adventure and Challenge command/workspace mutations depend on one exact request-contract owner from browser input through DRF validation and generated TypeScript.

The slice is complete when both gameplay modes use the same backend serializers and frontend payload adapters; equivalent OpenAPI components no longer collide or fork; PATCH file writes keep `path` required in the generated contract; DELETE documents the required query parameter; duplicated command/workspace payload types and endpoint casts are removed; real API mutations still preserve each mode's run/service semantics; displaced paths are guarded; and every unrelated dirty-worktree byte remains unchanged.

Gameplay services, models, command verification, simulator behavior, response payloads, caches, routes, throttles, rewards, UI, styles, and database state are outside this slice and must not change.
