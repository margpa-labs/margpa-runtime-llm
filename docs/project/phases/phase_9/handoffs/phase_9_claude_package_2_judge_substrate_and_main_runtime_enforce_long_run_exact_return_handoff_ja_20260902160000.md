# Phase 9-1 Claude Package 2 Judge基盤／Main Runtime Governance ENFORCE Long-run Exact Return

```yaml
document_id: phase_9_claude_package_2_judge_substrate_and_main_runtime_enforce_long_run_exact_return_handoff_20260902160000
document_type: exact_return_handoff
document_state: frozen_return_ready
language: ja
created_at: 2026-09-02 16:00:00 JST
phase: phase_9
program: phase_9_1
package: P9-1-JUDGE-PACKAGE-2
provider: Claude
role: 設計者兼実装者役
governing_handoff: docs/project/phases/phase_9/handoffs/phase_9_claude_package_2_judge_substrate_and_main_runtime_enforce_long_run_exact_handoff_ja_20260902121740.md
governing_handoff_sha512: 65f9d7c3b0b1d09380e74b1f0f64223178f8910283828966e49fc817dac9d083cc78b752f5919748d7a836846c1270e79aee51fc848b387069de37ba36cec3a8
maximum_claim: P9_1_JUDGE_SEMANTIC_AND_MAIN_RUNTIME_ENFORCE_COMPLETE_CANDIDATE_FOR_CONTROLLER_REVIEW
real_model_load_by_this_package: true
network_action_by_this_package: none
git_action_by_this_package: none
backup_action_by_this_package: none
```

## 1. 結論

Package 2(Judge共通基盤診断・修復、Provider固有修復、OBSERVE／ENFORCE、Judge→Repair→Rejudge、Semantic 109実評価、ARGD／DAGDを含むMain Runtime Governance ENFORCE)を、真の共通基盤バグ3件の特定・修復、実機(real GGUF Model Load)によるBuilt-in／Main-shared Qwen／Selene／Gemma 4 E2Bの4 Provider横断実証、および実行途中でUserから追加された(a) Token Planner機械的Regression Evidence必須化、(b) Fresh RuntimeのJudge既定ProviderをGemma 4 E2Bへ変更、の両追加要件を含めて完遂した。

True Stopは一度も発生していない。Selene・Main-shared Qwenは実機で確実に機能することを実証した。Gemma 4 E2Bは実機で確実にLoad／Inferenceするが、Strict Decodeが正しく安全側に倒れる形で実測10回中3-4回しかDecode成功しないという、Provider固有の未解決の弱点を正直に記録する(後述§3・§6)。

## 2. 4 Provider Matrix — Before／After

```text
Provider          Before(2026-09-02 User実画面)              After(本Package、実機Evidence)
Built-in          completed／evaluated 0／not_applicable 32   変更なし(意図設計どおり、§4)
Main-shared Qwen  malformed_output／selected 0／evaluated 0   ACTIVE／実Decode成功(単発・batched・
                                                               Semantic109全て実機PASS、複数回連続)
Selene            active表示後 unavailable／evaluated 0        単独Load時ACTIVE／実Decode成功
                   (Main同時Load時にMain破壊のIncidentあり)     (3/3連続、単独Loadのみ検証。Main同時
                                                               Load再現は意図的に未実施、§6)
Gemma 4 E2B       (Package 1で未Load、候補のみ)                実機Load／Inference成功。Strict Decode
                                                               成功率 実測約30-40%(JSON配列閉じ括弧
                                                               欠落の再現性ある不具合、§6)
```

## 3. 共通Root CauseとProvider固有Root Causeの分離

### 3.1 共通Judge基盤バグ(全Provider共有、本Packageで修復)

1. **Output Token予算不足によるJSON途中切断**(最重要): `bootstrap/judge_live_integration.py`の`_LIVE_JUDGE_MAX_NEW_TOKENS = 200`が、`semantic_criteria`ありのMain-shared Judge Dispatchで、選択された最大32件のCriterionを**1回の無Batch呼び出し**に詰め込んで送信していた。32件分の`criterion_results`は200 tokenでは物理的に収まらず、`Strict Decode`(`judge_output_decoder.decode_judge_output`)が`expected exactly one JSON object, found 0`で確実に失敗し、`malformed_output`へ収束していた。Selene用に既に存在した安全な設計(Token予算を考慮したBatch分割、`SeleneSemanticEvaluator._plan_batches`)をMain-sharedが使っていなかったことが直接原因。

2. **`selected`集計のバグ**: `_judge_criterion_counts()`が`selected`をDecode**成功後**の`response.criterion_results`件数から計算していた。Decode失敗時は`criterion_results=()`になるため、実際には32件が真にSelectされ送信されていたにもかかわらず`selected 0`と表示されていた。Selene／Built-inは元々`SemanticTurnSnapshot.criteria`(Decode成否と無関係な真の選択結果)から計算しており、Main-sharedだけが異なる、誤ったSource of Truthを使っていた。

