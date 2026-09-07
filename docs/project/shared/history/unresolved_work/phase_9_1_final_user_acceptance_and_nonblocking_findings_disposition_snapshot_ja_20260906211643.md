# Phase 9-1最終User Acceptance／非Blocking未解決事項Disposition Snapshot

```yaml
document_id: phase_9_1_final_user_acceptance_and_nonblocking_findings_disposition_snapshot_20260906211643
document_type: append_only_unresolved_reclassification_snapshot
document_state: historical_snapshot
language: ja
recorded_at: 2026-09-06 21:16:43 JST
decision_authority: user
authority_owner: Nazuna Research
phase: phase_9
program: phase_9_1
phase_9_1_status: complete_user_accepted
phase_9_full_closure_performed: false
next_program: phase_9_2
source_current_registry: ../../unresolved_work/current_unresolved_findings_registry_ja.md
source_result: ../../../phases/phase_9/history/operations/phase_9_1_post_gemma_constrained_decoding_user_mac_final_recheck_lossless_result_ja_20260906205100.md
raw_evidence: ../../../phases/phase_9/history/operations/phase_9_1_post_gemma_constrained_decoding_user_mac_final_recheck_raw_report_ja_20260906205100.txt
append_only: true
```

## 1. User Decision

Userは最終実画面結果の確認後、Phase 9-1の必須Acceptanceと共通基盤が成立したと判断し、Phase 9-1を完了扱いとした。通常Full Closure作業は挟まず、Phase 9-2へ通常進行する。

成立範囲は、Gemmaを独立Judgeに使った次の機械的経路である。

- Main Governance OFFでのJudge単独OBSERVE。
- Judge ENFORCE起点のRepair／Rejudge／採用。
- Main Governance ENFORCE起点のRepair／Rejudge／採用。
- JudgeとMain Governanceの両方が要求する`Repair起点: judge_and_main`。
- 32 Criterion評価と109件Count保存。
- Recording、Provider Identity、Presented Final、Guard、OFF／Unload。

Gemma Judge Runは実行到達8件中8件が`completed`であり、修正前の`malformed_output`／`unavailable`は再発しなかった。

この完了は、全Providerの同品質、意味評価の正しさ、Phase 11以降のJudge非依存Structural Governanceまたは製品品質を意味しない。

## 2. Resolved Reclassification

### UF-P9-003

Gemma 4 E2Bを軽量独立Judgeとして取得・統合し、Constrained Decoding後のUser Mac実画面で代表Golden Pathが成立したため解決済みとする。Seleneは別の保留事項として残す。

### UF-P9-004

現行Semantic LayerのMain Runtime Governance ENFORCEは、`Repair起点: main_governance`および`judge_and_main`を含むUser Mac実画面Golden Pathが成立したため解決済みとする。将来Structural Layerは本解決へ含めない。

### UF-UI-017

Judge準備後、Main GovernanceをOBSERVE経由なしでOFFから直接ENFORCEへ変更できたため解決済みとする。

## 3. New／Maintained Non-blocking Findings

### UF-P9-010 — Qwen Self Judge Repair非収束

Qwen Self Judgeは判定・Criterion評価まで動作するが、Deviationを検出した3 TurnでRepair採用0/3だった。共通基盤Failureではなく代替Provider品質の未解決とする。

### UF-P9-011 — Qwen Main＋DeepSeek Judge組合せ

`main_model_mismatch_requires_main_switch`でLoad前に拒否され、DeepSeekの実Load／Inferenceには到達しなかった。Provider組合せ契約の未解決とする。

### UF-P9-012 — Guard過敏性

Qwen3Guardは明確なPrompt Injectionを正しくBlockする一方、正当な矛盾検証文もBlockした。Runtime成立と分類品質を分離し、False Positiveとして追跡する。

### UF-P9-013 — 意味的False Improvement

Qwenの誤答をGemmaが受理し、User訂正後も意味的に改善していないRepairを`improved`として採用した。機械的経路は成立しており、Model／Prompt／Criterion／Evidence／成功判定品質の残件とする。暫定Model交換を見込むためPhase 9-1へ戻さない。

### UF-P9-014 — 16GB環境の性能制約

Judge単独で約1分、Repair込みで約2〜3分かかり、終盤に物理16GB、使用15.39GB、Swap 1.64GB、圧縮2.22GBを観測した。複数Batch／Repair／Rejudgeの直列CostとLocal Hardware制約の複合であり、単一画像からMemory Leakとは断定しない。

### UF-UI-018 — Guard後のJudge Current表示

Guardが入力段階でShort-circuitしたTurnではJudgeを実行しないが、Judge Panelは直前Turnの結果をCurrentらしく保持する。Current／Historical／Not RunのUI Projection残件とする。

## 4. Routing

```text
Phase 9-1へ戻さない:
  UF-P9-010／011／012／013／014、UF-UI-018

Phase 9-2の比較Evidence候補:
  Guard False Positive、Human vs Judge、False Improvement、Provider差、Latency

Phase 10 UI候補:
  Guard Short-circuit後のCurrent／Historical／Not Run表示

将来Provider／Hardware候補:
  Qwen Repair品質、DeepSeek Role独立化、Local性能
```

これらは未解決であるが、Phase 9-1完了を取り消すClosure Blockerではない。
