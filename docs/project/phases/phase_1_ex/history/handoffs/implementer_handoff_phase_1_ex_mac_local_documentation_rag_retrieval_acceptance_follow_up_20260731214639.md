# 実装担当向け Phase 1-ex Mac限定簡易Documentation RAG Retrieval Acceptance Follow-up Handoff

```yaml
document_id: implementer_handoff_phase_1_ex_mac_local_documentation_rag_retrieval_acceptance_follow_up
phase: phase_1_ex
status: accepted_ready_for_implementation
language: ja
created_at: 2026-07-31 21:46:39 JST
owner: 設計統括者役
target_role: 実装者役
source_review: designer_review_phase_1_ex_mac_local_documentation_rag_context_fallback_follow_up_20260731214639.md
supersedes: null
manual_acceptance_after_follow_up: pending_re_review
implementation_environment: local_macos_arm64
```

## 1. Objective

Context Fallback Follow-upで成立したExact Token Counter、Dynamic BudgetおよびContext Safetyを維持し、Accepted Manual Acceptanceを妨げる次の3件だけを解消する。

```text
F5:
  Natural-language lexical query relevance

F6:
  Canonical semantic integrity of R&D fixtures

F7:
  Measurement unit evidence coherence
```

新Dependency、Embedding、Vector DB、Persistent Index、Corpus追加、Public Demo RAGまたはLightning RAGを追加しない。

## 2. Authoritative References

必ずRead-onlyで次を参照する。

1. [本Follow-upの設計統括者Review](designer_review_phase_1_ex_mac_local_documentation_rag_context_fallback_follow_up_20260731214639.md)
2. [Context Fallback実装者Status](implementer_status_phase_1_ex_mac_local_documentation_rag_context_fallback_follow_up_20260731212414.md)
3. [Context Fallback Handoff](implementer_handoff_phase_1_ex_mac_local_documentation_rag_context_fallback_follow_up_20260731193204.md)
4. [Accepted Requirements](../../requirements/mac_local_documentation_rag_requirements_ja.md)
5. [Accepted Architecture](../../architecture/mac_local_documentation_rag_architecture_ja.md)
6. [Accepted ADR-0028](../../adr/adr_0028_mac_local_sparse_documentation_rag_and_external_adapter_hook_ja.md)
7. [Current Runtime Governance](../../../../current/governance/runtime_governance_specification_ja.md)
8. [Current Project Continuity](../../../../current/project_continuity/project_continuity_master_ja.md)
9. [Public Concept](../../../../../public/concept_ja.md)
10. [Documentation Rules](../../../../shared/conventions/documentation_rules_ja.md)
11. [Task Role／Write Authority](../../../../shared/task_roles/task_role_write_authority_policy_ja.md)
12. [Research Asset Mutation Control](../../../../shared/operations/research_asset_mutation_control_ja.md)

固有名称の意味はCurrent Canonical／Public Canonicalを正本とする。略称から意味を推測しない。

## 3. Authorized Mutation Scope

F5～F7とTestに必要な最小差分だけを変更できる。

```text
src/margpa_runtime_llm/modules/documentation_rag/
src/margpa_runtime_llm/adapters/documentation_rag/
src/margpa_runtime_llm/bootstrap/documentation_rag.py

tests/unit/documentation_rag/
tests/integration/documentation_rag/

docs/project/phases/phase_1_ex/history/handoffs/
  implementer_status_phase_1_ex_mac_local_documentation_rag_retrieval_acceptance_follow_up_YYYYMMDDHHMMSS.md
```

必要なPort／Contract伝播Testに限り、次を最小変更できる。

```text
tests/unit/conversation/
tests/unit/web/
tests/integration/web/
```

次は変更しない。

