# Phase 9-1 Controller独立Review(23:54版) IR-R3差分Rework Recovery

```yaml
document_id: phase_9_1_controller_ir_r3_delta_rework_recovery_20260905002426
document_state: complete_recovery
language: ja
created_at: 2026-09-05T00:24:26+09:00
phase: phase_9
program: phase_9_1
```

## 1. Current Point

Codex Controllerの2026-09-04 23:54:34 JST独立Review(CHANGES REQUIRED、IR-R3-01〜05)への対応として、5項目全てに着手・完了した。Exact Return Handoffを新規Fileとして提出済み、Codex Controller Independent Review待ちで停止している。

## 2. What Changed

- IR-R3-01: `repair_live_integration.py`の`_plan_rejudge()`にCounter例外の捕捉を追加。呼出し元でPlanning後の全体Wall-time Deadline再チェックを追加(Cancellation有無で共通)。Test 2件追加(Controller Probe正確な再現)。
- IR-R3-02: `_REJUDGE_TOKENS_PER_CRITERION`を実測(実Tokenizer)に基づき150→75へ再校正。26件成立/32件未成立を定量化。Test 4件追加。
- IR-R3-03: 既存Judge起点Test保持、新規Main起点(Main Governance ENFORCE)Test 2件追加、`repair_requested_by=="main_governance"`を実配線で検証。
- IR-R3-04: Gemma Smoke OracleをFAILED+malformed_output限定へ厳密化。Controllerの`-3`Probeを実Dispatch Engine経由で再現するFixture負例Test含む6件追加。絶対Log Path・因果Scope訂正Docs作成。
- §7④: Gemma Prompt Templateへ局所修復(閉じ括弧確認Rule)を有界2回試行、否定的結果を正直に記録。

## 3. Files Created This Round

- `docs/project/shared/history/unresolved_work/phase_9_1_rejudge_token_calibration_and_32_criterion_infeasibility_snapshot_ja_20260905000817.md`
- `docs/project/shared/history/unresolved_work/phase_9_1_gemma_evidence_refs_json_defect_absolute_log_paths_and_causal_scope_correction_snapshot_ja_20260905001646.md`
- `docs/project/shared/history/unresolved_work/phase_9_1_gemma_local_prompt_repair_attempt_bounded_negative_result_snapshot_ja_20260905002008.md`
- `docs/project/phases/phase_9/handoffs/phase_9_claude_p9_1_controller_ir_r3_delta_rework_exact_return_ja_20260905002304.md`(本Roundの正本Return)
- 本File(Recovery Index)

## 4. Exact Return Handoff

[phase_9_claude_p9_1_controller_ir_r3_delta_rework_exact_return_ja_20260905002304.md](../../handoffs/phase_9_claude_p9_1_controller_ir_r3_delta_rework_exact_return_ja_20260905002304.md)

Maximum Claim: `P9_1_REWORK_INCOMPLETE_FOR_CONTROLLER_REVIEW`

## 5. Open Items at This Point

- 32件Criterion Rejudge未成立(実測校正後も予算不足、最小変更案のみ提示・未実装)。
- Gemma `evidence_refs` JSON欠陥は未解決(局所修復試行は否定的結果、真因未確定)。
- Selene未解決継続(新規実機実行なし)。
- Mypy 43 errors/4 files(既存Baseline、今回Scope外)。
- Frontend再検証未実施(今回変更なし)。

## 6. Next Step

Codex Controller Independent Reviewを待つ。Phase Closure、次Phase着手は行わない。
