# Phase 9-1 — Component完全疎結合 R3残差Rework Exact Return

```yaml
document_type: exact_implementation_return
document_state: ready_for_controller_review
recorded_at: 2026-09-05 19:32:56 JST
language: ja
from: claude_designer_implementer
to: codex_controller
decision_authority: user
authority_owner: Nazuna Research
in_response_to: phase_9_controller_component_independence_r3_residual_rework_exact_handoff_ja_20260905181701.md
review_target_of_this_document: docs/project/phases/phase_9/history/operations/phase_9_1_component_independence_r2_return_controller_review_ja_20260905181701.md
maximum_claim: P9_1_R3_WU01_WU02_WU03_RESOLVED_WU04_NORMAL_ACCEPT_SCOPE_RESOLVED_WU05_FIXTURE_RESOLVED_REAL_TRIAL_FAILED_MALFORMED_ON_DEVIATION_CONTENT
phase_9_1_closure: false
git_mutation: none
append_only: true
```

## 1. 最大Claim

`P9_1_R3_WU01_WU02_WU03_RESOLVED_WU04_NORMAL_ACCEPT_SCOPE_RESOLVED_WU05_FIXTURE_RESOLVED_REAL_TRIAL_FAILED_MALFORMED_ON_DEVIATION_CONTENT`

Controller Review(2026-09-05 18:17:01 JST)が指摘したIR-R2-01〜05の全5件に対応した。R3-WU-01／02／03の3件は実装・新規Test・Sabotage-regressionで解決を確認した。R3-WU-04(Gemma Schema非曖昧化)は、Handoffが明示した「通常初回32 Criterion／4 Batch OBSERVE(All-Accept)」という定義済みScopeについては2回の実機Trialが両方とも完全にCleanで解決したが、その後R3-WU-05の実機Trialで**新たな残存Finding**を確認した——GemmaがDeviationを報告するために`evidence_refs`/`reason_code`へ非空の実内容を書く必要がある場合、同種のMalformed JSON Defectが再発する。R3-WU-05自体は、Fixture水準(実`build_phase1_web_runtime()`経由・実32 Criterion・Fake Gemma/Main)では完全に解決を確認したが、実機水準(1 Trial上限)では上記Findingにより`execution_state=failed`で終わった——これはHandoffが明示的に禁止した「Malformed／evaluated=0／Deviation 0のpytest.skip」を一切行わず、正直にFailのまま返した結果である。

**明示的除外**: Phase 9-1 Closureは主張しない。Selene、Phase 9-2／9-3、Phase 10、全面Rollbackには一切進んでいない。Git操作は一切行っていない。Current Registry／Phase Indexは編集していない。Decoder緩和・JSON補修・Retry追加は一切行っていない。

## 2. 対象

- Controller Review: `docs/project/phases/phase_9/history/operations/phase_9_1_component_independence_r2_return_controller_review_ja_20260905181701.md`
- R3 Exact Handoff: `docs/project/phases/phase_9/handoffs/phase_9_controller_component_independence_r3_residual_rework_exact_handoff_ja_20260905181701.md`
- R3-WU-01からR3-WU-06までを順序どおり実施。

## 3. Files Changed

### Source

