# Phase 1-G Minimal Web Surface Architecture

- 文書ID: `phase_1g_minimal_web_surface_architecture`
- 状態: `accepted_ready_for_implementation`
- 作成日時: `2026-07-21 09:39:52 JST`
- 更新日時: `2026-07-21 09:39:52 JST`
- Snapshot: `20260721093952`
- 作成担当: 設計者役担当Task
- 正本言語: 日本語
- Requirements: [phase_1g_minimal_web_surface_requirements_20260721093952.md](../requirements/phase_1g_minimal_web_surface_requirements_20260721093952.md)
- ADR: [adr_0016_batch_lightning_upload_after_phase_1h_20260721093952.md](../adr/adr_0016_batch_lightning_upload_after_phase_1h_20260721093952.md)
- supersedes: なし（Phase 1-G Architecture系列の初回）

## 1. Architectural Goal

Web FrameworkをApplication Coreにせず、Current Inference／Presentation Contractの外側へ交換可能なDelivery Adapterとして追加する。

```text
Vanilla Browser UI
        ↓ HTTP／SSE
FastAPI Entrypoint
        ↓ Typed Request／Application Call
Conversation Generation Orchestration
        ├─ Response Language Policy
        ├─ Generation Parameters
        ├─ Thinking Presentation
        └─ Cancellation
        ↓
Inference Service／Model Port
        ↓
llama.cpp Adapter／Qwen3-4B
```

## 2. Dependency Direction

```text
entrypoints/web／api
        ↓
orchestration／conversation application
        ↓
modules/inference + modules/presentation

bootstrap
        └─ concrete adapterとentrypointを接続
```

禁止：

- UIから`LlamaCppModelAdapter`を直接呼ぶ。
- FastAPI TypeをInference／Presentation Domain Contractへ入れる。
- Web EntrypointからCLIのPrivate FunctionをImportする。
- Model Output Protocol ParsingをJavaScriptへ再実装する。
- BrowserからSystem Messageを自由指定させる。
- Server Global Listへ全利用者のConversationを保存する。

## 3. Proposed Directory Additions

実装担当は既存構造へ最小限次を追加できる。

```text
src/margpa_runtime_llm/
├─ modules/
│  └─ conversation/
│     ├─ contracts/
│     └─ application/
├─ orchestration/
│  └─ conversation_generation.py
├─ bootstrap/
│  └─ web_application.py
└─ entrypoints/
   ├─ api/
   │  ├─ app.py
   │  ├─ schemas.py
   │  ├─ access_control.py
   │  ├─ error_mapping.py
   │  └─ streaming.py
   └─ web/
      ├─ main.py
      └─ static/
         ├─ index.html
         ├─ app.css
         └─ app.js

tests/
├─ unit/conversation/
├─ unit/web/
├─ contract/web/
└─ integration/web/
```

実際のFile分割は責務が小さい限り調整可能である。巨大な`app.py`へAuth、Schema、Streaming、Model Lifecycleを集約しない。

## 4. Composition／Lifecycle

```text
margpa-web Start
  → Startup Option／Environment Validate
  → Access Policy Validate
  → build_phase1_application系Composition
  → Model Load once
  → FastAPI serves requests／1 worker
  → Shutdown
  → Active Generation Cancel／Close
  → Model Unload once
```

Model Load失敗時はServerを半端に公開しない。Safe Logを出してStartup Failureとする。

FastAPI App FactoryはTest用のApplication Service／Fake Model Portを注入できる形にする。

## 5. Browser-owned Ephemeral Conversation

ConversationはBrowser Memoryが正本となる。

```text
Browser A messages[] ──request──┐
                               ├─ Stateless API Request Validation
Browser B messages[] ──request──┘
```

ServerはRequest終了後にConversation Message列を保存しない。このため、Shared Basic Credentialでも利用者間のHistoryが混ざらない。

Browserが保持するAssistant Messageは、Presentation済み全文ではなくCanonical Final Answerとする。

```text
Model Raw Output
  → Thinking Parser
      ├─ reasoning_content／ephemeral
      └─ final_content／conversation history
  → Presentation display_content／current screen only
```

## 6. Request Composition

Browser Request：

```json
{
  "messages": [
    {"role": "user", "content": "..."},
    {"role": "assistant", "content": "..."},
    {"role": "user", "content": "..."}
  ],
  "settings": {
    "response_language": "ja",
    "max_new_tokens": 2048,
    "thinking_visibility": "hidden"
  }
}
```

Server側：

```text
Validate user／assistant history
  → Resolve Response Language
  → Prepend Server-owned System Instruction
  → Copy Effective Generation Config with request max_new_tokens
  → Resolve Thinking Presentation with request visibility
  → GenerationRequest
```

Current `compose_generation_messages`を無理にWebへ流用してHistoryを失わないよう、Backend-independentなConversation Message Composerを追加する。

## 7. SSE Event Envelope

候補：

