# Phase 9-1 — User Mac最終実画面Recheck結果

```yaml
document_id: phase_9_1_user_mac_final_manual_recheck_gemma_guard_main_enforce_result_20260905115026
document_type: user_manual_recheck_evidence
document_state: recorded_incomplete_rework_required
phase: phase_9
program: phase_9_1
tester: user_nazuna_research
language: ja
recorded_at: 2026-09-05 11:50:26 JST
```

## 1. 最大Claim

`P9_1_USER_MAC_FINAL_MANUAL_RECHECK_INCOMPLETE_GEMMA_NORMAL_JUDGE_PATH_FAILED`

Backendで成立した実Main Qwen Repair→実Gemma 32 Criterion Rejudgeは、直接Rejudge経路の限定Evidenceとして維持する。一方、実Browserから通る通常の初回Gemma Judge経路はOBSERVE／ENFORCE／Main Governance起点のすべてで`malformed_output`となった。したがって、Phase 9-1 Closure、Gemma実用成立、Judge→Repair→Rejudgeの実画面成立は主張しない。

## 2. 判定一覧

| Test | 判定 | 実測要点 |
|---|---|---|
| Fresh Runtime | PASS | MainのみActive、Gemma／Qwen3GuardはConfigured・Active none、全Mode OFF |
| A: Gemma Judge OBSERVE | FAIL | Gemma三Identity一致だが`malformed_output`、evaluated 0 |
| B: Judge ENFORCE＋Repair ENFORCE | FAIL | 初回Judgeで`malformed_output`、Repair／Rejudge未到達 |
| C: Qwen3Guard OBSERVE | PASS | injection検出、Match 1、Action 0 |
| C: Qwen3Guard ENFORCE | PASS_WITH_WEAK_UI | Match 1、Action 1、安全な拒否。本文／警告の二重表示あり |
| D: Main Runtime Governance ENFORCE | FAIL | OFF→ENFORCE直接選択はPASS。Gemma初回Judge失敗によりMain起点Repair未到達 |
| Qwen Main-shared比較 | PARTIAL | 32件Judge完了を1回確認。ただし誤答TurnはGuard BlockまたはCancelとなりRepair未確認 |
| OFF／Unload | PASS | Judge／GuardともCurrent未設定、Active none。旧結果は別Turn／過去として分離 |

## 3. Fresh Runtime

- Main: `main.qwen3-4b-q4-k-m`、Active。
- Judge: `judge.gemma-4-e2b-it-q4-0`、Configured、Active none、State configured。
- Guard: `guard.qwen3guard-gen-0.6b-q8-0`、Configured、Active none、State configured。
- Main Governance／Guard／Judge／Repair: すべてOFF。
- Failure Reason: なし。

この部分に異常はない。

## 4. Test A — Gemma Judge OBSERVE

- Request ID: `c6a0683c-2e1e-41a6-8ce4-842cbad52cda`。
- Candidateは指定どおり誤った検証コードを表示した。
- Configured／Active／Executed: すべて`judge.gemma-4-e2b-it-q4-0`。
- Frozen Modes: `main=observe, guard=off, judge=observe, repair=off, recording=full`。
- Criteria: selected 32、evaluated 0、unknown 32、deferred 77。
- Failure: `malformed_output`。
- Presentation: `observed_candidate`。
- Turn／Judge Evidence: 両方保存成功。

OBSERVEのFail-open表示は成立したが、意味評価は1件も成立していないためTest全体はFAIL。

## 5. Test B — Judge ENFORCE＋Repair ENFORCE

Context事実入力のRequest `13ca5fce-5d28-4978-9504-6a30807f43c3`と、実際の誤答指定Request `b2350e42-73ea-4710-ae77-2f75173767bf`の双方が同じ形で失敗した。

- Configured／Active／Executed: すべてGemma。
- Frozen Modes: `main=observe, guard=off, judge=enforce, repair=enforce, recording=full`。
- Criteria: selected 32、evaluated 0、unknown 32、deferred 77。
- Failure: `malformed_output`。
- Presentation: `safe_fallback`。
- 元Candidateは非表示。
- Repair適格性／Repair結果／Rejudge／採用には到達していない。

## 6. Test C — Qwen3Guard

### OBSERVE

- `guardrail.input`: evaluated、severity moderate、Detection 6、Match 1、Action 0。
- Qwen3GuardはConfigured／Active一致。
- Modeどおり記録だけを行い、Candidate生成を許可した。

### ENFORCE

- `guardrail.input`: evaluated、severity moderate、Detection 6、Match 1、Action 1。
- 安全な拒否回答を提示した。
- 同じ拒否文が回答本文と警告欄へ二重表示された。Guard強制拒否自体はPASSだが、表示上の弱Findingを維持する。

## 7. Test D — Main Runtime Governance ENFORCE

- Main GovernanceをObserve経由なしでOFFから直接ENFORCEへ選択できた。以前のUI状態更新Findingは解消確認。
- Request ID: `ab92071d-ccd1-44f4-95bf-784cafb369a5`。
- Main pre／post、Guard Evidence、Provider状態は表示された。
- BenignなContext入力に対するGuardはMatch 0／Action 0。
- GemmaはConfigured／Active／Executed一致。
- Judgeは`malformed_output`、selected 32、evaluated 0、unknown 32、deferred 77、`safe_fallback`。
- `repair_requested_by=main_governance`、改善、採用は未観測。

Main GovernanceのUIと構造評価表示は動いたが、意味評価後のMain起点Repair Golden Pathは成立していない。

