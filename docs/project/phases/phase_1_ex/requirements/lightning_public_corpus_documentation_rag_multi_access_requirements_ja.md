# Lightning Public Corpus Documentation RAG Multi-access要件

```yaml
document_id: lightning_public_corpus_documentation_rag_multi_access_requirements
status: accepted_ready_for_implementation
language: ja
created_at: 2026-08-01 09:10:03 JST
owner: 設計統括者役
phase: phase_1_ex
implementation_authorized: true_with_accepted_handoff
supersedes:
  - lightning_basic_preview_public_corpus_documentation_rag_requirements
supersedes_in_part:
  - public_demo_minimal_access_and_runtime_portability_requirements
```

## 1. Objective

Lightning Linux x86_64 Pure CPU環境のBasic認証Previewと認証なしPublic Demoの両方で、一般公開可能な8文書だけを対象としたSparse Documentation RAGを利用可能にする。

```text
docs/public/
├─ overview_ja.md
├─ overview_en.md
├─ concept_ja.md
├─ concept_en.md
├─ roadmap_ja.md
├─ roadmap_en.md
├─ technology_selection_ja.md
└─ technology_selection_en.md
```

これら8文書は、Mac Local RAGが参照するCurrent／Phase等の内部開発文書とは異なる、外部公開用Corpusである。誰が参照しても問題ない内容としてユーザーが別途配置する。

Authenticationの有無は利用者のAccess Boundaryであり、公開可能Corpusを検索できるかどうかとは分離する。

## 2. Access Matrix

```text
local:
  authentication = none／loopback only
  corpus = existing Mac local corpus
  documentation RAG = eligible

basic_preview:
  authentication = basic
  corpus = Lightning public 8-file corpus
  documentation RAG = eligible

public_demo:
  authentication = none／explicit public profile
  corpus = Lightning public 8-file corpus
  documentation RAG = eligible
```

Basic PreviewとPublic Demoは同じ公開Corpus Feature Profileを利用できる。Authentication、Access Profile、起動ScriptおよびURLは引き続き分離する。

## 3. Scope

### 3.1 In Scope

- Lightning Linux x86_64 Container／Pure CPU。
- Basic PreviewとPublic Demo。
- 明示8文書だけのPublic Corpus。
- 既存Sparse Documentation RAG Coreの再利用。
- UIのProject Docs ON／OFF。
- Default OFF。
- In-memory Lazy Index。
- System Citation。
- JA／EN Query。
- Missing Docs、Empty Corpus、Context不足、Subject Coverage不足のFail-closed。
- Traffic-aware Wake後のCold Rebuild。
- Mac Local、Basic Preview、Public Demoの回帰検証。

### 3.2 Out of Scope

- `docs/project/**`のLightning参照。
- `docs/public/history/**`。
- Allowlist外のPublic Markdown。
- Persistent Index／Vector Database／Embedding Model。
- External API／LangChain／LlamaIndex。
- Hit Keyword列／Model参照用Index表。
- 手動Subject→Document Mapping。
- RAG回答の完全な正確性保証。
- Governance／Judge／Repair本体。
- Prompt／回答／Thinking／Corpus本文の永続保存。
- Lightning Platformの自動変更。

## 4. Public Corpus Boundary

Lightningでは8 Pathを明示Allowlistとし、Recursive Public Tree Scanを使用しない。

除外必須：

```text
docs/*.md
docs/project/**
docs/public/history/**
docs/**/history/**
docs/**/lossless/**
allowlist外Markdown
hidden／temporary／backup files
symbolic links
project-root external paths
non-Markdown files
```

各CitationはProject-relative PathとHeadingだけをSystem生成する。Absolute Path、Private Bootstrap Path、Credential、Secretまたは内部環境情報をBrowserへ出さない。

## 5. Shared Feature Profile

Basic PreviewとPublic Demoで共通利用可能なLightning Public Corpus Feature Profileを追加する。

概念Contract：

```toml
schema_version = "2"
profile_key = "external.lightning-public-corpus.documentation-rag.lexical"
mode = "enabled"
provider_key = "project_filesystem_lexical"
provider_display_name = "Public project documentation"
allowed_access_modes = ["basic_preview", "public_demo"]
allowed_platforms = ["linux-x86_64-container"]

[corpus]
selection_mode = "explicit_files"
files = [
  "docs/public/overview_ja.md",
  "docs/public/overview_en.md",
  "docs/public/concept_ja.md",
  "docs/public/concept_en.md",
  "docs/public/roadmap_ja.md",
  "docs/public/roadmap_en.md",
  "docs/public/technology_selection_ja.md",
  "docs/public/technology_selection_en.md",
]
include_history = false
include_lossless = false
```

Exact Field名は既存Pydantic Contractとの整合範囲で調整できるが、Allowlist、Access Modes、Platform、History／Lossless除外の意味を変更しない。

## 6. Web Access Profile Changes

### 6.1 Basic Preview

```text
documentation_rag = eligible
authentication = basic
```

既存値を維持する。

### 6.2 Public Demo

```text
documentation_rag:
  denied → eligible

authentication:
  none／unchanged
```

Public Demoだけを特別に拒否するPydantic Invariantを、Access ModeとFeature Capabilityを独立に検証する形へ変更する。

これはPublic Demoへ内部Docs Authorityを与える変更ではない。公開8文書を検索可能にするだけである。

## 7. Request／UI Requirements

