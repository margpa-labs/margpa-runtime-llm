# 汎用Governance Definition Platform要件

- 文書ID: `generic_governance_definition_platform_requirements`
- 状態: `accepted_planning_only`
- 作成日時: `2026-07-19 11:23:04 JST`
- 更新日時: `2026-07-19 11:23:04 JST`
- Snapshot: `20260719112304`
- 作成担当: 設計者役担当Task
- 対象: Phase 3 Generic Governance Definition Platform
- 正本言語: 日本語
- 上位要件: [post_phase_1e_research_platform_requirements_20260719112304.md](post_phase_1e_research_platform_requirements_20260719112304.md)
- 関連Catalog: [governance_definition_catalog_20260719112304.md](../governance/governance_definition_catalog_20260719112304.md)
- 最新Index: [documentation_index_20260719112304.md](../documentation_index_20260719112304.md)
- supersedes: なし（新規要件系列）

## 1. 最重要原則

Governance DefinitionはRuntimeの任意Pluginであり、Boot Dependencyではない。

Runtime Coreは、次のいずれも前提にしない。

- GDの名前
- GDの数
- ARGD／DAGD／CDOGDの存在
- File名やDirectory構造
- JSON Schemaの単一性
- Domain、Category、Point IDの固定一覧
- Definition Repositoryの存在

ARGDとDAGDも例外にしない。JSONが1個もない状態を正式なBaselineとし、Main Model Runtimeが正常に動作することを必須とする。

## 2. 必須の入力状態

少なくとも次の全状態を考慮する。

1. Definition Sourceが未設定
2. Definition Directoryが存在しない
3. Definition Directoryはあるが空
4. ManifestはあるがEntryが0件
5. 0 byte Fileがある
6. `{}`だけのJSONがある
7. 無関係なJSONがある
8. 日本語名または任意名のJSONがある
9. 未知SchemaのJSONがある
10. Manifestが指すAdapterがない
11. 複数Versionの同一Definition IDがある
12. Duplicate Identityがある
13. Dependency不足、Conflict、Hash不一致がある
14. ARGD／DAGDの複合Source JSONがある
15. 標準Envelopeを持つCustom Definitionがある
16. Custom SchemaとTrusted Adapterの組み合わせがある

どの状態も、理由のないProcess Crash、暗黙のEnforcement、名前からの自動解釈を起こさない。

## 3. Empty Baseline

### 3.1 Default

```toml
[governance]
enabled = false
definition_sources = []

[components.main_model.governance]
mode = "off"
```

### 3.2 動作

Definition 0件、Governance OFFで次が正常に動作する。

- Model Load／Unload
- Generate
- Streaming
- Cancel
- Response Language
- Generation Config
- CLI／将来のAPI

この場合、Governance由来の負荷は次とする。

```text
Definition Load        : 0
Governance Model Call  : 0
Governance Prompt      : 0
Governance Token       : 0
Governance Repair      : 0
```

Statusは次の意味を明示できる。

```text
governance_state : governance_disabled
definitions      : 0
```

## 4. Repository State

Repository全体の状態は、少なくとも次を区別する。

| State | 意味 |
|---|---|
| `unconfigured` | Sourceが設定されていない |
| `empty` | 有効なDefinition Entryが0件 |
| `ready` | 1件以上の利用可能Definitionがある |
| `degraded` | 一部にInvalid／Unsupported／Conflictがあるが、利用可能な部分がある |
| `error` | Source自体が読めない、またはRequired条件を満たせない |

判定原則：

- 任意Directoryがない場合は`unconfigured`または`empty`であり、それだけでFatal Errorとしない。
- 空Directoryは`empty`とする。
- Malformed JSONは`empty`ではなく`degraded／invalid_json`とする。
- Permission等で設定済みSourceにAccessできない場合は`error`とする。

## 5. ModeとDefinition 0件の組み合わせ

| Mode | Definition 0件時の必須動作 |
|---|---|
| `off` | Pass-throughで正常動作する |
| `observe` | `inactive_no_definitions`とWarningを記録する。BindingがRequiredならError |
| `enforce` | Required Governance Missingとして安全側に拒否／Error。Enforce成功と記録しない |

Modeが`enforce`であるだけで、Definitionの存在、Compile成功、Rule適用、Action実行を假定しない。

## 6. 汎用Contract要件

