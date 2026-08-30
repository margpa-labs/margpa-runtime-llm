# MARGPA Runtime LLM Phase 8 Index

```yaml
document_id: phase_8_index
document_state: ready_not_started
phase: phase_8
language: ja
created_at: 2026-08-30 19:18:06 JST
authority_owner: Nazuna Research
milestone: Governed Agentic Execution Research Foundation
design: accepted_frozen
implementation: not_started
activation: not_armed
```

## Current Decision

Phase 7はLocal Corpus、Current Evidence、Citation、Data Controls、Conversation継続性およびWeb Port／Security ScaffoldをPoC／MVP停止線まで成立させ、User Mac Manual Acceptanceを通過して`COMPLETE／ACCEPTED／CLOSED`となった。

Phase 8は、正式な自律開発Agent完成を主張するPhaseではない。次の4領域を、交換可能なPort、正直なFailure、停止／EvidenceおよびUser実画面確認を持つResearch Foundationとして構築する。

1. Userが明示したPublic `http／https` URLのManual Fetch／表示／Untrusted Evidence／Citation。
2. Branch UIの可逆的非表示と、Data Controls内のArchive一覧／開く／解除。
3. Project Root直下`constitution/`のProvisional Runtime Constitutionと`OFF／OBSERVE／ENFORCE`比較基盤。
4. 通常Chat／MARGPA Dev Agent切替、Tool Registry／Port、限定Tool、Approval／Autonomy Harness、Run／Step／EvidenceのResearch Preview。

Phase 8は全Docs統合、Shared Constitution完全版、PADG Package、Full Runtime Constitution、General Web Searchまたは正式Agent Level 1を完了済みと主張しない。

## Canonical Design

- [Requirements](requirements/phase_8_requirements_ja.md)
- [Architecture](architecture/phase_8_architecture_ja.md)
- [Execution Plan](operations/phase_8_execution_plan_ja.md)
- [Acceptance Matrix](operations/phase_8_acceptance_matrix_ja.md)
- [Design／Execution Freeze](history/operations/phase_8_design_and_execution_freeze_ja_20260830191806.md)
- [Implementation Exact Handoff](handoffs/phase_8_implementation_exact_handoff_ja_20260830191806.md)
- [READY Receipt](history/operations/phase_8_ready_receipt_ja_20260830191806.md)
- [Phase 7 Closure／Phase 8 READY Canonical Verification](../phase_7/history/operations/phase_7_closure_phase_8_ready_canonical_verification_receipt_ja_20260830191806.md)

## Package Map

```text
P8-0  Entry／As-built／Authority Freeze
P8-A  Manual URL Fetch／Evidence
P8-B  Entry UI Simplification／Archive Management
P8-C  Provisional Runtime Constitution
P8-D  Dev Agent／Tool／Approval Harness Foundation
P8-E  Integration／Lifecycle／Evidence／Persistence
P8-F  Internal Review／Canonical Verification／User Manual Candidate
```

## Known Inherited Debt

- Selene、Qwen3Guard、Semantic 109、Built-in意味評価、Judge／Repair Golden PathはPhase 9。
- Conversation History由来の古いFact再出力と言語DriftはPhase 9。
- General Web Search／Automatic Search、正式Agent Level 1〜3、Generic MCP、外部Side EffectはPhase 11以降。
- 全Docs統合、Shared Constitution、PADG、Full Runtime Constitutionおよび大規模UI統合はPhase 10。

正本は`docs/project/shared/未解決/current_unresolved_findings_registry_ja.md`および各Planned Workとする。

## READYと開始の分離

本Indexの`READY`は設計・工程・Acceptance・Handoffが開始可能な状態であることだけを意味する。Phase 8 Source Mutation、Network、外部Tool、MCP Server、Gitまたは実行権限を生成しない。
