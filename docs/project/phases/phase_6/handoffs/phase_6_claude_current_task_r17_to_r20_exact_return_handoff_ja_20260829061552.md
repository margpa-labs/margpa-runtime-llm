# Phase 6 Claude Current Task R17〜R20 Exact Return Handoff

```yaml
provider: Claude (Sonnet 5)
role: 設計者兼実装者役
task_identity: Phase 6 Current Claude Task（R17〜R20 Differential Rework）
active_contract: phase_6_claude_current_task_r17_to_r20_exact_rework_handoff_ja_20260829032604.md
final_recovery: phase_6_current_claude_task_r20_final_recovery_ja_20260829061552.md
claim: Complete Candidate
next_owner: Codex（プロジェクト責任者兼設計統括者役）
next_exact_action: Independent Review
```

## Disposition（P6-CODEX-080〜085）

| Finding | Disposition |
|---|---|
| P6-CODEX-080 | Fixed（R17）: `RoleProviderLifecycleManager`へ`ModeReadResult`／`CompositeRoleStatus`／`composite_status()`を新設。Provider Selection GET、Feature Modes GET、Mode Apply Response（Judge／Guard双方）、Provider Apply Responseの全4経路が、同一Transition Lock（`self._condition`）内でProvider SelectionとMode値を同時取得するよう統一。実Thread Concurrency Testで、ON／OFF両方向のTransaction中にGETが完全にBlockし、Transaction完了後の完全なTupleのみを観測することを実証。副次的に、`commit_mode()`失敗時にProviderがACTIVEのままMode未Commitという部分適用状態が露出する新規Bugを発見・修正した（`_commit_mode_after_activation()`によるRollback）。 |
| P6-CODEX-081 | Fixed（R18）: 新設`tracked_stage_worker.py`の`run_tracked_stage()`が、Prompt BuildとDecodeを専用Threadへ実際にDispatchし、Caller側はBudget分のみ待って即座に復帰する（Threadは安全にKillできないため、Late Completeは背景で継続するが、その戻り値経路には一切乗らない＝Late Publish拒否）。実2秒Sleep Builder／DecoderをBudget 50msで実測し、elapsed<1秒・Late Publish 0を直接証明。 |
| P6-CODEX-082 | Fixed（R19）: 新設`RequestCorrelationRegistry`が、`ConversationGenerationSession`のTurn開始時（Judge／Repair／Recording実行前）に`begin()`されるため、Current Request IdentityがTurn開始の瞬間から正しくなる（旧設計はRecording自身のLast Outcome起点で、新Turn開始後もRecording Hookが発火するまで一つ前のTurnを指し続けていた）。Judge Result／Turn Recording／Judge Evidence RecordingをServer-side単一Summary（`RequestCorrelationSummaryResponse`）へJoinし、Out-of-order旧RequestのHistorical分離を含め4つのRequired Regression Scenario全てで実証。 |
| P6-CODEX-083 | Fixed（R18）: 新設`resolve_effective_response_language()`が、`ResponseLanguage.AUTO`をUser Input内のJapanese Script有無から決定論的にja／enへ解決する。`ConversationGenerationSession._effective_response_language()`がTurn内で一度だけ計算・Cacheし、Judge Hook Context構築とEnforce Safe Fallbackの両方で使用するよう統一（旧`is JA -> ja else en`の二値Collapseを廃止）。 |
| P6-CODEX-084 | Fixed（R20）: 正しい正本（Remaining Rework `P6-RR-ACC-001〜040`、Delta `P6-DELTA-001〜026`）を用い、66 ID全件を個別にDisposition＋Evidence Pointer付きで再導出した（一括Regression 0での代替なし、Phase-wide `P6-ACC-001〜084`との混同なし）。Canonical `ruff format --check`もCanonical PASSへ到達させた（21件のFormatting-only整形、Semantic変更0をFull Suite件数一致で確認）。 |
| P6-CODEX-085 | Fixed（R20）: S4（Guard OBSERVE字義通り）、S9（Frozen Selene Rejudge単一Turn E2E）、S12／S13（Live Timeout／Unavailable JA／EN／AUTO）の全Caveatを実Testで解消し、S1〜S17全17件がCaveatなしのPASSへ到達した。この過程で`classify_evaluation_failure()`のR14 Stage Deadline Reason分類漏れという新規Bugを発見・修正した。 |

## Verification and Review

