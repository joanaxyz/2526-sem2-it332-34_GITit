# Home Hub Profile Workspace Ownership Implementation Plan

**Intent:** Advance the active codebase-maintainability goal by turning the 397-line Home Hub into a small URL-tab composition boundary with explicit owners for Profile integration, profile/rank rendering, and companion combat/spellbook choreography.
**Current Behavior:** `HomeHubView.tsx` is three lines below the global 400-line ceiling and simultaneously owns URL query mutation, background composition, Home tab markup, Profile/Rank UI state and markup, learned-skill and player-loadout reads, companion runtime conversion, sprite/effect refs, geometry, timers, and spellbook rendering. It has no direct workflow test; existing Home coverage is limited to three achievement utility cases.
**Expected Outcome:** `HomeHubView` owns only the backdrop, outer Home tab contract, and Overview/Loadout/Profile composition. An always-mounted `HomeProfileWorkspace` owns Profile data integration and the grid root. `HomeProfilePanel` owns Profile/Rank local state and display derivation. `HomeCombatShowcase` owns the sprite, spellbook, selection, geometry, effects, and timer lifecycle. No duplicate current-looking path remains.
**Target-Perspective Output:** A player sees the same Overview, Loadout, and Profile surfaces at the same URLs; unrelated query parameters survive replace-navigation; Profile/Rank and chosen-spell state survive an outer-tab round trip; rank, currency, clears, learned commands, companion art, and attack effects remain correct on desktop and mobile. A maintainer can change URL composition, Profile presentation, or combat choreography in one named owner without scanning a 397-line mixed component.
**Truth Owner:** Backend progress/stats services and existing frontend contracts remain authoritative for data; `shared/progress/rank.ts` remains authoritative for rank derivation; `usePlayerLoadout`, `useLearnedSkills`, companion runtime, sprite animation, and effect registry remain authoritative integrations. Within Home, `HomeHubView` owns outer URL composition, `HomeProfileWorkspace` owns Profile integration, `HomeProfilePanel` owns Profile/Rank presentation, and `HomeCombatShowcase` owns local attack choreography.
**Contract Boundary:** Preserve `HomeHubView({ home, stats, playerName, gitcoins })`, `/home`, `/design-preview/home`, the `tab=loadout|profile` contract, absent/invalid tab as Overview, unrelated search parameters, `{ replace: true }`, Profile remaining mounted while hidden, class names, DOM order, CSS variables, responsive layout, data precedence, cache coupling, skill labels, effect routing, loading/empty states, reduced-motion settling, and the existing Overview/Loadout children. The only intentional behavior correction is cancellation of delayed attack/effect work when replaced or unmounted.
**Cutover:** Add tests against the named Home Hub export, create the three focused owners, then atomically replace embedded Profile/workflow logic in `HomeHubView`. Current callers keep the same import and four-prop contract. No fixture-only production prop or compatibility barrel is introduced.
**Displaced Path:** `HomeHubView.tsx` may no longer import learned-skill/player-loadout hooks, battle effects, companion runtime, sprite animation/timing/types/pixel-bound utilities, rank ladder rendering, wallet icon, command icon helpers, or contain `ShowcaseMove`, effect geometry, animation refs/timers, Profile/Rank/Sprite/Spellbook markup, `playMove`, or `attackWithSkill`. The unused generic Run/Hurt/portrait showcase metadata is deleted; only the actually reachable Attack-to-Idle path remains.
**Value Density:** This removes the highest-ranked remaining frontend hotspot, adds direct coverage to an untested interactive surface, makes delayed effects safe on unmount, and creates durable ownership rules without touching the already-large Stats or write-owning Loadout workflows.
**Acceptance Evidence:** Deterministic Home Hub integration tests; architecture rejection of displaced imports/markers and reverse child dependencies; real dev-preview browser interaction with deterministic mocked learned-skill/shop reads; URL/state round-trip trace; Attack-to-Idle/effect trace; 1440x900 and 390x844 screenshots; 1280 and mobile overflow measurements; keyboard/accessibility observations; clean console/errors; build/lint/dead-code/API/quality gates; full-suite result; protected-path hashes; and independent POST/correctness/maintainability/verifier verdicts.
**Evidence Lane:** Dirty-worktree and browser baseline -> integration harness -> atomic Profile workspace/panel/combat cutover with timer cleanup -> architecture guard -> focused/full/static gates -> deterministic dev-preview browser evidence -> protected-state audit -> POST/correctness/maintainability/verifier reviews.
**Kill Criteria:** Hub at most 140 lines; workspace at most 100; Profile panel at most 190; combat showcase at most 240; one outer query-tab owner; one call each to `usePlayerLoadout` and `useLearnedSkills`, both in the workspace; Profile remains mounted under `hidden`; child components remain API/React Query/router-free; combat is the sole sprite/effect/timer owner; no unused generic showcase moves; no rendering child imports Hub/page; no production fixture seam; no Home CSS, backend, API, query-key, router, shared rank/cosmetic/story/sprite/effect, generated-contract, Stats, or Loadout edit; existing Slice 1-3 state remains byte-identical except the two explicitly shared architecture files.
**Architecture Slice:** `HomeHubView -> HomeProfileWorkspace -> HomeProfilePanel + HomeCombatShowcase`; external read owners remain unchanged and feed the workspace through existing hooks. See the full map below.
**Plan Review Gate:** Requires PRE review before execution.

