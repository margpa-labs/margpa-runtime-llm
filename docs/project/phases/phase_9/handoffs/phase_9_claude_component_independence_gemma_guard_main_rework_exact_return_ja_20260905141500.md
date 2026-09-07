# Phase 9-1 — Component完全疎結合／Gemma／Guard／Main Rework Exact Return Handoff

```yaml
document_type: exact_return_handoff
document_state: candidate_for_controller_review
from: claude
to: codex_controller
in_response_to: ../handoffs/phase_9_controller_component_independence_gemma_guard_main_rework_exact_handoff_ja_20260905121655.md
git_action: none
network_action: none
external_artifact_mutation: none
closure_authority: none_requested
language: ja
recorded_at: 2026-09-05 14:15:00 JST
```

## 1. Maximum Claim

`P9_1_COMPONENT_INDEPENDENCE_WU01_AND_WU04_RESOLVED_WU02_REAL_EVIDENCE_ONLY_WU03_CONFIRMED_NONISSUE_WU05_CORE_RECONFIRMED`

**主張すること**:
- **WU-01(独立Turn Context境界)**: Main Governance OFF/不在でも、Dedicated Judge(Selene/Gemma形状)が`semantic_snapshot_unavailable`にならず独立してOBSERVE/ENFORCE実行できることを、Source修正・Sabotage-regression・Fixture Parameterize Matrix(26 Test)で確認した。**確定的に解決**。
- **WU-04(Cancellation起源分類とEvidence Identity契約)**: (a) `judge_run_evidence`の`model_identity`が独立Judge Run(Gemma等)で誤ってMain自身のIdentityになっていた実バグを修正した。(b) `cancelled_by_request`が、真因の異なるMain優先Preemptionを誤って同一Labelへ収束させていた実バグを、`ModelAccessCoordinator`の新規`consume_preemption()`機構で修正した。両方ともSabotage-regressionで検出力を証明済み。**確定的に解決**。
- **WU-02(Gemma通常初回Judge)**: Test-only Batch別Observabilityを追加し、実機1回のトライアルで実Evidenceを取得した。**「最初の8 Criterion Batchで停止する」という当初仮説はこのTrialのEvidenceによって反証された**(Batch 1・2は`finish_reason=STOP`で正常完了、Batch 3が`STOP`かつToken上限未到達のまま不完全JSON断片で失敗)。原因はToken不足/Truncateではなく、Gemma固有の間欠的なJSON形式Quirk(`judge_output_decoder.py`が既に文書化済みの既知挙動)と特定した。**修正は適用していない**――利用可能な是正手段(Decoder緩和/JSON補修/盲目的Retry/Budget再拡大)は全て今回の禁止事項に該当するか、別途の明示的許可が必要(Prompt変更やSampling固定)であり、根拠なく実施することは避けた。
- **WU-03(Qwen3Guard Mode非依存分類)**: Source Codeで、`Qwen3GuardGenAdapter.classify_point()`/`Qwen3GuardDetectorAdapter.detect()`双方ともModeを一切受け取らないことを確認した(構造的にMode非依存)。実機1回、同一Input/Target/Providerでの2回連続呼び出しにより、benign入力に対する分類結果が一致することを確認した(Detection非決定性の疑いは今回のTrialでは再現しなかった)。**確定的な非決定性が確認されなかったため、確定的Generation Parameter導入という修正は適用していない**(WU-03自身の"必要なら"という条件を満たさなかったため)。
- **WU-05(Main起点RepairのProduction成立)**: WU-01〜04適用後、既存のHook-直結Golden Path実機Test(`test_a_real_gemma_main_governance_enforce_run_authorizes_and_adopts_the_repair`)を実機1回再実行し、PASSを確認した——Main Governance ENFORCE・Judge Gemma ENFORCE・Judge側Repair OFFという構成で、Main自身のAuthorityが`repair_requested_by=main_governance`としてRepairを起動し、改善・採用まで到達することを再確認した。

