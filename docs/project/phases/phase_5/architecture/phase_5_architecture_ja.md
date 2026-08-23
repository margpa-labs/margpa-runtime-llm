# Phase 5 Guardrail／Security／Policy／Authority Architecture

```yaml
document_id: phase_5_architecture
status: accepted_frozen_ready_for_backup
phase: phase_5
language: ja
recorded_at: 2026-08-22 09:57:48 JST
implementation_authorized: false
```

## 1. Architecture Summary

```text
Canonical User Input
  → guardrail.input
  → guardrail.context_source（RAG／External Context毎にSource Authority分離）
  → Phase 4 main_model.pre
  → Existing Model Generation
  → guardrail.stream_candidate（EnforceはBounded Holdback／Incremental Scan）
  → Phase 4 main_model.post
  → guardrail.output_candidate
  → Authorized Canonical Result
  → Persistent Commit
  → completed SSE

各Guardrail Point
  → Detection Facts
  → Applicable Policy
  → Current Authority／Approval State
  → Recommendation
  → Registered Action Resolver
  → Executed／Not Executed
  → Safe Evidence／Status
```

Phase 5はPhase 4 Runtime Governanceを内部的に書き換えない。Guardrail ResultとMain Governance Resultを独立に保ち、Terminal Orchestratorが明示的なConflict Ruleで統合する。

## 2. Module Boundary Candidate

```text
modules/guardrail_governance/
  domain/
  application/
  ports.py
  public.py

adapters/guardrail_governance/
  deterministic/
  policy/
  authority/
  safety_model/

bootstrap/guardrail_governance.py
web/guardrail_governance_routes.py
frontend Guardrail Panel／Status
```

実FileはPhase 5-0でAs-builtを再確認し、必要なものだけを動的に解決する。本図を固定Package量産指示としない。

## 3. Core Contracts

### 3.1 Guardrail Invocation

```text
GuardrailInvocation
  invocation_id
  point_id／stages
  request／turn／source references
  content_digest／bounded_typed_snapshot
  detector_registry_digest
  policy_snapshot_digest
  authority_snapshot_digest
  approval_snapshot_digest
  action_registry_digest
  mode／profile／budget
```

SnapshotはPoint毎のTyped Allowlistとし、Runtime Object全体Dumpにしない。Secret／PIIは実値でなく、必要な場合に限りEphemeral Scan BufferとTyped Spanで扱う。

### 3.2 Detection Result

```text
GuardDetection
  detection_id
  detector_id／revision／digest
  category_id
  outcome: clear／match／unknown／unavailable／error
  confidence／calibration_state
  severity
  typed_spans（optional, ephemeral／bounded）
  safe_reason_code
```

`clear`は対象Detectorがその範囲でHitを検出しなかっことだけを意味し、全面的な安全保証ではない。

### 3.3 Policy／Authority／Approval

```text
PolicyDecision
  policy_id／revision／digest
  applicable／not_applicable／unknown
  required_authority_ids
  approval_requirement
  recommended_action_ids

AuthorityDecision
  authority_revision／scope／digest
  granted／denied／unknown／stale

ApprovalState
  not_required／pending／approved／rejected／unavailable／expired
  approval_reference（opaque／non-secret）
```

Approval Portは外部で人間が作ったStateを受け取る。AI／Model／Definition／Detectorが`approved`を生成するMethodを持たない。

### 3.4 Guardrail Result

```text
GuardrailResult
  execution_state
  detections
  policy_decisions
  authority_decisions
  approval_states
  severity／critical_flags
  recommended_actions
  executed_actions
  not_executed_reasons
  evidence_refs
  latency／call／byte／token metrics
  unavailable／degraded reason
```

## 4. Mode Routing

### OFF

Guardrail CompositionはDetector／Safety Model／Policy／Authority／Actionを呼ばず、既存Phase 4／Generation経路へそのままShort-circuitする。

### OBSERVE

Detection、Policy RecommendationおよびSafe Evidenceを生成するが、送信、Generation Config、Stream Delta、Canonical Output、PersistenceまたはStopを変更しない。

### ENFORCE

```text
detection
  → policy applicability
  → conflict resolution
  → current authority
  → approval state
  → capability／budget
  → registered action validation
  → execute or typed not_executed
```

