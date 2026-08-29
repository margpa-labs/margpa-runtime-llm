# Phase 8 MARGPA Development Agent Research Preview／Phase 10以降 Capability Levels予約

```yaml
document_type: planned_work_reservation
document_state: accepted_user_direction_not_started
language: ja
created_at: 2026-08-28 08:47:45 JST
public_author: Nazuna Research
project: MARGPA Runtime LLM
target_phase:
  - phase_8_research_preview_foundation
  - phase_10_or_later_capability_completion
implementation_authority: not_granted
names_are_provisional: true
```

## 1. 予約の目的

2026-08-28の対話で確定した、自律型Engineering AgentのCapability段階、Phase配置、UI、Approval／Autonomy Harness、Tool／MCP、Governance Definition、Constitution、内部Agent構成、名称変更およびHardware制約をLosslessに予約する。

本予約で確定した最終方針は次のとおりである。

- Phase 8では完成級Level 1を主張せず、UIを含むAgent基盤とResearch Previewだけを作る。
- Level 1の正式な完成・Acceptance、Level 2およびLevel 3はPhase 10以降へ送る。
- Phase 8成果は「Agentらしい入口と統治可能な骨格が存在する」段階でよい。
- Mac LocalではFake／Deterministic／限定Local Toolを中心に実証し、大規模Modelを同時稼働させる完成級Acceptanceを要求しない。
- 名称、Levelおよび内部Agent Topologyは分離し、後から安全に名称変更できる構造にする。
- 本文は計画予約であり、Phase 8開始、実装、外部接続、Tool実行、MCP接続または権限付与を許可しない。

## 2. Capability Levels

三つの名称は現時点では仮名である。Capability名は、内部で単一Agentを使うか複数Agentを使うかではなく、System全体として何を自律遂行できるかを示す。

### 2.1 Level 1

**Formal Name**

`MARGPA Development Agent`

**Short Name**

`MARGPA Dev Agent`

**Positioning／Capability**

開発実行主体。設計補助、実装、Test、修正を中心に、与えられた開発目的・Taskを正確に遂行する。

```text
Design Support
→ Implementation
→ Test
→ Fix／Repair
```

案件全体の完全自律遂行より、Boundedな開発Taskを統治された範囲で「作る」能力を先に成立させる。ただし、正式なLevel 1完成・AcceptanceはPhase 10以降とし、Phase 8ではResearch Preview／Foundationに限定する。

### 2.2 Level 2

**Formal Name**

`MARGPA End-to-End Autonomous Engineering Agent`

**Short Name**

`MARGPA EEAE Agent`

**Positioning／Capability**

一つの案件・目的を入口から出口まで自律遂行する。

```text
Consulting
→ Discovery
→ Problem Definition
→ Research
→ Requirements
→ Architecture
→ Implementation
→ Verification
→ Release
→ Deployment
```

人間からGoalを受け取った後、目的を具体化し、必要工程を組み立て、完成状態まで到達させるEnd-to-End Engineering主体である。Phase 10以降の研究・実装候補とする。

### 2.3 Level 3

**Formal Name**

`MARGPA Full-Cycle Autonomous Engineering Agent`

**Short Name**

`MARGPA FCAE Agent`

**Positioning／Capability**

完成を終端にせず、対象のLifecycleそのものを継続的に自律運営する。

```text
Consulting
→ Research
→ Design
→ Build
→ Deploy
→ Operate
→ Monitor
→ Evaluate
→ Repair
→ Improve
→ Re-architect
→ Migrate／Retire
→ Next Cycle
```

Level 2のEnd-to-Endが一案件を最初から最後まで成立させる能力であるのに対し、Level 3のFull-Cycleは、成立後の運用、評価、修復、改善、再設計、移行、廃止および次Cycleまで継続する。対象はSoftware／Applicationだけに限定せず、AI関連Engineering全般および将来登場するAI System／Architectureを含む。Phase 10以降の長期研究候補とする。

### 2.4 Capability Evolution

```text
MARGPA Development Agent
        ↓
MARGPA End-to-End Autonomous Engineering Agent
        ↓
MARGPA Full-Cycle Autonomous Engineering Agent

Development
        ↓
End-to-End Autonomous Engineering
        ↓
Full-Cycle Autonomous Engineering
```

## 3. Capabilityと内部Agent Topologyの分離

上位Capabilityを一つの巨大Agentへ固定しない。上位Agentが案件全体を管理し、Task分割やSub-Agent生成を行う構成も候補に含める。

```text
Parent／Orchestrator
 ├─ Consulting Task
 ├─ Research Task
 ├─ Architecture Task
 ├─ Implementation Task
 ├─ Evaluation Task
 ├─ Safety／Governance Task
 ├─ Operations Task
 └─ 必要に応じてSub-Agent生成
```

したがって、次を同一視しない。

```text
Capability Name
≠ Internal Agent Topology
```

内部実装は、`Single Agent`、`Multi-Task Agent`、`Parent／Child Agent`、`Dynamic Sub-Agent Generation`または`Multi-Agent Organization`を、後続の設計・実測・Governance結果に基づいて選択する。

