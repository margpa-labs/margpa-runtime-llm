# 実装担当向け Phase 1-ex Mac限定簡易Documentation RAG Handoff

```yaml
document_id: implementer_handoff_phase_1_ex_mac_local_documentation_rag
phase: phase_1_ex
status: accepted_ready_for_implementation
language: ja
created_at: 2026-07-31 17:22:59 JST
owner: 設計統括者役
target_role: 実装者役
platform_operator: user
supersedes: null
implementation_environment: local_macos_arm64
```

## 1. Objective

Local Mac上の既存Web Runtimeへ、ProjectのCanonical／Stable Markdown Docsを参照できる簡易Documentation RAGを追加する。

初期実装は、追加Modelまたは新規Runtime Dependencyを使わない決定論的Sparse／Lexical Retrievalとする。

次を同時に成立させる。

```text
Local Mac:
  Documentation RAG利用可能
  UI Default OFF

Basic Preview:
  Capability eligibleを維持
  Initial External AdapterはBindingしない

Public Demo:
  Documentation RAG denied
  Adapterを生成しない

Future:
  Embedding／Dense／Hybrid／Persistent Index
  Lightning／Home Server／Cloud Adapter追加可能
```

## 2. Authoritative References

必ず次の順でRead-only参照する。

1. [Mac限定簡易Documentation RAG 要件定義](../../requirements/mac_local_documentation_rag_requirements_ja.md)
2. [Mac限定簡易Documentation RAG 技術選定](../../architecture/mac_local_documentation_rag_technology_selection_ja.md)
3. [Mac限定簡易Documentation RAG Architecture](../../architecture/mac_local_documentation_rag_architecture_ja.md)
4. [ADR-0028](../../adr/adr_0028_mac_local_sparse_documentation_rag_and_external_adapter_hook_ja.md)
5. [ADR-0027](../../adr/adr_0027_public_demo_minimal_access_and_deferred_control_hooks_ja.md)
6. [Documentation Rules](../../../../shared/conventions/documentation_rules_ja.md)
7. [Task Role／Write Authority](../../../../shared/task_roles/task_role_write_authority_policy_ja.md)
8. [Research Asset Mutation Control](../../../../shared/operations/research_asset_mutation_control_ja.md)
9. [Phase 1-ex Index](../../phase_index_ja.md)

Conflict時は次の優先順位とする。

```text
User Latest Explicit Instruction
  → Accepted ADR-0028
  → Accepted Requirements
  → Accepted Architecture
  → Accepted Technology Selection
  → This Handoff
  → Older Reservations
```

旧文書は履歴および未変更要件の参照に使用し、新Accepted設計を上書きしない。

## 3. Accepted Design Digest

```text
Requirements:
7ef26d2458ef481d47b0fa53dc5e8ec7e9da1d81c29bc35d0704245eb6cccb97b2ddfcc64e8a15b2071e3ea66a0eebe16fa081979d17f14eed791a4b1c6999be

Technology Selection:
56203c926ccf5cc99b04f3db210f1fb46aaedcccf30d55df70f5e3177f6b9970632ad1e87f8c7aa5a427561c43a5a34fbb88ef817a42ea91b2c68534ff347f53

Architecture:
0c7a27dd0cfa707a12654416576e357a49c52dc908b73a6d9dfc7ba1c85738c39ab46623a6e3fbaedd2a842b5486b5d6039272e1edb6a4f74aed43a317b49b0a

ADR-0028:
d2bee3efabbf8a7a025ba2fa4d6da462bbcb85160a5fa2458a9ff7996df0bbcfbbbfdb74d9d7516b0311b7c54309686646f2b9e962a8fe4c59c234ecc8fa2f9b
```

実装開始前にHashを再確認する。

不一致がある場合は勝手に旧版へ戻さず、現在Hash、差分対象および影響を報告して停止する。

## 4. Pre-mutation Gate

実装開始前に次を行う。

