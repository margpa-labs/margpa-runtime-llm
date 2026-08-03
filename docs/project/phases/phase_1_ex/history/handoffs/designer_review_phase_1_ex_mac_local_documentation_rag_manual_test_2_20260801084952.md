# 設計統括者Review：Phase 1-ex Mac限定簡易Documentation RAG 第2回手動Test

```yaml
document_id: designer_review_phase_1_ex_mac_local_documentation_rag_manual_test_2
phase: phase_1_ex
status: scoped_accepted_known_quality_limitations
language: ja
created_at: 2026-08-01 08:49:52 JST
owner: 設計統括者役
source_index: ../documentation_index_20260801014339.md
source_evidence: ../operations/mac_local_documentation_rag_manual_test_2_findings_20260801084952.md
supersedes_gate_from: user_handoff_phase_1_ex_mac_local_documentation_rag_manual_acceptance_retest_20260801014339.md
```

## 1. Decision

ユーザーがMac Local Webと実GGUFで実施した第2回手動Testの全報告をReviewした。

```text
Mac Local Documentation RAG Mechanism:
  ACCEPTED

Coverage Integrity／Fail-closed:
  ACCEPTED

Per-turn Retrieval／System Citation:
  ACCEPTED

Japanese／English Basic Grounding:
  PARTIAL PASS

Semantic Sufficiency／Answer Correctness:
  KNOWN LIMITATION

Authority-critical Use:
  NOT ACCEPTED

Additional Phase 1-ex Query-specific Tuning:
  DEFERRED

Next Gate:
  Lightning Basic Preview Documentation RAG Adapter Hook Design／Implementation
```

本判定は、Modelの全回答が正しいこと、Citationが全主張を裏付けることまたはGovernance用途に十分な信頼性があることをAcceptedとするものではない。

受け入れるのは、現段階のMVP RAG機構、Access Boundary、Retrieval Lifecycle、System Citationおよび根拠不足時の安全停止である。

## 2. Accepted Evidence

### 2.1 Three-subject Fail-closed

EASA／DLAGSA／OCILNSの日本語3 Subject Queryで必要根拠が揃わず、明示的なSafe Messageと実Assembly分のCitationを表示した。Modelは不足Subjectの事実回答を生成しなかった。再実行でも同境界を確認した。

### 2.2 English Combined Grounding

English QueryでEASA、DLAGSAおよびOCILNSの正式英語名称、概要および3 SubjectのCitationを確認した。通常英語がCoverage Slotを消費する先行Failureは再現しなかった。

### 2.3 Every-turn Retrieval

同一Chat内のEASA、ARGD、DLAGSAおよびRoadmapの各TurnでCitationを確認した。「初回だけ検索し、2回目以降は検索しない」という先行現象は再現しなかった。

### 2.4 RAG OFF Comparison

RAG OFFではEASAを欧州航空安全局とし、DLAGSAとOCILNSに実在根拠のない関係を生成した。RAG ONでは誤りが完全には消えない一方、Project固有定義の回答と根拠不足時の安全停止に明確な改善があった。

## 3. Known Quality Failures

### 3.1 ARGD／DAGD／EASA Confusion

ARGD／DAGD QueryでARGDをEASAと誤展開し、EASAがARGD／DAGDの元となるという関係を生成した。

根本原因は次の複合である。

```text
Lexical Coverage:
  Identifier存在は検出できる

Semantic Sufficiency:
  Canonical Definitionが十分なかを検証しない

Retriever:
  Package ExampleとEASA Catalogを選択した

Main Model:
  不足関係を推測で補った
```

### 3.2 Unsolicited DLAGSA Addition

OCILNS Queryに対し、OCILNSの概要は回答したが、質問されていないDLAGSAとEASAの関係を追加した。これは引用付き回答が自動的に全主張のGroundingを意味しないことを示す。

### 3.3 Roadmap Extraction

`docs/public/roadmap_ja.md`はCitationに出たが、現在の進捗を読み取れず、情報がないと回答した。該当Section Retrievalまたは小型Modelによる情報抽出の問題として記録する。

## 4. Why This Is Not a Current Blocker

現在のDocumentation RAGは、軽量Sparse RetrievalとQwen3 4B級Main ModelでPipeline境界を確認するPhase 1-ex MVPである。

現時点で個別Queryごとの調整を継続すると、特定Corpus、略称または表現への過適合となる可能性がある。

次はすでにPort／Adapter境界で交換可能である。

- Retriever。
- Query Analyzer。
- Context Assembler。
- Citation Adapter。
- Main Model。
- 将来のRAG Governance Point。
- 将来のJudge／Repair。
- 将来のEmbedding／Hybrid Adapter。

したがって、後続Phaseでの改善は当初Architectureの破棄ではなく、明示Portの実装追加／交換として行える。

## 5. Deferred Improvement Hooks

```text
Retrieval Guidance Metadata:
  per-document／per-section hit keywords
  canonical subjects
  aliases
  language
  document role
  authority tier
  heading anchors
  document SHA-512 binding

Retrieval:
  query decomposition
  authority-aware ranking
  language-aware ranking
  semantic reranker
  sparse／dense hybrid

Evaluation:
  claim-to-citation entailment
  LLM-as-a-Judge
  deterministic coverage audit

Governance／Repair:
  ARGD／DAGD
  unsupported relation suppression
  missing-premise detection
  retry／retrieve-more／refuse
```

Retrieval Guidance MetadataはSearch HintでありAuthorityまたはTruthを生成しない。Document Digestと一致しないMetadataを黙って使用しない境界を必須とする。

## 6. Acceptance Boundary

```text
Accepted now:
  Mac Local Adapter composition
  allowlisted corpus discovery
  deterministic chunking／lexical index
  per-turn retrieval
  bounded context
  system citations
  missing docs／context／subject fail-closed
  RAG OFF baseline separation

Not accepted now:
  every answer is correct
  every citation entails every claim
  semantic canonical-definition selection
  authority-critical operation
  safety decision delegation to the RAG answer
```

## 7. Next Gate

Mac Localの精度改善はKnown Limitationとして保存し、Lightning Basic認証Previewに限定したExternal Documentation RAG Adapter Hookの設計・実装へ進む。

Public DemoのDocumentation RAG強制無効を変更しない。
