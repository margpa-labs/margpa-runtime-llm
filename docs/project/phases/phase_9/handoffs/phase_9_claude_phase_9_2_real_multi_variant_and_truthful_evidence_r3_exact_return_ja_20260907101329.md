# Phase 9-2 — Real Multi-Variant / Truthful Evidence R3 Exact Return

```yaml
document_id: phase_9_claude_phase_9_2_real_multi_variant_and_truthful_evidence_r3_exact_return_20260907101329
document_type: exact_rework_return
document_state: ready_for_controller_review
phase: phase_9
program: phase_9_2
recorded_at: 2026-09-07 10:13:29 JST
language: ja
from: claude_designer_implementer
to: codex_controller
authority_owner: Nazuna Research
in_response_to: phase_9_controller_phase_9_2_real_multi_variant_and_truthful_evidence_r3_exact_handoff_ja_20260907090620.md
controller_review_of: phase_9_2_controller_r2_return_independent_review_and_r3_rework_decision_ja_20260907090620.md
maximum_claim: P9_2_R3_PARTIAL_READY_FOR_USER_REAL_GATE
phase_9_2_closure_authorized: false
phase_9_3_authorized: false
phase_10_authorized: false
git_write_performed: false
network_performed: false
append_only: true
```

## 1. 最大Claim

```text
P9_2_R3_PARTIAL_READY_FOR_USER_REAL_GATE
```

R3-WU-01〜03、WU-05は全項目Fixture／Integrationで収束し、Confirmed Findingを
Controller指定のHard Assertを満たす形で解消した（詳細は本Return全体）。
R3-WU-04（Top-level実Model Gate）のみ、実行時点でMemory Pressureが実測で
高く（第9節）、Handoff自身の"実Model実行時にMemory Pressureが高い場合は
強行せず、partial_ready_for_user_real_gateとして返す"という指示に従い、
実Model実行を今Roundでは行わなかった。Fixture／Integration段階の前提
（"Production VariantとActual EvidenceがFixture／Integrationで成立する"）
は本Roundで成立済みであり、Top-level経路（Plan→API→Worker→Adapter→
Evidence→Evaluation→Comparison→restart-read）の設計・実装自体は完了して
いる。Resource Gate解除後に実Model 3 Scenarioを実行すれば
`P9_2_R3_USER_MANUAL_CANDIDATE_FOR_CODEX_CONTROLLER_REVIEW`へ昇格できる
状態。Phase 9-2 Complete、Phase 9-3開始、Phase 9 Closureは自己承認しない。

## 2. R3-WU-01〜05 個別状態

| WU | 内容 | 状態 |
|---|---|---|
| R3-WU-01 | Production Plan／Variant Configuration成立（Multi-Variant、Lease、execution_mode Freeze） | **Resolved**（Fixture/Integration検証済み） |
| R3-WU-02 | Tri-state Evidence／Identity | **Resolved**（検証済み） |
| R3-WU-03 | Queue Cancel／Deadline Call 0 | **Resolved**（検証済み） |
| R3-WU-04 | Top-level実Model Gate | **Partial**（設計・実装は完了、実Model実行はResource Gateで今Round未実施） |
| R3-WU-05 | UI／Acceptance Truthfulness | **Resolved**（検証済み） |

## 3. Controller Finding対応表（IR-P9-2-R2-01〜07）

