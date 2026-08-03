# MARGPA Runtime LLM 文書索引

- 文書ID: `documentation_index`
- 状態: `current`
- 作成日時: `2026-07-19 14:25:58 JST`
- 更新日時: `2026-07-19 14:25:58 JST`
- 対象: `docs/`全体
- 正本言語: 日本語
- Snapshot: `20260719142558`
- supersedes: `documentation_index_20260719130303.md`

## 1. この索引の役割

この文書は、現在有効なRequirements、Architecture、Governance、Operations、ADR、Handoff、Status、Review、User Manualと、過去文書の世代関係を示す最新Indexである。

同一系列ではFile名末尾のTimestampが最も新しいDocumentを最新とする。

## 2. 今回のSnapshot Update

- 実装担当からPhase 1-Eの実装完了と、Acceptance Criteria `22／22 Pass`が報告された。
- Phase 1-Eは設計者役による独立レビュー前であるため、`Implementation Reported／Independent Review Pending`とした。
- Backup取得の発火条件を、Top-Level Phase全体の完了を設計者役が明示した直後に固定した。
- Subphase完了、実装担当の完了報告、Review途中ではBackupを取得しないことを明文化した。
- Phase完了BackupのArchive、Manifest、Receipt、SHA-512、除外対象、復元確認をOperations Policyとして新設した。
- 設計者役、実装者役、対外向けDocs作成者役の書込権限と読み取り専用境界を正式化した。
- `docs/operations/`の正本Ownershipを設計者役とした。
- 設計者役と実装者役の分離がPhase 1の実運用で機能していることを記録した。
- 対外向けDocs作成者役は、権限境界は正式化するが、実運用評価は今後とした。
- Documentation Rules、Common Handoff、Implementation Roadmapを後継化した。
- Source、Config、Test、Backup Archiveは今回変更・作成していない。

## 3. 最初に読む文書

1. [documentation_rules_20260719142558.md](requirements/documentation_rules_20260719142558.md)
2. [task_role_write_authority_policy_20260719142558.md](requirements/task_role_write_authority_policy_20260719142558.md)
3. [common_project_handoff_20260719142558.md](handoffs/common_project_handoff_20260719142558.md)
4. [project_requirements_20260718193435.md](requirements/project_requirements_20260718193435.md)
5. [implementation_roadmap_20260719142558.md](architecture/implementation_roadmap_20260719142558.md)
6. [phase_completion_backup_policy_20260719142558.md](operations/phase_completion_backup_policy_20260719142558.md)
7. [phase_1e_thinking_presentation_requirements_20260719130303.md](requirements/phase_1e_thinking_presentation_requirements_20260719130303.md)
8. [phase_1e_thinking_presentation_architecture_20260719130303.md](architecture/phase_1e_thinking_presentation_architecture_20260719130303.md)
9. [adr_0014_thinking_execution_presentation_and_persistence_separation_20260719130303.md](adr/adr_0014_thinking_execution_presentation_and_persistence_separation_20260719130303.md)
10. [designer_handoff_phase_1e_thinking_presentation_20260719130303.md](handoffs/designer_handoff_phase_1e_thinking_presentation_20260719130303.md)
11. [implementer_status_phase_1e_thinking_presentation_20260719134914.md](handoffs/implementer_status_phase_1e_thinking_presentation_20260719134914.md)
12. [post_phase_1e_research_platform_requirements_20260719112304.md](requirements/post_phase_1e_research_platform_requirements_20260719112304.md)
13. [generic_governance_definition_platform_requirements_20260719112304.md](requirements/generic_governance_definition_platform_requirements_20260719112304.md)
14. [governance_control_plane_architecture_20260719112304.md](architecture/governance_control_plane_architecture_20260719112304.md)
15. [governance_definition_platform_architecture_20260719112304.md](architecture/governance_definition_platform_architecture_20260719112304.md)
16. [experimental_runtime_ui_status_architecture_20260719112304.md](architecture/experimental_runtime_ui_status_architecture_20260719112304.md)
17. [lightning_ai_studio_cross_environment_architecture_20260719112304.md](architecture/lightning_ai_studio_cross_environment_architecture_20260719112304.md)
18. [governance_definition_catalog_20260719112304.md](governance/governance_definition_catalog_20260719112304.md)
19. [phase_1_macos_user_manual_20260719004209.md](user_manual/phase_1_macos_user_manual_20260719004209.md)

## 4. Current Requirements