## Outcome contract

### Non-goals

- Decomposing or redesigning `HomeStatsView` or `HomeLoadoutView`.
- Changing HomePage query/error ownership, loadout mutation semantics, backend metrics, APIs, generated types, query keys, rank tiers, companion definitions, effects, sprites, or CSS.
- Lazy-mounting Profile, adding new animation controls, changing copy, changing visuals, or broadening `HomeHubView` props for preview fixtures.
- Fixing the three pre-existing Admin Curriculum typography-policy violations.

### Risk if wrong

- Mutating search parameters incorrectly can lose preview or future campaign state or push history instead of replacing it.
- Conditional Profile mounting can reset Rank/spell selection and re-run queries.
- Duplicate loadout reads can obscure shop-catalog cache freshness.
- Moving refs across owners can shift projectile/ground effect anchors or break reduced-motion settlement.
- Unreviewed edits to shared sprite/effect/rank owners can turn a local refactor into a cross-product behavior change.

## Architecture map

### Files to create

- `frontend/src/features/home/components/home-hub/HomeProfileWorkspace.tsx`
- `frontend/src/features/home/components/home-hub/HomeProfilePanel.tsx`
- `frontend/src/features/home/components/home-hub/HomeCombatShowcase.tsx`
- `frontend/src/features/home/components/HomeHubView.test.tsx`
- `docs/goals/home-hub-profile-workspace-ownership/EVIDENCE.md`
- `docs/goals/home-hub-profile-workspace-ownership/evidence/home-profile-desktop.png`
- `docs/goals/home-hub-profile-workspace-ownership/evidence/home-profile-mobile.png`

### Files to modify

- `frontend/src/features/home/components/HomeHubView.tsx`
- `scripts/checks/check_architecture_boundaries.py` (additive; preserve every Slice 2/3 rule)
- `backend/common/tests/test_architecture_guard_algorithms.py` (additive; preserve every Slice 2/3 test)

### Files to avoid

- `frontend/src/features/home/pages/HomePage.tsx`
- `frontend/src/features/home/components/HomeStatsView.tsx`
- `frontend/src/features/home/components/HomeLoadoutView.tsx`
- `frontend/src/features/home/components/HomeRankBadge.tsx`
- `frontend/src/features/home/preview/`, `frontend/src/features/home/api/`, `frontend/src/features/home/types.ts`, and Home utilities
- `frontend/src/app/router.tsx`, `frontend/src/app/layouts/HomeLayout.tsx`, and shared navigation
- All Home CSS files
- Home/stats/skills/shop/player-loadout APIs and hooks, query keys, auth, generated contracts, rank, cosmetics, story-world, sprite, battle/effect, wallet, and Git-command truth owners
- All backend files and every completed Slice 1-3 artifact except the two additive architecture guard/test files

### Source of truth

| Concern | Authoritative owner preserved |
|---|---|
| Home metrics/mastery/streak | `backend/progress/services/metrics.py` -> existing Home summary contract |
| Stats headline/activity | Existing Stats summary service/API/types |
| Rank tiers/title/progress | `frontend/src/shared/progress/rank.ts` |
| Wallet balance | `useWalletSummary`, with current Stats fallback supplied through the four-prop Hub contract |
| Learned commands | `useLearnedSkills` and its existing skills API/query key |
| Equipped companion | `usePlayerLoadout` and the shared shop-catalog cache |
| Animation/effect behavior | Companion runtime, `SpriteAnimator`, animation timing, effect registry, and Git command family mapping |
| Home outer section | `tab` search parameter owned only by `HomeHubView` |

