# Gemma Code Toggle式・不正JSON限定Retry実験 予約

```yaml
document_id: gemma_code_toggle_bounded_malformed_json_retry_experiment_reservation_20260905200925
document_type: planned_work_reservation
document_state: reserved_not_started
language: ja
recorded_at: 2026-09-05 20:09:25 JST
decision_authority: user
authority_owner: Nazuna Research
depends_on: phase_9_1_r4_gemma_compact_schema_result
default_enabled: false
ui_control: none
implementation_started: false
append_only: true
```

## 1. Decision

Gemmaの間欠的なMalformed JSONに対し、コード上だけでON／OFFできるProvider限定Retryを比較実験候補として予約する。既定値はOFF。Phase 10のUIへは現時点で追加しない。

既存予約`bounded_judge_json_retry_evaluation_and_reuse_reservation_ja_20260905011625.md`の原則を維持し、今回はGemma、Feature Toggle、R4後という実行境界を追加する。

## 2. 実験機能の境界

- 対象はGemma JudgeのStrict Decode `malformed_output`だけ。
- 追加実行は最大1回。無制限Retry、成功するまでの反復は禁止。
- `finish_reason=LENGTH`、Timeout、Unavailable、Load Failure、Context／Budget不足、Cancellation、Model Busyは対象外。
- 同じFrozen Provider、Candidate、Criterion集合、Evidence、Mode、Deadline内で実行する。
- 初回の壊れたJSONを補修・部分採用しない。Retry出力も現行Strict Decoderで完全に検証する。
- Retryでも失敗した場合は従来どおりTyped Failure／Fail-closedとする。
- 初回FailureとRetry Attempt／Resultを別Evidenceとして残す。
- OFF時はCall数、Latency、Token、結果がRetry実装前と同じであることをTestする。

同一Prompt・同一Deterministic Seedの単純再実行は同じByteを再生成する可能性が高い。試す場合は、判定対象を変えず、二回目だけ固定のGemma専用「Compact Schemaで完全なJSONを再出力する」指示を使う案を比較する。Seed変更や自由なPrompt改変は同時に混ぜず、どの差分が効いたかを分離する。

## 3. 実行順序

1. R4のGemma Compact Criterion SchemaをRetryなしで検証する。
2. Compact Schemaだけで安定するなら、RetryをMVPへ追加しない。
3. 間欠的Malformedが残る場合だけ、コードToggle既定OFFで実装する。
4. OFF／ONを同じDeviation条件で比較する。
5. 回復率、追加時間、追加Token、Call数、Cancellation応答を記録して採否を決める。

R4へ途中追加してSchema変更とRetry効果を混同しない。

## 4. 採用条件

- Strict Decode成功率が明確に改善する。
- 判定内容を都合よく選び直す挙動にならない。
- User Stop、Main-priority Preemption、Deadline、Provider Lease Releaseを退行させない。
- 追加Latency／Token消費が実用上許容できる。
- OFFへ戻すだけで完全に旧挙動へ復帰できる。

改善が小さい、遅延が大きい、Evidenceが曖昧になる場合は既定OFFの実験機能としても採用せず、予約記録だけを残す。

## 2026-09-06 Disposition

Gemma Phase 9-1修復では不採用。Judge限定Constrained Decodingを先に採用し、JSON Retryは実装しない。同一`seed=0` Retryは無意味であり、Seed変更Retryも不安定なJudgeを安定化したことにはならない。本書は他Provider／他Structured Outputで将来再評価できる研究予約としてのみ保持する。
