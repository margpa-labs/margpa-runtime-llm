# ユーザー向け Phase 1-ex Mac限定簡易Documentation RAG Manual Acceptance Retest Handoff

```yaml
document_id: user_handoff_phase_1_ex_mac_local_documentation_rag_manual_acceptance_retest
phase: phase_1_ex
status: ready_for_user_manual_acceptance_retest
language: ja
created_at: 2026-08-01 01:43:39 JST
owner: 設計統括者役
execution_owner: user
source_review: designer_review_phase_1_ex_mac_local_documentation_rag_coverage_integrity_follow_up_20260801014339.md
external_service_change: prohibited
project_docs_mutation_for_test: prohibited
```

## 1. Purpose

1回目のMac手動Testで確認した次のFailureが、Coverage Integrity Follow-upにより閉じられたかを実GGUFとBrowserで再確認する。

```text
初回TurnだけRetrievalし、後続Turnで参照しない
一部のCitationだけで複数Subjectの残りを推測する
EASA／DLAGSA／OCILNS／ARGD等の正式名称や関係を混同する
```

本HandoffはManual Acceptance手順であり、Project DocsをTest用に変更、移動、改名または削除しない。

## 2. Preconditions

```text
Coverage Integrity implementation:
  ACCEPTED

Repository Full Suite:
  408 passed／3 deselected

Local Runtime:
  macOS arm64／Metal

Documentation RAG Default:
  OFF

Public Demo Documentation RAG:
  denied／out of scope
```

現在のWeb Processが旧Codeを読んでいる場合だけ、ユーザー自身が通常の方法で停止し、新しく起動する。設計統括者役および実装者役は勝手にProcessを停止しない。

## 3. Start

Project Rootで実行する。

```bash
./.venv/bin/python -m margpa_runtime_llm.entrypoints.web.main \
  --host 127.0.0.1 \
  --port 8000
```

Browser：

```text
http://127.0.0.1:8000/
```

## 4. Test Settings

Coverageと回答を分けて観測するため、最初の再試験は次で固定する。

```text
Project Docs:
  ON

Summary Mode:
  OFF

Thinking Generation:
  OFF

Thinking Visibility:
  OFF

Response Language:
  ja

Maximum New Tokens:
  512
```

`Maximum New Tokens=512`はDocumentation Context用の全体余力を確保するための試験条件である。Documentation Reference自体のBounded上限を無制限に緩和するものではない。

## 5. Required Retest

### 5.1 Japanese Combined Subject

新規Chatで次を1 Turnとして送る。

```text
EASAとは何ですか？
DLAGSAとは何ですか？
OCILNSとは何ですか？
それぞれ3行以内で、参照文書に記載された正式名称と役割だけを説明してください。
```

Correct canonical names：

```text
EASA:
  Exception Aware Safety Architecture
  例外認識型安全統治機構

DLAGSA:
  Distributed LEA Agentic Governance & Safety Architecture
  分散証跡型例外認識エージェント統治安全機構

OCILNS:
  Open Cognitive Interaction Ledger Network System
  認知対話証跡台帳網
```

### 5.2 English Prose-noise Combined Subject

UI言語ではなく回答言語を`en`へ変更し、新規Chatで次を送る。

```text
What are EASA, DLAGSA, and OCILNS?
Explain each in no more than three lines, using only the referenced project documents.
```

正常なCoverage SubjectはEASA／DLAGSA／OCILNSの3件だけである。`What`、`are`、`and`、`Explain`等はCoverage Subjectではない。UI上でCountを直接表示していないため、引用と回答の対応から確認する。

### 5.3 ARGD／DAGD Separation

回答言語を`ja`へ戻し、新規Chatで次を送る。

```text
ARGDとDAGDについて、それぞれの正式名称と担当領域を3行以内で説明してください。
EASAとの関係は参照文書に明記されている場合だけ説明してください。
```

Correct canonical names：

```text
ARGD:
  Axiomatic Reasoning Governance Definition v0.3.1

DAGD:
  Declarative AI Governance Definition v0.4.4
```

ARGDを「EASAの安全挙動を制御する専用Architecture」と断定する、またはDAGD／DLAGSAと混同する回答はFAILとする。

### 5.4 Every-turn Retrieval

同じChatの連続Turnで次を順に送る。

```text
Turn 1:
  EASAとは何ですか？3行で。

Turn 2:
  ARGDとは何ですか？3行で。

Turn 3:
  DLAGSAとは何ですか？3行で。

Turn 4:
  roadmapの現在の進捗を教えてください。
```

各Turnで次のどちらかが必須である。

```text
A:
  当該Turnの回答に対応する参照文書が表示される。

B:
  Context／Subject Coverage不足のSafe Errorにより回答を生成しない。
```

Turn 1の参照だけを使い回し、Turn 2以降でProject固有事実を知ったかぶりする場合はFAILとする。

### 5.5 Explicit Insufficient-boundary Observation

Combined Queryで次のSafe Messageのいずれかが出る場合がある。

```text
documentation_context_budget_insufficient
documentation_subject_coverage_insufficient
```

この場合は次を確認する。

- Assistantが推測による本文回答を生成しない。
- エラー後に次Turnを開始できる。
- 新規Chatまたは単一Subject Queryは継続して利用できる。

これはSafety BoundaryとしてPASSだが、Combined QueryのFunctional Acceptanceは「回答可能」と別に記録する。

## 6. Regression Smoke

最低限、次も確認する。

```text
RAG OFF normal chat:
  通常回答とCitationなし

RAG ON true unrelated query:
  無根拠のProject Citationを作らない

New Chat:
  Conversation、Citation、Turn-local stateを初期化

Browser Reload:
  RAG OFFへ戻る
```

Summary、Stop、Copy、Model BusyおよびPublic Demo Denialは前回までの自動／手動Evidenceを維持している。このRetestで新しい異常を観測しない限り、全項目の長時間再試験は必須としない。

## 7. Evidence to Report

```text
RAG OFF normal chat:
  PASS／FAIL

Japanese combined:
  GROUNDED PASS／SAFE DENY／FAIL
  citation path／heading:
  wrong expansion or relation:

English combined:
  GROUNDED PASS／SAFE DENY／FAIL
  citation path／heading:
  wrong expansion or relation:

ARGD／DAGD:
  GROUNDED PASS／SAFE DENY／FAIL
  citation path／heading:
  wrong expansion or EASA relation:

Every-turn retrieval:
  Turn 1:
  Turn 2:
  Turn 3:
  Turn 4:

Safe insufficient boundary:
  PASS／NOT_OBSERVED／FAIL

New Chat／Reload:
  PASS／FAIL
```

Failure時はSecret、Absolute Path、Raw Reference全文または個人情報を転記せず、次だけを記録する。

```text
Input Query
Visible Safe Error／Warning
Assistant Answer
Citation Project-relative Path
Citation Heading
Expected Canonical Name／Definition
Turn Number
```

## 8. Acceptance Rule

```text
正しい根拠が全SubjectでAssemblyされ、回答とCitationが一致:
  GROUNDED PASS

Context／Coverage不足を明示し、本文回答を作らない:
  SAFETY PASS
  Combined usabilityはPENDING

一部Citationだけで、未参照Subjectの正式名称、定義または関係を推測:
  FAIL／BLOCKER

2 Turn目以降でRetrieval／Citationを行わずProject固有回答を作成:
  FAIL／BLOCKER
```

ユーザー報告後、設計統括者役がManual EvidenceをAppend-onlyで確定し、CorrectnessとUsabilityを分離して最終判定する。
