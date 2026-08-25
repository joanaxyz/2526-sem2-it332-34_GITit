# Codebase Maintainability Modernization - Slice 1 Evidence

## Outcome

Reusable advanced curriculum mechanics now have explicit owners below authored
ledgers:

- cross-mode repository fixtures live at the shared curriculum source root;
- Adventure form-drill mechanics live in Adventure support;
- advanced Challenge construction lives in Challenge support.

No authored `v3_*` ledger imports a private implementation from another ledger.
Only explicit public content edges (`LEVELS`, `INCIDENTS`, `V3_CHALLENGES`, and
`V3_FORM_CHALLENGES`) remain. All six affected authored catalogs and the
generated-target artifact are identical to `HEAD`.

## Maintainer ownership map

| Change a maintainer needs to make | Truth owner after cutover | Inspection result |
| --- | --- | --- |
| Shared advanced repository fixture, end-state requirement, or command placeholder rendering | `backend/curriculum/seed_data/source/advanced_story_support.py` | Public API is `build_advanced_story_state`, `build_advanced_story_requirements`, and `render_advanced_story_command`. The module imports `spec_helpers` directly and loads no Adventure package or `v3_*` ledger. |
| Shared form-drill constants, clean/broken fixtures, variants, or evaluation builders | `backend/curriculum/seed_data/source/adventure_level_specs/form_drill_support.py` | The planned ten public symbols are in `__all__`; the module owns no authored catalog. |
| Shared advanced Challenge difficulty, narrative, or strategy variant construction | `backend/curriculum/seed_data/source/challenge_specs/advanced_challenge_support.py` | Public API is `ADVANCED_CHALLENGE_DIFFICULTY`, `advanced_challenge_scenario_copy`, and `build_advanced_challenge_variant`; both authored Challenge ledgers are sibling consumers. |
| Frost authored waves or Frost-only fixtures | `backend/curriculum/seed_data/source/adventure_level_specs/v3_frost_form_drills.py` | Frost calls public support names directly and exposes none of its ten displaced bindings. |
| Skyline authored waves | `backend/curriculum/seed_data/source/adventure_level_specs/v3_skyline_form_drills.py` | Skyline imports Adventure form support directly and has no Frost import. |
| Cross-story authored adventure incidents | `backend/curriculum/seed_data/source/adventure_level_specs/v3_advanced_workflows.py` | The ledger retains `ChapterIncident`, incident/level assembly, `INCIDENTS`, and `LEVELS`; all five moved fixture bindings are absent. |
| Primary advanced challenge content | `backend/curriculum/seed_data/source/challenge_specs/v3_story_challenges.py` | The ledger retains challenge assembly and authored catalogs; all five shared-construction bindings are absent. |
| Additional form/mastery challenge content | `backend/curriculum/seed_data/source/challenge_specs/v3_chapter_form_challenges.py` | The ledger imports public Challenge support and public Adventure content catalogs only. |

## Dependency cutover

| Before | After |
| --- | --- |
| Frost -> `v3_advanced_workflows._state` | Frost -> source-root `advanced_story_support.build_advanced_story_state` |
| Skyline -> nine private Frost constants/helpers | Skyline -> public `form_drill_support` contract |
| Challenge story specs -> `v3_advanced_workflows._state/_render/_requirements` | Challenge support -> public source-root advanced-story contract |
| Form/mastery challenge ledger -> five private `v3_story_challenges` bindings | Both Challenge ledgers -> public `advanced_challenge_support` contract |
| Challenge/composer -> public authored catalogs | Preserved intentionally as explicit content edges |

The AST guard scans every Python file below
`backend/curriculum/seed_data/source/`. It rejects private cross-ledger imports,
normal module imports, package-relative module imports, and wildcard imports of
`v3_*` ledgers. It permits only the four public content exports, rejects authored
ledger imports/catalog bindings in support modules, proves all twenty displaced
former-owner bindings remain absent, and rejects restoration of the temporary
Adventure-owned advanced-support path.

## Before/after module metrics

