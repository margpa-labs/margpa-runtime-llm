# Phase 1 Web／Lightning ユーザーマニュアル

- 文書ID: `phase_1_web_and_lightning_user_manual`
- 状態: `current_user_acceptance_candidate`
- 作成日時: `2026-07-21 18:50:31 JST`
- 更新日時: `2026-07-21 18:50:31 JST`
- Snapshot: `20260721185031`
- 作成担当: 設計者役担当Task
- 対象: MARGPA Runtime LLM Phase 1-A～Phase 1-H
- 対象ユーザー: Local MacまたはLightning AI StudioでPhase 1 Web Previewを起動・利用するユーザー
- 正本言語: 日本語
- Documentation Index: [documentation_index_20260721185031.md](../documentation_index_20260721185031.md)
- Phase 1-H Accepted Review: [designer_review_phase_1h_review_follow_up_20260721184140.md](../handoffs/designer_review_phase_1h_review_follow_up_20260721184140.md)
- Lightning Setup Script: `scripts/setup/setup_lightning_linux_x86_64_cuda.sh`
- supersedes: `phase_1_macos_user_manual_20260719171836.md`

## 1. このManualの目的

このManualは、MARGPA Runtime LLM Phase 1のWeb Previewについて、次を一つの手順として整理する。

- Local MacでWeb画面を起動する。
- Lightning AI StudioでCUDAまたはCPU Profileを選択して起動する。
- Lightningの外部公開URLを使用し、Lightning Accountを持たない利用者からWeb画面を開く。
- Web画面の設定と現在の制約を理解する。
- 起動失敗時に、Profile、Model Root、認証、Port公開を切り分ける。

Project一式のLightningへのUpload方法とModel Artifactの配置方法は、本Manualの対象外とする。これらが完了していることを前提とする。

## 2. 現在利用できる範囲

Phase 1 Web Previewで利用できる主な機能は次のとおりである。

- 一時的な複数Turn Chat
- Streaming表示
- 生成停止
- 新規Chat
- 回答言語 `ja／en／auto`
- 最大生成Token数 `1～2048`
- 推論過程表示 `OFF／ON`
- 要約モード `OFF／ON`
- 画面表示言語 `日本語／English`
- Model／Profile／Device情報の表示
- Preview用Basic認証
- Lightning向けCUDA／CPU Profile

現在の主な既定値：

```text
回答言語           : ja
最大生成Token数   : 2048
推論実行           : disabled
推論過程表示       : hidden
要約モード         : off
要約最大Token数    : 1024
画面表示言語       : ja
Web Host            : 127.0.0.1
Web Port            : 8000
```

## 3. 重要な制約

このWeb画面は少人数検証用Previewであり、本番Serviceではない。

- Basic認証は、本番用Account、権限管理、User管理を代替しない。
- 同時に実行できるModel Generationは1件である。
- 別Requestが生成中の場合、後続Requestは`model_busy`になることがある。
- Chat履歴はBrowser TabのMemoryだけに存在し、ReloadまたはTab終了で失われる。
- 新規ChatはBrowser内の一時履歴を消すが、ModelをReloadしない。
- Audit Log、永続Conversation、User Account、Rate Limitは未実装である。
- LightningのStudio、GPU、Processが停止またはSleepした場合、公開URLは一時的に利用不能またはCold Start待ちになる。
- Lightning実Reverse Proxy、CUDA、CPUでの最終受入は、Batch Lightning Gateで確認する。

## 4. 共通の前提

次が準備済みであることを前提とする。

- Project RootへProject一式が配置済みである。
- 実行環境ごとに`.venv/`が再構築済みである。
- `pyproject.toml`と`uv.lock`がProject内に存在する。
- Main Modelが次の論理構造で参照可能である。

```text
MODEL_ROOT/
└─ main/
   └─ qwen3-4b/
      └─ gguf/
         └─ Qwen3-4B-Q4_K_M.gguf
```

