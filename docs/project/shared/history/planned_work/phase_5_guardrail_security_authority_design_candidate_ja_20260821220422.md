# Phase 5 Guardrail／Security／Policy／Authority Design Candidate

```yaml
document_id: phase_5_guardrail_security_authority_design_candidate_20260821220422
status: program_level_candidate_not_frozen
phase: phase_5
recorded_at: 2026-08-21 22:04:22 JST
implementation_authorized: false
```

## 1. Goal

Main Modelの推論品質を扱うPhase 4 Governanceから、安全判定、Security、PolicyおよびAuthorityを独立Component／Pointへ分離する。

Milestone：`Security and Authority-aware Runtime`。

## 2. Candidate Subphase

```text
Phase 5-0 : Phase 4 As-built Reconciliation／Threat Model／Exact Freeze
Phase 5-A : Guardrail Result／Taxonomy／Rule Contract
Phase 5-B : Deterministic Input Guard
Phase 5-C : Deterministic Output／Streaming Guard
Phase 5-D : Policy／Authority／Human Approval Contract
Phase 5-E : Optional Safety Model Adapter／Calibration
Phase 5-F : Guardrail Point／Mode／Evidence／UI Integration
Phase 5-G : Integrated Adversarial Verification／COMPLETE_CANDIDATE
Phase 5-H : Codex Independent Review／User Acceptance／Minimal Closure
Phase 5-EX: AWS Public-ready Deployment Foundation（別Human Gate）
```

## 3. Core Candidate Requirements

- Rule-based Guardを正式Baselineとし、専用Safety Modelだけへ依存しない。
- Input／Output、Prompt Injection／Jailbreak、Secret／PII、Tool Abuse、Agent間攻撃を別Categoryとする。
- Detection、Policy Applicability、Authority、Recommendation、Executed Actionを分離する。
- Guard Model／Main Model／Judgeの出力を最終Authorityにしない。
- Tool Permissionは決定論的Policyと既存権限を正本とする。
- Policy／Authority不足時に`allow`を生成しない。
- Over-refusal／Under-refusal、False Positive／Negativeを別々に計測する。
- Guardrail OFF、OBSERVE、ENFORCEを個別比較可能にする。
- Security Critical ProfileではToggle非表示または固定ENFORCEを可能にするが、研究Local Profileでは比較Modeを許可できる。
- Secret／PII検知Evidenceへ検出対象の実値を複製しない。

## 4. Phase 4 Dependency

Phase 5は次を再利用する。

- Governance Point Runtime。
- Standard Governance Result。
- Binding／Capability／Authority／Budget Snapshot。
- Conflict／Action Resolver。
- Evidence／Status。

Phase 5固有に拡張する。

- Guardrail Result／Severity／Category。
- Policy Provider／Authority Provider／Approval Port。
- Security Action Adapter。
- Guardrail Point `pre／post／stream candidate`。
- Main GovernanceとのConflict Rule。

Phase 4 Action Resolverの欠陥をPhase 5側で迂回しない。Phase 4 Accepted後にExact Freezeする。

## 5. Safety Model Candidate

- `Qwen3Guard-Gen-0.6B`等は交換可能Adapter候補。
- Exact Artifact／Revision／License／CapabilityはPhase 5 Entryで再確認する。
- Safety ModelなしでもDeterministic Baselineが動く。
- Model ResultはConfidence、Calibration、Latency、Token、Failureを記録する。
- Model Error、Unknown LabelまたはTimeoutを安全判定成功へ変換しない。

## 6. Authority／Approval

```text
Guard Observation
  → Applicable Policy
  → Existing Authority／Delegation
  → Approval Requirement
  → Action Recommendation
  → Registered Action Resolver
  → Executed／Not Executed
```

Human Approval Hookは承認状態を受け取るPortであり、AIが承認を自己発行しない。External Action、Tool Side Effect、公開、Secret、課金または不可逆操作は既存User Authorityを越えない。

## 7. Adversarial Acceptance Candidate

- Direct／Indirect Prompt Injection。
- Encoded／Multilingual／Fragmented attack。
- RAG Source内Injection。
- Secret／PIIの実値非露出。
- Tool／Agent Authority spoofing。
- Guard Model false allow／false deny。
- Streaming途中とTerminalの差。
- Main GovernanceとGuardrailのConflict。
- OFF Call 0／Observe Mutation 0／Enforce Exact Action。
- Public／Basic／AWS ProfileのControl／Evidence Boundary。

## 8. Phase 5-EX Boundary

AWS準備はPhase 4以前からRead-only／Designで進められるが、Public-ready AcceptanceはPhase 5 Security／Authority成立後とする。初期AWSはQwen／Ephemeralを優先し、DeepSeek常時稼働やPersistent Data自動Bindingを前提にしない。

## 9. Exact Freeze Timing

Phase 4 Accepted後に、Phase 4 As-built Source／Test、実際のGuard Artifact、Threat ModelおよびUserのAWS方針を再確認し、Requirements／Architecture／ADR／Execution／Acceptance／Claude Handoffを正式作成する。

