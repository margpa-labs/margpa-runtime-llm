# MARGPA Runtime LLM 実装Roadmap

- 文書ID: `implementation_roadmap`
- 状態: `current`
- 作成日時: `2026-07-21 16:22:42 JST`
- 更新日時: `2026-07-21 16:22:42 JST`
- Snapshot: `20260721162242`
- 作成担当: 設計者役担当Task
- 正本言語: 日本語
- Phase 1-ex Requirements: [phase_1_ex_complete_operating_model_and_documentation_requirements_20260721155020.md](../requirements/phase_1_ex_complete_operating_model_and_documentation_requirements_20260721155020.md)
- External R&D Requirements: [phase_1_ex_external_r_and_d_publication_and_integration_requirements_20260721162242.md](../requirements/phase_1_ex_external_r_and_d_publication_and_integration_requirements_20260721162242.md)
- Phase 10 Catalog: [phase_10_original_r_and_d_system_catalog_20260721162242.md](../governance/phase_10_original_r_and_d_system_catalog_20260721162242.md)
- supersedes: `implementation_roadmap_20260721155020.md`

## 1. Current State

```text
Phase 1-A～1-F Repository／Mac                : Accepted
Phase 1-F Lightning Native                   : Deferred／Not Run
Phase 1-G Cross-thread Follow-up             : Implementer Report Received／Review Pending
Phase 1-H Summary Mode                       : Waiting Phase 1-G Acceptance
Phase 1 Cross-environment Final Review       : Waiting
Phase 1 User Acceptance／Backup              : Waiting
Phase 1-ex Operations Reorganization        : Accepted Reservation／Not Started
Initial GitHub Publication                  : Deferred until Phase 1-ex completion
Phase 10 External Original R&D Integration  : Accepted Future Reservation
```

## 2. Phase 1 Remaining Sequence

```text
Phase 1-G Final Review
  → Phase 1-H Summary Mode
  → Mac Acceptance
  → Batch Lightning Upload／Native／Web Gate
  → Cross-environment Final Review
  → User Manual Finalization
  → Designer Phase 1 Completion Declaration
  → User Final Acceptance
  → Phase 1 Backup
  → Phase 1-ex
```

## 3. Phase 1-H

```text
要約モード OFF／ON
Default OFF
Normal Generation max 2048
Summary Generation max 1024
Summary Thinking disabled
Same Main Model Sequential Reuse
Original Final Answer Preserve
Summary Failure時OriginalへWarning付きFallback
```

## 4. Batch Lightning Gate

Phase 1-G／1-HのMac Accepted後に、Source、Model、Dependency、CUDA／CPU、CLI、Web、Access、Summaryを一括検証する。

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
- Phase 10の3 Original R&Dを公開RoadmapとArchitectureへ記載

## 6. Phase 2以降の大分類

- Conversation Persistence／History／Resume
- Audit／Definition Infrastructure
- Main Runtime Governance
- Guardrail／Judge／Repair／Observability
- RAG
- Agent／Tool／Memory
- Experiment／Research Platform
- Cloud Scale／Multi Model／Multi GD

正式番号と境界はPhase 1公開後に再確認できる。

## 7. Phase 10：External Original R&D Integration

MARGPA Runtime LLMが一通り完成した後、別Project／別Taskの3 Systemを疎結合統合する。

### 7.1 EASA

```text
Exception Aware Safety Architecture
例外認識型安全統治機構
Research Area: AI Safety Governance
```

内部安全傾向、周辺安全制御、入力文脈、生成過程等の相互作用を対象とし、例外を含む複合的な安全挙動を統治する独立R&D Architecture。

### 7.2 DLAGSA

```text
Distributed LEA Agentic Governance & Safety Architecture
分散証跡型例外認識エージェント統治安全機構
Research Area: Multi-Agent Governance,
               Distributed Accountability,
               and Safety Assurance
```

複数の判断・実行・検証主体間における責任、委譲、例外、改竄耐性付き証跡、全体整合および異常時の安全側制御を扱う独立R&D Architecture。

### 7.3 OCILNS

```text
Open Cognitive Interaction Ledger Network System
認知対話証跡台帳網
Research Area: Cognitive Interaction Provenance,
               Verifiable AI Systems,
               and Distributed Auditability
```

人、AI、Tool、外部System間の認知的対話出来事を、検証、参照、継承、監査できる改竄耐性付き証跡として扱い、長期、分岐、多Model、多Thread環境で再接続可能性を維持する独立R&D System。

### 7.4 Common Integration Principle

```text
EASA   : OFF／ON
DLAGSA : OFF／ON
OCILNS : OFF／ON
Default: All OFF
```

- EASA／DLAGSAはGeneric Governance Provider Port
- OCILNSはGeneric Evidence Ledger Port
- Optional／Core非依存
- 3 Systemなしで本体動作
- Algorithm／核心は現在非掲載

## 8. Immediate Next Action

Phase 1-exまたはPhase 10へ移らず、Phase 1-G Cross-thread Follow-upの設計者Final Reviewを行う。

## 9. Authorization Boundary

本Roadmapは順序と将来予約を更新する。Phase 1-ex、Phase 1-H、Lightning Upload、Phase 10実装、Git、公開を自動許可しない。
