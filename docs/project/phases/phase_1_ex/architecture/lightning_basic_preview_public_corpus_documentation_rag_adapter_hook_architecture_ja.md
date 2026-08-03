# Lightning Basic Preview Public Corpus Documentation RAG Adapter Hook Architecture

```yaml
document_id: lightning_basic_preview_public_corpus_documentation_rag_adapter_hook_architecture
status: accepted_ready_for_implementation
language: ja
created_at: 2026-08-01 08:49:52 JST
owner: 設計統括者役
phase: phase_1_ex
implementation_authorized: true_with_accepted_handoff
requirements: ../requirements/lightning_basic_preview_public_corpus_documentation_rag_requirements_ja.md
decision: ../adr/adr_0029_lightning_basic_preview_public_corpus_documentation_rag_adapter_hook_ja.md
```

## 1. Architectural Goal

Mac Localに結び付いているRAG Composition条件を、「Access Profileが許可し、明示的に選択されたFeature Profileに対し、対応Adapterを組み立てる」境界へ一般化する。

実装後の主経路：

```text
Lightning API Builder／Private Bootstrap
  ↓ foreground run
basic_preview_service.sh
  ↓ validated CLI arguments
margpa-web
  ├─ Deployment Profile: Lightning Pure CPU
  ├─ Access Profile: basic_preview
  ├─ Model Definition: Qwen3 4B current default／replaceable
  └─ Documentation RAG Feature Profile: Lightning public corpus
       ↓
Generic Documentation RAG Composition
  ├─ Explicit Project Markdown Source
  ├─ Deterministic Markdown Chunker
  ├─ In-memory Lexical Index
  ├─ BM25-style Retriever
  ├─ Bounded Context Assembler
  └─ System Citation Adapter
       ↓
Conversation Application
       ↓
Existing llama.cpp Pure CPU Model
```

Public Demoは同じCoreを共有するが、Access Profile境界でDocumentation Adapterを構築しない。

## 2. Current Constraint and Required Change

現在のWeb Entry Pointは次の場合だけ`build_local_documentation_rag()`を呼ぶ。

```text
web access mode == local
platform.system() == Darwin
platform.machine() == arm64
```

このため、`basic_preview.toml`がDocumentation RAG `eligible`であっても、Lightning Linux x86_64ではAdapterが`unavailable`となる。

変更後は次を分離する。

```text
Access Capability:
  whether this surface may use documentation RAG

Feature Profile:
  which provider／corpus／limits／algorithm config is selected

Platform Compatibility:
  whether the selected provider can run on the detected deployment

Adapter Availability:
  whether construction succeeded

Requested Mode:
  whether the user enabled it for this browser request
```

存在、許可、選択、構築成功、有効化および回答成功を一つのBooleanへ潰さない。

## 3. Composition Refactoring

### 3.1 Generic Builder with Compatibility Wrapper

概念API：

```python
build_documentation_rag(
    project_root,
    defaults_path,
    feature_path,
    access_mode,
    platform_observation,
) -> DocumentationRagComposition
```

既存`build_local_documentation_rag()`はCompatibility Wrapperとして残すか、既存Call Site／Testが同等に動く形で移行する。

Builderの責務：

1. Defaults Configの検証。
2. Feature Profile Schemaの検証。
3. Access Mode Compatibilityの検証。
4. Platform Compatibilityの検証。
5. Corpus Selection Policyの生成。
6. Source／Chunker／Index／Retriever／Assembler／CitationのComposition。
7. Feature Profile Digestの生成。
8. Deferred Model Token Counter Binderの提供。

BuilderはWeb Request、Credential値、Lightning APIまたはPublic URLを参照しない。

### 3.2 Profile Schema Compatibility

現行Mac Profile v1は`current／public／active index／completed phase stable`がすべて固定Includeである。Lightningの明示8文書Corpusへそのまま流用しない。

推奨：

```text
Profile v1:
  existing Local Mac aggregate corpus

Profile v2:
  provider compatibility
  explicit file corpus selection
  future extensible source policy
```

Pydantic Discriminated Unionまたは同等の明示Schemaで、v1とv2の未知Field／未知値を拒否する。v1をv2として暗黙解釈しない。

## 4. Explicit Corpus Selection

### 4.1 Selection Plan

Filesystem Adapterに直接Feature Config全体を解釈させるのではなく、検証済みCorpus Selection Planを渡す構造を推奨する。

```text
DocumentationCorpusSelectionPlan:
  mode
  explicit_project_relative_files
  include_history = false
  include_lossless = false
```

Local Mac v1 Profileは既存Tree Selection Planへ変換し、Lightning v2 ProfileはExplicit File Selection Planへ変換する。

### 4.2 Path Validation

各Allowlist Pathに次を必須とする。

