# Phase 9-1 Judge／Governance — Controller独立Review(IR-R5版) 最終Micro Rework Exact Return Handoff

```yaml
document_type: exact_return_handoff
document_state: candidate_for_controller_review
from: claude
to: codex_controller
in_response_to: ../history/operations/phase_9_1_controller_ir_r4_return_review_and_final_micro_rework_ja_20260905071833.md
git_action: none
network_action: none
external_artifact_mutation: none
closure_authority: none_requested
language: ja
recorded_at: 2026-09-05 07:39:00 JST
```

## 1. Maximum Claim

`P9_1_REWORK_INCOMPLETE_FOR_CONTROLLER_REVIEW`

**主張しないこと(明示的除外)**:
- 32件Criterionの通常選択規模でのRejudge成立は主張しない(未変更、前回Return維持)。
- Seleneの未解決状態自体の解消は主張しない(延期候補登録のまま、変更なし)。
- Gemma不正JSON欠陥の確定的な根本原因の証明は主張しない(前回Return維持)。
- Phase Closureは主張しない。次Phaseへも進まない。

**今回新たに成立した主張**:
- Planner Failure(Counter例外／Token・Context不足／Worker Registry shutdown拒否)が、呼出し元で3種のTyped `rejected_reason`(`repair_rejudge_counter_failed`／`repair_rejudge_budget_insufficient`／`repair_rejudge_worker_registry_unavailable`)へ正しく分離された(Deadline/Cancelは前回IR-R4-01の帰属を維持)。
- Judge起点Gemma Repair Testが、safe fallbackでも成立してしまう弱いAssertから、`repair_outcome==improved`・`repair_accepted is True`・`presentation_outcome==repair_accepted`・非空かつ元回答と異なる提示内容のHard Assertへ強化され、実機1回で確認された(改善回答の採用そのものを直接証明)。
- Main Governance起点Testの誤解を招く関数名(`...persists_the_repair`)を、実態(Hook直接Test、`persistent=None`)に合わせて訂正した(`...authorizes_and_adopts_the_repair`)。

## 2. 対象

[Controller独立Review(2026-09-05 07:18:33 JST)](../history/operations/phase_9_1_controller_ir_r4_return_review_and_final_micro_rework_ja_20260905071833.md)のIR-R5-01、IR-R5-02、全項目。

## 3. Files Changed

| File | 対応項目 | 変更内容 |
|---|---|---|
| `src/margpa_runtime_llm/bootstrap/tracked_stage_worker.py` | IR-R5-01 | Worker Registry shutdown拒否時の内部Exception Messageを`REGISTRY_SHUTTING_DOWN_MESSAGE`という公開定数へ切り出し(文字列自体は無変更)、呼出し側が独自にMagic Stringを複製せず同一定数で判定できるようにした。 |
| `src/margpa_runtime_llm/bootstrap/repair_live_integration.py` | IR-R5-01 | `_plan_rejudge()`の実処理を`_plan_rejudge_outcome()`へ改名・拡張し、`_RejudgePlanOutcome`(`plan`と`rejection_reason`)を返すよう変更。Counter例外・Counter無usable結果は`"counter_failed"`、Token・Context算術不足は`"token_or_context_insufficient"`、Registry shutdown拒否(新設`_future_rejected_by_shutting_down_registry()`で判定)は`"registry_unavailable"`と分離。旧`_plan_rejudge()`は`_plan_rejudge_outcome(...).plan`を返すだけの薄いWrapperとして維持(既存の直接呼出しTestへの後方互換)。`attempt_live_repair()`側で`rejection_reason`を`repair_rejudge_counter_failed`／`repair_rejudge_worker_registry_unavailable`／`repair_rejudge_budget_insufficient`へ Typedにマップ。Deadline(`overall_budget_exceeded_before_rejudge`)とCancel(`cancellation.is_cancelled()`)の既存の優先チェック順序・帰属ロジックは無変更(前回IR-R4-01のまま)。 |
| `tests/unit/bootstrap/test_repair_live_integration.py` | IR-R5-01 | `test_a_counter_exception_returns_a_typed_result_never_an_uncaught_exception`の期待値を`repair_rejudge_budget_insufficient`→`repair_rejudge_counter_failed`へ訂正(Controllerが誤りと明示的に指摘した既存Test)。新規`test_a_shutting_down_worker_registry_rejects_counting_and_is_reported_distinctly`を追加(Controllerの第2Probe: 事前shutdown済みRegistryを渡すと`repair_rejudge_worker_registry_unavailable`が返ることを実際の`TrackedStageWorkerRegistry`で確認、Rejudge Call 0件)。 |
| `tests/integration/test_real_local_main_gemma_concurrent_dispatch_smoke.py` | IR-R5-02 | Judge起点Gemma Repair Test(`test_a_real_gemma_enforce_repair_run_uses_the_same_condition_rejudge_and_adopts_the_improved_answer`)へHard Assert追加(`repair_outcome=="improved"`、`repair_accepted is True`、`presentation_outcome=="repair_accepted"`、`presented_content.strip()!=""`)、既存Skip境界は無変更(新規Skip追加なし)。Main Governance起点Testを`test_a_real_gemma_main_governance_enforce_run_authorizes_and_persists_the_repair`→`test_a_real_gemma_main_governance_enforce_run_authorizes_and_adopts_the_repair`へ改名、Docstringに既存Fixture-model永続化Testとの二層Evidence関係を明記。 |

