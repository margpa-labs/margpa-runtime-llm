# Settings Modal UI再構成 — 完了Evidence

```yaml
document_id: claude_settings_modal_ui_restructure_completion_evidence
status: evidence_record
phase: phase_2
subphase: phase_2_e_i
from: Claude側設計統括者役
to: プロジェクト責任者兼設計統括者役（Codex）／ユーザー
role: design_governor
created_at: 2026-08-20 15:49:40 JST
language: ja
related:
  - claude_settings_modal_resize_complete_work_record_ja_20260820115319（前段：初回Resize作業の完全記録）
  - claude_output_anomaly_frontend_verification_loop_and_unwarned_system_permission_prompt_ja_20260820035328（前段：反映確認Failure分析）
  - claude_settings_modal_resize_verification_failure_recovery_index_ja_20260820035431（前段：対応するRecovery Index）
```

## 1. 位置づけ

本Docは、2026-08-20に行った、Settings Modal（設定画面）関連の一連のUI変更作業について、**ユーザーが「これでUI変更は全部完了」と明示した3項目**を対象に、最終状態と作業経緯をLossless水準で記録する完了Evidenceである。

対象は次の3項目。

1. 設定画面のSize変更（Modal自体の幅・高さ）
2. 設定画面内部の構成変更（「設定」Tab・「アドバンスモード」Tabの両方）
3. メイン画面への挨拶文追加

[claude_settings_modal_resize_complete_work_record_ja_20260820115319.md](claude_settings_modal_resize_complete_work_record_ja_20260820115319.md)（以下「前回Doc」）は、初回Resize作業（720px×640px → 870px×645px）とその反映確認Failureまでを記録していた。本Docは、それ以降に行われた、Modal Sizeの追加変更・内部構成の全面再設計・メイン画面の変更を対象とする続編である。

## 2. 項目1：設定画面のSize変更（最終状態への追加変更）

前回Doc時点の最終値は`width: min(870px, 100%)` / `max-height: min(645px, 100%)`だった。本Docの対象期間中、次の経緯でさらに変更された。

```text
870px × 645px（前回Doc時点）
  → 1450px × 645px（ユーザー指示「横幅、1450pxで。」）
  → 1550px × 645px（ユーザー指示「1550pxで」）
```

高さは645pxのまま変更なし。**最終値：`width: min(1550px, 100%)` / `max-height: min(645px, 100%)`。**

### 2.1「見た目が変わらない」という繰り返し報告の真因究明

870px×645pxへの変更後、ユーザーから「相変わらず全く変わってない」「5回目だぞ」との強い指摘が繰り返された。前回Docが特定できなかったPort 8000 Serverの断続的不安定性とは別に、本Doc対象期間では次の切り分けを行った。

- Claude側のBrowser Pane（実DataProfile・実`--configuration-control`込みで、ユーザーと同一のChat一覧を再現したServer Instance）で`getBoundingClientRect()`実測 → `870×645`を確認。
- `list_connected_browsers`によりClaude in Chrome拡張の接続を試みたが、未接続（拡張未Install）で直接のUser Browser調査は不可だった。
- ユーザー提供のScreenshot 2枚（時間差あり）を、CSS定義（`min(870px, 100%)`）とViewport幅（目視でおよそ1920px前後と推定）から比例計算した結果、実測値と矛盾しないことを確認。

最終的にユーザー自身から「1920pxの画面に対し、870pxで小さいゆーてたんだからそれはそうだ。僕が寝ぼけてたわ。すまん。」との説明があり、**Code・Build・配信経路のいずれにもBugは無く、大画面上での相対的な変化量の小ささ（720→870は幅+21%、640→645は高さ+5pxのみ）が体感しにくかったことが真因**と確定した。前回Docの「Port 8000断続的不安定性」とは別の、独立した要因である。

### 2.2 Server運用方針の確立（本件を機に整理）

本件の過程で、Server起動・停止に関する運用方針がユーザーから明示された。

