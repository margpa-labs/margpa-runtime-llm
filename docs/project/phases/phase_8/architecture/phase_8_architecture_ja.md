# Phase 8 Architecture — Governed Agentic Execution Research Foundation

```yaml
document_id: phase_8_architecture
document_state: complete_accepted_closed
phase: phase_8
language: ja
created_at: 2026-08-30 19:18:06 JST
architecture_style: modular_monolith_ports_and_adapters
```

## 1. Component Boundary

```text
Mode Selector
  ├─ Normal Chat Runtime
  └─ Dev Agent Preview
       ├─ Run Orchestrator
       ├─ Step／Budget／Cancellation
       ├─ Tool Registry／Tool Port
       │    ├─ Fake／Deterministic Tool Adapter
       │    ├─ Limited Native Tool Adapter
       │    └─ MCP Client Adapter Port（Phase 8はPort／Fixture中心）
       ├─ Constitution Provider ─┐
       ├─ Governance Providers ─┼─ Generic Decision Resolver
       ├─ Policy／Authority ─────┤
       └─ Approval Harness ──────┘
            └─ Execution／Result／Evidence
```

Constitution、GD、Policy、Approvalは互いのAuthorityを生成せず、Versioned Generic ResultをResolverへ渡す。Agent Coreは特定GD名、Provider、ModelまたはTool SDKへ依存しない。

## 2. Manual URL Evidence Flow

```text
User明示URL
  -> URL Parse／Normalize
  -> Scheme／Host／Address／Port Gate
  -> Consent／Mode Gate
  -> Bounded Fetch Port
  -> Redirect Revalidation
  -> Size／Timeout／Content-type Gate
  -> Text Normalizer
  -> Untrusted Evidence
  -> Screen Presentation／Main Model Context／Citation Persistence
```

Network AuthorityはURL Fetch Tool固有であり、Dev Agent全体のAuthorityではない。URL取得とGeneral Searchを同一視しない。

## 3. Canonical Contracts

- `AgentCapabilityIdentity`：Stable ID、Display Name、Revision。
- `AgentRun`：Run ID、Conversation ID、Profile、Frozen Envelope、State。
- `AgentStep`：Step ID、Intent、Tool Request、Decision、Result、Disposition。
- `ToolDescriptor`：Tool ID、Input Schema、Side Effect Class、Required Authority、Budget。
- `AuthorizationEnvelope`：Allowed Scope、Actions、Resource、Expiry、Gate Conditions。
- `ApprovalDecision`：Profile、Requirement、Decision、Actor、Timestamp。
- `ConstitutionManifest`：Revision、Digest、Rule Source、Capability View。
- `GovernanceDecisionEnvelope`：Provider、Rule／Finding、Mode、Recommendation、Action、Evidence。
- `ExternalUrlEvidence`：Canonical URL、Fetched At、Content Type、Digest、Transformation、Trust Label。

## 4. Approval Profiles

```text
plan_only:
  Plan／Previewだけ。Tool Execution 0。

manual:
  Side Effect前にUser Approval。

risk_based:
  Risk ClassとAuthorityに応じてApproval。

important_gate_only:
  Frozen Envelope内の安全なRead／Edit／Test／Bounded Reworkは継続。
  External Write、Network、Cost、不可逆操作、Secret／Privacy、Scope拡張、
  重大Incident、Completion等でUserを呼ぶ。
```

Platformが強制するSafety Gateは上記Profileと別Contractであり、Harnessは自動承認しない。

## 5. Constitution／GD Loose Coupling

```text
Constitution Provider ─┐
ARGD Provider ─────────┤
DAGD Provider ─────────┤
Unknown GD Provider ───┼─ Generic Resolver ─ Policy／Authority ─ Approval ─ Action
Deterministic Policy ──┘
```

- `constitution/`はPhase 8暫定Runtime Package。
- `docs/project/shared/constitution/`はPhase 10で全Docs二周後に作る開発運用正本。
- 17 JSON Source／18 Logical GDは候補Sourceであり、すべてをPhase 8で意味実行可能にするClaimではない。
- Conflict、Unsupported、UnknownはTyped Resultへ収束し、黙ってPassしない。

## 6. UI Boundary

```text
Main Surface
  Mode: Chat | MARGPA Dev Agent
  Agent Run／Step／Gate／Stop

Settings
  Data Controls
    Archived Chats: Lazy List／Open／Unarchive
  Constitution／Agent／Tool Research Controls

Conversation Turn
  Branch controls: default hidden
  Branch data/API: preserved
```

Phase 10後半のRight-side Observatoryや大規模Settings再編をPhase 8へ持ち込まない。

## 7. Lifecycle／Failure

Agent Runは`created → planning → awaiting_gate／running → completed／failed／cancelled`を持つ。Stop／Shutdownは新Step受付を止め、Tracked Worker完了または明示Failureを待つ。Cancel後のLate ResultはCurrentへPublishしない。

Failure例：

- `url_fetch_disabled`
- `url_rejected`
- `redirect_rejected`
- `content_unsupported`
- `tool_unavailable`
- `authority_denied`
- `approval_required`
- `constitution_mismatch`
- `governance_unresolved`
- `budget_exceeded`
- `deadline_exceeded`
- `cancelled`

## 8. Persistence／Evidence

Raw Secret、Credential、Provider MemoryまたはRaw ThinkingをEvidenceへ保存しない。Run／Step／Tool／Approval／Constitution／Governance／Final DispositionをID相関し、Reload／Restart後にCurrentとHistoricalを区別して再構成する。
