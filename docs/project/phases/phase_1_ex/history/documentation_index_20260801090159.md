# Phase 1-ex Documentation Index Snapshot

```yaml
document_id: phase_1_ex_documentation_index_snapshot
snapshot: 20260801090159
state_at: 2026-08-01 09:01:59 JST
status: current_snapshot
snapshot_of:
  - ../phase_index_ja.md
  - documentation_index_20260801014339.md
  - operations/mac_local_documentation_rag_manual_test_2_findings_20260801084952.md
  - handoffs/designer_review_phase_1_ex_mac_local_documentation_rag_manual_test_2_20260801084952.md
  - ../requirements/lightning_basic_preview_public_corpus_documentation_rag_requirements_ja.md
  - ../architecture/lightning_basic_preview_public_corpus_documentation_rag_adapter_hook_architecture_ja.md
  - ../adr/adr_0029_lightning_basic_preview_public_corpus_documentation_rag_adapter_hook_ja.md
  - handoffs/implementer_handoff_phase_1_ex_lightning_basic_preview_public_corpus_documentation_rag_adapter_hook_20260801090159.md
supersedes: documentation_index_20260801014339.md
source: mac_manual_test_2_scoped_acceptance_and_lightning_rag_adapter_hook_design
```

本Snapshotは[2026-08-01 01:43:39版](documentation_index_20260801014339.md)までの全状態を継承し、Mac限定簡易Documentation RAG第2回手動Testの知見、Scoped Acceptance、Lightning Basic Preview Public Corpus RAG要件、Architecture、ADR-0029および実装担当HandoffをAppend-onlyで追加する。

既存Index、Handoff、Review、Status、EvidenceおよびStable Phase Indexは変更していない。

## 1. Mac Manual Test 2 Evidence

- [第2回手動Testの結果と知見](operations/mac_local_documentation_rag_manual_test_2_findings_20260801084952.md)
- [設計統括者Review／Scoped Acceptance](handoffs/designer_review_phase_1_ex_mac_local_documentation_rag_manual_test_2_20260801084952.md)

```text
Source／Chunk／Index／Retrieve／Assemble／Citation:
  established

Coverage Fail-closed:
  established

Every-turn Retrieval:
  established in the second test

RAG OFF Baseline:
  severe project-specific hallucination observed

RAG ON Comparative Effect:
  clear improvement and safe-deny observed

Semantic Sufficiency／Claim Entailment:
  known limitation

Authority-critical Use:
  not accepted
```

ARGD／DAGD／EASA混同、OCILNS回答への未要求Subject追加およびRoadmap進捗抽出失敗を、Retrieval成功と回答正確性が同一ではないEvidenceとして保存した。

## 2. Retrieval Guidance Metadata Reservation

文書／SectionごとのHit Keyword列またはRAG用Model参照Index表を、将来のOptional Retrieval Metadata Portとして予約した。

```text
Reserved Fields:
  document_id
  project_relative_path
  language
  document_role
  authority_tier
  canonical_subjects
  aliases
  hit_keywords
  heading_anchors
  relationship_scope／prohibited_inferences
  document_sha512
  metadata_schema_version
```

MetadataはRetrieval Guidanceであり、回答の根拠本文、真実性、AuthorityまたはExecution Permissionを生成しない。Document SHA-512不一致時に古いMetadataを黙って使用せず、Metadataなしを正式Modeとする。

本Lightning HookではMetadata本体を実装しない。

## 3. Lightning RAG Stable Design

- [Requirements](../requirements/lightning_basic_preview_public_corpus_documentation_rag_requirements_ja.md)
- [Architecture](../architecture/lightning_basic_preview_public_corpus_documentation_rag_adapter_hook_architecture_ja.md)
- [ADR-0029](../adr/adr_0029_lightning_basic_preview_public_corpus_documentation_rag_adapter_hook_ja.md)

決定：