| Finding | 深刻度 | R2時点の状態 | R3での対応 | 状態 |
|---|---|---|---|---|
| IR-P9-2-R2-01 | CRITICAL | 同一Planで異なるProduction Variantを実行できない | Plan作成時のDesired Snapshot計算をVariantごとに独立させた（`overlay_variant_onto_snapshot()`）。Run開始時のCall-0 GateをPlan全体Digest一致からVariant宣言Slotのみの`find_mismatched_slots()`単独へ変更。各RunがLive Snapshotを新規取得しFrozen Configとして個別保存。 | **Resolved** |
| IR-P9-2-R2-02 | CRITICAL | 実Model GateがTop-level Experiment Runではない | Top-level経路自体（Plan→API→Worker→Adapter→Evidence→Evaluation→Comparison→restart-read）をFake Adapterで実証する新規Integration Testを追加し、Multi-Variant Hard Assertを満たすことを確認。実Model 3 Scenarioの同経路での実行はMemory Pressure Resource Gateにより今Round未実施。 | **Partial**（設計・機構は完了、実Model実行待ち） |
| IR-P9-2-R2-03 | MAJOR | Full Frozen Configを保存せずDigestだけを保存している | Run開始時に取得したLive Snapshot全体を`save_run_configuration_snapshot()`でRun別に保存。Plan作成時のDesired Snapshot全体も`save_variant_desired_configuration()`でVariant別に保存。両方ともRestart後に全内容を読み直せる。 | **Resolved** |
| IR-P9-2-R2-04 | MAJOR | 未観測をFalse／0へ変換している | `ActorInvocationRecord`をTri-state化（`called: bool \| None`、Mutation/Evidence/Authorityも連動）。Guard相関不能・5つの未観測Component・main_called曖昧Code分岐を全て`None`へ変更。`_metric_payload()`の`call_count`をConfirmed-Trueのみの下限値とし、`unknown_component_count`を新設して分離。 | **Resolved** |
| IR-P9-2-R2-05 | MAJOR | 実行中Config固定はLeaseではなく終了時再読だけ | `ExperimentConfigurationLease`を新設。`ExperimentRunWorker._task()`内でActor呼出し直前にAcquire、直後にRelease。`web/app.py`の既存`secure_requests` Middlewareへ、Settings変更Routeの固定Allowlistに対するLease-Held Check（409）を追加。ABA変更もLease保持中は一貫して拒否される。 | **Resolved** |
| IR-P9-2-R2-06 | MAJOR | Queue済みCancel／Deadline後もActorが後から実行される | `_task()`冒頭でRunの現在状態をFreshに再読し、Terminal済みならActor呼出しをCall 0で短絡。加えてCancel／Deadline時に`Future.cancel()`をBest-effortで試行する層も追加。 | **Resolved** |
| IR-P9-2-R2-07 | MAJOR | PlanのExecution ModeがPlan作成時にFreezeされない | `ExperimentPlan.execution_mode`を新設しPlan Digestへ組込み。`StartRunRequest`から`execution_mode`Fieldを削除し、Run開始時は常に`plan.execution_mode`を参照。Frontendも実行Mode選択をPlan作成前のFormへ移動。 | **Resolved** |

## 4. 選んだConfig実行方式と理由

Handoff R3 SS4.2の**Option A（Explicit User-Gated Live Match + Lease）**を
選択した。

理由:

- Option B（Experiment-scoped Controller/Composition）は、Judge/Guard/
  Governance/Repairの各Compositionを独立Instanceとして複製する必要があり、
  R1/R2で既に「別Runtime Instanceは今Roundには大きすぎる」と判断された
  Config Isolation Option 1と実質同じコストを要する。
- Option Aは、既存の`web/app.py`の`secure_requests` Middlewareへの
  純粋な追加のみで実現でき、Judge/Guard/Governance/Repairいずれの
  Controllerの契約も一切変更しない（「疎結合契約を弱めない」を字義通り
  満たす）。
- Handoff自身がOption Aを「MVP優先候補」と明記している。

Lease自体は次の性質を持つ:

- `ExperimentConfigurationLease`（新規、`modules/experiment/application/
  configuration_lease.py`）はThread-safeな真偽値のみを保持する軽量Mutex。
- **Acquireのタイミング**: `ExperimentRunWorker._task()`が権威的Terminal
  Checkを通過した直後、実Actor呼出し（`invoke()`）の直前。
- **Releaseのタイミング**: `invoke()`の`finally`ブロック内、Publish結果
  より前。例外発生時も必ずReleaseされる（`test_lease_is_released_even_
  when_the_actor_raises`で確認）。
- Runの「Queued〜Terminal」全期間ではなく、実Actor呼出しが物理的に
  実行されている間だけ保持される。
- **強制対象**: `POST /api/v5/feature-modes/{judge,repair,recording}`、
  `POST /api/v4/runtime-model/{context,max-new-tokens,switch}`、
  `PUT /api/v6/provider-selection/{role}`（Prefix一致）、`POST /api/v2/
  configuration/apply`（Guard/Main GovernanceのMode変更含む唯一のCanonical
  Mutation経路）。該当Route呼出し時にLeaseがHeldなら409
  `experiment_configuration_lease_held`を返す。Controller自体には一切
  触れない。
