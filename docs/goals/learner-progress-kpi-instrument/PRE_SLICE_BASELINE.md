# Pre-slice baseline

Captured 2026-10-19 before implementation. Current curriculum owner has already cut over to `arcane-spire`; all new learner copy follows the current workspace. The plan's historical Runebound naming means this same performance contract, not a restored story record. The current metrics service also scopes headline context to the active curriculum. Preserve that scope; do not reintroduce all-story counting.

Implementation stays sequential in the main agent. Board: 1A baseline; 1B parity proof; 2 shared KPI definitions and Admin consumer cutover; 3 learner instrument; 4 Home integration and visual verification; 5 durable boundaries, checks, and reviews. Every task inherits the allowed/forbidden files and evidence from PLAN.md.

## Pre-existing working tree manifest

```json
[
  {
    "status": " M",
    "path": "backend/LEVEL_CHEAT_SHEET.md",
    "bytes": 186736,
    "sha256": "DF2C063EDAEBD4AD02C7CD7D0A3781057383543D195F323FBB7FA4CB98226562"
  },
  {
    "status": " M",
    "path": "backend/adventures/tests/test_adventure_start_access.py",
    "bytes": 3777,
    "sha256": "A273E12C5316E525C3BB980239BBB3A1124916506FAE9FB817E6D4FB867A2D91"
  },
  {
    "status": " M",
    "path": "backend/common/management/commands/seed_all.py",
    "bytes": 2527,
    "sha256": "3B9C5A2509FEC8E3E3B3D9430BE0C74CE3C85DB9E322659CB0A9068FA2900AEA"
  },
  {
    "status": " M",
    "path": "backend/common/models.py",
    "bytes": 2159,
    "sha256": "A5EA601490E2D521D493DF44B57B437A653257EE9A43DDB023A1DEFBAD991314"
  },
  {
    "status": " M",
    "path": "backend/common/tests/test_seed_all_command.py",
    "bytes": 922,
    "sha256": "E643ACB3386F37B3714BBB33A9C72D7B328C0CA14CAB50189E3D145135EBD535"
  },
  {
    "status": " M",
    "path": "backend/conftest.py",
    "bytes": 1785,
    "sha256": "552543470848CCDF5107A5D81A240DA8EAFB9F04E63B6A44B419822773DAB019"
  },
  {
    "status": " M",
    "path": "backend/curriculum/management/commands/seed_curriculum.py",
    "bytes": 2647,
    "sha256": "5FF7B59CB4C830C93AA321564237DA90B30BD7139C56758BEB201D2608124A8A"
  },
  {
    "status": " M",
    "path": "backend/curriculum/management/commands/seed_legacy_modules.py",
    "bytes": 713335,
    "sha256": "B2A67AA906B19C204C40C12827DFC58D8EE2DB4084D0BA7C8E4F4C6E4AD7D958"
  },
  {
    "status": " M",
    "path": "backend/curriculum/seed_data/stories.py",
    "bytes": 2277,
    "sha256": "42F37A1986B77DEEA63CED90D98B227C378C0E73419A0D46DCB6B5F97FE5A0C0"
  },
  {
    "status": " M",
    "path": "backend/curriculum/tests/test_legacy_chapter_books.py",
    "bytes": 5232,
    "sha256": "A423C8B3CB1A66CE50DB1930E443E7EA79A3D7AC8F175796F1FA4DC04110A7AD"
  },
  {
    "status": " M",
    "path": "backend/curriculum/tests/test_module_4_variants.py",
    "bytes": 17920,
    "sha256": "D87798FC1EDD6125A223A305AC52F5A44109444A60783F425C263BF3E7F1F314"
  },
  {
    "status": " M",
    "path": "backend/curriculum/tests/test_story_access.py",
    "bytes": 3142,
    "sha256": "E5B1B7D25930200B998DBA211682011E2B5B4E968DF9FE19102317E2A3B9FAC6"
  },
  {
    "status": " M",
    "path": "backend/docker-entrypoint.sh",
    "bytes": 1071,
    "sha256": "E070D55E178319DA315511A79F593660157AF1D829A1475E35E6DE95B634FA4E"
  },
  {
    "status": " M",
    "path": "backend/drills/tests/test_drill_api.py",
    "bytes": 7164,
    "sha256": "95B9870D79DF6DFDC11FD82B332E6F3EDF4B6B50903D11327E9F94863B73E687"
  },
  {
    "status": " M",
    "path": "backend/progress/objectives.py",
    "bytes": 2134,
    "sha256": "3C8D8CCB2C6DD50132762D783478D912E923C4371A4F75C880635B0D00096504"
  },
  {
    "status": " M",
    "path": "backend/progress/services/metrics.py",
    "bytes": 32031,
    "sha256": "95A73A79EE539B75B1497175EF508F3BF7299BDB4ADAB377168B301084920C9A"
  },
  {
    "status": " M",
    "path": "backend/progress/tests/test_dashboard_summary_api.py",
    "bytes": 6830,
    "sha256": "8CE6E909B634AC628C64CD94EAEB27C1C4BF76C3C8400AD365E5CE995F60F200"
  },
  {
    "status": " M",
    "path": "backend/progress/tests/test_overall_scr.py",
    "bytes": 3880,
    "sha256": "A49D27FF34190B9924524CAA8ED5DE8717AB3B7D6D1DBC2F30F021277B9A1729"
  },
  {
    "status": " M",
    "path": "backend/progress/tests/test_performance_summary_api.py",
    "bytes": 5770,
    "sha256": "DF746ABBE3D873343D1221B567AB84FEAEB5E057F277603F636105E8B2839F98"
  },
  {
    "status": " M",
    "path": "backend/progress/tests/test_stats_player_scope.py",
    "bytes": 9475,
    "sha256": "19B861CAE3814CB7707A25A2C0F9F5CD241CC7F9C513A0B3686F37830C424097"
  },
  {
    "status": " M",
    "path": "backend/progress/tests/test_stats_summary_api.py",
    "bytes": 10432,
    "sha256": "1080215F17126121C46C0A82DD8DFDC50E9AF16C16402D2BC6335064ADF22AF5"
  },
  {
    "status": " M",
    "path": "backend/shop/tests/test_shop_integrity.py",
    "bytes": 3900,
    "sha256": "F3277A3BCE3B033CCC51D4076BF058059CAF0A36AFBDE8CB4C6ED688BC10115E"
  },
  {
    "status": " M",
    "path": "deploy/MODULE4_VARIANT_RESEED.md",
    "bytes": 11739,
    "sha256": "4C13F2E98926CC5C76EE4D3DB0217EA197E4A1C1FEF71C897C1D4E6982070FC5"
  },
  {
    "status": " M",
    "path": "deploy/RENDER.md",
    "bytes": 9520,
    "sha256": "FDB7AB93C618F53E1A4A2B433CC1BE29D93813664FE42AC74FB1EFA410BDB39B"
  },
  {
    "status": " M",
    "path": "frontend/src/app/RequireCompanion.test.tsx",
    "bytes": 2010,
    "sha256": "E02812C4D9BB39EAA1AD15618B8D1DB093AFB65898A24644E58C02A43151813E"
  },
  {
    "status": " M",
    "path": "frontend/src/app/router.test.tsx",
    "bytes": 1668,
    "sha256": "83AB5DFB558F57854B277B277678D8657B84F46ADFEFA4462D3E047395F24A86"
  },
  {
    "status": " M",
    "path": "frontend/src/features/admin/pages/AdminAnalyticsPage.tsx",
    "bytes": 13887,
    "sha256": "FEF1775A5FD9AC53D95C5A79E1134A5D884A0ABB0D9611783114A53D731FB75A"
  },
  {
    "status": " M",
    "path": "frontend/src/features/admin/pages/AdminDashboardPage.test.tsx",
    "bytes": 15422,
    "sha256": "ADC90A7C5D1D7BAD596A1EED284F8CBD02C3719BD3B3FA07BA7A19AA08E84597"
  },
  {
    "status": " M",
    "path": "frontend/src/features/admin/pages/AdminDashboardPage.tsx",
    "bytes": 15488,
    "sha256": "C772A9D58D4295C6644D334910FAF459B62C68E4538CCA291855ECEDE77378FE"
  },
  {
    "status": " M",
    "path": "frontend/src/features/auth/components/AuthEntry.test.tsx",
    "bytes": 3332,
    "sha256": "FE51F77D8E3DE63188843AE52DE4256D3529D568F09FAECBB98B87B3D40BA79E"
  },
  {
    "status": " M",
    "path": "frontend/src/features/dev/utils/drillPlan.json",
    "bytes": 10809,
    "sha256": "EECC0D23406B2B609B383F08B85CC1D408F03F107F2C6E45406EF8E3DC7F3BC9"
  },
  {
    "status": " M",
    "path": "frontend/src/features/home/components/HomeStatsView.test.tsx",
    "bytes": 16194,
    "sha256": "DD16294839CA5D8DB6A6B91BF763FFE4E51FA489AFD183071579DDC6DB96B175"
  },
  {
    "status": " M",
    "path": "frontend/src/features/home/components/home-hub/homeViews.ts",
    "bytes": 2179,
    "sha256": "FB22B360F18874639099B1FAB883E5EA036F030DC9F9CC9AF0EB92A8EE18D2D1"
  },
  {
    "status": " M",
    "path": "frontend/src/features/home/components/home-stats/HomeProgressPanel.tsx",
    "bytes": 6516,
    "sha256": "EF731C6E3C841C1DC601B6590B1D78C65BF35AC4D64B489ACCAB0373647D7504"
  },
  {
    "status": " M",
    "path": "frontend/src/features/home/components/home-stats/HomeResultsPanel.tsx",
    "bytes": 6612,
    "sha256": "482191C2DF71CE0F4E829A959C1033A2B4C1805359F7D7C1F9052CB3DC2A1E37"
  },
  {
    "status": " M",
    "path": "frontend/src/features/home/components/home-stats/HomeSkillsPanel.tsx",
    "bytes": 4426,
    "sha256": "CF6B421FC6BB8DACDB0BB66F18F4946F0B80E0117288454E4A0C8F050395724B"
  },
  {
    "status": " M",
    "path": "frontend/src/features/home/components/home-stats/homeStatsModel.test.ts",
    "bytes": 7040,
    "sha256": "96B326B20A9BE2470E11ECB46CE269708F13991BB07547C4DA76A3631BE95DD6"
  },
  {
    "status": " M",
    "path": "frontend/src/features/home/components/home-stats/homeStatsModel.ts",
    "bytes": 6629,
    "sha256": "2CA84DE81522F60DE7B3698FBFA47D7681BCE5248CB98218C72A327D2B199614"
  },
  {
    "status": " M",
    "path": "frontend/src/features/home/utils/achievementImages.ts",
    "bytes": 2347,
    "sha256": "BE91F976B1E508FFE0D124119C82023E32D8A75441D49B847EFBB07A602F2626"
  },
  {
    "status": " M",
    "path": "frontend/src/features/home/utils/achievements.test.ts",
    "bytes": 3182,
    "sha256": "3291D3CB1B252EAA13B8EA1FBCD6BDD011C676A1D383C039509C013721EA7C52"
  },
  {
    "status": " M",
    "path": "frontend/src/features/home/utils/achievements.ts",
    "bytes": 4771,
    "sha256": "DEB94B10D76F3A0D2D735CB44FA60E807B2BBDFFA645A532215D3D83DE9612A5"
  },
  {
    "status": " M",
    "path": "frontend/src/features/story-map/components/CompanionRequiredOverlay.test.tsx",
    "bytes": 2540,
    "sha256": "9C9A4082CBD66975F2D51BA1A59A47EB7A8CA05346E9FC5802618E3EED7A3928"
  },
  {
    "status": " M",
    "path": "frontend/src/features/story-map/hooks/useLeaveAbandonedRun.test.ts",
    "bytes": 1067,
    "sha256": "545486592502469C4027B3C60AEC9EE92A8F6E8587BFE2F103BF4E8E60C2057F"
  },
  {
    "status": " M",
    "path": "frontend/src/features/story-map/pages/StoryMapPage.tsx",
    "bytes": 15657,
    "sha256": "D9CFD9B5E78983C53EE822C4A3CD9EA9C487AEBDEEC5A58F3EDDE28A8B93D6CE"
  },
  {
    "status": " M",
    "path": "frontend/src/shared/navigation/legacyRoutes.test.ts",
    "bytes": 1788,
    "sha256": "220243B7AABB6B9C46E7252D404D0B573C569DF29655C9318648E70AE52507DA"
  },
  {
    "status": " M",
    "path": "frontend/src/shared/navigation/routes.ts",
    "bytes": 1331,
    "sha256": "287921C3C12BA4B87907E5B7A3A8C603DEA649F18FE45EA37F53B6754ECB3BE9"
  },
  {
    "status": " M",
    "path": "frontend/src/shared/story-worlds/registry.ts",
    "bytes": 2185,
    "sha256": "28DE9E8A92BC3AE492353E04C1C12A5E245282750C87C75F6257FDDB255DA6D0"
  },
  {
    "status": " M",
    "path": "frontend/src/styles/features/home/stats-kpis.css",
    "bytes": 3460,
    "sha256": "4E01E0796445C5C55A0FD2953FD71C1F31345094474CD3B5D79DB7F60AAF04EC"
  },
  {
    "status": " M",
    "path": "frontend/src/styles/features/home/stats-layout.css",
    "bytes": 5035,
    "sha256": "9360AB5400FCE9ACD412A58CF9DA17D43691E58063B4AB3764F01135E324B920"
  },
  {
    "status": " M",
    "path": "frontend/src/styles/features/home/stats-progress.css",
    "bytes": 8997,
    "sha256": "22CC509DC0B697E7ED599CA290D4A56B319AD6A25155D76E7D47ED59306A5534"
  },
  {
    "status": " M",
    "path": "frontend/src/styles/features/home/stats-responsive.css",
    "bytes": 2406,
    "sha256": "14CBA8525216CAD58D614A908882A5DE8108239B0979C05F643DC0EC4C68861F"
  },
  {
    "status": "??",
    "path": "backend/adventures/migrations/0011_alter_adventureleveltierwavevariant_label_and_more.py",
    "bytes": 609,
    "sha256": "E4815FABD8AD96BC7B1C3BAC223F5011022151152CD3DA553F548ABC14A5F1D1"
  },
  {
    "status": "??",
    "path": "backend/challenges/migrations/0005_alter_challengetrialvariant_label.py",
    "bytes": 429,
    "sha256": "E24A719BC8DF2E7722B7EBBCDE770678A2123663748A565C55BD6DFBA05C3D28"
  },
  {
    "status": "??",
    "path": "backend/curriculum/migrations/0004_collapse_story_records_to_arcane_spire.py",
    "bytes": 3080,
    "sha256": "A6D5F77DAC3FC54D1E8127ED660794F8999498BCA1370B922DB85259CD408E95"
  },
  {
    "status": "??",
    "path": "backend/curriculum/tests/test_story_record_cutover.py",
    "bytes": 2216,
    "sha256": "713D19445BE66400AAF03C3004FBE3ECA777CD33747C753C1DB651B73F4F4487"
  },
  {
    "status": "??",
    "path": "docs/goals/arcane-spire-story-record-cutover/EVIDENCE.md",
    "bytes": 4552,
    "sha256": "19F9B66EC07CA050E4F7D38F2CA7A77B68D5891143523DBF05B16D85D6788ECA"
  },
  {
    "status": "??",
    "path": "docs/goals/arcane-spire-story-record-cutover/GOAL.md",
    "bytes": 1312,
    "sha256": "1D2D85A1ED9978C67C1365945AC203E30B254E9961C7DA1AB3008CE0A5BCC39D"
  },
  {
    "status": "??",
    "path": "docs/goals/arcane-spire-story-record-cutover/PLAN.md",
    "bytes": 10547,
    "sha256": "E7184B27154122961C1E95679E8989AF9304F66A4DFD4B104050D5941675C501"
  },
  {
    "status": "??",
    "path": "docs/goals/learner-progress-kpi-instrument/GOAL.md",
    "bytes": 1068,
    "sha256": "2FEDA5E61CB0E81D25915336E89411B18753D346EBAA8C2ABF05462E8EA5B302"
  },
  {
    "status": "??",
    "path": "docs/goals/learner-progress-kpi-instrument/PLAN.md",
    "bytes": 27755,
    "sha256": "FFFD5C323731895E7940E55702FD2F18A2C1161E03A746C3A5446C06985BCDC4"
  }
]
```

## Baseline checks

- Backend performance/scope suite: 15 passed (13.80s).
- Frontend focused suite and architecture baseline started before edits; pending output will be recorded in final evidence.
- Baseline rich/empty browser snapshots confirm the current activity/citadel/three-value record/four-chart module path. Temporary screenshots are 1264x569 at `C:/Users/Joana/AppData/Local/Temp/kpi-progress-before.png` (SHA256 `0FA50DF259F461CC68F6F98B8910FAD486E302ECF64C958DF7C4E922C107F9A0`) and `kpi-progress-before-empty.png` (`0A97BA949EDE5E346CCDE4A3D7C7B93E00DFFE81A9E052F993293CEBBED4928C`). Preview cache seeding bypasses performance requests; request-path evidence will use `/home` after integration.
