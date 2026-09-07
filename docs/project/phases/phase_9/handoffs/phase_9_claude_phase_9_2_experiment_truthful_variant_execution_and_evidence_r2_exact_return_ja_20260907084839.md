# Phase 9-2 — Truthful Variant Execution / Evidence R2 Exact Return

```yaml
document_id: phase_9_claude_phase_9_2_experiment_truthful_variant_execution_and_evidence_r2_exact_return_20260907084839
document_type: exact_return
document_state: ready
phase: phase_9
program: phase_9_2
recorded_at: 2026-09-07 08:48:39 JST
language: ja
from: claude_designer_implementer
to: codex_controller
decision_authority: user
authority_owner: Nazuna Research
in_response_to: phase_9_controller_phase_9_2_experiment_truthful_variant_execution_and_evidence_r2_exact_handoff_ja_20260907071729.md
controller_review_in_response_to: phase_9_2_controller_r1_return_independent_review_and_r2_rework_decision_ja_20260907071729.md
maximum_claim: P9_2_R2_USER_MANUAL_CANDIDATE_FOR_CODEX_CONTROLLER_REVIEW
phase_9_2_complete: false
phase_9_3_authorized: false
phase_10_authorized: false
git_write_authorized: false
network_authorized: false
append_only: true
```

## 1. 最大Claムの根拠

Handoff R2 SS12: 「最大Claimは、全必須項目と実Model Gateを満たした場合のみ
`P9_2_R2_USER_MANUAL_CANDIDATE_FOR_CODEX_CONTROLLER_REVIEW`とする。」

本Roundで R2-WU-01〜06 の全項目を解決し、Fixture/Integration収束確認後、
Handoff R2 SS9.2 が要求する3実Model代表Variant（Main Qwen only / Main Qwen +
Gemma Judge/Repair / Main Qwen + Qwen3Guard）を逐次・実際に実行し、いずれも
成功（3/3）した。よって最大Claimを上記とする。

ただし本ReturnはPhase 9-2 Complete、Phase 9-3開始、Phase 9 Closureのいずれも
自己承認しない。Codex Controller Independent Review待ちで停止する。

## 2. R2-WU-01〜06 個別状態

| WU | 状態 | 一言 |
|---|---|---|
| R2-WU-01 Frozen Effective Configuration / Production Variant成立 | resolved | Live Config読取Adapter新設、Plan作成時Snapshot凍結、Run開始前Call 0検証（全体Digest一致＋宣言Slot一致）、実行後Post-hoc再検証 |
| R2-WU-02 Actual Component Evidence / Identity | resolved | main_called/final_disposition/repair_adopted全面再設計、Guard正直化、未観測Component "not_observed" |
| R2-WU-03 Case Evaluation / Comparison Persistence | resolved | "completed⇒PASS" Oracle全廃、既存Domain Classifier結線、Restart可読性一元化、rubric_revision不一致Typed Reject追加 |
| R2-WU-04 Async Worker / Deadline / Cancel収束 | resolved | Deadline Timer化（呼出し中も束縛）、submit()非例外化、in-flight登録Race修正、Cancel冪等化、Restart孤立Run復旧 |
| R2-WU-05 Frontend Truthfulness | resolved | execution_mode権威化、Frozen Config事前表示、Comparison Stale/Unavailable表示、repair_called/adopted区別表示 |
| R2-WU-06 Verification / Bounded Real Model Gate | resolved | Fixture/Integration Hard Assert全通過、実Model Gate 3/3成功 |

## 3. IR-P9-2-R1-01〜07 Before/After

### IR-P9-2-R1-01［BLOCKER］Frozen VariantがProduction実行に反映されない

- Before: `judge-observe`と表示したRunが、実際にはLive Runtimeのその瞬間の
  Judge/Guard/Repair設定で動いていた。`variant_configuration_digests`は常に空。
