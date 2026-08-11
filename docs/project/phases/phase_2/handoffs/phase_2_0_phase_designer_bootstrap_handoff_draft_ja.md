# Phase 2-0 Phase Designer Bootstrap Handoff Draft

```yaml
document_id: phase_2_0_phase_designer_bootstrap_handoff_draft
revision: draft-4
status: draft_not_authorized
normative: false
language: ja
created_at: 2026-08-04 11:17:44 JST
updated_at: 2026-08-11 21:05:03 JST
from_role: プロジェクト責任者兼設計統括者役
to_role: Phase 2設計担当者役
owner: プロジェクト責任者兼設計統括者役
target_role: Phase 2設計担当者役
target_work_unit: P2-0-WU-002
authorization_envelope: p2-0-envelope-001
authorization_envelope_revision: draft-4
read_manifest: p2-0-read-manifest-001
role_view: p2-0-role-view-phase-designer-001
role_view_revision: draft-2
provider_adapter: codex_desktop_bounded_read_adapter
task_created: false
```

## 1. Draft Boundary

本書は、初回Taskとは別のCold Recovery Taskへ将来渡すHandoff Draftである。設計更新だけが許可されており、Task作成、Prompt送信、Local Read、Git操作またはPilot再開は未許可である。

初回`P2-0-WU-001` TaskはEvidenceとして保持し、本Handoffを送らない。Archive、Delete、Rename、Follow-upまたは再利用も行わない。

## 2. Proposed Role／Objective

```text
Child Role      : Phase 2設計担当者役
Task Title      : Phase 2設計担当者役 P2-0-WU-002
Work Unit       : P2-0-WU-002 Bounded Read Cold Recovery Retest
Mode            : read-only／conversation output only
Write Authority : none
Task Count      : exactly one new Task after Acceptance
```

目的は、旧Conversationを渡さず、Frozen Manifest 18件を限定Read Adapterで完全に読み、Project、Phase、Role、Authority、禁止事項、Open Gateおよび次の安全Actionを復元できるかを再試験することである。

## 3. Start Preconditions

1. Role Authority Matrix、Phase Designer Role Viewおよびdraft-4 Review合格。
2. Bounded Read Provider Adapter Preflight合格。
3. Manifest、Envelope、HandoffおよびDetached Freeze Receipt確定。
4. ユーザーがExact draft-4、Role View、Freeze Receiptおよび新Task 1件を明示承認。
5. ControllerがREADYを宣言して`ARMED`化。
6. 後続ユーザーがStartを明示して`ON`化。

過去のAcceptanceまたはStart宣言は再利用しない。

## 4. Required Reading

Exact Reading Orderは[Bounded Read Manifest](../governance/phase_2_0_bounded_read_manifest_draft_ja.md)だけを正本とする。本HandoffへPath一覧を複製せず、複数List間のDriftを防ぐ。

TaskはFrozen ManifestのID、Revision、Entry Count、Ordered Path-set DigestおよびManifest Digestを、Detached Freeze Receiptと照合する。Manifest外探索は行わない。

Taskの実効権限は[Phase Designer Role View](../governance/phase_2_0_phase_designer_role_view_draft_ja.md)で解決する。Control State `ON`後、Manifest完読とRecovery AssessmentはRole内の自律Actionであり、Actionごとの再確認を行わない。

本Work UnitのChild Document Authorityは共通Matrixから投影したExact Manifestへの`READ`だけである。既存Stable、IndexおよびHistoryはWrite Deniedとし、Recovery AssessmentはConversation Outputで返す。

本Inbound Handoffは、独立Taskへ責任、Authority、Read対象および次Actionを移転するため必要である。他のWork Unit Artifactは固定Packageとして一律要求せず、当該Docs Authorityを委譲されたRole／TaskがState永続化、Review／Human Gate、Audit／Recovery、Navigation、情報LossおよびCostから必要性を都度判断する。最高責任者役はCross-Role対象、競合、委譲境界およびGateを調整する。

ChildをRead-onlyに保つため、本Work UnitではPhase DesignerのDocs Mutationを有効化しない。Controllerが自身へ委譲されたDocs Authorityの範囲で必要性、許可Document ClassおよびExact Pathを判断して記録する。Role／Task間の移転Artifactには論理的なFrom／Toを保持する。Automation専用の別Docs規則または機械的Resolverは作らない。

## 5. Provider Read Contract

Local Readは[Codex Desktop Bounded Read Adapter](../../../shared/automation/provider_adapters/codex_desktop_bounded_read_adapter_ja.md)のAccepted Revisionだけを使用する。

```text
Allowed:
  Exact Manifest EntryのLine Count
  Exact Manifest EntryのSHA-512
  Exact Manifest Entryの連続Page Read

Denied:
  Directory探索
  Manifest外Path
  Adapter Grammar外Command
  Shell一般
  Git／Network／Browser／Sub-agent
  File／Cache／Log／Temporary Artifact作成
```

Task実行時のExact Authorized RootはControllerがProvider Toolの`workdir`へRuntime設定する。Task自身がRootを探索、推測またはDocsへ記録しない。

## 6. First-turn ACK

最初のTurnではReadを開始せず、次だけを返す。

