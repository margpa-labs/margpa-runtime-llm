# Phase 9-1 — Gemma Constrained Decoding Final Contract Micro Rework Exact Return

```yaml
document_id: phase_9_claude_gemma_constrained_decoding_final_contract_micro_rework_exact_return_20260906131256
document_type: exact_return_handoff
document_state: ready
phase: phase_9
program: phase_9_1
recorded_at: 2026-09-06 13:12:56 JST
language: ja
from: claude_code
to: codex_controller
decision_authority: user
authority_owner: Nazuna Research
in_response_to: phase_9_controller_gemma_constrained_decoding_final_contract_micro_rework_exact_handoff_ja_20260906124425.md
phase_9_1_closure_authorized: false
git_write: none
append_only: true
```

## 1. 最大Claim

`P9_1_GEMMA_CONSTRAINED_DECODING_FINAL_CONTRACT_MICRO_REWORK_READY_FOR_USER_RECHECK`

Codex Controller Independent Reviewが指摘した3件(IR-FC-01/02/03)をすべて修正し、Sabotage-regression・非Model Full Suite・Ruff・Canonical Mypy・実機Golden Path 1回で成立を確認した。Gemma継続候補の提案は前Round(`phase_9_claude_gemma_judge_only_constrained_decoding_rework_exact_return_ja_20260906123248.md`)から変わらず維持する。ただしPhase 9-1 ClosureはCodex Controller/User側の判断であり、本Returnは主張しない。

## 2. 対象範囲(Scope Boundary遵守の確認)

- Constrained Decoding適用対象は初回Gemma Judgeと Repair Rejudgeのみ。Main通常回答、Repair Candidate生成、Qwen3Guard、RAG、Web、Dev Agentへの影響ゼロ(§7で機械的に再確認)。
- JSON Retry実装・Seed変更Retry・Decoder緩和・JSON補修・部分採用は一切追加していない。
- Gemma Prompt／Schema／Criterion／Budget／Contextへの追加Tuningなし。
- Selene・Guard・RAG・Web・Dev Agentの再実機試験なし。Phase 9-2/9-3/Phase 10作業なし。UI変更なし。
- Git write操作(`add`/`commit`/`push`/`stash`/`reset`)は一切実行していない。実行したGit操作は`git status --porcelain`(読み取り専用の状態確認)のみ。
- 既存Docsは無編集。本Returnと対になるRecovery Indexは、いずれも新規Pathで作成する。

## 3. IR-FC-01 — Gemma Rejudge Sampling契約の不一致(Before/After)

### Before

`attempt_live_repair()`のRejudge Callは`GenerationParameters(max_new_tokens=rejudge_plan.max_new_tokens)`のみから構築され、初回Judgeが使う`GEMMA_JUDGE_DETERMINISTIC_SAMPLING`(`temperature=0.0`/`top_p=1.0`/`top_k=1`/`min_p=0.0`/penalties=0/`repeat_penalty=1.0`/`seed=0`)を一切引き継がず、Library Default(`temperature=0.7`/`top_p=0.8`/`top_k=20`/`presence_penalty=1.5`/`seed=None`)に戻っていた。

### After

- `SeleneSemanticEvaluator`に読み取り専用`sampling_overrides`Propertyを追加([selene.py](../../../../../src/margpa_runtime_llm/adapters/evaluation/selene.py))。`structured_output_schema_factory`Propertyと同じ「Composition Rootが決める、`None`/空ならばDefault不変」パターンを踏襲。
- `attempt_live_repair()`に`rejudge_sampling_overrides: Mapping[str, object] | None = None`を追加。Rejudge Parametersは`GenerationParameters(max_new_tokens=rejudge_plan.max_new_tokens).model_copy(update=rejudge_updates)`で構築し、`rejudge_updates`はSampling Overridesと(既存どおり)`structured_output`のみを保持、`max_new_tokens`キーは明示的に`pop`して上書きされないことを保証([repair_live_integration.py](../../../../../src/margpa_runtime_llm/bootstrap/repair_live_integration.py))。
- `judge_live_integration.py`の`_run_selene_dispatch()`が`getattr(evaluator, "sampling_overrides", None)`でGemma固有の値だけを取得し、`_finalize_judge_dispatch()`→`repair_executor(...)`経由で伝播。Selene/Main-shared自身の`SeleneSemanticEvaluator`インスタンスは`sampling_overrides`を渡していないため空`{}`のままで、Rejudgeは以前と完全に同一のDefaultを維持する。
- `web_application.py`の`_repair_executor`ローカルClosureにも同じ引数を追加し、`attempt_live_repair()`へ透過。