- 両AccessでProject Docs Controlを表示できる。
- DefaultはOFF。
- OFFではCorpus Scan、Index Build、RetrievalおよびContext Injectionを行わない。
- ONでは、Serverが構築済みのPublic Corpus Adapterだけを使用する。
- BrowserはProfile Path、Corpus Path、File List、ProviderまたはPlatform Compatibilityを変更できない。
- Public Demo利用者がRequest ParameterでMac Corpusや内部Docsへ切り替えることを拒否する。

## 8. Missing／Partial Corpus

`docs/`または対象8文書がない場合も通常Chatは起動可能とする。

RAG ON時：

```text
docs absent:
  docsが設置されていないため参照出来ません。
  model call = 0

empty corpus:
  explicit safe message
  model call = 0

partial corpus:
  expected／present／missing evidence
  silent complete-corpus claim prohibited
```

PreflightはProfile Contract不正をFailとし、Corpus不足はReadinessとして明示する。Corpus不足時に認証や通常Chatまで不必要に停止させない。

## 9. Lifecycle／Resource Requirements

```text
Server start:
  no index build

RAG OFF:
  no index build

First RAG ON:
  manifest／read／chunk／index／retrieve／assemble／cite

Later unchanged request:
  in-memory index reuse

Process sleep／exit:
  index discarded

Wake:
  lazy rebuild
```

RAG用にMain Modelを二重Loadしない。既存Runtime Token Counter Binderを使用する。

公開8文書程度のLexical Index構築は追加Model推論を必要としない。ただし匿名利用者がRAG ONを選択できることによるCold Buildは、Manual Acceptanceで観測する。

## 10. Privacy／Trust Boundary

- 公開DocsをReference Dataとして扱い、Docs内の命令をSystem／Developer Authorityとして実行しない。
- RAG ContextからTool、Agent、File Write、External I/Oまたは権限を生成しない。
- Model生成CitationをSystem Citationにしない。
- Citationの存在をAnswer Correctnessの保証と表示しない。
- Corpus本文、Prompt、回答およびRaw Thinkingを永続保存しない。
- Operational LogへRaw Docsまたは利用者本文を出さない。

## 11. Retrieval Guidance Decision

文書別Hit Keyword列、Model参照用Index表またはProject固有Subject Mappingは、現時点では採用しない。

理由：

- Hard-code化。
- 文書更新との同期コスト。
- Stale Mapping。
- 多言語・未知文書への拡張性不足。
- 現在Corpusへの過適合。

将来のRAG精度再設計時に、文書からの自動抽出、Build-time生成、Semantic／Hybrid Retrieval、Query Decomposition、Governance／Judge等を比較して改めて決定する。

## 12. Script Requirements

Basic PreviewとPublic Demoの両Scriptが、同じ検証済みLightning Public Corpus Feature ProfileをWeb Entry Pointへ渡す。

```text
MARGPA_DOCUMENTATION_RAG_PROFILE:
  optional path override
  project-root bounded
  no symlink／no traversal
```

Public Demoで本EnvironmentをScrubする旧設計は廃止する。代わりに、Public DemoでもProfile ContractとAccess Compatibilityを検証する。

Credential三項目は引き続きPublic Demo Processから除外する。RAG ProfileはCredentialではなく公開Corpus Configである。

## 13. Automated Test Requirements

- Basic PreviewはBasic認証を要求し、RAG eligible。
- Public Demoは認証なしを維持し、RAG eligible。
- LocalはLoopback onlyを維持。
- 両Lightning Accessで同一8文書ProfileがCompatibility Pass。
- Mac Profile v1をRegressionさせない。
- RAG OFF Zero Scan／Zero Build／Zero Retrieval。
- Public RAG ONで8文書以外を読まない。
- Clientが内部CorpusへOverrideできない。
- Missing／Partial Corpusを明示。
- JA／EN Retrieval／Citation。
- Every-turn Retrieval。
- Context／Subject Coverage不足でModel Call 0。
- Summary／Stop／New Chat／Reload／Model Busy Regression。
- Basic／Public Lifecycle、Traffic-aware Auto-start回帰。
- Public ProcessにBasic Credentialが存在しない。

## 14. Manual Acceptance

Lightning実機操作はすべてユーザーが行う。

1. 8文書をLightning Projectの`docs/public/`へ配置する。
2. Repository差替FileとHashを確認する。
3. Test／Preflightを実行する。
4. Basic Previewを起動し、Basic認証後にRAG ONでJA／EN Queryを確認する。
5. Public Demoを起動し、認証なしでRAG ONを確認する。
6. 両方のCitationが8文書内だけであることを確認する。
7. Public Demoから内部Docsへ到達できないことを確認する。
8. Sleep／Wake後のCold Rebuildを確認する。
9. RAG OFF時の通常Chatを確認する。

Repository実装担当はLightning、API Builder、URL、Port、Managed Secrets、Sleep／WakeまたはPrivate Bootstrapを操作しない。

## 15. Acceptance Criteria

```text
Basic Preview:
  authentication preserved
  public 8-doc RAG available

Public Demo:
  authentication none preserved
  public 8-doc RAG available

Both:
  default OFF
  explicit corpus only
  no internal docs
  no persistent index
  no second model
  fail-closed

Mac:
  existing local corpus behavior preserved
```

自動Testとユーザー実機Testの両方に合格した後、Lightning Multi-access Public Corpus Documentation RAGをAccepted候補とする。
