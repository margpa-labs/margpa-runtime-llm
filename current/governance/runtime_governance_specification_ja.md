# MARGPA Runtime Governance 仕様書

```yaml
document_id: runtime_governance_specification
status: current_planned_not_implemented
language: ja
created_at: 2026-07-26 15:16:24 JST
updated_at: 2026-07-27 10:01:20 JST
owner: Nazuna Research
active_phase: phase_1_ex
rag_default: true
```

## 1. Purpose

ARGD／DAGDを巨大なSystem Promptとして貼るのではなく、Model直外のInference Control Planeで入力、Context、Generation、出力、評価、修復、状態および証跡を統治する。

Model内部のWeight、Attention、Hidden StateまたはInternal Activationへ直接介入しない。

## 2. Definition Independence

```text
definitions = 0
  → Main Model Runtimeは完全動作

definitions = 1..N
  → 明示Provider／Adapter／Compiler／Binding経由で追加
```

- ARGD／DAGDを含む固有略称をCore Enumにしない。
- 未知のDefinition名、Schema、VersionおよびCustom Providerを許容する。
- JSONが存在するだけでGovernanceとして実行しない。
- Malformed、Unsupported、AmbiguousをEmpty扱いしない。
- Definition原本を黙って補完または修正しない。

## 3. Platform

```text
Governance Definition Provider
  ↓
Package／Definition Registry
  ↓
Schema Adapter／Normalizer
  ↓
Normalized Governance IR
  ↓
Compiler
  ↓
Compiled Plan
  ↓
Governance Point
  ↓
Standard Governance Result
```

ProviderはFilesystem、Empty、Remote等のSource差を隠蔽する。AdapterはSchema差を吸収し、CompilerはBindingとRuntime Capabilityに必要なRuleだけを選択する。

## 4. Shared Control Plane

- Definition／Package Registry
- Activation／Rule Selection
- Compiled Plan Cache
- Shared Turn／Session Context
- Point-local State Namespace
- Evidence／Audit
- Evaluator Port／Budget
- Conflict／Action Resolver
- Status Event Publisher

各機能Layerには軽量なGovernance Pointだけを配置する。

## 5. Governance Point

```text
input.pre／post
rag.pre／post
guardrail.pre／post
policy.pre／post
agent.pre／post
tool.pre／post
judge.pre／post
main_model.pre／stream／post
repair.pre／post
output.pre／post
```

Point IDは拡張可能Stringであり、固定列挙だけに閉じない。

## 6. Execution Mode

### off

- Rule Selection、Semantic Call、Interventionを行わない。
- 最小Statusだけを返す。

### observe

- 判定、Score、Deviation、Recommendation、Costを記録する。
- Functional ComponentのInput／Outputを変更しない。

### enforce

- Compile済みRuleと登録済みAction Adapterの範囲だけで介入する。
- Capability、AuthorityまたはDependency不足を成功扱いしない。

## 7. ARGD／DAGD

初期参照Definition：

```text
ARGD: Axiomatic Reasoning Governance Definition v0.3.1
DAGD: Declarative AI Governance Definition v0.4.4
DAGD State: EXPERIMENTAL
License: CC-BY-SA-4.0
```

ARGDはPremise、Context、矛盾、情報不足、推論品質、表現およびRepairを扱う。DAGDはConstraint、Capability、Evaluation、Severity、State、Audit-to-ActionおよびStatusを扱う。

69KB全体を毎Turn投入せず、必要部分だけCompileする。決定論的State／Action判定はPython側を優先し、意味評価だけModelへ渡す。

## 8. Standard Result

```text
execution_state
repository_state
selected_definitions
selected_rules
observations
deviations
dimension_scores
severity
recommended_actions
executed_actions
warnings
errors
evidence_refs
state_patch
cost
```

Fact、Observation、Inference、Assumption、EvaluationおよびActionを混同しない。

## 9. Action／Authority

