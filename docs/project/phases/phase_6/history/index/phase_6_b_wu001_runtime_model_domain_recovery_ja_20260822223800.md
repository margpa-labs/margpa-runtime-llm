# Phase 6-B-WU-001 Runtime Model Domain／Ports Recovery Entry

```yaml
document_id: phase_6_b_wu001_runtime_model_domain_recovery
status: current_recovery_entry
phase: phase_6
subphase: phase_6_b
work_unit: p6_b_wu001_complete
role: Claude側設計統括者役
provider: claude_code
long_running_mode_active: true
created_at: 2026-08-22 22:38:00 JST
```

## Exact Mutation

```text
Created:
  src/margpa_runtime_llm/modules/runtime_model_control/__init__.py
  src/margpa_runtime_llm/modules/runtime_model_control/domain/__init__.py
  src/margpa_runtime_llm/modules/runtime_model_control/domain/identifiers.py
  src/margpa_runtime_llm/modules/runtime_model_control/domain/canonicalization.py
  src/margpa_runtime_llm/modules/runtime_model_control/domain/snapshot.py
  src/margpa_runtime_llm/modules/runtime_model_control/domain/errors.py
  src/margpa_runtime_llm/modules/runtime_model_control/ports.py
  src/margpa_runtime_llm/modules/runtime_model_control/application/__init__.py
  src/margpa_runtime_llm/modules/runtime_model_control/application/runtime_model_controller.py
  tests/unit/runtime_model_control/__init__.py
  tests/unit/runtime_model_control/conftest.py
  tests/unit/runtime_model_control/test_runtime_model_domain.py
  tests/unit/runtime_model_control/test_runtime_model_controller.py
Modified: なし（既存Source無変更）
```

## 実装内容（Architecture 3.1-3.3対応）

```text
RuntimeModelSnapshot   : revision／digest_sha512／selected_model_key／role_bindings／
                          artifact_identity・digest／backend_identity／runtime_state／
                          loaded_context_size／各Context Limit／current_max_new_tokens／
                          last_transition_receipt（Architecture 3.1に1:1対応、ImmutableContract）
RoleBinding            : role／model_identity／artifact_digest／backend_identity／
                          binding_state／independence_class／capability_digest（3.3対応）
TransitionReceipt      : transition_id／from_revision／to_model_key／outcome／
                          started_at・completed_at／failure_reason
CAS                    : RuntimeModelController.begin_switch()がexpected_revision／
                          expected_digestを検証し、不一致でRuntimeModelRevisionConflict
Busy Gate              : GenerationBusyGatePort.has_active_generation()で
                          Active Generation中はRuntimeModelBusyErrorとしIdle-only Switchを強制
Switch Transaction     : Unload → Candidate Load → 成功時Atomic Commit（Revision+1、
                          Digest再計算）／失敗時Previous ReceiptへのRollback
Rollback Failure       : Rollback自体も失敗した場合はUnavailableへ遷移し、
                          不明な旧値を推測復元しない（Architecture 3.2の明示要件）
```

## Ports（WU-002でAdapter実装予定、本WUはProtocol定義のみ）

```text
ModelBackendPort            : probe_capability／load／unload
GenerationBusyGatePort      : has_active_generation
ModelDefinitionResolverPort : resolve（model_key→ModelDefinition、Rollback時の
                               Definition再取得に必要。Snapshotからの再構成は
                               不可能なため独立Portとして設計）
```

## Validation

```text
New Unit Test        : 12 passed（Domain Contract 7件、Controller CAS／Busy／Switch／
                        Rollback／Double-failure-to-Unavailable 5件）
Full Backend Test     : 1248 passed／3 deselected（既存1236 + 新規12、回帰0）
Ruff                  : All checks passed
Mypy (src)            : Success — 9 source files（新規Module分）
```

## Next Exact Route

Phase 6-B-WU-002（Backend Adapter／Model Definition：Qwen／DeepSeekを同じPortへ登録）。
DeepSeek側はP6-A-WU-002のPre-tokenizer Blocker解消（User／Controller判断待ち）まで、
Model Definition自体は登録可能だがLoad実証は不可。Qwen側から先に進める。
