# Phase 10以降 MARGPA Agent Level 1〜3 Gate通知／双方向指示・承認追補予約

```yaml
document_type: planned_work_reservation_correction_and_extension
document_state: accepted_user_direction_not_started
language: ja
created_at: 2026-08-28 11:41:42 JST
public_author: Nazuna Research
project: MARGPA Runtime LLM
corrects_and_extends:
  - phase_10_plus_margpa_agent_level_2_3_important_gate_external_notification_reservation_ja_20260828113608.md
notification_implementation_target: level_2
notification_usage_scope:
  - level_1_margpa_development_agent
  - level_2_margpa_eeae_agent
  - level_3_margpa_fcae_agent
bidirectional_target:
  - level_2_if_bounded
  - level_3_if_material_work_package
implementation_authority: not_granted
external_notification_authority: not_granted
external_instruction_authority: not_granted
external_approval_authority: not_granted
```

## 1. Correction

重要Gate外部通知機能の基本実装時期はLevel 2とするが、利用対象はLevel 2／3だけに限定せず、Level 1〜3すべてとする。

```text
Implementation Milestone : Level 2
Available Capability     : Level 1／Level 2／Level 3
```

Level 1でも長時間のBuild、Test、Review、Rework、Resource待ちまたはHuman Gateが発生し得るため、Level 2で通知基盤が成立した後はLevel 1 Workflowからも同じNotification Portを利用できる構造にする。

本書は先行予約の「Level 1ではOptional」という扱いを、`実装時期はLevel 2、適用対象はLevel 1〜3`へ訂正する。先行予約の一方向通知、Provider-neutral Port、Privacy、Delivery Evidenceおよび通知とApprovalの分離原則は維持する。

## 2. External Gate Detail／Instruction／Approval

Userが外出中またはMARGPA Runtime LLM画面を見ていない場合でも、Gmail／EmailまたはLINEから次を行える将来Capabilityを追加予約する。

- 重要Gateの内容、理由、Severityおよび必要Actionを確認する。
- 現在のRun、Task、Phase、Budget、FailureおよびEvidence概要を確認する。
- Agentへ追加指示を返す。
- 提示されたGateへApprove／Reject／Request Changesを返す。
- 必要に応じてPause／Stop／Resume候補を指示する。
- 詳細確認が必要な場合に、安全なDetail Viewへ移動する。

目標Interactionは次のとおりである。

```text
Agent reaches Important Gate
        ↓
Gmail／LINE Notification
        ↓
User reviews Gate Detail outside the main UI
        ↓
User sends Instruction／Approve／Reject／Pause
        ↓
Inbound Channel Adapter verifies Identity and Request
        ↓
Runtime records Decision Candidate
        ↓
Authority／Scope／Freshness／Conflict Validation
        ↓
Accepted Action or Safe Rejection
```

## 3. Implementation Timing

### 3.1 Level 2同時実装候補

次のBounded構成で収まる場合、Level 2の一方向通知と同時に実装してよい。

- Gate Detailの安全な要約表示。
- Exact Request ID／Gate ID付き通知。
- 限定されたApprove／Reject／Pause等の定型Action。
- Verified Sender／Destination。
- One-time Action TokenまたはAuthenticated Callback。
- Expiry／Replay防止／Idempotency。
- Runtime内Audit／Decision Receipt。

### 3.2 Level 3への延期条件

次が必要となり、独立したPhase級またはMaterial Work Package級になる場合はLevel 3へ送る。

- Gmail／LINEのFree-form返信を一般的なAgent命令として解釈する。
- 複数Account／複数Approver／Delegated Approval。
- Complex OAuth／Webhook／Public Callback Infrastructure。
- Mobile向けDetail Portal。
- Long-lived Conversation ThreadとAgent Runの双方向同期。
- Attachment、Evidence BundleまたはSource Codeの外部Channel表示。
- Multi-step Approval Workflow／Quorum／Escalation Chain。
- Provider障害を跨ぐExactly-once Decision Delivery。

実装量が大きい場合でも、一方向通知までをLevel 2で成立させ、双方向指示・承認だけをLevel 3へ送ることができる。

## 4. Detail Presentation Boundary

Gmail／LINE本文へすべてのRaw Evidence、Prompt、Source Code、Secretまたは個人情報をそのまま送らない。

Gate Detailは段階化する。

```text
Notification Summary
  - Gate Type
  - Severity
  - Run／Request／Gate ID
  - Required User Action
  - Deadline／Expiry
  - Redacted Reason

Authenticated Detail View candidate
  - Expanded Evidence Summary
  - Proposed Action／Diff／Risk
  - Budget／Scope／Authority
  - Approve／Reject／Request Changes
```

Channel本文だけで安全に完結できるGateはChannel内操作を許容できる。機密性、長文、Source Diffまたは複雑なAuthority判断を伴うGateは、認証済みDetail Viewへ誘導する候補とする。

