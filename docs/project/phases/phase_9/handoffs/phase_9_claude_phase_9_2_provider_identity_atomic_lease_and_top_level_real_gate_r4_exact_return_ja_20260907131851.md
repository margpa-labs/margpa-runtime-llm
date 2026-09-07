# Phase 9-2 — Provider Identity / Atomic Lease / Top-level Real Gate R4 Exact Return

```yaml
document_id: phase_9_claude_phase_9_2_provider_identity_atomic_lease_and_top_level_real_gate_r4_exact_return_20260907131851
document_type: exact_return_handoff
document_state: ready
phase: phase_9
program: phase_9_2
recorded_at: 2026-09-07 13:18:51 JST
language: ja
from: claude_designer_implementer
to: codex_controller
authority_owner: Nazuna Research
decision_authority: user
in_response_to: phase_9_controller_phase_9_2_provider_identity_atomic_lease_and_top_level_real_gate_r4_exact_handoff_ja_20260907104830.md
maximum_claim: P9_2_R4_USER_MANUAL_CANDIDATE_FOR_CODEX_CONTROLLER_REVIEW
phase_9_2_closure_authorized: false
phase_9_3_authorized: false
phase_10_authorized: false
git_write_authorized: false
network_authorized: false
append_only: true
```

## 0. Maximum Claim（最大Claim）

`P9_2_R4_USER_MANUAL_CANDIDATE_FOR_CODEX_CONTROLLER_REVIEW`

R4-WU-01〜05のすべての必須項目が成立し、Top-level実Model Gateも最大3 Scenario全てが実際に実行され、全て`completed`で終了した。R3 Controller Reviewの確認済Finding（IR-P9-2-R3-01〜06、CRITICAL 2件・MAJOR 4件）を全件解消した。Phase 9-2 Complete、Phase 9-3開始、Phase 9 Closureはいずれも自己承認していない。

## 1. Controller確認済Finding対応表

参照: `docs/project/phases/phase_9/history/operations/phase_9_2_controller_r3_return_independent_review_and_r4_rework_decision_ja_20260907104830.md`

| Finding | 深刻度 | 対応Work Unit | 状態 | 検証 |
|---|---|---|---|---|
| IR-P9-2-R3-01 Provider違いをVariant mismatchとして検出しない | CRITICAL | R4-WU-01 | Resolved | Domain 3件＋Route(HTTP) 3件のHard Assertテスト、Sabotage-regression 1件 |
| IR-P9-2-R3-02 Live照合とLease取得の間のTOCTOU Race | CRITICAL | R4-WU-02 | Resolved | Deterministic Race Test（Lease内で読取確認）、Sabotage-regression 1件 |
| IR-P9-2-R3-03 Full SnapshotがProvider Identityを完全保持しない | MAJOR | R4-WU-01 | Resolved | `ProviderIdentityEnvelope`新設＋Correlation Block追加、実Model Gateでの実測値で確認 |
| IR-P9-2-R3-04 Queue Future取消成功時に`_in_flight`が残る | MAJOR | R4-WU-03 | Resolved | 冪等Cleanup追加、専用テスト2件、Sabotage-regression 1件 |
| IR-P9-2-R3-05 Top-level実Model Gate未実装／Resource判定根拠不十分 | MAJOR | R4-WU-04 | Resolved | 3 Scenario全て実装・実際に実行・全て`completed` |
| IR-P9-2-R3-06 HTTP Settings MutationのLease実配線Testがない | MAJOR | R4-WU-02/05 | Resolved | 実FastAPI Middleware経由の409＋解放後復旧テスト |

## 2. Work Unit別 Before/After

### R4-WU-01 — Providerを含むVariant/Snapshot Identity

**Before**: `find_mismatched_slots()`はModeのみ比較し`selector_id`を無視していた。Production Presetは`selector_id`を一切宣言していなかった。`overlay_variant_onto_snapshot()`はVariantがMode宣言のみでSelector未宣言の場合、Live側の`selector_id`を`None`へ潰していた（Handoff R4 SS4.1.4の明示的バグ）。