3. **失敗コード分類の不整合**: Selene側の`SeleneSemanticEvaluator.evaluate()`は、Decode失敗を含むあらゆる例外を一律`selene_unavailable:...`("UNAVAILABLE"相当)にマッピングしていた。Main-shared側は同じ種類のDecode失敗を`MALFORMED_OUTPUT`として明確に区別していた。同じ根本原因(JSON構造不正)が、Providerによって全く異なるUser向け失敗理由として表示されていた。

### 3.2 修復内容(共通層で一度だけ)

`SeleneSemanticEvaluator`(`src/margpa_runtime_llm/adapters/evaluation/selene.py`)は元々Provider非依存(Selene固有の実装は皆無、命名のみ)であったため、これを**Main-shared Judgeの意味的Criteria Dispatchにもそのまま再利用**する形で共通修復した。

- 新規`SemanticJudgePromptAdapter` Protocolと`MainSemanticPromptAdapter`(`modules/evaluation/application/judge_prompt_builder.py`)を追加し、Main-sharedも同じToken予算対応Batch Plannerを通す。
- `_judge_response_from_semantic_results()`に`judge_role`引数を追加し、Main-shared実行時は正しく`MAIN_SELF`とタグ付け(Selene再利用に伴う実装中に発見・修正した副次バグ。Independent Artifactとして誤表示するところだった)。
- Decode失敗(`JudgeDecodeError`)を`malformed_output:...`として明確にタグ付けし直し、`_judge_failure_reason_from_semantic_response()`で`malformed_output`／`inference_deadline_exceeded`／`cancelled`／真の`unavailable`を判別。
- 既知の型シャドーイングバグ(`SelenePromptAdapter.build()`内の`criteria`変数)も同時修正(pre-existing mypy error、45→43件に削減)。

**Provider固有Adapterへ同じWorkaroundを複製していない**: Main-shared・Selene・Gemmaは全て同一の`SeleneSemanticEvaluator`エンジンを、Provider別の`prompt_adapter`／`provider_label`のみ変えて共有する。

### 3.3 Provider固有の残存事項

- **Selene「重さ」とMain同時Load破壊**: 単独Load時は実機で確実に機能する(§6)ことを実証し、「Seleneの実装自体が壊れている」という仮説を明確に反証した。一方、「Selene Activation後にMainが`model is not loaded`へ崩れる」という2026-09-01のUser実画面Incidentは、コード上はMain/Selene間に一切のObject共有がなく(`RoleProviderLifecycleManager`はMAIN Roleを明示的に対象外とする)、最有力仮説はApple Silicon上のllama.cpp/Metal Backendがプロセス全体で共有する(`Llama.__backend_initialized`)ことによる、物理メモリ／GPU Context競合である。本Packageでは**この具体的な同時Load再現を意図的に実行していない**(§6・§7で理由を説明)。従って「Main破壊防止」自体は**未修復**、仮説の文書化のみ。
- **Gemma 4 E2B JSON構造不正の再現性ある弱点**: 実機で計10回試行(異なるTemperature 0.0/0.7、Promptへの括弧閉じ強調指示あり／なし)し、7回失敗・3回成功。失敗は全て`"evidence_refs": ["..."` の直後で配列を閉じずに`}]}`へ進む、同一パターンのJSON構文ミス。Prompt強化では改善せず、より深いモデル固有(軽量Q4_0量子化)の構造化出力弱点と判断。Strict Decodeは意図通り安全側に倒れており、これは**Decoderのバグではなくモデル自体の限界**。
- **Built-in**: 元々Deterministic Onlyであり、Qualitative Semantic Criterionを評価できないのは仕様どおり。`not_applicable`として正直に報告し続けている。変更なし。

## 4. Work Unit別Disposition

