# Phase 1-ex Documentation Index Snapshot

```yaml
document_id: phase_1_ex_documentation_index_snapshot
snapshot: 20260804035722
state_at: 2026-08-04 03:57:22 JST
status: current_snapshot
snapshot_of:
  - ../phase_index_ja.md
  - operations/git_source_target_integration_publication_and_single_root_cutover_20260804035722.md
  - ../../../current/documentation_index_ja.md
  - ../../../current/project_continuity/project_continuity_master_ja.md
  - ../../../shared/design_governance_handoff/design_governance_handoff_ja.md
  - ../../../shared/history/design_governance_handoff/design_governance_recovery_manifest_20260804035722.md
  - ../../../shared/operations/git_workflow_policy_ja.md
  - ../../../shared/operations/git_publication_sanitation_policy_ja.md
supersedes: documentation_index_20260804025318.md
source: user_directed_git_integration_publication_single_root_cutover_and_state_refresh
phase_complete: false
```

本Snapshotは[2026-08-04 02:53:18版](documentation_index_20260804025318.md)までの全状態を継承し、Source→Target Actual Integration、Publication Tree整合、GitHub反映、Risk-based Git Workflow、Direct `main` Docs Commit／Push、単一Canonical Git Root Cutover、旧Git Staging Root退役および設計統括者役のInterim Recovery PointをAppend-onlyで記録する。

## 1. Current Accepted State

```text
Phase 1                     : complete／accepted
Phase 1 Backup              : completed／verified
Phase 1-ex                  : in progress
Public Demo                 : accepted
Documentation RAG           : Mac／Lightning Basic／Public accepted
Existing Repository History : preserved
Pull Request #1             : merged by merge commit
Canonical Git Root          : margpa-runtime-llm
Default Branch              : main
HEAD／origin/main／remote   : 9ac8a6ba4a2120d93856356fababd130af3aa352
Former Git Staging Root     : retired／deleted after backup
Post-cutover Full Test      : 430 passed／3 deselected
Tag／Release                : none
```

## 2. Git Event Chain

```text
Existing Remote Baseline:
55e0ab854db07212dce987d1a7d7c4e43e2b63c6

Initial Integration Commit:
ce4f9ce5537aed2f34ceb0e4316685778fb063cc

Canonical Tree Alignment:
3a645f7317cd5c7f702c6004b8eb0b96d9c261cf

PR #1 Merge Commit:
9fff303175a3224963254eacddd66f9cf5112a5a

Direct main Documentation Commit:
9ac8a6ba4a2120d93856356fababd130af3aa352
```

Publication SetはSource／Target 1,053件、Source-only 0、Target-only 0、Content Mismatch 0である。廃止`docs/phases/`と旧Demo画像8件は除外し、現行Demo画像12件は保持した。

## 3. Current Git Workflow

- 小規模、決定論的、Exact Diff／Test／Sanitation／Rollbackが成立するDocs／Metadata変更は、当該Commit／Pushのユーザ明示承認がある場合だけDirect `main`候補。
- 新機能、大規模、高Risk、複数LayerまたはPhase統合はWorking Branch／Draft PR／Review／Merge Commitが原則。
- Force Push、History Rewrite、Repository再作成、Root Commit置換およびTag移動を行わない。
- Commit、Push、Merge、Tag、Release、Branch削除、Remote変更およびVisibility変更は、それぞれ個別のユーザ明示承認を要する。

## 4. Current Root／Backup

```text
Canonical Working Root:
margpa-runtime-llm

Former Staging Root:
retired／deleted by user after backup
```

Project Backupで`.venv/`を除外する場合、Canonical Root本体を変更しない。Canonical RootのBackup作業用Copyを作成し、Copy側から`.venv/`、Model、Cache、SecretおよびLocal Runtime Dataを除外してArchive化する。

## 5. Updated Stable Documents

### Current

