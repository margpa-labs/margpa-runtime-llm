# Phase 1-C Deployment／Platform／Acceleration Follow-up設計レビュー

- 文書ID: `designer_review_phase_1c_deployment_platform_acceleration_follow_up`
- 状態: `changes_requested_phase_1c_follow_up_partial_acceptance`
- 作成日時: `2026-07-19 03:03:41 JST`
- 更新日時: `2026-07-19 03:03:41 JST`
- 作成担当: 設計者役担当Task
- 対象: 実装者役担当Task
- 正本言語: 日本語
- Documentation Index: [documentation_index_20260719030341.md](../documentation_index_20260719030341.md)
- Review対象: [implementer_status_phase_1c_deployment_platform_acceleration_follow_up_20260719025250.md](implementer_status_phase_1c_deployment_platform_acceleration_follow_up_20260719025250.md)
- Initial Status: [implementer_status_phase_1c_deployment_platform_acceleration_20260719021411.md](implementer_status_phase_1c_deployment_platform_acceleration_20260719021411.md)
- Requirements: [phase_1c_deployment_platform_acceleration_requirements_20260719013109.md](../requirements/phase_1c_deployment_platform_acceleration_requirements_20260719013109.md)
- Architecture: [phase_1c_deployment_platform_acceleration_architecture_20260719013109.md](../architecture/phase_1c_deployment_platform_acceleration_architecture_20260719013109.md)
- Accepted ADR: [adr_0007_deployment_platform_acceleration_abstraction_20260719013109.md](../adr/adr_0007_deployment_platform_acceleration_abstraction_20260719013109.md)
- supersedes: なし（Phase 1-C Designer Review系列の初回文書）

## 1. Review Conclusion

Phase 1-C Follow-upで行われたRequired／Detected／Executed境界の修正を受理する。

Model Load直後の状態をRequest単位の`Executed State`として先取りする問題は解消された。

```text
Required State : Deployment Profileが保持
Detected State : Model Load後にBackend Adapterが観測
Executed State : Request単位の実行証拠が存在する場合だけ保持
```

Current Load Observationの正しい状態：

```text
detected.device_kind_key       : gpu
detected.acceleration_api_key  : metal
detected.gpu_offload           : true
executed                       : null
```

一方、前回の設計者Reviewで指摘した次の2件は未対応である。

1. 将来OS／Architecture追加時の拡張性
2. Profile Host不一致のLoad前拒否

したがって、今回のFollow-up修正は部分受入とし、Phase 1-C全体の最終受入は保留する。

```text
Executed State意味境界修正       : Accepted
Static／Default Regression       : Pass
実Model／Metal Regression         : Pass
将来OS／Architecture拡張性       : Changes Required
Host Pre-load Validation         : Changes Required
Phase 1-C Final Acceptance       : Pending
```

## 2. Review Scope

次を読取専用で確認した。

- 最新の実装担当Follow-up Status
- Phase 1-C Requirements／Architecture／ADR／Handoff
- Runtime Contract
- Profile Resolver
- Phase 1 Application Bootstrap
- Unit／CLI／Integration Test
- Static／Default／Environment Gate
- uv Offline Dry-run
- Native Metal Model Smoke
- CLI `model-info`
- Production Acceptance

Source、Config、Test、Scriptまたは既存Docsの変更は行っていない。

本Reviewと同一TimestampのDocumentation Indexだけを、ユーザーの既存許可に基づきAppend-Onlyで新規作成した。

## 3. Accepted Follow-up: Required／Detected／Executed境界

### 3.1 Contract

確認した変更：

- `DetectedRuntimeState`へ`gpu_offload`を追加
- `RuntimeObservation.executed`をOptional化
- `ExecutedRuntimeState`をRequest単位のEvidence用Contractとして維持
- Load Observation Builderで`executed=None`を設定

`ExecutedRuntimeState`の説明も、1件のInference Requestに対する実行証拠であることを明示している。

### 3.2 Deployment Validation

Load後のDeployment Ready判定は、Request未実行の`Executed State`ではなく`Detected State`を使用する。

比較対象：

```text
Backend Key／Version
Compute Kind
Acceleration API
Required Device Kind
Required Acceleration API
Required Capability
```

