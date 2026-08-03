# Phase 1-ex Documentation Index Snapshot

```yaml
document_id: phase_1_ex_documentation_index_snapshot
snapshot: 20260804043434
state_at: 2026-08-04 04:34:34 JST
status: current_snapshot
supersedes: documentation_index_20260804035722.md
source: user_directed_phase_2_pilot_governance_constitution_desktop_and_index_reservations
phase_complete: false
```

本Snapshotは[2026-08-04 03:57:22版](documentation_index_20260804035722.md)までの全状態を継承し、Phase 2 Orchestration Pilotの開始順、Project責任者、段階的Orchestration粒度、Phase 2以降の`history/index/`運用、Provider-neutralな統合憲法書およびDesktop Application化予約をAppend-onlyで追加する。

## 1. Accepted Reservations

```text
Desktop Application         : reserved／phase undecided
Phase 2 History Index       : history/index/ mandatory from first Phase 2 snapshot
Phase 2 First Work Unit     : Phase 2-0 Orchestration Pilot Design／Bootstrap
Project Responsible         : current design governance role
Initial Orchestration Unit  : one bounded work unit
Long-term Target            : phase completion／project completion
Constitution Package        : reserved／not created
Provider Portability        : Codex Desktop／Claude Code required
Agent／Tool Authority       : not granted by reservation
Phase 1-ex                  : in progress
```

## 2. Authority Boundary

設計統括者役はPhase 2以降のProject責任者としてProject全体、Cross-Phase不変条件、Task編成、Handoff、ReviewおよびRecoveryを統括する。

ユーザーは要件、Backup、Git／公開、External Service、Secret、課金、Destructive Action、User AcceptanceおよびPhase移行の最終Authorityを保持する。Task作成、Task名変更、Authority設定およびTask間通信は、ユーザーがAcceptedしたAuthorization Envelope内部だけで連結する。

## 3. Phase 2 Start Order

```text
Phase 1-ex Completion／Acceptance／Backup
  → Phase 2-0 Pilot Design
  → User-approved Authorization Envelope
  → Task Creation／Naming／Authority／Handoff
  → Bounded Work Unit
  → GO／ADJUST／STOP
  → Original Phase 2-A～2-F
```

Pilotの安定性が確認できた場合だけ、複数Unit、Subphase、Phase完了単位へ拡張する。Project完了単位は長期目標であり、自動的にAuthorityまたは自律性を拡大しない。

## 4. Phase History Index Rule

```text
Phase 1／Phase 1-ex:
  existing raw indexes remain under history/

Phase 2以降:
  docs/project/phases/<phase>/history/index/
  documentation_index_YYYYMMDDHHMMSS.md
```

Phase 1／Phase 1-exのRaw Indexを遡及移動しない。

## 5. Development Governance Constitution

Agent／Tool本格実装前に、絶対禁止、Docs、Authority、Mutation、Handoff、Review、Recovery、Backup、Git、Cost、停止条件およびIncident EvidenceをLosslessに統合した、章立て済みの開発統治憲法書を作る。

予定Rootは`docs/project/shared/constitution/`である。Folderを新規／他Projectへ配置し、Project固有Manifestを設定するだけで同等の開発体制を再構築できるPortable Packageを目標とする。

Normative CoreはProvider-neutralとし、Codex DesktopとClaude Codeの差をCapability Adapterへ分離する。憲法書の存在、配置または読込だけでAgent／ToolのAuthorityを生成しない。

## 6. Desktop Application

Desktop Application化を後続Phase予約とする。Phase、Framework、Packagingおよび対応OSは未決定である。Web／CLI／Runtime Coreの分離を維持し、Local Model、File Access、Offline、Sandbox、Secret Storage、Update、Code SigningおよびGPU Backendを後続で評価する。

## 7. Updated Stable Documents

### Current

- [Requirements Specification](../../../current/requirements/requirements_specification_ja.md)
- [Project Continuity Master](../../../current/project_continuity/project_continuity_master_ja.md)
- [Current Documentation Index](../../../current/documentation_index_ja.md)

### Shared

