# Phase 2設計担当者役 Documentation Capability Retest Handoff — P2-0-WU-004 exact-1

```yaml
document_id: phase_2_0_phase_designer_capability_retest_handoff_p2_0_wu_004_exact_1_20260811233209
handoff_id: p2-0-handoff-phase-designer-003
revision: exact-1
status: exact_candidate_user_acceptance_pending
phase: phase_2
subphase: phase_2_0
work_unit: P2-0-WU-004
created_at: 2026-08-11 23:32:09 JST
language: ja
from_role: プロジェクト責任者兼設計統括者役
to_role: Phase 2設計担当者役
task_title: Phase 2設計担当者役 P2-0-WU-004
task_limit: 1
write_count: 1
```

## 1. Exact Control Package

```text
Envelope ID／Revision : p2-0-envelope-003／exact-1
Envelope Path         : docs/project/phases/phase_2/history/governance/phase_2_0_documentation_capability_envelope_p2_0_wu_004_exact_1_20260811233209.md
Envelope Lines        : 184
Envelope SHA-512      : c3535189a8e7ebad1b46d86476a2c99031604869df5eafbfa2195af1a2a623ef12c4aa89ec4c729bb8b602aa2c0bde620d28f7b244a932978bdf5abbb5cb4cb8

Manifest ID／Revision : p2-0-documentation-capability-manifest-001／exact-1
Manifest Path         : docs/project/phases/phase_2/history/governance/phase_2_0_documentation_capability_manifest_p2_0_wu_004_exact_1_20260811233209.md
Manifest Lines        : 114
Manifest SHA-512      : 13352b02fb4a71156535cd9f3691587d3d7a05df6a4c0eeff0bc831c3621ffa2235ed607140fd2393970a627a566d2f69a5606dd603dc81fe82150fea8b0a706

Manifest Entry Count  : 6
Manifest Total Lines  : 1,324
Ordered Package SHA-512: 033b7d11d771beb477099984ebd4a023a9db9c8e12678e4b3f369adcf417d6a5dd3734727d266b6ae207cd23bb7053edb57fbc33f0b9e4a2db0a6a2e10496826
```

Freeze Receiptで本Handoff自身のLine Count／SHA-512を追加し、三文書のExact Identityを固定する。Receiptが存在しない、またはIdentityが一致しない場合はACKを受理しない。

## 2. Initial No-tool ACK

Taskの最初の応答ではTool、Filesystem Read、Mutationまたは外部Actionを一切行わず、次を構造化して返す。

```text
ACK_STATUS:
Role:
Task Title:
Work Unit:
Parent Role:
Automation Level／Control State:
Envelope ID／Revision／Lines／SHA-512:
Manifest ID／Revision／Lines／SHA-512:
Handoff ID／Revision／Lines／SHA-512:
Freeze Receipt ID／Revision／Lines／SHA-512:
Manifest Entry Count／Total Lines／Ordered Package SHA-512:
Exact Result Path:
Allowed Capability Semantics:
Provider Mapping Mode:
Mechanical Enforcement Claim:
Read Cardinality／Batch State:
Document Authority:
Prohibited Capability Classes:
Formal Stop Conditions:
Human Gates:
Open Questions:
```

一項目でも欠落、不明、不一致または推測補完があれば`ACK_STATUS: REJECTED`として停止する。ACK合格はCapability Startを意味しない。

## 3. Start Boundary

ACKがController Reviewで合格した後も自動開始しない。次の二条件を両方満たした場合だけP2-0-WU-004を開始する。

1. ControllerがExact Packageに対してREADY／ARMEDを宣言する。
2. ユーザーがその後にP2-0-WU-004の開始を明示する。

過去のAcceptance、READY、Start、別Task、別Work Unitまたは会話上の包括許可を継承しない。

## 4. Capability Semantics

### 4.1 Read

```text
Capability          : bounded_documentation_read／exact_single_target_read
Allowed Targets     : Control PackageとManifest 6 Entryだけ
Target Cardinality  : one exact target per invocation
Required Coverage   : complete content
Required Integrity  : exact line count + SHA-512
Batch Capability    : unavailable／deny
Discovery           : deny
```

Provider固有のRaw Command名は規範契約にしない。TaskはProvider Adapterの`semantic_mapping`に従い、一回のInvocationで一つのExact Targetだけを処理する。

各Targetについて次を保持・報告する。

- Exact Relative Path。
- Actual Invocation Class。
- Exact Target Count。
- Observed Line Count／SHA-512。
- Coverage Complete／Incomplete。
- Truncation、GapまたはOverlap。
- Provider Trace Available／Unavailable。
- Capability Deviationの有無。

ProviderがRaw Traceを返さない場合は`unverified`とし、使ったCommandや内部動作を推測しない。

### 4.2 Create

```text
Capability:
bounded_documentation_create

Exact Result Path:
docs/project/phases/phase_2/history/operations/phase_2_0_documentation_capability_conformance_result_p2_0_wu_004_20260811233209.md

Create Cardinality       : exactly one
Existing File Mutation   : zero
Additional Artifact      : zero
Patch／Create Invocation  : exactly one
```

Exact Result Pathが既に存在する場合は作成しない。別名、Suffix変更、上書き、二回目のPatchまたは一時Artifactで迂回しない。

## 5. Execution Order

