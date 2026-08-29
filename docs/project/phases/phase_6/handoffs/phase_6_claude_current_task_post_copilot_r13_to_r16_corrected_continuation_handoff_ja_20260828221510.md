# Phase 6 Claude Current Task Post-Copilot R13〜R16 Corrected Continuation Handoff

```yaml
document_id: phase_6_claude_current_task_post_copilot_r13_to_r16_corrected_continuation_handoff_20260828221510
document_type: corrected_differential_continuation_handoff
document_state: ready_for_single_step_start
language: ja
created_at: 2026-08-28 22:15:10 JST
authority_owner: Codex_プロジェクト責任者兼設計統括者役
target_provider: Claude
target_role: 設計者兼実装者役
target_task: current_existing_claude_task
preserved_baseline: current_working_tree_after_claude_and_copilot_r0_to_r12
first_exact_work_unit: P6-RR-R13-WU-001
remaining_packages: P6-RR-R13_to_R16
maximum_claim: complete_candidate_with_real_provider_and_user_manual_gates
phase_6_closure: prohibited
phase_7: prohibited
git_mutation: prohibited
network: prohibited
```

## 1. Correction／Supersession

本書は、次の旧Handoffを運用面でSupersedeする。

`docs/project/phases/phase_6/handoffs/phase_6_claude_post_copilot_r13_to_r16_exact_rework_handoff_ja_20260828214107.md`

旧Handoffの技術FindingとR13〜R16の実装目的は維持する。ただし、次の過剰契約は撤回する。

- Fresh Task前提および旧Claude Contextの一律非継承。
- Role／Authority Bootstrapの再実行。
- Mandatory Reading 44件の全再読。
- 各Work Unit成立後のRecovery Index必須化。
- Root外のRead／List／Stat、Git Read-onlyまたは実害のないTool Attemptだけで即時STOPPED_SAFEとする契約。
- 軽微なProcess IncidentごとにController判断を待ってLong-run全体を停止する運用。

対象は、現在待機中の同一Claude Taskである。新Task作成、初期化または旧Context消去を要求しない。

## 2. Current Baseline／Reconciliation

1. Claudeが5時間制限等で停止していた間に、GitHub Copilotが同じCurrent Working Treeへ正当な差分実装を行った。
2. CopilotによるCurrent Source／Test変更は外部競合や不明な改変ではなく、現在のPreserved Baselineである。
3. Claude自身が停止前に保持していたR0〜R3途中状態へ差し戻さない。Claude旧記憶とCurrent Sourceが異なる場合はCurrent Sourceを正本とする。
4. Copilot R9〜R12 Complete CandidateはCodex Independent Reviewにより`ADJUST / Rework Required`であり、P6-CODEX-074〜079が残っている。
5. R0〜R12をRollbackまたは一括再実装せず、Current SourceからR13〜R16だけを差分継続する。

## 3. Required Current Reading

現在のClaude TaskはRole文書および過去Phase 6文書を既に読了しているため、全再読しない。開始時に次の3文書だけを読む。

1. 本書。
2. `docs/project/phases/phase_6/history/operations/phase_6_gov021_copilot_r9_to_r12_controller_independent_review_ja_20260828214107.md`
3. `docs/project/phases/phase_6/handoffs/phase_6_copilot_r9_to_r12_exact_return_handoff_ja_20260828212032.md`

Current Source／Testは実装対象に到達した時点で必要な範囲だけ読む。Workspace全走査、過去文書の全再走査またはReceipt専用Digest確認は不要である。

## 4. Current Open Findings

```text
P6-CODEX-074: Unified Provider / Mode / Lifecycle Transaction
P6-CODEX-075: Real Stage-owned Deadline / Budget Enforcement
P6-CODEX-076: Turn-frozen Language independent of Semantic Snapshot
P6-CODEX-077: Judge-independent Request-ID Recording Correlation
P6-CODEX-078: Contract-complete QA / Return
P6-CODEX-079: Historical Copilot Root Boundary Incident accounting
```

P6-CODEX-079はHistorical Process Incidentの記録要件であり、それ自体は技術実装を停止させない。

## 5. Exact Remaining Packages

### P6-RR-R13 — Unified Role Transition Transaction

