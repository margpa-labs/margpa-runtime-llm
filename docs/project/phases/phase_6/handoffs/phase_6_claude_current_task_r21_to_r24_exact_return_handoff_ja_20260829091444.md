# Phase 6 Claude Current Task R21〜R24 Exact Return Handoff

```yaml
provider: Claude (Sonnet 5)
role: 設計者兼実装者役
task_identity: Phase 6 Current Claude Task（R21〜R24 Differential Rework）
active_contract: phase_6_claude_current_task_r21_to_r24_exact_rework_handoff_ja_20260829062910.md
reviewed_against: phase_6_gov023_claude_r17_to_r20_controller_independent_review_ja_20260829062910.md
r24_recovery: phase_6_current_claude_task_r24_final_recovery_ja_20260829091318.md
claim: Complete Candidate with Real Provider and User Manual Gates
next_owner: Codex（プロジェクト責任者兼設計統括者役）
next_exact_action: Controller Independent Review
```

## Disposition（P6-CODEX-081／084／086／087）

| Finding | Disposition |
|---|---|
| P6-CODEX-086 | Fixed（R21）: `RoleProviderLifecycleManager`へ`RoleTurnHandle`／`begin_role_turn()`を新設し、Adapter解決とTurn Lease取得を単一Lock Acquisitionで原子化。旧`active_adapter()`→別call`begin_turn()`のTOCTOU設計を廃止。Judge（`judge_live_integration.py`の`begin_judge_role_turn`/`end_judge_role_turn`、Hook入口でOFF早期return後にLease取得、`_run_judge()`のfinallyでExactly-once Release、Coordinator Slot拒否時の明示Release含む）とGuard（`qwen3guard_detector_adapter.py`の`detect()`、`try/finally`でLease保持区間を`classify_point()`呼出しに正確に一致）双方でProduction Call Siteへ実配線。5件の実Thread Testで、実Call中のShutdown Falseへの収束・Release後のUnload・Exception時Zero Leak・複数並行Leaseを証明。 |
| P6-CODEX-081 | Fixed（R22）: `TrackedStageWorkerRegistry`を新設。`run_tracked_stage()`が提出直後に`registry.track(future)`し、`future.add_done_callback()`でExactly-once除去（Exception／Timeout後のLate Complete含む全Pathで発火）。`shutdown()`は新規受付を停止し現在Track中のFuture全件を合計Timeout以内でBounded-Join、Bound超過でなお実行中なら`False`を返しCleanを偽装しない。`WebRuntime.close()`（`web/contracts.py`）が`role_provider_lifecycle.shutdown()`・`close_callback()`（Model Unload）より前にこのShutdown結果を確認し、False-clean時は`RuntimeError`でUnloadへ進まない。6件の実Thread Testで、Blocked Worker中Shutdown False・Release後Retry True・Worker Exception・複数Worker・Shutdown後の新規Dispatch拒否（最強形のLate Publish 0）を証明。 |
| P6-CODEX-087 | Fixed（R23）: `Qwen3GuardManifest`（新設）が、Qwen公式Hugging Face Repository（`Qwen/Qwen3Guard-Gen-0.6B`、Exact Revision `fada3b2f655b89601929198343c94cd2f64d93cc`）とQwenLM公式GitHub Repository（`QwenLM/Qwen3Guard`、Exact Revision `6a52eca94b3d2aedb8aebd36baa353828d4166f1`）から本Package限定Read-only Network Authorityで実取得した内容を記録。両Sourceの独立Corroborationにより`Jailbreak`がInput/Context限定Categoryであることを確認し、Target別Category Set（Input/Context 9件、Output Candidate 8件）とLine Protocol（2行／3行）をManifestへ固定。Strict Decoderの`Categories`任意許容Bugを修正（両Target共通で無条件必須化）。`verified_official_contract`を外部Boolean注入から`Qwen3GuardManifest.is_complete_and_verified`（8項目全検証）へ置換——単体Booleanでは絶対にVerifiedにならない。`Qwen3GuardGenAdapter`はConstruction時にManifest Schema Validationを行い（Fail-fast）、`classify_point()`はTarget-scoped Category Mappingを使用。21件のFixture Test新規追加（Official Valid／Missing Categories／Wrong Order／Wrong Target Category／Malformed／Unknown／Timeoutの7種別を網羅）。 |
| P6-CODEX-084 | Fixed（R24）: 正しい正本（`P6-RR-ACC: PASS 34/PARTIAL 1/N/A 3/NOT RUN 2=40`、`P6-DELTA: PASS 23/PARTIAL 3=26`）から、P6-RR-ACC-016／017（R21 Production Evidence）、P6-RR-ACC-022（R23 Manifest Evidence）、P6-DELTA-014（R24 failure_at実測Test）の4 IDを再導出。最終集計`PASS 59/PARTIAL 2/N/A 3/NOT RUN 2=66`を機械検証（`59+2+3+2=66`）。新規Test数（本Package全体34件）はTest Node ID実数から算出し、Package内訳（6+6+21+1）と一致することを確認。R20自身の「1744 passed」Baselineは本Session内で独立再検証しておらず、本Session実測合計1787との逆算差異9件をOpenとして正直に記録した。 |

