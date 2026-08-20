# Phase 2-E sqlite-1 → sqlite-2 Real Mac Migration and Rollback Procedure

```yaml
document_id: claude_phase_2_e_real_mac_migration_and_rollback_procedure_20260815092359
status: procedure
phase: phase_2
subphase: phase_2_e
from: Claude設計統括者役
to: ユーザー（実行者）／Codexプロジェクト責任者兼設計統括者役（Review者）
role: design_governor
baseline: e007110ba713b70f3715b991e0713e511ed21184
created_at: 2026-08-15 09:23:59 JST
language: ja
supersedes: なし（`claude_phase_2_e_rework_completion_handoff_20260815084816.md`第4節の曖昧な記載を、
             本文書が正本として置き換える。旧Fileは書き換えない）
source_finding: codex_to_claude_phase_2_e_final_rework_handoff_20260815090218.md P2E-CODEX-006
```

本手順は**ユーザーが実Mac上で自ら実行するもの**である。Claude側は実`runtime_data/`のMigration・Rollback・Read・Writeを一切行わない（既に取得済みのMetadata確認も本Reworkでは再実行していない）。

## 0. 前提の訂正（P2E-CODEX-006指摘の反映）

前回`claude_phase_2_e_rework_completion_handoff_20260815084816.md`第4.3節は`uv run margpa-web`という不完全な例示Commandを示していたが、これは実際にユーザーが使用・検証済みのLocal起動経路（`--conversation-persistence`、`--conversation-runtime-data-root`、`--conversation-scope-id`等、必須Flag一式を伴うもの）と一致しない可能性がある。

本文書は「新しいCommandを使う」のではなく、「**ユーザーが既に使い、動作を確認済みの、実際の起動Commandへ、Flagを1個だけ追加する**」という形で正本化する。Claude側はユーザーの実際のCommand文字列（`--conversation-runtime-data-root`の実Pathや`--conversation-scope-id`の実値を含む）を知らず、Docsへ記録することも許可されていない（Absolute Path等の非記録原則、Handoff §6.3系列と同じ境界）。

## 1. 事前確認（Migration要否の判定）

ユーザーが**普段どおりの、これまで動作確認済みの**起動Commandで、追加Flagなしにいつもどおり起動する。

```text
（普段どおりのCommand。例："uv run margpa-web --conversation-persistence
  --conversation-runtime-data-root <あなたが普段使っている実Path>
  --conversation-scope-id <あなたが普段使っている実Scope ID>" 相当。
  Host／Port等、他に普段付けているFlagがあればそのまま付ける）
```

次のErrorが出た場合だけ、本手順の対象である（Migration不要な場合はErrorが出ず、いつもどおり起動する）。

```text
error [invalid_configuration]: The conversation store uses an older schema and requires an
explicit, opted-in migration before it can start. Re-run with the migration opt-in enabled
to upgrade it in place.
```

## 2. Backup（ユーザー自身が実施、必須）

Migration実行前に、`<あなたのruntime_data_root>`Directory全体を、そのまま別の場所へCopyする（Finder上のDrag & Copy、または`cp -R`等、ユーザーの使い慣れた方法でよい）。Claude側はこのBackup取得を代行しない。

**Backup完了を確認してから次へ進む。**

## 3. Exact Migration Command

普段どおりのCommandに、**`--conversation-persistence-migrate`という1個のFlagだけを追加**して、1回だけ起動する。

```text
（普段どおりのCommand）+ --conversation-persistence-migrate
```

他のFlag・値は一切変更しない。このFlagは今回の1回限りの起動にだけ付け、Migration完了後は付けない（付けたままでも副作用はないが、通常は不要）。

起動すると、追加のユーザー操作なしに次が自動実行される。

1. 既存DBの`0600`権限付きCheckpoint（変更前DBの完全Copy）を`<runtime_data_root>/recovery/checkpoints/<scope_key>/conversations/`へ作成し、SHA-512で内容を記録する。
2. Staging DBへ`turn_citations`Table追加＋`storage_schema_version`を`sqlite-2`へ更新する。
3. 全Record再検証後、`fsync`＋`os.replace`による原子的Cutoverを行う。
4. Migration Marker（`completed`）を記録する。

