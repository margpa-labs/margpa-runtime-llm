# 実装担当向け Phase 1-ex Lightning Basic Preview Public Corpus Documentation RAG Adapter Hook Handoff

```yaml
document_id: implementer_handoff_phase_1_ex_lightning_basic_preview_public_corpus_documentation_rag_adapter_hook
phase: phase_1_ex
status: accepted_ready_for_implementation
language: ja
created_at: 2026-08-01 09:01:59 JST
owner: 設計統括者役
target_role: 実装者役
external_operation_owner: user
requirements: ../../requirements/lightning_basic_preview_public_corpus_documentation_rag_requirements_ja.md
architecture: ../../architecture/lightning_basic_preview_public_corpus_documentation_rag_adapter_hook_architecture_ja.md
decision: ../../adr/adr_0029_lightning_basic_preview_public_corpus_documentation_rag_adapter_hook_ja.md
source_evidence: ../operations/mac_local_documentation_rag_manual_test_2_findings_20260801084952.md
```

## 1. Objective

Mac LocalでScoped AcceptedとなったSparse Documentation RAG Coreを、既存Lightning Linux x86_64 Pure CPUのBasic認証Previewへ接続できるExternal Adapter Hookとして実装する。

Lightning Corpusは、ユーザーが別途配置する公開可能文書8件だけとする。

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

本Handoffの目的は、Mac用CorpusをLightningへ複製することではない。Access Profile、Corpus Selection、Platform Compatibility、Adapter AvailabilityおよびUser Requested Modeを分離し、Basic Previewだけが明示的なPublic Corpus Adapterを利用できる状態を作ることである。

```text
Basic Preview:
  Basic authentication required
  Documentation RAG eligible
  explicit public-corpus profile
  adapter may be constructed

Public Demo:
  authentication none
  Documentation RAG denied
  adapter construction zero
  docs scan zero
```

## 2. Required Reading

次の順序で全文をRead-only参照する。

1. `../operations/mac_local_documentation_rag_manual_test_2_findings_20260801084952.md`
2. `designer_review_phase_1_ex_mac_local_documentation_rag_manual_test_2_20260801084952.md`
3. `../../requirements/lightning_basic_preview_public_corpus_documentation_rag_requirements_ja.md`
4. `../../architecture/lightning_basic_preview_public_corpus_documentation_rag_adapter_hook_architecture_ja.md`
5. `../../adr/adr_0029_lightning_basic_preview_public_corpus_documentation_rag_adapter_hook_ja.md`
6. `../../requirements/mac_local_documentation_rag_requirements_ja.md`
7. `../../architecture/mac_local_documentation_rag_architecture_ja.md`
8. `../../adr/adr_0028_mac_local_sparse_documentation_rag_and_external_adapter_hook_ja.md`
9. `../../../../shared/operations/research_asset_mutation_control_ja.md`
10. `../../../../shared/task_roles/task_role_write_authority_policy_ja.md`

第2回手動Testで確認したSemantic Precisionの限界は、本実装で解消済みとして扱わない。本実装はCross-environment Adapter Hook、Public-only Corpus BoundaryおよびAccess Separationの実装である。

## 3. Source Freeze／Pre-mutation Gate

開始前に次を確認する。

- Project Rootが`margpa-runtime-llm/`である。
- Project Root外へ触れない。
- `models` Symbolic Linkを追跡しない。
- 既存History、Status、ReviewまたはIndexを上書きしない。
- 変更予定Fileを先に列挙する。
- 下記Baseline Hashと現在値を比較する。
- 不一致時は勝手にMergeせず、対象、現在Hashおよび必要な差分を報告して停止する。
- Git、GitHub、Lightning、API Builder、Upload、Port、Managed SecretsまたはPrivate Bootstrapを操作しない。

主要Baseline SHA-512：