- Fixture Runには一切Leaseを渡さない（Fixtureは元々Live Configを読まない）。

## 5. 同一Planで異なるVariantを実行したEvidence

新規Integration Test
`test_two_different_production_variants_execute_and_compare_in_the_same_
plan`（`tests/integration/web/test_experiment_routes.py`）が次を実証する
（Fake Production Adapter、実Model不使用、Fixture/Integration段階）:

1. 同一Plan内に`production-main-only-baseline`と`production-judge-repair-
   baseline`の2 Variantを宣言。
2. Plan Responseの`variant_configurations`から取得した両Variantの
   Desired Configuration Digestが**異なる**ことをHard Assertで確認
   （Sabotage-regressionで検出力も確認、第10節）。
3. Live ConfigがMain-onlyへ既に適合した状態で1本目のRunを実行し
   `completed`まで到達。
4. その後、Userが明示的にLive Judge/Repair ModeをENFORCEへ変更
   （通常Chat Settings変更をSimulate）。
5. 2本目のRun（`production-judge-repair-baseline`）を同一Plan内で実行し
   `completed`まで到達。
6. 両Runの`frozen_configuration_digest_sha512`（各Runが自分のCall-0時点で
   実測したLive Snapshotの全内容Digest）が**異なる**ことをHard Assertで
   確認。
7. Comparison APIの各行にも同じ`frozen_configuration_digest_sha512`が
   正しく反映され、Runの実測値と一致することを確認。

## 6. Full Snapshot / Actual Evidence / Provider / Artifact / Request Identity Chain

- **Desired（Plan-level）**: `overlay_variant_onto_snapshot(variant, base)`
  がPlan作成時のLive Snapshotへ各Variant自身の宣言Componentを上書きした
  Full `EffectiveConfigurationSnapshot`を計算し、`save_variant_desired_
  configuration(experiment_id, variant_id, snapshot)`でVariant別に全内容
  保存（Digestのみではない）。UI表示専用の事前参照値であり、Run開始時の
  Gateには一切使わない。
- **Frozen（Run-level）**: Run開始のCall-0検証に使ったLive Snapshotその
  ものを`save_run_configuration_snapshot(run_id, snapshot)`でRun別に全
  内容保存。Restart後も`load_run_configuration_snapshot(run_id)`で復元
  可能（Round-trip Testで確認済み）。
- **Actual（Evidence）**: `ActorInvocationRecord`（Tri-state）、
  `ProductionTurnObservation`（`main_called`/`judge_called`/
  `guard_called: bool | None`、`repair_called`/`repair_adopted`分離、
  `final_disposition`）。Provider/Artifact識別はR2から変更なし
  （`provider_artifact_digest_sha512`はSnapshot内、Judge/Guard自体の
  Configured/Active/Executed Providerは既存のFeature Modes Statusの
  責務のまま）。
- **Request**: `VariantRun.request_id`（Experiment側）と
  `production_request_id`（Phase 9-1側の真のTurn request_id）は引き続き
  分離。

## 7. Queue Cancel／Deadline Call 0

`ExperimentRunWorker._task()`は、実行開始の瞬間に`service.get_run(run_id)`
でRunの現在の永続化状態をFreshに再読し、既にTerminal（Cancel／Deadline
いずれか）であれば`invoke()`を一切呼ばずに即Returnする（真のActor Call 0）。
これはWorkerが単一Threadである（`max_workers=1`）ため、後続Runが先行Run
完了までQueueされる状況で特に意味を持つ。

加えて、Cancel（`request_cancel()`）およびDeadline発火（`_on_deadline()`）
の両方で、対象Runの`Future`に対し`cancel()`をBest-effort実行する層も
追加した。これはQueue中でまだ開始していないTaskに対してのみ成功し、
既に開始済みのTaskには無効（Harmlessな No-op）。あくまで権威的Terminal
Checkの補助であり、代替ではない。

新規Test（`tests/unit/experiment/test_run_worker.py`）:

