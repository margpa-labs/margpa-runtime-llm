# 実装担当向け Phase 1-G Minimal Web Surface Handoff

- 文書ID: `implementer_handoff_phase_1g_minimal_web_surface`
- 状態: `accepted_ready_for_implementation`
- 作成日時: `2026-07-21 09:39:52 JST`
- 更新日時: `2026-07-21 09:39:52 JST`
- Snapshot: `20260721093952`
- 作成担当: 設計者役担当Task
- 対象担当: 実装担当Task
- 正本言語: 日本語
- 要件: [phase_1g_minimal_web_surface_requirements_20260721093952.md](../requirements/phase_1g_minimal_web_surface_requirements_20260721093952.md)
- Architecture: [phase_1g_minimal_web_surface_architecture_20260721093952.md](../architecture/phase_1g_minimal_web_surface_architecture_20260721093952.md)
- ADR: [adr_0016_batch_lightning_upload_after_phase_1h_20260721093952.md](../adr/adr_0016_batch_lightning_upload_after_phase_1h_20260721093952.md)
- Roadmap: [implementation_roadmap_20260721093952.md](../architecture/implementation_roadmap_20260721093952.md)
- Phase 1-H予約要件: [post_generation_summary_mode_requirements_reservation_20260721090725.md](../requirements/post_generation_summary_mode_requirements_reservation_20260721090725.md)
- 最新Index: [documentation_index_20260721093952.md](../documentation_index_20260721093952.md)
- supersedes: なし（Phase 1-G実装開始用Handoffの初回）

## 1. Objective

既存のPhase 1 CLI／Model Adapter／Presentation機能を壊さず、Macと将来のLightning AI Studioで同じApplication Coreを利用できる、公開検証用の最小Web Surfaceを追加する。

Phase 1-Gの完成時点で、Browserから次を実行可能にする。

```text
新規Chat
一時的な複数Turn会話
Streaming回答
生成停止
Response Language変更
Max New Tokens変更
推論過程表示のON／OFF
Preview用Access Control
Health Check
```

本Phaseは本格UIではない。Phase 4でReact等へ交換可能なAPI境界と、他者がLightning上で試せる最小UIを成立させることが目的である。

## 2. Implementation Authorization

本Handoffにより、実装担当はPhase 1-Gに必要な次の変更を行ってよい。

- `pyproject.toml`
- `uv.lock`
- `config/application.toml`
- `src/`
- `tests/`
- `scripts/`
- Phase 1-Gの実行に必要なLocal Static Asset
- `docs/handoffs/implementer_status_phase_1g_minimal_web_surface_*`

実装担当は既存の要件・Architecture・Governance・ADR・Roadmap・Indexを読み取り専用として扱う。実装中に正本の変更が必要になった場合は、勝手に編集せず設計者役へ戻す。

## 3. Prohibited／Deferred Scope

Phase 1-Gでは次を実施しない。

- Phase 1-H Summary Modeの実装
- Summary Modeの未実装SwitchをUIへ表示すること
- Chat履歴の永続化
- Database／SQLite
- RAG
- Agent
- Guardrail Model
- Judge Model
- Runtime Governance本体
- User Account管理
- OAuth／OIDC
- TLS終端
- Rate Limitの本格実装
- React／Next.js／Node Build環境
- CDN／外部JavaScript／外部CSS
- Markdown HTML Rendering
- 複数Worker／複数Model Instance
- LightningへのProject Full Upload
- Lightning上でのDependency Install／Native Build／Model Transfer
- Backup、Git、GitHub公開

Lightningへの大量Uploadは、Phase 1-GとPhase 1-HをMacで受入後、一回にまとめる。Phase 1-FのLightning Native VerificationはDeferredのままであり、完了扱いにしない。

## 4. Work Package 1: Dependency／Setup

### 4.1 Dependency

次をVersion固定で追加する。

```text
Web Optional Extra
  fastapi==0.139.2
  uvicorn==0.51.0

Development／ASGI Test
  httpx==0.28.1
```

方針：

- `fastapi[standard]`は使用しない。
- `uvicorn[standard]`は初期導入しない。
- Jinja2、SSE専用Package、React、Nodeを追加しない。
- Web依存を推論Coreの必須依存へ直接混在させず、`web` Optional Extraとして分離する。
- Development Groupへ`httpx`を追加し、FastAPI／ASGI Test Clientに用いる。
- `uv.lock`を更新し、Mac 3.13.14とLightning 3.12.11の両方をSupport Pairとして維持する。

### 4.2 Setup Recipe

- MacのSetupでWeb Extraを選択できるようにする。
- Lightning Setup RecipeにもWeb Extraを含められるようRepositoryだけ更新する。
- 本PhaseではLightning上でSetup Recipeを実行しない。
- 通常同期と`llama-cpp-python` Native Rebuildの責務を混同しない。