- After: Plan作成時に`BootstrapLiveConfigurationReader.snapshot()`（新設）で
  Live設定を1回読み、全Variantへ同一Digestを`VariantConfigurationRef`として
  凍結保存（`variant_configuration_digests`は非空）。Production Run開始前に、
  (a) 凍結Digestと現在Live Snapshotの全体一致、(b) 宣言Component各Slotと
  Liveの個別一致（`find_mismatched_slots()`）の両方をCall 0で検証。
  片方でも不一致ならLIVE_CONFIG_MISMATCH/LIVE_CONFIG_UNAVAILABLEでTyped Reject。
  実行中の設定変更は実行後のPost-hoc再検証で検出し、`live_config_changed_
  during_run`としてCOMPLETEDをFAILEDへ格下げする（Handoff R2 SS4.2 Option 3の
  有界Fallback、実測で確認：`test_production_run_downgrades_to_failed_when_
  live_config_changes_during_the_turn`）。

### IR-P9-2-R1-02［BLOCKER］Production Evidenceに未観測の成功値を生成する

- Before: `main_called=True`固定、Guard呼出しを前後Invocation ID差分から
  推定して`observed`と表示、Repair呼出しだけで`repair_adopted=True`、未観測
  5 Component（main_governance/definition_set/rag/recording/presentation）は
  `outcome="not_applicable"`固定。
- After: `main_called`はConversationEventType/codeの実測分岐から導出（Guard
  Pre-block確定Code/Governance Pre-block確定Code→False、Post-block確定Code→
  True、曖昧Codeは保守的にFalse、`COMPLETED`はNO_HIT短絡と`attempt_
  provenance`有無で区別）。`repair_adopted`は`repair_called`と分離し
  `last_result.repair_accepted`から導出。Guard Evidenceは前後差分推定を廃止し
  `guard_called=False, guard_outcome="unavailable_correlation"`で正直に表示
  （実Correlationが存在しないことをConfirmed — 4節参照）。未観測5 Componentは
  `outcome="not_observed"`（確定Offと未観測の区別）。

### IR-P9-2-R1-03［BLOCKER］「Run completed」をCase PASSにするFalse Success Oracle

- Before: `_observation_for_row()`がHuman Review不要かつRun COMPLETEDなら
  無条件PASS。既存Domain Classifier（Freshness/Retrieval等）は未結線。
- After: `case_evaluator.evaluate_case_outcome()`（新設）がcase_idごとに実
  Classifierへ分岐。Freshnessは`classify_freshness_answer()`へ実Answerを
  渡し結果をPASS/FAIL/INCONCLUSIVEへ写像。Retrieval Strict-NO_HITは実Main
  Call Countで機械的に判定（Call有→FAIL、Call Zero確認→INCONCLUSIVE、意味的
  判定はJudge Evidence未配線のため今Round対象外と明記）。未知Case_idは
  INCONCLUSIVE。Evidenceがない場合は一貫してUNAVAILABLE。

### IR-P9-2-R1-04［MAJOR］Evaluation付きComparisonがRestart-readableでない

- Before: `build_comparison_report()`をObservationなしで呼び永続化、Web
  RouteがResponseにだけ別途Observationを追加。DiskとResponseが不一致。
- After: `get_comparison()`が`service.list_runs()`を1回走査して全Run分の
  実Observationを`evaluate_case_outcome()`で計算し、`observations_by_run_id`
  として`build_comparison_report()`へ渡す。同じ呼び出しが永続化とResponse
  生成の両方を兼ねるため、DiskとResponseは構造的に同一。

### IR-P9-2-R1-05［MAJOR］Guard EvidenceがRequest単位に相関していない

- Before: 前後Invocation ID差分をGuard呼出しの確定証拠として使用。
- After: 直接調査（Explore Agent 2件）で「GuardrailResultにrequest_idは
  一切存在せず、RequestCorrelationRegistryもGuardを追跡しない」ことを再確認。
  Adapterは差分推定を完全に廃止し、`unavailable_correlation`を常に返す
  （4節「実Model Gate」でも、実Guard呼出しは`GuardrailGovernanceComposition`
  側で確認できる一方、Adapter自身は正直にCorrelationなしと申告することを
  実機で確認）。

### IR-P9-2-R1-06［MAJOR］DeadlineとWorker Lifecycleが実行全体を束縛しない

