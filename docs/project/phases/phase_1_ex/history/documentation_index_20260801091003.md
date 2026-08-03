# Phase 1-ex Documentation Index Snapshot

```yaml
document_id: phase_1_ex_documentation_index_snapshot
snapshot: 20260801091003
state_at: 2026-08-01 09:10:03 JST
status: current_snapshot
snapshot_of:
  - ../phase_index_ja.md
  - documentation_index_20260801090159.md
  - operations/retrieval_guidance_hardcode_and_maintenance_reconsideration_20260801091003.md
  - ../requirements/lightning_public_corpus_documentation_rag_multi_access_requirements_ja.md
  - ../architecture/lightning_public_corpus_documentation_rag_multi_access_architecture_ja.md
  - ../adr/adr_0030_lightning_public_corpus_documentation_rag_multi_access_ja.md
  - handoffs/implementer_handoff_phase_1_ex_lightning_public_corpus_documentation_rag_multi_access_20260801091003.md
supersedes: documentation_index_20260801090159.md
source: public_corpus_rag_multi_access_redesign_and_retrieval_guidance_reconsideration
```

本Snapshotは[2026-08-01 09:01:59版](documentation_index_20260801090159.md)までの全状態を継承し、Retrieval Guidance Hard-code／Maintenance再検討、Lightning Public Corpus RAG Multi-access後継要件、Architecture、ADR-0030および実装担当HandoffをAppend-onlyで追加する。

旧ADR、Requirements、Architecture、Handoff、Review、EvidenceおよびIndexは、各時点の判断を示すHistoryとして保持し、編集または削除しない。

## 1. Retrieval Guidance Decision Update

- [Retrieval Guidance Hard-code／Maintenance再検討Record](operations/retrieval_guidance_hardcode_and_maintenance_reconsideration_20260801091003.md)

```text
Manual hit-keyword table:
  NOT SELECTED

Model-reference index table:
  NOT SELECTED

Project-specific subject mapping:
  NOT AUTHORIZED

Reason:
  hard-code
  maintenance burden
  stale mapping
  multilingual synchronization
  corpus overfitting

Future:
  redesign when RAG quality work resumes
```

前Indexで示したRetrieval Metadataは、実装予約ではなく未確定比較候補として扱う。

## 2. Multi-access Design

- [Multi-access Requirements](../requirements/lightning_public_corpus_documentation_rag_multi_access_requirements_ja.md)
- [Multi-access Architecture](../architecture/lightning_public_corpus_documentation_rag_multi_access_architecture_ja.md)
- [ADR-0030](../adr/adr_0030_lightning_public_corpus_documentation_rag_multi_access_ja.md)

最新Decision：

```text
Basic Preview:
  Basic authentication
  public 8-doc RAG eligible

Public Demo:
  authentication none
  public 8-doc RAG eligible

Shared corpus:
  exact 8 public files
  default OFF

Internal docs:
  unavailable from both Lightning access surfaces
```

## 3. Superseded Design

次はHistoryとして残るが、実装指示としてはSupersededである。

```text
ADR-0029:
  Basic Preview only／Public Demo denied

lightning_basic_preview_public_corpus_documentation_rag_requirements_ja.md
lightning_basic_preview_public_corpus_documentation_rag_adapter_hook_architecture_ja.md
implementer_handoff_phase_1_ex_lightning_basic_preview_public_corpus_documentation_rag_adapter_hook_20260801090159.md

ADR-0027 Section 4:
  Public Demo RAG denied
```

維持するのはAccess分離、Credential境界、Public Control Hook OFF、非永続性、Runtime交換性およびユーザーのPlatform Authorityである。

## 4. Effective Implementer Handoff

- [実装担当向けMulti-access Handoff](handoffs/implementer_handoff_phase_1_ex_lightning_public_corpus_documentation_rag_multi_access_20260801091003.md)

```text
Repository implementation:
  AUTHORIZED WITHIN EXPLICIT SCOPE

Lightning operation:
  USER ONLY

Public docs content mutation:
  DENIED

Internal docs exposure:
  DENIED

New dependency／persistent index／extra model:
  DENIED

Git／GitHub:
  DENIED
```

## 5. Integrity

```text
Previous Documentation Index:
  419da507fc3b9871d11f528e26270999e40d569153ec8ee8c40c794456668a0c49aa201ae7243808dfb8816a47be1ace900819ddbf41fd476f6e45fbbc794726

Phase Index Stable／Unchanged:
  67fff441677412c4e5e2aec2f951b597247ad5ee797497ba564d913eef58dec211237bbdb2a5d6adb5facfa829f662cd423a3a5023ea7c9d164458ba40c0478e

Basic Preview Web Profile Baseline:
  3b0c9ab2530322a2bd825b1afba139a8ccc8e80c7127d08fdf6b81e9e7732e13ea7344213491806002aeb9569609de02e30f623a4a548dc53c4c3453d9c21b21

Public Demo Web Profile Baseline:
  09db3c8045d2912434358d7cb6d3be70f7d78ccc083a6fee099ee94876bdd47cb2e0d3bb448d3710f5dc254e2dca8b25d4a7b1441acab2629eaa239051726b0e

Web Access Profile Code Baseline:
  554eaf66f4243608063a7cd9eecd02dd4ee8e65d5f40d553322c7c33c1877a7eec4e892e89211fa3d00dff5f60093f178442953e848fe23c1bed252124e4805b
```

本Index後に作成した新規文書のHashは、次のImplementer Status／Designer Review／Append-only Indexで固定する。

## 6. Next Gate

実装担当は最新Handoffだけを実装指示として使用し、Repository実装と自動Testを行う。

設計統括者役Review後、Lightning上の配置、Test、Preflight、Basic Preview、Public DemoおよびSleep／Wakeはユーザーが手動で行う。