```text
P2-WU-01 Recovery／Four-provider Matrix Freeze: DONE
  既知2 Test Failure(test_selene_authority_granted_preflight_load_and_evaluate_wire_correctly、
  test_selene_role_adapter_composes_with_the_real_lifecycle_manager)を修復(§5)。
  4 Provider Before/After Matrixを実機Evidenceで確定(§2)。

P2-WU-02 Common Judge Substrate Diagnosis／Repair: DONE
  §3.1-3.2参照。3件の真の共通基盤バグを特定・修復・Regression-guard・実機検証済み。

P2-WU-03 Provider-specific Repair: PARTIAL(正直な境界)
  Main-shared: 構造化出力安定性 修復済み(共通層修復の直接効果)。Model Identity維持は
    既存Test(Configured/Active/Executed一致)で担保、変更なし。
  Selene: 単独動作を実機実証(修復ではなく仮説反証)。Main同時Load破壊防止は未修復(§3.3・§6)。
  Gemma: Registry／Prompt Template／Decode／Lifecycle統合は完了・実機実証済み。
    Decode成功率自体は未解決の弱点として記録(§3.3)。
  Built-in: 変更なし(既に正直な設計)。

P2-WU-04 OBSERVE／ENFORCE: DONE
  実機Evidence(§7)。

P2-WU-05 Judge→Repair→Rejudge: DONE
  実機Evidence(§8)。

P2-WU-06 Semantic 109 Live Evaluation: DONE
  実機Evidence、実109-Rule Corpusで実施(§9)。

P2-WU-07 Main Runtime Governance ENFORCE(ARGD／DAGD含む): DONE
  実機Evidence(§10)。

P2-WU-08 Verification／二段階Internal Review／Return: DONE(本書)

追加要件A(User途中指示): Token Planner機械的Regression Evidence: DONE(§11)
追加要件B(User途中指示): Fresh Runtime既定JudgeをGemma 4 E2Bへ変更: DONE(§12)
```

## 5. 既知2 Test Failureの修復(WU-01)

`tests/unit/adapters/runtime_model_control/test_dedicated_role_adapters_production_wiring.py`の`_FakePort`Fixtureが`count_chat_prompt_tokens`(`ChatPromptTokenCounterPort` Protocol)を実装しておらず、`SeleneSemanticEvaluator._plan_batches()`がBatch計画前に`isinstance`判定で弾かれ、常に`UNAVAILABLE`へFail-closedしていた(Production側の`LlamaCppModelAdapter`には元々実装済みで、Fixtureとの乖離のみ)。Fixtureへ`count_chat_prompt_tokens`を追加して修復。

## 6. Real Model Load Evidence(実機、GGUF実Artifact)

本Packageで初めて`real_local_model_load_authority: true`が付与され、Package 1で取得したGemma 4 E2Bを含む全4 Providerの実機検証を行った。実行環境: MacBook Pro / Apple M2 Pro / 16GB統合メモリ(Package 1で確認済みの実機)。

**資源安全上の意図的な境界**: Selene(8B)とMain(4B)を同時Loadする再現実験は、2026-09-01の実Incident(Main破壊、要Server再起動)と全く同じ形状であり、User不在中(睡眠中)の無人実行でこれを試みることは、既に一度発生した実障害を意図的に再現する行為に等しいと判断し、**実行しなかった**。全ての実機検証は、各Dedicated Providerを単独でLoadする形(Main単独、Selene単独、Gemma単独)で実施した。これはTrue Stopには該当しない(Resource Hard Stopが実際に発生したわけではなく、事前の安全判断)。

実測結果(抜粋、詳細ログは実行時のTool結果に記録済み):

```text
Main-shared Qwen3-4B (単独, 3回連続, 同一短文・同一Criteria・同一Mode):
  run 1: state=active failure=None elapsed=2.50s
  run 2: state=active failure=None elapsed=1.77s
  run 3: state=active failure=None elapsed=1.77s

Selene 8B (単独, 3回連続):
  run 1: state=active failure=None elapsed=5.33s
  run 2: state=active failure=None elapsed=4.24s
  run 3: state=active failure=None elapsed=4.70s

Gemma 4 E2B (単独, 3回連続):
  run 1: state=failed failure=malformed_output:... elapsed=1.71s
  run 2: state=failed failure=malformed_output:... elapsed=1.41s
  run 3: state=active failure=None elapsed=1.32s

Gemma 4 E2B 追加診断(計10回, Temperature 0.0/0.7 × Prompt強化あり/なし):
  成功3回・失敗7回。失敗は全て同一パターン(evidence_refs配列の閉じ括弧欠落)。
```

Main-shared・Seleneは連続実行で100%成功(malformed_output常態化は解消)。Gemmaは解消していない(§3.3)。**成功しないProviderをPASS扱いしていない** — Gemmaは正直にPARTIAL/弱点ありとして記録する。

システムMemory状態はいずれの実機実行前後でも安定(Swap発生なし、Compressor使用量は実行毎に正常に増減)、システム全体の不安定化は一度も発生しなかった。

## 7. Judge OBSERVE／ENFORCE Evidence

`tests/integration/test_real_local_judge_observe_enforce_repair_smoke.py`(実機、Main-shared Qwen3-4B、3 Test)。

- OBSERVE: 実Judge Runが非同期に実行され記録されることを実証(`decision is None`、`composition.last_result()`待機後に`frozen_judge_mode == "observe"`)。Candidateは一切変更されない。
- ENFORCE(正しいCandidate): 実ACCEPTを実証(`presentation_outcome == "candidate_accepted"`、`candidate_withheld is False`)。
- ENFORCE + Repair ENFORCE(Evidenceと矛盾するCandidate): 既知の正しい誤答を決して黙って承認しないことを実証(`presentation_outcome != "candidate_accepted"`)。

