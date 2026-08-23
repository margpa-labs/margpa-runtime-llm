# Phase 4〜6 Runtime Governance Program Design

```yaml
document_id: phase_4_to_6_runtime_governance_program_design_20260821220422
status: accepted_design_candidate_not_activated
scope: phase_4_to_phase_6
language: ja
recorded_at: 2026-08-21 22:04:22 JST
owner_role: プロジェクト責任者兼設計統括者役
implementation_authorized: false
git_mutation_authorized: false
```

## 1. Purpose

Phase 4〜6を、個別機能の寄せ集めではなく、一つの依存順を持つRuntime Governance Programとして設計する。

```text
Phase 3: Definition／IR／Unbound Plan／Evidence
  ↓
Phase 4: Main Model Governance Point／Binding／Deterministic Evaluation／Enforce MVP
  ↓
Phase 5: Guardrail／Security／Policy／Authority Point
  ↓
Phase 6: Judge／Evaluation／Bounded Repair／Observability
```

Phase 6完了時点を`Runtime Governance MVP v1`の候補境界とする。Phase 7の本格RAGは、この評価・修復・Evidence基盤へ後から接続する。

## 2. Program-wide Invariants

1. Definition 0件、Component OFFおよびGovernance OFFのBaselineを全Phaseで維持する。
2. CoreへARGD、DAGD、AISGD等の固有名称、固定File名、固定件数または特定Model名をHard-codeしない。
3. Definition Source、Normalized IR、Compiled Plan、Binding、Evaluation、Recommendation、Executed ActionおよびRepairを別Identity／Stateにする。
4. `recommended_actions`と`executed_actions`を分離し、Definition／Judge／ModelがAuthorityを生成しない。
5. `off／observe／enforce`を共通Modeとし、Mode切替だけで未登録Capabilityを利用可能にしない。
6. `observe`はFunctional Input／Outputを変更しない。`enforce`は登録済みAction Adapter、Authority、BudgetおよびCapabilityの積集合だけを実行する。
7. Raw Thinking、System Prompt、Secret、Hidden Original、未確定Partial OutputまたはTool内部情報を通常Evidenceへ保存しない。
8. Qwen3-4BをMac／低資源／弱Model Governance比較Baselineとして維持する。
9. DeepSeekは交換可能なMain Model Candidateとして保持するが、Phase 4〜6 Completion Dependency、Default CurrentまたはAWS常時稼働要件にしない。
10. Public／Basic／Lightning／AWSへLocal-private Governance Control、Private DefinitionまたはEvidenceを自動Bindingしない。
11. Runtime Result、Governance Result、Guardrail Result、Judge ResultおよびRepair Resultを一つの曖昧なScoreへ潰さない。
12. 既存Conversation、RAG Citation、Streaming、Stop、Retry／RegenerateおよびPersistent Recoveryを壊さない。

## 3. Phase Responsibility

### 3.1 Phase 4 — Main Runtime Governance

Phase 3のUnbound PlanをMain Model `pre／post` Pointへ安全にBindingし、最初の実用的な`off／observe／enforce`比較を成立させる。

- Standard Governance Result。
- Runtime Capability／Authority／Budget Snapshot。
- Plan BindingとBinding Digest。
- Deterministic Evaluator。
- Main Model pre／post Point。
- Conflict／Action Resolver MVP。
- 非破壊・登録済みActionだけのEnforce MVP。
- ARGD／DAGD Reference AdapterのTyped Extension。
- Mode／Status／Evidence／UI。

Phase 4ではLLM-as-a-Judgeと反復Repairを実装しない。Semantic Evaluator Portは予約またはNo-op／Unavailableでよい。

### 3.2 Phase 5 — Guardrail／Security／Policy／Authority

推論品質Governanceと安全・権限判断を分離する。

- Rule-based Input／Output Guard。
- Prompt Injection／Jailbreak／Secret／PII／Tool Abuse検知。
- Guardrail Point。
- Model Policy／Authority／Approval Contract。
- 決定論的Tool Permissionとの接続境界。
- Qwen3Guard等のSafety Model Adapter候補。
- GuardrailとMain GovernanceのConflict Resolution。

専用Safety Modelは補助Evaluatorであり、最終Authorityにしない。Rule-based Baselineを常に残す。

### 3.3 Phase 6 — Judge／Evaluation／Repair／Observability

回答品質の独立評価と、有界な修復Loopを追加する。

- Deterministic JudgeとLLM-as-a-Judge Adapter。
- Judge Independence／Bias／Confidence／Calibration。
- Evaluation Set／User Feedback。
- Repair Trigger／Action／Budget／Success Criterion。
- `idle → generating → judging → repairing → completed|failed` Status。
- Governance効果、False Positive／Negative、Token、Latency、Repair回数の比較。