1. Freeze ReceiptのExact Identityだけを確認する。
2. Envelope、Manifest、HandoffおよびReceiptを一Targetずつ検証・全文Readする。
3. Manifest 6 Entryを記載順に、一TargetずつIdentity検証・全文Readする。
4. 各InvocationのCardinality、Coverage、DigestおよびTrace Availabilityを記録する。
5. 不足、矛盾またはDeviationがあればMutationせずFormal Stopする。
6. Exact Resultが不存在であることを確認する。
7. 一回の`bounded_documentation_create`でExact Resultを作成する。
8. Exact Resultだけを一Targetとして全文Readbackし、Line Count／SHA-512を算出する。
9. Conversation ResultをParent Roleへ返して停止する。

失敗後の自動Retry、代替Provider Grammar、Cleanup、Rollback、Scope拡張または二回目のMutationを行わない。

## 6. Exact Result Requirements

Result文書へ次を含める。

1. `status: completed_controller_review_pending`またはFormal Stopに対応する状態。
2. From Role、To Role、Task Title、Work Unit。
3. Envelope／Manifest／Handoff／Receipt Identity。
4. Consumed Target全件とCoverage。
5. Capability Semantics、Provider Mapping ModeおよびMechanical Enforcement Claim。
6. EntryごとのInvocation Class、Target Count、Provider Trace AvailabilityおよびDeviation。
7. Authority、Scope、Capability Semantics、Provider Mapping、Result、Evidence、Stop／Recoveryの独立自己評価候補。
8. P2-0-WU-003のResult／Reviewを変更、削除または遡及Acceptanceしていないこと。
9. Exact Mutation Report。
10. Missing Information／Contradiction。
11. First Safe Next Action。

Result自身の最終Line Count／SHA-512を本文へ自己埋込みしない。作成後のConversation ReportとController Reviewへ記録する。

## 7. Formal Stop Conditions

```text
STOP-IDENTITY-OR-ACK-MISMATCH
STOP-CONTROL-PACKAGE-MISMATCH
STOP-MANIFEST-DIGEST-LINE-MISMATCH
STOP-MISSING-DIRECTORY-SYMLINK-OR-UNREADABLE
STOP-COVERAGE-TRUNCATION-OR-EVIDENCE-GAP
STOP-BATCH-OR-MULTI-TARGET-INVOCATION
STOP-TARGET-ALREADY-EXISTS
STOP-UNEXPECTED-MUTATION
STOP-SECOND-ARTIFACT-OR-SECOND-PATCH
STOP-PROVIDER-RESOURCE-CONTEXT-ERROR
STOP-SUPREME-RULE-AUTHORITY-HUMAN-GATE-CONFLICT
```

Stop時は、原因、完了済み範囲、Mutation StateおよびFirst Safe Next Actionだけを報告し、証跡を消すActionを行わない。

## 8. Prohibited Capabilities

```text
Authorized Root／Allowed Path外Access
Directory List／Search／Glob／Recursive Traversal／Symlink Follow
Multi-target／Loop／Batch Read
Manifest外Read／追加Source要求なしの推測補完
Existing File Mutation／Second Artifact／Temporary Artifact
Permission／ACL／Owner／Group／Executable Bit変更
Delete／Rename／Move／Cleanup／Rollback
Git／GitHub／External／Network／Secret／Credential／課金Action
Task／Sub-agent作成／別Task Messaging
Phase 2-A／Stage 3／次Work Unit開始
```

## 9. Result Report

```text
FINAL_STATE:
ACK_RESULT:
CONTROL_PACKAGE_VERIFICATION:
READ_CAPABILITY_RESULT:
READ_CARDINALITY_RESULT:
PROVIDER_MAPPING_RESULT:
READ_COVERAGE:
WRITE_RESULT:
CREATED_PATH:
CREATED_LINES:
CREATED_SHA512:
MUTATION_REPORT:
P2-0-WU-003_PRESERVATION:
CONTRADICTIONS／MISSING_INFORMATION:
FORMAL_STOP／DEVIATION:
FIRST_SAFE_NEXT_ACTION:
```

Parent Roleの独立ReviewとユーザーFinal Acceptanceを待ち、次Work Unitへ自動移行しない。

## 10. Non-elevation

本Handoff候補の存在はTask作成、Acceptance、READY、ARMED、Start、WriteまたはPhase 2-A Authorityを生成しない。新規Task作成にはExact Package全体に対するユーザーの別途明示Acceptanceを必要とする。

## 11. Related Documents

- [Exact Envelope exact-1](../governance/phase_2_0_documentation_capability_envelope_p2_0_wu_004_exact_1_20260811233209.md)
- [Exact Manifest exact-1](../governance/phase_2_0_documentation_capability_manifest_p2_0_wu_004_exact_1_20260811233209.md)
- [Documentation Capability Contract](../../../../shared/automation/documentation_capability_contract_ja.md)
- [Codex Desktop Documentation I/O Adapter](../../../../shared/automation/provider_adapters/codex_desktop_documentation_io_adapter_ja.md)
- [P2-0-WU-003 Controller Review](../operations/phase_2_0_bounded_write_controller_review_p2_0_wu_003_20260811225656.md)
- [Capability Contract Redesign Evidence](../operations/phase_2_0_capability_contract_redesign_after_p2_0_wu_003_20260811231332.md)
