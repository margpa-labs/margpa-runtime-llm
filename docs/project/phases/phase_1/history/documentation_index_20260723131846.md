# MARGPA Runtime LLM Documentation Index

- 文書ID: `documentation_index`
- 状態: `current`
- 作成日時: `2026-07-23 13:18:46 JST`
- 更新日時: `2026-07-23 13:18:46 JST`
- Snapshot: `20260723131846`
- 作成担当: 設計者役担当Task
- 正本言語: 日本語
- supersedes: `documentation_index_20260723131526.md`

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
Future ML Extension                      : Added／Future Reservation
Quantitative Calculation Mode            : Added／Future Reservation
Qualitative Evaluation Mode              : Added／Future Reservation
Docs Writer until Phase 1-ex Complete    : Current Designer Task Only
Initial GitHub Publication               : Deferred until Phase 1-ex completion
Git                                      : Not Initialized
```

## 2. Snapshot Resolution

Phase 1-H Accepted Evidence、Current User Manual、Documentation単一Writer、README Roadmap最優先要件およびFuture ML Extensionは、[documentation_index_20260723131526.md](documentation_index_20260723131526.md)から継承する。

本Snapshotは、ユーザーの訂正により、Future機能の直前Snapshotにおける旧称を「定量計算モード」として正規化したことを記録する。

## 3. Current Public Roadmap

[roadmap_ja.md](public/roadmap_ja.md)

変更前の初期Roadmap Snapshot：

[roadmap_ja_20260722023908.md](public/history/roadmap_ja_20260722023908.md)

## 4. Future ML／Evaluation Modes

Phase 10のFuture Trackに、次を予約する。

```text
ML／Training／Adaptation
定量計算モード : OFF／ON
定性評価モード : OFF／ON

Mode:
  quantitative_calculation
  qualitative
  combined
  off
```

`combined`は、定量計算結果と定性評価結果を別Evidenceとして保持したうえで併用する。両者を無条件に単一Scoreへ圧縮しない。

## 5. Conceptual Configuration

```toml
[components.machine_learning]
enabled = false

[components.evaluation]
enabled = true
mode = "combined"

[components.evaluation.quantitative_calculation]
enabled = true

[components.evaluation.qualitative]
enabled = true
```

最終Key／Schemaは対象Phaseで確定する。上記名称をCoreへHard-codeする指示ではない。

## 6. Validation Boundary

- `combined`と各Switchの矛盾を黙って自動修正しない。
- 両方OFFの場合、計算・評価済みと記録しない。
- 定量計算モードはDataset、Metric、Threshold、Sample、Seed、Versionを記録する。
- 定性評価モードはRubric、Evaluator、Version、Scopeを記録する。
- Judge結果をGround Truthまたは最終Authorityと同一視しない。
- ML Component、Training Pipeline、定量計算モード、定性評価モードは個別にON／OFF可能とする。
- OFF時は対象処理、Training、Model Call、Artifact Write、Side Effectを行わない。

## 7. Scoped Authorization

本更新はPublic Roadmapの用語訂正と最新Index作成だけを対象とする。

次を自動許可しない。

- ML／Training／Fine-tuning／LoRA実装
- Dataset取得／登録
- Model Download／Weight更新
- Config実装
- Phase 1-ex開始
- Git／GitHub操作
- Lightning外部操作
- Future R&D System実装

## 8. Next Gate

```text
Future Mode Terminology Corrected
  → Phase 1 Current Gate継続
  → Lightning Native／Public URL Validation
  → Cross-environment Final Review
  → Phase 1 Completion／Backup
  → Phase 1-ex
```

## 9. Append-Only

旧Indexは変更せず保持する。新Timestampの本Indexを最新とする。
