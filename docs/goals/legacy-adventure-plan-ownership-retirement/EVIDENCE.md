# Slice 17 Evidence: Legacy Adventure Plan Ownership Retirement

## Target-person result

A curriculum author now has one visible ownership path for each kind of adventure
grouping:

- foundational level/wave values are authored only in the existing blueprint
  ledgers under `backend/curriculum/seed_data/source/blueprint/`;
- `_FOUNDATIONAL_ADVENTURE_ORDER` owns only the stable published sequence of
  those 16 blueprint keys;
- `_ADVANCED_DRILL_WAVE_PLANS` owns exactly the 19 Frost/Skyline drill
  groupings;
- `ADVENTURE_WAVE_PLANS` is composed once through a validated projection and a
  guard-before-merge helper that cannot silently replace a key.

The authoring guide names those owners and explicitly describes the public map
as composition output rather than a second authoring surface. The obsolete
`ADVENTURE_LEVEL_PLAN` definition, imports, exports, seed-writer loop, and
Chapter 1 migration package are absent.

## Cutover proof

The immutable pre-cutover manifest and settled verifier replay the complete
public boundary:

- 35 adventure plan keys in the exact original insertion order;
- the exact 16-key foundational order, including `seal-the-snapshot` before
  `untrack-and-undo-edits`;
- 95 plan levels and 437 waves;
- all 16 foundational values retain object identity with
  `BLUEPRINT_ADVENTURE_LEVELS`;
- all 19 advanced literal values retain their exact normalized AST and source
  segment fingerprints;
- 663 `ADVENTURE_LEVELS` entries and 663 `SPEC_BY_SLUG` entries;
- 29 adventure sources;
- the exact 159-form supported command set both before and after removing the
  redundant legacy reuse loop;
- byte-identical generated targets covering 2,056 variants.

The AST census scans executable Python under `backend/` and `scripts/`, excluding
only the self-referential checker and focused policy test. It finds no live
import, export, binding, name access, or attribute access for
`ADVENTURE_LEVEL_PLAN`. All three retained wrapper/package surfaces omit that
symbol while retaining `ADVENTURE_LEVELS`, `SPEC_BY_SLUG`, and
`adventure_levels_for`.

The displaced `backend/curriculum/seed_data/source/ch1` path is absent on disk;
a fresh `importlib.util.find_spec("curriculum.seed_data.source.ch1")` returns
`None`.

## Durable ownership policy

`scripts/checks/check_curriculum_source_layout.py` keeps the existing Repository
Foundations topology policy and composes the path-injectable adventure ownership
checks from `scripts/checks/adventure_plan_ownership.py`. Generic Python lexical,
namespace, provenance, and mutator analysis is isolated in
`scripts/checks/mutable_owner_analysis.py`; the curriculum policy depends on that
analyzer in one direction through a narrow public API. An invocation-local
`MutableOwnerAnalyzer` reuses each syntax tree's node sequence, lexical map,
access counts, definition counts, immutable lookups, and safe-container results
across parameter checks. The policy freezes the exact foundational order,
advanced key set, composition AST, validated projection AST, guard-before-merge
AST, owner-module topology, and literal advanced-plan schema. It rejects:

- missing, extra, duplicate, or reordered foundational keys;
- missing, extra, or foundational keys in the advanced owner;
- public subscript assignment, augmented assignment, deletion, and mutating
  methods including `update`, `setdefault`, `pop`, `popitem`, and `clear`;
- a silenced/reordered collision guard, union-based helper, or nondeterministic
  duplicate ordering;
- any second owner-module reference or rebinding of the public plan, merge
  helper, order owner, advanced owner, or blueprint input;
- nested-list mutation, alias mutation, unbound dict mutators, destructuring,
  loop rebinding, helper rebinding, or drift in the sole canonical reader;
- mutation or rebinding inside the canonical reader's normalization helpers;
- chained assignments, named-expression aliases, mutable order aliases,
  duplicate blueprint imports, and Unicode NFKC-equivalent identifiers;
- rogue consumers of the private advanced owner, the blueprint composite, or
  any mutable blueprint leaf/subleaf implementation module;
- drift in the complete 27-module blueprint owner graph or in any approved
  blueprint consumer's normalized module AST;
- restored legacy bindings, imports, attribute accesses, wrapper exports,
  authoring guidance, or the `source/ch1` path.

The combined CLI preserves its exact success contract:

```text
Curriculum source layout is consistent.
```

## Immutable evidence bindings

