# ADR-0009: Application／Deployment Configuration Separation

- 文書ID: `adr_0009_application_deployment_configuration_separation`
- 状態: `accepted`
- 作成日時: `2026-07-19 04:18:47 JST`
- 更新日時: `2026-07-19 04:18:47 JST`
- 承認日時: `2026-07-19 04:18:47 JST`
- Snapshot: `20260719041847`
- Decision Owner: 設計者役担当Task
- 承認者: ユーザー
- 対象: Configuration Layer、Application Config、Deployment Profile、Phase 1-D
- 正本言語: 日本語
- Requirements: [configuration_layer_requirements_20260719041847.md](../requirements/configuration_layer_requirements_20260719041847.md)
- Architecture: [configuration_layer_architecture_20260719041847.md](../architecture/configuration_layer_architecture_20260719041847.md)
- 関連ADR: [adr_0006_model_runtime_port_and_configuration_20260718224308.md](adr_0006_model_runtime_port_and_configuration_20260718224308.md)
- 関連ADR: [adr_0007_deployment_platform_acceleration_abstraction_20260719013109.md](adr_0007_deployment_platform_acceleration_abstraction_20260719013109.md)
- 修正対象ADR: [adr_0008_response_language_policy_20260719040237.md](adr_0008_response_language_policy_20260719040237.md)
- supersedes: ADR-0008の`response.language`配置とProfile Schema更新理由を本ADRで修正する。その他のResponse Language Decisionは維持する

## Status Decision

ユーザーは、Platform ProfileからApplication共通設定を分離し、`config/application.toml`を共通設定の正本とする方針を承認した。

本ADRを`accepted`とする。

Source／Config／Test実装は、Phase 1-D実装開始の明示許可後に行う。

## Context

Current `local_macos_arm64.toml`には次が混在している。

- Selected Model
- Model Root
- Load Config
- Generation Config
- Host／Compute／Backend／Runtime Requirement

ADR-0008では`response.language`も同じProfileへ追加する案だった。

Linux、WindowsまたはCloud Profileを増やすと、Platformと無関係なGeneration／Response設定まで複製される。

これは単一責任、交換可能性および設定の一意な正本に反する。

## Decision

### 1. Common Application Config

次を新設する。

```text
config/application.toml
```

### 2. Application-owned Fields

- Selected Model
- Model Root
- Common Load Default
- Generation Default
- Response Language Default

### 3. Deployment-owned Fields

- Host／Architecture／Execution Environment
- Compute／Vendor／Acceleration
- Backend Runtime／Build Variant
- Runtime Requirements
- Hardware-dependent Load Override

### 4. Model-owned Fields

- Artifact／Hash／Format／Quantization
- Architecture／Native Limit
- Capability／Provenance

### 5. No Generic Deep Merge

型付きContractとSection別Resolverで合成する。

### 6. Schema

```text
Application Config Schema : 1
Deployment Profile Schema : 3
```

Deployment Schema更新理由はApplication Field除去と`load_overrides`導入である。

### 7. ADR-0008 Amendment

ADR-0008の次を修正する。

```text
Old : [response]をlocal_macos_arm64.tomlへ追加
New : [response]をconfig/application.tomlへ追加
```

ADR-0008の次は維持する。

- `ja／en／auto`
- Default `ja`
- Application／Orchestration Ownership
- Environment／CLI Override
- Phase 1-D／1-E分離

## Reasons

- Platform追加時に共通値を複製せずに済む
- Generation／Language変更を一つの正本で行える
- ModelとDeploymentを独立選択できる
- Hardware TuningだけをPlatform Profileへ閉じ込められる
- Configuration Driftを減らせる
- Sourceと責務をAuditで説明しやすい

## Consequences

### Positive

- Linux／Windows Profile追加が小さくなる
- Common Config変更が全Deploymentへ一貫して反映される
- Phase 1-D Language PolicyをPlatformから分離できる
- 将来Generation／Response Presetへ拡張できる

### Negative／Cost

- Config LoaderとEffective Config Composerの変更が必要
- Current ProfileのSchema Migrationが必要
- Application ConfigとDeployment Profileの複数Fileを読む必要がある
- Field別Precedence Testが増える

### Risk Mitigation

- ConfigごとにStrict Schemaを持つ
- Deployment OverrideをAllowlist化する
- Unknown Fieldを拒否する
- Migration前後のEffective Configを比較する
- Current Mac／Metal Native RegressionをGateにする

## Alternatives Considered

### Current Profileをそのまま複製する

Platform追加ごとに共通設定が複製され、Driftするため不採用。

### 一つの巨大`config.toml`へ全Platformを書く

責務と変更範囲が拡大し、Plugin／Profile交換性が下がるため不採用。

### 全Configを汎用Deep Mergeする

Field Owner、List規則、ValidationおよびProvenanceが曖昧になるため不採用。

### Model DefinitionへGeneration Defaultを移す

GenerationはTask／利用者Preferenceでもあり、Model固有事実と一致しないため初期正本にはしない。将来Model推奨Presetとして参照可能にする。

### Platform ProfileへResponse Languageを残す

OS変更で利用者の言語Preferenceが変化する不自然な設計になるため不採用。

## Acceptance

本ADRはAcceptedである。

実装担当は最新Requirements、Architecture、Phase 1-D後継文書およびHandoffを読み、ユーザーの実装許可後に着手する。

Decision変更時は本Fileを編集せず、新Timestampまたは新ADRを作成する。
