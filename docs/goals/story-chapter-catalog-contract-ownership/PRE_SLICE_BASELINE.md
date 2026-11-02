# Pre-Slice-8 Story/Chapter Catalog Contract Baseline

Captured on 2026-08-10 after the Krypton PRE reviewer returned `APPROVE`, its two preservation-hardening suggestions were incorporated, and before any Slice 8 production, test, generated-contract, or shared-guard implementation edit.

## Preservation Rule

The 111-entry dirty manifest belongs to completed Slice 1-7 work plus the approved Slice 8 plan package. At the terminal gate, 107 entries must remain byte-identical. Four already-dirty shared targets may change only under separate review:

- generated `openapi.json` and `apiTypes.ts` — generator-only Story/Chapter catalog projections; every unrelated component and operation must remain semantically identical;
- the shared architecture checker and algorithm tests — additions only; deletion counts stay frozen at `2` and `0`, and every prior rule/test remains.

The clean Curriculum serializer and Story Map type/API targets are separately hashed below and may change only as planned. New `PRE_SLICE_BASELINE.md`, `EVIDENCE.md`, and the new catalog endpoint test are outside the captured manifest.

## Dirty-Worktree Manifest

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
M | 8148 | 14DD17A24B0C7A0436164CCB3A27816017FE0A1843690D83BD6CD5505933F8A5 | backend/common/openapi.py
M | 49541 | EE01FACCEBD7000817647B775C891508415CE59C5640BC16A1E7A85EF4862014 | backend/common/tests/test_architecture_guard_algorithms.py
M | 17717 | 6B5A2A5AD0B5B7FCBF51485A92FB1EFEA0AD3ACC8C38D420D068DE8D50115935 | backend/curriculum/seed_data/source/adventure_level_specs/v3_advanced_workflows.py
M | 132710 | C4F7F8D31A4D3CD0F6ABA50BB1D2E3847BB8AA927D04499F6A4658181BA14C7F | backend/curriculum/seed_data/source/adventure_level_specs/v3_frost_form_drills.py
M | 39224 | B7FD4B22D941CF80CC9B4E8801942C988D9CDA4A8D828D475EB7343FB3132F62 | backend/curriculum/seed_data/source/adventure_level_specs/v3_skyline_form_drills.py
M | 8462 | E26CE3B95BC2B570D47F361738F64B86415C2B3ACB33C4CA82678E4E1B669332 | backend/curriculum/seed_data/source/challenge_specs/v3_chapter_form_challenges.py
M | 9842 | 077FEBC5852BFBA6B42AFEBA7DA72F187C0642625EAED03F53EA6E224D8785A2 | backend/curriculum/seed_data/source/challenge_specs/v3_story_challenges.py
M | 6322 | 20ED4FE14B2AE2DD5B3D0D348779A10369CB61D88F04C9A33B8E15DE16FF3483 | backend/curriculum/tests/test_seed_data_source_layout.py
M | 2921 | 5147607F3754CBE35B0004E2140409652F4ACD7D2E0079AC708476098231D7E8 | backend/progress/serializers.py
M | 1222 | B47DFA61F7EB58C5D4D7BB1EFB4A862B041631C723FEFC3A7DC1D303A1EE648F | backend/progress/views.py
M | 1370 | 47E63675CB3C3978AB21D5EFEE021A0F3C56ED4F047D2111A103DBCFE8162990 | frontend/src/features/authoring/hooks/useUnsavedChangesGuard.ts
M | 3938 | 19185C6042D968CA88142C6D6DC42CBC86C679DB5FE7DD524F2691A6DBB85052 | frontend/src/features/authoring/pages/ContentEditorPage.tsx
M | 3150 | 7555D28CC021504FC1AB375FD0A2F10511038878DC38370A9F16C4CB5649AC14 | frontend/src/features/home/components/HomeHubView.tsx
M | 1339 | A861F34C13841D805DC48D745AF94651543719D44BACEDE3CB1F176A108516FA | frontend/src/features/home/components/HomeStatsView.tsx
M | 3412 | 8A2BE32FD9DB2E7E1AF66D68F531442DB20458D74D207F5EF9BBF10FB2195AC0 | frontend/src/features/home/preview/fixtures.ts
M | 2279 | 690D9C0B67FC08A67B02216336E4505EB2BEF4FE8DAB71658BA21C91A28DBAC5 | frontend/src/features/home/utils/achievements.test.ts
M | 4566 | 7F7227B65E7C6AC631436459E889E92E0A044A9365C0730EA77D04A154ADC3BC | frontend/src/features/home/utils/achievements.ts
M | 188 | 03032F98394096617A57834BADCEB6348BE42F54E80BBAA360270040A058DD94 | frontend/src/features/stats/api/statsApi.ts
M | 255 | 1AB6D119FC5E3A31D1B9492DA4803776B2220B8689EF963643E596F22EDF70BB | frontend/src/features/stats/types.ts
M | 43654 | 5DA15628791B892AC1577931F2C0058160FE66AE0283B0A7C1EEC417FB8C42CF | frontend/src/shared/api/generated/apiTypes.ts
M | 196402 | 32AD95552CA54D8CD55F33D43551A860E93DAC8803E58A863424C0540D973640 | frontend/src/shared/api/generated/openapi.json
M | 311 | 696A5219C3E4881173A90C9680EA18F34797214D30B9340E1AB9AC158A810CBC | frontend/src/shared/progress/homeSummaryApi.ts
M | 132 | 0DF902817A0C3FBBA46670D34A9B151E8E867BD601BDE9F663CDCA4B311F983B | frontend/src/shared/progress/types.ts
M | 3680 | D773E2234835894CD2B3618B3966DA22C7A632750A3B3C1DA0CCBA9DCA4EDA8E | frontend/src/styles/features/authoring/editor-shell.css
M | 127 | 23DBB5423B746FCC740932B4392E756A28E0622E90984B8EEEAB4DC817B6286E | frontend/src/styles/features/home.css
D | 0 | <deleted> | frontend/src/styles/features/home/achievements.css
M | 4277 | 5A5810592FF0F4D0A84107810C43004BC85BB814C6BC1F8A0752318195A82819 | frontend/src/styles/features/home/stats-achievements.css
D | 0 | <deleted> | frontend/src/styles/features/home/stats-actions.css
M | 3012 | D1B53888A3C08EF617DABD9995E02C53A2735E5D5F13FFCDA802ECBE0420A6FC | frontend/src/styles/features/home/stats-responsive.css
M | 132 | 48574E4043A90DD6A96CDFFC8DFDA25FDAC29410FB2C5997581B428F177230E0 | frontend/src/styles/features/home/stats.css
M | 105348 | 05C6DD54E7797508AD4F0CFC96B176C8B87B78B1ADAC92BFADA1E3DE1E4B4584 | scripts/checks/check_architecture_boundaries.py
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
?? | 6112 | 6C790D25E7A825AD4313C419843DEC5AB700CE393F8D3B2BFDCC829891344256 | backend/progress/tests/test_dashboard_summary_api.py
?? | 3898 | E8EF52C4686AC62FD9A65DCCC252A65826198A758B35B95B62C36DEC26A75EDE | backend/progress/tests/test_stats_summary_api.py
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
?? | 16013 | 471B59110119CFE38190F3CD6559655ACD43C4B616B112B4EC74B9A6F74DC31C | docs/goals/dashboard-summary-contract-ownership/EVIDENCE.md
?? | 861 | F300D132A402D36F26F138A798A3C39F8B00B1C4146D33BCACA6DEB132D04F2E | docs/goals/dashboard-summary-contract-ownership/GOAL.md
?? | 18369 | A10EFBFE795777C0AD61D9D07EAA02D57D8A463CE23A541F978D6AD2FAB11409 | docs/goals/dashboard-summary-contract-ownership/PLAN.md
?? | 20093 | 7ACFA18A91FACFED49B9D04485A17ADE1218EFCE565CB8F46A25EF88B9902899 | docs/goals/dashboard-summary-contract-ownership/PRE_SLICE_BASELINE.md
?? | 5809 | E905D08062CC0CE831B45497A1D3419773F5B87122CA0DB035C8E7B164282E45 | docs/goals/home-hub-profile-workspace-ownership/EVIDENCE.md
?? | 953 | 4BB53EAFE381E67D4DF2F10C0B5E3EBEDCD1E643BDC70944D1DBB2C8F6727B69 | docs/goals/home-hub-profile-workspace-ownership/GOAL.md
?? | 23295 | FE4F75CE0BF20A916D09FF256A791E9736553E7D89035CCA0A271F93A3FCF7C2 | docs/goals/home-hub-profile-workspace-ownership/PLAN.md
?? | 14783 | 3DA3ADB6F5B747F94CDE73D7E0226F365B4E7319DDB32D1E686CAF4BEFEACD55 | docs/goals/home-hub-profile-workspace-ownership/PRE_SLICE_BASELINE.md
?? | 640423 | AF83AD144CE9F8BB13843C2C42DAC17F495AB94E6D82AA9747E596588615B717 | docs/goals/home-hub-profile-workspace-ownership/evidence/home-profile-desktop.png
?? | 254082 | 166B59B24F900DBD082D54BF24D1061BD28FA1CD127CABA28337F6948783FFC9 | docs/goals/home-hub-profile-workspace-ownership/evidence/home-profile-mobile.png
?? | 10525 | C809CE2879B9B89CDC3BC3D55AF0A37329B6CADDCF0650A6816640669E6811D2 | docs/goals/home-overview-ownership/EVIDENCE.md
?? | 1114 | F5A3D201FA7B00910EF7D35160B51BAFF5275BA78C0FF334B44ED86A20B8B80E | docs/goals/home-overview-ownership/GOAL.md
?? | 20857 | 183B5B1FC10717C022D897112FB367FA113718DD25DACA106BCBD049F800D1C5 | docs/goals/home-overview-ownership/PLAN.md
?? | 19080 | B3B42D79F9A05909353A3E2FBC8B52D0C87379BDD71D461003898F156D43F871 | docs/goals/home-overview-ownership/PRE_SLICE_BASELINE.md
?? | 464106 | 6ACFD8681FCB7ADD10E9D0AF5D53E5C4D72E66492355339841984C6E6CC94DDF | docs/goals/home-overview-ownership/evidence/home-overview-desktop.png
?? | 142746 | 49C820AE45906A969DE142103EA5594700210A57B96888FBB98EB99BBCF7A0BA | docs/goals/home-overview-ownership/evidence/home-overview-mobile.png
?? | 11968 | 8AD75AF9ECEBF0E59550C22DAD0C6CF0652566E78929EF1E707A3577D79CD03B | docs/goals/stats-summary-contract-ownership/EVIDENCE.md
?? | 911 | 37436338A76FF11344D8FC3CBDF13E91E8929334A4E08243C6BCD6EFC521F8AE | docs/goals/stats-summary-contract-ownership/GOAL.md
?? | 19663 | 2F58F9FA089BFF4FC2DEC017729699376F6FF851F74C80552027C537184388FA | docs/goals/stats-summary-contract-ownership/PLAN.md
?? | 17662 | 931F206C87E7D3BF6117DFF7301BE075D5BC64FBA2054AC04FD1FFB5062F6908 | docs/goals/stats-summary-contract-ownership/PRE_SLICE_BASELINE.md
?? | 1076 | 7D24A8A7D4D5EDA4424B7D1F4E9E56CB9D0691702CEF94DB2D6DEF5CBEF6E94F | docs/goals/story-chapter-catalog-contract-ownership/GOAL.md
?? | 16084 | 16F7C3FC6029E9E90215D1A5DFF3E69441168D1FB4525D098276C804CA614E3A | docs/goals/story-chapter-catalog-contract-ownership/PLAN.md
?? | 3132 | 59044C5C5AABC34FA418F38B61590D160A2BFD54AFD834C90F8D3D63656DEEFA | frontend/src/features/authoring/components/content-editor/ContentDestinationSection.tsx
?? | 1928 | DEF4CC1436E1CEA182E5A233DA61ED460949B57E2F4EF5F648611702DB961B8C | frontend/src/features/authoring/components/content-editor/ContentEditorDiagnostics.tsx
?? | 1930 | 0C75288F680741AA0B4798753D88288E7BBA435D4EB4FE16551AC3DF30976EF5 | frontend/src/features/authoring/components/content-editor/ContentEditorHeader.tsx
?? | 3443 | 95E28176D9BD979B8C5F2813BD8F05D5C5E21F24F35845D9EBE7845CBD5614CA | frontend/src/features/authoring/components/content-editor/ContentMetadataSection.tsx
?? | 1174 | 27FE1FA39BCBD006A85D854530DE171F8B867AECE73715CA9CFBCF0B7176792C | frontend/src/features/authoring/hooks/contentEditorDraftState.ts
?? | 12327 | F7002971DC8F6C79583B1EAFF6BA88DE178D849E93462F6F2339B43136E99F64 | frontend/src/features/authoring/hooks/useContentEditorController.ts
?? | 26557 | 7CBCA1A3355A240107A0E72FB6F866683A2A5BA1BF6E69B69BE30FC34A04EC13 | frontend/src/features/authoring/pages/ContentEditorPage.test.tsx
?? | 11120 | B84B43D250A819CCF68A8951223B490222629265CD6A5B29406975813F1B828F | frontend/src/features/home/components/HomeHubView.test.tsx
?? | 7766 | 0ACE15912E4DA902CECEE3813C4F21189AFC6FFC8D84395B53682046ECB398A5 | frontend/src/features/home/components/HomeStatsView.test.tsx
?? | 8793 | 1D150278D111C3C5543E118AA8A2C91356A9DAA17EEEDECD4DFED7577999C941 | frontend/src/features/home/components/home-hub/HomeCombatShowcase.tsx
?? | 5974 | 1AF2565858821226EED9D0203668CBD7B133CF40141790B77E02C4E739AD26D9 | frontend/src/features/home/components/home-hub/HomeProfilePanel.tsx
?? | 1358 | 58355B21119DE1B5B177A153A226414B22138F9276C9B954F0D89653B10F14F9 | frontend/src/features/home/components/home-hub/HomeProfileWorkspace.tsx
?? | 3700 | 49658F9515797BBAF82304B60548AE365D180165C87FD58BA9A3D97D1BCDCA03 | frontend/src/features/home/components/home-stats/HomeAchievementGallery.tsx
?? | 6428 | 8D1D1BCE29FA6908052A96B1159F8CABEA4FAF5B915AD64CEB62EBF51BE2AA3F | frontend/src/features/home/components/home-stats/HomeStatsDashboard.tsx
?? | 4799 | 0A138E734CE7EBF06E5471678E80CC50F126AB3F4FBE5B992B4C8DC3C243FE97 | frontend/src/features/home/components/home-stats/homeStatsModel.test.ts
?? | 3139 | D234BA4A38E2E2BCF886ACA81E81E3A1C07EFA3A80B9BEB8D5F0C1C365AD7FF9 | frontend/src/features/home/components/home-stats/homeStatsModel.ts
```

Manifest entries: 111. Terminal strict preservation target: 107 of 107 byte-identical; four shared dirty targets are reviewed separately.

## Shared and Clean Target Baseline

| Path | Non-empty lines | Bytes | SHA-256 | Existing numstat |
|---|---:|---:|---|---|
| `backend/curriculum/serializers.py` | 124 | 4,722 | `B98FB35ED8E886EE3D023FCFF1BA0591D3E68FAC27F36E8B97155B894096E25F` | clean |
| `frontend/src/features/story-map/types.ts` | 92 | 2,436 | `B26915B95D7DA0947D00F9B146B6C33CF887F9B09CC3DBF435E1211D8F25EE08` | clean |
| `frontend/src/features/story-map/api/storyMapApi.ts` | 26 | 1,118 | `36B36F232EF1DE270AD77E97DC548DC169DCA945020CF51B5951F0E75CFAA178` | clean |
| `frontend/src/shared/api/generated/openapi.json` | 5,643 | 196,402 | `32AD95552CA54D8CD55F33D43551A860E93DAC8803E58A863424C0540D973640` | `238 + / 23 -` |
| `frontend/src/shared/api/generated/apiTypes.ts` | 486 | 43,654 | `5DA15628791B892AC1577931F2C0058160FE66AE0283B0A7C1EEC417FB8C42CF` | `11 + / 2 -` |
| `scripts/checks/check_architecture_boundaries.py` | 2,527 | 105,348 | `05C6DD54E7797508AD4F0CFC96B176C8B87B78B1ADAC92BFADA1E3DE1E4B4584` | `2336 + / 2 -` |
| `backend/common/tests/test_architecture_guard_algorithms.py` | 1,032 | 49,541 | `EE01FACCEBD7000817647B775C891508415CE59C5640BC16A1E7A85EF4862014` | `1120 + / 0 -` |

Generated files may change only through `python scripts/generate_api_contract.py`; non-catalog schema/operation projections must remain semantically identical. Guard additions must preserve deletion counts `2` and `0` and all existing 26 algorithm tests.

## Protected Baseline

| Path | Non-empty lines | Bytes | SHA-256 |
|---|---:|---:|---|
| `backend/curriculum/views.py` | 119 | 5,086 | `43EB21D7D4D11E2E8FC0D3284EC762515C64BDECCF7385319AC4108F10EA480C` |
| `backend/curriculum/selectors/stories.py` | 150 | 6,416 | `248B9E0797DC7394FF0DDE2EEEBF195117C8CCCA5D8C67F50AFDB02F981A452A` |
| `backend/curriculum/selectors/progress_counts.py` | 46 | 2,049 | `1088A466966589DDC5205010221CF1B045410CF61CC6F6783D65CEAB9479CE61` |
| `backend/curriculum/services/chests.py` | 39 | 1,403 | `1031F58AC0CE088DF9DE925830CC4E2211B5E4C53597DCDF38D1364F8B042945` |
| `backend/curriculum/models.py` | 189 | 8,108 | `34163BBCBA4876CF633F0EE087382E418E92A35CF028007CE46136027428F0ED` |
| `scripts/api/api_contract.py` | 422 | 19,497 | `FCF41D695D712401E5F98BC347995E89079E3DDCF132DAC6C29FBD1618B14D23` |
| `frontend/src/shared/api/httpClient.ts` | 143 | 5,433 | `41B94C89B7E713598002AD1D0FC627CA63CC13171338D27802A12F4DA59DF8C5` |

## Authenticated Runtime Baseline

A fresh migrated test database and authenticated real URL/view/selector/serializer requests produced:

- `/api/stories/`: HTTP 200, two rows with exact 14-key shape; the first has `prerequisite_story: null`; the second has `{slug: "foundation", title: "Foundation", completed: false}`; all stable model/default fields are present; difficulty values are `beginner`/`advanced`.
- `/api/chapters/?story=summit`: HTTP 200, exactly the filtered chapter with exact 15-key shape; typed four-key `story`; `level_completion` is always `{value: 0.0, numerator: 0, denominator: 0}`; `chest_schedule` is the four exact `{threshold, coins}` rows.
- Existing story/access regression lane: 13 passed in 115.31 seconds.

These values are the executable contract to document, not change.

## Declared/Generated Mismatch Baseline

The current committed schema has all top-level properties but:

- Story requires only `completed,id,lock_reason,locked,owned,prerequisite_story,slug,title`; stable `summary,price,sort_order,is_published,world_slug,difficulty` appear optional.
- `Story.prerequisite_story` is a nullable open object.
- ChapterList requires only `adventure_level_count,challenge_count,chest_schedule,command_skill_count,description,id,level_completion,lock_reason,locked,number,slug,story,title`; stable `sort_order,is_playable` appear optional.
- `ChapterList.story` and `level_completion` are open objects; each chest row is an open object.
- `storyMapApi` overrides the generated operations with handwritten `Story[]` and `LearningChapter[]`, masking these schema gaps.

## Passing-but-Insufficient Baseline

Existing regression tests, generated-contract currency, TypeScript, and architecture checks can pass while these nested response objects remain open and stable fields appear optional. Slice 8 must add direct runtime/schema parity and generated-only ownership without changing values or consumers.
