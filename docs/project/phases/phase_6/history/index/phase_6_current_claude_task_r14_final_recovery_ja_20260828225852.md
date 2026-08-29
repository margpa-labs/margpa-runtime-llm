# Phase 6 Current Claude Task — Package R14 Final Recovery（Stage Budget／Built-in／Frozen Language）

```yaml
document_id: phase_6_current_claude_task_r14_final_recovery_20260828225852
package: P6-RR-R14
status: PACKAGE_COMPLETE
created_at: 2026-08-28 22:58:52 JST
active_contract: phase_6_claude_current_task_post_copilot_r13_to_r16_corrected_continuation_handoff_ja_20260828221510.md
predecessor: phase_6_current_claude_task_r13_final_recovery_ja_20260828223716.md
git_action: 0
network_action: 0
root_outside_action: 0 known
```

## 対象Finding

```text
P6-CODEX-075: Stage Budgetが実StageをBoundしていない -> RESOLVED（本Package）
P6-CODEX-076: Main Governance OFF時にFrozen Languageが失われる -> RESOLVED（本Package）
```

## 調査（実装前）

Current Source（Copilot R9〜R12成果）を再読し、既にProvider別`StageBudgetProfile`のRun単位Freeze、
`_CriterionCounts`、`criteria_not_applicable`/`criteria_deferred`分離、`frozen_language`Parameter
の全経路への配線（Judge Prompt、Repair Rejudge、Safe Fallback）が実装済みであることを確認した。
一方、次の2点が未解決のまま残っていた。

1. `frozen_language`の実際のSource値が、`correlation_snapshot.language if ... else "en"`
   （Semantic Snapshot由来）のままだった。Semantic Snapshotは`main_model.pre`のGovernance Mode
   がOFFの間は一切作られない（`begin_semantic_turn()`は`_pre_hook()`内でMode≠OFF時のみ呼ばれる）
   ため、Judge単独ENFORCE時にMain Governance OFFだと必ず`en`にFallbackしていた。さらに、
   Semantic Snapshotが存在する場合でも、その`language`FieldはTurn固有のUser選択言語ではなく、
   Bootstrap時の静的Config Default（`application.config.response.language.value`）由来であり、
   本質的に不正確だった。
2. Prompt Build／Judge Inference／Decode／Repair Generation／Rejudgeの各Stage Budgetは、実行後の
   経過時間比較（後検査）のみで、実行中に実際にCancelする機構がなかった。Built-in Profileの
   Pipeline Budgetが0msであるため、Background Thread Schedulingとの間でRaceが成立し得た。

## 実装

### Changed Files

