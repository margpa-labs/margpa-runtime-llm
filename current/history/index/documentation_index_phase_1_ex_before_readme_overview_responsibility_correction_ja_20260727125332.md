# MARGPA Runtime LLM Current Documentation Index

```yaml
document_id: current_documentation_index
status: current
language: ja
created_at: 2026-07-26 15:16:24 JST
updated_at: 2026-07-27 12:32:38 JST
owner: 設計統括者役
active_phase: phase_1_ex
rag_default: true
```

## Current Position

```text
Phase 1                  : COMPLETE／ACCEPTED
Phase 1 Backup           : COMPLETED／VERIFIED
Phase 1-ex               : IN PROGRESS
Documentation Migration : COMPLETE／LEGACY ROOT RETIRED
Source Inventory         : 499／499 VALIDATED
Continuity／Roadmap Pass1: COMPLETE
Current Canonical        : RECONSTRUCTED
Phase 1 Lossless         : FINAL／316 OF 316 PASS
Phase 1-ex Lossless      : INTERIM／145 OF 145 PASS
Shared                   : RECONSTRUCTED
Continuity／Roadmap Pass2: COMPLETE
Public／Root Initial Set : COMPLETE／VALIDATED
Design Governance Recovery: INTERIM CURRENT STATE／READY
Git／GitHub              : NOT STARTED
```

## Current Canonical

- [要件定義書](requirements/requirements_specification_ja.md)
- [全体設計書](architecture/system_architecture_ja.md)
- [技術選定書](architecture/technology_selection_ja.md)
- [基本設計書](architecture/basic_design_ja.md)
- [Runtime Governance仕様書](governance/runtime_governance_specification_ja.md)
- [Project Continuity Master](project_continuity/project_continuity_master_ja.md)

## Active Phase

- [Phase 1-ex Index](../phases/phase_1_ex/phase_index_ja.md)
- [Phase 1-ex Target Documentation Structure](../phases/phase_1_ex/architecture/target_documentation_structure_ja.md)
- [Migration Manifest](../phases/phase_1_ex/operations/source_to_target_documentation_migration_manifest.json)
- [Migration Receipt](../phases/phase_1_ex/operations/documentation_directory_migration_receipt_ja.md)
- [Migration Validation](../phases/phase_1_ex/operations/documentation_directory_migration_validation_ja.md)
- [Legacy Root Retirement Manifest](../phases/phase_1_ex/operations/documentation_legacy_root_retirement_manifest.json)
- [Legacy Root Retirement Validation](../phases/phase_1_ex/operations/documentation_legacy_root_retirement_validation_ja.md)
- [ADR-0025 Public Demo／Auto-start／Pre-release Gate](../phases/phase_1_ex/adr/adr_0025_public_demo_auto_start_and_pre_release_gate_ja.md)
- [Public Demo／Auto-start／Pre-release Requirements](../phases/phase_1_ex/requirements/public_demo_auto_start_and_pre_release_requirements_ja.md)
- [Public Demo／Auto-start／RAG Extension Architecture](../phases/phase_1_ex/architecture/public_demo_auto_start_and_rag_extension_architecture_ja.md)
- [Pre-initial Commit Documentation Refresh Plan](../phases/phase_1_ex/operations/pre_initial_commit_documentation_refresh_plan_ja.md)
- [Documentation Reconstruction Inventory](../phases/phase_1_ex/history/operations/documentation_reconstruction_inventory_20260727093727.md)
- [Documentation Reconstruction Source Manifest](../phases/phase_1_ex/history/operations/documentation_reconstruction_source_inventory_20260727093727.json)
- [Continuity／Roadmap First-pass Record](../phases/phase_1_ex/history/operations/documentation_reconstruction_continuity_and_roadmap_first_pass_20260727094639.md)
- [Current Canonical Reconstruction](../phases/phase_1_ex/history/operations/current_canonical_reconstruction_20260727101132.md)
- [Phase 1／Phase 1-ex Lossless Reconstruction](../phases/phase_1_ex/history/operations/phase_1_and_phase_1_ex_lossless_reconstruction_20260727102850.md)
- [Shared Documentation Reconstruction](../phases/phase_1_ex/history/operations/shared_documentation_reconstruction_20260727104505.md)
- [Public／Canonical／Legal Documentation Reconstruction](../phases/phase_1_ex/history/operations/public_canonical_and_legal_documentation_reconstruction_20260727110347.md)
- [Documentation Reconstruction Final Validation](../phases/phase_1_ex/history/operations/documentation_reconstruction_final_validation_20260727110834.md)
- [Post-documentation Design Governance Recovery Manifest](../shared/history/design_governance_handoff/design_governance_recovery_manifest_20260727121343.md)
- [Public Concept Governance Kernel Reintegration](../phases/phase_1_ex/history/operations/public_concept_governance_kernel_reintegration_20260727123238.md)

