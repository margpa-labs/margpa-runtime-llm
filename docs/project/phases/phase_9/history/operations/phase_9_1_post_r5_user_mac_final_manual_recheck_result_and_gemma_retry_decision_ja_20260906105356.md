# Phase 9-1 — Post-R5 User Mac最終実画面Recheck結果とGemma Retry判断

```yaml
document_id: phase_9_1_post_r5_user_mac_final_manual_recheck_result_and_gemma_retry_decision_20260906105356
document_type: user_manual_test_result_and_controller_disposition
document_state: phase_9_1_not_closed_rework_required
phase: phase_9
program: phase_9_1
tester: user_nazuna_research
controller: codex
language: ja
recorded_at: 2026-09-06 10:53:56 JST
source_checklist: phase_9_1_post_r5_user_mac_final_manual_recheck_checklist_ja_20260906003155.md
append_only: true
```

## 1. 最大Claim

`P9_1_COMPONENT_INDEPENDENCE_VISIBLE_BUT_GEMMA_PRODUCTION_JSON_RELIABILITY_NOT_ESTABLISHED`

Phase 9-1はClosureしない。

Main Governance OFFでもGemma Judgeが独立実行できる経路、Qwen3Guard単独経路、OFF／Unloadは実画面で成立した。一方、Gemmaは同一実画面系列で一度正常完了した後も`malformed_output`を再発し、Judge起点RepairとMain Governance起点Repairを成立させられなかった。

## 2. 結果一覧

| Test | 判定 | 根拠 |
|---|---|---|
| Fresh Runtime | PASS | Main Active、Gemma／GuardはConfigured・Active none、全Mode OFF、Failureなし |
| A: Gemma単独OBSERVE | PARTIAL | Main OFFでGemma三Identity一致・32件Decode完了。ただしDeviation必須というManual Oracleは曖昧 |
| B: Judge ENFORCE＋Repair | FAIL | 初回Judgeが`malformed_output`で失敗し、Repairへ到達しない |
| C: Main Governance ENFORCE起点 | FAIL | OFF→ENFORCE操作とMain Evidenceは成立したが、Gemmaが`malformed_output`で失敗 |
| D: Guard単独OBSERVE | PASS | Match 1、Action 0、Qwen3Guard Active |
| D: Guard単独ENFORCE | PASS | Match 1、Action 1、安全な拒否、Qwen3Guard Active |
| OFF／Unload | PASS | Judge／GuardともCurrent未設定、Configured保持・Active none |

GuardとOFF／Unloadは修復後の既存実績を再確認できた。Gemma修復中は同じ確認を反復しない。

## 3. Test A — 独立実行は成立、意味判定Oracleは訂正

Request ID: `26613948-71ad-4edf-8e53-03a419a8dee2`

```text
execution_state: completed
recommendation: accept
confidence: 1.00
configured/active/executed: judge.gemma-4-e2b-it-q4-0
frozen: main=off, guard=off, judge=observe, repair=off, recording=full
selected=32, evaluated=32, passed=32, deviated=0, unknown=0, not_applicable=0, deferred=77
presentation: observed_candidate
```

この結果は次を実証する。

- Main Governance OFFでもGemma Judgeを独立実行できる。
- Semantic Snapshot、Provider Load、32件Batch、Strict Decode、Evidence保存まで一度は完走する。
- Component完全疎結合の実画面経路は成立している。

ただし、最初にUserが`765`を会話上の事実として置き、次のUser入力で明示的に`000`と回答させる試験は、過去Dialogueとの整合と現在User指示への追従が競合する。Citation Evidenceを与えていないため、Deviation必須をPASS条件にしたChecklistは曖昧だった。

したがって`accept 1.00`は品質上の要観察ではあるが、本結果だけでGemmaの意味評価バグとは断定しない。今後のDeviation／Repair Oracleは、Fixtureまたは明示的な`evidence_context`を正本とする。

## 4. Test B — Gemma初回Judgeの実障害

Request ID: `341b6a03-5314-4679-9041-1451ce4a728b`

```text
execution_state: failed
failure_reason: malformed_output
configured/active/executed: judge.gemma-4-e2b-it-q4-0
frozen: main=off, guard=off, judge=enforce, repair=enforce, recording=full
selected=32, evaluated=0, unknown=32, deferred=77
presentation: safe_fallback
```

Provider LoadやMain Governance結合のFailureではない。同じRuntime内でTest Aが完了した後、GemmaのStructured OutputがStrict Decodeを通過できず失敗した。RepairはJudge結果が確定しなかったため未実行であり、Judge→Repair→Rejudge成立を主張できない。

TurnとJudge Evidenceの保存自体は正常だった。

## 5. Test C — Main Governance起点Repairは未確認

Request ID: `7b841814-9185-4c9f-8341-6a7279b796c3`

```text
main_model.pre: selected=109, deviation=1, deferred=109
main_model.post: selected=109, pass=0, deviation=0, deferred=77
judge execution_state: failed
judge failure_reason: malformed_output
configured/active/executed: judge.gemma-4-e2b-it-q4-0
frozen: main=enforce, guard=off, judge=enforce, repair=off, recording=off
selected=32, evaluated=0, unknown=32, deferred=77
presentation: safe_fallback
```

Main GovernanceをObserve経由なしでOFFから直接ENFORCEへ変更できた点はPASS。Main Evidenceも表示された。

ただしGemma Judgeが失敗したため、Main Governance起点のRepair要求、Repair改善、Rejudge、採用およびPresented Finalは確認不能。現Phase 9-1の意味評価層はJudge結果を使うため、Gemmaが安定しない限りこの実画面Golden Pathは受理できない。

