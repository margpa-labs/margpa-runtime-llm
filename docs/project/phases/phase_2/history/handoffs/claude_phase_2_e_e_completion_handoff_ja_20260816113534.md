# Claude Phase 2-E-E Completion Handoff — React/Vite移行（1:1 Parity）

```yaml
document_id: claude_phase_2_e_e_completion_handoff_20260816113534
status: implementation_complete
phase: phase_2
subphase: phase_2_e_e
from: Claude側設計統括者役
to: ユーザー（最終確認者）／Codexプロジェクト責任者兼設計統括者役
role: design_governor
baseline: e007110ba713b70f3715b991e0713e511ed21184
created_at: 2026-08-16 11:35:34 JST
language: ja
authorization: ユーザーからの明示的な全権委任
  （「2-E-EからGまで、Checkpointなしで一気に(Bypass実験その2として)進める」
  「完全ノンストップでの実験を優先」、2026-08-16朝）
related:
  - claude_phase_2_e_e_to_h_react_migration_design_ja_20260816102654（設計、承認済み）
```

## 1. Mission

承認済み設計（[claude_phase_2_e_e_to_h_react_migration_design_ja_20260816102654.md](../architecture/claude_phase_2_e_e_to_h_react_migration_design_ja_20260816102654.md)）の2-E-E：既存Vanilla JS SPA（`app.js` 1724行、`safe_markdown.js` 311行、`index.html`、`app.css`）を、React 19 + Vite 8 + TypeScript（strict）へ移行する。本段階は**1:1 Parity（新規UIなし）**が唯一の目標であり、2-E-F（Sidebar）・2-E-G（Account/設定Modal）は後続。

本Handoffは**実装完了時点**の報告である。最終的な「2-E-E完了」判定はユーザー自身が画面を見て行う契約は変わらない。

## 2. 実装内容

```text
frontend/                          （新規、Python Packageから完全独立）
  package.json / tsconfig.json / vite.config.ts / eslint.config.js
  index.html                        configuration-bootstrap Tagを一字一句保持
  src/
    main.tsx, App.tsx               全体Orchestration（旧app.jsの状態機械を忠実移植）
    types.ts                        Backend Contract型（手書き、Boundaryで信頼する既存方針を踏襲）
    i18n/translations.ts            ja/en辞書（既存Key・文言は無変更、Sidebar/設定Modal用の新Keyのみ追加）
    hooks/usePreference.ts          Language/Theme共通の localStorage 読み書きHook
    lib/safeMarkdown.tsx            safe_markdown.js の忠実移植（dangerouslySetInnerHTML不使用を維持）
    lib/eventStream.ts              SSE Framing（parseEventBlock/readEventStream）の移植
    lib/configurationBootstrap.ts   configuration-bootstrap Tag読み取り
    api/client.ts                   既存API Endpoint群への型付きFetch Wrapper
    components/*.tsx                TopBar, PersistentPanel, ConfigurationControlPanel,
                                     MessageList, MessageBubble, CitationsSection,
                                     CopyButton, Composer, SettingsPanel

src/margpa_runtime_llm/web/static/  Vite Build出力先（既存FastAPI StaticFiles Mountは無改変）
  index.html / app.js / app.css     決定的（非Hash）Filenameで出力するようVite設定
                                     （FastAPIの"/"経路によるconfiguration-bootstrap文字列置換、
                                     および既存Testの/assets/app.js Path参照を維持するため）
  safe_markdown.js                  廃止（Bundleへ吸収、単独Fileとしては存在しなくなる）
```

## 3. 設計判断・実装中に発見した実装Detail

### 3.1 忠実移植で発見・修正した実装Bug（3件、いずれもReact化に伴う新規混入であり元のapp.jsには存在しない）

- `chatHistoryRef`（Model送信用の会話履歴）と`messages`（表示用のDisplay List）の混同：初期実装ではDisplay Listから直接履歴を組み立てており、失敗・中断・空応答のTurnまでModelへ再送信されうる状態だった。元のapp.jsの`state.messages.push/pop`意味論に厳密に合わせ、両者を分離した。
- Stop（中断）時のAssistant Bubble処理：初期実装ではAbortError時にBubbleを消去していたが、元の挙動は「部分的に届いたContentをそのまま残す」。修正済み。
- `safeLinkTarget`の制御文字判定Regexで、Write Tool側の`\uXXXX`Escape解釈により制御Byteが生Fileへ混入した事故を検出・修正（Python Scriptでの再書き込み＋全File Byte走査で確認）。

### 3.2 忠実移植の結果、元から存在した実装Bugをそのまま保持した1件（新規混入ではない）