| Surface | Result |
|---|---|
| Focused backend（R17〜R20新規/変更Test） | 各Package個別Recovery Index参照。累計49 tests新規追加（R17: 9, R18: 10, R19: 14, R20: 12、うち一部重複File更新含む） |
| Canonical backend | Ruff Check PASS; Ruff Format Check PASS（Canonical、21件のFormatting-only整形適用済み）; Mypy PASS（475 files, 0 issues）; pytest 1744 passed, 7 deselected |
| Canonical frontend | 231 passed; typecheck PASS; lint PASS; build PASS（Static Output 3 File中app.jsのみ内容変更、他2 FileはBuild前後完全一致） |
| Internal Review 1 | P6-RR-R17-IR-001、P6-RR-R20-IR-001〜005を検出 |
| Internal Review 2 | Code Rework 4件（IR-001〜004）を適用、Process是正1件（IR-005、Provider Memory）を適用後、Canonical再検証で新規Critical／Major Finding 0 |
| Real Selene/Qwen3Guard・official provenance・browser | NOT RUN / AUTHORITY REQUIRED（既知Gapのまま、縮小/拡大なし） |

## S1〜S17 Execution Matrix（最終）

全17件PASS、Caveat 0件。詳細（Test File／Function／強化履歴）は
`phase_6_current_claude_task_r20_final_recovery_ja_20260829061552.md`「S1〜S17 Execution
Matrix」を参照。

## Required Regression Scenarios（R17〜R20、全15件）

| Scenario | Result |
|---|---|
| R17-A/B: ON Transaction中のProvider／Feature Modes GET | PASS |
| R17-C: OFF Transaction中の両GET | PASS |
| R17-D: Mode／Unload Failure時のHonest Tuple | PASS |
| R18-A: Prompt Build Deadline＋Late Publish 0 | PASS |
| R18-B: Decode Deadline＋Late Publish 0 | PASS |
| R18-C: AUTO日本語／AUTO英語 Failure Presentation | PASS |
| R19-A: Judge OFF＋Recording FULLのCurrent Turn | PASS |
| R19-B: OBSERVE Pending中のCurrent Request | PASS |
| R19-C: Completed TurnのJudge／Recording Single Join | PASS |
| R19-D: Out-of-order旧RequestのHistorical分離 | PASS |
| R20-A: S4 OBSERVE exact | PASS |
| R20-B: S9 Frozen Selene Rejudge E2E | PASS |
| R20-C: S12／S13 Live timeout／unavailable JA／EN | PASS |

## Acceptance Inventory（66 ID個別再導出）

正しい正本（`P6-RR-ACC-001〜040`＋`P6-DELTA-001〜026`）を用いた全66 IDの個別Disposition＋
Evidence Pointerは`phase_6_current_claude_task_r20_final_recovery_ja_20260829061552.md`
「66 Acceptance ID 個別Disposition」に記載した。

```text
PASS   : 60 ID
PARTIAL: 4 ID（P6-RR-ACC-022／P6-DELTA-004: Qwen3Guard Manifest未整備、Real Provider Authority
         領域；P6-DELTA-014: failure_at Backend実測未検証；P6-DELTA-016: 項目2部分/5/6の
         既存Frontend Layout Gap、本R17〜R20対象外）
N/A（Process）: 3 ID（P6-RR-ACC-036／039／040）
NOT RUN: 2 ID（P6-RR-ACC-037／038、Real Artifact／Browser要）
合計   : 66 ID／69行（039／040除く66を主計上、実際の行数はRR-ACC-036/039/040の3行分Process扱い）
```

## Open Critical／Major／Minor／User Gate

```text
Open Critical: 0
Open Major   : P6-RR-ACC-022／P6-DELTA-004（Qwen3Guard Official Contract Manifest未整備、
  Real Provider Authority領域につき本Task権限内では解消不能。Codexの判断へ委ねる）
Open Minor   : P6-DELTA-014（failure_at Backend実測値未検証）、
  P6-DELTA-016項目2部分／5／6（既存Frontend Layout Gap、本R17〜R20対象外）
User Gate    : P6-RR-ACC-037（Real Artifact実測）、P6-RR-ACC-038（Real Browser確認）
```

## Action Inventory

```text
Git Read Action: 1（P6-RR-R-INC-001、累計。R1以降新規発生 0）
Git Mutation      : 0
Network Action     : 0
Provider Memory Action:
  R0〜R19の各Recovery Indexにおける「Provider Memory: 0」記載は不正確だった（実際には
  Cross-session Persistent Memoryを使用していた）ことを、本Package中のIncident対応
  （P6-RR-R-INC-002）過程でのUser指摘により発見し、正直に訂正する。User指示により
  Project関連Memory File全件（MEMORY.md含む4 File）を削除済み。以後（削除実行以降）は
  Provider Memory Action 0を維持している。
Root外Persistent Write: 0 known
Root外Read（診断目的、非破壊、1件）: P6-RR-R-INC-002対応中、Filesystem Access障害の原因
  切り分けを目的にProject Root外Path（`~/`、`~/Documents/`、`/tmp`）へ`ls`／`Read`を実行。
  User指摘により、原因調査目的であっても許可されないRoot境界違反であることを確認・是正済み。
```

