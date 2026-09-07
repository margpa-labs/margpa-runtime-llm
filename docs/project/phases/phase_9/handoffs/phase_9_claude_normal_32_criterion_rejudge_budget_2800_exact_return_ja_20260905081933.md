# Phase 9-1 — 通常32 Criterion Rejudge予算2800 実装 Exact Return Handoff

```yaml
document_type: exact_return_handoff
document_state: candidate_for_controller_review
from: claude
to: codex_controller
in_response_to: ../handoffs/phase_9_controller_normal_32_criterion_rejudge_budget_2800_exact_handoff_ja_20260905075241.md
git_action: none
network_action: none
external_artifact_mutation: none
closure_authority: none_requested
language: ja
recorded_at: 2026-09-05 08:19:33 JST
```

## 1. Maximum Claim

`P9_1_BUDGET_2800_UNIT_VERIFIED_REAL_32_CRITERION_REJUDGE_INCOMPLETE`

**主張すること**:
- `LIVE_REPAIR_BUDGET.max_additional_tokens`の2000→2800変更(User許可済みの唯一の変更)を実装した。Repair上限400、Rejudge 75 Token/Criterion、最大32 Criterion選択、最大Model Call 2、Deadline、Cancellation、Context上限は無変更。
- Fixture/Unit水準では、通常32 Criterion(候補Token上限400消費時を含む)のToken Plan受理、および実`attempt_live_repair()`を通したRepair→同一32 Criterion Rejudge→改善回答採用のEnd-to-End成立を確認した。
- 旧2000へ戻すRegression Sabotageで、新規/書換Testが意図どおり検出力を持つことを確認し、復元後に差分が残らないことを確認した。

**主張しないこと(明示的除外)**:
- **実機(Main Qwen Repair→Gemma 32 Criterion Rejudge)は、指示どおり正確に1回実行し、不成立(`accepted=False`)だった。** 反復・Criterion削減・追加予算拡大のいずれも行っていない。Complete Candidateへの引き上げは行わない。
- Selene解決、Phase 9-1 Closureは主張しない。
- Gemmaの実機32 Criterion Decode失敗の確定的な根本原因の特定は主張しない(観測結果の報告のみ)。

## 2. 対象

[Codex Controller Exact Handoff(2026-09-05 07:52:41 JST)](../handoffs/phase_9_controller_normal_32_criterion_rejudge_budget_2800_exact_handoff_ja_20260905075241.md)、§2(実装境界)・§3(必須検証A/B)全項目。

## 3. Files Changed

| File | 変更内容 |
|---|---|
| `src/margpa_runtime_llm/bootstrap/repair_live_integration.py` | `LIVE_REPAIR_BUDGET.max_additional_tokens`を2000→2800へ変更(唯一のBudget変更)。`_REJUDGE_TOKENS_PER_CRITERION`・`_REPAIR_MAX_NEW_TOKENS`・`max_total_model_calls`・`max_wall_time_ms`は無変更。2000固定を前提にしていた3箇所のDocstring/Comment(`_REJUDGE_TOKENS_PER_CRITERION`直前、`_plan_rejudge_outcome()`のP1/IR-R2-01 Docstring、`LIVE_REPAIR_BUDGET`直前)を、過去事実(2000当時)と現行値(2800)が混同されないよう最小限訂正。`LIVE_REPAIR_BUDGET`直前のCommentに、実機32 Criterion Rejudgeの今回の不成立結果を明記(Plan/Budget層とReal Decode層は別問題である旨)。 |
| `tests/unit/bootstrap/test_repair_live_integration.py` | 2000時点の境界を記述していた4 Test(26/21・22/27/32件不成立)を削除し、現行2800境界を記述する3 Test(32件Plan受理・32/33件境界・2800を1 Token超過時の拒否)へ置換。32件の`_plan_rejudge()`直接呼出しTest(旧: 40件へ変更、40は現行2800でも genuinely 予算超過)のDocstring/件数を訂正。既存End-to-End Test`test_a_large_criterion_count_never_reaches_the_rejudge_call_end_to_end`(32件不成立を証明)を`test_a_normal_32_criterion_selection_rejudge_succeeds_end_to_end_within_the_2800_token_live_budget`(候補Token上限400消費時の32件成立をEnd-to-Endで証明)へ全面書換。`test_a_rejudge_that_overruns_its_own_affordable_plan_is_still_rejected_after_the_call`の`rejudge_completion_tokens`を2500→3000へ訂正(現行2800を確実に超過する値)。他Docstring内の2000言及を過去形へ訂正。 |
| `tests/integration/test_real_local_main_gemma_concurrent_dispatch_smoke.py` | 実機32 Criterion Rejudge Smoke Test(`test_a_real_normal_32_criterion_selection_repair_on_main_rejudge_on_gemma_within_the_2800_budget`)を新規追加。実109 CriterionコーパスからCodex Controller Handoff §3.Bの指示どおり`freeze_semantic_turn(max_criteria=32)`で通常選択した実32 Criterionを、Main Qwen(Repair Candidate)→Gemma(同一Frozen 32 Criterion Rejudge)へ`attempt_live_repair()`で直接渡す。Module Docstringへ今回の実機結果(不成立)を追記。 |

