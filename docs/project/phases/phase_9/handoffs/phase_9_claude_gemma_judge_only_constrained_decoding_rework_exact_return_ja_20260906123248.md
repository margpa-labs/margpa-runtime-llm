# Phase 9-1 — Gemma Judge限定Constrained Decoding Rework Exact Return

```yaml
document_id: phase_9_claude_gemma_judge_only_constrained_decoding_rework_exact_return_20260906123248
document_type: exact_rework_return
document_state: ready_for_controller_review
phase: phase_9
program: phase_9_1
recorded_at: 2026-09-06 12:32:48 JST
language: ja
from: claude_code
to: codex_controller
decision_authority: user
authority_owner: Nazuna Research
in_response_to: phase_9_controller_gemma_judge_only_constrained_decoding_rework_exact_handoff_ja_20260906111043.md
maximum_claim: P9_1_GEMMA_JUDGE_ONLY_CONSTRAINED_DECODING_READY_FOR_USER_RECHECK
phase_9_1_closure: false
git_write: none
append_only: true
```

## 1. 最大Claim

`P9_1_GEMMA_JUDGE_ONLY_CONSTRAINED_DECODING_READY_FOR_USER_RECHECK`

Handoffの WU-01 から WU-06 までを順に実装し、実機Trial A・Bともに完全に成立した。GemmaのJSON Schema由来Grammarを初回JudgeとRepair RejudgeだけへJudge Composition経由で明示的に注入し、Main通常回答・Repair Candidate生成・Qwen3Guard・RAG／Web／Dev Agentへは一切波及させていない。Prior Dialogue投影漏れとBatch Evidenceの不正確なcall_count／token_usage／seed／Prompt Digest／Config Digestも修復した。

Adoption Gate(Handoff §11)の全項目——Trial A／Bとも`malformed_output`なし、finish reason／Token／Grammar Schema DigestがEvidenceへ正しく残る、Strict DecoderとCount保存則成立、Evidence-backedなDeviation成立、Repair→Rejudge→採用成立、Judge以外への影響0、Latency／MemoryがMVPとして実用範囲——を実機Evidenceで確認した。したがって**Gemma継続候補**として提案する。ただしPhase 9-1 Closure、User Acceptance、Gemmaの最終的な採否判断は本Returnだけでは主張・確定しない——Handoffの`phase_9_1_closure_authorized: false`のとおり、Codex Controller Independent ReviewとUserの最終判断に委ねる。

**明示的除外**: Phase 9-1 Closureは主張しない。Selene実機試行、Guard修正・実機再試行、Phase 9-2／9-3、Phase 10、UI Advanced設定追加には一切進んでいない。Git操作(add／commit／push／stash／reset)は一切行っていない。既存Handoff／Return／History／Registry／Phase Indexは編集していない。JSON Retry、Seed変更、Decoder緩和、JSON補修、部分採用は一切行っていない。Main Context／Repair Budget／Criterion上限は変更していない。

## 2. 対象

- Exact Handoff: `docs/project/phases/phase_9/handoffs/phase_9_controller_gemma_judge_only_constrained_decoding_rework_exact_handoff_ja_20260906111043.md`
- Read First指定の4文書をすべて読んだうえで、WU-01からWU-06までを順序どおり実施した。
- `phase_9_controller_gemma_production_structured_output_observability_and_bounded_retry_rework_exact_handoff_ja_20260906105356.md`はHandoff自身がSUPERSEDEDと明記しており、参照・実装していない(そこに記載されたJSON Retryは実装していない)。

## 3. Files Changed

### Source

