# Claude Phase 2-E-H（会話「名前変更」「削除」）工程分割・工程設計

```yaml
document_id: claude_phase_2_e_h_process_breakdown_design_20260816173714
status: design_draft
phase: phase_2
subphase: phase_2_e_h
from: Claude側設計統括者役
to: 新Task（新Session）のClaude側設計統括者役／プロジェクト責任者兼設計統括者役（Codex）
role: design_governor
baseline: e007110ba713b70f3715b991e0713e511ed21184
created_at: 2026-08-16 17:37:14 JST
language: ja
authorization: |
  ユーザー指示（2026-08-16、Context Window残り約4%時点）。
  「Hの工程分割、工程設計をやって」。今Session内でHについて最も
  理解を持つ状態のうちに、着手前設計を先出ししておく目的。
  実装は本Docの承認を経て新Task側で行う想定（未着手）。
related:
  - claude_phase_2_e_expansion_index_ja_20260816165825
  - claude_phase_2_e_e_to_h_react_migration_design_ja_20260816102654
```

## 0. 位置付け

本Docは2-E-H着手前の設計をまとめたもの。第5節の設計判断は2026-08-16、ユーザー確認により全4問（Q1〜Q4）確定済み。実装（Domain／Port／Adapter／API／Frontend何れも）は依然として一切未着手——ユーザーが実装着手前にBackupを取得したい意向のため、着手はBackup完了後のユーザー指示を待つ。

**新Task化はしない**：Context Window圧縮Trigger実験（[運用メモ第9節](../../../shared/task_roles/claude_side_design_governor_operating_notes_ja.md)）の結果、圧縮後にContext余裕が実質的に回復したため、Hは新Task（新Session）へ切り替えず、本Sessionが引き続き担当する。以下の「新Task側Claude Code」向け記述は、将来的にRecovery目的で本Docを読む別Sessionが現れた場合の一般的な参照情報として残す。

## 1. Mission

会話一覧（ChatListItem Option Menu）に既存の「再開／Archive・Unarchive」へ加え、「名前変更（Rename）」「削除（Delete）」を新規実装する。2-E-B〜Gが既存機能のFrontend移植・UI調整だったのに対し、Hは**新規Backend機能**を要する初のSub-phase（既存Docsでも「余力枠」「Scopeが一段階上がる」と位置付けられていた）。

## 2. 設計の前提（本Session内で確認済みの既存Architecture事実）

着手前設計にあたり、以下をCode直接確認した（新Task側の再確認コストを省くため記録）。

```text
src/margpa_runtime_llm/modules/conversation/ports/conversation_store.py
  ConversationRepositoryPort（Protocol）:
    get() / get_commit_receipt() / commit(command: CommitConversation) / list()
  → 書込みPrimitiveは commit() の一本のみ。「Snapshot＋Revision」型の
    Event-sourcing寄りモデルであり、個別Fieldに対するUPDATE文的な
    Port Methodは存在しない（例：set_archived的なPort Methodはない）。

src/margpa_runtime_llm/web/persistent_routes.py
  /{conversation_id}/archive, /unarchive はどちらも共通の
  _archive_mutation() 経由で service.set_archived(...) を呼ぶ。
  → 「Archived状態」はPort層ではなくApplication層
    （PersistentConversationService、application/persistent_conversation_service.py）
    のMethodとして表現されており、内部でCommitConversationを組み立てて
    commit()を呼んでいると推測される（本Session内では当該Service実装
    本体までは未確認、新Task側で最初に読むべき箇所）。

frontend/src/components/Sidebar/ChatListItem.tsx
  ChatListAction = "resume" | "archive" | "unarchive"（Union型）。
  Option Menuは`onAction(item.conversation_id, action)`を呼ぶ薄い
  Presentation Component。App.tsx側のchatListItemAction()が
  非選択中会話のRevision取得→Mutation呼出という共通Flowを担う
  （2-E-F実装時に確立、Session内Errors記録済み）。
```

**この前提から導かれる設計方針**：RenameもDeleteも、Archiveの前例に倣い「Snapshotへ新規Stateを載せてcommit()する」形で実装するのが、既存Architectureと一貫性を持つ唯一の素直な経路。Port層に新規Method追加は（Archiveがそうしなかったのと同様）不要な可能性が高い——ただしDeleteを「物理削除」として設計する場合はこの前提が崩れる（第5節Q2で扱う）。

## 3. Phase分割（H-1〜H-5）

2-E-E/F/Gの「設計→実装→Validation→実Browser確認→Docs化」のCycleを踏襲。

