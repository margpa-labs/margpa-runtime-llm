# Phase 9-2 — Evidence Oracle / Claim Truthfulness R5 Exact Handoff

```yaml
document_id: phase_9_controller_phase_9_2_evidence_oracle_and_claim_truthfulness_r5_exact_handoff_20260907132840
document_type: exact_rework_handoff
document_state: ready
phase: phase_9
program: phase_9_2
recorded_at: 2026-09-07 13:28:40 JST
language: ja
from: codex_controller
to: claude_designer_implementer
authority_owner: Nazuna Research
decision_authority: user
in_response_to: phase_9_claude_phase_9_2_provider_identity_atomic_lease_and_top_level_real_gate_r4_exact_return_ja_20260907131851.md
controller_review: phase_9_2_controller_r4_return_independent_review_and_r5_micro_rework_decision_ja_20260907132840.md
maximum_claim: P9_2_R5_USER_MANUAL_CANDIDATE_FOR_CODEX_CONTROLLER_REVIEW
phase_9_2_closure_authorized: false
phase_9_3_authorized: false
phase_10_authorized: false
git_write_authorized: false
network_authorized: false
append_only: true
```

## 1. Objective

R4の有効な実装を保持し、最上位Claimを支えるTest Oracleと記録だけを局所的に完結させる。

```text
Restart Readの全対象Hard Assert
-> Scenario 2／3のFalse PASS除去
-> Expected／Actual Identity Claimの正確化
-> Shutdown後Cleanup証明
-> 最小限の実Model再確認
```

## 2. Non-negotiable Boundary

- R4のProvider Selector照合、Atomic Lease、Queue Cleanup、Top-level経路をRollbackしない。
- Phase 9-1のJudge／Guard／Repair／Governance実装は変更しない。
- Selene、DeepSeek Judge、Gemma Schema／Sampling／Retry／Budgetは変更しない。
- Guardの実Request相関をこのRoundで新設計しない。未観測は`unavailable_correlation`のまま保持する。
- 新しいUI機能を追加しない。
- Git Write、Stash、Commit、Push、Reset、Cleanを行わない。
- 既存Return・Handoff・Recoveryを上書きしない。ReturnとRecoveryは新規Pathで作成する。

## 3. R5-WU-01 — Restart Read Oracle完結

`tests/integration/test_real_top_level_experiment_production_gate_smoke.py` のRestart Read Helperを次のHard Assertで完結させる。

1. Fresh `LocalFilesystemExperimentStore`からPlanを読める。
2. 対象VariantのDesired Configurationを`load_variant_desired_configuration()`で読める。
3. Desired DigestがPlanの対応Variant Configuration Digestと一致する。
4. RunとFrozen Configurationを読める。
5. Frozenの`correlation` BlockがRun／Experiment／Variant／Case Digest／Plan Digestと一致する。
6. Frozenの`provider_identity` Blockを「存在する」だけでなく対象ScenarioのConfigured／Active／Expectedと照合する。
7. Raw EvidenceとMetricを読める。
8. Comparisonが`None`でなく、対象RunのRow、Metric、Evaluation Observationを含む。
9. 対象RunのIdentityがPlan／Comparison／Raw Evidence間で一致する。

EvaluationがComparison Row内に保存される現行契約なら、別の架空Store APIは作らず、Row内Observationを直接Assertする。

## 4. R5-WU-02 — Top-level実Model Scenario Oracle強化

### 4.1 Scenario 2

- `state == "completed"`をHard Assertする。`failed`をPASS対象にしない。
- Main `called is True`、Judge `called is True`をAssertする。
- JudgeのConfigured／Active／ExpectedがGemma、MainのActive／ExpectedがQwenであることをFrozen SnapshotでAssertする。
- Judge AcceptによりRepairが非発火である場合は、その実測のまま受理する。Repair発火を強制するために入力を歪めない。

### 4.2 Scenario 3

