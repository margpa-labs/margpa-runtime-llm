# Codex Fresh Executor Phase 6 Remaining Rework — Long-run／Stop／Resume／Return／Independent Review Evidence

```yaml
document_id: codex_fresh_executor_phase_6_remaining_rework_long_run_stop_resume_return_and_independent_review_evidence_20260826204058
status: recorded_with_manual_gate_and_claude_delta_handoff_reserved
classification: automation_operational_evidence
created_at: 2026-08-26 20:40:58 JST
scope: phase_6_remaining_rework_fresh_codex_executor_cycle
provider_behavior_claim_grade: observed_cycle_only
phase_6_closure: blocked
phase_7: not_started
execution_activation: not_granted_by_this_document
git_authority: not_granted_by_this_document
supersedes: none
```

## 1. 目的

本書は、Fresh ContextのCodex `設計者兼実装者役` TaskへPhase 6 Remaining Reworkを委任してから、Long-run、True Stop、差分再開、5時間制限、Resource Signal訂正、Package J返送およびController Independent Reviewへ到達するまでを、Append-only Automation Evidenceとして記録する。

特に次を分離して残す。

1. Task再生成とAuthority／Identity Routingの成立。
2. Executor稼働中にControllerが実装／Reviewを並走しないSequential運用。
3. Package単位Recovery Indexによる差分再開。
4. Root外Action検出時の`STOPPED_SAFE`。
5. Codexの5時間制限解除後に自動再開せず、明示Continuationを要した今回の実測。
6. Userから伝えられた週間残量`9%`に従うResource Safe Stopと、直後の`69%`への訂正。
7. 自動Testが広範囲にPASSした後も、Controller Independent ReviewがProduction WiringのCritical／Major Findingを検出した事実。
8. User Mac Manual Check後に、残課題だけをFresh Claude `設計者兼実装者役`へ渡す次段階。

本書はCodex、ClaudeまたはCodex Appの恒久的なProvider特性を宣言するものではない。

## 2. Actor／Task Identity

| Provider | Role | Task／Thread ID | このCycleの責務 |
|---|---|---|---|
| Codex | プロジェクト責任者兼設計統括者役 | `019f739b-8a21-7592-95cc-c83c9c08e5f6` | Authority、差分Resume、Independent Review、Manual Gate設計 |
| Codex | 設計者兼実装者役 | `01a03b6c-2a68-7881-99bc-c788a600f632` | Phase 6 Remaining Reworkの詳細設計、実装、Test、Recovery、Return |
| Claude | 設計者兼実装者役 | Fresh Task未作成 | Manual Result後の残差Rework候補 |

Task TitleはHuman-readable Label、Frozen HandoffはScope／Authorityの正本、Task／Thread IDは配送先の正本として扱った。CodexとClaudeで同じRole名を使う場合も、ProviderとTask Identityを省略しない。

## 3. 前提となったFresh Task運用

旧Codex Executor TaskをHistorical Taskとして保持し、新Taskへ次だけを配送した。

- 実行Authorityの成立条件。
- Docs取扱Authority。
- Frozen Exact Handoff。
- Mandatory Reading Set。
- 旧Taskの会話Context、Authorityおよび未完了状態を非継承とする規則。

新Taskは実装前に次を返した。

```text
Authority通知を受領。
旧TaskのAuthority・会話Context・未完了状態は継承しない。
WAITING_FOR_EXACT_USER_STARTとして待機する。
```

このReceiptにより、Task再生成、Identity Routing、AuthorityとActivationの分離およびDirect Return経路を確認した。

使用したFrozen Contractは次である。

- `docs/project/phases/phase_6/handoffs/phase_6_claude_remaining_rework_exact_handoff_ja_20260825130924.md`
- `docs/project/phases/phase_6/history/operations/phase_6_remaining_rework_design_freeze_ja_20260825130924.md`
- `docs/project/phases/phase_6/history/operations/phase_6_remaining_rework_execution_plan_and_acceptance_ja_20260825130924.md`

File名に`claude`を含むHandoffをCodex Taskが再利用したが、Provider IdentityはTask ReceiptとDirect MessageでCodexへ固定した。File名だけからClaude Authorityを継承していない。

## 4. 採用したSequential Orchestration

前CycleではExecutorとControllerが並走し、User観測で利用可能量が約70〜80%減少した。今回は次をDefaultとした。

```text
ControllerがFrozen HandoffとExact Authorityを送信
  -> Codex Executorが単独Long-run
  -> Controllerは実装／Test／途中Reviewを行わず待機
  -> ExecutorがInterim／STOPPED_SAFE／Complete CandidateをDirect Return
  -> 必要時だけControllerがIncident ReviewまたはExact Continuationを返す
  -> Complete Candidate後にControllerがIndependent Review
```

