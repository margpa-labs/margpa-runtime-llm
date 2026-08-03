# Phase 1-H 実装者Status — Summary Mode and UI Language

- 更新時点: 2026-07-21 18:12:02 JST
- 担当: 実装者役担当Task
- 対象: Phase 1-H Summary Mode／UI Language
- 状態: 実装・自動検証・Mac Metal実Model検証・Browser手動検証 完了、設計者Review待ち
- 正本取扱い: Requirements／Architecture／Governance／ADR／Index／Designer Handoffは読み取り専用

## 1. 実施Scope

Phase 1-GのConversation／Web Runtimeを維持したまま、次を実装した。

- Summary Mode `off | post_generation`
- 同一Main Modelによる通常回答→要約の直列2段Pipeline
- Summary失敗時のOriginal Answer fallback
- Application Config schema `2` → `3`
- Runtime DefaultsへのSummary Mode追加
- 日本語／英語のBrowser-only UI切替
- UI Languageの専用localStorage保持
- Summary／UI LanguageのUnit・Integration・実Model Test

後続Phase、Lightning upload、Model転送、Backup、Git／GitHub作業には進んでいない。

## 2. 変更File

### Runtime／Config

- `config/application.toml`
- `src/margpa_runtime_llm/bootstrap/config_loader.py`
- `src/margpa_runtime_llm/bootstrap/web_application.py`
- `src/margpa_runtime_llm/modules/conversation/contracts.py`
- `src/margpa_runtime_llm/modules/conversation/application/conversation_generation.py`
- `src/margpa_runtime_llm/modules/conversation/public.py`
- `src/margpa_runtime_llm/modules/summarization/__init__.py`
- `src/margpa_runtime_llm/modules/summarization/contracts.py`
- `src/margpa_runtime_llm/modules/summarization/public.py`
- `src/margpa_runtime_llm/orchestration/summarization.py`
- `src/margpa_runtime_llm/web/contracts.py`
- `src/margpa_runtime_llm/web/static/index.html`
- `src/margpa_runtime_llm/web/static/app.css`
- `src/margpa_runtime_llm/web/static/app.js`

### Test

- `tests/unit/conversation/test_conversation_generation.py`
- `tests/unit/summarization/test_summary_contract.py`
- `tests/unit/inference/test_config_and_registry.py`
- `tests/unit/inference/test_cli.py`
- `tests/integration/web/test_web_app.py`
- `tests/integration/llama_cpp/test_phase1b_runtime.py`

新規Dependency、`pyproject.toml`、`uv.lock`、CLI Contractの変更はない。

## 3. Directory／Contract

- `modules/summarization/`を新設し、Summary Mode、Backend、Failure Policy、Application-owned Configを型Contract化した。
- `orchestration/summarization.py`がserver-owned Summary Promptを構成する。
- Browser／FastAPIからInferenceを2回直接呼ばず、`ConversationGenerationService`配下の1 Sessionだけが2段処理を統治する。
- `ConversationEventType.STATUS`を追加した。
- `ConversationSettings.summary_mode`を追加した。
- `RuntimeDefaults.summary_mode`を追加した。
- OFF時のSSE順序は `start → delta* → warning* → completed` のまま維持した。

## 4. Config Migration

`config/application.toml`をschema `3`へ更新し、次を追加した。

```toml
[layers.summarization]
mode = "off"
backend = "main_model"
max_new_tokens = 1024
thinking_mode = "disabled"
preserve_original = true
failure_policy = "fallback_original"
```

- Deployment Profile schemaは変更していない。
- `max_new_tokens`は`1024`固定。
- Main Model以外、Thinking有効、Original非保持、非fallback policy、未知Fieldを拒否する。
- 旧Application schema `2`は暗黙受理しない。
- Runtime APIはApplication Configのdefault Summary Modeを返す。

## 5. Summary Prompt Boundary

