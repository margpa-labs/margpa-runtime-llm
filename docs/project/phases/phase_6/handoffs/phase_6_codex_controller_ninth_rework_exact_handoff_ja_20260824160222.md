# Phase 6 Ninth Rework — Exact Handoff

```yaml
document_id: phase_6_codex_controller_ninth_rework_exact_handoff_20260824160222
status: exact_rework_authority_active
phase: phase_6
from: プロジェクト責任者兼設計統括者役
to: 設計者兼実装者役
created_at: 2026-08-24 16:02:22 JST
scope: late_judge_evidence_publish_ownership_only
phase_closure_authority: false
git_mutation_authority: false
```

## 1. Objective

Eighth Reworkの実装と検証を保持し、`P6-RW8-CODEX-001`だけを差分修正する。

```text
Objective:
  Deadline／Cancel Terminal確定後に、失効した同期ENFORCE Workerが
  Judge EvidenceをCommitできるTOCTOUを除去する。
```

## 2. Mandatory Reading

1. `docs/project/phases/phase_6/history/operations/phase_6_gov013_eighth_rework_controller_independent_review_ja_20260824160222.md`
2. 本Handoff。
3. `docs/project/phases/phase_6/handoffs/phase_6_codex_designer_implementer_eighth_rework_complete_candidate_handoff_ja_20260824155701.md`
4. `docs/project/phases/phase_6/handoffs/phase_6_codex_controller_eighth_rework_exact_handoff_ja_20260824152512.md`のLate Worker Ownership契約。

## 3. Exact Scope

Allowed:

- `src/margpa_runtime_llm/bootstrap/judge_live_integration.py`
- Judge Evidence Publish ownershipに直接必要な既存Port／typed private helperの最小変更。
- `tests/unit/bootstrap/test_judge_live_integration.py`
- 直接影響するFocused Testの最小追随。
- Phase 6 Append-only Recovery／Return Handoff。

Forbidden:

- Seventh Package A〜G／Eighth RW8-A〜Cの全面再実装。
- UI、Runtime Model、Context、Max New Tokens、Real Model、RAG、Guardrailの新規変更。
- Phase 6 Closure、Phase 7、Roadmap、Backup、Git、Network。
- User`runtime_data`、Provider Memory、Model Artifact、Root外Temporary。

## 4. Required Implementation Contract

1. 同期ENFORCE Worker内の外部Evidence Writer直接Commitを禁止する。
2. Workerは必要なEvidence内容をMemory上のTyped Pending Payloadとして返せるが、Publish Authorityを持たない。
3. Caller-owned ArbitrationがWorker Resultを期限内に採用した場合だけ、正規Evidence Publish経路へ進める。
4. Deadline／Cancel／Caller Failureが勝った場合、Pending Evidenceは破棄し、Late Worker終了後もCommit 0。
5. Publish処理自身がCallerの有界Terminalを無期限に保持しない設計にする。既存RecorderのAtomic／Failure契約を確認し、
   必要なら「Evidence unavailable」と「Presented Final」を分離する。
6. OBSERVE Backgroundは既存どおりEvidenceを記録する。
7. 正常ENFORCEはEvidence exactly once、Recording OFFはCall 0。
8. Repair前／後、Judge失敗、Malformed Output、Model Error、Cancellationの全Evidence分類を失わない。
9. Last-result、Response、Conversation Persistence、Repair PersistenceのEighth非上書き契約を維持する。

実装方法は上記Contractを満たす範囲で設計者兼実装者役が確定する。単純な`owns_run()`再確認追加だけでは
同じCheck-then-Act競合が残るため不可。

## 5. Mandatory Regression

Controller Reproductionを正式Regressionへ移す。

```text
Fake Judge        : Deadline前にResultを返す
Fake Recorder     : Commit直前でBlock
Caller            : Deadline Terminalを確定して有界Return
Recorder Gate     : Return後に解放
Expected Evidence : 0
Expected Result   : deadline_exceeded不変
```

追加:

- User CancelがRecorder競合中に勝つ → Cancelled exactly once／Evidence 0。
- 正常ENFORCE → Evidence exactly once。
- OBSERVE → Evidence exactly once。
- Recording OFF → Recorder Call 0。
- Coordinator解放／Shutdown cleanの既存Regression PASS。

## 6. Exact Validation Boundary

最初にProject内Task-owned Tempを作る。

```text
<Authorized Root>/.venv/.t/phase_6_ninth_rework_<timestamp>/
```

全pytestへExact `--basetemp=<Task Temp>/pytest`を付ける。Frontend変更がない限りFrontend Full再実行は
不要で、Eighth PASS EvidenceをReuseする。実行順:

1. Focused Judge／Conversation／Coordinator Tests。
2. Canonical Mypy。
3. Ruff Format Check／Ruff Check。
4. Backend Full。
5. Boundary Review。
6. Append-only Recovery／Complete CandidateをControllerへ直接返送。

## 7. Incident Accounting

```text
P6-RW7-INC-001 : Historical、保持
P6-RW8-INC-001 : Historical、保持
Phase 6 cumulative known Root-outside Incidents: 2
```

Incident 0／全Process準拠へ書き換えない。新Cycleの実測を別に記録する。

## 8. Stop and Return

真のStop Condition以外では人間確認・進捗報告を理由に停止しない。Rework完了後は次を返す。

- Exact changed files／Digest。
- Adversarial Evidence競合Regression。
- Focused／Mypy／Ruff／Backend Full。
- Root／Provider Memory／User Data／Git／Network／Model Artifact境界。
- Open Critical／Major。

Phase 6 Closureへ進まず、Controller Independent Re-reviewで停止する。