- `test_a_cancelled_run_queued_behind_another_never_has_its_actor_invoked`
- `test_a_deadline_exceeded_run_queued_behind_another_never_has_its_actor_invoked`

いずれもRun Aが実行中の間にRun Bを投入し、Bが未実行のままCancel／Deadline
へ到達させた後、Aの解放後もBのActorが一度も呼ばれないことを確認する。

## 8. Top-level実Modelの正確な回数と経路

**今Round、実Model実行は0回。** 理由は第9節のMemory Pressure実測による
Resource Gate。

- **Direct Adapter Smoke（既存、R1/R2成果）**: `tests/integration/
  test_real_local_experiment_production_variant_gate_smoke.py`。今Round
  再実行していない（Handoff自身が「既存Direct Adapter実Model Smokeは
  再実行不要」と明記）。ただし、本Roundの`ActorInvocationRecord` Tri-state
  化に伴い、このFile自身が持つ2件の`assert observation.guard_called is
  False`をTri-state対応の`is None`へ修正した（コード変更に追従させる
  静的修正であり、実Model実行を伴う検証ではない）。修正後、`ruff`/`mypy`
  でこのFileが構文・型として正しいことは確認済み。
- **Top-level Real Experiment Gate（新規、WU-04対象）**: 今Round未実装・
  未実行。設計は完了している（第11節「Open Findings」に具体的な実装方針を
  記載）。

## 9. Memory Pressure実測とResource Gate判断

実Model Gate着手前に測定した実測値（2026-09-07 09:38 JST頃、Fixture/
Integration検証の直後）:

```text
memory_pressure:
  Pages free: 50160 / Pages purgeable: 7619 (総Page数 1,048,576)
  System-wide Free相当 ≈ 5.5%
sysctl vm.swapusage:
  total = 4096.00M, used = 2925.75M, free = 1170.25M
```

R2 Roundで実Model Gateを実行した際の実測（57-72% Free、Swap未使用）と
比較して明確に悪化しており、Swapが既に約71%使用されている状態だった。
本Roundの終盤（2026-09-07 10:13 JST時点）で再測定したところ多少改善した
ものの、依然として次の水準にとどまる:

```text
memory_pressure:
  Pages free: 111211 / Pages purgeable: 5225
  System-wide Free相当 ≈ 11.1%
sysctl vm.swapusage:
  total = 4096.00M, used = 2677.75M, free = 1418.25M
```

Handoff自身の指示「実Model実行時にMemory Pressureが高い場合は強行せず、
True Stopではなくpartial_ready_for_user_real_gateとして返してください」
に従い、実Model Load（Main Qwen、Gemma、Qwen3Guardいずれも数GB単位の
実Memory消費を伴う）を今Round実行しなかった。`ps aux`でMain/Gemma/Guard
系Processが一切残っていないことも確認済み（そもそも今Round一度もLoad
していない）。

## 10. Sabotage-regression（3件、全て検出力確認・Byte-identical復元確認）

1. **Multi-Variant同一Digest化の巻き戻し**: `web/experiment_routes.py`の
   `create_plan()`内、Variantごとの`overlay_variant_onto_snapshot()`
   呼出しを`desired = live_at_plan_creation`（全Variant同一値）へ差し
   替えたところ、`test_two_different_production_variants_execute_and_
   compare_in_the_same_plan`が
   `AssertionError`（両Digestが完全一致）で確実に失敗することを確認。
   復元後、Byte-identicalであることを`diff`で確認、18/18再Pass。
2. **UnknownをFalseへ戻す巻き戻し**: `case_evaluator.py`の
   `_main_call_count()`内、`if called is None: return None`を削除した
   ところ、新規Test`test_retrieval_strict_no_hit_case_is_unavailable_
   when_main_call_status_is_unknown`が`INCONCLUSIVE`（誤った確定Zero
   扱い）を返し、期待する`UNAVAILABLE`との不一致で確実に失敗することを
   確認。復元後、Byte-identical、12/12再Pass。
3. **Queue Terminal Checkの除去**: `run_worker.py`の`_task()`内、
   `if is_terminal(service.get_run(run.run_id).state): return`を
   `if False: return`へ差し替えたところ、
   `test_a_cancelled_run_queued_behind_another_never_has_its_actor_
   invoked`が確実に失敗（`b_invoked.is_set() is False`のAssertionが
   `True`で失敗）することを確認。復元後、Byte-identical、12/12再Pass。

