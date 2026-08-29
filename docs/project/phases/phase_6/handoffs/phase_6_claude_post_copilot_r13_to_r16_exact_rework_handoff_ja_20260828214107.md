# Phase 6 Claude Post-Copilot R13〜R16 Exact Differential Rework Handoff

```yaml
document_id: phase_6_claude_post_copilot_r13_to_r16_exact_rework_handoff_20260828214107
document_type: frozen_exact_differential_rework_handoff
document_state: ready_for_bootstrap
language: ja
created_at: 2026-08-28 21:41:07 JST
authority_owner: Codex_プロジェクト責任者兼設計統括者役
target_provider: Claude
target_role: 設計者兼実装者役
task_identity: Fresh_Claude_Phase_6_Post_Copilot_Rework_Task
preserved_baseline: P6_RR_R0_to_R8_plus_controller_accepted_R9_to_R12_parts
first_exact_work_unit: P6-RR-R13-WU-001
remaining_packages: P6-RR-R13_to_R16
maximum_claim: complete_candidate_with_real_provider_and_user_manual_gates
implementation_authority: false_until_exact_user_start
phase_6_closure: prohibited
phase_7: prohibited
git: prohibited_including_read_only
network: prohibited
```

## 1. Authority Statement

本書はP6-GOV-021後に残った差分だけをClaudeが実装・検証・自己Review・ReworkするFrozen Contractである。旧Claude／Copilot Taskの会話Context、Memory、Authority、未完了推測またはComplete Claimを継承しない。

本書のReadだけでは実装Authorityは発生しない。Mandatory ReadingとDigest Receiptの後、Userが次を送信した場合だけ開始する。

```text
Phase 6 Claude Post-Copilot R13〜R16 Reworkを開始する。
```

## 2. Canonical Root／Identity

```text
Canonical Root:
<PROJECT_ROOT>

Provider: Claude
Role: 設計者兼実装者役
Controller: Codex プロジェクト責任者兼設計統括者役
Old Context / Authority Inheritance: NONE
```

## 3. Mandatory Reading

指定順に全文読む。Summary、過去会話、Provider Memoryまたは先行Task Claimで代替しない。

### Stable Role／Automation Contract

1. `docs/project/shared/task_roles/claude_side_design_governor_operating_notes_ja.md`
2. `docs/project/shared/task_roles/claude_side_long_running_automation_companion_ja.md`
3. `docs/project/shared/task_roles/claude_side_implementation_internal_review_rework_loop_operating_contract_ja.md`

### Phase 6 Contract／Manual／Controller Evidence

4. `docs/project/phases/phase_6/history/operations/phase_6_gov017_user_mac_provider_semantic_recording_manual_acceptance_evidence_ja_20260827211749.md`
5. `docs/project/phases/phase_6/history/operations/phase_6_gov018_user_mac_provider_false_activation_and_execution_identity_addendum_ja_20260827215158.md`
6. `docs/project/phases/phase_6/history/operations/phase_6_gov019_claude_post_manual_production_wiring_delta_controller_independent_review_ja_20260828180240.md`
7. `docs/project/phases/phase_6/handoffs/phase_6_post_claude_independent_review_exact_rework_handoff_ja_20260828180240.md`
8. `docs/project/phases/phase_6/history/operations/phase_6_gov020_copilot_r3_to_r8_controller_independent_review_ja_20260828210944.md`
9. `docs/project/phases/phase_6/handoffs/phase_6_copilot_post_independent_review_r9_to_r12_exact_rework_handoff_ja_20260828210944.md`
10. `docs/project/phases/phase_6/handoffs/phase_6_copilot_r9_to_r12_exact_return_handoff_ja_20260828212032.md`
11. `docs/project/phases/phase_6/history/index/phase_6_copilot_r12_final_recovery_index_ja_20260828212032.md`
12. `docs/project/phases/phase_6/history/operations/phase_6_copilot_r12_internal_review_finding_ledger_ja_20260828212032.md`
13. `docs/project/phases/phase_6/history/operations/phase_6_copilot_r9_path_boundary_incident_ja_20260828212032.md`
14. `docs/project/phases/phase_6/history/operations/phase_6_gov021_copilot_r9_to_r12_controller_independent_review_ja_20260828214107.md`
15. 本書。

### Current Source

