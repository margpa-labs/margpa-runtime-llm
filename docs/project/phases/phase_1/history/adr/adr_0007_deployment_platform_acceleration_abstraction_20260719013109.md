# ADR-0007: Deployment／Platform／Acceleration Abstraction

- 文書ID: `adr_0007_deployment_platform_acceleration_abstraction`
- 状態: `accepted`
- 作成日時: `2026-07-19 01:31:09 JST`
- 更新日時: `2026-07-19 01:31:09 JST`
- 承認日時: `2026-07-19 01:31:09 JST`
- Snapshot: `20260719013109`
- Decision Owner: 設計者役担当Task
- 承認者: ユーザー
- 対象: Phase 1-C、Deployment Profile、Platform、Acceleration、Runtime Capability
- 正本言語: 日本語
- 要件: [phase_1c_deployment_platform_acceleration_requirements_20260719013109.md](../requirements/phase_1c_deployment_platform_acceleration_requirements_20260719013109.md)
- Architecture: [phase_1c_deployment_platform_acceleration_architecture_20260719013109.md](../architecture/phase_1c_deployment_platform_acceleration_architecture_20260719013109.md)
- 関連ADR: [adr_0006_model_runtime_port_and_configuration_20260718224308.md](adr_0006_model_runtime_port_and_configuration_20260718224308.md)
- supersedes: なし（ADR-0006をPlatform観点で拡張・一部修正する新規Decision）

## Status Decision

ユーザーは、Windows専用Hookではなく、OS、CPU Architecture、GPU／NPU Vendor、Acceleration API、Backend Adapter、Artifact VariantおよびLocal／Remote Topologyを分離する汎用Phase 1-C方針を承認した。

本ADRを`accepted`とする。

本ADRのAccepted化はSource実装、Config変更、Dependency変更、Native Buildまたは外部環境操作を自動的に解禁しない。

## Context

Phase 1-BはModel Port、llama.cpp Adapter、TOML ProfileおよびCurrent Mac／Metal Runtimeを成立させた。

一方、`gpu_offload`がModel Required Capabilityへ含まれ、Current Mac Deploymentの条件がModel固有条件として扱われている。

将来候補には次が存在する。

- macOS／Metal／MLX／MPS
- Windows／CPU／CUDA／HIP／Vulkan／DirectML
- Linux／CPU／CUDA／ROCm／Vulkan／SYCL
- Home Server／LAN Remote
- Cloud／vLLM／GPU／TPU／AWS Neuron
- Single GPU／Multi-GPU／Multi-Node
- GGUF／Safetensors／MLX／ONNX等のArtifact Variant

これらを全実装することは初期MVPのScopeを超える。

しかし、WindowsとMacだけの閉じたSchemaにすると、Home ServerまたはCloud追加時に再設計が必要になる。

## Decision

### 1. Phase名

```text
Phase 1-C：Deployment／Platform／Acceleration Abstraction Hook
```

とする。

### 2. 全環境の実装ではなく全環境を表現できる境界

Phase 1-Cでは、全OS／全Hardware／全Backendを実装しない。

現在のMac以外を後から追加できる最小Contract、Profile Schema、Resolver HookおよびValidation境界を作る。

### 3. Model CapabilityとDeployment Requirementの分離

`gpu_offload`はQwen3-4B Model自体の必須能力ではない。

Model Registry上ではOptionalまたはRuntime Capabilityとして扱い、Current macOS Metal ProfileがRequiredとする。

ADR-0006のPhase 1-B Required Capability一覧に含まれる`gpu_offload`は、Phase 1-C以降、Deployment Required Capabilityとして再分類する。

その他のPhase 1-B Decisionは維持する。

### 4. Orthogonal Dimension

次を独立軸として扱う。

- Host OS
- Architecture
- Execution Environment
- Compute Kind
- Hardware Vendor
- Acceleration API
- Memory Topology
- Backend Adapter
- Backend Build Variant
- Model Artifact Variant
- Execution Topology
- Required／Detected／Executed Capability

