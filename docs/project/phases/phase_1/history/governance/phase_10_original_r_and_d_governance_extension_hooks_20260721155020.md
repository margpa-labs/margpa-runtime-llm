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
- Phase 1-ex Requirements: [phase_1_ex_complete_operating_model_and_documentation_requirements_20260721155020.md](../requirements/phase_1_ex_complete_operating_model_and_documentation_requirements_20260721155020.md)
- Roadmap: [implementation_roadmap_20260721155020.md](../architecture/implementation_roadmap_20260721155020.md)
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
