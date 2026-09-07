# Phase 9-1 — Gemma Production Structured Output Observability・根本原因・有界Retry Rework Exact Handoff

```yaml
document_id: phase_9_controller_gemma_production_structured_output_observability_and_bounded_retry_rework_exact_handoff_20260906105356
document_type: exact_rework_handoff
document_state: ready_for_claude_implementation
phase: phase_9
program: phase_9_1
controller: codex
implementer: claude_code_fresh_or_current_session
language: ja
created_at: 2026-09-06 10:53:56 JST
maximum_authorized_claim: P9_1_GEMMA_PRODUCTION_JSON_RELIABILITY_REWORK_READY_FOR_USER_RECHECK
phase_9_1_closure_authorized: false
git_write_authorized: false
append_only_docs: true
```

## 1. 目的

User実画面で再発したGemma Judgeの`malformed_output`を、推測ではなくProduction Batch単位Evidenceで分類し、局所原因を修復する。加えて、予約済みのProvider-neutral有界Structured Output Retryを実装・比較し、採否をEvidenceで決める。

Guard、Unload、Component Independenceそのものは今回のUser実画面で成立した。対象をGemma Structured Output経路へ限定する。

## 2. 必ず読む正本

1. `docs/project/phases/phase_9/history/operations/phase_9_1_post_r5_user_mac_final_manual_recheck_result_and_gemma_retry_decision_ja_20260906105356.md`
2. `docs/project/phases/phase_9/handoffs/phase_9_claude_component_independence_r5_final_micro_rework_exact_return_ja_20260906002247.md`
3. `docs/project/phases/phase_9/history/operations/phase_9_1_component_independence_r5_controller_acceptance_ja_20260906002712.md`
4. `docs/project/shared/history/planned_work/gemma_code_toggle_bounded_malformed_json_retry_experiment_reservation_ja_20260905200925.md`
5. `docs/project/shared/history/planned_work/provider_neutral_bounded_structured_output_retry_policy_addendum_ja_20260905201130.md`

Docsだけを盲信せず、現在Source、Test、User実Evidenceの順で事実を照合する。

## 3. User実Evidence

### A: 独立OBSERVE

- Request: `26613948-71ad-4edf-8e53-03a419a8dee2`
- Main OFFでGemma三Identity一致。
- 32 evaluated／32 passed、deferred 77、`completed`。
- Component Independenceと少なくとも一つのStrict Decode成功を実証。
- `765`宣言後に現在Userが`000`回答を命じる入力は意味Oracleとして曖昧。Deviation必須にはしない。

### B: Judge ENFORCE＋Repair ENFORCE

- Request: `341b6a03-5314-4679-9041-1451ce4a728b`
- Main OFF、Guard OFF、Gemma三Identity一致。
- `malformed_output`、32 unknown、safe fallback。
- 初回Judge失敗のためRepair未到達。

### C: Main Governance ENFORCE起点

- Request: `7b841814-9185-4c9f-8341-6a7279b796c3`
- Main ENFORCE、Guard OFF、Judge Gemma ENFORCE、Repair OFF。
- Main Evidenceは表示。Gemmaは`malformed_output`、safe fallback。
- RecordingがOFFだった点はChecklistとの差分だがMalformed原因とは扱わない。

## 4. Confirmed Controller Findings

現在の保存Judge EvidenceはDedicated batched Judgeの診断に不十分かつ一部不正確である。

1. 実Promptではなく`prompt_description`のDigestを保存し、A／Bで同じDigestになる。
2. `call_count=1`固定で、最大4 Batchの実Callsを表現しない。
3. `token_usage=0`で、`SemanticEvaluationBudget.completion_tokens`を失う。
4. GemmaにはComposition Rootで`seed=0`を注入するが、Evidenceは`seed_pinned=false`を記録する。
5. Config Digestが汎用Single-callの200 Token設定由来で、Gemmaの実Batch／Sampling設定を表さない。
6. `malformed_output`の内部理由、Batch番号、finish reason、Raw長／Digestが保存されない。

これらは今回のRework対象である。Userへ追加のBlind UI Trialを要求してはならない。

## 5. WU-01 — Production Batch Attempt Evidenceを正確にする

Shared EvaluatorへProvider-neutralなAttempt Evidenceを追加する。名称にGemma／Selene等を埋め込まない。

最低限、Batch／Attemptごとに次を保持する。