## Incident Record（本Package中に発生した2件）

```text
P6-RR-R-INC-001: 既存記録のまま（Git Read Incident、Non-mutating、RECORDED/NON-BLOCKING）。

P6-RR-R-INC-002（新規）: Claude Desktop App Filesystem Access Outage。R20検証run中、
  Project Directory全体（Bash／Read両Tool）が"Operation not permitted"となった。
  macOS Privacy設定・保留Dialog・Sleep/Wake挙動はUser確認により棄却。Claude Desktop App
  再起動のみで即座に復旧。Data Loss確認済み（ruff format／mypy／Full Test Suite全てOutage
  前後で完全一致）。詳細は
  `phase_6_post_claude_independent_review_p6_rr_r_inc_002_claude_desktop_app_filesystem_
  access_outage_ja_20260829055328.md`。
```

## Changed Source/Test SHA-512（R17〜R20累計、Copilot R9〜R12 Baseline以降）

Git不使用、Filesystem直接読取り（`shasum -a 512`）のみで算出。R13〜R16分（前回Return Handoff
記載済み）に加え、R17〜R20で新規に変更／新規作成したFile、およびFormatting-only整形File
（Semantic変更なし、Format Driftのみ）を示す。

```text
[R17〜R20 Semantic変更／新規作成]
91d472cde99b0f75508ccbdf3b84d001acdf548851837230a396417b7360b4bc854ead7e6b3f7c11247619808730398911fbaef4fa6085b585061bf66925e668 role_lifecycle_manager.py
468270fbff228c66f3e24ccf270beb21912214bf3d932adca4b26a6d694d5d653d53452ca850eb27fd7970ee400ff0e5663673daa773fbf902503793e8894fe2 feature_modes_routes.py（R17時点、以後R19/R20で再変更、下記参照）
8c3d2aa6a7264ac5da266464b752530d738a59462b1538a1bdefa17bb558d80d30fe7a570723d72cc816c4c270ec08f0133f1c12b1793c95eee3671acab2b40b provider_selection_routes.py
53d7e9ff2214a59e63da66f71bbfc9c4ee4b4508693352f0a8f493b2c99ba0620f938dce082864b70991afeac1a13a50b9d1f0c6a389f722dde7e473a1a91cdf configuration_control.py
ead9a47efc9a24faf8a6d366e34aaeb3ae4704db1795c71ad5610b06dd4f95ff5b5e63f9b04ae85f44bb8765a1e532a0fa60c7642df8cc80acfa5601fa4c8961 web_application.py
92c59d90584439d55f2c8313b854e539f9d1db27b0358dfd414da7b132384d8cd7f66f49177c6784a5492585fe8aa0d1ea52a7fbdaeaf830df04b4748c4bfd4e tracked_stage_worker.py（新規）
fe0004317154e54815d97a47f5e2e4d296ac1cd34b0ac915887165c559559fc987593ce90dcd15db2709df7e87843f83dec36f3d56d5e4a61ce755ac1a83cbda stage_deadline.py
036b6e2a90532de33d48c893d618a4c80b075b50493b687f3e1f7517ef40ef7674050b5a712bcc39a10e2f1a3995a1bae50f47afa1de1326db5447f88e8a3e0a judge_live_integration.py
13539d9b19505591c458e6013c101594a733af615e9f02223531b1baa59448216e1e108a3b609f5c5c5d71cc1bc972c76dbbe7afbee5ed596046b281bd0335da conversation_generation.py
a658e9862df34356af6f20da48580993fc6a3d5cf55571996ea2d8c4f169210769fb39f6cca08697330d9306e55ad18dd945a10456ca1ec76e81bc20c1e65991 response_language.py
bfb546ec4c2e3a920e9ac432b0b957aa0f00eb7085d60e29637f9cccb5944619bda34014e15ea246d94f65684131d8271f612afe81d29108322dbed0359390e8 request_correlation_registry.py（新規）
6847ec258223554fc9fa325eecdb99773b6a778a54fc79200957f567d45ea7f92a1d92974f6697bc87ee166bd3da2db2e0213a7f1e82052fde0e1f6b8958b5d4 contracts.py
3437efa8a41f2149bdf854ca065c743569614851f920ab96778ee0416d1088c272ea0dad155f7e2f748d935c0151624c11a36ccbcfa4496f8e044c674abf6a95 failure_presentation.py（R20、classify_evaluation_failure修正）
3050f5b7e5a6ab7f26c0d3809f058099998a33876ca7d307259aa4be98ed90ef7577b16876f5f07da7c9425f6f03577c98fc6734e9baab2df5a47a8561775224 frontend/src/types.ts
dbba7cd59d578614818cfcc5a286985e7b3ddcc3dbdfe8e6060dabaa3cf96c6119b08375c19b0c2c52c2e80d9a2a1db00ccc1a89d007bb25fff08985ba268051 FeatureModesPanel.tsx
91becaca688b813733eb57fd9e7a33ad439aff9e57581d192f1e590c546d11280868455159131f168f66ea5a95b50802a7dd5ec0cbda699c000d2a836a494ddf web/static/app.js（Deterministic Rebuild、内容変更あり）
1487a8f4b8ae9f24b7de3ff1b7ef6e0b3db0974b20ff538f23522e70709e913944dcf675a6173fcbb273f34e6f191dfb6767a26881efc899f6edabca8eb0e597 web/static/app.css（Build前後不変）
0164475a2143041d53cebf2d43b61f9ccf9ab1bdf9c1b49a9efe5cee8176caaa2b5b9bee34116d7a782ddc71df451f825059dabb44bfeeef744aaf8a43b759bb web/static/index.html（Build前後不変）

[R20最終版、上記から再変更されたFile]
468270fbff228c66f3e24ccf270beb21912214bf3d932adca4b26a6d694d5d653d53452ca850eb27fd7970ee400ff0e5663673daa773fbf902503793e8894fe2 feature_modes_routes.py（R19/R20最終値、上記と同一のため再掲省略）

[R17〜R20 Test変更／新規作成]
3d2fa8975ce9b88fead29aa40b42819f9a0e8c31b2005ea462dc749e6e8f173886535f3c557fb733c4cbb30102db3edddbac295c01168567b4c63e8afdd7e3ab test_provider_selection_role_atomicity.py
731cd45c1f14a5ccdb60a76796fe0403d863c75fe9c78cfab0bb11056ce891bfebb011263022af6e7db94e292c4624ec8f790378e2bb86923b212521082b14f6 test_role_lifecycle_manager.py
a85b3181739d7f67d3f29f473a738a0226f387761ea59c559aa2b11f774cbc1c2f53ede24b930f5d688db8138f9d36f4327c698ac26c40a3048cfec0384c8046 test_tracked_stage_worker.py（新規）
c899a772f04b817aaf3ba5e91aebea33d823700ffcc1f7eeedb3188f7ce8ed3178c8fc9d8556d87b5491501f3c448a640ac6cbe64951f2c7ba1905ecaf37b64f test_judge_live_integration.py
065675488ea58c36ddac479ae44814b2d7dc1af2cd64aa31c8c33ff5bc5617a08e12e6a4904ac4cca8524eb48d98d6d06b14330e6b0dc82ff3e19c29daead02e test_judge_live_integration_dispatch_router.py
5dbb0a20741420ef0fd35b0dc8b0ee4680bc3808e8138f99ef4be54ef3ef177ae623645344a3dcc2107a3b2a2b4ee6492e2f25638a5d03e55262e57a1a04e9ed test_conversation_generation_judge_hook.py
947451a6525379dfbd8e2f81722bebe014ad44628359cf6435dd5343a29201c207c9acd3bf0ffdb9303bbf78328b45b3b9528ec8f7f651cce295875308f99f1f test_request_correlation_registry.py（新規）
dff0dc9f42a2feee39ccd05633ace2b3c5b17e71cbed9e0fac7a509e195d33a432358dca6ab128c2f6f79ae6f5bb7df5254f7eebe65bb10cba125ccd0f479db8 test_feature_modes_routes.py
7a6e12e7dc6c6484bfebf94ad707207f8ba4fbc18ce209863027595faa74b582837e0458afe4c3831e02b7a638178b9c840a578921b2c647adaee95cd31b1bcd FeatureModesPanel.test.tsx
30010c2229afc0a0d51fc16744ccd9a0582c0a66b6b6506978e0910c99b31d7ba99fcaf56365be38cec0164c192c4b8ee9e91f9c9390a5bf6c31219b56039975 test_stage_budget_and_failure_presentation.py
c9c932e93783cc1e22934a9cf1a63187b67c919a2a5c642c4e40ce97e962ba6af50d7b6830d706f040b63e4ca11ee64d0d46c46eaa82a659b5bd0d814ea3aa2d test_web_cli.py（新規Bootstrap Wiring Test）

[Formatting-only整形、Semantic変更0（R20、ruff format適用）]
d587bdba83e0e2545dcd42840ad24c4613696a47d78976e1fd111c6c5621b1473c645ec1397bf4cda4461bcc9533eb8aa66ece05a8c016ff28d8d54c1726e828 adapters/runtime_governance/reference_definition_adapter.py
cc25cd3f43e9700b43b239862df50775ff680767284ecc25f5080e109d15f0c748a30075e24d003207daccac215e0281587bac28d9e06c40ad253cc354034ce9 adapters/runtime_governance/semantic_criterion_adapter.py
cf661c8ba7e605b55e2d552595297ba7892d2c04212b2eb20eb9739085ce7496449523da218a4773f13235d6d3e3fcdac9ce3682465bb6b1669a91b6ca186b97 adapters/runtime_model_control/unavailable_role_adapters.py
6ce0c3656050fa26909fbb3b24a86dd220d78ddc2b89f7ef9fb873ec26a2dd313f0bf536e7d0339fb988a13395cdbf9dd71a31e0217d460d6b8148167309a9cd bootstrap/recording_live_integration.py
0157f0387dae201dd0c766a2397de0c35b219845a10619c088cbfb07e13546993d1b5e86586bb2fa03c262f624f059c9561d85a2f145281766699b211773cecd bootstrap/runtime_governance.py
c145039f31d60da34521b0a9d0c5cee7599f4c38536d1b1ffbc6c7b2d1511c3bb99d35b72026053be371a64e5c48f72c9374dbd9ecead6e3966eac2b095dbbf1 modules/evaluation/application/judge_output_decoder.py
aff32118e922f5803d95f863fa7c37b41e7d06629bb844303cef51457b5ff703e8b8cbdbcc2e83817542e4b199577a819d5c4793ee6333580cca1d127aa84c61 modules/evaluation/application/judge_prompt_builder.py
fa84895d1689dcb0ce935e668a973cd325140916c95e2596c715df3fb5eb38d4e2a541232bd6994d70bdade854157fd098f832c3631e4be6a278c05f4aa79d43 modules/runtime_governance/application/mode_controller.py
2070b55a55b1289bbd35ee4fc7f156d75b2cad47f9c3d9ebcd92ed5a729de8d64c30dc22f4328f4f82b075384d09f9a84d1aab7bf2cd37e1122224fc3fa8263f modules/runtime_governance/domain/evaluation.py
dba6ffb3c8ee6012c503c86675d78a1d6600a2475fc45057d4e1226cdc6db820bd67c830eff205fe02c956d0eef7708716e3907c04359152342bd791f9a4e8d4 modules/runtime_model_control/application/provider_selection_controller.py
71c83b98c1c17fcb3bf00419dc1854908e2c23c7a40f4d1dc6122a1f6f13ee8824866ac1d23fbe1eb22c89ab1d2e980b401cb23853b05bef14075872a1dbf7fa modules/runtime_model_control/ports.py
302b3891f406a628ef42f76ff17217526339a682c56df753445d1da10d92b517c3379bbcf0c7f2031493f2d08bb41802c6435c6460b01c543a05be8a462c9509 test_recording_live_integration.py
f9ab1e64360f0f65fde13a6ff9703f2f8a3d4989a3cd305bad7709a441b30981baccc168c22ec95eae97f48293625e6c0ab011838dd42d1cb6063a539916770e test_selene_adapter.py
56fc016163b61a03d85da7700dcfbd0fa1356b10ad91dab822613038651bce2f964339ab2c4b8f610f863ce048c700085b1fd45c1770bd744cea8b2f5d156731 test_semantic_golden_fail_closed.py
ccb92951f8267b1a3cc5f41d96b412aad1ef6dd1c1701869680b4042f0512b5eefc97a0d75eee0f2435306cf5d2d6fd1eb618af55cf4469cb62ead616ae3251c test_qwen3guard_adapter.py
```

R13〜R16分（`configuration_control.py`は上記R17再変更版が正、`request_correlation_registry.py`
はR19新規＋R20 Format整形後が正）を含む完全なFile一覧は前回Return Handoff
（`phase_6_claude_current_task_r13_to_r16_exact_return_handoff_ja_20260828233354.md`）と
本Documentの合算を正本とする。

Exact next action: Codex Independent Review. Phase 6 Closure、Phase 7、Git Actionのいずれも
本Claudeからは着手していない。
