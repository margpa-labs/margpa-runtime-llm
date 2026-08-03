# MARGPA Runtime LLM Documentation Index

- 文書ID: `documentation_index`
- 状態: `current`
- 作成日時: `2026-07-21 01:06:21 JST`
- 更新日時: `2026-07-21 01:06:21 JST`
- Snapshot: `20260721010621`
- 作成担当: 設計者役担当Task
- 正本言語: 日本語
- supersedes: `documentation_index_20260721010200.md`

## 1. Current Position

```text
Current Design Role                    : 設計者役／Unchanged
Phase 1-F Repository Follow-up         : Accepted
Phase 1-F Lightning Preflight          : Authorized／Ready for Execution
Phase 1-F Full Upload                  : Not Authorized
Phase 1-F Lightning CUDA／CPU Gate     : Not Run
generation.max_new_tokens              : 2048／Applied
Phase 1-G Concept                      : User Accepted／Canonical Docs Not Created
Phase 1 Completion／Backup             : Waiting
Phase 1-ex                             : Accepted Reservation／Not Started
Git                                    : Not Initialized
Initial GitHub Publication             : Deferred until Phase 1-ex completion
```

## 2. Snapshot Resolution

変更のないCurrent Setは[documentation_index_20260721010200.md](documentation_index_20260721010200.md)から継承する。本Snapshotでは、Phase 1-F Lightning Read-only Preflight専用Handoffを追加する。

## 3. Replaced Documents

| 状態 | 旧文書 | Current文書 |
|---|---|---|
| historical | [documentation_index_20260721010200.md](documentation_index_20260721010200.md) | 本文書 |

## 4. Added Documents

| 状態 | 文書 | 役割 |
|---|---|---|
| accepted_ready_for_execution | [実装担当向けPhase 1-F Lightning Read-only Preflight Handoff](handoffs/implementer_handoff_phase_1f_lightning_read_only_preflight_20260721010621.md) | 小型Preflightの外部実行Scope、合否、Evidence、禁止事項 |

## 5. Preflight Scope

Lightning Targetへ先に配置するのは次の1ファイルだけである。

```text
scripts/setup/preflight_lightning_ai_studio.sh
```

```text
Allowed
  ├─ Script 1ファイル配置
  ├─ Help確認
  ├─ GPU Read-only Preflight
  ├─ CPU Candidate Read-only Preflight
  └─ Implementer Status作成

Not Allowed Yet
  ├─ Project Full Upload
  ├─ Model Upload
  ├─ Dependency Install／Sync
  ├─ Native Build
  ├─ Environment変更
  └─ CUDA／CPU Native Acceptance
```

## 6. Immediate Next Gate

```text
Lightning Read-only Preflight実行
  → implementer_status_phase_1f_lightning_read_only_preflight_*
  → Designer Preflight Review
  → Full Upload可否判定
```

Preflightが失敗した場合、その場でEnvironment修復を行わず、Evidenceを記録してReviewへ戻す。

## 7. Deferred Items

- Full Upload、Python Dependency Sync、CUDA Build／Reuse、Model配置はPreflight Review後に判断する。
- Thinking表示Label変更はPhase 1-Gで扱う。
- Phase 1 Completion、Backup、Phase 1-ex、Git、GitHub公開は未着手である。

## 8. Authorization Boundary

本IndexとHandoffは、Lightning Read-only Preflight Script 1ファイルの配置と実行だけを許可する。Full Upload、Model Transfer、Dependency Install、Native Build、Source変更、Phase 1-G実装、Backup、Git、GitHub公開は許可しない。

## 9. Append-Only

既存Docsを編集せず、新TimestampのIndexとして追加した。
