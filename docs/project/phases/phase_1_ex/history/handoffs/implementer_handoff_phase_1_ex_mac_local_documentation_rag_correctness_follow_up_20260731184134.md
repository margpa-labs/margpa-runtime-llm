# 実装担当向け Phase 1-ex Mac限定簡易Documentation RAG Correctness Follow-up Handoff

```yaml
document_id: implementer_handoff_phase_1_ex_mac_local_documentation_rag_correctness_follow_up
phase: phase_1_ex
status: accepted_ready_for_implementation
language: ja
created_at: 2026-07-31 18:41:34 JST
owner: 設計統括者役
target_role: 実装者役
source_review: designer_review_phase_1_ex_mac_local_documentation_rag_20260731184134.md
supersedes: null
manual_acceptance_after_follow_up: pending_re_review
implementation_environment: local_macos_arm64
```

## 1. Objective

初回Mac限定簡易Documentation RAG実装の構造を維持し、設計統括者Reviewで確認された4件のCorrectness／Composition Findingだけを解消する。

```text
F1:
  BM25 Document Frequency Correctness

F2:
  Per-request Dynamic Context Budget／Safety Margin

F3:
  Empty Valid Corpus after Partial Read Failure

F4:
  Local Mac Runtime Eligibility
```

新しい検索技術、Embedding、Dependency、Model、Persistent Index、Public Demo RAGまたはLightning RAGを追加しない。

## 2. Authoritative References

必ずRead-onlyで次を参照する。

1. [設計統括者Review](designer_review_phase_1_ex_mac_local_documentation_rag_20260731184134.md)
2. [初回実装者Status](implementer_status_phase_1_ex_mac_local_documentation_rag_20260731174758.md)
3. [初回Accepted Handoff](implementer_handoff_phase_1_ex_mac_local_documentation_rag_20260731172259.md)
4. [Requirements](../../requirements/mac_local_documentation_rag_requirements_ja.md)
5. [Technology Selection](../../architecture/mac_local_documentation_rag_technology_selection_ja.md)
6. [Architecture](../../architecture/mac_local_documentation_rag_architecture_ja.md)
7. [ADR-0028](../../adr/adr_0028_mac_local_sparse_documentation_rag_and_external_adapter_hook_ja.md)
8. [Documentation Rules](../../../../shared/conventions/documentation_rules_ja.md)
9. [Task Role／Write Authority](../../../../shared/task_roles/task_role_write_authority_policy_ja.md)
10. [Research Asset Mutation Control](../../../../shared/operations/research_asset_mutation_control_ja.md)

Conflict時：

```text
User Latest Explicit Instruction
  → Accepted ADR／Requirements
  → Accepted Architecture
  → This Follow-up Handoff
  → Initial Handoff
  → Older Documents
```

## 3. Authorized Mutation Scope

F1～F4の解消とTestに必要な最小差分だけを変更できる。

```text
src/margpa_runtime_llm/modules/documentation_rag/
src/margpa_runtime_llm/adapters/documentation_rag/
src/margpa_runtime_llm/modules/conversation/
src/margpa_runtime_llm/bootstrap/
src/margpa_runtime_llm/entrypoints/web/

tests/unit/documentation_rag/
tests/unit/conversation/
tests/unit/web/
tests/integration/web/

docs/project/phases/phase_1_ex/history/handoffs/
  implementer_status_phase_1_ex_mac_local_documentation_rag_correctness_follow_up_YYYYMMDDHHMMSS.md
```

必要なContract値をFeature Profileへ追加・修正する場合に限り、次を最小変更できる。

```text
config/feature_profiles/documentation_rag_defaults.toml
config/feature_profiles/local_documentation_rag.toml
```

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

### 5.1 F1：BM25 DF

- Body／Heading／PathのDocument Frequencyを、Chunk内出現回数ではなくTokenを含むChunk数として計算する。
- `0 <= df <= population`を不変条件とする。
- Term Frequencyは各`IndexedChunk`内へ従来どおり保持する。
- IDF、BM25 Length Normalization、Field Weight、Exact Phrase、Corpus PriorityおよびTie-breakは変更しない。

Required Test：

```text
Repeated English Token:
  one chunk contains same token many times
  df remains 1
  matching chunk is retrieved

Repeated Japanese N-gram:
  same 2-gram／3-gram repeats in one chunk
  each df remains <= population
  matching chunk is retrieved

Existing Determinism／Diversity／No-hit:
  remains green
```

### 5.2 F2：Dynamic Context Budget

RAG Budgetを固定値だけで決めず、Requestごとに次を反映する。

```text
effective_context_size
  - requested_max_new_tokens
  - estimated_or_exact_system_history_current_prompt_tokens
  - safety_margin_tokens
  = request_available_rag_tokens

effective_rag_tokens
  = min(configured_maximum_rag_tokens, request_available_rag_tokens)
```

Contract要件：

