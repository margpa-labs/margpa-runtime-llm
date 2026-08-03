# Public Demo／RAG／Bilingual Docs／Git Sequence Decision

```yaml
event_id: public_demo_rag_bilingual_docs_and_git_sequence_decision
phase: phase_1_ex
status: accepted
created_at: 2026-07-26 17:53:18 JST
owner: 設計統括者役
```

## Accepted Decisions

- Lightning Auto-start Read-only Preflightを先行する。
- 合格した場合、Basic認証Previewと分離したPublic Demo基盤を前半で実装する。
- Public Demoは匿名Access、Rate Limit、Token上限、Cost保護、Tool／RAG／外部操作なしとする。
- Public Demo基盤を実装しても、匿名Public Access有効化は公開Docs、Git運用、SanitationおよびInitial Commit準備後とする。
- Mac限定簡易Documentation RAGはDocs再整理／Canonical／Public Docs作成後に実装する。
- Mac限定実装でも、将来Lightning、Home ServerまたはCloudへ展開可能なPort／Adapter Hookを予約する。
- `docs/project/current/`と`docs/public/`は日本語正本と英語派生版を作る。
- Phase、Shared、Historyおよび内部Operationsは日本語のみとする。
- Git運用設計はPhase 1-ex後半へ配置する。
- Initial Commit前にDocs全体の必要箇所を最終実装状態へ再編集する。

## Authorization Boundary

本Decisionは設計・文書化を確定する。Public Access変更、Git操作、Lightning設定変更または実装開始を単独で許可しない。
