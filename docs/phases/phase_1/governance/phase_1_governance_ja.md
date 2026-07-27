# Phase 1 Governance Lossless Compilation
```yaml
document_id: phase_1_governance_lossless_compilation
phase: phase_1
status: frozen
language: ja
created_at: 2026-07-26 15:16:24 JST
frozen_at: 2026-07-26 15:16:24 JST
source_documents: 5
source_manifest: ../../phase_1_ex/operations/source_to_target_documentation_migration_manifest.json
source_hash_algorithm: sha512
supersedes: null
rag_default: true
```

## Compilation Policy

本書はPhase 1中に作成されたSource文書を、省略、要約、意味変更または再解釈せず、Source Path順に再配置したLossless Compilationである。

本文は原文を維持し、Directory Migration後も参照可能にするため、MarkdownのLocal Link Pathだけを機械的に正規化している。原文File、原文SHA-512および移動先はSource Manifestから一意に解決できる。

矛盾、旧判断、未解決事項および後継文書への置換前状態も削除していない。Currentな判断はCurrent Canonical文書とPhase Indexを参照する。

## Source Documents

<!-- SOURCE_BEGIN 1: docs/governance/audit_evaluation_security_20260718174637.md -->

### Source 1: `docs/governance/audit_evaluation_security_20260718174637.md`

- History Target: `docs/project/phases/phase_1/history/governance/audit_evaluation_security_20260718174637.md`
- Source SHA-512: `240cd8ce9cb56c2d21096c08d84cc36a9273a19db7f18000e1bdacae7f796a0bc69908661b8cc56396624994b8b46332bb4b5a89459baa4179191be178e2dc28`
- Source Size: `7245` bytes

# 監査・評価・説明・安全性設計基準

- 文書ID: `audit_evaluation_security`
- 状態: `current`
- 作成日時: `2026-07-18 17:46:37 JST`
- 更新日時: `2026-07-18 17:46:37 JST`
- 対象: Audit Log、Evaluation、Repair、Guardrail、Tool Permission、Judge
- 正本言語: 日本語
- 関連Governance: [runtime_governance_20260718174637.md](../history/governance/runtime_governance_20260718174637.md)

## 1. Audit Log基本要件

- 専用Log保存Directoryを作る
- User入力からAssistant回答までの一往復を基本単位とする
- 一往復に関係する観測可能情報を構造化保存する
- 各Log単位にSHA-512を適用する
- 整合性検証を可能にする
- 過去Logを原則上書きしない
- Evaluation、Regeneration、Repairを追記Eventとして残す
- System TraceとModel Generated Explanationを分離する
- Model、Governance、Guard、RAG、Toolを関連IDで接続する

「全情報」はSystemが観測・再現可能な情報を意味し、Model内部の真の思考過程を意味しない。

## 2. 記録項目候補

### Identity

- Schema Version
- Session ID
- Turn ID
- Request ID
- Message ID
- Event ID
- Parent Event ID
- Timestamp

### Input／Context

- User Input
- System Prompt
- Modelへ渡したMessage列
- Context
- Context Source
- Context Truncation
- Summary利用有無

### Model

- Model ID
- Model Revision
- Model File
- Model File Hash
- Quantization
- Backend
- Backend Version
- Generation Config
- Output
- Token Count
- Latency
- Stop Reason
- Error

### Governance

- Governance Definition
- Governance Version
- Governance Hash
- Governance Plan
- Governance Profile
- State Before
- State After
- Applied Rule
- Dimension Score
- Deviation
- Severity
- Affected Segment
- Recommended Action
- Executed Action
- Repair
- Re-fix

### Guard／Tool

- Guard Input
- Guard Output
- Guard Category
- Guard Severity
- Tool Call
- Tool Result
- Tool Permission
- Human Approval

### RAG／Judge／User

- RAG Query
- Retrieved Chunk
- Source
- Judge Result
- User Rating
- User Comment
- 問題Tag
- 高水準の説明概要

## 3. SHA-512

概念形：

```json
{
  "payload": {},
  "integrity": {
    "algorithm": "sha512",
    "canonicalization": "...",
    "digest": "..."
  }
}
```

`integrity`を除いた正規化済み`payload`へSHA-512を適用する。

未決事項：

- UTF-8の明文化
- Key Order
- Whitespace
- Unicode Normalization
- Number Representation
- JSON Canonicalization方式
- JCS採用可否
- Event単位／Turn単位
- Binary／Attachment
- Hash再計算手順

ARGD／DAGD本体はTurnごとに複製せず、内容Hash単位の不変Snapshotとして保存し、Turn Logから参照する。

