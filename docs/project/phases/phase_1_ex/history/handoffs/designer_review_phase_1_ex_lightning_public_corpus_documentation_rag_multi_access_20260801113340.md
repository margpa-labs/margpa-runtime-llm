# 設計統括者Review：Phase 1-ex Lightning Public Corpus Documentation RAG Multi-access

```yaml
document_id: designer_review_phase_1_ex_lightning_public_corpus_documentation_rag_multi_access
phase: phase_1_ex
status: implementation_accepted_lightning_manual_acceptance_go
language: ja
created_at: 2026-08-01 11:33:40 JST
owner: 設計統括者役
source_index: ../documentation_index_20260801091003.md
source_handoff: implementer_handoff_phase_1_ex_lightning_public_corpus_documentation_rag_multi_access_20260801091003.md
reviewed_status: implementer_status_phase_1_ex_lightning_public_corpus_documentation_rag_multi_access_20260801093954.md
manual_acceptance_gate: go_with_complete_public_corpus_precondition
```

## 1. Decision

実装担当Status、変更Artifact、Feature Profile、Access Matrix、Explicit Corpus Source、Composition Root、Web CLI、Lightning Lifecycle Script、Unit／Integration TestおよびSHA-512を独立に確認した。

```text
Repository Implementation:
  ACCEPTED

Basic Preview Basic Auth:
  PRESERVED

Basic Preview Public 8-doc RAG:
  ACCEPTED／ELIGIBLE／DEFAULT OFF

Public Demo Authentication None:
  PRESERVED

Public Demo Public 8-doc RAG:
  ACCEPTED／ELIGIBLE／DEFAULT OFF

Mac Local Documentation RAG v1:
  PRESERVED

Internal Project Docs Exclusion:
  ACCEPTED

Lightning Manual Acceptance:
  GO／USER-ONLY／PUBLIC CORPUS COMPLETION REQUIRED

Feature Final Acceptance:
  PENDING LIGHTNING MANUAL EVIDENCE
```

BlockerまたはHigh／Medium Priorityの不整合は確認されなかった。Repository実装はAcceptedとし、ユーザー担当によるLightning実機配置、Preflight、Basic Preview、Public Demo、RAG ON／OFFおよびSleep／Wake確認へ進める。

## 2. Accepted Access and Corpus Boundary

### 2.1 Access Matrix

次の二つの公開Surfaceは、Access境界を共有せず、同じ公開Corpus Adapterだけを明示的に利用できる。

```text
Basic Preview:
  authentication = basic
  documentation_rag = eligible
  corpus = exact public 8 files
  default = off

Public Demo:
  authentication = none
  documentation_rag = eligible
  corpus = exact public 8 files
  default = off
```

Public Demoは起動Scriptの最初にBasic Credential三項目を除去する。Basic Previewは既存Credential、Stateful LifecycleおよびProcess Identityを維持する。Public DemoからBasic LifecycleのPID、Log、MarkerまたはLockを新たに参照する経路はない。

### 2.2 Explicit Public Corpus

Lightning Profile v2のCorpusは次の8件と完全一致する。

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

`ExplicitMarkdownDocumentSource`はこの8 Pathだけを候補化し、`rglob`を使用しない。Absolute Path、Traversal、Backslash、Line Break、Duplicate、Symlink、Root Escape、History、LosslessおよびAllowlist外をContractまたはSource境界で拒否する。

したがって、次はLightning RAG Corpusへ入らない。

```text
docs/project/**
docs/public/history/**
docs/**/history/**
docs/**/lossless/**
Allowlist外Markdown
Hidden／Temporary／Backup File
```

### 2.3 Default OFF and Lazy Build

Basic PreviewとPublic DemoはともにRAG Default OFFである。OFF RequestではManifest、File Read、Chunk、IndexおよびRetrievalを行わない。最初のON Requestでのみ8 PathのManifestを作り、Process-local In-memory Indexを構築する。Persistent Index、追加Model、Embedding DependencyまたはCross-process Cacheはない。

## 3. Current Public Corpus Readiness

現在のローカルProject RootをRead-onlyで確認した結果は次のとおりである。

