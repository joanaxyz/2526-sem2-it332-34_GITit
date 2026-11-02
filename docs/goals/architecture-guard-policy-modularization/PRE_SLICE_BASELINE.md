# Slice 13 Pre-Implementation Preservation Baseline

Captured after the independent PRE verdict APPROVED and before any architecture-guard production extraction.

## Approval and scope

- PRE result: APPROVED ? no remaining P0/P1 findings.
- Approved slice: architecture-guard policy modularization only.
- Product/runtime/generated behavior changes: forbidden.
- The checker and its algorithm test were already heavily dirty; preservation therefore uses symbol/test AST fingerprints in addition to whole-file hashes.

## Mutable-path boundary

Only these paths may change after capture:

- scripts/checks/check_architecture_boundaries.py
- backend/common/tests/test_architecture_guard_algorithms.py
- ARCHITECTURE.md
- scripts/README.md
- approved files under scripts/checks/architecture_guard/
- approved files under backend/common/tests/architecture_guard/
- new docs/goals/architecture-guard-policy-modularization/EVIDENCE.md

All other 194 captured dirty paths are strict status/bytes/SHA-256 preservation entries. The 4 captured mutable entries may change only within the approved plan. The baseline file itself is an approved new self-describing artifact and is hashed during final replay.

## Pre-cutover structure

- Checker: 5367 lines, 109 top-level functions, 205602 bytes, SHA-256 a603466344e4425dc36ce807262f088eefecaa46b2a7845a2e90d1317aca31af.
- Algorithm test: 1877 lines, 43 tests, 216 assert nodes, 83163 bytes, SHA-256 95aa671dd3e69d8ace066f7db89ef73692b222902dcd98023df810689ad84824.
- Relative-to-HEAD dirty target numstat: 1857	0	backend/common/tests/test_architecture_guard_algorithms.py; 4990	64	scripts/checks/check_architecture_boundaries.py.
- Moved-symbol manifest: PRE_CUTOVER_SYMBOL_MANIFEST.json, 118 symbols, checker source SHA bound.
- Test/assertion manifest: PRE_CUTOVER_TEST_MANIFEST.json, 43 tests and 216 assertions, normalized namespace-to-direct-import fingerprinting.

## Pre-cutover behavior

- Direct command from repository root: exit 0; stdout bytes decode as Architecture boundaries look clean.\r\n; stderr empty.
- Compatibility wrapper from frontend: exit 0; stdout bytes decode as Architecture boundaries look clean.\r\n; stderr empty.
- Controlled in-memory failure: exit 1; stdout empty; globals restored in finally; no filesystem mutation.

Controlled failure stderr (logical newlines):

    Architecture boundary violations found:
      fixture/one.py: deterministic first violation
      fixture/two.ts: deterministic second violation

    Rules: shared cannot import features; non-page feature modules cannot import pages; backend runtime code cannot inspect frontend source/assets or form import cycles; feature folders and backend service/common layers must keep the normalized shape; Dashboard summary API contract ownership must stay generated through Home shims; Stats summary API contract ownership must stay generated and one-way; Auth success contracts must stay account-owned, generated, and one-way; gameplay mutation request contracts must stay shared, generated, and one-way; Home Overview workflow ownership must stay one-way; content editor and Home Hub workflow ownership must stay one-way; displaced architecture paths must stay deleted.

- Pre-cutover focused test from backend: python -m pytest common/tests/test_architecture_guard_algorithms.py -q -> 43 passed in 32.48s.
- Golden equivalence case file: {'bytes': 6569, 'sha256': 'a1250a91f120487b0c74044da0a8ed85a72bef2333e403be783991225e9b9048'}.
- Golden ordered violation counts: Catalog 3, Auth 4, Progress 4, Gameplay 15.

## Protected aggregates

Canonical aggregate input is path\0bytes\0sha256, sorted by path over git-visible files; __pycache__ and .pytest_cache are ignored.

- backend_excluding_architecture_guard_tests: 483 files, 15111237 bytes, SHA-256 f47e3a68ab04eff466d728479eca7db9ee3cb42e05d56ed1bbdc52a8709072b0.
- frontend: 1142 files, 414286178 bytes, SHA-256 9ba3258a90d7e83a952d2f7f468caea5c10c0e2d26e9a96bfc4d51a46aa0ab7d.

Exact public wiring hashes:

- .github/workflows/ci.yml: 5492 bytes, SHA-256 750756da5afe4c9223552ed0b5b0b1f491bb93d5ab33d3fd872e397ebc24fa5a.
- scripts/check_architecture_boundaries.py: 318 bytes, SHA-256 e801d3f0e9110b62671a4545262062d88e3ddbff7c8ae103b0fa9c0fbba5bc5b.
- scripts/checks/check_quality_gates.py: 1632 bytes, SHA-256 f92a185e61e1bc4926ca0217dc2b803dfca2ca12eaa43974db9629dd1f39ec2c.
- scripts/checks/check_ci_quality_gates.py: 4549 bytes, SHA-256 0b5880a68b5ed70ae6cdac94081829c665fe5822a2d645d8d8e11a779547b1ac.

Exact generated-contract hashes:

- frontend/src/shared/api/generated/openapi.json: 198553 bytes, SHA-256 eab01f4b773612d90ec421011aa5a00dcabb322db96240d1f1e3dfc2ccb1a26b.
- frontend/src/shared/api/generated/apiTypes.ts: 43930 bytes, SHA-256 658865c60edb02458179fc8f510de2be39b0ed6b1c6e7b6e95416bbed17b806e.

Strict goal/baseline-input hashes:

- docs/goals/architecture-guard-policy-modularization/GOAL.md: 922 bytes, SHA-256 137d94433c250919944266f1f8dc03c3d859f44d9732d3048443065eeea418af.
- docs/goals/architecture-guard-policy-modularization/PLAN.md: 21015 bytes, SHA-256 bdf1991c43a5948c1c4a607382f62ba25f10aaaba87cbde0f96ff91f33dd42db.
- docs/goals/architecture-guard-policy-modularization/PRE_CUTOVER_SYMBOL_MANIFEST.json: 38942 bytes, SHA-256 c463db6d507f960e2e3d3aa713f79c29ab992f317a8fb102bbac1c8c0e083944.
- docs/goals/architecture-guard-policy-modularization/PRE_CUTOVER_TEST_MANIFEST.json: 30397 bytes, SHA-256 a53186207f52bfe6c5c197165140ae3e804212f502a770205ccd9f84b8058b9b.

