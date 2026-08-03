# Public Demo Access Profile／RAG分離／Runtime交換 Architecture

```yaml
document_id: public_demo_access_profile_and_runtime_portability_architecture
status: accepted
language: ja
created_at: 2026-07-30 14:49:21 JST
owner: 設計統括者役
phase: phase_1_ex
supersedes_in_part:
  - public_demo_auto_start_and_rag_extension_architecture
```

## 1. Architecture Goal

既存Basic認証Previewを保持し、認証なしPublic Demoを別の明示的Access Profileとして追加する。

Public DemoのためにConversation Core、Model Adapter、Deployment Profileまたは既存Basic Lifecycleを複製しない。Access、Feature、Control、Model、DeploymentおよびPlatform Lifecycleを直交する設定軸として扱う。

## 2. Orthogonal Configuration Axes

```text
Application Core
  ├─ Model Definition／Model Adapter
  ├─ Deployment Profile
  ├─ Web Access Profile
  ├─ Feature Profile
  ├─ Optional Control Policy
  └─ Platform Lifecycle Adapter
```

各軸の責務：

| 軸 | 責務 |
|---|---|
| Model Definition | Model ID、Artifact、Format、Quantization、Capability |
| Model Adapter | Load、Tokenizer、Chat Template、Streaming、Cancel |
| Deployment Profile | OS、Architecture、CPU／GPU、Backend Build、Load Override |
| Web Access Profile | Local／Basic Preview／Public Demo、Authentication |
| Feature Profile | RAG、Summary、Thinking、Tool等の利用可否 |
| Control Policy | Rate、Budget、Cooldown、Cost Guard |
| Platform Lifecycle Adapter | Lightning、Local、Home Server、Cloudの起動方法 |

一つの軸を変更しても、無関係な軸の再実装を要求しない。

## 3. Web Access Model

推奨Contract：

```text
WebExposureMode:
  local
  basic_preview
  public_demo
```

認証はExposure Modeの属性として解決する。

```text
local:
  loopback_only
  authentication = none

basic_preview:
  non_loopback_allowed
  authentication = basic

public_demo:
  non_loopback_allowed
  authentication = none
  explicit_selection_required = true
```

現在の`WebAuthMode.DISABLED`をそのままPublic Demoの識別子にしない。

```text
Authentication None
≠ Public Demo承認
```

`public_demo`を明示選択したときだけ、Non-loopback＋Authentication Noneを許可する。

## 4. Config配置

候補：

```text
config/web_profiles/
├─ basic_preview.toml
└─ public_demo.toml
```

概念例：

```toml
schema_version = "1"
profile_key = "public_demo"

[access]
mode = "public_demo"
authentication = "none"
non_loopback_allowed = true

[features]
documentation_rag = "disabled"
summary = "enabled"
thinking_generation = "enabled"
thinking_presentation = "enabled"

[controls.rate_limit]
mode = "off"

[controls.generation_budget]
mode = "off"

[controls.cooldown]
mode = "off"

[controls.cost_guard]
mode = "off"
```

Basic Preview：

```toml
schema_version = "1"
profile_key = "basic_preview"

[access]
mode = "basic_preview"
authentication = "basic"
non_loopback_allowed = true

[features]
documentation_rag = "eligible"
```

`eligible`は、RAGが自動的に有効であることを意味しない。RAG Module、SourceおよびFeature設定が揃った場合に有効化できることだけを示す。

## 5. Request Pipeline

```text
HTTP Request
  → Exposure Profile Resolution
  → Bind／Authentication Validation
  → Existing Security Headers
  → Existing Request Validation
  → Feature Policy
  → Optional Control Policy Port
  → Conversation Application
  → Optional RAG Port
  → Model Port
  → Streaming Response
```

Phase 1-ex Public Demo：

```text
Feature Policy:
  documentation_rag = disabled

Optional Control Policy:
  Null／Off Implementation

Conversation:
  Existing Phase 1 behavior
```

## 6. Limit Hook Architecture

将来制限機構はPortとして追加可能にする。

```text
PublicControlPolicyPort
  ├─ check_request()
  ├─ before_generation()
  ├─ observe_generation()
  └─ after_generation()
```

初期Adapter：

```text
DisabledPublicControlPolicy
  mode = off
  side_effect = none
  rejection = none
  persistence = none
```

将来Adapter：

```text
InMemoryRateLimitAdapter
PersistentQuotaAdapter
CostBudgetAdapter
CloudProviderBudgetAdapter
```

Phase 1-exで将来Adapterを実装しない。Null／Off ContractをWeb Routeへ直接条件分岐として散らさず、Composition Rootから注入できる形を優先する。

## 7. RAG Architecture