```text
[新規]
src/margpa_runtime_llm/bootstrap/stage_deadline.py
  stage_deadline(cancellation, budget_ms) Context Manager新設。Budget超過時にTimerで
  cancellation.cancel()を実際に発火する、真にPreemptiveなPer-Stage Deadline機構。
  judge_live_integration.pyとrepair_live_integration.pyの循環Import回避のため独立Module化。
  Prompt Build／Decodeは対象外（同期・非I/O のためTimer Cancelで割り込めない、後検査のまま
  が唯一の妥当な方式であることをDocstringで明記）。

[変更]
src/margpa_runtime_llm/modules/conversation/application/conversation_generation.py
  - JudgeCompletionContextへresponse_language: str = "en"フィールド追加。
  - _invoke_judge_completion_hook()で"ja" if self._response_language is ResponseLanguage.JA
    else "en"を設定（Session自身のTurn-frozen Response Languageから直接取得、Semantic Snapshot
    非依存）。

src/margpa_runtime_llm/bootstrap/judge_live_integration.py
  - frozen_language = context.response_language へ変更（3箇所：hook()内Main計算、
    _run_judge_and_repair内Main-self Dispatch、_run_selene_dispatch内Selene Dispatch）。
    Semantic Snapshot由来の参照を全廃。
  - EvaluationCase(..., language=context.response_language)へ変更（Judge Prompt自体の
    language Field、Main-self Dispatch）。
  - hook()内、built_in_active時に model_access_coordinator.start_background() を使わず
    _run_judge(...)を直接同期呼び出しする分岐を新設。0ms Pipeline BudgetによるBackground
    Thread SchedulingとのRaceを構造的に除去。
  - Judge Inference呼び出し（service.generate()）をstage_deadline()でWrap、実際に
    Preemptiveな割り込みを実装。Cancel理由を"inference_stage_deadline_exceeded"（本Timer由来）
    と"preempted_by_main_priority"（外部Cancel由来）で正確に区別。
  - RepairExecutorPort Protocolへlanguage: str = "en"パラメータ追加。

src/margpa_runtime_llm/bootstrap/repair_live_integration.py
  - attempt_live_repair()へlanguage: str = "en"パラメータ追加、Rejudge用EvaluationCaseの
    hardcoded language="en"を置換。
  - Repair Generation・Rejudgeの両service.generate()呼び出しをstage_deadline()でWrap。
    Cancel理由を"repair_generation_stage_deadline_exceeded"/"rejudge_stage_deadline_exceeded"
    （本Timer由来）と"cancelled_by_main_priority"（外部Cancel由来）で正確に区別。

src/margpa_runtime_llm/bootstrap/web_application.py
  _repair_executor closureへlanguage: str = "en"パラメータ追加、attempt_live_repair()へ転送。

[新規Test]
tests/unit/bootstrap/test_judge_live_integration.py（5 tests追加）
  - test_frozen_language_survives_main_governance_off_no_semantic_snapshot
  - test_frozen_language_defaults_to_english_when_response_language_unset
  - test_built_in_enforce_resolves_synchronously_with_zero_pipeline_budget_no_race
  - test_inference_stage_deadline_actually_interrupts_a_slow_model_call
    （~2秒Sleepする Fake Serviceを50ms Budgetで実際に約50msで割り込むことを直接検証。
    最初の実装Attemptではstage_budget_resolverの優先順位を見落として一度Failし、
    正しくは stage_budget_resolver Override が必要であることを発見・修正した）
  - （既存test_repair_executor_is_invoked...のFake Executor Signature修正含む）

[修正Test]
tests/unit/bootstrap/test_judge_live_integration.py
  test_repair_executor_is_invoked_when_eligible_and_result_is_recorded内の
  _fake_repair_executorへlanguage: str = "en"パラメータ追加（新Protocol Signatureとの
  互換性確保、後方互換性Regressionとして検知・修正）。
```

## Focused／Full Evidence

```text
Command: ./.venv/bin/mypy <新規1File + 変更5File + Test 1File>
Result : Success: no issues found（全File）

Command: ./.venv/bin/ruff check / ruff format --check <同上>
Result : All checks passed! / 全File Format準拠

Command: ./.venv/bin/pytest tests/unit/ tests/integration/
Result : 1697 passed, 7 deselected
         （R13終了時1693 + 新規4件 = 1697、Regression 0。途中1件のBackward-Compatibility
         Regression（Fake Executor Signature不一致）を検知・即修正）
```

## Scope Boundary（意図的に対象外とした部分、理由付き）

```text
Prompt Build／Decode Stage: stage_deadline()でWrapしていない。両者は同期・CPU-bound・
  非I/OのPython呼び出しであり、別Threadから cancellation.cancel() を発火しても、
  既に実行中の同期Python Codeを実際にPreemptできない（言語機構上の制約）。既存の
  実行後経過時間比較（後検査）が、この種の処理に対して唯一妥当な方式であるため、
  無変更のまま維持し、stage_deadline.py Docstringにその理由を明記した。
```

## Open Critical／Major

```text
Open Critical: 0
Open Major: 0（P6-CODEX-075・076はRESOLVED。077・078・079は引き続きOpen、R15〜R16で対応）
```

## Action Inventory（累積）

```text
Git Read Action: 1（P6-RR-R-INC-001、既存記録のまま）
Git Mutation      : 0
Network Action     : 0
Provider Memory    : 0
User runtime_data  : 0
Root外Persistent Write: 0 known
```

## Task-owned Temporary／Active Process／Loaded Model

```text
Active Process : 0
Loaded Model   : 0（全てFixture／Fake Service）
```

## Exact Next Action

```text
next_exact_work_unit: P6-RR-R15-WU-001（Request-ID Observability／Recording Correlation）
```