実Browser確認中、`Runtime設定制御`Panelの詳細Field群（`revision`/`digest`/Field一覧/Preview Button）が、`research_developer_mode: off`（詳細非表示のはず）にもかかわらず**視覚的には表示されたまま**になる事象を検出した。`getComputedStyle`で直接確認したところ、`hidden`属性自体はReact側で正しく付与されているが（`hasAttribute("hidden") === true`）、`.configuration-meta`・`.configuration-fields`のCSSが`display: grid`を明示指定しており、`[hidden]`用のOverride Ruleが存在しないため、UA既定の`[hidden]{display:none}`が上書きされてしまっていた。

`git show HEAD:src/margpa_runtime_llm/web/static/app.css`で移行前のOriginal CSSを確認したところ、**同一のGapが移行前から存在していた**（新規混入ではない）。1:1 Parityが本段階の唯一の目標であるため、**今回は意図的に修正せず、Bugごと忠実に移植した**。UX上の実害（研究者向け詳細情報が意図せず見える）はあるため、Findingとして記録する。

- 対象: `frontend/src/styles/app.css`（および現時点でBuild済みの`src/margpa_runtime_llm/web/static/app.css`）の`.configuration-meta`・`.configuration-fields`
- 想定される最小修正: 両Selectorへ`&[hidden]{display:none}`相当のOverrideを追加
- 判断: 2-E-F／2-E-G、あるいは別途のUX Finding整理Timingでの対応候補とする（今回はScope外として見送り）

### 3.3 決定的（非Hash）Build出力Filename

Vite既定はHash付きFilename（例: `index-Bxxxxxx.js`）を生成する。FastAPIの`/`経路は`index.html`を実行時に読み直して文字列置換するためHashでも実害はないが、既存Backend Testが`/assets/app.js`という固定Pathを直接参照している（`tests/integration/web/test_web_app.py`の認証Test）ため、`vite.config.ts`の`build.rollupOptions.output`で`entryFileNames`/`assetFileNames`を固定し、`app.js`/`app.css`という既存名を維持した。

### 3.4 Vitest + jsdom + Node 25 の既知でない相性問題（新規発見、対処済み）

Node 25では`--webstorage`（Web Storage API）が既定で有効化されており、`globalThis.localStorage`がNode自身の実装で埋まる。jsdom Environment下のVitestでも`window.localStorage === globalThis.localStorage`となり、jsdomの完全なStorage実装ではなく機能不全のObjectが返る（`setItem`等が`undefined`）事象を検出した。`frontend/package.json`の`test`Scriptへ`NODE_OPTIONS=--no-webstorage`を追加することで、jsdom本来のStorage実装が使われるよう解消した。

## 4. Test移行（Python source-grep Test の退役 → Vitest Contract Testへの置換）

既存の一部Python Testは、旧`app.js`/`app.css`/`safe_markdown.js`の**Source文字列を直接grep**する形でContractを固定していた（変数名・関数名の存在確認等）。React化によりSourceがCompile・Bundle・Minifyされるため、これらのTestは意味を失う。以下を実施した。

```text
削除（廃止、Source文字列参照のため）:
  tests/unit/web/test_configuration_control_static_contract.py
  tests/unit/web/test_persistent_static_contract.py
  tests/unit/web/test_theme_static_contract.py
  tests/unit/web/test_safe_markdown.py
  tests/unit/web/safe_markdown.test.mjs

縮小（Source Grep部分のみ除去、実HTTP Contract部分は保持）:
  tests/integration/web/test_web_app.py
    - test_static_assets_are_local_thinking_aware_phase_1i_ui
      → test_package_identity_naming_is_current へ縮小
        （Backend __init__.py の製品名Invariantのみ残す。UI文言・Markup Contractは
        frontend側のVitest Suiteへ移動）
    - test_token_limit_warning_precedes_completed_and_ui_preserves_it
      → 末尾のSource Grep部分のみ除去（SSE Response自体のHTTP Contractは無変更で保持）

新規（frontend/src/**/*.test.{ts,tsx}、Vitest + Testing Library、43件）:
  safeMarkdown.test.tsx        旧Node Security Contract（危険URL Scheme拒否、生HTML非実行、
                                外部Link属性）の同等移植＋実DOM Render検証を追加
  usePreference.test.tsx       localStorage読み書き・不正値Fallbackの契約
  translations.test.ts         Key解決・Placeholder展開・ja/en Key集合一致
  eventStream.test.ts          SSE Framing（Chunk境界跨ぎ含む）
  configurationBootstrap.test.ts  Bootstrap Tag読み取りのFail-closed契約
  CopyButton.test.tsx          Clipboard成功/失敗のFeedback表示
  ConfigurationControlPanel.test.tsx  Bootstrap非活性時の非表示、詳細Field群の
                                Privacy Gating（Hidden Attribute経路での検証）
  App.test.tsx（7件）          Persistent Capability Negotiationが無効値で
                                Ephemeral/Persistentへ暗黙Fallbackしないこと、
                                Persistent有効時のList取得・Panel表示、
                                Persistent無効時にList Endpointを一切呼ばないこと、
                                Configuration Bootstrap無効時のPanel非表示・未Fetch、
                                Bootstrap有効時のPanel表示、
                                Browser StorageがUI設定2Keyのみを保持すること、
                                Token上限Warningが完了StatusでOverwriteされないこと
```