```text
event: status
data: {"state":"generating","request_id":"..."}

event: delta
data: {"text":"..."}

event: warning
data: {"code":"...","message":"..."}

event: completed
data: {
  "request_id":"...",
  "finish_reason":"stop",
  "assistant_message":{"role":"assistant","content":"..."},
  "usage":{...}
}

event: error
data: {"code":"...","message":"..."}
```

要件：

- JSONはUTF-8／`ensure_ascii=false`相当。
- Terminal Eventは`completed／cancelled／error`のいずれか1回。
- Hidden ReasoningをDeltaへ出さない。
- Clientは未知Eventを無視できる。
- Raw ExceptionをDataへ入れない。
- Keepaliveが必要なら意味を持たないCommentとして送る。

## 8. Sync Model／Async Web Boundary

llama.cpp Generationは同期Iteratorである。Event Loopを直接Blockしないよう、FastAPI／StarletteのThreadpoolまたは明示的Worker Thread境界を使用する。

同時実行制御：

```text
Process-wide Non-blocking Generation Lock
  ├─ acquired → generate
  └─ busy     → 409／runtime_busy
```

- 無制限Queueを作らない。
- LockはTerminal／Error／Disconnectの全経路でReleaseする。
- Stream ObjectはContext ManagerでCloseする。
- Browser Disconnect時に`cancel()`する。
- Cancel完了後のGenerationが成立することをTestする。

## 9. Access Control Boundary

Entrypoint Middleware／Dependencyが次を担う。

```text
Loopback + disabled
  → allowed

Non-loopback + basic + valid credentials
  → allowed

Non-loopback + disabled／missing credentials
  → startup denied
```

Credential ValidationはServer-sideで行い、`secrets.compare_digest`等を使用する。

保護対象：

```text
/
/assets/*
/api/v1/*
```

例外：

```text
/healthz
  → {"status":"ok"} only
```

Basic AuthはPreview Gateであり、User／Role／権限管理、DAAGD、Tool Permissionではない。

## 10. Static UI

Vanilla UIはAPI契約だけに依存する。

```text
Header
  ├─ Project Name
  ├─ Model／Device Status
  └─ New Chat

Chat Main
  ├─ Message List
  ├─ Runtime／Warning Status
  ├─ Input
  ├─ Send
  └─ Stop

Settings
  ├─ Response Language
  ├─ Max New Tokens
  └─ 推論過程を表示
```

- Text描画は`textContent`を基本とする。
- HTML／ScriptとしてModel Outputを解釈しない。
- CSS／JSをInlineへ大量埋め込みせずLocal Static Assetへ分離する。
- External CDNを使わない。
- UIは日本語を正本とする。
- React移行時もAPI Contractを維持する。

## 11. Thinking Presentation

Default Labelを`推論過程`へ変更する。

```text
Canonical Protocol : <think>...</think>
Display Label      : <推論過程>...</推論過程>
UI Heading         : 推論過程（モデル生成）
```

BrowserにRaw Protocol Tag処理を持たせず、Python Presentation ServiceがDisplay Deltaを生成する。

Visibility SwitchはPresentationだけを変更し、`generation.thinking_mode`を変更しない。

## 12. Config／Dependency

FastAPI／Uvicornは`web` Optional Extraへ置く。HTTPXはDev Groupへ置く。

```text
Application Config／Profile
  → Startup Defaults

Browser Settings
  → Request Override
  → no TOML write
```

Web SecretはConfig Loaderの一般Configへ混在させず、Entrypoint専用Environment Readerで扱う。

## 13. Error Mapping

Existing `InferenceErrorCode`をHTTP／SSEへSafe Mappingする。

候補：

```text
invalid_request／validation      → 400 or 422
authentication_required         → 401
runtime_busy                    → 409
context_limit_exceeded          → 400
model_not_loaded／backend error → 503
unexpected                     → 500／generic safe message
```

HTTP StatusとSSE Terminal Errorの二重終了を避ける。Streaming開始前のErrorはHTTP Response、開始後はSSE Error Eventで返す。

## 14. Test Architecture

```text
Fake Model Port
  → Deterministic chunks／finish reason／cancel
  → Conversation Application
  → FastAPI App Factory
  → HTTPX ASGI Transport
  → SSE／Auth／Static assertions
```

Native Model Testは少数の`model_smoke`へ限定する。Unit／ASGI TestでModel Fileを要求しない。

Browser手動Testは、Mac Localhostでユーザーが実行可能なManualを後続作成する。

## 15. Future Replacement

```text
Current Frontend : Vanilla HTML／CSS／JS
Future Frontend  : React等
Stable Boundary  : /api/v1 + SSE Contract
```

Phase 1-HではConversation Applicationの後段へSummarization Portを追加する。Web EntrypointからMain Modelを2回直接呼ばない。

## 16. Authorization Boundary

本ArchitectureはPhase 1-G実装の設計正本である。

Phase 1-H Summarization、Lightning Full Upload、History Storage、React、Governance、Guardrail、Git／GitHub操作は対象外である。