## 5. Work Package 2: Conversation／Application Boundary

### 5.1 Conversation Contract

Web RequestのMessage履歴は、明示的なTyped Contractとして受け取る。

最低要件：

```text
Allowed Role       : user／assistant
Disallowed Role    : system／developer／tool等
Empty Content      : Reject
Invalid Type       : Reject
Oversized Request  : Explicit Reject
```

BrowserからSystem Messageを注入させない。System InstructionとResponse Language InstructionはServer側で構成する。

### 5.2 History Ownership

- Chat履歴はBrowser Tab側が所有する。
- ServerのGlobal Mutable Stateへ利用者別Historyを保持しない。
- 複数Browser／複数利用者の履歴を混在させない。
- New ChatはBrowser Stateを消去し、Server ModelをReloadしない。
- Browser Reload後の履歴復元はPhase 1-G対象外である。

### 5.3 Context Handling

- Clientから受けた履歴を順序どおりModelへ渡せるMessage Composerを追加する。
- 既存のOne-shot CLI Message Composerを壊さない。
- Context超過時に履歴を無断要約または無断切捨てしない。
- Context Limitに収まらない場合は、明示的なValidation Errorとして返す。

### 5.4 Request Override

Web Request単位で次だけをOverrideできる。

```text
response.language                : ja／en／auto
generation.max_new_tokens        : integer
presentation.thinking.visibility : hidden／visible
```

Config FileをRequestごとに書き換えない。Effective ConfigをBaseとして、Validated Request OverrideをMemory上で合成する。

`generation.thinking_mode`と`presentation.thinking.visibility`は別の設定である。Visibilityの切替だけでThinking ExecutionをON／OFFしない。

## 6. Work Package 3: Web API

### 6.1 Application Factory／Lifecycle

- FastAPI Application Factoryを追加する。
- Model／Inference Service／Presentation ServiceはDependency Injectionする。
- Server Lifecycle中にModelを一度だけLoadする。
- RequestごとのModel Reloadを禁止する。
- TestではFake Service／Fake Streamを注入できるようにする。

### 6.2 Endpoint Contract

最低限、次の責務を分離する。

```text
GET  /healthz         : Process Healthのみ
GET  /                : Minimal UI
GET  /assets/...      : Local Static Asset
GET  /api/runtime     : UIに必要なSafe Runtime情報
POST /api/chat/stream : Streaming Generation
POST /api/chat/stop   : Cooperative Cancellation
```

Path名は局所的な実装都合により軽微変更可能だが、責務、認証境界、Testabilityを維持し、Statusへ最終Contractを記録する。

### 6.3 Streaming Envelope

Streaming Eventを明示的なSchemaで返す。

最低Event候補：

```text
start
delta
thinking_delta または presentation_delta
final
cancelled
error
done
```

要件：

- Event TypeとPayloadを区別する。
- Canonical Final AnswerとThinking Presentationを混同しない。
- Final Answer前にToken上限へ到達した場合、空成功にせず、`最終回答を生成する前にToken上限へ到達しました。`相当の明示状態を返す。
- Exception Trace、Local Path、Credential、内部Object RepresentationをClientへ返さない。
- Client切断時は可能な限りGenerationをCancelする。

### 6.4 Error Mapping

最低限、次を区別する。

```text
400／422 : Invalid Input／Invalid Setting
401      : Authentication Required／Failed
409      : Generation Busy
413      : Request Too Large候補
500      : Sanitized Internal Error
503      : Runtime Not Ready候補
```

## 7. Work Package 4: Concurrency／Cancellation

Phase 1-Gは次へ固定する。

```text
ASGI Worker                 : 1
Model Load Instance         : 1
Max Concurrent Generations : 1
Second Generation          : 409 Busy
Cancellation               : Cooperative
```

- Thread-safeなGeneration Gateを設ける。
- 同時Requestで同じModel Instanceを破損させない。
- Syncなllama.cpp StreamでASGI Event Loopを長時間Blockしないよう、Thread／Iterator境界を設ける。
- Stop APIとClient Disconnectの両方からCancel可能にする。
- Cancel後にGateが確実に解放され、次Generationを開始できることをTestする。
- Server起動時に`--workers 2`等を受け付けて複数Model Loadされる状態を許さない。

## 8. Work Package 5: Preview Access Control

### 8.1 Basic Policy

Phase 1-Gの公開Access Controlは、Server-side Basic Authentication相当の最小機構とする。

CredentialはEnvironment Variableからのみ受け取る。Config、Source、Docs、Log、Responseへ保存しない。

