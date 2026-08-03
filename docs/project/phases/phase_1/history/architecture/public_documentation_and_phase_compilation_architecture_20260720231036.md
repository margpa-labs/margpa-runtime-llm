# Public Documentation／Phase Compilation Architecture

- 文書ID: `public_documentation_and_phase_compilation_architecture`
- 状態: `accepted_reservation`
- 作成日時: `2026-07-20 23:10:36 JST`
- 更新日時: `2026-07-20 23:10:36 JST`
- Snapshot: `20260720231036`
- 作成担当: 設計者役担当Task
- 実施予定担当: 対外Docs役
- 正本言語: 日本語
- Requirements: [Lossless Compilation要件](../requirements/lossless_phase_document_compilation_requirements_20260720231036.md)
- supersedes: なし

## 1. 目的

GitHub閲覧者向けPublic Docsと、Task再作成用のPhase単位Lossless Handoffを分離しつつ、Phase完了時に同じSource Snapshotから生成する。

## 2. Proposed Layout

Phase 1-exで確定・移行する候補構造：

```text
margpa-runtime-llm/
├─ README.md
├─ LICENSE
└─ docs/
   └─ public/
      ├─ overview_ja.md
      ├─ concept_ja.md
      ├─ roadmap_ja.md
      └─ phases/
         └─ phase_<id>_summary_ja.md
```

Lossless Compilationの物理配置、内部Docs History、Current Canonical Docs、Task HandoffのDirectoryはPhase 1-exで別途確定する。上記は現在のDirectoryを即時変更する指示ではない。

## 3. Language／Tone

| File | Language | Tone |
|---|---|---|
| `README.md` | 日本語、末尾に英語Abstract | 日本語本文は敬語 |
| `LICENSE` | 採用Licenseの公式原文を基本候補 | License原文に従う |
| `overview_ja.md` | 日本語 | 研究文書風 |
| `concept_ja.md` | 日本語 | 研究文書風 |
| `roadmap_ja.md` | 日本語 | 研究文書風 |
| `phase_<id>_summary_ja.md` | 日本語 | 現在のDocsと同等 |

将来必要になった場合、`overview_en.md`、`concept_en.md`、`roadmap_en.md`等を追加できるが、現時点では作成を要求しない。

## 4. README Requirements

最低限の候補：

- 何を作っているか
- Projectの目的／位置づけ
- 現在動作する範囲
- 未実装範囲／Known Limitations
- 対応Platform／Python／Backend
- 使用ModelとModelをRepositoryへ含めないこと
- Runtime Governance概要
- Architecture概要
- Setup／起動方法
- Lightning公開サイトURL
- Phase一覧、各概要、Complete／In Progress／Planned状態
- Documentation Entry Point
- Privacy／Security方針
- License／Attribution
- 最終SectionのEnglish Abstract

Lightning URLは実在する公開URLが確定してから記載し、架空URLを公開しない。

## 5. Overview

`overview_ja.md`はProject全体像、現在の到達点、構成要素、利用対象、動作環境、Evidence、Limitationsを研究文書風に記述する。

## 6. Concept

`concept_ja.md`は、Nazuna Research Governance LLM、Model-independent Runtime Governance、Canonical／Artifact分離、疎結合、交換可能性、研究装置としてのON／OFF比較等のConceptを日本語で記述する。

## 7. Roadmap

`roadmap_ja.md`はPhase一覧、各Phaseの目的、実装範囲、状態、依存、完了条件、将来候補を示す。実装済みと予定を混同しない。

## 8. Phase Document

Phase文書は人間向け説明だけでなく、Taskを作り直して即時再開できる粒度を持つ。

最低限：

- Phase目的
- User Requirements
- Accepted Requirements／ADR／Architecture
- 実装範囲／主要Artifact
- Model／Backend／Environment
- Config／Directory／Interface
- Test／Native Evidence
- Known Issues／Limitations
- Authorization Boundary
- Backup／Commit／Tag
- 次PhaseへのHandoff
- Source Inventory／Hash

Canonical Ruleを含む部分はLossless Compilation要件に従う。

## 9. License Boundary

`LICENSE`は英語原文を許容し、採用Licenseの公式Textを優先する。Code、ARGD／DAGD、Model、DependencyのLicenseを混同しない。

Project Code LicenseはPhase 1-exでユーザーが最終決定する。ARGD／DAGDのCC-BY-SA-4.0表記、Model License、第三者Attributionは別途明示する。

## 10. Git Editing Model

Public DocsはStable Filenameで更新する候補とする。Git Historyが差分を保持するため、Timestamp付きAppend-Only Docsと同じ規則を機械的に適用するとは限らない。

ただし、Git導入後のCurrent／History／Lossless Compilation／Public Docsの正本関係はPhase 1-exで明示的に決める。決定前に旧Docsを削除・移動しない。

## 11. Notification

Directory移行完了後、各担当Taskへ次を通知する。

- New Directory Tree
- Write／Read-only Authority
- Current Index／Canonical Entry Point
- Public Docs Ownership
- Phase Compilation Procedure
- Git Workflow
- Migration完了時点
- 旧Pathの扱い
- Rollback／Error Reporting

## 12. Authorization Boundary

本書はPhase 1-ex向けArchitecture予約である。現在のREADME／LICENSE作成、Directory作成・移動、Docs統合、Git操作、Lightning公開を許可しない。
