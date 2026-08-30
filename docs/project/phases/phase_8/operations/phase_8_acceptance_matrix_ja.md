# Phase 8 Acceptance Matrix

```yaml
document_id: phase_8_acceptance_matrix
document_state: accepted_frozen_ready
phase: phase_8
language: ja
created_at: 2026-08-30 19:18:06 JST
acceptance_count: 40
```

| ID | Acceptance |
|---|---|
| P8-ACC-001 | Phase 7 Local RAG／Citation／Data Controls／Persistenceを破壊しない。 |
| P8-ACC-002 | Manual URL機能OFF時、Network Call 0。 |
| P8-ACC-003 | User明示のPublic `http／https`だけをFetch候補にする。 |
| P8-ACC-004 | Credential／Private／Loopback／Link-local／Metadata／危険Schemeを拒否する。 |
| P8-ACC-005 | RedirectごとにTargetを再検証する。 |
| P8-ACC-006 | Timeout／Size／Content Typeを有界化する。 |
| P8-ACC-007 | JavaScript／Cookie／Login／Form／Downloadを実行しない。 |
| P8-ACC-008 | 取得ContentをUntrustedとして画面表示できる。 |
| P8-ACC-009 | 明示操作時だけ取得ContentをMain Model Evidenceへ渡す。 |
| P8-ACC-010 | CitationにCanonical URL／取得時刻／Digest／Source Classがある。 |
| P8-ACC-011 | Reload／Restart後もURL Evidence／Citationを復元できる。 |
| P8-ACC-012 | Fetch成功とContent信頼を同一視せず、Failureを正直に表示する。 |
| P8-ACC-013 | Branch操作UIが既定非表示になる。 |
| P8-ACC-014 | Branch Data／API／過去履歴は保持される。 |
| P8-ACC-015 | Data ControlsからArchive済みChatをLazy一覧表示できる。 |
| P8-ACC-016 | Archive済みChatのTitle／Timestampを表示し、開ける。 |
| P8-ACC-017 | Archive解除後に手動Resumeなしで送信できる。 |
| P8-ACC-018 | 完全削除／一括Delete／Exportを虚偽表示しない。 |
| P8-ACC-019 | `constitution/` Manifest／Rule／ViewのRevisionとDigestを検証できる。 |
| P8-ACC-020 | ConstitutionとGD Providerが疎結合な並列Resultを返す。 |
| P8-ACC-021 | OFF／OBSERVE／ENFORCEの差がEvidenceで確認できる。 |
| P8-ACC-022 | Constitution OFFでもPlatform Security／既存Authorityを解除しない。 |
| P8-ACC-023 | Constitution ViewはAuthorityを追加できない。 |
| P8-ACC-024 | 不明Rule／Conflict／Digest不一致を黙ってPassにしない。 |
| P8-ACC-025 | Agent Coreへ特定GD名／Provider／User PathをHard-codeしない。 |
| P8-ACC-026 | 通常ChatとDev Agent PreviewをUIで切替できる。 |
| P8-ACC-027 | Stable Capability IDとDisplay Nameを分離する。 |
| P8-ACC-028 | Run／Step／State／Tool Request／Result／Dispositionを追跡できる。 |
| P8-ACC-029 | Tool Port／RegistryとAdapterを交換可能にする。 |
| P8-ACC-030 | Fake／Deterministic Toolの複数Step Golden Pathが完了する。 |
| P8-ACC-031 | MCP Client Adapter Portを持つが、Remote MCP完成を主張しない。 |
| P8-ACC-032 | Plan-only／Manual／Risk-based／Important-gate-onlyを区別する。 |
| P8-ACC-033 | Important-gate-onlyはFrozen Envelope内だけ逐次確認なしで進む。 |
| P8-ACC-034 | External Write／Network／Cost／不可逆／Scope拡張等でGate待機する。 |
| P8-ACC-035 | HarnessがProvider／Platform強制Gateを迂回しない。 |
| P8-ACC-036 | Max Step／Deadline／Retry／Budget／Loop防止が作用する。 |
| P8-ACC-037 | Stop／Cancel後のLate ResultがCurrentへ追加されない。 |
| P8-ACC-038 | Run／Step／Tool／Approval／Constitution／GDをID相関して永続化する。 |
| P8-ACC-039 | Canonical Backend／Static／Frontend検証が変更範囲に比例してPASSする。 |
| P8-ACC-040 | User実画面でManual URL、Archive管理、Chat／Agent切替、Gate／Stopを確認できる。 |

`P8-ACC-040`前にPhase 8 Closureを主張しない。Real NetworkまたはMCPがAuthority不足でNOT RUNの場合は、Fixture PASSと実接続PASSを混同しない。
