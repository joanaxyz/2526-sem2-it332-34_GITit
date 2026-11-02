# Truthful Home Companion Status and Alias-Safe Hook Ownership Plan

**Intent:** Close the two correctness and maintainability gaps found after the
Home Hub ownership cutover: unresolved loadout reads must not masquerade as a
confirmed empty loadout, and aliased hook imports must not bypass the production
owner census.
**Current Behavior:** `HomeHubView` correctly suppresses the Overview companion
CTA while the loadout is loading or errored, but it passes only nullable
companion values to the persistent Profile workspace. Profile therefore renders
the confirmed-empty copy and Shop links during loading and indefinitely after a
failed catalog read. Separately, the Home hook census counts literal hook call
names, so `usePlayerLoadout as useLoadout` in a non-owner is invisible.
**Expected Outcome:** The Hub derives one presentation-only discriminated union
with `loading`, `error`, `empty`, and `ready` states. Only `empty` renders the
companion Shop CTA; `loading` and `error` render truthful non-action states;
`ready` carries the companion definition and slug. The Hub maps only `empty` to
the existing Overview `companionRequired` boolean, while the full state drives
both persistent Profile panels. The architecture census resolves canonical
hook-module imports, named aliases, and namespace calls and rejects every direct
non-owner import.
**Target-Perspective Output:** On a direct Profile visit, a player sees
"Loading companion" while catalog truth is unresolved, "Companion unavailable"
after a failed catalog read, "No companion selected" plus exact Shop links only
after a successful empty read, and the equipped companion after a successful
ready read. Loading/error states never show `Choose companion` or fallback Blue
art.
**Truth Owner:** `usePlayerLoadout` remains the catalog/loadout truth owner.
`HomeHubView` remains the only Home loadout reader and owns conversion from query
facts into the presentation union. `companionPresentation.ts` owns only the
type-level boundary; it contains no derivation or runtime truth. `HomeProfileWorkspace`
remains the only learned-skills reader. TypeScript import-analysis helpers remain
the canonical way architecture checks resolve alias and relative module references.
**Contract Boundary:** Across the Hub-to-workspace boundary, pass one small
`CompanionPresentation` union rather than React Query flags, nullable parallel
values, or a raw loadout object. The `ready` variant alone contains
`definition` and `slug`; all other variants contain no companion payload.
**Cutover:** Atomically replace the parallel `companionDef`/`companionSlug`
boundary with the discriminated presentation union, extract non-ready Profile
presentation from the combat owner, then replace literal-name census logic with
canonical import/binding analysis. No compatibility props or duplicate status
derivations remain.
**Displaced Path:** Remove `companionDef` and `companionSlug` from the workspace
boundary, leaf null-as-empty inference, the inline combat empty-state branch,
and literal-only hook ownership counting.
**Value Density:** One coherent status contract fixes a visible false claim,
eliminates impossible prop combinations, keeps combat below its line ceiling,
and makes the existing architecture invariant enforceable against ordinary
TypeScript aliasing.
**Acceptance Evidence:** Focused tests cover loading, error, empty, cached-ready,
and ready behavior; synthetic guard fixtures reject named aliases, namespace
imports, re-exports, require/dynamic imports, and duplicate owners; the live
checker and quality gates pass; browser traces prove loading/error/empty/ready
Profile output with no false CTA or fallback art; protected hashes replay;
POST, correctness, and maintainability reviewers accept the settled slice.
**Evidence Lane:** Dirty-tree baseline -> PRE review -> presentation-contract
cutover -> guard hardening -> focused/static/full gates -> browser proof ->
protected-path replay -> independent reviews.
**Kill Criteria:** Exactly one direct import and one invocation of
`usePlayerLoadout`, in `HomeHubView`; exactly one direct import and invocation of
`useLearnedSkills`, in `HomeProfileWorkspace`; no direct re-export, dynamic
import, require, named alias, or namespace use of those modules elsewhere under
production Home. Only confirmed `empty` may display companion Shop CTAs. No raw
loadout/query object or parallel nullable companion pair crosses the workspace
boundary. Hub stays at most 140 lines, workspace 100, Profile 190, combat 250,
and the extracted status renderer 120. The live architecture checker has zero
violations.
**Architecture Slice:** `usePlayerLoadout -> HomeHubView ->
CompanionPresentation -> HomeProfileWorkspace -> HomeProfilePanel +
HomeCombatShowcase`, with `HomeCompanionStatus` owning Profile/combat non-ready
rendering. Overview keeps its existing boolean API and renders its existing
content for loading/error.
**Plan Review Gate:** Requires PRE review before runtime, style, test, or guard
edits.

## Outcome contract

### Non-goals

- Changing the shop query, retry/cache policy, shared loadout hook, APIs, or
  generated contracts.
