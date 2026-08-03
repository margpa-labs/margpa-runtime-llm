# MARGPA Runtime LLM Documentation Index

- 文書ID: `documentation_index`
- 状態: `current`
- 作成日時: `2026-07-19 19:51:34 JST`
- 更新日時: `2026-07-19 19:51:34 JST`
- Snapshot: `20260719195134`
- 作成担当: 設計者役担当Task
- 正本言語: 日本語
- supersedes: `documentation_index_20260719171836.md`

## 1. Current Position

```text
Phase 1 User Acceptance Test  : In Progress
Acceptance Follow-up          : Proposed／Implementation authorization waiting
Phase 1 Completion            : Not declared
Phase 1 Backup                : Not triggered
Phase 2 Implementation        : Not authorized
```

## 2. Current Snapshot Resolution

本Indexは、変更のないCurrent Setを次の完全Indexから継承する。

- [documentation_index_20260719171836.md](documentation_index_20260719171836.md)

次の系列だけを本Snapshotで置換または追加する。この継承元と下表を組み合わせることでCurrent Setを再現できる。

## 3. Replaced Current Documents

| 状態 | 旧文書 | Current文書 |
|---|---|---|
| historical | [known_issues_and_observations_20260719171836.md](operations/known_issues_and_observations_20260719171836.md) | [known_issues_and_observations_20260719195134.md](operations/known_issues_and_observations_20260719195134.md) |
| historical | [common_project_handoff_20260719171836.md](handoffs/common_project_handoff_20260719171836.md) | [common_project_handoff_20260719195134.md](handoffs/common_project_handoff_20260719195134.md) |
| historical | [documentation_index_20260719171836.md](documentation_index_20260719171836.md) | [documentation_index_20260719195134.md](documentation_index_20260719195134.md) |

## 4. Added Current Documents

| 状態 | 文書 | 役割 |
|---|---|---|
| current_supplement | [phase_1_user_acceptance_findings_20260719195134.md](user_manual/phase_1_user_acceptance_findings_20260719195134.md) | CLI仮引数、Thinking、Cross-platformのUser Test補足 |
| proposed_waiting_implementation_authorization | [phase_1_acceptance_follow_up_requirements_20260719195134.md](requirements/phase_1_acceptance_follow_up_requirements_20260719195134.md) | Help／Token上限Warning要件 |
| waiting_user_implementation_authorization | [implementer_handoff_phase_1_acceptance_follow_up_20260719195134.md](handoffs/implementer_handoff_phase_1_acceptance_follow_up_20260719195134.md) | 実装担当向けFollow-up |

## 5. Current User Manual Set

- 基本Manual: [phase_1_macos_user_manual_20260719171836.md](user_manual/phase_1_macos_user_manual_20260719171836.md)
- Current補足: [phase_1_user_acceptance_findings_20260719195134.md](user_manual/phase_1_user_acceptance_findings_20260719195134.md)

Follow-up後の再受入時に、必要に応じて両文書を統合した新Timestampの後継Manualを作成する。既存Manualは変更しない。

## 6. Known Issues State

```text
MARGPA-OBS-0001 : accepted_deferred
MARGPA-OBS-0002 : open_required
MARGPA-OBS-0003 : accepted_deferred
MARGPA-OBS-0004 : accepted_deferred
MARGPA-OBS-0005 : accepted_deferred
```

## 7. Next Gate

```text
Follow-up Disposition
  → 必要なら実装／Test／Review
  → User Acceptance再確認
  → Designer Completion Declaration
  → Phase 1 Backup
```

## 8. Authorization Boundary

本Indexと関連Docsは、Source／Config／Tests変更、外部Service操作、Phase 1完了、Backup、Phase 2実装を許可しない。

## 9. Append-Only

- 本Snapshotで既存Docsを編集、削除、改名、移動していない。
- 新しいTimestampのIndexをCurrent Entry Pointとする。
- 前Snapshotの完全Indexと本Indexの明示差分でCurrent Setを再現する。
