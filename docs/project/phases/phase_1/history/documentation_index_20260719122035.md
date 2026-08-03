# MARGPA Runtime LLM 文書索引

- 文書ID: `documentation_index`
- 状態: `current`
- 作成日時: `2026-07-19 12:20:35 JST`
- 更新日時: `2026-07-19 12:20:35 JST`
- 対象: `docs/`全体
- 正本言語: 日本語
- Snapshot: `20260719122035`
- supersedes: `documentation_index_20260719112304.md`

## 1. この索引の役割

この文書は、現在有効なRequirements、Architecture、Governance、ADR、Handoff、Status、Review、User Manualと、過去文書の世代関係を示す最新Indexである。

同一系列ではFile名末尾のTimestampが最も新しいDocumentを最新とする。

## 2. 今回のSnapshot Update

- Phase 1-DのSource、Config、Test、Implementer Statusを設計Reviewした。
- Blocking／High／Medium Findingは0件であった。
- Acceptance Criteria 16／16をPassと判定した。
- Static、Default Test、Environment、Lock／Offline、Native Metal、Real CLI、Production Acceptanceを独立再実行した。
- Phase 1-Dを`Complete／Accepted`へ更新した。
- RoadmapのCurrent PositionとNext Actionを更新した。
- 次の設計対象はPhase 1-E Thinking Presentationである。

## 3. 最初に読む文書

1. [documentation_rules_20260718193435.md](requirements/documentation_rules_20260718193435.md)
2. [common_project_handoff_20260718193435.md](handoffs/common_project_handoff_20260718193435.md)
3. [project_requirements_20260718193435.md](requirements/project_requirements_20260718193435.md)
4. [implementation_roadmap_20260719122035.md](architecture/implementation_roadmap_20260719122035.md)
5. [designer_review_phase_1d_final_20260719122035.md](handoffs/designer_review_phase_1d_final_20260719122035.md)
6. [post_phase_1e_research_platform_requirements_20260719112304.md](requirements/post_phase_1e_research_platform_requirements_20260719112304.md)
7. [generic_governance_definition_platform_requirements_20260719112304.md](requirements/generic_governance_definition_platform_requirements_20260719112304.md)
8. [governance_control_plane_architecture_20260719112304.md](architecture/governance_control_plane_architecture_20260719112304.md)
9. [governance_definition_platform_architecture_20260719112304.md](architecture/governance_definition_platform_architecture_20260719112304.md)
10. [experimental_runtime_ui_status_architecture_20260719112304.md](architecture/experimental_runtime_ui_status_architecture_20260719112304.md)
11. [lightning_ai_studio_cross_environment_architecture_20260719112304.md](architecture/lightning_ai_studio_cross_environment_architecture_20260719112304.md)
12. [governance_definition_catalog_20260719112304.md](governance/governance_definition_catalog_20260719112304.md)
13. [adr_0010_research_runtime_phase_reorganization_20260719112304.md](adr/adr_0010_research_runtime_phase_reorganization_20260719112304.md)
14. [adr_0011_shared_governance_control_plane_and_distributed_points_20260719112304.md](adr/adr_0011_shared_governance_control_plane_and_distributed_points_20260719112304.md)
15. [adr_0012_optional_generic_governance_definition_platform_20260719112304.md](adr/adr_0012_optional_generic_governance_definition_platform_20260719112304.md)
16. [adr_0013_lightning_ai_studio_external_development_20260719112304.md](adr/adr_0013_lightning_ai_studio_external_development_20260719112304.md)
17. [designer_handoff_post_phase_1e_research_platform_20260719112304.md](handoffs/designer_handoff_post_phase_1e_research_platform_20260719112304.md)
18. [phase_1_macos_user_manual_20260719004209.md](user_manual/phase_1_macos_user_manual_20260719004209.md)

## 4. Current Requirements

