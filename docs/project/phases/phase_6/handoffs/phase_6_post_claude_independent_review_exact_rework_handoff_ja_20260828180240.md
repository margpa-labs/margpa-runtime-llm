# Phase 6 Post-Claude Independent Review — Exact Differential Rework Handoff

```yaml
document_id: phase_6_post_claude_independent_review_exact_rework_handoff_20260828180240
status: READY_FOR_EXACT_USER_START
classification: frozen_exact_differential_rework_handoff
created_at: 2026-08-28 18:02:40 JST
authority_owner: プロジェクト責任者兼設計統括者役
target_provider: Claude_or_Codex
target_role: 設計者兼実装者役
implementation_authority: FALSE_UNTIL_EXACT_USER_START
base_candidate: phase_6_claude_post_manual_production_wiring_delta_complete_candidate_handoff_ja_20260828185500.md
controller_review: phase_6_gov019_claude_post_manual_production_wiring_delta_controller_independent_review_ja_20260828180240.md
controller_review_sha512: f77d0c6a376db6677935560f720304fe94cd809025457cfb1e9c00ec8cb51059e88df523348c48b39ab8ce229db5fd02f06b4b70cbdf90e1aca4329bfea5a240
phase_6_closure: PROHIBITED
phase_7: PROHIBITED
git: PROHIBITED
```

## 1. Authority Statement

本書は、P6-GOV-019 Controller Independent Reviewで検出したOpen Major Findingだけを差分修正するFrozen Exact Handoffである。

本書を読むだけでは実装Authorityは発生しない。対象TaskはMandatory ReadingとDigest確認後、`WAITING_FOR_EXACT_USER_START`で停止する。Userが次のExact Startを明示した場合に限り実装を開始する。

```text
Phase 6 Post-Claude Independent Review Reworkを開始する。
```

## 2. Preserved Baseline

次は成立済みBaselineとして保存し、理由なく再実装しない。

- Phase 6 Package 0〜I。
- Claude Package K〜Qのうち、P6-GOV-019で棄却していない成果。
- Main Provider DropdownのRuntime Model Switch Transaction。
- Production Role Adapter FactoryとAuthority Gateの骨格。
- Built-in Deterministic Model Call 0経路。
- Qwen3Guard Additive Detectorの骨格。
- Bounded UI Deltaのうち、User Manualで希望どおりと確認された配置・非表示化。
- Claude Canonical Backend／Frontend／Static Regression Evidence。
- Historical Incident、PARTIAL、NOT RUN、FAILおよびUser Gate。

新Taskは旧Taskの会話Context、Memory、未完了Stateまたは暗黙Authorityを継承しない。正本は本書、Mandatory Readingおよび明示Startだけである。

## 3. Mandatory Reading

Canonical Root：現在この文書を保持する`margpa-runtime-llm` Repository Root。以下はすべてRepository Root相対Pathとして解決する。

次を指定順で全文読む。

1. `docs/project/shared/task_roles/claude_side_design_governor_operating_notes_ja.md`
2. `docs/project/shared/task_roles/claude_side_long_running_automation_companion_ja.md`
3. `docs/project/shared/task_roles/claude_side_implementation_internal_review_rework_loop_operating_contract_ja.md`
4. `docs/project/phases/phase_6/handoffs/phase_6_claude_post_manual_production_wiring_delta_exact_handoff_ja_20260827211749.md`
5. `docs/project/phases/phase_6/handoffs/phase_6_claude_post_manual_production_wiring_delta_exact_handoff_addendum_ja_20260827215158.md`
6. `docs/project/phases/phase_6/history/operations/phase_6_post_manual_production_wiring_delta_design_and_execution_freeze_ja_20260827211749.md`
7. `docs/project/phases/phase_6/history/operations/phase_6_gov017_user_mac_provider_semantic_recording_manual_acceptance_evidence_ja_20260827211749.md`
8. `docs/project/phases/phase_6/history/operations/phase_6_gov018_user_mac_provider_false_activation_and_execution_identity_addendum_ja_20260827215158.md`
9. `docs/project/phases/phase_6/history/index/phase_6_post_manual_delta_package_q_recovery_ja_20260828184500.md`
10. `docs/project/phases/phase_6/handoffs/phase_6_claude_post_manual_production_wiring_delta_complete_candidate_handoff_ja_20260828185500.md`
11. `docs/project/phases/phase_6/history/operations/phase_6_gov019_claude_post_manual_production_wiring_delta_controller_independent_review_ja_20260828180240.md`
12. 本書。