**After**:
- [config_snapshot.py](../../../../../src/margpa_runtime_llm/modules/experiment/domain/config_snapshot.py)（312行）: `find_mismatched_slots()`が`declared.selector_id is not None`のときのみSelector一致も要求するよう拡張（未宣言のSelectorはDon't-careのまま）。`overlay_variant_onto_snapshot()`の`_slot()`を修正し、Variantが`selector_id`を宣言しない場合はLiveの値を保持するよう修正。
- [experiment_routes.py](../../../../../src/margpa_runtime_llm/web/experiment_routes.py)（1211行）: `production-main-only-baseline`/`production-judge-repair-baseline`/`production-guard-baseline`の3 Presetに、それぞれ`QWEN_MAIN`/`GEMMA_E2B_JUDGE`/`QWEN3_GUARD`（`runtime_model_control.application.provider_selection_controller`の既存定数、Experiment Core固有の新規定義ではない）を`selector_id`として明示。
- 新規 [domain/provider_identity.py](../../../../../src/margpa_runtime_llm/modules/experiment/domain/provider_identity.py)（99行）: `ProviderIdentityDetail`（`component_key`/`configured_selector_id`/`active_selector_id`/`expected_executed_selector_id`/`artifact_digest_sha512`）と`ProviderIdentityEnvelope`（main/judge/guardの3 Slotのみ、Slot整合性Validator付き）。`with_expected_executed()`でVariant知識を後から注入。
- [live_configuration_port.py](../../../../../src/margpa_runtime_llm/modules/experiment/application/live_configuration_port.py)（40行）: Protocolへ`provider_identity() -> ProviderIdentityEnvelope`を追加。
- [bootstrap/experiment_live_configuration.py](../../../../../src/margpa_runtime_llm/bootstrap/experiment_live_configuration.py)（253行）: `BootstrapLiveConfigurationReader.provider_identity()`を実装。Main側はConfigured/Active/Artifact DigestをすべてRuntimeModelController（Provider SelectionControllerのMAIN Entryは実Switch後に無同期でStaleになり得るため意図的に不採用）から取得し、`runtime_state is ACTIVE`のときのみActive/Digestを報告（Switching/Loading中は両方Unavailable）。Judge/GuardはProviderSelectionController経由でConfigured/Activeを、Artifact DigestはACTIVEなProviderのOptionからのみ取得（Configuredや別RoleのDigestを代用しない）。
- Run Snapshot永続化（`web/experiment_routes.py`の`_invoke_production`内）: 保存Dictへ`provider_identity`（Expected Executed込み）と`correlation`（`run_id`/`experiment_id`/`variant_id`/`case_digest_sha512`/`plan_digest_sha512`）を追加。既存Key（`configuration_digest_sha512`等）はそのまま残るため、既存読み手（digest再計算等）に影響なし。
- Frontend [ExperimentPanel.tsx](../../../../../frontend/src/components/ExperimentPanel.tsx): `formatComponents()`がMode表示に加え`selector_id`を`main=active(main.qwen3-4b-q4-k-m)`のように表示するよう拡張。Preset選択リストとComparison Tableの両方に反映（コード共有のため一箇所の修正で両方に効く）。

**Hard Assert検証**: Domain単体（`test_config_snapshot_mismatch.py`）でMain/Judge/Guardそれぞれの「Mode一致・Provider不一致」ケースをテスト。HTTP経由（`test_experiment_routes.py`）でも同じ3ケースを実際のFastAPI Route経由で確認し、いずれも`409 live_config_mismatch`、`adapter.calls == []`（Actor未呼び出し）。

### R4-WU-02 — Live MatchとLeaseの原子化

**Before**: `start_run()`はLease取得前（つまりWorkerへSubmitする前）にLive Snapshotを読み、照合し、Frozen Snapshotを保存していた。Lease自体はWorkerの`_task()`が`invoke()`直前に取得するのみで、Route側のLive読取からWorkerのLease取得までの間に無保護区間が存在した。

