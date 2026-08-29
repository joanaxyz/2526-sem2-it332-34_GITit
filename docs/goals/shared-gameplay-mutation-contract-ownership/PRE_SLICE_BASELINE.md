# Slice 12 Pre-Implementation Preservation Baseline

Captured after PRE approval and before any Slice 12 production edit.

## Preservation rules

- The manifest below contains all 165 dirty, deleted, and untracked paths present at capture.
- The four already-dirty implementation targets are `frontend/src/shared/api/generated/openapi.json`, `frontend/src/shared/api/generated/apiTypes.ts`, `scripts/checks/check_architecture_boundaries.py`, and `backend/common/tests/test_architecture_guard_algorithms.py`; only the plan-approved deltas may be added to those files.
- All other manifest entries are strict byte-for-byte preservation entries, including the approved Slice 12 `PLAN.md` and `GOAL.md`.
- Clean planned targets may change only within the reviewed file map. Protected files below must retain their exact hashes.
- Generated artifacts must be replaced only by the repository generator.

## Full dirty-worktree manifest at capture

Format: `status | bytes | SHA-256 | path`. Deleted paths are recorded as absent.

```text
 M | 3669 | 4C0992166F52CDAB966461ECCC3BB5D287C926C6C10DFA33E1DF43A68015480E | backend/accounts/serializers.py
 M | 8707 | 67C8782706E7A774F4DCD3F09FD5BFB98AECBE137680EF9418F7065A65CE6517 | backend/accounts/views.py
 M | 652 | D8CE573ABC5ADC1937CE8E88738128C9A0B2929CC69262F3987EEAB9BBAF47AD | backend/adminconsole/flags.py
 M | 1372 | 5D37AE3B8FC3F02E805A7F9FF8B655C268987005F1BCFE3421DF961EC6338825 | backend/adminconsole/selectors/__init__.py
 M | 2401 | 2CE279231AE6F7AADA4F31FA15215F20487448DEAC737F0A2F8042392E92AD7E | backend/adminconsole/selectors/content.py
 M | 2664 | 9A70B23A9EAE0E9DFFEFB9CA442C81970B4299266248F739FC8D686BD6C70685 | backend/adminconsole/selectors/curriculum.py
 M | 1497 | 9C8F4789719F218758E701551AB10FF5C8FAEE0426796D4C8256A379038557DB | backend/adminconsole/selectors/users.py
 M | 575 | 090B9B09BFA5362B97C07B98F899F3C5CA7E292E374802ABBFCBD08DF4124179 | backend/adminconsole/services/__init__.py
 M | 9055 | 4F5176CE4C42A6914D4585AEDE064A710CA76585C32A2A40B18EDCCBB7B292AC | backend/adminconsole/services/curriculum.py
 M | 21785 | FBA9B549BDAC702FDCF24153D835113FC4FAB2C1D4F1CA59E14A73EA82F8F536 | backend/adminconsole/tests/test_admin_api.py
 D | ABSENT | ABSENT | backend/adminconsole/views.py
 M | 13900 | 47749F4758ABEEA6021DA3431E2525113564312E1890186EB6745F21CA4708ED | backend/authoring/services/core.py
 M | 14068 | CC0B70899957BD36CCE1D49A890A23C23692EA2F5A842C1577334BADD2729BEC | backend/authoring/tests/test_authoring_api.py
 M | 6546 | 13E7DE38857BEB39194140BEA54D69A9B60EF21B98972398683369651557A93C | backend/common/openapi.py
 M | 76454 | 949FCA4E22082821D3AA8E4D334749C97262193B13C13E948B7153BB1402064F | backend/common/tests/test_architecture_guard_algorithms.py
 M | 17717 | 6B5A2A5AD0B5B7FCBF51485A92FB1EFEA0AD3ACC8C38D420D068DE8D50115935 | backend/curriculum/seed_data/source/adventure_level_specs/v3_advanced_workflows.py
 M | 132710 | C4F7F8D31A4D3CD0F6ABA50BB1D2E3847BB8AA927D04499F6A4658181BA14C7F | backend/curriculum/seed_data/source/adventure_level_specs/v3_frost_form_drills.py
 M | 39224 | B7FD4B22D941CF80CC9B4E8801942C988D9CDA4A8D828D475EB7343FB3132F62 | backend/curriculum/seed_data/source/adventure_level_specs/v3_skyline_form_drills.py
 M | 8462 | E26CE3B95BC2B570D47F361738F64B86415C2B3ACB33C4CA82678E4E1B669332 | backend/curriculum/seed_data/source/challenge_specs/v3_chapter_form_challenges.py
 M | 9842 | 077FEBC5852BFBA6B42AFEBA7DA72F187C0642625EAED03F53EA6E224D8785A2 | backend/curriculum/seed_data/source/challenge_specs/v3_story_challenges.py
 M | 5780 | 58153FD96108F8C40C02E6521CCB192C2AA5D1B7EA2C84CA5BFA07A068F3E0C8 | backend/curriculum/serializers.py
 M | 6322 | 20ED4FE14B2AE2DD5B3D0D348779A10369CB61D88F04C9A33B8E15DE16FF3483 | backend/curriculum/tests/test_seed_data_source_layout.py
 M | 1939 | CC86C33E7EB970B1AE3A33D94220271493C99F6AD3B8FF513C8B6F580EC2D40E | backend/players/views.py
 M | 2921 | 5147607F3754CBE35B0004E2140409652F4ACD7D2E0079AC708476098231D7E8 | backend/progress/serializers.py
 M | 1222 | B47DFA61F7EB58C5D4D7BB1EFB4A862B041631C723FEFC3A7DC1D303A1EE648F | backend/progress/views.py
 M | 1887 | 21CF4A8B28FEBBC7F2F04D639AA439790F4A9FE3E202AAE051541E79D0F13CB3 | backend/shop/catalog.py
 M | 10751 | 8F2E5364F3EEE822994C1600A5586DE62E009831DB5B9B5A3AC3E832F048FBB6 | backend/shop/tests/test_shop_catalog.py
 M | 1637 | 7E20E33E019D46B3AEC435530B91525AF1C7136B676CE16C49DA74E8114E1016 | backend/shop/views.py
 M | 1427 | 095A6B4EE87F6B228AD36474C8165FE8D3979C65055DA78D2788A64863BAE16C | frontend/src/app/Protected.tsx
 M | 1370 | 47E63675CB3C3978AB21D5EFEE021A0F3C56ED4F047D2111A103DBCFE8162990 | frontend/src/features/authoring/hooks/useUnsavedChangesGuard.ts
 M | 3938 | 19185C6042D968CA88142C6D6DC42CBC86C679DB5FE7DD524F2691A6DBB85052 | frontend/src/features/authoring/pages/ContentEditorPage.tsx
 M | 3150 | 7555D28CC021504FC1AB375FD0A2F10511038878DC38370A9F16C4CB5649AC14 | frontend/src/features/home/components/HomeHubView.tsx
 M | 9699 | 92CBA318DB3BAB6405F9241EFC44774FBD5B63F311E80307068F7D820A86AB3C | frontend/src/features/home/components/HomeLoadoutView.tsx
 M | 1339 | A861F34C13841D805DC48D745AF94651543719D44BACEDE3CB1F176A108516FA | frontend/src/features/home/components/HomeStatsView.tsx
 M | 3412 | 8A2BE32FD9DB2E7E1AF66D68F531442DB20458D74D207F5EF9BBF10FB2195AC0 | frontend/src/features/home/preview/fixtures.ts
 M | 2279 | 690D9C0B67FC08A67B02216336E4505EB2BEF4FE8DAB71658BA21C91A28DBAC5 | frontend/src/features/home/utils/achievements.test.ts
 M | 4566 | 7F7227B65E7C6AC631436459E889E92E0A044A9365C0730EA77D04A154ADC3BC | frontend/src/features/home/utils/achievements.ts
 D | ABSENT | ABSENT | frontend/src/features/shop/api/shopApi.test.ts
 D | ABSENT | ABSENT | frontend/src/features/shop/api/shopApi.ts
 M | 4546 | DE62D3D9E48DF741A8A6E1900221F49654AF17F003A2C984B07DEF8B1110B30A | frontend/src/features/shop/components/CompanionShop.tsx
 M | 7479 | 3B27B4B512696671CB9FB37536012A78C5FF10B749F66875925989C59A00F52D | frontend/src/features/shop/components/StoryShop.tsx
 M | 6035 | 9D6F511DEFFC08CADA33B541B3061FDD2D82F73D6F39B3A09CB22D57E83BE060 | frontend/src/features/shop/pages/ShopPage.tsx
 D | ABSENT | ABSENT | frontend/src/features/shop/types.ts
 M | 1382 | 2AB638715FCECFD7578EDF304C4B85F76418C2024B3B544A3C5F2AD968DA980D | frontend/src/features/shop/utils/shopDisplay.test.ts
 M | 1955 | C2A57EE9E92BB9F18E8FEE5A1FD39B47129F8E16251A4F7FB34E3ADEE8CF2648 | frontend/src/features/shop/utils/shopDisplay.ts
 M | 188 | 03032F98394096617A57834BADCEB6348BE42F54E80BBAA360270040A058DD94 | frontend/src/features/stats/api/statsApi.ts
 M | 255 | 1AB6D119FC5E3A31D1B9492DA4803776B2220B8689EF963643E596F22EDF70BB | frontend/src/features/stats/types.ts
 M | 935 | 1C20E9F67925C3ADA9076989C2646A6B004B7065AA4568CDB60FC729460617E8 | frontend/src/features/story-map/api/storyMapApi.ts
 M | 1494 | 49A0E195772D0617B064E086465C97D34F7581C9B737BCC51A0D0AA64739F0E1 | frontend/src/features/story-map/types.ts
 M | 44161 | 8ACA708EAFFB702635D1EC0E1AA76803DD4D13389616521085AF905681FED92A | frontend/src/shared/api/generated/apiTypes.ts
 M | 200086 | 8581B1975B00F996BC5033AE5B197775416DE66402980B869A70A466521A4C50 | frontend/src/shared/api/generated/openapi.json
 M | 6361 | 3790425184463DB9BC7CB344C4487BFAC48364271EF7521A6CFCF2B78B01C00A | frontend/src/shared/api/httpClient.test.ts
 M | 5453 | EA0CC2B4BBBBB7ADA9E6D3AFDAF4564769CE428A6F7F8C239D69838FBD16702C | frontend/src/shared/api/httpClient.ts
 M | 2103 | A8B39E86686A0281291AD81B3C058CB9B2A93742A63F5C39DADA9CCC1B6D97A8 | frontend/src/shared/auth/authApi.ts
 M | 105 | AB1711BF58E58130560D7775EA720B96743B4B02B33132CFFED5C0EFEFE2DAD4 | frontend/src/shared/auth/types.ts
 M | 2662 | BBC136D1629496E45697393E39AA7D5CAF070D7D76D99710DE5EB19F63EA0BE5 | frontend/src/shared/auth/useAuth.ts
 M | 1514 | 4F48A674FCDE3270AC2B4125D4A51C46B3BE2A7E902863AA905BE03D30E7096E | frontend/src/shared/player-loadout/usePlayerLoadout.ts
 M | 311 | 696A5219C3E4881173A90C9680EA18F34797214D30B9340E1AB9AC158A810CBC | frontend/src/shared/progress/homeSummaryApi.ts
 M | 132 | 0DF902817A0C3FBBA46670D34A9B151E8E867BD601BDE9F663CDCA4B311F983B | frontend/src/shared/progress/types.ts
 M | 3680 | D773E2234835894CD2B3618B3966DA22C7A632750A3B3C1DA0CCBA9DCA4EDA8E | frontend/src/styles/features/authoring/editor-shell.css
 M | 127 | 23DBB5423B746FCC740932B4392E756A28E0622E90984B8EEEAB4DC817B6286E | frontend/src/styles/features/home.css
 D | ABSENT | ABSENT | frontend/src/styles/features/home/achievements.css
 M | 4277 | 5A5810592FF0F4D0A84107810C43004BC85BB814C6BC1F8A0752318195A82819 | frontend/src/styles/features/home/stats-achievements.css
 D | ABSENT | ABSENT | frontend/src/styles/features/home/stats-actions.css
 M | 3012 | D1B53888A3C08EF617DABD9995E02C53A2735E5D5F13FFCDA802ECBE0420A6FC | frontend/src/styles/features/home/stats-responsive.css
 M | 132 | 48574E4043A90DD6A96CDFFC8DFDA25FDAC29410FB2C5997581B428F177230E0 | frontend/src/styles/features/home/stats.css
 M | 3441 | EFDC33789266466A565663C7E6F823AB346CD306D9E148966B198C998EA7CEB5 | scripts/checks/check_api_type_adoption.py
 M | 187005 | 1A71EFCFC67A0A3191DCC45F60FDBC4DF17F50F12BFC9177C1E4F1812D19600B | scripts/checks/check_architecture_boundaries.py
 M | 2929 | 5DF0F9A639BEB7566DEFDA9A405E036E98F0E21BB4A116A39EF8DFC7D544F153 | scripts/checks/check_frontend_api_usage.py
?? | 7669 | 079C3CEAACD9DAC4880769D82C21650868714C376430E16511D81E53F5A21739 | backend/accounts/tests/test_auth_contract_api.py
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
?? | 5208 | 62B1F58A81389DAE7EE3FF0D62E316002630CA55B7F631DB2AA2A8ABCE9AE2C7 | backend/curriculum/tests/test_catalog_contract_api.py
?? | 6112 | 6C790D25E7A825AD4313C419843DEC5AB700CE393F8D3B2BFDCC829891344256 | backend/progress/tests/test_dashboard_summary_api.py
?? | 3898 | E8EF52C4686AC62FD9A65DCCC252A65826198A758B35B95B62C36DEC26A75EDE | backend/progress/tests/test_stats_summary_api.py
?? | 2120 | 06016A0A034AA5DA9820E1D4BBCD539681DE0A7C4E1DF5D9EFDAFBF318172982 | backend/shop/serializers.py
?? | 9580 | E81F8C015F79F3064B29491D6DD0A76661611E3D3ED100C5A81E8E7142AEB0FC | docs/goals/admin-console-http-read-model-ownership/EVIDENCE.md
?? | 639 | 125C9EFD327AB9B48DF65A23DFD1EE066CADCF86B1476B04AA11F7129E282BEA | docs/goals/admin-console-http-read-model-ownership/GOAL.md
?? | 20650 | 441B86D5F23FCC0F6449386F22FAE4132BF6DFED35A0C52F6105CE2E01602B99 | docs/goals/admin-console-http-read-model-ownership/PLAN.md
?? | 12480 | 694F28897AF2AD2ED6C117A3A39121505C594921742232A3B1975305A748A89D | docs/goals/auth-browser-state-boundary/EVIDENCE.md
?? | 17791 | A4DD457387A7C4F4E554CF6CD7DD724803BDC16EB0A0D8D0809AD4994E878996 | docs/goals/auth-browser-state-boundary/PLAN.md
?? | 23046 | D0ACB24F89AAA59C2CEF56D0320D313B6E177AE52289206611D6F4CA095814FA | docs/goals/auth-browser-state-boundary/PRE_SLICE_BASELINE.md
?? | 12030 | EF3599BF16470F2DD6FDC862754BBA537EAC2FB718E9340A572385EE00490318 | docs/goals/auth-session-success-contract-ownership/EVIDENCE.md
?? | 661 | D9851C6BD062CCACAE4F094907D578A7999476C2B1E8825E9E8F076B56FA0C17 | docs/goals/auth-session-success-contract-ownership/GOAL.md
?? | 13407 | 1102C127B3002D6BF83B98154CC9CCC4E7ED234308B57687AD4D3EA80DCBFEE2 | docs/goals/auth-session-success-contract-ownership/PLAN.md
?? | 23226 | D017FE76CC9E75A5324FEAC36829B8449497501287932F5753A35FEB75FEAD6F | docs/goals/auth-session-success-contract-ownership/PRE_SLICE_BASELINE.md
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
?? | 935 | B5921D0621971D517C6C5E919DC59168F1CF1A222F3575D7D04F4FDF46356A0A | docs/goals/shared-gameplay-mutation-contract-ownership/GOAL.md
?? | 17830 | BB5CBDF87EB3938D46C2699295E1ADE29FFC6AC9C3D55BAEC2AE54DCDD29EB34 | docs/goals/shared-gameplay-mutation-contract-ownership/PLAN.md
?? | 10988 | D36D9DD384A92A970AF8E9EBB3A2F89C2880048ED4AFA4F44D23950BC21BF664 | docs/goals/shop-contract-cache-ownership/EVIDENCE.md
?? | 552 | 39DEE889CBEBF1B6E54397F27F6146F1B61850A589E4D9FE8D6690AFFE9F09A4 | docs/goals/shop-contract-cache-ownership/GOAL.md
?? | 20335 | 3DFED767CC653459A0C0560AB625A815A37AA6D3222960252B16C18F61A5894E | docs/goals/shop-contract-cache-ownership/PLAN.md
?? | 27141 | F320BAFFDADE73EBC8F771E5ED1DA68CFD02C2A34F0A304F4FDDFEE56E71DB46 | docs/goals/shop-contract-cache-ownership/PRE_SLICE_BASELINE.md
?? | 11968 | 8AD75AF9ECEBF0E59550C22DAD0C6CF0652566E78929EF1E707A3577D79CD03B | docs/goals/stats-summary-contract-ownership/EVIDENCE.md
?? | 911 | 37436338A76FF11344D8FC3CBDF13E91E8929334A4E08243C6BCD6EFC521F8AE | docs/goals/stats-summary-contract-ownership/GOAL.md
?? | 19663 | 2F58F9FA089BFF4FC2DEC017729699376F6FF851F74C80552027C537184388FA | docs/goals/stats-summary-contract-ownership/PLAN.md
?? | 17662 | 931F206C87E7D3BF6117DFF7301BE075D5BC64FBA2054AC04FD1FFB5062F6908 | docs/goals/stats-summary-contract-ownership/PRE_SLICE_BASELINE.md
?? | 11403 | E1C5AFF44EE6867B4C5BE89DE07B07C40C16F7C22F10725072C96AB6698BFD5B | docs/goals/story-chapter-catalog-contract-ownership/EVIDENCE.md
?? | 1076 | 7D24A8A7D4D5EDA4424B7D1F4E9E56CB9D0691702CEF94DB2D6DEF5CBEF6E94F | docs/goals/story-chapter-catalog-contract-ownership/GOAL.md
?? | 16084 | 16F7C3FC6029E9E90215D1A5DFF3E69441168D1FB4525D098276C804CA614E3A | docs/goals/story-chapter-catalog-contract-ownership/PLAN.md
?? | 20472 | CEA7C8168E719F5B32C85F0C2D791E2809051D6C0FCC6B5EFD641D7A36D8CDA6 | docs/goals/story-chapter-catalog-contract-ownership/PRE_SLICE_BASELINE.md
?? | 2581 | 196D0F669570D3F171CF48A024CA3E37C19A4A5158A1002CF13B07BB9774CC36 | frontend/src/app/Protected.test.tsx
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
?? | 7831 | 7EE83F6817F7D793482523635C7EA6C4DE75A351E8928661CE5E975316957255 | frontend/src/features/shop/pages/ShopPage.test.tsx
?? | 7255 | 67BC57C8F5F9C224A9AD9FECE25B7B6DC3F0FD985A097AA05FB3D0C046318DEF | frontend/src/shared/auth/authSessionBoundary.test.ts
?? | 5902 | 80790432D76A92FC9B32A272DD4BA17A1AF7356145C40595E80BB7A2CBDB9E86 | frontend/src/shared/auth/authSessionBoundary.ts
?? | 7680 | A616855587CA3E7F926B7648D49D417B7C4FF1D27E8B3B9D7A3C9F4DDD5D4793 | frontend/src/shared/auth/useAuth.test.ts
?? | 1471 | 60F87AA921E6B2F443E92B9F896ABA1EC5EC152AA1F73C77CB51B2DE11553E12 | frontend/src/shared/shop/api/shopApi.test.ts
?? | 1133 | 1B5DE86AA7D7D31AA6CE3B0602135BAEAE043D099EA91A9540C022F0235FB0E0 | frontend/src/shared/shop/api/shopApi.ts
?? | 1790 | D7B7AD00EF48B898430B26B9E3C0D3DFFC1F4BD9D31D75E173E266E445F24912 | frontend/src/shared/shop/model/shopPresentation.test.ts
?? | 1496 | 6E17B177FDB0DC1AC7420D5CE8A013CF26D16692C468D7BBC3144398785ED94D | frontend/src/shared/shop/model/shopPresentation.ts
```