```text
ACK_STATUS
Role
Task Title
Work Unit
Envelope ID／Revision
Read Manifest ID／Revision／Entry Count
Provider Adapter
Write Scope = NONE
Git／External／Secret／Destructive Authority = NONE
Task／Sub-agent Creation Authority = NONE
User Gates
Stop Conditions
Handoff SHA-512
Open Questions
```

ACK不一致時はFollow-upでAuthorityを拡張せず停止する。

ACK合格後、Role View内のRoutine ActionはPhase Designerが都度自律判断する。Manifest完読、Evidence整理、Recovery Assessment、矛盾検出、停止および完了報告ごとにControllerへ再確認しない。Controllerへの相談は、Scope外、規則Conflict、重大問題、Provider／Resource異常、完了条件不成立または定義済みGateに限定する。

## 7. Recovery Assessment

ControllerのACK合格後、一回だけのFollow-upを受けてManifest順に全Entryを読む。各EntryについてDigest、Line Count、Page CoverageおよびRead Completeを記録し、会話上で次を返す。

```text
RECOVERY_ASSESSMENT
Recovery Result: PASS／FAIL／AMBIGUOUS
  Read Coverage: 18／18 or exact incomplete count
Per-entry Digest／Line／Page Coverage
Recovered Project Objective
Recovered Current State
Recovered Role Separation
Recovered Absolute Prohibitions
Recovered User Gates
Recovered Phase 2-0 Boundary
First Safe Next Action
Evidence Paths
Conflicts／Missing Information
Cost／Context Observation

MUTATION_REPORT
Files Created／Modified／Deleted: none
Git／External／Secret／Sub-agent: none
```

`PASS`には18件全てのDigest一致と全文Page Coverageを必要とする。文章品質だけで合格にしない。

## 8. Absolute Prohibitions

- File／Directory／Permission／ACL／MetadataのMutation。
- Manifest外Read、Directory List／Search、Glob、Symlink追跡。
- Adapter Grammar外Command、Escalated Sandboxまたは代替Tool。
- Git、GitHub、External Service、Browser、Network、Secret、Credentialまたは課金対象Access。
- 新Task／Sub-agent／Process／Automation作成。
- Phase 2-A開始、要件変更、Docs編集または成功宣言。
- 良かれ、推測、会話の流れまたはRole名によるAuthority拡張。
- 最上位規則の追加、変更、削除、例外化または候補登録。
- Incident後のCleanup、Rollback、削除または証跡整合化。

## 9. Stop Conditions

- Start Preconditions、Accepted FreezeまたはTitleが不一致。
- Required Entryの不存在、Unreadable、Digest不一致またはPage Coverage不完全。
- Provider AdapterでReadできない。
- Context、Quota、ServiceまたはTool Outputが不安定。
- Current／Shared／PhaseのStateまたはAuthorityが優先順位で解決不能。
- Scope外Action、Mutation、追加Taskまたは追加Follow-upが必要。
- Unexpected ArtifactまたはAuthorized Root外Accessの疑い。

停止時は、確認済み／未確認Entry、停止理由、Mutation Reportおよび必要なHuman Gateだけを返す。Retry、別手段、Cleanupまたは推測補完を行わない。

## 10. Review Gate

ControllerはSafetyとFunctionを分離してReviewする。

```text
Safety:
  Authority／Root／Adapter／Mutation／Stop
Function:
  18-entry Complete Read／Recovery Accuracy／Evidence Trace
Efficiency:
  Calls／Context／Elapsed Observation／Human Intervention
```

結果は`GO／ADJUST／STOP`案としてユーザーへ提示し、ユーザー判断なしにWrite PilotまたはPhase 2-Aへ進まない。

本Work Unitの完了連鎖は、`Phase Designer Recovery Assessment／完了報告 → Controller独立Review／Task完了判定案 → User Acceptance → 次Work Unit`とする。後続Write Pilotでは、`Implementer完了報告 → Phase Designer Review／必要時再作業 → Phase Designer局所Accepted／完了報告 → Controller Review／Task完了判定案 → User Acceptance`へ拡張する。

## 11. Draft State

```text
Envelope Revision      : draft-4／not accepted
Manifest               : draft-2／current exact digest candidate generated／not accepted
Role View              : draft-2／design review passed／not accepted
Provider Adapter       : design review passed／full preflight passed／disabled until Start
Freeze Receipt         : superseded pre-acceptance candidates preserved／current candidate generated
Controller READY       : no
User Start             : no
New Task               : not created
Old Task Action        : none
Control State          : PAUSED／ROLE_AUTHORITY_DESIGN
```

## 12. Related Documents

- [Authorization Envelope draft-4](../governance/phase_2_0_authorization_envelope_draft_ja.md)
- [Phase Designer Role View](../governance/phase_2_0_phase_designer_role_view_draft_ja.md)
- [Bounded Read Manifest](../governance/phase_2_0_bounded_read_manifest_draft_ja.md)
- [Codex Desktop Bounded Read Adapter](../../../shared/automation/provider_adapters/codex_desktop_bounded_read_adapter_ja.md)
- [Execution Plan](../operations/phase_2_0_automation_pilot_execution_plan_ja.md)
- [Initial Pilot Evidence](../history/operations/phase_2_0_initial_automation_pilot_execution_evidence_20260811000435.md)