## R21〜R24 Recovery Index（各Package1件、簡潔）

```text
R21: phase_6_current_claude_task_r21_recovery_ja_20260829084104.md
R22: phase_6_current_claude_task_r22_recovery_ja_20260829084917.md
R23: phase_6_current_claude_task_r23_recovery_ja_20260829090242.md
R24: phase_6_current_claude_task_r24_final_recovery_ja_20260829091318.md（Internal Review含む）
```

## Production LeaseとTracked Worker Shutdownの実Thread Test（名前／結果）

```text
[R21 — tests/unit/runtime_model_control/test_role_lifecycle_manager.py]
test_begin_role_turn_pairs_adapter_and_lease_from_one_lock_acquisition ............ PASS
test_begin_role_turn_returns_none_for_a_none_provider_no_lease_acquired ........... PASS
test_begin_role_turn_blocks_shutdown_from_unloading_until_release ................. PASS
test_lease_released_via_finally_after_a_real_call_exception_leaves_zero_leak ...... PASS
test_multiple_concurrent_role_turns_each_track_their_own_lease_generation ......... PASS

[R21 — tests/unit/bootstrap/test_judge_live_integration_dispatch_router.py]
test_selene_initial_judge_repair_and_frozen_selene_rejudge_single_turn_e2e
  （Lease Release Tracker Assertion追加、S9 E2E経由でRelease exactly-once実証） ..... PASS

[R21 — tests/unit/adapters/guardrail_governance/test_qwen3guard_detector_adapter.py]
test_reports_error_when_classify_point_raises_and_still_releases_lease ............ PASS
test_forwards_clear_when_active_and_safe_and_releases_lease_exactly_once .......... PASS
test_end_role_turn_raising_never_masks_the_detection_result ....................... PASS

[R22 — tests/unit/bootstrap/test_tracked_stage_worker.py]
test_registry_shutdown_returns_false_while_a_worker_is_still_blocked .............. PASS
test_registry_shutdown_retried_after_release_reports_true ......................... PASS
test_registry_untracks_a_worker_that_raises_zero_leak .............................. PASS
test_registry_untracks_a_late_completing_worker_that_raises_zero_leak ............. PASS
test_registry_tracks_several_concurrent_workers_independently ..................... PASS
test_registry_refuses_new_work_once_shutdown_has_begun_zero_late_publish .......... PASS
```

## Qwen3Guard Manifest Identity、公式Source、Decoder Contract差分

