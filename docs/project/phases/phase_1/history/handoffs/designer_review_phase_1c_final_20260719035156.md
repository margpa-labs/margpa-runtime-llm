# Phase 1-C Deployment／Platform／Acceleration 最終設計レビュー

- 文書ID: `designer_review_phase_1c_final`
- 状態: `accepted_phase_1c_complete`
- 作成日時: `2026-07-19 03:51:56 JST`
- 更新日時: `2026-07-19 03:51:56 JST`
- 作成担当: 設計者役担当Task
- 対象: 実装者役担当Task
- 正本言語: 日本語
- Documentation Index: [documentation_index_20260719035156.md](../documentation_index_20260719035156.md)
- Review対象: [implementer_status_phase_1c_platform_registry_reference_integrity_follow_up_20260719034523.md](implementer_status_phase_1c_platform_registry_reference_integrity_follow_up_20260719034523.md)
- Previous Review: [designer_review_phase_1c_platform_registry_and_preload_validation_follow_up_20260719033038.md](designer_review_phase_1c_platform_registry_and_preload_validation_follow_up_20260719033038.md)
- Initial Phase 1-C Review: [designer_review_phase_1c_deployment_platform_acceleration_follow_up_20260719030341.md](designer_review_phase_1c_deployment_platform_acceleration_follow_up_20260719030341.md)
- Requirements: [phase_1c_deployment_platform_acceleration_requirements_20260719013109.md](../requirements/phase_1c_deployment_platform_acceleration_requirements_20260719013109.md)
- Architecture: [phase_1c_deployment_platform_acceleration_architecture_20260719013109.md](../architecture/phase_1c_deployment_platform_acceleration_architecture_20260719013109.md)
- Accepted ADR: [adr_0007_deployment_platform_acceleration_abstraction_20260719013109.md](../adr/adr_0007_deployment_platform_acceleration_abstraction_20260719013109.md)
- supersedes: `designer_review_phase_1c_platform_registry_and_preload_validation_follow_up_20260719033038.md`

## 1. Review Conclusion

Phase 1-C Deployment／Platform／Acceleration Abstraction Hookを最終受入し、完了と判定する。

前回までのRequired Follow-upはすべて完了した。

```text
Required／Detected／Executed意味境界        : Pass
Model Capability／Deployment Requirement分離: Pass
OS／Architecture Alias Registry            : Pass
Platform Default Registry                   : Pass
Platform Registry参照整合                   : Pass
Unknown Platform Fail-Closed                : Pass
Profile Resolution Priority                 : Pass
Host／Fallback／Backend Pre-load Validation : Pass
Detected Capability Post-load Validation    : Pass
Current Mac／Metal Regression               : Pass
```

重大、中程度または軽微な未解決不具合は、今回のReview Scopeでは確認されなかった。

Phase 1-CのDeployment Contract、Platform Registry、Profile Resolver、Pre-load／Post-load Validation、Runtime ObservationおよびCurrent macOS／Metal Runtimeは、次段階の基盤として利用できる。

本ReviewはPhase 1-C完了を示す。次Phaseの設計または実装を自動的に解禁するものではない。

## 2. Follow-up履歴

Phase 1-C実装後、設計者Reviewで次を段階的に確認・修正した。

### 2.1 Required／Detected／Executed境界

初期実装では、Model Load時のDevice観測値をRequest単位の`Executed State`として記録していた。

修正後：

```text
Required : Deployment Profileが保持
Detected : Model Load後にBackend Adapterが観測
Executed : Request単位の実行証拠がある場合のみ保持
```

Current Load Observation：

```text
detected.device_kind_key       : gpu
detected.acceleration_api_key  : metal
detected.gpu_offload           : true
executed                       : null
```

Request Telemetry未実装の状態で実行事実を推測しない境界が成立した。

### 2.2 Platform Registry／Pre-load Validation

OS／Architecture AliasとPlatform DefaultをSource Code内の固定MappingからTracked Registryへ移動した。

