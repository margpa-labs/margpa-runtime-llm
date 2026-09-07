# Phase 9-2 — Experiment Live Composition／Evidence Convergence R1 Exact Return

```yaml
document_id: phase_9_claude_phase_9_2_experiment_live_composition_and_evidence_convergence_r1_exact_return_20260907032749
document_type: exact_return_handoff
document_state: ready_for_independent_review
phase: phase_9
program: phase_9_2
recorded_at: 2026-09-07 03:27:49 JST
language: ja
from: claude_designer_implementer
to: codex_controller
decision_authority: user
authority_owner: Nazuna Research
in_response_to: phase_9_controller_phase_9_2_experiment_live_composition_and_evidence_convergence_r1_exact_handoff_ja_20260907002521.md
maximum_claim: P9_2_R1_USER_MANUAL_CANDIDATE_FOR_CODEX_CONTROLLER_REVIEW
phase_9_2_closure_self_approved: false
phase_9_3_self_approved: false
phase_10_self_approved: false
git_write_performed: false
network_performed: false
root_outside_mutation_performed: false
append_only: true
```

## 1. Maximum Claim

`P9_2_R1_USER_MANUAL_CANDIDATE_FOR_CODEX_CONTROLLER_REVIEW` — R1-WU-01〜05は`resolved`。R1-WU-06はFixture／Integration Hard Assertまで`resolved`、実Model 3-Run Gateは測定Evidenceに基づき`true_stop_partial`（詳細は§9）。Phase 9-2 Complete／Phase 9-3開始／Phase 9 Closureは自己承認しない。Codex Controller Independent Review待ち。

## 2. R1-WU別状態

| WU | 状態 | 一言 |
|---|---|---|
| R1-WU-01 Identity/Case/Config Correlation | resolved | `ExperimentPlan`に`case_id`/`case_digest_sha512`/`VariantConfigurationRef`追加、`VariantRun.request_id`必須化 |
| R1-WU-02 Frozen Plan Execution/Invariant修正 | resolved | mode=None Call 0修正、Budget/Execution Order Runtime強制、Routeは`plan.variant()`のみ参照 |
| R1-WU-03 Production Turn Variant Adapter | resolved | 実`ConversationGenerationService`を1 Variant Runとして包む、Config Isolation Option 2 |
| R1-WU-04 Case Evaluation/Comparison結線 | resolved | Case Digest再検証、Comparison Report API/UI結線、Deterministic Metric Oracle |
| R1-WU-05 Async Lifecycle/Cancel/Failure | resolved | Tracked Worker、非同期202応答、実Cancel Hook、Actor例外→FAILED |
| R1-WU-06 Verification/Real Model Gate | partial | Fixture/Integration Hard Assert 全項目resolved。実Model 3-Run Gateはtrue_stop（§9） |

## 3. Before/After（IR-P9-2-01〜07 個別対応）

- **IR-P9-2-01（Fixture固定）**: `StartRunRequest.execution_mode`(`fixture`/`production`)を追加。`production_turn_adapter`が利用可能な場合、実`ConversationGenerationService`を1回実行する経路が実在する（`bootstrap/experiment_production_turn_adapter.py`）。
- **IR-P9-2-02（Case/Config/Run/Digest相関なし）**: `ExperimentPlan.case_id`/`case_digest_sha512`を追加(必須)。`VariantRun.request_id`を必須化。Web Routeは`request_id`を生成またはClient値を受理しResponse/Persistenceへ返す。
- **IR-P9-2-03（Live Presetを実行）**: `start_run`は`service.store.load_plan(...).variant(...)`のみを参照する。`_PRESET_VARIANTS`はPlan作成時のInputとしてのみ残る。回帰Test: `test_a_preset_change_after_plan_creation_never_affects_the_frozen_run`。
- **IR-P9-2-04（Comparison未結線）**: `GET /api/v7/experiment/experiments/{id}/comparison`を新設、`build_comparison_report()`を実際に呼ぶ。Frontend Comparison Tableに反映。
- **IR-P9-2-05（Case未使用）**: `_resolve_frozen_case()`がCase Pack実Contentから`case.input`を再導出し、Production Adapterへ渡す。Digest不一致はActor呼び出し前にTyped Reject。
- **IR-P9-2-06（Budget/Cancelが実Contractでない）**: `max_variant_runs`/`stop_policy`（Execution Order）は`ExperimentService.start_run()`で強制。`deadline_ms`は`ExperimentRunWorker`でActor呼び出し前にCall 0判定。Web Runは非同期化（202→Poll）。
- **IR-P9-2-07（mode=None がCall 1）**: `composition_runner.run_variant()`の判定を`selection.mode is None or selection.mode in _OFF_MODE_VALUES`に修正。Sabotage-regressionで検出力確認済み。

