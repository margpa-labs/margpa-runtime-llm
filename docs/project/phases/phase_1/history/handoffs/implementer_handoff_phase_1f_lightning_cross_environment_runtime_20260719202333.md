# 実装担当向け Phase 1-F Lightning Cross-environment Runtime Handoff

- 文書ID: `implementer_handoff_phase_1f_lightning_cross_environment_runtime`
- 状態: `accepted_ready_for_user_start_instruction`
- 作成日時: `2026-07-19 20:23:33 JST`
- 更新日時: `2026-07-19 20:23:33 JST`
- Snapshot: `20260719202333`
- 作成担当: 設計者役担当Task
- 対象担当: 実装担当Task
- 正本言語: 日本語
- 要件: [phase_1f_lightning_cross_environment_runtime_requirements_20260719202333.md](../requirements/phase_1f_lightning_cross_environment_runtime_requirements_20260719202333.md)
- Architecture: [lightning_ai_studio_cross_environment_architecture_20260719202333.md](../architecture/lightning_ai_studio_cross_environment_architecture_20260719202333.md)
- ADR: [adr_0015_phase_1f_lightning_and_python_312_support_20260719202333.md](../adr/adr_0015_phase_1f_lightning_and_python_312_support_20260719202333.md)
- supersedes: `implementer_handoff_lightning_ai_studio_dual_runtime_profiles_20260719200711.md`

## 1. Objective

Phase 1公開前に、Mac 3.13／Metalを維持しながら、Lightning 3.12／CUDA Runtimeを同一Repositoryで成立させる。CPU Profileも実装対象とする。

## 2. Authorized Scope after User Start Instruction

```text
pyproject.toml
uv.lock
.python-version                 # 原則3.13.14維持。変更時は理由必須
config/
src/
tests/
scripts/
docs/handoffs/implementer_status_*
```

README／Public Docs／Git操作／GitHub操作はScope外である。

## 3. Work Packages

### WP-1 Python Compatibility

- `requires-python = ">=3.12,<3.14"`
- Lock再生成
- Ruff／Mypy最小Version 3.12
- 3.12／3.13 Dependency Resolution確認
- Mac Setup／Verifier Regression

### WP-2 Execution Environment

- Container Detection
- Platform Registry／Schema整合
- Native Mac互換性
- Pre-load Validation Test

### WP-3 CUDA Runtime

- CUDA Device Detection
- CUDA Profile
- Linux CUDA Setup Recipe
- Runtime Observation
- CUDA Unit／Native Smoke

### WP-4 CPU Runtime

- CPU Profile
- `gpu_layers=0`
- CUDA BuildによるCPU実行確認
- 不成立時はEvidenceをStatusへ記録し、別CPU Build案を提示

### WP-5 Acceptance Follow-up Coordination

- [implementer_handoff_phase_1_acceptance_follow_up_20260719195134.md](implementer_handoff_phase_1_acceptance_follow_up_20260719195134.md)のCLI Help／Token上限Warningを、同じMaterial Change Setまたは明確に分離したStatusで扱う。

## 4. Verification

Mac：

- Ruff／Mypy／Compileall
- Default Test
- Native Metal Smoke
- CLI User Test影響範囲

Lightning：

- Python 3.12.11
- Dependency／Lock
- Container Detection
- CUDA Build／System Info
- CUDA Profile Model Info
- Generate／Stream／Non-stream／Cancel／Unload
- Language／Thinking
- SHA-512
- CPU Profile Testまたは明示Finding

## 5. Status

実装完了時、新Timestampで最低限次を記録する。

```text
docs/handoffs/implementer_status_phase_1f_lightning_cross_environment_runtime_*.md
```

Mac／Lightningで実行したCommand、Version、Hardware、Build Option、Test結果、変更File、Known Limitation、CPU Dispositionを含める。

## 6. External Action Boundary

Repository変更は実装担当Taskで行う。Lightning上のPackage Install、CUDA Build、Model配置、GPU利用は外部環境操作であり、ユーザーがLightning側で実行するか、別途その操作を許可する。

## 7. Start Condition

本HandoffはAcceptedであり、ユーザーが実装担当TaskへPhase 1-F開始を明示した後に着手できる。
