# MARGPA Runtime LLM 実装Roadmap

- 文書ID: `implementation_roadmap`
- 状態: `current`
- 作成日時: `2026-07-21 17:43:46 JST`
- 更新日時: `2026-07-21 17:43:46 JST`
- Snapshot: `20260721174346`
- 作成担当: 設計者役担当Task
- 正本言語: 日本語
- Phase 1-H Requirements: [phase_1h_summary_mode_and_ui_language_requirements_20260721174346.md](../requirements/phase_1h_summary_mode_and_ui_language_requirements_20260721174346.md)
- Phase 1-H Architecture: [phase_1h_summary_mode_and_ui_language_architecture_20260721174346.md](phase_1h_summary_mode_and_ui_language_architecture_20260721174346.md)
- Phase 1-ex Requirements: [phase_1_ex_complete_operating_model_and_documentation_requirements_20260721155020.md](../requirements/phase_1_ex_complete_operating_model_and_documentation_requirements_20260721155020.md)
- supersedes: `implementation_roadmap_20260721162242.md`

## 1. Current State

```text
Phase 1-A～1-G Repository／Mac        : Accepted
Phase 1-F Lightning Native           : Deferred／Not Run
Phase 1-H Requirements／Architecture : Accepted／Implementation Waiting Authorization
Phase 1 Cross-environment Final      : Waiting
Phase 1 User Acceptance／Backup      : Waiting
Phase 1-ex                           : Accepted Reservation／Not Started
Initial GitHub Publication           : Deferred until Phase 1-ex completion
Phase 10 External R&D Integration    : Accepted Future Reservation
```

## 2. Phase 1 Remaining Sequence

```text
User authorizes Phase 1-H Implementation
  → Summary Mode／UI Language実装
  → Implementer Status
  → Designer Review
  → User Mac Acceptance
  → Batch Lightning Upload／Native／Web Gate
  → Cross-environment Final Review
  → User Manual Finalization
  → Designer Phase 1 Completion／Next Phase Ready Declaration
  → User Final Acceptance
  → Phase 1 Backup
  → Phase 1-ex
```

## 3. Phase 1-H Fixed Scope

### Summary Mode

```text
OFF／ON
Default OFF
Normal Generation max 2048
Summary Generation max 1024
Summary Thinking disabled
Same Main Model Sequential Reuse
Original／Summary Artifact Separation
Failure／Empty／Context／Length → Original Fallback
Cancel → No Fallback／Cancelled
```

### UI Language

```text
Top-right 日本語／English
Default 日本語
Browser-only Preference
Response Language ja／en／autoとは独立
localStorageはUI Languageだけ
External i18n Dependencyなし
```

## 4. Batch Lightning Gate

Phase 1-HをMacでAccepted後、Phase 1-F～1-HをまとめてLightningへUploadする。

- Python 3.12.11
- CUDA／Tesla T4 Profile
- CPU Profile
- Project-local uv 0.11.29
- Dependency／llama.cpp Build
- CLI／Web／Access Control
- Summary OFF／ON
- UI Language ja／en
- Cancel／Shutdown

Upload時間を抑えるため、Phase 1-H以前に小刻みなFull Uploadを行わない。

## 5. Phase 1-ex

- Role／Authority再編
- Git移行
- Docs Directory Migration
- Stable Canonical Docs 5件
- Project Continuity Master
- Lossless Phase Compilation
- README／LICENSE／CITATION／NOTICE／Public Docs
- Public Identity／Privacy／License／Access
- Backup／Commit／Tag／GitHub対応
- Phase 10 Original R&Dを公開RoadmapとArchitectureへ記載

## 6. Phase 2以降

- Conversation Persistence／History／Resume
- Audit／Definition Infrastructure
- Main Runtime Governance
- Guardrail／Judge／Repair／Observability
- RAG
- Agent／Tool／Memory
- Experiment／Research Platform
- Cloud Scale／Multi Model／Multi GD

正式番号と境界はPhase 1公開後に再確認する。

## 7. Phase 10 Reservation

EASA、DLAGSA、OCILNSをOptional／Core非依存、個別OFF／ON、疎結合Portとして将来統合する予約は継続する。詳細は前RoadmapおよびPhase 10 Catalogから継承する。

## 8. Immediate Next Action

Phase 1-ex、Lightning Full Upload、Phase 10へ移らず、ユーザー承認後にPhase 1-H実装を開始する。

## 9. Authorization Boundary

本RoadmapはPhase 1-H設計完了後の順序を記録する。Phase 1-H実装、Lightning操作、Backup、Phase 1-ex、Git、GitHub公開を自動許可しない。
