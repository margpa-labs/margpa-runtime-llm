# 実装担当 Phase 1-G Minimal Web Surface Status

- 文書ID: `implementer_status_phase_1g_minimal_web_surface`
- 状態: `implementation_complete_waiting_designer_review`
- 作成日時: `2026-07-21 10:50:05 JST`
- 更新日時: `2026-07-21 10:50:05 JST`
- Snapshot: `20260721105005`
- 作成担当: 実装担当Task
- 正本言語: 日本語
- Documentation Index: [documentation_index_20260721093952.md](../documentation_index_20260721093952.md)
- Requirements: [phase_1g_minimal_web_surface_requirements_20260721093952.md](../requirements/phase_1g_minimal_web_surface_requirements_20260721093952.md)
- Architecture: [phase_1g_minimal_web_surface_architecture_20260721093952.md](../architecture/phase_1g_minimal_web_surface_architecture_20260721093952.md)
- ADR: [adr_0016_batch_lightning_upload_after_phase_1h_20260721093952.md](../adr/adr_0016_batch_lightning_upload_after_phase_1h_20260721093952.md)
- Implementer Handoff: [implementer_handoff_phase_1g_minimal_web_surface_20260721093952.md](implementer_handoff_phase_1g_minimal_web_surface_20260721093952.md)

## 1. Authorization／Scope

ユーザーの「最新Indexと、Handoff、他、中に記載のある関連文章を読んで作業」指示に基づき、Phase 1-G Minimal Web SurfaceだけをRepositoryへ実装し、Macで検証した。

Phase 1-H Summary Mode、Conversation永続化、React／Node、Lightning Full Upload／Dependency Install／Native Build／Model Transfer、Backup、Git、GitHub公開は実施していない。Canonical Requirements／Architecture／ADR／Roadmap／Indexは読み取り専用として扱い、既存文書を編集していない。

## 2. Implementation Summary

```text
Delivery Adapter       : FastAPI／Uvicorn
Frontend               : Local Vanilla HTML／CSS／JavaScript
Transport              : HTTP + Server-Sent Events
Conversation Ownership : Browser Tab Memory
Persistence            : None
Model Lifecycle         : LifespanごとにLoad 1回／Unload 1回
ASGI Worker             : 1
Concurrent Generation  : 1／Second Requestは409
Cancellation           : Stop API + Client Disconnect／Cooperative
Preview Access         : Server-side Basic Auth
Default Bind           : 127.0.0.1:8000
Rendering              : Plain Text／textContent
```

FastAPI固有型をInference／Presentation Domain Contractへ入れず、既存Model Port／llama.cpp AdapterのPublic Contractを変更していない。既存AdapterのNon-blocking Generation Lockを維持し、その外側へWeb Application用のActive Request GateとCancellation管理を追加した。

## 3. Changed Files

### Dependency／Config／Setup

- `pyproject.toml`
- `uv.lock`
- `config/application.toml`
- `scripts/setup/setup_macos_arm64_metal.sh`
- `scripts/setup/setup_lightning_linux_x86_64_cuda.sh`
- `scripts/models/phase1f_cross_environment_acceptance.py`

### Source

- `src/margpa_runtime_llm/bootstrap/web_application.py`
- `src/margpa_runtime_llm/entrypoints/web/__init__.py`
- `src/margpa_runtime_llm/entrypoints/web/main.py`
- `src/margpa_runtime_llm/modules/conversation/__init__.py`
- `src/margpa_runtime_llm/modules/conversation/contracts.py`
- `src/margpa_runtime_llm/modules/conversation/application/__init__.py`
- `src/margpa_runtime_llm/modules/conversation/application/conversation_generation.py`
- `src/margpa_runtime_llm/modules/conversation/public.py`
- `src/margpa_runtime_llm/modules/presentation/contracts/thinking.py`
- `src/margpa_runtime_llm/orchestration/response_language.py`
- `src/margpa_runtime_llm/web/__init__.py`
- `src/margpa_runtime_llm/web/app.py`
- `src/margpa_runtime_llm/web/auth.py`
- `src/margpa_runtime_llm/web/contracts.py`
- `src/margpa_runtime_llm/web/error_mapping.py`
- `src/margpa_runtime_llm/web/streaming.py`
- `src/margpa_runtime_llm/web/static/index.html`
- `src/margpa_runtime_llm/web/static/app.css`
- `src/margpa_runtime_llm/web/static/app.js`

