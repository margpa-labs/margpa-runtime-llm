# Public Demo最小公開／RAG分離／Runtime交換性 要件

```yaml
document_id: public_demo_minimal_access_and_runtime_portability_requirements
status: accepted
language: ja
created_at: 2026-07-30 14:49:21 JST
owner: 設計統括者役
phase: phase_1_ex
supersedes_in_part:
  - public_demo_auto_start_and_pre_release_requirements
```

## 1. 目的

Traffic-aware Auto-startが成立済みのLightning環境へ、既存Basic認証Previewを維持したまま、認証なしPublic Demoを別Access Profileとして追加する。

現時点では利用者数が少ないと見込まれ、Lightningの現在環境、公開目的および運用負荷を考慮し、Public専用Rate Limit、Generation Budget、Cooldownおよび追加Token Hard Capを必須実装にしない。

ただし、将来の利用増加、Credit消費、高性能Model、GPU Server、Home Serverまたは外部Cloud移行時に追加できるよう、制限PolicyのHookと設定境界を予約する。

## 2. 今回確定するAccess Profile

```text
basic_preview:
  Authentication = Basic
  Purpose        = 少人数向け検証
  Documentation RAG = 将来利用可能

public_demo:
  Authentication = None
  Purpose        = 匿名閲覧・試用
  Documentation RAG = 強制無効
```

両者は同じApplication Core、Conversation Service、Model PortおよびWeb UIを共有できるが、Access Profile、起動入口、Feature PolicyおよびTestを分離する。

Basic認証を既存Entry Pointから単純削除し、それを暗黙にPublic Demoとして扱ってはならない。

## 3. Basic Preview維持要件

- 現在のBasic認証Previewを削除、Renameまたは挙動変更しない。
- `MARGPA_WEB_AUTH_USERNAME`と`MARGPA_WEB_AUTH_PASSWORD`は引き続きEnvironment／Managed Secretsからだけ取得する。
- Basic PreviewのLifecycle、Traffic-aware Auto-start、Port、Private Bootstrapおよび既存Testを破壊しない。
- 将来Documentation RAGを追加する場合、Basic PreviewはRAG有効化対象にできる。
- RAG未実装または`docs/`不在時も、通常Chatは利用できる。

## 4. Public Demo最小要件

Public Demoは、現在のPhase 1 Web機能を原則そのまま提供する。

```text
Text Chat
New Chat
Stop
Copy
UI日本語／English
回答言語 ja／en／auto
Thinking生成
Thinking表示
Summary Mode
最大生成Token設定
```

今回Public Demoだけに追加する利用量制限はない。

ただし、既存Runtimeが持つ次の技術的境界は維持する。

- Request Schema Validation
- 既存Request Body上限
- 既存Generation Parameter上限
- Single Worker
- Model側の同時生成制約
- Model Busy応答
- Cancel／Shutdown
- Safe Error Mapping
- Security Header
- Prompt／回答の非永続

これらはPublic専用のRate／Cost制限ではなく、既存Web Runtimeの安全・整合性境界である。

## 5. Explicit Public Access

Non-loopback Bindで認証を無効化できるのは、明示的に`public_demo` Access Profileが選択された場合だけとする。

```text
Access Profile不明:
  Startup Refusal

Basic PreviewでCredential不足:
  Startup Refusal

Local／Disabled AuthのままNon-loopback Bind:
  Startup Refusal

Explicit Public Demo:
  Non-loopback＋Authentication Noneを許可
```

単一の`MARGPA_WEB_AUTH_MODE=disabled`だけでPublic化できる設計にしない。

## 6. Documentation RAG分離

Public Demoでは、Documentation RAGを強制無効とする。

- RAG UIを表示しない、または無効状態として扱う。
- RAG AdapterをLoadしない。
- `docs/`を走査しない。
- Document Indexを作成しない。
- Retrieval、Context InjectionおよびCitationを実行しない。
- RequestまたはClient Parameterから有効化できない。

Basic Previewでは、将来次を選択可能にする。

```text
documentation_rag:
  unavailable
  disabled
  enabled
```

現在のPhase 1-exでは、RAG Port／Adapter境界の予約を行い、Public Demoにおける強制無効Contractを先に固定する。Lightning向けRAG実装そのものは今回の実装範囲に含めない。

## 7. 将来制限Hook

次のPolicy HookをAccess Profileへ保持する。

```text
rate_limit
generation_budget
cooldown
public_max_new_tokens
request_quota
cost_guard
```

初期状態：

```text
mode = "off"
```

将来候補：

```text
off
observe
enforce
```

今回、`observe`または`enforce`の実処理を完成させる必要はない。未知Mode、不正値または矛盾した設定を黙って受理しない。

