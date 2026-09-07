# Phase 9-1 — Component完全疎結合 R2差分Rework Exact Return

```yaml
document_type: exact_implementation_return
document_state: ready_for_controller_review
recorded_at: 2026-09-05 17:58:16 JST
language: ja
from: claude_designer_implementer
to: codex_controller
decision_authority: user
authority_owner: Nazuna Research
in_response_to: phase_9_controller_component_independence_r2_delta_rework_exact_handoff_ja_20260905163632.md
review_target_of_this_document: docs/project/phases/phase_9/history/operations/phase_9_1_component_independence_rework_controller_review_ja_20260905163632.md
maximum_claim: P9_1_R2_WU01_WU02_WU03_WU05_WU06_RESOLVED_WU04_SAMPLING_FIX_VERIFIED_JSON_DEFECT_NARROWED_NOT_ELIMINATED
phase_9_1_closure: false
git_mutation: none
append_only: true
```

## 1. 最大Claim

`P9_1_R2_WU01_WU02_WU03_WU05_WU06_RESOLVED_WU04_SAMPLING_FIX_VERIFIED_JSON_DEFECT_NARROWED_NOT_ELIMINATED`

Controller Review(2026-09-05 16:36:32 JST)が指摘したIR-CI-01〜06の全6件に対応した。うちR2-WU-01／02／03／05／06の5件は、実装・新規Test・Sabotage-regressionまたは実機Evidenceで解決を確認した。R2-WU-04(Structured Role Generation局所固定)はSampling固定の実装と検証は完了したが、実機32 Criterion Gemma初回JudgeのJSON不完全性という根本Defectは、認可された1回のPrompt/Schema局所強化を経てもなお部分的に残存する——これはCorrected Scopeの誠実な報告であり、隠蔽ではない。

**明示的除外**: Phase 9-1 Closureは主張しない。Selene、Phase 9-2／9-3、Phase 10、全面Rollbackには一切進んでいない。Git操作は一切行っていない。Current Registry／Phase Indexは編集していない。

## 2. 対象

- Controller Review: `docs/project/phases/phase_9/history/operations/phase_9_1_component_independence_rework_controller_review_ja_20260905163632.md`
- R2 Exact Handoff: `docs/project/phases/phase_9/handoffs/phase_9_controller_component_independence_r2_delta_rework_exact_handoff_ja_20260905163632.md`
- R2-WU-01からR2-WU-06までを順序どおり実施。

## 3. Files Changed

### Source