| File | WU | 変更内容 |
|---|---|---|
| [runtime_governance.py](../../../../../src/margpa_runtime_llm/bootstrap/runtime_governance.py) | R3-WU-01 | `JudgeSemanticTurnProvider.__call__`が`judge_modes: JudgeExecutionModeSnapshot \| None`を第2引数として受理し、渡された場合はConversationが既に解決済みの`judge_mode`/`repair_mode`をそのまま使う(`_context_provider()`からの独立した二重読取を廃止)。Turn開始時のFreeze試行が失敗(例外)した場合、同一`request_id`の内部State(`_begin_attempted_request_id`/`_begin_failed`)へ記録し、以降の同一`request_id`呼び出しは`_context_provider()`/`coordinator.begin()`へ一切到達せず`None`を返す(Judge Completion Hookからの遅延Live再読を根絶)。戻り値型を`SemanticTurnSnapshot`から`SemanticTurnSnapshot \| None`へ変更。 |
| [conversation_generation.py](../../../../../src/margpa_runtime_llm/modules/conversation/application/conversation_generation.py) | R3-WU-01 | `semantic_turn_begin_hook`の型を`Callable[[str], object]`から`Callable[[str, JudgeExecutionModeSnapshot], object]`へ変更。`start()`内、既に解決済みの`judge_modes`をHookの第2引数として渡す(新規の独立読取は追加しない)。 |
| [judge_live_integration.py](../../../../../src/margpa_runtime_llm/bootstrap/judge_live_integration.py) | R3-WU-01 | `_run_judge_and_repair()`に、Completion時に解決した`active_adapter.provider_id`がTurn開始時Freeze済みSnapshotの`active_provider`と一致しない場合のGateを追加——Model Call 0、`SemanticDeferredReason.PROVIDER_IDENTITY_MISMATCH`を記録し`judge_provider_identity_mismatch`のTyped Failureを返す(Leaseは`_run_judge`側の既存`finally`で解放)。 |
| 〃 | R3-WU-02 | `_run_built_in_semantic_judge()`内の`_pending_evidence()`呼び出しで、`model_key=context.model_key`/`model_runtime_info=context.model_runtime_info`(Main自身の値)だった箇所を`model_key=_BUILT_IN_JUDGE_PROVIDER_ID`/`model_runtime_info=None`へ修正(Built-inはModel Call 0であり、Model Artifactを持たない事実を`unavailable`として正直に表す)。 |
| 〃 | R3-WU-03 | ENFORCE Wait Loopの`cancellation.is_cancelled()`分岐内で、Workerの`outcome_holder[0]`が既に`cancelled`/`failed`のTerminal Resultを保持している場合はそれをそのまま採用し、`model_access_coordinator.was_preempted()`への新規再問い合わせ(既にcleanup済みの可能性がある)を行わない。Workerの結果がまだ無い、または`completed`(正常完了とCancellationの同時発生)の場合のみ、従来どおり`was_preempted()`で再分類する。 |
| [semantic_criteria.py](../../../../../src/margpa_runtime_llm/modules/runtime_governance/domain/semantic_criteria.py) | R3-WU-01 | `SemanticDeferredReason`Enumへ`PROVIDER_IDENTITY_MISMATCH = "provider_identity_mismatch"`を新規追加。 |
| [selene.py](../../../../../src/margpa_runtime_llm/adapters/evaluation/selene.py) | R3-WU-04 | `SelenePromptAdapter.build()`のSchema例構築を`_criterion_result_example()`という新規Overridable Methodへ抽出(Selene自身の出力Byteは無変更)。新規`GemmaPromptAdapter(SelenePromptAdapter)`を追加——`_criterion_result_example()`のみOverrideし、`"short reference"`/`"short code"`という自然言語Placeholderを、構造的に現実的な単一の非曖昧JSON例(`evidence_refs: ["/rules/evidence/1"]`, `reason_code: "insufficient_evidence"`)へ置換。`build()`自身・Selene用の呼び出し元は無変更。 |
| [dedicated_role_adapters.py](../../../../../src/margpa_runtime_llm/adapters/runtime_model_control/dedicated_role_adapters.py) | R3-WU-04 | `SeleneRoleAdapter.__init__`へ`prompt_adapter_factory: type[SelenePromptAdapter] = SelenePromptAdapter`を追加(既定はSelene時と同一、無変更)。`preflight()`内の`SelenePromptAdapter(...)`直接構築を`self._prompt_adapter_factory(...)`へ変更。`ProductionRoleAdapterFactory.create()`のGemma分岐のみ`prompt_adapter_factory=GemmaPromptAdapter`を追加指定(Selene分岐は無変更)。 |
| [gemma_4_e2b/project_derived_multi_criterion_prompt_v1.txt](../../../../../config/judge_templates/gemma_4_e2b/project_derived_multi_criterion_prompt_v1.txt) | R3-WU-04 | R2で追加したRule 6(Placeholder複写禁止の注記Rule)を削除——Schema自体が非曖昧になったため、打ち消すRuleが不要になった。Selene用の同名File(別Path)には触れていない。 |
| [gemma_4_e2b/manifest.json](../../../../../config/judge_templates/gemma_4_e2b/manifest.json) | R3-WU-04 | Template変更に伴い`derived_template_sha512`/`project_contract_digest_sha512`を再計算・更新。 |

