# Phase 9-1 — 実32 Criterion Truncation Evidence受理／Budget 3600提案

```yaml
document_type: controller_independent_review
document_state: evidence_accepted_budget_change_awaiting_user_authority
recorded_at: 2026-09-05 09:11:59 JST
language: ja
reviewer: codex_controller
phase_9_1_closure: false
```

## 1. Evidence判定

Claude Execution-only ReturnをACCEPTする。

- 完全Log: `/private/tmp/phase9_gemma32_claude_complete_capture_20260905085447.log`
- Log SHA-512: `1c8bba6f8fd9bfc0721f4991b5fbe494574adae5fc30040156e08e40b140efd13b1aa7ab3feec82e792788797099aca9fbb7c032c4e1d9d3e28c2d8f3352f277`
- Controller再計算SHA-512: 一致
- `finish_reason=length`
- Prompt 3612 Token／Completion 2400 Token
- Rejudge `max_new_tokens=2400`
- Strict Decoder: FAILED／未完JSON Object
- Model Load Failure: なし
- 実行時間: 75.14秒、Rejudge生成64.06秒

今回のRunについて、Decoder COMPLETED＋Criterion UNKNOWNではなく、2400 Token上限到達による応答切断と、その結果の未完JSONによるDecoder FAILEDが不成立原因と確定する。これを「Gemmaは常に32 Criterionを処理不能」とは一般化しない。

## 2. Current値の評価

`_REJUDGE_TOKENS_PER_CRITERION=75`と`LIVE_REPAIR_BUDGET.max_additional_tokens=2800`はPlan／Fixtureでは成立するが、実Gemma 32件では実測上不足した。2400 Tokenを完全消費して`LENGTH`となったため、同一上限のRetryは原因へ作用せず、時間だけを追加消費する可能性が高い。

## 3. 最小変更提案

User承認が得られた場合に限り、次を変更する。

- `_REJUDGE_TOKENS_PER_CRITERION`: 75→100
- `LIVE_REPAIR_BUDGET.max_additional_tokens`: 2800→3600
- Repair Candidate上限400、32 Criterion、最大Call 2、Context、Deadline、Decoder、Schemaは不変

算術:

```text
Rejudge: 100 × 32 = 3200
Repair:  400
Total:   3600
Gemma context: prompt 3612 + output ceiling 3200 = 6812 < 8192
Observed speed projection: 3200 ÷ (2400 / 64.06s) ≈ 85.4s < 120s rejudge deadline
```

Context／時間には余裕がある計算だが、成功保証ではない。変更後は完全Log保存付き実機Runを1回だけ行い、成功またはFailureを確定する。診断にはRaw内の`criterion_id`出現数も追加し、再度LENGTHならどこまで生成できたかを残す。

## 4. 代替案の扱い

- 同一2400でのRetry: 今回は採用しない。
- Prompt／Schema圧縮: 意味・Evidence品質への影響があるため第一選択にしない。
- Rejudge Batching: 設計・集約・Cancel／Budget検証が増えるためMVP最小修復にしない。
- 100／3600で再びLENGTHの場合: 自動再拡大せず、125／4400、Prompt圧縮、Batchingを改めて比較する。

## 5. Current Disposition

原因分離Evidenceは完了。実32 Criterion Rejudge成立は未完了。Budget変更はUser未承認のため未実装であり、Phase 9-1 Closureは引き続き行わない。

