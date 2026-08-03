# Phase 1-D Response Language Policy Architecture

- 文書ID: `phase_1d_response_language_architecture`
- 状態: `accepted_ready_for_implementation_authorization`
- 作成日時: `2026-07-19 04:02:37 JST`
- 更新日時: `2026-07-19 04:02:37 JST`
- Snapshot: `20260719040237`
- 作成担当: 設計者役担当Task
- 対象: Phase 1-D、Response Policy Resolver、System Message Composer、Config、CLI
- 正本言語: 日本語
- Requirements: [phase_1d_response_language_requirements_20260719040237.md](../requirements/phase_1d_response_language_requirements_20260719040237.md)
- Accepted ADR: [adr_0008_response_language_policy_20260719040237.md](../adr/adr_0008_response_language_policy_20260719040237.md)
- 設計元: [response_language_and_thinking_output_policy_20260719013109.md](response_language_and_thinking_output_policy_20260719013109.md)
- 前Phase: [phase_1c_deployment_platform_acceleration_architecture_20260719013109.md](phase_1c_deployment_platform_acceleration_architecture_20260719013109.md)
- supersedes: なし（設計元のResponse Language部分をPhase 1-Dとして具体化する新規Architecture）

## 1. Architecture Conclusion

Response LanguageをModel Generation ParameterやBackend Capabilityではなく、Modelへ渡すMessage列を構築するApplication Policyとして実装する。

```text
Built-in／Profile／Environment／Explicit
                    ↓
       Response Language Resolver
                    ↓
       Effective Response Policy
                    ↓
 User Prompt＋Optional User System Message
                    ↓
          System Message Composer
                    ↓
          GenerationRequest.messages
                    ↓
             InferenceService
                    ↓
               Model Port
                    ↓
              Model Adapter
```

InferenceService、Model Portおよびllama.cpp Adapterは、Language Policyを解決しない。合成済みのBackend-independent `ChatMessage`列だけを受け取る。

## 2. Current Architectureとの差分

### Current

```text
CLI
  ├─ --system
  └─ --prompt
       ↓
CLIが直接ChatMessage列を構築
       ↓
InferenceService
```

### Phase 1-D

```text
Deployment Profile／Environment／CLI
       ↓
Response Language Resolver
       ↓
CLI Input
       ↓
Application-owned Message Composer
       ↓
InferenceService
```

CLIは入力値の取得と表示を担当し、Language Instructionの本文や合成規則を所有しない。

## 3. Responsibility Boundary

### Contract

- 許可Language値
- Effective Policy
- Policy Source
- Validation

### Bootstrap／Config

- TOML Profile読込
- Environment Override読込
- Explicit Override適用
- Effective Policy生成
- Applied Source記録

### Orchestration／Application Policy

- Language Instructionの選択
- User System Messageとの合成
- Final `ChatMessage`列の生成

### Entrypoint

- `--response-language`受付
- User Prompt／System入力
- Composer呼び出し
- Output描画

### InferenceService／Model Port

- 合成済みMessage列のValidationと推論
- Language Policyの意味を解釈しない

### Adapter

- Chat Template適用
- Model固有Protocol処理
- Default日本語／英語を持たない

## 4. Contract Design

### 4.1 `ResponseLanguage`

候補Location：

```text
src/margpa_runtime_llm/modules/inference/contracts/response.py
```

概念形：

```python
class ResponseLanguage(StrEnum):
    JA = "ja"
    EN = "en"
    AUTO = "auto"
```

LanguageがInference Parameterではないことを明確にするため、`GenerationParameters`へ追加しない。

### 4.2 `ResponseLanguageSource`

概念形：

```python
class ResponseLanguageSource(StrEnum):
    BUILT_IN_DEFAULT = "built_in_default"
    PROFILE = "profile"
    ENVIRONMENT = "environment"
    EXPLICIT = "explicit"
```