## Planned existing target baseline

| Path | Bytes | SHA-256 | Approved mode |
|---|---:|---|---|
| `backend/common/serializers.py` | 1,907 | `3EBA384B586AF981B49D5A25796ACC52A57346DD63BB9699FF099A84F8A6367D` | add four shared request serializers |
| `backend/adventures/views.py` | 11,233 | `F5778BCE26D2F7BE219372C4923B0AC770402BAD5F21639C59C15B0AFFF019FD` | common imports and OpenAPI annotations only |
| `backend/adventures/serializers.py` | 815 | `B85F5FE918EBF53075EE0FE62CFF7777BB7E455B4E1F0C0F50EC8391CD4DE115` | displaced deletion |
| `backend/challenges/views.py` | 10,948 | `6B423DE5A2904FE2A4FE50BBA3ECB061EB7ACF2B4996E9E2ABA8380DD18877E5` | common imports and OpenAPI annotations only |
| `backend/challenges/serializers.py` | 1,291 | `780683E52E6D330F6D07B118B673143A1189CA40AA4DF9D04083340415B5B84D` | retain run-start serializer only |
| `backend/common/tests/test_bug_regressions.py` | 6,927 | `60901528869C97B787785060F4117A948B78B7BF943F04C67D6450D7F61C83CC` | import cutover only |
| generated `openapi.json` | 200,086 | `8581B1975B00F996BC5033AE5B197775416DE66402980B869A70A466521A4C50` | generator output only; already dirty |
| generated `apiTypes.ts` | 44,161 | `8ACA708EAFFB702635D1EC0E1AA76803DD4D13389616521085AF905681FED92A` | generator output only; already dirty |
| `frontend/src/shared/level/types.ts` | 3,700 | `E19C3C127A496C85AE290B67AD8EA710E9EBC3E5135518B0160A0F582C64A884` | generated command-payload refinement only |
| `frontend/src/shared/git/simulator/types.ts` | 1,939 | `C24C15C7B987A4363C9B684D0FA12D39DEFA3ACE606ED385BD994345F2852B9F` | remove duplicate payload only |
| `frontend/src/shared/git/simulator/engine.ts` | 8,538 | `8CCF4CB32520C3D29FAA1CB6E723D777449ECE2BE949FF06BA1E4AB33ADA7E52` | canonical payload import/assertion only |
| `frontend/src/shared/git/simulator/workspaceFiles.ts` | 10,165 | `1EA1F65AA93F4B586B11D33BAA0689F0BCE4302F7E6A44B37596324D1ECBC86B` | shared workspace type import only |
| `frontend/src/shared/level/utils/projectFiles.ts` | 4,510 | `711ACBD814B21633913310BF33B2CF2D00DA116CB7D0C85E1EC7137A5207E3BF` | move workspace type declaration only |
| `frontend/src/shared/level/components/WorkspaceEditorOverlay.tsx` | 13,061 | `FC811AB557285265E259114A8B6804B239EA8DD92CB31D23A409A59225CE6FCE` | type import only |
| `frontend/src/shared/level/components/ProjectStructurePanel.tsx` | 12,413 | `DF5085D135B9EEC812E89DCD7B4D558E321993AD8E894B00519C9E54602141D3` | replace structural input shadows only |
| `frontend/src/shared/level/commandExecution.ts` | 615 | `8BFADAED18324D9638345CC4AC9DC600CA3770CB93CEFD271B2ABED96B5E70D2` | canonical import only |
| `frontend/src/shared/level-runtime/useOptimisticGitCommand.ts` | 4,490 | `825BD56EB91F7838B0BB0439F8F4FD502454FE38FF17CCE6E1EF052EADB84D76` | canonical import only |
| `frontend/src/features/adventures/api/adventuresApi.ts` | 2,875 | `970E05208BCDB0F383AA2380A6B08AF1A1607157EBE2DDB54B59CF3D30869A55` | shared inputs/adapters only |
| Adventure API test | 2,639 | `24F6056FC26F52BE93F9AD02086F49ABED67CF75F9C9D9FABA7DF74A5C6EB764` | adapter assertions only |
| Adventure hook | 3,754 | `47760BCA311D84EA6AB520ABDF7738004D47EF4BB11FBB2C2468C91C96E3C9A9` | shared type imports only |
| Adventure workspace main | 4,232 | `1C24ADC2305C47AD116658E50920D120C228B1D76B315FEE37A274424EEA190F` | shared type imports only |
| Challenge API | 2,162 | `6021B3EAF297D1F0DE8F367D08C67B3CC4418084BA4F8E5B3DB0EF99A5925A95` | shared inputs/adapters only |
| Challenge API test | 2,376 | `248548B7706B77E051341DDBCB98B3504DAA598425EF505D84E47C31CE21D049` | adapter assertions only |
| Challenge workspace hook | 7,335 | `12DDA73311EA6665723D6012FC3FCABAC76E3D6E1AE41845430D29BC863C7E6C` | shared type imports only |
| Challenge workspace panels | 6,584 | `D178B41D67CFA36FE95A9A2F7E97B6953C4D4F606FF66280AA7CAD03B6802754` | shared type imports only |
| Challenge workspace main | 5,125 | `56C3A79535C836F7AB270F04F78381D86C0A0EC13056DC5210F607F636992E1D` | shared type imports only |
| architecture checker | 187,005 | `1A71EFCFC67A0A3191DCC45F60FDBC4DF17F50F12BFC9177C1E4F1812D19600B` | one focused guard; already dirty |
| architecture algorithm tests | 76,454 | `949FCA4E22082821D3AA8E4D334749C97262193B13C13E948B7153BB1402064F` | focused guard tests; already dirty |

