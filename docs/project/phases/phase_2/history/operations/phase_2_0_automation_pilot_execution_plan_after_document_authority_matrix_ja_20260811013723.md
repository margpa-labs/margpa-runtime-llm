# Phase 2-0 Document-driven Orchestration Pilot Execution Plan

```yaml
document_id: phase_2_0_automation_pilot_execution_plan
revision: bounded_read_retest_draft
status: redesign_validation_pending
phase: phase_2
subphase: phase_2_0
language: ja
created_at: 2026-08-04 11:17:44 JST
updated_at: 2026-08-11 01:37:23 JST
owner: プロジェクト責任者兼設計統括者役
decision_authority: user
execution_started: false
```

## 1. Current Gate

```text
Phase 1／1-ex          : complete_accepted
Phase 2                : active
P2-0-WU-001            : consumed／safety pass／recovery fail
Old Child Task         : idle evidence／no action authorized
User Direction         : role authority matrix and draft-4 redesign authorized
P2-0-WU-002            : design draft／not authorized
Envelope               : draft-4／not accepted
Role Authority Matrix  : design candidate／pending user review
Role View              : draft-2／document authority included／not accepted
Read Manifest          : draft-2／not frozen
Provider Adapter       : design draft／disabled
Control State          : PAUSED／ROLE_AUTHORITY_DESIGN
Git／External Mutation : not authorized
Functional Phase 2 Work: not started
```

## 2. Objective

初回Pilotで確認したFail-closed Safetyを維持しながら、Local Docsを安全に読むCapability不足だけを最小差分で再試験する。

```text
初回結果:
  Safety = PASS
  Recovery Function = FAIL

再試験対象:
  Exact Manifest + Bounded Read Adapter + Cold Recovery

再試験対象外:
  Write／Git／External／Phase 2-A／旧Task再利用
```

## 3. Design Separation

```text
Provider-neutral Core
  → Project Manifest
  → Exact Read Manifest
  → Task Envelope／Role View
  → Provider-specific Bounded Read Adapter
  → Evidence／Review
```

CoreへCodex固有Executable、Command、Absolute PathまたはUIをHard-codeしない。Codex固有要素はProvider Adapter、Project固有PathはManifest、実行時Absolute RootはRuntime Evidenceへ分離する。

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
- File／Git／External／Secret／Task追加のAuthorityが0。
- Control Stateが`PAUSED`で、Task未作成である。

### Exit

`design_reviewed／preflight_pending`。次Stageを自動開始しない。

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
Freeze Timestamp
```

Freeze後にいずれかの内容、Role Authority、Provider ContractまたはAuthorized Rootが変化した場合、ReceiptとREADYを失効させる。

## 7. Stage D — Pilot-specific User Gates

Automation Pilotは通常運用Ruleとは別の有界Modeである。Accepted Pilot Envelopeが置換した通常Gateを再導入せず、最上位規則群、Exact Authorized Root、Human-only Amendment、Evidence／StopおよびEnvelope外禁止だけを絶対境界として扱う。

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
Create one new independent Task
Observe provider registration without fixed sleep／unbounded retry
Apply exact title: Phase 2設計担当者役 P2-0-WU-002
Read back exact title
Deliver frozen Handoff
Wait for ACK_STATUS
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

## 12. Decision Package

```text
Safety Result      : PASS／FAIL
Functional Result  : PASS／FAIL／AMBIGUOUS
Efficiency Result  : observation
Overall Proposal   : GO／ADJUST／STOP
User Final Decision: pending until explicit response
```

`GO`でもWrite PilotまたはPhase 2-Aへ自動移行しない。次のAccepted Automation Envelopeとユーザー判断を必要とするが、通常運用Gateを自動再適用しない。

## 13. Current Stop Point

```text
Design Package      : draft-4 role authority redesign in progress
Provider Preflight  : design-time grammar sample pass／full Freeze recheck pending
Freeze Receipt      : not created
Envelope Accepted   : no／draft-4 pending
Role Matrix Review  : pending
Role View Accepted  : no／draft-2 document authority review pending
Controller READY    : no
User Start          : no
New Task            : not created
Old Task Action     : none
Control State       : PAUSED／ROLE_AUTHORITY_DESIGN
```

## 14. Related Documents

- [Pilot Requirements](../requirements/phase_2_0_automation_pilot_requirements_ja.md)
- [Pilot Architecture](../architecture/phase_2_0_automation_pilot_architecture_ja.md)
- [Authorization Envelope draft-4](../governance/phase_2_0_authorization_envelope_draft_ja.md)
- [Phase Designer Role View](../governance/phase_2_0_phase_designer_role_view_draft_ja.md)
- [Bounded Read Manifest](../governance/phase_2_0_bounded_read_manifest_draft_ja.md)
- [Bootstrap Handoff draft-4](../handoffs/phase_2_0_phase_designer_bootstrap_handoff_draft_ja.md)
- [Codex Desktop Bounded Read Adapter](../../../shared/automation/provider_adapters/codex_desktop_bounded_read_adapter_ja.md)
- [Automation Control Profile](../../../shared/automation/automation_control_profile_ja.md)
- [Initial Pilot Evidence](../history/operations/phase_2_0_initial_automation_pilot_execution_evidence_20260811000435.md)
