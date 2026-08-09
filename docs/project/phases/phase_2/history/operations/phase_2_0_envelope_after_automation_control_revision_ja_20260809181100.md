# Phase 2-0 Orchestration Authorization Envelope Draft

```yaml
document_id: phase_2_0_authorization_envelope_draft
envelope_id: p2-0-envelope-001
revision: draft-1
status: draft_not_authorized
phase: phase_2
subphase: phase_2_0
work_unit: P2-0-WU-001
language: ja
created_at: 2026-08-04 11:17:44 JST
updated_at: 2026-08-09 18:11:00 JST
owner: プロジェクト責任者兼設計統括者役
technical_owner: プロジェクト責任者兼設計統括者役
decision_authority: user
accepted: false
```

## 1. Status Boundary

本書はユーザーReview用Draftである。作成されたこと、Gitで追跡されたこと、Phase 2が開始したこと、Task作成Capabilityが存在することは、いずれも本EnvelopeのAcceptanceまたはTask作成許可を意味しない。

```text
Current State:
  draft_not_authorized

Required Next Gate:
  user explicitly accepts this exact revision
  and explicitly requests creation of the listed independent Task
```

## 2. Proposed Authorization

| Field | Draft Value |
|---|---|
| Phase | Phase 2 |
| Subphase | Phase 2-0 |
| Work Unit | P2-0-WU-001 Docs-only Recovery and Authority Acknowledgement |
| Provider | Codex Desktop independent Task capability |
| Allowed Task Count | 1 |
| Maximum Active New Task | 1 |
| Maximum Replacement Task | 0 |
| Task Role | Phase 2設計担当者役 |
| Proposed Task Name | Phase 2 設計担当者役 |
| Work Mode | read-only |
| Automation Level | bounded_unit |
| Authorized Root | Project Manifestで実行時解決 |
| File Write | none |
| Git／GitHub | prohibited |
| External Service | prohibited |
| Secret／Credential | prohibited |
| Destructive Action | prohibited |
| Sub-agent | prohibited |
| Concurrent Writer | 0 |
| Completion | Structured Acknowledgement／Recovery Assessment returned |
| Expiration | End of P2-0-WU-001 or user revocation |

## 3. Allowed Actions

Backup／Dual Consentと本Envelope Acceptanceが成立した後、プロジェクト責任者兼設計統括者役が連結できるAction候補は次だけである。

1. Provider CapabilityをRead-onlyでPreflightする。
2. 1つの独立Taskを作成する。
3. Task名を`Phase 2 設計担当者役`へ設定する。
4. Accepted Handoff Path／Digest、Reading Order、AuthorityおよびExpected Outputを送信する。
5. Authority Acknowledgementを待機／取得する。
6. Acknowledgementが正しい場合に、Read-only Recovery Assessmentを依頼する。
7. Statusを待機／取得する。
8. Scope内の説明不足に対し、最大1回のFollow-upを送る。
9. 結果をReviewし、GO／ADJUST／STOP案をユーザーへ提示する。

Task Pin、Archive、InterruptまたはTitle変更の具体的操作は、Capability PreflightとAccepted Envelopeの範囲内であることを実行直前に確認する。本DraftはPinまたはArchiveを必須Actionにしない。

## 4. Read Scope

Task候補は次をRead-onlyで読める。

1. `docs/project/current/documentation_index_ja.md`
2. `docs/project/current/project_continuity/project_continuity_master_ja.md`
3. `docs/project/shared/project_responsibility_handoff/project_responsibility_handoff_ja.md`
4. `docs/project/shared/history/project_responsibility_handoff/project_responsibility_recovery_manifest_20260804061104.md`
5. `docs/project/shared/design_governance_handoff/design_governance_handoff_ja.md`
6. `docs/project/shared/task_roles/task_role_write_authority_policy_ja.md`
7. `docs/project/shared/operations/documentation_structure_and_task_operations_ja.md`
8. `docs/project/shared/operations/experimental_document_driven_codex_task_orchestration_ja.md`
9. `docs/project/shared/automation/automation_governance_index_ja.md`
10. `docs/project/shared/automation/automation_control_profile_ja.md`
11. `docs/project/shared/automation/automation_governance_evidence_log_ja.md`
12. `docs/project/phases/phase_2/phase_index_ja.md`
13. Phase 2-0のRequirements／Architecture／Governance／Operations／Handoff。

