# Phase 8 P8-RW6 Codex Controller 二段階Targeted Re-review

```yaml
document_id: phase_8_codex_controller_rw6_two_cycle_targeted_re_review_20260831065406
document_type: controller_independent_review
document_state: final
language: ja
created_at: 2026-08-31 06:54:06 JST
phase: phase_8
review_target: P8-RW6-0_through_E
review_cycles: 2
implementation_mutation_by_controller: 0
maximum_disposition: REWORK_REQUIRED_BEFORE_USER_MANUAL
```

## 1. 結論

P8-RW6で実装した4件の中心修正は、個別のRuntime経路では成立している。

```text
P8-CODEX-005  Redirect Evidence Truthfulness     RESOLVED
P8-CODEX-006  Deterministic Dev Agent Budget     RESOLVED
P8-CODEX-007  Completion Gate Runtime Wiring     RESOLVED_WITH_NON_BLOCKING_CONTRACT_GAP
P8-CODEX-008  Constitution Three-mode Preview    PARTIALLY_RESOLVED
```

ただし第2 Cycleで、P8-CODEX-008のExact Handoff要件に未実装部分が残ることを確認した。
したがってP8-ACC-021をPASSへ昇格したP8-RW6 Returnの集計は維持できず、User Manual Candidateへはまだ渡さない。

```text
PASS                 36
PARTIAL               2  P8-ACC-021 / P8-ACC-038
FAIL                  1  P8-ACC-039（既知・PoC Runtime非Blocker）
USER MANUAL GATE      1  P8-ACC-040
TOTAL                40
```

## 2. Review Cycle 1 — 4 FindingのTargeted成立確認

### 2.1 P8-CODEX-005 — PASS

- Requested URLとRedirect後Canonical URLは別Fieldとして保持される。
- Source Authorityは最終Canonical URLのHostから再計算される。
- Evidence、Citation、REST／SSE、Persistence、Frontend Projectionに両URLが流れる。
- `.gov`から一般DomainへRedirectするFocused Regressionで、`OFFICIAL`を継承せず`GENERAL`へ収束する。

### 2.2 P8-CODEX-006 — PASS

- `ToolDescriptor.budget_cost`、`RunSnapshot.budget_limit`、`budget_consumed`が存在する。
- Tool実行直前にBudgetを検査し、超過時はTool Call 0の`budget_exceeded`へ収束する。
- Max Stepとは独立して作用し、失敗した実行Attemptも消費へ加算する。
- Limit／UsageはRun Storeで復元される。

### 2.3 P8-CODEX-007 — Runtime PASS

- `important_gate_only`は全Step成功後に`awaiting_completion_approval`へ遷移する。
- Completion ApprovalはStep Approvalと異なるTyped Evidenceであり、Run Identityを持つ。
- Pending／Denied／Approved／Restart／Cancel／Cross-run分離がTestされている。
- Network、Cost、Irreversible、Secret／Privacy、Scope Expansion、Critical IncidentはFixture DescriptorでGeneric Gate処理を通る。

### 2.4 P8-CODEX-008 — Preview経路自体はPASS

- `/api/v2/constitution/preview`は同一ManifestのOFF／OBSERVE／ENFORCEを返す。
- Production Active ModeはOFFのままで、Preview呼出し後も変化しない。
- UIはPreviewでありActive Runtime Modeではない旨を明示する。
- Digest不一致、Provider未接続は既存のTyped Failureへ収束する。

### 2.5 Focused Verification

```text
Backend selected 8 files: 165 passed
Frontend selected 4 files: 30 passed
```

## 3. Review Cycle 2 — Negative／Composition／Persistence／UI／Claim再検証

第1 Cycleの修正点を前提にせず、Frozen Contract、実ManifestのProjection、Frontend表示、Canonical TestおよびAcceptance Claimを再導出した。

### P8-CODEX-011 — Completion GateがFrozen EnvelopeのGate Conditionsへ現れない

```yaml
severity: moderate_contract_truthfulness
priority: P1
closure_blocker: false_for_phase_8_PoC
classification: frozen_envelope_observability_mismatch
affected_requirements:
  - P8-REQ-026
  - P8-REQ-027
affected_acceptance:
  - P8-ACC-033
  - P8-ACC-034
```

