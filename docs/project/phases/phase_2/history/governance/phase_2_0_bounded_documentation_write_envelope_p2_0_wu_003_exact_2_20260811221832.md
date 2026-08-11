# Phase 2-0 Bounded Documentation Write Envelope — P2-0-WU-003 exact-2

```yaml
document_id: phase_2_0_bounded_documentation_write_envelope_p2_0_wu_003_exact_2_20260811221832
envelope_id: p2-0-envelope-002
revision: exact-2
status: exact_candidate_user_acceptance_pending
phase: phase_2
subphase: phase_2_0
work_unit: P2-0-WU-003
created_at: 2026-08-11 22:18:32 JST
language: ja
issuer: プロジェクト責任者兼設計統括者役
decision_authority: user
automation_level: bounded_unit
control_state: PAUSED_EXACT_PACKAGE
task_limit: 1
supersedes: p2-0-envelope-002/exact-1
```

## 1. Correction from exact-1

Pre-acceptance Reviewで、Result文書自身へ最終SHA-512を埋め込む自己参照契約と、Exact Target不存在確認用Capabilityの記載不足を検出した。exact-1をHistoryとして保持し、本exact-2で次のように修正する。

- Result文書自身には最終Digest値を埋め込まない。
- Childは作成後にLine Count／SHA-512を計算し、Conversation Resultへ外部Evidenceとして返す。
- Controllerが独立再計算してReview文書へ固定する。
- Exact Target不存在確認用の`test ! -e`を、対象一Path限定で許可する。
- Envelope／Manifest／HandoffのControl Packageは、Capability開始時にExact PathのLine Count／SHA-512だけを検証できる。

exact-1をActivation、AcceptanceまたはTask入力へ使用しない。

## 2. Authorized Outcome Candidate

新しい`Phase 2設計担当者役 P2-0-WU-003`一件が、Exact Initial Operational Viewを読み、必要なら許可範囲内のDifferential Supplementを要求し、次の新規History文書一件だけを作成してController Reviewへ返す。

```text
docs/project/phases/phase_2/history/operations/phase_2_0_layered_recovery_operational_view_result_p2_0_wu_003_20260811220630.md
```

Phase 2-A、Stage 3、Stable Docs変更またはGit操作は含まない。

## 3. Effective Authority／Task Identity

```text
Human-defined Supreme Rules
  ∩ Role Authority Matrix／phase_designer
  ∩ this Exact Envelope
  ∩ Exact Manifest／Accepted Differential Supplement
  ∩ Available Provider Capability

Task Title    : Phase 2設計担当者役 P2-0-WU-003
Role          : Phase 2設計担当者役／phase_designer
Work Unit     : P2-0-WU-003
Parent Role   : プロジェクト責任者兼設計統括者役
Task Count    : exactly one new Task
Old Task Use  : none
```

Role名、Task名、親RoleのAuthorityまたはAutomation `ON`だけでは権限を追加しない。

## 4. Allowed Capabilities

| Capability | Boundary |
|---|---|
| Identity／Authority ACK | Tool Call前にMachine-readable応答 |
| Exact Control Package Verification | Accepted Envelope／Manifest／HandoffのExact Pathに対するLine Count／SHA-512だけ |
| Exact Text Read | Accepted ManifestまたはAccepted Differential Supplementだけ |
| Exact Digest Verification | 指定Entryだけ |
| Exact Target Absence Check | Section 2の一Pathに対する`test ! -e`だけ |
| Exact New File Create | Section 2の一Pathに対する`apply_patch Add File`だけ |
| Created File Readback | Section 2の一Pathだけ |
| Conversation Status／Result | Parent Role宛て |

## 5. Differential Supplement Delegation

Childが`PAUSED_MISSING_INFORMATION`として具体的な不足を返した場合、親Roleは次を全て満たすRead-only Supplementだけを発行できる。

- 現在のAuthorized Root内
- 同一Phase／Subphase／Work Unit目的内
- Childが示した不足へ直接必要
- 既知のExact File Path
- Line Count／SHA-512／Purpose／失効条件付き
- Mutation、Directory探索、Git、ExternalまたはSecretなし
- Minimum Necessary

SupplementはTaskのWrite Countを増やさず、Childへ新しいWrite Authorityを与えない。条件を満たせない場合はScopeを拡張せずユーザーへ戻す。

## 6. Documentation Authority

```text
Initial Manifest Read        : READ
Accepted Differential Read   : READ
Exact Result Path            : CREATE_NEW／one file
Existing Stable Docs         : READ only when listed／WRITE DENY
Existing History             : READ only when listed／MUTATION DENY
Other New Artifacts          : DENY
```

Result文書はTask Identity、Consumed View、Current State、Authority、Missing Information、Differential Supplementの有無、Mutation Report、Digestを外部Evidenceとして計算する契約およびFirst Safe Next Actionを保持する。Result自身の最終Line Count／SHA-512値はConversation ResultとController Reviewに保持する。

## 7. Prohibited Actions

- Authorized Root外Access
- Control Package Verification、Initial ManifestまたはAccepted Supplement外Read
- Directory List、Search、Glob、Recursive Traversalまたは代替Path
- Existing Fileの編集、上書き、移動、削除またはPermission変更
- 二件目以降のFile作成
- Git／GitHub／Network／External／Secret
- Task／Sub-agent作成
- Cleanup／Rollback
- Phase 2-A、Stage 3または次Work Unit開始
- 最上位規則、AuthorityまたはEnvelopeの自己変更

## 8. Stop Conditions

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

## 9. Gate／Completion

```text
Current State         : PAUSED_EXACT_PACKAGE
Before Task Creation  : Exact Digests／Controller Review／User Acceptance
Before Capability     : Controller READY／User Start／Task ACK PASS
After Child Result    : Controller Independent Review／User Acceptance
```

Completionには、7 Entry一致、必要時の正しい不足報告、一つの新規History Fileだけの作成、既存File Mutation 0、外部EvidenceとしてのLine Count／SHA-512、独立Reviewおよび次Stage非開始を必要とする。

## 10. Expiration／Related Documents

Manifest、Handoff、Task Identity、Write Target、Role Authority、Authorized RootまたはProvider Capabilityの変化で失効する。ユーザーは開始前後を問わず停止・取消できる。

- [Exact Manifest exact-1](phase_2_0_bounded_documentation_write_manifest_p2_0_wu_003_20260811221344.md)
- [Superseded Envelope exact-1](phase_2_0_bounded_documentation_write_envelope_p2_0_wu_003_20260811221344.md)
- [Design Candidate](../operations/phase_2_0_bounded_documentation_write_candidate_p2_0_wu_003_20260811220630.md)
- [Role Authority Matrix](../../../../shared/task_roles/role_authority_matrix_ja.md)
- [Automation Control Profile](../../../../shared/automation/automation_control_profile_ja.md)