```text
src/margpa_runtime_llm/bootstrap/documentation_rag.py
a0b47d49ec7f386aaf4253f145b72d73d49f976da0d758f44c8f10b9e3834596b869e2aeade3eb7bf42b832c192dfdfb0be600fedb46224abb44c4d56598a49b

src/margpa_runtime_llm/entrypoints/web/main.py
e6e176c234e452a963599a8610e6f2fdc16b6da101fa96c97833f59a867cf2e1961c0db6a4c1395c8a3531468d7803d434d8b1085603ba0b187f5c692577cbd2

config/feature_profiles/local_documentation_rag.toml
cb7e937ffcb00a6cd181727c322356d54f00bba14149d4db7bf41e5a20db33d82091dd7b90f4a6b30d49a1ed473930ed6dc43c61562e747054b4dcf8aca92f31

scripts/runtime/lightning/basic_preview_common.sh
e86e1dd85eb48d68523bcc0e3fe859c66e413cff3688412a84c90ce8ec86cd9bab71e9ea9ec27bb52230159fd574a45b789c8b205a6cb37d6fe2bf2a2f843c14

scripts/runtime/lightning/basic_preview_service.sh
eb24cc058be641ab09ace05340cb05377900474ff2cbfac6227308ee52a3926c4bec921c8f981885b973351406b2d05cb2fcf7c691015deb626e6d3639e0e102

scripts/runtime/lightning/public_demo_service.sh
8f4cac68946ab3827e82446f2c04a58516ffffcb13fe27c81218086a112443e1ee4042b3a0084a785ebc00cf2251fd2c9e41e8bb1f015dbbf62a3139ff416aa8

tests/unit/runtime/test_lightning_basic_preview_service.py
502866c3cce07145ffd13b046b1b0e2fa4811c8731c288b2925f236f9b4acd5a74b589c16316da1cbb0f1f3f8c2035b54b27c64ba1d25ebb4979cbd6253ff46b
```

## 4. Authorized Mutation Scope

必要な最小差分に限り、次を変更できる。

```text
config/feature_profiles/
  lightning_basic_preview_public_documentation_rag.toml

src/margpa_runtime_llm/modules/documentation_rag/
src/margpa_runtime_llm/adapters/documentation_rag/
src/margpa_runtime_llm/bootstrap/documentation_rag.py
src/margpa_runtime_llm/bootstrap/web_application.py
src/margpa_runtime_llm/entrypoints/web/main.py

scripts/runtime/lightning/basic_preview_common.sh
scripts/runtime/lightning/basic_preview_service.sh
scripts/runtime/lightning/public_demo_service.sh

tests/unit/documentation_rag/
tests/integration/documentation_rag/
tests/unit/web/
tests/integration/web/test_web_app.py
tests/unit/runtime/test_lightning_basic_preview_service.py

docs/project/phases/phase_1_ex/history/handoffs/
  implementer_status_phase_1_ex_lightning_basic_preview_public_corpus_documentation_rag_adapter_hook_YYYYMMDDHHMMSS.md
```

既存Moduleの公開Exportを後方互換に保つための`__init__.py`最小変更は許可する。

次は変更しない。

```text
docs/public/
docs/project/current/
docs/project/shared/
Phase Index
Accepted Requirements／Architecture／ADR
既存History
README.md
LICENSE／TERMS_OF_USE／NOTICE／CITATION
config/web_profiles/
config/profiles/
config/models/
pyproject.toml
uv.lock
Model Artifact
Repository外Private Bootstrap
```

公開8文書の作成、翻訳、編集または内容修正は実装者Scope外である。TestではProject内のPytest Temporary Fixtureに同名の最小文書を作り、実Corpusの内容へ依存しない。

## 5. Required Implementation

### 5.1 Backward-compatible Feature Profile Contract

既存Mac Profile v1を壊さず、Lightningの明示File Corpusを表すProfile Contractを追加する。

必須意味：

```text
schema_version:
  v1 Mac tree selectionとv2 explicit file selectionを曖昧に混在させない

allowed_access_modes:
  basic_preview only

allowed_platforms:
  linux x86_64 container

corpus.selection_mode:
  explicit_files

corpus.files:
  exact public 8-file allowlist

include_history:
  false

include_lossless:
  false
```

Unknown Schema、Unknown Provider、Unknown Access Mode、Unknown Platform、Duplicate Path、Absolute Path、Traversal、Backslash、Line Break、SymlinkまたはProject Root EscapeをFail Closedで拒否する。

### 5.2 Explicit Corpus Selection

既存`LocalMarkdownDocumentSource`のTree ScanをLightningへ流用して`docs/public/**/*.md`を丸ごと読む実装は禁止する。

検証済みCorpus Selection Planまたは同等のNarrow Contractを導入し、Lightningでは前掲8件だけを候補とする。

除外必須：

```text
docs/project/**
docs/public/history/**
docs/**/history/**
docs/**/lossless/**
allowlist外Markdown
hidden／temporary／backup files
symbolic links
project-root external paths
```

