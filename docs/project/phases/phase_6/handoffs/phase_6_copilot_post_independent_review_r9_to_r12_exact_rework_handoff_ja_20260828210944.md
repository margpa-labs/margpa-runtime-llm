# Phase 6 Copilot Post-Independent-Review R9〜R12 Exact Rework Handoff

```yaml
document_id: phase_6_copilot_post_independent_review_r9_to_r12_exact_rework_handoff_20260828210944
document_type: frozen_exact_rework_handoff
document_state: ready_for_bootstrap
language: ja
created_at: 2026-08-28 21:09:44 JST
authority_owner: プロジェクト責任者兼設計統括者役
target_provider: GitHub Copilot app
target_role: 設計者兼実装者役
task_identity: Copilot_Phase_6_Post_Review_Rework_Task
preserved_packages: P6-RR-R0_to_R8_current_source
first_exact_work_unit: P6-RR-R9-WU-001
remaining_packages: P6-RR-R9_to_R12
maximum_claim: complete_candidate_with_real_provider_authority_gate
implementation_authority: false_until_exact_user_start
phase_6_closure: prohibited
phase_7: prohibited
git: prohibited_including_read_only
network: prohibited
```

## 1. Authority Statement

本書はP6-GOV-020のController Independent Review後に残った差分だけを修正するFrozen Exact Handoffである。同じCopilot Taskを継続する場合も、Fresh Taskを使用する場合も、会話記憶や旧Authorityを正本にしない。

本書を読むだけでは実装Authorityは発生しない。Mandatory Reading／Digest Receipt後、Userが次を明示送信した場合だけ開始する。

```text
Phase 6 Copilot Post-Review R9〜R12 Reworkを開始する。
```

## 2. Canonical Root／Task Boundary

```text
Canonical Root:
<PROJECT_ROOT>

Provider: GitHub Copilot app
Role: 設計者兼実装者役
Controller: Codex プロジェクト責任者兼設計統括者役
Old Context Authority: NONE
```

## 3. Mandatory Reading

指定順に全文読む。Summaryや会話記憶で代替しない。

1. `docs/project/shared/task_roles/copilot_side_designer_implementer_operating_notes_ja.md`
2. `docs/project/shared/task_roles/copilot_side_long_running_automation_companion_ja.md`
3. `docs/project/shared/task_roles/copilot_side_implementation_internal_review_rework_loop_operating_contract_ja.md`
4. `docs/project/phases/phase_6/handoffs/phase_6_post_claude_independent_review_exact_rework_handoff_ja_20260828180240.md`
5. `docs/project/phases/phase_6/handoffs/phase_6_copilot_post_claude_r3_to_r8_exact_continuation_handoff_ja_20260828193037.md`
6. `docs/project/phases/phase_6/handoffs/phase_6_copilot_r3_to_r8_complete_candidate_return_handoff_ja_20260828201804.md`
7. `docs/project/phases/phase_6/history/operations/phase_6_copilot_r8_implementation_freeze_ja_20260828201800.md`
8. `docs/project/phases/phase_6/history/operations/phase_6_copilot_r8_internal_review_cycle_1_finding_ledger_ja_20260828201801.md`
9. `docs/project/phases/phase_6/history/operations/phase_6_copilot_r8_internal_review_cycle_2_final_verification_ja_20260828201802.md`
10. `docs/project/phases/phase_6/history/operations/phase_6_gov020_copilot_r3_to_r8_controller_independent_review_ja_20260828210944.md`
11. `docs/project/shared/history/automation/phase_6_copilot_pilot_repeated_unnecessary_stop_failure_addendum_ja_20260828202127.md`
12. `docs/project/shared/history/automation/copilot_first_long_run_pilot_empirical_automation_and_resource_evidence_ja_20260828210944.md`
13. 本書。

続けて、次のCurrent Source／Testを全文再導出する。

14. `src/margpa_runtime_llm/web/provider_selection_routes.py`
15. `src/margpa_runtime_llm/modules/runtime_model_control/application/provider_selection_controller.py`
16. `src/margpa_runtime_llm/modules/runtime_model_control/application/role_lifecycle_manager.py`
17. `src/margpa_runtime_llm/modules/runtime_model_control/domain/provider_selection.py`
18. `src/margpa_runtime_llm/web/feature_modes_routes.py`
19. `src/margpa_runtime_llm/bootstrap/judge_live_integration.py`
20. `src/margpa_runtime_llm/bootstrap/repair_live_integration.py`
21. `src/margpa_runtime_llm/bootstrap/web_application.py`
22. `src/margpa_runtime_llm/modules/conversation/application/conversation_generation.py`
23. `src/margpa_runtime_llm/modules/runtime_governance/application/semantic_runtime.py`
24. `src/margpa_runtime_llm/modules/runtime_governance/domain/semantic_runtime.py`
25. `src/margpa_runtime_llm/web/runtime_governance_routes.py`
26. `src/margpa_runtime_llm/modules/evaluation/domain/stage_budget.py`
27. `src/margpa_runtime_llm/modules/evaluation/application/failure_presentation.py`
28. `frontend/src/types.ts`
29. `frontend/src/components/FeatureModesPanel.tsx`
30. `frontend/src/components/ProviderSelectionPanel.tsx`
31. `tests/integration/web/test_provider_selection_role_atomicity.py`
32. `tests/unit/bootstrap/test_judge_live_integration.py`
33. `tests/unit/bootstrap/test_judge_live_integration_dispatch_router.py`
34. `tests/unit/conversation/test_conversation_generation_judge_hook.py`
35. `tests/unit/runtime_governance/test_semantic_runtime.py`
36. `tests/unit/web/test_runtime_governance_routes.py`
37. `tests/unit/evaluation/test_stage_budget_and_failure_presentation.py`
38. `frontend/src/components/FeatureModesPanel.test.tsx`
39. `frontend/src/components/ProviderSelectionPanel.test.tsx`