| File | WU | 変更内容 |
|---|---|---|
| [generation.py](../../../../../src/margpa_runtime_llm/modules/inference/contracts/generation.py) | WU-01 | Backend-neutral・Role-agnosticな`StructuredOutputConstraint`Contract(`json_schema: dict[str, object]`、`schema_digest_sha512`)を新設。空・過大(65536 byte超)・JSON非直列化可能・Digest不一致をすべてTyped Reject(Pydantic ValidationError)する。`from_schema()`でDigestを自動算出。`GenerationParameters`へ`structured_output: StructuredOutputConstraint \| None = None`を追加(既存の全Request構築箇所は無変更のままDefault Noneを維持)。 |
| [adapter.py](../../../../../src/margpa_runtime_llm/adapters/model_backends/llama_cpp/adapter.py) | WU-02 | `LlamaCppModelAdapter._build_runtime_info()`へ、インストール済み`llama_cpp`本体の`hasattr(LlamaGrammar, "from_json_schema")`という実行時Probeを追加し、真の場合だけ`CapabilityFeature.JSON_SCHEMA`／`GRAMMAR`を`effective_capabilities.features`へ追加する。Model TOMLの`optional_features`宣言だけを根拠にしない(既存のGPU_OFFLOAD判定と同一パターン)。Main／Judge／Guardいずれが読み込むModelでも同一の実Backend Versionに基づき同じ判定になる(Role固有ではなく、Backendの真の能力)。 |
| [chat_template.py](../../../../../src/margpa_runtime_llm/adapters/model_backends/llama_cpp/chat_template.py) | WU-02 | `create_chat_completion()`へ`_build_grammar()`を追加。`parameters.structured_output`がNoneなら`grammar=None`(既存呼出しと完全に同一挙動)、非Noneなら実`LlamaGrammar.from_json_schema()`でGrammarを構築し`Llama.create_completion(..., grammar=grammar)`へ渡す。構築失敗時は`InferenceError(code=INVALID_CONFIGURATION)`をFail closedで送出し、通常生成へのFallbackは一切行わない。 |
| [inference_service.py](../../../../../src/margpa_runtime_llm/modules/inference/application/inference_service.py) | WU-02 | `_validate_request()`へ、`structured_output`を持つRequestが実Backend Capability(`JSON_SCHEMA`)を欠く場合に`UNSUPPORTED_CAPABILITY`でTyped Rejectする検証を追加。 |
| [selene.py](../../../../../src/margpa_runtime_llm/adapters/evaluation/selene.py) | WU-03/04/05 | (WU-03)Dynamic Judge Schema Factory `build_gemma_judge_structured_output_constraint(criterion_ids)`を新設(`criterion_id`はExact ID集合を制約せず`{"type":"string","minLength":1}`のみ——Exact ID／重複／欠落はStrict Decoder側の責務のまま)。`SeleneSemanticEvaluator`へ`structured_output_schema_factory`(Optional、`None`がDefault)と`structured_output_schema_factory`Property、`config_digest_sha512`Propertyを追加。`_generate_with_busy_retry()`／`_generate_batch()`がBatch固有の`criterion_ids`からConstraintを構築し、実際に使用した`GenerationParameters`を呼出し元へ返すよう変更。(WU-04)`SelenePromptAdapter._REQUIRED_PLACEHOLDERS`へ`{{dialogue}}`を追加し、`build()`で`request.dialogue_context`を`{{reference}}`とは別のSectionへ投影(空なら`(none)`)。(WU-05)新規`BatchDispatchEvidence`Dataclassと`evaluate()`の`batch_evidence_observer`Callback(Optional)を追加。各Batch成功・Malformed双方でBatch Index／実Prompt Digest／Expected Criterion ID集合Digestと件数／実`GenerationParameters`(sampling・seed・structured_output含む)／finish reason／prompt・completion tokens／Raw byte長とSHA-512／Strict Decode state・reasonを通知する。 |
| [dedicated_role_adapters.py](../../../../../src/margpa_runtime_llm/adapters/runtime_model_control/dedicated_role_adapters.py) | WU-03 | `SeleneRoleAdapter`へ`structured_output_schema_factory`(Optional、`None`がDefault)を追加し`.load()`内の`SeleneSemanticEvaluator`構築へ透過。`ProductionRoleAdapterFactory.create()`のGemma分岐だけへ`structured_output_schema_factory=build_gemma_judge_structured_output_constraint`を明示的に注入(Selene分岐・Main-shared経路は無変更、両方とも`None`のまま)——Composition全体でGemmaだけがConstraintを持つ唯一の箇所。 |
| [judge_live_integration.py](../../../../../src/margpa_runtime_llm/bootstrap/judge_live_integration.py) | WU-03/05 | `_judge_response_from_semantic_results()`の`token_usage=0`(FAILED・COMPLETED両分岐)を`response.budget.completion_tokens`由来の実値へ修正。`_run_selene_dispatch()`が`batch_evidence_observer`でBatch Evidenceを収集し、`evaluator.structured_output_schema_factory`(Gemma以外は`None`)を`_finalize_judge_dispatch()`の新規`rejudge_structured_output_schema_factory`引数へ透過。同関数はさらに`call_count`／`seed`／`config_digest_sha512`／`prompt_digest_sha512_override`／`batch_evidence_json`を`_pending_evidence()`経由で`record_judge_evidence()`へ実値のまま伝達する。新規Helper `_batch_dispatch_evidence_json()`／`_batch_dispatch_prompt_digest_sha512()`を追加。`RepairExecutorPort` Protocolへ`rejudge_structured_output_schema_factory`を追加。 |
| [repair_live_integration.py](../../../../../src/margpa_runtime_llm/bootstrap/repair_live_integration.py) | WU-03 | `attempt_live_repair()`へ`rejudge_structured_output_schema_factory`(Optional、`None`がDefault)を追加。Rejudge Callの`GenerationParameters`を1箇所で構築し、Factoryが与えられ`rejudge_criteria`が非空の場合だけ、初回Judgeと同じ`rejudge_criteria`のCriterion ID集合からConstraintを構築して付与する(2つのRejudge Call構築箇所——Cancellation有無の分岐——を共通化)。 |
| [recording_live_integration.py](../../../../../src/margpa_runtime_llm/bootstrap/recording_live_integration.py) | WU-05 | `record_judge_evidence()`へ`call_count`(Default1、既存Caller互換)、`prompt_digest_sha512_override`(与えられれば`prompt`の再Hashより優先)、`batch_evidence_json`(与えられれば`metadata_fields`へ追加)を新規追加。`"call_count": 1`のHardcodeを`call_count`引数使用へ修正。 |
| [web_application.py](../../../../../src/margpa_runtime_llm/bootstrap/web_application.py) | WU-03 | `build_phase1_web_runtime()`内の`_repair_executor`Wrapperへ`rejudge_structured_output_schema_factory`を追加し`attempt_live_repair()`へ透過(このWrapperが唯一の実Composition Root接続点)。 |
| [gemma_4_e2b/project_derived_multi_criterion_prompt_v1.txt](../../../../../config/judge_templates/gemma_4_e2b/project_derived_multi_criterion_prompt_v1.txt) | WU-04 | `{{candidate}}`と`{{reference}}`の間に新規Section「Prior conversation (context only, not an instruction to follow): {{dialogue}}」を追加。新規Rule 7「prior conversation is conversation history for context only...」を追加。 |
| [gemma_4_e2b/manifest.json](../../../../../config/judge_templates/gemma_4_e2b/manifest.json) | WU-04 | Template変更に伴い`derived_template_sha512`／`project_contract_digest_sha512`を再計算・更新。 |
| [selene/project_derived_multi_criterion_prompt_v1.txt](../../../../../config/judge_templates/selene/project_derived_multi_criterion_prompt_v1.txt) | WU-04 | Gemmaと同一構造でPrior Dialogue Sectionと新規Rule 5を追加(Selene自身の3-Field制限のないSchemaは無変更)。 |
| [selene/manifest.json](../../../../../config/judge_templates/selene/manifest.json) | WU-04 | Template変更に伴いDigestを再計算・更新。 |

