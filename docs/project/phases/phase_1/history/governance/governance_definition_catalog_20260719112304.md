# Governance Definition Catalog

- 文書ID: `governance_definition_catalog`
- 状態: `current_reference_catalog`
- 作成日時: `2026-07-19 11:23:04 JST`
- 更新日時: `2026-07-19 11:23:04 JST`
- Snapshot: `20260719112304`
- 作成担当: 設計者役担当Task
- 対象: 現時点で計画されているGovernance Definitionの意味と制約
- 正本言語: 日本語
- 関連要件: [generic_governance_definition_platform_requirements_20260719112304.md](../requirements/generic_governance_definition_platform_requirements_20260719112304.md)
- 関連Architecture: [governance_definition_platform_architecture_20260719112304.md](../architecture/governance_definition_platform_architecture_20260719112304.md)
- 最新Index: [documentation_index_20260719112304.md](../documentation_index_20260719112304.md)
- supersedes: なし（新規Catalog系列）

## 1. Catalogの使い方

本Catalogは、現時点で計画されているGovernance Definition（GD）の名称、意味、作者提案の配置先、重要な権限境界を記録する。

ただし、本Catalogに記載された名称はRuntime Coreの固定一覧ではない。

- すべてのGDは任意である。
- ARGD／DAGDを含め、まったく存在しない構成が有効である。
- Catalog外の名前、日本語名、別Schema、別DomainのGDが入ることを前提とする。
- File名やGD名からCapability、Domain、Pointを推測しない。
- 配置Pathは作者管理Layoutの推奨値であり、Runtime Contractではない。
- 実際のDiscoveryはManifestまたは標準Envelope、実行はDescriptor／Capability／Bindingに基づく。

## 2. Foundational Governance

### 2.1 ARGD

```text
略称     : ARGD
正式名称 : Axiomatic Reasoning Governance Definition
現行Version: 0.3.1
```

ARGDは、推論の前提、Context、矛盾、情報不足、根拠、反証、代替仮説、表現構造、Drift、Repair等を統治する。

主な領域：

1. Input Interpretation／Premise
2. Context Priority
3. Contradiction／Information Insufficiency
4. Reasoning Quality
5. Structural Expression
6. Efficiency／Repair

主な要素：

- 入力構造保持
- 前提・決定事項の固定
- 無断要約の抑制
- Context混在防止
- 矛盾未解決時の停止
- 情報不足を推測で埋めない
- Fact／Observation／Inference／Assumption／Evaluationの分離
- Sycophancy防止
- Refutation／Alternative Hypothesis
- Drift Detection／Re-fix

現行SourceはDAGDと同一JSON内に含まれる。

### 2.2 DAGD

```text
略称     : DAGD
正式名称 : Declarative AI Governance Definition
現行Version: 0.4.4
状態     : EXPERIMENTAL
```

DAGDは、Policy Goal、Constraint、Capability、Evaluation、Severity、Audit、Repair、Activation、Self Audit、Audit-to-Action、Status Reportingを扱う。

主なGovernance Operation：

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

Score、State、Actionはそのまま実行Codeにハードコードせず、Legacy Adapter、Normalized IR、Compiler、Action Resolverを通す。

### 2.3 現行複合Source

```text
/path/to/private-definition-source/
  思想_脳内構造_理論系/
  モシュール型LLMランタイム統治フロンプト設計/
  宣言型LLM統治フロンプト設計/
  GitHub公開関連/部品類_20260603/構文置き場_20260603/元構文_20260623/
  argd_v0.3.1_en_dagd_v0.4.4_en.json
```

- Top Level: `argd`、`dagd`
- Author: Nazuna Research
- License: CC-BY-SA-4.0
- Runtime取込み時は不変SnapshotとDigestを保持する。
- 利便性のため原本を独自分割せず、Legacy Adapterが2定義として展開する。
- このSourceが無い場合もRuntimeは動作する。

## 3. Optional Governance Extensions

### 3.1 CDOGD

```text
略称     : CDOGD
正式名称 : Cross-Domain Orchestration Governance Definition
作者提案Path: definitions/orchestration/cdogd_v0.1.0_en.json
```

