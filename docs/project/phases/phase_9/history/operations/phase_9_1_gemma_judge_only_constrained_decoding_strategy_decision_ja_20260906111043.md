# Phase 9-1 — Gemma Judge限定Constrained Decoding作戦決定

```yaml
document_id: phase_9_1_gemma_judge_only_constrained_decoding_strategy_decision_20260906111043
document_type: controller_user_strategy_decision
document_state: accepted_for_bounded_rework
phase: phase_9
program: phase_9_1
owner: nazuna_research
controller: codex
language: ja
recorded_at: 2026-09-06 11:10:43 JST
json_retry: rejected_for_current_rework
constrained_decoding_scope: judge_only
append_only: true
```

## 1. 決定

Gemmaを即時廃棄せず、最後の有界修復としてJudge限定Constrained Decodingを実装・評価する。

対象は次だけである。

1. 初回LLM-as-a-Judge評価。
2. Repair Candidate生成後のRejudge。

対象外は次である。

- Main通常回答
- Repair Candidate生成
- Guardrail
- RAG／Web／Dev Agent
- 将来の構造Governance生成
- その他のRole／Provider

共通Inference Contractに任意の構造制約表現を置くこと自体は許容する。ただしDefaultは必ず無効であり、Judge Compositionだけが明示的に注入する。Judge以外のGeneration RequestとBackend呼出しが変更前と同一であることをTestで証明する。

## 2. Retry不採用

JSON Retryは今回実装しない。

- Gemmaは`seed=0`であり、同一Promptの再試行は同じ壊れた出力を再現する。
- Seed変更Retryは成功可能性を多少上げても、不安定なJudgeという根本問題を残す。
- Constrained DecodingがJSON構造を強制できるならRetryは不要。
- Retry成功をPhase 9-1 Closure根拠にしない。

既存の`MODEL_BUSY`用Retryは別のLifecycle対策であり、本決定のJSON Retry禁止対象ではない。変更しない。

## 3. 判明した構造上の原因

現在の`llama-cpp-python 0.3.34`は次を提供する。

```text
Llama.create_completion(..., grammar=...)
LlamaGrammar.from_json_schema(json_schema, verbose=...)
```

一方、現在のMARGPA `GenerationParameters`とmanual `Llama.create_completion()`配線はGrammar／JSON Schemaを渡していない。GemmaはPromptだけを頼りにJSONを自由生成し、Strict Decoderは生成後に拒否するだけである。

Strict DecoderのFail-closed自体は正しい。欠けているのは生成時の構造制約である。

またDedicated Judge用Prompt Adapterは`dialogue_context`を受領しているがPromptへ投影していない。User Test AではGemmaに先行Turnの`765`が見えておらず、現在指示とCandidateだけを評価していた。これをGemma品質FAILと誤認せず、Prompt Contractの投影漏れとして修復する。

## 4. 成否Gate

Constrained Decoding適用後、次を有界評価する。

- JSON SyntaxがGrammarにより崩れない。
- Strict DecoderによるField、Value、Criterion ID、件数検証を維持する。
- Evidence-backedな明白な矛盾をDeviationとして評価できる。
- Judge起点Repair→Rejudge→採用が成立する。
- Main Governance起点Repair→Rejudge→採用が成立する。
- Main通常Chat、Repair Candidate、GuardへGrammarが漏れない。
- LatencyとPC負荷がMVPとして許容範囲にある。

成立すればGemmaを既定独立Judgeとして継続する。なお不安定、意味評価品質不足、または実用上重すぎる場合はGemmaをExperimentalへ降格し、別の軽量独立Judgeを選定する。Gemmaへの無期限Reworkは行わない。