## 4. SHA-512の限界

SHA-512単体では、PayloadとDigestを同時に改ざんされた場合を防げない。

将来候補：

- Hash Chain
- HMAC
- Digital Signature
- Append-Only Storage
- WORM
- Merkle Tree
- External Timestamp
- Remote Audit Sink

## 5. Chain of Thought方針

生のChain of Thoughtは原則保存・公開しない。

理由：

- Log量が膨大になる
- 真の内部推論と一致する保証がない
- 機密情報を含む可能性
- 安全上の問題
- 小型Modelへの負荷
- 説明用生成文と内部計算は同一ではない

代替として保存するもの：

- Interpreted Intent
- Answer Basis
- Process Summary
- Applied Governance Rule
- Retrieval Source
- Tool Usage
- Uncertainty
- Limitation
- High-Level Explanation
- Affected Claim
- Repair Summary

「Transparent Reasoning」は次として解釈する。

- Basis Disclosure
- Source Traceability
- Applied Rule
- Affected Claim
- High-Level Explanation
- Uncertainty Disclosure

System Trace由来の事実とModel Generated Explanationを明確に分離する。

## 6. User Evaluation

候補機能：

- Rating
- Comment
- 問題Tag
- Regenerate
- 修正要求
- 修正前後比較

問題Tag候補：

- 前提逸脱
- 根拠不足
- 文脈喪失
- 矛盾
- 過剰一般化
- 過剰肯定
- 過剰否定
- 不要な確認
- 出典不足
- 不確実性未開示

## 7. Automatic Evaluation

将来、GovernanceとJudgeを利用して次を評価する。

- Context Preservation
- Premise Preservation
- Scope
- Reasoning Integrity
- Expression Precision
- Dialog Efficiency
- Self Repair
- Guardrail Compliance
- Citation Support
- Uncertainty Disclosure

Rule Basedで評価できる項目はLLMへ投げない。

## 8. Repair Event Model

過去回答を削除・上書きしない。

```text
Original Answer
    ↓
Evaluation Event
    ↓
Repair Request Event
    ↓
Regenerated Answer Event
    ↓
Comparison Event
```

すべて関連IDで接続する。

## 9. Runtime GovernanceとGuardrailの分離

```text
Runtime Governance
  推論品質、前提、根拠、文脈、監査、修復

Guardrail
  安全性、禁止事項、秘密情報、攻撃検出

Tool Permission
  外部実行の許可、拒否、承認
```

関連はするが、別Moduleとして実装する。

## 10. 初期Guard方針

```text
Guard Model:
  Qwen3Guard-Gen-0.6B
  Phase 4で追加

Prompt Injection:
  Rule Based中心
  専用Classifierは後から追加

Tool Permission:
  Modelではなく決定論的Policy
```

将来候補：

- Input Guardrail
- Output Guardrail
- Tool Guardrail
- Prompt Injection
- Jailbreak
- Secret検出
- Personal Information検出
- Tool悪用
- Agent間攻撃
- Human Approval
- Allow／Deny List
- Capability Based Permission
- Side Effect確認

未決事項：

- 禁止範囲
- Guard強度
- Fail Open／Fail Closed
- False Positive
- False Negative
- User Override
- System Policyとの優先順位
- Governanceとの競合
- 日本語Moderation Dataset
- Streaming中のOutput停止
- Guard Model障害時

## 11. Tool Permission

Tool実行許可をLLMへ委ねない。

ModelはTool利用を提案できても、最終的な実行可否は決定論的Policy Layerが判断する。

候補状態：

- Allowed
- Denied
- Requires Human Approval
- Allowed with Constraints
- Capability Missing
- Policy Conflict
- Unknown

将来のDAAGDは既存の権限、委任、承認状態を解釈できるが、新しい権限を生成しない。

## 12. LLM-as-a-Judge

目的：

- 回答品質評価
- Governance Deviation評価
- Repair前後比較
- 複数候補Ranking
- Human Rating補助
- Rule Basedで判断しにくい意味的評価

原則：

- Judgeを常駐させない
- Judge出力を絶対視しない
- JudgeのModel ID、Config、Hashを記録する
- Judge PromptとRubricをVersion管理する
- Judge結果もAudit Eventとして記録する
- Judgeを交換可能にする
- Judge利用不可時はDegradeする
- Rule Based評価を優先できるものはJudgeへ投げない

初期候補：

```text
Selene-1-Mini-Llama-3.1-8B Q5_K_M
```

未決事項：

