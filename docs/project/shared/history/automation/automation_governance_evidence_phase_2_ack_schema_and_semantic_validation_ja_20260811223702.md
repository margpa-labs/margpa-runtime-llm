# Automation Governance Evidence — ACK Schema／Semantic Validation

```yaml
document_id: automation_governance_evidence_phase_2_ack_schema_and_semantic_validation_20260811223702
status: append_only_history_event
phase: phase_2
subphase: phase_2_0
work_unit: P2-0-WU-003
created_at: 2026-08-11 22:37:02 JST
language: ja
from_role: プロジェクト責任者兼設計統括者役
to_role:
  - user
  - future_automation_governance_compiler
observation_id: OGE-P2PILOT-020
normative: false
```

## 1. Observation

ACK対象SchemaがSource ArtifactのFieldと一致せず、Taskは欠落を自然言語で明示しながらStatusを`ACKNOWLEDGED`とした。Controllerが個別Fieldを意味照合したことで、Capability開始前に不整合を検知し、Mutation 0のまま停止できた。

```text
Source Contract Completeness : FAIL
Child Status Label            : ACKNOWLEDGED
Child Semantic Content        : MISSING FIELD DISCLOSED
Controller Semantic Review    : REJECTED
Tool／Read／Write              : 0
```

## 2. Reusable Finding — Status Label Is Not Evidence by Itself

```text
ACK_STATUS == ACKNOWLEDGED
  != Every Required Field Exists
  != Every Field Is Exact
  != Contract Is Internally Consistent
  != Capability May Start
```

ACK GateはStatus Labelだけで通過させず、Required Field Set、Source Schema、Exact Value、Unknown／N/A表現、Open QuestionおよびStop Contractを上位Roleが意味照合する。

## 3. Reusable Finding — Projection Completeness

Handoff／Receipt／Prompt間でFieldを投影する場合、送信先へ要求するFieldは送信元Sourceに存在しなければならない。存在しないFieldを必須化する場合は、Activation前にSource SchemaをAppend-only Correctionで明示的に補う。

```text
Canonical Source Field
  -> Freeze Artifact Field
  -> In-band Prompt Field
  -> Task ACK Field
  -> Controller Semantic Comparison
```

各段階でField名、Optionality、`N/A`の許否、RevisionおよびDigest責務を一致させる。

## 4. Dual-layer Fail-closed

Child自身のFail-closedと、Parent／Controllerによる独立Fail-closedを別Controlとして保持する。Childが誤ってPASSを返しても、ControllerがFieldの意味不一致を検出した場合はCapabilityを開始しない。

本事例ではChild Fail-closedは失敗し、Controller Fail-closedが事故を防止した。成功ログだけでなく、このようなNear MissをAutomation／Constitution候補Evidenceへ残す。

## 5. Correction Principle

- 既存History／Receiptを上書きしない。
- Correction Artifactを新規作成し、Supersedes関係を明示する。
- Correction後は同じTaskへNo-tool ACKだけを再要求する。
- ACK再合格を過去のStart Authorizationへ読み替えない。
- Read／Write Capabilityには別のUser Startを必要とする。

## 6. Classification

```text
RULE_EFFECTIVE   : Controller independent semantic review
RULE_AMBIGUOUS   : Receipt Revision optionality／ACK schema projection
RULE_MISSING     : Source-to-ACK field completeness check
NEAR_MISS        : Child acknowledged despite missing required field
HUMAN_GATE       : Start remains separately user-controlled
```

## 7. Non-elevation

本記録は最上位規則、憲法正本または実行可能Ruleへ自動昇格しない。Phase 2／3の追加EvidenceとHuman Reviewを経て、将来のRule ID、Schema ValidationまたはProvider-neutral ACK Validator候補として扱う。

## 8. Evidence

- [Phase-specific ACK Review](../../../phases/phase_2/history/operations/phase_2_0_bounded_write_initial_ack_review_p2_0_wu_003_20260811223702.md)
- [Original Freeze Receipt](../../../phases/phase_2/history/operations/phase_2_0_bounded_documentation_write_freeze_receipt_p2_0_wu_003_20260811222544.md)
