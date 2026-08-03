# MARGPA Runtime LLM Documentation Index

- 文書ID: `documentation_index`
- 状態: `current`
- 作成日時: `2026-07-22 02:39:08 JST`
- 更新日時: `2026-07-22 02:39:08 JST`
- Snapshot: `20260722023908`
- 作成担当: 設計者役担当Task
- 正本言語: 日本語
- supersedes: `documentation_index_20260721191915.md`

## 1. Current Position

```text
Public Author／Research Name           : Nazuna Research
Phase 1-G                              : Accepted
Phase 1-H                              : Accepted
User Mac Acceptance                    : Waiting
Phase 1-F／1-G／1-H Lightning Native   : Deferred／Batch Gate
Phase 1 Overall Completion             : Not Declared
Phase 1-ex                             : Accepted Reservation／Not Started
Public Roadmap                         : Created／Current
Docs Writer until Phase 1-ex Complete  : Current Designer Task Only
Initial GitHub Publication             : Deferred until Phase 1-ex completion
Git                                     : Not Initialized
```

## 2. Snapshot Resolution

Phase 1-H Accepted Evidence、Current User Manual、Documentation単一Writer、README Roadmap最優先要件は[documentation_index_20260721191915.md](documentation_index_20260721191915.md)から継承する。

本Snapshotは、ユーザーの明示指示によりPublic Roadmapを前倒し作成したことを記録する。

## 3. Current Public Roadmap

[roadmap_ja.md](public/roadmap_ja.md)

本Roadmapは、現在の最小Web Previewだけでは伝わらないProject全体像を、次の進展として公開する中核文書である。

```text
Portable Model Runtime
  → Cross-platform Runtime
  → Conversation Continuity／Component Switchboard
  → Audit／Evidence／Generic Definition Platform
  → MARGPA Main Governance
  → Guardrail／Policy／Authority Governance
  → Judge／Evaluation／Repair／Observability
  → RAG／Data Governance
  → Agent／Tool／Memory／Handoff Governance
  → Experiment／Multi-Governance Platform
  → Hardening／Cloud Scale／External Original R&D Integration
```

## 4. Roadmap Core Message

MARGPA Runtime LLMは単なるLocal LLM、Chat UI、Model Wrapperを最終目的としない。

Model、Guardrail、Policy、Judge、Repair、RAG、Agent、Tool、Memory、Audit、Governance Definitionを独立Componentとして扱い、共有Governance Control Planeと分散Governance Pointを通じて、構成差の効果とCostを再現可能に比較するRuntime Governance型AI研究基盤を目指す。

## 5. Phase State Accuracy

Roadmapは、次を明示的に分離している。

- Complete／Accepted
- Repository Accepted
- Validation Waiting
- Accepted Reservation
- Planned
- Future R&D

Phase 1-G／1-HはAcceptedとして記載する。一方、Lightning Native Gate、User Acceptance、Cross-environment Final Review、Phase 1 Completion Declarationは未完了として記載する。

## 6. Governance Architecture Represented

- Governance Definition 0件Baseline
- 未知GD／未知Schema／任意JSON
- 特定GD名のCore Hard-code禁止
- Immutable Definition Source＋Adjustment＋Binding
- 共有Governance Control Plane＋分散Governance Point
- Functional ComponentとGovernanceの独立切替
- `off／observe／enforce`
- Deterministic Rule First
- Semantic Evaluation Budget
- Evidence／Action／Authority Boundary
- CDOGD非必須／Custom Orchestrator交換性

## 7. Original R&D Public Boundary

RoadmapはPhase 10に、公開決定済みの次の名称、研究領域、概要、接続方向だけを記載する。

- EASA
- DLAGSA
- OCILNS

独自Algorithm、内部Protocol、改竄耐性の具体方式、非公開実装情報は記載しない。

## 8. Scoped Authorization

既存Phase 1-ex要件ではPublic Docs生成をPhase 1-ex開始後としていたが、ユーザーは本TurnでRoadmapだけの前倒し作成を明示的に許可した。

この許可は`docs/public/roadmap_ja.md`の作成と、そのIndex反映だけを対象とする。

次を自動許可しない。

- README、Overview、Concept、LICENSE、CITATION、NOTICEの作成
- Phase 1-ex開始
- Docs Directory Migration
- Lossless Compilation実行
- Git初期化、Commit、Tag、Push
- GitHub公開
- Lightning外部操作
- Future Phase実装

## 9. Next Gate

```text
Public Roadmap Created
  → User Review
  → Phase 1 Current Gate継続
  → Lightning Native／Public URL Validation
  → Cross-environment Final Review
  → Phase 1 Completion／Backup
  → Phase 1-ex
```

## 10. Append-Only

前Indexと既存Roadmap正本を変更せず、安定File名のPublic Roadmapと新TimestampのIndexを追加した。Public RoadmapはPhase 1-exでGit履歴へ移行予定のStable Derived Documentとして扱う。
