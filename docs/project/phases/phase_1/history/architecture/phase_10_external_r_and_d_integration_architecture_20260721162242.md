# Phase 10 External Original R&D Integration Architecture

- 文書ID: `phase_10_external_r_and_d_integration_architecture`
- 状態: `accepted_future_reservation`
- 作成日時: `2026-07-21 16:22:42 JST`
- 更新日時: `2026-07-21 16:22:42 JST`
- Snapshot: `20260721162242`
- 作成担当: 設計者役担当Task
- 正本言語: 日本語
- Requirements: [phase_1_ex_external_r_and_d_publication_and_integration_requirements_20260721162242.md](../requirements/phase_1_ex_external_r_and_d_publication_and_integration_requirements_20260721162242.md)
- System Catalog: [phase_10_original_r_and_d_system_catalog_20260721162242.md](../governance/phase_10_original_r_and_d_system_catalog_20260721162242.md)
- supersedes: なし

## 1. Goal

EASA、DLAGSA、OCILNSをMARGPA Runtime LLM Coreから独立させ、Phase 10でAdapterを追加するだけで個別統合できる構造を予約する。

## 2. System Placement

```text
External Original R&D Systems
  ├─ EASA
  │    Exception Aware Safety Architecture
  │         └─ Governance Adapter
  │
  ├─ DLAGSA
  │    Distributed LEA Agentic Governance & Safety Architecture
  │         └─ Governance Adapter
  │
  └─ OCILNS
       Open Cognitive Interaction Ledger Network System
            └─ Ledger Adapter

Governance Adapters ──→ External Governance Provider Port
                         ├─ Registry
                         ├─ Capability
                         └─ Standard Governance Result

Ledger Adapter ──────→ Generic Evidence Ledger Port
                         ├─ Event／Evidence Reference
                         ├─ Verification／Retrieval
                         └─ Handoff／Audit Connection
                                  ↓
              MARGPA Application／Governance／Audit
```

EASA／DLAGSAはGovernance Provider系、OCILNSはEvidence Ledger系として接続する。OCILNSを無理にGovernance Providerとして扱わない。

## 3. Core Dependency Direction

```text
MARGPA Core
  → Generic Port／Contract
  ✕ External R&D Implementation

External Adapter
  → Generic Port Implementation
  → External R&D System
```

- Coreは固有PackageをImportしない。
- Providerなしで起動、会話、既存Governance、Auditが成立する。
- External SystemのDeploy、Storage、RuntimeをCoreへ固定しない。
- 外部Systemは別Process、別Service、同一Process Adapter等へ将来配置できる。

## 4. Registry／Capability

Systemごとに次を宣言可能にする。

- Provider／System ID
- Display Name
- Version／Revision／Hash
- Capability
- Required Input／Output Scope
- Activation Condition
- Timeout／Retry／Failure Policy
- Side Effect
- Data Disclosure Scope
- Health／Availability
- Evidence／Audit Reference

名称はRegistry Metadataとして扱い、Core Logicの分岐条件にしない。

## 5. Configuration

```text
extensions.easa.enabled   = false
extensions.dlagsa.enabled = false
extensions.ocilns.enabled = false
```

上記は概念表現であり最終TOML Schemaではない。

- Default All OFF
- 個別切替
- OFF時はLoad／Call／Writeなし
- ON時はCapability／Dependency Validation
- 無効な組合せはSafe Error
- Effective Configへ反映
- AuditへEnabled Stateを記録
- 将来UIでは研究開発者向け設定

EASA／DLAGSAでは、Enabled Stateと`observe／enforce`等のGovernance Modeを分離する。OCILNSのOperation ModeはOCILNS側Contract確定後に定義する。

## 6. Event／Evidence Boundary

候補となる共通Event：

- Interaction Received
- Model Request／Response
- Tool Request／Execution／Result
- Decision／Delegation／Verification
- Exception／Deviation
- Governance Result／Action
- Handoff／Unresolved Item
- Evidence Reference／Integrity State

Raw Chain of Thoughtの保存を必須にしない。高水準の判断根拠、System Trace、Source、Constraint、Uncertaintyを区別する既存方針を維持する。

## 7. OCILNS Boundary

OCILNSへ渡す候補は、Systemが観測可能で、Policy上記録可能な認知対話Eventである。

- 人の意図と入力
- AI Output
- Tool／External System Event
- Model／Provider／Config
- 前提／制約
- 高水準の判断根拠
- 未解決事項／継承対象
- 順序／時刻
- Integrity／改変検知情報

個人情報、Secret、Raw Thinking、外部Provider規約に反するDataを無条件送信しない。Selective DisclosureとData Minimizationを適用可能にする。

## 8. Failure Isolation

- External System FailureをCore Failureと同一視しない。
- ProfileごとにFail Open／Fail Closed／Degradedを定義する。
- OFF時はExternal Failureの影響を受けない。
- OCILNS Write Failure時に、記録成功を偽装しない。
- EASA／DLAGSAの`observe`結果を`enforce`済みと表示しない。
- Timeout、Retry、Circuit状態をStatus／Auditへ記録できる。

## 9. Testability

- Fake Provider／Fake Ledger Adapter
- ProviderなしBaseline
- System単位ON／OFF Matrix
- Capability不足
- Timeout／Failure／Recovery
- Evidence Reference整合
- No External Call when OFF
- Core Regression
- Config Snapshot／Audit

## 10. Phase 10 Start Condition

- MARGPA Runtime LLM本体が一通り完成している。
- Generic PortとData／Authority Boundaryが安定している。
- External R&D側Interfaceが確定している。
- 公開／非公開、Privacy、Security、Evidence範囲を再Reviewしている。
- ユーザーが個別System統合を許可している。

## 11. Authorization Boundary

本Architectureは将来予約である。Port実装、Config追加、External Call、3 Systemの統合を現在許可しない。