Summary Requestへ渡すSourceは、Thinking Parser通過後のOriginal canonical final answerだけである。

- 渡さない: 通常生成のThinking、会話履歴、元System Prompt、User Prompt、Path、Credential、Runtime内部状態
- Server System Message: Sourceを命令ではなくuntrusted dataとして扱い、事実・結論・制約・警告・否定・Code・数値を保持し、追加主張を禁止
- User Message: `{"source_answer": ...}`のJSON data value
- `ja`: 日本語要約
- `en`: 英語要約
- `auto`: Sourceの主言語を維持
- Summary raw outputにもThinking Parserを適用し、Reasoningは表示・履歴へ出さない

Prompt injection境界、JSON escape、3種類のResponse LanguageはUnit Testで固定した。

## 6. Model Call／Sequential性

### OFF

- Main Model call: 1回
- 既存Generation Parameter、Thinking Visibility、表示／canonical分離を維持

### ON

- Main Model call: 2回
- 1回目: User指定の`max_new_tokens`（上限2048）で通常回答
- 2回目: `max_new_tokens=1024`、`thinking_mode=disabled`でSummary
- 同一`model_key`を使用
- 通常StreamをContext Managerでcloseした後にSummary Streamを生成
- 2 Stream同時Openなし
- 親Sessionが通常生成開始からSummary／fallback／cancel terminalまでGeneration Gateを保持
- Stream生成、Iteration、native cancel／closeはproducer thread側

Unit／Web Integration Testでcall count、request order、Parameter、message boundary、両Stream closeを確認した。Mac Metal実Model TestでもSummary ONが`presented_source=summary`で完了した。

## 7. Fallback Matrix

次は`summary_fallback_original` warning後、Original canonical answerを`assistant_message`として完了する。

| 条件 | 動作 |
|---|---|
| Summary Inference Error／Context Limit | Originalへfallback |
| Summary empty／whitespace final | Originalへfallback |
| Summary Thinking Parser failure／unclosed protocol | Originalへfallback |
| Summary `finish_reason=length` | 不完全Summaryを表示せずOriginalへfallback |
| Summary terminal chunk欠落／不整合 | 不完全Summaryを表示せずOriginalへfallback |
| Original canonical finalがempty／whitespace | Summary callせずOriginalへfallback |

- Original／Summary／PresentedはONのcompleted payloadで別Fieldとして保持する。
- Browser履歴へ入るのは`assistant_message`、つまりPresentedだけ。
- 不完全Summary deltaはbufferし、validity確定前には送らない。
- Summary failureの内部例外詳細はBrowserへ出さない。
- Original側warningはSummary成功／fallbackのどちらでもterminal前に維持する。

Cancelはfallbackではない。通常生成中、段間、Summary中のcancelはいずれも`cancelled` terminalとなり、assistant historyを作らない。

## 8. SSE Order

### Summary OFF

```text
start(state=generating)
delta*
warning*
completed
```

### Summary ON成功

```text
start(state=generating_answer)
[normal generation: hidden]
status(state=summarizing_answer)
[summary generation: buffered]
delta(valid summary)
warning*
completed
```

### Summary ON fallback

```text
start(state=generating_answer)
[normal generation: hidden]
status(state=summarizing_answer)
delta(original canonical answer, if non-empty)
original warning*
warning(code=summary_fallback_original)
completed(presented_source=original)
```

各経路のterminal eventは1回だけである。

## 9. Cancel／Shutdown Boundary

- Phase 1-Gのcooperative cancelを維持した。
- HTTP disconnect／Stop／Shutdown workerはcancel flagだけを設定する。
- producer threadが次のchunk boundaryで同じthread上からnative `cancel()`／`close()`を行う。
- Summary中cancelのThread-affine Integration Testを追加し、fallback／completedを出さないことを確認した。
- Summary段間cancelでは2回目のModel callを開始しない。
- Session終了時にGateを解放し、後続Generationが可能。
- `WebRuntime.close()`のidempotent closeとtimeout boundaryを既存Testで回帰確認した。
- `force_cancel`の呼出しはRuntime source内0件のまま。