- DefinitionはActionを推奨できるが、外部権限を生成しない。
- Tool Permission、Human Approval、System PolicyおよびRuntime Policyを越えない。
- 未知Actionは実行せずRecommendationとして記録する。
- 複数ActionはAuthority、Scope、Severity、PointおよびConflict Policyで解決する。
- 単純な固定優先順位だけで全Conflictを処理しない。

## 10. Repair

```text
Detect
  ↓
Classify／Severity
  ↓
Recommended Repair
  ↓ Authority／Budget
  ↓
Repair／Regenerate／Rebind
  ↓
Success Evaluation
```

Max Attempt、Max Time、Max Token、Max Total CallおよびSuccess Criterionを必須とする。無限RepairとMeta-governance再帰を禁止する。

## 11. Audit／Status

- Definition ID／Version／Digest
- Compiler／Plan／Binding Digest
- Point／Mode／Profile
- Applied Rule
- Evaluator Result
- Recommended／Executed Action
- State Before／After
- Latency／Token／Call Count
- Repair Count

Status ReportingはEvent Subscriberとし、失敗しても推論実行を壊さない。

## 12. External R&D Port

```text
Generic External Governance Provider Port:
  EASA
  DLAGSA

Generic Evidence Ledger Port:
  OCILNS
```

固有名称によるRoutingをCoreへ実装しない。Manifest／Capability／Bindingで接続し、Default OFF、Failure Isolation、OFF時Zero Side Effectを守る。

## 13. Current State

```text
Phase 1:
  Model／Config／Platform Runtimeのみ実装

Phase 1-ex:
  Documentation／Publication／Git準備

Governance Platform:
  Accepted Design／Not Implemented
```

## 14. Known Open Issues

- DAGD State名の正規化
- Dimension ScoreとWeight
- Critical Action条件
- Expression Precision Action
- 複数Action Conflict
- Context Overflowと無断要約禁止
- Semantic Judgeの信頼性
- Repair成功判定
- Streaming監査
- Guardrail／Policy／Governanceの優先関係

## 15. Traceability

- [Governance Compilation](../../phases/phase_1/governance/phase_1_governance_ja.md)
- [Architecture Compilation](../../phases/phase_1/architecture/phase_1_architecture_ja.md)
- [Requirements](../requirements/requirements_specification_ja.md)

## 16. Scope／Non-scope

### 16.1 Scope

Runtime Governance Layerは、Modelのすぐ外側にあるInference Control Planeを所有する。

- Input／Premise検査
- Context選択／優先関係
- Prompt／Message構築
- Generation Config制御
- Decoding Capability選択
- Streaming監視
- Output監査
- Deviation／Severity判定
- Repair／Regenerate／Rebind／Enforce
- Governance State更新
- Audit／Evidence／Status

### 16.2 Non-scope

- Model Weightの直接変更
- Attention／Hidden State／Internal Activationへの直接介入
- 存在しないSystem Policyの生成
- 外部に存在しない権限の生成
- Human Approvalの代替
- Tool PermissionのModel単独決定
- Raw Chain of Thoughtの永続保存
- すべての安全性または正確性の保証

## 17. Governance Definition Package

### 17.1 Package Contract

```text
package_id
package_version
package_digest
publisher
license
definitions[]
schemas[]
resources[]
dependencies[]
signatures[]
```

### 17.2 Definition Contract

```text
definition_id
definition_version
definition_digest
display_name
domain
schema_id
source_format
activation_condition
required_capabilities
input_scope
output_scope
priority
dependencies
conflicts
bindings
rules
evaluation
actions
state_schema
evidence_schema
```

Definition IDは任意Stringであり、ARGD、DAGD、AISGD等の既知略称だけに制限しない。Domainも固定Enumだけに閉じない。

### 17.3 Empty Baseline

```text
Provider configured     : 0..N
Package loaded          : 0..N
Definition validated    : 0..N
Definition activated    : 0..N
Governance Point bound  : 0..N
```

すべて0でもMain Model Runtime、CLIおよびWebは正常動作する。

### 17.4 Unknown Definition

