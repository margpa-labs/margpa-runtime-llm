# Phase 9 Execution Plan — 9-1 Fast Closure First

```yaml
document_id: phase_9_execution_plan
document_state: accepted_frozen_ready_not_started
phase: phase_9
language: ja
created_at: 2026-08-31 21:02:44 JST
execution_order: phase_9_1_then_phase_9_2_then_conditional_phase_9_3
first_target: P9_1_COMPLETE_CANDIDATE_FOR_CONTROLLER_REVIEW
reviewer: Codex project responsible and design governor role
```

## 1. Execution Policy

- Phase 8 Formal Closure、Roadmap更新、Clean／Commit／Push、User BackupおよびPhase 9 Preflightが終わるまでSource実装を開始しない。
- Phase 9-1を最初の独立Programとして完了候補まで連結実行する。
- Phase 9-2／9-3は、本計画の入口条件を超えて9-1へ混入させない。
- Phase 6の成立済みProvider／Lifecycle／Budget／Recording／Guard／Judge／Repair基盤を再実装しない。
- Package BoundaryでRecovery Indexを作る。CompactionまたはResource Hard Stop接近時はCurrent Work Unit単位のExact Recoveryを残す。
- Routine報告、Minor Finding、Diff量、Blast RadiusまたはIndependent Review前であることを理由に停止しない。
- RiskはFocused Test、Canonical Regression、Internal Review、RecoveryおよびExact Failure Evidenceで管理する。
- Critical／Major／MVP BlockerだけをCurrent Reworkし、Minor／Hardening／Polishは未解決Registryへ送る。
- 最大ClaimはProgramごとに分離する。9-1 ExecutorはPhase 9 Closureを主張しない。

## 2. Relative Effort

Work Unitは時間保証ではなく、Recovery可能な実施単位である。

| Program | Detail Level | Relative Effort | Current Priority |
|---|---:|---:|---|
| Phase 9-1 | Detailed／23 WU | XL／高不確実性 | 最優先・先に決着 |
| Phase 9-2 | Package予約のみ | XL | 9-1 User Checkpoint後 |
| Phase 9-3 | Conditional Package予約のみ | L〜XL | 9-2後、利用可能量で判断 |

9-1の主な不確実性は、Local Mac実Artifact Memory、Prompt／Output Contract、Semantic Criterion適用範囲およびProduction Judge／Repair配線である。UI磨き、Experiment Platform、Context Coreを切り離すことで最短化する。

## 3. Phase 9-1 Packages／Work Units

### P9-1-0 Entry／As-built／Authority Freeze — 3 WU

- **P9-1-0-WU-001**：Phase 6 Special Minimal Closure、Final User Mac Evidence、Phase 7／8 Regression BoundaryおよびCurrent未解決RegistryをAs-built Mapへ固定する。
- **P9-1-0-WU-002**：Selene／Qwen3Guard Artifact、Manifest、Prompt、Parser、Model Registry、Hardware Profile、Runtime FlagおよびComposition RootをRead-only Auditする。
- **P9-1-0-WU-003**：Local Artifact Load／Inference、Network、Git、User runtime_data、Temp、Backup、BrowserおよびModel SmokeのAuthority／禁止事項／Test Matrixを固定する。

Exit：ゼロから再実装する領域、既存再利用領域、Real Artifact Gateおよび最初のSource接続点が確定している。

### P9-1-A Dedicated Selene／Qwen3Guard Runtime — 5 WU

- **P9-1-A-WU-001**：Artifact／Manifest／Digest／Quantization／Backend／Hardware Preflight Contractを共通化し、Role固有差をAdapterへ閉じ込める。
- **P9-1-A-WU-002**：SeleneをCandidate Load、Strict Prompt／Output Decode、Inference、Deadline／Cancel、EvidenceへProduction配線する。
- **P9-1-A-WU-003**：Qwen3GuardをInput／Output Target別Contract、Line Protocol、Inference、Deadline／Cancel、EvidenceへProduction配線する。
- **P9-1-A-WU-004**：Mode ON時のCandidate Preflight／Load後Atomic Commit、Frozen Lease、OFF／Shutdown UnloadおよびFailure Recoveryを検証する。
- **P9-1-A-WU-005**：Real Local Artifact Smokeを個別Gateで実行し、Call Count、Memory／Latency、Configured／Active／ExecutedおよびFailure Stageを記録する。

Exit：Dedicated各Roleが実Artifactで動くか、物理的／Authority上動かない理由がStage別に確定する。Fixture PASSだけでDedicated PASSを主張しない。

### P9-1-B Semantic 109／Built-in Evaluation — 5 WU

- **P9-1-B-WU-001**：109 RuleをDefinition／Point／Capability／Criterion Type別に機械Inventory化し、Expected Applicabilityを固定する。
- **P9-1-B-WU-002**：Normalized IRから実Semantic Criterionへ変換するAdapter／Registryを既存Contract内で拡張する。
- **P9-1-B-WU-003**：Built-in Evaluatorの対応Criterionを実評価し、非対象／未対応／Unknown／Deferredを分離する。
- **P9-1-B-WU-004**：Main pre／post、Guard、JudgeでCriterion Identity、Count、ReasonおよびEvidenceをLosslessに投影する。
- **P9-1-B-WU-005**：Golden Case、Negative Case、Malformed Definition、Budget、Cancel、Restartおよび全109件集計をRegression Testする。

Exit：109件一律Deferredではなく、対応Criterionの実評価と非評価理由がRule単位で追跡できる。

