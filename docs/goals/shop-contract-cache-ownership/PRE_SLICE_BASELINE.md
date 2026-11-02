# Pre-Slice-11 Shop Contract and Cache Ownership Baseline

Captured on 2026-08-12 after the Krypton PRE reviewer returned `aligned` and before any Slice 11 production, generated, enforcement, or test edit.

## Preservation modes

The 139-entry dirty manifest below belongs to completed Slices 1–10 plus the reviewed Slice 11 plan package. The following five already-dirty entries are approved mutable targets with their exact starting hashes retained below:

- `backend/common/openapi.py`: delete only the relocated Shop serializer classes and their Shop-only spacing.
- `frontend/src/shared/api/generated/openapi.json` and `apiTypes.ts`: generator output only.
- `scripts/checks/check_architecture_boundaries.py`: replace only the displaced `frontend/src/features/shop/api` data-module path with `frontend/src/shared/shop` in the existing Home Hub rule.
- `docs/goals/shop-contract-cache-ownership/PLAN.md`: reviewed amendments only.

The other 134 captured entries are **strict ordinary mode** and must remain byte-identical. Clean planned targets may change only as listed in the plan. The new serializer/shared-shop/tests, this baseline, and `EVIDENCE.md` were absent at capture. `GOAL.md` is part of the strict manifest and is frozen.

## Dirty-worktree manifest

