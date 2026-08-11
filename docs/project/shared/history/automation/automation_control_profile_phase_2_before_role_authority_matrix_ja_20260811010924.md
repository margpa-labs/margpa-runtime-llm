# Automation Control Profile

```yaml
document_id: automation_control_profile
status: design_draft
normative: true
language: ja
created_at: 2026-08-09 18:11:00 JST
updated_at: 2026-08-11 00:57:38 JST
owner_role: プロジェクト責任者兼設計統括者役
decision_authority: user
provider_neutral: true
project_neutral_core: true
default_level: manual
default_control_state: OFF
default_deny: true
```

## 1. Purpose

Automationを単純な`ON／OFF`ではなく、「どこまで自動継続、Task編成、Mutation、ReviewおよびPhase進行を許可するか」を明示する段階的Control Profileとして扱う。

Automation Profileは、自動化Capabilityの存在をAuthorityへ変換しない。各Scopeで明示された上限より先へ進まず、曖昧な場合は最も制限の強いProfileへ解決する。

## 2. Abstract Automation Levels

| Level | Meaning | Autonomous Continuation |
|---|---|---|
| `manual` | 各Actionを人間が個別に開始する | なし |
| `advisory` | Read-only分析、設計案、Handoff案を作る | Mutationなし |
| `bounded_unit` | Accepted Envelope内の一つの有界Work Unitを進める | Unit終端まで |
| `workflow` | 列挙済み複数Unitを依存順に進める | Workflow終端まで |
| `phase` | Accepted Phase Contract内でSubphaseを連結する | Phase Final Gate直前まで |
| `project` | Accepted Project Contract内で複数Phaseを編成する | 各Human GateとProject終端まで |

Level名はProject固有のRoleやProvider Commandではなく、Portableな意味契約である。`project`も無制限、自律的権限拡張またはUser Authority代替を意味しない。

### 2.1 Control State Machine

Automation Levelと、現在実行可能かを示すControl Stateを分離する。

| State | Meaning | Exit Authority |
|---|---|---|
| `OFF` | 自動連結なし。個別の人間指示が必要 | 人間が認めたPreflightへの移行 |
| `ARMED` | READY Evidence済み、Two-key Activation待ち | 双方合意だけ |
| `ON` | Accepted Envelope内で自動連結可能 | Work Unit完了、Pause、Stopまたは人間指示 |
| `PAUSED` | Resource、Review、Decisionまたは安全な中断待ち | 原因解消と必要な人間指示 |
| `EMERGENCY_STOP` | Authority逸脱、Root境界違反または重大Incident | 人間の明示的な再承認だけ |

`OFF`はRule無効化ではない。`EMERGENCY_STOP`後にAI側がCleanup、RollbackまたはState再開を自己承認しない。Phase 2-0初回Unit終了後の現在Control Stateは`PAUSED／REDESIGN`である。

## 3. Independent Capability Dimensions

Levelだけで許可範囲を決めない。各Profileは少なくとも次を別Fieldとして持つ。

```yaml
automation_profile:
  level: manual | advisory | bounded_unit | workflow | phase | project
  authorized_root: manifest_reference
  allowed_paths: []
  allowed_actions: []
  prohibited_actions: []
  task_creation:
    allowed: false
    maximum_active: 0
    maximum_replacement: 0
  delegation:
    allowed_roles: []
    subagents_allowed: false
  mutation:
    filesystem: deny
    git: deny
    external: deny
    secret: deny
    destructive: deny
  continuation:
    maximum_work_units: 0
    stop_at_review: true
    stop_at_backup: true
    stop_at_commit: true
    stop_at_phase_transition: true
  resources:
    time_limit: explicit_or_unknown
    usage_limit: explicit_or_unknown
    context_stop: required
  evidence:
    status_required: true
    review_required: true
    recovery_required: true
  expiration: explicit
  revocation: immediate
```

最終Effective ProfileはUser Decision、Constitution、Project Manifest、Phase Contract、Role View、Task EnvelopeおよびProvider Capabilityを解決し、最も制限の強い値を採用する。下位TaskやAdapterはProfileを広げられない。

## 4. Supreme Authorized Root Boundary

Automation Levelが`manual`から`project`のどこであっても、`authorized_root`と`allowed_paths`より外へ、個別のユーザー明示許可なく触れてはならない。

```text
Automation Scope
  ≠ Filesystem Scope Expansion
  ≠ External Scope Expansion
  ≠ Symlink Target Authorization
```

本境界はプロジェクト責任者兼設計統括者役、将来の上位Role、Agent、ToolおよびProvider Adapterを含む全主体に適用する。Project単位Automationであっても、Project外、Sibling、Backup、User-only Areaまたは未列挙Mountへ触れない。

Formal ExceptionはUserがExact Root、Path、Action、期間、RollbackおよびEvidenceを明示した場合だけ有効で、Task／Phase／Projectへ継承しない。