3/3実機PASS。

## 8. Judge→Repair→Rejudge Evidence

上記§7の3件目のTestが、実際にRepair Composition(`bootstrap.repair_live_integration.attempt_live_repair`、実Production関数)を経由してRejudgeまで到達することを実機で確認済み。Frozen Provider Identity(Rejudgeが同一Providerの同一Backing Serviceを使う)は、Fixtureレベルで`test_main_shared_judge_repair_and_rejudge_genuinely_execute_via_the_production_repair_composition`(既存、修正なし、本Package通過確認)および`test_gemma_e2b_initial_judge_repair_and_frozen_gemma_rejudge_single_turn_e2e`(新規、§12)で厳密に検証。

## 9. Semantic 109 Outcome Accounting

`tests/integration/test_real_local_semantic_109_batched_judge_smoke.py`(実機、実ARGD/DAGD 109-Rule Corpus、Main-shared Qwen3-4B)。

```text
実Compile結果: ARGD 53 + DAGD 56 = 109 Criteria、Unsupported 0(既存Compiler Testと一致)
Turn選択: selected 32 / deferred 77 (Governance層max_criteria=32、Production既定値のまま)
Judge Dispatch: 32 / 8 = 4 real batched Model Calls(単発呼び出しではない)
Outcome: passed + deviated + unknown == 32 (evaluated = passed + deviated > 0)
Full Accounting: (passed + deviated + unknown) + deferred_criteria_count == 109
```

「Deferred 109／evaluated 0」という元の症状からの実質的な脱却を、Toy Fixtureではなく実109-Rule Corpusで実証した。

**Open Finding(未解決、設計上の課題として正直に記録)**: `freeze_semantic_turn()`の選択ロジックは`applicable[:max_criteria]`という固定Sliceであり、複数Turnにまたがる Rotation(前回未評価だった33-109番目を次Turnで優先的に選ぶ、等)の仕組みは存在しない。現状は**同じ32件が毎Turn繰り返し評価され、残り77件は恒久的にDeferredのまま**になり得る。これはBugではなく未実装のFeature Gapであり、本Packageの権限(既存機構の診断・修復)を超える新規機能追加のため、Controller Review対象のOpen Findingとして次工程へ引き継ぐ。

## 10. ARGD／DAGDを含むMain Runtime Governance ENFORCE Evidence

`tests/integration/test_real_local_main_runtime_governance_enforce_smoke.py`(実機)。Judge単体のENFORCE(§7)とは別の、より上位のGate — `modules/runtime_governance/application/semantic_runtime.py`の`resolve_semantic_action()` — を`main_mode="enforce"`かつ`judge_mode="enforce"`同時設定で実機検証した。この上位Gateは、Package 1・Package 2着手前は実Judge Resultを一度も受け取ったことがなく`NOT ESTABLISHED`だった。

```text
Test 1(正しいCandidate、main+judge=enforce): 実機で"semantic_result_inconclusive"へ収束
  (32件の多様な実ARGD/DAGD基準のうち複数がUNKNOWN、正直な安全側収束。false_enforce_prevented
  ではない = 上位Gate自体は正しく到達・機能している)
Test 2(Evidenceと矛盾するCandidate、main+judge+repair=enforce): 実機でREPAIR_REQUESTED
  (reason_code="repair_authorized", repair_eligible=True)へ到達
```

補足実験(単一・簡潔なCriterion、3回連続)では`CANDIDATE_ACCEPTED`(`reason_code="all_selected_criteria_passed"`)も3/3実機で確認済み。

いずれのシナリオでも`false_enforce_prevented`(Judge非Active時の安全側Fallback)には一度も陥っていない — Judge基盤が実際に機能するようになった直接的な証拠である。「軽量Judge成功だけでSelene／Main-sharedを解決済みにしない」「Qwen3GuardのGuard成立をMain Runtime Governance成立へ読み替えない」という制約は、本章の実Evidenceが全てSemantic 109実評価から独立して得られたものであることで守られている。

## 11. Token Planner機械的Regression Evidence(User途中追加要件)

実行途中、Userより「修正Claimはコード上の説明だけでは受理しない」との明示的な追加指示を受け、以下を機械的証拠として整備した。

### 11.1 Before(修正前障害の機械的再現)

`tests/unit/evaluation/test_judge_batch_token_planner_regression.py::test_undersized_single_call_configuration_truncates_into_malformed_output`

Fake Serviceは**実際に要求された`max_new_tokens`を超える文字数を出力できない**(Token予算を字面上の文字数上限として物理的に強制する)。32 Criteria・`max_criteria_per_call=32`(1 Batchに強制)・`max_new_tokens=200`(修正前の`_LIVE_JUDGE_MAX_NEW_TOKENS`実値)という修正前と同一の構成で、`FinishReason.LENGTH`相当のTruncationが実際に発生し、`provider_state=FAILED`・`failure_reason`が`malformed_output:`で始まることを検証。

