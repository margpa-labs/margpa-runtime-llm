# MARGPA Runtime LLM プロジェクト要件

- 文書ID: `project_requirements`
- 状態: `current`
- 作成日時: `2026-07-18 19:34:35 JST`
- 更新日時: `2026-07-18 19:34:35 JST`
- 対象: プロジェクト全体
- 正本言語: 日本語
- supersedes: `project_requirements_20260718174637.md`
- 文書ルール: [documentation_rules_20260718193435.md](documentation_rules_20260718193435.md)

## 1. プロジェクト識別情報

```text
Project Name : margpa-runtime-llm
Display Name : MARGPA Runtime LLM
Internal Name: Nazuna Research Governance LLM
```

プロジェクトルート：

```text
/path/to/margpa-runtime-llm
```

## 2. プロダクト定義

Hugging Face由来の事前学習済みオープンモデルを利用し、ローカルおよび将来のクラウド環境で動作できるGPT風対話型LLMシステムを構築する。

単なるChat UIではなく、モデル外部のRuntimeが推論、統治、監査、評価、修復、安全性、権限を管理するシステムとする。

成果物の位置づけ：

> Hugging Face由来の事前学習済みオープンモデルを用い、ローカル推論、対話管理、監査、評価、修復、外部統治を一体化した、モデル非依存のRuntime Governance型LLMプロトタイプ。

基盤モデル自体を独自に事前学習したとは主張しない。

## 3. MVPの対応範囲

少なくとも次の対話を対象とする。

- AI研究
- AI設計
- AI実装
- 開発相談
- 要件整理
- Architecture設計
- コード関連
- 技術調査
- 一般的な質問
- 普通の雑談

## 4. 機能Scope

段階的に次を統合する。

- ローカル推論
- 会話管理
- GPT風Web UI
- Streaming
- 会話履歴
- 履歴再開
- 生成停止
- 回答再生成
- Generation Config
- Model交換
- Runtime Governance
- ARGD／DAGD統合
- Guardrail
- Prompt Injection対策
- Tool Permission
- Audit Log
- SHA-512整合性検証
- 回答評価
- Deviation検出
- Repair／Regeneration
- 高水準の説明概要
- RAG
- AI Agent
- LLM-as-a-Judge
- Governance Definition交換
- Local／Cloud／Hybrid展開

## 5. 優先順位

1. 要求機能が一通り実際に動くこと
2. システム全体の骨格を成立させること
3. Moduleが分離・交換可能であること
4. Runtime Governance、監査、説明、修復が成立すること
5. 現在のMacBook Proで継続的に動作すること
6. GitHubへ成果物として提示できること
7. 推論速度
8. Context長
9. 回答品質

小型モデルの回答性能が十分高くなくても、システム全体の機能が成立すれば初期MVPとして許容する。

将来、機材更新やCloud移行を行ったときに、Modelだけを交換して高性能化できる状態を優先する。

## 6. 設計思想

ユーザーの基本思想：

> 基本、可能な限り全部分離する。依存性は敵。オブジェクト指向、疎結合、交換可能性を基本とする。

採用原則：

- 単一責任
- 疎結合
- 依存性逆転
- Interface／Port経由の接続
- 依存性注入
- Model Adapter
- Storage Adapter
- Governance Adapter
- 外部I/Oと内部Logicの分離
- Framework固有コードの局所化
- 循環依存の禁止
- Module単位で交換・無効化・Test可能
- すべてを無理にClass化しない
- Framework自体をDomain Logicにしない
- PathをCoreへハードコードしない
- Secretを分離する

初期構成はMicroservicesではなく、内部が明確に分離されたModular Monolithとする。

## 7. 実行環境

```text
PC              : MacBook Pro
Hardware Model  : Mac14,9
SoC             : Apple M2 Pro
CPU             : 10コア（高性能6 + 高効率4）
GPU             : Apple M2 Pro 内蔵GPU
RAM             : 16GB LPDDR5ユニファイドメモリ
Architecture    : Apple Silicon / ARM64
GPU API         : Metal / MPS
CUDA            : 使用不可
内蔵Display      : 3024 × 1964 Retina
外部Display      : BenQ XL2420T / 1920 × 1080
```

制約：

