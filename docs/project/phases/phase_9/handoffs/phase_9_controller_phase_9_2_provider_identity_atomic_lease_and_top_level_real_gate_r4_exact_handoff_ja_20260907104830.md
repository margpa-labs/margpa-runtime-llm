# Phase 9-2 — Provider Identity / Atomic Lease / Top-level Real Gate R4 Exact Handoff

```yaml
document_id: phase_9_controller_phase_9_2_provider_identity_atomic_lease_and_top_level_real_gate_r4_exact_handoff_20260907104830
document_type: exact_rework_handoff
document_state: ready
phase: phase_9
program: phase_9_2
recorded_at: 2026-09-07 10:48:30 JST
language: ja
from: codex_controller
to: claude_designer_implementer
authority_owner: Nazuna Research
decision_authority: user
in_response_to: phase_9_claude_phase_9_2_real_multi_variant_and_truthful_evidence_r3_exact_return_ja_20260907101329.md
controller_review: phase_9_2_controller_r3_return_independent_review_and_r4_rework_decision_ja_20260907104830.md
maximum_claim: P9_2_R4_USER_MANUAL_CANDIDATE_FOR_CODEX_CONTROLLER_REVIEW
phase_9_2_closure_authorized: false
phase_9_3_authorized: false
phase_10_authorized: false
git_write_authorized: false
network_authorized: false
append_only: true
```

## 1. Objective

R3の有効成果を保持し、次の順でPhase 9-2をUser実画面確認候補へ収束させる。

```text
Providerを含むVariant Identity
-> Live照合とLeaseの原子境界
-> Queue Cancel/Deadline Cleanup
-> Production Web Lease証明
-> Top-level実Model Experiment 3 Scenario
```

## 2. Primary Inputs

1. R3 Controller Review。
2. R3 Return／Recovery／Exact Handoff。
3. 現行Experiment Source／Test／UI。
4. Phase 9-2 Requirements／Acceptance Matrix。

無関係なHistoryの全件再読はしない。

## 3. Non-negotiable Boundary

- R3で成立したMulti-Variant、Tri-state、Plan-level Execution Mode、Restart Read、Evaluation／Comparison、UIをRollbackしない。
- 通常Chat Global設定をExperimentが無言変更しない。
- Production VariantはModeだけでなくProvider Identityも照合する。
- Live照合後からActor終了まで、設定変更が入り込む無保護区間を残さない。
- 未観測Identityを推測値で埋めない。
- Fixture／Production-fixture／Direct Adapter Smoke／Top-level実Model Experimentを混同しない。
- Selene、DeepSeek Judge、Gemma Schema／Sampling／Retry、Phase 9-1評価Logicは変更しない。
- Phase 9-3／Phase 10へ進まない。

## 4. R4-WU-01 — Providerを含むVariant／Snapshot Identity

### 4.1 Required Behavior

1. Production Presetは少なくとも次を明示する。

```text
production-main-only-baseline:
  Main = Qwen3 4B

production-judge-repair-baseline:
  Main = Qwen3 4B
  Judge = Gemma 4 E2B

production-guard-baseline:
  Main = Qwen3 4B
  Guard = Qwen3Guard 0.6B
```

2. Provider固有値はExperiment Coreへ埋め込まず、Web／Bootstrap Adapter層の既存Provider定数を使う。
3. `find_mismatched_slots()`は、Variantが`selector_id`を宣言したSlotについてModeとSelectorの両方を比較する。宣言していないSelectorはDon't-careのままとする。
4. Desired Snapshot作成時、宣言ModeだけをOverlayしたために必要Providerが`None`へ消えない。
5. Full Snapshot／保存Envelopeは、取得可能な範囲でMain／Judge／GuardのConfigured、Active、期待Executed、Artifact Digestを別Fieldとして保持する。取得不能値はUnavailableであり、同一値へ潰さない。
6. Run SnapshotをCase Digest／Plan Digest／Variant ID／Run IDから辿れるようにする。Digest循環を作らず、Snapshot本体または保存Envelopeで相関すればよい。

### 4.2 Hard Assert