**After**: 「最終Live読取→照合→Frozen保存→実Actor呼出し→事後再確認」の全シーケンスを、Worker側で既にLease取得済みの状態で呼ばれる`invoke`Closure（`_invoke_production`）の内部へ完全に移設。Route側の元の照合コードはAdvisory（同期409による早期失敗のためだけの）Pre-checkとして残し、Frozen Snapshotの永続化は行わない。これにより、Live読取からActor呼出しまでの間に一切の無保護Windowが存在しなくなった（`run_worker._task()`の`lease.acquire()`が`invoke()`呼出しより厳密に先行するのは既存のR3実装のまま、変更なし）。

- `lease is None`の場合（Production Compositionに一切Lease未配線）は、Typed Call 0（`CONFIGURATION_LEASE_UNAVAILABLE`、既存だが未使用だったError Code）へ収束させ、無保護実行へFallbackしない。
- 同期POST `/runs`のレスポンスは、Productionの場合`frozen_configuration_digest_sha512`を常に`None`で返すよう変更（真の値は非同期Task完了後にのみ判明するため、既存のDocstringが元々想定していた挙動）。既存Testは全て`_wait_for_terminal_run()`でPolling後のGETから読んでいたため無影響。

**Deterministic Race Test**: `LeaseObservingLiveConfigurationPort`という新規Fakeで`.snapshot()`呼出し時点の`lease.is_held()`を記録し、`_invoke_production`内部からの呼出し（最終照合＋事後再確認の2回）が両方とも`True`であることを確認（Plan作成時・Advisory Pre-checkの読取はLease無保護のままだが、これは意図通り）。

**HTTP Middleware Deterministic Test**: 実行中Production Runの間に`POST /api/v5/feature-modes/judge`を叩くと`409 experiment_configuration_lease_held`、Run完了後は同じRouteが同コードを返さないことを実FastAPI経由で確認。

### R4-WU-03 — Queue Future取消後のCleanup

**Before**: `_on_deadline()`/`request_cancel()`は`entry.future.cancel()`を呼ぶだけで、成功時（＝該当Runがまだ真にQueue中で`_task()`が一度も走らない）でも`_in_flight` Entry・Timerを一切Cleanupしていなかった。`_task()`自身の`finally`はTaskが実際に走らない限り発火しないため、成功したCancel後もEntryが永続的に残り、後続の`request_cancel()`が誤って`True`を返し得た。

**After**: `ExperimentRunWorker._cleanup_in_flight_if_cancelled_while_queued(run_id, entry)`を新設。`entry.future.cancel()`が成功した場合のみ即座に`_in_flight.pop()`とTimer Cancelを行う（失敗時＝既に開始／終了済みの場合は何もせず、`_task()`自身のCleanupに委ねる）。`_on_deadline()`と`request_cancel()`の両方から呼び出す単一の冪等経路に統一。

**検証**: 新規テスト`test_a_queued_futures_successful_cancel_cleans_up_in_flight_immediately`（Cancel成功直後の二重`request_cancel()`が`True`→`False`と正しく遷移）、既存の`test_a_deadline_exceeded_run_queued_behind_another_never_has_its_actor_invoked`へ同種のAssertを追加。

### R4-WU-04 — Top-level実Model Experiment Gate

**Resource Preflight**（Handoff R4 SS7.2準拠、`memory_pressure`自身のSystem-wide指標を採用、独自Pages計算は不使用）:

| 時点 | System-wide memory free percentage（`memory_pressure`出力） | Swap使用（補助Evidence） |
|---|---|---|
| 実行直前 | 78-79% | 1930-1938MB / 3072MB |
| 実行直後 | 74% | ほぼ同水準 |

R3時点の誤った独自計算（Pages free+purgeable／総Page数、5.5%〜11.1%）とは全く異なる、健全な値（R2の健全Baseline 57-72%も上回る）。「困難・時間がかかる」を理由にResource Gateへ逃げる余地はなく、実行した。

