# Phase 6 GitHub Copilot Post-Claude R3〜R8 Exact Differential Continuation Handoff

```yaml
document_id: phase_6_copilot_post_claude_r3_to_r8_exact_continuation_handoff_20260828193037
document_type: frozen_exact_cross_provider_continuation_handoff
document_state: ready_for_bootstrap
language: ja
created_at: 2026-08-28 19:30:37 JST
authority_owner: プロジェクト責任者兼設計統括者役
target_provider: GitHub Copilot app
target_role: 設計者兼実装者役
task_state: fresh_task
implementation_authority: false_until_backup_and_exact_user_start
preserved_packages: Phase_6_0_to_I_Claude_K_to_Q_and_Rework_R0_to_R2
partial_package: P6-RR-R3
first_exact_work_unit: P6-RR-R3-WU-001_REDERIVATION_WITH_CURRENT_PARTIAL_PRESERVED
remaining_packages: P6-RR-R3_to_R8
maximum_claim: complete_candidate
phase_6_closure: prohibited
phase_7: prohibited
git: prohibited_including_read_only
network: prohibited
```

## 1. Authority Statement

本書は、ClaudeがP6-RR-R3途中で停止した状態をGitHub Copilot appのFresh Taskへ差分移管し、R3のCurrent Partialを保全したままR3〜R8を完了させるFrozen Exact Handoffである。

本書を読むだけでは実装Authorityは発生しない。対象TaskはMandatory ReadingとDigest Receiptを返し、`WAITING_FOR_EXACT_USER_START`で停止する。

UserがBackup完了後に次のExact Startを送った場合だけ実装を開始する。

```text
Phase 6 Copilot Differential Continuationを開始する。
```

Exact Startの送信は、Userが本Handoff発行後のBackup Gateを完了したことを意味する。CopilotがBackupを取得、検査または変更してはならない。

## 2. Provider／Role／Task Boundary

```text
Provider: GitHub Copilot app
Role: 設計者兼実装者役
Task Identity: Fresh Copilot Phase 6 Differential Continuation Task
Controller: Codex プロジェクト責任者兼設計統括者役
Old Claude／Codex／Copilot Context Inheritance: NONE
Old Authority Inheritance: NONE
```

ClaudeのConversation、Compaction後Context、Tool State、未完了Memoryまたは暗黙Authorityを継承しない。Repository Canonical Docsと本Handoffだけから再構成する。

## 3. Canonical Root

```text
<PROJECT_ROOT>
```

このRootだけがAuthorized Rootである。親Directory、Sibling Repository、Home、`/tmp`、OS既定Temporary、Copilot Cache、GitHub外部状態または外部Model Directoryは含まれない。

## 4. Mandatory Reading

次を指定順で全文読む。抜粋、Summaryまたは会話記憶で代替しない。

### 4.1 Copilot Stable Role Rule

1. `docs/project/shared/task_roles/copilot_side_designer_implementer_operating_notes_ja.md`
2. `docs/project/shared/task_roles/copilot_side_long_running_automation_companion_ja.md`
3. `docs/project/shared/task_roles/copilot_side_implementation_internal_review_rework_loop_operating_contract_ja.md`
4. `docs/project/shared/task_roles/role_authority_matrix_ja.md`
5. `docs/project/shared/task_roles/task_role_write_authority_policy_ja.md`
6. `docs/project/shared/automation/provider_memory_and_repository_canonical_authority_ja.md`
7. `docs/project/shared/operations/research_asset_mutation_control_ja.md`
8. `docs/project/shared/operations/transition_blocker_escalation_and_closure_contract_ja.md`

### 4.2 Phase 6 Base／Manual／Review

