# Lightning Public Corpus Documentation RAG Multi-access Architecture

```yaml
document_id: lightning_public_corpus_documentation_rag_multi_access_architecture
status: accepted_ready_for_implementation
language: ja
created_at: 2026-08-01 09:10:03 JST
owner: 設計統括者役
phase: phase_1_ex
implementation_authorized: true_with_accepted_handoff
requirements: ../requirements/lightning_public_corpus_documentation_rag_multi_access_requirements_ja.md
decision: ../adr/adr_0030_lightning_public_corpus_documentation_rag_multi_access_ja.md
supersedes: lightning_basic_preview_public_corpus_documentation_rag_adapter_hook_architecture
```

## 1. Goal

Authentication境界を保ったまま、Basic PreviewとPublic Demoの双方へ、同じ公開8文書だけを参照するDocumentation RAG AdapterをCompositionする。

```text
Lightning Public Corpus Profile
  ├─ Basic Preview Entry
  │    ├─ Basic authentication
  │    └─ RAG eligible
  └─ Public Demo Entry
       ├─ Authentication none
       └─ RAG eligible

Both Entries
  ↓ validated feature profile
Generic Documentation RAG Composition
  ↓
Explicit 8-file Public Corpus
  ↓
Existing Sparse RAG Core
```

## 2. Separation of Concerns

次を別状態として保持する。

```text
Access Mode:
  local／basic_preview／public_demo

Authentication:
  none／basic

RAG Capability:
  eligible／denied

Corpus Profile:
  Mac local aggregate／Lightning public explicit files

Adapter Availability:
  available／unavailable

User Requested State:
  off／on
```

Public Demoで認証がないことは、RAGを拒否する理由にも、内部Corpusを許可する理由にもならない。RAG可否とCorpusはFeature Profileが明示し、Access ProfileはそのCompatibilityを検証する。

## 3. Required Profile Graph

```text
Web Access Profile
  ├─ basic_preview.toml
  │    documentation_rag = eligible
  └─ public_demo.toml
       documentation_rag = eligible

Documentation RAG Feature Profile
  └─ lightning_public_documentation_rag.toml
       allowed_access_modes = [basic_preview, public_demo]
       allowed_platforms = [linux-x86_64-container]
       corpus = exact 8 files
```

BasicとPublicのために同内容のFeature Profileを複製しない。将来異なるCorpusが必要になった場合は別Profileを追加し、Access Compatibilityを明示する。

## 4. Web Access Contract Refactoring

現行`WebAccessProfile`はPublic DemoならDocumentation RAGが必ず`denied`であるというInvariantを持つ。これを削除し、次を独立検証する。

```text
Public Demo:
  authentication must be none
  non-loopback must be explicit
  documentation_rag may be eligible or denied by profile

Basic Preview:
  authentication must be basic
  non-loopback must be explicit
  documentation_rag may be eligible or denied by profile

Local:
  authentication none
  loopback only
```

未知値、Access ModeとAuthenticationの矛盾およびLocal Non-loopbackは引き続き拒否する。

## 5. Corpus Selection Architecture

### 5.1 Explicit Selection Plan

```text
ExplicitFileCorpusSelectionPlan
  files: tuple[ProjectRelativeMarkdownPath, ...]
  include_history: false
  include_lossless: false
```

`LocalMarkdownDocumentSource`または後継Sourceは、検証済みSelection Planだけを受け取る。LightningではRecursive Scanを行わない。

### 5.2 Path Validation

- POSIX Project-relative Path。
- `docs/public/`直下のAllowlist File。
- `.md`。
- Duplicateなし。
- Absolute／`..`／Backslash／Line Breakなし。
- Symlink Componentなし。
- Resolve後にProject Root内。
- Regular File、UTF-8、Size Limit内。

Missing FileはManifest Warning／Readinessへ記録する。存在するFileだけを別の完全Corpusへ自動変換しない。

## 6. Generic Builder

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

責務：

1. Defaults／Feature Schema検証。
2. Access Compatibility検証。
3. Platform Compatibility検証。
4. Corpus Selection Plan生成。
5. Source／Chunker／Index／Retriever／Assembler／Citation Composition。
6. Profile Digest生成。
7. Deferred Token Counter Binder提供。

既存`build_local_documentation_rag()`はCompatibility Wrapperとして残すか、既存APIとTestを壊さない形で移行する。

## 7. Entry Point Decision Order

```text
1. Resolve and validate Web Access Profile
2. Resolve RAG Capability
3. Resolve explicit Documentation RAG Feature Profile
4. Validate access compatibility
5. Validate platform compatibility
6. Build adapter if eligible and valid
7. Bind loaded-model token counter
8. Expose OFF／ON control according to availability
```

明示Profileがない場合：

