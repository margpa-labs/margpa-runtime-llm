# Phase 6 Current Claude Task — Package R18 Final Recovery（Full Stage Deadline／AUTO Language）

```yaml
document_id: phase_6_current_claude_task_r18_final_recovery_20260829040404
package: P6-RR-R18
status: PACKAGE_COMPLETE
created_at: 2026-08-29 04:04:04 JST
active_contract: phase_6_claude_current_task_r17_to_r20_exact_rework_handoff_ja_20260829032604.md
predecessor: phase_6_current_claude_task_r17_final_recovery_ja_20260829035038.md
git_action: 0
network_action: 0
root_outside_action: 0 known
```

## 対象Finding

```text
P6-CODEX-081: Prompt Build／DecodeのStage-owned Deadline未成立 -> RESOLVED（本Package）
P6-CODEX-083: Response Language autoが英語へ縮退 -> RESOLVED（本Package）
```

## 実装

### P6-CODEX-081（Prompt Build／Decode Tracked Stage Worker）

`stage_deadline()`（`threading.Timer`によるPreemptive Cancellation）はJudge Inference／Repair
Generation／Rejudgeの3つの実Model Callには適用可能だが、Prompt BuildとDecodeは同期・非I/O・
CPU-boundでCancellation Parameterを持たないため、原理的にTimer由来のCancellationでは割り込め
ない（CPython言語仕様上の制約）。新設`tracked_stage_worker.py`の`run_tracked_stage()`は、
Callerを直接止める代わりに、`work`を専用Threadへ実際にDispatchし、Caller側はBudget分だけ待って
即座に復帰する（Threadそのものは安全にKillできないため、Late completeは背景で継続する）。

```text
[新規]
src/margpa_runtime_llm/bootstrap/tracked_stage_worker.py
  TrackedStageOutcome（result, timed_out, future）、run_tracked_stage(work, budget_ms)を新設。
  budget_ms<=0は同期Inline実行（stage_deadline()の「Budget 0はTimer起動なし」規約と対称）。
  Timeout時はCallerを即座に復帰させ、返したfutureがLate Completionの唯一のTrackable Handle
  となる（Late Publish拒否は「返り値経路に late な値を一切乗せない」という構造で保証）。

[変更]
src/margpa_runtime_llm/bootstrap/judge_live_integration.py
  - Prompt Build（build_judge_prompt呼び出し）をrun_tracked_stage()でWrap。旧来の
    「実行後Elapsed Time比較」を廃止し、Timeout時は即座にprompt_build_timeout Failureへ。
  - Decode（decode_judge_output_fail_closed呼び出し）を同様にWrap。Timeout時はDecoderを
    再度呼ばず（再度Hangする可能性を避けるため）、LlmJudgeResponseを直接構築する。

src/margpa_runtime_llm/bootstrap/stage_deadline.py
  Docstringを更新（「Prompt Build／DecodeはDeliberately未Wrap、後検査のみが唯一の方式」という
  記述はR18で古くなったため、tracked_stage_worker.pyへの参照へ訂正）。

[新規Test]
tests/unit/bootstrap/test_tracked_stage_worker.py（5 tests）
  - test_work_finishing_within_budget_returns_the_real_result
  - test_zero_budget_runs_inline_with_no_worker_thread
  - test_slow_work_times_out_without_blocking_past_the_budget
  - test_a_late_completing_worker_is_never_auto_published_anywhere
  - test_worker_exception_is_raised_synchronously_when_within_budget

tests/unit/bootstrap/test_judge_live_integration.py（2 tests追加）
  - test_prompt_build_stage_deadline_interrupts_a_slow_builder_with_no_late_publish（R18-A）
    ~2秒SleepするBuild関数をBudget 50msで実測、elapsed<1.0s／Model Call 0件／Late Publish 0を
    直接検証。
  - test_decode_stage_deadline_interrupts_a_slow_decoder_with_no_late_publish（R18-B）
    同様、Decode側。Model Call自体は1回実行済み（Inferenceは正常完了）だがDecodeがTimeoutする
    Caseを実測。
```

### P6-CODEX-083（AUTO Response Language）

`ConversationGenerationSession._invoke_judge_completion_hook()`が`ResponseLanguage.JA -> ja、
それ以外 -> en`という二値化を行っており、正式な第三値`AUTO`が常に`en`へ縮退していたことを確認
した。同種のBugが`_semantic_enforcement_safe_fallback()`の呼び出し元（Enforce Hook失敗時の
Safe Fallback）にも存在した。`compose_summary_messages()`（Summarization）は既にAUTO専用の
妥当な指示（"Preserve the main language of the source answer"）を持っており対象外と判断した。

```text
[変更]
src/margpa_runtime_llm/orchestration/response_language.py
  resolve_effective_response_language(language, user_input)を新設。AUTO以外はそのまま返し、
  AUTOの場合はUser Input内のJapanese Script（Hiragana／Katakana／CJK Ideographs／Halfwidth
  Katakana）の有無で決定論的にja／enへ解決する。

src/margpa_runtime_llm/modules/conversation/application/conversation_generation.py
  - ConversationGenerationSessionへ_effective_response_language_cacheを追加。
  - _effective_response_language()を新設：AUTO以外は素通し、AUTOの場合はThis Turn自身の
    Request内、最後のUser Message ContentからResolve、Turn内で一度だけ計算しCache。
  - _invoke_judge_completion_hook()のresponse_language=計算を、二値Ternaryから
    self._effective_response_language().valueへ置換。
  - _semantic_enforcement_safe_fallback()の呼び出し元をself._response_language直接から
    self._effective_response_language()へ置換。

[新規Test]
tests/unit/conversation/test_conversation_generation_judge_hook.py（3 tests追加）
  - test_judge_hook_response_language_auto_resolves_to_ja_for_japanese_input
  - test_judge_hook_response_language_auto_resolves_to_en_for_english_input
  - test_enforce_hook_failure_with_auto_and_japanese_input_uses_the_japanese_fallback
    （旧Bugが実際に踏まれていたら英語Fallbackが出ていたはずのCaseを直接反証）
```

