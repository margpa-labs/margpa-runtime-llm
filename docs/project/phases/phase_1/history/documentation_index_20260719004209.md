# MARGPA Runtime LLM 文書索引

- 文書ID: `documentation_index`
- 状態: `current`
- 作成日時: `2026-07-19 00:42:09 JST`
- 更新日時: `2026-07-19 00:42:09 JST`
- 対象: `docs/`全体
- 正本言語: 日本語
- Snapshot: `20260719004209`
- supersedes: `documentation_index_20260719002104.md`

## 1. この索引の役割

この文書は、現在有効なRequirements、Architecture、Governance、ADR、Handoff、Status、Review、User Manualと、過去文書との世代関係を示す最新Indexである。

同じ主題のDocumentが複数存在する場合、File名末尾のTimestampが最も新しいDocumentを最新とする。

`documentation_index`もTimestampが最も新しいものを最新Indexとする。

## 2. 最初に読む文書

1. [documentation_rules_20260718193435.md](requirements/documentation_rules_20260718193435.md)
2. [common_project_handoff_20260718193435.md](handoffs/common_project_handoff_20260718193435.md)
3. [project_requirements_20260718193435.md](requirements/project_requirements_20260718193435.md)
4. [phase_1_macos_user_manual_20260719004209.md](user_manual/phase_1_macos_user_manual_20260719004209.md)
5. [designer_review_phase_1b_model_runtime_final_20260719001604.md](handoffs/designer_review_phase_1b_model_runtime_final_20260719001604.md)
6. [implementer_status_phase_1b_model_runtime_test_follow_up_20260719001341.md](handoffs/implementer_status_phase_1b_model_runtime_test_follow_up_20260719001341.md)
7. [phase_1b_model_runtime_contract_20260718223203.md](architecture/phase_1b_model_runtime_contract_20260718223203.md)
8. [adr_0006_model_runtime_port_and_configuration_20260718224308.md](adr/adr_0006_model_runtime_port_and_configuration_20260718224308.md)

## 3. Current Requirements

| 状態 | 文書 | 役割 |
|---|---|---|
| current | [documentation_rules_20260718193435.md](requirements/documentation_rules_20260718193435.md) | File名、Append-Only、Timestamp、最新判定、読み取り専用原則 |
| current | [project_requirements_20260718193435.md](requirements/project_requirements_20260718193435.md) | Project目的、Scope、優先順位、Hardware、制約、現在の決定 |

## 4. Current Architecture

| 状態 | 文書 | 役割 |
|---|---|---|
| current | [system_architecture_20260718193435.md](architecture/system_architecture_20260718193435.md) | Modular Monolith、Port／Adapter、Deployment、UI、Storage |
| current | [project_directory_structure_20260718192110.md](architecture/project_directory_structure_20260718192110.md) | 機能別Module＋Port／Adapter、Phase別Directory、依存方向 |
| current | [model_strategy_20260718174637.md](architecture/model_strategy_20260718174637.md) | Model選定、Quantization、Storage、Registry、GitHub方針 |
| current | [python_environment_and_dependency_strategy_20260718201744.md](architecture/python_environment_and_dependency_strategy_20260718201744.md) | Python、Venv、uv、Package Version、Dependency Group、Fallback |
| implemented | [phase_1b_model_runtime_contract_20260718223203.md](architecture/phase_1b_model_runtime_contract_20260718223203.md) | Phase 1-B Contract、Port、Capability、Error、Registry、Config、CLI、Test |
| current | [future_extensions_20260718174637.md](architecture/future_extensions_20260718174637.md) | RAG、Agent、Image、Cloud、複数Model／GD |
| current | [implementation_roadmap_20260718193435.md](architecture/implementation_roadmap_20260718193435.md) | Phase、現在地点、次の設計、未決事項 |

## 5. Current Governance

| 状態 | 文書 | 役割 |
|---|---|---|
| current | [runtime_governance_20260718174637.md](governance/runtime_governance_20260718174637.md) | ARGD、DAGD、Compiler、Profile、将来GD |
| current | [audit_evaluation_security_20260718174637.md](governance/audit_evaluation_security_20260718174637.md) | Audit、SHA-512、説明、Evaluation、Guard、Judge、Permission |

## 6. Current ADR

