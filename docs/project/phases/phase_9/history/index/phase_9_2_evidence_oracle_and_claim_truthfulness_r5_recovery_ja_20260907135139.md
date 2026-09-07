# Phase 9-2 Evidence Oracle / Claim Truthfulness R5 Recovery

```yaml
document_id: phase_9_2_evidence_oracle_and_claim_truthfulness_r5_recovery_20260907135139
document_state: full_recovery
language: ja
created_at: 2026-09-07T13:51:39+09:00
phase: phase_9
program: phase_9_2
```

## 1. Current Point

Codex Controller R4 Return Independent Review（`phase_9_2_controller_r4_return_independent_review_and_r5_micro_rework_decision_ja_20260907132840.md`、判定`CHANGES_REQUIRED`、Confirmed Findings IR-P9-2-R4-01〜05）を受け、同時に発行されたR5 Exact Handoff（`phase_9_controller_phase_9_2_evidence_oracle_and_claim_truthfulness_r5_exact_handoff_ja_20260907132840.md`）のR5-WU-01〜04を実施した。5件のConfirmed Finding（MAJOR 3件、MODERATE 1件、OPERATIONAL MAJOR 1件）を全件解消した。Restart Read Oracleを実際の値照合まで強化し、Scenario 2/3の実Model Gateはその強化されたOracleのまま実機で再実行して両方とも`completed`を確認した。Exact Returnを新規Fileとして提出、Codex Controller Independent Review待ち。

## 2. What Changed

- **Restart Read Oracle完結（R5-WU-01、IR-P9-2-R4-01 MAJOR修正）**: `_restart_read()`をPlan／Variant Desired Configuration（Digest照合）／Run／Frozen Snapshotの`correlation`＋`provider_identity`（値照合）／Raw Evidence／Comparison（Row＋Metric＋Observation）の9項目Hard Assertへ全面書き直し。Fixtureベースの正例1件＋欠陥注入4パターンのRegression Testで検出力を確認。
- **Scenario Oracle強化（R5-WU-02、IR-P9-2-R4-02 MAJOR修正）**: Scenario 2/3の終了判定を`state == "completed"`のみへ強化（`failed`を許容しない）。Main/Judge/Guardの`called`値をHard Assert、Frozen SnapshotでProvider Identityを照合。False-success回帰Testで検出力を確認した上、実機で両Scenarioを再実行し両方`completed`。
- **Identity Claimの正確化（R5-WU-03、IR-P9-2-R4-03 MAJOR修正）**: Source/Test Docstringに過大表現は存在しなかったことを確認（変更不要と判断）。ReturnにExpected（Frozen Configured/Active/Expected Executed）とActual Executed Provider（全Role`Unavailable`、Request相関Evidence自体が存在しないため）を明確に分離したIdentity Matrixを記載。
- **Shutdown後Cleanupの機械証明（R5-WU-04、IR-P9-2-R4-04 MODERATE修正）**: Handoffの5Step手順どおりの新規専用Testを追加し、`shutdown()`実行後にActor Call 0・Terminal State・`request_cancel()==False`を確認。既存Deadline Testにも同様のPost-shutdown Assertを追加。`run_worker.py`自体は無変更（新規Testは既存R4修正だけでPASSし、追加のProduction Defectは検出されず）。
- **Git操作記録の訂正（IR-P9-2-R4-05 OPERATIONAL MAJOR修正）**: R4の`git stash`/`git stash pop`はGit Write禁止への違反だったと正確に訂正。R5では`git`のRead-onlyコマンド（`rev-parse`/`stash list`/`status --short`）以外は一切実行せず、Backup／復元はローカルファイルの`cp`のみを使用した。

## 3. Files Created/Modified This Round

**新規ファイル**:
- `docs/project/phases/phase_9/handoffs/phase_9_claude_phase_9_2_evidence_oracle_and_claim_truthfulness_r5_exact_return_ja_20260907135139.md`（本Roundの正本Return）
- 本File（Recovery Index）

**修正ファイル（Test、`src/`本体への変更は本Round一切なし）**:
- `tests/integration/test_real_top_level_experiment_production_gate_smoke.py`
- `tests/unit/experiment/test_run_worker.py`

## 4. Exact Return Handoff

[phase_9_claude_phase_9_2_evidence_oracle_and_claim_truthfulness_r5_exact_return_ja_20260907135139.md](../../handoffs/phase_9_claude_phase_9_2_evidence_oracle_and_claim_truthfulness_r5_exact_return_ja_20260907135139.md)

Maximum Claim: `P9_2_R5_USER_MANUAL_CANDIDATE_FOR_CODEX_CONTROLLER_REVIEW`

## 5. Verification Summary

- Restart Read Oracle Focused（Fixtureベース）: 正例1件＋欠陥注入4パターン、全PASS。
- Scenario Oracle False-success回帰: 1件PASS。
- Queue Cancel／Deadline／Shutdown: `test_run_worker.py`全15件PASS（新規1件＋既存2件へAssert追加）。
- Experiment Web Integration: `test_experiment_routes.py`24件全PASS（R5での変更なし、回帰なし）。
- Backend Non-model Full Suite: `2665 passed, 43 deselected`（84.27秒）。R4終了時点`2649 passed, 43 deselected`から純増16件。
- Ruff（Whole Repo）: `All checks passed!`。
- Canonical Mypy（Whole Repo）: `43 errors/4 files`（既存Baseline完全一致）。
- Frontend: 本Round変更なし（Handoff境界どおり着手せず）。
- Sabotage/False-success回帰4件、全て検出力確認・（Production Source変更を伴うものはByte-identical復元も）確認済み。
- 実Model Gate: Scenario 2/3を各1回、逐次実行（最大2 Run上限どおり）。両方`completed`。`_restart_read()`の全9 Hard Assertが両Scenarioで実際にPASS。実行後Modelプロセス残存ゼロ確認済み。
- Resource Preflight: `memory_pressure`のSystem-wide free percentage 81%（実行前）→76%（実行後）、健全。

## 6. Open Items at This Point

- Guard Evidence相関は引き続き`unavailable_correlation`（`called=None`）——真の相関機構自体はPhase 9-1側に存在せず今Round対象外。
- Main/Judgeについても、Provider識別子自体をRequestに紐づけるEvidenceは存在しない（本Roundで明確化、Guardだけの問題ではない）。
- `main_called`曖昧Error Code問題はPhase 9-1側の改修待ち（Scope外）。
- Definition Set/RAG/Presentationの3 Slotは引き続きLive Controller不在（対象外）。
- 実Model Gateの再確認はScenario 2/3各1 Trialのみ（Handoff上限どおり）——複数Trialでの再現性確認は未実施。
- Provider Identity/CorrelationはStore層のみに存在し、Web API DTOへは引き続き未露出（Confirmed Blockerではない）。

## 7. Next Step

Codex Controller Independent Reviewを待つ。Phase 9-2 Complete、Phase 9-3着手、Phase 9 Closure、追加の実Model実行のいずれも、本Returnの範囲では行わない。次の指示を待つ。