### Read path

```text
/home or /design-preview/home
  -> HomePage/preview supplies home + stats + playerName + gitcoins
  -> HomeHubView owns backdrop and outer query tab
     -> HomeStatsView (unchanged)
     -> HomeLoadoutView (unchanged)
     -> always-mounted HomeProfileWorkspace
        -> usePlayerLoadout + useLearnedSkills
        -> HomeProfilePanel
        -> HomeCombatShowcase
```

### Write path

- Outer Home tab: `HomeHubView -> setSearchParams(new URLSearchParams(current), { replace: true })`.
- Profile/Rank selection: local to `HomeProfilePanel`.
- Chosen spell, sprite animation, and effect timers: local to `HomeCombatShowcase`.
- Loadout server writes remain exclusively in unchanged `HomeLoadoutView`; Profile observes the same shop-catalog cache through the existing loadout hook.

### Contract boundary and component props

- `HomeHubView`: unchanged four props. Owns `HomeTab`, parsing/selecting it, backdrop style, tab markup, Overview/Loadout conditional composition, and an always-mounted Profile workspace with `hidden`.
- `HomeProfileWorkspace`: receives `home`, `stats`, `playerName`, `gitcoins`, and `hidden`; invokes both integration hooks exactly once; owns only the `.home-ref-grid` section and passes explicit values to its two children.
- `HomeProfilePanel`: receives `home`, `stats`, `playerName`, `gitcoins`, and `companionDef`; owns `profileView` and all Profile/Rank display derivation and markup. It receives no query, router, ref, timer, or effect object.
- `HomeCombatShowcase`: receives `companionDef`, `companionSlug`, `skills`, and `skillsLoading`; owns sprite conversion, refs, pixel-bound pedestal style, selected skill, Attack-to-Idle choreography, geometry, effect dispatch, and cleanup. It receives no query object and makes no HTTP call.

### Integration points

- React Router search params and history replacement.
- React Query hook results already shared with Loadout through `queryKeys.shopCatalog`.
- Existing Home/Stats value precedence and rank derivation.
- Sprite imperative ref and effect layer DOM geometry.
- Existing dev-only preview route and fixtures; browser-only network interception supplies deterministic learned-skill and active-companion responses without changing production props.

### Migration/cutover

The cutover is internal and atomic: callers continue importing the same named view. The Profile workspace remains present in the DOM under `hidden` for non-Profile tabs, preserving local state and query/cache behavior. The old embedded helpers/markup are deleted in the same change that introduces the focused owners. No barrel, alias, duplicate controller, or compatibility layer remains.

### Acceptance evidence gate

A player-facing verifier must observe real rendered Profile behavior—not only unit tests—on the dev-only route with deterministic same-origin API interception: correct Profile/rank and spellbook states, query-tab replacement/preservation, state retention across an outer-tab round trip, skill selection, visible Attack-to-Idle label transition/effect dispatch without console errors, keyboard order, and no horizontal overflow at 1440, 1280, and 390 widths. Desktop/mobile screenshots and exact request/geometry traces are retained.

## Baseline and preservation preflight

`PRE_SLICE_BASELINE.md` is authoritative for the pre-Slice-4 dirty worktree. Before the first runtime/test/checker edit:

1. Recompute every pre-existing dirty path hash/deletion state and abort on mismatch.
2. Recompute the full-file and pre-existing Git-diff hashes for the two shared architecture files.
3. Confirm the Home subtree is clean against `HEAD`, and confirm the planned files-to-avoid hashes.
4. Confirm the retained browser baseline artifacts exist outside the workspace with the documented sizes/hashes, and port 51058 plus the recorded browser/Vite processes are closed.

The same protected checks run at the terminal gate. Shared architecture files then use preservation of all recorded functions/tests plus focused Slice 4 additions because their hashes intentionally change.

## Task 1: Freeze the Home Hub contract with integration tests

