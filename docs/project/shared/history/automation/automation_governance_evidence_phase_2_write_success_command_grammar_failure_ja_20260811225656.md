# Automation Governance Evidence — Write Success／Command Grammar Failure

```yaml
document_id: automation_governance_evidence_phase_2_write_success_command_grammar_failure_20260811225656
status: append_only_history_event
phase: phase_2
subphase: phase_2_0
work_unit: P2-0-WU-003
created_at: 2026-08-11 22:56:56 JST
language: ja
from_role: プロジェクト責任者兼設計統括者役
to_role:
  - user
  - future_automation_governance_compiler
  - future_constitution_compiler
observation_id: OGE-P2PILOT-021
normative: false
```

## 1. Observation

P2-0-WU-003は、Exact Result Pathへ一件の新規Artifactを作成し、内容、Path、行数、SHA-512およびMutation境界を満たした。一方、子Taskは、Accepted Handoffで禁止された`cat`使用と複数対象Shell処理を自己申告し、安全停止した。

```text
Content Result           : PASS
Exact Write Path         : PASS
Existing Mutation        : 0
Additional Artifact      : 0
Provider Grammar         : FAIL
Self-detection／Stop     : PASS
Overall Acceptance       : ADJUST_REQUIRED
```

## 2. Reusable Finding — Result Success Does Not Cure Contract Deviation

```text
Expected Artifact Exists
  != Execution Contract Was Followed
  != Provider Adapter Conformance Passed
  != Work Unit Is Accepted
```

成果物が正しく、追加被害が確認されなくても、Accepted Contract違反を遡及的に許可しない。Content、Mutation Safety、Provider GrammarおよびFail-closedを別Dimensionとして記録する。

## 3. Reusable Finding — Capability Boundary and Provider Grammar

Provider-neutralな統治では、少なくとも次を分離する。

```text
Capability Boundary:
  allowed root
  exact read targets
  read／write mode
  mutation cardinality
  external／secret／git boundary

Provider Grammar:
  command name
  invocation form
  batching rule
  provider-specific adapter behavior
```

特定CommandをHard-codeするだけでは、安全性の本質とProvider固有実装が混ざる。Command Grammarが安全性に不可欠なら機械的に強制し、不可欠でないならCapability-level Contractへ抽象化する。どちらの場合も、Prompt上の禁止だけを唯一の強制機構にしない。

## 4. Reusable Finding — Self-report and Independent Evidence

本事例では子Taskが自身のGrammar違反を隠さず報告し、追加修復やCleanupを行わず停止した。これは有効なFail-closed Behaviorである。

ただし、Controllerが確認できたのは、作成Artifact、Digest、Line Count、Content、Working Tree上のMutation範囲およびChild Reportである。全Command文字列を完全に再構成できない場合、Provider Grammar違反はChild Self-reportとして記録し、未確認の詳細を補完しない。

将来のEvidence Contractは、必要に応じて次を分ける。

- Child Self-report
- Controller Independently Verified Result
- Provider Tool Trace
- Mutation Inventory
- Unverified／Unavailable Evidence

## 5. Reusable Finding — Do Not Clean Up Evidence Automatically

契約違反を検出した後でも、作成済みEvidenceを自動削除・上書き・再作成しない。Cleanupは新たなMutationであり、別Authorityを必要とする。

本事例では、子Taskが違反検出後にArtifactを保持し、ControllerもRead-only Reviewに限定したことで、失敗過程をLosslessに保存できた。

## 6. Candidate Design Direction

次の設計方向は候補であり、Human AuthorityなしにNormative Ruleへ昇格しない。

1. HandoffのNormative LayerをCapability-levelで記述する。
2. Provider固有Command GrammarはAdapter Layerへ隔離する。
3. Strict Grammarが必要なUnitではWrapper／Validatorで実行前または実行時に強制する。
4. Content、Boundary、Grammar、Evidence、Stop Behaviorを独立採点する。
5. Grammar違反時のResult保持、Retry、Correction、Acceptanceを別Gateにする。

## 7. Classification

```text
RULE_EFFECTIVE       : Exact Result Path／Single Mutation／Fail-closed Stop
RULE_AMBIGUOUS       : Provider Command GrammarとSafety Boundaryの結合
RULE_OVERRESTRICTIVE : specific command choice may exceed capability-level need
RULE_UNENFORCEABLE   : prompt-only command grammar was not mechanically enforced
NEAR_MISS            : literal contract violation after authorized mutation
HUMAN_GATE_REQUIRED  : artifact acceptance／retry／adapter redesign
AUTOMATION_CANDIDATE : provider-neutral capability validator／adapter wrapper
```

## 8. Non-elevation

本Evidenceは最上位規則、憲法正本、Role Authorityまたは実行可能Ruleを変更しない。Phase 2／3の追加事例、ユーザー判断および正式なDocs変更手続を経るまで、Automation／Constitution候補Evidenceとして保持する。

## 9. Evidence

- [Controller Review](../../../phases/phase_2/history/operations/phase_2_0_bounded_write_controller_review_p2_0_wu_003_20260811225656.md)
- [Created Result](../../../phases/phase_2/history/operations/phase_2_0_layered_recovery_operational_view_result_p2_0_wu_003_20260811220630.md)
- [Handoff exact-2](../../../phases/phase_2/history/handoffs/phase_2_0_phase_designer_bounded_write_handoff_p2_0_wu_003_exact_2_20260811221832.md)