- 導入Phase
- Evaluation Axis
- Score
- 日本語性能
- Bias
- Self Preference
- Model系列間の偏り
- Evaluation Cost
- Judge障害時
- 複数Judge合議
- Human Ratingとの統合

## 13. Storage方針

初期候補：

- JSON
- JSONL
- Append-Only Event Log

SQLiteはIndex／検索用途のHookとする。

CloudではPostgreSQL、Object Storage、専用Audit基盤を候補とする。

<!-- SOURCE_END 1: docs/governance/audit_evaluation_security_20260718174637.md -->

---

<!-- SOURCE_BEGIN 2: docs/governance/governance_definition_catalog_20260719112304.md -->

### Source 2: `docs/governance/governance_definition_catalog_20260719112304.md`

- History Target: `docs/project/phases/phase_1/history/governance/governance_definition_catalog_20260719112304.md`
- Source SHA-512: `88311ce365d745009fee2a09d7d7237a52dfeeb5dedcefc59f131bb7756807b67ddbca0d3aeda30d225ad9be48b5eb85c22e8edaed8bfd60488eee2e05723714`
- Source Size: `16127` bytes

# Governance Definition Catalog

- 文書ID: `governance_definition_catalog`
- 状態: `current_reference_catalog`
- 作成日時: `2026-07-19 11:23:04 JST`
- 更新日時: `2026-07-19 11:23:04 JST`
- Snapshot: `20260719112304`
- 作成担当: 設計者役担当Task
- 対象: 現時点で計画されているGovernance Definitionの意味と制約
- 正本言語: 日本語
- 関連要件: [generic_governance_definition_platform_requirements_20260719112304.md](../history/requirements/generic_governance_definition_platform_requirements_20260719112304.md)
- 関連Architecture: [governance_definition_platform_architecture_20260719112304.md](../history/architecture/governance_definition_platform_architecture_20260719112304.md)
- 最新Index: [documentation_index_20260719112304.md](../history/documentation_index_20260719112304.md)
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

<!-- SOURCE_END 2: docs/governance/governance_definition_catalog_20260719112304.md -->

---

<!-- SOURCE_BEGIN 3: docs/governance/phase_10_original_r_and_d_governance_extension_hooks_20260721155020.md -->

### Source 3: `docs/governance/phase_10_original_r_and_d_governance_extension_hooks_20260721155020.md`

- History Target: `docs/project/phases/phase_1/history/governance/phase_10_original_r_and_d_governance_extension_hooks_20260721155020.md`
- Source SHA-512: `15fa4fb23a18581f1c007913f1683bd5c0fd22b642c274c331af905e22ba8d7da4f0fc3fe2ebd1cc713203d626a27711d3d1cb991557419063b101778c7bb938`
- Source Size: `8663` bytes

# Phase 10 Original R&D Governance Extension Hooks

- 文書ID: `phase_10_original_r_and_d_governance_extension_hooks`
- 状態: `accepted_future_reservation`
- 作成日時: `2026-07-21 15:50:20 JST`
- 更新日時: `2026-07-21 15:50:20 JST`
- Snapshot: `20260721155020`
- 作成担当: 設計者役担当Task
- Decision Owner: ユーザー
- 公開区分: 公開可能な構想概要
- 正本言語: 日本語
- Phase 1-ex Requirements: [phase_1_ex_complete_operating_model_and_documentation_requirements_20260721155020.md](../history/requirements/phase_1_ex_complete_operating_model_and_documentation_requirements_20260721155020.md)
- Roadmap: [implementation_roadmap_20260721155020.md](../history/architecture/implementation_roadmap_20260721155020.md)
- supersedes: なし

## 1. Position

本書は、MARGPA Runtime LLMが一通り完成した後のPhase 10で、別Project／別Taskとして研究開発されるオリジナルR&D機構を疎結合統合するための予約である。

本書は構想の存在、研究領域、公開可能な作業概念、統合Hookだけを記録する。Algorithm、独自評価方式、実装構造、未公開の核心は記載しない。

```text
Implementation Time : Phase 10／本体一通り完成後
Development         : Separate Projects／Separate Tasks
Integration         : Optional／Loosely Coupled
Core Dependency     : Prohibited
Public Status       : Direction and existence disclosed
```

## 2. 例外認識型安全統治機構

```text
名称     : 例外認識型安全統治機構
研究領域 : AI Safety Governance
```

公開概要：

> 内部安全傾向、周辺安全制御、入力文脈、生成過程等の相互作用を対象とし、例外を含む複合的な安全挙動を統治する独立R&D機構。

