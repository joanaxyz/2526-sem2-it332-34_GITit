# Repository Foundations Ledger Decomposition — Slice 16 Evidence

## Outcome

The 2,887-line authored Repository Foundations ledger is now a 21-line stable composer over seven concept-owned leaf ledgers. Every leaf is below the approved 700-line ceiling. The stable import and public export remain unchanged, while the former inline 17-level literal has been removed completely from the composer.

The dedicated `scripts/checks/check_curriculum_source_layout.py` command owns topology enforcement and is registered once in the fast quality-gate aggregate. The generated-target checker remains unchanged and continues to own authored/generated target consistency only.

## Baseline and Cutover Evidence

- Original composer: 140,426 bytes; SHA-256 `4D6458472D6C6FE2405589DD82CFDD73B22D5D1DFFAD5779F01654B554391CD3`.
- Captured authored data: 17 levels, 76 waves; ordered level and per-level wave slugs recorded in `PRE_CUTOVER_CONTENT_MANIFEST.json`.
- Captured canonical sorted JSON: 77,768 bytes; SHA-256 `B6627CDD4E69826B1E0907DBDAB70807332DBD879997BBF8F0D9D3C844F4036B`.
- Every level dictionary's normalized AST and exact parsed source segment replay after the move.
- Stable raw export, `BLUEPRINT_ADVENTURE_LEVELS["repository-foundations"]`, `ADVENTURE_WAVE_PLANS["repository-foundations"]`, generated blueprint specs, and public adventure-level specs replay the same canonical fingerprints.
- Generated targets remain 11,008,324 bytes with SHA-256 `6EE61275D1571FABD983C5602FA2D323A5DAF4B6F637FA71D3B617B0F916DF54`.
- Pre-cutover relevant regression baseline: 1,465 passed in 171.01s; seed-target structure and generated-target currency commands exited 0.

Final authored module sizes:

| Owner | Lines |
|---|---:|
| Stable composer | 21 |
| `fresh_starts.py` | 675 |
| `history_and_status.py` | 556 |
| `cloning.py` | 452 |
| `configuration.py` | 350 |
| `founding_workflows.py` | 364 |
| `fresh_start_drills.py` | 267 |
| `inspection_drills.py` | 271 |
| Package initializer | 1 |

## Topology Mutation Evidence

The focused test file contains 13 tests. Its live case accepts the settled tree, and isolated temporary copies prove the checker rejects:

- a missing or unexpected leaf module;
- a nested alternate Python owner;
- inline level dictionaries or `_wave` calls in the composer;
- reordered composition;
- wrong or duplicate slug ownership;
- leaf-to-leaf and leaf-to-composer dependencies;
- composer or leaf size regression;
- package re-exports; and
- fallback top-level leaf ownership.

The checker also statically requires the canonical seven imports and starred-list order, one public `ADVENTURE_LEVELS` list, one literal `LEVELS` list per leaf, the exact slug allocation, docstring-only package initialization, and only `..helpers._wave` as a leaf dependency.

## Command Evidence

All commands ran from `C:\Users\Joana\Documents\GIT-IT`.

| Command | Result |
|---|---|
| `python docs/goals/repository-foundations-ledger-decomposition/verify_evidence.py --phase baseline` | Exit 0; `Slice 16 baseline evidence replay passed.` |
| `python docs/goals/repository-foundations-ledger-decomposition/verify_evidence.py --phase content` | Exit 0; exact AST/source/runtime/public/generated replay passed. |
| `python docs/goals/repository-foundations-ledger-decomposition/verify_evidence.py --phase topology` | Exit 0; live topology replay passed. |
| `python docs/goals/repository-foundations-ledger-decomposition/verify_evidence.py` | Exit 0; full evidence and preservation replay passed. |
| `python -m pytest -q backend/curriculum/tests/test_repository_foundations_source_layout.py` | Exit 0; 13 passed in 4.00s. |
| Relevant seven-file curriculum command from `PLAN.md` | Exit 0; 1,465 passed in 205.99s. |
| `python -m pytest -q backend/curriculum/tests` | Exit 0; 1,528 passed in 530.96s. |
| `python scripts/checks/check_curriculum_source_layout.py` | Exit 0; exact stdout `Curriculum source layout is consistent.` and empty stderr. |
| `python scripts/checks/check_seed_targets.py` | Exit 0; unchanged exact stdout `Generated curriculum targets are consistent (2056 cases).` and empty stderr. |
| `python scripts/checks/check_generated_targets_current.py` | Exit 0; collected 2,056 variants and reported generated targets up to date. |
| `python scripts/checks/check_quality_gates.py` | Exit 0; every existing fast gate plus the dedicated layout gate passed. |
| `python -m ruff check ...` on all Slice 16 Python paths | Exit 0; all checks passed. |
| `git diff --check` | Exit 0; no whitespace errors. Git emitted two line-ending warnings for preserved pre-existing paths, documented below. |