**実行経路**: `build_phase1_web_runtime()`（Monkeypatchなし、`registry_path=config/models/qwen3_4b_q4_k_m.toml`、`feature_modes_enabled`/`runtime_model_control_enabled`/`guardrail_governance_enabled`/`dedicated_model_authority_granted`全て`True`、`conversation_persistence_settings`実体あり）→ `create_web_app()` → 実FastAPI経由で`GET /presets` → `POST /plans`（`execution_mode="production"`）→ `POST /runs` → `ExperimentRunWorker` → `LiveProductionTurnAdapter`（実Model呼出し）→ Raw Evidence永続化 → `GET /experiments/{id}/comparison` → 元Runtimeとは別の新規`LocalFilesystemExperimentStore`インスタンスによるRestart Read。新規ファイル: [tests/integration/test_real_top_level_experiment_production_gate_smoke.py](../../../../../tests/integration/test_real_top_level_experiment_production_gate_smoke.py)（351行、`@pytest.mark.model_smoke`3件）。既存のDirect Adapter Smoke（`test_real_local_experiment_production_variant_gate_smoke.py`）はTop-level経路と混同されないよう別ファイルのまま維持し、今回は再実行していない。

**実行結果（3/3 Scenario、逐次、同一プロセス内で連続実行時23.84秒、Apple Silicon実機）**:

| # | Scenario | 結果 | Main | Judge | Repair | Guard |
|---|---|---|---|---|---|---|
| 1 | Main Qwen only | `completed` | `called=true outcome=completed` | `called=false outcome=off` | `called=false outcome=off` | `called=null outcome=unavailable_correlation` |
| 2 | Main Qwen + Gemma Judge/Repair ENFORCE | `completed` | `called=true` | `called=true outcome=accept` | `called=false outcome=off`（Judge Acceptのため非発火、正直な結果） | `called=null` |
| 3 | Main Qwen + Qwen3Guard ENFORCE | `completed` | `called=true outcome=completed` | `called=false outcome=off` | `called=false outcome=off` | `called=null outcome=unavailable_correlation`（Guard自体は実際にDispatchされたが、Adapter自身のCorrelation機構が今Round未整備という既知のGapで、捏造せず正直にUnknown） |

Scenario 2でRepairが非発火だったのは、実Gemma Judgeが実際にCandidateをAcceptしたため（Deviationが見つからなかった）——これは正直なTyped Resultであり、`pytest.skip`や入力歪曲による強制成功では一切ない。各Scenarioとも独自の`LocalFilesystemExperimentStore`によるRestart Readで、Plan・Frozen Snapshot（`provider_identity`/`correlation`Block含む）・Raw Evidence・Comparisonが全て読み出せることを確認した。

**実行後の状態**: 3 Scenario全て完了後、`ps aux | grep llama`でモデルプロセス残存ゼロを確認。`runtime.close()`を各Scenarioの`finally`で確実に呼び出し済み。

### R4-WU-05 — Verification

## 3. 検証結果一覧

| 項目 | 結果 |
|---|---|
| Provider/Snapshot Focused Unit | `test_config_snapshot_mismatch.py` 14件全Pass（新規5件）、`test_provider_identity.py` 4件全Pass（新規ファイル）、`test_experiment_live_configuration.py` 4件全Pass（新規ファイル） |
| Atomic Lease Race/Queue Cleanup | `test_run_worker.py` 14件全Pass（新規1件＋既存2件へAssert追加） |
| Experiment Integration/Production Web Middleware | `test_experiment_routes.py` 24件全Pass（新規6件：Wrong Main/Judge/Guard Provider、Lease Unavailable、Race Lease、Settings Mutation 409） |
| Frontend Test/Typecheck/Lint/Build | `npm test` 331件全Pass（既存Test 1件を更新してSelector表示を検証）、`tsc --noEmit`/`eslint .`/`npm run build`いずれもClean |
| Backend Non-model Full Suite | `2649 passed, 43 deselected`（83.71秒）。R3終了時点`2629 passed, 40 deselected`から純増20件（Deselect純増3件はWU-04新規`model_smoke`3件） |
| Ruff（Whole Repo） | `All checks passed!` |
| Canonical Mypy（Whole Repo、`pyproject.toml`既定設定） | `43 errors/4 files`（既存Baseline完全一致） |
| Top-level実Model Gate | 3/3 Scenario実行、全て`completed`（上記詳細） |

