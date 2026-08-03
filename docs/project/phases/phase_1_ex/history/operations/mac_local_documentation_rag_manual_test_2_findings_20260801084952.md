# Mac限定簡易Documentation RAG 第2回手動Testの結果と知見

```yaml
document_id: mac_local_documentation_rag_manual_test_2_findings
phase: phase_1_ex
status: evidence_recorded
language: ja
created_at: 2026-08-01 08:49:52 JST
owner: 設計統括者役
execution_owner: user
source_handoff: ../handoffs/user_handoff_phase_1_ex_mac_local_documentation_rag_manual_acceptance_retest_20260801014339.md
source_review: ../handoffs/designer_review_phase_1_ex_mac_local_documentation_rag_coverage_integrity_follow_up_20260801014339.md
```

## 1. Purpose

Coverage Integrity Follow-up後のMac Local Webと実GGUFに対し、次を確認した第2回手動TestのEvidenceを保存する。

- 複数Subjectの根拠不足を検出して安全停止できるか。
- 日本語と英語の複数Subject Queryを区別できるか。
- 各TurnでRetrievalとSystem Citationを実行するか。
- ARGD、DAGD、EASA、DLAGSA、OCILNS等のProject固有定義を混同しないか。
- RAG OFF Baselineと比較し、RAGの効果と限界を分離できるか。

本RecordはModel回答を正本として保存するものではない。回答の成功、誤り、安全停止およびCitationの対応をTest Evidenceとして整理する。

## 2. Test Condition

```text
Environment:
  Mac Local Web
  macOS arm64／Metal

Main Model:
  Qwen3 4B Q4_K_M GGUF

Maximum New Tokens:
  512

Documentation RAG:
  ON for Sections 3–9
  OFF for Section 10

Summary:
  OFF

Primary Corpus:
  Current／Public／Active Phase Index／Completed Phase Stable
```

## 3. Japanese Three-subject Query

Query：

```text
EASAとは何ですか？
DLAGSAとは何ですか？
OCILNSとは何ですか？
それぞれ3行以内で、参照文書に記載された正式名称と役割だけを説明してください。
```

Observed：

```text
Result:
  「質問対象の一部に必要なProject Docsの根拠が揃わないため、回答を停止しました。」

Generated factual answer:
  none

Citations:
  EASA definition
  DLAGSA definition
  Common Integration Principle

OCILNS-specific assembled basis:
  insufficient
```

Assessment：

```text
Coverage Integrity:
  PASS

Fail-closed:
  PASS

Combined-query usability:
  NOT SATISFIED
```

一部根拠だけで残りのSubjectをModelが推測することなく、必要根拠不足として停止した。同一Queryを後で再実行した場合も同じSafe Boundaryを確認した。

## 4. Japanese Two-subject and Single-subject Queries

### 4.1 EASA／DLAGSA

EASAとDLAGSAの2 Subject Queryでは、各日本語名称と役割の概要を回答し、EASAおよびDLAGSAの個別HeadingをSystem Citationとして表示した。

```text
Retrieval／Citation:
  PASS

Definition separation:
  PASS for the tested short answer
```

### 4.2 EASA Single Subject

EASAのSingle Subject Queryでは、Exception Aware Safety Architecture、例外認識型安全統治機構および複合安全挙動を扱う独立R&D Architectureという説明を返した。

```text
Answer direction:
  PASS

Citation:
  PASS
```

### 4.3 DLAGSA Single Subject

DLAGSAのSingle Subject Queryでは、分散証跡型例外認識エージェント統治安全機構、複数の判断・実行・検証主体間の責任、委譲、例外、改竄耐性付き証跡、全体整合および異常時の安全側制御を扱うという方向の回答を返した。

```text
Answer direction:
  PASS

Citation:
  PASS
```

## 5. OCILNS Follow-up Query

OCILNSのSingle Subject Queryでは、Open Cognitive Interaction Ledger Network System、認知対話証跡台帳網、人・AI・Tool・外部System間の認知対話出来事を改竄耐性付き証跡単位として扱うという概要は回答できた。

一方で、質問されていないDLAGSAを追加し、EASAと連携して安全な認知対話環境を実現するという、当該Citationから直接は確認できない関係を追加した。

```text
OCILNS core definition:
  PASS

Instruction adherence:
  FAIL／unsolicited subject added

Claim-to-citation consistency:
  FAIL／unsupported relationship added
```