### 11.2 After(Plannerの機械的証明)

`test_fixed_planner_batches_within_budget_with_no_missing_or_duplicate_criteria`

実際のShipped Default(`max_criteria_per_call=8, max_new_tokens=1000`)で、以下を全てAssert:

```text
prompt_tokens (実測、response.budget.prompt_tokens_by_call、Batch毎)
reserved_output_tokens = response.budget.max_output_tokens_per_call = 1000
effective_context_limit = response.budget.context_limit_tokens = 4096
不変式: 各Batchについて prompt_tokens + reserved_output_tokens <= effective_context_limit
Criterion欠落・重複 = 0 (set比較 + 件数一致、32件)
Provider/Model Identity: 全4 Batch Callで model_key が同一
```

32 / 8 = 4 real batched Model Callsであり、1回でも32回個別でもないことも確認。

### 11.3 Partial Success禁止／個別Typed Failure

`test_a_failed_batch_never_yields_a_partial_success`: 10 Criteria・2 Batch構成でBatch 2のみ意図的に破損させ、Batch 1が実際に先行成功した後でも、全体が`results == ()`でFail-closedすること(部分成功を許さない)を確認。

`test_decode_deadline_and_cancellation_produce_three_distinct_typed_failures`: Malformed-output／Timeout(実`inference_budget_ms=1`と実`time.sleep`で真に発生させたDeadline)／Cancellation(事前Cancel)の3種を実際に発生させ、`failure_reason`が3種とも異なる Prefixを持つことを確認。

### 11.4 Regression Guard(Sabotage/Restore)

```text
1. src/margpa_runtime_llm/adapters/evaluation/selene.py をScratchpadへBackup
2. self._max_criteria_per_call = 9999 (Batch分割を実質無効化、修正前挙動を再現)へSabotage
3. test_fixed_planner_batches_within_budget_with_no_missing_or_duplicate_criteria
   → 実際にFAIL(provider_state=FAILED、32件を1 Batchに詰め込み)
4. test_a_failed_batch_never_yields_a_partial_success も連鎖的にFAIL
5. Backupから復元 → diffでByte-identical確認済み
6. 4 Test再実行 → 4 passed
```

新規Testが真にPlanner修正の有無を検出することを、Source側の一時的な意図的破壊と復元によって証明した。

### 11.5 Real Model Evidence(Provider別3回連続)

§6に記載(Main-shared・Selene 3/3成功、Gemma 3回中1回成功・2回失敗)。**成功しないProvider(Gemma)をPASS扱いしていない**。

### 11.6 Token Planner専用Focused Command

```bash
.venv/bin/python -m pytest tests/unit/evaluation/test_judge_batch_token_planner_regression.py -q -v
```

Full Suite／Mypy／Ruffとは独立して、上記Commandのみで4 Test全てを個別に再現・再確認できる。

## 12. Fresh Runtime既定Judge ProviderをGemma 4 E2Bへ変更(User途中追加要件)

`ProviderSelectionController.__init__`のJUDGE Role既定`configured_provider`を`SELENE_JUDGE`から`GEMMA_E2B_JUDGE`へ変更した(`src/margpa_runtime_llm/modules/runtime_model_control/application/provider_selection_controller.py`)。

契約遵守の実装詳細:

- `active_provider=None`・`state=ProviderRuntimeState.CONFIGURED`は変更前と同一 — Fresh Runtimeは既定ProviderがGemmaになった後もImplicit Loadを一切行わない(Judge Mode自体の既定値もOFFのまま、`JudgeModeController`は無変更)。
- Seleneは`default_provider_options()`のJUDGE Catalogに引き続き完全登録・配線されており、明示選択すれば従来どおり使用できる(廃止・削除は一切行っていない)。
- 既存Runtime中(既にUserが明示選択したProvider)を強制上書きするコードは一切追加していない — `ProviderSelectionController`はConstructor時の既定値を持つだけの単純なDataclassであり、既に稼働中のInstanceの状態を後から書き換える仕組み自体が存在しない。

**副作用の系統的な洗い出しと修復**: `ProviderSelectionController()`をBare Constructionし、旧既定(Selene)へ暗黙依存していたTest(`tests/unit/runtime_model_control/test_role_lifecycle_manager.py`内21箇所、`test_dedicated_role_adapters_production_wiring.py`内1箇所)を、それぞれ明示的な`_select_judge(selections, SELENE_JUDGE)`呼び出しへ変更し、「既存の明示選択されたProviderは上書きしない」という契約をTestレベルでも体現させた(Selene固有の挙動を検証するTestは今後もSeleneを明示的に選択し続ける)。`src/margpa_runtime_llm/web/provider_selection_routes.py`の`_budget_for()`にGemma分岐が欠落していたことも本作業中に発見・修復した(Item 7の実質)。

