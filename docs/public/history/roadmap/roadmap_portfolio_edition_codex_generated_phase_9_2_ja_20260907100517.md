# MARGPA Runtime LLM Roadmap — Portfolio Edition

```yaml
document_type: public_roadmap_portfolio_edition
document_state: current
language: ja
project_initiated_at: 2026-07-18 17:46:37 JST
created_at: 2026-09-01
updated_at: 2026-09-07 09:54 JST
public_author: Nazuna Research
project: MARGPA Runtime LLM
edition: portfolio_selected_detail
source_basis: current_project_records
current_phase: phase_9_2_in_progress
```

MARGPA Runtime LLMは、ローカルLLMを使った会話、知識検索、安全性確認、回答評価、回答修正、Agent実行を一つの画面で試せる研究用Platformである。

一般的なChat画面に機能を足すだけではなく、それぞれを独立した部品として扱う。必要な機能だけを有効にし、構成を変えた結果を比較できることを重視している。

## 1. Projectの目的

LLM Applicationでは、Modelの回答品質だけでなく、検索結果、安全性判定、修正処理、実行履歴などが最終結果へ影響する。

本Projectでは、これらを一体化したまま扱わない。役割を分け、どの処理が実行され、何が回答を変えたのかを追跡できる仕組みを構築している。

目標は次の3点である。

1. Modelや補助機能を交換しやすくする。
2. 観測だけを行う構成と、回答へ介入する構成を比較できるようにする。
3. 成功だけでなく、失敗理由と実行経路も検証できるようにする。

## 2. 現在利用できる機能

### 2.1 ChatとModel実行

- GGUF形式のModelをMac上で実行するローカル推論。
- 生成中のStreaming表示と停止操作。
- 会話の保存、再開、名称変更、Archive管理。
- Model、Context Size、出力Token上限の設定と状態表示。
- 複数Modelの登録と役割別の選択。

### 2.2 知識と根拠

- Project文書と登録文書を対象にしたローカル検索。
- 検索結果を回答根拠として表示するCitation機能。
- 文書更新後も、過去の回答が参照した根拠を保持する履歴管理。
- 指定したPublic URLの本文取得と、外部情報であることを明示したEvidence表示。

### 2.3 Governanceと回答評価

- Main Modelの入出力を確認するGovernance Point。
- 安全性を確認するGuardrail。
- 別Modelを使って回答を評価するLLM-as-a-Judge。
- 評価結果に応じた回答修正と再評価。
- `OFF／OBSERVE／ENFORCE`による非介入・観測・介入の切替。
- 設定したModel、実行したModel、評価に使ったModelの区別。

### 2.4 AgentとTool

- 通常Chatと開発Agent用画面の切替。
- 限定Workspace内でのFile一覧、読取、書込の検証。
- 外部作用を伴う処理の承認待ち表示。
- Run、Step、入力、出力、結果の保存。

## 3. 技術基盤

Applicationは、Backend、Frontend、Model Adapter、Storageを分けて構成している。

- Python Backendが処理の流れと型付きContractを管理する。
- React FrontendがChat、Settings、Evidence、実験画面を提供する。
- SQLiteとFilesystemが会話、Citation、Run、Evidenceを保存する。
- Modelや外部機能はAdapterを介して接続する。
- Request、Turn、Run、Evidenceに安定したIdentityを持たせる。

この分離により、一つのModelや機能を変更しても、会話画面、保存機能、検証機能を再利用できる。

## 4. 開発の進捗

| Phase | 状態 | 主な到達点 |
|---|---|---|
| Phase 0 | 完了 | 目的、要件、責任境界を定義 |
| Phase 1／1-ex | 完了 | ローカル推論、CLI、Web、Streaming、停止を実装 |
| Phase 2 | 完了 | 永続会話、React UI、Citation、Settingsを実装 |
| Phase 3 | 完了 | 汎用的なGovernance Definition基盤を実装 |
| Phase 4 | 完了 | Main Model前後の検査と記録を実装 |
| Phase 5 | 完了 | Security、Policy、Authority、Approvalを分離 |
| Phase 6 | 完了 | Model制御、Judge、Repair、Recordingの基盤を実装 |
| Phase 7 | 完了 | Local Corpus、RAG、Citation、Data Controlsを実装 |
| Phase 8 | 完了 | Web Evidence、Archive、Agent／Tool基盤を実装 |
| Phase 9-1 | 完了 | 独立Judge、Guardrail、意味評価、Repair連携を実機確認 |
| Phase 9-2 | 進行中 | 複数構成を同じ条件で比較する実験基盤を構築 |
| Phase 9-3 | 計画済み | Context圧縮と復旧の技術基盤を検証 |
| Phase 10 | 計画済み | 文書、Runtime規約、UIをProject全体で統合 |
| Phase 11以降 | 計画中 | 外部接続、拡張Agent、追加Model、長期運用へ発展 |

