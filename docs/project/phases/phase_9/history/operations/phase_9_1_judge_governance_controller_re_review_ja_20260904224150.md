# Phase 9-1 Judge／Governance — Controller再Review

```yaml
document_id: phase_9_1_judge_governance_controller_re_review_20260904224150
document_type: controller_independent_re_review
recorded_at: 2026-09-04 22:41:50 JST
language: ja
decision: changes_required
maximum_claim: P9_1_REWORK_INCOMPLETE_FOR_CONTROLLER_REVIEW
real_model_run_by_reviewer: false
source_mutation_by_reviewer: false
append_only: true
```

## 1. 対象と受理範囲

[Claudeの新規Return](../../handoffs/phase_9_claude_p9_1_judge_and_governance_rework_controller_review_response_exact_return_ja_20260904223155.md)を対象とする。指定された22:15版との内容差を確認し、上書き旧内容の復旧・鑑識には進まない（User決定）。[前回Review](phase_9_1_judge_governance_rework_controller_review_ja_20260904191646.md)の全履歴再調査ではなく、修正箇所と直接の境界を確認した。

- **IR-01受理**：切断した後続JSONと未完外側Objectの内側だけを拾う2条件はTyped Failureへ修正され、Regressionがある。
- **IR-02の欠落修正を受理**：Frozen Criterion定義・期待IDがRejudgeへ渡る。Criterion結果なしの汎用acceptを拒否するRegressionがある。ただし複数Criterion時の予算問題は下記に残る。
- **IR-03一部受理**：実Compiler由来の1件、Main Context 16384、Hookで修復・採用を必須Assertionにした点は改善。ControllerがModelをFixture、Repairを必ず拒否する関数へメモリ上で差し替えると、今回のHook Testは期待どおりAssertionで失敗した。以前の誤ったPASSは解消。
- **WU-05の親App検証を受理**：追加4件を含むFrontend全327件がPASS。成功時の直接可用化、拒否時の非可用維持、取得失敗、古い応答の巻き戻し防止を確認。手動Browser Acceptanceとは区別する。
- **Seleneは未解決**：原因の過大断定を訂正したことは確認。Main同時Loadが障害の必要条件だと一般化せず、今回の比較条件で差が出たという範囲に留める。

## 2. P1／IR-R2-01 — Rejudgeの予算配分と分岐不一致

対象：[repair_live_integration.py](../../../../../../src/margpa_runtime_llm/bootstrap/repair_live_integration.py)の`_rejudge_max_new_tokens()`、`LIVE_REPAIR_BUDGET`、RejudgeのCancellation有無の2分岐。

Criterion数×150で上限を決める新処理は、総追加Token予算2000と残量を考慮しない。32件では4800を要求する一方、Cancellationなしの分岐は古い固定200のまま。今回の新しい複数Criterion対応が、分岐によって一致していない。

Controllerは32件の合成CriterionとProductionの`attempt_live_repair()`を使い、ModelだけをFixtureとして実行した（実Load 0）。

| 条件 | Repair／Rejudgeへ渡された上限 | 結果 |
|---|---|---|
| Cancellationあり | 400／4800 | 上限が総予算2000を超えている |
| Cancellationなし | 400／200 | 同じCriterion集合でも旧上限へ戻る |
| Cancellationあり、合成UsageをRepair 5＋Rejudge 2100とする | 400／4800 | 2105を消費した後に`repair_budget_exceeded_after_rejudge`でReject |

合成Usageは実Tokenizer測定ではない。通常の32件が必ず失敗するという証明ではなく、実行前に予算内へ制限せず、消費後の棄却だけになっていることの再現である。1 Criterionの実機成功ではこの問題を検証できない。

修正条件：Cancellation有無で同じ計画を使い、入力Context・出力上限・残Token・Deadline／Call予算の範囲でRejudgeを組み立てる。既存Planner等の再利用を優先し、予算を黙って増やしたり、必要なCriterionを落として成功化したりしない。実行不能は呼出し前にTypedな未成立として扱う。通常件数の正経路も有界条件で示す。

## 3. P2／IR-R2-02 — 保存Testは通常ENFORCE経路の代わりになっていない

対象：[実機Smokeの保存Test](../../../../../../tests/integration/test_real_local_main_governance_origin_repair_smoke.py)の`test_a_real_main_governance_origin_repair_persists_a_derived_turn_through_the_normal_conversation_save_path()`。

このTestはExecutorを直接呼び、`persist_accepted_attempt=True`で新しいREPAIR起源Turnを作る。一方、[Conversationの通常ENFORCE経路](../../../../../../src/margpa_runtime_llm/modules/conversation/application/conversation_generation.py)は`enforce_presented_final=True`でHookを呼び、[Dispatch](../../../../../../src/margpa_runtime_llm/bootstrap/judge_live_integration.py)は`persist_accepted_attempt=False`を渡し、同一Turnの最終回答を置き換える。二つの別経路を確認しただけでは、通常ConversationでMain起点Repairが同一Turnへ保存されることの結合検証にはならない。

加えて保存Testは修復不成立をSKIPする経路を残す。今回2 PASSというClaudeの報告は保持するが、将来の回帰検出力とは別である。実Modelを反復する前に、ProductionのConversation→Hook→Repair→Rejudge→同一Turn保存をFixture Modelで通し、修復失敗・古い回答の保存・重複Turn生成を確実に検出するTestを追加する。

## 4. Gemma成立とSelene先送りの条件

Userは「追加の有界調査でもSeleneが難しければ、Gemmaが正常に使え、後工程へ支障がないことを条件にSeleneを先送りする」と承認した。旧来のSelene必須条件を無条件に維持するのでも、今回直ちに解除するのでもない。

今回Returnの実機正経路はMain-self Qwen・1 Criterionであり、Gemma実機成立の報告はない。次は共通基盤の残件を解消した上で、通常構成のMain＋GemmaによるOBSERVE／ENFORCE、Repair→同条件Rejudge→最終採用、Main Governance ENFORCEを確認する。後工程がSelene固有機能に依存しないことも有界に照合する。

条件が揃えばSeleneの登録・再調査入口と未解決記録を残して延期できる。延期は「Seleneも完成」ではなく、User判断による完了条件の変更として明示する。Gemmaの未成立をMain-selfやFixture成功で代用しない。

## 5. 今回の検証・運用補強

- Backend Focused：Decoder／Selene／Judge Hook／Dispatch／Repair／Semantic Runtime／Feature Modes Route、**176 passed / 6.65s**。
- Frontend既定`npm test -- --reporter=dot`：**33 files / 327 passed / 5.09s**。
- 変更対象PythonのRuff：PASS。全Backend／Mypy／Build／実Modelは今回再実行していない。43 Mypy errors等はClaude報告と前回Controller結果を区別して保持する。
- Hookの強制Repair拒否Probeは期待するAssertion Failure。32件予算Probeは上記の不一致を再現。Source／Testは変更していない。
- [Claude運用Contract §14](../../../../shared/task_roles/claude_side_implementation_internal_review_rework_loop_operating_contract_ja.md)へ、Return作成・存在確認・Index連結・最終Path提示と、既存Handoff／Return／Historyの上書き禁止を短く追記した。次回指示にも反映する。
- 上書き旧内容の復元、新たなIncident長文、Git mutation、実装再開、Phase Closureは行っていない。追加の文書は本Reviewのみ。
