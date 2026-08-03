# Phase 1-ex External Original R&D 公開・統合予約要件

- 文書ID: `phase_1_ex_external_r_and_d_publication_and_integration_requirements`
- 状態: `accepted_reservation_not_started`
- 作成日時: `2026-07-21 16:22:42 JST`
- 更新日時: `2026-07-21 16:22:42 JST`
- Snapshot: `20260721162242`
- 作成担当: 設計者役担当Task
- Decision Owner: ユーザー
- 正本言語: 日本語
- Parent Requirements: [phase_1_ex_complete_operating_model_and_documentation_requirements_20260721155020.md](phase_1_ex_complete_operating_model_and_documentation_requirements_20260721155020.md)
- System Catalog: [phase_10_original_r_and_d_system_catalog_20260721162242.md](../governance/phase_10_original_r_and_d_system_catalog_20260721162242.md)
- Integration Architecture: [phase_10_external_r_and_d_integration_architecture_20260721162242.md](../architecture/phase_10_external_r_and_d_integration_architecture_20260721162242.md)
- supersedes: なし（Phase 1-ex外部R&D公開・統合系列の初回）

## 1. 目的

Phase 1-exで作成する公開DocsとProject Continuity Masterへ、MARGPA Runtime LLM本体完成後に統合予定の3つのオリジナルR&D Systemを、正式名称付きで記録する。

3 Systemは別Project／別Taskで独立開発し、Phase 10でMARGPA Runtime LLMへ疎結合統合する。構想の存在と方向性は公開し、Algorithm、実装方式、研究の核心は現在開示しない。

## 2. Official Public Names

### 2.1 EASA

```text
Abbreviation  : EASA
English Name  : Exception Aware Safety Architecture
Japanese Name : 例外認識型安全統治機構
Research Area : AI Safety Governance
```

### 2.2 DLAGSA

```text
Abbreviation  : DLAGSA
English Name  : Distributed LEA Agentic Governance & Safety Architecture
Japanese Name : 分散証跡型例外認識エージェント統治安全機構
Research Area : Multi-Agent Governance,
                Distributed Accountability,
                and Safety Assurance
```

`LEA`の正式な意味を本Project側で推測、展開、再定義しない。正式表記をそのまま保持する。

### 2.3 OCILNS

```text
Abbreviation  : OCILNS
English Name  : Open Cognitive Interaction Ledger Network System
Japanese Name : 認知対話証跡台帳網
Research Area : Cognitive Interaction Provenance,
                Verifiable AI Systems,
                and Distributed Auditability
```

## 3. Public Summary

### EASA

内部安全傾向、周辺安全制御、入力文脈、生成過程等の相互作用を対象とし、例外を含む複合的な安全挙動を統治する独立R&D Architecture。

### DLAGSA

複数の判断・実行・検証主体間における責任、委譲、例外、改竄耐性付き証跡、全体整合および異常時の安全側制御を扱う独立R&D Architecture。

### OCILNS

人、AI、Tool、外部System間の認知的対話出来事を、後から検証、参照、継承、監査できる改竄耐性付き証跡単位として扱い、長期、分岐、多Model、多Thread環境でも再接続可能性を維持する独立R&D System。

## 4. Phase 1-ex Documentation Placement

### `docs/public/roadmap_ja.md`

各Systemについて次だけを記載する。

- 略称
- 正式英名
- 日本語名
- 研究領域
- 1から2行のPublic Summary
- Phase 10／別Project／疎結合統合予定

### `docs/system_architecture_ja.md`

- 3 Systemの外部配置
- EASA／DLAGSA用Generic Governance Provider Port
- OCILNS用Generic Evidence Ledger Port
- Optional／Core非依存
- Configによる個別ON／OFF

内部Algorithmや使用技術は記載しない。

### `docs/runtime_governance_specification_ja.md`

- EASA／DLAGSAをExternal Governance Providerとして扱う将来Hook
- OCILNSをEvidence／Ledger Providerとして接続できる将来Hook
- Standard Result、Event、Evidence Reference、Mode、Failure Boundary
- 固有Systemなしでも本体が成立する原則

### `docs/project_continuity/project_continuity_master_ja.md`