本境界は現在確認済みの最上位規則群の一つである。最上位規則を追加、変更、削除、並替えまたは例外化する指示権は、ユーザーまたはユーザーが明示指定した人間にだけある。Automation Profile、Role、Task、Agent、ToolまたはProviderは、Evidenceから最上位Rule候補を自発登録することも含め、当該権限を一切持たない。

### 4.1 Pilot Authority Precedence

Automation Pilotは通常運用Ruleとは別の有界Modeである。Effective Authorityは次で解決する。

```text
Human-defined Supreme Rules
  > Exact Accepted Automation Envelope
  > Pilot Work Unit／Role View
  > Provider Adapter
  > Ordinary Operational Defaults／Conventions
```

Accepted Envelopeが明示的に置換した通常運用の確認、Backup、Git、CheckpointまたはAction単位Gateを、AI側の判断で再適用しない。これは最上位規則を弱めるものではなく、Pilotの範囲内で下位Defaultを置換するAuthority Resolutionである。

Human-private Backup／Recovery AssetはAutomation Control PlaneのInput、Evidence、Read Target、ValidationまたはActivation Gateにしない。存在、場所、内容または状態をAI側が認識する必要もない。

## 5. Manual／Reduced Automation

Automationをいつでも下げられることを必須とする。

- Userは任意時点で`manual`またはより低い段階へ変更できる。
- Project責任者兼設計統括者役はRisk、Cost、Context、Capability不明またはNear Missを検出した場合、より低い段階への変更を提案し、安全停止できる。
- Task／Agent／Toolは自らLevelを上げられない。
- Level低下後に、旧Envelopeの残りActionを実行しない。
- `manual`はRule、Security、EvidenceまたはBackupの無効化ではない。

## 6. Promotion／Demotion

自動化範囲を広げるには、十分なEvidence、安定性、安全性、有効性およびUser Acceptanceを必要とする。

```text
Evidence accumulation
  → Safety／Effectiveness Review
  → Proposed Profile Diff
  → Backup／Recovery readiness
  → User Acceptance
  → Time-bounded promotion
  → Observation
```

Incident、Authority逸脱、Folder Boundary違反、未観測Mutation、Cost急増、Provider不整合、Recovery不成立またはHuman Gate省略を検出した場合は即時停止し、`manual`またはSafe Profileへ降格する。自動Rollback、自動Cleanup、誤生成Artifactの削除または「元に戻す」目的の追加Mutationを行わず、Exact TargetとActionを報告して人間の明示指示を待つ。

## 7. Pilot Activation Handshake

Pilot Design／Review／Validationが開始可能候補へ達した後、Exact EnvelopeとFreeze Evidenceを確定し、Pilot固有のTwo-key Activationへ進む。

```text
Design／Review／Validation complete
  → exact Envelope／Manifest／Freeze Evidence
  → final readiness preflight
  → controller ready declaration
  → user start declaration
```

Git／Commit／Push、Human-private Backupおよび通常運用CheckpointはPilot Activationと別Authorityであり、Envelopeが含めない限りGateへ追加しない。

その後、次の順序で双方合意を成立させる。

```text
プロジェクト責任者兼設計統括者役:
  「準備OK。いつでも開始出来ます。」

User:
  「ok。では開始する。」
```

前者はDesign、Capability、Scope、最上位規則、StopおよびEvidenceがその時点で合格した場合だけ宣言できる。後者を受けた瞬間をPilot Start Eventとし、Timestamp、Profile Revision、Authorized Root、Task名およびEnvelope DigestをEvidenceへ記録する。

両者の順序が逆、どちらか欠落またはReady後にStateが変化した場合は開始しない。

`ARMED`へ移行する前に、Design Review、Authorization Envelope、Authorized Root／Allowed Path、最上位規則群、Resource／Capability、Stop Condition、Evidenceおよび最初の有界Work UnitをREADY Evidenceとして固定する。一項目でも未確認なら`PAUSED`または`OFF`を維持する。

Pilot Start Event成立直後、Provider Capabilityが利用可能なら現在Task名を`プロジェクト責任者兼設計統括者役`へ変更する。失敗時はRole Identity不一致として停止する。

## 8. Provider／Project Abstraction

Normative Coreは特定Provider、Project、Repository、Phase、Task、CommandまたはAbsolute PathをHard-codeしない。

```text
Normative Core
  → Project Manifest
  → Role／Task View
  → Provider Capability Adapter
  → Runtime Execution
```

Provider AdapterはTask Creation、Naming、Messaging、Status、Wait、Interrupt、Filesystem、Shell、GitおよびExternal CapabilityをMappingする。未対応Capabilityを別操作で推測代替せず、`unsupported／manual_required／blocked`として返す。

新規Projectと既存Projectへの埋め込みでは、既存規則、Root、History、Git、Backup、RoleおよびProvider差をInventoryし、Coreを書き換えずManifestで設定する。

