# Phase 9-1 — 実32 Criterion Rejudge Budget 3600 実装 Exact Return Handoff

```yaml
document_type: exact_return_handoff
document_state: candidate_for_controller_review
from: claude
to: codex_controller
in_response_to: ../handoffs/phase_9_controller_real_32_criterion_rejudge_budget_3600_exact_handoff_ja_20260905091431.md
git_action: none
network_action: none
external_artifact_mutation: none
closure_authority: none_requested
language: ja
recorded_at: 2026-09-05 09:30:32 JST
```

## 1. Maximum Claim

`P9_1_REAL_32_CRITERION_REJUDGE_BUDGET_3600_GENUINELY_SUCCEEDED`

**主張すること**:
- User承認済みの2値変更(`_REJUDGE_TOKENS_PER_CRITERION` 75→100、`LIVE_REPAIR_BUDGET.max_additional_tokens` 2800→3600)のみを実装した。Repair Candidate 400、通常32 Criterion選択、最大Model Call 2、Main Context 16384、Gemma Context 8192、Rejudge Deadline 120秒はいずれも無変更。
- Fixture/Unit水準(§3、6項目全て)の成立を確認した。旧75/2800へのSabotageで新境界Testが失敗することを確認し、復元後の差分ゼロを確認した。
- Preflightで残存Process/Portなしを確認し、実機試験を正確に1回実行した。**今回、実Main Qwen Repair→実Gemma 32 Criterion Rejudgeが、Decoder COMPLETED・全32 ID一致・Recommendation ACCEPT・改善回答採用という形で、真に成立した。** `finish_reason=STOP`(正常終了、前回のLENGTHではない)、`completion_tokens=3011`(Plan上限3200を使い切る前に自然終了)。

**主張しないこと(明示的除外)**:
- この1回の成功が「常に成功する」ことの保証だとは主張しない——実Modelの非決定性は変わらず存在する。
- Selene解決、Phase 9-1 Closureは主張しない。
- Decoder/Schema/Prompt/Batchingへの変更は行っていない(禁止事項どおり)。

## 2. 対象

[Codex Controller Exact Handoff(2026-09-05 09:14:31 JST)](../handoffs/phase_9_controller_real_32_criterion_rejudge_budget_3600_exact_handoff_ja_20260905091431.md)、§2(実装)・§3(Fixture/Unit 6項目)・§4(実機1回)全項目。

## 3. Files Changed

| File | 変更内容 |
|---|---|
| `src/margpa_runtime_llm/bootstrap/repair_live_integration.py` | `_REJUDGE_TOKENS_PER_CRITERION`を75→100、`LIVE_REPAIR_BUDGET.max_additional_tokens`を2800→3600へ変更(唯一の2値変更)。両定数直前のComment群を、2000→2800→3600という履歴を正確に区別する形で最小訂正(前回2800の実機Confirm済みTruncate Evidenceを引用し、今回の変更の根拠として明記)。 |
| `tests/unit/bootstrap/test_repair_live_integration.py` | 32/33 Criterion境界Test群・E2E成功Test・1 Token超過Testを75/2800→100/3600へ全面書換(関数名・Docstring・Assert値含む)。`test_a_rejudge_that_overruns_its_own_affordable_plan_is_still_rejected_after_the_call`の`rejudge_completion_tokens`を3000→4000へ訂正(新3600 Budgetを確実に超過する値)。他Docstring内の2800/375等の言及を3600/500等へ訂正。 |
| `tests/integration/test_real_local_main_gemma_concurrent_dispatch_smoke.py` | 実機32 Criterion Testを`..._within_the_2800_budget`→`..._within_the_3600_budget`へ改名、Docstringを前回のTruncate Confirm結果と今回の変更根拠で更新。Test-only Observabilityへ`raw_content.count("criterion_id")`による出現数Countを追加。Module Docstringへ前回Confirm結果と今回のUpdateを追記。 |

## 4. Files Deliberately Not Changed

