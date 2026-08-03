# Phase 1-C Platform Registry／Pre-load Validation Follow-up設計レビュー

- 文書ID: `designer_review_phase_1c_platform_registry_and_preload_validation_follow_up`
- 状態: `changes_requested_phase_1c_registry_reference_integrity`
- 作成日時: `2026-07-19 03:30:38 JST`
- 更新日時: `2026-07-19 03:30:38 JST`
- 作成担当: 設計者役担当Task
- 対象: 実装者役担当Task
- 正本言語: 日本語
- Documentation Index: [documentation_index_20260719033038.md](../documentation_index_20260719033038.md)
- Review対象: [implementer_status_phase_1c_platform_registry_and_preload_validation_follow_up_20260719031938.md](implementer_status_phase_1c_platform_registry_and_preload_validation_follow_up_20260719031938.md)
- Previous Review: [designer_review_phase_1c_deployment_platform_acceleration_follow_up_20260719030341.md](designer_review_phase_1c_deployment_platform_acceleration_follow_up_20260719030341.md)
- Requirements: [phase_1c_deployment_platform_acceleration_requirements_20260719013109.md](../requirements/phase_1c_deployment_platform_acceleration_requirements_20260719013109.md)
- Architecture: [phase_1c_deployment_platform_acceleration_architecture_20260719013109.md](../architecture/phase_1c_deployment_platform_acceleration_architecture_20260719013109.md)
- Accepted ADR: [adr_0007_deployment_platform_acceleration_abstraction_20260719013109.md](../adr/adr_0007_deployment_platform_acceleration_abstraction_20260719013109.md)
- supersedes: `designer_review_phase_1c_deployment_platform_acceleration_follow_up_20260719030341.md`

## 1. Review Conclusion

前回Reviewで要求した次の2件を受理する。

1. OS／Architecture AliasおよびPlatform DefaultのRegistry化
2. Host／Fallback／BackendのPre-load Validation

確認結果：

```text
Executed State意味境界              : Accepted／維持
OS／Architecture Alias拡張性       : Accepted
Platform Default拡張性              : Accepted
Unknown Platform Fail-Closed        : Accepted
Profile Resolution Priority         : Accepted
Host Pre-load Validation            : Accepted
Fallback Pre-load Validation        : Accepted
Backend Pre-load Validation         : Accepted
Host不一致時Adapter Constructor     : 0回
Host不一致時Model Port load()       : 0回
Static／Default／Metal Regression   : Pass
```

ただし、新しいPlatform Registryに参照整合上の未検出不備が1件ある。

`profile_defaults`が、Alias集合に存在しないCanonical OS／Architecture Keyまたは、Registryが検出する値と異なるExecution Environment Keyを参照しても、Registry Validationが成功する。

Current Mac Runtimeに影響する不具合ではなく、Unknown PlatformのFail-Closedも維持される。

一方、ADR-0007が要求する「Unknown Keyの形式と参照整合をValidationする」を満たしていないため、Phase 1-Cの最終受入はこの1件のFollow-up完了まで保留する。

```text
今回の主要Follow-up          : Accepted
新規重大不具合               : なし
Registry参照整合             : Changes Required
Phase 1-C Final Acceptance   : Pending
```

## 2. Review Scope

次を読取専用で確認した。

- 最新の実装担当Follow-up Status
- 前回Designer Review
- Phase 1-C Requirements／Architecture／ADR
- `config/platforms/platform_registry.toml`
- Platform Registry Contract／Loader／Resolver
- Pre-load／Post-load Validation
- Phase 1 Application Bootstrap
- Registry／Deployment Unit Test
- Static／Default／Environment Gate
- uv Lock／Offline Dry-run
- Native Metal Model Smoke
- CLI `model-info`
- Config／Lock Hash

Source、Config、Test、Scriptまたは既存Docsは変更していない。

本Reviewと同一TimestampのDocumentation Indexだけを、既存のユーザー許可に基づきAppend-Onlyで新規作成した。

## 3. Accepted: Platform Registry境界

### 3.1 Source Code外へ移動した情報

[platform_registry.toml](../../config/platforms/platform_registry.toml)が次を保持する。

```text
OS Raw Alias             → Canonical OS Key
Architecture Raw Alias   → Canonical Architecture Key
Execution Environment Key
Host Key                 → Default Profile Path
```

Current Definition：