| Artifact | SHA-256 |
|---|---|
| `PRE_SLICE_BASELINE.json` | `1F3FB3EAF5E61B2F4F244830148DD8288E30CDC528CF4BD1CF35D7605CFB7FA9` |
| `PRE_CUTOVER_PLAN_MANIFEST.json` | `A73888EADE78980DFAA6E51AA3B366C1799A163691ADB1C961BADA7A2AF3C71C` |
| `FINAL_COMMAND_RESULTS.json` | Pending: not captured while preservation and aggregate gates are red on unrelated worktree drift |
| `verify_evidence.py` | `2FEEBDC0627EB66DFF4059F00403B204B7A9B259FEB46948002F69151E622BA2` |

When the unrelated worktree is reconciled, `FINAL_COMMAND_RESULTS.json` will
retain every command, argv, cwd, accepted exit, stdout/stderr bytes and digests,
both manifest fingerprints, zero-staging state, and settled implementation
fingerprints. Canonical replay strictly decodes both base64 streams, recomputes
both digests, checks cwd/argv/exits, rejects unexpected stderr except preserved
`git diff --check` warnings, and requires the expected result/count tokens.

## Command evidence

| Gate | Result |
|---|---|
| Canonical verifier | Exit 1: implementation/runtime checks pass; preservation drift and missing final-results artifact remain |
| Focused ownership/topology | 230 passed in 250.96s |
| Focused seed/data flow | 19 passed in 213.80s |
| Complete curriculum regression | 1,745 passed in 550.80s |
| Dedicated layout CLI | Exit 0 with exact success stdout |
| Seed target structure | 2,056 cases consistent |
| Generated-target currency | 2,056 variants; generated file current |
| Fast aggregate | Exit 1 only on six unrelated Home Hub architecture-boundary violations; every other aggregate check passed |
| Semantic legacy census | Exit 0 |
| Supporting text census | Previously verified accepted exit 1 with empty stdout/stderr; pending final recapture |
| Ruff on every planned Python path | Exit 0 |
| `git diff --check` | Exit 0 with three unrelated CRLF normalization warnings |

The canonical verifier currently reports exactly two final-phase problems:
an immutable visible repository path changed after baseline capture, and
`FINAL_COMMAND_RESULTS.json` is absent. The preservation delta contains 82
out-of-slice paths (39 changed and 43 added), predominantly frontend assets and
Home/Story Map work plus two asset-processing script files. The Git index remains
empty; no file was staged, committed, discarded, or normalized by this slice.

## Review findings and corrections

The mandatory PRE review was aligned after it required an explicit 16-key public
order owner, semantic consumer census, exact Task 3 mutation scope, and exact
collision messages.

Iterative correctness and maintainability review challenged every mutable
identity path: public/nested aliases, helper rebinding, canonical-reader helper
mutation, NFKC-normalized identifiers, approved-consumer callee shadowing, and
imports of composite, leaf, and Repository Foundations subleaf owners. Each
reproduction became a controlled policy test. The settled policy freezes the
owner/reader helper contracts, approved consumer modules, and the complete
blueprint owner graph, while resolving relative imports before applying the
owner-private boundary. Further correctness review expanded conservative
coverage for async calls, statement bindings, comprehensions, dynamic module
namespaces, destructuring, partial callables, fresh sinks, and nested escapes.
The focused ownership corpus now contains 217 cases, plus 13 Repository
Foundations topology cases in the combined gate.

The verifier was hardened in parallel to validate strict base64 payloads,
recomputed stream hashes, cwd, argv, exits, stderr policy, required proof
tokens, implementation bindings, and zero-staging state. Every pre-fix command
record was discarded. A maintainability reviewer required and then accepted the
generic analyzer extraction, returning `MAINTAINABLE`. The latest correctness
review found no implementation defect; it identified only this evidence record's
stale completion claims, which this revision removes.

The settled reviewers returned `STATIC_ALIGNED`, `MAINTAINABLE`, and
`POST_ALIGNED`. Final command capture remains pending until the unrelated
preservation and Home Hub architecture state is reconciled.

## Deviations and residual risk

There was no runtime or public-data deviation from the approved plan. Execution
refinements strengthened the planned guard from pattern checks to exact helper
AST contracts after independent review demonstrated bypasses, and extracted the
reusable AST/dataflow subsystem after maintainability review found that the
single policy module had grown beyond one responsibility.

Residual implementation risk is limited to out-of-repository consumers importing
the retired internal symbol and runtime-only dynamic reflection/monkeypatching
that static AST policy cannot observe. Closure risk is external to this slice:
the baseline preservation snapshot remains red on those 82 unrelated paths, and
the fast aggregate remains red on six Home Hub architecture violations, so final
evidence must not be captured yet.
