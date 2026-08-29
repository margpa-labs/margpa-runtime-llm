# Claude Task再生成とCross-provider Role Identity Operating Correction

```yaml
document_id: claude_task_recreation_and_cross_provider_role_identity_operating_correction_20260826094454
status: adopted_for_future_operation
classification: automation_operating_correction
created_at: 2026-08-26 09:44:54 JST
scope: claude_fresh_task_and_cross_provider_role_identity
execution_activation: not_performed_by_this_document
supersedes: claude_role_title_design_governor_for_future_tasks
git_authority: not_granted_by_this_document
```

## 1. Correction概要

Claude Taskを長期利用した後に週間利用可能量または5時間制限が回復しても、旧TaskをそのままCurrent Executorとして再利用することをDefaultにしない。Frozen HandoffとCurrent差分DocsからFresh Taskを起動し、旧Context、旧AuthorityおよびAuto Compaction後の曖昧な状態を非継承とする。

また、ClaudeのCurrent Role名を`設計統括者役`から`設計者兼実装者役`へ変更する。ClaudeはProject全体の最終設計統括Authorityではなく、Frozen Contractに基づく詳細設計、実装、検証、RecoveryおよびReworkを主に担当しているためである。

## 2. Fresh Taskを採用する理由

新Taskの作成によってProvider Account全体の週間利用可能量または5時間制限がResetされるとは扱わない。一方、Fresh Taskには次の効果を期待できる。

- 蓄積Contextの削減。
- Auto Compaction後の曖昧な状態の排除。
- 旧Authorityおよび撤回済み仕様の混入防止。
- Exact HandoffからのClean Start。
- 不要な途中停止、過去状態の誤継承および自己解釈の抑制。

これらは期待効果であり、Resource Savingsを保証するものではない。Mandatory Readingの再読Cost、Fresh TaskのContext不足またはRework増加により相殺される可能性がある。実際の効果は後続Automation Evidenceで評価する。

## 3. Claude Task再生成Default

```text
旧Claude Task
  -> Historical TaskへRename
  -> 過去Evidence参照用として保持
  -> Current WorkのDefault送信先にしない

新Claude Task
  -> Provider: Claude
  -> Role: 設計者兼実装者役
  -> Frozen Exact Handoff＋Mandatory Readingのみを正本とする
  -> 旧Context／Provider Memory／Authority／未完了状態を非継承
```

Claude復帰時には、その時点のCodex実装結果と残件を基にClaude専用の差分Handoffを作成する。Codexが完了した範囲を最初から重複実装させず、Independent Review、残Rework、未実装PackageまたはResource停止後の差分再開へ投入する。

## 4. Cross-provider Role整理

今後の基本Roleは次の通りとする。

| Provider | Task Role | 主責務 |
|---|---|---|
| Codex | プロジェクト責任者兼設計統括者役 | Authority／Architecture／Acceptance Freeze、Independent Review、Rework判定、Closure Recommendation |
| Codex | 設計者兼実装者役 | 詳細設計、実装、Test、Recovery、Exact Rework |
| Claude | 設計者兼実装者役 | 詳細設計、実装、Test、Recovery、Exact Rework |

ClaudeとCodex ExecutorのRole名が同一でも、同一Task、同一Provider、同一Authorityまたは相互代替可能性を意味しない。Roleは責務Classを示し、実在するActorはProviderとTask Identityで区別する。

## 5. Identity Envelope必須化

Task間Handoff、Return、ReviewおよびEvidenceでは、原則として次を併記する。

```text
Provider      : Codex / Claude
Role          : 設計者兼実装者役
Task Identity : Exact Task／Thread／Session Identity
Contract      : Exact Handoff Path／Revision／Digest
Authority     : GRANTED_BUT_NOT_ACTIVATED / ACTIVATED / STOPPED
```

Role TitleだけをRouting Authorityとして使用しない。特に`設計者兼実装者役`はCodexとClaudeの双方に存在するため、Provider省略やTask Identity省略による誤配送を防ぐ。

Task TitleはHuman-readable Label、Frozen HandoffはRole／Scope／Authorityの正本、Task／Thread／Session Identityは配送先の正本として分離する。