## 4. Files Deliberately Not Changed

- Selene関連一式、不正JSON限定リトライ機構、`decode_judge_output_fail_closed()`のDecoder厳密性 — 無変更。
- IR-R5-01 Planner Failure分類(`_plan_rejudge_outcome()`のCounter失敗/Registry shutdown/Token・Context不足の3分岐)・IR-R5-02 Gemma Golden Path・Gemma Schema Field順序修正 — 受理済みのため再設計・再実装なし。
- Context上限、`max_new_tokens`全体設定、Call上限(`max_total_model_calls=2`)、`max_wall_time_ms` — 無変更。
- Frontend一式 — 今回未編集。
- `docs/project/shared/unresolved_work/current_unresolved_findings_registry_ja.md`、`docs/project/phases/phase_9/phase_index_ja.md` — 直接編集していない。

## 5. Real Evidence

### 5.1 §3.A — Fixture/Unit(4項目)

1. **候補Token上限400消費後も32 Criterion全件のPlanが2400 Tokenで成立**: `test_a_32_criterion_token_plan_is_the_boundary_when_the_candidate_uses_its_full_token_allowance`で確認(`400+75*32=2800<=2800`ちょうど、33件は`2875>2800`で不成立)。
2. **32件を1件も落とさずRepair→同一集合Rejudge→改善採用がEnd-to-Endで成立**: `test_a_normal_32_criterion_selection_rejudge_succeeds_end_to_end_within_the_2800_token_live_budget`で確認。`repair_completion_tokens=400`(候補Token上限を実際に消費)、Rejudge Callの`max_new_tokens==2400`、`result.accepted is True`、実Model Call数2回、合計使用量が2800以下であることを確認。
3. **2800を1 Tokenでも超える条件・Context不足・Deadline・Cancel・Counter失敗・Registry shutdownは従来どおりTypedに拒否**: `test_the_2800_token_budget_is_exceeded_by_exactly_one_token_and_rejected`(新規、32件・remaining=2399で不成立)に加え、IR-R5-01由来の既存Test(Counter失敗→`repair_rejudge_counter_failed`、Registry shutdown→`repair_rejudge_worker_registry_unavailable`、Deadline→`repair_budget_exceeded_before_rejudge`、Cancel→`cancelled_by_main_priority`)を無変更のまま全PASSで再確認。
4. **旧2000へ戻すRegression Sabotageで検出力を証明**: `max_additional_tokens`を一時的に2000へ戻し、新規/書換の3 Test(32件Plan受理・32/33境界・32件E2E成功)を実行 → **3件とも意図どおり失敗**(`assert None is not None`×2、`accepted is False`×1)。直後に2800へ復元し、バックアップとのdiffが完全に一致すること(`diff`コマンドで無差分)を確認、Unit Suite再実行で全PASSに復帰したことを確認した。

### 5.2 §3.B — 実モデル(1回のみ)

`test_a_real_normal_32_criterion_selection_repair_on_main_rejudge_on_gemma_within_the_2800_budget`を、Apple Silicon実機でMain(Qwen, context=16384)+Gemma(context=8192)同時Load下、**正確に1回**実行した。

