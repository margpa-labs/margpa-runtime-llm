# Phase 2設計担当者役 Bounded Write Handoff — P2-0-WU-003 exact-2

```yaml
document_id: phase_2_0_phase_designer_bounded_write_handoff_p2_0_wu_003_exact_2_20260811221832
handoff_id: p2-0-handoff-phase-designer-002
revision: exact-2
status: exact_candidate_user_acceptance_pending
phase: phase_2
subphase: phase_2_0
work_unit: P2-0-WU-003
created_at: 2026-08-11 22:18:32 JST
language: ja
from_role: プロジェクト責任者兼設計統括者役
to_role: Phase 2設計担当者役
task_title: Phase 2設計担当者役 P2-0-WU-003
write_count: 1
supersedes: p2-0-handoff-phase-designer-002/exact-1
```

## 1. Exact Control Package

```text
Envelope ID／Revision : p2-0-envelope-002／exact-2
Envelope Path         : docs/project/phases/phase_2/history/governance/phase_2_0_bounded_documentation_write_envelope_p2_0_wu_003_exact_2_20260811221832.md
Envelope Lines        : 148
Envelope SHA-512      : ab893d07f22dfc8a165eca912a29a2ab78fb5a318810db297f5ca69e7a84e54cba65932dcb8a61fdbbcf09b20cf8beae45119d232652900d0b481c7df724e738

Manifest ID／Revision : p2-0-write-view-manifest-001／exact-1
Manifest Path         : docs/project/phases/phase_2/history/governance/phase_2_0_bounded_documentation_write_manifest_p2_0_wu_003_20260811221344.md
Manifest Lines        : 95
Manifest SHA-512      : 616332df3343c4c73466736d875240afc7f77f2ffc68d4cd46ff7b93973dd2b4742d4fa39ffe4550f1dce4ee11dfac362fc1c4795a0dd86906565ef06e38c5f4

Initial Entry Count   : 7
Initial Package SHA-512: c6efe357d6cacab39948ed8fd3607e58c65ced42a9c8a8c9d124c76f0c273c5c5998597222e5916863e9adb6e1e947740a22cd0d98f04de2c9d500801e94adb0
```

exact-1 Envelope／HandoffはPre-acceptance ReviewでSupersededとなった。Activation、ACKまたは実行に使用しない。

## 2. Initial No-tool ACK

最初の応答ではToolを使用せず、次を構造化して返す。

```text
ACK_STATUS:
Role:
Task Title:
Work Unit:
Parent Role:
Envelope ID／Revision／SHA-512:
Manifest ID／Revision／SHA-512:
Handoff ID／Revision／SHA-512:
Initial Read Entry Count／Package SHA-512:
Exact Write Path:
Allowed Capabilities:
Prohibited Capabilities:
Formal Stop Conditions:
Human Gates:
Open Questions:
```

Handoff SHA-512は、将来作成するFreeze ReceiptおよびInitial Promptから受領する。一項目でも不一致、不明または不足なら`ACK_STATUS: REJECTED`として停止する。Tool、Local ReadまたはMutationを行わない。

## 3. Start Boundary

ACK合格後も自動開始しない。Parent Roleから、このExact Handoffに対する一回の明示Follow-upを受けた場合だけCapabilityを開始する。過去のTask、Acceptance、Start Event、ConversationまたはAuthorityを継承しない。

## 4. Allowed Provider Grammar

対象はControl Package、Manifest Entry、Accepted Differential SupplementおよびExact Result Pathに限定する。

```text
test -f EXACT_PATH
test ! -L EXACT_PATH
test ! -e EXACT_RESULT_PATH
wc -l EXACT_PATH
shasum -a 512 EXACT_PATH
sed -n 'START,ENDp' EXACT_PATH
apply_patch Add File: EXACT_RESULT_PATH
```

ShellのDirectory List、Search、Glob、Recursive Traversal、Git、代替Command、RedirectによるWriteまたは複数Target処理を行わない。`apply_patch`はExact Result Pathへの一回の`Add File`だけに使用する。

## 5. Execution Order

1. Freeze Receiptに記載されたEnvelope、ManifestおよびHandoffのLine Count／SHA-512をExact Pathで検証する。
2. Manifest 7 Entryを記載順に`test -f`、`test ! -L`、`wc -l`、`shasum -a 512`で検証する。
3. 各Entryを`sed -n`の連続Rangeで、Gap／重複なく全文Readする。
4. 根拠が不足する場合はFileを作成せず、Section 6の形式で停止する。
5. 根拠が揃う場合はExact Result Pathへ`test ! -e`を行う。
6. 一回の`apply_patch Add File`で一件だけ作成する。
7. Exact Result Pathだけを全文Readbackし、Line Count／SHA-512を計算する。
8. Conversation ResultをParent Roleへ返し、User Acceptanceを待つ。