1. Project Rootが`margpa-runtime-llm/`であることを確認する。
2. Project Root外を走査、作成、変更または削除しない。
3. `models` Symbolic Linkを追跡しない。
4. 変更予定Fileを先に列挙する。
5. 既存変更と衝突しないことを確認する。
6. 変更対象のBefore SHA-512をStatus用に取得する。
7. `.venv/`、Model、Cache、Secret、Credentialまたは外部Environmentを変更しない。
8. Git、GitHub、LightningまたはNetwork操作を行わない。
9. Dependency InstallまたはModel Downloadを行わない。
10. 実Projectの`docs/`を移動、改名、削除または一時退避してTestしない。

Scope外変更が必要な場合は実装せず、理由、対象、必要差分および影響をStatusへ記載して設計統括者役へ戻す。

## 5. Authorized Mutation Scope

本Handoffに必要な最小差分に限り、次を変更できる。

```text
src/margpa_runtime_llm/modules/documentation_rag/
src/margpa_runtime_llm/adapters/documentation_rag/
src/margpa_runtime_llm/bootstrap/

src/margpa_runtime_llm/modules/conversation/
src/margpa_runtime_llm/entrypoints/web/
src/margpa_runtime_llm/web/

config/application.toml
config/feature_profiles/

tests/unit/documentation_rag/
tests/unit/conversation/
tests/unit/web/
tests/integration/documentation_rag/
tests/integration/web/

docs/project/phases/phase_1_ex/history/handoffs/
  implementer_status_phase_1_ex_mac_local_documentation_rag_YYYYMMDDHHMMSS.md
```

既存Test配置規約に合わせるため、必要なTest Fileを既存`tests/unit/inference/`等へ置くことは許可する。

次は原則変更しない。

```text
pyproject.toml
uv.lock
config/models/
config/profiles/
config/web_profiles/
scripts/runtime/lightning/
README.md
docs/public/
docs/project/current/
docs/project/shared/
ADR／Requirements／Architecture正本
Phase Index
既存History
Model Artifact
```

`config/web_profiles/`または既存Access Profile実装へ変更が必要な場合は、Public `denied`とBasic `eligible`を維持する最小差分だけ許可する。変更理由とBefore／After ContractをStatusへ記載する。

## 6. Mandatory Technology

初期実装：

```text
Language:
  Existing Python 3.12／3.13 Contract

Source:
  Local Markdown／UTF-8

Normalization:
  Unicode NFKC／Latin casefold

Japanese Search:
  Character 2-gram／3-gram

English／Code Search:
  Latin／digit／identifier／path token

Ranking:
  BM25-style lexical ranking

Index:
  In-memory immutable snapshot

Lifecycle:
  Lazy Build／Manifest Digest Cache

Integrity:
  SHA-512

UI／API:
  Existing FastAPI／SSE／Vanilla JavaScript
```

禁止：

```text
LangChain
LlamaIndex
PyTorch
Transformers
Sentence Transformers
MLX
FAISS
Chroma
Qdrant
SQLite FTS
Embedding Model
External API
Network Access
New Runtime Dependency
Persistent Index
```

## 7. Required Implementation

### 7.1 Domain／Port

最低限次を独立Contractとして実装する。

```text
DocumentSourcePort
ChunkerPort
EmbeddingPort
IndexStorePort
RetrieverPort
ContextAssemblerPort
CitationPort
RagOrchestratorPort
```

初期Lexical Pipelineは`EmbeddingPort`を呼ばない。

`EmbeddingPort`にDummy Semantic処理、Main Model流用またはHidden Downloadを実装しない。

DomainへFastAPI、DOM、Filesystem、llama.cppまたは具体Config Parser型を入れない。

### 7.2 Local Source Adapter

Default Corpus：

```text
docs/project/current/**/*.md
docs/public/**/*.md
docs/project/phases/<active_phase>/phase_index_ja.md
docs/project/phases/<completed_phase>/**/*_ja.md
```

Default Exclusion：

```text
**/history/**
**/lossless/**
Hidden File
.DS_Store
Backup
Archive
Temporary File
Symbolic Link
Project Root外
Non-Markdown
Limit超過
```

