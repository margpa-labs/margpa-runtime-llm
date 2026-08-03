# Generic Governance Definition Platform Architecture

- 文書ID: `governance_definition_platform_architecture`
- 状態: `accepted_planning_only`
- 作成日時: `2026-07-19 11:23:04 JST`
- 更新日時: `2026-07-19 11:23:04 JST`
- Snapshot: `20260719112304`
- 作成担当: 設計者役担当Task
- 対象: Definition 0件を含む汎用GD Plugin基盤
- 正本言語: 日本語
- 上位要件: [generic_governance_definition_platform_requirements_20260719112304.md](../requirements/generic_governance_definition_platform_requirements_20260719112304.md)
- 関連Catalog: [governance_definition_catalog_20260719112304.md](../governance/governance_definition_catalog_20260719112304.md)
- 関連ADR: [adr_0012_optional_generic_governance_definition_platform_20260719112304.md](../adr/adr_0012_optional_generic_governance_definition_platform_20260719112304.md)
- 最新Index: [documentation_index_20260719112304.md](../documentation_index_20260719112304.md)
- supersedes: なし（新規Architecture系列）

## 1. Architecture Goal

次の2状態を同一Application Coreで成立させる。

```text
A. definitions = 0
   → GovernanceなしでMain Model Runtimeが完全動作

B. definitions = 1..N
   → 任意Provider／Schema／Adapter／Bindingを通じて統治を追加
```

Coreの変更なしに、将来の未知GD、Custom Point、Custom Orchestratorを追加できることを目標とする。

## 2. Dependency Direction

```text
Entrypoint／UI／CLI
        ↓
Application Orchestration
        ↓
Governance Ports／Contracts
        ↑
Infrastructure Adapters
  ├─ Empty Definition Provider
  ├─ Filesystem Definition Provider
  ├─ Legacy ARGD／DAGD Adapter
  ├─ Standard GD Adapter
  └─ Generic Rule Adapter
```

Domain側はFilesystem Path、JSON Parser、TOML Parser、ARGD／DAGDの個別Schemaに依存しない。

## 3. Core Data Model

### 3.1 Provider Descriptor

```text
provider_id
provider_kind
source_uri
configured
availability
trust_level
capabilities
```

### 3.2 Package Manifest

```text
manifest_schema
package_id
package_version
package_digest
author
license
definitions[]
```

Definition Entry：

```text
namespace
definition_id
definition_version
relative_path
expected_digest
schema_id
adapter_id
required_dependencies[]
optional_dependencies[]
conflicts[]
```

### 3.3 Standard Definition Descriptor

```text
canonical_ref
provider_ref
package_ref
namespace
definition_id
definition_version
source_digest
schema_id
adapter_id
display_name
domain_tags[]
capabilities[]
recommended_points[]
dependencies[]
conflicts[]
author
license
validation_state
activation_metadata
```

`domain_tags`、`capabilities`、`recommended_points`はExtensible Stringである。新しいDomainのたびにCore Enumを修正する設計にしない。

### 3.4 Normalized Governance IR

IRはSource Schemaの差を吸収し、Compilerに対して次を提供する。

- Definition Identity
- Rule Identity
- Rule Class
- Input／Output Scope
- Activation Condition
- Preconditions
- Deterministic Predicate
- Semantic Evaluation Request
- Severity Mapping
- Recommended Action
- Repair Hint
- Evidence Requirement
- Dependency／Conflict Metadata

IRは未知フィールドを無条件に捨てない。Preserved Extension MetadataまたはUnsupported Featureとして表現する。

### 3.5 Compiled Plan

```text
plan_id
plan_digest
compiler_id
compiler_version
point_id
binding_digest
definition_refs[]
definition_digests[]
adjustment_digest
runtime_capability_digest
deterministic_steps[]
semantic_steps[]
action_mappings[]
budgets
warnings[]
```

## 4. Provider Port

Conceptual Interface：

```text
GovernanceDefinitionProvider
  describe() -> ProviderDescriptor
  repository_state() -> GovernanceRepositoryState
  list_packages() -> PackageSummary[]
  list_definitions(package_ref?) -> DefinitionSummary[]
  load_manifest(package_ref) -> RawManifest
  load_definition(definition_ref) -> RawDefinition
```

ProviderがRaw Definitionの意味を解釈しない。解釈はAdapterの責務である。

## 5. Empty Definition Provider

```text
provider_id        : built_in.empty
repository_state   : empty
packages           : []
definitions        : []
external_io        : none
```

### 5.1 必要性

- Definitionなしが異常ではないことを型で表現する。
- Unit Test専用Dummyにしない。
- `baseline_empty_governance`の正式Providerとする。
- FilesystemがないEnvironmentでもGovernance Portを満たす。

