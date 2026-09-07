# Phase 9-2 R3 Return — Codex Controller Independent Review / R4 Rework Decision

```yaml
document_id: phase_9_2_controller_r3_return_independent_review_and_r4_rework_decision_20260907104830
document_type: controller_independent_review
document_state: completed
phase: phase_9
program: phase_9_2
recorded_at: 2026-09-07 10:48:30 JST
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

- Return: `phase_9_claude_phase_9_2_real_multi_variant_and_truthful_evidence_r3_exact_return_ja_20260907101329.md`
- Return SHA-512: `80b6658addcbe8d99bf07d727cd000e7962fd4e56432ff35d522d7257fd45c297f919688e8c6a0aa14ce93eec1c2dfb0efa03b7da439f0ad314e6d749c22d09e`
- Recovery: `phase_9_2_real_multi_variant_and_truthful_evidence_r3_recovery_ja_20260907101329.md`
- Recovery SHA-512: `b0f822430dc9a86008f442cb79d1d7fc378ad191bd7dcd9f868b412afa0e5345a6a9c6fd70b9108c23976de38fc4b9452177fde46085c215678357c49fb38819`
- R3 Exact Handoffと現行Source／Test／UI。

Controller focused verification:

```text
235 passed in 2.34s
```

実Modelは再実行していない。

## 2. 結論

```text
CHANGES_REQUIRED
Maximum accepted claim:
P9_2_R3_PARTIAL_MULTI_VARIANT_FIXTURE_FOUNDATION
```

R3は、Variant別Desired Snapshot、Tri-state Evidence、Plan-level Execution Mode、Queue済みRunのActor Call 0、比較UIを前進させた。一方、Production VariantのProvider Identity、Live照合とLeaseの原子境界、Queue Future取消後のWorker状態、Top-level実Model Gateが未成立である。

したがって、`P9_2_R3_PARTIAL_READY_FOR_USER_REAL_GATE`はそのまま受理しない。残件は実機実行だけではなく、実機Gate前に直すべき局所的なSource残差を含む。

## 3. R3で受理する成果

次はRollbackしない。

1. 同一Plan内でVariantごとに異なるDesired Snapshotを生成・保存する仕組み。
2. RunごとのFull Snapshot保存とRestart Read。
3. `ActorInvocationRecord`のTri-state化とUnknown Count分離。
4. `execution_mode`のPlan-level Freeze。
5. Queue開始時のTerminal再確認によるActor Call 0。
6. Desired／Frozen Digest、実行Mode、Unknown Evidenceを区別するUI。
7. R3で通過したFocused／Full／Frontend／Static検証。

## 4. Confirmed Findings

### IR-P9-2-R3-01 [CRITICAL] Provider違いをVariant mismatchとして検出しない

`find_mismatched_slots()`は宣言Modeしか比較せず、`selector_id`を比較していない。

- `src/margpa_runtime_llm/modules/experiment/domain/config_snapshot.py:248-292`

Controller Probeでは、VariantがGemmaを宣言し、Live JudgeがMain-shared Qwenでも空Tupleを返した。

```text
find_mismatched_slots(...) == ()
```

さらにProduction PresetはMain／Judge／GuardのProviderを宣言せず、`overlay_variant_onto_snapshot()`は宣言済みSlotのLive Selectorを`None`へ置き換える。

- `src/margpa_runtime_llm/web/experiment_routes.py:52-127`
- `src/margpa_runtime_llm/modules/experiment/domain/config_snapshot.py:222-229`

このままでは「Main Qwen + Gemma」と「Main Qwen + Qwen3Guard」のVariantが別Providerで実行されてもCall 0にならない。Modeが一致するだけで別構成を同一Variantとして実行できるため、Top-level実Model GateのIdentity Claimを成立させられない。

### IR-P9-2-R3-02 [CRITICAL] Live照合とLease取得の間にTOCTOU Raceがある

HTTP RouteはLive Snapshotを読み、照合・Run作成・Snapshot保存を行った後でWorkerへSubmitする。

- `src/margpa_runtime_llm/web/experiment_routes.py:722-770`

Lease取得はWorker Threadが後から`invoke()`直前に行う。

- `src/margpa_runtime_llm/modules/experiment/application/run_worker.py:152-172`

したがって、RouteのLive照合後からWorkerのLease取得前まで、Settings変更を拒否する主体が存在しない。この間にConfigが変わると、ActorはFrozen Snapshotと異なる構成で実行される。終了時再読は継続中の差をFailedへ落とせるだけで、A→B→AのABA変更や、実Model Call自体の発生を防げない。

これは「Run前Live mismatchはCall 0」「一致後、実行中の変更をLeaseで拒否」の双方を破る。

### IR-P9-2-R3-03 [MAJOR] Full SnapshotがProvider Identityを完全には保持しない

`BootstrapLiveConfigurationReader`はJudge／Guardについて`active_provider`だけを一つの`selector_id`へ写し、ConfiguredとActiveを分離しない。Artifact DigestもMainの単一Digestだけである。

- `src/margpa_runtime_llm/bootstrap/experiment_live_configuration.py:110-185`
- `src/margpa_runtime_llm/modules/experiment/domain/config_snapshot.py:35-59`

Judge／GuardのConfigured／Active／期待Executed／ArtifactをRun Snapshotから区別できず、`case_digest_sha512`と`plan_digest_sha512`もLive Reader生成時は`None`のままである。R3 Handoff §4.1.3のFull Snapshot契約は部分成立に留まる。

### IR-P9-2-R3-04 [MAJOR] Queue Future取消成功時に`_in_flight`が残る

Deadline／User CancelでQueue中Futureの`cancel()`が成功すると、そのTaskは開始されないため、`_task()`の`finally`にある`_in_flight.pop()`も実行されない。

- `src/margpa_runtime_llm/modules/experiment/application/run_worker.py:128-150, 201-205, 270-290`

Actor Call 0自体は守れるが、Terminal RunのWorker EntryとCancel Hookが残り、`request_cancel()`が終了済みRunを再び見つけ得る。取消成功、Timer、Shutdownを含むCleanupを一つの冪等経路へ収束させる必要がある。

### IR-P9-2-R3-05 [MAJOR] Top-level実Model Gateは未実装であり、Resource判定根拠も不十分

Return §8／§15はTop-level実Model Testを「未実装・未実行」と明記している。よって残件は単なるUser実行待ちではなく、Test経路の実装を含む。

またReturnの5.5%／11.1%は、macOSの`Pages free + purgeable`を総Page数で割った独自計算であり、`memory_pressure`自身が出すSystem-wide Memory Pressure指標ではない。Swap使用量も過去の圧力を保持し得るため、それ単独では現在の危険判定にならない。

Controller確認時の`memory_pressure`は`System-wide memory free percentage: 85%`を返した。ただし、これは10:48時点の再測定であり、Claude実行時点が安全だったと遡及断定する証拠ではない。次回はOSが直接提示するPressure状態を使って実行直前に再判定する。

### IR-P9-2-R3-06 [MAJOR] HTTP Settings MutationのLease実配線Testがない

Middlewareに409応答は追加されているが、現行TestはLease Objectの`is_held()`だけを確認し、実際のFeature Mode／Provider／Runtime Model／Configuration Apply RouteがActor実行中に409となり、解放後に復旧することを確認していない。

- `src/margpa_runtime_llm/web/app.py:175-205, 349-371`
- `tests/unit/experiment/test_run_worker.py:350-390`

R3 Handoff §4.3のSettings変更拒否、ABA防止、Lease解放後復旧はProduction Web Composition水準で未証明である。

## 5. Disposition

- Phase 9-2: `INCOMPLETE_FOR_USER_MANUAL`
- Phase 9-3: 未承認
- Phase 10: 未承認
- Git Write: 未承認
- 次Action: R4局所Rework後、Top-level実Model Gateを最大3 Scenarioで実施する。

