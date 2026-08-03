# 実装担当向け Phase 1-ex Mac限定簡易Documentation RAG Context Fallback Follow-up Handoff

```yaml
document_id: implementer_handoff_phase_1_ex_mac_local_documentation_rag_context_fallback_follow_up
phase: phase_1_ex
status: accepted_ready_for_implementation
language: ja
created_at: 2026-07-31 19:32:04 JST
owner: 設計統括者役
target_role: 実装者役
source_review: designer_review_phase_1_ex_mac_local_documentation_rag_correctness_follow_up_20260731193204.md
supersedes: null
manual_acceptance_after_follow_up: pending_re_review
implementation_environment: local_macos_arm64
```

## 1. Objective

Correctness Follow-upで解消したF1、F3およびF4を維持し、F2に残るProduction Context Fallbackの単位不整合と実効性不足だけを解消する。

```text
Preserve:
  Request-specific dynamic token budget
  Safety margin
  Minimum useful boundary
  Backend final context validation
  No arbitrary chunk truncation
  System-owned references and citations

Resolve:
  Token／Character／UTF-8 Byte unit mismatch
  Default short-query citation starvation
```

新しい検索技術、Embedding、Dependency、Model、Persistent Index、Public Demo RAGまたはLightning RAGを追加しない。

## 2. Authoritative References

必ずRead-onlyで次を参照する。

1. [本Follow-upの設計統括者Review](designer_review_phase_1_ex_mac_local_documentation_rag_correctness_follow_up_20260731193204.md)
2. [Correctness Follow-up実装者Status](implementer_status_phase_1_ex_mac_local_documentation_rag_correctness_follow_up_20260731191521.md)
3. [初回Review](designer_review_phase_1_ex_mac_local_documentation_rag_20260731184134.md)
4. [Accepted Requirements](../../requirements/mac_local_documentation_rag_requirements_ja.md)
5. [Accepted Architecture](../../architecture/mac_local_documentation_rag_architecture_ja.md)
6. [Accepted ADR-0028](../../adr/adr_0028_mac_local_sparse_documentation_rag_and_external_adapter_hook_ja.md)
7. [Documentation Rules](../../../../shared/conventions/documentation_rules_ja.md)
8. [Task Role／Write Authority](../../../../shared/task_roles/task_role_write_authority_policy_ja.md)
9. [Research Asset Mutation Control](../../../../shared/operations/research_asset_mutation_control_ja.md)

Conflict時：

```text
User Latest Explicit Instruction
  → Accepted ADR／Requirements
  → Accepted Architecture
  → This Follow-up Handoff
  → Earlier Handoffs
  → Older Documents
```

## 3. Authorized Mutation Scope

残存F2の解消とTestに必要な最小差分だけを変更できる。

```text
src/margpa_runtime_llm/modules/documentation_rag/
src/margpa_runtime_llm/adapters/documentation_rag/
src/margpa_runtime_llm/modules/inference/
src/margpa_runtime_llm/adapters/model_backends/llama_cpp/
src/margpa_runtime_llm/modules/conversation/
src/margpa_runtime_llm/bootstrap/
src/margpa_runtime_llm/entrypoints/web/

tests/unit/documentation_rag/
tests/unit/inference/
tests/unit/conversation/
tests/unit/web/
tests/integration/web/

docs/project/phases/phase_1_ex/history/handoffs/
  implementer_status_phase_1_ex_mac_local_documentation_rag_context_fallback_follow_up_YYYYMMDDHHMMSS.md
```

具体llama.cpp型をDocumentation Domainへ持ち込まない。Inference側を変更する場合は、Token計測専用の狭いPort／CallableをAdapterまたはComposition Rootから注入するために必要な最小変更だけとする。

次は変更しない。

```text
pyproject.toml
uv.lock
config/application.toml
config/models/
config/profiles/
config/web_profiles/
scripts/runtime/lightning/
README.md
docs/public/
docs/project/current/
docs/project/shared/
Accepted ADR／Requirements／Architecture
Phase Index
Existing History
Model Artifact
```

## 4. Pre-mutation Gate

1. Project Rootだけを対象にする。
2. Project Root外を走査、作成、変更または削除しない。
3. `models` Symbolic Linkを追跡しない。
4. 変更予定Fileを先に列挙する。
5. Existing Changeとの衝突を確認する。
6. 変更対象のBefore SHA-512をStatus用に取得する。
7. `.venv/`、Model、Cache、SecretまたはCredentialを変更しない。
8. Git、GitHub、LightningまたはNetwork操作を行わない。
9. Dependency InstallまたはModel Downloadを行わない。
10. 実Projectの`docs/`を移動、改名、削除または一時退避しない。

## 5. Required Implementation

### 5.1 Unit Contractを一致させる

次を混同しない。

```text
maximum_tokens:
  Main Model Contextに対するToken Budget

fallback_maximum_characters:
  Exact Token Counterがない場合のCharacter Budget

UTF-8 bytes:
  CharacterでもModel Tokenでもない別単位
```

- `fallback_maximum_characters`を`effective_tokens`へ無条件に`min`して、同数Byteとして扱わない。
- Contract名、設定値、計測方法およびEvidenceの単位を一致させる。
- `context_used`がToken数かFallback単位かを既存`token_budget_used`等で明確に区別する。
- 既定値`768 tokens`と`2,400 characters`の意味を壊さない。

### 5.2 Productionへ実効的かつ安全な計測をBindingする

推奨は、既にLoad済みのMain Backend／Tokenizerから、TextのToken数を返す狭いPortまたはCallableをComposition Rootへ公開し、`BoundedDocumentationContextAssembler`へ注入する構成である。

