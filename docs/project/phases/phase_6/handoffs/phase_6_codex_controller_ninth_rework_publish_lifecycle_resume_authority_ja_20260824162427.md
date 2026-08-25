# Phase 6 Ninth Rework — Publish Lifecycle差分再開Authority

```yaml
document_id: phase_6_codex_controller_ninth_rework_publish_lifecycle_resume_authority_20260824162427
status: exact_resume_authority_active
phase: phase_6
from: プロジェクト責任者兼設計統括者役
to: 設計者兼実装者役
created_at: 2026-08-24 16:24:27 JST
resume_from: ninth_rework_current_implementation
phase_closure_authority: false
git_read_authority: false
git_mutation_authority: false
```

## 1. Incident Decision

`P6-RW9-INC-001`を次のとおり受理する。

```text
Unauthorized Git Read : 1
Git Mutation          : 0
Product Impact        : 0
Root-outside Action   : 0
Disposition           : RECORDED／STOPPED_SAFE／NON-BLOCKING FOR RESUME
```

read-only `git diff`でありProduct／Index／RefへのMutationはない。Incidentを0へ戻さず、Gitを使った
Rollback／Cleanup／追加Inspectionも行わない。Ninthの現行Source／Test実装と次のValidation Evidenceを保持する。

```text
Focused Backend : 61 passed
Mypy            : 443 files／0 errors
Ruff            : PASS
Backend Full    : 1598 passed／7 deselected
```

## 2. Cumulative Incident Accounting

```text
P6-RW7-INC-001 : Root-outside npm Log Attempt
P6-RW8-INC-001 : Root-outside pytest Temporary Write
P6-RW9-INC-001 : Unauthorized Git Read
Phase 6 cumulative known Process Incidents     : 3
Phase 6 cumulative known Root-outside Incidents: 2
Ninth cumulative unauthorized Git Read         : 1
```

`Incident 0`、`Git Action 0`、`全Process準拠`の主張は禁止する。

## 3. Exact Resume Scope

Ninth Reworkの現行Pending Evidence／Terminal Arbitration実装を保持し、次の3点だけを照合・必要最小修正する。

1. Replacement FinalへのGovernance／Guardrail Post Hook等によりTerminal OwnerのPublish判断が0.25秒を超えても、
   正常Completed ENFORCE Evidenceが黙って消失しないこと。
2. Terminal承認後にRecorderがBlockしても、ModelAccessCoordinatorのBackground Model Leaseを保持せず、
   次のMain Turnを`INTERNAL_TASK_PREEMPTION_FAILED`へ落とさないこと。
3. Evidence Publish Workerを導入・使用する場合、Detached／Untracked Workerにせず、Shutdown clean／Failure Evidence／
   exactly-onceを検証できる所有境界を持つこと。

単にArbitration Timeoutを延長・無期限化する、Recorderは常に速いと仮定する、Main wait timeoutを延長する、
Evidence欠落をBest-effort扱いへ変更することは禁止する。

## 4. Required Contract

- Judge／Repair Model WorkerはMemory-only Pending Evidenceを返し、外部Recorderへ直接Commitしない。
- Deadline／Cancel／Final Rejectionが勝ったPending Evidenceは永久破棄し、Commit 0。
- 正常ENFORCE CompletedはEvidence exactly once。
- OBSERVEはEvidence exactly once、Recording OFFはRecorder Call 0。
- Evidence Recorderの遅延／FailureはPresented Final、Conversation Terminal、Model Access Leaseを壊さない。
- Evidence Publicationの所有者とLifecycleは明示的にtrackedで、Runtime Shutdown時に安全にCancel／Drain／Joinまたは
  明示的Failureへ収束する。
- 新しいMain TurnはJudge Model Call終了後、Evidence Writerの遅延から独立してModel Accessを取得できる。
- Eighthで閉じたActive Request、Stop、Deadline、Late Last-result、UI Revisionを退行させない。

## 5. Mandatory Adversarial Regression

1. Terminal Publish判断を0.25秒超遅延させても、正常ENFORCE Evidence exactly once。
2. RecorderをCommit入口でBlockした状態でも、次のMain Model lease取得がEvidence待ちにならない。
3. Recorder Block中のShutdownがfalse-cleanを返さず、規定Lifecycleへ収束する。
4. Deadline勝利後にJudge Worker／Evidence Workerを解放してもEvidence 0。
5. Cancel勝利後に全Workerを解放してもEvidence 0。
6. Normal ENFORCE／OBSERVE exactly once、Recording OFF 0。
7. Existing Focused Lifecycle／Coordinator Regression全PASS。

## 6. Execution Boundary

Project内Task-owned Tempを作成し、全pytestへExact`--basetemp`を付ける。Git Commandはread-onlyを含めて一切
実行しない。差分確認は`rg`、`sed`、`shasum`、対象Fileの直接読取で行う。

実行順:

1. Current implementationのDirect Read Review。
2. 上記3点の最小Correction。
3. Adversarial Focused。
4. Canonical Mypy／Ruff。
5. Backend Full。
6. Boundary Review（Gitを使わない）。
7. Append-only Recovery／Complete CandidateをControllerへ直接返送。

Frontend変更がない限り、Eighth Frontend PASS EvidenceをReuseする。

## 7. Forbidden

- Git全操作・全参照。
- Network、Model Artifact、User`runtime_data`、Provider Memory、Root外Temporary。
- UI／RAG／Guardrail／Runtime Modelの隣接変更。
- Phase 6 Closure、Phase 7、Roadmap、Backup。

真のStop Condition以外では停止せず、Ninth Rework Complete CandidateでControllerへ返す。
