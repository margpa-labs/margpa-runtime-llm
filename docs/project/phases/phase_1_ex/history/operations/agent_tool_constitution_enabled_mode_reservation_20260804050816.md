# Agent／Tool Constitution Enabled Mode予約

```yaml
document_id: agent_tool_constitution_enabled_mode_reservation
status: accepted_design_reservation
normative: false
phase: phase_1_ex
language: ja
created_at: 2026-08-04 05:08:16 JST
owner: 設計統括者役
decision_authority: user
rag_default: false
```

## 1. Decision

将来のAgentおよび各Toolに、Component本体のON／OFFとは別に「憲法有効モード」ON／OFFを設ける。

```text
component.enabled
constitution.enabled = ON／OFF
governance.mode = off／observe／enforce
```

Agentと各Toolは独立したConstitution状態を持つ。

## 2. ON

- Accepted Constitution Revisionを解決する。
- Role／Phase／Task／Component別Constitution Viewを解決する。
- View Digest、適用Rule ID、Authority、Stop ConditionおよびEvidence Contractを検証する。
- Agent ActionまたはTool Call前後の定義済みGovernance Pointで適用する。
- Revision、View、DigestまたはEnforcement Capabilityが不足する場合はFail-closedとする。
- 必要Artifact不足時に、黙ってOFFへFallbackしない。

## 3. OFF

- Constitution ViewをLoadしない。
- 憲法固有Evaluationおよび憲法固有Evidenceを生成しない。
- Governance比較、Ablationおよび研究Baselineとして使用できる。
- `allow all`として扱わない。
- Platform Security、Sandbox、File／Tool Permission、Access Control、Human Approval、既存Authority、法令およびProject開発運用ルールを無効化しない。

## 4. Composition

Agent Constitution ONは、Tool Constitution ON、Tool Permission、Side Effect ApprovalまたはHuman Approvalを生成しない。各Toolで独立して状態とAuthorityを解決する。

次を黙って正常扱いしない。

```text
Agent OFF／Agent Constitution ON
Tool OFF／Tool Constitution ON
Constitution ON／View Unresolved
Constitution ON／Digest Mismatch
```

結果は`invalid_combination`、`not_applicable`またはFail-closed Errorとして明示する。

## 5. Profile／UI Boundary

Research／Developer Modeでは、AuthorityとProfileが許可する場合にON／OFF比較を提供できる。一般公開、Productionまたは安全性固定ProfileではON固定またはToggle非表示にできる。

Default値、変更Authority、UI表示および公開範囲は後続設計で確定する。Toggleの存在はAuthority昇格、Security Boundary回避、絶対禁止事項停止またはProject運用ルール停止を意味しない。

## 6. Current Boundary

本記録は将来設計の予約である。Source、Config、UI、Agent、Tool、Constitution FolderまたはCompilerは実装していない。

## 7. Related Documents

- [Cross-project Development Governance Constitution Plan](../../../../shared/operations/cross_project_development_governance_constitution_plan_ja.md)
- [Requirements Specification](../../../../current/requirements/requirements_specification_ja.md)
- [Basic Design](../../../../current/architecture/basic_design_ja.md)
- [Runtime Governance Specification](../../../../current/governance/runtime_governance_specification_ja.md)
- [Project Continuity Master](../../../../current/project_continuity/project_continuity_master_ja.md)
- [Public Roadmap](../../../../../public/roadmap_ja.md)
