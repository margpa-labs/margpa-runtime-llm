# Phase 9-1 Judge／Governance — Controller独立Review(IR-R4版) 残差Rework Exact Return Handoff

```yaml
document_type: exact_return_handoff
document_state: candidate_for_controller_review
from: claude
to: codex_controller
in_response_to: ../history/operations/phase_9_1_controller_ir_r3_return_review_and_delta_rework_ja_20260905003507.md
git_action: none
network_action: none
external_artifact_mutation: none
closure_authority: none_requested
language: ja
recorded_at: 2026-09-05 03:07:20 JST
```

## 1. Maximum Claim

`P9_1_REWORK_INCOMPLETE_FOR_CONTROLLER_REVIEW`

**主張しないこと(明示的除外)**:
- 32件Criterionの通常選択規模でのRejudge成立(Plan受理・実行成立とも)は主張しない。実測校正後も予算不足のまま(未変更、前回Return維持)。
- Seleneの未解決状態自体の解消は主張しない。延期は「登録された候補」であり、「完成」への言い換えではない。
- Phase Closureは主張しない。次Phaseへも進まない。

**今回新たに成立した主張**:
- Gemma実機のGolden Path(OBSERVE／ENFORCE／Repair→同条件Rejudge→採用／Main Governance ENFORCE)が、局所修復(第2仮説、Schema Field順序変更)を経て、実機5/5全PASSで成立した。User事前承認条件が今回初めて両方充足したため、Seleneを延期候補として登録した(Selene自体の未解決状態は変更なし)。

## 2. 対象

[Controller独立Review(2026-09-05 00:35:07 JST)](../history/operations/phase_9_1_controller_ir_r3_return_review_and_delta_rework_ja_20260905003507.md)のIR-R4-01、IR-R4-02、§4(off/observeパラメータ化)、§4/§5(Gemma別仮説局所修復)、全項目。

## 3. Files Changed

| File | 対応項目 | 変更内容 |
|---|---|---|
| `src/margpa_runtime_llm/bootstrap/repair_live_integration.py` | IR-R4-01 | `_plan_rejudge()`内の`count_chat_prompt_tokens()`呼出しを`run_tracked_stage()`(既存の追跡Worker機構)で包み、残り全体Wall-time Deadlineで有界化。呼出し元で、Planning後のCancellation再チェックを`_budget_exceeded`チェックより先に実施。`_budget_exceeded`を`rejudge_plan is None`より先にチェックする順序へ変更し、Timeout由来のNoneをToken不足へ誤帰属させない。`attempt_live_repair()`/`_plan_rejudge()`へ`tracked_stage_registry`引数を追加。 |
| `src/margpa_runtime_llm/bootstrap/judge_live_integration.py` | IR-R4-01 | `RepairExecutorPort`へ`tracked_stage_registry`引数を追加、`repair_executor(...)`呼出しへ同Hookが既に保持するRegistryを転送。 |
| `src/margpa_runtime_llm/bootstrap/web_application.py` | IR-R4-01 | `_repair_executor`Closureへ`tracked_stage_registry`引数を追加、`attempt_live_repair()`へ転送。 |
| `src/margpa_runtime_llm/adapters/evaluation/selene.py` | §4/§5(Gemma局所修復) | `SelenePromptAdapter.build()`のSchema構築DictでCriterion Entry内`evidence_refs`(配列)を最後のFieldから外し、`reason_code`の前へ移動(Field順序のみ、Decoder無変更)。 |
| `src/margpa_runtime_llm/modules/evaluation/application/judge_prompt_builder.py` | §4/§5(Gemma局所修復) | `_semantic_response_instruction()`で同様のField順序修正(Main-shared用、Repair Rejudgeの現行Prompt含む)。 |
| `tests/unit/bootstrap/test_repair_live_integration.py` | IR-R4-01, IR-R4-02, IR-R4-05 | Controller Probe(Event解放待ちCounter、Counter内Cancel)の正確な再現Test 2件追加。既存Test名・DocstringをPlan受理の言明へ訂正、候補Token上限400消費時の21件境界Test追加。 |
| `tests/unit/bootstrap/test_judge_live_integration.py`, `test_judge_live_integration_dispatch_router.py` | IR-R4-01 | Fake Repair Executor関数4件へ`tracked_stage_registry`引数追加(既存Pattern踏襲)。 |
| `tests/unit/bootstrap/test_judge_repair_rejudge_normal_enforce_save_path.py` | IR-R4 §4 | 既存Main起点保存Test 2件を`repair_mode ∈ {"off","observe"}`でParametrize。既存Judge起点Test 2件は無変更のまま保持。 |
| `tests/integration/test_real_local_main_gemma_concurrent_dispatch_smoke.py` | IR-R4 §4/§5 | Golden Path実機Test 4件新規追加(OBSERVE／ENFORCE-accept／ENFORCE-Repair-Rejudge／Main Governance ENFORCE)。Module Docstring更新。 |

