# Pre-Slice-5 Home Overview Baseline

Captured on 2026-08-10 after PLAN/GOAL PRE review returned `ALIGNED` and before any Slice 5 runtime, test, style, utility, or architecture-checker implementation edit.

## Preservation rule

Every entry in the dirty-worktree manifest belongs to completed Slice 1-4 work or the approved Slice 5 plan package. At the terminal gate, its SHA-256 must remain byte-identical unless the path is one of the explicitly allowed Slice 5 targets. `<deleted>` must remain absent. The two architecture files may change additively only; all prior functions, calls, and tests must remain behaviorally intact.

## Dirty-worktree manifest

Format: `status | bytes | SHA-256 | path`.

```text
 M | 652 | D8CE573ABC5ADC1937CE8E88738128C9A0B2929CC69262F3987EEAB9BBAF47AD | backend/adminconsole/flags.py
 M | 1372 | 5D37AE3B8FC3F02E805A7F9FF8B655C268987005F1BCFE3421DF961EC6338825 | backend/adminconsole/selectors/__init__.py
 M | 2401 | 2CE279231AE6F7AADA4F31FA15215F20487448DEAC737F0A2F8042392E92AD7E | backend/adminconsole/selectors/content.py
 M | 2664 | 9A70B23A9EAE0E9DFFEFB9CA442C81970B4299266248F739FC8D686BD6C70685 | backend/adminconsole/selectors/curriculum.py
 M | 1497 | 9C8F4789719F218758E701551AB10FF5C8FAEE0426796D4C8256A379038557DB | backend/adminconsole/selectors/users.py
 M | 575 | 090B9B09BFA5362B97C07B98F899F3C5CA7E292E374802ABBFCBD08DF4124179 | backend/adminconsole/services/__init__.py
 M | 9055 | 4F5176CE4C42A6914D4585AEDE064A710CA76585C32A2A40B18EDCCBB7B292AC | backend/adminconsole/services/curriculum.py
 M | 21785 | FBA9B549BDAC702FDCF24153D835113FC4FAB2C1D4F1CA59E14A73EA82F8F536 | backend/adminconsole/tests/test_admin_api.py
 D | 0 | <deleted> | backend/adminconsole/views.py
 M | 13900 | 47749F4758ABEEA6021DA3431E2525113564312E1890186EB6745F21CA4708ED | backend/authoring/services/core.py
 M | 14068 | CC0B70899957BD36CCE1D49A890A23C23692EA2F5A842C1577334BADD2729BEC | backend/authoring/tests/test_authoring_api.py
 M | 13936 | 3F0D843743920C05FB6EA27C6ECA7E77313036819F010F7BACA3FA45432F977A | backend/common/tests/test_architecture_guard_algorithms.py
 M | 17717 | 6B5A2A5AD0B5B7FCBF51485A92FB1EFEA0AD3ACC8C38D420D068DE8D50115935 | backend/curriculum/seed_data/source/adventure_level_specs/v3_advanced_workflows.py
 M | 132710 | C4F7F8D31A4D3CD0F6ABA50BB1D2E3847BB8AA927D04499F6A4658181BA14C7F | backend/curriculum/seed_data/source/adventure_level_specs/v3_frost_form_drills.py
 M | 39224 | B7FD4B22D941CF80CC9B4E8801942C988D9CDA4A8D828D475EB7343FB3132F62 | backend/curriculum/seed_data/source/adventure_level_specs/v3_skyline_form_drills.py
 M | 8462 | E26CE3B95BC2B570D47F361738F64B86415C2B3ACB33C4CA82678E4E1B669332 | backend/curriculum/seed_data/source/challenge_specs/v3_chapter_form_challenges.py
 M | 9842 | 077FEBC5852BFBA6B42AFEBA7DA72F187C0642625EAED03F53EA6E224D8785A2 | backend/curriculum/seed_data/source/challenge_specs/v3_story_challenges.py
 M | 6322 | 20ED4FE14B2AE2DD5B3D0D348779A10369CB61D88F04C9A33B8E15DE16FF3483 | backend/curriculum/tests/test_seed_data_source_layout.py
 M | 1370 | 47E63675CB3C3978AB21D5EFEE021A0F3C56ED4F047D2111A103DBCFE8162990 | frontend/src/features/authoring/hooks/useUnsavedChangesGuard.ts
 M | 3938 | 19185C6042D968CA88142C6D6DC42CBC86C679DB5FE7DD524F2691A6DBB85052 | frontend/src/features/authoring/pages/ContentEditorPage.tsx
 M | 3150 | 7555D28CC021504FC1AB375FD0A2F10511038878DC38370A9F16C4CB5649AC14 | frontend/src/features/home/components/HomeHubView.tsx
 M | 3680 | D773E2234835894CD2B3618B3966DA22C7A632750A3B3C1DA0CCBA9DCA4EDA8E | frontend/src/styles/features/authoring/editor-shell.css
 M | 41601 | 8868679E21CD852685B57C30176A1E8CBED520A74B52D1F85181E78328756498 | scripts/checks/check_architecture_boundaries.py
?? | 247 | 1736545581CB7DD5E87C17027A5EEF9DC9F8C503DE4CF5CA05FAB776C8370150 | backend/adminconsole/curriculum_options.py
?? | 4364 | BBDCAEF2C0F976DD282C85C5B54B8C690D907A2D8B00F429410459AA6C89784C | backend/adminconsole/selectors/analytics.py
?? | 1057 | EBDB8B4CA6C6C5BD4696294C8356B91FC7AFCBB2F3549039464533AF05BC0051 | backend/adminconsole/selectors/economy.py
?? | 2306 | 20FB3C07991B0B88549B68740FA4649872DB8A7BA01B1DAEFC42700570786516 | backend/adminconsole/selectors/overview.py
?? | 906 | BBE56F5CD7FB61064EAE86FC99E4E6230933B466D68BFDF4EDD2111517D4A254 | backend/adminconsole/selectors/settings.py
?? | 312 | FD8178093055FF4C545511C45DA6D5AC287CCF2E7A7322FDA7E1DBC4F307F828 | backend/adminconsole/tests/helpers.py
?? | 11502 | 85276D0CA398FF463E7A0B6CBA33C0F02062A39073167AC8088075A8C8977D42 | backend/adminconsole/tests/test_admin_read_api.py
?? | 1101 | A986221D8E08A834FCB7F1CD8AAF163452DBE09229C518C83EDB0EA7773C7F16 | backend/adminconsole/views/__init__.py
?? | 2454 | 3C7D709498131F3CA583AE0D3BA70C7C5A3760304E1E5A881C7CFC6C79C0BD1D | backend/adminconsole/views/content.py
?? | 4152 | 875686586BCC731E59DCA19717D35547DAD4F65D5841CDF39ABB92EDC023F9F6 | backend/adminconsole/views/curriculum.py
?? | 887 | 5A10E4D519C5C22D9996DBE2E0FE9FE04D78DE568F52B69CBAC37AB7B366B316 | backend/adminconsole/views/dashboard.py
?? | 2266 | 9399CE1E89A7D51B0AB912C67C936AC2617EAE8F76280D06B5F001DAEF995417 | backend/adminconsole/views/economy.py
?? | 1258 | 2B76979DF6E0F438D843638DBA730A3B33B90B20048EBD87D77D9E313817E9F5 | backend/adminconsole/views/settings.py
?? | 3037 | A7D97E71FEFA25E44968F45E207BE08CB8B5ECC67B58D0AC36B0224602AC7C2D | backend/adminconsole/views/users.py
?? | 5243 | C3884538AF5ABC1D41EA7FB933EE599CABC2AD82EFBFEB8ACC6ECB5D6087E734 | backend/curriculum/seed_data/source/advanced_story_support.py
?? | 3442 | C083CC4DEF6174BF12A79B8445DCEA616C11490092F7B8B00E6D0834C4635CB9 | backend/curriculum/seed_data/source/adventure_level_specs/form_drill_support.py
?? | 9533 | 7E9BA3510FFA065D8C43A8633B6CE1554CCDB1A06347203AE9BA78A18E7AD58F | backend/curriculum/seed_data/source/challenge_specs/advanced_challenge_support.py
?? | 9580 | E81F8C015F79F3064B29491D6DD0A76661611E3D3ED100C5A81E8E7142AEB0FC | docs/goals/admin-console-http-read-model-ownership/EVIDENCE.md
?? | 639 | 125C9EFD327AB9B48DF65A23DFD1EE066CADCF86B1476B04AA11F7129E282BEA | docs/goals/admin-console-http-read-model-ownership/GOAL.md
?? | 20650 | 441B86D5F23FCC0F6449386F22FAE4132BF6DFED35A0C52F6105CE2E01602B99 | docs/goals/admin-console-http-read-model-ownership/PLAN.md
?? | 7815 | 155FF457F6781A33BE1D9FA27261679961F92D9858CBB01AF6DC6E563B435919 | docs/goals/codebase-maintainability-modernization/EVIDENCE.md
?? | 516 | 044CD7E2BF35DD180F072E28A1362E64EDE7C5085F945A214B3A4450B8A004EB | docs/goals/codebase-maintainability-modernization/GOAL.md
?? | 17302 | D2B0085F30167E3065298E06D3E9C504D29248B27D5EA8D0A4DC7C0EB43FAEC1 | docs/goals/codebase-maintainability-modernization/PLAN.md
?? | 9574 | 1333552ACEEF649472A65B73FBFD86AE9CB40A0F53551C7E553432A964D05488 | docs/goals/content-editor-workflow-ownership/EVIDENCE.md
?? | 1539 | 62C74C74B40B1A60DF54B35FA351B538005A63F379A3E76356A9D225273A8FFC | docs/goals/content-editor-workflow-ownership/GOAL.md
?? | 38613 | 6EDE146133A8D59605F422D485087F5DDB57E3870B57DCDE1E4541C56682C0D6 | docs/goals/content-editor-workflow-ownership/PLAN.md
?? | 7967 | DBBC37B6B8295F0848DBDD2CF10ADC38E6E73F1CA90106E4F255840F124464C9 | docs/goals/content-editor-workflow-ownership/PRE_SLICE_BASELINE.md
?? | 170634 | 996767C8DC6D127C9FAB5E19F61341490065EC063C7ADFFFD6F78B877153C00B | docs/goals/content-editor-workflow-ownership/evidence/content-editor-desktop.png
?? | 89213 | B403715D8C51FEF6F45F9B3B58ED2ACF4E8747EF6F7DA1EF85B974B8085BC29D | docs/goals/content-editor-workflow-ownership/evidence/content-editor-mobile.png
?? | 5809 | E905D08062CC0CE831B45497A1D3419773F5B87122CA0DB035C8E7B164282E45 | docs/goals/home-hub-profile-workspace-ownership/EVIDENCE.md
?? | 953 | 4BB53EAFE381E67D4DF2F10C0B5E3EBEDCD1E643BDC70944D1DBB2C8F6727B69 | docs/goals/home-hub-profile-workspace-ownership/GOAL.md
?? | 23295 | FE4F75CE0BF20A916D09FF256A791E9736553E7D89035CCA0A271F93A3FCF7C2 | docs/goals/home-hub-profile-workspace-ownership/PLAN.md
?? | 14783 | 3DA3ADB6F5B747F94CDE73D7E0226F365B4E7319DDB32D1E686CAF4BEFEACD55 | docs/goals/home-hub-profile-workspace-ownership/PRE_SLICE_BASELINE.md
?? | 640423 | AF83AD144CE9F8BB13843C2C42DAC17F495AB94E6D82AA9747E596588615B717 | docs/goals/home-hub-profile-workspace-ownership/evidence/home-profile-desktop.png
?? | 254082 | 166B59B24F900DBD082D54BF24D1061BD28FA1CD127CABA28337F6948783FFC9 | docs/goals/home-hub-profile-workspace-ownership/evidence/home-profile-mobile.png
?? | 1114 | F5A3D201FA7B00910EF7D35160B51BAFF5275BA78C0FF334B44ED86A20B8B80E | docs/goals/home-overview-ownership/GOAL.md
?? | 20857 | 183B5B1FC10717C022D897112FB367FA113718DD25DACA106BCBD049F800D1C5 | docs/goals/home-overview-ownership/PLAN.md
?? | 3132 | 59044C5C5AABC34FA418F38B61590D160A2BFD54AFD834C90F8D3D63656DEEFA | frontend/src/features/authoring/components/content-editor/ContentDestinationSection.tsx
?? | 1928 | DEF4CC1436E1CEA182E5A233DA61ED460949B57E2F4EF5F648611702DB961B8C | frontend/src/features/authoring/components/content-editor/ContentEditorDiagnostics.tsx
?? | 1930 | 0C75288F680741AA0B4798753D88288E7BBA435D4EB4FE16551AC3DF30976EF5 | frontend/src/features/authoring/components/content-editor/ContentEditorHeader.tsx
?? | 3443 | 95E28176D9BD979B8C5F2813BD8F05D5C5E21F24F35845D9EBE7845CBD5614CA | frontend/src/features/authoring/components/content-editor/ContentMetadataSection.tsx
?? | 1174 | 27FE1FA39BCBD006A85D854530DE171F8B867AECE73715CA9CFBCF0B7176792C | frontend/src/features/authoring/hooks/contentEditorDraftState.ts
?? | 12327 | F7002971DC8F6C79583B1EAFF6BA88DE178D849E93462F6F2339B43136E99F64 | frontend/src/features/authoring/hooks/useContentEditorController.ts
?? | 26557 | 7CBCA1A3355A240107A0E72FB6F866683A2A5BA1BF6E69B69BE30FC34A04EC13 | frontend/src/features/authoring/pages/ContentEditorPage.test.tsx
?? | 11120 | B84B43D250A819CCF68A8951223B490222629265CD6A5B29406975813F1B828F | frontend/src/features/home/components/HomeHubView.test.tsx
?? | 8793 | 1D150278D111C3C5543E118AA8A2C91356A9DAA17EEEDECD4DFED7577999C941 | frontend/src/features/home/components/home-hub/HomeCombatShowcase.tsx
?? | 5974 | 1AF2565858821226EED9D0203668CBD7B133CF40141790B77E02C4E739AD26D9 | frontend/src/features/home/components/home-hub/HomeProfilePanel.tsx
?? | 1358 | 58355B21119DE1B5B177A153A226414B22138F9276C9B954F0D89653B10F14F9 | frontend/src/features/home/components/home-hub/HomeProfileWorkspace.tsx
```

