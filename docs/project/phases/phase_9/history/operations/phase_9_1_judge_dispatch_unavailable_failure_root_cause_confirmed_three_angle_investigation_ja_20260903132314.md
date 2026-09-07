# Phase 9-1 Judge Dispatch "unavailable"即時失敗 — 3視点独立調査による根本原因確定(実機再現込み)

```yaml
document_id: phase_9_1_judge_dispatch_unavailable_failure_root_cause_confirmed_three_angle_investigation_20260903132314
document_type: root_cause_investigation_result
document_state: candidate_for_controller_review
phase: phase_9
program: phase_9_1
recorded_at: 2026-09-03 13:23:14 JST
recorder_role: Claude(Bounded Implementation Worker)
trigger: User指示「3連続で、完全に視点を変えながら、judge周りを捜査出来る？いかれてる原因。」
methodology: 3つの独立Agentによる並行調査(相互に結果を見せない状態で開始)
  agent_1: 静的Lock/Exception経路監査(Read-only、コード読解のみ)
  agent_2: 実機Main+Judge同時Load再現(実Model、実Registry、実Snapshot形状)
  agent_3: Production配線監査＋Git履歴Provenance調査
git_action: none
source_mutation_this_task: none
closure_authority: none
implementation_authority: none（本Docは調査結果の記録であり、修正Source変更はまだ行っていない）
supersedes: none(Append-only。既存のOpen Finding 5を置き換えるのではなく解決する)
relates_to: handoffs/phase_9_claude_fresh_session_sss_targeted_resource_gate_recovery_exact_return_addendum_selene_failure_point_ja_20260903020447.md
```

## 0. 位置づけ

既存のOpen Finding 5(Selene Judge ENFORCE即時失敗、Exact Trigger未特定、Read-only調査の限界で確定に至らず)を引き継ぎ、Userの明示指示により3つの完全に独立した視点(静的監査／実機再現／配線・履歴監査)で並行調査を実施した。3つは互いの結果を見ずに開始しており、収束した結論はPremise Anchoringのリスクが低い。

結果、**根本原因を実機再現(生Exception捕捉込み)で確定した**。Source修正はまだ行っていない(本Taskの指示は「捜査」であり、修正の実装Authorityは別途指示待ち)。

## 1. Maximum Claim

```text
P9_1_JUDGE_DISPATCH_UNAVAILABLE_ROOT_CAUSE_CONFIRMED_BY_REAL_HARDWARE_REPRODUCTION_CANDIDATE_FOR_CONTROLLER_REVIEW
```

Fix実装、Closure、Acceptanceは主張しない。

## 2. 確定した根本原因(3視点収束)

