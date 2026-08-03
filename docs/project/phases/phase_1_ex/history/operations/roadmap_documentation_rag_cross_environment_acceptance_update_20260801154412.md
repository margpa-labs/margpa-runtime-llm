# Roadmap Documentation RAG Cross-environment Acceptance更新記録

```yaml
document_id: roadmap_documentation_rag_cross_environment_acceptance_update
phase: phase_1_ex
status: completed
language: ja
created_at: 2026-08-01 15:44:12 JST
owner: 設計統括者役
```

## 1. Scope

ユーザーの明示指示に基づき、`docs/public/roadmap_ja.md`だけをPublic Stable文書の更新対象とした。Overview、Concept、README、Current、Project Continuity、他Shared Stableまたは英語版の全面再整理は行っていない。

Runtime Deployment Snapshot運用方針は、今回の復旧から得られた今後のCross-environment Deploymentに必要な関連運用文書として新規作成した。

## 2. Normal History Procedure

```text
Before Snapshot:
  docs/public/history/roadmap/roadmap_phase_1_ex_before_documentation_rag_cross_environment_acceptance_ja_20260801154412.md

Stable:
  docs/public/roadmap_ja.md

After Snapshot:
  docs/public/history/roadmap/roadmap_phase_1_ex_after_documentation_rag_cross_environment_acceptance_ja_20260801154412.md
```

Before Snapshotは更新前StableとSHA-512一致、After Snapshotは更新後StableとSHA-512一致する。

## 3. Updated Facts

- Gitを使用しないGitHub直接掲載は完了した。
- Basic認証Previewと分離した認証なしPublic Demo Surfaceは成立した。
- Traffic-aware Auto-startはBasic／Publicの双方で成立した。
- Mac Local Documentation RAGは機能Acceptance済みである。
- Lightning Basic PreviewとPublic Demoは公開8文書RAGを利用できる。
- 全RAG ProfileはDefault OFFである。
- 回答品質、Semantic GroundingおよびRetriever Tuningは既知の後続課題である。
- Phase 1-exの次工程はGit運用設計である。

## 4. Integrity

```text
Roadmap Before:
  7ef57196d6c0a4c02ecdb26bc22484c4e0fe345e72795a9f546b0fbba34bc6aba9d29682c4c9b58859e3127519b8ed19bd16e61a96504f44d792ca18de864884

Roadmap After:
  f8e0c05ef74e5bcea8db28984c0dd25938ea8634716d94be5b03c8ad656c320607d919d814e32297ab47add2a1039c376cb3d69ebd57e7bc739a5772c307cec4
```

旧Snapshotまたは既存Roadmap Historyは変更・削除していない。

## 5. Deferred Documentation Work

次はPhase 1-ex終盤のDocs再整理で扱う。

- READMEと公開入口の現行State同期
- Overview／Concept等の必要箇所更新
- Current／Shared／Public英語派生版の再判断
- Phase 1-ex Final Lossless
- Design Governance Recovery更新
- Project Continuity最終反映

本更新だけをDocs全体同期完了とみなさない。
