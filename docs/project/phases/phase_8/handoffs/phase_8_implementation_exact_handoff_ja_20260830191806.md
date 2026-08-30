# Phase 8 Implementation Exact Handoff

```yaml
document_id: phase_8_implementation_exact_handoff_20260830191806
document_type: exact_execution_handoff
document_state: frozen_ready_not_started
language: ja
created_at: 2026-08-30 19:18:06 JST
phase: phase_8
provider: unassigned
role: 設計者兼実装者役
maximum_claim: COMPLETE_CANDIDATE_FOR_USER_MANUAL
implementation_authority: false
git_authority: false
backup_authority: false
phase_8_closure_authority: false
```

## 1. Objective

Phase 8の`Governed Agentic Execution Research Foundation`を、P8-0〜P8-Fの順で実装する。正式Agent Level 1、General Web Search、Generic MCPまたはFull Constitutionを完成済みと主張しない。

## 2. Mandatory Reading Order

1. `docs/project/phases/phase_8/phase_index_ja.md`
2. `docs/project/phases/phase_8/requirements/phase_8_requirements_ja.md`
3. `docs/project/phases/phase_8/architecture/phase_8_architecture_ja.md`
4. `docs/project/phases/phase_8/operations/phase_8_execution_plan_ja.md`
5. `docs/project/phases/phase_8/operations/phase_8_acceptance_matrix_ja.md`
6. `docs/project/phases/phase_7/history/operations/phase_7_minimal_final_closure_ja_20260830191806.md`
7. `docs/project/phases/phase_7/history/operations/phase_7_user_mac_final_rag_citation_context_freshness_manual_acceptance_ja_20260830190930.md`
8. `docs/project/shared/未解決/current_unresolved_findings_registry_ja.md`
9. `docs/project/shared/task_roles/poc_mvp_portfolio_resource_constrained_delivery_and_closure_operating_policy_ja.md`
10. `docs/project/shared/history/planned_work/phase_8_entry_manual_url_fetch_and_llm_evidence_reservation_ja_20260830083225.md`
11. `docs/project/shared/history/planned_work/phase_8_entry_branch_ui_hide_and_archived_chat_management_reservation_ja_20260830175855.md`
12. `docs/project/shared/history/planned_work/phase_8_margpa_dev_agent_level_1_important_gate_only_autonomy_harness_reservation_ja_20260830181055.md`
13. `docs/project/shared/history/planned_work/phase_8_provisional_and_phase_10_full_runtime_agent_constitution_staging_reservation_ja_20260829113647.md`
14. `docs/project/shared/history/planned_work/runtime_constitution_normal_chat_agent_tool_loose_coupling_and_hardcode_avoidance_reservation_ja_20260829114640.md`

Provider固有の運用文書は実際のExecutor確定時にControllerが追加する。旧Task ContextまたはProvider MemoryをRepository正本より優先しない。

## 3. Execution Contract

- P8-0からP8-Fまで成立済みPackageを再実装せず連結する。
- Package BoundaryごとにRecovery Indexを作る。
- Routine報告後もTrue Stop Conditionがなければ継続する。
- Internal Review Cycle 1を実施し、Critical／Major／MVP BlockerだけをReworkする。
- Review Cycle 2でRework結果を確認する。
- Real Network／MCP／External Side Effectが未許可でも、Fixture／Port／UI／Lifecycle／Failure／Regressionを継続し、該当実接続だけNOT RUNへ分離する。
- Source／Test／Config／DocsのMutation InventoryをReturnへ記載する。

## 4. Forbidden Claim／Scope

- Phase 8 Closure、Phase 9開始、Roadmap、Git、Backup。
- 正式Agent Level 1、End-to-EndまたはFull-Cycle完成。
- General／Automatic Web Search。
- Generic Remote MCP、OAuth、任意Tool／Deploy／Git／Network権限。
- Shared Constitution、PADG、Full Runtime Constitution完成。
- Phase 6 Semantic Debt解決。

## 5. Exact Start Gate

本Handoffを読んだだけでは実装を開始しない。Controller／Userが別に次を明示した後だけP8-0-WU-001から開始する。

```text
Phase 8 Governed Agentic Execution Research Foundationを開始する。
```

## 6. Return

Exact Return Handoffに、Acceptance 40件の個別Disposition、Evidence Pointer、Canonical検証、Internal Review、Incident、PARTIAL／NOT RUN、User Manual Test Sheetおよび次の正確なGateを記録し、Controller Independent Review待ちで停止する。