```text
Hugging Face: Qwen/Qwen3Guard-Gen-0.6B
  Exact Revision : fada3b2f655b89601929198343c94cd2f64d93cc
  Source         : tokenizer_config.json（当該Revision Pin取得）
  Source SHA-512 : 3ad26646bb8fe326f2781a995f4b1c3375b1cccfa5a06419c7d3b05fea5728b0
                   4cddf2dd739c7bfdf430dfc369a4431704df2fdbb55f02dcb2964481264248df

GitHub: QwenLM/Qwen3Guard
  Exact Revision : 6a52eca94b3d2aedb8aebd36baa353828d4166f1
  Source         : README.md（当該Commit Raw取得）
  Source SHA-512 : 0fda11e35c0cd33237d6108baae4a6c0d3eca93e71ac8b8d294ad8f5a69c99b1
                   4f754622d03bf2c833a5e544ffa50dd7b33198b839f47361ccb0a5d0b580d31c

Decoder Contract差分（旧→新）:
  Input/Context Categories必須性: 任意 -> 無条件必須（Safeも`Categories: None`必須）
  Output Candidate Categories必須性: 任意 -> 無条件必須
  Target別Category Set: 単一Flat Mapping（Target区別なし） ->
    Input/Context 9件（Jailbreak含む）／Output Candidate 8件（Jailbreak除く）
  verified_official_contract: 外部Boolean単体注入 -> Manifest 8項目完全性検証必須
  Classification新規Field: contract_manifest_digest_sha512（Manifest File自体のSHA-512）
```

## S1〜S17／Required Regression Scenarios（R17〜R20から変更なし）

R21〜R24はS1〜S17 Execution Matrixの再検証対象ではない（R17〜R20 Return Handoff記載の全17件
PASS・Caveat 0件を保持）。R21〜R24自身のRegression Scenario（Production Lease、Tracked Worker
Shutdown、Qwen3Guard Manifest、failure_at）は上記各Test名で個別に証明済み。

## Acceptance Inventory（66 ID、正しい集計）

```text
PASS   : 59 ID
PARTIAL: 2 ID（P6-DELTA-004: Guard専用Evidence Recorder不在によるIdentity Field往復記録Test
         欠如；P6-DELTA-016: Phase 9予約Frontend Layout項目、Handoff明示指示によりPARTIALを
         維持）
N/A（Process）: 3 ID（P6-RR-ACC-036／039／040）
NOT RUN: 2 ID（P6-RR-ACC-037／038、Real Artifact／Browser要）
合計   : 66 ID（59+2+3+2=66、機械検証PASS）
```

個別62 ID（本Packageで変更していないID）のDisposition／Evidence Pointerは
`phase_6_current_claude_task_r20_final_recovery_ja_20260829061552.md`「66 Acceptance ID
個別Disposition」記載のまま正本とする。本Task（R21〜R24）で更新した4 ID
（P6-RR-ACC-016／017／022、P6-DELTA-014）の詳細は`phase_6_current_claude_task_r24_final_
recovery_ja_20260829091318.md`「2. 66 ID正本再集計」参照。

## Canonical Verification結果

```text
ruff check .                : All checks passed（483 files）
ruff format --check .       : 483 files already formatted
mypy（pyproject.toml既定）   : Success: no issues found in 483 source files
pytest（Backend Full）       : 1787 passed, 7 deselected
frontend typecheck           : Clean
frontend lint                 : Clean
frontend test                : 231 passed（25 test files、Regression 0、Frontend Source変更0）
frontend build                : Clean（89ms、警告0）
```

## Internal Review（Implementation Freeze後）

Requirement-by-Requirement（R21〜R24全30 Contract項目、未実装0）、Cross-component（R21/R22の
意図的分離設計・R21/R23の直列合成、いずれも競合なし再確認）、Concurrency（Lock内Atomic性
再確認）、Failure Injection（Judge 5経路／Guard 3経路、全Release確認）、Negative Path（3構成
でRegression 0確認）、Claim Audit（本節自体）の6観点で実施。Finding 1件
（`IR-R24-001`、`RoleProviderLifecycleManager._unload_locked()`のException時Pop非対称性、
R21以前からの既存性質でP6-CODEX-086の契約範囲外、Observationとして記録・Rework対象外と
判断）。Rework Trigger 0件のためCycle 2 Reviewは未実施。詳細は R24 Recovery Index参照。

## Open Critical／Major／Minor／Real Model／User Gate

