# Phase 1-E後 AI実験・統治Platform拡張要件

- 文書ID: `post_phase_1e_research_platform_requirements`
- 状態: `accepted_planning_only`
- 作成日時: `2026-07-19 11:23:04 JST`
- 更新日時: `2026-07-19 11:23:04 JST`
- Snapshot: `20260719112304`
- 作成担当: 設計者役担当Task
- 対象: Phase 1-E完了後のProject全体要件
- 正本言語: 日本語
- 関連: [generic_governance_definition_platform_requirements_20260719112304.md](generic_governance_definition_platform_requirements_20260719112304.md)
- 最新Index: [documentation_index_20260719112304.md](../documentation_index_20260719112304.md)
- supersedes: なし（新規要件系列）

## 1. 文書の位置づけ

本文書は、Phase 1-E完了後に優先度を上げる機能群と、それに伴うProject全体の要件変更を正本化する。

今回の変更は、単なる機能追加ではない。`margpa-runtime-llm`を、単一のLocal LLM推論Runtimeから、次の性格を持つプラットフォームへ拡張する。

> 機能層、統治層、評価、修復、実験、配置環境をそれぞれ交換・観測・有効化・無効化できる、疎結合なAI実験・Runtime Governance Platform。

## 2. 変更後の最上位目標

### 2.1 骨格の優先

- 小型Modelの性能を限界まで追求するより、全機能を差し替え可能にする骨格を先に成立させる。
- 将来、高性能機材、Home Server、Lightning AI Studio、Cloud GPU、別Backendを使う際に、Application Coreを作り直さない。
- Model、Guard、Judge、RAG、Agent、Tool、Repair、Governance Definitionの交換はPortとAdapterを通じて行う。

### 2.2 研究装置としての目標

すべての任意ComponentとそのGovernanceを個別に制御し、次を比較できることを重視する。

- Governanceなし
- Governanceの観測のみ
- Governanceによる介入あり
- Guard、Judge、Repair、Agent等の個別ON／OFF
- 同一Input、Model、Seed、Configでの再現実行
- 品質、Latency、Token、追加Model Call、Repair回数の比較

目標は「疎結合です」という構造上の主張に留まらず、構成差による効果とコストを再現可能に比較できる状態である。

## 3. Scopeの基本単位

### 3.1 Functional Component

Functional Componentは実際の処理を行う。

- Main Model
- Input Processing
- RAG
- Guardrail
- Policy
- Judge
- Repair
- Agent
- Tool
- Memory
- Output Processing
- Audit Storage
- Status Projection

### 3.2 Governance Point

Governance PointはFunctional Componentの前後または必要な境界に置く軽量な実行点である。そのPointに必要なRuleだけを適用する。

### 3.3 Governance Control Plane

定義、Compile、状態、Evidence、Action解決、Auditを共通化する。各Pointに完全なMARGPA一式を複製しない。

### 3.4 Governance Binding

PointとDefinitionをBindingする設定単位とする。Bindingは少なくとも次を持つ。

- 対象Point
- Definition ReferenceまたはCapability Requirement
- Profile
- Mode
- Activation Condition
- Budget
- Priority
- Required／Optional

DefinitionはRuleのSource、Pointは処理経路上の場所、Bindingは接続設定である。JSON 1個を1つの実行層と同一視しない。

## 4. 疎結合と依存性要件

### 4.1 Component制御

- Main Model以外の任意Functional Componentは`enabled`を持つ。
- 各Governance Bindingは`mode = off | observe | enforce`を持つ。
- `off`: 実行せず、Governance由来のToken、Call、Repairを発生させない。
- `observe`: 判定と記録は行うが、出力や処理経路に介入しない。
- `enforce`: 停止、拒否、修復、再生成、制約適用等の登録済みActionを実行できる。
- Main ModelはChat実行時の必須Componentとするが、Main Model Governanceは無効化できる。

### 4.2 階層構造

平坦で曖昧なBoolean群ではなく、少なくとも次の責務分離を持つ。

```toml
[components.guard]
enabled = false

[components.guard.governance]
mode = "off"
```

### 4.3 構成Validation

すべてのComponentとBindingについて、次を表現・検証できること。

- Required Dependency
- Optional Dependency
- Conflict
- Capability Requirement
- Degraded Mode
- Invalid Combination
- Hot Reload可否
- Model Reload必要性
- Application Restart必要性
- Side Effect Level

例：

- `Agent OFF + Agent Governance ON`は通常はInvalidとする。
- `Judge OFF + Repair ON`は、RepairのTrigger SourceがJudge以外にあるかで有効性が変わる。
- 依存不足を黙って無視せず、Error、Warning、Degradedのいずれかとして表示・記録する。

### 4.4 無効化できない外部制約