- Variant=Gemma、Live Judge=Main-shared Qwen、両方ENFORCEならCall 0 Typed mismatch。
- Variant=Qwen Main、Live Main=別ProviderならCall 0 Typed mismatch。
- Gemma VariantのDesired表示とRestart ReadにGemma Identityが残る。
- Configured Gemma／Active noneと、Configured Gemma／Active Gemmaを区別できる。
- Judge／Guard Artifact不明をMain Artifact Digestで代用しない。

## 5. R4-WU-02 — Live MatchとLeaseの原子化

### 5.1 Required Behavior

現在の`Live Snapshot read -> match -> Run persist -> Worker submit -> Lease acquire`間のTOCTOUを除去する。

実装方式は局所性を優先して選んでよいが、次を同時に満たすこと。

1. Production Actorを呼ぶ最終Snapshot読取・Variant照合は、設定変更を拒否する同一Lease境界内で行う。
2. mismatch時はMain／Judge／Guard／Repair Call 0でTyped Failureへ収束する。
3. Lease取得不能またはProduction CompositionでLease未配線なら、無保護実行へFallbackせずTyped Call 0とする。
4. LeaseはActor呼出しと必要な直後Snapshot取得まで保持し、例外・Cancel・Deadlineでも冪等に解放する。
5. A→B→AのABA変更をActor実行中に成立させない。
6. 通常Chat Controller自体へExperiment固有契約を埋め込まない。

同期HTTP 409か非同期Run FAILEDかは、既存Async APIを壊さず、状態とTyped Codeが正直に残る方式を選ぶ。Runを作成した後にCall 0 Rejectする場合は、`running`のまま残さない。

### 5.2 Deterministic Race Tests

- Snapshot読取直後／Lease取得直前へBarrierを置き、Settings変更を試みてもActorが誤構成で呼ばれない。
- Queue中のProduction Runが開始する前に設定変更を試み、最終照合がLease内で行われる。
- Actor実行中のJudge Mode、Provider Selection、Runtime Model、Configuration Applyが409。
- Actor終了後は同じRouteが通常どおり使える。
- Actor例外、Cancel、Deadline後もLeaseが残らない。

## 6. R4-WU-03 — Queue Future取消後のCleanup

1. Queue中Futureの`cancel()`成功時も、`_in_flight` Entry、Timer、Cancel Hookを冪等にCleanupする。
2. Task実行時`finally`、Future Done Callback、Deadline、User Cancelの複数経路が競合しても二重Terminal Publishや例外を起こさない。
3. Cancel／Deadline済みQueue RunはActor Call 0を維持する。
4. Terminal後の`request_cancel(run_id)`は`False`となる。
5. Shutdown後に取消済みEntryが残らないことを機械検証する。

## 7. R4-WU-04 — Top-level Real Experiment Gate

WU-01〜03とProduction Web Testが通った後だけ実施する。

### 7.1 Test経路

新しい実Model TestはDirect Adapter呼出しではなく、実際に次を通す。

```text
build_phase1_web_runtime()
-> create_web_app()
-> Plan API
-> Run API
-> ExperimentRunWorker
-> LiveProductionTurnAdapter
-> Raw Evidence Persistence
-> Evaluation
-> Comparison
-> Runtime再構成後のRead
```

実装したTestをFixture／Fakeで先に通し、Top-level経路自体を確認する。

### 7.2 Resource Preflight

- `memory_pressure`が直接出すSystem-wide Pressure／Free Percentageと、Activity MonitorのMemory Pressureを優先する。
- `Pages free + purgeable`の独自割合をSystem-wide Free Percentageとして扱わない。
- Swap使用量は補助Evidenceとし、単独の停止理由にしない。
- Pressureが実際に高い場合だけ、実Model 0回のPartial Returnを許容する。
- 実行前後にProcess／Port／Model Unloadを確認する。

### 7.3 Scenario（最大3 Run、逐次）

1. Main Qwen only。
2. Main Qwen + Gemma Judge／Repair ENFORCE。
3. Main Qwen + Qwen3Guard ENFORCE。

