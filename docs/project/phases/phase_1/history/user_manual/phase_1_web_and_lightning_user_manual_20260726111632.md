# Phase 1 Web／Lightning ユーザーマニュアル

- 文書ID: `phase_1_web_and_lightning_user_manual`
- 状態: `current_verified_phase_1`
- 作成日時: `2026-07-26 11:16:32 JST`
- 更新日時: `2026-07-26 11:16:32 JST`
- Snapshot: `20260726111632`
- 作成担当: 設計者役担当Task
- 対象: MARGPA Runtime LLM Phase 1-A～Phase 1-I
- 対象環境: Mac Local Web／Lightning Linux x86_64 Pure CPU Web
- 詳細なLightning再構築手順: [lightning_pure_cpu_actual_environment_reconstruction_manual_20260726092413.md](lightning_pure_cpu_actual_environment_reconstruction_manual_20260726092413.md)
- Acceptance Review: [designer_review_top_level_phase_1_completion_and_lightning_web_acceptance_20260726111632.md](../handoffs/designer_review_top_level_phase_1_completion_and_lightning_web_acceptance_20260726111632.md)
- 正本言語: 日本語
- supersedes: `phase_1_web_and_lightning_user_manual_20260721185031.md`

## 1. このManualの目的

Phase 1で実際に検証済みのWeb Preview機能、Mac起動、Lightning Pure CPU起動、外部公開、停止および現在の制約を整理する。

環境をゼロから再構築する場合は、詳細なLightning再構築手順を先に参照する。

## 2. Phase 1で利用できる機能

- 一時的な複数Turn Chat
- Streaming
- Send／Stop
- `Cmd+Enter`／`Ctrl+Enter`送信
- New Chat
- UI日本語／English
- 回答言語`ja／en／auto`
- 最大生成Token数`1～2048`
- Thinking Generation
- Thinking Visibility
- Summary Mode
- User／Assistant Message Copy
- 完了後の安全なMarkdown Rendering
- Basic認証
- Model Busyの安全な拒否
- Mac Metal
- Lightning Linux x86_64 Pure CPU

Phase 1の会話はBrowser Tab内の一時Memoryであり、永続保存されない。

## 3. Current Defaults

```text
Response Language       : ja
Max New Tokens          : 2048
Thinking Generation     : off
Thinking Visibility     : hidden
Summary Mode            : off
UI Language             : ja
Mac Host                : 127.0.0.1
Lightning Host          : 0.0.0.0
Port                    : 8000
Lightning Profile       : config/profiles/lightning_linux_x86_64_cpu_native.toml
```

## 4. Macで起動する

Project Root：

```bash
cd /path/to/margpa-runtime-llm
```

起動：

```bash
./.venv/bin/margpa-web
```

Browser：

```text
http://127.0.0.1:8000/
```

停止：

```text
Ctrl+C
```

Macで外部公開することを本Manualは想定しない。

## 5. Lightningの確認済み配置

```text
/teamspace/studios/this_studio/
├─ margpa-runtime-llm/
│  ├─ .python-version
│  ├─ .venv/
│  ├─ config/
│  ├─ models -> ../models
│  ├─ pyproject.toml
│  ├─ scripts/
│  ├─ src/
│  ├─ tests/
│  └─ uv.lock
├─ models/
│  └─ main/qwen3-4b/gguf/Qwen3-4B-Q4_K_M.gguf
└─ .runtime-tools/uv/0.11.29/bin/
```

## 6. Lightning Webを手動起動する

### 6.1 Environment

```bash
export MARGPA_WORKSPACE_ROOT=/teamspace/studios/this_studio
export MARGPA_PROJECT_ROOT="$MARGPA_WORKSPACE_ROOT/margpa-runtime-llm"
export MARGPA_MODEL_ROOT="$MARGPA_WORKSPACE_ROOT/models"
export MARGPA_UV_BIN="$MARGPA_WORKSPACE_ROOT/.runtime-tools/uv/0.11.29/bin"
export MARGPA_ENV_PREFIX="$MARGPA_PROJECT_ROOT/.venv"
export PATH="$MARGPA_UV_BIN:$PATH"

cd "$MARGPA_PROJECT_ROOT"
```

確認：

```bash
test -x "$MARGPA_ENV_PREFIX/bin/margpa-web"
test -f "$MARGPA_MODEL_ROOT/main/qwen3-4b/gguf/Qwen3-4B-Q4_K_M.gguf"

printf 'WEB_PREREQUISITES_EXIT=%s\n' "$?"
```

期待値：

```text
WEB_PREREQUISITES_EXIT=0
```

### 6.2 Basic認証

```bash
export MARGPA_WEB_AUTH_MODE=basic
export MARGPA_WEB_AUTH_USERNAME='preview'
export MARGPA_WEB_AUTH_PASSWORD="$(
  "$MARGPA_ENV_PREFIX/bin/python" -c \
  'import secrets; print(secrets.token_urlsafe(32))'
)"
```

現在の手動Previewでは、一度だけ表示して安全な経路で控える。

```bash
printf 'Preview Username: %s\n' "$MARGPA_WEB_AUTH_USERNAME"
printf 'Preview Password: %s\n' "$MARGPA_WEB_AUTH_PASSWORD"
```

CredentialをDocs、Config、Screenshot、Git、公開Logへ保存しない。

