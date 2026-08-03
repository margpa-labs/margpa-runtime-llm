# Phase 1-F Lightning Cross-environment Runtime要件

- 文書ID: `phase_1f_lightning_cross_environment_runtime_requirements`
- 状態: `accepted_ready_for_implementation`
- 作成日時: `2026-07-19 20:23:33 JST`
- 更新日時: `2026-07-19 20:23:33 JST`
- Snapshot: `20260719202333`
- 作成担当: 設計者役担当Task
- Decision Owner: ユーザー
- 対象: Python 3.12／3.13、Lightning Linux Container、CUDA必須、CPU候補
- 正本言語: 日本語
- ADR: [adr_0015_phase_1f_lightning_and_python_312_support_20260719202333.md](../adr/adr_0015_phase_1f_lightning_and_python_312_support_20260719202333.md)
- Architecture: [lightning_ai_studio_cross_environment_architecture_20260719202333.md](../architecture/lightning_ai_studio_cross_environment_architecture_20260719202333.md)
- Handoff: [implementer_handoff_phase_1f_lightning_cross_environment_runtime_20260719202333.md](../handoffs/implementer_handoff_phase_1f_lightning_cross_environment_runtime_20260719202333.md)
- supersedes: `lightning_ai_studio_dual_runtime_profile_requirements_20260719200711.md`

## 1. Objective

Phase 1公開前に、同一Repository、Application Core、Model Definition、Qwen3-4B GGUFを用いて次を成立させる。

```text
Mac       : CPython 3.13.14／macOS arm64／Metal
Lightning : CPython 3.12.11／Ubuntu 24.04 Container／Linux x86_64／CUDA
Lightning : CPython 3.12.11／Ubuntu 24.04 Container／Linux x86_64／CPU候補
```

## 2. Python Support

Project Metadata候補：

```toml
requires-python = ">=3.12,<3.14"
```

要件：

- Macの`.python-version = 3.13.14`をPrimary Defaultとして維持してよい。
- Lightning SetupはPython 3.12.11を明示選択する。
- `uv.lock`はPython 3.12／3.13の両方を解決可能とする。
- Pinned Direct Dependency Versionは、両Versionで解決できる限り維持する。
- Ruff TargetとMypy Python Versionは、最小Supportである3.12のSyntax／Typingを検査する。
- Mac 3.13とLightning 3.12でDefault Testを実行する。
- Platform固有Environment Verificationが他PlatformのPython Patchを誤拒否しない構造にする。
- Python 3.11以下はSupport対象外とする。

## 3. Lightning Profiles

必須：

```text
config/profiles/lightning_linux_x86_64_cuda.toml
```

Best Effort／期限管理対象：

```text
config/profiles/lightning_linux_x86_64_cpu.toml
```

Profile意味は、前身Dual Profile要件を継承する。

- CUDA: `gpu／nvidia／cuda／gpu_layers=-1／fallback=deny`
- CPU: `cpu／cpu_native／gpu_layers=0／fallback=deny`
- Host: `linux／x86_64／container／ubuntu`
- Hardware SKUはProfile名へ固定しない。
- 初期版はExplicit `--profile`で選択する。

## 4. Required Code／Configuration Changes

1. Python Support RangeとLockを3.12／3.13へ拡張する。
2. Ruff／Mypy／Setup／Verificationを最小Python 3.12とPlatform差へ整合させる。
3. Container Execution Environmentを検出する。
4. Mac Native Detectionを維持する。
5. llama.cpp CUDA Build／Executionを検出する。
6. CPU実行をCUDA実行と分離して申告する。
7. CUDA ProfileとCPU Profileを追加する。
8. Linux CUDA Build Recipeを追加する。
9. 可能ならLinux CPU Recipeまたは同一CUDA BuildのCPU Modeを成立させる。
10. Model RootをLightningのPersistent StorageからEnvironmentで指定できるよう維持する。
11. Metal固有Test Marker／Help／VerifierをCross-environment構造へ整理する。

## 5. Phase 1-F Mandatory Gate

必須合格条件：

- Mac Python 3.13.14の既存Default／Metal TestがPassする。
- Lightning Python 3.12.11でProject Install／Syncが成立する。
- Lightning Default TestがPassする。
- Lightning CUDA Buildが成立する。
- CUDA ProfileでQwen3-4BをLoadできる。
- `device_kind=gpu`、`acceleration_api=cuda`、`gpu_offload=true`を観測する。
- SHA-512がMacの同一Model Artifactと一致する。
- Generate、Streaming、Non-streaming、Cancel、Unloadが成立する。
- Response Language／Thinking Presentationの主要Contractが成立する。
- GPU未割当時にCUDA ProfileがCPUへ黙ってFallbackしない。
- Environment、Profile、Backend、Model、Test EvidenceをStatusへ記録する。

## 6. CPU Gate

CPU Profileは実装対象とするが、次の2段階で扱う。

### Preferred

- CUDA-enabled Buildのまま`gpu_layers=0`でCPU実行できる。
- GPU未割当状態でもImport／Load／Generateできる。
- CPU Observationが正しい。

### Deadline-safe Alternative

同一Environmentで成立せず、別Native Build／Environmentが公開期限を大きく圧迫する場合：

- CPU Profile候補、失敗Evidence、必要なFollow-upを記録する。
- CUDA RuntimeをPhase 1-F必須Gateとして先に完了できる。
- CPU対応を未実装のまま「対応済み」と主張しない。
- 延期判断は実装担当が独断で行わず、設計者Reviewとユーザー承認で確定する。

## 7. Publication Gate

Phase 1-F完了後に次を行う。

1. Mac／Lightning User Manual更新
2. Phase 1 Cross-environment Final Review
3. ユーザー受入テスト
4. 設計者のPhase 1完了・次Phase移行可能宣言
5. Phase 1 Backup
6. Public README、Setup、License、Model取得手順、Known Limitations
7. Secret、実Log、Model Binary、Local Path、Credentialの除外確認
8. ユーザーの明示許可後にGit／GitHub公開操作

## 8. Out of Scope

- Web UI／Live Demo URL
- Multi-turn Conversation
- Runtime Governance本実装
- Guard／Judge／Agent
- Arbitrary Linux Hardware Auto-router
- Windows Native Runtime
- ROCm／Vulkan
- GPU Quotaを検知したRuntime自動Fallback

## 9. Authorization Boundary

本要件は実装開始可能な設計正本である。実装担当TaskがSource／Config／Lock／Tests／Scriptsを変更するには、ユーザーから当該Handoffへの開始指示を受ける。Lightning上のInstall、Build、Model配置、GPU利用はLightning側で別途実行する。