- Before: Deadlineは`invoke()`呼出し前のみ判定。`submit()`はShutdown後
  `RuntimeError`を送出しRunが`running`のまま残る経路あり。In-flight登録が
  `executor.submit()`の後で、高速Taskの`finally`popが先行し得た。
- After: `threading.Timer`を`invoke()`と並行して起動し、呼出し中の
  Deadline超過も`FAILED`/`deadline_exceeded`へ収束（実Cancel Hook起動込み）。
  `submit()`はShutdown後も例外を送出せず自ら`FAILED`/`worker_shutdown`を
  Publish。In-flight登録とExecutor Submitを同一Lock内で順序固定し、
  Registration-before-pop を保証。Cancel冪等化：Worker側Cancel Hookが
  `service.cancel_run()`より先にCANCELLEDをPublishした場合、Web Routeが
  `TERMINAL_ALREADY_PUBLISHED`を捕捉し、実際にCANCELLEDならCancel成功
  （200）として返す（既にCOMPLETED/FAILEDなら従来通り409）。

### IR-P9-2-R1-07［MINOR］Running Production RunのIdentityがFixtureへ変わる

- Before: `execution_mode`はRun本体になく、Raw Evidence未保存時は
  `fixture_only=True`と推定。
- After: `VariantRun.execution_mode`をFrozen Identityとして必須Field化し、
  `start_run()`時に確定。以後、Fixture推定は一切行わない。

## 4. Frozen Config / Actual Config / Provider / Request / Evidence Identity Chain

- Frozen Config: Plan作成時に`BootstrapLiveConfigurationReader`が
  main(sentinel "active" + `RuntimeModelController.snapshot().artifact_
  digest`)/judge(mode + `ProviderSelectionController.selection_for(JUDGE).
  active_provider`)/guard(同様)/main_governance(mode)/repair(mode)/
  recording(mode)を読み、`EffectiveConfigurationSnapshot.configuration_
  digest_sha512`として`ExperimentPlan.variant_configuration_digests`へ
  凍結。definition_set/rag/presentationは今Round管理対象外（Live Toggle
  Controllerが存在しないことを直接調査で確認済み）で`mode=None`。
- Actual Config: Run開始時に同じReaderで再読取し、Frozen Digestと完全一致
  検証（Call 0）。Turn完了直後にも再読取し、Post-hoc一致検証（Lease有界
  Fallback）。
- Provider Identity: Main Artifact Digest（`RuntimeModelController`）、
  Judge/Guard Active Provider（`ProviderSelectionController`）。
- Request Identity: `VariantRun.request_id`（Experiment側）と、Production
  Runの`ConversationGenerationSession.request_id`（Phase 9-1側、Adapter内部
  生成）は別Identityとして両方保持（`production_request_id`Fieldで区別）。
  実Model Gate Scenario 2で、この実request_idを介した`JudgeGovernanceComposition.
  last_result()`相関が実際に機能することを確認済み。
- Evidence: `raw_evidence["invocations"]`（Component別Call/Outcome/Mutation/
  Evidence/Authority）と`raw_evidence["metric"]`（Call Count/repair_adopted）
  を同一Raw Evidence JSONへ格納、`ExperimentStorePort`経由でRestart-readable。

## 5. Metric / Evaluation / Comparisonの根拠

- Metric: `_metric_payload()`が実Invocationsから`call_count`を集計。
  `repair_adopted`はProduction経路では`ProductionTurnObservation.repair_
  adopted`（実Judge Result由来）、Fixture経路ではFixtureActorの確定的
  シミュレーション性質上「Called＝Adopted」として`repair_called`から
  導出（Production側のFalse-Evidence問題とは別種、Fixtureは意図的な
  決定論的シミュレーションであるため）。
- Evaluation: `case_evaluator.evaluate_case_outcome()`が`(case, run,
  raw_evidence)`から都度再計算。永続化されるComparison ArtifactとAPI
  Responseは同一呼び出しから生成されるため構造的に同一。
