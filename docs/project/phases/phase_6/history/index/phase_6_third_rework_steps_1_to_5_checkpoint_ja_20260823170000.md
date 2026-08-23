most_recent_recovery_index: docs/project/phases/phase_6/history/index/phase_6_recovery_consolidation_second_rework_through_third_review_and_stage_d_ja_20260823154500.md

# Phase 6 Third Rework — Step 1〜5 完了チェックポイント

```yaml
document_id: phase_6_third_rework_steps_1_to_5_checkpoint
status: current_recovery_entry
phase: phase_6
subphase: phase_6_third_rework
work_unit: required_rework_sequence_step_1_through_5
role: Claude側設計統括者役
long_running_mode_active: true
created_at: 2026-08-23 17:00:00 JST
authority: phase_6_codex_third_independent_review_rework_handoff_ja_20260823133224.md
```

## 目的

Third Independent Review §4 Required Rework Sequence（10 Step）のうち、Step 1〜5が
Source／Test実装済み・Full Test Suite PASS・ruff／mypy PASSまで到達したため、
Step 6以降（UI／Calibration Harness／Acceptance再導出／Full再実行／Candidate作成）
に進む前のCheckpointとして記録する。ユーザーからの明示指示「通常の進捗報告では
停止せず連結実行」に従い、これはUserへの停止・確認要求ではなく、Long-running
Automation Companion契約上のStep境界Self-check（Index更新）としてのみ実施する。

## 実施結果（Step 1〜5）

```text
Step 1: P6-GOV-003 Root Boundary/Evidence Correction作成。
  phase_6_governance_evidence_correction_ja_20260823160000.md
  4件目のGovernance Incidentを記録、「Root外操作:0」等の誤申告を訂正。

Step 2: Coordinator/Judge Run Lifecycle修正（P6-CODEX-019/020）。
  - ModelAccessCoordinator: Main-priority実Preemption（CancellationToken経由）、
    Thread start失敗時のSlot Rollback、shutdown()のBool返却化（Thread生存確認）、
    shutdown後のacquire_main即時拒否、MODEL_BUSYと分離した新規Error Code
    INTERNAL_TASK_PREEMPTION_FAILED。
  - LlamaCppModelAdapter/ChatTemplate: stopping_criteria経由の実Cancellation実装
    （Handler Bridgeを経由しない専用経路）。
  - judge_live_integration.py: judge_mode/repair_mode同時Freeze、
    JudgeRunState拡張（queued_or_skipped/cancelled/degraded追加）、
    mark_skipped()のRequest Identity相関化（OFF Modeも含む）、
    _run_judge全体のTerminal Boundary化（あらゆる例外がTyped Failureへ収束）。
  新規Test: tests/unit/inference/test_model_access_coordinator.py（15件）、
  tests/unit/bootstrap/test_judge_live_integration.py（20件）。

Step 3: Repair Fail-closed/Budget/Atomicity修正（P6-CODEX-021）。
  - repair_live_integration.py: Governance/Guardrail Hook例外をFail-closed化
    （degraded Field追加）、実Call数/Token/Wall Timeを実測しBudget実施行使
    （max_total_model_calls 1→2に是正）、3-step永続化チェーンの各失敗を
    fail_generation()でBest-effort補償（最終安全網はrecover_incomplete_
    conversations()既存Restart Recovery）。
  新規Test: tests/unit/bootstrap/test_repair_live_integration.py（17件）。

Step 4: Recording Writer/Evidence Trace修正（P6-CODEX-022）。
  - LocalFilesystemRecordingWriter: os.write() Short Write対応ループ化、
    containment_root経由の中間Path Component Symlink検査、Orphan Temp File
    Age-gated Pruning（300秒未満は保護）、fcntl.flock経由のCross-process/
    Cross-instance直列化、既存*.jsonエントリのHardlink/Symlink Fail-closed化
    （lstat+S_ISREG判定）。
  - Judge Evidence: artifact_digest_sha512/backend_key/backend_versionを
    ModelRuntimeInfo経由で実値記録（従来model_identityのみ）。
  新規Test: tests/unit/runtime_observability/test_local_filesystem_recording_writer.py
  （28件、9件新規）。

Step 5: Attempt Generation Config Provenance修正（P6-CODEX-023）。
  - ConversationGenerationSession._completed_event(): 実際に適用された
    GenerationParametersのCanonical化＋SHA-512 Digestをattempt_provenanceへ
    追加（_generation_config_digest_sha512()）。
  - Repair側もrepair_live_integration.py内で独立Digest（role="repair"）を
    生成・保存（Main/Judge/Repairで異なるDigestを混同しない）。
  新規Test: test_conversation_generation_attempt_provenance.py・
  test_persistent_attempt_provenance.pyへ追加。
```

## 検証状態（Step 5完了時点）

```text
Full Test: TMPDIR="$PWD/.venv/.t" pytest -p no:cacheprovider
  --basetemp=.venv/.t/f4 → 1523 passed, 5 deselected。
Static: ruff check（対象File） → All checks passed。
        mypy src → Success: no issues found in 274 source files。
Git Mutation: 0。Root外操作: 0（本Step群の作業における）。
Provider Memory接触: 0。
```

## Next Exact Route

```text
Step 6: Current Request UI StateとManual Acceptanceの完成（P6-CODEX-024）。
Step 7: Project-local Calibration Harnessと比較Matrixの完成（P6-CODEX-018）。
Step 8: Acceptance IDを1件ずつSource/Test/実機Evidenceから再判定。
Step 9: Full/Static/Frontend/Real Model/Real Browser再実行。
Step 10: 新しい"Phase 6 Claude Third Rework Complete Candidate Handoff"作成。
（Third Review §4 Exact Sequenceに準拠、継続実行中）
```
