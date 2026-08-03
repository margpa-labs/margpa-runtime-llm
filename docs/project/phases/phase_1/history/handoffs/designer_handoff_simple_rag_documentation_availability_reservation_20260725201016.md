# Simple RAG Documentation Availability 実装担当予約Handoff

- 文書ID: `designer_handoff_simple_rag_documentation_availability_reservation`
- 状態: `accepted_reservation_not_authorized_for_implementation`
- 作成日時: `2026-07-25 20:10:16 JST`
- 更新日時: `2026-07-25 20:10:16 JST`
- Snapshot: `20260725201016`
- 作成担当: 設計者役担当Task
- 対象: 将来の実装者役担当Task
- 正本言語: 日本語
- Requirements: [simple_rag_documentation_availability_requirements_20260725201016.md](../requirements/simple_rag_documentation_availability_requirements_20260725201016.md)
- Accepted ADR: [adr_0023_simple_rag_missing_docs_explicit_unavailable_result_20260725201016.md](../adr/adr_0023_simple_rag_missing_docs_explicit_unavailable_result_20260725201016.md)
- supersedes: なし

## 1. Timing

本HandoffはPhase 1-ex完了後のSimple RAG実装に備えた予約文書である。現時点ではSource、Config、TestまたはDependencyを変更しない。

## 2. Locked Contract

```text
OFF:
  docs/ probeなし
  index loadなし
  retrievalなし
  model callなし

ON／明示利用＋docs/ missing:
  state=unavailable
  reason_code=docs_directory_missing
  Project説明の推測生成なし
  Application Crashなし
```

日本語表示：

```text
docs/が設置されていないため参照できません。
```

## 3. Deployment Policy

### Mac Local

Phase 1-ex後、Simple RAG本体を実装・有効化できる。ON時に`docs/`がなければ共通Unavailable Resultを返す。

### Lightning

当面はHook-only／Default OFFとする。`docs/`、Corpus、RetrieverまたはProviderを要求しない。将来ONにした場合だけAvailability Gateを通す。

## 4. Future Implementation Requirements

- Availability PortをRetriever実装から分離する。
- Logical Docs RootをConfigから解決する。
- Absolute Pathを利用者向けErrorへ出さない。
- Missing時にIndex／Retriever／Modelを呼ばない。
- UI／CLI／APIへ同じReason Codeを渡す。
- Audit Eventを発行可能にする。
- Missingから配置後の明示的Retryを可能にする。

## 5. Required Test after Authorization

- OFF／ON
- Mac／Lightning
- Missing／Present
- 日本語／英語
- Model Call非発生
- Path非露出
- Retry Recovery

## 6. Stop Condition

Phase 1-exが完了し、Public Canonical Corpus、Manifestおよび実装Scopeが承認されるまで着手しない。

