# Phase 1-ex Documentation Index Snapshot

```yaml
document_id: phase_1_ex_documentation_index_snapshot
snapshot: 20260731214639
state_at: 2026-07-31 21:46:39 JST
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
  - handoffs/implementer_status_phase_1_ex_mac_local_documentation_rag_context_fallback_follow_up_20260731212414.md
  - handoffs/designer_review_phase_1_ex_mac_local_documentation_rag_context_fallback_follow_up_20260731214639.md
  - handoffs/implementer_handoff_phase_1_ex_mac_local_documentation_rag_retrieval_acceptance_follow_up_20260731214639.md
supersedes: documentation_index_20260731193204.md
source: mac_local_documentation_rag_context_fallback_re_review_and_retrieval_acceptance_follow_up
```

本Snapshotは[2026-07-31 19:32:04版](documentation_index_20260731193204.md)までの全状態を継承する。

Context Fallback実装者Status、設計統括者再ReviewおよびRetrieval Acceptance Follow-up HandoffをAppend-onlyで追加した。

Accepted Requirements、Technology Selection、Architecture、ADR-0028およびPhase Index Stableは変更していない。

## Review Result

```text
Previous F1／BM25 DF:
  RESOLVED

Previous F2／Dynamic Context and Fallback Units:
  RESOLVED

Previous F3／Empty Valid Corpus:
  RESOLVED

Previous F4／Local Mac Eligibility:
  RESOLVED

New F5／Natural-language Retrieval Relevance:
  CHANGES REQUIRED／BLOCKING

New F6／R&D Fixture Semantic Integrity:
  CHANGES REQUIRED

New F7／Measurement Evidence Units:
  CHANGES REQUIRED

Automated Regression:
  GREEN

Manual Local GGUF／Browser Acceptance:
  NO_GO

Next Implementation:
  RETRIEVAL ACCEPTANCE FOLLOW-UP AUTHORIZED
```

## Reviewed Implementer Status

- [Mac限定簡易Documentation RAG Context Fallback実装者Status](handoffs/implementer_status_phase_1_ex_mac_local_documentation_rag_context_fallback_follow_up_20260731212414.md)

## Designer Re-review

- [Mac限定簡易Documentation RAG Context Fallback Review](handoffs/designer_review_phase_1_ex_mac_local_documentation_rag_context_fallback_follow_up_20260731214639.md)

Context FallbackのToken／Character／UTF-8 Byte単位分離、Load済みMain Tokenizer Binding、Dynamic Safetyおよび768 Token上限はAcceptedとした。

実Project Corpusでは全7質問区分でReferenceが768 Token内へ収まった。一方、自然な日本語質問のRetrieval RelevanceがAccepted Manual Acceptanceを満たさない。

```text
roadmapの現在の進捗を教えてください:
  Roadmapを取得せず、Phase 1-D Language Smoke／Japanese Instructionだけを取得

ARGDとDAGDについて説明してください:
  ARGD／DAGD定義を取得せず、Roadmap変更規則／旧Documentation Snapshot断片を取得

short identifier query:
  roadmap／ARGD DAGD／DLAGSA／OCILNSは正本を取得
```

Corpus不足ではなく、自然文中の丁寧表現N-gramが高Signal Identifierを埋没させるQuery Analysis／Weighting問題である。

## Additional Required Findings

```text
F6:
  Functional Fixture内のARGD／DAGD、EASA、DLAGSA、OCILNS説明がCanonical定義と異なる。

F7:
  Character Fallback時にもBlock.estimated_tokensへCharacter数を格納する。
  Counter未設定時のFallback使用状態も一意に記録されない。
```

## Accepted Follow-up Handoff

- [Mac限定簡易Documentation RAG Retrieval Acceptance Follow-up Handoff](handoffs/implementer_handoff_phase_1_ex_mac_local_documentation_rag_retrieval_acceptance_follow_up_20260731214639.md)

Follow-upは次に限定する。

```text
generic natural-language query signal handling
no domain acronym hard-code
noisy-corpus ranking fixtures
real-corpus read-only retrieval smoke
canonical R&D fixture meanings
truthful measurement-unit evidence
```

Embedding、New Dependency、Corpus Scope、Persistent Index、Public Demo RAGおよびLightning RAGは対象外である。

## Verification Evidence

```text
Combined Target Suite:
  256 passed in 3.72s

Repository Full Suite:
  386 passed
  3 deselected
  49.61s

Ruff Check:
  PASS

Ruff Format:
  PASS／119 files

Mypy:
  PASS／119 source files

JavaScript Syntax:
  PASS

Real Corpus Exact-token Smoke:
  Project overview 615／768
  Roadmap progress 621／768
  Architecture 678／768
  ARGD／DAGD 649／768
  EASA 743／768
  DLAGSA 590／768
  OCILNS 574／768
```

実Model生成およびBrowser Manual Acceptanceは未実施であり、Pass扱いしない。

## Integrity

```text
Previous Documentation Index:
  7031e82948644e6aa47ea05bc772f40993e2dc0dabf68f09c61c35135bae91e98b41987ce08339314972f5cdf0b61a081557aacb3caf4622cb79ffc70726b16d

Phase Index Stable／Unchanged:
  67fff441677412c4e5e2aec2f951b597247ad5ee797497ba564d913eef58dec211237bbdb2a5d6adb5facfa829f662cd423a3a5023ea7c9d164458ba40c0478e

Context Fallback Implementer Status:
  4020ec9d45a46fc16e6c081985b058f7ac063a6b42c772955fc9a94c8e925f3a99662b59053327ac1b0fa4cac120757c707084344b45fb909285d81381c08b65

Designer Re-review:
  70aea50da64f0219300b9106a2c409178650af90ba43fa5a7d1b6d5bf4a96dbfea90a1115cc6efda3f907d137d17cb4fd8cd4bd72bdf61685c05149385cce505

Retrieval Acceptance Follow-up Handoff:
  5005b54449b441e90b89cf50d085a5fe2df4da1974ecc2d8db496d51f9d518d52ca6e34d5eca9d6b61aa255b509020815d15cc61971d44c764819a110a0960b9
```

## Authority Boundary

```text
Implement Retrieval Acceptance Follow-up:
  AUTHORIZED

Manual GGUF／Browser Acceptance:
  DENIED UNTIL RE-REVIEW

New Dependency／Model／Embedding／Persistent Index:
  DENIED

Domain Acronym Hard-code／Corpus Expansion:
  DENIED

Lightning／Public Demo RAG:
  DENIED

Git／GitHub／Project Root Outside Operation:
  DENIED
```

## Next Gate

実装担当はRetrieval Acceptance Follow-up Handoffに従い、新しいAppend-only Statusを提出する。

設計統括者役が自然文Query Relevance、固有研究名称の意味保全、計測単位Evidence、Context Safetyおよび全Regressionを再Reviewし、Manual Acceptance GOを明示するまで、ユーザーのLocal GGUF／Browser試験へ進まない。