```text
pyproject.toml
uv.lock
config/application.toml
config/models/
config/profiles/
config/web_profiles/
config/feature_profiles/
src/margpa_runtime_llm/modules/conversation/
src/margpa_runtime_llm/modules/inference/
src/margpa_runtime_llm/adapters/model_backends/
src/margpa_runtime_llm/web/
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

## 5. F5 Required Implementation

### 5.1 Natural-language Query Signal

次のような自然文でもSubjectを維持する。

```text
roadmapの現在の進捗を教えてください
ARGDとDAGDについて説明してください
EASAとは何ですか？
DLAGSAとは何ですか？
OCILNSとは何ですか？
システムArchitectureを説明してください
```

Production Codeへ`roadmap`、`ARGD`、`DAGD`、`EASA`、`DLAGSA`または`OCILNS`の固定語一覧を追加してはならない。

一般則の候補：

- Latin／Identifier TokenのExact Coverageを高Signalとして扱う。
- Heading／PathのIdentifier Exact Matchを自然文の一般N-gramより優先する。
- 日本語の質問定型表現を検索Subjectと同じ重みで大量加算しない。
- Query AnalyzerをRetrieverと分離し、将来交換可能にする。
- Query全体を捨てず、Subject Signalと補助Context Signalを区別する。

実装方式は上記を満たす範囲で実装担当が選べる。ただし特定Project名称に依存しない。

### 5.2 Ranking Contract

- BM25のDF修正を維持する。
- Body／Heading／Path／Exact Phrase／Corpus Priority／Document Diversityを維持する。
- No Hit、Minimum ScoreおよびTie-breakを壊さない。
- 同一Corpus、Query、ConfigおよびImplementation Versionで同一結果を返す。
- Tokenizer、Query AnalyzerまたはRetriever Algorithmを変更した場合、該当Versionを更新して旧Index Cacheと分離する。
- Query Frequencyを使う場合、丁寧表現の反復SignalがIdentifierを埋没させないことをTestする。

### 5.3 Required Noisy-corpus Fixtures

Temporary／In-memory Corpusへ、正本Chunkと多数の無関係な日本語文書を同時に置く。

最低条件：

```text
Natural polite query
Canonical subject chunk
Irrelevant chunks containing common polite／explanatory Japanese n-grams
Top K = production default
```

次を固定する。

```text
Roadmap natural query:
  top-ranked citation is Roadmap／current-progress source

ARGD／DAGD natural query:
  top-ranked citation is ARGD／DAGD canonical definition

EASA／DLAGSA／OCILNS natural query:
  top-ranked citation is the matching canonical definition

Architecture natural query:
  top-ranked citation is system architecture source

Project overview:
  existing behavior remains relevant
```

単に対象Documentだけを一件置くFixtureでは不十分である。

### 5.4 Real Corpus Read-only Smoke

実Project Docsを変更せず、Model生成なしで現在のAllowlist Corpusを検索し、StatusへPath／Headingを記録する。

最低合格条件：

```text
roadmapの現在の進捗を教えてください:
  docs/public/roadmap_ja.mdの現在地／進捗相当Chunkを含む

ARGDとDAGDについて説明してください:
  Current GovernanceまたはPhase 1 Governance Catalogの定義Chunkを含む

EASA／DLAGSA／OCILNS:
  各Canonical／Catalog定義Chunkを含む

Architecture:
  System Architecture文書を含む
```

高Signal Identifier質問では、無関係なUser ManualまたはLanguage Smokeだけが定義Chunkより上位を占めないこと。

実GGUF Model Generationは行わない。Model Tokenizerを使う必要はなく、Retrieval結果だけを確認してよい。

## 6. F6 Required Implementation

`test_realistic_japanese_corpus_yields_citation_with_default_context_budget`等のFixture本文を、Current Canonical／Phase 1 Governance Catalogと同じ意味へ修正する。

必須意味：

```text
ARGD:
  Premise、Context、矛盾、情報不足、根拠、反証、代替仮説、表現、Drift、Repair

DAGD:
  Policy Goal、Constraint、Capability、Evaluation、Severity、Audit、Repair、
  Activation、Self Audit、Audit-to-Action、Status Reporting

EASA:
  内部安全傾向、周辺安全制御、入力文脈、生成過程およびComposite Safety Behavior
  単一物理Layerを断定しない