- [Documentation Rules](../../../shared/conventions/documentation_rules_ja.md)
- [Documentation Structure／Task Operations](../../../shared/operations/documentation_structure_and_task_operations_ja.md)
- [Experimental Document-driven Codex Task Orchestration](../../../shared/operations/experimental_document_driven_codex_task_orchestration_ja.md)
- [Phase 2 Subphase／Task Orchestration Preplan](../../../shared/operations/phase_2_subphase_and_task_orchestration_preplan_ja.md)
- [Cross-project Development Governance Constitution Plan](../../../shared/operations/cross_project_development_governance_constitution_plan_ja.md)
- [Task Role／Write Authority Policy](../../../shared/task_roles/task_role_write_authority_policy_ja.md)
- [Design Governance Handoff](../../../shared/design_governance_handoff/design_governance_handoff_ja.md)

### Phase／Public

- [Phase 1-ex Index](../phase_index_ja.md)
- [Event Record](operations/phase_2_pilot_governance_constitution_and_desktop_reservation_20260804043434.md)
- [Public Roadmap](../../../../public/roadmap_ja.md)

## 8. Before／After Snapshot Set

- [Requirements Before](../../../current/history/requirements/requirements_specification_phase_1_ex_before_phase_2_pilot_and_governance_constitution_reservation_ja_20260804043434.md)
- [Requirements After](../../../current/history/requirements/requirements_specification_phase_1_ex_after_phase_2_pilot_and_governance_constitution_reservation_ja_20260804043435.md)
- [Continuity Before](../../../current/history/project_continuity/project_continuity_master_phase_1_ex_before_phase_2_pilot_and_governance_constitution_reservation_ja_20260804043434.md)
- [Continuity After](../../../current/history/project_continuity/project_continuity_master_phase_1_ex_after_phase_2_pilot_and_governance_constitution_reservation_ja_20260804043435.md)
- [Current Index Before](../../../current/history/index/documentation_index_phase_1_ex_before_phase_2_pilot_and_governance_constitution_reservation_ja_20260804043434.md)
- [Current Index Intermediate After](../../../current/history/index/documentation_index_phase_1_ex_after_phase_2_pilot_and_governance_constitution_reservation_ja_20260804043435.md)
- [Current Index Final After](../../../current/history/index/documentation_index_phase_1_ex_after_phase_2_pilot_and_governance_constitution_reservation_ja_20260804043436.md)
- [Documentation Rules Before](../../../shared/history/conventions/documentation_rules_phase_1_ex_before_phase_2_pilot_and_governance_constitution_reservation_ja_20260804043434.md)
- [Documentation Rules After](../../../shared/history/conventions/documentation_rules_phase_1_ex_after_phase_2_pilot_and_governance_constitution_reservation_ja_20260804043435.md)
- [Orchestration Before](../../../shared/history/operations/experimental_document_driven_codex_task_orchestration_phase_1_ex_before_phase_2_pilot_and_governance_constitution_reservation_ja_20260804043434.md)
- [Orchestration After](../../../shared/history/operations/experimental_document_driven_codex_task_orchestration_phase_1_ex_after_phase_2_pilot_and_governance_constitution_reservation_ja_20260804043435.md)
- [Phase 2 Preplan Before](../../../shared/history/operations/phase_2_subphase_and_task_orchestration_preplan_phase_1_ex_before_phase_2_pilot_and_governance_constitution_reservation_ja_20260804043434.md)
- [Phase 2 Preplan After](../../../shared/history/operations/phase_2_subphase_and_task_orchestration_preplan_phase_1_ex_after_phase_2_pilot_and_governance_constitution_reservation_ja_20260804043435.md)
- [Docs Operations Before](../../../shared/history/operations/documentation_structure_and_task_operations_phase_1_ex_before_phase_2_pilot_and_governance_constitution_reservation_ja_20260804043434.md)
- [Docs Operations After](../../../shared/history/operations/documentation_structure_and_task_operations_phase_1_ex_after_phase_2_pilot_and_governance_constitution_reservation_ja_20260804043435.md)
- [Role Policy Before](../../../shared/history/task_roles/task_role_write_authority_policy_phase_1_ex_before_phase_2_pilot_and_governance_constitution_reservation_ja_20260804043434.md)
- [Role Policy After](../../../shared/history/task_roles/task_role_write_authority_policy_phase_1_ex_after_phase_2_pilot_and_governance_constitution_reservation_ja_20260804043435.md)
- [Design Handoff Before](../../../shared/history/design_governance_handoff/design_governance_handoff_phase_1_ex_before_phase_2_pilot_and_governance_constitution_reservation_ja_20260804043434.md)
- [Design Handoff After](../../../shared/history/design_governance_handoff/design_governance_handoff_phase_1_ex_after_phase_2_pilot_and_governance_constitution_reservation_ja_20260804043435.md)
- [Roadmap Before](../../../../public/history/roadmap/roadmap_phase_1_ex_before_phase_2_pilot_and_governance_constitution_reservation_ja_20260804043434.md)
- [Roadmap Intermediate After](../../../../public/history/roadmap/roadmap_phase_1_ex_after_phase_2_pilot_and_governance_constitution_reservation_ja_20260804043435.md)
- [Roadmap Final After](../../../../public/history/roadmap/roadmap_phase_1_ex_after_phase_2_pilot_and_governance_constitution_reservation_ja_20260804043436.md)
- [Phase Index Before](operations/phase_index_phase_1_ex_before_phase_2_pilot_and_governance_constitution_reservation_ja_20260804043434.md)
- [Phase Index After](operations/phase_index_phase_1_ex_after_phase_2_pilot_and_governance_constitution_reservation_ja_20260804043435.md)
- [Constitution Plan Initial Snapshot](../../../shared/history/operations/cross_project_development_governance_constitution_plan_phase_1_ex_initial_ja_20260804043435.md)