```text
darwin／macos → macos
windows       → windows
linux         → linux

arm64／aarch64 → arm64
amd64／x86_64 → x86_64

macos／arm64／native
  → config/profiles/local_macos_arm64.toml
```

OS／Architecture AliasおよびDefault Profile追加時に、NormalizerまたはApplication CoreへOS別条件分岐を追加する必要はなくなった。

### 3.2 拡張性Test

Source Mappingを変更せず、Memory上で次を追加するTestを確認した。

```text
FutureOS 2371   → futureos
FutureArch 2371 → futurearch
futureos／futurearch／native
  → config/profiles/future.toml
```

Profile ResolverはFuture AliasをCanonical Keyへ変換し、Registry Defaultを選択できる。

Acceptance Criteria 6のOS／Vendor／Acceleration Key拡張性は、参照整合Follow-upを除く構造面で成立した。

### 3.3 Resolution Priority／Fail-Closed

次のPriorityを維持している。

```text
Explicit Profile
  > MARGPA_PROFILE
  > Platform Registry Default
```

未登録OS／Architecture AliasをmacOSとして推測しない。

登録済みAliasでもDefault Profileが存在しない場合は`profile_required`となる。

## 4. Accepted: Pre-load／Post-load Validation分離

### 4.1 Pre-load Validation

Native Adapter Constructorより前に次を検証する。

```text
Profile Host OS              vs Detected Host OS
Profile Architecture         vs Detected Architecture
Profile Execution Environment vs Detected Execution Environment
Fallback Policy              vs Implemented Policy
Profile Backend／Version     vs Model Definition Backend／Version
```

Host不一致時のUnit Testで次を確認した。

```text
Native Adapter Constructor : 0回
Model Port load()          : 0回
Artifact SHA-512           : 未実行
Native Model Load          : 未実行
Error                      : unsupported_platform
```

前回の「不一致判定前に約2.5GB ModelをHash／Loadする」問題は解消された。

### 4.2 Post-load Validation

Model Load後はDetected Stateを使用し、次を検証する。

```text
Detected Backend／Version
Detected Device Kind
Detected Acceleration API
Required Device／Acceleration
Required Capability
```

Capability不足時のUnloadとLifecycle回復を維持している。

Request実行証拠がないLoad Observationでは`executed=null`を維持する。

## 5. Required Follow-up: Platform Registry参照整合

### 5.1 Finding

`PlatformRegistry.validate_unique_entries()`は次を検証する。

- OS Raw Aliasの重複
- Architecture Raw Aliasの重複
- Default Host Keyの重複
- Canonical Keyの形式
- Default Profile Pathの相対Path安全性

しかし、Default Hostが参照するCanonical Keyの存在を検証していない。

設計者Taskで次のRegistry Objectを構築した。

```text
Known OS Alias Canonical           : macos
Known Architecture Alias Canonical : arm64
Registry Execution Environment     : native

Default OS                         : macso
Default Architecture               : arm65
Default Execution Environment      : container
```

`macso`、`arm65`および`container`は現在のRegistry Detectionから到達不能だが、Validationは成功した。

### 5.2 Impact

- Default Keyの誤記をRegistry Load時に検出できない
- 存在しているDefault ProfileがRuntime上は到達不能になる
- 設定不備が`invalid_configuration`ではなく、後段の`profile_required`として現れる
- Registry DefinitionとHost Detectionの参照整合が保証されない
- ADR-0007のRisk Mitigationを満たさない

誤ったDefaultへ暗黙Fallbackする動作ではないため、安全側のFail-Closed性は維持される。

### 5.3 Required Validation

最低限、Registry Load時に次を検証する。

1. `operating_system_aliases`が1件以上存在する
2. `architecture_aliases`が1件以上存在する
3. 各Defaultの`operating_system_key`がOS AliasのCanonical Key集合に存在する
4. 各Defaultの`architecture_key`がArchitecture AliasのCanonical Key集合に存在する
5. 各Defaultの`execution_environment_key`が現在検出可能なExecution Environmentと一致する

Current Schemaが単一の`execution_environment_key`を持つ間は、Default側の値がRegistry値と一致することを検証する。

将来、Native／WSL／VM／Containerを同時選択する段階では、Execution Environment Alias／Detectorを複数定義可能なRegistryへ拡張する。

### 5.4 Required Test

次のNegative Testを追加する。