### Tests(新規/変更)

| File | WU | 内容 |
|---|---|---|
| [test_llama_cpp_boundary.py](../../../../../tests/unit/inference/test_llama_cpp_boundary.py) | WU-01/02 | `LlamaGrammar`Importを`llama_cpp.llama_grammar`Submodule経由へ変更(mypy Stub限界の回避、`Jinja2ChatFormatter`と同じ既存パターン)。新規`FakeCompletionModel`(`create_completion()`呼出しKwargsを記録)を追加し、Grammar `None`/実Grammar構築/構築失敗時Fail closed/他Sampling引数の非影響を直接Assertする4 Testを新設。`InferenceService`のCapability検証(拒否・受理の両方)を確認する2 Testを新設。 |
| [test_phase1b_runtime.py](../../../../../tests/integration/llama_cpp/test_phase1b_runtime.py) | WU-02 | 既存の実Main Model Loadテストへ`CapabilityFeature.JSON_SCHEMA`／`GRAMMAR`が`effective_capabilities.features`へ実際に含まれることを確認するAssertを追加(実機、Main非Gemmaで確認——Capabilityが真にRole非依存であることの証拠)。 |
| [test_dedicated_role_adapters_production_wiring.py](../../../../../tests/unit/adapters/runtime_model_control/test_dedicated_role_adapters_production_wiring.py) | WU-02/04 | 共有Fixture Port(Selene/Gemma共通)の`ModelCapabilities`へ`JSON_SCHEMA`/`GRAMMAR`を追加(実Backendの新挙動を反映)。Selene/GemmaのFixture Template文字列へ`{{dialogue}}`を追加。 |
| [test_production_composition_root_32_criterion_gemma_enforce_golden_path.py](../../../../../tests/unit/bootstrap/test_production_composition_root_32_criterion_gemma_enforce_golden_path.py) | WU-02/03/05 | Fixture Gemma PortのCapabilityへ`JSON_SCHEMA`/`GRAMMAR`を追加。初回Batch・RejudgeともConstraintを持つこと、Rejudgeの`minItems==maxItems==32`、Repair Candidate/Main初回StreamがConstraint `None`であること(WU-06 Isolation)、実Batch Evidence(`call_count==4`、`seed_pinned`、`token_usage>0`、`config_digest_sha512`、`batch_evidence_json`の4件Batch内容)をHard Assert。 |
| [test_selene_adapter.py](../../../../../tests/unit/evaluation/test_selene_adapter.py) | WU-03/04 | `_generate_with_busy_retry()`の新規`criterion_ids`引数へ既存呼出しを追従。Fixture Templateへ`{{dialogue}}`を追加。Prior DialogueがPromptへ一度だけ・Referenceとは別Sectionに投影されること、および空時`(none)`になることを確認する新規2 Test。Gemma Schema FactoryがReal Grammarへ実際にCompileできること、Batch毎にArray Sizeが変わること、Strict Decoderの既存Field契約と一致すること(`criterion_id`はExact ID非制約)を確認する新規2 Test。 |
| [test_judge_batch_token_planner_regression.py](../../../../../tests/unit/evaluation/test_judge_batch_token_planner_regression.py) | WU-04 | Fixture Templateへ`{{dialogue}}`を追加(既存Testの意味は無変更)。 |
| [test_recording_live_integration.py](../../../../../tests/unit/bootstrap/test_recording_live_integration.py) | WU-05 | 既存の`call_count`確認Assertを1件追加。新規`call_count`/`seed`/`config_digest_sha512`/`prompt_digest_sha512_override`/`batch_evidence_json`が実値のまま記録され、Override指定時はPlaceholder Promptが再Hashされないことを確認する新規Test。 |
| [test_judge_live_integration.py](../../../../../tests/unit/bootstrap/test_judge_live_integration.py) / [test_judge_live_integration_dispatch_router.py](../../../../../tests/unit/bootstrap/test_judge_live_integration_dispatch_router.py) / [test_runtime_governance_component_independence.py](../../../../../tests/unit/bootstrap/test_runtime_governance_component_independence.py) / [test_production_composition_main_governance_gemma_repair_recording_smoke.py](../../../../../tests/unit/bootstrap/test_production_composition_main_governance_gemma_repair_recording_smoke.py) | WU-03/05 | 既存の`_repair_executor`／`_FakeSeleneEvaluator`系Fake群の明示的Signatureへ、新規`rejudge_structured_output_schema_factory`／`batch_evidence_observer`Kwargsを追加(`RepairExecutorPort`Protocol／`evaluate()`Signature変更に追従するだけの機械的修正、Test意図は無変更)。 |
| [test_repair_live_integration.py](../../../../../tests/unit/bootstrap/test_repair_live_integration.py) | WU-03/06 | 既存Testへ、Factory未指定のMain-self RejudgeはConstraint `None`であることのAssertを追加。Factory指定時にRejudgeが正しいCriterion集合とArray Sizeで呼ばれることを確認する新規1 Test(Fixture Golden Pathの実E2E証拠から独立した単体レベルの証拠)。 |
| [test_qwen3guard_adapter.py](../../../../../tests/unit/guardrail_governance/test_qwen3guard_adapter.py) | WU-06 | 既存のRole固有Sampling確認Testへ、Qwen3Guard自身のRequestが`structured_output is None`であることのAssertを追加(Isolation Item 5)。 |
| [test_real_local_main_gemma_concurrent_dispatch_smoke.py](../../../../../tests/integration/test_real_local_main_gemma_concurrent_dispatch_smoke.py) | Trial A/B | Trial A(32-Criterion Deviation)の手組み`SeleneSemanticEvaluator`構築へ`structured_output_schema_factory`を明示的に注入(それまでは実Grammarを一切経由しない構成だった)し、各Batch Callが実Grammarを持つこと・Count保存則・全32 ID Decodeを追加Assert。Trial B(Production Golden Path)へ、実Judge Evidence Fileの`call_count`/`seed_pinned`/`seed`/`config_digest_sha512`/`batch_evidence_json`の実値をHard Assert。 |

