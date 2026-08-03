# MARGPA Runtime LLM Documentation Index

- 文書ID: `documentation_index`
- 状態: `current`
- 作成日時: `2026-07-20 23:10:36 JST`
- 更新日時: `2026-07-20 23:10:36 JST`
- Snapshot: `20260720231036`
- 作成担当: 設計者役担当Task
- 正本言語: 日本語
- supersedes: `documentation_index_20260720222402.md`

## 1. Current Position

```text
Current Design Role           : 設計者役／Unchanged
Phase 1-F                     : Review／Lightning Native Verification Pending
Phase 1 Completion／Backup    : Waiting
Phase 1-ex                    : Accepted Reservation／Not Started
Git                           : Not Initialized
Docs Directory               : Current Structure／Unchanged
Initial GitHub Publication    : Deferred until Phase 1-ex completion
```

## 2. Snapshot Resolution

変更のないCurrent Setは[documentation_index_20260720222402.md](documentation_index_20260720222402.md)から継承する。本Snapshotの置換／追加を下表に示す。

## 3. Replaced Documents

| 状態 | 旧文書 | Current文書 |
|---|---|---|
| historical | [model_strategy_20260718174637.md](architecture/model_strategy_20260718174637.md) | [model_strategy_20260720231036.md](architecture/model_strategy_20260720231036.md) |
| historical | [phase_1_ex_operations_reorganization_requirements_20260720222402.md](requirements/phase_1_ex_operations_reorganization_requirements_20260720222402.md) | [phase_1_ex_operations_reorganization_requirements_20260720231036.md](requirements/phase_1_ex_operations_reorganization_requirements_20260720231036.md) |
| historical | [common_project_handoff_20260720222402.md](handoffs/common_project_handoff_20260720222402.md) | [common_project_handoff_20260720231036.md](handoffs/common_project_handoff_20260720231036.md) |
| historical | [documentation_index_20260720222402.md](documentation_index_20260720222402.md) | 本文書 |

## 4. Added Documents

| 状態 | 文書 | 役割 |
|---|---|---|
| accepted | [ADR-0016](adr/adr_0016_canonical_model_and_deployment_artifact_separation_20260720231036.md) | Canonical ModelとDeployment Artifact分離 |
| accepted_reservation | [ADR-0017](adr/adr_0017_phase_1_ex_operating_model_and_documentation_transition_20260720231036.md) | Phase 1-ex Role／Git／Docs Transition |
| accepted_reservation | [Lossless Compilation Requirements](requirements/lossless_phase_document_compilation_requirements_20260720231036.md) | Source本文を変更しないPhase統合 |
| accepted_reservation | [Public Docs Architecture](architecture/public_documentation_and_phase_compilation_architecture_20260720231036.md) | README／LICENSE／日本語Public Docs／Phase文書 |

## 5. Model Current Decision

```text
Guard Local／Mac   : DevQuasar Q8_0を維持
Guard Canonical    : Qwen公式通常Model
Judge Local／Mac   : bartowski Q5_K_Mを維持
Judge Canonical    : AtlaAI公式通常Model
Official Download  : Deferred
Selene Japanese    : Unverified／Experimental
```

## 6. Phase 1-ex Accepted Reservations

- 現在は設計者役を維持し、Phase 1-exで設計統括者役へ変更
- Phase別設計者役と設計統括者役の分離
- 4役のDocs／Git／Review Authority再整理
- Git導入とDocs運用再定義
- Docs Directory Migrationと完了後通知
- Phase単位Lossless Compilation
- Phase完了時のPublic Docs作成・更新
- 初回GitHub公開はPhase 1-ex完了後

## 7. Public File Reservation

```text
README.md
LICENSE
docs/public/overview_ja.md
docs/public/concept_ja.md
docs/public/roadmap_ja.md
docs/public/phases/phase_<id>_summary_ja.md
```

全Docsは日本語を基本とし、README末尾だけEnglish Abstractを追加する。LICENSEは公式英語原文を許容する。

## 8. Lossless Integrity

運用、共通ルール、Handoff等をPhase単位で統合する際、要約、意訳、再解釈、重複削除、矛盾解消を禁止する。Sourceと再抽出PayloadのSHA-512／Byte Size一致を完了条件とする。

## 9. Immediate Next Gate

```text
Phase 1-F Independent Review
  → Lightning CUDA／CPU Native Verification
  → Current User Manual／User Acceptance
  → Phase 1 Completion／Backup
  → Phase 1-ex Detailed Definition／Execution
  → Initial GitHub Publication
```

## 10. Authorization Boundary

本IndexはModel Download、Role変更、Git操作、Directory変更、Docs統合、Public Docs生成、Task通知、Lightning操作、Backup、GitHub公開を許可しない。

## 11. Append-Only

既存Docsを編集せず、新Timestampの後継文書として追加した。
