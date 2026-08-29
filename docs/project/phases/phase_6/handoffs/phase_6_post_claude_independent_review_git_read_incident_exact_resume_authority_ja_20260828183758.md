# Phase 6 Post-Claude Independent Review — Git Read Incident Exact Resume Authority

```yaml
document_id: phase_6_post_claude_independent_review_git_read_incident_exact_resume_authority_20260828183758
incident_id: P6-RR-R-INC-001
status: RECORDED_NON_BLOCKING_EXACT_RESUME_AUTHORIZED
classification: controller_incident_disposition_and_differential_resume_authority
created_at: 2026-08-28 18:37:58 JST
authority_owner: プロジェクト責任者兼設計統括者役
target_provider: Claude
target_role: 設計者兼実装者役
active_handoff: phase_6_post_claude_independent_review_exact_rework_handoff_ja_20260828180240.md
resume_work_unit: P6-RR-R0-WU-001
phase_6_closure: PROHIBITED
git_action_after_resume: PROHIBITED
```

## 1. Controller Decision

Claude Taskは、Active ContractがGit Read-only Actionも禁止している状態でGit Read Commandを1回実行したと自己申告し、True Stop Conditionとして停止した。この停止判断は正しい。

同時に、現在確認できる事実は次である。

```text
Unauthorized Git Read Action : 1
Git Mutation                 : 0
Stage／Commit／Branch／Push   : 0
Network Action               : 0
Secret Exposure              : 0 known
Source／Test／Config Mutation : 0
Persistent Root-outside Write: 0 known
```

違反は遡及的に0へしない。一方、Working Tree、Source、Test、Config、NetworkまたはSecretへMaterial Mutationがなく、Technical Reworkの成立済みBaselineを破棄する理由はない。

Controllerは本Incidentを次へ分類する。

```text
P6-RR-R-INC-001:
  RECORDED
  STOPPED_SAFE
  REVIEWED_BY_CONTROLLER
  PROCESS_NONCONFORMANCE
  TECHNICALLY_NON_BLOCKING
  EXACT_DIFFERENTIAL_RESUME_AUTHORIZED
```

P6-GOV-019のController IncidentをClaudeが自己判断の前例として流用することは認めない。本書により、今回のClaude IncidentだけをController Authorityで非Blockingと判定する。

## 2. Mandatory Incident Evidence Before Resume

Claudeは新しいSource／Test／Config／Frontend Mutationまたは実装Commandより前に、次の2 Artifactを作成する。

1. Incident Evidence

```text
Directory:
docs/project/phases/phase_6/history/operations/

Filename pattern:
phase_6_post_claude_independent_review_p6_rr_r_inc_001_unauthorized_git_read_incident_ja_<timestamp>.md
```

最低限含めるもの：

- Incident ID。
- 実行したExact Command。
- 実行日時または観測可能なTimestamp。
- Command OutputのCategory。内容全文を不必要に複製しない。
- OutputがSession冒頭で既知だった情報と同一というClaude申告。
- Git Read 1、Git Mutation 0。
- Network／Secret／Provider Memory／User runtime_data／Root外Persistent WriteのInventory。
- Stop判断。
- 本Controller Disposition Path／Digest。
- Incidentを0へしない宣言。

2. Entry／Resume Recovery Index

```text
Directory:
docs/project/phases/phase_6/history/index/

Filename pattern:
phase_6_post_claude_independent_review_rework_r0_entry_after_git_read_incident_ja_<timestamp>.md
```

最低限含めるもの：

- Active Contract Path／Digest。
- 本Resume Authority Path／Digest。
- Context Compaction 96%実施済みというUser報告。
- 5時間枠残39%という直前User報告。Current値を推測更新しない。
- Source／Test／Config Mutation 0時点。
- Last Completed Work Unit：none in R0。
- Exact Next Work Unit：P6-RR-R0-WU-001。
- Recovery Indexを各Work Unit／Package／高Cost処理前に残すContract。

## 3. Resume Scope

上記2 Artifact作成後、P6-RR-R0-WU-001から差分再開する。

```text
Redo Package 0-I                 : PROHIBITED
Redo accepted Package K-Q scope : PROHIBITED
Start R1 before R0 Index        : PROHIBITED
Further Git Read／Mutation       : PROHIBITED
Exact Next Work Unit             : P6-RR-R0-WU-001
```

本Incident時点でRework R0のSource Mutationが0であるため、Rollbackは不要である。Git Outputを設計EvidenceまたはSource Truthとして再利用しない。

## 4. Recovery／Compaction／Resource Contract

元のClaude Execution Instruction Packageにある次を変更しない。

- 各Work Unit直後のCheckpoint。
- 各Package Entry／Final Recovery Index。
- Long-running Command、Full Test、Build、Compaction、Resource Stop前のCheckpoint。
- Compaction／5時間制限解除後のStable Role 3文書、Active Handoff、最新2 Index、Current Package再読。
- 成立済みWork Unitを再実行しない差分Resume。

今回、96% Compaction後にUserがMessage 1〜3を再投入したことをConversation Evidenceとして受領する。ただし、Repository正本とDigestを優先する。

## 5. Authority／Prohibition

本書が新たに許可するのは、Incident Evidence、Entry／Resume Recovery Indexおよび既存Exact Rework Handoff内の差分実装再開だけである。

引き続き禁止：

- 全Git Action。Read-onlyを含む。
- Network。
- Provider Memory。
- User runtime_data。
- Project Root外Model Artifact。
- Phase 6 Closure。
- Phase 7。
- Roadmap／Public／Stable Constitution。
- Backup。
- Historical Evidenceの削除／上書き。

## 6. Return／Stop

Incident EvidenceとEntry Recovery Index作成後は、Receipt待ちで停止せずP6-RR-R0-WU-001へ進む。

次の場合だけ再停止する。

- 本Resume Authority Digest不一致。
- Active Handoff Digest不一致。
- Git Mutation、Network、Secret Exposureまたは別の新Incidentが判明した。
- Recovery Index作成前にSource Mutationが既に成立していたことが判明した。
- Active HandoffのTrue Stop Condition。

完了後の最大Claim、Internal Review、Exact Return HandoffおよびIndependent Review待ちはActive Handoffから変更しない。
