# P6-CODEX-007 Real Browser Golden Path — Critical Race Condition発見・修正

```yaml
document_id: phase_6_codex_p6_codex_007_real_browser_golden_path_and_critical_fix
status: current_recovery_entry
phase: phase_6
work_unit: p6_codex_007_partial_critical_fix
role: Claude側設計統括者役
long_running_mode_active: true
created_at: 2026-08-23 07:05:00 JST
```

## 概要（最重要）

```text
本WUの実Server／実Model／実Browser Golden Path検証中、Judge Mode
（observe／enforce）が有効な状態で実Chatメッセージを送信すると、
Model自体は正常に応答しているにも関わらず、その応答が
`Error: model_busy`（`Modelは別のRequestを処理中です。`）へ置き換わって
消える、という重大な実Regressionを発見した。これはUnit Test（すべてFake
Inference Service使用、瞬時応答のため本Raceを再現しない）では検出不可能
だった、実Hardware・実Concurrency特有の不具合である。

「未実測事項をPASSと捏造しない」原則どおり、これを隠さず記録し、
Root Causeを特定し、実際に修正し、実Server／実Browserで修正を再検証
した。
```

## 発見の経緯（実測ベース）

```text
1. Judge Mode=observeを実Serverで有効化後、新規Chatの最初のMessageを
   送信 → 実Modelの応答が生成された後、Errorへ置き換わって消失する
   ことを実Browserで複数回確認（`.venv/.t/`配下のProject-local Temp
   Root使用、Governance Correction Item 1に準拠）。
2. Judge Mode=offでは同一操作が確実に成功することを確認（複数回）。
3. Bisectで--phase-6-feature-modes単独でも（Judge Mode自体はoffのまま）
   問題が再現しないことを確認 → Judge Modeが実際にon（observe/enforce）
   であることが必要条件と判明。
4. src/margpa_runtime_llm/modules/conversation/application/
   conversation_generation.pyおよびsrc/margpa_runtime_llm/adapters/
   model_backends/llama_cpp/adapter.pyの全MODEL_BUSY Raise箇所
   （計5箇所）へ一時的なDebug Trace（Thread一覧出力）を追加し、実Server
   で再現・Log採取した。
5. Root Cause特定: `_completed_event()`内で`self._invoke_judge_
   completion_hook(...)`を`_context_usage()`（`data`辞書構築の一部）
   より前に呼んでいたため、同一Turnの中で「今まさに起動した
   Background Judge Thread」と「同じTurnの`_context_usage()`が呼ぶ
   `_text_token_counter`（=Adapterの`count_text_tokens`、Main Model
   生成と同じ`_generation_lock`を共有）」が自己衝突（Self-collision）
   していた。Response Language Policyは既定でSystem Messageを常に
   Prependするため、`_context_usage()`のSystem-role分岐（Token Counter
   呼び出し）は実運用では常に実行される経路だった。
   非決定的だった理由: どちらのThread（Main ThreadのToken Counter呼び
   出し vs 新規Background Judge Threadの`service.generate()`）が先に
   `_generation_lock`を獲得するかはOS Schedulingに依存するため。
```

## Exact Mutation（修正）

```text
Modified:
  src/margpa_runtime_llm/modules/conversation/application/conversation_generation.py
    + _completed_event()内、_invoke_judge_completion_hook()の呼び出しを
      dataの構築（_context_usage()呼び出しを含む）より後、
      Event返却の直前へ移動——同一Turn内の自己衝突を解消。
    + _context_usage()のSystem／RAG Token Counting Loopをtry/exceptで
      保護し、Counter失敗（Model Busy等）時はSystem／RAG分をToken数0へ
      Degrade——既に成功した応答全体を失敗させない（Defense in Depth、
      Cross-turn Collision等の残余Riskへの備え）。
  src/margpa_runtime_llm/bootstrap/judge_live_integration.py
    + Judge自身のGenerationRequestへ`parameters=GenerationParameters(
      max_new_tokens=200)`を明示指定（既定512→200）。Judge出力は短い
      JSON 1件のみのため、Judge Callの所要時間を短縮しCollision Windowを
      縮小する（根絶ではなく低減、Residual Riskとして開示）。
Modified（Test）:
  tests/unit/conversation/test_conversation_generation_judge_hook.py
    + FakeStreamへusage引数追加（実Usage Dataを伴うTest経路を可能にする）
    + test_context_usage_token_counting_runs_before_the_judge_hook_fires
      （Call Order直接検証：Token Counter→Judge Hookの順序を固定）
    + test_context_usage_degrades_gracefully_when_the_token_counter_is_busy
      （Counter例外時も応答全体は失敗しないことを直接検証）
  tests/unit/bootstrap/test_judge_live_integration.py
    + test_judge_call_uses_a_tight_max_new_tokens_cap
```

## 実Server再検証（修正後、実Model・実Browser）

```text
実施内容: Judge Mode=observeを有効化した状態で、待機時間を最小限にした
  3連続Real Chat Message（"Message A."→"Message B."→"Message C."）を
  実Qwen3-4Bへ送信。Message Bおよび Cは、直前のMessageの完了直後
  （Backgroud Judge Threadがまだ実行中である可能性が高いTiming）に
  意図的に送信した。

結果: 3／3件とも実Model応答が正常に表示され、model_busyは一切
  発生しなかった（修正前は同種の操作で高頻度に再現していた）。
  GET /api/v5/feature-modes/statusで実際のLive Judge結果を確認:
    {"judge": {"current_mode": "observe", "last_result": {
      "judge_role": "main_self", "recommendation": "accept",
      "confidence": 0.95, "execution_state": "completed",
      "repair_eligibility": null}}}
  repair_eligibility=nullは、Judge Mode=observe（enforceではない）
  時にEligibility Resolutionが実行されないという、P6-CODEX-002
  修正済み動作とも整合している。
```

## Validation

```text
Backend Full: TMPDIR="$PWD/.venv/.t" pytest -p no:cacheprovider --basetemp=.venv/.t/f
  1434 passed, 5 deselected in 63.42s（新規2 Test含む、回帰0）
Ruff: All checks passed!
Mypy: Success: no issues found in 430 source files
実Server: 3回の実Server起動・実Browser Session全て正常終了・Process確認済み
```

## 残存Risk（正直な開示）

```text
本修正は「同一Turn内の自己衝突」という、実測で確認された最も高頻度な
発生パターンを解消し、実Browser上での複数回の連続Real Messageで
再現しなくなったことを確認した。ただし、以下は理論上なお残る:

- Cross-turn Collision: あるTurnのJudge Background ThreadがまだModel
  推論中に、直後の新しいTurnがまさに同じMillisecond Windowで開始
  すれば、なお`model_busy`が発生し得る（Windowは
  max_new_tokens=200への短縮でMILDに縮小したが、根絶はしていない）。
  この場合もRetryable=trueであり、既存の「再試行」UIで回復可能。
- 完全な根絶には、Judge専用の独立Model Instance／Context、または
  Main Chat向けRequestを常に優先させるQueueing機構が必要——本
  ReworkのSafe Scopeを超える設計変更のため、Controller-owned Followup
  として次のCandidate Handoffに明記する。
```

## Next Exact Route

P6-CODEX-006（Calibration／Mode Comparison／Metrics）およびP6-CODEX-008
（Acceptance Matrix全数Audit／Candidate再発行）へ進む。