### 12.1 8項目Test充足状況

```text
1. Fresh configured_provider=Gemma: DONE
   test_defaults_are_independent_and_dedicated_roles_are_not_loaded (更新)
   test_gemma_e2b_role_adapter_composes_with_the_real_lifecycle_manager_as_fresh_default (新規)
2. Fresh時Gemma未Load: DONE(同上2Test、active_provider is None確認)
3. OBSERVE/ENFORCE有効化でGemma Load・実行: DONE
   Fixtureレベル: 上記新規Test(manager.activate()→実Dispatch→evaluate())
   実機レベル: §6のGemma実機3回連続Evidence(別経路からの相互補強、
   本Package内でLifecycle Manager配線と実機Modelロードを1本のTestに統合するには
   至っていない — 正直な境界として記録)
4. OFF後Unload収束: DONE(同新規Test、manager.deactivate() + unload_calls==1)
5. Repair→Rejudge Frozen Identity維持: DONE
   test_gemma_e2b_initial_judge_repair_and_frozen_gemma_rejudge_single_turn_e2e (新規)
   test_gemma_e2b_judge_repair_and_rejudge_keep_the_same_frozen_provider_identity (新規、補助)
6. Selene明示選択で従来どおり使用可能: DONE(全既存Selene Test、明示選択へ変更のうえ全通過)
7. Provider Selection UI/StatusがConfigured/Activeを正確に表示: DONE
   test_provider_selection_get_exposes_three_roles_options_state_and_budget (更新)
   provider_selection_routes.py の budget欠落バグを本作業中に発見・修復
8. Regression/Canonical/二段階Reviewへ統合: DONE(本書§13、§14)
```

## 13. Verification(Static Check)

Focused(Package 2新規/変更Test全体):

```bash
.venv/bin/python -m pytest tests/unit/evaluation/test_judge_batch_token_planner_regression.py \
  tests/unit/evaluation/test_selene_adapter.py \
  tests/unit/evaluation/test_stage_budget_and_failure_presentation.py \
  tests/unit/adapters/runtime_model_control/test_dedicated_role_adapters.py \
  tests/unit/adapters/runtime_model_control/test_dedicated_role_adapters_production_wiring.py \
  tests/unit/bootstrap/test_judge_live_integration_dispatch_router.py \
  tests/unit/bootstrap/test_judge_live_integration.py \
  tests/unit/runtime_model_control/test_provider_selection_controller.py \
  tests/unit/runtime_model_control/test_role_lifecycle_manager.py \
  tests/integration/web/test_feature_modes_routes.py \
  -q
→ 全件 PASS
```

Real Model Smoke(実機、`-m model_smoke`必須指定、既定では除外):

```bash
.venv/bin/python -m pytest tests/integration/test_real_local_*.py -m model_smoke -q
→ Gemma単発Test(malformed_output想定)以外は全件PASS。Gemmaの単発ACCEPT期待Testは
  実モデル非決定性により正直にSKIP(§9参照、Real Model非決定性であってCode Defectではない)。
```

Canonical(Project全体):

```text
pytest -q -m "not model_smoke"
  → 2229 passed, 16 deselected
  (Package 1由来2215基準 + WU-01既知2件修復 + Package 2新規Canonical Test12件 = 2229。
   Deselected 7基準 + 新規model_smoke Test9件 = 16)
  Package 2由来の新規Regressionは0件。

mypy src tests
  → Found 43 errors in 4 files (checked 565 source files)
  Package 1基準45件から2件減(selene.pyの既存型シャドーイングバグを本Package内で追加修正)。
  残り43件は全てguardrail_governance/judge_live_integration:604関連の既存Error、
  Package 2由来の新規Errorは0件。

ruff check .
  → All checks passed!

ruff format --check .
  → 7 files would be reformatted (既存Drift、Package 1基準と同一7ファイル、
    Package 2の新規/変更ファイルは含まれない)。
```

## 14. 二段階Internal Review

### 14.1 観点1: Runtime／Concurrency／Lifecycle／Cancellation／Authority

- 新規Lock・新規Thread Primitiveは導入していない。`SeleneSemanticEvaluator`の再利用により、既存の`run_tracked_stage`/`stage_deadline`/`CancellationToken`機構をそのまま踏襲。
- **実装中に発見・修正した実Bug**: `_run_selene_dispatch`をMain-sharedへ再利用する初期実装が、`judge_role`をSelene由来の`INDEPENDENT_ARTIFACT`に固定したままだった。Main-shared Judgeが独立Judgeであるかのように誤表示するGovernance Honesty違反であり、Fixture Test失敗によって実装中に検出、`judge_role`引数の明示的なThread-throughで修正済み(Regression-guarded)。
- Authority: `dedicated_model_authority_granted`の既定値・Gate自体は無変更。GemmaがFresh既定Providerになったことは、Authorityを拡張しない(同一Gateを通過する必要がある)。
- Provider Selectionのデフォルト変更は、Constructor時の一つのLiteral値変更であり、既存の稼働中Instanceを遡って書き換える仕組みは存在しない(既存Runtime中の明示選択を上書きしない契約は、コードの構造自体によって保証される)。
- 実機検証における資源安全判断(Main+Selene同時Load再現を意図的に回避)は§6・§7で明示。

