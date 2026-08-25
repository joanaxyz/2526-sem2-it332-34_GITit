# Pre-Slice-4 Dirty-Worktree and Browser Baseline

Captured on 2026-08-06 after the Slice 4 PLAN/GOAL were created but before any Slice 4 runtime, test, or architecture-checker implementation edit.

## Preservation rule

The paths in the dirty-worktree table belong to completed Slice 1-3 work. Their SHA-256 value must be identical at the terminal gate; `<deleted>` must remain absent. The two shared architecture files are listed separately because Slice 4 may edit them additively. No reset, checkout, staging, broad formatter, or cleanup command may overwrite these artifacts.

## Pre-existing dirty-worktree manifest

| Path | Status | SHA-256 before Slice 4 |
|---|---|---|
| `backend/adminconsole/flags.py` | ` M` | `D8CE573ABC5ADC1937CE8E88738128C9A0B2929CC69262F3987EEAB9BBAF47AD` |
| `backend/adminconsole/selectors/__init__.py` | ` M` | `5D37AE3B8FC3F02E805A7F9FF8B655C268987005F1BCFE3421DF961EC6338825` |
| `backend/adminconsole/selectors/content.py` | ` M` | `2CE279231AE6F7AADA4F31FA15215F20487448DEAC737F0A2F8042392E92AD7E` |
| `backend/adminconsole/selectors/curriculum.py` | ` M` | `9A70B23A9EAE0E9DFFEFB9CA442C81970B4299266248F739FC8D686BD6C70685` |
| `backend/adminconsole/selectors/users.py` | ` M` | `9C8F4789719F218758E701551AB10FF5C8FAEE0426796D4C8256A379038557DB` |
| `backend/adminconsole/services/__init__.py` | ` M` | `090B9B09BFA5362B97C07B98F899F3C5CA7E292E374802ABBFCBD08DF4124179` |
| `backend/adminconsole/services/curriculum.py` | ` M` | `4F5176CE4C42A6914D4585AEDE064A710CA76585C32A2A40B18EDCCBB7B292AC` |
| `backend/adminconsole/tests/test_admin_api.py` | ` M` | `FBA9B549BDAC702FDCF24153D835113FC4FAB2C1D4F1CA59E14A73EA82F8F536` |
| `backend/adminconsole/views.py` | ` D` | `<deleted>` |
| `backend/authoring/services/core.py` | ` M` | `47749F4758ABEEA6021DA3431E2525113564312E1890186EB6745F21CA4708ED` |
| `backend/authoring/tests/test_authoring_api.py` | ` M` | `CC0B70899957BD36CCE1D49A890A23C23692EA2F5A842C1577334BADD2729BEC` |
| `backend/curriculum/seed_data/source/adventure_level_specs/v3_advanced_workflows.py` | ` M` | `6B5A2A5AD0B5B7FCBF51485A92FB1EFEA0AD3ACC8C38D420D068DE8D50115935` |
| `backend/curriculum/seed_data/source/adventure_level_specs/v3_frost_form_drills.py` | ` M` | `C4F7F8D31A4D3CD0F6ABA50BB1D2E3847BB8AA927D04499F6A4658181BA14C7F` |
| `backend/curriculum/seed_data/source/adventure_level_specs/v3_skyline_form_drills.py` | ` M` | `B7FD4B22D941CF80CC9B4E8801942C988D9CDA4A8D828D475EB7343FB3132F62` |
| `backend/curriculum/seed_data/source/challenge_specs/v3_chapter_form_challenges.py` | ` M` | `E26CE3B95BC2B570D47F361738F64B86415C2B3ACB33C4CA82678E4E1B669332` |
| `backend/curriculum/seed_data/source/challenge_specs/v3_story_challenges.py` | ` M` | `077FEBC5852BFBA6B42AFEBA7DA72F187C0642625EAED03F53EA6E224D8785A2` |
| `backend/curriculum/tests/test_seed_data_source_layout.py` | ` M` | `20ED4FE14B2AE2DD5B3D0D348779A10369CB61D88F04C9A33B8E15DE16FF3483` |
| `frontend/src/features/authoring/hooks/useUnsavedChangesGuard.ts` | ` M` | `47E63675CB3C3978AB21D5EFEE021A0F3C56ED4F047D2111A103DBCFE8162990` |
| `frontend/src/features/authoring/pages/ContentEditorPage.tsx` | ` M` | `19185C6042D968CA88142C6D6DC42CBC86C679DB5FE7DD524F2691A6DBB85052` |
| `frontend/src/styles/features/authoring/editor-shell.css` | ` M` | `D773E2234835894CD2B3618B3966DA22C7A632750A3B3C1DA0CCBA9DCA4EDA8E` |
| `backend/adminconsole/curriculum_options.py` | `??` | `1736545581CB7DD5E87C17027A5EEF9DC9F8C503DE4CF5CA05FAB776C8370150` |
| `backend/adminconsole/selectors/analytics.py` | `??` | `BBDCAEF2C0F976DD282C85C5B54B8C690D907A2D8B00F429410459AA6C89784C` |
| `backend/adminconsole/selectors/economy.py` | `??` | `EBDB8B4CA6C6C5BD4696294C8356B91FC7AFCBB2F3549039464533AF05BC0051` |
| `backend/adminconsole/selectors/overview.py` | `??` | `20FB3C07991B0B88549B68740FA4649872DB8A7BA01B1DAEFC42700570786516` |
| `backend/adminconsole/selectors/settings.py` | `??` | `BBE56F5CD7FB61064EAE86FC99E4E6230933B466D68BFDF4EDD2111517D4A254` |
| `backend/adminconsole/tests/helpers.py` | `??` | `FD8178093055FF4C545511C45DA6D5AC287CCF2E7A7322FDA7E1DBC4F307F828` |
| `backend/adminconsole/tests/test_admin_read_api.py` | `??` | `85276D0CA398FF463E7A0B6CBA33C0F02062A39073167AC8088075A8C8977D42` |
| `backend/adminconsole/views/__init__.py` | `??` | `A986221D8E08A834FCB7F1CD8AAF163452DBE09229C518C83EDB0EA7773C7F16` |
| `backend/adminconsole/views/content.py` | `??` | `3C7D709498131F3CA583AE0D3BA70C7C5A3760304E1E5A881C7CFC6C79C0BD1D` |
| `backend/adminconsole/views/curriculum.py` | `??` | `875686586BCC731E59DCA19717D35547DAD4F65D5841CDF39ABB92EDC023F9F6` |
| `backend/adminconsole/views/dashboard.py` | `??` | `5A10E4D519C5C22D9996DBE2E0FE9FE04D78DE568F52B69CBAC37AB7B366B316` |
| `backend/adminconsole/views/economy.py` | `??` | `9399CE1E89A7D51B0AB912C67C936AC2617EAE8F76280D06B5F001DAEF995417` |
| `backend/adminconsole/views/settings.py` | `??` | `2B76979DF6E0F438D843638DBA730A3B33B90B20048EBD87D77D9E313817E9F5` |
| `backend/adminconsole/views/users.py` | `??` | `A7D97E71FEFA25E44968F45E207BE08CB8B5ECC67B58D0AC36B0224602AC7C2D` |
| `backend/curriculum/seed_data/source/advanced_story_support.py` | `??` | `C3884538AF5ABC1D41EA7FB933EE599CABC2AD82EFBFEB8ACC6ECB5D6087E734` |
| `backend/curriculum/seed_data/source/adventure_level_specs/form_drill_support.py` | `??` | `C083CC4DEF6174BF12A79B8445DCEA616C11490092F7B8B00E6D0834C4635CB9` |
| `backend/curriculum/seed_data/source/challenge_specs/advanced_challenge_support.py` | `??` | `7E9BA3510FFA065D8C43A8633B6CE1554CCDB1A06347203AE9BA78A18E7AD58F` |
| `docs/goals/admin-console-http-read-model-ownership/EVIDENCE.md` | `??` | `E81F8C015F79F3064B29491D6DD0A76661611E3D3ED100C5A81E8E7142AEB0FC` |
| `docs/goals/admin-console-http-read-model-ownership/GOAL.md` | `??` | `125C9EFD327AB9B48DF65A23DFD1EE066CADCF86B1476B04AA11F7129E282BEA` |
| `docs/goals/admin-console-http-read-model-ownership/PLAN.md` | `??` | `441B86D5F23FCC0F6449386F22FAE4132BF6DFED35A0C52F6105CE2E01602B99` |
| `docs/goals/codebase-maintainability-modernization/EVIDENCE.md` | `??` | `155FF457F6781A33BE1D9FA27261679961F92D9858CBB01AF6DC6E563B435919` |
| `docs/goals/codebase-maintainability-modernization/GOAL.md` | `??` | `044CD7E2BF35DD180F072E28A1362E64EDE7C5085F945A214B3A4450B8A004EB` |
| `docs/goals/codebase-maintainability-modernization/PLAN.md` | `??` | `D2B0085F30167E3065298E06D3E9C504D29248B27D5EA8D0A4DC7C0EB43FAEC1` |
| `docs/goals/content-editor-workflow-ownership/EVIDENCE.md` | `??` | `1333552ACEEF649472A65B73FBFD86AE9CB40A0F53551C7E553432A964D05488` |
| `docs/goals/content-editor-workflow-ownership/GOAL.md` | `??` | `62C74C74B40B1A60DF54B35FA351B538005A63F379A3E76356A9D225273A8FFC` |
| `docs/goals/content-editor-workflow-ownership/PLAN.md` | `??` | `6EDE146133A8D59605F422D485087F5DDB57E3870B57DCDE1E4541C56682C0D6` |
| `docs/goals/content-editor-workflow-ownership/PRE_SLICE_BASELINE.md` | `??` | `DBBC37B6B8295F0848DBDD2CF10ADC38E6E73F1CA90106E4F255840F124464C9` |
| `docs/goals/content-editor-workflow-ownership/evidence/content-editor-desktop.png` | `??` | `996767C8DC6D127C9FAB5E19F61341490065EC063C7ADFFFD6F78B877153C00B` |
| `docs/goals/content-editor-workflow-ownership/evidence/content-editor-mobile.png` | `??` | `B403715D8C51FEF6F45F9B3B58ED2ACF4E8747EF6F7DA1EF85B974B8085BC29D` |
| `frontend/src/features/authoring/components/content-editor/ContentDestinationSection.tsx` | `??` | `59044C5C5AABC34FA418F38B61590D160A2BFD54AFD834C90F8D3D63656DEEFA` |
| `frontend/src/features/authoring/components/content-editor/ContentEditorDiagnostics.tsx` | `??` | `DEF4CC1436E1CEA182E5A233DA61ED460949B57E2F4EF5F648611702DB961B8C` |
| `frontend/src/features/authoring/components/content-editor/ContentEditorHeader.tsx` | `??` | `0C75288F680741AA0B4798753D88288E7BBA435D4EB4FE16551AC3DF30976EF5` |
| `frontend/src/features/authoring/components/content-editor/ContentMetadataSection.tsx` | `??` | `95E28176D9BD979B8C5F2813BD8F05D5C5E21F24F35845D9EBE7845CBD5614CA` |
| `frontend/src/features/authoring/hooks/contentEditorDraftState.ts` | `??` | `27FE1FA39BCBD006A85D854530DE171F8B867AECE73715CA9CFBCF0B7176792C` |
| `frontend/src/features/authoring/hooks/useContentEditorController.ts` | `??` | `F7002971DC8F6C79583B1EAFF6BA88DE178D849E93462F6F2339B43136E99F64` |
| `frontend/src/features/authoring/pages/ContentEditorPage.test.tsx` | `??` | `7CBCA1A3355A240107A0E72FB6F866683A2A5BA1BF6E69B69BE30FC34A04EC13` |

