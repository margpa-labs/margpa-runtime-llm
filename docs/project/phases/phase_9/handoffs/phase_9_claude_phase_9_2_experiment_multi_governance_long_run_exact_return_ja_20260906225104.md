# Phase 9-2 — Experiment/Multi-Governance Long Run Exact Return

```yaml
document_id: phase_9_claude_phase_9_2_experiment_multi_governance_long_run_exact_return_20260906225104
document_type: exact_return_handoff
document_state: ready
phase: phase_9
program: phase_9_2
recorded_at: 2026-09-06 22:51:04 JST
language: ja
from: claude_code
to: codex_controller
decision_authority: user
authority_owner: Nazuna Research
in_response_to:
  - phase_9_controller_phase_9_2_experiment_multi_governance_long_run_exact_handoff_ja_20260906212349.md
  - phase_9_2_experiment_multi_governance_execution_design_and_work_breakdown_ja.md
phase_9_2_closure_authorized: false
phase_9_3_authorized: false
phase_10_authorized: false
git_write: none
append_only: true
```

## 1. 最大Claim

`P9_2_USER_MANUAL_CANDIDATE_FOR_CODEX_CONTROLLER_REVIEW`

Handoffが指定したP9-2-AからP9-2-Fまでを依存順で実装した。P9-2-A〜Eは完全に実装・検証済み(`resolved`)。P9-2-Fは、Comparison Report・Fixture Matrix→Acceptance Mapping・Internal Review A/Bを完了したが、F3(実Model Gate)は意図的に今Round未実行(`not_run`、詳細は§3・§9)。Phase 9-2 Complete、Phase 9-3開始、Phase 9 Closureのいずれも主張しない。

## 2. 対象範囲(Scope Boundary遵守の確認)

- Phase 9-1で回復したComponent疎結合(Component OFF/不在/Unsupported時のCall/Mutation/Evidence/Authority 0)を、既存Componentの内部契約を一切変更せず、新しいResearch層(`modules/experiment/`)としてのみ実装した。既存の`judge_live_integration.py`、`guardrail_governance`、`runtime_governance`、`repair_live_integration.py`等の内部Dispatch/Decode/Failure-mapping/Provider Lifecycle自体は無変更(`web_application.py`への追加は新規`experiment_service`変数の構築ブロックのみ)。
- Existing Dirty Working Tree(前Round群からの多数の未commit変更・未追跡実機Test File)は一切触れていない。`git status --porcelain`は本Round開始前後で自分が作成/編集したFileのみを`M`/`??`として示すことを確認した。
- Selene・DeepSeek Judgeは一切実行していない(Fixture上でも実Model上でも参照コードを書いていない)。
- Network、Model Download、Package Installは一切行っていない。
- Phase Index、現行未解決Registry、Roadmap、Technology Selectionは無編集。
- 既存Handoff/Return/Historyは無編集。本Returnと対になるRecovery Indexは、いずれも新規Pathで作成する。
- Git write操作(`add`/`commit`/`push`/`stash`/`reset`)は一切実行していない。実行したGit操作は`git status --porcelain`/`git diff --cached`(状態確認のみ)。

## 3. 各WUの状態

| WU | 状態 | 一言 |
|---|---|---|
| P9-2-A Experiment Core | `resolved` | Identity/Plan/Config Snapshot/Lifecycle/Persistence/Minimal APIを実装・検証済み |
| P9-2-B Evaluation Core | `resolved` | Case Manifest/Metric/Evaluator Identity分離/Baseline-Regression-Ablation単一要因検証を実装・検証済み |
| P9-2-C Variant Composition | `resolved` | Actor Port/Composition Runner/Independence Matrix/Conflict-Routing/Isolationを実装・検証済み |
| P9-2-D Semantic Research Case Pack | `resolved` | Freshness/Retrieval Grounding/Belief Revision/False Improvementの分類関数とNeutral Case Packを実装・検証済み |
| P9-2-E Trace/Presentation/Minimal UI | `resolved` | Model Call 0 Trace/Strict Buffer/Progressive Presentationの契約、および実際に動くBackend Route＋Frontend Panelを実装・検証済み |
| P9-2-F Comparison/Verification/Review | `partial` | F1 Comparison Report・F2 Fixture Matrix→Acceptance Mapping・F4 Internal Review A/Bは完了。F3(実Model Gate)は今Round意図的に`not_run`(§9) |