Executor実行中もUserからの別件、予約およびResource報告はControllerが受け付けた。ただし、ControllerはComplete Candidate前のSource先行Reviewを行わず、前回の二重消費Schedulingを再現しなかった。

## 5. 実行Timeline

### 5.1 Package 0／A／B

Fresh ExecutorはP6-RR-0、A、Bを完了し、次を成立範囲として記録した。

- Entry／Authority／Baseline Reconciliation。
- Requirement Definition Reconciliation。
- ARGD 53件＋DAGD 56件、合計109件のSemantic Criterion Compiler。
- Source Identity、Digest、Unsupported 0の再導出。

Recovery Index：

- `docs/project/phases/phase_6/history/index/phase_6_remaining_rework_package_0_entry_baseline_recovery_ja_20260826093853.md`
- `docs/project/phases/phase_6/history/index/phase_6_remaining_rework_package_a_requirement_definition_reconciliation_ja_20260826094400.md`
- `docs/project/phases/phase_6/history/index/phase_6_remaining_rework_package_b_semantic_criterion_compiler_ja_20260826094401.md`

### 5.2 P6-RR-INC-001と最初のSTOPPED_SAFE

P6-RR-C-WU-001のRead Commandで、Executorが誤って`2>/tmp/not_allowed`を使用した。Project Root外Action禁止に抵触したため、Cleanupや追加Inspectionを行わず即時停止した。

```text
Incident             : P6-RR-INC-001
Root-outside Action  : 1
Automatic Cleanup    : 0
Git／Network         : 0
Provider Memory      : 0
User runtime_data    : 0
Active Process       : 0
```

Evidence：

- `docs/project/phases/phase_6/history/operations/phase_6_remaining_rework_root_outside_stderr_redirect_incident_ja_20260826094511.md`
- `docs/project/phases/phase_6/history/index/phase_6_remaining_rework_package_c_root_outside_incident_stopped_safe_recovery_ja_20260826094511.md`
- `docs/project/phases/phase_6/handoffs/phase_6_remaining_rework_stopped_safe_return_handoff_ja_20260826094511.md`

ControllerはIncidentを非隠蔽のHistorical Nonconformanceとして保持し、P6-RR-C-WU-001からだけ再開するExact Differential Resume Authorityを発行した。P6-RR-0／A／Bを再実行させなかった。

- `docs/project/phases/phase_6/handoffs/phase_6_remaining_rework_p6_rr_inc_001_exact_resume_authority_ja_20260826094752.md`

### 5.3 Package C〜Iの差分継続

Executorは次をPackage単位で実装・検証・記録した。

| Package | 主対象 | Recovery Index |
|---|---|---|
| C | Semantic Runtime／Action／Evidence | `phase_6_remaining_rework_package_c_semantic_runtime_action_evidence_recovery_ja_20260826142011.md` |
| D | Independent Provider Registry／State／CAS | `phase_6_remaining_rework_package_d_independent_provider_registry_state_recovery_ja_20260826142011.md` |
| E | Role Lifecycle／Resource Scheduling | `phase_6_remaining_rework_package_e_role_lifecycle_resource_scheduling_recovery_ja_20260826142524.md` |
| F | Selene Judge Adapter | `phase_6_remaining_rework_package_f_selene_judge_adapter_recovery_ja_20260826143045.md` |
| G | Qwen3Guard Adapter | `phase_6_remaining_rework_package_g_qwen3guard_adapter_recovery_ja_20260826143607.md` |
| H | Judge／Repair／Failure／Recording | `phase_6_remaining_rework_package_h_judge_repair_failure_recording_recovery_ja_20260826144618.md` |
| I | API／Advanced Mode UI | `phase_6_remaining_rework_package_i_api_advanced_mode_ui_recovery_ja_20260826145813.md` |

上表のRecovery Indexはすべて`docs/project/phases/phase_6/history/index/`配下にある。Package Indexがあったため、5時間制限やSTOPPED_SAFE後も成立済みPackageを最初からやり直さずに済んだ。

### 5.4 5時間制限と手動Continuation

Long-run中、Userは同一Cycleで5時間制限へ複数回到達したと報告した。制限解除後もCodex Executor TaskはClaudeで過去に観測されたような自動再開を行わず、停止状態を維持した。

UserがExecutorへ途中報告を求め、ControllerがCurrent PackageとRecovery Boundaryを確認した後、明示Continuationを送ることで差分再開した。