- Macの`.venv/`をLightningへUploadしていない。
- Model RootがProject外にある場合、`MARGPA_MODEL_ROOT`または`--model-root`で明示する。
- SecretをTracked Config、Docs、Command履歴、Screenshot、公開Logへ保存しない。

`requirements.txt`はCurrent Projectの依存関係正本ではない。依存関係の正本は`pyproject.toml`と`uv.lock`であり、`uv sync --frozen`をSetup Script経由で使用する。

## 5. Local Macで起動する

### 5.1 Project Rootへ移動する

```bash
cd /path/to/margpa-runtime-llm
```

### 5.2 Helpを確認する

```bash
./.venv/bin/margpa-web --help
```

Helpに表示される`HOST`、`PORT`、`PROFILE_PATH`等の大文字は、実際の値へ置き換える仮引数名である。文字列`HOST`や`PROFILE_PATH`をそのまま入力しない。

### 5.3 Local専用で起動する

```bash
./.venv/bin/margpa-web
```

明示する場合：

```bash
./.venv/bin/margpa-web \
  --host 127.0.0.1 \
  --port 8000
```

Browserで次を開く。

```text
http://127.0.0.1:8000/
```

`127.0.0.1`は同じMacだけから接続できるLoopback Addressである。この場合に限り、認証無効の既定値で起動できる。

### 5.4 起動を停止する

起動したTerminalで`Ctrl+C`を押す。

Model Generation中に停止した場合も、Current RuntimeはCooperative CancelとShutdown Cleanupを行う。ただしTerminalを強制終了するより、まず`Ctrl+C`を使用する。

## 6. Lightning AI Studioの実行設定

### 6.1 確認済みの対象環境

Current Lightning Profileは次のObserved Environmentを対象とする。

```text
OS                  : Ubuntu 24.04 LTS
Architecture        : x86_64
Execution Environment: container
Python              : 3.12.11
uv                  : 0.11.29（Project用に隔離したBinary）
GPU Candidate       : NVIDIA Tesla T4／CUDA
CPU Candidate       : Intel Xeon／4 CPU
Backend             : llama-cpp-python 0.3.34／GGML_CUDA=on
```

Lightning既設の`uv 0.11.18`を置換しない。Project用`uv 0.11.29`をPATHの先頭へ一時的に追加する。

```bash
export MARGPA_UV_BIN=/teamspace/studios/this_studio/.runtime-tools/uv/0.11.29/bin
export PATH="$MARGPA_UV_BIN:$PATH"
uv --version
```

期待値：

```text
uv 0.11.29 (x86_64-unknown-linux-gnu)
```

### 6.2 Project Rootへ移動する

```bash
cd /teamspace/studios/this_studio/margpa-runtime-llm
```

Projectを別の場所へ配置した場合は、その実際のProject Rootへ移動する。

### 6.3 Model Rootを明示する

Project Root内の`models/`を使用する場合：

```bash
export MARGPA_MODEL_ROOT="$PWD/models"
```

Project外へModelを配置した場合：

```bash
export MARGPA_MODEL_ROOT=/absolute/path/to/models
```

確認：

```bash
test -f "$MARGPA_MODEL_ROOT/main/qwen3-4b/gguf/Qwen3-4B-Q4_K_M.gguf"
printf 'MODEL_CHECK_EXIT=%s\n' "$?"
```

`MODEL_CHECK_EXIT=0`なら、期待するPathにModelが存在する。

### 6.4 Preview用Basic認証を設定する

Lightningの外部公開では`0.0.0.0`へBindするため、Basic認証が必須である。

```bash
export MARGPA_WEB_AUTH_MODE=basic
export MARGPA_WEB_AUTH_USERNAME='<preview-user>'
export MARGPA_WEB_AUTH_PASSWORD='<long-random-preview-password>'
```

`<...>`全体を実際の値へ置き換える。Credentialを上記の例のまま使わない。

運用上の注意：