Application ConfigのON／OFFは、Host OS、System Policy、Developer Policy、外部Service、実在する権限・法令・承認条件を無効化しない。

Tool PermissionをOFFにすることを`allow all`と解釈しない。Permission判定が無い場合は、Toolを無効化するか、安全側に拒否する。

## 5. Governance実行要件

### 5.1 共有Control Planeと分散Point

採用構成は次とする。

```text
Governance Control Plane
  ├─ Definition Registry／Provider
  ├─ Validator／Adapter／Compiler
  ├─ Rule Selection
  ├─ Namespaced Governance State
  ├─ Evidence／Audit
  ├─ Conflict Resolution
  └─ Action Resolver

Execution Pipeline
  ├─ Input Governance Point
  ├─ RAG Governance Point
  ├─ Guardrail Governance Point
  ├─ Agent Governance Point
  ├─ Tool Governance Point
  ├─ Judge Governance Point
  ├─ Main Model Governance Point
  └─ Output／Repair Governance Point
```

### 5.2 実行負荷

- Startup時はMetadataを中心に読み、Definition本体は必要時にLazy Loadする。
- ターンに必要なDefinitionとRuleのみをCompileする。
- 決定論的に判定できる項目はPython側で処理する。
- 意味的判定が必要なときだけSemantic Evaluatorを呼ぶ。
- Definition Hash、Adjustment Hash、Compiler Version、PointをKeyにCompiled PlanをCacheする。
- Model Call、Token、Latency、Repair、RetryにBudgetを設ける。
- Functional Componentが呼ばれない場合、対応Pointも呼ばない。

各層にPointを分散させるだけで軽量になるわけではない。上記のActivation、Selection、Cache、Budgetを必須とする。

### 5.3 StateとAction

- Turn／Session単位のShared Context、PointごとのLocal State Namespace、Append-Only Evidence／Eventを分離する。
- 単一のMutableな巨大Stateに集約しない。
- 複数PointからActionが発火した場合は、中央のAction Resolverで最終解決する。
- 未知ActionはRecommendationとEvidenceに残すだけとし、登録済みAction Adapter、Capability、Authorityがなければ実行しない。
- GovernanceがGovernanceを無限に呼ぶ再帰構造を禁止する。Meta-governanceは将来機能とし、原則OFFまたは非同期、最大Depth 1とする。

## 6. Experiment Runtime要件

### 6.1 Profile

少なくとも次の比較Profileを作成可能にする。

```text
baseline_no_governance
baseline_empty_governance
main_governance_observe
main_governance_enforce
guard_judge_repair
all_implemented_layers
```

### 6.2 Run Record

一回の実験実行に次を関連づけて保存する。

- `experiment_id`
- `run_id`
- Model ID／Artifact Digest／Quantization／Backend
- Definition／Package／Adjustment／Compiled Plan Digest
- Effective Config Snapshot／Hash／Source
- Enabled Component／Governance Mode
- Seed
- Input／Output
- Token Count／Latency／Stop Reason
- Audit Result／Score／Deviation／Severity
- Repair Count／Retry Count
- Runtime Status／Warning／Error

## 7. Runtime Status／Observability要件

Status ReportingはGuardrail等の前に直列で挿入する層ではなく、Eventを購読する横断的なProjectionとする。

- 各Componentは共通Runtime Event Contractに従う。
- CLI、Web UI、Audit Log、Experiment Recordが同じEventを利用できる。
- Reporting／Projectionの障害でInference本体を失敗させない。
- 必須Lifecycle Stateと、表示／永続化するReportingを分離する。
- DAGD内部のGovernance Status Reporterと、全RuntimeのStatus Projectionを区別する。

表示候補：

```text
idle
preparing
governance_precheck
guarding
generating
judging
repairing
agent_running
completed
cancelled
failed
```

加えて、Current Component、Governance State、Attempt、Warning、Elapsed Timeを表示可能にする。

## 8. UI／Configuration要件

### 8.1 一般向けの基本UI

一般利用者が触る可能性を考慮し、表側は次を中心にする。

- New Chat
- Chat History／Resume
- Main Model
- Response Language
- Generate／Stop／Regenerate
- 簡易なCurrent Status

`New Chat`はTOML設定ではなくApplication Actionである。

### 8.2 開発・研究設定

上記以外は、UI上の`開発・研究設定`に集約し、次の見出しで分離する。

- Generation
- Model Runtime
- Component Structure
- Governance
- Evaluation／Repair
- Agent／Tool
- Experiment
- Status／Audit
- Deployment

### 8.3 Typed Config Service

UIからVersion Control対象の`config/application.toml`を直接書き換えない。

```text
UI Input
  ↓
Typed Schema Validation
  ↓
Effective Config Preview
  ↓
Diff／Source／Apply Mode表示
  ↓
Atomic Save
```