```text
1. Selene/Gemma共有Engine `SeleneSemanticEvaluator._plan_batches()`
   (src/margpa_runtime_llm/adapters/evaluation/selene.py:509-551) は、
   各BatchのGenerate呼び出しを行う"前に"、候補Criterion毎に
   `self._service.count_chat_prompt_tokens(...)` (同L529) を同期的に呼ぶ。

2. これは `LlamaCppModelAdapter.count_chat_prompt_tokens()`
   (adapters/model_backends/llama_cpp/adapter.py:343-363) に到達し、
   `self._generation_lock.acquire(blocking=False)` を試みる。既に
   held中なら即座に `InferenceError(code=MODEL_BUSY,
   safe_message="The model is already processing another request.")`
   を投げる(待機なし)。

3. `_generation_lock` は `generate()` 実行中、`_begin_generation()`
   (同L371-408) で保持され、`generate()`自身の
   `finally: self._end_generation()` (同L285-287) でのみ解放される。

4. `run_tracked_stage()` (bootstrap/tracked_stage_worker.py) は自身の
   budget_ms待機が切れても、背後のBackground Thread(実Generate呼び出し
   を実行中)を"殺さない"設計(Docstringに明記、Pythonで安全にKillできない
   ため)。呼び出し元(evaluate())はTimeoutとして先に諦めて戻るが、
   その背後Threadは`_generation_lock`を握ったまま実行を継続する
   ("Late Complete"、意図された挙動)。

5. その状態で同一Adapter Instanceへの"次のTurn"のJudge Dispatchが
   `_plan_batches()` に到達すると、(2)のLock Checkが即座に失敗し、
   `evaluate()`の`try/except Exception`(selene.py:348-354)がこれを
   `f"{provider_label}_unavailable:{type(exc).__name__}"` =
   `"..._unavailable:InferenceError"` へ収める。

6. `judge_live_integration.py`の
   `_judge_failure_reason_from_semantic_response()` (L911-936) は、
   "malformed_output"始まりでも"deadline_exceeded"/"cancelled"を
   含むのでもない文字列を無条件で `JudgeFailureReason.UNAVAILABLE`
   (表示上「unavailable」)へ収束させる。ここで `InferenceError.code`
   (MODEL_BUSY等の詳細)は完全に失われる。

結果: Provider Activationは常に成立するが(Adapter自体はLoaded状態の
まま)、"一度でも"先行するJudge Dispatchが打ち切られてBackground Thread
が取り残されると、以降"そのAdapter Instanceが再Loadされるまで"、次の
Turn以降のJudge Dispatchは即座に(実測0.2ms〜、実UI観測55-125ms)
"unavailable"へ落ちる。SeleneとGemmaが完全に同一症状を示すのは、両者が
文字通り同一の`SeleneRoleAdapter`/`SeleneSemanticEvaluator`/
`LlamaCppModelAdapter`Codeを共有しているため(Provider固有の問題では
ない)。
```

## 3. 実機再現Evidence(Agent 2、CONFIRMED)

```text
実行: build_phase1_application()経由でMain(16K Context)を実際にLoad
     ／Active維持。ProductionRoleAdapterFactory + 実
     TrackedStageWorkerRegistry() (Noneではない) 経由でGemma 4 E2B
     Judgeを実Load。freeze_semantic_turn(max_criteria=32)で109件から
     実際に selected=32 / deferred=77 のSnapshotを構築(実Production
     形状と完全一致)。

Turn 1 (inference_budget_ms=1で意図的にCooperative Cancellationを
       誘発): 35ms で FAILED / gemma_e2b_inference_deadline_exceeded
       として"戻る"。しかし戻った直後、registry.active_count()は
       まだ1 — 背後のGenerate Threadは実際にはまだ走っていた
       (Late Complete、取り残し確認)。

Turn 2 (同一Evaluator Instance、直後、実Default Budget、Override
       なし): 0.2ms で provider_state=unavailable,
       failure_reason="gemma_e2b_unavailable:InferenceError"。
       Script側Monkeypatch(Source非変更、実行Instanceへの局所計装
       のみ)により、収束"前"の生Exceptionを捕捉:

         type=InferenceError
         code=<InferenceErrorCode.MODEL_BUSY: 'model_busy'>
         safe_message='The model is already processing another
                       request.'

Clean Teardown確認: registry.shutdown(timeout_seconds=180) ->
  clean=True, waited_s=0.854(取り残しThreadが実際に約0.85秒後に
  自然完了したことも確認)。Gemma Unload後Main正常動作確認、RSS/
  Available Memoryとも正常回復、ps aux残存Processなし。src/tests/
  config配下は一切変更していない。

Agent自身が記録した誠実な補足: このReproでは"取り残しWindow"が
Cooperative Cancellation(短いBudget)による早期Unwind経由で開いた
のであり、「初回Generate呼び出しが単純に長時間Hang/Slow」という
経路そのものを実証したわけではない。しかし"Mechanism"(背後Thread
がLockを握ったまま残り、次のPlan Batchesがそれを即座に検知して
失敗する)自体は仮説どおり実証された。実Productionでは、Main同時
Active下でのGPU/Metal競合による純粋なSlow/Hang経路と、Cancellation
Unwind Window経路の両方が同じDownstream症状に到達しうる。
```

