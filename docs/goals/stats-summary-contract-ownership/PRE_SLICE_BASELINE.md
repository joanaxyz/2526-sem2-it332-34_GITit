# Pre-Slice-6 Stats Summary Contract Baseline

Captured on 2026-08-10 after `PLAN.md`/`GOAL.md` PRE review returned `ALIGNED` with no findings and before any Slice 6 production, test, generated-contract, or shared-guard implementation edit.

## Preservation rule

Every entry in the 91-entry dirty-worktree manifest belongs to completed Slice 1-5 work or the approved Slice 6 plan package. At the terminal gate, every entry must remain byte-identical unless it is one of the two explicitly additive shared architecture files. `<deleted>` entries must remain absent. The Stats implementation targets were clean at this baseline and may change only as named by `PLAN.md`; all protected files must retain their exact hashes.

## Dirty-worktree manifest

Format: `status | bytes | SHA-256 | path`.

```text
 D | 0 | <deleted> | backend/adminconsole/views.py
 D | 0 | <deleted> | frontend/src/styles/features/home/achievements.css
 D | 0 | <deleted> | frontend/src/styles/features/home/stats-actions.css
 M | 127 | 23DBB5423B746FCC740932B4392E756A28E0622E90984B8EEEAB4DC817B6286E | frontend/src/styles/features/home.css
 M | 132 | 48574E4043A90DD6A96CDFFC8DFDA25FDAC29410FB2C5997581B428F177230E0 | frontend/src/styles/features/home/stats.css
 M | 132710 | C4F7F8D31A4D3CD0F6ABA50BB1D2E3847BB8AA927D04499F6A4658181BA14C7F | backend/curriculum/seed_data/source/adventure_level_specs/v3_frost_form_drills.py
 M | 1339 | A861F34C13841D805DC48D745AF94651543719D44BACEDE3CB1F176A108516FA | frontend/src/features/home/components/HomeStatsView.tsx
 M | 1370 | 47E63675CB3C3978AB21D5EFEE021A0F3C56ED4F047D2111A103DBCFE8162990 | frontend/src/features/authoring/hooks/useUnsavedChangesGuard.ts
 M | 1372 | 5D37AE3B8FC3F02E805A7F9FF8B655C268987005F1BCFE3421DF961EC6338825 | backend/adminconsole/selectors/__init__.py
 M | 13900 | 47749F4758ABEEA6021DA3431E2525113564312E1890186EB6745F21CA4708ED | backend/authoring/services/core.py
 M | 14068 | CC0B70899957BD36CCE1D49A890A23C23692EA2F5A842C1577334BADD2729BEC | backend/authoring/tests/test_authoring_api.py
 M | 1497 | 9C8F4789719F218758E701551AB10FF5C8FAEE0426796D4C8256A379038557DB | backend/adminconsole/selectors/users.py
 M | 17717 | 6B5A2A5AD0B5B7FCBF51485A92FB1EFEA0AD3ACC8C38D420D068DE8D50115935 | backend/curriculum/seed_data/source/adventure_level_specs/v3_advanced_workflows.py
 M | 21785 | FBA9B549BDAC702FDCF24153D835113FC4FAB2C1D4F1CA59E14A73EA82F8F536 | backend/adminconsole/tests/test_admin_api.py
 M | 2279 | 690D9C0B67FC08A67B02216336E4505EB2BEF4FE8DAB71658BA21C91A28DBAC5 | frontend/src/features/home/utils/achievements.test.ts
 M | 2401 | 2CE279231AE6F7AADA4F31FA15215F20487448DEAC737F0A2F8042392E92AD7E | backend/adminconsole/selectors/content.py
 M | 24777 | A1BF369699C63F508F59E5ED63C6ABC83E46774C3742B1EEA15798433A57C981 | backend/common/tests/test_architecture_guard_algorithms.py
 M | 2664 | 9A70B23A9EAE0E9DFFEFB9CA442C81970B4299266248F739FC8D686BD6C70685 | backend/adminconsole/selectors/curriculum.py
 M | 3012 | D1B53888A3C08EF617DABD9995E02C53A2735E5D5F13FFCDA802ECBE0420A6FC | frontend/src/styles/features/home/stats-responsive.css
 M | 3150 | 7555D28CC021504FC1AB375FD0A2F10511038878DC38370A9F16C4CB5649AC14 | frontend/src/features/home/components/HomeHubView.tsx
 M | 3680 | D773E2234835894CD2B3618B3966DA22C7A632750A3B3C1DA0CCBA9DCA4EDA8E | frontend/src/styles/features/authoring/editor-shell.css
 M | 39224 | B7FD4B22D941CF80CC9B4E8801942C988D9CDA4A8D828D475EB7343FB3132F62 | backend/curriculum/seed_data/source/adventure_level_specs/v3_skyline_form_drills.py
 M | 3938 | 19185C6042D968CA88142C6D6DC42CBC86C679DB5FE7DD524F2691A6DBB85052 | frontend/src/features/authoring/pages/ContentEditorPage.tsx
 M | 4277 | 5A5810592FF0F4D0A84107810C43004BC85BB814C6BC1F8A0752318195A82819 | frontend/src/styles/features/home/stats-achievements.css
 M | 4566 | 7F7227B65E7C6AC631436459E889E92E0A044A9365C0730EA77D04A154ADC3BC | frontend/src/features/home/utils/achievements.ts
 M | 575 | 090B9B09BFA5362B97C07B98F899F3C5CA7E292E374802ABBFCBD08DF4124179 | backend/adminconsole/services/__init__.py
 M | 62572 | EA27887CC80F8D8917021B80D504C68750B411402263ADC6E7AF16DC2F20C40E | scripts/checks/check_architecture_boundaries.py
 M | 6322 | 20ED4FE14B2AE2DD5B3D0D348779A10369CB61D88F04C9A33B8E15DE16FF3483 | backend/curriculum/tests/test_seed_data_source_layout.py
 M | 652 | D8CE573ABC5ADC1937CE8E88738128C9A0B2929CC69262F3987EEAB9BBAF47AD | backend/adminconsole/flags.py
 M | 8462 | E26CE3B95BC2B570D47F361738F64B86415C2B3ACB33C4CA82678E4E1B669332 | backend/curriculum/seed_data/source/challenge_specs/v3_chapter_form_challenges.py
 M | 9055 | 4F5176CE4C42A6914D4585AEDE064A710CA76585C32A2A40B18EDCCBB7B292AC | backend/adminconsole/services/curriculum.py
 M | 9842 | 077FEBC5852BFBA6B42AFEBA7DA72F187C0642625EAED03F53EA6E224D8785A2 | backend/curriculum/seed_data/source/challenge_specs/v3_story_challenges.py
?? | 10525 | C809CE2879B9B89CDC3BC3D55AF0A37329B6CADDCF0650A6816640669E6811D2 | docs/goals/home-overview-ownership/EVIDENCE.md
?? | 1057 | EBDB8B4CA6C6C5BD4696294C8356B91FC7AFCBB2F3549039464533AF05BC0051 | backend/adminconsole/selectors/economy.py
?? | 1101 | A986221D8E08A834FCB7F1CD8AAF163452DBE09229C518C83EDB0EA7773C7F16 | backend/adminconsole/views/__init__.py
?? | 11120 | B84B43D250A819CCF68A8951223B490222629265CD6A5B29406975813F1B828F | frontend/src/features/home/components/HomeHubView.test.tsx
?? | 1114 | F5A3D201FA7B00910EF7D35160B51BAFF5275BA78C0FF334B44ED86A20B8B80E | docs/goals/home-overview-ownership/GOAL.md
?? | 11502 | 85276D0CA398FF463E7A0B6CBA33C0F02062A39073167AC8088075A8C8977D42 | backend/adminconsole/tests/test_admin_read_api.py
?? | 1174 | 27FE1FA39BCBD006A85D854530DE171F8B867AECE73715CA9CFBCF0B7176792C | frontend/src/features/authoring/hooks/contentEditorDraftState.ts
?? | 12327 | F7002971DC8F6C79583B1EAFF6BA88DE178D849E93462F6F2339B43136E99F64 | frontend/src/features/authoring/hooks/useContentEditorController.ts
?? | 1258 | 2B76979DF6E0F438D843638DBA730A3B33B90B20048EBD87D77D9E313817E9F5 | backend/adminconsole/views/settings.py
?? | 1358 | 58355B21119DE1B5B177A153A226414B22138F9276C9B954F0D89653B10F14F9 | frontend/src/features/home/components/home-hub/HomeProfileWorkspace.tsx
?? | 142746 | 49C820AE45906A969DE142103EA5594700210A57B96888FBB98EB99BBCF7A0BA | docs/goals/home-overview-ownership/evidence/home-overview-mobile.png
?? | 14783 | 3DA3ADB6F5B747F94CDE73D7E0226F365B4E7319DDB32D1E686CAF4BEFEACD55 | docs/goals/home-hub-profile-workspace-ownership/PRE_SLICE_BASELINE.md
?? | 1539 | 62C74C74B40B1A60DF54B35FA351B538005A63F379A3E76356A9D225273A8FFC | docs/goals/content-editor-workflow-ownership/GOAL.md
?? | 170634 | 996767C8DC6D127C9FAB5E19F61341490065EC063C7ADFFFD6F78B877153C00B | docs/goals/content-editor-workflow-ownership/evidence/content-editor-desktop.png
?? | 17302 | D2B0085F30167E3065298E06D3E9C504D29248B27D5EA8D0A4DC7C0EB43FAEC1 | docs/goals/codebase-maintainability-modernization/PLAN.md
?? | 19042 | 20D9791A6B76F3A158317A654C4E19EB97CD046090B4DB46F3BCA80A4C577EB0 | docs/goals/stats-summary-contract-ownership/PLAN.md
?? | 19080 | B3B42D79F9A05909353A3E2FBC8B52D0C87379BDD71D461003898F156D43F871 | docs/goals/home-overview-ownership/PRE_SLICE_BASELINE.md
?? | 1928 | DEF4CC1436E1CEA182E5A233DA61ED460949B57E2F4EF5F648611702DB961B8C | frontend/src/features/authoring/components/content-editor/ContentEditorDiagnostics.tsx
?? | 1930 | 0C75288F680741AA0B4798753D88288E7BBA435D4EB4FE16551AC3DF30976EF5 | frontend/src/features/authoring/components/content-editor/ContentEditorHeader.tsx
?? | 20650 | 441B86D5F23FCC0F6449386F22FAE4132BF6DFED35A0C52F6105CE2E01602B99 | docs/goals/admin-console-http-read-model-ownership/PLAN.md
?? | 20857 | 183B5B1FC10717C022D897112FB367FA113718DD25DACA106BCBD049F800D1C5 | docs/goals/home-overview-ownership/PLAN.md
?? | 2266 | 9399CE1E89A7D51B0AB912C67C936AC2617EAE8F76280D06B5F001DAEF995417 | backend/adminconsole/views/economy.py
?? | 2306 | 20FB3C07991B0B88549B68740FA4649872DB8A7BA01B1DAEFC42700570786516 | backend/adminconsole/selectors/overview.py
?? | 23295 | FE4F75CE0BF20A916D09FF256A791E9736553E7D89035CCA0A271F93A3FCF7C2 | docs/goals/home-hub-profile-workspace-ownership/PLAN.md
?? | 2454 | 3C7D709498131F3CA583AE0D3BA70C7C5A3760304E1E5A881C7CFC6C79C0BD1D | backend/adminconsole/views/content.py
?? | 247 | 1736545581CB7DD5E87C17027A5EEF9DC9F8C503DE4CF5CA05FAB776C8370150 | backend/adminconsole/curriculum_options.py
?? | 254082 | 166B59B24F900DBD082D54BF24D1061BD28FA1CD127CABA28337F6948783FFC9 | docs/goals/home-hub-profile-workspace-ownership/evidence/home-profile-mobile.png
?? | 26557 | 7CBCA1A3355A240107A0E72FB6F866683A2A5BA1BF6E69B69BE30FC34A04EC13 | frontend/src/features/authoring/pages/ContentEditorPage.test.tsx
?? | 3037 | A7D97E71FEFA25E44968F45E207BE08CB8B5ECC67B58D0AC36B0224602AC7C2D | backend/adminconsole/views/users.py
?? | 312 | FD8178093055FF4C545511C45DA6D5AC287CCF2E7A7322FDA7E1DBC4F307F828 | backend/adminconsole/tests/helpers.py
?? | 3132 | 59044C5C5AABC34FA418F38B61590D160A2BFD54AFD834C90F8D3D63656DEEFA | frontend/src/features/authoring/components/content-editor/ContentDestinationSection.tsx
?? | 3139 | D234BA4A38E2E2BCF886ACA81E81E3A1C07EFA3A80B9BEB8D5F0C1C365AD7FF9 | frontend/src/features/home/components/home-stats/homeStatsModel.ts
?? | 3442 | C083CC4DEF6174BF12A79B8445DCEA616C11490092F7B8B00E6D0834C4635CB9 | backend/curriculum/seed_data/source/adventure_level_specs/form_drill_support.py
?? | 3443 | 95E28176D9BD979B8C5F2813BD8F05D5C5E21F24F35845D9EBE7845CBD5614CA | frontend/src/features/authoring/components/content-editor/ContentMetadataSection.tsx
?? | 3700 | 49658F9515797BBAF82304B60548AE365D180165C87FD58BA9A3D97D1BCDCA03 | frontend/src/features/home/components/home-stats/HomeAchievementGallery.tsx
?? | 38613 | 6EDE146133A8D59605F422D485087F5DDB57E3870B57DCDE1E4541C56682C0D6 | docs/goals/content-editor-workflow-ownership/PLAN.md
?? | 4152 | 875686586BCC731E59DCA19717D35547DAD4F65D5841CDF39ABB92EDC023F9F6 | backend/adminconsole/views/curriculum.py
?? | 4364 | BBDCAEF2C0F976DD282C85C5B54B8C690D907A2D8B00F429410459AA6C89784C | backend/adminconsole/selectors/analytics.py
?? | 464106 | 6ACFD8681FCB7ADD10E9D0AF5D53E5C4D72E66492355339841984C6E6CC94DDF | docs/goals/home-overview-ownership/evidence/home-overview-desktop.png
?? | 4690 | C1A7CBE93763534330AEA7256D5F4BBAE97A09B229BB5547FCD07C50BB26237E | frontend/src/features/home/components/home-stats/homeStatsModel.test.ts
?? | 516 | 044CD7E2BF35DD180F072E28A1362E64EDE7C5085F945A214B3A4450B8A004EB | docs/goals/codebase-maintainability-modernization/GOAL.md
?? | 5243 | C3884538AF5ABC1D41EA7FB933EE599CABC2AD82EFBFEB8ACC6ECB5D6087E734 | backend/curriculum/seed_data/source/advanced_story_support.py
?? | 5809 | E905D08062CC0CE831B45497A1D3419773F5B87122CA0DB035C8E7B164282E45 | docs/goals/home-hub-profile-workspace-ownership/EVIDENCE.md
?? | 5974 | 1AF2565858821226EED9D0203668CBD7B133CF40141790B77E02C4E739AD26D9 | frontend/src/features/home/components/home-hub/HomeProfilePanel.tsx
?? | 639 | 125C9EFD327AB9B48DF65A23DFD1EE066CADCF86B1476B04AA11F7129E282BEA | docs/goals/admin-console-http-read-model-ownership/GOAL.md
?? | 640423 | AF83AD144CE9F8BB13843C2C42DAC17F495AB94E6D82AA9747E596588615B717 | docs/goals/home-hub-profile-workspace-ownership/evidence/home-profile-desktop.png
?? | 6428 | 8D1D1BCE29FA6908052A96B1159F8CABEA4FAF5B915AD64CEB62EBF51BE2AA3F | frontend/src/features/home/components/home-stats/HomeStatsDashboard.tsx
?? | 7766 | 0ACE15912E4DA902CECEE3813C4F21189AFC6FFC8D84395B53682046ECB398A5 | frontend/src/features/home/components/HomeStatsView.test.tsx
?? | 7815 | 155FF457F6781A33BE1D9FA27261679961F92D9858CBB01AF6DC6E563B435919 | docs/goals/codebase-maintainability-modernization/EVIDENCE.md
?? | 7967 | DBBC37B6B8295F0848DBDD2CF10ADC38E6E73F1CA90106E4F255840F124464C9 | docs/goals/content-editor-workflow-ownership/PRE_SLICE_BASELINE.md
?? | 8793 | 1D150278D111C3C5543E118AA8A2C91356A9DAA17EEEDECD4DFED7577999C941 | frontend/src/features/home/components/home-hub/HomeCombatShowcase.tsx
?? | 887 | 5A10E4D519C5C22D9996DBE2E0FE9FE04D78DE568F52B69CBAC37AB7B366B316 | backend/adminconsole/views/dashboard.py
?? | 89213 | B403715D8C51FEF6F45F9B3B58ED2ACF4E8747EF6F7DA1EF85B974B8085BC29D | docs/goals/content-editor-workflow-ownership/evidence/content-editor-mobile.png
?? | 906 | BBE56F5CD7FB61064EAE86FC99E4E6230933B466D68BFDF4EDD2111517D4A254 | backend/adminconsole/selectors/settings.py
?? | 911 | 37436338A76FF11344D8FC3CBDF13E91E8929334A4E08243C6BCD6EFC521F8AE | docs/goals/stats-summary-contract-ownership/GOAL.md
?? | 953 | 4BB53EAFE381E67D4DF2F10C0B5E3EBEDCD1E643BDC70944D1DBB2C8F6727B69 | docs/goals/home-hub-profile-workspace-ownership/GOAL.md
?? | 9533 | 7E9BA3510FFA065D8C43A8633B6CE1554CCDB1A06347203AE9BA78A18E7AD58F | backend/curriculum/seed_data/source/challenge_specs/advanced_challenge_support.py
?? | 9574 | 1333552ACEEF649472A65B73FBFD86AE9CB40A0F53551C7E553432A964D05488 | docs/goals/content-editor-workflow-ownership/EVIDENCE.md
?? | 9580 | E81F8C015F79F3064B29491D6DD0A76661611E3D3ED100C5A81E8E7142AEB0FC | docs/goals/admin-console-http-read-model-ownership/EVIDENCE.md
```

