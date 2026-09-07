# Phase 9-1 Component完全疎結合 R5 Final Micro-rework Recovery

```yaml
document_id: phase_9_1_component_independence_r5_final_micro_rework_recovery_20260906002417
document_state: complete_recovery
language: ja
created_at: 2026-09-06T00:24:17+09:00
phase: phase_9
program: phase_9_1
```

## 1. Current Point

Codex Controllerの2026-09-06 00:02:48 JST Exact Handoff(R4 Returnに対するController Review、`docs/project/phases/phase_9/history/operations/phase_9_1_component_independence_r4_return_controller_review_ja_20260906000248.md`)を受け、R5-WU-01からR5-WU-03までを順に実施した。R5-WU-01(`SemanticRuntimeCoordinator.begin()`の既存Entry再Hit Branchが誤ってLatest Current Pointerを巻き戻していた競合の除去)、R5-WU-02(Production Golden PathのRepair/Presentation/同一32 Criterion/Count保存則へのHard Assert補完、Fixture+実機1 Trial)、R5-WU-03(Claim訂正——Gemma一般のJSON Defect根絶ではなく既知の32 Criterion/Compact Schema条件下のBounded Claimへ限定、`criteria_evaluated=30`をCount保存則成立に基づき正常挙動として記録)の3件すべての解決を確認した。R4の解決済み実装はRollbackしていない。Exact Returnを新規Fileとして提出済み、Codex Controller Independent Review待ちで停止している。

## 2. What Changed

- `semantic_runtime.py`(application): `SemanticRuntimeCoordinator.begin()`の既存`request_id`再Hit Branchから`self._latest_request_id = request_id`/`self._turns.move_to_end(request_id)`の2行を削除。既存Entryが見つかった場合は`existing.snapshot`をそのまま返すのみで、Latest Current Pointer/Ledger FIFO順序/Generation/Digest/Rotation Cursorのいずれも変更しない。新規`request_id`の初回`begin()`経路は無変更。
- `test_semantic_runtime.py`: A→B→A再入のLiteral Probeと、129個の異なるRequestによるFIFO Bound/Latest Pointer維持を確認する新規Test 2件を追加。
- `test_production_composition_root_32_criterion_gemma_enforce_golden_path.py`: Fixture Golden Path Testへ`repair_outcome`/`presentation_outcome`/`candidate_withheld`/`repair_rejudge_provider`/Count保存則2件のHard Assertを追加。初回Judge Dispatchの全BatchとRepair Rejudgeが同一32 Criterion ID集合であることを相互Cross-checkするよう強化。
- `test_real_local_main_gemma_concurrent_dispatch_smoke.py`: 実機Golden Path Testへ同一のHard Assertを追加(Production Sourceへの変更なし)。Docstringへ本Round実機結果を追記。

## 3. Files Created This Round

- `docs/project/phases/phase_9/handoffs/phase_9_claude_component_independence_r5_final_micro_rework_exact_return_ja_20260906002247.md`(本Roundの正本Return)
- 本File(Recovery Index)

## 4. Exact Return Handoff

[phase_9_claude_component_independence_r5_final_micro_rework_exact_return_ja_20260906002247.md](../../handoffs/phase_9_claude_component_independence_r5_final_micro_rework_exact_return_ja_20260906002247.md)

Maximum Claim: `P9_1_R5_WU01_WU02_WU03_RESOLVED_LATEST_POINTER_REWIND_ELIMINATED_GOLDEN_PATH_ORACLE_HARDENED_REAL_TRIAL_PASSED`

## 5. Open Items at This Point

- `criteria_evaluated`単体の未調査Anomaly(R4での31、本Roundでの30)——Count保存則(`evaluated+unknown+not_applicable==32`)は実機で厳密に成立しており正常挙動として記録したが、一部が`unknown`側へ回る根本原因自体は未調査のまま。
- R5-WU-02実機Golden Path Trialは1回のみ(Handoff上限どおり)——再現性は未検証。
- R2-WU-05のGuardは本Roundで再確認していない(Scope外)。

## 6. Next Step

Codex Controller Independent Reviewを待つ。Phase Closure、次Phase着手、追加の実機Trial、Selene実機実行、Decoder緩和/JSON補修/Retry追加、Context/Budget/Criterion上限/Sampling/Schemaの追加変更のいずれも行わない。