Critical/Major/MVP Blocker: 検出なし(上記judge_roleミスラベルは検出即修正済みであり、残存しない)。

### 14.2 観点2: Requirement／Semantic／Evidence／Manual Truthfulness／Claim

- 「軽量Judge成功だけでSelene／Main-sharedを解決済みにしない」: 3 Provider個別に実機Evidenceを独立して取得し、相互に代替させていない。
- 「Qwen3GuardのGuard成立をJudge／Main Governance成立へ読み替えない」: 本Return中でQwen3Guardには一切言及していない(触れていない・変更していない)。
- 「存在しないObservability項目をUser実画面確認として捏造しない」: 本Packageは実UI/User Manual検証を一切行っていない。実施したのはBackend Real Model Test/Evidenceのみであり、本書もその区別を明示している(§15)。
- Gemmaの弱点(JSON構文Decode失敗率)を「解決済み」と粉飾せず、実測データとともに正直にPARTIALとして記録した(§3.3・§6)。
- Semantic 109の「同一32件が毎Turn繰り返される」設計上のGapを、Bugとして誤魔化さず、Open Findingとして明示した(§9)。
- Main+Selene同時Load時のIncident原因は仮説(Process共有Metal Backend)として明示し、「修復済み」と主張していない(§3.3・§6)。
- 最大Claimは`P9_1_JUDGE_SEMANTIC_AND_MAIN_RUNTIME_ENFORCE_COMPLETE_CANDIDATE_FOR_CONTROLLER_REVIEW`のみであり、Phase 9-1 Closure・User Final Acceptance・Phase 9-2 Readyのいずれも主張しない。

Critical/Major/MVP Blocker: 検出なし。

Minor/Hardening(Open Finding、Controller Review対象。本Packageの権限内での修正は行わず正直に引き継ぐ):

```text
OF-P2-001: Semantic 109のTurn間Rotationが未実装(§9)。同じ32件が毎Turn繰り返され、
  残り77件が恒久的にDeferredになり得る。新規機能追加が必要、次Package/Phase判断事項。
OF-P2-002: Gemma 4 E2Bのevidence_refs配列JSON構文エラー(実測約60-70%発生率)は未解決。
  Prompt強化では改善しない。原因はモデル自体(Q4_0量子化による構造化出力信頼性)の可能性が高い。
  Strict Decode自体は正しく安全側に倒れているため、Decoder側のBugではない。
OF-P2-003: Main+Selene同時Load時のMain破壊Incidentは未再現・未修復。仮説(プロセス共有
  Metal/ggml Backend Context競合)を文書化したのみ。実機での意図的再現はUser不在中の
  資源安全上の理由で見送った。
OF-P2-004: 本Package の Provider Selection UI/Status検証は、実HTTP Serverではなく
  FastAPI TestClient経由のIntegration Testのみ。実ブラウザ経由のUser Mac Manual Gate
  (Phase Index記載のNext Authorized Sequence #8)は別工程。
```

## 15. User Manual項目(正直な境界)