```text
Codex automatic resume after five-hour reset : NOT OBSERVED IN THIS CYCLE
Explicit report／continuation                 : REQUIRED
Completed Package redo                        : 0 instructed
Permanent product rule                        : NOT CLAIMED
```

これは2026-08-26時点の当該Task／Account／App Cycleの実測であり、全Accountまたは将来Versionへ一般化しない。

### 5.5 Package J Canonical Verification

ExecutorはPackage Jで次のCanonical Evidenceを得た。

```text
Backend Full : 1656 passed / 7 deselected
Mypy         : 465 source files / 0 issues
Ruff         : PASS
Frontend     : typecheck / lint / test / build 各Exit 0
Real Model   : NOT RUN / UNAVAILABLE under authority boundary
Real Browser : USER MANUAL GATE / NOT RUN
```

FrontendのExact Test数は永続Logから再導出できなかったため、最終Bounded Returnでは捏造せず未主張とした。

### 5.6 週間残量9%の誤SignalとResource STOPPED_SAFE

Userから週間利用可能量`残り9%`というSignalが届いた。既存Policyの最低保全線50%を大幅に下回るため、ExecutorはHard Stopとして解釈し、Package Jを`RESOURCE_EXHAUSTED／STOPPED_SAFE`へ固定した。

- `docs/project/phases/phase_6/history/index/phase_6_remaining_rework_package_j_weekly_resource_exhausted_stopped_safe_recovery_ja_20260826201830.md`
- `docs/project/phases/phase_6/handoffs/phase_6_remaining_rework_weekly_resource_exhausted_stopped_safe_handoff_ja_20260826201830.md`

直後にUserが正しい値は`残り69%`だったと訂正した。したがって`9%`を現在のResource判断へ再利用しない。一方、当時受領したSignalに基づく停止処理とAppend-only Evidenceは削除しない。

この事象は次を示した。

- Resource Signalが正しければ、保全Policyに従うSafe Stopは機能する。
- Human／UI由来Signalは、5時間枠と週間枠を取り違える可能性がある。
- Signal訂正時は過去Evidenceを改ざんせず、Current Stateだけを訂正する必要がある。
- Resource停止後の再開は、Exact残件と既存Evidence再利用を明示する必要がある。

### 5.7 69%訂正後のBounded Completion

User Overrideにより、Executorは新規実装、Test、Static、Frontend、Browser、Real Modelまたは追加調査を行わず、既存EvidenceだけでPackage Jを確定した。

- `docs/project/phases/phase_6/history/index/phase_6_remaining_rework_package_j_bounded_completion_recovery_ja_20260826202200.md`
- `docs/project/phases/phase_6/handoffs/phase_6_remaining_rework_bounded_complete_candidate_handoff_ja_20260826202200.md`

返送Statusは次である。

```text
COMPLETE_CANDIDATE_WITH_PARTIAL_NOT_RUN_AND_USER_GATES
Acceptance self-classification:
  PASS 27
  PARTIAL 10
  NOT RUN / UNAVAILABLE 1
  USER MANUAL GATE 1
  FAIL 1
Phase 6 Closure: NOT CLAIMED
```

ExecutorはOpen Majorとして、Dedicated Selene／Qwen3Guard Production Binding、Main-self固定のLive Judge Hook、Official Provenance不足等を自ら明記した。Return後は停止し、Controller Independent Reviewを待った。

## 6. Controller Independent Review

ControllerはComplete Candidate返送後に初めて集中Reviewを行い、成立済みDomain／Adapter TestとProduction Compositionを分離した。

Controller focused revalidation：

```text
Focused files : 6
Result        : 52 passed / Exit 0
Scope         : Semantic Runtime、Provider Controller、Role Lifecycle、
                Selene Adapter、Qwen3Guard Adapter、Feature Mode Routes
```

この52件は部品、Fake LifecycleおよびAPI Contractの成立Evidenceであり、Production Web Turnへ実Providerが接続されたEvidenceではなかった。

Controller判定：

```text
Phase 6 Remaining Rework Package completion : PARTIAL ACCEPT
Phase 6 Technical Acceptance                : FAIL / ADJUST
Phase 6 Closure                             : BLOCKED
Open Critical                               : 1
Open Major                                  : 6
Real Browser Gate                           : OPEN
Real Model Gate                             : OPEN
```

### 6.1 Independent Finding

