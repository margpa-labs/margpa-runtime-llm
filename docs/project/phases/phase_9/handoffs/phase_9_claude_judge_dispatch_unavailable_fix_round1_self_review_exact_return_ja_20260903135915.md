# Phase 9-1 Judge Dispatch "unavailable" Fix — Round 1実装＋3観点Self-Review Exact Return

```yaml
document_id: phase_9_claude_judge_dispatch_unavailable_fix_round1_self_review_exact_return_20260903135915
document_type: exact_bounded_implementation_return
document_state: candidate_for_controller_review
phase: phase_9
program: phase_9_1
created_at: 2026-09-03 13:59:15 JST
provider: Claude(Bounded Implementation Worker)
authorized_by: User直接指示「じゃ、直して。」(Root Cause確定Docの§8 Option A提案への承認)
  および「一周終わったら、3観点自己レビューして。でfindingあったらそのまま直して、
  でまた3観点自己レビューして。って繰り返しといて。」(自走Loop許可)
in_response_to: history/operations/phase_9_1_judge_dispatch_unavailable_failure_root_cause_confirmed_three_angle_investigation_ja_20260903132314.md
git_action: none
```

## 0. Maximum Claim

```text
P9_1_JUDGE_DISPATCH_LOCK_CONTENTION_FIX_ROUND1_APPLIED_NEW_OPEN_FINDING_SURFACED
CANDIDATE_FOR_CONTROLLER_REVIEW
```

Judge Dispatch "unavailable"問題の完全解消は主張しない。§4で正直に記録するとおり、
今回のFixは確認済みの1つの原因を確実に解消したが、実機再検証により**別の、正当な**
原因が新たに露呈しており、Round 2以降の対処または別Authority判断が必要である。

## 1. 実装したFix(Option A)

```text
対象: src/margpa_runtime_llm/adapters/model_backends/llama_cpp/adapter.py
  count_text_tokens() / count_chat_prompt_tokens()

変更: `_generation_lock`の非ブロッキング取得要求を完全に除去。`_state_lock`は
  従来どおり呼び出し全体で保持し続ける(unload()との競合防止に必要、Round 1
  Concurrency-Safety Reviewで独立に再確認済み、§3.1参照)。適格State判定を
  `_state is LOADED`から`_state in (LOADED, GENERATING)`へ緩和(Lock除去だけ
  では不十分で、この緩和も必須だったことをRound 1 Test Coverage Reviewが指摘、
  §3.2 Finding 5参照)。

理由: Tokenizeは`self._chat_template`(Model Vocabへの読み取り専用参照)のみに
  依存し、`_generation_lock`が実際に保護しているMutable Generation/KV-cache
  State(generate()/stream()のみが書き込む)には一切触れない。したがって
  実行中のgenerate()と並行して安全に呼び出せる。
```

## 2. Test変更

```text
tests/unit/inference/test_llama_cpp_boundary.py:
  - 既存Test`test_adapter_token_counter_obeys_loaded_and_busy_lifecycle`を
    `test_adapter_token_counter_obeys_loaded_lifecycle`へRename、旧Busy
    Assertion(Bug自体を検証していたTest)を除去。
  - 新規`test_adapter_token_counter_is_never_gated_by_an_in_flight_generation`
    追加(_state=GENERATING かつ _generation_lock保持中でもToken Countが
    成立することを確認、Fixの直接Regression Test)。

tests/unit/evaluation/test_selene_adapter.py:
  - 新規`test_plan_batches_failure_preserves_exception_code_in_failure_reason`
    追加(_plan_batches()内Exceptionの.codeがfailure_reason文字列へ保存
    されることを確認)。
  - 新規`test_generate_failure_preserves_exception_code_in_failure_reason`
    追加(run_tracked_stage()/generate()側Exceptionの.codeも同様に保存
    されることを確認)。

Focused Command: pytest tests/unit/evaluation/test_selene_adapter.py
  tests/unit/inference/test_llama_cpp_boundary.py -q -> 30 passed
Full Backend Suite: pytest -q -m "not model_smoke" -> 2253 passed, 22 deselected
Ruff/Mypy: 対象File Clean
```

## 3. Round 1 3観点Self-Review結果

### 3.1 Concurrency-Safety Adversarial Review — Finding無し

