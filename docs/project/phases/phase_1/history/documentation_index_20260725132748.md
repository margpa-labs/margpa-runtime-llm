# MARGPA Runtime LLM Documentation Index

- 文書ID: `documentation_index`
- 状態: `current`
- 作成日時: `2026-07-25 13:27:48 JST`
- 更新日時: `2026-07-25 13:27:48 JST`
- Snapshot: `20260725132748`
- 作成担当: 設計者役担当Task
- 正本言語: 日本語
- supersedes: `documentation_index_20260723134544.md`

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
Public Warranty Disclaimer               : Reserved for Phase 1-ex
Phase 4 UI Interaction Requirements      : Added／Planned
Future ML Extension                      : Added／Future Reservation
Quantitative Calculation Mode            : Added／Future Reservation
Qualitative Calculation Mode             : Added／Future Reservation
Research／Developer Mode                 : Added／Future Reservation
Docs Writer until Phase 1-ex Complete    : Current Designer Task Only
Initial GitHub Publication               : Deferred until Phase 1-ex completion
Git                                      : Not Initialized
```

## 2. Snapshot Resolution

Phase 1-H Accepted Evidence、Current User Manual、Documentation単一Writer、README Roadmap最優先要件、Future ML Extension、定量／定性計算モードおよび研究・開発者モードは、[documentation_index_20260723134544.md](documentation_index_20260723134544.md)から継承する。

本Snapshotは、Phase 1-exの公開免責要件とPhase 4のUI Interaction要件を追加したことを記録する。

## 3. Current Public Roadmap

[roadmap_ja.md](public/roadmap_ja.md)

変更前の初期Roadmap Snapshot：

[roadmap_ja_20260722023908.md](public/history/roadmap_ja_20260722023908.md)

## 4. Phase 1-ex Public Warranty Disclaimer

Phase 1-exで作成するREADMEと`LICENSE`の両方に、本Projectおよび配布物について一切の動作保証を行わない旨を明記する。

対象：

- 動作
- 可用性／継続性
- 互換性
- 正確性
- 安全性
- 特定目的への適合性
- Hardware／OS／Backend／Model／Dependency／外部Service／設定差

READMEには一般利用者向けの明確な日本語の注意書きを置く。`LICENSE`には採用利用条件と整合する正式な免責条項を置き、適用法令で認められる範囲の責任制限を明記する。

## 5. Phase 4 Local Folder Input

- 「ローカルフォルダを追加」ボタン
- Folderのドラッグ＆ドロップ（Drag and Drop）
- 対象、File数、Size、処理状態、Errorの表示
- 個別解除
- 未選択Pathの自動走査禁止
- 元Fileの変更、移動、削除禁止
- Hidden File、Secret、Symbolic Link、巨大Folder、未対応形式、重複FileのValidation
- 外部ServerへUploadする場合の事前表示
- Source Identity、Hash、採用範囲、処理結果のTraceability

Phase 4ではUI Entry Pointと安全な受渡し境界を設計し、本格的なIndex、Retrieval、Document更新はPhase 7のRAG責務と整合させる。

## 6. Phase 4 Generation Stop

- `Ctrl+C`を一般利用者向け停止方法にしない。
- 生成中に「停止」ボタンを表示する。
- Cooperative CancelをRuntimeへ伝播する。
- 受付、処理中、完了を区別する。
- 部分出力へ`cancelled`等の状態を関連づける。
- Cancel Eventと取得可能なEvidenceをAuditへ残す。

## 7. Phase 4 Send Interaction

長文や大きなContextではEnter単独送信による誤送信Riskが高まるため、Enter単独送信を固定仕様にしない。

検討候補：

- Enterで改行
- `Cmd+Enter`／`Ctrl+Enter`で送信
- 明示的な送信ボタン
- Enter送信の利用者設定
- IME変換確定中の誤送信防止
- Desktop／Mobile別操作
- 長文時の送信前状態の明確化

初期推奨候補は「Enterで改行、`Cmd+Enter`／`Ctrl+Enter`または送信ボタンで送信」とする。最終仕様はPhase 4で決定する。

## 8. Scoped Authorization

本更新はPublic Roadmapへの将来要件追加と最新Index作成だけを対象とする。

次を自動許可しない。

- README／LICENSEの現時点での作成または変更
- UI／Folder Input／RAG実装
- Phase 1-exまたはPhase 4の開始
- Git／GitHub操作
- Lightning外部操作

## 9. Next Gate

```text
Public Disclaimer／Phase 4 UI Requirements Reserved
  → Phase 1 Current Gate継続
  → Lightning Native／Public URL Validation
  → Cross-environment Final Review
  → Phase 1 Completion／Backup
  → Phase 1-ex
```

## 10. Append-Only

旧Indexは変更せず保持する。新Timestampの本Indexを最新とする。