## 4. Phase 8 Research Preview／Foundation

### 4.1 Positioning

Phase 8で作るものの作業名は、仮に`MARGPA Dev Agent Research Preview`または`MARGPA Development Agent Foundation`とする。これはLevel 1完成宣言ではない。

Phase 8 Milestoneは既存の`Governed Agentic Execution Prototype`を維持し、次のBoundedな基盤を含める。

- 通常ChatとDev Agentを切り替えるUI入口。
- 表示名から独立した安定Internal Capability ID。
- Agent Run／Step／State Machineの基礎。
- Tool Registry、Tool PortおよびTool Capability記述。
- MCP Client Adapter Portの入口。
- Approval／Autonomy Profileの基礎。
- Authorization Envelope内でGateまで不要な確認を行わない実行State Contract。
- `margpa-runtime-llm/constitution/`のMachine-readable Constitution Hook。
- Agent／Tool Governance Point。
- Generic Governance Definition Hook。
- Stop／Cancel／Step Budget／Time Budget／Retry／Audit／Evidence。
- Fake／Deterministic Toolによる、実Side Effectを伴わない実行証明。

### 4.2 Phase 8で完成扱いしないもの

- Level 1の正式完成、Production Readinessまたは汎用案件Acceptance。
- 任意のMCP Serverへ完全互換で接続するGeneric MCP Runtime。
- 多数の実Tool Adapter、OAuth、外部Service認証またはRemote Side Effect。
- Dynamic Sub-Agent生成、常設Multi-Agent組織または自己増殖的Topology。
- 長時間の完全自律運転。
- 広範なGit／Network／Deployの自動許可。
- Production-grade Planning／Replanning／Self-repair。
- 実案件を入口からReleaseまで完遂するEnd-to-End Acceptance。
- 完成後も運用Cycleを継続するFull-Cycle Acceptance。

## 5. UI Mode Switch

Codex等のMode Selectorに近いUIとして、少なくとも次を切り替え可能にする。

```text
Normal Chat
MARGPA Dev Agent
```

この切替は単なるPrompt置換ではなく、Capability、Tool可視性、State Machine、Approval Profile、Constitution View、BudgetおよびEvidence SchemaのBindingを変更するControl Surfaceとする。

将来名称を変更しても、保存済みRun、Audit、PolicyまたはProvider Bindingを壊さないよう、表示名とInternal Identityを分離する。

```yaml
capability_id: margpa.development_agent.v1
formal_name: MARGPA Development Agent
short_name: MARGPA Dev Agent
```

`formal_name`および`short_name`は変更可能な表示Metadataとし、`capability_id`、Schema RevisionおよびEvidence Identityは明示Migrationなしに変更しない。

## 6. Approval／Autonomy Harness

Harnessは段階化し、少なくとも次のProfileを比較可能にする。

### 6.1 Manual Approval

Mutationまたは外部Action前に確認する。高いHuman Controlを持つBaseline。

### 6.2 Risk-based Approval

Safe／Read-only／Bounded Actionは自走し、危険性、不可逆性、権限拡張または外部Side EffectがあるActionだけ確認する。

### 6.3 Envelope Autonomous／Gate-only Confirmation

Userが事前にExact Scope、Authority、Budget、禁止事項、Stop条件およびGateを受諾した範囲では、Gate到達まで逐次確認しない。Userの自己責任を明示するMode候補である。

ただし、これはAuthority Bypassではない。Constitution、Platform Security、OS Sandbox、Access Control、既存Authority、Secret／Privacy境界および法令はProfileによって解除しない。Envelope外、Authority不明、矛盾、重大IncidentまたはTrue Stop Conditionでは停止する。

### 6.4 Plan Only

計画と差分候補だけを作成し、Mutation／Tool Side Effectを実行しない。

Profile名、段数および既定値は後続設計で確定する。一般公開時は危険Profileを非表示または明示Opt-inにできる構造を維持する。

## 7. Tool／MCP Foundation

Phase 8では、MCPをAgent Coreへ直結せず、次の交換可能境界を予約する。

```text
Agent Plan／Step
→ Tool Port
→ Tool Registry
→ Native Tool Adapter／MCP Client Adapter
→ Permission／Constitution／Approval／Budget Gate
→ Tool Execution
→ Observation／Evidence
```

MCP関連のPhase 8対象はAdapter Port、Capability Metadata、Fakeまたは限定Reference AdapterおよびGovernance境界の実証までとする。任意Server Discovery、Remote Authentication、OAuth、Secret管理、一般Remote Side Effect、Server Marketplaceまたは完全互換性はPhase 10以降へ送る。

Toolが存在すること、接続できること、Modelが使いたいと提案したこと、Permissionがあること、Human Approvalが成立したこと、Actionが実行されたことを別Stateにする。

## 8. Governance Definitionの活用