| File | WU | 変更内容 |
|---|---|---|
| [runtime_governance.py](../../../../../src/margpa_runtime_llm/bootstrap/runtime_governance.py) | R2-WU-01 | `RuntimeGovernanceComposition.begin_semantic_turn()`をpeer read-or-begin化(既存Snapshotがあれば読むだけ、`main_mode`引数を無視)。`record_semantic_response()`/`record_semantic_deferred()`に、対象requestの`frozen_main_mode`が`observe`/`enforce`でなければCall 0で`None`を返すGateを追加(`semantic_runtime.record_response()`/`record_deferred()`へ一切到達しない)。 |
| [conversation_generation.py](../../../../../src/margpa_runtime_llm/modules/conversation/application/conversation_generation.py) | R2-WU-01 | `ConversationGenerationService.__init__`に`semantic_turn_begin_hook: Callable[[str], object] \| None`を追加。`start()`内、`judge_modes`/`runtime_snapshot`と同じAttempt境界(Judge/Repair/Recordingの各Hookより前、実Generationより前)で一度だけ呼ぶ。例外は握り潰す(Turnをブロックしない)。本Module自体は`runtime_governance`型に一切依存しない。 |
| [web_application.py](../../../../../src/margpa_runtime_llm/bootstrap/web_application.py) | R2-WU-01 | `ConversationGenerationService(...)`へ`semantic_turn_begin_hook=semantic_snapshot_for_judge`を追加(既存の`JudgeSemanticTurnProvider`インスタンスをそのまま再利用——新規Closure不要)。 |
| [recording_live_integration.py](../../../../../src/margpa_runtime_llm/bootstrap/recording_live_integration.py) | R2-WU-02 | `record_judge_evidence()`に`evaluated_model_identity`/`configured_judge_provider`/`active_judge_provider`の3新規引数を追加し、`metadata_fields`へ記録。既存`model_identity`/`artifact_digest_sha512`/`backend_key`/`backend_version`の意味は変更しない(Executed Judge Providerを指す、の一意固定のまま)。 |
| [judge_live_integration.py](../../../../../src/margpa_runtime_llm/bootstrap/judge_live_integration.py) | R2-WU-02 | `_pending_evidence()`に`configured_judge_provider`/`active_judge_provider`引数を追加し、`evaluated_model_identity=context.model_key`を常時渡す。`_run_selene_dispatch()`/`_finalize_judge_dispatch()`に`executed_model_runtime_info`を新規スレッド——Dedicated Gemma/Selene経路は`evaluator.inference_service.runtime_info`(実行Adapter自身のLoad Receipt)、Main-shared経路は`context.model_runtime_info`(Main自身)を渡す、呼び出し元ごとに正しく分岐。 |
| 〃 | R2-WU-03 | `model_access_coordinator.consume_preemption()`呼び出し2箇所(Worker側cancel分岐、ENFORCE Wait Loop)を`was_preempted()`へ変更。内部Reason文字列を`cancelled_by_main_priority_preemption`へ統一(旧`preempted_by_main_priority`は廃止)。 |
| [model_access_coordinator.py](../../../../../src/margpa_runtime_llm/modules/inference/application/model_access_coordinator.py) | R2-WU-03 | `consume_preemption()`(破壊的one-shot)を`was_preempted()`(非破壊的peek)へ置換。`start_background()`の`_run()`内`finally`で`_preempted_task_ids.discard(task_id)`を追加——Run自身のTerminalで一度だけ確実にcleanupする。 |
| [selene.py](../../../../../src/margpa_runtime_llm/adapters/evaluation/selene.py) | R2-WU-04 | `SeleneSemanticEvaluator.__init__`に`sampling_overrides: Mapping[str, object] \| None`を追加(既定`None`)。`_generate_with_busy_retry()`の`GenerationParameters`構築を`.model_copy(update=self._sampling_overrides)`で上書き。Selene/Main-shared呼び出し元は`None`のまま(無変更)。 |
| [dedicated_role_adapters.py](../../../../../src/margpa_runtime_llm/adapters/runtime_model_control/dedicated_role_adapters.py) | R2-WU-04 | `GEMMA_JUDGE_DETERMINISTIC_SAMPLING`定数(temperature=0/top_p=1/top_k=1/min_p=0/penalty=0/repeat_penalty=1/seed=0)を新設。`SeleneRoleAdapter`に`sampling_overrides`を追加しGemma分岐のみへ注入(Selene分岐は無変更)。 |
| [qwen3guard_adapter.py](../../../../../src/margpa_runtime_llm/adapters/guardrail_governance/qwen3guard_adapter.py) | R2-WU-04 | 同一の決定的Sampling値を`_DETERMINISTIC_SAMPLING`としてこのAdapter専用にハードコード(単一Role専用Classのため注入不要)。`classify_point()`の`GenerationParameters`へ`.model_copy(update=...)`で適用。 |
| [gemma_4_e2b/project_derived_multi_criterion_prompt_v1.txt](../../../../../config/judge_templates/gemma_4_e2b/project_derived_multi_criterion_prompt_v1.txt) | R2-WU-04 | 認可された1回のみのPrompt局所強化: Rule 6を追加——Schema例中の`"short reference"`/`"short code"`はPlaceholder Labelであり文字どおりOutputへ複写してはならない旨、`evidence_refs`は他Keyの前に`]`で閉じる旨を明記。Selene用の同名File(別Path)には触れていない。 |
| [gemma_4_e2b/manifest.json](../../../../../config/judge_templates/gemma_4_e2b/manifest.json) | R2-WU-04 | Template変更に伴い`derived_template_sha512`/`project_contract_digest_sha512`を再計算・更新(Digest不一致でFail-closedしないため)。 |

