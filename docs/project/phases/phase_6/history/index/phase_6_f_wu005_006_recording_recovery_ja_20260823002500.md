# Phase 6-F-WU-005／006 Recording Mode／Protected Data Negative Matrix Recovery Entry

```yaml
document_id: phase_6_f_wu005_006_recording_recovery
status: current_recovery_entry
phase: phase_6
subphase: phase_6_f
work_unit: p6_f_wu005_wu006_complete_domain_level
role: Claude側設計統括者役
long_running_mode_active: true
created_at: 2026-08-23 00:25:00 JST
```

## Exact Mutation

```text
Created:
  src/margpa_runtime_llm/modules/runtime_observability/domain/recording.py
    （RecordingMode／SafeRecordingEnvelope／build_recording_envelope）
  src/margpa_runtime_llm/modules/runtime_observability/ports.py（RecordingWriterPort）
  src/margpa_runtime_llm/modules/runtime_observability/application/recording_service.py
  tests/unit/runtime_observability/test_recording.py（11 Test）
Modified: なし
Git Mutation: 0
User実runtime_data接触: 0（実Filesystem Writer未実装、Fake Writerのみでテスト）
```

## Work Unit対応

```text
P6-F-WU-005（Recording Modes）        : 完了（Domain／Service層）。OFF→build_recording_envelope
                                        がNoneを返し、RecordingService.record()もWriterへ
                                        到達しない（Test直接検証、Write Call Count=0）。
                                        METADATAはcanonical_input／presented_answerを常にNone化。
                                        実Filesystem Adapter（Atomic Write、Quota、Failure、
                                        Git除外境界）は未実装、Adapter層は別途必要。
P6-F-WU-006（Protected Data Negative）: 完了。SafeRecordingEnvelopeのextra="forbid"により、
                                        thinking／system_prompt／secret／rag_internal_context／
                                        tool_internal_state／hidden_original／partial_outputの
                                        7 Fieldいずれも構造的に受理不可能（Field自体が存在しない）
                                        ことをTestで直接検証。
```

## Validation

```text
New Unit Test  : 11 passed
Full Backend   : 1362 passed／3 deselected（回帰0）
Frontend       : 175 passed／20 files（回帰0）
Ruff／Mypy      : Clean（398 source files）
```

## 未実施（後続）

```text
実Filesystem Recording Adapter（runtime_data/persistent/<scope>/evaluations等への
Atomic Write、Quota／Failure処理、.gitignore境界）は、Phase 6-F完了時点でも未実装。
Conversation GenerationおよびEvaluation/Repair Runへの実配線（6-F-WU-004 User Feedback含む）
と合わせて後続Batchで実施する。
```

## Next Exact Route

Phase 6-G（Integrated UI、P6-G-WU-002 Advanced Component Identity：runtime_model_control
SnapshotとJudge Role Resolverを結合したCurrent Main／Guardrail／Judge／Governance Layer
Projection）、または6-B-WU-006と同種の実Persistence配線を優先するかを次Batchで判断する。