## 4. Before/After Product Behavior

### Before

Phase 9-2着手前、Main/Judge/Guard/Governance/RAG/Repair/Recording/Presentationの構成差を比較するための独立したExperiment Identity、Persistence、Composition機構は存在しなかった。比較を行うには、都度Feature Modes API(`/api/v5/feature-modes`)を手動で切り替え、実Chatを1件ずつ試すしかなかった(Phase 9-1のUser Mac実画面Recheckが実際にそうしていた)。

### After

- 新規`modules/experiment/`が、Model/Provider/GD固有Schemaを一切Hard-codeしない汎用Research Coreとして、Experiment/Plan/Variant/Run Identityを分離管理する。
- `ExperimentService`(Filesystem Persistence)がPlan作成・Run開始・状態取得・Cancel・結果取得のVersioned APIを提供し、同一RunのTerminal結果二重Publish、Stale Generationからの遅延結果を確実にTyped Rejectする。
- `run_variant()`(Composition Runner)が、Component OFF/不在/Unsupportedの場合に当該ComponentのActorを一度も呼ばないことをHard Assert可能な形で実装されており、Independence Matrixとして機械検証済み。
- Freshness/RAG Grounding/Strict NO_HIT/Belief Revision/False Improvementの各分類が、Neutral(ALPHA/BETA式)なFixture Case Packとして再現可能になった。
- Model Call 0が発生した場合、`call_zero_reason`を伴わない`call_count=0`はContract自体がTyped Rejectするため、"表示文言だけの捏造"が構造的に起こり得ない。
- Strict Buffer/Progressive Presentationが型で分離され、Progressiveの状態遷移は一方向・非repeat・非backwardのみ許可される。
- 実際に動くMinimal UI(`/api/v7/experiment`のBackend Route＋`ExperimentPanel.tsx`)が、Preset Case選択・Variant選択・実行・比較表・詳細Evidence表示を提供する。この画面のRunは全てFixture Actor限定であり、実Main/Judge/Guard/Repair/Model Callを一切発生させない(UI上に明記)。

## 5. Files Changed / Deliberately Not Changed

### 新規作成(Backend)

```text
src/margpa_runtime_llm/modules/experiment/__init__.py
src/margpa_runtime_llm/modules/experiment/ports.py
src/margpa_runtime_llm/modules/experiment/domain/__init__.py
src/margpa_runtime_llm/modules/experiment/domain/errors.py
src/margpa_runtime_llm/modules/experiment/domain/canonical.py
src/margpa_runtime_llm/modules/experiment/domain/identity.py
src/margpa_runtime_llm/modules/experiment/domain/config_snapshot.py
src/margpa_runtime_llm/modules/experiment/domain/run.py
src/margpa_runtime_llm/modules/experiment/domain/dataset.py
src/margpa_runtime_llm/modules/experiment/domain/evaluation.py
src/margpa_runtime_llm/modules/experiment/domain/comparison_declaration.py
src/margpa_runtime_llm/modules/experiment/domain/composition.py
src/margpa_runtime_llm/modules/experiment/domain/freshness.py
src/margpa_runtime_llm/modules/experiment/domain/retrieval_case.py
src/margpa_runtime_llm/modules/experiment/domain/belief_revision.py
src/margpa_runtime_llm/modules/experiment/domain/false_improvement.py
src/margpa_runtime_llm/modules/experiment/domain/case_pack.py
src/margpa_runtime_llm/modules/experiment/domain/trace.py
src/margpa_runtime_llm/modules/experiment/domain/presentation.py
src/margpa_runtime_llm/modules/experiment/domain/comparison_report.py
src/margpa_runtime_llm/modules/experiment/application/__init__.py
src/margpa_runtime_llm/modules/experiment/application/experiment_service.py
src/margpa_runtime_llm/modules/experiment/application/composition_runner.py
src/margpa_runtime_llm/modules/experiment/application/comparison_service.py
src/margpa_runtime_llm/adapters/experiment/__init__.py
src/margpa_runtime_llm/adapters/experiment/local_filesystem_experiment_store.py
src/margpa_runtime_llm/adapters/experiment/fixture_actor_adapters.py
src/margpa_runtime_llm/web/experiment_routes.py
```

### 新規作成(Test)