```text
Fixの中心的主張(Tokenizeと生成は別のNative Stateにしか触れない、および
unload()との競合Windowが実際には存在しないこと)を、Llama-cpp-python
0.3.34の実Install Sourceまで遡って行毎に検証した結果、破綻箇所は発見
されなかった。unload()のRace懸念(Lockが一度解放されてからmodel.close()
が走る点)についても、Token Counter側が呼び出し全体を通じて`_state_lock`
を握り続けるため、Interleaveが原理的に発生しないことを確認した。この
保護構造自体はFix前から不変であり、今回のFixが新たに依存したものでは
ない。唯一の残存不確実性は、Native Library内部(llama_tokenize自体)の
Thread-Safety保証をC++ Source非公開のため完全には検証できない点のみ
(Static Auditの限界として明記、Cを直接検証する手段は現状ない)。
```

### 3.2 Test Coverage／Regression-Breadth Audit — Finding複数、主要な物は本Roundで対処

```text
Finding 1(中〜高、対処済み): Selene/evaluate()層自体にMODEL_BUSY発生時の
  挙動を検証するTestが皆無だった。実際にBug症状が観測された層。
  -> §2の新規2 Test追加で対処。

Finding 2(中、未対処・Follow-up候補): 実機Smoke Test(test_real_local_
  gemma_e2b_judge_smoke.py等)に、今回のRoot Cause Doc §3が使った
  「短Budget Timeout直後に2連続Turn」を恒久Fixture化したものが存在しない。
  Model Smoke指定(Fast Suite除外)でCoreが重いため、本Round未対処。
  将来Follow-upとして残す。

Finding 3(中、情報共有): 新規Regression Test
  (test_adapter_token_counter_is_never_gated_by_an_in_flight_generation)
  は単一Thread内でState/Lockを手動Simulateしており、真の並行Threadでの
  検証ではない。ただしConcurrency-Safety Review(§3.1)がその側面を別途
  担当しているため、Gapとしては両Review間で埋まっている。

Finding 4(低〜中、未対処・Follow-up候補): generate()自体の排他性
  (_begin_generation()のMODEL_BUSY)を検証する高速Unit Testが実在せず、
  実機Smoke Testにのみ依存している。今回のFixが導入した問題ではない
  (Fix前から存在するTest Debt)。Fake Llama Model(create_completion対応)
  構築のCostを踏まえ、本Round未対処、Follow-up候補として記録のみ。

Finding 5(低、対処済み): Root Cause Doc §8 Option Aの記述が、実際に必要
  だった2つの変更(Lock除去 + State適格範囲緩和)のうち後者を明記して
  いなかった。本Doc §1で正確に記録することで対処。
```

### 3.3 実機End-to-End再検証 — CONFIRMED(狙った原因)だが新規発見あり

```text
`lock_contention_repro_post_fix_verification.py`(実Main+実Gemma同時Load、
実Registry、実109->32/77 Snapshot)で、修正前と同一Scenarioを再実行した。

確認1(Fix成立の直接証拠): Turn 2の`budget_calls_started`が0->1へ変化。
  Fix前はTurn 2が`_plan_batches()`の`count_chat_prompt_tokens()`Lock
  Checkで即座に失敗し、実Batch Dispatchへ一度も到達していなかった。
  Fix後は実際にBatch Dispatchを試みるようになった(Fixが狙った原因は
  確実に解消)。

確認2(新規発見、正直に記録): それでもTurn 2は最終的に同一の表示Category
  (`unavailable`)へ到達した。原因はもはやTokenize側のSpurious Lock競合
  ではなく、Turn 1の取り残しBackground Threadが"実際にまだGenerate中"
  である間にTurn 2自身の実generate()試行が`_begin_generation()`の
  (正当で、変更していない)MODEL_BUSY Checkに衝突したもの。これも同じ
  `selene.py`の汎用`except Exception`(L379-396)で捕捉され、同じ
  `unavailable`Categoryへ収束する。

  この経路はFixが導入した新規Bugではない — Fix前は必ずTokenize側の
  Spurious Lockに先に引っかかっていたため、この"正当な"Busy衝突経路
  自体が一度も表面化していなかった(1層目が2層目を覆い隠していた)。

確認3: generate()自体の排他性は変更どおり健全(実際に2並行generate()を
  試行し、後発が正しくMODEL_BUSYで拒否されることを実機確認)。

確認4: Teardown Clean(Registry Drain、Main保全、Process残存なし、
  Memory復帰)。
```

