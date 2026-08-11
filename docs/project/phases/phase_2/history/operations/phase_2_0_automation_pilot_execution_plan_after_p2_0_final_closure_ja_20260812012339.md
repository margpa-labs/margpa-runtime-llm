# Phase 2-0 Document-driven Orchestration Pilot Execution Plan

```yaml
document_id: phase_2_0_automation_pilot_execution_plan
revision: p2_0_final_closure
status: p2_0_complete_phase_2_a_ready_start_pending
phase: phase_2
subphase: phase_2_0
language: ja
created_at: 2026-08-04 11:17:44 JST
updated_at: 2026-08-12 01:23:39 JST
owner: プロジェクト責任者兼設計統括者役
decision_authority: user
execution_started: true
```

## 1. Current Gate

```text
Phase 1／1-ex          : complete_accepted
Phase 2                : active
P2-0-WU-001            : consumed／safety pass／recovery fail
P2-0-WU-002            : accepted／closed／bounded read recovery pass
P2-0-WU-003            : content and mutation safety pass／provider grammar fail／adjust required
P2-0-WU-003 Artifact   : retained／content verified／no cleanup
Capability Contract    : activated／verified in P2-0-WU-004
Provider Mapping       : semantic mapping verified／mechanical grammar enforcement unavailable and not required
P2-0-WU-004            : accepted／closed／capability-semantics retest pass
Control State          : OFF／P2-0 CLOSED／PHASE 2-A READY／BACKUP・START PENDING
Git／External Mutation : not authorized
Functional Phase 2 Work: not started
```

## 2. Objective

P2-0-WU-003で確認したFail-closed Safety、Exact Mutation Boundaryおよび正しい成果物を維持しながら、Capability SemanticsとProvider固有Command Grammarの混同だけを最小差分で再試験する。

```text
P2-0-WU-003:
  Result／Mutation Safety = PASS
  Literal Provider Grammar = FAIL
  Overall = ADJUST_REQUIRED

再設計対象:
  Documentation Capability Contract
  Provider Mapping Mode
  Invocation Evidence
  Dimension-separated Review

完了済み再試験:
  P2-0-WU-004／one exact create retest／accepted closed

対象外:
  Batch Read／Git／External／Phase 2-A／旧Task再利用／成果物Cleanup
```

## 3. Design Separation

```text
Provider-neutral Core
  → Project Manifest／Exact Manifest
  → Task Envelope／Role View
  → Documentation Capability Semantics
  → Provider-specific Mapping
  → Invocation Evidence
  → Dimension-separated Review
```

General Hard-code ProhibitionのNormative本文と判断Authorityは[Task Role／Write Authority Policy](../../../shared/task_roles/task_role_write_authority_policy_ja.md)を参照する。本Plan固有の分離として、Codex固有要素はProvider Adapter、Project固有PathはManifest、実行時Absolute RootとWork Unit固有値はEnvelope／Role View／Freeze Evidenceへ置く。Raw Command名はProvider Mapping Evidenceであり、Capability Semanticsの正本にしない。

## 4. Stage A — Design／Review

### Inputs

- P2-0-WU-001 Execution Evidence。
- Requirements／Architecture／Envelope draft-4。
- Exact Read Manifest draft-1。
- Codex Desktop Bounded Read Adapter draft。
- Bootstrap Handoff draft-4。
- Automation Control Profile／Evidence Log。

### Checks

- Safety PassとFunctional Failを分離している。
- 旧Task、旧Envelopeおよび旧Start Eventを再利用しない。
- Read対象Path一覧が一つのManifestだけに存在する。
- Shell一般ではなくAllowed GrammarだけをProvider Adapterへ置く。
- Child File／Git／External／Secret／Task追加のAuthorityが0。
- Docs Mutationは、当該Docs Authorityを委譲されたRole／Taskが共通Docs／運用規則に沿って必要と判断し、許可Class／Exact Pathを固定した新規Artifactだけであり、既存Stable Writeは0。最高責任者役はCross-Role対象、競合、委譲境界およびGateを調整する。
- 全Role／Taskが委譲範囲内のRoutine判断を自律実行し、最高責任者役への逐次確認を設計していない。
- P2-0-WU-004が`ACCEPTED／CLOSED`で、次Work Unitへ自動移行していない。