```text
tests/unit/experiment/__init__.py
tests/unit/experiment/test_experiment_identity_and_plan_contracts.py
tests/unit/experiment/test_experiment_config_snapshot.py
tests/unit/experiment/test_variant_run_lifecycle.py
tests/unit/experiment/test_local_filesystem_experiment_store.py
tests/unit/experiment/test_experiment_service.py
tests/unit/experiment/test_evaluation_case_manifest.py
tests/unit/experiment/test_evaluation_observations_and_evaluator_identity.py
tests/unit/experiment/test_comparison_declaration.py
tests/unit/experiment/test_composition_runner_independence_matrix.py
tests/unit/experiment/test_governance_composition_conflict_and_routing.py
tests/unit/experiment/test_variant_isolation.py
tests/unit/experiment/test_freshness_case.py
tests/unit/experiment/test_retrieval_case.py
tests/unit/experiment/test_belief_revision_and_false_improvement.py
tests/unit/experiment/test_case_pack.py
tests/unit/experiment/test_execution_trace.py
tests/unit/experiment/test_presentation.py
tests/unit/experiment/test_comparison_report.py
tests/unit/experiment/test_acceptance_mapping_p9_2.py
tests/integration/web/test_experiment_routes.py
```

### 新規作成(Frontend)

```text
frontend/src/components/ExperimentPanel.tsx
frontend/src/components/ExperimentPanel.test.tsx
```

### 変更(既存File、いずれも小さな追加のみ)

```text
src/margpa_runtime_llm/web/contracts.py
  -- WebRuntimeへ experiment_service: ExperimentService | None = None を追加。
src/margpa_runtime_llm/web/app.py
  -- ExperimentWebError用exception_handler登録、create_experiment_router()登録。
src/margpa_runtime_llm/bootstrap/web_application.py
  -- 既存の Recording Writer構築ブロック直後に、同じ runtime_data/persistent/<scope>/
     階層規約へ experiments/ サブディレクトリを追加し、ExperimentService(Local
     FilesystemExperimentStore)を構築する20行程度のブロックを追加。既存の
     Recording/Judge Evidence/Persistent Conversation構築ロジックは一切変更していない。
frontend/src/App.tsx
  -- experimentPanelOpen state追加、TopBarへonOpenExperiment、ExperimentPanel描画を追加。
frontend/src/components/TopBar.tsx
  -- onOpenExperiment propと切替Buttonを1つ追加。
frontend/src/types.ts / api/client.ts / i18n/translations.ts / styles/app.css
  -- Experiment*型、/api/v7/experiment向けFetch関数、ja/en翻訳Key、Panel用CSSを追加。
```

### 意図的に変更していないもの

- `judge_live_integration.py`、`repair_live_integration.py`、`guardrail_governance/*`、`runtime_governance/*`本体のDispatch/Decode/Failure-mapping/Provider Lifecycle。
- Main通常回答、Repair Candidate生成、Recording Envelope形式。
- 既存`web/*.py`の他Router(`feature_modes_routes.py`等)の実装。
- Settings/Sidebar/Main Chat/右Panelの既存構造(TopBarへのButton1個以外は無変更)。
- Phase 9-1で追加された実機Test File群、Existing Dirty Working Tree。

## 6. Acceptance Mapping

| Requirement/Acceptance | 主Package | 状態 | Evidence |
|---|---|---|---|
| P9-REQ-201/P9-ACC-039 | A | 成立 | `test_acceptance_mapping_p9_2.py::test_p9_req_201_p9_acc_039_experiment_run_request_and_digests_correlate` |
| P9-REQ-202/P9-ACC-040 | C | 成立 | 同File `test_p9_req_202_p9_acc_040_variant_composition_differs_on_the_same_case` |
| P9-REQ-203/P9-ACC-045 | B/F | 成立 | 同File `test_p9_req_203_p9_acc_045_baseline_regression_and_reviewer_kinds_never_conflated` |
| P9-REQ-204/P9-ACC-041 | C | 成立 | 同File `test_p9_req_204_p9_acc_041_multiple_definition_conflict_and_routing_compared` |
| P9-REQ-205〜207/P9-ACC-042〜043 | D | 成立 | 同File `test_p9_req_205_to_207_p9_acc_042_to_043_freshness_grounding_and_belief_revision` |
| P9-REQ-208 | E | 成立 | 同File `test_p9_req_208_strict_buffer_and_progressive_presentation_are_separated` |
| P9-REQ-209/P9-ACC-044 | E | 成立 | 同File `test_p9_req_209_p9_acc_044_manual_url_fail_closed_trace_shows_call_0` |