最低限のSource再導出対象：

13. `src/margpa_runtime_llm/web/provider_selection_routes.py`
14. `src/margpa_runtime_llm/web/feature_modes_routes.py`
15. `src/margpa_runtime_llm/modules/runtime_model_control/application/provider_selection_controller.py`
16. `src/margpa_runtime_llm/modules/runtime_model_control/application/role_lifecycle_manager.py`
17. `src/margpa_runtime_llm/bootstrap/web_application.py`
18. `src/margpa_runtime_llm/bootstrap/judge_live_integration.py`
19. `src/margpa_runtime_llm/bootstrap/guardrail_governance.py`
20. `src/margpa_runtime_llm/bootstrap/runtime_governance.py`
21. `src/margpa_runtime_llm/modules/runtime_governance/application/semantic_runtime.py`
22. `src/margpa_runtime_llm/adapters/runtime_governance/semantic_criterion_adapter.py`
23. `src/margpa_runtime_llm/modules/conversation/application/conversation_generation.py`
24. `src/margpa_runtime_llm/modules/evaluation/application/failure_presentation.py`
25. `frontend/src/components/FeatureModesPanel.tsx`
26. `frontend/src/components/ProviderSelectionPanel.tsx`

Digest正本：

```text
Base Handoff:
0ff64eb24991a2fafa1b96a32af3555f949c3546339f27e5d79b66d6ff0e0149913379c9c6c2ca56827a1d79b9b140fe692874cad9c14c0ba94089aa6968eb91

Addendum:
5bb0c5a33ecc3dbd8d3685c4b1aba5d4a3d292ec65b31497715d345df9ee174c30ec5f8af7597642a8168a17f728a831f43d8fe671fe3e7fe989f359c3f3b764

P6-GOV-019:
f77d0c6a376db6677935560f720304fe94cd809025457cfb1e9c00ec8cb51059e88df523348c48b39ab8ce229db5fd02f06b4b70cbdf90e1aca4329bfea5a240
```

## 4. Exact Objective

次をProduction Pathで成立させる。

1. Judge／Guard Provider変更をMode、LifecycleおよびProvider StateとAtomicにする。
2. `Mode ON / Active none`をCommitしない。失敗時は旧Active／旧ModeへRollbackする。
3. Built-in、Main-shared Qwen／DeepSeek、Dedicated Seleneを実際のSelected Judge AdapterへDispatchする。
4. Configured、Active、Executed、Recorded、Displayed Identityを独立させ、推測しない。
5. Qwen3Guardを選択した場合、Authority成立時はDedicated Guardを実行し、未成立時はModeをONにせずExact Reasonを返す。
6. 109 Semantic CriterionをReal Turn Snapshotから評価し、全件へDispositionまたはDeferred／N/A Reasonを付ける。
7. Main Runtime Governance表示へ同一TurnのSemantic結果を投影する。
8. Provider別Stage Budgetを実行へ適用し、固定30秒相当を全Providerへ流用しない。
9. Repair RejudgeはTurn開始時にFrozenしたJudge Provider／Adapter／Budgetを使う。
10. Safe Fallbackは回答言語とFailure Classに応じ、ユーザーの責任を示唆しない。
11. Judge／Repair／Recording StatusをBounded Live Refreshし、Request ID単位に相関表示する。
12. P6-GOV-018 Scenario A〜CおよびP6-GOV-019 ReproductionをRegression Testへ昇格する。