Project RootはComposition Rootから注入する。

Current Working Directoryだけから暗黙推測しない。

CandidateはProject相対PathでSortする。

### 7.3 Source Manifest

各Document：

```text
source_id
project_relative_path
corpus_priority
document_sha512
size_bytes
media_type
encoding
```

Corpus Manifest Digestは相対Path、SizeおよびSHA-512から決定論的に生成する。

Absolute PathをDomain Result、Citation、SSEまたはErrorへ出さない。

### 7.4 Markdown Chunker

次を識別する。

- ATX Heading。
- Heading Breadcrumb。
- Paragraph。
- Blank Line。
- Fenced Code Block。

初期値：

```text
target_characters = 900
overlap_characters = 120
maximum_characters = 1600
```

同じDocumentとConfigから同じChunk ID、順序およびContent Digestを生成する。

Code Fence内の`#`をHeadingと解釈しない。

### 7.5 Lexical Tokenizer／Retriever

最低限：

```text
Unicode NFKC
Latin casefold
Japanese 2-gram／3-gram
Latin／digit／underscore／dot／slash／hyphen token
BM25 k1 = 1.5
BM25 b = 0.75
top_k = 4
max_chunks_per_document = 2
```

Body、Heading、Path、Exact PhraseおよびCorpus Priorityを独立WeightとしてConfig可能にする。

Tie-break：

```text
Score DESC
Corpus Priority ASC
Relative Path ASC
Heading ASC
Chunk Ordinal ASC
Chunk ID ASC
```

同じInputで同じ結果を返す。

### 7.6 In-memory Index

- Startupで全文Indexを必須構築しない。
- 最初のRAG RequestでLazy Buildする。
- Exact Corpus Manifest Digestを確認する。
- Cache KeyへAlgorithm VersionとProfile Digestを含める。
- 同時Buildを単一Lockで直列化する。
- 完成後にAtomic Replaceする。
- Build失敗時に不完全Indexを公開しない。
- DiskへIndexを保存しない。
- OFF時にFilesystem Scanを行わない。

### 7.7 Context Assembler

RAG ContextはUser Messageへ文字列連結しない。

System所有の非信頼Reference Messageとして分離する。

最低Budget：

```text
maximum_rag_context_tokens = 768
minimum_useful_rag_context_tokens = 128
safety_margin_tokens = 512
fallback_maximum_rag_characters = 2400
```

Tokenizer利用可能時はToken Budgetを優先し、利用不可時は保守的文字数上限を使用する。

Docs本文内の命令に従わず、Project説明の根拠としてだけ扱うSystem Instructionを付ける。

Reference Markerと衝突する本文はEscapeする。

### 7.8 System Citation

CitationはRetriever Resultから生成する。

```text
citation_id
project_relative_path
heading_breadcrumb
chunk_id
document_sha512
retrieval_score
selected_order
truncated
```

Modelが生成したCitation文字列をSystem Citationへ昇格しない。

### 7.9 Conversation Integration

最新User Messageだけを初期Retrieval Queryにする。

全Conversationを無差別連結しない。

Summary Mode：

```text
Retrieve once
  → Original Answer
  → Existing Summary Stage
  → Original Retrieval Citationを維持
```

Summary Stageで再検索しない。

既存のStreaming、Cancel、New Chat、Model Busy、Thinking、LanguageおよびCopy契約を壊さない。

### 7.10 Feature State

次を混同しない。

```text
Access Capability
Server Feature Availability
Request／UI Selection
Adapter Availability
Corpus Availability
```

Effective State：

```text
disabled
unavailable
enabled
denied
```

Local Mac：

- Adapterを利用可能にする。
- UIのTurn設定初期値はOFF。
- OFF時はRAG Serviceを呼ばない。

Basic Preview：

- `eligible`を維持する。
- 初期External AdapterをBindingしない。

Public Demo：

- `denied`。
- RAG Adapterを生成しない。
- Request Overrideを拒否する。
- UI Controlを表示しない。

