# Phase 2-B Conversation Persistence／Lifecycle Acceptance Matrix

```yaml
document_id: phase_2_b_conversation_persistence_acceptance_matrix
status: accepted_and_frozen_for_phase_2_b
phase: phase_2
subphase: phase_2_b
language: ja
created_at: 2026-08-14 JST
owner_role: Phase 2設計担当者役
executor_role: Phase 2実装者役
```

## 1. 判定規則

全`required`項目がEvidence付きPASSでなければPhase 2-Bを完了としない。Test名／Command／Source Pathの少なくとも一つから各IDを追跡可能にする。実装者PASSだけで閉じず、設計担当者ReviewとController Closure Reviewを必要とする。

## 2. Storage／Serialization

| ID | Required acceptance | Evidence |
|---|---|---|
| P2B-STO-001 | Import／Builder／InspectはPath不存在時Write 0、Initializeだけが安全なRoot配下へ作成 | Target Test＋前後Inventory |
| P2B-STO-002 | 新規Permission 0700／0600、Unsafe既存Path／Symlinkを無変更で拒否 | Unit Test |
| P2B-STO-003 | Canonical JSON Round-trip、SHA-512、Exact Field、Metadata一致を検証 | Unit Test |
| P2B-STO-004 | Unknown Schema、Malformed JSON、Digest改ざん、Domain不整合をFail-closed | Unit Test |
| P2B-STO-005 | Scope本文をPathに使わず、異ScopeGet／List／Receipt／Commitを分離 | Unit Test |

## 3. CAS／Idempotency／Pagination

| ID | Required acceptance | Evidence |
|---|---|---|
| P2B-CAS-001 | Create／UpdateがRevisionを1だけ進め、二Adapter相当Lost Updateを防止 | Integration Test |
| P2B-CAS-002 | 同一Operation＋同一Commandは同一Receipt、異CommandはMutation 0 | Unit Test |
| P2B-CAS-003 | Response喪失／Unknown OutcomeがReceipt照合へ収束しBlind Retry 0 | Fault Injection Test |
| P2B-CAS-004 | Listが`updated_at DESC, id ASC`、Opaque Keyset Cursor、本文非露出 | Unit Test |
| P2B-CAS-005 | Generation中にDB Transaction／Connection／Lockを保持しない | Instrumented Test |

## 4. Schema／Migration／Failure

| ID | Required acceptance | Evidence |
|---|---|---|
| P2B-MIG-001 | Empty／Ready／Required／Incomplete／Unsupported／Corruptを区別 | Unit Test |
| P2B-MIG-002 | Test Legacy StepがCheckpoint、Marker、Staging全件Validation、Atomic Cutoverを通す | Integration Test |
| P2B-MIG-003 | 変換失敗／中断で旧Active Store不変、Marker残存後は通常Open拒否 | Fault Injection Test |
| P2B-MIG-004 | Target Digest一致時だけRollbackし、Migration後Write相当を拒否 | Integration Test |
| P2B-FAL-001 | Lock／Read-only／Permission／Capacity／Corrupt／UnknownをTyped Safe Errorへ正規化 | Unit Test |
| P2B-FAL-002 | Safe ErrorへPath、SQL、Driver Text、Message本文、Secretを出さない | Assertion＋Scan |

## 5. Lifecycle／Generation／Recovery

| ID | Required acceptance | Evidence |
|---|---|---|
| P2B-LIF-001 | Create／Resume／Pending／Generating／Terminal／Archive遷移がDomain不変条件を維持 | Unit Test |
| P2B-LIF-002 | Pending Userは生成前、Canonical Assistant＋Headは完了後に別CAS Commit | Event／Repository Spy |
| P2B-LIF-003 | Terminal Commit成功後だけTerminal Eventを公開し、失敗時にEphemeral成功なし | Fault Injection Test |
| P2B-LIF-004 | Cancel／Complete競合は一方だけ成立し、Cancelled等へ本文を保存しない | Concurrency Test |
| P2B-MAP-001 | Completed Branch＋Pending Userだけを古い順に既存Inputへ写像 | Unit Test |
| P2B-MAP-002 | 既存入力上限超過でGeneration Call 0、Truncate／Summary／Record変更0 | Unit Test |
| P2B-REC-001 | StartupでPending／Generating＋Active SessionをInterruptedへ確定 | Integration Test |
| P2B-REC-002 | Recovery CAS Conflict／Unknownを有界処理し、完了前Readyにならない | Fault Injection Test |

## 6. Privacy／Compatibility／Recording

| ID | Required acceptance | Evidence |
|---|---|---|
| P2B-PRV-001 | 通常DBにCanonical User／Assistant Final以外を表現・保存しない | Schema＋Fixture Scan |
| P2B-PRV-002 | Thinking、Prompt、RAG Context、Citation本文、Partial、Hidden Original、Secretが保存0 | Sentinel Test |
| P2B-REC-003 | RecordingはDefault OFF、Recorder Binding／Call／Filesystem Artifact 0 | Spy＋Inventory |
| P2B-CMP-001 | Existing `/api/v1/chat/*` Source変更0、Wire／Cancel／Summary／RAG Regression PASS | Git Diff＋Web Tests |
| P2B-CMP-002 | Public Demo／Shared Basic Preview Binding 0、Storage Write 0 | Config Diff＋Regression Test |
| P2B-CMP-003 | Test後Project Root `runtime_data/`作成0、実Runtime Data変更0 | 前後Inventory |

## 7. Quality Gates

| ID | Required acceptance | Command |
|---|---|---|
| P2B-QA-001 | Phase 2-B Target Tests PASS | Handoff記載Target Command |
| P2B-QA-002 | Conversation／Web Regression PASS | `.venv/bin/pytest -q tests/unit/conversation tests/integration/web` |
| P2B-QA-003 | Ruff Format／Check PASS | `.venv/bin/ruff format --check src tests`／`.venv/bin/ruff check src tests` |
| P2B-QA-004 | Mypy PASS | `.venv/bin/mypy` |
| P2B-QA-005 | Full Suite PASS | `.venv/bin/pytest -q` |

## 8. Required Closure Output

```text
Phase 2実装者役 -> Phase 2設計担当者役
  exact changes／test results／acceptance ID map／rollback／findings

Phase 2設計担当者役 -> Controller
  Design Conformance: ACCEPT | REWORK | STOP
  Required failures: NONE | exact IDs
  Deferred items: exact list and current-transition impact

Controller -> User
  Closure Recommendation: GO | ADJUST | STOP
  Human-only action: final acceptance／next authorization／backup when required
```

## 9. Deferred and Non-acceptance Items

Persistent API／UI、List／Resume UX、Retry／Regenerate／Branch UX、Recording Mode Control、Retention／Purge、Encryption、Cloud、Protected Research CaptureはPhase 2-B Acceptanceに含めない。Deferred項目を新EvidenceなしにBlockerへ再活性化しない。

## 10. Related Documents

- [Requirements](../requirements/phase_2_b_conversation_persistence_requirements_ja.md)
- [Architecture](../architecture/phase_2_b_conversation_persistence_architecture_ja.md)
- [ADR](../adr/phase_2_b_conversation_persistence_adr_ja.md)
- [Implementation Handoff](../handoffs/phase_2_b_implementation_handoff_ja.md)