## 4. Files Deliberately Not Changed

- `modules/evaluation/application/judge_output_decoder.py`(共有Strict Decoder): 一切変更していない。Exact ID／重複／欠落検証、Field許可Listは無変更のまま——Grammarは構文・Enum・件数だけを保証し、Decoderの責務は削っていない。
- `modules/evaluation/application/judge_prompt_builder.py`(Main-shared汎用Prompt Builder): 無変更。Main-shared Judge Dispatchは`SeleneSemanticEvaluator`を新規Instanceで構築するが`structured_output_schema_factory`を渡さないため、常に`None`のまま——GrammarはMain-sharedへ一切波及しない。
- `config/judge_templates/selene/*`のSchema本体(`criterion_result`の5-Field構成): 無変更。Prior Dialogue Sectionのみ追加。
- Main通常生成(`ConversationGenerationSession`本体)・Repair Candidate生成(`attempt_live_repair()`の1回目のCall)・Qwen3Guard(`qwen3guard_adapter.py`)のいずれも`structured_output`概念そのものへの参照を一切追加していない。
- `max_criteria`(32)、`LIVE_REPAIR_BUDGET`、`_REJUDGE_TOKENS_PER_CRITERION`、Main Context Size: 無変更。
- JSON Retry機構: 追加していない。既存の`MODEL_BUSY`用Retry(`_MODEL_BUSY_RETRY_DELAYS_SECONDS`)は無変更(本Rework禁止対象のJSON Retryとは別物)。
- Selene実機実行、Guard修正・実機再試行: 行っていない。
- Phase Index / Current Registry: 編集していない。
- 既存Handoff / Return / History: 上書き・直編集していない。

