# Lightning Basic Preview Public Corpus Documentation RAG 要件

```yaml
document_id: lightning_basic_preview_public_corpus_documentation_rag_requirements
status: accepted_ready_for_implementation
language: ja
created_at: 2026-08-01 08:49:52 JST
owner: 設計統括者役
phase: phase_1_ex
implementation_authorized: true_with_accepted_handoff
depends_on:
  - mac_local_documentation_rag_requirements
  - public_demo_minimal_access_and_runtime_portability_requirements
  - adr_0026_lightning_basic_preview_lifecycle_and_managed_secrets
  - adr_0027_public_demo_minimal_access_and_deferred_control_hooks
  - adr_0028_mac_local_sparse_documentation_rag_and_external_adapter_hook
```

## 1. Objective

Mac Localで成立したSparse Documentation RAGを、既存Lightning Linux x86_64 Pure CPU RuntimeのBasic認証Previewに限定して接続する。

Lightningへ配置するCorpusは、一般公開可能として別途作成した日本語／英語文書8件だけとする。

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

本実装はMac用CorpusをLightningへ全Copyするものではない。Basic Preview向けのPublic Corpus境界を明示し、Public DemoのRAG強制無効を維持する。

## 2. Scope

### 2.1 In Scope

- Lightning Linux x86_64 Container／Pure CPU。
- Basic認証Preview Access Profile。
- Project Root内`docs/public/`の明示8文書。
- 既存Sparse／Lexical RAG Adapterの再利用。
- In-memory Lazy Index。
- SHA-512 Manifest／Document／Chunk Integrity。
- Existing Model Token Counter。
- Existing UIのProject Docs ON／OFF。
- System Citation。
- Missing Docs／Empty Corpus／Context不足／Subject Coverage不足のFail-closed。
- Traffic-aware Wake-up後のCold Index Build。
- Mac Local、Basic PreviewおよびPublic DemoのRegression。

### 2.2 Out of Scope

- Public DemoでのDocumentation RAG。
- 認証なしAccessへのDocs提供。
- `docs/project/current/`、Phase Index、Completed Phase、History、LosslessまたはSharedのLightning検索。
- Persistent Index、Vector Database、Embedding ModelまたはExternal API。
- LangChainまたはLlamaIndex。
- Retrieval Guidance Metadata／Hit Keyword Manifestの実装。
- RAG回答の完全な正確性保証。
- ARGD／DAGD／Judge／Repairの実行。
- Lightning Platform、API Builder、Public URL、Port、Managed Secrets、Private BootstrapまたはCreditの自動変更。
- 設計統括者役または実装者役によるLightning実機操作。

## 3. Access and Authority Requirements

### 3.1 Basic Preview

```text
Access Profile:
  basic_preview

Authentication:
  Basic

Documentation RAG Capability:
  eligible

Adapter Availability after implementation:
  available when a valid Lightning RAG Feature Profile is selected

Default requested mode in browser:
  OFF
```

Credentialは既存どおりLightning Managed Secrets／Environmentからのみ取得する。RAG Config、Citation、LogまたはStatusへCredentialを書かない。

### 3.2 Public Demo

```text
Access Profile:
  public_demo

Documentation RAG Capability:
  denied

Adapter construction:
  prohibited

Corpus scan:
  prohibited

UI enablement:
  prohibited

Request override:
  rejected
```

Public Demoは、Lightning RAG Feature ProfileのFile、Environment VariableまたはCLI Optionが存在してもRAG Adapterを構築しない。

### 3.3 Client Boundary

Browser Clientが指定できるのは、Serverが許可した場合のRAG ON／OFFだけである。

Clientは次を変更できない。

- Feature Profile Path。
- Corpus Root。
- Allowed Document List。
- History／Lossless Inclusion。
- Provider Key。
- Index Backend。
- Public Demo Capability。
- Authority Priority。

## 4. Corpus Requirements

### 4.1 Explicit Public File Set

Lightning Corpusは前掲8 Pathの明示Allowlistとする。`docs/public/**/*.md`の無制限Recursive ScanをLightning Profileの簡略手段としない。

次は検索対象外とする。

```text
docs/*.md
docs/project/**
docs/public/history/**
docs/**/history/**
docs/**/lossless/**
hidden files
temporary files
backup files
symbolic links
project-root external paths
non-Markdown files
allowlist外のMarkdown
```

### 4.2 Bilingual Corpus

日本語版と英語版は概要版／詳細版の関係ではなく、公開Docs作成ルールに従い同等粒度の派生版とする。

初期Lightning Adapterは8文書すべてをIndex化できる。ただし、同一SubjectのJA／EN Chunk重複がTop Kを消費しないことをTestする。

必要であれば、後方互換なOptional `preferred_document_language`をRetrieval Contextへ追加できる。`ja`、`en`および`auto`の回答言語とDocument Languageを同一の固定値へ強制しない。

### 4.3 Missing／Partial Corpus

`docs/`または`docs/public/`がない場合、通常Chatは起動可能とする。RAG ON Requestでは次を返し、Project固有回答をModelに推測させない。

