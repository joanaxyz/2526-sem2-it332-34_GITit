# Overview and Admin Performance Consolidation — Pre-slice Baseline

Captured 2026-09-12 on branch `main` at `dba7be8a9bddfdd78c18a14b132d8458f73f6bf0` before production edits for this goal.

## Preservation contract

- The worktree contained 83 modified/deleted/untracked status entries before this slice. Every path outside `PLAN.md`'s explicit create/modify/delete lists is frozen.
- Existing changes in the overlapping files below are user-owned. Implementation may edit only task-related hunks and must preserve their baseline semantics.
- `docs/PERFORMANCE_KPIS.md` was already deleted and must remain untouched.
- Generated API files may change only through `scripts/generate_api_contract.py`; the existing onboarding enum change must survive regeneration.
- The moved onboarding implementation lives under `frontend/src/features/onboarding/{components,hooks,pages,utils}`. The deleted flat onboarding paths are displaced user work and must not be restored.

## Overlapping dirty targets

Format: `path | bytes | SHA-256`.

```text
frontend/src/features/home/components/HomeHubView.tsx | 4356 | ECF94907BCE05D81B11A246A1220FD97EA81BAC4E1E5DA964DC2A1B15C43DA2E
frontend/src/styles/features/home/stats-layout.css | 14026 | 483F983CA03C0CA0FBEB1BE880FB999543845B3B8B5BA9148B0CACDDEC9B1FAE
frontend/src/styles/features/home/stats.css | 160 | 09164669B3A3185E55C2431CDB28D828F232E8DA30E3EBFC0AF19CC3FFE5F75A
frontend/src/styles/features/home/stats-kpis.css | 3436 | 5C69442DE4C14E9613C0B16E1FD0616DCFA0CE2AC092F8384AB4DACD57FBD55E
frontend/src/shared/api/generated/apiTypes.ts | 54262 | 13F8FA2A10D274EFDCA2B46DDAA12D728B1A017854C8DBF5994A660AD3262367
frontend/src/shared/api/generated/openapi.json | 243472 | 2DBB9CF66E5311E54BF5AB373426D9EA60E3D97EBDC1CA31F6F569CCCEFCEAE7
scripts/checks/check_architecture_boundaries.py | 68870 | 95103AD700F22F8660698F4C5454D480EB3DD658942A897AE21C503D72D242C1
backend/common/tests/test_architecture_guard_algorithms.py | 30567 | F20B4B0CE2CD9513584E382E2FBCFDABE86840670BA4A93148692B7B1257D23E
frontend/src/features/onboarding/components/HomeOnboarding.tsx | 7654 | 5581738358E7D23AD71C6736A20C8923912232D031DACB886F89F3B221578676
frontend/src/features/onboarding/pages/OnboardingJourney.test.tsx | 13735 | 07CAF0E6B9490CDFDC30C9D0DFD966E8B547D5B1C58671159FCE5732DC30F34D
docs/PERFORMANCE_KPIS.md | absent before slice
```

## Read-path baseline

- Player performance: `GET /api/progress/performance/` -> `MetricsService.performance_summary(player=...)`; Runebound story, Modules 1–4, replay-excluded.
- Admin analytics: `GET /api/admin/analytics/` -> `AdminAnalyticsAPIView` with `IsStaff` -> `admin_analytics_payload`; no Runebound technical metrics before this slice.
- The pictured “Recommended next step” is a static `companionRequired` branch, not a next-level resolver.
- The current Overview KPI strip mixes Dashboard-summary KPIs and Stats accuracy and is not equivalent to the Runebound performance contract.
- `PerformanceModule` has no CAR field; module CAR must not be fabricated.

## Baseline verification

- Explorer-reported focused frontend lane: 6 files, 10 tests passed.
- Explorer-reported backend Admin/performance lane: 26 tests passed.
- Browser baseline: unauthenticated `/admin` redirects to `/login`.
- Admin visual defect baseline: the app has no Tailwind runtime, but Admin markup relies on undefined responsive/spacing utilities such as `md:flex`, `md:hidden`, `lg:grid-cols-4`, `max-w-[1500px]`, and `overflow-x-auto`. This leaves the desktop rail hidden, mobile tabs visible at desktop, analytics grids collapsed, spacing absent, and the per-story table clipped.