## 4. Files Deliberately Not Changed

- Gemma Schema Field順序修正(`selene.py`／`judge_prompt_builder.py`) — 前回IR-R4で受理済み、再設計・再実装なし。
- `LIVE_REPAIR_BUDGET`／`_REJUDGE_TOKENS_PER_CRITERION`等の予算・係数 — 無変更(拡大・削減いずれもなし)。
- `decode_judge_output_fail_closed()`等のDecoder厳密性 — 無変更。
- 不正JSON限定リトライ機構 — 実装せず(既存の保留候補のまま)。
- Main Governance起点Test以外の他3件の実機Test(Crux／OBSERVE／ENFORCE-accept) — 今回は再実行していない(名称・Assert自体も無変更)。
- Selene関連一式 — 今回未着手(延期候補登録のまま)。
- Frontend一式 — 今回未編集。
- `docs/project/shared/unresolved_work/current_unresolved_findings_registry_ja.md`、`docs/project/phases/phase_9/phase_index_ja.md` — 直接編集していない。

## 5. Real Evidence

### 5.1 IR-R5-01 — Planner Failure分類

- 静的確認: `_plan_rejudge_outcome()`の各Return地点で`rejection_reason`を明示的にTag付け。Counter自体が`RuntimeError`を送出する経路、`count_chat_prompt_tokens()`が`None`同等の無usable結果を返す経路は`"counter_failed"`。Token予算・Context算術不足(Counter呼出し前の即時判定、およびCounter成功後のContext超過判定)は`"token_or_context_insufficient"`。事前shutdown済み`TrackedStageWorkerRegistry`が新規submitを拒否する経路(`run_tracked_stage()`がTimeout形状の`TrackedStageOutcome`で返す、`future.exception()`が`tracked_stage_worker.REGISTRY_SHUTTING_DOWN_MESSAGE`と一致)は`"registry_unavailable"`。
- Test実測: `test_a_counter_exception_returns_a_typed_result_never_an_uncaught_exception`(Counter例外)→`rejected_reason=="repair_rejudge_counter_failed"`を確認。新規`test_a_shutting_down_worker_registry_rejects_counting_and_is_reported_distinctly`(実際の`TrackedStageWorkerRegistry().shutdown(timeout_seconds=1.0)`後に渡す)→`rejected_reason=="repair_rejudge_worker_registry_unavailable"`、Rejudge Call 0件を確認。
- Deadline/Cancel回帰確認: `test_a_slow_counter_exhausting_the_overall_deadline_blocks_the_rejudge_call`、`test_a_counter_that_blocks_past_the_deadline_returns_promptly_and_never_reaches_rejudge`、`test_a_cancellation_firing_during_counting_blocks_the_rejudge_call`の3件とも既存の期待値(`repair_budget_exceeded_before_rejudge`／`cancelled_by_main_priority`)のまま全PASS——前回IR-R4-01で確立した優先順序(Cancel確認→全体Budget確認→Plan内訳)は今回変更していない。
- 既存Plan受理/境界Test(26件/21件/22件/27件/32件、`_plan_rejudge()`直接呼出し)は全て無変更のTest本文のまま全PASS——薄いWrapperが旧来の`_RejudgePlan | None`という返り値の形を保っていることを確認。