## Completed Phase

- [Phase 1 Index](../phases/phase_1/phase_index_ja.md)
- [Phase 1 Final Lossless](../phases/phase_1/lossless/phase_1_lossless_ja.md)
- [Phase 1 Final Lossless Manifest](../phases/phase_1/lossless/phase_1_lossless_manifest.json)
- [Phase 1 ADR](../phases/phase_1/adr/phase_1_adr_ja.md)
- [Phase 1 Architecture](../phases/phase_1/architecture/phase_1_architecture_ja.md)
- [Phase 1 Governance](../phases/phase_1/governance/phase_1_governance_ja.md)
- [Phase 1 Requirements](../phases/phase_1/requirements/phase_1_requirements_ja.md)
- [Phase 1 Operations](../phases/phase_1/operations/phase_1_operations_ja.md)
- [Phase 1 Handoffs／Reviews／Status](../phases/phase_1/handoffs/phase_1_handoffs_ja.md)
- [Phase 1 User Manual](../phases/phase_1/user_manual/phase_1_user_manual_ja.md)
- [Phase 1 Index History Compilation](../phases/phase_1/index/phase_1_documentation_index_ja.md)

## Shared

- [Documentation Rules](../shared/conventions/documentation_rules_ja.md)
- [Documentation Structure／Task Operations](../shared/operations/documentation_structure_and_task_operations_ja.md)
- [Task Role／Write Authority](../shared/task_roles/task_role_write_authority_policy_ja.md)
- [Design Governance Handoff](../shared/design_governance_handoff/design_governance_handoff_ja.md)
- [Latest Interim Design Governance Recovery Manifest](../shared/history/design_governance_handoff/design_governance_recovery_manifest_20260727121343.md)

Sharedには`schemas/`、`templates/`および対応Historyの正式な配置先を予約している。Artifactが未作成のDirectoryへDummy文書は作らない。

## Public

- [Public Overview](../../public/overview_ja.md)
- [Public Concept](../../public/concept_ja.md)
- [Public Roadmap](../../public/roadmap_ja.md)
- [README](../../../README.md)
- [LICENSE](../../../LICENSE)
- [Terms of Use](../../../TERMS_OF_USE.md)
- [NOTICE](../../../NOTICE.md)
- [CITATION](../../../CITATION.cff)
- [Phase 1 Roadmap History](../../public/history/roadmap/roadmap_phase_1_ja.md)

PublicのOverview／Concept／RoadmapおよびRoot公開Artifactは、Phase 1-exの初回公開Corpusとして作成済みである。対応History Rootは`docs/public/history/overview/`、`docs/public/history/concept/`および`docs/public/history/roadmap/`である。

Research Preview初版は作成済みだが、GitHub公開操作は未実施である。Initial Commit前に公開Allowlist、Secret／Identity、第三者Attribution、Model Licenseおよび利用条件を再検証する。

## Stable History

- Current Stable Index変更前後原文：`docs/project/current/history/index/`
- Current Canonical変更前後原文：`docs/project/current/history/<category>/`
- Shared Stable変更前後原文：`docs/project/shared/history/<category>/`
- Public Stable変更前後原文：`docs/public/history/<category>/`

Stable HistoryとActive PhaseのAppend-only Documentation Index Snapshotは別Artifactであり、両方を保持する。

## Current Canonical Reconstruction

2026年7月27日のCurrent Canonical再構築では、更新前原文を各`history/`へ保存した後、既存本文を削除せず累積拡張した。

| Stable Document | Current Line Count | Current State |
|---|---:|---|
| Requirements Specification | 766 | Reconstructed |
| System Architecture | 745 | Reconstructed |
| Technology Selection | 471 | Reconstructed |
| Basic Design | 828 | Reconstructed |
| Runtime Governance Specification | 1141 | Reconstructed |
| Project Continuity Master | 1025 | Second Pass Complete |
| Public Roadmap | 1716 | Second Pass Complete |
| Public Overview | 23 | Created |
| Public Concept | 342 | Governance Kernel Concept Reintegrated |
| README | 240 | Created／Phase Position Added |
| LICENSE | 110 | Research Preview v0.1 |
| TERMS_OF_USE | 124 | Created |
| NOTICE | 108 | Created |
| CITATION | 34 | Created |

