# Phase 6 GOV-013 — Eighth Rework Controller Independent Review

```yaml
document_id: phase_6_gov013_eighth_rework_controller_independent_review_20260824160222
status: adjust_rework_required
phase: phase_6
reviewer: プロジェクト責任者兼設計統括者役
review_target: phase_6_eighth_rework_complete_candidate
created_at: 2026-08-24 16:02:22 JST
closure_recommendation: do_not_close
```

## 1. Review Result

```text
Result                  : ADJUST
Eighth Complete Candidate: NOT ACCEPTED
Open Critical           : 0
Open Major              : 1
Phase 6 Closure         : STOP
```

Eighth Reworkは、前回3 Findingの主要経路、Frontend Revision競合、Shutdown Timeout退行を修正し、
Canonical Test／Staticを通過した。ただし独立Adversarial Testにより、期限切れTerminal確定後にLate
WorkerがJudge Evidenceを書込めるTOCTOUを再現した。Complete Candidateの「Late Worker Judge Evidence
mutation 0」主張は、通常Timing Testでは成立するが、競合境界では成立しない。

## 2. Verified Improvements

- Main Model LeaseとService Active Correlationの分離。
- Judge中のUser StopがCancellationへ到達し、Active RequestをTerminalまで維持。
- Session停止Timeout時、Coordinator shutdown／Adapter unloadへ進まず`False`を返す。
- 同期ENFORCEのWall-clock Deadline／Bounded Grace。
- Run GenerationによるLast-result ProjectionのLate overwrite防止。
- Runtime StatusとMax New TokensのRevision単位Projection。
- Controller Focused Backend `76 passed`。
- Controller Frontend App Test `29 passed`。

## 3. Major Finding — P6-RW8-CODEX-001

### 3.1 Finding

`_run_judge_and_repair()`はJudge Evidence書込み前に次を確認する。

```python
if composition.owns_run(run_generation=run_generation):
    _record_evidence(...)
```

しかしOwnership確認とRecorderの実書込みは同一Atomic Operationではない。次の順序が成立する。

```text
Worker : owns_run == true
Worker : Judge Evidence Recorderへ入るが、実書込み前に停止
Caller : Deadline到達
Caller : deadline_exceededをTerminal／Last-resultとして確定
Caller : Safe Fallbackを返す
Worker : Recorder再開
Worker : Terminal確定後にJudge Evidenceを書込む
```

これにより、CallerがTerminal Ownershipを取得した後も、失効したWorkerがAudit／Recording Stateを変更する。
Presented FinalやLast-result自体は変わらないが、Complete Candidate §2／§3の「Late Worker Judge Evidence
Recording書込不可」と一致しない。

### 3.2 Reproduction

Controller-owned Project内Temporary Test:

```text
.venv/.t/phase_6_eighth_controller_review_20260824160300/test_late_evidence_race.py
```

条件:

1. Fake JudgeはDeadline前に正常Resultを返す。
2. Fake Evidence Recorderは呼出し直後、Commit前にGate待機する。
3. CallerはRecorder待機中にDeadlineへ到達してSafe Fallbackを返す。
4. その後Recorder Gateを解放する。

結果:

```text
1 failed
AssertionError: late worker committed Judge Evidence after terminal ownership loss
```

`evidence_calls`はTerminal直後`0`だが、Late Worker終了後`1`となる。

## 4. Required Correction

1. 同期ENFORCE Workerは、失効後に外部Recorderへ直接書込める構造を持たないこと。
2. `owns_run()`のCheck-then-ActだけでEvidence Mutationを保護しないこと。
3. Judge／Repair計算結果とEvidence Payloadを、Worker内のMemory上のPending Resultとして分離すること。
4. Evidence Publishを行う場合は、Caller-owned Terminal Arbitrationと整合する一つのPublish境界に集約すること。
5. Deadline／CancelでCallerが勝った場合、Workerが既にRecorder入口へ到達していても、実Evidence Commit 0であること。
6. OBSERVE Backgroundの既存Evidence記録、正常ENFORCEのEvidence記録、Recording OFF Call 0を退行させないこと。
7. Presented Final、Conversation Persistence、Repair Derived Turn、Last-resultの既存非上書き境界を維持すること。

Recorderを遅くしてTestを通す、Deadlineを伸ばす、Recorder Timeoutを仮定する、競合確率を理由に除外することは
Correctionではない。

## 5. Required Regression

- RecorderがCommit直前でBlockした状態でDeadlineが勝つ。
- Hookは有界時間内にSafe Fallbackを返す。
- Recorder Gate解放後もEvidence Call／Commit 0。
- Last-resultは`deadline_exceeded`のまま。
- Background Coordinatorは最終的に解放される。
- 正常ENFORCE完了時はEvidence exactly once。
- OBSERVE完了時はEvidence exactly once。
- Recording OFFはEvidence Call 0。
- Cancel勝利時もLate Evidence Call／Commit 0。

## 6. Evidence Classification

```text
P6-RW8-INC-001       : RECORDED／RECOVERED／NON-BLOCKING
P6-RW8-CODEX-001     : OPEN／MAJOR／CURRENT_REWORK_BLOCKER
Real Model／Metal    : USER GATE、再活性化しない
User Browser         : Ninth Rework後のAcceptance Gate
Phase 6 Closure      : NOT READY
```