- UsernameとPasswordは空にしない。
- Usernameには`:`を使用しない。
- Passwordは十分に長いRandom値を使用する。
- CredentialをGit、Docs、`.toml`、Screenshot、共有Chatへ残さない。
- Credentialは公開URLと別経路で検証利用者へ伝える。
- 検証終了後または漏えい疑いがある場合は、新しいCredentialへ変更してProcessを再起動する。

### 6.5 GPU Profileで起動する

LightningへNVIDIA GPUが割り当てられている場合：

```bash
./.venv/bin/margpa-web \
  --host 0.0.0.0 \
  --port 8000 \
  --profile config/profiles/lightning_linux_x86_64_cuda.toml \
  --model-root "$MARGPA_MODEL_ROOT"
```

GPU Profileの主要設定：

```text
Profile Key     : external.lightning-linux-x86_64.cuda
Device Kind     : gpu
Acceleration    : cuda
GPU Layers      : -1
Fallback Policy : deny
```

CUDAが必要なProfileでCUDAを利用できない場合、CPUへ黙ってFallbackしない。CPUで動かす場合はCPU Profileを明示する。

### 6.6 CPU Profileで起動する

GPU割当上限、GPU未割当、CPU比較検証等の場合：

```bash
./.venv/bin/margpa-web \
  --host 0.0.0.0 \
  --port 8000 \
  --profile config/profiles/lightning_linux_x86_64_cpu.toml \
  --model-root "$MARGPA_MODEL_ROOT"
```

CPU Profileの主要設定：

```text
Profile Key     : external.lightning-linux-x86_64.cpu
Device Kind     : cpu
Acceleration    : cpu_native
GPU Layers      : 0
Fallback Policy : deny
```

Current CPU Profileも、同じ`GGML_CUDA=on`でBuildした`llama-cpp-python`を`gpu_layers=0`で使用する。CPU実行はGPU実行より大幅に遅くなる可能性がある。

### 6.7 起動成功の確認

起動Processを実行したTerminalは、そのまま起動状態にしておく。別Terminalで次を確認する。

```bash
curl -i http://127.0.0.1:8000/healthz
```

期待値：

```text
HTTP/1.1 200 OK
{"status":"ok"}
```

`/healthz`は認証対象外だが、最小のStatusだけを返す。Model情報、Path、Credential、Prompt、回答は返さない。

Web RootはBasic認証対象である。

```bash
curl -i http://127.0.0.1:8000/
```

Credentialなしで`401 Unauthorized`になれば、認証境界が有効である。

## 7. Lightning Account外から開く

### 7.1 Studio編集画面ではなくWeb AppのPortを公開する

Lightning Account外の利用者へ見せる対象は、Studio編集画面やTerminalではなく、Port `8000`のWeb App公開URLである。

Lightning公式のCurrent案内では、独自Web AppはStudioのMenuから`Port viewer`／Ports Pluginを導入し、対象Portを開いて公開URLを取得する。UI名称はLightning側の更新で変わる可能性がある。

参考：

