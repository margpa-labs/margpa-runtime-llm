# Phase 1-ex Mac限定簡易Documentation RAG：1回目手動Testの結果から得られた知見

```yaml
document_id: mac_local_documentation_rag_manual_test_1_findings
phase: phase_1_ex
status: evidence_recorded_manual_acceptance_failed
language: ja
created_at: 2026-07-31 23:19:40 JST
owner: 設計統括者役
execution_owner: user
test_environment: local_macos_arm64_web_gguf
documentation_rag_mode: enabled_for_all_reported_turns
model: main.qwen3-4b-q4-k-m
```

## 1. Purpose

ユーザーがLocal Mac Webの実GGUF Modelで実施した1回目のDocumentation RAG Manual Testを、将来のRetrieval、Grounding、ARGD／DAGD、JudgeおよびRepair比較のBaseline Evidenceとして保全する。

本RecordはModel回答の内容を正しい事実として採用しない。「どの資料が取得され、どのような誤りが生じたか」をEvidenceとする。

## 2. Confirmed Test Condition

ユーザー確認：

```text
Documentation RAG:
  報告対象の全TurnでON

Conversation:
  複数Turnを同一Chatで連続実行

Observed impression:
  1回目は調べる
  2回目以降は参照を使わず、推測で発言する
```

RAG OFF／ONの取り違えではない。

## 3. Observed Cases

### 3.1 Combined EASA／DLAGSA／OCILNS Query

Input：

```text
EASAとは何ですか？
DLAGSAとは何ですか？
OCILNSとは何ですか？
```

Citationは4件表示されたが、主にCommon Integration、Common Handoff、Research Areas IndexおよびEASA Catalogであった。

Result：

```text
EASA:
  おおむね参照資料に忠実

DLAGSA:
  正式名称を別の意味として創作
  Distributed Ledger系と誤認

OCILNS:
  正式名称を創作
  Project正本にないProvenance系説明を断定
```

複数の高Signal Identifierを同時に質問した場合、BM25の単純上位選択が「全名称を列挙した一般文書」を優先し、各SubjectのCanonical DefinitionをTop K内に保証しないことを示す。

### 3.2 Subsequent Turns with RAG ON

次のQueryでは、UI上のCitationがすべて「参照文書なし」となった。

```text
Nazuna Research Governance LLMとは何ですか？
roadmapの現在の進捗を教えてください。
システムArchitectureを説明してください。
ARGDとDAGDについて説明してください。
EASA／DLAGSA／OCILNSの再質問
```

それでもModel生成は継続し、次の創作が発生した。

- `Nazuna Research`を会社と断定。
- Roadmapを読まず、EASA／DLAGSA／OCILNSの一般的進捗を創作。
- Project固有Architectureではなく、System Architectureの一般論を回答。
- ARGD／DAGDをAdversarial Robustness／Detection系の略称として創作。
- DLAGSA／OCILNSの誤った定義を反復。

これはRAGがOFFになった結果ではない。RAG ONであるにもかかわらず、Reference Contextを渡せない状態でModel生成を継続した。

### 3.3 Short Individual Queries

#### EASA

`EASAとは何ですか？ 3行で。`では、EASAのCanonical／Catalog系統から4件を取得し、回答もおおむね正しかった。

```text
Retrieval:
  success

Grounding:
  mostly successful
```

#### ARGD

`ARGDとは何ですか？ 3行で。`では、Current GovernanceおよびPhase Architectureを取得した。

しかし回答は次を創作した。

```text
公理的推論型安全定義:
  unsupported expansion

EASAの安全挙動を制御する:
  unsupported relationship
```

参照文書が存在してもModelが忠実に使わない「Grounding Failure」が存在する。また、直前のEASA説明をARGDの関係として混入するContext Contaminationが観測された。

#### DLAGSA

`DLAGSAとは何ですか？ 3行で。`ではCitationがなく、「動的リスク評価と安全制御Architecture」等の定義を創作した。

