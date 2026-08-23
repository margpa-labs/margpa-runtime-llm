# Phase 6-D Subphase Recovery（LLM-as-a-Judge）

```yaml
document_id: phase_6_d_subphase_recovery
status: current_recovery_entry
phase: phase_6
subphase: phase_6_d
work_unit: p6_d_wu001_wu002_wu003_wu006_complete
role: Claude側設計統括者役
long_running_mode_active: true
created_at: 2026-08-23 00:00:00 JST
```

## Exact Mutation（本Subphase累計）

```text
Created:
  src/margpa_runtime_llm/modules/evaluation/domain/llm_judge.py
  src/margpa_runtime_llm/modules/evaluation/application/judge_role_resolver.py
  src/margpa_runtime_llm/modules/evaluation/application/judge_prompt_builder.py
  src/margpa_runtime_llm/modules/evaluation/application/judge_output_decoder.py
  src/margpa_runtime_llm/modules/evaluation/application/judge_budget_gate.py
  tests/unit/evaluation/test_llm_judge_contracts.py
  tests/unit/evaluation/test_judge_role_resolver.py
  tests/unit/evaluation/test_judge_prompt_and_decoder.py
  tests/unit/evaluation/test_judge_budget_gate.py
Modified:
  src/margpa_runtime_llm/modules/evaluation/ports.py（LlmJudgePort追加）
Git Mutation: 0
```

## Work Unit対応

```text
P6-D-WU-001（Typed Judge Adapter）        : 完了。Role／Artifact／Rubric／Prompt Digest／
                                             Seed／Config／Timeout／Token／Latency／Cost／
                                             Failure Contract実装。Core非依存Port。
P6-D-WU-002（Role-separated Binding）      : 完了。resolve_judge_independence()で
                                             MAIN_SELF／SHARED_ARTIFACT／INDEPENDENT_ARTIFACT／
                                             UNAVAILABLEを捏造なく判定。
P6-D-WU-003（Rubric／Prompt／Decoder）      : 完了。Prompt Builder（決定的、Raw非保存前提）、
                                             Strict Decoder（6種のMalformed Shapeで
                                             Fail-closed検証）。
P6-D-WU-004（Calibration／Bias Matrix）    : 未実施。比較実験Infrastructure（Position／
                                             Verbosity／Language／Self-preference比較）は
                                             Phase 6-H Experiment Freezeと合わせて実施する
                                             方が重複が少ないと判断、Backlog化。
P6-D-WU-005（Real Local Judge Experiment） : 未実施。実Qwen Model LoadがCurrent Environment
                                             で必要（model_smoke Class）。6-I Real Browser
                                             Golden Path前後で実施する。
P6-D-WU-006（Failure／Cost Gate）           : 完了。apply_judge_budget_gate()でToken／
                                             Wall-time超過をCOST_LIMIT_EXCEEDED／TIMEOUTへ
                                             Downgrade。既にFAILEDのResponseは再分類しない。
```

## Validation

```text
New Unit Test  : 23 passed（Judge Contract 3、Role Resolver 5、Prompt/Decoder 11、Budget Gate 4）
Full Backend   : 1314 passed／3 deselected（回帰0）
Frontend       : 175 passed／20 files（回帰0）
Ruff／Mypy      : Clean（366 source files）
```

## Next Exact Route

Phase 6-E（Bounded Repair、P6-E-WU-001 Repair Domain／Registry）へ進む。
