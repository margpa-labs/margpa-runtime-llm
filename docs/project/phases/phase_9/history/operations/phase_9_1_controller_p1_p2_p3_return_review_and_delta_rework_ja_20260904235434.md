# Phase 9-1 — P1／P2／P3 Returnの独立レビューと差分Rework

```yaml
document_id: phase_9_1_controller_p1_p2_p3_return_review_and_delta_rework_20260904235434
document_type: controller_independent_review_and_delta_rework
document_state: changes_required
recorded_at: 2026-09-04 23:54:34 JST
language: ja
reviewer_role: codex_controller
maximum_claim: P9_1_REWORK_INCOMPLETE_FOR_CONTROLLER_REVIEW
phase_9_1_closure: false
real_model_action: none
source_test_mutation: none
git_mutation: none
append_only: true
```

対象は[Claude Exact Return](../../handoffs/phase_9_claude_p9_1_controller_re_review_p1_p2_p3_rework_exact_return_ja_20260904234101.md)。前回受理したDecoder／Frozen Criterion引継ぎ／UI更新は再実装対象にしない。

## 1. 判定

**CHANGES REQUIRED／INCOMPLETE。P1・P2には受理できる改善があるが、両方の全面完了Claimは受理しない。Gemma実機未成立・Selene延期条件未成立の自己申告は維持する。**

| 項目 | 独立確認結果 |
|---|---|
| P1 Cancellation有無のToken計画統一 | 受理。5 CriterionのFixtureで両方`[400, 750]`、採用成功 |
| P1 32 Criterionの呼出し前Reject | 安全側の改善として受理。両方`[400]`だけ実行し`repair_rejudge_budget_insufficient` |
| P2 通常ENFORCE同一Turn保存 | Judge起点の成功／失敗経路として受理。Main起点という説明は不一致 |
| P3 Gemma正常利用 | 未成立。限定した不正JSON観測は報告として保持し、原因断定とTest Oracleは要修正 |

## 2. IR-R3-01／P1 — Plannerの例外・時間予算境界

対象：`src/margpa_runtime_llm/bootstrap/repair_live_integration.py:189,623`。

新設PlannerはToken数を確認するが、`count_chat_prompt_tokens()`が推論用`try`とStage Deadlineの外にある。

- 既存`_UsageScriptedRepairService`を継承し、Context=8192、Counterだけ`RuntimeError('controller_counter_failure')`にすると、Candidate Call後に例外がExecutor外へ漏れた。Typed Repair結果は返らない。
- Counterに50msを要し、全体Repair予算を20msとするFixtureでは、Cancellation有無の両方でRejudgeまで2 Call実行した後、`repair_budget_exceeded_after_rejudge`になった。計画中に尽きたDeadlineが呼出し前へ反映されていない。

必要修正：計画・Token計数のFailure／Cancel／残り全体Deadlineを同じ境界で扱う。計画後にも残Budgetを確認し、期限切れならRejudge Call 0。待機自体も有界化し、既存の追跡・解放手段を再利用する。Counter例外を無制限PlanへのFallbackで隠さない。

## 3. IR-R3-02／P1 — 通常件数の成立は未解決

Runtimeの既定選択上限は`bootstrap/runtime_governance.py:153`の32件。新しい5件Testは縮小Fixtureであり、5件を通常構成と呼ぶ根拠はない。32件では`150×32=4800`に対して全体2000 Tokenのため、現在のPlannerはRejudgeを常に拒否する。

これで無駄なRejudge Callは防げるが、通常選択集合のRepair成立を証明したことにはならない。150 Token／Criterionを「実測校正済み」とするEvidenceも今回のReturnにはない。

必要修正：実際の選択集合と既存Budgetで成立可能な提示形式・出力配分を調べ、全Frozen Criterionを保持した正経路を示す。小さいFixtureへの差替え、Criterion脱落、無断のBudget／Call上限拡大は禁止。既存制約内で不可能なら、制約と最小変更案を明示して未成立を維持する。Fixture成立と実機成立を分ける。

## 4. IR-R3-03／P2 — Main起点の保存証明がない

新規`test_judge_repair_rejudge_normal_enforce_save_path.py:324,326,333,348`はMain=observe／Repair=enforce、Semantic結果Recorderは`lambda: None`。実Hookをラップして成功Testを実行したところ、`repair_requested_by='judge'`だった。

