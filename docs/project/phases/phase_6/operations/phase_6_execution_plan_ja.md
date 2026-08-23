# Phase 6 Execution Plan

    document_id: phase_6_execution_plan
    status: accepted_frozen_not_activated
    phase: phase_6
    recorded_at: 2026-08-22 21:13:08 JST
    implementation_authorized: false
    completion_line: phase_6_i_complete_candidate

## 1. Execution Policy

Phase 6-0〜6-IをClaude側設計統括者役が長期連結実行し、6-JをCodex／User Gateとして分離する。Work UnitはAuto-Compactionから再開可能な有界単位とするが、Recovery／Evidence文書はWork Unitごとに量産せずSubphaseまたはMaterial Boundary単位でまとめる。

## 2. Subphase Map

    6-0  Entry／As-built Reconciliation／Exact Freeze
    6-A  DeepSeek Local Artifact／Backend Feasibility
    6-B  Runtime Model／Context／Token Control
    6-C  Evaluation Contract／Dataset／Deterministic Judge
    6-D  LLM-as-a-Judge／Independence／Calibration
    6-E  Bounded Repair／Success Evaluation
    6-F  Runtime Status／Safe Refusal／Feedback／Recording
    6-G  Advanced Settings／Sidebar／UI Naming Cleanup
    6-H  Comparative Experiment
    6-I  Integrated Adversarial Verification／COMPLETE_CANDIDATE
    6-J  Codex Independent Review／User Acceptance／Full Closure

## 3. Work Units

### Phase 6-0 — Entry／Freeze

#### P6-0-WU-001：Authority／Recovery Preflight

Mandatory Reading、Authorized Root、Read-only Git Current Diff、Phase 5 Technical／Mac Acceptance、Automation State、Compaction Recoveryおよび禁止Scopeを確認する。Git Index／Ref／Worktree Mutationは行わない。

#### P6-0-WU-002：Phase 4／5 As-built Reconciliation

Main Governance、Guardrail、Policy、Authority、Configuration Control、Streaming、Persistence、RAGおよびUIの実Source／Testを照合する。

#### P6-0-WU-003：Model／Runtime／Resource Reconciliation

Qwen Current Route、models Symbolic LinkのLogical／Resolved Boundary、DeepSeek Canonical Snapshot、llama.cpp Toolchain、Config Registry、Disk／Memory／Backend Capabilityを確認する。Resolved Target内容のReadはActivation ReceiptのExact Authority成立後に限る。

#### P6-0-WU-004：Exact Mutation／Test／Rollback Freeze

Frozen DesignとAs-built差分から必要なSource／Test／Derived Artifact範囲を動的に確定し、Phase 6-0 Recovery Entryを作る。

### Phase 6-A — DeepSeek Local Feasibility

#### P6-A-WU-001：Canonical Snapshot Revalidation

Exact Commit、Manifest、Missing File、Size、Source Digest EvidenceおよびLicenseを再検証する。全巨大Weight Digest再計算のCostと必要性を区別する。

#### P6-A-WU-002：Conversion Tool／Recipe Freeze

Official Snapshot→GGUF→Q4_K_MのTool Revision、Recipe、Tokenizer／Template、Output Path、Disk GateおよびRollbackを確定する。

#### P6-A-WU-003：Derived Artifact Creation

Activation時のModel Mutation Authority内でだけDerived ArtifactとManifestを作成し、Sourceを変更しない。

#### P6-A-WU-004：Local Load／Unload Smoke

Load、First Token、Streaming、Cancel、Unload、Reload、Context、Memory、LatencyおよびThermal観測を行う。

#### P6-A-WU-005：Feasibility Decision

Supported／Degraded／Unsupportedを事実に基づき確定する。False Successを禁止し、Qwen継続可能なBoundaryを残す。

### Phase 6-B — Runtime Model／Generation Control

#### P6-B-WU-001：Runtime Model Domain／Ports

Snapshot、Role Binding、Capability、Transition、Receipt、Failure、CASおよびBusy Contractを実装する。

#### P6-B-WU-002：Backend Adapter／Model Definition

Qwen／DeepSeekを同じModel Portへ登録し、Artifact／Template／Backend差をAdapter／Definitionへ隔離する。

#### P6-B-WU-003：Qwen→DeepSeek→Qwen Switch

Idle-only Switch、Unload／Load、Atomic Commit、Load FailureおよびRollback Failureを実装する。

#### P6-B-WU-004：Dynamic Context Size

Capability-derived Maximum、Preview、Internal Reload、成功照合、RollbackおよびStateを実装する。

#### P6-B-WU-005：Dynamic Max New Tokens

固定Frontend上限を除去し、Server Capability、Prompt TokenおよびReserved Token込みのValidationを実装する。

#### P6-B-WU-006：Generation Identity／Compatibility

Turn／AttemptへExact Model／Artifact／Backend／Context／Configを関連付け、Conversation／RAG／Governance／Guardrail回帰を確認する。

#### P6-B-WU-007：Model Control Recovery