## 5. Rework Package

### P6-RR-R0 — Entry／Claim Correction

- R0-WU-001：P6-GOV-019と本書のDigest照合。
- R0-WU-002：Claude Candidateの成立済み成果と棄却Claimを分離。
- R0-WU-003：P6-CODEX-062〜068をOpen Finding Ledgerへ登録。
- R0-WU-004：Task-owned Temp、Test Base Temp、Frontend Cache／TMPをProject内へ固定。
- R0-WU-005：Package R0 Recovery Index作成。

### P6-RR-R1 — Atomic Provider／Mode／Lifecycle Transaction

- R1-WU-001：Judge／Guard Provider変更のPreflightをMode Commit前に実施。
- R1-WU-002：Built-in→Dedicated、Dedicated→Built-in、Dedicated→none、Main-shared間のTransition State Machineを定義。
- R1-WU-003：Activation成功時だけConfigured／Active／Modeを単一RevisionへCommit。
- R1-WU-004：失敗時は旧Configured／Active／Mode／Lifecycleへ完全Rollbackし、Exact Failure Code／Reason／Timestampを保持。
- R1-WU-005：旧AdapterをDrain／Unloadし、stale active adapterを残さない。
- R1-WU-006：JudgeとGuard両Roleへ同じAtomicity Contractを適用。
- R1-WU-007：Package R1 Recovery Index作成。

### P6-RR-R2 — Production Execution Router／Identity

- R2-WU-001：Judge HookへFrozen Active Adapter Lease Resolverを接続。
- R2-WU-002：Built-in Deterministic、Main-shared Qwen、Main-shared DeepSeek、Dedicated Seleneを明示Dispatch。
- R2-WU-003：暗黙Main-selfはExplicit Main Provider選択と区別し、Fallbackとして使用しない。
- R2-WU-004：Executed Providerは実Lease／Adapterからだけ取得し、ConfiguredまたはActiveから推測しない。
- R2-WU-005：Recorded EvidenceとFrontendへConfigured／Active／Executedを別Fieldで渡す。
- R2-WU-006：Active none時はModel Call 0、Mode ON Commit 0、Executed Provider 0を保証。
- R2-WU-007：Qwen3GuardもFrozen Active Guard Adapterを実Detector経路へ接続。
- R2-WU-008：Package R2 Recovery Index作成。

### P6-RR-R3 — Semantic 109 Live Evaluation／Projection

- R3-WU-001：ARGD 53＋DAGD 56のLive Turn選択数を再導出。
- R3-WU-002：選択CriterionをFrozen Judge Requestへ渡す。
- R3-WU-003：各Criterionへ`PASS / DEVIATION / UNKNOWN / NOT_APPLICABLE / DEFERRED`とReasonをexactly onceで記録。
- R3-WU-004：Budget Exhausted、Unsupported Mapping、Provider Failureを別Reasonにする。
- R3-WU-005：`evaluated / unknown / not_applicable / deferred` Countを意味どおり分離。
- R3-WU-006：Main Runtime Governanceのpre／post表示へ同一Request IDのSemantic結果を投影。
- R3-WU-007：late resultがCurrent Turnを上書きしない。
- R3-WU-008：Package R3 Recovery Index作成。

### P6-RR-R4 — Provider Budget／Repair Rejudge

- R4-WU-001：Frozen Provider SelectionからStage Budget Profileを解決。
- R4-WU-002：Main-shared、Selene、Built-inへ別Budget Contractを適用。
- R4-WU-003：Built-inはModel Call／LLM Deadline 0のまま維持。
- R4-WU-004：Repair後のRejudgeへFrozen Judge Adapter／Identity／Budgetを引き継ぐ。
- R4-WU-005：Provider変更またはTimeout後のlate publishを拒否。
- R4-WU-006：Package R4 Recovery Index作成。

