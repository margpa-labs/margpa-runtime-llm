# Phase 7 Non-Web Closure Alignment — Package P7-NW-D Recovery（User Manual Candidate／Observability）

```yaml
document_id: phase_7_non_web_closure_p7_nw_d_recovery_20260829225900
document_type: package_recovery_index
document_state: final
language: ja
created_at: 2026-08-29 22:59:00 JST
active_contract: phase_7_claude_non_web_closure_alignment_exact_differential_handoff_ja_20260829224014.md
package: P7-NW-D
```

## 0. Recovery Index Pointer

前Package: [P7-NW-BC Recovery](phase_7_non_web_closure_p7_nw_bc_recovery_ja_20260829225700.md)。本Packageの成果物: [User Manual Test Sheet](../operations/phase_7_local_corpus_data_controls_user_manual_test_sheet_ja_20260829225900.md)。次Package: P7-NW-E Recovery（Internal Review／Return）。

## 1. 実施内容

Handoff §4 P7-NW-Dが指定する10項目（初期状態とRAG OFF副作用0、Local Document登録、固有Fact質問、Citation表示、Reload／別Tab／Restart、Document更新、Document削除、Data Controls全Default OFF、Consent独立切替、虚偽成功表示なし）を全て含む[User Manual Test Sheet](../operations/phase_7_local_corpus_data_controls_user_manual_test_sheet_ja_20260829225900.md)を新規作成した。

実際のSettings Modal構造（`SettingsModal.tsx`のCategory `basic／advanced／data_controls`、`LocalCorpusPanel`と`WebSearchPanel`は`advanced`Tab、`DataControlsPanel`は独立`data_controls`Tab）と、各Tabの実際のJa Label（`settingsMenuLabel: "設定"`、`advancedModeLabel: "アドバンスモード"`、`dataControlsMenuLabel: "データコントロール"`）を本Task内でSource直接確認の上、手順文言へ反映した。

## 2. Scope境界の遵守

- User Browserを本Task内でClaudeが操作していない（Real Browser Action 0）。
- 実Web検索、Public URL、NetworkまたはUser既存`runtime_data`へのAccessをManual Sheetへ要求していない（2.10項目でWeb Search Panel操作を含めているが、これはFixture Providerによる固定Sample結果を確認する項目であり、Real Public Webへは到達しない——既存Production CompositionがFixture固定であること自体は`P7-CODEX-001`で既に確認済み）。
- Web Source確認項目（実Web検索結果の正確性等）は本書に含めていない。P7-ACC-032のWeb部分はDeferred（本Addendum§2参照）。

## 3. Action Inventory

```text
Git Action: 0
Network Action: 0
Real Browser Action: 0
Source／Test Mutation: 0
```

Exact next action: P7-NW-E（Internal Review／Final Verification／Exact Return Handoff）へ連結して進む。