- Project-relative。
- POSIX Separator。
- `docs/public/`直下の指定File。
- `.md`。
- `.`、`..`、Empty Segment、BackslashまたはAbsolute Prefixなし。
- Duplicateなし。
- Symlink Componentなし。
- Resolved PathがProject Root内。
- Regular File。
- UTF-8。
- Size／Corpus Limit内。

Candidateの存在はManifest Build時に判定する。Missing PathはWarning／EvidenceとしてCountし、秘密情報やAbsolute PathをUIへ出さない。

### 4.3 Priority

Lightningの8文書はすべてPublic Corpusである。ただしRetrieval品質のため、Document RoleをPathだけでHard-codeしない。初期は同一Corpus Priorityとし、Heading／Body／Path／Exact Phraseの既存Scoreを使用する。

後続でRetrieval Guidance Metadata Portが導入された場合だけ、Document Role／Authority Tier／Alias／Language Boostを検証済みMetadataから受け取る。

## 5. Web Entry Point

### 5.1 New Explicit Option

```text
--documentation-rag-profile DOCUMENTATION_RAG_PROFILE_PATH
```

Entry Pointの決定順：

1. Web Access Profileを読む。
2. Bind／Authentication Policyを検証する。
3. Documentation RAG Capabilityを確認する。
4. Capability `denied`であればAdapterを構築しない。
5. Explicit Feature ProfileがあればPathとCompatibilityを検証する。
6. Explicit Profileがなく、Local Mac条件なら現行Mac Profileを選択する。
7. その他はAdapter `unavailable`とする。
8. Adapter構築成功後にToken Counter BinderをRuntimeへ渡す。

Public DemoでExplicit RAG Profileを受け取った場合は、Startup RefusalまたはProfileを完全に無視してDeniedとする方法がある。本Projectでは設定誤りを見逃さないためStartup Refusalを推奨する。どちらの方法でもBuilder Call／Docs Scanは0でなければならない。

### 5.2 Runtime Snapshot

UI／Runtime Snapshotは次を区別する。

```text
capability:
  eligible／denied

adapter:
  available／unavailable

effective_state:
  enabled／disabled／unavailable／denied

provider_display_name:
  non-secret display value

default_mode:
  off
```

CorpusのAbsolute Root、Feature Profile Absolute PathまたはPrivate Bootstrap PathをBrowserへ出さない。

## 6. Lightning Script Integration

### 6.1 Basic Preview Common

新しい解決値：

```text
margpa_documentation_rag_profile
```

Default Candidate：

```text
config/feature_profiles/lightning_basic_preview_public_documentation_rag.toml
```

Preflightは次を検証する。

- Project Root内Regular File。
- Expected Schema／Profile Key／Provider Key。
- `allowed_access_modes = [basic_preview]`。
- Lightning Platform Compatibility。
- Explicit 8 Path Contract。
- History／Lossless false。
- Expected／Present／Missing Count。

Corpus不足をWeb Server自体の起動Blockerとするかは、二つのPreflight Levelに分離する。

```text
Configuration Contract:
  fail when invalid

Corpus Readiness:
  pass／warning with counts
  RAG request itself remains fail-closed
```

### 6.2 Argument Construction

Basic Preview専用Validationに合格した場合だけ、Web Argumentへ次を追加する。

```text
--documentation-rag-profile <validated project file>
```

Public DemoとBasic Previewで同じ`margpa_build_web_arguments()`を使用する場合は、Access Modeを引数として明示し、Public経路へRAG Argumentが混入しないようにする。

### 6.3 Public Demo Environment Scrub

Public Demo Processは既存Basic Credentialに加え、次のOverrideを継承しない。

```text
MARGPA_DOCUMENTATION_RAG_PROFILE
```

Public ScriptのHelp／PreflightはRAG Deniedを表示するが、Corpus PathとPresent Fileを走査しない。

## 7. Index and Token Lifecycle

```text
Server Startup:
  no corpus read
  no index build

RAG OFF Request:
  no corpus read
  no index build

First RAG ON Request:
  build manifest
  read allowlisted docs
  deterministic chunk
  build in-memory index
  retrieve／assemble／cite

Later unchanged RAG ON Request:
  reuse in-memory index

Manifest change:
  build replacement index
  atomic replace after success

Studio sleep／process exit:
  memory index disappears

Next wake:
  lazy rebuild
```

Model Token Counterは既存Inference RuntimeがLoadした単一Model InstanceからBinder経由で取得する。RAG用にGGUFを二重Loadしない。

## 8. Bilingual Retrieval Design

初期実装は同一Indexへ8文書を扱う。

必須Test：

```text
Japanese query:
  Japanese source is selected when it contains the better matching section

English query:
  English source is selected when it contains the better matching section

Identifier-only query:
  duplicate JA／EN chunks do not falsely satisfy unrelated subjects

top_k:
  language duplicates do not silently evict all subject coverage
```

