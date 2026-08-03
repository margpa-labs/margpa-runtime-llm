# Phase 1-G Minimal Web Surface 要件定義

- 文書ID: `phase_1g_minimal_web_surface_requirements`
- 状態: `accepted_ready_for_implementation`
- 作成日時: `2026-07-21 09:39:52 JST`
- 更新日時: `2026-07-21 09:39:52 JST`
- Snapshot: `20260721093952`
- 作成担当: 設計者役担当Task
- Decision Owner: ユーザー
- 対象: FastAPI、最小Web UI、Ephemeral Multi-turn、Preview Access Control
- 正本言語: 日本語
- Architecture: [phase_1g_minimal_web_surface_architecture_20260721093952.md](../architecture/phase_1g_minimal_web_surface_architecture_20260721093952.md)
- ADR: [adr_0016_batch_lightning_upload_after_phase_1h_20260721093952.md](../adr/adr_0016_batch_lightning_upload_after_phase_1h_20260721093952.md)
- Handoff: [implementer_handoff_phase_1g_minimal_web_surface_20260721093952.md](../handoffs/implementer_handoff_phase_1g_minimal_web_surface_20260721093952.md)
- supersedes: なし（Phase 1-G正本要件の初回）

## 1. Objective

Current Model-independent Runtimeへ、Macと将来Lightningで利用可能な最小Web Surfaceを追加する。

```text
Browser
  → Server-side Preview Access Control
  → FastAPI Application Boundary
  → Conversation／Generation Application Service
  → Existing Inference／Presentation Contracts
  → Model Port
```

Phase 1-Gは本格的なGPT風製品UIではなく、Phase 1公開候補を少人数で操作・検証できる最小構成である。

## 2. Technology Decision

```text
API Framework : FastAPI 0.139.2
ASGI Server   : Uvicorn 0.51.0／base package
API Test      : HTTPX 0.28.1
Frontend      : Vanilla HTML／CSS／JavaScript
Transport     : HTTP + Server-Sent Events
Python        : >=3.12,<3.14
```

Dependency方針：

- `fastapi[standard]`は採用しない。
- FastAPI本体とUvicorn baseを明示Pinする。
- `uvicorn[standard]`のPlatform固有Optional Dependencyを初期必須にしない。
- Jinja2、React、Node、npm、WebSocket専用Library、SSE追加Libraryを初期導入しない。
- HTTPXはASGI Test用Dev Dependencyとする。

正本確認先：