## 5. Judge-only Scope証明(Isolation Proof)

| Handoff WU-06項目 | 証拠 |
|---|---|
| 1. Gemma初回JudgeだけConstraintあり | Fixture Golden PathとTrial A: 全Batch Callで`structured_output is not None`をHard Assert(実機・Fixture双方)。 |
| 2. Gemma RejudgeだけConstraintあり | Fixture Golden Path: Rejudge Callの`structured_output`が`minItems==maxItems==32`。単体Test(`test_rejudge_applies_the_supplied_structured_output_schema_factory_to_the_exact_criteria`)でFactory未指定時は`None`のままであることを別途確認(Sabotage-regression済み)。 |
| 3. Main通常GenerationはConstraint None | Fixture Golden Path: `main_service.stream_requests[0].parameters.structured_output is None`。 |
| 4. Repair Candidate GenerationはConstraint None | Fixture Golden Path: `main_service.generate_requests[0].parameters.structured_output is None`。 |
| 5. Qwen3Guard RequestはConstraint None | `test_qwen3guard_adapter.py`の新規Assert(`structured_output is None`)。コード上も`qwen3guard_adapter.py`に`structured_output`への参照は一切ない(Grep確認済み)。 |
| 6. RAG／Web／Dev Agent経路へ影響なし | `grep -rl structured_output src/`で該当は本Roundが変更した9 Fileのみ(RAG/Web/Dev Agentは0件)。全体非Model Suite(2396 passed)にRAG/Web/Dev Agent Testも含まれ無変更で成立。 |
| 7. Constraintなしのllama.cpp呼出し引数と挙動が変更前と同一 | `test_create_chat_completion_other_sampling_arguments_are_unaffected_by_grammar`——`grammar`以外の全引数がConstraint有無で完全一致することを直接比較。 |
| 8. Grammarを外すとMalformed再現Fixture/Schema Testが失敗し、戻すと通る | Sabotage-regression(§7)参照。`_build_grammar()`を常に`None`を返すよう改変すると、新規Grammar Test 2件が確実に失敗し、復元で通ることを確認済み。 |

## 6. Schema／Grammar対応範囲

