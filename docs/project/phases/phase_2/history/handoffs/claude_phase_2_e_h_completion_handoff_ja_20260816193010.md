# Claude Phase 2-E-H（会話「名前変更」「削除」）Completion Handoff

```yaml
document_id: claude_phase_2_e_h_completion_handoff_20260816193010
status: implementation_complete
phase: phase_2
subphase: phase_2_e_h
from: Claude側設計統括者役
to: ユーザー（最終確認者）／Codexプロジェクト責任者兼設計統括者役
role: design_governor
baseline: e007110ba713b70f3715b991e0713e511ed21184
created_at: 2026-08-16 19:30:10 JST
language: ja
authorization: |
  ユーザー指示（2026-08-16、Backup取得完了後）：「作業開始で、可能であれば
  ノンストップH実装完了狙いでよろしく」。設計は事前に
  claude_phase_2_e_h_process_breakdown_design_ja_20260816173714.md で
  確定済み（Q1〜Q4＋追加確認事項2件）。
related:
  - claude_phase_2_e_h_process_breakdown_design_ja_20260816173714
  - claude_phase_2_e_expansion_index_ja_20260816165825
```

## 1. Mission

会話「名前変更（Rename）」「削除（Delete、Soft）」の新規Backend実装（Domain→Port→Adapter→API→Test一式）＋Frontend配線。設計Doc確定内容どおり、Non-stopで最後まで実装完了した（想定外の技術Blockerは発生せず、途中停止なし）。

## 2. 実装内容

### 2.1 Backend

```text
src/margpa_runtime_llm/modules/conversation/domain/models.py
  - ConversationState.DELETED新設。
  - ConversationSnapshot／ConversationSummaryへtitle: str | None追加
    （MAX_CONVERSATION_TITLE_CHARACTERS = 200、非空・Trim済み・
    制御文字禁止のValidator共通化）。
  - validate_aggregate()のARCHIVED専用制約（Active Session禁止・
    非終端Turn禁止）をDELETEDにも拡張。

src/margpa_runtime_llm/modules/conversation/adapters/sqlite_conversation_store.py
  - STORAGE_SCHEMA_VERSIONを sqlite-2 → sqlite-3 へ。
  - conversations Tableへtitle TEXT列追加（CREATE TABLE／INSERT／
    UPDATE／SELECT全箇所、state・head_turn_idと同じ「Domain Field
    ＋冗長SQL列・整合Cross-check」Patternで実装）。

src/margpa_runtime_llm/modules/conversation/adapters/sqlite_migration.py
  - LEGACY_STORAGE_SCHEMA_VERSION_SQLITE_2新設。
  - 既存TURN_CITATIONS_MIGRATION_STEPのtarget_versionを、動的な
    STORAGE_SCHEMA_VERSION参照から固定のsqlite-2Literalへ訂正
    （後述3.2）。
  - 新規CONVERSATION_TITLE_MIGRATION_STEP（sqlite-2→sqlite-3、
    ALTER TABLE ADD COLUMN title、純追加・既存Row書換えなし）。

src/margpa_runtime_llm/modules/conversation/adapters/persistence_factory.py
  - known_legacy_versionsへsqlite-2追加、steps Tupleへ新Migration
    Step追加。

src/margpa_runtime_llm/modules/conversation/application/persistent_conversation_service.py
  - rename_conversation()：set_archived()と同型（expected_revision
    受取→Snapshot更新→commit()）。DELETED状態からのRenameは拒否。
  - set_deleted()：一方向（Restore方法なし、5.1節[A]設計判断どおり）。
    Active Session Close・非終端Turn拒否はset_archived(archived=True)
    と同じGuardを流用。

src/margpa_runtime_llm/web/persistent_contracts.py
  - PersistentRenameRequest（title、空文字列許容＝Auto Titleへ
    Fallbackの合図、制御文字は拒否）。
  - Summary／Detail両ResponseへtitleField追加。

src/margpa_runtime_llm/web/persistent_routes.py
  - POST /{id}/rename、POST /{id}/delete新設。
  - list_conversations：state未指定時のDefaultを「全State」から
    「DELETED以外全State」へ変更（Archived等の既存表示は無変更、
    Deletedのみ新たに除外）。明示的に?state=deletedを指定すれば
    引き続き参照可能（将来のSelf-service Restore UI等のため、5.2節
    未定事項）。
```

### 2.2 Frontend

