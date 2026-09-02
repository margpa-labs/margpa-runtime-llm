# MARGPA Runtime LLM 技術選定 — Portfolio Edition

```yaml
document_type: public_technology_selection_portfolio_edition
document_state: current_portfolio_edition
language: ja
created_at: 2026-09-01
updated_at: 2026-09-01 19:03 JST
public_author: Nazuna Research
project: MARGPA Runtime LLM
source_document: docs/public/technology_selection_ja.md
related_roadmap: docs/public/roadmap_portfolio_edition_ja.md
current_phase: phase_9_1_in_progress_adjust
```

本書は、MARGPA Runtime LLMで採用している主要技術と選定理由を、採用・技術面談向けに整理した用途別文書である。全Decisionや内部仕様を置き換えるものではなく、通常版Technology Selectionと各Architecture Documentを正本とする。

## 1. Selection Principles

- Local-firstで開始し、Cloudや特定Vendorを必須条件にしない。
- Domainと外部Libraryを分離し、Model、Storage、Frontend、検索方式を交換可能にする。
- 実装状態、Candidate、Deferred、未採用を明確に区別する。
- Test、Digest、Evidence、MigrationおよびRollback可能性を重視する。
- 個人R&D／PoC／MVPとして、実証価値と保守可能性の釣り合いを取る。

## 2. Current Technology Stack

| 領域 | 採用技術 | 主な用途 |
|---|---|---|
| Language | Python 3.12〜3.13 | Runtime、Domain、Adapter、Backend、Test |
| Contract／Config | Pydantic／pydantic-settings | Validation、Immutable Data、Configuration |
| Local Inference | GGUF／llama.cpp／llama-cpp-python | Model Load、Streaming、停止、Role別推論 |
| Web Backend | FastAPI／Uvicorn | REST API、SSE、Local Control Surface |
| Web Frontend | React 19／TypeScript／Vite | Chat、Settings、Status、Evidence UI |
| Persistence | SQLite／JSON／Filesystem | Conversation、Citation、Run、Evidence |
| Retrieval | BM25 Baseline／HTML本文抽出 | Project Docs、Local Corpus、Manual Web Evidence |
| Backend Test | pytest | Unit、Integration、Contract、Regression |
| Frontend Test | Vitest／Testing Library | Component、State、Interaction、Regression |
| Static Analysis | Mypy／Ruff／TypeScript／ESLint | 型、Lint、Format、Build前検査 |
| Package／Build | uv／npm | Lock、Dependency、Frontend Build |
| Integrity | Canonical JSON／SHA-512 | Manifest、Revision、Digest、Evidence Identity |

## 3. Model Strategy

### Main Model

- Qwen3-4B GGUF Q4_K_MをMac LocalのCurrent Defaultとして使用する。
- 小型Modelの品質限界を前提に、Runtime、RAG、評価機構およびUIのBaselineとして扱う。
- DeepSeek系8B ModelはLocal Loadと切替を確認済みだが、回答品質の検証が未完了のためDefaultへ昇格していない。
- より大規模なModelはServer／Cloud Candidateとして分離し、Mac Localの必須要件にしない。

### Guard／Judge Model

- Qwen3Guard-Gen 0.6BはLocal Artifactを使った基本的な検知・拒否経路をUser Macで確認済みである。
- Selene 1 Mini 8BはLocal Loadまで成立したが、実評価経路とResource負荷に未解決事項があり調整中である。
- Main Modelによる自己評価は利用可能だが、出力形式と安定性の追加検証を必要とする。
- Seleneを修復対象として維持しつつ、Current Hardwareに適した軽量Judge Candidateも比較する。

## 4. Application Architecture

- BackendはDomain、Application、Port、Adapter、Web Entry Pointを分離する。
- Model、RAG、Guardrail、Judge、Repair、Agent、ToolおよびStorageを独立Componentとして扱う。
- FrontendはBackendの状態を表示し、UIだけでRuntime上の事実や権限を作らない。
- Conversation、Turn、Generation、Citation、Run、StepおよびEvidenceへ安定Identityを持たせる。
- 外部作用や重要操作には明示的な承認境界を設ける。

## 5. Data／Retrieval

- ConversationとCitationはSQLiteをServer側の正本として保存する。
- Project DocsとUser登録Documentを検索対象として分離する。
- 検索結果にはSource、Title、Path／URL、Digest等を保持する。
- Public URLはUserが指定した場合だけ取得し、外部Contentであることを画面へ明示する。
- Local CorpusのRevision更新後も、過去Turnが参照したEvidenceを維持する。
- General Web Search、Automatic Searchおよび外部Provider運用は後続Phaseで扱う。

## 6. Frontend／UX

- ReactとTypeScriptでChat、Sidebar、Settings、Archive、Model状態およびEvidence表示を構成する。
- SSEによる生成表示、停止、再生成、Copy、言語切替およびContext使用量表示を実装する。
- 通常ChatとAgent Foundationを同じ画面から切り替えられる。
- White／Dark Themeと日本語／英語UIを保持する。
- 大規模な情報再配置とResponsive最適化は後続の統合工程で扱う。

## 7. Quality and Operations

- 2,000件超のBackend Testと300件超のFrontend Testを継続運用している。
- Mypy、Ruff、TypeScript、ESLintおよびProduction Buildを検証工程へ含める。
- Fixture／Mock Testと実Model／User Mac Manualを分離し、片方だけで完成を主張しない。
- Recovery IndexとHandoffにより、長時間作業や担当Model変更後も途中状態を復元する。
- Source実装、Test、Review、Manual AcceptanceおよびPhase Closureを別Gateで管理する。

## 8. Deferred／Not Selected

| 技術／方式 | 現在の扱い | 判断理由 |
|---|---|---|
| MLX Runtime | 未採用 | 現行llama.cpp経路を先に安定化し、Backend比較を後続化 |
| vLLM／SGLang | 将来候補 | GPU Server／Cloud向けで、Mac Local Currentには不要 |
| LangChain／LangGraph | 未採用 | 現時点では明示的なDomain／Port Contractを優先 |
| Vector Database | Deferred | Current Corpus規模ではBM25 Baselineを優先し、必要時に比較 |
| Public Conversation Persistence | 未採用 | Privacy、Authentication、Retention、Costの設計が先 |
| Online Learning | 未採用 | User Conversationから暗黙にModel Weightを更新しない |

## 9. Current Status

Local Runtime、Persistent Chat、RAG／Citation、Manual Web Evidence、Security／Evaluation基盤およびAgent／Tool Foundationは実装済みである。現在はPhase 9-1として、専用Judge／Guard、意味評価、修正連携およびModel Lifecycleを実Modelで調整している。

詳細は[通常版Technology Selection](technology_selection_ja.md)、[Portfolio Roadmap](roadmap_portfolio_edition_ja.md)、[通常版Roadmap](roadmap_ja.md)を参照する。
