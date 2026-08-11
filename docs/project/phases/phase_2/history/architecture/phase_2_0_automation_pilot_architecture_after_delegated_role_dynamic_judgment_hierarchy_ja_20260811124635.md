# Phase 2-0 Document-driven Orchestration Pilot Architecture

```yaml
document_id: phase_2_0_automation_pilot_architecture
status: design_draft
phase: phase_2
subphase: phase_2_0
language: ja
created_at: 2026-08-04 11:17:44 JST
updated_at: 2026-08-11 12:46:35 JST
owner: プロジェクト責任者兼設計統括者役
project_gate_owner: プロジェクト責任者兼設計統括者役
provider_neutral_core: true
runtime_source_change: false
```

## 1. Architecture Goal

本Architectureは、DocsをSource of Truthとし、独立Taskの作成、Handoff、Acknowledgement、Status、Review、Follow-up、StopおよびRecoveryを、明示的なAuthority Envelopeの下で状態機械とEvidenceに変換する。

実行プロバイダのToolシーケンスをProjectのNormative Ruleにせず、次の二層へ分ける。

```text
Provider-neutral Orchestration Contract
  → Provider Capability Adapter
     → Codex Desktop Task Capability
     → future Claude Code Capability
     → manual_required fallback
```

## 2. System Boundary

### 2.1 Included Control Plane

```text
Current Documentation Index
Project Continuity Master
Project Responsibility Handoff／Recovery
Design Governance Handoff／Recovery
Shared Rules／Authority／Cost／Git
Phase 2 Index
Phase 2-0 Requirements／Architecture／Envelope／Plan／Handoff
Status／Review／Evidence
```

### 2.2 Excluded Data Plane

- LLM Inference Runtime。
- Conversation Persistence。
- Web UI／API。
- Model、RAG、Agent、ToolおよびGovernance Runtimeの実装。
- GitHub、Lightningその他External ServiceのMutation。

Pilotの開発運用Control Planeと、MARGPA Runtimeの製品Data Planeを混同しない。

## 3. Roles

### 3.1 User

- Projectの最終Decision Authority。
- Authorization Envelope Acceptance。
- Task作成、Write拡張、Git／External／Secret／DestructiveおよびPhase移行のGate。
- Pilot GO／ADJUST／STOPのFinal Acceptance。

### 3.2 プロジェクト責任者兼設計統括者役

- Cross-Phase不変条件、Pilot State、Task編成、Human Gate、RecoveryおよびFinal Reviewの調整。
- Accepted Envelopeの範囲外を実行しない。
- Pilot Requirements、Architecture、Envelope Draft、Handoff、Technical ReviewおよびPhase 2 Design Boundary。
- Phase 2設計担当者役が返すDesign AssessmentのReview。
- Task作成AuthorityをRole名から推測しない。
- Project ResponsibilityとDesign GovernanceのRecoveryを分離して相互参照する。
- 最上位Folder境界、User Gateおよび運用ルールから免除されない。

### 3.3 Phase 2設計担当者役候補

- 初回Work UnitではRead-only。
- Docs-only Recovery、Authority AcknowledgementおよびPilot Design Assessmentだけを返す。
- File、Git、External、Secret、Task作成およびSub-agent使用は禁止。
- Accepted Role Viewの範囲内では、Actionごとの最高責任者確認を行わず、設計判断、局所Review、Finding整理および完了報告を自律実行する。
- 後続Write Pilotでは、別Envelopeで委譲された場合に限り、Assigned Phase内で実装担当へのAccepted Design伝達、Reviewおよび再作業指示を担う。

### 3.4 Phase 2実装者役

Phase 2-0初回Work Unitでは作成しない。後続のWrite PilotまたはPhase 2-A以降で、別Envelopeとユーザー承認により候補とする。作成後はAccepted Designと担当Source／Test Scope内の実装、局所修正、再Test、担当内EvidenceおよびStatusを自律判断し、Routine ActionごとにPhase Designerまたは最高責任者役へ確認しない。

### 3.5 Layered Authority／Role-local Judgment

Role分離は全判断を最高責任者役へ集中させることではない。全Role／Taskは、最高責任者役へ与えられたProject Authorityの内側で、自Roleへ委譲された役割、実行権限、Docs Authority、Accepted DesignおよびWork Unitの交差内を都度判断する。