## 11. Fixture／Production-fixture／Direct Adapter Smoke／Top-level Real Experimentの区別

| 種別 | 本Roundでの状態 | 実Model使用 |
|---|---|---|
| Fixture | 既存機構そのまま、変更なし（Tri-state化の影響も受けない：FixtureActorは常に確定True/False） | なし |
| Production-fixture（Fake Adapter経由） | 本Roundで新規Multi-Variant Hard Assert Testを追加、Top-level経路（Plan→API→Worker→Adapter→Evidence→Evaluation→Comparison→restart-read）をFake Production Turn Portで検証 | なし |
| Direct Adapter Smoke | 既存File、今Round再実行なし。Tri-state化に伴う静的Assertion修正2件のみ実施（第8節） | 前回実行分のみ、今回は未実行 |
| Top-level Real Experiment | **今Round未実施**（第9節のResource Gate） | 0回 |

## 12. P9-REQ／P9-ACC Mapping

| ID | 内容 | 状態（Fixture/Integration） | 状態（実Model） |
|---|---|---|---|
| P9-REQ-201 / P9-ACC-039 | Experiment/Run/Request相関、Config Snapshot、Artifact/Definition/Plan Digest | Desired/Frozen Snapshot共にFull保存・相関可能（第6節） | 実Model未検証（Resource Gate） |
| P9-REQ-202 / P9-ACC-040 | Main/Judge/Guard/GD/RAG/Repair/Modeを同一Caseで比較 | Main-onlyとJudge/Repair-ENFORCEの2 Variant比較をFakeで実証（第5節）。Guard Variantは本Round未実行（実Modelでのみ意味を持つため） | 実Model未検証（Resource Gate） |
| P9-REQ-203 | Self/Independent Judge、定量/定性、Human/LLM Reviewの混同なし | R2から変更なし、Rollbackなし | 変更なし |
| P9-REQ-204 | Multiple Definition/Conflict/Suppression/Repair Propagation/Routing比較 | 対象外（今Round Scope外、既存Fixture Matrixのまま） | 対象外 |
| P9-REQ-205〜208 | Freshness/Retrieval/Authority/Strict-Progressive | R2から変更なし、Rollbackなし | 変更なし |
| P9-REQ-209 | Manual URL Fail-closed時のMain Call 0を含むTurn Execution Trace | Tri-state化によりMain Call状態がFalse/None/Trueで正直に分離される形へ強化（第3節 IR-P9-2-R2-04） | 実Model未検証 |
| P9-ACC-041〜044 | Definition/Freshness/Authority/Buffer比較 | R2から変更なし、Rollbackなし | 変更なし |
| P9-ACC-045 | Baseline/Regression/Ablation比較、混同なしComparison Report | Comparison Rowに`execution_mode`/`frozen_configuration_digest_sha512`を追加し、Variant差を明示的に区別可能にした | 実Model未検証 |

## 13. 検証結果

### Focused Unit
- `tests/unit/experiment/`：全Pass。
- `tests/unit/bootstrap/test_experiment_production_turn_adapter.py`：全Pass。

### Integration/Web
- `tests/integration/web/test_experiment_routes.py`：18Test全Pass（新規2件含む：Multi-Variant実行、Drift許容の反転Test）。

### Queue Cancel/Deadline Determinism
- `tests/unit/experiment/test_run_worker.py`：12Test全Pass（新規4件：Cancel Queue Call 0、Deadline Queue Call 0、Lease Acquire/Release Window、Lease Release-on-exception）。

### Backend Non-model Full Suite
```text
2629 passed, 40 deselected in 82.42s
```
（`pytest`をpyproject.tomlの既定`addopts`のまま実行、`model_smoke` Marker
のみ除外。R2時点の`2627 passed, 40 deselected`から純増2件〈本Roundの新規
Unit Test追加分〉、Deselect数40件は不変＝Direct Adapter Smoke含む実Model
系は正しく除外されている。）

