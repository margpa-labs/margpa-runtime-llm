# 設計統括者Review：Phase 1-ex Documentation RAG Cross-environment Manual Acceptance

```yaml
document_id: designer_review_phase_1_ex_documentation_rag_cross_environment_manual_acceptance
phase: phase_1_ex
status: functional_accepted_quality_tuning_deferred
language: ja
created_at: 2026-08-01 15:44:12 JST
owner: 設計統括者役
manual_evidence: ../operations/documentation_rag_manual_test_3_and_lightning_recovery_findings_20260801154412.md
```

## 1. Decision

ユーザーのMac／Lightning実機Evidence、Lightning復旧後Test、Import Smoke、Public／Basic Access、公開8文書Corpus、CitationおよびAuto-start動作を確認した。

```text
Mac Local Documentation RAG:
  ACCEPTED

Lightning Basic Preview Documentation RAG:
  ACCEPTED

Lightning Public Demo Documentation RAG:
  ACCEPTED

Public 8-doc Corpus Boundary:
  ACCEPTED

RAG Default OFF:
  ACCEPTED

Cross-environment Adapter Hook:
  COMPLETE

Answer Quality:
  LIMITED／TUNING DEFERRED

Phase 7 Full RAG:
  NOT IMPLEMENTED／NOT CLAIMED
```

本Decisionは、すべての質問へ正確に回答すること、CitationがClaimを含意すること、Current Statusを常に正しく抽出することまたはHallucinationが解消したことを意味しない。

## 2. Acceptance Basis

- Mac LocalでRAG ON／OFFとCitationを実測した。
- Lightningへ公開8文書を全件配置した。
- Basic／Public Preflightで`expected=8 present=8 missing=0`を確認した。
- Coherent Runtime Snapshot同期後、Application Importが成立した。
- Focused Testは185 Passed、Node.js不在による1 Skipである。
- Web Integration単体は28 Passedである。
- Public DemoはManual ForegroundとAuto-startで動作した。
- Basic PreviewはAuto-startで認証、LLMおよびRAGが動作した。
- Public DemoとBasic PreviewはAccess Profileを分離したまま、同じ公開Corpus Contractを使用できた。

## 3. Non-blocking Limitations

- Lightweight Qwen3-4Bの理解・要約・指示追従能力に制約がある。
- Lexical RetrievalはSemantic Entailmentを保証しない。
- 無関係または弱関連Chunkを選ぶ場合がある。
- Current／Historical／Supersededの意味的優先は完全ではない。
- Citation表示は回答文の全Claimを自動検証しない。
- Basic Previewの今回のManual Foreground Commandだけは再確認していないが、Auto-startと既存Lifecycle Acceptanceが成立している。

これらは後続Tuning対象であり、今回のCross-environment Adapter AcceptanceをBlockしない。

## 4. Deployment Finding

最新差分だけの配置では、対象Lightning Baselineとの差によりTransitive Sourceが不足した。今後はBaseline不一致時、同一時点のRuntime Deployment Snapshotを高優先度で使用する。

- [Runtime Deployment Snapshot運用方針](../../../../shared/operations/runtime_deployment_snapshot_policy_ja.md)
- [Lightning Deployment Follow-up Architecture](../architecture/lightning_documentation_rag_deployment_snapshot_follow_up_architecture_20260801154412.md)
- [第3回Manual Test／Recovery Findings](../operations/documentation_rag_manual_test_3_and_lightning_recovery_findings_20260801154412.md)

## 5. Deferred Quality Work

次は今回の完了条件から分離する。

- Retriever／Chunk／Ranking再評価
- Current／Superseded Metadata
- Evaluation DatasetとRegression
- JudgeによるCitation／Claim評価
- ARGD／DAGD等のGovernance適用差分
- 高性能Modelへの交換比較
- Phase 7 Embedding／Vector Store／任意Corpus

手動Hit Keyword表、Project固有略称Allowlistまたは固定Subject Mappingは、保守性とHard-code依存を再評価するまで導入しない。

## 6. Next Gate

Documentation RAG実装工程は一旦完了とする。Roadmapを現在Evidenceへ更新した後、Phase 1-exの次工程であるGit運用設計へ進む。