```text
Expected:
  8

Present regular non-symlink files:
  3

Present:
  docs/public/overview_ja.md
  docs/public/concept_ja.md
  docs/public/roadmap_ja.md

Missing:
  docs/public/overview_en.md
  docs/public/concept_en.md
  docs/public/roadmap_en.md
  docs/public/technology_selection_ja.md
  docs/public/technology_selection_en.md
```

これはRepository実装の不合格ではない。実装担当Scopeでは公開文書の作成、翻訳または内容変更が禁止されており、RuntimeはPartial Corpusを`expected=8 present=N missing=8-N`とWarningで明示する。

ただし「公開可能な8文書をBasic／Publicの双方から参照する」という今回のManual Acceptanceを判定するには、ユーザーが別途用意した8文書をLightning Projectの上記Pathへ全件配置し、Preflightで`expected=8 present=8 missing=0`を確認することを前提とする。

## 4. Independent Verification

### 4.1 Artifact Integrity

Implementer Statusに記録された変更・追加Artifact 18件のAfter SHA-512を現在Fileと照合した。

```text
18／18:
  MATCH

Unchanged Baseline Artifact:
  3／3 MATCH
```

### 4.2 Automated Verification

同一Project Environmentから独立に再実行した。

```text
Focused Lightning／Documentation RAG／Web:
  178 passed
  55.57s

Repository Full Suite:
  430 passed
  3 deselected
  56.77s

Ruff Check:
  PASS

Ruff Format:
  PASS／122 files

Mypy:
  PASS／122 source files

JavaScript Syntax:
  PASS

Lightning Shell Syntax:
  PASS／3 scripts
```

Full Suiteの3 deselectedはReal-model系Markであり、Lightning実機GGUF Acceptanceは本Reviewでは行っていない。

## 5. Non-blocking Observation

### 5.1 Direct Web CLIのLinux Platform Observation

`margpa-web`のDocumentation RAG Platform Helperは、現在Linux x86_64を`linux-x86_64-container`として分類する。Lightningの正式起動経路である`basic_preview_service.sh`と`public_demo_service.sh`は、共通PreflightでLinux、x86_64およびContainer Evidenceを独立に検証してからWeb CLIを起動するため、今回のLightning Manual Acceptance、安全境界およびExternal Wake経路には影響しない。

一方、将来このv2 ProfileをLifecycle Scriptを通さずNative Linux、Home Serverまたは別Cloudへ直接再利用する場合は、実行環境の誤分類を避けるため、既存Execution Environment Detectorの再利用またはNative／Container Platform Key分離を検討する。

```text
Priority:
  LOW／FUTURE PORTABILITY HARDENING

Current Lightning impact:
  NONE

Current manual gate:
  NOT BLOCKED
```

## 6. Mutation Boundary

Review中にSource、Config、Test、Model、Current、Shared、Public、Stable Requirements、Architecture、Governance、ADR、Phase Index、既存History、Lightning、API Builder、URL、Port、Managed Secrets、Private Bootstrap、GitまたはGitHubを変更していない。

既存Web ProcessのStop、Restart、Model Load、Generation、Permission変更、File CopyまたはProject Root外操作も行っていない。

Append-onlyの本Review、ユーザー向けManual Acceptance HandoffおよびDocumentation Index Snapshotだけを新規追加する。

## 7. Next Gate

ユーザーがLightning上で次を手動実施する。

1. 公開8文書を確定Pathへ全件配置する。
2. 差し替えArtifactのSHA-512とPermissionを確認する。
3. Focused TestとPreflightを行う。
4. Basic PreviewでBasic認証、RAG Default OFF、RAG ON JA／EN、CitationおよびInternal Docs非参照を確認する。
5. Public Demoで認証なし、RAG Default OFF、RAG ON JA／EN、CitationおよびInternal Docs非参照を確認する。
6. 両SurfaceのSleep／Traffic-aware Wake後も同じ境界が再現することを確認する。

Manual Evidence受領後、設計統括者役はBasic PreviewとPublic Demoを分離してAcceptanceを判定する。
