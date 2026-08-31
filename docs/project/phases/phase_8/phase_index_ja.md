# MARGPA Runtime LLM Phase 8 Index

```yaml
document_id: phase_8_index
document_state: complete_accepted_closed
phase: phase_8
language: ja
created_at: 2026-08-30 19:18:06 JST
authority_owner: Nazuna Research
milestone: Governed Agentic Execution Research Foundation
design: complete
implementation: complete
user_manual: pass
formal_closure: complete
final_acceptance: 39_pass_1_partial_40_total
```

## Current Decision

Phase 8は次の4領域を、交換可能なPort、正直なFailure、停止／EvidenceおよびUser実画面確認を持つResearch Foundationとして成立させ、2026-08-31に`COMPLETE／ACCEPTED／CLOSED`となった。

1. Userが明示したPublic `http／https` URLのManual Fetch／表示／Untrusted Evidence／Citation。
2. Branch UIの可逆的非表示と、Data Controls内のArchive一覧／開く／解除。
3. Project Root直下`constitution/`のProvisional Runtime Constitutionと`OFF／OBSERVE／ENFORCE`比較基盤。
4. 通常Chat／MARGPA Dev Agent切替、Tool Registry／Port、限定Tool、Approval／Autonomy Harness、Run／Step／EvidenceのResearch Preview。

Phase 8は正式な自律開発Agent完成を主張するPhaseではない。全Docs統合、Shared Constitution完全版、PADG Package、Full Runtime Constitution、General Web Searchまたは正式Agent Level 1を完了済みと主張しない。

## Final Acceptance

```text
PASS     39
PARTIAL   1  P8-ACC-038 GD／Guard correlation on model-output-producing Agent execution
TOTAL    40
```

Manual URL Evidence、Archive管理、Branch UI既定非表示、Provisional Runtime Constitution、Dev Agent Fixture Workspace、Tool／Completion Gate、Authorization Envelope、Run PersistenceおよびUser Mac Manual Acceptanceは成立した。P8-ACC-038の既知PARTIALはFoundation境界を正直に表し、Phase 9へ渡す。未解決0件や正式Agent Level 1はClosure条件ではない。

## Canonical Design

- [Requirements](requirements/phase_8_requirements_ja.md)
- [Architecture](architecture/phase_8_architecture_ja.md)
- [Execution Plan](operations/phase_8_execution_plan_ja.md)
- [Acceptance Matrix](operations/phase_8_acceptance_matrix_ja.md)
- [Design／Execution Freeze](history/operations/phase_8_design_and_execution_freeze_ja_20260830191806.md)
- [Implementation Exact Handoff](handoffs/phase_8_implementation_exact_handoff_ja_20260830191806.md)
- [READY Receipt](history/operations/phase_8_ready_receipt_ja_20260830191806.md)
- [Phase 7 Closure／Phase 8 READY Canonical Verification](../phase_7/history/operations/phase_7_closure_phase_8_ready_canonical_verification_receipt_ja_20260830191806.md)
- [Phase 8 Minimal Final Closure](history/operations/phase_8_minimal_final_closure_ja_20260831213232.md)
- [Phase 8 Closure／Phase 9 READY Canonical Verification](history/operations/phase_8_closure_phase_9_ready_canonical_verification_receipt_ja_20260831213232.md)
- [Final Closure Recovery](history/index/phase_8_final_closure_and_phase_9_ready_recovery_ja_20260831213232.md)

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

## Closureと次Phase開始の分離

Phase 8 ClosureはPhase 9 Source実装、Real Model Load、Network、外部ToolまたはMCP Authorityを生成しない。Phase 9はREADY／NOT STARTEDであり、User Backup、Preflightおよび別のStart Authorizationを必要とする。
