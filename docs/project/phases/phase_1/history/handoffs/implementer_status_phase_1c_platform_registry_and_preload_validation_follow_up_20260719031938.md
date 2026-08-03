# Phase 1-C Platform Registry／Pre-load Validation Follow-up実装状況

- 文書ID: `implementer_status_phase_1c_platform_registry_and_preload_validation_follow_up`
- 状態: `implementation_complete_review_requested`
- 作成日時: `2026-07-19 03:19:38 JST`
- 更新日時: `2026-07-19 03:19:38 JST`
- 作成担当: 実装者役担当Task
- 対象: 設計者役担当Task
- 正本言語: 日本語
- Documentation Index: [documentation_index_20260719030341.md](../documentation_index_20260719030341.md)
- Designer Review: [designer_review_phase_1c_deployment_platform_acceleration_follow_up_20260719030341.md](designer_review_phase_1c_deployment_platform_acceleration_follow_up_20260719030341.md)
- Requirements: [phase_1c_deployment_platform_acceleration_requirements_20260719013109.md](../requirements/phase_1c_deployment_platform_acceleration_requirements_20260719013109.md)
- Architecture: [phase_1c_deployment_platform_acceleration_architecture_20260719013109.md](../architecture/phase_1c_deployment_platform_acceleration_architecture_20260719013109.md)
- Accepted ADR: [adr_0007_deployment_platform_acceleration_abstraction_20260719013109.md](../adr/adr_0007_deployment_platform_acceleration_abstraction_20260719013109.md)
- supersedes: [implementer_status_phase_1c_deployment_platform_acceleration_follow_up_20260719025250.md](implementer_status_phase_1c_deployment_platform_acceleration_follow_up_20260719025250.md)

## 1. 結論

Designer Review `20260719030341`のChanges Requestedを実装した。

```text
Executed State意味境界             : 既存修正を維持
OS／Architecture Alias拡張性     : Pass
Platform Default拡張性              : Pass
Unknown Platform Fail-Closed            : Pass
Profile Resolution Priority             : Pass
Host Pre-load Validation                : Pass
Fallback Pre-load Validation            : Pass
Profile／Model Backend Pre-load Validation: Pass
Host不一致時Model Port Load呼出し       : 0回
Static／Default／Metal Regression       : Pass
Phase 2以降への越境                    : なし
```

Phase 1-Cの実装担当側Acceptanceは全件Passと判定し、最終Designer Reviewを依頼する。

## 2. Platform Registry

新規Tracked Definition:

[platform_registry.toml](../../config/platforms/platform_registry.toml)

Registryは次をSource Code外で保持する。

```text
OS Raw Alias              → Canonical OS Key
Architecture Raw Alias    → Canonical Architecture Key
Execution Environment Key
Host Key                  → Default Profile Path
```

Current Definition:

```text
darwin／macos → macos
windows       → windows
linux         → linux

arm64／aarch64 → arm64
amd64／x86_64 → x86_64

macos／arm64／native
  → config/profiles/local_macos_arm64.toml
```

AliasまたはDefault Profile追加はRegistry Definitionの追加で表現でき、NormalizerまたはApplication CoreのOS別分岐追加を必須としない。

Future OS／Architecture／Default ProfileをRuntimeで組み立て、Source Mapping修正なしで解決できるUnit Testを追加した。

## 3. Registry Validation

Platform Registryは次を検証する。

- TOML Syntax
- Unknown Field拒否
- Alias Raw Valueの正規化
- Canonical Keyの形式
- Alias重複拒否
- Default Host Key重複拒否
- Default Profile Pathの絶対Path／`..`拒否

Unknown OS／ArchitectureをmacOSへ推測しない。

Known AliasでもDefault Profileが存在しない場合は`profile_required`となる。

## 4. Profile Resolution Priority

既存Priorityを維持した。

```text
Explicit Profile
  > MARGPA_PROFILE
  > Platform Registry Default
```

Host DetectionはRegistry Aliasを使用する。未登録AliasはExplicit／Environment Profile指定時もFail-Closedとなるが、新PlatformはRegistry追加で認識可能になる。

## 5. Pre-load／Post-load Validation分離

### Pre-load Validation

Native Adapter生成より前に次を検証する。

```text
Profile Host OS              vs Detected Host OS
Profile Architecture         vs Detected Architecture
Profile Execution Environment vs Detected Execution Environment
Fallback Policy              vs Implemented Policy
Profile Backend／Version     vs Model Definition Backend／Version
```

不一致時はSafe ErrorでFail-Closedとする。

Host不一致Testで次を確認した。

```text
Native Adapter Constructor : 0回
Model Port load()          : 0回
Artifact SHA-512           : 未実行
Native Model Load          : 未実行
Error                      : unsupported_platform
```

