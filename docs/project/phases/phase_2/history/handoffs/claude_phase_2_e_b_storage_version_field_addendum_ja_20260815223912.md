# Claude Phase 2-E-B Addendum — Storage Engine Version Field

```yaml
document_id: claude_phase_2_e_b_storage_version_field_addendum_20260815223912
status: complete_candidate
phase: phase_2
subphase: phase_2_e_b_e_c
from: Claude側設計統括者役
to: Codexプロジェクト責任者兼設計統括者役／ユーザー
role: design_governor
baseline: e007110ba713b70f3715b991e0713e511ed21184
created_at: 2026-08-15 22:39:12 JST
language: ja
authorization: ユーザーからのChat上での明示指示（2026-08-15、
                「今の方式のままでver番号まで取れんかな？」）
related:
  - claude_phase_2_e_b_e_c_completion_handoff_ja_20260815221756
```

## 1. 背景

[claude_phase_2_e_b_e_c_completion_handoff_ja_20260815221756.md](claude_phase_2_e_b_e_c_completion_handoff_ja_20260815221756.md)にて`conversation_storage_kind`（DB種別、例："sqlite"）を追加した後、ユーザーから「Engine自体のVersion番号（Postgresで言う`16.x`相当）も同じ方式のまま取れないか」という追加依頼を受けた。

`sqlite-1`／`sqlite-2`（`storage_schema_version`）はこのProject自身が定義するSchema版であり、SQLiteというSoftware自体のVersionとは別概念である旨を先にChatで説明し、その上で「DB Engine自体のVersion」を新規に取得する方針で合意した。

## 2. 実装内容

```text
src/margpa_runtime_llm/modules/conversation/adapters/sqlite_conversation_store.py
  - SQLiteConversationStore.backend_version Propertyを追加（sqlite3.sqlite_version を返す。
    リンクされているSQLite C Library自体のVersion。Fileを開かずに取得可能）

src/margpa_runtime_llm/modules/conversation/adapters/persistence_factory.py
  - LocalConversationPersistence に storage_backend_version: str | None を追加

src/margpa_runtime_llm/bootstrap/configuration_control.py
  - build_configuration_control() に conversation_storage_backend_version 引数を追加
  - 新規Field "conversation_storage_version" を追加
    （有効時: 実Engine Version／無効時: "disabled"、
     source=COMPOSED_RUNTIME、apply_disposition=READ_ONLY）

src/margpa_runtime_llm/bootstrap/web_application.py
  - Persistence Compositionから storage_backend_version を橋渡し

src/margpa_runtime_llm/modules/configuration_control/application.py
  - _validated_fields() の閉集合Allowlist等へ "conversation_storage_version" を追加
    （前回2-E-Bで発見済みのValidatorのため、今回は波及箇所を事前に把握した上で
    一度で反映）
```

Frontend無改修（既存の汎用描画ループにより自動反映）。将来Postgres等のAdapterが追加された場合も、そのAdapterが`backend_version`（実際にはLive接続からのServer Version問い合わせ等になる想定）を実装するだけで、この上位の仕組みは変更不要である。

## 3. Test更新

前回2-E-Bで発見した閉集合Validatorの存在を踏まえ、今回は事前に全波及箇所を洗い出してから一括反映した（実装後の追加発覚は0件）。

```text
tests/unit/configuration_control/test_effective_config_sources.py
  - Field集合Assertionへ追加
  - test_conversation_storage_kind_reflects_the_actual_composed_backend を
    test_conversation_storage_kind_and_version_reflect_the_actual_composed_backend へ拡張
    （kind・version 両方をenabled/disabled双方でパラメータ化検証）
tests/unit/configuration_control/test_configuration_control_service.py
  - service()合成Fixtureへ追加、Field集合Assertion2箇所へ追加
tests/integration/web/test_configuration_control_web_app.py
  - configuration_service()合成Fixtureへ追加、Field集合Assertionへ追加
```

## 4. Validation結果

```text
静的解析: ruff check . — All checks passed
        mypy src/ — Success: no issues found in 117 source files
Test    : 676 passed, 3 deselected（既定Suite、前回2-E-B/2-E-Cと同数を維持）
実Browser: 実Server起動、GET /api/v2/configuration/effective で
        "conversation_storage_version": "3.53.1" を実際に確認
        （このMac実機にLinkされているSQLite C Libraryの実Version。
        `sqlite3.sqlite_version`をSourceに直接埋め込まず、都度呼び出して
        取得する設計にしたため、Hardcode値ではなく実行時の実測値である）
Server終了: SIGINT 1回で正常停止。
```

## 5. Mutation境界

```text
新規変更File: 上記6File（2-E-B/2-E-Cで既に変更済みのFileへの追記）
新規Docs    : 本Fileのみ
Stable Docs／Git／Provider Memory／.claude/settings.local.json: 無変更
実runtime_data/: Server起動・確認のみ、破壊的操作なし
```

## 6. Status

```text
Current Point            : Storage Version Field 追加完了。
Files Created／Modified   : 第2節のとおり。新規Docsは本Fileのみ。
Validation                : 676 passed / 3 deselected、ruff／mypy Clean、実Browser確認済み。
Open Current Blocker      : NONE
Exact Next Route          : ユーザー確認待ち。
```
