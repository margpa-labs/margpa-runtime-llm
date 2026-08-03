# 実装担当向け Lightning AI Studio Dual Runtime Profiles Handoff

- 文書ID: `implementer_handoff_lightning_ai_studio_dual_runtime_profiles`
- 状態: `waiting_future_phase_authorization`
- 作成日時: `2026-07-19 20:07:11 JST`
- 更新日時: `2026-07-19 20:07:11 JST`
- Snapshot: `20260719200711`
- 作成担当: 設計者役担当Task
- 対象担当: 実装担当Task
- 正本言語: 日本語
- 要件: [lightning_ai_studio_dual_runtime_profile_requirements_20260719200711.md](../requirements/lightning_ai_studio_dual_runtime_profile_requirements_20260719200711.md)
- Architecture: [lightning_ai_studio_cross_environment_architecture_20260719200711.md](../architecture/lightning_ai_studio_cross_environment_architecture_20260719200711.md)
- supersedes: なし（新規Handoff系列）

## 1. Objective

Lightning AI Studio上で、同一Application Core／Model Contractを使い、CUDAとCPUを明示Profileで交換可能にする。

## 2. Planned Files／Scopes

実装開始時に、現行構造を再確認して最小範囲を確定する。

```text
config/profiles/lightning_linux_x86_64_cuda.toml
config/profiles/lightning_linux_x86_64_cpu.toml
config/platforms/platform_registry.toml             # 必要なSchema／Entry
src/.../bootstrap/profile_resolver.py                # Container Detection
src/.../adapters/model_backends/llama_cpp/           # CUDA Detection
scripts/setup/                                       # Linux CUDA／CPU Recipe
tests/                                               # Unit／Native Smoke
docs/handoffs/implementer_status_*
```

ConfigはConditional Write Scopeであり、ユーザーの当該Phase実装許可後に変更する。

## 3. Required Implementation

1. Linux x86_64 Docker Containerを正確に検出する。
2. Mac Native Detectionを壊さない。
3. CUDA／CPU ProfileをSchema 3で作る。
4. Profileは初期`defined`とし、Evidenceなしに`native_verified`としない。
5. llama.cppのCUDA実行を`gpu／cuda／gpu_offload=true`として検出する。
6. `gpu_layers=0`を`cpu／cpu_native／gpu_offload=false`として検出する。
7. GPU未割当時のCUDA ProfileはSafe Failureとし、暗黙CPU Fallbackしない。
8. Explicit CPU ProfileでCPU実行を確認する。
9. CUDA-enabled BuildをCPU Profileでも使用できるか先に検証し、失敗時だけBuild Environmentを分ける。
10. Mac Test、Linux Unit、CUDA Smoke、CPU Smoke、Model Digestを記録する。

## 4. Known Current Limitations

- Execution EnvironmentがRegistryの`native`固定。
- Current Device DetectorはMetal以外をCPU扱いする。
- Platform Default KeyだけではCUDA／CPUを自動選択できない。
- `fallback_policy = explicit_fallback`は未実装である。

## 5. Out of Scope

- Arbitrary Linux Hardwareの完全自動Router
- Windows Profile
- ROCm／Vulkan
- vLLM／Transformers Adapter
- ZeroGPU
- UIからのProfile自動切替
- RuntimeによるNative Package自動再Install

## 6. Authorization Boundary

本Handoffは将来実装用である。現在のPhase 1受入Follow-up、Config変更、Lightning Install／Build、GPU利用、Model転送を開始しない。ユーザーの明示的なPhase開始指示を待つ。