- `config/application.toml`はRepository内のDefault正本とする。
- UIはGit対象外のLocal Runtime Override TOMLへ保存する。具体PathはPhase 4で決める。
- 変更前後のDiff、各値のSource、Effective Configを表示する。
- 適用時期をImmediate／Next Request／Model Reload／Application Restartで表示する。
- 将来のReset／Export／Import／Presetに対応できる。
- Governance調整UIは原始Definition JSONを変更せず、Adjustment Overlay／Profileを編集する。

## 9. 外部開発／検証環境要件

### 9.1 採用環境

Phase 2の主要外部開発／検証環境は`Lightning AI Studio`とする。

- 現行Repositoryを通常のLinux開発環境として動かす。
- Linux x86_64／CUDA／llama.cpp用Deployment Profileを追加する。
- SSH、VS Code、永続Storage、GPU、Port公開を使用する。
- 同一Model Port、GGUF、Config Composition、Test Contractを共有する。
- Model ArtifactはGitに含めず、環境ごとに配置しHashを検証する。
- Mac MetalとLightning CUDAの実効Config、Capability、Latency、Token Speed、Outputを比較できる。

### 9.2 ZeroGPU

Hugging Face ZeroGPUは直近のMVP実行基盤には採用しない。Phase 10の次の用途に延期する。

- 公開Demo
- PyTorch／Transformers Backend交換性の実証
- Gradio Adapterの追加
- GGUF／llama.cppとは別系統のDeployment Adapter検証

## 10. 将来のFunctional LayerとGovernance Hook

次のFunctional Layerは段階的に追加する。各Layerの実装時に、Governance PointとBinding Hookも用意する。ただし、実装前のLayerの完全なGovernance処理を先行実装しない。

| Functional Layer | Governance例 | 主な関心事 |
|---|---|---|
| Main Model | Main Governance | Premise、Context、Scope、Generation Constraint |
| Guardrail | Guard Governance | Injection、Jailbreak、Secret、Policy |
| Judge | Judge Governance | Evaluation Criteria、Independence、Confidence、Conflict |
| Repair | Repair Governance | Trigger、Budget、Success Criteria、Loop Prevention |
| Agent | Agent Governance | Plan、Step、State、Handoff、Completion |
| Tool | Tool Governance | Permission、Scope、Side Effect、Approval |
| RAG | RAG／Data Governance | Source、Chunk、Evidence、Injection、Leakage |
| Policy | Policy Governance | Applicable Policy、Priority、Exception、Record |

## 11. Non-functional Requirements

### 11.1 交換性

- Definition名、Model名、OS名、GPU種別をDomain Coreにハードコードしない。
- Adapter、Provider、Registry、CapabilityとTyped Contractで解決する。

### 11.2 再現性

- Artifact、Definition、Config、Compiler、Profile、Seed、EnvironmentのIdentityとHashを記録する。
- 実効値とSourceを記録する。

### 11.3 障害分離

- Status Projection、Audit Sink、非必須Governance Providerの障害でMain Inferenceを必ず失敗させない。
- Fail Open／Fail ClosedはComponent、Mode、Required Flag、Side Effectで明示的に決める。

### 11.4 セキュリティ

- Definition JSONを実行Codeとして扱わない。
- Tool／Agent／外部I/Oの実行は、Modelの推奨だけで行わない。
- 既存の権限、Policy、承認条件に対する解釈と、権限の生成を区別する。

## 12. Scope外・延期

- Phase 1-E完了前の大規模なGovernance Platform実装
- Phase 3での16 GD全実装・全同時実行
- CDOGDを必須とする自動Routing
- ZeroGPUの即時対応
- 生のChain of Thoughtの保存・公開
- JSONからの任意Code実行
- Application ConfigからのSystem／Host／外部Policy無効化

## 13. Acceptance Criteria

### Phase 2受入基準

- Component RegistryがON／OFF、Dependency、Conflict、Capabilityを表現できる。
- Governance Modeの`off／observe／enforce`を型として表現できる。
- Experiment ProfileとRun RecordによりBaselineと構成差を比較できる。
- Event ContractとStatus ProjectionがInferenceと疎結合である。
- Mac MetalとLightning Linux／CUDAで共通Contract Testを実行できる。

### Phase 3受入基準

- Governance Definitionが0個でもMain Model Runtimeが完全に動作する。
- 任意のDefinition PackageをCore改修なしで登録・Bindingできる。
- Source JSONを変更せず、Adapter／IR／Compiler／Adjustmentで実行Planを生成できる。
- Main Governanceで`off／observe／enforce`を比較できる。
- Definitionなしの`enforce`を成功扱いしない。

## 14. Authorization Boundary

本文書は要件のAccepted Snapshotである。今回のユーザー指示はDocs作成の許可であり、Phase 2以降のSource、Config、Test、Dependency、外部環境を実装・変更する許可ではない。
