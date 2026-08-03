# 実装担当向け Phase 1-ex Mac限定簡易Documentation RAG Coverage Integrity Follow-up Handoff

```yaml
document_id: implementer_handoff_phase_1_ex_mac_local_documentation_rag_coverage_integrity_follow_up
phase: phase_1_ex
status: accepted_ready_for_implementation
language: ja
created_at: 2026-08-01 00:36:25 JST
owner: 設計統括者役
target_role: 実装者役
source_review: designer_review_phase_1_ex_mac_local_documentation_rag_multi_turn_grounding_follow_up_20260801003625.md
reviewed_status: implementer_status_phase_1_ex_mac_local_documentation_rag_multi_turn_grounding_follow_up_20260801001058.md
manual_acceptance_after_follow_up: pending_designer_re_review
```

## 1. Objective

F8、F9、F11およびF12のAccepted部分を維持し、再Reviewで確認したF13／F14だけを修正する。

```text
F13:
  Retrieval Coverageと実Assembled Reference Coverageの不一致

F14:
  通常の英語文章TokenをHigh-signal Identifier Subjectとして扱う誤分類
```

本Follow-upはRetrieval件数を増やす作業ではない。Modelが実際に受け取ったReferenceと、Coverage、Citation、Grounding DecisionおよびEvidenceを一致させる作業である。

## 2. Authoritative References

必ずRead-onlyで次を読む。

1. [Coverage Integrity Review](designer_review_phase_1_ex_mac_local_documentation_rag_multi_turn_grounding_follow_up_20260801003625.md)
2. [Implementer Status](implementer_status_phase_1_ex_mac_local_documentation_rag_multi_turn_grounding_follow_up_20260801001058.md)
3. [Manual Test 1 Findings](../operations/mac_local_documentation_rag_manual_test_1_findings_20260731231940.md)
4. [Multi-turn Follow-up Requirements](../requirements/mac_local_documentation_rag_multi_turn_grounding_follow_up_requirements_20260731231940.md)
5. [Multi-turn Follow-up Architecture](../architecture/mac_local_documentation_rag_multi_turn_grounding_follow_up_architecture_20260731231940.md)
6. [ADR-0028](../../adr/adr_0028_mac_local_sparse_documentation_rag_and_external_adapter_hook_ja.md)
7. [Documentation Rules](../../../../shared/conventions/documentation_rules_ja.md)
8. [Task Role Authority](../../../../shared/task_roles/task_role_write_authority_policy_ja.md)
9. [Research Asset Mutation Control](../../../../shared/operations/research_asset_mutation_control_ja.md)

## 3. Authorized Mutation Scope

F13／F14に必要な最小差分に限り、次を変更可能とする。

```text
src/margpa_runtime_llm/modules/documentation_rag/
src/margpa_runtime_llm/adapters/documentation_rag/
src/margpa_runtime_llm/modules/conversation/
src/margpa_runtime_llm/web/static/

tests/unit/documentation_rag/
tests/unit/conversation/
tests/unit/web/
tests/integration/documentation_rag/
tests/integration/web/
```

実装上不可欠な場合に限り、既存Narrow Portの接続Testを変更できる。Inference／llama.cpp Adapter本体を変更する必要がある場合は、先に設計統括者役へEscalateする。

実装Statusのみ新規追加できる。

```text
docs/project/phases/phase_1_ex/history/handoffs/
  implementer_status_phase_1_ex_mac_local_documentation_rag_coverage_integrity_follow_up_YYYYMMDDHHMMSS.md
```

次を変更しない。

```text
config/
pyproject.toml
uv.lock
README.md
docs/public/
docs/project/current/
docs/project/shared/
Accepted Stable Requirements／Architecture／Governance／ADR
Phase Index
Existing History
Model Artifact
Lightning Scripts／Profiles
Public Demo Profiles
```

## 4. Required Implementation

### 4.1 High-signal Identifier Classification

通常のLatin文章Tokenと、Coverage対象のHigh-signal Identifier Subjectを分離する。

必須条件：

- Project固有語Allowlistを使用しない。
- NFKCおよびCase-insensitive Retrievalは維持する。
- Original Surfaceの大文字略称、数字／Separator／Code-like形状、Heading／Path Exact Evidenceなど、一般化可能なSignalを使う。
- `What`、`are`、`and`、`Explain`、`briefly`等の通常文章がCoverage Slotを消費しない。
- 通常語はLexical Retrieval Signalとして残せるが、Subject Coverage Slotとは分離する。
- EASA、DLAGSA、OCILNS以外の未知Identifierでも同じ一般則で動く。

実装方法は固定しない。ただし英語Stopwordの追加だけを主解決にせず、未知Language／未知Domainでも不必要な誤分類を抑える構造を優先する。

Tokenizer／Analyzerの意味が変わる場合はVersionを更新し、Cache Keyを分離する。

### 4.2 Per-subject Coverage Trace

RetrieverからAssemblerまで、どのSelected ChunkがどのHigh-signal SubjectをCoverageするかをTransient Contractで保持する。

```text
query subject
→ candidate chunk
→ retrieved selection
→ assembled reference block
→ system citation
→ evidence count
```

Raw Query、Raw DocsまたはAbsolute PathをEvidenceへ追加しない。Subject文字列自体を永続Evidenceへ残す必要はなく、Count／DigestまたはTransient Mappingでよい。

### 4.3 Assembled Coverage Integrity

最終の`covered_subject_count`／`uncovered_subject_count`は、少なくともModel Promptへ実際に入ったReference Block集合と一致させる。

Pre-assembly Retrieval Coverageを残す場合は、Field名と意味を分離する。