### Tests

- `tests/unit/conversation/test_conversation_generation.py`
- `tests/unit/web/test_auth.py`
- `tests/unit/web/test_web_cli.py`
- `tests/integration/web/test_web_app.py`
- `tests/unit/presentation/test_thinking_presentation.py`
- `tests/unit/inference/test_cli.py`
- `tests/unit/inference/test_config_and_registry.py`
- `tests/integration/llama_cpp/test_phase1b_runtime.py`

### Status

- `docs/handoffs/implementer_status_phase_1g_minimal_web_surface_20260721105005.md`

## 4. Dependency／Lock／Setup

```text
Web Optional Extra
  fastapi==0.139.2
  uvicorn==0.51.0

Development Group
  httpx==0.28.1

Resolved Lock
  122 packages
```

`fastapi[standard]`、`uvicorn[standard]`、Jinja2、SSE専用Package、React、Node、CDN Dependencyは追加していない。

Mac／Lightning Setup Recipeへ`--extra web`を追加した。Web Dependency Syncと`llama-cpp-python` Native Buildの既存責務分離は維持し、今回のWeb同期では既存Metal版`llama-cpp-python`を再Install／再Buildしていない。

`requires-python = ">=3.12,<3.14"`を維持し、Mac 3.13.14／Lightning 3.12.11 Support Pairを変更していない。

## 5. Final CLI／Entrypoint

追加Entry Point：

```text
margpa-web
```

Option：

```text
--host HOST
--port PORT
--profile PROFILE_PATH
--registry MODEL_DEFINITION_PATH
--model-root MODEL_ROOT
--model-key MODEL_KEY
--context-size TOKENS
```

```text
Default Host : 127.0.0.1
Default Port : 8000
Reload       : Disabled
Workers      : 1／固定
```

既存`margpa-llm` Entry Point、`generate`、`model-info`を変更していない。Web EntrypointからCLI Private FunctionをImportしていない。

## 6. Final Endpoint／SSE Contract

```text
GET  /healthz                : Unauthenticated／{"status":"ok"} only
GET  /                       : Protected Minimal UI
GET  /assets/*               : Protected Local Static Asset
GET  /api/v1/runtime         : Protected Safe Runtime Metadata
POST /api/v1/chat/stream     : Protected Validated Conversation／SSE
POST /api/v1/chat/stop       : Protected Cooperative Cancellation
```

SSE Event：

```text
Non-terminal : start／delta／warning
Terminal     : completed／cancelled／errorのいずれか1回
```

`completed`はCanonical Final Assistant Message、Finish Reason、利用可能なToken Usageを返す。Visible Thinkingは現在画面用の`delta`だけに含め、Canonical Assistant Historyへ入れない。Hidden ThinkingはClient Payloadへ送らない。Streaming開始前のBusy／Context等はHTTP Error、開始後の安全なFailureはSSE `error`として返す。

## 7. Conversation／Config Boundary

Browserは`user／assistant`のCanonical Message列をTab Memory上で保持し、Requestごとに全列を送信する。ServerはConversation Historyを永続化せず、利用者間のHistoryを共有しない。

Validation：

```text
Allowed Role              : user／assistant
First／Final Role          : user
Role Order                : user／assistant交互
Max Messages              : 64
Max Characters／Message   : 32768
Max Total Characters      : 131072
Client system／tool Role  : Reject
Empty Message             : Reject
```

Request Overrideは次の3項目だけである。

```text
response.language                : ja／en／auto
generation.max_new_tokens        : Strict Integer／1～2048
presentation.thinking.visibility : hidden／visible
```

