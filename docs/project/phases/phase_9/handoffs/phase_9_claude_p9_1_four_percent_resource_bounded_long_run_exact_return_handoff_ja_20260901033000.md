# Phase 9-1 Claude Four-percent Resource-bounded Long-run Exact Return Handoff

```yaml
document_id: phase_9_1_claude_four_percent_resource_bounded_long_run_exact_return_20260901033000
document_type: exact_return_handoff
document_state: frozen
language: ja
created_at: 2026-09-01 03:30 JST
provider: Claude
role: 設計者兼実装者役
task_identity: Current Claude Designer Implementer Task
task_state: continued_not_fresh
phase: phase_9
program: phase_9_1
execution_scope: P9-1-0_through_P9-1-D
入力Exact_Handoff: phase_9_claude_p9_1_four_percent_resource_bounded_long_run_exact_handoff_ja_20260831221823.md
入力Exact_Handoff_sha512: 974ffffcce6cd9a74cb16a5ea020ff2aa9d38e44b96e3cfeab27e5ebf277adfd9d4017026b0b4bdc4f939f379b12f3c6be9ff92f555033f521683d617934ef15
maximum_claim: P9_1_COMPLETE_CANDIDATE_FOR_CONTROLLER_REVIEW
phase_9_2_entered: false
git_mutation_executed: false
git_read_executed: false
network_used: false
real_browser_used: false
real_model_used: false
real_mcp_used: false
user_runtime_data_touched: false
real_artifact_touched: false
```

## 1. 結論

P9-1-0からP9-1-Dまで連結実行し、`P9_1_COMPLETE_CANDIDATE_FOR_CONTROLLER_REVIEW`として
Returnする。

Phase 6で成立済みのSemantic 109、Selene／Qwen3Guard Adapter、Role Lifecycle、Provider
Selection、Judge Dispatch、Budget／Cancel／Recordingは一切再実装・Rollbackしていない。
本Sessionの実装Authority境界（Project Root外Artifact禁止、Real Model Load禁止、Network
禁止）の中で、User Macで未成立だったProduction接続の差分だけをProbeし、最小差分（Backend
Source変更1ファイル、Test追加4ファイル）で接続・検証した。

**最重要Finding**: Semantic 109の`Deferred／evaluated 0`固定から脱却する経路は、Built-in
Judge Evaluatorの改善では**ない**（109件全Criterionが`CLASSIFICATION*`／`ABSOLUTE_SCORING`
――決定的Checkでは誠実に解決できない質的判断であることをCode／既存Testから確認済み）。
唯一のAuthority非依存の脱却経路は、既存UI上で選択可能な**Main-shared自己Judge**
（MainのRoleに既にLoad済みのModelをそのままJudgeとして使う）であり、本Sessionの新規Test
がこの経路が実際にProduction Codeとして正しく機能することを証明した。User Mac Evidenceが
観測した「全件Deferred／evaluated 0」は、User自身が`Judge Built-in Deterministic`を選択
していたことの正しい帰結である。

```yaml
p9_1_a_dedicated_runtime_disposition: COMPLETE_EXCEPT_WU_005_AUTHORITY_REQUIRED
p9_1_b_semantic_109_disposition: COMPLETE
p9_1_c_judge_repair_rejudge_enforce_disposition: COMPLETE
p9_1_d_integration_review_disposition: COMPLETE
mvp_blocker_open: 0
critical_open: 0
```

## 2. Package／Work Unit別Disposition

