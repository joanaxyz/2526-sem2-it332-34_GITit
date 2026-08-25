# Truthful Home Companion Status and Alias-Safe Hook Ownership Evidence

Captured on 2026-08-25 against the settled corrective slice.

## Outcome

Home no longer treats an unresolved catalog read as a confirmed absence.
`HomeHubView` remains the sole loadout reader and converts its destructured facts
into a presentation-only discriminated union:

| State | Precedence and payload | Profile output | Shop CTA |
|---|---|---|---|
| `ready` | equipped data wins, including cached data during refresh failure | companion art and combat | none |
| `loading` | no equipped data and initial read pending | `Loading companion` | none |
| `error` | no equipped data and read failed | `Companion unavailable` | none |
| `empty` | successful read with no equipped companion | `No companion selected` | exact required-companion links |

`companionPresentation.ts` is type-only; Hub owns all runtime derivation. The
workspace receives one impossible-state-resistant view model rather than a raw
query/loadout object or parallel nullable props. `HomeCompanionStatus` owns the
Profile/combat non-ready presentation. It uses a skeleton rather than a spinner,
has a reduced-motion fallback, distinguishes error with icon and text, and emits
only one live-region announcement even though both panels show the state.

Overview keeps its existing boolean API: only confirmed `empty` maps to
`companionRequired=true`; loading/error preserve the existing Overview content.

## Ownership and code shape

| Owner | Responsibility | Lines | Limit |
|---|---|---:|---:|
| `HomeHubView` | URL composition, sole loadout read, status derivation | 122 | 140 |
| `HomeProfileWorkspace` | sole learned-skills read, persistent composition, live announcement | 48 | 100 |
| `HomeProfilePanel` | Profile/Rank presentation and local tab state | 157 | 190 |
| `HomeCombatShowcase` | ready-state sprite/effect/timer/spell behavior | 222 | 250 |
| `HomeCompanionStatus` | loading/error/empty Profile and combat output | 96 | 120 |
| `companionPresentation` | type-only discriminated boundary | 10 | 30 |

The guard now checks both direct module ownership and imported-call ownership.
It canonicalizes alias/relative paths, resolves named import aliases and
namespace bindings, retains detection for unbound literal rogue calls, and
rejects direct non-owner re-exports, dynamic imports, and `require` references.
Controlled fixtures reject:

- named and relative named aliases;
- namespace imports/calls;
- re-exports;
- dynamic imports and `require`;
- learned-skills named aliases;
- runtime declarations/value imports, anonymous default exports, and top-level
  executable expressions in the exact type-only presentation contract;
- declarative router links in Profile/combat after CTA ownership moved to the
  status renderer;
- a 121-line status component and 251-line combat component.

Comment-only import examples are ignored, and namespace calls are deduplicated
in diagnostics. The presentation contract is a required guarded target and
cannot acquire a runtime derivation helper without failing CI.

The live production Home census finds one direct import/call of
`usePlayerLoadout` in `HomeHubView` and one direct import/call of
`useLearnedSkills` in `HomeProfileWorkspace`.

## Verification

| Gate | Result |
|---|---|
| Focused Home Hub/Overview | PASS - 2 files / 21 tests |
| Full frontend suite | PASS - 76 files / 503 tests |
| Full ESLint | PASS |
| Dead-code scan | PASS |
| Production TypeScript/Vite build | PASS - 2,660 modules |
| Architecture algorithm tests | PASS - 15 tests |
| Ruff and Python compilation | PASS |
| Live architecture checker | PASS |
| Aggregate fast-quality gates | PASS |
| UI typography audit | External failure - three existing `text-[10px]` usages in Admin Curriculum files |
| `git diff --check` | PASS; three unrelated CRLF warnings only |

## Browser evidence

An isolated same-origin Vite proof ran on strict `127.0.0.1:51068` with exact
fixtures for `/api/shop/catalog/` and `/api/skills/learned/`.

- Loading: two visible `Loading companion` labels, one `role=status`, zero
  companion Shop links, no fallback Blue art, and zero horizontal overflow.
- Error: two visible `Companion unavailable` labels, one `role=alert`, zero
  companion Shop links, no fallback Blue art, and zero horizontal overflow.
- Confirmed empty: two `No companion selected` labels and exactly two links,
  both `/shop?tab=companions&required=1`; no fallback Blue art, no live-region
  noise, and zero horizontal overflow.
- Ready: Blue idle animation plus two learned skills, no non-ready copy, no
  companion Shop link, and zero horizontal overflow.

The visible four-state browser proof preceded the final relocation of the sole
live announcement from the Profile-only branch to the persistent workspace; no
visible markup, CTA, art, or layout output changed. The settled focused DOM
evidence keeps Rank Ladder selected while loading becomes error and proves that
the workspace still exposes exactly one `role=alert` with no Shop CTA.

The browser tab was finalized, the verified Vite process was stopped, port
51068 is free, and the temporary Vite config is absent. Host policy rejected
deleting `%TEMP%\git-it-home-companion-status-proof-20260825`; it contains only
proof-server logs and no workspace or product artifact depends on it.

## Preservation

All four protected baseline paths are byte-identical: the shared loadout hook,
Home Overview, Home Loadout, and shared routes. No API, generated contract,
backend product code, preview fixture, or historical goal package was edited by
this slice. No slice-owned path is staged; unrelated existing staged/unstaged
work was left untouched.

## Review state

The repeated PRE review returned `aligned` with no remaining finding after the
plan explicitly scoped the shared status renderer to Profile/combat and kept
runtime derivation in Hub. The first POST review returned `aligned`. Correctness
then found that the live region disappeared on Rank Ladder; maintainability
found stale Profile/combat Link allowances, an unguarded type-only contract, and
comment/namespace diagnostic weaknesses. All findings were corrected and every
affected gate was replayed. The correctness re-review is clean. A subsequent
maintainability re-review found anonymous default/top-level execution could
still enter the contract; exact canonical-shape enforcement and regressions now
close that escape hatch.

Final verdicts:

- POST: `aligned`, with no blocker, major, or minor finding.
- Correctness: no remaining issue. Residual risk is that the final live-region
  relocation is proven by DOM-role regression rather than an assistive-technology
  browser session.
- Maintainability: `MAINTAINABLE`, with no remaining finding. Residual risk is
  the intentionally lexical/exact contract guard, which requires coordinated
  checker/fixture updates for a legitimate future union change; facades outside
  the Home subtree remain an explicit non-goal.
