# Phase 2-0 Bounded Documentation Write Envelope — P2-0-WU-003

```yaml
document_id: phase_2_0_bounded_documentation_write_envelope_p2_0_wu_003_20260811221344
envelope_id: p2-0-envelope-002
revision: exact-1
status: exact_candidate_user_acceptance_pending
phase: phase_2
subphase: phase_2_0
work_unit: P2-0-WU-003
created_at: 2026-08-11 22:13:44 JST
language: ja
issuer: プロジェクト責任者兼設計統括者役
decision_authority: user
automation_level: bounded_unit
control_state: PAUSED_EXACT_PACKAGE
task_limit: 1
```

## 1. Authorized Outcome Candidate

新しい`Phase 2設計担当者役 P2-0-WU-003`一件が、Exact Initial Operational Viewを読み、必要なら許可範囲内のDifferential Supplementを要求し、次の新規History文書一件だけを作成してController Reviewへ返す。

```text
docs/project/phases/phase_2/history/operations/phase_2_0_layered_recovery_operational_view_result_p2_0_wu_003_20260811220630.md
```

本Envelopeは`P2-0-WU-002`のAuthorityを継承せず、Phase 2-A、Stage 3、Stable Docs変更またはGit操作を含まない。

## 2. Effective Authority

```text
Human-defined Supreme Rules
  ∩ Role Authority Matrix／phase_designer
  ∩ this Exact Envelope
  ∩ Exact Manifest／Accepted Differential Supplement
  ∩ Available Provider Capability
```

Role名、Task名、親RoleのAuthorityまたはAutomation `ON`だけでは権限を追加しない。

## 3. Exact Task Identity

```text
Task Title    : Phase 2設計担当者役 P2-0-WU-003
Role          : Phase 2設計担当者役
Role Archetype: phase_designer
Work Unit     : P2-0-WU-003
Parent Role   : プロジェクト責任者兼設計統括者役
Task Count    : exactly one new Task
Old Task Use  : none
```

## 4. Allowed Capabilities

| Capability | Boundary |
|---|---|
| Identity／Authority ACK | Tool Call前にMachine-readable応答 |
| Exact Text Read | Accepted ManifestまたはAccepted Differential Supplementだけ |
| Exact Digest Verification | 指定Entryだけ |
| Exact New File Create | Section 1の一Pathだけ |
| Created File Readback | Section 1の一Pathだけ |
| Conversation Status／Result | Parent Role宛て |

Provider固有Tool SequenceはFrozen Handoffへ投影し、Core Authorityを拡張しない。

## 5. Differential Supplement Delegation

Childが`PAUSED_MISSING_INFORMATION`として具体的な不足を返した場合、親Roleは次を全て満たすRead-only Supplementだけを発行できる。

- 現在のAuthorized Root内
- 同一Phase／Subphase／Work Unit目的内
- Childが示した不足へ直接必要
- 既知のExact File Path
- Line Count／SHA-512／Purpose／失効条件付き
- Mutation、Directory探索、Git、ExternalまたはSecretなし
- Minimum Necessary

Supplement発行はTaskのWrite Countを増やさず、Childへ新しいWrite Authorityを与えない。上記を満たせない場合、親RoleはScopeを拡張せずユーザーへ戻す。

## 6. Exact Documentation Authority

```text
Initial Manifest Read        : READ
Accepted Differential Read   : READ
Exact Result Path            : CREATE_NEW／one file
Existing Phase Stable Docs   : READ only when listed／WRITE DENY
Existing History             : READ only when listed／MUTATION DENY
Other New Artifacts          : DENY
```

Result文書は、Task Identity、Consumed View、Current State、Authority、Missing Information、Differential Supplement、Created File Digest、Mutation ReportおよびFirst Safe Next Actionを保持する。

## 7. Prohibited Actions

- Authorized Root外Access
- Initial Manifest／Accepted Supplement外Read
- Directory List、Search、Glob、Recursive Traversalまたは代替Path
- Existing Fileの編集、上書き、移動、削除またはPermission変更
- 二件目以降のFile作成
- Git／GitHub／Network／External／Secret
- Task／Sub-agent作成
- Cleanup／Rollback
- Phase 2-A、Stage 3または次Work Unit開始
- 最上位規則、AuthorityまたはEnvelopeの自己変更

## 8. Stop Conditions

次のいずれかでFail-closedとする。

- ACK Field不一致または欠落
- Envelope／Manifest／Handoff Digest不一致
- Entry欠落、Unreadable、Symlink、Line CountまたはSHA-512不一致
- Exact Write Targetが開始前に存在
- Root／Manifest／Role／Write Scope外の情報またはActionが必要
- Required Outputを根拠付きで作成できない
- Unexpected Mutationまたは二件目Artifactの疑い
- Provider／Resource／Context異常
- 最上位規則、Human GateまたはAuthority Conflict

停止後にCleanup、削除、修正、再試行またはScope拡張を自己承認しない。

## 9. Human Gates／State Transition

```text
Current:
  PAUSED_EXACT_PACKAGE

Required before Task Creation:
  Envelope／Manifest／Handoff Exact Digests
  Controller Review
  User Exact Package Acceptance／Task Creation Authorization

Required before Capability:
  Controller READY
  User Start
  Task ACK PASS

After Child Result:
  Controller independent review
  User Acceptance
```

本EnvelopeがAcceptedされても、ユーザーのStart Event前にCapabilityを実行しない。Work Unit完了後も次Stageへ自動移行しない。

## 10. Completion Criteria

- Initial Viewの7 EntryがExact一致する。
- 情報不足時に無許可探索せず正確にEscalateできる。
- 一つのExact新規History Fileだけを作成する。
- Existing Stable／History Mutation、Git／External／Secret／Task Creationが0である。
- Controllerが差分、内容、Digest、AuthorityおよびCostを独立Reviewできる。
- User Acceptance前に次Work Unitへ進まない。

## 11. Expiration／Revocation

Manifest、Handoff、Task Identity、Write Target、Role Authority、Authorized RootまたはProvider Capabilityの変化で失効する。ユーザーまたはHuman-only Authorityは開始前後を問わず停止・取消できる。

## 12. Related Documents

- [Exact Manifest](phase_2_0_bounded_documentation_write_manifest_p2_0_wu_003_20260811221344.md)
- [Design Candidate](../operations/phase_2_0_bounded_documentation_write_candidate_p2_0_wu_003_20260811220630.md)
- [Role Authority Matrix](../../../../shared/task_roles/role_authority_matrix_ja.md)
- [Automation Control Profile](../../../../shared/automation/automation_control_profile_ja.md)
