# Phase 9-1 — Gemma Constrained Decoding Final Contract Micro Rework Exact Handoff

```yaml
document_id: phase_9_controller_gemma_constrained_decoding_final_contract_micro_rework_exact_handoff_20260906124425
document_type: exact_rework_handoff
document_state: ready
phase: phase_9
program: phase_9_1
recorded_at: 2026-09-06 12:44:25 JST
language: ja
from: codex_controller
to: claude_code
decision_authority: user
authority_owner: Nazuna Research
in_response_to: phase_9_claude_gemma_judge_only_constrained_decoding_rework_exact_return_ja_20260906123248.md
phase_9_1_closure_authorized: false
git_write: prohibited
append_only: true
```

## 1. Controller結論

前RoundのGemma Judge限定Constrained Decodingは、実機Trial A／BでMalformed JSON再現経路を防ぎ、Judge単独実行とRepair→Rejudge→採用を成立させた。主配線とJudge-only Isolationは妥当であり、大規模再設計は不要。

ただし、User実画面Recheckの前に、以下3件のみを修正する。これをGemma固有の追加研究、Prompt Tuning、Retry、新規Observabilityの追加に拡張しない。

## 2. IR-FC-01 — Gemma Rejudge Sampling契約の不一致

### Finding

Gemma初回Judge Batchは`GEMMA_JUDGE_DETERMINISTIC_SAMPLING`により、`temperature=0.0` / `top_p=1.0` / `top_k=1` / `min_p=0.0` / penalties / `seed=0`を使う。

一方、`attempt_live_repair()`のRejudgeは`GenerationParameters(max_new_tokens=...)`から作られ、Grammarは付くがSamplingはDefaultの`temperature=0.7` / `top_p=0.8` / `top_k=20` / `presence_penalty=1.5` / `seed=None`へ戻る。

これは同一Gemma Judgeの初回判定とRejudgeが別の生成契約で動く状態である。

### Required Fix

- GemmaのRejudgeに、初回Judgeと同じProvider-local Sampling契約を渡す。
- 渡す値はTurn／ProviderでFreezeされ、Rejudge時のLive再読みにしない。
- `max_new_tokens`は既存Rejudge Planの値を使い、Sampling契約から上書きしない。
- Gemma以外のSelene／Main-shared／Built-inには波及させない。
- Main通常回答、Repair Candidate、Guardは無変更。

### Required Tests

- Gemma Rejudge Requestが`seed=0` / `temperature=0.0` / `top_k=1`等の初回Judgeと同じSampling値を持つ。
- Rejudge Planの`max_new_tokens`は維持される。
- Factory／Override未指定の既存Rejudgeは現在のDefaultのまま。
- Repair CandidateにSampling／Grammarが逆流しない。

## 3. IR-FC-02 — StructuredOutputConstraintのSchema／Digest不変性

### Finding

`StructuredOutputConstraint` 自体は`frozen=True`だが、`json_schema` は可変`dict`である。Controller Probeで構築後に`constraint.json_schema["type"] = "number"`が成功し、`schema_digest_sha512`は変更前の値のまま残った。

このままでは、EvidenceのDigestと実際にGrammar Compilerへ渡すSchemaを不一致にできる。

### Required Fix

- 少なくともGrammar構築直前にCanonical SerializationとSHA-512を再計算し、保持Digestと違う場合はTyped Fail-closedにする。
- 可能ならContract内でNested Schemaも変更不能、またはCanonical JSONを真実源にする。ただし大規模API再設計は不要。
- `from_schema()`のJSON非直列化可能入力がRaw `TypeError`で終わる現状も、既存ContractのTyped Validation Failureと整合させる。

### Required Tests

- 構築後のNested Schema変更を試みても、変更不能か、Grammar構築前にDigest不一致でTyped Rejectされる。
- JSON非直列化可能値は契約境界のTyped Failureに収束する。
- 正常SchemaのGrammar構築は維持する。

## 4. IR-FC-03 — Model Call 0時のEvidence Call Count

### Finding

Dedicated batched Judgeの`_run_selene_dispatch()`は`call_count=len(frozen_batch_evidence) or 1`を渡す。Prior Dialogueを含むPromptがBudgetを超えて全CriterionがDeferredになった場合など、Batch／Model Call 0でも`1`が記録される。

### Required Fix

- Dedicated／batched経路からは実際のBatch Call数をそのまま渡す。0なら0を記録する。
- 非batched既存CallerのDefault `call_count=1`は変更しない。
- Model Call 0時にPrompt DigestやBatch Evidenceを捏造しない。利用可能な情報がなければ`unavailable`／未設定とする。

### Required Tests

- `max_calls=0`、または全CriterionがPrompt Budget Deferredとなる確定的Fixtureで、Model Call 0およびEvidence `call_count=0`を確認する。
- 通常の4 Batch経路は`call_count=4`を維持する。

## 5. Return Claimの訂正

- 前Returnは「Adoption Gate全7項成立」としたが、Memory RSS等は未計測である。LatencyとCrash／Timeout非発生は成立したが、Memoryの定量的成立までは主張しない。追加Memory Profileは今Roundで要求しない。
- `criteria_evaluated=31` + `unknown=1`は、現行定義の`evaluated=passed+deviated`とCount保存則に合致する。これ自体を未調査Anomalyと呼ばない。Unknown 1件の判定理由を今Roundで追加調査しない。
- 訂正は新規Exact Returnに記録し、既存Returnを上書きしない。

## 6. Verification

1. 上記3件のFocused Unit／Integration Test。
2. Judge-only Isolationの既存回帰Test。
3. 非Model Full Suite。
4. Ruff。
5. Canonical Mypyと既存Baseline比較。
6. 実機Golden Pathは最大1回だけ。Gemma初回Judge→Repair Candidate→Gemma Rejudge→採用と、Rejudgeの固定Samplingを確認する。

実機前後にProcess／Portを確認し、存在しなければKillしない。実機1回が失敗しても追加反復せず、そのまま返却する。

## 7. Scope Boundary

- JSON Retry／Seed変更Retry／Decoder緩和／JSON補修を禁止する。
- Gemma Prompt／Schema／Criterion／Budget／Contextの追加Tuningを禁止する。
- Selene／Guard／RAG／Web／Dev Agentの再実機試験を禁止する。
- Phase 9-2／9-3／Phase 10作業を禁止する。
- UI変更を禁止する。
- Git add／commit／push／stash／resetを禁止する。Gitはread-onlyのみ。
- 既存Docsの上書き／直編集を禁止する。必要なReturn／Recoveryは新規Pathで作る。
- Phase 9-1 Complete／Closureを主張しない。

## 8. Exact Return

新規Exact ReturnとRecovery Indexに次を記録する。

- 最大Claim
- 3 FindingのBefore／After
- Rejudge SamplingのFrozen値と非波及証明
- Schema／Digest不変性または使用直前照合の証明
- Model Call 0時のEvidence
- Unit／Full／Static／実機1回の結果
- 前ReturnのMemory／`criteria_evaluated`表現の訂正
- 未解決事項
- Git writeなし
- Codex Controller Independent Review待ちで停止
