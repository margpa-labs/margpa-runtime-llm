# MARGPA Runtime LLM 文書索引

- 文書ID: `documentation_index`
- 状態: `current`
- 作成日時: `2026-07-18 19:34:35 JST`
- 更新日時: `2026-07-18 19:34:35 JST`
- 対象: `docs/`全体
- 正本言語: 日本語
- Snapshot: `20260718193435`
- supersedes: `documentation_index_20260718174637.md`

## 1. この索引の役割

この文書は、現在有効なRequirements、Architecture、Governance、ADR、Handoffと、過去文書との世代関係を示す。

同じ主題のDocumentが複数存在する場合、File名末尾のTimestampが最も新しいDocumentを最新とする。

`documentation_index`もTimestampが最も新しいものを最新Indexとする。

## 2. 最初に読む文書

1. [documentation_rules_20260718193435.md](requirements/documentation_rules_20260718193435.md)
2. [common_project_handoff_20260718193435.md](handoffs/common_project_handoff_20260718193435.md)
3. [project_requirements_20260718193435.md](requirements/project_requirements_20260718193435.md)

## 3. Requirements

| 状態 | 文書 | 役割 |
|---|---|---|
| current | [documentation_rules_20260718193435.md](requirements/documentation_rules_20260718193435.md) | File名、Append-Only、Timestamp、最新判定、読み取り専用原則 |
| current | [project_requirements_20260718193435.md](requirements/project_requirements_20260718193435.md) | Project目的、Scope、優先順位、Hardware、制約、現在の決定 |

## 4. Architecture

| 状態 | 文書 | 役割 |
|---|---|---|
| current | [system_architecture_20260718193435.md](architecture/system_architecture_20260718193435.md) | Modular Monolith、Port／Adapter、Deployment、UI、Storage |
| current | [project_directory_structure_20260718192110.md](architecture/project_directory_structure_20260718192110.md) | 機能別Module＋Port／Adapter、Phase別Directory、依存方向 |
| current | [model_strategy_20260718174637.md](architecture/model_strategy_20260718174637.md) | Model選定、Quantization、Storage、Registry、GitHub方針 |
| current | [future_extensions_20260718174637.md](architecture/future_extensions_20260718174637.md) | RAG、Agent、Image、Cloud、複数Model／GD |
| current | [implementation_roadmap_20260718193435.md](architecture/implementation_roadmap_20260718193435.md) | Phase、現在地点、次の設計、未決事項 |

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
| current | [common_project_handoff_20260718193435.md](handoffs/common_project_handoff_20260718193435.md) | 全担当Task |
| current | [designer_handoff_20260718193435.md](handoffs/designer_handoff_20260718193435.md) | 設計者役 |
| waiting | [implementer_handoff_20260718193435.md](handoffs/implementer_handoff_20260718193435.md) | 将来の実装者役 |
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

Project全体のDirectory構成も決定済みで、Phase 1最小Directoryだけ作成済み。

次の設計議題はLocal Backend、Python Version、Dependency管理、Config、Model Registry、Phase 1 Acceptance Criteria。

実装はまだ解禁されていない。

## 10. Snapshot構成

現在のDocument Setには次の18文書が含まれる。

```text
Requirements : 2
Architecture : 5
Governance   : 2
ADR          : 4
Handoffs     : 4
Index        : 1
Total        : 18
```

## 11. Historical Document Set

Append-Only移行前に更新されていた8文書について、`20260718174637`版を作成当初の内容へ復元し、現在内容を`20260718193435`版として保存した。

旧文書自体には後継情報を追記していない。

| 状態 | 旧文書 | 最新文書 |
|---|---|---|
| historical | [documentation_rules_20260718174637.md](requirements/documentation_rules_20260718174637.md) | [documentation_rules_20260718193435.md](requirements/documentation_rules_20260718193435.md) |
| historical | [project_requirements_20260718174637.md](requirements/project_requirements_20260718174637.md) | [project_requirements_20260718193435.md](requirements/project_requirements_20260718193435.md) |
| historical | [system_architecture_20260718174637.md](architecture/system_architecture_20260718174637.md) | [system_architecture_20260718193435.md](architecture/system_architecture_20260718193435.md) |
| historical | [implementation_roadmap_20260718174637.md](architecture/implementation_roadmap_20260718174637.md) | [implementation_roadmap_20260718193435.md](architecture/implementation_roadmap_20260718193435.md) |
| historical | [common_project_handoff_20260718174637.md](handoffs/common_project_handoff_20260718174637.md) | [common_project_handoff_20260718193435.md](handoffs/common_project_handoff_20260718193435.md) |
| historical | [designer_handoff_20260718174637.md](handoffs/designer_handoff_20260718174637.md) | [designer_handoff_20260718193435.md](handoffs/designer_handoff_20260718193435.md) |
| historical | [implementer_handoff_20260718174637.md](handoffs/implementer_handoff_20260718174637.md) | [implementer_handoff_20260718193435.md](handoffs/implementer_handoff_20260718193435.md) |
| historical | [documentation_index_20260718174637.md](documentation_index_20260718174637.md) | [documentation_index_20260718193435.md](documentation_index_20260718193435.md) |

## 12. Repository内の文書総数

```text
Current Document Set : 18
Historical Documents : 8
Total Stored Files    : 26
```

Current Document Setは現在の正本構成数であり、Historical Documentsを含まない。

## 13. Append-Only判定規則

- 新しいTimestampのDocumentを最新とする
- 新しいTimestampのIndexを最新Indexとする
- 旧文書を上書きしない
- 旧文書を削除・改名・移動しない
- 後継文書の`supersedes`で旧文書を示す
- 旧文書の状態は最新Index側で示す