- Claude側がVerification目的でServerを起動する場合も、**ユーザーと同一のPort（8000）・同一の起動Command（実`runtime_data/`・実Scope ID `mac-local-primary`・`--configuration-control`）を用いる**（別Port・別Scratch Dataでの独自環境は使わない）。
- **確認が終わったら、毎回必ずServerを停止する**（ユーザー自身の確認・作業を妨げないため）。同一Portは1 Processしか専有できず、Claude側が起動したままではユーザー側が起動できないという物理的制約も、この方針を裏付ける。

以降のVerification（項目2・3の検証を含む）は、この方針に従って実施した。

## 3. 項目2：設定画面内部の構成変更

「設定」Tab・「アドバンスモード」Tabの両方について、Nav・Button／Toggle・Layout・Field順序の変更を行った。ユーザーからの指示は2Roundに分かれ、1st Roundで縮小し過ぎた箇所を2nd Roundで調整する形となった。

### 3.1 Nav Tab（「設定」「アドバンスモード」）

```text
1st Round: flex-basis 168px→112px, font-size 0.62rem, padding 6px 8px（縮小指示）
2nd Round: flex-basis 112px→176px, font-size 0.62rem→0.93rem（1.5倍）,
           padding 6px 8px→9px 12px（縮小し過ぎとの指摘を受け拡大）
```

「アドバンスモード」の折返し有無は、両Roundとも実測（`getBoundingClientRect().height`が単一行の高さと一致すること）で確認した。

### 3.2 Button・OFF/ON Toggle類のSize統一

1st Roundでは、Research・Developer Mode Toggleのみを除外して他のButton・Toggleを縮小したが、結果的にResearch・Developer Mode側が相対的に大きく見え過ぎるという指摘を受けた。2nd Roundで、**要約モードのOFF/ON Toggle（Segmented Control）を基準としてその1.5倍**を統一Sizeと定義し、Research・Developer Mode Toggleを含む全Button・Toggleをこの1つのSizeへ統一した。

```text
統一後: font-size 0.75rem, padding 6px 11px
（Segmented Control Spanのみmin-width 53pxも追加指定）
```

対象：`.settings-modal-content`配下の全`<button>`（Refresh／Preview／Apply／Research・Developer Mode Toggle）、および`.segmented-control span`（要約モード・プロジェクトDocs参照）。Checkbox（`.switch-row input`、10px×10px）は本Roundの対象外（1st Round時点のSizeを維持）。

### 3.3「設定」Tab：2 Column化

`SettingsPanel.tsx`のJSX構造を、単一Grid（旧`grid-template-columns: repeat(2, minmax(0,1fr))`によるAuto Placement）から、明示的な2 Column Wrapper（`.settings-column-left` / `.settings-column-right`、中央に境界線）へ再構成した。

```text
左Column: 回答言語＋最大生成Token数（横並びPair）、推論生成＋推論過程を表示（横並びPair）、
          thinking-note、LLMへContext使用率を伝える、コンテキスト表示、表現重視モード
          （各Note付き）
右Column: 要約モード、プロジェクトDocs参照（各Note付き）
```

回答言語＋最大生成Token数のPairは、左Column幅（＝設定画面全体のちょうど半分）いっぱいに横並び配置。要約モード・プロジェクトDocs参照は、元の縦順序を保ったまま右Columnへ移動。プロジェクトDocs参照のNote文（日英とも）へ「RAG（Retrieval-Augmented Generation）」の言及を追加した。

**Bug発生と修正：`.switch-row{align-self:end}`。** この宣言は旧Grid Layout（`display:grid`）向けの調整だったが、2 Column化で`.settings-column`を`display:flex; flex-direction:column`へ変更したことにより、Cross軸（Column方向Flexでは水平方向）の「終端揃え」＝**右端揃え**という意図しない副作用を生んだ。横並びPair化した2項目（推論生成／推論過程を表示）は`flex:1`の効果で偶然影響を受けなかったが、単独行のままだった3項目（LLMへContext使用率を伝える／コンテキスト表示／表現重視モード）はこの副作用を直接受け、右端へ寄っていた。ユーザーからの再指摘を受けて特定・削除し、修正後は左端揃えを実測で確認した。

