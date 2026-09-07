# Phase 9-1 — Component完全疎結合 R4 Return Controller独立Review

```yaml
document_type: controller_independent_review
document_state: changes_required
recorded_at: 2026-09-06 00:02:48 JST
language: ja
reviewer_role: codex_controller
review_target: ../../handoffs/phase_9_claude_component_independence_r4_convergence_rework_exact_return_ja_20260905232353.md
maximum_claim: P9_1_COMPONENT_INDEPENDENCE_R4_NARROW_FINAL_CHANGES_REQUIRED
phase_9_1_closure: false
real_model_action_by_controller: none
controller_focused_verification: 69_passed
git_mutation: none
append_only: true
```

## 1. 判定

`CHANGES REQUIRED / narrow final micro-rework`。

R4でRequest-local Ledger、Identity三経路、Cancellation Arbitration、Gemma Compact Schemaおよび実Golden Pathは大きく収束した。全面Rollbackや追加設計は不要である。ただし、UI向けLatest Current Pointerが古いrequestへ巻き戻る競合が一つ残り、Golden Path TestのHard AssertもHandoff要求を直接固定し切っていない。Phase 9-1 ClosureまたはUser実画面Acceptanceへ進む前に、この二点だけを閉じる。

Controllerは実Modelを再実行せず、対象Unit／Fixture 69件を実行して全件PASSを確認した。

## 2. 受理する結果

- R4-WU-02：Built-in、Main-shared、Dedicated Gemmaの保存Evidence Identity Matrixは、各経路で直接Assertされている。
- R4-WU-03：Worker通常FailureとUser Stop／Main-priority Preemptionの競合は、Cancellation起源を優先する固定Schedule Testで成立している。
- R4-WU-04：Gemma専用Criterion Schemaを三Fieldへ縮小し、共有Decoder、Selene、Main-sharedへ波及させていない。
- R4-WU-04実機Evidence：Compact Schemaを使う意図的Deviation条件で2/2 TrialがStrict Decode、全32 ID、同一出力を成立させたEvidenceは受理する。
- R4-WU-05実機Evidence：一回のProduction Root Golden Pathで`completed`、Main Governance起点Repair、`improved`、採用、同一Turn保存が成立したEvidenceは、一回分の成功として受理する。
- `criteria_evaluated=31`または`30`は直ちに欠陥ではない。現契約では`evaluated=passed+deviated`であり、Decode済み32件中の`unknown`はevaluatedへ含まれない。Count保存則をTestで明示すればよい。

## 3. IR-R4-01 — idempotent再BeginでCurrent Pointerが巻き戻る

`SemanticRuntimeCoordinator.begin()`は、既存`request_id`を見つけた場合にも次を実行する。

```python
self._latest_request_id = request_id
self._turns.move_to_end(request_id)
```

このため次のScheduleで、Bが最新の新規TurnであるにもかかわらずCurrent表示がAへ戻る。

```text
A begin（generation 1）
B begin（generation 2、Current=B）
A begin再入（既存Snapshotのidempotent read）
Current=A  ← 誤り
```

同一request再入は新しいTurn開始ではない。既存Snapshotを返すだけにし、Latest Current Pointerと保持順序を変更してはならない。これはR4 Handoffの「UI向けLatest Current Pointerと実Turn Ledgerの分離」「BのCurrent表示へ混入させない」に対する残差である。

また、現在のCommentはFIFOと説明するが、`move_to_end()`があるため実際は再Hit可能なLRU挙動になる。上記修正により説明と実装を一致させる。

## 4. IR-R4-02 — Golden Path Oracleを要求どおり固定する

実機Golden Path Testは`repair_accepted=True`等をAssertするが、R4 Handoffが要求した次の最終状態を直接Assertしていない。

- `repair_outcome == "improved"`
- `presentation_outcome == "repair_accepted"`
- `candidate_withheld is True`
- `repair_rejudge_provider == Gemma`
- Rejudgeが同一32 Criterionを要求すること
- Count保存則（selected 32と、evaluated／unknown等の整合）

Fixture Production Root TestはRejudge Prompt内の同一32 IDを直接確認しているため、その契約は受理する。実機Testにも観測可能な上記FieldをHard Assertし、`repair_accepted`だけから暗黙推定しない。Production SourceやEvidence Schemaへ新Fieldを増やす必要はない。

## 5. Claim境界

「GemmaのMalformed JSON Defectを一般に根絶」は広すぎる。受理できるClaimは次である。

> Gemma専用Compact Criterion Schemaを用いた、今回の32 Criterion All-Accept／Deviation／Production Golden Pathでは、既知のMalformed JSON再現経路が解消した。

別内容、別長、将来Schemaまたは長期反復まで含む一般保証ではない。Provider局所で`reason_code`／`evidence_refs`を省略したため、Criterion単位の詳細Evidenceが減るTrade-offも残る。ただしOverall reasoningとDispositionは保持され、MVPの局所対策としては受理する。

## 6. Disposition

[R5 Final Micro-rework Exact Handoff](../../handoffs/phase_9_controller_component_independence_r5_final_micro_rework_exact_handoff_ja_20260906000248.md)だけを次に実行する。Selene、Retry、Budget／Context変更、Phase 9-2／9-3、Phase 10、Git操作へは進まない。