**主張しないこと(明示的除外)**:
- WU-02は未解決のまま——Gemma通常初回Judgeの実用的な信頼性は今回のRework終了時点でも確立されていない。
- WU-03は「常に非決定性がない」ことの証明ではない——1回のTrialでの非確認であり、確定的Parameter導入が将来的に不要と主張するものではない。
- WU-05は「Production Web Composition」全体(実FastAPI App起動・実HTTP/SSE経由・実32 Criterion選択・Recording=FULL・実Persistence)を新規に構築・検証したとは主張しない——既存のHook直結Testでの再確認に留まる(詳細は§8)。
- Phase 9-1 Closure、Selene解決、Phase 9-2/9-3進行は主張しない。
- Decoder/JSON Schema/Prompt/Batching/Frontend/Selene/Git操作への変更は一切行っていない。

## 2. 対象

[Codex Controller Exact Handoff(2026-09-05 12:16:55 JST)](../handoffs/phase_9_controller_component_independence_gemma_guard_main_rework_exact_handoff_ja_20260905121655.md)、WU-01〜WU-05全項目。

## 3. Files Changed

| File | 変更内容 |
|---|---|
| `src/margpa_runtime_llm/bootstrap/runtime_governance.py` | (WU-01)`build_neutral_semantic_runtime(descriptors)`関数を新設(Main非依存にCriteria Provider Portから`SemanticRuntimeCoordinator`を構築)。`JudgeSemanticTurnProvider`Classを新設(Coordinator+Context Provider+Main Mode Providerから、既存Snapshotを読むか新規`begin()`するneutralな"begin-or-get"境界)。`RuntimeGovernanceComposition.__init__`に`semantic_runtime`引数を追加(注入がなければ従来どおり内部構築、既存呼び出し元は完全後方互換)。 |
| `src/margpa_runtime_llm/bootstrap/web_application.py` | (WU-01)`semantic_runtime_coordinator`の構築を`runtime_governance_enabled`条件から`runtime_governance_enabled or feature_modes_enabled`条件へ変更(Main不在でもJudge有効なら構築)。`_semantic_runtime_context()`をMain存在条件から独立させ常時構築。`_current_main_mode()`を新設(Main存在時は実Mode、不在時は`"absent"` Sentinel)。旧来の読取専用Lambda(`runtime_governance_composition.semantic_runtime.snapshot_for(...) if ... else None`)を`JudgeSemanticTurnProvider`インスタンスへ置換。 |
| `src/margpa_runtime_llm/bootstrap/judge_live_integration.py` | (WU-04a)`_finalize_judge_dispatch()`・般Quality分岐の`failed`/`cancelled`分岐、計3箇所の`_pending_evidence(model_key=context.model_key, ...)`を`model_key=executed_provider or context.model_key`へ修正(実行Judgeの実Identityを正しく記録)。(WU-04b)ENFORCE Wait Loopの`cancelled_by_request`固定Labelを、`model_access_coordinator.consume_preemption()`を用いた分岐(`cancelled_by_main_priority_preemption`／`cancelled_by_request`)へ修正。同様に、般Quality分岐の`cancel_reason`(旧: Deadline以外は無条件`preempted_by_main_priority`)も同じ`consume_preemption()`分岐で正しく`cancelled_by_request`へフォールバックするよう修正。 |
| `src/margpa_runtime_llm/modules/inference/application/model_access_coordinator.py` | (WU-04b)`_preempted_task_ids: set[str]`を新設。`acquire_main()`のPreemption実行箇所で、Preempt対象の`task_id`を記録するよう追加(既存の`self._current_cancel()`呼び出し自体は無変更)。新規Public Method `consume_preemption(task_id)`を追加(one-shot check-and-clear)。 |
| `tests/unit/bootstrap/test_runtime_governance_component_independence.py`(新規) | (WU-01)`JudgeSemanticTurnProvider`/`build_neutral_semantic_runtime`の直接Unit Test(Group A、9本)、実Dispatch Router経由の結合Test(Group B、5本、うち1本はGuard Mode非依存のMatrix確認)、`build_phase1_web_runtime()`自体の配線を検証するWiring Test(Group C、1本、Sabotage-regressionで検出力を確認済み)、Mode Matrixの16通りParameterize Testを含む。全26本。 |
| `tests/integration/test_real_local_main_gemma_concurrent_dispatch_smoke.py` | (WU-02)実機Batch別Observability付きTest`test_a_real_normal_32_criterion_initial_gemma_observe_judge_batch_evidence`を新規追加(`model_smoke`)。(WU-05)既存Golden Path Test再実行のみ、Source変更なし。 |
| `tests/integration/test_real_local_qwen3guard_mode_independence_smoke.py`(新規) | (WU-03)Qwen3Guard同一Input二重呼び出し実機Test`test_a_real_benign_input_classified_twice_under_identical_conditions`。 |
| `tests/unit/bootstrap/test_judge_live_integration.py` | (WU-04b)既存Test`test_main_preemption_reaching_judge_produces_cancelled_terminal_state`を、実際の`ModelAccessCoordinator.acquire_main()`経由の真のPreemptionを駆動する形へ修正(旧Fixtureは`generate()`内で`cancellation.cancel()`を自己呼出しするだけで、実Preemption機構を一切経由していなかった)。新規Test`test_main_priority_preemption_is_reported_by_the_enforce_wait_loop_itself`を追加(ENFORCE Wait Loop自身の分岐を専用に検証)。 |
| `tests/unit/bootstrap/test_judge_live_integration_dispatch_router.py` | (WU-04a)新規Test`test_selene_shaped_dispatch_records_the_executing_providers_evidence_identity`を追加(Sabotage-regressionで検出力を確認済み)。 |
| `tests/unit/inference/test_model_access_coordinator.py` | (WU-04b)新規Test`test_consume_preemption_reports_true_exactly_once_for_a_preempted_task`・`test_consume_preemption_reports_false_for_a_task_never_preempted`を追加。 |