## 6. English Three-subject Query

Query：

```text
What are EASA, DLAGSA, and OCILNS?
Explain each in no more than three lines, using only the referenced project documents.
```

Observed：

- EASAをException Aware Safety Architectureとして説明した。
- DLAGSAをDistributed LEA Agentic Governance & Safety Architectureとして説明した。
- OCILNSをOpen Cognitive Interaction Ledger Network Systemとして説明した。
- EASA、DLAGSAおよびOCILNSの3 Subjectに対応するCitationを表示した。

```text
English prose-noise classification:
  PASS

Three-subject retrieval／assembly:
  PASS in this run

Formal names:
  PASS

Answer-to-citation direction:
  PASS in this run
```

日本語3 Subject QueryがSafe Denyとなり、英語3 Subject Queryが回答できたことは、QueryとChunkの表層一致、Chunk Size、RankingおよびContext Assemblyの差が結果に影響することを示す。

## 7. ARGD／DAGD／EASA Separation Query

Query：

```text
ARGDとDAGDについて、それぞれの正式名称と担当領域を3行以内で説明してください。
EASAとの関係は参照文書に明記されている場合だけ説明してください。
```

Observed Failure：

- ARGDをException Aware Safety Architectureと誤展開した。
- DAGDについて、ARGDと同一のSource Path／Digestを参照するというPackage Example上の記述を、定義の正式な役割のように使用した。
- EASAをARGD／DAGDの元となる機構と断定した。
- CitationはARGD／DAGD Package ExampleとEASA Catalogであり、Canonical ARGD／DAGD Definitionの詳細根拠として不十分だった。

Correct Canonical Names：

```text
ARGD:
  Axiomatic Reasoning Governance Definition v0.3.1

DAGD:
  Declarative AI Governance Definition v0.4.4
```

Assessment：

```text
Lexical identifier presence:
  detected

Semantic definition sufficiency:
  not established

Formal-name correctness:
  FAIL

Unsupported relationship suppression:
  FAIL
```

この結果は「Chunk内にIdentifierが存在する」ことと、「質問に必要なCanonical Definitionが十分に含まれる」ことが同一ではないことを示す。

## 8. Sequential Every-turn Retrieval

同一ChatでEASA、ARGD、DLAGSA、Roadmapを順に質問した。

| Turn | Subject | Retrieval／Citation | Answer Assessment |
|---:|---|---|---|
| 1 | EASA | 対応Citationあり | 概要は正しい |
| 2 | ARGD | ARGD対応Citationあり | 訳と表現に粗さはあるが、EASA専用とはしなかった |
| 3 | DLAGSA | DLAGSA対応Citationあり | 概要はおおむね正しい |
| 4 | Roadmap | `docs/public/roadmap_ja.md`等のCitationあり | 現在の進捗を読み取れず「明示的な情報はない」と回答 |

```text
Every-turn retrieval:
  PASS

Every-turn citation refresh:
  PASS

Every-turn answer correctness:
  PARTIAL

Roadmap progress extraction:
  FAIL
```

第1回手動Testで見られた「初回だけ調べ、2 Turn目以降は調べない」という現象は、本Testでは再現しなかった。一方、Retrievalが行われても、正しいSectionの選択またはModelによる読解が成功するとは限らない。

## 9. Repeated Safe-deny Observation

EASA／DLAGSA／OCILNSの3 Subject Queryを別のTurnで再実行した際も、必要根拠不足を明示し、Modelによる事実回答を作成しなかった。

```text
Repeat fail-closed:
  PASS

Unsafe guessed completion:
  not observed for the combined Japanese query
```

## 10. RAG OFF Baseline

RAG OFFで同系統の質問を行った結果、次の明確なHallucinationを観測した。

- EASAを欧州航空安全局として回答した。
- DLAGSAを実在根拠のないEASAの地域事務局として生成した。
- OCILNSを欧州航空安全局に関係する委員会として生成した。
- Roadmapの対象を特定できず、一般論を生成した。

```text
RAG OFF project-specific correctness:
  FAIL

RAG ON comparative improvement:
  CLEARLY OBSERVED
```

RAG ONでも回答品質の失敗は残るが、完全な無根拠回答の頻度を下げ、根拠不足時に安全停止できる効果は確認できた。

## 11. Findings

### 11.1 Mechanism and Quality Must Remain Separate

