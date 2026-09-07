# MARGPA Runtime LLM Roadmap 要約版

```yaml
document_type: public_roadmap_summary
document_state: phase_9_1_complete_phase_9_2_in_progress
language: ja
project_initiated_at: 2026-07-18 17:46:37 JST
created_at: 2026-08-23
updated_at: 2026-09-07 09:54 JST
public_author: Nazuna Research
project: MARGPA Runtime LLM
current_phase: phase_9_2_in_progress
```

MARGPA Runtime LLMは、LLMを中心とした複数の機能を自由に組み替え、動作と結果を比較するためのローカル研究Platformである。

会話Model、検索、Guardrail、回答評価、回答修正、Agent、Tool、記録機能を独立したComponentとして扱う。Governance系Componentは`OFF／OBSERVE／ENFORCE`、その他のComponentは役割に応じたON／OFF等を個別に選択でき、他のComponentがなくても可能な範囲で単独動作することを基本方針としている。

`OBSERVE`は結果を記録するだけで回答へ介入しない。`ENFORCE`は判定結果に応じて、拒否や回答修正などのActionを実行する。

## 1. 全体進捗

| Phase | 状態 | 主な成果 |
|---|---|---|
| Phase 0 | 完了 | 要件、責任境界、Model非依存方針を定義 |
| Phase 1／1-ex | 完了 | GGUF推論、CLI、Web、Streaming、停止、Docs運用を実装 |
| Phase 2 | 完了 | 永続会話、React UI、Citation、Settings、復旧運用を実装 |
| Phase 3 | 完了 | 汎用Governance Definition、Manifest、Compiler、Evidenceを実装 |
| Phase 4 | 完了 | Main Model前後のGovernance Pointを実装 |
| Phase 5 | 完了 | Guardrail、Policy、Authority、Approvalを分離 |
| Phase 6 | 完了 | Model切替、Judge、Repair、Recording、Observabilityの基盤を実装 |
| Phase 7 | 完了 | Local Corpus、RAG、Citation、Data Controlsを実装 |
| Phase 8 | 完了 | Manual Web Evidence、Archive、Agent／Tool基盤を実装 |
| Phase 9-1 | 完了 | 独立Judge、Guard、意味評価、Repair、Rejudgeを実画面で確認 |
| Phase 9-2 | 進行中 | Experiment、Evaluation、複数Governance構成の比較基盤を構築 |
| Phase 9-3 | 計画済み | Context圧縮と復旧の非Visual技術Coreを検証 |
| Phase 10 | 計画済み | 全Docs、Constitution、Runtime規約、UIを統合 |
| Phase 11以降 | 計画中 | 拡張機能群。外部接続、Cloud、定性定量併用活用、開発Agent、Context Window強化、Multimodal、他個人R&Dシステム統合、その他を段階拡張 |

## 2. 現在の構成

```text
Main Model
  ├─ Local RAG／Citation
  ├─ Main Runtime Governance
  ├─ Guardrail
  ├─ LLM-as-a-Judge
  ├─ Repair／Rejudge
  ├─ Recording／Evidence
  └─ Agent／Tool Runtime
```

各機能を一本の処理へ固定せず、役割ごとのPortとAdapterで接続する。設定したProvider、実際に有効なProvider、実行したProvider、評価に使ったModelを別々に記録する。

通常Chatの設定を実験側が無言で変更しないこと、OFFのComponentがCallやAuthorityを発生させないこと、失敗したRunを成功として保存しないことを共通原則としている。

## 3. Phase 1〜2 — RuntimeとApplication

### Phase 1

- GGUFとllama.cppを使ったローカル推論を実装。
- CLIとWeb UIを用意し、Streaming、停止、Thinking表示を分離。
- Model RuntimeをApplication本体からAdapterで分離。

### Phase 2

- SQLiteによる会話、Turn、Citationの永続化を実装。
- ReactによるChat List、再開、再生成、分岐、Settingsを実装。
- Browser表示とServer上の正本を分離し、再起動後も会話を復元。

## 4. Phase 3〜5 — Governance基盤

### Phase 3

Governance Definitionを特定のRule群へ固定せず、Provider、Manifest、Validation、正規化、Compiler、Bindingへ分けた。