### Tests(新規/変更)

| File | WU | 内容 |
|---|---|---|
| [test_runtime_governance_component_independence.py](../../../../../tests/unit/bootstrap/test_runtime_governance_component_independence.py) | R3-WU-01 | Group E追加(2 Test): 既に解決済みの`judge_modes`がSnapshotの`frozen_judge_mode`/`frozen_repair_mode`として使われ、Context Providerの独立した(かつ意図的に異なる値を返す)Live読取が無視されることを確認。Turn開始Freeze失敗後、同一`request_id`の再呼び出しがContext Providerを再度呼ばずに`None`を返すこと、かつ別`request_id`(新規Turn)は正常にFreezeできることを確認。 |
| [test_judge_live_integration.py](../../../../../tests/unit/bootstrap/test_judge_live_integration.py) | R3-WU-01 | Provider Identity Mismatch(Turn開始時Active ProviderとCompletion時解決Adapterの不一致)がModel Call 0・Typed Failure・Lease解放を1回だけ実行することを確認するTestを新規追加。 |
| 〃 | R3-WU-02 | Built-in経路の実Judge Evidence File(実`LocalFilesystemRecordingWriter`経由)で、`model_identity=built_in.deterministic`(Main自身の値ではない)・`artifact_digest_sha512`/`backend_key`/`backend_version`が`unavailable`であることを確認するTestを新規追加。 |
| 〃 | R3-WU-03 | Controller Review IR-R2-03のController Probe Scheduleをそのまま再現するTestを新規追加——`_PollLoopDelayedCancellationToken`(Poll Threadの`is_cancelled()`のみをThread識別で選択的に保留)と、Workerの実Terminal Cleanup(`was_preempted()`がTrue→Falseへ遷移する瞬間)を確定的に検知してから保留を解除するWatcher Threadで、「Worker先行終了→Cleanup→Terminal Owner読取」を確定的に(Flakyな競合待ちではなく)再現し、ENFORCE Wait LoopがWorker自身の既に正しい`cancelled_by_main_priority_preemption`を上書きしないことを確認。 |
| [test_conversation_generation_semantic_turn_begin.py](../../../../../tests/unit/conversation/test_conversation_generation_semantic_turn_begin.py) | R3-WU-01 | R2既存の5 Testを新シグネチャ(`Callable[[str, JudgeExecutionModeSnapshot], object]`)へ更新(2引数で呼ばれることを前提とした形へ修正——旧シグネチャのままだと内部でTypeErrorが握り潰され、Testが偽陽性でPassしていた)。新規に、Hookの第2引数が実際に解決済み`JudgeExecutionModeSnapshot`であることを確認するTestを1件追加。 |
| [test_selene_adapter.py](../../../../../tests/unit/evaluation/test_selene_adapter.py) | R3-WU-04 | 実Production Gemma Manifest/Templateを`GemmaPromptAdapter`で描画し、`{{response_schema}}`部分を実際に`json.loads()`して必須Key集合・Field順・型を確認するTestを新規追加(`"short reference"`/`"short code"`が描画結果に一切含まれないことも確認)。Seleneの共有Schemaは無変更のまま維持されることを確認するTestも新規追加。 |
| [test_dedicated_role_adapters_production_wiring.py](../../../../../tests/unit/adapters/runtime_model_control/test_dedicated_role_adapters_production_wiring.py) | R3-WU-04 | 既存のGemma実Lifecycle経由Testへ、実際に送信されたPromptに`"short reference"`/`"short code"`が含まれないことを確認するAssertionを追加(`ProductionRoleAdapterFactory`の実配線で`GemmaPromptAdapter`が使われることの確認)。 |
| [test_production_composition_root_32_criterion_gemma_enforce_golden_path.py](../../../../../tests/unit/bootstrap/test_production_composition_root_32_criterion_gemma_enforce_golden_path.py)(新規) | R3-WU-05 | 実`build_phase1_web_runtime()`(Production Composition Root)を、実ARGD/DAGD Definitions経由の実32 Criterion Rotation Selectionで駆動するFixture Test。`build_phase1_application`/`build_governance_observer`のみMonkeypatch(Main/Gemmaの実Model Loadを回避、Evidence書込みFolderを`tmp_path`へ隔離)——それ以外(Provider Selection/Lifecycle、Judge/Repair/Recording Mode Controller、Main Governance Composition、実`SemanticRuntimeCoordinator`/`semantic_turn_begin_hook`配線、実`PersistentConversationService`、実Recording Writer)は無変更のProduction配線のまま。Fake Gemma Model Portは実際に受信したPrompt文字列から既知の32 Criterion IDを検出して応答を組み立てる(Batch境界を再実装せずに追従)。 |
| [test_real_local_main_gemma_concurrent_dispatch_smoke.py](../../../../../tests/integration/test_real_local_main_gemma_concurrent_dispatch_smoke.py) | R3-WU-04 / R3-WU-05 | 既存5箇所の`SelenePromptAdapter(manifest_path=GEMMA_MANIFEST)`を`GemmaPromptAdapter(manifest_path=GEMMA_MANIFEST)`へ置換(未使用になった`SelenePromptAdapter` importを削除)。R3-WU-04実機Testの新規追加(後述)。R3-WU-05実機Test`test_a_real_production_composition_root_32_criterion_gemma_enforce_golden_path`を新規追加——実`build_phase1_web_runtime()`経由、実Gemma(Monkeypatchなし)、実Main(`_RealMainWithFixedInitialAnswer`で初回回答のみ決定的固定・Repair Candidate生成は実Main)。Malformed／evaluated=0／Deviation 0を`pytest.skip`しない(Hard Assertのみ)。 |