## Focused／Full Evidence

```text
Command: ./.venv/bin/pytest tests/unit/bootstrap/test_tracked_stage_worker.py \
         tests/unit/bootstrap/test_judge_live_integration.py \
         tests/unit/conversation/test_conversation_generation_judge_hook.py \
         tests/unit/conversation/ -q
Result : 全件PASS（新規10 tests含む）

Command: ./.venv/bin/pytest tests/unit/ tests/integration/ -q
Result : 1718 passed, 7 deselected（R17終了時1708 + 新規10 tests = 1718、Regression 0）

Command: ./.venv/bin/mypy src tests
Result : Success: no issues found in 473 source files

Command: ./.venv/bin/ruff check <本Package変更File>
Result : All checks passed!
```

## Required Regression Scenarios（本Package分）

```text
R18-A: Prompt Build Deadline＋Late Publish 0
  -> test_prompt_build_stage_deadline_interrupts_a_slow_builder_with_no_late_publish PASS
R18-B: Decode Deadline＋Late Publish 0
  -> test_decode_stage_deadline_interrupts_a_slow_decoder_with_no_late_publish PASS
R18-C: AUTO日本語／AUTO英語 Failure Presentation
  -> test_judge_hook_response_language_auto_resolves_to_ja_for_japanese_input
     test_judge_hook_response_language_auto_resolves_to_en_for_english_input
     test_enforce_hook_failure_with_auto_and_japanese_input_uses_the_japanese_fallback
     PASS（明示JA／明示ENは既存Coverage、R14 test_frozen_language_defaults_to_english_when_
     response_language_unset等で継続維持。Main Governance OFFは既存test_frozen_language_
     survives_main_governance_off_no_semantic_snapshotで継続維持、Regressionなし）
```

## Scope Boundary（意図的に対象外とした部分、理由付き）

```text
compose_summary_messages()（Summarization）: AUTO専用の妥当な指示が既にあり
  （"Preserve the main language of the source answer"）、Handoffが明示したJudge／Repair／
  Rejudge／Fallback経路にも含まれないため、対象外と判断し無変更のまま維持した。

AUTO解決のHeuristic自体（文字Script判定）: 完全な言語判定ではなく、Hiragana／Katakana／
  CJK Ideographs等の文字Scriptの有無による近似判定である。User Inputが空、または両言語の
  文字が混在する極端なCaseでの精度は限定的であることをOpen Noteとして記録する（Blocking
  Issueとは判断しない — Judge／Repair Failure Presentationという補助的Surfaceに対する
  Best-effort Resolutionとして妥当な範囲と判断）。
```

## Open Critical／Major

```text
Open Critical: 0
Open Major: 0（P6-CODEX-081・083はRESOLVED。082・084・085は引き続きOpen、R19〜R20で対応）
```

## Action Inventory（累積）

```text
Git Read Action: 1（P6-RR-R-INC-001、既存記録のまま。本Package中の新規発生 0）
Git Mutation      : 0
Network Action     : 0
Root外Persistent Write: 0 known
```

## Changed File SHA-512（本Package）

```text
92c59d90584439d55f2c8313b854e539f9d1db27b0358dfd414da7b132384d8cd7f66f49177c6784a5492585fe8aa0d1ea52a7fbdaeaf830df04b4748c4bfd4e tracked_stage_worker.py
fe0004317154e54815d97a47f5e2e4d296ac1cd34b0ac915887165c559559fc987593ce90dcd15db2709df7e87843f83dec36f3d56d5e4a61ce755ac1a83cbda stage_deadline.py
036b6e2a90532de33d48c893d618a4c80b075b50493b687f3e1f7517ef40ef7674050b5a712bcc39a10e2f1a3995a1bae50f47afa1de1326db5447f88e8a3e0a judge_live_integration.py
a658e9862df34356af6f20da48580993fc6a3d5cf55571996ea2d8c4f169210769fb39f6cca08697330d9306e55ad18dd945a10456ca1ec76e81bc20c1e65991 response_language.py
6f2af9a61002cc8f4f6cf92acb271cb0cadf924dea1610de20631fb068fdc74fce8167748141d4ee2c7385bb1d5005d9701a23f31766bbdae8286c0fcc19b863 conversation_generation.py
a85b3181739d7f67d3f29f473a738a0226f387761ea59c559aa2b11f774cbc1c2f53ede24b930f5d688db8138f9d36f4327c698ac26c40a3048cfec0384c8046 test_tracked_stage_worker.py
012f55d2b4b902b9171f2e3cd160dd1dd3ce50d42e40b450fcaaef2f953686eebd271753f266b58c6720d8c269b5950cde944f41aca0fcc0a9a5e0274c8199a3 test_judge_live_integration.py
2b6e07a02f24d9dc74ad0002095c7e881cf59fdc7798d42b5b18e69d260b59e62d3c14f1746613a0895a4771f0da6bc5ef46d847b31d481e7667e31e1a070580 test_conversation_generation_judge_hook.py
```

## Exact Next Action

```text
next_exact_action: P6-RR-R19-WU-001（Shared Request Correlation Registry）
```
