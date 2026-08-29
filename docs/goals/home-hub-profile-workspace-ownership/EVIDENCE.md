# Home Hub Profile Workspace Ownership — Evidence

Captured on 2026-08-09 for Slice 4 of the codebase maintainability goal.

## Outcome

The Profile surface was cut over atomically from the 397-line `HomeHubView` to
three explicit owners without changing the page's public four-prop contract,
Home CSS, backend/API contracts, or shared rank/cosmetic/sprite/effect truth
owners.

| Owner | Responsibility | Lines | Limit |
|---|---|---:|---:|
| `HomeHubView` | URL tab state, backdrop, outer tab composition | 99 | 140 |
| `HomeProfileWorkspace` | learned-skill/loadout integration and persistent grid | 44 | 100 |
| `HomeProfilePanel` | Profile/Rank state, derivation, and markup | 148 | 190 |
| `HomeCombatShowcase` | sprite runtime, attack/effect geometry, timers, spellbook | 210 | 240 |

`HomeProfileWorkspace` is always mounted and uses `hidden` outside the Profile
tab. It calls and immediately destructures `useLearnedSkills` and
`usePlayerLoadout` once each, then passes narrow data props. A companion change
remounts only the combat owner, so its timers are cancelled while Profile/Rank
state remains owned by the stable panel.

## Behavior evidence

The focused Home Hub lane passed 12/12 tests across two files. It covers:

- default, invalid, Profile, and Loadout URL selection;
- unrelated-query preservation and `REPLACE` navigation;
- hidden-not-unmounted Profile behavior and Rank/spell state retention;
- exact display-data precedence;
- learned-skill loading, empty, and rich states;
- attack selection/effect dispatch;
- latest-only delayed effects and stale-settle cancellation;
- unmount cleanup and companion-change cleanup without resetting Rank state.

The intentional timer correction is now explicit: starting an attack clears the
prior settle/effect timers and invalidates its completion token; unmount clears
all scheduled work. The browser trace observed `Blue attack animation` with one
effect node, followed by `Blue idle animation` with zero effect nodes.

## Exact same-origin browser proof

A disposable Vite middleware fixture served only these exact paths on strict
`127.0.0.1:51061` with `VITE_API_BASE_URL=/api`:

- `/api/skills/learned/`
- `/api/shop/catalog/`

The fixture was installed before the target page opened. On both the rich and
empty Profile loads, browser resource timing recorded skills `1`, shop `1`, and
cross-origin API requests `0`. No wildcard intercepted any other URL. The
temporary Vite config was deleted, its identity-checked process was stopped, and
port 51061 was verified free.

The rich-state interaction trace proved:

- `?tab=profile&proof=1` -> Overview `?proof=1` -> Profile
  `?proof=1&tab=profile`;
- Rank Ladder and the selected `git log` spell survived the outer-tab round trip;
- keyboard order from the outer Profile button was inner Profile, Rank Ladder,
  `git add`, then `git log`;
- the empty fixture rendered `newcomer`, `Novice`, and currency values `0`/`0`;
- page-error collection was empty; console output contained only normal Vite and
  React DevTools development notices.

| Viewport | Document/client width | Profile grid | Result |
|---|---:|---:|---|
| 1440x900 | 1430 / 1430 | 1393 | no horizontal overflow |
| 1280x800 | 1270 / 1270 | 1237 | no horizontal overflow |
| 390x844 | 380 / 380 | 356 | no horizontal overflow |

Final screenshots were visually compared with the retained pre-slice captures;
layout and responsive behavior match, with the expected deterministic rich
spellbook replacing the baseline empty response.

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| `evidence/home-profile-desktop.png` | 640,423 | `AF83AD144CE9F8BB13843C2C42DAC17F495AB94E6D82AA9747E596588615B717` |
| `evidence/home-profile-mobile.png` | 254,082 | `166B59B24F900DBD082D54BF24D1061BD28FA1CD127CABA28337F6948783FFC9` |

## Verification gates

- Full frontend suite: 65 files, 455 tests passed.
- Focused Home lane: 2 files, 12 tests passed.
- Full ESLint: passed.
- Knip/dead-code gate: passed.
- Production TypeScript/Vite build: passed; application entry
  `261.11 kB` (`44.19 kB` gzip).
- Architecture guard unit lane: 9 tests passed.
- Live architecture checker: clean.
- Fast quality bundle: all repository gates passed.
- `git diff --check`: passed.
- UI typography comparator reported exactly the three planned, byte-identical
  Admin Curriculum `text-[10px]` baseline violations and no Home violation.

## Preservation audit

- All 56 pre-Slice-4 dirty-worktree manifest entries remain byte-identical or
  deleted as recorded.
- All 22 protected Home files retain their exact line counts and SHA-256 hashes.
- The 14 grouped files-to-avoid paths have empty Git diffs, including Home
  Stats/Loadout, CSS, router/layout, shared owners, and generated API contracts.
- All earlier Admin Console and Content Editor checker behavior remains covered;
  the Home ownership guard and its synthetic bypass cases are additive.

The two retained pre/final temporary evidence directories remain outside both
workspace roots. Their exact contents were validated before deletion was
attempted, but the host command policy rejected filesystem deletion; no product
or workspace artifact depends on them.

## Review gates

The pre-implementation plan review returned `ALIGNED` after the atomic cutover,
exact same-origin request, and role-specific guard requirements were made
explicit.

The requested independent post-plan, correctness, and maintainability reviewers
could not run because their shared agent quota was exhausted until 2026-08-13.
No independent verdict is claimed. A local fallback audit found no blocking or
advisory finding: the implementation matches the plan, tests exercise the
timer/state contracts, ownership direction is one-way, and all static,
behavioral, visual, and preservation gates above are green.
