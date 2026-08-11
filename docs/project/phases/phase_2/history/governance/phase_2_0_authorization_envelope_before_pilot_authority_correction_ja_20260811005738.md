# Phase 2-0 Orchestration Authorization Envelope Draft

```yaml
document_id: phase_2_0_authorization_envelope_draft
envelope_id: p2-0-envelope-001
revision: draft-3
status: draft_not_authorized
phase: phase_2
subphase: phase_2_0
work_unit: P2-0-WU-002
language: ja
created_at: 2026-08-04 11:17:44 JST
updated_at: 2026-08-11 00:19:18 JST
owner: プロジェクト責任者兼設計統括者役
decision_authority: user
accepted: false
previous_revision: draft-2_consumed_by_P2-0-WU-001
design_adjustment_authorized: true
```

## 1. Status Boundary

本書は、初回PilotのSafety Pass／Functional Failを受けたBounded Read Recovery再試験用Draftである。ユーザーはdraft-3と関連Docsの再設計を許可したが、本RevisionのAcceptance、新Task作成、Local Command実行、Git操作またはPilot再開はまだ許可していない。

```text
Previous Unit   : P2-0-WU-001 consumed／closed for execution
Previous Task   : idle evidence／no further message or mutation authorized
Current Unit    : P2-0-WU-002 draft
Control State   : PAUSED／REDESIGN
Required Gate   : exact draft-3 Freeze → user acceptance → READY／ARMED → user start
```

## 2. Proposed Authorization

| Field | Draft Value |
|---|---|
| Work Unit | P2-0-WU-002 Bounded Read Cold Recovery Retest |
| Provider | Codex Desktop independent Task capability |
| Controller | プロジェクト責任者兼設計統括者役 |
| New Task Creation Count | exactly 1 after all Gates |
| Existing Task Mutation | none |
| Replacement Task Count | 0 |
| Child Role | Phase 2設計担当者役 |
| Proposed Task Title | `Phase 2設計担当者役 P2-0-WU-002` |
| Work Mode | read-only／conversation output only |
| Automation Level | bounded_unit |
| Control State | PAUSED; separate Gates required for ARMED／ON |
| Authorized Root | Project ManifestでRuntime時にExact解決 |
| Exact Read Scope | `p2-0-read-manifest-001` Frozen Revisionだけ |
| Local Command | Provider AdapterのAllowed Grammarだけ |
| File Write／Git／External／Secret／Destructive | prohibited |
| Sub-agent／Additional Task | prohibited |
| Follow-up | ACK後のRecovery依頼1回だけ |
| Completion | Structured Recovery Assessment and Mutation Report |
| Expiration | Review確定、User revocationまたはContract変化の最初 |

## 3. Allowed Controller Actions

全Pre-activation Gate成立後、Controllerが連結できるActionは次だけである。

1. 新しい独立Taskを1件作成する。
2. Provider上のRegistrationを観測可能になるまでRead-onlyに確認する。
3. Exact Titleを1回設定し、Read-backで一致を確認する。
4. Frozen Handoff／Manifest／Digest／Authorityを初回Promptとして送る。
5. Authority Acknowledgementを取得する。
6. ACK合格時だけ、1回のFollow-upでRecovery Assessmentを依頼する。
7. Status／Final Reportを取得する。
8. PostflightをRead-onlyで照合し、GO／ADJUST／STOP案をユーザーへ提示する。

Task Creation成功後も、Registration未確認、Title設定失敗またはHandoff不成立なら自動再試行せず`PAUSED`へ戻る。固定Sleep、無制限Polling、別Task作成または旧Task再利用は禁止する。

## 4. Child Read Authority

Child Taskは、次の全条件を同時に満たす場合だけLocal Text Readを実行できる。

```text
Accepted Envelope Revision = draft-3
Accepted Work Unit          = P2-0-WU-002
Control State               = ON
Authorized Root             = Controller-resolved Exact Root
Read Target                 = Frozen Manifest Exact Entry
Command                     = Accepted Provider Adapter Grammar
Sandbox                     = default／no escalation
Output                      = stdout-only
```

Exact Read Scopeは[Bounded Read Manifest](phase_2_0_bounded_read_manifest_draft_ja.md)、Provider固有手段は[Codex Desktop Bounded Read Adapter](../../../shared/automation/provider_adapters/codex_desktop_bounded_read_adapter_ja.md)を正本とする。Directory探索、Manifest外Pathまたは代替Commandへ拡張しない。

## 5. Write／Mutation Scope

```text
none
```

Child TaskはFile／Directory作成、編集、削除、Rename、Copy、Move、Permission／ACL／Metadata変更、Cache、Log、Temporary Artifact、Test、Build、Formatter、Git、Browser、NetworkまたはExternal Actionを行わない。

## 6. Absolute Prohibitions

- Accepted Adapter Grammar外のShell／Command／Tool実行。
- Project Root内外のFile Mutation。
- Manifest外のRead、List、Search、Stat、Glob、Recursive TraversalまたはSymlink追跡。
- Git Statusを含むGit Command。
- Secret、Credential、Private Keyまたは個人情報のRead／記録。
- GitHub、Lightning、Browser、Network、ConnectorまたはExternal Service操作。
- Task、Sub-agent、Thread、ProcessまたはAutomationの新規作成。
- 旧TaskへのFollow-up、Rename、Archive、DeleteまたはRecovery再依頼。
- Handoff外の要件変更、設計変更、権限拡張またはPhase 2-A移行。
- 最上位規則の追加、変更、削除、並替え、例外化または候補登録。
- Incident後のCleanup、Rollback、Move、再生成または証跡整合化。