8件の一部が存在しない場合、存在する文書だけを完全Corpusと表示しない。Expected／Present／Missing Countを非秘密Evidenceとして識別し、RAG ON Requestは既存Fail-closed Contractで安全に処理する。

### 5.3 Generic Composition／Mac Compatibility

`build_local_documentation_rag()`をLinuxで条件外に直接呼ぶだけのHard-codeは禁止する。

次を満たすGeneric Builderまたは同等構造へ整理する。

```text
Inputs:
  project root
  defaults profile
  feature profile
  access mode
  platform observation

Outputs:
  contextual RAG orchestrator
  validated config
  profile digest
  deferred token counter binder
```

既存Mac Call SiteとTestはCompatibility Wrapperまたは同等の後方互換経路で維持する。Main Modelを二重Loadせず、既存Token Counter Binderを再利用する。

### 5.4 Web Composition Boundary

Web CLIへ明示Optionを追加する。

```text
--documentation-rag-profile DOCUMENTATION_RAG_PROFILE_PATH
```

決定順：

1. Web Access Profileを検証する。
2. Documentation RAG Capabilityを確認する。
3. `denied`ならFeature Profileを構築せず、Docsを走査しない。
4. Explicit ProfileがあればPath、AccessおよびPlatform Compatibilityを検証する。
5. Explicit ProfileがなくLocal Mac条件なら既存Mac Profileを選択する。
6. その他はAdapter `unavailable`とする。
7. 構築成功後だけToken CounterをBindする。

Public DemoへExplicit RAG Profileが与えられた場合はStartup Refusalを推奨する。少なくともBuilder Call 0、Docs Scan 0およびUI Enablement 0をTestで証明する。

### 5.5 Lightning Basic Preview Script

Basic Preview用の既定Feature ProfileをProject内追跡Fileとして解決する。

```text
config/feature_profiles/lightning_basic_preview_public_documentation_rag.toml
```

Optional Environment Override名：

```text
MARGPA_DOCUMENTATION_RAG_PROFILE
```

値はCredentialではないが、Project Root内Regular File、No Symlink、No Traversalを検証する。Basic Previewの`run`へ検証済みProfile Argumentだけを渡す。

Preflightは次を分離する。

```text
Configuration Contract invalid:
  fail

Corpus Readiness partial／missing:
  explicit expected／present／missing evidence
  server startup itselfは必ずしも阻止しない
  RAG request remains fail-closed
```

既存Foreground `run`、Traffic-aware Wake-up、Basic認証、Managed Secrets、Port 7860およびLifecycle Contractを変更しない。

### 5.6 Public Demo Denial／Environment Scrub

Public Demo Processでは次を継承しない。

```text
MARGPA_DOCUMENTATION_RAG_PROFILE
```

Public DemoのPreflight／RunでCorpus Pathを解決、表示または走査しない。既存`documentation_rag = denied`を維持し、Client Requestで有効化できないことを証明する。

### 5.7 Index Lifecycle

```text
Server startup:
  no corpus read
  no index build

RAG OFF:
  no corpus read
  no index build

First RAG ON:
  manifest／read／chunk／in-memory index／retrieve／assemble／cite

Unchanged later RAG ON:
  reuse in-memory index

Process sleep／exit:
  index disappears

Next wake:
  lazy rebuild
```

Persistent Index、Cache File、Vector Databaseまたは追加Embedding Modelを作らない。

## 6. Retrieval Guidance Metadata Reservation

第2回手動Testで必要性候補となった文書別Hit Keyword列／RAG用Model参照Index表は、今回実装しない。

ただし、将来次のOptional Portを追加できる境界を壊さない。

```text
RetrievalMetadataPort:
  document path
  document SHA-512
  section anchor
  language
  canonical subjects
  aliases
  hit keywords
  document role
  authority tier
  relationship scope／prohibited inference
```

MetadataはRetrieval Hintであり、根拠本文、真実性、AuthorityまたはExecution Permissionを生成しない。個別のEASA、DLAGSA、OCILNS、ARGD、DAGD等をSource CodeへHard-codeしない。

## 7. Required Automated Tests

### 7.1 Config／Source

- v1 Mac Profileが従来どおり有効。
- v2 Explicit File Profileが8 Pathを正確に保持。
- Unsafe／Unknown Profileを拒否。
- ManifestはAllowlist 8件だけ。
- Current、Shared、Phase、History、Lossless、Allowlist外Publicを除外。
- Missing／Partial CorpusのCountを識別。
- Symlink、Traversal、Root Escapeを拒否。
- Content変更でManifest Digestが変化。