- Judge／GuardのProvider Selection、Mode Apply、Lifecycle、Status Readを同一のRole Transition Coordinator／Lock Boundaryへ置く。
- Mode SnapshotとConfigured CommitのTOCTOUを除く。
- Provider変更とMode OFF／OBSERVE／ENFORCE変更を直列化し、`Mode ON / Active none`等の中間Tupleを外部観測不能にする。
- Provider Selection GET、Feature Modes GET、Mode Apply、Provider Applyが旧または新の完全Tupleだけを返すようにする。
- Preflight、Candidate Load、Old Unload、Selection Commit、Mode Commit、RollbackをJudge／Guard双方でFailure Injection検証する。
- Old Unload部分失敗時はFalse Activeを表示せず、再Load成功またはMode OFF＋DEGRADED／FAILEDへ収束する。
- Active Turn Drain、No-op Reselect、Shutdown、Concurrent Status Reader、Concurrent Mode ApplyをRegression化する。

### P6-RR-R14 — Stage Budget／Built-in／Frozen Language

- Prompt Build、Judge Inference、Decode、Repair Generation、Rejudgeが各自のStage Deadline／Cancel／Terminal Ownerを持つ。
- 他Stageの余剰時間を流用せず、Stage超過時にCancellationを発火する。
- Cancellation無視WorkerからPresented Final、Evidence、Last ResultへのLate Publishを拒否し、Worker／Leaseは実完了まで追跡する。
- OBSERVE BackgroundにもStage Deadline Ownerを持たせ、未追跡Thread／Timerを残さない。
- Built-in DeterministicはModel Call 0、LLM Wait 0を維持し、0ms Deadline Raceなく確定終了する。
- Turn開始時Response LanguageをSemantic Snapshotから独立してFreezeする。
- Judge、Repair、RejudgeおよびFailure Presentation全経路へ同じFrozen Languageを継承する。
- Repair Rejudgeの`EvaluationCase.language="en"`固定を除く。

### P6-RR-R15 — Request-ID Observability／Recording Correlation

- Current Turn IdentityをJudge Compositionから独立した共有Correlation Registryへ置く。
- Judge OFF＋Recording FULL／METADATAでも新TurnをCurrentとして扱い、過去Judge Requestへ誤Joinしない。
- Turn開始時Frozen Recording ModeをTurn RecordingとJudge Evidenceの双方で使用し、完了時のLive Mode再読を除く。
- Turn、Judge Result、Judge Evidenceをbase request_idでServer-side Joinする。
- UI SummaryへRequest ID、時刻、Frozen Modes、Configured／Active／Executed、Budget、Judge Outcome、Final Disposition、Failure、Turn Recording、Judge Evidence Recordingを表示する。
- OBSERVE Background中のCurrent＋Pending、完了後の同Request ID結果、別RequestのHistorical／Unmatched分離を成立させる。
- 2秒Poll、設定再Open、Unmount Cleanup、Out-of-order Responseを維持する。

### P6-RR-R16 — Internal Review／QA／Return

- R13〜R15 Focused Backend／Frontendを実行する。
- S1〜S17をTest Path／Exact Test Name／Result付きで再構築する。
- Original Acceptance 40＋Delta Acceptance 26を66 ID個別に再導出する。
- Identity、Stage Budget／Cancel／Rejudge、109 Criterion、Failure Language、Request-ID Correlation Matrixを作る。
- Full Path付きChanged File InventoryとSHA-512を作る。
- Implementation Freeze後、Requirement、Cross-component、Concurrency、Failure Injection、Negative Path、Claim Auditを含むInternal Review Cycle 1を実施する。
- FindingをReworkし、Cycle 2で再Reviewする。Cycle 2でFindingが残れば同じCycleを必要範囲で繰り返す。
- Canonical Mypy／Ruff／Backend Full／Frontend Typecheck・Lint・Test・Buildを実行する。
- Final RecoveryとExact Return Handoffを作成する。

## 6. Automation／Recovery — Proportional Rule

