# MARGPA Runtime Governance 仕様書

```yaml
document_id: runtime_governance_specification
status: current_planned_not_implemented
language: ja
created_at: 2026-07-26 15:16:24 JST
updated_at: 2026-07-26 15:16:24 JST
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