### 2.1 Safety Stackの作業上の区分

公開版では「Safety Stack全体」という広い表現だけにせず、次の3区分で扱う。

#### モデル内部に形成された安全傾向

特定製品の内部構造を断定する意味ではなく、EASA上の作業概念として使用する。EASAの正式な公開定義は本書で新しく推測または補完しない。

- 危険回避方向への出力傾向
- 曖昧時の保守化
- 拒否傾向
- 一般化傾向
- 迎合抑制と肯定抑制
- 学習／調整によって形成された応答傾向

便宜上、`Embedded Safety Layer`または「内部安全傾向」と呼ぶ。

ただし、単一の物理的なLayerが存在すると断定しない。特定Model、製品、Providerの内部実装を推定または主張する用語として使用しない。

#### 周辺の安全制御

- 応答方針
- 外部判定
- 権限制御
- 製品上の制約
- 運用上の判断

具体的な製品名や非公開技術名を、この公開概要へ記載しない。

#### 複合安全挙動

内部安全傾向、周辺制御、入力文脈、生成過程等が相互作用し、最終応答として現れる挙動を`Composite Safety Behavior`として扱う。

### 2.2 MARGPAとの関係

- MARGPA Coreへ内部安全傾向の存在を固定前提としてHard-codeしない。
- 観測可能な入力、出力、外部Signal、Governance ResultをContract境界とする。
- 特定Modelの内部構造を監査できると過剰主張しない。
- Hookが未接続でもCore Runtimeは成立する。

## 3. 分散証跡型例外認識エージェント統治安全機構

```text
名称     : 分散証跡型例外認識エージェント統治安全機構
研究領域 : Multi-Agent Governance,
           Distributed Accountability,
           and Safety Assurance
```

公開概要：

> 複数の判断・実行・検証主体間における責任、委譲、例外、改竄耐性付き証跡、全体整合および異常時の安全側制御を扱う独立R&D機構。

### 3.1 対象

- 複数のAgent
- 判断主体
- 実行主体
- 検証主体
- 必要に応じた人間主体
- 判断、委譲、実行、検証、例外、安全側制御

### 3.2 扱うProblem

- 責任拡散
- 隠れた権限集中
- 証跡断絶
- 局所判断の連鎖破綻
- 主体間での委譲範囲不整合
- 検証主体と実行主体の分離失敗
- 例外発生時の責任／安全制御断絶

### 3.3 単純な既存構成との区別

本機構は次だけを意味しない。

- 単純な複数AIの並列化
- 単一のSafety Filter
- 単一のLog機構
- Agent数を増やすOrchestration
- すべての主体を一つの中央判断へ置き換える構造

### 3.4 複数主体を一つの統治対象とする理由

- 個別主体だけを見ても全体安全性を判断できない。
- 主体間関係そのものが危険源になり得る。
- 委譲、責任、検証、例外が主体間で断絶し得る。
- 局所的に妥当な判断の連鎖が、全体として不整合になる場合がある。

### 3.5 主要な作業概念

- 責任境界
- 委譲
- 主体間検証
- 全体整合
- 例外認識
- 改竄耐性付き証跡
- 監査可能性
- 異常時の安全側制御
- 人間との関係

`改竄耐性付き証跡`は本機構の予定要素として公開概要にも明記する。具体的な方式、暗号構成、分散方式、保証範囲は現時点で開示しない。

## 4. Public Disclosure Levels

### 4.1 Roadmap

次だけを掲載する。

- 名称
- 研究領域
- 1から2行の公開概要
- Phase 10／別R&D／疎結合統合予定

### 4.2 System Architecture

- External R&D Extensionとしての接続位置
- Generic Provider Port経由
- Optionalであること
- Core非依存

### 4.3 Project Continuity Master

本書Section 2、3の作業概念、統合原則、公開境界を再開可能な粒度で記載する。

### 4.4 非掲載

- 独自Algorithm
- 評価方法の核心
- 未公開Schema／Protocol
- Security上公開すべきでないAssumption
- 実装Repository／非公開資料へのPath

## 5. Generic Integration Hook

両R&D機構をCoreへ固有実装として埋め込まず、次の汎用境界で接続する。

```text
External Governance Provider
  → Registration／Identity／Version／Hash
  → Capability Declaration
  → Activation Condition
  → Input Scope／Output Scope
  → Event／Evidence Reference
  → Standard Governance Result
  → Recommended Action
  → Executed Action／Governance State
```

候補Port／Contract：