RepositoryのDefinition Inventoryは、17 JSON Sourceから18 Logical Definitionを展開する。ARGD／DAGDだけでなく、`orchestration/`、`domain_extensions/conditional_watchdogs/`、`domain_extensions/decision_pipelines/`および`domain_extensions/ordinary/`の既存Definition群をAgent開発へ再利用する。

特に、Agent、Software Engineering、Decision Authority、Planning、Security、Incident、Operation、Completion、Orchestrationに関係するAAGD、SEGD、DCAGD、PMOGD、CDOGD、DAAGD、SPPGD、SDAGD、SDMRGD、AISGD、ACRGD、AIRGDおよびOMRGD等を候補とする。

ただし、Agent CoreへDefinition名をHard-codeしない。既存のGeneric Definition Provider／Manifest／Adapter／Compiler／Selection／Conflict Resolution境界を使用する。

```text
Agent Event
→ Generic Governance Point
→ Orchestration／Selection
→ Applicable Governance Definitions
→ Evaluation／Conflict Resolution
→ Permission／Approval／Action Resolution
```

Definitionの存在、選択、評価、推奨Action、Authority、Approvalおよび実行を分離する。GDは存在しない権限を新しく生成しない。

## 9. Constitutionの二つの境界

次を混同しない。

- `docs/project/shared/constitution/`：Codex／Claude等を用いた開発体制、Project運用、Role、Authority、Docs、Handoffおよび移植用Packageの正本候補。
- `margpa-runtime-llm/constitution/`：Phase 8以降に製品Runtimeへ埋め込むAgent／Tool専用のMachine-readable Constitution、Manifest、ViewおよびEnforcement Hook。

Phase 8 Research Previewは後者のHookと最小View検証を扱う。Constitutionの存在または読込だけでTool Authorityを発生させず、Revision、Digest、対象Role／Capability、ProviderおよびApprovalを検証する。

## 10. 規模見積りとPhase配置判断

2026-08-28時点の概算では、元のPhase 8へBoundedなResearch Previewを追加する増分は約25〜45%である。Level 1を完成級までPhase 8へ詰める場合はPhase 8全体がほぼ倍増し得る。

比較感は次のとおりである。

- Bounded Level 1 Foundation：Phase 6の約0.6〜0.9倍相当の可能性。
- Generic MCP、Dynamic Sub-Agent、汎用Planning、完全自律を含む完成級：Phase 6の約1.3〜2倍相当まで拡大する可能性。

UI Switchと名称間接化だけなら小さいが、Agent State Machine、Tool Permission、Side Effect、Constitution Enforcement、Evidence、Recovery、MCPおよび自律実行Acceptanceを一体で成立させるとPhase級の工事になる。そのため、Phase 8はPreviewに留め、正式完成をPhase 10以降へ分離する。

## 11. Hardware／Execution Strategy

現在のMacでMain Model、独立Judge、Guard、Agent PlanningおよびTool実行を常時同時Loadする完成級構成は、Memory、LatencyおよびContextの面で現実的でない可能性が高い。

Phase 8では次を優先する。

- Fake／Deterministic Tool。
- 小さなBounded Plan。
- Single Agentまたは固定Task Graph。
- Limited Local ModelまたはModelを使わないDeterministic Evaluation。
- Side Effectなし／Project内限定のExecution Proof。
- State、Authority、Stop、EvidenceおよびRecovery Contractの検証。

Server／Cloud／Home Server／大規模Model構成でのCapability AcceptanceはPhase 10以降のDeployment／Hardware Gateで行う。Declared Capabilityと当該HardwareでのVerified Capabilityを分離する。

## 12. Phase 10以降の完成境界

Phase 10以降では、Phase 8 Previewを捨てずに次へ発展させる。

1. `MARGPA Development Agent` Level 1の正式完成、実案件Acceptanceおよび安定したTool／MCP運用。
2. `MARGPA End-to-End Autonomous Engineering Agent` Level 2のDiscoveryからDeploymentまでの一案件完遂。
3. `MARGPA Full-Cycle Autonomous Engineering Agent` Level 3のOperate、Monitor、Evaluate、Repair、Improve、Re-architect、Migrate／RetireおよびNext Cycle継続。
4. Generic MCP、複数Tool Provider、Dynamic Sub-Agent、Multi-Agent Organization、Remote／Cloud RuntimeおよびCross-provider Capability Routing。
5. Capability LevelごとのAcceptance Matrix、Safety Case、Cost／Latency／Resource Budget、Incident RecoveryおよびHuman Sovereignty検証。

正式なLevel昇格は名称だけで行わず、各LevelのCapability Contract、実測Evidence、Failure BoundaryおよびUser Acceptanceを満たした場合だけ行う。

## 13. 予約状態

```text
Phase 8 Research Preview／Foundation : RESERVED
Level 1 Formal Completion             : PHASE 10 OR LATER
Level 2 EEAE                          : PHASE 10 OR LATER
Level 3 FCAE                          : PHASE 10 OR LATER
Current Implementation Authority      : NOT GRANTED
Current External Tool／MCP Authority  : NOT GRANTED
Names                                 : PROVISIONAL／RENAMABLE
```