Model品質FAIL、Judge／Repair非発火、Guard非発火は捏造せず、Typed ResultとActual Evidenceを保存する。`pytest.skip()`、Retry、入力を歪めた強制成功は禁止する。最低1 ScenarioでRuntime再構成後もPlan／Desired／Frozen／Run／Raw Evidence／Evaluation／Comparisonを読めること。

## 8. R4-WU-05 — Verification

順序:

1. Provider／Snapshot Focused Unit。
2. Atomic Lease Race／Queue Cleanup Test。
3. Experiment Integration／Production Web Middleware Test。
4. Frontend Test／Typecheck／Lint／Build。
5. Backend Non-model Full Suite。
6. Ruff／Canonical Mypy Baseline差分。
7. 条件成立後のみTop-level実Model Gate。
8. 完全に観点を分けたInternal Review A／B。

Sabotage-regressionは最低限次を含める。

- Selector比較を外すとWrong Provider Testが落ちる。
- Lease内最終照合をLease外へ戻すとRace Testが落ちる。
- Future Cancel時Cleanupを外すとTerminal後`request_cancel()==False`が落ちる。

## 9. Review A / B

Review A:

- VariantのMode／Provider／Artifact／Configured／Activeが混ざっていないか。
- Desired／Frozen／Actual／Executedが相関可能か。
- Wrong ProviderがCall 0になるか。
- Top-level実Model経路がDirect Smokeへ短絡していないか。

Review B:

- Lease前Race、ABA、Queue、Cancel、Deadline、Shutdown。
- Future取消成功時のCleanup。
- UnknownをFalse／0へ変換していないか。
- Resource判定をmacOSの非権威的な独自割合で誤判定していないか。

Confirmed Critical／Major／MVP Blockerだけを修正し、無限Reviewを行わない。

## 10. Scope / Authority

- Phase 9-1、Selene、DeepSeek、Gemma Decoder／Schema／Sampling／Retryを変更しない。
- RAG／Definition Set／Presentationの新Controllerを作らない。
- Phase 9-3／Phase 10へ進まない。
- Main Chat／Settings／右Panelの大改造をしない。
- Network、Download、Install、Root外Mutationを行わない。
- Git `add`／`commit`／`push`／`stash`／`reset`／`clean`を行わない。
- Phase Index、Roadmap、Technology Selection、Unresolved Registryを編集しない。
- Existing Return／Historyを上書きしない。
- Existing Dirty Treeを保持する。

## 11. Exact Return / Recovery

新規Pathへ作成する。

```text
docs/project/phases/phase_9/handoffs/
  phase_9_claude_phase_9_2_provider_identity_atomic_lease_and_top_level_real_gate_r4_exact_return_ja_<timestamp>.md

docs/project/phases/phase_9/history/index/
  phase_9_2_provider_identity_atomic_lease_and_top_level_real_gate_r4_recovery_ja_<timestamp>.md
```

Returnには、各WU状態、Finding対応表、Before／After、Provider Identity Matrix、Atomic Lease Timeline、Queue Cleanup、Top-level実Model回数と経路、Resource Preflight生値、Verification、Review A／B、Open Findings、Git／Process／Model状態を記録する。

最大Claim:

- 全必須項目とTop-level実Model Gate成立: `P9_2_R4_USER_MANUAL_CANDIDATE_FOR_CODEX_CONTROLLER_REVIEW`
- Source／Fixture成立、実Modelだけ正当なResource Gate: `P9_2_R4_PARTIAL_READY_FOR_USER_REAL_GATE`
- Critical／Major残存: `P9_2_R4_INCOMPLETE_FOR_CONTROLLER_REVIEW`

Phase 9-2 Complete、Phase 9-3開始、Phase 9 Closureは自己承認しない。

## 12. True Stop

- 原子的なLive照合とLeaseに通常Chat Global設定の無言Mutationが不可避。
- Provider Identityを分離するとPhase 9-1の疎結合契約破壊が必要。
- Existing Dirty Treeを保持できない。
- 新Authority、Network、Cost、Model取得、Git Writeが必要。
- 実Modelを安全にUnload／Stopできない。

難しい、時間がかかる、Test未実装、独自Memory割合が低いという理由だけで必須項目を独断でScope外へ移さない。