## 4. 静的監査Evidence(Agent 1、SUPPORTED)

```text
Lock/State管理自体(generate/_begin_generation/_end_generation/
count_chat_prompt_tokens/count_text_tokens)はModule内Logicとして
一貫しており、通常のException経路でLockがLeakするBugはない
(finally節が確実に発火する)。問題は"Architecturalな Gap"であり、
Module内Bugではない: run_tracked_stage()の「取り残しThreadは
Turn境界で誰もJoinしない」設計そのものが、Selene/GemmaのTimeout時
`late_worker_observer`経由でFutureを受け取っても、全体Cancellation
経路以外では"誰もそのFutureを二度と見ない"("Dead End"、
judge_live_integration.py:1431-1455の分岐で全体Cancel時のみ
`deferred_role_release`として伝播、通常のBatch単位Timeoutでは
握り潰される)。

もう一つの独立した候補として、`_mark_generation_unavailable()`
(adapter.py:417-427)が、Pathological Repetition検知時に
`_state`を`FAILED`へ"永続的に"Latchする経路も発見(Role再
Activateまで回復しない)。これは小型量子化Model特有のJSON配列
繰り返し出力で現実的に起こりうる、Lock取り残しとは"別"の Adapter
汚染経路であり、収束後の文字列(`..._unavailable:InferenceError`)
がLock競合と区別不能なため、実Incidentでどちらが起きたか(あるいは
両方起きうるか)は本調査単体では確定できない。今回の実機再現(§3)は
"Lock競合"経路の実在を直接証明したが、これによって
Pathological Repetition Latch経路が"起きていない"ことまでは証明
されない(両方が現実の別Failure Instanceとして共存しうる)。
```

## 5. 配線・履歴監査Evidence(Agent 3、決定的補強)

```text
(A) 配線: TrackedStageWorkerRegistry()はfeature_modes_enabled時に
    1個だけ構築され(web_application.py:322)、Dedicated
    (Selene/Gemma)経路・Main-shared経路の両方へ同一Instanceとして
    到達することを確認(ProductionRoleAdapterFactory経由、Runtime
    Model Switch後も再構築されない)。Stale/None Registry経路は
    存在しない — 実際に問題を起こす配線が"常に"生きている経路で
    あることを確認。

(B) Native-level競合: Python層でMain用Adapterと Judge用Adapterの
    Instance間を直接Serializeする明示的な排他制御はRepo内に存在
    しない。ただしllama-cpp-pythonはProcessごとに1回だけ
    `llama_backend_init()`を呼ぶ(全Model共有のProcess-global
    State)。GPU/Metal Level競合が実際にあるかはStatic監査だけ
    では確証できないが、「なぜ先行するGenerate呼び出しが取り残される
    ほど長引くのか」の Plausible な前提条件として矛盾しない
    (Main同時Active時のみ実失敗が観測されている、という既存Evidence
    と整合)。

(C) 履歴Provenance(最重要補強): `count_chat_prompt_tokens()`を
    Batch Dispatch"前"に呼ぶ`_plan_batches()`自体が、現在の
    Git HEAD `1f0e70e`("feat: checkpoint phase 9 judge governance
    work"、SSS Recovery時のStable Recovery Pointそのもの)で
    "新規追加"されたことをgit log -p --followで確認した。それ以前
    のSeleneSemanticEvaluatorは単一Unbatched Generate呼び出しのみで、
    事前にLockへ触れる工程自体が存在しなかった。つまりこの脆弱性は
    "P9-1 Package 2"のBatch Planner導入によって初めて生まれたもの
    であり、「なぜ今になって発生したか」を明確に説明する。現在の
    Working Tree上の未Commit Diff(selene.pyのLabel/Decode-error
    一般化)はこの脆弱性箇所自体には触れていない — 現Working Tree
    でも未修正のまま残っている。
```

## 6. 除外された仮説

