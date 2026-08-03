# ADR-0019 Phase 10 Original R&D正式名称・公開範囲・個別Switch

- 文書ID: `adr_0019_phase_10_original_r_and_d_public_names_and_switches`
- 状態: `accepted_future_reservation`
- 作成日時: `2026-07-21 16:22:42 JST`
- 更新日時: `2026-07-21 16:22:42 JST`
- Snapshot: `20260721162242`
- Decision Owner: ユーザー
- 作成担当: 設計者役担当Task
- 正本言語: 日本語
- Requirements: [phase_1_ex_external_r_and_d_publication_and_integration_requirements_20260721162242.md](../requirements/phase_1_ex_external_r_and_d_publication_and_integration_requirements_20260721162242.md)
- Catalog: [phase_10_original_r_and_d_system_catalog_20260721162242.md](../governance/phase_10_original_r_and_d_system_catalog_20260721162242.md)
- supersedes: なし

## 1. Context

Phase 10の独立R&D構想は、これまで日本語名と研究方向だけを予約していた。ユーザーは略称と正式英名も先に公開し、OCILNSを同じ粒度で追加することを決定した。

## 2. Decision

公開名称を次で確定する。

```text
EASA
Exception Aware Safety Architecture
例外認識型安全統治機構

DLAGSA
Distributed LEA Agentic Governance & Safety Architecture
分散証跡型例外認識エージェント統治安全機構

OCILNS
Open Cognitive Interaction Ledger Network System
認知対話証跡台帳網
```

研究領域：

```text
EASA
  AI Safety Governance

DLAGSA
  Multi-Agent Governance,
  Distributed Accountability,
  and Safety Assurance

OCILNS
  Cognitive Interaction Provenance,
  Verifiable AI Systems,
  and Distributed Auditability
```

## 3. Public Disclosure

- Roadmapには名称、研究領域、1から2行の概要を記載する。
- System Architectureには接続位置とOptional性を記載する。
- Project Continuity Masterには作業概念をもう少し詳しく記載する。
- Algorithm、具体的改竄耐性方式、研究の核心は現在記載しない。

## 4. Config Decision

Phase 10統合時、EASA、DLAGSA、OCILNSをConfigで個別にON／OFF可能にする。DefaultはすべてOFFとする。

OFF時は対象SystemへのLoad、Call、Write、Side Effectを行わない。

## 5. Integration Decision

- EASA／DLAGSA：Generic External Governance Provider Port
- OCILNS：Generic Evidence Ledger Port
- Coreは3 Systemに直接依存しない。
- 3 Systemなしで本体は完全動作する。
- 各Systemは別Project／別Taskで開発する。

## 6. Consequences

- 構想の存在と研究方向を先行公開できる。
- MARGPA Runtime LLMの将来拡張位置を説明できる。
- Coreの疎結合と実験比較を維持できる。
- 正式名称の表記揺れを防止できる。
- 公開情報を増やす際は別DecisionとReviewが必要になる。

## 7. Authorization Boundary

本ADRは名称、公開範囲、将来Switchの予約を確定する。実装、Config変更、外部統合、核心公開を現在許可しない。
