# MARGPA Runtime LLM 文書索引

- 文書ID: `documentation_index`
- 状態: `current`
- 作成日時: `2026-07-19 04:18:47 JST`
- 更新日時: `2026-07-19 04:18:47 JST`
- 対象: `docs/`全体
- 正本言語: 日本語
- Snapshot: `20260719041847`
- supersedes: `documentation_index_20260719040237.md`

## 1. この索引の役割

この文書は現在有効なRequirements、Architecture、Governance、ADR、Handoff、Status、Review、User Manualと過去文書との世代関係を示す最新Indexである。

同一系列ではFile名末尾のTimestampが最も新しいDocumentを最新とする。

## 2. 最初に読む文書

1. [documentation_rules_20260718193435.md](requirements/documentation_rules_20260718193435.md)
2. [common_project_handoff_20260718193435.md](handoffs/common_project_handoff_20260718193435.md)
3. [project_requirements_20260718193435.md](requirements/project_requirements_20260718193435.md)
4. [implementation_roadmap_20260719041847.md](architecture/implementation_roadmap_20260719041847.md)
5. [designer_review_phase_1c_final_20260719035156.md](handoffs/designer_review_phase_1c_final_20260719035156.md)
6. [configuration_layer_requirements_20260719041847.md](requirements/configuration_layer_requirements_20260719041847.md)
7. [configuration_layer_architecture_20260719041847.md](architecture/configuration_layer_architecture_20260719041847.md)
8. [phase_1d_response_language_requirements_20260719041847.md](requirements/phase_1d_response_language_requirements_20260719041847.md)
9. [phase_1d_response_language_architecture_20260719041847.md](architecture/phase_1d_response_language_architecture_20260719041847.md)
10. [adr_0009_application_deployment_configuration_separation_20260719041847.md](adr/adr_0009_application_deployment_configuration_separation_20260719041847.md)
11. [designer_handoff_phase_1d_response_language_20260719041847.md](handoffs/designer_handoff_phase_1d_response_language_20260719041847.md)
12. [phase_1_macos_user_manual_20260719004209.md](user_manual/phase_1_macos_user_manual_20260719004209.md)

## 3. Current Requirements

| 状態 | 文書 | 役割 |
|---|---|---|
| current | [documentation_rules_20260718193435.md](requirements/documentation_rules_20260718193435.md) | Append-Only、Timestamp、最新判定、読み取り専用原則 |
| current | [project_requirements_20260718193435.md](requirements/project_requirements_20260718193435.md) | Project目的、Scope、優先順位、Hardware、制約 |
| implemented_accepted | [phase_1c_deployment_platform_acceleration_requirements_20260719013109.md](requirements/phase_1c_deployment_platform_acceleration_requirements_20260719013109.md) | Phase 1-C Requirement、全Criteria Pass |
| accepted_ready_for_implementation_authorization | [configuration_layer_requirements_20260719041847.md](requirements/configuration_layer_requirements_20260719041847.md) | Application／Model／Deployment／Platform Registry責務分離 |
| accepted_ready_for_implementation_authorization | [phase_1d_response_language_requirements_20260719041847.md](requirements/phase_1d_response_language_requirements_20260719041847.md) | Config分離、`ja／en／auto`、Composition、Acceptance |

## 4. Current Architecture

| 状態 | 文書 | 役割 |
|---|---|---|
| current | [system_architecture_20260718193435.md](architecture/system_architecture_20260718193435.md) | Modular Monolith、Port／Adapter、Deployment、UI、Storage |
| current | [project_directory_structure_20260718192110.md](architecture/project_directory_structure_20260718192110.md) | Module、Port／Adapter、依存方向 |
| current | [model_strategy_20260718174637.md](architecture/model_strategy_20260718174637.md) | Model選定、Quantization、Storage、Registry |
| current | [python_environment_and_dependency_strategy_20260718201744.md](architecture/python_environment_and_dependency_strategy_20260718201744.md) | Python、Venv、uv、Dependency、Fallback |
| implemented | [phase_1b_model_runtime_contract_20260718223203.md](architecture/phase_1b_model_runtime_contract_20260718223203.md) | Model Runtime Contract、Config、CLI、Test |
| implemented_accepted | [phase_1c_deployment_platform_acceleration_architecture_20260719013109.md](architecture/phase_1c_deployment_platform_acceleration_architecture_20260719013109.md) | Deployment／Platform／Acceleration Hook |
| accepted_ready_for_implementation_authorization | [configuration_layer_architecture_20260719041847.md](architecture/configuration_layer_architecture_20260719041847.md) | Application Config、Deployment Profile、Typed Composer |
| accepted_ready_for_implementation_authorization | [phase_1d_response_language_architecture_20260719041847.md](architecture/phase_1d_response_language_architecture_20260719041847.md) | Configuration Composition、Response Resolver、Message Composer |
| partially_refined_phase_1e_source | [response_language_and_thinking_output_policy_20260719013109.md](architecture/response_language_and_thinking_output_policy_20260719013109.md) | Thinking部分をPhase 1-E設計元として保持 |
| current | [future_extensions_20260718174637.md](architecture/future_extensions_20260718174637.md) | RAG、Agent、Image、Cloud、複数Model／GD |
| current | [implementation_roadmap_20260719041847.md](architecture/implementation_roadmap_20260719041847.md) | Phase 1-D Config分離＋Language、Phase 1-E、後続Phase |