Manifest entries: 71.

## Shared additive architecture baseline

| Path | Full-file SHA-256 | Existing diff SHA-256 | Existing numstat |
|---|---|---|---|
| `scripts/checks/check_architecture_boundaries.py` | `8868679E21CD852685B57C30176A1E8CBED520A74B52D1F85181E78328756498` | `58FE9E9C9BE92DFF7BFE2B7FBBABFB87657BC9F10A94B6BD6BC09C660D5FCDAE` | `698 + / 2 -` |
| `backend/common/tests/test_architecture_guard_algorithms.py` | `3F0D843743920C05FB6EA27C6ECA7E77313036819F010F7BACA3FA45432F977A` | `474F2F556E5EA46E913872CC2ECC0281D998D4111579674CF189C02EF95DD7EB` | `319 + / 0 -` |

The terminal audit must preserve every existing runtime-cycle, Admin Console, Content Editor, and Home Profile guard/test and keep all current checks invoked by `main`.

## Approved Slice 5 target baseline

| Target path | Lines | Bytes | SHA-256 |
|---|---:|---:|---|
| `frontend/src/features/home/components/HomeStatsView.tsx` | 339 | 13,113 | `2B5C55F1EE2239983843AEFCEFBA19970A31B718F4A0DDF644FE04A235EBAF23` |
| `frontend/src/features/home/utils/achievements.ts` | 122 | 5,028 | `11D244DE84EA9EDBCE191DD6B6D835588E51464ED3A3DC19D2709D858DACB633` |
| `frontend/src/features/home/utils/achievements.test.ts` | 93 | 2,519 | `42875CFAFD727EC554E1152D699F58C4A71EEA0A6CD8E16F7E4BE0CCBCE30EB0` |
| `frontend/src/styles/features/home.css` | 7 | 162 | `7666F6671C972C61B4CFB5F88058A5581683A2752E7F71481949F6851B97F351` |
| `frontend/src/styles/features/home/stats.css` | 6 | 163 | `EBE1496E0D1F7233974CFF089C62173BC79E2AEDE68056F60E1C00E5E953645B` |
| `frontend/src/styles/features/home/stats-layout.css` | 435 | 10,572 | `E6841265E81094553B651F22982A389E35544B334FD5E83516993DB98AC816E3` |
| `frontend/src/styles/features/home/stats-achievements.css` | 81 | 1,994 | `2304D5B72A330D77AB099F0E064310BA91D2971DAE7C55D2E80560EEA08D689F` |
| `frontend/src/styles/features/home/stats-responsive.css` | 122 | 3,820 | `9ACB144D2BD9DAD97C0EEC3101BD3B2A409FEC40875B966B2022C441E2D0D856` |
| `frontend/src/styles/features/home/continue-card.css` | 90 | 2,254 | `6ECF53236E678E7FF0955AAA2664C72E57E7ADF26857CEEB40C9D41D42100685` |
| `frontend/src/styles/features/home/stats-actions.css` | 163 | 3,180 | `325CE9A2ECDC31303599B2204BE62D940FE8ADC768F8584CCD1C056464B6B0C7` |
| `frontend/src/styles/features/home/achievements.css` | 226 | 4,330 | `BD39BC4C10E549E5F7233C1BC8AC2B4EAE488068337D3FFB750C3C0F559C940C` |

