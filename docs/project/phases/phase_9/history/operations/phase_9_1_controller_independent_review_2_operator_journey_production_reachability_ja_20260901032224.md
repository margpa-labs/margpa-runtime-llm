# Phase 9-1 Controller Independent Review 2 — Operator Journey／Production Reachability

```yaml
document_id: phase_9_1_controller_independent_review_2_operator_journey_production_reachability_20260901032224
document_state: finding_confirmed_rework_required
language: ja
created_at: 2026-09-01T03:22:24+09:00
phase: phase_9
program: phase_9_1
review_ordinal: 2
review_axis: operator_journey_and_production_reachability
independent_from_review_1: true
phase_9_1_closure: forbidden
```

## 1. Review境界

Review 1のRequirements／Acceptance／Claim照合は繰り返していない。本Reviewは、利用者が実際に起動してから結果を見るまでの次のProduction経路だけを追跡した。

```text
CLI Startup Opt-in
→ Production Composition Root
→ Provider選択
→ Mode ON
→ Preflight
→ Artifact Load
→ Role固有Prompt／Contract構築
→ 実Inference
→ Strict Decode
→ Evidence／UI
→ Mode OFF
→ Unload
```

Review 1で成立済みとされたTest数、Acceptance件数およびMaximum Claimは、本Reviewの根拠として流用していない。

## 2. 実Artifact存在確認

Projectの既定`model_root = ./models`に、次の両Artifactが存在することをRead-only `stat`で確認した。

- Selene Q5_K_M: 5,732,992,896 bytes
- Qwen3Guard Q8_0: 804,753,472 bytes

これはArtifactの存在だけを示す。実Load、Registry SHA-512一致、Metal実行、実InferenceおよびUnload成立を示すものではない。

## 3. P9-CODEX-006 — Selene Production Contractが現在成立不能

```yaml
severity: critical_mvp_blocker
disposition: open_rework_required
affected_scope:
  - real_selene_activation
  - semantic_109_evaluation
  - active_state_truthfulness
  - production_evidence
```

### 3.1 現Production Manifest

`config/judge_templates/selene/manifest.json`は次の状態である。

- `template_type = official_selene_prompt_template_unresolved`
- `upstream_revision = null`
- `template_file = null`
- `template_sha512 = null`
- `verified_official_copy = false`

したがって`SelenePromptAdapter.build()`は、実評価時に必ず`SelenePromptUnavailable`へ収束する。

### 3.2 Active表示と実行可能性の分離

`SeleneRoleAdapter.preflight()`はSelene Prompt Manifestを検査しない。`load()`はGGUFをLoadした後に`SelenePromptAdapter`を構築するが、実際のTemplate完全性とPlaceholder契約は最初の`build()`まで検査しない。

このため現在は、Artifact Loadが成功すればProvider Selectionが`active`を表示し得る一方、最初の実Semantic評価は必ず`UNAVAILABLE`になる。これは「Active Providerは実行可能なProviderである」という利用者向け表示契約を満たさない。

### 3.3 公式Promptと現Decoderの契約不一致

Atla公式GitHubは、Selene Miniの学習時PromptとしてClassification、Absolute Scoring等の個別Templateを公開している。

- https://github.com/atla-ai/selene-mini/tree/main/prompt-templates
- https://github.com/atla-ai/selene-mini/blob/main/prompt-templates/classification.yaml
- https://github.com/atla-ai/selene-mini/blob/main/prompt-templates/absolute-scoring.yaml

公式TemplateのPlaceholder／出力は、概ね次の契約である。

- 入力：`user_input`、`assistant_response`、単一Rubric、必要ならReference
- 出力：`**Reasoning:** ...`と`**Result:** Yes|No`、または1〜5

一方、現Projectの`SelenePromptAdapter`は次を一つのTemplateへ必須としている。

- `{{query}}`
- `{{candidate}}`
- `{{reference}}`
- `{{criteria}}`
- `{{response_schema}}`

さらに現`decode_judge_output()`は、全Criterionを含むProject独自JSON Objectを要求する。よって、公式TemplateのExact Copyを配置するだけでは現Decoderを通らず、現Project独自Templateを置けば`verified_official_copy`というClaimが虚偽になる。

これは単なる未取得Fileではなく、Prompt Assembly／呼出し粒度／Decode／Evidence集約を明示的に設計し直す必要があるContract不一致である。

### 3.4 Testの偽陽性

`tests/unit/evaluation/test_selene_adapter.py`および`tests/unit/adapters/runtime_model_control/test_dedicated_role_adapters_production_wiring.py`は、`https://example.invalid/fixture`をSourceとするProject独自Templateへ`verified_official_copy = true`を設定している。

これらはFixture配線Testとしては利用できるが、公式Prompt互換またはProduction Selene成立のEvidenceにはならない。Test名・Docstring・Claimは、Fixture ContractとOfficial Contractを分離しなければならない。

## 4. P9-CODEX-007 — Dedicated Preflightの名称・Claimが実装より強い

```yaml
severity: major_claim_and_diagnostic_gap
disposition: open_rework_required
affected_scope:
  - selene_preflight
  - qwen3guard_preflight
  - failure_reason_truthfulness
  - recovery_docs
```

Claude追加の`_run_dedicated_preflight()`は、Docstring上「Artifact／Manifest／Digest／Quantization／Backend／Hardware capability probe」とClaimしている。しかし実際の`LlamaCppRuntimeModelBackend.probe_capability()`は、`ModelDefinition`と設定済みContext Sizeから値を計算するだけである。

Preflight時点では次を行っていない。

- Artifact存在確認
- Artifact Size確認
- Artifact SHA-512確認
- GGUF Open
- Embedded Chat Template確認
- Role固有Manifest完全性確認
- Metal／CPU上の実Load確認
- 実Inference確認

これらは後続`load()`またはさらに後の実Inferenceで初めて発生する。したがって現Preflightは「Authority＋Registry Definition＋静的Capability計算」であり、名称、Comment、Recovery ClaimおよびAcceptance Evidenceを実装どおりに訂正する必要がある。

## 5. Qwen3Guard Source-level到達性

Qwen3Guardについては、本Reviewで次を確認した。

- 公式Contract ManifestはExact Revision付きで完全状態。
- Local GGUFには`tokenizer.chat_template`が存在する。
- Embedded TemplateにQwen3Guard固有`# Task:`が含まれる。
- Production AdapterはUser-onlyまたはUser＋Assistant Messageを渡し、GGUF Embedded Templateを共通Llama.cpp経路で適用する。
- Strict Decoderは公式`Safety／Categories／Refusal`形状を処理する。

したがってSource-level wiringはSeleneより成立度が高い。ただしReal Artifact Load／Registry Digest一致／実Inference／Evidence／OFF後Unloadはまだ実行していないため、Phase 9-1 Closure条件は未成立のままである。

## 6. Review 2結論

Review 1の合格判定では検出されなかったCritical 1件、Major 1件を検出した。Phase 9-1は、少なくともP9-CODEX-006／007のReworkと、Selene／Qwen3Guard両方のReal Production Smokeが終わるまでComplete Candidateへ戻してはならない。