実109 CriterionコーパスをMain実機Corpus読込Pipelineで読み込み、実`freeze_semantic_turn(max_criteria=32)`で通常どおり32件選択(`selected=32, deferred=77`)、`attempt_live_repair()`を直接呼出し(`service`=実Main、`rejudge_service`=実Gemma、`rejudge_criteria`=同一32 Criterion、`before_recommendation`=NEEDS_REPAIRをScript指定——このTestはRejudge自体の検証が目的であり、上流のDeviation検出パスは検証対象外のため)。

**結果: 不成立(`accepted=False`)。**

```text
[FACT] result.rejected_reason は事前Typed拒否(Budget不足/Deadline/Cancel/
       Counter失敗/Registry shutdown)のいずれでもなかった(該当Setに
       含まれないことをHard Assertで確認、PASS) -- Plan/Budget層は
       実機でも2800がPlan=2400を正しく受理した。
[FACT] result.rejudge_model_identity == "judge.gemma-4-e2b-it-q4-0"、
       result.rejudge_role == "independent_artifact" -- 同一Gemma
       Identityも確認(PASS)。
[FACT] result.outcome == "unknown"、result.accepted == False、
       rejected_reason は事後(Rejudge後)のNone(Pre-call Typed失敗では
       ない)。`evaluate_repair_success()`の定義上、before=NEEDS_REPAIR
       かつafter=UNKNOWNの場合のみoutcome="unknown"になるため、Gemma
       自身のRejudge Decodeが32 Criterion規模でCOMPLETEDに至らなかった
       (Fail-closed)ことに一致する観測結果である。
[FACT] 実Token/時間の詳細Telemetryは、この回では未捕捉(Test構造上、
       Print文が後続のAssert失敗より後に配置されていたため)。再実行して
       捕捉することはせず(指示どおり反復禁止)、Test自体は将来の実行で
       捕捉できるようPrint配置をAssert前へ修正した(今回の1回の実施結果
       自体には影響しない、コードのみの事後修正)。
```

反復・Criterion削減・追加予算拡大のいずれも行っていない。観測結果をそのまま報告する。

## 6. Focused／Static Verification

- 対象File Ruff: `./.venv/bin/ruff check src/margpa_runtime_llm/bootstrap/repair_live_integration.py tests/unit/bootstrap/test_repair_live_integration.py tests/integration/test_real_local_main_gemma_concurrent_dispatch_smoke.py` → **All checks passed**。
- Canonical Mypy: `./.venv/bin/mypy src tests` → **43 errors, 4 files**(既存Baseline維持、新規Errorなし)。
- Unit Suite単体: `tests/unit/bootstrap/test_repair_live_integration.py` → **38 passed**(前回38、Test構成の純増減±0——4 Test削除・3 Test追加・1 Test改名)。
- Backend非実機Full Suite: `./.venv/bin/python -m pytest -q -m "not model_smoke"` → **2316 passed, 30 deselected**(前回2316/29から、新規実機Test 1件分でDeselected数のみ増分)。
- 実機Model Smoke(対象Testのみ、1回): **1 failed**(§5.2のとおり、観測結果として報告)。他の既存実機Test(Golden Path 4件・Crux 1件)は指示により再実行していない。
- Frontend: 今回未変更のため再実行していない。

## 7. Internal Review(2回、観点の異なる完全別Pass)

### Review A — Handoffの実装境界・必須検証への適合性

- [OK] §2実装境界: `max_additional_tokens`のみ変更、他のBudget/Criterion/Decoder値は全て無変更であることをGrep・Diffで確認。
- [OK] §2 Source Comment/Test更新: 2000固定前提の記述を過去事実として明示し直し、Current値(2800)との混同を排除。22/26/27/32-不成立という古い境界をCurrent仕様として残していない。
- [OK] §3.A 1-4全項目: Fixture/Unit水準で全て確認、旧2000へのSabotageで検出力を実証。
- [OK] §3.B: 実機試験を正確に1回実行、Artifact不足以外でSkipしていない、失敗を反復せず観測結果とTyped結果をそのまま報告している。
- [OK] §4禁止事項: Selene・JSON Retry・Decoder緩和・Context/Global max_new_tokens・Call上限・Batching・Native/Download/ResourceGate・Frontend・Phase 9-2/9-3・Closure・Git変更のいずれも行っていない。IR-R5-01/IR-R5-02/Gemma Schema修正等の受理済み実装は再設計していない。

