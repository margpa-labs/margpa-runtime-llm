# Phase 7 削除後NO_HIT Stale Code防止・最小Rework — Exact Return Handoff

```yaml
document_id: phase_7_claude_no_hit_stale_code_prevention_bounded_rework_exact_return_handoff_20260830143000
document_type: exact_differential_execution_return_handoff
document_state: final
language: ja
created_at: 2026-08-30 14:30:00 JST
provider: Claude
role: 設計者兼実装者役
task_identity: current_claude_task
phase: phase_7
execution_scope: P7-RW4
active_contract: docs/project/phases/phase_7/history/operations/phase_7_codex_controller_p7_rw3_rag_grounding_citation_ui_independent_review_ja_20260830132855.md
active_contract_sha512: b479ed17ac3e6d05d75ebd689c1422d811001fe1d90384aed5fcade2a732e40e115210e51d89427befe1d1d4b2da3ebf7880e28c8a5805c28dff09e38fd27d73
maximum_claim: COMPLETE_CANDIDATE_FOR_CONTROLLER_REVIEW
phase_7_closure_authority: false
phase_8_authority: false
git_authority: false
```

## 1. Digest照合

対象Controller Review（正本）の実File SHA-512を`shasum -a 512`で照合し、上記`active_contract_sha512`と一致を確認した。

## 2. Package Recovery Index

```text
P7-RW4（削除後NO_HIT Stale Code防止、P7-CODEX-013残り1経路）:
  docs/project/phases/phase_7/history/index/phase_7_no_hit_stale_code_prevention_p7_rw4_final_recovery_ja_20260830142000.md
  SHA-512:
  550e63703aa766c3758cc75417a0199d719d97f03841d30ae16c5d7931555ef602ea20a42aa3f7ad4fdb206c429ebb6a48c87cdf6f8e2d583f4fc2318a8f01f3
```

## 3. Finding解決状況

### P7-CODEX-013 — Partial Identifier Overlap Produces False Grounding（残り1経路）

```yaml
disposition: RESOLVED_FOR_THIS_REWORK_SCOPE
controller_prior_disposition: PARTIAL_REWORK_REQUIRED（severity: major_grounding,
  closure_blocker: true）
root_cause: P7-RW3-CのOutput Consistency Boundaryは`GROUNDED_READY`
  （`_grounded_rag_turn()`）にのみ適用されており、Local Document削除後の
  NO_HIT状態には及んでいなかった。`Nazuna Probe Orion`型の複合固有名詞は
  P7-RW3-BのDeterministic Identifier NO_HIT Denial（identifier_subject_
  count>0のみ発動）の対象にもならず、実Inference Callへ進んでいた。
fix:
  - 新規メソッド`_no_hit_rag_turn()`を追加し、`grounding_state is NO_HIT`
    のみを判定（新しいSubject／Identifier検出Heuristicは追加していない）。
  - `_finalize_grounded_presentation()`の適用条件を
    GROUNDED_READYのみからGROUNDED_READY OR NO_HITへ拡張した。判定本体
    （既存の`_CODE_IDENTIFIER_PATTERN`／`_unsupported_candidate_
    identifiers()`／Safe Grounding Failureへの置換）は無変更のまま
    再利用した。
  - `_events_without_summary()`のBuffering判定（`emit_deltas`／
    `force_bulk_emit`）も同じ拡張条件へ揃え、NO_HIT Candidateが検査前に
    Streamingされないようにした。
  - NO_HIT状態では`_grounded_evidence_text()`が既存Schema Invariant
    （`reference_blocks`／`reference_message`いずれも空）により空文字列
    となるため、既存の判定式がそのままCandidate内のCode形状Identifier
    全てを「未サポート」として検出する——新しい判定式は1件も追加して
    いない。
verification: 新規Integration Test 1件（Handoff必須10項目を1Testで
  網羅、Controllerが指摘した「最初から安全な文面を注入していた」問題を
  是正しCEDAR-9847を明示的に注入）、新規Unit Test 2件（機構単体の
  肯定・否定ケース）。
```