### 5.2 IR-R5-02 — Judge起点Gemma Repair TestのOracle強化

- 修正後Assert: `result.repair_outcome=="improved"`、`result.repair_accepted is True`、`decision.presentation_outcome=="repair_accepted"`、`candidate not in decision.presented_content`、`decision.presented_content.strip()!=""`。
- 実機実行(1回のみ、Oracle強化後のJudge起点Repairに限定): `uv run pytest tests/integration/test_real_local_main_gemma_concurrent_dispatch_smoke.py::test_a_real_gemma_enforce_repair_run_uses_the_same_condition_rejudge_and_adopts_the_improved_answer -m model_smoke` → **1 passed(16.61s)**。実Gemmaが矛盾Candidateへ実際にDeviationを検出し、実MainがRepair候補を生成、同一GemmaによるRejudgeで改善回答が採用されたことを、safe fallbackでは満たせない強いAssertで直接確認した。
- 他4件の実機Test(Crux／OBSERVE／ENFORCE-accept／Main Governance ENFORCE)は、指示に従い今回は再実行していない。Main Governance起点Testの改名後の関数名がCollect可能であることのみ`--collect-only`で確認(実行はしていない)。

## 6. Focused／Static Verification

- 対象File Ruff: `./.venv/bin/ruff check src/margpa_runtime_llm/bootstrap/repair_live_integration.py src/margpa_runtime_llm/bootstrap/tracked_stage_worker.py tests/unit/bootstrap/test_repair_live_integration.py tests/integration/test_real_local_main_gemma_concurrent_dispatch_smoke.py` → **All checks passed**。
- Canonical Mypy: `./.venv/bin/mypy src tests` → **43 errors, 4 files**(既存Baseline維持、新規Errorなし。対象4File中に本Round変更Fileは含まれない)。
- Backend Full Suite: `./.venv/bin/python -m pytest -q -m "not model_smoke"` → **2317 passed, 29 deselected**(前回2316から新規Registry shutdown Test 1件分の増分)。
- Unit Suite単体: `tests/unit/bootstrap/test_repair_live_integration.py` → **39 passed**。
- 実機Model Smoke: 上記5.2の1件のみ実行、**1 passed**。他4件は今回未実行(前回Returnの5/5 PASSは維持、再検証していない)。
- Frontend: 今回未変更のため再実行していない。

## 7. Internal Review(2回、観点の異なる完全別Pass)

### Review A — Controllerの2指摘への適合性

- [OK] IR-R5-01: Counter例外・Registry shutdown拒否・Token/Context不足の3経路を`_RejudgePlanOutcome.rejection_reason`で明示的に分離し、呼出し元で3種のTyped `rejected_reason`へ写像した。成功PlanへのFallbackは行っていない(全経路でRejudge Call 0件のまま)。Deadline/Cancelの既存の優先チェック順序(前回IR-R4-01)は変更しておらず、回帰Test 3件で確認した。「新規の大きなPlanner階層」は導入していない(1 Dataclass、1 Helper関数、1薄いWrapperのみ)。
- [OK] IR-R5-02: Judge起点Testは、safe fallbackでも通ってしまっていた旧Assert(`presentation_outcome != "candidate_accepted"`等)を、`repair_outcome`／`repair_accepted`／`presentation_outcome`の直接Hard Assertへ置き換え、実機1回で確認した。既存のDeviation-foundSkip境界より後に新規Skipは追加していない(Repair失敗はSkipへ変えていない)。Main Governance起点Testは、Controllerが提示した2案(二層Evidence説明／改名)の両方を適用した(改名 + Docstringでの二層Evidence明記)。新規の実モデル永続化Testは追加していない。