9. `docs/project/phases/phase_6/handoffs/phase_6_claude_post_manual_production_wiring_delta_exact_handoff_ja_20260827211749.md`
10. `docs/project/phases/phase_6/handoffs/phase_6_claude_post_manual_production_wiring_delta_exact_handoff_addendum_ja_20260827215158.md`
11. `docs/project/phases/phase_6/history/operations/phase_6_post_manual_production_wiring_delta_design_and_execution_freeze_ja_20260827211749.md`
12. `docs/project/phases/phase_6/history/operations/phase_6_gov017_user_mac_provider_semantic_recording_manual_acceptance_evidence_ja_20260827211749.md`
13. `docs/project/phases/phase_6/history/operations/phase_6_gov018_user_mac_provider_false_activation_and_execution_identity_addendum_ja_20260827215158.md`
14. `docs/project/phases/phase_6/handoffs/phase_6_claude_post_manual_production_wiring_delta_complete_candidate_handoff_ja_20260828185500.md`
15. `docs/project/phases/phase_6/history/operations/phase_6_gov019_claude_post_manual_production_wiring_delta_controller_independent_review_ja_20260828180240.md`
16. `docs/project/phases/phase_6/handoffs/phase_6_post_claude_independent_review_exact_rework_handoff_ja_20260828180240.md`
17. `docs/project/phases/phase_6/handoffs/phase_6_post_claude_independent_review_git_read_incident_exact_resume_authority_ja_20260828183758.md`

### 4.3 R0〜R3 Recovery

18. `docs/project/phases/phase_6/history/index/phase_6_post_claude_independent_review_rework_package_r0_recovery_ja_20260828184118.md`
19. `docs/project/phases/phase_6/history/index/phase_6_post_claude_independent_review_rework_package_r1_recovery_ja_20260828184813.md`
20. `docs/project/phases/phase_6/history/index/phase_6_post_claude_independent_review_rework_package_r2_recovery_ja_20260828190438.md`
21. `docs/project/phases/phase_6/history/index/phase_6_copilot_takeover_after_claude_r3_partial_controller_reconstruction_ja_20260828193037.md`
22. 本書。

### 4.4 Current R3 Partial Source／Test

23. `src/margpa_runtime_llm/bootstrap/judge_live_integration.py`
24. `src/margpa_runtime_llm/web/runtime_governance_routes.py`
25. `src/margpa_runtime_llm/web/feature_modes_routes.py`
26. `frontend/src/types.ts`
27. `frontend/src/components/FeatureModesPanel.tsx`
28. `tests/unit/bootstrap/test_judge_live_integration.py`
29. `tests/unit/web/test_runtime_governance_routes.py`

R4〜R8着手時は、元Exact Rework Handoff §3のSource再導出対象13〜26もCurrent Sourceから読む。

## 5. Digest Authority

```text
Copilot Operating Notes:
1137b5ca000b1d73325de6c4802eef4557d3cb38c6fb57debf7795c961b68ed8e550942b0afa3ae8f401609e1448c78c99380def9702340ef9b5b79df678d3e6

Copilot Long-running Companion:
1be99fd71c1b5861ab8e07b9d53a83de0dba0edb7c6fa2c722cb16f5ab6c891439fea746621a01674f177b53f6320aa4a6320b9aacc5de79b15d345f5d1c7fc0

Copilot Internal Review Contract:
b5836985692420c81824e17bbb41b5cc2bed269bdc8fa5660ee7e9f61a94efc75d354eedf12a98565826cd643e6db651e6a65af192529e4b7f7ad86e5c32b39c

Original Exact Rework Handoff:
8de37770693bf84c7e6a51fb46189341a2f3035a3ccf30c19bf6dcb1284f1991a0322573c783d65153820dbdea62e6e99063f697fbded637ef65132b35d5736a

Git Incident Resume Authority:
08d516baf62eeeb3b4020405321c8881e1437eec8b56ae47e16d50d6cd5b59381dff9c5b1f04d0605261b04a67eb63aa4ecfd1decd135f5649637b6af8753996

P6-GOV-019:
f77d0c6a376db6677935560f720304fe94cd809025457cfb1e9c00ec8cb51059e88df523348c48b39ab8ce229db5fd02f06b4b70cbdf90e1aca4329bfea5a240

R0 Recovery:
182be76e429827ae7bbc587ff43536bb1102730e5a4f5f5112f83d0c5a639f5247ab4d8bffa6eabc36a5a80422755f5ff188e92dda1cc88841c435dcf175af17

R1 Recovery:
8ada5c355eef54c3c4b67e6ca2bb5af1916d9f3e1f5c8ae6ee7c9aeae8a8595640c0f88f5d597c33f9b8b289eb62c99e3805946bd6ae8c24727f5e69f1b5b894

R2 Recovery:
c51dd28b59208538f6c2853f7b717ba9b0e5354fcb84448f5d0878016f128c2ddafdfa6983a44ec42db746cd1be3b143a6f91a9fa303bb3154cae2358e78fad8

Controller R3 Reconstruction:
f7f5702820b967430ea5c501057952d2944de106a8a8ef650c459c11b6b18ef8dc0ba9c87d50573b68326f9ad06af7cb14c0ae3bb4d091c4084d6564cc82404b
```