Request実行前の状態を実行事実として扱わないため、ARGD／DAGD、Auditおよび将来Telemetryへ誤った事実が伝播するRiskは解消された。

### 3.3 CLI／実Model

Native Metal環境で`model-info`を実行し、次を独立確認した。

```text
profile_resolution_source         : platform_default
verification_state                : native_verified
detected backend                  : llama_cpp 0.3.34
detected device                   : gpu
detected acceleration             : metal
detected gpu_offload              : true
executed                          : null
artifact_digest_verified          : true
```

Production Acceptanceでも、Generation、Streaming CancelおよびPost-cancel Generationの後に、Application Load Observationの`executed`は`null`を維持した。

これはRequest Telemetry未実装という現在の事実と一致する。

## 4. Required Follow-up 1: 将来OS／Architecture追加時の拡張性

### 4.1 Finding

`normalize_operating_system()`と`normalize_architecture()`は、Source Code内の固定Mappingである。

Current OS Mapping：

```text
darwin  → macos
windows → windows
linux   → linux
```

Current Architecture Mapping：

```text
arm64／aarch64 → arm64
amd64／x86_64 → x86_64
```

未知のOSまたはArchitectureでは、明示ProfileまたはEnvironment Profileが指定されていても、Profile選択前のHost Detectionで`unsupported_platform`となる。

また、Platform Defaultは`phase1_application.py`内で次の1件だけがSource Codeとして登録されている。

```text
macos／arm64 → local_macos_arm64.toml
```

### 4.2 Requirementとの関係

Phase 1-C Acceptance Criteria 6：

> 将来のOS／Vendor／Acceleration Key追加にCore変更を必須としない

VendorおよびAcceleration APIは拡張可能なString Keyとして成立している。

しかし、OS／Architectureの新規追加は現在もProfileまたはRegistry追加だけでは成立せず、NormalizerおよびDefault CompositionのSource変更を必要とする。

### 4.3 Required Direction

次の意味境界を維持しながら修正する。

- 未知PlatformをmacOSとして推測しない
- Default Profileが存在しない場合はFail-Closedとする
- Explicit／Environment／Platform DefaultのPriorityを維持する
- 正規化AliasとPlatform Default対応をConfig、Definitionまたは差し替え可能Registryへ分離する
- Application CoreへOS別条件分岐を増殖させない

実装方法は実装担当が現在の責務境界内で選択してよい。

## 5. Required Follow-up 2: Host不一致のLoad前拒否

### 5.1 Finding

Current Bootstrap Sequence：

```text
Profile Resolution
  ↓
Profile Load
  ↓
Model Definition Load
  ↓
Artifact SHA-512 Verification
  ↓
Native Model Load
  ↓
Host Profile Validation
```

検出済みHostとProfile HostはNative Model Load前に比較可能だが、現在はModel Load後の`validate_loaded_deployment()`で比較している。

Profile不一致時にも約2.5GBのArtifact検証とNative Backend初期化を行った後で拒否する構造である。

将来、Windows／Linux／CUDA／ROCm等のProfileを追加した場合、非互換なNative Buildまたは不要な高負荷処理を先に開始する可能性がある。

### 5.2 Required Direction

Validationを最低限、次の二段階へ分離する。

```text
Pre-load Validation
  Host OS
  Architecture
  Execution Environment
  Fallback Policyの実装可否
  ProfileとModel DefinitionのBackend整合

Post-load Validation
  Detected Backend／Version
  Detected Device Kind
  Detected Acceleration API
  Required Capability
```

Host不一致時はArtifact HashまたはNative Model Loadへ進まず、Safe ErrorでFail-Closedとする。

## 6. Verification Evidence

### 6.1 Static／Default／Environment

設計者Taskによる独立再検証：

```text
Ruff Format Check          : Pass／51 files
Ruff Check                 : Pass
mypy --strict              : Pass／51 source files
Default pytest             : Pass／67 passed, 2 deselected
bash -n Setup Recipe       : Pass
Environment Verification  : Pass
Python                     : CPython 3.13.14／arm64
llama-cpp-python           : 0.3.34
GPU Offload Support        : true
Metal System Info          : present
Dependency Version Match   : true
Out-of-scope Package       : absent
```

