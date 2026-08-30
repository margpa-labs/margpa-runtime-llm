# Phase 7 Post-Manual Bounded Rework — Package P7-RW2-0 Recovery（Entry／Regression Freeze）

```yaml
document_id: phase_7_post_manual_bounded_rework_p7_rw2_0_recovery_20260830103000
document_type: package_recovery_index
document_state: final
language: ja
created_at: 2026-08-30 10:30:00 JST
active_contract: phase_7_claude_post_manual_citation_freshness_auto_resume_bounded_rework_exact_handoff_ja_20260830101851.md
package: P7-RW2-0
```

## 0. Recovery Index Pointer

先行Package: なし（本差分Taskの最初のPackage）。次Package: P7-RW2-A Recovery。

## 1. Digest照合

Mandatory Reading 8件を`shasum -a 512`で照合し、Handoff記載のExpected SHA-512と全件一致した。

```text
poc_mvp_portfolio_...operating_policy_ja.md                                     一致
phase_7_requirements_ja.md                                                       一致
phase_7_acceptance_matrix_ja.md                                                  一致
phase_7_claude_non_web_closure_alignment_exact_return_handoff_ja_20260829230500  一致
phase_7_codex_controller_non_web_closure_alignment_review_ja_20260829230354      一致
phase_7_local_corpus_data_controls_user_manual_test_sheet_controller_revision... 一致
phase_7_user_mac_local_corpus_data_controls_manual_acceptance_adjust_ja_...      一致
phase_8_manual_url_evidence_and_phase_11...lossless_scope_refinement_ja_...      一致
```

Handoff本体（`phase_7_claude_post_manual_citation_freshness_auto_resume_bounded_rework_exact_handoff_ja_20260830101851.md`）も事前にDigest照合済み（`f977711...02f1a6`）。

## 2. 再現経路の固定（限定Source読解）

P7-CODEX-007〜009それぞれについて、Source上の正確な原因箇所を固定した。

### P7-CODEX-007（Citation Projection Gap）

```text
DocumentationCitation（modules/documentation_rag/contracts.py）:
  chunk_id, document_sha512は既に保持（Phase 7当初から）。
  source_classは保持していない（今回追加対象）。
SystemCitationAdapter.build()（adapters/documentation_rag/system_citation_adapter.py）:
  DocumentationReferenceBlock.source_classを読み取り済みだが、
  DocumentationCitationへ渡していない。
PersistentCitationResponse（web/persistent_contracts.py）:
  project_relative_path, heading_breadcrumb, retrieval_score,
  selected_order, truncatedのみ。chunk_id/document_sha512/source_class欠落。
project_persistent_event()のRETRIEVAL分岐（web/persistent_streaming.py）:
  Live SSEも同じ5Fieldのみ投影、chunk_id/document_sha512/source_class欠落。
  ただしRaw Event Data自体（conversation_generation.py）は
  augmentation.citationsのmodel_dump(mode="json")全量を既に載せている
  ため、欠落はProjection層3箇所（Domain Contract、Persistent Contract、
  SSE Projection）に限定される。
Frontend Citation型（types.ts）:
  project_relative_path, heading_breadcrumbの2Fieldのみ。
  CitationsSection.tsxが実際に描画する箇所も同じ2Fieldのみ。
```

### P7-CODEX-008（Current Turn Freshness）

```text
ConversationGenerationSession（conversation_generation.py）:
  RAG Queryは常に最新Message一つだけを使う（既に正しい、Bug対象外）。
  Local Corpus Manifestも毎Turn再読込（既に正しい、Bug対象外）。
Main Model Promptの構築（_build_request/compose_conversation_generation_
messages）:
  過去Turnの文字列全体を無条件でHistoryとしてそのまま渡す
  （REFERENCE_INSTRUCTIONによる「過去回答はAuthorityでない」抑制は
  Reference Messageがある時だけ発火し、NO_HIT時は発火しない）。
NO_HIT状態（documentation_rag.py _enabled()）:
  should_generate=Trueのまま、reference_message=None、citations=()の
  ままModelへ進む。「現在の根拠なし」を明示するInstructionが存在しない。
BM25 Fallback Backfill（bm25_retriever.py）:
  Identifier対象Subjectが尽きた後、残りTop-k枠を無関係な高ScoreChunkで
  埋める。Query文が典型的なIdentifier形状で無い場合
  （query_analyzer.identifier_tokensが空）、identifier_subject_count=0
  となり、Subject Coverage Gateが実質不発のままGROUNDED_READYへ落ち、
  無関係なChunkがReference/Citationとして採用される。
```

### P7-CODEX-009（Manual Resume Required）

```text
recover_incomplete_conversations()（persistent_conversation_service.py）:
  起動時1回、非終端TurnまたはActive SessionをInterruptedへ遷移するのみ
  （新規Resumeは行わない、意図通り、変更しない）。
append_user_turn()のGate（persistent_conversation_service.py）:
  Active Sessionがちょうど1件でなければinvalid_lifecycleで拒否。
  Restart後やUnarchive直後はActive Session 0件のため、ここで拒否される。
set_archived(archived=False)（persistent_conversation_service.py）:
  Conversation StateをACTIVEへ戻すだけでSessionには触れない
  （Archive時にForce-CloseされたままSession 0件で復帰）。
Frontend ChatListItem.tsx:
  item.state === "active" && !item.has_active_sessionの時だけ
  「再開」Actionを表示し、手動Clickでresume_conversation()を呼ぶ
  以外に経路がない。
```

## 3. Baseline再確認

Package 0〜IおよびP7-NW-0〜Eの既存成果物へは触れていない。Frozen Requirements／Acceptance Matrixも無改変。

## 4. Temporary使用

Project内Task-owned Temporary（本Docs作成のみ）。追加Process起動なし。

## 5. Action Inventory

```text
Git Action: 0
Network Action: 0
Source／Test Mutation: 0（本Packageは調査のみ）
Root外Read/Write: 0
```

Exact next action: P7-RW2-A（Citation Identity Projection）へ連結して進む。