## 4. Acceptance（P7-RW4指定要件）

```text
P7-RW4-ACC-001: PASS（RAG ON＋NO_HIT＋Code-shaped Identifier Candidate
  は非表示、固定Presentationへ置換、Judge Mode非依存）
P7-RW4-ACC-002: PASS（Citation 0件、同一Chat／新規Chat両方で確認）
P7-RW4-ACC-003: PASS（過去Turn／Citation／Digest不変を直接assert）
P7-RW4-ACC-004: PASS（NO_HIT Candidateは検査前にStreamingされない、
  RAG ON＋NO_HIT Turnのみ最小Buffer）
P7-RW4-ACC-005: PASS（RAG OFFのStreaming・挙動は無変更のまま維持）
P7-RW4-ACC-006: PASS（Title-Case Run Heuristic・固有名Allowlist・
  `Nazuna Probe Orion`のHard-code・新しい意味解析基盤のいずれも
  新設していない）
P7-RW4-ACC-007: PASS（P7-CODEX-011／012／Auto-Resumeへ一切触れていない、
  frontend/への本Package由来の変更は0件）
```

## 5. Canonical検証（最終差分、各1回）

```text
uv run pytest -q                     -> 1944 passed, 7 deselected
uv run mypy                          -> Success, no issues found in 526 source files
uv run ruff check .                  -> All checks passed
uv run ruff format --check .         -> 526 files already formatted
```

P7-RW3-D基準（Backend 1941 passed）から、Backend +3（Integration Test 1件＋Unit Test 2件）。全件Regression 0。

Frontend Source変更は本Package内で0件のため（`git status`で確認済み）、Handoff検証順§4の指定通りFrontend再検証は実施していない。Node v22の再Install／再Downloadは一切行わず、既存の`uv run`ツールチェーンのみを使用した——P7-RW3-INCIDENT-001と同種のNetwork逸脱は本Packageでは発生していない（Network Action: 0）。

## 6. Internal Review（1 Cycle）

Recovery Index §7に全観点を記録済み。Critical／Major／MVP Blocker 0件。Minor 1件のみ（P7-RW4-IR-001、新規発生ではなく既存の開示済み境界の延長）。

```yaml
finding_id: P7-RW4-IR-001
severity: minor_observation
disposition: known_deferred_non_blocking
summary: 本Gateが閉じるのはCode形状Identifier（CEDAR-9847型）に限る。
  数字・区切り文字を含まない平易なStale事実文の再利用は対象外のまま
  残る——Handoff自体が要求した契約の範囲内であり、P7-RW3-IR-001／
  P7-RW2-IR-001と同一系統の既開示Scope境界の延長。
```

## 7. Scope境界の遵守

```text
Citation UI／Field順（P7-CODEX-011）: 無変更（frontend/への変更0件）。
Current Reference修正（P7-CODEX-012）: `_splice_before_final_user_
  message()`／`CURRENT_EVIDENCE_AUTHORITY_INSTRUCTION`は無変更。
Auto-Resume: `persistent_conversation_service.py`／`ChatListItem.tsx`
  は本Package開始時点から一切Read/Editしていない。
Node追加Install／再Download: 0件（既存の`uv run`ツールチェーンのみ）。
Network／Git／Backup／Roadmap／Phase 7 Closure／Phase 8／User
  `runtime_data/`: いずれも0件。
Title-Case Run Heuristic再導入: 0件。
```

## 8. Exact Next Action

Codex Controller Bounded Independent Review待ちで停止する。

最大Claimは`COMPLETE_CANDIDATE_FOR_CONTROLLER_REVIEW`。Phase 7 ClosureまたはUser Manual PASSを代行しない。P7-CODEX-011／012は既存のUser実画面Gate（TECHNICALLY_RESOLVED_USER_BROWSER_GATE／TECHNICALLY_RESOLVED_USER_REAL_MODEL_GATE）を維持したまま、本Packageでは変更していない。