```text
Conversation Application
  → Optional RagOrchestratorPort
     ├─ DocumentSourcePort
     ├─ ChunkerPort
     ├─ EmbeddingPort
     ├─ IndexStorePort
     ├─ RetrieverPort
     ├─ ContextAssemblerPort
     └─ CitationPort
```

Access Profileによる解決：

```text
basic_preview:
  RAG Capability = eligible
  Effective State = unavailable／disabled／enabled

public_demo:
  RAG Capability = denied
  Effective State = disabled
```

Public Demoでは、Request到着後にRAGを止めるだけでなく、Composition RootでRAG Adapterを構築しない。

Clientから`rag=true`等を送っても、Public DemoでCapabilityを昇格させない。

## 8. Basic／Public Lifecycle分離

```text
Basic Preview:
  Existing Private Bootstrap
    → basic_preview_service.sh
    → Web Access Profile = basic_preview

Public Demo:
  User-managed Platform Entry
    → public_demo_service.sh
    → Web Access Profile = public_demo
```

Public Demoは別Scriptまたは別Subcommandを持つ。既存`basic_preview_service.sh`からCredential検査を削除しない。

両Processが同じModelを同時LoadするとMemoryとCreditを余分に消費するため、同一Studioでの同時常駐は既定運用にしない。Basic Previewを保持するとは、設定・Entry Point・Rollback可能性を保持することであり、常時二重起動を意味しない。

Platform上のAPI Builder作成、Port、URLおよびBootstrap配置はユーザー操作とする。

## 9. Model Portability

```text
Web Access Profile
  → model_keyを所有しない

Application Configuration
  → selected_model

Model Definition
  → Artifact／Capability／Backend

Model Adapter
  → Backend固有実装
```

Public Demo Entry PointはModel Root、Model Key、RegistryおよびDeployment Profileを既存Config Layerへ渡すだけとする。

Qwen、GGUF、llama.cpp、Metal、CUDA、Lightning等をWeb Access Domainへ持ち込まない。

## 10. Deployment Portability

```text
Mac Metal:
  local_macos_arm64.toml

Lightning Pure CPU:
  lightning_linux_x86_64_cpu_native.toml

Lightning CUDA:
  lightning_linux_x86_64_cuda.toml

Future Home Server:
  home_<os>_<arch>_<accelerator>.toml

Future Cloud:
  cloud_<provider-neutral-target>.toml
```

Profile名は例であり、特定ProviderをCore Contractにしない。

Environment検出はDeployment Profile選択を補助できるが、Access Profile、RAG可否またはPublic公開許可を自動生成しない。

## 11. High-performance Migration

高性能Model／Server導入が早まる可能性を考慮し、次を実装時に確認する。

- Public Demo Entry PointがModel Keyを引数またはConfigから解決する。
- Web Runtime SnapshotがModel Capabilityを安全に表示する。
- Model Context、Generation上限およびCapability不足をModel Definitionから扱う。
- CPU／Metal／CUDAの切替をDeployment Profileへ閉じ込める。
- Remote Model Backend追加時もWeb Access Profileを再実装しない。
- High-cost環境へ移行した場合、`controls.*.mode`を`observe／enforce`へ拡張できる。

## 12. Failure Policy

```text
Unknown Access Profile:
  Startup Refusal

Basic Credential Missing:
  Startup Refusal

Public Demo＋RAG enabled:
  Startup Refusal

Public Control Unknown Mode:
  Startup Refusal

Model Capability Missing:
  Explicit Degrade／Warning／Refusal

Deployment Profile Invalid:
  Startup Refusal
```

Public Demoを起動できない場合、Basic Previewを自動的に匿名化してFallbackしない。

## 13. Test Architecture

### Unit

- Exposure Profile Parse／Validation
- Bind Policy Matrix
- Basic Credential Contract
- Public Credential Independence
- Public RAG Denial
- Control Hook `off`
- Unknown Mode Fail Closed
- Model／Deployment非依存

### Web Integration

- Basic Root `401`
- Basic Credential Success
- Public Root `200`
- Public Chat／Stop／New Chat
- Summary／Thinking／Language
- Public RAG有効化拒否
- Security Header
- Safe Error

### Regression

- Mac Local
- Lightning Basic Preview
- Lightning Pure CPU
- Existing Web Test
- Existing Lifecycle Test
- CLI／Model Port Contract

## 14. 実装境界

実装候補：

```text
src/margpa_runtime_llm/web/
src/margpa_runtime_llm/bootstrap/
src/margpa_runtime_llm/entrypoints/web/
config/web_profiles/
scripts/runtime/lightning/
tests/unit/
tests/integration/web/
```

今回変更しない：

```text
Model Artifact
Dependency
Native Backend
Lightning Platform設定
Private Bootstrap
External Cloud
Home Server
RAG実装本体
```