| 状態 | 文書 | 役割 |
|---|---|---|
| current | [documentation_rules_20260719142558.md](requirements/documentation_rules_20260719142558.md) | Project Root、Append-Only、Timestamp、Index、Review、Role、Backup Trigger |
| accepted_current | [task_role_write_authority_policy_20260719142558.md](requirements/task_role_write_authority_policy_20260719142558.md) | Role別Write Authority、Read-only Boundary、Operations Ownership |
| current | [project_requirements_20260718193435.md](requirements/project_requirements_20260718193435.md) | Project目的、Scope、優先順位、Hardware、制約 |
| implemented_accepted | [phase_1c_deployment_platform_acceleration_requirements_20260719013109.md](requirements/phase_1c_deployment_platform_acceleration_requirements_20260719013109.md) | Phase 1-C Requirement、全Criteria Pass |
| implemented_accepted | [configuration_layer_requirements_20260719041847.md](requirements/configuration_layer_requirements_20260719041847.md) | Application／Model／Deployment／Platform Registry責務分離 |
| implemented_accepted | [phase_1d_response_language_requirements_20260719041847.md](requirements/phase_1d_response_language_requirements_20260719041847.md) | Config分離、`ja／en／auto`、Composition、Acceptance |
| implementation_reported_review_pending | [phase_1e_thinking_presentation_requirements_20260719130303.md](requirements/phase_1e_thinking_presentation_requirements_20260719130303.md) | Default `高度推論`、4責務分離、22 Criteria |
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
| implementation_reported_review_pending | [phase_1e_thinking_presentation_architecture_20260719130303.md](architecture/phase_1e_thinking_presentation_architecture_20260719130303.md) | Presentation Module、Parser Registry、Stateful Streaming、CLI |
| current | [future_extensions_20260718174637.md](architecture/future_extensions_20260718174637.md) | RAG、Agent、Image、Cloud、複数Model／GD |
| accepted_planning_only | [governance_control_plane_architecture_20260719112304.md](architecture/governance_control_plane_architecture_20260719112304.md) | 共有Control Plane、分散Point、Binding、State、Action／Budget |
| accepted_planning_only | [governance_definition_platform_architecture_20260719112304.md](architecture/governance_definition_platform_architecture_20260719112304.md) | Empty／Filesystem Provider、Manifest、Adapter、IR、Compiler／Security |
| accepted_planning_only | [experimental_runtime_ui_status_architecture_20260719112304.md](architecture/experimental_runtime_ui_status_architecture_20260719112304.md) | Switchboard、Experiment、Event／Status、Typed Config、UI |
| accepted_planning_only | [lightning_ai_studio_cross_environment_architecture_20260719112304.md](architecture/lightning_ai_studio_cross_environment_architecture_20260719112304.md) | Mac Metal／Lightning Linux CUDAのCross-environment設計 |
| current | [implementation_roadmap_20260719142558.md](architecture/implementation_roadmap_20260719142558.md) | Phase 1-E Review待ち、Phase 0～10、Phase Completion／Backup Gate |

## 6. Current Governance

| 状態 | 文書 | 役割 |
|---|---|---|
| current | [runtime_governance_20260718174637.md](governance/runtime_governance_20260718174637.md) | ARGD、DAGD、Compiler、Profile、将来GD |
| current | [audit_evaluation_security_20260718174637.md](governance/audit_evaluation_security_20260718174637.md) | Audit、SHA-512、Evaluation、Guard、Judge、Permission |
| current_reference_catalog | [governance_definition_catalog_20260719112304.md](governance/governance_definition_catalog_20260719112304.md) | ARGD／DAGDと16 Optional Extensionの意味、制約、推奨Binding |

## 7. Current Operations

| 状態 | 文書 | 役割 |
|---|---|---|
| accepted_current | [phase_completion_backup_policy_20260719142558.md](operations/phase_completion_backup_policy_20260719142558.md) | Phase完了直後のArchive、Manifest、Receipt、SHA-512、復元確認 |

## 8. Current ADR

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
| accepted | [adr_0014_thinking_execution_presentation_and_persistence_separation_20260719130303.md](adr/adr_0014_thinking_execution_presentation_and_persistence_separation_20260719130303.md) | Default `高度推論`、Thinking 4責務分離、Parser Key、Raw保存OFF |

## 9. Current Handoffs／Status／Review

| 状態 | 文書 | 対象 |
|---|---|---|
| current | [common_project_handoff_20260719142558.md](handoffs/common_project_handoff_20260719142558.md) | 全担当Task、Role、Review、Phase完了／Backup Trigger |
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
| implementation_reported | [designer_handoff_phase_1e_thinking_presentation_20260719130303.md](handoffs/designer_handoff_phase_1e_thinking_presentation_20260719130303.md) | Phase 1-E正式実装Handoff |
| implementation_complete_review_requested | [implementer_status_phase_1e_thinking_presentation_20260719134914.md](handoffs/implementer_status_phase_1e_thinking_presentation_20260719134914.md) | Phase 1-E実装報告、22／22 Pass、独立Review待ち |
| planning_handoff_current_scope | [designer_handoff_post_phase_1e_research_platform_20260719112304.md](handoffs/designer_handoff_post_phase_1e_research_platform_20260719112304.md) | Phase 1-E後の全体実装計画／境界 |
| waiting | [public_documentation_handoff_20260718174637.md](handoffs/public_documentation_handoff_20260718174637.md) | 対外Docs作成者役 |

## 10. Current User Manual

| 状態 | 文書 | 対象 |
|---|---|---|
| current | [phase_1_macos_user_manual_20260719004209.md](user_manual/phase_1_macos_user_manual_20260719004209.md) | Mac上でのPhase 1操作、Test、Troubleshooting |

