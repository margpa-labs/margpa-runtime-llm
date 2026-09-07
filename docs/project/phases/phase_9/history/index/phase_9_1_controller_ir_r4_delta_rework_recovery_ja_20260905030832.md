# Phase 9-1 Controller独立Review(IR-R4版) 残差Rework Recovery

```yaml
document_id: phase_9_1_controller_ir_r4_delta_rework_recovery_20260905030832
document_state: complete_recovery
language: ja
created_at: 2026-09-05T03:08:32+09:00
phase: phase_9
program: phase_9_1
```

## 1. Current Point

Codex Controllerの2026-09-05 00:35:07 JST独立Review(CHANGES REQUIRED、IR-R4-01/02/§4/§5)への対応として、全項目に着手・完了した。今回、Gemma不正JSON欠陥の第2仮説(Schema Field順序変更)が有界試行で成功し、Golden Path実機Test 5件全PASSという大きな進展があった。User事前承認条件を今回両方充足したため、Seleneを延期候補として登録した(Selene自体は未解決のまま)。Exact Return Handoffを新規Fileとして提出済み、Codex Controller Independent Review待ちで停止している。

## 2. What Changed

- IR-R4-01: `_plan_rejudge()`のCounter呼出しを`run_tracked_stage()`で有界化(残り全体Deadline、Cancel伝播)。`_budget_exceeded`を`rejudge_plan is None`より先にチェックする順序へ変更。Controller Probe 2件の正確な再現Test追加。
- IR-R4-02: 「26件成立」→「26件Plan受理」への訂正。21件境界(候補400 Token消費時)を追加確認。
- §4前半: Main起点保存Test 2件を`repair_mode ∈ {"off","observe"}`でParametrize、既存Judge起点Testは無変更で保持。
- §4/§5: Gemma不正JSON欠陥の第2仮説(evidence_refsをCriterion Entry内の最後のFieldにしない)を有界2回で検証、成功。`selene.py`/`judge_prompt_builder.py`のSchema Field順序を正式修正。Golden Path実機Test 4件新規追加、既存Crux Testと合わせ5/5全PASS。

## 3. Files Created This Round

- `docs/project/shared/history/unresolved_work/phase_9_1_26_criterion_plan_acceptance_vs_execution_claim_correction_snapshot_ja_20260905005446.md`
- `docs/project/shared/history/unresolved_work/phase_9_1_gemma_golden_path_normalized_via_schema_field_order_fix_snapshot_ja_20260905030530.md`
- `docs/project/phases/phase_9/handoffs/phase_9_claude_p9_1_controller_ir_r4_delta_rework_exact_return_ja_20260905030720.md`(本Roundの正本Return)
- 本File(Recovery Index)

## 4. Exact Return Handoff

[phase_9_claude_p9_1_controller_ir_r4_delta_rework_exact_return_ja_20260905030720.md](../../handoffs/phase_9_claude_p9_1_controller_ir_r4_delta_rework_exact_return_ja_20260905030720.md)

Maximum Claim: `P9_1_REWORK_INCOMPLETE_FOR_CONTROLLER_REVIEW`(ただしGemma Golden Path実機成立・Selene延期候補登録という新規の肯定的進展を含む)

## 5. Open Items at This Point

- Selene: 未解決のまま(延期候補として登録のみ、Native Crash原因未確定)。
- 32件Criterion Rejudge: 実測校正後も予算不足のまま未変更。
- Gemma不正JSON欠陥の真因: 修正は有効だったが、確定的な根本原因検証はしていない。
- Mypy 43 errors/4 files(既存Baseline、今回Scope外)。
- Frontend再検証未実施(今回変更なし)。

## 6. Next Step

Codex Controller Independent Reviewを待つ。Phase Closure、次Phase着手は行わない。
