# Phase 9-1 Judge Dispatch "unavailable" Fix — Round 3 Bounded Retry実装＋3観点Self-Review Exact Return

```yaml
document_id: phase_9_claude_judge_dispatch_unavailable_fix_round3_busy_retry_and_self_review_exact_return_20260903185144
document_type: exact_bounded_implementation_return
document_state: candidate_for_controller_review
phase: phase_9
program: phase_9_1
created_at: 2026-09-03 18:51:44 JST
provider: Claude(Bounded Implementation Worker)
authorized_by: User直接指示「まず賛成する。で、万が一謎のループに入る可能性も考慮し、
  retryの回数は決めよう。例えば3回までとか。何回にするかは一旦任せるわ。それでしばらく
  使ってみて、多い（待ち時間が長すぎる）とかだったら、またその時考える。」
in_response_to: handoffs/phase_9_claude_judge_dispatch_unavailable_fix_round2_self_review_and_docs_correction_addendum_ja_20260903162057.md
  §5 Open Finding 6
git_action: none
```

## 0. Maximum Claim

```text
P9_1_JUDGE_DISPATCH_OPEN_FINDING_6_BOUNDED_RETRY_IMPLEMENTED_REAL_HARDWARE_
CONFIRMED_CANDIDATE_FOR_CONTROLLER_REVIEW
```

Judge Dispatchの完全な問題解消は主張しない。Retry機構自体は実機で有効性を確認したが、
実機再検証中に**別の、無関係な**問題(Gemma 4 E2Bの複数JSON Object出力によるDecode
失敗)を発見しており、これは本Taskのscope外として別途起票した(§6参照)。

## 1. 実装内容(Open Finding 6への対応)

```text
対象: src/margpa_runtime_llm/adapters/evaluation/selene.py

新規追加:
  _MODEL_BUSY_RETRY_DELAYS_SECONDS: tuple[float, ...] = (3.0, 6.0, 12.0)
  SeleneSemanticEvaluator._generate_with_busy_retry()

変更: _generate_batch()が、直接self._service.generate(...)を呼ぶ代わりに
  _generate_with_busy_retry()を呼ぶよう変更。

Retry判定: 例外の.codeが実際にInferenceErrorCode.MODEL_BUSY(Identity比較、
  文字列比較ではない)である場合のみRetry。それ以外(他のInferenceErrorCode、
  .code属性を持たない例外、Cancellation済み)は即座に再送出、Retryしない。

Retry上限: User指示どおり3回まで(念のため、謎のLoop防止)。Wait方式は
  cancellation.wait(timeout=...)を使用(Round 3 Self-Review内で自ら発見・
  修正、§3.1参照。当初はtime.sleep()だった)。
```

## 2. 実装経緯(誠実な記録: 初版から2点修正した)

```text
初版(User承認直後に実装):
  _MODEL_BUSY_RETRY_DELAYS_SECONDS = (1.0, 2.0, 4.0)  # 合計7.0秒
  Wait方式: time.sleep(delay)

Round 3 Self-Review(§3)で2つの問題を自ら発見・修正:

  修正1(Test Coverage監査Finding): このDocstring自体が「実機観測: Gemma
    ~1.7秒、Selene ~14.2秒」と書いていたにもかかわらず、Retry上限合計が
    7.0秒(<14.2秒)だった — 自分の挙げた根拠を自分の実装が満たしていない
    という矛盾。(3.0, 6.0, 12.0) = 合計21.0秒へ修正し、実機観測された
    最大値を明確に上回るようにした。

  修正2(Concurrency-Safety監査Finding): time.sleep()は中断不可能であり、
  本Codebaseの既存慣習(CancellationTokenの中断可能Wait、
  judge_live_integration.pyのENFORCE Wait Loop等)から外れていた。Main
  優先Preemption(Cancellation)がRetry待機中に発生した場合、最大で
  Delay分(旧: 最大4秒、新: 最大12秒)、反応が遅れる可能性があった。
  cancellation.wait(timeout=delay)へ変更し、Cancellationが発生した瞬間に
  即座にRetryを打ち切るようにした。
```

## 3. Round 3 3観点Self-Review結果

### 3.1 Correctness Adversarial Review — Finding 1件(対処済み)、Finding無し4件

```text
Finding(対処済み、§2修正2): time.sleep()の中断不可能性。上記のとおり
  cancellation.wait()へ変更して解決。

Finding無し(4件、詳細は監査Reportそのものを参照):
  - stage_deadline()/run_tracked_stage()との相互作用: 新規Orphan Threadを
    積み増す経路はない、既存Budgetの範囲内(独立確認)。
  - InferenceErrorCode.MODEL_BUSY Identity比較: 実Production経路(_begin_
    generation())では常に本物のEnum Memberが使われるため健全。
  - Main-shared Judge Dispatchでの再利用: Retry自体は同様に正当、ただし
    Main自身の非Judge通常Generate PathがこのRoot Causeから未保護のまま
    残っている点を指摘(Round 1 Handoffで既に開示済みの既知事項、Round 3
    Scope外として維持)。
  - Test 4件(初版分): 実Code Pathを正しく辿っていることを確認。
```

### 3.2 Test Coverage Audit — Finding5件、うち2件を本Round内で対処

