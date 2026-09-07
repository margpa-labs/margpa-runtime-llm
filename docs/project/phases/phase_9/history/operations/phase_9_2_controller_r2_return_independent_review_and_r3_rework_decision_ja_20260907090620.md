# Phase 9-2 R2 Return — Codex Controller Independent Review / R3 Rework Decision

```yaml
document_id: phase_9_2_controller_r2_return_independent_review_and_r3_rework_decision_20260907090620
document_type: controller_independent_review
document_state: completed
phase: phase_9
program: phase_9_2
recorded_at: 2026-09-07 09:06:20 JST
language: ja
authority_owner: Nazuna Research
reviewer: codex_controller
decision: changes_required
phase_9_2_complete: false
phase_9_3_authorized: false
git_write_authorized: false
append_only: true
```

## 1. Review対象

- Return: `phase_9_claude_phase_9_2_experiment_truthful_variant_execution_and_evidence_r2_exact_return_ja_20260907084839.md`
- Return SHA-512: `55e9189ecf6f4b928bde733605922eab1ec20b46b98c22a5c361a969114ea62d4c0fcc7e76e77df9547b3fcf0ca125490a6d9263909a5cac1175ae74eee7eb84`
- Recovery: `phase_9_2_experiment_truthful_variant_execution_and_evidence_r2_recovery_ja_20260907084839.md`
- Recovery SHA-512: `5d6879b58f198a7e2457db9b9648a77f2910db9bc9ca01e072f667a1b13757f12cb08d1ebf9f7e4812be4d7c6febd197a0dbc13dab90bd927adc080385b5768d`
- R2 Exact Handoff: `phase_9_controller_phase_9_2_experiment_truthful_variant_execution_and_evidence_r2_exact_handoff_ja_20260907071729.md`
- As-built Source / Test / UI。

Controller focused verification:

```text
224 passed in 1.77s
```

対象は`tests/unit/experiment`、Experiment Production Adapter Unit、Experiment Web Integrationであり、実Modelは再実行していない。

## 2. 結論

```text
CHANGES_REQUIRED
Maximum accepted claim:
P9_2_R2_PARTIAL_FOUNDATION_WITH_DIRECT_REAL_ADAPTER_SMOKES
```

R2は、R1のFalse SuccessとLifecycle欠陥を複数修正している。一方で、Phase 9-2の中心要件である「同一Caseへ異なるProduction Variantを適用して比較する」経路は成立していない。報告された実Model 3/3もTop-level Experiment Runではなく、`LiveProductionTurnAdapter`を直接呼ぶModel Smokeである。

したがって`P9_2_R2_USER_MANUAL_CANDIDATE_FOR_CODEX_CONTROLLER_REVIEW`は受理しない。Phase 9-2 Complete、Phase 9-3開始およびUser Manual開始も未承認とする。

## 3. R2で受理する成果

次はRollbackしない。

1. Case DigestとPlan／Run／Request Identityの分離。
2. `completed => PASS`の無条件Oracle廃止。
3. Judge ResultのProduction Request ID相関。
4. `repair_called`と`repair_adopted`の分離。
5. Comparison Responseと保存Artifactの同一生成経路。
6. Running Runの`execution_mode`保持。
7. Actor呼出し中Deadline Timer、Terminal二重Publish拒否、Restart孤立Run収束。
8. FrontendのComparison stale／unavailable表示。
9. Main／Gemma、Main／Qwen3GuardがDirect Adapter Smokeでは実行可能だった実測。

## 4. Confirmed Findings

### IR-P9-2-R2-01 [CRITICAL] 同一Planで異なるProduction Variantを実行できない

`create_plan()`はPlan作成時のLive Snapshotを一度だけ読み、その同一Digestを選択した全Variantへ複製する。

- `src/margpa_runtime_llm/web/experiment_routes.py:487-505`
- Return自身も「全Variantへ同一Digest」と明記する。

Production Main-only、Judge/Repair、Guardの宣言Modeは相互に異なる。しかしRun開始時は、Live Snapshot全体がPlan作成時Digestと一致し、さらにVariant宣言Slotとも一致することを要求する。

- `src/margpa_runtime_llm/web/experiment_routes.py:591-609`

結果としてPlan作成時のLive設定と一致するVariantしか実行できない。次Variant用にSettingsを変更すると全体Digest不一致でCall 0になる。UIは複数Variant選択と各Run Buttonを提供しているため、見た目は比較可能だが、異なるProduction構成の同一Plan比較は構造上成立しない。

これはP9-REQ-202／P9-ACC-040およびR2 Handoff §4.2の未成立である。

### IR-P9-2-R2-02 [CRITICAL] 実Model GateがTop-level Experiment Runではない

実Model Test自身が、Experiment Routerを通らない別Scriptであると明記している。

- `src/margpa_runtime_llm/web/experiment_routes.py:1-9`
- `tests/integration/test_real_local_experiment_production_variant_gate_smoke.py:1-15`

3 Testはいずれも`LiveProductionTurnAdapter.run_turn()`を直接呼ぶ。次は通っていない。

```text
Plan -> Frozen Config -> POST /runs -> ExperimentRunWorker
-> Raw Evidence Persistence -> Case Evaluation -> Comparison -> Restart Read
```