### P6-RR-R5 — Failure Presentation

- R5-WU-001：回答言語をTurn開始時にFreeze。
- R5-WU-002：`malformed_output / deadline_exceeded / provider_unavailable / activation_failed / cancelled / repair_failed`を別MessageへMapping。
- R5-WU-003：Final Safe Fallback本文もFrozen Languageへ従わせる。
- R5-WU-004：Runtime Timeoutを「再試行や根拠確認をしないユーザーの問題」のように表現しない。
- R5-WU-005：Evidence用ReasonとPresented Finalを同じFailure Classへ相関。
- R5-WU-006：Package R5 Recovery Index作成。

### P6-RR-R6 — Live Observability／Recording Correlation

- R6-WU-001：Settings表示中だけBounded Poll、SSEまたは同等の更新機構を実装。Unmount／Modal Closeで停止。
- R6-WU-002：Current Run、Historical Last Result、OFF状態を分離。
- R6-WU-003：Configured／Active／Executed Providerを常に明示し、noneも省略しない。
- R6-WU-004：Request ID、開始／完了時刻、Frozen Modes、Budget、Outcome／Failure、Turn Recording、Judge Evidence Recordingを一つの相関表示へまとめる。
- R6-WU-005：Activation Failure Code／Reason／Provider／TimestampをPanel再読後も保持。
- R6-WU-006：Mode変更またはTurn完了後、一つ前のResultをCurrentとして残さない。
- R6-WU-007：Package R6 Recovery Index作成。

### P6-RR-R7 — Authority-independent Fixture／Authority-dependent Real Gate

- R7-WU-001：Fake Selene AdapterでLoad、Dispatch、Budget、Evidence、Repair RejudgeをEnd-to-End検証。
- R7-WU-002：Fake Qwen3Guard AdapterでAdditive Result、Frozen Mode、Executed Identityを検証。
- R7-WU-003：Built-in OBSERVE→Selene Config変更で`Mode ON / Active none`にならないことを検証。
- R7-WU-004：Built-in ENFORCE→Qwen3Guard Config変更のAtomic Commit／Rollbackを検証。
- R7-WU-005：Configured Dedicated／Active noneでMain Serviceが暗黙実行されないことを検証。
- R7-WU-006：日本語／英語とFailure Class別Fallbackを検証。
- R7-WU-007：109件Fixture BatchとMain Governance Projectionを検証。
- R7-WU-008：Real Model／Official ProvenanceはAuthorityがあれば実行し、なければそれだけを`NOT RUN / AUTHORITY REQUIRED`へ分類。
- R7-WU-009：Package R7 Recovery Index作成。

### P6-RR-R8 — Canonical Verification／Internal QA／Return

- R8-WU-001：Focused Backend／Frontend。
- R8-WU-002：Canonical Mypy／Ruff／Backend Full／Frontend Typecheck・Lint・Test・Build。
- R8-WU-003：Original Acceptance 40件とDelta Acceptance 26件を一件ずつ再導出。
- R8-WU-004：Implementation Freeze後にClaude Internal Review Cycle 1。
- R8-WU-005：FindingがあればReworkし、Cycle 2以降を実施。
- R8-WU-006：ReviewではRequirement-by-Requirement、Scenario A〜C、Cross-component Wiring、Failure Injection、Negative Pathを確認。
- R8-WU-007：Open Majorが残る場合は0へ捏造せず列挙。
- R8-WU-008：Package R8 Recovery IndexとExact Return Handoffを作成。

## 6. Mandatory Regression Scenarios

最低限、次を明示Test名またはMatrix IDで固定する。