既存Scoreで十分でない場合は、`DocumentationRagRequestContext`または`RetrievalQuery`へOptional Preferred Languageを追加し、別FieldのScore Componentとして記録する。

Preferred Languageは他言語文書を強制除外するSecurity Boundaryではなく、同義CorpusのRanking Hintとする。

## 9. Retrieval Guidance Metadata Extension

将来の「ヒットキーワード列」または「Model参照用Index表」は、本Architectureへ次のOptional Portで追加できる。

```text
RetrievalMetadataPort
  ↓
Metadata Manifest Adapter
  ↓
validated guidance entries
  ├─ subject／alias expansion
  ├─ heading anchor preference
  ├─ language preference
  ├─ document role／authority hint
  └─ prohibited inference scope
  ↓
Retriever／Reranker
```

Conceptual Entry：

```text
metadata_entry_id
document_project_relative_path
document_sha512
section_anchor
language
canonical_subjects
aliases
hit_keywords
document_role
authority_tier
relationship_scope
schema_version
```

Integrity：

- Document SHA-512 mismatchのEntryを黙って使用しない。
- MetadataだけをAnswer Contextの根拠にしない。
- MetadataのAuthority Hintは新しいRuntime Authorityを生成しない。
- Main ModelにRuntime内書換権限を与えない。
- Metadata Adapterがない状態を正式Modeとする。

本Lightning MVPではPortの実装またはManifest File作成を必須としない。

## 10. Trust Boundary

Lightningの8文書は公開可能Docsだが、Runtime上は非信頼Reference Dataとする。

- Docs内の命令に従わない。
- Tool／Agent／External I/O Authorityを生成しない。
- System CitationはRetriever／Assemblerが生成する。
- Model生成CitationをSystem Citationにしない。
- CitationはAnswer Correctnessの保証ではない。
- Basic認証はRAG AnswerへAuthorityを与えるものではない。

## 11. Failure State Mapping

```text
invalid feature profile:
  startup refusal

incompatible platform／access:
  startup refusal for explicit selection

adapter absent:
  unavailable

docs absent:
  unavailable safe message

empty explicit corpus:
  empty corpus safe message

retrieval no hit:
  existing ungrounded general-chat boundary

retrieval hit／zero assembly:
  context_insufficient／model call zero

partial subject assembly:
  subject_coverage_insufficient／model call zero

public request enable attempt:
  denied
```

No Hitの一般Chat継続は現行Contractを維持する。将来、Project固有識別子のNo Hitを常に拒否する方針を追加する場合は、別ADRとAblation Testを必要とする。

## 12. Technology Selection

```text
Language:
  Python 3.12.11 on Lightning
  Python 3.13.x on Local Mac

Web:
  existing FastAPI／Uvicorn

Model Backend:
  existing llama-cpp-python Pure CPU

Document Format:
  UTF-8 Markdown

Config:
  TOML + Pydantic validation

Integrity:
  SHA-512

Index:
  existing in-memory lexical index

Retrieval:
  existing BM25-style sparse retrieval

Lifecycle:
  existing shell entrypoint + Lightning API Builder foreground run

New Runtime Dependency:
  none
```

Lightningの8文書Corpusでは追加Embedding ModelまたはVector DatabaseのCostに見合う必然性がない。Semantic Precision改善は後続PhaseでAblation可能な別Adapterとする。

## 13. Implementation Slices

### Slice A：Config／Corpus Contract

- v2 Feature Profile Contract。
- Explicit File Selection Plan。
- Lightning Profile TOML。
- Path／Corpus Validation。

### Slice B：Generic Composition

- Generic Builder。
- Mac Compatibility Wrapper／Regression。
- Explicit Web CLI Option。
- Access／Platform Compatibility。

### Slice C：Lightning Scripts

- Basic Preview Profile Resolution／Preflight。
- Basic `run`へArgument追加。
- Public Demo Environment Scrub／Argument非追加。

### Slice D：Tests

- Config／Source／Composition。
- Basic／Public Access。
- JA／EN Corpus。
- Existing Mac／Lightning Lifecycle／Web Regression。

### Slice E：User Manual Handoff

- 変更File配置。
- SHA-512。
- Test Command。
- Basic Preview Preflight／Run。
- Sleep／Wake。
- Public Demo Denial。

## 14. Acceptance View

```text
Basic Preview
  ├─ Basic authentication: required
  ├─ Public 8-doc corpus: available
  ├─ User RAG switch: OFF／ON
  ├─ In-memory lazy index: enabled when requested
  └─ Known semantic limits: disclosed

Public Demo
  ├─ Authentication: none
  ├─ Documentation adapter: absent
  ├─ Corpus scan: zero
  └─ RAG request: denied
```

本Architectureは、LightningへMac Corpusをそのまま持ち込むことではなく、Access、Provider、Corpus、PlatformおよびUser Selectionを分離するExternal Adapter Hookの最初の実証である。
