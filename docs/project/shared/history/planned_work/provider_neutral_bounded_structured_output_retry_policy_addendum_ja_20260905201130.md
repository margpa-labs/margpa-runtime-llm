# Provider-neutral Bounded Structured Output Retry Policy 追補予約

```yaml
document_id: provider_neutral_bounded_structured_output_retry_policy_addendum_20260905201130
document_type: planned_work_reservation_addendum
document_state: reserved_not_started
language: ja
recorded_at: 2026-09-05 20:11:30 JST
decision_authority: user
authority_owner: Nazuna Research
supersedes_scope_of: gemma_code_toggle_bounded_malformed_json_retry_experiment_reservation_ja_20260905200925.md
implementation_started: false
append_only: true
```

## 1. 補正Decision

最初の検証対象はGemmaでも、Retry機構そのものをGemma専用Hardcodeにはしない。他のJudge Providerや将来のStructured Output Providerへ再利用できる、Provider-neutralな有界Policy／Portとして設計する。

## 2. 実装境界

- 共有名は`StructuredOutputRetryPolicy`、`retry_policy`、`retry_attempt`など役割を表す名称とし、Gemma名を共有変数／共有分岐へ埋め込まない。
- Policyは少なくとも`enabled`、`max_retries`、対象Failure、Retry Prompt Strategyを明示的に持つ。
- Evaluator共有処理に`if provider_id == "judge.gemma..."`を追加しない。
- Providerごとの差はFactory／Adapter構築時のPolicy注入、またはProvider Registry設定で表す。
- Retry PromptのProvider固有差分はStrategy／Callableとして注入し、共通Evaluatorへ文言をHardcodeしない。
- Policy未注入または`enabled=false`なら追加Call 0で、現在の挙動と一致させる。
- 初期設定は全ProviderでOFF。Gemmaは最初の比較対象にすぎず、自動ONにはしない。
- Strict Decoder、Budget、Cancellation、Evidence契約はProviderに関係なく同じ境界を使う。

## 3. 実行時期

R4のCompact Schema結果を先に確認する。Retryが必要と判断された場合のみ、このProvider-neutral境界で実装し、Gemmaを最初の適用Test Caseとする。R4中には追加しない。

## 2026-09-06 Disposition

共有設計知識として保持するが、現在のGemma Judge Reworkでは実装しない。JSON崩れはJudge限定Constrained Decodingで先に構造的解消を試みる。Retryによる確率的成功化をPhase 9-1 Closure根拠にしてはならない。
