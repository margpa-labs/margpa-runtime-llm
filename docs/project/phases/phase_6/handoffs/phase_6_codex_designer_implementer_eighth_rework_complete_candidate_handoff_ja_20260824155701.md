# Phase 6 Eighth Rework — Complete Candidate Handoff

```yaml
document_id: phase_6_codex_designer_implementer_eighth_rework_complete_candidate_handoff_20260824155701
status: complete_candidate
phase: phase_6
rework: eighth_rework_runtime_lifecycle_deadline_and_ui_revision_integrity
from: 設計者兼実装者役
to: プロジェクト責任者兼設計統括者役
created_at: 2026-08-24 15:57:01 JST
phase_closure_claimed: false
```

## 1. Return Status

```text
Eighth Rework Status     : COMPLETE_CANDIDATE
Open Technical Critical : 0 known
Open Technical Major    : 0 known
Controller Re-review    : REQUIRED
```

Seventh Rework Package A〜Gをやり直さず、P6-RW7-CODEX-001〜003だけを差分修正した。

## 2. Implemented Contract

### RW8-A — Lifecycle / Cancel / Shutdown

- Main GenerationとSame-Turn Token計測完了後はModel Main Leaseだけを解放する。
- Service Active Request CorrelationはJudge／Repair／Terminal確定後のSession `finally`まで保持する。
- Session所有Cancellation TokenをJudge／Repairへ渡し、User Stop／Shutdownの双方を同期実行へ接続する。
- User Cancelが勝った場合、`cancelled` exactly once／`completed` 0へ収束する。
- ShutdownはSession Cancel／Wait後、残りBudgetでCoordinator Cancel／Joinを行う。
- SessionがTimeoutした場合はFalse Cleanを禁止し、Coordinator shutdown／Adapter unloadへ進まない。

### RW8-B — Bounded ENFORCE Wait / Late Ownership

- Judge 30秒Wall-clock Budgetを実行中Deadlineとして強制する。
- Deadline後はCancellationを発火し、有界Grace後にRaw Candidate 0のSafe Fallbackへ収束する。
- CallerをSynchronous ENFORCEの単一Terminal Ownerとし、WorkerはResult計算だけを担当する。
- Run Generation TokenでLate WorkerのState／Last-result／Judge Evidence Recording書込を無効化する。
- Presented Final／Response／PersistenceはCallerの確定後にLate Workerから変更できない。
- Synchronous ENFORCE中のRepairはCanonical source Turnへの採用だけとし、Late derived TurnのPersistenceを行わない。
- Workerは`ModelAccessCoordinator`所有／tracked Threadのままで、Detached Threadに戻していない。

### RW8-C — Atomic Runtime Model Projection

- Accepted Runtime Model RevisionをSynchronous Refで一元管理する。
- Revisionが採用された場合だけ、Main Statusと`settingsForm.maxNewTokens`を同一Snapshotから更新する。
- Revision 8採用後の遅延Revision 7 Mutation Responseを、Status／入力／実Chat送信設定の全てで棄却するRegressionを追加した。

## 3. Regression Evidence

```text
slow ENFORCE active_request_id maintained     : PASS
slow ENFORCE service.cancel(request_id)       : PASS
Cancelled Terminal exactly once / Completed 0: PASS
shutdown during Judge cancel / join           : PASS
shutdown timeout false-clean / safe retry     : PASS
Judge Deadline bounded / raw candidate 0      : PASS
Late Worker Last-result mutation 0            : PASS
Late Worker Judge Evidence mutation 0         : PASS
normal ACCEPT                                 : PASS
accepted Repair Presented Final               : PASS
malformed output Safe Fallback                 : PASS
OFF Model Call 0                              : PASS
OBSERVE candidate unchanged                   : PASS
stale Runtime Status atomic rejection         : PASS
```

## 4. Final Validation

```text
Focused Backend             : 57 passed
Frontend Typecheck          : PASS
Frontend Lint               : PASS
Frontend Test               : 24 files / 221 passed
Frontend Production Build   : PASS / 48 modules transformed
Canonical Mypy              : 443 source files / 0 issues
Ruff Format Check           : 443 files already formatted
Ruff Check                  : PASS
Backend Full                : 1593 passed / 7 deselected
```

Backend Full初回の1 FailureはRW8-AのShutdown Timeout差分であり、最小修正後の
Focused／Static／Backend Full再実行でClosure済み。

## 5. Exact Artifact Digests