## Shared additive architecture files

The Slice 4 implementation may append Home Hub rules/tests but must preserve the existing Slice 2/3 behavior.

| Shared path | Full-file SHA-256 | Existing Git-diff SHA-256 | Existing diff lines |
|---|---|---|---:|
| `scripts/checks/check_architecture_boundaries.py` | `967B7BE61EB862A8F7437D223AE40B4F7F1282DC8F00850A51226929C39C5189` | `85539BF9E9D853E20BDA2595FAC8BEA966ACDD36AEFD87D0BB170FD76894C528` | 473 |
| `backend/common/tests/test_architecture_guard_algorithms.py` | `C026727B7B3B6B29C35235F44CD8BBB2BEAD1A2583175BC9D2E6EDCAAC63EE25` | `67D1F9D5B58684E8468D5678881E893428B9839D452677E30CBEDC662CB0A16B` | 229 |

Required preserved checker symbols/invocations include `imported_module_references`, `strongly_connected_components`, all Admin Console ownership helpers/checks, `content_editor_source_violations`, `content_editor_css_violations`, `admin_authoring_import_violations`, `check_content_editor_workflow_ownership`, both backend runtime-cycle/displaced-path checks, and every current call in `main`.

Required preserved tests include the runtime-cycle test, both Admin Console tests, all four Content Editor guard/runtime tests, and their existing assertions. Slice 4 tests are additive.

