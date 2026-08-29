# Phase 6 GitHub Copilot Post-Claude R3〜R8 Execution Instruction Package

```yaml
document_id: phase_6_copilot_post_claude_r3_to_r8_execution_instruction_package_20260828193037
document_type: cross_provider_copy_paste_instruction_package
document_state: ready_after_user_backup
language: ja
created_at: 2026-08-28 19:30:37 JST
controller: Codex_プロジェクト責任者兼設計統括者役
target_provider: GitHub Copilot app
target_role: 設計者兼実装者役
message_count: 3
backup_required_before_message_3: true
```

## 1. 使用順序

UserがBackupを取得した後、新しいGitHub Copilot TaskへMessage 1を送る。ReceiptがExactであればMessage 2、二つ目のReceiptもExactであればMessage 3を送る。

三つを一度に送らない。Role、Contract、Implementation Authorityを段階的に成立させる。

## 2. Message 1 — Fresh Role／Authority Bootstrap

以下をそのまま送る。

```text
【Fresh GitHub Copilot Task Role／Authority Bootstrap】

Provider: GitHub Copilot app
Role: 設計者兼実装者役
Task Identity: Fresh Copilot Phase 6 Differential Continuation Task

このTaskはFresh Taskです。
旧Copilot、Claude、Codex Taskの会話Context、Memory、Authority、未完了状態、Tool State、自己判断したScopeを一切継承しないでください。

現在許可するのは、次の3文書のReadとReceipt返却だけです。
まだ実装、Source／Test／Config／Docs Mutation、Command実行、Network、Git、Model Load、Browser、Provider Memory、User runtime_dataまたはProject Root外Actionを開始しないでください。

1.
<PROJECT_ROOT>/docs/project/shared/task_roles/copilot_side_designer_implementer_operating_notes_ja.md

2.
<PROJECT_ROOT>/docs/project/shared/task_roles/copilot_side_long_running_automation_companion_ja.md

3.
<PROJECT_ROOT>/docs/project/shared/task_roles/copilot_side_implementation_internal_review_rework_loop_operating_contract_ja.md

3文書を抜粋やSummaryではなく全文読了してください。

読了後、次だけを日本語で返してください。

Provider: GitHub Copilot app
Role: 設計者兼実装者役
Task Identity: Fresh Copilot Phase 6 Differential Continuation Task
Mandatory Stable Role Reading: COMPLETE
Old Context / Memory / Authority Inheritance: NONE
Autopilot / Harness Creates Project Authority: FALSE
Implementation Authority: FALSE
State: WAITING_FOR_EXACT_HANDOFF

返却後は停止してください。
```

## 3. Message 2 — Exact Handoff／Mandatory Reading Bootstrap

Message 1のReceiptがExactな場合、以下をそのまま送る。

```text
【Phase 6 GitHub Copilot Post-Claude R3〜R8／Exact Handoff Bootstrap】

ClaudeがPackage R3途中で停止した状態から、R3のCurrent Partialを保全し、R3〜R8を差分継続するExact Handoffを渡します。

Canonical Project Root:
<PROJECT_ROOT>

Exact Handoff:
<PROJECT_ROOT>/docs/project/phases/phase_6/handoffs/phase_6_copilot_post_claude_r3_to_r8_exact_continuation_handoff_ja_20260828193037.md

Exact Handoff SHA-512:
a71d747d4715c550ebc51de5c543bcd76be520329c500bfe57ac15a1bf079d67f14e249134e079d9f49a7c374de0ae7072fa63d1f0da0bb8d93d77baafba2bab

Controller R3 Reconstruction:
<PROJECT_ROOT>/docs/project/phases/phase_6/history/index/phase_6_copilot_takeover_after_claude_r3_partial_controller_reconstruction_ja_20260828193037.md

Controller R3 Reconstruction SHA-512:
f7f5702820b967430ea5c501057952d2944de106a8a8ef650c459c11b6b18ef8dc0ba9c87d50573b68326f9ad06af7cb14c0ae3bb4d091c4084d6564cc82404b

Exact Handoff §4のMandatory Reading全29件を、指定順で抜粋せず全文読んでください。
Handoff §5のDigestを照合してください。

現在の正本状態は次です。

- Phase 6 Package 0〜I: PRESERVED
- Claude Package K〜Q: P6-GOV-019で棄却されていない範囲をPRESERVED
- Rework R0〜R2: PACKAGE COMPLETE／再実装禁止
- R3: PARTIAL／UNVERIFIED／Current SourceをRollback禁止
- R4〜R8: NOT STARTED
- P6-CODEX-062／063: R1／R2修正候補成立、Controller再Review待ち
- P6-CODEX-064〜067: OPEN
- P6-CODEX-068: ACKNOWLEDGED、R8で最終是正
- Historical Unauthorized Git Read: 1を保持

この段階ではまだ実装、Source／Test／Config／Docs Mutation、Test／Build、Network、Git、Model LoadまたはRoot外Actionを開始しないでください。
Digest照合に必要なProject Root内Read-only SHA-512 Commandだけを許可します。Git Commandは禁止です。

読了・照合後、次だけを日本語で返してください。

Provider: GitHub Copilot app
Role: 設計者兼実装者役
Task Identity: Fresh Copilot Phase 6 Differential Continuation Task
Mandatory Reading: COMPLETE / MISSING
Exact Handoff Digest: MATCH / MISMATCH
Controller R3 Reconstruction Digest: MATCH / MISMATCH
Copilot Stable 3 Digest: MATCH / MISMATCH
Active Contract: Phase 6 Copilot Post-Claude R3〜R8 Exact Differential Continuation Handoff
Preserved Baseline: Phase 6 0〜I／Claude K〜Q accepted scope／Rework R0〜R2
Partial Preserved: P6-RR-R3 Current Source
Redo Prohibited: Phase 6 0〜I／Claude K〜Q／Rework R0〜R2
Next Exact Work Unit: P6-RR-R3-WU-001_REDERIVATION_WITH_CURRENT_PARTIAL_PRESERVED
Git / Network / Root-outside / Provider Memory / User runtime_data / Real Model Authority: FALSE
Implementation Authority: FALSE
State: WAITING_FOR_EXACT_USER_START

Digest不一致またはMissingがあれば、Observed DigestとExact Pathを返してください。
Receipt返却後は停止してください。
```