JudgeはRecommendationを返すだけで、最終Authorityまたは無制限再生成権限を持たない。

## 4. Dependency Gates

### Phase 4 Entry

- Phase 3 Technical FindingがClosed。
- Phase 3 Final Closure／User Acceptanceまたは、ユーザーが明示した限定Start Gate。
- Phase 3 Definition／IR／Plan／EvidenceのAs-built Contractを再確認。
- Qwen Current Routeが正常。

### Phase 5 Entry

- Phase 4 Main Pointが`off／observe／enforce`でAccepted。
- Standard Governance ResultとAction Resolverが安定。
- Authority不足時のAction 0、Mode OFF時Call 0が証明済み。

### Phase 6 Entry

- Phase 5 Guardrail／Policy／AuthorityがAccepted。
- JudgeがGuardrailやAuthorityを上書きしないConflict Ruleが固定済み。
- Repair可能ActionとRepair不能Actionが型で分離済み。

### Program Closure

- Phase 4〜6のOFF／OBSERVE／ENFORCE比較が再現可能。
- Qwen Baselineで知ったかぶり、根拠不足、定義混同、形式逸脱等を評価可能。
- Governance／Guardrail／Judge／Repairそれぞれの寄与、CostおよびFailureを分離観測可能。
- Phase 7 RAG Governanceへ接続できるPortが存在する。

## 5. Execution／Review Strategy

全体設計は先に固定するが、Exact Implementation FreezeとClosureはPhase単位で行う。

```text
Phase 4 Design Freeze
  → Claude Phase内実行／Self-review／COMPLETE_CANDIDATE
  → Codex重大FindingだけのIndependent Review
  → Claude局所Rework
  → 最小Closure
  → Phase 5 Exact Freeze
  → 同じFlow
  → Phase 6 Exact Freeze
  → 同じFlow
  → Phase 4〜6 Program Final Review
```

Phase 4の欠陥を抱えたままPhase 5／6を実装しない。Codex Reviewは重大Findingへ限定し、軽微な改善、将来HardeningまたはPhase 7事項をCurrent Blockerへ再活性化しない。

Phase 4／5のFinal Docs／Git／Backup作業は最小限にし、Phase 6完了時にPhase 4〜6をまとめて本格整理できる。ただし、各Phase境界のRecovery Index、Exact Mutation、Test結果およびOpen Major Findingは必ず残す。

## 6. Qwen／DeepSeek Strategy

- Current Default：既存Qwen3-4B。
- Phase 4実験Baseline：Qwen Governance OFF／OBSERVE／ENFORCE。
- Practical DeepSeek Candidate：DeepSeek-R1-0528-Qwen3-8B。
- Large Research Candidate：DeepSeek-V4-Flash-0731。
- DeepSeek Load／Benchmark／Current Promotionは別Gate。
- AWSでは当面Qwenまたは短時間8B検証を優先し、V4常時稼働を前提にしない。
- Model／Backend差をGovernance Coreへ漏らさず、Capability SnapshotとAdapterで吸収する。

## 7. Cross-phase Acceptance Axes

各Phaseで次を別々に報告する。

1. Technical correctness。
2. Security／Authority compliance。
3. OFF compatibility／zero side effect。
4. Observe non-intervention。
5. Enforce exact action and fail-closed behavior。
6. Evidence completeness／privacy。
7. Token／Latency／Call／Repair cost。
8. Automation／Compaction／Cross-provider fidelity。
9. Human clarification／intervention burden。
10. False completion／Codex-detected major finding／Self-repair。

## 8. Deferred

- Phase 5-EX AWS Public-ready Surface。
- Phase 7本格RAG／Data Governance。
- Phase 8 Agent／Tool／Memory。
- Phase 9 Experiment Platform／Desktop App Preview。
- DeepSeek V4常時運用。
- Full Prompt／Output／ThinkingのProtected Research Capture。
- EASA／DLAGSA／OCILNSの本実装。

これらはProgram Interfaceを予約できるが、Phase 4〜6 Completion Blockerにしない。

## 9. Current Status

```text
Phase 3                 : Claude Rework／Codex Re-review pending
Phase 4〜6 Program Design: CANDIDATE PREPARED
Phase 4 Design          : Candidate package preparation authorized
Phase 4 Implementation  : NOT AUTHORIZED
Phase 5／6 Exact Freeze : NOT PERFORMED
Git／External／AWS       : NOT AUTHORIZED
```

