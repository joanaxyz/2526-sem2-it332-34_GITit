# Frost Form Ledger Chapter Ownership Evidence

## Outcome

The 2,948-line `v3_frost_form_drills.py` authored ledger is absent. Its unchanged public import now resolves to a same-stem package with an export-only initializer, a private ordered catalog, one Frost-only fixture owner, and nine chapter owners. The two existing consumers were not edited.

The target-perspective command is:

```text
python docs/goals/frost-form-ledger-chapter-ownership/verify_evidence.py
Frost form ledger evidence verified.
```

That deterministic verifier proves content identity, topology, protected-file identity, all non-slice dirty-path identity, and absence of staged slice files. Supporting tests and gates are recorded below.

## Maintainer ownership map

| A maintainer wants to change | Canonical owner | Final lines |
| --- | --- | ---: |
| Public Frost `LEVELS` import surface | `v3_frost_form_drills/__init__.py` | 7 |
| Final chapter/list order | `v3_frost_form_drills/_catalog.py` | 43 |
| Frost-only repository state fixtures | `v3_frost_form_drills/_fixtures.py` | 132 |
| Chapter 1: Temper the Commit | `v3_frost_form_drills/temper_the_commit.py` | 608 |
| Chapter 2: Choose the Integration | `v3_frost_form_drills/choose_the_integration.py` | 217 |
| Chapter 3: Survive the Conflict | `v3_frost_form_drills/survive_the_conflict.py` | 394 |
| Chapter 4: Move the Patch | `v3_frost_form_drills/move_the_patch.py` | 404 |
| Chapter 5: Reforge the Branch | `v3_frost_form_drills/reforge_the_branch.py` | 201 |
| Chapter 6: Govern the Remote | `v3_frost_form_drills/govern_the_remote.py` | 547 |
| Chapter 7: Deliver the Release | `v3_frost_form_drills/deliver_the_release.py` | 289 |
| Chapter 8: Hunt the Regression | `v3_frost_form_drills/hunt_the_regression.py` | 136 |
| Chapter 9: Publish the Core | `v3_frost_form_drills/publish_the_core.py` | 87 |
| Cross-story form mechanics | existing `adventure_level_specs/form_drill_support.py` | protected/unchanged |
| Cross-mode advanced repository fixtures | existing `source/advanced_story_support.py` | protected/unchanged |

The largest Frost owner is now 608 lines instead of 2,948. The package has 3,065 total lines because each owner has an explicit docstring/import boundary; the improvement is single-responsibility ownership and bounded review scope, not line-count compression.

## Cutover and displaced-path proof

- `backend/curriculum/seed_data/source/adventure_level_specs/v3_frost_form_drills.py`: absent.
- `backend/curriculum/seed_data/source/adventure_level_specs/v3_frost_form_drills/`: exact twelve-file manifest across all regular files except runtime `__pycache__` contents.
- Public contract remains `curriculum.seed_data.source.adventure_level_specs.v3_frost_form_drills.LEVELS`.
- Existing callers `adventure_level_specs/__init__.py` and `challenge_specs/v3_chapter_form_challenges.py` match their frozen status/existence/size/SHA-256 tuples.
- `__init__.py` exports only `LEVELS`; `_catalog.py` alone defines the ordered aggregate.
- Each leaf defines `DRILLS` and `WORKFLOWS`; only Survive additionally owns `_conflict_read` and `NO_MARKERS`.
- `_fixtures.py` owns the exact fifteen approved Frost-only helper functions.
- The integrated checker rejects restored monoliths, Python or non-Python manifest drift, every cap class, initializer/catalog ownership drift, reordered composition, inline catalog content, duplicate declarations, unexpected top-level execution/destructuring, unexpected/duplicate helpers, wildcard or sibling imports, external deep/non-public imports anywhere under repository `backend` or `scripts`, and displaced support aliases. Its external scan prunes virtualenv/cache/temp/vendor directories and byte-prefilters for the Frost module token before AST parsing.

## Source-list identity

All before/after canonical fingerprints are equal. Serialization is UTF-8 `json.dumps(..., sort_keys=True, separators=(",", ":"))`, with dataclasses converted to dictionaries and sets sorted.

| Source list | Items | SHA-256 before and after |
| --- | ---: | --- |
| Choose drills | 4 | `F11E2D87618E020427D45EFDC56F98F05B01525631FC5E9E84F03E3090548453` |
| Choose workflows | 4 | `ED514C5D0E4AA8576FEFFE28656FAB721DE2B1D8071CB8BCEB590EFA62FA2AD1` |
| Deliver drills | 6 | `CFE720EC6986CA2DF2D780A96F2072BDBE9A2A6687EDD8E81D42451AE548BC83` |
| Deliver workflows | 6 | `6BBAD96C1268C24F753D3B8CE96141D330BAF8E0CC13BCDCD9069E7D5CE43E3F` |
| Govern drills | 8 | `732A00D29FDC4F1A286C1BB064FC02AC7E6F9567A9ACE5476155E602AEEE2B89` |
| Govern workflows | 12 | `825523F7795E9DB570AFE48465FD10914202D27194B7E6AB28AE02E3AA0609EC` |
| Hunt drills | 2 | `3309F9C532BB6BFEB174DDCBC82DA32A590253480132E008BAE955AC71D5B8AF` |
| Hunt workflows | 4 | `06B6E4C8D66A2415D80599AE4359F2D479103E17E5DE49EFE54276DE5F6F2832` |
| Move drills | 7 | `45B89DD97F9CF0A83C0CD4E41A8D3A1DBC5CCD47D90ABE6170C55AA94347C6D4` |
| Move workflows | 8 | `5715AE6739189A90A3089FA4D020A268A9A94799D74F1E78D242785B7140BD48` |
| Publish drills | 2 | `DBB978C2645C8DF8BEE7332C8DDE3BBB5D06D28E27DFDDC77675525C1C2C45DF` |
| Publish workflows | 2 | `FB0ED8F266750E71C9A7C723B9326513DAA5194CA274097FD3BD1AAE47D2805B` |
| Reforge drills | 2 | `113C2C30A629350417F2E61CCD147752E7B5FB97DC9A45A6B99636EAB7B0338B` |
| Reforge workflows | 4 | `734178C40C782C499BA01175AF8CFAE62F97E53722656791ED7FE1CF9E07510C` |
| Survive drills | 9 | `BF94B84FEFFEA8150F0A264464AA3CC971C4C0919129FD297313ABA97E65C637` |
| Survive workflows | 8 | `CAC256D767A1A1C536C203C4D64C5BD3A587FE3DBAD45700A2242BDAB41373AD` |
| Temper drills | 11 | `84BA9A3AA269FD9E8ECA1ACA69F3736503FEF88BF01A4D79395D7364694E3508` |
| Temper workflows | 13 | `6DEF1F45CC877F0CB4367C01608F95555674E555C4F653F274E8125263672554` |

