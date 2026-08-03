# MARGPA Runtime LLM 文書索引

- 文書ID: `documentation_index`
- 状態: `current`
- 作成日時: `2026-07-18 17:46:37 JST`
- 更新日時: `2026-07-18 17:46:37 JST`
- 対象: `docs/`全体
- 正本言語: 日本語
- Snapshot: `20260718174637`

## 1. この索引の役割

この文書は、現在有効なRequirements、Architecture、Governance、ADR、Handoffを示す。

同じ主題のDocumentが複数存在する場合、この索引で`current`として掲載されたDocumentを正本として扱う。

## 2. 最初に読む文書

1. [documentation_rules_20260718174637.md](requirements/documentation_rules_20260718174637.md)
2. [common_project_handoff_20260718174637.md](handoffs/common_project_handoff_20260718174637.md)
3. [project_requirements_20260718174637.md](requirements/project_requirements_20260718174637.md)

## 3. Requirements

| 状態 | 文書 | 役割 |
|---|---|---|
| current | [documentation_rules_20260718174637.md](requirements/documentation_rules_20260718174637.md) | File名、Timestamp、日本語、更新、正本の共通ルール |
| current | [project_requirements_20260718174637.md](requirements/project_requirements_20260718174637.md) | Project目的、Scope、優先順位、Hardware、制約 |

## 4. Architecture

| 状態 | 文書 | 役割 |
|---|---|---|
| current | [system_architecture_20260718174637.md](architecture/system_architecture_20260718174637.md) | Modular Monolith、Port／Adapter、Deployment、UI、Storage |
| current | [model_strategy_20260718174637.md](architecture/model_strategy_20260718174637.md) | Model選定、Quantization、Storage、Registry、GitHub方針 |
| current | [future_extensions_20260718174637.md](architecture/future_extensions_20260718174637.md) | RAG、Agent、Image、Cloud、複数Model／GD |
| current | [implementation_roadmap_20260718174637.md](architecture/implementation_roadmap_20260718174637.md) | Phase、現在地点、次の設計、未決事項 |

## 5. Governance

| 状態 | 文書 | 役割 |
|---|---|---|
| current | [runtime_governance_20260718174637.md](governance/runtime_governance_20260718174637.md) | ARGD、DAGD、Compiler、Profile、将来GD |
| current | [audit_evaluation_security_20260718174637.md](governance/audit_evaluation_security_20260718174637.md) | Audit、SHA-512、説明、Evaluation、Guard、Judge、Permission |

## 6. ADR

| 状態 | 文書 | Decision |
|---|---|---|
| accepted | [adr_0001_initial_model_selection_20260718174637.md](adr/adr_0001_initial_model_selection_20260718174637.md) | Main、Guard、JudgeとQuantization |
| accepted | [adr_0002_external_model_storage_20260718174637.md](adr/adr_0002_external_model_storage_20260718174637.md) | External Model RootとPOSIX Symbolic Link |
| accepted | [adr_0003_japanese_documentation_and_handoffs_20260718174637.md](adr/adr_0003_japanese_documentation_and_handoffs_20260718174637.md) | 日本語Docs、Timestamp File、担当別Handoff |
| accepted | [adr_0004_modular_monolith_20260718174637.md](adr/adr_0004_modular_monolith_20260718174637.md) | Initial ArchitectureとしてModular Monolithを採用 |

## 7. Handoffs

| 状態 | 文書 | 対象 |
|---|---|---|
| current | [common_project_handoff_20260718174637.md](handoffs/common_project_handoff_20260718174637.md) | 全担当Task |
| current | [designer_handoff_20260718174637.md](handoffs/designer_handoff_20260718174637.md) | 設計者役 |
| waiting | [implementer_handoff_20260718174637.md](handoffs/implementer_handoff_20260718174637.md) | 将来の実装者役 |
| waiting | [public_documentation_handoff_20260718174637.md](handoffs/public_documentation_handoff_20260718174637.md) | 将来の対外Docs作成者役 |

## 8. 担当別Reading Order

### 設計者

1. Common Handoff
2. Project Requirements
3. System Architecture
4. Model Strategy
5. Runtime Governance
6. Roadmap
7. ADR

### 実装者

1. Common Handoff
2. Implementer Handoff
3. Project Requirements
4. System Architecture
5. Model Strategy
6. Runtime Governance
7. Audit／Security
8. Roadmap
9. ADR

### 対外Docs作成者

1. Common Handoff
2. Public Documentation Handoff
3. Project Requirements
4. Model Strategy
5. Runtime Governance
6. Audit／Security
7. ADR

## 9. 現在地点

```text
Phase 0
要件定義・技術選定・Architecture設計
```

Model選定とModel Storageは基本決定済み。

次の設計議題はProject全体のDirectory構成。

実装はまだ解禁されていない。

## 10. Snapshot構成

この初期Snapshotには次の17文書が含まれる。

```text
Requirements : 2
Architecture : 4
Governance   : 2
ADR          : 4
Handoffs     : 4
Index        : 1
Total        : 17
```
