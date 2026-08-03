# Phase 1-C Deployment／Platform／Acceleration 実装Follow-up状況

- 文書ID: `implementer_status_phase_1c_deployment_platform_acceleration_follow_up`
- 状態: `implementation_complete_review_requested`
- 作成日時: `2026-07-19 02:52:50 JST`
- 更新日時: `2026-07-19 02:52:50 JST`
- 作成担当: 実装者役担当Task
- 対象: 設計者役担当Task
- 正本言語: 日本語
- Documentation Index: [documentation_index_20260719013109.md](../documentation_index_20260719013109.md)
- Implementer Handoff: [designer_handoff_phase_1c_deployment_platform_acceleration_20260719013109.md](designer_handoff_phase_1c_deployment_platform_acceleration_20260719013109.md)
- Requirements: [phase_1c_deployment_platform_acceleration_requirements_20260719013109.md](../requirements/phase_1c_deployment_platform_acceleration_requirements_20260719013109.md)
- Architecture: [phase_1c_deployment_platform_acceleration_architecture_20260719013109.md](../architecture/phase_1c_deployment_platform_acceleration_architecture_20260719013109.md)
- Accepted ADR: [adr_0007_deployment_platform_acceleration_abstraction_20260719013109.md](../adr/adr_0007_deployment_platform_acceleration_abstraction_20260719013109.md)
- supersedes: [implementer_status_phase_1c_deployment_platform_acceleration_20260719021411.md](implementer_status_phase_1c_deployment_platform_acceleration_20260719021411.md)

## 1. 結論

Phase 1-C実装のRequired／Detected／Executed境界を修正した。

旧StatusではModel Load時のDevice観測値を、「当該Requestで実際に使用したDevice／Backend／Offload」である`Executed State`として記録していた。

これはRequest実行前に実行事実を先取りするため、次へ訂正した。

```text
Required State : Deployment Profileが保持
Detected State : Model Load後にBackend Adapterが観測
Executed State : Request単位の実行証拠がある場合のみ保持
```

Model Load直後の`RuntimeObservation`:

```text
detected.device_kind_key       : gpu
detected.acceleration_api_key  : metal
detected.gpu_offload           : true
executed                       : null
```

ADR-0007の「Observation不能値を推測しない」に従う。

## 2. 確認した最新正本

修正時点で`docs/`に配置されている最新Indexは`20260719013109`であり、Phase 1-C実装後のDesigner Reviewは未配置だった。

次を読取専用で再確認した。

- Documentation Index `20260719013109`
- Phase 1-C Requirements `20260719013109`
- Phase 1-C Architecture `20260719013109`
- Phase 1-C Implementer Handoff `20260719013109`
- ADR-0007 `20260719013109`

## 3. 修正内容

### Contract

- `DetectedRuntimeState`へ`gpu_offload`を追加
- `RuntimeObservation.executed`をOptional化
- `ExecutedRuntimeState`はRequest単位のEvidence用Contractとして維持
- Load時のObservation Builderは`executed=None`を生成

### Deployment Validation

次はLoad後のDetected Stateと比較する。

```text
Backend／Version
Compute Kind
Acceleration API
Required Device Kind
Required Acceleration API
Required Capability
```

Request未実行の`Executed State`をDeployment Ready判定に使わない。

### Regression Test

- CPU概念DeploymentでDetected GPU Offloadが`false`、Executedが`null`であること
- Metal Load ObservationがDetected GPU／Metal／Offloadを保持すること
- Load ObservationがRequest Executionを主張しないこと
- CLI `model-info`が`executed: null`を出力すること
- 実Model IntegrationがDetectedとExecutedを分離すること

## 4. 変更File

```text
M src/margpa_runtime_llm/modules/inference/contracts/runtime.py
M src/margpa_runtime_llm/bootstrap/profile_resolver.py
M tests/unit/inference/test_deployment_platform.py
M tests/unit/inference/test_cli.py
M tests/integration/llama_cpp/test_phase1b_runtime.py
A docs/handoffs/implementer_status_phase_1c_deployment_platform_acceleration_follow_up_20260719025250.md
```

Config、`pyproject.toml`、`uv.lock`およびDependencyに変更はない。

## 5. Static／Default／Environment Gate

```text
Ruff Format Check          : Pass／51 files
Ruff Check                 : Pass
mypy --strict              : Pass／47 source files
compileall                 : Pass
bash -n Setup Recipe       : Pass
Default pytest             : 67 passed, 2 deselected
Environment Verification  : Pass
uv lock --check            : Pass／117 packages
uv sync offline dry-run    : Pass／115 packages／Would make no changes
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

## 6. 実Model／Metal Regression

Sandbox内ではMetal Context作成が`Failed to create llama_context`で失敗した。同一TestをSandbox外のNative Metal環境で再実行し、通過した。

```text
pytest -m model_smoke : 2 passed, 67 deselected
```

`model-info`実測:

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

Production Acceptance:

```text
Success                         : true
Load including SHA-512          : 2.7010 seconds
Generation Result               : フェーズ1-B生産ランタイム成功
Generation Speed                : 30.19 tokens／second
Explicit Stream Terminal State  : cancelled
Post-cancel Generation          : OK／stop
Unload                          : 0.0428 seconds
```

Generation自体は成功したが、Current ContractにはRequestとExecution Observationを結び付けるTelemetryがない。そのため、Application Load Observationの`executed`はGeneration後も推測で埋めず`null`を維持する。

## 7. 旧Statusの訂正箇所

旧Statusの次の記述は本Follow-upで訂正する。

- Section 3のExecuted実測値
- Section 7のApplication Runtime ObservationにおけるExecuted State
- Section 8のCompute／AccelerationとExecutedの比較
- Section 9のExecuted Device／Acceleration／GPU Offload

正しい記述は「Load時はDetected、Request Executionは未観測」である。

## 8. Scope境界

次は未実装のままである。

- Request単位のExecution Telemetry／Audit
- Windows／Linux実Profile
- CUDA／ROCm／Vulkan等のBackend
- Response Language／Thinking Presentation
- Phase 2以降の機能

macOS／Apple Silicon arm64／Metal以外を`native_verified`とは主張しない。

## 9. 設計者へのReview依頼

次を再Reviewしてほしい。

1. Load時Detected StateとRequest時Executed Stateの意味境界
2. `executed=null`による未観測値の表現
3. Deployment RequirementをDetected Stateで検証する境界
4. `model-info`のObservation事実性
5. Static／Default／Metal Regression Evidence

