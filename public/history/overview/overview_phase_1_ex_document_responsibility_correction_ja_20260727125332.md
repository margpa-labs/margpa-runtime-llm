# MARGPA Runtime LLM 概要

```yaml
document_id: public_overview
status: current
language: ja
created_at: 2026-07-27 10:49:00 JST
updated_at: 2026-07-27 12:53:32 JST
owner: Nazuna Research
active_phase: phase_1_ex
```

## 1. Project概要

MARGPA Runtime LLMは、既存の言語モデルを交換可能な実行Componentとして扱い、その周囲にGovernance、評価、修復、証跡および実験のための共通Runtimeを構築する研究Projectである。

目的は、特定のModel、Backend、UIまたは単一のGovernance手法へ密結合したApplicationを作ることではない。ModelとGovernance Definitionの双方を交換可能にし、周辺Componentも明確なPortとContractを通じて接続する。

Project全体として目指すのは、AIの認知、評価、修復、実行、権限、責任、証跡および学習に関係する構成要素を、分解、交換、比較、監査およびRollback可能にするGovernance実行・実験基盤である。

## 2. 背景と対象問題

言語モデルを利用するSystemでは、次の要素が一つのApplication、Framework、PromptまたはModel判断へ集中しやすい。

- Modelの選択と実行
- Contextと生成条件
- PolicyとGuardrail
- 評価とJudge
- Repairと再生成
- AgentとTool実行
- AuthorityとApproval
- LogとEvidence
- UIとDeployment

これらが密結合すると、Model変更のたびに周辺設計を作り直す、Governance変更の影響範囲を特定できない、評価と実行権限が混同される、構成差を再現できない、Failure時に原因と責任境界を追跡できない、といった問題が生じる。

MARGPA Runtime LLMは、各責務を分けたうえで共通Contractへ接続し、何を有効化し、何を観測し、何が介入し、どのEvidenceが残ったかを明示できる構造を作る。

## 3. Projectの位置付け

本Projectは、独自の基盤Modelを事前学習したと主張するものではない。また、単一の安全Filter、Prompt Template、Chat UI、Agent Frameworkまたは監査Log製品でもない。

事前学習済みModelをRuntimeの一部として利用しながら、その外側に次の能力を段階的に成立させる。

```text
Model-independent Execution
  → Observable Runtime
  → Governance Definition Platform
  → Distributed Governance
  → Evaluation／Repair
  → Evidence／Audit
  → Reproducible Experimentation
  → Governed AI Lifecycle
```

個々の能力は独立Moduleとして設計し、未搭載のModuleが存在してもCore Runtimeを成立させられる構造を維持する。

## 4. 全体構造

全体は、概念上次の領域へ分ける。

```text
Interface／Application
  ├─ User Interaction
  ├─ Configuration
  └─ Status／Explanation

Execution Pipeline
  ├─ Input／Context
  ├─ Retrieval
  ├─ Guardrail／Policy／Authority
  ├─ Agent／Tool
  ├─ Judge
  ├─ Main Model
  └─ Output／Repair

Governance Control Plane
  ├─ Definition Provider／Registry
  ├─ Validation／Normalization
  ├─ Compiler／Binding
  ├─ Rule Selection
  ├─ State／Budget
  ├─ Evidence／Evaluation
  ├─ Conflict Resolution
  └─ Action Resolution

Infrastructure Ports
  ├─ Model Backend
  ├─ Storage
  ├─ Evidence Ledger
  ├─ External Governance Provider
  └─ Deployment
```

すべてを一つの巨大なGovernance Promptで処理せず、共有Control Planeと各遷移点の軽量なGovernance Pointを組み合わせる。各Pointは、その場所に必要なRule、State、CapabilityおよびBudgetだけを受け取る。

## 5. Governance Definitionを第一級Componentにする

Governance Definitionは、人間が読むPolicy文書として保存するだけでなく、Runtimeが出所、Identity、Version、Hash、Schema、Capability、Activation、DependencyおよびConflictを検証し、実行計画へ変換できる対象として扱う。

概念上の処理経路は次のとおりである。

```text
Provider
  → Manifest
  → Descriptor
  → Trusted Adapter
  → Normalized IR
  → Compiler
  → Compiled Plan
  → Binding
  → Runtime Execution
```

特定のDefinition名をCoreへHardcodeしない。既知Definitionが存在しない状態、Definitionが0件の状態、未知の名前やSchemaを持つDefinition、Custom Providerを正式な入力状態として扱う。対応不能なDefinitionを黙って実行せず、その状態と理由をEvidenceへ残す。

## 6. 設計原則

### 6.1 疎結合

Model、Backend、Configuration、Governance Definition、評価、Repair、Evidence、InterfaceおよびDeploymentを分離する。Framework固有処理はAdapter境界へ閉じ込め、Application Coreへ直接依存させない。

### 6.2 単一責任

評価するComponent、権限を解決するComponent、実行するComponent、Evidenceを保存するComponentを同一視しない。

### 6.3 交換可能性

特定のModelやDefinitionを交換しても、他のCore Componentを作り直さずに済むContractを維持する。