## 4. Files Deliberately Not Changed

- `judge_output_decoder.py`(Production Decoder/Contract)、Prompt Template一式(`SelenePromptAdapter`/`GEMMA_MANIFEST`含む)、JSON Schema、Batching機構(`SeleneSemanticEvaluator._plan_batches()`) — 無変更。
- `_REJUDGE_TOKENS_PER_CRITERION`(100)、`LIVE_REPAIR_BUDGET.max_additional_tokens`(3600)、`SeleneSemanticEvaluator`の`max_new_tokens`(1000)/`max_criteria_per_call`(8)/`max_calls`(4) — 無変更。
- `Qwen3GuardGenAdapter`のGeneration Parameter(temperature/top_p/top_k/seed) — 無変更(WU-03の非決定性が確認されなかったため)。
- Selene関連一式、Frontend一式(`frontend/`) — 今回未編集。
- `docs/project/shared/unresolved_work/current_unresolved_findings_registry_ja.md`、`docs/project/phases/phase_9/phase_index_ja.md` — 直接編集していない。
- 旧Return/Recovery一式 — 上書きしていない(append-only)。
- `CancellationToken`Class自体(共有Low-level Primitive) — 無変更(WU-04bの解決はより外側の`ModelAccessCoordinator`のみで完結させた)。

## 5. Real Evidence

### 5.1 WU-01 — Fixture/Unit Matrix(26 Test)とSabotage

- `JudgeSemanticTurnProvider`が、Main OFF/不在(main_mode_provider="off"/"absent")でも有効なSnapshotを返し(Group A)、Main側が先にFreezeした場合は同一Snapshotを再利用すること(共有の相互性)を確認。
- Criteria Provider空(`descriptors=()`)でも例外を投げず、`criteria=()`のSnapshotを返すこと(汎用品質評価への収束条件)を確認。
- `RuntimeGovernanceComposition(semantic_runtime=...)`の注入が真に共有されること(外部から読んだCoordinatorに同一Turnが見えること)を確認。
- `resolve_semantic_action()`が、`main_mode`が`"off"`/`"absent"`いずれでも、DEVIATIONに対し`REPAIR_REQUESTED`を絶対に返さない(`OBSERVED`のみ)ことを確認(Main Evidence/Action=0の直接証明)。
- Mode Matrix(main_mode×judge_mode、16通り)全て、Providerが例外なく正しいModeを保持したSnapshotを返すことを確認(Group A)。
- Dispatch Router経由(Group B)で、Main OFF/不在下でもSelene形状Adapterが`semantic_snapshot_unavailable`にならず`completed`まで到達することを確認(3 Test: Main OFF、Main不在、Repair OFF/ENFORCE組合せ)。Guard Hookの有無がJudge起動可否を変えないことも確認(Matrix項目6)。
- Group C(`build_phase1_web_runtime()`自体の配線検証)で、`runtime_governance_enabled=False, feature_modes_enabled=True`という実配線条件下、`build_judge_completion_hook`へ渡される`semantic_snapshot_provider`が`None`ではなく機能することを確認。
- **Sabotage**: `web_application.py`の`semantic_snapshot_provider=`を旧来の読取専用Lambdaへ戻すと、Group Cの新規Testが`snapshot is None`で確実に失敗することを確認。復元後、`diff`でByte一致を確認。

