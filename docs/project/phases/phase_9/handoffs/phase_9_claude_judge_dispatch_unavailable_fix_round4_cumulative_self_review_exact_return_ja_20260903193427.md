# Phase 9-1 Judge Dispatch "unavailable" Fix — Round 4 累積差分3観点Self-Review Exact Return

```yaml
document_id: phase_9_claude_judge_dispatch_unavailable_fix_round4_cumulative_self_review_exact_return_20260903193427
document_type: exact_bounded_implementation_return
document_state: candidate_for_controller_review
phase: phase_9
program: phase_9_1
created_at: 2026-09-03 19:34:27 JST
provider: Claude(Bounded Implementation Worker)
authorized_by: User直接指示「じゃ、3連観点入れ替え自己レビューしな。たぶん2個ぐらいは
  出てくると予想。」
in_response_to: Round 1-3累積差分(handoffs/phase_9_claude_judge_dispatch_
  unavailable_fix_round{1,2,3}_*.md)
git_action: none
```

## 0. Maximum Claim

```text
P9_1_JUDGE_DISPATCH_CUMULATIVE_DIFF_ROUND4_SELF_REVIEW_ONE_CORRECTION_
APPLIED_TWO_LOW_SEVERITY_OPEN_FINDINGS_RECORDED_CANDIDATE_FOR_CONTROLLER_
REVIEW
```

Round 1-3で得られたRound 1-3累積差分(adapter.py、selene.py、両Test File、
計565行追加/62行削除)を一つの纏まった変更として改めて3観点でSelf-Review
した。ユーザー予想どおり、実質的なFindingが複数得られた。

## 1. Round 4 3観点Self-Review結果

### 1.1 累積差分Integration監査

```text
確認された事実(Non-Issue、詳細確認済み):
  - Retry枯渇時の例外伝播経路(_generate_with_busy_retry -> stage_deadline
    -> run_tracked_stage -> evaluate()の外側except -> _diagnostic_
    exception_detail)を実際に辿り、Testでも再確認、正しく機能している。
  - Round 1(Tokenize時のLock除去)とRound 3(Retry)の組合せによる新規の
    Turn内並行アクセスPatternは生まれていない(_plan_batches()は常に
    Batch Loop開始前に同期完了するため)。
  - 同一Orphan Eventが二重に検出・処理されることはない
    (Cancellation Tokenの伝播経路がRound 3のRetry Loopとも正しく整合)。

Finding(Docs-only、対処済み): _MODEL_BUSY_RETRY_DELAYS_SECONDS Docstring内
  のTest名参照が実際のTest関数名と食い違っていた(末尾"_observation"の
  有無)。§2で修正。

Finding(Plausible-Risk、未対処・Open Finding化):
  1) stage_deadline()自身のTimerが、Retry待機中(cancellation.wait())に
     発火した場合、素のMODEL_BUSY例外がそのまま再送出され、本来の
     "..._inference_deadline_exceeded"(TIMEOUT分類)ではなく
     "unavailable"(UNAVAILABLE分類)として誤って報告されうる。現在の
     実Production Budget(inference_budget_ms=120,000ms)はRetry Window
     最大21秒を大きく上回るため到達不能だが、将来より小さいBudgetが
     設定された場合に顕在化しうる構造的な誤分類経路。
  2) close()のDefault Timeout(10秒)が、Retry Windowの最大21秒より
     短いため、Busy衝突からのRetry中にShutdownが発生した場合、以前は
     瞬時に失敗していたPathが今はTracked Stage Workerを最大21秒
     生存させうる — closeがWorker未停止としてRuntimeErrorを送出する
     可能性(未確証、上流でCancellation Tokenが先に発火する経路の有無を
     完全には追いきれていない)。

Full Suite再実行: 2260 passed, 22 deselected(独立確認)。
```

### 1.2 Docs全体整合性監査 — 最重要Finding

