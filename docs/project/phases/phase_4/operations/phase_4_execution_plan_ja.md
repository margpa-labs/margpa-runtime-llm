# Phase 4 Execution Plan

```yaml
document_id: phase_4_execution_plan
status: accepted_frozen_ready_for_backup
phase: phase_4
language: ja
recorded_at: 2026-08-21 22:04:22 JST
implementation_authorized: false
claude_completion_line: phase_4_g_complete_candidate
frozen_at: 2026-08-21 23:20:56 JST
```

## 1. Execution Principle

Phase 4〜6全体Architectureを共有するが、Phase 4だけを実装する。各SubphaseはMaterial Boundaryであり、軽微な途中報告で停止しない。

## 2. Subphase Plan

```text
Phase 4-0 : Entry／As-built Reconciliation／Execution Freeze
Phase 4-A : Standard Result／Identity／Snapshot Contracts
Phase 4-B : Binding／Cache／Capability／Authority Boundary
Phase 4-C : Typed Definition Extension／Deterministic Evaluation
Phase 4-D : Main Model pre／post Point Runtime
Phase 4-E : Mode／Conflict／Action Resolver／Enforce MVP
Phase 4-F : Evidence／Configuration／Web／UI Integration
Phase 4-G : Integrated Verification／Automation Evidence／COMPLETE_CANDIDATE
Phase 4-H : Codex Independent Review／User Acceptance／Minimal Closure
```

## 3. Work Units

### Phase 4-0

#### P4-0-WU-001：Entry Preflight

Phase 3 Closure、Current HEAD、Working Tree、Qwen Current Route、Phase 3 As-built Package／IR／Plan／Evidence Contract、Forbidden PathおよびUser Backup報告を確認する。Read-only。Phase 3 ClosureとAs-built Reconciliationは開始前Controller Gateで成立済みだが、ClaudeはActivation時点の差分とBackup報告を再確認する。

#### P4-0-WU-002：As-built Compatibility Matrix

既存v1／v2／Persistent／Ephemeral／RAG／Configuration／Governance Route／Public／Basicの変更禁止・拡張境界を、Controller Reconciliationを起点に実Source／Testから再確認する。重大差分がなければ既存Reconciliationを再作成しない。

#### P4-0-WU-003：Exact Execution Freeze

Phase 4-A〜GのAllowed／Forbidden Path Class、Baseline Test、Material Recovery境界およびCompletion LineはController Exact Freezeを継承し、Activation時点のHEAD／Working Treeだけを追補する。

### Phase 4-A — Contracts

#### P4-A-WU-001：Identity／Snapshot

Point Invocation、Binding、Evaluation、Action、Result、Capability／Authority／Policy／Budget SnapshotのTyped Identityを実装する。

#### P4-A-WU-002：Standard Result

Observation／Deviation／Score／Critical Flag／Recommendation／Execution／Cost／Evidenceを分離したImmutable Resultを実装する。

#### P4-A-WU-003：Contract／Limit／Canonicalization Test

Cross-ID、Unbounded Collection、NaN、Raw Payload、Digest不整合およびUnknown StateをFail-closed Testする。

### Phase 4-B — Binding

#### P4-B-WU-001：Binder Port／Bound Plan

Unbound Planを変更せず、Point／Capability／Authority／Policy／Budget／RegistryをBinding Artifactへ変換する。

#### P4-B-WU-002：Binding Cache／Invalidation

全Integrity InputをKeyへ含め、Hit時再検証、Revision変化、OFF、Registry変更およびStale ArtifactをTestする。

#### P4-B-WU-003：Unknown／Conflict／Authority Matrix

Unknown Rule／Action、Dependency不足、Conflict、Authority不足およびDefinition 0件を実行不能または明示No-opへ落とす。

### Phase 4-C — Definition／Evaluation

#### P4-C-WU-001：Generic Typed Execution Descriptor

Rule、Condition、Evaluator、Recommended ActionおよびLossを表すGeneric Extensionを実装する。固有GD名をCoreへ入れない。

#### P4-C-WU-002：ARGD／DAGD Trusted Adapter Extension

Reference Sourceの実Fieldを読み、存在するSemanticsだけをGeneric Descriptorへ変換する。Ambiguity／欠落を推測補完しない。

#### P4-C-WU-003：Deterministic Evaluator

追加Model Call 0で評価できるRuleを実装し、Fact／Observation／Evaluationを分離する。

#### P4-C-WU-004：Corpus／Adapter Adversarial Matrix