- `ExternalGovernanceProviderPort`
- Governance Provider Registry
- Capability Negotiation
- Exception State
- Decision／Delegation／Execution／Verification Event
- Evidence Reference
- Standard Governance Result
- Timeout／Failure Result
- Audit／Status Event

具体的Class名はPhase 10で再評価できる。Core要件は責務とContractであり、上記名称の固定ではない。

## 6. Runtime Modes

統合時も研究比較可能性を維持する。

```text
off      : 完全無効
observe  : 判定／証跡／Statusだけ。実行へ介入しない
enforce  : 許可された範囲で停止、制御、修復等へ介入
```

Provider本体とProvider用Governance PointのON／OFFを分離可能にする。

## 7. Authority／Safety Boundary

- 外部機構は存在しない権限を生成しない。
- 上位System Policy、Developer Policy、Runtime Policyを無断上書きしない。
- Evidenceがない状態で責任主体や安全性を確定しない。
- `observe`結果を`enforce`済みと誤表示しない。
- 外部Provider Failure時のFail Open／Fail ClosedをProfileで明示する。
- 人間承認が必要な判断を自律判断へ変換しない。

## 8. Dependency Rule

```text
MARGPA Core → Generic Port only
External R&D Adapter → Generic Port implementation
External R&D System → Adapterの外側
```

- External PackageなしでCore TestがPassする。
- Providerなしで起動、会話、Governance OFF比較が成立する。
- Provider固有DependencyをCore Dependencyへ昇格させない。
- Version、Hash、Capability、ModeをAuditへ残す。

## 9. Phase 10 Start Condition

- MARGPA Runtime LLM本体が一通り完成している。
- Generic Governance PlatformとAdapter Boundaryが安定している。
- 対象R&D側の独立要件とInterfaceが定義されている。
- 公開／非公開情報境界が再確認されている。
- Performance、Privacy、Authority、Evidence Storageの影響が評価されている。
- ユーザーが統合開始を明示している。

## 10. Authorization Boundary

本書は将来HookのAccepted Reservationである。Phase 10実装、別Project作成、Algorithm公開、Provider追加、Core変更を現在許可しない。

<!-- SOURCE_END 3: docs/governance/phase_10_original_r_and_d_governance_extension_hooks_20260721155020.md -->

---

<!-- SOURCE_BEGIN 4: docs/governance/phase_10_original_r_and_d_system_catalog_20260721162242.md -->

### Source 4: `docs/governance/phase_10_original_r_and_d_system_catalog_20260721162242.md`

- History Target: `docs/project/phases/phase_1/history/governance/phase_10_original_r_and_d_system_catalog_20260721162242.md`
- Source SHA-512: `2be2605cc6e0fff1f752c76c2ed6bac42976fb453e65aa282ba004bae022ae20f126b2e1245478b900ff311e937013e8274f3978bc189cbee40a66c26ca32b0e`
- Source Size: `4447` bytes

# Phase 10 Original R&D System Catalog

- 文書ID: `phase_10_original_r_and_d_system_catalog`
- 状態: `current_future_reservation`
- 作成日時: `2026-07-21 16:22:42 JST`
- 更新日時: `2026-07-21 16:22:42 JST`
- Snapshot: `20260721162242`
- 作成担当: 設計者役担当Task
- Decision Owner: ユーザー
- 公開区分: 公開可能な名称・方向性・作業概念
- 正本言語: 日本語
- Requirements: [phase_1_ex_external_r_and_d_publication_and_integration_requirements_20260721162242.md](../history/requirements/phase_1_ex_external_r_and_d_publication_and_integration_requirements_20260721162242.md)
- Architecture: [phase_10_external_r_and_d_integration_architecture_20260721162242.md](../history/architecture/phase_10_external_r_and_d_integration_architecture_20260721162242.md)
- supersedes: `phase_10_original_r_and_d_governance_extension_hooks_20260721155020.md`

## 1. Position

MARGPA Runtime LLM本体が一通り完成した後のPhase 10で、別Project／別Taskとして独立開発される3つのOriginal R&D Systemを疎結合統合する。

存在と方向性を公開し、研究の核心は現在開示しない。

## 2. EASA

```text
EASA
Exception Aware Safety Architecture
例外認識型安全統治機構

Research Area:
AI Safety Governance
```

内部安全傾向、周辺安全制御、入力文脈、生成過程等の相互作用を対象とし、例外を含む複合的な安全挙動を統治する独立R&D Architecture。

作業概念：

- 内部安全傾向
- `Embedded Safety Layer`
- 周辺の安全制御
- `Composite Safety Behavior`

