# Phase 9-1 — Component完全疎結合 R4収束Rework Exact Return

```yaml
document_type: exact_implementation_return
document_state: ready_for_controller_review
recorded_at: 2026-09-05 23:23:53 JST
language: ja
from: claude_designer_implementer
to: codex_controller
decision_authority: user
authority_owner: Nazuna Research
in_response_to: phase_9_controller_component_independence_r4_convergence_rework_exact_handoff_ja_20260905195051.md
review_target_of_this_document: docs/project/phases/phase_9/history/operations/phase_9_1_component_independence_r3_return_controller_review_ja_20260905195051.md
maximum_claim: P9_1_R4_WU01_WU02_WU03_WU04_WU05_RESOLVED_GEMMA_DEVIATION_MALFORMED_DEFECT_ELIMINATED_REAL_GOLDEN_PATH_PASSED
phase_9_1_closure: false
git_mutation: none
append_only: true
```

## 1. 最大Claim

`P9_1_R4_WU01_WU02_WU03_WU04_WU05_RESOLVED_GEMMA_DEVIATION_MALFORMED_DEFECT_ELIMINATED_REAL_GOLDEN_PATH_PASSED`

Controller Review(2026-09-05 19:50:51 JST)が指摘したIR-R3-01〜05の全5件に対応した。R4-WU-01からR4-WU-05までの5件すべてを解決し、そのうちR4-WU-04は**R3から持ち越されていたGemma Deviation報告時のMalformed JSON Defectを実機2 Trialで根絶を確認**、R4-WU-05は**その修正を土台に実`build_phase1_web_runtime()`経由の実機Golden Path Trial(1回)で完全な成功(`execution_state='completed'`、`repair_accepted=True`)を確認**した。R3-WU-05が実機水準で正直にFailしたまま停止していた残存Findingは、本Roundで実機Evidenceに基づき解消された。

**明示的除外**: Phase 9-1 Closureは主張しない。Selene、Phase 9-2／9-3、Phase 10、全面Rollbackには一切進んでいない。Git操作は一切行っていない。Current Registry／Phase Indexは編集していない。Decoder緩和・JSON補修・Retry追加は一切行っていない。Criterion上限(`max_criteria=32`)・Budget(`LIVE_REPAIR_BUDGET`/`_REJUDGE_TOKENS_PER_CRITERION`)は変更していない。

## 2. 対象

- Controller Review: `docs/project/phases/phase_9/history/operations/phase_9_1_component_independence_r3_return_controller_review_ja_20260905195051.md`
- R4 Exact Handoff: `docs/project/phases/phase_9/handoffs/phase_9_controller_component_independence_r4_convergence_rework_exact_handoff_ja_20260905195051.md`
- R4-WU-01からR4-WU-06までを順序どおり実施。

## 3. Files Changed

### Source