未知Definitionを受けた場合：

1. Sourceを取得する。
2. Size／Digest／Media Typeを記録する。
3. Schemaを特定する。
4. 対応Adapterを明示検索する。
5. Adapter不在なら`unsupported_definition`とする。
6. 原本を変更しない。
7. Empty Definitionへ黙って変換しない。
8. 実行せずRepository StateとReasonを返す。

単なるJSON、空JSON、無関係なJSON、破損JSONおよび悪意あるPayloadを「Governanceらしい」と推測して実行しない。

## 18. Provider／Repository State

Definition Sourceは次のStateを区別する。

```text
not_configured
unavailable
empty
discovered
loaded
validated
unsupported
invalid
disabled
active
failed
```

`empty`、`unsupported`、`invalid`および`unavailable`を同一扱いしない。

Provider候補：

- Filesystem Provider
- Empty Provider
- Package Provider
- Remote Provider
- Embedded Test Provider
- Future Signed Registry Provider

Remote ProviderはNetwork、Authentication、Cache、TimeoutおよびFailure Policyを明示し、Defaultで必要としない。

## 19. Normalized Governance IR

Schema AdapterはDefinition原本を直接Runtimeへ渡さず、Normalized Governance IRへ変換する。

```text
GovernanceIR
  ├─ identity
  ├─ source_provenance
  ├─ domain
  ├─ activation
  ├─ scopes
  ├─ conditions
  ├─ rules
  ├─ evaluators
  ├─ actions
  ├─ state_model
  ├─ evidence_requirements
  ├─ dependencies
  └─ conflicts
```

Normalizerは次を行わない。

- 欠落Ruleの推測補完
- Ambiguous Actionの自動実行可能化
- Priorityの暗黙付与
- Authorityの生成
- Source Definitionの書換え

正規化時のLoss、Unsupported FieldまたはAmbiguityはWarning／ErrorとしてEvidenceへ残す。

## 20. Compiler

### 20.1 Input

- Normalized Governance IR
- Active Task／Turn Context
- Governance Profile
- Point Binding
- Runtime Capability
- External Policy／Authority State
- Budget

### 20.2 Output

```text
compiled_plan_id
compiler_id
compiler_version
source_definition_digests
profile
selected_rules
selected_evaluators
selected_actions
point_bindings
dependencies
conflicts
budgets
warnings
plan_digest
```

### 20.3 Selection

- Taskに必要なDefinitionだけをLazy Loadする。
- 必要なRuleだけをCompileする。
- Deterministic Ruleを優先する。
- Semantic EvaluationはBudget内で明示的に選択する。
- 無関係なGDをInactiveとする。
- 全GDを毎Turn、全Pointへ投入しない。

### 20.4 Cache

Compiled Planは、Definition Digest、Compiler Version、Profile、Binding、CapabilityおよびPolicy StateをCache Keyに含める。いずれかが変わった場合、古いPlanを黙って再利用しない。

## 21. Governance Profile

### 21.1 Core

- 必須Rule
- Deterministic Validation中心
- 追加Model Call最小
- Critical Boundary優先

### 21.2 Standard

- Core
- 回答後主要監査
- 主要Dimension
- 必要時の軽量Repair

### 21.3 Full

- 回答前後監査
- 詳細Dimension Score
- Severity
- Repair Loop
- Rebind／Enforce／Reinitialize候補
- 詳細Status

Definition内容とExecution負荷を分離する。同じDefinitionでもProfileにより選択Rule、Semantic Call、Repair Budgetを変えられる。

## 22. Governance Point Contract

各Pointは次を受け取る。

```text
point_id
stage
turn_context
component_context
compiled_plan_ref
input_snapshot
runtime_capabilities
authority_state
budget
```

返却：

```text
standard_governance_result
optional_transformed_input
optional_state_patch
status_events
evidence_events
```

Pointは自分に必要なScopeだけを見る。Main Model PointがTool Side Effectを直接承認したり、Judge PointがConversation Storageを直接変更したりしない。