推奨Environment Keyは実装時に確定してよいが、`MARGPA_WEB_AUTH_*` Namespaceへ統一する。

### 8.2 Fail-closed

```text
Loopback Bind + Auth Disabled
  → Local Developmentとして許可

Non-loopback Bind + Credentialあり
  → 起動許可

Non-loopback Bind + Credentialなし
  → 起動失敗
```

- `0.0.0.0`、公開Host等でCredentialなしの起動を禁止する。
- `/healthz`だけはCredential不要の最小Health Responseとする。
- `/`、Static Asset、全`/api/*`は保護する。
- Runtime InfoではPrivate Path、Environment Value、Credentialを返さない。
- Authentication Failureの比較はTiming Attackを不必要に悪化させない標準手法を用いる。

Basic AuthはPreview用であり、本番Account SystemではないことをUI／Manual／Statusへ明記する。

## 9. Work Package 6: Minimal UI

UIはRepository内のVanilla HTML／CSS／JavaScriptで構築する。

### 9.1 Required UI

```text
Chat表示領域
入力欄
送信Button
停止Button
新規Chat Button
Response Language Pull-down
Max New Tokens Integer Input
推論過程表示 ON／OFF Switch
Streaming状態／Error表示
```

### 9.2 Setting Values

```text
Response Language
  ja／en／auto

Max New Tokens
  Default: 2048

Thinking Visibility
  Default: OFF／hidden
```

### 9.3 Thinking Wording

既存初期Labelを次のように変更する。

```text
旧: 高度推論
新: 推論過程
```

UI上は`推論過程（モデル生成）`等、内部の真のChain of Thoughtを保証するものではないと分かる表記にする。

近傍へ次の意味の注記を表示する。

> 推論過程表示は、モデルが出力したThinking区間の表示を切り替えます。推論実行自体のON／OFFではありません。Max New Tokensが小さい場合、最終回答前に上限へ到達することがあります。

### 9.4 Rendering Safety

- Model OutputはTextとして表示する。
- `innerHTML`へModel Outputを直接代入しない。
- Phase 1-GではMarkdown Rendererを導入しない。
- Local Static Assetだけを使い、CDNへ依存しない。
- UIが停止／切断／Errorを区別して表示する。
- Summary Mode SwitchはPhase 1-H完成まで表示しない。

## 10. Work Package 7: Start Command

Web専用Entry Pointを追加する。

推奨名：

```text
margpa-web
```

最低Option候補：

```text
--host
--port
--profile
--registry
--model-root
--model-key
--context-size
```

要件：

- 既存`margpa-llm` CLIを変更または破壊しない。
- Default Hostは`127.0.0.1`とする。
- Default Portは衝突しにくい明示値を決め、Helpへ表示する。
- ReloadはDefault無効とする。
- Worker数は1へ固定する。
- `--help`で大文字の`HOST`、`PROFILE`等が実値ではなく仮引数名であることが利用者に分かるDescriptionを付ける。

## 11. Proposed File Boundary

実装担当は既存構造との整合を確認し、概ね次の責務分離を行う。File名は軽微変更可能だが、Web Framework固有CodeをCoreへ漏らさない。

```text
src/margpa_runtime_llm/
  web/
    app.py
    dependencies.py
    auth.py
    contracts.py
    streaming.py
    static/
      index.html
      app.css
      app.js
  application／inference/
    conversation message composition／request override
  cli／entrypoint/
    web command

tests/
  unit/
    web auth／contract／conversation／stream／cancel
  integration/
    ASGI endpoint／busy／disconnect／static safety
```

FastAPI Type、Request、Response、Depends等をDomain／Model AdapterへImportしない。

## 12. Required Tests

最低限、次を自動Testする。

### 12.1 Regression

- 既存Testが全件合格する。
- `margpa-llm generate`／`model-info`が破壊されていない。
- Existing Model Smokeが合格する。
- Default Max New Tokensが2048のままである。
- Default Thinking Visibilityがhiddenである。
- Default Display Labelが`推論過程`へ統一される。

### 12.2 Contract／Config

- ja／en／autoだけを受理する。
- Max New Tokensの範囲外、Bool、Float、文字列等を安全に拒否する。
- Clientのsystem Roleを拒否する。
- Empty Message／Invalid Historyを拒否する。
- Request OverrideがConfig Fileを変更しない。
- New ChatでModel Reloadしない。

### 12.3 Auth

- Loopback＋Auth Disabledは起動可能。
- Non-loopback＋Credentialなしは起動拒否。
- Non-loopback＋Credentialありは起動可能。
- `/healthz`以外は未認証で拒否。
- Error／Runtime Info／LogへCredentialが出ない。

### 12.4 Streaming／Concurrency