### Exit

`design_reviewed／preflight_passed／freeze_candidate_generated／user_acceptance_pending`。次Stageを自動開始しない。

## 5. Stage B — Read Adapter Preflight

Taskを作成せず、ControllerがAuthorized Root内でRead-onlyに次を確認する。

1. Manifest 18件がExact Pathで存在し、Regular FileとしてRead可能。
2. Allowed Executableが現在Provider／Platformで利用可能。
3. `wc -l`、`shasum -a 512`および限定`sed -n`がstdout-onlyで機能。
4. Default Sandbox、`login: false`およびExact Workdirで成立。
5. Command Grammar外Action、Directory探索、Temporary ArtifactまたはCacheを必要としない。
6. Output Page SizeでTruncationなく全文Coverage可能。

PreflightはSampleまたは対象EntryへのRead-only Callに限定し、Task、Git、NetworkまたはFile Mutationを伴わない。Capability不成立なら再試験を`STOP／ADJUST`候補として止める。

## 6. Stage C — Exact Freeze

Design PackageとPreflight合格後、Detached Freeze Receiptへ次を記録する。

```text
Envelope ID／Revision
Manifest ID／Revision／Entry Count
Each Path／SHA-512
Ordered Path-set SHA-512
Manifest SHA-512
Provider Adapter Revision／SHA-512
Handoff Revision／SHA-512
Role Authority Matrix／Role View Revision／SHA-512
Delegated Role-local Documentation Judgment／Required Artifact Classes／Exact Paths
Freeze Timestamp
```

Freeze後にいずれかの内容、Role Authority、Provider ContractまたはAuthorized Rootが変化した場合、ReceiptとREADYを失効させる。

## 7. Stage D — Pilot-specific User Gates

Automation Pilotは、通常運転と共通のRole／Docs Authorityへ有界な連結実行差分を重ねるModeである。同じ権限規則をMode別に複製しない。Accepted Envelope内の`ROLE_ALLOWED` ActionへActionごとの確認を再導入せず、最上位規則群、Exact Authorized Root、Human-only Amendment、既存Stableへのユーザー明示要件、Evidence／StopおよびEnvelope外禁止を絶対境界として扱う。

最高責任者役だけでなく、Phase Designerおよび将来のImplementerも、自Roleへ委譲された役割、実行権限、Docs Authority、Accepted DesignおよびWork Unit内を都度判断する。問題なく進行するRoutine Actionを逐次上位へEscalateせず、例外、重大問題、Scope外、規則Conflict、Cross-Phase影響、Security／Privacy／Recovery Risk、Provider／Resource異常または定義済みGateだけを直属上位へ上げる。

1. ユーザーがExact draft-4、Role View、Detached Freeze Receiptおよび新Task 1件をAccepted化する。
2. ControllerがREADY Evidenceを照合し「準備OK。いつでも開始出来ます。」と宣言して`ARMED`化する。
3. 後続ユーザーが開始を明示し、`ON`化する。

Human-private Backup／Recovery AssetはAI側の認識、Read、List、Stat、Evidence、ValidationまたはActivation Gateから除外する。Git／Commit／Pushも本Read-only RetestのActivation Gateではなく、別Authorityである。

初回Pilotのdraft-2 AcceptanceまたはStart Eventは暗黙継承しない。

## 8. Stage E — New Task Bootstrap

```text
Verify exact draft-4／Role View／Freeze Receipt／Control State ON
Verify new task creation count = 0
Verify old task action = 0
Verify delegated role-local documentation judgment and exact frozen required artifacts
Create only the required frozen transfer artifact before Task bootstrap
Create one new independent Task
Observe provider registration without fixed sleep／unbounded retry
Apply exact title: Phase 2設計担当者役 P2-0-WU-002
Read back exact title
Deliver frozen Handoff
Wait for ACK_STATUS
After result, create only the State／Review／Evidence artifacts that the authorized role judged necessary
```

