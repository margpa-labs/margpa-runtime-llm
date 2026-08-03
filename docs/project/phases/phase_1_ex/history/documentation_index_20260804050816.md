# Phase 1-ex Documentation Index Snapshot

```yaml
document_id: phase_1_ex_documentation_index_snapshot
snapshot: 20260804050816
state_at: 2026-08-04 05:08:16 JST
status: current_snapshot
supersedes: documentation_index_20260804045158.md
source: user_directed_agent_tool_constitution_enabled_mode_reservation
phase_complete: false
```

本Snapshotは[2026-08-04 04:51:58版](documentation_index_20260804045158.md)までの全状態を継承し、Agentおよび各Toolへ独立した「憲法有効モード」ON／OFFを設ける設計予約をAppend-onlyで追加する。

## 1. Accepted Reservation

```text
Component State             : enabled true／false
Constitution State          : constitution.enabled ON／OFF
Governance State            : off／observe／enforce
Agent／Tool Independence    : required
ON Missing Artifact         : fail-closed
OFF Meaning                 : constitution-specific processing disabled
OFF Security Meaning        : never allow-all
Public／Production Profile : may lock ON or hide toggle
Default                     : deferred
Implementation              : not started
```

## 2. Safety Boundary

Constitution OFFは、Platform Security、Sandbox、File／Tool Permission、Access Control、Human Approval、既存Authority、法令またはProject開発運用ルールを無効化しない。

Agent Constitution ONは、Tool Constitution ON、Tool Permission、Side Effect ApprovalまたはHuman Approvalを生成しない。Constitution ONでRevision、View、DigestまたはEnforcement Capabilityを解決できない場合は、黙ってOFFへFallbackせずFail-closedとする。

## 3. Updated Stable Documents

- [Requirements Specification](../../../current/requirements/requirements_specification_ja.md)
- [Project Continuity Master](../../../current/project_continuity/project_continuity_master_ja.md)
- [Basic Design](../../../current/architecture/basic_design_ja.md)
- [Runtime Governance Specification](../../../current/governance/runtime_governance_specification_ja.md)
- [Current Documentation Index](../../../current/documentation_index_ja.md)
- [Cross-project Development Governance Constitution Plan](../../../shared/operations/cross_project_development_governance_constitution_plan_ja.md)
- [Public Roadmap](../../../../public/roadmap_ja.md)
- [Phase 1-ex Index](../phase_index_ja.md)
- [Decision Record](operations/agent_tool_constitution_enabled_mode_reservation_20260804050816.md)

## 4. Before／After Snapshot Set

- [Requirements Before](../../../current/history/requirements/requirements_specification_phase_1_ex_before_agent_tool_constitution_mode_reservation_ja_20260804050816.md)
- [Requirements After](../../../current/history/requirements/requirements_specification_phase_1_ex_after_agent_tool_constitution_mode_reservation_ja_20260804050817.md)
- [Continuity Before](../../../current/history/project_continuity/project_continuity_master_phase_1_ex_before_agent_tool_constitution_mode_reservation_ja_20260804050816.md)
- [Continuity After](../../../current/history/project_continuity/project_continuity_master_phase_1_ex_after_agent_tool_constitution_mode_reservation_ja_20260804050817.md)
- [Basic Design Before](../../../current/history/architecture/basic_design_phase_1_ex_before_agent_tool_constitution_mode_reservation_ja_20260804050816.md)
- [Basic Design After](../../../current/history/architecture/basic_design_phase_1_ex_after_agent_tool_constitution_mode_reservation_ja_20260804050817.md)
- [Runtime Governance Before](../../../current/history/governance/runtime_governance_specification_phase_1_ex_before_agent_tool_constitution_mode_reservation_ja_20260804050816.md)
- [Runtime Governance After](../../../current/history/governance/runtime_governance_specification_phase_1_ex_after_agent_tool_constitution_mode_reservation_ja_20260804050817.md)
- [Current Index Before](../../../current/history/index/documentation_index_phase_1_ex_before_agent_tool_constitution_mode_reservation_ja_20260804050816.md)
- [Current Index After](../../../current/history/index/documentation_index_phase_1_ex_after_agent_tool_constitution_mode_reservation_ja_20260804050817.md)
- [Constitution Plan Before](../../../shared/history/operations/cross_project_development_governance_constitution_plan_phase_1_ex_before_agent_tool_constitution_mode_reservation_ja_20260804050816.md)
- [Constitution Plan After](../../../shared/history/operations/cross_project_development_governance_constitution_plan_phase_1_ex_after_agent_tool_constitution_mode_reservation_ja_20260804050817.md)
- [Roadmap Before](../../../../public/history/roadmap/roadmap_phase_1_ex_before_agent_tool_constitution_mode_reservation_ja_20260804050816.md)
- [Roadmap After](../../../../public/history/roadmap/roadmap_phase_1_ex_after_agent_tool_constitution_mode_reservation_ja_20260804050817.md)
- [Phase Index Before](operations/phase_index_phase_1_ex_before_agent_tool_constitution_mode_reservation_ja_20260804050816.md)
- [Phase Index After](operations/phase_index_phase_1_ex_after_agent_tool_constitution_mode_reservation_ja_20260804050817.md)

## 5. Stable SHA-512

```text
Requirements:
80172f8bac9a5d1eae20f2bf460481b0982a70dc166a5720cc0e2b792114cf2bb52835a5989a9625a9264911f1af0ddbb5ce6fe7e164d06a2aa80334fd52c473

Project Continuity:
758e79a24e101b874ce81672fc7e2565ffd4b2b2001d1def24158fc36e657f838d46fa070916ea5efb2e00ff4d5d7fb43daf217e47f3994486067f3b82a9be24

Basic Design:
11abfd14a0bc0654237f59acc4ce4b68a287860748400c4bde944587ce8761b2a0e0a24c4ebbf1e07d6ad29d3ea55b51042c39fa04049f0f6070effb9acf12d9

Runtime Governance:
dc817234714cb49fbc9cbe9e467bb8f172ae6b89f34bf516d3713f5bc983f0e2adde2d897fdce77886d4e793d25ef0f8a35e4a7181269486d6a6094aa37ac1e9

Current Index:
10de9f5735b76750894908f5f9c52f94f0e20a6c2996cb021689c82b8819c6c92ac1ffaca56f8b748d2cb3f7183396f63815155484251b50b9b1e104120639bb

Constitution Plan:
902eca499b453b6f4bfe232879f22da0ca7fb8948ffc5c1bfa614503e4838f5ac829c4ef17da7121225ae41a011ec659fde222a7f29600b2207328d52f5e8e1d

Public Roadmap:
16186f58faa148d2c3ba67cb0e27e4b3008207f5d56967de391c3033450ab41215af5e014599d274b5b406f61531a529e1ec900c7885016a487a32f142e8401d

Phase Index:
ce0b2a02c2718bca3f35c8f100d76c821d53f23594364708389f27d8ed7967847c27817a99bb27419d828dc04aead52d49242e0fa2ce5f99e8e5187d0f092139

Decision Record:
3304cc1209cd2ce0644c5b1335b925fe27c96a2d385126942b32a4585fdc9790a760c9fba4862b3d5dfaa9483394071b6566a2e806850a8fc441d1d5a620dd17
```

## 6. Mutation Boundary

```text
Authorized Project Docs     : updated／added
Runtime／Config／Tests      : unchanged
Agent／Tool Source          : unchanged
Git Commit／Push／Tag      : none at snapshot creation
Remote／Visibility         : unchanged at snapshot creation
Constitution Mode          : reserved／not implemented
```