実装担当Statusの`mypy --strict : Pass／47 source files`は、設計者再実測の`51 source files`と一致しない。

検査結果自体はPassであり、Source不具合ではなくStatus上の軽微な件数誤記として扱う。

### 6.2 uv Dependency Gate

`uv lock --check`はPassした。

Offline Dry-runは、Setup Recipeと同じ完全なOptionを指定して確認した。

```text
uv sync --dry-run --frozen --offline \
  --extra inference-llama \
  --group dev \
  --group notebook \
  --no-binary-package llama-cpp-python
```

結果：

```text
Checked 115 packages
Would make no changes
```

実装担当Statusの`uv sync offline dry-run`という省略表記では、必要なExtra／Groupが読み手へ伝わらない。

次回Statusでは完全なCommandまたはSetup Recipeと同一Optionであることを明記する。

### 6.3 Native Metal Gate

Codex Sandbox内ではMetal Deviceを取得できないため、Native Metal GateをSandbox外で実行した。

```text
pytest -q -m model_smoke
  2 passed, 67 deselected
```

Production Acceptance：

```text
Success                         : true
Load including SHA-512          : 2.4746 seconds
Generation Result               : フェーズ1-B生産ランタイム成功
Generation Speed                : 30.22 tokens／second
Explicit Stream Terminal State  : cancelled
Post-cancel Generation          : OK／stop
Unload                          : 0.0436 seconds
Detected Device                 : gpu／metal
Detected GPU Offload            : true
Executed State                  : null
```

## 7. Acceptance Criteria判定

| # | Acceptance Criteria | 判定 | 備考 |
|---:|---|---|---|
| 1 | Model DefinitionからDeployment固有のGPU必須を分離 | Pass | Model Optional、Mac Deployment Required |
| 2 | Mac Metal ProfileがGPU Offloadを要求 | Pass | `gpu_offload`、GPU、Metalを明示 |
| 3 | RequiredとDetected Capabilityを比較 | Pass | Detected Stateで検証 |
| 4 | 未対応Platformを暗黙にmacOS扱いしない | Pass | UnknownはFail-Closed |
| 5 | Profile ResolverがTest可能 | Pass | Unit Testあり |
| 6 | 将来OS／Vendor／Acceleration Key追加にCore変更を必須としない | Changes Required | Vendor／AccelerationはPass、OS／Architectureは固定Mapping |
| 7 | Tracked Configへユーザー固有絶対Pathを入れない | Pass | 相対Model Rootを維持 |
| 8 | Default／Static／Metal GateがPass | Pass | 独立再検証済み |
| 9 | macOS以外を`native_verified`と誤記しない | Pass | Mac／Metalのみ |
| 10 | Phase 2以降へ越境しない | Pass | Telemetry等はDeferred |

Acceptance Criteria 6が未達であり、Host Pre-load Validationにも将来Platform接続前の修正が必要である。

## 8. 次回Follow-up Acceptance条件

実装担当は次を完了し、新TimestampのStatusを作成する。

1. OS／Architecture AliasまたはNormalizationの差し替え境界を実装する
2. Platform Default対応をSource固定から拡張可能なDefinition／Registry境界へ移す、または同等の拡張性を証明する
3. Unknown PlatformのFail-Closedを維持する
4. Explicit／Environment／Platform Default Priorityを維持する
5. Host／FallbackのPre-load Validationを追加する
6. Host不一致時にModel Portの`load()`が呼ばれないTestを追加する
7. Current Mac／Metal Regressionを通す
8. `mypy`対象件数とuv Offline Dry-runの完全なCommandをStatusへ正確に記録する

## 9. Scope／Authorization Boundary

本Reviewは、Phase 1-CのFollow-up修正要求と受入条件を示す。

Source、Config、Test、ScriptまたはDependencyの変更を自動的に許可するものではない。

実装担当による追加修正は、ユーザーから明示的な実装許可と書込範囲が与えられた後に行う。

Request単位のExecution Telemetry、Windows／Linux実Profile、CUDA／ROCm／Vulkan Backend、Response Language／Thinking PresentationおよびPhase 2機能は、引き続き本Follow-upのScope外とする。