```text
Retrieval context:
  unavailable to generation

Generation:
  continued

Answer:
  hallucinated
```

### 3.4 Unrelated General Query

Project Docsと無関係な一般質問ではCitationなしでModel回答が継続した。

本CaseはDocumentation RAGのNo Hitとしては許容されるが、Main Modelの一般回答にも不正確な根拠説明があり、4B級ModelのHallucination Baselineとして分離記録する。医療的正しさの判定は本RAG Acceptanceの範囲外とする。

## 4. Root Cause Analysis

### 4.1 Prompt Usage is Counted as UTF-8 Bytes

ConversationのDocumentation Request Contextは、次をPrompt Tokenの保守的推定として加算する。

```text
len(message.content.encode("utf-8"))
```

日本語は多くの文字がUTF-8で3 Byteであり、Byte数をToken数のように扱うことで実際より大きく見積もる。

現在既定値：

```text
Loaded Context Size:
  4096

Requested Max New Tokens:
  2048

Documentation Safety Margin:
  512

Prompt／History／Docsに残る理論上限:
  1536 tokens before prompt consumption
```

1回目の日本語回答をHistoryへ追加した後、Byte数ベースのEstimateが残りを消費し、次TurnのDocumentation Budgetが`minimum_useful_tokens=128`未満または0となる。

### 4.2 Retrieval Hit can Fall Through to Ungrounded Generation

RetrieverがChunkを選択しても、Context AssemblerがBudget不足でBlockを0件にした場合、現行ApplicationはWarningを追加するが`should_generate=true`を維持する。

その結果：

```text
RAG ON
→ Retrieval attempted
→ Reference Context unavailable
→ Citation empty
→ Model generation allowed
→ Ungrounded answer
```

RAG ONという表示と実際のGrounding状態が一致しない。

### 4.3 UI Does Not Distinguish No Hit and Budget Exhaustion Clearly

UIはCitation 0件をどちらも「参照文書なし」と表示する。

```text
Case A:
  Corpusに根拠がないNo Hit

Case B:
  根拠はHitしたがContext Budgetに入らない
```

両者をユーザーが識別できない。

### 4.4 Multi-subject Coverage is Not Guaranteed

Current Rankingは総合Scoreの上位を選ぶが、Query内の複数Identifierそれぞれに対するDefinition Coverageを保証しない。

### 4.5 Citation Presence Does Not Guarantee Answer Faithfulness

CitationはSystemが選択したEvidenceであり、ModelがそのEvidenceに忠実に回答したことの保証ではない。ARGD Caseは、Citationが存在してもFormal NameとSystem間関係を創作することを示した。

## 5. Knowledge Gained

```text
Documentation RAG Pipeline:
  搭載済み

Single-turn Retrieval／Citation:
  成立し得る

Multi-turn Documentation Grounding:
  未成立

Retrieval Hit without Context:
  fail-openであり危険

Multiple Identifier Coverage:
  不足

Citation-to-answer Faithfulness:
  Modelにより失敗し得る

4B Main Model Hallucination:
  高頻度で観測
```

## 6. Research Value

今回の出力は、次の3状態を同一Modelで分離した。

```text
Retrieval success + mostly grounded answer:
  EASA

Retrieval success + grounding failure:
  ARGD

Reference unavailable + hallucinated answer:
  DLAGSA and subsequent turns
```

将来のARGD／DAGD Runtime、Judge、RepairおよびGovernance `off／observe／enforce`比較のBaseline Test Set候補とする。

ただし、Governance効果の公正な比較前に、RAGが各Turnで同じ根拠を供給できる状態を成立させる。Retrieval失敗とGovernance失敗を混同しない。

## 7. Acceptance Decision

```text
RAG Core／UI／Citation Installation:
  IMPLEMENTED

Current Manual Acceptance:
  FAIL／NO_GO

Reason:
  multi-turn budget exhaustion
  ungrounded fail-open generation
  multi-subject coverage gap
  citation-to-answer grounding failure
```