```text
User
  → 最高責任者役：Project／Cross-Phase／委譲／Final Review
     → Phase Designer：Assigned Phase設計／実装伝達／局所Review
        → Implementer：Accepted Design内実装／Test／局所修正
```

問題なくScope内を進行するRoutine Actionは各Roleで閉じる。例外、重大問題、Scope外、規則Conflict、Cross-Phase影響、Security／Privacy／Recovery Risk、Resource／Provider異常または定義済みGateだけを直属上位へEscalateする。Automationはこの階層判断を機械的に固定せず、承認済み到達線内で連結する。

## 4. Logical Components

### 4.1 Phase State Registry

Phase、Subphase、Work Unit、Role、Current StateおよびAccepted Evidenceの論理正本。Phase IndexがHuman-readable正本、将来のManifestがMachine-readable派生候補となる。

### 4.2 Authorization Envelope Resolver

Draft、Accepted Revision、Expiration、Revocation、Allowed Capability、Task上限およびHuman Gateを解決する。設計書からAccepted状態を推測しない。

### 4.3 Provider Capability Adapter

```text
create_task
set_task_title
deliver_initial_handoff
send_follow_up
observe_status
wait
interrupt
pin／archive
```

各Capabilityを`available／unavailable／manual_required／unknown`とし、Provider固有Tool、制約、User-visible効果およびFailure ContractにMappingする。

### 4.4 Handoff Resolver

Handoff Path、SHA-512／Digest、Reading Order、Role、Scope、Expected Output、StopおよびExpirationを一つの契約として解決する。

### 4.5 Single Writer Lease

Write Task、Path Scope、Start、Expiration、ReleaseおよびConflictを保持する。初回Read-only Work UnitではLeaseを取得しない。

### 4.6 Evidence Recorder

Task作成、Acknowledgement、Status、Review、Follow-up、Human Gate、Stop、Recovery、CostおよびNear MissをAppend-onlyで保持する。将来のMachine-readable EvidenceはHuman-readable Recordの意味を勝手に拡張しない。

### 4.7 Review Gate

```text
accepted
adjust_required
rejected
paused_resource_limit
stopped_authority
stopped_capability
stopped_conflict
```

Reviewは実装成果だけでなく、Authority、Files、Git／External State、Cost、RecoveryおよびEvidenceを確認する。

### 4.8 Automation Profile Resolver

`manual／advisory／bounded_unit／workflow／phase／project`と独立Capability DimensionからEffective Automation Profileを解決する。User Decision、Constitution、Project Manifest、Phase Contract、Role View、Task EnvelopeおよびProvider Capabilityのうち、最も制限の強い値を採用する。

### 4.9 General Hard-code Prohibition／Project Manifest／Provider Adapter

General Hard-code ProhibitionのNormative本文は[Task Role／Write Authority Policy](../../../shared/task_roles/task_role_write_authority_policy_ja.md)を参照する。本Architecture固有の分離として、Authorized Root、Docs Source、Role MappingおよびGit／Backup境界はProject Manifest、Task作成・命名・Messaging・Wait等はProvider Adapterへ置く。Runtime Manifest／Envelope／Role View／Config／FreezeによるExact BindingはCoreへの固定埋込みと区別する。

現在の許可範囲内の抽象化方法、不可避性、EvidenceおよびTestは、その時点の最高責任者役が都度判断する。Codex／Claude Code等のMulti-providerは将来候補であり、初回Pilotでは単一Providerに限定する。

### 4.10 Control State Resolver

Automation Levelと独立して`OFF／ARMED／ON／PAUSED／EMERGENCY_STOP`を解決する。入力はUser Decision、Accepted Envelope、READY Evidence、Authorized Root、Provider Capability、Resource、IncidentおよびExpirationである。

```text
Level Resolver    : どこまで自動化できるか
State Resolver    : 今その範囲を実行できるか
Authority Resolver: 実際に何をしてよいか
```

三者を合成し、最も制限の強い結果をEffective Contractとする。

### 4.11 Safety Enforcement Adapter Reservation

Path Allowlist、外部Directory Read-only、隔離Workspace、Mutation Inventory、許可Root外Diff検知、Tool WrapperおよびPermission Hardeningは、Normative Coreから分離した将来Adapter候補とする。現時点では未実装・未承認であり、初回Pilotの成立条件として仮定しない。

### 4.12 Bounded Read Capability Resolver

Local Documentation Readを次のProvider-neutral Contractへ正規化する。

