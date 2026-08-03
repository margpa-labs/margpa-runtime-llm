# Documentation Legacy Root Retirement Notification — External Docs

```yaml
event_id: documentation_legacy_root_retirement_notification_external_docs
phase: phase_1_ex
status: acknowledged
created_at: 2026-07-26 16:14:11 JST
sender: 設計統括者役
recipient: 対外Docs役
```

## Notification

旧`docs/` Rootのカテゴリ別重複配置は、全原文をPhase HistoryへSHA-512一致で保全した後に退役した。

今後は次だけを参照・使用する。

```text
docs/project/current/
docs/project/shared/
docs/project/phases/<phase>/
docs/public/
```

旧Pathへ書き込まず、旧Pathの存在も前提にしない。

対外Docs Statusは次へ新規Eventとして作成する。

```text
docs/project/phases/<active_phase>/history/handoffs/external_docs_status_*
```

## Acknowledgement

対外Docs役から、新しいDocs構造だけを参照・使用し、旧Pathの存在を前提にせず、旧Pathへ書き込まない旨の受領確認を得た。