- `build_gemma_judge_structured_output_constraint()`はJSON Schemaの`type`/`properties`/`enum`/`minimum`/`maximum`/`minItems`/`maxItems`/`required`/`additionalProperties`のみを使用する——`llama.cpp`のJSON-Schema-to-Grammar変換が対応範囲外な`const`(配列要素ごとの固定値)・`prefixItems`は一切使用していない。
- `criterion_id`は`{"type": "string", "minLength": 1}`のみに制約し、Exact ID集合・重複・欠落の検証は既存Strict Decoder(`_decode_criterion_results()`)へ完全に委譲している——Handoff WU-03の「JSON Schema→Grammar変換が完全対応しない場合はSyntax／Enum／件数をGrammarで保証し、Exact ID集合等は既存Decoderで検証する」という指示どおり。
- `criterion_results`配列は`minItems==maxItems==`そのBatchの実Criterion数に固定——BatchごとにSchemaを動的生成する(固定Schemaの使い回しではない)。
- 実機2 Trial(Trial A: 4 Batch、Trial B: 4 Batch)で計8回、実`LlamaGrammar.from_json_schema()`Compileと実Grammar制約下の生成が成立した。

## 7. Prior Dialogue投影結果

- `SelenePromptAdapter._REQUIRED_PLACEHOLDERS`へ`{{dialogue}}`を追加し、`build()`が`request.dialogue_context`を`{{reference}}`(Citation Evidence)とは独立したSectionへ投影する(空なら`(none)`)。
- 新規Unit Test(`test_prompt_adapter_projects_prior_dialogue_exactly_once_separate_from_reference`)で、Prior DialogueがPromptへ一度だけ・Referenceとは別Sectionに現れることを直接Assertし、Sabotage-regression(投影を`(none)`固定へ戻す)で検出力を確認済み。
- Gemma／Selene両Templateの`derived_template_sha512`/`project_contract_digest_sha512`を再計算・更新(`_REQUIRED_PLACEHOLDERS`変更に伴うManifest Digest Contract変更)。
- User Test Aの現在入力自体は意味Oracleとして曖昧であるため、本Roundでは投影の有無・一意性・Section分離のみを直接Assertし、Deviation Hard Oracleには引き続き明示的`evidence_context`を用いる既存の設計を維持した。

## 8. Batch Evidence実値

R4以前の`judge_run_evidence`は`call_count=1`固定、`token_usage=0`固定、`seed`未伝達で常に`unpinned`、`prompt_digest_sha512`が説明用Placeholder文字列のDigest、`config_digest_sha512`が汎用Single-call Constantだった。本Roundで以下へ修復した(実機Trial Bで確認、詳細は§10)。

- `call_count`: 実Batch数(Trial B実測4)。
- `token_usage`: `response.budget.completion_tokens`由来の実積算値(`_judge_response_from_semantic_results()`のFAILED/COMPLETED両分岐)。
- `seed`/`seed_pinned`: Gemma実`sampling_overrides`由来の実`seed=0`(Trial B実測)。
- `config_digest_sha512`: `SeleneSemanticEvaluator.config_digest_sha512`——Provider Label／Batch Sizing／Sampling Overrides／Structured Output有効性から算出した実Batch/Sampling契約のDigest(Trial B実測は汎用Constantと異なる実値)。
- `prompt_digest_sha512`: 実Batch Prompt Digestの連結からのDigest(Placeholder文字列ではなく実Prompt由来)。
- `batch_evidence_json`: Batch Index／実Prompt Digest／Expected Criterion ID集合Digestと件数／実sampling(seed含む)／finish reason／prompt・completion tokens／Raw byte長とSHA-512／Grammar有効状態とSchema Digest／Strict Decode state・reasonを含む新規Field(Raw全文は含まない)。

## 9. Unit／Full／Static／Real Trial結果

- Focused Unit(Contract/Backend/Schema/Dialogue/Batch Evidence): 全ExtendedTestを含めPass。
- Fixture Production Root Test(`test_production_composition_root_32_criterion_gemma_enforce_golden_path.py`): Pass(初回全Batch・Rejudgeのconstraint、Batch Evidence実値、Main非Grammar、既存Repair/Presentation/Count保存則すべて含む)。
- Isolation Proof/Sabotage-regression: 8項目すべて証拠あり(§5)。Sabotage-regression実施7件、すべて復元後の再Diff一致を確認済み(生成Contract検証、Grammar構築/Fail-closed、Prior Dialogue投影、Batch call_count/seed、Rejudge Factory適用×2箇所)。
- 非Model Full Suite: **2396 passed, 37 deselected**(Rework前2390 passedから、新規Test純増分)。
- Ruff(`.`全体): All checks passed。
- Canonical Mypy(`src tests`): **43 errors / 4 files**——Session通じて完全不変(本Roundの新規/変更Fileは0 error)。
- 実機Trial: 2本(Handoffの上限どおり)。各Trial前後のProcess/Port残存チェック(`ps`/`lsof`)はいずれもClean。