| ID | Severity | 概要 |
|---|---|---|
| P6-CODEX-046 | Major | Dedicated Provider Production FactoryがUnavailable固定 |
| P6-CODEX-047 | Critical | 選択Judgeと実行Main-self Judgeが不一致でEvidence Identityが虚偽 |
| P6-CODEX-048 | Major | Qwen3GuardがGuardrail Production経路へ未接続 |
| P6-CODEX-049 | Major | Main Provider Dropdownが実Runtime Switchへ未接続 |
| P6-CODEX-050 | Major | Model Statusが新Provider Stateを投影しない |
| P6-CODEX-051 | Major | Stage Budget／Repair RejudgeがSelected Providerへ未接続 |
| P6-CODEX-052 | Major | Selene／Qwen3Guard Official Contract Provenance未成立 |
| P6-CODEX-053 | Non-critical／一部Acceptance Blocker | Guard Mode Freeze、Recording相関、CLI説明、Real Model／Browser残件 |

Review正本：

- `docs/project/phases/phase_6/history/operations/phase_6_gov016_remaining_rework_controller_independent_review_ja_20260826202919.md`

この結果は、広範囲なBackend／Frontend／Static PASSだけではProduction Wiring、実Provider IdentityまたはResearch Evidenceの正しさを保証しないことを再確認した。Sequential運用はController ResourceをReview境界まで温存し、False CompletionのClosure昇格を防いだ。

## 7. User Manual Gate

Controllerは、Source Reviewで未接続と判明した機能をUI表示だけでPASSへ昇格させない前提で、User Mac限定のM-1〜M-7を作成した。

1. 初期Provider State。
2. Main Dropdownと実Main／Sidebar／Model Statusの不一致。
3. Selene ActivationのUnavailable。
4. Qwen3Guard ActivationのUnavailable。
5. Built-in JudgeのFalse IdentityとSemantic 109件の実行状態。
6. Judge OFF後のCurrent／Historical State分離。
7. RecordingのRequest ID、時刻、Frozen Mode、Provider、Outcome／Reason相関。

Manual Check正本：

- `docs/project/phases/phase_6/handoffs/phase_6_user_mac_bounded_manual_check_after_remaining_rework_ja_20260826202919.md`

Userは翌日に実画面確認し、M-1〜M-7の結果をControllerへ返す予定である。その結果を受領する前に、ControllerはClaude用最終差分Handoffを確定しない。

## 8. Resource／Platform観測

### 8.1 今回観測したこと

- Fresh Executor Taskと限定Mandatory Readingでも、Codex利用可能量はUserの予想より速く減少した。
- 同一Long-runで5時間制限へ複数回到達したとUserが報告した。
- Userが途中で週間残量`74%`、後に`69%`を報告した。
- Fresh Task化は旧Contextの混入防止には有効だったが、Project自体の重量を除去しない。
- Executor実行中にControllerを完全並走させないことで、ControllerをIndependent Reviewまで利用可能に保てた。

### 8.2 現時点で断定しないこと

- Context蓄積だけが消費増の原因であること。
- CodexがClaudeより恒久的に燃費が悪いこと。
- CodexのQuota計算方式が特定日時に変更されたこと。
- Claudeの50%増加Campaign条件を除いた厳密なProvider比較。
- 5時間制限解除後の自動再開不成立がCodex全体の恒久仕様であること。

現時点では、Project規模、Regression範囲、Source／Test／Docs横断、Concurrency／Evidence要件、Provider固有消費、Product／Quota条件およびContext量の複合要因と扱う。

## 9. Automation評価

| 観点 | 評価 | 根拠 |
|---|---|---|
| Fresh Task Identity／Authority分離 | PASS | 旧Context非継承、WAITING Receipt、誤配送0 |
| Direct Task Communication | PASS | Interim、STOPPED_SAFE、Complete Candidate返送成立 |
| Sequential Controller Waiting | PASS | Executor中の並行Source Review／Testなし |
| Package Recovery／Differential Resume | PASS | A／B再実行なしでCから再開 |
| Root Boundary Stop | PASS WITH INCIDENT | 違反1件を検出し非隠蔽で停止 |
| 5時間制限からの自動再開 | NOT OBSERVED | 明示Report／Continuationが必要 |
| Resource Signal Stop | PASS WITH SIGNAL CORRECTION | 9%で停止、69%訂正後にBounded Resume |
| Executor Self-acceptance | PARTIAL | Open Majorは記録したがProduction Wiringを十分再分類できず |
| Controller Independent Review | REQUIRED／EFFECTIVE | Critical 1、Major 6を検出 |
| Phase 6 Closure | BLOCKED | Manual GateとClaude差分Reworkが残る |

## 10. 運用上のCorrection