```text
Authorized Root Resolver
  → Exact Read Manifest Resolver
  → Digest／Coverage Contract
  → Provider Read Adapter
  → stdout-only Evidence
  → Recovery Assessment
```

CoreはExecutable、Command、ShellまたはUIを指定しない。Exact Root、Exact Entry、Expected Digest、Complete Coverage、Mutation禁止、EvidenceおよびStopだけを定義する。

### 4.13 Exact Read Manifest Resolver

Read対象の単一正本をPhase固有Manifestとして解決する。Requirements、Envelope、PlanおよびHandoffはManifest ID／Revisionを参照し、Path一覧を複製しない。Freeze時はEntry Digest、Ordered Path-set Digest、Manifest DigestおよびHandoff DigestをDetached Receiptへ固定する。

### 4.14 Codex Desktop Bounded Read Adapter

Codex固有Adapterは、Exact Authorized Rootを`workdir`へ固定し、Manifest Entryに対するLine Count、SHA-512および連続Page Readだけを許可候補へMappingする。Shell一般、Directory探索、Pipe／Redirection、Git、Network、Sandbox EscalationまたはArtifact生成はMappingしない。

このAdapterはNormative Coreではなく、別Providerへ再利用しない。利用可能であることとAccepted Envelope内で有効であることを分離する。

### 4.15 Task Registration Resolver

```text
task_id_returned
  ≠ registration_observable
  ≠ exact_metadata_applied
  ≠ exact_metadata_verified
  ≠ handoff_delivered
```

ProviderのEventual Consistencyを固定Sleepまたは無制限Retryへ変換しない。Provider Read／WaitでRegistrationを観測し、部分失敗時は新Taskを実行させず`PAUSED`へ戻す。

### 4.16 Pilot Authority Resolver

Automation PilotのEffective Authorityは、通常運転と共通のRole／Docs Authorityへ、承認済み到達線とWork Unit連結の差分だけを重ねて解決する。

```text
Human-defined Supreme Rules
  → Exact Accepted Pilot Envelope
  → Common Role／Docs Authority Matrix
  → Pilot Work Unit／Role View
  → Provider Capability Adapter
```

Accepted Envelope内の`ROLE_ALLOWED` ActionへActionごとの確認を再適用しない。一方、Envelopeは共通Role／Docs Authority、最上位規則、Authorized Root、Human-only Amendment、既存Stableへのユーザー明示要件、Evidence／StopまたはEnvelope外禁止を上書きできない。

Human-private Backup／Recovery AssetはControl PlaneへのInput、Evidence、Read TargetまたはActivation Gateにしない。

Role ViewはAction Authorityとは別に、共通Matrixから狭めたDocument Authorityを保持する。

```text
Document Authority Resolver
  Role Document Ceiling
    ∩ Envelope Document Classes／Exact Paths
    ∩ Work Unit Document View
    ∩ Provider Read／Write Capability
```

Resultは`READ／CREATE_NEW／APPEND_NEW／EXISTING_WRITE_USER_EXPLICIT／REVIEW_ONLY／DENY`のいずれかへ解決する。Filesystem Write CapabilityまたはDocs Read AuthorityをStable Write Authorityへ暗黙変換しない。既存History Mutationは全RoleでDenyとし、新規Appendと分離する。

Work Unit Artifactは固定Packageとして一律生成しない。当該Docs Authorityを委譲されたRole／Taskが、共通Docs／運用規則、Work Unit、Role／Task境界、State Transition、Mutation Risk、Review／Human Gate、Audit／Recovery、Provider Capability、情報Loss、CostおよびContextから必要Artifactだけを都度判断する。最高責任者役はCross-Role対象、競合、委譲境界およびGateを調整する。

IndexはNavigation／Recovery入口、Handoffは責任／Authority／入力／次Actionの移転、StatusはState永続化、Review／Acceptanceは独立判定、Evidenceは監査／復元／再現性が必要な場合だけ作る。一つのArtifactが複数責務をLosslessに満たせる場合は統合し、不要Artifactを作らない。Role／Task間の移転ArtifactにだけFrom／Toを記録する。

Project Bindingと上位Roleからの委譲が許可Document Root／Classを与え、当該Docs Authorityを持つRoleが必要な対象をExact Pathへ固定する。最高責任者役はCross-Role対象または競合を調整する。Automation側で別の規則または機械的Resolverを作らず、この判断は既存Stableへの直書き、既存History Mutation、許可外Document ClassまたはAuthorized Root外へのAuthorityを生成しない。

