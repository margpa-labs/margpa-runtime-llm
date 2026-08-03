# Phase 1-ex Mac限定簡易Documentation RAG Multi-turn Grounding Safety Follow-up 要件

```yaml
document_id: mac_local_documentation_rag_multi_turn_grounding_follow_up_requirements
phase: phase_1_ex
status: accepted_for_follow_up_implementation
language: ja
created_at: 2026-07-31 23:19:40 JST
owner: 設計統括者役
source_evidence: ../operations/mac_local_documentation_rag_manual_test_1_findings_20260731231940.md
source_review: ../handoffs/designer_review_phase_1_ex_mac_local_documentation_rag_manual_test_1_20260731231940.md
```

## 1. Objective

既存Documentation RAGのSource、Chunk、Index、Retrieval、Citation、UIおよびAccess Profile構造を維持しながら、次を成立させる。

1. 日本語の長い回答後も、Contextに実際の余力がある限り次TurnでDocsを参照する。
2. 根拠がHitしたがPromptへ入れられない場合、RAG回答を装った無根拠生成を行わない。
3. 複数の高Signal Identifierを同時に質問した場合、各Subjectの定義候補を可能な範囲でCoverageする。
4. Citationの存在と回答の忠実性を混同せず、Project固有事実の創作を抑制する。
5. No Hit、Context不足、RAG UnavailableおよびRAG Deniedを別状態としてUI／Evidenceから識別できる。

## 2. Exact Prompt Measurement

### 2.1 Required Measurement

Local llama.cpp Runtimeでは、Load済みModelのChat TemplateおよびTokenizerが生成する実Prompt Token数を使う。

```text
Input:
  composed system messages
  conversation history
  current user message
  response-language instruction
  thinking mode affecting chat template

Output:
  exact formatted prompt token count
```

UTF-8 Byte数、Unicode Character数または固定係数の値を`exact tokens`として扱わない。

### 2.2 Portability

Prompt計測はllama.cpp固有ObjectをConversation Domainへ渡さない。Composition Rootから狭いCallable／Portを注入する。

BackendがExact Chat Prompt Counterを提供できない場合：

- Exactと偽らない。
- Fallback Unit／ModeをEvidenceで明示する。
- Local Documentation RAGのSafetyを保てない場合はFail closedにする。

### 2.3 Budget Formula

```text
available_documentation_tokens =
  loaded_context_size
  - exact_base_prompt_tokens
  - requested_max_new_tokens
  - safety_margin_tokens
```

`maximum_tokens`との小さい方をDocumentation Context Limitとする。Backendの最終Formatted Prompt Validationを維持する。

## 3. Fail-closed Grounding Boundary

### 3.1 Retrieval Hit／No Reference

```text
retrieval.selected > 0
and
assembled blocks == 0
```

の場合、次とする。

```text
should_generate:
  false

safe reason:
  documentation_context_budget_insufficient

model call:
  prohibited

user guidance:
  new chat, shorter requested output, or context availability adjustment
```

参照なしのModel生成をDocumentation Grounded Answerとして継続しない。

### 3.2 True No Hit

Corpus内に検索Hitがない場合は、Current Designの一般Chat継続を維持できる。ただしUIは「Docsに根拠なし」と明示し、Grounded Answerと表示しない。

## 4. Multi-subject Coverage

### 4.1 Generic Rule

Production CodeにEASA、DLAGSA、OCILNS、ARGD、DAGDその他Project固有語のAllowlistをHard-codeしない。

Query Analyzerが取得したDistinct High-signal Identifierごとに、次を優先する。

1. Heading Exact Identifier Match。
2. Path Component Exact Identifier Match。
3. BodyのSubject-specific Match。
4. 残り枠をOverall Rankingで補充。

Bodyに複数名を列挙しただけの一般文書一件を、全SubjectのDefinition Coverageと見なさない。

### 4.2 Capacity

Distinct Identifier数がTop K以内であり、各Identifierの有効な定義候補がCorpusにある場合、各Subjectを1件以上Coverageする。

Distinct Identifier数がCapacityを超える場合、黙って全て参照したことにしない。Coverage MetadataまたはSafe Warningで未Coverageを識別できるようにする。

## 5. Grounding Contract

System-owned Reference Instructionに次を明示する。

- Project固有の正式名称、略称展開、定義およびSystem間関係は参照文書を根拠とする。
- 参照文書にない略称展開をModel知識から創作しない。
- 現在のReferenceと矛盾する過去Assistant回答は正本ではない。
- 必要なDefinitionがReferenceになければ、不明／根拠不足と回答する。
- Citation存在だけで回答正しさを保証しない。

本Follow-upはJudge／Repair／ARGD／DAGD Runtimeを実装しない。ModelがInstructionを必ず守ると主張せず、実Model Manual Evidenceで限界を記録する。

## 6. UI／Evidence

UIは最低限次を区別する。

```text
No retrieval hit:
  参照対象のDocsに根拠が見つかりません。

Retrieval hit but no context budget:
  Context余力不足のため、取得したDocsを回答に使用できません。

Docs missing／unavailable:
  既定のSafe Message

Denied:
  Access Profileによる拒否
```

Evidenceは次を識別可能にする。

```text
base prompt measurement value／unit／exactness
resolved documentation budget
retrieval selected count
assembled block count
identifier subject count
covered subject count
uncovered subject count
generation allowed／denied reason
```

Raw Query、Raw Docs、Absolute Path、Model ObjectまたはSecretを追加保存しない。

## 7. Required Tests

1. Exact Chat Prompt CounterがLoad済みModel AdapterからCompositionされる。
2. 日本語文字列のUTF-8 Byte数をExact Token数として使わない。
3. 日本語の長いAssistant回答後の2～3 Turnで、実余力内ならCitationが継続する。
4. 真にBudgetが不足する場合、Inference Call数が増えずFail closedになる。
5. No HitとBudget不足のUI／Eventが異なる。
6. `EASA + DLAGSA + OCILNS`の同時Queryで、各SubjectのCanonical／Catalog DefinitionをCoverageする。
7. Project固有略称のProduction Hard-codeがない。
8. Previous Assistantの虚偽記述があっても、新しいReference Instructionで正本優先を示す。
9. Summary、Stop、New Chat、Browser Reload、Model Busy、Public Demo RAG Denialを回帰させない。
10. Full Suite、Ruff、MypyおよびJavaScript SyntaxがGreenである。

## 8. Prohibited Shortcut

次のみで修正完了としない。

```text
max_new_tokensを下げるだけ
context_sizeを上げるだけ
top_kを増やすだけ
safety_marginを下げるだけ
ユーザーに毎Turn New Chatを求める
誤りを4B Modelのせいだけにする
```

## 9. Out of Scope

```text
ARGD／DAGD Runtime実装
Judge／Repair
Embedding／Hybrid／Vector DB
New Model／Dependency
Context Windowの大幅変更
Conversation Compression／Persistent Memory
Lightning／Public Demo Documentation RAG
```