```text
Finding(重要度High、対処済み): _MODEL_BUSY_RETRY_DELAYS_SECONDS Docstring
  が「実機観測: Gemma ~1.7秒、Selene ~14.2秒」を"取り残しThreadの自然完了
  時間の実測値"として引用していたが、これは誤帰属だった。実際には:
    - "Selene ~14.2秒"の出所は、Selene単独診断(Main非同時、合成Criteria、
      Registry未接続)での"成功した"1回のGenerate呼び出し全体のLatency
      であり、しかもこの診断自体はBug症状を再現できていなかった。
    - "Gemma ~1.7秒"の出所は、Main非同時のGemma単独実行での成功
      Latencyで、しかも3回中2回は別の(OF-P2-002系統の)無関係な失敗
      だった。
    - 「取り残しThreadの自然完了時間」を実際に実測した記録は、根本原因
      調査時のAgent 2実機再現(Main+Gemma同時Load)における
      waited_s=0.854(約0.85秒)ただ1件のみ。
  Fix自体は21秒という大きな余裕を持ったBudgetのため実害はないが、根拠
  記述が事実と異なっていた。§2で修正。

その他確認(Clean):
  - Round 3 Doc記載のTest数・全Suite数は現在のRepoと完全一致(自己修正後
    の最終値を反映していることも確認)。
  - Round 1 Docで発生した行番号Staleさは、Round 3 Docでは行番号引用
    自体を避けており、再発していない。
  - Canonical Documentsの4件、すべて解決可能かつ正しい順序。
  - Append-only原則は本Fix Arc関連の全記載で維持されている。

軽微なFinding(未対処、Follow-up候補): OF-P2-002の当初記述(閉じ括弧欠落)
  とRound 3実機再検証で観測した症状(複数JSON Object)は厳密には異なる
  失敗形状であり、「同一問題」というのはUserの判断に基づくもので技術的に
  証明されたものではない、という点。Phase Index上は正確にUser決定として
  記録済みのため、Docs上の欠陥ではない。
```

### 1.3 Main-shared経路 実機再検証 — 新規Positive Evidence

```text
これまでDedicated(Selene/Gemma)経路でのみ実機確認していたRetry機構を、
Main-shared Judge Dispatch経路(User自身のMain ModelをJudgeとして選択した
場合、SeleneSemanticEvaluatorをMain自身のInferenceServiceで再構築する
経路)でも実機再現・再検証した。

結果: 正当なMODEL_BUSY衝突を実機で再現(2 Cycle)、いずれもRetry 1回目
(3.0秒待機)で解消し、最終的にProvider_state=ACTIVE、32件全Criteria評価
成功まで到達した。Round 3で「確認済みTheoretically Sound、実機未検証」
とされていたGapを解消した。

構造的な明確化(副産物): Busy衝突は同一evaluate()呼び出し"内"では発生し
えない(最初のBatchがTimeout/Orphan化した時点でevaluate()は即座に
Returnするため)。実世界で到達可能な形は、"後続の別Turn"が同一Adapter上の
先行Orphanと衝突するCaseのみ。

Clean Teardown確認済み。
```

## 2. 本Roundで対処したこと

```text
src/margpa_runtime_llm/adapters/evaluation/selene.py:
  _MODEL_BUSY_RETRY_DELAYS_SECONDSのDocstringを全面訂正: 誤帰属していた
  "Gemma ~1.7秒、Selene ~14.2秒"という記述を削除し、実際の唯一の実測値
  (waited_s=0.854秒、根本原因調査Agent 2実機再現)を正しく引用。Round 3/4
  の実機再検証(Dedicated/Main-shared双方でRetry 1回目成功)も追記。
  Test名参照の食い違いも修正。

tests/unit/evaluation/test_selene_adapter.py:
  test_model_busy_retry_window_covers_the_largest_documented_real_hardware_
  orphanのAssertion根拠を、誤帰属していた14.2秒から、実際の実測値0.854秒
  の10倍という誠実に説明可能な安全マージンへ変更。

Focused: pytest tests/unit/evaluation/test_selene_adapter.py -q -> 16 passed
Full Suite: pytest -q -m "not model_smoke" -> 2260 passed, 22 deselected
Ruff format/check、Mypy: Clean
```

## 3. 新規Open Finding(未対処、正直な記録)

```text
Open Finding 7(stage_deadline Timer vs Retry Wait競合による誤分類、
  現在到達不能): §1.1参照。inference_budget_ms(現実Production=120,000ms)
  がRetry Window(最大21秒)を大きく上回る限り顕在化しないが、構造上の
  誤分類経路として記録する。対処には、Retry LoopがCancellation発火の
  "理由"(外側Turn Cancel vs 自身のstage_deadline Timeout)を区別できる
  必要があり、これは新規のPlumbingを要する設計判断のため、本Round単独
  では実施しない。

Open Finding 8(close() Timeout(10秒)とRetry Window(最大21秒)の潜在的
  不整合、未確証): §1.1参照。上流でCancellation Tokenが先に発火する経路
  が既にあるかどうかを完全には追いきれていない。Shutdown Path全体の
  追加調査が必要であり、本Round単独では実施しない。
```

## 4. Recovery Index

```text
本Round差分:
  src/margpa_runtime_llm/adapters/evaluation/selene.py(Docstring訂正のみ)
  tests/unit/evaluation/test_selene_adapter.py(Assertion根拠訂正のみ)

Git/Commit/Push: なし。
```

## 5. Exact Next Action

```text
1. 本Round(Round 1-4)全体の結果をUserへ最終報告する。
2. Open Finding 7/8は、対処にはさらなる設計判断・調査が必要なため、
   Controller/User Authority判断待ちとして記録するのみ。
3. Loop継続の要否はUser判断に委ねる。
```