- Streaming Event順序。
- Final AnswerとThinking区間の分離。
- Hidden時にThinkingをClient表示Payloadへ混ぜない。
- Cancel後に次Generationが可能。
- Concurrent Generationは409。
- Generator Exception時にGateを解放する。
- Client Disconnect時のCancel処理。
- Final Answer前Token Exhaustionを明示する。

### 12.5 UI Safety

- Model OutputがHTMLとして注入されない。
- Static AssetがLocalだけで完結する。
- Summary Modeの未実装Controlが存在しない。
- UIに3設定だけが公開される。

## 13. Verification Commands

Repository実装後、少なくとも次を実行する。CommandはRepositoryの確定Setup Scriptに合わせて必要最小限の調整をしてよい。

```bash
./.venv/bin/ruff format --check src scripts tests
./.venv/bin/ruff check src scripts tests
./.venv/bin/mypy .
./.venv/bin/python -m compileall -q src scripts tests
./.venv/bin/pytest -q
./.venv/bin/pytest -q -m model_smoke
bash -n scripts/setup/*.sh
```

Web依存導入とLock整合も確認する。

```bash
uv lock --check
./.venv/bin/python -c "import fastapi, uvicorn, httpx; print(fastapi.__version__, uvicorn.__version__, httpx.__version__)"
```

Mac Manual Smoke候補：

```bash
./.venv/bin/margpa-web --host 127.0.0.1 --port 8000
```

公開Bind Testでは実CredentialをCommand HistoryやStatusへ記録しない。PlaceholderだけをDocsへ書く。

Manual Smokeでは次を確認する。

1. BrowserでUIが開く。
2. 日本語PromptへStreaming回答する。
3. New Chatで履歴が消える。
4. Stopで生成を中断でき、その後再生成できる。
5. ja／en／autoを切り替えられる。
6. Max New Tokens初期値が2048である。
7. Thinking Visibility初期値がOFFである。
8. ON時は`推論過程`として表示される。
9. 別Tabの履歴がServer側で混ざらない。
10. Non-loopback＋CredentialなしでFail-closedになる。

## 14. Acceptance Criteria

次をすべて満たした場合にPhase 1-G実装完了候補とする。

- Requirements／ArchitectureのMandatory項目が実装済み。
- CLI Regressionなし。
- ModelはProcess中に一度だけLoadされる。
- Browser単位のEphemeral Multi-turnが成立する。
- Streaming／Stop／New Chatが成立する。
- UIの設定は指定3項目だけである。
- Max New Tokens Defaultは2048である。
- Thinking VisibilityとThinking Executionが分離されている。
- Token Exhaustionが空Responseにならず明示される。
- Preview Access ControlがFail-closedである。
- Model Output RenderingがPlain Textとして安全である。
- 全Static／Unit／Integration／Model Smokeが合格する。
- LightningへまだFull Uploadしていない。

## 15. Implementer Status Requirement

完了後、次の新規文書を作成する。

```text
docs/handoffs/implementer_status_phase_1g_minimal_web_surface_YYYYMMDDHHMMSS.md
```

最低限、次を含める。

```text
実装概要
変更File一覧
最終Endpoint Contract
最終CLI／Entry Point
Dependency Version／Lock変更
Auth Environment Key名（値は記載禁止）
Default Host／Port
Conversation History Ownership
Model Load回数の設計根拠
Concurrency／Cancellation方式
Thinking Presentation変更
Token Exhaustionの扱い
実行した全Verification Command／Exit Code／結果
Test総数
Manual Smoke結果
未実行項目
既知の制約
Phase 1-Hへ渡すInterface
Lightning Full Uploadを実施していないこと
```

Status作成後、設計者役へRepositoryとStatusのReviewを依頼する。Accepted Review前にPhase 1-Hへ着手しない。

## 16. Stop／Escalation Conditions

次の場合は推測で進めず、実装を停止して設計者へ戻す。

- llama.cpp AdapterのPublic Contract変更が必要
- Phase 1 CLIの互換性を壊す必要がある。
- Multiple Worker／Multiple Model Loadが避けられない。
- Authentication SecretをConfig／Fileへ保存する必要が生じる。
- CDN、Node、React、本格Databaseが必要になる。
- Context Overflowを無断切捨てしないと成立しない。
- Phase 1-H Summary Modeを同時実装しないと成立しない。
- Lightningへ先にFull Uploadする必要が生じる。
- Canonical Docsの要件間に矛盾が見つかる。

## 17. Start Condition

本HandoffはAcceptedである。ユーザーの本Turnにおける「実装担当への指示書を作って」を、Phase 1-G設計の正式引き渡し指示として扱う。

実装担当は本Handoff、Requirements、Architecture、ADR、Roadmap、最新Indexを読み、Phase 1-Gだけへ着手できる。