```text
docsが設置されていないため参照出来ません。
```

8文書の一部が不足する場合、存在する文書だけを黙って完全Corpusと表示しない。Preflight／Runtime EvidenceでExpected／Present／Missing Countを非秘密情報として識別できるようにする。

## 5. Feature Profile Requirements

Lightning用Documentation RAGは、既存Deployment Profile、Web Access ProfileおよびModel Definitionと分離したFeature Profileとする。

概念Contract：

```toml
schema_version = "2"
profile_key = "external.lightning-basic-preview.documentation-rag.lexical"
mode = "enabled"
provider_key = "project_filesystem_lexical"
provider_display_name = "Lightning public documentation"
allowed_access_modes = ["basic_preview"]
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

Exact Field名は実装時のPydantic Contractに合わせて調整できるが、次の意味を変更しない。

1. Access ModeがBasic Previewに限定される。
2. PlatformがLightning想定のLinux x86_64 Containerとして検証される。
3. Corpusが明示8文書に限定される。
4. Mac v1 Profileの挙動を変更しない。
5. Unknown Schema、Provider、Access Mode、Platformまたは安全でないPathを拒否する。

## 6. Composition Requirements

### 6.1 Explicit Composition

Web Entry Pointは、OS判定だけでRAGを自動有効化しない。

新しい明示入力概念：

```text
--documentation-rag-profile DOCUMENTATION_RAG_PROFILE_PATH
```

Resolution：

```text
Mac Local／option omitted:
  existing local Mac default profile

Linux／option omitted:
  adapter unavailable

Linux Basic Preview／valid option:
  build selected documentation adapter

Public Demo／option present:
  refuse or ignore without construction according to fail-closed access contract
  request can never enable RAG
```

Feature Profile PathはProject Root内のRegular Fileとし、Symlink、Traversal、Root外PathまたはLine Breakを拒否する。

### 6.2 Existing Adapter Reuse

次を再利用する。

- Deterministic Markdown Chunker。
- Unicode／Japanese-aware Tokenizer。
- BM25-style Retriever。
- In-memory Lexical Index。
- Bounded Context Assembler。
- System Citation Adapter。
- Deferred Model Token Counter Binder。
- Coverage Integrity／Fail-closed Contract。

`build_local_documentation_rag()`をLinuxで直接Hard-codeして呼ぶだけの場当たり対応にせず、汎用Composition Functionまたは互換Wrapperとして整理する。Mac用Public APIを破壊しない。

## 7. Lightning Lifecycle Requirements

### 7.1 Basic Preview Service

Basic Preview用Scriptは、Lightning RAG Feature Profileの既定Pathを検証し、Foreground `run`のWeb Argumentへ安全に渡す。

新しいEnvironment概念：

```text
MARGPA_DOCUMENTATION_RAG_PROFILE
```

CredentialではなくPath Configである。値をLogへ無制限に出さず、Project-relativeまたは検証済みProject内Pathとして扱う。

Basic PreviewのDefaultとして追跡済みLightning RAG Profileを選択するか、明示Environmentで選択するかは実装時に固定する。ただしAPI Builder／Private Bootstrapの長大なCommandを再導入しない。既存`run`契約とTraffic-aware Wake-upを維持する。

### 7.2 Public Demo Service

Public Demo Scriptは次を必ず行う。

- Documentation RAG ProfileのEnvironment Overrideを引き継がない。
- Documentation RAG CLI Argumentを渡さない。
- Public Access Profileの`denied`をPreflightで確認する。
- Adapter Builderが呼ばれないことをTestする。

### 7.3 Sleep／Wake

Studio Sleep後のTraffic-aware Wake-upでは、Process Memory内Indexは失われる。起動後の最初のRAG ON RequestでManifestとIndexをLazy Buildする。

Persistent Index Fileを勝手に作成しない。通常Chatだけの利用でDocs ScanまたはIndex Buildを強制しない。

## 8. Runtime Requirements

- Python 3.12.11の現行Lightning Environmentで動作する。
- Python 3.13 Local Macの既存動作を維持する。
- 新規Dependencyを追加しない。
- Main Modelの二重Loadを行わない。
- Loaded llama.cpp ModelのToken CounterをExisting Binder経由で使用する。
- RAG OFFでRetrieval／Index Build／Context Injectionを行わない。
- Corpus本文、Prompt、AnswerおよびRaw Thinkingを永続保存しない。
- Operational LogへRaw Docs、Absolute Path、CredentialまたはSecretを出さない。
- CitationはProject-relative PathとHeadingだけをSystemが生成する。

## 9. Error Requirements

| Condition | Required State |
|---|---|
| Feature Profile不正 | Startup refusal |
| Public DemoにRAG Profile指定 | No adapter construction／RAG denied |
| `docs/`なし | Explicit unavailable message／Model Call 0 |
| Corpus 0件 | Explicit empty-corpus message／Model Call 0 |
| 文書不足 | EvidenceとSafe Stateで識別 |
| Context 0 Block | `context_insufficient`／Model Call 0 |
| Subject Coverage不足 | `subject_coverage_insufficient`／Model Call 0 |
| No lexical hit | Existing no-hit boundary |
| Read中変更 | Changed document exclusion／Warning |
| Index Build失敗 | Existing valid indexを真として強制使用しない |

## 10. Retrieval Quality Boundary

Mac第2回手動Testで確認した次の限界は、Lightningでも継承される。

- Citationの存在は、Answerの全ClaimがGroundedである保証ではない。
- Lexical Subject CoverageはSemantic Sufficiencyの保証ではない。
- 4B級Modelは正式名称、略称、System間関係またはRoadmap進捗を誤る可能性がある。
- Lightningへ移すこと自体は精度向上を保証しない。

これらを隠してProduction-readyまたはAuthority-readyと表示しない。

## 11. Future Retrieval Guidance Hook

文書／Section単位のHit Keyword、Alias、Language、Document Role、Authority Tier、Heading AnchorおよびDocument SHA-512を扱うOptional Metadata Portを後続実装可能とする。

```text
RetrievalMetadataPort:
  optional
  default unbound
  deterministic
  read-only
  digest-bound
  not an authority generator
