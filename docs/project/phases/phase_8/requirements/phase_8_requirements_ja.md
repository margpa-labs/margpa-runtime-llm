# Phase 8 要件 — Governed Agentic Execution Research Foundation

```yaml
document_id: phase_8_requirements
document_state: complete_accepted_closed
phase: phase_8
language: ja
created_at: 2026-08-30 19:18:06 JST
authority_owner: Nazuna Research
implementation_scope: poc_mvp_research_foundation
```

## 1. 目的

Phase 8は、LLMへ無制限な行動権限を与えるのではなく、Userが与えたScope、既存Authority、Constitution、Approval、BudgetおよびEvidenceの内側で、限定Toolを複数Step実行できるAgent Runtimeの基盤を作る。

同時に、Phase 7で成立したWeb Fetch PortとCitationを再利用し、Userが明示的に貼ったURLだけを読むManual URL Evidenceを成立させる。

## 2. Functional Requirements

### 2.1 Manual URL Evidence

| ID | 要件 |
|---|---|
| P8-REQ-001 | Web URL取得の既定値をOFFとし、OFF時Network Call 0を維持する。 |
| P8-REQ-002 | Userが明示したPublic `http／https` URLだけをManual Fetch候補とする。 |
| P8-REQ-003 | Credential-bearing URL、Loopback、Private、Link-local、Metadata Endpoint、危険Port／Schemeを拒否する。 |
| P8-REQ-004 | Redirectごとに再検証し、Timeout、Response Size、Content Typeを有界化する。 |
| P8-REQ-005 | JavaScript実行、Cookie／Login、Form送信、File Download、Archive／Media解析を行わない。 |
| P8-REQ-006 | 取得Contentを画面表示し、Untrusted External EvidenceとしてMain Modelへ明示的に渡せる。 |
| P8-REQ-007 | URL、Canonical URL、取得時刻、Content Type、Digest、Source ClassをCitationへ保持する。 |
| P8-REQ-008 | Prompt Injection等のDetectionをEvidence化し、取得成功と内容信頼を同一視しない。 |

### 2.2 UI／Archive Management

| ID | 要件 |
|---|---|
| P8-REQ-009 | Branch Data／API／履歴を保持したまま、Branch操作UIを既定非表示にする。 |
| P8-REQ-010 | Data ControlsへArchive済みChatのLazy一覧、Title、Timestamp、開く、Archive解除を追加する。 |
| P8-REQ-011 | Archive解除後は手動Resumeなしで送信可能なPhase 7契約を維持する。 |
| P8-REQ-012 | 完全削除、Cascade Delete、TTL、一括Delete／Exportを実装済みと表示しない。 |

### 2.3 Provisional Runtime Constitution

| ID | 要件 |
|---|---|
| P8-REQ-013 | Project Root直下`constitution/`に暫定Runtime Constitutionを配置する。 |
| P8-REQ-014 | Stable Rule ID、Revision、Digest、Source Pointer、Capability Viewを持つ。 |
| P8-REQ-015 | Constitution ProviderとGD Providerを並列独立に扱い、ConstitutionをGD群の親へ密結合しない。 |
| P8-REQ-016 | `OFF／OBSERVE／ENFORCE`を比較でき、OFFを`allow all`と解釈しない。 |
| P8-REQ-017 | 通常Chat、Agent、Tool別Viewを生成でき、ViewはAuthorityを追加できない。 |
| P8-REQ-018 | 不明Rule、Digest不一致、Conflictまたは未対応Actionを正直なResultへ収束する。 |
| P8-REQ-019 | GD名、Provider名、User固有PathまたはModel名をAgent CoreへHard-codeしない。 |

### 2.4 Dev Agent／Tool／Approval Harness

| ID | 要件 |
|---|---|
| P8-REQ-020 | UIで通常Chatと`MARGPA Development Agent` Research Previewを切替できる。 |
| P8-REQ-021 | 表示名とStable Capability IDを分離し、後の名称変更をMigrationなしのID破壊にしない。 |
| P8-REQ-022 | Run／Step／State、Plan、Tool Request、Tool Result、Completion／FailureをVersioned Contractで表現する。 |
| P8-REQ-023 | Tool Port／RegistryとNative／MCP Client Adapter Portを分離する。 |
| P8-REQ-024 | Fake／Deterministic Toolまたは安全な限定Local Toolで複数Step実行を証明する。 |
| P8-REQ-025 | `plan_only／manual／risk_based／important_gate_only`を比較可能なApproval Profileとして持つ。 |
| P8-REQ-026 | Important-gate-onlyは事前Envelope内の安全な処理を逐次確認なしで進めるが、Authorityを拡張しない。 |
| P8-REQ-027 | External Write、Network、Cost、不可逆操作、Secret／Privacy、Scope拡張、重大IncidentおよびCompletionを重要Gateとして表現する。 |
| P8-REQ-028 | Provider／Platform側の強制Safety GateをHarnessから自動承認または迂回しない。 |
| P8-REQ-029 | Max Step、Deadline、Retry、Budget、Stop／Cancel、Loop防止、Late Result拒否を持つ。 |
| P8-REQ-030 | Agent／Tool／Constitution／GD／Approval／OutcomeをRequest／Run／Step IDで相関しEvidence化する。 |

### 2.5 Compatibility／Truthfulness

| ID | 要件 |
|---|---|
| P8-REQ-031 | 通常Chat、Local RAG、Citation、Data Controls、Conversation PersistenceをRegressionさせない。 |
| P8-REQ-032 | Disabled／Unavailable／Denied／Timed out／Cancelled／FailedをSuccessと表示しない。 |
| P8-REQ-033 | Level 1完成、Generic MCP、General Web Search、Dynamic Sub-Agent、外部Deployを主張しない。 |

## 3. Scope外

- General Web Search、Automatic Search、Search Account／Credential／Cost運用。
- 認証Site、JavaScript Browser、PDF／Archive／Media／Hostile-site Sandbox。
- 正式なMARGPA Development Agent Level 1、Level 2、Level 3。
- Generic MCP Discovery、OAuth、Remote Side Effect、任意Toolの無制限実行。
- Dynamic Sub-Agent Generation、長時間完全自律、Production Planning。
- 全Docs統合、`docs/project/shared/constitution/`完全版、PADG、Full Runtime Constitution。
- Phase 6／9 Semantic Governance Debtの解消。
- Archive完全削除、Branch Data／API削除。

## 4. MVP停止線

```text
Manual URLは明示操作だけで取得され、OFF時Network 0。
取得ContentはUntrustedで、Citation／DigestとFailureが追跡可能。
Branch UI非表示とArchive一覧／開く／解除がUser画面で成立。
通常ChatとDev Agent Previewを切替可能。
Fake／Deterministic Toolの複数Step RunがEvidence付きで完了／停止可能。
Constitution OFF／OBSERVE／ENFORCEの差が虚偽なく表示される。
Important-gate-onlyが事前Envelope内だけ進み、重要Gateで待機する。
既存Chat／RAG／Citation／Persistenceに重大Regressionがない。
User Manual Candidateへ渡せる。
```