```text
Open Critical: 0
Open Major   : 0
Open Minor   : P6-DELTA-004（Guard専用Evidence Recorder不在）、P6-DELTA-016（Phase 9予約
  Frontend Layout項目、本Task対象外）、IR-R24-001（`_unload_locked`のException時Pop
  非対称性、Observation）
Real Model   : Qwen3Guard／Selene実Artifact NOT RUN（`dedicated_model_authority_granted=
  False`のまま、本Taskでは変更していない——Contract ProvenanceとModel Load Authorityは
  独立したGateであることをR23で明示的に維持）
User Gate    : P6-RR-ACC-037（Real Artifact実測）、P6-RR-ACC-038（Real Browser確認）
```

## Action Inventory（R21〜R24累積）

```text
Git Action        : 0
Network Action     : 4（R23限定、HF Models API・HF tokenizer_config.json pinned raw・
  GitHub commits API・GitHub README raw、全てRead-only・匿名・Qwen公式Domain限定）
Provider Memory Action: 0（前Task（R17〜R20）での訂正・削除を継続維持）
Root外Read/Write   : 0
Destructive/Irreversible Mutation: 0
```

## Incident Record

本Package群（R21〜R24）中に新規Incidentは発生していない。既存記録（P6-RR-R-INC-001: Git
Read Incident、P6-RR-R-INC-002: Claude Desktop App Filesystem Access Outage）はそのまま
保持。

## Changed Source/Test SHA-512（R21〜R24）