### 22.1 Main Model Point

- Premise
- Context
- Scope
- Generation Constraint
- Thinking Control
- Output Protocol

### 22.2 Guardrail Point

- Prompt Injection
- Jailbreak
- Secret／PII
- Prohibited Content
- Policy Avoidance
- Tool Abuse

### 22.3 Agent／Tool Point

- Plan Scope
- Tool Permission
- Side Effect
- Approval
- Budget
- Completion
- Handoff

### 22.4 Judge Point

- Evaluation Criteria
- Judge Independence
- Evidence Scope
- Confidence
- Conflict
- Retry Limit

### 22.5 RAG Point

- Document Authorization
- Source Integrity
- Retrieval Scope
- Prompt Injection in Source
- Citation Coverage
- Context Budget

## 23. Mode Semantics

### 23.1 Functional Component OFF／Governance OFF

Componentも専用Pointも実行しない。最小構成Baselineである。

### 23.2 Functional Component ON／Governance OFF

Component本体だけを実行する。Governance効果比較用Baselineとして許可できるが、Security Critical ComponentではProfileにより拒否できる。

### 23.3 Functional Component ON／Governance Observe

判定、Score、Deviation、Recommendation、CostおよびEvidenceを記録するが、Component Input／Outputを変更しない。

### 23.4 Functional Component ON／Governance Enforce

登録済みAction AdapterとAuthority範囲内で停止、変換、RepairまたはEscalationを実行する。

### 23.5 Functional Component OFF／Governance ON

原則InvalidまたはNo-opである。Preflight Governance等、Componentなしでも意味を持つ明示Use Caseだけ例外とし、Schemaで宣言する。

## 24. ARGD詳細

```text
ARGD
Axiomatic Reasoning Governance Definition
Version 0.3.1
```

主な6領域：

1. Input Interpretation／Premise
2. Context Priority
3. Contradiction／Information Insufficiency
4. Reasoning Quality
5. Structural Expression
6. Efficiency／Repair

主なRule：

- 入力構造保持
- 前提固定
- 決定事項固定
- 無断要約禁止
- Context混在防止
- 矛盾未解決時停止
- 情報不足を推測で埋めない。
- 複数仮説保持
- Fact／Observation／Inference／Assumption／Evaluation分離
- Sycophancy防止
- Refutation／Alternative Hypothesis
- Drift検出
- Repair／Re-fix

Tag：

```text
KEEP
FIXD
ANTI
FALS
LEAD
TONE
REPR
```

ARGDはPrompt断片、Deterministic Rule、Semantic EvaluationおよびRepair Policyへ分割Compileする。

## 25. DAGD詳細

```text
DAGD
Declarative AI Governance Definition
Version 0.4.4
State EXPERIMENTAL
```

構造：

- Policy Goal
- Constraints
- Capabilities
- Evaluation
- Severity
- Audit Log Schema
- Repair
- Activation
- Self Audit
- Audit-to-Action
- Status Reporting

Operation候補：

```text
activate
run
rebind
enforce
reinitialize
full_dagd_reinjection
user_requested_re_fix
audit_failure_reactivation
```

Score／State候補：

- 0～100
- Stable
- Acceptable with Minor Drift
- Degraded
- Unstable
- Low／Moderate／High／Critical

Dimension候補：

- Context Preservation
- Premise Preservation
- Scope Definition
- Reasoning Integrity
- Expression Precision
- Dialog Efficiency
- Self Repair

DAGD State名、Critical ConditionおよびAction Resolutionには原Definition内の整合課題があるため、Compiler／Adapterで明示Validationし、原本を黙って直さない。

## 26. Governance Definition Catalog

次は将来候補であり、2026年7月27日時点では実装・有効化していない。

### 26.1 CDOGD

```text
Cross-Domain Orchestration Governance Definition
```

複数GDの選択、範囲、重複、引渡し、抑制、弱化、修復伝播およびConflictを扱う。

### 26.2 SPPGD