- [Lightning公式: Expose web apps](https://lightning.ai/docs/overview/host-web-apps/expose-web-apps)
- [Lightning公式: Host web apps](https://lightning.ai/docs/overview/host-web-apps)
- [Lightning公式: Studio SDK／Exposing ports](https://lightning.ai/docs/overview/sdk/studio)

### 7.2 Port公開の操作

1. Lightning Studioを起動する。
2. Section 6のCommandで`margpa-web`を`0.0.0.0:8000`へ起動する。
3. StudioのMenuまたはPlugin画面を開く。
4. `Port viewer`、`Ports`または同等のPort公開Pluginを追加・開く。
5. Port番号`8000`を指定する。
6. Private／Account限定URLではなく、外部共有用の`Public link`を有効にする。
7. Lightningが生成したHTTPSの公開URLを取得する。
8. AccountへLoginしていないIncognito／Private Windowで公開URLを開く。
9. MARGPA PreviewのBasic認証Promptが表示されることを確認する。
10. Section 6.4で設定したPreview Credentialを入力する。

Lightningの`Publish Studio`は、Studio環境を複製・共有する別機能である。今回の「他者がChat画面を試す」という目的では、Web AppのPort公開URLを使用し、Studio全体を公開する必要はない。

### 7.3 Account外Accessの合格条件

次をすべて満たせば、Account外のPreview Accessは成立したと判断する。

- LightningへLoginしていないBrowserでHTTPS公開URLを開ける。
- Preview CredentialなしではWeb Rootを表示できない。
- 正しいPreview CredentialでChat画面を表示できる。
- Runtime情報が画面下部等へ表示される。
- 短い日本語Promptで回答が生成される。
- `停止`が動作する。
- `新規Chat`でBrowser内履歴を初期化できる。
- Page Reload後に一時Chat履歴が失われる。
- 外部利用者からStudio Terminal、File、Editorへ到達できない。

### 7.4 公開時の安全境界

- Public Portを有効にする前に、必ずBasic認証を設定する。
- Raw `http://IP:8000`をInternetへ直接公開せず、LightningのHTTPS公開URLを使用する。
- Studio編集用共有LinkをPreview利用者へ渡さない。
- `healthz`が公開される点を認識する。ただし返すのは`status=ok`だけである。
- URLを知る人が増えた場合、Credentialを更新する。
- 少人数Previewの範囲を超える場合、本格Authentication、Rate Limit、Audit、User管理を実装するまで公開範囲を拡大しない。

## 8. Web画面の使い方

### 8.1 画面表示言語

画面右上の`日本語／English`でUI文字だけを変更する。

- UI LanguageはBrowserのLocal Storageへ保存される。
- Modelへ送る回答言語は変更しない。
- 回答言語と独立しているため、「画面はEnglish、回答は日本語」等の組み合わせが可能である。

### 8.2 回答言語

設定の`回答言語`で次を選ぶ。

```text
ja   : 日本語を要求する
en   : 英語を要求する
auto : Promptに応じてModelへ判断させる
```

小型Modelであるため、指定言語を常に完全保証するものではない。

### 8.3 最大生成Token数

`1～2048`の整数を指定する。既定値は`2048`である。

小さい値では、推論過程の生成中に上限へ到達し、最終回答が生成されないことがある。その場合、画面にToken上限到達Warningが表示される。

### 8.4 推論過程を表示

このSwitchは、Modelが生成した推論過程の表示／非表示を切り替える。

- 推論実行自体のON／OFFではない。
- 表示内容の正しさや、真の内部思考との一致を保証しない。
- Raw Thinkingは永続保存しない。
- 通常利用ではOFFを推奨する。

### 8.5 要約モード

`ON`では、通常回答の完了後に同じMain Modelで回答を要約し、要約だけを画面へ表示する。

```text
OFF : Main Model Call 1回
ON  : 通常回答＋要約のSequential Call
```

注意：

- 処理時間とToken使用量が増える。
- 要約最大Token数は`1024`である。
- 詳細、前提、注意事項が省略または変形される可能性がある。
- 要約を安全に完了できない場合、元の回答をFallback表示する。
- Cancel時はFallback表示せず、取消状態にする。

### 8.6 新規Chat

`新規Chat`は現在のBrowser Tab内のMessage列を初期化する。

- ModelはUnload／Reloadしない。
- Server側に履歴を保存しない。
- 複数Chatの一覧、Chat削除、履歴再開は未実装である。

## 9. Troubleshooting

### 9.1 Non-loopback Bindを拒否される

症状：

```text
error [invalid_configuration]: A non-loopback web bind requires preview authentication.
```

原因：`0.0.0.0`で起動したがBasic認証が設定されていない。

対処：Section 6.4の3 Environment Variableを設定し、Processを再起動する。

### 9.2 Basic認証設定を拒否される

症状：

```text
Basic preview authentication requires both credentials.
```

原因：UsernameまたはPasswordが未設定、空文字、空白だけである。

対処：両方を設定してProcessを再起動する。

### 9.3 Public URLでLightning Loginを要求される

原因候補：

- PortがPrivate／Teamspace限定になっている。
- Web App公開URLではなく、Studio編集画面のURLを共有している。

対処：Ports／Port ViewerでPort `8000`の`Public link`を有効にし、生成されたWeb App URLをIncognito Windowで再確認する。

### 9.4 Public URLへ接続できない

確認順：

1. Studioが起動中か。
2. `margpa-web` Processが終了していないか。
3. `--host 0.0.0.0 --port 8000`で起動したか。
4. `/healthz`がStudio内部から200を返すか。
5. Port Viewerの対象Portが8000か。
6. Lightning側のSleep／Cold Start待ちではないか。

### 9.5 ModelがLoadできない

確認：

```bash
printf '%s\n' "$MARGPA_MODEL_ROOT"
ls -lh "$MARGPA_MODEL_ROOT/main/qwen3-4b/gguf/Qwen3-4B-Q4_K_M.gguf"
```

Model Rootは、`main/`の一つ上を指す。

### 9.6 GPU Profileで起動できない

確認：

```bash
nvidia-smi
./.venv/bin/python scripts/setup/verify_phase1_environment.py --target lightning-cuda
```

GPUが割り当てられていない場合はCPU Profileを使用する。CUDA ProfileからCPUへ暗黙Fallbackさせない。

### 9.7 CPUで遅い

Qwen3-4B Q4_K_Mを4 CPUで実行するため、GPUより遅いことはExpected Behaviorである。短いPromptと小さめの最大生成Token数で疎通確認し、品質確認はGPU Profileで行う。

### 9.8 要約ONで長時間表示が変わらない

通常回答の後に同じModelで要約するため、回答が表示されるまでのSilent Intervalが増える。Current Runtimeは15秒ごとにSSE Keepalive Commentを送るが、Lightning実Reverse Proxyでの確認はBatch Gate対象である。

## 10. Lightning公開前の最小Checklist

```text
[ ] Project一式を配置済み
[ ] Modelを配置済み
[ ] Mac由来の.venvを搬入していない
[ ] Lightning上で.venvを再構築済み
[ ] Project用uv 0.11.29を選択済み
[ ] MARGPA_MODEL_ROOTを確認済み
[ ] CUDAまたはCPU Profileを明示済み
[ ] Preview Basic認証を設定済み
[ ] 0.0.0.0:8000で起動済み
[ ] Studio内healthzが200
[ ] Port 8000のPublic linkを有効化
[ ] Incognito WindowでAccount外Access確認
[ ] Credentialなしで401確認
[ ] CredentialありでChat画面確認
[ ] 短い生成／停止／新規Chat確認
[ ] UI LanguageとResponse Languageの独立確認
[ ] Summary OFF／ON確認
```

## 11. 現在の受入状態

```text
Mac Source／Static／Test Review        : Accepted
Mac Metal Model Smoke                  : Accepted
Phase 1-H Summary／UI Language         : Accepted
Lightning Read-only Preflight          : Accepted
Lightning Full Upload                  : User Operation
Lightning CUDA Native Gate             : Waiting
Lightning CPU Native Gate              : Waiting
Lightning Public URL／Reverse Proxy     : Waiting
Account外Browser Acceptance             : Waiting
Phase 1 Overall Completion             : Not Declared
```

本Manualの作成は、Lightning Native Gate、Account外Access、Phase 1全体完了を自動的に合格扱いしない。実際の操作結果をEvidenceとして確認した後に最終判定する。

## 12. Append-Only

既存のMac専用Manualを変更せず、Phase 1-F～1-H、Lightning起動、外部公開、Current Web設定を統合した新TimestampのManualを追加した。新しいTimestampの本Manualを最新とする。