## 5. Validation結果

```text
Frontend:
  npm run lint       : Clean（0 errors）
  npm run typecheck   : Clean（0 errors）
  npm test            : 43 passed
  npm run build        : 成功（app.js 240.61kB / gzip 74.37kB、app.css 10.82kB / gzip 2.98kB）

Backend:
  pytest -q           : 664 passed, 3 deselected
                         （669 passed基準から、退役5Fileの分だけ純減。新規失敗なし）
  ruff check .         : All checks passed
  mypy src tests       : Success（170 source files）
```

## 6. 実Browser確認（実LLM、実Backend）

実Model（`main/qwen3-4b/gguf/Qwen3-4B-Q4_K_M.gguf`）を実際に起動し（`--conversation-persistence --configuration-control`他、通常Contract）、Build済みReact Frontendに対して確認した。

```text
初期表示        : Title・Theme切替・Language切替・新規Chat Button・Preview Note・
                  Runtime設定制御Panel、いずれも正しく表示。
Theme切替       : Dark Click → data-theme="dark"、localStorage反映、背景色
                  rgb(11,13,18) 等、2-E-D時点の設計値と一致。
Language切替    : English Click → 全UI文言が英語へ切替、<html lang>／
                  document.titleも連動更新（Tab Title変化で確認）。
Persistent一覧  : 既存9件の保存済みChatが正しく表示・選択可能。
実Chat送信      : 新規Chatを作成し「React移行の動作確認です。短く一言だけ
                  返答してください。」を実送信。実Modelから
                  「React移行の動作確認済み。」を含む応答をStreaming受信、
                  Status「完了 (stop)」、Copy／再生成Buttonが正しく表示。
                  （既存Archived会話への誤送信では、Backendが正しく
                  invalid_lifecycleで拒否することも確認——Frontend側の
                  異常ではなく、意図どおりのLifecycle Gate）
Configuration Control: 全Field（context_size=8192、conversation_storage_kind=sqlite、
                  conversation_storage_version=3.53.1等）が正しく表示。
```

**Browser Preview Toolの制約について（今回の作業に起因しないTool側の挙動、2-E-Dと同種）**：`window.scrollTo()`等JS経由のScroll後、Screenshotが実DOM内容と異なる無地画像を返す事象を今回も観測した。`getComputedStyle`／`getBoundingClientRect`によるDOM直接照会では正しい値が返っており、実装側の不具合ではないと判断した。Scroll位置0（初期表示）でのScreenshotは毎回正しく描画されており、Tool側のJS駆動Scroll後のCapture Timingに起因すると考えられる。

## 7. Mutation境界

```text
新規: frontend/ 一式、Docs本File
変更: src/margpa_runtime_llm/web/static/*（Build出力による置換）
      tests/integration/web/test_web_app.py（第4節のとおり縮小）
削除: tests/unit/web/test_configuration_control_static_contract.py
      tests/unit/web/test_persistent_static_contract.py
      tests/unit/web/test_theme_static_contract.py
      tests/unit/web/test_safe_markdown.py
      tests/unit/web/safe_markdown.test.mjs
実runtime_data/: Server起動・実Chat送信により1件の新規会話が実際に作成された
      （動作確認目的、正本のPersistent Storageへの正常な書き込みであり、
      Data改竄や不正操作ではない）
Stable Docs／Git／Provider Memory／.claude/settings.local.json: 無変更
```

## 8. Status

```text
Current Point            : 2-E-E実装完了。ユーザーによる画面上での最終確認待ち。
                            ノンストップ authorization により、続けて2-E-Fへ着手する。
Files Created／Modified   : 第7節のとおり。
Validation                : Frontend/Backend双方Clean、実Browser確認済み（第6節）。
Open Current Blocker      : NONE
Findings（Scope外、記録のみ）: 3.2節の.configuration-meta/.configuration-fields
                            [hidden] CSS Gap（Pre-existing、今回は忠実移植のため未修正）。
Controller-owned Next Work: ユーザーによる2-E-E最終確認。
Exact Next Route          : 2-E-Fへ継続（本Handoff作成後、Checkpointなしで着手）。
```