The first fast-aggregate attempt exposed an integration error in the new registry entry: it resolved the canonical checker as `scripts/check_curriculum_source_layout.py` instead of `scripts/checks/check_curriculum_source_layout.py`. The only fix changed that registry entry and the verifier's corresponding normalization. The canonical verifier, direct checker, 13 mutation tests, and complete fast aggregate all passed after the fix.

## Preservation Evidence

- `PRE_SLICE_BASELINE.json` protects 1,824 repository-visible paths outside the approved allowlist, recording existence, byte count, and SHA-256.
- Full replay passes after implementation; no unapproved repository-visible path appeared or disappeared.
- Zero paths were staged before capture and zero are staged after implementation.
- `GOAL.md` and `PLAN.md` replay their immutable baseline hashes.
- The quality-gate file normalizes byte-for-byte to its preimage after removing the one approved registry entry.
- The generated target and every generated/public/product/dirty path outside the allowlist remain byte-identical.
- `git diff --check` emitted line-ending warnings for two unrelated pre-existing dirty paths. Both remain exact against baseline:
  - `backend/curriculum/seed_data/source/challenge_specs/v3_story_challenges.py`: 9,842 bytes; SHA-256 `077FEBC5852BFBA6B42AFEBA7DA72F187C0642625EAED03F53EA6E224D8785A2`.
  - `frontend/src/shared/api/generated/apiTypes.ts`: 45,418 bytes; SHA-256 `67B87CAA9B83AD9E69F25142D4DE9524FBA2D4096F93C8A3665AAC696E7E5FC5`.

Finalized evidence-artifact fingerprints before independent review:

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| `GOAL.md` | 516 | `8A6C6BE8F8A66E6C94001A52EEA6D15DE35DD4F546CFFA5A684423DF08D92C31` |
| `PLAN.md` | 24,915 | `1532F5D39B8CC3AF0D220C29AE7EB15ADD10A259D430C36D28436A1030AAE792` |
| `PRE_SLICE_BASELINE.json` | 564,288 | `9AAA2418D8770F669E957F8968CF0FC691C7AD96AD185ADC5C454783B718C4F6` |
| `PRE_CUTOVER_CONTENT_MANIFEST.json` | 198,744 | `10EB6FE810A6BD236E508BB0E375C8C7A2FF49D6EB49CBDEC49317A9B09A4E43` |

## Structured Final Command Evidence

The lossless JSON block below is generated by `verify_evidence.py --capture-final-commands`. It records exact commands, working directory, exit code, byte counts, SHA-256 digests, and base64 stdout/stderr, bound to the settled implementation and both immutable manifests. The normal verifier authenticates and validates every row.