### 4.3 `ResolvedResponseLanguagePolicy`

概念形：

```python
class ResolvedResponseLanguagePolicy(ImmutableContract):
    language: ResponseLanguage
    source: ResponseLanguageSource
```

Phase 1-DではObserved Output Language Fieldを追加しない。

### 4.4 Config用Contract

Profile内のConfigはSourceを持たない。

概念形：

```python
class ResponsePolicyConfig(ImmutableContract):
    language: ResponseLanguage = ResponseLanguage.JA
```

`Phase1Profile.response`は`ResponsePolicyConfig`、`EffectivePhase1Config.response`は`ResolvedResponseLanguagePolicy`を持つ。

## 5. Profile Schema

### 5.1 Schema Version

```text
Before : 2
After  : 3
```

Profile構造の追加を明示するためVersionを更新する。

### 5.2 Current Profile

```toml
schema_version = "3"

[response]
language = "ja"
```

`config/profiles/local_macos_arm64.toml`以外の実ProfileはPhase 1-D時点で存在しない。

### 5.3 Compatibility

Tracked Current ProfileはSchema `3`へMigrationする。

Schema `2`を暗黙補完してCurrentとして扱わない。将来Profile Migration機構が必要になった場合は、専用Version Migrationとして追加する。

Platform Registryは同じProfile Pathを参照するため、Reference Key変更は不要である。

## 6. Resolution Algorithm

入力：

```text
Built-in Default : ja
Profile Value    : ja／en／auto
Environment      : MARGPA_RESPONSE_LANGUAGE
Explicit Value   : CLI／将来API
```

概念Algorithm：

```text
language = ja
source = built_in_default

if Profileに有効値がある:
    language = Profile値
    source = profile

if Environmentに値がある:
    language = Environment値
    source = environment

if Explicit Overrideがある:
    language = Explicit値
    source = explicit

return ResolvedResponseLanguagePolicy(language, source)
```

ValidationはPydantic Contractで行い、不正Environment値を黙って`ja`へFallbackしない。

### 6.1 Existing `applied_sources`

既存`EffectivePhase1Config.applied_sources`は、Config全体にProfile／Environment／CLIが関与した事実として維持する。

Response Language専用の最終Sourceは`response.source`で表す。

## 7. Message Composition

### 7.1 Location

候補Location：

```text
src/margpa_runtime_llm/orchestration/response_language.py
```

このModuleはBackend、llama.cpp、QwenおよびMetalへ依存しない。

### 7.2 Public Function

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

Phase 1-DではClass化を必須にしない。状態を持たないPure Functionで十分である。

### 7.3 Language Instruction

初期意味を次に固定する。

```text
ja:
回答は原則として日本語で行ってください。
ユーザーが回答言語を明示的に指定した場合は、その指定を優先してください。

en:
Respond in English by default.
If the user explicitly requests a different response language, follow that request.

auto:
Language Instructionなし
```

文言の軽微な変更でもModel Behaviorへ影響するため、実装時はTest Fixtureとして固定する。

### 7.4 Composition Cases

#### `ja／en`＋User Systemなし

```text
SYSTEM    : Project Response Language Instruction
USER      : User Prompt
```

#### `ja／en`＋User Systemあり

BackendごとのMultiple System Message対応差を上位層へ漏らさないため、Applicationで単一System Messageへ決定論的に合成する。

```text
SYSTEM:
  Project Response Language Instruction
  Stable Separator
  User-provided System Instruction

USER:
  User Prompt
```

要件：

- User System文字列は改変せずSubstringとして保持する
- Stable Separatorは固定値とする
- User SystemをProject Policyへ文字列置換しない
- 空User Systemは既存Validationに従い拒否する

#### `auto`＋User Systemなし

```text
USER : User Prompt
```

#### `auto`＋User Systemあり

```text
SYSTEM : User-provided System Instruction
USER   : User Prompt
```