16. `src/margpa_runtime_llm/web/provider_selection_routes.py`
17. `src/margpa_runtime_llm/web/feature_modes_routes.py`
18. `src/margpa_runtime_llm/bootstrap/configuration_control.py`
19. `src/margpa_runtime_llm/bootstrap/web_application.py`
20. `src/margpa_runtime_llm/bootstrap/judge_live_integration.py`
21. `src/margpa_runtime_llm/bootstrap/repair_live_integration.py`
22. `src/margpa_runtime_llm/bootstrap/recording_live_integration.py`
23. `src/margpa_runtime_llm/bootstrap/runtime_governance.py`
24. `src/margpa_runtime_llm/modules/runtime_model_control/application/provider_selection_controller.py`
25. `src/margpa_runtime_llm/modules/runtime_model_control/application/role_lifecycle_manager.py`
26. `src/margpa_runtime_llm/modules/runtime_model_control/domain/provider_selection.py`
27. `src/margpa_runtime_llm/modules/evaluation/application/judge_mode_controller.py`
28. `src/margpa_runtime_llm/modules/evaluation/domain/stage_budget.py`
29. `src/margpa_runtime_llm/modules/evaluation/application/failure_presentation.py`
30. `src/margpa_runtime_llm/modules/guardrail_governance/application/mode_controller.py`
31. `src/margpa_runtime_llm/modules/conversation/application/conversation_generation.py`
32. `frontend/src/types.ts`
33. `frontend/src/components/FeatureModesPanel.tsx`
34. `frontend/src/components/ProviderSelectionPanel.tsx`

### Current Tests

35. `tests/integration/web/test_provider_selection_role_atomicity.py`
36. `tests/integration/web/test_feature_modes_routes.py`
37. `tests/unit/bootstrap/test_judge_live_integration.py`
38. `tests/unit/bootstrap/test_judge_live_integration_dispatch_router.py`
39. `tests/unit/bootstrap/test_repair_live_integration.py`
40. `tests/unit/bootstrap/test_recording_live_integration.py`
41. `tests/unit/conversation/test_conversation_generation_judge_hook.py`
42. `tests/unit/evaluation/test_stage_budget_and_failure_presentation.py`
43. `frontend/src/components/FeatureModesPanel.test.tsx`
44. `frontend/src/components/ProviderSelectionPanel.test.tsx`

## 4. Preserved／Superseded／Open

### Preserved

- P6-RR-R0〜R8 Current Source／Test。
- P6-CODEX-063の明示Dispatch Router。
- P6-CODEX-064の109 Criterion Fixture／Projection骨格。
- Copilot R9〜R12で追加されたCandidate Preflight-first、Frozen Run Budget、JA／EN Conversation Fallback、base request_id Recording、Current／Unmatched UI骨格。
- Controller Focused 104 Backend、16 Frontend、Mypy 14、Ruff PASS。
- Historical Real Model／Browser Gate、Incident、Authority不足。

### Superseded

- Copilot R9〜R12 Complete Candidate Claim。
- P6-CODEX-069〜073を全CLOSEDとするClaim。
- Original 40＋Delta 26をCanonical Regressionだけで全PASSとする一括Claim。
- Root-outside Action 0を示唆するClaim。

### Current Open

```text
P6-CODEX-074: Unified Provider / Mode / Lifecycle Transaction
P6-CODEX-075: Real Stage-owned Deadline / Budget Enforcement
P6-CODEX-076: Turn-frozen Language independent of Semantic Snapshot
P6-CODEX-077: Judge-independent Request-ID Recording Correlation
P6-CODEX-078: Contract-complete QA / Return
P6-CODEX-079: Historical Copilot Root Boundary Incident accounting
```

## 5. Exact Packages

### P6-RR-R13 — Unified Role Transition Transaction

- R13-WU-001：Judge／GuardについてProvider Selection、Mode Apply、Lifecycle、Status Readが共有するRole Transition Coordinator／Lock Boundaryを設計する。
- R13-WU-002：Provider RouteのMode SnapshotとConfigured CommitのTOCTOUを除く。
- R13-WU-003：Mode OFF→ONとProvider変更が競合しても`Mode ON / Active none`を外部観測不能にする。
- R13-WU-004：Provider変更中のMode OFF／OBSERVE／ENFORCE変更を直列化し、旧または新の完全Tupleだけを返す。
- R13-WU-005：Provider Selection GET、Feature Modes GET、Mode Apply、Provider ApplyがTransition中間状態を投影しないようにする。
- R13-WU-006：Preflight／Candidate Load／Old Unload／Selection Commit／Mode Commit／Rollback各Failure InjectionをJudge／Guard双方に追加する。
- R13-WU-007：Old Unload部分失敗時は利用可能と捏造せず、再Load成功を確認するかMode OFF＋DEGRADED／FAILEDへ正直に収束する。
- R13-WU-008：Active Turn Drain、No-op Reselect、Shutdown、Concurrent Status Reader、Concurrent Mode ApplyをRegression化する。
- R13-WU-009：Package Recovery Indexを作成する。

### P6-RR-R14 — Stage Budget／Built-in／Frozen Language