### 3.4「アドバンスモード」Tab：2 Column化とField順序

`ConfigurationControlPanel.tsx`を、`snapshot.fields.map()`による単一Grid Auto Placementから、`LEFT_COLUMN_FIELD_KEYS` / `RIGHT_COLUMN_FIELD_KEYS`という明示的なKey配列2本による2 Column Renderへ再構成した（Snapshot自体のField順序を変えず、表示順序のみをFrontend側で制御）。

Field順序は2 Roundの指示を経て、最終的に次の5:5へ確定した。

```text
左Column: research_developer_mode, context_size, max_new_tokens, selected_model, profile_key
右Column: acceleration_api, backend_kind, device_kind,
          conversation_storage_kind, conversation_storage_version
```

太字Key・Value部分のFont-sizeを3/4（12px）に縮小、「Research・Developer Mode」Labelを1.5倍・Bold（20.64px）に拡大。いずれも実測で確認済み。

### 3.5「表現重視モード」説明文の書き換え

日英とも、「www」「顔文字」等の口語的な例示表現を除き、より Business 文体（Tone調整である旨を簡潔に説明する形）へ書き換えた。

## 4. 項目3：メイン画面への挨拶文追加

`MessageList.tsx`の空状態表示（`.empty-state`、Chat未開始時）へ、`.empty-state-wrap`（Flex Column）で囲んだ上で、既存のTitle＋Note Blockと、固定Position表示の入力欄（Composer）との間に、次の挨拶文を追加した。

```text
ja: こんにちは。何でも質問してください。
en: Hello. Feel free to ask anything.
```

Font-sizeはTitle（`.empty-state h2`）と同一の1.5rem・Boldへ揃えた。配置は、`.main-content`／`.messages`の既存Padding値（Topbar Clearance分・Composer Clearance分）を差し引いた残りSpace（`calc(100vh - 76px - 190px - 18px - 18px)`）をFlex Columnとし、Title Blockの下の残余領域を`flex:1`＋中央揃えで埋めることで、Title BlockとComposerの間のちょうど中間に来るよう実装した。

## 5. 最終Deliverable状態

```text
frontend/src/styles/app.css                    : Settings Modal・内部構成・
                                                   空状態挨拶文、すべて反映済み
frontend/src/components/SettingsPanel.tsx        : 2 Column化・Pair化 反映済み
frontend/src/components/ConfigurationControlPanel.tsx
                                                  : 2 Column Field Render・
                                                    順序配列 反映済み
frontend/src/components/MessageList.tsx          : 挨拶文追加 反映済み
frontend/src/i18n/translations.ts                : RAG言及追加・表現重視モード
                                                    文言修正・挨拶文Key追加
                                                    （日英とも）反映済み
src/margpa_runtime_llm/web/static/*             : 上記すべてを反映した
                                                   最新Build成果物
                                                   （npm run build実行済み）
```

Verificationは、Claude側Browser Pane上で、ユーザーと同一のPort・実Data・実Scope ID・`--configuration-control`込みのServer Instanceに対し、`getBoundingClientRect()`・`getComputedStyle()`による実測、およびField順序の直接読み取りで行った。検証後、Serverは毎回停止済み（第2.2節の運用方針）。

## 6. Related Documents

- [claude_settings_modal_resize_complete_work_record_ja_20260820115319.md](claude_settings_modal_resize_complete_work_record_ja_20260820115319.md) — 前段：初回Resize作業の完全記録。
- [claude_output_anomaly_frontend_verification_loop_and_unwarned_system_permission_prompt_ja_20260820035328.md](../ai_system_anomalies/claude_code/claude_output_anomaly_frontend_verification_loop_and_unwarned_system_permission_prompt_ja_20260820035328.md) — 前段：反映確認Failureの分析・教訓。
- [claude_settings_modal_resize_verification_failure_recovery_index_ja_20260820035431.md](../../../phases/phase_2/history/handoffs/claude_settings_modal_resize_verification_failure_recovery_index_ja_20260820035431.md) — 対応するRecovery Index。