## 5. Current Governance

| 状態 | 文書 | 役割 |
|---|---|---|
| current | [runtime_governance_20260718174637.md](governance/runtime_governance_20260718174637.md) | ARGD、DAGD、Compiler、Profile、将来GD |
| current | [audit_evaluation_security_20260718174637.md](governance/audit_evaluation_security_20260718174637.md) | Audit、SHA-512、Evaluation、Guard、Judge、Permission |

## 6. Current ADR

| 状態 | 文書 | Decision |
|---|---|---|
| accepted | [adr_0001_initial_model_selection_20260718174637.md](adr/adr_0001_initial_model_selection_20260718174637.md) | Main、Guard、JudgeとQuantization |
| accepted | [adr_0002_external_model_storage_20260718174637.md](adr/adr_0002_external_model_storage_20260718174637.md) | External Model RootとPOSIX Symbolic Link |
| accepted | [adr_0003_japanese_documentation_and_handoffs_20260718174637.md](adr/adr_0003_japanese_documentation_and_handoffs_20260718174637.md) | 日本語Docs、Timestamp、担当別Handoff |
| accepted | [adr_0004_modular_monolith_20260718174637.md](adr/adr_0004_modular_monolith_20260718174637.md) | Modular Monolith |
| accepted | [adr_0005_python_environment_and_dependency_management_20260718201744.md](adr/adr_0005_python_environment_and_dependency_management_20260718201744.md) | Python 3.13.14、`.venv`、uv、Fallback |
| accepted | [adr_0006_model_runtime_port_and_configuration_20260718224308.md](adr/adr_0006_model_runtime_port_and_configuration_20260718224308.md) | Model Port、Lifecycle、Capability、Config、CLI |
| accepted_implemented | [adr_0007_deployment_platform_acceleration_abstraction_20260719013109.md](adr/adr_0007_deployment_platform_acceleration_abstraction_20260719013109.md) | Platform Hook、Capability分離、Validation |
| accepted_amended_by_0009 | [adr_0008_response_language_policy_20260719040237.md](adr/adr_0008_response_language_policy_20260719040237.md) | `ja／en／auto`維持、Config配置をADR-0009で修正 |
| accepted | [adr_0009_application_deployment_configuration_separation_20260719041847.md](adr/adr_0009_application_deployment_configuration_separation_20260719041847.md) | `application.toml`、Deployment責務分離、Typed Composition |

## 7. Current Handoffs／Status／Review

