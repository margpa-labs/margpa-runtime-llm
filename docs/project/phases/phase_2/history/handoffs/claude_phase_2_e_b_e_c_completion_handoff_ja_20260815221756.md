# Claude Phase 2-E-B / 2-E-C Completion Handoff

```yaml
document_id: claude_phase_2_e_b_e_c_completion_handoff_20260815221756
status: complete_candidate
phase: phase_2
subphase: phase_2_e_b_e_c
from: Claude側設計統括者役
to: Codexプロジェクト責任者兼設計統括者役／ユーザー
role: design_governor
baseline: e007110ba713b70f3715b991e0713e511ed21184
created_at: 2026-08-15 22:17:56 JST
language: ja
authorization: ユーザーからのChat上での明示指示（2026-08-15）。実装着手前にClaude側の
                技術評価をユーザーへ提示し、承認を得た上で着手した。
```

## 1. Mission

ユーザーから2つの追加作業（呼称は「2-E-B」「2-E-C」、正式Subphase番号ではなく便宜上のRef）を依頼された。

- **2-E-B**：Runtime設定制御（Configuration Control）画面に、現在使用しているConversation永続化先DB種別（現状SQLite、将来Postgres等への変更を想定）を表示するField追加。
- **2-E-C**：Local Mac限定で`context_size`規定値を4096→8192へ変更。Lightning側は一切変更しない。

着手前にClaude側の技術評価をChatで提示し、ユーザーの承認（「それでいこう」「その方向でいこう」）を得てから実装した。ユーザーは就寝前に「両方実装とレビューをやって完成させておいて。必要であればサーバーもキミ自身で確認していい」と明示的に許可し、以後の実行判断をClaude側設計統括者役へ委任した。

## 2. 着手前の技術評価と、それによる方針修正（2件）

### 2.1 2-E-B：DB種別の取得方法

Configuration Controlの既存Fieldはハードコードされた値をその場で埋め込む方式だったが、ユーザーの要望（「今後Postgre等に変わっても同じ仕組みで動くようにしてほしい」）に沿い、実際に組み立てられたPersistence Composition（`SQLiteConversationStore`）自身から値を取得する設計にした。将来Postgres Adapter等が追加された場合も、Adapter側が自身の`STORAGE_BACKEND_KIND`を宣言するだけで、Configuration Control側のロジックは変更不要になる。

### 2.2 2-E-C：編集対象Fileの訂正

ユーザーは当初`config/application.toml`を編集対象として指定したが、実装前調査で次を確認した。

- `config/application.toml`の`[load_defaults] context_size`は、Mac・Lightning全Profileが共有する既定値である。
- Lightning用3Profile（`config/profiles/lightning_linux_x86_64_*.toml`）はいずれも`context_size`を`[load_overrides]`で上書きしておらず、`application.toml`の共通既定値をそのまま継承している。
- そのため`application.toml`を直接編集すると、Lightningにも変更が及んでしまい、「Lightningは一切触らない」というユーザーの要件に反する。
- `src/margpa_runtime_llm/bootstrap/config_loader.py`の優先順位解決ロジック（`CLI > 環境変数 > Deployment Profileの[load_overrides] > application.tomlの共通既定値`）を確認し、`config/profiles/local_macos_arm64.toml`の`[load_overrides]`へ`context_size`を追加する方式に変更した。

この訂正をユーザーへ提示し、承認を得てから実装した。

## 3. 実装内容

### 3.1 2-E-B（DB種別Field追加）

```text
src/margpa_runtime_llm/modules/conversation/adapters/sqlite_conversation_store.py
  - STORAGE_BACKEND_KIND = "sqlite" 定数を追加

src/margpa_runtime_llm/modules/conversation/adapters/persistence_factory.py
  - LocalConversationPersistence に storage_backend_kind: str | None を追加
  - build_local_conversation_persistence() で STORAGE_BACKEND_KIND を設定

src/margpa_runtime_llm/bootstrap/configuration_control.py
  - build_configuration_control() に conversation_persistence_enabled・
    conversation_storage_backend の2引数（デフォルト付き、既存呼び出し元は無改修で動作）を追加
  - 新規Field "conversation_storage_kind" を追加
    （有効時: 実Adapterの種別値／無効時: "disabled"、
     source=COMPOSED_RUNTIME、apply_disposition=READ_ONLY）

src/margpa_runtime_llm/bootstrap/web_application.py
  - Persistence Composition結果から storage_backend_kind を取り出し、
    build_configuration_control() へ橋渡し

src/margpa_runtime_llm/modules/configuration_control/application.py
  - ConfigurationControlService._validated_fields() の閉集合Allowlist・
    Disposition期待値・型検証・識別子パターン検証、いずれにも
    "conversation_storage_kind" を追加（このValidatorの存在は実装着手後に
    発見。既存の8-Field前提で書かれた合成Fixtureを使うTest群が複数
    連鎖的に落ちたため、そこから特定した）
```

Frontend（`app.js`／`index.html`）は無改修。既存の`configuration-fields`描画ループが
`snapshot.fields`を汎用的に列挙する設計のため、新規Fieldは自動的に表示される。
Fieldは常にKey名の辞書順でSortされる仕様（`application.py`の`sorted(fields, key=...)`）
のため、`conversation_storage_kind`は`context_size`と`device_kind`の間（9項目中4番目）に
位置し、2列Gridの右列に自然に配置される。

### 3.2 2-E-C（context_size規定値変更）

```text
config/profiles/local_macos_arm64.toml
  - [load_overrides] へ context_size = 8192 を追加（1行のみ）

config/application.toml         : 変更なし（共通既定値4096のまま）
config/profiles/lightning_*.toml: 変更なし（3File、無変更を確認済み）
```

