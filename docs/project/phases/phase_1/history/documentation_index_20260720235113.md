# MARGPA Runtime LLM Documentation Index

- 文書ID: `documentation_index`
- 状態: `current`
- 作成日時: `2026-07-20 23:51:13 JST`
- 更新日時: `2026-07-20 23:51:13 JST`
- Snapshot: `20260720235113`
- 作成担当: 設計者役担当Task
- 正本言語: 日本語
- supersedes: `documentation_index_20260720231036.md`

## 1. Current Position

```text
Current Design Role           : 設計者役／Unchanged
Phase 1-F Repository Review   : Changes Requested
Phase 1-F Lightning Gate      : Not Started
Phase 1-G Concept             : User Accepted／Canonical Docs Not Created
Phase 1 Completion／Backup    : Waiting
Phase 1-ex                    : Accepted Reservation／Not Started
Git                           : Not Initialized
Initial GitHub Publication    : Deferred until Phase 1-ex completion
```

## 2. Snapshot Resolution

変更のないCurrent Setは[documentation_index_20260720231036.md](documentation_index_20260720231036.md)から継承する。本SnapshotではPhase 1-F ReviewとIndexだけを追加／置換する。

## 3. Replaced Documents

| 状態 | 旧文書 | Current文書 |
|---|---|---|
| historical | [documentation_index_20260720231036.md](documentation_index_20260720231036.md) | 本文書 |

## 4. Added Documents

| 状態 | 文書 | 役割 |
|---|---|---|
| changes_requested | [Phase 1-F Lightning Cross-environment Runtime設計Review](handoffs/designer_review_phase_1f_lightning_cross_environment_runtime_20260720235113.md) | Repository実装の独立ReviewとLightning搬入前Follow-up |

## 5. Phase 1-F Review Summary

```text
Static／Default Gate       : Pass
Mac 3.13／Metal Gate      : Pass
Python 3.12 Native Gate   : Not Run
Lightning CUDA Gate       : Not Run
Lightning CPU Gate        : Not Run
High Finding              : 2
Medium Finding            : 2
Low Observation           : 1
Decision                  : Changes Requested
```

主な必須Follow-up：

- CUDA Capability／RequestとActual GPU Offload Observationの分離
- Acceptance ProbeのFail Closed化
- Response Language／Thinking PresentationのNative Check強化
- Target Lightning StudioでのVenv利用可否確認

## 6. Phase 1-G Position

ユーザーとの要件定義会話において、Phase 1-GをLightning公開用の最小Web Surfaceとして追加する方向は合意済みである。

```text
Backend       : FastAPI
Current UI    : Minimal Vanilla HTML／CSS／JavaScript
Future UI     : React等へ交換可能
Chat          : Single Ephemeral Multi-turn
Settings      : Language／Max New Tokens／Thinking
Access        : Minimal Preview Access Control
```

ただし、Phase 1-GのRequirements、Architecture、ADR、Handoffは本Snapshotでは作成しておらず、実装も許可されていない。

## 7. Immediate Next Gate

```text
Phase 1-F Implementer Follow-up
  → Phase 1-F Follow-up Review
  → Lightning Preflight／Single Upload
  → Lightning CUDA／CPU Native Verification
  → Phase 1-F Final Review
  → Phase 1-G Canonical Design／Implementation
```

Phase 1 Completion、Backup、Phase 1-ex、Git、GitHub公開は未許可／未着手である。

## 8. Authorization Boundary

本IndexはSource修正、Lightning操作、Model Download、Phase 1-G実装、Backup、Git、GitHub公開を許可しない。

## 9. Append-Only

既存Docsを編集せず、新TimestampのIndexとして追加した。