Manifest entries: 91. Terminal preservation target: 89 of 89 non-architecture entries byte-identical; the other two shared architecture files may change additively only.

## Shared additive architecture baseline

| Path | Lines | Full-file SHA-256 | Existing diff SHA-1 | Existing numstat |
|---|---:|---|---|---|
| `scripts/checks/check_architecture_boundaries.py` | 1,704 | `EA27887CC80F8D8917021B80D504C68750B411402263ADC6E7AF16DC2F20C40E` | `528346d6ba5dd6119fa78528f8d0b88d4b9ea554` | `1265 + / 2 -` |
| `backend/common/tests/test_architecture_guard_algorithms.py` | 581 | `A1BF369699C63F508F59E5ED63C6ABC83E46774C3742B1EEA15798433A57C981` | `250fa561fe97e56219ba4da688af2d9d6929a872` | `561 + / 0 -` |

All earlier checker functions, messages, `main` calls, and tests must remain. Slice 6 additions may not delete or weaken prior behavior.

## Approved target and protected baseline

| Path | Lines | Bytes | SHA-256 | Role |
|---|---:|---:|---|---|
| `backend/common/openapi.py` | 229 | 9,209 | `471B92587307654211B4F56AC44F08DAC4D36C60C45E1A8E8C4CC545E57F4603` | allowed exact displaced removals |
| `backend/progress/serializers.py` | 9 | 299 | `B697FC3CE38388FDEBDCC1F12A4072F7C014D5B51856689088A02D633F999AF6` | allowed owner replacement |
| `backend/progress/views.py` | 33 | 1,194 | `2249553313205008F5D5A6D9B4B9885FDA5935039916D61A2BC8214D5026783F` | allowed import-only cutover |
| `frontend/src/features/stats/types.ts` | 41 | 728 | `0BD8857D2C866BA155987CC4B5A051DD46E83C657C6E83D7A19BE7AA9C623B92` | allowed derived-type cutover |
| `frontend/src/features/stats/api/statsApi.ts` | 11 | 444 | `187381E1622DE8FF59C3B8F2543635447F7B468D32C09DDC6203C5AD06E0BDB2` | allowed override deletion |
| `frontend/src/shared/api/generated/openapi.json` | 5,428 | 189,446 | `EBC5DC3AFFD1BAB839649382429E7AA159DB031F172E1E3331C4103494A19BA5` | generator-only target |
| `frontend/src/shared/api/generated/apiTypes.ts` | 487 | 42,535 | `A817CA33F74364D69A536A67361E19FB7E623A4C19BA23F8EC3ABADD33375FE6` | generator-only target |
| `backend/progress/services/metrics.py` | 442 | 18,930 | `BC10D8BFADC22F33AB0A4DE0D1692F92C49E3628F94AD2217EBD0FA843EEA38F` | protected executable truth |
| `scripts/api/api_contract.py` | 464 | 19,497 | `FCF41D695D712401E5F98BC347995E89079E3DDCF132DAC6C29FBD1618B14D23` | protected generator |
| `frontend/src/shared/api/httpClient.ts` | 170 | 5,433 | `41B94C89B7E713598002AD1D0FC627CA63CC13171338D27802A12F4DA59DF8C5` | protected transport |