- 16GBをOS、Model、KV Cache、RAG、UI、監査等で共有する
- 小～中規模の量子化Modelを中心とする
- 複数の大型Modelを常時同時ロードしない
- Judgeは原則On-Demandとする
- Full Governanceでは推論回数が増える可能性がある
- 速度、発熱、消費電力、Memoryを後で実測する
- CUDA専用処理をInitial Coreへ持ち込まない

## 8. Context保持方針

- 初期段階では長大なContextを最優先しない
- まず要求機能を一つずつ完成させる
- 会話履歴、要約、検索、長期記憶のHookは設ける
- 機材更新またはCloud利用後に強化する
- ARGDの無断要約禁止と物理的Context上限の整合は今後設計する

## 9. Local／Cloud両対応

Application Coreを共通化し、Deployment Profileで切り替える。

```text
Local Profile
  Metal / MPS / MLX / llama.cpp
  Local Model
  JSON / JSONL

Cloud Profile
  CUDA / vLLM等
  GPU Server
  PostgreSQL / Object Storage等

Hybrid Profile
  UIとApplicationはLocal
  推論だけCloud
```

初期から守ること：

- macOS固有処理をApplication Coreへ入れない
- Device選択を設定化する
- Model BackendをAdapter化する
- StorageをAdapter化する
- Cloud SDKをCoreへ入れない
- Secretを外部設定へ分離する

## 10. 初期Model構成

詳細は[model_strategy_20260718174637.md](../architecture/model_strategy_20260718174637.md)を正本とする。

```text
Main Model:
  Qwen/Qwen3-4B-GGUF
  Qwen3-4B-Q4_K_M.gguf
  Q4_K_M

Guard Model:
  DevQuasar/Qwen.Qwen3Guard-Gen-0.6B-GGUF
  Qwen.Qwen3Guard-Gen-0.6B.Q8_0.gguf
  Q8_0
  Phase 4

LLM-as-a-Judge:
  bartowski/Selene-1-Mini-Llama-3.1-8B-GGUF
  Selene-1-Mini-Llama-3.1-8B-Q5_K_M.gguf
  Q5_K_M
  将来On-Demand
```

必要性が出た場合の通常版候補：

```text
Qwen/Qwen3Guard-Gen-0.6B
AtlaAI/Selene-1-Mini-Llama-3.1-8B
```

## 11. 初期対象外

- Fine-tuning
- LoRA
- DPO
- RLHF
- 継続事前学習
- 独自Weight更新
- Image入力
- Docker
- Microservices化
- SQL必須化
- 16個の将来GD実装
- CDOGDによる自動Routing
- Judgeの常時稼働
- 複数大型Modelの同時常駐

## 12. 現在の禁止事項

明示的な実装解禁があるまで、原則として次を行わない。

- 実装
- Source File作成・変更
- Config File作成・変更
- Dependency Install
- 追加Model Download
- Git初期化
- 外部Serviceへの変更操作
- 勝手な技術選定確定

個別に許可され完了した操作：

- Project構造の読み取り確認
- 専用範囲の`.DS_Store`削除
- Finder Aliasの削除
- POSIX Symbolic Linkの作成
- 3つのGGUF参照確認
- このDocs一式の作成
- Project全体のDirectory構成決定
- Phase 1最小Directoryの作成

これらは一般的な実装解禁を意味しない。

## 13. 現在の主要未決事項

- Local Inference Backend
- Config方式
- Model Registry形式
- Dependency管理方式
- UI技術
- API境界
- Governance Compiler仕様
- Audit JSON Canonicalization
- GuardのFail Open／Fail Closed
- Repository License

## 14. 関連文書

- [system_architecture_20260718193435.md](../architecture/system_architecture_20260718193435.md)
- [project_directory_structure_20260718192110.md](../architecture/project_directory_structure_20260718192110.md)
- [model_strategy_20260718174637.md](../architecture/model_strategy_20260718174637.md)
- [runtime_governance_20260718174637.md](../governance/runtime_governance_20260718174637.md)
- [audit_evaluation_security_20260718174637.md](../governance/audit_evaluation_security_20260718174637.md)
- [implementation_roadmap_20260718193435.md](../architecture/implementation_roadmap_20260718193435.md)
