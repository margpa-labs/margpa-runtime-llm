# 設計統括者Review：Phase 1-ex Mac限定簡易Documentation RAG Context Fallback Follow-up

```yaml
document_id: designer_review_phase_1_ex_mac_local_documentation_rag_context_fallback_follow_up
phase: phase_1_ex
status: changes_required_before_manual_acceptance
language: ja
created_at: 2026-07-31 21:46:39 JST
owner: 設計統括者役
source_review: designer_review_phase_1_ex_mac_local_documentation_rag_correctness_follow_up_20260731193204.md
reviewed_status: implementer_status_phase_1_ex_mac_local_documentation_rag_context_fallback_follow_up_20260731212414.md
follow_up_handoff: implementer_handoff_phase_1_ex_mac_local_documentation_rag_retrieval_acceptance_follow_up_20260731214639.md
manual_acceptance_gate: no_go
supersedes_review: designer_review_phase_1_ex_mac_local_documentation_rag_correctness_follow_up_20260731193204.md
```

## 1. Review結論

```text
Context Fallback Unit Blocker:
  RESOLVED

Loaded Main Tokenizer Binding:
  ACCEPTED

Dynamic Context Safety:
  ACCEPTED

Repository Automated Verification:
  GREEN

Real Corpus Context Assembly:
  TOKEN BUDGET GREEN
  RETRIEVAL RELEVANCE CHANGES REQUIRED

Manual Local GGUF／Browser Acceptance:
  NO_GO
```

前回確認したToken、Unicode CharacterおよびUTF-8 Byteの単位混同は解消した。Local Mac Production Compositionでは、既にLoad済みのMain Model Tokenizerを狭い`TextTokenCounterPort`経由でBindingし、Model二重Load、Model File再Open、新DependencyおよびDocumentation Domainへのllama.cpp型漏出を生じさせていない。

実Project CorpusとLocal Qwen3 Tokenizerを使ったModel非生成Smokeでも、取得したReferenceは768 Token上限へ収まり、Context Fallbackの実効性は確認できた。

一方、Accepted Manual Acceptanceで使用する自然な日本語質問では、丁寧表現の日本語N-gramが高SignalのLatin Identifier／Path／Headingより強くScoreへ寄与する。Roadmap進捗およびARGD／DAGD質問で、正本定義を一件も取得せず無関係なPhase 1文書だけを選択した。

Citationが存在するだけでは、該当質問の根拠取得に成功したことにならない。現在の状態でModel Manual Acceptanceを行うと、誤った根拠による回答または根拠不足回答を、RAG成功と誤認するため、手動試験へはまだ進めない。

## 2. Accepted Implementation

### 2.1 Exact Token Counter

- `TextTokenCounterPort`はBackend非依存の狭いOptional Protocolである。
- `InferenceService`がOptional Capabilityを公開する。
- `LlamaCppModelAdapter`は既存Load済みChat Template／Tokenizerを使う。
- Non-blocking Generation Lockで同時Generationと競合させない。
- Unloaded／Busy／Counter Failureを安全なErrorへ変換する。
- Deferred CounterはWeb RuntimeのModel Load完了後にBindingされる。
- Basic Preview、Public DemoおよびLightningへDocumentation AdapterをBindingしない。

### 2.2 Unit Coherence

```text
maximum_tokens:
  dynamic Main Model token budget

fallback_maximum_characters:
  Unicode character budget

UTF-8 bytes:
  corpus file-size boundary only
```

Resolverは`fallback_maximum_characters`をToken数へ縮めなくなった。Exact Counter時はToken Budget、Fallback時はUnicode Character Budgetで計測する。

### 2.3 Dynamic Safety

- Effective Context、Requested Generation、Prompt／History EstimateおよびSafety Marginを動的Budgetへ反映する。
- Minimum Useful未満ではReference／Citationを構成しない。
- Exact Counter時のReferenceはEffective RAG Token Budget以下である。
- 採用済みChunkを途中切断しない。
- Backend最終Context Limit検査を維持する。
- Contextから除外したChunkのFalse Citationを生成しない。

