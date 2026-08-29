# Phase 6 P6-GOV-021 — Copilot R9〜R12 Controller Independent Review

```yaml
document_id: phase_6_gov021_copilot_r9_to_r12_controller_independent_review_20260828214107
document_type: controller_independent_review
document_state: frozen
language: ja
created_at: 2026-08-28 21:41:07 JST
review_owner: Codex_プロジェクト責任者兼設計統括者役
review_target_provider: GitHub_Copilot_app
review_target_role: 設計者兼実装者役
review_target_return: phase_6_copilot_r9_to_r12_exact_return_handoff_ja_20260828212032.md
verdict: ADJUST_REWORK_REQUIRED
phase_6_closure: prohibited
phase_7: prohibited
git_action: none
network_action: none
real_model_action: none
user_runtime_data_action: none
```

## 1. 結論

CopilotのR9〜R12 `Complete Candidate` Claimは受理しない。判定は次のとおりである。

```text
Technical regression baseline: PASS
Frozen Contract completion: FAIL
Controller verdict: ADJUST / Rework Required
Open Technical Critical: 0 known
Open Technical Major: 4
Open Evidence / Return Major: 1
Open Process Incident: 1 recorded, non-blocking for technical rework
Phase 6 Closure: NOT READY
```

Copilot実装には成立した改善がある。一方、P6-CODEX-069〜073をすべてCLOSEDとするには不足があり、P6-CODEX-074〜079として差分を再Openする。

## 2. Review対象

### Return／Recovery

- `docs/project/phases/phase_6/handoffs/phase_6_copilot_r9_to_r12_exact_return_handoff_ja_20260828212032.md`
- `docs/project/phases/phase_6/history/index/phase_6_copilot_r12_final_recovery_index_ja_20260828212032.md`
- `docs/project/phases/phase_6/history/operations/phase_6_copilot_r12_internal_review_finding_ledger_ja_20260828212032.md`
- `docs/project/phases/phase_6/history/operations/phase_6_copilot_r9_path_boundary_incident_ja_20260828212032.md`
- R9〜R12のEntry／Checkpoint／Recovery群。

### Frozen Contract

- `docs/project/phases/phase_6/history/operations/phase_6_gov020_copilot_r3_to_r8_controller_independent_review_ja_20260828210944.md`
- `docs/project/phases/phase_6/handoffs/phase_6_copilot_post_independent_review_r9_to_r12_exact_rework_handoff_ja_20260828210944.md`

### Current Source／Test

R9〜R12 Return記載のSource／Test SHA-512をCurrent Fileで再計算した。記載されたDigestは一致した。これは「Return対象とCurrent Fileが同一」であることだけを示し、実装契約の成立を自動的には示さない。

## 3. Controller Verification

ControllerはProject内Task-owned Tempだけを使用した。

```text
Task Temp:
.venv/.t/phase_6_controller_copilot_r9_r12_review_20260828223000/

Backend Focused:
104 passed / Exit 0

Frontend Focused:
2 files / 16 tests passed / Exit 0

Targeted Mypy:
14 source files / 0 issues / Exit 0

Targeted Ruff:
All checks passed / Exit 0
```

最初のController pytest CommandはTest Pathを1件誤指定し、Project Root内でExitした。収集0、Root外Action 0、Source／Test／Config Mutation 0である。正しいPathへ直して上記104件を実行した。

Copilotが主張したCanonical Backend 1700 passed／Frontend 230 passedはHistorical Candidate Evidenceとして保持する。ControllerはFull Suiteを再実行しておらず、Controller独自PASSへ昇格しない。

## 4. Accepted／Preserved

次は成立部分として保全する。

1. Candidate ProviderをPreflight／LoadしてからSelection Commitへ進む方向への改善。
2. Provider別`StageBudgetProfile`をRun開始時にFreezeし、ENFORCE全体のCaller DeadlineとCancel Graceへ使用する骨格。
3. Conversation-owned Hook例外／None／空DecisionのJA／EN Fallback。
4. Turn RecordingとJudge Evidenceがbase `request_id`を保存する実装。
5. API／UIで異なるRecording IDをCurrentから外す骨格。
6. R9〜R12 Source／Test DigestのCurrent一致。
7. Focused／Static RegressionがPASSしていること。