全行、Fixture/Deterministic Testで機械検証済み。実Model上での検証は§9の通り今Round対象外。

## 7. 検証結果(正確な数値)

### Focused Unit Test(`tests/unit/experiment/`)

`149 passed`(内訳: WU-A 54件、WU-B +19件=73件、WU-C +20件=93件、WU-D +27件=120件、WU-E +18件=138件、WU-F +11件=149件)。

### Integration Route Test(`tests/integration/web/test_experiment_routes.py`)

`5 passed`(Presets無効/有効、Plan→Run→List完全Lifecycle、未知Variant拒否、完了RunへのCancel拒否)。

### Backend Non-model Full Suite(1回、最終候補前として実行)

```text
pytest -m "not model_smoke"
2557 passed, 37 deselected in 82.24s
```

本Round追加分はPhase 9-2の新規Test 154件(149+5)。前Round終了時点の数値(2402 passed、前々Roundの記録)から単純加算すると2556になり、実測2557との差1件がある。この差の原因はPhase 9-1側の直近変更によるものと推定されるが、本Round開始前の状態を独立に再測定していないため断定しない。重要なのは新規Failureがゼロで、全件Passしていること。

### Ruff(Whole Repo)

```text
ruff check .
All checks passed!
```

### Canonical Mypy(Whole Repo)

```text
mypy src tests
Found 43 errors in 4 files
```

既存Baseline(`test_stream_guard.py`、`test_point_runtime.py`、`test_conversation_generation_guardrail_stream_integration.py`、`judge_live_integration.py:631`)と完全一致。新規Error 0件。

### Frontend Test/Typecheck/Lint/Build

```text
npm run test       -> Test Files 34 passed (34), Tests 330 passed (330)
npm run typecheck  -> (no output = success)
npm run lint       -> (no output = success)
npm run build      -> tsc --noEmit && vite build succeeded, dist written to
                       src/margpa_runtime_llm/web/static/{index.html,app.css,app.js}
```

新規Test 3件(`ExperimentPanel.test.tsx`)を含む。

### Sabotage-regression(検出力確認、いずれも復元後Byte一致を確認)

1. `run.py`の`validate_transition`(Terminal-already-publishedをInvalid-state-transitionへ縮退) → 10件Test失敗を確認。
2. `evaluation.py`の`_validate_human_identity_shape`(Human判定を強制True化) → 4件Test失敗を確認。
3. `composition_runner.py`の`run_variant`(OFF判定を無効化) → 4件Test失敗を確認。
4. `freshness.py`の`classify_freshness_answer`(Citation改変検知を無効化) → 1件Test失敗を確認。
5. `trace.py`の`TraceStageRecord`(Call Zero Reason必須化を無効化) → 1件Test失敗を確認。
6. `comparison_report.py`の`ComparisonRow._validate`(False Success拒否を無効化) → 1件Test失敗を確認。
7. `presentation.py`の`validate_progressive_sequence`(単調性検査を無効化) → 2件Test失敗を確認。

## 8. Review A/B Findingと修正有無

### Review A(Identity/Component疎結合/Authority/Variant Isolation/Persistence)

Confirmed Critical/Major/MVP Blockerは0件。

- Identity: Experiment/Run/Variant/Requestの4つのIDが常に別Fieldであることを確認(Contract Levelで強制)。
- Component疎結合: `run_variant()`のOFF/不在/Unsupported判定をSabotage-regressionで確認済み。
- Authority: `resolve_governance_composition()`の未登録Actor拒否を確認済み(Typed Reject、テスト済み)。
- Variant Isolation: Composition Runnerが呼び出しごとに独立した`VariantExecutionResult`を返すこと、Web Route層が`FixtureActor`Registryを呼び出しごとに新規生成すること(共有Module変数を持たない)を確認済み。
- Persistence: 正常系Restart(`ExperimentService`を同一Storeで再構築)後もPlan/Run/Raw Evidence/Comparisonを読めることをTest済み。加えて、Late-Result Generation機構は現行API経路(全結果が同期的にTerminalへ到達する)では`is_terminal`判定と重複するが、これはPhase 9-1由来の非同期Late Result拒否パターンを将来の実Actor Adapterのために保持した意図的な設計であり、Blockerではない。

