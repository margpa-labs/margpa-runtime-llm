# Phase 2-C Persistent Conversation API／UX Acceptance Matrix

```yaml
document_id: phase_2_c_persistent_conversation_api_ux_acceptance_matrix
status: accepted_and_frozen_for_phase_2_c
phase: phase_2
subphase: phase_2_c
created_at: 2026-08-14 JST
owner_role: Phase 2設計担当者役
executor_role: Phase 2実装者役
```

## 1. Rule

全`required`がEvidence付きPASSでなければPhase 2-Cを完了としない。Implementerの自己判定で閉じず、Designer Conformance ReviewとController Closure Reviewを必須とする。

## 2. Exposure／Compatibility

| ID | Required acceptance | Evidence |
|---|---|---|
| P2C-EXP-001 | Local／Loopback／Explicit opt-inだけがv2 PersistenceをBinding | Startup Matrix Test |
| P2C-EXP-002 | Public／Basic／Non-loopback+opt-inをStore Build前にFail-closed | Spy／Filesystem Inventory |
| P2C-EXP-003 | Public／Basicの通常起動はPersistent Build／Read／Write 0 | Regression Test |
| P2C-CMP-001 | Existing `/api/v1/**` Wire／SSE／Cancel／Request Limit不変 | Existing Web Suite／Diff |
| P2C-CMP-002 | v1 ChatはPersistent Service／Store Call 0 | Spy Test |

## 3. API／Source of Truth

| ID | Required acceptance | Evidence |
|---|---|---|
| P2C-API-001 | v2 ContractはExtra Field／Invalid ID／OversizeをTyped Safe Failureで拒否 | Contract Test |
| P2C-API-002 | List／DetailはCanonical ProjectionだけでScope／Path／Receipt／Hidden Data 0 | Projection Test／Sentinel Scan |
| P2C-API-003 | Turn RequestはCurrent Content／Settings／Operation／RevisionだけでFull History Field 0 | Schema Test |
| P2C-API-004 | Reload／Conversation Select／Terminal／Conflict後にServer Detailで再描画 | Browser Unit／Integration Test |
| P2C-API-005 | Browser StorageへConversation本文を保存しない | Static Scan／Browser Test |
| P2C-IDM-001 | Client Operation IDからInternal IDをDomain-separatedで決定的導出 | Unit Test |
| P2C-IDM-002 | Applied済みAction IDの再送はBodyの同異にかかわらず409／新Mutation 0／Detail再Readへ収束 | Fault Injection Test |

## 4. Lifecycle／Streaming

| ID | Required acceptance | Evidence |
|---|---|---|
| P2C-LIF-001 | New ChatがConversation／Active Session／Revision 1を作成 | API Integration Test |
| P2C-LIF-002 | History OpenはWrite 0、Terminal SessionだけExplicit Resumeで新Session | Spy／Lifecycle Test |
| P2C-STR-001 | startがDurable Generating Revision／IDsを返し、DeltaはDisplay-only | SSE Test |
| P2C-STR-002 | completed／cancelled／errorはDurable Commit／Exact Receipt後だけ公開 | Fault Injection Test |
| P2C-STR-003 | Terminal Persistence FailureはSuccess Terminal 0／Ephemeral Fallback 0 | Fault Injection Test |
| P2C-STR-004 | StopとDisconnectがCancelledまたはInterruptedへ有界収束 | Async／Thread-affinity Test |

## 5. Retry／Regenerate／Branch

| ID | Required acceptance | Evidence |
|---|---|---|
| P2C-BRN-001 | Retryは非Completed Terminal SourceのUser／Parentを保ったDerived Turn | Domain/Application Test |
| P2C-BRN-002 | RegenerateはCompleted SourceからAlternativeを作りSourceを不変保持 | Integration Test |
| P2C-BRN-003 | Branch SelectはCompleted TurnだけをHeadにしRecord追加／削除 0 | CAS Test |
| P2C-BRN-004 | Invalid Source State／Parent／Stale Revisionは409／Mutation 0 | Negative Test |
| P2C-BRN-005 | 選択Head後のNormal Turnが選択Branchの履歴だけをContext化 | Mapper Integration Test |

## 6. Conflict／Privacy

| ID | Required acceptance | Evidence |
|---|---|---|
| P2C-CAS-001 | 二Browser相当のStale Mutationは409／Write 0 | Concurrent Client Test |
| P2C-CAS-002 | Conflict後はGET再取得しSilent Merge／Blind Retry／Last-write-wins 0 | Browser Test |
| P2C-PRV-001 | HTTPがScope ID／Root／Schema／Record ExistenceをSurface跨ぎで露出しない | Cross-profile Test |
| P2C-PRV-002 | Thinking／Prompt／RAG Context／Citation本文／Partial／Hidden／SecretがDB／API／Browser Storage 0 | Sentinel Test |
| P2C-PRV-003 | RecorderはOFF／Unbound／Call 0 | Spy Test |

## 7. UX／Quality Gates

| ID | Required acceptance | Evidence／Command |
|---|---|---|
| P2C-UX-001 | v2 Enabled時のList／History／New／Resume／Stop／Branch UIとja／en表示 | Browser DOM Test／Manual Matrix |
| P2C-UX-002 | v2 Disabled時はExisting Ephemeral UIが不変 | Existing Static／Web Test |
| P2C-QA-001 | Target Tests PASS | Handoff Target Command |
| P2C-QA-002 | Conversation／Web Regression PASS | `.venv/bin/pytest -q tests/unit/conversation tests/integration/conversation tests/integration/web` |
| P2C-QA-003 | Static JS Security PASS | Node／Pytest Static Tests |
| P2C-QA-004 | Ruff Format／Check、Mypy PASS | Standard Commands |
| P2C-QA-005 | Full Suite PASS／Project Root Runtime Data 0 | `.venv/bin/pytest -q`／Inventory |

## 8. Closure Output

```text
Implementer -> Designer:
  exact changes / acceptance map / tests / boundaries / rollback / findings

Designer -> Controller:
  PASS | REWORK | STOP
  exact required failures
  closure recommendation GO | ADJUST | STOP
```

## 9. Deferred Non-blockers

Config Control、Research／Developer Mode、Settings Persistence、Rename／Search／Delete／Export、Account／Remote Persistence、Concrete Recording、Encryption／CloudはPhase 2-C Acceptanceに含めない。新EvidenceなしにCurrent Blockerへ再活性化しない。
