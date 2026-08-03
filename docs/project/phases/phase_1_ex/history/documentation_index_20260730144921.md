# Phase 1-ex Documentation Index Snapshot

```yaml
document_id: phase_1_ex_documentation_index_snapshot
snapshot: 20260730144921
state_at: 2026-07-30 14:49:21 JST
status: current_snapshot
snapshot_of:
  - ../phase_index_ja.md
  - ../adr/adr_0027_public_demo_minimal_access_and_deferred_control_hooks_ja.md
  - ../requirements/public_demo_minimal_access_and_runtime_portability_requirements_ja.md
  - ../architecture/public_demo_access_profile_and_runtime_portability_architecture_ja.md
supersedes: documentation_index_20260728000358.md
source: public_demo_scope_reduction_and_runtime_portability
```

本Snapshotは[2026-07-28 00:03:58版](documentation_index_20260728000358.md)までの全状態を継承する。

## Added Stable Artifacts

- [ADR-0027 Public Demo最小公開／制限Hook延期／Runtime交換性](../adr/adr_0027_public_demo_minimal_access_and_deferred_control_hooks_ja.md)
- [Public Demo最小公開／RAG分離／Runtime交換性 Requirements](../requirements/public_demo_minimal_access_and_runtime_portability_requirements_ja.md)
- [Public Demo Access Profile／RAG分離／Runtime交換 Architecture](../architecture/public_demo_access_profile_and_runtime_portability_architecture_ja.md)

## Added Event／Handoff Artifacts

- [Public Demo Scope Reduction／Runtime Portability Decision](operations/public_demo_scope_reduction_and_runtime_portability_decision_20260730144921.md)
- [Implementer Handoff](handoffs/implementer_handoff_phase_1_ex_public_demo_minimal_access_and_runtime_portability_20260730144921.md)
- [Phase Index Before](operations/phase_index_phase_1_ex_before_public_demo_minimal_access_and_runtime_portability_ja_20260730144921.md)
- [Phase Index After](operations/phase_index_phase_1_ex_after_public_demo_minimal_access_and_runtime_portability_ja_20260730144921.md)

## Accepted Decision

```text
Basic Preview:
  KEEP
  Authentication = Basic
  Documentation RAG = Future Eligible

Public Demo:
  SEPARATE ACCESS PROFILE
  Authentication = None
  Documentation RAG = Denied

Public-specific Controls:
  Rate Limit = Off Hook
  Generation Budget = Off Hook
  Cooldown = Off Hook
  Additional Token Hard Cap = Not Required
  Cost Guard = Off Hook

Existing Runtime Safety:
  KEEP

Model／Deployment／Access／Feature／Lifecycle:
  SEPARATE
```

## Implementation Boundary

実装担当はAccepted Handoffに基づき、Project内の明示Scopeだけを変更できる。

Lightning API Builder、Public URL、Port、Private Bootstrap、Managed Secrets、Sleep／Wake、Cloud、Home Server、Model Artifact、GitおよびGitHubはユーザー担当または今回Scope外である。

匿名Public Accessの有効化はRepository実装と設計統括者Review後にユーザーが判断する。

## Integrity

```text
ADR-0027:
fe9c9103a0b8f646b782b0f15a54504fdc755a54a69dd0cb7e3baa390453cb77f3bbc9b4a8a0eab1b2435c35089120614a3d283d55c0b60d11a6c3c4c5d12dd6

Requirements:
c94c1b690797c12fad5bb0c32e12b0b9918f860a3a4cc2ebeb29a57881c2cedbe75b592bb6943e3c28350e2bf05b72f3a05ed5caa53ecd9bdd75a9f378cbae67

Architecture:
2fcddbfb6cd932eb356466ef66b6f064c7e2403402ff2ca697849e7a816b6c7401480e02bd2b08611eca46fd8bc607a4eb7de4be949058c9bd3926eb43610ae6

Decision Record:
552663e5dc4c0eb9e6788bc3e3bd80ab7959ac338092cd84d32195f62f6aa322755483b7a17ca524304416cf574cef8756f257fe4117c0e13027f3604c3f68d2

Implementer Handoff:
163d5ffa6178115a7f9865c267a2a96aca44a3b51a5039be019b85b9b6c356641e9a36cce5153330759cf3e85bf43a1d4b8f9e0ae61b8202df0fd8016e239636

Phase Index Before:
e040d54d74dfdb1ded3e45c61d49da68cc607c980a7ffdea2d5f80cd92446ebf4e297e2322686477f4d6ed033c66a5c4e9cebfeec0109e7f99debd4d391f2338

Phase Index After／Stable:
67fff441677412c4e5e2aec2f951b597247ad5ee797497ba564d913eef58dec211237bbdb2a5d6adb5facfa829f662cd423a3a5023ea7c9d164458ba40c0478e
```

## Validation Scope

- 新規文書だけを追加した。
- Phase Indexは変更前後の完全原文Snapshotを保存した。
- 旧ADR、Requirements、Architecture、HistoryおよびHandoffを変更していない。
- Source、Config、Script、Test、Model、EnvironmentおよびProject外を変更していない。
- Git、GitHubおよびLightningへ変更操作を行っていない。