### 非波及証明

- `test_a_normal_criterion_count_rejudge_succeeds_end_to_end_within_the_default_live_budget`([test_repair_live_integration.py](../../../../../tests/unit/bootstrap/test_repair_live_integration.py)): Override未指定のMain-selfRejudgeは`temperature=0.7`/`top_p=0.8`/`top_k=20`/`seed=None`のままであることを新規Assertで確認(Required Test「Factory/Override未指定の既存Rejudgeは現在のDefaultのまま」)。
- `test_rejudge_applies_the_supplied_sampling_overrides_matching_the_initial_judge_contract`(新規): `GEMMA_JUDGE_DETERMINISTIC_SAMPLING`を渡すと、Rejudge Callの`temperature=0.0`/`top_p=1.0`/`top_k=1`/`min_p=0.0`/`presence_penalty=0.0`/`frequency_penalty=0.0`/`repeat_penalty=1.0`/`seed=0`が成立し、`max_new_tokens`はRejudge Plan値(`_REJUDGE_TOKENS_PER_CRITERION*3`)のまま変わらないことを確認。
- `test_rejudge_sampling_overrides_never_leak_into_the_repair_candidate_call`(新規): 同じOverrideを渡してもRepair Candidate Call(`service.calls[0]`)は`temperature=0.7`/`seed=None`/`structured_output=None`/`max_new_tokens=_REPAIR_MAX_NEW_TOKENS`のまま不変であることを確認(「Repair CandidateにSampling/Grammarが逆流しない」)。
- Fixture Golden Path([test_production_composition_root_32_criterion_gemma_enforce_golden_path.py](../../../../../tests/unit/bootstrap/test_production_composition_root_32_criterion_gemma_enforce_golden_path.py))にも新規Assertを追加し、実Composition Root(`ProductionRoleAdapterFactory`のGemma分岐、実`GEMMA_JUDGE_DETERMINISTIC_SAMPLING`)経由でRejudge Callが`temperature=0.0`/`top_p=1.0`/`top_k=1`/`seed=0`を持つことを確認。初回Batch Callも同様。
- Sabotage-regression: `rejudge_updates`をSampling Overrides無視に改変 → `test_rejudge_applies_the_supplied_sampling_overrides_matching_the_initial_judge_contract`が`0.7 == 0.0`で失敗することを確認、復元後diff一致を確認。

## 4. IR-FC-02 — StructuredOutputConstraintのSchema/Digest不変性(Before/After)

### Before

`StructuredOutputConstraint`は`frozen=True`だがField自体が可変`dict`のため、構築後の`constraint.json_schema["type"] = "number"`が成功し、`schema_digest_sha512`は変更前の値のまま残った。`from_schema()`は非JSON直列化可能な入力に対して生の`TypeError`/`ValueError`を送出し、Contract自身のTyped Validation Failureへ収束していなかった。

### After

- `LlamaCppChatTemplate._build_grammar()`([chat_template.py](../../../../../src/margpa_runtime_llm/adapters/model_backends/llama_cpp/chat_template.py))がGrammar構築の直前に`constraint.json_schema`をCanonical再直列化・再SHA-512計算し、保持`schema_digest_sha512`と一致しない場合は`InferenceError(code=INVALID_CONFIGURATION)`でTyped Fail-closedにする(Grammar Compileへ進まない)。既存の"Compile失敗時のFail-closed"と同じ`InferenceErrorCode`・パターンを再利用。
- `from_schema()`は`json.dumps`のTypeError/ValueErrorを捕捉した場合、`cls(json_schema=schema, schema_digest_sha512="0"*128)`を呼ぶことで、Contract自身の`_validate_schema()`が同じ直列化を再試行して先に失敗し、既存の`ValueError`(Pydantic `ValidationError`として表面化)へ収束する。大規模API再設計・Nested Dict Deep-freezeは行っていない(Handoffの「大規模API再設計は不要」を遵守)。