Host、Fallback PolicyおよびProfile／Model Backend整合をNative Adapter生成前に検証する。

Host不一致時：

```text
Native Adapter Constructor : 0回
Model Port load()          : 0回
Artifact SHA-512           : 未実行
Native Model Load          : 未実行
Error                      : unsupported_platform
```

Model Load後はDetected Backend／Device／Acceleration／Capabilityだけを検証する。

### 2.3 Platform Registry参照整合

Platform Registryへ次のValidationを追加した。

1. OS Alias集合が1件以上存在する
2. Architecture Alias集合が1件以上存在する
3. Default OS KeyがOS AliasのCanonical Key集合に存在する
4. Default Architecture KeyがArchitecture AliasのCanonical Key集合に存在する
5. Default Execution EnvironmentがRegistryの検出値と一致する

従来受理されていた次の到達不能参照は拒否される。

```text
macso／arm64／native
macos／arm65／native
macos／arm64／container
```

設定不備はLoader境界でSafeな`invalid_configuration`へ変換される。

## 3. Platform Registry最終確認

### 3.1 Current Tracked Definition

[platform_registry.toml](../../config/platforms/platform_registry.toml)は次を保持する。

```text
darwin／macos → macos
windows       → windows
linux         → linux

arm64／aarch64 → arm64
amd64／x86_64 → x86_64

macos／arm64／native
  → config/profiles/local_macos_arm64.toml
```

Windows／Linux Aliasは定義されているが、Default ProfileまたはNative Verificationは追加していない。

### 3.2 Extensibility

新しいOS／Architecture AliasおよびPlatform Defaultは、Registry Definitionの追加で表現できる。

NormalizerまたはApplication CoreへOS別条件分岐を追加する必要はない。

Future Alias／DefaultをMemory上で追加するUnit TestがPassした。

### 3.3 Validation

確認した項目：

- TOML Syntax
- Unknown Field拒否
- Alias Raw Value正規化
- Canonical Key形式
- Alias集合非空
- Raw Alias重複拒否
- Default Host Key重複拒否
- Default Canonical参照整合
- Default Execution Environment参照整合
- Default Profile Pathの絶対Path／`..`拒否
- Loader Safe Error Mapping

ADR-0007の「形式Validation、必須Fieldおよび参照整合を厳格に行う」を満たす。

## 4. Profile Resolution／Validation最終確認

### 4.1 Resolution Priority

```text
Explicit Profile
  > MARGPA_PROFILE
  > Platform Registry Default
```

未知OS／ArchitectureをmacOSとして推測しない。

Known AliasでもDefault Profileが存在しない場合は`profile_required`となる。

### 4.2 Pre-load Validation

```text
Profile Host OS              vs Detected Host OS
Profile Architecture         vs Detected Architecture
Profile Execution Environment vs Detected Execution Environment
Fallback Policy              vs Implemented Policy
Profile Backend／Version     vs Model Definition Backend／Version
```

不一致時はNative Adapterを生成せず、Safe ErrorでFail-Closedとする。

### 4.3 Post-load Validation

```text
Detected Backend／Version
Detected Device Kind
Detected Acceleration API
Required Device Kind
Required Acceleration API
Required Capability
```

Capability不足時はRuntimeをUnloadし、Lifecycleを回復する。

## 5. Independent Verification Evidence

### 5.1 Static／Default／Environment

```text
Ruff Format Check          : Pass／51 files
Ruff Check                 : Pass
mypy --strict              : Pass／51 source files
Default pytest             : Pass／77 passed, 2 deselected
bash -n Setup Recipe       : Pass
Environment Verification  : Pass
Python                     : CPython 3.13.14／arm64
llama-cpp-python           : 0.3.34
GPU Offload Support        : true
Metal System Info          : present
Dependency Version Match   : true
Out-of-scope Package       : absent
```

### 5.2 Reference Integrity Reproduction

