# Phase 9-2 Explicit Default-OFF Experiment Runtime Gate Final Recovery

```yaml
document_id: phase_9_2_explicit_default_off_experiment_runtime_gate_final_recovery_20260911162216
document_state: final_complete_candidate
language: ja
created_at: 2026-09-11T16:22:16+09:00
phase: phase_9
program: phase_9_2
executor_identity_type: session_id
executor_session_id: local_d7f17853-1ab4-45aa-bacd-b9d6db898b65
controller_provider: codex
controller_task_id: 019f739b-8a21-7592-95cc-c83c9c08e5f6
completion_claimed: true
maximum_claim: P9_2_EXPLICIT_DEFAULT_OFF_EXPERIMENT_RUNTIME_GATE_COMPLETE_CANDIDATE_FOR_CODEX_CONTROLLER_REVIEW
phase_9_2_closure_authorized: false
phase_9_3_authorized: false
git_write_performed: false
```

## 1. Current Point

CodexのPartial Return（`phase_9_codex_phase_9_2_explicit_default_off_experiment_runtime_gate_partial_exact_return_ja_20260911160254.md`）がユーザー中継指示によりControllerへ固定返却された後、Controller（Codex, Task ID `019f739b-8a21-7592-95cc-c83c9c08e5f6`）がユーザー中継でClaude（Session ID `local_d7f17853-1ab4-45aa-bacd-b9d6db898b65`）へ差分継続Exact Handoffを発行した。Claudeは同Handoffの本文とMandatory Reading 5点をSHA-512照合の上で読了し、Current Working Treeをロールバックせずに残差6項目（CL-GATE-01〜06）を完結させ、Final Exact Returnを新規Append-only Pathで作成した。

## 2. What Changed（本Round追加分）

- `web/app.py`の未検証non-local lifespan fail-closed GuardをFocused Testで検証し、PASSを確認。
- `experiment_routes.py`の全Mutation/Read Endpointが一律`service is None`（`/runs`は`worker is None`も）でDisabled化することをSource全数確認。
- 最終Source状態に対するRelevant Regression（`test_web_cli.py` + `test_experiment_routes.py`）で`72 passed`を確認。
- `web/app.py`のGuard条件を一時的にSabotage（`if False and (...)`）し、Focused Testが確実にFailureを検出することを確認。`cp`によるLocal Backup（`git stash`不使用）から復元し、Byte一致（SHA-512一致、`diff`空）と復元後PASSを確認。
- Changed 8 PathへRuffを実行しClean確認。
- Repository全体へMypyを実行し、Changed Path内で新規Error 1件（`test_experiment_routes.py`内の変数名衝突による型不整合）を検出・局所修正、修正後Changed Path内新規Error 0を確認。Repository全体の残り43件はChanged Path外の既存Baselineであり本Round Scope外。
- Backend-onlyReworkであり`frontend/`および配信Bundleを変更していないため、Frontend Build再実行は不要と判断（判断理由をReturnに明記）。
- Review A（Default OFF/Authority/Bootstrap/API/Lease/Direct Factory/Access Policy/Shutdown）とReview B（Explicit ON Regression/非波及/Test Oracle偽PASS耐性/Disabled Surface/Configuration整合）を完了。Confirmed Blocker/Major残件0。

## 3. Files Created/Modified This Round

**新規ファイル**:
- `docs/project/phases/phase_9/handoffs/phase_9_claude_phase_9_2_explicit_default_off_experiment_runtime_gate_final_exact_return_ja_20260911162216.md`（本Roundの正本Return）
- 本File（Final Recovery Index）

**修正ファイル（本Round分、Codex分に追加）**:
- `tests/integration/web/test_experiment_routes.py`（Mypy Finding修正: 変数名改名+型注釈追加、1箇所）

**Sabotage→復元によりByte一致で無変更に帰結したファイル**:
- `src/margpa_runtime_llm/web/app.py`（Sabotage-regression実施後、復元によりSabotage前とSHA-512完全一致）

**Codex分（本Roundでは非接触、そのまま維持）**:
- `src/margpa_runtime_llm/entrypoints/web/main.py`
- `src/margpa_runtime_llm/bootstrap/web_application.py`
- `src/margpa_runtime_llm/web/experiment_routes.py`
- `src/margpa_runtime_llm/web/contracts.py`
- `tests/unit/web/test_web_cli.py`
- `tests/integration/test_real_top_level_experiment_production_gate_smoke.py`

## 4. Exact Return Handoff

[phase_9_claude_phase_9_2_explicit_default_off_experiment_runtime_gate_final_exact_return_ja_20260911162216.md](../../handoffs/phase_9_claude_phase_9_2_explicit_default_off_experiment_runtime_gate_final_exact_return_ja_20260911162216.md)

Maximum Claim: `P9_2_EXPLICIT_DEFAULT_OFF_EXPERIMENT_RUNTIME_GATE_COMPLETE_CANDIDATE_FOR_CODEX_CONTROLLER_REVIEW`

## 5. Verification Summary

- Focused Guard Test: `1 passed, 31 deselected`
- Relevant Regression（最終Source状態）: `72 passed`
- Sabotage-regression: 検出→`cp`復元→Byte一致（SHA-512一致）→再PASS、全て確認済み
- Ruff（Changed 8 Path）: Clean
- Mypy（Repository全体、`pyproject.toml`準拠）: Changed Path内新規Error 0（発見1件は本Round内で修正済み）、Changed Path外Baseline 43件は対象外
- Frontend Build: 未実施（Backend-onlyReworkのため不要と判断）
- Real Model／Browser／Network: 実行なし
- Git操作: `rev-parse`（Read-only）のみ、HEAD不変（`abbdafa12a735b1a90c7038f2d8f2347eb912c0d`）

## 6. Open Items at This Point

- Confirmed Blocker/Major、Minor/Non-blockerともに残件なし。
- Repository全体のMypy Baseline Error 43件（Changed Path外）は本Round Scope外の既知事項として記録。Controller判断で将来Scopeへ入れるかを別途決定。
- `.task_tmp/p9_2_experiment_gate`はProject-root-local Test Tempとして保持、削除していない。

## 7. Next Step

Codex Controller Independent Reviewを待つ。追加Rework、User Manual、Phase 9-2 Closure、Phase 9-3/10着手、Git操作のいずれも、本Returnの範囲では行わない。
