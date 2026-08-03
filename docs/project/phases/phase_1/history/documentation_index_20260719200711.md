# MARGPA Runtime LLM Documentation Index

- 文書ID: `documentation_index`
- 状態: `current`
- 作成日時: `2026-07-19 20:07:11 JST`
- 更新日時: `2026-07-19 20:07:11 JST`
- Snapshot: `20260719200711`
- 作成担当: 設計者役担当Task
- 正本言語: 日本語
- supersedes: `documentation_index_20260719195134.md`

## 1. Current Position

```text
Phase 1 User Acceptance              : In Progress
Phase 1 Follow-up                    : Waiting Implementation Authorization
Phase 1 Completion／Backup           : Not Triggered
Lightning Dual Profile Design        : Accepted Planning Only
Lightning Implementation／Validation : Waiting Future Phase Authorization
```

## 2. Snapshot Resolution

変更のないCurrent Setは次のIndexから継承する。

- [documentation_index_20260719195134.md](documentation_index_20260719195134.md)

本Snapshotでは下表の系列を置換または追加する。継承元と本差分によりCurrent Setを再現する。

## 3. Replaced Documents

| 状態 | 旧文書 | Current文書 |
|---|---|---|
| historical | [lightning_ai_studio_cross_environment_architecture_20260719112304.md](architecture/lightning_ai_studio_cross_environment_architecture_20260719112304.md) | [lightning_ai_studio_cross_environment_architecture_20260719200711.md](architecture/lightning_ai_studio_cross_environment_architecture_20260719200711.md) |
| historical | [common_project_handoff_20260719195134.md](handoffs/common_project_handoff_20260719195134.md) | [common_project_handoff_20260719200711.md](handoffs/common_project_handoff_20260719200711.md) |
| historical | [documentation_index_20260719195134.md](documentation_index_20260719195134.md) | [documentation_index_20260719200711.md](documentation_index_20260719200711.md) |

## 4. Added Documents

| 状態 | 文書 | 役割 |
|---|---|---|
| accepted_planning_only | [lightning_ai_studio_dual_runtime_profile_requirements_20260719200711.md](requirements/lightning_ai_studio_dual_runtime_profile_requirements_20260719200711.md) | CUDA／CPU Profile、Container／Detection要件 |
| waiting_future_phase_authorization | [implementer_handoff_lightning_ai_studio_dual_runtime_profiles_20260719200711.md](handoffs/implementer_handoff_lightning_ai_studio_dual_runtime_profiles_20260719200711.md) | 実装担当向け将来Handoff |

## 5. Current Profile Plan

```text
Mac Current : config/profiles/local_macos_arm64.toml
Lightning   : config/profiles/lightning_linux_x86_64_cuda.toml  # planned
Lightning   : config/profiles/lightning_linux_x86_64_cpu.toml   # planned
```

Lightning Profile Fileはまだ作成していない。Container／CUDA DetectionとNative Buildが同時に必要であり、未検証TOMLだけをPhase 1 Snapshotへ混入させない。

## 6. Next Gates

```text
Phase 1:
  Acceptance Follow-up Disposition
    → 必要なら実装／Review／再Test
    → User Acceptance
    → Completion／Backup

Lightning:
  Future Phase Authorization
    → Container／CUDA Detection
    → CUDA／CPU Profile + Setup
    → Native Verification
    → Review／Index
```

## 7. Authorization Boundary

本Indexと設計Docsは、Source／Config／Tests変更、Lightning外部操作、Package Install、Model Download／Upload、GPU利用を許可しない。

## 8. Append-Only

- 既存Docsを編集、削除、改名、移動していない。
- 新しいTimestampの本IndexをCurrent Entry Pointとする。