| 状態 | 文書 | 役割 |
|---|---|---|
| current | [documentation_rules_20260718193435.md](requirements/documentation_rules_20260718193435.md) | Append-Only、Timestamp、最新判定、読み取り専用原則 |
| current | [project_requirements_20260718193435.md](requirements/project_requirements_20260718193435.md) | Project目的、Scope、優先順位、Hardware、制約 |
| implemented_accepted | [phase_1c_deployment_platform_acceleration_requirements_20260719013109.md](requirements/phase_1c_deployment_platform_acceleration_requirements_20260719013109.md) | Phase 1-C Requirement、全Criteria Pass |
| implemented_accepted | [configuration_layer_requirements_20260719041847.md](requirements/configuration_layer_requirements_20260719041847.md) | Application／Model／Deployment／Platform Registry責務分離 |
| implemented_accepted | [phase_1d_response_language_requirements_20260719041847.md](requirements/phase_1d_response_language_requirements_20260719041847.md) | Config分離、`ja／en／auto`、Composition、Acceptance |
| accepted_planning_only | [post_phase_1e_research_platform_requirements_20260719112304.md](requirements/post_phase_1e_research_platform_requirements_20260719112304.md) | Phase 2以降の疎結合AI実験・統治Platform要件 |
| accepted_planning_only | [generic_governance_definition_platform_requirements_20260719112304.md](requirements/generic_governance_definition_platform_requirements_20260719112304.md) | 全GD任意、0件Baseline、汎用Provider／Adapter／IR／Compiler要件 |

## 5. Current Architecture

| 状態 | 文書 | 役割 |
|---|---|---|
| current | [system_architecture_20260718193435.md](architecture/system_architecture_20260718193435.md) | Modular Monolith、Port／Adapter、Deployment、UI、Storage |
| current | [project_directory_structure_20260718192110.md](architecture/project_directory_structure_20260718192110.md) | Module、Port／Adapter、依存方向 |
| current | [model_strategy_20260718174637.md](architecture/model_strategy_20260718174637.md) | Model選定、Quantization、Storage、Registry |
| current | [python_environment_and_dependency_strategy_20260718201744.md](architecture/python_environment_and_dependency_strategy_20260718201744.md) | Python、Venv、uv、Dependency、Fallback |
| implemented | [phase_1b_model_runtime_contract_20260718223203.md](architecture/phase_1b_model_runtime_contract_20260718223203.md) | Model Runtime Contract、Config、CLI、Test |
| implemented_accepted | [phase_1c_deployment_platform_acceleration_architecture_20260719013109.md](architecture/phase_1c_deployment_platform_acceleration_architecture_20260719013109.md) | Deployment／Platform／Acceleration Hook |
| implemented_accepted | [configuration_layer_architecture_20260719041847.md](architecture/configuration_layer_architecture_20260719041847.md) | Application Config、Deployment Profile、Typed Composer |
| implemented_accepted | [phase_1d_response_language_architecture_20260719041847.md](architecture/phase_1d_response_language_architecture_20260719041847.md) | Configuration Composition、Response Resolver、Message Composer |
| phase_1e_design_source | [response_language_and_thinking_output_policy_20260719013109.md](architecture/response_language_and_thinking_output_policy_20260719013109.md) | Thinking部分をPhase 1-E設計元として保持 |
| current | [future_extensions_20260718174637.md](architecture/future_extensions_20260718174637.md) | RAG、Agent、Image、Cloud、複数Model／GD |
| accepted_planning_only | [governance_control_plane_architecture_20260719112304.md](architecture/governance_control_plane_architecture_20260719112304.md) | 共有Control Plane、分散Point、Binding、State、Action／Budget |
| accepted_planning_only | [governance_definition_platform_architecture_20260719112304.md](architecture/governance_definition_platform_architecture_20260719112304.md) | Empty／Filesystem Provider、Manifest、Adapter、IR、Compiler／Security |
| accepted_planning_only | [experimental_runtime_ui_status_architecture_20260719112304.md](architecture/experimental_runtime_ui_status_architecture_20260719112304.md) | Switchboard、Experiment、Event／Status、Typed Config、UI |
| accepted_planning_only | [lightning_ai_studio_cross_environment_architecture_20260719112304.md](architecture/lightning_ai_studio_cross_environment_architecture_20260719112304.md) | Mac Metal／Lightning Linux CUDAのCross-environment設計 |
| current | [implementation_roadmap_20260719122035.md](architecture/implementation_roadmap_20260719122035.md) | Phase 1-D Accepted、Phase 1-EがNext、Phase 0～10 |

## 6. Current Governance

