# Phase 2-0 Documentation Capability Envelope — P2-0-WU-004 exact-1

```yaml
document_id: phase_2_0_documentation_capability_envelope_p2_0_wu_004_exact_1_20260811233209
envelope_id: p2-0-envelope-003
revision: exact-1
status: exact_candidate_user_acceptance_pending
phase: phase_2
subphase: phase_2_0
work_unit: P2-0-WU-004
created_at: 2026-08-11 23:32:09 JST
language: ja
owner_role: プロジェクト責任者兼設計統括者役
target_role: Phase 2設計担当者役
automation_level: bounded_unit
control_state: PAUSED_PACKAGE_REVIEW
```

## 1. Purpose／Completion Line

P2-0-WU-004は、Provider-neutral Documentation Capability ContractとCodex Desktop semantic mappingを用いて、一つの小規模Source SetをExact Single-targetで読み、一件の新規Documentation Artifactを作成・検証・報告する有界再試験である。

```text
Start  : exact package acceptance + READY／ARMED + later user Start
End    : one Result returned／Child stopped／Controller review pending
Limit  : one Child Task／one Work Unit／one exact create
```

本EnvelopeはPhase 2-A、Stage 3、次Work Unit、Git、ExternalまたはPermission Authorityを含まない。

## 2. Exact Identity

```text
Envelope ID／Revision : p2-0-envelope-003／exact-1
Manifest ID／Revision : p2-0-documentation-capability-manifest-001／exact-1
Manifest Path         : docs/project/phases/phase_2/history/governance/phase_2_0_documentation_capability_manifest_p2_0_wu_004_exact_1_20260811233209.md
Manifest Lines        : 114
Manifest SHA-512      : 13352b02fb4a71156535cd9f3691587d3d7a05df6a4c0eeff0bc831c3621ffa2235ed607140fd2393970a627a566d2f69a5606dd603dc81fe82150fea8b0a706
Entry Count           : 6
Entry Lines           : 1,324
Ordered Package SHA-512: 033b7d11d771beb477099984ebd4a023a9db9c8e12678e4b3f369adcf417d6a5dd3734727d266b6ae207cd23bb7053edb57fbc33f0b9e4a2db0a6a2e10496826
```

## 3. Effective Authority

```text
Human-defined Supreme Rules
  ∩ Accepted p2-0-envelope-003/exact-1
  ∩ Common Role／Docs Authority
  ∩ Documentation Capability Contract capability-semantics-1
  ∩ Codex Desktop Documentation I/O Adapter semantic-mapping-1
  ∩ Exact Manifest／Result Path
  ∩ Provider Available Capability
```

一つでも不一致、UnknownまたはUnavailableなら、最も制限の強い結果へ解決して停止する。

## 4. Child Execution Authority

### 4.1 Allowed

- Initial No-tool ACK。
- Accepted Start後のControl Package Exact Verification。
- Manifest 6 Entryへの`bounded_documentation_read／exact_single_target_read`。
- EntryごとのLine Count、SHA-512、Complete CoverageおよびInvocation Evidence。
- Exact Result Pathへの`bounded_documentation_create`一回。
- Exact ResultのReadback、Line Count／SHA-512およびConversation Report。
- Scope内判断とMissing Information報告。

### 4.2 Document Authority

```text
Control Package／Manifest Entry : READ
Exact Result Path               : CREATE_NEW／exactly one
Existing Stable／History        : DENY
Additional Artifact             : DENY
Index／Status／Review／Evidence  : Child DENY／Parent-owned after result
```

### 4.3 Provider Mapping

```text
Mapping Policy         : semantic_mapping
Mechanical Enforcement: unavailable／not claimed
Read Cardinality       : one exact target per invocation
Batch Capability       : unavailable／deny
Raw Command Allowlist  : none in Normative Contract
```

Childは実際に使用したInvocation Classを報告する。ProviderがRaw Command Traceを返さない場合は`unverified`とし、推測で補完しない。

## 5. Exact Mutation Boundary

```text
Exact Result Path:
docs/project/phases/phase_2/history/operations/phase_2_0_documentation_capability_conformance_result_p2_0_wu_004_20260811233209.md

Create Count            : 1
Existing File Mutation  : 0
Additional File Create  : 0
Delete／Rename／Move     : 0
Permission／ACL         : 0
Git／GitHub             : 0
External／Network       : 0
Secret／Credential      : 0
Task／Sub-agent         : 0
```

Exact Result Pathが既に存在する場合は作成せず停止する。別名、Suffix変更または上書きで迂回しない。

## 6. Explicit Prohibitions

- Authorized Root／Allowed Path外Access。
- Control Package、Manifest 6 EntryおよびExact Result以外のRead。
- Directory List、Search、Glob、Recursive TraversalまたはSymlink追跡。
- 一Invocationでの複数Target処理、LoopまたはBatch。
- Existing File Mutation、二件目のArtifactまたは二回目のPatch。
- Git、GitHub、External、Network、Secret、Credentialまたは課金Action。
- Permission、ACL、Owner、Group、Executable Bit、Delete、Move、RenameまたはCleanup。
- Task／Sub-agent作成、別Task MessagingまたはScope外Follow-up。
- P2-0-WU-003 Artifactの修正、削除、再分類または遡及Acceptance。
- Phase 2-A、Stage 3、次Work UnitまたはAutomation Level拡張。

## 7. Evidence Dimensions

Child ReportとController Reviewは次を独立判定する。

```text
Authority
Scope
Capability Semantics
Provider Mapping
Result
Evidence
Stop／Recovery
```

成果物成功はProvider Mapping不一致を治癒せず、Provider Mapping不一致だけで未確認のAuthority逸脱を推測しない。

## 8. Formal Stop Conditions

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

Stop後はCleanup、Rollback、代替Command／Tool、Scope拡張、Task再作成または自動Retryを行わない。

## 9. Human Gates／Activation

本Package作成時点では`PAUSED_PACKAGE_REVIEW`である。次を順序どおり必要とする。

1. ControllerによるPackage整合Review。
2. ユーザーによるExact Envelope／Manifest／Handoff／Receiptと新Task 1件のAcceptance。
3. ControllerのREADY宣言と`ARMED`。
4. 後続ユーザーStart宣言と`ON`。
5. Child No-tool ACK合格。
6. Child Result後のController独立Review。
7. ユーザーFinal Acceptance。

過去のP2-0-WU-002／003 Acceptance、READYまたはStartを継承しない。

## 10. Expiration／Revocation

次の最初の時点で失効する。

- Envelope、Manifest、Handoff、Receipt、Capability ContractまたはAdapter Revision変化。
- Manifest EntryまたはExact Result PathのState／Digest変化。
- Authorized Root、Role、Task Title、Provider CapabilityまたはUser Direction変化。
- User revocation。
- Work Unit Result返却、Formal StopまたはController Review開始。

## 11. Non-elevation

本Envelope候補の存在はAcceptance、Task作成、READY、StartまたはWrite Authorityを単独生成しない。ユーザーの明示Acceptance前にChild Taskを作成しない。