## 4. Files Changed

### 4.1 新規 (R1)
- `src/margpa_runtime_llm/modules/experiment/application/production_turn_runner.py`
- `src/margpa_runtime_llm/modules/experiment/application/run_worker.py`
- `src/margpa_runtime_llm/bootstrap/experiment_production_turn_adapter.py`
- `tests/unit/experiment/test_production_turn_runner.py`
- `tests/unit/experiment/test_run_worker.py`
- `tests/unit/experiment/test_r1_hard_assert_mapping.py`

### 4.2 修正 (R1)
- `src/margpa_runtime_llm/modules/experiment/domain/identity.py`（`case_id`/`case_digest_sha512`/`StopPolicy`/`VariantConfigurationRef`/Budget下限）
- `src/margpa_runtime_llm/modules/experiment/domain/run.py`（`request_id`必須化）
- `src/margpa_runtime_llm/modules/experiment/domain/dataset.py`（`compute_case_digest_sha512()`追加）
- `src/margpa_runtime_llm/modules/experiment/domain/errors.py`（新規Error Code 8件）
- `src/margpa_runtime_llm/modules/experiment/domain/comparison_report.py`（Run/Case不一致Reject追加）
- `src/margpa_runtime_llm/modules/experiment/application/composition_runner.py`（mode=None Call 0修正）
- `src/margpa_runtime_llm/modules/experiment/application/experiment_service.py`（Budget/Execution Order強制、publish_result書き込み順序修正）
- `src/margpa_runtime_llm/web/experiment_routes.py`（execution_mode、非同期202、Comparison Route、Case再検証）
- `src/margpa_runtime_llm/web/contracts.py`（`production_turn_adapter`/`experiment_run_worker`Field、`close()`順序）
- `src/margpa_runtime_llm/bootstrap/web_application.py`（両Fieldの実配線）
- `tests/unit/experiment/test_case_pack.py`／`test_local_filesystem_experiment_store.py`／`test_variant_run_lifecycle.py`／`test_experiment_identity_and_plan_contracts.py`／`test_experiment_service.py`／`test_comparison_report.py`／`test_acceptance_mapping_p9_2.py`／`test_composition_runner_independence_matrix.py`（新Field/Signature対応、新規Hard Assert Test追加）
- `tests/integration/web/test_experiment_routes.py`（非同期Flow対応、Production Mode Test 4件、Preset/Case改変Test 2件追加）
- `frontend/src/types.ts`／`api/client.ts`／`components/ExperimentPanel.tsx`／`components/ExperimentPanel.test.tsx`／`i18n/translations.ts`（execution_mode選択、Poll、Comparison表示）

### 4.3 変更なし（意図的）
- `src/margpa_runtime_llm/modules/experiment/application/comparison_service.py`（既存Logic流用のまま、Route側でObservationを構築）
- `src/margpa_runtime_llm/adapters/experiment/fixture_actor_adapters.py`／`local_filesystem_experiment_store.py`
- `src/margpa_runtime_llm/modules/experiment/domain/{composition,freshness,retrieval_case,belief_revision,false_improvement,trace,presentation,case_pack,evaluation,comparison_declaration,canonical}.py`
- Phase 9-1既存Production Composition（`modules/conversation/*`、`bootstrap/judge_live_integration.py`、`bootstrap/guardrail_governance.py`等）— 一切再実装せず読み取りのみ

