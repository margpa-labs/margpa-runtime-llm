# MARGPA Runtime LLM Roadmap — Portfolio Edition

```yaml
document_type: public_roadmap_portfolio_edition
document_state: current_portfolio_edition
language: ja
created_at: 2026-09-01
updated_at: 2026-09-01 19:03 JST
public_author: Nazuna Research
project: MARGPA Runtime LLM
source_document: docs/public/roadmap_summary_ja.md
canonical_detailed_roadmap: docs/public/roadmap_ja.md
current_phase: phase_9_1_in_progress_adjust
```

本書は、MARGPA Runtime LLMの開発成果と今後の工程を、採用・技術面談向けに概観できるよう再構成した用途別Roadmapである。全仕様を置き換える文書ではなく、詳細な進捗と研究計画は通常版Roadmapを正本とする。

## 1. Project Overview

MARGPA Runtime LLMは、Local LLMを中心に、会話、知識参照、安全性評価、回答評価、修正支援、Agent／Tool実行および運用証跡を一つのWeb Platformで検証する個人R&D Projectである。

単一のChat画面だけを作るのではなく、各機能を交換・比較・停止できるComponentとして整理し、実装結果をTestとEvidenceで追跡できる状態を目指している。

## 2. Current Capabilities

- GGUF Modelを利用したMac Local推論、Streamingおよび生成停止。
- React Web UIによるChat、Settings、Model状態および実験状態の表示。
- SQLiteによる会話、Turn、Citationおよび関連Evidenceの永続化。
- Project DocsとLocal Corpusを対象にした検索、回答根拠およびCitation表示。
- Userが指定したPublic URLの取得、本文抽出、根拠利用および再読込後のEvidence復元。
- 入出力の検査、回答評価、失敗理由、記録状態およびModel Roleの可視化。
- Fixture Workspaceを使ったAgent Run、Step、File Tool、承認および完了確認。
- Archive、言語切替、Context使用量、再生成、Copy等を含む継続利用向けUI。

## 3. Development Progress

| Phase | 状態 | 主な成果 |
|---|---|---|
| Phase 0 | 完了 | 要件、責任境界、Portable Runtime方針を定義 |
| Phase 1／1-ex | 完了 | Local推論、CLI／Web、Streaming、停止、公開Docs運用を成立 |
| Phase 2 | 完了 | 永続会話、React UI、Citation、Settings、復旧可能な開発運用を成立 |
| Phase 3 | 完了 | 汎用定義、Manifest、Validation、Compiler、Evidence基盤を成立 |
| Phase 4 | 完了 | Main Model前後の検査・記録Pointと構造Rule処理を成立 |
| Phase 5 | 完了 | Security、Policy、Authority、Approvalの基盤を独立Component化 |
| Phase 6 | 最小Closure | Model切替、Judge／Repair、Recording、Observability基盤を実装。意味評価は調整継続 |
| Phase 7 | 完了 | Local RAG、Citation、Data Controlsおよび再起動後の継続性を確認 |
| Phase 8 | 完了 | Manual Web Evidence、Archive、Agent／Tool Foundation、承認・永続化を確認 |
| Phase 9 | 進行中 | 専用評価Model、Guard Model、意味評価および複数構成の比較基盤を調整中 |
| Phase 10 | 計画済み | Project全Docs、開発規約、Runtime規約、UI／Observabilityを順次統合 |
| Phase 11以降 | 将来研究 | External Web、Cloud、Formal Agent、Multimodal、Training等を段階拡張 |

## 4. Current Focus

現在はPhase 9-1として、Phase 6から保持しているSemantic Evaluation、Dedicated Judge／Guard、Repair連携およびModel Lifecycleを再検証している。

Qwen3Guardの基本的な検知・拒否・解除経路はUser Macで確認済みである。一方、Seleneによる評価、Main Modelを使った自己評価、意味Rule群およびModel Role切替後の安定性には未解決事項があり、Phase 9-1は完了ではなく調整中である。

次の工程へ進む前に、自動Testの合格だけでなく、実Modelを使った画面上の動作と通常Chatへの復帰を確認する。

## 5. Verification Approach

- Backend／Frontendの自動Testと型・Lint・Build検査を継続する。
- Fixture、Mock、実Model SmokeおよびUser Mac Manualを役割別に使い分ける。
- 実装完了、Review完了、User確認、Phase Closureを別状態として管理する。
- 失敗や途中状態を削除せず、Recovery、HandoffおよびEvidenceとして記録する。
- Current、Preview、Fixture、DeferredおよびFutureを混同しない。

## 6. Next Milestones

1. Phase 9-1のDedicated Judge／Guard、意味評価、修正連携およびLifecycleを実画面で成立させる。
2. Phase 9-2でModel、RAG、評価、修正および複数構成を比較できる実験基盤を整える。
3. 必要Resourceを確認し、Phase 9-3でContext圧縮・復旧の技術Coreを扱う。
4. Phase 10で全Docsと運用知識を再整理し、Runtimeと開発運用の規約を統合する。
5. UIの情報密度、Trace、Context表示およびResponsive Layoutを再構成する。
6. 後続PhaseでExternal Web、Cloud、正式Agent Capabilityおよび追加研究へ拡張する。

## 7. Engineering Value

このProjectでは、機能数だけでなく、交換可能性、失敗時の収束、状態復元、根拠追跡およびHuman Gateを含む開発工程そのものを実装対象としている。

個人開発でありながら、Requirements、Architecture、Acceptance、Implementation、Review、Rework、Manual TestおよびClosureをPhase単位で接続し、長期継続できるSoftware／AI Research Platformとして整備している。

詳細は[通常版Roadmap](roadmap_ja.md)、[Roadmap要約版](roadmap_summary_ja.md)、[Technology Selection](technology_selection_ja.md)を参照する。