```text
[R21〜R24 Semantic変更／新規作成 Source]
6c0936bdc68e01fc3034b311c1e41d7cd931e2f29cbaaa3a6f6ffb88ecef24fccd4c018dde31ffa2dad153e7e6b0b32d22887b545f152a5191b0e38652b2eef5 role_lifecycle_manager.py
dc7131c8f87f38892139a1f5e9ecd0db0b41998082dc957dfa289d695eeb479118480a7093c86454f6ff3f774ab6aa9cd71c3a2ff6da2b4a9c76681326b816ed runtime_model_control/application/__init__.py
105ffcbb30768c94486adf44c2c7b2bf49a5e574bc090a3bf5853e48362e7dc9562bc9c6b8c33a8f01e5ac44a3e8dcbf53ef987cee6b3cb5be1b5464e14e2637 qwen3guard_detector_adapter.py
2199f7e07dff16c511d4e12a2f5d3bf05bc23cea390ffddf15794903ff90a5b4c9bcae6a1a273d3c91cdef1b5104b2985fe281f758fe8bbca57cc35974d836bb guardrail_governance.py
2774099b0e440050b636ec6c5634b5573999676742e08be447821f1201d375234c083aa27fad8b59ce1ca575c6baa6054060960e62a6a9dec69b3a0cc0754175 web_application.py
a4f7cf41da07f0072f24a2ca7e9aa44a954fc438a42d5fefc285bd87f68890814fd00cafbcebf415cc4fda67079f12c24de50ab5767f7be7a0b268a309de9178 judge_live_integration.py
c6b2f93d44c491e09e30d240489e4eee79fa9b8f6ee81ee9b3363326ddb279f5d37188a78f15dfd3bcb1b173d7d4f4d4b8c44f75d3fbeaf89787da5283037a5e tracked_stage_worker.py
8498fa25a0eb829b267a4c980085421236ad75a23e53700e7096347689f58b7b95b1c17712bd072174185d1f4cc827081ada9a2d8f065ae3b1769892313d3165 web/contracts.py
096a2624c1f7bc95ad2b17012b7c6d2c55088f22d6a4477c800810aa9bd8527b29ee7c0f155a9b09de858c27b99b9ea6956083a6d9675e8d97b5e631c6b5d84b modules/guardrail_governance/domain/qwen3guard.py
a5e8ad739d8d84418564fea0e6dc6d6f5fcfc955dbf35ac77b9bf97acfa9bf2e9c409a57ffad2a868cb81550aeb28b2ba2285946e8b03d30895c9f9570a89a1e modules/guardrail_governance/domain/taxonomy.py
dd465d39862ba5894395929cd16dd52b8b74c1750958f894f7fdf942e8d1b4748a1e2f899e02f1aae7f57b6d95ab6d863738e0f6646a935024aa87c008af0817 qwen3guard_adapter.py
96d17d7c1727efd6e2c712cc26fa8fa780654ab96573579ccfd521cad3816edd20a3cb268e979caa13f83de51a129602721460073cb25f0b1d9a3616ca0785e9 qwen3guard_manifest.py（新規）
ede5c8d50c8d97a795ded302acbb7f7ead435776f308039f913d91f267f1a5588d6e4f3b07661202779ecf9409f634d675a5763ad31b8b6a3c064dbd79ea4dcb dedicated_role_adapters.py
fa713fa79ea28d3ba201cd4067701e9fd465f6d6511e725588dbd35a00b052b41ca1df7d49b7f3b966fe4c233b061f5d13d09fbc13f230d378b36d178e3db66c config/guardrail/qwen3guard/manifest.json（新規、実Fetch値）

[R21〜R24 Test変更／新規作成]
73552f536f9ba1cc144589aa2fd13b1ee512498a859fe61267b3962d8e68ae591d77ea2b97fd80e6616b0359c30022285916858051f1982be3845102552cf859 test_role_lifecycle_manager.py
cc2e2c0993a92971bcddc9243ed2348e1c781a209a7978ffb7e04aba950badb506a47745c58e18a820a1028b72f57fbaa417be11bcdd359f6d6712d68a1e065d test_qwen3guard_detector_adapter.py
7270917707fdece200a4cfd7427a969c3e077d12e23d55ad118118ebc17c75de51568937475aae7aa6b782cdb276b1d9306c47e44de78f8a2d74567f34b17369 test_bootstrap_hooks.py
0ecd44a2f94195c072b455cd856be53b0c18d1ffcf1e4542180ba4a93088a3869afea567800ed09d8f2f93d7dd95df49a94f4b418cb865aa02b8e89024c028ec test_judge_live_integration.py
402288b715181f5a4ff2040beeb5f587ec5f86dbbaff9c4e0dbecdad1a3f009e4eb5cb9edf97e3f82b1ed2ee7a3f2b116e0d6d6adcfe974a487960a8877aa59d test_judge_live_integration_dispatch_router.py
45afde22da0cac26aa916d69a8d9cb386b154ed9b25dfb77fedbf84e364d54f8551d05af4c20c4cc2e7da770c9d10584383032b09e765abea9ca80353f847774 test_tracked_stage_worker.py
a8fec8351d2cb020392ea1b163eadd787ad9547cba8110e278aeac3e3191b862370c0e4aace78ee3436522bbe81f8ccde9ef9047340ea62b6c762b3162f5e34d test_dedicated_role_adapters.py
ea884da2b31b367c7efc41a3dcdcf14a4d9ecb72a46ab3affa0a2cc50747e5c918b71b4e25a364257a6d6228e6f7d63b5da5b896fc7e7361758ca279de7d797e test_qwen3guard_adapter.py
01bbf3e9b1d4d1493a1e5eef52b095ec638d811d0024f3a0fe34d66b1654bfe6fcd225a13ef50c75f4e140f8a0723432ad3fe97cbcb4e4d8ab7273937e2a9234 test_qwen3guard_manifest.py（新規）
15531e70e2c135cad15e555a34518227bd0e4094c858d2b02fc7761815373c2337faaf26988f39e8138241c4c981d06e3928e527228aae90333c1511038d3672 test_provider_selection_role_atomicity.py
```

R17〜R20分（`configuration_control.py`はR17再変更版、`request_correlation_registry.py`は
R19新規＋R20 Format整形後）を含む完全なFile一覧は前回Return Handoff
（`phase_6_claude_current_task_r17_to_r20_exact_return_handoff_ja_20260829061552.md`）と
本Documentの合算を正本とする。Frontend Source File変更は本R21〜R24累積で0件。

Exact next action: Codex Controller Independent Review。Phase 6 Closure、Phase 7、Git
Actionのいずれも本Claudeからは着手していない。