## 5. Inbound Instruction Classification

外部Channelから届いたMessageをすべて同じAuthorityで処理しない。

```text
Free-form Message Received
≠ Authenticated User Identity
≠ Exact Run／Gate Correlation
≠ Valid Instruction
≠ Approval
≠ Authority Expansion
≠ Action Execution
```

Inbound Messageは最低限、次へ分類する。

- `information_request`
- `instruction_candidate`
- `approve_candidate`
- `reject_candidate`
- `request_changes_candidate`
- `pause_candidate`
- `stop_candidate`
- `resume_candidate`
- `unknown_or_ambiguous`

`candidate`は認証、対象Run、Gate Revision、Expiry、Scope、AuthorityおよびConflict検証を通過するまで正式Decisionではない。曖昧な自然言語を「たぶんApprove」と解釈して実行しない。

## 6. Approval Security Contract

Gmail／LINE経由のApprovalは外部Side EffectとAuthority入力を伴うため、少なくとも次を要求する。

- Verified User／Approver Identity。
- Exact Request ID、Run ID、Gate IDおよびGate Revision。
- One-time Nonce／Token。
- Expiry。
- Replay防止。
- Approved Scope／Action／Budgetの明示。
- Stale Gate拒否。
- Duplicate DecisionのIdempotent処理。
- Conflicting DecisionのFail-closed処理。
- Provider Message改変／Forward／Alias／Group送信の考慮。
- Decision ReceiptとRuntime内Canonical Evidence。
- Approval後、実行前にStateが変化した場合の再検証。

Email AddressまたはLINE Accountが一致しただけで包括Authorityを与えない。返信本文、Button、LinkまたはCallbackは、Accepted Authorization Envelopeを拡張しない。

## 7. Channel Adapter Boundary

```text
Outbound Notification Port
├── Gmail／Email Adapter
└── LINE Adapter

Inbound Instruction／Approval Port
├── Gmail／Email Inbound Adapter
└── LINE Inbound Adapter
```

OutboundとInboundを別Capabilityとして管理する。一方向通知だけ利用可能、双方向操作はUnavailableという状態を正確に表示できるようにする。

```text
notification_outbound : active／unavailable／off
instruction_inbound   : active／unavailable／off
approval_inbound      : active／unavailable／off
```

Channel ProviderがMessageを配信したことと、RuntimeがDecisionを受理したことを分離する。

## 8. Level別利用

### Level 1 — MARGPA Development Agent

- 長時間Build／Test／Review完了通知。
- Mutation／Release／Resource Gate。
- ReworkまたはFailureによるUser判断要求。
- Level 2で基盤実装後に利用可能にする。

### Level 2 — MARGPA EEAE Agent

- Notification Foundationの基本実装Target。
- ConsultingからDeploymentまでの重要Gate通知。
- Boundedなら定型Approve／Reject／指示を同時実装。

### Level 3 — MARGPA FCAE Agent

- Operate／Monitor／Evaluate／Repair／Improve／Re-architect／Retire／Next Cycleの長期Gate通知。
- Level 2で完了しなかった双方向指示・承認の本格実装。
- Userが通常画面をほぼ見ない運用を想定したDelivery、EscalationおよびSafe Stop Acceptance。

## 9. Failure／Safe State

- 通知送信失敗をApproval拒否または承認と混同しない。
- 返信取得失敗時にDefault Approveしない。
- Expired／Stale／Unknown MessageはSafe Rejectionする。
- 通知必須Gateでは、Delivery不能時にRuntime内Gateを保持する。
- User応答待ち中にAgentが同じGateを迂回しない。
- Stop／Pause指示は対象RunとCurrent Stateを再確認する。
- Provider障害時は別Channel、Runtime内通知またはSafe StopへFallbackする。
- 外部Channelからの指示でConstitution、Sandbox、PolicyまたはHuman-only Amendment RuleをBypassしない。

## 10. Reserved State

```text
Notification Implementation Target : LEVEL 2
Notification Usage Scope           : LEVEL 1／2／3
Outbound Gmail／LINE                : PHASE 10+ CANDIDATE
Inbound Instruction                : LEVEL 2 IF BOUNDED／OTHERWISE LEVEL 3
Inbound Approval                   : LEVEL 2 IF BOUNDED／OTHERWISE LEVEL 3
Free-form General Commands         : MATERIAL SCOPE／LEVEL 3 CANDIDATE
Current Implementation             : NOT STARTED
Current External Account Authority : NOT GRANTED
```

## 11. Non-authorization

本書は予約であり、Gmail、LINE、Email、Webhook、OAuth、External Account、Credential、Network、Frontend、Backend、SchemaまたはAgent実装への操作権限を与えない。Level 2／3開始、Message送信、外部指示受信またはApproval実行も開始しない。