- [Requirements Specification](../../../current/requirements/requirements_specification_ja.md)
- [Project Continuity Master](../../../current/project_continuity/project_continuity_master_ja.md)
- [Current Documentation Index](../../../current/documentation_index_ja.md)

### Shared

- [Task Role／Write Authority Policy](../../../shared/task_roles/task_role_write_authority_policy_ja.md)
- [Documentation Structure／Task Operations](../../../shared/operations/documentation_structure_and_task_operations_ja.md)
- [Task Execution Routing／Cost Control](../../../shared/operations/task_execution_routing_and_cost_control_ja.md)
- [Git Workflow Policy](../../../shared/operations/git_workflow_policy_ja.md)
- [GitHub Publication Sanitation Policy](../../../shared/operations/git_publication_sanitation_policy_ja.md)
- [Design Governance Handoff](../../../shared/design_governance_handoff/design_governance_handoff_ja.md)

### Active Phase

- [Phase 1-ex Index](../phase_index_ja.md)
- [Git Source→Target統合／公開反映／単一Git Root移行記録](operations/git_source_target_integration_publication_and_single_root_cutover_20260804035722.md)
- [Interim Design Governance Recovery Manifest](../../../shared/history/design_governance_handoff/design_governance_recovery_manifest_20260804035722.md)

## 6. Before／After Snapshot Set

### Current

- [Requirements Before](../../../current/history/requirements/requirements_specification_phase_1_ex_before_git_single_root_cutover_ja_20260804035722.md)
- [Requirements After](../../../current/history/requirements/requirements_specification_phase_1_ex_after_git_single_root_cutover_ja_20260804035723.md)
- [Project Continuity Before](../../../current/history/project_continuity/project_continuity_master_phase_1_ex_before_git_single_root_cutover_ja_20260804035722.md)
- [Project Continuity After](../../../current/history/project_continuity/project_continuity_master_phase_1_ex_after_git_single_root_cutover_ja_20260804035723.md)
- [Current Index Before](../../../current/history/index/documentation_index_phase_1_ex_before_git_single_root_cutover_ja_20260804035722.md)
- [Current Index Intermediate After](../../../current/history/index/documentation_index_phase_1_ex_after_git_single_root_cutover_ja_20260804035723.md)
- [Current Index Final After](../../../current/history/index/documentation_index_phase_1_ex_after_git_single_root_cutover_ja_20260804035724.md)

### Shared

- [Role Policy Before](../../../shared/history/task_roles/task_role_write_authority_policy_phase_1_ex_before_git_single_root_cutover_ja_20260804035722.md)
- [Role Policy After](../../../shared/history/task_roles/task_role_write_authority_policy_phase_1_ex_after_git_single_root_cutover_ja_20260804035723.md)
- [Docs Operations Before](../../../shared/history/operations/documentation_structure_and_task_operations_phase_1_ex_before_git_single_root_cutover_ja_20260804035722.md)
- [Docs Operations After](../../../shared/history/operations/documentation_structure_and_task_operations_phase_1_ex_after_git_single_root_cutover_ja_20260804035723.md)
- [Task Routing Before](../../../shared/history/operations/task_execution_routing_and_cost_control_phase_1_ex_before_git_single_root_cutover_ja_20260804035722.md)
- [Task Routing After](../../../shared/history/operations/task_execution_routing_and_cost_control_phase_1_ex_after_git_single_root_cutover_ja_20260804035723.md)
- [Git Workflow Before](../../../shared/history/operations/git_workflow_policy_phase_1_ex_before_git_single_root_cutover_ja_20260804035722.md)
- [Git Workflow After](../../../shared/history/operations/git_workflow_policy_phase_1_ex_after_git_single_root_cutover_ja_20260804035723.md)
- [Sanitation Before](../../../shared/history/operations/git_publication_sanitation_policy_phase_1_ex_before_git_single_root_cutover_ja_20260804035722.md)
- [Sanitation After](../../../shared/history/operations/git_publication_sanitation_policy_phase_1_ex_after_git_single_root_cutover_ja_20260804035723.md)
- [Design Handoff Before](../../../shared/history/design_governance_handoff/design_governance_handoff_phase_1_ex_before_git_single_root_cutover_ja_20260804035722.md)
- [Design Handoff After](../../../shared/history/design_governance_handoff/design_governance_handoff_phase_1_ex_after_git_single_root_cutover_ja_20260804035723.md)