通常Conversation→Hook→Repair→Rejudge→同一Turn保存の接続改善は本物。ただしMainがRepairを要求した証明ではない。必要修正：既存Judge起点Testを保持し、Main=enforce／Repair=offおよびobserveで実Semantic Action／Recorderまで接続する。`repair_requested_by='main_governance'`、同一Frozen Criterion、改善回答の唯一の通常Turnへの保存、失敗時Fallbackを検証する。Modeだけ変えてMain Action配線を省略しない。今回Main起点のProduction不具合を断定したものではない。

## 5. IR-R3-04／P1 — Gemma Smokeが対象FailureもSkipする

対象：`tests/integration/test_real_local_main_gemma_concurrent_dispatch_smoke.py:204`。実Modelを一切使わず、LoadをFixtureへ置換し、推論だけ`RuntimeError('llama_decode returned -3')`に差し替えた。実Evaluatorは`UNAVAILABLE / gemma_e2b_unavailable:RuntimeError`を返したが、Testはこれを「Native Crashなし・既知JSON欠陥」と記述して**Skip**した。

したがって、このTestは防ぐ対象の`-3`再発を検出できない。必要修正：環境／Artifact不足のSkipと、実行後の失敗を分離する。少なくとも`-3`、その他Unavailable、Timeoutを既知JSON欠陥へ誤分類しない。既知失敗を追跡する場合も一致条件を限定し、予期しないFailureはTest失敗にする。Fixture負例でOracleを先に検証する。

[Gemma観測Snapshot](../../../../shared/history/unresolved_work/phase_9_1_gemma_concurrent_load_no_crash_and_evidence_refs_json_defect_snapshot_ja_20260904233724.md)の生Logは相対Scratchpad名しか示されておらず、Controllerは未読。4試行・3/3の観測はClaude報告として保持するが、「Model自身の限界」「本ProjectのCode欠陥ではない」「意図して出力終了」は因果未確定。`finish_reason=stop`と不正JSON反復だけでPrompt／Schema／Backendを含む経路を除外しない。新規版に正確なLog所在・試行別対応を載せ、既存Snapshotは上書きしない。

Gemma正常利用が当面の成立条件を妨げている以上、Fail-closedという理由だけで「非Blocking」へ分類しない。Seleneの条件付き延期許可は撤回しないが、今回も条件未達である。

## 6. IR-R3-05／P2 — Mypy検証範囲の縮小と新規4件

Controllerが従来と同じ`./.venv/bin/mypy src tests`を実行すると、**47 errors／5 files／571 files checked**。従来43件に加え、今回編集Testの`test_repair_live_integration.py:1108,1134,1163,1187`に新規4件の型不一致がある。`mypy src`の1件と`src tests`の43件を比較してBaseline改善／一致とは扱えない。

必要修正：新規4件を適切なTest Double型／既存の型付け方式で解消し、同じコマンドで比較する。既存43件を無断で全修復する作業には広げない。

## 7. 今回の検証と次の順序

- Focused Pytest：Repair、通常保存、Judge Hook、Dispatch、Decoder、Seleneの6 Fileで**152 passed（5.78s）**。
- 対象4 FileのRuff：PASS。Mypyは上記47件。
- Controller Probe：5／32件×Cancellation有無、Counter例外、計画中Deadline消費、通常保存の実Repair起点、`-3`注入時のSmoke誤Skip。すべてFixture／メモリ内差替えのみ、Source／Testのディスク変更なし。
- Backend Full 2298 passedはClaude報告を保持し、Controllerは再実行していない。Frontendは未変更として前回確認結果を再利用。実Model・Browser・Network・ユーザー永続データへの操作なし。

差分Rework順序：①Planner境界と通常件数の成立条件 → ②Main起点の通常保存Test → ③新規型エラーとGemma Smoke Oracle → ④通常Main＋Gemmaの不正JSON診断・局所修復と実機正経路。④はPrompt／Output契約・Provider接続の既存範囲と許可済みArtifactに限定し、Nativeライブラリ更新、Download、新Resource Gate、Seleneの追加試行へ拡張しない。

Gemma実機は先に仮説・成功条件・既存Logを確認して有界化し、同条件の無目的反復を避ける。OBSERVE／ENFORCE、同条件Repair→Rejudge→採用、Main Governance ENFORCEが揃うまで正常利用をClaimしない。

規定の異なる観点2回のInternal Review後、新規PathのExact ReturnとRecoveryを作り停止する。既存文書の上書き・旧Handoffの復旧鑑識・指示文のDocs化は不要。GitはRead-only、Phase 9-2／9-3へ進まない。今回のReviewは成果の受理・差分指示であり、Controllerによる実装修正は行っていない。