Source Codeは初回Work Unitの復元目的に不要であり、既定Read Scopeに含めない。追加Sourceを必要と判断した場合は、自行読取せずOpen Questionとして返す。

## 5. Write Scope

```text
none
```

TaskはFile作成、編集、削除、Rename、Copy、Move、Permission変更、Format、Cache生成を意図したCommand、Test、GitまたはExternal Actionを実行しない。

## 6. Prohibited Actions

- Project Root内外のFile Mutation。
- Shell／Test／Build／Formatterの実行。
- Git Statusを含むGit Command。初回TaskにGit調査を必要としない。
- GitHub、Lightning、Browser、Network、ConnectorまたはExternal Service操作。
- Secret、Credential、Private Key、個人情報の読取／記録。
- Task、Sub-agent、Thread、ProcessまたはAutomationの新規作成。
- Handoff外の設計変更、要件変更、権限拡張。
- Phase 2-Aへの移行またはPilot成功宣言。

## 7. Required Output

```yaml
acknowledgement:
  role: string
  phase: phase_2
  subphase: phase_2_0
  work_unit: P2-0-WU-001
  read_scope_understood: true_or_false
  write_scope: none
  prohibited_actions: list
  human_gates: list
  stop_conditions: list
  handoff_digest: string

recovery_assessment:
  project_purpose: string
  current_state: string
  completed_phases: list
  active_phase: string
  role_boundaries: mapping
  source_of_truth: list
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

- Reading OrderのFileが存在しない、または読めない。
- Current Stateが文書間で衝突し、優先順位で解決できない。
- Authority、Scope、RoleまたはExpected Outputを解決できない。
- File／Git／External Mutationが必要と判断した。
- TaskのContext／Service／Quotaが安定しない。
- Handoff Digestを確認できない。
- Scope外指示を受けた。

停止時は、推測で穴埋めせず、確認できた最後のState、不明点と必要なHuman Gateだけを返す。

## 9. Resource Boundary

- Active New Taskは1つ。
- Replacement Taskは0。
- Follow-upは最大1回。
- 同じ質問への無制限再試行をしない。
- Usage／Creditが取得できない場合は、追加Taskを作らず本Unitだけで停止できるようにする。

## 10. Expiration／Revocation

次の最初の一つでEnvelopeは失効する。

- P2-0-WU-001 Reviewの確定。
- Taskが停止／Archive対象になる。
- Authority Deviationまたはその疑い。
- ユーザーの取消。
- Envelope Revisionの置換。
- Phase 2-0以外への移行。
- Authorized Root／Allowed Path、Automation ProfileまたはProvider Capabilityの変化。

Expired Envelopeを次Work Unit、Write Pilot、Phase 2-Aまたは交代Taskへ流用しない。

## 11. Acceptance Block

```yaml
accepted_by_user: false
accepted_at: null
accepted_revision: null
task_creation_explicitly_requested: false
large_backup_confirmed: false
controller_ready_declared: false
user_start_declared: false
notes: >-
  ユーザーの後続明示指示があるまでDraftのまま保持する。
```

## 12. Related Documents

- [Pilot Requirements](../requirements/phase_2_0_automation_pilot_requirements_ja.md)
- [Pilot Architecture](../architecture/phase_2_0_automation_pilot_architecture_ja.md)
- [Execution Plan](../operations/phase_2_0_automation_pilot_execution_plan_ja.md)
- [Bootstrap Handoff Draft](../handoffs/phase_2_0_phase_designer_bootstrap_handoff_draft_ja.md)