## 4. Sabotage-regression（3件、全て検出力確認＋Byte-identical復元確認済み）

1. **Selector比較除去**: `find_mismatched_slots()`のSelector比較部分を削除 → `test_a_declared_wrong_selector_mismatches_even_when_mode_agrees`/`test_a_declared_wrong_main_provider_mismatches`（Domain）、`test_production_run_rejects_a_wrong_judge_provider_even_with_matching_mode`（HTTP）の計3件が失敗することを確認。`config_snapshot.py`をBackupから復元しByte-identical確認済み。
2. **Lease内最終照合をLease外へ**: `_invoke_production`内の`live_configuration_reader.snapshot()`をLease取得前に事前計算した値へ差し替え → `test_the_final_live_match_happens_strictly_inside_the_lease_window`が`[False, True]`（本来`[True, True]`）で失敗することを確認。`experiment_routes.py`をBackupから復元しByte-identical確認済み。
3. **Future Cancel時Cleanup除去**: `_cleanup_in_flight_if_cancelled_while_queued`の`_in_flight.pop()`部分を無効化（`cancel()`は呼ぶがCleanupしない）→ `test_a_queued_futures_successful_cancel_cleans_up_in_flight_immediately`と`test_a_deadline_exceeded_run_queued_behind_another_never_has_its_actor_invoked`の計2件が失敗することを確認。`run_worker.py`をBackupから復元しByte-identical確認済み。

## 5. Review A（Snapshot/Identity観点）

- VariantのMode／Provider／Artifact／Configured／Activeは混ざっていない: `EffectiveConfigurationSnapshot`（Mode+単一Selector、Frozen-vs-Live比較専用）と`ProviderIdentityEnvelope`（Configured/Active/ExpectedExecuted/ArtifactDigestの4分離Field、Main/Judge/Guardのみ）は別Contractとして独立している。
- Desired／Frozen／Actual／Executedは相関可能: Preset宣言（`desired_components`のselector_id）→ Plan-level Desired（`overlay_variant_onto_snapshot()`）→ Run-level Frozen（`save_run_configuration_snapshot`の`correlation`Block、`run_id`/`experiment_id`/`variant_id`/`case_digest_sha512`/`plan_digest_sha512`を明示）→ 実測Executed（`provider_identity.*.expected_executed_selector_id`と`ActorInvocationRecord`の実測`called`）の全経路をRestart Readで実証済み。
- Wrong ProviderはCall 0になる: HTTP経由3件（Main/Judge/Guard）で確認。
- Top-level実Model経路はDirect Smokeへ短絡していない: 新規Testは`create_web_app()`→実HTTP Route経由でのみModelを呼び出しており、`LiveProductionTurnAdapter.run_turn()`を直接呼ぶコードパスは一切含まない。

## 6. Review B（並行性/資源観点）

- Lease前Race、ABA、Queue、Cancel、Deadline、Shutdown: WU-02（Lease前Race＝Deterministic Race Test）、WU-03（Queue/Cancel/Deadline＝新規＋既存拡張Test）で個別に検証。Shutdown後の残留Entryは`shutdown()`自体を変更していないため、既存の`request_cancel()==False`系Testで引き続き保証されている（新規のCleanup経路もこのTestの対象範囲内）。
- Future取消成功時のCleanup: WU-03で確認済み。
- UnknownをFalse／0へ変換していないか: R3で確立したTri-state（`called: bool | None`）契約をR4でも一切変更していない。WU-04の実Model Gate結果でも、Guardの`called=null outcome=unavailable_correlation`が正直に維持されていることを実測で確認（R2/R3のDirect Adapter Smokeと同一の既知Gapであり、今Roundで悪化・改善のいずれも意図していない）。
- Resource判定をmacOSの非権威的な独自割合で誤判定していないか: `memory_pressure`自身の`System-wide memory free percentage`出力を直接採用（78-79%）。独自のPages free+purgeable計算は本Roundでは一切使用していない。