## Planned path state at capture

- scripts/checks/architecture_guard/__init__.py: absent.
- scripts/checks/architecture_guard/repository.py: absent.
- scripts/checks/architecture_guard/python_analysis.py: absent.
- scripts/checks/architecture_guard/typescript_analysis.py: absent.
- scripts/checks/architecture_guard/contracts/__init__.py: absent.
- scripts/checks/architecture_guard/contracts/catalog.py: absent.
- scripts/checks/architecture_guard/contracts/auth.py: absent.
- scripts/checks/architecture_guard/contracts/progress.py: absent.
- scripts/checks/architecture_guard/contracts/gameplay.py: absent.
- backend/common/tests/architecture_guard/__init__.py: present, 47 bytes, SHA-256 bf07bdab1ba51816eba2980b1e061298a5b416b36b924181e8e3939b92143667.
- backend/common/tests/architecture_guard/policy_equivalence_cases.py: present, 6569 bytes, SHA-256 a1250a91f120487b0c74044da0a8ed85a72bef2333e403be783991225e9b9048.
- backend/common/tests/architecture_guard/test_policy_equivalence.py: absent.
- backend/common/tests/architecture_guard/test_catalog_policy.py: absent.
- backend/common/tests/architecture_guard/test_auth_policy.py: absent.
- backend/common/tests/architecture_guard/test_progress_policy.py: absent.
- backend/common/tests/architecture_guard/test_gameplay_policy.py: absent.
- docs/goals/architecture-guard-policy-modularization/PRE_SLICE_BASELINE.md: absent.
- docs/goals/architecture-guard-policy-modularization/EVIDENCE.md: absent.

## Full dirty manifest

Capture contains 198 dirty paths:  D=7,  M=82, ??=109.