途中でProcessが異常終了した場合、旧DBは変更されないか、次回起動時に`MIGRATION_INCOMPLETE`として検出されFail-closedで停止する（第5節参照）。

## 4. 成功判定

- サーバーが通常どおり起動し、Chat Listと各Conversationの内容が全て表示される。
- 以後の起動では`--conversation-persistence-migrate`は不要（既に`sqlite-2`のため）。普段どおりのCommand（Flag追加前のもの）へ戻してよい。

## 5. Rollback（Exact、新しい破壊的CLIを追加せず、既存手段だけを使う）

### 5.1 第一手段：ユーザー自身のBackup復元（推奨、最も確実）

1. サーバーを停止する（`Ctrl+C`）。
2. 現在の`<runtime_data_root>`を別名でRename（削除しない）。
3. 第2節で取得したBackupを、元の`<runtime_data_root>`の場所へCopyし直す。
4. `--conversation-persistence-migrate`を付けずに、普段どおりのCommandで起動する。Migration前の状態に戻っていることを確認する。
5. 問題なければ、Rename済みの現在Directory（手順2）を削除してよい（ユーザー自身の判断・実行）。

### 5.2 第二手段：Migrationが作成したCheckpointからの手動復元（Backupを取り忘れた場合）

Migration自体が、変更前DBの完全Copyを自動的にCheckpointとして保存している（第3節手順1）。Backupを取り忘れていても、この内部Checkpointから復元できる。

1. サーバーを停止する。
2. `<runtime_data_root>/persistent/<scope_key>/conversations/`の`<scope_key>`（実際のFolder名としてFinder等でそのまま見える）を確認する。
3. 同じ`<scope_key>`を使う`<runtime_data_root>/recovery/checkpoints/<scope_key>/conversations/`Directoryを開く。今回が初めてのMigrationであれば、`.sqlite3`File（Checkpoint）は1個だけ存在する。
4. 現在の`<runtime_data_root>/persistent/<scope_key>/conversations/conversations.sqlite3`を別名でRename（削除しない）。
5. 手順3のCheckpoint Fileを、`conversations.sqlite3`という名前で`persistent/<scope_key>/conversations/`へCopyする。
6. `--conversation-persistence-migrate`を付けずに起動し、Migration前の状態に戻っていることを確認する。

### 5.3 技術的注記（実装状況の正直な開示）

現在の実装（`SQLiteConversationMaintenance.rollback()`）は、Migration実行直後に返る`MigrationReceipt`オブジェクトを使った自動Rollback経路を内部に持つが、この`MigrationReceipt`を後から参照できる形でFileへ保存する機能は、本Rework時点では未実装である（本FinalReworkのAllowed Mutation Scope外のため、今回は追加していない）。したがって現時点でのRollbackは、上記5.1または5.2の**手動File操作**が正本の手順であり、両方とも新しいCLI・新しいCode変更を必要としない。

将来、Migration実行結果（Checkpoint IDを含む）をユーザーが参照しやすい形で記録する改善は、別Workとして検討候補になり得る（本文書はその実装を主張しない）。

## 6. Status

```text
Current Point            : P2E-CODEX-006 CLOSED
Files Created／Modified   : 本Fileのみ（新規作成）
Validation                : 手順は既存の`_run_explicit_migration()`実装（P2E-CODEX-001）および
                            既存`SQLiteMigrationEngine`のCheckpoint／Cutover契約（Phase 2-B以来）と
                            整合していることをCode Reviewで確認済み。実Mac環境での実行はユーザー自身が
                            行うため、Claude側の自動Testでは検証していない。
Open Current Blocker      : NONE
Controller-owned Next Work: NONE
Deferred Evidence         : MigrationReceipt永続化によるRollback自動化は将来検討候補（第5.3節）
Exact Next Route          : Final Rework Completion Handoffへ集約
```