CDOGDは、複数のGDを横断してまとめるための自動動的RoutingのOrchestration GDである。

現在の依頼や対象に応じて、どのGDをどの範囲で働かせるかを整理する。また、GD同士の重なり、引き渡し、抑制、弱化、修復の伝播を扱う。

注意：

- CDOGD自身も任意である。
- CDOGDが空または不在でもよい。
- Dynamic RoutingはPhase 9の将来機能である。
- Custom Orchestrator-capability Definitionに交換可能である。

### 3.2 SPPGD

```text
略称     : SPPGD
正式名称 : Strategic Planning and Prioritization Governance Definition
作者提案Path: definitions/domain_extensions/decision_pipelines/sppgd_v0.1.0_en.json
```

SPPGDは、戦略判断の構造を整理するGDである。

目的、前提、制約、選択肢、選ばなかった選択肢、優先順位、配分、順序、継続、停止、撤退、保留、再評価条件などを整理する。

### 3.3 DAAGD

```text
略称     : DAAGD
正式名称 : Decision Authority and Accountability Governance Definition
作者提案Path: definitions/domain_extensions/decision_pipelines/daagd_v0.1.0_en.json
```

DAAGDは、MARGD内で判断権限状態を判断するAuthority／Accountability GDである。

DAAGDは、既存のSystem Policy、Developer Policy、Runtime Policy、Tool権限、外部実行権限、委任条件、承認条件、責任分界に基づき、当該判断をAIまたはRuntimeの自律判断として扱えるか、人間判断へ戻すべきか、承認待ちとすべきか、委任範囲外とすべきか、責任主体未確定とすべきかを判断する。

ただし、DAAGDは外部に存在しない権限を新しく生成するものではない。DAAGDは、既に存在する方針、権限、委任、承認条件、責任分界の範囲内で、MARGD内のAuthority／Accountability Stateを判断する。

### 3.4 SDAGD

```text
略称     : SDAGD
正式名称 : Strategic Decision Audit Governance Definition
作者提案Path: definitions/domain_extensions/decision_pipelines/sdagd_v0.1.0_en.json
```

SDAGDは、戦略判断に関する監査を担当するGDである。

SDAGDは、SPPGDが整理した判断構造と、DAAGDが判断したAuthority／Accountability Stateを監査する。

SDAGDが示すのは、あくまで監査上の状態である。SDAGDは戦略判断そのものを作らず、DAAGDを代替せず、自律判断可否、承認待ち状態、委任範囲内外、責任主体成立状態を判断しない。

### 3.5 SDMRGD

```text
略称     : SDMRGD
正式名称 : Strategic Decision Meta-Review Governance Definition
作者提案Path: definitions/domain_extensions/conditional_watchdogs/sdmrgd_v0.1.0_en.json
```

SDMRGDは、SDAGDの監査状態をMeta ReviewするGDである。

SDAGDの監査範囲、監査根拠、監査結果分類、形式的通過の危険、過剰監査、過少監査、修復の必要性などを確認する。

SDMRGDにおけるEscalationは、外部の最終判断や承認へ直接進めることではない。基本的には、SDAGD側のSelf Audit、Repair、Re-audit、または上位Runtime側の条件確認へ戻す。

### 3.6 DSGD

```text
略称     : DSGD
正式名称 : Data Science Governance Definition
作者提案Path: definitions/domain_extensions/ordinary/dsgd_v0.1.0_en.json
```

DSGDは、データ分析の観点から、分析目的、対象範囲、データ、構造、出所、品質、仮説、手法、評価指標、漏れ、偏り、統計的妥当性、分析主張を扱うGDである。

分析結果そのものだけでなく、その分析がどの前提、データ、手法、評価条件に基づいているかを整理する。

### 3.7 ACRGD

```text
略称     : ACRGD
正式名称 : Artifact Composition and Review Governance Definition
作者提案Path: definitions/domain_extensions/ordinary/acrgd_v0.1.0_en.json
```

ACRGDは、成果物の構成、変換、読みやすさ、形式、配置、公開・提出可能性の主張を扱うGDである。

文章、資料、構造化File、提出物などについて、目的、読者、構成、形式、開示範囲、改訂履歴などを整理する。