Definitionが0件でもRuntimeを動かせるため、Governance機能の存在をApplication全体の必須条件にしない。

### Phase 4

Main Modelの実行前と実行後へGovernance Pointを追加した。Rule選択、Observation、Deviation、Action Resolutionを分け、観測と介入を比較できる形にした。

### Phase 5

Prompt Injection、Secret、個人情報などの検知を行うGuardrail基盤を追加した。Detection、Policy、Authority、Approval、実行Actionを別の状態として管理する。

## 5. Phase 6〜8 — 評価、知識、Agent

### Phase 6

- Main Modelの切替とRuntime Identity表示。
- Context Sizeと出力Token上限の管理。
- LLM-as-a-Judge、回答修正、Rejudge、Recordingの基盤。
- Deadline、停止、Worker管理、失敗理由の型付き記録。

Phase 6では基盤を成立させ、実Modelを使った意味評価と修正の最終確認をPhase 9-1へ引き継いだ。

### Phase 7

- Project DocsとLocal Corpusを対象としたBM25検索。
- Citation、Document Digest、Revision、過去Evidenceの保持。
- Local Corpusの登録、更新、Soft Delete。
- Data Controlsと外部接続用のPort。

一般的なWeb自動検索は、このPhaseの完成条件から分離し、後続の外部Knowledge Runtimeへ送っている。

### Phase 8

- 指定したPublic URLの取得と本文抽出。
- 外部ContentをUntrusted Evidenceとして区別したCitation。
- Chat Archiveと通常一覧の分離。
- 限定Workspaceを使ったDev Agent Preview。
- Run、Step、File Tool、Approval、Completionの永続化。
- 暫定Runtime Constitution。

## 6. Phase 9-1 — Governance Semantic基盤の成立

Phase 9-1では、Phase 6から引き継いだ評価Model、Guardrail、意味評価、回答修正の実Model経路を再構成した。

### 成立した経路

- Main GovernanceがOFFでも、Gemma Judgeが独立してOBSERVEできる。
- Judge ENFORCEが回答修正を要求し、Main Modelが修正候補を生成できる。
- 同じGemmaが修正候補をRejudgeし、採用または不採用を決定できる。
- Repair ModeがOFFでも、Main Governance ENFORCEが独自にRepairを要求できる。
- JudgeとMain Governanceの双方が要求した場合、`judge_and_main`として区別できる。
- Qwen3GuardはOBSERVEとENFORCEで同じ検知結果を使い、Actionだけを切り替えられる。
- 全Mode OFF後にJudgeとGuardをUnloadし、通常Chatへ戻れる。

### 意味評価

ARGD／DAGDから構成される109件の意味評価Criterionを、実行予算内の32件とDeferred 77件に分けて扱う。

実行した32件は、Pass、Deviation、Unknown、Not Applicableのいずれかへ分類する。合計が109件と一致する保存則を持ち、未評価をPassへ変換しない。

Gemma向けにはJudge専用のStructured Output制約を導入し、JSON構造を生成時点で限定した。これにより、実画面でJudge、Repair、Rejudge、最終回答の採用までを連続して確認できた。

Phase 9-1は、定義した機械的Acceptanceを満たしたため、通常Full Closureを省略して完了とした。Modelの知識精度や判定品質は、基盤の成立とは分けて未解決課題として管理する。

## 7. Phase 9-2 — Experiment／Multi-Governance

Phase 9-2の目的は、同じCaseに異なる構成を適用し、結果、Evidence、評価を比較できる状態を作ることである。

### 実装済みの基盤

- Experiment Plan、Variant Run、CaseのIdentity分離。
- Case ManifestとDigestによる入力固定。
- Baseline、Regression、Ablationの単一要因差検証。
- Component OFF時のCall、Mutation、Evidence、Authorityを0にする独立性Matrix。
- Freshness、RAG Grounding、Belief Revision、False ImprovementのCase分類。
- 非同期Worker、Cancel、Deadline、Terminal結果のExactly-once管理。
- Restart後も読み直せるPlan、Run、Raw Evidence、Comparison。
- Preset選択、実行、比較表、詳細Evidenceを備えた最小Experiment UI。
- Qwen Main、Gemma Judge、Qwen3Guardを接続するProduction Adapter。

