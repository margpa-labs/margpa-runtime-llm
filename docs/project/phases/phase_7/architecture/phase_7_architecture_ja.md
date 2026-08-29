# Phase 7 Architecture — Traceable Grounded Knowledge Runtime

```yaml
document_id: phase_7_architecture
document_state: accepted_frozen
phase: phase_7
language: ja
created_at: 2026-08-29 17:14:22 JST
architecture_style: modular_monolith_ports_and_adapters
```

## 1. Component Boundary

```text
Chat／Generation
  -> Retrieval Orchestrator
       -> Corpus Registry
       -> Chunker Port
       -> Embedding Port
       -> Index／Retriever Port
       -> Web Search Port
       -> Web Fetch Port
       -> Content Normalizer
       -> Evidence Assembler
  -> Context Injection Boundary
  -> Main Model
  -> Citation Projector
  -> Conversation／Citation Persistence
```

既存Phase 2 Retrieval／Citation PortをAdapterとして再利用し、Conversation DomainへVector StoreやSearch Providerを直接埋め込まない。

## 2. Canonical Entities

- `CorpusIdentity`：Corpus ID、Source Class、Owner Scope、Revision。
- `DocumentIdentity`：Document ID、Canonical Identity、Digest、Version、State。
- `ChunkIdentity`：Document Revisionに属するChunk ID、Digest、位置情報。
- `RetrievalRun`：Request ID、Query、Retriever／Index Revision、Candidate／Selected Chunk。
- `WebSearchRun`：Activation、Provider、Query、Result Identity、Cost／Time。
- `WebEvidence`：Canonical URL、Source Authority、Fetch時刻、Digest、Normalized Content。
- `CitationEvidence`：Presented AnswerとSource／Chunkの対応。
- `DataControlPolicy`：Purpose、Consent、Retention、Export、Delete、External Transmission。

## 3. Invariants

1. Web検索OFF時はSearch／Fetch Adapter Call 0。
2. Search ActivationとEvidence Governanceを混同しない。
3. Snippetを取得本文と偽らない。
4. 未取得URLを読んだSourceとしてCitationしない。
5. CitationはAssistant本文、Raw Prompt、Raw Thinkingと分離する。
6. Document更新後は旧Revision Evidenceを消さず、CurrentとHistoricalを区別する。
7. User提供DataをPublic WebまたはTraining Dataへ再分類しない。
8. Provider固有SDK型をDomainへ流入させない。
9. Phase 6の未解決Judge／Repairへ依存してRetrieval自体を停止しない。ただしJudge／Repair成立をClaimしない。
10. Runtime／Evidence FailureをConversation破損へ波及させない。

## 4. Web Security Boundary

URLはParse／Normalize後にScheme、Host、Port、Redirect、Resolved Address、Response Size、Content Type、TimeoutおよびBudgetを検証する。Private／Loopback／Link-local／Metadata EndpointおよびCredential-bearing URLはDefault拒否とする。

Search Providerへ送るQueryとConversation Contextは明示Policyで最小化し、Secret／PII候補は送信前に検査する。Modelは直接Browser／Network Authorityを持たず、Application ServiceがGoverned Portを呼ぶ。

## 5. Data Controls

通常Settingsへ次を投影する。

```text
設定
  Web検索 OFF | ON
  要約Mode
  RAG設定

データコントロール
  Chat Retention
  Local RAG Evidence
  Web Evidence Retention
  External Query／Context Transmission
  Feedback Research Use
  Synthetic Data Use
  Future Training Export
  Export／Delete
```

UIはCanonical Server Snapshotを表示し、Browser Local Stateを正本にしない。

## 6. Attachment Sizing Boundary

Phase 7-Aで次を判定する。

```text
Transport only
Metadata persistence
Safe local storage
Text extraction
RAG ingestion
Archive inspection
Model-native multimodal
```

最初の5項目までが既存Boundary内で局所化できる場合のみ採用候補とする。Archive SandboxまたはModel-native Multimodalを必須とする場合はPhase 10以降へ送る。

## 7. Failure Model

- `search_disabled`
- `search_provider_unavailable`
- `fetch_rejected`
- `fetch_timeout`
- `content_unsupported`
- `document_unavailable`
- `index_unavailable`
- `no_relevant_evidence`
- `citation_unavailable`
- `data_control_denied`

失敗理由、Stage、Provider、Elapsed、Request IDをEvidenceへ残し、User入力が原因と決めつけない。