### 8.1 Bounded Read Capability

Portable CoreはLocal Text Readを、`Authorized Root／Exact Manifest Entry／Expected Digest／Complete Coverage／Read-only Evidence／Stop`として定義する。Shell、Executable、CommandまたはTool名はCoreへ含めない。

Provider Adapterは、Accepted Envelopeが明示するExact Manifestに対してのみ、最小Read手段をMappingできる。Shell一般、Directory探索、Glob、Git、Network、Escalation、Temporary Artifactまたは代替Commandを付随許可しない。

```text
Capability Available
  ≠ Adapter Activated
  ≠ Path Authorized
  ≠ Command Authorized
  ≠ Result Accepted
```

Adapter Failure、Digest不一致、Coverage欠落またはUnexpected Artifactの疑いでは、Scopeを広げず`PAUSED`または`EMERGENCY_STOP`候補へ移行する。

### 8.2 Permission Hardening Reservation

AI／Agent／Tool／Automationが作成したDirectory／Fileに対するPermission Hardeningは、未決定の将来研究候補である。作成主体はPermission変更Authorityを獲得しない。Permission／ACL／Owner／Group／Executable Bitの変更は独立Mutationとし、Exact Target、Before／After、Platform差、継承、Lockout Risk、Rollbackおよび人間の明示承認がない限り`deny`とする。

## 9. Multi-provider Reservation

複数Provider併用は将来候補であり、現時点では未決定・未承認である。

検討対象：

- 一つのControl Taskが別ProviderのTaskへHandoffする構成
- Providerごとの得意領域に応じたTask分解
- Cross-provider Status／Evidence／Review／Recovery
- 同一Working TreeのSingle Writer／Worktree分離
- Provider間のContext、Cost、CapabilityおよびAuthority差
- 同じ運用規則とAutomation Profileを複数Providerで維持できるか

複数Provider化を開発速度だけで採用しない。Authority、Folder Boundary、Evidence、Conflict、CostおよびRecoveryが単一Providerより悪化しないことをPilotで確認する。

## 10. Git Cadence

Git Commit／Pushは原則として次の大きな区切りで検討する。

- 復元可能な有界Milestone
- 大きなSubphase完了
- Phase完了
- Risk上、途中Checkpointが必要な変更
- ユーザーが明示指定した時点

小さなDocs更新や各Task往復ごとにCommit／Pushしない。Docs History、BackupおよびRecoveryを中間復元へ利用する。ただしDocsはGit／Backupを完全代替せず、長期間差分を肥大化させない。各Commit／Pushは従来どおりUser Explicit AuthorizationとSanitation Gateを必要とする。

Riskの高い変更前、大規模Mutation前またはAutomation Work Unit境界では、`local commit／patch／archive／working tree snapshot／manifest付きBackup`等のLightweight Checkpointを将来検討できる。ただし現在の包括許可ではなく、それぞれのMutation Authority、Exact Target、保存先、Recoveryおよびユーザー承認を必要とする。

## 11. Current Pilot Retest Profile Draft

```yaml
level: bounded_unit
control_state: PAUSED
work_unit: P2-0-WU-002
authorized_root: current_project_manifest
task_creation:
  allowed: true_after_dual_consent
  maximum_active: 1
  maximum_replacement: 0
existing_task:
  action: deny
read:
  manifest: p2-0-read-manifest-001_frozen_revision_required
  provider_adapter: codex_desktop_bounded_read_adapter_accepted_revision_required
  directory_discovery: deny
  manifest_outside_path: deny
  sandbox_escalation: deny
mutation:
  filesystem: deny
  git: deny
  external: deny
  secret: deny
  destructive: deny
continuation:
  maximum_work_units: 1
  stop_at_review: true
human_private_recovery:
  ai_awareness: prohibited
  activation_gate: false
ordinary_operational_gates:
  inherited: false
  only_if_exact_envelope_includes: true
start_handshake:
  controller_ready_required: true
  user_start_required: true
status: draft_not_active_retest
```

Project固有Path、Provider ToolおよびTask内部IDは本Profile Coreへ埋めず、Start Event時のManifest／Adapter／Evidenceで解決する。

## 12. Related Documents

- [Automation Governance Index](automation_governance_index_ja.md)
- [Pre-pilot Automation Governance Baseline](pre_pilot_governance_baseline_ja.md)
- [Automation／Governance Evidence Log](automation_governance_evidence_log_ja.md)
- [Codex Desktop Bounded Read Adapter](provider_adapters/codex_desktop_bounded_read_adapter_ja.md)
- [Research Asset Mutation Control](../operations/research_asset_mutation_control_ja.md)
- [Experimental Document-driven Task Orchestration](../operations/experimental_document_driven_codex_task_orchestration_ja.md)
- [Constitution Plan](../operations/cross_project_development_governance_constitution_plan_ja.md)
- [Constitution Research Index](../constitution/constitution_research_index_ja.md)