```text
Strategic Planning and Prioritization Governance Definition
```

目的、前提、制約、選択肢、非選択肢、優先順位、配分、順序、継続、停止、撤退、保留および再評価条件を扱う。

### 26.3 DAAGD

```text
Decision Authority and Accountability Governance Definition
```

既存Policy、Tool権限、外部実行権限、委任、承認条件および責任分界に基づき、Authority／Accountability Stateを解釈する。外部に存在しない権限を生成しない。

### 26.4 SDAGD

```text
Strategic Decision Audit Governance Definition
```

SPPGDの判断構造とDAAGDのAuthority／Accountability Stateを監査する。戦略判断または権限判断を代替しない。

### 26.5 SDMRGD

```text
Strategic Decision Meta-Review Governance Definition
```

SDAGDの範囲、根拠、分類、形式的通過、過剰／過少監査および修復必要性をMeta Reviewする。

### 26.6 DSGD

```text
Data Science Governance Definition
```

分析目的、範囲、Data、出所、品質、仮説、手法、Metric、Leakage、Bias、統計妥当性および分析主張を扱う。

### 26.7 ACRGD

```text
Artifact Composition and Review Governance Definition
```

成果物の目的、読者、構成、形式、配置、開示範囲、改訂履歴および公開／提出可能性を扱う。

### 26.8 AAGD

```text
Agentic AI Governance Definition
```

目的、Scope、Plan、Procedure、Tool Call、Side Effect、State、Handoff、MemoryおよびCompletionを扱う。実行許可を生成しない。

### 26.9 AISGD

```text
AI Security Governance Definition
```

Prompt Injection、Jailbreak、Instruction Leakage、Secret、PII、Tool Abuse、Authority Confusion、Policy AvoidanceおよびAgent間攻撃を扱う。

### 26.10 MPGD

```text
Model Policy Governance Definition
```

Policy／Clause識別、適用範囲、Priority、Conflict、Exception、Over-refusal、Under-refusal、Re-evaluation、RepairおよびDecision Historyを扱う。存在しないPolicyを生成しない。

### 26.11 DCAGD

```text
Development Consulting AI Governance Definition
```

Requirement、Technology Option、Design／Implementation Policy、Feasibility、Difficulty、Effort、Risk、MaintainabilityおよびExtensibilityを扱う。

### 26.12 PMOGD

```text
Project Management and Orchestration Governance Definition
```

Task、Owner、Deadline、Dependency、Blocker、Handoff、Agreement、Open IssueおよびDeliverabilityを扱う。

### 26.13 AIRGD

```text
AI Research Governance Definition
```

Research Question、Prior Work、Novelty Claim、Hypothesis、Falsification、Research Design、Evidence、Execution History、Result／Claim分離、LimitationおよびReproductionを扱う。

### 26.14 AIAGD

```text
AI Architecture Governance Definition
```

System Goal、Requirement、Quality Attribute、Component Responsibility、Connection、Information Flow、Trust／Authority BoundaryおよびRuntime Consistency Claimを扱う。

### 26.15 SEGD

```text
Software Engineering Governance Definition
```

Requirement、Acceptance、Specification、Design／Implementation Trace、Repository、Source／Config／Dependency Change、Verification、Build、Deployment Readiness、RollbackおよびImplementation Historyを扱う。

### 26.16 OMRGD

```text
Operations, Maintenance, and Reliability Governance Definition
```

Service Health、Monitoring、Log、Metric、Alert、Incident、Failure、Degradation、Outage、Runbook、Rollback、Recovery、Maintenance、Risk、Change Impact、Recurrence PreventionおよびContinuous Improvementを扱う。

## 27. Standard Governance Result詳細

```text
result_schema_version
result_id
turn_id
point_id
stage
mode
execution_state
repository_state
selected_definition_refs
selected_rule_refs
facts
observations
inferences
assumptions
evaluations
deviations
dimension_scores
total_score
severity
affected_segments
recommended_actions
executed_actions
warnings
errors
evidence_refs
state_patch
cost
latency
token_usage
call_count
```

