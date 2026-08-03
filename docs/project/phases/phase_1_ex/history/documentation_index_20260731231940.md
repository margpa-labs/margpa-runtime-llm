# Phase 1-ex Documentation Index Snapshot

```yaml
document_id: phase_1_ex_documentation_index_snapshot
snapshot: 20260731231940
state_at: 2026-07-31 23:19:40 JST
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
  - handoffs/implementer_status_phase_1_ex_mac_local_documentation_rag_retrieval_acceptance_follow_up_20260731220726.md
  - handoffs/designer_review_phase_1_ex_mac_local_documentation_rag_retrieval_acceptance_follow_up_20260731222302.md
  - handoffs/user_handoff_phase_1_ex_mac_local_documentation_rag_manual_acceptance_20260731222302.md
  - operations/mac_local_documentation_rag_manual_test_1_findings_20260731231940.md
  - handoffs/designer_review_phase_1_ex_mac_local_documentation_rag_manual_test_1_20260731231940.md
  - requirements/mac_local_documentation_rag_multi_turn_grounding_follow_up_requirements_20260731231940.md
  - architecture/mac_local_documentation_rag_multi_turn_grounding_follow_up_architecture_20260731231940.md
  - handoffs/implementer_handoff_phase_1_ex_mac_local_documentation_rag_multi_turn_grounding_follow_up_20260731231940.md
supersedes: documentation_index_20260731222302.md
source: mac_local_documentation_rag_manual_test_1_and_multi_turn_grounding_follow_up
```

本Snapshotは[2026-07-31 22:23:02版](documentation_index_20260731222302.md)までの全状態を継承し、1回目の実GGUF／Browser手動Test Evidence、設計統括者Review、修正要件、修正Architectureおよび実装担当HandoffをAppend-onlyで追加する。

旧Review、旧Manual Acceptance Handoffおよび旧Indexは当時の判断を示すHistoryとして保持する。旧文書へ追記、修正または削除は行わない。現在のGateとAuthorityは本Indexおよび新しいReviewを正とする。

Accepted Requirements、Technology Selection、Architecture、ADR-0028およびPhase Index Stableは変更していない。

## Manual Test 1 Evidence

- [1回目手動Testの結果から得られた知見](operations/mac_local_documentation_rag_manual_test_1_findings_20260731231940.md)

確認された状態：

```text
Documentation RAG:
  全報告TurnでON

Component Installation:
  IMPLEMENTED

Single-turn Retrieval:
  WORKING／ADJUSTMENT_REQUIRED

Multi-turn Grounding:
  FAILED

Observed Failure:
  1回目は参照を取得する一方、長い回答後の後続Turnで参照が組み立てられず、
  Project固有用語を無根拠に生成する
```

本結果はDocumentation RAGの搭載失敗を意味しない。Retrieval、CitationおよびUIまでの構造は成立している。一方、Token計測、Context Budget、Fail-closed、複数Subject CoverageおよびGroundingの境界がManual Acceptance水準へ達していない。

## Designer Review

- [Manual Test 1 設計統括者Review](handoffs/designer_review_phase_1_ex_mac_local_documentation_rag_manual_test_1_20260731231940.md)

```text
Previous Manual Acceptance GO:
  SUPERSEDED BY ACTUAL MANUAL EVIDENCE

Current Manual Acceptance Gate:
  NO_GO

Further Implementation Follow-up:
  REQUIRED／AUTHORIZED
```

旧Retrieval Acceptance Reviewが許可した「手動確認へ進むこと」と、実手動確認後の最終受入を区別する。実手動確認でF8～F12が確認されたため、Mac限定簡易Documentation RAGの最終Acceptanceは行わない。

## Follow-up Design

- [Multi-turn Grounding Safety Follow-up 要件](requirements/mac_local_documentation_rag_multi_turn_grounding_follow_up_requirements_20260731231940.md)
- [Multi-turn Grounding Safety Follow-up Architecture](architecture/mac_local_documentation_rag_multi_turn_grounding_follow_up_architecture_20260731231940.md)

修正対象：