### Tests(新規/変更)

| File | WU | 内容 |
|---|---|---|
| [test_runtime_governance_component_independence.py](../../../../../tests/unit/bootstrap/test_runtime_governance_component_independence.py) | R2-WU-01 | Group D追加(8 Test): Main OFF/absent時のMain Semantic Evidence/History Call 0(Counting Coordinator Spy使用)、Main OBSERVE/ENFORCE時のみEvidence投影、`begin_semantic_turn()`のpeer-read確認。 |
| [test_conversation_generation_semantic_turn_begin.py](../../../../../tests/unit/conversation/test_conversation_generation_semantic_turn_begin.py)(新規) | R2-WU-01 | `semantic_turn_begin_hook`がTurn開始時に一度だけ・実Generation前に・Judge Hook有無に関わらず・例外を握り潰して発火することを確認(5 Test)。 |
| [test_model_access_coordinator.py](../../../../../tests/unit/inference/test_model_access_coordinator.py) | R2-WU-03 | 旧`consume_preemption`一発消費Testを2件、`was_preempted`の非破壊peek + Terminal cleanup Testへ置換。新規に16並行ReaderがすべてTrueで一致するRace Test 1件を追加。 |
| [test_judge_live_integration.py](../../../../../tests/unit/bootstrap/test_judge_live_integration.py) | R2-WU-03 | 統一後の`cancelled_by_main_priority_preemption`文字列へAssertion/Docstringを更新。 |
| [test_selene_adapter.py](../../../../../tests/unit/evaluation/test_selene_adapter.py) | R2-WU-04 | `sampling_overrides`未指定時はLibrary Default据え置き、指定時は実`GenerationRequest.parameters`へ反映されることを確認する2 Testを追加。 |
| [test_qwen3guard_adapter.py](../../../../../tests/unit/guardrail_governance/test_qwen3guard_adapter.py) | R2-WU-04 | `classify_point()`が実`GenerationRequest.parameters`へ決定的Samplingを適用することを確認する1 Testを追加。 |
| [test_dedicated_role_adapters_production_wiring.py](../../../../../tests/unit/adapters/runtime_model_control/test_dedicated_role_adapters_production_wiring.py) | R2-WU-04 | 既存のGemma/Selene実Lifecycle経由TestへSampling値のAssertionを追加(Geminiは決定的値、Seleneは無変更のまま)。 |
| [test_real_local_main_gemma_concurrent_dispatch_smoke.py](../../../../../tests/integration/test_real_local_main_gemma_concurrent_dispatch_smoke.py) | R2-WU-04 / R2-WU-06 | `_load_gemma_evaluator()`へ`sampling_overrides`引数を追加(既存呼び出し元は無変更)。実機Test 2件を新規追加(後述)。 |
| [test_real_local_qwen3guard_production_mode_independence_smoke.py](../../../../../tests/integration/test_real_local_qwen3guard_production_mode_independence_smoke.py)(新規) | R2-WU-05 | Production Guard Hook経由・Handoff実文言入力での実機Test。 |
| [test_production_composition_main_governance_gemma_repair_recording_smoke.py](../../../../../tests/unit/bootstrap/test_production_composition_main_governance_gemma_repair_recording_smoke.py)(新規) | R2-WU-06 | Fixture ModelによるProduction Composition Integration。 |

## 4. Files Deliberately Not Changed