- R14-WU-001：Prompt Build、Judge Inference、Decode、Repair Generation、RejudgeごとにStage Start／Deadline／Cancel／Terminal Ownerを持つ実行契約を作る。
- R14-WU-002：各Stageが自身のBudgetを超えた時点でCancellationを発火し、後続Stageへ他Stageの余剰時間を流用しない。
- R14-WU-003：BackendがCancellationを無視してもPresented Final／Evidence／Last ResultをLate Publish不能にし、Model Lease／Workerは実完了まで追跡する。
- R14-WU-004：OBSERVE BackgroundにもStage Deadline Ownerを持たせる。未追跡Thread／Timerを残さない。
- R14-WU-005：Built-in DeterministicはModel Call 0、LLM Wait 0を維持し、0ms Pipeline Deadline Raceを起こさず確定的に終端する。
- R14-WU-006：`JudgeCompletionContext`へTurn開始時Response Languageを追加し、Semantic SnapshotがなくてもJA／ENを正しくFreezeする。
- R14-WU-007：Judge、Repair、Rejudge、Hook例外、None、空Decision、Provider Unavailable、Malformed、Timeout、Cancel、Budget、Model Busyの全Failure Presentationへ同じFrozen Languageを継承する。
- R14-WU-008：Repair Rejudgeの`EvaluationCase.language="en"`固定を除き、Frozen Languageを継承する。
- R14-WU-009：Main Governance OFF＋Judge ENFORCE＋日本語、Built-in ENFORCE＋Semantic Snapshot有無、Provider別BudgetをRegression化する。
- R14-WU-010：Package Recovery Indexを作成する。

### P6-RR-R15 — Request-ID Observability／Recording Correlation

- R15-WU-001：Current Turn IdentityをJudge Compositionから独立した共有Correlation Registryへ置く。
- R15-WU-002：Judge OFF＋Recording FULL／METADATAでも新TurnがCurrentとなり、過去Judge Requestへ誤Joinされないようにする。
- R15-WU-003：Turn開始時のFrozen Recording ModeをTurn RecordingとJudge Evidenceの両方で使用し、完了時Live Mode再読を除く。
- R15-WU-004：Turn、Judge Result、Judge Evidenceをbase request_idでJoinするServer-side Correlation Contractを作る。
- R15-WU-005：単一UI SummaryへRequest ID、時刻、Frozen Modes、Configured／Active／Executed、Budget、Judge Outcome、Final Disposition、Failure、Turn Recording、Judge Evidence Recordingを表示する。
- R15-WU-006：OBSERVE Background中はCurrent Turn＋Judge Pendingを表示し、完了後に同じRequest IDのResult／Evidenceへ収束する。
- R15-WU-007：別RequestのOutcomeはHistorical／Unmatchedへ分離し、Currentへ混入しない。記録履歴が1件しかない場合の限界も明示する。
- R15-WU-008：2秒Poll、設定再Open、Unmount Cleanup、Out-of-order Responseを維持する。
- R15-WU-009：Judge OFF、Recording OFF、Recording-only、Observe Async、Enforce Sync、Cross-ID、Mid-turn Mode Change、Write FailureをRegression化する。
- R15-WU-010：Package Recovery Indexを作成する。

### P6-RR-R16 — Internal Review／Contract-complete QA／Return

- R16-WU-001：R13〜R15 Focused Backend／Frontendを実行する。
- R16-WU-002：S1〜S17をTest Path／Exact Test Name／Result付きで再構築する。
- R16-WU-003：Original Acceptance 40＋Delta Acceptance 26を全66 ID個別にPASS／PARTIAL／FAIL／NOT RUN／USER GATEへ再導出する。
- R16-WU-004：Configured／Active／Executed／Recorded／Displayed Identity Matrixを具体値で作る。
- R16-WU-005：Provider別Stage Budget／Cancel／Repair Rejudge Matrixを具体値で作る。
- R16-WU-006：109 Criterion Disposition／Reason Matrix、Failure Class別JA／EN Matrix、Request-ID Correlation Matrixを作る。
- R16-WU-007：Full Path付きChanged File Inventoryと各SHA-512を作る。
- R16-WU-008：Implementation Freezeを作る。
- R16-WU-009：Requirement-by-Requirement、Cross-component、Concurrency、Failure Injection、Negative Path、Claim Auditを含むInternal Review Cycle 1を実行する。
- R16-WU-010：FindingをReworkし、Cycle 2で再Reviewする。Finding 0でもEvidenceを省略しない。
- R16-WU-011：Canonical Mypy／Ruff／Backend Full／Frontend Typecheck・Lint・Test・BuildをProject内Temp／Cacheで実行する。
- R16-WU-012：Final RecoveryとExact Return Handoffを作成する。

## 6. Acceptance Delta

最低限、次を新規または再固定する。

