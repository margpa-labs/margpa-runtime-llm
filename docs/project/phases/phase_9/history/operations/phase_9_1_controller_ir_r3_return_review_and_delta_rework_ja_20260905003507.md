# Phase 9-1 — IR-R3 Return独立レビュー・残差Rework

```yaml
document_id: phase_9_1_controller_ir_r3_return_review_and_delta_rework_20260905003507
document_type: controller_independent_review_and_delta_rework
document_state: changes_required
recorded_at: 2026-09-05 00:35:07 JST
language: ja
reviewer_role: codex_controller
maximum_claim: P9_1_REWORK_INCOMPLETE_FOR_CONTROLLER_REVIEW
phase_9_1_closure: false
real_model_action: none
source_test_mutation: none
git_mutation: none
append_only: true
```

対象：[00:23 Exact Return](../../handoffs/phase_9_claude_p9_1_controller_ir_r3_delta_rework_exact_return_ja_20260905002304.md)。比較基準は[前回Review](phase_9_1_controller_p1_p2_p3_return_review_and_delta_rework_ja_20260904235434.md)。既受理部分の再実装は不要。

## 1. 判定と受理範囲

**CHANGES REQUIRED／INCOMPLETE。修正は進んでいるが、IR-R3-01の全面完了は受理しない。通常32件・Gemma正常利用・Selene延期条件の未成立は維持する。**

| 対象 | 独立確認・扱い |
|---|---|
| Counter例外／計画後Deadline再確認 | 例外の外部流出と、計画が戻った時点で期限切れなのにRejudgeする問題は改善。ただし待機・Cancelは§2の残件 |
| Token見積り150→75 | 合成JSONを実Tokenizerで計数した限定的根拠として受理。通常件数の実推論成立ではない（§3） |
| Main起点の同一通常Turn保存 | Repair=offの成功／失敗2 Testを受理。Controllerがメモリ内でobserveへ切り替えた2経路もPASS |
| Gemma Smokeの誤Skip | 実Smoke関数へFixtureの`llama_decode returned -3`を注入し、今回は期待通りTest失敗。前回の誤Skipは解消 |
| 新規Mypy4件 | 同一Commandで43 errors／4 filesへ戻ったことを確認。既存43件を無断修復する指示ではない |

## 2. IR-R4-01／P1 — Plannerの待機とCancelが残る

対象：`src/margpa_runtime_llm/bootstrap/repair_live_integration.py:218,656,695`。

`count_chat_prompt_tokens()`は依然として同期呼出しで、Plannerを囲む時間・Cancel待機境界がない。例外捕捉と処理後の経過時間確認だけでは、計数処理が戻らない場合を止められない。

- 既存`_UsageScriptedRepairService`を継承し、Context=8192、CounterがEvent解放まで待つFixtureで再現。全体Budget=20msでも120ms後にExecutorは未返却。ControllerがEventを解放した後、約123msで`repair_budget_exceeded_before_rejudge`になった。Cancellation有無の両方で同じ。Rejudge自体は呼ばれず、この点の改善は確認できた。
- Counter内で渡したCancellationTokenをcancelしてから10を返すFixtureでは、`:repair`に加え`:rejudge`のサービス呼出しにも到達し、その後`cancelled_by_main_priority`になった。実Native推論やToken消費を実証したProbeではないが、Executorの呼出し前停止境界が欠けていることは再現した。
- Probeはメモリ内のTest Doubleのみ。待機Eventを必ず解放し、Threadをjoinして残存なし。Source／Testのディスク変更なし。

残差修正：既存の追跡Worker／Lease方式を確認し、計画待機を残り全体Deadline・Cancelで有界化する。Python Threadの強制終了や、計数が続くModelの先行Unload／解放をしない。計画開始前・計画後／推論直前のCancel・期限切れではRejudgeサービス呼出し0を保証する。例外／Timeout／Cancelを成功Planや単なるToken不足へ混同しない。元の計画統一と全Frozen Criterion保持は維持する。

## 3. IR-R4-02／P2 — 「26件成立」の範囲を訂正する

`tests/unit/bootstrap/test_repair_live_integration.py:1344`は`_plan_rejudge()`を呼び、`max_new_tokens==1950`を確認するだけで、生成・Decode・改善採用・保存を実行していない。したがって成立しているのは**Candidate使用量5 Tokenという仮定での26件Plan受理**であり、26件のRepair→Rejudge成立ではない。

