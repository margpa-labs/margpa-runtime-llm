# Phase 9-1 Controller Independent Review 3 — Temporal State／Concurrency／Lifecycle

```yaml
document_id: phase_9_1_controller_independent_review_3_temporal_state_concurrency_lifecycle_20260901033408
document_state: finding_confirmed_rework_required
language: ja
created_at: 2026-09-01T03:34:08+09:00
phase: phase_9
program: phase_9_1
review_ordinal: 3
review_axis: temporal_state_concurrency_and_lifecycle
independent_from_review_1_and_2: true
default_review_policy_changed: false
phase_9_1_closure: forbidden
```

## 1. Review境界

Review 1のRequirement／Acceptance／Claim照合と、Review 2のOperator Journey／Production Reachabilityは繰り返していない。本Reviewは、時間軸上のState変化、並行Turn、失敗途中のResource所有権、Cancel／DeadlineおよびUnloadだけを対象とした。

```text
Candidate Load途中失敗
→ Rollback／Cleanup
→ 複数Lease発行
→ Duplicate／Stale Release
→ Mode OFF中Drain
→ Guard実Inference中Cancel／Deadline
→ Shutdown／Unload
```

既存のPASS件数、Acceptance件数およびMaximum Claimは、本Reviewの根拠として流用していない。

## 2. P9-CODEX-008 — Candidate部分Load失敗後のResourceが追跡不能になる

```yaml
severity: critical_mvp_blocker
disposition: open_rework_required
affected_scope:
  - dedicated_provider_activation
  - model_memory_ownership
  - rollback_truthfulness
  - shutdown_and_unload
```

### 2.1 原因

`RoleProviderLifecycleManager._activate_locked()`および`_transition_to_locked()`は、`candidate.load()`が例外を送出した時に`candidate.unload()`を呼ばない。

Dedicated Adapterの`load()`は単一Atomic操作ではない。Selene／Qwen3Guardともに、先にGGUFをLoadし、その後にRole固有Manifest／Adapterを構築する。この後半で例外が起きると、Model Resourceは既にLoad済みでもLifecycle ManagerはCandidateを`_active_adapters`へ登録せず、参照を破棄する。

### 2.2 Deterministic Probe

`load()`内でResourceを取得した後に例外を送出するAdapterを与えた結果、次を再現した。

```text
state: unavailable
candidate.loaded: true
candidate.unload_calls: 0
manager.active_adapter: none
```

すなわちProvider状態は`unavailable`へ収束する一方、実ResourceだけがLoad済みで追跡不能になる。

### 2.3 Rollback Testの実Adapter非相似

既存Testの`_FakeAdapter(fail_load=True)`はResource取得前に即時例外を送出し、部分Loadを再現しない。また旧Provider復旧時に同じFakeへ即`previous.load()`を再実行できるが、実Dedicated Adapterの`unload()`はPreflightで構築したBackend／Definitionを消去するため、再Preflightなしの`previous.load()`は成立しない。

### 2.4 Required Rework

- `candidate.load()`失敗時は、部分Loadの有無にかかわらずBest-effort `candidate.unload()`を必ず実行する。
- Cleanup失敗を無視して`UNAVAILABLE`と表示せず、Resource所有権不明を示すTyped Failure／`DEGRADED`へ収束する。
- 旧Provider Rollbackは実AdapterのPreflight→Load Contractに従って再構築するか、Rollback不能として正直に`DEGRADED`へ収束する。
- Resource取得後例外、Candidate Cleanup例外、旧Provider再Load例外を別々にRegression Testする。
- `NONE`／`BUILT_IN`切替で既存Dedicated AdapterのUnloadが失敗した場合も、その結果を捨てて新状態を`ACTIVE`／`NONE`とClaimしない。

## 3. P9-CODEX-009 — LeaseのIdentityを消費せず、Duplicate／Stale Releaseで別Turnを終了できる

```yaml
severity: critical_concurrency_blocker
disposition: open_rework_required
affected_scope:
  - judge_turn_lease
  - guard_turn_lease
  - mode_off_drain
  - provider_switch
  - unload_safety
```

### 3.1 原因