これらは以下のOpen Findingを上書きしない。

## 5. Open Findings

### P6-CODEX-074 — Role Provider／Modeの真のAtomicity未成立

```yaml
severity: major
reopens: [P6-CODEX-069, P6-CODEX-062]
```

`provider_selection_routes._apply_role_provider_selection()`は、ModeをLock外で先に読み、その後に別Lockを持つ`RoleProviderLifecycleManager.transition_to()`または`ProviderSelectionController.select()`へ進む。

Mode Controller、Provider Selection Controller、Role Lifecycleの間に共通Transaction Lock／Composite Commitがない。特に次の競合が残る。

```text
Thread A: Provider変更RouteがMode OFFを観測
Thread B: 旧ProviderをActivateしてMode ONへCommit
Thread A: Configured-only selectをCommit
Result: Mode ON / Active none またはConfiguredとActiveの不整合
```

現行Testは成功後／失敗後の最終状態を確認するが、Mode ApplyとのConcurrency、Status Readerの中間観測、Mode Commit Failure、旧Adapter Unloadが部分失敗した場合のHonest Stateを検証していない。

また、旧Adapter `unload()`が例外を返した場合、Controller上は旧Active Tupleを保持するが、Adapterが実際に利用可能かは保証できない。それを完全Rollbackと主張してはならない。

### P6-CODEX-075 — Stage Budgetが実StageをBoundしていない

```yaml
severity: major
reopens: [P6-CODEX-070, P6-CODEX-065]
```

Provider別ProfileからENFORCE全体のWait Deadlineを導出する改善は成立した。しかし、Frozen Contract R10-WU-002はPrompt／Inference／Decode／Repair／Rejudgeを実行上Boundすることを求める。

Current Sourceでは次が後検査である。

- Judge Prompt Build：完了後のLatency比較。
- Judge Inference：`service.generate()`完了後に`apply_judge_budget_gate()`。
- Decode：完了後のLatency比較。
- Repair Generation：`service.generate()`完了後のLatency比較。
- Rejudge：`service.generate()`完了後のLatency比較。

外側のENFORCE Pipeline Deadlineは全Stage Budgetの合計であり、Judge Inference単体が自身の`inference_budget_ms`を超えて他Stageの時間を消費することを防がない。OBSERVE BackgroundにもStage単位のDeadline Ownerがない。

さらにBuilt-in ProfileのPipeline Budgetは0msである。Semantic SnapshotがBuilt-in Activeを示すENFORCE経路では、Background実行と0ms DeadlineがRaceになり得る。Built-inはModel Call 0を維持しつつ、Deterministic処理を同期または明示的なControl Budgetで確実に終端させる必要がある。

### P6-CODEX-076 — Main Governance OFF時にFrozen Languageが失われる

```yaml
severity: major
reopens: [P6-CODEX-071, P6-CODEX-066]
```

Conversation Layerの狭いHook例外／None／空Result経路はJA／EN化された。しかしJudge Hookの`frozen_language`はSemantic Snapshotがない場合に`en`へ固定される。

Semantic SnapshotはMain Runtime Governance PREがOFFなら作られない。一方、Judge Modeは独立してOBSERVE／ENFORCEにできる。したがって、次の正規構成で英語Failureが残る。

```text
Main Runtime Governance: OFF
Judge: ENFORCE
Response Language: 日本語
Semantic Snapshot: none
Judge malformed / timeout / unavailable
Result: frozen_language = en
```

`JudgeCompletionContext`自体にTurn開始時のResponse Languageがないことが根因である。またRepair Rejudgeの`EvaluationCase.language="en"`もFrozen Languageを継承していない。

### P6-CODEX-077 — Recording CorrelationはJudge非依存TurnとFrozen Modeを扱えない

```yaml
severity: major
reopens: [P6-CODEX-072, P6-CODEX-067]
```

