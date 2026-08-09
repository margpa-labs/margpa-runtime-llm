# Phase 2-0 Document-driven Orchestration Pilot 要件定義

```yaml
document_id: phase_2_0_automation_pilot_requirements
status: design_draft
phase: phase_2
subphase: phase_2_0
language: ja
created_at: 2026-08-04 11:17:44 JST
updated_at: 2026-08-09 18:11:00 JST
owner: プロジェクト責任者兼設計統括者役
project_gate_owner: プロジェクト責任者兼設計統括者役
decision_authority: user
implementation_started: false
task_creation_authorized: false
```

## 1. 目的

Phase 2-0では、元来のConversation Continuity実装より先に、Current／Shared／Phase DocsをControl Planeとして独立Taskを安全に編成、引き継ぎ、監督、停止および復元できるかを最小有界単位で検証する。

目標は「Taskを自動で作れた」ことではない。次の存在、登録、権限、承認、実行および責任を分離したまま、従来より再説明CostとContext Pollutionを減らせるかを評価する。

```text
Capability Exists
  ≠ Task Authorized
  ≠ Task Created
  ≠ Authority Acknowledged
  ≠ Mutation Authorized
  ≠ Result Accepted
  ≠ Phase Complete
```

## 2. Scope

### 2.1 Included

- Phase 2開始状態とPhase 2-0のDocs Control Planeを成立させる。
- Provider Capabilityと現在のTool契約をRead-onlyで確認する。
- Phase Orchestration Authorization EnvelopeのDraftを作る。
- 独立Task用Reading Order、Role、Scope、Prohibition、StatusおよびStopを設計する。
- ユーザーがEnvelopeとTask作成を明示承認した場合に限り、後続の最初のRead-only Work Unitを実行できる状態まで設計する。
- GO／ADJUST／STOPの判定要件とEvidenceを定義する。
- Phase 1-ex ClosureのIncident／Near MissをPilotと将来憲法書の入力にする。

### 2.2 Excluded

- 本設計Task中の新規独立Task作成、Task名変更、Pin、ArchiveまたはTask間送信。
- `src/`、`tests/`、`scripts/`、`config/`およびRuntimeの変更。
- Conversation Persistence、Configuration UI、Component SwitchboardまたはRAG Follow-upの実装。
- Git Commit／Push／Branch／PR／Tag／Release。
- External Service、Lightning、Secret、Credential、課金環境または公開状態の変更。
- 複数Taskによる同一Working Treeへの同時Write。
- Phase 2-A以降への自動移行。

## 3. Functional Requirements

### P2-0-FR-001 — Phase State

Phase 1とPhase 1-exを`complete_accepted`、Phase 2を`active`、Phase 2-0を`pilot_design`とし、Phase 2の機能実装は`not_started`と分離する。

### P2-0-FR-002 — Authorization Envelope

Task作成より前に、少なくとも次を含むEnvelopeを作成する。

```text
Envelope ID／Revision／State
Phase／Subphase／Work Unit
Allowed Task Role／Task Name
Maximum Active／Replacement Task Count
Provider／Capability
Read／Write／External／Git／Secret Authority
Working Tree／Single Writer Boundary
Allowed Actions／Prohibited Actions
Cost／Usage／Context Stop
Human Gate
Evidence／Status／Review／Recovery Path
Expiration／Revocation
User Approval Evidence
```

Draftの存在は承認を意味しない。`draft → accepted`はユーザーの明示指示でだけ変化できる。

### P2-0-FR-003 — Provider Capability Preflight

Task作成、Task名設定、Prompt／Handoff送信、Follow-up、Status取得、Wait、Stop／Interrupt、Pin／ArchiveおよびRecoveryの現在Capabilityを、実行前に`available／unavailable／manual_required／unknown`へ分類する。

Tool名をNormative Coreにせず、Provider Adapter候補として記録する。Capability不足時に代替Actionを推測実行しない。

### P2-0-FR-004 — Docs-only Recovery

新Taskは旧会話を読まず、指定Reading Orderから次を説明できなければならない。

- Project目的と現在Phase。
- Phase 1／1-exの完了とPhase 2-0の位置。
- ユーザー、プロジェクト責任者役、設計統括者役および自TaskのAuthority差。
- Allowed／Prohibited／Stop／Escalation。
- Current／Shared／Phase／Public／History／Lossless／Backup／Gitの正本境界。
- 最初の作業と完了条件。