## 4. Preserved／Superseded／Open

### Preserved

- R0〜R8のCurrent Source／TestとAppend-only Recovery。
- P6-CODEX-063の明示Dispatch Router。
- P6-CODEX-064の109 Criterion Fixture／Count／Projection骨格。
- Provider Stage Budget Domain、Failure Presentation表、Bounded Poll、Identity Field。
- Copilot Canonical Verification結果はHistorical Candidate Evidenceとして保持。
- Historical Incident／Automation Failure／Authority Gate。

### Superseded

- Copilot ReturnのComplete Candidate Claim。
- P6-CODEX-062／065／066／067／068をCLOSEDとするClaim。
- Open Major 0を示唆するClaim。

### Current Open

```text
P6-CODEX-069: Atomic Provider Transition / Rollback
P6-CODEX-070: Provider-owned Runtime Deadline / Budget Enforcement
P6-CODEX-071: Frozen-language Final Fallback without hardcoded English escape
P6-CODEX-072: Request-ID Recording Correlation
P6-CODEX-073: Acceptance / Internal Review / Return Contract
```

## 5. Exact Rework Packages

### P6-RR-R9 — Atomic Provider Transition

- R9-WU-001：Judge／Guard変更のUnified Transition StateとLock Boundaryを再導出する。
- R9-WU-002：Mode OFF中の選択はConfigured-onlyとし、Mode ON中の変更は新Provider Preflight／Activation成功後だけCommitする。
- R9-WU-003：成功時にConfigured／Active／Mode／Lifecycleを一つの外部可視Transactionへ収束させる。
- R9-WU-004：Preflight、Load、Deactivate、UnloadまたはMode Commit失敗時、旧Configured／Active／Mode／AdapterへRollbackする。
- R9-WU-005：Status ReaderがTransaction途中の`Mode ON / Active none`を観測しないBoundaryを実装する。
- R9-WU-006：Judge／Guardの両RoleへFailure Injectionを追加する。
- R9-WU-007：S2〜S6を明示Test／Matrixへ固定する。
- R9-WU-008：Package Recovery Indexを作成する。

### P6-RR-R10 — Runtime Budget／Failure Finalization

- R10-WU-001：Frozen Active Providerから解決したStage BudgetがCaller Deadlineを所有するよう修正する。
- R10-WU-002：Prompt／Inference／Decode／Repair／Rejudgeを後検査だけでなく実行上Boundする。
- R10-WU-003：Built-inはModel Call 0／LLM Wait 0を維持する。
- R10-WU-004：Repair RejudgeへFrozen Adapter／Provider／Role／Budgetをexactly onceで継承する。
- R10-WU-005：Provider変更、Timeout、Cancel後のLate Publishを拒否する。
- R10-WU-006：Conversation Layerの英語固定`SEMANTIC_ENFORCEMENT_SAFE_FALLBACK`依存をUser-facing経路から除く。
- R10-WU-007：Hook例外、None、空Resultを含む全Final経路をFrozen Language＋Failure Classへ収束させる。
- R10-WU-008：S9、S12、S13、S17を明示Testへ固定する。
- R10-WU-009：Package Recovery Indexを作成する。

### P6-RR-R11 — Request-ID Observability／Recording Correlation

- R11-WU-001：Judge Result、Turn Recording、Judge Evidence RecordingをRequest IDでJoinするResponse Contractを作る。
- R11-WU-002：同じRequest IDのOutcomeだけを単一Correlation Summaryへ表示する。
- R11-WU-003：別Requestの最新RecordingはHistorical／Unmatchedとして分離し、Currentへ混入しない。
- R11-WU-004：Request ID、時刻、Frozen Modes、Configured／Active／Executed、Budget、Judge Outcome、Final Disposition、Failure、二Recording Outcomeを表示する。
- R11-WU-005：Recording OFFはCall 0／Current Recordingなしとし、古いRecordingをCurrent扱いしない。
- R11-WU-006：既存2秒PollとUnmount Cleanupを維持する。
- R11-WU-007：S14〜S16を明示Testへ固定する。
- R11-WU-008：Package Recovery Indexを作成する。

