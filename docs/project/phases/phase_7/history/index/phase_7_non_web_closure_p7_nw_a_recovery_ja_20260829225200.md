# Phase 7 Non-Web Closure Alignment — Package P7-NW-A Recovery（Scope／Acceptance Claim Correction）

```yaml
document_id: phase_7_non_web_closure_p7_nw_a_recovery_20260829225200
document_type: package_recovery_index
document_state: final
language: ja
created_at: 2026-08-29 22:52:00 JST
active_contract: phase_7_claude_non_web_closure_alignment_exact_differential_handoff_ja_20260829224014.md
package: P7-NW-A
```

## 0. Recovery Index Pointer

前Package: [P7-NW-0 Recovery](phase_7_non_web_closure_p7_nw_0_recovery_ja_20260829224815.md)。本Packageの成果物: [Phase 7 Non-Web Scope／Acceptance Addendum](../operations/phase_7_non_web_scope_and_acceptance_addendum_ja_20260829225200.md)。次Package: P7-NW-BC Recovery。

## 1. 実施内容

Append-onlyの[Phase 7 Non-Web Scope／Acceptance Addendum](../operations/phase_7_non_web_scope_and_acceptance_addendum_ja_20260829225200.md)を新規作成した。`phase_7_acceptance_matrix_ja.md`（Frozen）は無変更。32 Acceptance全件を個別にClass（`CURRENT_PHASE_APPLICABLE`／`DEFERRED_TO_PHASE_11_PLUS`／`CURRENT_KNOWN_PARTIAL_NON_BLOCKING`）とDisposition（PASS／PARTIAL／DEFERRED／USER MANUAL GATE）へ再導出し、各IDへ直接Evidence Pointerを付した。

Handoff §4 P7-NW-Aで指定された最低限の割当（P7-ACC-003, 016-022, 024, 028のWeb部分, 032のWeb部分をDeferred／P7-ACC-001,002,004-015のLocal Corpus部分,023のLocal Context Source部分,025-031の非Web部分,032のLocal部分をCurrent Phase Applicable）をそのまま使用し、Handoffで明示されなかったID（005-007, 009, 010, 012-015, 026, 027, 029-031）はP7-I Final Recovery §6とController Review §7の既存Evidenceから本書が個別に再導出した。

## 2. P7-ACC-008の捏造防止確認

`P7-ACC-008`はHandoff §4の明示指示どおり`CURRENT_KNOWN_PARTIAL_NON_BLOCKING`のまま`PARTIAL`とし、`PASS`へ捏造していない。本Task中にEmbedding Model、Vector DBまたは疑似Embeddingを一切追加していないことをSource Diff 0（P7-NW-0 Recovery §5参照）で保証する。

## 3. P7-ACC-025の追加検討（Handoffの最低限指定を超える個別確認）

Handoff §4の最低限指定では`P7-ACC-025-031の非Web部分`を一括で`CURRENT_PHASE_APPLICABLE`としていたが、個別導出の過程で`P7-ACC-025`（Source／Retention／Export／Delete／External Transmission／Purpose Consentの分離）の「Export」「Delete」という文言に対し、実装がこの2軸を独立したData Lifecycle操作として一切実装していないことを確認した（`/api/v2/data-controls`は`/policy` `/consent` `/reset`の3経路のみ）。

この欠落自体は元Exact Return Handoff §9で既に開示済みの意図的Scope縮小（Hard Scope Exclusion「全Data Export／Delete」）であり、UI／API側も虚偽のCapability表示を一切行っていないことを`DataControlsPanel.tsx`、全`dataControls*`翻訳キー、`data_controls_routes.py`、`data_controls_contracts.py`の直接確認で検証した（P7-NW-0 Recovery §4観点2）。したがって`P7-ACC-025`は一括`PASS`ではなく`PARTIAL`として個別に記録した——Handoffの最低限指定を「一括Regression 0だけで代替しない」（Handoff §4本文）という要求に沿って、より正確な粒度へ補正したものである。

## 4. Verification（Docs-only変更）

```text
新規File: history/operations/phase_7_non_web_scope_and_acceptance_addendum_ja_20260829225200.md
既存File変更: 0（phase_7_acceptance_matrix_ja.md、Exact Return Handoff、Controller Review、
  External Web Deferral Decisionのいずれも無変更、Append-onlyを厳守）
Source／Test変更: 0
```

Verification Contract §5.2「Docsだけの変更ならMarkdown、Path、Digest、Acceptance Mappingを確認する」に従い、本Addendumの32項目全件がFrozen Acceptance Matrixの32 IDと1対1対応することを目視確認した（新規ID追加、既存ID欠落いずれもなし）。

## 5. Action Inventory

```text
Git Action: 0
Network Action: 0
Source／Test Mutation: 0
```

Exact next action: P7-NW-BC（Local Corpus／Data Controls Closure Readiness確認）へ連結して進む。