### P9-1-C Judge／Repair／Rejudge／Semantic ENFORCE — 6 WU

- **P9-1-C-WU-001**：Main Candidate、Frozen Context、Independent Judge DispatchおよびStrict DecodeをProduction Turnへ配線する。
- **P9-1-C-WU-002**：Judge OutcomeからRepair Eligibility／Plan／Budget／Candidate生成へ接続する。
- **P9-1-C-WU-003**：Repair CandidateをRejudgeし、Adopt／Reject／Safe Fallback／Failureを同一Request Chainへ収束する。
- **P9-1-C-WU-004**：Semantic ENFORCEのSupported Action、Conflict、Priority、BudgetおよびAuthority非拡張を配線する。
- **P9-1-C-WU-005**：Cancel、Deadline、Provider Failure、Malformed、Late Result、Mode OFFおよびShutdownのNegative Golden Pathを成立させる。
- **P9-1-C-WU-006**：Configured／Active／Executed、Criterion、Judge、Repair、Rejudge、Final、RecordingのIdentity ChainとCurrent／Historical Projectionを検証する。

Exit：Judge -> Repair -> Rejudge -> Adopt／Fallbackが実Turnで成立し、Semantic ENFORCEが対応Actionだけを実行する。

### P9-1-D Integration／Review／User Manual Candidate — 4 WU

- **P9-1-D-WU-001**：通常Chat、RAG、Citation、Manual URL、Dev Agent、Persistence、Cancel／RestartのFocused Regression。
- **P9-1-D-WU-002**：Canonical Backend／Mypy／Ruff／Frontend（変更時）／Build／Static配信物の比例検証。
- **P9-1-D-WU-003**：観点変更二段階Internal Review。Cycle 1はRequirement／Negative／Concurrency／Resource、Cycle 2はEvidence Truthfulness／Acceptance／User Journey／PoC停止線。
- **P9-1-D-WU-004**：Traceability、Real Artifact Disposition、User Mac Manual Sheet、Recovery IndexおよびExact Return Handoff。

Exit：`P9_1_COMPLETE_CANDIDATE_FOR_CONTROLLER_REVIEW`。Phase 9-2はまだ開始しない。

## 4. Phase 9-1 Fast Closure Rules

### 4.1 やらないこと

- 新しい汎用Experiment Frameworkを先に作らない。
- Right-side ObservatoryまたはSettings全面改修をしない。
- Full Runtime Constitution、PADGまたは全Docs統合へ入らない。
- General Web Search、Formal Agent、CloudまたはExternal Serviceを追加しない。
- 全Semantic Ruleを同じ実装方式へHard-codeしない。
- Minor UI、命名、余白、低頻度Edge CaseをReview Loopへ追加しない。

### 4.2 Verification効率

```text
Work Unit:
  Focused Test／Type Check

Package:
  Related Integration／Regression

P9-1-D:
  Canonical Full Verification

Real Artifact:
  最小Smoke -> Golden Turn -> Stop／Unload
```

全Packageごとに全Repository Suiteを反復して利用可能量を浪費しない。Riskと変更範囲に比例する。

## 5. Phase 9-2 Reserved Packages

9-1 User Checkpoint後にAs-builtを再確認し、Work Unitを正式Freezeする。現時点のPackage境界は次とする。

1. **P9-2-A Experiment Identity／Plan／Config Snapshot**
2. **P9-2-B Evaluation Dataset／Metric／Rubric／Baseline**
3. **P9-2-C Multi-Governance Composition／Conflict／Routing**
4. **P9-2-D Freshness／False-positive RAG／Strict NO_HIT／Belief Revision**
5. **P9-2-E Model Call 0 Trace／Strict vs Progressive Presentation**
6. **P9-2-F Comparison Report／Internal Review／User Candidate**

入口条件：P9-1 Controller Review完了、UserがP9-1 Dispositionを受理、中心Identity／Evaluation／Repair Contractが安定している。

## 6. Phase 9-3 Conditional Reserved Packages

9-2後に、利用可能量とUser優先順位を再評価する。

1. **P9-3-A Effective Context Budget／Pressure State**
2. **P9-3-B Snapshot／Structured Context／Artifact Identity**
3. **P9-3-C Atomic Compaction／Rollback**
4. **P9-3-D Recovery Index／Selective Rehydration／Handoff**
5. **P9-3-E UI-independent Event／Projection Contract**
6. **P9-3-F Verification／Research Evidence／Disposition**

入口条件：P9-2のExperiment Run／Trace Identityが成立し、Compaction前後を比較可能である。Phase 10 UIを先取りしない。

## 7. True Stop Conditions

次だけをProgram全体停止候補とする。

- Authorized Root外への実Mutationまたは回復不能なUser Data破損。
- 必須Artifactが存在せず、取得に新しいNetwork／License／Cost Authorityが必要。
- Canonical Working Stateが競合し、どのStateを保持すべきかEvidenceから決定不能。
- Resource Hard StopでCurrent Work Unitを安全収束できない。
- Real ModelがMacを不安定化し、安全なUnload／Process停止ができない。
- User Manual GateまたはController Review Return Point。

実装難度、大きなDiff、Review前、不確実性、Minor Finding、既知の非Blocking Failureだけでは停止しない。

## 8. Authority Boundary

本設計文書はSource実装、Real Model Load、Network、Git、Backup、Phase 8 ClosureまたはPhase 9開始Authorityを生成しない。Phase 8 Closure、User Backup、Phase 9 READY、PreflightおよびExact Handoffを別途必要とする。
