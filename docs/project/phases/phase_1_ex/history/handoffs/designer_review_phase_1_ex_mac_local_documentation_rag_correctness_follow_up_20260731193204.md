# 設計統括者Review：Phase 1-ex Mac限定簡易Documentation RAG Correctness Follow-up

```yaml
document_id: designer_review_phase_1_ex_mac_local_documentation_rag_correctness_follow_up
phase: phase_1_ex
status: changes_required_before_manual_acceptance
language: ja
created_at: 2026-07-31 19:32:04 JST
owner: 設計統括者役
source_review: designer_review_phase_1_ex_mac_local_documentation_rag_20260731184134.md
reviewed_status: implementer_status_phase_1_ex_mac_local_documentation_rag_correctness_follow_up_20260731191521.md
follow_up_handoff: implementer_handoff_phase_1_ex_mac_local_documentation_rag_context_fallback_follow_up_20260731193204.md
manual_acceptance_gate: no_go
supersedes_review: designer_review_phase_1_ex_mac_local_documentation_rag_20260731184134.md
```

## 1. Review結論

```text
Repository Automated Verification:
  GREEN

F1 BM25 Document Frequency:
  RESOLVED

F2 Dynamic Request Context Budget:
  PARTIALLY RESOLVED／ONE BLOCKER REMAINS

F3 Empty Valid Corpus Boundary:
  RESOLVED

F4 Local Mac Host Eligibility:
  RESOLVED

Manual Model／Browser Acceptance:
  NO_GO

Required Next Action:
  NARROW CONTEXT FALLBACK FOLLOW-UP
```

初回Reviewで確認した4件のうち、F1、F3およびF4はAccepted要件どおり解消した。F2もRequest単位のContext情報、動的Budget式、Safety Margin、Minimum Useful境界およびBackend最終Context検査まで接続されている。

一方、Production CompositionでExact Token CounterをBindingせず、Fallbackの「文字数」をUTF-8 Byte数として計測したうえ、その上限をToken数へ縮めている。この単位不整合により、通常の既定値でも取得済みChunkがすべて除外され、Accepted Manual Acceptanceの主要質問でCitation 0件となる。

安全側に倒れる挙動ではあるが、Local Mac Documentation RAGとして必要なProject説明機能を成立させないため、ユーザーの実Model／Browser Manual Acceptanceへはまだ進めない。

## 2. Reviewed Scope

主に次を確認した。

```text
implementer_status_phase_1_ex_mac_local_documentation_rag_correctness_follow_up_20260731191521.md

src/margpa_runtime_llm/adapters/documentation_rag/
src/margpa_runtime_llm/modules/documentation_rag/
src/margpa_runtime_llm/modules/conversation/
src/margpa_runtime_llm/bootstrap/
src/margpa_runtime_llm/entrypoints/web/

tests/unit/documentation_rag/
tests/unit/conversation/
tests/unit/web/
tests/integration/web/

Accepted Requirements／Architecture／ADR-0028
Initial Review／Correctness Follow-up Handoff
```

実装者Statusに列挙された変更FileのAfter SHA-512は、Review時の実Fileと一致した。

## 3. Resolved Findings

### 3.1 F1：BM25 Document Frequency

Status: RESOLVED

- Body、HeadingおよびPathのDFは各ChunkにつきToken Keyを1回だけ加算する。
- `df <= population`を英語反復Tokenと日本語反復N-gramで固定している。
- Retriever Versionを`2`へ更新し、旧Cacheとの混在を防止している。
- 独立再現は次となった。

```text
population = 2
df(test) = 1
selected = 1
retriever_version = 2
```

### 3.2 F3：Empty Valid Corpus Boundary

Status: RESOLVED

- Manifest後の二回目Readで有効Document 0件をUnavailableとする。
- Chunk 0件もUnavailableとする。
- Empty IndexをAtomic Storeへ公開しない。
- Partial Failureで有効Documentが残る場合だけDegraded継続する。
- `document_count`を実際の有効Document／Indexへ合わせている。

### 3.3 F4：Local Mac Host Eligibility

Status: RESOLVED

- Local ExposureだけではMac AdapterをBindingしない。
- Darwin／ARM64をComposition Rootで確認する。
- Linux／Windows Local、Basic PreviewおよびPublic DemoでMac Adapterを構築しない。
- OS固有分岐をDocumentation Domainへ持ち込んでいない。

## 4. Partially Resolved Finding

### F2：Dynamic Budgetは接続済みだがFallbackの単位が不整合

Severity: High／Manual Acceptance Blocking

対象：

```text
src/margpa_runtime_llm/modules/documentation_rag/application/documentation_rag.py:407-430
src/margpa_runtime_llm/adapters/documentation_rag/bounded_context_assembler.py:27-96
src/margpa_runtime_llm/bootstrap/documentation_rag.py:45-80
```

Accepted Requirementsは次を別単位として定義する。

```text
maximum_rag_context_tokens: 768 tokens
fallback_maximum_rag_characters: 2,400 characters
```

現在のResolverは次を行う。

