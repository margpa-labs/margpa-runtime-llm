# Phase 9-1 — Gemma Final Contract: Model Call 0 Evidence Micro Rework Exact Handoff

```yaml
document_id: phase_9_controller_gemma_final_contract_zero_call_evidence_micro_rework_exact_handoff_20260906133525
document_type: exact_rework_handoff
document_state: ready
phase: phase_9
program: phase_9_1
recorded_at: 2026-09-06 13:35:25 JST
language: ja
from: codex_controller
to: claude_code
decision_authority: user
authority_owner: Nazuna Research
in_response_to:
  - phase_9_claude_gemma_constrained_decoding_final_contract_micro_rework_exact_return_ja_20260906131256.md
  - phase_9_claude_gemma_constrained_decoding_final_contract_micro_rework_exact_return_addendum_real_hardware_rejudge_sampling_confirmation_ja_20260906132919.md
phase_9_1_closure_authorized: false
git_write: prohibited
append_only: true
```

## 1. Controller判定

以下は解決を確認した。

- Gemma初回JudgeとRepair Rejudgeの固定Sampling一致。
- Addendumによる実機Rejudge Requestの8 Sampling値とStructured Output付与の直接確認。
- Structured Output Schemaの使用直前Digest再照合とTyped Fail-closed。
- JSON非直列化可能SchemaのTyped Validation Failure化。
- Dedicated batched JudgeのModel Call 0時の`call_count=0`、`seed=None`、Batch Evidenceなし。
- Focused Test 112件とRecording Test 10件のController再実行は全PASS。

Gemma Judgeの主機能を再設計する必要はない。実画面Recheckを妨げる機能障害も新たに確認していない。

ただしIR-FC-03のEvidence契約が1点だけ未完了であるため、以下だけをMicro Reworkする。

## 2. IR-FC-04 — Model Call 0時のPrompt Digest誤記録

### Finding

Dedicated batched経路でBatchが0件の場合、`_batch_dispatch_prompt_digest_sha512()`は`None`を返す。

その`None`はRecording層で「Overrideなし」と解釈され、実際のModel Promptではない固定説明文
`(dedicated Selene evaluator: prompt built internally by SelenePromptAdapter)`
のSHA-512を`prompt_digest_sha512`として保存する。

したがって、`call_count=0`でModel Callも実Promptも存在しないEvidenceに、正規のPrompt Digestらしい128桁値が残る。前Handoff §4の「Model Call 0時にPrompt Digestを捏造しない。利用可能な情報がなければunavailable／未設定」と一致しない。

既存Testは`call_count`、`seed`、`batch_evidence_json`だけを確認し、最終的に保存される`prompt_digest_sha512`を確認していないため、この残差を検出できない。

### Required Fix

- Dedicated batched経路で実Batch Evidenceが0件なら、保存Metadataの`prompt_digest_sha512`を明示的に`unavailable`とする。保存Schema上で安全に省略できるなら未設定でもよいが、既存Metadata契約との整合を優先する。
- 実Batchが1件以上ある場合は、現在の実Batch Prompt Digest集約値を維持する。
- 非batched既存Callerの「渡された実Promptをhashする」挙動は変更しない。
- `call_count=0`、`seed=unpinned`、Batch Evidenceなしという今回の修正済み値を維持する。
- Model Call、Judge判定、Repair、Constrained Decoding、Provider Lifecycleには触れない。

### Required Test

実`build_judge_evidence_recorder()`まで通す確定的Testで、Model Call 0の保存Metadataを直接確認する。

- `call_count == 0`
- `prompt_digest_sha512 == "unavailable"`、または採用した契約どおり未設定
- `seed_pinned is False`
- `seed == "unpinned"`
- `batch_evidence_json`なし

併せて、通常batched経路のPrompt Digestと、非batched既存CallerのPrompt Digestが変わらないことを既存Testまたは最小追加Testで確認する。

## 3. Verification

- 上記Recorder経由Test。
- Judge dispatch routerとRecording integrationのFocused Test。
- 変更FileのRuff／Mypy。
- 実モデル、実機Golden Path、Server起動は不要かつ禁止。
- 非Model Full Suiteの再実行も、このEvidence 1点のためには不要。

## 4. Scope Boundary

- Gemma／Selene／Qwen／Guardの実機試験を行わない。
- Retry、Seed変更、Decoder、Schema、Prompt、Sampling、Budget、Contextを変更しない。
- UI、Phase 9-2／9-3、Phase 10へ拡張しない。
- Git add／commit／push／stash／resetを行わない。Gitはread-onlyのみ。
- 既存Docsを上書きしない。Return／Recoveryは新規Pathへ追加する。
- Phase 9-1 Complete／Closureを主張しない。

## 5. Exact Return

新規Exact ReturnとRecovery Indexへ、IR-FC-04のBefore／After、保存Metadataの実値、Focused／Static検証、Git writeなしを簡潔に記録し、Codex Controller Independent Review待ちで停止する。