- Adding a retry button or new navigation behavior.
- Redesigning Profile, Rank, combat choreography, learned skills, or Overview;
  Overview keeps its existing content during loading/error and receives
  `companionRequired=true` only for confirmed empty.
- Changing the public four-prop `HomeHubView` contract or persistent hidden-tab
  behavior.
- Generalizing the TypeScript analyzer into a full compiler or tracing facades
  outside the production Home subtree.
- Resolving unrelated staged/unstaged work or the external dead-code warning.

### Risk if wrong

- Treating loading/error as empty sends players to Shop based on unknown truth.
- Giving error precedence over cached equipped data hides usable stale data.
- Passing independent status/data props permits impossible combinations.
- Counting only call spellings makes architecture evidence stronger than its
  enforcement.

## Architecture map

### Files to create

- `frontend/src/features/home/components/home-hub/companionPresentation.ts`
- `frontend/src/features/home/components/home-hub/HomeCompanionStatus.tsx`
- `docs/goals/home-companion-status-and-hook-ownership-hardening/PRE_SLICE_BASELINE.json`
- `docs/goals/home-companion-status-and-hook-ownership-hardening/EVIDENCE.md`

### Files to modify

- `frontend/src/features/home/components/HomeHubView.tsx`
- `frontend/src/features/home/components/HomeHubView.test.tsx`
- `frontend/src/features/home/components/home-hub/HomeProfileWorkspace.tsx`
- `frontend/src/features/home/components/home-hub/HomeProfilePanel.tsx`
- `frontend/src/features/home/components/home-hub/HomeCombatShowcase.tsx`
- `frontend/src/styles/features/home/hub-empty-states.css`
- `scripts/checks/check_architecture_boundaries.py`
- `backend/common/tests/test_architecture_guard_algorithms.py`

### Files to avoid

- `frontend/src/shared/player-loadout/usePlayerLoadout.ts`
- `frontend/src/features/home/components/HomeStatsView.tsx`
- `frontend/src/features/home/components/HomeLoadoutView.tsx`
- `frontend/src/shared/navigation/routes.ts`
- Home pages/preview/API, backend product code, generated files, and historical
  goal packages

### Source of truth and paths

| Concern | Read owner | Boundary | Consumer |
|---|---|---|---|
| Catalog/loadout facts | `usePlayerLoadout` | destructured hook result | Hub only |
| Companion presentation state | `HomeHubView` | type-only `CompanionPresentation` | persistent Profile workspace |
| Learned commands | `useLearnedSkills` | narrow skills/loading values | combat |
| Non-ready copy/actions | `HomeCompanionStatus` | status variant | Profile/combat |
| Hook ownership policy | architecture checker | canonical module/import bindings | CI/live checker |

### Read and write paths

- Read: catalog query -> `usePlayerLoadout` -> one Hub call -> presentation
  union -> workspace -> leaf renderers.
- Write: none for loadout status; only existing declarative empty-state Shop
  links and existing local Profile/combat interactions remain.
- Guard: production Home source census -> canonical module resolution -> named
  and namespace binding calls -> exact expected owner comparison.

## Task board

### Task 1 - Freeze and PRE-review the contract

**Files allowed:** This goal package only.
**Output:** Baseline hashes/statuses and green current focused/guard results;
PRE reviewer confirms outcome, owner, union boundary, cutover, and evidence.
**Verification:** Replay hashes and review verdict.
**Parallel:** No.

### Task 2 - Make unresolved loadout states truthful

**Files allowed:** The seven Home runtime/test/style paths named above plus the
two new Home Hub files.
**Output:** Hub derives a presentation union with ready data precedence, then
loading, error, and empty; the type-only contract module performs no derivation.
Hub maps only empty to Overview's existing `companionRequired` boolean.
Profile/combat use one extracted non-ready renderer. Only empty has Shop links;
existing ready, Rank, learned-skill, animation, and timer behavior remains.
**Verification:** Focused Home tests and scoped ESLint.
**Parallel:** No.

### Task 3 - Make hook ownership alias-safe

**Files allowed:** `check_architecture_boundaries.py` and
`test_architecture_guard_algorithms.py` only.
**Output:** The census checks canonical direct module ownership and imported
named/namespace call bindings, while retaining literal-call detection for
unbound rogue calls. Controlled fixtures prove alias/re-export/dynamic/require
bypasses fail and the live tree passes.
**Verification:** Architecture algorithm pytest, Ruff, Python compilation, and
live checker.
**Parallel:** No.

### Task 4 - Verify from the target perspective and review

**Files allowed:** Create `EVIDENCE.md`; any implementation correction requires
rerunning affected gates.
**Output:** Focused/full frontend, lint/build/dead-code, architecture/quality,
diff, protected-hash, and browser evidence for all four states. Independent
POST, correctness, and maintainability verdicts are recorded.
**Verification:** Commands and observed target output captured in evidence.
**Parallel:** Read-only gates may run concurrently after implementation.
