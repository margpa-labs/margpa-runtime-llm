# Runtime Governance 設計基準

- 文書ID: `runtime_governance`
- 状態: `current`
- 作成日時: `2026-07-18 17:46:37 JST`
- 更新日時: `2026-07-18 17:46:37 JST`
- 対象: ARGD、DAGD、Governance Runtime、将来GD
- 正本言語: 日本語
- 上位要件: [project_requirements_20260718174637.md](../requirements/project_requirements_20260718174637.md)

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