APIのRecording Correlationは`JudgeGovernanceComposition.current_request_id()`を正本にする。しかしProduction ConversationはJudge OFF時にJudge Hookを呼ばないため、`mark_skipped(judge_off)`は到達しない。Recording FULL／Judge OFFの新Turnでは、Judge側Request IDが前Turnのままになり、新しいTurn RecordingがHistorical／Unmatched扱いになる。

RecordingはJudgeから独立したModeであり、Current Turn IdentityをJudge Compositionだけに依存させてはならない。

加えてTurn Recording Hookは`context.recording_mode`ではなく、完了時のLive `RecordingModeController`を読み直す。一方Judge EvidenceはTurn開始時にFrozenされたRecording Modeを使う。Turn途中でModeが変わると、同じRequest IDのTurn RecordingとJudge Evidenceが異なるMode契約で動く。

UIの`feature-modes-recording-correlation-summary`はRecording 2種類だけを表示し、Judge Result／Final Disposition／Failureと一つのServer-side Correlation Contractへ統合していない。土台は改善したが、Single Request-ID SummaryはPARTIALである。

### P6-CODEX-078 — R12 Return Contract未充足

```yaml
severity: major_evidence
reopens: [P6-CODEX-073, P6-CODEX-068]
```

R12 Returnは次を省略または一括Claimで代替した。

- S1〜S17の各Test Path／Test Name／Exact Result。
- Original 40＋Delta 26の全66 ID個別DispositionとEvidence Pointer。
- Full Path付きChanged File Inventory。
- Canonical VerificationのExact Command／Scope／Exit Evidence。
- Identity／Budget／109 Criterion／Failure Language／Recording Matrixの具体値。
- Requirement-by-Requirement／Cross-component／Failure Injection／Negative Pathを含む実質的Internal Review Cycle 2。

「Canonical Regressionでcovered」は66件個別再導出の代替にならない。R9〜R11 Recoveryも数行であり、WU単位の成立境界を復旧できる情報量に達していない。

### P6-CODEX-079 — Copilot R9 Root境界Incident

```yaml
severity: process_incident
technical_rework_blocking: false
```

Copilot Evidence自身が、Canonical Rootの親側にTask Temporary Directoryを一度作成したと記録している。これはActive Contract上のProject Root外Writeであり、`external_contact: none`とは両立しない。

Persistent Product Artifact、Git、Network、Secret、Provider Memory、User runtime_data、Model Artifactへの接触は確認されていないため、Technical Reworkを止めるCritical Integrity Failureへは昇格しない。ただしIncident 0／Root-outside Action 0へ改変してはならない。

## 6. Required Differential Rework

次のClaude差分Handoffで扱う。

1. Provider／Mode／Lifecycle／Status Projectionを共通Transaction Boundaryへ統合する。
2. Stage Budgetを各StageのDeadline／Cancellation Ownerへ昇格し、Built-in 0ms Raceを除く。
3. Response LanguageをTurn開始時にJudge ContextへFreezeし、Semantic Snapshot非依存で全Failureへ継承する。
4. Recording Current IdentityをJudge非依存にし、Turn／Judge Result／Judge Evidenceを単一Request-ID SummaryへJoinする。
5. Recording ModeをTurn開始時Freezeへ統一する。
6. 66 Acceptance、S1〜S17、全Matrix、Full Path／SHA／Exact Commandを再導出する。

## 7. Boundary／Next Action

```text
Root-outside Action by Controller Review: 0
Git Action: 0
Network Action: 0
Provider Memory Contact: 0
User runtime_data Contact: 0
Real Model Load / Inference: 0
Source / Test / Config Mutation by Controller: 0
Phase 6 Closure: 0
Phase 7 Action: 0
```

Exact Next ActionはClaude用Frozen Exact Differential Rework HandoffのBootstrapである。Claude実装後も最大ClaimはComplete Candidateまでとし、Codex Independent ReviewとUser Mac Manual GateなしにPhase 6 Closureへ進まない。