| 状態 | 文書 | 役割 |
|---|---|---|
| current | [runtime_governance_20260718174637.md](governance/runtime_governance_20260718174637.md) | ARGD、DAGD、Compiler、Profile、将来GD |
| current | [audit_evaluation_security_20260718174637.md](governance/audit_evaluation_security_20260718174637.md) | Audit、SHA-512、Evaluation、Guard、Judge、Permission |
| current_reference_catalog | [governance_definition_catalog_20260719112304.md](governance/governance_definition_catalog_20260719112304.md) | ARGD／DAGDと16 Optional Extensionの意味、制約、推奨Binding |

## 7. Current ADR

| 状態 | 文書 | Decision |
|---|---|---|
| accepted | [adr_0001_initial_model_selection_20260718174637.md](adr/adr_0001_initial_model_selection_20260718174637.md) | Main、Guard、JudgeとQuantization |
| accepted | [adr_0002_external_model_storage_20260718174637.md](adr/adr_0002_external_model_storage_20260718174637.md) | External Model RootとPOSIX Symbolic Link |
| accepted | [adr_0003_japanese_documentation_and_handoffs_20260718174637.md](adr/adr_0003_japanese_documentation_and_handoffs_20260718174637.md) | 日本語Docs、Timestamp、担当別Handoff |
| accepted | [adr_0004_modular_monolith_20260718174637.md](adr/adr_0004_modular_monolith_20260718174637.md) | Modular Monolith |
| accepted | [adr_0005_python_environment_and_dependency_management_20260718201744.md](adr/adr_0005_python_environment_and_dependency_management_20260718201744.md) | Python 3.13.14、`.venv`、uv、Fallback |
| accepted | [adr_0006_model_runtime_port_and_configuration_20260718224308.md](adr/adr_0006_model_runtime_port_and_configuration_20260718224308.md) | Model Port、Lifecycle、Capability、Config、CLI |
| accepted_implemented | [adr_0007_deployment_platform_acceleration_abstraction_20260719013109.md](adr/adr_0007_deployment_platform_acceleration_abstraction_20260719013109.md) | Platform Hook、Capability分離、Validation |
| accepted_implemented_amended_by_0009 | [adr_0008_response_language_policy_20260719040237.md](adr/adr_0008_response_language_policy_20260719040237.md) | `ja／en／auto`、Config配置はADR-0009で修正 |
| accepted_implemented | [adr_0009_application_deployment_configuration_separation_20260719041847.md](adr/adr_0009_application_deployment_configuration_separation_20260719041847.md) | `application.toml`、Deployment責務分離、Typed Composition |
| accepted | [adr_0010_research_runtime_phase_reorganization_20260719112304.md](adr/adr_0010_research_runtime_phase_reorganization_20260719112304.md) | Phase 2へExperimental Control Planeを置きPhase 0～10へ再編 |
| accepted | [adr_0011_shared_governance_control_plane_and_distributed_points_20260719112304.md](adr/adr_0011_shared_governance_control_plane_and_distributed_points_20260719112304.md) | 共有Control Plane + 分散Point + Explicit Binding |
| accepted | [adr_0012_optional_generic_governance_definition_platform_20260719112304.md](adr/adr_0012_optional_generic_governance_definition_platform_20260719112304.md) | 全GD任意、0件Baseline、非ハードコード |
| accepted | [adr_0013_lightning_ai_studio_external_development_20260719112304.md](adr/adr_0013_lightning_ai_studio_external_development_20260719112304.md) | 第一外部開発／検証環境にLightning AI Studioを採用 |

## 8. Current Handoffs／Status／Review

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
| implemented_accepted | [designer_handoff_phase_1d_response_language_20260719041847.md](handoffs/designer_handoff_phase_1d_response_language_20260719041847.md) | Phase 1-D Config／Language実装Handoff |
| reviewed_accepted | [implementer_status_phase_1d_configuration_and_response_language_20260719095111.md](handoffs/implementer_status_phase_1d_configuration_and_response_language_20260719095111.md) | Phase 1-D実装報告／Review済み |
| accepted_phase_1d_complete | [designer_review_phase_1d_final_20260719122035.md](handoffs/designer_review_phase_1d_final_20260719122035.md) | Phase 1-D最終受入 |
| planning_handoff_current_scope | [designer_handoff_post_phase_1e_research_platform_20260719112304.md](handoffs/designer_handoff_post_phase_1e_research_platform_20260719112304.md) | Phase 1-E後の全体実装計画／境界 |
| waiting | [public_documentation_handoff_20260718174637.md](handoffs/public_documentation_handoff_20260718174637.md) | 対外Docs作成者役 |

