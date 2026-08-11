# Phase 2-0 Bounded Read Retest Redesign Evidence

```yaml
document_id: phase_2_0_bounded_read_retest_redesign_20260811001918
status: append_only_design_revision_evidence
phase: phase_2
subphase: phase_2_0
language: ja
created_at: 2026-08-11 00:19:18 JST
owner: プロジェクト責任者兼設計統括者役
control_state_after: PAUSED_REDESIGN
new_task_created: false
git_mutation: false
```

## 1. Authorization Boundary

ユーザーは、初回Pilot Evidence記録後にEnvelope draft-3と関連Docsの再設計を明示した。本TransactionはDocs再設計とRead-only Validationに限定し、次を行っていない。

```text
Envelope Acceptance : no
Pilot Restart       : no
New Task Creation   : no
Old Task Action     : no
Local Runtime Change: no
Git Commit／Push    : no
External Mutation   : no
```

## 2. Source Observation

初回`P2-0-WU-001`はAuthority Acknowledgement、Fail-closed StopおよびMutation 0に成功した一方、Provider-native Local Reader不在とShell全面禁止の組合せにより、18件中0件しか読めずRecoveryに失敗した。

再設計時、RequirementsとHandoffへ重複記載されたReading ListのEntry 8が一致していないことも確認した。再試験前にRead対象の正本を一つへ統合しなければ、Capability問題を解消してもSource選択が曖昧になる可能性があった。

## 3. Design Decision

```text
Old Work Unit       : P2-0-WU-001 consumed
Old Task            : retained as idle evidence／no action
New Work Unit Draft : P2-0-WU-002 Bounded Read Cold Recovery Retest
New Task Draft      : exactly one after fresh user acceptance
Read Source         : p2-0-read-manifest-001 single source
Core Capability     : bounded_local_text_read
Provider Adapter    : Codex Desktop-specific allowed grammar
Write／Git／External : none
Control State       : PAUSED／REDESIGN
```

Normative CoreはAuthorized Root、Exact Manifest、Digest、Complete Coverage、Mutation禁止、EvidenceおよびStopだけを扱う。Codex固有Executable、Command Grammar、Tool ParameterおよびTask Registration挙動はProvider Adapterへ隔離した。

## 4. Provider Adapter Boundary

Design候補として許可した形式は、Exact Manifest Entryに対する次の三つだけである。

```text
Line Count
SHA-512
250行以内の連続Page Read
```

Shell一般、Directory探索、Glob、Pipe、Redirection、Git、Network、Sandbox Escalation、Temporary Artifact、代替Commandおよび自動Retryは禁止した。

Task Registrationは`Task ID返却 → Registration観測 → Exact Title設定 → Read-back → Handoff`へ分離し、固定Sleepまたは無制限Retryを設計しなかった。

## 5. Design-time Validation

```text
Exact Manifest Paths Exist : 18／18
Relative Links Checked     : 109
Relative Link Failures     : 0
Allowed Grammar Sample     : wc／shasum／sed, all exit 0
Sandbox Escalation         : none
Temporary Artifact         : none
git diff --check           : pass for redesigned scope
```

SampleはManifest Entry 1件をExact Workdir、Default Sandboxおよび`login: false`でRead-only検証した。これは全18件のFreeze、Child Task内実行、Context成立またはRecovery成功を意味しない。

## 6. Design Artifact Digests

```text
Envelope draft-3:
  5c65f7faa047dc9bd0c5b4871417fc3945d8e89245b69439c4cb2ddd80dfbf1a471636ccbbda3e451f7e4cdb022e43e4896c96e419628014969fa841efdec41c

Read Manifest draft-1:
  eafaf87b49f6ffaeedf9e22be0f8f55f5205907016047d2b6a443be4e50308f4139b6b33566c79e2a57d146612d036c2eec4f26ee687546c22b8b0ae714538b4

Bootstrap Handoff draft-3:
  26bd9266297deef3c6fa42248f3f6b5be175480a44f65131fe0ba29a0bbf238480b0e2fc18fc130992e6611650cfd0c7c41c72bc9f94ee1d1cf84835b9cbf5ce

Codex Desktop Bounded Read Adapter:
  d4e7b1a18b90cb8b0159574a86c1a861c986df39af2cfc2f5898a1c8f013900d7feeaaa653f6f5ebc740ee3958163baf1b06e8b4f7919d53962c001b241bd7a2
```

これらはDesign Revisionの監査Digestであり、Acceptance用Detached Freeze Receiptではない。後続修正があれば再計算し、旧Digestを流用しない。

## 7. Current Gate

次に必要なのはDesign Package最終Validation、Provider Adapter Full Preflight、Detached Freeze Receipt、必要なGit／Backup Gate、Exact draft-3 User Acceptance、Controller READY／ARMEDおよび後続User Startである。

本書はそれらを成立させず、新TaskまたはPilot再開を許可しない。

## 8. Related Documents

- [Phase 2 Index](../../phase_index_ja.md)
- [Authorization Envelope draft-3](../../governance/phase_2_0_authorization_envelope_draft_ja.md)
- [Bounded Read Manifest](../../governance/phase_2_0_bounded_read_manifest_draft_ja.md)
- [Execution Plan](../../operations/phase_2_0_automation_pilot_execution_plan_ja.md)
- [Bootstrap Handoff draft-3](../../handoffs/phase_2_0_phase_designer_bootstrap_handoff_draft_ja.md)
- [Codex Desktop Bounded Read Adapter](../../../../shared/automation/provider_adapters/codex_desktop_bounded_read_adapter_ja.md)
- [Initial Pilot Evidence](phase_2_0_initial_automation_pilot_execution_evidence_20260811000435.md)