| 状態 | 文書 | 対象 |
|---|---|---|
| current | [common_project_handoff_20260718193435.md](handoffs/common_project_handoff_20260718193435.md) | 全担当Task |
| current | [designer_handoff_20260718193435.md](handoffs/designer_handoff_20260718193435.md) | 設計者役 |
| waiting | [implementer_handoff_20260718193435.md](handoffs/implementer_handoff_20260718193435.md) | 実装者役・General |
| waiting | [designer_python_environment_handoff_20260718201744.md](handoffs/designer_python_environment_handoff_20260718201744.md) | Python環境専用Handoff |
| reviewed | [implementer_status_phase_1_environment_reproducibility_follow_up_20260718214958.md](handoffs/implementer_status_phase_1_environment_reproducibility_follow_up_20260718214958.md) | Phase 1-A再現性Follow-up |
| accepted | [designer_review_phase_1_environment_reproducibility_follow_up_20260718221255.md](handoffs/designer_review_phase_1_environment_reproducibility_follow_up_20260718221255.md) | Phase 1-A受入 |
| implemented | [designer_handoff_phase_1b_model_runtime_20260718224308.md](handoffs/designer_handoff_phase_1b_model_runtime_20260718224308.md) | Phase 1-B Handoff |
| reviewed_accepted | [implementer_status_phase_1b_model_runtime_test_follow_up_20260719001341.md](handoffs/implementer_status_phase_1b_model_runtime_test_follow_up_20260719001341.md) | Phase 1-B最終Status |
| accepted_phase_1b_complete | [designer_review_phase_1b_model_runtime_final_20260719001604.md](handoffs/designer_review_phase_1b_model_runtime_final_20260719001604.md) | Phase 1-B最終受入 |
| implemented | [designer_handoff_phase_1c_deployment_platform_acceleration_20260719013109.md](handoffs/designer_handoff_phase_1c_deployment_platform_acceleration_20260719013109.md) | Phase 1-C Handoff |
| reviewed_accepted | [implementer_status_phase_1c_platform_registry_reference_integrity_follow_up_20260719034523.md](handoffs/implementer_status_phase_1c_platform_registry_reference_integrity_follow_up_20260719034523.md) | Phase 1-C最終Status |
| accepted_phase_1c_complete | [designer_review_phase_1c_final_20260719035156.md](handoffs/designer_review_phase_1c_final_20260719035156.md) | Phase 1-C最終受入 |
| ready_for_implementation_authorization | [designer_handoff_phase_1d_response_language_20260719041847.md](handoffs/designer_handoff_phase_1d_response_language_20260719041847.md) | Phase 1-D Config／Language実装Handoff |
| waiting | [public_documentation_handoff_20260718174637.md](handoffs/public_documentation_handoff_20260718174637.md) | 対外Docs作成者役 |

## 8. Current User Manual

| 状態 | 文書 | 対象 |
|---|---|---|
| current | [phase_1_macos_user_manual_20260719004209.md](user_manual/phase_1_macos_user_manual_20260719004209.md) | Mac上でのPhase 1操作、Test、Troubleshooting |

## 9. 現在地点

```text
Phase 1-A Environment                         : Complete／Accepted
Phase 1-B Model Runtime                       : Complete／Accepted
Phase 1-C Deployment／Platform／Acceleration  : Complete／Accepted
Phase 1-D Configuration／Response Language    : Designed／Accepted／Implementation Not Authorized
Phase 1-E Thinking Presentation Policy        : Planned／Not Designed／Not Authorized
Current Native Verification                  : macOS／Apple Silicon arm64／Metal
```

Phase 1-DのSource／Config／Test実装は、ユーザーが明示的に実装開始を許可した後に行う。

## 10. Supersession Update

| 状態 | 旧文書 | 最新文書 |
|---|---|---|
| historical | [phase_1d_response_language_requirements_20260719040237.md](requirements/phase_1d_response_language_requirements_20260719040237.md) | [phase_1d_response_language_requirements_20260719041847.md](requirements/phase_1d_response_language_requirements_20260719041847.md) |
| historical | [phase_1d_response_language_architecture_20260719040237.md](architecture/phase_1d_response_language_architecture_20260719040237.md) | [phase_1d_response_language_architecture_20260719041847.md](architecture/phase_1d_response_language_architecture_20260719041847.md) |
| historical | [designer_handoff_phase_1d_response_language_20260719040237.md](handoffs/designer_handoff_phase_1d_response_language_20260719040237.md) | [designer_handoff_phase_1d_response_language_20260719041847.md](handoffs/designer_handoff_phase_1d_response_language_20260719041847.md) |
| historical | [implementation_roadmap_20260719040237.md](architecture/implementation_roadmap_20260719040237.md) | [implementation_roadmap_20260719041847.md](architecture/implementation_roadmap_20260719041847.md) |
| historical | [documentation_index_20260719040237.md](documentation_index_20260719040237.md) | [documentation_index_20260719041847.md](documentation_index_20260719041847.md) |

ADR-0008は削除しない。`ja／en／auto` Decisionを保持し、Config配置だけをADR-0009で修正する。

## 11. Historical Chain

直前までの完全なHistorical Chain：

- [documentation_index_20260719040237.md](documentation_index_20260719040237.md)

## 12. Current Snapshot構成

```text
Requirements : 5
Architecture : 11
Governance   : 2
ADR          : 9
Handoffs     : 14
User Manual  : 1
Index        : 1
Current      : 43
Historical   : 43
Total        : 86
```

## 13. Append-Only判定規則

- 新しいTimestampのDocumentを最新とする
- 新しいTimestampのIndexを最新Indexとする
- 旧文書を上書きしない
- 旧文書を削除・改名・移動しない
- 後継文書の`supersedes`で旧文書を示す
- 旧文書の状態は最新Index側で示す