設計者Taskで、OS=`macso`、Architecture=`arm65`、Execution Environment=`container`の到達不能Defaultを持つRegistry Objectを再構築した。

修正前はValidationが成功したが、修正後はPydantic `ValidationError`で拒否された。

```text
validation_rejected
default profile references an unknown operating system key
```

OS、Architecture、Execution Environmentの個別Negative Testと、File Loader Safe Error TestもPassした。

### 5.3 Dependency Gate

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

### 5.4 Native Metal Gate

Sandbox外のNative Metal環境で実行した。

```text
pytest -q -m model_smoke
  2 passed, 77 deselected
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

Platform Registry DefaultからCurrent Mac Profileを解決し、Model Load、Generation、Streaming、Cancel、Post-cancel GenerationおよびUnloadが成立した。

### 5.5 Hash

報告書記載値と独立計算値が一致した。

```text
Platform Registry SHA-512:
5af43fff30e5cf0716a927e05d1bde74a443e5a0484490a32398421824e3b4cc0539f64578dcc509fe620790686d7473587d7650665f2436b4c988281712d574

pyproject.toml SHA-256:
a46fcd0b61e8db84a5f90ac4459b92bf9ec9deb7d6219ce88d7b22c240b5ecfa

uv.lock SHA-256:
e5efe33d69105547fe0d4f348b6b189b85f7ed55323f8ecd993ef5df7846fee1
```

## 6. Acceptance Criteria最終判定

| # | Acceptance Criteria | 判定 | 備考 |
|---:|---|---|---|
| 1 | Model DefinitionからDeployment固有のGPU必須を分離 | Pass | Model Optional、Mac Deployment Required |
| 2 | Mac Metal ProfileがGPU Offloadを要求 | Pass | GPU／Metalを明示 |
| 3 | RequiredとDetected Capabilityを比較 | Pass | Post-load Validation |
| 4 | 未対応Platformを暗黙にmacOS扱いしない | Pass | Unknown AliasはFail-Closed |
| 5 | Profile ResolverがTest可能 | Pass | Unit／Negative Testあり |
| 6 | 将来OS／Vendor／Acceleration Key追加にCore変更を必須としない | Pass | Registry／String Key境界が成立 |
| 7 | Tracked Configへユーザー固有絶対Pathを入れない | Pass | 相対Pathを維持 |
| 8 | Default／Static／Metal GateがPass | Pass | 独立再検証済み |
| 9 | macOS以外を`native_verified`と誤記しない | Pass | Mac／Metalのみ |
| 10 | Phase 2以降へ越境しない | Pass | Scope外機能は未実装 |

全Acceptance CriteriaがPassした。

## 7. Deferred／Non-blocking Items

次はPhase 1-C最終受入を妨げない後続事項である。

- Windows／Linux実Profile
- CUDA／ROCm／Vulkan／MLX／Remote Backend
- 複数Execution Environment Alias／Detector
- Request単位のExecution Telemetry／Audit
- Runtime Device Name／IDの追加観測
- llama.cpp Build VariantのNative APIによる直接観測
- Logical Model／Artifact Variantの全面分離
- Response Language／Thinking Presentation
- Phase 2以降の機能

これらを実装・検証済みとは主張しない。

## 8. Phase 1-C完了状態

```text
Phase 1-A Environment                         : Complete／Accepted
Phase 1-B Model Runtime                       : Complete／Accepted
Phase 1-C Deployment／Platform／Acceleration  : Complete／Accepted
Current Native Verification                  : macOS／Apple Silicon arm64／Metal
```

Phase 1-C完了により、将来Deploymentの追加時に利用する最小Contract、Registry、Resolver、ValidationおよびObservation境界が成立した。

## 9. Scope／Authorization Boundary

本ReviewはPhase 1-Cの最終受入と完了を示す。

次PhaseのRequirements作成、設計、Source実装、Config変更またはDependency追加を自動的に許可するものではない。

次の作業は、ユーザーが議題と実施範囲を決定した後に開始する。

