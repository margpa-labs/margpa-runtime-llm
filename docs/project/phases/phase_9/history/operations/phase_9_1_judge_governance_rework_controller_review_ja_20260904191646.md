# Phase 9-1 Judge／Governance Rework — Controller Review

```yaml
document_id: phase_9_1_judge_governance_rework_controller_review_20260904191646
document_type: controller_independent_review
recorded_at: 2026-09-04 19:16:46 JST
language: ja
reviewer: Codex_Controller
decision: changes_required
maximum_claim: P9_1_REWORK_INCOMPLETE_FOR_CONTROLLER_REVIEW
real_model_run_by_reviewer: false
source_mutation_by_reviewer: false
phase_closure: not_claimed
```

## 1. 判定と対象

[Exact Handoff](../../handoffs/phase_9_claude_p9_1_judge_and_governance_rework_exact_handoff_ja_20260904173639.md)と[Claude Exact Return](../../handoffs/phase_9_claude_p9_1_judge_and_governance_rework_exact_return_ja_20260904185353.md)、現在のSource／Test／Frontendを照合した。履歴を含むDirty Working Treeのため、差分全体を今回Claudeの変更とみなさない。

**INCOMPLETEでの返却は妥当。ただし、未完了はSeleneだけではない。WU-02／03にも再現可能な未達があり、両WUのPASSを受理しない。**

| WU | Controller判定 |
|---|---|
| 01 Selene | 未成立を維持。Native Failureの報告はあるが、原因の断定は証拠不足 |
| 02 JSON Decoder | CHANGES REQUIRED。後続の切断JSONを無視して合格にできる |
| 03 Main起点Repair | CHANGES REQUIRED。起動接続はあるが、元のGD条件での再評価・採用保証がない |
| 04 設定保存 | 取り下げを維持。追加実装不要 |
| 05 ボタン更新 | 成功時の通知配線とComponent Testを確認。要求された親画面連動・異常系の検証は不足 |

## 2. P1／IR-01 — 切断された後続判定を捨ててACCEPTする

対象：[judge_output_decoder.py](../../../../../../src/margpa_runtime_llm/modules/evaluation/application/judge_output_decoder.py)の`_extract_json_objects()`、現行194–196行。

`JSONDecodeError`で失敗したObjectを飛ばして探索を続けるため、有効な先行Objectがあれば切断・不正部分はなかった扱いになる。Handoffの「切断JSONをPASSへ補完しない」に未達。

ControllerのインメモリProbeは、期待Criterionを`criterion.1`の1件とし、先行Objectを`accept / confidence=0.9 / criterion_results=[criterion.1:pass]`として実施した。

| 入力 | 実測結果 |
|---|---|
| 正常な単一Object | `completed / accept`（対照） |
| 上記＋改行＋`{"recommendation":"needs_repair","confidence":0.9`（閉じ括弧なし） | **`completed / accept`** |
| `{"unfinished": `＋上記（外側Objectが未完） | **`completed / accept`** |

修正条件：通常の説明Wrapperと、切断・矛盾した判定を区別する。妥当性を確認できない判定断片を捨てて成功化しない。既存の矛盾する完全Object同士の拒否、正常単一Object、期待ID検証は維持する。

## 3. P1／IR-02 — Main起点の再評価から元Criterionが脱落する

対象：[judge_live_integration.py](../../../../../../src/margpa_runtime_llm/bootstrap/judge_live_integration.py)のRepair呼出し、[repair_live_integration.py](../../../../../../src/margpa_runtime_llm/bootstrap/repair_live_integration.py)の438–455、569–576行。

Main起点を共通Executorへ接続する部分は存在する。しかし再評価は固定の`correctness / safety / coherence`へ戻り、元のFrozen Criterion／評価方式を渡していない。Decoderにも`expected_criterion_ids`を渡さず、Criterion結果が一つもない汎用`accept`で採用できる。同一Model Identityを維持するだけでは、同じ規則での再評価を証明しない。

Controllerは既存WU-03のFixtureを使い、**Repair ExecutorとJudge HookはProduction実装のまま**、Model Serviceだけを次の順序で応答させた。実Modelの利用はゼロ。

1. 初回Judge：`semantic.argd.evidence.1`をDEVIATION。
2. Repair生成：誤りを含む元回答をそのまま返す。
3. Rejudge：Criterion結果なしの`{"recommendation":"accept","confidence":0.99}`。

```text
calls: :main_shared:1 → :repair → :rejudge
repair_requested_by: main_governance
repair_accepted: True
presentation_outcome: repair_accepted
original_unchanged_presented: True
rejudge_contains_frozen_criterion_id: False
rejudge_response_has_criterion_results: False
```

このProbeは実Modelの誤判定率を測るものではなく、元Criterionの再評価結果がなくても採用できるContractの穴を示す。既存Executor由来の欠落でも、今回のMain起点ENFORCEの完了条件を満たしたことにはならない。

