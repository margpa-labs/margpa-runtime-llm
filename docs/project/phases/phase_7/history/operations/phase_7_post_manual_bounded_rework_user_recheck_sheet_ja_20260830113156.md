# Phase 7 Post-Manual Bounded Rework — User Recheck Sheet

```yaml
document_id: phase_7_post_manual_bounded_rework_user_recheck_sheet_20260830113156
document_type: bounded_user_manual_recheck_sheet
document_state: ready
language: ja
created_at: 2026-08-30 11:31:56 JST
authority_owner: Nazuna Research
phase: phase_7
items: 4
```

## 1. Citation Identity

1. Local Documentを登録する。
2. 固有Factを質問する。
3. Citationを確認する。

確認:

- `Local Corpus`と表示される。
- Project Docs Citationは`Project Docs`と表示される。
- Chunk IDとDocument Digestの短縮値が表示される。
- Copyで完全な値を取得できる。
- Reload後も同じ値が残る。

## 2. Update／Historical Immutability

1. 同じLocal Documentを新しい値へ更新する。
2. 同じChatで再質問する。

確認:

- 新Turnは最新値を回答する。
- 新TurnのDocument Digestが更新前と異なる。
- 更新前Turnの回答／Chunk ID／Document Digestは変化しない。

## 3. Delete／Current Freshness

1. Local Documentを削除する。
2. 同じChatで同じ質問をする。
3. 新しいChatでも同じ質問をする。

確認:

- 同じChat／新しいChatとも、削除済みの値をCurrent Factとして断定しない。
- 「現在のCorpusに根拠がない」相当へ収束する。
- 無関係なProject Docsを回答根拠のCitationとして表示しない。
- 削除前の過去Turn／過去Citationは変化しない。

## 4. Restart／Unarchive Auto-Resume

### 4.1 Restart

1. ArchiveしていないChatを残してServerを再起動する。
2. そのChatを開き、短い質問を送る。

確認:

- Sidebarに「再開」がない。
- 「再開」を押さず送信・回答できる。

### 4.2 Unarchive

1. ChatをArchiveする。
2. Archiveを解除する。
3. 短い質問を送る。

確認:

- Archive中に勝手な回答生成やSession開始がない。
- Archive解除後、「再開」を押さず送信・回答できる。

## 5. 返却形式

各項目を次で返す。

```text
1. Citation Identity: PASS / FAIL
2. Update／Historical: PASS / FAIL
3. Delete／Freshness: PASS / FAIL
4. Restart／Unarchive: PASS / FAIL

FAIL時:
  実際の表示文言
  操作順
  同じChatか新しいChatか
```