```text
P9-1-0          Preserved Controller Preflight固定                              COMPLETE
P9-1-A-WU-001   Preflight Contract共通化                                        COMPLETE
P9-1-A-WU-002   Selene Production配線（Candidate Load〜Evidence）               COMPLETE (Fixture)
P9-1-A-WU-003   Qwen3Guard Production配線（同上）                               COMPLETE (Fixture)
P9-1-A-WU-004   Lifecycle合成（Atomic Commit／Lease／Unload）                   COMPLETE (Fixture)
P9-1-A-WU-005   Real Local Artifact Smoke                                       AUTHORITY REQUIRED / NOT RUN
P9-1-B-WU-001   109 Rule Inventory（Definition／Point／Capability／Type）        VERIFIED
P9-1-B-WU-002   Normalized IR -> Semantic Criterion Registry拡張                VERIFIED（拡張不要、既に109/109）
P9-1-B-WU-003   Built-in対応Criterionの実評価                                   VERIFIED（対応Criterionは0件、これが正）
P9-1-B-WU-004   Criterion Identity／Count／Reason／EvidenceのLossless投影        COMPLETE (NEW TEST)
P9-1-B-WU-005   Golden／Negative／Malformed／Budget／Cancel／Restart／109集計    COMPLETE（新規1件＋既存確認）
P9-1-C-WU-001   Main Candidate／Frozen Context／Judge Dispatch／Strict Decode    VERIFIED（既存配線）
P9-1-C-WU-002   Judge Outcome -> Repair Eligibility／Plan／Budget／Candidate     COMPLETE (NEW TEST)
P9-1-C-WU-003   Repair Candidate -> Rejudge -> Adopt／Reject／Fallback収束       COMPLETE (NEW TEST + 既存確認)
P9-1-C-WU-004   Semantic ENFORCE Action／Conflict／Priority／Authority          COMPLETE (NEW TEST x3)
P9-1-C-WU-005   Negative Golden Path（Cancel／Deadline／Failure／Malformed／OFF）VERIFIED（既存で充足）
P9-1-C-WU-006   Configured／Active／Executed／Criterion Identity Chain          COMPLETE (NEW TEST)
P9-1-D-WU-001   Focused Regression（Chat／RAG／Citation／Manual URL等）          COMPLETE（無変更、Full Suiteで確認）
P9-1-D-WU-002   Canonical Backend／Mypy／Ruff比例検証                            COMPLETE
P9-1-D-WU-003   観点変更二段階Internal Review                                   COMPLETE（Finding 0件）
P9-1-D-WU-004   Traceability／Return Handoff                                    COMPLETE（本文書）
```

## 3. Mandatory Reading／Digest

```text
Exact Handoff SHA-512  : 974ffffcce6cd9a74cb16a5ea020ff2aa9d38e44b96e3cfeab27e5ebf277adfd9d4017026b0b4bdc4f939f379b12f3c6be9ff92f555033f521683d617934ef15
Preflight SHA-512      : f6af1d33f13fd541426a1ff9b3f0f9787fb4f90e3e6a7a23b595745318356fbc2a5556a408a90ba6f531172f1abd70425c7f6d48730d8b181b8622abb6097cdb
Execution Plan SHA-512 : 54ca3dd7e5c9eb40d208fd765465f5fd14d1f3b661358e154189235ea00167344a3250be3eb4d6a43fdb25b1a52343fa2c35254b5aac7e2a91bb3d42dc5f8ea2
```

3文書とも指定通り全文読み、Hashを照合した。Preflight（P9-1-0-WU-001〜003相当）を再監査せず、
そのままPreserved Controller PreflightとしてP9-1-0 Recoveryへ固定し、直ちにP9-1-Aから
着手した。

## 4. Preserved As-built（再実装・Rollback無し）

`modules/runtime_governance/`のSemantic Criterion／Frozen Turn／Provider State／Result／
Action Resolution／Evidence、Canonical 109 Descriptor Compiler／Adapter
（`semantic_criterion_adapter.py`）、`adapters/evaluation/selene.py`、
`adapters/guardrail_governance/qwen3guard_*`、Provider Selection／Role Lifecycle／Lease／
Tracked Worker、`bootstrap/judge_live_integration.py`のBuilt-in／Selene／Main-shared
Dispatch、Phase 6 Budget／Deadline／Cancel／Recording ―― いずれも本文コード自体は無変更
である。`dedicated_role_adapters.py`のみ、挙動を変えないPreflight Contract共通化Refactorを
実施した（§5参照）。

## 5. Package別Finding／実施内容

### P9-1-A（Dedicated Selene／Qwen3Guard Runtime）

`SeleneRoleAdapter.preflight()`／`Qwen3GuardRoleAdapter.preflight()`は文字通り同一の19行
だった。共通Helper`_run_dedicated_preflight()`へ統一（挙動無変更、既存9 Testが無改造で
全PASS）。続けて、Authority付与後の配線が実際に機能するかを`LlamaCppModelAdapter`を
`ModelPort`形状のFixture Doubleへmonkeypatchして証明した――`test_dedicated_role_adapters_
production_wiring.py`（新規）4 Test。`LlamaCppRuntimeModelBackend`自体は純粋な委譲／計算の
みのため無改造、Real Artifact・Network・`llama_cpp`ライブラリのいずれにも未到達。
Production Composition Root（`web_application.py`の`dedicated_model_authority_granted=
False`）は意図的に無変更のまま――これはFail-closed安全機構そのものであり、本Sessionの
Authority境界（Real Artifact禁止）に照らして正しい。WU-005（Real Local Artifact Smoke）は
`AUTHORITY REQUIRED／NOT RUN`として明示的に分離した。

