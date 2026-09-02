# Phase 9-1 全Judge実用不成立／再開順序 未解決Snapshot

```yaml
document_id: phase_9_1_all_judge_operational_failure_and_rework_order_snapshot_20260902103228
document_type: append_only_unresolved_reclassification_snapshot
document_state: historical_snapshot
language: ja
recorded_at: 2026-09-02 10:32:28 JST
source_current_registry: ../../未解決/current_unresolved_findings_registry_ja.md
decision_authority: user
authority_owner: Nazuna Research
phase: phase_9
program: phase_9_1
phase_9_1_closure: false
```

## 1. Trigger

2026-09-02のUser実画面再確認で、Main-shared Qwen JudgeとBuilt-in Deterministic Judgeの双方が実用可能な判定を返さなかった。

前日のSelene `unavailable／evaluated 0`を含め、現時点でPhase 9-1のSemantic Judge経路はProvider横断で実用不成立である。

## 2. Observed State

| Provider | Runtime State | Direct Result | Operational Disposition |
|---|---|---|---|
| Main-shared Qwen | Configured／Active／Executed一致 | `malformed_output` | FAIL |
| Built-in Deterministic | completed | evaluated 0／not_applicable 32／deferred 77 | NOT OPERATIONALLY APPLICABLE |
| Selene | prior Active表示 | unavailable／evaluated 0 | FAIL |
| Qwen3Guard | ON／OFFでJudge結果不変 | basic Guard baselineは別途PASS | Judge原因から分離 |

## 3. Reclassification

- UF-P9-002：Selene単体またはPC負荷だけでなく、Main-sharedと共通Role Lifecycleを含むP0へ維持。
- UF-P9-003：軽量Judge候補を将来予約から、Quota回復後の次Package入口へ昇格。
- UF-P9-004：Main Runtime Governance ENFORCEはJudge成立後の必須P0として維持。
- UF-P9-007：全Judge実用不成立と共通Judge基盤回帰仮説を新規P0として追加。

## 4. Causal Boundary

三Providerの直接Failureは一致していないため、同一Root Causeとは断定しない。

次を共有経路として横断診断する。

- Criteria Selection
- Semantic Snapshot
- Prompt Build
- Inference Result
- Strict Decode
- Result Projection
- Recording Correlation
- Role Load／Lease／Unload
- Mode Transition／Cancellation／Deadline

Built-inのSemantic能力不足、Main-sharedの構造化出力失敗、SeleneのRuntime／Resource問題は個別差分として残り得る。

## 5. Frozen Rework Order

```text
軽量Judge候補選定／取得
→ 四Provider同一条件Matrix
→ 共通Judge基盤修復
→ Provider固有修復
→ Judge OBSERVE／ENFORCE
→ Judge→Repair→Rejudge
→ Semantic 109 Budget内実評価
→ ARGD／DAGDを含むMain Runtime Governance ENFORCE
→ User Mac Manual
```

## 6. Current Decision

- AI利用可能量回復前は実装、Model取得または追加Manualを開始しない。
- 軽量Judge追加はSelene／Main-shared修復の代替ではない。
- Qwen3Guardの基本PASSをJudge PASSまたはGD系ENFORCE PASSへ読み替えない。
- Judge問題の解決前にMain Runtime Governance ENFORCEへ進まない。
- Phase 9-1は`FAIL／REWORK REQUIRED／NOT CLOSED`を維持する。

詳細Evidence：

`docs/project/phases/phase_9/history/operations/phase_9_1_all_judge_operational_failure_common_substrate_hypothesis_and_rework_order_ja_20260902103228.md`