## Slice 4 source and planned files-to-avoid

`HomeHubView.tsx` starts clean against `HEAD` at 397 lines and SHA-256 `0A93D6B7A604EB810DFA77281658C0D1F808E2B79CB9DCA8ADE1C7A52CF586BF`.

| Protected Home path | Lines | SHA-256 |
|---|---:|---|
| `frontend/src/features/home/pages/HomePage.tsx` | 51 | `AC4120D5382A70CFA41444C23A05C480EA765ED80A5BE61BE0F56B0A799B1092` |
| `frontend/src/features/home/components/HomeStatsView.tsx` | 339 | `2B5C55F1EE2239983843AEFCEFBA19970A31B718F4A0DDF644FE04A235EBAF23` |
| `frontend/src/features/home/components/HomeLoadoutView.tsx` | 218 | `3F8058A3DB98FE0995C1965A8CD59D2B3E408EC3FE2A6596D00F807D802AC112` |
| `frontend/src/features/home/components/HomeRankBadge.tsx` | 28 | `AF9BB7F0C65918D9147431DE32AF73489F4E9043CCCBD8D4CD0F3FFEC8450CBB` |
| `frontend/src/features/home/preview/HomePreviewPage.tsx` | 31 | `8AE1538CF781412D8A55079534BB55AB7571649FC1187B77D5BBDB9ADE50A6D7` |
| `frontend/src/features/home/preview/fixtures.ts` | 83 | `C81AF5304BF24DAEADF49F68BA80A2AB728912E5E3D0EB39F3C24E40606C0DBA` |
| `frontend/src/features/home/types.ts` | 1 | `B2CA6CAFE5F24B4E5745B14801A642EC6702FA0DAE5F352C2608BF13F238871C` |
| `frontend/src/features/home/api/homeApi.ts` | 1 | `8140C752589F6E6CEEDE2AE186FF32C351A0E2B417D4B57B17C097F9C7394AF4` |
| `frontend/src/styles/features/home.css` | 7 | `7666F6671C972C61B4CFB5F88058A5581683A2752E7F71481949F6851B97F351` |
| `frontend/src/styles/features/home/achievements.css` | 226 | `BD39BC4C10E549E5F7233C1BC8AC2B4EAE488068337D3FFB750C3C0F559C940C` |
| `frontend/src/styles/features/home/continue-card.css` | 90 | `6ECF53236E678E7FF0955AAA2664C72E57E7ADF26857CEEB40C9D41D42100685` |
| `frontend/src/styles/features/home/hub.css` | 3 | `DFDBEED190F7E2AFA4267251D88CAC34AC757798E92CD8217DD03681F2584D2E` |
| `frontend/src/styles/features/home/hub-effects.css` | 287 | `3CE40B3656C5A0AF2ED091C5719C9ABB1B440AF62F67FBE420FFC6DD9EB7FCCE` |
| `frontend/src/styles/features/home/hub-layout.css` | 456 | `C80F31CD0C3946DF0B34B00FE17902C54B9C0D4BE6823032F4664939715265DD` |
| `frontend/src/styles/features/home/hub-responsive.css` | 256 | `174DD6530B52E09C0315EBA2882D90F056FD66FCCCE38893D9DBD03A87F5072D` |
| `frontend/src/styles/features/home/loadout.css` | 474 | `D493A53B02FCA5100D268470F0185741D0894D0B3C76F995B7CB211ADEC5AB2E` |
| `frontend/src/styles/features/home/loadout-responsive.css` | 35 | `64D1D65872B5F3E4FF8DAA46AA416B3F86CFB9330B9F41424E3D253C4D721233` |
| `frontend/src/styles/features/home/stats.css` | 6 | `EBE1496E0D1F7233974CFF089C62173BC79E2AEDE68056F60E1C00E5E953645B` |
| `frontend/src/styles/features/home/stats-achievements.css` | 81 | `2304D5B72A330D77AB099F0E064310BA91D2971DAE7C55D2E80560EEA08D689F` |
| `frontend/src/styles/features/home/stats-actions.css` | 163 | `325CE9A2ECDC31303599B2204BE62D940FE8ADC768F8584CCD1C056464B6B0C7` |
| `frontend/src/styles/features/home/stats-layout.css` | 435 | `E6841265E81094553B651F22982A389E35544B334FD5E83516993DB98AC816E3` |
| `frontend/src/styles/features/home/stats-responsive.css` | 122 | `9ACB144D2BD9DAD97C0EEC3101BD3B2A409FEC40875B966B2022C441E2D0D856` |

