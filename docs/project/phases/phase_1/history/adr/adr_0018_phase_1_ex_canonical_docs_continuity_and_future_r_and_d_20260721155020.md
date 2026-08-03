# ADR-0018 Phase 1-ex Canonical Docs／Continuity／Future R&D公開Hook

- 文書ID: `adr_0018_phase_1_ex_canonical_docs_continuity_and_future_r_and_d`
- 状態: `accepted_reservation`
- 作成日時: `2026-07-21 15:50:20 JST`
- 更新日時: `2026-07-21 15:50:20 JST`
- Snapshot: `20260721155020`
- Decision Owner: ユーザー
- 作成担当: 設計者役担当Task
- 正本言語: 日本語
- Requirements: [phase_1_ex_complete_operating_model_and_documentation_requirements_20260721155020.md](../requirements/phase_1_ex_complete_operating_model_and_documentation_requirements_20260721155020.md)
- supersedes: なし

## 1. Context

既存Docsは詳細EvidenceとTask間Communicationを高精度で保持する一方、File数とTimestamp系列が増え、Project全体の入口としては重くなっている。

GitHub閲覧者向けの説明と、Codex Taskを一から作り直して即時再開するための情報量も異なる。

また、本体完成後に別Taskで開発する独立R&D機構2件について、Coreへ依存を作らず、構想の存在と方向性だけを公開しておきたい。

## 2. Decision

Phase 1-exで次を作成する。

```text
docs/requirements_specification_ja.md
docs/system_architecture_ja.md
docs/technology_selection_ja.md
docs/basic_design_ja.md
docs/runtime_governance_specification_ja.md
docs/project_continuity/project_continuity_master_ja.md
```

最初の5文書は公開可能なStable Canonical Technical Docsとする。Project Continuity Masterも公開可能とし、Task再開に必要な情報をより広く統合する。

詳細設計書の網羅的作成は行わない。既存Granular Docsを保持し、将来必要なSubsystemだけ任意に追加する。

## 3. File／Language Decision

- File名とDirectory名は英語を使用する。
- 本文は日本語を正本とする。
- 日本語文書には`_ja`を付ける。
- Git移行後のStable DocsはTimestampを付けず、Git Historyで変更履歴を保持する。
- 既存Timestamp DocsとImmutable Compilationは保持する。

## 4. Continuity Decision

Project Continuity Masterは短い概要ではなく、Decision、Boundary、Current State、Known Issue、Next Gate、Task Authority、Source Mapを再開可能な粒度で保持する。

ただし公開Fileであるため、Secret、個人Path、Credential、実会話Log等を含めない。

## 5. Future R&D Decision

次をPhase 10の独立R&D Extensionとして予約する。

1. 例外認識型安全統治機構
2. 分散証跡型例外認識エージェント統治安全機構

両機構は別Project／別Taskで開発し、本体完成後に汎用Portを通じて疎結合統合する。

公開範囲：

- Roadmap：名称、研究領域、1から2行の概要
- System Architecture：接続位置だけ
- Project Continuity Master：提供済みの作業概念と統合方針
- Algorithm、実装方式、研究の核心：現時点では記載しない

## 6. Consequences

- 一般閲覧者、技術Review、Task再開の入口を分離できる。
- Git Historyと既存Append-only Evidenceを両立できる。
- Project全体を新Taskへ高精度で引き継げる。
- R&D構想の存在を先行公開しながら核心を保持できる。
- Stable Docsの更新時にCanonical Sourceとの整合Reviewが必要になる。
- Public DocsとContinuity Masterの重複を正本Mappingで管理する必要がある。

## 7. Authorization Boundary

本ADRはPhase 1-exのAccepted Reservationである。Stable Docs生成、Directory変更、Git操作、公開、Phase 10実装をまだ許可しない。