Subphase Test、Manual Load Evidence、Exact MutationおよびCurrent Support StateをRecovery Entryへまとめる。

### Phase 6-C — Evaluation／Deterministic Judge

#### P6-C-WU-001：Evaluation Domain／Ports

Dataset、Case、Criteria、Ground Truth、Evaluator Binding、Run、Result、MetricおよびFailureを実装する。

#### P6-C-WU-002：Evaluation Dataset／Manifest

Synthetic／Public／Project-approved Reference FixtureをManifest化する。Qwenの知ったかぶり、定義混同、根拠不足、矛盾、形式逸脱および不確実性表現を含める。

#### P6-C-WU-003：Deterministic Evaluator Registry

Schema、Exact Reference、Required Field、Contradiction、Unsupported Claim CandidateおよびFormatの交換可能Evaluatorを実装する。

#### P6-C-WU-004：Result／Metric／Evidence

Dimension Result、Confidence、Ground Truth State、Latency／Token／CallおよびSafe Evidenceを実装する。

#### P6-C-WU-005：Baseline Verification

Model 0件、Judge OFF、Deterministic-only、Unknown ReferenceおよびMalformed Caseを検証する。

### Phase 6-D — LLM-as-a-Judge

#### P6-D-WU-001：Typed Judge Adapter

Role、Artifact、Rubric、Prompt Digest、Seed、Config、Timeout、Token、Latency、CostおよびFailure Contractを実装する。Selene候補を含む将来の専用JudgeをCore変更なしで追加できるPortを維持する。

#### P6-D-WU-002：Role-separated Runtime Binding

Main自己評価、同一Artifact Judgeおよび独立Artifact Judgeを区別し、Availability／Independence Stateを投影する。

#### P6-D-WU-003：Rubric／Prompt／Output Decoder

CriteriaをBounded Typed Promptへ変換し、Strict DecoderでUnknown／MalformedをFail-closedする。Raw Judge Promptを通常Evidenceへ保存しない。

#### P6-D-WU-004：Calibration／Bias Matrix

順序反転、回答長差、言語差、Self-preference、ConfidenceおよびDeterministic ResultとのConflictを検証する。

#### P6-D-WU-005：Real Local Judge Experiment

AvailableなQwenまたはDeepSeekで少なくとも一つの実LLM Judge Runを行い、Fake／Stub TestとEvidence Classを分離する。

#### P6-D-WU-006：Failure／Cost Gate

Unavailable、Timeout、Context Overflow、Cancel、Model Switch競合およびCost／Token上限を検証する。

### Phase 6-E — Bounded Repair

#### P6-E-WU-001：Repair Domain／Registry

Trigger、Strategy、Plan、Attempt、Budget、Success Criterion、ResultおよびFailureを実装する。

#### P6-E-WU-002：Eligibility／Authority Resolver

Judge Recommendation、Guardrail／Authority Result、Mode、CapabilityおよびBudgetから実行可否を決定する。

#### P6-E-WU-003：Repair Orchestrator

New Attempt、Structured Feedback、Generation、全Governance Point再通過、RejudgeおよびPresented Answer選択を実装する。

#### P6-E-WU-004：Loop／Budget Prevention

Attempt、Depth、Call、Token、Wall Time、Deadline、CancelおよびRecursionを有界化する。

#### P6-E-WU-005：Success／Degradation Evaluation

Before／Afterを同Criteriaで比較し、Improved／No Change／Worse／Unknownを区別する。

#### P6-E-WU-006：Terminal／Persistence／Conflict

Safety Deny非解除、Ghost Completion 0、Hidden Original非保存、Commit-before-completedおよびRetry／RegenerateとのIdentity分離を検証する。

### Phase 6-F — Observability／Presentation／Recording

#### P6-F-WU-001：Runtime Event Contract

Request／Turn／Generation／Judge／Repairを相関するEvent EnvelopeとState Machineを実装する。

#### P6-F-WU-002：Current Request Status Projection

Current RequestとHistorical Latestを分離し、未実行PointへTyped Stateを表示する。前RequestのOutput／Stream Result混在を解消する。

#### P6-F-WU-003：Safe Refusal Presentation

Guardrail RejectをModel Call 0のまま日本語／英語の安全な会話表示へ変換し、Reload／Resumeで再構築する。

#### P6-F-WU-004：User Feedback

Good／Bad、Category、Optional Comment、明示的な再生成／修正要求、Traceability、PrivacyおよびNo-auto-trainingを実装する。

#### P6-F-WU-005：Recording Modes

OFF／METADATA／FULL、Local-only Adapter、runtime_data Scope、Atomic Write、Quota／FailureおよびGit除外境界を実装する。

#### P6-F-WU-006：Protected Data Negative Matrix

Thinking、System Prompt、Secret、RAG Internal Context、Tool内部、Hidden OriginalおよびPartial Output保存0を検証する。

### Phase 6-G — Integrated UI

#### P6-G-WU-001：Sidebar Current Model