Approved additions absent at capture:

- `backend/common/tests/test_gameplay_mutation_contract.py`
- `frontend/src/shared/level/workspaceFileTypes.ts`
- `frontend/src/shared/level-runtime/runMutationInputs.ts`
- `frontend/src/shared/level-runtime/runMutationInputs.test.ts`
- `docs/goals/shared-gameplay-mutation-contract-ownership/PRE_SLICE_BASELINE.md`
- `docs/goals/shared-gameplay-mutation-contract-ownership/EVIDENCE.md`

## Protected-file baseline

| Path | Bytes | SHA-256 |
|---|---:|---|
| Adventure models | 8,698 | `EE7556C69C80B66AEBF6AE778686B9357B9F8F53A85E70921F48B6574A1A5CAE` |
| Adventure payloads | 13,921 | `E7BD7D8D130CD3290C218562F7168D54785DAE07129BCB878C5F55C3AF74667D` |
| Adventure services package entry | 721 | `FA0FD9C3DC211CF36919758320B34691F6E53DC54A76A12EF2EB1C0F6A6AEFB9` |
| Adventure commands service | 9,127 | `72B25A95D8BEC4B6DE7AFDC2BA8E165037BECBD6F75C93B433F3900D5BB715AC` |
| Adventure history service | 1,753 | `520AA8B6E2890DCF6AB9597595E4A953DECC04837504FC1F4D0EEF9DA39F0A66` |
| Adventure runs service | 13,523 | `27003DDB704C592CB9B10FEEEADEE07FC6D02AB96026FC09A13C299DBEFE2860` |
| Adventure selectors service | 3,341 | `3AC61458EC3E40175F0F3B09A3EABCDDBE17A6E1A259DF25C624C1ED482384F7` |
| Challenge models | 7,012 | `4DC4B3C036AD54342E7D9B7D030B1E09C8B5BE9EFEA8751B3D232F7A5355F3E5` |
| Challenge payloads | 9,387 | `7C72D7696EBF8520069A9BF84554A8297BBA076EC68A936B4FEE1F89FD51B8C9` |
| Challenge services package entry | 332 | `C96660D5EEE3655774B3053C76BE0A06D0075CB26F85B32CAFA4F8ABDD113408` |
| Challenge command-processing service | 14,566 | `881D3BAE316DD30BFD8348547FF29921D335954DECBE287E2329E07E1D7BE52F` |
| Challenge history service | 1,456 | `CFCAA43D0CAD2E8DE5F80DA6C250C59BF392652AD71385C92F1B9FFBD03491A8` |
| Challenge runs service | 7,956 | `6AB52EB609B0326576C595780C758AB6DCD7E2D1721740F3B2EDA1FCD9ADBA5D` |
| Challenge variants service | 2,464 | `FA6EC74D7A20EC69685BE6B6E462D76825CC4730D36A526E01639E369ACBD586` |
| shared run-workspace service | 3,389 | `7E5D7BEBA5D9DE49F599EDE1F94BE184983D7E078D922A33FB5CF33F7039BFAD` |
| backend workspace mutation algorithms | 9,434 | `653CF99BE327A0A0888B6B8EDF1AE6C1EB2549CC5D62DDE6A0F6827360ECA58E` |
| backend route owner | 1,091 | `52863A1873884DBC9870FCEB21D6F322195D49492DF4A00308ED8CA31E846623` |
| Adventure session UI | 10,603 | `533B79C12519C54F17D1134CE0910E3921A01B03A9E497F5CA5E1F10DAAEB9D4` |
| Challenge workspace controller | 14,526 | `1E9AD176C3B427A7B30F9669A5CDD0EA6F9D3D42999A0439D65F62BB96787734` |
| simulator state core | 11,693 | `57B0525EFDF55B4A1331813AB14F8B1C950B299CA72F023AE8662A0199CA0A50` |
| simulator snapshot algorithms | 2,500 | `F0CBF0FA5F1247769F37EDFFF17DB90B18ED10F5454B0F2815CF53899242C6F0` |
| frontend HTTP helper | 5,453 | `EA0CC2B4BBBBB7ADA9E6D3AFDAF4564769CE428A6F7F8C239D69838FBD16702C` |
| API generator implementation | 19,497 | `FCF41D695D712401E5F98BC347995E89079E3DDCF132DAC6C29FBD1618B14D23` |
| completed Slice 11 evidence | 10,988 | `D36D9DD384A92A970AF8E9EBB3A2F89C2880048ED4AFA4F44D23950BC21BF664` |

