# Phase 1-ex Documentation Index Snapshot

```yaml
document_id: phase_1_ex_documentation_index_snapshot
snapshot: 20260731172259
state_at: 2026-07-31 17:22:59 JST
status: current_snapshot
snapshot_of:
  - ../phase_index_ja.md
  - ../requirements/mac_local_documentation_rag_requirements_ja.md
  - ../architecture/mac_local_documentation_rag_technology_selection_ja.md
  - ../architecture/mac_local_documentation_rag_architecture_ja.md
  - ../adr/adr_0028_mac_local_sparse_documentation_rag_and_external_adapter_hook_ja.md
  - handoffs/implementer_handoff_phase_1_ex_mac_local_documentation_rag_20260731172259.md
supersedes: documentation_index_20260731171824.md
source: mac_local_documentation_rag_acceptance_and_implementer_handoff
```

本Snapshotは[2026-07-31 17:18:24版](documentation_index_20260731171824.md)までの全状態を継承する。

ユーザーの明示承認により、Mac限定簡易Documentation RAGのRequirements、Technology Selection、ArchitectureおよびADR-0028をAccepted状態へ移行した。

実装担当向けAccepted HandoffをAppend-onlyで新規作成した。

Phase Index Stableは今回変更していない。

## Accepted Stable Documents

- [Mac限定簡易Documentation RAG 要件定義](../requirements/mac_local_documentation_rag_requirements_ja.md)
- [Mac限定簡易Documentation RAG 技術選定](../architecture/mac_local_documentation_rag_technology_selection_ja.md)
- [Mac限定簡易Documentation RAG Architecture](../architecture/mac_local_documentation_rag_architecture_ja.md)
- [ADR-0028: Mac限定Sparse Documentation RAG／External Adapter Hook](../adr/adr_0028_mac_local_sparse_documentation_rag_and_external_adapter_hook_ja.md)

## Accepted Implementer Handoff

- [実装担当向け Phase 1-ex Mac限定簡易Documentation RAG Handoff](handoffs/implementer_handoff_phase_1_ex_mac_local_documentation_rag_20260731172259.md)

## Before-update History Snapshots

- [Requirements Proposed Snapshot](requirements/mac_local_documentation_rag_requirements_20260731172259.md)
- [Technology Selection Proposed Snapshot](architecture/mac_local_documentation_rag_technology_selection_20260731172259.md)
- [Architecture Proposed Snapshot](architecture/mac_local_documentation_rag_architecture_20260731172259.md)
- [ADR-0028 Proposed Snapshot](adr/adr_0028_mac_local_sparse_documentation_rag_and_external_adapter_hook_20260731172259.md)

Before Snapshotは、Stable文書のAccepted更新前内容を一切再解釈せず、そのまま保存した。

## Accepted Decision

```text
Initial Runtime:
  Local Mac

Retrieval:
  Deterministic Sparse／Lexical BM25-style

Japanese Search:
  Unicode NFKC＋2-gram／3-gram

Index:
  In-memory／Lazy Build／No Persistent Write

New Runtime Dependency:
  None

New Model:
  None

Citation:
  System-derived

Local UI:
  Available／Default OFF

Basic Preview:
  Eligible／Initial External Adapter not bound

Public Demo:
  Denied／Adapter not constructed

External Runtime:
  Hook Only
```

## Implementation Authority

```text
Repository Implementation:
  AUTHORIZED WITH ACCEPTED HANDOFF

Project Root Outside Operation:
  DENIED

Dependency Install:
  DENIED

Model Download:
  DENIED

Lightning Mutation:
  DENIED

Public Demo RAG:
  DENIED

Git／GitHub:
  DENIED
```

実装担当はHandoffのAuthorized Mutation Scope、Prohibited Actions、Required TestsおよびStatus Contractに従う。

## Required Implementer Result

```text
docs/project/phases/phase_1_ex/history/handoffs/
implementer_status_phase_1_ex_mac_local_documentation_rag_YYYYMMDDHHMMSS.md
```

実装完了後、設計統括者役はStatus、Source、Config、Test、Security BoundaryおよびLocal Model SmokeをReviewする。

## Stable Integrity

```text
Requirements／Accepted:
7ef26d2458ef481d47b0fa53dc5e8ec7e9da1d81c29bc35d0704245eb6cccb97b2ddfcc64e8a15b2071e3ea66a0eebe16fa081979d17f14eed791a4b1c6999be

Technology Selection／Accepted:
56203c926ccf5cc99b04f3db210f1fb46aaedcccf30d55df70f5e3177f6b9970632ad1e87f8c7aa5a427561c43a5a34fbb88ef817a42ea91b2c68534ff347f53

Architecture／Accepted:
0c7a27dd0cfa707a12654416576e357a49c52dc908b73a6d9dfc7ba1c85738c39ab46623a6e3fbaedd2a842b5486b5d6039272e1edb6a4f74aed43a317b49b0a

ADR-0028／Accepted:
d2bee3efabbf8a7a025ba2fa4d6da462bbcb85160a5fa2458a9ff7996df0bbcfbbbfdb74d9d7516b0311b7c54309686646f2b9e962a8fe4c59c234ecc8fa2f9b

Implementer Handoff:
3e910e040948bccd6ed81f79050547265709851091c086bcf19b7d16e7bb728d151cb42a503eb220a03a7ed994782d82e155e47639fd4555cfc1e5619c80493a
```

## Proposed Snapshot Integrity

```text
Requirements／Proposed:
4f08dce7e24e628c8ab40973853c2034fa87a0bb441279f3ca8d8bf4d5c4a0b0314d98b955d429177e217bf49e78214df2b933aa1e907c8ce032c2b84faaa479

Technology Selection／Proposed:
bfac8068bf8124d9a997fd6faed0e1414805796456937468f96207743a721c50fab9be327abb2dab9fa874572d2414fdb1105f4434209325661b9adb32b7e91e

Architecture／Proposed:
7d48bb8abdfd7b46ae9466c0272d1be95d3373d8aef9e2c0f8493af61d5415b12a8f20d04e33e33bb6e080918920d79fb278c06546fa6d7e803dac121a5b7fa9

ADR-0028／Proposed:
e169dc713d98018bfaf581a6e8e276bdf2c4b6ffdc438b2118acc3553c03bfa28d54badd3abf79e5b131713fd132439b8f003f79b47621df6d181afb24a5e89b
```

## Previous Integrity

```text
Previous Documentation Index:
a45f44fce1a73743635e08c0c15deab067eb4498f65e06bad530d455747ec5ce2943c8456960b13bfe796a11e7b3e93f8a6719ddc65b2ca288b417b5c9fe1e9d

Phase Index Stable／Unchanged:
67fff441677412c4e5e2aec2f951b597247ad5ee797497ba564d913eef58dec211237bbdb2a5d6adb5facfa829f662cd423a3a5023ea7c9d164458ba40c0478e
```

## Validation Scope

- Proposed版4文書をBefore Historyへ保存した。
- Stable4文書の状態をAcceptedへ更新した。
- Accepted Handoffと本Indexを新規追加した。
- Proposed SnapshotのSHA-512が更新前Stable Digestと一致することを確認した。
- Source、Config、Script、TestおよびModelを変更していない。
- Dependencyを追加していない。
- ModelをDownloadしていない。
- Public URL、Credentialまたは個人識別情報を保存していない。
- Project Root外へ触れていない。
- Lightning、GitおよびGitHubを変更していない。