今後の同種Long-runでは次をDefaultとする。

1. Provider、Role、Task Identity、Contract Path／DigestをHandoffごとに固定する。
2. Fresh Taskへ旧Authority、旧会話Contextおよび未完了状態を継承させない。
3. Executor稼働中、ControllerはUser対応を除いて実装／Reviewを並走しない。
4. Package／Work UnitごとにRecovery Indexを作り、制限後の全再実行を避ける。
5. 5時間制限解除後は自動再開を前提にせず、Current RecoveryとActive Processを確認してExact Continuationを送る。
6. Resource Signalは`週間`と`5時間`を明示し、停止後に訂正された場合はAppend-onlyでCurrent判定だけを更新する。
7. `Test PASS`、`Adapter存在`、`API存在`および`Dropdown表示`をProduction Binding成立と同一視しない。
8. Executor Complete Candidate後のController Independent Reviewを省略しない。
9. User Manual ResultをSource Reviewより強いEvidenceとして誤用せず、両方を結合してRework Scopeを確定する。
10. Claude復帰時はFresh Taskへ現在の残差だけを渡し、Codexが成立させたPackage 0〜Iを最初から重複実装させない。

## 11. 次の予約

```text
User Mac Manual Check M-1〜M-7
  -> User Result Return
  -> ControllerがManual EvidenceをAppend-only記録
  -> P6-CODEX-046〜053＋Manual Resultだけを対象にClaude用Exact Delta Handoff作成
  -> Fresh Claude TaskへAuthority／Docs取扱Authorityを先に配送
  -> Claude運用メモ2件を読了
  -> User Start成立後にClaude Long-run
  -> Controller Independent Re-review
  -> Phase 6 Closure可否判定
```

Claude Fresh Taskの事前運用正本：

- `docs/project/shared/history/automation/claude_task_recreation_and_cross_provider_role_identity_operating_correction_ja_20260826094454.md`
- `docs/project/shared/history/planned_work/claude_fresh_designer_implementer_task_activation_sequence_reservation_ja_20260826094454.md`
- `docs/project/shared/task_roles/claude_side_design_governor_operating_notes_ja.md`
- `docs/project/shared/task_roles/claude_side_long_running_automation_companion_ja.md`

## 12. 関連Automation Evidence

- `docs/project/shared/history/automation/codex_two_task_long_run_review_rework_orchestration_reservation_ja_20260823095316.md`
- `docs/project/shared/history/automation/codex_two_task_phase_6_parallel_controller_resource_observation_ja_20260825014841.md`
- `docs/project/shared/history/automation/codex_task_recreation_identity_routing_authority_delivery_and_resource_preservation_evidence_ja_20260826092621.md`
- `docs/project/shared/history/automation/codex_five_hour_manual_resume_resource_consumption_project_weight_and_future_provider_comparison_evidence_ja_20260826145850.md`
- `docs/project/shared/history/automation/claude_task_recreation_and_cross_provider_role_identity_operating_correction_ja_20260826094454.md`

## 13. 現在地

```text
Fresh Codex Executor Long-run             : COMPLETE TO BOUNDED RETURN
Packages 0-I                              : IMPLEMENTED／RECORDED
Package J                                 : BOUNDED COMPLETE CANDIDATE
Five-hour Automatic Resume                : NOT OBSERVED IN THIS CYCLE
Weekly Resource Signal                    : 69% USER CORRECTION IS CURRENT
Superseded Resource Signal                : 9%
Controller Independent Review             : COMPLETE
Controller Verdict                        : ADJUST_REWORK_REQUIRED
Open Critical                             : 1
Open Major                                : 6
User Mac Manual Gate                      : READY／NOT YET EXECUTED
Claude Delta Handoff                      : RESERVED AFTER MANUAL RESULT
Phase 6 Closure                           : BLOCKED
Phase 7                                   : NOT STARTED
Git                                       : NO ACTION BY THIS EVIDENCE
```

## 14. Evidence限界

- Codex内部のQuota Accounting、Token Cache、Task Context圧縮および5時間制限の実装は観測できない。
- User-visible PercentageはToken量、CostまたはTask別消費を直接表すとは限らない。
- Real Qwen、DeepSeek、Selene、Qwen3GuardおよびReal Browser AcceptanceはこのAutomation Cycleでは未完了である。
- Controller FindingはSource／Focused Test Evidenceに基づくが、翌日のUser Manual ResultとClaude差分Rework後に再評価される。
- 本書はPhase 6 Closure、Phase 7開始、Git操作、Network取得、Model Artifact変更またはClaude実行を許可しない。
