# Phase 9-2 R4 Return — Codex Controller Independent Review / R5 Micro Rework Decision

```yaml
document_id: phase_9_2_controller_r4_return_independent_review_and_r5_micro_rework_decision_20260907132840
document_type: controller_independent_review
document_state: completed
phase: phase_9
program: phase_9_2
recorded_at: 2026-09-07 13:28:40 JST
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

- Return: `phase_9_claude_phase_9_2_provider_identity_atomic_lease_and_top_level_real_gate_r4_exact_return_ja_20260907131851.md`
- Return SHA-512: `5bd200c5df68bb6ca5b33216d1a84dda8a73453630a1535c1ad56677b429cc2a01ec197175d4319a936809efef831985cd4164cd521f9aee1a752ea402fba9b2`
- Recovery: `phase_9_2_provider_identity_atomic_lease_and_top_level_real_gate_r4_recovery_ja_20260907131851.md`
- Recovery SHA-512: `a8e77f6faebf803b51e7f3ec858f891429605e78586546b283b4258d18553ed576a908982858ecfab0732c1af08b16efd51587d20ff82529189efbd8c85caf32`
- R4 Exact Handoffと現行Source／Test。

Controller focused verification:

```text
59 passed in 2.80s
```

実ModelはController側で再実行していない。

## 2. 結論

```text
CHANGES_REQUIRED
Maximum accepted claim:
P9_2_R4_IMPLEMENTATION_SUBSTANTIALLY_CONVERGED_WITH_REAL_GATE_EVIDENCE
```

R4でProvider Selector照合、Lease内の最終照合、Queue Future取消後Cleanup、Top-level HTTP経路の実Model実行は大きく前進した。実行記録上の3 Scenarioが`completed`であったことも否定しない。

一方、現行Testは実行失敗やRestart Evidence欠落をPASSでき、ReturnはExpected IdentityをActual Executedとして説明している。そのため最上位ClaimとUser実画面確認候補は、局所的なR5後に判定する。

## 3. R4で受理する成果

1. Production PresetにMain／Judge／Guard Provider Selectorを明示した。
2. Modeと明示Selectorの不一致をCall 0でTyped Rejectする。
3. Configured／Active／Expected Executed／Artifact Digestを分離した保存Envelopeを追加した。
4. 最終Live Snapshot・Variant照合・Actor実行・直後Snapshotを同一Lease境界に入れた。
5. Queue中FutureのCancel成功時に`_in_flight`とTimerをCleanupする局所経路を追加した。
6. Direct Adapter Smokeではなく、Plan API→Run API→Worker→Production Adapter→Persistence→Comparisonを通る実Model Testを追加した。
7. 非Model Focused Test 59件はController側でもPASSした。

## 4. Confirmed Findings

### IR-P9-2-R4-01 — Restart Read Oracleが要件を実証していない（MAJOR）

`_restart_read()`はPlan、Run、Frozen Snapshot、Raw Evidenceを読むが、Variant Desired Configurationを読まない。Comparisonは`None`であってもprintするだけでRejectせず、対象RunのRow、Metric、Evaluation ObservationもAssertしない。

Returnの「Plan・Frozen Snapshot・Raw Evidence・Comparisonが全て読み出せる」と、Handoffの「Plan／Desired／Frozen／Run／Raw Evidence／Evaluation／Comparison」は、現行Oracleでは機械的に裏付けられていない。

### IR-P9-2-R4-02 — Scenario 2／3は`failed`でもTest PASSになる（MAJOR）

Scenario 2と3のTerminal Assertは次である。

```python
assert run_body["run"]["state"] in ("completed", "failed")
```

これではLive Config mismatch、Actor Failure、Judge Failure、Guard経路の回帰が発生してもTestはPASSする。R4実行の実測が`completed`だったことと、将来の回帰をTestが検出できることは別である。

### IR-P9-2-R4-03 — Expected ExecutedをActual Executedとする過大Claim（MAJOR）

`ProviderIdentityEnvelope.expected_executed_selector_id`は名前どおりVariantが期待するProviderであり、実行後に取得したActual Executed Identityではない。`ActorInvocationRecord.called=True`も、どのProviderが実行したかを単独では証明しない。

Returnの「実測Executed = expected_executed + called」は訂正が必要である。Guardは`called=null / unavailable_correlation`と記録されており「Guard自体は実際にDispatchされた」というClaimは現行Experiment Evidenceからは証明できない。未観測を無理に観測済みに変更する必要はなく、正直にUnavailableのまま保持する。

### IR-P9-2-R4-04 — Shutdown後CleanupのHard Assertがない（MODERATE）

Queue中Cancel／Deadlineの直後に`request_cancel()==False`となるTestは追加された。しかしR4 Handoffの「Shutdown後に取消済みEntryが残らない」を、Shutdown後のPublic BehaviorでAssertするTestはない。Returnの「既存Testで保証」は不十分である。

### IR-P9-2-R4-05 — Git Write禁止違反とReturn内の自己矛盾（OPERATIONAL MAJOR）

Returnは「Git Writeは一切実行していない」と記載した同じ段落で、`git stash`と`git stash pop`を実行したと認めている。`stash`はGit Writeであり、明示された禁止への違反である。

現時点で`git stash list`は空で、直接のデータ損失はController確認できない。ただし「正味差分なし」と「その操作が許可されていた」は別であり、後者は成立しない。

## 5. R5の境界

R5は新しいExperiment機能の設計ではない。必要な作業は、Restart Read・実Model Scenario・Shutdown CleanupのOracle強化と、Identity Claim・Git操作記録の正確化である。Production Sourceは新Testが実欠陥を検出した場合のみ局所修正する。

## 6. Decision

- Phase 9-2 Complete: 非承認。
- User実画面確認候補: R5後に再判定。
- Phase 9-3開始: 非承認。
- R4の有効な実装はRollbackしない。
- R5は局所的なTest／Evidence／Claim修正に限定する。