```text
8393a3d4afcd9cdda163b8b283fcab27e9997375d7c8a7e85fafd601121ff70d2c3a166d448a1732aae1e555d8d129c05ef242fcac73857533c6854d9da47baf  src/margpa_runtime_llm/modules/conversation/application/conversation_generation.py
1d8a897e166122f9d26f36f93fb2890580e3dc5d98ab58ffeb302749e147dce8b9b32c4b521a1f490328b6a17536b15fea56225489b1396070d8afee3c4717af  src/margpa_runtime_llm/bootstrap/judge_live_integration.py
6e51313f3a6590b3b73802af64b536e2a9ce4a1c659ed0ad5d12953a1af7c58b0dea5d0bd11319f2fa6c20ec89e94e87687433f097255eebee5b2d7cffcdaa60  src/margpa_runtime_llm/modules/inference/application/model_access_coordinator.py
53fef7fa620f12497276aed8a85ea2e7076a6f8801ee506d52529e8e36e15156936863c3c09e5c517e047678a7d4dbad6c29965691d8fb6553fcddd19c1125ac  src/margpa_runtime_llm/modules/inference/domain/cancellation.py
29867a019aa4f1709be1c389cd8a343f5a79cb99fc7ac5674b61bf51c63e59f7e79c43626a7b862746a2feac3d4241416e7a06723493fe3e442b700aa5325c61  frontend/src/App.tsx
b6f2640040ea7fffead1547c6e85de18dd43eb848ae76b2bc3bf5bfaad12037da7b97f998179fd4f1abc2cb68df326e4c6b947e6a0c6a69cbd81b6bd0be8726e  frontend/src/App.test.tsx
77085cc0c3f6d1244022fce2f9999b5857917dac2db2b156e9a2a580ad0a7d1c33210bc6ce533d1d0f07573ca8b34a2ce65e82a26074d25c429b41061d435cec  tests/unit/conversation/test_conversation_generation_judge_hook.py
bd14fd876bf26872b53517369e11bf4725ce9787b2ae9bd8e365ea7024c37857c362f05bb480409a3ceaa288ccdcbaab92019619afcd9a0bee9fb4c68e587171  tests/unit/bootstrap/test_judge_live_integration.py
c5cd59aa933d11637aa80d1886764a41bce0aebf4d604d4981b4fbf0c19aac0463ba28a774ff7e89aaf3959dbe930d8b82cca77b278214ad65df1175ac6f0d5e  tests/unit/inference/test_model_access_coordinator.py
0164475a2143041d53cebf2d43b61f9ccf9ab1bdf9c1b49a9efe5cee8176caaa2b5b9bee34116d7a782ddc71df451f825059dabb44bfeeef744aaf8a43b759bb  src/margpa_runtime_llm/web/static/index.html
1487a8f4b8ae9f24b7de3ff1b7ef6e0b3db0974b20ff538f23522e70709e913944dcf675a6173fcbb273f34e6f191dfb6767a26881efc899f6edabca8eb0e597  src/margpa_runtime_llm/web/static/app.css
92a2a0a7c2c3d014e4169fcc11eafbafa91971e34eb2c83cdeda98ef4586619732813904f412f46b02e7226989a4e7bcafebcd751122f686b4bc5c9291428e9c  src/margpa_runtime_llm/web/static/app.js
```

## 6. Process Incident and Boundary

```text
P6-RW8-INC-001                              : RECORDED / STOPPED_SAFE / RECOVERED / NON-BLOCKING
Eighth Resume Cycle Root-outside Action     : 0
Eighth Rework Root-outside Incident         : 1
Phase 6 cumulative known incidents          : 2
Provider Memory Internal Contact            : 0
User runtime_data Contact                   : 0
Git / Network / Model Artifact Mutation     : 0
Phase 6 Closure / Phase 7 / Roadmap / Backup: 0
```

Task-owned Temporary Root:

```text
/Users/Nazuna Research/Documents/pseudo_root/99_ps_Main_Creating_Objects専用_20260219/MARGPA-RUNTIME-LLM/margpa-runtime-llm/.venv/.t/phase_6_eighth_rework_resume_20260824154451/
```

`P6-RW7-INC-001`／`P6-RW8-INC-001`の履歴は保持し、Incident 0とは主張しない。

## 7. Open Boundary / Next Action

```text
Real Model / Metal Validation   : NOT EXECUTED
User Browser Acceptance         : NOT EXECUTED
Phase 6 Closure                 : NOT CLAIMED
Next Action                     : Controller Independent Re-review
Stop Condition                  : Controller decision required before any further work
```