Digest不一致では実装を開始しない。Mismatch PathとObserved Digestだけを返す。

## 6. Preserved／Superseded／Open State

### 6.1 Preserved

- Phase 6 Package 0〜I。
- Claude Package K〜QのうちP6-GOV-019で棄却していない成果。
- Rework R0〜R2と各Recovery。
- P6-CODEX-062／063の修正候補SourceとRegression Evidence。
- Historical Incident、FAIL、PARTIAL、NOT RUNおよびUser Gate。
- Current R3 Partial七File。

### 6.2 Superseded／Rejected

- Claude Complete Candidateの`Open Major 0`／Closure相当Claim。
- P6-GOV-019が棄却したAcceptance Claim。
- Git Read Incidentを0とするClaim。
- R3途中差分をPackage CompleteとするClaim。

### 6.3 Current Open

```text
P6-CODEX-064: R3 Semantic 109 Live Evaluation／Projection
P6-CODEX-065: R4 Provider Budget／Frozen Repair Rejudge
P6-CODEX-066: R5 Failure Presentation
P6-CODEX-067: R6 Live Observability／Recording Correlation
P6-CODEX-068: R8 Acceptance／Internal Review Claim Correction
```

## 7. Exact Objective

元Exact Rework Handoff §4、§5、§6および§7を維持する。特に次を完成させる。

1. R3 Current Partialの成立／不成立をWU単位で再導出する。
2. 109 Criterionを同一Turn Snapshotで評価し、全件へ排他的DispositionとReasonをexactly onceで与える。
3. `evaluated／passed／deviated／unknown／not_applicable／deferred`を意味どおり数える。
4. Main Runtime Governanceの同一Request IDへSemantic結果を投影し、Late Resultを拒否する。
5. Provider別Stage Budgetを実行へ適用する。
6. Repair RejudgeへFrozen Judge Adapter／Identity／Budgetを引き継ぐ。
7. Safe FallbackをFrozen LanguageとFailure Class別にし、User責任を示唆しない。
8. Live Observability／Recording CorrelationをRequest ID単位で更新する。
9. Authority-independent Fixture／Negative Pathを完成させる。
10. Original 40＋Delta 26 Acceptanceを再導出し、内部Review／Reworkを最大二周行う。

## 8. Exact Work Sequence

### 8.1 R3 Recovery／Completion

最初に次を実行する。

```text
P6-RR-R3-WU-001_REDERIVATION_WITH_CURRENT_PARTIAL_PRESERVED
```

- 本HandoffとController R3 ReconstructionをEntry Recoveryとして扱う。
- 七FileのCurrent PartialをRollbackしない。
- R3-WU-001〜008をSource／Test／Focused Verificationから再導出する。
- 成立済み部分を無駄に書き直さず、不成立部分だけを修正する。
- 各WU直後にCheckpointを作る。
- R3全体のFocused／Static成立後にFinal Recovery Indexを作る。

### 8.2 R4〜R8

R3完了後、元Exact Rework Handoff §5のR4〜R8を順に連結実行する。Work Unit、Regression Scenario S1〜S17、Acceptance Maximum、Return Contractを変更しない。

