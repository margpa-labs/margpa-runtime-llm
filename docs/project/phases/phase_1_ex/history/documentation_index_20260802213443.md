# Phase 1-ex Documentation Index Snapshot

```yaml
document_id: phase_1_ex_documentation_index_snapshot
snapshot: 20260802213443
state_at: 2026-08-02 21:34:43 JST
status: current_snapshot
snapshot_of:
  - ../phase_index_ja.md
  - ../../../current/documentation_index_ja.md
  - ../../../shared/operations/task_execution_routing_and_cost_control_ja.md
  - ../../../shared/operations/experimental_document_driven_codex_task_orchestration_ja.md
supersedes: documentation_index_20260802210438.md
source: user_requested_future_document_driven_codex_task_orchestration_experiment_reservation
```

本Snapshotは[2026-08-02 21:04:38版](documentation_index_20260802210438.md)までの全状態を継承し、Codex Desktopにおける独立Task作成、Document-driven Handoff、進捗待機、ReviewおよびFollow-upを将来実験候補としてAppend-onlyで記録する。

## 1. Current Decision

```text
Capability Concept Confirmation : complete
Operational Adoption            : not started
Candidate Pilot                 : Phase 2専用設計担当者役
Independent Task Creation       : not executed
Sub-agent Dispatch              : not executed
Automatic Task Creation         : prohibited
Required Start Condition        : explicit user request
```

本予約は、「設計統括者役が必要な独立Taskを作り、IndexとHandoffを同時に渡し、Acknowledgement後に進捗を待ち、ReviewとFollow-upまで連結する」運用の将来実験枠である。現在のPhase 1-ex運用への適用許可ではない。

## 2. Independent TaskとSub-agentの分離

```text
Independent Codex Task:
  ユーザーがSidebar上で所有する継続的な担当Task。
  Phase設計担当者役のような、独立した責任境界と継続的なHandoffを必要とする役割の候補。

Sub-agent:
  現在Task内の限定された並行作業単位。
  Read-only Inventory、Link検証、独立した証跡照合などの有界なSubtask候補。
```

両者は置き換えない。独立Taskを作る場合でも、権限、開始条件、正本、書込範囲、受入条件、停止条件およびユーザー承認GateはDocsに固定する。

## 3. Stable Updates

- [Experimental Document-driven Codex Task Orchestration](../../../shared/operations/experimental_document_driven_codex_task_orchestration_ja.md)
- [Task Execution Routing・Cost Control](../../../shared/operations/task_execution_routing_and_cost_control_ja.md)
- [Phase 1-ex Index](../phase_index_ja.md)
- [Current Documentation Index](../../../current/documentation_index_ja.md)

## 4. Stable History

### Before

- [Task Routing Before](../../../shared/history/operations/task_execution_routing_and_cost_control_phase_1_ex_before_document_driven_task_orchestration_experiment_ja_20260802213443.md)
- [Phase Index Before](operations/phase_index_phase_1_ex_before_document_driven_task_orchestration_experiment_ja_20260802213443.md)
- [Current Index Before](../../../current/history/index/documentation_index_phase_1_ex_before_document_driven_task_orchestration_experiment_ja_20260802213443.md)

### After

- [Task Routing After](../../../shared/history/operations/task_execution_routing_and_cost_control_phase_1_ex_after_document_driven_task_orchestration_experiment_ja_20260802213443.md)
- [Experiment Reservation Snapshot](../../../shared/history/operations/experimental_document_driven_codex_task_orchestration_phase_1_ex_ja_20260802213443.md)
- [Phase Index After](operations/phase_index_phase_1_ex_after_document_driven_task_orchestration_experiment_ja_20260802213443.md)
- [Current Index After](../../../current/history/index/documentation_index_phase_1_ex_after_document_driven_task_orchestration_experiment_ja_20260802213443.md)

## 5. SHA-512

```text
Previous Documentation Index:
  90e64de5f7f08ee4a2f84d3e20c5b0669da775f13114959b70a58d54530a28a2f2012cdaa3a28459945024d8e4fa014547b2f83a0f3dda25d0b89def33b04dec

Task Execution Routing・Cost Control Before:
  9150608fe3761f38c21b969b9b308bfacc519c47cd8d3ff04ff4d2ab4d5f00376291b1d301c592b36d0f1b27753e617df5637c48736d26a81630f669cab5d59d

Task Execution Routing・Cost Control After:
  01e7c23d17d8d8bfd35f5a3d1834835c6cf24d1ff3c24af4d87d563fd76a004d340f8254641723e7cec476fb9a34e6d6ac6c97acdf9bdf1621ae213238d2e4a2

Experimental Document-driven Codex Task Orchestration:
  5da5627a20f4b6a23214df8c388a39e8e35370bd89907b7b94e79441baed75335ee4e7a0c45b30389cc3aa1e7e43bee49bb8d92a3796058afc2e9a3cc9eb1493

Phase 1-ex Index Before:
  b84a95d76e4fddfeb523ad1f0a4b5124432ab4f49d7fbc466b273c67a207e2bc0b664622eebc351e2000cae3c20a99c420240703a795072ab49f7ccea609458d

Phase 1-ex Index After:
  2866068a51f0cae634946869282244ddde357cd18382bff6b8017f1d0b0497ffd1e2097324b2cba1ffa508d261b077fe051d8ca1f2b536307417fd4b2d90e366

Current Documentation Index Before:
  dd79a7bb8782edae5e1305bfe33a5bfeb715276df772fc650d1aef768f0afbf032b5ab837318097d3f50649f80f26f6c7a00ccaf4cb1b4d20b91936afaece9e9

Current Documentation Index After:
  a7fe2875d2fbfc9f48c32c22bceae69f3214bd5a69d19ac78b71914b958991f8e53f53cb809cacb82e747d74423229256a4d4386a31063be5e270faab7b3d958
```

## 6. Mutation Boundary

```text
Project Source・Config・Tests : unchanged
Root Public Artifacts         : unchanged
Git Operation                 : none
GitHub Operation              : none
External Filesystem Operation : none
Independent Task Creation     : none
Sub-agent Dispatch            : none
Credential・Personal Data     : not recorded
```

## 7. Future Pilot Gate

Phase 2専用設計担当者役を候補とし、ユーザーが実験開始を明示的に依頼した後にだけ、開始時点のDocs構造、Authority、Handoff、Acknowledgement、Review、停止およびRollback条件を再確認する。それまで本件は「いずれやってみたい運用」の予約状態を維持する。
