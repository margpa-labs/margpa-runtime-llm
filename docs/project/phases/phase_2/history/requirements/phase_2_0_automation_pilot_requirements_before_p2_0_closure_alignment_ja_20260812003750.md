# Phase 2-0 Document-driven Orchestration Pilot 要件定義

```yaml
document_id: phase_2_0_automation_pilot_requirements
status: capability_contract_redesign_complete_wu_004_candidate_pending
phase: phase_2
subphase: phase_2_0
language: ja
created_at: 2026-08-04 11:17:44 JST
updated_at: 2026-08-11 23:13:32 JST
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
- 初回PilotのSafety Pass／Functional Failを分離し、限定Local Read Capabilityを用いたCold Recovery再試験を別Work Unitとして設計する。
- P2-0-WU-003のContent Success／Provider Grammar Failureを分離し、Documentation Capability SemanticsとProvider Mappingを再設計する。

### 2.2 Excluded

- 本設計Task中の新規独立Task作成、Task名変更、Pin、ArchiveまたはTask間送信。
- `src/`、`tests/`、`scripts/`、`config/`およびRuntimeの変更。
- Conversation Persistence、Configuration UI、Component SwitchboardまたはRAG Follow-upの実装。
- Git Commit／Push／Branch／PR／Tag／Release。
- External Service、Lightning、Secret、Credential、課金環境または公開状態の変更。
- 複数Taskによる同一Working Treeへの同時Write。
- Phase 2-A以降への自動移行。
- 初回Taskの再利用、追加Follow-up、Archive、Delete、RenameまたはEvidence状態の変更。

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

Task作成、Task登録観測、Task名設定、Prompt／Handoff送信、Follow-up、Status取得、Wait、Stop／Interrupt、Pin／ArchiveおよびRecoveryの現在Capabilityを、実行前に`available／unavailable／manual_required／unknown`へ分類する。Docs Recoveryを要求するWork Unitでは、Local Text Read Capability、実行手段、Read-only性、Artifact生成、Output TruncationおよびStop ContractもTask作成前に検証する。

Tool名をNormative Coreにせず、Provider Adapter候補として記録する。Capability不足時に代替Actionを推測実行しない。

Provider Adapterは`semantic_mapping／strict_enforced_mapping／strict_prompt_only`のいずれかを明示する。特定CommandをPromptへ列挙しただけの状態を、機械的に強制済みのAllowlistとして扱わない。

### P2-0-FR-004 — Docs-only Recovery

新Taskは旧会話を読まず、Frozen Exact Read Manifestを指定順序、Digestおよび全文Coverage付きで読み、次を説明できなければならない。

- Project目的と現在Phase。
- Phase 1／1-exの完了とPhase 2-0の位置。
- ユーザー、プロジェクト責任者役、設計統括者役および自TaskのAuthority差。
- Allowed／Prohibited／Stop／Escalation。
- Current／Shared／Phase／Public／History／Lossless／Backup／Gitの正本境界。
- 最初の作業と完了条件。

Manifest外探索、Directory単位の包括Readまたは類似Pathへの代替をRecoveryに含めない。

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

### P2-0-FR-014 — Common Role Authority／Automation Overlay／Dual Consent

通常運転とAutomationは同じRole Authority、Docs AuthorityおよびRoleごとの判断責任を使う。Automation Pilotは、ユーザーがAccepted化した有界到達線、Work Unit連結、Control Stateおよび継続上限だけを差分として追加する。同じ規則をMode別に二重定義せず、判断を機械的Resolverへ置換しない。

Role Authority MatrixをRoleに与え得る上限、Accepted Envelopeを今回有効化するScope、Role ViewをTaskへ渡す交差とする。Control State `ON`後、交差内の`ROLE_ALLOWED` Actionは個別再確認なしで自律実行する。

Docs Authorityは、文書ClassまたはExact Pathごとに`READ／CREATE_NEW／APPEND_NEW／EXISTING_WRITE_USER_EXPLICIT／REVIEW_ONLY／DENY`をRole Viewへ明示する。既存Stable文書への直書きはModeを問わずユーザーのExact Authorizationを必要とする。

必要Artifactは、当該Docs Authorityを委譲されたRole／Taskが、共通Docs／運用規則、Work Unit、Role／Task境界、State Transition、Mutation Risk、Review／Human Gate、Audit／Recovery、Provider Capability、情報Loss、CostおよびContextから都度判断する。最高責任者役はCross-Role対象、競合、委譲境界およびGateを調整する。Index、Handoff、Status、Review／AcceptanceまたはEvidenceは必要な場合だけ作り、一つのArtifactが複数責務をLosslessに満たせる場合は統合する。Role／Task間の移転ArtifactにFrom／Toを記録し、Index、Requirements／Designおよび単一Role内Evidenceは各責務に対応するOwner／Authority／Reader／Actor情報を持つ。

人間側のBackup、Recovery Assetまたは私的保全状態は、AI／Task／Agent／Toolの認識、Read、List、Stat、Evidence、ValidationまたはActivation Gateの対象にしない。

Control Taskの「準備OK。いつでも開始出来ます。」と、後続ユーザーの「ok。では開始する。」を順序どおり確認した場合だけStart Eventを成立させる。

### P2-0-FR-015 — Supreme Authorized Root

Role、Automation Level、Phase／Project ScopeまたはProviderに関係なく、明示されたAuthorized Root／Allowed Path外へ無許可で触れない。Read、List、Search、Stat、Temporary Artifact、Symlink先および暗黙Tool Accessも含める。

### P2-0-FR-016 — General Hard-code Prohibition／Portable Core

General Hard-code ProhibitionのNormative本文は[Task Role／Write Authority Policy](../../../shared/task_roles/task_role_write_authority_policy_ja.md)を参照する。Phase 2-0固有要件として、Project固有値をManifest、Provider固有操作をAdapter、Work Unit固有値をEnvelope／Role View／Freeze Eventへ分離する。

現在の許可範囲内でHard-codeの不可避性、抽象化方法、EvidenceおよびTestを判断するのは、その時点の最高責任者役である。最上位規則改変、Root／Scope／Authority拡張その他のHuman-only事項だけをユーザーへ返す。CodexとClaude Code等の併用は未決定の将来候補であり、別EvidenceとUser Acceptanceなしに初回Pilotへ含めない。

### P2-0-FR-017 — Automation Control State

Automation Levelと独立して、`OFF／ARMED／ON／PAUSED／EMERGENCY_STOP`のControl Stateを保持する。P2-0-WU-003のContract Deviation後かつCapability再設計中の現在Stateは`PAUSED／CAPABILITY_CONTRACT_REDESIGN`とする。

- `ARMED`はREADY Evidence成立後かつユーザーStart宣言前。
- `ON`はAccepted Envelope内の実行中だけ。
- `PAUSED`はResource／Review／Capability等による安全停止。
- `EMERGENCY_STOP`はAuthority、Authorized Root、重大MutationまたはEvidence断絶のIncident。
- State変更はActor、Evidence、Timestamp、Scopeおよび再開条件を必要とする。
- StateはAutomation Level、Task数、Filesystem Scope、Git、ExternalまたはPermission Authorityを自動拡張しない。

### P2-0-FR-018 — READY Evidence

Control TaskがREADYを宣言する前に、Design Review、Role Authority Matrix、Role View、Accepted Envelope、Authorized Root／Allowed Path、最上位規則群、Stop／Evidence、Resource／Provider Capability、最初の有界Work Unitおよび未解決事項を照合する。

READY後にScope、Profile、RevisionまたはCapabilityが変化した場合はREADYを失効させる。AIは人間側のBackup／Recovery Assetを認識、確認またはGate化しない。

### P2-0-FR-019 — Incident後No-cleanup

Authority逸脱または疑いの後は、自Taskが作成したArtifactでもDelete、Cleanup、Rollback、Move、再生成または証跡整合化を行わない。Exact Stateを報告し、人間の明示指示を待つ。

### P2-0-FR-020 — Permission／Mechanical Enforcement Reservation

AI／Task／Tool作成ArtifactのPermission／ACL Hardeningは未決定とし、初回Pilotへ含めない。Path Allowlist、許可外DirectoryのRead-only化、隔離Workspace、Mutation Inventory、許可Root外Diff検知およびTool Wrapperは将来研究候補であり、未実装・未承認とする。

これらを採用する場合は、Target、Before／After、Platform影響、Lockout、False Positive、Recoveryおよびユーザー明示承認を必要とする。

### P2-0-FR-021 — Canonical Pre-activation Gate Order

再試験の準備と開始は次の順序へ固定する。後続Gateの成立を理由に前段を省略せず、Capability PreflightをREADY宣言またはTask作成後へ遅延させない。

```text
1. Design Package／Role Authority Matrix／Role View Review
2. Bounded Read Provider Adapter Preflight
3. Exact Manifest／Envelope／Role View／Handoff／AdapterとDetached Freeze Receiptの確定
4. Exact Envelope Revision、Role View、Freeze Receiptと新Task 1件のユーザーAcceptance
5. Control TaskのREADY宣言とControl State `ARMED`
6. 後続ユーザーStart宣言とControl State `ON`
7. 1つの新規独立Task作成、Provider登録観測、Task名検証、Handoff送信
8. Authority Acknowledgement、Bounded Read Recovery Assessment、Review
```

現在Taskの名称は`プロジェクト責任者兼設計統括者役`、作成候補Child Taskの名称は`Phase 2設計担当者役 P2-0-WU-002`とし、両者および旧Taskを混同しない。Git／Backup等の通常運用は本Read-only Pilot Activation Gateに含めず、別Authorityとして切り分ける。

### P2-0-FR-022 — Bounded Local Text Read Contract

Portable CoreはLocal Text ReadをShell Command名ではなく、次のCapability Contractとして表現する。

```text
Exact Authorized Root
Exact Manifest Entry
Expected Digest
Complete Page Coverage
Read-only／stdout-only
No Artifact／No Escalation
Evidence／Failure／Stop
```

Provider固有Executable、Command Grammar、Tool ParameterおよびOutput制約はProvider Adapterへ分離する。Shell一般許可、任意Command許可またはDirectory探索許可へ読み替えない。

### P2-0-FR-023 — Single-source Read Manifest

Recovery対象Pathは一つのPhase固有Manifestだけを正本とし、Requirements、Envelope、PlanおよびHandoffへPath一覧を重複記載しない。ManifestはOrdered Path Set、Entry Count、File DigestおよびFreeze Receiptで固定する。Manifest変更は旧Acceptanceを失効させる。

### P2-0-FR-024 — Retest Isolation

初回`P2-0-WU-001`とそのTaskを実行Evidenceとして保持し、再試験は新しい`P2-0-WU-002`と新しいTaskで行う。旧TaskへのFollow-up、Rename、Archive、Deleteまたは再利用は、新しいユーザー明示指示なしに行わない。過去のEnvelope Acceptance、Start EventまたはTask Authorityを再試験へ継承しない。

### P2-0-FR-025 — Provider Registration Lifecycle

Task ID返却、Provider登録、Metadata解決、Exact Title設定、Read-back VerificationおよびHandoff成立を別Stateとして扱う。固定Sleep、無制限Polling、自動Task再作成または無許可RetryへHard-codeしない。部分失敗はTaskを作業開始させず`PAUSED`へ移行する。

### P2-0-FR-026 — Delegated Role-local Judgment／Layered Completion

全Role／Taskは、最高責任者役へ委譲されたProject Authorityの内側で、さらに自Roleへ割り当てられた役割、実行権限、Docs Authority、Accepted DesignおよびWork Unitの交差内を都度判断する。Automationはこの判断を機械的に固定せず、承認済み到達線までの連結を追加するだけである。

Phase別設計担当者役はAssigned Phase内の設計判断、Accepted Designの実装担当への伝達、局所Review、Finding解決および再作業指示を自律実行する。実装担当役はAccepted Designと担当Source／Test Scope内で実装方法、局所修正、再Test、担当内EvidenceおよびStatusを自律判断する。問題なくScope内を進行しているRoutine Actionごとに、最高責任者役へ確認しない。

例外、重大問題、Role／Work Unit／Path外、要件／規則Conflict、Cross-Phase影響、Security／Privacy／Recovery Risk、Resource／Provider異常、完了条件不成立または定義済みReview／Acceptance Gateだけを直属上位RoleへEscalateする。Roleは委譲範囲を自ら拡張できないが、すでに委譲されたActionを不必要に再承認対象へ戻さない。

初期Pilotの標準完了連鎖は、`Implementer完了報告 → Phase Designer Review／必要時再作業 → Phase Designer局所Accepted／Task完了報告 → 最高責任者役Review／Task完了判定案 → User Acceptance → 次Work Unit`とする。初期はTask／有界Work Unit単位で検証し、Evidence、安全性、安定性、有効性、RecoveryおよびCostが十分な場合だけ、Subphase、Phase、Project単位へ段階的に拡張する。

### P2-0-FR-027 — Capability Semantics／Provider Mapping Separation

Documentation Read／Createは、Raw Command名ではなく、Authority、Exact Root／Target、Operation、Coverage、Cardinality、Mutation、EvidenceおよびStopからなるCapability Contractとして定義する。

```text
Authority
  → Capability Semantics
     → Provider Mapping
        → Invocation Evidence
           → Independent Review