`AuthorizationEnvelope.gate_reasons`はPlan内Tool Descriptorだけから生成される。CompletionはTool Descriptorではないため、
Completion Gateが確実に発生する`important_gate_only` RunでもEnvelopeは空のGate理由を返し得る。

Codex実Probe：

```text
envelope_gate_reasons = []
runtime_state         = awaiting_completion_approval
```

Runtimeは実際に停止し、Typed Completion Evidenceも成立するためAuthority Bypassではない。`approval_profile`もRunへFrozen保存される。
よってPhase 8 PoC Closure Blockerにはしないが、EnvelopeをGate Conditionsの正本表示として読むと実挙動と一致しない。
将来修正時は`important_gate_only`のEnvelopeへ`completion`を含め、Persistence／REST／UI Testで固定する。

### P8-CODEX-012 — Constitution PreviewがDecision以外の比較Contractを実装していない

```yaml
severity: major
priority: P0
closure_blocker: true
classification: exact_handoff_scope_omission_and_false_acceptance_claim
affected_requirements:
  - P8-REQ-016
affected_acceptance:
  - P8-ACC-021
exact_handoff_requirement:
  - Decision
  - Action Permission
  - Violation Presentation
```

Exact Handoffは、各Modeの`Decision／Action Permission／Violation Presentation`を比較可能に表示するよう要求した。
実装されたPreview Contractは`mode／rule_ids／decisions`だけで、Action PermissionまたはViolation PresentationのFieldを持たない。
APIの`reason`はFrontendで表示されず、FrontendはOutcome文字列だけを列挙する。

さらにProduction Routeは`resolve_constitution_mode_preview()`へ`supported_rule_ids`を渡さない。Current Manifestの実Probeは次の通り。

```text
chat:
  OFF      -> not_evaluated
  OBSERVE  -> unsupported_action
  ENFORCE  -> unsupported_action
agent:
  OFF      -> not_evaluated
  OBSERVE  -> unsupported_action
  ENFORCE  -> unsupported_action
tool:
  OFF      -> not_evaluated
  OBSERVE  -> unsupported_action
  ENFORCE  -> unsupported_action
```

これは「未対応Ruleをobserved／enforcedへ捏造しない」という点では正しい。しかしUserが実画面で確認できるのはMode名とOutcomeだけで、
OBSERVEとENFORCEのAction Permission差、Violation時のPresentation差を確認できない。したがってP8-CODEX-008はPreview入口まで成立したが、
Exact Handoff全体は未完了であり、P8-ACC-021は`PARTIAL`へ戻す。

最小修正ScopeはPreview専用Contract／Projection／UI／Testだけでよい。Production Mode Activation、Runtime Enforcement、GD接続、
Model Injectionまたは新しいRule Engineは不要である。

## 4. Canonical Verification

Codex環境で次を再実行した。

```text
Backend: 2121 passed, 3 failed, 7 deselected
Frontend: 302 passed
Mypy:     Success, 344 source files
Ruff:     All checks passed
```

Backendの3 Failureは既知のP8-CODEX-010と同一である。

```text
tests/unit/conversation/test_conversation_generation.py
  test_manual_web_evidence_is_injected_as_an_untrusted_tool_message
  test_manual_web_evidence_and_documentation_rag_are_both_injected_in_the_same_turn
  test_guardrail_context_source_hook_also_governs_manual_web_evidence
```

Network制限環境でTestだけが実DNSへ到達する非Hermetic構成であり、今回のRW6 Regressionではない。P8-ACC-039は既知FAILのまま保持する。

## 5. Controller Disposition

```yaml
rw6_core_runtime_regression: none_detected
p8_codex_005: resolved
p8_codex_006: resolved
p8_codex_007: resolved_with_non_blocking_contract_gap
p8_codex_008: partially_resolved
new_major_findings: 1
new_non_blocking_findings: 1
user_manual_ready: false
phase_8_closure_ready: false
implementation_authority_exercised_by_controller: false
```

Exact Next Actionは、P8-CODEX-012だけを限定Reworkし、P8-CODEX-011は未解決Registryへ送ることである。
新しいConstitution Engine、Production ActivationまたはPhase 9作業へScopeを広げない。