[再校正Snapshot](../../../../shared/history/unresolved_work/phase_9_1_rejudge_token_calibration_and_32_criterion_infeasibility_snapshot_ja_20260905000817.md)の1771／1901 Tokenは、実ARGD/DAGD IDを含む合成JSONをQwenの`count_chat_prompt_tokens()`で計数した値。実生成32件のcompletion usageでも、Gemma／Seleneを含む全Providerの最悪値でもない。75は暫定見積りとして扱う。

- `5+26×75=1955`は現2000予算内。一方、Candidateが上限400 Tokenを使う場合は`400+26×75=2350`で入らず、この算式で入るのは21件まで。
- 通常上限32件は`32×75=2400`のため現Planでは拒否される。ただし、2400を全ての実出力に必須の情報量と証明したわけではない。
- 3000 Token案はCandidate400＋暫定Rejudge2400を収める算式上の案であり、Context／全体時間／実モデル成立の保証ではない。今回も実装許可に読み替えない。
- Batchingだけを導入しても総Token予算2000が自動的に増えるわけではなく、Call上限との整合も必要。単純な代替解決として記載しない。

新規の短い訂正で測定・Plan・実行を分ける。過去文書は上書きしない。通常32件未成立の正直な報告自体は受理する。小さいFixtureやさらに小さい係数で通常成立を代用せず、予算方針変更が必要なら最小案と確認事項を提示して判断を待つ。

## 4. Gemma／保存経路の残件

[Gemma局所試行記録](../../../../shared/history/unresolved_work/phase_9_1_gemma_local_prompt_repair_attempt_bounded_negative_result_snapshot_ja_20260905002008.md)の絶対Pathから診断Scriptと生Logを読んだ。Scriptは実Templateを使用し、修正後Promptに第5規則が含まれることも確認。誤答側生出力は依然`evidence_refs`の閉じ角括弧が欠け、`finish_reason=stop`、completion_tokens=88。狭いPrompt修正で未解決だったという否定的結果を受理する。Model限界やBackend無罪の断定には使わない。

Smokeの新OracleはFAILED＋`malformed_output:`という**失敗カテゴリ**を識別するもので、閉じ括弧欠落という個別原因の機械的特定ではない。現在のSkipをGemma正常利用PASSへ数えない。

Main起点は今回Controllerのobserve変種も成功したため、追加のProductionバグは指摘しない。次回は既存2 Testをoff／observeでパラメータ化する程度で保持し、Helperや長い説明を複製しない。

## 5. 検証と次の差分

- Focused Pytest：Repair、通常保存、Judge Hook、Dispatch、Decoder、Selene、Gemma Smoke Oracleの7 Fileで**165 passed／1 deselected（6.08s）**。除外は実モデルSmoke。Main=ENFORCE／Repair=observeの2 ProbeもPASS。
- 対象4 File Ruff：PASS。`./.venv/bin/mypy src tests`：**43 errors／4 files／571 files checked**。Backend全体2311 PASSはClaude報告を保持し、Controllerは全体再実行していない。
- Controllerによる実Model Load／Inference、Network、Browser、User永続データ操作、Git変更、実装修正は0。Review文書新規作成とIndex追記のみ。

次の順序：①IR-R4-01の残差修復とEventベースの回帰Test → ②IR-R4-02のClaim訂正・off/observe保存Test保持 → ③Gemmaの別仮説を先に明示した局所修復。既に無効だった注意文の同条件反復はしない。実機は許可済みMain＋Gemma、既存Context／資源上限内、最初の別仮説は最大2試行で判定。正常化した場合のみ既承認のOBSERVE／ENFORCE・同条件Repair→Rejudge→採用・Main Governance経路の確認へ進む。

Budget／Call上限の無断拡大、Criterion削減、Decoder厳密性緩和、Native更新、Download、新Resource Gate、Selene追加試行、Phase 9-2／9-3は禁止。実機未成立ならINCOMPLETEで止める。異なる観点2回のInternal Review後、新規PathのExact Return／Recoveryを必ず作って停止。旧Handoffの復旧鑑識や指示文のDocs化は不要。
