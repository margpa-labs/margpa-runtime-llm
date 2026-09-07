# Phase 9-1 通常32 Criterion Rejudge予算2800 実装 Recovery

```yaml
document_id: phase_9_1_normal_32_criterion_rejudge_budget_2800_recovery_20260905082000
document_state: complete_recovery
language: ja
created_at: 2026-09-05T08:20:00+09:00
phase: phase_9
program: phase_9_1
```

## 1. Current Point

Codex Controllerの2026-09-05 07:52:41 JST Exact Handoff(`LIVE_REPAIR_BUDGET.max_additional_tokens`を2000→2800へ変更する、User承認済みの最小案)への対応として、指示された実装境界・必須検証(A: Fixture/Unit、B: 実モデル1回)に着手・完了した。Fixture/Unit水準は全て成立を確認したが、実機(Main Qwen Repair→Gemma 32 Criterion Rejudge)は正確に1回実施し不成立(`accepted=False`)だった。反復・Criterion削減・追加予算拡大は行わず、観測結果をそのまま報告するExact Returnを新規Fileとして提出済み、Codex Controller Independent Review待ちで停止している。

## 2. What Changed

- `LIVE_REPAIR_BUDGET.max_additional_tokens`を2000→2800へ変更(唯一のBudget変更)。他のBudget/Criterion/Decoder値は無変更。
- 2000固定を前提にしていたSource Comment 3箇所、Test 4件(22/26/27/32-不成立)を、現行2800の境界(32件Plan受理・32/33件境界・2800を1 Token超過時の拒否)を記述するCommentと3 Testへ更新。既存E2E Test(32件不成立を証明)を32件成立を証明するTestへ全面書換。
- 旧2000へ戻すRegression Sabotageを実施し、新規/書換Testの検出力(3件とも意図どおり失敗)を確認、復元後の差分無しを確認。
- 実機32 Criterion Rejudge Smoke Testを新規実装、実109 Criterionから実`freeze_semantic_turn(max_criteria=32)`で通常選択した32件を、Main Qwen Repair→Gemma同一Frozen集合Rejudgeへ直接渡す構成で正確に1回実行、不成立を確認・報告。

## 3. Files Created This Round

- `docs/project/phases/phase_9/handoffs/phase_9_claude_normal_32_criterion_rejudge_budget_2800_exact_return_ja_20260905081933.md`(本Roundの正本Return)
- 本File(Recovery Index)

## 4. Exact Return Handoff

[phase_9_claude_normal_32_criterion_rejudge_budget_2800_exact_return_ja_20260905081933.md](../../handoffs/phase_9_claude_normal_32_criterion_rejudge_budget_2800_exact_return_ja_20260905081933.md)

Maximum Claim: `P9_1_BUDGET_2800_UNIT_VERIFIED_REAL_32_CRITERION_REJUDGE_INCOMPLETE`(Budget変更・Fixture/Unit成立は主張、実機32 Criterion Rejudgeの成立は主張しない)

## 5. Open Items at This Point

- 実機32 Criterion Rejudge: 今回1回の実施で不成立(`outcome=unknown`、Plan/Budget層は正常、実Decode層が今回はCOMPLETEDに至らず)。根本原因未確定、反復・Criterion削減・予算拡大は行っていない。
- 実Token/時間Telemetry: 今回の実施では未捕捉(Code側は次回実行に向けて修正済み)。
- Selene: 未解決のまま(前回Returnと同じ、今回変更なし)。
- Mypy 43 errors/4 files(既存Baseline、今回Scope外)。
- Frontend再検証未実施(今回変更なし)。

## 6. Next Step

Codex Controller Independent Reviewを待つ。Phase Closure、次Phase着手は行わない。