**Files allowed:** Create `frontend/src/features/home/components/HomeHubView.test.tsx` only.
**Exact scope:** Use a memory router, real `HomeHubView`, fixture Home/Stats data, and controlled mocks only at the unchanged Stats/Loadout child-view boundaries and external hook/sprite/effect boundaries. Freeze default/invalid/Profile/Loadout tab selection; preservation of unrelated search params; `REPLACE` history action; exact four-prop display precedence; Profile hidden-not-unmounted behavior; Rank/Profile local-state retention; learned-skill loading/empty/rich states; active companion propagation; accessibility roles/names; and current attack selection/effect-family behavior. Tests for the intentional timer-cleanup correction may be added as initially failing assertions immediately before Task 2.
**Expected output:** A deterministic harness protects current behavior before markup moves.
**Verification:** `npm test -- src/features/home/components/HomeHubView.test.tsx src/features/home/utils/achievements.test.ts --reporter=dot`; scoped ESLint.
**Acceptance evidence:** Test names and assertions map explicitly to the contract above.
**Parallel:** No. These tests are the cutover harness.

## Task 2: Atomically extract the Profile workspace, presentation, and combat owners

**Files allowed:** Create `HomeProfileWorkspace.tsx`, `HomeProfilePanel.tsx`, and `HomeCombatShowcase.tsx`; modify `HomeHubView.tsx` and the integration test only.
**Exact scope:** In one atomic cutover, move `usePlayerLoadout` and `useLearnedSkills` into the workspace; move `profileView`, rank derivation, value fallbacks, and exact Profile/Rank markup into the Profile panel; and move companion conversion, pedestal pixel bounds, sprite/effect refs, selected skill, geometry, Git-command effect placement, stage/spellbook markup, and Attack-to-Idle behavior into the combat component. The workspace owns only the unchanged `.home-ref-grid` root plus the two existing integration-hook calls, stays mounted for every outer tab using `hidden`, immediately destructures hook results, and passes narrow data props to both children. It may not forward a hook/query/loadout object or a render prop back to Hub. Delete unreachable `ShowcaseMove` Run/Hurt/portrait metadata. Track both settle and delayed-effect timers; a newer attack cancels the prior settle and not-yet-fired effect timer, and unmount clears every outstanding timer so no effect or state update fires after teardown. Preserve the 120ms effect delay, `animationDuration(..., 1600)` fallback, placement rules, values, labels, loading skeleton, empty copy, and every existing class name/DOM order/copy/ARIA contract.
**Expected output:** Hub is the small outer composition owner; workspace is integration-and-grid only; Profile is presentation-only; combat is query-free and owns the complete local sprite/spellbook lifecycle. No intermediate or duplicate owner is left in the tree.
**Verification:** Focused tests and scoped ESLint after the atomic cutover. Fake timers and captured SpriteAnimator callbacks prove correct family/placement, latest-attack-only delayed effects, Attack-to-Idle settlement, and unmount cleanup.
**Acceptance evidence:** State retention under `hidden`, value/role assertions, and deterministic callback/timer/effect traces all pass against the final owners.
**Parallel:** No. The three new owners and Hub cut over together so there is never a query/render bridge or temporary duplicate path.

## Task 3: Harden the ownership boundary

**Files allowed:** Additive edits to `scripts/checks/check_architecture_boundaries.py` and `backend/common/tests/test_architecture_guard_algorithms.py` only.
**Exact scope:** Add canonical alias/relative/static/dynamic/require/template-aware rules for Hub/workspace/profile/combat roles. Enforce 140/100/190/240 line ceilings; required files; direction `Hub -> workspace -> children`; no child-to-Hub/page import; Hub displaced imports/markers/markup absent; exactly one workspace invocation; workspace owns `.home-ref-grid` and exactly one call to each integration hook. Workspace must remain integration-and-grid only: reject rank/RankBadge/GitCoin/profile-view markup, companion runtime, sprite/effect/command-family/geometry imports or markers, React local-state/ref/effect hooks, and timers. Profile and combat are React Query/API/router-free; Profile must remain timer/ref/sprite/effect/geometry-free; Combat must remain rank/profile/wallet and integration-query-hook-free and must be the only role allowed to contain `setTimeout`, `clearTimeout`, SpriteAnimator refs, effect placement/dispatch, and ground/anchor geometry. Reject production fixture seams, render props, and whole integration/query/loadout object forwarding. Add synthetic alias/relative/dynamic/require/template bypass cases for every role-specific boundary. Preserve all Slice 2/3 guard functions/tests unchanged in behavior and keep `main` invoking their checks.
**Expected output:** CI prevents the mixed owner or bypass imports from returning.
**Verification:** Synthetic positive rejection tests, actual-tree clean assertion, full architecture algorithm file, live checker.
**Acceptance evidence:** Exact violation trace for representative alias, relative, dynamic, require, template, oversized, reverse, displaced-marker, duplicate-hook, and production-fixture cases.
**Parallel:** No. Guard the final shape, not an intermediate one.

