# Phase 1-D Response Language Policy Architecture

- 文書ID: `phase_1d_response_language_architecture`
- 状態: `accepted_ready_for_implementation_authorization`
- 作成日時: `2026-07-19 04:18:47 JST`
- 更新日時: `2026-07-19 04:18:47 JST`
- Snapshot: `20260719041847`
- 作成担当: 設計者役担当Task
- 対象: Phase 1-D、Configuration Composition、Response Resolver、Message Composer、CLI
- 正本言語: 日本語
- Requirements: [phase_1d_response_language_requirements_20260719041847.md](../requirements/phase_1d_response_language_requirements_20260719041847.md)
- Configuration Architecture: [configuration_layer_architecture_20260719041847.md](configuration_layer_architecture_20260719041847.md)
- ADR-0008: [adr_0008_response_language_policy_20260719040237.md](../adr/adr_0008_response_language_policy_20260719040237.md)
- ADR-0009: [adr_0009_application_deployment_configuration_separation_20260719041847.md](../adr/adr_0009_application_deployment_configuration_separation_20260719041847.md)
- supersedes: `phase_1d_response_language_architecture_20260719040237.md`

## 1. Architecture Conclusion

Phase 1-DはConfiguration CompositionとResponse Language Compositionを連続する二段階として実装する。

```text
config/application.toml
  ├─ selected_model
  ├─ model_root
  ├─ load_defaults
  ├─ generation
  └─ response.language
          │
          ├──────────── Model Definition
          └──────────── Deployment Profile
                         │
                         ↓
               Typed Config Composer
                         ↓
               EffectivePhase1Config
                         ↓
              Response Language Policy
                         ↓
               System Message Composer
                         ↓
                 GenerationRequest
                         ↓
                 InferenceService
```

## 2. Configuration Boundary

詳細は[Configuration Layer Architecture](configuration_layer_architecture_20260719041847.md)を正本とする。

Phase 1-Dで重要な境界：

```text
Application Config : Generation／Response／Model選択
Deployment Profile : Platform／Backend／Hardware Tuning
Model Definition   : Artifact／Capability／Model固有上限
```

Language PolicyはApplication Configだけから解決し、Deployment Profileを参照しない。

## 3. Target Files

```text
config/application.toml                              # New
config/models/qwen3_4b_q4_k_m.toml                  # 原則維持
config/profiles/local_macos_arm64.toml               # Schema 3
config/platforms/platform_registry.toml              # 原則維持
```

## 4. Contract

候補：

```python
class ResponseLanguage(StrEnum):
    JA = "ja"
    EN = "en"
    AUTO = "auto"

class ResponseLanguageSource(StrEnum):
    BUILT_IN_DEFAULT = "built_in_default"
    APPLICATION = "application"
    ENVIRONMENT = "environment"
    EXPLICIT = "explicit"

class ResponsePolicyConfig(ImmutableContract):
    language: ResponseLanguage = ResponseLanguage.JA

class ResolvedResponseLanguagePolicy(ImmutableContract):
    language: ResponseLanguage
    source: ResponseLanguageSource
```

前版のSource名`profile`は`application`へ修正する。

## 5. Application Config Integration

`ApplicationConfig`：

```python
class ApplicationConfig(BaseModel):
    schema_version: Literal["1"]
    application_key: str
    selected_model: str
    model_root: ModelRootConfig
    load_defaults: CommonLoadDefaults
    generation: GenerationParameters
    response: ResponsePolicyConfig
```

Strict `extra="forbid"`を維持する。

Default Path：

```text
config/application.toml
```

## 6. Deployment Profile Integration

Current `Phase1Profile`相当を、Deployment責務だけに限定する。

```python
class DeploymentProfile(BaseModel):
    schema_version: Literal["3"]
    profile_key: str
    verification_state: DeploymentVerificationState
    host: HostPlatformDefinition
    compute: ComputeTargetDefinition
    backend_runtime: BackendRuntimeDefinition
    runtime_requirements: DeploymentRequirements
    load_overrides: DeploymentLoadOverrides
```

次を持たせない。

```text
selected_model
model_root
generation
response
```

## 7. Effective Configuration

```python
class EffectivePhase1Config(ImmutableContract):
    application_key: str
    profile_key: str
    selected_model: str
    verification_state: DeploymentVerificationState
    host: HostPlatformDefinition
    compute: ComputeTargetDefinition
    backend_runtime: BackendRuntimeDefinition
    runtime_requirements: DeploymentRequirements
    model_root: Path
    load: ModelLoadConfig
    generation: GenerationParameters
    response: ResolvedResponseLanguagePolicy
    profile_resolution_source: ...
    applied_sources: tuple[str, ...]
```

## 8. Resolver Order