### 5.2 WU-02 — 実機Batch別Observability(実機1回)

Preflight(残存Process/Port確認)はClean。実機Gemma OBSERVE、通常32 Criterion選択(実109件corpusから production selection)で1回実行。

```
[real-32-criterion-initial-gemma-judge-evidence] elapsed_ms=26738 planned_batch_count=4 call_count=3
  decision_is_none=True result_execution_state='failed' result_failure_reason='malformed_output'
  result_recommendation='unknown' result_criteria_selected=32 result_criteria_evaluated=0
[batch=1] max_new_tokens=1000 finish_reason=STOP completion_tokens=545 diagnostic_execution_state='completed' missing_ids=[] extra_ids=[]
[batch=2] max_new_tokens=1000 finish_reason=STOP completion_tokens=505 diagnostic_execution_state='completed' missing_ids=[] extra_ids=[]
[batch=3] max_new_tokens=1000 finish_reason=STOP completion_tokens=500 diagnostic_execution_state='failed'
  diagnostic_failure_reason='found `{` that does not decode as one complete, well-formed JSON object -- ...'
  missing_ids=[8件全て] extra_ids=[]
```

**結論**: Batch 1・2は正常完了(Token上限に対し余裕あり、Decode成功)。Batch 3のみ、Token上限未到達(`STOP`、500/1000)のまま不完全JSON断片で失敗。「最初のBatchで停止」という当初仮説は反証された。原因はTruncateではなく、Gemma固有の間欠的JSON形式Quirk(`judge_output_decoder.py`の`_extract_json_objects()`が既に文書化している"Gemma 4 E2Bが複数JSON Objectを出力することがある"という既知挙動の一種)。

参考: 別途、User Mac実画面Recheck記録(`phase_9_1_user_mac_final_manual_recheck_gemma_guard_main_enforce_result_ja_20260905115026.md`§10)によれば、Userが観測した実UI上の4件の失敗は全て`call_count=1`(最初のBatchで失敗)だった。今回のTrialは`call_count=3`(3番目のBatchで失敗)であり、失敗するBatch位置がTrialごとに異なることは、本件が固定的な「最初のBatchの構造的限界」ではなく、間欠的なQuirkであるという特定と整合する。

ログ: `/private/tmp/phase9_gemma32_initial_judge_batch_evidence_20260905133000.log`(SHA-512: `c5098adb2692f75b1d3f239aed22e40f2fed3d0b73fa8279f35116f377f8b2f29d2f04c7480665b9c8949fa918e45d7fa2273760277f2d6aaa5fead861967a5f`、243行)

**修正未適用の理由**: 是正しうる手段(Decoder緩和/JSON補修/盲目的Retry/Budget再拡大)は全て今回の禁止事項に直接該当する。残る手段(Prompt強化、Qwen3Guard同様の確定的Sampling固定)は、本Handoff自体が「Structured出力のSampling固定が必要ならRole別Parameter Contractとして局所化する」という将来の別途判断事項として位置づけており、今回のTrial1回のみで根拠なく実施することは避けた。

### 5.3 WU-03 — Qwen3Guard Mode非依存(実機1回)

Source確認: `Qwen3GuardGenAdapter.classify_point()`/`Qwen3GuardDetectorAdapter.detect()`いずれもMode引数を受け取らない(構造的にMode非依存)。

実機1回(同一benign入力`"What is the capital of France?"`を、同一Target/Providerで2回連続呼び出し):

```
[real-qwen3guard-mode-independence-evidence] input='What is the capital of France?'
  first=(failure=NONE outcome=CLEAR latency_ms=176 token_count=7)
  second=(failure=NONE outcome=CLEAR latency_ms=63 token_count=7)
  first_clear=True second_clear=True identical_outcome=True
```

両呼び出しとも`CLEAR`で一致。今回のTrialでは分類の非決定性は再現しなかった。ログ: `/private/tmp/phase9_qwen3guard_mode_independence_20260905134500.log`(SHA-512: `b8f629d0688c922be1b51a00633733840a612b89d8c74437ed5ed85fa53c9a6994eca49bddf56d361a04512b76f0d274fad5e159472f1fc858c7713a291f30ea`)

**結論**: Mode-Detection結合は構造的に存在しない(Code上の事実)。実機Evidenceも今回は非決定性を示さなかった。したがって確定的Generation Parameter導入という修正は適用しない(WU-03自身の"必要なら"条件が満たされていない)。

### 5.4 WU-04a — Evidence Identity(Unit、Sabotage-regression)

新規Test`test_selene_shaped_dispatch_records_the_executing_providers_evidence_identity`にて、Selene形状Dispatch(Main Identity `"main.test-model"`とは別の`_SELENE_PROVIDER_ID`)で`judge_run_evidence`の`model_identity`が正しく実行Provider(Selene ID)になることを確認。**Sabotage**: `_finalize_judge_dispatch()`の`model_key=executed_provider or context.model_key`を旧`model_key=context.model_key`へ戻すと、Testが`'main.test-model' == 'judge.selene...'`で確実に失敗することを確認。復元後Byte一致を確認。

### 5.5 WU-04b — Cancellation起源分類(Unit、Sabotage-regression×2)

- `test_consume_preemption_*`(2本)で`ModelAccessCoordinator.consume_preemption()`の基本契約(1回だけTrue、以降False、Preemptされていなければ常にFalse)を確認。
- `test_main_preemption_reaching_judge_produces_cancelled_terminal_state`を、実際の`acquire_main()`経由の真のPreemptionを駆動する形へ書き換え(旧Fixtureは症状だけを模倣し実機構を経由していなかったことが判明したため)、`preempted_by_main_priority`を正しく報告することを確認。
- `test_main_priority_preemption_is_reported_by_the_enforce_wait_loop_itself`(新規)で、ENFORCE Wait Loop自身の分岐が`cancelled_by_main_priority_preemption`を正しく報告することを確認。
- **Sabotage**: 両分岐の`consume_preemption()`呼び出しをそれぞれ削除し、旧来の固定Labelへ戻すと、対応するTestがそれぞれ確実に失敗することを確認(2回)。復元後Byte一致を確認。

### 5.6 WU-05 — Main起点Repair実機再確認(実機1回)

Preflight Clean。既存Golden Path Test`test_a_real_gemma_main_governance_enforce_run_authorizes_and_adopts_the_repair`(Main Governance ENFORCE・Judge Gemma ENFORCE・Judge側Repair OFF)を実機1回再実行し、PASS(15.10秒)。`repair_requested_by=="main_governance"`・`repair_outcome=="improved"`・`repair_accepted is True`・`presentation_outcome=="repair_accepted"`を確認。ログ: `/private/tmp/phase9_wu05_main_governance_origin_repair_20260905140500.log`

## 6. Focused／Static Verification

- Ruff: 今回変更した全File、`All checks passed!`。
- Canonical Mypy(`./.venv/bin/mypy src tests`): 43 errors / 4 files(既存Baseline、今回変更による新規Errorなし)。
- 非Model Full Suite(`pytest tests/`、`model_smoke`除外): **2346 passed, 32 deselected**(Rework開始前は2316 passed, 30 deselected——新規追加した非Model Test 30本の内訳は、WU-01のGroup A/B/C 26本 + WU-04関連4本(既存修正1本除く純増分))。
- Model Smoke(`model_smoke`、実機): WU-02用1本・WU-03用1本・WU-05用既存1本、計3回のみ実行(規定どおり)。

## 7. Internal Review(2回、完全別2観点)

### Review ① — Component Independence／Mode／Authority／OFF Call 0

- [OK] Main OFF/不在でJudge/Guard/Recordingへの影響が実際に0であることを、Fixture(26本)・Sabotage・実機(WU-01は実機不要のため対象外)で確認した。
- [OK] Judge OFF(`feature_modes_enabled=False`または`judge_mode_control is None`)でMain構造Observe/Enforceが独立して動くことは、Main側`_pre_hook`が元々Judgeを一切参照しない(無変更)ことをCode Readingで確認した——新規Regression不要と判断。
- [OK] Guard OFF/OBSERVE/ENFORCEの組合せがJudge起動可否を変えないことを、Matrix項目6の専用Testで確認した。
- [FINDING→FIXED] 当初、`load_reference_descriptors()`呼び出しを完全無条件化したところ、`runtime_governance_enabled=False`かつ`feature_modes_enabled=False`という既存Testの最小Fixture(`test_web_cli.py`)が`runtime_info.backend_key`欠如で破壊された。`runtime_governance_enabled or feature_modes_enabled`条件へ絞り込み、Full Suite全Green(2342→2346)を再確認して解決した。
- [OK] `resolve_semantic_action()`自体は無変更——Main Evidence/Action=0はSnapshotの`frozen_main_mode`が正しく伝播することのみに依存しており、Action解決Logic自体を触らずに済んだことを確認(改修範囲の最小化)。

### Review ② — Model出力／Decode／Budget／Cancellation／Evidence Truthfulness

- [OK] WU-02: 実機Evidenceに基づき当初仮説(最初のBatch停止)を明示的に反証し、Test Docstringを訂正した(過去のSelf-reviewで指摘されたような「未確認のClaimを恒久化する」Patternを繰り返さないよう注意した)。
- [OK] WU-02: 修正候補(Decoder/JSON/Retry/Budget/Prompt/Sampling)は全て検討したが、根拠なく実施することを避け、Hard Assertは意図した挙動のまま(Failする状態のまま)残した——見せかけの成功のためにAssertを緩めていない。
- [OK] WU-03: 実機Evidenceが「非決定性あり」を示さなかったことを、そのまま「非決定性なし」と過大解釈せず、「今回のTrialでは再現しなかった」という限定的な書き方に留めた。
- [OK] WU-04a: `model_identity`修正がSabotage-regressionで検出可能であることを実証した。
- [FINDING→FIXED] WU-04bの2箇所目のFix(ENFORCE Wait Loop)を検証する新規Testが、当初`enforce_presented_final`を指定しなかったため、実際には非同期(OBSERVE同様)経路を通り、対象コードに到達していなかった(診断Scriptで`hook()`が即時Returnしていることを実際に確認して発見)。`enforce_presented_final=True`を追加してSynchronous ENFORCE Wait Loopへ正しく到達させ、Sabotageで検出力を確認した。
- [OK] 新規`cancelled_by_main_priority_preemption`Labelは`classify_evaluation_failure()`の既存"cancel"/"preempt"部分文字列Matchにより、User向け表示は既存の`preempted_by_main_priority`/`cancelled_by_request`と同じCANCELLED表示へ収束することを確認した(Frontend変更なしでも表示が壊れない)。
- [残存Finding、修正せず] 「Main優先Preemption」を表す内部文字列が、旧来の`preempted_by_main_priority`(般Quality分岐)と新規の`cancelled_by_main_priority_preemption`(ENFORCE Wait Loop分岐)とで綴りが異なる。両者は`classify_evaluation_failure()`経由で同一のUser向け表示に収束するため機能上の実害はないが、命名の一貫性は取れていない。既存の`preempted_by_main_priority`という文字列は他所で参照されている可能性を考慮し、今回のScopeでは統一Renameを行わなかった(Codex Controller判断待ち、§8参照)。

## 8. Open Findings／True Stop

1. **WU-02未解決**: Gemma通常初回Judgeの実用的信頼性は未確立。次の一手(Prompt強化／確定的Sampling導入／Decoder許容度調整のいずれか)はCodex Controllerの明示的な追加許可が必要。
2. **WU-03の確認範囲が限定的**: 1回のTrialでの非再現であり、実運用での非決定性を完全に排除するものではない。
3. **WU-05のScope縮小**: 今回「Production Web Composition」(実FastAPI起動・実HTTP/SSE・実32 Criterion選択・Recording=FULL・実Turn Persistence)を新規構築・検証していない。既存のHook直結Golden Path(1 Criterion・`persistent=None`・`recording_mode="off"`)の再PASS確認に留まる。Full Matrixでの新規検証は、実施するとすればWU-02解決後が望ましいと考える(WU-02が未解決のまま32 Criterion Production経路を回すと、同じ間欠Quirkに再度遭遇する可能性が高いため)。
4. **Cancellation Reason命名の不統一**(§7 Review②の残存Finding、上記参照)。
5. **拒否文二重表示**(WU-03の対象外として明示的に分離指示された既存の弱Finding): 今回未着手のまま維持。

True Stopに該当する事項はない(全て報告済みのOpen Findingであり、実装作業自体を停止させる要因ではない)。

## 9. Action Inventory

**実行した**:
- WU-01: `runtime_governance.py`/`web_application.py`のSource修正、新規Test File 1本(26 Test)、Sabotage-regression 1回。
- WU-02: 実機Batch別Observability付きTest 1本を新規追加、実機1回実行、Test Docstring訂正。修正は適用せず。
- WU-03: Source Code確認(修正不要と判断)、実機Test 1本を新規追加、実機1回実行。
- WU-04a: `judge_live_integration.py`の3箇所修正、新規Test 1本、Sabotage-regression 1回。
- WU-04b: `model_access_coordinator.py`の新機構追加、`judge_live_integration.py`の2箇所修正、既存Test 1本の書換、新規Test 3本、Sabotage-regression 2回。
- WU-05: 既存Golden Path実機Testの1回再実行(Source変更なし)。
- 全体: Ruff/Canonical Mypy/非Model Full Suite確認(複数回)、Preflight確認(3回)、Post-run Cleanliness確認。

**実行しなかった**:
- Selene修復、Phase 9-2/9-3、Phase 10、全面Rollback、Context拡張、Decoder緩和、JSON補修、盲目的Retry、無根拠なBudget拡大、Prompt/Schema変更、Frontend変更、Batching変更。
- Git add/commit/push/stash(一切なし)。
- Current Registry/Phase Index編集(一切なし)。
- 既存Handoff/Return/History一式の上書き(一切なし、全て新規Path)。
- WU-02への追加実機Trial(修正未適用のため、追加確認の必要性なしと判断)。
- Cancellation Reason文字列の統一Rename(§7/§8参照、Codex Controller判断待ち)。

**Temporary Artifact／Active Process／Model Load**: 実機Trial後、毎回Preflight相当のPost-run確認(`ps aux`/`lsof`)でMARGPA関連Process・Port残存なしを確認済み。一時Logは全て`/private/tmp/`配下(3ファイル、上記各節に記載のPath/SHA-512)。Scratchpad配下のSabotage用Backupファイルは作業完了後もそのまま残置(次回セッションでの参照用、削除は行っていない)。

## 10. Exact Next Action for Codex Controller

1. WU-01・WU-04の解決を受理するか判断してください。
2. WU-02(Gemma通常初回Judge未解決)について、次の一手(Prompt強化/確定的Sampling/Decoder許容度調整のいずれか、または全て見送り)を明示的に指示してください。
3. WU-05の「Production Web Composition」Full Matrix(実App起動・Recording=FULL・実Persistence・実32 Criterion)を今回のScopeとして追加要求するか、WU-02解決後まで延期するかを判断してください。
4. §7 Review②の残存Finding(Cancellation Reason命名不統一)について、統一Renameを許可するか、現状維持を指示してください。
5. Phase 9-1のClosure可否は、上記全てが解決してから改めて判断してください(今回は主張していません)。

本Returnの提出をもって停止します。Phase Closure、次Phase着手、追加の実機Trialのいずれも行いません。Codex Controller Independent Review待ちです。