### 7.11 Config

Portable Default、Feature ProfileおよびAccess Ceilingを分離する。

推奨：

```text
config/application.toml:
  UI／Request default = off

config/feature_profiles/local_documentation_rag.toml:
  Local Lexical Provider
  Corpus／Chunk／Ranking／Budget

config/web_profiles/*.toml:
  Existing Access Capability Ceiling
```

Field名はTyped ContractとTestで固定する。

`application.toml` Schemaを更新する場合はVersionを明示し、既存Config Migration／Default Testを更新する。

Model Key、Model Filename、Mac User PathまたはPublic URLをFeature Profileへ入れない。

### 7.12 Web／SSE／UI

Local UI：

```text
Japanese:
  プロジェクトDocs参照

English:
  Project Docs

Control:
  OFF／ON

Default:
  OFF
```

System-derived Retrieval EventをModel Deltaと分離する。

各Assistant Turnへ次を関連付ける。

```text
retrieval_state
citations
index_rebuilt
safe_warnings
```

Assistant本文Copyは本文だけとする。Citationは別領域でProject相対Pathを個別Copy可能にする。

Browser Reload後は既定OFFへ戻す。

Local StorageへConversation、CitationまたはCorpus Dataを保存しない。

### 7.13 Safe Error

Docs不在：

```text
docsが設置されていないため参照出来ません。
```

この場合、RAG経由のModel Callを開始しない。

No Hit：

- 通常Chatは継続可能。
- Citationは空。
- Project Docsに基づく回答と表示しない。
- Safe Warningを表示する。

個別File Error：

- 有効Documentが残る場合はDegradedで継続。
- 有効Documentが0件ならUnavailable。

Internal Exception、Absolute Path、Document本文、User名またはCredentialをBrowserへ返さない。

## 8. Required Limits

初期Default：

```text
max_documents = 512
max_file_bytes = 4 MiB
max_corpus_bytes = 32 MiB
max_chunks = 20000
top_k = 4
max_chunks_per_document = 2
maximum_rag_context_tokens = 768
fallback_maximum_rag_characters = 2400
```

上限到達を黙って無視せず、Safe Status／Warningとして分類する。

## 9. Required Tests

### 9.1 Source Security

- Project Root外拒否。
- Allowlist外拒否。
- Symbolic Link拒否。
- `history/`除外。
- `lossless/`除外。
- Hidden／Temporary／Backup除外。
- UTF-8 Decode失敗。
- File／Corpus／Document Count上限。
- Absolute Path非露出。

### 9.2 Chunk／Retrieval

- Heading Breadcrumb。
- Code Fence。
- Chunk Overlap。
- Chunk ID再現性。
- 日本語2-gram／3-gram。
- English／Code Identifier。
- BM25 Ranking。
- Field Weight。
- Corpus Priority。
- Tie-break。
- Minimum Score。
- Document Diversity。
- No Hit。

### 9.3 Index

- Cold Build。
- Warm Cache。
- Manifest変更によるRebuild。
- Algorithm Version変更によるRebuild。
- Concurrent Build。
- Build失敗時のAtomicity。
- OFF時のNo Scan／No Build／No Write。

### 9.4 Context／Citation

- Token／Character Budget。
- Reference Instruction分離。
- Marker Escape。
- System Citation。
- Model Citation非昇格。
- Raw Content非露出。
- Evidence Digest。

### 9.5 Conversation

- RAG OFF既存挙動。
- RAG ON Reference注入。
- Latest User MessageだけをQuery化。
- Summaryで一度だけ検索。
- Cancel。
- New Chat。
- Model Busy。
- Thinking。
- Response Language。

### 9.6 Web／Access

- Local UI Control。
- UI Default OFF。
- SSE Retrieval Event。
- Citation Block。
- Browser Reload。
- Basic PreviewはEligible／Unavailable。
- Public DemoはDenied。
- Public Request Override拒否。
- Public起動時Adapter非生成。
- Public／Basic既存機能Regression。