```text
Local Mac:
  existing local default profile

Lightning Basic／Public:
  adapter unavailable unless service supplies tracked public profile
```

Browser RequestはProfileを選択しない。

## 8. Lightning Service Integration

### 8.1 Shared Resolver

Basic PreviewとPublic Demoは、共通Helperで次を検証する。

```text
MARGPA_DOCUMENTATION_RAG_PROFILE
  ↓ default tracked profile when unset
Project-root bounded regular TOML
  ↓
profile key／schema／access modes／platform／corpus contract
```

### 8.2 Basic Preview

既存Credential検証とRuntime State Lifecycleを維持し、Foreground `run`へRAG Profile Argumentを追加する。

### 8.3 Public Demo

既存Stateless Preflight、Credential ScrubおよびForeground `run`を維持し、同じRAG Profile Argumentを追加する。

Public Demoは次だけをScrubする。

```text
MARGPA_WEB_AUTH_MODE
MARGPA_WEB_AUTH_USERNAME
MARGPA_WEB_AUTH_PASSWORD
```

`MARGPA_DOCUMENTATION_RAG_PROFILE`はScrubしない。ただし検証前の値をそのままCommandへ渡さない。

## 9. Runtime Lifecycle

```text
Application Composition:
  adapter object only
  corpus not read

RAG OFF Request:
  no manifest／index／retrieval

First RAG ON:
  manifest
  allowlisted document read
  deterministic chunks
  in-memory index
  retrieve／assemble／cite

Same manifest:
  reuse

Manifest change:
  build replacement
  atomic replace after success

Process exit／sleep:
  discard index
```

BasicとPublicが別Processなら、それぞれ独立のIn-memory Indexを持つ。Cross-process Cacheは作らない。

## 10. Public Trust Boundary

Public Corpusは公開可能でも、Runtime上はReference Dataである。

```text
Document text:
  not system instruction
  not tool authority
  not policy authority

System citation:
  generated by citation adapter

Model citation:
  untrusted generated text
```

匿名Public利用者は、Query本文にPath、内部文書名またはOverride指示を書いても、Allowlist以外を検索できない。

## 11. Retrieval Quality Position

Mac第2回手動TestのKnown Limitationを継承する。

- Lexical HitはSemantic Sufficiencyを保証しない。
- Citationは全ClaimのEntailmentを保証しない。
- 小型Modelは略称、正式名称、関係またはRoadmap進捗を誤る可能性がある。

手動Hit Keyword／参照Indexは、Hard-codeと保守性問題のため採用しない。

将来検討候補：

```text
document-derived automatic signals
reproducible build-time metadata
query decomposition
language-aware ranking
semantic／hybrid adapter
claim-to-citation judge
governance／repair
model upgrade
```

本Architectureは将来方式を固定しない。

## 12. Failure Mapping

```text
invalid access profile:
  startup refusal

invalid／unsafe feature profile:
  startup refusal

incompatible feature profile:
  startup refusal

docs absent:
  unavailable safe message／model call zero

corpus empty:
  empty-corpus safe message／model call zero

partial subject coverage:
  subject_coverage_insufficient／model call zero

RAG OFF:
  ordinary chat／zero retrieval
```

## 13. Test Architecture

### Access Matrix

| Access | Auth | RAG Capability | Corpus |
|---|---|---|---|
| Local | None／Loopback | Eligible | Existing Mac |
| Basic Preview | Basic | Eligible | Public 8 files |
| Public Demo | None／Explicit | Eligible | Public 8 files |

### Security／Corpus

- Public Queryから`docs/project/**`取得0。
- History／Lossless取得0。
- Profile OverrideでRoot Escape不可。
- Credential値がPublic Process／Logに存在しない。
- Citationは8 Path内だけ。

### Regression

- Mac Local RAG。
- Basic authentication。
- Public anonymous access。
- Traffic-aware Wake。
- Summary、Stop、New Chat、Reload、Model Busy。
- RAG OFF Zero Call。

## 14. Implementation Slices

```text
Slice A:
  Access Profile capability change and tests

Slice B:
  Feature Profile v2／explicit corpus

Slice C:
  Generic composition／Mac compatibility

Slice D:
  Basic and Public service integration

Slice E:
  Corpus／access／conversation／lifecycle regression tests

Slice F:
  user manual acceptance handoff after designer review
```

## 15. Acceptance View

```text
Basic Preview
  ├─ Basic authentication
  ├─ Public 8-doc corpus
  ├─ Project Docs OFF／ON
  └─ Existing lifecycle

Public Demo
  ├─ No authentication
  ├─ Public 8-doc corpus
  ├─ Project Docs OFF／ON
  └─ Stateless public lifecycle

Neither
  ├─ Internal docs
  ├─ Persistent index
  ├─ Extra model
  └─ Tool／Agent／external I/O authority
```