## Pre-slice executable baseline

Backend focused baseline:

```text
python -m pytest common/tests/test_bug_regressions.py common/tests/test_run_workspace_service.py common/tests/test_workspace_file_mutations.py adventures/tests/test_adventure_command_payload_integrity.py adventures/tests/test_adventure_command_budget_integrity.py challenges/tests/test_challenge_command_payload_integrity.py challenges/tests/test_challenge_command_budget_integrity.py -q
24 passed in 67.34s
```

Frontend focused baseline:

```text
npm test -- --run src/features/adventures/api/adventuresApi.test.ts src/features/challenges/api/challengeRunsApi.test.ts src/shared/git/simulator/workspaceFiles.test.ts
3 files passed; 12 tests passed; duration 23.72s
```

Generated-contract baseline:

```text
python scripts/check_openapi_schema.py
Generated API contract is current.
```

Observed pre-slice contract defects:

- Schema generation emits component-name collision warnings for the two feature-owned `CommandSubmitSerializer` identities and for the two `WorkspaceFileRenameSerializer` identities.
- Adventure create/write bodies generate `WorkspaceFile`/`PatchedWorkspaceFile`; Challenge generates equivalent `WorkspaceFileCreate`/`PatchedWorkspaceFileCreate`.
- Both PATCH runtime serializers require `path`, but generated patched schemas make every field optional.
- DELETE runtime accepts `path` from query parameters, but generated operations expose no query parameter.
- The two frontend APIs repeat six `as ApiRequestBody` assertions and four local request aliases.
- Frontend source declares `CommandExecutionPayload` twice and repeats workspace input shapes across API, feature, shared UI, and simulator modules.