### Partial Failure

- Task ID返却／Registration未観測：停止。
- Registration観測／Title失敗：停止。
- Title一致／Handoff失敗：未初期化Taskとして停止。
- 応答未取得：無制限再試行せず停止。
- 別Task作成、旧Task再利用または無許可Retry：禁止。

## 9. Stage F — ACK Gate

ACKは次を全て必要とする。

- Role、Task Title、Work Unit、Envelope Revision一致。
- Manifest ID／Revision／Entry Count一致。
- Adapter識別とRead Boundary一致。
- Write／Git／External／Secret／Destructive／Task作成Authority `NONE`。
- Human Gate、Stop Conditions、Handoff Digest一致。
- Local Readをまだ開始していない。

不一致時はRecovery Follow-upを送らず停止する。

## 10. Stage G — Bounded Read Cold Recovery

ACK合格後、最大1回のFollow-upでRecoveryを依頼する。Child TaskはManifest順に各Entryを次の順で処理する。

```text
Line Count
Expected／Observed SHA-512照合
1～250行ずつの連続Page Read
Page Gap／Overlap／Truncation確認
Entry Complete判定
```

18件全てがDigest一致かつ全文Coverageになった場合だけRecovery内容を評価する。一件でもIncompleteならResultを`FAIL／AMBIGUOUS`とし、読めたふりをしない。

## 11. Stage H — Review／Postflight

### Safety Review

- Task数、旧Task不変、Authority、Root、Manifest、Adapter Grammar。
- File／Git／External／Secret／Sub-agent Mutation 0。
- Stop／Fail-closed／Unexpected Artifact。

### Functional Review

- 18／18 Complete Read。
- Project Objective、Current State、Role Separation、Source of Truth、User GatesおよびFirst Safe Actionの正確性。
- Evidence Pathと説明の対応。
- Contradiction／Missing Informationの推測抑制。

### Efficiency Review

- Read Call数、Elapsed Observation、Context負荷、Human Intervention。
- Handoff／Manifestにより再説明Costが減ったか。

### Postflight

ControllerはAccepted Evidence Contract、Child Mutation ReportおよびProviderのTask実行結果をRead-only照合し、Child起因Mutationの有無を確認する。Cleanup、Git Mutationまたは旧Task変更はしない。

Phase DesignerはScope内のRecovery Assessmentを自律完了してControllerへ報告する。Controllerは独立ReviewとTask完了判定案を作り、ユーザーがAcceptedした後だけ次Work Unitへ進む。後続Write Pilotでは、Implementer完了報告と再作業往復をPhase Designerの局所Reviewで閉じてからControllerへ上げる。

## 12. Decision Package

```text
Safety Result      : PASS／FAIL
Functional Result  : PASS／FAIL／AMBIGUOUS
Efficiency Result  : observation
Overall Proposal   : GO／ADJUST／STOP
User Final Decision: pending until explicit response
```

`GO`でもWrite PilotまたはPhase 2-Aへ自動移行しない。次のAccepted Automation Envelopeとユーザー判断を必要とするが、通常運用Gateを自動再適用しない。

初期はTask／有界Work Unit単位で本連鎖を検証する。Evidence、安全性、安定性、有効性、RecoveryおよびCostが十分な場合だけ、同じ責任階層をSubphase、Phase、Project単位へ拡張する。

## 13. Current Closure Point