## Task 4: Capture target-perspective evidence and close the slice

**Files allowed:** Create `EVIDENCE.md` and the two final screenshots only. Runtime edits after browser evidence require a documented plan amendment and rerun of affected gates.
**Exact scope:** Run focused/full/static/architecture/quality/protected gates. Start Vite on a newly checked non-default `127.0.0.1` port with explicit `VITE_API_BASE_URL=/api`, the exact host/port bound with `--strictPort`, a recorded PID tree, and an isolated browser session. Before opening the preview, intercept exactly `http://127.0.0.1:<frontend-port>/api/skills/learned/` and `http://127.0.0.1:<frontend-port>/api/shop/catalog/` with deterministic contract-valid JSON; no wildcard may match any other URL. Assert each exact request occurs once on initial Profile load and no cross-origin API request occurs. On `/design-preview/home?tab=profile`, prove rich and empty Profile states, Profile/Rank switch, outer-tab URL replacement and unrelated-param preservation, retained Rank/skill state, skill attack/selection and Attack-to-Idle label, keyboard traversal, zero console/page errors, and overflow measurements. Capture 1440x900 desktop and 390x844 mobile screenshots; measure 1280 breakpoint behavior. Stop only recorded process/browser trees and delete only the verified temporary session child after final evidence is copied.
**Expected output:** Durable evidence demonstrates unchanged player behavior and cleaner ownership on the real rendered surface.
**Verification:** Commands below plus browser evidence trace.
**Acceptance evidence:** `EVIDENCE.md`, screenshots, hashes, request/interaction/geometry observations, and PRE/POST/correctness/maintainability/verifier verdicts.
**Parallel:** No. Evidence follows final integration.

## Verification commands and timeout policy

Run from the repository root unless a command changes directory explicitly:

```powershell
Set-Location frontend
npm test -- src/features/home/components/HomeHubView.test.tsx src/features/home/utils/achievements.test.ts --reporter=dot
npx eslint src/features/home/components/HomeHubView.tsx src/features/home/components/HomeHubView.test.tsx src/features/home/components/home-hub
npm run lint
npm run lint:dead
npm run build
npm test -- --reporter=dot
npm run ui:typography-check
Set-Location ..

python -m pytest backend/common/tests/test_architecture_guard_algorithms.py -q
python scripts/check_architecture_boundaries.py
python scripts/check_quality_gates.py
git diff --check
git diff --exit-code -- frontend/src/shared/api/generated
git diff --exit-code -- frontend/src/features/home/pages/HomePage.tsx frontend/src/features/home/components/HomeStatsView.tsx frontend/src/features/home/components/HomeLoadoutView.tsx frontend/src/features/home/components/HomeRankBadge.tsx frontend/src/features/home/preview frontend/src/features/home/api frontend/src/features/home/types.ts frontend/src/features/home/utils frontend/src/styles/features/home.css frontend/src/styles/features/home frontend/src/app/router.tsx frontend/src/app/layouts/HomeLayout.tsx frontend/src/shared
```

- Focused tests, architecture tests, lint, build, and browser acceptance are blockers on nonzero exit.
- The full Vitest run has a hard 300-second ceiling and must complete successfully; the current final tree baseline is 64 files/446 tests.
- The UI typography command is expected to report exactly the three byte-identical Admin Curriculum `text-[10px]` baseline violations and no Home violation. Any new/different violation is a blocker.
- Do not run destructive Git cleanup, reset, checkout, staging, commit, or broad formatting.

## Review gates

1. PRE plan reviewer: aligned before any runtime/test/checker edit.
2. POST plan reviewer: implementation/evidence remain aligned with this plan.
3. Correctness reviewer: URL/state, data precedence, cache freshness, effect placement/timers, and browser proof.
4. Maintainer: no duplicate owner, stale generic move path, boundary bypass, or unclear contract.
5. Verifier: independently inspect rendered screenshots/interaction evidence and rerun representative deterministic gates.

## Broader-goal continuation

This slice does not complete the broad codebase-modernization goal. After verification, separately map and PRE-review `HomeStatsView`, then `HomeLoadoutView` because it owns a real mutation workflow; later candidates include `ProblemsEditor.tsx` and large battle/runtime modules.