### 9.7 Test Fixture Safety

Docs Missing、Symbolic Link、Root EscapeおよびCorpus Limit Testは、Pytest Temporary RootまたはProject内承認済みFixtureだけで行う。

実Projectの`docs/`、Current Docs、Public DocsまたはHistoryを移動、改名、削除または書換しない。

## 10. Required Verification

既存`.venv`で実行し、新規Installを行わない。

最低限：

```text
Targeted Documentation RAG Unit Tests
Conversation Unit Tests
Web Unit／Integration Tests
Access Profile Tests
Full pytest
Ruff Check
Ruff Format Check
Mypy
```

Local Modelが利用可能な場合：

```text
Existing Model Smoke
Documentation RAG Model Smoke
```

Model Smokeを実行できない場合は、未実施理由をStatusへ記載する。

## 11. Manual Acceptance Preparation

実装担当は手動試験用手順をStatusへ記載する。

対象：

1. Local Mac Web起動。
2. RAG OFF通常Chat。
3. RAG ON Project概要。
4. RAG ON Roadmap。
5. RAG ON Architecture。
6. RAG ON英語略称。
7. Citation Path／Heading。
8. Docs変更検知。
9. No Hit。
10. Summary Mode。
11. Stop。
12. New Chat。
13. Browser Reload。
14. Public Demo RAG拒否。

実際の手動操作はユーザーが行う。

## 12. Performance Evidence

Local Macで、Model生成時間とRAG処理時間を分けて報告する。

目標：

```text
Cold Index Build:
  <= 10 seconds

Warm Retrieval:
  <= 1 second

Additional Resident Memory:
  <= 256 MiB
```

Memory計測がTestを不安定にする場合、Manual Evidenceとして分離してよい。

目標未達でも勝手にEmbedding、DatabaseまたはDependencyを追加しない。実測と原因を報告する。

## 13. Implementer Status

新規作成：

```text
docs/project/phases/phase_1_ex/history/handoffs/
implementer_status_phase_1_ex_mac_local_documentation_rag_YYYYMMDDHHMMSS.md
```

最低記載事項：

- 読んだ正本文書とSHA-512。
- 変更File一覧。
- 各変更FileのBefore／After SHA-512。
- 新規File一覧。
- 実装したContract。
- Config Schema／Default／Source Priority。
- Corpus Include／Exclude。
- Chunk／Retriever／Index Version。
- Public／Basic／Local Effective State。
- Test Commandと全結果。
- Model Smoke結果。
- Cold／Warm性能。
- Manual Test手順。
- Known Limitation。
- 未実施項目。
- Scope外変更がないこと。
- Project Root外を変更していないこと。
- Dependency／Model／Lightning／Git／GitHubを変更していないこと。

## 14. Completion Definition

次を全て満たした場合だけ、実装完了として設計統括者役へReview依頼する。

1. Accepted Port境界を実装した。
2. Local MacでRAG UIを利用できる。
3. UI DefaultはOFF。
4. OFF時Zero WorkがTestされている。
5. Public DemoでRAGを有効化できない。
6. Public DemoでRAG Adapterを生成しない。
7. `history/`／`lossless/`がDefault Corpusから除外される。
8. CitationがSystem由来である。
9. Docs不在時の指定文言とNo Model Callを満たす。
10. Existing Test、RuffおよびMypyがGreen。
11. Local Model Smokeを実施、または未実施理由を記録した。
12. Implementer Statusを新規作成した。

## 15. Prohibited Actions

- Project Root外の操作。
- Model Download。
- Dependency Install。
- `pyproject.toml`／`uv.lock`変更。
- Persistent Vector／Search Index作成。
- External API／Network利用。
- Public Demo RAG有効化。
- Lightning設定変更。
- Git／GitHub操作。
- Current／Public／Shared／Phase正本文書の編集。
- 既存Historyの編集または削除。
- 実Project Docsを破壊的Testへ使用。
- Scope外Cleanup。
- `.DS_Store`等を本Handoffに便乗して削除。