Phase 1-exでAuto-startを導入する場合は、毎回Random Passwordを作らず、Lightning Managed Secretsに保存した安定Credentialを使用して明示Rotateする。

### 6.3 Pure CPU Profile

```bash
"$MARGPA_ENV_PREFIX/bin/margpa-web" \
  --host 0.0.0.0 \
  --port 8000 \
  --profile config/profiles/lightning_linux_x86_64_cpu_native.toml \
  --model-root "$MARGPA_MODEL_ROOT"
```

このTerminalは起動中のままにする。

Model Load、GGUF MetadataおよびSHA-512検証に時間がかかる場合がある。Pure CPU生成、ThinkingおよびSummary ModeはMac Metalより大幅に遅い。

## 7. Health Check

別Terminal：

```bash
curl -i http://127.0.0.1:8000/healthz
```

期待値：

```text
HTTP/1.1 200 OK
{"status":"ok"}
```

CredentialなしRoot：

```bash
curl -i http://127.0.0.1:8000/
```

期待値：

```text
401 Unauthorized
```

`/healthz`は認証対象外だが、最小Statusだけを返す。

## 8. Lightning Port公開

Lightning StudioのPort ViewerでPort `8000`を追加し、外部共有時はPublic Linkを有効化する。

LightningへLoginしていないPrivate／Incognito Windowから次を確認する。

- Basic認証が表示される。
- 誤Credentialでは開けない。
- 正しいCredentialでMARGPA画面が開く。
- Studio TerminalまたはFile Editorは外部から見えない。

確認済みPublic Link：

```text
https://lightning-preview-url-redacted.invalid/not-published
```

Lightning側の再構成によりURLが変わる可能性がある。

## 9. Web操作

### 9.1 送信

- Send Button
- `Cmd+Enter`
- `Ctrl+Enter`

Enterだけでは送信しない。

### 9.2 Stop

生成中またはSummary処理中にStop Buttonを押す。停止後に再送信できる。

### 9.3 New Chat

Current Conversation Contextを消去する。ModelはReloadしない。

生成中にNew Chatを押した場合、Current Generationを停止し、Contextを初期化する。

### 9.4 Language

```text
UI Language       : 日本語／English
Response Language : ja／en／auto
```

両者は独立している。

### 9.5 Thinking

Thinking GenerationをONにした場合だけThinking VisibilityをONにできる。

表示内容はModel生成の推論過程であり、真の内部思考、正解または完全な説明責任を保証しない。保存およびFinal Copyの対象外である。

### 9.6 Summary

Summary Modeは通常回答後に同じMain Modelをもう一度呼ぶ。Pure CPUではLatencyが大きく増える。

## 10. Model Busy

同時Generation数は1である。別Tabで同時に生成した場合、後続Requestは安全に拒否される。

英語：

```text
The model is processing another request.
The request failed.
```

日本語：

```text
Modelは別のRequestを処理中です。
Requestに失敗しました。
```

先行Request完了後に再実行する。

## 11. Browser Reload

Reloadすると次が消える。

- Conversation
- Response Languageの一時変更
- Max New Tokensの一時変更
- Thinking設定
- Summary Mode

UI LanguageだけはBrowserへ保持される。

## 12. 終了

起動Terminal：

```text
Ctrl+C
```

CredentialをShellから除去する。

```bash
unset MARGPA_WEB_AUTH_PASSWORD
unset MARGPA_WEB_AUTH_USERNAME
unset MARGPA_WEB_AUTH_MODE
```

別TerminalのHealth Checkが接続失敗になれば、Process停止を確認できる。

Lightningを使用しない場合はMachineをManual Sleepにする。Browserを閉じただけでCost停止したと仮定せず、Lightning DashboardでMachine Stateを確認する。

## 13. Auto-start

Current Phase 1はManual Startである。Sleep／Wake後に上記Commandを再入力しないAuto-startは未実装である。

Phase 1-exで次を検討する。

- `~/.lightning_studio/on_start.sh`
- Project-owned Launcher
- Lightning Managed Secrets
- Traffic-aware Auto-start
- Cold Start表示
- CPU固定
- Idle Sleep
- Duplicate Process防止

Auto-start完了までは、使用時に手動起動し、終了時にManual Sleepする。

## 14. iPhone／Mobile

iPhone／iOSは「不可能」ではなく、Current Phase 1でResponsive Acceptanceを行っていない。

Phase 4または後続UI Phaseで、iOS Safari、Touch、Virtual Keyboard、Safe Area、Narrow ViewportおよびCode Block横Overflowを検証する。

## 15. Current Limitations

- Pure CPU生成は遅い。
- Persistent Conversationはない。
- Multi-user Accountはない。
- Rate Limitはない。
- Basic認証は本番認証ではない。
- Streaming中はRaw Markdownが見える場合がある。
- Markdown Tableは未対応である。
- Code Block個別Copyは未対応である。
- Busy表示は具体Messageと汎用Messageが重複する。
- Mobile Responsive Acceptanceは未実施である。
- Auto-startは未実装である。

## 16. Acceptance State

MacおよびLightning Pure CPUについて、本Manual記載のPhase 1 Web機能はUser Acceptance済みである。

```text
Mac Web                  : PASS
Lightning External Web  : PASS
Phase 1                 : COMPLETE／ACCEPTED
```