| File | WU | 変更内容 |
|---|---|---|
| [semantic_runtime.py](../../../../../src/margpa_runtime_llm/modules/runtime_governance/application/semantic_runtime.py) | R4-WU-01 | `SemanticRuntimeCoordinator`の単一`_current`Slotを、`request_id`単位の`OrderedDict`ベースRequest-local Ledger(`_turns`)へ置換。`begin()`はLock下で既存Entryを先に確認し、既に同一`request_id`が存在する場合は新Generationを作らずそのまま返す(2 Thread同時Beginでも1 Generationのみ)。`snapshot_for()`/`record_response()`は`_turns.get(request_id)`で直接検索するため、別`request_id`が後からBeginしても元のRequestのSnapshot/Evidence記録は妨げられない。UI向け"Latest Current"Pointer(`_latest_request_id`)を`begin()`内だけで更新される別Fieldとして分離、`current_snapshot()`/`latest_evidence()`はこのPointer経由のまま(Status投影の既存契約は無変更)。`_MAX_TRACKED_TURNS=128`のFIFO Evictionを追加(Evicted Entry分のHistory/Criterion-key Bookkeepingも同時に除去)。 |
| [runtime_governance.py](../../../../../src/margpa_runtime_llm/bootstrap/runtime_governance.py) | R4-WU-01 | `JudgeSemanticTurnProvider`の単一`_begin_attempted_request_id`/`_begin_failed` Slotを、`request_id`単位の`OrderedDict`ベースFreeze-failure Memory(`_failed_request_ids`、`_MAX_TRACKED_FREEZE_FAILURES=128`でFIFO Eviction)へ置換。別`request_id`の成功/失敗が既存Requestの失敗記録を上書きしなくなった。 |
| [judge_live_integration.py](../../../../../src/margpa_runtime_llm/bootstrap/judge_live_integration.py) | R4-WU-03 | ENFORCE Wait Loopの`cancellation.is_cancelled()`分岐で、Workerの`outcome_holder[0]`をそのまま採用する条件を`execution_state in ("cancelled", "failed")`から`execution_state == "cancelled"`のみへ限定。通常の`failed`(Cancellationと無関係なModel/Decode Error)がReady直後にUser Stop/Main-priority Preemptionが検知された場合、必ず`was_preempted()`ベースの新規Classificationへfall throughし、無関係なFailureがCancellationを上書きしなくなった。 |
| [selene.py](../../../../../src/margpa_runtime_llm/adapters/evaluation/selene.py) | R4-WU-04 | `GemmaPromptAdapter._criterion_result_example()`を、`reason_code`/`evidence_refs`を含む5-Field例から`criterion_id`/`disposition`/`confidence`のみのCompact 3-Field例へ変更。共有Decoder(`judge_output_decoder.py`)・`SelenePromptAdapter`本体・Main-shared Prompt Builderは無変更。 |
| [gemma_4_e2b/project_derived_multi_criterion_prompt_v1.txt](../../../../../config/judge_templates/gemma_4_e2b/project_derived_multi_criterion_prompt_v1.txt) | R4-WU-04 | 新規Rule 6を追加: "Each entry in criterion_results must contain ONLY criterion_id, disposition, and confidence. Do not include reason_code or evidence_refs."(構造的な省略の明示であり、R2で否定された「曖昧なPlaceholderを見せてRuleで打ち消す」構造ではない)。Selene用の同名File(別Path)には触れていない。 |
| [gemma_4_e2b/manifest.json](../../../../../config/judge_templates/gemma_4_e2b/manifest.json) | R4-WU-04 | Template変更に伴い`derived_template_sha512`/`project_contract_digest_sha512`を再計算・更新。 |

### Tests(新規/変更)