- OS Canonical参照不整合を拒否する
- Architecture Canonical参照不整合を拒否する
- Execution Environment参照不整合を拒否する
- OS Aliasが空のRegistryを拒否する
- Architecture Aliasが空のRegistryを拒否する
- File Loaderが不整合をSafeな`invalid_configuration`へ変換する

Current `platform_registry.toml`のParse、Future Alias Test、Unknown Platform Fail-ClosedおよびMac Default Regressionを維持する。

## 6. Independent Verification Evidence

### 6.1 Static／Default／Environment

```text
Ruff Format Check          : Pass／51 files
Ruff Check                 : Pass
mypy --strict              : Pass／51 source files
Default pytest             : Pass／71 passed, 2 deselected
bash -n Setup Recipe       : Pass
Environment Verification  : Pass
Python                     : CPython 3.13.14／arm64
llama-cpp-python           : 0.3.34
GPU Offload Support        : true
Metal System Info          : present
Dependency Version Match   : true
Out-of-scope Package       : absent
```

実装担当Statusの件数と一致した。

### 6.2 Dependency Gate

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

前回要求した完全なOption列が最新Statusへ記録されている。

### 6.3 Native Metal Gate

Sandbox外のNative Metal環境で実行した。

```text
pytest -q -m model_smoke
  2 passed, 71 deselected
```

実CLI `model-info`：

```text
profile_resolution_source : platform_default
verification_state        : native_verified
backend                    : llama_cpp 0.3.34
device                     : gpu／metal
gpu_offload                : true
executed                   : null
artifact_digest_verified   : true
```

Platform Registry DefaultからCurrent Mac Profileを解決し、Model Load、Metal ObservationおよびUnloadに成功した。

Model SmokeにはProduction RuntimeのGeneration、Streaming、Cancel、Post-cancel GenerationおよびUnloadが含まれる。

### 6.4 Hash

報告書記載値と独立計算値が一致した。

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

## 7. Acceptance Criteria判定

| # | Acceptance Criteria | 判定 | 備考 |
|---:|---|---|---|
| 1 | Model DefinitionからDeployment固有のGPU必須を分離 | Pass | Model Optional、Mac Deployment Required |
| 2 | Mac Metal ProfileがGPU Offloadを要求 | Pass | GPU／Metalを明示 |
| 3 | RequiredとDetected Capabilityを比較 | Pass | Post-load Validation |
| 4 | 未対応Platformを暗黙にmacOS扱いしない | Pass | Unknown AliasはFail-Closed |
| 5 | Profile ResolverがTest可能 | Pass | Unit Testあり |
| 6 | 将来OS／Vendor／Acceleration Key追加にCore変更を必須としない | Pass with Follow-up | Registry境界は成立、参照整合を追加する |
| 7 | Tracked Configへユーザー固有絶対Pathを入れない | Pass | 相対Pathを維持 |
| 8 | Default／Static／Metal GateがPass | Pass | 独立再検証済み |
| 9 | macOS以外を`native_verified`と誤記しない | Pass | Mac／Metalのみ |
| 10 | Phase 2以降へ越境しない | Pass | Windows Profile等は未実装 |

## 8. 次回Follow-up Acceptance条件

実装担当は次を完了し、新TimestampのStatusを作成する。

1. Platform RegistryのCanonical参照整合Validationを追加する
2. Alias集合の空を拒否する
3. Execution Environment参照整合を検証する
4. 不整合RegistryをSafeな`invalid_configuration`へ変換する
5. 必要なNegative Testを追加する
6. Current Registry／Future Alias／Unknown Platform／Pre-load Validation Testを維持する
7. Static／Default／Environment Gateを通す
8. Native Metal Regressionを通す

このFollow-upはPlatform Registry ContractとTestの局所修正であり、Windows／Linux Profileまたは追加Backend実装を要求しない。

## 9. Scope／Authorization Boundary

本Reviewは、Platform Registry参照整合のFollow-up修正要求と受入条件を示す。

Source、Config、Test、ScriptまたはDependencyの変更を自動的に許可するものではない。

実装担当による追加修正は、ユーザーから明示的な実装許可と書込範囲が与えられた後に行う。

Windows／Linux実Profile、CUDA／ROCm／Vulkan／MLX／Remote Backend、Request単位のExecution Telemetry、Response Language／Thinking PresentationおよびPhase 2機能は、引き続きScope外とする。