## 5. Acceptance Mapping（R1 9.1 Hard Assert）

`tests/unit/experiment/test_r1_hard_assert_mapping.py`参照。

| # | 要求 | 状態 | 実Evidence |
|---|---|---|---|
| 1 | 同Revision異Case混同なし | resolved | `test_item_01_...` |
| 2 | Plan後Preset変更でもFrozen実行 | resolved | `test_a_preset_change_after_plan_creation_never_affects_the_frozen_run`(integration) |
| 3 | mode=None/OFF/Absent/UnsupportedはCall 0 | resolved | `test_item_03_...`、`test_a_present_component_with_mode_none_is_call_zero_never_called` |
| 4 | Case/Config/Plan Digest不一致はCall 0 | resolved(Case)／not_populated_this_round(Config) | `test_a_case_pack_content_change_after_plan_creation_rejects_the_run_before_any_call`。Config Digest不一致の「Live vs Frozen再検証」はConfig Snapshotが未配線のため今Round未実施(§9) |
| 5 | max_variant_runs/Deadline/StopPolicy/ExecutionOrder違反はCall 0 | resolved | `test_item_05_...`、`test_run_worker.py::test_an_exceeded_deadline_...` |
| 6 | Actor例外→FAILED、Cancel→CANCELLED、Late Publish拒否 | resolved | `test_item_06_...`、`test_run_worker.py`各Test |
| 7 | ComparisonがRun/Case/Observation不一致を拒否 | resolved | `test_item_07_...`、`test_comparison_report.py`新規2件 |
| 8 | Fixture/Productionの実Identityが残る | resolved | `test_a_production_run_completes_with_fixture_only_false`等 |
| 9 | Experiment不在時に通常Chat等へ影響0 | resolved | `test_item_09_...`(構造的Import禁止)＋既存2588-test回帰無変化 |
| 10 | UIはFixture ResultをReal表示しない | resolved | `test_item_10_...`、`ExperimentPanel.test.tsx`新規1件 |

## 6. Verification結果

- Focused Unit(`tests/unit/experiment/`): 185 passed。
- Integration(`tests/integration/web/test_experiment_routes.py`): 12 passed。
- Backend Non-model Full Suite: `2588 passed, 37 deselected`(81.4s)。
- Ruff(Whole Repo): `All checks passed!`。
- Canonical Mypy(Whole Repo): `43 errors/4 files`（既存Baseline完全一致、新規Error 0）。
- Frontend: `npm test`(34 files/331 tests全Pass、`NODE_OPTIONS=--no-webstorage`必須)、`tsc --noEmit`/`eslint .`/`npm run build`いずれも成功。
- Sabotage-regression 3件（今Round新規の最Critical機構が対象）:
  1. `ComparisonRow`のRun/Case不一致拒否 → 該当2 Test失敗確認 → 復元後Byte一致。
  2. `composition_runner.py`のmode=None Call 0修正 → 該当2 Test失敗確認 → 復元後Byte一致。
  3. `experiment_service.py`のmax_variant_runs強制 → 該当2 Test失敗確認 → 復元後Byte一致。

## 7. Fixture／Production-fixture／実Model Evidence

- **Fixture**: `tests/integration/web/test_experiment_routes.py::test_full_plan_run_and_list_lifecycle`が実HTTP経路でFixture Runを完走させ、Comparison Reportまで実際に取得している。
- **Production-fixture**（`FakeProductionTurnPort`によるRoute層の実結線検証、real Modelなし）: `test_a_production_run_completes_with_fixture_only_false`、`test_cancel_reaches_an_in_flight_production_run`、`test_start_run_rejects_production_mode_when_adapter_unavailable`。
- **実Model**: 0回。理由と測定根拠は§9参照。`LiveProductionTurnAdapter`自体は実`ConversationGenerationService`/`JudgeGovernanceComposition`/`GuardrailGovernanceComposition`に対して直接実装済みだが、今Roundでは実際に起動していない。