## 6. Filesystem Provider

### 6.1 Rootの取得

Root PathはApplication Config／Environment／Explicit OverrideのTyped Precedenceで解決する。Source CodeへAbsolute Pathをハードコードしない。

### 6.2 Layout例

```text
definitions/
  packages/
    margpa_foundational/
      manifest.toml
      argd_v0.3.1_en_dagd_v0.4.4_en.json
    nazuna-research_domain_extensions/
      manifest.toml
      orchestration/
      domain_extensions/
    custom_vendor/
      manifest.toml
      anything.json
```

Directory名は人間の管理用であり、Runtime Semanticsを持たない。

### 6.3 Discovery Order

1. Configured Source Rootの安全性検証
2. Explicit Package Manifestの列挙
3. Manifest SchemaとDigestの検証
4. Definition SummaryのRegistry登録
5. 必要時のRaw Definition Lazy Load
6. 明示設定時のみStandard Envelope Discovery

Directory全体を無制限に再帰し、見つけたJSONをすべてGovernanceとして読む方式は採用しない。

## 7. Adapter Registry

```text
AdapterRegistry
  resolve(schema_id, adapter_id, source_metadata)
  register(adapter_descriptor, factory)
  describe(adapter_id)
```

### 7.1 Legacy ARGD／DAGD Adapter

現行複合JSONを読み、`argd`と`dagd`を個別Descriptor／IRに展開する。

- Source Digestは複合JSON全体で保持する。
- Sub-definition IdentityにTop-level Keyを関連づける。
- 原本Fileは書き換えない。
- 未対応の項目は無断変換せずWarning／Unsupportedとする。

### 7.2 Standard GD Adapter

Projectが公開する将来のStandard Envelope／SchemaをNormalized IRへ変換する。

### 7.3 Generic Declarative Rule Adapter

単純な決定論Rule、Severity、Action Recommendationを持つ安全な汎用Schemaを扱う。任意Expression EvaluationやCode実行を許容しない。

### 7.4 Trusted Custom Adapter

- Python Package等の明示的なInstallを必要とする。
- Adapter ID／Version／Digest／Trust Sourceを記録する。
- Definition JSONの値だけでDynamic Importしない。

## 8. Registry Resolution

Canonical Referenceの概念形：

```text
provider://package_namespace/definition_id@definition_version#source_digest
```

### 8.1 Version

- Same ID + Multiple Versionは共存可能。
- BindingがVersionを固定するか、明示的なVersion Constraintで解決する。
- 単に最新Versionを無条件に選ばない。
- Same Canonical Identity + Different Digestは`duplicate_identity`または`hash_mismatch`とする。

### 8.2 Capability

CapabilityによるSelectionは、次の順で絞り込む。

1. Active Provider
2. Valid Definition State
3. Compatible Adapter／Compiler
4. Required Capability
5. Dependency／Conflict
6. Explicit Priority／Profile

## 9. Repository State Calculation

```text
no configured provider
  → unconfigured

configured providers, valid entries = 0, invalid entries = 0
  → empty

valid entries > 0, invalid entries = 0
  → ready

valid entries > 0, invalid entries > 0
  → degraded

configured source inaccessible or required resolution impossible
  → error
```

Malformed JSONをEmptyと数えない。`invalid_json`のDefinition StateとEvidenceを残す。

## 10. Binding Resolution with Empty State

```text
mode=off
  → Provider/Definitionを実行せずPass-through

mode=observe, required=false, definitions=0
  → inactive_no_definitions + warning + no intervention

mode=observe, required=true, definitions=0
  → binding_resolution_error

mode=enforce, definitions=0
  → required_governance_missing + refuse/error
```

## 11. Source／Adjustment／Binding Separation

### 11.1 Source

- 作者の定義内容
- Immutable
- Version／Digest／Licenseを保持

### 11.2 Adjustment

- Runtimeの運用・実験用Overlay
- Rule Selection、Soft Weight、Threshold、Budget、Action Mapping
- Sourceを変更しない
- Hard Constraintや外部Authorityを弱化しない

### 11.3 Binding

- Definition／CapabilityをPointへ配置
- Mode、Required、Profile、Budgetを指定
- SourceのDomainとPointを同一視しない

## 12. Adjustment Profile Example

```toml
[governance.adjustments.main_standard]
mode = "observe"
include_rules = []
exclude_advisory_rules = []
priority_offset = 0
max_semantic_calls = 1
max_evaluator_tokens = 512
max_latency_ms = 5000
max_repair_attempts = 1
status_verbosity = "standard"
```