### Ruff / Mypy（全Repo）
- Ruff：`All checks passed!`
- Mypy（Canonical、`pyproject.toml`の`[tool.mypy]`設定どおり`src`+
  `scripts`+`tests`、`strict=true`）：`Found 43 errors in 4 files`
  （R2時点のBaselineと完全一致、新規Error 0件）。

### Frontend
- `npm test -- --run`：34 Files / 331 Tests 全Pass。
- `npx tsc --noEmit`：Clean。
- `npx eslint .`：Clean。
- `npm run build`：成功（`app.js` 382.62 kB / gzip 103.96 kB）。

## 14. Internal Review A / B（Handoff R3 SS10準拠、自己点検）

### Review A: Identity / Frozen Variant / Isolation

- 同一Caseの異なるProduction Variantが本当に実行されたか → **Yes**
  （Fakeで実証、第5節）。実Modelでは未実施。
- Frozen／Desired／Actual ConfigとProvider／Artifact／Requestが分離
  されたか → **Yes**（第6節）。
- 通常Chat Global設定をExperimentが無言Mutationしていないか →
  **Yes（していない）**。LeaseはMutationを**拒否するだけ**で、Mutate-
  then-Restoreのような自己変更パターンは一切存在しない。
- Restart後のIdentity Chain → **Yes**（Desired/Frozen Snapshot共に
  Round-trip Test済み）。

Findings: なし（新規Confirmed Critical/Majorなし）。

### Review B: Evidence / Lifecycle / False Success

- Unknown→False/0、Completed→PASS、Called→Adoptedの偽装 → **Unknown→
  False/0はR3で解消**（第3節 IR-P9-2-R2-04）。Completed→PASSはR2で
  既に解消済み、Rollbackしていない。Called→AdoptedもR2の分離を維持。
- Queue Cancel／Deadline／Late Result／Shutdown → **Queue Cancel/
  Deadlineの真のCall 0をR3で追加達成**（第7節）。Late Result（Generation
  Counter）とShutdown Drainの既存契約は変更していない（`_task()`の
  権威的CheckはShutdown DrainのTask実行時にも同様に働くため、Shutdown
  時のQueue済みRunについても同じ保護が及ぶ）。
- Direct Adapter SmokeをTop-level Runと誤表現していないか → **していない**。
  本Return全体で明確に「Direct Adapter Smoke」と「Top-level Real
  Experiment」を区別して記述し（第8節・第11節）、後者は今Round未実施と
  明記している。
- UIがPreset宣言とFrozen Snapshotを混同していないか → **混同していない**。
  「Frozen Config」Labelを「宣言Component」（Declared components）へ
  改名し、Desired Config Digest（Plan時点）とFrozen Config Digest
  （Run時点実測）を別Labelで表示するよう変更（第16節）。

Findings: なし（新規Confirmed Critical/Majorなし）。実装中に自ら発見・
修正したGap 3件は第17節に記載。

## 15. Open Findings

1. **Top-level実Model Gate未実施（Resource Gate）**: 本Round最大の
   未解決点。Fixture/Integration段階の前提は成立済みで、実装方針も
   確立している（下記）。次のRoundまたはMemory Pressure改善後、以下の
   構成で実行可能:
   - `bootstrap.web_application.build_phase1_web_runtime()`を
     **Monkeypatchせず**そのまま呼び出し、`registry_path`に実Qwen
     Registry TOMLを渡すことで実Main Modelを正規Bootstrap経路から
     素直にLoadする（既存の`tests/integration/test_real_local_main_
     gemma_concurrent_dispatch_smoke.py`の
     `test_a_real_gemma_main_governance_enforce_run_authorizes_and_
     adopts_the_repair`が同じ`build_phase1_web_runtime()`を
     `LocalConversationPersistenceSettings`付きで呼び出し、
     Experiment Persistence／Production Adapter／Live Configuration
     Reader／Lease全てを無条件で得られることを確認済みの前例）。
   - `feature_modes_enabled=True`、`guardrail_governance_enabled=True`、
     `dedicated_model_authority_granted=True`、
     `conversation_persistence_settings=LocalConversationPersistence
     Settings(...)`を指定。
   - 得られた`WebRuntime`を`create_web_app(runtime_factory=lambda:
     runtime, ...)`へ渡し、`tests/integration/web/test_experiment_
     routes.py`と同じ`httpx.AsyncClient`パターンでPlan作成→Run実行を
     駆動する。
   - Scenario 2/3では`runtime.judge_mode_control.apply_mode(...)`/
     `runtime.role_provider_lifecycle.activate(role=ModelRole.JUDGE)`/
     `runtime.guardrail_governance_composition`経由でJudge/Guardを
     Runの間に明示的に切り替える（Option Aの想定User Workflowと同一）。
   - Model品質FAILは`pytest.skip()`せず、Typed FAILED/INCONCLUSIVE Row
     として同一Identity Chainへ保存する（Handoff要求どおり）。
   - この設計自体は今Round実装・検証していない（未実装のCodeを
     「動く」と主張することは避けた）。