Format: `status | bytes | SHA-256 | path`.

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
D | 0 | <deleted> | backend/adminconsole/views.py
M | 13900 | 47749F4758ABEEA6021DA3431E2525113564312E1890186EB6745F21CA4708ED | backend/authoring/services/core.py
M | 14068 | CC0B70899957BD36CCE1D49A890A23C23692EA2F5A842C1577334BADD2729BEC | backend/authoring/tests/test_authoring_api.py
M | 7733 | 26B1D55DD56173270786C8368D4DFDB727365B82D5EFB39C8A1C605901B42313 | backend/common/openapi.py
M | 76454 | 949FCA4E22082821D3AA8E4D334749C97262193B13C13E948B7153BB1402064F | backend/common/tests/test_architecture_guard_algorithms.py
M | 17717 | 6B5A2A5AD0B5B7FCBF51485A92FB1EFEA0AD3ACC8C38D420D068DE8D50115935 | backend/curriculum/seed_data/source/adventure_level_specs/v3_advanced_workflows.py
M | 132710 | C4F7F8D31A4D3CD0F6ABA50BB1D2E3847BB8AA927D04499F6A4658181BA14C7F | backend/curriculum/seed_data/source/adventure_level_specs/v3_frost_form_drills.py
M | 39224 | B7FD4B22D941CF80CC9B4E8801942C988D9CDA4A8D828D475EB7343FB3132F62 | backend/curriculum/seed_data/source/adventure_level_specs/v3_skyline_form_drills.py
M | 8462 | E26CE3B95BC2B570D47F361738F64B86415C2B3ACB33C4CA82678E4E1B669332 | backend/curriculum/seed_data/source/challenge_specs/v3_chapter_form_challenges.py
M | 9842 | 077FEBC5852BFBA6B42AFEBA7DA72F187C0642625EAED03F53EA6E224D8785A2 | backend/curriculum/seed_data/source/challenge_specs/v3_story_challenges.py
M | 5780 | 58153FD96108F8C40C02E6521CCB192C2AA5D1B7EA2C84CA5BFA07A068F3E0C8 | backend/curriculum/serializers.py
M | 6322 | 20ED4FE14B2AE2DD5B3D0D348779A10369CB61D88F04C9A33B8E15DE16FF3483 | backend/curriculum/tests/test_seed_data_source_layout.py
M | 2921 | 5147607F3754CBE35B0004E2140409652F4ACD7D2E0079AC708476098231D7E8 | backend/progress/serializers.py
M | 1222 | B47DFA61F7EB58C5D4D7BB1EFB4A862B041631C723FEFC3A7DC1D303A1EE648F | backend/progress/views.py
M | 1427 | 095A6B4EE87F6B228AD36474C8165FE8D3979C65055DA78D2788A64863BAE16C | frontend/src/app/Protected.tsx
M | 1370 | 47E63675CB3C3978AB21D5EFEE021A0F3C56ED4F047D2111A103DBCFE8162990 | frontend/src/features/authoring/hooks/useUnsavedChangesGuard.ts
M | 3938 | 19185C6042D968CA88142C6D6DC42CBC86C679DB5FE7DD524F2691A6DBB85052 | frontend/src/features/authoring/pages/ContentEditorPage.tsx
M | 3150 | 7555D28CC021504FC1AB375FD0A2F10511038878DC38370A9F16C4CB5649AC14 | frontend/src/features/home/components/HomeHubView.tsx
M | 1339 | A861F34C13841D805DC48D745AF94651543719D44BACEDE3CB1F176A108516FA | frontend/src/features/home/components/HomeStatsView.tsx
M | 3412 | 8A2BE32FD9DB2E7E1AF66D68F531442DB20458D74D207F5EF9BBF10FB2195AC0 | frontend/src/features/home/preview/fixtures.ts
M | 2279 | 690D9C0B67FC08A67B02216336E4505EB2BEF4FE8DAB71658BA21C91A28DBAC5 | frontend/src/features/home/utils/achievements.test.ts
M | 4566 | 7F7227B65E7C6AC631436459E889E92E0A044A9365C0730EA77D04A154ADC3BC | frontend/src/features/home/utils/achievements.ts
M | 188 | 03032F98394096617A57834BADCEB6348BE42F54E80BBAA360270040A058DD94 | frontend/src/features/stats/api/statsApi.ts
M | 255 | 1AB6D119FC5E3A31D1B9492DA4803776B2220B8689EF963643E596F22EDF70BB | frontend/src/features/stats/types.ts
M | 935 | 1C20E9F67925C3ADA9076989C2646A6B004B7065AA4568CDB60FC729460617E8 | frontend/src/features/story-map/api/storyMapApi.ts
M | 1494 | 49A0E195772D0617B064E086465C97D34F7581C9B737BCC51A0D0AA64739F0E1 | frontend/src/features/story-map/types.ts
M | 43977 | 6FDAAB9D163FBDE8AFC695D84FFE3E510B814D24BDA67F280EE7EF057F89DE14 | frontend/src/shared/api/generated/apiTypes.ts
M | 199009 | 11AFC8265CD0201952079F8B7F78B98AE4E2C5127E8D1B52DB349954A40E9EE8 | frontend/src/shared/api/generated/openapi.json
M | 6361 | 3790425184463DB9BC7CB344C4487BFAC48364271EF7521A6CFCF2B78B01C00A | frontend/src/shared/api/httpClient.test.ts
M | 5453 | EA0CC2B4BBBBB7ADA9E6D3AFDAF4564769CE428A6F7F8C239D69838FBD16702C | frontend/src/shared/api/httpClient.ts
M | 2103 | A8B39E86686A0281291AD81B3C058CB9B2A93742A63F5C39DADA9CCC1B6D97A8 | frontend/src/shared/auth/authApi.ts
M | 105 | AB1711BF58E58130560D7775EA720B96743B4B02B33132CFFED5C0EFEFE2DAD4 | frontend/src/shared/auth/types.ts
M | 2662 | BBC136D1629496E45697393E39AA7D5CAF070D7D76D99710DE5EB19F63EA0BE5 | frontend/src/shared/auth/useAuth.ts
M | 311 | 696A5219C3E4881173A90C9680EA18F34797214D30B9340E1AB9AC158A810CBC | frontend/src/shared/progress/homeSummaryApi.ts
M | 132 | 0DF902817A0C3FBBA46670D34A9B151E8E867BD601BDE9F663CDCA4B311F983B | frontend/src/shared/progress/types.ts
M | 3680 | D773E2234835894CD2B3618B3966DA22C7A632750A3B3C1DA0CCBA9DCA4EDA8E | frontend/src/styles/features/authoring/editor-shell.css
M | 127 | 23DBB5423B746FCC740932B4392E756A28E0622E90984B8EEEAB4DC817B6286E | frontend/src/styles/features/home.css
D | 0 | <deleted> | frontend/src/styles/features/home/achievements.css
M | 4277 | 5A5810592FF0F4D0A84107810C43004BC85BB814C6BC1F8A0752318195A82819 | frontend/src/styles/features/home/stats-achievements.css
D | 0 | <deleted> | frontend/src/styles/features/home/stats-actions.css
M | 3012 | D1B53888A3C08EF617DABD9995E02C53A2735E5D5F13FFCDA802ECBE0420A6FC | frontend/src/styles/features/home/stats-responsive.css
M | 132 | 48574E4043A90DD6A96CDFFC8DFDA25FDAC29410FB2C5997581B428F177230E0 | frontend/src/styles/features/home/stats.css
M | 187011 | 53814BE32D540A9C4AD360470B7E2A2359B71433B65B2141969BB80FE5ECB169 | scripts/checks/check_architecture_boundaries.py
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
?? | 552 | 39DEE889CBEBF1B6E54397F27F6146F1B61850A589E4D9FE8D6690AFFE9F09A4 | docs/goals/shop-contract-cache-ownership/GOAL.md
?? | 20340 | B5C8D418C007178E37F6DC13A8D58D252E75002EA5C062918ED6195E96D736B8 | docs/goals/shop-contract-cache-ownership/PLAN.md
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
?? | 7255 | 67BC57C8F5F9C224A9AD9FECE25B7B6DC3F0FD985A097AA05FB3D0C046318DEF | frontend/src/shared/auth/authSessionBoundary.test.ts
?? | 5902 | 80790432D76A92FC9B32A272DD4BA17A1AF7356145C40595E80BB7A2CBDB9E86 | frontend/src/shared/auth/authSessionBoundary.ts
?? | 7680 | A616855587CA3E7F926B7648D49D417B7C4FF1D27E8B3B9D7A3C9F4DDD5D4793 | frontend/src/shared/auth/useAuth.test.ts
```

## Planned existing target baseline

| Path | Non-empty lines | Bytes | SHA-256 | Approved mode |
|---|---:|---:|---|---|
| `backend/common/openapi.py` | 143 | 7,733 | `26B1D55DD56173270786C8368D4DFDB727365B82D5EFB39C8A1C605901B42313` | already dirty; delete relocated Shop serializers only |
| `backend/shop/views.py` | 31 | 1,435 | `8B40DE2FDF06D06C1B947C13C641EDC8BD9C2FD7D294415670B30C398AA48279` | request validation and exact response serialization |
| `backend/players/views.py` | 38 | 1,875 | `22E83ED156528BD73BDEB50C686F1FC6200DDBCD143928FD5C050034C845257C` | Shop serializer imports and equip response serialization only |
| `backend/shop/catalog.py` | 61 | 2,278 | `316C96379004EF0729C135E1C4498C70B7E901D393CF73B78B72D9E0F95C7D8E` | remove duplicate top-level story listing metadata |
| `backend/shop/tests/test_shop_catalog.py` | 189 | 7,978 | `BBB447FB49A2EB5AB13EEA5BD73ED33C9409D6C19661D6579EF1C2AFC16E1575` | exact contract and strict-input cases |
| generated `openapi.json` | 5,732 | 199,009 | `11AFC8265CD0201952079F8B7F78B98AE4E2C5127E8D1B52DB349954A40E9EE8` | generator output only |
| generated `apiTypes.ts` | 490 | 43,977 | `6FDAAB9D163FBDE8AFC695D84FFE3E510B814D24BDA67F280EE7EF057F89DE14` | generator output only |
| `frontend/src/features/shop/api/shopApi.ts` | 25 | 670 | `BB3EE72E0DFF791F137A88B630959166DF4669271851496DAB4098AAB87083D9` | displaced file deletion |
| `frontend/src/features/shop/api/shopApi.test.ts` | 22 | 865 | `A217C537BF3BA12427243F9A6A53AB73617E472907DAC28A85CD859C756591EF` | displaced test deletion after movement |
| `frontend/src/features/shop/types.ts` | 31 | 850 | `23CDD2F3C73203F7FCE2AD686DDE0147887D54177A02FF339ADA04D52E26319D` | handwritten wire-contract deletion |
| `frontend/src/features/shop/pages/ShopPage.tsx` | 139 | 5,854 | `C83BB0D7366FCEC11120F5B733D82A8543D5E3978E27C27109943347D31E4186` | shared query/wallet and purchase cache transition only |
| `frontend/src/features/shop/components/CompanionShop.tsx` | 121 | 4,492 | `C2BFCF39C3DF42B6B2DFD3FE63FEF83946BEB1B18DB0C7909A815BCD3A8BAAB1` | presentation import cutover only |
| `frontend/src/features/shop/components/StoryShop.tsx` | 199 | 7,425 | `B29B83B894BE3017948D66416B372C60EE911ED302ED52009150E98FBC845438` | presentation import cutover only |
| `frontend/src/features/shop/utils/shopDisplay.ts` | 96 | 3,373 | `F230C288EFBB8E0813769E48035F5E79EFD1EDBD115A339EB03D299EB842A72C` | remove shared projection responsibilities |
| `frontend/src/features/shop/utils/shopDisplay.test.ts` | 57 | 2,498 | `CA5880741618FBBFAB1B1F2A11D485C889FE59F0065CFC830A73F51F461D9EDF` | keep feature action/tab cases only |
| `frontend/src/features/home/components/HomeLoadoutView.tsx` | 204 | 9,745 | `3F8058A3DB98FE0995C1965A8CD59D2B3E408EC3FE2A6596D00F807D802AC112` | shared Shop imports/query options only |
| `frontend/src/shared/player-loadout/usePlayerLoadout.ts` | 46 | 1,689 | `61041FA09C5E0815B159471665785E9A12CDF552DFE123BB2E226E0E8CCD1F33` | remove partial DTO/raw request, preserve observer policy |
| `scripts/checks/check_api_type_adoption.py` | 81 | 3,443 | `95E5E41BCD5067CE3FAA613D4A211F5B6C1C8403E08A994E9AB9AADBD011E0A5` | enforcement path replacement only |
| `scripts/checks/check_frontend_api_usage.py` | 70 | 2,931 | `69FBE6F05FB2AD390BF061FD64D2CC21FA2C4CE7EED19104336BEB1E0D59AC8A` | enforcement path replacement only |
| `scripts/checks/check_architecture_boundaries.py` | 4,527 | 187,011 | `53814BE32D540A9C4AD360470B7E2A2359B71433B65B2141969BB80FE5ECB169` | one displaced module-path replacement only |
| `docs/goals/shop-contract-cache-ownership/PLAN.md` | 158 | 20,340 | `B5C8D418C007178E37F6DC13A8D58D252E75002EA5C062918ED6195E96D736B8` | reviewed plan; amendments require review |
| `docs/goals/shop-contract-cache-ownership/GOAL.md` | 9 | 552 | `39DEE889CBEBF1B6E54397F27F6146F1B61850A589E4D9FE8D6690AFFE9F09A4` | strict/frozen |

Approved additions absent at capture:

- `backend/shop/serializers.py`
- `frontend/src/shared/shop/api/shopApi.ts` and `.test.ts`
- `frontend/src/shared/shop/model/shopPresentation.ts` and `.test.ts`
- `frontend/src/features/shop/pages/ShopPage.test.tsx`
- `docs/goals/shop-contract-cache-ownership/PRE_SLICE_BASELINE.md`
- `docs/goals/shop-contract-cache-ownership/EVIDENCE.md`

## Protected-file baseline

| Path | Bytes | SHA-256 |
|---|---:|---|
| `backend/shop/services/store.py` | 2,626 | `DD6C3F2D2BBB330C3328FFBA564FC0CABBAFEC7B6B57BBB1D4E95BD7443323A7` |
| `backend/shop/models.py` | 1,526 | `186CD6ED2B9AC26A00B05604116179E3033F823069256CA6BF3BF79D7A8D8BD4` |
| `backend/shop/access.py` | 1,981 | `CCCD8B30A5BE1F82C8CB3A339FFF2374F2E6ACE58497E4B2B42BE7B3E02839EE` |
| `backend/progress/wallet.py` | 2,594 | `7A75DD3EAF628D9A8098527A9692B8213DE89FD92AF1850D9F368DBB9CD77168` |
| `backend/progress/models.py` | 4,703 | `FB3E993E647AC975685254EED9EA8E18F15E9AD4FDCC0C10882172EA482D53C1` |
| architecture algorithm tests | 76,454 | `949FCA4E22082821D3AA8E4D334749C97262193B13C13E948B7153BB1402064F` |
| `frontend/src/shared/wallet/api/walletApi.ts` | 365 | `51B027245E3B722279647675352BC3A204DFE535304611EFB79C79D3D774A51E` |
| `frontend/src/shared/wallet/hooks/useWallet.ts` | 314 | `F34B5EC1DCCAD9D61AA3FEAB0A5A7ECD3A17C632DFF83EBB8C22352E6E3A46FE` |
| `frontend/src/shared/api/queryKeys.ts` | 1,906 | `541F2705518090BC7545DA4AC089ACA0B34123348CADB84F8E2BC85C32A1DEF1` |
| `frontend/src/shared/player-loadout/playerLoadoutApi.ts` | 630 | `2A4269F007EF3716BC87C62D8D155170F425011E44CE70B3A5BF9FCB3F95BD1E` |
| `frontend/src/shared/navigation/AppNavigation.tsx` | 9,270 | `EE8A063158DECE48705F8F5055D8B545940191EE9BB5244E5CA9B9925F7EFCF7` |
| companion registry | 930 | `1F6449E3CC0514BB27DB9DA439EC22E9953190EFE631DD31D7B72C738F4E84D2` |
| story-world registry | 2,030 | `C8941713AE479021A5597A50561F04D0DCFA666A5ADB6F3D82CA14A5502EBCA5` |
| Shop stylesheet entry | 266 | `6D7F17C1C5F15F0831E73E34BE8566C8258D0F01D28B88A70CF858977A269FC0` |

## Pre-slice behavior and regression baseline

Focused backend command:

```text
python -m pytest backend/shop/tests/test_shop_catalog.py backend/shop/tests/test_shop_integrity.py backend/progress/tests/test_wallet.py -q
20 passed in 34.58s
```

Focused frontend command:

```text
npm test -- --run src/features/shop/api/shopApi.test.ts src/features/shop/utils/shopDisplay.test.ts
2 files passed; 6 tests passed; duration 8.48s
```

Contract checks were current before the slice: generated API currency, frontend operation usage, and generated type adoption all passed.

Observed pre-slice behavior:

- `ShopPurchaseAPIView` calls `.strip()` directly on arbitrary request values, so list/object input can raise before a controlled validation response.
- Runtime story catalog items contain undocumented top-level `world_slug`, `difficulty`, and `prerequisite_story` in addition to `unlocks_story`.
- Generated `unlocks_story` is an open JSON dictionary and `active_companion` is optional.
- The handwritten frontend DTO permits `expert` but omits the backend's valid `intermediate` difficulty.
- `usePlayerLoadout` writes a full runtime response into `queryKeys.shopCatalog` through a raw request typed as a one-field partial object.
- ShopPage discards `{shop,wallet}` after purchase and invalidates both queries, requiring compensating GETs before visible state converges.

The post-slice replay must preserve all 20 existing backend transaction/integrity/wallet cases and the six existing frontend API/display cases after their ownership move.