### Phase Index

- [Phase Index Before](operations/phase_index_phase_1_ex_before_git_single_root_cutover_ja_20260804035722.md)
- [Phase Index Intermediate After](operations/phase_index_phase_1_ex_after_git_single_root_cutover_ja_20260804035723.md)
- [Phase Index Final After](operations/phase_index_phase_1_ex_after_git_single_root_cutover_ja_20260804035724.md)

## 7. SHA-512

```text
Previous Documentation Index:
fd398daf75f22ef0f5999e1a3308d1ce26f1942c5aa5b7b004e327e72457bd973155a069f7d2f5ab654d54b5725438e1c9809aa52ce1f1150e8c585dee0b33fe

Requirements Before:
71cd545dc1c0768dc0cbd27291c79175790d199698743b307a4aaaa11e8ce2124faa102d18c1588bf9e66334a4d5a543b44d5ffd8f152f99df00cc5ebbe373c1
Requirements After／Stable:
6cc4b0217e07f8da915b16f3354f8ca386140eddcce37a6bc9f609e6ed0d8d1290cb20949b1371e70a333f45dcbb01766ec619e6ed69e425b7b9c1f283f78c36

Project Continuity Before:
fe084aa3d55bdc1a5a193d2a099ac7354fec3e6f80f7c01a4642fac639551ab9846aa9f1e45719bc120c5fe0d4f2aacba2c6cb7a5cc2f13da5384e60215d34ae
Project Continuity After／Stable:
470dd27adf4e3769639b8e166a304582629e22744aef079f86382cc007ef992c62aa80a160197de8406a9d329ea893b98738d53819fe3eb8b10f2bee7b42f07e

Current Index Before:
8c7eacf6fbb8ce559bc3e31df89f6211b61cbc0a567aaa0561a3413f60fc033872024a5cac55a2bb85defaabee85bebc2085d2d99ec97922449095237e71e813
Current Index Final After／Stable:
df23048ee6914e2c15d9c6145e1f3970c5985d80682633871542824e137055e39635e569ed40a3750d1b24355450cf122becf8860d2cb4726d24ac025a0d008d

Role Policy Before:
6629590fd70e73e0d1a61195ceac9b15842fc6784c485cdcfca3644bad73f666abdc9a3b97ae8c1994c3b261ac39c0a24753ed45edf62770a7b299d1177247e3
Role Policy After／Stable:
e187351057aae34cab22b391088906044825df062b534661a330a1c1193a5ed7873be69d485b353c928d4e6bb2b3e5cf018954ea42fa59e7673cd0acb35eddba

Docs Operations Before:
4b2007fab4a655a2644454df72f9ecf9caa20131b576157948bd5cac95ce978278d4610eda6b0546af0339cba311a9fb8fee45c972bbe962aa130d9a6f4267a2
Docs Operations After／Stable:
848f49d38e557e2e89ba21f23c4e57bef08495cff85ca9df74b074b687cc54008fa238a09a91d7cb08ba3d3a0c6de0061624b918301d7bc085e3f7b755aa07c3

Task Routing Before:
679c23fcf24d1897d102f614181724f1b041b7e3360c2c5a22e87a0cec52ae00b7f362cee17bc96d85a6adb7df13d2eac77a6fe52f21daf44766a89ba154f8f6
Task Routing After／Stable:
84b21ea019d6cb28bbfb8a5cf582b1b4211c69876328189a678d0476e3e2802538e0c78c17b5aa0974863659bbcaf5f08c6fd6a077e626feb5bfabd60f0a287f

Git Workflow Before:
0051c05dfa30d91b7d41fa17efe2952a25896bea0290912ea4b462df992ab840603fb10dfba64aab93aed6a77e4306f1a5d8f19cfc274a61cbd159d67dcca509
Git Workflow After／Stable:
36adb25665cf3ae24620e7a37b8f9d8afe9c5b6cfda5066394ca8ff6326187c6b9cd152782e37de79140cdd8c2e0eeca34f8984942214dc6a85375353d46c619

Sanitation Before:
3c4f8d559469df32a0f8044978b9e3be83ce3540ee5671e8c1ead43332486347f704b472af2cad9b9f6f213a7d763b601efed4911fe8945cedbf4678ef5292c8
Sanitation After／Stable:
0145791b0cf3b4f34a3c7b76280e4ce7e37bb038885c1bdc68f5dfe2ff5c97f4b5a2cb5ca225367bcd7f6aa3655234345c8ea2710eb50a23e0d4d130fa63716d

Design Handoff Before:
e6ef806fd95f3d0620ee5f6f7854eee2cfc902c9143f9ec67c182ed4ac1a9cbe6ff92d423cef7b5e60074d2a13fb93b480b2ce06913de66455bcdec78d8d27b0
Design Handoff After／Stable:
5faba24a69834092962a53bd74fef848b5e13b93f3101bc21e78c376c28ce9c94d5b19f2873aa3760163cb7d9913b3f628cb9911515684df59765b1f52109e2d

Phase Index Before:
b321c87f376965de2914c2df6b12e9abb49fd6d104cc000e91f8d7b9e331e19fae280553b77fc28a41acd6ab761fe8c992c836849b0aaad39d81b7b47f74f916
Phase Index Final After／Stable:
50569d640bfd265f6ef48b8438a667ec1a1b03d4a763ee1950162a1b947f91ac4f4ed29028e96c2f7fc996271977effe8d107ef14d1bca2c3d6c51afd2fd0214

Git Integration／Cutover Record:
6ad589eb194a57d2e574668a5b6e318b28049632a4bf48b1b320155a30c9a0300ef04e1396fd33d5f80338e34b923286b48ac970b9ff6c3b86ef1cf1d1705d0f

Interim Recovery Manifest:
eb6ab172fb9672fb3c29f3a3a233328cf0ddcc2625bbc70833642ebc02ffee4dd5e0c8ff6c64c99abed7836ec2296dcec9382c9c2ad10e5090204cd92d87c071
```