| Class | Status | Bytes | SHA-256 | Path |
|---|---:|---:|---|---|
| strict |  M | 3669 | 4c0992166f52cdab966461eccc3bb5d287c926c6c10dfa33e1df43a68015480e | backend/accounts/serializers.py |
| strict |  M | 8707 | 67c8782706e7a774f4dcd3f09fd5bfb98aecbe137680ef9418f7065a65ce6517 | backend/accounts/views.py |
| strict |  M | 652 | d8ce573abc5adc1937ce8e88738128c9a0b2929cc69262f3987eeab9bbaf47ad | backend/adminconsole/flags.py |
| strict |  M | 1372 | 5d37ae3b8fc3f02e805a7f9ff8b655c268987005f1bcfe3421df961ec6338825 | backend/adminconsole/selectors/__init__.py |
| strict |  M | 2401 | 2ce279231ae6f7aada4f31fa15215f20487448deac737f0a2f8042392e92ad7e | backend/adminconsole/selectors/content.py |
| strict |  M | 2664 | 9a70b23a9eae0e9dffefb9ca442c81970b4299266248f739fc8d686bd6c70685 | backend/adminconsole/selectors/curriculum.py |
| strict |  M | 1497 | 9c8f4789719f218758e701551ab10ff5c8faee0426796d4c8256a379038557db | backend/adminconsole/selectors/users.py |
| strict |  M | 575 | 090b9b09bfa5362b97c07b98f899f3c5ca7e292e374802abbfcbd08df4124179 | backend/adminconsole/services/__init__.py |
| strict |  M | 9055 | 4f5176ce4c42a6914d4585aede064a710ca76585c32a2a40b18edccbb7b292ac | backend/adminconsole/services/curriculum.py |
| strict |  M | 21785 | fba9b549bdac702fdcf24153d835113fc4fab2c1d4f1ca59e14a73ea82f8f536 | backend/adminconsole/tests/test_admin_api.py |
| strict |  D | absent | ABSENT | backend/adminconsole/views.py |
| strict |  D | absent | ABSENT | backend/adventures/serializers.py |
| strict |  M | 11629 | fbf8abb1b34e6267da5f1798911d12143a91ea3319cab005a9ed00380c044a7c | backend/adventures/views.py |
| strict |  M | 13900 | 47749f4758abeea6021da3431e2525113564312e1890186eb6745f21ca4708ed | backend/authoring/services/core.py |
| strict |  M | 14068 | cc0b70899957bd36cce1d49a890a23c23692ea2f5a842c1577334badd2729bec | backend/authoring/tests/test_authoring_api.py |
| strict |  M | 509 | e5580483c3e9223b477641a5c784e10a53bda038f2ba1e148b66d04b6f969f4b | backend/challenges/serializers.py |
| strict |  M | 11330 | f05b63c1ea6e7b497d4d150fcb3469940907c661ffe0c71b252fbac73996c110 | backend/challenges/views.py |
| strict |  M | 6546 | 13e7de38857beb39194140bea54d69a9b60ef21b98972398683369651557a93c | backend/common/openapi.py |
| strict |  M | 2760 | cbd96ac92760beb3321339c74065daabb815fa9f1bd80843cb8e23cb5cf29ac9 | backend/common/serializers.py |
| mutable |  M | 83163 | 95aa671dd3e69d8ace066f7db89ef73692b222902dcd98023df810689ad84824 | backend/common/tests/test_architecture_guard_algorithms.py |
| strict |  M | 6923 | 4210aae6261b36ee0c7bf6ea6422dbace9b88ff431ee0897e5f4900a0aa21ace | backend/common/tests/test_bug_regressions.py |
| strict |  M | 17717 | 6b5a2a5ad0b5b7fcbf51485a92fb1efea0ad3acc8c38d420d068de8d50115935 | backend/curriculum/seed_data/source/adventure_level_specs/v3_advanced_workflows.py |
| strict |  M | 132710 | c4f7f8d31a4d3cd0f6aba50bb1d2e3847bb8aa927d04499f6a4658181ba14c7f | backend/curriculum/seed_data/source/adventure_level_specs/v3_frost_form_drills.py |
| strict |  M | 39224 | b7fd4b22d941cf80cc9b4e8801942c988d9cda4a8d828d475eb7343fb3132f62 | backend/curriculum/seed_data/source/adventure_level_specs/v3_skyline_form_drills.py |
| strict |  M | 8462 | e26ce3b95bc2b570d47f361738f64b86415c2b3acb33c4ca82678e4e1b669332 | backend/curriculum/seed_data/source/challenge_specs/v3_chapter_form_challenges.py |
| strict |  M | 9842 | 077febc5852bfba6b42afeba7da72f187c0642625eaed03f53ea6e224d8785a2 | backend/curriculum/seed_data/source/challenge_specs/v3_story_challenges.py |
| strict |  M | 5780 | 58153fd96108f8c40c02e6521ccb192c2aa5d1b7ea2c84ca5bfa07a068f3e0c8 | backend/curriculum/serializers.py |
| strict |  M | 6322 | 20ed4fe14b2ae2dd5b3d0d348779a10369cb61d88f04c9a33b8e15de16ff3483 | backend/curriculum/tests/test_seed_data_source_layout.py |
| strict |  M | 1939 | cc86c33e7eb970b1ae3a33d94220271493c99f6ad3b8ff513c8b6f580ec2d40e | backend/players/views.py |
| strict |  M | 2921 | 5147607f3754cbe35b0004e2140409652f4acd7d2e0079ac708476098231d7e8 | backend/progress/serializers.py |
| strict |  M | 1222 | b47dfa61f7eb58c5d4d7bb1efb4a862b041631c723fefc3a7dc1d303a1ee648f | backend/progress/views.py |
| strict |  M | 1887 | 21cf4a8b28febbc7f2f04d639aa439790f4a9fe3e202aae051541e79d0f13cb3 | backend/shop/catalog.py |
| strict |  M | 10751 | 8f2e5364f3eee822994c1600a5586de62e009831db5b9b5a3ac3e832f048fbb6 | backend/shop/tests/test_shop_catalog.py |
| strict |  M | 1637 | 7e20e33e019d46b3aec435530b91525af1c7136b676ce16c49da74e8114e1016 | backend/shop/views.py |
| strict |  M | 1427 | 095a6b4ee87f6b228ad36474c8165fe8d3979c65055da78d2788a64863bae16c | frontend/src/app/Protected.tsx |
| strict |  M | 2778 | 2c79a31aecfc896097ad495d1fbf20d2a650a97c108504ef86788b25896a3f30 | frontend/src/features/adventures/api/adventuresApi.ts |
| strict |  M | 4212 | f34597cb56f7f625742cc27e7ceb50d68b967f3b37686a8c1f65c7e0c1fede03 | frontend/src/features/adventures/components/AdventureWorkspaceMain.tsx |
| strict |  M | 3822 | deab77c4949a747b821ee5f601c9a028ba8c8d0b9887a7c28973ea5269b084ca | frontend/src/features/adventures/hooks/useAdventureRun.ts |
| strict |  M | 1370 | 47e63675cb3c3978ab21d5efee021a0f3c56ed4f047d2111a103dbcfe8162990 | frontend/src/features/authoring/hooks/useUnsavedChangesGuard.ts |
| strict |  M | 3938 | 19185c6042d968ca88142c6d6dc42cbc86c679db5fe7dd524f2691a6dbb85052 | frontend/src/features/authoring/pages/ContentEditorPage.tsx |
| strict |  M | 2064 | f0952f279b7decb90efe959a087612e7af7b931606c7918eea4d4e13f294bd07 | frontend/src/features/challenges/api/challengeRunsApi.ts |
| strict |  M | 5196 | c7c6afc7bd7d5f0f825930f4a84519afad9a9c7aed8563d2e642f322bccd0490 | frontend/src/features/challenges/components/ChallengeWorkspaceMain.tsx |
| strict |  M | 6557 | 5910cc567e0c4e20fbefcab058aced2b2d3508753c4a2ef4c5425196b39b36bd | frontend/src/features/challenges/components/ChallengeWorkspacePanels.tsx |
| strict |  M | 7403 | 1b8b6361d69b7d02bbbe10e571e29a800ad32bf6d284d9177ca85d363eb9965e | frontend/src/features/challenges/hooks/useChallengeWorkspaceMutations.ts |
| strict |  M | 3150 | 7555d28cc021504fc1ab375fd0a2f10511038878dc38370a9f16c4cb5649ac14 | frontend/src/features/home/components/HomeHubView.tsx |
| strict |  M | 9699 | 92cba318db3bab6405f9241efc44774fbd5b63f311e80307068f7d820a86ab3c | frontend/src/features/home/components/HomeLoadoutView.tsx |
| strict |  M | 1339 | a861f34c13841d805dc48d745af94651543719d44bacede3cb1f176a108516fa | frontend/src/features/home/components/HomeStatsView.tsx |
| strict |  M | 3412 | 8a2be32fd9db2e7e1af66d68f531442db20458d74d207f5ef9bbf10fb2195ac0 | frontend/src/features/home/preview/fixtures.ts |
| strict |  M | 2279 | 690d9c0b67fc08a67b02216336e4505eb2bef4fe8dab71658ba21c91a28dbac5 | frontend/src/features/home/utils/achievements.test.ts |
| strict |  M | 4566 | 7f7227b65e7c6ac631436459e889e92e0a044a9365c0730ea77d04a154adc3bc | frontend/src/features/home/utils/achievements.ts |
| strict |  D | absent | ABSENT | frontend/src/features/shop/api/shopApi.test.ts |
| strict |  D | absent | ABSENT | frontend/src/features/shop/api/shopApi.ts |
| strict |  M | 4546 | de62d3d9e48df741a8a6e1900221f49654af17f003a2c984b07def8b1110b30a | frontend/src/features/shop/components/CompanionShop.tsx |
| strict |  M | 7479 | 3b27b4b512696671cb9fb37536012a78c5ff10b749f66875925989c59a00f52d | frontend/src/features/shop/components/StoryShop.tsx |
| strict |  M | 6035 | 9d6f511deffc08cada33b541b3061fdd2d82f73d6f39b3a09cb22d57e83be060 | frontend/src/features/shop/pages/ShopPage.tsx |
| strict |  D | absent | ABSENT | frontend/src/features/shop/types.ts |
| strict |  M | 1382 | 2ab638715fcecfd7578edf304c4b85f76418c2024b3b544a3c5f2ad968da980d | frontend/src/features/shop/utils/shopDisplay.test.ts |
| strict |  M | 1955 | c2a57ee9e92bb9f18e8fee5a1fd39b47129f8e16251a4f7fb34e3adee8cf2648 | frontend/src/features/shop/utils/shopDisplay.ts |
| strict |  M | 188 | 03032f98394096617a57834badceb6348be42f54e80bbaa360270040a058dd94 | frontend/src/features/stats/api/statsApi.ts |
| strict |  M | 255 | 1ab6d119fc5e3a31d1b9492da4803776b2220b8689ef963643e596f22edf70bb | frontend/src/features/stats/types.ts |
| strict |  M | 935 | 1c20e9f67925c3ada9076989c2646a6b004b7065aa4568cdb60fc729460617e8 | frontend/src/features/story-map/api/storyMapApi.ts |
| strict |  M | 1494 | 49a0e195772d0617b064e086465c97d34f7581c9b737bcc51a0d0aa64739f0e1 | frontend/src/features/story-map/types.ts |
| strict |  M | 43930 | 658865c60edb02458179fc8f510de2be39b0ed6b1c6e7b6e95416bbed17b806e | frontend/src/shared/api/generated/apiTypes.ts |
| strict |  M | 198553 | eab01f4b773612d90ec421011aa5a00dcabb322db96240d1f1e3dfc2ccb1a26b | frontend/src/shared/api/generated/openapi.json |
| strict |  M | 6361 | 3790425184463db9bc7cb344c4487bfac48364271ef7521a6cfcf2b78b01c00a | frontend/src/shared/api/httpClient.test.ts |
| strict |  M | 5453 | ea0cc2b4bbbbb7ada9e6d3afdaf4564769ce428a6f7f8c239d69838fbd16702c | frontend/src/shared/api/httpClient.ts |
| strict |  M | 2103 | a8b39e86686a0281291ad81b3c058cb9b2a93742a63f5c39dada9ccc1b6d97a8 | frontend/src/shared/auth/authApi.ts |
| strict |  M | 105 | ab1711bf58e58130560d7775ea720b96743b4b02b33132cffed5c0efefe2dad4 | frontend/src/shared/auth/types.ts |
| strict |  M | 2662 | bbc136d1629496e45697393e39aa7d5caf070d7d76d99710de5eb19f63ea0be5 | frontend/src/shared/auth/useAuth.ts |
| strict |  M | 8748 | 601887796bc84a3e19b071eeca93d13e218d87ba24e481a25f3e6e9f32bdb289 | frontend/src/shared/git/simulator/engine.ts |
| strict |  M | 1549 | 4aad2842e42059a769802b60be40397331657d666b4247bdcd60d7b274b3323e | frontend/src/shared/git/simulator/types.ts |
| strict |  M | 10124 | 48eeff3705dc2982017f97ff488238b67d78b5d776c3ee4cd4d243cec5f8d8ac | frontend/src/shared/git/simulator/workspaceFiles.ts |
| strict |  M | 12410 | 36f5ec151c58c200520c248959b592d9a3f7dfadae77f2bb9002459e9431c199 | frontend/src/shared/level/components/ProjectStructurePanel.tsx |
| strict |  M | 13117 | c385103509cecba65a788ce1150b2c344284ca0e107fda9b518a709b6ba33de3 | frontend/src/shared/level/components/WorkspaceEditorOverlay.tsx |
| strict |  M | 3672 | df30e6cd3df9b6bc89487d1bef1a42f4dbbf91072459a9fb38cad2a70776a5ec | frontend/src/shared/level/types.ts |
| strict |  M | 4439 | 44ef06bf97377b2ff924356ff3d84333c87389df2b78935382fc0918066e8ac8 | frontend/src/shared/level/utils/projectFiles.ts |
| strict |  M | 1514 | 4f48a674fcde3270ac2b4125d4a51c46b3be2a7e902863aa905be03d30e7096e | frontend/src/shared/player-loadout/usePlayerLoadout.ts |
| strict |  M | 311 | 696a5219c3e4881173a90c9680ea18f34797214d30b9340e1ab9ac158a810cbc | frontend/src/shared/progress/homeSummaryApi.ts |
| strict |  M | 132 | 0df902817a0c3fbba46670d34a9b151e8e867bd601bde9f663cdca4b311f983b | frontend/src/shared/progress/types.ts |
| strict |  M | 3680 | d773e2234835894cd2b3618b3966da22c7a632750a3b3c1da0ccba9dca4eda8e | frontend/src/styles/features/authoring/editor-shell.css |
| strict |  M | 127 | 23dbb5423b746fcc740932b4392e756a28e0622e90984b8eeeab4dc817b6286e | frontend/src/styles/features/home.css |
| strict |  D | absent | ABSENT | frontend/src/styles/features/home/achievements.css |
| strict |  M | 4277 | 5a5810592ff0f4d0a84107810c43004bc85bb814c6bc1f8a0752318195a82819 | frontend/src/styles/features/home/stats-achievements.css |
| strict |  D | absent | ABSENT | frontend/src/styles/features/home/stats-actions.css |
| strict |  M | 3012 | d1b53888a3c08ef617dabd9995e02c53a2735e5d5f13ffcda802ecbe0420a6fc | frontend/src/styles/features/home/stats-responsive.css |
| strict |  M | 132 | 48574e4043a90dd6a96cdffc8dfda25fdac29410fb2c5997581b428f177230e0 | frontend/src/styles/features/home/stats.css |
| strict |  M | 3441 | efdc33789266466a565663c7e6f823ab346cd306d9e148966b198c998ea7ceb5 | scripts/checks/check_api_type_adoption.py |
| mutable |  M | 205602 | a603466344e4425dc36ce807262f088eefecaa46b2a7845a2e90d1317aca31af | scripts/checks/check_architecture_boundaries.py |
| strict |  M | 2929 | 5df0f9a639beb7566defda9a405e036e98f0e21bb4a116a39ef8dfc7d544f153 | scripts/checks/check_frontend_api_usage.py |
| strict | ?? | 7669 | 079c3ceaacd9dac4880769d82c21650868714c376430e16511d81e53f5a21739 | backend/accounts/tests/test_auth_contract_api.py |
| strict | ?? | 247 | 1736545581cb7dd5e87c17027a5eef9dc9f8c503de4cf5ca05fab776c8370150 | backend/adminconsole/curriculum_options.py |
| strict | ?? | 4364 | bbdcaef2c0f976dd282c85c5b54b8c690d907a2d8b00f429410459aa6c89784c | backend/adminconsole/selectors/analytics.py |
| strict | ?? | 1057 | ebdb8b4ca6c6c5bd4696294c8356b91fc7afcbb2f3549039464533af05bc0051 | backend/adminconsole/selectors/economy.py |
| strict | ?? | 2306 | 20fb3c07991b0b88549b68740fa4649872db8a7ba01b1daefc42700570786516 | backend/adminconsole/selectors/overview.py |
| strict | ?? | 906 | bbe56f5cd7fb61064eae86fc99e4e6230933b466d68bfdf4edd2111517d4a254 | backend/adminconsole/selectors/settings.py |
| strict | ?? | 312 | fd8178093055ff4c545511c45da6d5ac287ccf2e7a7322fda7e1dbc4f307f828 | backend/adminconsole/tests/helpers.py |
| strict | ?? | 11502 | 85276d0ca398ff463e7a0b6cba33c0f02062a39073167ac8088075a8c8977d42 | backend/adminconsole/tests/test_admin_read_api.py |
| strict | ?? | 1101 | a986221d8e08a834fcb7f1cd8aaf163452dbe09229c518c83edb0ea7773c7f16 | backend/adminconsole/views/__init__.py |
| strict | ?? | 2454 | 3c7d709498131f3ca583ae0d3ba70c7c5a3760304e1e5a881c7cfc6c79c0bd1d | backend/adminconsole/views/content.py |
| strict | ?? | 4152 | 875686586bcc731e59dca19717d35547dad4f65d5841cdf39abb92edc023f9f6 | backend/adminconsole/views/curriculum.py |
| strict | ?? | 887 | 5a10e4d519c5c22d9996dbe2e0fe9fe04d78de568f52b69cbac37ab7b366b316 | backend/adminconsole/views/dashboard.py |
| strict | ?? | 2266 | 9399ce1e89a7d51b0ab912c67c936ac2617eae8f76280d06b5f001daef995417 | backend/adminconsole/views/economy.py |
| strict | ?? | 1258 | 2b76979df6e0f438d843638dba730a3b33b90b20048ebd87d77d9e313817e9f5 | backend/adminconsole/views/settings.py |
| strict | ?? | 3037 | a7d97e71fefa25e44968f45e207be08cb8b5ecc67b58d0ac36b0224602ac7c2d | backend/adminconsole/views/users.py |
| strict | ?? | 585 | c6c13d32668ceae980557474d07c049bf5ba4613488a233563c851dc0f40ac6f | backend/common/schemas/openapi.py |
| mutable | ?? | 47 | bf07bdab1ba51816eba2980b1e061298a5b416b36b924181e8e3939b92143667 | backend/common/tests/architecture_guard/__init__.py |
| mutable | ?? | 6569 | a1250a91f120487b0c74044da0a8ed85a72bef2333e403be783991225e9b9048 | backend/common/tests/architecture_guard/policy_equivalence_cases.py |
| strict | ?? | 5755 | 09d8d5df88a5177549830b3c72ed9ba83406927491007f14024df7b859cac036 | backend/common/tests/test_gameplay_mutation_contract.py |
| strict | ?? | 5243 | c3884538af5abc1d41ea7fb933ee599cabc2ad82efbfeb8acc6ecb5d6087e734 | backend/curriculum/seed_data/source/advanced_story_support.py |
| strict | ?? | 3442 | c083cc4def6174bf12a79b8445dcea616c11490092f7b8b00e6d0834c4635cb9 | backend/curriculum/seed_data/source/adventure_level_specs/form_drill_support.py |
| strict | ?? | 9533 | 7e9ba3510ffa065d8c43a8633b6ce1554ccdb1a06347203ae9ba78a18e7ad58f | backend/curriculum/seed_data/source/challenge_specs/advanced_challenge_support.py |
| strict | ?? | 5208 | 62b1f58a81389dae7ee3ff0d62e316002630ca55b7f631db2aa2a8abce9ae2c7 | backend/curriculum/tests/test_catalog_contract_api.py |
| strict | ?? | 6112 | 6c790d25e7a825ad4313c419843dec5ab700ce393f8d3b2bfdcc829891344256 | backend/progress/tests/test_dashboard_summary_api.py |
| strict | ?? | 3898 | e8ef52c4686ac62fd9a65dccc252a65826198a758b35b95b62c36dec26a75ede | backend/progress/tests/test_stats_summary_api.py |
| strict | ?? | 2120 | 06016a0a034aa5da9820e1d4bbcd539681de0a7c4e1df5d9efdafbf318172982 | backend/shop/serializers.py |
| strict | ?? | 9580 | e81f8c015f79f3064b29491d6dd0a76661611e3d3ed100c5a81e8e7142aeb0fc | docs/goals/admin-console-http-read-model-ownership/EVIDENCE.md |
| strict | ?? | 639 | 125c9efd327ab9b48df65a23dfd1ee066cadcf86b1476b04aa11f7129e282bea | docs/goals/admin-console-http-read-model-ownership/GOAL.md |
| strict | ?? | 20650 | 441b86d5f23fcc0f6449386f22fae4132bf6dfed35a0c52f6105ce2e01602b99 | docs/goals/admin-console-http-read-model-ownership/PLAN.md |
| strict | ?? | 922 | 137d94433c250919944266f1f8dc03c3d859f44d9732d3048443065eeea418af | docs/goals/architecture-guard-policy-modularization/GOAL.md |
| strict | ?? | 21015 | bdf1991c43a5948c1c4a607382f62ba25f10aaaba87cbde0f96ff91f33dd42db | docs/goals/architecture-guard-policy-modularization/PLAN.md |
| strict | ?? | 38942 | c463db6d507f960e2e3d3aa713f79c29ab992f317a8fb102bbac1c8c0e083944 | docs/goals/architecture-guard-policy-modularization/PRE_CUTOVER_SYMBOL_MANIFEST.json |
| strict | ?? | 30397 | a53186207f52bfe6c5c197165140ae3e804212f502a770205ccd9f84b8058b9b | docs/goals/architecture-guard-policy-modularization/PRE_CUTOVER_TEST_MANIFEST.json |
| strict | ?? | 12480 | 694f28897af2ad2ed6c117a3a39121505c594921742232a3b1975305a748a89d | docs/goals/auth-browser-state-boundary/EVIDENCE.md |
| strict | ?? | 17791 | a4dd457387a7c4f4e554cf6cd7dd724803bdc16eb0a0d8d0809ad4994e878996 | docs/goals/auth-browser-state-boundary/PLAN.md |
| strict | ?? | 23046 | d0acb24f89aaa59c2cef56d0320d313b6e177ae52289206611d6f4ca095814fa | docs/goals/auth-browser-state-boundary/PRE_SLICE_BASELINE.md |
| strict | ?? | 12030 | ef3599bf16470f2dd6fdc862754bba537eac2fb718e9340a572385ee00490318 | docs/goals/auth-session-success-contract-ownership/EVIDENCE.md |
| strict | ?? | 661 | d9851c6bd062ccacae4f094907d578a7999476c2b1e8825e9e8f076b56fa0c17 | docs/goals/auth-session-success-contract-ownership/GOAL.md |
| strict | ?? | 13407 | 1102c127b3002d6bf83b98154cc9ccc4e7ed234308b57687ad4d3ea80dcbfee2 | docs/goals/auth-session-success-contract-ownership/PLAN.md |
| strict | ?? | 23226 | d017fe76cc9e75a5324feac36829b8449497501287932f5753a35feb75fead6f | docs/goals/auth-session-success-contract-ownership/PRE_SLICE_BASELINE.md |
| strict | ?? | 7815 | 155ff457f6781a33be1d9fa27261679961f92d9858cbb01af6dc6e563b435919 | docs/goals/codebase-maintainability-modernization/EVIDENCE.md |
| strict | ?? | 516 | 044cd7e2bf35dd180f072e28a1362e64ede7c5085f945a214b3a4450b8a004eb | docs/goals/codebase-maintainability-modernization/GOAL.md |
| strict | ?? | 17302 | d2b0085f30167e3065298e06d3e9c504d29248b27d5ea8d0a4dc7c0eb43faec1 | docs/goals/codebase-maintainability-modernization/PLAN.md |
| strict | ?? | 9574 | 1333552aceef649472a65b73fbfd86ae9cb40a0f53551c7e553432a964d05488 | docs/goals/content-editor-workflow-ownership/EVIDENCE.md |
| strict | ?? | 1539 | 62c74c74b40b1a60df54b35fa351b538005a63f379a3e76356a9d225273a8ffc | docs/goals/content-editor-workflow-ownership/GOAL.md |
| strict | ?? | 38613 | 6ede146133a8d59605f422d485087f5ddb57e3870b57dcde1e4541c56682c0d6 | docs/goals/content-editor-workflow-ownership/PLAN.md |
| strict | ?? | 7967 | dbbc37b6b8295f0848dbdd2cf10adc38e6e73f1ca90106e4f255840f124464c9 | docs/goals/content-editor-workflow-ownership/PRE_SLICE_BASELINE.md |
| strict | ?? | 170634 | 996767c8dc6d127c9fab5e19f61341490065ec063c7adfffd6f78b877153c00b | docs/goals/content-editor-workflow-ownership/evidence/content-editor-desktop.png |
| strict | ?? | 89213 | b403715d8c51fef6f45f9b3b58ed2acf4e8747ef6f7da1ef85b974b8085bc29d | docs/goals/content-editor-workflow-ownership/evidence/content-editor-mobile.png |
| strict | ?? | 16013 | 471b59110119cfe38190f3cd6559655acd43c4b616b112b4ec74b9a6f74dc31c | docs/goals/dashboard-summary-contract-ownership/EVIDENCE.md |
| strict | ?? | 861 | f300d132a402d36f26f138a798a3c39f8b00b1c4146d33bcaca6deb132d04f2e | docs/goals/dashboard-summary-contract-ownership/GOAL.md |
| strict | ?? | 18369 | a10efbfe795777c0ad61d9d07eaa02d57d8a463ce23a541f978d6ad2fab11409 | docs/goals/dashboard-summary-contract-ownership/PLAN.md |
| strict | ?? | 20093 | 7acfa18a91facfed49b9d04485a17ade1218efce565cb8f46a25ef88b9902899 | docs/goals/dashboard-summary-contract-ownership/PRE_SLICE_BASELINE.md |
| strict | ?? | 5809 | e905d08062cc0ce831b45497a1d3419773f5b87122ca0db035c8e7b164282e45 | docs/goals/home-hub-profile-workspace-ownership/EVIDENCE.md |
| strict | ?? | 953 | 4bb53eafe381e67d4df2f10c0b5e3ebedcd1e643bdc70944d1dbb2c8f6727b69 | docs/goals/home-hub-profile-workspace-ownership/GOAL.md |
| strict | ?? | 23295 | fe4f75ce0bf20a916d09ff256a791e9736553e7d89035cca0a271f93a3fcf7c2 | docs/goals/home-hub-profile-workspace-ownership/PLAN.md |
| strict | ?? | 14783 | 3da3adb6f5b747f94cde73d7e0226f365b4e7319ddb32d1e686caf4befeacd55 | docs/goals/home-hub-profile-workspace-ownership/PRE_SLICE_BASELINE.md |
| strict | ?? | 640423 | af83ad144ce9f8bb13843c2c42dac17f495ab94e6d82aa9747e596588615b717 | docs/goals/home-hub-profile-workspace-ownership/evidence/home-profile-desktop.png |
| strict | ?? | 254082 | 166b59b24f900dbd082d54bf24d1061bd28fa1cd127caba28337f6948783ffc9 | docs/goals/home-hub-profile-workspace-ownership/evidence/home-profile-mobile.png |
| strict | ?? | 10525 | c809ce2879b9b89cdc3bc3d55af0a37329b6caddcf0650a6816640669e6811d2 | docs/goals/home-overview-ownership/EVIDENCE.md |
| strict | ?? | 1114 | f5a3d201fa7b00910ef7d35160b51baff5275ba78c0ff334b44ed86a20b8b80e | docs/goals/home-overview-ownership/GOAL.md |
| strict | ?? | 20857 | 183b5b1fc10717c022d897112fb367fa113718dd25daca106bcbd049f800d1c5 | docs/goals/home-overview-ownership/PLAN.md |
| strict | ?? | 19080 | b3b42d79f9a05909353a3e2fbc8b52d0c87379bdd71d461003898f156d43f871 | docs/goals/home-overview-ownership/PRE_SLICE_BASELINE.md |
| strict | ?? | 464106 | 6acfd8681fcb7add10e9d0af5d53e5c4d72e66492355339841984c6e6cc94ddf | docs/goals/home-overview-ownership/evidence/home-overview-desktop.png |
| strict | ?? | 142746 | 49c820ae45906a969de142103ea5594700210a57b96888fbb98eb99bbcf7a0ba | docs/goals/home-overview-ownership/evidence/home-overview-mobile.png |
| strict | ?? | 9297 | 31e4ae52706e8292c3f45e5658f521ab1d5e4434aaa125fe7bec7e4378b3b75e | docs/goals/shared-gameplay-mutation-contract-ownership/EVIDENCE.md |
| strict | ?? | 935 | b5921d0621971d517c6c5e919dc59168f1cf1a222f3575d7d04f4fdf46356a0a | docs/goals/shared-gameplay-mutation-contract-ownership/GOAL.md |
| strict | ?? | 17830 | bb5cbdf87eb3938d46c2699295e1ade29ffc6ac9c3d55baec2ae54dcdd29eb34 | docs/goals/shared-gameplay-mutation-contract-ownership/PLAN.md |
| strict | ?? | 31586 | e70656ff8e4865c9e48a8d9bf4f26dd438879ffcdc68d5ca34f64ed337b880ec | docs/goals/shared-gameplay-mutation-contract-ownership/PRE_SLICE_BASELINE.md |
| strict | ?? | 10988 | d36d9dd384a92a970af8e9ebb3a2f89c2880048ed4afa4f44d23950bc21bf664 | docs/goals/shop-contract-cache-ownership/EVIDENCE.md |
| strict | ?? | 552 | 39dee889cbebf1b6e54397f27f6146f1b61850a589e4d9fe8d6690affe9f09a4 | docs/goals/shop-contract-cache-ownership/GOAL.md |
| strict | ?? | 20335 | 3dfed767cc653459a0c0560ab625a815a37aa6d3222960252b16c18f61a5894e | docs/goals/shop-contract-cache-ownership/PLAN.md |
| strict | ?? | 27141 | f320baffdade73ebc8f771e5ed1da68cfd02c2a34f0a304f4fddfee56e71db46 | docs/goals/shop-contract-cache-ownership/PRE_SLICE_BASELINE.md |
| strict | ?? | 11968 | 8ad75af9ecebf0e59550c22dad0c6cf0652566e78929ef1e707a3577d79cd03b | docs/goals/stats-summary-contract-ownership/EVIDENCE.md |
| strict | ?? | 911 | 37436338a76ff11344d8fc3cbdf13e91e8929334a4e08243c6bcd6efc521f8ae | docs/goals/stats-summary-contract-ownership/GOAL.md |
| strict | ?? | 19663 | 2f58f9fa089bff4fc2dec017729699376f6ff851f74c80552027c537184388fa | docs/goals/stats-summary-contract-ownership/PLAN.md |
| strict | ?? | 17662 | 931f206c87e7d3bf6117dff7301be075d5bc64fba2054ac04fd1ffb5062f6908 | docs/goals/stats-summary-contract-ownership/PRE_SLICE_BASELINE.md |
| strict | ?? | 11403 | e1c5aff44ee6867b4c5be89de07b07c40c16f7c22f10725072c96ab6698bfd5b | docs/goals/story-chapter-catalog-contract-ownership/EVIDENCE.md |
| strict | ?? | 1076 | 7d24a8a7d4d5eda4424b7d1f4e9e56cb9d0691702cef94db2d6def5cbef6e94f | docs/goals/story-chapter-catalog-contract-ownership/GOAL.md |
| strict | ?? | 16084 | 16f7c3fc6029e9e90215d1a5dff3e69441168d1fb4525d098276c804ca614e3a | docs/goals/story-chapter-catalog-contract-ownership/PLAN.md |
| strict | ?? | 20472 | cea7c8168e719f5b32c85f0c2d791e2809051d6c0fcc6b5efd641d7a36d8cda6 | docs/goals/story-chapter-catalog-contract-ownership/PRE_SLICE_BASELINE.md |
| strict | ?? | 2581 | 196d0f669570d3f171cf48a024ca3e37c19a4a5158a1002cf13b07bb9774cc36 | frontend/src/app/Protected.test.tsx |
| strict | ?? | 3132 | 59044c5c5aabc34fa418f38b61590d160a2bfd54afd834c90f8d3d63656deefa | frontend/src/features/authoring/components/content-editor/ContentDestinationSection.tsx |
| strict | ?? | 1928 | def4cc1436e1cea182e5a233da61ed460949b57e2f4ef5f648611702db961b8c | frontend/src/features/authoring/components/content-editor/ContentEditorDiagnostics.tsx |
| strict | ?? | 1930 | 0c75288f680741aa0b4798753d88288e7bba435d4eb4fe16551ac3df30976ef5 | frontend/src/features/authoring/components/content-editor/ContentEditorHeader.tsx |
| strict | ?? | 3443 | 95e28176d9bd979b8c5f2813bd8f05d5c5e21f24f35845d9ebe7845cbd5614ca | frontend/src/features/authoring/components/content-editor/ContentMetadataSection.tsx |
| strict | ?? | 1174 | 27fe1fa39bcbd006a85d854530de171f8b867aece73715ca9cfbcf0b7176792c | frontend/src/features/authoring/hooks/contentEditorDraftState.ts |
| strict | ?? | 12327 | f7002971dc8f6c79583b1eaff6ba88de178d849e93462f6f2339b43136e99f64 | frontend/src/features/authoring/hooks/useContentEditorController.ts |
| strict | ?? | 26557 | 7cbca1a3355a240107a0e72fb6f866683a2a5ba1bf6e69b69be30fc34a04ec13 | frontend/src/features/authoring/pages/ContentEditorPage.test.tsx |
| strict | ?? | 11120 | b84b43d250a819ccf68a8951223b490222629265cd6a5b29406975813f1b828f | frontend/src/features/home/components/HomeHubView.test.tsx |
| strict | ?? | 7766 | 0ace15912e4da902cecee3813c4f21189afc6ffc8d84395b53682046ecb398a5 | frontend/src/features/home/components/HomeStatsView.test.tsx |
| strict | ?? | 8793 | 1d150278d111c3c5543e118aa8a2c91356a9daa17eeedecd4dfed7577999c941 | frontend/src/features/home/components/home-hub/HomeCombatShowcase.tsx |
| strict | ?? | 5974 | 1af2565858821226eed9d0203668cbd7b133cf40141790b77e02c4e739ad26d9 | frontend/src/features/home/components/home-hub/HomeProfilePanel.tsx |
| strict | ?? | 1358 | 58355b21119de1b5b177a153a226414b22138f9276c9b954f0d89653b10f14f9 | frontend/src/features/home/components/home-hub/HomeProfileWorkspace.tsx |
| strict | ?? | 3700 | 49658f9515797bbaf82304b60548ae365d180165c87fd58ba9a3d97d1bcdca03 | frontend/src/features/home/components/home-stats/HomeAchievementGallery.tsx |
| strict | ?? | 6428 | 8d1d1bce29fa6908052a96b1159f8cabea4faf5b915ad64ceb62ebf51be2aa3f | frontend/src/features/home/components/home-stats/HomeStatsDashboard.tsx |
| strict | ?? | 4799 | 0a138e734ce7ebf06e5471678e80cc50f126ab3f4fbe5b992b4c8dc3c243fe97 | frontend/src/features/home/components/home-stats/homeStatsModel.test.ts |
| strict | ?? | 3139 | d234ba4a38e2e2bcf886aca81e81e3a1c07efa3a80b9beb8d5f0c1c365ad7ff9 | frontend/src/features/home/components/home-stats/homeStatsModel.ts |
| strict | ?? | 7831 | 7ee83f6817f7d793482523635c7ea6c4de75a351e8928661ce5e975316957255 | frontend/src/features/shop/pages/ShopPage.test.tsx |
| strict | ?? | 7255 | 67bc57c8f5f9c224a9ad9fece25b7b6dc3f0fd985a097aa05fb3d0c046318def | frontend/src/shared/auth/authSessionBoundary.test.ts |
| strict | ?? | 5902 | 80790432d76a92fc9b32a272dd4ba17a1af7356145c40595e80bb7a2cbdb9e86 | frontend/src/shared/auth/authSessionBoundary.ts |
| strict | ?? | 7680 | a616855587ca3e7f926b7648d49d417b7c4ff1d27e8b3b9d7a3c9f4ddd5d4793 | frontend/src/shared/auth/useAuth.test.ts |
| strict | ?? | 1168 | 69619f77ec08ed7d0d796b8a8678e78bf69b0847b243439da3d35287bb265eb4 | frontend/src/shared/level-runtime/runMutationInputs.test.ts |
| strict | ?? | 684 | 13d7579b5716a268e61722c424db0997d4b2ce79f88ade992ee44b93f9f7b72b | frontend/src/shared/level-runtime/runMutationInputs.ts |
| strict | ?? | 417 | 06655b92f12bc9abd081436b188ece0fe1f574c6e4bfa6f1309501b0b8685a09 | frontend/src/shared/level/workspaceFileTypes.ts |
| strict | ?? | 1471 | 60f87aa921e6b2f443e92b9f896aba1ec5ec152aa1f73c77cb51b2de11553e12 | frontend/src/shared/shop/api/shopApi.test.ts |
| strict | ?? | 1133 | 1b5de86aa7d7d31aa6ce3b0602135baeae043d099ea91a9540c022f0235fb0e0 | frontend/src/shared/shop/api/shopApi.ts |
| strict | ?? | 1790 | d7b7ad00ef48b898430b26b9e3c0d3dffc1f4bd9d31d75e173e266e445f24912 | frontend/src/shared/shop/model/shopPresentation.test.ts |
| strict | ?? | 1496 | 6e17b177fdb0dc1ac7420d5ce8a013cf26d16692c468d7bbc3144398785ed94d | frontend/src/shared/shop/model/shopPresentation.ts |

## Replay rule

At closeout, every strict entry must match status, byte length, and SHA-256 exactly; no new path may exist outside the mutable allowlist; protected aggregates and exact wiring/generated hashes must match; moved-symbol and test/assertion manifests must replay; and mutable diffs must be attributable to the approved cutover.