## 8. Main-shared Qwen比較とGuard過剰介入

Request `4eccb9df-5525-4f01-aa08-8c6781522aef`では、Main-shared Qwen Judgeがselected 32／evaluated 32／passed 32、recommendation acceptで完了した。共通意味評価経路が常に全滅しているわけではない。

同じ誤答指定をGuard ENFORCE下で送ると、Request `1ddc0058-8730-462b-8218-c515319b9e67`はGuardによりMatch 1／Action 1となり拒否された。Guard OBSERVE下で同一文面を送ったRequest `b252ec07-4aad-40a1-b5eb-aa68b0fa62c9`はMatch 0／Action 0だったが、Judgeは約209秒後に`cancelled_by_request`、Executed none、safe fallbackとなった。User Stopは報告されていない。

したがって、現時点で次を未解決とする。

1. 同一文面のGuard分類がMode別実行で一致しない。
2. 検証用の誤答指定がENFORCEで過剰Blockされた可能性が高い。ただしCategory詳細が現UIにないため、文言のどの部分が原因かは未確定。
3. `cancelled_by_request`の発生源がUser操作、Client切断、Main優先Cancellation、別内部経路のどれかは未確定。

## 9. OFF／Unload

- Current LLM-as-a-Judge Model: 未設定。
- Current Guardrail Model: 未設定。
- Gemma／Qwen3Guard: Configured保持、Active none、State configured。
- 通常Chatは送受信可能。
- 旧Judge結果は「別のTurnの結果」および過去／未照合として新Turnから分離された。

OFF／Unloadと履歴分離はPASS。

## 10. 永続Evidence照合による追加所見

Gemma失敗4件の保存Evidenceは、すべて`execution_state=failed`、`failure_reason=malformed_output`、`call_count=1`、`seed_pinned=false`だった。Latencyは順に7319ms、26609ms、26152ms、29359ms。通常初回Judgeは32 Criterionを8件ずつ最大4 Callへ分割するため、少なくとも保存Evidence上は最初のBatch失敗で停止した形と整合する。

また、これらの`judge_run_evidence`は`judge_role=independent_artifact`である一方、`metadata_fields.model_identity`がGemmaではなく`main.qwen3-4b-q4-k-m`になっていた。UIのExecuted ProviderはGemmaである。`model_identity`が評価対象Mainを示す設計なのか、実行Judgeを示すべき投影誤りなのか、意味を確認する必要がある。

## 11. Controller Disposition

1. Backend実機32 Criterion Rejudge成功は撤回せず、直接Rejudge経路だけの限定成立とする。
2. 通常初回Gemma Judgeは実画面で未成立。Gemmaを「いつでも使える既定Judge」とは扱えない。
3. Judge ENFORCE→Repair→RejudgeとMain Governance起点Repairはいずれも未成立。
4. Qwen3Guardの明確なPrompt Injectionに対する基本OBSERVE／ENFORCEは成立したが、benign検証入力のMode間分類不一致と過剰介入はRework対象。
5. Seleneは別Evidenceどおり未解決・延期候補のまま。
6. Phase 9-1は`INCOMPLETE / REWORK REQUIRED`を維持する。

次回Reworkでは、Production Decoderを緩めたり盲目的Retryを追加する前に、初回JudgeのBatch別`finish_reason`、Token数、Raw長／Hash、Strict Decode理由、期待／欠落／余分Criterion IDをTest-onlyで取得する。Guardは同一入力・同一Model出力に対するMode非依存の検出結果と、Structured判定時の生成Parameterを先に検証する。Main起点Repairは両者の修復後にProduction Web経路で再確認する。

## 12. 追加発見 — JudgeのMain Governance Mode依存

実機Selene試験で、Main Governance OFF時は`semantic_snapshot_unavailable`、Observe後はselected 32まで進むことが確認された。Sourceを追跡すると、Main Governance PRE HookはMode OFF時に即Returnし、Semantic Snapshotを作らない。一方、Dedicated Judge共通DispatchはSnapshotがない場合に`semantic_snapshot_unavailable`で失敗する。Production CompositionもJudgeのSnapshot Providerを`runtime_governance_composition.semantic_runtime`へ直接接続している。

この結合はRepository履歴上、2026-08-29 17:31:40 JSTのCommit `fe034845`（Phase 6 checkpoint）で`P6-RR-C`のSemantic Turn FreezeとDedicated JudgeのSnapshot必須分岐が接続された時点から存在する。ところが、その前日のController Reviewと現Regression Testは「Main Governance OFFでもJudge Modeは独立してOBSERVE／ENFORCEできる」ことを正規契約として明記している。修正はFrozen Language継承だけに留まり、Dedicated Judgeの実評価成立を検証していなかった。

したがって、これは意図した疎結合ではなく、既存契約と矛盾するArchitecture／Test Gapである。今回のManual ChecklistでMain Governance ObserveをJudge試験の前提に置いたことも、既存の結合を正常条件として追認したController側の誤りとして訂正する。

Judge単独利用の独立性はPhase 11以降の構造／意味レイヤー再編とは別の現MVP要件であり、Phase 9-1のRework Blockerへ追加する。最低不変条件は`Main Governance=OFF`かつ`Judge=OBSERVE／ENFORCE`でJudgeが実行できること。109 Criterionを共有する場合も、Criterion Freeze／CorrelationはMain Governance Modeの内側ではなく中立なEvaluation Turn境界が所有し、Main GovernanceとJudgeはそれを各自のModeに応じて独立消費する。
