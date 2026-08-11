# Phase 2-0 Draft-3再設計からDocument Authority明示までの新規知見

```yaml
event_id: phase_2_0_draft3_to_document_authority_findings
event_time: 2026-08-11 01:37:23 JST
phase: phase_2
subphase: phase_2_0
status: design_evidence_recorded
control_state: PAUSED_ROLE_AUTHORITY_DESIGN
pilot_restarted: false
new_task_created: false
git_or_external_action: false
history_policy: append_only
```

## 1. Record Scope

本Recordは、Authorization Envelope draft-3と関連Docsの再設計開始から、Role Authority MatrixおよびDocument Authorityの明示に至るまでに新たに得られた知見だけを固定する。

初回PilotのTask作成、Title再設定、Authority ACK、Read 0件でのFail-closedおよびMutation 0の事実は既存Evidenceの正本とし、本Recordで重複再述しない。

## 2. Sequence

1. ユーザーは、draft-3と関連Docsの再設計を許可した。この許可は設計更新だけを対象とし、新Task作成またはPilot再開は含まなかった。
2. Local Docsの有界Readを成立させるため、Provider-neutral Core、Exact Read ManifestおよびProvider-specific Adapterを分離した。
3. その後のAuthority補正で、ControllerはAutomation Pilotへ通常運用のGit／Backup／Action単位Gateを再適用し、Human-private Recovery Assetの認識をActivationの前提に入れた。
4. ユーザーは、Automation Modeが通常運用とは別の事前授権Modeであり、最上位規則だけはAI Sideの全Roleに絶対適用されることを再確定した。
5. 再点検により、RoleごとのWrite ScopeとAutomation Levelは存在していたが、Role上限、Accepted Envelope、Work UnitおよびProvider Capabilityを結合する実効権限表がなかったことを特定した。
6. Role Authority MatrixとPhase Designer Role Viewを追加し、draft-4のAuthority Resolutionを修正した。
7. さらに、実行Actionの許可だけではDocsの取扱いが一意にならないことを確認した。Role ViewにRead-only、Stable Write、Append-only Add、Review-only、Human GateおよびDenyを独立して保持する設計へ更新した。

## 3. Root Cause

直接原因は、安全規則が強すぎたことではない。最上位規則、通常運用Default、Role上限、Pilot固有EnvelopeおよびProvider Capabilityを一つの明示的Resolverで結合していなかったことである。

```text
Supreme Ruleへの忠実さ
  ≠ 通常運用DefaultをAutomationへ常に再適用すること

RoleにWrite Scopeがある
  ≠ そのWork UnitでWriteが有効であること

Fileを読める
  ≠ StableまたはHistoryを変更できること
```

## 4. Corrected Authority Model

```text
Effective Authority
  = Human-defined Supreme Rulesに適合
  ∩ Accepted Automation Envelope
  ∩ Role Authority Matrix
  ∩ Assigned Work Unit Role View
  ∩ Available Provider Capability
```

- 最上位規則は全AI Roleに絶対であり、追加、変更、削除、例外化および候補登録の指示AuthorityはHuman-onlyである。
- Automation `ON`では、Accepted EnvelopeとRole Authorityの交差内にある`AUTO`をActionごとの再確認なしで実行する。
- Envelope外、Role外、Authorized Root／Allowed Path外、`HUMAN_GATE`または`DENY`は自動化でも拡張しない。
- Human-private Backup／Recovery AssetはAI Control PlaneのInput、Read Target、Evidence、ValidationまたはActivation Gateに含めない。
- Provider Capabilityの存在は、Adapter Activation、Path AuthorizationまたはAction Authorizationを意味しない。

## 5. Document Authority Finding

Role Viewは、実行Actionの列挙だけでは不十分である。少なくとも次のDocs Authorityを文書ClassまたはExact Pathごとに保持する必要がある。

```text
READ_AUTO
WRITE_STABLE_AUTO
APPEND_AUTO
REVIEW_ONLY
HUMAN_GATE
DENY
```

Stable Writeは、更新前Snapshot、Stable更新、更新後Snapshot、Change RecordおよびIndex Snapshotを一つのDocument Transactionとして事前授権できる。ただし、既存HistoryのMutationは全RoleでDenyとし、新規Appendと分離する。

今回の`P2-0-WU-002`はRead-only Recoveryであるため、Phase Designerの一般Role上限にWrite Authorityがあっても有効化しない。Exact Manifest 18件の`READ_AUTO`だけを有効化し、Docs、History、StatusおよびEvidence FileへのWriteは行わない。

## 6. Current Boundary

```text
Automation Pilot : PAUSED
Envelope          : draft-4／not accepted
Role Matrix       : design candidate／pending user review
Role View         : draft-2／not accepted
New Task          : not created
Pilot Retest      : not started
Git／External    : none
```

本Recordの作成はPilot開始、Task作成、Envelope AcceptanceまたはREADY／ARMED宣言を意味しない。

## 7. Related Documents

- [Role Authority Matrix](../../../../shared/task_roles/role_authority_matrix_ja.md)
- [Task Role／Write Authority Policy](../../../../shared/task_roles/task_role_write_authority_policy_ja.md)
- [Automation Control Profile](../../../../shared/automation/automation_control_profile_ja.md)
- [Automation／Governance Evidence Log](../../../../shared/automation/automation_governance_evidence_log_ja.md)
- [Authorization Envelope Draft](../../governance/phase_2_0_authorization_envelope_draft_ja.md)
- [Phase Designer Role View Draft](../../governance/phase_2_0_phase_designer_role_view_draft_ja.md)
- [Bounded Read Retest Redesign](phase_2_0_bounded_read_retest_redesign_20260811001918.md)
- [Role Authority Matrix Redesign](phase_2_0_role_authority_matrix_redesign_20260811010924.md)