`include_rules = []`の意味はAdapter／Profile Schemaで明示する。「すべて」と「0件」の曖昧性を残さない。

## 13. Security Architecture

### 13.1 Data Limits

- Max File Bytes
- Max JSON Depth
- Max Object Keys
- Max Array Length
- Max Definitions per Package
- Max Rules per Definition
- Max Text／Prompt Bytes
- Max Compiled Steps

### 13.2 Path Safety

- ManifestからのRelative PathをCanonicalizeする。
- Configured Package Root外へ出るPathを拒否する。
- Symbolic LinkのResolved PathもRoot境界で検証する。
- Absolute Path、`..`、URLをDefaultで拒否する。

### 13.3 Action Safety

```text
JSON recommendation
  → Normalized Action ID
  → Registered Action Adapter?
  → Runtime Capability?
  → Authority／Permission?
  → Mode=enforce?
  → Execute or Record-only
```

## 14. Caching

### 14.1 Metadata Cache

Provider／Package／Definition Summaryに限定し、Startupを軽量化する。

### 14.2 Raw Source Cache

Source DigestをKeyに不変ObjectとしてCacheできる。

### 14.3 IR／Plan Cache

- IR: Source Digest + Adapter Version
- Plan: IR Digest Set + Adjustment Digest + Compiler Version + Point + Capability Digest

Cache Hitであっても、Binding Mode、Runtime Deadline、Required Flagは毎回検証する。

## 15. ARGD／DAGD Package Example

Manifest概念形：

```toml
manifest_schema = 1
package_id = "nazuna-research.margpa-foundational"
package_version = "1"

[[definitions]]
namespace = "nazuna-research.margpa"
definition_id = "argd"
definition_version = "0.3.1"
path = "argd_v0.3.1_en_dagd_v0.4.4_en.json"
schema_id = "legacy.margpa.combined"
adapter_id = "legacy_margpa_combined"

[[definitions]]
namespace = "nazuna-research.margpa"
definition_id = "dagd"
definition_version = "0.4.4"
path = "argd_v0.3.1_en_dagd_v0.4.4_en.json"
schema_id = "legacy.margpa.combined"
adapter_id = "legacy_margpa_combined"
```

2 Entryが同一Source Path／Digestを参照することを許容する。

## 16. Custom Definition Acceptance Flow

```text
1. Empty ProviderでRuntime起動
2. Custom Package SourceをConfigに追加
3. Manifest／EnvelopeをDiscovery
4. Schema ID／Adapter IDを解決
5. DescriptorとIRを生成
6. Explicit BindingをCustom Pointへ設定
7. ObserveでEvaluationとEvidenceを確認
8. Action Adapter／Authorityを検証後にEnforce
9. Packageを外しEmpty Baselineへ復帰
```

Step 2～8のためにRuntime Coreを変更しないことが受入基準である。Custom Adapterが必要な場合は、Trusted Adapter Pluginの追加は許容するがCore固有分岐は追加しない。

## 17. Test Architecture

### 17.1 Contract Test

すべてのProvider／Adapter／Compilerに共通Contract Testを適用する。

### 17.2 Fixture Category

```text
empty/
invalid_json/
unknown_schema/
adapter_missing/
duplicate/
dependency_conflict/
legacy_margpa_combined/
standard_custom/
custom_orchestrator/
```

### 17.3 Non-regression

- Definition Sourceの有無でModel AdapterのContractが変わらない。
- Governance OFFでPrompt／Token／Model Callが増えない。
- Invalid Optional PackageでValid Packageが不要に無効にならない。
- Required Binding不足でEnforce Successを記録しない。
- Filename変更だけでSemanticsが変わらない。

## 18. 実装モジュール候補

具体Directoryは実装時に現行Source Treeと整合させるが、責務は次のように分ける。

```text
modules/governance/
  contracts/
  domain/
  application/
  ports/
  public.py

adapters/governance/
  providers/
  definition_adapters/
  compilers/
  evaluators/
  actions/
```

Framework固有のFile／JSON／TOML処理はAdapter側に閉じ込める。

## 19. 未決事項

- ManifestにTOMLとJSONのどちらを第一採用するか
- Standard GD EnvelopeのSchema Version 1
- Canonical Referenceの厳密表記
- Signature／Trust StoreのPhase
- Remote Providerの信頼境界
- Adapter PluginのInstall／Allowlist方式
- Definition PackageのLicense表示／再配布Policy
- Custom Rule Expressionを導入するか（初期は導入しない）

## 20. Authorization Boundary

本ArchitectureはAcceptedであるが、Directory、Source、Config、Schema、Test、ARGD／DAGD Snapshotの作成は未解禁である。
