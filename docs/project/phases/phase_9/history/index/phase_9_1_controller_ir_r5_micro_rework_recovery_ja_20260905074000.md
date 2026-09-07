# Phase 9-1 Controller独立Review(IR-R5版) 最終Micro Rework Recovery

```yaml
document_id: phase_9_1_controller_ir_r5_micro_rework_recovery_20260905074000
document_state: complete_recovery
language: ja
created_at: 2026-09-05T07:40:00+09:00
phase: phase_9
program: phase_9_1
```

## 1. Current Point

Codex Controllerの2026-09-05 07:18:33 JST独立Review(CHANGES REQUIRED、IR-R5-01/02)への対応として、指定された残件2件のみに着手・完了した。受理済みのGemma Schema修正・他経路の再設計は行っていない。Exact Return Handoffを新規Fileとして提出済み、Codex Controller Independent Review待ちで停止している。

## 2. What Changed

- IR-R5-01: `_plan_rejudge()`の実処理を`_plan_rejudge_outcome()`へ拡張し、Counter例外・Token/Context不足・Worker Registry shutdown拒否を`rejection_reason`で明示的に分離。呼出し元(`attempt_live_repair()`)で3種のTyped `rejected_reason`(`repair_rejudge_counter_failed`／`repair_rejudge_budget_insufficient`／`repair_rejudge_worker_registry_unavailable`)へ写像。Deadline/Cancelの既存優先チェック順序(前回IR-R4-01)は無変更。既存のCounter例外Testの誤った期待値を訂正し、Registry shutdown拒否の新規回帰Testを追加。
- IR-R5-02: Judge起点Gemma Repair Testへ`repair_outcome`／`repair_accepted`／`presentation_outcome`のHard Assertを追加し、safe fallbackでも成立してしまっていた弱いAssertを置き換え。実機1回で確認(全実機Assert通過)。Main Governance起点Testの誤解を招く関数名(`...persists_the_repair`)を`...authorizes_and_adopts_the_repair`へ改名、既存Fixture-model永続化Testとの二層Evidence関係をDocstringに明記。

## 3. Files Created This Round

- `docs/project/phases/phase_9/handoffs/phase_9_claude_p9_1_controller_ir_r5_micro_rework_exact_return_ja_20260905073900.md`(本Roundの正本Return)
- 本File(Recovery Index)

## 4. Exact Return Handoff

[phase_9_claude_p9_1_controller_ir_r5_micro_rework_exact_return_ja_20260905073900.md](../../handoffs/phase_9_claude_p9_1_controller_ir_r5_micro_rework_exact_return_ja_20260905073900.md)

Maximum Claim: `P9_1_REWORK_INCOMPLETE_FOR_CONTROLLER_REVIEW`(Planner Failure分類の完成、Judge起点Gemma Repair Testの改善回答採用の直接証明という2件の新規成立を含む)

## 5. Open Items at This Point

- 32件Criterion Rejudge: 実測校正後も予算不足のまま未変更。
- Selene: 未解決のまま(延期候補登録のみ、今回変更なし)。
- Gemma不正JSON欠陥の真因: 修正は有効だが確定的な根本原因検証はしていない。
- Mypy 43 errors/4 files(既存Baseline、今回Scope外)。
- Frontend再検証未実施(今回変更なし)。
- 他4件の実機Test(Crux／OBSERVE／ENFORCE-accept／Main Governance ENFORCE): 前回5/5 PASSを維持しているが、今回は再実行していない。

## 6. Next Step

Codex Controller Independent Reviewを待つ。Phase Closure、次Phase着手は行わない。