失敗後に代替Command、Retry、Cleanupまたは二回目のPatchを行わない。

## 6. Missing Information／Differential Supplement

Initial ViewだけではRequired Resultを根拠付きで作成できない場合は、次を返す。

```text
STATE: PAUSED_MISSING_INFORMATION
Missing Question／Claim:
Why Current View Is Insufficient:
Requested Document Class／Purpose:
Partial Write: none
Mutation State: none
```

Parent RoleがEnvelope exact-2 Section 5を満たすExact Supplementを発行した場合、ChildはPath、Line Count、SHA-512、Purposeおよび失効条件をNo-tool ACKし、Parentの明示Follow-up後にだけ同じRead Contractで追加Readする。

## 7. Exact Write Contract

```text
Exact Result Path:
docs/project/phases/phase_2/history/operations/phase_2_0_layered_recovery_operational_view_result_p2_0_wu_003_20260811220630.md

Allowed Action         : create one regular UTF-8 Markdown file
Existing File Mutation : none
Additional File Create : none
```

Result文書には次を含める。

- `status: completed_controller_review_pending`
- Logical Author、From Role、To Role、Task Title、Work Unit
- Envelope／Manifest／Handoff Identity
- Consumed Initial Viewと、使用した場合だけDifferential Supplement
- Current Phase／Subphase／Pilot State
- 自RoleのExecution／Docs Authority
- Absolute Prohibitions／Human Gates
- Missing Information／Contradictionの有無
- Result自身のDigestは外部Evidenceとして計算・報告するという契約
- Mutation Report
- First Safe Next Action

Result自身へ最終Line Count／SHA-512値を埋め込まない。値は作成後のConversation ResultとController Reviewに保持する。

## 8. Formal Stop Conditions

```text
STOP-IDENTITY-MISMATCH
STOP-CONTROL-PACKAGE-MISMATCH
STOP-DIGEST-OR-LINE-MISMATCH
STOP-MISSING-OR-UNREADABLE-ENTRY
STOP-SYMLINK-OR-BOUNDARY-UNCERTAINTY
STOP-TARGET-ALREADY-EXISTS
STOP-MISSING-INFORMATION
STOP-UNEXPECTED-MUTATION
STOP-SECOND-ARTIFACT-REQUIRED
STOP-PROVIDER-RESOURCE-CONTEXT-ERROR
STOP-SUPREME-RULE-AUTHORITY-HUMAN-GATE-CONFLICT
```

Stop後は原因を隠すCleanup、削除、Rollback、再試行、代替CommandまたはScope拡張を行わない。

## 9. Prohibited Capabilities

```text
Authorized Root外Access
Control Verification／Manifest／Accepted Supplement外Read
Directory List／Search／Glob／Recursive Traversal
Existing File Mutation／Second File Creation
Git／GitHub／External／Network／Secret
Permission／ACL／Delete／Rename／Move
Task／Sub-agent Creation
Phase 2-A／Stage 3／Next Work Unit Start
```

## 10. Result Report

```text
FINAL_STATE:
ACK_RESULT:
CONTROL_PACKAGE_VERIFICATION:
READ_COVERAGE:
DIFFERENTIAL_SUPPLEMENT:
WRITE_RESULT:
CREATED_PATH:
CREATED_LINES:
CREATED_SHA512:
MUTATION_REPORT:
CONTRADICTIONS／MISSING_INFORMATION:
FIRST_SAFE_NEXT_ACTION:
```

Parent RoleのReviewとUser Acceptanceを待ち、次Work Unitへ自動移行しない。

## 11. Related Documents

- [Exact Envelope exact-2](../governance/phase_2_0_bounded_documentation_write_envelope_p2_0_wu_003_exact_2_20260811221832.md)
- [Exact Manifest exact-1](../governance/phase_2_0_bounded_documentation_write_manifest_p2_0_wu_003_20260811221344.md)
- [Superseded Handoff exact-1](phase_2_0_phase_designer_bounded_write_handoff_p2_0_wu_003_20260811221344.md)
- [Design Candidate](../operations/phase_2_0_bounded_documentation_write_candidate_p2_0_wu_003_20260811220630.md)