`stats-actions.css` and `achievements.css` total 389 lines. Runtime TS/TSX has zero consumers for the old `.home-stat-*`, `.home-meter-*`, `.home-activity-*`, `.home-awards*`, and `.home-award-*` selectors. `latestAchievement` has exactly one non-definition reference, in its own test.

## Protected Home baseline

| Protected path | Lines | SHA-256 |
|---|---:|---|
| `frontend/src/features/home/components/HomeHubView.tsx` | 99 | `7555D28CC021504FC1AB375FD0A2F10511038878DC38370A9F16C4CB5649AC14` |
| `frontend/src/features/home/components/HomeHubView.test.tsx` | 287 | `B84B43D250A819CCF68A8951223B490222629265CD6A5B29406975813F1B828F` |
| `frontend/src/features/home/components/home-hub/HomeProfileWorkspace.tsx` | 44 | `58355B21119DE1B5B177A153A226414B22138F9276C9B954F0D89653B10F14F9` |
| `frontend/src/features/home/components/home-hub/HomeProfilePanel.tsx` | 148 | `1AF2565858821226EED9D0203668CBD7B133CF40141790B77E02C4E739AD26D9` |
| `frontend/src/features/home/components/home-hub/HomeCombatShowcase.tsx` | 210 | `1D150278D111C3C5543E118AA8A2C91356A9DAA17EEEDECD4DFED7577999C941` |
| `frontend/src/features/home/components/HomeLoadoutView.tsx` | 218 | `3F8058A3DB98FE0995C1965A8CD59D2B3E408EC3FE2A6596D00F807D802AC112` |
| `frontend/src/features/home/components/HomeRankBadge.tsx` | 28 | `AF9BB7F0C65918D9147431DE32AF73489F4E9043CCCBD8D4CD0F3FFEC8450CBB` |
| `frontend/src/features/home/pages/HomePage.tsx` | 51 | `AC4120D5382A70CFA41444C23A05C480EA765ED80A5BE61BE0F56B0A799B1092` |
| `frontend/src/features/home/preview/HomePreviewPage.tsx` | 31 | `8AE1538CF781412D8A55079534BB55AB7571649FC1187B77D5BBDB9ADE50A6D7` |
| `frontend/src/features/home/preview/fixtures.ts` | 83 | `C81AF5304BF24DAEADF49F68BA80A2AB728912E5E3D0EB39F3C24E40606C0DBA` |
| `frontend/src/features/home/types.ts` | 1 | `B2CA6CAFE5F24B4E5745B14801A642EC6702FA0DAE5F352C2608BF13F238871C` |
| `frontend/src/features/home/api/homeApi.ts` | 1 | `8140C752589F6E6CEEDE2AE186FF32C351A0E2B417D4B57B17C097F9C7394AF4` |

