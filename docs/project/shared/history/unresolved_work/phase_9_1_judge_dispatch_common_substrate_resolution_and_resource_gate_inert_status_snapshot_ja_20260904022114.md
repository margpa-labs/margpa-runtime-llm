# Phase 9-1 Judge Dispatch共通基盤解決／Resource Gate不発状況確認 未解決Snapshot

```yaml
document_id: phase_9_1_judge_dispatch_common_substrate_resolution_and_resource_gate_inert_status_snapshot_20260904022114
document_type: append_only_unresolved_reclassification_snapshot
document_state: historical_snapshot
language: ja
recorded_at: 2026-09-04 02:21:14 JST
source_current_registry: ../../unresolved_work/current_unresolved_findings_registry_ja.md
decision_authority: user
authority_owner: Nazuna Research
phase: phase_9
program: phase_9_1
phase_9_1_closure: false
supersedes_rework_order: phase_9_1_all_judge_operational_failure_and_rework_order_snapshot_ja_20260902103228.md
```

## 1. Trigger

前Snapshot(`phase_9_1_all_judge_operational_failure_and_rework_order_snapshot_ja_20260902103228.md`)が凍結した「共通Judge基盤修復」ステップが、2026-09-03のUser指示による3視点独立調査(静的Lock/Exception経路監査／実機Main+Judge同時Load再現／Production配線＋Git履歴Provenance監査)により、実機再現込みで根本原因確定・修正まで完了した。あわせて2026-09-04、Userの依頼によりPackage 2残Open Finding(OF-P2-005/006/007)の現況をSource(`git diff`)から直接確認した。本Snapshotはこれらの結果によるRegistry再分類を記録する。

## 2. Root Cause(確定)

共有Engine`SeleneSemanticEvaluator._plan_batches()`(P9-1 Package 2で新規追加)が、各BatchのGenerate呼び出し"前"に`count_chat_prompt_tokens()`を同期呼出しし、これが`LlamaCppModelAdapter._generation_lock`を非ブロッキング取得していた。先行Judge Turnの取り残しBackground Thread(`run_tracked_stage()`の意図された"Late Complete"設計)がLockを握ったままだと、後続Turnのこの事前Lock Checkが即座に`InferenceError(MODEL_BUSY)`で失敗し、表示Category「unavailable」へ収束していた。SeleneとGemmaが同一症状を示していたのは、両者が文字通り同一のAdapter/Evaluator Codeを共有していたため(Provider固有問題ではない)。

対処: Round 1でTokenize系(`count_text_tokens`/`count_chat_prompt_tokens`)から`_generation_lock`要求自体を除去(読み取り専用操作のため安全)。Round 3で、これとは別の正当なBusy衝突(取り残しThreadが実際にまだGenerate中)へBounded Retry(最大3回、Delay 3.0/6.0/12.0秒、User承認済み・再検討不要)を追加。Round 3(Dedicated Selene/Gemma経路)・Round 4(Main-shared経路)とも実機で成功確認済み。

詳細: `docs/project/phases/phase_9/history/operations/phase_9_1_judge_dispatch_unavailable_failure_root_cause_confirmed_three_angle_investigation_ja_20260903132314.md`

## 3. Reclassification

- **UF-P9-002**(Selene Judge unavailable／Main-shared Lifecycle不安定): `open P0` → `resolved`。根本原因確定・修正・実機確認済み。
- **UF-P9-007**(全Judge実用不成立と共通Judge基盤回帰仮説): `open P0` → `resolved`。仮説どおり共通基盤の単一Root Causeだったことが確定した。Built-in Deterministicの`evaluated 0`のみ、Bugではなく設計どおりの挙動として本Findingから分離。
- **UF-P9-004**(Main Runtime Governance Semantic ENFORCE未成立): `open P0` → `P1(User Manual再確認待ち)`。Semantic全件Deferredの技術的Blockerは除去された(Main-shared経路で実機32件全Criteria評価成功を確認)が、Judge→Repair→Rejudgeを含む全体ENFORCE Golden PathのUser Manual再確認はまだ済んでいないため、`resolved`へは変更しない。
- **新規UF-P9-008**(stage_deadline Timer競合による誤分類、Round 4 Open Finding 7): 現Production Budget(120秒)がRetry Window最大(21秒)を大きく上回るため到達不能、P2で保留。
- **新規UF-P9-009**(close() Shutdown Timeout 10秒とRetry Window最大21秒の不整合、Round 4 Open Finding 8): 実際に再現可能な経路と確認したが、発生条件が狭く(Busy Retry待機中のServer停止のみ)、安全な修正には許容Shutdown待ち時間のTradeoff判断が要るため、数字を独断で決めずP2で保留。

## 4. OF-P2-005／006／007 現況確認(Package 2残Open Finding、Phase 9 Index管理)

`git diff`でWeb Application(`src/margpa_runtime_llm/bootstrap/web_application.py`)の現在の未commit差分を直接確認した結果、SSS級Incident後の復旧(`SystemMemoryRoleResourceGate`のProduction配線除去、`AllowAllRoleResourceGate`への復帰)により、OF-P2-005(逆方向Gate未実装)・OF-P2-006(Main Active時Gemma拒否)・OF-P2-007(DeepSeek8B時Qwen3Guard拒否)が依拠するGate自体が、現在Production配線から外れていることを確認した。3件とも**現在は不発(inert)**である。

より重要な生きているRisk: Gate除去の直接的な副作用として、OF-P2-003が本来防止対象としていた「Main+Selene同時LoadによるMain実Crash」への保護が、現在また無防備な状態に戻っている(2026-09-01の実Incidentと同一条件)。Resource Gate SubsystemはSSS級Incidentを起こしたのと同一のものであるため、User明示の再着手判断なしにClaude側からは一切変更しない。

## 5. Current Decision

- Judge Dispatch共通基盤の修復により、「共通Judge基盤修復」から始まる前Snapshotの凍結Rework Orderは、この最初のステップを完了したと見なす。
- Full Golden Path(Judge→Repair→Rejudge→Main ENFORCE)のUser Manual再確認は、まだUserが実施していない次のStepとして残す。
- UF-P9-008／009、OF-P2-005/006/007のいずれも、現時点でPhase 9-1 Closureを止めない(P2、非Blocking)。
- Resource Gate Subsystemの再設計・再配線は、User明示の指示があるまで一切着手しない。

詳細Evidence(Round 1-4全体)：

- `docs/project/phases/phase_9/history/operations/phase_9_1_judge_dispatch_unavailable_failure_root_cause_confirmed_three_angle_investigation_ja_20260903132314.md`
- `docs/project/phases/phase_9/handoffs/phase_9_claude_judge_dispatch_unavailable_fix_round1_self_review_exact_return_ja_20260903135915.md`
- `docs/project/phases/phase_9/handoffs/phase_9_claude_judge_dispatch_unavailable_fix_round2_self_review_and_docs_correction_addendum_ja_20260903162057.md`
- `docs/project/phases/phase_9/handoffs/phase_9_claude_judge_dispatch_unavailable_fix_round3_busy_retry_and_self_review_exact_return_ja_20260903185144.md`
- `docs/project/phases/phase_9/handoffs/phase_9_claude_judge_dispatch_unavailable_fix_round4_cumulative_self_review_exact_return_ja_20260903193427.md`