## 3. Independent Verification

設計統括者役が独立再実行した。

```text
Combined Required Target Suite:
  256 passed in 3.72s

Repository Full Suite:
  386 passed
  3 deselected
  49.61s

Ruff Check:
  PASS

Ruff Format Check:
  PASS／119 files

Mypy:
  PASS／119 source files

JavaScript Syntax:
  PASS
```

実装者Statusに列挙された変更FileのAfter SHA-512は、Review時の実Fileと一致した。

## 4. Real Corpus Exact-token Smoke

条件：

```text
Corpus:
  current Local Documentation RAG allowlist

effective_context_size:
  4096

requested_max_new_tokens:
  2048

prompt/history estimate:
  300

safety_margin_tokens:
  512

effective RAG budget:
  768

counter:
  Local Qwen3 GGUF tokenizer／read-only／no generation
```

Token Budget結果：

| 質問区分 | Citation | Used／Budget | Token計測 |
|---|---:|---:|---|
| Project概要 | 4 | 615／768 | Exact |
| Roadmap進捗 | 4 | 621／768 | Exact |
| Architecture | 3 | 678／768 | Exact |
| ARGD／DAGD | 3 | 649／768 | Exact |
| EASA | 4 | 743／768 | Exact |
| DLAGSA | 3 | 590／768 | Exact |
| OCILNS | 3 | 574／768 | Exact |

全区分でReferenceがToken Budget内へ収まった。前回のContext Citation Starvationは解消している。

## 5. Blocking Finding

### F5. 自然な日本語質問で高Signal Identifierより丁寧表現N-gramが優先される

Severity: High／Manual Acceptance Blocking

対象：

```text
src/margpa_runtime_llm/adapters/documentation_rag/lexical_tokenizer.py
src/margpa_runtime_llm/adapters/documentation_rag/bm25_retriever.py
```

Accepted Manual Acceptanceは、少なくともRoadmap進捗、Architectureおよび英語略称質問を含む。

実Corpusで次を実行した。

```text
roadmapの現在の進捗を教えてください
```

取得結果：

```text
1. Phase 1-D Native Metal／Language Smoke
2. Phase 1-D Native Metal／Language Smoke
3. Phase 1-D Japanese Response Instruction
4. Phase 1-D Japanese Response Instruction
```

`docs/public/roadmap_ja.md`の「現在地」またはRoadmap本文は一件も取得されなかった。

次も同様である。

```text
ARGDとDAGDについて説明してください
```

取得結果：

```text
1. docs/public/roadmap_ja.md／Roadmap変更規則
2. Phase 1 Requirements／旧Documentation Snapshot断片
3. Phase 1 Requirements／旧Documentation Snapshot断片
```

`runtime_governance_specification_ja.md`のARGD／DAGD定義、またはPhase 1 Governance Catalogを取得していない。

対照として、短い高Signal Queryでは正本を取得できる。

```text
roadmap
  -> docs/public/roadmap_ja.md

Roadmap進捗
  -> docs/public/roadmap_ja.md

ARGD DAGD
  -> docs/project/current/governance/runtime_governance_specification_ja.md

DLAGSA
  -> Phase 1 Governance Catalog／Project Continuity／Current Governance

OCILNS
  -> Phase 1 Architecture／Governance／Current Governance
```

したがってCorpus不足ではなく、自然文QueryのSignal抽出／Weighting不足である。質問末尾の「について説明してください」「とは何ですか」「を教えてください」等から生成される多数の日本語2-gram／3-gramが、Latin Identifier、PathおよびHeadingの一致を上回る。

Required：

- Domain固有略称をHard-codeせず、高Signal Latin／Identifier Tokenを一般則で優先する。
- 日本語の質問定型表現が検索Subjectを埋没させないQuery Analysisを追加する。
- `roadmap`、`ARGD`、`DAGD`等をProduction Codeの固定語一覧へ入れない。
- Identifier、Path、Heading、Phrase、Corpus PriorityおよびDocument Diversityの既存責務を維持する。
- 同じCorpus、Query、ConfigおよびVersionでDeterministicにする。
- Algorithm／Tokenizer挙動を変更した場合はVersionを更新してIndex Cacheを分離する。
- 自然文QueryでTop-ranked Referenceが質問Subjectの正本またはCatalogになるFixtureを追加する。

