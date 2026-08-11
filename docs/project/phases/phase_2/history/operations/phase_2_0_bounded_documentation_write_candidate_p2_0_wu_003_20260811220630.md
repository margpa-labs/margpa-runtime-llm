# Phase 2-0 Bounded Documentation Write Candidate — P2-0-WU-003

```yaml
document_id: phase_2_0_bounded_documentation_write_candidate_p2_0_wu_003_20260811220630
status: design_candidate_user_acceptance_pending
phase: phase_2
subphase: phase_2_0
work_unit: P2-0-WU-003
stage: bounded_documentation_write
created_at: 2026-08-11 22:06:30 JST
language: ja
owner: プロジェクト責任者兼設計統括者役
decision_authority: user
task_candidate: Phase 2設計担当者役 P2-0-WU-003
automation_level: bounded_unit
control_state: PAUSED_DESIGN_CANDIDATE
```

## 1. Purpose

`P2-0-WU-002`で合格したRead-only Cold Recoveryの次段として、一つの新規History文書だけを作成するBounded Documentation Writeを検証する。同時に、Full CorpusではなくPhase／Work Unitに必要なOperational Viewだけを最初に与え、不足時に親Roleが差分Packageを追加するLayered Recoveryの成立性を観測する。

本Candidateは設計であり、Task作成、File Write、Automation再開またはPhase 2-A開始を許可しない。

## 2. Proposed Task／Role

```text
Task Title     : Phase 2設計担当者役 P2-0-WU-003
Role           : Phase 2設計担当者役／phase_designer
Task Instance  : new／independent／no old conversation inheritance
Parent         : プロジェクト責任者兼設計統括者役
Write Count    : exactly one new file
Stable Mutation: none
History Rewrite: none
```

Task TitleへWork Unit IDを付けるのは、本Pilot Instance、Handoff、Write結果およびEvidenceを一対一で追跡するためである。将来の全Taskへ同形式を固定する命名規則ではない。

## 3. Initial Operational View

初期Read Scopeは、次のExact Relative Pathだけを候補とする。Directory List、Search、Glob、Git History、Networkまたは別Taskからの補完は含めない。

1. `docs/project/shared/operations/research_asset_mutation_control_ja.md`
2. `docs/project/shared/task_roles/role_authority_matrix_ja.md`
3. `docs/project/shared/automation/automation_control_profile_ja.md`
4. `docs/project/phases/phase_2/phase_index_ja.md`
5. `docs/project/phases/phase_2/history/operations/phase_2_0_bounded_read_retest_review_20260811210503.md`
6. `docs/project/phases/phase_2/history/operations/phase_2_0_bounded_read_user_acceptance_p2_0_wu_002_20260811220630.md`
7. `docs/project/shared/history/automation/automation_governance_evidence_phase_2_task_identity_and_layered_recovery_ja_20260811220038.md`

Activation前に、各FileのLine Count、SHA-512、Ordered Path-setおよびPackage DigestをDetached Freeze Evidenceへ固定する。

## 4. Differential Supplement Contract

Initial Operational ViewだけではRequired Outputを根拠付きで作成できない場合、Child Taskは探索または推測で補完せず、次をConversation Outputで親Roleへ返して`PAUSED_MISSING_INFORMATION`となる。

```text
Missing Question／Claim
Why Current View Is Insufficient
Requested Document Class／Purpose
Whether Any Partial Write Occurred
Current Mutation State
```

親Roleは不足内容をReviewし、現在のUser-approved Completion Line、Role AuthorityおよびCost内で必要と判断できる場合だけ、Exact Path、Digest、Read Purposeおよび失効条件を持つDifferential Packageを追加する。追加がScope／Authority拡張またはHuman-only判断に該当する場合はユーザーへ戻す。

差分追加後はACKとDigestを再確認し、追加前の不足を曖昧に消去しない。

## 5. Exact Write Candidate

```text
Action     : create one new append-only History artifact
Exact Path : docs/project/phases/phase_2/history/operations/phase_2_0_layered_recovery_operational_view_result_p2_0_wu_003_20260811220630.md
Must Exist Before Start: no
Allowed Existing File Mutation: none
Delete／Rename／Move／Permission: none
```

