# Phase 9-1 — IR-R4 Return独立レビュー・最終Micro Rework

```yaml
document_id: phase_9_1_controller_ir_r4_return_review_and_final_micro_rework_20260905071833
document_type: controller_independent_review_and_delta_rework
document_state: changes_required
recorded_at: 2026-09-05 07:18:33 JST
language: ja
reviewer_role: codex_controller
maximum_claim: P9_1_REWORK_INCOMPLETE_FOR_CONTROLLER_REVIEW
phase_9_1_closure: false
real_model_action: none
source_test_mutation: none
git_mutation: none
append_only: true
```

対象：[IR-R4 Exact Return](../../handoffs/phase_9_claude_p9_1_controller_ir_r4_delta_rework_exact_return_ja_20260905030720.md)。前回の[IR-R3 Return Review](phase_9_1_controller_ir_r3_return_review_and_delta_rework_ja_20260905003507.md)からの差分だけを確認した。

## 1. 判定

**CHANGES REQUIRED／INCOMPLETEを維持するが、今回の主要修正とGemma実機正常化は受理する。残件は2件のMicro Reworkと、以前から残る通常32 Criterionの予算方針だけである。**

| 対象 | Controller判定 |
|---|---|
| Planner待機の有界化 | 受理。Event待機は期限で復帰し、Cancel後のRejudge Callも0になった |
| 26件のClaim訂正／21件境界 | 受理。Plan受理と実行成立が分離された |
| Main起点off／observe保存Test | 受理。重複せずパラメータ化された |
| Gemma Schema順序修正 | 受理。Decoderを緩和せず、修正後Promptと共有Schemaが整合する |
| Gemma実機5件 | Claude実行時の5 PASSを有効な実機Evidenceとして受理。ただしControllerは実モデルを再実行していない |
| Selene延期 | Provider非依存経路をGemmaで代替できる設計Evidenceがあるため、**延期候補として受理**。Selene解決／Phase 9-1 Closureとはしない |

## 2. IR-R5-01 — Planner Failureの分類が残る

`_plan_rejudge()`はCounter例外、Token／Context不足、Worker Registryのshutdown拒否を全て`None`へ変換する。呼出し元はDeadline／Cancelでなければ一律`repair_rejudge_budget_insufficient`を返す。

Controller Probeでは、`count_chat_prompt_tokens()`が`RuntimeError('counter_failed')`を送出する場合も、既にshutdownした`TrackedStageWorkerRegistry`が新規Workを拒否する場合もPlanは`None`になった。既存TestもCounter例外へ`repair_rejudge_budget_insufficient`を期待している。したがって、前回指示の「例外／Timeout／Cancelを単なるToken不足へ混同しない」はまだ未成立。

必要修正：Plan成功／Token・Context不足／Counter失敗／Deadline／Cancel／Registry shutdownを、最低限呼出し元がTypedな`rejected_reason`へ写せる形にする。成功PlanへのFallbackはせず、Rejudge Call 0と現在の有界待機を維持する。新規の大きなPlanner階層は不要。

## 3. IR-R5-02 — Judge起点Gemma Repair TestのOracle不足

`test_a_real_gemma_enforce_repair_run_uses_the_same_condition_rejudge_and_adopts_the_improved_answer()`は、Deviation後に次しかAssertしていない。

- Rejudge ProviderがGemma。
- `presentation_outcome != candidate_accepted`。
- 元の誤答が表示内容にない。

これはsafe fallbackでも成立するため、Test名とReturnが主張する「改善回答を採用」を直接証明しない。`repair_outcome == improved`、`repair_accepted is True`、`presentation_outcome == repair_accepted`、提示内容が非空かつ元回答と異なることをHard Assertする。実モデルがDeviationを返すかどうかの既存Skip境界より後は、Repair失敗をSkipへ変えない。

Main Governance起点Testは上記の強いAssertを既に持つため受理する。ただし関数名の「persists」は、`persistent=None`のHook直接Testでは永続保存を意味しない。既存Fixture Modelの保存経路Testと組み合わせた二層Evidenceとして説明するか、関数名を「presents／adopts」相当に訂正する。新たな実モデル永続化Testの追加までは要求しない。

## 4. Gemma／Selene／通常規模のDisposition

Gemma 4 E2Bは、1 Criterionの実機SmokeにおいてOBSERVE、ENFORCE accept、Judge起点Repair、Main Governance起点Repairの各経路へ到達した。これはGemma正常化の有力な成立Evidenceだが、Semantic 109全体や通常選択32件の成立を意味しない。

Seleneは未解決のまま、Gemmaを利用できる範囲で延期候補にする。Current Registry本体への確定反映は、上記Micro ReworkとUser Mac ManualでGemmaが実画面でも成立した後に行うのが安全である。

通常32件は`32×75=2400`だけで現在のRepair総Token予算2000を超えるため未成立。Criterion削減や係数の再縮小で閉じない。予算／Call上限を変更する場合は、実測根拠・Context・待ち時間を含む最小案を提示し、User判断を待つ。

今回相談した不正JSON限定リトライは本Returnで未実装であり、[別の保留候補](../../../../shared/history/planned_work/bounded_judge_json_retry_evaluation_and_reuse_reservation_ja_20260905011625.md)のまま。今回のSchema順序修正が実機で効いているため、Phase 9-1へ無条件で追加しない。

## 5. Controller Verificationと次の停止線

- Focused Pytest：**170 passed／5 deselected（6.70s）**。5 deselectedは実モデルSmokeで、Controllerは再実行していない。
- 対象8 File Ruff：PASS。対象8 File Mypy：既存`judge_live_integration.py`の1件だけ。Claude報告のFull 2316 PASS／実機Gemma 5 PASS／全体Mypy 43件は保持する。
- Planner Probe：Counter例外とRegistry shutdown拒否がともに`None`へ収束することを確認。すべてFixture／メモリ内で、実Model、Network、Browser、User永続データ、Git操作なし。

次はIR-R5-01／02だけを直し、対象Testと規定の異なる観点2回のInternal Reviewを行う。受理済みのGemma修正を再設計しない。実モデル再試行は、Oracle強化後のJudge起点Repair 1回を上限とし、Main Governance等4件を無目的に再実行しない。新規PathのExact Return／Recoveryを作って停止する。

Budget拡大、Criterion削減、Decoder緩和、JSON限定リトライ、Native更新、Download、新Resource Gate、Selene追加試行、Phase 9-2／9-3、Git変更は禁止。過去Handoff／Historyを上書きしない。