```text
frontend/src/types.ts
  - PersistentConversationSummaryへtitle追加、PersistentConversation
    Detail.stateへ"deleted"追加。

frontend/src/api/client.ts
  - renamePersistentConversation()新設。

frontend/src/components/Sidebar/ChatListItem.tsx
  - ChatListAction += "delete"（"rename"はTitleを伴うため別Callback
    onRenameとして分離）。
  - List内Inline編集：Rename選択でText Box化（現Title Seed、Enter／
    Blurで確定、Escapeで破棄）。
  - Delete選択でwindow.confirm()確認後にonAction("delete")。

frontend/src/components/Sidebar/ChatList.tsx、Sidebar.tsx
  - onRename PropをApp.tsxまで一貫して配線。

frontend/src/App.tsx
  - chatListItemRename()新設（chatListItemAction()と同型のRevision
    解決ロジックを流用）。
  - chatListItemAction()：action==="delete"かつ選択中会話が対象の
    場合、Detail再表示ではなく選択解除（Message欄Clear）——削除
    直後にStaleなMessageを表示し続けないための対応。

frontend/src/i18n/translations.ts
  - persistentRename／persistentDelete／persistentDeleteConfirm
    （ja／en）追加。

frontend/src/styles/app.css
  - .chat-list-item-rename-input新設（--focus-accent枠。第4/5弾で
    否定されたComposer／Topbarの静的Chrome境界とは異なり、こちらは
    入力中であることを示す一時的なFocus Indicatorとしての使用であり、
    用途として妥当と判断）。
```

## 3. 設計判断メモ（実装時に確定した技術詳細）

### 3.1 titleをDomain Snapshotに含めつつDOMAIN_SCHEMA_VERSIONは据え置いた理由

`ConversationSnapshot`は`snapshot_json` BLOBへ丸ごとJSON Serializeされ、その Envelopeには`domain_schema_version`が埋め込まれて厳格照合される。titleを新規Optional Field（デフォルトNone）として追加するだけなら、Pydanticの標準的な後方互換（旧Recordに"title"KeyがなくてもNone Defaultで解決）で十分であり、`DOMAIN_SCHEMA_VERSION`（現状"1"、これまで一度も変更実績なし）を上げると、既存Snapshot全件のEnvelope書換えを伴う、より重い・Risk高めのMigrationになる。今回はPure additive（新Column追加のみ、既存Row無変更）で済む`STORAGE_SCHEMA_VERSION`側のBumpだけに留め、`DOMAIN_SCHEMA_VERSION`は不変とした。

### 3.2 既存TURN_CITATIONS_MIGRATION_STEPのtarget_version訂正について

同Stepは元々`target_version=STORAGE_SCHEMA_VERSION`（当時"sqlite-2"）という、モジュール定数を直接参照する書き方だった。今回`STORAGE_SCHEMA_VERSION`を"sqlite-3"へ変更したことで、この動的参照が意図せず「sqlite-1から直接sqlite-3へ」を主張してしまう不整合が発生（実際にはturn_citations Tableを足すだけのTransformであり、title列は追加しない）。固定Literal `LEGACY_STORAGE_SCHEMA_VERSION_SQLITE_2`へ参照を切り替えて訂正した。これに伴い、既存Test`test_turn_citations_migration_step_adds_the_table_additively`（sqlite_migration.py）、および`tests/integration/conversation/test_local_conversation_persistence.py`の`_downgrade_to_legacy_sqlite1()`Helperが、fresh storeから作った「偽Legacy State」にtitle列が残ったままだったため`ALTER TABLE conversations DROP COLUMN title`を追加して修正した（同Pattern2箇所）。

### 3.3 Deleteの一方向性（Restoreなし）の実装

`set_deleted()`は`set_archived()`と異なり`deleted: bool`引数を持たない、常に一方向のTransitionのみを提供するMethodとして実装した。設計Doc5.1節[A]の決定（Restoreは運用側のみ・DB直接操作）どおり、Application層にもRestore経路のAPIを一切用意していない。

## 4. Validation結果

```text
Backend:
  pytest -q                : 682 passed, 3 deselected（Baseline 664から
                              新規18件、既存Test2件の修正込み）
  ruff check                : All checks passed（変更File一式）
  mypy                      : Success, no issues found（32 source files）

Frontend:
  npm run lint              : Clean（0 errors）
  npm run typecheck          : Clean（0 errors）
  npm test                    : 69 passed（12 Test Files、Baseline 64から
                                新規9件・修正6件）
  npm run build                : 成功（app.js 247.12kB / gzip 76.03kB、
                                app.css 15.48kB / gzip 3.94kB）
```