`recommended_actions`と`executed_actions`を必ず分ける。Action未実行理由として、Mode、Capability、Authority、Budget、ConflictまたはFailureを記録する。

## 28. Score／Severity

Score計算はDefinitionまたはProfileにより異なり得るため、Coreで固定公式をHard-codeしない。

最低限記録：

```text
dimension_id
raw_value
normalized_value
weight
evidence_refs
evaluator
confidence
aggregation_method
```

Total ScoreだけでCritical Violationを隠さない。Critical Boundaryは独立Flag／SeverityとしてAction Resolutionへ渡す。

## 29. Semantic Evaluator

意味評価用ModelはMain Modelと同じ場合も別Judgeの場合もある。

必要Field：

- evaluator_id
- model_id／artifact_digest
- prompt／criteria_digest
- seed
- generation_config
- evidence_scope
- output_schema
- confidence
- latency／token／cost

Model Self Auditは補助Evidenceであり、単独で最終Authorityとしない。EvaluatorなしのDeterministic Baselineを常に比較可能にする。

## 30. Conflict Resolution

Conflictは次の軸で解決する。

1. External System／Developer／Runtime Authority
2. Applicable Policy Scope
3. Point／Stage
4. Safety Criticality
5. Definition Dependency
6. Explicit Conflict Rule
7. Evidence Quality
8. Budget／Capability

固定Priority NumberだけでAuthority Conflictを処理しない。解決不能時はStop、Degraded、Human ApprovalまたはRecommendation-onlyへ戻す。

## 31. Action Adapter

Actionは登録済みAdapterだけが実行する。

```text
action_id
adapter_id
required_authority
required_capabilities
allowed_points
allowed_modes
input_schema
output_schema
side_effect_class
approval_requirement
rollback
evidence_fields
```

候補：

- warn
- stop
- reject
- redact
- constrain_generation
- regenerate
- repair
- rebind
- enforce
- reinitialize
- request_human_approval
- recommend_only

未知Action、Side Effect不明ActionまたはRollback不能Actionを自動実行しない。

## 32. Governance State Machine

StateはPoint-local NamespaceとShared Turn／Session Stateを分離する。

```text
inactive
activating
active
observing
enforcing
repairing
degraded
failed
completed
```

Definition固有StateはNamespace内に保持し、Core共通Stateと混同しない。

DAGDの`rebinding_then_active`等、主要State一覧と整合しない名称はAdapter Validation対象とし、暗黙に`active`へ変換しない。

## 33. Audit／Evidence

### 33.1 Definition Evidence

- Original Source Path／URI
- Content Type
- Size
- SHA-512
- Package／Definition ID
- Version
- License
- Adapter／Compiler
- Normalization Warning

### 33.2 Execution Evidence

- Turn／Point／Stage
- Mode／Profile
- Input／Output Snapshot Ref
- Selected Rule
- Evaluator
- Score／Severity
- Recommendation
- Execution
- State Before／After
- Repair Attempt
- Budget Consumption

### 33.3 Integrity

Canonicalized PayloadへSHA-512を適用する。将来Hash Chain、HMAC、Digital Signature、Append-only Store、WORM、Merkle Tree、External TimestampまたはOCILNSへ接続できる。

## 34. Status Reporting

Status ReportingはExecution Pipelineの直列必須LayerではなくEvent Subscriberとする。

```text
governance_definition_loaded
governance_plan_compiled
governance_point_started
deviation_detected
action_recommended
action_executed
repair_started
repair_completed
governance_degraded
governance_failed
```

Status Subscriberが落ちても推論を壊さない。ただしCritical Audit WriteがFail Closed Profileで必須の場合は、明示Policyに従いTurnを停止できる。

## 35. Guardrail／Policy／Authority分離

