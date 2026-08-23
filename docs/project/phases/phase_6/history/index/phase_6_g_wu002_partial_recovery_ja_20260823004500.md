# Phase 6-G-WU-002 Advanced Component Identity（Main／Judge部分） Recovery Entry

```yaml
document_id: phase_6_g_wu002_partial_recovery
status: current_recovery_entry
phase: phase_6
subphase: phase_6_g
work_unit: p6_g_wu002_partial_main_and_judge_only
role: Claude側設計統括者役
long_running_mode_active: true
created_at: 2026-08-23 00:45:00 JST
```

## Exact Mutation

```text
Created:
  src/margpa_runtime_llm/modules/runtime_observability/projection/component_identity_projection.py
  tests/unit/runtime_observability/test_component_identity_projection.py（4 Test）
Modified: なし
Git Mutation: 0
```

##範囲と意図的な未実施

```text
実施済み: Current Main Model Identity、Current LLM-as-a-Judge Model Identity
          （runtime_model_control Snapshot + judge_role_resolverの合成）。
          ComponentIdentityState（None／Unavailable／Invalid／Loading／Degraded／Active）
          をP6-ACC-056どおり区別。
未実施　: Current Guardrail Model Identity、Current Governance Layer Identity。
          既存Phase 4/5のguardrail_governance／governance_definitions Moduleの正確な
          Contract形状を未再検証のまま実装すると捏造Riskがあるため、意図的に保留した
          （「未実測事項をPASSと捏造しない」原則を本Projectionにも適用）。
```

## Validation

```text
New Unit Test  : 4 passed
Full Backend   : 1366 passed／3 deselected（回帰0）
Frontend       : 175 passed／20 files（回帰0）
Ruff／Mypy      : Clean（400 source files）
```

## Next Exact Route

Phase 6-G-WU-002残り（Guardrail Model／Governance Layer Identity、既存Module正確な
再調査後に実装）、Phase 6-G-WU-001（Sidebar Current Model）、または6-E-WU-003
（Repair Orchestrator実配線）のいずれかへ進む。