## 11. Current Position

```text
Phase 0                                             : Complete
Phase 1-A Environment                              : Complete／Accepted
Phase 1-B Model Runtime                            : Complete／Accepted
Phase 1-C Deployment／Platform／Acceleration     : Complete／Accepted
Phase 1-D Configuration／Response Language        : Complete／Accepted
Phase 1-E Thinking Presentation                    : Implementation Reported／Independent Review Pending
Phase 1 Overall                                    : Final Review Pending／Completion Not Declared
Phase 1 Backup                                     : Not Triggered
Phase 2+                                           : Requirements／Architecture Accepted／Implementation Not Authorized
Current Native Verification                        : macOS／Apple Silicon arm64／Metal
Planned External Verification                      : Lightning AI Studio／Linux x86_64／CUDA
```

## 12. Phase Completion／Backup Decision

```text
Implementer Completion Report
       ↓
Designer Independent Review
       ↓
Follow-up／Re-review if needed
       ↓
Phase Final Acceptance／User Manual／Docs／Index
       ↓
Designer Explicit Completion Declaration
  "Phase Nは完了です。次はPhase N+1です。"
       ↓
Phase Backup and Restore Verification
       ↓
Next Phase Substantive Changes
```

この条件はすべてのTop-Level Phaseに共通である。

## 13. Role Operation Status

```text
Designer Role     : Operationally Validated in Phase 1
Implementer Role  : Operationally Validated in Phase 1
Designer／Implementer Separation : Functioning as intended
External Docs Role: Authority Defined／Operational Validation Pending
Operations Owner  : Designer Role
```

## 14. Supersession Update

| 状態 | 旧文書 | 最新文書 |
|---|---|---|
| historical | [documentation_rules_20260718193435.md](requirements/documentation_rules_20260718193435.md) | [documentation_rules_20260719142558.md](requirements/documentation_rules_20260719142558.md) |
| historical | [common_project_handoff_20260718193435.md](handoffs/common_project_handoff_20260718193435.md) | [common_project_handoff_20260719142558.md](handoffs/common_project_handoff_20260719142558.md) |
| historical | [implementation_roadmap_20260719130303.md](architecture/implementation_roadmap_20260719130303.md) | [implementation_roadmap_20260719142558.md](architecture/implementation_roadmap_20260719142558.md) |
| historical | [documentation_index_20260719130303.md](documentation_index_20260719130303.md) | [documentation_index_20260719142558.md](documentation_index_20260719142558.md) |

`task_role_write_authority_policy_20260719142558.md`と`phase_completion_backup_policy_20260719142558.md`は新規系列である。

## 15. Historical Chain

直前までの完全なHistorical Chain：

- [documentation_index_20260719130303.md](documentation_index_20260719130303.md)

## 16. Current Snapshot構成

```text
Requirements : 9
Architecture : 15
Governance   : 3
Operations   : 1
ADR          : 14
Handoffs     : 19
User Manual  : 1
Index        : 1
Current      : 63
Historical   : 60
Total        : 123
```

## 17. 前回Index以降に追加した文書

- [implementer_status_phase_1e_thinking_presentation_20260719134914.md](handoffs/implementer_status_phase_1e_thinking_presentation_20260719134914.md)
- [phase_completion_backup_policy_20260719142558.md](operations/phase_completion_backup_policy_20260719142558.md)
- [task_role_write_authority_policy_20260719142558.md](requirements/task_role_write_authority_policy_20260719142558.md)
- [documentation_rules_20260719142558.md](requirements/documentation_rules_20260719142558.md)
- [common_project_handoff_20260719142558.md](handoffs/common_project_handoff_20260719142558.md)
- [implementation_roadmap_20260719142558.md](architecture/implementation_roadmap_20260719142558.md)
- [documentation_index_20260719142558.md](documentation_index_20260719142558.md)

## 18. Next Gate

```text
Phase 1-E Implementation Report : Received
       ↓
Designer Independent Review     : Next
       ↓
Phase 1 Final Acceptance
       ↓
Designer Completion Declaration
       ↓
Phase 1 Backup
       ↓
Phase 2
```

## 19. Authorization Boundary

今回許可されたのは、Backup Policy、Role Authority Policy、共通規則、Common Handoff、Roadmap、Indexの文書化である。

今回実施していないもの：

- Phase 1-E Source／Config／Testの修正
- Phase 1-Eの独立レビューとAccepted判定
- Phase 1完了宣言
- Backup Archive／Manifest／Receiptの生成
- Phase 2以降の実装
- Dependency Install／Update
- Model Download
- Lightning AI Studio／ZeroGPU操作

## 20. Append-Only判定規則

- 新しいTimestampのDocumentを最新とする
- 新しいTimestampのIndexを最新Indexとする
- 旧文書を上書きしない
- 旧文書を削除・改名・移動しない
- 後継文書の`supersedes`で旧文書を示す
- 旧文書の状態は最新Index側で示す

