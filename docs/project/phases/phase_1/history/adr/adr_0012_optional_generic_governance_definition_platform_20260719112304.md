# ADR-0012: 全GD任意・0件Baselineの汎用Definition Platform

- 文書ID: `adr_0012_optional_generic_governance_definition_platform`
- 状態: `accepted`
- 作成日時: `2026-07-19 11:23:04 JST`
- 更新日時: `2026-07-19 11:23:04 JST`
- Snapshot: `20260719112304`
- Decision Owner: ユーザー
- 記録担当: 設計者役担当Task
- 正本言語: 日本語
- 関連要件: [generic_governance_definition_platform_requirements_20260719112304.md](../requirements/generic_governance_definition_platform_requirements_20260719112304.md)
- 関連Architecture: [governance_definition_platform_architecture_20260719112304.md](../architecture/governance_definition_platform_architecture_20260719112304.md)
- 最新Index: [documentation_index_20260719112304.md](../documentation_index_20260719112304.md)
- supersedes: なし

## Context

現在参照しているARGD／DAGDと、将来追加予定のCDOGD、AISGD、AAGD、MPGD等がある。ただし、実際の利用者は、それらと無関係なGD、まったく異なる名前、異なるSchema、またはDefinition 0件の構成を使う可能性がある。

特定GD名、数、Path、Category、Schema、CDOGDの存在をCoreにハードコードすると、Governance Definition交換性の主張が成立しない。

## Decision

- Governance DefinitionをOptional Pluginとする。
- ARGD／DAGDも必須Dependencyにしない。
- Definition 0件を正式なProduction Baselineとする。
- CoreはGD名、GD数、File名、Directory、Domain、Point IDのClosed Listを持たない。
- Provider／Manifest／Descriptor／Adapter／Normalized IR／Compiler／Bindingを通じて取り込む。
- `EmptyDefinitionProvider`を正式実装とする。
- Manifest Firstを推奨し、標準Envelopeがある場合のみContent Discoveryを許容する。
- Filename-based Discovery／Semanticsを禁止する。
- JSONはDataのみとし、Custom Adapterは別のTrusted Pluginとする。
- CDOGDも任意とし、Dynamic RoutingはOrchestration Capabilityを持つDefinitionがある場合のみ有効化できる。

## Mode Semantics with No Definitions

| Mode | Decision |
|---|---|
| `off` | Pass-through |
| `observe` | `inactive_no_definitions` + Warning。RequiredならError |
| `enforce` | Required Governance MissingとしてRefuse／Error |

Definition 0件でEnforcement Successを記録することを禁止する。

## Rationale

1. 実際に誰がどのGDを使うか予測できない。
2. 将来のGD追加でCore修正を必要にしないことが交換性の必要条件である。
3. ARGD／DAGDありとなしを比較できること自体が研究上重要である。
4. FilenameやJSONの存在だけで行動を実行するのは誤解釈とSecurity Riskを招く。
5. SourceをImmutableにし、Adapter／IR／Adjustmentで吸収すれば、Author定義とRuntime調整を分離できる。

## Consequences

### Positive

- Definition 0件でMain Runtimeを使える。
- Catalog外のCustom Definitionを取り込める。
- ARGD／DAGDを特別扱いせずに第一実証として使える。
- CDOGDがなくてもManual／Static Routingを使える。
- Invalid／Unsupported PackageをQuarantineし、影響範囲を限定できる。

### Negative

- Manifest、Descriptor、Adapter Registry、IR、Compiler等の概念が必要になる。
- 任意JSONを自動で完全解釈できるわけではない。Custom SchemaにはAdapterが必要になる。
- DefinitionのState、Dependency、Conflict、Versionを管理する必要がある。

## Alternatives Considered

### Alternative A: ARGD／DAGDをBuilt-in必須にする

却下。Empty Baseline、他者Definitionの利用、統治なし比較を阻害する。

### Alternative B: 16 GDのClass／Loaderを先に作る

却下。未来のGD名とSchemaをCoreに固定し、未使用の実装工数を増やす。

### Alternative C: Directory内のJSONを全て自動解釈

却下。無関係JSON、Malformed JSON、Custom Schemaの誤解釈とSecurity Riskがある。

### Alternative D: CDOGDをRoutingの必須Coreにする

却下。CDOGDが不在、空、Custom Orchestratorに交換される構成を阻害する。

## Acceptance Proof

第一の拡張性証明は次とする。

1. 0 DefinitionでRuntimeが動作する。
2. 任意名のDefinition、Manifest、Adapter、Bindingを追加する。
3. Core変更なしでObserve実行できる。
4. 必要なAction Adapter／Authorityを追加しEnforceできる。
5. Definitionを外し0 Definitionに戻る。

## Authorization Boundary

本ADRはDecisionのみAcceptedとし、Definition Directory、Manifest、Adapter、Sourceの作成は個別の実装許可まで行わない。