Backend, Stats feature, shared truth owners, generated API contracts, router/layout, and every remaining Home path are files-to-avoid and must have no new Slice 5 diff.

## Deterministic test/static baseline

- Full frontend: 65 files, 455 tests passed.
- Existing focused Home lane: 2 files, 12 tests passed with one worker.
- Scoped Home Overview/Hub/preview ESLint: passed.
- Architecture boundary checker: clean.
- CSS architecture checker: clean.
- `HomeStatsView` has no direct component test before Slice 5.

## Retained browser baseline

Session child: `C:\Users\Joana\AppData\Local\Temp\git-it-home-overview-baseline-470afd0785134ef2a49271442861b5fb`, outside both workspace roots.

| Artifact | Viewport | Bytes | SHA-256 |
|---|---:|---:|---|
| `home-overview-before-desktop.png` | 1440x900 | 464,106 | `6ACFD8681FCB7ADD10E9D0AF5D53E5C4D72E66492355339841984C6E6CC94DDF` |
| `home-overview-before-mobile.png` | 390x844 | 142,746 | `49C820AE45906A969DE142103EA5594700210A57B96888FBB98EB99BBCF7A0BA` |

The isolated initial rich Overview load requested each exact same-origin URL once: wallet `1`, learned skills `1`, shop catalog `1`; cross-origin API requests `0`. Viewport changes were reload-free and counts stayed one each. Continue href was `/stories/arcane-spire`. The heatmap had 14 cells with levels `2,1,3,2,1,4,2,3,2,4,2,4,3,3`. All showed 8 cards (7 unlocked/1 locked); Unlocked showed 8/8 unlocked; Locked showed 3/3 locked. Keyboard order was All -> Unlocked -> Locked. Leaving Overview for Profile and returning reset the filter to All without another request.