特定GDごとのLoader／ClassをCoreに追加する方式を禁止する。次の汎用Conceptを用いる。

- `GovernanceDefinitionProvider` Port
- `EmptyDefinitionProvider`
- `FilesystemDefinitionProvider`
- `GovernanceDefinitionRegistry`
- `GovernancePackageManifest`
- `GovernanceDefinitionDescriptor`
- `GovernanceDefinitionAdapterRegistry`
- `GovernanceDefinitionCompiler` Port
- `NormalizedGovernanceIR`
- `CompiledGovernancePlan`
- `GovernanceBinding`
- `GovernancePoint`
- `GovernanceRepositoryState`
- `GovernanceExecutionResult`

`EmptyDefinitionProvider`はTest Dummyではなく、0件Baselineを表現する正式なProduction Implementationとする。

## 7. SchemaとAdapter

任意JSONは、存在するだけでGovernanceとして解釈できない。次のPipelineを必須とする。

```text
Raw JSON
  ↓ Definition Adapter
Standard Descriptor
  ↓ Normalization
Normalized Governance IR
  ↓ Compiler
Compiled Governance Plan
```

初期Adapter候補：

1. Legacy ARGD／DAGD Adapter
2. Standard GD Adapter
3. Generic Declarative Rule Adapter
4. 将来のTrusted Custom Adapter

Custom Adapterは実行Codeであり、JSONとは別のTrusted Pluginとして登録する。JSONがCode、Module Import、Shell Command、Network Fetchを指示することは認めない。

## 8. Discovery要件

### 8.1 Manifest First

Package Manifestによる明示登録を推奨する。

Manifestは最低限、次を持つ。

- Package ID／Version
- Definition ID／Version
- Relative Path
- Expected Digest
- Schema ID
- Adapter ID
- Required／Optional Dependency

### 8.2 Content Discovery

標準Envelopeを持つJSONに限り、Content-based Discoveryを将来許容できる。

### 8.3 禁止事項

- File名の`aisgd`を見てSecurityと決めない。
- File名の`cdogd`を見てOrchestratorと決めない。
- Directory名の`ordinary`、`orchestration`をRuntime Semanticsにしない。
- 名前や作者推奨PathをCapabilityの根拠にしない。

明示Binding、Descriptor、Capabilityが正本である。

## 9. Package Layout

次は推奨例であり、Runtime Contractではない。

```text
definitions/
  packages/
    margpa_foundational/
      manifest.toml
      argd_v0.3.1_en_dagd_v0.4.4_en.json
    nazuna-research_domain_extensions/
      manifest.toml
      definitions/...
    custom/
      manifest.toml
      definitions/...
```

`definitions/`全体が空、`packages/`がない、Custom ProviderがFilesystemを使わない、という構成も有効とする。

## 10. Standard Descriptor

Descriptorは次の情報を表現できる。

- Provider ID
- Package ID／Version
- Namespace
- Definition ID／Version／Digest
- Schema ID／Adapter ID
- Display Name
- Domain Tag
- Capability
- Dependency／Conflict
- Recommended Point
- License／Author
- Validation State
- Activation Metadata

Domain Tag、Capability、Point IDは拡張可能なStringとし、Core内のClosed Enumで全世界を固定しない。

## 11. Definition State

個別Definitionに少なくとも次の状態を持てること。

```text
available
active
inactive
disabled
missing
empty
invalid_json
invalid_schema
unsupported_schema
adapter_missing
hash_mismatch
duplicate_identity
dependency_missing
conflict
incompatible
quarantined
```

- Manifestに記載されない無関係JSON、または標準EnvelopeのないJSONは無視できる。
- Manifestで明示登録されたがSchemaまたはAdapterを理解できない場合は、黙って読み替えず`quarantined／unsupported_schema／adapter_missing`とする。
- Invalidな1件が任意Package全体やMain Model Runtimeを無条件にCrashさせない。

## 12. Security制約

- JSONをDataとしてのみ扱う。
- Code Execution、Shell、Dynamic Import、自動URL Downloadを禁止する。
- Configured Root外へのPath Traversalを禁止する。
- File Size、Nesting Depth、Rule Count、Prompt Size、Compiled Plan Sizeに上限を設ける。
- Digestを検証し、Duplicate Identityは明示的に拒否する。
- Unknown Actionは実行しない。
- Adapter PluginはJSON Packageより高いTrustと明示的なInstall／Registrationを必要とする。

