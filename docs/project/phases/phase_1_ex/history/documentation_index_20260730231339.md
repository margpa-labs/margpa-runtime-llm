# Phase 1-ex Documentation Index Snapshot

```yaml
document_id: phase_1_ex_documentation_index_snapshot
snapshot: 20260730231339
state_at: 2026-07-30 23:13:39 JST
status: current_snapshot
snapshot_of:
  - ../phase_index_ja.md
  - operations/lightning_public_demo_and_basic_preview_manual_acceptance_20260730231339.md
  - handoffs/designer_review_phase_1_ex_lightning_public_demo_manual_acceptance_20260730231339.md
supersedes: documentation_index_20260730170710.md
source: lightning_public_demo_and_basic_preview_manual_acceptance
```

本Snapshotは[2026-07-30 17:07:10版](documentation_index_20260730170710.md)までの全状態を継承する。

Phase Index Stableは今回変更していない。Lightning手動Acceptance Evidence、設計統括者Reviewおよび本IndexをAppend-only Eventとして追加した。

## Added Event Artifacts

- [Lightning Public Demo／Basic Preview Manual Acceptance](operations/lightning_public_demo_and_basic_preview_manual_acceptance_20260730231339.md)
- [設計統括者Review：Lightning Public Demo Manual Acceptance](handoffs/designer_review_phase_1_ex_lightning_public_demo_manual_acceptance_20260730231339.md)

## Acceptance Decision

```text
Public Demo Repository:
  ACCEPTED

Lightning Public Demo:
  ACCEPTED

Anonymous Access:
  ACCEPTED

Basic Preview:
  ACCEPTED／PRESERVED

Basic Authentication:
  ACCEPTED

LLM Web Runtime:
  ACCEPTED

Public／Basic Separation:
  ACCEPTED

Cold Start:
  OBSERVED／approximately 2 minutes

Rollback Drill:
  NOT_RUN／NON_BLOCKING
```

## Procedure Correction

初回Target Testでは20件が同じ`invalid_profile_contract`で失敗した。

原因は、Public用`MARGPA_WEB_ACCESS_PROFILE`をTest前に親TerminalへExportしたManual Procedureの順序不備である。

Project SourceまたはLightning Runtimeの不具合ではない。

今後は次を固定する。

```text
Target Test:
  Public Profile Exportより前に実行

or

Pytest:
  env -u MARGPA_WEB_ACCESS_PROFILE
```

## External Evidence Boundary

```text
External Operation:
  Performed by user

Public URL:
  Not recorded

Credential:
  Not recorded

Account Identifier:
  Not recorded

Prompt／Response Body:
  Not recorded
```

## Remaining Gate

次回GitHub／公開物同期前に、前Reviewで検出したPublication Hygiene Findingを処理する。

```text
P1:
  最新実装Statusの実ユーザー由来絶対Path 1件

P2:
  Project Rootおよびdocs/の.DS_Store 2件
```

本Eventでは無断修正・削除していない。

## Next

```text
Mac限定簡易Documentation RAG:
  DESIGN NEXT

External Environment Adapter Hook:
  DESIGN NEXT

Public Demo Documentation RAG:
  DENIED／DO NOT LOAD
```

## Integrity

```text
Previous Documentation Index:
51f64119122328e57ea081a49203fd1dffa1ce5a47858b91d32ce3ec710702040beb77a88a9cbd5c3228558291c02251dbb7c905b994854cb5851fe3dc404c90

Phase Index Stable／Unchanged:
67fff441677412c4e5e2aec2f951b597247ad5ee797497ba564d913eef58dec211237bbdb2a5d6adb5facfa829f662cd423a3a5023ea7c9d164458ba40c0478e

Manual Acceptance Evidence:
7dbaaa350481707984c6f31cc9aa3270971dec7950069499d543889c81d48e48cd493669da355f38cefbe8affdc2b0563219737bfe6f93e14baddf94bec242ce

Designer Review:
f1346f69f477f48bffaf8c468567dde53a809f9469b227e0710ebf2f1aa32218a3e383e38c59682a6a3464c9391dc00fa9940e321ea5331e5cc93fe4850431b3
```

## Validation Scope

- Manual Evidence、Reviewおよび本Indexを新規追加した。
- 既存Docsを上書きしていない。
- Phase Index Stableを変更していない。
- Source、Config、Script、TestおよびModelを変更していない。
- Public URL、Credentialまたは個人識別情報を保存していない。
- Project Root外へ触れていない。
- Lightning、GitおよびGitHubを変更していない。
