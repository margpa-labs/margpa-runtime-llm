# Phase 6-G-WU-001 API Route Recovery Entry（Runtime Model Status）

```yaml
document_id: phase_6_g_wu001_api_route_recovery
status: current_recovery_entry
phase: phase_6
subphase: phase_6_g
work_unit: p6_g_wu001_backend_route_complete
role: Claude側設計統括者役
long_running_mode_active: true
created_at: 2026-08-23 00:25:00 JST
```

## 調査結果

```text
既存Pattern確認: runtime_governance_routes.pyのFactory不要引数Router、
                  Composition None→Safe Empty Response（200、enabled: false）、
                  web/app.py Lifespan Local-loopback Gateを完全再現。
```

## Exact Mutation

```text
Created:
  src/margpa_runtime_llm/web/runtime_model_control_routes.py
    （GET /api/v4/runtime-model/status、Main／Judge Model Identityのみ投影。
      Guard Model／Governance Layerは意図的に含めない——Route自体が
      guardrail_governance／governance_definitions Compositionへの
      Access Pathを持たないため）
  tests/integration/web/test_runtime_model_control_public_basic_call0.py
    （4 Test：Unbound Safe Degrade、Bound Snapshot投影、Non-local Exposure
      拒否×2 Policy）
Modified:
  src/margpa_runtime_llm/web/app.py
    （Import追加、Lifespan Local-loopback Gate追加（他5Compositionと同一Pattern）、
      include_router追加）
```

## Validation

```text
New Test       : 4 passed
Full Backend   : 1382 passed／3 deselected（回帰0）
Frontend       : 175 passed／20 files（回帰0）
Ruff／Mypy      : Clean（407 source files）
```

## 未実施

```text
Frontend側でのAPI消費（Sidebar Current Model表示、Advanced Settings Component
Identity表示）は未実施。Real Browser Verificationを伴うため次Batchで実施する。
```

## Next Exact Route

Frontend側でこの新規Endpointを消費するComponent実装（Sidebar／Advanced Settings）、
Real Browser Preview検証。