- `batch_index`
- `retry_attempt`（初回0、Retry 1）
- Expected Criterion件数とID集合Digest
- 実Prompt Digest。Raw Prompt全文は通常保存しない。
- 実Sampling Parameters（少なくともseed、temperature、top_k、max_new_tokens）
- `finish_reason`
- prompt／completion Token数
- 生成時間
- Raw Content byte lengthとSHA-512。Raw全文は通常保存しない。
- Strict Decode stateと、`JudgeDecodeError.reason`の安全なTyped分類
- Retryを行わなかった／行った理由

Run集約Evidenceの`call_count`、`token_usage`、Prompt／Config Digest、seed情報を実値から生成する。Main-shared、Built-in、DedicatedのIdentity意味を壊さない。

UIへ大量情報を追加する作業ではない。既存の安全な要約表示は維持し、保存EvidenceまたはTest logで診断可能にする。

必須Test:

- 4 Batch成功時に`call_count=4`、総Tokenが一致。
- Batch 3 Decode失敗時にBatch 3／Attempt 0の理由が残る。
- Gemma sampling overrideがEvidenceへ`seed=0`として残る。
- Main-shared／Selene等の未固定samplingを虚偽の固定値にしない。
- Recording OFFはRecorder Call 0という既存契約を維持する。

## 6. WU-02 — Malformedの具体原因を一回で分類する

Production Web Compositionと同じContext生成、Semantic Snapshot、Provider Selection、Batch Planner、Strict Decoderを通るTest Harnessを使う。`SeleneSemanticEvaluator`という既存Class名に引きずられず、実体がProvider-neutral shared engineであることを維持する。

User Test B相当を再現し、各Batchについて次を区別する。

- `finish_reason=LENGTH`のTruncation
- `finish_reason=STOP`だが不完全JSON
- 複数Objectの競合
- Unexpected Field／Value
- Criterion ID missing／extra／duplicate
- その他のStrict Protocol違反

原因を「Gemmaの癖」「Metal」「Memory」「Token不足」等へEvidenceなしに一般化しない。KV Cache／SWA初期化Logは原因Evidenceとして扱わない。

局所Prompt／Schema／Batch組立に原因がある場合だけ、最小修復を行う。Strict Decoder緩和、Brace補完、部分JSON採用、先頭Object優先等による成功化は禁止する。

## 7. WU-03 — Provider-neutral有界Retry

共有機構は次のような役割名を使う。

```text
StructuredOutputRetryPolicy
retry_policy
retry_attempt
retryable_failure
retry_prompt_strategy
```

Gemma固有設定はComposition／Adapter／Registry側から注入する。Shared Evaluator内でProvider IDを比較するHardcodeは禁止する。

契約:

- 全Provider Default OFF。
- 最大Retry 1回。
- 失敗したBatchだけをRetryする。
- Retry可能なのは、WU-02で分類した非Truncate型のStrict Malformedだけ。
- LENGTH、Timeout、Unavailable、Busy枯渇、Cancel、Deadline、Budget／Context不足はRetryしない。
- Provider、Artifact、Candidate、Criteria、Evidence、Mode、Request相関を維持する。
- Whole-stage DeadlineとCancellationを再確認し、残Budgetがない場合はCall 0。
- 初回成功Batchを再実行しない。
- 初回失敗とRetry失敗を別AttemptとしてEvidenceへ残す。
- Retry失敗時は最終的に従来どおりTyped `malformed_output`へFail closedする。
- OFF時は追加Call 0をTestする。

`max_calls`とRetry Callを曖昧に混ぜない。通常Batch Call Budgetと、認可されたRetry 1回を明示的に計画・集計し、上限超過を隠さない。

## 8. WU-04 — Retry Strategy比較と条件付き採用

次の二方式を同時変更せず順番に比較する。

1. 同一Prompt／同一SeedのExact Retry。
2. 二回目だけ完全な単一JSON再出力を要求するProvider局所Prompt Strategy。

Exact RetryでRaw Digestが一致して再失敗する場合、Blind Retryは無効と判定する。そこでSeedまで同時変更して結果を混同しない。

Provider局所Prompt Strategyは、Candidate、Evidence、Criteria、判定対象を変えてはならない。完全なJSON再出力だけを要求する。

Gemma policyを実運用でONにしてよいのは次を全て満たす場合だけ。

