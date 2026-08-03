# Phase 1-ex Documentation Index Snapshot

```yaml
document_id: phase_1_ex_documentation_index_snapshot
snapshot: 20260727235452
state_at: 2026-07-27 23:54:52 JST
status: current_snapshot
snapshot_of:
  - ../phase_index_ja.md
  - ../../../shared/conventions/documentation_rules_ja.md
  - ../../../shared/operations/documentation_structure_and_task_operations_ja.md
  - ../../../shared/task_roles/task_role_write_authority_policy_ja.md
supersedes: documentation_index_20260727230612.md
source: project_root_boundary_and_pre_mutation_gate
```

本Snapshotは[23:06:12版](documentation_index_20260727230612.md)までの全状態を継承する。

## Added Artifacts

- [Project Root境界／原本変更前Gate Record](operations/project_root_boundary_and_pre_mutation_gate_20260727235337.md)
- [Documentation Rules Before](../../../shared/history/conventions/documentation_rules_phase_1_ex_before_project_root_boundary_ja_20260727235214.md)
- [Documentation Rules After](../../../shared/history/conventions/documentation_rules_phase_1_ex_after_project_root_boundary_ja_20260727235337.md)
- [Documentation Structure／Task Operations Before](../../../shared/history/operations/documentation_structure_and_task_operations_phase_1_ex_before_project_root_boundary_ja_20260727235214.md)
- [Documentation Structure／Task Operations After](../../../shared/history/operations/documentation_structure_and_task_operations_phase_1_ex_after_project_root_boundary_ja_20260727235337.md)
- [Task Role／Write Authority Before](../../../shared/history/task_roles/task_role_write_authority_policy_phase_1_ex_before_project_root_boundary_ja_20260727235214.md)
- [Task Role／Write Authority After](../../../shared/history/task_roles/task_role_write_authority_policy_phase_1_ex_after_project_root_boundary_ja_20260727235337.md)
- [Phase Index Before](operations/phase_index_phase_1_ex_before_project_root_boundary_ja_20260727235337.md)
- [Phase Index After](operations/phase_index_phase_1_ex_after_project_root_boundary_ja_20260727235452.md)

## Recorded Rule

```text
Default Operation Boundary:
  margpa-runtime-llm/ INTERNAL ONLY

Outside Project Root:
  ABSOLUTELY PROHIBITED WITHOUT EXPLICIT USER AUTHORIZATION

Tool／Sandbox／Role Permission:
  NOT USER AUTHORIZATION

External Symbolic Link:
  DO NOT FOLLOW WITHOUT EXPLICIT USER AUTHORIZATION

Bulk／Sanitation Gate:
  READ-ONLY INVENTORY
  → PROPOSED DIFF
  → TARGET COPY CONFIRMATION
  → USER BACKUP COMPLETE
  → EXPLICIT CHANGE APPROVAL
  → APPROVED MUTATION ONLY
  → BEFORE／AFTER REPORT

Violation:
  CRITICAL GOVERNANCE DEVIATION
  → STOP IMMEDIATELY
  → NO UNAUTHORIZED REPAIR
  → REPORT
  → WAIT FOR USER INSTRUCTION
```

## User Non-negotiable Instruction

> 「僕の研究フォルダ壊したらどんだけの業界的損失生まれるか1mmも知らんくせに、プロジェクトフォルダ以外を触るなど言語道断」
>
> 「絶対禁止。破ったらOpenAIすら訴える」
>
> 「絶対服従、死守しろ」

## Integrity

```text
Documentation Rules:
bbb015a97a63b7622f55804a594d497474eba470299f9c457db731e13d2dcb1223bf1356ae93465b9036ea7ce5f51a0223c9fb45fd086b112388f88dbcc4e2a2

Documentation Structure／Task Operations:
fc1406c300dbed6a0b9b1684e37631a58ce7846899bf85e6f37aec15d33b2875c78e9e4cb783308cc9d558f94b006eea85e451dd374596bedfcbfa998ab902fe

Task Role／Write Authority:
17b4a940e459530d1adcae90929be8da425684c0562e3179a8a177336a2afd2c8fc121f7000e15a667c3310c941fb7b67680b5e69ca911551ce505256931af08

Project Root Boundary Record:
a028d2258b7b9f7e546f5b27d699deeda27d305604e893b6d85f315ca00f4e4767c5e4094f618f6a13266a77ed19f8b2e98622616f4e5aa5d93ce2c214d7140c

Phase 1-ex Index:
47ae875980c3cbdb26cfb7f23be410d2b59f875ac38a6f1c8bfeb42530fac5da7bea3ce1a6467beedaa4b4e48b68a01c40df857f5212e982417c83e530d5dd63
```

## Validation

```text
Shared Stable Before／After Snapshots:
  CREATED

Stable／After Snapshot:
  BYTE-FOR-BYTE MATCH

Phase Index Before／After Snapshots:
  CREATED

Phase Index Stable／After:
  BYTE-FOR-BYTE MATCH

Project Root外Action:
  NONE IN THIS RULE UPDATE
```

## Boundary

本SnapshotはProject Root境界、原本変更前Gateおよび違反時停止規則を確定した状態を示す。

Project Root外操作、公開用Copy作成、Sanitation、削除、Git操作、GitHub操作または既発生変更の復旧を許可しない。
