# Phase 1-C Platform Registry参照整合 Follow-up実装状況

- 文書ID: `implementer_status_phase_1c_platform_registry_reference_integrity_follow_up`
- 状態: `implementation_complete_review_requested`
- 作成日時: `2026-07-19 03:45:23 JST`
- 更新日時: `2026-07-19 03:45:23 JST`
- 作成担当: 実装者役担当Task
- 対象: 設計者役担当Task
- 正本言語: 日本語
- Documentation Index: [documentation_index_20260719033038.md](../documentation_index_20260719033038.md)
- Designer Review: [designer_review_phase_1c_platform_registry_and_preload_validation_follow_up_20260719033038.md](designer_review_phase_1c_platform_registry_and_preload_validation_follow_up_20260719033038.md)
- Requirements: [phase_1c_deployment_platform_acceleration_requirements_20260719013109.md](../requirements/phase_1c_deployment_platform_acceleration_requirements_20260719013109.md)
- Architecture: [phase_1c_deployment_platform_acceleration_architecture_20260719013109.md](../architecture/phase_1c_deployment_platform_acceleration_architecture_20260719013109.md)
- Accepted ADR: [adr_0007_deployment_platform_acceleration_abstraction_20260719013109.md](../adr/adr_0007_deployment_platform_acceleration_abstraction_20260719013109.md)
- supersedes: [implementer_status_phase_1c_platform_registry_and_preload_validation_follow_up_20260719031938.md](implementer_status_phase_1c_platform_registry_and_preload_validation_follow_up_20260719031938.md)

## 1. 結論

Designer Review `20260719033038`で要求されたPlatform Registry参照整合Validationを実装した。

```text
OS Alias集合の非空Validation                    : Pass
Architecture Alias集合の非空Validation          : Pass
Default OS Canonical参照整合                   : Pass
Default Architecture Canonical参照整合         : Pass
Default Execution Environment参照整合          : Pass
Loader Safe Error Mapping                         : Pass
Current Registry／Future Alias／Unknown Fail-Closed    : Pass
Pre-load Validation                               : Pass
Static／Default／Metal Regression                   : Pass
```

Phase 1-Cの実装担当側Acceptance Criteriaは全件Passと判定し、最終Designer Reviewを依頼する。

## 2. 参照整合Validation

`PlatformRegistry`のPydantic Model Validationへ次を追加した。

1. `operating_system_aliases`が1件以上存在する
2. `architecture_aliases`が1件以上存在する
3. 各Defaultの`operating_system_key`がOS AliasのCanonical Key集合に存在する
4. 各Defaultの`architecture_key`がArchitecture AliasのCanonical Key集合に存在する
5. 各Defaultの`execution_environment_key`がRegistryの検出値と一致する

従来受理されていた次の参照は、Registry Load時に拒否される。

```text
macso／arm64／native
macos／arm65／native
macos／arm64／container
```

設定不備は後段の`profile_required`ではなく、Loader境界でSafeな`invalid_configuration`へ変換される。

## 3. Negative Test

追加したTest:

- OS Canonical参照不整合を拒否
- Architecture Canonical参照不整合を拒否
- Execution Environment参照不整合を拒否
- OS Alias空集合を拒否
- Architecture Alias空集合を拒否
- File Loaderが参照不整合をSafeな`invalid_configuration`へ変換

維持したTest:

- Current `platform_registry.toml` Parse
- Future OS／Architecture AliasとDefault Profile追加
- Unknown Platform Fail-Closed
- Explicit／Environment／Platform Default Priority
- Host／Fallback／Backend Pre-load Validation
- Host不一致時のAdapter／Model Port未呼出

## 4. 変更File

```text
M src/margpa_runtime_llm/bootstrap/profile_resolver.py
M tests/unit/inference/test_config_and_registry.py
A docs/handoffs/implementer_status_phase_1c_platform_registry_reference_integrity_follow_up_20260719034523.md
```

`config/platforms/platform_registry.toml`、`pyproject.toml`、`uv.lock`およびDependencyに変更はない。

## 5. Static／Default／Environment Gate

```text
Ruff Format Check          : Pass／51 files
Ruff Check                 : Pass
mypy --strict              : Pass／51 source files
compileall                 : Pass
bash -n Setup Recipe       : Pass
Default pytest             : 77 passed, 2 deselected
Environment Verification  : Pass
```

Environment:

```text
Python                    : CPython 3.13.14／arm64／GIL enabled
llama-cpp-python          : 0.3.34
GPU Offload Support       : true
Metal System Info         : present
Dependency Version Match  : true
Out-of-scope Package      : absent
```

## 6. Dependency Gate

```text
uv lock --check
  Resolved 117 packages

uv sync --dry-run --frozen --offline \
  --extra inference-llama \
  --group dev \
  --group notebook \
  --no-binary-package llama-cpp-python

  Checked 115 packages
  Would make no changes
```

## 7. Native Metal Regression

Sandbox外のNative Metal環境で実行した。

```text
.venv/bin/pytest -q -m model_smoke
  2 passed, 77 deselected
```

`model-info`:

```text
profile_resolution_source : platform_default
verification_state        : native_verified
backend                    : llama_cpp 0.3.34
device                     : gpu／metal
gpu_offload                : true
executed                   : null
artifact_digest_verified   : true
```

Production Acceptance:

```text
Success                         : true
Load including SHA-512          : 2.5619 seconds
Generation Result               : フェーズ1-B生産ランタイム成功
Generation Speed                : 29.86 tokens／second
Explicit Stream Terminal State  : cancelled
Post-cancel Generation          : OK／stop
Unload                          : 0.0703 seconds
Detected Device                 : gpu／metal
Detected GPU Offload            : true
Executed State                  : null
```

## 8. Hash／Dependency不変

```text
Platform Registry SHA-512:
5af43fff30e5cf0716a927e05d1bde74a443e5a0484490a32398421824e3b4cc0539f64578dcc509fe620790686d7473587d7650665f2436b4c988281712d574

pyproject.toml SHA-256:
a46fcd0b61e8db84a5f90ac4459b92bf9ec9deb7d6219ce88d7b22c240b5ecfa

uv.lock SHA-256:
e5efe33d69105547fe0d4f348b6b189b85f7ed55323f8ecd993ef5df7846fee1
```

## 9. Scope境界

未実装のままである。

- Windows／Linux実Profile
- CUDA／ROCm／Vulkan／MLX／Remote Backend
- 複数Execution Environment Alias／Detector
- Request単位のExecution Telemetry
- Response Language／Thinking Presentation
- Phase 2以降の機能

Native VerifiedはCurrent macOS／Apple Silicon arm64／Metalのみである。

## 10. 設計者への最終Review依頼

次を確認し、Phase 1-Cの最終受入を判定してほしい。

1. Alias集合の非空Validation
2. Default OS／Architecture Canonical参照整合
3. Default Execution Environment参照整合
4. LoaderのSafe Error Mapping
5. Current Registry／Future Alias／Unknown Fail-Closed Regression
6. Pre-load／Post-load Validation Regression
7. Static／Default／Native Metal Gate