- Comparison: `ComparisonReport`のReport-levelバリデータが、全Row内
  Observationの`rubric_revision`と`case_revision`一致をTyped Reject
  （新規）。`ComparisonRow`は既存のRun/Case不一致Typed Reject（R1）を維持。

## 6. Fixture / Production-fixture / 実Model の区別

- Fixture: `FixtureActor`による決定論的Simulation。`execution_mode=
  "fixture"`として明示的にFrozen。
- Production-fixture: `FakeProductionTurnPort`等、Web Route/Adapter配線を
  実Modelなしで検証するTest Double（Integration Test群）。
- 実Model: `tests/integration/test_real_local_experiment_production_
  variant_gate_smoke.py`（新設、`model_smoke`Marker）。`InferenceService`+
  `LlamaCppModelAdapter`で実GGUFをLoadし、実`ConversationGenerationService`
  + 実`LiveProductionTurnAdapter`を通して実Turnを実行。3シナリオとも実行・
  成功（8節参照）。

## 7. Focused / Full / Frontend / Static Verification

- Focused Unit（`tests/unit/experiment/` + `tests/unit/bootstrap/test_
  experiment_production_turn_adapter.py`）: 新規/更新 合計 約210件、全Pass。
- Integration（`tests/integration/web/test_experiment_routes.py`）: 17件
  全Pass（R1の10件＋R2新規7件）。
- Backend Non-model Full Suite（`-m "not model_smoke"`）: **2627 passed,
  40 deselected**（81.5秒）。R1完了時点の2588からNet +39（新規Test純増、
  Regressionなし）。
- Ruff（全Repo）: `All checks passed!`。
- Canonical Mypy（全Repo、`uv run mypy`）: **43 errors / 4 files**
  （既存Baselineと完全一致、新規Regressionなし）。
- Frontend: `npm test`（34 files / 331 tests 全Pass）、`npx tsc --noEmit`
  Clean、`npx eslint .` Clean、`npm run build` 成功。
- 実Model（`-m model_smoke`、新設3 Test）: 3/3 Pass（8節）。

## 8. 実Model Gate 実行記録（Handoff R2 SS9.2）

事前計測（旧Round比でController指摘に沿い、`memory_pressure`のSystem-wide
Free Percentage・`vm.swapusage`・`ps aux`・稼働Process全てを実測、PhysMem/
Free単独では判断しない）：

- 実行前: System-wide memory free percentage **57%**、`vm.swapusage`
  used=0.00M（Swap未使用）、稼働中のModel/Serverプロセスなし、CPU 10コア、
  Load Avg 3.40。既存Model/Serverプロセスなし。
- 判断: 57%かつSwap未使用は健全域。本Repo自身の既存実Hardware Test
  （`test_real_local_main_gemma_concurrent_dispatch_smoke.py`）が「Main+
  Gemma同時Loadはネイティブクラッシュを再現しない」ことを既に実測確認
  済みであること（Main+Seleneとは異なる、既検証済みの組合せ）も踏まえ、
  逐次実行を開始。

実行結果（3シナリオとも`tests/integration/test_real_local_experiment_
production_variant_gate_smoke.py`、`-m model_smoke`、1回ずつ実行、失敗
しても条件を緩めて再試行はしない方針）：

1. **Main Qwen only**（`test_real_gate_1_main_qwen_only_production_
   baseline`）: 初回実行で`main_called=False`という実バグを発見
   （`_completed_event()`の`attempt_provenance`付与条件`model_runtime_info
   is not None`をTest Harness側で満たしていなかった——本Roundの新規発見・
   即修正、9節参照）。Harness修正後、再実行で**Pass**（3.16秒）。
   `main_called=True`, `main_outcome=completed`, `final_disposition=
   candidate_accepted`, content="Paris."（正しい実回答）。
