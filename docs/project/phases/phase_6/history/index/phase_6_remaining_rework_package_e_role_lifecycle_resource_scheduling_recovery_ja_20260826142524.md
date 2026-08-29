# Phase 6 Remaining Rework — Package E Recovery

```yaml
document_id: phase_6_remaining_rework_package_e_role_lifecycle_resource_scheduling_recovery_20260826142524
status: package_complete_next_active
package: P6-RR-E
completed_wus: [P6-RR-E-WU-001, P6-RR-E-WU-002, P6-RR-E-WU-003, P6-RR-E-WU-004, P6-RR-E-WU-005, P6-RR-E-WU-006, P6-RR-E-WU-007]
created_at: 2026-08-26 14:25:24 JST
next_exact_work_unit: P6-RR-F-WU-001
```

## Result

- Role Adapter Factory／Adapter／Resource Gate Portと、Dedicated Guard／Judge Adapterの所有権を持つ`RoleProviderLifecycleManager`を実装した。Main Lifecycleは既存`RuntimeModelController`所有として分離した。
- ActivationはConfigured Providerを固定してPreflight→Loading→Load→Commitする。Load失敗時はPrevious Adapterを再Loadし、失敗原因とConfigured／Active差分を保持する。別Providerへの暗黙Fallbackは0。
- Mode OFFのDeactivateはActive Turnがあれば`active_turn_drain_pending`としてUnloadを延期し、Lease終了後にLazy Unloadする。Switch中Active Turn、Shutdown中ActivationをRejectする。
- Resource Gate denial、Preflight unavailable、Load／Rollback／Unload failureを`unavailable／failed／degraded`へ分離し、False Active／False Cleanを防ぐ。
- Judge Mode RouteはSelected ProviderがACTIVEへCommitした後だけMode変更する。Unavailable ProviderではHTTP 409 Typed FailureとしJudge ModeをOFFに保持する。Guardrail Configuration Applyにも同じActivation Gateを接続した。
- Web CompositionはProvider Selection／Lifecycle／Semantic Contextを結線した。Project Root外Artifactを自動TraverseしないUnavailable Factoryを既定境界に置き、Dedicated ProviderをMain-selfへFallbackしない。
- Existing `ModelAccessCoordinator`のMain priority、Background／Switch Lease、Cancel、Auxiliary Evidence I/O separationを再利用し、Role Lifecycle側はActive Turn Leaseを追加した。

## Changed Source／Test

- `src/margpa_runtime_llm/modules/runtime_model_control/ports.py`
- `src/margpa_runtime_llm/modules/runtime_model_control/application/role_lifecycle_manager.py`
- `src/margpa_runtime_llm/modules/runtime_model_control/application/__init__.py`
- `src/margpa_runtime_llm/modules/runtime_model_control/application/provider_selection_controller.py`
- `src/margpa_runtime_llm/adapters/runtime_model_control/unavailable_role_adapters.py`
- `src/margpa_runtime_llm/bootstrap/configuration_control.py`
- `src/margpa_runtime_llm/bootstrap/web_application.py`
- `src/margpa_runtime_llm/web/contracts.py`
- `src/margpa_runtime_llm/web/feature_modes_routes.py`
- `src/margpa_runtime_llm/web/app.py`
- `tests/unit/runtime_model_control/test_role_lifecycle_manager.py`
- `tests/unit/runtime_model_control/test_model_definition_registry.py`
- `tests/integration/web/test_feature_modes_routes.py`

## Validation

```text
Runtime Model Control Unit + Feature Mode Web Integration: 58 passed / exit 0
Scoped Mypy: 58 source files PASS / exit 0
Scoped Ruff: PASS / exit 0
Earlier broad focused attempt: 269 passed / 1 expected-registry assertion FAIL;
  assertion was updated for the two authorized new Model Definitions and rerun PASS in the 58-test set
Integrated Backend Full: NOT RUN in Package E
Frontend: NOT RUN in Package E
Real Model: NOT RUN / Dedicated state remains Configured or Typed Unavailable
Browser: NOT RUN
```

Key SHA-512:

```text
role_lifecycle_manager.py:
84637d13dce52e9f6c973f92b452d61900202366ed76fc2ca554488ef80f09410a3085da9f274c2566707066205dba68cc0c39d533423ce33862559b99664a3d
unavailable_role_adapters.py:
74e29a42978dd652b7769c5fa3551137c646da7e8e6fd0d9bad45fa29bd87323586fb214c211f0521a709739015560fa3bb06c9b3ef79964a0d0bcd723cb4fdc
```

## Acceptance／Finding

```text
P6-RR-ACC-013: PASS / Startup Dedicated Load 0
P6-RR-ACC-014: CURRENT PASS for activation transaction and Typed Unavailable; Real Load NOT RUN
P6-RR-ACC-015: PASS by failure/rollback regression; implicit fallback 0
P6-RR-ACC-016: PASS by Active Turn Drain/Lazy Unload regression
P6-RR-ACC-017: CURRENT PASS for lifecycle/controller race contracts; Integrated real backend race NOT RUN
open_critical: 0
open_major: Dedicated production inference adapter/runtime binding remains F/G
open_non_critical: Current deployment defaults Dedicated Artifact access to Typed Unavailable
```

## Authority／Incident Inventory

```text
current package root_outside/provider_memory/runtime_data/git/network/model_mutation: 0/0/0/0/0/0
historical P6-RR-INC-001 root-outside action: 1 retained
P6-RR-ACC-039: FAIL retained
active_process: 0
loaded_model_by_this_task: none
task_owned_temp: .venv/.t/phase_6_remaining_rework_claude_20260826093407/
claims_not_made: Dedicated Real Load PASS, Integrated Full PASS, Browser PASS, Phase 6 Closure, Phase 7 Ready
```

`next_exact_work_unit: P6-RR-F-WU-001`
