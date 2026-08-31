# Phase 8 User Mac Manual Web Segment 1 — 未解決Snapshot

```yaml
document_id: phase_8_user_mac_manual_web_segment_1_unresolved_snapshot_20260831112449
document_type: unresolved_finding_snapshot
document_state: frozen_historical
language: ja
created_at: 2026-08-31 11:24:49 JST
source_evidence: docs/project/phases/phase_8/history/operations/phase_8_user_mac_manual_acceptance_web_segment_1_evidence_ja_20260831112449.md
```

| Registry ID | 内容 | Severity／Priority | Closure Blocker | Disposition |
|---|---|---|---:|---|
| UF-P8-005 | 普通のPublic URL取得が不安定で、取得失敗後もModelが非Grounded回答 | Major／P0 | Yes | Phase 8 Manual URL MVPのBounded Rework候補 |
| UF-P8-006 | Raw HTML全体注入でContext Budget超過 | Major usability／P1 | No by current User reservation | 簡易Hard CapまたはTyped FailureはPhase 8候補、Full ExtractorはPhase 11以降 |
| UF-P8-007 | Chat EvidenceがSpecific Reasonを`url_rejected`へ潰す | Moderate observability／P1 | No standalone | UF-P8-005と同時修正候補 |
| UF-UI-007 | 専用URL欄と通常Composer URL貼付のUX差 | UI scope／P2 | No | Phase 10右Panel／Phase 11 Web UI |

Controllerが`dns_resolution_failed`をUser Runtimeの確定原因と断定した件は撤回済み。Current Evidenceで確定しているのは
Public URL取得失敗、Specific Reason消失および非Grounded回答であり、具体Transport原因は未観測である。

このSnapshotはAppend-onlyであり、解決・再分類時も改変しない。Current StatusはStable未解決Registryで更新する。
