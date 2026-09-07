# Phase 9-1 — Component完全疎結合 R3残差Rework Exact Handoff

```yaml
document_type: exact_implementation_handoff
document_state: ready
recorded_at: 2026-09-05 18:17:01 JST
language: ja
from: codex_controller
to: claude_designer_implementer
decision_authority: user
authority_owner: Nazuna Research
in_response_to: phase_9_claude_component_independence_r2_delta_rework_exact_return_ja_20260905175816.md
review: ../history/operations/phase_9_1_component_independence_r2_return_controller_review_ja_20260905181701.md
maximum_claim: P9_1_COMPONENT_INDEPENDENCE_R3_RESIDUAL_REWORK_READY
phase_9_1_closure: false
git_action: prohibited
append_only: true
```

## 1. 目的と保持範囲

R2をRollbackしない。Main OFF／absentのMain Semantic Evidence Call 0、Dedicated Gemma Identity分離、Role局所Sampling固定、Guard同一条件Test、同一Turn保存の有効差分を保持し、Controller Reviewの残差だけを順番どおり修正する。

最上位契約は変えない。

```text
Component OFF／不在／空定義
  => 当該ComponentのCall／Mutation／Evidence／Authority 0
  => 他Componentの起動／Context／Evidenceを欠損させない
```

## 2. R3-WU-01 — Evaluation Turn Startを単一Freeze境界にする

`runtime_snapshot`、Judge／Repair／Recording Mode、Main Mode、Judge Configured／Active Provider／State、Language／Budget／Criteria Generationを、Conversation Turn開始時の一つのImmutable Evaluation Turn Contextとして確定する。

- `semantic_turn_begin_hook(request_id)`からLive Modeを別読みする現形は廃止する。既に取得したJudge／Repair／Recording Modeを同じ開始契約へ渡すか、単一Providerの戻り値をConversationとSemantic Runtimeが共用する。
- MainとJudgeは中立ContextのPeer Consumerとし、Main Composition ObjectをJudgeの必須依存にしない。
- Turn開始Freezeが失敗したら、そのrequestでは後からLive値を読んで初回Freezeをやり直さない。Main Chatはブロックせず、JudgeはTyped Unavailable／Deferredに収束する。
- Completion時に取得したDedicated AdapterのProvider IdentityがTurn開始時Active Providerと異なる場合、別Providerをそのまま実行しない。Leaseを解放しTyped Failureにする。

Regressionは、Snapshot取得の間にMode／Providerを変更するController ProbeをそのままTest化し、ConversationとSemantic Snapshotが一致すること、開始失敗後のProvider呼出しが合計1回であることをAssertする。Main OFF／absentのMain Evidence Call 0は維持する。

## 3. R3-WU-02 — 三Judge経路のIdentityを完結させる

Dedicated Gemma、Main-shared Qwen、Built-in Deterministicの三経路で、保存した実JSONの次のFieldをそれぞれAssertする。

- Evaluated Main Identity。
- Configured／Active／Executed Judge Provider。
- Executed Judge Artifact Digest／Backend Key／Version。

Built-inは`model_identity=built_in.deterministic`とし、Model Artifactが無い事実を`unavailable`／`not_applicable`の既存契約で正直に表す。Main Artifactを流用しない。Live Resultと保存EvidenceのExecutedが一致することをSabotageで証明する。

## 4. R3-WU-03 — Cancellation起源をTerminal確定まで保持する

Worker内部だけではなく、ENFORCE Terminal Ownerが結果を確定するまでMain-priority Preemption起源を失わないRun-local契約にする。

- Worker先行終了→cleanup→Terminal Owner読取のScheduleを固定したController ProbeをRegression Test化する。
- User Stop／Client disconnect、Main-priority Preemption、Deadlineを異なるReasonのまま保持する。
- Result ReadyとCancellationが同時の場合も、Workerが既に確定したPreemption ReasonをGeneric Request Cancelで上書きしない。
- Terminal確定後／成功shutdown後にBookkeepingを残さない。

Model Call／Cancel Grace／Deadline／Release上限は変えない。

## 5. R3-WU-04 — Gemma Schemaの非曖昧化

Deterministic Samplingは保持する。Gemma専用経路だけで、`short reference`／`short code`のような自然言語Placeholderを見せた後にRuleで否定する構造を廃止し、パース可能な一つの正規JSON Example／Schemaにする。SeleneとMain-shared Promptには波及させない。

Unitで生成Prompt内のSchema自体をJSON parseし、必須Key／型／Field順をAssertする。実Gemmaの通常初回32 Criterion／4 Batch OBSERVEは最大2 Trial。全Batch Strict Decode、32 ID一致、`evaluated>0`をHard Assertする。二回とも成立した場合だけ次へ進む。

Decoder緩和、JSON補修、Retry追加は行わない。失敗時はRaw全文をDocsに転記せずDigest／finish reason／token／Decoder reason／失敗Batchのみ返して停止する。

## 6. R3-WU-05 — 真の32 Criterion Production Web Golden Path

R3-WU-01〜04成立後にのみ行う。

```text
Main Governance: ENFORCE
Judge: Gemma ENFORCE
Repair: OFF
Guard: OFFまたはOBSERVE
Recording: FULL
Criteria: 通常選択32
```

- Fixtureは4件ではなく32件を使い、同一32件がRejudgeまで維持されることを確認する。
- 手組みの類似Compositionではなく、`build_phase1_web_runtime()`のProduction Composition Root、またはそこから抽出した同一Builderを通す。
- R3-WU-01のEvaluation Turn Start Hook、通常Conversation完了、PersistentConversationService、Recording FULLを同一経路で通す。
- `repair_requested_by=main_governance`、Repair improved／accepted、同一Gemma／同一32 Criterion Rejudge、Presented Final、同一Turn Record／Judge EvidenceをHard Assertする。
- 実機は1 Trial上限。Missing Artifact以外のSKIPを禁止し、Malformed／`evaluated=0`／Deviation 0はFAILのまま返す。

## 7. R3-WU-06 — Claim訂正・Verification／Return

- Guardは対象一Trialの一致までをClaimし、過去DivergenceのRoot CauseをSamplingに一意確定しない。Guard実機の再実行は不要。
- Focused Unit／Integration、Backend非Model Full、Ruff、Canonical Mypyを実行する。Frontend非変更ならFrontend再検証は不要。
- Internal Review AはTurn Freeze／OFF Call 0／Provider切替／Composition Root、Review BはIdentity／Terminal Race／Strict Decode／32件Persistence Oracleに完全分離する。
- Exact ReturnとRecoveryは必ず新規Pathへ作る。既存Handoff／Return／History／Phase Indexを上書き・直編集しない。

## 8. 禁止事項

Selene修復／実機実行、Phase 9-2／9-3、Phase 10、全面Rollback、Context／Budget／Criterion上限変更、Decoder緩和、JSON補修、Retry追加、Native更新、Download、新Resource Gate、Git add／commit／push／stashは禁止する。

Return後はCodex Controller Review待ちで停止する。Phase 9-1 Complete、User Acceptance、次Phaseへ進まない。
