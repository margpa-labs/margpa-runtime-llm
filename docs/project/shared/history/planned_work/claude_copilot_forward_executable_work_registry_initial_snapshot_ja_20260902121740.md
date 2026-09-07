# Claude／Copilot 前倒し可能作業Registry Initial Snapshot

```yaml
document_id: claude_copilot_forward_executable_work_registry_initial_snapshot_20260902121740
document_type: append_only_registry_snapshot
document_state: accepted_initial_snapshot
language: ja
created_at: 2026-09-02 12:17:40 JST
owner: Nazuna Research
source_registry: docs/project/shared/operations/claude_copilot_forward_executable_work_registry_ja.md
execution_authority: false
```

## 1. Initial Decision

Claude／Copilot向け前倒し作業は、Providerが自律的に選択するBacklogではなく、User／Controllerが一件ずつExact Handoffで割り当てるCatalogとして管理する。

同時MutationはDefaultで禁止し、次の直列経路を基本とする。

```text
User／Controller Assignment
-> Single Active Executor
-> Recovery／Exact Return
-> ControllerまたはUser Disposition
-> Next Assignment
```

## 2. Initial Catalog

- Phase 9-1 Lightweight Judge選定／取得。
- Phase 9-1 Judge基盤／Semantic 109／Main Runtime Governance ENFORCE Long-run。
- Controller Findingに限定したRegression Guard。
- Test Hermeticity／Fixture隔離。
- 対象を固定したMypy／Ruff Debt解消。
- Phase 10 Docs Source InventoryとConstitution 3系統Traceability準備。
- 内部Observability UIのDocs-only設計。
- Provider Resource Evidenceの比較可能な正規化。
- Recovery／Handoff／IndexのDocs-only整合。

Network、Model Artifact、Dependency、User Data、Git、Backup、ClosureおよびPhase移行は、個別Handoffに明記しない限り許可しない。

## 3. Initial Provider Position

ClaudeはLong-run／Architecture／Cross-module Review、Copilotは小Work Unit／Regression／Mechanical Fixへ優先する。ただしこれは能力の恒久的順位ではなく、2026-09-02時点の観測とResource Costに基づくRoutingである。