<!-- SLICE16_FINAL_COMMAND_RESULTS_START
{
  "cwd": "C:\\Users\\Joana\\Documents\\GIT-IT",
  "implementation_fingerprints": {
    "backend/curriculum/seed_data/source/README.md": {
      "bytes": 670,
      "exists": true,
      "sha256": "0E03B9ABA6C57D2DB84BEC08F2B4B08AE332CAB6CBD673D766207F2972DC82A2"
    },
    "backend/curriculum/seed_data/source/blueprint/adventure_repository_foundations.py": {
      "bytes": 932,
      "exists": true,
      "sha256": "2D1F93016671A16CF623600624FF333F0A1A864495BF03D46AF63B4151732E88"
    },
    "backend/curriculum/seed_data/source/blueprint/repository_foundations/__init__.py": {
      "bytes": 63,
      "exists": true,
      "sha256": "6C598A1C9DD01DC6BA70F1941EC14A445A613C497F1C0233E5D05C2239A0F1A6"
    },
    "backend/curriculum/seed_data/source/blueprint/repository_foundations/cloning.py": {
      "bytes": 21509,
      "exists": true,
      "sha256": "14BD83041F2067C4DCC14979DEE19674D525E8FA1CAF4087B3EC2762CBF02C56"
    },
    "backend/curriculum/seed_data/source/blueprint/repository_foundations/configuration.py": {
      "bytes": 17116,
      "exists": true,
      "sha256": "1534E797465251EA4DB1F6AB16551CDCE89FA242ACA0A78C33821889215FC895"
    },
    "backend/curriculum/seed_data/source/blueprint/repository_foundations/founding_workflows.py": {
      "bytes": 17919,
      "exists": true,
      "sha256": "5F6314DEEEF150BD4B5A09A0076A681FDA88767F8503D16D7D55750A05CC3176"
    },
    "backend/curriculum/seed_data/source/blueprint/repository_foundations/fresh_start_drills.py": {
      "bytes": 12820,
      "exists": true,
      "sha256": "04C37A1BEE050799F9DA5BC265CF5A06204C83144AF0E2FC2D812D0730248025"
    },
    "backend/curriculum/seed_data/source/blueprint/repository_foundations/fresh_starts.py": {
      "bytes": 32223,
      "exists": true,
      "sha256": "1595EFA3B86547FF52E7762AA24BA91F5A7758AA3A73640E7AF99462061CC772"
    },
    "backend/curriculum/seed_data/source/blueprint/repository_foundations/history_and_status.py": {
      "bytes": 26541,
      "exists": true,
      "sha256": "DEB6FFC4C3399B445A4A6686F5D53A62F36D52A413AA234583EAC2FF67005564"
    },
    "backend/curriculum/seed_data/source/blueprint/repository_foundations/inspection_drills.py": {
      "bytes": 13123,
      "exists": true,
      "sha256": "2DC72CE25EAFEF319702192E0E28C34B8BFE6F99655FFB2951674B74E40A1261"
    },
    "backend/curriculum/tests/test_repository_foundations_source_layout.py": {
      "bytes": 5762,
      "exists": true,
      "sha256": "60B875224F73A2E049A05C99E82F9907777D359D1327DAD4115F5447195DB5C6"
    },
    "docs/goals/repository-foundations-ledger-decomposition/verify_evidence.py": {
      "bytes": 35891,
      "exists": true,
      "sha256": "4242B9788648D31AA1BB521E75B131EEE4E098CDC449255596DCA8F5558A0721"
    },
    "scripts/checks/check_curriculum_source_layout.py": {
      "bytes": 11201,
      "exists": true,
      "sha256": "09B2481FC577B60B684CE14A15CCC27D4B00F052906D1D257A58B5B83F6DD983"
    },
    "scripts/checks/check_quality_gates.py": {
      "bytes": 1680,
      "exists": true,
      "sha256": "77681057B9D1A1AB33AA8A2EF52FD4D8AB1AE747F358623914733A4C27E1E38F"
    }
  },
  "manifest_fingerprints": {
    "PRE_CUTOVER_CONTENT_MANIFEST.json": {
      "bytes": 198744,
      "exists": true,
      "sha256": "10EB6FE810A6BD236E508BB0E375C8C7A2FF49D6EB49CBDEC49317A9B09A4E43"
    },
    "PRE_SLICE_BASELINE.json": {
      "bytes": 564288,
      "exists": true,
      "sha256": "9AAA2418D8770F669E957F8968CF0FC691C7AD96AD185ADC5C454783B718C4F6"
    }
  },
  "records": {
    "canonical_verifier": {
      "argv": [
        "C:\\Program Files\\Python313\\python.exe",
        "docs/goals/repository-foundations-ledger-decomposition/verify_evidence.py"
      ],
      "command": "python docs/goals/repository-foundations-ledger-decomposition/verify_evidence.py",
      "cwd": "C:\\Users\\Joana\\Documents\\GIT-IT",
      "exit_code": 0,
      "stderr_b64": "",
      "stderr_bytes": 0,
      "stderr_sha256": "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855",
      "stdout_b64": "U2xpY2UgMTYgYWxsIGV2aWRlbmNlIHJlcGxheSBwYXNzZWQuDQo=",
      "stdout_bytes": 38,
      "stdout_sha256": "6991786E7B43D1A329197A310CCD5EAADC0DE65BEB724EB4598B6D9290798738"
    },
    "complete_curriculum_tests": {
      "argv": [
        "C:\\Program Files\\Python313\\python.exe",
        "-m",
        "pytest",
        "-q",
        "backend/curriculum/tests"
      ],
      "command": "python -m pytest -q backend/curriculum/tests",
      "cwd": "C:\\Users\\Joana\\Documents\\GIT-IT",
      "exit_code": 0,
      "stderr_b64": "",
      "stderr_bytes": 0,
      "stderr_sha256": "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855",
      "stdout_b64": "Li4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uIFsgIDQlXQ0KLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uIFsgIDklXQ0KLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uIFsgMTQlXQ0KLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uIFsgMTglXQ0KLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uIFsgMjMlXQ0KLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uIFsgMjglXQ0KLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uIFsgMzIlXQ0KLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uIFsgMzclXQ0KLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uIFsgNDIlXQ0KLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uIFsgNDclXQ0KLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uIFsgNTElXQ0KLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uIFsgNTYlXQ0KLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uIFsgNjElXQ0KLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uIFsgNjUlXQ0KLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uIFsgNzAlXQ0KLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uIFsgNzUlXQ0KLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uIFsgODAlXQ0KLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uIFsgODQlXQ0KLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uIFsgODklXQ0KLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uIFsgOTQlXQ0KLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uIFsgOTglXQ0KLi4uLi4uLi4uLi4uLi4uLiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIFsxMDAlXQ0KMTUyOCBwYXNzZWQgaW4gNTMwLjk2cyAoMDowODo1MCkNCg==",
      "stdout_bytes": 1816,
      "stdout_sha256": "D2BDB532EF8DDD0DA8A9C4C7FFD0D548E3591C23BE0D9357707FAB34C31C9BD3"
    },
    "curriculum_source_layout": {
      "argv": [
        "C:\\Program Files\\Python313\\python.exe",
        "scripts/checks/check_curriculum_source_layout.py"
      ],
      "command": "python scripts/checks/check_curriculum_source_layout.py",
      "cwd": "C:\\Users\\Joana\\Documents\\GIT-IT",
      "exit_code": 0,
      "stderr_b64": "",
      "stderr_bytes": 0,
      "stderr_sha256": "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855",
      "stdout_b64": "Q3VycmljdWx1bSBzb3VyY2UgbGF5b3V0IGlzIGNvbnNpc3RlbnQuDQo=",
      "stdout_bytes": 41,
      "stdout_sha256": "EB6C5FC12D4741A7113D42A3E25941B14D8D6AFDAEB455D27C3CF2F3762BABC0"
    },
    "diff_check": {
      "argv": [
        "git",
        "diff",
        "--check"
      ],
      "command": "git diff --check",
      "cwd": "C:\\Users\\Joana\\Documents\\GIT-IT",
      "exit_code": 0,
      "stderr_b64": "d2FybmluZzogaW4gdGhlIHdvcmtpbmcgY29weSBvZiAnYmFja2VuZC9jdXJyaWN1bHVtL3NlZWRfZGF0YS9zb3VyY2UvY2hhbGxlbmdlX3NwZWNzL3YzX3N0b3J5X2NoYWxsZW5nZXMucHknLCBDUkxGIHdpbGwgYmUgcmVwbGFjZWQgYnkgTEYgdGhlIG5leHQgdGltZSBHaXQgdG91Y2hlcyBpdAp3YXJuaW5nOiBpbiB0aGUgd29ya2luZyBjb3B5IG9mICdmcm9udGVuZC9zcmMvc2hhcmVkL2FwaS9nZW5lcmF0ZWQvYXBpVHlwZXMudHMnLCBDUkxGIHdpbGwgYmUgcmVwbGFjZWQgYnkgTEYgdGhlIG5leHQgdGltZSBHaXQgdG91Y2hlcyBpdAo=",
      "stderr_bytes": 305,
      "stderr_sha256": "C6F305F77487A18BE481E985025372B2CA5F55301083F25531503B4E80DFB459",
      "stdout_b64": "",
      "stdout_bytes": 0,
      "stdout_sha256": "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855"
    },
    "fast_quality_gates": {
      "argv": [
        "C:\\Program Files\\Python313\\python.exe",
        "scripts/checks/check_quality_gates.py"
      ],
      "command": "python scripts/checks/check_quality_gates.py",
      "cwd": "C:\\Users\\Joana\\Documents\\GIT-IT",
      "exit_code": 0,
      "stderr_b64": "",
      "stderr_bytes": 0,
      "stderr_sha256": "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855",
      "stdout_b64": "DQo9PT4gcHl0aG9uIHNjcmlwdHMvY2hlY2tfbGVnYWN5X3Rlcm1zLnB5DQpObyBmb3JiaWRkZW4gbGVnYWN5IHByb2R1Y3Qgdm9jYWJ1bGFyeSBmb3VuZCBpbiBhY3RpdmUgY29kZS4NCg0KPT0+IHB5dGhvbiBzY3JpcHRzL2NoZWNrX2FyY2hpdGVjdHVyZV9ib3VuZGFyaWVzLnB5DQpBcmNoaXRlY3R1cmUgYm91bmRhcmllcyBsb29rIGNsZWFuLg0KDQo9PT4gcHl0aG9uIHNjcmlwdHMvY2hlY2tfY3NzX2FyY2hpdGVjdHVyZS5weQ0KQ1NTIGFyY2hpdGVjdHVyZSBsb29rcyBjbGVhbi4NCg0KPT0+IHB5dGhvbiBzY3JpcHRzL2NoZWNrcy9jaGVja19jdXJyaWN1bHVtX3NvdXJjZV9sYXlvdXQucHkNCkN1cnJpY3VsdW0gc291cmNlIGxheW91dCBpcyBjb25zaXN0ZW50Lg0KDQo9PT4gcHl0aG9uIHNjcmlwdHMvY2hlY2tfc2VlZF90YXJnZXRzLnB5DQpHZW5lcmF0ZWQgY3VycmljdWx1bSB0YXJnZXRzIGFyZSBjb25zaXN0ZW50ICgyMDU2IGNhc2VzKS4NCg0KPT0+IHB5dGhvbiBzY3JpcHRzL2NoZWNrX2FwaV9jb250cmFjdC5weQ0KR2VuZXJhdGVkIEFQSSBjb250cmFjdCBpcyBjdXJyZW50Lg0KDQo9PT4gcHl0aG9uIHNjcmlwdHMvY2hlY2tfZnJvbnRlbmRfYXBpX3VzYWdlLnB5DQpGcm9udGVuZCBydW50aW1lIEFQSSB3cmFwcGVycyB1c2UgdGhlIGdlbmVyYXRlZCBBUEkgY29udHJhY3QgaGVscGVyLg0KDQo9PT4gcHl0aG9uIHNjcmlwdHMvY2hlY2tfYXBpX3R5cGVfYWRvcHRpb24ucHkNClJ1bnRpbWUgQVBJIHdyYXBwZXIgdHlwZXMgY29tcG9zZSB0aGUgZ2VuZXJhdGVkIEFQSSBjb250cmFjdC4NCg0KPT0+IHB5dGhvbiBzY3JpcHRzL2NoZWNrX2RvY3VtZW50YXRpb25fY3VycmVudC5weQ0KUm9vdCBkb2N1bWVudGF0aW9uIGlzIGN1cnJlbnQgYW5kIC9kb2NzIGlzIGxpbWl0ZWQgdG8gc2NvcGVkIGdvYWxzLg0KDQo9PT4gcHl0aG9uIHNjcmlwdHMvY2hlY2tfY2lfcXVhbGl0eV9nYXRlcy5weQ0KQ0kgcXVhbGl0eSBnYXRlIG1hbmlmZXN0IGlzIGNvbXBsZXRlLg0KDQo9PT4gcHl0aG9uIHNjcmlwdHMvY2hlY2tfcmVwb3NpdG9yeV9hcnRpZmFjdHMucHkNCk5vIGdlbmVyYXRlZC9jYWNoZSBhcnRpZmFjdHMgYXJlIHRyYWNrZWQgYnkgR2l0Lg0KDQpBbGwgZmFzdCBxdWFsaXR5IGdhdGVzIHBhc3NlZC4NCg==",
      "stdout_bytes": 1141,
      "stdout_sha256": "5A2CE72CD9616B4CBED27AAFD0325EAE0D72337732D28528CF038C619F201690"
    },
    "focused_topology_tests": {
      "argv": [
        "C:\\Program Files\\Python313\\python.exe",
        "-m",
        "pytest",
        "-q",
        "backend/curriculum/tests/test_repository_foundations_source_layout.py"
      ],
      "command": "python -m pytest -q backend/curriculum/tests/test_repository_foundations_source_layout.py",
      "cwd": "C:\\Users\\Joana\\Documents\\GIT-IT",
      "exit_code": 0,
      "stderr_b64": "",
      "stderr_bytes": 0,
      "stderr_sha256": "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855",
      "stdout_b64": "Li4uLi4uLi4uLi4uLiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIFsxMDAlXQ0KMTMgcGFzc2VkIGluIDQuMDBzDQo=",
      "stdout_bytes": 101,
      "stdout_sha256": "D9C813BD5FF94AF6AD1474D990E85B01B4D28BA69797D61A081B83D478C62CDA"
    },
    "generated_targets_current": {
      "argv": [
        "C:\\Program Files\\Python313\\python.exe",
        "scripts/checks/check_generated_targets_current.py"
      ],
      "command": "python scripts/checks/check_generated_targets_current.py",
      "cwd": "C:\\Users\\Joana\\Documents\\GIT-IT",
      "exit_code": 0,
      "stderr_b64": "",
      "stderr_bytes": 0,
      "stderr_sha256": "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855",
      "stdout_b64": "Q29sbGVjdGVkIDIwNTYgdmFyaWFudCBzb2x1dGlvbnMuDQpnZW5lcmF0ZWQvZ2VuZXJhdGVkX3RhcmdldHMucHkgaXMgdXAgdG8gZGF0ZS4NCg==",
      "stdout_bytes": 82,
      "stdout_sha256": "CABAD6EE9F4BFBDC456190AA0D8F8070AE4467DBC0D8F070905C1F32CA65D328"
    },
    "relevant_curriculum_tests": {
      "argv": [
        "C:\\Program Files\\Python313\\python.exe",
        "-m",
        "pytest",
        "-q",
        "backend/curriculum/tests/test_blueprint_pedagogy_invariants.py",
        "backend/curriculum/tests/test_chapter_content_invariants.py",
        "backend/curriculum/tests/test_objective_soundness.py",
        "backend/curriculum/tests/test_seed_source_command_routing.py",
        "backend/curriculum/tests/test_arcane_curriculum_preservation.py",
        "backend/curriculum/tests/test_level_brief_required_details.py",
        "backend/curriculum/tests/test_advanced_pedagogy_invariants.py"
      ],
      "command": "python -m pytest -q backend/curriculum/tests/test_blueprint_pedagogy_invariants.py backend/curriculum/tests/test_chapter_content_invariants.py backend/curriculum/tests/test_objective_soundness.py backend/curriculum/tests/test_seed_source_command_routing.py backend/curriculum/tests/test_arcane_curriculum_preservation.py backend/curriculum/tests/test_level_brief_required_details.py backend/curriculum/tests/test_advanced_pedagogy_invariants.py",
      "cwd": "C:\\Users\\Joana\\Documents\\GIT-IT",
      "exit_code": 0,
      "stderr_b64": "",
      "stderr_bytes": 0,
      "stderr_sha256": "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855",
      "stdout_b64": "Li4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uIFsgIDQlXQ0KLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uIFsgIDklXQ0KLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uIFsgMTQlXQ0KLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uIFsgMTklXQ0KLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uIFsgMjQlXQ0KLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uIFsgMjklXQ0KLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uIFsgMzQlXQ0KLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uIFsgMzklXQ0KLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uIFsgNDQlXQ0KLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uIFsgNDklXQ0KLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uIFsgNTQlXQ0KLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uIFsgNTglXQ0KLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uIFsgNjMlXQ0KLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uIFsgNjglXQ0KLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uIFsgNzMlXQ0KLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uIFsgNzglXQ0KLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uIFsgODMlXQ0KLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uIFsgODglXQ0KLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uIFsgOTMlXQ0KLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uIFsgOTglXQ0KLi4uLi4uLi4uLi4uLi4uLi4uLi4uLi4uLiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIFsxMDAlXQ0KMTQ2NSBwYXNzZWQgaW4gMjA1Ljk5cyAoMDowMzoyNSkNCg==",
      "stdout_bytes": 1735,
      "stdout_sha256": "9D55932C99A77F1AC033ADAD115DD3E6BBAA2E61F721D28AD4549B82401D7AA3"
    },
    "ruff": {
      "argv": [
        "C:\\Program Files\\Python313\\python.exe",
        "-m",
        "ruff",
        "check",
        "scripts/checks/check_curriculum_source_layout.py",
        "backend/curriculum/tests/test_repository_foundations_source_layout.py",
        "backend/curriculum/seed_data/source/blueprint/adventure_repository_foundations.py",
        "backend/curriculum/seed_data/source/blueprint/repository_foundations",
        "docs/goals/repository-foundations-ledger-decomposition/verify_evidence.py"
      ],
      "command": "python -m ruff check scripts/checks/check_curriculum_source_layout.py backend/curriculum/tests/test_repository_foundations_source_layout.py backend/curriculum/seed_data/source/blueprint/adventure_repository_foundations.py backend/curriculum/seed_data/source/blueprint/repository_foundations docs/goals/repository-foundations-ledger-decomposition/verify_evidence.py",
      "cwd": "C:\\Users\\Joana\\Documents\\GIT-IT",
      "exit_code": 0,
      "stderr_b64": "",
      "stderr_bytes": 0,
      "stderr_sha256": "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855",
      "stdout_b64": "QWxsIGNoZWNrcyBwYXNzZWQhCg==",
      "stdout_bytes": 19,
      "stdout_sha256": "82B3E6A6C090A57601D22943BD23FCA9218D1031DBE5A7B754092F9A156B4F18"
    },
    "seed_targets": {
      "argv": [
        "C:\\Program Files\\Python313\\python.exe",
        "scripts/checks/check_seed_targets.py"
      ],
      "command": "python scripts/checks/check_seed_targets.py",
      "cwd": "C:\\Users\\Joana\\Documents\\GIT-IT",
      "exit_code": 0,
      "stderr_b64": "",
      "stderr_bytes": 0,
      "stderr_sha256": "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855",
      "stdout_b64": "R2VuZXJhdGVkIGN1cnJpY3VsdW0gdGFyZ2V0cyBhcmUgY29uc2lzdGVudCAoMjA1NiBjYXNlcykuDQo=",
      "stdout_bytes": 59,
      "stdout_sha256": "780C7E0E24569A0D6CAE6CDDE6E93DC9C32557BCC0370AE5974B01A06EC1E86F"
    }
  },
  "version": 1
}
SLICE16_FINAL_COMMAND_RESULTS_END -->

