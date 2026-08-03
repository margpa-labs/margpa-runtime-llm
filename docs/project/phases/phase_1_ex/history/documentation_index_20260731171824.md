# Phase 1-ex Documentation Index Snapshot

```yaml
document_id: phase_1_ex_documentation_index_snapshot
snapshot: 20260731171824
state_at: 2026-07-31 17:18:24 JST
status: current_snapshot
snapshot_of:
  - ../phase_index_ja.md
  - ../requirements/mac_local_documentation_rag_requirements_ja.md
  - ../architecture/mac_local_documentation_rag_technology_selection_ja.md
  - ../architecture/mac_local_documentation_rag_architecture_ja.md
  - ../adr/adr_0028_mac_local_sparse_documentation_rag_and_external_adapter_hook_ja.md
supersedes: documentation_index_20260730231339.md
source: mac_local_documentation_rag_design
```

本Snapshotは[2026-07-30 23:13:39版](documentation_index_20260730231339.md)までの全状態を継承する。

Phase Index Stableは今回変更していない。

Mac限定簡易Documentation RAGについて、Requirements、Technology Selection、ArchitectureおよびProposed ADRを新規作成した。

## Added Stable Design Documents

- [Mac限定簡易Documentation RAG 要件定義](../requirements/mac_local_documentation_rag_requirements_ja.md)
- [Mac限定簡易Documentation RAG 技術選定](../architecture/mac_local_documentation_rag_technology_selection_ja.md)
- [Mac限定簡易Documentation RAG Architecture](../architecture/mac_local_documentation_rag_architecture_ja.md)
- [ADR-0028: Mac限定Sparse Documentation RAG／External Adapter Hook](../adr/adr_0028_mac_local_sparse_documentation_rag_and_external_adapter_hook_ja.md)

## Proposed Design Decision

```text
Initial Runtime:
  Local Mac

Initial Retrieval:
  Deterministic Lexical BM25-style

Japanese Retrieval:
  Unicode NFKC＋2-gram／3-gram

Index:
  In-memory／Lazy Build／No Persistent Write

Integrity:
  SHA-512 Document／Chunk／Manifest

New Runtime Dependency:
  None

New Model:
  None

Default Corpus:
  Canonical／Stable Markdown

Default Exclusion:
  history／lossless／hidden／temporary／symlink

Citation:
  System-derived／Model textと分離

Public Demo:
  DENIED／Adapterを生成しない

External Runtime:
  Hook Only
```

## Port Boundary

```text
DocumentSourcePort
ChunkerPort
EmbeddingPort
IndexStorePort
RetrieverPort
ContextAssemblerPort
CitationPort
```

初期Lexical実装は`EmbeddingPort`を呼ばない。

Embedding、Dense Retrieval、Hybrid Retrieval、Persistent Index、Lightning、Home ServerおよびCloudは、後からAdapter追加できる境界として維持する。

## Safety Boundary

- Documentation RAGはDefault OFF。
- OFF時はZero Load／Zero Call／Zero Write／Zero Side Effect。
- Docs本文は非信頼の参照Dataであり、Runtime Policyまたは権限を生成しない。
- SourceはProject Root配下のAllowlistへ限定する。
- Browser ResponseおよびCitationへAbsolute Pathを出さない。
- Public DemoではCapability Resolution後、Filesystem Scan以前にRAG Compositionを終了する。
- Docs不在時はModelで推測せず、指定されたSafe Messageを返す。

## Current Corpus Observation

設計時点のCanonical／Stable Markdown Candidate：

```text
Document Count:
  38

Total Size:
  approximately 3.1 MiB
```

Phase 1のCompiled文書が大部分を占める。

`history/`および`lossless/`をDefault Corpusへ含めないことは、情報削除ではなく、通常検索と保存証跡を分離するDecisionである。

## Status

```text
Requirements:
  PROPOSED FOR REVIEW

Technology Selection:
  PROPOSED FOR REVIEW

Architecture:
  PROPOSED FOR REVIEW

ADR-0028:
  PROPOSED

Implementation:
  NOT AUTHORIZED

Implementer Handoff:
  NOT CREATED
```

## Acceptance Gate Before Implementation

1. ユーザーが設計内容を確認する。
2. 必要な修正を新しい設計状態として反映する。
3. ADR-0028 Accepted後継状態を作る。
4. 実装担当向けHandoffと新しいDocumentation Indexを作る。
5. 実装担当はHandoff後にだけSource／Test／Configを変更する。

## Integrity

```text
Previous Documentation Index:
75340211f191fd59a2bb753540a10e98ad978c5dfab44c831c63432dbbe7143397b7cddf9a0d8ed482f6241f1cee9b237d476971dcc24dcbe67bf41d7bcf7ead

Phase Index Stable／Unchanged:
67fff441677412c4e5e2aec2f951b597247ad5ee797497ba564d913eef58dec211237bbdb2a5d6adb5facfa829f662cd423a3a5023ea7c9d164458ba40c0478e

Requirements:
4f08dce7e24e628c8ab40973853c2034fa87a0bb441279f3ca8d8bf4d5c4a0b0314d98b955d429177e217bf49e78214df2b933aa1e907c8ce032c2b84faaa479

Technology Selection:
bfac8068bf8124d9a997fd6faed0e1414805796456937468f96207743a721c50fab9be327abb2dab9fa874572d2414fdb1105f4434209325661b9adb32b7e91e

Architecture:
7d48bb8abdfd7b46ae9466c0272d1be95d3373d8aef9e2c0f8493af61d5415b12a8f20d04e33e33bb6e080918920d79fb278c06546fa6d7e803dac121a5b7fa9

ADR-0028:
e169dc713d98018bfaf581a6e8e276bdf2c4b6ffdc438b2118acc3553c03bfa28d54badd3abf79e5b131713fd132439b8f003f79b47621df6d181afb24a5e89b
```

## Validation Scope

- Requirements、Technology Selection、Architecture、ADRおよび本Indexを新規追加した。
- 既存Docsを上書きしていない。
- Phase Index Stableを変更していない。
- Source、Config、Script、TestおよびModelを変更していない。
- Dependencyを追加していない。
- ModelをDownloadしていない。
- Public URL、Credentialまたは個人識別情報を保存していない。
- Project Root外へ触れていない。
- Lightning、GitおよびGitHubを変更していない。

