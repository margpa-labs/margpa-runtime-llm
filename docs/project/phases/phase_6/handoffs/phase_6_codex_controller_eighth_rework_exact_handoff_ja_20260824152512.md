# Phase 6 Eighth Rework — Codex Controller Exact Handoff

```text
From: プロジェクト責任者兼設計統括者役
To: 設計者兼実装者役
Status: AUTHORIZED_FOR_EXACT_REWORK
Source Review: phase_6_gov012_seventh_rework_controller_independent_review_ja_20260824152512.md
Phase 6 Closure: FORBIDDEN
```

Timestamp: 2026-08-24 15:25:12 JST

## 1. Objective

Seventh Reworkの成立範囲を保持したまま、P6-RW7-CODEX-001〜003だけを差分修正し、
Controller Independent Re-reviewへCOMPLETE_CANDIDATEを返す。

## 2. Mandatory Reading

1. `docs/project/phases/phase_6/history/operations/phase_6_gov012_seventh_rework_controller_independent_review_ja_20260824152512.md`
2. `docs/project/phases/phase_6/handoffs/phase_6_codex_designer_implementer_seventh_rework_complete_candidate_handoff_ja_20260824151646.md`
3. `docs/project/phases/phase_6/history/index/phase_6_seventh_rework_package_e_semantic_enforcement_complete_ja_20260824145630.md`
4. `docs/project/phases/phase_6/history/index/phase_6_seventh_rework_package_g_integrated_verification_complete_ja_20260824151646.md`

## 3. Exact Required Rework

### RW8-A — Lifecycle／Cancel／Shutdown

- Model Main Lease解放とService Active Request解放を分離する。
- Main Modelの生成・Token計測完了後はModel Leaseのみ解放し、Session Active Correlationは
  Judge／Repair／Terminal確定まで保持する。
- User Stopを同期Judge／RepairのCancellationへ接続する。
- CancelがTerminal競争に勝った場合は`cancelled` exactly onceとし、Safe Fallback
  `completed`へ変換しない。
- Shutdownは同期Judge／Repair中のSessionをActiveとして認識し、Cancel／Joinする。

### RW8-B — Bounded ENFORCE Wait

- Judge Wall-clock Budgetを実行中Deadlineとして強制する。
- Timeout時はCancellationを発火し、Raw Candidateを公開せずSafe Fallbackへ収束する。
- Cancel／Timeout／Shutdownの競争をDeterministicにする。
- WorkerのLate ResultはPresented Final、Persistence、Terminal、Last-result Projectionを
  後から上書きしない。必要ならRun Generation／Terminal Ownership Tokenを導入する。
- ThreadをDetached／Untrackedへ戻さない。

### RW8-C — Runtime Status Atomic Projection

- `acceptRuntimeModelStatus()`でRevision採用が成立した場合だけ、Statusと
  `settingsForm.maxNewTokens`を同じCanonical Snapshotから更新する。
- 古いPolling Responseが新Revisionの入力欄を巻き戻さないRegressionを追加する。

## 4. Minimum Authorized Paths

必要な範囲だけ使用する。主対象:

```text
src/margpa_runtime_llm/modules/conversation/application/conversation_generation.py
src/margpa_runtime_llm/bootstrap/judge_live_integration.py
src/margpa_runtime_llm/modules/inference/application/model_access_coordinator.py
frontend/src/App.tsx
tests/unit/conversation/test_conversation_generation_judge_hook.py
tests/unit/bootstrap/test_judge_live_integration.py
tests/unit/inference/test_model_access_coordinator.py
frontend/src/App.test.tsx
docs/project/phases/phase_6/history/index/phase_6_eighth_rework_<timestamp>.md
docs/project/phases/phase_6/handoffs/phase_6_codex_designer_implementer_eighth_rework_complete_candidate_handoff_<timestamp>.md
```

隣接Production Pathが本当に必要なら、目的をEvidenceへ記録して最小拡張してよい。
Package A〜G全体のやり直しは禁止。

## 5. Required Regression

```text
- slow ENFORCE Judge中 active_request_id == request_id
- slow ENFORCE Judge中 service.cancel(request_id) == true
- Cancelled Terminal exactly once / Completed 0
- shutdown during Judge returns only after cancel/join, false clean 0
- Judge Deadline exceeded -> bounded return / raw candidate 0 / safe fallback
- Late worker -> canonical mutation 0
- normal ACCEPT / Repair accepted / malformed safe fallback regression
- OFF call 0 / OBSERVE raw unchanged
- stale Runtime Status response -> status and max token input both unchanged
```

## 6. Validation

Rework Focusedを先に実行し、最終状態で次を実行する。

```text
.venv/bin/python -m pytest -q -p no:cacheprovider --basetemp=<Project内Task Temp> <focused paths>
.venv/bin/python -m mypy
.venv/bin/python -m ruff format --check
.venv/bin/python -m ruff check
.venv/bin/python -m pytest tests/ -q -p no:cacheprovider --basetemp=<Project内Task Temp>
```

FrontendはExact `<Root>/frontend` workdir、Project内Task-owned `NPM_CONFIG_CACHE`／`TMPDIR`で、
Typecheck／Lint／Test／Buildを行う。Project Rootでnpmを実行しない。

## 7. Boundary

- Authorized Root外Action 0。
- `.claude`／`.codex`／Provider Memory内部接触0。
- User `runtime_data`接触0。
- Network／Git／Model Artifact Mutation 0。
- Phase 6 Closure／Phase 7／Roadmapへ進まない。
- `P6-RW7-INC-001`はHistorical Nonconformanceのまま保持する。
- 真のStop Condition以外でUser確認へ返さない。

## 8. Return Contract

新規Recovery EntryとComplete Candidate HandoffをAppend-onlyで作り、このController Taskへ直接返す。
Critical／Major 0を独力でClosureへ変換せず、Controller Independent Re-reviewで停止する。
