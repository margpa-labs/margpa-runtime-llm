# Phase 8 Post-MR8 Manual Deferred Work — Phase 9／10／11 Routing予約

```yaml
document_id: phase_8_post_mr8_manual_deferred_phase_9_10_11_routing_reservation_20260831181553
document_type: append_only_planned_work_routing_reservation
document_state: reserved_not_started
language: ja
recorded_at: 2026-08-31 18:15:53 JST
decision_authority: user
implementation_authorized: false
source_evidence: ../../../phases/phase_8/history/operations/phase_8_user_mac_post_mr8_full_manual_acceptance_and_behavior_evidence_ja_20260831181553.md
```

## 1. Current Phase 8最終Rework

Phase 8 Closure前に直すのは次の4件だけとする。

1. Completion GateのCurrent Reasonを`completion`として表示する。
2. Chat切替／新規Chat／成功Turnで、過去Web Failure警告をCurrent Composerから消す。
3. `Untrusted External Content`の文字色を統一する。
4. `新しいDemo Runを開始`を既存Primary Button Styleへ統一する。

## 2. Phase 9

- Manual URL Fail-closed時のMain Model Call 0を含むTurn Execution Trace／Observability。
- 無関係Project DocsのFalse-positive Retrieval／Grounding。
- 削除／更新済みSource FactとHistorical Conversation ContextのFreshness Governance。
- Strict NO_HIT、Semantic GD、Judge、Repair、Rejudgeの比較。
- Source Authority／ProvenanceとCorrection Acceptance／Belief Revision Successの実験設計。

## 3. Phase 10 UI

- Settings Manual URL結果のClear／Close／Reopen Lifecycle。
- Manual URL成功／失敗CardのTitle／URL／Failure表示整理。
- 専用URL欄を通常Composer URL貼付へ統合する最終UX。
- Archive専用Manage ModalとSettings情報整理。
- Web／Local／Project Docs／JSON／Markdown等のSource詳細を右Panelへ移す既存予約との統合。

## 4. Phase 11以降 Web Ingestion

- Shift_JIS／x-sjisその他Charset検出とDecode。
- `content_type_unsupported`から`charset_unsupported／decode_failed`等へのFailure Taxonomy分離。
- Full Readability／Normalizer／Chunking／Relevance Selection／Budgeted Injection。
- Hostile Content／Prompt Injection／Attack Site Hardening。
- 実Keyword Search Provider、Automatic SearchおよびProvider Account／Token／Self-hosted境界。

## 5. Non-goal

本予約はSource実装、Network、Model Load、Git、Phase 8 ClosureまたはPhase 9開始のAuthorityを与えない。