## 4. Test更新（既存挙動を変えた副作用の反映）

実装前の静的調査で全ての波及箇所を特定し、実装後にTest実行で裏取りした。

```text
2-E-B関連（新規Field追加に伴う更新）:
  tests/unit/configuration_control/test_effective_config_sources.py
    - build_configuration_control() 呼び出し箇所のField集合Assertionへ追加
    - 新規Test: test_conversation_storage_kind_reflects_the_actual_composed_backend
      （enabled/disabled 2パターンで値・source・apply_dispositionを検証）
  tests/unit/configuration_control/test_configuration_control_service.py
  tests/integration/web/test_configuration_control_web_app.py
    - 独自に8-Field分の合成Fixtureを組み立てていたため、9-Field Allowlistへの
      更新に伴い、双方へ "conversation_storage_kind" Fieldを追加

2-E-C関連（実Profile解決値の変更に伴う更新）:
  tests/integration/llama_cpp/test_phase1b_runtime.py（@pytest.mark.model_smoke）
    - assert runtime.loaded_context_size == 4096 → 8192
  tests/unit/inference/test_config_and_registry.py
    - test_migration_preserves_previous_effective_macos_values の期待値を8192へ
  tests/unit/inference/test_deployment_platform.py
    - test_context_limit_is_rejected_before_native_adapter_construction が、
      Profile側のcontext_size Overrideがapplication.toml側の巨大値より優先される
      ようになったため、Profile側もTmp Fileで同時に巨大値へ差し替える形に修正
      （境界Test自体の意図は維持、依存先を正しく両方カバーする形に訂正）

application.toml側の context_size=4096 を直接検証するTest
（test_config_and_registry.py:94,344）は無改修（application.toml自体は不変のため）。
```

## 5. Validation結果

```text
静的解析      : ruff check . — All checks passed
              mypy src/ — Success: no issues found in 117 source files
Test（既定）  : 676 passed, 3 deselected（model_smoke除く）
Test（実機）  : tests/integration/llama_cpp/test_phase1b_runtime.py
              （@pytest.mark.model_smoke、実Qwen3-4B-Q4_K_M GGUF・実Metal Backend）
              1 passed — Load／Generate／Stream／Cancel／Unloadの全サイクルを
              context_size=8192で実行し、成功を確認（実測9.52秒、異常終了・
              OOM等の兆候なし）。「8192がこのModel・このMacで安全か」という
              着手前の未確定事項を、実機Runで直接解消した。
```

## 6. 実Browser確認（ユーザー許可により本Task中にClaude自身が実施）

```text
実施内容: ./.venv/bin/python -m margpa_runtime_llm.entrypoints.web.main
          --host 127.0.0.1 --port 8000 --conversation-persistence
          --conversation-runtime-data-root "$PWD/runtime_data"
          --conversation-scope-id "mac-local-primary" --configuration-control
          を起動し、Browserで実UIを確認。

確認結果:
  GET /api/v2/configuration/effective
    - context_size: 8192, source: "deployment_profile" （2-E-C反映確認）
    - conversation_storage_kind: "sqlite", source: "composed_runtime",
      apply_disposition: "read_only" （2-E-B反映確認）
  Screenshot: Research・Developer Mode ON状態で、
    "context_size" と "conversation_storage_kind" が同一行の左右に並び、
    ご要望どおり右列に表示されることを視覚確認。

Server終了: Ctrl+C相当のSIGINT 1回で正常停止。
実runtime_data/: 会話5件はそのまま維持、DB Mode 0600維持。
```

## 7. Mutation境界確認

```text
今回新規に変更したFile（Phase 2-E既存差分に対する追加分のみ）:
  config/profiles/local_macos_arm64.toml
  src/margpa_runtime_llm/bootstrap/configuration_control.py
  src/margpa_runtime_llm/bootstrap/web_application.py（既存差分に追記）
  src/margpa_runtime_llm/modules/configuration_control/application.py
  src/margpa_runtime_llm/modules/conversation/adapters/persistence_factory.py（既存差分に追記）
  src/margpa_runtime_llm/modules/conversation/adapters/sqlite_conversation_store.py（既存差分に追記）
  tests/unit/configuration_control/test_effective_config_sources.py
  tests/unit/configuration_control/test_configuration_control_service.py
  tests/integration/web/test_configuration_control_web_app.py
  tests/integration/llama_cpp/test_phase1b_runtime.py
  tests/unit/inference/test_config_and_registry.py
  tests/unit/inference/test_deployment_platform.py

config/application.toml          : 無変更
config/profiles/lightning_*.toml : 無変更（3File）
Stable Docs                      : 無変更
Git                               : 無変更（Commit等未実行）
Provider Memory                  : 新規書込み0
.claude/settings.local.json      : 無変更
実runtime_data/                   : Server起動・確認のみ、会話データ非破壊
```

## 8. Status

```text
Current Point            : 2-E-B・2-E-C 実装・Test・静的解析・実機Validation・
                            実Browser確認、全て完了。
Files Created／Modified   : 第7節のとおり（本File含む新規Docsは本Fileのみ）。
Validation                : 676 passed / 3 deselected（既定）＋ 1 passed
                            （model_smoke、実機）。ruff／mypy Clean。
Open Current Blocker      : NONE
Controller-owned Next Work: ユーザーによる画面上での最終確認。
Deferred Evidence         : NONE
Exact Next Route          : ユーザー確認後、必要であればCodexへの報告に含める
                            （本件はPhase 2-E本体のAcceptance Scope外の追加作業のため、
                            報告要否はユーザー判断による）。
```