## 7. Required Output

最初のTurnは`ACK_STATUS`だけを返し、Local Readを開始しない。

```yaml
acknowledgement:
  role: Phase 2設計担当者役
  work_unit: P2-0-WU-002
  envelope_revision: draft-3
  read_manifest: p2-0-read-manifest-001
  write_scope: none
  provider_adapter: codex_desktop_bounded_read_adapter
  prohibited_actions: list
  human_gates: list
  stop_conditions: list
  handoff_digest: sha512
```

ACK合格後の一回だけのFollow-upに対し、次を会話上で返す。

```yaml
recovery_assessment:
  result: PASS | FAIL | AMBIGUOUS
  read_coverage: per_entry_mapping
  project_purpose: string
  current_state: string
  completed_phases: list
  active_phase: string
  role_boundaries: mapping
  source_of_truth: list
  absolute_prohibitions: list
  first_safe_action: string
  contradictions_or_stale_state: list
  missing_information: list
  proposed_next_gate: string
mutation_report:
  files_created: []
  files_modified: []
  files_deleted: []
  git_mutation: none
  external_mutation: none
```

## 8. Stop Conditions

- Envelope、Manifest、Freeze Receipt、Handoff DigestまたはTask Titleが不一致。
- Required Entryの一つでも不存在、Unreadable、Digest不一致またはRead不完全。
- Adapter Allowed Grammarでは評価できない。
- Output Truncation、Page GapまたはProvider Tool Failureを安全に解決できない。
- Authority、Role、Current StateまたはSource of Truthが優先順位で解決不能。
- File／Git／External Mutation、追加Task、追加Follow-upまたはScope拡張が必要。
- Resource、Context、ServiceまたはQuotaが不安定。
- Authorized Root外Access、Unexpected ArtifactまたはEvidence不整合の疑い。

停止時は確認済み範囲、未確認範囲、Exact Stop Reasonおよび必要なHuman Gateだけを返す。代替手段、Cleanup、自動Retryまたは推測補完を行わない。

## 9. Resource Boundary

- 新規Task作成は1件。
- 旧TaskへのActionは0件。
- Replacement Taskは0件。
- ACK後Follow-upは1回。
- Read CommandはManifest 18件のLine Count、Digestおよび欠落のないPage Readに必要な範囲だけ。
- Provider Failure時の自動再試行は0回。
- Usage／Creditを取得できなくても、本Unitだけで安全停止できること。

## 10. Pre-activation Gates

次を順序どおり全て必要とする。

1. draft-3 Design Package Review合格。
2. Provider Adapter Read-only Preflight合格。
3. Exact Manifest／Envelope／HandoffとDetached Freeze Receipt確定。
4. ユーザーが明示承認した場合だけGit Checkpoint／PushとRemote一致確認。
5. ユーザーによるBackup Basis確認。
6. ユーザーがExact draft-3、Freeze Receiptおよび新Task 1件を明示Accepted化。
7. ControllerがREADY Evidenceを照合し`ARMED`を宣言。
8. 後続ユーザーがStartを明示し`ON`へ移行。

過去のdraft-2 Acceptance、初回Start Eventまたは旧Task存在を、本RevisionのGateへ流用しない。

## 11. Registration Lifecycle

Provider固有Lifecycleは次の論理Stateへ分離する。

```text
task_creation_requested
  → task_id_returned
  → registration_observable
  → exact_title_applied
  → exact_title_verified
  → handoff_delivered
```

`task_id_returned`を`registration_observable`と同一視しない。Observationは固定時間や無制限再試行へHard-codeせず、ProviderのRead／Wait結果で確認する。各部分失敗はEvidenceを残して停止する。

## 12. Expiration／Revocation

次の最初の一つで失効する。

- P2-0-WU-002 Review確定。
- User revocation。
- Authority Deviationまたはその疑い。
- Envelope／Manifest／Handoff／Adapter Revision変更。
- Authorized Root、Provider Capability、Automation ProfileまたはGit Freeze状態の変化。
- Phase 2-0以外への移行。

Expired EnvelopeをWrite Pilot、Phase 2-A、旧Taskまたは別Providerへ流用しない。

## 13. Acceptance Block

```yaml
accepted_by_user: false
accepted_at: null
accepted_revision: null
accepted_freeze_receipt: null
new_task_creation_explicitly_requested: false
provider_read_adapter_preflight: design_time_sample_pass_full_freeze_recheck_pending
git_checkpoint_confirmed: false
remote_alignment_confirmed: false
backup_basis_confirmed_by_user: false
authorized_root_resolved: false
manifest_frozen: false
handoff_digest_confirmed: false
ready_evidence_complete: false
control_state: PAUSED_REDESIGN
controller_ready_declared: false
user_start_declared: false
```

## 14. Related Documents

- [Pilot Requirements](../requirements/phase_2_0_automation_pilot_requirements_ja.md)
- [Pilot Architecture](../architecture/phase_2_0_automation_pilot_architecture_ja.md)
- [Bounded Read Manifest](phase_2_0_bounded_read_manifest_draft_ja.md)
- [Execution Plan](../operations/phase_2_0_automation_pilot_execution_plan_ja.md)
- [Bootstrap Handoff Draft](../handoffs/phase_2_0_phase_designer_bootstrap_handoff_draft_ja.md)
- [Codex Desktop Bounded Read Adapter](../../../shared/automation/provider_adapters/codex_desktop_bounded_read_adapter_ja.md)
- [Initial Pilot Evidence](../history/operations/phase_2_0_initial_automation_pilot_execution_evidence_20260811000435.md)
