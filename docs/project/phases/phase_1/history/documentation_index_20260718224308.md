# MARGPA Runtime LLM 文書索引

- 文書ID: `documentation_index`
- 状態: `current`
- 作成日時: `2026-07-18 22:43:08 JST`
- 更新日時: `2026-07-18 22:43:08 JST`
- 対象: `docs/`全体
- 正本言語: 日本語
- Snapshot: `20260718224308`
- supersedes: `documentation_index_20260718223203.md`

## 1. この索引の役割

この文書は、現在有効なRequirements、Architecture、Governance、ADR、Handoff、Status、Reviewと、過去文書との世代関係を示す。

同じ主題のDocumentが複数存在する場合、File名末尾のTimestampが最も新しいDocumentを最新とする。

`documentation_index`もTimestampが最も新しいものを最新Indexとする。

## 2. 最初に読む文書

1. [documentation_rules_20260718193435.md](requirements/documentation_rules_20260718193435.md)
2. [common_project_handoff_20260718193435.md](handoffs/common_project_handoff_20260718193435.md)
3. [project_requirements_20260718193435.md](requirements/project_requirements_20260718193435.md)
4. [phase_1b_model_runtime_contract_20260718223203.md](architecture/phase_1b_model_runtime_contract_20260718223203.md)
5. [adr_0006_model_runtime_port_and_configuration_20260718224308.md](adr/adr_0006_model_runtime_port_and_configuration_20260718224308.md)
6. [designer_handoff_phase_1b_model_runtime_20260718224308.md](handoffs/designer_handoff_phase_1b_model_runtime_20260718224308.md)

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
| current | [python_environment_and_dependency_strategy_20260718201744.md](architecture/python_environment_and_dependency_strategy_20260718201744.md) | Python、Venv、uv、Package Version、Dependency Group、Fallback |
| approved | [phase_1b_model_runtime_contract_20260718223203.md](architecture/phase_1b_model_runtime_contract_20260718223203.md) | Phase 1-B Contract、Port、Capability、Error、Registry、Config、CLI、Test |
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
| accepted | [adr_0005_python_environment_and_dependency_management_20260718201744.md](adr/adr_0005_python_environment_and_dependency_management_20260718201744.md) | Python 3.13.14、`.venv`、uv、Phase単位Install、3.12 Fallback |
| accepted | [adr_0006_model_runtime_port_and_configuration_20260718224308.md](adr/adr_0006_model_runtime_port_and_configuration_20260718224308.md) | Model Port、Lifecycle、Capability、TOML Registry／Profile、Phase 1-B CLI |

## 7. Handoffs／Status／Review

| 状態 | 文書 | 対象 |
|---|---|---|
| current | [common_project_handoff_20260718193435.md](handoffs/common_project_handoff_20260718193435.md) | 全担当Task |
| current | [designer_handoff_20260718193435.md](handoffs/designer_handoff_20260718193435.md) | 設計者役 |
| waiting | [implementer_handoff_20260718193435.md](handoffs/implementer_handoff_20260718193435.md) | 実装者役・General |
| waiting | [designer_python_environment_handoff_20260718201744.md](handoffs/designer_python_environment_handoff_20260718201744.md) | Python環境設計から実装者役への専用引き継ぎ |
| reviewed | [implementer_status_phase_1_environment_reproducibility_follow_up_20260718214958.md](handoffs/implementer_status_phase_1_environment_reproducibility_follow_up_20260718214958.md) | Phase 1-A再現性Follow-up実装結果 |
| accepted | [designer_review_phase_1_environment_reproducibility_follow_up_20260718221255.md](handoffs/designer_review_phase_1_environment_reproducibility_follow_up_20260718221255.md) | Phase 1-A Follow-up受入、Required項目完了、非ブロッカー記録 |
| ready | [designer_handoff_phase_1b_model_runtime_20260718224308.md](handoffs/designer_handoff_phase_1b_model_runtime_20260718224308.md) | Phase 1-B実装担当。実装許可／Write Scope確認待ち |
| waiting | [public_documentation_handoff_20260718174637.md](handoffs/public_documentation_handoff_20260718174637.md) | 将来の対外Docs作成者役 |

## 8. 担当別Reading Order

### 設計者

1. Common Handoff
2. Project Requirements
3. Latest Designer Review
4. Phase 1-B Model Runtime Contract
5. ADR-0006 Accepted
6. Phase 1-B Implementer Handoff
7. System Architecture
8. Project Directory Structure
9. Model Strategy
10. Python Environment Strategy
11. Runtime Governance
12. Roadmap

### 実装者

1. Latest Documentation Index
2. Phase 1-B Implementer Handoff
3. Phase 1-B Model Runtime Contract
4. ADR-0006 Accepted
5. Common Handoff
6. Latest Designer Review
7. General Implementer Handoff
8. Latest Implementer Status
9. Python Environment Strategy
10. Project Directory Structure
11. Model Strategy
12. System Architecture

### 対外Docs作成者

1. Common Handoff
2. Public Documentation Handoff
3. Project Requirements
4. Phase 1-B Model Runtime Contract
5. ADR-0006 Accepted
6. Latest Designer Review
7. Model Strategy
8. Runtime Governance
9. Audit／Security

## 9. 現在地点

```text
Phase 1-A
Environment Setup／Qwen3-4B Metal Smoke／Environment再現性を完了

Phase 1-B
Model Runtime Contract詳細設計 : Approved
ADR-0006                       : Accepted
Implementer Handoff            : Ready
Source Implementation          : Not Started／Not Authorized
```

Phase 1-B Implementation Gate：