## 6. Required Semantic Finding

### F6. Functional Fixtureが固有R&D名称を誤定義している

Severity: Moderate／Required Before Acceptance

対象：

```text
tests/unit/documentation_rag/test_context_citation_and_orchestrator.py:640-687
```

追加FixtureはCitation生存確認用でありRuntime Corpusへ混入しない。しかし、Project固有名称を実際と異なる意味へ再定義している。

例：

```text
Fixture EASA:
  EvidenceとAuditの受入境界

Canonical EASA:
  Model内部安全傾向、周辺安全制御および入力文脈／生成過程から現れる
  Composite Safety Behaviorを扱う例外認識型安全統治機構

Fixture DLAGSA:
  Guard／Judge／Repairの責務と状態遷移

Canonical DLAGSA:
  複数の判断・実行・検証主体間における責任、委譲、例外、
  改竄耐性付き証跡、全体整合および異常時安全側制御

Fixture OCILNS:
  Context／Instruction／Lifecycle／Namespaceの安全境界

Canonical OCILNS:
  人、AI、Tool、外部System間の認知対話を、
  検証・参照・継承・監査可能な改竄耐性付き証跡単位として扱う台帳網
```

ARGD／DAGD Fixtureも正本より粗く、意味が異なる。

Test Dataであっても、固有研究名称の意味を推測、創作または再定義しない。Fixture本文はCurrent CanonicalまたはPhase 1 Governance Catalogの公開定義と一致させる。

## 7. Evidence Semantics Observation

### F7. Fallback時にも`estimated_tokens`へCharacter数を格納する

Severity: Moderate／Required Follow-up

対象：

```text
src/margpa_runtime_llm/modules/documentation_rag/contracts.py:154-161
src/margpa_runtime_llm/adapters/documentation_rag/bounded_context_assembler.py:79-87
```

Exact Counter時の`DocumentationReferenceBlock.estimated_tokens`はToken数である。一方、Fallback時は`len(text)`のUnicode Character数が同じFieldへ入る。

Context全体は`context_token_budget_used`と`token_counter_fallback_used`で区別できるが、Block単位Field名はTokenと断定しており、値の単位が一致しない。また、最初からCounter未設定の場合はCharacter Fallbackを使っても`token_counter_fallback_used = false`となる。

Required：

- Block単位の計測値と単位を明示し、Character数を`estimated_tokens`と記録しない。
- Counterが未Binding／未設定／失敗のどの場合も、実際に使った計測ModeをEvidenceから一意に判定可能にする。
- 現在のUIへRaw内容または内部Pathを追加しない。

本FindingはContext Overflowを直接発生させないが、将来Audit／EvaluationがToken Costを誤読するため、Unit Coherence Follow-upの完了条件に含める。

## 8. Authority Boundary

```text
Retrieval Acceptance Follow-up:
  AUTHORIZED BY ATTACHED HANDOFF

Manual Local GGUF／Browser Acceptance:
  DENIED UNTIL NEXT RE-REVIEW

New Dependency／Embedding／Persistent Index:
  DENIED

Domain-specific Acronym Hard-code:
  DENIED

Corpus Scope Expansion:
  DENIED

Lightning／Public Demo RAG:
  DENIED

Git／GitHub／Project Root Outside Operation:
  DENIED
```

## 9. Next Gate

実装担当はRetrieval Acceptance Follow-up Handoffに従い、F5～F7だけを解消して新しいAppend-only Statusを提出する。

設計統括者役が自然文Queryの実Corpus Retrieval、固有名称の意味保全、Evidence単位、Context Safetyおよび全Regressionを再Reviewし、Manual Acceptance GOを明示するまで、ユーザーのLocal GGUF／Browser試験へ進まない。