The empty preview rendered mastery `0%`, twelve `--` skill values, fourteen level-0 activity cells, story counts `0/0/0`, `Finish rate 0%`, four `--` KPIs, `0 / 19 unlocked`, and eight visible locked cards.

## Responsive computed-layout baseline

Each cell is `computed grid-template-columns @ rounded bounding width`. All widths had `scrollWidth == clientWidth` and no horizontal overflow.

| Viewport | Overview | Achievement grid | Master row | Stat subgrid | KPI row | Command row | Story body | Achievement card |
|---:|---|---|---|---|---|---|---|---|
| 1440 | `979.859 400.219 @1393` | `366.219 @366` | `724.266 208 @946` | `448.484 485.844 @946` | `236.453 236.469 236.469 236.469 @946` | `28.797 208 391.734 51.188 @714` | `128 309.469 @453` | `53.594 194.609 92.453 @366` |
| 1190 | `1149.06 @1149` | `549.531 549.531 @1115` | `893.469 208 @1115` | `529.688 573.859 @1115` | `278.766 x4 @1115` | `28.797 208 560.938 51.188 @883` | `128 397.484 @541` | `53.594 377.922 92.453 @550` |
| 1170 | `1129.59 @1130` | `261.891 261.906 261.891 261.906 @1096` | `874 208 @1096` | `520.344 563.719 @1096` | `273.891/273.906 x4 @1096` | `28.797 208 541.469 51.188 @864` | `128 387.344 @531` | `53.594 90.281 92.453 @262` |
| 810 | `776 @776` | `363 363 @742` | `742 @742` | `742 @742` | `371 371 @742` | `32 363.203 254.234 48 @732` | `128 565.625 @710` | `53.594 191.391 92.453 @363` |
| 750 | `716 @716` | `333 333 @682` | `682 @682` | `682 @682` | `341 341 @682` | `32 335.547 234.875 48 @672` | `128 505.625 @650` | `53.594 161.391 92.453 @333` |
| 530 | `496 @496` | `466.812 @467` | `466.812 @467` | `466.812 @467` | `466.812 @467` | `28.797 365.641 48 @457` | `434.438 @434` | `53.594 295.203 92.453 @467` |
| 470 | `436 @436` | `406.812 @407` | `406.812 @407` | `406.812 @407` | `406.812 @407` | `28.797 305.641 48 @397` | `374.438 @374` | `48 344.438 @407` |
| 390 | `356 @356` | `326.812 @327` | `326.812 @327` | `326.812 @327` | `326.812 @327` | `28.797 225.641 48 @317` | `294.438 @294` | `48 264.438 @327` |

Console output contained only Vite connection and React DevTools development notices. Page-error collection was empty. The browser session was closed, the exact Vite PID 18360 was identity-checked and stopped, port 51062 was verified free, and the temporary Vite config was deleted.

## Known separate contract issue

Runtime/frontend Stats use `activity_trend` and `headline`, while the OpenAPI/generated shape still advertises `activity` and `headlines`. Slice 5 must preserve current runtime behavior and must not claim authenticated API-path proof; that contract repair requires its own plan. The `.home-ref-grid[hidden]` rule in `stats-layout.css` also remains untouched for a separate Profile CSS ownership slice.