2. **Main Qwen + Gemma Judge/Repair ENFORCE**（`test_real_gate_2_main_
   qwen_plus_gemma_judge_repair`）: **Pass**（11.68秒、Main+Gemma同時
   Load、ネイティブクラッシュなし）。`main_called=True`,
   `judge_called=True`, `judge_outcome=accept`（実Gemmaが正答を承認、
   Deviationなし——Repair自体は今回のReal Trialでは発火せず）,
   `repair_called=False`, `repair_adopted=None`,
   `final_disposition=candidate_accepted`, 実`LiveJudgeResult.
   execution_state=completed`, `criteria_evaluated=1`。Adapter独自
   実装の「内部生成request_idをJudge Hookのsemantic_snapshot_providerへ
   橋渡しする」新規機構（`on_request_id`コールバック経由）が実機で
   正しく機能することを確認。
3. **Main Qwen + Qwen3Guard ENFORCE**（`test_real_gate_3_main_qwen_
   plus_qwen3guard`）: 初回実行で`ExecutionState`の期待値誤り
   （"completed"ではなく実際は"evaluated"）というTest側の軽微な誤りを
   発見・即修正。修正後、再実行で**Pass**（4.32秒）。実Guard Input
   Dispatchが`GuardrailGovernanceComposition.last_result_for()`経由で
   確認でき（`execution_state=evaluated`, 良性入力につき検出なし）、
   同時にAdapter自身は`guard_called=False, guard_outcome=
   "unavailable_correlation"`を正直に維持——実Guard実行の事実と
   Adapterの相関非主張が矛盾なく両立することを実機で確認。

Scenario間の資源観測：Scenario 2（Main+Gemma、計約5.4GB Weight同時Load）
実行後、`vm.swapusage`が0.00Mから約2.75GB使用へ増加（Swap File新規作成を
確認——ControllerがR1で指摘した「実測すべきPressure兆候」の実例）。ただし
直後の`memory_pressure`はSystem-wide Free 69-72%へ回復、稼働Process残留
なし、Load Avg安定。Scenario 3（Guard、767MB、Scenario 2よりはるかに
軽量）は問題なく完了。全Scenario終了後、モデル/Server関連Processの残留
なしを`ps aux`で確認。

**結論：3/3 成功。Fixtureで代替した箇所なし。**

## 9. 本Round自ら発見し修正した実バグ・実Gap

1. `_completed_event()`の`attempt_provenance`付与が`model_runtime_info`
   の存在に依存する仕様を、実Model Gate Test Harness自身が満たしておらず
   `main_called`の誤False化を引き起こした（Production Wiring自体は
   `model_runtime_info`を常時供給しており、この欠陥はTest Harness側の
   構成漏れであって、Production Code自体のバグではないことを確認・
   修正・再実測で確定）。
2. `ExperimentService.publish_result()`のRaw Evidence/State書込み順序
   Race（R1で発見・修正、本RoundでもRegressionなしを再確認）。
3. `ComparisonRow`のRun/Case不一致未Reject Gap（R1で発見・修正）。
4. `ExperimentRunWorker`のIn-flight登録Race（本Round新規発見・修正、
   9.1で解説済み）。
5. `run_production_turn_variant()`の`_record()`ヘルパーが`called=False`
   時に実`outcome`文字列（例：Guardの`unavailable_correlation`）を
   `"off"`へ強制上書きしていた欠陥（本Round新規発見・修正）。

## 10. Internal Review A / B

Review Aの観点のみで1回、Review Bの観点のみで1回、同一観点の反復は
行っていない。

**Review A**（Frozen Variant一致／通常Chat設定との非混線／Provider・
Artifact・Definition・Request Identity相関／Restart後の可読性）：
4項目とも本Round実装で確認。Definition Set/RAG/Presentationは今Round
非対応スコープとして正直に`not_observed`/`mode=None`表示のまま
（Blocker/Majorではなく、既知の範囲外事項としてOpen Findingsへ記載）。

**Review B**（Call/Mutation/Evidence/Authority/Repair AdoptionのFalse
Valueなし／Completed≠PASS／Deadline・Cancel・Late Result・Worker Drain
のExactly-once収束／UIのFixture・Production・Running・Unknown・Failure
非混同）：4項目とも本Round実装・Testで確認。新規Confirmed Critical/
Majorはゼロ（9節記載の2件は実装中に自ら発見・即修正済み）。