Unknown Definition、Malformed、Digest変化、Unsupported Field、Source不在、順序変化、巨大入力およびAdapter LossをTestする。

### Phase 4-D — Main Point Runtime

#### P4-D-WU-001：Point Runtime Port

`main_model.pre／post`のInvocation、ResultおよびFailure Contractを実装する。

#### P4-D-WU-002：Pre-generation Observe

Premise／Scope／Context／Configの評価を非介入で接続する。Existing Model InputのByte／Semantic同値をTestする。

#### P4-D-WU-003：Post-generation Observe

Canonical Final Outputを非介入評価し、Streaming／Summary／RAG Citation／Persistent Completion順序を維持する。

#### P4-D-WU-004：Concurrency／Cancellation／Terminal Matrix

Multi-tab、Stop、Cancel vs Complete、Retry／Regenerate、BranchおよびObserver FailureをTestする。

### Phase 4-E — Enforce MVP

#### P4-E-WU-001：Conflict Resolver

Authority、Policy Scope、Point、Criticality、Dependency、EvidenceおよびCapabilityでResolutionする。固定Priorityだけにしない。

#### P4-E-WU-002：Action Registry／Adapters

Phase 4 Allowlist ActionとSchema、Authority、Mode、Side Effect Class、Rollback／Evidenceを実装する。

#### P4-E-WU-003：Enforce Routing

Mode→Authority→Capability→Budget→Adapterの順で、実行または明示Not-executedへ収束する。

#### P4-E-WU-004：Action Fault／No-repair Boundary

Unknown／Failure／Timeout／Conflict／Double Execute／Partial ActionをTestし、Repair／Regenerateが自動実行されないことを固定する。

### Phase 4-F — Surface／Evidence

#### P4-F-WU-001：Evidence Event Extension

Binding、Invocation、Evaluation、Recommendation、ActionおよびDegraded MetadataをPhase 3 Evidence Portへ追加する。

#### P4-F-WU-002：Configuration Control

Governance Mode、Profile、BudgetおよびAvailabilityをPreview／Apply CASへ接続する。Default OFF、Local-only。

#### P4-F-WU-003：Status API／UI

Binding／Rule／Result／Action／Cost／Degradedを安全に表示する。Source本文／Path／Secretは出さない。

#### P4-F-WU-004：Public／Basic／v1／v2 Call-0 Regression

Private Control非露出、OFF Call 0、Observe非介入およびExisting API互換をSpy／Integrationで固定する。

### Phase 4-G — Integrated Verification

#### P4-G-WU-001：OFF／OBSERVE／ENFORCE Golden Matrix

Definition 0件、Reference Bundle、Invalid Bundle、Qwen Current Route、Persistent／Ephemeral／RAGを横断検証する。

#### P4-G-WU-002：Security／Performance／Recovery

Path、Digest、Cache、Concurrency、Crash、Evidence Failure、Token／Latency／Call 0、Restartを検証する。

#### P4-G-WU-003：Claude Self-review／COMPLETE_CANDIDATE

Design Conformance、Adversarial Review、Full Test、Static、FrontendおよびAutomation／Compaction Evidenceをまとめ、日本語Handoffを作成して停止する。

### Phase 4-H — Codex／User

#### P4-H-WU-001：Codex Independent Major Review

Claude自己申告を独立再現し、重大Findingだけを返す。

#### P4-H-WU-002：User Mac Acceptance

Qwen OFF／OBSERVE／ENFORCE、UI、Restart、RAG／Persistent互換を手動確認する。

#### P4-H-WU-003：Minimal Closure

必要最小限のCurrent／Roadmap／Recovery、Backup勧告、Git判断およびPhase 5 Gateを扱う。

## 4. Validation Ladder

```text
Per WU       : focused tests only
Per Subphase : focused + adjacent regression + static
Phase 4-G    : backend full + frontend test/typecheck/lint/build + diff/security review
Phase 4-H    : independent reproduction + user manual
```

Full Testを小修正ごとに反復しない。Test数は実Command出力から取得する。

## 5. Stop Conditions

- Root／Authority／Stable／User Data／Git／External境界の変更が必要。
- Phase 5／6責務なしにPhase 4要件を満たせない。
- Existing API／Persistenceの不可逆Migrationが必要。
- Qwen Current RouteがBaselineで起動不能。
- Major Security／Privacy／Recovery Riskをユーザーが受容する必要。

上記以外のRoutineな不具合はClaudeが局所Reworkする。
