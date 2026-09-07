# Phase 9-1 — Gemma Judge限定Constrained Decoding Rework Exact Handoff

```yaml
document_id: phase_9_controller_gemma_judge_only_constrained_decoding_rework_exact_handoff_20260906111043
document_type: exact_rework_handoff
document_state: ready_for_implementation
phase: phase_9
program: phase_9_1
controller: codex
implementer: claude_code
language: ja
created_at: 2026-09-06 11:10:43 JST
maximum_authorized_claim: P9_1_GEMMA_JUDGE_ONLY_CONSTRAINED_DECODING_READY_FOR_USER_RECHECK
phase_9_1_closure_authorized: false
json_retry_authorized: false
git_write_authorized: false
append_only_docs: true
```

## 1. Objective

Gemma初回Judge／RejudgeだけへJSON Schema由来Grammarを適用し、Prompt遵守だけに依存したMalformed JSON生成を構造的に防ぐ。同時にPrior Dialogue投影とBatch Evidenceの正確性を修復する。

Main通常回答、Repair Candidate生成、Guardその他のRoleへ構造制約を漏らしてはならない。

## 2. Read First

1. `docs/project/phases/phase_9/history/operations/phase_9_1_gemma_judge_only_constrained_decoding_strategy_decision_ja_20260906111043.md`
2. `docs/project/phases/phase_9/history/operations/phase_9_1_post_r5_user_mac_final_manual_recheck_result_and_gemma_retry_decision_ja_20260906105356.md`
3. `docs/project/phases/phase_9/handoffs/phase_9_claude_component_independence_r5_final_micro_rework_exact_return_ja_20260906002247.md`
4. `docs/project/phases/phase_9/history/operations/phase_9_1_component_independence_r5_controller_acceptance_ja_20260906002712.md`

`phase_9_controller_gemma_production_structured_output_observability_and_bounded_retry_rework_exact_handoff_ja_20260906105356.md`はSUPERSEDEDである。そこに記載されたJSON Retryを実装してはならない。

## 3. Fixed Decisions

- JSON Retryは実装しない。
- Seedを変更しない。
- Strict Decoderを緩和しない。
- GemmaのCompact Criterion Schemaを基礎にする。
- Constrained Decodingは初回JudgeとRejudgeだけ。
- Main通常生成とRepair Candidate生成は従来どおり非Grammar。
- Shared Type／Backend extensionは任意かつDefault `None`。
- Judge Compositionが明示しない限りBackendへGrammarを渡さない。

## 4. WU-01 — Judge-only Structured Constraint Contract

必要最小限のBackend-neutral Contractを設計する。名称はRole中立でもよいが、利用はJudgeだけに限定する。

例:

```text
StructuredOutputConstraint
json_schema
schema_digest_sha512
```

必須条件:

- OptionalかつDefault `None`。
- 空、過大、不正JSON SchemaをTyped Rejectする。
- Request Freeze後に変更されないImmutable値。
- Schema全文を通常Evidenceへ保存せずDigestを保存できる。
- Main／Repair／Guardの既存Request Serializationを変えない。

`GenerationParameters`へ直接置くか別Contractにするかは、既存層境界と最小変更で判断する。ただしMain等のCall siteを一斉書換えする設計は禁止する。

## 5. WU-02 — llama.cpp Grammar配線

現Environmentで存在確認済みの次を使用する。

```text
LlamaGrammar.from_json_schema(schema, verbose=False)
Llama.create_completion(..., grammar=grammar)
```

制約指定があるRequestだけGrammarを構築・注入する。指定がないRequestは`grammar=None`で従来と同一挙動にする。

Backend Runtime Capabilityは実態と一致させる。現在Model TOMLのOptional `json_schema`だけを根拠に虚偽のEffective Capabilityを出してはならない。Backend Versionの実Capability、Request validation、Typed failureを整合させる。

Grammar構築失敗を通常生成へFallbackしてはならない。Judge RunをTyped FailureへFail closedする。

## 6. WU-03 — Dynamic Judge Schema

各Judge BatchのExpected Criterion集合からJSON Schemaを決定的に生成する。

最低限、次を構造制約する。

- Top-levelは単一Object。
- `recommendation`は`accept | needs_repair | unknown`。
- `confidence`は0.0から1.0。
- `reasoning`はString。
- `criterion_results`はArray。
- 各EntryはGemma Compact Schemaの`criterion_id`、`disposition`、`confidence`だけ。
- `disposition`は`pass | deviation | unknown`。
- Additional Propertiesを許さない。
- Batchの必要件数を制約する。

JSON Schema→Grammar変換が`const`／`prefixItems`等を完全対応しない場合、Syntax／Enum／件数をGrammarで保証し、Exact ID集合、duplicate、missing／extraは既存Strict Decoderで検証する。Decoderの責務を削らない。