## 4. Message 3 — Exact User Start

Message 2のReceiptがExactであり、User Backupが完了済みなら、以下をそのまま送る。

```text
Phase 6 Copilot Differential Continuationを開始する。

この開始Messageの送信により、User Backup Gateは完了済みです。Copilot自身はBackupを取得・検査・変更しないでください。

Phase 6 Copilot Post-Claude R3〜R8 Exact Differential Continuation HandoffをActive Execution Contractとして、P6-RR-R3-WU-001_REDERIVATION_WITH_CURRENT_PARTIAL_PRESERVEDから開始してください。

R3のCurrent Partial七FileをRollbackしないでください。最初にR3-WU-001〜008の成立範囲をCurrent Source／Testから再導出し、Focused／Staticで検証して、不成立または中断部分だけを差分実装してください。

Phase 6 Package 0〜I、Claude K〜Q、Rework R0〜R2を再実装しないでください。

R3完了後、元Exact Rework ContractどおりR4、R5、R6、R7、R8を連結実行してください。

初回Copilot Pilotとして、次を必ず守ってください。

1. 最初のCommand／Mutation前にshared/history/automationへPilot Entry Evidenceを作成。
2. 各Work Unit直後にPhase 6 history/indexへAppend-only Checkpointを作成。
3. 各Package Entry／FinalでRecovery Indexを作成。
4. Full Test、Frontend Build、長時間Command、Compaction、Resource Stop前にRecoveryを確定。
5. Progress報告後もTrue StopまたはExact Returnまで自走。
6. Compaction／Session／利用制限復帰後はStable 3文書、Active Handoff、最新2 Index、Current Packageを全文再読。
7. 実装後にImplementation Freeze → Internal Review 1 → Finding Ledger → Rework → Internal Review 2 → Final Verificationを最大二周で実行。
8. Self-reviewをCodex Independent ReviewとClaimしない。

Task-owned Temporary、pytest basetemp、Cache、TMPDIRおよびLogは次へ固定してください。

<PROJECT_ROOT>/.venv/.t/phase_6_copilot_continuation_20260828193037/

GitはRead-onlyを含め全禁止です。Network、MCP、Provider Memory、User runtime_data、Project Root外Action、Real Model Load、Backup、Stable Shared Docs、Roadmap、Public Docs、Constitution、Phase 6 ClosureおよびPhase 7も禁止です。

Selene／Qwen3GuardのReal Model／Network Authority不足だけを全体停止理由にしないでください。Authority不要のRouter、Lifecycle、Semantic 109、Budget、Repair Rejudge、Failure、Observability、Recording、Fixture、Negative Path、UIおよびRegressionを継続し、Real Model項目だけをNOT RUN／AUTHORITY REQUIREDへ分類してください。

最大ClaimはComplete Candidateまでです。

完了、IncompleteまたはStopped-safe時はExact Return Handoffと最新Recoveryを作成し、Provider／Role／Task Identity、R3再導出、R3〜R8 Disposition、Finding、Verification、Incident、Action Inventory、Copilot Pilot EvidenceおよびExact Next Actionを日本語で返してください。

返却後はCodexプロジェクト責任者兼設計統括者役によるIndependent Review待ちで停止してください。
```

## 5. Receipt Acceptance Rule

Message 1／2のReceiptに欠落、旧Authority継承、実装開始、Git許可、R0〜R2再実装またはR3 Rollbackが含まれる場合、Message 3を送らない。ControllerがCorrection Messageを作成する。

## 6. Current Gate

```text
Instruction Package: READY
User Backup: REQUIRED BEFORE MESSAGE 3
Copilot Pilot: NOT STARTED
Implementation Authority: FALSE UNTIL MESSAGE 3
```
