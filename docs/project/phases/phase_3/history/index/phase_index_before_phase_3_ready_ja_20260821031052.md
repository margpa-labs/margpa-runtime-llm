# MARGPA Runtime LLM Phase 3 Index

```yaml
document_id: phase_3_index
status: design_candidate_not_started
phase: phase_3
active_subphase: phase_3_0_entry_design
language: ja
created_at: 2026-08-21 02:05:30 JST
owner_role: プロジェクト責任者兼設計統括者役
execution_provider_candidate: claude_code
execution_role_candidate: Claude側設計統括者役
implementation_authorized: false
automation_control_state: OFF
governance_runtime_default: off
git_mutation_authorized: false
```

## 1. Current Decision

Phase 3の設計、工程分割、AcceptanceおよびClaude Code向け開始前Handoffを作成した。

これはPhase 3実装の開始、Automationの有効化、Claude Codeへの送信、Git操作、既存Phaseの完了、Phase 3の完了またはPhase 4への移行を意味しない。

```text
Phase 2                 : Phase 2-F Final Closure Pending
Phase 3 Design          : CANDIDATE／USER REVIEW PENDING
Phase 3 Implementation  : NOT STARTED
Claude Long-running Mode: OFF／USER ACTIVATION REQUIRED
Governance Runtime Mode : initial default = off
Final Closure           : Codex／User専用Gate
```

## 2. Goal

Phase 3のMilestoneは、`Auditable and Definition-ready Runtime`である。

- Runtimeの出来事を、内容の過剰保存を避けながら、Identity、Canonicalization、SHA-512およびAppend-only Evidenceで検証可能にする。
- Governance Definitionが0件でも既存Runtimeを完全動作させる。
- 未知、非対応、破損または隔離対象のDefinitionを、実行可能なDefinitionやEmpty状態と混同しない。
- `Provider → Manifest／Descriptor → Trusted Adapter → Normalized IR → Compiler → Unbound Compiled Plan`を成立させる。
- `off／observe／enforce`を共通契約として導入し、初期既定値を`off`とする。
- Phase 3では`observe`までを非介入で成立させ、`enforce`をPhase 4のBinding成立前に動作済みと見せない。
- Claude CodeによるPhase規模の長期実行とAuto-Compaction Recoveryの再現性・移植性を検証する。

## 3. Subphase Plan

```text
Phase 3-0 : Entry Gate／Baseline／Claude Recovery Bootstrap
Phase 3-A : Audit Identity／Canonical Evidence Contracts
Phase 3-B : Append-only Local Evidence Store
Phase 3-C : Definition Package／Provider／Repository State
Phase 3-D : Trusted Adapter Registry／Normalized Governance IR
Phase 3-E : Compiler／Unbound Compiled Plan／Digest Cache
Phase 3-F : Governance Mode／Configuration／Status／Local UI／Observation Hook
Phase 3-G : Integrated Verification／Automation Experiment／COMPLETE_CANDIDATE
Phase 3-H : Codex Independent Review／User Acceptance／Final Closure
```

Claude Code側の実行到達線はPhase 3-Gの`COMPLETE_CANDIDATE`返却までである。Phase 3-Hは実行してはならない。

## 4. Design Package

- [Requirements](requirements/phase_3_requirements_ja.md)
- [Architecture](architecture/phase_3_architecture_ja.md)
- [ADR](adr/phase_3_adr_ja.md)
- [Claude Automation Governance](governance/phase_3_claude_automation_governance_ja.md)
- [Definition Source Inventory](operations/phase_3_definition_source_inventory_ja.md)
- [Execution Plan](operations/phase_3_execution_plan_ja.md)
- [Acceptance Matrix](operations/phase_3_acceptance_matrix_ja.md)
- [Claude Execution Handoff](handoffs/phase_3_claude_execution_handoff_ja.md)

## 5. Source of Truth／Reading Order

Phase 3実行者は、開始許可後に次の順で読む。