1. ユーザーによるPhase 1-B実装開始許可
2. `config/`作成・変更許可
3. 必要な場合の`pyproject.toml`変更許可
4. Model SHA-512計算許可
5. 実Model／Metal Integration Test実行許可

Locked Decision：

- Thinking Default OFF、設定で切替可能
- Initial Context 4,096、上限固定ではない
- 一問一答＋Streaming＋Stop CLI
- Multi-TurnはPhase 2
- Model Port Instanceは同時に1 Modelを所有
- Phase 1-Bの同時Generation数は1
- Capability不足は明示Error
- Streaming Stopは協調Cancel
- Registry／Deployment Profile／Generation Profileを分離
- TOML＋Pydantic v2
- llama.cpp固有処理はAdapterへ隔離
- Performance値はConfig／Profileで交換可能

Known Non-blocking Item：

- 通常Setupでも`llama-cpp-python`を毎回Native再Buildする
- Qwen3 Soft Switchでは空Thinking Tagが残る場合がある
- Distribution Revision／Commitを推測で埋めない
- Raw Output／Display Output分離は後続設計で確定する
- `.DS_Store`再生成は別のRepository Hygiene事項

## 10. Review／Index作成運用

正式Reviewを完了した場合は、原則として同じ作業単位で次を新規作成する。

1. 新TimestampのReview文書
2. Review対象、Review結果、旧文書との世代関係を反映した新Timestampの`documentation_index`

旧Review、旧Status、旧Indexは上書きしない。

## 11. Current Snapshot構成

現在の正本Document Setには次の26文書が含まれる。

```text
Requirements : 2
Architecture : 7
Governance   : 2
ADR          : 6
Handoffs     : 8
Index        : 1
Total        : 26
```

## 12. Historical Document Set

| 状態 | 旧文書 | 最新文書 |
|---|---|---|
| historical | [documentation_rules_20260718174637.md](requirements/documentation_rules_20260718174637.md) | [documentation_rules_20260718193435.md](requirements/documentation_rules_20260718193435.md) |
| historical | [project_requirements_20260718174637.md](requirements/project_requirements_20260718174637.md) | [project_requirements_20260718193435.md](requirements/project_requirements_20260718193435.md) |
| historical | [system_architecture_20260718174637.md](architecture/system_architecture_20260718174637.md) | [system_architecture_20260718193435.md](architecture/system_architecture_20260718193435.md) |
| historical | [implementation_roadmap_20260718174637.md](architecture/implementation_roadmap_20260718174637.md) | [implementation_roadmap_20260718193435.md](architecture/implementation_roadmap_20260718193435.md) |
| historical | [common_project_handoff_20260718174637.md](handoffs/common_project_handoff_20260718174637.md) | [common_project_handoff_20260718193435.md](handoffs/common_project_handoff_20260718193435.md) |
| historical | [designer_handoff_20260718174637.md](handoffs/designer_handoff_20260718174637.md) | [designer_handoff_20260718193435.md](handoffs/designer_handoff_20260718193435.md) |
| historical | [implementer_handoff_20260718174637.md](handoffs/implementer_handoff_20260718174637.md) | [implementer_handoff_20260718193435.md](handoffs/implementer_handoff_20260718193435.md) |
| historical | [implementer_status_phase_1_environment_and_metal_smoke_20260718210342.md](handoffs/implementer_status_phase_1_environment_and_metal_smoke_20260718210342.md) | [implementer_status_phase_1_environment_reproducibility_follow_up_20260718214958.md](handoffs/implementer_status_phase_1_environment_reproducibility_follow_up_20260718214958.md) |
| historical | [designer_review_phase_1_environment_and_metal_smoke_20260718212502.md](handoffs/designer_review_phase_1_environment_and_metal_smoke_20260718212502.md) | [designer_review_phase_1_environment_reproducibility_follow_up_20260718221255.md](handoffs/designer_review_phase_1_environment_reproducibility_follow_up_20260718221255.md) |
| historical | [adr_0006_model_runtime_port_and_configuration_20260718223203.md](adr/adr_0006_model_runtime_port_and_configuration_20260718223203.md) | [adr_0006_model_runtime_port_and_configuration_20260718224308.md](adr/adr_0006_model_runtime_port_and_configuration_20260718224308.md) |
| historical | [documentation_index_20260718174637.md](documentation_index_20260718174637.md) | [documentation_index_20260718193435.md](documentation_index_20260718193435.md) |
| historical | [documentation_index_20260718193435.md](documentation_index_20260718193435.md) | [documentation_index_20260718201744.md](documentation_index_20260718201744.md) |
| historical | [documentation_index_20260718201744.md](documentation_index_20260718201744.md) | [documentation_index_20260718212502.md](documentation_index_20260718212502.md) |
| historical | [documentation_index_20260718212502.md](documentation_index_20260718212502.md) | [documentation_index_20260718221255.md](documentation_index_20260718221255.md) |
| historical | [documentation_index_20260718221255.md](documentation_index_20260718221255.md) | [documentation_index_20260718223203.md](documentation_index_20260718223203.md) |
| historical | [documentation_index_20260718223203.md](documentation_index_20260718223203.md) | [documentation_index_20260718224308.md](documentation_index_20260718224308.md) |

## 13. Repository内の文書総数

```text
Current Document Set : 26
Historical Documents : 16
Total Stored Files    : 42
```

Current Document Setは現在の正本構成数であり、Historical Documentsを含まない。

## 14. Append-Only判定規則

- 新しいTimestampのDocumentを最新とする
- 新しいTimestampのIndexを最新Indexとする
- 旧文書を上書きしない
- 旧文書を削除・改名・移動しない
- 後継文書の`supersedes`で旧文書を示す
- 旧文書の状態は最新Index側で示す