| 状態 | 文書 | Decision |
|---|---|---|
| accepted | [adr_0001_initial_model_selection_20260718174637.md](adr/adr_0001_initial_model_selection_20260718174637.md) | Main、Guard、JudgeとQuantization |
| accepted | [adr_0002_external_model_storage_20260718174637.md](adr/adr_0002_external_model_storage_20260718174637.md) | External Model RootとPOSIX Symbolic Link |
| accepted | [adr_0003_japanese_documentation_and_handoffs_20260718174637.md](adr/adr_0003_japanese_documentation_and_handoffs_20260718174637.md) | 日本語Docs、Timestamp File、担当別Handoff |
| accepted | [adr_0004_modular_monolith_20260718174637.md](adr/adr_0004_modular_monolith_20260718174637.md) | Initial ArchitectureとしてModular Monolithを採用 |
| accepted | [adr_0005_python_environment_and_dependency_management_20260718201744.md](adr/adr_0005_python_environment_and_dependency_management_20260718201744.md) | Python 3.13.14、`.venv`、uv、Phase単位Install、3.12 Fallback |
| accepted | [adr_0006_model_runtime_port_and_configuration_20260718224308.md](adr/adr_0006_model_runtime_port_and_configuration_20260718224308.md) | Model Port、Lifecycle、Capability、TOML Registry／Profile、Phase 1-B CLI |

## 7. Current Handoffs／Status／Review

| 状態 | 文書 | 対象 |
|---|---|---|
| current | [common_project_handoff_20260718193435.md](handoffs/common_project_handoff_20260718193435.md) | 全担当Task |
| current | [designer_handoff_20260718193435.md](handoffs/designer_handoff_20260718193435.md) | 設計者役 |
| waiting | [implementer_handoff_20260718193435.md](handoffs/implementer_handoff_20260718193435.md) | 実装者役・General |
| waiting | [designer_python_environment_handoff_20260718201744.md](handoffs/designer_python_environment_handoff_20260718201744.md) | Python環境設計から実装者役への専用引き継ぎ |
| reviewed | [implementer_status_phase_1_environment_reproducibility_follow_up_20260718214958.md](handoffs/implementer_status_phase_1_environment_reproducibility_follow_up_20260718214958.md) | Phase 1-A再現性Follow-up実装結果 |
| accepted | [designer_review_phase_1_environment_reproducibility_follow_up_20260718221255.md](handoffs/designer_review_phase_1_environment_reproducibility_follow_up_20260718221255.md) | Phase 1-A Follow-up受入 |
| implemented | [designer_handoff_phase_1b_model_runtime_20260718224308.md](handoffs/designer_handoff_phase_1b_model_runtime_20260718224308.md) | Phase 1-B実装指示の基準文書 |
| reviewed_accepted | [implementer_status_phase_1b_model_runtime_test_follow_up_20260719001341.md](handoffs/implementer_status_phase_1b_model_runtime_test_follow_up_20260719001341.md) | Test-only Follow-up完了、Phase 1-B最終Status |
| accepted_phase_1b_complete | [designer_review_phase_1b_model_runtime_final_20260719001604.md](handoffs/designer_review_phase_1b_model_runtime_final_20260719001604.md) | Phase 1-B最終受入、Required Follow-up完了 |
| waiting | [public_documentation_handoff_20260718174637.md](handoffs/public_documentation_handoff_20260718174637.md) | 将来の対外Docs作成者役 |

## 8. Current User Manual

| 状態 | 文書 | 対象 |
|---|---|---|
| current | [phase_1_macos_user_manual_20260719004209.md](user_manual/phase_1_macos_user_manual_20260719004209.md) | Mac上でのPhase 1操作、動作確認、Test、Troubleshooting |

## 9. 現在地点

```text
Phase 1-A                      : Complete
Phase 1-B                      : Complete
Phase 1 Mac User Verification : Pass
Phase 1 macOS User Manual     : Current
Phase 1-C Cross-platform Hook : Next Design Task
```

Phase 1-C候補：

- Windows x86_64 Profile
- CPU／CUDA／Vulkan等のBackend Profile
- PowerShell Setup Hook
- Cross-platform Device識別
- GPU Offload RequirementのProfile化
- OS別Path／Test境界

Phase 1-Cの実装は、新しい設計、ADR、Handoffおよびユーザー許可後に行う。

## 10. Historical Chain

直前までの完全なHistorical Chainは、次のIndexに保持されている。

- [documentation_index_20260719002104.md](documentation_index_20260719002104.md)

本Indexによる追加関係：

| 状態 | 旧文書 | 最新文書 |
|---|---|---|
| historical | [documentation_index_20260719002104.md](documentation_index_20260719002104.md) | [documentation_index_20260719004209.md](documentation_index_20260719004209.md) |

## 11. Current Snapshot構成

```text
Requirements : 2
Architecture : 7
Governance   : 2
ADR          : 6
Handoffs     : 10
User Manual  : 1
Index        : 1
Current      : 29
Historical   : 26
Total        : 55
```

## 12. Append-Only判定規則

- 新しいTimestampのDocumentを最新とする
- 新しいTimestampのIndexを最新Indexとする
- 旧文書を上書きしない
- 旧文書を削除・改名・移動しない
- 後継文書の`supersedes`で旧文書を示す
- 旧文書の状態は最新Index側で示す