本TurnはRecording OFFだった。ChecklistのFULLと不一致だが、これはEvidence未保存の説明であり、`malformed_output`の原因とは扱わない。

## 6. GuardとUnload

Qwen3Guard単独OBSERVEは`guardrail.input`がMatch 1／Action 0、単独ENFORCEはMatch 1／Action 1と安全な拒否で成立した。Main Governance／Judge／Repairとの結合を必要としない。

全Mode OFF後はCurrent Judge／Guardが未設定、Gemma／Qwen3GuardがConfiguredを保持したままActive noneへ収束し、通常Chatも成立した。

これらは現在のBlockerではない。Gemmaが修復されるまで再試験しない。

## 7. Terminal表示の解釈

次の表示はGemma Load時のllama.cpp KV Cache／SWA構成情報であり、今回の`malformed_output`を直接示すError、Tracebackまたは原因Evidenceではない。

```text
llama_kv_cache_iswa: using full-size SWA cache
llama_kv_cache: the V embeddings have different sizes across layers and FA is not enabled - padding V cache to 512
```

本結果ではServer Crash、Native Decode Error、Timeout、Unavailableは観測されていない。

## 8. 現時点で言える原因範囲

確定している直接原因は、Gemmaが生成したStructured OutputをStrict Decoderが受理できなかったことまでである。今回の保存Evidenceだけでは次を区別できない。

- Token上限到達による切断JSON
- STOP完了だが括弧等が壊れた非Truncate JSON
- 複数Object、予期しないField、Criterion ID不整合等のProtocol違反
- Batch固有Prompt／Criteria集合による再現

Compact Schemaは過去に確認した特定のMalformed経路を解消したが、任意の実画面PromptでJSON完全性を保証するものではなかった。Gemmaは同じModelでもDialogue、Criteria Batch、Prompt形状が変われば別の決定的出力を生成するため、`seed=0`だけでは全入力のJSON妥当性を保証できない。

## 9. 保存Judge Evidenceで新たに確認した診断上の欠陥

Test A／Bの保存Fileを直接確認したところ、実Batch診断に必要な値が正確に残っていない。

- 両Runの`prompt_digest_sha512`が同一。実Promptではなく説明用PlaceholderのDigestである。
- `call_count=1`固定。実際の最大4 Batchを表現していない。
- `token_usage=0`。Batchの実Completion Tokenを保持していない。
- `seed_pinned=false / seed=unpinned`。Gemma Compositionは実際には`seed=0`を注入するため不整合。
- `config_digest_sha512`が汎用Single-call設定由来で、GemmaのBatch／Sampling契約を正確に表さない。
- `failure_reason`は`malformed_output`へ縮約され、Batch番号、`finish_reason`、Raw長／Digest、Strict Decode理由がない。

このため、追加の同一UI試験を先に繰り返しても原因分離能力は上がらない。先にProduction Batch単位のObservabilityとEvidence正確性を修復する。

## 10. Retry判断

Provider-neutralな有界Structured Output Retryを、次Reworkで実装・比較する。これは根本修復の代替ではなく、非Truncate型の間欠的Malformedに対するMVP用Containmentである。

条件は次とする。

- Shared EngineはProvider名を持たない。
- 全ProviderのDefaultはOFF。Gemmaだけを最初の適用候補とする。
- 最大Retryは1回、失敗したBatchだけを対象とする。
- `malformed_output`のうち認可された非Truncate分類だけをRetryする。
- LENGTH、Timeout、Unavailable、Cancel、Budget不足はRetryしない。
- Provider、Candidate、Criteria、Evidence、Mode、Deadline、Cancellationを変えない。
- Strict Decoderの緩和、壊れたJSONの補修、部分採用は行わない。
- 初回とRetryを別Attemptとして記録する。
- 同一Prompt／同一Seedで同一Raw Digestを再生成する場合、Blind Retryは不採用とする。
- 必要なら二回目だけ「完全なJSON Objectを再出力する」Provider局所Prompt Strategyを比較するが、Seed変更と同時に混ぜない。
- 成功率だけでなくLatency、Token、Cancellation、Evidence整合を採否条件にする。

将来のより強い根本対策はGrammar／JSON Schema等によるConstrained Decodingである。ただし現在のGeneration ContractからBackendへ配線されていないため、今回ReworkではEvidenceに基づく適合性調査までとし、無断でInference Core全体を拡張しない。

## 11. 次Action

1. 追加User実画面試験は行わず、Serverを停止する。
2. Production Batch単位Observabilityと保存Evidenceの不整合を先に修復する。
3. 同じProduction CompositionでMalformedの具体形を一回捕捉する。
4. 局所原因を修復し、Provider-neutral有界RetryをOFF／ON比較する。
5. その後、Gemma A／B／CだけをUser実画面で再確認する。
6. Guard、OFF／Unload、Selene、RAG、Web、Dev Agentは再確認対象から外す。

## 12. 2026-09-06 User作戦会議による最終訂正

§10のRetry案は採用しない。

- 同一Prompt／同一`seed=0`のRetryは同じ出力を再現するため無意味。
- Seedを変更するRetryは成功確率を上げる可能性しかなく、Judgeの不安定性自体を解消しない。
- Judge限定Constrained DecodingでJSON崩れを構造的に防げるなら、JSON Retryを追加する理由がない。
- Provider-neutral Retry案は将来の別用途に使える予約知識として残すが、今回のGemma修復では実装・有効化しない。

次Actionは、Judge限定Constrained Decoding、Prior Dialogue投影、Evidence正確化である。実装対象は初回JudgeとRepair後のRejudgeだけとし、Main通常回答、Repair Candidate生成、Guardその他の生成経路へ影響させない。