## 5. State Machine

```text
DESIGN_DRAFT
  → CAPABILITY_PREFLIGHT_PASSED
  → ROLE_AUTHORITY_FROZEN
  → DESIGN_FROZEN
  → AWAITING_USER_AUTHORIZATION
  → AUTHORIZED
  → TASK_CREATED
  → AWAITING_ACKNOWLEDGEMENT
  → ACKNOWLEDGED
  → RUNNING
  → REVIEW_PENDING
  → ACCEPTED／ADJUST_REQUIRED／STOPPED／PAUSED_RESOURCE_LIMIT
```

上記Work Unit State Machineの外側にAutomation Control Stateを置く。

```text
OFF → ARMED → ON → PAUSED／OFF
                 → EMERGENCY_STOP
```

`EMERGENCY_STOP`からの自動復帰は禁止する。`PAUSED`からの再開も、停止原因、Envelope、ResourceおよびEvidenceを再確認する。

### 5.1 Invalid Transition

- `DESIGN_DRAFT → TASK_CREATED`。
- `TASK_CREATED → RUNNING`でAcknowledgementを省略。
- `RUNNING → ACCEPTED`でReviewを省略。
- `STOPPED → RUNNING`を旧Authorizationのまま再開。
- `READ_ONLY → WRITE`を暗黙拡張。

Invalid TransitionはFail-closedで拒否し、新しいUser GateまたはEnvelope Revisionを必要とする。

## 6. Adjusted Retest Work Unit Flow

```text
Project Responsibility／Design Governance
  → Preserve P2-0-WU-001 and old Task as immutable evidence
  → Review Role Authority Matrix／Role View／draft-4／Read Manifest／Provider Adapter
  → Preflight bounded local read without creating a Task
  → Freeze exact Matrix／Role View／Manifest／Envelope／Handoff／Adapter and Detached Receipt
  → User accepts exact draft-4／Role View／Freeze Receipt／one new Task scope
  → Controller declares READY／ARMED
  → User declares Start／ON
  → Create one new independent Task for P2-0-WU-002
  → Observe Provider registration
  → Set and verify exact Task title
  → Deliver frozen bootstrap handoff
  → Receive Authority Acknowledgement
  → If mismatch: STOP
  → Request one bounded-read recovery assessment
  → Read 18 Manifest Entries with Digest／Coverage Evidence
  → Receive Status
  → Phase Designer local Review／completion report
  → Design Governance／Project Responsibility Review and Task completion proposal
  → User Final Decision
```

後続Write Pilotでは、`Implementer完了報告 → Phase Designer Review／必要時再作業 → Phase Designer局所Accepted → 最高責任者役Review／Task完了判定案 → User Acceptance`を標準連鎖とする。初期はTask／有界Work Unit単位で実証し、成立後にSubphase、Phase、Project単位へ段階的に拡張する。

Taskの作成、Provider登録、命名、Read-backおよびHandoffは別Stateとして扱う。Taskだけ作成され、登録、命名またはHandoffが失敗した場合は、未初期化Taskとして記録し、自動で作業継続、再作成または旧Task代替を行わない。

Capability PreflightはTaskを作成しないRead-only Gateであり、READY Evidenceへ含める。Preflight後にProvider契約、対象Project、Envelope RevisionまたはHandoff Revisionが変化した場合は失効し、Task作成前に再実施する。

## 7. Concurrency Model

```text
Read-only Parent Review + Read-only Child Assessment : allowed
Parent Write + Child Read-only                         : avoid during state freeze
Parent Write + Child Write                            : prohibited
Multiple Child Writes                                 : prohibited
```

初回Work Unitでは新TaskにWrite Authorityを与えない。後続Write PilotはSingle Writer Lease、Exact Path、Before Snapshot、StatusおよびReviewを別途設計する。

## 8. Evidence Model

```yaml
experiment_id: string
work_unit_id: string
envelope_id: string
envelope_revision: string
phase: string
subphase: string
provider: string
task_role: string
task_name: string
handoff_path: string
handoff_digest: sha512
read_manifest_id: string
read_manifest_digest: sha512
ordered_pathset_digest: sha512
read_coverage: mapping
provider_adapter_revision: string
state_before: string
state_after: string
capabilities: mapping
read_scope: list
write_scope: list
files_created: list
files_modified: list
files_deleted: list
git_state: string
external_state: string
acknowledgement: mapping
status: mapping
review: mapping
human_gate: mapping
resource_observation: mapping
incident: list
near_miss: list
classification: list
recovery: mapping
```

