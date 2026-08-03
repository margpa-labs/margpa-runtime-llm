# 実装担当向け Phase 1-ex Mac限定簡易Documentation RAG Multi-turn Grounding Safety Follow-up Handoff

```yaml
document_id: implementer_handoff_phase_1_ex_mac_local_documentation_rag_multi_turn_grounding_follow_up
phase: phase_1_ex
status: accepted_ready_for_implementation
language: ja
created_at: 2026-07-31 23:19:40 JST
owner: 設計統括者役
target_role: 実装者役
source_manual_evidence: ../operations/mac_local_documentation_rag_manual_test_1_findings_20260731231940.md
source_review: designer_review_phase_1_ex_mac_local_documentation_rag_manual_test_1_20260731231940.md
source_requirements: ../requirements/mac_local_documentation_rag_multi_turn_grounding_follow_up_requirements_20260731231940.md
source_architecture: ../architecture/mac_local_documentation_rag_multi_turn_grounding_follow_up_architecture_20260731231940.md
manual_acceptance_after_follow_up: pending_designer_re_review
```

## 1. Objective

現行Documentation RAGを作り直さず、一回目の実GGUF Manual Testで確認されたF8～F12だけを解消する。

```text
F8:
  UTF-8 byte based prompt token estimation

F9:
  retrieval-hit / no-context fail-open generation

F10:
  multiple identifier coverage gap

F11:
  citation-to-answer grounding and prior-assistant contamination

F12:
  no-hit / context-insufficient UI ambiguity
```

## 2. Authoritative References

必ずRead-onlyで次を読む。

1. [Manual Test 1 Findings](../operations/mac_local_documentation_rag_manual_test_1_findings_20260731231940.md)
2. [Manual Test 1 Designer Review](designer_review_phase_1_ex_mac_local_documentation_rag_manual_test_1_20260731231940.md)
3. [Follow-up Requirements](../requirements/mac_local_documentation_rag_multi_turn_grounding_follow_up_requirements_20260731231940.md)
4. [Follow-up Architecture](../architecture/mac_local_documentation_rag_multi_turn_grounding_follow_up_architecture_20260731231940.md)
5. [Accepted Documentation RAG Requirements](../../requirements/mac_local_documentation_rag_requirements_ja.md)
6. [Accepted Documentation RAG Architecture](../../architecture/mac_local_documentation_rag_architecture_ja.md)
7. [ADR-0028](../../adr/adr_0028_mac_local_sparse_documentation_rag_and_external_adapter_hook_ja.md)
8. [Documentation Rules](../../../../shared/conventions/documentation_rules_ja.md)
9. [Task Role Authority](../../../../shared/task_roles/task_role_write_authority_policy_ja.md)
10. [Research Asset Mutation Control](../../../../shared/operations/research_asset_mutation_control_ja.md)

## 3. Authorized Mutation Scope

本Follow-upの必須差分に限り、次を変更可能とする。

```text
src/margpa_runtime_llm/modules/inference/ports/
src/margpa_runtime_llm/modules/inference/application/
src/margpa_runtime_llm/adapters/model_backends/llama_cpp/
src/margpa_runtime_llm/modules/conversation/
src/margpa_runtime_llm/modules/documentation_rag/
src/margpa_runtime_llm/adapters/documentation_rag/
src/margpa_runtime_llm/bootstrap/
src/margpa_runtime_llm/web/static/

tests/unit/inference/
tests/unit/conversation/
tests/unit/documentation_rag/
tests/unit/web/
tests/integration/documentation_rag/
tests/integration/web/
tests/integration/llama_cpp/
```

実装Statusのみ新規追加できる。

```text
docs/project/phases/phase_1_ex/history/handoffs/
  implementer_status_phase_1_ex_mac_local_documentation_rag_multi_turn_grounding_follow_up_YYYYMMDDHHMMSS.md
```

次は変更しない。

```text
config/
pyproject.toml
uv.lock
README.md
docs/public/
docs/project/current/
docs/project/shared/
Accepted Stable Requirements／Architecture／ADR
Phase Index
Existing History
Model Artifact
Lightning Scripts／Profiles
Public Demo Profiles
```

Config変更が不可欠と判断した場合は、変更前に理由、対象Key、互換性、Default値、RollbackおよびTestをStatusではなく設計統括者役へEscalateする。

## 4. Pre-mutation Gate

1. Project Root外を走査、作成、変更または削除しない。
2. `models` Symbolic Linkを追跡しない。
3. 変更予定Fileを先に列挙する。
4. 各変更対象のBefore SHA-512を取得する。
5. Existing Changeと衝突しないことを確認する。
6. Git／GitHub／Network／Lightning／External Service操作を行わない。
7. Dependency InstallまたはModel Downloadを行わない。
8. 既存Local Web Processを勝手に停止、KillまたはRestartしない。
9. Manual Acceptanceを実施済みと記録しない。

## 5. Required Implementation

### 5.1 Exact Chat Prompt Token Counter

- Optional Narrow Portを追加する。
- llama.cppの既存Chat Template `format_prompt(...).token_count`と同じPathを使う。
- `thinking_mode`を含む実生成と同じFormattingを使う。
- Inference Service経由で提供し、BootstrapからConversation Serviceへ注入する。
- Conversation ServiceはUTF-8 Byte推定をExactとして使わない。
- Existing Documentation Block Token Counterと二重Model Loadせず、同じLoad済みModelを使う。

### 5.2 Dynamic Budget

Accepted公式を実Tokenで解決する。

```text
loaded context
- exact base chat prompt
- requested max new tokens
- safety margin
= available documentation tokens
```