### Review B — 手続き・Regression・実機実行範囲の遵守

- [OK] Git: Read-onlyのみ(変更操作なし)。
- [OK] Append-only: 新規Docs2件(本Return・Recovery)はいずれも新規Path、既存Handoff/Return/History上書きなし。
- [OK] 実機実行範囲: Judge起点Gemma Repair Test 1回のみ実行、他4件(Crux／OBSERVE／ENFORCE-accept／Main Governance ENFORCE)は無目的な再実行をしていない(Collect確認のみ)。
- [OK] 予算・Criterion・Decoder: `LIVE_REPAIR_BUDGET`・`_REJUDGE_TOKENS_PER_CRITERION`・Criterion選択数・Decoder`expected_criterion_ids`厳密性のいずれも変更していない。
- [OK] Gemma Schema Field順序修正(前回受理済み)の再設計・再実装は行っていない(`selene.py`/`judge_prompt_builder.py`は今回のDiffに含まれない)。
- [OK] 実機Trialの`finally`Unload確認(Judge起点Test 1件、既存の`finally: gemma_service.unload(); main_service.unload()`構造のまま、新規Load/Unload構造変更なし)。

## 8. Open Findings／True Stop

Open Findingのまま(True Stopではない、Codex Controller判断待ち):

1. **32件Criterion Rejudge**: 実測校正後も予算不足のまま未変更(前回Returnと同じ)。
2. **Selene**: 未解決のまま(延期候補登録のみ、前回Returnと同じ、今回変更なし)。
3. **Gemma不正JSON欠陥の真因**: 修正は有効だが確定的な根本原因検証はしていない(前回Returnと同じ)。
4. **Mypy 43 errors/4 files**: 既存Baseline、今回のScope外。
5. **Frontend再検証**: 今回変更なしのため未実施。
6. **他4件の実機Test**: 前回5/5 PASSの結果を維持しているが、今回は再実行していない(指示された実行範囲の遵守)。

## 9. Action Inventory

**実行した**: IR-R5-01(Planner Failure分類の実装・既存Test訂正・新規Test追加・全PASS確認)、IR-R5-02(Judge起点TestのHard Assert強化・実機1回確認、Main Governance起点Testの改名)。対象FileのRuff・Canonical Mypy・Backend Full Suite・Unit Suite単体実行。本Return Handoff・Recovery新規File作成。

**実行しなかった**: Gemma Schema修正・Selene・予算・Criterion数・Decoder厳密性のいずれの再設計・再実装。他4件の実機Testの再実行。Git Add/Commit/Push等の変更操作。新規の実モデル永続化Test追加。

**Temporary Artifact／Active Process／Model Load**: 実機Trial(1件)完了後、既存の`finally`Blockにより両Model Unload済み、残存Load・稼働Process・Blocked Threadなし。新規Scratchpad Artifactは今回作成していない。

## 10. Exact Next Action for Codex Controller

1. IR-R5-01(Planner Failure分類)の実装・Test(§3, §5.1, §7 Review A)を、Controller自身のProbe(Counter例外、Registry shutdown拒否)で独立再現し確認する。
2. IR-R5-02(Judge起点Gemma Repair TestのOracle強化)を確認し、`repair_outcome`／`repair_accepted`／`presentation_outcome`のHard Assertが「改善回答の採用」を直接証明する形になっていることに同意するか判断する。Main Governance起点Testの改名(`...adopts_the_repair`)を確認する。
3. 上記1-2を踏まえ、本Rework全体をACCEPTするか、追加のCHANGES REQUIREDを発行するか、あるいはPhase 9-1の次Step(Selene Registry反映判断、32件Criterionの予算方針判断を含む)を判断する。

本Returnの提出をもって停止する。Phase Closure、次Phaseへの着手、追加のGit操作は行わない。Codex Controller Independent Reviewを待つ。
