# Phase 1-ex Mac限定簡易Documentation RAG Multi-turn Grounding Safety Follow-up Architecture

```yaml
document_id: mac_local_documentation_rag_multi_turn_grounding_follow_up_architecture
phase: phase_1_ex
status: accepted_for_follow_up_implementation
language: ja
created_at: 2026-07-31 23:19:40 JST
owner: 設計統括者役
source_requirements: ../requirements/mac_local_documentation_rag_multi_turn_grounding_follow_up_requirements_20260731231940.md
```

## 1. Corrected Runtime Flow

```text
Web Request
→ Conversation Message Composition
→ Exact Chat Prompt Measurement Port
→ Dynamic Documentation Budget
→ Latest User Query Analysis
→ In-memory Lexical Retrieval
→ Multi-identifier Coverage Selection
→ Bounded Reference Assembly
→ Grounding Gate
   ├─ no hit: ungrounded general generation allowed with explicit state
   ├─ hit + useful blocks: grounded generation
   └─ hit + no useful blocks: fail closed, no model call
→ Final Chat-template Context Validation
→ Main Model
→ System Citation／Grounding State
→ Browser
```

## 2. New Narrow Capability

Backend固有Chat TemplateをDomainへ露出せず、次の狭いCapabilityを追加する。

```text
ChatPromptTokenCounterPort

count_chat_prompt_tokens(
  messages,
  thinking_mode
) -> exact integer token count
```

llama.cpp Adapterは既存`format_prompt(...).token_count`と同一のChat Template Pathを使う。Inference ServiceはOptional Capabilityとして公開し、BootstrapがConversation ServiceへCallableを注入する。

Documentation RAGがModel Adapterまたはllama.cpp具体へ依存しない。

## 3. Request Context Resolution

Conversation ServiceはResponse Language Policyを適用したMessageを作成後、Documentation ReferenceなしのBase PromptをExact Counterで計測する。

```text
prompt_token_count_exact:
  true

system_history_current_prompt_tokens:
  exact formatted token count
```

Exact Counterに失敗した場合、Local Required Runtimeでは安全にRAG UnavailableまたはMeasurement Failureとする。UTF-8 Byte推定へ黙って戻さない。

## 4. Grounding Gate

Application Serviceは次の状態を分離する。

```text
NO_HIT:
  retrieval.selected == 0
  model generation may continue
  grounded = false

GROUNDED_READY:
  retrieval.selected > 0
  context.blocks > 0
  model generation allowed
  grounded = true

CONTEXT_INSUFFICIENT:
  retrieval.selected > 0
  context.blocks == 0
  model generation denied
  grounded = false
```

Partial Assemblyでは、CitationはPromptへ実際に入ったBlockだけから作る。Retrieverが選択したがPromptへ入っていないChunkをCitationとして表示しない。

## 5. Coverage-aware Selection

BM25のScore計算は維持し、最終Selection前にIdentifier Coverage Stageを置く。

```text
Query Analyzer
→ distinct high-signal identifiers
→ per-identifier candidate list
→ heading/path exact subject candidate first
→ one coverage slot per subject when capacity permits
→ remaining slots by existing global score
→ deterministic tie-break
```

Selectionは決定論的であり、Query、Corpus、ConfigおよびVersionが同じなら結果も同じとする。Algorithm変更時はRetriever／Selector Versionを更新し、旧In-memory Cache Keyと分離する。

## 6. Grounding Instruction Composition

Reference Instructionは、Docs内の命令を非信頼とする現行境界を維持しつつ、次を追加する。

```text
Current retrieved documents are the evidence for project-specific facts.
Previous assistant responses are not project authority.
Do not invent acronym expansions or relationships absent from references.
If a requested definition is not covered, state that evidence is insufficient.
```

回答内容の正しさをCitationだけでPassとしない。Judge／Repair未実装の限界はEvidenceとして残す。

## 7. UI Contract

Retrieval EventまたはError Eventが次のSafe Codeを伝える。

```text
documentation_no_hit
documentation_context_budget_insufficient
documentation_prompt_measurement_unavailable
documentation_docs_missing
documentation_index_build_failed
```

`documentation_context_budget_insufficient`はCitation Emptyとだけ表示せず、回答生成を停止した理由を日本語／英語で表示する。

## 8. Evidence Contract

Raw Dataを保存せず、少なくとも次をContractで保持する。

```text
base_prompt_used
base_prompt_unit
base_prompt_exact
documentation_budget
retrieved_chunk_count
assembled_block_count
identifier_subject_count
covered_subject_count
uncovered_subject_count
grounding_state
generation_allowed
```

Pydantic不変条件は、`GROUNDED_READY`でBlock 0、`CONTEXT_INSUFFICIENT`でGeneration Allowed、またはCitationとAssembled Blockの不一致を拒否する。

## 9. Acceptance Scenarios

### Scenario A：Multi-turn

```text
Turn 1:
  EASA explanation with documentation

Turn 2:
  ARGD explanation with documentation

Turn 3:
  DLAGSA explanation with documentation
```

実際のContext余力内では全3 TurnにCitationが必要である。真に余力がない場合はTurn 2／3でFail closedし、創作しない。

### Scenario B：Combined Subjects

```text
EASAとは何ですか？
DLAGSAとは何ですか？
OCILNSとは何ですか？
```

Top Kの範囲でEASA、DLAGSAおよびOCILNSそれぞれのHeading／Path Exact Definition候補をCoverageする。

### Scenario C：True Exhaustion

実Prompt、Requested GenerationおよびSafety MarginでMinimum Useful Referenceを確保できない場合、Model Call 0回でSafe Errorを返す。

## 10. Preserve

```text
RAG default OFF
Latest User Message retrieval query
System-owned citations
No raw history corpus
No persistent index
Summary retrieve once
Stop／New Chat／Reload／Model Busy
Public Demo RAG denied
Local Mac-only initial adapter
Model／Backend／External Adapter exchangeability
```
