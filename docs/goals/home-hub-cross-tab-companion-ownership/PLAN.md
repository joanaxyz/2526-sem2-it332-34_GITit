# Home Hub Cross-Tab Companion Ownership Corrective Plan

**Intent:** Reconcile the completed Home Hub ownership architecture with the
later no-companion UX, so one shared loadout read cleanly serves Overview and
Profile without a wide integration object crossing component boundaries.
**Current Behavior:** The rendered Home behavior and 17 focused tests are green,
but `HomeHubView` stores the complete `PlayerLoadout` hook result and forwards it
to `HomeProfileWorkspace`. The historical architecture guard still requires the
loadout hook inside that Profile-only workspace, rejects the newer declarative
Shop links in Profile/combat, and retains a pre-feature 240-line combat limit.
The live checker consequently reports six violations.
**Expected Outcome:** `HomeHubView` invokes and immediately destructures
`usePlayerLoadout` exactly once because companion presence affects both outer
Overview and persistent Profile composition. It passes only
`companionDef: CompanionDef | null` and `companionSlug: string | null` to
`HomeProfileWorkspace`; the workspace remains the sole learned-skills reader.
Profile and combat may render an exact declarative `Link`, but cannot own router
state or navigation hooks. The guard matches and enforces this current contract.
**Target-Perspective Output:** A new player still sees “Choose your first
companion” on Overview and both Profile empty states link to
`/shop?tab=companions&required=1`. A player with a companion retains the same
Profile/Rank/spell and attack behavior across outer-tab round trips. One catalog
read supplies both surfaces.
**Truth Owner:** `usePlayerLoadout` and `shopCatalogQueryOptions` remain the
authoritative equipped/absent-companion read. `hasCompanion`, not the fallback
Blue slug, determines absence. Within Home, `HomeHubView` owns the one cross-tab
loadout integration call; `HomeProfileWorkspace` owns the one learned-skills
call and persistent grid; existing Profile/combat owners retain local UI state.
**Contract Boundary:** Preserve the four public `HomeHubView` props, outer URL
tab behavior, always-mounted Profile workspace, HomeStats no-companion CTA,
empty Profile links, class/DOM behavior, and existing data/cache owners. Across
the Hub-to-workspace boundary only narrow companion values may pass.
**Cutover:** Characterize the current behavior, atomically replace the opaque
`playerLoadout` prop with narrow values, then replace only the stale Home Hub
guard assumptions and their synthetic tests. No compatibility prop or second
hook call remains.
**Displaced Path:** Remove `const playerLoadout = usePlayerLoadout()`, the
`playerLoadout={...}` JSX prop, `PlayerLoadout` from the workspace contract, and
the workspace’s type dependency on the hook module. Retire the guard rules that
assign cross-tab loadout state to the Profile-only workspace or reject exact
declarative `Link` imports.
**Value Density:** This clears all six live architecture failures, removes a
wide integration boundary, preserves the newer product behavior, and restores
the aggregate quality gate with five runtime/checker files plus focused tests.
**Acceptance Evidence:** Focused Home Hub/Overview behavior tests; exact Shop
href assertions; synthetic rejection of duplicate/non-destructured loadout
calls, raw loadout forwarding, workspace loadout reads, and router hooks; clean
live architecture and fast-quality gates; lint/build/full frontend results;
browser rich/empty Profile and Overview traces if the local preview is
available; protected-path audit; POST/correctness/maintainability verdicts.
**Evidence Lane:** Current dirty-tree baseline -> PRE review -> narrow runtime
cutover -> stale guard replacement -> focused/static/full gates -> browser proof
-> preservation audit -> independent reviews.
**Kill Criteria:** Exactly one `usePlayerLoadout` call in the Home Hub ownership
subtree, in `HomeHubView`, and exactly one `useLearnedSkills` call, in
`HomeProfileWorkspace`. No hook/query/`PlayerLoadout` object crosses a component
boundary. Hub remains at most 140 lines; workspace 100; Profile 190; combat 250.
Leaf views may import only the declarative `Link` surface from React Router and
must not own router/navigation hooks or `<Navigate>`. Combat remains the sole
sprite/effect/timer owner. The public Hub API and persistent `hidden` behavior
remain unchanged. The live architecture checker has zero violations.
**Architecture Slice:** `HomePage -> HomeHubView(loadout integration) ->
HomeStatsView + HomeLoadoutView + HomeProfileWorkspace(learned-skill
integration) -> HomeProfilePanel + HomeCombatShowcase`.
**Plan Review Gate:** Requires PRE review before runtime, test, or guard edits.

## Outcome contract

### Non-goals

- Redesigning Home UI, copy, styles, Profile/Rank, or combat choreography.
- Editing `HomeStatsView`, its model/dashboard/gallery, or `HomeLoadoutView`.
- Changing `usePlayerLoadout`, shop query/cache behavior, shared navigation,
  companion definitions, rank, sprites, effects, APIs, or generated contracts.
- Centralizing the companion-required Shop path across unrelated features.
- Rewriting the completed August goal packages or their historical evidence.
- Resolving unrelated dirty-worktree changes.