### 証明

- `test_create_chat_completion_fails_closed_when_schema_mutated_after_construction`(新規、[test_llama_cpp_boundary.py](../../../../../tests/unit/inference/test_llama_cpp_boundary.py)): `GenerationParameters`構築後に`parameters.structured_output.json_schema["type"] = "number"`でMutateし、`create_chat_completion()`が`InferenceError(code=INVALID_CONFIGURATION)`を送出し、`model.create_completion_calls == []`(実Backend未到達)であることを確認。
  - 注記: `GenerationParameters(structured_output=constraint)`のConstructor自体は、Mutate前の`constraint`をそのまま渡した場合はPydanticが再Validationして即座に検出する(このProjectのPydantic設定での実際の挙動)。よってTestは「先に有効な`GenerationParameters`を構築し、その後Nested DictをMutateする」という、実際にController Probeが示した窓(既存Parametersオブジェクトに対する事後Mutation)を再現している。
- `test_structured_output_constraint_from_schema_converges_non_serializable_input_to_typed_failure`(新規): `StructuredOutputConstraint.from_schema({"type": object()})`が`pydantic.ValidationError`(メッセージに"not JSON-serializable"を含む)に収束することを確認。
- 既存の`test_create_chat_completion_builds_a_real_grammar_when_structured_output_is_set`等、正常Schemaの実Grammar構築Testはすべて継続Pass(再照合の追加が正常経路を壊していないことを確認)。
- Sabotage-regression: (a) `_build_grammar()`のDigest再照合を無効化 → Mutated Testが「DID NOT RAISE InferenceError」で失敗、復元後diff一致。(b) `from_schema()`のtry/exceptを除去 → 生の`TypeError`がPytestまで伝播し「converges」Testが失敗、復元後diff一致。

## 5. IR-FC-03 — Model Call 0時のEvidence Call Count(Before/After)

### Before

`judge_live_integration.py`の`_run_selene_dispatch()`は`call_count=len(frozen_batch_evidence) or 1`を`_finalize_judge_dispatch()`へ渡していた。全CriterionがPrompt Budget Deferredとなり実Batch Callが1件も発行されない場合(`frozen_batch_evidence=()`)でも、`call_count=1`が捏造されて記録されていた。

### After

`call_count=len(frozen_batch_evidence)`に変更(`or 1`Fallback削除)。非batched既存Caller(`_pending_evidence()`の他2箇所)は`call_count`引数自体を渡していないため、そのDefault`call_count=1`は無変更。Model Call 0時、`_batch_dispatch_prompt_digest_sha512()`/`_batch_dispatch_evidence_json()`はすでに空Tupleに対して`None`を返す実装だったため、Prompt Digest/Batch Evidenceの捏造は発生しない(`prompt_digest_sha512_override=None`は既存Fallback、`batch_evidence_json=None`はMetadataへ追加されない=「未設定」)。

### 証明

- `test_evaluate_with_zero_max_calls_makes_zero_model_calls_and_emits_zero_batch_evidence`(新規、[test_selene_adapter.py](../../../../../tests/unit/evaluation/test_selene_adapter.py)): 実`SeleneSemanticEvaluator(max_calls=0)`が`_plan_batches()`の`len(batches) >= self._max_calls`Guardにより全Criterionを即Deferredし、`self._service`(`generate()`)が一切呼ばれず(`service.requested_model is None`)、`batch_evidence_observer`も一度も呼ばれないことを確認(`response.budget.calls_started == 0`/`calls_completed == 0`)。
- `test_selene_shaped_dispatch_with_zero_batch_calls_records_evidence_call_count_zero`(新規、[test_judge_live_integration_dispatch_router.py](../../../../../tests/unit/bootstrap/test_judge_live_integration_dispatch_router.py)): `_FakeSeleneEvaluator`(`batch_evidence_observer`を一切呼ばないFake)で全Deferred相当のResponseをDispatchし、記録されたJudge Evidenceの`call_count == 0`、`seed`は`None`、`batch_evidence_json`はキー自体が存在しないことを確認。
- 通常4 Batch経路(`test_production_composition_root_32_criterion_gemma_enforce_golden_path.py`の既存Test、および実機Trial)は引き続き`call_count == 4`を維持することを確認(回帰なし)。
- Sabotage-regression: `call_count=len(frozen_batch_evidence)`を`... or 1`へ戻す → 新規Testが`1 == 0`で失敗、復元後diff一致。

