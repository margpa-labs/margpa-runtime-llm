# Phase 6 Judge／Evaluation／Repair／Observability Design Candidate

```yaml
document_id: phase_6_judge_repair_observability_design_candidate_20260821220422
status: program_level_candidate_not_frozen
phase: phase_6
recorded_at: 2026-08-21 22:04:22 JST
implementation_authorized: false
```

## 1. Goal

回答品質を独立評価し、AuthorityとBudgetに従う有界Repairを追加する。Phase 6完了をPhase 4〜6 `Runtime Governance MVP v1`の統合Milestone候補とする。

## 2. Candidate Subphase

```text
Phase 6-0 : Phase 4／5 As-built Reconciliation／Exact Freeze
Phase 6-A : Evaluation Identity／Criteria／Dataset／Result Contract
Phase 6-B : Deterministic Judge／Rule Evaluation
Phase 6-C : LLM-as-a-Judge Adapter／Independence／Calibration
Phase 6-D : Repair Trigger／Budget／Orchestrator／Success Evaluation
Phase 6-E : Runtime Status／Observability／User Feedback UI
Phase 6-F : OFF／OBSERVE／ENFORCE／Repair Comparative Experiment
Phase 6-G : Program Integrated Verification／COMPLETE_CANDIDATE
Phase 6-H : Codex Independent Review／User Acceptance／Phase 4〜6 Closure
```

## 3. Judge Requirements Candidate

- JudgeはMain Model、Guardrail、Policy、AuthorityおよびAction Resolverから独立したComponentとする。
- Deterministic Judgeを比較Baselineとして残す。
- LLM-as-a-JudgeはEvaluator ID、Model／Artifact Digest、Criteria／Prompt Digest、Seed、Config、Evidence Scope、Confidence、Latency、TokenおよびCostを持つ。
- Main Model自己評価を補助Evidenceとし、単独の最終Authorityにしない。
- Position Bias、Self-preference、Verbosity Bias、Language差、CalibrationおよびReproducibilityを評価する。
- Judge Conflictは固定多数決だけで解決しない。
- JudgeがConversation Storage、Tool PermissionまたはExternal Actionを直接変更しない。

## 4. Repair Requirements Candidate

```text
Detect
  → Classify／Severity
  → Recommended Repair
  → Authority／Policy／Budget
  → One bounded repair attempt
  → Independent success evaluation
  → accept／retry within limit／fail／human escalation
```

必須上限：

- Max Attempts。
- Max Wall Time。
- Max Additional Tokens。
- Max Total Model Calls。
- Max Repair Depth／Recursion。
- Explicit Success Criterion。

無限Loop、Judge→Repair→Judgeの無制限再帰、RepairによるAuthority拡張、失敗Originalの隠蔽および未完了を成功扱いすることを禁止する。

Repairは新しいAttempt／Resultとして記録し、Original、Recommended Action、Executed Action、OutcomeおよびCanonical Presented Answerを区別する。通常EvidenceへHidden Original全文を保存するかはPhase 6で自動許可しない。

## 5. Runtime Status Candidate

```text
idle
  → generating
  → governance_observing | governance_enforcing
  → guarding
  → judging
  → repairing
  → rejudging
  → completed | rejected | cancelled | failed | degraded
```

UI表示状態と内部Authority Stateを同一視しない。Status Subscriber FailureはRuntime成功を捏造せず、安全なDegradedへ投影する。

## 6. User Evaluation

- Good／Bad等の最小Feedback。
- Optional Category／Commentは明示保存Scopeを持つ。
- User Feedbackを自動的にPolicy、AuthorityまたはTraining Dataへ昇格しない。
- Conversation／Turn／Answer／Model／Governance Configへ追跡可能にする。
- Privacy／Retention／Export／Delete方針を別Gateにする。

## 7. Phase 4／5 Dependency

- Phase 4のStandard Result、Point Runtime、Action Resolver、Evidence。
- Phase 5のGuardrail、Policy、Authority、Approval。
- Judge Recommendationはこれらを上書きせず、Action Resolverへ入力する。
- Repair可能Actionは登録済みAdapterとAuthorityがあるものだけ。
- Guardrail Critical Rejectを、品質Judgeの高Scoreで解除しない。

## 8. Comparative Acceptance Candidate

同一Qwen Input／Config／Definition／Seed候補で次を比較する。

1. Governance OFF。
2. Main Governance OBSERVE。
3. Main Governance ENFORCE。
4. Guardrail追加。
5. Deterministic Judge追加。
6. LLM Judge追加。
7. Bounded Repair追加。

測定：正答／根拠不足停止／定義混同／形式遵守／過剰拒否／過少拒否／修復成功／悪化／Token／Latency／Call／Cost。

## 9. Program Closure Candidate

- Qwenの弱点をGovernance／Guardrail／Judge／Repairでどこまで制御できるか再現可能。
- 各Componentの寄与と失敗を分離観測可能。
- OFF BaselineとSafety Critical Profileの両方が成立。
- Open Major Finding 0。
- Codex Independent ReviewとUser Acceptance。
- Phase 4〜6のFinal Docs／Backup／Git／Roadmapを統合整理。

## 10. Exact Freeze Timing

Phase 5 Accepted後にAs-built Result／Guardrail／Authority／Evidenceを再確認し、Judge Model候補、Evaluation Set、Repair CeilingおよびUser Feedback保存ScopeをHuman Gateとして固定する。