- `config/judge_templates/selene/*`: Gemma専用Template強化はSeleneへ一切波及させていない(別Path、別Digest)。
- `modules/evaluation/application/judge_prompt_builder.py`(Main-shared汎用Prompt Builder): Sampling/Prompt変更は一切なし——Main会話Generation DefaultおよびMain-shared Judgeの汎用品質Path双方は無変更。
- `modules/evaluation/application/judge_output_decoder.py`: Decoder緩和・JSON補修は一切行っていない(禁止事項)。
- Retry機構: 追加していない。
- Recording/Persistence以外のWeb層(FastAPI Route/Frontend): 無変更。

## 5. Real Evidence

### 5.1 R2-WU-01(Fixture-only、実Model不使用)

38 Test(新規/拡張分含む)がFixtureのみで全Pass。Sabotage-regression: `record_semantic_response()`のGateを除去すると、`test_main_off_or_absent_is_call_zero_into_main_semantic_evidence`(2 Parametrize)が確実に失敗することを確認済み(Evidence非Noneを検出)。復元後の再Diff一致を確認済み。

### 5.2 R2-WU-02(Fixture + 実機Golden Path経由で確認)

Fixture Sabotage: `_run_selene_dispatch`呼び出し元の`executed_model_runtime_info`を`context.model_runtime_info`へ戻すSabotageで、`test_production_composition_main_enforce_gemma_judge_repair_recording_full_same_turn_save`の`artifact_digest_sha512`Assertionが`'unavailable' != 'cccc...'`で確実に失敗することを確認済み(復元後再Diff一致)。5.4節の実機Trialでも`judge_evidence["metadata_fields"]["model_identity"] == GEMMA_MODEL_KEY`かつ`evaluated_model_identity == QWEN_MODEL_KEY`を実Fileから確認。

### 5.3 R2-WU-03(Fixture-only)

新規Race Test(16並行Reader)で`was_preempted()`が全Reader一致を返すことを確認。Sabotage: `was_preempted()`を旧one-shot実装へ戻すと、`test_was_preempted_reports_true_for_a_preempted_task_still_running`と`test_concurrent_readers_never_race_for_a_single_preemption_answer`が確実に失敗(片方`False`)することを確認済み(復元後再Diff一致)。

### 5.4 R2-WU-04(実機2 Trial、認可上限どおり)