### Review B — 手続き・Regression・実機結果の正直な報告

- [OK] Git: Read-onlyのみ(変更操作なし)、`git status`で意図しない変更がないことを確認。
- [OK] Append-only: 新規Docs2件(本Return・Recovery)は新規Path、既存Handoff/History上書きなし。
- [OK] Sabotage実施と復元: 一時変更→3 Test失敗確認→復元→バックアップとのdiff完全一致(無差分)→Unit Suite再確認、を実施し、コードへの残留影響がないことを確認した。
- [OK] 実機失敗の扱い: Skipへ変えず、Hard Assert失敗のまま維持した(§5.2)。Print文配置の事後修正はTelemetry捕捉のための将来向けCode改善であり、今回の実施結果自体を書き換えるものではないことを明記した。
- [OK] Maximum Claimは実結果(実機不成立)に合わせ、Complete Candidateへの引き上げは行っていない。

## 8. Open Findings／True Stop

Open Findingのまま(True Stopではない、Codex Controller判断待ち):

1. **実機32 Criterion Rejudge**: 今回1回の実施で不成立(`accepted=False`, `outcome=unknown`)。Plan/Budget層は正しく機能したが、実Gemmaによる32 Criterion規模でのDecodeが今回はCOMPLETEDに至らなかった。根本原因(小型ModelのDecode限界か、他の要因か)は未確定。
2. **実Token/時間Telemetry**: 今回の1回の実施では未捕捉(構造上の理由)。次回実施があれば捕捉できるようCode側は修正済み。
3. **Selene**: 未解決のまま(前回Returnと同じ、今回変更なし)。
4. **Mypy 43 errors/4 files**: 既存Baseline、今回のScope外。
5. **Frontend再検証**: 今回変更なしのため未実施。

## 9. Action Inventory

**実行した**: `LIVE_REPAIR_BUDGET.max_additional_tokens`の2000→2800変更、関連Source Comment訂正、Fixture/Unit Test群の書換・新規追加(§3.A 1-4全項目)、旧2000へのSabotage検証と復元確認、実機32 Criterion Rejudge Smoke Testの新規実装、実機試験1回の実施と結果の正直な報告、対象File Ruff・Canonical Mypy・非実機Full Suite・Unit Suite単体実行。Telemetry捕捉のためのCode側の事後修正(実行結果への影響なし)。本Return Handoff・Recovery新規File作成。

**実行しなかった**: 実機試験の反復・再実行。Criterion削減・追加予算拡大による実機不成立への対処。Selene・JSON Retry・Decoder・Context/Global設定・Call上限・Batching・Native/Download/ResourceGate・Frontend・Phase 9-2/9-3・Closureへの着手。Git Add/Commit/Push等の変更操作。既存Mypy 43件の無断修復。

**Temporary Artifact／Active Process／Model Load**: 実機Trial完了後、既存の`finally`BlockによりMain/Gemma両Model Unload済み、残存Load・稼働Processなし。Sabotage検証用のBackup FileはScratchpad配下(Session-scoped)に作成、復元後も参照用に保持。

## 10. Exact Next Action for Codex Controller

1. `LIVE_REPAIR_BUDGET.max_additional_tokens`の2000→2800変更が、指示された実装境界(他のBudget/Criterion/Decoder値は無変更)どおりであることを確認する。
2. §3.A Fixture/Unit水準の4項目(Plan成立・E2E成立・境界拒否・Sabotage検出力)を確認する。
3. §3.B実機試験の結果(1回実施、不成立、観測結果の報告)を確認し、次のStep(再試行を承認するか、Fixture水準の成立で本Handoffを一旦区切りとするか、他の対応を判断するか)をUserとともに判断する。
4. 上記を踏まえ、本Rework全体をACCEPTするか、追加のCHANGES REQUIREDを発行するか判断する。

本Returnの提出をもって停止する。Phase Closure、次Phaseへの着手、追加のGit操作は行わない。Codex Controller Independent Reviewを待つ。