### P9-1-B（Semantic 109／Built-in Evaluation）

`_ARGD_MAP`／`_mapping_for()`を実読し、109件のCanonical Descriptorが全件
`CLASSIFICATION_WITH_REFERENCE`／`ABSOLUTE_SCORING`／`CLASSIFICATION`のいずれかへ写像
される（＝質的判断のみ）ことを確認した。`_run_built_in_semantic_judge()`自身のDocstring
と既存Test（`test_built_in_judge_reports_every_semantic_criterion_as_not_applicable`等）が
同じ結論を既に証明しており、Built-inの対応Criterion集合は空集合であることが判明した――
これはBugではなくPhase 6で審査済みのArchitecture上の結論である。

唯一Authority非依存で実評価に到達できる経路はMain-shared自己Judgeであると判断し、既存の
Routing専用Test（`test_main_shared_active_adapter_is_dispatched_and_tagged_as_executed_
provider`）が実Criterionを一度も演習していなかったGapを埋める新規Test
`test_main_shared_active_adapter_genuinely_evaluates_semantic_criteria`を追加した。実
Semantic Snapshot付きでMain-shared Dispatchを駆動し、`criteria_evaluated == 1`
（Deferred／0からの実脱却）とEvidence Lossless記録を証明した。

### P9-1-C（Judge／Repair／Rejudge／Semantic ENFORCE）

既存の`test_selene_initial_judge_repair_and_frozen_selene_rejudge_single_turn_e2e`は
Initial Judge -> Repair -> Frozen Rejudgeを1本のTurnとして証明しているが、Selene限定
（本Task未保有のReal Artifact Authorityが必要で実行不能）だった。新規Test
`test_main_shared_judge_needs_repair_and_rejudge_reuses_the_same_main_service_single_
turn_e2e`で、Authority非依存のMain-shared経路について同じ証明を行った――実Criterionが
DEVIATION、Repair Eligibility ELIGIBLE、Rejudgeの実IdentityがSelene版と同じく「同じ既に
Load済みの１つのModel」であること（`rejudge_service is service`）、Turn Leaseが1回のみ
Acquire／Releaseされることを証明した。

`resolve_semantic_action()`（Semantic ENFORCEの中心Action Resolver、Preserved As-built）は
唯一の既存Testが単一Criterion・OBSERVEモードのみで、複数Criterion間のConflict／Priority、
実ENFORCEモードのDeviation／Uncertain分岐を一度も演習していなかった。新規Test 3件で、
Uncertain優先のConflict解決、複数Deviationの単一Repair Requestへの収束、
`repair_mode="off"`時のAuthority非拡張（Recommendationは正直に保持、Executeはしない）を
証明した。

### P9-1-D（Integration／Review）

Canonical Backend Full Suite（2200 passed, 7 deselected）、`mypy src/`（346ファイル）、
`mypy tests/`（212ファイル）、`ruff check`／`ruff format --check`（558ファイル）――いずれも
Clean。Frontendは本Session無変更のため検証・Static Artifact再生成は不要（Handoff§7の
Fast Closure Rulesに沿う）。観点変更二段階Internal ReviewはいずれもCritical／Major／MVP
Blocker Finding 0件だった（詳細はP9-1-D Recovery Index §2）。

## 6. Regression Guard方式

新規Test全9件について、対応する実装の一部を意図的に一時破壊し（例:
`SeleneRoleAdapter.load()`の`model_key`破損、`SeleneRoleAdapter.unload()`の状態Reset削除、
`rejudge_service=service`を`None`へ、`_judge_criterion_counts()`の`evaluated`を0へ固定、
`resolve_semantic_action()`のUncertain／Deviation分岐順序入替）、新規Testが実際に該当
症状でFailすることを確認してから復元し、diffで完全一致を確認した。すべて成功。

## 7. Semantic 109 集計（正直な開示）

