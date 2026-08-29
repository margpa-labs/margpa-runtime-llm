# Phase 7 要件 — RAG／Web検索／Data Governance

```yaml
document_id: phase_7_requirements
document_state: accepted_frozen
phase: phase_7
language: ja
created_at: 2026-08-29 17:14:22 JST
authority_owner: Nazuna Research
milestone: Traceable Grounded Knowledge Runtime
implementation_scope: poc_mvp
```

## 1. 目的

Phase 7は、外部知識を単にPromptへ連結するのではなく、どのSourceを、なぜ採用し、回答のどこへ利用したかを追跡できるKnowledge Runtimeを成立させる。

Phase 2のDocumentation RAG、Persistent Citation、Conversation／Branch／Regenerate境界を破棄せず、Local Corpus、Embedding、Index／Retriever、Web検索、Citation EvidenceおよびData Controlsへ拡張する。

## 2. Functional Requirements

| ID | 要件 |
|---|---|
| P7-REQ-001 | RAGは`OFF／ON`を持ち、OFF時にRetrieval／Injectionを行わない。 |
| P7-REQ-002 | Local Documentを登録、更新、削除し、Version／Digestを追跡できる。 |
| P7-REQ-003 | Chunking、Embedding、Index、Retrieverを交換可能なPort／Adapterで構成する。 |
| P7-REQ-004 | Query、採用Chunk、Score、Document／Chunk ID、Digest、Index RevisionをEvidence化する。 |
| P7-REQ-005 | CitationをAssistant本文と分離し、Reload／Restart／Branch／Regenerate後も復元する。 |
| P7-REQ-006 | 複数CorpusとSource Classを混同せず扱う。 |
| P7-REQ-007 | Vendor非依存のWeb Search／Fetch／Normalizer境界を持つ。 |
| P7-REQ-008 | Search Activationを`disabled／manual／automatic`として管理する。 |
| P7-REQ-009 | Web Evidence Governanceを`OFF／OBSERVE／ENFORCE`として検索起動と分離する。 |
| P7-REQ-010 | 初期値はWeb検索OFF／disabledで、Network Call 0を保証する。 |
| P7-REQ-011 | Web EvidenceへURL、Canonical URL、Title、Provider、取得時刻、公開／更新時刻、Content Type、Digestを保持する。 |
| P7-REQ-012 | Official／Primary／Secondary／General／Unknown SourceをAuthority Classで区別する。 |
| P7-REQ-013 | Current／Latest／Today／Official、Knowledge Cutoff外、User明示Search、Unsupported ClaimをAutomatic Trigger候補として扱う。 |
| P7-REQ-014 | Model Knowledgeと取得Evidenceの矛盾をEvidenceとして後続Judge／Repairへ渡せる。 |
| P7-REQ-015 | Document Prompt Injection、SSRF、Private Network、危険Scheme、Redirect、巨大Response、Secret／PII送信、Cost超過を制御する。 |
| P7-REQ-016 | Settingsへ第三領域`データコントロール`を追加する。 |
| P7-REQ-017 | 通常Settingsの要約Mode／RAG列の最上段へ、同一Toggle ComponentによるWeb検索`OFF／ON`を配置する。 |
| P7-REQ-018 | Chat、RAG／Web Evidence、Feedback、Synthetic DataのRetention、Export、Delete、外部送信、将来Training利用Consentを用途別に分離する。 |
| P7-REQ-019 | User Data／Feedback／Synthetic Dataの研究・Training利用は初期値OFFとする。 |
| P7-REQ-020 | `public_web／local_corpus／public_project_corpus／user_provided／human_feedback／synthetic_generated`をSource Classとして識別する。 |
| P7-REQ-021 | 保存だけでModel Training／Weight更新が行われたと表示しない。 |
| P7-REQ-022 | 汎用File AttachmentをPhase冒頭でSizingし、Upload、Storage、Parser、RAG取込、Multimodal推論を分離する。 |
| P7-REQ-023 | Attachmentが局所的なVersioned Boundaryで成立する場合だけPhase 7へ含め、Phase級ならPhase 10以降へ延期する。 |
| P7-REQ-024 | Conversation、Citation、Branch、Recording、Stop、PersistenceをRegressionさせない。 |
| P7-REQ-025 | Failure時に検索・取得・Citation・Index状態を虚偽成功へ変換しない。 |

## 3. Source Class最小契約

```text
public_web
local_corpus
public_project_corpus
user_provided
human_feedback
synthetic_generated
partner_licensed        # Schema Seamのみ。Phase 7ではUnavailable
```

Phase 7の最小Provenanceは、Source Class、Canonical Identity、取得／更新時刻、Content Digest、Transformation、採否理由およびCitationである。これはClean、Label Correct、Training EligibleまたはProduction Eligibleの認定ではない。

## 4. Scope外

- Model WeightのTraining／Fine-tuning／Promotion。
- User DataのDefault Training利用。
- 企業提携／有償License Dataの実接続、契約、Credentialまたは課金。
- Full Dataset Cleaning、Label／Annotator／Adjudication Governance、Eligibility。
- MP4等の動画Multimodal分析。
- 最大Context Window拡張、Hardware自動Profile昇格。
- Phase級と判定されたAttachment基盤。
- Phase 6のSelene／Qwen3Guard／Semantic 109／Repair Debtの解決済みClaim。

## 5. MVP停止線

Phase 7は次を満たした時点でUser Manualへ渡す。

```text
RAG OFFで既存Chatが動く。
Web検索OFFでNetwork Call 0。
Local Documentを登録・更新・検索できる。
採用ChunkとCitationを追跡できる。
Web SourceへCanonical URLと取得時刻が付く。
Reload／Restart／Branch／Regenerate後もCitationが残る。
危険なDocument／URL／送信を拒否できる。
Failureを正直に表示する。
既存Conversation／Citation／Branch／Persistenceを壊さない。
Userが実画面でSourceとCitationを確認できる。
```

理論完全性、企業運用、全Provider、全File形式または全Web品質をClosure条件へ追加しない。