Effective ConfigをMemory上でCopyし、`config/application.toml`をRequestごとに変更しない。Visibility Overrideは`generation.thinking_mode`を変更しない。

## 8. Lifecycle／Concurrency／Cancellation

FastAPI Lifespan開始時にComposition Rootを1回実行し、Modelを1回Loadする。RequestおよびNew ChatではModelをReloadしない。ShutdownではActive GenerationへCancelを要求して終了を待ち、その後Modelを1回Unloadする。

同期llama.cpp Iteratorは専用Threadで消費し、Bounded Async Queueを通してSSEへ渡すため、ASGI Event LoopをGenerationでBlockしない。

```text
Conversation Gate acquire成功 → Generation開始
Conversation Gate busy        → HTTP 409／model_busy
Stop API                      → Active request_idへCancel Event
Client Disconnect            → Cooperative Cancel Event
Terminal／Error／Cancel       → Stream Close + Gate Release
Post-cancel                  → 次Generationを許可
```

Server Global Mutable StateはActive Generation Session 1件だけであり、Conversation Message列は保存しない。

## 9. Preview Access／Security

Environment Key名：

```text
MARGPA_WEB_AUTH_MODE=disabled|basic
MARGPA_WEB_AUTH_USERNAME
MARGPA_WEB_AUTH_PASSWORD
```

Credential値はSource、TOML、Docs、Log、HTML、API Responseへ記録していない。PolicyのRepresentationからもCredential Fieldを除外した。比較は`secrets.compare_digest`を使用する。

```text
Loopback + disabled                    : Start可能
Non-loopback + disabled                : Startup前にFail Closed
basic + Credential不足                 : Startup前にFail Closed
basic + Credentialあり                 : Server-side認証
/healthz                               : 例外として未認証
UI／Assets／全API                       : 同じ認証境界
Interactive API Docs／ReDoc／OpenAPI   : Disabled
```

Model OutputはDOM `textContent`で描画する。`innerHTML`、Markdown HTML Rendering、External CDN／Script／Fontを使用していない。`Cache-Control: no-store`、CSP、`nosniff`、`no-referrer`を付与する。Uvicorn Access Logは初期Entry Pointで無効化した。

Basic Authは少人数Preview Gateであり、本番Account／Role／Permission／Governance機能ではない。Non-loopback公開時のTLS終端は信頼できるReverse Proxy側の責務として維持する。

## 10. Thinking Presentation／Token Exhaustion

Default Display Labelを次へ変更した。

```text
旧 : 高度推論
新 : 推論過程
UI : 推論過程（モデル生成）
```

Canonical Protocol `<think>...</think>`とParser Contractは変更していない。UIには、表示SwitchがThinking実行のON／OFFではないこと、内容の正しさや真の内部思考を保証しないこと、Token上限、Raw Thinking非永続化を明示した。

`finish_reason=length`かつCanonical Finalが空の場合、空成功にせず次のWarning Code／Messageを返す。

```text
code    : final_answer_token_limit
message : 最終回答を生成する前にToken上限へ到達しました。
```

## 11. Automated Verification

### Dependency／Entrypoint

```text
uv lock                                           : Exit 0／122 packages
uv sync --frozen --extra web ...                  : Exit 0／Native llama-cpp再Buildなし
uv lock --check --offline                         : Exit 0／122 packages
python import fastapi, uvicorn, httpx              : Exit 0／0.139.2 0.51.0 0.28.1
margpa-web --help                                  : Exit 0
margpa-llm --help                                  : Exit 0
```

初回Sandbox内`uv lock`は共有uv CacheへのAccess制限でExit 2となった。Repository／Lock内容のFailureではないため、同一CommandをSandbox外で再実行しExit 0を確認した。

### Static／Default Gate

```text
ruff format --check src scripts tests             : Exit 0／88 files
ruff check src scripts tests                      : Exit 0
mypy .                                            : Exit 0／88 source files
python -m compileall -q src scripts tests         : Exit 0
bash -n Mac Setup／Lightning Setup／Preflight      : Exit 0
pytest -q                                         : Exit 0／209 passed、3 deselected
```

