# Pre-Slice-3 Dirty-Worktree Baseline

Captured on 2026-08-06 after the Slice 3 plan documents were created but before any Slice 3 runtime, test, style, or architecture-checker implementation edit.

## Preservation rule

All paths below belong to completed Slice 1/2 work and are outside Slice 3. Their SHA-256 value must be identical at the terminal gate; `<deleted>` must remain absent. The only shared implementation files authorized for additive Slice 3 edits are listed separately below. Do not revert, reformat, rename, or overwrite pre-existing hunks.

| Out-of-scope path | SHA-256 before Slice 3 |
|---|---|
| `backend/adminconsole/curriculum_options.py` | `1736545581CB7DD5E87C17027A5EEF9DC9F8C503DE4CF5CA05FAB776C8370150` |
| `backend/adminconsole/selectors/analytics.py` | `BBDCAEF2C0F976DD282C85C5B54B8C690D907A2D8B00F429410459AA6C89784C` |
| `backend/adminconsole/selectors/economy.py` | `EBDB8B4CA6C6C5BD4696294C8356B91FC7AFCBB2F3549039464533AF05BC0051` |
| `backend/adminconsole/selectors/overview.py` | `20FB3C07991B0B88549B68740FA4649872DB8A7BA01B1DAEFC42700570786516` |
| `backend/adminconsole/selectors/settings.py` | `BBE56F5CD7FB61064EAE86FC99E4E6230933B466D68BFDF4EDD2111517D4A254` |
| `backend/adminconsole/tests/helpers.py` | `FD8178093055FF4C545511C45DA6D5AC287CCF2E7A7322FDA7E1DBC4F307F828` |
| `backend/adminconsole/tests/test_admin_read_api.py` | `85276D0CA398FF463E7A0B6CBA33C0F02062A39073167AC8088075A8C8977D42` |
| `backend/adminconsole/views/__init__.py` | `A986221D8E08A834FCB7F1CD8AAF163452DBE09229C518C83EDB0EA7773C7F16` |
| `backend/adminconsole/views/content.py` | `3C7D709498131F3CA583AE0D3BA70C7C5A3760304E1E5A881C7CFC6C79C0BD1D` |
| `backend/adminconsole/views/curriculum.py` | `875686586BCC731E59DCA19717D35547DAD4F65D5841CDF39ABB92EDC023F9F6` |
| `backend/adminconsole/views/dashboard.py` | `5A10E4D519C5C22D9996DBE2E0FE9FE04D78DE568F52B69CBAC37AB7B366B316` |
| `backend/adminconsole/views/economy.py` | `9399CE1E89A7D51B0AB912C67C936AC2617EAE8F76280D06B5F001DAEF995417` |
| `backend/adminconsole/views/settings.py` | `2B76979DF6E0F438D843638DBA730A3B33B90B20048EBD87D77D9E313817E9F5` |
| `backend/adminconsole/views/users.py` | `A7D97E71FEFA25E44968F45E207BE08CB8B5ECC67B58D0AC36B0224602AC7C2D` |
| `backend/curriculum/seed_data/source/advanced_story_support.py` | `C3884538AF5ABC1D41EA7FB933EE599CABC2AD82EFBFEB8ACC6ECB5D6087E734` |
| `backend/curriculum/seed_data/source/adventure_level_specs/form_drill_support.py` | `C083CC4DEF6174BF12A79B8445DCEA616C11490092F7B8B00E6D0834C4635CB9` |
| `backend/curriculum/seed_data/source/challenge_specs/advanced_challenge_support.py` | `7E9BA3510FFA065D8C43A8633B6CE1554CCDB1A06347203AE9BA78A18E7AD58F` |
| `docs/goals/admin-console-http-read-model-ownership/EVIDENCE.md` | `E81F8C015F79F3064B29491D6DD0A76661611E3D3ED100C5A81E8E7142AEB0FC` |
| `docs/goals/admin-console-http-read-model-ownership/GOAL.md` | `125C9EFD327AB9B48DF65A23DFD1EE066CADCF86B1476B04AA11F7129E282BEA` |
| `docs/goals/admin-console-http-read-model-ownership/PLAN.md` | `441B86D5F23FCC0F6449386F22FAE4132BF6DFED35A0C52F6105CE2E01602B99` |
| `docs/goals/codebase-maintainability-modernization/EVIDENCE.md` | `155FF457F6781A33BE1D9FA27261679961F92D9858CBB01AF6DC6E563B435919` |
| `docs/goals/codebase-maintainability-modernization/GOAL.md` | `044CD7E2BF35DD180F072E28A1362E64EDE7C5085F945A214B3A4450B8A004EB` |
| `docs/goals/codebase-maintainability-modernization/PLAN.md` | `D2B0085F30167E3065298E06D3E9C504D29248B27D5EA8D0A4DC7C0EB43FAEC1` |
| `backend/adminconsole/flags.py` | `D8CE573ABC5ADC1937CE8E88738128C9A0B2929CC69262F3987EEAB9BBAF47AD` |
| `backend/adminconsole/selectors/__init__.py` | `5D37AE3B8FC3F02E805A7F9FF8B655C268987005F1BCFE3421DF961EC6338825` |
| `backend/adminconsole/selectors/content.py` | `2CE279231AE6F7AADA4F31FA15215F20487448DEAC737F0A2F8042392E92AD7E` |
| `backend/adminconsole/selectors/curriculum.py` | `9A70B23A9EAE0E9DFFEFB9CA442C81970B4299266248F739FC8D686BD6C70685` |
| `backend/adminconsole/selectors/users.py` | `9C8F4789719F218758E701551AB10FF5C8FAEE0426796D4C8256A379038557DB` |
| `backend/adminconsole/services/__init__.py` | `090B9B09BFA5362B97C07B98F899F3C5CA7E292E374802ABBFCBD08DF4124179` |
| `backend/adminconsole/services/curriculum.py` | `4F5176CE4C42A6914D4585AEDE064A710CA76585C32A2A40B18EDCCBB7B292AC` |
| `backend/adminconsole/tests/test_admin_api.py` | `FBA9B549BDAC702FDCF24153D835113FC4FAB2C1D4F1CA59E14A73EA82F8F536` |
| `backend/adminconsole/views.py` | `<deleted>` |
| `backend/curriculum/seed_data/source/adventure_level_specs/v3_advanced_workflows.py` | `6B5A2A5AD0B5B7FCBF51485A92FB1EFEA0AD3ACC8C38D420D068DE8D50115935` |
| `backend/curriculum/seed_data/source/adventure_level_specs/v3_frost_form_drills.py` | `C4F7F8D31A4D3CD0F6ABA50BB1D2E3847BB8AA927D04499F6A4658181BA14C7F` |
| `backend/curriculum/seed_data/source/adventure_level_specs/v3_skyline_form_drills.py` | `B7FD4B22D941CF80CC9B4E8801942C988D9CDA4A8D828D475EB7343FB3132F62` |
| `backend/curriculum/seed_data/source/challenge_specs/v3_chapter_form_challenges.py` | `E26CE3B95BC2B570D47F361738F64B86415C2B3ACB33C4CA82678E4E1B669332` |
| `backend/curriculum/seed_data/source/challenge_specs/v3_story_challenges.py` | `077FEBC5852BFBA6B42AFEBA7DA72F187C0642625EAED03F53EA6E224D8785A2` |
| `backend/curriculum/tests/test_seed_data_source_layout.py` | `20ED4FE14B2AE2DD5B3D0D348779A10369CB61D88F04C9A33B8E15DE16FF3483` |