```text
Application Config Load
       ↓
Deployment Profile Resolution
       ↓
Model Selection Resolution
       ↓
Model Definition Load
       ↓
Typed Load／Generation／Response Resolution
       ↓
Cross-object Validation
       ↓
Effective Config
```

### Response

```text
Explicit
  > MARGPA_RESPONSE_LANGUAGE
  > Application Config
  > Built-in ja
```

### Load

```text
Explicit
  > Environment
  > Deployment load_overrides
  > Application load_defaults
  > Built-in
```

## 9. Response Message Composer

候補Location：

```text
src/margpa_runtime_llm/orchestration/response_language.py
```

概念形：

```python
def compose_generation_messages(
    *,
    user_prompt: str,
    user_system_message: str | None,
    policy: ResolvedResponseLanguagePolicy,
) -> tuple[ChatMessage, ...]:
    ...
```

### Composition Matrix

| Language | User System | Result |
|---|---:|---|
| `ja` | なし | Policy System＋User |
| `ja` | あり | 合成System＋User |
| `en` | なし | Policy System＋User |
| `en` | あり | 合成System＋User |
| `auto` | なし | Userのみ |
| `auto` | あり | User System＋User |

Multiple System MessageのBackend差を避けるため、PolicyとUser SystemはApplicationで単一System Messageへ決定論的に合成する。

## 10. Instruction Semantics

### Japanese

```text
回答は原則として日本語で行ってください。
ユーザーが回答言語を明示的に指定した場合は、その指定を優先してください。
```

### English

```text
Respond in English by default.
If the user explicitly requests a different response language, follow that request.
```

### Auto

Language Instructionなし。

正確な文字列はTest Fixtureとして固定する。

## 11. Entrypoint

```text
margpa-llm generate --response-language ja
margpa-llm generate --response-language en
margpa-llm generate --response-language auto
```

CLIはInput取得と描画だけを担当する。Instruction文字列をCLIへ置かない。

Message CompositionはStreaming／Non-streaming分岐前に行う。

## 12. `model-info`

概念形：

```json
{
  "effective_config": {
    "application_key": "default",
    "profile_key": "local.macos-arm64",
    "selected_model": "main.qwen3-4b-q4-k-m",
    "load": {},
    "generation": {},
    "response": {
      "language": "ja",
      "source": "application"
    },
    "applied_sources": []
  }
}
```

## 13. Model／Adapter Boundary

次へLanguage Policyを追加しない。

```text
Model Definition
Model Port
InferenceService
llama.cpp Adapter
Qwen Chat Template固有処理
```

Model Portは合成済み`ChatMessage`を受け取るだけとする。

## 14. Validation

### File-local

- Application Schema／Field
- Deployment Schema／Field
- Model Schema／Field
- Platform Registry Reference

### Cross-object

- Selected Model Key一致
- Model Backend／Deployment Backend一致
- Context Limit
- Host／Runtime Requirement

### Response

- `ja／en／auto`
- Unknown Error
- Source Tracking

## 15. No Deep Merge

Section Resolverを使う。

```text
resolve_load_config
resolve_generation_config
resolve_response_policy
```

Platform Profileが`generation`または`response`を含む場合、Unknown Fieldとして拒否する。

## 16. Candidate Source Scope

```text
src/margpa_runtime_llm/bootstrap/config_loader.py
src/margpa_runtime_llm/bootstrap/phase1_application.py
src/margpa_runtime_llm/modules/inference/contracts/response.py
src/margpa_runtime_llm/modules/inference/contracts/__init__.py
src/margpa_runtime_llm/modules/inference/public.py
src/margpa_runtime_llm/orchestration/response_language.py
src/margpa_runtime_llm/entrypoints/cli/main.py
config/application.toml
config/profiles/local_macos_arm64.toml
tests/unit/inference/test_config_and_registry.py
tests/unit/inference/test_response_language.py
tests/unit/inference/test_cli.py
tests/integration/llama_cpp/test_phase1b_runtime.py
```

## 17. Migration Safety

Migration前後で、Default Current Macの次が一致することをTestする。

```text
selected_model
model_root resolved path
complete ModelLoadConfig
complete GenerationParameters
Deployment Requirement
```

新規差分は次だけである。

```text
response.language = ja
response.source = application
application_key = default
```

## 18. Phase 1-E Boundary

```text
Phase 1-D:
Config → Input Message Composition → Model

Phase 1-E:
Model Raw Output → Parser → Presentation → Display
```

Phase 1-DでOutput／Streaming Chunkを加工しない。

## 19. Authorization Boundary

本ArchitectureはAcceptedである。

実装担当はユーザーからPhase 1-D実装開始の明示許可を得た後に変更する。