## 4. Files Deliberately Not Changed

- `config/judge_templates/selene/*`: Gemma専用Schema非曖昧化はSeleneへ一切波及させていない(別Path、別Digest、`GemmaPromptAdapter`はSelene用呼び出し元から一切参照されない)。
- `modules/evaluation/application/judge_prompt_builder.py`(Main-shared汎用Prompt Builder): 無変更。
- `modules/evaluation/application/judge_output_decoder.py` / `adapters/evaluation/selene.py`の`decode_judge_output`呼び出し: Decoder緩和・JSON補修は一切行っていない(禁止事項)。
- Retry機構: 追加していない。
- Phase Index / Current Registry: 編集していない。
- 既存Handoff / Return / History: 上書き・直編集していない。

## 5. Real Evidence

### 5.1 R3-WU-01(Fixture-only、実Model不使用)

新規Group E 2 Test + `test_judge_live_integration.py`のProvider Mismatch Test 1件が全Pass。Sabotage-regression3件を実施、いずれも復元後の再Diff一致を確認済み:

- `JudgeSemanticTurnProvider.__call__`を旧(単一引数・毎回再Begin)実装へ戻すと、Group Eの2 Testが両方とも確実に失敗(`frozen_judge_mode`不一致 / `second is None`不成立)。
- `_run_judge_and_repair()`のProvider Identity Mismatch Gate(`if False:`へ置換)を除去すると、Mismatch Testが確実に失敗(`service.calls == []`不成立、実際にModel Callが発生)。

R2既存の`test_conversation_generation_semantic_turn_begin.py`5 Testは、新シグネチャへの追従漏れにより偽陽性でPassしていたことを全Suite実行で発見・修正した(Section 6参照)。

### 5.2 R3-WU-02(Fixture-only、実Model不使用)

新規Built-in Identity Test 1件が全Pass。Sabotage: `_pending_evidence()`の`model_key`/`model_runtime_info`引数を`context.model_key`/`context.model_runtime_info`へ戻すと、確実に失敗(`'main.qwen3-4b' == 'built_in.deterministic'`不成立)することを確認済み(復元後再Diff一致)。これでDedicated Gemma(R2-WU-02)・Main-shared(既存)・Built-in(本Round)の3経路すべてでIdentity分離を確認した。

### 5.3 R3-WU-03(Fixture-only、実Model不使用)