```text
Runtime Governance:
  推論品質、前提、文脈、監査、修復

Guardrail:
  安全性、禁止操作、Injection、Secret

Model Policy:
  Policy識別、適用、例外、拒否妥当性

Authority:
  既存権限、委任、承認、責任状態

Tool Permission:
  実行可否の決定論的Policy
```

関連はするが同一Moduleにしない。AISGD、MPGDおよびDAAGDは各Componentへ接続できるが、外部Policy／Authorityを上書きしない。

## 36. External Original R&D Ports

### 36.1 EASA

```text
Exception Aware Safety Architecture
例外認識型安全統治機構
```

Model内部安全傾向、周辺安全制御およびComposite Safety Behaviorを扱う独立R&D候補。Generic External Governance Providerとして接続し、単一物理Layerの存在を断定しない。

### 36.2 DLAGSA

```text
Distributed LEA Agentic Governance & Safety Architecture
分散証跡型例外認識エージェント統治安全機構
```

複数主体間の責任、委譲、例外、改竄耐性付き証跡、全体整合および異常時安全側制御を扱う独立R&D候補。

### 36.3 OCILNS

```text
Open Cognitive Interaction Ledger Network System
認知対話証跡台帳網
```

人、AI、Tool、外部System間の認知対話を検証・参照・継承・監査可能な証跡単位として扱う独立Ledger候補。

### 36.4 Common Boundary

- Default OFF
- 個別ON／OFF
- ProviderなしでCore動作
- OFF時Zero Side Effect
- Generic Manifest／Capability／Binding
- Failure Isolation
- Authority非上書き
- 固有名称Hard-code禁止

## 37. Security Requirements

- Definition File Size上限
- JSON Depth／Collection Size上限
- Path Traversal拒否
- Remote Fetch Default OFF
- Schema Validation
- Signature／Trust Metadata Hook
- Prompt Injectionを含むDefinition Textの非実行
- Template Variable Allowlist
- Action Adapter Allowlist
- Secret非挿入
- Tool Permission別管理
- Audit Log Redaction
- Resource Budget
- Recursive Governance上限

Definitionを信頼済みSystem Promptと同一視しない。

## 38. Performance Requirements

- Lazy Load
- Selective Compile
- Plan Cache
- Deterministic First
- Semantic Call Budget
- Point-local Rule Selection
- Bounded Repair
- Bounded Recursion
- Context Budget
- Audit Write Budget

複数GDを追加しても、全Definition全文を毎Turn Modelへ送らない。Runtime CostをDefinition数ではなく実際に選択したRule／Evaluator／Action単位で測定する。

## 39. Current Implementation Boundary

2026年7月27日時点：

```text
Implemented:
  Model／Config／Platform Runtime
  Capability／Runtime Observation
  Thinking Protocol／Presentation
  Web／Summary／Basic Preview

Repository Prepared:
  Lightning Auto-start Stage A／B

Documented／Designed:
  Generic Governance Platform
  Main Governance
  Distributed Governance Points
  Definition 0件／Unknown Definition
  Standard Result
  Profiles
  External R&D Ports

Not Implemented:
  Definition Loader／Registry
  Schema Adapter／IR
  Compiler
  Governance Point Runtime
  Evaluator
  Action Resolver
  Governance State Store
  Audit Writer
  ARGD／DAGD Activation
  AISGD／AAGD／MPGD／DAAGD／CDOGD等
  EASA／DLAGSA／OCILNS
```

設計文書に存在することを実装済みとみなさない。

## 40. Implementation Order

1. Definition Provider Port
2. Empty Provider
3. Generic Package／Definition Repository State
4. Source Digest／Size／Schema Validation
5. Normalized IR
6. Compiler Interface
7. Core Profile
8. Main Model pre／post Point
9. Standard Governance Result
10. Deterministic Rule Evaluator
11. Evidence／Status
12. ARGD／DAGD Adapter
13. Semantic Evaluator Port
14. Bounded Repair
15. Guardrail／Judge／Agent等の分散Point
16. Multi-GD／CDOGD

各段階でDefinition 0件BaselineとGovernance OFF Baselineを維持する。