### 3.8 AAGD

```text
略称     : AAGD
正式名称 : Agentic AI Governance Definition
作者提案Path: definitions/domain_extensions/ordinary/aagd_v0.1.0_en.json
```

AAGDは、Agentic AIの実行過程を扱うGDである。

目的、作業範囲、計画、手順、Tool Call、副作用、作業状態、引き渡し、記憶、完了確認などを整理する。AAGDが実行過程を確認することは、実行許可を出すことではない。

### 3.9 AISGD

```text
略称     : AISGD
正式名称 : AI Security Governance Definition
作者提案Path: definitions/domain_extensions/ordinary/aisgd_v0.1.0_en.json
```

AISGDは、AIを介して発生するAI Security上の危険を扱うGDである。

Prompt Injection、Jailbreak試行、指示漏え、秘密情報の露出、個人情報の露出、Tool悪用、権限混同、方針回避、Agent間攻撃などを扱う。

### 3.10 MPGD

```text
略称     : MPGD
正式名称 : Model Policy Governance Definition
作者提案Path: definitions/domain_extensions/ordinary/mpgd_v0.1.0_en.json
```

MPGDは、Model Policy上の判断について、根拠、適用範囲、例外、記録を扱うGDである。

方針や条項の識別、適用可否、優先関係、矛盾、例外、過剰拒否、過少拒否、再評価、修復、判断履歴などを整理する。

MPGDは、存在しないPolicyを新しく生成しない。既存Policyの識別と適用状態を扱う。

### 3.11 DCAGD

```text
略称     : DCAGD
正式名称 : Development Consulting AI Governance Definition
作者提案Path: definitions/domain_extensions/ordinary/dcagd_v0.1.0_en.json
```

DCAGDは、AI支援型の開発相談を扱うGDである。

要件整理、技術選択肢、設計方針、実装方針比較、実現可能性、難易度、概算工数、開発上の危険、保守性、拡張性などを整理する。

### 3.12 PMOGD

```text
略称     : PMOGD
正式名称 : Project Management and Orchestration Governance Definition
作者提案Path: definitions/domain_extensions/ordinary/pmogd_v0.1.0_en.json
```

PMOGDは、Project進行の整理を扱うGDである。

作業項目、担当、期限、依存関係、阻害要因、引き渡し、合意事項、未解決事項、納品可能性、Domain横断の作業状態などを整理する。

### 3.13 AIRGD

```text
略称     : AIRGD
正式名称 : AI Research Governance Definition
作者提案Path: definitions/domain_extensions/ordinary/airgd_v0.1.0_en.json
```

AIRGDは、AI研究における研究主張、新規性、証拠と主張のつながりを扱うGDである。

研究課題、先行研究、新規性の主張、仮説、反証条件、研究設計、証拠、実行履歴、結果と主張の分離、限界、再現条件などを整理する。

### 3.14 AIAGD

```text
略称     : AIAGD
正式名称 : AI Architecture Governance Definition
作者提案Path: definitions/domain_extensions/ordinary/aiagd_v0.1.0_en.json
```

AIAGDは、AI Systemの構造、構成要素の責務、接続関係、情報の流れ、境界設計、配置、構造上の主張、実行時の整合主張を扱うGDである。

Systemの目的、要件、品質属性、構成要素の責務、接続関係、信頼境界、権限境界の構造、Model・検索機構・記憶機構・Tool・Agent・Policy層・評価層の配置などを整理する。

### 3.15 SEGD

```text
略称     : SEGD
正式名称 : Software Engineering Governance Definition
作者提案Path: definitions/domain_extensions/ordinary/segd_v0.1.0_en.json
```

SEGDは、Software Engineeringの実行、検証、変更管理、成果物の識別、修復、巻き戻し、再実行、実装履歴を扱うGDである。

要件、受け入れ条件、仕様、設計と実装の対応、Repository、Branch、Source Codeの変更、Config変更、Dependency変更、検証結果、Build結果、Deployment準備状態、実装判断の履歴などを整理する。

### 3.16 OMRGD

```text
略称     : OMRGD
正式名称 : Operations, Maintenance, and Reliability Governance Definition
作者提案Path: definitions/domain_extensions/ordinary/omrgd_v0.1.0_en.json
```