### P6-RR-R12 — Contract-complete QA／Return

- R12-WU-001：R9〜R11 Focused Backend／Frontendを実行する。
- R12-WU-002：S1〜S17を明示Matrix化し、各Test Path／Test Name／結果を付ける。
- R12-WU-003：Original Acceptance 40＋Delta Acceptance 26をID単位で全66件再導出する。
- R12-WU-004：Exact Changed File Inventoryと各SHA-512を作る。
- R12-WU-005：Identity、Budget／Rejudge、109 Criterion、Failure Language、Recording Correlation Matrixを作る。
- R12-WU-006：Implementation Freezeを作る。
- R12-WU-007：Requirement-by-Requirement、Cross-component、Failure Injection、Negative Pathを含むInternal Review Cycle 1を実行する。
- R12-WU-008：FindingがあればReworkし、Cycle 2で再確認する。Findingがない場合もEvidenceを省略しない。
- R12-WU-009：Canonical Mypy／Ruff／Backend Full／Frontend Typecheck・Lint・Test・Buildを実行する。
- R12-WU-010：R12 Final RecoveryとExact Return Handoffを作成する。

## 6. Automation／Recovery Control

Copilot Pilotでは不要停止が少なくとも4回発生した。次を必須とする。

1. 各Work Unit開始前または直後にAppend-only Checkpointを残す。
2. 各Package Entry／FinalでRecovery Indexを残す。
3. Long Command、Full Test、Frontend Build、CompactionまたはResource Stop前にCurrent Recoveryを確定する。
4. Progress報告は停止理由ではない。報告後、そのまま次WUへ進む。
5. Test Failure、Finding、難度、Authority-dependent Real Gateまたは長時間は停止理由ではない。
6. Copilot UIがOS Temporary Pathを表示しただけではRoot外Actionと判定しない。Copilot自身のCommand／Tool Actionとの因果を確認する。
7. Context／Credit／SessionのPlatform Hard Stopが発生した場合は、最後の成立Boundary、Active Process 0、Exact Next WUをRecoveryへ書いてSTOPPED_SAFEで返す。
8. Userへ不要な確認を求めず、Frozen Contract内の可逆な判断は自走する。

## 7. Mutation／Tool Boundary

Exact Start後に許可：

- R9〜R12対象Source／Test／Frontend／Generated Static／Config。
- Project内Task-owned Temp／Cache／Log。
- Phase 6 Append-only Index／Operations／Handoff。
- Copilot Pilotの継続Evidence。
- Active Scopeに必要なFocused／Static／Regression／Build。

禁止：

- Git Read／Mutation／GitHub操作。
- Network／Web／MCP／外部Account。
- Provider Memory、User `runtime_data/`。
- Project Root外Read／Write／List／Stat／Command／Temp／Cache／Log。
- Real Model Artifact／Load／Inference。
- Backup、Roadmap、Stable Shared Rule、Public Docs、Constitution。
- Phase 6 Closure、Phase 7。
- Historical Evidenceの上書き／削除。

Task-owned Temp：

```text
.venv/.t/phase_6_copilot_post_review_r9_r12_20260828210944/
```

## 8. True Stop Conditions

次だけで停止する。

- Authorized Root外Actionまたは成立可能性。
- Git、Network、Provider Memory、User Data、Real Modelまたは外部Accountへの未許可接触。
- Secret／Credential／Privacyへの予期しない接触。
- Contract Digest不一致。
- Current SourceがPreserved Baselineと競合し、差分継続不能。
- 不可逆／Destructive Actionが必要。
- Critical Integrity Failure。
- User明示Stop／Scope変更／Resource Stop。
- Platform Hard StopまたはActive Processを安全に収束不能。

## 9. Return Contract

最低限、次をすべて含む。

- Provider／Role／Task IdentityとActive Contract Digest。
- R9〜R12のWU／Package Dispositionと全Recovery Path。
- Exact Changed File Inventoryと各SHA-512。
- P6-CODEX-069〜073と再Openした062／065／066／067／068のDisposition。
- S1〜S17全件Matrix。
- Original 40＋Delta 26全66件Acceptance。
- Configured／Active／Executed／Recorded／Displayed Identity Matrix。
- Provider別実Budget／Repair Rejudge Matrix。
- 109 Criterion Count／Disposition／Reason Matrix。
- Failure Class別Language Matrix。
- Request-ID Recording Correlation Matrix。
- Implementation Freeze、Internal Review各Cycle、Finding／Rework Ledger。
- Canonical VerificationのExact Command Scope／Count／Exit。
- Root外／Git／Network／Provider Memory／runtime_data／Model／Temporary Inventory。
- Real Model／BrowserのPASS／PARTIAL／NOT RUN／User Gate。
- Open Critical／Major／Non-critical。

最大ClaimはComplete Candidateまで。Phase 6 Closure、Git、Backup、RoadmapまたはPhase 7へ進まない。