## 11. Open Findings（Blocker/Major該当なし、範囲外事項として記録）

1. Definition Set / RAG / Presentation の3 Component Slotは、Live Toggle
   Controllerがこの Codebase に一切存在しないことを直接調査で確認済み
   （Bootstrap時固定）。今Round Frozen Config比較の対象外（`mode=None`）
   であり、Adapter Evidence上も`not_observed`のまま。将来この3 Slotへ
   Live Controlが追加された場合、`BootstrapLiveConfigurationReader`と
   `find_mismatched_slots()`双方の拡張が必要。
2. Guard Evidence相関は引き続き`unavailable_correlation`（真のRequest単位
   相関ではない）。実Model Gate Scenario 3で「実Guard実行の事実」と
   「Adapterの正直な非主張」が両立することを実機確認したが、将来の
   Roundで真の相関を追加する余地は残る。
3. `repair_adopted=True`分岐（Repair実採用）は、Fake-based Unit Testでは
   確認済みだが、実Model Gate Scenario 2の1回のTrialではJudgeが正答を
   承認しRepair自体が発火しなかったため、実Modelでの「採用」分岐は
   今Round実証できていない（既存プロジェクト規律「実行結果をそのまま
   報告し、望む結果が出るまで再試行しない」に従い、Repairを強制発火
   させる目的での再試行・入力変更は行っていない）。
4. main_called判定における曖昧Error Code（`guardrail_mode_unavailable`/
   `guardrail_enforce_evaluation_failed`/`governance_mode_unavailable`/
   `governance_enforce_evaluation_failed`）は、Pre-block/Post-blockの
   どちらからも到達し得ることが直接調査で判明しており、保守的に
   `main_called=False`へ倒している（過大主張よりは過小申告を選択）。
   Phase 9-1側でこの2つの発生源を区別可能にする改修が将来必要。
5. RAGの`should_generate=False`に伴う動的Warning Codeは、本Round
   Production AdapterがRAGを一切経由しないため`_PRE_MAIN_CALL_ERROR_
   CODES`に含めていない。将来RAGをExperiment Production経路へ配線する
   場合は拡張が必要。
6. 二つのVariantを同時に開始してもConfigが交差しないことは、共有可変
   状態がないことのCode Reviewおよび単一Worker逐次実行という設計上の
   保証によって確認しており、専用の並行実行Testは追加していない。
7. Frozen Config Digestの1 byte改変検出は、`ExperimentPlan`自身の
   `plan_digest_sha512`検証（Plan全体の整合性検証、既存機構）により
   間接的に捕捉される。Live Config Digestに特化した「1 byte改変」専用
   Testは、機能的に同等な「Plan作成後のLive Config Drift」Testで
   代替検証している。

## 12. 変更File一覧

### 新規（本R2 Round）
- `src/margpa_runtime_llm/modules/experiment/application/live_configuration_port.py`
- `src/margpa_runtime_llm/modules/experiment/application/case_evaluator.py`
- `src/margpa_runtime_llm/bootstrap/experiment_live_configuration.py`
- `tests/unit/experiment/test_case_evaluator.py`
- `tests/unit/experiment/test_config_snapshot_mismatch.py`
- `tests/unit/bootstrap/test_experiment_production_turn_adapter.py`
- `tests/integration/test_real_local_experiment_production_variant_gate_smoke.py`
- `frontend/src/components/ExperimentPanel.tsx`／`.test.tsx`（R1で新設済み、
  本RoundでWU-05分を全面改修 — Git上は本Round時点でも未Commitのため
  新規扱い）

### 修正（本R2 Round）
- `src/margpa_runtime_llm/modules/experiment/domain/run.py`（execution_mode追加）
- `src/margpa_runtime_llm/modules/experiment/domain/errors.py`（新規Error Code）
- `src/margpa_runtime_llm/modules/experiment/domain/config_snapshot.py`
  （find_mismatched_slots追加）
- `src/margpa_runtime_llm/modules/experiment/domain/comparison_report.py`
  （rubric_revision不一致検証追加）