## 4. Files Deliberately Not Changed

- `config/judge_templates/gemma_4_e2b/`(Template File・Manifest) — 今回未編集。Schema自体はPython側で動的生成されるため、Field順序修正にTemplate File変更・Digest再計算は不要。
- `docs/project/shared/unresolved_work/current_unresolved_findings_registry_ja.md` — Stable文書のため直接編集していない。
- `docs/project/phases/phase_9/phase_index_ja.md` — 直接編集していない。
- Frontend一式 — 今回未編集。

## 5. Real Evidence

### 5.1 IR-R4-01 — Plannerの待機・Cancel境界(Controller Probe再現)

- Event解放待ちProbe: `_EventBlockingCounterRepairService`(無期限Block)+`RepairBudget(max_wall_time_ms=100)`で、`attempt_live_repair()`自体が~100ms付近で速やかに復帰(2秒未満、Safety Net 5秒とは別に実測)、`repair_budget_exceeded_before_rejudge`、Rejudge Call 0件を確認(`test_a_counter_that_blocks_past_the_deadline_returns_promptly_and_never_reaches_rejudge`)。BlockされたBackground Threadは強制終了せず、Test自身がEvent解放。
- Counter内Cancel Probe: `_SelfCancellingCounterRepairService`(Counter自身が渡されたCancellationTokenをCancelしてから正常値を返す)で、`cancelled_by_main_priority`、Rejudge Call 0件を確認(`test_a_cancellation_firing_during_counting_blocks_the_rejudge_call`)。

### 5.2 IR-R4-02 — 「26件成立」の訂正

Test名・Docstringを「26件Token Plan受理」(実行成立ではない)へ訂正。候補Token上限400消費時の境界(21件成立/22件不成立)を新規Testで追加確認。新規短文Snapshotで測定・Plan・実行の3層を明示的に分離。

### 5.3 IR-R4 §4前半 — Main起点off/observeパラメータ化

既存2 Testを`repair_mode ∈ {"off","observe"}`でParametrize(計4パラメータ化Test + 既存Judge起点2Test = 6 Test)、全PASS。Helper／Docstringの複製はせず、既存Builder関数へ`repair_mode`引数を追加するのみ。

### 5.4 IR-R4 §4/§5 — Gemma別仮説局所修復とGolden Path実機成立(最重要)

第2仮説(応答末尾の連続4個閉じ構造Tokenのうち、evidence_refs自身の`]`が常に欠落 → Criterion Entry内でevidence_refsを最後のFieldにしない)を、Source変更前に有界2回(誤答・正答)の診断Scriptで検証、2/2とも構文的に有効なJSONを確認。正式にSource実装(`selene.py`/`judge_prompt_builder.py`のSchema Field順序修正、Decoder無変更)。

修正後、Gemma実機Test 5件(既存Crux Test含む)を実行し、**5/5全PASS**:
- Native Crash非再現(Crux、修正前はSkip扱いだった箇所が今回はPASS)。
- OBSERVE(実Gemma Dispatch正常完了)。
- ENFORCE-accept(正答Candidateを正しくaccept)。
- ENFORCE-Repair(実GemmaがDeviation検出、Main候補生成、同一GemmaによるRejudgeで改善回答採用、Hard Assertion)。
- Main Governance ENFORCE(Judge側Repair Mode=OFF、Main Governance自身の判断のみでRepair成立)。

詳細は[新規Snapshot](../../../shared/history/unresolved_work/phase_9_1_gemma_golden_path_normalized_via_schema_field_order_fix_snapshot_ja_20260905030530.md)。User事前承認条件(Gemma正常利用・後工程非依存)が今回両方充足したため、**Seleneを延期候補として登録**した(Selene自体の未解決状態、Native Crash原因未確定は変更なし。「完成」への言い換えはしていない)。

## 6. Focused／Static Verification

- Backend Full Suite: `uv run pytest -q` → **2316 passed, 29 deselected**(前回2311/25から、新規Test追加分)。
- Selene/Gemma/judge_prompt個別再検証: `uv run pytest -q -k "selene or gemma or judge_prompt"` → **81 passed**(共有Prompt構築Code変更の回帰確認)。
- Backend Ruff: `uv run ruff check .` → **All checks passed**。
- Backend Mypy: `./.venv/bin/mypy src tests`(Controllerと同一Command) → **43 errors, 4 files**(既存Baseline維持、新規Errorなし)。
- 実機Model Smoke(Gemma、Main+Gemma同時Load): `uv run pytest tests/integration/test_real_local_main_gemma_concurrent_dispatch_smoke.py -m model_smoke` → **5 passed**(前回1 skippedから、局所修復後は全PASS)。
- Frontend: 今回未変更のため再実行していない。