`requested_max_new_tokens=2048`を勝手に下げない。実余力がない場合は設定を黙って変更せず、Fail-closed Stateを返す。

### 5.3 Fail Closed

Retriever Hit後にAssembled Blockが0件なら：

```text
should_generate = false
model call = zero
safe warning = documentation_context_budget_insufficient
```

No Hitとは別Contractにする。

### 5.4 Multi-identifier Coverage

- Generic IdentifierごとにHeading／Path Exact Match候補を優先する。
- Capacity内ならDistinct Identifierごと1 Definition候補をCoverageする。
- General List DocumentのBody Matchだけで全Subject Coverage済みにしない。
- Existing BM25 Score、Corpus Priority、Document DiversityおよびTie-breakを維持する。
- Algorithm Versionを更新する。
- Project固有語Hard-codeを行わない。

### 5.5 Grounding Instruction

System-owned Reference Instructionに、次の意味を追加する。

```text
Project-specific formal names and relations require current reference evidence.
Previous assistant messages are not project authority.
Do not infer acronym expansions absent from references.
State insufficient evidence when requested subjects are uncovered.
```

Docs本文がRuntime Policyまたは権限を生成しない現行境界を弱化しない。

### 5.6 UI／Event

- No Hitは「Docsに対応根拠なし」。
- Context不足は「根拠を取得したがContext余力不足で使用不可」。
- Context不足時は通常回答を表示しない。
- 日本語／英語のUI Messageを同時に定義する。
- Citation 0件という表示だけで原因を隠さない。

## 6. Mandatory Regression Fixtures

### 6.1 Multi-turn Japanese Fixture

1回目のAssistantに十分長い日本語回答を入れ、2回目／3回目のRAG Queryを実行する。

```text
Exact room remains:
  citation continues

True room exhausted:
  fail closed
  inference stream not called
```

UTF-8 Byte推定だと2回目が失敗するFixtureにする。

### 6.2 Combined Subject Noisy Corpus

```text
Query:
  EASA + DLAGSA + OCILNS natural Japanese question

Corpus:
  each canonical definition
  general document listing all names
  polite Japanese distractors

Expected:
  each subject covered in top_k=4
  deterministic repeated result
```

Fixtureの定義はCanonical Docsと同じ意味にし、略称から創作しない。

### 6.3 Grounding Boundary Fixture

- Previous AssistantがARGDとEASAの虚偽の関係を記述する。
- Current ReferenceはARGDのCanonicalだけを持つ。
- System ReferenceがPrevious AssistantをAuthorityとしない指示を含む。
- TestはPrompt Compositionの不変条件を確認し、Model品質をUnit Testで偽らない。

### 6.4 Existing Boundaries

次を回帰する。

```text
Summary retrieve once
Stop during cold retrieval
New Chat
Browser Reload returns RAG OFF
Model Busy
Docs Missing fixture
Empty Corpus
No Hit
Public Demo RAG denied
Basic Preview unavailable／eligible boundary
No absolute path
No raw docs in evidence
```

## 7. Required Verification

```bash
./.venv/bin/pytest -q tests/unit/documentation_rag
./.venv/bin/pytest -q tests/integration/documentation_rag
./.venv/bin/pytest -q tests/unit/inference
./.venv/bin/pytest -q tests/unit/conversation
./.venv/bin/pytest -q tests/unit/web
./.venv/bin/pytest -q tests/integration/web/test_web_app.py
./.venv/bin/pytest -q
./.venv/bin/ruff check .
./.venv/bin/ruff format --check .
./.venv/bin/mypy .
node --check src/margpa_runtime_llm/web/static/app.js
```

Model Smokeは、既存Local Web Modelが常駐中なら二重Loadしない。実施できない場合は理由をStatusに正確に記録する。

## 8. Real Corpus Read-only Smoke

Model生成なしで次を取得する。

```text
individual:
  EASA
  ARGD
  DLAGSA

combined:
  EASA + DLAGSA + OCILNS

multi-turn budget simulation:
  long Japanese previous assistant message
  current ARGD or DLAGSA query
```

StatusにPath、Heading、Subject Coverage、Prompt Measurement値、Documentation BudgetおよびGeneration Allowed／Deniedを記録する。Raw Docs本文、Absolute Pathまたは個人情報を記録しない。

## 9. Prohibited Actions

- `max_new_tokens`のDefaultを下げるだけで対処しない。
- `context_size`、`top_k`またはSafety MarginのConfig変更だけで対処しない。
- EASA、DLAGSA、OCILNS、ARGDまたはDAGDをProduction CodeへHard-codeしない。
- Judge／Repair／ARGD／DAGD Runtimeを追加しない。
- Embedding、Vector DB、Persistent IndexまたはNew Dependencyを追加しない。
- Public Demo／LightningでRAGを有効化しない。
- Accepted Stable Docs、Current、Shared、PublicまたはPhase Indexを変更しない。
- User Manual Acceptanceを実施済みと記録しない。
- Scope外Refactor、Rename、MoveまたはCleanupを行わない。

## 10. Implementer Status

新規Append-only Statusに次を含める。

```text
F8～F12 before／after
changed files
before／after SHA-512
exact prompt measurement contract
multi-turn fixture result
combined subject coverage result
fail-closed inference call evidence
UI state separation
real corpus read-only result
target／full／static verification
model smoke performed or exact reason not performed
remaining limitations
manual acceptance not performed
```

## 11. Next Gate

実装担当Status提出後、設計統括者役がF8～F12、Regression、Real Corpus、Fail-closedおよびGrounding Contractを再Reviewする。

再ReviewがGOとするまで、ユーザーManual Acceptanceを再開しない。