```

本Lightning HookのAcceptanceにこのMetadata実装を必須としない。

## 12. Automated Test Requirements

### 12.1 Config／Composition

- Mac Local Option省略で既存Adapterが構築される。
- Linux Option省略でAdapterが構築されない。
- Linux Basic Preview／Valid Lightning Feature ProfileでAdapterが構築される。
- Public DemoでBuilder Call 0、Docs Scan 0、RAG Denied。
- Unknown／Unsafe Profileを拒否する。

### 12.2 Corpus

- 8文書だけがManifestに含まれる。
- `docs/`Root、Current、Shared、Phase、History、LosslessおよびAllowlist外Public Markdownを除外する。
- JA／ENの各Pathを識別する。
- Missing／Partial Corpusを明示する。
- Symlink／Traversal／Root Escapeを拒否する。
- Manifest DigestがContent変更で変化する。

### 12.3 Retrieval／Conversation

- `overview`、`concept`、`roadmap`および`technology selection`のJA／EN Query。
- RAG OFF Zero Call。
- RAG ON Every-turn Retrieval。
- Summary Original Stage Retrieve Once。
- Context／Subject Coverage Fail-closed。
- Citation Relative Path／Heading。
- Stop／New Chat／Reload／Model Busy Regression。

### 12.4 Lightning Scripts

- Basic Preview PreflightがRAG ProfileとCorpus Presenceを値非公開で検証する。
- Basic Preview `run`がFeature Profile Argumentを渡す。
- Public Demo `run`がFeature Profile Argumentを渡さない。
- Public Demo Process EnvironmentからRAG Profile Overrideを除外する。
- Existing Lifecycle／Traffic-aware Auto-start TestをRegressionさせない。

### 12.5 Full Verification

```bash
./.venv/bin/pytest -q tests/unit/documentation_rag
./.venv/bin/pytest -q tests/integration/documentation_rag
./.venv/bin/pytest -q tests/unit/web
./.venv/bin/pytest -q tests/integration/web/test_web_app.py
./.venv/bin/pytest -q tests/unit/runtime/test_lightning_basic_preview_service.py
./.venv/bin/pytest -q
./.venv/bin/ruff check .
./.venv/bin/ruff format --check .
./.venv/bin/mypy .
node --check src/margpa_runtime_llm/web/static/app.js
bash -n scripts/runtime/lightning/basic_preview_common.sh
bash -n scripts/runtime/lightning/basic_preview_service.sh
bash -n scripts/runtime/lightning/public_demo_service.sh
```

## 13. Manual Acceptance Requirements

Lightning実機操作はユーザーが行う。

1. 8文書を`margpa-runtime-llm/docs/public/`へ配置する。
2. PreflightでBasic Preview、RAG Profile、CorpusおよびCredentialを確認する。
3. Repository Testを実行する。
4. Basic PreviewをForeground／API Builder契約で起動する。
5. Basic認証後、Project Docs ControlをONにしてJA／EN Queryを確認する。
6. Citation Pathが8文書のいずれかであることを確認する。
7. Studio Sleep後のURL AccessでWakeし、RAG ON RequestがCold Rebuild後に動作することを確認する。
8. Public DemoでRAG Controlがなく、Request有効化が拒否されることを確認する。

外部Access、Sleep／Wake、Port、Managed Secrets、API BuilderおよびPublic URLの変更を実装者に実施させない。

## 14. Acceptance Criteria

```text
Basic Preview:
  authenticated access preserved
  RAG control available
  8-file corpus only
  JA／EN retrieval works or safely denies
  citations are project-relative

Public Demo:
  RAG denied
  adapter not constructed
  docs not scanned

Runtime:
  no new dependency
  no persistent index
  no second model load
  no Mac regression
  no Lightning lifecycle regression

Documentation quality:
  known semantic limitations remain explicit
```

すべての自動Testとユーザー実機Testに合格した後、Lightning Basic Preview Documentation RAG Adapter HookをAccepted候補とする。