UnavailableまたはStaleなSnapshotをObserveへSilent Downgradeしない。

## 5. Input／Context Guard

- User Input、RAG Source、System-owned InstructionおよびTool ResultのSource Classを混ぜない。
- RAG Source内のInstruction-like Textは「検索されたData」であり、上位Instruction Authorityを持たない。
- Deterministic Detectorは、必要最小限のUnicode Normalization、不可視文字／分断、Encoded Candidate、Secret／PII Pattern、Authority Spoofing MarkerおよびSize Limitを分離して処理する。
- Enforce RejectはModel Call前のTyped Terminalとし、入力原文をSafe Error／Evidenceへ複製しない。

## 6. Streaming／Output Guard

### 6.1 Observe

Current Streamingの表示を変えず、Bounded Scanner Stateが観測する。Observation FailureはOutputを変更せずDegradedを記録する。

### 6.2 Enforce

Deterministic Stream GuardはChunk境界を跨ぐPatternのため有界Suffixを保持する。Safe Prefixだけを放出し、Hit時は一致Contentを放出せずTyped Terminalへ収束する。

Safety ModelのTerminal-only Evaluationを将来導入する場合、未検査ContentをStreamingした後でRejectする構成は不可である。全Buffer／Delayed Releaseまたは別Capabilityとし、Latency／Memory Budgetを明示する。

### 6.3 Terminal／Persistence Order

```text
Model／Summary Candidate
  → Phase 4 main_model.post
  → Phase 5 guardrail.output_candidate
  → Guardrail pass／authorized transform only
  → Assistant Message Atomic Commit
  → completed SSE
```

Reject／Unknown Fail-closed／Action Failureで未承認CandidateをConversation History／Citation／Headへ永続化しない。

## 7. Main Governance Conflict Rule

- Safety／Authority DenyはMain Governance Allow／Passで解除されない。
- Main Governance RejectはGuardrail AllowでCompletionへ変わらない。
- 複数Reject／Stopは一つのTyped Terminalへ収束し、二重Action／二重Evidence・二重SSEを避ける。
- RedactionとRejectが衝突する場合、PolicyとAuthorityで明示解決できなければRejectとする。
- Phase 6 Judge／RepairはPhase 5 Safety／Authority Denyを上書きできない。

## 8. Safety Model Seam

Safety Model AdapterはTyped Request／Response、Label Schema、Exact Revision、CalibrationおよびFailure Contractを持つ。Providerなしで`unavailable`、Timeout／Unknown Labelで`unknown`とし、決定論的DetectorとのConflictをPolicyが解決する。Phase 5 Initial FreezeではProduction Model Callを必須にしない。

## 9. Evidence／Status／UI

- EvidenceはContent自体でなく、Point／Detector／Category／Policy／Authority／Approval／ActionのIdentityとSafe Outcomeを保存する。
- UIはGuardrail Mode、Point State、Detection Count、Category Count、Severity、Recommended／Executed Count、Approval／Degraded／Unavailableを表示する。
- Secret／PIIはValue、Prefix／Suffix、Hash、Reversible Tokenのいずれも通常Statusに出さない。
- Research LocalでMode比較できるが、Public／BasicではPrivate ControlとPrivate Evidenceを表示しない。

## 10. Failure／Concurrency／Recovery

- Detector／Policy／Authority／Approval／Action Failureは異なるTyped Reasonを持つ。
- Cancel vs Reject vs CompleteはTerminal一件だけが勝つ。
- Stream Scanner StateはRequest-localとし、別Turn／Tab／Userへ混同しない。
- Mode／Policy／Authority／Registry Revision変更後に旧State／Cacheを黙って再利用しない。
- Unknown Commit Resultは既存Operation Receipt／Detail再読へ収束し、再生成で推測修復しない。

## 11. Phase 6 Seam

- Semantic Judge PortはGuardrail Detectionを上書きせず、別Resultを返す。
- Repair OrchestratorはGuardrail／Authority Final Denyを再承認できない。
- RepairされたCandidateは新しいAttemptとして全Pointを再通過する。
- Phase 5でJudge／Repairが実装済みと表記しない。
