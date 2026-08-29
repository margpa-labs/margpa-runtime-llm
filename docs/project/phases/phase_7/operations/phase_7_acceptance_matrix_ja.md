# Phase 7 Acceptance Matrix

```yaml
document_id: phase_7_acceptance_matrix
document_state: accepted_frozen_ready
phase: phase_7
language: ja
created_at: 2026-08-29 17:14:22 JST
acceptance_count: 32
```

| ID | Acceptance |
|---|---|
| P7-ACC-001 | Phase 2 Citation／Conversation Contractを破壊しない。 |
| P7-ACC-002 | RAG OFFでRetrieval／Injection Call 0。 |
| P7-ACC-003 | Web検索OFFでSearch／Fetch／Network Call 0。 |
| P7-ACC-004 | Local Corpusを登録できる。 |
| P7-ACC-005 | Document更新時にRevision／Digestが更新される。 |
| P7-ACC-006 | Document削除後もHistorical EvidenceをCurrentと混同しない。 |
| P7-ACC-007 | Chunk ID／DigestがDocument Revisionへ結び付く。 |
| P7-ACC-008 | Embedding／Index／Retriever IdentityをEvidence化する。 |
| P7-ACC-009 | Candidate／Selected ChunkとScoreを区別する。 |
| P7-ACC-010 | No Relevant Evidenceを回答根拠ありへ変換しない。 |
| P7-ACC-011 | Context Injectionへ選択Evidenceだけを渡す。 |
| P7-ACC-012 | CitationにDocument／Chunk／Digest／Source Identityがある。 |
| P7-ACC-013 | Reload後もCitationが復元される。 |
| P7-ACC-014 | Server Restart後もCitationが復元される。 |
| P7-ACC-015 | Branch／Regenerate／Resume後も正しいCitationへ分岐する。 |
| P7-ACC-016 | Manual Web SearchがPort越しに実行される。 |
| P7-ACC-017 | Search SnippetとFetched Contentを区別する。 |
| P7-ACC-018 | Canonical URL、Title、Provider、取得時刻、DigestをEvidence化する。 |
| P7-ACC-019 | Official／Primary／Secondary／General／Unknownを区別する。 |
| P7-ACC-020 | Private／Loopback／Metadata Endpointを拒否する。 |
| P7-ACC-021 | 危険Scheme／Redirect／巨大Response／Timeoutを有界化する。 |
| P7-ACC-022 | Secret／PII候補を無断送信しない。 |
| P7-ACC-023 | Document Prompt InjectionをDetection Evidenceへ残す。 |
| P7-ACC-024 | Web Search Toggleが通常Settingsの指定位置・既存Toggle形式で表示される。 |
| P7-ACC-025 | Data ControlsがSource、Retention、Export、Delete、External Transmission、Purpose Consentを分離する。 |
| P7-ACC-026 | Feedback／Synthetic／Future Training利用のDefaultがOFF。 |
| P7-ACC-027 | Data保存をTraining完了と表示しない。 |
| P7-ACC-028 | Failure Reason／Stage／Provider／Request IDを正直に表示する。 |
| P7-ACC-029 | Conversation／Branch／Recording／Stopに重大Regressionがない。 |
| P7-ACC-030 | Attachment Sizingの採用／延期と理由がEvidence化される。 |
| P7-ACC-031 | Canonical Backend／Static／Frontend検証が変更範囲に比例してPASSする。 |
| P7-ACC-032 | User実画面でLocal Source、Web Source、Citation、OFF副作用0を確認できる。 |

`P7-ACC-032`前にPhase 7 Closureを主張しない。Phase 6既知Debtは本MatrixのPASSへ読み替えない。