## 8. Mutation Boundary

```text
Authorized Project Docs      : updated／added
Runtime Source               : unchanged
Config／Tests／Scripts      : unchanged
Git Commit／Push            : none in this documentation refresh
Remote                       : unchanged
Tag／Release                 : none
Branch Protection            : unchanged
Repository Visibility        : unchanged
Former Staging Root          : already retired before this docs refresh
Project Root Outside Scope   : not accessed
User-only Area               : not accessed
Task／Sub-agent Creation     : none
```

## 9. Remaining Gate

1. Phase 1-ex Final Source Freeze／Lossless Compilation／Manifest。
2. Roadmap等の必要Docs Final Refresh。
3. Phase Final Full Review／Test／Static Check／Link／Privacy／Publication Sanitation。
4. Open Finding解決または明示承認済みDeferral。
5. User Acceptance。
6. 設計統括者役からユーザーへPhase Backup取得を明示依頼。
7. Phase Final Backup／SHA-512／Restore Evidence。
8. Canonical Rootからの次回の正当なCommit／Push判断。
9. Phase 1-ex Completion Tag／Release判断。
10. Phase 2 Start Gate。

本SnapshotはPhase 1-ex完了を宣言しない。Commit／Push、Tag／ReleaseおよびExternal Mutationは、対象ごとのユーザ明示承認なしに実行しない。