- Conversationは具体Assemblerへ依存せず、RAG PortへRequest Context／Budget情報を渡す。
- Context Sizeは既存Runtime／DeploymentのEffective値を正本とする。
- `max_new_tokens`は当該Web RequestのEffective値を使う。
- Main Model Tokenizerを安全に呼べる場合はExact Token Countを優先する。
- Tokenizerを呼べない境界では、全History／System／User Messageを含む保守的Fallbackを使う。
- Configの`maximum_tokens`は動的上限を上書きせず、その範囲内のCapとする。
- Safety Marginを実計算で差し引く。
- Available値がMinimum Useful未満ならReferenceを注入しない。
- その場合はProject Docsに基づいたCitationを出さず、安全なWarning／Evidenceを返す。
- Backend側最終Context Limit検査を残す。

必要なら`RagOrchestratorPort.augment`へImmutableなRequest Context DTOを追加してよい。具体llama.cpp型、FastAPI型またはDOM型をDocumentation Domainへ持ち込まない。

Required Test：

```text
same query／same corpus:
  larger history -> smaller or equal RAG budget
  larger max_new_tokens -> smaller or equal RAG budget
  larger safety margin -> smaller or equal RAG budget

insufficient budget:
  no reference injection
  no false citation
  safe warning／state

normal budget:
  accepted chunks fit final effective budget
  final request remains within context limit

summary:
  retrieve once contract remains unchanged
```

既存BackendからExact Token Counterを安全に公開するためにPhase 1全体の広いInterface変更が必要な場合、Hidden couplingを追加しない。保守的Fallbackを成立させたうえで、Exact Counter HookをStatusへ明記するか、必要設計を報告して停止する。

### 5.3 F3：Empty Valid Corpus

- Manifestが非空でも、二回目Read後の有効Documentが0件ならUnavailableにする。
- Chunkが0件の場合もUnavailableにする。
- `should_generate = false`とし、RAG Model Callを開始しない。
- Empty IndexをStoreへReplaceしない。
- Partial Failureで有効Documentが残る場合だけDegraded継続する。
- `document_count`は、当該Index／Augmentationで実際に有効なDocument数を示す。
- ErrorへAbsolute PathまたはDocument本文を出さない。

Required Test：

- Manifest作成後、全Fileが変更されたSource Fixture。
- Manifest作成後、全Fileが読取不能になったSource Fixtureまたは同等Fake Port。
- 有効Documentが1件残るPartial Failure Fixture。
- Empty Index非公開の確認。

### 5.4 F4：Local Mac Eligibility

- `WebExposureMode.LOCAL`だけでMac Local AdapterをBindingしない。
- Web Access CapabilityとHost／Deployment EligibilityをComposition Rootで分けて解決する。
- Local Mac対象Profileでは既存Local AdapterをAvailableにする。
- Linux／Windows／External RuntimeではExternal Adapterが未登録ならUnavailableにする。
- Public DemoはDeniedかつAdapter非構築を維持する。
- Basic PreviewはEligibleかつInitial Adapter未Bindingを維持する。
- Documentation DomainへOS固有分岐を埋め込まない。

Required Test：

- macOS ARM64／Local：Local Adapter available。
- Linux x86_64／Local：Mac Adapter not bound／unavailable。
- Basic Preview：eligible／unavailable。
- Public Demo：denied／adapter factory not called。

## 6. Prohibited Actions

- User Manual Acceptanceを実施済みと記録しない。
- 実GGUF Model Smokeを偽装しない。
- 新Dependency、Embedding Model、Vector DBまたはPersistent Indexを追加しない。
- Public Demo／Basic PreviewでDocumentation Adapterを有効化しない。
- Accepted Design文書を修正しない。
- Scope外Refactor、File移動、RenameまたはCleanupをしない。
- Git操作、External Service変更またはProject Root外操作をしない。

## 7. Required Verification

最低限：

```bash
./.venv/bin/pytest -q tests/unit/documentation_rag
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

さらに、F1の反復語再現が修正後に取得成功となることを記録する。

Model Download、Dependency Install、実Project Docs MutationまたはLightning試験は行わない。

## 8. Required Status

新規Append-only Status：

```text
docs/project/phases/phase_1_ex/history/handoffs/
implementer_status_phase_1_ex_mac_local_documentation_rag_correctness_follow_up_YYYYMMDDHHMMSS.md
```

必須記載：

- Result／未完了事項。
- F1～F4ごとのBefore、修正内容、After Evidence。
- 変更File一覧。
- Before／After SHA-512。
- Request Budget計算式とFallback方式。
- Runtime Eligibility解決方法。
- Target／Full Suite／Ruff／Mypy／JS結果。
- 実GGUF／Browser Manual Acceptanceは未実施であること。
- Dependency／Model／Network／Lightning／Git／Project Root外操作なし。
- Scope外の観察事項。

## 9. Completion Boundary

実装担当Status提出だけではManual Acceptanceを許可しない。

設計統括者役がF1～F4、Source、Testおよび全Suiteを再Reviewし、`ACCEPTED_REPOSITORY_ONLY／MANUAL_ACCEPTANCE_GO`を明示した後に限り、ユーザーがLocal Mac上の実GGUF／Browser試験へ進む。
