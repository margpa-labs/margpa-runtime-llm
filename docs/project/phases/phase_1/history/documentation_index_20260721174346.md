# MARGPA Runtime LLM Documentation Index

- 文書ID: `documentation_index`
- 状態: `current`
- 作成日時: `2026-07-21 17:43:46 JST`
- 更新日時: `2026-07-21 17:43:46 JST`
- Snapshot: `20260721174346`
- 作成担当: 設計者役担当Task
- 正本言語: 日本語
- supersedes: `documentation_index_20260721172916.md`

## 1. Current Position

```text
Public Author／Research Name           : Nazuna Research
Phase 1-G                              : Accepted
Phase 1-H Requirements／Architecture   : Accepted
Phase 1-H Implementation               : Waiting User Authorization
Phase 1-F Lightning Native             : Deferred／Not Run
Phase 1-ex                              : Accepted Reservation／Not Started
Phase 10 Original R&D Systems           : EASA／DLAGSA／OCILNS
Initial GitHub Publication              : Deferred until Phase 1-ex completion
Git                                     : Not Initialized
```

## 2. Snapshot Resolution

変更のないCurrent Setは[documentation_index_20260721172916.md](documentation_index_20260721172916.md)から継承する。

本SnapshotはPhase 1-H Summary Mode／UI Languageの正本要件、Architecture、Accepted ADR、実装担当Handoff、Roadmapを追加する。

Phase 1-G Accepted結果、Phase 1-ex予約、EASA／DLAGSA／OCILNS予約、公開名義、Append-only規則は継続する。

## 3. Added Documents

| 状態 | 文書 | 役割 |
|---|---|---|
| accepted | [Phase 1-H Requirements](requirements/phase_1h_summary_mode_and_ui_language_requirements_20260721174346.md) | Summary Mode／UI Language正本要件 |
| accepted | [Phase 1-H Architecture](architecture/phase_1h_summary_mode_and_ui_language_architecture_20260721174346.md) | Pipeline／SSE／Cancel／i18n設計 |
| accepted | [ADR-0020](adr/adr_0020_phase_1h_summary_pipeline_and_ui_language_separation_20260721174346.md) | SummaryとUI Language分離判断 |
| waiting | [Implementer Handoff](handoffs/implementer_handoff_phase_1h_summary_mode_and_ui_language_20260721174346.md) | ユーザー承認後の実装範囲 |
| current | [Implementation Roadmap](architecture/implementation_roadmap_20260721174346.md) | Phase 1-H以後の順序 |

## 4. Phase 1-H Decisions

### Summary Mode

- OFF／ON、Default OFF
- ONは同じMain Modelによる逐次2段生成
- Normal max 2048、Summary max 1024
- Summary Thinking disabled
- Original Canonical Finalだけを要約対象にする
- Original／Summary／Presentedを分離する
- Error／Empty／Context／LengthはWarning付きOriginal Fallback
- CancelはFallbackせずCancelled
- Application Config Schemaを3へ更新する
- Deployment Profileは変更しない

### UI Language

- 右上の日本語／English Switch
- Default日本語
- Response Language `ja／en／auto`と完全分離
- Browser-only Translation Dictionary
- UI LanguageだけをNamespaced Local Storageへ保存
- Model Output／Thinkingを翻訳しない
- 新規Dependencyなし

## 5. Preserved Phase 1-G Boundaries

- Browser-owned Ephemeral Conversation
- One Process／One Worker／One Model Instance
- Process-wide Non-blocking Generation Gate
- Producer Thread上のNative Cancel／Close
- Disconnect／Backpressure／ShutdownのCooperative Cancel
- Model Load once／Close once
- Preview Basic Auth／Non-loopback Fail Closed
- Plain Text Rendering／No External CDN
- Terminal Event Exactly Once

## 6. Phase 1-H Acceptance Direction

```text
Design Complete
  → User authorizes implementation
  → Implementer Status
  → Designer Review + New Index
  → User Mac Test
  → Batch Lightning Upload／Validation
```

## 7. Deferred State

- Phase 1-H Source／Config／UIは未変更。
- Lightning Full Upload／Model Transferは未実行。
- Phase 1完了宣言／Backupは未実施。
- Phase 1-exは未着手。
- Git／GitHub公開は未実施。
- Phase 10 Original R&D統合は将来予約のまま。

## 8. Authorization Boundary

本IndexはPhase 1-H設計完了を記録する。Phase 1-H実装、Lightning操作、Upload、Backup、Phase 1-ex、Git、GitHub公開を自動許可しない。

## 9. Append-Only

既存文書を変更せず、Phase 1-H設計文書と新Indexを追加した。新しいTimestampの本Indexを最新とする。