| File | WU | 内容 |
|---|---|---|
| [test_runtime_governance_component_independence.py](../../../../../tests/unit/bootstrap/test_runtime_governance_component_independence.py) | R4-WU-01 | Group F追加(4 Test): Controller Review §3の3 Probe(「Aの開始Freeze失敗→B成功→Aを再読」「A成功→B成功→Aを再読(同一Generation/Digest)」「A成功→B成功→AのResponseを記録(B自身のCurrent/Evidenceは無影響)」)をそのままRegression化。加えて、2 Threadが同一`request_id`を`threading.Barrier`で同時Beginしても1 Generationのみ得られることを確認するConcurrency Testを追加。 |
| [test_semantic_runtime.py](../../../../../tests/unit/runtime_governance/test_semantic_runtime.py) | R4-WU-01 | 既存`test_coordinator_rejects_duplicate_and_late_publication`を、旧(単一Slot)契約の前提(「別Turn開始後の遅延Publicationは拒否される」)を反映した内容だったため`test_coordinator_rejects_exact_duplicate_republication`(完全重複のみ)と新規`test_coordinator_records_a_genuinely_new_late_response_after_a_different_turn_begins`(訂正された正しい契約——別Turn開始後の遅延だが真に新規のResponseは、その別Turn自身のEvidenceには一切影響を与えずに記録される)へ分割。 |
| [test_judge_live_integration.py](../../../../../tests/unit/bootstrap/test_judge_live_integration.py) | R4-WU-01/02/03 | (WU-02) 既存の3経路(Built-in／Main-shared／Dedicated Gemma)それぞれについて、実`freeze_semantic_turn()`Fixtureを介した実Snapshotを供給したうえで`evaluated_model_identity`/`configured_judge_provider`/`active_judge_provider`/`model_identity`(Executed)/`artifact_digest_sha512`/`backend_key`/`backend_version`の全Fieldを直接Assertする新規Test 2件(`test_main_shared_judge_evidence_records_the_full_identity_matrix`、`test_dedicated_gemma_judge_evidence_records_the_full_identity_matrix`)を追加し、既存Built-in Testを同様に拡張。(WU-03) 「Worker Failure Ready→genuine User Stop」「Worker Failure Ready→genuine Main-priority Preemption」の2固定Scheduleをそれぞれ再現する新規Test 2件を追加(`_PollLoopHeldUntilReleasedToken`でPoll Threadの`is_cancelled()`を無条件Hold、Preemption変種は`_FakePreemptingCoordinator`でCoordinator内部のCleanup Timing Raceを回避し決定的に構成)。既存`test_wu03_a_late_stale_semantic_result_after_stop_is_never_recorded_as_current`を、訂正された正しい契約(Stale Turnの遅延Responseは記録されるがFresh Turn自身のEvidenceには一切影響しない)を反映するようRename・修正。 |
| [test_runtime_governance_routes.py](../../../../../tests/unit/web/test_runtime_governance_routes.py) | R4-WU-01(Full Suite実行で新規発見) | 既存`test_late_result_for_a_superseded_turn_never_overwrites_the_current_turn`が旧(単一Slot)契約前提の`assert late_evidence is None`を持っていたため、訂正された正しい契約(旧Turn自身のEvidenceは記録されるが、Status投影が読む"Latest Current"Pointerは新Turnを指したままなので投影自体は無影響)へ修正。 |
| [test_judge_prompt_and_decoder.py](../../../../../tests/unit/evaluation/test_judge_prompt_and_decoder.py) | R4-WU-04 | 共有Decoderの既存契約(`reason_code`/`evidence_refs`は省略可能で、省略時は`None`/`()`にDefault)を、Schema変更に着手する前に固定する新規Pin Test `test_decode_criterion_reason_code_and_evidence_refs_are_optional_fields`を追加。 |
| [test_selene_adapter.py](../../../../../tests/unit/evaluation/test_selene_adapter.py) | R4-WU-04 | 既存`test_gemma_prompt_schema_is_a_single_unambiguous_parseable_json_example`を、実Production Gemma Manifest/Template描画がCompact 3-Field Schemaのみを要求すること(`evidence_refs`/`reason_code`がSchema行に一切現れない、新規Rule 6の文言が本文に含まれる)を確認する内容へ更新。 |
| [test_dedicated_role_adapters_production_wiring.py](../../../../../tests/unit/adapters/runtime_model_control/test_dedicated_role_adapters_production_wiring.py) | R4-WU-04 | 既存のGemma実Lifecycle経由Testへ、実際に送信されたPromptのSchema行が`evidence_refs`/`reason_code`を含まないことを確認するAssertionを追加(このTest自身のManifest/Templateは独立したFixtureのため、新規Rule 6文言そのものは別途`test_selene_adapter.py`側でAssert)。 |
| [test_production_composition_root_32_criterion_gemma_enforce_golden_path.py](../../../../../tests/unit/bootstrap/test_production_composition_root_32_criterion_gemma_enforce_golden_path.py) | R4-WU-05 | Fixtureの`dedicated_role_load.context_size`をR3-WU-05由来の`32768`(Fixture限定の水増し値)から、実配置と同じ`8192`へ修正。実32 Criterion Rejudge Promptの実approx token数(chars//4)を計算のうえ、実Budget(3600/32=3200許容)の範囲内に収まることを確認して適用(Criterion上限・Budget値自体は無変更)。 |
| [test_real_local_main_gemma_concurrent_dispatch_smoke.py](../../../../../tests/integration/test_real_local_main_gemma_concurrent_dispatch_smoke.py) | R4-WU-04/05 | R4-WU-04実機Test新規追加(`test_a_real_32_criterion_initial_gemma_observe_judge_with_a_genuine_deviation_under_the_compact_schema`)——既存Testが常にAll-Accept(`candidate_answer`が引用Evidenceと完全一致)だったのに対し、意図的に誤った回答(`"The capital of France is Tenon."`)でGenuine Deviationを誘発し、Compact Schema下でGemmaが実際に非空内容相当のDeviation Dispositionを32件中の一部について報告しても全Batch Strict Decode/32 ID一致が成立することを確認。既存R3-WU-05実機Test(`test_a_real_production_composition_root_32_criterion_gemma_enforce_golden_path`)のDocstringを、当時の`Trial 1失敗`という記述からR4での`実機Trial成功`という実際の結果へ更新(Testコード自体・Hard Assertionは無変更)。 |

## 4. Files Deliberately Not Changed

- `config/judge_templates/selene/*`: Gemma専用Compact Schema化はSeleneへ一切波及させていない。
- `modules/evaluation/application/judge_prompt_builder.py`(Main-shared汎用Prompt Builder)/ `modules/evaluation/application/judge_output_decoder.py`: 無変更。R4-WU-04は共有Decoderの既存の「`reason_code`/`evidence_refs`は省略可能」という契約に依存するのみで、Decoder自体は一切変更していない。
- `modules/repair/application/repair_eligibility_resolver.py` / `bootstrap/repair_live_integration.py`の`_REJUDGE_TOKENS_PER_CRITERION`/`LIVE_REPAIR_BUDGET`: 無変更(Criterion上限・Budget拡大は禁止事項)。
- Retry機構: 追加していない。
- Phase Index / Current Registry: 編集していない。
- 既存Handoff / Return / History: 上書き・直編集していない。

## 5. Real Evidence

### 5.1 R4-WU-01(Fixture-only、実Model不使用)

Group F新規4 Test + `test_semantic_runtime.py`/`test_runtime_governance_routes.py`の訂正Testすべて全Pass。Sabotage-regression4件を実施、いずれも復元後の再Diff一致を確認済み:

- `SemanticRuntimeCoordinator.begin()`の既存Entry確認Branchを除去(旧: 無条件で新Generation作成)すると、Concurrency Test(2 Thread同時Begin)が確実に失敗(`1 == 2`不成立)。
- `SemanticRuntimeCoordinator`全体を単一`_current`Slotへ戻す(`_turns`/`_latest_request_id`を除去)と、Probe 2/3/Concurrency/`test_late_result_for_a_superseded_turn`の計4 Testが確実に失敗(Probe 1相当の1件は`JudgeSemanticTurnProvider`側の別Fixで守られているため無影響——別Sabotageで個別確認)。
- `JudgeSemanticTurnProvider`の`_failed_request_ids`を旧`_begin_attempted_request_id`/`_begin_failed`単一Slot構成へ戻すと、Probe 1(`test_a_failed_freeze_for_one_request_survives_a_different_requests_success`)が確実に失敗(`late_a is None`不成立——B成功後にAが誤って再Freezeされる)。

全Suite実行で、`test_runtime_governance_routes.py`内の既存`test_late_result_for_a_superseded_turn_never_overwrites_the_current_turn`が旧契約前提のまま残っていたことを発見・修正した(Section 6参照)。

### 5.2 R4-WU-02(Fixture-only、実Model不使用)

新規Identity Matrix Test 2件(Main-shared/Dedicated Gemma)+既存Built-in Testの拡張版、全Pass。Sabotage: `_finalize_judge_dispatch()`内の`_pending_evidence()`呼び出しで`configured_judge_provider`/`active_judge_provider`を無条件`None`へ差し替えると、新規2 Testが両方とも確実に失敗(`'unavailable' == 'dedicated.gemma'`等の不成立)することを確認済み(復元後再Diff一致)。これで3経路すべてについて、Handoffが要求した保存JSON Fieldの全Matrix(`evaluated_model_identity`/`configured_judge_provider`/`active_judge_provider`/`model_identity`/Artifact/Backend/Version)を直接Assertする形で完結した。

### 5.3 R4-WU-03(Fixture-only、実Model不使用)

新規Test 2件、全Pass。Sabotage: ENFORCE Wait Loopの再採用条件を`execution_state == "cancelled"`から旧`in ("cancelled", "failed")`へ戻すと、2 Testとも確実に失敗(`'failed' == 'cancelled'`不成立)することを確認済み(復元後再Diff一致)。「Worker Failure Ready→User Stop」「Worker Failure Ready→Main-priority Preemption」の両Scheduleで、通常のFailureがCancellationを上書きしなくなったことを確認した。

### 5.4 R4-WU-04(実機2 Trial、Deviation含む32 Criterion、Compact Schema)

事前に共有Decoderの契約(`reason_code`/`evidence_refs`は省略可能)をUnit Testで固定した(`test_decode_criterion_reason_code_and_evidence_refs_are_optional_fields`)うえで、Gemma専用Schemaから両Fieldを完全に除去。

**Trial 1・Trial 2**(`test_a_real_32_criterion_initial_gemma_observe_judge_with_a_genuine_deviation_under_the_compact_schema`、`candidate_answer="The capital of France is Tenon."`で意図的にDeviationを誘発、Pinned Deterministic Sampling): 両Trialとも完全にClean、かつ完全に決定的(Batch毎の`completion_tokens`が2 Trial間でByte一致): Batch 1=279, Batch 2=267, Batch 3=274, Batch 4=281トークン。全4 Batch Strict Decode成功(`finish_reason=STOP`)、`all_decoded_id_count=32`、`missing_from_all_32=[]`、`result_execution_state='completed'`、`result_failure_reason=None`、`result_criteria_evaluated=31`、**`result_criteria_deviated=12`**(2 Trialとも同一Criterion IDが同一Batchで同一Dispositionを報告——完全決定的)。

**確定した結論**: R3-WU-05の実機Trialが確認した「Deviation報告のため`evidence_refs`/`reason_code`へ非空内容を書く必要がある場合に同種のMalformed JSON Defectが再発する」という残存Findingは、両Fieldそのものを共有Decoderの既存の省略可能性を利用してSchemaから完全に除去することで、2/2 Trialとも完全に解消された。R2/R3のSchema非曖昧化(Placeholderの実例化)はAll-Accept条件下でのみ有効だったが、R4-WU-04のCompact化はAll-Accept・Deviation双方の条件で有効であることを実機で確認した。2回とも成立したため、Handoffの「2/2成立した場合のみ次へ進む」ゲートを満たしR4-WU-05へ進んだ。

### 5.5 R4-WU-05

**Fixture(実`build_phase1_web_runtime()`経由)**: `context_size`を実配置と同じ`8192`へ修正した状態で`test_production_composition_root_32_criterion_gemma_enforce_golden_path`を実行、全Pass(旧`32768`のFixture限定水増し値を排除しても成立することを確認)。Sabotage: `context_size`を意図的に不足させた`3900`へ差し替えると、確実に失敗(`repair_rejudge_budget_insufficient`)することを確認済み(復元後再Diff一致)——これはFixtureの`_approx_token_count`が単なる甘い近似ではなく、実際にBudget不足を検知できる真のGateであることの直接証拠である。

**実機(1 Trial、Handoffの上限どおり)**: `test_a_real_production_composition_root_32_criterion_gemma_enforce_golden_path`実行(実`build_phase1_web_runtime()`経由、実Main`_RealMainWithFixedInitialAnswer`、実Gemma、Monkeypatchなし、実配置と同じ`context_size=8192`)。

実結果: `execution_state='completed' failure_reason=None criteria_selected=32 criteria_evaluated=30 criteria_deviated=10 repair_requested_by='main_governance' repair_outcome='improved' repair_accepted=True`。R3-WU-05が実機水準で`malformed_output`/`criteria_evaluated=0`/`criteria_deviated=0`のまま正直にFailしていた同一Golden Pathが、R4-WU-04のCompact Schema修正を土台として実機で完全に成功した。Judge Evidence File(実`LocalFilesystemRecordingWriter`経由)にも`model_identity=judge.gemma-4-e2b-it-q4-0`/`evaluated_model_identity=main.qwen3-4b-q4-k-m`/`repair_accepted=True`/実Artifact Digest/`backend_key=llama_cpp`が記録されていることを確認した。Handoffの1 Trial上限のため、2回目の確認的Trialは認可されておらず実施していない。

## 6. Focused/Static Verification

- 全体非Model Suite: **2382 passed, 37 deselected**(R3残差Rework後 2372 passed / 36 deselected から、新規Test純増分。全Sabotage-regression実施後も復元確認済みで最終的にこの数値で安定)。
- 全Suite実行中に、R3以前から残っていた`test_runtime_governance_routes.py`内1 Testが、R4-WU-01の請求-Local Ledger契約変更に伴い偽陽性状態から真の失敗状態へ転じたことを検出・修正した(Section 5.1)。
- Ruff(`src tests`): All checks passed(本Round中に発生した`F401`/`F821`/`E501`/`RUF002`の一時的な違反はすべて修正済み)。
- Canonical Mypy(`src tests`): **43 errors / 4 files**——Sessionを通じて完全不変(本Reworkの新規/変更Fileは0 error)。
- 実機Trial回数: R4-WU-04が2回(認可上限どおり)、R4-WU-05が1回(認可上限どおり)。計3回。事前/事後のProcess残存チェック(`ps`/`lsof`)は毎回Clean。

## 7. Internal Review

### Review A: Turn Snapshot Request-locality / Identity Matrix完結 / Composition Root

- [OK] Semantic Turn Snapshot/Freeze Failure/EvidenceはすべてRequest-local(`request_id`+`generation`帰属)になった: 別Turn開始で上書き・再Freeze・誤相関しないことを、Controller Review §3の3 Probeそのままの形でRegression化して確認した(R4-WU-01、Sabotage-regression済み)。
- [OK] UI向けLatest Current Pointerと実Turn Ledgerの分離: `current_snapshot()`/`latest_evidence()`は`begin()`内でのみ更新される独立Pointer経由のままであり、既存Status投影(`_point_status()`)の契約(遅延Turnの結果は現在のTurn表示を汚染しない)は無変更で維持されている(R4-WU-01)。
- [OK] Lock下での重複Begin/同一request競合防止: 2 Threadが同一`request_id`を同時Beginしても1 Generationのみが得られることを確定的なBarrier-based Testで確認した(R4-WU-01、Sabotage-regression済み)。
- [OK] Judge Identity 3経路(Dedicated Gemma・Main-shared・Built-in)すべてで、Handoffが要求した保存JSON全Field(`evaluated_model_identity`/`configured_judge_provider`/`active_judge_provider`/`model_identity`/Artifact/Backend/Version)を実`freeze_semantic_turn()`Fixture経由で直接Assertする形に完結した(R4-WU-02、Sabotage-regression済み)。
- [OK] R4-WU-05のFixture Testで、実`build_phase1_web_runtime()`(手組みではない実Production Composition Root)経由のGolden Pathが、実配置と同じ`context_size=8192`でも成立することを確認した(Sabotage-regression済み)。

### Review B: Cancellation Arbitration / Gemma Strict Decode / 実機Golden Path

- [OK] ENFORCE Wait LoopのCancellation Arbitrationは、Worker自身が確定した`cancelled`のみを再利用し、任意の`failed`はUser Stop/Main-priority Cancellationを上書きしなくなった(R4-WU-03、2固定Schedule共にSabotage-regression済み)。
- [OK] Gemma専用Compact Criterion Schema(`criterion_id`/`disposition`/`confidence`のみ)は、共有Decoderの既存の省略可能性を利用して導入され、共有Decoder・Selene Schema・Main-shared Promptには一切波及していない(R4-WU-04、Unit TestでSabotage-regression済み)。
- [OK] **R3から持ち越されていたGemma Malformed JSON Defect(Deviation報告時)は、R4-WU-04の実機2 Trial(完全決定的、Byte一致)で根絶を確認した**——All-Accept条件だけでなくDeviation条件(`criteria_deviated=12`)でも全Batch Strict Decodeが成立した。
- [OK] **R4-WU-05の実機Golden Path Trialは完全に成功した**(`execution_state='completed' repair_accepted=True`)——R3-WU-05が実機水準で`malformed_output`のまま停止していた同一Golden Pathが、R4-WU-04の修正を土台として実機で解決した。Handoffの1 Trial上限どおり、2回目の確認的Trialは実施していない(再現性はR4-WU-04自身の2 Trial決定性から推定されるのみで、Golden Path自体としては未検証)。

観点入れ替え後の再確認でも新規Findingなし。

## 8. Open Findings / True Stop

1. **R4-WU-05実機Golden Path Trialは1回のみ(Handoffの上限どおり)**: 再現性(同一条件での複数回一致)は確認していない——R4-WU-04自身の2 Trialが完全に決定的(Byte一致)だったこと、およびR4-WU-05自身が同一のPinned Deterministic Sampling契約下で動作することから、同一条件下での再実行も同じ結果になる可能性が高いと推定されるが、未検証の推定であり断定ではない。
2. **R4-WU-04のDeviation Trialにおける`result_criteria_evaluated=31`(32ではない)**: 全32 Criterionが正しくDecodeされた(`all_decoded_id_count=32`, `missing_from_all_32=[]`)にもかかわらず、`result.criteria_evaluated`が31と報告されている。これはCriterion単位の`passed+deviated`計算(既存の`_judge_criterion_counts`/`_semantic_criterion_counts`ロジック、本Round無変更)の挙動であり、31 passed/deviated + 1 unknown相当という実際の分布による可能性が高いが、本Roundでは深掘りしていない(Hard Assertionは`criteria_evaluated > 0`のみで、この数値自体の正確性は本RoundのScope外)。
3. **R2で報告済みのGuard(R2-WU-05)は本Roundで再確認していない**: 本RoundのScopeはController Reviewが指摘したIR-R3-01〜05のみであり、対象外だった(既存の解決状態は変更していない)。

未達項目をScope外へ事後的に変更したものは無い。

## 9. Action Inventory

- R4-WU-01: 解決(resolved)。
- R4-WU-02: 解決(resolved)。
- R4-WU-03: 解決(resolved)。
- R4-WU-04: 解決(resolved)——R3から持ち越されたGemma Deviation Malformed JSON Defectを実機2 Trialで根絶を確認。
- R4-WU-05: 解決(resolved)——Fixture(実Composition Root経由、`context_size=8192`)・実機(1 Trial、Handoff上限どおり)の両方でGolden Pathが完全に成立。
- R4-WU-06: 解決(resolved)——Focused/Static Verification・Internal Review A/B完全分離・本Return/Recovery提出。

## 10. Exact Next Action for Codex Controller

1. R4-WU-01/02/03の解決を受理するか判断する。
2. R4-WU-04によるGemma Malformed JSON Defect(Deviation報告時含む)の根絶Claimを、2/2実機Trialの決定的Evidenceに基づき受理するか判断する。
3. R4-WU-05の実機Golden Path成功(1 Trial)を受理するか、再現性未検証(Open Finding 1)を理由に追加Trialを要求するか判断する。
4. Open Finding 2(`criteria_evaluated=31`)について、追加調査を要求するか、既存ロジックの正常な挙動として現状のまま受理するか判断する。
5. Phase 9-1 Closureを主張するか、さらなるRoundを要求するかを判断する。
6. 本ReturnとRecoveryの内容を踏まえ、次のExact Handoffを発行する(必要な場合)。

新規PathのExact ReturnとRecoveryを提出し、Codex Controller Independent Review待ちで停止する。Phase Index／Current Registryは編集していない。既存Handoff／Return／Historyの上書きは行っていない。