新規Terminal Race Test 1件(Controller Probe Scheduleの確定的再現)が全Pass。Sabotage: ENFORCE Wait Loopの新規Worker結果優先分岐を除去し旧(`was_preempted()`への無条件再問い合わせ)実装へ戻すと、確実に失敗(`'cancelled_by_request' == 'cancelled_by_main_priority_preemption'`不成立)することを確認済み(復元後再Diff一致)。

### 5.4 R3-WU-04(実機2 Trial、通常All-Accept Scopeの認可上限どおり)

**Trial 1・Trial 2**(`test_a_real_normal_32_criterion_initial_gemma_observe_judge_with_pinned_deterministic_sampling`、Gemma-only Schema非曖昧化後): 両Trialとも完全にClean、かつ完全に決定的(Batch毎の`completion_tokens`が2 Trial間でByte一致): Batch 1=349, Batch 2=407, Batch 3=403, Batch 4=429トークン。全4 Batch Strict Decode成功(`finish_reason=STOP`)、`all_decoded_id_count=32`、`missing_from_all_32=[]`、`result_execution_state='completed'`、`result_criteria_evaluated=32`。2回とも成立したため、Handoffの「二回とも成立した場合だけ次へ進む」ゲートを満たしR3-WU-05へ進んだ。

**確定した結論(R2からの訂正)**: R2のRule 6(Placeholder複写禁止の注記)による部分改善とは異なり、Schema自体からPlaceholder自然言語Phraseを完全に除去したことで、全Batch All-Accept(`evidence_refs`が常に空)の場合のMalformed JSON Defectは完全に解消された(2/2 Trial、100%決定的)。ただしこの結論は「Gemmaが空でない`evidence_refs`/`reason_code`を実際に書く必要がある場合」を検証していない——この限界がR3-WU-05で表面化した(5.5節)。

### 5.5 R3-WU-05

**Fixture(実`build_phase1_web_runtime()`経由)**: `test_production_composition_root_32_criterion_gemma_enforce_golden_path`実行、全Pass。実ARGD/DAGD Definitions(109 Criteria)から実Rotation Selectionで32 Criteriaを選択、Fake Gemma/Main経由で`repair_requested_by='main_governance'`・`repair_accepted=True`・同一32 Criterion RejudgeがGemma識別子で実施・実`PersistentConversationService`で同一Turnへ改善済み回答が保存・実Judge Evidence Fileに`model_identity=judge.gemma-4-e2b-it-q4-0`/`evaluated_model_identity=main.qwen3-4b`が記録されることを確認。Sabotage: `web_application.py`の`semantic_result_recorder`配線を`None`へ差し替えると、`repair_requested_by`が`None`のまま確実に失敗する(Main Governance自身のRepair Authorizationが機能しなくなる)ことを確認済み(復元後再Diff一致)——これはIR-R2-04が指摘した「手組みComposition」ではなく実Production配線を通していることの直接証拠である。

**実機(1 Trial、Handoffの上限どおり)**: `test_a_real_production_composition_root_32_criterion_gemma_enforce_golden_path`実行。実`build_phase1_web_runtime()`経由、実Main(初回回答のみ決定的固定文字列、Repair Candidate生成は実Main Generation)、実Gemma(Monkeypatchなし、`ProductionRoleAdapterFactory`/`SeleneRoleAdapter`/`GemmaPromptAdapter`が実際にLoad・Dispatch)。

実結果: `execution_state='failed' failure_reason='malformed_output' criteria_selected=32 criteria_evaluated=0 criteria_deviated=0 repair_requested_by=None repair_outcome=None repair_accepted=None`。**Handoffの指示どおりpytest.skipは一切行わず、Hard Assertionのまま正直にFailした**。`SeleneSemanticEvaluator.evaluate()`はBatch単位Fail-fast設計のため、`criteria_evaluated=0`は「全Batchが失敗した」ことを必ずしも意味しない——最初に失敗した1 Batch以前の成功結果も含めて破棄される。

**新規Finding(R3-WU-04の適用範囲に対する訂正)**: R3-WU-04の2 Trialは両方ともAll-Accept(`evidence_refs`が常に空)条件下でのみ検証されていた。本Trialは意図的にDeviationを誘発する回答(`"The capital of France is Tenon."`)を使ったため、Gemmaが`evidence_refs`/`reason_code`へ実際に非空の内容を書く必要がある——これはまさに元のMalformed JSON Defectが最初に発生した条件そのものである。実機1回のみの結果であり、Handoffの明示的禁止事項(Decoder緩和・JSON補修・Retry追加・追加のPrompt変更)によりこれ以上の実機Trialや修正は行っていない。