### 現在の調整点

Phase 9-2はまだ完了していない。

現在は、同一Experiment内で異なるProduction Variantを順番に実行する境界を整えている。Variantごとの設定をFreezeし、実行前後の設定一致を確認し、実行中の設定変更を防ぐ。

Evidenceは、`呼ばれた`、`呼ばれなかった`、`観測できない`を分ける。相関できない情報をFalseや0へ変換しない。

次のReworkでは、Top-level Experiment RunからProduction Adapter、Persistence、Evaluation、Comparison、Restart Readまでを通す実Model Gateを確認する。

## 8. Phase 9-3 — Context Compaction／Recovery

Phase 9-2成立後、Context Windowを長時間利用するための非Visual技術Coreを扱う。

- Context使用量と残量の計測。
- Compaction対象と保持対象の分離。
- 圧縮前後のProvenanceとDigest。
- 失敗時のRollbackとRecovery。
- Main、Judge、Guard、Agent間のContext境界。
- Phase 10のUIが参照できるProjection Contract。

右側Panel等の大規模な画面改造はPhase 10へ残す。

## 9. Phase 10 — Project-wide Integration

Phase 10は次の順序で進める。

1. 全DocsをInventory化し、Current、Phase、Public、Shared、Historyを整理する。
2. 全Docsを再読し、抜け、Conflict、古いPointer、Current／Historical混同を監査する。
3. Shared Constitutionを全Docsから二段階で編纂する。
4. 開発統治RuleをPortable Packageとして整理する。
5. 暫定Runtime ConstitutionをFull Runtime Constitutionへ発展させる。
6. 最後にSettings、Sidebar、Context表示、右側検証Panelを再構成する。

Constitution関連の統合品質を上げるため、全範囲統合の直前にClaude側とCodex側で指定範囲の独立統合を行う。互いの成果を先に見ない状態で作り、その差分を最終統合の材料にする。

## 10. Phase 11以降

### 構造制御と意味評価の分離

ARGD／DAGDとRuntime Constitutionは、Judgeに依存せず生成前からModelを制御する構造制御Layerと、意味評価の結果からRepairを要求する意味評価Layerへ分離する。

どちらか一方だけでも利用でき、Judge、Repair、Guardrailが存在しない構成も許容する。

### Development Agentの段階拡張

Agentは一度に完成させず、通常の開発Agentから、Governanceを備えた自律的な開発運用へ段階的に発展させる。

上位にはARGD、DAGD、Runtime Constitutionを置く。必要時にOrchestration、戦略、承認、監査、メタ監査のGovernanceを起動し、その下でDomain特化Governanceを選択する構想を持つ。

### 外部機能

- Governed External Web Knowledge Runtime。
- Cloud／GPU Serverと追加Inference Backend。
- 追加Model、Multimodal、Long Context。
- 学習Data、Evaluation、Promotionを分けたTraining Pipeline。
- EASA、DLAGSA、OCILNS等の外部R&D接続。

## 11. 検証と開発運用

```text
要件
→ 設計
→ 実装
→ 自動Test
→ Independent Review
→ Rework
→ 実Model Test
→ 実画面確認
→ Acceptance
```

- Backendは2,600件超、Frontendは330件超のTestを継続している。
- pytest、Vitest、Mypy、Ruff、TypeScript、ESLint、Production Buildを使用する。
- Fixture、Production-fixture、実Modelを別のEvidenceとして扱う。
- Testを意図的に壊して、回帰検出力を確認するSabotage-regressionを使う。
- Handoff、Recovery、Historyを保存し、長時間作業や担当変更後も復旧できるようにする。
- 完了、未解決、保留、予約を別Directoryと別状態で管理する。

## 12. 現在地

Phase 9-1までに、Main Governance、独立Judge、Guardrail、Repair、Rejudge、Recordingの機械的な基盤が実画面で成立した。

現在はPhase 9-2で、これらを単独で試す段階から、複数Variantを同じCaseで比較する段階へ進めている。Phase 9-2のProduction比較経路が成立した後、Context Compaction／Recovery、Project全体のDocs／Constitution統合、UI再構成へ進む。