### Risk if wrong

- Using the fallback companion slug instead of `hasCompanion` can let an
  unequipped player bypass the required-companion UX.
- A second loadout hook obscures cache ownership and can produce inconsistent
  loading/error behavior across tabs.
- Passing a query/loadout object recreates a wide boundary and couples the
  workspace to hook implementation details.
- Broadly allowing router ownership in leaf views can reintroduce query-state
  mutation below the Hub.

## Architecture map

### Files to create

- `docs/goals/home-hub-cross-tab-companion-ownership/PRE_SLICE_BASELINE.json`
- `docs/goals/home-hub-cross-tab-companion-ownership/EVIDENCE.md`

### Files to modify

- `frontend/src/features/home/components/HomeHubView.tsx`
- `frontend/src/features/home/components/HomeHubView.test.tsx`
- `frontend/src/features/home/components/home-hub/HomeProfileWorkspace.tsx`
- `scripts/checks/check_architecture_boundaries.py`
- `backend/common/tests/test_architecture_guard_algorithms.py`

### Files to avoid

- `frontend/src/features/home/components/HomeStatsView.tsx`
- `frontend/src/features/home/components/HomeLoadoutView.tsx`
- `frontend/src/features/home/components/home-hub/HomeProfilePanel.tsx`
- `frontend/src/features/home/components/home-hub/HomeCombatShowcase.tsx`
- `frontend/src/features/home/components/home-stats/**`
- `frontend/src/features/home/pages/**`, `preview/**`, `api/**`, and Home styles
- `frontend/src/shared/**`, backend/API/generated files, and historical goal
  packages

### Source of truth and paths

| Concern | Read owner | Consumer path | Write path |
|---|---|---|---|
| Companion presence/definition | `usePlayerLoadout` | Hub -> Overview/Profile | none |
| Learned commands | `useLearnedSkills` | workspace -> combat | none |
| Outer tab | `HomeHubView` | search params -> composition | Hub replace-navigation |
| Profile/Rank state | `HomeProfilePanel` | local render | panel buttons |
| Combat state/effects | `HomeCombatShowcase` | skill -> sprite/effect | local timers/callbacks |

### Contract boundary

- Hub immediately destructures `companion`, `companionSlug`, `hasCompanion`,
  `isLoading`, and `isError` from one `usePlayerLoadout()` call.
- `companionRequired` is true only after a successful non-loading read with no
  equipped companion.
- Hub passes the workspace exactly its existing four display values, `hidden`,
  and nullable `companionDef`/`companionSlug`; no raw loadout object.
- Workspace invokes/destructures `useLearnedSkills()` once and passes narrow
  values to the two existing children.
- Profile/combat may use exact static `{ Link }` imports from
  `react-router-dom`; dynamic/require imports, `<Navigate>`, and router hooks are
  rejected.

## Task board

### Task 1 — Freeze and review the corrective contract

**Files allowed:** This goal package only.
**Output:** A JSON baseline records status, hashes, and line counts for every
planned/protected file plus current architecture/focused-test results.
**Verification:** Replay the baseline before runtime edits; PRE reviewer returns
aligned with no blocker.
**Parallel:** No.

### Task 2 — Narrow the cross-tab loadout boundary

**Files allowed:** `HomeHubView.tsx`, `HomeProfileWorkspace.tsx`, and
`HomeHubView.test.tsx` only.
**Output:** Hub immediately destructures the sole loadout read, derives nullable
companion values with `hasCompanion`, and passes no integration object. Tests
prove one call, absent/rich behavior, exact Shop links, persistent Profile state,
and unchanged attack/timer behavior.
**Verification:**
`npm --prefix frontend test -- src/features/home/components/HomeHubView.test.tsx src/features/home/components/HomeStatsView.test.tsx --reporter=dot`
and scoped ESLint.
**Parallel:** No.

### Task 3 — Replace stale architecture enforcement

**Files allowed:** `scripts/checks/check_architecture_boundaries.py` and
`backend/common/tests/test_architecture_guard_algorithms.py` only.
**Output:** The guard enforces sole Hub loadout ownership, immediate
destructuring, narrow workspace props, sole workspace learned-skill ownership,
exact declarative Link allowance, routing-hook rejection, and the 250-line combat
ceiling while preserving every unrelated rule.
**Verification:**
`python -m pytest backend/common/tests/test_architecture_guard_algorithms.py -q`
and `python scripts/checks/check_architecture_boundaries.py`.
**Parallel:** No.

### Task 4 — Verify and review

**Files allowed:** Create `EVIDENCE.md`; no runtime edits after evidence without
rerunning affected gates.
**Output:** Focused/full/static/quality results, protected hash replay, and, when
available, browser traces for equipped and empty companion states. Independent
POST, correctness, and maintainability reviews assess the settled tree.
**Verification:** Focused commands above, full frontend tests, lint, dead-code,
build, fast quality gates, `git diff --check`, and browser acceptance.
**Parallel:** Read-only static gates may run concurrently after implementation.