### Post-load Validation

Model Load後はDetected Stateを使用し、次だけを検証する。

```text
Detected Backend／Version
Detected Device Kind
Detected Acceleration API
Required Device／Acceleration
Required Capability
```

Capability不足時のUnload／Lifecycle回復を維持した。

## 6. Required／Detected／Executed

前Follow-upで受理された意味境界を維持した。

```text
Required : Deployment Profile
Detected : Load後のBackend Adapter Observation
Executed : Request単位のEvidenceがある場合のみ
```

Current `model-info`:

```text
detected.device_kind_key      : gpu
detected.acceleration_api_key : metal
detected.gpu_offload          : true
executed                      : null
```

## 7. 変更File

### Source／Config

```text
A config/platforms/platform_registry.toml
M src/margpa_runtime_llm/bootstrap/profile_resolver.py
M src/margpa_runtime_llm/bootstrap/phase1_application.py
```

### Test

```text
M tests/unit/inference/test_deployment_platform.py
M tests/unit/inference/test_config_and_registry.py
```

### Handoff

```text
A docs/handoffs/implementer_status_phase_1c_platform_registry_and_preload_validation_follow_up_20260719031938.md
```

`pyproject.toml`、`uv.lock`およびDependencyに変更はない。

## 8. Static／Default／Environment Gate

```text
Ruff Format Check          : Pass／51 files
Ruff Check                 : Pass
mypy --strict              : Pass／51 source files
compileall                 : Pass
bash -n Setup Recipe       : Pass
Default pytest             : 71 passed, 2 deselected
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

## 9. Dependency Gate

Lock Check:

```text
uv lock --check
```

Result:

```text
Resolved 117 packages
```

Setup Recipeと同一OptionのOffline Dry-run:

```text
uv sync --dry-run --frozen --offline \
  --extra inference-llama \
  --group dev \
  --group notebook \
  --no-binary-package llama-cpp-python
```

Result:

```text
Checked 115 packages
Would make no changes
```

## 10. Native Metal Regression

Sandbox外のNative Metal環境で実行した。

```text
.venv/bin/pytest -q -m model_smoke
  2 passed, 71 deselected
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
Load including SHA-512          : 2.5733 seconds
Generation Result               : フェーズ1-B生産ランタイム成功
Generation Speed                : 30.78 tokens／second
Explicit Stream Terminal State  : cancelled
Post-cancel Generation          : OK／stop
Unload                          : 0.0506 seconds
Detected Device                 : gpu／metal
Detected GPU Offload            : true
Executed State                  : null
```

## 11. Config／Lock Hash

```text
Platform Registry SHA-512:
5af43fff30e5cf0716a927e05d1bde74a443e5a0484490a32398421824e3b4cc0539f64578dcc509fe620790686d7473587d7650665f2436b4c988281712d574

Model Definition SHA-512:
2a1d3951b56dba2514fd4c37161dbea8048e80efc1ac9a8672f4a7f1f5d2c6aa3e3aaace7216b522dd2c1627fb30d676a80d7a761881f039f2337983d510f4be

Local Mac Profile SHA-512:
a2ccc4525223c6c04c2d91114699d7d850bb8092829b3bdc3ce02698e94ee0c943af789c94b10a3332bf97f245950f263211bf9ed818c5f3ca4c451f57cfd77c

pyproject.toml SHA-256:
a46fcd0b61e8db84a5f90ac4459b92bf9ec9deb7d6219ce88d7b22c240b5ecfa

uv.lock SHA-256:
e5efe33d69105547fe0d4f348b6b189b85f7ed55323f8ecd993ef5df7846fee1
```

## 12. Verification State／Scope

Native Verified:

```text
macOS／Apple Silicon arm64／Metal : native_verified
```

Windows／Linux AliasはRegistryに定義したが、Default ProfileとNative Verificationは追加していない。

未実装:

- Windows／Linux実Profile
- CUDA／ROCm／Vulkan／MLX／Remote Backend
- Request単位のExecution Telemetry
- Response Language／Thinking Presentation
- Phase 2以降の機能

## 13. 設計者へのReview依頼

次の最終Reviewを依頼する。

1. OS／Architecture AliasのDefinition境界
2. Platform Default ProfileのRegistry境界
3. Unknown Platform Fail-Closed
4. Explicit／Environment／Platform Default Priority
5. Host／Fallback／Backend Pre-load Validation
6. Host不一致時にAdapter／Model Port Loadが呼ばれないこと
7. Post-load Detected Capability Validation
8. Current Mac／Metal Regression
9. Phase 1-C Acceptance Criteria 6の完了判定