設計統括者役の即時復旧用に、Documentation Corpus完成直後のStable Handoffを累積更新し、Phase未完了であることを明示した`interim_current_state` Recovery Manifestを作成した。これはPhase 1-ex完了版Manifestではなく、Task障害時の臨時完全復旧点である。

Public Conceptは、Governanceを実行可能な第一級Componentとして扱う構造、AI System内部の分散Governance Point、反証可能な実験、存在とAuthorityの分離、AI Lifecycle、External R&D Port、Project運用上の自己適用およびPhase 1の位置付けを累積再統合した。Hypervisor／実験OSは概念的比喩であり、実装済み製品の主張ではない。

Current Canonicalの主な追加範囲：

- Project制約、優先順位およびPrototype境界
- Model Runtime／Artifact／Generation／Thinking／Language
- Conversation／Web／Summary／Markdown／Copy
- Config Source、Component Switchboard、Invalid Combination
- Mac／Lightning Pure CPU／Basic Preview／Auto-start／Public Demo
- Documentation Lifecycle、Task Role、Lossless Compilation
- Audit／Evidence／Evaluation／Repair
- RAG／Agent／ML／定量計算／定性計算
- Generic Governance Definition Platform
- ARGD／DAGDおよび16 GD候補
- EASA／DLAGSA／OCILNS
- Public Identity、利用条件、免責および公開Artifact

Current Canonicalは要約差分ではなく、現在のTaskを再作成しても再説明なしで継続できる累積・自己完結文書として扱う。

## Current Reconstruction History

### Before

- [Requirements Before](history/requirements/requirements_specification_phase_1_ex_before_canonical_reconstruction_ja_20260727100120.md)
- [System Architecture Before](history/architecture/system_architecture_phase_1_ex_before_canonical_reconstruction_ja_20260727100120.md)
- [Technology Selection Before](history/architecture/technology_selection_phase_1_ex_before_canonical_reconstruction_ja_20260727100120.md)
- [Basic Design Before](history/architecture/basic_design_phase_1_ex_before_canonical_reconstruction_ja_20260727100120.md)
- [Runtime Governance Before](history/governance/runtime_governance_specification_phase_1_ex_before_canonical_reconstruction_ja_20260727100120.md)
- [Current Index Before](history/index/documentation_index_phase_1_ex_before_canonical_reconstruction_ja_20260727100120.md)

### Reconstructed

- [Requirements Reconstructed](history/requirements/requirements_specification_phase_1_ex_canonical_reconstruction_ja_20260727101017.md)
- [System Architecture Reconstructed](history/architecture/system_architecture_phase_1_ex_canonical_reconstruction_ja_20260727101017.md)
- [Technology Selection Reconstructed](history/architecture/technology_selection_phase_1_ex_canonical_reconstruction_ja_20260727101017.md)
- [Basic Design Reconstructed](history/architecture/basic_design_phase_1_ex_canonical_reconstruction_ja_20260727101017.md)
- [Runtime Governance Reconstructed](history/governance/runtime_governance_specification_phase_1_ex_canonical_reconstruction_ja_20260727101017.md)

### Continuity／Public Second Pass

- [Project Continuity Before Second Pass](history/project_continuity/project_continuity_master_phase_1_ex_before_second_pass_ja_20260727105501.md)
- [Project Continuity Second Pass](history/project_continuity/project_continuity_master_phase_1_ex_second_pass_ja_20260727105744.md)
- [Roadmap Before Second Pass](../../public/history/roadmap/roadmap_phase_1_ex_before_second_pass_ja_20260727105501.md)
- [Roadmap Second Pass](../../public/history/roadmap/roadmap_phase_1_ex_second_pass_ja_20260727105744.md)
- [Public Overview Snapshot](../../public/history/overview/overview_phase_1_ex_ja_20260727105501.md)
- [Public Concept Snapshot](../../public/history/concept/concept_phase_1_ex_ja_20260727105501.md)
- [Public Concept Before Governance Kernel Reintegration](../../public/history/concept/concept_phase_1_ex_before_governance_kernel_reintegration_ja_20260727123044.md)
- [Public Concept Governance Kernel Reintegration](../../public/history/concept/concept_phase_1_ex_governance_kernel_reintegration_ja_20260727123238.md)

## Reading Rule

通常はCurrentとPhase Indexを読む。Raw HistoryはSource確認、監査、矛盾追跡または明示指定時だけ参照する。

次Taskは、まず本Index、Project Continuity Master、Active Phase IndexおよびRoadmapを読む。その後、作業対象に応じてRequirements／Architecture／Governance／Phase Losslessを読む。