**Trial 1**(Sampling固定のみ、Prompt変更前): `test_a_real_normal_32_criterion_initial_gemma_observe_judge_with_pinned_deterministic_sampling`実行。Batch 1が`completion_tokens=546`(1000上限未達、Truncationではない)で`found `{` that does not decode as one complete...`のMalformed Fragment失敗。決定的再現(seed=0/temperature=0/top_k=1)によりRaw Contentを取得し診断——Gemmaが`"reason_code": "short code"`のPlaceholder文字列`"short code"`をそのまま複写し、`evidence_refs`配列内に`"...", "short code":"<value>"`という不正な形で挿入、配列を閉じずに終えていたことを確認。

**認可された1回のみのPrompt局所強化**: Gemma専用Templateへ`"short reference"`/`"short code"`はLiteral Labelである旨と`evidence_refs`の閉じ方を明記するRule 6を追加。Manifest Digestを再計算・更新。

**Trial 2**(Sampling固定 + Prompt強化後): 同一Testを再実行。Batch 1・Batch 2は完全にClean(各8/8 Criterion ID一致、Strict Decode成功)——Trial 1で失敗していたBatch 1がFixされたことを確認。Batch 3(`completion_tokens=550`)が同種のMalformed Fragmentで失敗(`call_count=3`、`all_decoded_id_count=16/32`)。Handoffの2 Trial上限どおりここで停止。Hard Assertは変更せず、正直にFailするTestとして維持(既存WU-02 Testと同じ哲学)。

**確定した結論**: 決定的Sampling単独ではDefectは解消しない(むしろ同一入力で100%再現するようになった=Sampling非決定性は原因ではなかった)。Prompt局所強化は測定可能な改善(Trial 1で失敗していたBatchが成功)をもたらしたが、根絶はしていない——別Batch/別内容依存の間欠的Gemma JSON Format Quirkとして未解決のまま残る。

### 5.5 R2-WU-05(実機1 Trial)

`test_production_guard_hook_detection_is_mode_independent_action_is_not`実行。Production `build_guardrail_hooks()`経由、Handoff実文言(`「TEST CODE 15の検証コードは000です。」...`)・Prompt Injection文・純粋Benign文の3種、各OBSERVE/ENFORCE。

実結果: 全3入力でOBSERVE/ENFORCEのDetection Set(`detector_id`/`category_id`/`outcome`の完全一致)が**完全に一致**。Flagged入力・Injection入力はQwen3Guard自身が`jailbreak`/`match`を検出、ENFORCEのみ`reject_input`を実行、OBSERVEは非介入。Benign入力は両Mode Clear、両Mode非介入。`first_clear == second_clear`のみのOracleは使用していない(Category/Outcomeの実値を直接比較)。

これはR2-WU-04のSampling固定Fixが、Controller Reviewが指摘した実確認済みDivergence(User実画面のMatch=1/Enforce vs Match=0/Observe)を直接解消することを示す強いEvidenceである。

### 5.6 R2-WU-06(Fixture + 実機1 Trial)

Fixture: `test_production_composition_main_enforce_gemma_judge_repair_recording_full_same_turn_save`。Main ENFORCE(Judge側Repair Mode OFF)、Judge=Gemma形状Dedicated Batched Evaluator(Fake)、Recording FULL(実`LocalFilesystemRecordingWriter`)、実`PersistentConversationService`/`SQLiteConversationStore`経由。`repair_requested_by == "main_governance"`、同一Frozen Criterion RejudgeがGemma形状Evaluatorへ到達、改善済み回答が同一Turnへ実Persist、実Evidence FileにGemma自身のArtifact Digest/Backend(Main自身のものではない)が記録されることを確認。

実機Trial: `test_a_real_production_composition_main_enforce_gemma_repair_recording_full_same_turn_save`実行(1回)。実Main(Qwen)+実Gemma、初回Candidateのみ決定的固定文字列(既存の全実機Gemma+Repair Testと同一の確立済みPattern——実Main Generationを騙して誤答させる非決定的手法は使っていない)、それ以外(Gemma初回Judge・Main実Repair Candidate生成・Gemma実Rejudge・実Persistence・実Recording)は全て実処理。

実結果: `execution_state='completed'`, `criteria_deviated=1`, `repair_requested_by='main_governance'`, `repair_outcome='improved'`, `repair_accepted=True`。同一TurnへCorrected Answerが実Persist、実Evidence Fileへ`model_identity=Gemma`/`evaluated_model_identity=Qwen`が記録された。1回のTrialでPASS(Skipなし)。

## 6. Focused/Static Verification

- 全体非Model Suite: **2363 passed, 35 deselected**(R2差分Rework前 2359 passed / 34 deselected から、新規/純増Test分)。
- Ruff(`src tests`): All checks passed。
- Canonical Mypy(`src tests`): **43 errors / 4 files**——Sessionを通じて完全不変(本Reworkの新規/変更Fileは0 error)。
- 実機Trial回数: WU-04が2回(認可上限どおり)、WU-05が1回、WU-06が1回。計4回。事前/事後のProcess残存チェック(`ps`/`lsof`)は毎回Clean。

## 7. Internal Review

### 観点A: Component Independence／Mode／Authority／OFF Call 0

- [OK] Main OFF/absent → Main自身のSemantic Evidence/History/Action Decision Call 0(R2-WU-01、Sabotage-regression済み)。
- [OK] Evaluation Turn ContextはConversation Turn開始時に一度だけFreeze——Judge HookからのLive Mode再読はもはや発生しない(Production配線では常にConversation start側が先着)。
- [OK] Repair(Judge側)=OFFでもMain Governance自身のENFORCE権限は独立して機能する(5.6節実機Evidenceで再確認)。
- [OK] Guardの検出結果はMode非依存、Action Authorityのみが変わる(5.5節実機Evidenceで確認)。
- [FINDING→FIXED] `begin_semantic_turn()`が無条件`begin()`だった点(R2-WU-01前)は、peer read-or-begin化により解消。

### 観点B: Model出力／Decode／Budget／Cancellation／Evidence Truthfulness

- [OK] Judge Evidenceの`model_identity`は一意にExecuted Judge Providerを指し、`evaluated_model_identity`と明確に分離された(R2-WU-02、Sabotage-regression済み)。
- [OK] Cancellation起源のRaceはWorker/ENFORCE Loop間で解消(非破壊peek、Sabotage-regression済み)。
- [残存Finding] Gemma初回32 Criterion JudgeのMalformed JSON Fragment Defectは、Sampling固定・1回の局所Prompt強化を経ても間欠的に残存する(5.4節)。Root Causeは「Gemma固有のSchema Placeholder誤認・JSON構造Errorを起こしやすい傾向」まで特定したが、完全な根絶には至っていない。

観点入れ替え後の再確認でも新規Findingなし。上記[残存Finding]は当初から認識済みでOpen Findingとして報告する。

## 8. Open Findings / True Stop

1. **R2-WU-04 Gemma JSON Defect未根絶**: 32 Criterion選択下で間欠的にBatch単位のMalformed JSON Fragmentが発生する。今回の1回のPrompt局所強化で改善(Trial 1で失敗したBatchがTrial 2で成功)したが、別Batchでの再発を確認した。Handoffの2 Trial上限に達しているため、これ以上のPrompt変更・Decoder変更・Retry追加は行わない。次の一手はCodex Controllerの明示的判断を待つ。
2. **Cancellation Reason文字列の統一は完了、旧文字列`preempted_by_main_priority`は完全に廃止**(R1で残存していた不統一はR2-WU-03で解消済み、Open Findingではない——念のため明記)。
3. **R2-WU-06実機TrialはMain初回回答を決定的Fixed文字列としている**: 既存の全実機Gemma+Repair Testと同一の確立済みPatternだが、「Main自身の実Generationが誤答するケース」の実機確認ではない(Main自身の生成品質は本Reworkの検証対象外と判断したうえでの選択)。
4. **Qwen3Guard決定的Sampling導入後の非決定性再検証は1 Trialのみ**: R2-WU-05の実機Trialは1回。長期的な決定性の保証ではなく、この1Trialでの一致を報告するものである。

未達項目をScope外へ事後的に変更したものは無い。上記は全て当初のScope内でReal Evidenceが指し示した、正直な残存Findingである。

## 9. Action Inventory

- R2-WU-01: 解決(resolved)。
- R2-WU-02: 解決(resolved)。
- R2-WU-03: 解決(resolved)。
- R2-WU-04: 部分解決(partial)——Sampling固定は実装・検証済み、Root Cause自体は未根絶。
- R2-WU-05: 解決(resolved)。
- R2-WU-06: 解決(resolved)——Fixture配線・実機Golden Path双方確認済み。

## 10. Exact Next Action for Codex Controller

1. R2-WU-01/02/03/05/06の解決を受理するか判断する。
2. R2-WU-04の残存Gemma JSON Defectについて、次の一手(a. さらなるPrompt/Schema強化の追加認可、b. Decoder Tolerance方針への転換検討、c. 現状のまま次Phaseへ委ねる、のいずれか)を明示的に決定する。
3. Phase 9-1 Closureを主張するか、さらなるRoundを要求するかを判断する。
4. 本ReturnとRecoveryの内容を踏まえ、次のExact Handoffを発行する(必要な場合)。

新規PathのExact ReturnとRecoveryを提出し、Codex Controller Independent Review待ちで停止する。Phase Index／Current Registryは編集していない。既存Handoff／Return／Historyの上書きは行っていない。
