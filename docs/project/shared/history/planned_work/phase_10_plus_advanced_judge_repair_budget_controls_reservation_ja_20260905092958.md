# Phase 10以降予約 — Advanced Judge／Repair Budget設定

```yaml
document_id: phase_10_plus_advanced_judge_repair_budget_controls_reservation_20260905092958
document_type: planned_work_ui_and_runtime_configuration_reservation
document_state: reserved_effort_gate_pending
language: ja
recorded_at: 2026-09-05 09:29:58 JST
decision_authority: user
authority_owner: Nazuna Research
target_phase: phase_10_if_low_effort_else_later
project_stage: individual_r_and_d_mvp_portfolio
implementation_authorized: false
append_only: true
```

## 1. 予約内容

Judge→Repair→RejudgeのToken BudgetをSource定数だけに固定せず、将来のAdvanced設定候補として扱う。Phase 10のUI再構成時に低工数で既存設定系へ接続できるなら同Phase内、Runtime Contract・保存・Evidenceの広い変更が必要ならMVP後へ送る。

通常利用者向けの主要画面には常時表示せず、SettingsのAdvanced領域へ置く。右側検証パネルでは、設定操作ではなく「対象Turnで実際にFrozenされた値」を必要時に確認できるRead-only詳細とする。

## 2. Phase 9-1で得た実測経緯

1. Rejudge出力見積りを実Qwen Tokenizerで測り、最悪59.4 Token／Criterionへ約25% Marginを加えて暫定75とした。
2. Repair Candidate上限400＋75×32=2800のため、User承認で総Budgetを2000→2800へ変更した。
3. Fixtureでは32 CriterionのPlan／Repair→Rejudge→採用が成立した。
4. 実GemmaではPrompt 3612、Completion 2400、`finish_reason=length`となり、未完JSONでStrict Decode FAILEDとなった。75×32の実出力上限が不足したことを完全Logで確認した。
5. Userは次の最小修復として100 Token／Criterion、総Budget 3600を承認した。実機再確認は別Handoffで進行する。

この経緯から、適切な値はProvider、Criterion数、Prompt長、Context、Hardware、応答の冗長性に依存し、単一の永久固定値とは限らない。ただしMVP段階で複雑な自動最適化を必須化しない。

## 3. Advanced設定候補

| UI表示候補 | Current候補 | 内部対応 |
|---|---:|---|
| Rejudge出力上限／Criterion | 100 | `_REJUDGE_TOKENS_PER_CRITERION`相当 |
| Repair Pipeline総Token Budget | 3600 | `LIVE_REPAIR_BUDGET.max_additional_tokens`相当 |
| Repair Candidate上限 | 400 | 原則Read-only。既存値を表示 |
| 最大選択Criterion数 | 32 | MVPではRead-only候補 |
| Rejudge計算上限 | 3200 | `100×32`の自動計算表示 |
| 必要最小総量 | 3600 | `400＋100×32`の自動計算表示 |

ラベルは内部変数名だけで示さず、「何の上限か」「増やすと速度・メモリ・待ち時間へどう影響するか」を短く説明する。Defaultへ戻す操作を用意する。

## 4. 保存・検証要件

- 設定は明示保存し、Server再起動後も維持する。
- Turn開始時に値をFrozenし、進行中Turnを設定変更で巻き戻さない。
- `総Budget >= Repair Candidate上限 + Criterion単価 × 最大Criterion数`を満たさない保存は拒否する。
- `Prompt Token + Rejudge上限 <= Provider Context`を事前検証し、不成立を成功扱いしない。
- 数値は正の整数、上限値を設け、極端な値には警告を出す。
- Current設定と、過去Turnで実際に使ったFrozen値を混同しない。
- 設定変更はEvidenceへ値と時刻を残すが、Raw Model Outputの保存許可を自動拡張しない。
- Provider別Profileは将来候補。Phase 10 MVPではGlobal Defaultのみでもよい。

## 5. Phase 10で行う条件

次を既存の設定保存・Validation・Frozen Turn Contractの再利用で実装できるなら、Phase 10中の小規模項目として採用候補とする。

- Backend設定2値の読込／保存
- Advanced UIの入力2項目と計算表示
- Invalid値拒否、Default復元、再起動維持
- 対象TurnへのFrozen値反映Test

次が必要ならPhase 10必須条件にせず、後続予約へ送る。

- DB Migrationや複数保存形式の新設
- Provider別の動的Profile設計
- In-flight更新、複雑なConcurrency制御
- Evidence Schema全体の変更
- Rejudge Batching／自動Budget最適化
- UI全体の再設計を止める規模のRework

## 6. 非目標

本予約はBudgetを無制限化するものではない。JSON Retry、Decoder緩和、Criterion削減、失敗の成功化を設定画面から許可しない。Phase 9-1の実機成立条件や、Phase 10の既定計画をこの時点で変更しない。

