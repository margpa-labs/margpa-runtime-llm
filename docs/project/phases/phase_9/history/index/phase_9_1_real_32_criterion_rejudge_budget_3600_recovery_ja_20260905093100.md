# Phase 9-1 実32 Criterion Rejudge Budget 3600 実装 Recovery

```yaml
document_id: phase_9_1_real_32_criterion_rejudge_budget_3600_recovery_20260905093100
document_state: complete_recovery
language: ja
created_at: 2026-09-05T09:31:00+09:00
phase: phase_9
program: phase_9_1
```

## 1. Current Point

Codex Controllerの2026-09-05 09:14:31 JST Exact Handoff(実32 Criterion Rejudge Budget 3600)への対応として、User承認済みの2値変更(`_REJUDGE_TOKENS_PER_CRITERION` 75→100、`LIVE_REPAIR_BUDGET.max_additional_tokens` 2800→3600)を実装した。Fixture/Unit水準の全6項目とSabotage検証を完了し、Preflight(残存なし確認)を経て実機試験を正確に1回実行した結果、**実Main Qwen Repair→実Gemma 32 Criterion Rejudgeが真に成立した**(`finish_reason=STOP`、Decoder COMPLETED、全32 ID一致、Recommendation ACCEPT、改善回答採用)。前回のTruncate(`finish_reason=LENGTH`)問題が解消されたことを実機Evidenceで確認した。Exact Returnを新規Fileとして提出済み、Codex Controller Independent Review待ちで停止している。

## 2. What Changed

- `_REJUDGE_TOKENS_PER_CRITERION`: 75→100、`LIVE_REPAIR_BUDGET.max_additional_tokens`: 2800→3600(唯一の変更、他のBudget/Criterion/Decoder/Context/Deadline値は無変更)。
- Unit Test群(32/33 Criterion境界、E2E成功、1 Token超過)を新しい100/3600の値へ全面書換、Sabotage検証で検出力を確認。
- Test-only Observabilityへ`criterion_id`出現数Countを追加。
- 実機試験を正確に1回実行(Preflight・`tee`完全Log保存込み)、結果は**PASS**——真の成功。

## 3. Files Created This Round

- `docs/project/phases/phase_9/handoffs/phase_9_claude_real_32_criterion_rejudge_budget_3600_exact_return_ja_20260905093032.md`(本Roundの正本Return)
- 本File(Recovery Index)

## 4. Exact Return Handoff

[phase_9_claude_real_32_criterion_rejudge_budget_3600_exact_return_ja_20260905093032.md](../../handoffs/phase_9_claude_real_32_criterion_rejudge_budget_3600_exact_return_ja_20260905093032.md)

Maximum Claim: `P9_1_REAL_32_CRITERION_REJUDGE_BUDGET_3600_GENUINELY_SUCCEEDED`

## 5. Open Items at This Point

- 再現性: 今回1回の成功が常に再現するかは未確認(追加試行は今回の指示で禁止)。
- Gemma Identity/Presented Contentの具体的文字列: 今回のPrint対象に含めておらず、Hard Assert通過という事実からの確定に留まる。
- Selene: 未解決のまま(今回変更なし)。
- Mypy 43 errors/4 files(既存Baseline、今回Scope外)。

## 6. Next Step

Codex Controller Independent Reviewを待つ。Phase Closure、次Phase着手、追加の実機試行のいずれも行わない。
