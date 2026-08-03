# ユーザー向け Phase 1-ex Mac限定簡易Documentation RAG Manual Acceptance Handoff

```yaml
document_id: user_handoff_phase_1_ex_mac_local_documentation_rag_manual_acceptance
phase: phase_1_ex
status: ready_for_user_manual_acceptance
language: ja
created_at: 2026-07-31 22:23:02 JST
owner: 設計統括者役
execution_owner: user
source_review: designer_review_phase_1_ex_mac_local_documentation_rag_retrieval_acceptance_follow_up_20260731222302.md
external_service_change: prohibited
project_docs_mutation_for_test: prohibited
```

## 1. Purpose

設計統括者ReviewでAcceptedとなったMac限定簡易Documentation RAGを、Local Macの単一GGUF Model InstanceおよびBrowserで最終確認する。

本Handoffは手動受入手順であり、自動Testの代替ではない。実ProjectのCanonical DocsをTestのために変更、移動、改名または削除しない。

## 2. Precondition

```text
Designer Re-review:
  ACCEPTED

Required Automated Suite:
  395 passed／3 deselected

Local Runtime:
  macOS arm64／Metal

Documentation RAG Default:
  OFF

Public Demo RAG:
  denied
```

現在Port 8000で旧Web Processが動作中の場合、差し替え後Codeを読ませるために、ユーザー自身が通常の方法で旧Processを終了してから新しく起動する。設計統括者役および実装者役は勝手にProcessを停止しない。

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

Model Load、Artifact SHA-512確認およびCold Index Buildに時間がかかる場合がある。

## 4. Minimum Manual Acceptance

### 4.1 Existing Chat Regression

1. Runtime情報が表示される。
2. `プロジェクトDocs参照／Project Docs`が表示される。
3. 初期値がOFFである。
4. OFFのまま通常Chatを1 Turn行い、既存生成が成立する。

### 4.2 Required RAG Queries

RAGをONにし、次を個別Turnで確認する。

```text
Project概要:
  Nazuna Research Governance LLMとは何ですか？

Roadmap:
  roadmapの現在の進捗を教えてください。

Architecture:
  システムArchitectureを説明してください。

Governance:
  ARGDとDAGDについて説明してください。

External R&D Hooks:
  EASAとは何ですか？
  DLAGSAとは何ですか？
  OCILNSとは何ですか？
```

各Turnで次を確認する。

- Assistant回答が生成される。
- CitationはModel本文と別に表示される。
- Citation PathはProject相対Pathであり、Absolute Pathを含まない。
- Citation Headingが表示される。
- Citation Path Copyが動作する。
- 回答の断定が参照Docsと明らかに矛盾しない。

### 4.3 Expected Citation Direction

Exact Rankの固定ではないが、少なくとも次の正本系統を含む。

```text
Roadmap:
  docs/public/roadmap_ja.md

Architecture:
  docs/project/current/architecture/system_architecture_ja.md

ARGD／DAGD:
  docs/project/current/governance/runtime_governance_specification_ja.md
  or Phase 1 Governance Catalog

EASA／DLAGSA／OCILNS:
  Current／Public Canonical
  or Phase 1 Governance／Architecture Catalog
```

無関係なLanguage Smoke、User Manualまたは過去のHistory断片だけがCitationに出る場合は不合格Evidenceとする。

## 5. Safety／Lifecycle Acceptance

### 5.1 No Hit

Project Docsと明らかに無関係な質問を送る。

Expected：

```text
Citation:
  empty

Status／Warning:
  safe

Subsequent normal turn:
  available
```

No HitはModelの無関係な一般知識回答を保証するものではない。Retrievalが無根拠のCitationを作らないことを確認する。

### 5.2 Summary Mode

1. RAG ON。
2. Summary Mode ON。
3. Projectに関する質問を送る。
4. RetrievalがOriginal Stageの一度だけである。
5. Summary完了後もOriginal RetrievalのCitationが維持される。

### 5.3 Stop

Cold Retrieval中またはModel生成中に停止する。

Expected：

- 安全に停止する。
- 中途なCitationを完了Evidenceとして表示しない。
- 停止後の次Turnを開始できる。

### 5.4 New Chat

New Chatで次を初期化する。

```text
Conversation
Citation
Turn-local RAG state
```

ModelとProcessのReloadは不要である。

### 5.5 Browser Reload

RAGをONにした後にBrowser Reloadする。

Expected：

```text
Documentation RAG:
  OFFへ戻る

Temporary Conversation／Citation:
  cleared
```

## 6. Index Rebuild Boundary

Manual TestのためにCanonical Docsを変更しない。

Docsの設計上必要な正式変更が別件でAcceptedされ、実際に変更された場合だけ、次のRAG ON RequestでIndexがManifest Digestに従い再構築されることを確認する。

```text
Test-only Docs Mutation:
  PROHIBITED

Accepted real Docs change:
  rebuild observation allowed
```

Docs Missing試験は既にTemporary Fixtureで自動化されている。実Projectの`docs/`を移動、改名または一時退避しない。

## 7. Public Demo Boundary

Public Demoを現在起動している場合にのみ確認する。本Manual AcceptanceのためにLightningを起動、変更または課金しない。

Expected：

```text
Public Demo RAG Control:
  hidden

Public Request documentation_rag_mode=enabled:
  denied

Documentation Adapter:
  not composed
```

Public Demoが停止中の場合、RepositoryのAutomated Access Profile TestがGreenであることを証跡とし、外部環境の手動起動は必須としない。

## 8. Evidence to Report

各項目を次の形式で報告できる。

```text
RAG OFF normal chat:
  PASS／FAIL

Project overview:
  PASS／FAIL
  citation path／heading:

Roadmap:
  PASS／FAIL
  citation path／heading:

Architecture:
  PASS／FAIL
  citation path／heading:

ARGD／DAGD:
  PASS／FAIL
  citation path／heading:

EASA／DLAGSA／OCILNS:
  PASS／FAIL
  citation path／heading:

No Hit:
  PASS／FAIL

Summary:
  PASS／FAIL

Stop／Recovery:
  PASS／FAIL

New Chat:
  PASS／FAIL

Browser Reload:
  PASS／FAIL

Public Demo boundary:
  PASS／FAIL／NOT_RUN
```

Failure時は、Secret、Absolute Path、Raw Reference本文または個人情報を転記せず、次を記録する。

```text
Input Query
Visible Safe Error／Warning
Citation Project-relative Path
Citation Heading
Expected Source
Stop／Reload／Summary状態
```

## 9. Acceptance Rule

```text
Required functional and lifecycle items all pass:
  Manual Acceptance candidate PASS

Wrong canonical source／unsafe path／RAG state leak／regression:
  FAIL／return to designer review

Public Demo not running:
  NOT_RUN／non-blocking because automated denial test is Green
```

ユーザー報告後、設計統括者役がManual EvidenceをAppend-onlyで確定し、Mac限定簡易Documentation RAGの最終Acceptanceを判定する。