OMRGDは、運用状態、保守性、復旧可能性、信頼性を扱うGDである。

運用状態、Serviceの健全性、監視対象、Log、指標、Alert、Incident、Failure、Degradation、Outage、Runbook、Rollback手順、Recovery手順、保守作業、運用上の危険、変更影響、再発防止、継続的改善項目などを整理する。

## 4. 推奨Binding Map

次はInitial Profile設計の参考であり、名前による自動Binding規則ではない。明示的なDescriptor、Capability、Bindingが必ず優先される。

| Point／Profile | 参考Definition | 意図 |
|---|---|---|
| Main Foundational | ARGD、DAGD | 前提、Context、Audit、Repair |
| Input | ARGD、AISGD、MPGD | 入力解釈、Injection、Policy |
| AI Development | ARGD、DAGD、DCAGD、AIAGD、SEGD | 開発相談、Architecture、実装 |
| AI Research | ARGD、DAGD、AIRGD | 研究主張、証拠、再現性 |
| Strategic Decision | SPPGD、DAAGD、SDAGD | 計画、Authority、Audit |
| Strategic Watchdog | SDMRGD | 条件付きMeta Review |
| Data／RAG | DSGD、AISGD、ARGD | Data Quality、Source、Injection |
| Artifact／Output | ACRGD、ARGD、DAGD | 構成、公開可能性、表現精度 |
| Guardrail | AISGD、MPGD、DAAGD | Security、Policy、Authority |
| Agent／Tool | AAGD、AISGD、DAAGD | 実行過程、危険、権限 |
| Judge | ARGD、DAGD、対象Domain GD | 評価基準、独立性、根拠 |
| Repair | DAGD、対象Domain GD | 修復条件、成功判定 |
| Project Management | PMOGD、SPPGD、DAAGD | 作業状態、優先順位、承認 |
| Operations | OMRGD、DAGD | 運用、復旧、状態 |
| Orchestration | CDOGDまたは同等Capabilityを持つCustom GD | 動的Routing、Conflict、Handoff |

## 5. 権限と責務の固定境界

### 5.1 AAGD

AAGDはAgentの実行過程を統治するが、Toolまたは外部操作の許可を生成しない。

### 5.2 DAAGD

DAAGDは既存の委任、承認、権限、責任分界を解釈するが、外部に存在しない権限を生成しない。

### 5.3 MPGD

MPGDは既存のModel Policyを識別・適用・監査するが、存在しないPolicyを生成しない。

### 5.4 SDAGD／SDMRGD

SDAGDの監査状態やSDMRGDのEscalationは、外部の最終判断、承認、権限付与を代替しない。

### 5.5 共通原則

どのGDも、System Policy、Developer Policy、Host Policy、Tool Permission、外部Authorityを上書きしない。

## 6. Runtimeにおける非ハードコード原則

Runtimeは次の定数分岐を持たない。

```text
if definition_id == "ARGD": ...
if filename contains "aisgd": ...
if cdogd exists: enable router
known_gd_count = 16
```

代わりに次を使用する。

```text
Provider
  ↓
Manifest／Envelope
  ↓
Descriptor／Capability
  ↓
Adapter／Normalized IR
  ↓
Compiler／Plan
  ↓
Explicit Binding／Governance Point
```

## 7. 現時点の実装境界

- Phase 3で汎用の入れ物、Empty Provider、Filesystem Provider、Manifest、Adapter、IR、Compiler、Bindingを実装対象とする。
- Phase 3でARGD／DAGDをMain Governanceの第一実証とするが、必須Dependencyにしない。
- 他の16 ExtensionすべてをPhase 3で実装／有効化しない。
- 各Functional Layerの実装Phaseで、対応するDefinitionとBindingを段階的に追加できるようにする。
- Dynamic Cross-Domain OrchestrationはPhase 9に延期する。

## 8. Catalogの更新原則

新しいGD、Version、制約、Author Layoutが追加された場合は、本Fileを上書きせず、新Timestampの後継Catalogを作成する。Runtime CoreのClosed EnumとしてCatalogを取り込まない。
