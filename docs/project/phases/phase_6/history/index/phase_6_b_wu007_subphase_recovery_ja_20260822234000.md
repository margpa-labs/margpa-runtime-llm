# Phase 6-B Subphase Recovery（WU-007：Model Control Recovery）

```yaml
document_id: phase_6_b_subphase_recovery
status: current_recovery_entry
phase: phase_6
subphase: phase_6_b
work_unit: p6_b_wu007_complete
role: Claude側設計統括者役
long_running_mode_active: true
created_at: 2026-08-22 23:40:00 JST
```

## Subphase Test集計

```text
runtime_model_control関連 New Unit Test: 30 passed
  Domain (WU-001)            : 12
  Registry／BusyGate／Backend (WU-002): 12
  Dynamic Context／Tokens (WU-004/005): 6
Bootstrap配線 New Unit Test (WU-006)   : 2
Full Backend Suite合計                  : 1266 passed／3 deselected（回帰0）
Frontend Suite                          : 175 passed／20 files（回帰0）
Ruff／Mypy                               : 全体Clean
```

## Manual Load Evidence

```text
実Qwen GGUF Loadを伴うEnd-to-end Test: 未実施（model_smoke Marker、既定Deselect）。
runtime_model_control_enabled Flagは既定Falseで、既存WebRuntime経路への影響0を
Full Regression（1266 passed）で確認済み。実Hardware Manual Loadは6-I Real Browser
Golden Pathで実施する。
```

## Exact Mutation（本Subphase累計）

```text
Created: src/margpa_runtime_llm/modules/runtime_model_control/**
         src/margpa_runtime_llm/adapters/runtime_model_control/**
         src/margpa_runtime_llm/bootstrap/runtime_model_control.py
         tests/unit/runtime_model_control/**, tests/unit/bootstrap/test_runtime_model_control_bootstrap.py
Modified: src/margpa_runtime_llm/bootstrap/phase1_application.py（adapter field追加）
          src/margpa_runtime_llm/bootstrap/web_application.py（Opt-in配線追加）
          src/margpa_runtime_llm/web/contracts.py（Optional Field追加）
Git Mutation: 0
```

## Current Support State

```text
Qwen  : Runtime Model Control経由でSnapshot／Switch／Context／Token機構が実装され、
        実LlamaCppModelAdapterへ配線済み（Opt-in、Default OFF）。
DeepSeek: CURRENT_TOOLCHAIN_UNSUPPORTED／NOT EXECUTED（P6-A、CONTROLLER_OWNED_FOLLOWUP）。
          Model Definition未登録。Switch機構自体はFakeで汎用検証済み（WU-003 Status Determination）。
```

## Next Exact Route

Phase 6-C（Evaluation Domain／Deterministic Judge）、P6-C-WU-001（Evaluation Domain／Ports）へ進む。