### 6.4 Capabilityの明示

利用可能な機能を推測せず、各AdapterとProviderがCapabilityを申告する。Capability不足はWarning、Degraded、FallbackまたはRefusalとして明示する。

### 6.5 Fail-closed

Authority、Permission、Binding、Integrityまたは対象Scopeが不明な場合、都合のよい推測で実行許可を作らない。

### 6.6 証跡と復元

結果だけでなく、構成、入力、Model、Definition、Rule、Action、評価、修復および制約を追跡可能にする。Project開発でも正本、History、Manifest、Hash、HandoffおよびRecoveryを保持する。

## 7. Authorityに関する不変条件

何かが存在、登録または評価された事実だけでは、真実性、Authorityまたは実行許可を獲得しない。

```text
存在
≠ 登録
≠ 検証
≠ 有効化
≠ 評価
≠ 判断
≠ 権限
≠ 承認
≠ 実行
≠ 責任
```

Governance Definitionが読み込まれてもActiveとは限らない。Judgeは評価できても最終Authorityとは限らない。Agent Governanceは実行過程を扱っても新しいPermissionを生成しない。Research向け設定を表示しても権限昇格にはならない。

この分離は、認知、評価、権限、実行および責任が一つのModelやComponentへ集中することを防ぐための中核原則である。

## 8. 比較可能な研究基盤

各ComponentとGovernanceは、構成差を比較できるよう独立して制御する。Governanceでは次のModeを区別する。

```text
off      : 実行しない
observe  : 評価とEvidence記録だけを行う
enforce  : 許可されたActionの範囲で介入する
```

同じInput、Model、Seed、Config、DefinitionおよびArtifactを用い、介入なし、観測のみ、介入ありを比較する。品質だけでなく、Latency、Token、Resource Cost、Failure、Repair、VarianceおよびKnown Limitationを関連付ける。

定量計算と定性計算は分離して保持し、異質な評価を根拠なく単一Scoreへ統合しない。評価条件、測定限界、判断主体および再現条件をEvidenceとして残す。

## 9. EvidenceとProject Continuity

Runtimeでは、Input、Output、Context、Model Provenance、Config、Definition、Compiled Plan、Binding、Rule、Action、評価、RepairおよびIntegrity情報を構造化して関連付ける。

生のChain of Thoughtを正本として保存するのではなく、System Trace、高水準の説明概要、適用Rule、根拠、UncertaintyおよびLimitを区別する。

Project運用でも同じ原則を適用する。

- Current Canonical
- Phase単位の正本
- Shared Rule
- Public文書
- Stable／History
- Source Inventory
- Before／After Snapshot
- SHA-512
- Lossless Compilation
- Handoff／Review
- Rollback／Recovery

長期化したTaskが停止または再作成されても、会話記憶へ依存せずDocsから現在状態を復元できることを重視する。

## 10. 現在地

Phase 1では、後続能力を載せるための最初の交換可能なRuntime契約を成立させた。現在はPhase 1-exとして、初回公開前の文書、証跡、Authority、Recovery、利用条件および運用境界を整備している。

現在の画面や機能はProject全体の完成像ではない。Phaseごとの実装済み範囲、未実装範囲、依存順序および将来構想は、[Roadmap](roadmap_ja.md)を唯一の進捗正本とする。

## 11. 本Projectが重視しない短絡

次の状態をProjectの完成とは扱わない。

- Modelが一度応答しただけの状態
- UI上に設定項目が存在するだけの状態
- Governance文書をSystem Promptへ貼り付けただけの状態
- Logが保存されるだけで再検証できない状態
- JudgeがScoreを返すだけでAuthority境界がない状態
- Layer数が多いだけで構成差を比較できない状態
- 疎結合を主張するだけで交換Testがない状態

構造、Runtime Contract、Evidence、Failure、Recoveryおよび比較結果が対応して初めて、対象能力が成立したと判断する。

## 12. Public文書の読み方

本概要はProject全体の目的、対象問題、構造および原則を説明する。

- [コンセプト](concept_ja.md)：Projectの思想、不変条件および研究上の意味
- [Roadmap](roadmap_ja.md)：Phase別の実装状態、依存順序および将来構想
- [要件定義書](../project/current/requirements/requirements_specification_ja.md)：機能要件・非機能要件
- [全体設計書](../project/current/architecture/system_architecture_ja.md)：System全体の構成
- [基本設計書](../project/current/architecture/basic_design_ja.md)：Component、Contractおよび主要Flow
- [Runtime Governance仕様書](../project/current/governance/runtime_governance_specification_ja.md)：Governance実行境界

利用条件と免責は、Rootの`LICENSE`、`TERMS_OF_USE.md`および`NOTICE.md`を正本とする。

## 13. 境界

本Projectは研究・検証中であり、現在の実装がRoadmap上の全能力を備えているとは扱わない。ConceptとOverviewは方向性と構造を説明し、実装状態はRoadmap、詳細な要件と設計はCurrent Canonicalを参照する。

動作、互換性、正確性、安全性、完全性、可用性および特定目的への適合性を保証しない。