## 6. Focused/Static Verification

- 全体非Model Suite: **2372 passed, 36 deselected**(R2差分Rework後 2363 passed / 35 deselected から、新規Test純増分)。
- 全Suite実行中に、R2既存の`test_conversation_generation_semantic_turn_begin.py`内3 Testが、R3-WU-01のシグネチャ変更(`semantic_turn_begin_hook`が1引数から2引数へ)に伴い偽陽性状態から真の失敗状態へ転じたことを検出・修正した(Section 5.1)。
- Ruff(`src tests`): All checks passed。
- Canonical Mypy(`src tests`): **43 errors / 4 files**——Sessionを通じて完全不変(本Reworkの新規/変更Fileは0 error)。
- 実機Trial回数: R3-WU-04が2回(認可上限どおり)、R3-WU-05が1回(認可上限どおり)。計3回。事前/事後のProcess残存チェック(`ps`/`lsof`)は毎回Clean。

## 7. Internal Review

### Review A: Turn Freeze / Main OFF Call 0 / Provider切替 / Composition Root

- [OK] Evaluation Turn Contextの単一Freeze境界: `judge_modes`はConversationが一度だけ解決した値がSemantic Turn Snapshotへそのまま渡され、`JudgeSemanticTurnProvider`自身の独立Live再読は発生しない(R3-WU-01、Sabotage-regression済み)。
- [OK] Turn開始Freeze失敗後の遅延再Freezeは根絶: 同一`request_id`の再呼び出しはContext Providerへ一切到達せず`None`を返す(Sabotage-regression済み)。Main Chat自体はBlockされない(既存の`try/except: pass`経由)。
- [OK] Completion時解決Provider IdentityとTurn開始Active Providerの不一致はModel Call 0・Typed Failureへ収束する(R3-WU-01、Sabotage-regression済み)。
- [OK] Main OFF/absent → Main自身のSemantic Evidence/History/Action Decision Call 0は、R2-WU-01の既存Gate(`record_semantic_response()`/`record_semantic_deferred()`)がそのまま維持されている(本Roundでの変更なし、Full Suite再Pass確認済み)。
- [OK] R3-WU-05のFixture Testで、実`build_phase1_web_runtime()`(手組みではない実Production Composition Root)を通したEnd-to-Endが、Main Governance ENFORCE + Judge-side Repair Mode OFFという構成でも、Main自身のENFORCE権限がRepairを独立して認可することを確認した(Sabotage-regression済み)。

### Review B: Identity分離 / Terminal Race / Strict Decode / 32件Persistence Oracle

- [OK] Judge Evidenceの3経路(Dedicated Gemma・Main-shared・Built-in)すべてで`model_identity`(Executed Judge Provider)と`evaluated_model_identity`(Main自身)が正しく分離されている——Built-in経路の残存混同を本Roundで修正した(R3-WU-02、Sabotage-regression済み)。
- [OK] Cancellation起源のTerminal Race(Worker先行終了→Cleanup→Terminal Owner読取)は、Workerの既に確定した正しいClassificationを優先することで解消された(R3-WU-03、確定的なController Probe再現によるSabotage-regression済み)。
- [部分解決/残存Finding] Gemma Schema非曖昧化(R3-WU-04)は、Handoffが定義した「通常All-Accept 32 Criterion/4 Batch OBSERVE」というScopeについては2/2実機Trialで完全に解決した。しかしR3-WU-05の実機Trialで、Deviation報告のため`evidence_refs`/`reason_code`へ非空内容を書く必要がある場合に同種のMalformed JSON Defectが再発することを確認した——これはR3-WU-04自身の検証範囲外だった条件であり、当初のGemma JSON Defect全体としては未根絶のままである。
- [OK/正直な残存] 32件Persistence Oracle(同一Criterion集合がRejudgeまで維持される)は、Fixture水準では実`build_phase1_web_runtime()`経由で確認した(Sabotage-regression済み)。実機水準では、上記残存Findingにより初回Judge自体がFailしたため、Rejudgeまで到達しなかった——Oracle自体の設計に問題はなく、その手前の入力(初回Judge結果)が実機で得られなかったことによる。

