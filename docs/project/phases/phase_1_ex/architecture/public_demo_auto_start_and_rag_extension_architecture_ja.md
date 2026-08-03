# Public Demo／Auto-start／RAG Extension Architecture

```yaml
document_id: public_demo_auto_start_and_rag_extension_architecture
status: accepted
language: ja
created_at: 2026-07-26 17:53:18 JST
updated_at: 2026-07-26 19:49:49 JST
owner: 設計統括者役
phase: phase_1_ex
```

## 1. Overview

```text
Lightning Public URL
  → Traffic-aware Auto-start
  → Web Access Profile
  → Public Demo Policy Middleware
  → Conversation Application
  → Model Port
  → llama.cpp Adapter

Basic Preview
  → Basic Access Profile
  → Existing Web Surface
```

Application CoreとModel Adapterは共有し、Access、Public Limit、Platform起動およびDemo表示を境界Adapterへ隔離する。

## 2. Auto-start Boundary

候補：

```text
Lightning API Builder／Public App:
  Traffic-aware Wake-up
  Public URL
  Serverless／Sleep

Lightning on_start.sh:
  Studio起動後のServer Process開始
  Traffic-aware Wake-up自体は担当しない
```

Auto-start PreflightはProject側とPlatform側を分ける。

```text
Project Read-only:
  Command
  Profile
  Model Path
  Environment
  Health Endpoint
  Fail-closed Config

Platform Manual:
  Plugin Availability
  Auto-start Toggle
  Public URL
  Sleep／Wake
  Cold Start
  Credit
```

公式参照：

- [Lightning Expose web apps](https://lightning.ai/docs/overview/host-web-apps/expose-web-apps)
- [Lightning On-start actions](https://lightning.ai/docs/overview/ai-studio/on-start-actions)
- [Lightning Auto sleep](https://lightning.ai/docs/overview/ai-studio/auto-sleep)
- [Lightning Host web apps](https://lightning.ai/docs/overview/host-web-apps)

## 3. Web Access Profile

Deployment ProfileとWeb Access Profileを分離する。

```text
Deployment Profile:
  OS
  Architecture
  Compute
  Backend
  Model Load

Web Access Profile:
  Access Mode
  Authentication
  Public Limit
  Allowed Features
  Privacy
  Presentation
```

候補配置：

```text
config/web_profiles/basic_preview.toml
config/web_profiles/public_demo.toml
```

最終配置はConfiguration Layer設計と整合させて実装Handoffで確定する。

## 4. Public Policy Pipeline

```text
Request
  → Security Header
  → Access Mode Validation
  → Body Size
  → Rate／Budget
  → Public Input Limit
  → Feature Allowlist
  → Model Busy Gate
  → Generation Timeout
  → Safe Streaming
  → Public Output
```

Rate Limitは初期版ではProcess内Token BucketまたはSliding Windowでよい。

```text
Single Process
Single Worker
No Shared External Store
Restart Resets Budget
```

将来Multi-worker／Multi-replica化する場合はExternal Store Adapterへ交換する。

## 5. Cost Boundary

App内LimitはStudio起動後に機能する。Public URLへのAccessによるPlatform Wake-up自体を防止できない。

したがってCost保護は次の二層で扱う。

```text
Platform:
  Auto-start
  Sleep
  Machine
  Credit
  Deployment／Plugin Limit

Application:
  Rate Limit
  Token Limit
  Generation Budget
  Timeout
  Feature Disable
```

## 6. Public／Basic Separation

Access ModeをRuntime起動時に固定し、Request単位で自由に切り替えない。

Public DemoがBasic Credentialを読まず、Basic PreviewがPublic Policyへ暗黙Degradeしないようにする。

非Loopback BindでAccess Modeが不明な場合は起動拒否する。

### 6.1 Basic Preview Lifecycle

```text
Lightning Managed Secrets
  → Environment Variables
  → Repository Lifecycle Script
     ├─ preflight
     ├─ run
     ├─ start
     ├─ stop
     ├─ status
     └─ restart
  → margpa-web
```

Credential値はRepositoryへ保存しない。Lifecycle ScriptはEnvironmentからCredentialを子Processへ継承し、Argument、Log、PID FileまたはStatusへ出さない。

Lightningの`on_start.sh`またはAPI BuilderはRepository内Lifecycle Scriptを呼ぶThin Platform Hookとする。Platform Hookの配置・設定はユーザーが行い、実装担当はRepository側ScriptとTestだけを作る。

## 7. RAG Extension Hook

```text
Conversation
  → Optional RagOrchestratorPort
     ├─ DocumentSourcePort
     ├─ ChunkerPort
     ├─ EmbeddingPort
     ├─ IndexStorePort
     ├─ RetrieverPort
     ├─ ContextAssemblerPort
     └─ CitationPort
  → Model Port
```

Phase 1-ex：

```text
Execution:
  Mac only

Source:
  Local docs/

Index:
  Local／lightweight

Public Demo:
  Disabled
```

Future：

```text
Lightning／Home Server／Cloud:
  Filesystem Adapter
  Object Storage Adapter
  Remote Embedding Adapter
  External Vector Store Adapter
  Remote Inference Adapter
```

Core ContractへmacOS、`/Users/...`、Lightning固定Pathまたは特定Vector Store名を埋め込まない。

## 8. Documentation Language Architecture

```text
Japanese Canonical:
  docs/project/current/*_ja.md
  docs/public/*_ja.md

English Derived:
  docs/project/current/*_en.md
  docs/public/*_en.md

Japanese Only:
  docs/project/phases/
  docs/project/shared/
  Raw History
```

英語版は日本語版の`document_id`または`translation_of`を参照し、英語版だけで新規Decisionを作らない。

## 9. Failure／Degrade

```text
Auto-start unavailable:
  Keep Basic Preview
  Public Demo Activation deferred

RAG docs missing:
  RAG unavailable
  Chat remains usable

Public Budget exceeded:
  429 + Retry-After

Public Policy invalid:
  Startup refusal

Model busy:
  409／No queue
```

## 10. Validation

- Basic／Public Config isolation
- Non-loopback Fail Closed
- Public Hard Cap
- Rate／Budget／Timeout
- Disabled Feature cannot Load／Call
- No Prompt persistence
- Health does not expose Runtime detail
- Sleep／Wake／Cold Start
- Mac／Lightning Profile independence
- JA／EN Link
- RAG disabled without docs