- Retry OFFよりMalformed成功率が明確に改善。
- Timeout／Cancel／Deadline契約を壊さない。
- 追加Latency／TokenがMVPとして許容可能。
- Strict DecodeとCount保存則を維持。
- Attempt Evidenceが正確。

成立しなければ共通機構とGemma policyのDefaultをOFFのまま残し、無理に成功Claimを作らない。

## 9. WU-05 — 意味評価Oracleの分離

User実画面Test Aの「過去に765と宣言し、現在は000と答えろ」は、現在User指示とPrior Dialogueが競合するため、Deviation必須Oracleとして使わない。

意味評価／RepairのHard Oracleには、Fixtureまたは明示的`evidence_context`へ正解を置き、Candidateだけを矛盾させる。次を別々に証明する。

- JSON／Protocolとして完了する。
- Trusted Evidenceへの明白な矛盾をDeviationとして扱う。
- Judge起点Repairが改善・Rejudge・採用へ進む。
- Main Governance起点RepairがRepair Mode OFFでも改善・採用へ進む。

Execution安定性と意味判定品質を一つのAssertへ混ぜない。

## 10. Constrained Decodingの扱い

Model Registryは`json_schema`をOptional Capabilityとして掲げるが、現在の`GenerationParameters`とmanual `Llama.create_completion()`経路にはGrammar／JSON Schema指定が配線されていない。

Grammar／JSON SchemaによるConstrained Decodingは、Retryより強い将来の根本対策候補である。ただしInference Core横断変更になり得る。今回は次だけを報告する。

- 現Backend Versionで利用可能なAPI
- 動的Criterion IDを含むSchemaを安全に表現できるか
- Main通常Generationへ影響させずRole局所注入できるか
- おおよその実装・Test工数とRisk

Codex／Userの追加承認なしに本Reworkへ実装しない。

## 11. Verification

順序は固定する。

1. Focused Unit／Integration
2. Failure、Cancel、Deadline、OFF Call 0のSabotage-regression
3. 非Model Full Suite
4. Ruff
5. Canonical Mypyを既存Baselineと比較
6. 実Model Trial

実Model Trialは最大3回。ただし目的のない反復は禁止する。

- Trial 1: Instrumented Retry OFFで既知Production相当Caseを一回。
- Trial 2: Trial 1がRetry対象Malformedだった場合のみ、認可Strategy ONで一回。
- Trial 3: Exact Retryが同一Digest再失敗した場合に限り、Provider局所再出力Strategyを一回。Trial 2で既にこのStrategyを使ったなら実施しない。

各Trial前後にMARGPA Server、pytest、Python／llama残存ProcessとPort 8000を確認する。残存がなければKill操作をしない。

## 12. 禁止事項

- Selene実機試行
- Guard再実装／再実機試行
- OFF／Unload、RAG、Web、Dev Agent再試験
- Phase 9-2／9-3、Phase 10作業
- Decoder緩和、JSON補修、部分採用
- Context、Criterion上限、Repair Budget、Samplingの無断変更
- Git add／commit／push／stash／reset
- 既存Handoff／Return／Historyの上書き
- Phase Index／Registry Docsの直接編集
- 成立していないPhase 9-1 Complete／Closure Claim

## 13. Exact Return

新規Pathだけで次を作る。

1. Exact Return Handoff
2. Recovery Index

Returnには次を含める。

- 最大Claim
- Files Changed／Deliberately Not Changed
- WU別Before／After
- User実Evidenceと再現結果の対応
- Batch／Attempt Evidenceの実値
- Root Causeの確定範囲と未確定範囲
- Retry OFF／ONの成功率、Latency、Token、Raw Digest比較
- Retry採用／不採用判断
- Constrained Decoding工数評価
- Focused／Full／Static／Real Trial結果
- Open Findings
- Git writeなしの明記
- Codex Controller Independent Review待ちで停止

## 14. SUPERSEDED — 2026-09-06 User決定

本Handoffは実装開始前の作戦会議により失効した。特にWU-03／04のJSON Retryは実行しない。

後続正本は次である。

`phase_9_controller_gemma_judge_only_constrained_decoding_rework_exact_handoff_ja_20260906111043.md`

理由は、同一`seed=0` Retryは同じ出力を再現し、Seed変更RetryはJudgeの不安定性を残したまま成功確率だけを変えるためである。本Handoffを単独で実装指示として使用してはならない。