```text
Finding 1(対処済み、§2修正1): Retry上限がDocstring自身の実機観測値
  (Selene 14.2秒)を下回っていた矛盾。数値修正、および今後の乖離を検知する
  Tripwire Test(test_model_busy_retry_window_covers_the_largest_documented_
  real_hardware_orphan)を追加。

Finding 2(対処済み): Retry Delay値そのもの(順序・具体値)を固定するTest
  が存在せず、pop()とpop(0)の取り違え等を検知できなかった。
  test_model_busy_retry_uses_the_documented_delay_sequence_in_orderを追加。

Finding 3(未対処、Follow-up候補): stage_deadline()のTimerがRetry Sleep
  "中"にCancellationを発火するCaseの専用Testが存在しない(現実のBudget
  ではRetry Windowよりはるかに大きいため実害はないと評価、Test追加は
  見送り)。

Finding 4(未対処、Follow-up候補として明示的にRound 1より優先度を上げて
  記録): 実機Regression Fixtureが存在しない。Round 1の同種指摘より
  Priorityが高いと評価された理由は、Round 3が実運用のTiming/Retry挙動
  そのものを変更する変更であり、かつFinding 1が示すとおり自己申告の
  数値だけでは判断を誤りうるため。

Finding 5(未対処、Follow-up候補): Main-shared Judge Dispatch + Busy
  衝突の組み合わせのTestが存在しない。
```

### 3.3 実機End-to-End再検証 — RETRY CONFIRMED EFFECTIVE(範囲内)

```text
実Main+実Gemma同時Load、実Registry、実109->32/77 Snapshotで、意図的に
短いBudgetでTurn 1のOrphan化を誘発し、直後にTurn 2を実行するCycleを
2回実施(初版のRetry値(1.0, 2.0, 4.0)秒に対して、まだ§2修正1適用前の
段階で実施)。

Cycle A: Turn 2の初回Attemptが実際にMODEL_BUSYへ衝突(生Exception捕捉)、
  1.0秒Sleep後の2回目AttemptでReal Generate(8.24秒)が成功。旧来の
  即時"unavailable"Signatureは消滅したことを実機で確認。

Cycle B: Busy衝突ゼロ(Orphanが既に解消済み)。

両Cycleとも、Turn 2は最終的に別の無関係な理由(下記§6)で失敗したが、
これはRetry機構自体の失敗ではなく、Busy衝突が正しく解消された"後"に
Real Generateが実際に実行され、その出力がDecode段階で問題を起こした
ことによるもの。Retry機構そのものの有効性は実機で確認された。

Clean Teardown確認済み(Registry Drain、Main保全、Process残存なし、
Memory回復)。
```

## 4. 追加Verification(§2修正後、最終)

```text
.venv/bin/python -m pytest tests/unit/evaluation/test_selene_adapter.py -q
  -> 16 passed
.venv/bin/python -m pytest -q -m "not model_smoke"
  -> 2260 passed, 22 deselected
Ruff format/check、Mypy: adapter.py, selene.py, 両Test File Clean
```

## 5. Loop収束についての判断

```text
Round 3では、Correctness監査・Test Coverage監査それぞれから実質的な
Findingが得られ、両方とも本Round内で対処した(§2、§3.2)。実機再検証は
Retry機構自体の有効性を確認しつつ、Scope外の別問題を発見した(§6)。

対処しなかったFinding(Test Coverage Finding 3〜5)は、いずれも
「今すぐ危険ではないが、あると良い」種のFollow-up候補であり、これ以上
本Loopを継続してもCode自体の新規Bug発見には至らないと判断する。Round 3
をもって本Loopをここで一区切りとし、User報告へ移行する。
```

## 6. Scope外で発見した別問題(正直な記録、Source変更なし)

```text
実機再検証(§3.3)中、Busy衝突ゼロの状態(Cycle B)でも、GemmaのReal
Generateが8-Criteria Batchに対して単一JSON Objectではなく複数(7個)の
JSON Objectを返し、decode_judge_output()が
"malformed_output:expected exactly one JSON object, found 7"で失敗する
ことを確認した。これはBusy衝突/Retry機構とは無関係な、Gemma 4 E2Bの
Prompt/Decode互換性に関する別問題であり、本Round(Open Finding 6対応)の
Scope外である。実機再検証を実施したAgentが、この発見を別Background Task
として提起済み(Task ID: task_cb580334)。本Taskでは対処しない。
```

## 7. Recovery Index

```text
本Round差分:
  src/margpa_runtime_llm/adapters/evaluation/selene.py
    (_MODEL_BUSY_RETRY_DELAYS_SECONDS, _generate_with_busy_retry追加、
     _generate_batch変更)
  tests/unit/evaluation/test_selene_adapter.py
    (新規Test6件追加、既存Fake拡張)

Git/Commit/Push: なし。
```

## 8. Exact Next Action

```text
1. 本Round(Round 1-3)全体の結果をUserへ最終報告する。
2. §6のGemma複数JSON Object問題は、別途起票済みのTaskとして
   Controller/User Authority判断待ちとする。
3. §3.2 Finding 3-5(実機Regression Fixture、Main-shared+Busy衝突Test、
   stage_deadline Timer中のCancellation Test)はFollow-up候補として
   記録するのみ、本Task内では対処しない。
```