- [FastAPI PyPI](https://pypi.org/project/fastapi/)
- [Uvicorn PyPI](https://pypi.org/project/uvicorn/)
- [HTTPX PyPI](https://pypi.org/project/httpx/)

## 3. User-visible Scope

### 3.1 Chat

- 1 Browser Tabにつき1つのCurrent Chatを持つ。
- 複数Turnの`user／assistant`会話を行える。
- Streaming表示する。
- 生成をStopできる。
- New ChatでCurrent Chatを初期化できる。
- Input送信中の二重送信を防止する。
- Model／Profile／Device等の最小Runtime Statusを表示する。
- Safe Error／Warningを画面上へ表示する。

### 3.2 Settings

一般UIへ次の3項目だけを表示する。

```text
Response Language
  └─ ja／en／autoのPull-down

Max New Tokens
  └─ Integer
  └─ Initial／Default 2048

推論過程を表示
  └─ OFF／ON Switch
  └─ presentation.thinking.visibilityだけを変更
```

Settings変更はBrowser Current Chat／Request単位であり、`config/application.toml`を書き換えない。

要約モードOFF／ONはPhase 1-Hで追加する。Phase 1-Gで動かないSwitchを先に表示しない。

### 3.3 Thinking注記

UI上の表示名を次へ変更する。

```text
Config Display Label : 推論過程
UI説明名             : 推論過程（モデル生成）
```

`高度推論`は、品質が高度であると誤認させる可能性があるためDefaultから変更する。

UIに次の趣旨を明示する。

- これはModelが生成した推論形式のTextであり、真の内部思考や正しさを保証しない。
- VisibilityはThinking実行のON／OFFとは別である。
- Thinkingが無効な場合、VisibilityをONにしても推論過程は表示されない。
- Token上限によって最終回答前に生成が終了する場合がある。
- Raw Thinkingは永続保存しない。

内部Model Protocolの`<think>...</think>`は変更しない。

## 4. Conversation State

Phase 1-GではConversation HistoryをServerへ永続保存しない。

```text
Browser Memory
  └─ user／assistant Canonical Final Messages
       ↓ every request
FastAPI
  └─ validate／compose／generate
```

- BrowserはCurrent ChatのMessage列をMemory上で保持する。
- RequestごとにCurrent Message列全体をServerへ送る。
- ServerはBrowser間でConversation Stateを共有しない。
- Page ReloadでHistoryが失われてもよい。
- New ChatはBrowser MemoryをClearする。
- Server Restartで復元しない。
- 複数Saved Chatを作らないためDelete Buttonは不要である。
- History／Resume／Delete／Title／Searchは後続Phaseで扱う。

複数利用者が同じPreview Credentialを使っても、BrowserごとのMessage列が混ざらないことを必須とする。

## 5. Message Contract

Browserから受理するRoleは次だけとする。

```text
user
assistant
```

- Client指定の`system`／`tool` Roleを受理しない。
- 空Messageを拒否する。
- 最終Messageは`user`でなければならない。
- Role順序を検証し、不正列はSafe Errorとする。
- ServerがResponse Language用System Instructionを先頭へ構成する。
- Client Historyへ戻すAssistant MessageはCanonical Final Answerだけとする。
- Visible Thinkingを次TurnのAssistant Historyへ混入させない。
- Context超過時にHistoryを黙って削除・要約・切り詰めない。
- Context不足は明示Error／Warningとして返す。

## 6. API Scope

最低限の候補Endpoint：

```text
GET  /healthz
GET  /api/v1/runtime
POST /api/v1/chat/stream
GET  /
GET  /assets/*
```

### `/healthz`

- 認証不要としてよい。
- `status`以外のModel、Path、Version、Credentialを返さない。
- Readinessの詳細主張はしない。

### `/api/v1/runtime`

- 認証必須。
- Model Key、Profile Key、Device Kind、Acceleration API、Default UI Settingを返してよい。
- Absolute Path、Secret、Raw System Promptを返さない。

### `/api/v1/chat/stream`

- 認証必須。
- Validated Message列と3 Settingを受け取る。
- Server-Sent EventsでStatus、Display Delta、Warning、Completion、Safe Errorを識別可能に返す。
- CompletionにはFinish ReasonとCanonical Final Assistant Messageを含める。
- Hidden ThinkingをClientへ送信しない。

## 7. Streaming／Cancellation

- Browserは`AbortController`等でStreaming RequestをCancelする。
- ServerはDisconnectを検出し、Native Generation StreamへCooperative Cancelを伝播する。
- Cancel後もModel Runtimeを再利用可能である。
- Cancelled ResponseをAssistant HistoryへCompleted Messageとして追加しない。
- Terminal Eventは1回だけ発生する。
- StreamingとNon-streaming内部Contractを重複実装しない。
- UI Status表示の遅延でModel GenerationをBlockしない。

Phase 1-Gは1 Process／1 Worker／1 Model Instanceとする。

- 同時Generationは1件だけ許可する。
- Busy時は無制限Queueに積まず、SafeなBusy Responseを返す。
- ModelをRequestごとにLoadしない。
- Startup／Lifespanで1回Loadし、Shutdownで1回Unloadする。

## 8. Preview Access Control

Phase 1-GのAccess Controlは、公開製品認証ではなく少人数Preview用Server-side Basic Authenticationとする。

Environment候補：

```text
MARGPA_WEB_AUTH_MODE=disabled|basic
MARGPA_WEB_AUTH_USERNAME=...
MARGPA_WEB_AUTH_PASSWORD=...
```

要件：

- Default Bindは`127.0.0.1`とする。
- Loopback BindではAuth Disabledを許可する。
- `0.0.0.0`等Non-loopback BindではBasic Authを必須とし、Credential不足ならStartupをFail Closedする。
- CredentialはEnvironmentからだけ受け取る。
- CredentialをTOML、Source、Log、Error、HTML、API Responseへ出さない。
- 比較はTiming Attackを避ける標準のConstant-time Compareを使用する。
- `/healthz`以外のUI、Assets、APIを同じAccess Controlで保護する。
- Interactive API Docs／ReDocは初期版で公開しない。
- Query Parameter／URLへTokenを入れない。
- Client-side JavaScriptだけのPassword判定を行わない。
- TLS終端はLightning等の信頼できるReverse Proxyへ委ねる。直接InternetへPlain HTTP公開しない。

## 9. Web Security／Privacy

- Model Outputを`innerHTML`で描画しない。
- Plain Textとして安全に表示する。
- 初期版でMarkdown HTML Renderingを行わない。
- External CDN／External JavaScript／External Fontを使わない。
- Static AssetはRepository内へ保持する。
- Broad CORSを有効にしない。
- Same-origin前提とする。
- `Cache-Control: no-store`等の適切なResponse Headerを検討する。
- Credential、Message、Model OutputをAccess Logへ本文として残さない。
- Traceback、Absolute Path、Environment VariableをClientへ返さない。
- Error Responseは既存`InferenceError.safe_message`思想を継承する。

Phase 1-GはGuardrail、Prompt Injection Defense、Content Safetyを実装したとは主張しない。

## 10. Config／Runtime Behavior

- UIはTracked TOMLを直接編集しない。
- UI DefaultはEffective Configから取得する。
- Response Languageは`ja／en／auto`だけを許可する。
- Max New Tokensは正のInteger、Phase 1-G上限2048とする。
- Thinking Visibilityは`hidden／visible`へMappingする。
- Thinking ExecutionはUI Visibilityから暗黙変更しない。
- Model Root、Profile、Model Key、Context Size等はServer Startup Configとし、一般UIから変更しない。
- Config SourceとRequest OverrideをAudit可能な境界として分離する。

## 11. CLI／Entrypoint

候補Command：

```text
margpa-web
```

要件：

- Current CLI `margpa-llm`を壊さない。
- Web EntrypointはCLIのPrivate FunctionをImportしない。
- Host、Port、Profile、Registry、Model Root等のStartup Optionを提供できる。
- Worker数は1に固定する。
- Development Auto Reloadを公開候補で使用しない。
- Non-loopback BindとAuthの整合をStartup前に検証する。

## 12. Dependency／Setup

候補`pyproject.toml`構造：

```toml
[project.optional-dependencies]
web = [
  "fastapi==0.139.2",
  "uvicorn==0.51.0",
]

[dependency-groups]
dev = [
  "httpx==0.28.1",
]
```

実際のTOML構造は既存GroupとMergeし、重複Tableを作らない。

- `uv.lock`を更新する。
- Mac Setup Recipeへ`--extra web`を追加する。
- Lightning Setup Recipeも最終搬入前に`--extra web`対応へ更新する。
- Native `llama-cpp-python` Build手順とWeb Dependency Syncを混同しない。
- Requirements.txtはPhase 1-G必須正本にせず、Public Packaging時に必要性を再評価する。

## 13. Test Requirements

### Unit／Contract

- API Request Schema
- Role／Order Validation
- Language／Token／Visibility Validation
- Context Errorの非破壊動作
- Safe Error Mapping
- Basic Auth Success／Failure／Missing Credential
- Non-loopback Fail Closed
- Secret Redaction
- Busy Response
- Thinking Hidden／Visible
- Canonical FinalとDisplay Contentの分離

### ASGI

- HTTPXによるIn-process ASGI Test
- Fake Model Port／Fake StreamをDependency Injectionする。
- `/healthz`
- Runtime Metadata Redaction
- SSE Event Order
- Completion 1回
- Client Disconnect／Cancel
- Static Asset配信
- AuthでUI／Assets／APIが同じく保護される。

### Native／Manual

- Mac 3.13.14／MetalでServer Startup
- Browserから日本語／英語／auto
- Multi-turn
- Streaming
- Stop後の再生成
- New Chat
- Max New Tokens 2048
- Thinking Visibility注記
- ModelをRequestごとに再Loadしない。
- Existing CLI／Model Smoke Regression

## 14. Acceptance Criteria

- FastAPI／UvicornをEntrypointへ局所化できている。
- Browser間でConversationが混ざらない。
- New ChatがCurrent BrowserだけをResetする。
- Settings 3項目がRequest Overrideとして動く。
- Tracked TOMLを書き換えない。
- Streaming／Stop／Post-cancel Generationが成立する。
- Hidden ThinkingがClientへ漏れない。
- Public BindがCredentialなしで起動しない。
- Model OutputをHTMLとして実行しない。
- Modelを1回Load／1回Unloadする。
- Full Static／Default／Mac Native TestがPassする。
- Phase 1-HとLightning Full Uploadを実行していない。

## 15. Out of Scope

- Conversation永続化
- Chat History／Resume／Delete／Title／Search
- Regenerate
- Multiple Model選択
- TOML Editor／Save／Diff
- Developer／Research Setting UI本体
- Post-generation Summary Mode実装
- Runtime Governance／ARGD／DAGD
- Guardrail／Judge／Repair／Agent／RAG
- Rate Limiting本格実装
- OAuth／OIDC／User Account
- Markdown／Code Highlighting
- React／Next.js／Node Build
- Lightning Full Upload／Live URL公開

## 16. Authorization Boundary

本要件とHandoffにより、実装担当はPhase 1-GのRepository変更とMac検証を開始できる。

Phase 1-H、Lightning Full Upload、Model Transfer、Lightning Dependency Sync／Native Build、Backup、Git、GitHub公開は許可しない。