The terminal gate also requires empty Git diffs for router/HomeLayout, Home preview/API/types/utils, all shared frontend truth owners, and generated API files.

## Deterministic baseline

- Home Hub: 397 lines, 24 imports, no direct component/workflow test.
- Existing Home test lane: `achievements.test.ts` passed 3/3.
- Scoped Home Hub/Page/preview ESLint: passed.
- The completed pre-Slice-4 full frontend baseline is 64 files and 446 tests; the production build and all fast quality gates passed on the same runtime tree.

## Retained browser baseline

The baseline session child is `C:\Users\Joana\AppData\Local\Temp\git-it-home-baseline-f1b881a3ceba42aa946c7969ab71bb9f`, outside both workspace roots. It contains only Vite logs and these screenshots:

| Artifact | Viewport | Bytes | SHA-256 |
|---|---:|---:|---|
| `home-profile-before-desktop.png` | 1440x900 | 634,258 | `316208D72831A91475B372A87B0E0FB9A2B3C5F897897ABF20AB108F7CE133E8` |
| `home-profile-before-mobile.png` | 390x844 | 254,073 | `B0EE96DA52E5088E83304E9EDCE9C02EB103FBDDFF8F403A787FE644FF85CC18` |

Observed baseline contracts:

- `/design-preview/home?tab=profile` rendered Profile selected, Rank Ladder available, Sprite Showcase, and Spellbook.
- Rank Ladder selection changed the inner tab without changing the URL.
- Opening `?empty=1&tab=profile` then selecting Overview produced `?empty=1`, preserving the unrelated parameter and removing only `tab`.
- Desktop `document.scrollWidth - innerWidth` was `-10` (no horizontal overflow).
- Mobile measured viewport 390, document width 380, Profile grid width 356, and Home tab width 356.
- Console contained only Vite connection and React DevTools development notices; page error collection was empty.

The isolated browser session was closed. The exact Vite process tree rooted at PID 26092 was identity-checked and stopped; port 51058 was verified free. The retained temporary child must be deleted only after final visual comparison and only after re-validating that exact path is outside both workspace roots.