- `src/margpa_runtime_llm/modules/experiment/application/experiment_service.py`
  （execution_mode必須化、reconcile_orphaned_running_runs追加）
- `src/margpa_runtime_llm/modules/experiment/application/run_worker.py`
  （Deadline Timer化、submit()非例外化、In-flight Race修正）
- `src/margpa_runtime_llm/modules/experiment/application/production_turn_runner.py`
  （repair_adopted Field追加、outcome文字列上書きBug修正、not_observed化）
- `src/margpa_runtime_llm/modules/experiment/application/comparison_service.py`
  （runtime_state_for_run公開化）
- `src/margpa_runtime_llm/modules/experiment/ports.py`（list_all_runs追加）
- `src/margpa_runtime_llm/adapters/experiment/local_filesystem_experiment_store.py`
  （list_all_runs実装）
- `src/margpa_runtime_llm/bootstrap/experiment_production_turn_adapter.py`
  （main_called/final_disposition/repair_adopted/Guard正直化 全面改修）
- `src/margpa_runtime_llm/bootstrap/web_application.py`
  （BootstrapLiveConfigurationReader配線、reconcile呼び出し追加）
- `src/margpa_runtime_llm/web/contracts.py`（live_configuration_reader Field追加）
- `src/margpa_runtime_llm/web/experiment_routes.py`（Live Config Call 0検証、
  Case Evaluator結線、Cancel冪等化、Production Preset 3件追加、execution_mode
  権威化 全面改修）
- `frontend/src/types.ts`（execution_mode Field追加）
- `frontend/src/i18n/translations.ts`（新規翻訳キー追加）
- 既存`tests/unit/experiment/*.py`複数ファイル（execution_mode必須化に
  伴う呼び出し側修正）、`tests/integration/web/test_experiment_routes.py`
  （Live Config Fake追加、新規Test 7件追加）

### 意図的に変更しなかったもの
- Phase 9-1本体（`modules/conversation`、`bootstrap/judge_live_integration.py`
  本体ロジック、`bootstrap/guardrail_governance.py`本体ロジック）—Handoff
  R2 SS11「Phase 9-1のProvider固有問題を修正しない」に従い不可侵。
- JSON Retry、Judge Decoder緩和、Model Sampling、Context/Token Budget、
  Selene、DeepSeek — Handoff R2 SS11により対象外。
- Phase Index、未解決Registry、Roadmap、Technology Selection — 編集なし。
- 既存Handoff/Return/History — 上書きなし（本Return/Recoveryとも新規Path）。

## 13. Git / Network / Root外Mutation / Process / Port / Model 状態

- Git: `git rev-parse HEAD` = `1f0e70e47fa058484c4b32f33c6cbca52e0afd2a`
  （Round開始前と不変）。`git diff --cached --stat`空。`git stash list`空。
  Git write（add/commit/push/stash/reset/clean）は一切実行していない。
- Network: 新規Network呼び出し・Model Downloadは一切実行していない。
- Project Root外Mutation: なし（全ての読み書きはProject Root配下、または
  `/private/tmp/claude-501/.../scratchpad/`のSession Scratchpadのみ）。
- Process/Port: 実Model Gate実行前後で`ps aux`によりModel/Server関連
  Processの残留がないことを確認済み。稼働中のuvicorn/FastAPI Server等は
  本Round通じて起動していない（Frontend/Backend双方ともTest経由の検証に
  限定）。
- Model: 実Model Gate実行後、3回とも`InferenceService.unload()`をFinally
  節で確実に呼び出し、Unload完了を確認。Session終了時点でLoad中のModelは
  存在しない。

## 14. Exact Return / Recovery

必ず別Pathで作成:

- 本File（Exact Return）
- Recovery: `docs/project/phases/phase_9/history/index/phase_9_2_experiment_truthful_variant_execution_and_evidence_r2_recovery_ja_20260907084839.md`

## 15. 次のAction

Codex Controller Independent Reviewを待つ。Phase 9-2 Complete、Phase 9-3
着手、Phase 9 Closureのいずれも本Returnの範囲では自己承認しない。