1. `docs/project/current/automation_cross_provider_compaction/automation_cross_provider_compaction_governance_integrated_ja.md`
2. `docs/project/shared/task_roles/claude_side_design_governor_operating_notes_ja.md`
3. `docs/project/shared/task_roles/claude_side_long_running_automation_companion_ja.md`
4. 本Index
5. Phase 3 Requirements／Architecture／ADR
6. Phase 3 Governance／Execution Plan／Acceptance Matrix
7. Phase 3 Claude Execution Handoff
8. `docs/project/current/governance/runtime_governance_specification_ja.md`
9. `docs/public/roadmap_ja.md`のPhase 3／Phase 4境界
10. `definitions/`およびPhase 3 Definition Source Inventory
11. 開始時点の最新Phase 2-F Closure／Phase 3 Entry Evidence

Provider Memory、会話Summary、古いPhase 2予約記述またはTimestampの新しさだけを正本解決に使わない。

## 6. Entry Gates

Phase 3実装開始には、次の全条件を必要とする。

1. Phase 2-Fが完了し、Phase 2 ClosureがAcceptedされている。
2. ユーザーがPhase 3設計Packageを確認し、必要な修正を完了している。
3. ユーザーが必要なBackupを取得した事実を通知している。AIはBackup本体を読まない。
4. Claude実行Scope、Completion Line、Stable／History Write範囲およびGit禁止が確定している。
5. Claude側長期戦Modeを使用する場合、ユーザーが明示的に有効化している。
6. Codexが`READY／ARMED`を宣言する。
7. その後、ユーザーがPhase 3実装開始を明示する。

一条件でも欠ける間、Automation Control Stateは`OFF`である。

## 7. Phase Boundary

### 7.1 Phase 3に含む

- Audit／EvidenceのDomain、Port、Local Adapterおよび非介入Hook。
- Definition Package、Provider、Manifest、Descriptor、Repository State、Trusted Adapter、IR、Compiler、Unbound Plan。
- 初期値`off`のGovernance Mode契約、`observe`の非介入実行、`enforce`のUnavailable境界。
- Mac Local／Loopback／Auth-disabled環境のStatus／Settings UI。
- Empty、Unknown、Unsupported、Invalid、QuarantineおよびReference Definition Bundleの検証。
- ClaudeのPhase規模実行、Compaction Recovery、Self-repairおよびHuman BurdenのEvidence。

### 7.2 Phase 3に含めない

- Main Model入出力の停止、変換、RepairまたはRegenerateをGovernanceが実行すること。
- ARGD／DAGD／CDOGDまたはDomain ExtensionのRuntime Authority付与・実Activation。
- Action Adapter、Semantic Evaluator、Main Governance Pointの本実装。
- Guardrail／Policy／Agent／Tool／Judge／RAG Governanceの本実装。
- Remote Provider、自動URL Download、Dynamic Import、Definition由来Code実行。
- LightningへのPhase 3反映。
- Provider Memory、Raw Chain of Thought、Secret、System PromptまたはHidden Originalの保存。
- Git Commit／Push／Tag／Release、Phase 3 Final ClosureおよびPhase 4開始。

## 8. Initial Mode Decision

```text
default                    : off
off                        : provider／adapter／compiler／governance hook call 0
observe                    : validate／normalize／compile／record only; model I/O mutation 0
enforce                    : declared but unavailable until Phase 4 binding
enforce request in Phase 3 : unsupported／state mutation 0／no silent downgrade
```

`off`から`observe`への切替は明示的なLocal Configuration Applyを必要とする。`observe`から`off`へ戻した後は、以後のGenerationに対するGovernance固有CallとEvidence生成を停止する。既に作成済みのEvidenceを自動削除しない。

## 9. Current Stop Point

```text
Current Point        : Phase 3 Design Candidate Created
Current Blocker      : User Review／Phase 2-F Closure／Entry Authorization
Controller-owned Work: Design self-review and consistency validation
User Action Required : Design review and later explicit start decision
Next Safe Transition : Design Accepted → Phase 2-F Closure → Backup → READY／ARMED
```