## 6. Claude Role名Correction

```text
Historical／Former Label : 設計統括者役
Current／Future Label    : 設計者兼実装者役
```

このCorrection後、Claudeへ次のAuthorityを自動付与してはならない。

- User Authority。
- Project全体の最終設計変更権。
- Frozen Acceptance変更権。
- Independent Closure判定権。
- Git／Network／External Service／Destructive Action権限。

ClaudeはFrozen Contract内で設計判断を行えるが、Contractそのものを自己拡張しない。

既存File名`claude_side_design_governor_operating_notes_ja.md`はHistorical Nameを含む。File名の変更は本書のScope外であり、当面は内容をClaude運用メモとして使用する。ただし、File名から`設計統括者役`Authorityを再導出しない。

## 7. 新Claude TaskのOnboarding順序

1. Fresh Task作成とTask Identity固定。
2. Codex Controllerから実行Authority成立条件とDocs取扱Authorityだけを通知。
3. 次の2運用メモを全文読了。
   - `docs/project/shared/task_roles/claude_side_design_governor_operating_notes_ja.md`
   - `docs/project/shared/task_roles/claude_side_long_running_automation_companion_ja.md`
4. Authority／Role／非継承／実装未開始のReceipt。
5. Codex ControllerがCurrent差分Handoffを作成。
6. 必要DocsだけをExact順序で配送。
7. User StartまたはFrozen Activation条件成立後にLong Run開始。

詳細予約は次を正本とする。

`docs/project/shared/history/planned_work/claude_fresh_designer_implementer_task_activation_sequence_reservation_ja_20260826094454.md`

## 8. 旧Task Retention

旧Claude Taskは、過去のCompaction、5時間制限、False Completion、Recovery、Rework、Provider挙動およびUser Relayを検証するHistorical Evidenceとして保持できる。新旧TitleとSession Identityが分離できる場合、ArchiveまたはDeleteを必須としない。

旧Taskを参照した場合も、過去会話をCurrent Authorityとして扱わず、Current Frozen Handoffへ照合する。

## 9. Codex側運用Evidenceとの接続

本Correctionは、Codex側で成立したFresh Executor TaskのIdentity Routing／Authority Delivery試験をClaude運用へ展開するものである。

- `docs/project/shared/history/automation/codex_task_recreation_identity_routing_authority_delivery_and_resource_preservation_evidence_ja_20260826092621.md`
- `docs/project/shared/history/automation/codex_two_task_long_run_review_rework_orchestration_reservation_ja_20260823095316.md`
- `docs/project/shared/history/automation/codex_two_task_phase_6_parallel_controller_resource_observation_ja_20260825014841.md`

Codexで成立したDirect Task MessagingがClaudeでも使用可能とは推定しない。Claude側Return経路はActivation時の実測に基づき、Direct Return、Repository HandoffまたはUser Relayを正確に分類する。

## 10. 後続検証

新Claude Taskを実際に使用した後、次をAutomation Evidenceとして記録する。

- Fresh Task作成と旧Task Retention。
- Authority通知とReceipt。
- 2運用メモ読了。
- Old Context／Memory／Authority非継承。
- Current差分Handoffと重複実装の有無。
- Long Run、Auto Compactionおよび5時間制限後のRecovery Fidelity。
- Independent Reviewで検出したFinding。
- Rework回数、False Completion、Scope／Authority Incident。
- ClaudeとCodex双方の利用可能量消費傾向。
- Cross-provider Role／Identity Envelopeの誤配送防止効果。

## 11. 現在地

```text
Claude Role Rename Policy          : ADOPTED FOR FUTURE TASK
Fresh Claude Task                  : NOT CREATED BY THIS DOCUMENT
Old Claude Task Rename／Retention  : RESERVED
Authority Delivery                : RESERVED
Operating Notes Reading           : RESERVED
Current Delta Handoff             : NOT CREATED
Claude Long Run                   : NOT STARTED
Cross-provider Identity Envelope  : ADOPTED
Execution Evidence                : NOT YET RECORDED
```
