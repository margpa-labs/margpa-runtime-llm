# MARGPA Runtime LLM Documentation Index

- 文書ID: `documentation_index`
- 状態: `current`
- 作成日時: `2026-07-25 16:47:39 JST`
- 更新日時: `2026-07-25 16:47:39 JST`
- Snapshot: `20260725164739`
- 作成担当: 設計者役担当Task
- 正本言語: 日本語
- supersedes: `documentation_index_20260725162648.md`

## 1. Current Position

```text
Public Author／Research Name             : Nazuna Research
Phase 1-G                                : Accepted
Phase 1-H                                : Accepted
User Mac Acceptance                      : Waiting
Phase 1-F／1-G／1-H Lightning Native     : Deferred／Batch Gate
Phase 1 Overall Completion               : Not Declared
Phase 1-ex                               : Accepted Reservation／Not Started
Public Roadmap                           : Updated／Current
Public Documentation Corpus              : Added／Phase 1-ex Reservation
Project Documentation Explainer          : Added／Phase 2 Optional Reservation
Full RAG                                 : Phase 7 Planned
LLM Validation／Evaluation Design        : Phase 9 Reserved
Responsive UI／Multi-device Experience   : Future Phase Reserved
Docs Writer until Phase 1-ex Complete    : Current Designer Task Only
Initial GitHub Publication               : Deferred until Phase 1-ex completion
Git                                      : Not Initialized
```

## 2. Snapshot Resolution

Phase 1-H Accepted Evidence、Current User Manual、Documentation単一Writer、Phase 1-ex Docs言語／Filename Policy、公開免責、ON／OFF留意事項およびLLM動作検証／評価設計は、[documentation_index_20260725162648.md](documentation_index_20260725162648.md)から継承する。

本Snapshotは、Public Documentation Corpus、軽量Project Documentation ExplainerおよびPhase 7 Full RAGへの拡張境界を追加したことを記録する。

## 3. Preliminary Repository Observation

2026-07-25時点のRead-only Preliminary Scan：

```text
docs/ File Count             : 264
docs/ Markdown Count         : 262
docs/ Approximate Size       : 2.7 MB
Private Key Pattern          : Not Detected
Common API Token Pattern     : Not Detected
Identifier／Local Path Files : 8
docs/public Markdown         : Relevant Pattern Not Detected
```

これは公開承認または完全なSecret Scanを意味しない。Phase 1-exで対象Snapshotを固定し、改めてPrivacy、Secret、PathおよびPublic Allowlistを検証する。

## 4. Corpus Boundary

`docs/`全体を無差別にCorpusへ投入しない。

Default Corpus候補：

- GitHub公開Allowlistに含まれる日本語正本`*_ja.md`
- 必要な慣例名Public Document
- Current Stateの文書

Default除外：

- Phase統合前のHandoff／Status／Review／Index
- Superseded Snapshot
- Local Path／旧識別情報／非公開URLを含む文書
- Markdown以外の不要File

Corpus ManifestへPath、Title、Language、State、Snapshot、Size、SHA-512を記録する。

## 5. Project Documentation Explainer

Phase 2のOptional Early Featureとして予約する。

```text
Project Documentation Explainer : OFF／ON
```

目的：

- Project Overviewの説明
- Architectureの説明
- Roadmap／Current Statusの説明
- Governance Conceptの説明
- 公開Docsに基づく一問一答
- Multi-turn成立後のSource付きFollow-up

## 6. Lightweight Preview Boundary

- Embedding Model／Vector Storeを必須にしない。
- 日本語対応の軽量Lexical／Character N-gram Retriever候補を使用する。
- Adapter経由で交換可能にする。
- 関連ChunkだけをContext Budget内で注入する。
- Source Document／Section／Linkを表示する。
- Snapshot／Chunk／Score／Digest／Token Budgetを記録可能にする。
- Retrieval失敗、Corpus不足、Context切捨てを表示する。
- Retrieved TextをInstructionではなくSource Dataとして扱う。
- Docs内の命令表現をRuntime Instructionとして実行しない。
- Docsに基づく説明とModel推測を区別する。
- OFF時はIndex Load、Retrieval、Context Injectionおよび追加Writeを行わない。

## 7. README Claim Gate

未実装時：

> 将来、このProjectの公開Docsを参照し、LLM自身にProjectを説明させる機能を予定しています。

実装とAcceptance完了後：

> このProjectについて、公開Docsを参照しながらLLM自身に説明させることができます。

実装前に現在利用可能な機能として記載しない。実装後もSourceと既知の限界を併記する。

## 8. Full RAG Boundary

軽量ExplainerはFull RAGを代替しない。

Phase 7で追加する候補：

- Arbitrary Local Document Registration
- Embedding
- Vector Store
- Multiple Corpus
- Document Update／Delete
- Index Lifecycle
- RAG Governance
- Data Leakage／Prompt Injection Control

早期Previewを実装した場合も、同一Retrieval／Evidence PortからPhase 7へ拡張する。

## 9. Early Implementation Gate

一問一答だけでもProject説明Demoとして有意義である。

ただし早期実装は、次をすべて満たす場合に限る。

- Phase 1-exの公開正本とCorpus Manifestが完成している。
- Privacy／Secret／Path Scanが完了している。
- 新規Embedding ModelまたはVector Storeを要求しない。
- Model Adapter／Conversation CoreへRAG固有依存を漏らさない。
- Source表示、Context Budget、Failure State、OFF動作をTestできる。
- Phase 1完了、公開移行または主要Gateを遅延させない。

満たさない場合はPhase 2またはPhase 7へ延期する。

## 10. Scoped Authorization

本更新はPublic Roadmapへの要件予約と最新Index作成だけを対象とする。

次を自動許可しない。

- RAG／Retriever／Index実装
- Docs全体のCorpus登録
- READMEへの実装済みClaim追加
- Embedding Model／Dependency Download
- Phase 1-ex／Phase 2／Phase 7開始
- Git／GitHub操作
- 外部環境操作

## 11. Next Gate

```text
Project Documentation Explainer Reserved
  → Phase 1 Current Gate継続
  → Cross-environment／Local Final Review
  → Phase 1 Completion／Backup
  → Phase 1-ex Public Corpus Preparation
  → Optional Early Explainer Decision
```

## 12. Append-Only

旧Indexは変更せず保持する。新Timestampの本Indexを最新とする。