`Embedded Safety Layer`はEASA上の作業概念であり、特定製品内に単一の物理Layerが存在すると断定しない。

## 3. DLAGSA

```text
DLAGSA
Distributed LEA Agentic Governance & Safety Architecture
分散証跡型例外認識エージェント統治安全機構

Research Area:
Multi-Agent Governance,
Distributed Accountability,
and Safety Assurance
```

複数の判断・実行・検証主体間における責任、委譲、例外、改竄耐性付き証跡、全体整合および異常時の安全側制御を扱う独立R&D Architecture。

単純な複数AIの並列化、単一Safety Filter、単一Log機構ではない。主体間関係そのものを統治対象として扱う。

`LEA`の意味をMARGPA側で推測または再定義しない。

## 4. OCILNS

```text
OCILNS
Open Cognitive Interaction Ledger Network System
認知対話証跡台帳網

Research Area:
Cognitive Interaction Provenance,
Verifiable AI Systems,
and Distributed Auditability
```

人、AI、Tool、外部System間の認知的対話出来事を、後から検証、参照、継承、監査できる改竄耐性付き証跡単位として扱い、長期、分岐、多Model、多Thread環境でも再接続可能性を維持する独立R&D System。

LLM応答精度の直接向上を目的とせず、対話保存、改変検知、Model／Thread横断継承、選択的開示、監査支援、Local LLM検証、証跡ベースHandoffを長期運用される認知対話基盤として扱う。

特定LLM Provider、保存先、UI、Cloud環境へ依存しない。改竄耐性は単一SHA-512 Digestだけに依存しない構成を予定するが、具体方式は現在開示しない。

## 5. Config Requirement

Phase 10統合時、3 Systemを個別にON／OFF可能にする。

```text
EASA   : OFF／ON
DLAGSA : OFF／ON
OCILNS : OFF／ON
Default: All OFF
```

OFF時はSystemをLoad、Call、Writeしない。ON時にProviderが存在しない場合は、黙って無視せず明示的に扱う。

## 6. Loose Coupling

```text
EASA／DLAGSA
  → Generic External Governance Provider Port

OCILNS
  → Generic Evidence Ledger Port
```

- 3 SystemなしでMARGPA Runtime LLMは完全動作する。
- 独立したVersion、Capability、Lifecycleを持つ。
- Coreへ固有Dependencyを入れない。
- Adapterを通じて後付けできる。
- Effective Enabled Stateを記録できる。

## 7. Public Information Level

```text
Roadmap             : 正式名称、研究領域、1から2行概要
System Architecture : 接続位置とON／OFF
Continuity Master   : 本書の作業概念をやや詳しく記録
Algorithm           : 現在非掲載
```

## 8. Authorization Boundary

本Catalogは公開可能な将来予約である。3 Systemの実装、外部接続、Config変更、核心公開を現在許可しない。

<!-- SOURCE_END 4: docs/governance/phase_10_original_r_and_d_system_catalog_20260721162242.md -->

---

<!-- SOURCE_BEGIN 5: docs/governance/runtime_governance_20260718174637.md -->

### Source 5: `docs/governance/runtime_governance_20260718174637.md`

- History Target: `docs/project/phases/phase_1/history/governance/runtime_governance_20260718174637.md`
- Source SHA-512: `4a5c1af261e2934959da34cd08f6e5cb021f9e88f8ad68173baa5bd6caa0ab02f60910a42ac284df7575e64edb9728bf63a5950f907546c4d3061cc5c09e2ecf`
- Source Size: `9559` bytes

# Runtime Governance 設計基準

- 文書ID: `runtime_governance`
- 状態: `current`
- 作成日時: `2026-07-18 17:46:37 JST`
- 更新日時: `2026-07-18 17:46:37 JST`
- 対象: ARGD、DAGD、Governance Runtime、将来GD
- 正本言語: 日本語
- 上位要件: [project_requirements_20260718174637.md](../history/requirements/project_requirements_20260718174637.md)

## 1. 中核方針

ARGD／DAGDを巨大なSystem Promptとしてそのまま貼るだけにはしない。

Modelの推論呼び出しを所有・制御する、Model非依存のRuntime Governance Layerとして実装する。

初期版ではModel内部のWeight、Attention、Hidden State、Internal Activationへ直接介入しない。

介入対象はModel直外のInference Control Planeである。

## 2. 実行構造