Result文書は少なくとも次を含む。

- Exact Task Identity、Role、Work UnitおよびParent
- 読んだInitial Operational ViewとDigest照合結果
- Current Phase／Subphase／Pilot Stateの復元
- 自RoleのExecution／Docs Authorityと禁止事項
- 一つのExact Write Scope
- Missing Information、ContradictionまたはDifferential Supplement要求の有無
- 作成FileのLine Count／SHA-512
- Mutation Report
- First Safe Next Action

既存文書の要約置換、Phase 2-A設計、Source実装または次Stageの開始を成果物へ含めない。

## 6. Allowed Capability Candidate

```text
READ_EXACT_TEXT       : section 3 exact paths only
VERIFY_EXACT_DIGEST   : frozen manifest entries only
CREATE_EXACT_NEW_FILE : section 5 exact path only
VERIFY_CREATED_FILE   : exact path line count／SHA-512／content readback
CONVERSATION_STATUS   : parentへのACK／status／result
```

次は許可候補へ含めない。

- Directory探索、Recursive Read、Globまたは代替Path
- Initial／Differential Package外Read
- Existing File Write
- 二件目のFile作成
- Git／GitHub／External／Network／Secret
- Permission／ACL／Delete／Rename／Move／Cleanup／Rollback
- Task／Sub-agent作成
- Phase 2-A開始

## 7. Stop Conditions

次のいずれかを検出した場合、Write前ならMutation 0のまま、Write後なら追加修正やCleanupをせず停止する。

- Task Identity、Envelope、HandoffまたはDigest不一致
- Initial Viewの欠落、Unreadable、SymlinkまたはExpected Digest不一致
- Exact Write Targetが開始前から存在する
- Package外情報が必要
- 一つの新規File以外のMutationが疑われる
- Required Outputを根拠付きで作れない
- Provider／Resource／Context異常
- 最上位規則、Authorized Root、Role AuthorityまたはHuman GateとのConflict

## 8. Review／Acceptance Chain

```text
Phase Designer ACK
  -> Initial Operational View Read
  -> optional PAUSED_MISSING_INFORMATION／Differential Supplement
  -> exactly one History File Create
  -> Phase Designer Result／Mutation Report
  -> Controller independent diff／content／digest review
  -> Controller GO／ADJUST／STOP proposal
  -> User Acceptance
```

User Acceptance後でもStage 3、追加Task、Stable Docs WriteまたはPhase 2-Aへ自動移行しない。

## 9. Acceptance Criteria

- Task作成前のExact Package AcceptanceとTwo-key Startが成立する。
- Initial Operational Viewだけで完了できたか、必要な差分追加を正しく要求できたかを説明できる。
- 一つのExact新規History Fileだけが作成される。
- Existing Stable／History Mutationが0である。
- Role／Authority／Stop／Human Gateを誤認しない。
- ControllerがChild成果とWorking Tree差分を独立Reviewできる。
- Context、Tool Call、追加ReadおよびHuman Intervention Costを記録できる。

## 10. Current Gate

```text
P2-0-WU-002 User Acceptance : complete
P2-0-WU-003 Design          : candidate
Envelope／Manifest／Handoff : not frozen
New Task                    : not created
Controller READY            : no
User Acceptance             : pending
User Start                  : no
Automation                  : PAUSED
```

## 11. Related Documents

- [P2-0-WU-002 User Acceptance](phase_2_0_bounded_read_user_acceptance_p2_0_wu_002_20260811220630.md)
- [P2-0-WU-002 Controller Review](phase_2_0_bounded_read_retest_review_20260811210503.md)
- [Task Identity／Layered Recovery Evidence](../../../../shared/history/automation/automation_governance_evidence_phase_2_task_identity_and_layered_recovery_ja_20260811220038.md)
- [Pilot Architecture](../../architecture/phase_2_0_automation_pilot_architecture_ja.md)
- [Role Authority Matrix](../../../../shared/task_roles/role_authority_matrix_ja.md)
