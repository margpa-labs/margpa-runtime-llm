# Phase 11以降予約 — Layered AI Safety Stack Gap評価とLearned Safety拡張

```yaml
document_id: phase_11_plus_layered_ai_safety_stack_gap_assessment_and_learned_safety_extension_reservation_20260903070107
document_type: planned_work_reservation
document_state: reserved_not_started
recorded_at: 2026-09-03 07:01:07 JST
language: ja_with_structured_english_terms
project: MARGPA-RUNTIME-LLM
decision_authority: user
earliest_phase: phase_11_plus
mvp_priority: deferred_after_mvp
training_authority: not_granted
data_export_authority: not_granted
network_authority: not_granted
constitution_auto_change: prohibited
append_only: true
```

## 0. Reservation

現代のAI Safetyは、単一のRule-based AIではなく、複数Layerの合成として成立する。

```text
Learned Policy
Reward／Preference Training
Classifier
Inference-time Guardrail
System Policy
Tool Permission
Context Management
Human Oversight
Evaluation／Incident Feedback
```

MARGPA-RUNTIME-LLMはRule、Runtime Governance、Guardrail、Judge、Tool Gate、Evidenceを既に持つが、全Layerが完成しているわけではない。MVPを遅らせず、Phase 11以降にCurrent実装と不足Layerを再評価し、必要な拡張を判断する。

## 1. Current Gap Map

| Safety Layer | Current State | Main Gap |
|---|---|---|
| Rule／Runtime Governance | 強い基盤あり | Structural／Semantic適用、実ENFORCE、Layer間整合は未完 |
| Learned Policy | Base Model側へ依存 | Project-owned Policy Trainingなし |
| Reward／Preference Training | 未実装 | Reward Model、DPO／RLHF／RLAIF、Preference Pipelineなし |
| Dedicated Classifier | 部分的 | Qwen3Guard／Patternはあるが、独立・校正済みClassifier層は未成立 |
| Inference-time Guardrail | 実装あり | Provider安定性、Failure時整合、Layer Fusionの継続改善 |
| System Policy | 実装あり／統合予定 | Phase 10 Constitution統合後の妥当性再評価が必要 |
| Tool Permission | 実装あり | Capability拡張時のAuthority／Consent／Audit維持 |
| Context Management | 部分実装 | Compaction、Recovery、Context IntegrityはPhase 9-3以降 |
| Human Oversight | 実運用あり | Human Attention Cost、Escalation Budget、不要確認の抑制 |
| Feedback／Training Loop | 未実装 | Feedback収集、Dataset化、Consent、Export、再学習の閉Loopなし |
| Calibration／Uncertainty | 部分的 | Confidenceの信頼性、OOD、Unknown、Abstention評価が不足 |

## 2. 特に不足しているもの

Currentで明確に不足している中心は次である。

```text
1. Project-owned Learned Safety Policy
2. Reward／Preference Training
3. 独立した学習済みSafety／Quality Classifier
4. Feedback → Dataset → Training → Evaluationの閉Loop
5. Provider横断のCalibration／Uncertainty／Abstention
6. Rule／Judge／Guard／Classifier／Humanを統合するArbitration
```

Base Modelに学習済みSafety Policyが含まれていても、それはProvider／Model由来であり、MARGPA自身がVersion、Training Data、Preference Objectiveまたは更新条件を所有するものではない。

## 3. Candidate Work

Phase 11以降、必要性とResourceを再評価したうえで次を候補にする。

```text
A. Safety Capability Map
   各LayerのAuthority、Input、Output、Failure、Evidence、Fallbackを一覧化する。

B. Independent Classifier Layer
   軽量Classifier候補を比較し、Guard LLM／Rule Patternと役割分離する。

C. Calibration／Abstention
   Confidenceをそのまま信頼せず、Unknown／Defer／Human Escalationを校正する。

D. Feedback Dataset Contract
   Human Feedback、Synthetic Data、Incident EvidenceのConsent、Retention、Provenance、
   Contamination防止およびExport境界を定義する。

E. Preference／Reward Research
   DPO、RLHF、RLAIF、Constitutional Feedback等を比較する。
   実Trainingは別Authority Gateとする。

F. Layer Arbitration
   Rule、Classifier、Guard、Judge、Tool Permission、Human Decisionが競合した場合の
   Priority、Fail-safe、Appeal、Recoveryを定義する。

G. Incident-to-Evaluation Loop
   Claude Resource Gate Incident等の実Failureを再現可能なEvaluationへ変換する。
```

## 4. MARGPA Research Inputs

次の実Evidenceは、高価値な教材候補である。

```text
- Completion BiasとFalse Complete Claim
- Self-reviewによる誤前提の自己強化
- Unverified HypothesisからProtective Controlを作るFailure
- Safe RefusalとProduct Regressionの混同
- Active／Executed Identityと実Inference成功の混同
- Long Session／Compaction後のPremise Anchoring仮説
- Human Attention／Quota／Machine／Opportunity Cost
- External Controllerがない場合のAuthority逸脱
```

これらを即座にTraining Dataへ投入しない。まずProvenance、Consent、Privacy、Bias、RepresentativenessおよびEvaluation分離を設計する。

## 5. Non-goals

```text
- Phase 9-1 Recoveryを遅らせない。
- Phase 10の予定内容を増やさない。
- MVP前にTraining Infrastructureを作らない。
- User ConsentなしにConversation／FeedbackをTraining Dataへ転用しない。
- Synthetic Data生成をTraining実施と同一視しない。
- External ProviderのSafety Claimを無検証で採用しない。
- 本予約だけでConstitution Ruleを変更しない。
```

## 6. Entry Conditions

```text
- MVP完成またはUserによる明示前倒し判断
- Phase 10 Constitution三系統の初版統合完了
- Phase 11以降の中立他Task／他Provider評価方針確定
- Data Consent／Retention／Export境界確定
- Evaluation DatasetとTraining Datasetの分離
- Compute／Quota／Artifact／License条件の確認
```

## 7. Maximum Claim

```text
LAYERED_AI_SAFETY_GAP_IDENTIFIED
LEARNED_POLICY_REWARD_PREFERENCE_CLASSIFIER_AND_FEEDBACK_LOOP_RESERVED
NO_TRAINING_OR_DATA_EXPORT_AUTHORIZED
PHASE_10_SCOPE_UNCHANGED
MVP_PRIORITY_PRESERVED
```