観点入れ替え後の再確認でも新規Findingなし。上記[部分解決/残存Finding]は当初から想定しておらず、本RoundのWU-05実機Trialで初めて確認された、正直な新規Findingである。

## 8. Open Findings / True Stop

1. **Gemma Malformed JSON Defectは、Deviation報告時(非空`evidence_refs`/`reason_code`)については未根絶**: R3-WU-04のSchema非曖昧化はAll-Accept条件下で完全に有効だが、実際にDeviationを報告する必要がある条件では同種のDefectが再発することをR3-WU-05の実機Trialで確認した。Handoffの明示的禁止事項(Decoder緩和・JSON補修・Retry追加・追加のPrompt変更)、およびR3-WU-05自身の1 Trial上限により、これ以上の実機Trialや修正は行っていない。次の一手はCodex Controllerの明示的判断を待つ。
2. **R3-WU-05の実機Golden Pathは、上記Findingにより`repair_requested_by`/`repair_accepted`等のHard Assertionまで到達していない**: Fixture水準(Fake Gemma使用)では全Assertion含め完全に解決を確認しているが、実機水準ではGemma初回Judge自体がMalformed Outputで停止したため、Repair Authorization以降のOracleは実機では未検証のまま残る。
3. **R3-WU-05実機Trialは1回のみ(Handoffの上限どおり)**: 再現性(同一条件での複数回一致)は確認していない——ただしR3-WU-04の2 Trialが完全に決定的(Byte一致)だったことから、同一条件下での再実行も同じ結果になる可能性が高いと推定される(未検証の推定であり、断定ではない)。
4. **R2で報告済みのGuard(R2-WU-05)・Cancellation文字列統一(R2-WU-03)は本Roundで再確認していない**: 本RoundのScopeはController Reviewが指摘したIR-R2-01〜05のみであり、これらは対象外だった(既存の解決状態は変更していない)。

未達項目をScope外へ事後的に変更したものは無い。上記は全て当初のScope内でReal Evidenceが指し示した、正直な残存Findingである。

## 9. Action Inventory

- R3-WU-01: 解決(resolved)。
- R3-WU-02: 解決(resolved)。
- R3-WU-03: 解決(resolved)。
- R3-WU-04: 部分解決(partial)——Handoffが定義した通常All-Accept Scopeについては解決(2/2実機Trial)。ただしR3-WU-05実機Trialにより、Gemma JSON Defect全体としては未根絶であることが判明した。
- R3-WU-05: 部分解決(partial)——Fixture水準(実Composition Root経由)は解決。実機水準は1 Trialで正直にFail(Skipなし)。
- R3-WU-06: 解決(resolved)——Claim訂正・Focused/Static Verification・Internal Review A/B完全分離・本Return/Recovery提出。

## 10. Exact Next Action for Codex Controller

1. R3-WU-01/02/03の解決を受理するか判断する。
2. R3-WU-04の「通常All-Accept Scope解決」と「Deviation報告時の未根絶」という訂正されたClaim範囲を受理するか判断する。
3. R3-WU-05のFixture解決(実Composition Root経由)を受理するか、実機水準の未解決をもって全体を不受理とするか判断する。
4. 残存するGemma Malformed JSON Defect(Deviation報告時)について、次の一手(a. Schema内`evidence_refs`/`reason_code`のさらなる非曖昧化の追加認可、b. Decoder Tolerance方針への転換検討、c. 現状のまま次Phaseへ委ねる、のいずれか)を明示的に決定する。
5. Phase 9-1 Closureを主張するか、さらなるRoundを要求するかを判断する。
6. 本ReturnとRecoveryの内容を踏まえ、次のExact Handoffを発行する(必要な場合)。

新規PathのExact ReturnとRecoveryを提出し、Codex Controller Independent Review待ちで停止する。Phase Index／Current Registryは編集していない。既存Handoff／Return／Historyの上書きは行っていない。