## Composed-content identity

| Catalog/artifact | Items | Canonical bytes | SHA-256 before and after |
| --- | ---: | ---: | --- |
| Frost `LEVELS` | 112 | 1,578,356 | `9088754962466A989181BA17685C462F834335CF3D3820F3B4E24A138093FBD2` |
| Aggregate `ADVENTURE_LEVELS` | 663 | 7,676,379 | `5C4F2AE3E4894D280BF4849385D3E173773B7B4C4F0984D0692576ACB4C7FFCB` |
| Derived `V3_FORM_CHALLENGES` | 26 | 3,383,597 | `DEFB819D154466460D9D651F8122417EAB6C6EFD051F995AE309FE3C4C9E4E97` |
| Raw `generated_targets.py` | — | 11,008,324 | `6EE61275D1571FABD983C5602FA2D323A5DAF4B6F637FA71D3B617B0F916DF54` |

`generate_targets --check` independently collected and replayed all 2,056 variant solutions and reported the generated artifact current.

## Dirty-worktree preservation

`PROTECTED_BASELINE.json` records:

- four pre-existing planned-path states;
- seven explicit caller/support/generated states;
- a compressed canonical manifest of all 381 dirty paths outside this slice's file/prefix allowlist;
- manifest byte count `54,816` and SHA-256 `FECC80E737C8116A093D3EF0A3530DA5CEA7344891628ECDA69BDAEEF794440A`.

The terminal verifier decompresses and compares every path's Git status, existence, byte count, and SHA-256. It also rejects staged slice paths. Final result: exact match; no slice path staged.

The verifier also pins the two frozen inputs by raw file hash: `PRE_SLICE_BASELINE.json` is `C5A070DB75CB9E23A980DC898AD83328AFC5CF33C5716A5C2779C3FB0F9C60D2`; `PROTECTED_BASELINE.json` is `361DED99A124ED426E06C1D228929870797D9478DCFDE6F44A652E4295730997`. Baseline edits therefore fail before any evidence comparison runs.

## Verification record

| Gate | Result |
| --- | --- |
| Synthetic Frost topology mutation corpus | 22 passed, 1 live test initially deselected before cutover |
| Final Frost topology tests | 33 passed in 6.14s |
| Final Frost topology + reusable-owner tests | 36 passed in 2.39s (warm run) |
| Focused layout/story/brief/pedagogy/challenge/content suites | 63 passed in 158.73s |
| Ruff over package, checker, tests, verifier | passed |
| Integrated curriculum source layout command | `Curriculum source layout is consistent.` |
| Persistent evidence verifier | `Frost form ledger evidence verified.` |
| `generate_targets --check` | 2,056 solutions; current |
| Fast repository quality gates | all passed |
| Django application check | no issues (0 silenced) |
| Frontend production build | passed; 2,660 modules transformed |
| Generated target working-tree diff | empty |
| `git diff --check` | exit 0; unrelated pre-existing CRLF warnings only |
| Staged slice paths | none |

The first focused pytest attempt was invoked from `backend` and could not resolve the repository-level `scripts` package. No test ran in that attempt. The plan command was corrected to the repository root, matching the existing checker-test convention; the authoritative runs above then passed.

## Review gates

- Explorer: selected this as the highest-value bounded remaining slice and recommended the same-stem package boundary.
- Initial PRE: partially aligned; requested protected dirty-work evidence, an executable verifier, and exact helper ownership.
- Final PRE: aligned after all three corrections; two wording minors were also applied and both baselines frozen.
- Initial POST plan review: aligned with no findings; a final re-review followed the guard hardening.
- Correctness/trust and target-perspective verifier review: `VERIFIED`; independently reconstructed chapter composition and confirmed all hashes, protected paths, generated targets, and staged-path absence. Its stale-count documentation finding is corrected above.
- Maintainability review: initial guard-bypass findings for duplicate/side-effect ownership, narrow external scanning, wildcard imports, non-Python manifest drift, and duplicated policy were corrected with mutations. Its follow-up traversal/performance finding was also corrected. Final verdict: `MAINTAINABLE`, with no actionable code finding.
- Final POST plan re-review: `aligned` with no findings after the stale verification counts were corrected; no blocker, undeclared file, or scope deviation remains.

## Blockers and residual risk

Blockers: none.

The remaining intended coordination cost is that adding a Frost chapter or legitimate shared fixture requires updating the exact topology manifest, cap table, mutation tests, and evidence mapping in the same change. That is deliberate: it makes ownership changes explicit rather than allowing a second quiet path.