## 13. CDOGDとOrchestration

- CDOGDは任意Definitionの1つであり、Coreの必須Dependencyではない。
- CDOGDがなくてもManual Binding、Static Routing、User-selected Profileは動作する。
- Dynamic Routingは、Orchestration Capabilityを持つActive Definitionが存在する場合にのみ有効化できる。
- CDOGD以外のCustom Definitionが同等のCapabilityを申告する場合、交換可能である。
- CDOGDという名前だけでDynamic Routing Capabilityを付与しない。
- Dynamic Routing自体はPhase 9まで延期する。

## 14. ARGD／DAGDの扱い

- 現在の参照SourceはARGD v0.3.1とDAGD v0.4.4をTop Levelの`argd`と`dagd`に持つ複合JSONである。
- SourceはByte-for-byteで保存し、SHA系DigestとLicense／Author／Versionを記録する。
- Runtime上ではLegacy Adapterが2つのStandard Descriptorへ展開できる。
- 正式に分離されたSourceがない限り、利便性のために原本JSONを独自分割しない。
- `margpa_foundational`等のPackageはDefault提供候補ではあるが、Coreに必須ではない。
- ARGD／DAGDの名前をCore Class、Required Profile、Fixed Pointにハードコードしない。

## 15. Source不変・Adjustment要件

Definition Source JSONをRuntime調整のために書き換えない。

```text
Immutable Definition Source
  + Package Manifest
  + Runtime Adjustment Profile
  + Binding
  + Compiler Version
  ↓
Compiled Governance Plan
```

Adjustment Profileは次を持てる。

- Activation
- Include／Exclude Rule
- Priority
- Soft Weight
- Threshold／Severity
- Mode
- Semantic Evaluator Selection
- Model Call／Token／Latency／Repair Budget
- Action Mapping
- Status Verbosity

Ruleは少なくとも次に分類する。

| Rule Class | Adjustmentの扱い |
|---|---|
| Hard Constraint | Runtime Profileで無効化・弱化しない |
| Structural Rule | 依存と整合する範囲で選択可 |
| Soft Rule | Weight／Threshold調整可 |
| Advisory Rule | 記録・推奨中心 |

Adjustmentは、存在しないPolicy、Authority、Approval、Capabilityを生成しない。

## 16. Identity／Audit要件

次を個別にIdentityとDigestで記録する。

- Raw Definition Source
- Package Manifest
- Standard Descriptor
- Adapter ID／Version
- Normalized IR
- Adjustment Profile
- Compiler ID／Version
- Compiled Plan
- Governance Point
- Binding
- Evaluation Result
- Recommended Action
- Executed Action

## 17. Test Matrix

### 17.1 Discovery／Validation

- Missing Directory
- Empty Directory
- Empty Manifest
- 0 byte File
- `{}`
- Unrelated JSON
- Arbitrary／Japanese Filename
- Unknown Schema
- Adapter Missing
- Duplicate Identity
- Same ID with Multiple Versions
- Hash Mismatch
- Dependency Missing
- Conflict

### 17.2 Compatibility

- Combined ARGD／DAGD Source
- Standard Custom Definition
- Custom Schema + Trusted Adapter
- Custom Point ID
- CDOGD Absent
- Custom Orchestrator Capability

### 17.3 Runtime Mode

- Zero Definition + OFF
- Zero Definition + OBSERVE
- Zero Definition + ENFORCE
- Optional Binding + Missing
- Required Binding + Missing
- Unknown Action
- Invalid DefinitionとValid Definitionの混在

## 18. 第一拡張受入シナリオ

1. Definition 0件でMain Model RuntimeとExperiment Baselineが動作する。
2. 任意名のJSON 1個、Manifestまたは標準Envelope、Adapter、Profile、Bindingを追加する。
3. Runtime Coreの改修なしで、そのDefinitionがDiscovery、Validation、Compile、Point実行に参加する。
4. Definitionを外すと、0件Baselineに戻る。
5. それぞれのRun Recordから、構成差と負荷差を再現できる。

## 19. Authorization Boundary

本文書はPhase 3の要件をAcceptedとするが、実装は未解禁である。今回行うのはDocs作成のみである。