`RoleTurnLease`は`role`、`provider_id`、固有`generation`を持つが、Managerが保持するのはRole単位の`_active_turns: int`だけである。`end_turn()`は`provider_id`と`generation`を検査せず、Countが正なら常に1減算する。

このためLeaseは「固有の実行権限」ではなく「同Roleの任意Countを1減らせる再利用可能Token」になっている。

### 3.2 Deterministic Probe

同じProviderへLease A／Bを発行し、Mode OFF相当のDrainへ入れた後、Aを二度Releaseした。

```text
Release A first time:
  active Turn B remains
  unload_calls = 0

Release A second time:
  active Turn B remains unreleased
  unload_calls = 1
  active_adapter = none
```

実行中のBが残っているのにAdapterがUnloadされた。Bの正規Releaseはその後何も保護できない。同様に、Provider切替前のStale Leaseを再送すると新ProviderのTurn Countを減算し得る。

### 3.3 Existing Test Gap

既存Testは複数Leaseの`generation`が異なることだけを確認し、Lease IdentityのExactly-once消費、Duplicate Release、Stale Provider Release、Forged Leaseを検証していない。

### 3.4 Required Rework

- Active Leaseを`generation -> (role, provider_id)`として登録する。
- `end_turn()`は一致する未消費LeaseだけをExactly onceで消費する。
- Duplicate／Stale／Forged／Provider不一致Leaseは、他Turn Countを変更せずTypedに拒否または安全にIgnoreする。
- Drain中の二重Releaseでも最後の実Leaseが終了するまでUnloadしないThread Testを追加する。
- Provider切替前Leaseが切替後Providerを減算できないRegression Testを追加する。

## 4. P9-CODEX-010 — Qwen3Guard実InferenceにDeadline／Cancellationが配線されていない

```yaml
severity: major_mvp_liveness_blocker
disposition: open_rework_required
affected_scope:
  - guardrail_input
  - guardrail_context_source
  - guardrail_output_candidate
  - user_stop
  - mode_off_and_shutdown
```

### 4.1 原因

`Qwen3GuardGenAdapter.classify_point()`は`InferenceService.generate()`を同期呼出しするが、`CancellationToken`を渡さず、Stage Deadlineにも包まれていない。`GuardrailPointRuntime.invoke()`と`build_guardrail_hooks()`も同じRequest実行経路上で同期的にDetectorを呼び出す。

`except TimeoutError`は存在するが、Timeoutを発火させるBudget／Timer／CancellationはこのProduction経路にない。Judge／Repair側に存在する`stage_deadline()`とTracked Stage Workerの規律が、Guard側には適用されていない。

### 4.2 影響

- Qwen3Guard推論が停止または長時間化するとChat Request全体が待ち続ける。
- Leaseは同期Call終了まで保持される。
- Mode OFFはDrainへ入っても、実CallをPreemptできない。
- Server ShutdownもActive Leaseが残ればCleanに収束できない。
- User StopがMain生成を止めても、Guardの同期実Inferenceを止める保証がない。

Phase 9-1が要求する「実Qwen3Guardが動く」とは、成功時だけでなくStop／OFF／Unloadへ戻れることを含むため、単なるHardeningではなくMVP Liveness条件である。

### 4.3 Required Rework

- GuardのInput／Context Source／Output Candidate全経路へ共通Stage Budgetと`CancellationToken`を配線する。
- Timeout時は実Token Loopを止め、Typed `TIMEOUT` Detection／Evidenceへ収束させる。
- Deadline Return後もWorkerが残る場合はTracked Worker Registryへ登録し、Unload前にDrain結果を確認する。
- Timeout後のLate ResultをCurrent Evidenceへ追加しない。
- Mode OFF／User Stop／ShutdownとのRaceを実Thread Testで確認する。

## 5. Review 3結論

Review 1／2では検出されなかったCritical 2件、Major 1件を検出した。

```text
P9-CODEX-008: Candidate部分Load Resource Leak
P9-CODEX-009: Duplicate／Stale Lease Release
P9-CODEX-010: Unbounded Qwen3Guard Inference
```

Phase 9-1は、P9-CODEX-006〜010をReworkし、実Selene／実Qwen3GuardについてLoad→Inference→Evidence→OFF／Stop→UnloadをUser Mac上で成立させるまでComplete Candidateへ戻してはならない。
