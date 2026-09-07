# Phase 9-1 — Component完全疎結合 R5 Final Micro-rework Exact Handoff

```yaml
document_type: exact_implementation_handoff
document_state: ready
recorded_at: 2026-09-06 00:02:48 JST
language: ja
from: codex_controller
to: claude_designer_implementer
decision_authority: user
authority_owner: Nazuna Research
in_response_to: phase_9_claude_component_independence_r4_convergence_rework_exact_return_ja_20260905232353.md
review: ../history/operations/phase_9_1_component_independence_r4_return_controller_review_ja_20260906000248.md
maximum_claim: P9_1_COMPONENT_INDEPENDENCE_R5_FINAL_MICRO_REWORK_READY
phase_9_1_closure: false
git_action: prohibited
append_only: true
```

## 1. 目的

R4をRollbackしない。Controller Reviewの二残差だけを局所修正し、Component完全疎結合ReworkをUser実画面確認へ渡せる状態にする。

## 2. R5-WU-01 — Latest Current Pointer再巻き戻りの除去

`SemanticRuntimeCoordinator.begin()`が既存`request_id`を見つけた場合は、その既存Snapshotを返すだけにする。

- `_latest_request_id`を更新しない。
- `_turns.move_to_end(request_id)`を行わない。
- generation、digest、rotation cursorを変更しない。
- 新規requestの初回Begin時だけLatest Current Pointerを更新する。
- 既存のBound 128と、Evidence／criterion-key同時Evictionは維持する。

次をUnit Test化する。

```text
A begin
B begin
A begin再入
=> Aは同一generation／digest
=> CurrentはBのまま
=> Aの遅延Evidence記録後もCurrent／Latest EvidenceはBへ誤混入しない
```

加えて129個の異なるrequestをBeginし、LedgerがBoundを超えず、最古EntryがFIFOでEvictされ、最新Pointerが最新の新規requestを維持することを確認する。Sabotageで既存request再入時のPointer更新を戻すと新規Testが失敗することを示す。

## 3. R5-WU-02 — Golden Path Oracle補完

Fixture Production Root Testと実機Golden Path Testの観測可能な結果へ、少なくとも次のHard Assertを追加する。

```text
repair_outcome == improved
repair_accepted is True
presentation_outcome == repair_accepted
candidate_withheld is True
repair_requested_by == main_governance
repair_rejudge_provider == Gemma
criteria_selected == 32
criteria_evaluated + criteria_unknown + criteria_not_applicable == 32
criteria_evaluated + criteria_unknown + criteria_not_applicable + criteria_deferred == 109
```

Fixtureでは既存どおり、初回とRejudge Promptが同一32 Criterion ID集合であることを直接Assertする。実機ではProduction SourceへTest専用Fieldを追加せず、上記公開Result、Presented Final、同一Turn保存、Judge EvidenceをHard Assertする。

実機Golden Pathの再実行は最大1 Trial。Missing Artifact以外をSKIPしない。既存R4実機Evidenceを否定するためではなく、強化後Oracleが同じProduction経路で成立するかだけを確認する。

## 4. R5-WU-03 — Claim訂正と確認

Returnでは、Gemma一般のJSON Defect根絶を主張しない。次のBounded Claimへ限定する。

```text
Compact Criterion Schemaを使う既知の32 Criterion
All-Accept／Deviation／Production Golden Pathで、
既知のMalformed再現経路が解消した。
```

`criteria_evaluated=31/30`は、残りが`unknown`としてCount保存則を満たすなら正常挙動と記録する。保存則を満たさない場合だけ新規Findingとして停止する。

## 5. Verification

- 新規／変更Focused UnitとFixture Production Root Test。
- Backend非Model Full Suite。
- Ruff。
- Canonical Mypyを既存Baselineと比較。
- 実機Trialを行った場合は、実行前後のMARGPA Server、別pytest／Python／llama Process、Port 8000残存を確認する。
- Internal Review A：A→B→A再入、FIFO Bound、Late Evidence、Latest Pointer。
- Internal Review B：Repair outcome、Presentation、同一32 Criterion、Count保存則、Persistence、Evidence。

## 6. 禁止事項

- Selene修復・実機実行。
- Retry／JSON補修／共有Decoder緩和。
- Context、Budget、Criterion上限、Sampling、Schemaの追加変更。
- Phase 9-2／9-3、Phase 10、全面Rollback。
- Phase Index／Current Registryの編集。
- Git add／commit／push／stash。
- 既存Handoff、Return、Review、Historyの上書き・直編集。

Exact ReturnとRecoveryを必ず新規Pathで作成する。Handoff作成を省略せず、append-onlyを守る。終了後はCodex Controller Independent Review待ちで停止し、Phase 9-1 CompleteまたはClosureを自己宣言しない。