Credential、Private Key、個人Email、個人Pathまたは不要なTask内部識別子を収集しない。

## 9. Failure／Stop Architecture

| Failure | Required State | Action |
|---|---|---|
| User Gate未成立 | awaiting_user_authorization | Taskを作成しない |
| Capability不明／不足 | stopped_capability | manual requiredまたは停止 |
| Manifest不存在／Digest不一致／Coverage欠落 | stopped_capability | 代替探索せず停止 |
| Authority Acknowledgement不一致 | stopped_authority | Follow-upで再確認。Mutation禁止 |
| Scope外Action候補 | stopped_authority | 証跡固定、ユーザーへEscalate |
| Write Conflict | stopped_conflict | 追加WriteせずLease／State確認 |
| Resource Limit | paused_resource_limit | 最後の確認済みStateを保持 |
| Task反応なし | review_pendingまたはstopped | 無制限再試行しない |
| Provider部分成功 | stopped_capability | Created Taskの状態を明示し安全停止 |
| Registration未観測／Title不一致 | stopped_capability | 自動Retry／Task再作成せず停止 |
| Authorized Root外Access／無許可Mutation | EMERGENCY_STOP | CleanupせずExact Stateを報告し人間判断待ち |
| READY Evidence失効 | OFFまたはawaiting_user_authorization | Startせず再Review |

停止後に「良かれ」で新Task、代替Provider、追加課金、Git、File変更または強制Recoveryを開始しない。

## 10. Recovery

Recoveryは次の順序で行う。

1. Project Responsibility Handoff／最新Recovery。
2. Design Governance Handoff／最新Recovery。
3. Current Documentation Index／Project Continuity。
4. Phase 2 Index。
5. Accepted Envelope Revision。
6. Handoff Digest／Acknowledgement／最終Status／Review。
7. Role Authority Matrix／Role View／Provider Capability。
8. 次の最小安全Action。

Accepted Envelope draft-4がない現在は、Recovery後の次Actionは「Role Authority Review、FreezeとTwo-key Start」である。旧draft-2／3／3a Acceptanceを再利用しない。

## 11. Security／Authority Properties

- UI／Task名／Role名はSecurity Boundaryではない。
- Taskの存在はWrite／Git／External Authorityを生成しない。
- DocsのRead AuthorityはStable、IndexまたはHistoryのWrite Authorityを生成しない。
- Parent TaskのAuthorityをChild Taskへ暗黙継承しない。
- Childの成果をParentがReviewせずAcceptedにしない。
- プロジェクト責任者役も最上位規則、Accepted Envelope、Authorized Root、Evidence、StopおよびHuman Gateに従属する。
- Authorized Root／Allowed Path外への無許可Accessは全Role、全Level、全Providerで禁止する。

## 12. Future Extension

Phase 2-0のRead-only Pilot合格後だけ、次を再設計できる。

```text
Stage 2: one bounded documentation write
Stage 3: one connected design／review work unit
Stage 4: one subphase
Stage 5: phase completion
Stage 6: project completion
```

上位Stageは自動で有効化しない。Phase 2で成立性、Phase 3で再現性／移植性を別個に検証する。

## 13. Related Documents

- [Pilot Requirements](../requirements/phase_2_0_automation_pilot_requirements_ja.md)
- [Authorization Envelope Draft](../governance/phase_2_0_authorization_envelope_draft_ja.md)
- [Bounded Read Manifest Draft](../governance/phase_2_0_bounded_read_manifest_draft_ja.md)
- [Execution Plan](../operations/phase_2_0_automation_pilot_execution_plan_ja.md)
- [Bootstrap Handoff Draft](../handoffs/phase_2_0_phase_designer_bootstrap_handoff_draft_ja.md)
- [Automation Governance Index](../../../shared/automation/automation_governance_index_ja.md)
- [Automation Control Profile](../../../shared/automation/automation_control_profile_ja.md)
- [Automation／Governance Evidence Log](../../../shared/automation/automation_governance_evidence_log_ja.md)
- [Codex Desktop Bounded Read Adapter](../../../shared/automation/provider_adapters/codex_desktop_bounded_read_adapter_ja.md)