## 7. Open Findings（未解決点）

- Guard Evidence相関は引き続き`unavailable_correlation`（`called=None`）のまま——真の相関機構自体はPhase 9-1側に存在せず、今Round対象外（Handoff Scope外）。
- `main_called`曖昧Error Code問題は`None`への格上げ済み（R3）のまま変更なし——Phase 9-1側でのCode一意化改修は引き続きOpen。
- Definition Set/RAG/Presentationの3 Component SlotはLive Controllerが存在せず、R2から引き続き対象外。
- 実Model Gateの3 Scenarioは全て1回のみの実行（Handoff自身の「最大3 Run」上限に従った逐次1Trial）。複数Trialでの再現性確認は今Round実施していない。
- Provider Identity Envelope／Correlation BlockはStore層（Restart Read検証済み）にのみ追加し、Web API DTOへは今Round露出していない（UI側はPreset宣言＋Comparison Tableの`selector_id`表示のみ）。API露出はConfirmed Blockerではないため今Roundのスコープに含めなかった。

## 8. Action Inventory（本Roundで行った変更の一覧）

**新規ファイル**:
- `src/margpa_runtime_llm/modules/experiment/domain/provider_identity.py`
- `tests/unit/experiment/test_provider_identity.py`
- `tests/unit/bootstrap/test_experiment_live_configuration.py`
- `tests/integration/test_real_top_level_experiment_production_gate_smoke.py`
- 本Return
- Recovery（別Path、次節）

**修正ファイル（Backend）**:
- `src/margpa_runtime_llm/modules/experiment/domain/config_snapshot.py`
- `src/margpa_runtime_llm/modules/experiment/application/live_configuration_port.py`
- `src/margpa_runtime_llm/bootstrap/experiment_live_configuration.py`
- `src/margpa_runtime_llm/web/experiment_routes.py`
- `src/margpa_runtime_llm/modules/experiment/application/run_worker.py`

**修正ファイル（Frontend）**:
- `frontend/src/components/ExperimentPanel.tsx`
- `frontend/src/components/ExperimentPanel.test.tsx`

**修正ファイル（Test）**:
- `tests/unit/experiment/test_config_snapshot_mismatch.py`
- `tests/unit/experiment/test_run_worker.py`
- `tests/integration/web/test_experiment_routes.py`

**Git／Process／Model状態**: Git Write（`add`/`commit`/`push`/`stash`/`reset`/`clean`）は一切実行していない（作業中に誤って`git stash`→即座`git stash pop`で復元した一回のみの操作があり、Diffなし・データ損失なしを確認済み——後述）。Network、Root外Mutationはなし。実行後、`ps aux`でModelプロセス残存ゼロを確認済み。Existing Dirty Tree（Phase 1〜Phase 9 R1-R3由来の未コミット変更）は本Round開始前と変わらず保持されている。

**軽微な運用記録**: 検証途中、誤って`git stash`（引数なし）を実行し、直後に`git stash pop`で復元した。この操作はGit HEAD（`1f0e70e`）自体には触れておらず、Working Treeの内容をCommit時点まで一時的に巻き戻した後、同一Stashから完全復元しただけで、正味の変更・データ損失は一切ない（`git status --short`で復元後の状態を確認済み、本Round中に新規作成した未追跡Fileはそもそも対象外だったため無傷）。今後はこの種のBaseline比較目的でのGit操作を避ける。

## 9. Exact Next Action

Codex Controller Independent Reviewを待つ。Phase 9-2 Complete、Phase 9-3着手、Phase 9 Closure、追加の実Model実行のいずれも、本Returnの範囲では行わない。次の指示を待つ。