DLAGSA:
  複数の判断・実行・検証主体間の責任、委譲、例外、改竄耐性付き証跡、
  全体整合および異常時安全側制御

OCILNS:
  人、AI、Tool、外部System間の認知対話を、
  検証・参照・継承・監査可能な改竄耐性付き証跡単位として扱う台帳網
```

研究の非公開Algorithmや未開示Protocolを追加しない。正本を変に要約、再解釈または創作しない。

## 7. F7 Required Implementation

Block単位とContext単位の計測値を、単位ごとに真実に記録する。

必須条件：

- Unicode Character数を`estimated_tokens`として格納しない。
- Exact Token Counter使用時はToken単位と判別できる。
- Counter未設定、未Bindingまたは失敗後のCharacter Fallbackは、すべてFallback使用と判別できる。
- `context_used`、Block計測値およびBudgetの単位をEvidenceから一意に解決できる。
- Existing UI／Citationへ不要な内部情報を追加しない。
- Raw Reference本文、Absolute PathまたはModel固有ObjectをEvidenceへ追加しない。

Contract変更時は、Pydantic不変条件と既存Serialization Testを更新する。

## 8. Must Preserve

```text
Exact loaded-model token counter
No second model load
Dynamic context formula
Safety margin
Minimum useful boundary
Backend final context validation
No arbitrary chunk truncation
System-owned untrusted reference
System-generated citations
RAG default OFF
Mac-only adapter binding
Basic Preview unavailable
Public Demo denied
Summary retrieve-once
Cancellation／Model Busy／New Chat
```

## 9. Prohibited Actions

- User Manual Acceptanceを実施済みと記録しない。
- 実GGUF Model Generationを行わない。
- Domain固有略称またはPathをProduction CodeへHard-codeしない。
- New Dependency、Morphological Analyzer、Embedding Model、Vector DBまたはPersistent Indexを追加しない。
- Corpus Allowlistを拡張しない。
- Configの`top_k`、Context Size、Chunk Size、`max_new_tokens`またはSafety Margin変更だけで症状を隠さない。
- Public Demo／Basic PreviewでDocumentation Adapterを有効化しない。
- Accepted Design文書を修正しない。
- Scope外Refactor、File移動、RenameまたはCleanupをしない。
- Git操作、External Service変更またはProject Root外操作をしない。

## 10. Required Verification

最低限：

```bash
./.venv/bin/pytest -q tests/unit/documentation_rag
./.venv/bin/pytest -q tests/integration/documentation_rag
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

加えてReal Corpus Read-only SmokeのQuery、選択PathおよびHeadingをStatusへ記録する。

## 11. Required Status

新規Append-only Status：

```text
docs/project/phases/phase_1_ex/history/handoffs/
implementer_status_phase_1_ex_mac_local_documentation_rag_retrieval_acceptance_follow_up_YYYYMMDDHHMMSS.md
```

必須記載：

- Result／未完了事項。
- F5 Query Signal／RankingのBefore／After。
- Production CodeにDomain固有語をHard-codeしていないEvidence。
- Tokenizer／Query Analyzer／Retriever Version変更。
- F6 Fixture定義と参照したCanonical箇所。
- F7 Measurement Unit Contract。
- Noisy-corpus Fixture結果。
- Real Corpus Read-only SmokeのPath／Heading。
- 変更File一覧とBefore／After SHA-512。
- 全Verification結果。
- 実GGUF Generation／Browser Manual Acceptanceは未実施であること。
- Scope外操作をしていないこと。

既存Historyを編集しない。

## 12. Completion Gate

実装担当Status提出後、設計統括者役が再Reviewする。

Manual Local GGUF／Browser Acceptanceは、設計統括者役が次をすべて確認して明示的にGOとした後だけ行う。

```text
natural-language retrieval relevance green
canonical semantic fixtures green
measurement unit evidence coherent
exact token budget preserved
full regression green
no false citation
no context overflow regression
```