```text
Governance Definition
        ↓
Governance Compiler
        ↓
Governance Plan
        ↓
┌── Runtime Governance Layer ──┐
│ 入力・前提・文脈の検査       │
│ Prompt / Context構築          │
│ Generation Config制御         │
│ Decoding制御                  │
│ Streaming監視                 │
│ 出力監査                      │
│ 修復・再生成                  │
│ Governance State更新          │
│ Audit Log生成                 │
└─────────────────────────────┘
        ↓
Model Adapter
        ↓
Pretrained Model
```

## 3. 介入候補

- Input Interpretation
- Premise固定
- Context選択
- Prompt構築
- System Message構築
- Temperature
- Top-p
- Seed
- Max Tokens
- Stop Sequence
- Logit Bias
- 禁止Token
- Grammar
- JSON Schema
- Streaming中の停止
- 複数候補生成
- 候補評価
- Output監査
- Repair
- Re-fix
- Rebind
- Enforce
- Reinitialize
- Tool Permissionとの接続
- Governance State記録
- Audit Log生成

## 4. ModelとGovernance Definitionの独立性

- ModelはARGD／DAGDの存在を知らなくてよい
- ARGD／DAGDは特定Modelを前提にしない
- ModelとGovernance Definitionを実行時に接続する
- Modelを交換可能にする
- Governance Definitionを交換可能にする
- Governance無効化による比較実行を将来可能にする
- Model変更でGovernance Coreを変更しない
- Governance変更でModel Adapterを変更しない
- 組み合わせをAudit Logへ記録する
- Capability不足を黙って無視しない

初期版ではModelとGovernance Definitionを設定で手動選択する。

自動Routingは将来Scopeとする。

## 5. 参照Definition

原文JSON：

```text
/path/to/private-definition-source/
思想_脳内構造_理論系/
モジュール型LLMランタイム統治プロンプト設計/
宣言型LLM統治プロンプト設計/
GitHub公開関連/部品類_20260603/構文置き場_20260603/元構文_20260623/
argd_v0.3.1_en_dagd_v0.4.4_en.json
```

確認結果：

```text
形式        : Valid JSON
サイズ      : 約69KB
行数        : 約1,793行
Top Level   : argd / dagd
ARGD        : v0.3.1
DAGD        : v0.4.4
DAGD状態    : EXPERIMENTAL
Author      : Nazuna Research
License     : CC-BY-SA-4.0
```

原文JSONをDefinitionの正本とする。

Projectでは内容Hash単位の不変Snapshotとして保存・参照し、Turnごとに全文を複製しない。

## 6. ARGD

```text
Axiomatic Reasoning Governance Definition
```

主な6領域：

1. Input Interpretation／Premise
2. Context Priority
3. Contradiction／Information Insufficiency
4. Reasoning Quality
5. Structural Expression
6. Efficiency／Repair

主な統治内容：

- 入力構造保持
- 前提固定
- 決定事項固定
- 無断要約禁止
- Context混在防止
- 矛盾未解決時の停止
- 情報不足を推測で埋めない
- 複数仮説保持
- Fact／Observation／Inference／Assumption／Evaluationの分離
- Sycophancy防止
- Refutation検討
- Alternative Hypothesis検討
- Drift検出
- Repair
- Re-fix
- 過剰な確認の抑制
- 表現精度
- 対話効率

主なTag：

```text
KEEP
FIXD
ANTI
FALS
LEAD
TONE
REPR
```

ARGD全体を毎回Promptへ投入せず、TaskとExecution Profileに必要な部分をCompileする。

## 7. DAGD

```text
Declarative AI Governance Definition
```

DAGD v0.4.4は`EXPERIMENTAL`。

含まれる構造：

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

Governance操作：

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

State／Score：

- 0～100
- Stable
- Acceptable with Minor Drift
- Degraded
- Unstable
- Low
- Moderate
- High
- Critical

Dimension候補：

- Context Preservation
- Premise Preservation
- Scope Definition
- Reasoning Integrity
- Expression Precision
- Dialog Efficiency
- Self Repair

## 8. Internal Module

```text
ARGD / DAGD
  ├─ Definition Repository
  ├─ Definition Loader
  ├─ Definition Validator
  ├─ Governance Compiler
  ├─ Prompt Policy
  ├─ Runtime Rule Engine
  ├─ Audit Evaluator
  ├─ State Machine
  ├─ Action Resolver
  ├─ Repair Engine
  └─ Status Reporter
```

役割分担：

- ARGDの必要部分をPromptへCompileする
- DAGDのState遷移とAction判定はPython側を中心とする
- Rule Basedで判定できる項目はLLMへ投げない
- 意味的評価が必要な項目だけLLMを利用する
- Definition、Rule、State、ActionをAudit Logへ記録する
- Definition内容と実行負荷を分離する

