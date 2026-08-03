# MARGPA Runtime LLM 共通プロジェクト引き継ぎ

```yaml
document_state: current
created_at: 2026-07-21 16:22:42 JST
supersedes: common_project_handoff_20260721155020.md
project_root: margpa-runtime-llm/
public_identity: Nazuna Research
current_design_role: 設計者役
future_design_role: 設計統括者役（Phase 1-exで変更予定）
```

## 1. Current State

```text
Phase 1-G Cross-thread Follow-up : Implementer Report Received／Review Pending
Phase 1-H                       : Waiting Phase 1-G Acceptance
Phase 1 Completion／Backup      : Waiting
Phase 1-ex                      : Accepted Reservation／Not Started
Phase 10 Original R&D           : Accepted Future Reservation
Git                             : Not Initialized
```

## 2. Phase 1-ex Stable Docs

```text
docs/requirements_specification_ja.md
docs/system_architecture_ja.md
docs/technology_selection_ja.md
docs/basic_design_ja.md
docs/runtime_governance_specification_ja.md
docs/project_continuity/project_continuity_master_ja.md
```

File名は英語、本文は日本語。Project Continuity Masterを含め公開可能とする。

## 3. Official Original R&D Names

### EASA

```text
Exception Aware Safety Architecture
例外認識型安全統治機構
Research Area: AI Safety Governance
```

### DLAGSA

```text
Distributed LEA Agentic Governance & Safety Architecture
分散証跡型例外認識エージェント統治安全機構
Research Area: Multi-Agent Governance,
               Distributed Accountability,
               and Safety Assurance
```

### OCILNS

```text
Open Cognitive Interaction Ledger Network System
認知対話証跡台帳網
Research Area: Cognitive Interaction Provenance,
               Verifiable AI Systems,
               and Distributed Auditability
```

## 4. OCILNS Position

人、AI、Tool、外部Systemの認知的対話出来事を、検証、参照、継承、監査可能な改竄耐性付き証跡単位として扱う。

長期、分岐、多Model、多Threadでも、入力、出力、順序、時刻、Model情報、判断根拠、未解決事項、継承対象、改変検知情報を再接続可能な状態で維持することを目的とする。LLM応答精度の直接向上を目的としない。

内部使用技術はMARGPA Docsへ記載しない。

## 5. Phase 10 Integration

```text
EASA／DLAGSA
  → Generic External Governance Provider Port

OCILNS
  → Generic Evidence Ledger Port
```

3 Systemは別Project／別Taskで開発し、本体完成後にAdapterで統合する。

```text
EASA   : Config OFF／ON
DLAGSA : Config OFF／ON
OCILNS : Config OFF／ON
Default: All OFF
```

3 SystemなしでMARGPA Runtime LLM本体は完全動作する。

## 6. Public Disclosure

- Roadmap：正式名称、研究領域、1から2行概要
- System Architecture：接続位置とON／OFF
- Project Continuity Master：作業概念をやや詳しく記載
- Algorithm、具体的改竄耐性方式、核心：現在非掲載

構想の存在と方向性を先に公開する。

## 7. Current Entry Points

- [Latest Documentation Index](../documentation_index_20260721162242.md)
- [External R&D Requirements](../requirements/phase_1_ex_external_r_and_d_publication_and_integration_requirements_20260721162242.md)
- [Original R&D Catalog](../governance/phase_10_original_r_and_d_system_catalog_20260721162242.md)
- [Integration Architecture](../architecture/phase_10_external_r_and_d_integration_architecture_20260721162242.md)
- [ADR-0019](../adr/adr_0019_phase_10_original_r_and_d_public_names_and_switches_20260721162242.md)
- [Current Roadmap](../architecture/implementation_roadmap_20260721162242.md)

## 8. Immediate Next Gate

Phase 1-ex／Phase 10へ移らず、Phase 1-G Cross-thread Follow-upをReviewする。

## 9. Authorization Boundary

本Handoffは、Phase 1-ex開始、Config変更、External System統合、Git操作、公開を許可しない。
