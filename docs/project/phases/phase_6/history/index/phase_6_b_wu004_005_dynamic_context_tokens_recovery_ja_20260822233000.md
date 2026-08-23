# Phase 6-B-WU-004／005 Dynamic Context Size／Max New Tokens Recovery Entry

```yaml
document_id: phase_6_b_wu004_005_dynamic_context_tokens_recovery
status: current_recovery_entry
phase: phase_6
subphase: phase_6_b
work_unit: p6_b_wu004_wu005_complete
role: Claude側設計統括者役
provider: claude_code
long_running_mode_active: true
created_at: 2026-08-22 23:30:00 JST
```

## Exact Mutation

```text
Modified:
  src/margpa_runtime_llm/modules/runtime_model_control/domain/errors.py
    （RuntimeModelContextLimitExceeded／RuntimeModelMaxNewTokensExceeded追加）
  src/margpa_runtime_llm/modules/runtime_model_control/application/runtime_model_controller.py
    （request_context_change()／set_max_new_tokens()追加）
Created:
  tests/unit/runtime_model_control/test_dynamic_context_and_tokens.py
```

## 実装内容（Architecture 5.1／5.2対応）

```text
request_context_change() : Same ModelをRequested ContextでReload（5.1）。
                            既存begin_switch()のUnload→Load→Commit/Rollback機構を、
                            target_definition=Current Modelとして再利用する設計とし、
                            新規Reload専用State Machineを別実装しない（重複回避）。
                            Effective Max（native／backend Context Limitのmin）超過は
                            Backendへ一切触れずに拒否（5.1「Context変更失敗で
                            RequestedをCurrent化0」を、そもそもBackend呼び出し前に
                            拒否することで保証）。
set_max_new_tokens()      : Atomic Runtime Override、Reload 0（5.2）。CAS検証のみで
                            即時Snapshot更新。max_output_token_limit超過は拒否。
                            Per-request Prompt Token／Governance／Safety Reserved控除
                            を含む実Request-time Validationは本WUの対象外（Generation
                            実行時の別Layerで行う、5.2式の後半部分は6-B-WU-006以降）。
```

## Validation

```text
New Unit Test  : 6 passed（Context Reload成功／Limit超過拒否／Reload失敗時Non-adoption、
                  Max New Tokens Atomic更新／Limit超過拒否／Stale CAS拒否）
Full Backend   : 1264 passed／3 deselected（既存1258 + 新規6、回帰0）
Ruff           : All checks passed
Mypy           : Success（9 source files）
```

## Next Exact Route

Phase 6-B-WU-006（Generation Identity／Compatibility：Turn／Attemptへの関連付け、
既存Conversation／RAG／Governance／Guardrail回帰確認）。ここから実際のbootstrap配線
（web_application.pyへのRuntimeModelController統合）に入るため、既存Production経路への
影響確認を伴う、より慎重なMaterial Stepとなる。