### 5. Extensible Identifier

Vendor、BackendおよびAcceleration APIを全世界分の閉じたEnumへ固定しない。

形式ValidationされたString KeyとDefinition／Registryにより拡張可能にする。

### 6. Profile Resolution

```text
Explicit指定
  > Environment指定
  > Platform Default Resolver
```

の優先順位を採用する。

未対応PlatformをCurrent Mac Profileへ黙ってFallbackしない。

### 7. Verification State

設計、実装、Static Verification、Native Verificationを分離する。

Phase 1-C完了時点でも、Current Mac以外を実機検証済みと主張しない。

### 8. Current Scope

Phase 1-CはCurrent Mac ProfileのMigration、Contract、Resolver Hook、Capability分離、TestおよびRegressionまでとする。

Windows／Linux Profile、Native Setup、CUDA／ROCm／Vulkan Build等はHardware決定後に追加する。

## Reasons

- Current Mac固定条件の上位層への伝播を早期に止められる
- 未所有Hardware向けのSpeculative Implementationを避けられる
- Home ServerやCloudをWindowsの特殊例として扱わずに済む
- Model、Artifact、Backend、Hardwareを独立交換できる
- Governance／AuditへRequired／Detected／Executed Stateを正確に渡せる
- 未対応環境を誤ってSupport済みと表示しない

## Consequences

### Positive

- Phase 2以降をMacで進めてもPlatform追加時の変更を局所化できる
- CPU ProfileとGPU Profileが同じModel Definitionを共有できる
- CUDA、ROCm、Vulkan等をProfile／Build Variantとして追加できる
- Remote Model AdapterとLocal Adapterを同じ上位境界へ接続できる
- Logical ModelとArtifact Variant分離へ発展可能になる

### Negative／Cost

- Profile SchemaとRuntime ContractのFieldが増える
- Current Mac ProfileのMigrationが必要になる
- Capability ValidationがModelとDeploymentの二段階になる
- Platform Keyの自由度と誤記防止の両立が必要になる
- Device ObservationはBackendごとの差を吸収する必要がある

### Risk Mitigation

- Phase 1-Cに必要な最小Fieldだけ実装する
- 全候補Backend用の空Classや空Directoryを作らない
- 未検証Profileを作らない
- Current Mac RegressionをAcceptance Gateとする
- Observation不能値を推測しない
- Unknown Keyの形式と参照整合をValidationする

## Alternatives Considered

### Windows専用ProfileとPowerShellだけを今追加する

短期的には分かりやすいが、Linux、Home Server、Cloud、CUDA、ROCm等で同じ再設計が必要になるため不採用。

### 全Platformを今実装する

未所有Hardware、Driver、OS、Backend Buildを検証できず、MVP Scopeと保守Costを拡大するため不採用。

### Current MacのままPhase最後まで進み、後で全修正する

Model CapabilityとDeployment Requirementの誤分類がUI、AuditおよびGovernanceへ伝播するRiskがあるため、最小Hookだけは今作る。

### VendorとAccelerationを閉じたEnumにする

型安全性は高いが、新Hardware／Plugin追加ごとにCore Releaseが必要になるため不採用。

### すべて自由文字列にする

誤記と参照不整合を検出できないため不採用。形式ValidationとDefinition参照を組み合わせる。

## Acceptance

本ADRはAcceptedである。

実装は、次を満たした後に開始する。

1. 実装担当が最新Index、本ADR、Requirements、ArchitectureおよびHandoffを読む
2. ユーザーがPhase 1-C実装開始を明示する
3. `src/`、`tests/`、`config/`、必要な`pyproject.toml`等のWrite Scopeを確認する
4. Current Mac Regressionおよび実Model／Metal Test実行許可を確認する

Decision変更時は本Fileを編集せず、新Timestampまたは新ADRを作成する。