| Module | Before | After | Delta |
| --- | ---: | ---: | ---: |
| `v3_advanced_workflows.py` | 431 | 316 | -115 |
| `v3_frost_form_drills.py` | 3,017 | 2,948 | -69 |
| `v3_skyline_form_drills.py` | 902 | 902 | 0 |
| `v3_story_challenges.py` | 427 | 240 | -187 |
| `v3_chapter_form_challenges.py` | 188 | 192 | +4 |
| source-root `advanced_story_support.py` | - | 172 | +172 neutral owner |
| `form_drill_support.py` | - | 119 | +119 Adventure owner |
| `advanced_challenge_support.py` | - | 253 | +253 Challenge owner |

The additional form-challenge lines are only explicit public imports/call names;
authored scenario data did not move or change.

## Canonical catalog equality against isolated HEAD

The baseline was extracted with `git archive HEAD backend/curriculum` into a
validated temporary directory. Baseline and working tree were imported under
separate `PYTHONPATH` values. Values were serialized with sorted compact JSON,
dataclasses converted with `dataclasses.asdict`, sets sorted, and then SHA-256
hashed.

| Catalog | Count | HEAD and worktree SHA-256 |
| --- | ---: | --- |
| `v3_advanced_workflows.INCIDENTS` | 21 | `2f5b8034e12af9d1d09b8a9b762ddddb4c1de8a8fa76b5db856aa5df823b2b29` |
| `v3_advanced_workflows.LEVELS` | 63 | `0fa3136ff5837de6a7d037e445f1ecef79620aebf4c765d651e341dbae6bed7d` |
| `v3_frost_form_drills.LEVELS` | 112 | `9088754962466a989181ba17685c462f834335cf3d3820f3b4e24a138093fbd2` |
| `v3_skyline_form_drills.LEVELS` | 43 | `f650ef420da9a960a3eb1f8d7b3042725c0301d81813360b05f3847bbf8ca4a4` |
| `v3_story_challenges.V3_CHALLENGES` | 22 | `74c761d02391082a574a8c32e789b1f0b3061c5bf24af3403aa49e6e505dd307` |
| `v3_chapter_form_challenges.V3_FORM_CHALLENGES` | 26 | `defb819d154466460d9d651f8122417eab6c6efd051f995ae309fe3c4c9e4e97` |

Result: the complete six-name/count/hash maps matched exactly. Temporary archive,
extraction, and helper artifacts were removed after comparison.

## Verification evidence

- Initial and amended PRE reviews: `aligned`; no remaining blocker or major.
- Reviewer-driven ownership corrections: source-root cross-mode support,
  Challenge support, generic AST import enforcement, and former-owner binding
  removal are implemented.
- Focused curriculum suite:
  `python -m pytest curriculum/tests/test_seed_data_source_layout.py curriculum/tests/test_three_story_curriculum.py curriculum/tests/test_level_brief_required_details.py curriculum/tests/test_challenge_form_coverage.py -q`
  -> `19 passed in 85.82s`.
- Focused Ruff lint lane over three support modules, five authored callers, and
  the ownership test -> `All checks passed!`.
- Scoped Ruff format lane over the three maintained support modules and ownership
  test -> all four files formatted.
- Isolated support import -> the source-root advanced support loaded zero `v3_*`
  modules.
- Former-owner smoke -> all twenty displaced bindings absent.
- `python manage.py generate_targets --check` -> collected `2056` variant
  solutions; generated targets are current.
- `python scripts/check_quality_gates.py` -> every fast repository guard passed,
  including architecture, API contract, API usage/type adoption, seed targets,
  documentation, CI manifest, and artifact checks.
- `git diff --check` -> clean.
- Generated target diff -> unchanged.
- Generated target SHA-256 before and after:
  `6EE61275D1571FABD983C5602FA2D323A5DAF4B6F637FA71D3B617B0F916DF54`.

## Scope confirmation

No generated target, migration, API contract, frontend file, asset, database, or
unrelated tracked file was edited. This evidence completes only the approved
curriculum ownership slice; the broader maintainability goal remains active for
separately mapped and PRE-reviewed follow-up slices.
