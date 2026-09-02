# MARGPA Runtime LLM Roadmap — Portfolio Edition

```yaml
document_type: public_roadmap_portfolio_edition
document_state: current_portfolio_edition
language: ja
created_at: 2026-09-01
updated_at: 2026-09-01 19:46 JST
public_author: Nazuna Research
project: MARGPA Runtime LLM
edition: employment_portfolio
source_basis: current_project_records
current_phase: phase_9_1_in_progress_adjust
```

本書は、MARGPA Runtime LLMの開発成果と今後の工程を、採用・技術面談向けに概観できるよう再構成した用途別Roadmapである。全仕様を置き換える文書ではなく、詳細な進捗と研究計画は通常版Roadmapを正本とする。

## 1. Project Overview

MARGPA Runtime LLMは、Local LLMを中心に、会話、知識参照、安全性評価、回答評価、修正支援、Agent／Tool実行および運用証跡を一つのWeb Platformで検証する個人R&D Projectである。

単一のChat画面だけを作るのではなく、各機能を交換・比較・停止できるComponentとして整理し、実装結果をTestとEvidenceで追跡できる状態を目指している。

## 2. Current Capabilities

現在の実装は、直接利用するApplication Surfaceと、研究・検証を継続するためのEngineering Foundationから構成される。

### 2.1 Application Surface

- GGUF Modelを利用したMac Local推論、Streamingおよび生成停止。
- React Web UIによるChat、Settings、Model状態および実験状態の表示。
- SQLiteによる会話、Turn、Citationおよび関連Evidenceの永続化。
- Project DocsとLocal Corpusを対象にした検索、回答根拠およびCitation表示。
- 指定したPublic URLの取得、本文抽出、根拠利用および再読込後のEvidence復元。
- 入出力の検査、回答評価、失敗理由、記録状態およびModel Roleの可視化。
- Fixture Workspaceを使ったAgent Run、Step、File Tool、承認および完了確認。
- Archive、言語切替、Context使用量、再生成、Copy等を含む継続利用向けUI。

### 2.2 Engineering Foundation

- Backend、Frontend、Model AdapterおよびStorageの責務分離。
- Request、Conversation、Turn、Citation、Run、Stepを追跡する安定Identity。
- 構成変更や再起動後も状態を復元できるPersistent Contract。
- 実行結果、失敗理由、参照情報および操作履歴を残すEvidence設計。
- Fixture／Mock、自動Test、実Model Smoke、検証用 Manualを分離した検証工程。
- Phase、Work Unit、Acceptance、ReviewおよびClosureを接続する開発管理。

## 3. Development Progress

| Phase | 状態 | 主な成果 |
|---|---|---|
| Phase 0 | 完了 | 要件、責任境界、Portable Runtime方針を定義 |
| Phase 1／1-ex | 完了 | Local推論、CLI／Web、Streaming、停止、公開Docs運用を成立 |
| Phase 2 | 完了 | 永続会話、React UI、Citation、Settings、復旧可能な開発運用を成立 |
| Phase 3 | 完了 | 汎用定義、Manifest、Validation、Compiler、Evidence基盤を成立 |
| Phase 4 | 完了 | Main Model前後の検査・記録Pointと構造Rule処理を成立 |
| Phase 5 | 完了 | Security、Policy、Authority、Approvalの基盤を独立Component化 |
| Phase 6 | 完了 | Model切替、Judge／Repair、Recording、Observability基盤を実装 |
| Phase 7 | 完了 | Local RAG、Citation、Data Controlsおよび再起動後の継続性を確認 |
| Phase 8 | 完了 | Manual Web Evidence、Archive、Agent／Tool Foundation、承認・永続化を確認 |
| Phase 9 | 進行中 | 専用評価Model、Guard Model、意味評価および複数構成の比較基盤を調整中 |
| Phase 10 | 計画済み | Project全Docs、開発規約、Runtime規約、UI／Observabilityを順次統合。MVP地点 |
| Phase 11以降 | 計画中 | 拡張機能群。External Web、Cloud、定性定量併用活用、開発Agent、Context Window強化、Multimodal、他個人R&Dシステム統合、その他を段階拡張 |

## 4. Phase Progression

### 4.1 RuntimeからApplicationへ

Phase 1ではLocal Modelを安定してLoadし、CLI／Web、Streaming、停止および設定を実装した。Phase 2では会話を一時的な画面状態からPersistent Applicationへ発展させ、Chat List、Resume、Citation、SettingsおよびReact UIを追加した。

この段階で、Model実行と会話Applicationを分離し、Modelを変更しても会話、StorageおよびFrontendを再利用できる土台を整えた。

### 4.2 Evaluation and Safety Foundation

Phase 3〜5では、入力・出力を検査するための定義、Validation、Evidence、Security、PolicyおよびApprovalの基盤を段階的に追加した。

判定結果と実際のActionを分離し、記録だけを行う場合と処理へ介入する場合の違いをTestできるArchitectureへ拡張した。Portfolio Editionでは、その内部判定方式ではなく、交換可能性と検証可能性という成果に焦点を置く。

### 4.3 Model Control and Evaluation

Phase 6では複数Local Modelの切替、Context／Token設定、Runtime Identity、回答評価、修正候補、RecordingおよびStatus UIを統合した。

また、意味評価、Guardrail、LLM-as-a-Judge等の基盤を整えた。

### 4.4 Knowledge and Tool Use

Phase 7ではProject DocsとLocal Corpusを検索し、回答とCitationを結び付けるLocal Knowledge機能を成立させた。Document更新後も過去Turnの根拠を維持し、Reload／Restart後の継続性を確認している。