## 6. 前ReturnのMemory/criteria_evaluated表現の訂正

Handoff §5の指示どおり、前Return(`phase_9_claude_gemma_judge_only_constrained_decoding_rework_exact_return_ja_20260906123248.md`)の以下2点を、既存Returnを書き換えずここに訂正として記録する。

- **Memory**: 前Returnは「Adoption Gate全7項成立」と記載したが、Memory RSS等は未計測であった。Latency実測とCrash/Timeout非発生は成立したが、Memoryの定量的成立までは主張しない。本Roundでも追加のMemory Profileは実施していない(Handoffが「今Roundで要求しない」と明記)。
- **criteria_evaluated**: 前Returnは`criteria_evaluated=31`(Trial A/B)を「未調査Anomaly」と表現したが、これは訂正する。現行定義`evaluated=passed+deviated`とCount保存則(`evaluated+unknown+not_applicable=32`)に照らせば、Unknown 1件は正常に説明された状態であり、Anomalyと呼ぶべきではない。Unknown 1件自体の判定理由(なぜGemmaがそのCriterionをUnknownと判定したか)は、本Roundでも追加調査していない(Handoffが「今Roundで追加調査しない」と明記)。

## 7. WU-06 Isolation再確認(退行なし)

本Micro Reworkの変更後も、Fixture Golden Pathの既存Assertが全てPassしていることを確認した:

- `main_service.generate_requests[0].parameters.structured_output is None`(Repair Candidate相当のMain初期Streamにも波及なし)
- `main_service.stream_requests[0].parameters.structured_output is None`
- `test_a_normal_criterion_count_rejudge_succeeds_end_to_end_within_the_default_live_budget`: Qwen3Guard/Main-self Rejudgeへの`structured_output`非波及(既存)、および今Round追加したSampling非波及(`temperature=0.7`等)。
- `test_qwen3guard_adapter.py`の既存Assert(`parameters.structured_output is None`)は無変更のまま継続Pass。

Sharedコード配置(`sampling_overrides`Property自体は`SeleneSemanticEvaluator`という共有Engineに存在する)が、全Role適用と混同されていないことは、Selene/Main-shared自身のConstruction箇所が本Roundで一切変更されていないこと(`SeleneRoleAdapter`のSelene分岐、`judge_live_integration.py`内のMain-shared用`SeleneSemanticEvaluator`Construction)で担保される。

## 8. Verification結果

1. **Focused Unit/Integration Test**: 新規6件すべてPass(内訳: IR-FC-01×2 + Golden Path Assert追加、IR-FC-02×2、IR-FC-03×2)。
2. **Judge-only Isolation既存回帰Test**: 全Pass(§7参照)。
3. **非Model Full Suite**: `2402 passed, 37 deselected`(前Round終了時点の2396から+6、新規追加分と一致)。
4. **Ruff**: `All checks passed!`(新規追加時に発生した`RUF002`/`RUF003`全角スラッシュ警告2件は半角`/`へ修正し解消)。
5. **Canonical Mypy**: `Found 43 errors in 4 files`——既存Baseline(`tests/unit/guardrail_governance/test_point_runtime.py`、`tests/integration/conversation/test_conversation_generation_guardrail_stream_integration.py`、`tests/unit/guardrail_governance/test_stream_guard.py`、`src/margpa_runtime_llm/bootstrap/judge_live_integration.py:631`)と完全一致、新規Error 0件。
6. **実機Golden Path(1回のみ)**: `tests/integration/test_real_local_main_gemma_concurrent_dispatch_smoke.py::test_a_real_production_composition_root_32_criterion_gemma_enforce_golden_path`を実機Apple Silicon上で1回実行、`1 passed in 158.29s`(exit code 0)。

### 実機結果(生Evidence)

