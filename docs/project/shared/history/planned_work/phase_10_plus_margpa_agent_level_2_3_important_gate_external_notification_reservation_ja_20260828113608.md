# Phase 10以降 MARGPA Agent Level 2／3 重要Gate外部通知予約

```yaml
document_type: planned_work_reservation_followup
document_state: accepted_user_direction_not_started
language: ja
created_at: 2026-08-28 11:36:08 JST
public_author: Nazuna Research
project: MARGPA Runtime LLM
target_phase: phase_10_or_later
target_capability_levels:
  - level_2_margpa_eeae_agent
  - level_3_margpa_fcae_agent
extends:
  - phase_8_margpa_development_agent_research_preview_and_phase_10_capability_levels_reservation_ja_20260828084745.md
implementation_authority: not_granted
external_notification_authority: not_granted
external_account_contact_authority: not_granted
```

## 1. User Direction

`MARGPA End-to-End Autonomous Engineering Agent` Level 2および`MARGPA Full-Cycle Autonomous Engineering Agent` Level 3では、Userが常時MARGPA Runtime LLMの画面を監視していることを前提にしない。

特にLevel 3の利用像は次のとおりである。

> UserはProblemと方向だけを与える。Agentは研究、設計、実装、検証、運用および改善を自律的に進め、重要GateでだけUserを呼ぶ。

そのため、重要Gateへ到達した際に、Gmail／EmailまたはLINE等へ通知できる外部通知機能をPhase 10以降の候補として予約する。実装がBoundedに収まる場合は、Level 2実装時点で前倒ししてよい。

Level 1段階の必須Completion Dependencyにはしない。

## 2. UI Candidate

Settingsに`通知`または`Notifications` Categoryを追加する候補とする。

最低限、次を設定可能にする。

- 外部通知のOFF／ON。
- 通知Channel。
- Gmail／Email Adapter。
- LINE Adapter。
- 通知対象Gate。
- Quiet Hours／抑制時間帯。
- 同一Eventの重複抑制。
- Test Notification。
- Recipient／Destination Allowlist。
- 通知本文のDetail Level／Redaction Profile。
- Delivery Status／Failure Reason。

名称、画面配置、Channelおよび既定値は実装時に再設計する。本予約だけでGmail、LINE、外部Account、CredentialまたはAPIへ接触しない。

## 3. Notification Boundary

通知はAgentの内部状態と外部Providerを疎結合にする。

```text
Agent／Workflow Event
        ↓
Important Gate Classifier
        ↓
Notification Policy／User Preference
        ↓
Notification Port
        ↓
Gmail／Email Adapter or LINE Adapter
        ↓
Delivery Receipt／Failure Evidence
```

GmailまたはLINEをAgent CoreへHard-codeしない。後から別Channelを追加できるProvider-neutral Notification Portを設ける。

## 4. Important Gate Candidate

すべてのStepを通知してUserを疲弊させず、重要Gateだけを対象にする。

候補は次のとおりである。

- Human Approvalが必須になった。
- 事前Authorization Envelopeの終端へ到達した。
- Scope、Authority、Budgetまたは外部Side Effectの拡張が必要になった。
- Release／Deploy／Production Promotion Gateへ到達した。
- Cost、Token、時間、StorageまたはCompute Budgetの閾値へ到達した。
- Security、Privacy、Secret、PolicyまたはConstitution Incidentを検出した。
- Repeated Failure、Repair Budget ExhaustionまたはSafe Stopが発生した。
- External Dependency／Provider／Human Input待ちでBlockedになった。
- Architectureの重大変更、MigrationまたはRe-architecture判断が必要になった。
- Data Migration、Destructive Action、Irreversible ActionまたはRetirement Gateへ到達した。
- End-to-End案件のAcceptance Candidateが完成した。
- Full-Cycleの運用評価、改善提案またはNext Cycle Gateへ到達した。
- Agent自身が「通常画面を継続監視していないUserを呼ぶべき」と判断したが、通知Policy上の条件を満たした。

Gate Classifierが通知対象と判断したことは、Action Authority、Approval成立またはGate通過を意味しない。

## 5. NotificationとApprovalの分離

最初の実装候補は一方向通知とする。

```text
Notification Sent
≠ User Viewed
≠ User Acknowledged
≠ User Approved
≠ Authority Granted
≠ Action Executed
```