## 10. UI Language／Storage

- Header右上に`日本語 | English`を追加した。
- defaultは日本語。
- Browser-only translation dictionaryを使用し、外部CDN／i18n Dependencyは追加していない。
- 翻訳対象: `document.title`、`html lang`、Button、Label、Placeholder、Status、既知Warning／Error、ARIA、Empty／New Chat、Settings、Response Language option label。
- Response Language value `ja | en | auto`は不変で、UI Languageから独立。
- Model output／Thinkingは翻訳しない。
- 既知Warning／Errorはcodeで翻訳し、未知codeはserver safe textまたはgeneric safe textを使用。
- DOM更新は`textContent`のみで、`innerHTML`は使用しない。
- localStorage keyは`margpa.ui_language.v1`のみ。
- 保存値は`ja | en`のみ。invalid／storage unavailableは`ja`へfallback。
- Chat、Prompt、Credential、Model output、Response Languageは保存しない。
- New ChatはUI Languageを維持し、Reloadで復元する。

Browser手動確認:

- 日本語→英語: title、`html lang`、Button、Label、Placeholder、ARIA、option labelが英語化
- UI English＋Response Language `en`＋Summary ONを独立設定可能
- New Chat後もEnglish維持
- Reload後もEnglish復元
- 390×844 viewportでLanguage SwitcherとNew Chatの重なりなし
- 横overflowなし

## 11. Verification Result

### Static／Unit／Integration

```text
./.venv/bin/ruff format --check src scripts tests
  PASS: 93 files already formatted

./.venv/bin/ruff check src scripts tests
  PASS: All checks passed

./.venv/bin/mypy .
  PASS: 93 source files, no issues

./.venv/bin/python -m compileall -q src scripts tests
  PASS

./.venv/bin/pytest -q
  PASS: 242 passed, 3 deselected

./.venv/bin/pytest -q tests/unit/conversation tests/unit/summarization tests/integration/web
  PASS: 47 passed

node --check src/margpa_runtime_llm/web/static/app.js
  PASS

uv lock --check --offline
  PASS: Resolved 122 packages

bash -n scripts/setup/setup_macos_arm64_metal.sh \
  scripts/setup/setup_lightning_linux_x86_64_cuda.sh \
  scripts/setup/preflight_lightning_ai_studio.sh
  PASS
```

### Mac Metal／実Model

```text
./.venv/bin/pytest -q -m model_smoke
  PASS (Mac Metal直接実行): 2 passed, 1 skipped, 241 deselected
```

補足:

- Sandbox内の初回実行はMetal `llama_context`を作成できず、Model Load前に既存2 Smokeが失敗した。
- 同一CommandをMac Metal直接Accessで再実行し、既存SmokeとPhase 1-H実Model Summary ONがともに通過した。
- Skip 1件は`MARGPA_PHASE1F_PROFILE`未設定のPhase 1-F cross-environment smokeであり、Phase 1-H blockerではない。

## 12. 未解決／Review観点

- Phase 1-H実装上の既知blockerなし。
- UI manualはlocal fake Runtime metadataで表示・操作を確認し、Generation pipelineはASGI IntegrationとMac Metal実Model Testで別途確認した。
- Lightning native executionはPhase 1-Fの扱いどおりdeferred。Upload／Model転送は実施していない。
- 設計者には、ON completed payloadのOriginal／Summary／Presented分離、fallback event order、Application schema 3、Browser-only i18n境界を重点Reviewしてほしい。

## 13. 非実施

- Phase 1完了宣言
- Phase 1-Ex／後続Phase着手
- Backup／Release作業
- Git初期化、Commit、Push、PR
- Lightning upload、Model transfer、Cloud実行
- Public Docs更新
