# ADR-0023 Simple RAG Missing Docs Explicit Unavailable Result

- 文書ID: `adr_0023_simple_rag_missing_docs_explicit_unavailable_result`
- 状態: `accepted`
- 作成日時: `2026-07-25 20:10:16 JST`
- 更新日時: `2026-07-25 20:10:16 JST`
- Snapshot: `20260725201016`
- 作成担当: 設計者役担当Task
- Decision Owner: ユーザー
- 正本言語: 日本語
- Requirements: [simple_rag_documentation_availability_requirements_20260725201016.md](../requirements/simple_rag_documentation_availability_requirements_20260725201016.md)
- supersedes: なし

## 1. Decision

Simple RAG／Project Documentation Explainerを明示利用した時に`docs/`が存在しない場合、推測回答やApplication Crashではなく、構造化されたUnavailable Resultを返す。

```text
state       : unavailable
reason_code : docs_directory_missing
message_ja  : docs/が設置されていないため参照できません。
```

## 2. OFF Semantics

ComponentがOFFの場合は`docs/`を探索しない。Lightning Hook-only Profileを含め、`docs/`不存在をStartup Errorにしない。

## 3. Rationale

- LocalとCloudで同じFailure Contractを維持できる。
- Project Docsを参照した回答と、Modelの一般知識による推測を混同しない。
- Optional Componentの不存在がCore Runtimeを壊さない。
- UI、CLI、API、Auditが表示文言ではなくReason Codeで処理できる。

## 4. Consequences

- Corpus Availability Gateが必要になる。
- Missing、Empty、Unreadable、Manifest Missing等の分類が必要になる可能性がある。
- OFF時とUnavailable時を別状態として扱う。
- RAG実装と同時に自動Testを追加する。

## 5. Implementation Timing

実装はPhase 1-ex完了後のSimple RAG Handoffで行う。本ADRは現時点のRAG実装を許可しない。