## Review Gates

- PRE plan review: `APPROVED` after correcting command specificity, checker ownership, task sequencing, and non-circular manifest evidence.
- Initial POST/correctness review found one major/P1 evidence-auditability gap: final command output was summarized rather than retained and authenticated. The settled verifier now validates lossless structured results for every matrix row, both pinned manifests, exact outputs/counts, and settled implementation fingerprints.
- Initial maintainability review found one P2 topology bypass for nested Python modules. Recursive relative-path discovery and the `legacy/levels.py` mutation close it.
- POST alignment re-review: `aligned`; no remaining findings.
- Correctness/data-integrity re-review: no remaining findings.
- Maintainability re-review: no remaining slice-blocking findings.
- Accepted follow-up risks outside this slice: retire the stale `source/ch1/` migration scaffold; remove or demote the runtime-overwritten 11-level `ADVENTURE_WAVE_PLANS["repository-foundations"]` literal in `adventures.py`; split `fresh_starts.py` before it grows beyond its enforced 700-line ceiling.
- Final target-perspective verification: `FINAL_VERIFIED`; live canonical verifier, dedicated layout checker, and 2,056-case seed-target checker passed; authenticated 13/1,465/1,528 test records, manifest pins, 1,824 protected paths, and zero staged paths were confirmed. Blockers: none.