## 5. 実Browser確認（実LLM Server起動、実Backend、White／Dark両Theme）

`.claude/launch.json`へ新規Preview設定`margpa-web-h-verify`を追加（Scratchpad配下の専用runtime-data-rootを使用、実DataやProduction Runtime Dataには一切触れない）。

```text
Rename        : Sidebar Option Menu→「名前変更」→List内Inline編集への
                切替、既存Titleがtext入力欄へSeedされることを確認。
                Enterで確定・一覧へ反映、Blurでも確定（クリックして
                Message入力欄へFocus移動）、Escapeで破棄（元Titleへ
                復帰）——3経路すべて実Browserで確認。
Delete        : Option Menu→「削除」→Confirm Dialog経由→Sidebar一覧
                から即消滅を確認。Network Request（POST .../delete）
                200 OKを確認。Server側 `GET /api/v2/conversations`
                （Default）で対象が含まれないこと、`?state=deleted`
                では引き続き参照可能・title保持済みであることを
                curlで直接確認。
White／Dark   : Rename Inline編集Input（--focus-accent枠）がDark
                Themeでも視認性良好であることを確認。
```

**運用知見（Tool制約、3件）**：

```text
1. Browser PreviewのPlugin起動（`preview_start` with name経由）が、
   本Project Directory Path（日本語文字を含む）に対し
   "getcwd: cannot access parent directories: Operation not permitted"
   でCode 126失敗した。Bash Tool側では同一Pathへ全く問題なくアクセス
   できており、Browser Preview Tool固有のSandbox制約と判断。回避策：
   Bash側で`nohup ... &`によりServerを直接起動し、`preview_start`は
   `url`のみ指定してAttachする形へ切替えた（既存の2-E-E運用知見と
   同系統の回避Pattern）。

2. `window.confirm()`のような、Native Browser Blocking Dialogは、本
   Browser Tool環境では自動的にCancel（`false`）される（明示的な
   Accept手段が見当たらない）。Delete Confirm Flowの実地検証では、
   `javascript_tool`で`window.confirm`を一時的に`() => true`へ
   Monkey-patchした上でClickし直すことで、実装コード自体
   （`window.confirm(...)`呼び出しそのもの）を変更せずに検証できた。
   Production Code側は素の`window.confirm()`のまま、この回避は検証
   手順のみに閉じている。

3. `computer` Toolの`key`Actionで`text: "Return"`を送った場合、
   ReactのonKeyDownで`event.key === "Enter"`とは一致せず、Rename
   確定が発火しなかった（Blur経由では正しく確定した）。`text: "Enter"`
   へ変更したところ正しく動作した——同じ物理キーでも、本Tool内部の
   Key Label指定によってDOM Event側の`key`値が変わる（または正しく
   伝播しない）Caseがある、という運用知見。今後Enter Keyの動作検証
   をする際は`"Enter"`Labelを使うこと。
```

## 6. Mutation境界

```text
変更: 上記2.1／2.2のFile一式（Backend/Frontend Source＋Test）
      src/margpa_runtime_llm/web/static/*（Build出力による置換）
      .claude/launch.json（新規、Preview検証専用Server設定を追加）
実runtime_data/: 実データ・本番Runtime Dataは無変更。実Browser確認は
      Scratchpad配下の専用runtime-data-root（H検証専用、Scope ID
      "h-verify-scope"）でのみ実施し、確認後にServer停止済み。
Stable Docs／Git／Provider Memory／.claude/settings.local.json:
      Git・Provider Memory無変更。Stable Docsは
      claude_phase_2_e_h_process_breakdown_design_ja_20260816173714.md
      （設計確定時点で既に更新済み、本Handoffでは追加変更なし）。
```

## 7. Status

```text
Current Point            : 2-E-H（Rename・Delete）実装完了。Backend／
                            Frontend双方Clean Validation、実Browser
                            確認（Light／Dark）まで完了。Non-stop完走
                            （途中停止なし）。
Files Created／Modified   : 第2節・第6節のとおり。
Validation                : 第4節のとおり、Backend／Frontend双方Clean。
Open Current Blocker      : NONE
Controller-owned Next Work: ユーザーによる最終確認（実画面での目視含む）。
Exact Next Route          : ユーザー確認待ち。5.2節の未定事項（将来の
                            Self-service Restore UI等）は引き続き
                            未定のまま、着手判断はユーザー次第。
```