Gmail／LINEのMessageへ返信したことを自動的に正式Approvalとして解釈しない。将来、外部ChannelからApprove／Rejectできる双方向Approvalを追加する場合は、Identity、Authentication、Request ID、Nonce、Expiry、Replay防止、Exact Scope、Signature／Callback ValidationおよびAuditを別Gateで設計する。

通知送信に失敗しても、通知必須Gateを黙って通過しない。対象GateのContractに従い、Runtime内表示、Retry、別Channel、Safe StopまたはUser Input待ちへ収束させる。

## 6. Privacy／Security／Reliability

外部通知は外部Side Effectであり、明示Opt-inを必須とする。

最低限、次を設計する。

- Credential／TokenをSource、Docs、GitまたはEvidenceへ平文保存しない。
- Recipient／Destinationの明示登録と確認。
- Raw Prompt、Secret、個人情報、Source Codeまたは内部Evidenceを既定で全文送信しない。
- Notification PayloadのRedaction／Minimization。
- Request ID／Run ID／Gate IDによる相関。
- Idempotency、Deduplication、Rate LimitおよびRetry Budget。
- Delivery Attempt、Provider Response、Delivery ReceiptおよびFailure ReasonのEvidence。
- 通知洪水を防ぐAggregation／Cooldown。
- Provider障害時のFallbackとSafe Failure。
- Channel別Retention／Deletion／Privacyの説明。
- Test Notificationと本番通知の分離。

「自己責任Mode」であっても、Credential、外部送信、Recipient、SecretおよびPrivacy境界を自動的に解除しない。

## 7. Capability Levelとの関係

### Level 1

Optional。通常画面を見ながらBoundedな開発Taskを行う段階では必須にしない。

### Level 2

実装が小さくBoundedに収まる場合、重要Gate通知の最初の実用候補とする。ConsultingからDeploymentまでの長時間Workflowで、Userが画面から離れていてもHuman Gateを見落とさないために使用する。

### Level 3

長期間にわたり研究、運用、監視、評価、修復、改善、再設計および次Cycleを自律実行するため、実用上は重要なControl Surfaceとする。Level 3の正式Acceptanceでは、重要Gate通知、Delivery Failure、User不在、Acknowledgement待ちおよびSafe StopのContractを検証対象にする。

ただし、外部通知Channelが一つ利用不能であるだけでLevel 3 Coreを永久に不成立とするかは、Channel Capability、Runtime内通知および代替Providerを含めて後続Gateで決定する。

## 8. Observability／Evidence Candidate

Runtime内では最低限、次を表示または記録する。

- Notification Mode。
- Configured Channel／Active Channel。
- Latest Gate ID／Run ID／Request ID。
- Gate Type／Severity／Required Action。
- Created／Queued／Sent／Delivered／Failed／Acknowledged候補のState。
- Attempt Count／Retry Budget。
- Redaction Profile。
- Provider Failure Reason。
- User Action待ちか、通知だけでWorkflow継続可能か。

通知本文だけを正本とせず、Runtime内State／Evidenceを正本とする。Provider側Messageが削除、遅延または重複しても、Agent Stateを推測で進めない。

## 9. Implementation Timing

```text
Phase 8 Research Preview          : NOT REQUIRED
Level 1 Formal Completion        : OPTIONAL
Level 2 Implementation           : EARLY CANDIDATE IF BOUNDED
Level 3 Practical Operation      : IMPORTANT／ACCEPTANCE CANDIDATE
Target Phase                     : PHASE 10 OR LATER
```

Level 2着手時に、Notification Port、一方向通知、Settings、重要Gate数種およびDelivery Evidenceが小規模に成立するなら同時実装してよい。Gmail／LINE固有認証、双方向Approval、複雑なWebhook InfrastructureまたはMobile PushがPhase級工事になる場合は、別Work Packageへ分離する。

## 10. Non-authorization

本書は予約であり、次を許可しない。

- Gmail／Google Accountへの接続。
- LINE Account／Messaging APIへの接続。
- Email／Message送信。
- Credential作成、読取、保存または変更。
- Settings／Backend／Frontend／Schemaの実装開始。
- Network、Webhook、OAuth、External API操作。
- Phase 10、Level 2またはLevel 3の開始。