Current Model、Loading／Switching／Rollback／UnavailableをServer Snapshotから表示する。

#### P6-G-WU-002：Advanced Component Identity

Current Main Model、Current Guardrail Model、Current LLM-as-a-Judge Model、Current Governance LayerとStateを表示する。

#### P6-G-WU-003：Context／Token Control UI

Current、Requested、Maximum、Source、Reload要否、Preview／Apply／Rollback Resultを表示する。

#### P6-G-WU-004：Judge／Repair／Recording UI

Default OFF、Current Mode、Apply、Status、BudgetおよびFailureを安全に表示する。

#### P6-G-WU-005：UI Naming／Legacy Cleanup

Main Runtime Governance、Guardrail Governanceその他の利用者向けLabelからPhase番号を除去する。Phase 3専用設定Panelを通常Surfaceから整理し、内部基盤を保持する。

#### P6-G-WU-006：Browser Synchronization／Accessibility

Settings再Open、Reload、別Tab、CAS Conflict、ja／en、Keyboard、Focus、Responsive LayoutおよびNo-secret Projectionを検証する。

### Phase 6-H — Comparative Experiment

#### P6-H-WU-001：Experiment Freeze

Dataset、Model、Role、Mode、Seed候補、Definition、Rubric、BudgetおよびMetricをFreezeする。

#### P6-H-WU-002：Qwen Mode Comparison

Governance／Guardrail／Judge／RepairのOFF／OBSERVE／ENFORCE組合せをQwenで比較する。

#### P6-H-WU-003：DeepSeek Comparison

Supportedの場合だけ同DatasetをDeepSeekで実行する。Unsupportedの場合はCall 0とReasonを記録する。

#### P6-H-WU-004：Judge／Repair Effect

Accuracy Candidate、Unsupported Claim、Definition Confusion、Abstention、Over-refusal、Repair Success／Worse、Token／Latency／Callを比較する。

#### P6-H-WU-005：Recording／Feedback／Reproducibility

Run Manifest、Digest、Result、Recording Mode、Feedback境界および再実行可能性を検証する。

RAGは機能Smokeだけとし、回答品質の最終判定をPhase 7へ渡す。

### Phase 6-I — Integrated Verification

#### P6-I-WU-001：Adversarial／Fault Matrix

Malformed Judge、Stale Digest、Race、Cancel、Switch、Context Overflow、Repair Exhaustion、Recorder Failure、Status FailureおよびSecret非露出を検証する。

#### P6-I-WU-002：Full Regression／Static／Frontend

Backend Full、Frontend Test／Typecheck／Lint／Build、Ruff／Mypy、Source／Diff／Public／Basic／runtime_data Boundaryを検証する。

#### P6-I-WU-003：Real Browser Golden Path

Model Switch、Context／Token変更、Mode再Open、Safe Reject、Judge、Repair、Status、Identity、Conversation／Citation RecoveryをMac Localで確認する。User実Dataを自動操作しない。

#### P6-I-WU-004：Self-review／COMPLETE_CANDIDATE

Design Conformance、Exact Mutation、Test、Model Artifact、Open Major Finding、Compaction／Quota、False Completion、Human BurdenおよびRollbackを日本語Handoffへ統合し停止する。

### Phase 6-J — Codex／User Full Closure

1. Codex Independent Major Review。
2. Claude局所Reworkと再Review。
3. User Mac Manual Acceptance。
4. Phase 4〜6 Program Full Review／Lossless Compilation／Manifest。
5. Current／Phase Index／Roadmap／Recovery更新。
6. User Backup／SHA-512／復元可能性Gate。
7. Phase 7 READY。
8. 明示許可範囲のCommit／Pushと一致確認。

## 4. Validation Ladder

    Per WU       : Focused Test
    Per Subphase : Focused + Adjacent Regression + Static
    6-B／6-D／6-E: Material Runtime／Model Test
    6-H          : Reproducible Comparison
    6-I          : Full Backend／Frontend／Static／Adversarial
    6-J          : Codex Independent + User Mac + Full Closure

Full Suiteと大量EvidenceはMaterial Boundaryでまとめ、小修正ごとに数千File Contextを生成しない。

## 5. Stop Conditions

- Project Root外、Git Mutation、Network、AWS、Lightning、Secret、課金、User実DataまたはStable正本への権限拡張が必要。Activation Receipt記載のExact Model Symlink Target操作と許可済みRead-only Git Inspectionは除く。
- Qwen／Canonical DeepSeek／V4等の保護Artifactを変更／削除する必要。
- Frozen Scopeを変える重大設計衝突。
- Model Conversion／Loadに未承認のDisk／Memory／Thermal Riskがある。
- models Symbolic LinkのResolved Target／DeepSeek Subtreeに対するCurrent CycleのExact Authorizationがない。
- Irreversible Storage MigrationまたはConversation破壊が必要。
- 最上位規則違反またはHuman Risk受容が必要。

通常の局所Bug、Test Failure、UI不整合、Recovery、CompactionおよびQuota自動再開は停止理由にしない。
