# Phase 6-I-WU-001 Adversarial／Fault Matrix

```yaml
document_id: phase_6_i_wu001_adversarial_fault_matrix
status: current_recovery_entry
phase: phase_6
subphase: phase_6_i
work_unit: p6_i_wu001_complete
role: Claude側設計統括者役
long_running_mode_active: true
created_at: 2026-08-23 03:00:00 JST
```

## 目的

P6-I-WU-001要件（Malformed Judge、Stale Digest、Race、Cancel、Switch、Context
Overflow、Repair Exhaustion、Recorder Failure、Status FailureおよびSecret
非露出）の10項目全てについて、既存Evidenceの棚卸しと、真のGapのみへの新規
Focused Testを行う。

## Exact Mutation

```text
Modified:
  tests/unit/runtime_observability/test_recording.py
    + _FailingWriter、test_writer_failure_propagates_and_is_not_counted_as_a_successful_write
  tests/unit/runtime_observability/test_status_projection.py
    + test_current_request_projection_surfaces_a_failed_state_verbatim_not_coerced
```

## Matrix（項目→Evidence）

| # | 項目 | Evidence | 種別 |
|---|---|---|---|
| 1 | Malformed Judge | `test_judge_prompt_and_decoder.py::test_decode_fails_closed_on_every_malformed_shape`／`test_fail_closed_variant_never_raises_and_reports_malformed_output` | 既存 |
| 2 | Stale Digest | `test_runtime_model_controller.py::test_stale_expected_digest_is_rejected_even_with_correct_revision`／`test_dynamic_context_and_tokens.py::test_set_max_new_tokens_with_stale_cas_is_rejected` | 既存 |
| 3 | Race（Busy Gate） | `test_runtime_model_controller.py::test_switch_is_rejected_while_a_generation_is_active_idle_only_gate`／`test_generation_busy_gate.py` | 既存 |
| 4 | Cancel | `test_conversation_generation.py`（`request_cancel`／`force_cancel`／`cancelled`Path群、既存Phase実装） | 既存 |
| 5 | Switch（失敗／Rollback／二重失敗） | `test_runtime_model_controller.py::test_load_failure_rolls_back_to_previous_model_and_raises_load_failure`／`test_double_failure_leaves_runtime_unavailable_not_a_guessed_previous_value` | 既存 |
| 6 | Context Overflow | `test_dynamic_context_and_tokens.py::test_context_change_above_effective_max_is_rejected_without_touching_the_backend` | 既存 |
| 7 | Repair Exhaustion | `test_state_machine_and_budget.py::test_budget_exhausted_on_attempts_raises`／`test_budget_exhausted_on_depth_raises` | 既存 |
| 8 | Recorder Failure | `test_recording.py::test_writer_failure_propagates_and_is_not_counted_as_a_successful_write` | **新規（真のGap）** |
| 9 | Status Failure | `test_status_projection.py::test_current_request_projection_surfaces_a_failed_state_verbatim_not_coerced` | **新規（真のGap）** |
| 10 | Secret非露出 | ①`_RuntimeModelContract`/`_FeatureModesContract`が`extra="forbid"`＋明示Field Allowlistで構造的に担保。②`runtime_model_control_error_response()`の502分岐は`str(error)`を含めない固定Safe Message（Load/Rollback Failureの`reason`はSnapshot内部のみに保持され、Web Responseへ非露出）。③`RuntimeModelStatusResponse`は`last_transition_receipt`／`failure_reason`を含まない。 | 既存の構造的性質を確認（コード監査） |

## 発見事項

```text
#8 Recorder Failure: RecordingService.record()はWriterがRaiseした場合、
  例外をそのままPropagateし、write_call_countをIncrementしない（成功として
  誤ってCountされない）ことを確認した。これはFail-closed原則と整合するが、
  従前は明示的なTestが存在しなかった真のGapだった。

#9 Status Failure: project_current_request_status()は"failed"のような
  失敗Stateも他のPointの成功Stateと混在した状態で、無加工のまま透過する
  ことを確認した。特別なCoercion／Maskingロジックが存在しないことを実証。

#10 Secret非露出: RuntimeModelLoadFailure／RuntimeModelRollbackFailureの
  reasonフィールド（Backend例外由来でLocal File Pathを含みうる）は、
  Web層のCatch-all 502 Responseでは固定Safe Messageに置換され、
  str(error)も、Snapshotのfailure_reasonも、Web Responseへは一切
  含まれないことをCode Audit（web/runtime_model_control_routes.py:217-223、
  RuntimeModelStatusResponseのField一覧）で確認した。
```

## Validation

```text
新規Test単体: 2 passed（0.06s）
Full Suite  : 1405 passed, 5 deselected in 62.18s（既存1403 + 新規2、回帰0）
Ruff        : All checks passed!
Mypy        : Success: no issues found in 418 source files
```

## Next Exact Route

P6-I-WU-003（Real Browser Golden Path）へ進む。実Hardware Model Loadと実Settings
UIを初めて統合した検証を行う。