## 8. Internal Review

### Review A（Identity／Frozen Plan／Authority／Component Independence／Variant Isolation／Production Composition／Persistence）

- Identity: `ExperimentPlan`は`experiment_id`/`case_id`/`case_revision`/`case_digest_sha512`/Variant集合/Budgetの全内容から`plan_digest_sha512`を再計算し一致検証する。改ざん検知は既存の仕組みのまま拡張。
- Frozen Plan: Routeは`plan.variant()`のみを参照するよう修正済み。Preset変更後もFrozen Variantが実行されることを実HTTP Testで確認。
- Authority: Production Adapterは`ProviderSelectionController`/`JudgeModeController`/`GuardrailModeController`など既存の設定変更APIを一切呼ばない(Grep確認済み、`experiment_production_turn_adapter.py`は読み取りのみ)。
- Component Independence: Fixture Composition Runnerの独立性はmode=None修正後も既存Matrix Testで維持を確認。
- Variant Isolation: 既存のThreadPoolベースIsolation Testは無変更のまま全Pass。
- Production Composition: `LiveProductionTurnAdapter`は`conversation`/`judge_governance_composition`/`guardrail_governance_composition`をそのままBootstrapから受け取る同一Instanceであり、別Instanceを新設していない(Config Isolation Option 2として意図通り)。
- Persistence: `publish_result()`の書き込み順序Bug(state先書き)を発見し修正($4.2参照)。Restart-readabilityの既存Testは無変更のまま全Pass。

**Confirmed Findings**: なし(Blocker/Major新規なし)。上記Persistenceの発見は本Round内で即修正済み。

### Review B（Metric Oracle／Case参照整合／False Success／Call 0／Cancel-Late Result／Strict-Progressive／Comparison UI真実性）

- Metric Oracle: `_observation_for_row()`は`is_successful_runtime_state()`と`case.requires_human_review`のみから決定論的に導出し、Human Review未実施のCaseは`runtime_state=completed`でも`NOT_RUN`(未実施)として表示、PASSへ格上げしない。
- Case参照整合: `ComparisonRow`にRun/Case不一致Rejectを追加(§4.2)。
- False Success: 既存の`_validate_no_success_claim_on_non_completed_state`は無傷。新設したRun/Case不一致Rejectと共存を確認。
- Call 0: mode=None/Deadline/max_variant_runs/Execution Orderの4種、全てSabotage-regressionまたは専用Testで検証。
- Cancel/Late Result: `cancel_run()`→`Worker.request_cancel()`→`service.cancel_run()`の順で実行され、後着Publishは既存のGeneration機構でReject。実HTTP経路での検証済み(`test_cancel_reaches_an_in_flight_production_run`)。
- Strict/Progressive: 本Roundで無変更、既存Test全Pass。
- Comparison UI真実性: Frontend Comparison Tableは実際のMetric/Evaluation/Failureを表示し、Human Review未実施を専用文言で表示する。Fixture/Real Resultの開示文言はfixture_onlyの実値で切替(Test済み)。

**Confirmed Findings**: なし(Blocker/Major新規なし)。

## 9. Open Findings（実Model Gate True Stop、その他）

### 9.1 実Model Gate — True Stop（Partial）

Handoff R1 9.2は、User Manual Candidate前必須としてMain Qwen only／Main+Gemma Judge／Main+Qwen3Guardの代表3 Run実行を求めている。安全性確認のため実行直前にSystem State計測を行った。

```text
hw.memsize: 17179869184 (16 GiB)
PhysMem: 14G used (1687M wired, 3216M compressor), 1302M unused
vm.swapusage: used = 0.00M (Swap未使用、Swap Fileの余力は不明)
稼働Process: margpa/uvicorn/llama_cpp系プロセスなし(Clean)
```