- `judge_output_decoder.py`(Production Decoder/Contract)、Schema、Prompt、Batching機構 — 無変更。
- `_REPAIR_MAX_NEW_TOKENS`(400)、`max_total_model_calls`(2)、Main Context(16384)、Gemma Context(8192)、Rejudge Deadline(`LOCAL_MACOS_MAIN_SELF_JUDGE_BUDGET.rejudge_budget_ms=120_000`) — 無変更(Grep・Diffで確認済み)。
- 通常32 Criterion選択上限 — 無変更。
- Selene関連一式、Frontend一式 — 今回未編集。
- `docs/project/shared/unresolved_work/current_unresolved_findings_registry_ja.md`、`docs/project/phases/phase_9/phase_index_ja.md` — 直接編集していない。
- 旧Return/Recovery一式 — 上書きしていない(append-only)。

## 5. Real Evidence

### 5.1 §3 Fixture／Unit(6項目)

1. **400＋32×100＝3600でPlan成立**: `test_a_32_criterion_token_plan_is_the_boundary_when_the_candidate_uses_its_full_token_allowance`で確認(`plan_32.max_new_tokens==3200`、候補400消費時に成立、33件では`3700>3600`で不成立)。
2. **Rejudge max_new_tokens＝3200**: 上記および`test_a_32_criterion_token_plan_is_accepted_within_the_3600_budget_after_a_minimal_candidate_cost`で確認(`_REJUDGE_TOKENS_PER_CRITERION*32==3200`)。
3. **同一32 CriterionのRepair→Rejudge→改善採用**: `test_a_normal_32_criterion_selection_rejudge_succeeds_end_to_end_within_the_3600_token_live_budget`で確認(Fixture水準、`accepted is True`、Model Call 2回、合計使用量3600以下)。
4. **局所Budget 3599で1 Token不足**: `test_the_3600_token_budget_is_exceeded_by_exactly_one_token_and_rejected`で確認(局所`RepairBudget(max_additional_tokens=3599)`、Production `LIVE_REPAIR_BUDGET`は3600のまま無変更であることも同Test内でAssert)。
5. **33 CriterionはProduction Budget 3600で拒否**: 上記項目1の33件側で確認。
6. **既存Typed FailureとCall抑止を維持**: Context不足・Counter失敗・Deadline・Cancel・Registry shutdownの既存Test群(IR-R5-01由来)は無変更のまま全PASS(Unit Suite単体38 passed、§6)。

### 5.2 §3.6 — 旧75／2800へのSabotage検証

`_REJUDGE_TOKENS_PER_CRITERION`を一時的に75へ、`LIVE_REPAIR_BUDGET.max_additional_tokens`を一時的に2800へ戻し、新境界Test群(32/33件境界・E2E成功・1 Token超過の4 Test)を実行 → **4件とも意図どおり失敗**(`plan_32.max_new_tokens`不一致×2、`plan is None`不成立、`LIVE_REPAIR_BUDGET.max_additional_tokens==3600`不一致)。直後に100/3600へ復元し、バックアップとのdiffが完全一致(無差分)であることを確認、Unit Suite再実行で全PASSに復帰したことを確認した。

### 5.3 §4 — 実機1回(Preflight含む)

**Preflight(Read-only)**: `ps aux`によるpython/pytest/llama/uvicorn/margpa関連Process、`lsof`による全LISTEN Port・Port 8000個別確認、いずれも該当なし。Kill操作は発生していない。

**実行**: `set -o pipefail`付きで対象Testを正確に1回実行、出力を`tail`を経由せず`tee`で`/private/tmp/phase9_gemma32_claude_budget3600_capture_20260905091431.log`へ完全保存、pytest終了Codeを保持した。

```text
[FACT] pytest終了Code: 0(PASSED)。"1 passed in 96.78s (0:01:36)"。
[FACT] 完全Log絶対Path:
       /private/tmp/phase9_gemma32_claude_budget3600_capture_20260905091431.log
[FACT] 完全Log SHA-512:
       91ba197af7087f35a74801d284bc45fbc2ddaf2abe02a87e02df95bfb4d9b43
       d86657e755eae6bacc23a61107602bdd3a9935bb9c43d94ae77963043520377f9
[FACT] 完全Logサイズ: 1085 bytes、6行。
[FACT] `[real-32-criterion-rejudge-evidence]` Marker: 1件(4行目、実行結果
       がPASSだったためTraceback由来の重複表示はなし)。
```