## 7. Internal Review(2回、観点の異なる完全別Pass)

### Review A — Controllerの4指摘への適合性

- [OK] IR-R4-01: Controllerの2つの正確なProbe(Event解放待ち、Counter内Cancel)で再現・修正を実測確認。`_budget_exceeded`を`rejudge_plan is None`より先にチェックする順序変更により、Timeout由来のNoneをToken不足へ誤帰属させない設計とした。
- [OK] IR-R4-02: 「26件成立」→「26件Plan受理」への言い換え、21件境界の追加確認、測定/Plan/実行の3層分離を短文Snapshotで明示。
- [OK] §4前半: 既存2 TestをParametrizeのみで拡張、複製なし。
- [OK] §4/§5: 第1仮説(前回)と明確に異なる第2仮説を有界2回(Source変更前)で判定、成功後のみGolden Path確認へ進んだ。予算拡大・Criterion削減・Decoder緩和・Native更新・Download・新Resource Gate・Selene追加試行のいずれも行っていない。

### Review B — 手続き・Regression・Evidence整合

- [OK] Git: Read-onlyのみ。
- [OK] Append-only: 新規Docs4件はいずれも新規Path、既存Handoff/Return/History上書きなし。
- [OK] 共有Code変更(`selene.py`/`judge_prompt_builder.py`)の影響範囲確認: Backend全体Regression(2316 passed)に加え、Selene/Gemma/judge_prompt個別再検証(81 passed)を実施し、Field順序変更がSelene/Main-self側へ悪影響を与えていないことを確認した。
- [OK] 実機Trial全てで`finally`によるUnload・Event解放を確認、残存Load・Blockされたままの Threadなし。
- [OK] Selene延期の登録は「候補」としての言明に留め、Selene自体の未解決状態(Native Crash原因未確定)を「解決」と言い換えていないことを確認。

## 8. Open Findings／True Stop

Open Findingのまま(True Stopではない、Codex Controller判断待ち):

1. **Selene**: 未解決のまま(延期候補として登録のみ、完成への言い換えなし)。Native Crash原因は未確定。
2. **32件Criterion Rejudge**: 実測校正後も予算不足のまま未変更(前回Returnと同じ)。
3. **Gemma不正JSON欠陥の真因**: 修正は有効だったが、「小型Modelの構造的限界」という仮説自体を確定的に検証したわけではない(効果があった修正の理由は仮説と整合するに留まる)。
4. **Mypy 43 errors/4 files**: 既存Baseline、今回のScope外。
5. **Frontend再検証**: 今回変更なしのため未実施。

## 9. Action Inventory

**実行した**: IR-R4-01〜§5全項目の実装・Test追加・実行・全PASS確認。Gemma別仮説の有界2回診断→正式Source実装→Golden Path実機5件全PASS確認。新規History Snapshot 3件作成。Backend Full Suite・Ruff・CanonicalなMypy Command・Selene/Gemma個別再検証の最終実行。本Return Handoffの新規File作成。

**実行しなかった**: 32件Criterion成立のための予算拡大・Batching機構追加。Seleneの新規実機実行。既存Mypy 43件の無断修復。Git Add/Commit/Push等の変更操作。Selene自体の「解決」宣言。

**Temporary Artifact／Active Process／Model Load**: 全実機Trialで`finally`Unload・Event解放を確認、残存Load・稼働Process・Blocked Threadなし。Scratchpad配下のScript/Logは保持(絶対Pathを新規Docsへ記録済み)。

## 10. Exact Next Action for Codex Controller

1. IR-R4-01(Planner待機・Cancel境界)の修正・Test(§3, §5.1, §7 Review A)を、Controller自身のProbe(Event解放待ち、Counter内Cancel)で独立再現し確認する。
2. IR-R4-02(26件成立の訂正)を確認し、「Plan受理」と「実行成立」の区別が今後も維持されることに同意するか判断する。
3. Main起点off/observeパラメータ化(§4前半)を確認する。
4. Gemma別仮説局所修復とGolden Path実機成立(§4/§5、§5.4)を確認し、Seleneを延期候補として登録した判断に同意するか判断する。同意する場合、Registry本体(`current_unresolved_findings_registry_ja.md`)への反映可否を判断する。
5. 上記1-4を踏まえ、本Rework全体をACCEPTするか、追加のCHANGES REQUIREDを発行するか、あるいはPhase 9-1の次Stepを判断する。

本Returnの提出をもって停止する。Phase Closure、次Phaseへの着手、追加のGit操作は行わない。Codex Controller Independent Reviewを待つ。