## 9. Current User Manual

| 状態 | 文書 | 対象 |
|---|---|---|
| current | [phase_1_macos_user_manual_20260719004209.md](user_manual/phase_1_macos_user_manual_20260719004209.md) | Mac上でのPhase 1操作、Test、Troubleshooting |

## 10. Current Position

```text
Phase 0                                             : Complete
Phase 1-A Environment                              : Complete／Accepted
Phase 1-B Model Runtime                            : Complete／Accepted
Phase 1-C Deployment／Platform／Acceleration     : Complete／Accepted
Phase 1-D Configuration／Response Language        : Complete／Accepted
Phase 1-E Thinking Presentation                    : Planned／Not Designed／Not Authorized
Phase 2+                                            : Requirements／Architecture Accepted／Implementation Not Authorized
Current Native Verification                         : macOS／Apple Silicon arm64／Metal
Planned External Verification                       : Lightning AI Studio／Linux x86_64／CUDA
```

## 11. Phase 1-D Independent Gate Summary

```text
Ruff Format        : Pass／54 files
Ruff Check         : Pass
Mypy Strict        : Pass／54 source files
Compileall         : Pass
Default Pytest     : 94 passed, 2 deselected
Model Smoke        : 2 passed, 94 deselected
Environment        : Pass／Python 3.13.14／Metal
uv Lock            : Pass／117 packages
uv Offline Dry Run : Pass／115 packages／No changes
Real CLI ja        : 成功。
Real CLI en        : success
Real CLI auto      : OK
Production Runtime : success
```

## 12. Supersession Update

| 状態 | 旧文書 | 最新文書 |
|---|---|---|
| historical | [implementation_roadmap_20260719112304.md](architecture/implementation_roadmap_20260719112304.md) | [implementation_roadmap_20260719122035.md](architecture/implementation_roadmap_20260719122035.md) |
| historical | [documentation_index_20260719112304.md](documentation_index_20260719112304.md) | [documentation_index_20260719122035.md](documentation_index_20260719122035.md) |

Phase 1-D Reviewは新規系列であり、置換先を持たない。

## 13. Historical Chain

直前までの完全なHistorical Chain：

- [documentation_index_20260719112304.md](documentation_index_20260719112304.md)

## 14. Current Snapshot構成

```text
Requirements : 7
Architecture : 15
Governance   : 3
ADR          : 13
Handoffs     : 17
User Manual  : 1
Index        : 1
Current      : 57
Historical   : 47
Total        : 104
```

## 15. 今回作成したSnapshot文書

- [designer_review_phase_1d_final_20260719122035.md](handoffs/designer_review_phase_1d_final_20260719122035.md)
- [implementation_roadmap_20260719122035.md](architecture/implementation_roadmap_20260719122035.md)
- [documentation_index_20260719122035.md](documentation_index_20260719122035.md)

## 16. Next Design Target

```text
Phase 1-E Thinking Presentation
  ├─ Thinking実行と表示の分離
  ├─ 表示／非表示
  ├─ Display Label
  ├─ Model Protocol Parser
  ├─ Streaming Filter
  ├─ Raw／Display Output
  └─ 保存Policy
```

## 17. Authorization Boundary

Phase 1-DはAcceptedである。Phase 1-Eの設計は次の対象として進められる。

ただし、次は未解禁である。

- Phase 1-EのSource／Config／Test実装
- Phase 2以降の実装
- Dependency Install
- Model Download
- Lightning Studio／ZeroGPU操作

## 18. Append-Only判定規則

- 新しいTimestampのDocumentを最新とする
- 新しいTimestampのIndexを最新Indexとする
- 旧文書を上書きしない
- 旧文書を削除・改名・移動しない
- 後継文書の`supersedes`で旧文書を示す
- 旧文書の状態は最新Index側で示す
