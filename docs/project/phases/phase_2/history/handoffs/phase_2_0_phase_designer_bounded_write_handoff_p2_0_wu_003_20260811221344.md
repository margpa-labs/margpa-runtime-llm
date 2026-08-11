# Phase 2設計担当者役 Bounded Write Handoff — P2-0-WU-003

```yaml
document_id: phase_2_0_phase_designer_bounded_write_handoff_p2_0_wu_003_20260811221344
handoff_id: p2-0-handoff-phase-designer-002
revision: exact-1
status: exact_candidate_user_acceptance_pending
phase: phase_2
subphase: phase_2_0
work_unit: P2-0-WU-003
created_at: 2026-08-11 22:13:44 JST
language: ja
from_role: プロジェクト責任者兼設計統括者役
to_role: Phase 2設計担当者役
task_title: Phase 2設計担当者役 P2-0-WU-003
write_count: 1
```

## 1. Exact Accepted Inputs Required before Activation

```text
Envelope ID       : p2-0-envelope-002
Envelope Revision : exact-1
Envelope Path     : docs/project/phases/phase_2/history/governance/phase_2_0_bounded_documentation_write_envelope_p2_0_wu_003_20260811221344.md
Envelope Lines    : 164
Envelope SHA-512  : d4c04dd9e494d4f333476037ed49cca89619ac6dc0b7436945236ec6ea6432d0fc386576cb085ec3900cb9bd43d314ad672fa9b4cd71175f573c1248ba3777b5

Manifest ID       : p2-0-write-view-manifest-001
Manifest Revision : exact-1
Manifest Path     : docs/project/phases/phase_2/history/governance/phase_2_0_bounded_documentation_write_manifest_p2_0_wu_003_20260811221344.md
Manifest Lines    : 95
Manifest SHA-512  : 616332df3343c4c73466736d875240afc7f77f2ffc68d4cd46ff7b93973dd2b4742d4fa39ffe4550f1dce4ee11dfac362fc1c4795a0dd86906565ef06e38c5f4
```

本Handoff、Envelope、Manifest、Task作成、Controller READYおよびUser StartがExact一致するまで、Tool CallまたはLocal Readを行わない。

## 2. Initial No-tool ACK

最初の応答ではToolを使わず、次を構造化して返す。

```text
ACK_STATUS:
Role:
Task Title:
Work Unit:
Parent Role:
Envelope ID／Revision／SHA-512:
Manifest ID／Revision／SHA-512:
Initial Read Entry Count:
Initial Package SHA-512:
Exact Write Path:
Allowed Capabilities:
Prohibited Capabilities:
Formal Stop Conditions:
Human Gates:
Open Questions:
```

一項目でも不一致、不明または不足なら`ACK_STATUS: REJECTED`として停止する。自然言語上の推測でFieldを補完しない。

## 3. Start Boundary

ACKが完全一致した後も自動開始しない。Parent Roleから、このExact Handoffに対する一回の明示Follow-upを受けた場合だけCapabilityを開始する。

過去のTask、Envelope Acceptance、Start Event、ConversationまたはAuthorityを継承しない。

## 4. Exact Initial Read Contract

Manifest `p2-0-write-view-manifest-001／exact-1`の7 Entryを記載順に処理する。各Entryで次を行う。

1. `wc -l`でExact Line Countを確認する。
2. `shasum -a 512`でExact Digestを確認する。
3. `sed -n`による連続Page Readで全文を欠落なく読む。
4. Expected値と一致しない場合は後続Read／Writeを行わず停止する。

許可されたCommand Grammarは、Manifest記載のExact Fileを対象とする`wc -l`、`shasum -a 512`および`sed -n`だけである。Directory List、Search、Glob、Recursive Traversal、Gitまたは代替Commandを使用しない。

Page Rangeは重複またはGapなく全行を覆う。Command失敗、出力欠落またはTruncationが疑われる場合は推測で継続しない。

## 5. Missing Information／Differential Supplement

Initial ViewだけではRequired Resultを根拠付きで作成できない場合、Fileを作成せず次をParent Roleへ返す。

```text
STATE: PAUSED_MISSING_INFORMATION
Missing Question／Claim:
Why Current View Is Insufficient:
Requested Document Class／Purpose:
Partial Write: none
Mutation State: none
```

Parent RoleがEnvelope Section 5内でExact Differential Supplementを発行した場合は、Path、Line Count、SHA-512、Purposeおよび失効条件をNo-tool ACKし、明示Follow-up後にだけ同じRead Contractで追加Readする。

## 6. Exact Write Contract

Initial ViewまたはAccepted Differential Supplementにより根拠が揃った場合だけ、開始前に次のTargetが存在しないことをExact Pathで確認する。

```text
docs/project/phases/phase_2/history/operations/phase_2_0_layered_recovery_operational_view_result_p2_0_wu_003_20260811220630.md
```

Targetが存在する場合は上書きせず停止する。存在しない場合は、`apply_patch`の`Add File`でこの一件だけを作成する。

Result文書には次を含める。

- `status: completed_controller_review_pending`
- Logical Author、From Role、To Role、Task Title、Work Unit
- Envelope／Manifest／Handoff Identity
- Consumed Initial Viewと、使用した場合だけDifferential Supplement
- Current Phase／Subphase／Pilot State
- 自RoleのExecution／Docs Authority
- Absolute Prohibitions／Human Gates
- Missing Information／Contradictionの有無
- Created FileのLine Count／SHA-512
- Mutation Report
- First Safe Next Action

Phase 2-A設計、Stable Docs編集、既存History編集または次Stage開始を含めない。

## 7. Post-write Verification

作成後はExact Targetだけを対象に、全文Readback、Line CountおよびSHA-512を確認する。不足や誤りを検出しても、二回目のPatch、削除、置換またはCleanupを自己承認せず停止してExact Stateを報告する。

## 8. Formal Stop Conditions

```text
STOP-IDENTITY-MISMATCH
STOP-ENVELOPE-MISMATCH
STOP-MANIFEST-MISMATCH
STOP-HANDOFF-MISMATCH
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

Stop後は、原因を隠すCleanup、削除、Rollback、再試行、代替CommandまたはScope拡張を行わない。

## 9. Prohibited Capabilities

```text
Authorized Root外Access
Manifest／Accepted Supplement外Read
Directory List／Search／Glob／Recursive Traversal
Existing File Mutation
Second File Creation
Git／GitHub／External／Network／Secret
Permission／ACL／Delete／Rename／Move
Task／Sub-agent Creation
Phase 2-A／Stage 3／Next Work Unit Start
```

## 10. Result Report to Parent

Conversation Outputで次を返す。

```text
FINAL_STATE:
ACK_RESULT:
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

- [Exact Envelope](../governance/phase_2_0_bounded_documentation_write_envelope_p2_0_wu_003_20260811221344.md)
- [Exact Manifest](../governance/phase_2_0_bounded_documentation_write_manifest_p2_0_wu_003_20260811221344.md)
- [Design Candidate](../operations/phase_2_0_bounded_documentation_write_candidate_p2_0_wu_003_20260811220630.md)
