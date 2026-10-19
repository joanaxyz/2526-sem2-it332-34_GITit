# Current Route and Seed Names Evidence

## Current behavior

- `seed_curriculum` now owns the current Arcane Spire Module 0-4 curriculum. `seed_all` invokes that command, followed by the command library and drills.
- `seed_curriculum_fixture` explicitly names the retired multi-story test fixture and still refuses to execute outside the test harness.
- Django command discovery reports the current and fixture commands; `seed_legacy_modules` is absent. No forwarding command was retained.
- The current authored scenario files are `scenario_bank.json`, `scenario_bank.py`, and `scenario_runtime.py`. Generators, the scenario importer, structural checks, and tests use their new names.
- Eighteen obsolete URL aliases have no router match, including old story/shared/editor URLs and `/performance`, `/gallery`, `/dashboard`, `/stats`, and `/store`. The compatibility route module and redirect component were deleted; their prior versions remain recoverable from Git history.
- Current story, home, shop, authoring, gameplay, auth, and admin routes remain registered. Story-map layout classification uses the same exact route patterns as routing.
- Challenge return navigation now selects the run's own story and chapter instead of always selecting the default story.

## Exact curriculum preservation

Before and after the rename, the full story/chapter/orientation/form/level payload has SHA-256:

```text
a2a032da543b28b689795f371ae051303d865f2528e5d8ec1561f8c711ad65f7
```

All 2,321 generator case inputs retain SHA-256:

```text
8c3ead28a9cb053fc362f0aec2c7bf35addbf8c45cff48e6763dcac49dd7e4a9
```

The renamed scenario JSON is byte-identical, with SHA-256:

```text
19a4fe0239b680efa911538ff01075dc20f6df62a5a2c6dfef422e5230752c02
```

No live database reseed or migration was performed for this naming change. Stored form slugs, scenario IDs, generated targets, and migration history retain their original identities.

## Verification

- Backend canonical seed, fixture idempotency/guardrails, scenario contract, story access, orchestration, and progress tests: **31 passed**.
- Route/auth/companion regression run: **47 passed**.
- Current/removed route, challenge return-navigation, and abandoned-run regression run: **46 passed**. This overlaps the first frontend run and is not an additional unique-test total.
- Full backend test collection: **2,575 collected**, with no missing imports or collection failures.
- Frontend production build: **passed**.
- ESLint on the changed frontend files: **passed**.
- Ruff lint/format on the changed backend and script files: **passed**.
- Generated target structural check: **2,321 cases consistent**.
- Root documentation currentness check: **passed**.
- `git diff --check`: **passed**, with line-ending notices only.
- The architecture check reports only the previously known 423-line `frontend/src/shared/level/components/useWorkspaceTourTransform.ts` size violation. That file is outside this change; no new route or seed ownership violation was reported.

## Final reviews

- **POST alignment:** The active seed has one canonical command name; the retired fixture is explicit; deleted aliases have no substitute redirect path.
- **Correctness:** Canonical seeding still creates the sole Arcane Spire tree with 5 chapters, 21 levels, and 63 tiers. Repeated seeding preserves IDs. Fixture guards remain effective. Gameplay return navigation retains story/chapter context.
- **Maintainability:** Removed route constants/helpers and the old command are gone rather than wrapped. Current guidance and tooling use the new names. Historical goals and database identities remain historical records.
- **Verifier:** Route-match tests, command discovery, functional seed tests, and exact pre/post data hashes prove the requested behavior. Unrelated dirty KPI/UI/model work remains in the shared workspace and was not discarded.