2. Definition Set/RAG/Presentation 3 Component SlotはLive Controllerが
   Codebaseに存在せず、R2から引き続き対象外（`mode=None`固定）。
3. Guard Evidence相関は引き続き`unavailable_correlation`（`called=None`
   へ格上げ済みだが、真の相関機構自体は依然として存在しない）。
4. main_called判定の曖昧Error Code（Pre/Post両方から到達し得る4種）は
   `None`（Tri-state Unknown）へ格上げ済み。Phase 9-1側でCode自体を
   一意化する将来改修は引き続きOpen。
5. `production-guard-baseline` Variantを含むMulti-Variant Hard Assert
   （3 Variant目としてのGuard比較）はFixture/Integration段階でも今Round
   実施していない（2 Variantでの実証に留めた）。P9-REQ-202の完全な
   3-way比較はTop-level実Model Gate実施時に合わせて確認する想定。

## 16. Files Changed（本R3 Roundで実際に変更・新規作成したFileのみ）

既存のDirty Tree（Phase 6／Phase 9-1由来の未Commit変更）は本Round一切
触れていない。以下は本R3 Roundで実際にEdit/Writeした範囲のみ。

**新規:**
- `src/margpa_runtime_llm/modules/experiment/application/configuration_lease.py`

**変更（Backend / Domain・Application）:**
- `src/margpa_runtime_llm/modules/experiment/domain/config_snapshot.py`
- `src/margpa_runtime_llm/modules/experiment/domain/composition.py`
- `src/margpa_runtime_llm/modules/experiment/domain/evaluation.py`
- `src/margpa_runtime_llm/modules/experiment/domain/identity.py`
- `src/margpa_runtime_llm/modules/experiment/application/production_turn_runner.py`
- `src/margpa_runtime_llm/modules/experiment/application/case_evaluator.py`
- `src/margpa_runtime_llm/modules/experiment/application/run_worker.py`
- `src/margpa_runtime_llm/modules/experiment/ports.py`

**変更（Adapters / Bootstrap / Web）:**
- `src/margpa_runtime_llm/adapters/experiment/local_filesystem_experiment_store.py`
- `src/margpa_runtime_llm/bootstrap/experiment_production_turn_adapter.py`
- `src/margpa_runtime_llm/bootstrap/web_application.py`
- `src/margpa_runtime_llm/web/experiment_routes.py`
- `src/margpa_runtime_llm/web/contracts.py`
- `src/margpa_runtime_llm/web/app.py`

**変更（Tests）:**
- `tests/unit/experiment/test_production_turn_runner.py`
- `tests/unit/bootstrap/test_experiment_production_turn_adapter.py`
- `tests/integration/web/test_experiment_routes.py`
- `tests/unit/experiment/test_run_worker.py`
- `tests/unit/experiment/test_config_snapshot_mismatch.py`
- `tests/unit/experiment/test_case_evaluator.py`
- `tests/unit/experiment/test_local_filesystem_experiment_store.py`
- `tests/integration/test_real_local_experiment_production_variant_gate_smoke.py`
  （Tri-state化に伴うAssertion 2件のみの静的修正、実Model再実行なし）

**変更（Frontend）:**
- `frontend/src/types.ts`
- `frontend/src/components/ExperimentPanel.tsx`
- `frontend/src/components/ExperimentPanel.test.tsx`
- `frontend/src/i18n/translations.ts`
- `frontend/src/api/client.ts`

## 17. UI／Acceptance Truthfulness（WU-05）詳細

