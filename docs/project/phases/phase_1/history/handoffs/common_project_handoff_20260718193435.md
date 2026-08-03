# MARGPA Runtime LLM 共通引き継ぎ

- 文書ID: `common_project_handoff`
- 状態: `current`
- 作成日時: `2026-07-18 19:34:35 JST`
- 更新日時: `2026-07-18 19:34:35 JST`
- 対象: すべての担当タスク
- 正本言語: 日本語
- supersedes: `common_project_handoff_20260718174637.md`
- 文書索引: [documentation_index_20260718193435.md](../documentation_index_20260718193435.md)

## 0. 最重要指示

現在は要件定義・技術選定・Architecture設計Phaseである。

ユーザーから明示的な実装解禁があるまで、原則として次を行わない。

- 実装
- Source File作成・変更
- Config File作成・変更
- Dependency Install
- 追加Model Download
- Git初期化
- 外部Serviceへの変更操作
- 勝手な技術選定確定

このDocs一式の作成は個別に許可された。一般的な実装解禁ではない。

## 1. Project

```text
Project Name : margpa-runtime-llm
Display Name : MARGPA Runtime LLM
Internal Name: Nazuna Research Governance LLM
```

Project Root：

```text
/path/to/margpa-runtime-llm
```

論理的なProject Root表記：

```text
margpa-runtime-llm/
```

ユーザーが`docs/`等の相対Pathだけを指定した場合、明示的に別の基準Pathが指定されていない限り、`margpa-runtime-llm/docs/`として解釈する。

## 1.1 タスク間の情報伝達とDocs権限

タスク間の情報伝達、進捗通達、決定事項、未決事項、引き継ぎは、原則として次を共通基盤とする。

```text
margpa-runtime-llm/docs/
```

Docsを読み込む、確認する、参照する、引き継ぐよう依頼された場合は、原則として必ず読み取り専用で扱う。

読み取り依頼は、File作成、編集、削除、移動、改名、正本差し替えの許可を意味しない。変更はユーザーから明示的な変更指示または作成・更新許可を受けた場合だけ行う。

矛盾や誤記を発見しても、読み取り依頼だけで勝手に修正せず、発見内容を報告する。

## 2. 目的

Hugging Face由来の事前学習済みModelを利用し、Localおよび将来のCloudで動作できる、Model非依存・Governance Definition交換可能なRuntime Governance型対話LLM Prototypeを構築する。

対応範囲：

- AI研究
- AI設計
- AI実装
- 開発相談
- 要件整理
- コード
- 技術調査
- 一般質問
- 雑談

Model自体を独自事前学習したとは主張しない。

## 3. 優先順位

1. 要求機能が一通り動くこと
2. 全体骨格を成立させること
3. Moduleが分離・交換可能であること
4. Governance、Audit、Explanation、Repairが成立すること
5. M2 Pro・16GBで動作すること
6. GitHubへ提示できること
7. 速度
8. Context長
9. 回答品質

小型Modelの性能が十分高くなくても、System全体が成立すればMVPとして許容する。

## 4. 設計原則

- 単一責任
- 疎結合
- 依存性逆転
- Port／Adapter
- 依存性注入
- 循環依存禁止
- Framework固有コードの局所化
- Model、Backend、Storage、UI、Governanceの交換性
- PathとSecretの外部化
- Modular Monolith

## 5. Hardware

```text
MacBook Pro Mac14,9
Apple M2 Pro
CPU 10コア
RAM 16GB Unified Memory
Apple Silicon / ARM64
Metal / MPS
CUDA不可
```

複数大型Modelの常時同時Loadを避ける。

## 6. Initial Model

```text
Main:
  Qwen/Qwen3-4B-GGUF
  Qwen3-4B-Q4_K_M.gguf
  Q4_K_M

Guard:
  DevQuasar/Qwen.Qwen3Guard-Gen-0.6B-GGUF
  Upstream: Qwen/Qwen3Guard-Gen-0.6B
  Qwen.Qwen3Guard-Gen-0.6B.Q8_0.gguf
  Q8_0
  Phase 4

Judge:
  bartowski/Selene-1-Mini-Llama-3.1-8B-GGUF
  Upstream: AtlaAI/Selene-1-Mini-Llama-3.1-8B
  Selene-1-Mini-Llama-3.1-8B-Q5_K_M.gguf
  Q5_K_M
  将来On-Demand
```

通常時はMain＋Guard。Judgeは非Load。

Judge実行時はMainを一時停止またはUnloadし、JudgeをOn-Demand Loadする方針。

## 7. Model Storage

物理Root：

```text
/path/to/margpa-models/
```

Project Link：

```text
margpa-runtime-llm/models
  → /path/to/margpa-models
```

これはPOSIX Symbolic Link。Finder Aliasではない。

確認済みPath：

```text
models/main/qwen3-4b/gguf/Qwen3-4B-Q4_K_M.gguf
models/guard/qwen3guard-gen-0.6b/gguf/Qwen.Qwen3Guard-Gen-0.6B.Q8_0.gguf
models/judge/selene-1-mini-llama-3.1-8b/gguf/Selene-1-Mini-Llama-3.1-8B-Q5_K_M.gguf
```

RuntimeはSymbolic Link自体へ依存せず、設定可能なModel Rootを使用する。

Model BinaryとSymbolic LinkはGitへ含めない。

## 8. Existing LLaVA

```text
llava-phi-3-mini-int4.gguf
llava-phi-3-mini-mmproj-f16.gguf
```

既存のImage用Model。初期Scope外。将来Vision Adapterから利用可能にする。