制限Hookの存在は、現在制限が有効であることを意味しない。UI、Runtime Snapshotおよび運用文書で、制限が無効な状態を有効と誤表示しない。

## 8. Model交換性

Public Demo、Basic PreviewおよびConversation Coreへ特定Modelを固定しない。

Model選択は次を経由する。

```text
Model Registry
  → Model Definition
  → Model Key
  → Model Root
  → Model Adapter
```

要件：

- Public Demo Profileへ`Qwen3-4B`をHard-codeしない。
- Model File PathをWeb LayerへHard-codeしない。
- Model ID、Format、Quantization、Context LimitおよびCapabilityをModel Definitionから解決する。
- GGUF／llama.cpp以外のBackend追加をAccess Profile変更なしで行える。
- Model交換時にBasic／Public Access Policyを作り直さない。
- Capability不足時はWarning、DegradeまたはStartup Refusalを明示する。

## 9. Deployment／Compute交換性

次を相互に独立させる。

```text
Web Access Profile
Deployment Profile
Model Definition
Feature Profile
Platform Lifecycle Adapter
```

想定環境：

```text
Local Mac／Metal
Lightning Linux／Pure CPU
Lightning Linux／CUDA
Home Server／CPU
Home Server／NVIDIA CUDA
Home Server／その他GPU
External Cloud／GPU
Remote Inference
```

Public Demoの認証有無やRAG可否を、OS、GPU Vendor、Model名、Cloud Providerまたは固定Pathで判定しない。

高性能Model、高性能Home Serverまたは外部Cloudへの移行がPhase計画より早く発生しても、Deployment Profile、Model AdapterおよびModel Definitionの追加・選択変更で受け入れられること。

## 10. Platform運用境界

Repository実装担当は次を変更しない。

- Lightning API Builder
- Public URL
- Port公開設定
- Studio Machine
- Managed Secrets
- Private Bootstrap
- Sleep／Wake設定
- Credit
- 外部Cloud
- Home Server

Repository側は、Public Demo用の明示的なForeground Entry Point、Preflight、Config ContractおよびTestを提供する。

Platform上の配置・設定・起動・停止・公開操作はユーザーが行う。

## 11. Privacy／外部副作用

Public Demoでは次を追加しない。

- Prompt／回答の永続保存
- IP／Browser識別子の永続保存
- Raw Thinking保存
- File Write
- Database Write
- Tool Call
- Agent Execution
- External API Call
- RAG Document Access
- Long-term Memory

Operational LogへPrompt本文、回答本文、Credential、Secretまたは内部Pathを出さない。

## 12. Test要件

- Basic Previewが従来どおりCredentialを要求する。
- Public DemoはCredentialを要求しない。
- Public Demoは明示Profileなしに起動できない。
- Local Auth DisabledをNon-loopback Publicへ流用できない。
- Public DemoがBasic Credentialを読み取らない。
- Public DemoでDocumentation RAGを有効化できない。
- Basic Previewで将来RAG有効化余地が残る。
- Public／Basicで現在のChat UI機能が壊れない。
- Public専用Limit Hookが`off`であることを確認できる。
- 未知Access Profile／Feature Policy／Control Modeを拒否する。
- Model KeyとDeployment Profileを変更してもAccess Policy Contractが維持される。
- 既存Mac／Lightning TestをRegressionさせない。

## 13. Acceptance条件

1. Basic PreviewとPublic Demoが別Profileとして存在する。
2. Basic Previewの認証、LifecycleおよびTraffic-aware Auto-startが維持される。
3. Public Demoは明示的に認証なしで起動できる。
4. 認証無効化だけで偶発的Public化できない。
5. Public Demoの既存Phase 1機能が利用できる。
6. Public DemoでDocumentation RAGが強制無効である。
7. Public専用Rate／Budget／Cost制限は`off`であり、有効と誤表示されない。
8. 将来制限Policyを追加できるHookがある。
9. Access、Feature、Model、DeploymentおよびPlatform Lifecycleが分離される。
10. 高性能Model／Home Server／Cloud移行でWeb Access Coreの作り直しを要求しない。
11. Platform変更を実装担当が行っていない。
12. Test、変更一覧、SHA-512および未解決事項がStatusに記録される。

## 14. 今回のOut of Scope

- Rate Limiter実装
- Generation Budget実装
- Cost Guard実装
- Persistent Quota
- Account System
- Payment
- Public Documentation RAG
- Lightning Documentation RAG
- Home Server構築
- Cloud構築
- Model Download／変換
- Backend追加
- Guardrail／Judge／Agent／Tool
- Production SLA