Public Summaryより少し詳しく、次を記録する。

- EASAのSafety Stack作業概念
- DLAGSAの複数主体、責任、委譲、検証、例外、改竄耐性付き証跡
- OCILNSの認知対話、長期／分岐／多Model／多Thread、継承、検証、改変検知、Provider非依存
- 3 Systemの独立開発、Phase 10、疎結合、ON／OFF
- 未公開の核心を推測または補完しない境界

### その他のCanonical Docs

- `requirements_specification_ja.md`：将来拡張要件として名称と任意統合を記載
- `basic_design_ja.md`：Generic PortとConfig境界だけを記載
- `technology_selection_ja.md`：本体側Adapter要件だけ。各R&D Systemの内部使用技術は記載しない

## 5. Config ON／OFF Requirement

EASA、DLAGSA、OCILNSを個別にON／OFFできるConfigをPhase 10統合時に持つ。

概念例：

```toml
[extensions.providers.easa]
enabled = false

[extensions.providers.dlagsa]
enabled = false

[extensions.providers.ocilns]
enabled = false
```

最終SchemaはPhase 10で決定する。上記KeyをCore Codeへ固定する指示ではない。Registry／Provider Definitionから設定を解決できる構造を優先する。

Mandatory Behavior：

- Defaultは3 SystemともOFFとする。
- 3 Systemを独立してON／OFFできる。
- OFF時はLoad、Network Call、External Write、評価、Side Effectを行わない。
- ProviderまたはRequired Capabilityがない状態でONにした場合、黙って無視せずSafe Error／Degraded／Refusalを返す。
- Effective Config、Provider ID、Version、Hash、Enabled StateをAudit可能にする。
- 将来UIへ出す場合は一般設定ではなく研究開発者向け設定に置く。
- System本体とSystem用Governance Pointの有効状態を必要に応じて分離する。

EASA／DLAGSAは、ON時に`observe／enforce`等のGovernance Modeを別設定として持てる。ON／OFFと介入Modeを同一視しない。

OCILNSは証跡記録／検証Systemであり、Governance介入Modeを無理に適用しない。OCILNS固有のOperation ModeはPhase 10側要件で定義する。

## 6. OCILNS Scope Boundary

OCILNSの目的はLLM応答精度の直接向上ではない。

対象は、認知的作業に関わる対話出来事を、後から再参照、再検証、再接続、継承、監査可能な状態で維持することである。

候補Evidence：

- Input／Output
- Event順序／時刻
- Model／Provider情報
- 人の意図
- AI応答
- Tool実行
- 判断根拠の高水準記録
- 制約／前提／補助情報
- 未解決事項
- 継承対象
- 改変検知情報

OCILNSは特定LLM Provider、保存先、UI、Cloud環境へ依存しない。単一SHA-512 Digestだけに依存しない改竄耐性構成を予定するが、具体方式は本書へ記載しない。

## 7. Integration Boundary

```text
EASA／DLAGSA
  → External Governance Adapter
  → Generic External Governance Provider Port

OCILNS
  → Evidence Ledger Adapter
  → Generic Evidence Ledger Port

MARGPA Core
  → Generic Ports only
```

- 固有PackageなしでMARGPA Coreが動作する。
- 外部System FailureがCoreを無条件に停止させない。Fail PolicyをConfigで明示する。
- 存在しない権限やPolicyを生成しない。
- ProviderなしのBaseline比較が可能である。
- 外部SystemのVersion、Definition、Evidence ReferenceをAuditへ残せる。

## 8. Public／Non-public Boundary

公開する：

- 名称、略称、正式英名、日本語名
- 研究領域
- Public Summary
- Phase 10、別Project、疎結合統合
- Config個別ON／OFF予定
- Generic Port上の位置

現在記載しない：

- 独自Algorithm
- 内部Data Structure／Protocol
- 改竄耐性の具体方式
- 評価方式の核心
- 非公開Repository、Path、実装情報

## 9. Authorization Boundary

本書はPhase 1-exの記載予約とPhase 10の統合要件予約である。3 Systemの実装、Config変更、Adapter追加、外部接続、Algorithm公開を現在許可しない。
