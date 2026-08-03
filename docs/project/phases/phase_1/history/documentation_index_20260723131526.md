# MARGPA Runtime LLM Documentation Index

- 文書ID: `documentation_index`
- 状態: `current`
- 作成日時: `2026-07-23 13:15:26 JST`
- 更新日時: `2026-07-23 13:15:26 JST`
- Snapshot: `20260723131526`
- 作成担当: 設計者役担当Task
- 正本言語: 日本語
- supersedes: `documentation_index_20260722023908.md`

## 1. Current Position

```text
Public Author／Research Name           : Nazuna Research
Phase 1-G                              : Accepted
Phase 1-H                              : Accepted
User Mac Acceptance                    : Waiting
Phase 1-F／1-G／1-H Lightning Native   : Deferred／Batch Gate
Phase 1 Overall Completion             : Not Declared
Phase 1-ex                             : Accepted Reservation／Not Started
Public Roadmap                         : Updated／Current
Future ML Extension                    : Added／Future Reservation
Quantitative／Qualitative Evaluation   : Added／Future Reservation
Docs Writer until Phase 1-ex Complete  : Current Designer Task Only
Initial GitHub Publication             : Deferred until Phase 1-ex completion
Git                                     : Not Initialized
```

## 2. Snapshot Resolution

Phase 1-H Accepted Evidence、Current User Manual、Documentation単一Writer、README Roadmap最優先要件、Public Roadmapの基本構成は[documentation_index_20260722023908.md](documentation_index_20260722023908.md)から継承する。

本Snapshotは、ユーザーの明示指示によりPublic Roadmap後半へML追加と定量／定性評価設定の将来予約を追加したことを記録する。

## 3. Current Public Roadmap

[roadmap_ja.md](public/roadmap_ja.md)

Previous Roadmap Snapshot：

[roadmap_ja_20260722023908.md](public/history/roadmap_ja_20260722023908.md)

Previous Snapshot SHA-512：

```text
5585a1e5f11633306f645fe16fcf6a1311349d4bd359c3242491d9be88ad184dce722b5f6a57b5ff7e58543fbc661ec4de9fb293f7e7c7be1a1c079af948e344
```

## 4. Future ML Extension

Phase 10のFuture Trackへ、Machine Learning／Training／Adaptation Extensionを追加した。

対象候補：

- Dataset Registry／Version／Digest／Provenance
- Traditional Machine Learning
- Fine-tuning／LoRA等のAdaptation
- Training Run／Experiment Identity
- Candidate Model Artifact
- Baseline Comparison
- Model Promotion／Rollback
- Drift／Regression Detection

Current Phase 1ではWeight更新を行わない。将来もUser Conversationから暗黙にWeightを更新するOnline LearningをDefaultにしない。

## 5. Quantitative／Qualitative Evaluation

次を独立して設定可能にする将来要件をRoadmapへ追加した。

```text
定量評価 : OFF／ON
定性評価 : OFF／ON

Mode:
  quantitative
  qualitative
  combined
  off
```

`combined`は定量＋定性を意味する。両者を単一Scoreへ無条件に圧縮せず、別Evidenceとして保持する。

## 6. Configuration Boundary

Conceptual Structure：

```toml
[components.machine_learning]
enabled = false

[components.evaluation]
enabled = true
mode = "combined"

[components.evaluation.quantitative]
enabled = true

[components.evaluation.qualitative]
enabled = true
```

最終Key／Schemaは対象Phaseで確定する。ML、Training、定量評価、定性評価を個別にON／OFF可能とする。

## 7. Validation Boundary

- `combined`と各Switchの矛盾を黙って自動修正しない。
- 両評価OFFを評価済みと記録しない。
- 定量評価はDataset、Metric、Threshold、Sample、Seed、Versionを記録する。
- 定性評価はRubric、Evaluator、Version、Scopeを記録する。
- Judge結果をGround Truthまたは最終Authorityと同一視しない。
- Candidate Modelは評価と採用Gate前にCurrent Modelを上書きしない。
- OFF時は対象処理、Training、Model Call、Artifact Write、Side Effectを行わない。

## 8. Scoped Authorization

本更新はPublic RoadmapへのFuture Reservation追加とIndex反映だけを対象とする。

次を自動許可しない。

- ML／Training／Fine-tuning／LoRA実装
- Dataset取得／登録
- Model Download／Weight更新
- Config実装
- Phase 1-ex開始
- Git／GitHub操作
- Lightning外部操作
- Future R&D System実装

## 9. Next Gate

```text
Roadmap Future ML／Evaluation Reservation Added
  → Phase 1 Current Gate継続
  → Lightning Native／Public URL Validation
  → Cross-environment Final Review
  → Phase 1 Completion／Backup
  → Phase 1-ex
```

## 10. Append-Only

更新前のPublic Roadmapを`docs/public/history/`へ不変Snapshotとして保存したうえで、Stable Current RoadmapへFuture ML／Evaluation要件を追加した。新Timestampの本Indexを最新とする。
