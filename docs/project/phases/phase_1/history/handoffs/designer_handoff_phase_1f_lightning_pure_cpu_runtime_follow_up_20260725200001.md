# Phase 1-F Lightning Pure CPU Runtime Follow-up 実装担当Handoff

- 文書ID: `designer_handoff_phase_1f_lightning_pure_cpu_runtime_follow_up`
- 状態: `accepted_ready_for_repository_implementation`
- 作成日時: `2026-07-25 20:00:01 JST`
- 更新日時: `2026-07-25 20:00:01 JST`
- Snapshot: `20260725200001`
- 作成担当: 設計者役担当Task
- 対象: 実装者役担当Task
- 正本言語: 日本語
- Requirements: [phase_1f_lightning_pure_cpu_runtime_follow_up_requirements_20260725200001.md](../requirements/phase_1f_lightning_pure_cpu_runtime_follow_up_requirements_20260725200001.md)
- Architecture: [phase_1f_lightning_pure_cpu_runtime_follow_up_architecture_20260725200001.md](../architecture/phase_1f_lightning_pure_cpu_runtime_follow_up_architecture_20260725200001.md)
- Accepted ADR: [adr_0022_lightning_pure_cpu_and_optional_component_hook_only_profile_20260725200001.md](../adr/adr_0022_lightning_pure_cpu_and_optional_component_hook_only_profile_20260725200001.md)
- Source Review: [designer_review_phase_1_mac_web_ui_user_acceptance_and_follow_up_20260725192903.md](designer_review_phase_1_mac_web_ui_user_acceptance_and_follow_up_20260725192903.md)
- supersedes: なし

## 1. Handoff Conclusion

FreshなLinux x86_64 CPU環境向けに、CUDA Toolchainを要求しないPure CPU Runtime HookをRepositoryへ追加する。

本HandoffはRepository実装だけを許可する。外部Studio起動、Upload、Dependency Installation、Model配置、Native Testは別Gateである。

## 2. Required Reading Order

1. 本Handoff
2. Requirements
3. Architecture
4. ADR-0022
5. Source Review
6. [adr_0015_phase_1f_lightning_and_python_312_support_20260719202333.md](../adr/adr_0015_phase_1f_lightning_and_python_312_support_20260719202333.md)
7. [documentation_index_20260725192903.md](../documentation_index_20260725192903.md)

## 3. Scope

```text
New Pure CPU Profile
New CPU Setup Script
CPU Preflight Mode／Script
Verification Target
Static／Unit／Integration Test
Repository Status Report
```

## 4. Locked Decisions

```text
Build Variant           : cpu
Execution Device        : cpu
Acceleration API        : none
GPU Layers              : 0
GPU Required            : no
NVIDIA Driver Required  : no
CUDA Required           : no
nvcc Required           : no
Model Download          : no
External Execution      : no
RAG Implementation      : no
```

## 5. Step A — Existing Contract Inventory

変更前に次のReferenceを列挙する。

- Existing CUDA Profile
- Existing CUDA Build CPU Execution Profile
- Profile Resolver
- Build Variant Contract
- Environment Verification Target
- Setup／Preflight Scripts
- Acceptance Script
- Tests

Existing CPU ProfileをRename／Deleteしない。

## 6. Step B — Pure CPU Profile

候補：

```text
config/profiles/lightning_linux_x86_64_cpu_native.toml
```

意味：

```text
Linux／x86_64／container
llama_cpp／cpu build
cpu device
no acceleration
gpu_layers=0
fallback deny
```

Profile Schemaに`none`等が未対応なら、CoreへProvider固有Hard-codeを入れず、Generic Contractとして追加する。

## 7. Step C — Setup

候補：

```text
scripts/setup/setup_lightning_linux_x86_64_cpu.sh
```

要件：

- Python 3.12／3.13 Support Range
- `llama-cpp-python==0.3.34`
- Pure CPU Build検証
- Reuse／Explicit Rebuild分離
- GPU Commandを呼ばない。
- `nvcc`を確認しない。
- Model Smokeは明示Option。
- Model不足時にDownloadしない。
- Idempotentに再実行可能。

## 8. Step D — Preflight／Verification

Preflight：

- OS／Architecture／Container
- Python／uv
- CPU／Memory
- Writable Path

Verification Target候補：

```text
lightning-cpu-native
```

Pass条件：

- build variant cpu
- device cpu
- acceleration none
- gpu offload false
- gpu layers 0

## 9. Step E — Test

- Profile Parse／Validation
- Explicit Resolution
- Wrong Host／Architecture
- CPU Build Observation
- CUDA Marker非Required
- Mac Profile Regression
- CUDA Profile Regression
- Script Syntax
- ScriptのGPU Command非依存
- Native Pending State

実際のModel GenerationをLocal MacでCPU Profileとして偽装しない。

## 10. Project Documentation Explainer

本Handoffでは実装しない。

将来Component追加後、Lightning CPU Profileでは次を満たす。

```text
hook present
enabled false
provider absent allowed
no index load
no retrieval
no additional model call
```

Mac Localでの有効化はPhase 1-ex後の別Handoffとする。

## 11. Candidate File Scope

Expected：

```text
config/profiles/lightning_linux_x86_64_cpu_native.toml
scripts/setup/setup_lightning_linux_x86_64_cpu.sh
scripts/setup/verify_phase1_environment.py
scripts/setup/preflight_lightning_ai_studio.sh or CPU-specific preflight
tests/unit/inference/
tests/integration/
docs/handoffs/implementer_status_phase_1f_pure_cpu_*
```

Conditional：

```text
src/margpa_runtime_llm/bootstrap/profile_resolver.py
src/margpa_runtime_llm/modules/inference/contracts/runtime.py
config/platforms/platform_registry.toml
```

Do Not Change：

```text
Mac Profile
CUDA GPU Profile semantics
Model Port
Web UI
RAG
Model Artifact
pyproject dependency versions
```

## 12. Required Report

`docs/handoffs/implementer_status_phase_1f_pure_cpu_runtime_follow_up_YYYYMMDDHHMMSS.md`

必須内容：

- Changed Files
- Existing CPU Profile disposition
- Pure CPU Build detection
- Commands
- Static／Unit／Integration Result
- External Native Test Pending
- No External Operation
- Known Limitation

## 13. Stop Conditions

- Pure CPUをCUDA Buildとして申告する必要がある。
- CPU ProfileがGPU Commandを必須にする。
- Existing Mac／CUDA Contractを壊す。
- External EnvironmentなしではPassを偽装する必要がある。
- Model Downloadが必要になる。

上記の場合は実装を拡大せずStatusへ戻す。