### P2-0-FR-005 — Authority Acknowledgement

作業前に新Taskが次を構造化して返す。

```text
role
phase／subphase／work_unit
read_scope
write_scope
prohibited_actions
human_gates
stop_conditions
expected_output
open_questions
acknowledged_handoff_digest
```

Acknowledgementが不足、誤読またはHandoff Digest不一致の場合は作業を開始しない。

### P2-0-FR-006 — Single Writer Lease

同一Working Treeでは、実際にWriteするTaskを1つに限定する。LeaseはTask ID、Path Scope、Start／Expiration／Release Stateを持つ。初回Work UnitはRead-onlyのためLeaseを`not_required_read_only`とする。

### P2-0-FR-007 — Orchestration State Machine

```text
draft
  → awaiting_user_authorization
  → authorized
  → task_created
  → awaiting_acknowledgement
  → acknowledged
  → running
  → review_pending
  → accepted／adjust_required／stopped／paused_resource_limit
```

各TransitionはActor、Timestamp、Input Evidence、Result、Open FindingおよびNext Gateを持つ。中間Stateを`complete`と表示しない。

### P2-0-FR-008 — Status／Review／Follow-up

StatusはChanged Filesだけでなく、No Mutation、Git／External State、Test、Open Finding、Authority Deviation、Cost ObservationおよびRecoveryを含む。Reviewは`accepted／follow_up／rejected／paused`を明示する。

### P2-0-FR-009 — Evidence Classification

成功と問題を次へ分類する。

```text
RULE_EFFECTIVE
RULE_AMBIGUOUS
RULE_MISSING
RULE_OVERRESTRICTIVE
RULE_UNENFORCEABLE
HUMAN_GATE_REQUIRED
AUTOMATION_CANDIDATE
```

Near Miss、Human Interventionおよび偶然成功を省略しない。

### P2-0-FR-010 — Cost／Resource Stop

Token／Credit／Quotaを取得できない場合は、十分であると推測しない。初回を1 Task、1 Work Unit、Read-onlyに制限する。Limit、Service Error、Context不安定化または繰り返し失敗を検出したら`paused_resource_limit`または`stopped`にする。

### P2-0-FR-011 — User Gate

次はユーザーの明示承認を必要とする。

- 初回の独立Task作成。
- Authorization EnvelopeのAccepted化。
- Read-onlyからWrite Pilotへの拡張。
- Task追加、交代、上限変更またはScope拡張。
- Git／GitHub、External、Secret、課金、Destructive Action。
- GO／ADJUST／STOPのFinal Acceptance。
- Phase 2-Aへの移行。

### P2-0-FR-012 — Combined Role／Separated Recovery

当面、現在Taskは`プロジェクト責任者兼設計統括者役`として兼務する。独立した設計統括者Taskは新設しない一方、Project ResponsibilityとDesign GovernanceのStable／History／Recoveryを分離して相互参照する。兼務はAuthority合算または運用ルール免除を生成しない。

### P2-0-FR-013 — Gradient Automation Control

AutomationをBinary ON／OFFだけで表現せず、少なくとも`manual／advisory／bounded_unit／workflow／phase／project`のLevelと、Task作成、Mutation、Continuation、Git、External、ResourceおよびHuman Gateの独立Dimensionを持つ。初回Pilotは`bounded_unit`を上限とする。

### P2-0-FR-014 — Pre-pilot Backup／Dual Consent

Pilot開始前にユーザーによる大規模Backup完了報告を必要とする。その後、Control Taskの「準備OK。いつでも開始出来ます。」と、後続ユーザーの「ok。では開始する。」を順序どおり確認した場合だけStart Eventを成立させる。

### P2-0-FR-015 — Supreme Authorized Root

Role、Automation Level、Phase／Project ScopeまたはProviderに関係なく、明示されたAuthorized Root／Allowed Path外へ無許可で触れない。Read、List、Search、Stat、Temporary Artifact、Symlink先および暗黙Tool Accessも含める。

### P2-0-FR-016 — Portable Core／Multi-provider Reservation

Automation／Constitution Coreへ特定Project、Provider、Repository、Absolute Path、Phase、Task、CommandまたはUIをHard-codeしない。Project固有値をManifest、Provider固有操作をAdapterへ分離する。CodexとClaude Code等の併用は未決定の将来候補であり、別EvidenceとUser Acceptanceなしに初回Pilotへ含めない。