## 4. 本Roundで追加対処したこと(§3の指摘への直接対応)

```text
src/margpa_runtime_llm/adapters/evaluation/selene.py:
  新規`_diagnostic_exception_detail()`Helperを追加し、3箇所の汎用Exception
  収束点(L349-354 _plan_batches、L386-396 run_tracked_stage、L464-468
  decode)全てで、例外が`.code`属性(InferenceError.code等)を持つ場合に
  それをfailure_reason文字列へ含めるよう変更(Duck-typed、inference
  Moduleへの新規依存なし)。

  意図的にJudgeFailureReasonのCategory分類自体(judge_live_integration.py
  の3-prefix判定)は変更していない — 表示上は引き続き"unavailable"のまま。
  これは意図的な最小Scopeの判断である: §3.3で発見した「正当なBusy衝突」
  経路への本格対処(例えばTurn側でBoundedにWait/Retryする等)は、ENFORCE
  Pipelineの Timing／UX Tradeoffに関わる設計判断であり、Bounded
  Implementation Workerの権限外と判断し、本Roundでは実装していない
  (§5 Open Findingとして記録、別Authority判断を仰ぐ)。
```

## 5. 新規Open Finding(正直な記録、Source未対処)

```text
Open Finding 6(正当なProvider Busy衝突がJudge Dispatch失敗として観測
  される、Rapid-succession Turn限定):
  Turn Nの Judge Dispatchが`run_tracked_stage()`のTimeout/Cancellationで
  Background Threadを取り残し、そのThreadが実際にまだGenerate中である
  間にTurn N+1が同一Dedicated Adapterへ実Generate試行すると、正当な
  `MODEL_BUSY`が`selene.py`の汎用Exception Handlerに捕捉され、
  ユーザーには他の原因と区別不能な"unavailable"として表示される。

  今回のDiagnostic Detail追加(§4)により、永続Evidence上の生
  failure_reason文字列からは区別可能になったが(例:
  `gemma_e2b_unavailable:InferenceError:model_busy`)、UI表示・Judge
  Failure Category自体、および実際の成功率(Waitすれば高確率で成功する
  はずのTurnが即時失敗のままである点)は変更していない。

  考えられる対処候補(未実装、設計判断が必要):
    a) 当該Dedicated Adapterの`_generation_lock`がMODEL_BUSYを返した
       場合に限り、既存のinference_budget_ms/cancel_grace_ms予算内で
       Bounded Wait/Retryする(Stage Budgetという既存設計思想の自然な
       延長だが、_begin_generation()という共有基盤Codeの排他Semantics
       を変更するため、Main側Generate Pathへの影響も含め慎重な設計
       Reviewが必要)。
    b) JudgeFailureReasonへ新規Category(例: PROVIDER_BUSY)を追加し、
       UI側で「一時的、再試行で解消する可能性が高い」ことを明示する
       (Enum拡張はUI表示文字列・Frontend側Mapping・既存Test網羅性等、
       Blast Radiusが広く、単独では実装しない判断)。
    c) 何もしない(現状維持、Diagnostic Detail追加のみで留める) —
       Rapid-succession Turnの発生頻度・実User体験への実害を、まず
       実運用Evidenceで観察してから判断する。

  本Findingの対処方針はUser/Controller Authorityへ委ねる。
```

## 6. Recovery Index

```text
本Round差分:
  src/margpa_runtime_llm/adapters/model_backends/llama_cpp/adapter.py
    (count_text_tokens/count_chat_prompt_tokens、Root Cause Fix本体)
  src/margpa_runtime_llm/adapters/evaluation/selene.py
    (_diagnostic_exception_detail追加、3箇所へ適用)
  tests/unit/inference/test_llama_cpp_boundary.py
    (既存Test更新、新規Regression Test追加)
  tests/unit/evaluation/test_selene_adapter.py
    (新規Test2件追加)

Git/Commit/Push: なし。
```

## 7. Exact Next Action

```text
1. Round 2の3観点Self-Review(本Round差分=§4のDiagnostic Detail追加、
   および新規Testを対象)へ、User許可どおり自走で進む。
2. §5 Open Finding 6の対処方針は、Round 2以降で追加のSource変更を
   伴わない限り、本Task内ではこれ以上判断しない(Controller/User
   Authority待ち)。
```
