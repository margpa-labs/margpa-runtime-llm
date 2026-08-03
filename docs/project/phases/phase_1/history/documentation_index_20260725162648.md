# MARGPA Runtime LLM Documentation Index

- 文書ID: `documentation_index`
- 状態: `current`
- 作成日時: `2026-07-25 16:26:48 JST`
- 更新日時: `2026-07-25 16:26:48 JST`
- Snapshot: `20260725162648`
- 作成担当: 設計者役担当Task
- 正本言語: 日本語
- supersedes: `documentation_index_20260725133218.md`

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
Phase Docs Language／Filename Policy     : Added／Phase 1-ex Reservation
Public Warranty／Switch Notice           : Added／Phase 1-ex Reservation
LLM Validation／Evaluation Design        : Added／Phase 9 Reservation
Responsive UI／Multi-device Experience   : Added／Future Phase
Future ML Extension                      : Added／Future Reservation
Docs Writer until Phase 1-ex Complete    : Current Designer Task Only
Initial GitHub Publication               : Deferred until Phase 1-ex completion
Git                                      : Not Initialized
```

## 2. Snapshot Resolution

Phase 1-H Accepted Evidence、Current User Manual、Documentation単一Writer、README Roadmap最優先要件、公開免責、Phase 4 UI InteractionおよびResponsive UI要件は、[documentation_index_20260725133218.md](documentation_index_20260725133218.md)から継承する。

本Snapshotは、Phase 1-exのDocs言語／Filename Policy、既存規約文書の再利用候補、ON／OFF可能設計に伴う留意事項、およびJudge導入後のLLM動作検証／評価設計を追加したことを記録する。

## 3. Current Public Roadmap

[roadmap_ja.md](public/roadmap_ja.md)

変更前の初期Roadmap Snapshot：

[roadmap_ja_20260722023908.md](public/history/roadmap_ja_20260722023908.md)

## 4. Existing Fragmented Development Docs

Phase統合前のRequirements、Architecture、ADR、Review、Handoff、Status、Index等は、一括英訳または機械的Renameの対象にしない。

- 既存Path、Filename、Timestamp、State、本文、Hashを保持する。
- 原文を英訳目的で書き換えない。
- Phase単位Lossless CompilationのSourceとして扱う。
- 公開可否はGitHub AllowlistとPrivacy／Secret Scanで別途決定する。

## 5. Phase Compilation Documents

Phaseごとに一つの日本語統合文書を作成し、Filenameへ`_ja`を付ける。

```text
phase_1_compilation_ja.md
phase_2_compilation_ja.md
```

統合作業では、元資料を勝手に要約、意訳、再解釈または意味変更しない。Source Set、Path、State、Size、SHA-512および抽出可能性を記録する。

## 6. Public Document Filenames

人が直接読む公開文書は、原則として日本語正本を`_ja`で示す。

```text
overview_ja.md
concept_ja.md
roadmap_ja.md
requirements_specification_ja.md
system_architecture_ja.md
technology_selection_ja.md
basic_design_ja.md
runtime_governance_specification_ja.md
```

慣例的な固定名は例外とする。

- `README.md`
- `LICENSE`
- `CITATION.cff`
- `NOTICE.md`
- 必要に応じた`TERMS_OF_USE.md`

`README.md`は日本語を主とし、末尾に英語Abstractを置く。

## 7. Optional English Documents

余力がある場合に限り、Phase統合文書と公開文書の英語版を`_en`で作成できる。

- 英語版は必須Phase Gateにしない。
- 日本語正本をSource of Truthとする。
- 対応日本語File、Version、SnapshotまたはHashを示す。
- 要件、権限、免責、Status、未解決事項を追加、削除または弱化しない。
- 同期状態を明示する。

## 8. Prior TERMS_OF_USE／NOTICE Reuse

ユーザーが別Projectで作成した`TERMS_OF_USE.md`と`NOTICE.md`を後日提示した場合、再利用可能な条項を候補SourceとしてReviewする。

確認対象：

- Project名／対象範囲
- 利用許諾／禁止事項
- 免責／責任制限
- 第三者License／Model License
- Hosted Service条件
- README／LICENSE／NOTICE／TERMS_OF_USE間の矛盾

無検証のCopyは行わない。

## 9. ON／OFF Research Design Notice

本Projectは研究、比較および検証のため、各Componentと各Governance Pointを個別にON／OFF可能にする方向で設計する。

そのため、READMEの留意事項と、必要に応じて`LICENSE`、`TERMS_OF_USE.md`または`NOTICE.md`へ次を記載する。

- すべての設定組合せの動作、安全性または妥当性を保証しない。
- OFFにしたComponentの検査、制御、修復またはEvidenceが失われる可能性がある。
- Effective Config、無効Component、Warning、Degraded Stateを可能な範囲で表示・記録する。
- 研究自由度を理由にAccess Control、外部Authority、Tool Permissionまたは法令を迂回しない。
- 無意味、未対応または危険な組合せを黙って受理しない。

## 10. LLM動作検証／評価設計

Judge／Evaluation／Repairの基礎が成立するPhase 6より後のPhase 9に配置する。

主な対象：

- AI Research／AI Architecture／Software Engineering支援
- 要件／設計／実装支援
- 一般質問／雑談
- 日本語／英語
- Instruction／Premise／Context／Decision Preservation
- Governance／Guard／Judge／Repairの構成差
- RAG／Agent／Toolは各実装後に追加
- Streaming／Cancel／Context Limit
- Latency／Token／Memory／Failure Rate

評価には、Version付きEvaluation Set、定量計算モード、定性計算モード、Human Review、LLM-as-a-Judge、Baseline、Regression、Ablation、EvidenceおよびReproduction Procedureを含める。

Judgeを唯一のGround Truthまたは最終Authorityにしない。Judge Bias、Position Effect、Verbosity Bias、Language差およびModel依存性を検証する。評価結果が良好でも、READMEまたは`LICENSE`上の動作保証を意味しない。

## 11. Scoped Authorization

本更新はPublic Roadmapへの将来要件追加と最新Index作成だけを対象とする。

次を自動許可しない。

- 既存DocsのRename／Translation／統合
- README／LICENSE／NOTICE／TERMS_OF_USE作成
- LLM Validation／Evaluation実装
- Judge／ML／Future Phase実装
- Phase 1-ex開始
- Git／GitHub操作
- Lightning外部操作

## 12. Next Gate

```text
Phase 1-ex Docs／Notice and Future Evaluation Design Reserved
  → Phase 1 Current Gate継続
  → Lightning Native／Public URL Validation
  → Cross-environment Final Review
  → Phase 1 Completion／Backup
  → Phase 1-ex
```

## 13. Append-Only

旧Indexは変更せず保持する。新Timestampの本Indexを最新とする。