```text
S1  Built-in Judge OFF -> OBSERVE -> Active Built-in
S2  Built-in OBSERVE中にConfigured Seleneへ変更
S3  Built-in ENFORCE中にConfigured Main Qwen／DeepSeekへ変更
S4  Guard Built-in OBSERVE中にConfigured Qwen3Guardへ変更
S5  Activation成功時のAtomic Commit
S6  Activation失敗時の完全Rollback
S7  Configured Dedicated / Active none時Model Call 0
S8  Executed IdentityはAdapter Lease由来
S9  Repair RejudgeはFrozen Judge由来
S10 109 Criterion全件Disposition／Reason
S11 Main Governance同一Turn Projection
S12 日本語のmalformed／timeout／unavailable Fallback
S13 英語のmalformed／timeout／unavailable Fallback
S14 Live Refreshで一つ前のResultをCurrent表示しない
S15 Recording FULL相関Summary
S16 OFF後Currentなし／Historical分離
S17 Stop／Cancel／Late Publish拒否
```

## 7. Acceptance Maximum

次を満たすまでPhase 6 Closure Candidateへ昇格しない。

- P6-CODEX-062〜068がCLOSEDまたはAuthority依存Gateへ正確に限定される。
- Delta 001〜026を全件再導出する。
- Authority不要項目にFAILまたは未接続が残らない。
- `Mode ON / Active none`が全Roleで成立しない。
- Executed ProviderをConfigured／Activeから推測しない。
- 109 CriterionがRealまたはFixtureのLive Turnで全件Disposition／Reasonを持つ。
- Main Governance表示とJudge／Recording EvidenceがRequest IDで一致する。
- Internal QA後もIndependent Review待ちで停止する。

Real Selene／Qwen3GuardのAuthorityがない場合、最大Claimは次でよい。

```text
COMPLETE_CANDIDATE_WITH_REAL_PROVIDER_AUTHORITY_GATE
```

その場合もFactory／Router／Lifecycle／Budget／Fixture／Failure／UIはCOMPLETEでなければならない。

## 8. True Stop Conditions

次だけで停止する。

- Project Root外Action、Provider Memory、User runtime_data、Git、NetworkまたはModel Artifactへ、Authority外で接触した。
- Frozen Contract Digest不一致。
- Source Stateが本書のPreserved Baselineと競合し、差分継続で安全に解けない。
- Userが停止、Scope変更またはResource Stopを明示した。
- Active Process／Model Loadを安全に収束できない。

Real Model Authority不足、Open Major Finding、Fixtureで再現可能なFailure、作業難度、長時間、内部ReviewでFindingが出たこと自体はStop条件ではない。成立済みPackageを再実行せず、Recovery Indexから差分継続する。

## 9. Mutation Boundary

許可されるのは、明示Start後のPhase 6差分Source／Test／Frontend／Generated Static／Phase 6 append-only Evidence／Handoffだけである。

禁止：

- Phase 6 Closure。
- Phase 7以降。
- Roadmap、Stable Shared Constitution、Public Docs。
- Git Stage／Commit／Push／Branch操作。
- Backup。
- User runtime_data。
- Provider Memory。
- NetworkとProject Root外Model Artifact。別途User Authorityがある場合だけ、その明示範囲で扱う。
- Historical Evidenceの上書きまたは削除。

## 10. Return Contract

Return Handoffは最低限次を含む。

- Provider／Role／Task Identity。
- Active Contract Digest。
- Package R0〜R8のDispositionとRecovery Index。
- Exact Changed File InventoryとSHA-512。
- P6-CODEX-062〜068のDisposition。
- Configured／Active／Executed／Recorded／Displayed Identity Matrix。
- Provider別BudgetとRepair Rejudge Identity。
- 109 Criterion Count／Disposition／Reason Count。
- Failure Class別Language Matrix。
- Recording Correlation Matrix。
- Original 40＋Delta 26 Acceptance全件。
- Internal Review CycleとFinding Ledger。
- Root外／Provider Memory／runtime_data／Git／Network／Model Mutation Inventory。
- Real Model／BrowserのPASS／PARTIAL／NOT RUN／User Gate。
- Open Critical／Major／Non-critical。
- 最大ClaimはComplete Candidateまで。

Return後はController Independent Review待ちで停止する。