```text
fallback_characters
  = min(configured_fallback_characters, effective_rag_tokens)
```

既定の正常Budgetでは、`min(2400, 768) = 768`となる。その後、AssemblerはFallbackをUnicode文字数ではなくUTF-8 Byte数で計測する。

```text
configured fallback: 2,400 characters
effective production fallback: 768 UTF-8 bytes
```

日本語本文では1文字が複数Byteとなるため、Reference Headerと非信頼資料Instructionを含めると、通常のChunkが1件も入らない場合が多い。`fallback_maximum_characters`というContract名、Accepted設定値および実測単位が一致していない。

これはContext Overflowを起こさない点では安全だが、機能要件を満たさない。Backendの最終Context Limit検査が残ることだけでは、RAGが正常に根拠を供給できることの代替にならない。

## 5. Real Corpus Model-free Smoke

Production Composition、実Projectの許可Corpus、既定Web条件を用い、Model生成を行わずRetrieval／Context Assembly／Citationまで確認した。

条件：

```text
effective_context_size: 4096
requested_max_new_tokens: 2048
short-prompt conservative estimate: 300
safety_margin_tokens: 512
effective_rag_budget: 768
production context assembler: no exact token counter
```

結果：

```text
MARGPA Runtime LLMとは何ですか？
  selected chunks: 1
  citations: 1

ARGDとDAGDについて説明してください
  selected chunks: 0
  citations: 0
  warning: documentation_context_budget_insufficient

EASAとは何ですか？
  selected chunks: 0
  citations: 0
  warning: documentation_context_budget_insufficient

roadmapの現在の進捗を教えてください
  selected chunks: 1
  citations: 1

システムArchitectureを説明してください
  selected chunks: 0
  citations: 0

DLAGSAとは何ですか？
  selected chunks: 0
  citations: 0

OCILNSとは何ですか？
  selected chunks: 0
  citations: 0
```

Accepted Manual AcceptanceはProject概要、Roadmap進捗、Architectureおよび英語略称質問を最低限含む。上記はその主要区分を満たさない。

## 6. Exact Token Counter Comparison

原因分離のため、Local Qwen3 GGUFのTokenizerを読み取り専用で使用し、同じRetrieval結果へExact Token Counterだけを一時的に注入して比較した。Model生成、File変更およびDownloadは行っていない。

```text
ARGD／DAGD:
  citations 3／used 649 tokens

EASA:
  citations 4／used 743 tokens

MARGPA Runtime LLM:
  citations 4／used 603 tokens

Architecture:
  citations 3／used 678 tokens

DLAGSA:
  citations 3／used 590 tokens

OCILNS:
  citations 3／used 574 tokens
```

すべて768 Token内へ収まる。したがって根本原因はRetrieverのNo HitでもRAG Token Budget不足でもなく、Production FallbackがToken BudgetをByte Budgetへ縮めることにある。

## 7. Independent Verification

設計統括者役が再実行した。

```text
Specified Target Suite:
  102 passed in 1.39s

Repository Full Suite:
  371 passed
  3 deselected
  49.43s

Ruff Check:
  PASS

Ruff Format Check:
  PASS／119 files

Mypy:
  PASS／119 source files

JavaScript Syntax:
  PASS
```

Automated SuiteがGreenでも、実Corpusの長い日本語ChunkとProduction Fallbackの組合せを固定するTestがないため、本Findingを検出できていない。

## 8. Required Resolution

新しい限定Handoffに従い、次だけを解消する。

1. TokenとCharacter／Byteの単位を混同しない。
2. 動的Token Budget、Safety Margin、Minimum Useful境界およびBackend最終検査を維持する。
3. Local Mac Production Compositionへ安全なExact Token CounterをBindingするか、同等の安全性と実効性を持つ明確なFallbackを構成する。
4. 既定4096 Context／2048 Outputの短い質問で、必須質問区分に少なくとも1件のCitationを構成できることをTestする。
5. Chunk本文の無秩序な途中切断、False CitationおよびContext Overflowを導入しない。

Retrieval relevanceの精密評価は将来Evaluation対象であり、本Follow-upでは検索技術、WeightまたはCorpus Priorityを広く変更しない。ただし必須質問でCitation 0件となる現状は非ブロッカーではない。

## 9. Authority Boundary

```text
Context Fallback Follow-up:
  AUTHORIZED BY ATTACHED HANDOFF

Manual Local GGUF／Browser Acceptance:
  DENIED UNTIL NEXT RE-REVIEW

New Dependency／Embedding／Persistent Index:
  DENIED

Retrieval Algorithm／Corpus Scope Redesign:
  DENIED

Lightning／Public Demo RAG:
  DENIED

Git／GitHub／Project Root Outside Operation:
  DENIED
```

## 10. Next Gate

実装担当は限定Follow-up Handoffに従い、新しいAppend-only Statusを提出する。

設計統括者役がProduction Fallbackの実効性、Context Safetyおよび全Regressionを再Reviewし、Manual Acceptance GOを明示するまで、ユーザーのLocal GGUF／Browser試験へ進まない。