```text
P6-CLAUDE-R13-001: Mode OFF観測後のConcurrent ONとProvider変更でInvalid Tuple 0
P6-CLAUDE-R13-002: Provider変更中のConcurrent OFF/OBSERVE/ENFORCEを直列化
P6-CLAUDE-R13-003: Status Readerの中間Tuple観測 0
P6-CLAUDE-R13-004: Old Unload FailureをFalse Activeへ捏造 0
P6-CLAUDE-R14-001: 各Stageが自身のDeadlineを所有
P6-CLAUDE-R14-002: Built-in ENFORCEはModel Call 0かつ0ms Race 0
P6-CLAUDE-R14-003: Main Governance OFFでも日本語Failureは日本語
P6-CLAUDE-R14-004: Repair/RejudgeもFrozen Provider/Role/Budget/Language継承
P6-CLAUDE-R15-001: Judge OFF＋Recording ONでCurrent Turn相関成立
P6-CLAUDE-R15-002: Turn/Judge/Judge Evidence same request_id
P6-CLAUDE-R15-003: Mid-turn Recording Mode変更でFrozen Contract不変
P6-CLAUDE-R15-004: Single Correlation Summaryに必要Fieldを表示
P6-CLAUDE-R16-001: 66 Acceptance ID個別再導出
P6-CLAUDE-R16-002: S1〜S17 Exact Test Pointer
P6-CLAUDE-R16-003: Internal Review 2 CycleとClaim Audit
```

## 7. Automation／Recovery

1. 各Package Entry、各WU成立後、各Package FinalでAppend-only Recovery Indexを作成する。
2. ClaudeのCompaction、5時間制限、週間制限またはPlatform Stop前に、最後の成立境界、Active Process、Exact Next WUを必ず記録する。
3. Progress報告は停止理由ではない。報告後に自走する。
4. Test Failure／Finding／Authority-dependent Real Gate／長時間は単独の停止理由ではない。
5. Internal ReviewはComplete Candidate作成前に必ず実行し、FindingがあればRework→再Reviewする。
6. Context Compaction後は本書、最新Recovery、Current Sourceだけを再読し、完了Packageを再実装しない。
7. Root外／Git／Network等のTrue Stopが発生した場合は即時STOPPED_SAFEとする。Incidentを軽微だからと自己許可しない。

## 8. Tool／Mutation Boundary

Exact Start後に許可：

- R13〜R16対象Source／Test／Frontend／Generated Static／必要最小Config。
- Project内Task-owned Temp／Cache／Log。
- Phase 6 Append-only Index／Operations／Handoff。
- Claude Automation Evidence。
- Focused／Static／Regression／Build。

禁止：

- Git Read／Mutation／GitHub Action。
- Network／Web／MCP／外部Account。
- Provider Memory、User `runtime_data/`。
- Project Root外Read／Write／List／Stat／Command／Temp／Cache／Log。
- Real Model Artifact Read／Load／Inference。
- Backup、Roadmap、Stable Shared Rule、Public Docs、Constitution。
- Phase 6 Closure、Phase 7。
- Historical Evidenceの上書き／削除。

Task-owned Temp：

```text
.venv/.t/phase_6_claude_post_copilot_r13_r16_20260828214107/
```

## 9. True Stop Conditions

- Canonical Root外Actionまたは成立可能性。
- Git、Network、Provider Memory、User Data、Real Model、外部Accountへの未許可接触。
- Secret／Credential／Privacyへの予期しない接触。
- Contract Digest不一致。
- Current SourceとPreserved Baselineの差分継続不能な競合。
- 不可逆／Destructive Actionが必要。
- Critical Integrity Failure。
- User明示Stop／Scope変更／Resource Stop／Platform Hard Stop。
- Active Processを安全に収束不能。

## 10. Return Contract

最低限、次をすべて含む。

- Provider／Role／Task Identity、Active Contract Path／Digest。
- R13〜R16全WU／Package DispositionとRecovery Path。
- P6-CODEX-074〜079のDisposition。
- S1〜S17全件のTest Path／Exact Test Name／Result。
- Original 40＋Delta 26全66件のID別Disposition／Evidence Pointer。
- P6-CLAUDE-R13〜R16 Acceptance。
- Full Path付きChanged File Inventory／SHA-512。
- Identity、Stage Budget／Cancel／Rejudge、109 Criterion、Failure Language、Request-ID Correlation Matrix。
- Implementation Freeze、Internal Review Cycle 1／Rework／Cycle 2、Finding Ledger。
- Canonical VerificationのExact Command／Scope／Count／Exit。
- Root外／Git／Network／Provider Memory／runtime_data／Model／Temporary Inventory。
- Real Model／BrowserのPASS／PARTIAL／NOT RUN／USER GATE。
- Open Critical／Major／Non-critical。

最大ClaimはComplete Candidateまで。Phase 6 Closure、Git、Backup、RoadmapまたはPhase 7へ進まない。完了後はCodex Independent Review待ちで停止する。
