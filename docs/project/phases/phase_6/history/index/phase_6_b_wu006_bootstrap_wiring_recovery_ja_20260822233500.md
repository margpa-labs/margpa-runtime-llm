# Phase 6-B-WU-006 Generation Identity／Bootstrap配線 Recovery Entry

```yaml
document_id: phase_6_b_wu006_bootstrap_wiring_recovery
status: current_recovery_entry
phase: phase_6
subphase: phase_6_b
work_unit: p6_b_wu006_complete_qwen_only
role: Claude側設計統括者役
long_running_mode_active: true
created_at: 2026-08-22 23:35:00 JST
```

## Exact Mutation

```text
Modified:
  src/margpa_runtime_llm/bootstrap/phase1_application.py
    （Phase1Applicationへadapter: LlamaCppModelAdapterフィールド追加。
      唯一の構築箇所（同ファイル内build_phase1_application）のみ更新。
      grep確認：他箇所でのPhase1Application(...)直接構築 0件）
  src/margpa_runtime_llm/bootstrap/web_application.py
    （runtime_model_control_enabled: bool = False 引数追加。
      Default Falseのため既存WebRuntime構築15+箇所は無影響）
  src/margpa_runtime_llm/web/contracts.py
    （WebRuntimeへ runtime_model_control: RuntimeModelController | None = None 追加。
      Optional・Default Noneのため既存Construction Call Site全て無影響）
  src/margpa_runtime_llm/adapters/runtime_model_control/llama_cpp_backend.py
    （_capability_digest → compute_capability_digest へRename、Bootstrap側から再利用可能に）
  tests/unit/runtime_model_control/conftest.py, test_runtime_model_domain.py, test_llama_cpp_backend.py
    （Pre-existing mypy軽微Issue3件を本WUのMypy Full Pass時に検出・修正：
      relative_pathへのstr誤代入、未使用type:ignore、無型注釈引数）
Created:
  src/margpa_runtime_llm/bootstrap/runtime_model_control.py
    （build_runtime_model_controller()：既存adapter再利用、実RuntimeInfoからInitial Snapshot構築）
  tests/unit/bootstrap/test_runtime_model_control_bootstrap.py
```

## 設計判断

```text
第二Adapter禁止        : Phase1ApplicationがLlamaCppModelAdapterを保持していなかったため、
                          新規Adapterを構築すると同一model_rootへ二重Bindが生じるRiskがあった。
                          Phase1Applicationへadapterフィールドを追加する最小変更で解消（第二
                          Adapter構築を回避）。
Opt-in Default False   : 既存WebRuntime Construction（Integration Test 15+箇所）を壊さないため、
                          runtime_model_control_enabled Flagおよび全Optionalフィールドとして追加。
Capability Digest共有化 : Adapter側とBootstrap側で同一Capability Digest計算式を重複実装せず、
                          compute_capability_digestとして公開・共用。
```

## Validation

```text
New Unit Test   : 2 passed（Bootstrap配線が実RuntimeInfoからInitial Snapshotを正しく構築、
                   Runtime Info未Load時のFail-closed）
Full Backend    : 1266 passed／3 deselected（既存1264 + 新規2、回帰0）
Frontend        : 175 passed（20 files、回帰0）
Ruff (repo全体) : All checks passed
Mypy (src+tests): Success — 338 source files（既存Pre-existing軽微Issue3件も本WUで解消）
```

## Next Exact Route

Phase 6-B-WU-007（Model Control Recovery：Subphase Test、Manual Load Evidence、Exact Mutation、Current Support StateをRecovery Entryへまとめる）を経て、Phase 6-C（Evaluation Domain／Deterministic Judge）へ進む。