```text
ModelAccessCoordinator Level(start_background()拒否によるBusy)は、
そのRefusal時にComposition側`mark_skipped()`が呼ばれ、Judge Run
Stateが`queued_or_skipped`になる経路であり、`failed`にはならない
(judge_live_integration.py:453-474)。実UI観測は一貫して
「実行状態: failed」であり、`queued_or_skipped`ではなかった
ため、この経路は今回観測されたFailureの直接原因からは除外できる。
```

## 7. 残る未確定点(正直な記録)

```text
1. Pathological Repetition FAILED-Latch経路(§4後半)が、実際の
   2026-09-02/09-03の観測Incidentで"実際に起きていたか"は未確認
   (Lock競合経路と収束後の文字列が区別不能なため)。両経路とも
   `InferenceError.code`を保持したまま記録するよう修正すれば、
   将来のIncidentでは区別可能になる(§8 Option C)。
2. Native Metal/GPU Cross-instance競合(§5-B)が実際にLock取り残し
   Windowを開くほどの遅延を生むかは、実機Profilingでしか確認
   できない。今回の実機再現(§3)はCooperative Cancellation経由の
   Window生成であり、これとは別経路である可能性がある。
3. 実Productionの2件の観測Incident(Selene 2026-09-02、Gemma
   2026-09-03)それぞれが、"当該SessionのJudgeとして初回Dispatch"
   だったのか、"複数Turn目"だったのかは、既存の永続Evidenceからは
   確認できていない(Turn番号の記録がないため)。
```

## 8. 提案する修正方向(未実装、Authority待ち)

```text
Option A(推奨、最小侵襲): count_chat_prompt_tokens()/
  count_text_tokens()はTokenizer参照(self._chat_template)のみに
  依存し、実Generate State(self._model)を変更しない読み取り専用
  操作である。これらから`_generation_lock`要求自体を除去すれば、
  進行中のGenerateと同時に安全に呼び出せ、Lock競合による誤Busy化
  そのものが起こらなくなる。Generate自体の排他制御(本来の目的)は
  `generate()`/`stream()`側のLockのみで引き続き担保される。

Option B(補完、より侵襲的): Adapter Instance単位で「前Turnの
  取り残しThreadがまだ実行中」を検知・待機/報告できるようにし、
  現在の黙って`MODEL_BUSY`へ落ちる挙動を、より診断可能な専用
  Failure Reason(例: judge_previous_dispatch_still_finishing)
  へ分離する。

Option C(観測性改善、単独では根本修正にならない): `InferenceError.
  code`を`evaluate()`の収束Stringに含める(例:
  f"{label}_unavailable:{type(exc).__name__}:{getattr(exc,'code',
  None)}")。既存の3-prefix判定ロジックには影響しない形で追加すれば、
  将来のIncidentでLock競合とPathological Repetition Latchを
  区別できるようになる。

3案は排他的ではない。AだけでLock競合由来の症状は解消するが、
Pathological Repetition Latch経路(§4後半)はAでは解消しないため、
別途Cで観測性を上げつつ実際に再発するか監視するのが妥当と考える。
```

## 9. Source変更

```text
本Task(調査)ではSource変更なし。3つのAgentが使用したReproduction
ScriptはすべてScratchpad配下(Project外、Git管理外)のみ。
git commit/pushは一切実行していない。
```

## 10. Exact Next Action

```text
1. 本Docの根本原因確定をController/User Authorityでレビューする。
2. Option A(count_chat_prompt_tokens/count_text_tokensから
   _generation_lock要求を除去)を実装するか、User明示指示を待つ。
3. 実装する場合、Focused Test(Lockが実際に不要であることを示す
   Regression Test含む)と、可能であれば実機での連続Turn再現Test
   (§3のPatternを恒久Fixture化)を追加する。
4. §7の未確定点(特にPathological Repetition Latch経路の実際の
   発生有無)は、Option C実装後の実運用Evidenceで継続観察する。
```