1. Recovery Indexは各Package Finalで1件作成する。各WUごとの文書作成は不要である。
2. 5時間制限、週間制限、CompactionまたはPlatform停止が近いと判明した場合は、可能な範囲で成立境界とExact Next WUを最新Package Recoveryへ残す。
3. Progress報告、Test Failure、Finding、長時間処理、Authority-dependent Real Gateは単独の停止理由ではない。
4. 指示範囲内の設計、実装、修正、Test、Internal Review、Recovery作成は追加確認なしで継続する。
5. 不明点が非破壊的な実装判断で解決できる場合は、妥当な仮定をEvidenceへ明記して継続する。
6. 同じ質問、Receipt、全Mandatory Readingまたは完了Packageを繰り返さない。

## 7. Tool／Mutation Boundary

許可：

- R13〜R16に必要なSource／Test／Frontend／Generated Static／必要最小ConfigのRead／Mutation。
- Project内Task-owned Temp／Cache／Log。
- Phase 6のPackage Recovery、Operations Evidence、Final Handoff。
- Focused／Static／Regression／Buildおよび必要な通常Command。
- Python、Node、Compiler、Package Manager等が通常実行のためSystem Runtime／Libraryを読むこと。

禁止：

- Git Mutation、Stage、Commit、Branch、Reset、Checkout、PushまたはGitHub Action。
- Git Read-onlyも使用しない。ただし誤ってRead-only Git Commandを実行し、Mutation／Network／Secret接触が0なら、それだけでLong-runを停止しない。
- Network／Web／MCP／外部Account操作。
- Provider Memory、User `runtime_data/`への接触。
- Real Model ArtifactのRead／Load／Inference。
- Backup、Roadmap、Stable Shared Rule、Public Docs、Constitution、Phase 6 Closure、Phase 7。
- Historical Evidenceの上書き／削除。

制御可能なTemp／Cache／LogはProject内へ置く。ToolまたはRuntimeがSystem Libraryを読むこと、あるいは実害のない外部Log／Temp作成Attemptを表示しただけでは停止しない。

## 8. Incident Classification

### Record and Continue

次は、再発を避け、次のPackage RecoveryまたはFinal Incident Inventoryへ正直に記録したうえで継続する。

- Git Read-onlyを誤って実行したがMutation／Network／Secret接触が0。
- Project Root外の名前、metadata、System RuntimeまたはLibraryを意図せずReadしただけ。
- ToolがRoot外Log／Temp作成を試みたが、Material Persistent ArtifactまたはSensitive Data接触が成立していない。
- Command typo、Test Failure、Lint Failure、Type Failureまたは回復可能な実装Failure。

Incidentを隠蔽したり0件と捏造してはならない。一方、軽微なIncidentごとにUser／Controller回答を待つためLong-runを止めてはならない。

### True Stop

- Userの明示StopまたはScope変更。
- 利用可能量、5時間制限またはPlatform Hard Stopで実行継続不能。
- Destructive／不可逆Actionが必要。
- Git Mutation、Stage、Commit、Branch、Reset、CheckoutまたはPushが成立した、または成立状態が不明。
- 未許可Network、外部Account Mutation、Message送信、DeploymentまたはSecret／Credential／Privacy接触が成立した、または成立状態が不明。
- User Data、Real Model ArtifactまたはProject Root外へMaterial Persistent Mutationが成立し、安全な影響範囲を確認できない。
- Current Sourceの同一箇所に未解決の並行編集があり、安全に差分継続不能。
- Critical Integrity Failure。
- Active Processを安全に収束不能。

## 9. Return Contract

最低限、次を含める。

- R13〜R16 Package DispositionとRecovery Path。
- P6-CODEX-074〜079のDisposition。
- S1〜S17のTest Path／Exact Test Name／Result。
- Original 40＋Delta 26の66 ID別Disposition／Evidence Pointer。
- Full Path付きChanged File Inventory／SHA-512。
- Identity、Stage Budget／Cancel／Rejudge、109 Criterion、Failure Language、Request-ID Correlation Matrix。
- Internal Review Cycle 1、Finding、Rework、Cycle 2。
- Canonical VerificationのExact Command／Scope／Count／Exit。
- Incident Inventory。既知Incidentを隠蔽または0へ捏造しない。
- Real Model／BrowserのPASS／PARTIAL／NOT RUN／USER GATE。
- Open Critical／Major／Non-critical。

最大ClaimはComplete Candidateまでとする。Phase 6 Closure、Git、Backup、RoadmapまたはPhase 7へ進まない。完了後はCodex Independent Review待ちで停止する。