```text
RAG Pipeline:
  Source／Chunk／Index／Retrieve／Assemble／Citationが成立

Coverage Fail-closed:
  成立

Multi-turn Retrieval:
  成立

Semantic Sufficiency:
  未成熟

Claim-to-citation Entailment:
  未成熟

Small-model Instruction Adherence:
  未成熟
```

Citationが表示されることは、Modelのすべての主張がCitationにより裏付けられたことを意味しない。

### 11.2 Lexical Coverage Is Not Semantic Sufficiency

IdentifierのHeading／Path／Bodyへの存在は、一般説明、Package Example、実装上の参照またはCanonical Definitionを区別しない。

後続改善候補：

- SubjectごとのQuery Decomposition。
- Canonical Definition／Current／Public正本のAuthority-weighted Retrieval。
- Section Type、Document RoleおよびLanguageのMetadata。
- Semantic Reranker。
- Claim-to-Citation整合性評価。
- ARGD／DAGDによる前提、情報不足、矛盾および推測の統治。
- LLM-as-a-Judge。
- Repair／再検索。
- Main Modelの交換。

### 11.3 Hit Keyword／Model-reference Index Hook

従来型RAGのように、文書またはSectionごとの「ヒットキーワード列」、またはRAG用の「Model参照用Index表」が必要になる可能性がある。

予約する概念：

```text
Retrieval Guidance Metadata／Manifest:
  document_id
  project_relative_path
  language
  document_role
  authority_tier
  canonical_subjects
  aliases
  hit_keywords
  heading_anchors
  prohibited_inferences／relationship_scope
  document_sha512
  metadata_schema_version
```

必須不変条件：

1. Metadataの存在は、文書内容の真実性またはAuthorityを新しく生成しない。
2. MetadataはRetrieval Guidanceであり、回答の根拠本文を代替しない。
3. `document_sha512`と一致しない古いMetadataを黙って使用しない。
4. Runtime中にMain ModelがMetadataを勝手に書き換えない。
5. Metadataなしを正式な劣化Modeとして扱う。
6. Retrieval AlgorithmからNarrow Port経由で利用し、Coreに個別SubjectをHard-codeしない。

本PhaseでただちにMetadata Manifestを実装することは決定しない。現在のManual Baselineを保存し、Governance、Judge、RerankerまたはRAG精度改善Phaseで再評価する。

### 11.4 Current Tuning Should Stop Here

4B級軽量ModelとSparse Lexical Retrievalの個別Query調整を続けると、特定略称や現在Corpusへの過適合が発生する可能性がある。

本時点では次を優先する。

```text
Accept:
  Adapter分離
  Corpus境界
  Lazy In-memory Index
  System Citation
  Per-turn Retrieval
  Coverage Fail-closed

Defer:
  Semantic Precision
  Answer Entailment
  Authority Metadata
  Reranking
  Judge／Repair
  Model Upgrade
```

## 12. Scientific Value

本Testは、後続のGovernance／Judge／Repair／Model交換を比較するBaselineとして使用できる。

```text
Baseline A:
  RAG OFF
  severe unsupported project-specific answers

Baseline B:
  Sparse RAG ON
  improved definitions／citations／fail-closed
  remaining semantic confusion

Future C:
  RAG + Governance

Future D:
  RAG + Governance + Judge

Future E:
  RAG + Governance + Judge + Repair

Future F:
  Same stack + upgraded Main Model
```

同一Query、Model、Config、Docs DigestおよびSeedを使用し、正確性、拒否、Citation Coverage、Latency、TokenおよびFailureを比較する価値がある。

## 13. Scoped Acceptance

```text
Mac Local Documentation RAG Mechanism:
  ACCEPTED

Corpus／Citation／Lifecycle Boundary:
  ACCEPTED

Coverage Fail-closed:
  ACCEPTED

Multi-turn Retrieval:
  ACCEPTED

Semantic Retrieval Precision:
  KNOWN LIMITATION／DEFERRED

Answer Correctness:
  KNOWN LIMITATION／DEFERRED

Authority-critical Use:
  NOT ACCEPTED

Immediate Additional Query-specific Tuning:
  DEFERRED
```

## 14. Next Direction

Mac Localの追加精度調整はここで停止し、既存Basic認証Previewに限定したLightning用Documentation RAG Adapter Hookの設計・実装・検証へ進む。

Public DemoのDocumentation RAG強制無効は維持する。