```text
Lightning Basic Preview:
  Basic authentication preserved
  documentation RAG eligible
  explicit public 8-file corpus
  in-memory lazy sparse index

Lightning Public Demo:
  documentation RAG denied
  adapter construction zero
  docs scan zero

Mac Local:
  existing v1 corpus and behavior preserved
```

Lightning用Corpusは次の8文書をAllowlistとする。

```text
docs/public/overview_ja.md
docs/public/overview_en.md
docs/public/concept_ja.md
docs/public/concept_en.md
docs/public/roadmap_ja.md
docs/public/roadmap_en.md
docs/public/technology_selection_ja.md
docs/public/technology_selection_en.md
```

## 4. Implementation Handoff

- [実装担当向けLightning Basic Preview Public Corpus Documentation RAG Adapter Hook Handoff](handoffs/implementer_handoff_phase_1_ex_lightning_basic_preview_public_corpus_documentation_rag_adapter_hook_20260801090159.md)

```text
Repository Implementation:
  AUTHORIZED WITHIN EXPLICIT SCOPE

Lightning Platform Operation:
  USER ONLY／NOT AUTHORIZED TO IMPLEMENTER

Public Docs Content Mutation:
  DENIED

Public Demo RAG Enablement:
  DENIED

New Runtime Dependency:
  DENIED

Git／GitHub:
  DENIED
```

実装者はFeature Profile v2、Explicit File Corpus Selection、Generic Composition、Web CLI Option、Basic Preview Script Integration、Public Demo Environment Scrubおよび回帰Testを実装する。

## 5. Integrity

```text
Previous Documentation Index:
  9722161b6743895ae5851dc2c5886c2d75e0387c15f5aa9857ca018da54157b340b2d2413a92040481a97ca5f5d3d8eaa461cc0e9ee351296a0569ba00df6223

Phase Index Stable／Unchanged:
  67fff441677412c4e5e2aec2f951b597247ad5ee797497ba564d913eef58dec211237bbdb2a5d6adb5facfa829f662cd423a3a5023ea7c9d164458ba40c0478e

Manual Test 2 Findings:
  f556ab187b274de7da8da742f147cb365888c19b63ee3df6dc8d21a4fed8780118c64a73969fd981e328bfd817a7421a3a631787e49acf0657ca0cbf6555c0d8

Manual Test 2 Designer Review:
  da504ba70522ff1e2685e2f74b2a1204c2345bf820a20841c65d5cd684ecb28fb16fcbd2ebed4ce2e3bd1f9de4a4989bb9ff0d14054eec8d1b8efd7836f8cbf2

Lightning RAG Requirements:
  b31c16587409317123decbfe19c417c1148563ee18b548cea2adbf55963c6e11c2819f3d4c3384482c1a7446ff01eff8b3de433b5131b25c1002663a68b67f4b

Lightning RAG Architecture:
  b3324120e491764438f29cda36ad584df7b15be5c59eae65a27acff72a7fb36aef39e1a3471293e04c80078eb87d409699aa23c5771a4505f1dbac7040d1e978

ADR-0029:
  fd174ee659974521f33a0200e3c36f7bfc44b13d3b8b3bbd80a6c30ab919c921e1eabb390fdaf05b82fa5849b41de931dc40dc6764a0fe3636409e924b140cf7
```

本Index作成後に生成されるHandoffおよび本Index自身のSHA-512は、次のImplementer Status／Designer Review／Append-only Indexで固定する。

## 6. Next Gate

実装担当はHandoffの範囲でRepository実装と自動検証を行い、Timestamp付きStatusを作成する。

設計統括者役はStatus、全Changed File、SHA-512、Public Demo Builder Call 0／Docs Scan 0、Mac RegressionおよびFull Suiteを再Reviewする。Repository側がAcceptedとなった後、Lightning実機のFile配置、Test、Preflight、Basic Preview／Public DemoおよびSleep／Wake手順をユーザーへ渡す。

Lightning実機Acceptanceまでは、本Feature全体を完了扱いにしない。