## 9. Evidence／Recovery Cadence

初回Copilot Pilotとして、通常より高い頻度でEvidenceを残す。

1. Exact Start後、最初のCommand／Mutation前に`docs/project/shared/history/automation/`へPilot Entry Evidenceを作る。
2. 各Work Unit直後にPhase 6 `history/index/`へAppend-only Checkpointを作る。
3. 各Package Entry／FinalでRecovery Indexを作る。
4. Full Test、Frontend Build、長時間Command、CompactionまたはResource Stop前にRecoveryを確定する。
5. Compaction／Session／利用制限復帰後はCopilot Stable 3文書、本Handoff、最新2 Index、Current Packageを全文再読する。
6. Incident／Near Miss／Unexpected Tool Behaviorは`shared/history/automation/`またはPhase 6 `history/operations/`へ即時Evidence化する。
7. Implementation Freeze、Internal Review各Cycle、Rework、Final Returnを別Boundaryとして記録する。

Progress報告後もTrue StopまたはReturnまで自走する。

## 10. Mutation／Tool Boundary

Exact Start後に許可するもの：

- Phase 6 R3〜R8対象のSource／Test／Frontend／Config差分。
- Project内Task-owned Temporary／Cache／Log。
- Phase 6 Append-only Evidence／Index／Handoff。
- Copilot Pilot用`docs/project/shared/history/automation/` Append-only Evidence。
- Active Scopeに必要なFocused／Static／Regression／Build Command。

禁止：

- Git Read／Mutation／GitHub操作。
- Network／Web／Package取得／MCP／外部Account。
- Provider Memory。
- User `runtime_data/`。
- Project Root外のRead／Write／List／Stat／Command／Temp／Cache／Log。
- Real Model Artifact／Model Load／Inference。
- Backup操作。
- Existing Historyの上書き／削除。
- Stable Shared Rule、Roadmap、Public Docs、ConstitutionのMutation。
- Phase 6 Closure、Phase 7、Current Promotion。

Task-owned Temporaryは次へ固定する。

```text
.venv/.t/phase_6_copilot_continuation_20260828193037/
```

pytest basetemp、Mypy／Ruff Cache、NPM Cache、TMPDIRおよびLogをこのDirectory配下へ明示する。OS既定TemporaryやUser CacheへFallbackしない。

## 11. True Stop Conditions

次だけで停止する。

- Authorized Root外Actionまたは成立可能性。
- Git、Network、Provider Memory、User Data、Real Modelまたは外部Accountへの未許可接触。
- Secret／Credential／Privacyへの予期しない接触。
- Contract Digest不一致。
- Current SourceがController Reconstructionと競合し、差分継続できない。
- 不可逆／Destructive Actionが必要。
- Critical Integrity Failure。
- Userが停止／Scope変更／Resource Stopを明示。
- Active Processを安全に収束できない。

Real Model Authority不足、Open Finding、Test Failure、Implementation Difficulty、Internal Review Findingまたは長時間だけでは全体停止しない。該当項目を分類し、Authority内の修正を継続する。

## 12. Internal Review／Return

R3〜R8実装後にImplementation Freezeを作り、Copilot Internal Review Contractに従って最大二周のReview／Rework／Re-reviewを行う。

Return Handoffには、元Exact Rework Handoff §10に加え次を含める。

- Copilot Pilot Evidence一覧。
- Compaction／Session／Resource挙動。
- R3 Partialの再導出結果。
- R0〜R2再実装0の確認。
- Work Unit／Package Recovery一覧。
- Autopilot／Harnessに関する実測Evidence。
- Self-reviewとCodex Independent Reviewの分離。

最大Claimは次のいずれかまでである。

```text
COMPLETE_CANDIDATE
COMPLETE_CANDIDATE_WITH_REAL_PROVIDER_AUTHORITY_GATE
INCOMPLETE_WITH_OPEN_FINDINGS
STOPPED_SAFE
```

Return Artifact作成後、Userへ日本語でPathと要約を返し、Codex Controller Independent Review待ちで停止する。