- `state == "completed"`をHard Assertする。`failed`をPASS対象にしない。
- Main `called is True`をAssertする。
- GuardのConfigured／Active／ExpectedがQwen3GuardであることをFrozen SnapshotでAssertする。
- Request-local Guard Evidenceがない現行契約では、Guard `called is None` / `outcome == "unavailable_correlation"`を正直にAssertする。これを「Guard Actual Dispatch証明」と言い換えない。

### 4.3 False-success回帰

Fixture／FakeでScenario 2／3が`failed`の場合、強化したOracleが必ず検出することを確認する。ProductionのTestに再び`completed | failed`の無条件受理を入れない。

## 5. R5-WU-03 — Identity Claimの正確化

1. `expected_executed_selector_id`はExpectedでありActual Executedではない。
2. `ActorInvocationRecord.called=True`はCallの証拠でありProvider Identityの証拠ではない。
3. Actual Executed Providerを取得できる既存request-correlated Evidenceがある経路だけActualと記載する。
4. GuardのActual Dispatchは今RoundではUnavailableと記録する。
5. Actual Identity取得のための新しいPhase 9-1相関機構は作らない。

R4 Returnは上書きせず、R5 ReturnでR4の過大Claimを明示訂正する。誤解を生むSource Comment／Test Docstringがある場合は、必要最小限だけ訂正する。

## 6. R5-WU-04 — Queue Cancel後Shutdownの機械証明

1. Run AがWorkerを占有中、Run BをQueueする。
2. Run BをQueue中にCancelし、Future Cancel成功経路を通す。
3. Run Aを解放し、WorkerをShutdownする。
4. Shutdown後にRun BのActor Call 0、Terminal State、`request_cancel(run_b)==False`をAssertする。
5. Deadline経路にも同じ残留がないことを、既存Testまたは最小の追加Assertで確認する。

新TestがProduction Defectを検出しない限り`run_worker.py`は変更しない。検出した場合のみ、そのLifecycle境界に限定して修正する。

## 7. Verification Order

1. Restart Read／Provider Identity Focused Test。
2. Scenario OracleのFake／Fixture Test。
3. Queue Cancel／Deadline／Shutdown Test。
4. Experiment Web Integration。
5. Backend Non-model Full Suite。
6. Ruff／Canonical Mypy Baseline差分。
7. `memory_pressure`によるResource Preflight。
8. 条件成立時のみ実Model Scenario 2と3を各1回、逐次実行する（最大2 Run、Retryなし）。Scenario 1は本Roundで再実行不要。
9. Internal Review A／B。

実Model Scenarioが不成立な場合は、Test Oracleを弱めずPartial Returnとする。同じ実Model Testの反復、Seed変更、Retry、入力差し替えは行わない。

## 8. Operational Correction

R4の`git stash` / `git stash pop`はGit Writeであり、禁止違反だったと正確に記録する。「Git Writeは一切実行していない」と併記しない。現時点のStashが空であること、Controller側で現時点のデータ損失を確認していないことは分けて記録する。

R5ではGit Read-only以外を行わない。Baseline比較やSabotage復元にStashを使わず、局所Backupまたは明示的なバイト保存・復元を使う。

## 9. Return Contract

Returnには次を含める。

- WU-01〜04の個別状態。
- Restart Readで実際に読んだ対象とHard Assert。
- Scenario 2／3の実Model回数、Terminal State、Invocation Evidence、Frozen Provider Identity。
- ExpectedとActual Executedを分けたIdentity Matrix。
- Queue Cancel／Deadline／Shutdownの結果。
- 検証数値、Resource Preflight、Process／Port／Model残留。
- R4過大ClaimとGit操作記録の訂正。
- Open Findings。

ReturnとRecoveryはAppend-onlyの新規Pathで作成する。Phase Index、Registry、Stable Docsは変更しない。

## 10. Stop Condition

`P9_2_R5_USER_MANUAL_CANDIDATE_FOR_CODEX_CONTROLLER_REVIEW`を主張できるのは、WU-01〜04と実Model Scenario 2／3のHard Assertが成立した場合だけである。未成立がある場合はPartialとし、Oracleを弱めない。

Phase 9-2 Complete／Phase 9-3開始／Phase 9 Closureは自己承認せず、Codex Controller Independent Review待ちで停止する。