```
execution_state='completed' failure_reason=None criteria_selected=32
criteria_evaluated=31 criteria_deviated=7 criteria_unknown=1
criteria_not_applicable=0 criteria_deferred=77
repair_requested_by='main_governance' repair_outcome='improved'
repair_accepted=True presentation_outcome='repair_accepted'
candidate_withheld=True repair_rejudge_provider='judge.gemma-4-e2b-it-q4-0'

call_count=4 seed_pinned=True seed=0
config_digest_sha512=9da5dca58d5b72f717a784a77f3df73cc4967e35c7152828dce565a1eb4577bfaba3dc114420432c9e6a6c009165b23d99133f124cf267ae70d981b929787c3a
```

Count保存則: `31+1+0=32`(成立)、`32+77=109`(成立)。全4 Batchとも`structured_output_enabled=True`/`temperature=0.0`/`top_k=1`/`top_p=1.0`/`seed=0`/`strict_decode_state='decoded'`/`finish_reason='stop'`。Repair→Rejudge→採用(`repair_accepted=True`, `presentation_outcome='repair_accepted'`)が同一Gemma Provider(`judge.gemma-4-e2b-it-q4-0`)で成立。

Process/Port確認: 実機Trial前後とも`ps`/`lsof -iTCP:8000`はともに空(残存なし、Killなし)。

### Rejudgeの固定Sampling(実機Trialでの取り扱いに関する正直な注記)

実機Golden Pathの`judge_run_evidence`は初回Batch DispatchのEvidence(`batch_evidence_json`)のみを実測記録しており、Rejudge Call自体のSampling値(`temperature`/`seed`等)は本番Evidenceとして計装されていない(前Roundの`structured_output`と同じ既存の設計上の制約であり、今Roundで新規Observabilityを追加することはHandoffの禁止事項に該当するため行っていない)。したがって、Rejudgeが実際に固定Sampling契約で走ったことの直接的な実機計装による確認はできていない。ただし、以下の状況証拠がある:

- Fixture Golden Path(実Composition Root経由、Model PortのみFake)で、Rejudge Callが`GEMMA_JUDGE_DETERMINISTIC_SAMPLING`と一致する`temperature=0.0`/`top_p=1.0`/`top_k=1`/`seed=0`を持つことを機械的に確認済み(§3)——本番の配線コード自体は実機Trialと完全に同一。
- 実機TrialはRepair→Rejudge→採用(`repair_outcome='improved'`, `repair_accepted=True`, `repair_rejudge_provider='judge.gemma-4-e2b-it-q4-0'`)が成立しており、Rejudge Callがクラッシュや設定不整合なく完走したことを示す。

これは前Round(`phase_9_claude_gemma_judge_only_constrained_decoding_rework_exact_return_ja_20260906123248.md`)がRejudgeの`structured_output`について採った同じ「機構レベルで証明済み、実機での独立計装なし」の扱いであり、新規のOpen Findingとして以下§9に記録する。

## 9. 未解決事項(Open Findings)

1. **Rejudge Samplingの実機独立計装なし**(§8末尾): Fixture Golden Path(実配線コード、Fake Model Port)による機械的証明と、実機Trialの成功(`repair_outcome='improved'`)という状況証拠にとどまる。Production Evidenceへの追加ではなく、テスト計装として実施可能かは次Roundの検討対象。
2. **`criteria_evaluated`のUnknown 1件判定理由**: Handoff §5により今Roundは追加調査しない(Anomalyではなく、Count保存則が成立する正常な既知の挙動として記録)。
3. **Memory(Process RSS)定量計測は未実施**: Handoff §5により今Roundは要求されていない。
4. **他5箇所の既存実機Test**(`test_real_local_main_gemma_concurrent_dispatch_smoke.py`内、Trial A/B以外)は本Round対象外のまま未更新・未実行(前Roundからの既知の制約、実機1回の上限内で対応せず)。
5. **R2-WU-05のGuard**は本Roundでも再確認していない(Scope外)。

## 10. Git

`git add`/`commit`/`push`/`stash`/`reset`は一切実行していない。実行したGit操作は`git status --porcelain`(状態確認のみ、書き込みなし)。

## 11. Next Step

Codex Controller Independent Reviewを待つ。Phase 9-1 Closure、User Acceptance、次Phase着手、追加の実機Trial、Selene実機実行、Guard修正・実機再試行、JSON Retry/Seed変更/Decoder緩和/JSON補修/部分採用、Main Context/Repair Budget/Criterion上限の変更のいずれも行わない。本Returnで停止する。