**1件の非Blocker Open Finding**: `ComponentSelection.mode=None`(Selectionは存在するがModeが未設定)の場合、`run_variant()`は"OFF"ではなく"呼び出す"側に倒れる。この組合せを明示的にExerciseするTestは書いていない。具体的なFailure Scenarioが無いため今Roundでは修正せず、§9のOpen Findingsへ記録する。

### Review B(Metric Oracle/False Success/Freshness/Call 0/Strict-Progressive Truthfulness)

Confirmed Critical/Major/MVP Blockerは0件。

- Metric Oracle/False Success: `ComparisonRow`が非COMPLETED Runへの PASS Observation添付をTyped Rejectすることを確認済み(Sabotage-regressionで検出力確認済み)。`RunState -> RuntimeOutcomeState`の対応表は`PLANNED`/`RUNNING`を`NOT_RUN`にのみ写像し、`COMPLETED`以外を成功として扱わない。
- Freshness: `classify_freshness_answer()`のHistorical Citation改変検知をSabotage-regressionで確認済み。
- Call 0: `TraceStageRecord`のCall Zero Reason必須化をSabotage-regressionで確認済み。
- Strict/Progressive Truthfulness: `validate_progressive_sequence()`の単調性検査をSabotage-regressionで確認済み。Strict BufferがFinal以外のEventを一切emitできないことも既存Testで確認済み。

修正が必要なConfirmed Findingは0件だった。

## 9. Open Findings(Phase 9-2 Blockerではない)

1. **`ComponentSelection.mode=None`の呼び出し判定が未Exercise**(Review A由来、§8参照)。具体的なFailure Scenarioなし。Blockerではない。
2. **F3(実Model Gate)を今Round意図的に未実行**。設計書§11 F3・Handoff §6 F3は「Fixture／Static検証後だけに限り…最大3 Top-level Experiment Run、逐次実行して**よい**」という許可(Permissive)であり、義務ではない。実行するには、実Componentが独立Invokeできないという実システムの実態(Main/Judge/Guard/Repairは1つのTurnとして一体で動く、Fixtureのように個別Component単位でInvokeできない)に対応した、Fixture Independence Matrixとは別設計の"実Turn全体を1 Variant Runとして記録するAdapter"を新規に書き、実際に16GB Mac上で最大3回の実Model Loadを伴うRunを実行する必要がある。本Long Runは既にA〜Fの大半を実装・検証しており、この時点でさらに新規の実Adapterコードを書いて未検証のまま実機で走らせることは、Handoffの「新規Scope拡大禁止」および実機側の資源Riskとのバランスを考慮すると、今Round着手しない方が安全と判断した。この判断はUserへの追加確認なしに自律的に行った(Handoff「True Stop以外では途中確認を要求せず」に基づく)。次Round以降で対応可能。
3. **Selene/DeepSeek Judgeとの比較Case**は今Round未実装(Handoff・設計書の明示Scope外どおり)。
4. **`criteria_evaluated`のUnknown判定理由、Memory定量計測**(Phase 9-1由来の既知Open Finding)は本Roundでも対象外のまま。

## 10. Real Model実行回数

`0`回。§9-2の判断によりF3(実Model Gate)を実行していない。実行前後のProcess/Port確認も本Roundでは不要だった(実行していないため)。

## 11. Git/Network/Root外Mutation

- Git write(`add`/`commit`/`push`/`stash`/`reset`)は一切実行していない。実行したGit操作は`git status --porcelain`および`git diff --cached --stat`(状態確認のみ)。
- Network、Model Download、Package Installは一切行っていない。
- Project Root外への書き込みは行っていない(Sabotage-regressionのBackupは指定Scratchpad Directory配下)。
- Frontend Buildの出力先(`src/margpa_runtime_llm/web/static/`)はProject Root内の既存Build出力先そのものであり、新規外部Pathではない。

## 12. Codex ControllerのExact Next Action

1. 本ReturnとA〜F各WUの`resolved`/`partial`判定、Acceptance Mapping、Sabotage-regression結果、Review A/B Findingを確認する。
2. F3(実Model Gate)を今Round見送った判断(§9-2)の当否を判断する。次Round実行を指示する場合、実Turn全体を1 Variant Runとして扱う新規Adapter設計の承認、および実機Run回数上限(最大3)の再確認をお願いしたい。
3. Phase 9-2 Closure、Phase 9-3着手、追加Package、UI大改造のいずれも、本Returnの範囲では自己承認していない。次の指示を待つ。

本Returnで停止する。