Phase 8では指定URLを外部Evidenceとして扱う機能、Archive管理、Agent／Tool Foundationおよび段階的な承認を追加した。Agent機能は限定WorkspaceでのFoundationであり、汎用的な自律実行の完成は主張しない。

### 4.5 Research Platformへの移行

Phase 9では、これまで個別に実装したModel、Knowledge、Safety、Evaluation、RepairおよびAgent機能を、構成差として比較できる研究Platformへ発展させる。

Phase 9-1で既知の中心課題を解消し、Phase 9-2で比較実験、Phase 9-3でContext圧縮・復旧の技術Coreを扱う。Phase 10では蓄積したDocs、Runtime、開発運用およびUIをProject全体で再統合する。

## 5. Current Focus

現在はPhase 9-1として、Phase 6から保持しているSemantic Evaluation、Dedicated Judge／Guard、Repair連携およびModel Lifecycleを再検証している。

Qwen3Guardの基本的な検知・拒否・解除経路は実機 Macで確認済みである。一方、Seleneによる評価、Main Modelを使った自己評価、意味Rule群およびModel Role切替後の安定性には未解決事項があり、Phase 9-1は完了ではなく調整中である。

次の工程へ進む前に、自動Testの合格だけでなく、実Modelを使った画面上の動作と通常Chatへの復帰を確認する。

## 6. Verification Approach

- Backend／Frontendの自動Testと型・Lint・Build検査を継続する。
- Fixture、Mock、実Model Smokeおよび実機 Mac Manualを役割別に使い分ける。
- 実装完了、Review完了、実機確認、Phase Closureを別状態として管理する。
- AIの失敗や途中状態を削除せず、Recovery、HandoffおよびEvidenceとして記録する。
- Current、Preview、Fixture、DeferredおよびFutureを混同しない。

| 検証層 | 主な確認対象 |
|---|---|
| Unit | Domain Rule、Validation、Failure、Boundary |
| Integration | Storage、API、Model Adapter、Component連携 |
| Frontend | 表示、状態遷移、User Interaction、Regression |
| Static | 型、Lint、Format、Production Build |
| Real Model | Load、Inference、Latency、Failure Presentation |
| Test Manual | 実画面、再起動、操作順、期待表示、利用可能性 |
| Independent Review | 要件との一致、過大Claim、抜け、回帰Risk |

## 7. Next Milestones

1. Phase 9-1のDedicated Judge／Guard、意味評価、修正連携およびLifecycleを実画面で成立させる。
2. Phase 9-2でModel、RAG、評価、修正および複数構成を比較できる実験基盤を整える。
3. 必要Resourceを確認し、Phase 9-3でContext圧縮・復旧の技術Coreを扱う。
4. Phase 10で全Docsと運用知識を再整理し、Runtimeと開発運用の規約を統合する。
5. UIの情報密度、Trace、Context表示およびResponsive Layoutを再構成する。
6. 後続PhaseでExternal Web、Cloud、正式Agent Capabilityおよび追加研究へ拡張する。

## 8. Representative Deliverables

- Local LLM RuntimeとModel Adapter。
- Persistent Conversation APIとReact Chat UI。
- Local Document登録、検索、CitationおよびEvidence表示。
- Manual Web Evidenceの取得、本文抽出および永続Citation。
- Model／Component StatusとContext使用量の画面表示。
- Security／Evaluationの観測結果と失敗理由の記録。
- Agent Run／Step、Fixture File Tool、ApprovalおよびRun Persistence。
- Backend 2,000件超、Frontend 300件超の継続Test Suite。
- Phase単位のRequirements、Architecture、Acceptance、RecoveryおよびReview運用。

## 9. Engineering Value

このProjectでは、機能数だけでなく、交換可能性、失敗時の収束、状態復元、根拠追跡およびHuman Gateを含む開発工程そのものを実装対象としている。

個人開発でありながら、Requirements、Architecture、Acceptance、Implementation、Review、Rework、Manual TestおよびClosureをPhase単位で接続し、長期継続できるSoftware／AI Research Platformとして整備している。

### 9.1 Software Engineering

- Port／Adapterによる外部技術とDomainの分離。
- Persistent StateとUI Stateの責務分離。
- Failureを例外Messageだけで終わらせないTyped Contract。
- Migration、Backward CompatibilityおよびRestart Recovery。
- Backend／Frontendを通したEnd-to-EndなIdentity保持。

### 9.2 AI／LLM Engineering

- Local ModelのLoad、Streaming、CancelおよびRole別利用。
- RAGとExternal Evidenceの出典・Digest・Revision管理。
- Model出力の検査、評価、修正候補および結果表示。
- Model品質、Runtime品質、Retrieval品質を分離する検証方針。
- 小型Local Modelの特性を、他Modelとの比較検証可能なBaselineとして活用。

### 9.3 Project and Research Management

- 大規模ScopeをPhaseとWork Unitへ分割。
- 自動Test、Independent Review、Manual Testを別Gateとして運用。
- 未完了や失敗を次工程へ埋め込まず、Current Stateとして明示。
- 長時間作業や担当AI変更に備えたRecovery／Handoff。
- Resource、実装価値、Human Attentionを含む進行判断。

## 10. Current Position

MARGPA Runtime LLMは、Local Chatの基礎実装を終え、Persistent Application、Knowledge Grounding、Safety／Evaluation、Web EvidenceおよびAgent Foundationまで拡張している。

現在は、個別Componentが「存在する」段階から、実Modelを使って安定して連携し、比較可能な研究基盤として利用できる段階へ移行中である。完成済み範囲と調整中の範囲を分けながら、MVPを優先して継続開発している。
