# Current Route and Seed Names Implementation Plan

**Intent:** Remove retired URL aliases and give the active Arcane Spire curriculum its canonical seed name.
**Current Behavior:** Compatibility routes redirect removed pages into unrelated current screens. `seed_legacy_modules` seeds the active curriculum while `seed_curriculum` names a retired, test-only fixture.
**Expected Outcome:** Current pages use their own URLs; obsolete aliases have no route registration. `seed_curriculum` owns the active Module 0-4 tree, `seed_curriculum_fixture` explicitly names the test-only retired fixture, and no active seed or scenario-bank module is named legacy.
**Target-Perspective Output:** `/stories/arcane-spire`, `/home`, `/shop`, and current editor/gameplay routes remain usable; removed URLs no longer silently open other screens. `manage.py seed_curriculum` and `seed_all` seed the same current story.
**Truth Owner:** Frontend `shared/navigation/routes.ts` and the router own current URLs. The active curriculum command owns the existing authored Module 0-4 data and stable database IDs.
**Contract Boundary:** Route definitions -> navigation consumers; Django command discovery -> canonical seed -> existing story/content rows.
**Cutover:** Delete alias registrations and their helper modules. Move the retired command to an explicit fixture name before moving the current seed into `seed_curriculum.py`; update every caller/import and scenario-bank name atomically.
**Displaced Path:** Delete `legacyRoutes.ts`, `LegacyRedirects.tsx`, old route constants, and the `seed_legacy_modules` command. No compatibility seed wrapper or obsolete URL redirect remains.
**Value Density:** Naming and routing changes remove two competing meanings without changing the curriculum or persisted identities.
**Acceptance Evidence:** Router matching/navigation tests, command-discovery and seed tests, canonical story counts and idempotency, generated-target consistency, TypeScript build, lint, and static searches for displaced imports/commands.
**Evidence Lane:** Source inventory -> atomic naming cutover -> router/seed regression tests -> generated-content preservation checks -> final source review.
**Kill Criteria:** No registered retired aliases; no production import of deleted route modules; `seed_curriculum` always means the current curriculum; fixtures remain disabled outside tests; normal seeds never recreate retired stories; no authored scenario data, stable keys, or unrelated dirty work is changed.
**Architecture Slice:** Frontend routing, active seed/scenario-bank naming, explicit retired fixture entry point, affected tests/tooling/docs.
**Plan Review Gate:** PRE self-review completed; no unresolved owner, caller, or preservation issue. No delegation is needed for this bounded slice.

## Architecture and Task Board

1. **Remove route aliases.** Edit `frontend/src/app/router.tsx` and `shared/navigation/routes.ts`; delete `LegacyRedirects.tsx` and `legacyRoutes.ts`; replace compatibility tests with current-route and removed-route tests. Remove obsolete `/tower`, `/towers`, `/archive`, `/my-tower`, shared/editor variants, `/performance`, `/gallery`, `/dashboard`, `/stats`, `/store`, and the old design-preview alias. Preserve `/`, current story/home/shop/authoring/gameplay/auth/admin routes. Correct challenge return links to use the run's own story. Verify actual router matches and default navigation.
2. **Name the canonical seed correctly.** Move retired `seed_curriculum.py` to `seed_curriculum_fixture.py`; move active `seed_legacy_modules.py` into `seed_curriculum.py`; update orchestration, fixture callers, active imports/constants, help text, and seed tests. Preserve all authored literals and persisted command-form/generated-target keys. Verify command discovery, fresh seed, reseed, guardrails, and existing seed/content tests.
3. **Name the current scenario source correctly.** Rename the active `revised_legacy_*` reader/runtime/data files to current scenario-bank names; update importer, generator, checks, and tests. Verify identical scenario JSON bytes and matching generated targets/case identities.
4. **Update guidance and verify.** Update README/currentness-check references and deployment/current seed documentation. Keep historical migrations and completed goal evidence as historical records. Run focused backend/frontend tests, build/lint, source searches, and final correctness/maintenance review. Capture results in `EVIDENCE.md`.

## Preservation and Review

- Do not alter the unrelated dirty KPI/UI/architecture work or variant-label changes already present in the shared workspace.
- Do not rename stored `legacy-m*` form slugs or generated target IDs: those are persisted content identities, not command/route entry points.
- Do not rewrite scenario prose or solution/evaluation payloads.
- Do not reseed the configured live database merely to prove a naming change; use isolated test databases.
- PRE review: old and new command ownership is explicit, fixture callers are distinguished before replacement, and removed aliases have no continuing redirect path.