```text
F8:
  UTF-8 Byte数によるPrompt Token推定を、BackendのChat Template／Tokenizerに基づく実測へ置換

F9:
  Retrieval Hit後に有効なReference Blockを組み立てられない場合のFail-openを禁止

F10:
  複数High-signal Identifier QueryのSubject Coverageを追加

F11:
  Citationの存在と回答の忠実性を分離し、過去Assistant回答を根拠にしないGrounding Contractを追加

F12:
  No Hit、Context不足、UnavailableおよびDeniedをUI／Evidenceで区別
```

## Implementer Handoff

- [実装担当向け Multi-turn Grounding Safety Follow-up Handoff](handoffs/implementer_handoff_phase_1_ex_mac_local_documentation_rag_multi_turn_grounding_follow_up_20260731231940.md)

```text
Handoff State:
  ACCEPTED／READY_FOR_IMPLEMENTATION

Implementation Owner:
  実装者役

Manual Retest:
  BLOCKED UNTIL IMPLEMENTATION STATUS AND DESIGNER RE-REVIEW
```

## Architecture Boundary

今回のFollow-upはARGD、DAGD、JudgeまたはRepairを先行実装しない。Main Model単体のBaselineで、取得したEvidenceをPromptへ正しく供給し、供給不能時にRAG回答を装わない境界を先に成立させる。

本Manual Testは、将来の比較実験における重要なBaselineである。ARGD／DAGD追加後は、同一Input、Model、Seed、Context、DocsおよびGeneration設定を可能な限り固定し、Governance OFF／observe／enforceの差分として評価する。

## Integrity

```text
Previous Documentation Index:
  74bbf502f84f80d1d8a8958478672ef5079638f58107c61c2c1b5f71dc0bc494bab98831d2445a86438b20cb2fbb4a75d8f44984857c403d57bb54aebb436a9a

Phase Index Stable／Unchanged:
  67fff441677412c4e5e2aec2f951b597247ad5ee797497ba564d913eef58dec211237bbdb2a5d6adb5facfa829f662cd423a3a5023ea7c9d164458ba40c0478e

Manual Test 1 Findings:
  f1f9c885613d44bb25fd4066e7db4e4a902551bd79bb84889e1ff160087e8c795e75c49f3807edb52650b15465c72cec89f4b943025e1da3a905dd9cbac29c46

Designer Manual Review:
  0ed7da6409423be069a46cc18b92533472f1ca8f19ef10df1b0452b7c0abcc600be455812118f4813b7de3b1c73da487115af84c76f82858b2b134bb9ba75027

Follow-up Requirements:
  90ed078742bd7d8e547d7b1741cf1c4413bb13d9a9d34887cfe3fe50498e1f55561dc62ce5bb56bb618d6fae78a6746fc29287b374bb000d4b932520968fdc6a

Follow-up Architecture:
  fd7cd235ae0ed277db7611728f67e0bc9be89b0a4b93b47909ddf2b86eea92dc97adc60afb1001edd7a1ca6c16f1f5fc3d760b7a3f65eb9d109ecaba62199b1a

Implementer Handoff:
  2de4bf31534d49b003c40e499d175d6a95a150b3fe842c1ee7b0ba581e3f8b38c369681379b2f6ac7ec4b13aebebf37ef9f54c58256b253faef34f209c86d6ff
```

## Authority Boundary

```text
Follow-up Implementation:
  AUTHORIZED FOR IMPLEMENTER ROLE

Designer Source Mutation:
  DENIED／NOT_PERFORMED

Current／Shared／Public Docs Mutation:
  DENIED／NOT_PERFORMED

Phase Index Mutation:
  DENIED／NOT_PERFORMED

Model／GGUF Mutation:
  DENIED／NOT_PERFORMED

Lightning／Public Demo Documentation RAG:
  DENIED／OUT_OF_SCOPE
```

## Next Gate

実装者役がHandoffに従ってF8～F12を修正し、実装者StatusをAppend-onlyで提出する。

設計統括者役はSource、Test、Static CheckおよびStatusをReviewする。Review通過後にのみ、同一の実GGUF／Browser Manual Testを再開する。
