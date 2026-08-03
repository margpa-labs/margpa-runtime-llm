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
- Requirements: [phase_1_ex_external_r_and_d_publication_and_integration_requirements_20260721162242.md](../requirements/phase_1_ex_external_r_and_d_publication_and_integration_requirements_20260721162242.md)
- Architecture: [phase_10_external_r_and_d_integration_architecture_20260721162242.md](../architecture/phase_10_external_r_and_d_integration_architecture_20260721162242.md)
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