このMacは、Nazuna Researchの通常作業(Claude Desktop、ChatGPT/Codexアプリ、Chrome、VS Code等)により、総16GiB中約14GiBが既に使用中で、名目上の空き容量は約1.3GiBのみであった。Swapは現在未使用である一方、実際の空き容量には強い余裕がない。

この状態でMain Qwen(約2.5GB)またはGemma／Qwen3Guardを`gpu_layers=-1`でLoadした場合、User自身が現在使用中の他Application(このClaude Desktop本体を含む)のMemory Page圧縮／退避が発生し、Userの実作業に体感できる遅延を与えるRiskが具体的な計測値として確認された。これはHandoff §13 True Stopの趣旨(実行前提の安全性を実測せず強行しない)、および§9.2自身の「Memory Pressureがあれば追加Runを止め、Partial／True Stopで返す」という明示的許可に該当すると判断し、実Model Gateの実行そのものを本Roundでは行わなかった。

- Production Adapter自体(`LiveProductionTurnAdapter`)は実装・単体Fake検証済みであり、Userが他Applicationを終了するなどして安全な空き容量を確保した上で、次Round以降に同一Codeで実行することを妨げるものではない。
- Selene／DeepSeek Judgeは(実行しない対象として)一切触れていない。
- Fixtureでの代替や、実行したという偽装は一切行っていない。

### 9.2 Config Digest不一致のRuntime再検証は未配線

`VariantConfigurationRef`／`CONFIG_DIGEST_UNKNOWN_VARIANT`Contract検証は実装済みだが、現在の`create_plan`route実装はEffective Configuration Snapshotを一切構築せず(`variant_configuration_digests`は常に空)、Runtime時点で「Live Config vs Frozen Config」の再検証を行う経路が存在しない。Production Adapter自体もOption 2設計(Live Configを読み取るのみ、強制しない)のため、今Roundでは実質的に比較対象となるFrozen Config自体が生成されない。Case Digestの再検証(`_resolve_frozen_case`)と対になる「Config Digest再検証」は、将来Configuration Snapshotの実配線を伴うRoundでの対応が必要。

### 9.3 Guard Evidence相関はrequest_id非依存

`GuardrailResult.invocation_id`はGuardrail Governance側で独立採番され、Turnの`request_id`と直接相関しない(`bootstrap/guardrail_governance.py`実装事実として確認)。`LiveProductionTurnAdapter`は「Turn開始前後でのInvocation ID変化」を検出Signalとして採用しているが、これは真の意味でのRequest単位相関ではなく、単一Turn逐次実行という利用規律の下でのみ正しく機能する近似である。Return内でも明記の通り、正確なGuard単位Correlationは今回のBoundaryを超える。

### 9.4 Rubric Revisionの簡略化

`_observation_for_row()`は`rubric_revision`として`case.revision`をそのまま用いている。専用のRubric概念は本Roundで新設していない、意図的な簡略化。

## 10. Action Inventory

- Git: `add`/`commit`/`push`/`stash`/`reset`/`clean`いずれも未実行(`git rev-parse HEAD`は Session開始時と同一`1f0e70e`)。
- Network: 未実行(実Model DownloadやAPI呼び出しなし)。
- Project Root外Mutation: 未実行(Filesystem書き込みは全て`tmp_path`Test Fixture、または本Repository配下の実Source/Test/Docs)。
- Model Load/Unload: 実行していない(§9.1)。稼働Process確認上もClean。
- 既存Handoff/Return/History: 上書きなし。本Returnと対になるRecoveryは別Pathで新規作成。

## 11. Exact Next Action

Codex Controller Independent Reviewを待つ。特に次の判断を仰ぐ:

1. §9.1の実Model Gate True Stop判断(現在の空きMemory不足を理由とする)の当否。
2. §9.2のConfig Digest再検証未配線を今Round許容するか、追加Reworkを要求するか。
3. Phase 9-2 User Manual Candidateとしての最終可否。

Phase 9-2 Complete、Phase 9-3着手、Phase 9 Closureのいずれも本Returnでは自己承認しない。