The shared `WalletSummaryResponseSerializer`, Shop response family, routes, Home files/fixtures, and every other file are protected by the plan and/or dirty manifest.

## Authenticated runtime baseline

An isolated in-memory database was migrated, a real user was created, DRF `APIClient` force-authenticated that user, and the real `/api/progress/stats/` URL/view/service path returned:

```json
{
  "status": 200,
  "top_level_keys": ["activity_trend", "headline", "skill_profile"],
  "activity_points": 14,
  "activity_point_keys": ["commands_run", "date", "levels_completed"],
  "headline_keys": [
    "accuracy",
    "boss_floors",
    "comebacks",
    "commands_run",
    "day_streak",
    "finish_rate",
    "gitcoins",
    "levels_completed",
    "longest_streak",
    "perfect_clears"
  ],
  "finish_rate": {"denominator": 0, "numerator": 0, "value": null},
  "legacy_activity_present": false,
  "legacy_headlines_present": false,
  "legacy_totals_present": false
}
```

This is the executable contract to preserve.

## Declared/generated mismatch baseline

`StatsSummaryResponseSerializer`, committed OpenAPI, and generated TypeScript advertise:

- properties: `skill_profile`, `activity`, `headlines`, optional `totals`;
- required: `skill_profile`, `activity`, `headlines`;
- generated TypeScript: `{ activity: Array<Record>; headlines: Record; skill_profile: Array<Record>; totals?: Record }`.

`frontend/src/features/stats/types.ts` independently declares the actual response, and `StatsSummaryResult = ApiSchemas['StatsSummaryResponse'] & StatsSummary` masks the disagreement.

## Passing-but-insufficient gate baseline

- API contract current check: passed.
- Frontend API usage check: passed.
- API type-adoption check: passed.
- Architecture boundary checker: passed.
- CSS architecture checker: passed.
- Focused Home Stats/model/achievement lane: 3 files / 13 tests passed.

These gates prove internal schema/generated consistency and existing UI behavior, but none currently proves runtime response-to-schema conformity. Slice 6 must close that evidence and enforcement gap.