## 9. Governance Execution Profile

### Core

- 必須Rule
- Rule Based中心
- 追加LLM呼び出し最小
- M2 Pro・16GBで常用できることを重視

### Standard

- Core
- 回答後監査
- 主要Dimension
- 必要時の軽量Repair

### Full

- 回答前後監査
- 詳細Score
- Severity
- Repair Loop
- Rebind
- Enforce
- Reinitialize
- 詳細Status

Fullが重い場合はExecution Profileだけでなく、軽量Definitionを交換可能な別Definitionとして検討する。

## 10. 未決事項

- Deviation検出方法
- Dimension Score計算
- Weight
- Total Score
- Rule Based評価とLLM評価の統合
- 複数Actionの競合解決
- State Machine正規化
- Repair成功判定
- Capability不足時の動作
- Context Overflow
- 無断要約禁止とContext上限の両立
- Audit回数
- 同期Audit／非同期Audit
- Model Self Auditの信頼性
- Judgeの信頼性
- Repair Loop最大回数
- Infinite Repair防止
- Streaming中のDeviation検出
- GuardとGovernanceの競合
- User指示とGovernanceの関係
- 上位System Policyとの優先関係

確認済みのDefinition整合課題：

- `rebinding_then_active`等が主要State一覧と一致しない
- `expression_precision_score`の個別Action規則が不足
- Critical一回と複数回でReinjection条件が揺れている
- 複数系統から発火したActionの最終解決規則が必要

原Definitionを黙って改変せず、Compiler、Normalizer、Action Resolver側の解釈仕様として明示する。

## 11. 将来のGD構造

```text
Foundational Governance
  ├─ ARGD：推論規律
  └─ DAGD：宣言型Runtime統治

Optional Governance Extensions
  ├─ AISGD：AI Security／Guardrail
  ├─ AAGD：Agent実行過程
  ├─ MPGD：Model Policy
  ├─ DAAGD：権限・責任・承認状態
  └─ その他のDomain GD

Future Orchestration
  └─ CDOGD：GD選択、抑制、弱化、引き渡し、競合解決
```

## 12. 将来の16GD

- CDOGD：GD横断Orchestration
- SPPGD：戦略計画・優先順位
- DAAGD：判断権限・責任・承認状態
- SDAGD：戦略判断監査
- SDMRGD：戦略監査のMeta Review
- DSGD：Data Science
- ACRGD：成果物構成・Review
- AAGD：Agentic AI
- AISGD：AI Security
- MPGD：Model Policy
- DCAGD：開発相談
- PMOGD：Project Management
- AIRGD：AI Research
- AIAGD：AI Architecture
- SEGD：Software Engineering
- OMRGD：運用・保守・信頼性

初期版では実装しない。

### AISGD候補Scope

- Prompt Injection
- Jailbreak
- Secret
- Personal Information
- Tool悪用
- 権限混同
- Agent間攻撃

### AAGD候補Scope

- Planning
- Tool Call
- Side Effect
- Work State
- Memory
- Handoff
- Completion Check

### MPGD候補Scope

- Policy識別
- 適用範囲
- 優先関係
- 矛盾
- 例外
- 過剰拒否
- 過少拒否
- 判断履歴

### DAAGD候補Scope

- 既存権限
- 委任
- 承認
- 責任状態
- 実行許可条件の解釈

重要な制約：

- AAGDは実行許可を生成しない
- MPGDは存在しないPolicyを生成しない
- DAAGDは外部に存在しない権限を生成しない
- 上位System Policyを上書きしない

## 13. 将来の汎用Hook

```text
Governance Registry
    ↓
Governance Definition
    ↓
Governance Compiler
    ↓
Governance Instance
    ↓
Standard Governance Result
```

標準化候補：

- Definition ID
- Version
- Hash
- Domain
- Activation Condition
- Required Capability
- Input Scope
- Output Scope
- Priority
- Dependencies
- Conflicts
- Evaluation Result
- Recommended Action
- Executed Action
- Governance State

運用原則：

- 必要なGDだけLazy Load
- Taskに必要なGDのみActivation
- 必要なRuleだけCompile
- 無関係なGDはInactive
- Rule Based処理を優先
- Modelへ渡す内容を最小化
- 有効GDとRuleをAudit Logへ記録

初期版では複数GD Registry、自動合成、競合解決、CDOGD Routingを実装しない。

<!-- SOURCE_END 5: docs/governance/runtime_governance_20260718174637.md -->

---