## 5. Phase 9で扱っていること

### 5.1 Phase 9-1 — 評価と修正の実行基盤

Phase 9-1では、Main Model、Guardrail、評価Model、回答修正を個別に有効化できる状態へ整理した。

Gemmaを独立した評価Modelとして使い、回答評価、修正要求、修正後の再評価、最終回答への採用までを実画面で確認している。Main Governanceと評価Modelが別々に修正を要求する経路も区別して記録できる。

Qwen3Guardは、観測だけを行う状態と、安全な拒否へ切り替える状態を実機で確認した。すべてをOFFにした後は、通常Chatへ戻れる。

ここで成立したのは、評価・修正・記録を正しく接続する基盤である。個々のModelが常に正しい判断をすることとは分けて扱っている。

### 5.2 Phase 9-2 — 比較実験

Phase 9-2では、同じCaseへ異なる機能構成を適用し、その結果を並べて確認する仕組みを構築している。

現在までに次の基盤を実装した。

- 実験Plan、実行Run、構成Variantを分けたIdentity。
- 再起動後も読み直せるFilesystem Persistence。
- Caseごとの評価とComparison Report。
- 非同期実行、停止、Deadline、二重結果防止。
- Preset選択、実行、比較表、詳細Evidenceを備えた最小UI。
- 実Modelを接続するProduction Adapter。

現在は、異なるProduction構成を同じExperiment内で安全に実行し、未観測の情報を成功や0件として扱わないための最終調整を進めている。

## 6. 検証方法

機能実装と検証結果を同じ状態として扱わず、複数の確認段階を設けている。

| 確認方法 | 対象 |
|---|---|
| Unit Test | Domain Rule、Validation、境界条件 |
| Integration Test | API、Storage、Component連携 |
| Frontend Test | 表示、操作、状態遷移 |
| Static Analysis | 型、Lint、Build |
| Real Model Test | Model Load、推論、連携、停止 |
| 実画面確認 | 操作順、表示、再起動後の状態 |
| Independent Review | 要件との一致、過大な完成判定、回帰Risk |

Backendでは2,600件を超える自動Test、Frontendでは330件を超えるTestを継続している。Test件数だけでなく、意図的に条件を壊したときに新しいTestが失敗を検出できることも確認する。

## 7. 次の工程

1. Phase 9-2のProduction Variant比較とEvidence表示を完成候補へ進める。
2. Phase 9-3でContext圧縮、復旧、状態追跡の技術Coreを検証する。
3. Phase 10でProject全体の文書を二段階で統合する。
4. Runtime Constitutionと開発運用規約を整理する。
5. 右側の検証Panelを中心に、情報量の多いUIを再構成する。
6. 後続Phaseで外部知識、追加Model、正式なAgent能力へ拡張する。

## 8. Engineering上の特徴

### 8.1 交換可能性

Model、検索、Guardrail、評価、回答修正、Agent、Tool、Storageを独立したComponentとして接続する。構成の一部をOFFにしても、不要な処理やEvidenceを発生させないことを重視している。

### 8.2 Evidence

画面上の設定だけで実行事実を判断しない。設定値、実行結果、Model Identity、失敗理由、保存状態を区別して記録する。

### 8.3 復旧可能性

会話や実験結果を再起動後も読み直せるようにし、長時間の開発や検証が途中で中断しても再開できる構造を維持する。

### 8.4 Human Control

外部作用や重要な変更は、自動実行と手動承認を分ける。安全な停止や失敗時の収束も、通常の成功経路と同じく設計対象に含める。

## 9. 現在地

MARGPA Runtime LLMは、ローカルChatから始まり、永続会話、RAG、Citation、Web Evidence、Governance、評価、回答修正、Agent／Tool基盤までを一つのApplicationへ統合している。

現在は、個別機能が動く段階から、異なる構成を同じ条件で比較し、結果と根拠を再利用できる研究Platformへ移行している。Phase 9-2の比較実験基盤を完成候補へ進めた後、Context管理とProject全体の統合へ進む。