### 7.5 Why Single System Message

- Chat TemplateごとのMultiple System Message処理差を避ける
- Current CLIのSystem Message概念を維持する
- Model Adapterに合成規則を追加せずに済む
- Unit TestでFinal Message列を決定論的に確認できる

将来、Message Provenance Contractを導入した場合は、Modelへ渡す合成MessageとAuditへ残す元要素を分離する。

## 8. Natural-language Language Request

Response Language PolicyはDefaultであり、強制的Output Filterではない。

次のPromptをApplicationが解析しない。

```text
英語で回答して
日本語で回答して
Explain in Japanese
Translate this into English
```

Default Instruction自体が「Userが別言語を明示した場合は優先」とModelへ伝える。

利点：

- 不完全なRule Based Language Detectionを避ける
- Code／引用／多言語文の誤判定を避ける
- Userの原文を保持する

限界：

- Modelが明示指示を正しく解釈する保証はない
- Applied PolicyとObserved Outputが異なる可能性がある
- Strict Language Enforcementではない

Strict判定が必要になった場合は、Output Evaluator／Guard／Judge側の別機能とする。

## 9. Bootstrap Integration

### 9.1 `config_loader.py`

追加候補：

```text
RESPONSE_ENVIRONMENT_FIELDS
ResponsePolicyConfig
Phase1Profile.response
EffectivePhase1Config.response
response_language_override
```

Environment Key：

```text
MARGPA_RESPONSE_LANGUAGE
```

### 9.2 `phase1_application.py`

`build_phase1_application`はExplicit Response Language OverrideをConfig Resolverへ渡す。

Application Build時にMessageを生成しない。MessageはRequest作成時にComposerを通す。

### 9.3 Request Boundary

Phase 1 CLIではRequestごとにApplicationをBuildしているため、Explicit CLI値をEffective Configへ含められる。

Phase 2の常駐Applicationでは、Request OverrideをProfile DefaultへMutationせず、Request単位Resolverで合成する。

Phase 1-D実装でPhase 2常駐Lifecycleを先行実装しない。

## 10. CLI Integration

### 10.1 Argument

```text
margpa-llm generate --response-language ja
margpa-llm generate --response-language en
margpa-llm generate --response-language auto
```

Argument Parserの`choices`または型変換により未知値を拒否する。

### 10.2 Existing Usage

次を維持する。

```text
margpa-llm generate --prompt "..."
margpa-llm generate --prompt "..." --system "..."
margpa-llm generate --prompt "..." --thinking
margpa-llm generate --prompt "..." --no-thinking
```

### 10.3 `model-info`

概念Output：

```json
{
  "effective_config": {
    "response": {
      "language": "ja",
      "source": "profile"
    }
  }
}
```

`generate --response-language`は生成Request専用であるため、その値を確認する場合は将来のRequest AuditまたはDebug表示へ接続する。Phase 1-Dで通常回答へMetadataを混在させない。

## 11. Streaming／Non-streaming

Message Compositionは`application.service.generate`と`application.service.stream`へ分岐する前に一度だけ行う。

```text
Compose Messages
      ↓
GenerationRequest
  ├─ generate
  └─ stream
```

Phase 1-DではStreaming Chunkを加工しない。

## 12. Model Adapter Boundary

原則として次は変更不要である。

```text
adapters/model_backends/llama_cpp/chat_template.py
adapters/model_backends/llama_cpp/adapter.py
modules/inference/ports/model_port.py
```

Test修正またはImport整理が必要な場合を除き、Language名、Instruction文またはPolicy解決をAdapterへ追加しない。

## 13. Error Model

### Invalid Profile／Environment

既存の`INVALID_CONFIGURATION`へMappingする。

```text
safe_message : The effective runtime configuration is invalid.
details      : exception_type等の安全な情報だけ
```

### Invalid CLI

ArgparseによるUsage ErrorとExit Code `2`を使用する。