初回JudgeとRepair Rejudgeが同じSchema Factoryを使う。Repair Candidate生成へ適用しない。

## 7. WU-04 — Prior Dialogue Projection

Dedicated JudgeのPrompt ContractへBounded `dialogue_context`を追加する。

- Gemma／Seleneの共有Prompt Adapter境界として正しく投影する。
- Citation Evidenceとは別Sectionにする。
- Prior DialogueはInstructionではなく会話履歴として扱う。
- Prompt Template／Manifest／Digestを正しく更新する。
- Token Plannerが追加分を実測し、Context／Budgetを超える場合は既存Typed Gateへ収束する。

User Test Aの現在入力は意味Oracleとして曖昧なので、TestではPrior DialogueがPromptへ一度だけ入ることを直接Assertする。Deviation Hard Oracleには明示的`evidence_context`を使う。

## 8. WU-05 — Truthful Batch Evidence

Dedicated batched Judgeについて、現在の次の誤記録を修復する。

- 実PromptでないPlaceholder Digest
- `call_count=1`固定
- `token_usage=0`
- Gemma実値と異なる`seed=unpinned`
- Generic 200 Token single-call由来Config Digest
- Batch、finish reason、Decode理由の欠落

Batchごとに次を安全に保持する。

- Batch Index
- Actual Prompt Digest
- Expected Criterion ID集合Digestと件数
- Actual max_new_tokens／sampling／seed
- finish reason
- prompt／completion Tokens
- Raw byte lengthとSHA-512（Raw全文は通常保存しない）
- Grammar有効状態とSchema Digest
- Strict Decode state／Typed reason

Run集約のCall数、Token数、Latencyを実値から計算する。Recording OFFはRecorder Call 0を維持する。

## 9. WU-06 — Isolation Proof

次をSabotage-regressionを含めて証明する。

1. Gemma初回Judge RequestだけConstraintあり。
2. Gemma Rejudge RequestだけConstraintあり。
3. Main通常GenerationはConstraint `None`。
4. Repair Candidate GenerationはConstraint `None`。
5. Qwen3Guard RequestはConstraint `None`。
6. RAG／Web／Dev Agent経路へ影響なし。
7. Constraintなしのllama.cpp呼出し引数と挙動が変更前と同一。
8. Grammarを意図的に外すとMalformed再現FixtureまたはSchema Testが失敗し、戻すと通る。

共通コードを置いたことを、全Roleへの機能適用と混同しない。

## 10. Verification and Real Trial

順序:

1. Contract／Backend／Schema Unit Test
2. Initial Judge／Rejudge Production Composition Test
3. Isolation Proof／Sabotage-regression
4. 非Model Full Suite
5. Ruff
6. Canonical Mypyと既存Baseline比較
7. Real Gemma Trial

Real Trialは最大2本だけ。

- Trial A: Evidence-backedな32 Criterion初回Judge。JSON完了、全ID、Count保存、Deviationを確認。
- Trial B: Judge起点またはMain Governance起点のProduction Golden Pathで、Repair Candidateは非Grammar、RejudgeだけGrammar、改善採用を確認。既存Test構成を最大限再利用する。

目的のない反復、Userへの追加試験依頼は禁止する。各Trial前後に残存Process／Portを確認し、存在しなければKillしない。

## 11. Adoption Gate

Gemma継続を提案できる条件:

- Trial A／Bとも`malformed_output`なし。
- finish reason、Token、Grammar／Schema DigestがEvidenceへ正しく残る。
- Strict DecoderとCount保存則成立。
- Evidence-backed Deviation成立。
- Repair→Rejudge→採用成立。
- Judge以外への影響0。
- Latency／MemoryがMVPとして実用範囲。

一つでも本質的に不成立なら、無期限Reworkを提案せず、GemmaをExperimentalへ降格して別軽量独立Judge選定へ移る判断材料を返す。

## 12. Prohibited

- JSON Retry実装／Seed変更
- Decoder緩和／JSON補修／部分採用
- Selene実機試行
- Guard修正／実機再試行
- Main Context／Repair Budget／Criterion上限の変更
- Phase 9-2／9-3、Phase 10作業
- UI Advanced設定追加
- Git add／commit／push／stash／reset
- 既存Handoff／Return／History上書き
- Phase Index／Registry Docs直接編集
- Phase 9-1 Complete／Closure Claim

## 13. Exact Return

新規PathでExact ReturnとRecovery Indexを作る。次を必ず含める。

- 最大Claim
- Files Changed／Not Changed
- WU別Before／After
- Judge-only Scope証明
- Schema／Grammar対応範囲
- Prior Dialogue投影結果
- Batch Evidence実値
- Unit／Full／Static／Real Trial結果
- Trial A／BのLatencyとMemory観測
- Gemma継続／Experimental降格の提案
- 未解決事項
- Git writeなし
- Codex Controller Independent Review待ちで停止