したがって「実Model Gate 3/3」はDirect Production Adapter Smoke 3/3としては受理できるが、P9-2 F3の「最大3 Top-level Experiment Run」3/3ではない。

Scenario 2には、実JudgeがDecode／評価不能なら`pytest.skip()`へ落とす分岐もあるため、Gate OracleとしてFail-closed結果を保存・比較する証明にもなっていない。

- `tests/integration/test_real_local_experiment_production_variant_gate_smoke.py:353-358`

### IR-P9-2-R2-03 [MAJOR] Full Frozen Configを保存せずDigestだけを保存している

R2 HandoffはVariantごとの`EffectiveConfigurationSnapshot`生成・保存を要求したが、Planが保持するのは`variant_id + configuration_digest_sha512`だけである。

- `src/margpa_runtime_llm/modules/experiment/domain/identity.py:165-176`
- 同File `ExperimentPlan.variant_configuration_digests`

Snapshot内容を復元できるStore／Pointerは存在しない。さらに単一`provider_artifact_digest_sha512`はMain Artifactだけで、Judge／GuardのConfigured／Active／Artifact Identityを完全には凍結しない。

FrontendがPlan前に表示する「Frozen Config」は、実際にはPresetの宣言Component文字列であり、保存済みEffective Snapshotではない。

- `frontend/src/components/ExperimentPanel.tsx:42-54, 276-293`

Restart後にDigestの指す内容を読めず、ActualとのField別比較もできないため、P9-REQ-201／P9-ACC-039は部分成立に留まる。

### IR-P9-2-R2-04 [MAJOR] 未観測をFalse／0へ変換している

Production AdapterはGuard相関不能および5つの未観測Componentを、Outcome文字列では正直に表す一方、型上は次を確定値として保存する。

```text
called = False
mutation_count = 0
evidence_count = 0
authority_exercised = False
```

- `src/margpa_runtime_llm/modules/experiment/application/production_turn_runner.py:121-150`
- `ActorInvocationRecord.called`は必須`bool`で、Unknownを表現できない。

これはR2 Handoff §3／§5の「未観測を0／Falseへ変換しない」に直接反する。さらに`_metric_payload()`は`called=True`だけを数えるため、Unknown ComponentをCall 0として集計へ混ぜる。

### IR-P9-2-R2-05 [MAJOR] 実行中Config固定はLeaseではなく終了時再読だけ

実装は、設定変更を防止するLeaseを持たず、Turn終了後にLive Digestを再読して成功をFailedへ格下げするだけである。Source CommentもPreventive Lockを今Round Scope外と明記する。

- `src/margpa_runtime_llm/web/experiment_routes.py:653-670`
- `src/margpa_runtime_llm/modules/experiment/application/live_configuration_port.py:20-31`

途中でA→B→Aへ戻るABA変更は検出できない。実行中の一部区間へ別Configが混入すること自体も防がない。これはR2 Handoff §4.2のOption 3にある「Leaseの下だけで実行」を満たさない。

### IR-P9-2-R2-06 [MAJOR] Queue済みCancel／Deadline後もActorが後から実行される

Workerは単一Threadである。2件目がQueue中にDeadlineまたはUser Cancelへ到達すると、Persisted RunはTerminalになるが、Queue内Futureは取り消されない。後で`_task()`が開始するとTerminal確認なしに`invoke()`を実行し、結果PublishだけがLate Resultとして拒否される。

- `src/margpa_runtime_llm/modules/experiment/application/run_worker.py:91-142, 193-199`
- `request_cancel()`もCancel Hookを呼ぶだけでQueue Futureを取り消さない。

これはCancelled／Deadline済みRunのActor Call 0を破り、不要な実Model CallとResource消費を発生させる。

### IR-P9-2-R2-07 [MAJOR] PlanのExecution ModeがPlan作成時にFreezeされない

`execution_mode`は`StartRunRequest`でRunごとに後指定される。同じPlan／VariantをFixtureとProductionの両方として実行でき、Plan作成時にどちらのConfig契約を凍結したのかが曖昧である。

- `src/margpa_runtime_llm/web/experiment_routes.py:198-220`

R2 Handoff §4.1の「Plan作成時にExecution Modeを生成・保存」を満たさない。

## 5. Review A / B Decision

### Review A: Identity / Frozen Variant / Isolation

```text
FINDING
```

Request相関と部分的Config照合は改善したが、VariantごとのSnapshot保存、異なるProduction Variant実行、実行中Lease、Top-level実機Identity Chainが未成立。

### Review B: Evidence / Lifecycle / False Success

```text
FINDING
```

Case無条件PASSは解消した。一方、Unknown→False/0変換、Queue済みCancel／Deadline後のActor実行、実Model GateのAdapter Smoke化が残る。

## 6. Disposition

- Phase 9-2: `INCOMPLETE_FOR_USER_MANUAL`
- Phase 9-3: 未承認
- Phase 10: 未承認
- Git Write: 未承認
- 次Action: R3 Exact Handoffの有界Rework

R3ではR2成果を保持し、全面再設計を避ける。ただし、単に別名のPresetを追加するだけ、同一Live DigestをVariant名へ複製するだけ、実Model Adapterを直接呼ぶだけでは解決扱いにしない。