```text
H-1  Backend設計確定（本Docの第5節Open Question解消がGate）
     - Rename: Snapshotに`title`（またはdisplay_name）Field追加要否の
       確定。追加する場合はStorage Schema変更＝Migration要（sqlite-1→
       sqlite-2の明示的Migration Path慣習に倣う）。
     - Delete: 「Soft（一覧から完全除外する新State）」か
       「Hard（物理行削除）」かの確定（第5節Q2）。

H-2  Backend実装：Rename
     - PersistentConversationServiceへrename_conversation()相当を追加
       （set_archived()と同型：expected_revision受取→CommitConversation
       構築→commit()）。
     - 必要ならSQLite Migration Step新規追加（sqlite_migration.py、
       既存Step Chainへ新Step追加、source_version/target_versionを
       既存の最終Versionから連番）。
     - web/persistent_contracts.py: PersistentMutationRequest系にTitle
       欄を持つ新規Contract（Rename専用、または既存Requestを拡張）。
     - web/persistent_routes.py: POST /{conversation_id}/rename
       （archive/unarchiveと同型のRoute定義）。
     - Test: Application層Unit Test（Service）、Adapter Test（SQLite
       実File経由、正常系／Revision競合409系）、Integration Test
       （test_persistent_web_app.py等、既存archiveのTest群を写経）。

H-3  Backend実装：Delete
     - 第5節Q2の結論に従う。Soft側で決着した場合はH-2とほぼ同型
       （新Stateの追加＋一覧Queryでのfilter対応）。Hard側で決着した
       場合はPort層へ新規Capability（例：purge()）の追加を要し、
       Scopeが拡大する（第5節Q2に詳細）。
     - Test: H-2と同型の3層（Service/Adapter/Integration）。

H-4  Frontend配線
     - ChatListAction Union型へ"rename" | "delete"を追加。
     - Rename: 既存Resume/Archiveは追加入力なしのFire-and-forgetだが、
       RenameはText入力を要するため、chatListItemAction()の単純な
       共通Flowでは足りない。Option Menu内Inline編集（Input表示→
       Enter/Blurで確定）を新規UI Patternとして設計する必要あり
       （SettingsModalのような別Modal起動ではなく、List内Inline編集の
       方がUX的に自然と考えられるが、これも設計判断——第5節Q3）。
     - Delete: 破壊的操作のため、確認Dialog（誤操作防止）を挟むかが
       設計判断（第5節Q4）。
     - api/client.ts: renameConversation() / deleteConversation()追加。
     - i18n/translations.ts: persistentRename, persistentDelete等の
       新規Key追加（ja/en両方）。

H-5  全体Validation・実Browser確認・Docs化
     - npm run {lint,typecheck,test,build} Clean確認。
     - pytest -q Clean確認（新規Test込みで既存664件から増加）。
     - 実Browser・実LLM・実Backendでの動作確認（Rename即時反映、
       Delete後に一覧から消えること、Revision競合時のError表示、
       White/Dark両Theme）。
     - Completion Handoff（claude_phase_2_e_h_completion_handoff_ja_
       YYYYMMDDHHMMSS.md）＋Automation Governance Evidence作成。
```

## 4. 既存慣習との対応表（新Task側の実装時Reference）

```text
観点                  Archiveでの前例                    Renameでの適用       Deleteでの適用
Application層Method   set_archived(id, archived, rev)    rename_conversation  soft: set_deleted 相当
                                                          (id, title, rev)     hard: 要新規設計
Route                 POST .../archive, .../unarchive     POST .../rename      POST .../delete
Frontend Action型      "archive" | "unarchive"            "rename"（要Text入力） "delete"（要確認UX）
Revision競合Handling   既存の409 Conflict Flow流用可能     同左                 同左
一覧表示                archivedはFilter切替で表示継続      通常表示のまま        一覧から即消える
                                                                                （soft/hard共通の
                                                                                 期待挙動）
```

## 5. 設計判断（旧Open Design Question、2026-08-16ユーザー確認により全4問確定）

Context予算の都合上、当初は技術検討のみに留め、製品としての意思決定はユーザー確認を経て確定させる方針としていた。以下、2026-08-16の会話でユーザーが全4問へ回答し、確定した。