Targeted Conversation／Web Testの最終結果は`26 passed`である。初回Targeted Testでは、Credential Redaction TestのAssertion文字列が一般語`preview`と衝突して1件失敗した。Credential固有値を使うTestへ修正し、Production Codeを緩めず合格させた。

### Native Model Smoke

```text
pytest -q -m model_smoke／Sandbox外Metal : Exit 0
Result                                  : 2 passed、1 skipped、209 deselected
Skip                                    : Lightning Profile Environment未指定
```

Sandbox内の初回Native実行はMetal Deviceが`null`となりCommand Queueを作成できずExit 1だった。Verbose既存Smokeで同一原因を確認し、Source変更を行わずSandbox外のNative Metal条件で再実行して2件合格した。Model Artifact、Hash、Build Version、Runtime ContractのFailureではない。

## 12. Mac Manual Browser Smoke

実Model／Metalの`margpa-web --host 127.0.0.1 --port 8765`を起動し、終了時はGraceful Shutdown／Exit 0を確認した。

```text
UI表示／Local Asset                : Pass
Safe Runtime Status                : Pass／Model・Profile・gpu・metal
Default Max New Tokens             : Pass／2048
Default Thinking Visibility        : Pass／OFF
Japanese Streaming                 : Pass
Ephemeral Multi-turn               : Pass／直前回答を再利用
New Chat                           : Pass／Browser Current ChatのみReset
Response Language en               : Pass／English Response
Max New Tokens Request Override    : Pass／64
Thinking Visibility ON             : Pass／Execution Settingは変更なし
Stop                               : Pass／Generating中に停止
Post-cancel Generation             : Pass／停止後に再生成成功
Second Browser Tab Isolation       : Pass／新規空History
Browser Console Error／Warning     : None
Non-loopback + Auth Disabled       : Expected Exit 2／Fail Closed
```

Cancelled Generationの部分表示はCurrent Screenに残るが、Completed Assistant HistoryとしてBrowser Message列へ追加しない。停止後の次Requestは新しいCanonical Historyとして正常に生成できた。

## 13. Known Limits／Unexecuted

- ConversationはPage Reloadで失われる。
- Saved Chat、Resume、Delete、Title、Search、Regenerateは未実装である。
- Plain Text表示のみでMarkdown Renderingはない。
- 1 Process／1 Worker／1 Model Instanceである。
- Basic AuthはPreview用であり、User Account、OAuth／OIDC、Rate Limit、TLS終端を提供しない。
- CancelはNative Chunk境界でのCooperative方式であり、瞬時の強制停止を保証しない。
- Phase 1-H Summary ModeのUI Control／Config／Inferenceは未実装である。
- Lightning Full Upload、Dependency Sync、CUDA／CPU Native Gate、Live URL Testは未実行である。
- Phase 1-F Lightning Native GateはDeferred／Not Completeのままである。
- Phase 1完了、Backup、Phase 1-ex、Git／GitHub公開は未実行である。

## 14. Phase 1-H Interface

Phase 1-Hは、`ConversationGenerationService`が生成したCanonical Final AnswerとSSE `completed`境界の間へ、Application-level Summarization Portとして追加できる。

```text
Normal Generation
  → Thinking Normalize
  → Canonical Final Answer
  → Phase 1-H Summarization Port候補
  → Presentation／completed
```

Phase 1-G Web EntrypointからMain Modelを直接2回呼ぶ必要はない。Browser Historyへ戻すMessageは、Phase 1-H正本で決定される最終Canonical Outputに置換可能である。Current Active Generation Gate／Cancellationは、将来のNormal GenerationとSummary Generationを同一Sequential Sessionとして扱える境界を持つ。

## 15. Review Request

Phase 1-G Repository実装、Automated Gate、Mac Native Model Smoke、Manual Browser Smokeは完了候補である。設計者役にはRequirements／Architecture／Security／SSE Contract／Manual Evidenceと本StatusのReviewを依頼する。

Accepted Review前にPhase 1-Hへ着手せず、Lightning Full Uploadも行わない。
