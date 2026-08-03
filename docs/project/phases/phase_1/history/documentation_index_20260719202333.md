# MARGPA Runtime LLM Documentation Index

- 文書ID: `documentation_index`
- 状態: `current`
- 作成日時: `2026-07-19 20:23:33 JST`
- 更新日時: `2026-07-19 20:23:33 JST`
- Snapshot: `20260719202333`
- 作成担当: 設計者役担当Task
- 正本言語: 日本語
- supersedes: `documentation_index_20260719200711.md`

## 1. Current Position

```text
Top-level Phase 1     : Reopened for Follow-up and Phase 1-F
Phase 1-F             : Accepted／Implementation Pending
User Acceptance       : Waiting
Backup                : Not Triggered
Publication           : Planned／Not Authorized
```

## 2. Snapshot Resolution

変更のないCurrent Setは[documentation_index_20260719200711.md](documentation_index_20260719200711.md)から継承する。本Snapshotの置換／追加を下表に示す。

## 3. Replaced Documents

| 状態 | 旧文書 | Current文書 |
|---|---|---|
| historical | [lightning_ai_studio_dual_runtime_profile_requirements_20260719200711.md](requirements/lightning_ai_studio_dual_runtime_profile_requirements_20260719200711.md) | [phase_1f_lightning_cross_environment_runtime_requirements_20260719202333.md](requirements/phase_1f_lightning_cross_environment_runtime_requirements_20260719202333.md) |
| historical | [lightning_ai_studio_cross_environment_architecture_20260719200711.md](architecture/lightning_ai_studio_cross_environment_architecture_20260719200711.md) | [lightning_ai_studio_cross_environment_architecture_20260719202333.md](architecture/lightning_ai_studio_cross_environment_architecture_20260719202333.md) |
| historical | [implementation_roadmap_20260719171836.md](architecture/implementation_roadmap_20260719171836.md) | [implementation_roadmap_20260719202333.md](architecture/implementation_roadmap_20260719202333.md) |
| historical | [implementer_handoff_lightning_ai_studio_dual_runtime_profiles_20260719200711.md](handoffs/implementer_handoff_lightning_ai_studio_dual_runtime_profiles_20260719200711.md) | [implementer_handoff_phase_1f_lightning_cross_environment_runtime_20260719202333.md](handoffs/implementer_handoff_phase_1f_lightning_cross_environment_runtime_20260719202333.md) |
| historical | [common_project_handoff_20260719200711.md](handoffs/common_project_handoff_20260719200711.md) | [common_project_handoff_20260719202333.md](handoffs/common_project_handoff_20260719202333.md) |
| historical | [documentation_index_20260719200711.md](documentation_index_20260719200711.md) | [documentation_index_20260719202333.md](documentation_index_20260719202333.md) |

## 4. Added Documents

| 状態 | 文書 | 役割 |
|---|---|---|
| accepted | [adr_0015_phase_1f_lightning_and_python_312_support_20260719202333.md](adr/adr_0015_phase_1f_lightning_and_python_312_support_20260719202333.md) | Lightning前倒し、Python 3.12／3.13 Support |

## 5. Current Phase 1 Work

- [Acceptance Follow-up Handoff](handoffs/implementer_handoff_phase_1_acceptance_follow_up_20260719195134.md)
- [Phase 1-F Handoff](handoffs/implementer_handoff_phase_1f_lightning_cross_environment_runtime_20260719202333.md)

## 6. Current Python／Platform Matrix

```text
macOS arm64 Native／Metal       : Python 3.13.14／Native Verified before new changes
Linux x86_64 Container／CUDA    : Python 3.12.11／Implementation Pending
Linux x86_64 Container／CPU     : Python 3.12.11／Preferred／Conditional
```

## 7. Next Gate

```text
Implementer Start
  → Shared Compatibility Changes
  → Mac Regression
  → Lightning CUDA Native Verification
  → CPU Disposition
  → Review／Manual／User Acceptance
  → Phase 1 Completion／Backup
  → Publication Preparation
```

## 8. Authorization Boundary

本Indexと設計Docsは、Source／Config／Lock変更、Lightning操作、Backup、Git／GitHub公開を許可しない。実装担当へのUser Start Instructionを待つ。

## 9. Append-Only

- 既存Docsを編集、削除、改名、移動していない。
- 新しいTimestampの本IndexをCurrent Entry Pointとする。