## 4. Non-functional Requirements

### P2-0-NFR-001 — Fail-closed

Authority、Capability、Target、Working Tree、Handoff Revision、CostまたはUser Gateが不明な場合は実行せず停止する。

### P2-0-NFR-002 — Provider Neutrality

Normative ContractはCodex固有Tool名へ直結させず、CapabilityとProvider Adapterを分離する。Claude Code等へ移植する際もAuthority、Evidence、Stop、RecoveryおよびHuman Gateを弱めない。

### P2-0-NFR-003 — Recoverability

新しいプロジェクト責任者役、設計統括者役またはPhase Taskが、Docsだけから最後に確認されたStateと次の安全な一手を復元できる。

### P2-0-NFR-004 — Bounded Cost

利用可能量が不明でも停止可能な小さい単位を使う。成功判定に「多数Taskを使ったこと」を含めない。

### P2-0-NFR-005 — Auditability

Task作成、Handoff、Acknowledgement、Status、Review、Stop、RecoveryおよびUser Gateを時系列で説明できる。Credential、個人情報または不要なProvider内部IDをDocsへ書かない。

### P2-0-NFR-006 — Non-interference

PilotはPhase 1 Runtimeを壊さず、Phase 2機能実装を先行せず、Git／External Stateを変更しない。

### P2-0-NFR-007 — Portability without Core Rewrite

新規Project、既存Projectまたは別Providerへ展開する際、Normative Coreの書換えを要求しない。Manifest／Adapter／Role Viewの差替えで同一Authority、Evidence、Stop、RecoveryおよびHuman Gateを保持する。

## 5. Initial Work Unit

```text
Work Unit ID  : P2-0-WU-001
Name          : Docs-only Recovery and Authority Acknowledgement
Task Candidate: Phase 2設計担当者役
Mode          : read-only
Write Scope   : none
External／Git : prohibited
Sub-agent     : prohibited
Replacement   : 0
Completion    : structured acknowledgement and recovery assessment returned
```

本Work UnitのTask作成は本書の作成だけでは許可されない。Authorization Envelope Draftのユーザー承認と、独立Taskを作成する明示指示を別途必要とする。

## 6. Acceptance Criteria

### Design Acceptance

- Requirements、Architecture、Envelope、Execution PlanおよびDraft Handoffが相互整合する。
- Phase 2開始とPilot実行開始を混同しない。
- ユーザーの追加承認が必要な地点が明示される。
- 実装、Git、External、SecretおよびDestructive ActionがScope外である。

### Future Work Unit Acceptance

- Taskがユーザー承認後にだけ作成された。
- Task名、Role、Phase、Handoff Revisionが一致した。
- Docs-only Recoveryに成功した。
- Authority Acknowledgementが完全で、誤ったAuthority拡張がなかった。
- File、Git、External、SecretおよびDestructive Mutationが0であった。
- Status、Review、Cost、Near MissおよびStop／Recoveryが追跡できた。
- 従来より再説明CostまたはContext Pollutionを減らせる見込みがEvidenceで説明できた。

## 7. Open Decisions

| Decision | Current State | Authority |
|---|---|---|
| Authorization EnvelopeのAccepted化 | awaiting user review | user |
| `Phase 2設計担当者役`Task作成 | not authorized | user |
| Task Title／Pin | capability preflight required | user／provider |
| Work Unit後のWrite Pilot | not designed as accepted scope | user |
| Phase 2-A移行 | blocked until P2-0 review | user |
| Phase 2実装者役Task | not created／not authorized | user |

## 8. Related Documents

- [Phase 2 Index](../phase_index_ja.md)
- [Pilot Architecture](../architecture/phase_2_0_automation_pilot_architecture_ja.md)
- [Authorization Envelope Draft](../governance/phase_2_0_authorization_envelope_draft_ja.md)
- [Execution Plan](../operations/phase_2_0_automation_pilot_execution_plan_ja.md)
- [Bootstrap Handoff Draft](../handoffs/phase_2_0_phase_designer_bootstrap_handoff_draft_ja.md)
- [Automation Governance Index](../../../shared/automation/automation_governance_index_ja.md)
- [Automation Control Profile](../../../shared/automation/automation_control_profile_ja.md)
- [Automation／Governance Evidence Log](../../../shared/automation/automation_governance_evidence_log_ja.md)