**Marker実測値の転記**(Raw Content全文は転記しない):

| 項目 | 値 |
|---|---|
| `result_outcome` | `'improved'` |
| `result_accepted` | `True` |
| Rejudge Requestの`max_new_tokens` | `3200` |
| `finish_reason` | `<FinishReason.STOP: 'stop'>` — **正常終了**(前回2800回のLENGTH打ち切りとは異なる) |
| Prompt Token | `3612` |
| Completion Token | `3011`(Plan上限3200を使い切る前に自然終了、`3200-3011=189`の余裕を残して完了) |
| 生成時間 | `85.07035487500252`秒(elapsed_ms=85645) |
| Raw Content文字数 | `9704`文字 |
| Raw Content SHA-512 | `fe2cd931d19b8e1275dc256b3eef2465c27053aebb4f9281e025db4460d95887127291567bd352408f243dd46fc73150c5ca6bc098f35fd6e8c594215254afa7` |
| Raw内`criterion_id`出現数 | `32`(新規追加のObservability、期待どおり32件) |
| Strict Decode State(診断用) | `'completed'` |
| Strict Decode Reason | `None`(失敗なし) |
| Recommendation | `'accept'` |
| pass/deviation/unknown | `32`/`0`/`0` |
| missing ID | `[]`(空、欠落なし) |
| extra ID | `[]`(空、余剰なし) |
| Gemma Identity | `result.rejudge_model_identity == "judge.gemma-4-e2b-it-q4-0"`、`result.rejudge_role == "independent_artifact"`(いずれもTest自身のHard Assertが通過したことにより確定。値そのものはPrint未対象だったため、この2点は「Assert通過という事実」からの確定であり、Log中の生の文字列としては記録していない——正直な報告として明記する) |
| 改善採用 | `result.accepted is True`、`result.outcome == "improved"`(Hard Assert通過により確定) |
| Presented Content | 非空(`.strip() != ""`)かつ元の誤答(`"...Tenon."`)を含まないことをHard Assertで確認(通過)。具体的な文字列自体はPrint対象に含めていなかったため、Logには記録されていない——Raw Content同様の理由で全文をDocsへ書く必要はないと判断したが、この項目については「Assert通過という事実」からの確定であることを正直に明記する |

**Post-run確認(Read-only)**: 残存Process・Port Listenともになし。両ModelがTest自身の`finally`Blockで正常にUnloadされたことを確認した。

## 6. Focused／Static Verification

- 対象Unit: `tests/unit/bootstrap/test_repair_live_integration.py` → **38 passed**。
- 対象Ruff: `./.venv/bin/ruff check src/margpa_runtime_llm/bootstrap/repair_live_integration.py tests/unit/bootstrap/test_repair_live_integration.py tests/integration/test_real_local_main_gemma_concurrent_dispatch_smoke.py` → **All checks passed**。
- Canonical Mypy: `./.venv/bin/mypy src tests` → **43 errors, 4 files**(既存Baseline維持、新規Errorなし)。
- Backend非実機Full Suite: `./.venv/bin/python -m pytest -q -m "not model_smoke"` → **2316 passed, 30 deselected**(前回と同数、Test構成の純増減なし)。
- 実機Model Smoke(対象Testのみ、正確に1回): **1 passed**(§5.3)。他の既存実機Testは指示により再実行していない。

## 7. Internal Review(2回、完全別2観点)

### Review ① — 予算・Token・Failure境界

- [OK] `_REJUDGE_TOKENS_PER_CRITERION`(100)と`LIVE_REPAIR_BUDGET.max_additional_tokens`(3600)以外のBudget/Criterion/Decoder/Context/Deadline値がいずれも無変更であることをGrep・Diffで確認した。
- [OK] 32/33 Criterion境界(3600/3700)、局所3599境界、既存Typed Failure(Context/Counter/Deadline/Cancel/Registry shutdown)の全パスが正しく機能することをUnit水準で確認した。
- [OK] Sabotage検証(旧75/2800)で新境界Test群が正しく失敗し、復元後に差分が残らないことを確認した——境界値がSourceの値に正しく追従していることの実証。
- [OK] 実機Rejudge Requestの`max_new_tokens`が実際に3200であったこと(Marker実測値)を確認し、Unit水準のArithmeticと実機実行が一致することを確認した。