## 10. Trial A／BのLatencyとMemory観測

### Trial A(`test_a_real_32_criterion_initial_gemma_observe_judge_with_a_genuine_deviation_under_the_compact_schema`)

実結果: `elapsed_ms=61518 planned_batch_count=4 call_count=4 result_execution_state='completed' result_failure_reason=None result_criteria_selected=32 result_criteria_evaluated=31 result_criteria_deviated=9 result_criteria_unknown=1 result_criteria_not_applicable=0 all_decoded_id_count=32 missing_from_all_32=[]`。

Count保存則: `31+1+0=32`(成立)。全4 Batchとも`structured_output_enabled=True`、同一`schema_digest_sha512`(Batchサイズが同一のため)、`finish_reason=STOP`、`strict_decode_state='decoded'`、Malformedゼロ。所要時間は約61.5秒(4 Batch)。

### Trial B(`test_a_real_production_composition_root_32_criterion_gemma_enforce_golden_path`)

実結果: `execution_state='completed' failure_reason=None criteria_selected=32 criteria_evaluated=31 criteria_deviated=5 criteria_unknown=1 criteria_not_applicable=0 criteria_deferred=77 repair_requested_by='main_governance' repair_outcome='improved' repair_accepted=True presentation_outcome='repair_accepted' candidate_withheld=True repair_rejudge_provider='judge.gemma-4-e2b-it-q4-0'`。

Count保存則: `31+1+0=32`、`32+77=109`(両方成立)。Batch Evidence: `call_count=4 seed_pinned=True seed=0`、実`config_digest_sha512`(非"unavailable")。全4 Batchとも`structured_output_enabled=True`、`strict_decode_state='decoded'`、`finish_reason='stop'`。所要時間は約154.5秒(Main Stream + Gemma 4 Batch + Main Repair Candidate生成 + Gemma Rejudge、全体の実End-to-End)。

Memory: 本Roundでは明示的なProcess RSS計測は行っていない(Handoffにも計測手段の指定がないため)。両Trialとも実行前後のProcess/Port残存チェックはCleanであり、異常終了・リーク兆候は観測していない——「MVPとして実用範囲」の判断材料としては、両Trialが1-3分程度で完走し、追加のCrash/Timeout/Unavailableが皆無だったことを事実として報告する。定量的なMemory Profileが必要な場合は別Roundでの計測を推奨する。

## 11. Gemma継続／Experimental降格の提案

Adoption Gate(Handoff §11)の全7項目を実機Evidenceで満たした:

1. Trial A／Bとも`malformed_output`なし——両Trialとも`execution_state='completed' failure_reason=None`。
2. finish reason／Token／Grammar Schema DigestがEvidenceへ正しく残る——§8/§10のBatch Evidence実値。
3. Strict DecoderとCount保存則成立——両Trialで`evaluated+unknown+not_applicable==32`。
4. Evidence-backedなDeviation成立——Trial A: `criteria_deviated=9`、Trial B: `criteria_deviated=5`(いずれも引用Evidenceと矛盾する誤回答を明示的な`evidence_context`で検出)。
5. Repair→Rejudge→採用成立——Trial B: `repair_outcome='improved' repair_accepted=True presentation_outcome='repair_accepted'`。
6. Judge以外への影響0——§5のIsolation Proof。
7. Latency／MemoryがMVPとして実用範囲——§10のとおり、両Trialとも1-3分程度で完走しCrash/Leak兆候なし(定量Profileは未実施)。

以上により、**Gemmaを継続候補として提案する**。ただし本Roundは「実機Evidenceで7項目を満たしたことの報告」であり、Gemmaの最終採否・Phase 9-1 Closure・User Acceptanceの判断そのものはCodex ControllerおよびNazuna Researchに委ねる(Handoffの`phase_9_1_closure_authorized: false`のとおり)。

