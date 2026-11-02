# Home Hub Cross-Tab Companion Ownership Evidence

Captured on 2026-08-25 for the corrective Home Hub ownership slice.

## Outcome

The later no-companion feature is preserved, but its cross-tab loadout data no
longer crosses into the Profile workspace as a complete `PlayerLoadout` object.

- `HomeHubView` is the sole Home production owner of `usePlayerLoadout`. It
  immediately destructures the companion-presence contract and uses
  `hasCompanion`—not the fallback Blue slug—to derive both the Overview CTA and
  nullable Profile values.
- `HomeProfileWorkspace` receives only `companionDef` and `companionSlug`, owns
  the one `useLearnedSkills` call, and remains mounted under `hidden`.
- `HomeProfilePanel` and `HomeCombatShowcase` retain their existing local state,
  rendering, and declarative Shop links. They own no router state or navigation
  hooks.

| Owner | Responsibility | Lines | Limit |
|---|---|---:|---:|
| `HomeHubView` | URL composition and cross-tab loadout integration | 117 | 140 |
| `HomeProfileWorkspace` | learned-skill integration and persistent grid | 47 | 100 |
| `HomeProfilePanel` | Profile/Rank presentation | 160 | 190 |
| `HomeCombatShowcase` | sprite/effect/timer/spell behavior | 244 | 250 |

The displaced `playerLoadout={playerLoadout}` prop, `PlayerLoadout` workspace
type, and workspace dependency on the hook module are absent.

## Architecture enforcement

The Home guard now reflects the current cross-tab contract instead of the
historical Profile-only data flow. It enforces:

- a production-wide Home subtree census with exactly one `usePlayerLoadout`
  call in `HomeHubView` and exactly one `useLearnedSkills` call in
  `HomeProfileWorkspace`;
- immediate destructuring of the full companion-presence contract;
- the unchanged four-prop public Hub signature;
- the exact seven narrow props passed to the persistent Profile workspace;
- rejection of a raw loadout/query/integration object boundary;
- static `{ Link }` as the only React Router surface allowed in Profile/combat,
  while dynamic/require router imports, `<Navigate>`, and router hooks remain
  forbidden;
- the revised 250-line combat ceiling, with a controlled 251-line rejection.

The architecture algorithm lane passed 14/14 tests and the live checker printed
`Architecture boundaries look clean.` The aggregate fast-quality suite also
passed every repository gate.

## Behavior evidence

The focused Home Hub/Overview lane passed 17/17 tests. It proves one loadout
hook call, empty/equipped behavior, exact companion Shop hrefs, URL replacement
and unrelated-query preservation, persistent hidden Profile state, Rank/spell
state retention, companion refresh, rich/empty learned skills, attack placement,
latest-only effects, and timer cleanup.

Full frontend verification:

| Gate | Result |
|---|---|
| Focused Home Hub/Overview | PASS — 2 files / 17 tests |
| Full frontend suite | PASS — 76 files / 499 tests |
| Full ESLint | PASS |
| Production TypeScript/Vite build | PASS — 2,659 modules |
| Architecture algorithm tests | PASS — 14 tests |
| Live architecture checker | PASS |
| Aggregate fast-quality gates | PASS |
| `git diff --check` | PASS; three unrelated CRLF warnings only |
| Dead-code scan | External failure: unused exported `ChallengeRunStepResponse` in `features/challenges/types.ts` |

## Browser evidence

An isolated Vite preview ran on strict `127.0.0.1:51067` with
`VITE_API_BASE_URL=/api` and exact same-origin fixtures for only
`/api/shop/catalog/` and `/api/skills/learned/`.

Both the empty and equipped sessions made exactly one request to each endpoint.
The empty Profile showed no fallback Blue sprite and rendered two exact
`/shop?tab=companions&required=1` links. Switching to Overview produced:

```text
heading: Choose your first companion
href: /shop?tab=companions&required=1
Profile mounted: yes
Profile hidden: yes
horizontal overflow: 0
```

The equipped Profile rendered the Blue idle animation and two learned skills.
After selecting Rank Ladder and `git log`, an Overview/Profile round trip
retained both selections and returned to Blue idle. Equipped Overview produced
`Continue your Git journey` with `/stories/arcane-spire`. The browser console
contained zero warnings or errors, and both states had zero horizontal overflow.

The controlled browser tab and verified Vite process tree were closed, port
51067 was confirmed free, and the temporary Vite config was deleted. The host
policy rejected deletion of the external temporary log directory
`%TEMP%\git-it-home-cross-tab-proof-20260825`; it contains logs only and no
workspace or product artifact depends on it.

## Preservation

All six protected baseline files are byte-identical: Home Overview, Loadout,
Profile, combat, the shared loadout hook, and shared navigation were not edited.
No Home CSS, backend/API/generated file, or historical goal package was changed
by this corrective slice. This slice's files remain unstaged; unrelated staged
work already present in the shared worktree was left untouched.

## Review state

The PRE reviewer returned `aligned` with no blocker, major, or minor finding.
POST, correctness, and maintainability reviews are pending against this settled
implementation and evidence.