## Shared additive files

| Shared path | Full-file SHA-256 | Existing Git-diff SHA-256 | Existing diff lines |
|---|---|---|---:|
| `scripts/checks/check_architecture_boundaries.py` | `5E97126874E1D37FC3E30170E3673E8F04426F06133C979617C4D74AE51DBCAF` | `1E3E117E045462B304388A8288A3677CC406E42F28D0C5214FE43FD01C468808` | 183 |
| `backend/common/tests/test_architecture_guard_algorithms.py` | `7313C14A8D26C8E736EBCDBD02272F6BCD4B2AB2B87775D36E5ECA6A56EC9FA3` | `6F87404093FA11E847232B5862B2404833A03A662D203B859CE2445620552688` | 78 |
| `backend/authoring/services/core.py` | `A289001AEE3249489E2E1D6911FCB99E6CBA902DFE5A398577ED297E5BC6B12B` | `E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855` | 0 |
| `backend/authoring/tests/test_authoring_api.py` | `957B9B00E67100976AD40E19EF6BF740F37B2EA687A9B170E357B706B52DFCB7` | `E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855` | 0 |

The pre-existing checker additions that must survive unchanged in behavior are:

- `backend/adminconsole/views.py` in `DISPLACED_BACKEND_PATHS`.
- `imported_module_references`.
- `adminconsole_view_source_violations`.
- `adminconsole_selector_source_violations`.
- `adminconsole_view_init_source_violations`.
- `check_adminconsole_http_read_ownership`.
- `check_adminconsole_selectors_are_http_free`.
- `views` included in the thin backend package-initializer check.
- Both admin-console checks invoked by `main`.

The pre-existing tests that must survive unchanged in behavior are:

- `test_adminconsole_layer_guard_rejects_wrong_owner_dependencies`.
- `test_adminconsole_runtime_layers_obey_http_read_ownership`.

The late-discovered backend correction starts from the two clean-file hashes above. It may only centralize the duplicated create/update destination branches with the exact authored-non-null/official-explicit/null-clearing precedence, move the null-ID return before the staff check in `_resolve_official_chapter`, and add one POST/PATCH API regression for a non-staff author's owned authored chapters with `official_chapter: null`. The existing both-non-null validation and non-null staff-boundary test must remain passing.

## Captured dirty status

Before implementation, Git reported modified Slice 1/2 curriculum/admin files, deletion of the flat `backend/adminconsole/views.py`, the two modified shared guard files, the new focused admin view/selector/test/support files, and the two earlier goal directories. The only Slice 3 paths present were this goal directory's planning documents. No frontend runtime or stylesheet path was dirty.