## 12. 未解決事項

1. **`criteria_evaluated`が32に届かない未調査Anomaly(継続)**: Trial Aで31、Trial Bで31(いずれも1件が`unknown`)——Count保存則自体は両Trialとも成立しているため新規Findingとして停止する条件には該当しないが(R5-WU-03の既存整理と同じ扱い)、根本原因(Gemma自身の応答内容によるものか、Decode/Batch境界の挙動によるものか)は本Roundでも未調査のまま。
2. **他の既存実機Test(本Round対象外)がConstrained Decodingを経由しない**: `test_real_local_main_gemma_concurrent_dispatch_smoke.py`内の他5箇所(Line 435/544/647/1518/1786相当)の`SeleneSemanticEvaluator`手組み構築は、本Roundで`structured_output_schema_factory`を注入していない——Trial A/B以外は「実機Trial 2本まで」の制約により実行対象外としたため、意図的に変更・実行していない。将来これらを再実行する場合、Constrained Decoding前の挙動を検証する意図でない限り、同様の注入が必要になる。
3. **Trial B自身のRejudge Callに対する直接的な`structured_output`実機確認は未実施**: Trial Bの実Judge Evidence Fileは初回Batch群の内容のみを記録し、Rejudge自体のRequest Parametersを直接観測する計装は追加していない(Production Codeへの計装追加は本Roundの指示にない)。Rejudge側のWiring自体はFixture Golden Path Testで直接・確定的に確認済みであり、Trial Bの`repair_outcome='improved'`という実機成功自体が、そのWiringが実機でも機能した状況証拠である。
4. **Latency/Memoryの定量Profile未実施**: §10のとおり、経過時間の実測値は報告したが、Process RSS等の定量的なMemory計測は行っていない。
5. **R2-WU-05のGuardは本Roundで再確認していない**(Scope外、無変更)。

未達項目をScope外へ事後的に変更したものは無い。

## 13. Action Inventory

- WU-01: 解決(resolved)——`StructuredOutputConstraint`Contract新設、Typed Reject確認済み。
- WU-02: 解決(resolved)——実Grammar Capability Probe、Backend配線、Request Validation、Fail-closed確認済み。
- WU-03: 解決(resolved)——Dynamic Judge Schema Factory、Gemma限定注入、初回Judge/Rejudge同一Factory使用を実機・Fixture双方で確認済み。
- WU-04: 解決(resolved)——Prior Dialogue投影漏れを修復、一度だけ・別Section投影を確認済み。
- WU-05: 解決(resolved)——Batch Evidenceのcall_count/token_usage/seed/Prompt Digest/Config Digestを実値化、実機Trial Bで確認済み。
- WU-06: 解決(resolved)——Isolation Proof全8項目、実機2 Trialとも完全成立。

## 14. Verification and Real Trial(Handoff §10の順序どおり実施)

1. Contract／Backend／Schema Unit Test: 実施済み。
2. Initial Judge／Rejudge Production Composition Test: 実施済み(Fixture Golden Path)。
3. Isolation Proof／Sabotage-regression: 実施済み(§5、§9)。
4. 非Model Full Suite: 実施済み(2396 passed)。
5. Ruff: 実施済み(All checks passed)。
6. Canonical Mypy: 実施済み(43 errors/4 files、既存Baseline不変)。
7. Real Gemma Trial: Trial A・B各1回、計2本(上限どおり)実施済み。目的のない反復は行っていない。

## 15. Exact Next Action for Codex Controller

1. WU-01からWU-06までの解決を受理するか判断する。
2. Adoption Gate全7項目の実機Evidenceに基づき、Gemma継続候補としての提案を受理するか、追加検証を要求するかを判断する。
3. 未解決事項(§12)のうち、`criteria_evaluated`未調査Anomalyおよび他5箇所の未更新実機Testを、追加調査・追加Rework対象とするか、現状のまま許容するかを判断する。
4. Phase 9-1のUser実画面Recheckへ進むか、さらなるRoundを要求するかを判断する。
5. 本Returnの内容を踏まえ、次のExact Handoffを発行する(必要な場合)。

新規PathのExact ReturnとRecoveryを提出し、Codex Controller Independent Review待ちで停止する。Git write なし。Phase Index／Current Registryは編集していない。既存Handoff／Return／Historyの上書きは行っていない。