### 7.2 Composition／Access

- Mac Local／Option省略で既存Adapterを構築。
- Linux／Option省略でAdapterを構築しない。
- Linux Basic Preview／Valid ProfileでAdapterを構築。
- Public DemoでBuilder Call 0、Docs Scan 0、RAG Denied。
- Public DemoのEnvironment Overrideを除外。

### 7.3 Conversation／Bilingual Corpus

- JA Queryが対応JA Sectionを取得できる。
- EN Queryが対応EN Sectionを取得できる。
- Identifier-only QueryでJA／EN重複が無関係Subjectを満たさない。
- RAG OFF Zero Call。
- RAG ON Every-turn Retrieval。
- Summary Original Stage Retrieve Once。
- Context／Subject Coverage不足でModel Call 0。
- CitationはProject-relative Path／Heading。
- Stop／New Chat／Reload／Model BusyをRegressionさせない。

TestはAnswer Correctnessを過剰に固定せず、Deterministic Retrieval、Access、Corpus、CitationおよびFail-closed Contractを検証する。

### 7.4 Lightning Script

- Basic Preview PreflightがProfile Contractを検証。
- Basic Preview `run`がRAG Profile Argumentを渡す。
- Public Demo `run`はArgumentを渡さない。
- Public Demoの全子ProcessにOverrideがない。
- 既存Lifecycle／Auto-start TestがGreen。

## 8. Verification Commands

最低限、次を実行する。

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

新規Dependencyがないことを確認し、`pyproject.toml`と`uv.lock`を変更しない。実GGUF Model Load、Lightning外部URL、Sleep／WakeおよびManual Browser Acceptanceは実装者Scope外であり、未実施項目をPassと書かない。

## 9. Prohibited

- Project Root外のRead／Write／Copy／Delete／Permission変更
- Lightning Studio／API Builder／Port／URL／Managed Secrets／Machine／Credit操作
- Repository外Private Bootstrapの変更
- Basic認証Previewの削除
- Public DemoへのRAG追加
- 公開8文書の作成、翻訳または編集
- Persistent Index／Cache作成
- Embedding、Vector DB、LangChain、LlamaIndexまたはExternal API追加
- ARGD／DAGD／Judge／Repairの先行実装
- Query固有略称のHard-code
- Model Artifact操作
- Dependency変更
- Git／GitHub操作
- `.DS_Store`、Cache、既存Artifactまたは無関係FileのCleanup
- Scope外のついで修正

## 10. Completion Status

完了後、新Timestampで次を作成する。

```text
docs/project/phases/phase_1_ex/history/handoffs/
implementer_status_phase_1_ex_lightning_basic_preview_public_corpus_documentation_rag_adapter_hook_YYYYMMDDHHMMSS.md
```

Statusへ必ず記載する。

- 全Changed／Added File。
- Before／After SHA-512。
- Profile v1／v2の互換境界。
- Explicit Corpus SelectionのCall Graph。
- Access判定からBuilderまでのCall Order。
- Public Demo Builder Call 0／Docs Scan 0のTest Evidence。
- Basic Preview Scriptへ渡すArgumentとPublic側のScrub位置。
- Lazy Index／Token Counter Lifecycle。
- Expected／Present／Missing Countの扱い。
- Test Command、件数、結果および所要時間。
- 未実行項目。
- Known Limitation。
- Project外、Lightning、GitおよびModel Artifactを変更していないこと。
- Scope外変更が0件であること。

既存Handoff、Status、Review、IndexまたはStable文書を上書きしない。

## 11. Acceptance Gate

実装者完了は、Repository実装と自動Testの完了であり、Lightning実機Acceptanceではない。

```text
Repository Implementation:
  accepted candidate after designer review

Mac Regression:
  required

Basic Preview RAG Hook:
  automated contract required

Public Demo RAG Denial:
  automated proof required

Lightning Manual Placement／Run／Wake／Browser:
  user only／pending after repository review

Semantic Answer Correctness:
  known limitation／not acceptance guarantee
```

設計統括者役Review後、ユーザー向けにLightning上の差替File、SHA-512、Test、Preflight、Basic Preview／Public DemoおよびSleep／Wake確認手順を別Handoffとして作成する。
