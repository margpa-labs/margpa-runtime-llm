# Phase 1-ex Documentation Index Snapshot

```yaml
document_id: phase_1_ex_documentation_index_snapshot
snapshot: 20260731193204
state_at: 2026-07-31 19:32:04 JST
status: current_snapshot
snapshot_of:
  - ../phase_index_ja.md
  - ../requirements/mac_local_documentation_rag_requirements_ja.md
  - ../architecture/mac_local_documentation_rag_technology_selection_ja.md
  - ../architecture/mac_local_documentation_rag_architecture_ja.md
  - ../adr/adr_0028_mac_local_sparse_documentation_rag_and_external_adapter_hook_ja.md
  - handoffs/implementer_handoff_phase_1_ex_mac_local_documentation_rag_20260731172259.md
  - handoffs/implementer_status_phase_1_ex_mac_local_documentation_rag_20260731174758.md
  - handoffs/designer_review_phase_1_ex_mac_local_documentation_rag_20260731184134.md
  - handoffs/implementer_handoff_phase_1_ex_mac_local_documentation_rag_correctness_follow_up_20260731184134.md
  - handoffs/implementer_status_phase_1_ex_mac_local_documentation_rag_correctness_follow_up_20260731191521.md
  - handoffs/designer_review_phase_1_ex_mac_local_documentation_rag_correctness_follow_up_20260731193204.md
  - handoffs/implementer_handoff_phase_1_ex_mac_local_documentation_rag_context_fallback_follow_up_20260731193204.md
supersedes: documentation_index_20260731184134.md
source: mac_local_documentation_rag_correctness_re_review_and_context_fallback_follow_up
```

本Snapshotは[2026-07-31 18:41:34版](documentation_index_20260731184134.md)までの全状態を継承する。

Correctness Follow-up実装者Status、設計統括者再ReviewおよびContext Fallback限定Follow-up HandoffをAppend-onlyで追加した。

Accepted Requirements、Technology Selection、Architecture、ADR-0028およびPhase Index Stableは変更していない。

## Review Result

```text
F1／BM25 Document Frequency:
  RESOLVED

F2／Dynamic Request Context Budget:
  PARTIALLY RESOLVED
  dynamic formula and safety are connected
  production fallback remains blocking

F3／Empty Valid Corpus:
  RESOLVED

F4／Local Mac Host Eligibility:
  RESOLVED

Automated Regression:
  GREEN

Manual Local GGUF／Browser Acceptance:
  NO_GO

Next Implementation:
  CONTEXT FALLBACK FOLLOW-UP AUTHORIZED
```

## Reviewed Implementer Status

- [Mac限定簡易Documentation RAG Correctness Follow-up実装者Status](handoffs/implementer_status_phase_1_ex_mac_local_documentation_rag_correctness_follow_up_20260731191521.md)

## Designer Re-review

- [Mac限定簡易Documentation RAG Correctness Follow-up Review](handoffs/designer_review_phase_1_ex_mac_local_documentation_rag_correctness_follow_up_20260731193204.md)

再Reviewでは、F1、F3およびF4の解消を確認した。F2もRequest単位の動的Budget式、Safety MarginおよびHost Runtime Contextとの接続まで確認した。

残存Finding：

```text
configured fallback:
  2,400 characters

production fallback:
  min(2,400 characters, 768 tokens)
  then measured as 768 UTF-8 bytes

effect:
  normal Japanese reference chunks can all be dropped
  architecture／ARGD-DAGD／EASA／DLAGSA／OCILNS queries can produce zero citations
```

Local Qwen3 Tokenizerによる読み取り専用比較では、同じ取得結果が768 Token内に収まることを確認した。検索結果または設定Token上限ではなく、Fallback単位の不整合が原因である。

## Accepted Follow-up Handoff

- [Mac限定簡易Documentation RAG Context Fallback Follow-up Handoff](handoffs/implementer_handoff_phase_1_ex_mac_local_documentation_rag_context_fallback_follow_up_20260731193204.md)

Follow-upは次だけに限定する。

```text
Token／Character／UTF-8 Byte unit coherence
already-loaded backend token counter hook or equivalent safe fallback
realistic Japanese reference fixture
required question category citation survival
dynamic context safety preservation
```

Retriever Algorithm、Corpus Scope、Embedding、Persistent Index、Public Demo RAGおよびLightning RAGは対象外である。

## Verification Evidence

```text
Specified Target Suite:
  102 passed in 1.39s

Repository Full Suite:
  371 passed
  3 deselected
  49.43s

Ruff Check:
  PASS

Ruff Format:
  PASS／119 files

Mypy:
  PASS／119 source files

JavaScript Syntax:
  PASS

BM25 Reproduction:
  population 2／df(test) 1／selected 1

Production Fallback Real-corpus Smoke:
  project overview: citation available
  roadmap progress: citation available
  architecture: zero citation
  ARGD／DAGD: zero citation
  EASA: zero citation
  DLAGSA: zero citation
  OCILNS: zero citation

Exact Token Counter Comparison:
  all above query categories fit within 768 tokens
```

実Model生成およびBrowser Manual Acceptanceは未実施であり、Pass扱いしない。

## Integrity

```text
Previous Documentation Index:
  8fcb2de7a686736c4431d015a2683116d2b3ecb05128e36acd3ae84246e5868aae08729e4405d01b13c101ce5fcb30938532f5137104ad8300fac3a0c8e2034b

Phase Index Stable／Unchanged:
  67fff441677412c4e5e2aec2f951b597247ad5ee797497ba564d913eef58dec211237bbdb2a5d6adb5facfa829f662cd423a3a5023ea7c9d164458ba40c0478e

Correctness Follow-up Implementer Status:
  9d76d31b0235aa00d56f73c599d3ce33602d501ccccbd201e3fce2237a7804529a516ef9996208f8991c782282b6ac273d6d93af41b734e3ad0a828b78ab0669

Designer Re-review:
  62cb8117e949b508f0cab25dc89c1d1727486961fc81d7043da5de344d3f59b64e92ffaff1012d03de33d1029df01fc74dce99a2ee980df1e35ec11c968909ce

Context Fallback Follow-up Handoff:
  6d91ac0db812f29867a9e4f144b24c6c18059bceb7ddcd27652b2ecf526e4d9cdc65625f394908aed1da5644b965c976ce8b7a5b492e0c30210f649d41343087
```

## Authority Boundary

```text
Implement Context Fallback Follow-up:
  AUTHORIZED

Manual GGUF／Browser Acceptance:
  DENIED UNTIL RE-REVIEW

New Dependency／Model／Embedding／Persistent Index:
  DENIED

Retriever／Corpus Redesign:
  DENIED

Lightning／Public Demo RAG:
  DENIED

Git／GitHub／Project Root Outside Operation:
  DENIED
```

## Next Gate

実装担当はContext Fallback Follow-up Handoffに従い、新しいAppend-only Statusを提出する。

設計統括者役が単位整合、実用長日本語Reference、必須質問区分、Context Safetyおよび全Regressionを再Reviewし、Manual Acceptance GOを明示するまで、ユーザーのLocal GGUF／Browser試験へ進まない。