要件：

- Modelを二重Loadしない。
- 追加Modelを常駐させない。
- RAGごとにModel Fileを再Openしない。
- 新Dependencyを追加しない。
- llama.cpp固有型をDocumentation Domainへ漏らさない。
- Token Counterが利用できないRuntimeでもFail Closedまたは明確なFallbackを維持する。
- Count失敗時にRaw Text、Absolute Pathまたは秘密情報をErrorへ出さない。
- CountingがGeneration Lock、CancellationおよびModel Lifecycleを破壊しない。

Exact Counterの接続が狭い変更で成立しない場合は、推測によるHidden Couplingを追加しない。Accepted要件と同等の安全性／実効性を持つFallback案、必要Contractおよび影響範囲をStatusへ記載して設計統括者役へ戻す。

### 5.3 Dynamic Safetyを維持する

次の式を維持する。

```text
request_available_rag_tokens
  = max(
      0,
      effective_context_size
      - requested_max_new_tokens
      - estimated_or_exact_system_history_current_prompt_tokens
      - safety_margin_tokens
    )

effective_rag_tokens
  = min(configured_maximum_rag_tokens, request_available_rag_tokens)
```

- History増加、`max_new_tokens`増加およびSafety Margin増加でBudgetが減ること。
- Available BudgetがMinimum Useful未満ならReference／Citationを生成しないこと。
- 採用済みChunk本文をBudgetへ合わせて無秩序に途中切断しないこと。
- Backendの最終Context Limit検査を維持すること。
- False Citationを生成しないこと。

### 5.4 Required Functional Fixtures

実Projectを変更せず、現実的な長さの日本語Markdown Chunkを持つTemporary／In-memory Fixtureを追加する。

最低条件：

```text
effective_context_size: 4096
requested_max_new_tokens: 2048
safety_margin_tokens: 512
configured maximum RAG tokens: 768
short user question／short history
```

次の質問区分ごとに、Retrieverが関連Chunkを返すFixtureを用意し、Context Assembly後に少なくとも1件のReference／Citationが残ることを固定する。

```text
Project overview
Roadmap progress
System Architecture
ARGD／DAGD
EASA
DLAGSA
OCILNS
```

Test DoubleのToken Counterを使ってよい。単に短いASCII 1文字Chunkだけで通さず、日本語本文、Reference Headerおよび非信頼資料Instructionを含む実用長で確認する。

追加で次を固定する。

```text
exact counter available:
  accepted reference tokens <= effective token budget

counter unavailable:
  documented fallback unit is honored
  overflow is not silently accepted

insufficient budget:
  no reference
  no citation
  safe warning
```

### 5.5 Scope Control

- Retriever Weight、BM25 Formula、Corpus PriorityまたはChunk Rankingを変更しない。
- Chunk Size Configを小さくして症状だけを隠さない。
- Context Limitを増やして症状だけを隠さない。
- `max_new_tokens`既定値を下げて症状だけを隠さない。
- Safety Marginを下げて症状だけを隠さない。

## 6. Prohibited Actions

- User Manual Acceptanceを実施済みと記録しない。
- 実GGUF Model Smokeを偽装しない。
- Model Artifactを変更、Copy、RenameまたはDownloadしない。
- 新Dependency、Embedding Model、Vector DBまたはPersistent Indexを追加しない。
- Public Demo／Basic PreviewでDocumentation Adapterを有効化しない。
- Accepted Design文書を修正しない。
- Scope外Refactor、File移動、RenameまたはCleanupをしない。
- Git操作、External Service変更またはProject Root外操作をしない。

## 7. Required Verification

最低限：

```bash
./.venv/bin/pytest -q tests/unit/documentation_rag
./.venv/bin/pytest -q tests/unit/inference
./.venv/bin/pytest -q tests/unit/conversation
./.venv/bin/pytest -q tests/unit/web/test_web_cli.py
./.venv/bin/pytest -q tests/unit/web/test_access_profiles.py
./.venv/bin/pytest -q tests/integration/web/test_web_app.py
./.venv/bin/pytest -q
./.venv/bin/ruff check .
./.venv/bin/ruff format --check .
./.venv/bin/mypy .
node --check src/margpa_runtime_llm/web/static/app.js
```

さらに、Required Functional Fixtures 7区分のReference／Citation件数とBudget使用量をStatusへ記録する。

Model Download、Dependency Install、実Project Docs MutationまたはLightning試験は行わない。

## 8. Required Status

新規Append-only Status：

```text
docs/project/phases/phase_1_ex/history/handoffs/
implementer_status_phase_1_ex_mac_local_documentation_rag_context_fallback_follow_up_YYYYMMDDHHMMSS.md
```

必須記載：

- Result／未完了事項。
- Unit mismatchのBefore／After。
- Exact CounterまたはFallbackのPort／Composition構造。
- Dynamic Safetyが維持されたEvidence。
- 7区分のFunctional Fixture結果。
- 変更File一覧とBefore／After SHA-512。
- 全Verification結果。
- 実GGUF／Browser Manual Acceptanceは未実施であること。
- Scope外操作をしていないこと。

既存Historyを編集しない。

## 9. Completion Gate

実装担当Status提出後、設計統括者役が再Reviewする。

Manual Local GGUF／Browser Acceptanceは、設計統括者役が次をすべて確認して明示的にGOとした後だけ行う。

```text
unit semantics coherent
required functional fixtures green
dynamic safety preserved
full regression green
no false citation
no context overflow regression
```