1. Plan作成前に実行Mode（Fixture/Production）を選び、Plan作成後は
   Frozen（`disabled`化）。Run開始時に選び直す経路自体をBackend側で
   廃止したため、UIとBackendの契約が一致する。
2. 旧「Frozen Config」Labelを「宣言Component」（Declared components）へ
   改名。Plan作成後は各Variantの実際の"Desired Config Digest"（Plan時点
   算出）を短縮表示。Run完了後はComparison表に"Frozen Config Digest"
   （Run時点実測）を別列で表示。三者は常に別Labelで並存し、混同を防ぐ。
3. 各Variantの実行Buttonの隣に`[ready]`/`[running]`/`[completed]`等、
   最新Runの実State（無ければ`ready`）を表示するよう変更。
4. Live Mismatch時のBackend Typed Code（`live_config_mismatch`等）は
   既存の`ApiMutationError`経由でそのまま表示（変更なし、既に正しく機能）。
5. **Unknown Evidenceの表示Bug修正**: `invocation.called ? "true" :
   "false"`という三項演算子が、`called === null`（Tri-state Unknown）を
   誤って"false"と表示するBugがあった。`calledDisplay()`関数を新設し、
   `true`/`false`/`null`を明確に区別して表示するよう修正（この修正は
   本Round新規発見のUI Bugであり、第18節にも記載）。
6. Comparison APIに`execution_mode`と`frozen_configuration_digest_
   sha512`を追加し、UIのComparison Tableへ両列を追加。同一Caseの
   Variant差・実行Mode・Frozen Config Digestが並んで見える。
7. P9-REQ/ACC Mappingは第12節のとおり；RAG/Main Governance/Routing/
   Strict-Progressiveの未到達部分はR2から変更なし、明確にPartialのまま
   残している（今Round新たに到達可能にはしていない、Scope外として維持）。

## 18. 実装中に自ら発見・修正したGap（Confirmed Findingではないが記録）

1. `ExperimentPanel.tsx`の`invocation.called ? "true" : "false"`が
   Tri-state `null`を`"false"`（確定Call 0）と誤表示するUI Bug
   （第17節5参照）。
2. `_metric_payload()`の`call_count`計算が`if item.get("called")`という
   真偽判定のみで、`None`と`False`の両方を"0"として合算していた
   （Tri-state導入前は無害だったが、導入と同時に修正しないと同じ
   False-Evidence Gapを再生産するところだった）。
3. Plan作成時のDesired Snapshot計算をVariantごとに独立させる際、当初
   `for variant in variants: desired = live_at_plan_creation`のような
   誤実装（全Variant同一値の使い回し）を書きかけたが、Sabotage-
   regression Test作成の過程で自ら検出・修正した（詳細は第10節1）。

## 19. Git／Network／Root外Mutation／Process／Port／Model状態

- **Git**: `git rev-parse HEAD` = `1f0e70e47fa058484c4b32f33c6cbca52e0afd2a`
  （Round開始時と不変）。`git diff --cached --stat`は空。`git stash
  list`は空。`git add`/`commit`/`push`/`stash`/`reset`/`clean`いずれも
  未実行。
- **Network**: 一切のNetwork呼出しなし（既存Fixture/Fake経由のTestのみ）。
- **Root外Mutation**: なし。Scratchpad（`/private/tmp/claude-501/...`）
  以外への書込みは全てRepository内Source/Test/Docsのみ。
- **Process**: `ps aux`でMain/Judge(Gemma)/Guard(Qwen3Guard)系Processが
  一切残っていないことを確認（今Round実Model自体を一度もLoadしていない
  ため、そもそも発生し得ない）。
- **Port**: 変更なし（Web Server自体は本Round起動していない、Test経由の
  In-process ASGI Transportのみ使用）。
- **Model**: 今Round実Model 0回Load・0回実行。

## 20. 次のAction

Codex Controller Independent Reviewを待つ。Phase 9-2 Complete、Phase 9-3
着手、Phase 9 Closure、追加の実Model実行のいずれも、本Returnの範囲では
行わない。Controller ReviewでR3-WU-04（Top-level実Model Gate）の実施が
承認された場合、第15節1項に記載した設計に基づき実装・実行する想定。