```

成果物の成功をContract遵守へ読み替えず、Provider Grammar違反をAuthority／Scope逸脱へ自動昇格しない。Authority、Scope、Capability Semantics、Provider Mapping、Result、EvidenceおよびStop／Recoveryを独立判定する。

### P2-0-FR-028 — Mechanical Enforcement／Batch Capability Boundary

特定Provider Grammar自体をSafety上の必須条件にする場合は、Wrapper、Validator、Provider-native AllowlistまたはTool Schemaによる機械的強制を必要とする。Promptだけで特定Commandを必須化する場合は`strict_prompt_only`としてEvidence化し、強制済みと表示しない。

複数Target処理は`exact_single_target_read`の実装詳細ではなく、別の`bounded_batch_read` Capabilityとする。Exact Target Set、Output分離、Partial Failure、CoverageおよびDigest Evidenceを持つAccepted Adapterがない限りDefault Denyとする。

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

## 5. Work Units

### 5.1 Initial Work Unit — Consumed

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

実行結果はSafety Pass／Recovery Failであり、`P2-0-WU-001`とdraft-2はConsumedである。再実行しない。

### 5.2 Adjusted Retest Work Unit — Accepted／Closed

```text
Work Unit ID  : P2-0-WU-002
Name          : Bounded Read Cold Recovery Retest
Task Candidate: Phase 2設計担当者役 P2-0-WU-002
Mode          : read-only／conversation output only
Read Scope    : Frozen p2-0-read-manifest-001 only
Read Adapter  : Accepted Provider-specific bounded read adapter
Write Scope   : none
External／Git : prohibited
Old Task      : no action
Replacement   : 0
Completion    : 18-entry complete read, recovery assessment and mutation report／ACCEPTED
```

P2-0-WU-002は18／18 Entry、6,692／6,692行のBounded Read Recoveryに合格し、ユーザーAccepted／Closedとなった。

### 5.3 Bounded Documentation Write — Adjust Required

```text
Work Unit ID  : P2-0-WU-003
Name          : Layered Recovery Operational View Bounded Write
Task          : Phase 2設計担当者役 P2-0-WU-003
Mode          : exact read + one exact create
Result        : content／path／digest／mutation safety PASS
Deviation     : Provider Grammar FAIL by Child self-report
Stop          : safe stop／no cleanup
Acceptance    : ADJUST_REQUIRED／not accepted
```

作成済みResultはEvidenceとして保持し、削除・上書き・再生成しない。P2-0-WU-003を遡及修正せず、Capability SemanticsとProvider Mappingを後続Work Unit用に再設計する。

### 5.4 Capability-semantics Retest Candidate

```text
Work Unit ID  : P2-0-WU-004
Name          : Capability-semantics Bounded Documentation Create Retest
Task Candidate: Phase 2設計担当者役／one new Task
Read Scope    : exact_single_target_read only
Write Scope   : one exact create only
Provider Mode : semantic_mapping
Batch         : unavailable／deny
Git／External : prohibited
State         : design candidate／exact package not created／not authorized
```

P2-0-WU-004は、Command名ではなくCapability Semantics、Exact Target、Coverage、Mutation Cardinality、Invocation EvidenceおよびStopを検証する。新しいExact Envelope、Manifest、Handoff、Receipt、Task作成、READY／ARMEDおよびユーザーStartを別途必要とする。

## 6. Acceptance Criteria

### Design Acceptance

- Requirements、Architecture、Envelope、Execution PlanおよびDraft Handoffが相互整合する。
- Phase 2開始とPilot実行開始を混同しない。
- ユーザーの追加承認が必要な地点が明示される。
- 実装、Git、External、SecretおよびDestructive ActionがScope外である。
- Control Stateが`PAUSED／CAPABILITY_CONTRACT_REDESIGN`であり、P2-0-WU-004のREADY／ARMED／ONへ未遷移である。
- Permission Hardeningと機械的強制が未実装・未承認である。
- Provider-neutral Documentation Capability ContractとProvider-specific Adapterが分離される。
- Read対象のSingle-source Manifestが成立し、Path一覧の重複Driftがない。
- P2-0-WU-003 Artifact／旧EnvelopeとP2-0-WU-004候補が分離される。
- Role Authority MatrixとRole Viewにより、交差内の自律ActionとScope外Gateが判定できる。

### Future Work Unit Acceptance

- Taskがユーザー承認後にだけ作成された。
- Task名、Role、Phase、Handoff Revisionが一致した。
- Docs-only Recoveryに成功した。
- Authority Acknowledgementが完全で、誤ったAuthority拡張がなかった。
- File、Git、External、SecretおよびDestructive Mutationが0であった。
- Status、Review、Cost、Near MissおよびStop／Recoveryが追跡できた。
- 従来より再説明CostまたはContext Pollutionを減らせる見込みがEvidenceで説明できた。
- Manifest全18件についてDigest一致と欠落のない全文Page CoverageがEvidence化された。
- Authority、Scope、Capability Semantics、Provider Mapping、Result、EvidenceおよびStop／Recoveryが独立判定された。
- Accepted CapabilityにないDirectory探索、Batch処理、追加ArtifactまたはScope拡張が0であった。
- Strict Grammarを必須化した場合は機械的強制Evidenceがあり、Prompt-only制約を強制済みと表示していない。

## 7. Open Decisions

| Decision | Current State | Authority |
|---|---|---|
| P2-0-WU-002 | accepted／closed | user |
| P2-0-WU-003 Result Artifact | retained／content verified／overall adjust required | user final classification pending |
| Documentation Capability Contract | design review passed／not activated | user／controller |
| Codex Documentation I/O Adapter | semantic mapping designed／not activated | user／provider preflight |
| `P2-0-WU-004` Exact Package | not created／not authorized | controller design／user acceptance |
| `P2-0-WU-004`新Task 1件作成 | not authorized | user |
| Mechanical Grammar Enforcement | unavailable／not claimed | future design／user |
| Bounded Batch Read | unavailable／denied | future design／user |
| Phase 2-A移行 | blocked until P2-0 review | user |
| Phase 2実装者役Task | not created／not authorized | user |

## 8. Related Documents

- [Phase 2 Index](../phase_index_ja.md)
- [Pilot Architecture](../architecture/phase_2_0_automation_pilot_architecture_ja.md)
- [Authorization Envelope Draft](../governance/phase_2_0_authorization_envelope_draft_ja.md)
- [Bounded Read Manifest Draft](../governance/phase_2_0_bounded_read_manifest_draft_ja.md)
- [Execution Plan](../operations/phase_2_0_automation_pilot_execution_plan_ja.md)
- [Bootstrap Handoff Draft](../handoffs/phase_2_0_phase_designer_bootstrap_handoff_draft_ja.md)
- [Automation Governance Index](../../../shared/automation/automation_governance_index_ja.md)
- [Automation Control Profile](../../../shared/automation/automation_control_profile_ja.md)
- [Automation／Governance Evidence Log](../../../shared/automation/automation_governance_evidence_log_ja.md)
- [Codex Desktop Bounded Read Adapter](../../../shared/automation/provider_adapters/codex_desktop_bounded_read_adapter_ja.md)
- [Documentation Capability Contract](../../../shared/automation/documentation_capability_contract_ja.md)
- [Codex Desktop Documentation I/O Adapter](../../../shared/automation/provider_adapters/codex_desktop_documentation_io_adapter_ja.md)
- [P2-0-WU-003 Capability Contract Redesign](../history/operations/phase_2_0_capability_contract_redesign_after_p2_0_wu_003_20260811231332.md)
