# Phase 7 Execution Plan — Bounded MVP

```yaml
document_id: phase_7_execution_plan
document_state: accepted_frozen_ready
phase: phase_7
language: ja
created_at: 2026-08-29 17:14:22 JST
executor_candidate: Claude
reviewer: Codex project responsible and design governor role
```

## 1. Execution Policy

- Phase 6の実装をやり直さない。
- 実装者はPackageを連結実行し、Routine報告で停止しない。
- PackageごとにRecovery Indexを残す。
- Controllerは実装中に並行実装せず、Return後にBounded Reviewする。
- Reviewは中心経路、Data Integrity、Network副作用、Citation、Regressionへ限定する。
- P2以下は未解決Registryへ送り、Enterprise Hardeningを追加しない。

## 2. Packages

### P7-0 Entry／As-built Freeze

- Phase 2 RAG、Citation、Conversation Persistence、Branch／RegenerateのAs-built Map。
- Phase 6既知Debtと非依存境界の固定。
- Test／Temp／Cache／Network Authorityの固定。

### P7-A Attachment Sizing

- Icon／Drag & Drop、対象File、Transport、Storage、Parser、RAG取込、Security影響を評価。
- Phase 7へ採用する最小範囲またはPhase 10延期を決定。
- Sizingだけを理由に本体を停止しない。

### P7-B Corpus／Document Lifecycle

- Corpus／Document／Revision／Chunk Identity。
- Local Registration、Update、Delete、Digest。
- Phase 2 Corpus Adapter互換。

### P7-C Embedding／Index／Retriever

- Port／Adapter、Index Revision、Retrieval Run。
- Candidate／Selected ChunkとScore Evidence。
- Empty／Unavailable／No Relevant Evidence。

### P7-D Context Injection／Citation Persistence

- Injection Boundary。
- Source／Chunk Citation。
- Reload／Restart／Branch／Regenerate／Resume Persistence。

### P7-E Web Search／Fetch

- Search／Fetch／Normalizer Port。
- disabled／manual／automatic。
- Settings Web検索Toggle。
- OFF時Network 0、Manual Search Golden Path。

### P7-F Web Security／Evidence Governance

- URL／Redirect／Private Network／Size／Timeout／Secret／PII／Cost Gate。
- OFF／OBSERVE／ENFORCE。
- Source Authority／Freshness／Snippet／Fetched Content分離。

### P7-G Data Controls

- Settings第三領域。
- Source Class、Retention、Export、Delete、External Transmission、Purpose Consent。
- User／Feedback／Synthetic Training利用Default OFF。

### P7-H Integration／Observability／Regression

- Request-correlated Retrieval／Search／Citation Status。
- Conversation／Citation／Branch／Recording／Stop Regression。
- Failure Language／Reason。

### P7-I User Manual Candidate／Complete Candidate

- Local Document Golden Path。
- Web Manual Search Golden Path。
- OFF Network 0。
- Citation Persistence。
- Attachment採用時のみ添付Golden Path。
- Complete Candidate Return。Closure／Git／Phase 8へ進まない。

## 3. Recovery Boundary

各Package Recoveryには次を含める。

```text
Completed Work Units
Changed Paths
Focused Verification
Known Findings／Deferrals
Network／Git／User Data／External Action Inventory
Active Process
Next Exact Work Unit
```

利用制限またはCompaction時は、最後に完了したPackageから差分再開する。成立済みPackageを再実行しない。

## 4. Controller Review上限

```text
Independent Review 1回
P0／P1 Bounded Rework 1回
Targeted Re-review 1回
User Manual
```

新しいP2／P3 HardeningをReview Loopへ追加しない。