```text
retrieval_covered_subject_count
assembled_covered_subject_count
```

のように、同じFieldへ異なるStageの値を混在させない。

Citation、Assembled Block Count、Grounding StateおよびGeneration Decisionは同じAssembled Reference Setから導出する。

### 4.4 Partial Subject Fail-closed

複数High-signal Subjectが質問され、各Subjectの有効候補をRetrieverが取得したにもかかわらず、Context Budgetにより一部しかPromptへ入らない場合、全Subject Coverage済みとしてModelを呼ばない。

初期Safe Contract：

```text
requested high-signal subjects > 1
retrieval has valid candidate for each subject
assembled coverage < required subject coverage

should_generate:
  false

model call:
  zero

safe reason:
  documentation_context_budget_insufficient
  または、明確に分離したdocumentation_subject_coverage_insufficient
```

新しいSafe Codeを採用する場合は、日本語／英語UI Message、Event Testおよび既存Client互換性を同時に追加する。

一部回答を許可する新Contractは、本Follow-upで黙って採用しない。必要なら設計統括者役へEscalateする。

### 4.5 Missing Subject Boundary

複数Subject Queryで一部SubjectだけCorpus根拠がない場合、残りSubjectのReferenceだけで全質問へGrounded Answerを生成しない。

少なくとも次を区別する。

```text
all requested high-signal subjects grounded:
  generation allowed

some requested high-signal subjects missing or not assembled:
  fail closed with coverage reason

true query-wide no hit:
  existing ungrounded general chat boundary
```

### 4.6 Preserve F8／F9／F11／F12

- Exact Chat Prompt Token Counterを維持する。
- Zero Assembled BlockのModel Call 0回を維持する。
- Previous Assistant非Authority Instructionを維持する。
- No Hit、Context不足、UnavailableおよびDeniedの状態分離を維持する。
- Public DemoではDocumentation RAGをDeniedのままにする。

## 5. Mandatory Regression Fixtures

### 5.1 Japanese Combined Subject

```text
Query:
  EASAとは何ですか？ DLAGSAとは何ですか？ OCILNSとは何ですか？

Expected with sufficient room:
  subject count = 3
  actual assembled coverage = 3
  citations cover 3 subjects
  generation allowed
```

### 5.2 English Combined Subject with Prose Noise

```text
Query:
  What are EASA, DLAGSA, and OCILNS?

Noise:
  headings／paths／bodies containing What, Are, And, Explain, Briefly

Expected:
  high-signal subject count = 3
  EASA／DLAGSA／OCILNS selected
  ordinary prose consumes zero coverage slots
```

未知の大文字Identifier 3件でも同じTestを追加し、Project固有Hard-codeがないことを確認する。

### 5.3 Partial Assembly

3 SubjectすべてをRetrieverがCoverageするが、Budgetには1～2 Subject分しか入らないFixtureを作る。

```text
retrieval coverage:
  3／3

assembled coverage:
  less than 3／3

generation:
  denied

inference stream call:
  zero

false full-coverage evidence:
  prohibited
```

### 5.4 Missing Subject

3 Subject Queryに対し2 SubjectのCanonicalだけをCorpusへ置く。

```text
grounded generation for all three:
  prohibited

missing coverage:
  explicit in safe state／evidence
```

### 5.5 Existing Regression

```text
Exact Prompt Measurement
long Japanese Multi-turn
true Budget Exhaustion
single Subject Grounding
true No Hit
Docs Missing／Empty Corpus
Summary retrieve once
Stop／New Chat／Reload／Model Busy
Public Demo RAG Denial
no absolute path／no raw docs evidence
```

## 6. Required Verification

```bash
./.venv/bin/pytest -q tests/unit/documentation_rag
./.venv/bin/pytest -q tests/integration/documentation_rag
./.venv/bin/pytest -q tests/unit/conversation
./.venv/bin/pytest -q tests/unit/web
./.venv/bin/pytest -q tests/integration/web/test_web_app.py
./.venv/bin/pytest -q
./.venv/bin/ruff check .
./.venv/bin/ruff format --check .
./.venv/bin/mypy .
node --check src/margpa_runtime_llm/web/static/app.js
```

## 7. Status Requirements

新しいAppend-only Statusに次を含める。

```text
F13／F14 before／after
changed files
before／after SHA-512
high-signal classification rule
English prose-noise result
Japanese combined-subject result
retrieval versus assembled coverage evidence
partial assembly inference call count
missing-subject state
production project-term hard-code scan
target／full／static verification
real corpus read-only result
manual GGUF acceptance not performed
remaining limitations
```

## 8. Prohibited Actions

- EASA、DLAGSA、OCILNS、ARGD、DAGDその他Project固有語をProduction CodeへHard-codeしない。
- `top_k`、Context Size、`max_new_tokens`、Chunk SizeまたはSafety MarginのConfig変更だけで回避しない。
- Partial Subject回答を新しいAccepted挙動として黙って導入しない。
- ARGD／DAGD Runtime、Judge、Repair、EmbeddingまたはVector DBを追加しない。
- Existing Local Web Processを停止、KillまたはRestartしない。
- Modelを二重Loadしない。
- Git／GitHub／Network／Lightning／External Serviceを操作しない。
- Accepted Stable Docs、Current、Shared、Public、Phase Indexまたは既存Historyを変更しない。
- Manual Acceptanceを実施済みと記録しない。

## 9. Next Gate

実装担当Status提出後、設計統括者役がF13／F14、既存F8～F12、Artifact SHA、RegressionおよびReal Corpusを再Reviewする。

再ReviewがGOとするまで、ユーザーManual Acceptanceは再開しない。