## 9. Model／Backend

ModelとBackendを分けて選定する。

Local Backend候補：

- llama.cpp
- llama-cpp-python
- MLX
- Transformers／PyTorch

GGUF採用によりllama.cpp系が有力だが未確定。

Cloud候補：

- vLLM
- Remote Inference API

## 10. Runtime Governance

ARGD／DAGDを巨大System Promptとして貼るだけにしない。

Inference Control PlaneをRuntime Governance Layerが所有する。

```text
Governance Definition
    ↓
Governance Compiler
    ↓
Governance Plan
    ↓
Runtime Governance Layer
    ↓
Model Port
    ↓
Model Adapter
    ↓
Pretrained Model
```

Model内部のWeight、Attention、Hidden Stateへは初期版で介入しない。

## 11. ARGD／DAGD

原文：

```text
argd_v0.3.1_en_dagd_v0.4.4_en.json
```

確認結果：

```text
Valid JSON
約69KB
約1,793行
Top Level: argd / dagd
ARGD v0.3.1
DAGD v0.4.4 EXPERIMENTAL
Author: Nazuna Research
License: CC-BY-SA-4.0
```

69KB全体を毎回Modelへ投入しない。

- 必要なARGD RuleをPromptへCompile
- DAGD State／ActionはPython側中心
- Rule Basedを優先
- 意味的評価だけLLM
- 使用Definition、Rule、State、ActionをAudit

Execution Profile候補：

- Core
- Standard
- Full

## 12. Future GD

初期版では実装しない。

- CDOGD
- SPPGD
- DAAGD
- SDAGD
- SDMRGD
- DSGD
- ACRGD
- AAGD
- AISGD
- MPGD
- DCAGD
- PMOGD
- AIRGD
- AIAGD
- SEGD
- OMRGD

特にAISGD、AAGD、MPGD、DAAGDのHookを意識する。

16GDをすべてPromptへ投入しない。自動Routingはさらに将来。

## 13. Guard／Permission

```text
Runtime Governance:
  推論品質、前提、文脈、監査、修復

Guardrail:
  安全性、禁止、攻撃、秘密情報

Tool Permission:
  外部実行の許可、拒否、承認
```

初期方針：

- GuardはQwen3GuardをPhase 4で追加
- Prompt InjectionはRule Based中心
- 専用Classifierは後から追加
- Tool Permissionは決定論的Policy

## 14. LLM-as-a-Judge

将来Hookのみ。

- Judgeを常駐させない
- Judge出力を絶対視しない
- Evaluation RubricをVersion管理
- Judge結果をAudit Event化
- 日本語性能を検証

## 15. Audit

- User入力からAssistant回答までの一往復を基本単位
- JSON／JSONL候補
- Append-Only
- 原則上書き禁止
- SHA-512
- Evaluation／Repair／Regenerationを追記Event化
- 生のChain of Thoughtは保存しない
- 高水準の説明概要を保存

SHA-512 Canonicalizationは未決。

将来、Hash Chain、HMAC、Digital Signature等を検討する。

## 16. RAG／Agent

RAGはPhase 5。

- Document
- Chunking
- Embedding
- Retrieval
- Source
- Citation
- Audit

AgentはPhase 6。

- Tool Registry
- Planning
- Multi-Step
- State
- Memory
- Handoff
- Human Approval
- Loop防止
- Tool Audit

## 17. Storage／Docker

初期Storage候補：

- JSON
- JSONL
- Append-Only Event Log

SQLiteはHook。CloudではPostgreSQL候補。

Dockerは初期不採用。

## 18. Docs Rule

File Name：

```text
lower_snake_case_YYYYMMDDHHMMSS.md
```

Timezone：`Asia/Tokyo / JST`

本文は可能な限り日本語。技術識別子と正式名称のみ英語を保持する。

Current文書は`documentation_index`で確認する。

## 19. 担当タスク構想

### 設計者役

- Requirements
- Architecture
- 技術選定
- ADR
- 未決事項

### 実装者役

- 設計に基づく実装
- Test
- Deviation報告
- 不明点の差し戻し

### 対外Docs作成者役

- README
- Setup
- Architecture説明
- Model取得手順
- GitHub向け日本語Docs

## 20. 現在地点と次

現在はPhase 0。

Project全体のDirectory構成は決定済み。

```text
src/margpa_runtime_llm/
├─ bootstrap/
├─ orchestration/
├─ shared/
├─ modules/
│  └─ inference/
├─ adapters/
│  └─ model_backends/
│     └─ llama_cpp/
└─ entrypoints/
   └─ cli/
```

上記Phase 1最小Directoryは作成済み。Source Fileはまだ作成していない。

次の設計議題：

- Local Backend最終決定
- Python Version
- Dependency管理方式
- Config形式
- Model Registry Schema
- Phase 1 Acceptance Criteria

## 21. 必読文書

- [project_requirements_20260718193435.md](../requirements/project_requirements_20260718193435.md)
- [system_architecture_20260718193435.md](../architecture/system_architecture_20260718193435.md)
- [project_directory_structure_20260718192110.md](../architecture/project_directory_structure_20260718192110.md)
- [model_strategy_20260718174637.md](../architecture/model_strategy_20260718174637.md)
- [runtime_governance_20260718174637.md](../governance/runtime_governance_20260718174637.md)
- [audit_evaluation_security_20260718174637.md](../governance/audit_evaluation_security_20260718174637.md)
- [implementation_roadmap_20260718193435.md](../architecture/implementation_roadmap_20260718193435.md)
