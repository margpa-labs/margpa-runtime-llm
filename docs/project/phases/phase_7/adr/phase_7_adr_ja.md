# Phase 7 ADR — RAG／Web Search／Data Governance

```yaml
document_id: phase_7_adr
document_state: accepted_frozen
phase: phase_7
language: ja
created_at: 2026-08-29 17:14:22 JST
```

## ADR-7-001：Phase 2 RAGを破棄せず拡張する

Persistent Citation、Conversation、Branch、Regenerate契約を保持し、Full RAG Adapterを接続する。

## ADR-7-002：Search ActivationとGovernance Modeを分離する

`disabled／manual／automatic`と`OFF／OBSERVE／ENFORCE`を別状態にする。初期値はdisabled／OFF。

## ADR-7-003：Web ProviderをPort越しに交換可能とする

Domain／Applicationへ特定Search Vendor SDKをHard-codeしない。

## ADR-7-004：CitationはEvidenceであり装飾ではない

Source Identity、Digest、取得時刻、採用ChunkがないCitationを成立扱いしない。

## ADR-7-005：SnippetとFetched Contentを区別する

検索Snippetだけを本文確認済みの一次Sourceとして扱わない。

## ADR-7-006：Data Purposeを個別Consentにする

Conversation保存、Evaluation、Dataset Export、将来Trainingを一つのONへまとめない。

## ADR-7-007：OFFは副作用0を意味する

Web検索OFF時はNetwork Call 0、Training利用OFF時はTraining Export 0とする。

## ADR-7-008：Phase 6既知Debtを隠さない

Retrieval／Citationを成立させても、Selene、Qwen3Guard、Semantic 109、Judge／Repairが解決したとClaimしない。

## ADR-7-009：AttachmentはSizing後に採否する

Upload、Storage、Parser、RAG Ingestion、Multimodalを分離し、局所実装だけをPhase 7候補にする。

## ADR-7-010：Phase 7はPoC／MVP停止線を守る

中心経路、正直なFailure、既存Regression、User Manualを満たした後のEnterprise Hardeningは未解決Registryへ送る。

## ADR-7-011：Data Quality／Label GovernanceはPhase 10以降

Phase 7は最小Identity／Provenance／Consent／Export Seamまでとし、Clean／Eligibleを保証しない。

## ADR-7-012：Phase 7完了前に実画面Probeを挟む

Local Retrieval、Web Manual Search、Citation Persistence、OFF副作用0をPackage単位でUser確認可能にする。