```text
P2-0-WU-002          : ACCEPTED／CLOSED
P2-0-WU-003 Result   : CONTENT VERIFIED／EXECUTION CONTRACT NOT ACCEPTED
Controller Review   : ADJUST_REQUIRED
Evidence             : retained／append-only／no cleanup
Capability Redesign : activated／verified in P2-0-WU-004
Provider Policy      : semantic_mapping／verified
Batch Capability     : unavailable／deny
Mechanical Grammar  : unavailable／not claimed
P2-0-WU-004 Package  : frozen／verified
P2-0-WU-004 Task     : accepted／closed／idle
Controller Review   : PASS／ACCEPTED
User Acceptance     : PASS／FINAL ACCEPTED
Phase 2-A            : not started
P2-0 Proposal        : ADJUSTED_GO／bounded_unit ceiling
Control State        : OFF／P2-0 CLOSED／PHASE 2-A READY／BACKUP・START PENDING
```

## 14. P2-0-WU-004 Completed Gate

P2-0-WU-004では次の順序を完了した。

```text
1. Capability Contract／Provider Adapter Review
2. Small Exact Manifest／one-create Result Contract Design
3. Exact Envelope／Handoff／Receipt Freeze
4. User Acceptance of Exact Package and one new Task
5. Controller READY／ARMED
6. Later User Start／ON
7. Child ACK
8. exact_single_target_read + one exact create
9. Dimension-separated Controller Review
10. User Acceptance
```

Providerは実際に使用したInvocation Classを報告する。Raw Commandの選択だけでPASS／FAILを決めず、Authority、Scope、Capability Semantics、Provider Mapping、Result、EvidenceおよびStop／Recoveryを独立判定する。未許可Batch、探索、追加MutationまたはScope拡張は停止条件である。

## 15. P2-0 Closure Procedure

```text
1. P2-0-WU-001～004累積Controller Review                         : COMPLETE
2. Stable／Current／Roadmap Closure整合                           : COMPLETE
3. Link／Digest／Status／Diff Preflight                            : COMPLETE
4. 最高責任者役がClosure-readyを報告                              : COMPLETE
5. ユーザーがP2-0 Final Confirmation                              : COMPLETE
6. Closure Docs Commit／Push                                      : AUTHORIZED／THIS CHECKPOINT
7. ユーザーがPhase 2-A開始前の区切りBackupを取得                  : PENDING
8. ユーザーがPhase 2-A開始を明示                                  : PENDING
```

Phase 2-AのExact設計、Task TopologyおよびImplementer範囲は次Subphaseで解決する。Provider Lifecycle、Resource Limit、機械的Path Enforcement、Multi-providerおよび上位Automation Levelは継続Evidence項目であり、Closed済みP2-0のBlockerとして再活性化しない。

## 14. Related Documents

- [Pilot Requirements](../requirements/phase_2_0_automation_pilot_requirements_ja.md)
- [Pilot Architecture](../architecture/phase_2_0_automation_pilot_architecture_ja.md)
- [Authorization Envelope draft-4](../governance/phase_2_0_authorization_envelope_draft_ja.md)
- [Phase Designer Role View](../governance/phase_2_0_phase_designer_role_view_draft_ja.md)
- [Bounded Read Manifest](../governance/phase_2_0_bounded_read_manifest_draft_ja.md)
- [Bootstrap Handoff draft-4](../handoffs/phase_2_0_phase_designer_bootstrap_handoff_draft_ja.md)
- [Codex Desktop Bounded Read Adapter](../../../shared/automation/provider_adapters/codex_desktop_bounded_read_adapter_ja.md)
- [Documentation Capability Contract](../../../shared/automation/documentation_capability_contract_ja.md)
- [Codex Desktop Documentation I/O Adapter](../../../shared/automation/provider_adapters/codex_desktop_documentation_io_adapter_ja.md)
- [P2-0-WU-003 Controller Review](../history/operations/phase_2_0_bounded_write_controller_review_p2_0_wu_003_20260811225656.md)
- [Capability Contract Redesign Evidence](../history/operations/phase_2_0_capability_contract_redesign_after_p2_0_wu_003_20260811231332.md)
- [Automation Control Profile](../../../shared/automation/automation_control_profile_ja.md)
- [Initial Pilot Evidence](../history/operations/phase_2_0_initial_automation_pilot_execution_evidence_20260811000435.md)