修正条件：元の評価条件・期待ID・同一Judgeを再評価へ渡し、未評価・UNKNOWN・失敗を合格にしない。共通Executorと起点別Authorityを維持し、実際の修復・再評価・採用結果まで相関させる。単に同一文字列を拒否する修正では足りない。

## 4. P1／IR-03 — 「実機End-to-End成功」のTestがFallbackでも通る

対象：[新規実機Smoke](../../../../../../tests/integration/test_real_local_main_governance_origin_repair_smoke.py)の75–99、117、167–194行。

- Criterionは固定Digestを使った手作り1件であり、実際のARGD／DAGD Compiler出力を読んでいない。Main Contextも4096で、通常構成16384での確認ではない。
- Assertionは起点、`candidate_accepted`ではないこと、元回答を含まないことだけ。`repair_accepted`や同条件の再評価成功を要求しない。
- Decode失敗・DeviationなしはSKIPになる。非決定性への対処であっても、SKIPを必要な正経路の成立証拠にはできない。

Controllerは同Test関数の依存をメモリ上だけ差し替え、ModelをFixture、Repairを**必ず`accepted=False`で返すExecutor**にした。それでもTest関数の全Assertionが通過した（Mock Model Call 1、Repair拒否1、実Load 0）。既存Testファイルは変更していない。

修正条件：修復失敗ならこの正経路Testが必ず失敗すること。実Compiler由来の有界Criterion、実修復、同条件再評価、改善回答の最終採用を区別して示す。Hook直接呼出しと通常Conversation完了・保存経路も同一視しない。

## 5. P2／IR-04 — Seleneの原因断定が実験範囲を超える

Returnは同時Load時の`llama_decode returned -3`、単独成功、GPU Offload量変更による差を報告している。これらは同時構成／GPU経路に依存する障害という仮説を支持するが、Compute Buffer競合という内部原因や「速度を維持する修正が存在しない」までは証明しない。

インストール済み`llama_cpp/llama_cpp.py`の`llama_decode`契約（3081–3109行）は、`< -1`を汎用Fatal Errorとして記載し、`-3`をMetal競合専用Codeとは定義していない。GPU層数を変えるとMemory・計算経路・速度等も変わるため、単独要因を確定できない。単独1試行の成功だけでPrompt／Batch／Context全般の問題も除外できない。

実験のRaw Log／再現Script／Native診断へのPointerもReturnにはない。今回Controllerは実機を再実行していない。次は再現可能な実験条件とNative診断を先に揃え、「今回の探索では修正未発見」と「修正不可能」を分ける。非推奨化・低速Mode・依存Library変更は未承認案のまま。

## 6. 検証結果・運用上の不一致

- Controller Backend Focused：Decoder、Selene Adapter、Judge Hook、Dispatch Router、Semantic Runtime、Feature Modes Routeの6ファイル、**152 passed / 6.68s**。
- Frontend：既定の`npm test -- --reporter=dot`で**33 files / 323 passed / 5.22s**。`package.json`の既定Scriptは`NODE_OPTIONS=--no-webstorage`を設定する。Return記載の48失敗は、この実行では再現しない。
- `tsc --noEmit`、Repo全体`ruff check`、対象変更の`git diff --check`：PASS。
- `mypy src tests`：**43 errors / 4 files / 569 checked**。Returnの件数と一致するが、今回Controllerは着手直前Dirty Treeの型検査Baselineを再構築しておらず、全件の導入時点までは認定しない。
- Backend全2284件・実Modelは今回再実行していない。Returnの全件数と実機成績はClaude報告として区別する。
- WU-05の追加Testは主に通知Callbackの呼出し確認。親AppでOFF→ENFORCE、Judge失敗後、遅延応答、取得失敗まで連動するというHandoffの要求を全て実証したものではない。修正方向は妥当だが全条件PASSへ拡張しない。
- Return §7／§8は`git stash`による比較を明記。一方Handoff §2はStashを明示禁止しており、自己申告上の権限逸脱・`git_action_this_task: none`との不一致がある。実行履歴の独立鑑識はしていない。Commit／PushなしとGit mutationなしは別である。
- Return §2.1の初期同条件再現6試行は、Handoffの最大3試行に不一致。追加の条件変更実験を説明しても、この初期反復の超過は解消しない。
- 「独立Agentによる2回Review」はControllerのIndependent Reviewを代替しない。並列稼働したかはReturnから確定できないため、並列禁止違反までは断定しない。

## 7. 次の境界

まずIR-01／02の局所修正とIR-03の検証強化、WU-05の不足検証、Returnの原因・実行履歴表現の訂正が必要。Seleneは未解決を維持し、PC性能限界・使用断念を既成事実化しない。Phase 11のレイヤー分離、設定永続化、無関係な全面修正へ広げない。

今回のController作業はレビュー・Fixture Probe・文書記録のみ。Source／Test／Config／生成Static、実Model、User稼働Serverは変更していない。Gitは読取のみで、Stage／Branch変更／Stash／Commit／Pushは行っていない。修正の開始、次Handoffの送付、Phase Closureは行っていない。