### No Silent Fallback

```text
MARGPA_RESPONSE_LANGUAGE=jp
```

を`ja`として扱わない。

## 14. Testing Architecture

### Unit Contract

- Enum／Config Validation
- Resolver Precedence
- Source Tracking
- Message Composition Matrix
- User Content Preservation

### CLI

- Parse／Override
- Invalid Choice
- `model-info`
- Existing Flag Compatibility

### Adapter Boundary

Fake Model Portへ渡ったFinal `GenerationRequest.messages`を検証する。

Language PolicyのUnit Testに実Modelを必要としない。

### Native Smoke

Current Qwen3-4B／Metalで次を観測する。

```text
Default ja:
  Prompt本文に「日本語で」を書かず、短い日本語回答を要求する

Explicit en:
  --response-language enで短い英語回答を要求する

auto:
  Language InstructionなしでGenerationが成立する
```

Model生成は確率的であるため、厳密な自然言語分類だけをAcceptance Gateにしない。Composerの決定論的TestとNative伝達確認を併用する。

## 15. Candidate File Changes

候補であり、実装担当は不要なFileを量産しない。

```text
src/margpa_runtime_llm/modules/inference/contracts/response.py
src/margpa_runtime_llm/modules/inference/contracts/__init__.py
src/margpa_runtime_llm/modules/inference/public.py
src/margpa_runtime_llm/orchestration/response_language.py
src/margpa_runtime_llm/bootstrap/config_loader.py
src/margpa_runtime_llm/bootstrap/phase1_application.py
src/margpa_runtime_llm/entrypoints/cli/main.py
config/profiles/local_macos_arm64.toml
tests/unit/inference/test_response_language.py
tests/unit/inference/test_config_and_registry.py
tests/unit/inference/test_cli.py
tests/integration/llama_cpp/test_phase1b_runtime.py
```

新規外部Dependencyは不要である。

## 16. Phase 1-E Hook

Phase 1-Dでは、将来のPhase 1-Eと衝突しないよう次を守る。

- CLI入力からGenerationRequestまでのMessage Compositionを独立関数化する
- Raw OutputをLanguage機能で加工しない
- Streaming ChunkをLanguage機能で加工しない
- Thinking Tagを削除しない
- Thinking実行FlagをLanguage Policyへ含めない

Phase 1-EはModel出力後のParser／Presentation Pipelineを追加する。

```text
Phase 1-D
Input → Language Policy → Message Composition → Model

Phase 1-E
Model Raw Output → Protocol Parser → Presentation Policy → Display Output
```

## 17. Security／Governance Note

Response Language InstructionはSecurity Policyではない。

- Prompt Injectionを防止しない
- Jailbreakを検出しない
- Tool Permissionを決めない
- System Authorityを新規生成しない
- ARGD／DAGDを自動適用しない

将来Governance CompilerがSystem Messageを構築する場合、Language PolicyはCompilerへ入力する独立Policyとして接続する。

## 18. Acceptance Mapping

| Requirement | Architecture Evidence |
|---|---|
| `ja／en／auto` | `ResponseLanguage` Contract |
| Default `ja` | Built-in／Profile Default |
| Override | Resolver Algorithm |
| Source | `ResolvedResponseLanguagePolicy` |
| Adapter Independence | Orchestration Composer |
| User Content Preservation | Composition Cases |
| `auto` | Instruction非注入 |
| Streaming Parity | 分岐前Composition |
| Observability | Effective Config／model-info |
| Phase 1-E分離 | Raw Output非加工 |

## 19. Authorization Boundary

本ArchitectureはAccepted ADRに基づく実装基準である。

実装担当は、ユーザーからPhase 1-D実装開始の明示許可を得た後にSource／Config／Testを変更する。

実装中にContract変更が必要になった場合、独断で拡張せず、実装担当Statusまたは質問として設計者へ返す。
