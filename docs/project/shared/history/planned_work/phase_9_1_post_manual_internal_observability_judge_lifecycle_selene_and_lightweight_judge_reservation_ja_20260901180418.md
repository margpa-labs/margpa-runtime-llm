# Phase 9-1 Post-Manual Internal Observability／Judge Lifecycle／Selene／軽量Judge予約

```yaml
document_id: phase_9_1_post_manual_internal_observability_judge_lifecycle_selene_and_lightweight_judge_reservation_20260901180418
document_type: append_only_planned_work_and_next_rework_reservation
document_state: reserved_not_started
language: ja
recorded_at: 2026-09-01 18:04:18 JST
decision_authority: user
project_stage: individual_r_and_d_poc_mvp_portfolio
implementation_authorized: false
mvp_priority: preserve_mvp_first
source_evidence:
  - ../automation/codex_controller_phase_9_1_user_manual_ui_observability_hallucination_and_user_cost_failure_evidence_ja_20260901173556.md
```

## 1. User Decision

Phase 9-1 User Mac Manualで、現在UIから確認可能な項目の確認は完了した。現在UIに存在しない内部状態を、Userへ追加で探させない。

次の内部Observabilityは研究用Platformとして将来価値があるため予約するが、実装時期は未定とし、現在のMVP進行を止めない。

- Model／Artifact／Manifestの詳細Identity。
- Preflight／Artifact Check／Load／Prompt Build／Inference／Strict Decode／Evidence Projectionの段階別状態。
- Main Model／Judge／Guard／Repair／Tool Call数。特にFail-closed時のCall 0。
- Late Result／Late Publish 0。
- Worker Admission／Drain／残存Worker 0。
- Exactly-once Release。
- Internal Cancellation Token伝播。
- Repair CandidateとPresented Candidateの内部Identity。
- Frozen Judge／Rejudge Identity。
- Whole-stage Deadline、残Budget、Maximum Repair回数。
- Active Turn Drain／Pending Unloadの内部状態。

## 2. UI設計境界

上記を既存Settings本文へ全件直書きしない。現在でも情報量が多く、MVP段階で全面追加すると可読性と実装工数を悪化させる。

将来実装時は、次のProgressive Disclosureを候補とする。

```text
通常画面:
  Current Result、Provider、Mode、Failure Codeだけ

Research Trace:
  Turn／Stage／Call／Budget／Lifecycleの要約

詳細Drawerまたは右Panel:
  Artifact／Manifest／Digest／Stage Timing／Candidate Identity

Exportable Evidence:
  Worker、Cancellation、Late Result、Exactly-once等の機械検証
```

専用Observability UIがない間、Backend Test専用の事項をUser Manual項目へ混入させない。

## 3. Main-shared Qwen Judgeの不安定性

User実画面では、Selene実行前のMain-shared Qwen Judgeは動作した実績がある。その後、Seleneを使用した後にMain-sharedへ戻すと`malformed_output`または`The model is not loaded`へ収束する事象が観測された。Server Restart後に回復する可能性がある。

現時点では、次のいずれも断定しない。

- Qwen Judge Model自体の恒常的Failure。
- Seleneだけが原因。
- Mac性能だけが原因。
- Judge／Repair Mode切替だけが原因。

次回は、Clean Server Restartを起点に、`Main-shared単独 → Selene → Main-shared再選択`を最小Sequenceで再現し、Role Lifecycle、Unload、Lease、Cancellation、Active Model IdentityおよびFailure CodeをSource／Automated Test側で照合する。

## 4. Seleneの現在判定

User UIでは次を確認した。

```text
Configured: judge.selene-1-mini-llama-3.1-8b-q5-k-m
Active: judge.selene-1-mini-llama-3.1-8b-q5-k-m
State: active
Judge Result: failed
Failure: unavailable
Criteria: selected 32 / evaluated 0 / unknown 32 / deferred 77
```

したがって判定は次である。

```text
Load／Lifecycle Activation: reached according to current UI
End-to-end Judge Inference／Decode／Result: not established
Selene usable on demand: false
```

Seleneが重くMacを固まりやすくすることは実観測である。ただし、`active`表示後に`unavailable`となり、さらにRole切替後のMainまで`model is not loaded`へ崩れたため、PCスペックだけへ原因を帰属しない。まずSource／Lifecycle／Budget／Deadline／Batch／CancellationのRework対象として扱い、Hardware制約は同じ再現でLatency、Memory PressureおよびTimeoutとの相関を取る。

Seleneを「選択肢に表示できる」だけでなく、「必要時に実際にJudgeとして使える」状態へすることはPhase 9-1の未完了事項である。

## 5. 軽量LLM-as-a-Judge候補

Selene 8B Q5_K_MはLocal Mac上で非常に重い。Seleneを修復して残す一方、常用または低負荷Experiment用の軽量Judge候補を別に持つ価値がある。

次回Packageでは、Resourceに余裕があれば次をSelene安定化と併行せず、同じ順序内で実施する。

1. SeleneのLifecycle／Inference Failureを先に修復する。
2. 軽量Judge候補の要件を固定する。
3. Candidateを比較し、Userが許可した1候補だけArtifact／Manifest／Adapterへ接続する。
4. Real Local SmokeでLatency、Memory、Strict Decode、Semantic Criterion CoverageおよびFailure収束を比較する。

候補評価軸：

- Local MacでのMemory／Latency。
- Structured Output／Strict Decode適合性。
- 日本語入力と日本語回答の評価能力。
- Classification／Scoring／Multi-criterion対応。
- Main Qwenからの独立性。
- License／Distribution／Artifact Provenance。
- Existing Judge Port／Lifecycle Contractの再利用率。
- Result Qualityだけでなく、Load／Unload／Cancel／Restartの安定性。

既存Contractを再利用できる場合、候補調査と1候補のBounded Integrationは小〜中規模を想定する。ただしArtifact取得、Prompt Contract差、Decoder追加またはLicense確認が必要なら拡大する。新ModelのDownload／Network／Artifact登録は別Authorityなしに開始しない。

## 6. Priority／Routing

```text
Current User Manual additional action: none
Next mandatory rework:
  Selene end-to-end usability
  Selene後のMain-shared／Main lifecycle stability

Optional in same next package if resource permits:
  lightweight Judge candidate selection and one-candidate smoke

Future timing unknown, non-blocking for current MVP:
  full internal execution observability UI
```

## 7. Non-goal

本予約は、Observability全項目の即時UI追加、外部Model Download、Network、Artifact登録、Source実装、Git、Phase Closureまたは新しいProvider Authorityを与えない。個人R&D／PoC／MVPの主経路を優先し、研究用詳細表示を無制限に増やさない。