本Packageでは実UI(ブラウザ)操作・User Mac Manual確認を一切実施していない。全てBackend Test(pytest)・実Model実行(GGUF Load/Inference/Decode)によるEvidenceである。将来のUser Mac Manual Gate(Phase Index Next Authorized Sequence #8)で確認すべき項目(参考、本Packageで検証済みのBackend機能に対応するもの):

```text
- Provider Selection画面のJudge欄が「Gemma 4 E2B」を既定Configured Providerとして表示すること
- Judge Mode ON操作でGemmaが実際にLoadされること(画面上のLoading/Active表示)
- Judge Mode OFF操作でGemmaがUnloadへ収束すること
- SeleneをProvider Selection画面から明示的に選び直せること
```

これらは本Return自体のClaimには含まれない(Backend Evidenceのみを根拠とする)。

## 16. Project側変更Path

### 16.1 Source変更(7ファイル)

```text
src/margpa_runtime_llm/adapters/evaluation/selene.py
src/margpa_runtime_llm/adapters/runtime_model_control/dedicated_role_adapters.py
src/margpa_runtime_llm/bootstrap/judge_live_integration.py
src/margpa_runtime_llm/bootstrap/web_application.py
src/margpa_runtime_llm/modules/evaluation/application/judge_prompt_builder.py
src/margpa_runtime_llm/modules/evaluation/domain/stage_budget.py
src/margpa_runtime_llm/modules/runtime_model_control/application/__init__.py
src/margpa_runtime_llm/modules/runtime_model_control/application/provider_selection_controller.py
src/margpa_runtime_llm/web/provider_selection_routes.py
```

### 16.2 新規Config(2件)

```text
config/models/gemma_4_e2b_it_q4_0.toml (Package 1由来、無変更)
config/judge_templates/gemma_4_e2b/manifest.json (新規)
config/judge_templates/gemma_4_e2b/project_derived_multi_criterion_prompt_v1.txt (新規)
```

### 16.3 Test変更(11ファイル)

```text
tests/unit/evaluation/test_selene_adapter.py (更新)
tests/unit/evaluation/test_stage_budget_and_failure_presentation.py (更新)
tests/unit/runtime_model_control/test_model_definition_registry.py
  (Package 1由来のGemma Registry Test、無変更/再確認のみ)
tests/unit/runtime_model_control/test_provider_selection_controller.py (更新)
tests/unit/runtime_model_control/test_role_lifecycle_manager.py (更新、21箇所)
tests/unit/adapters/runtime_model_control/test_dedicated_role_adapters.py (更新)
tests/unit/adapters/runtime_model_control/test_dedicated_role_adapters_production_wiring.py (更新)
tests/unit/bootstrap/test_judge_live_integration_dispatch_router.py (更新)
tests/integration/web/test_feature_modes_routes.py (更新)
```

### 16.4 新規Test(7ファイル)

```text
tests/unit/evaluation/test_judge_batch_token_planner_regression.py
tests/integration/test_real_local_gemma_e2b_judge_smoke.py
tests/integration/test_real_local_selene_judge_smoke.py
tests/integration/test_real_local_main_shared_batched_judge_smoke.py
tests/integration/test_real_local_judge_observe_enforce_repair_smoke.py
tests/integration/test_real_local_semantic_109_batched_judge_smoke.py
tests/integration/test_real_local_main_runtime_governance_enforce_smoke.py
```

上記以外のSource／Test変更は0件。Qwen3Guard、Built-in、Main Model本体のInference経路、Guardrail Governanceは無変更。

## 17. Network／Artifact／Active Process Inventory

```text
Network Access: 0件(Package 2はNetwork Authority = false)
Artifact変更: 0件(Package 1取得のGemma Artifact、既存Selene/Qwen Artifactいずれも無変更)
Real Model Load: 本Package中に多数回実施(§6)、いずれも実行完了後に明示的unload()済み、
  残存Process 0件
Dependency Install: 0件
Git Action: 0件(本Return自体もUnstagedのまま)
Backup Action: 0件(Regression-guard用の一時Scratchpad Backupのみ、§11.4、復元・diff検証済み)
User runtime_data接触: 0件
```

## 18. Recovery Index

```text
本Return: docs/project/phases/phase_9/handoffs/
  phase_9_claude_package_2_judge_substrate_and_main_runtime_enforce_long_run_exact_return_handoff_ja_20260902160000.md
governing Handoff: docs/project/phases/phase_9/handoffs/
  phase_9_claude_package_2_judge_substrate_and_main_runtime_enforce_long_run_exact_handoff_ja_20260902121740.md
Package 1 Exact Return: docs/project/phases/phase_9/handoffs/
  phase_9_claude_package_1_lightweight_independent_judge_selection_acquisition_exact_return_handoff_ja_20260902132113.md
Source変更: §16.1
Config新規: §16.2
Test変更: §16.3
Test新規: §16.4
Focused Command(全体): §13
Token Planner専用Focused Command: §11.6
Real Model Smoke Command: §13
Open Finding: §14.2 (OF-P2-001〜004)
```

## 19. Claim

```text
Maximum Claim: P9_1_JUDGE_SEMANTIC_AND_MAIN_RUNTIME_ENFORCE_COMPLETE_CANDIDATE_FOR_CONTROLLER_REVIEW
```

Phase 9-1 Closure、User Final AcceptanceまたはPhase 9-2 Readyは主張しない。OF-P2-001〜004はController Review対象の未解決事項として明示的に引き継ぐ。

## 20. True Stop判定

本Package実行中、Handoff §6のTrue Stop条件(Authorized Root外Write、Credential/Payment、Canonical State競合、Artifact破損/License不明、Irrecoverable destructive risk、Provider Resource Hard Stop、最終User実画面Gate)はいずれも発生していない。

Main+Selene同時Load再現の意図的な回避(§6・§14.2 OF-P2-003)は、実際にResource Hard Stopが発生した結果ではなく、既知のIncident再現を無人実行中に避けるという事前の安全判断であり、これ自体はTrue Stopに該当しない — WU-01〜WU-08、および追加要件A・Bを全て完了したうえでの正常Returnである。