### Review ② — 実機Evidence・Claim・手続き

- [OK] Preflightを対象を誤認せずRead-onlyで実施し、残存なしを確認した(Kill不要)。
- [OK] 実行は`tail`を経由せず`tee`で完全Logを保存し、pytest終了Code(0)を保持した。
- [OK] Marker実測値は、前回のTruncate Evidence(`finish_reason=LENGTH`、Completion=Plan上限一致)とは明確に異なる形状(`finish_reason=STOP`、Completion<Plan上限)であり、Claim(「真に成立した」)と実測値が整合している。
- [OK] Raw Content全文はDocsへ記載していない(文字数・SHA-512・`criterion_id`出現数のみ)。
- [自己指摘] Gemma Identity・Presented Content(具体的な文字列)は今回のPrint対象に含めておらず、Hard Assert通過という事実から確定させた。これは実測値そのものの欠落ではなく、Test成功時にはAssertion自体が確定的な証拠となるため実害はないと判断したが、Handoffが明示的に列挙した転記対象である以上、この限定を正直に記載した(§5.3)。
- [OK] 成功したことを理由に、追加の実機再実行・Criterion拡張・他の実機Test再実行など、指示にない行動は取っていない。

## 8. Open Findings／True Stop

Open Findingのまま(True Stopではない、Codex Controller判断待ち):

1. **再現性**: 今回1回の成功が、常に(あるいは高確率で)再現するかは、追加試行を行っていないため未確認(禁止事項により今回は確認していない)。
2. **Gemma Identity/Presented Contentの文字列自体**: 今回のObservability Print対象に含めておらず、Hard Assert通過という事実からの確定に留まる(§5.3、§7 Review②自己指摘)。
3. **Selene**: 未解決のまま(前回Returnと同じ、今回変更なし)。
4. **Mypy 43 errors/4 files**: 既存Baseline、今回のScope外。

## 9. Action Inventory

**実行した**: `_REJUDGE_TOKENS_PER_CRITERION`(75→100)・`LIVE_REPAIR_BUDGET.max_additional_tokens`(2800→3600)の変更、関連Source Comment訂正、Unit Test群の全面書換(§3全項目)、旧75/2800へのSabotage検証と復元確認、Test-only Observabilityへの`criterion_id`出現数Count追加、Preflight(Read-only)、実機試験の正確に1回の実行(`tee`による完全Log保存、pytest終了Code保持)、Log/Marker実測値のReturnへの転記、対象Unit・Ruff・Canonical Mypy・非実機Full Suiteの実行、本Return・Recovery新規File作成。

**実行しなかった**: 実機試験の反復。追加のBudget拡大・Criterion削減・Prompt/Schema/Decoder修正(成功したため元々不要だったが、念のため一切行っていないことを明記)。Selene・JSON Retry・Batching・Frontend・Phase 9-2/9-3・Closureへの着手。Git Add/Commit/Push等の変更操作。Current Registry/Phase Indexの編集。

**Temporary Artifact／Active Process／Model Load**: 実機Trial完了後、Post-run Read-only確認で残存Process・Port Listenともになし。完全Log File(`/private/tmp/phase9_gemma32_claude_budget3600_capture_20260905091431.log`)はTask専用の一時Fileとして保持している(削除していない)。

## 10. Exact Next Action for Codex Controller

1. §2実装境界(2値変更のみ、他は無変更)を確認する。
2. §3 Fixture/Unit全6項目とSabotage検証結果を確認する。
3. §4実機Evidence(Preflight結果、`tee`による完全Log保存、Marker実測値、特にGemma Identity/Presented Contentの文字列自体が今回未転記であるという限定)を確認する。
4. 今回の成功をもって「実32 Criterion Rejudge」項目の成立と判断するか、再現性確認のための追加試行(あるとすれば、User判断による新規Handoffが必要)を検討するか、あるいは他の対応を取るかを、Userとともに判断する。

本Returnの提出をもって停止する。Phase Closure、次Phaseへの着手、追加のGit操作、追加の実機試行は行わない。Codex Controller Independent Reviewを待つ。