```text
Q1. Renameの入力制約
    【決定】暫定的に、Claude／ChatGPT等の一般的な会話Threadと同等の
    制約とする（文字数上限あり、空文字列は自動生成Titleへfallback、
    改行・制御文字は許容しない単一行入力）。正確な数値は実装時に
    既存の入力Sanitize方針（safe_markdown.js削除の経緯等）と整合を
    取った上で決める。

Q2. Deleteの方式
    【決定】Soft（一覧除外のみ、DB内Row保持）。
    【理由（ユーザー原文要旨）】実装が楽だからではなく、将来利用者が
    増えた場合「大事なスレを誤ってDELETEしてしまった」という事故が
    必ず起きるため。DBに残っていれば運用側で復元できる可能性が残る。
    Archiveは本人が目に見えて自己管理できる点でDeleteと性質が異なる。

Q3. Rename UI
    【決定】List内Inline編集（Titleをその場でText Boxへ切替、
    別Dialog／Modalは起動しない）。

Q4. Delete実行前の確認Dialogの要否・文言
    【決定】確認Dialogは要。文言は暫定でよく、後から変更可能という
    前提のもと、「本当に削除しますか？慎重に判断してください。」
    程度のシンプルな文言で当面よい（下記5.1節[A]のRestore方式決定を
    踏まえ、「いつでもArchiveに戻す事は出来ます」という当初案は
    不採用とした）。
```

### 5.1 追加確認事項（同ラウンドで解決）

```text
[A] Restore方式：運用側のみがDB直接操作で復元可能とする
    （ユーザー向けSelf-service Restore UIは今回のH Scopeに含めない）。
    ユーザー本人から見た挙動としては、Deleteは一覧から完全に消える
    一方通行に近い操作となる。背景：ユーザーより「OSSなりプロダクト化
    した後の話を想定して(a) User Self-service Restore／(b) 運用側限定
    Restoreのどちらか聞いただけ」との補足あり。現時点のH Scopeでは(b)
    で確定。将来Self-service Restore UIを追加する余地は排除しない
    （追加時は別途新規Sub-phaseとして扱う）。

[B] 「設定内にArchive化したスレリスト」UI：H Scope外・将来Item。
    ユーザーより「そのうち置く予定」との明言あり。今回のH設計には
    組み込まない。将来このUIが追加された場合、Deleteとの関係
    （Delete後のRestoreをこのUI経由でSelf-service化するか等、[A]との
    関連）を改めて検討する余地がある、という点だけ記録しておく。
```

### 5.2 未定事項（現時点で計画なし、将来の可能性として排除しない）

```text
- User Self-service Restoreボタン／「Deleted一覧」的なUIの新設
  現時点では実装・計画の予定なし（本H Scopeでは5.1節[A]の通り、
  運用側限定でのRestoreとして確定）。ただし将来（OSS化・プロダクト化
  等の局面で）必要になる可能性はゼロではないため、確定事項ではなく
  未定事項として記録しておく。着手する場合、本Docの延長ではなく
  別途新規Sub-phaseとして扱う。
```

## 6. Risk・複雑度メモ

```text
- H-2（Rename）は既存Archive Patternへの追従度が高く、複雑度は
  2-E-B〜D相当（低〜中）と見積もる。
- H-3（Delete）はQ2の結論次第で複雑度が大きく変わる：Soft側なら
  H-2と同等、Hard側ならPort層拡張・Migration設計・Cascade削除
  （関連Turn／Citation等の付随Data）の考慮が追加され、2-E-E
  （React移行本体）に近い複雑度になり得る。
- Frontend Inline編集UI（Q3次第）は、本Session内で確立した
  CSS Architecture（.app-shell Custom Property継承等）と直接の
  衝突はないと考えられるが、新規Component設計であるため、
  過去5RoundのCSS微調整と同様、実画面確認前提でIteration計画を
  組むことを推奨する（[自己評価Evidence](../../../shared/history/automation/automation_governance_evidence_claude_frontend_design_capability_self_assessment_ja_20260816161000.md)参照）。
```

## 7. Status

```text
Current Point            : 第5節の設計判断、全4問（Q1〜Q4）＋追加確認
                            事項2件（5.1節[A][B]）、2026-08-16ユーザー
                            確認により確定。実装はユーザーがBackup取得を
                            先に済ませたい意向のため、まだ未着手。
Files Created／Modified   : 本Fileのみ（第0節・第5節を更新）。実装Fileは
                            無変更。
Validation                : N/A（設計Doc）
Open Current Blocker      : ユーザーによるBackup取得完了待ち
                            （実装着手Gate。技術的Blockerではない）。
Controller-owned Next Work: ユーザーがBackup取得完了後、H-1（Backend
                            設計確定、本Docでほぼ完了済み）以降の実装
                            着手指示。
Exact Next Route          : 本Session（新Task化なし）が、ユーザーの
                            実装開始指示を待ってH-1から着手する。
```