## 9. SHA-512

```text
Previous Documentation Index:
c288d6d92583d5609e1f7497572548bbfcbdcf850bb479b287569e85c7b849738e5be6d4ddbe2f7ef2451bb227ce46e7a99e5cf32abc8f8b47923150d051d896

Requirements Before:
6cc4b0217e07f8da915b16f3354f8ca386140eddcce37a6bc9f609e6ed0d8d1290cb20949b1371e70a333f45dcbb01766ec619e6ed69e425b7b9c1f283f78c36
Requirements After／Stable:
45a67fc0bbc67b549a9ec45b60893e583a216cc40c7c426544bd10b323c94821d39b44952299320729cb19e6d0ce249ed6e16c88576addd83eceb5b7a5c1fa59

Continuity Before:
470dd27adf4e3769639b8e166a304582629e22744aef079f86382cc007ef992c62aa80a160197de8406a9d329ea893b98738d53819fe3eb8b10f2bee7b42f07e
Continuity After／Stable:
8c411c7033bb6cac5d771cfa8d8df5e0fd76471a738fd2a4bf454e313a49dbeeb549b55a5597fa7af2ab59fb1157e3d42f4fc02d039481eccf50bacb335d4836

Current Index Before:
df23048ee6914e2c15d9c6145e1f3970c5985d80682633871542824e137055e39635e569ed40a3750d1b24355450cf122becf8860d2cb4726d24ac025a0d008d
Current Index Intermediate After:
451607cfd89a24364bca1cc1e6fcea6e6a2e0bd7ff9556ecf003bf2f50160a90a57262b3430ac7be0063b6cadf08276da483fd1901d2fbea8eea70ea3070e56c
Current Index Final After／Stable:
44cc5ca46278403c0f62ede4c6cb9e6afe18ba601bc76fbd94de7d7f09e5ca7b61b36b84ba292175bd060ac14d3268aa0fe6b50b67ee84ebf7473e4dbc1e26cb

Documentation Rules Before:
014c8ed93d6b70139ff184a42760acb8b406bcf8c3c0e2fd4a43761f4d9cc2aa61857c81bfebabf3bdaa0d9c48f2a732e84d989a49a7205c33d8eaf73415c818
Documentation Rules After／Stable:
61d7e733a5784d688ffd9134a8d49d49cd1f2dc1f30249e6666c1aa0c0b553965b78fc8dfedad1dd2bc646498cc9f46aff865483d1010e25a8bc6681c6d74acb

Orchestration Before:
c1397b3b4f539d799a5ca6720a14ae3f1bd0c6dbcd4abf6e767974594d2808369fbfb1fdb687943566e4b1e0057738c749aae9b70fa89c0a9a8332aaa2f52d1d
Orchestration After／Stable:
f6805c3d5dbafb0aeffbafca7f8c16d1c5c7c93db610d5d5cf85ca727c9deb5565338020743da14245d72dd5a391c6668485b5e635ad4e0ac8ad19ae9e39af88

Phase 2 Preplan Before:
2366ed5274a1692fb47cdd3ce6ba931bea0bafdcf6bc998b6ca9d94385230f35722e6638928c415e8e2a1ff435e14defdfdcd7605dad2a314dacda14a745afeb
Phase 2 Preplan After／Stable:
841587cce214bd29e4c13ffa22b320789c1ecc0f06995b97f3cae25ed449a2ed6ec401ffbd045fe44e7ed295b7ad2be41d534bd1cca02b10fd44eee769b78af9

Docs Operations Before:
848f49d38e557e2e89ba21f23c4e57bef08495cff85ca9df74b074b687cc54008fa238a09a91d7cb08ba3d3a0c6de0061624b918301d7bc085e3f7b755aa07c3
Docs Operations After／Stable:
22066e1f479cdd3b959d377c1a75591468b4ada7dcbdf7d4036129e1b19d32895c0160b525e0f3bec2580a5a35296af205cc9bbe56f803f2d5cd9371c0cac2e8

Role Policy Before:
e187351057aae34cab22b391088906044825df062b534661a330a1c1193a5ed7873be69d485b353c928d4e6bb2b3e5cf018954ea42fa59e7673cd0acb35eddba
Role Policy After／Stable:
2fe5ef2b45b1e9b857e8629c7e99539c33b72fb835da37a8c2ef859a67efb916693a43074e93806740f37d9d97ef8d92ca9eb183c6497822ee32bf0827157557

Design Handoff Before:
5faba24a69834092962a53bd74fef848b5e13b93f3101bc21e78c376c28ce9c94d5b19f2873aa3760163cb7d9913b3f628cb9911515684df59765b1f52109e2d
Design Handoff After／Stable:
abe8481a21ce9c5e1c948b56437f712800ac058db2318970877f09827e80ee96aaa539be0ae3a904b863bb0a948d7d619d48c662dcd546d034f9524101eeb3b4

Roadmap Before:
e4dd2139eae776dcb36c7c21cc7360e0c8cc43250c80bbdf749937682da5ddcdf46a255aea667368700c60bed81927308bc44b86dd67cea770ad29f7a51083bf
Roadmap Intermediate After:
a29d3d38ef5399df02812263364992c4e8131ecbecf91f72eae6b8189d771ebc2e8b796135720e721e3e845751341023edcd601a74c4bd2d80cd283d75dd54c8
Roadmap Final After／Stable:
aa10f7226aa95e1f60e08a3ca63024df44e4942dbd6c7ac4d8f37278253d6cafc038f418c2d5aa3bb0eb72e44336662b84ffad2163973ac853d0c6818ec34bff

Phase Index Before:
50569d640bfd265f6ef48b8438a667ec1a1b03d4a763ee1950162a1b947f91ac4f4ed29028e96c2f7fc996271977effe8d107ef14d1bca2c3d6c51afd2fd0214
Phase Index After／Stable:
3e7c18ab393ac6a558c2c3dbfccc1c20b96011fd128de9821dc3e2e0a4ec9990520caa96016f07b3531761062c43506516f8ca76cef6038e7e7e9f2d6455e949

Constitution Plan／Initial Snapshot:
9a05ecd7ca9b46949a629d4ff1006e782052f21a21061ee09ba0d5d7a5d0597e2831d654064455834a19605327a2fd3fce70396dd11cee38dd690e7cae96927a

Event Record:
b9eb676c7ce47d27bb39b349b31072ba72cd382f96da4abe47dba5f13061d12e587559e34a86c05f2d995a80cca7f116ee0628992988d09329ce6b7b6dc2c61f
```

## 10. Mutation Boundary

```text
Authorized Project Docs    : updated／added
Runtime／Config／Tests     : unchanged
Git Commit／Push／Tag     : none
Remote／Visibility        : unchanged
Task／Sub-agent Creation  : none
Constitution Folder       : not created
Desktop Source            : not created
Phase 2                   : not started
```

## 11. Remaining Gate

本予約はPhase 1-exの残作業順を変えず、Phase 2開始後の最初のWork Unitを明確化する。Phase 1-ex Final Lossless、Phase Final Review、User Acceptance、Backup、最終Git反映およびPhase 2 Start Gateは引き続き必要である。