```yaml
canonical_descriptor_total: 109
canonical_descriptor_compiled: 109
canonical_descriptor_unsupported: 0
evaluation_method_distribution: "全件 CLASSIFICATION_WITH_REFERENCE / ABSOLUTE_SCORING / CLASSIFICATION（質的判断のみ）"
built_in_applicable: 0
built_in_evaluated: 0
main_shared_applicable: "Batch選択数に依存（max_criteria／Budgetで決定、Turn毎に変動）"
selene_applicable: "Batch選択数に依存（同上、ただし本Task未保有のReal Artifact Authorityで未実行）"
```

本Sessionは実Production Turnを一度も実行していない（Fixture／Mockのみ）。したがって
「実際に何件評価されたか」というProduction観測値は主張しない。主張しているのは「Main-
shared経路の評価Mechanicsが正しく配線されていること」であり、実Turn数値は次のUser Mac
確認またはController Reviewでのみ得られる。

## 8. Network／Install／Git／Browser／Model／User runtime_data Action Count

```yaml
network_authority_used: false
real_network_calls_made: 0
install_authority_used: false
git_commands_executed: 0
real_browser_used: false
real_model_used: false
real_mcp_used: false
real_artifact_read_stat_digest_load: 0
user_runtime_data_read: 0
user_runtime_data_written: 0
```

新規Testは全て`monkeypatch`によるFixture Double、または既存の`_Fake*`パターンのみで完結
した。実Network・実Browser・実Model・実MCP・実Artifact・User `runtime_data/`のいずれにも
一切到達していない。

## 9. Changed Paths

```text
src/margpa_runtime_llm/adapters/runtime_model_control/dedicated_role_adapters.py            (modified, behavior-preserving refactor)
tests/unit/adapters/runtime_model_control/test_dedicated_role_adapters_production_wiring.py (new, 4 tests)
tests/unit/bootstrap/test_judge_live_integration_dispatch_router.py                         (modified, +2 tests)
tests/unit/runtime_governance/test_semantic_runtime.py                                      (modified, +3 tests)
```

## 10. Recovery Index Paths

```text
docs/project/phases/phase_9/history/index/phase_9_1_p9_1_0_entry_recovery_ja_20260831221823.md
docs/project/phases/phase_9/history/index/phase_9_1_p9_1_a_dedicated_runtime_recovery_ja_20260831231500.md
docs/project/phases/phase_9/history/index/phase_9_1_p9_1_b_semantic_109_recovery_ja_20260901010000.md
docs/project/phases/phase_9/history/index/phase_9_1_p9_1_c_judge_repair_rejudge_enforce_recovery_ja_20260901020000.md
docs/project/phases/phase_9/history/index/phase_9_1_p9_1_d_integration_review_recovery_ja_20260901033000.md
```

## 11. User Mac Manual Gate（次のUser確認事項）

```text
1. Settings/Provider SelectionでJudge Roleを"Built-in Deterministic"から
   "Qwen3 4B (self when Main is Qwen)"（またはMainがDeepSeekならその対応行）へ切り替える。
   これは既存UIの選択肢であり、新Feature追加は不要。
2. 通常Chatを1 Turn実行し、Dev Agent／Governance PanelでSemantic Criteriaの
   Evaluated件数が0より大きいことを確認する。
3. 意図的にNEEDS_REPAIRとなる応答（例: 根拠のない断定）を誘発し、Repair -> Rejudgeが
   同一Main Modelで完結すること（新しいModelのLoadが発生しないこと）を確認する。
4. Selene／Qwen3Guardの実Artifact配線（P9-1-A-WU-005）はReal Artifact Authorityが
   本Sessionに無いため未実行。User側でArtifactの存在・配置を確認できる場合、次の
   Executor TaskへReal Artifact Authorityとして明示的に付与することを推奨する。
```

## 12. Exact Next Action

```text
Codex Controller Independent Review待ちで停止する。
最大Claimは P9_1_COMPLETE_CANDIDATE_FOR_CONTROLLER_REVIEW。
Phase 9-2、Roadmap、Phase 9 Closureのいずれも主張していない。
Acceptance Matrix、Unresolved Registryは変更していない――Controller確認後の更新に委ねる。
Codex ControllerのReview完了後、User実画面での§11 Manual Gate確認が必要。
```

本ファイル確定後のSHA-512は、Task完了報告の本文（本文外）でCodex Controllerへ提示する。

Return後は本Handoffの通り停止する。
