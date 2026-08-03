# 設計統括者Review：Phase 1-ex Mac限定簡易Documentation RAG Manual Test 1

```yaml
document_id: designer_review_phase_1_ex_mac_local_documentation_rag_manual_test_1
phase: phase_1_ex
status: changes_required_manual_acceptance_no_go
language: ja
created_at: 2026-07-31 23:19:40 JST
owner: 設計統括者役
source_evidence: ../operations/mac_local_documentation_rag_manual_test_1_findings_20260731231940.md
supersedes_decision: designer_review_phase_1_ex_mac_local_documentation_rag_retrieval_acceptance_follow_up_20260731222302.md
manual_acceptance_gate: no_go
```

## 1. Decision

先行Reviewが示した「ユーザーManual Acceptanceへ進行可」は、実GGUF／BrowserのMulti-turn Evidenceにより取り消す。

```text
RAG Component Installation:
  ACCEPTED AS IMPLEMENTED STRUCTURE

Single-turn Retrieval:
  PARTIALLY ACCEPTED

Multi-turn Grounding:
  REJECTED

Manual Acceptance:
  FAIL／NO_GO

Next:
  Multi-turn Grounding Safety Follow-up
```

旧Review、旧Manual Handoffおよび旧IndexはAppend-only Historyとして保持し、編集または削除しない。最新Indexと本Reviewで現在Gateを示す。

## 2. Findings

### F8：Prompt Measurement Unit／Accuracy

```text
Severity:
  blocking

Observed:
  Japanese UTF-8 byte length is used as conservative prompt token estimate

Effect:
  first long Japanese answer consumes the estimated remaining context;
  later documentation budget becomes zero or below minimum useful size
```

### F9：Ungrounded Fail-open Generation

```text
Severity:
  blocking／safety boundary

Observed:
  retrieval can hit while assembled reference blocks are empty;
  generation still continues

Effect:
  RAG ON appears active while the model answers without documentation evidence
```

### F10：Multi-subject Identifier Coverage

```text
Severity:
  blocking for combined subject query

Observed:
  generic documents mentioning all identifiers occupy Top K;
  each canonical definition is not guaranteed

Effect:
  DLAGSA／OCILNS formal names are invented
```

### F11：Citation-to-answer Grounding／History Contamination

```text
Severity:
  blocking for project-specific factual explanation

Observed:
  ARGD citations are present, but the answer invents an expansion and an EASA relationship

Effect:
  citation presence can be mistaken for answer correctness;
  previous assistant hallucination contaminates the next subject
```

### F12：UI State Ambiguity

```text
Severity:
  required correction

Observed:
  no hit and context-budget exhaustion both appear as no references

Effect:
  user cannot distinguish absent evidence from discarded evidence
```

## 3. Review Correction

先行Reviewは次を確認したが、実Conversationの連続Turnを検査していなかった。

```text
single-query real-corpus retrieval
noisy-corpus ranking
measurement-unit serialization
full automated regression
```

これらは有効なEvidenceだが、Multi-turn Acceptanceの代替にはならない。後続Testに必ず日本語の長いAssistant回答を含む2～3 Turn以上を追加する。

## 4. Required Response

```text
F8:
  exact loaded-model chat prompt token measurement

F9:
  fail closed when retrieval hits but no useful reference can be assembled

F10:
  generic per-identifier canonical coverage for multi-subject queries

F11:
  stronger evidence-grounding and prior-assistant non-authority contract

F12:
  explicit no-hit versus context-insufficient UI state
```

`max_new_tokens`を512／1024へ下げること、`context_size`を8192へ上げること、`top_k`を増やすことのいずれかだけで解決済みとしてはならない。それらはTuning候補であり、Measurement、Fail-closedおよびCoverage Contractの代替ではない。

## 5. Authority

```text
Implement Multi-turn Grounding Safety Follow-up:
  AUTHORIZED BY ACCEPTED HANDOFF

Continue user manual acceptance before re-review:
  DENIED

ARGD／DAGD Runtime implementation in this follow-up:
  DENIED／NEXT SEPARATE SCOPE

New Model／Embedding／Vector DB／Dependency:
  DENIED

Public Demo／Lightning RAG:
  DENIED
```
