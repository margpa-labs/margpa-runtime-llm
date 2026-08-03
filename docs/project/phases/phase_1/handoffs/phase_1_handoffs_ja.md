# Phase 1 Handoffs／Reviews／Status Lossless Compilation
```yaml
document_id: phase_1_handoffs_lossless_compilation
phase: phase_1
status: frozen
language: ja
created_at: 2026-07-26 15:16:24 JST
frozen_at: 2026-07-26 15:16:24 JST
source_documents: 99
source_manifest: ../../phase_1_ex/operations/source_to_target_documentation_migration_manifest.json
source_hash_algorithm: sha512
supersedes: null
rag_default: true
```

## Compilation Policy

本書はPhase 1中に作成されたSource文書を、省略、要約、意味変更または再解釈せず、Source Path順に再配置したLossless Compilationである。

本文は原文を維持し、Directory Migration後も参照可能にするため、MarkdownのLocal Link Pathだけを機械的に正規化している。原文File、原文SHA-512および移動先はSource Manifestから一意に解決できる。

矛盾、旧判断、未解決事項および後継文書への置換前状態も削除していない。Currentな判断はCurrent Canonical文書とPhase Indexを参照する。

## Source Documents

<!-- SOURCE_BEGIN 1: docs/handoffs/common_documentation_single_writer_until_phase_1_ex_completion_20260721191915.md -->

### Source 1: `docs/handoffs/common_documentation_single_writer_until_phase_1_ex_completion_20260721191915.md`

- History Target: `docs/project/phases/phase_1/history/handoffs/common_documentation_single_writer_until_phase_1_ex_completion_20260721191915.md`
- Source SHA-512: `3d4b61c25bd949ba7ea6d4c15496fad606085da39e995e1fa718dd156dcfdd8d7a6b8a265f50a8fe16b65a30f8703c0c0d82a747dbae79a88b7ef23e4ad0c191`
- Source Size: `3153` bytes

# Phase 1-ex完了までのDocumentation単一Writer 共通Handoff

- 文書ID: `common_documentation_single_writer_until_phase_1_ex_completion`
- 状態: `current`
- 作成日時: `2026-07-21 19:19:15 JST`
- 更新日時: `2026-07-21 19:19:15 JST`
- Snapshot: `20260721191915`
- 作成担当: 設計者役担当Task
- 対象: 設計者役、将来の設計統括者役、Phase別設計者役、実装者役、対外Docs役
- 正本言語: 日本語
- Requirements: [phase_1_ex_interim_documentation_single_writer_and_roadmap_priority_requirements_20260721191915.md](../history/requirements/phase_1_ex_interim_documentation_single_writer_and_roadmap_priority_requirements_20260721191915.md)
- Latest Index: [documentation_index_20260721191915.md](../history/documentation_index_20260721191915.md)
- supersedes: なし（Phase 1-ex完了までの共通通知）

## 1. 即時適用事項

Phase 1-ex完了宣言までは、`docs/`配下の全Fileを現在の設計者役担当Taskが作成する。

```text
Single Documentation Writer : 現在の設計者役担当Task
Effective Until             : Phase 1-ex Completion Declaration
Scope                       : All docs/ Files and Phase 1-ex Public Docs
```

## 2. 各担当の対応

### 実装者役

- 実装結果、Test結果、変更File、Known Issueを会話または報告Payloadとして設計者役へ渡す。
- Phase 1-ex完了までは`implementer_status_*`を含むDocsを直接作成しない。
- Source／Test／Script等の実装Scopeは別途Accepted Handoffに従う。

### 対外Docs役

- README、Public Docs、CITATION、NOTICE、Phase Summary、Lossless Compilationを直接作成しない。
- 提案または校正Payloadを設計者役へ渡すことはできる。
- Phase 1-ex完了後のOwnershipは新Policy確定まで未決定とする。

### Phase別設計者役

- Phase内設計Payloadを現在の設計者役または移行後の設計統括者役へ返す。
- Phase 1-ex完了前はDocsへ直接書き込まない。

## 3. Phase Compilation

Phase単位の1File統合も現在の設計者役が担当する。

- Summary RewriteではなくLossless Compilationとする。
- 元本文を変更しない。
- Source Inventory、Size、SHA-512を記録する。
- 再抽出後のByte Size／SHA-512が1件でも不一致ならFail Closedとする。
- Privacy Scrubは別工程として記録する。

## 4. README Roadmap Priority

Phase 1-exで作成するREADMEは、`docs/public/roadmap_ja.md`を最優先の閲覧導線として上部で強調する。

Roadmapは、このProjectの現在地、全Phase、実装状況、将来機能、独立R&D統合Hookを示す中核公開文書として扱う。

README内でRoadmapを単なる末尾Linkまたは補助資料として扱わない。

## 5. Authorization Boundary

本HandoffはDocs Writerの一時統一を通知する。Source変更、Phase 1-ex開始、Git操作、GitHub公開、Lightning操作またはLicense条件決定を許可しない。

## 6. Append-Only

既存のRole別Write Scope文書を変更せず、Phase 1-ex完了までの期間限定Overrideを新しい共通Handoffとして追加した。

<!-- SOURCE_END 1: docs/handoffs/common_documentation_single_writer_until_phase_1_ex_completion_20260721191915.md -->

---

<!-- SOURCE_BEGIN 2: docs/handoffs/common_project_handoff_20260718174637.md -->

### Source 2: `docs/handoffs/common_project_handoff_20260718174637.md`

- History Target: `docs/project/phases/phase_1/history/handoffs/common_project_handoff_20260718174637.md`
- Source SHA-512: `4871f7ae589bec2b9ffdc5666d417f0ab26e73a89d1b3ad727ee66669b9614728c27a40fec99ad53d240eed27bb13d2ee886fa6bc181344ed56e50113abe5d70`
- Source Size: `8157` bytes

# MARGPA Runtime LLM 共通引き継ぎ

- 文書ID: `common_project_handoff`
- 状態: `current`
- 作成日時: `2026-07-18 17:46:37 JST`
- 更新日時: `2026-07-18 17:46:37 JST`
- 対象: すべての担当タスク
- 正本言語: 日本語
- 文書索引: [documentation_index_20260718174637.md](../history/documentation_index_20260718174637.md)

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

次の設計議題はProject全体のDirectory構成。

```text
margpa-runtime-llm/
├─ docs/
├─ models -> External Model Root
├─ src/
├─ tests/
├─ config/
├─ data/
├─ logs/
└─ scripts/
```

このSource構成はまだ未確定。

## 21. 必読文書

- [project_requirements_20260718174637.md](../history/requirements/project_requirements_20260718174637.md)
- [system_architecture_20260718174637.md](../history/architecture/system_architecture_20260718174637.md)
- [model_strategy_20260718174637.md](../history/architecture/model_strategy_20260718174637.md)
- [runtime_governance_20260718174637.md](../history/governance/runtime_governance_20260718174637.md)
- [audit_evaluation_security_20260718174637.md](../history/governance/audit_evaluation_security_20260718174637.md)
- [implementation_roadmap_20260718174637.md](../history/architecture/implementation_roadmap_20260718174637.md)

<!-- SOURCE_END 2: docs/handoffs/common_project_handoff_20260718174637.md -->

---

<!-- SOURCE_BEGIN 3: docs/handoffs/common_project_handoff_20260718193435.md -->

### Source 3: `docs/handoffs/common_project_handoff_20260718193435.md`

- History Target: `docs/project/phases/phase_1/history/handoffs/common_project_handoff_20260718193435.md`
- Source SHA-512: `3bf65b7dd1d2663010590159b0535b58b9d716b9ae154e67ed3820825953dfb206a7eb92762eaaf792e391db7b2a18c1823567883135f263a740c3b170c33a7c`
- Source Size: `9591` bytes

# MARGPA Runtime LLM 共通引き継ぎ

- 文書ID: `common_project_handoff`
- 状態: `current`
- 作成日時: `2026-07-18 19:34:35 JST`
- 更新日時: `2026-07-18 19:34:35 JST`
- 対象: すべての担当タスク
- 正本言語: 日本語
- supersedes: `common_project_handoff_20260718174637.md`
- 文書索引: [documentation_index_20260718193435.md](../history/documentation_index_20260718193435.md)

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

- [project_requirements_20260718193435.md](../history/requirements/project_requirements_20260718193435.md)
- [system_architecture_20260718193435.md](../history/architecture/system_architecture_20260718193435.md)
- [project_directory_structure_20260718192110.md](../history/architecture/project_directory_structure_20260718192110.md)
- [model_strategy_20260718174637.md](../history/architecture/model_strategy_20260718174637.md)
- [runtime_governance_20260718174637.md](../history/governance/runtime_governance_20260718174637.md)
- [audit_evaluation_security_20260718174637.md](../history/governance/audit_evaluation_security_20260718174637.md)
- [implementation_roadmap_20260718193435.md](../history/architecture/implementation_roadmap_20260718193435.md)

<!-- SOURCE_END 3: docs/handoffs/common_project_handoff_20260718193435.md -->

---

<!-- SOURCE_BEGIN 4: docs/handoffs/common_project_handoff_20260719142558.md -->

### Source 4: `docs/handoffs/common_project_handoff_20260719142558.md`

- History Target: `docs/project/phases/phase_1/history/handoffs/common_project_handoff_20260719142558.md`
- Source SHA-512: `22cbde44c5f45ed262b0941aa1c72e1e1783233ac7c60d3291e9792302be305ab2e3bb7e610487561789d4df1a4b5dd4f6b074a5af721b4b78fdba802224b3b6`
- Source Size: `7342` bytes

# MARGPA Runtime LLM 共通プロジェクト引き継ぎ

```yaml
document_state: current
created_at: 2026-07-19 14:25:58 JST
supersedes: common_project_handoff_20260718193435.md
project_root: margpa-runtime-llm/
```

## 1. 文書の目的

本書は、設計者役、実装者役、対外向けDocs作成者役など、複数タスク間で共有するプロジェクト共通情報の正本である。

タスク開始時は、まず最新の`documentation_index_YYYYMMDDHHMMSS.md`を読み、そこから現在有効な要件、Architecture、Governance、ADR、Operations、Handoff、User Manualを確認する。

Docsは原則として読み取り専用で扱い、担当範囲外の文書を勝手に変更しない。

## 2. プロジェクト識別情報

- Project Name: `margpa-runtime-llm`
- Display Name: `MARGPA Runtime LLM`
- 通称: `Nazuna Research Governance LLM`
- Project Root: `margpa-runtime-llm/`
- Shared Documentation Root: `margpa-runtime-llm/docs/`
- 初期実行環境: Apple M2 Pro、16GB RAM、macOS、Apple Silicon
- 初期Main Model: `Qwen3-4B-Q4_K_M.gguf`
- 初期Guard Model候補: `Qwen.Qwen3Guard-Gen-0.6B.Q8_0.gguf`
- 初期Judge Model候補: `Selene-1-Mini-Llama-3.1-8B-Q5_K_M.gguf`

ユーザーが`docs/`などの相対的なProject内パスだけを示した場合、Project Rootを基準として解釈する。

## 3. 現在有効な共通規則

- Documentation Rules: `docs/requirements/documentation_rules_20260719142558.md`
- Task Role Write Authority Policy: `docs/requirements/task_role_write_authority_policy_20260719142558.md`
- Phase Completion Backup Policy: `docs/operations/phase_completion_backup_policy_20260719142558.md`
- Current Roadmap: `docs/architecture/implementation_roadmap_20260719142558.md`
- Current Documentation Index: `docs/documentation_index_20260719142558.md`

文書名は英小文字と`_`を基本とし、末尾に作成時刻を秒まで含む`_YYYYMMDDHHMMSS`を付ける。既存文書は原則変更せず、変更時は新Timestampの後継文書を作る。新しいTimestampの文書を、その系列の最新候補として扱う。

## 4. タスク間の情報伝達

タスク間の情報伝達、進捗報告、レビュー結果、開始指示は、原則として`docs/`以下のTimestamp付き文書を介して行う。

主要な文書種別は次のとおりである。

- 要件・共通規則: `docs/requirements/`
- Architecture・Roadmap: `docs/architecture/`
- Governance設計: `docs/governance/`
- 意思決定記録: `docs/adr/`
- 運用・Backup・Release記録: `docs/operations/`
- タスク間Handoff・Status・Review: `docs/handoffs/`
- User Manual: `docs/user_manual/`
- 公開向け文書候補: Repository直下のREADME類、将来の`docs/public/`

## 5. 役割別の権限

詳細な正本は`task_role_write_authority_policy_20260719142558.md`とする。

### 5.1 設計者役

設計者役は、要件、Architecture、Governance、ADR、Operations、User Manual、Documentation Index、共通Handoff、設計者Handoff、各担当の開始用Handoffを管理する。

実装レビュー時は`src/`、`tests/`、`config/`、`scripts/`などを読み取り専用で確認し、ユーザーから修正を明示されていない限り、実装を勝手に修正しない。

### 5.2 実装者役

実装者役は、受理済みHandoffとユーザーの実装許可の範囲内で、`src/`、`tests/`、`scripts/`を変更し、`docs/handoffs/implementer_status_*`へ実装報告を新規作成する。

`config/`、Root直下のBuild・Dependency・Environment関連ファイルは、受理済みの設計またはHandoffで明示された場合に限り変更対象となる。

要件、Architecture、Governance、ADR、Operationsなどの正本文書は読み取り専用である。

### 5.3 対外向けDocs作成者役

対外向けDocs作成者役は、README類、将来の`docs/public/`、`docs/handoffs/external_docs_status_*`を担当する。

要件、Architecture、Governance、ADR、Operationsの正本は読み取り専用であり、公開文書へ変換する際も内容を勝手に変更しない。

### 5.4 現在の運用評価

設計者役と実装者役の分離は、Phase 1-AからPhase 1-Dまでの設計、Handoff、実装報告、独立レビューで実際に機能しており、Phase 1-Eでも同じ流れを継続している。

対外向けDocs作成者役は、現時点では十分な実運用実績がないため、権限境界は正式化するが、運用上の妥当性は今後検証する。

## 6. 現在のPhase状態

### 6.1 Phase 1

- Phase 1-A: Accepted／Complete
- Phase 1-B: Accepted／Complete
- Phase 1-C: Accepted／Complete
- Phase 1-D: Accepted／Complete
- Phase 1-E: Design Accepted／Implementation Reported／Independent Review Pending

Phase 1-Eについて、ユーザーから実装完了らしいとの共有はあるが、設計者役による最新Status、関連Source、Config、Testsの独立レビューはまだ完了していない。

したがって、Phase 1全体はまだ完了宣言前であり、Phase 1 Backupの発火条件にも達していない。

### 6.2 Phase 2以降

Phase 2以降の再構成済みRoadmapと主要Architecture方針は存在するが、Phase 2の実装はまだ開始しない。

## 7. Reviewの標準手順

1. 実装者役がTimestamp付きStatusを新規作成する。
2. 設計者役が最新Statusと関連実装を読み取り専用で確認する。
3. 受入条件、Test、回帰、文書整合性を確認する。
4. 問題があれば、Reviewと新しい実装者向けHandoffを作る。
5. 問題がなければ、Accepted Reviewを作る。
6. Reviewと同じ時点の新しいDocumentation Indexを作る。

Review後は、原則としてReview文書とDocumentation Indexを一緒に新規作成する。

## 8. Phase完了とBackupの発火条件

Backupは、実装者役が完了を報告した時点や、Phase内のSubphaseが完了した時点では取得しない。

各Top-Level Phaseについて、受入条件、独立レビュー、必要なFollow-up、User Manual、Indexなどを完了させ、設計者役がユーザーへ明示的に次の趣旨を宣言した直後をBackup取得タイミングとする。

> Phase Nは完了です。次はPhase N+1です。

全Phaseで同じ条件を用いる。Backup取得は次Phaseの実質的な変更開始より前に行う。

具体的なArchive、Manifest、SHA-512、除外対象、保管先、復元確認は`phase_completion_backup_policy_20260719142558.md`に従う。

この共通Handoffを読むこと自体は、Project外へのBackup作成や外部書き込みを許可しない。

## 9. 現在の次作業

1. 最新のPhase 1-E実装者Statusを特定して読む。
2. Phase 1-E関連のSource、Config、Testsを独立レビューする。
3. 必要ならFollow-up Handoffを作成し、実装修正後に再レビューする。
4. Phase 1全体の受入条件、User Manual、Docs、Indexを最終確認する。
5. 設計者役がPhase 1完了を明示する。
6. その直後にPhase 1 Backupを取得する。
7. Backup検証後、Phase 2へ移行する。

現時点では、Phase 1-Eの独立レビュー、Phase 1完了宣言、Phase 1 Backup、Phase 2実装のいずれも未完了である。

<!-- SOURCE_END 4: docs/handoffs/common_project_handoff_20260719142558.md -->

---

<!-- SOURCE_BEGIN 5: docs/handoffs/common_project_handoff_20260719164641.md -->

### Source 5: `docs/handoffs/common_project_handoff_20260719164641.md`

- History Target: `docs/project/phases/phase_1/history/handoffs/common_project_handoff_20260719164641.md`
- Source SHA-512: `6bed8a66d54f175479799da6e9f818f7a4cf5c44368182066e8aa63effab78fe79678648ccb68e32c538596dd02d4232c26d77af7c90553e90f2c53ff6f6d014`
- Source Size: `8177` bytes

# MARGPA Runtime LLM 共通プロジェクト引き継ぎ

```yaml
document_state: current
created_at: 2026-07-19 16:46:41 JST
supersedes: common_project_handoff_20260719142558.md
project_root: margpa-runtime-llm/
```

## 1. 文書の目的

本書は、設計者役、実装者役、対外向けDocs作成者役など、複数タスク間で共有するプロジェクト共通情報の正本である。

タスク開始時は、まず最新の`documentation_index_YYYYMMDDHHMMSS.md`を読み、そこから現在有効な要件、Architecture、Governance、ADR、Operations、Handoff、User Manualを確認する。

Docsは原則として読み取り専用で扱い、担当範囲外の文書を勝手に変更しない。

## 2. プロジェクト識別情報

- Project Name: `margpa-runtime-llm`
- Display Name: `MARGPA Runtime LLM`
- 通称: `Nazuna Research Governance LLM`
- Project Root: `margpa-runtime-llm/`
- Shared Documentation Root: `margpa-runtime-llm/docs/`
- 初期実行環境: Apple M2 Pro、16GB RAM、macOS、Apple Silicon
- 初期Main Model: `Qwen3-4B-Q4_K_M.gguf`
- 初期Guard Model候補: `Qwen.Qwen3Guard-Gen-0.6B.Q8_0.gguf`
- 初期Judge Model候補: `Selene-1-Mini-Llama-3.1-8B-Q5_K_M.gguf`

ユーザーが`docs/`などの相対的なProject内パスだけを示した場合、Project Rootを基準として解釈する。

## 3. 現在有効な共通規則

- Documentation Rules: `docs/requirements/documentation_rules_20260719142558.md`
- Task Role Write Authority Policy: `docs/requirements/task_role_write_authority_policy_20260719142558.md`
- Phase Completion Backup Policy: `docs/operations/phase_completion_backup_policy_20260719142558.md`
- Current Roadmap: `docs/architecture/implementation_roadmap_20260719164641.md`
- Current Documentation Index: `docs/documentation_index_20260719164641.md`
- Latest Phase Review: `docs/handoffs/designer_review_phase_1e_final_20260719164641.md`

文書名は英小文字と`_`を基本とし、末尾に作成時刻を秒まで含む`_YYYYMMDDHHMMSS`を付ける。既存文書は原則変更せず、変更時は新Timestampの後継文書を作る。新しいTimestampの文書を、その系列の最新候補として扱う。

## 4. タスク間の情報伝達

タスク間の情報伝達、進捗報告、レビュー結果、開始指示は、原則として`docs/`以下のTimestamp付き文書を介して行う。

主要な文書種別は次のとおりである。

- 要件・共通規則: `docs/requirements/`
- Architecture・Roadmap: `docs/architecture/`
- Governance設計: `docs/governance/`
- 意思決定記録: `docs/adr/`
- 運用・Backup・Release記録: `docs/operations/`
- タスク間Handoff・Status・Review: `docs/handoffs/`
- User Manual: `docs/user_manual/`
- 公開向け文書候補: Repository直下のREADME類、将来の`docs/public/`

## 5. 役割別の権限

詳細な正本は`task_role_write_authority_policy_20260719142558.md`とする。

### 5.1 設計者役

設計者役は、要件、Architecture、Governance、ADR、Operations、User Manual、Documentation Index、共通Handoff、設計者Handoff、各担当の開始用Handoffを管理する。

実装レビュー時は`src/`、`tests/`、`config/`、`scripts/`などを読み取り専用で確認し、ユーザーから修正を明示されていない限り、実装を勝手に修正しない。

### 5.2 実装者役

実装者役は、受理済みHandoffとユーザーの実装許可の範囲内で、`src/`、`tests/`、`scripts/`を変更し、`docs/handoffs/implementer_status_*`へ実装報告を新規作成する。

`config/`、Root直下のBuild・Dependency・Environment関連ファイルは、受理済みの設計またはHandoffで明示された場合に限り変更対象となる。

要件、Architecture、Governance、ADR、Operationsなどの正本文書は読み取り専用である。

### 5.3 対外向けDocs作成者役

対外向けDocs作成者役は、README類、将来の`docs/public/`、`docs/handoffs/external_docs_status_*`を担当する。

要件、Architecture、Governance、ADR、Operationsの正本は読み取り専用であり、公開文書へ変換する際も内容を勝手に変更しない。

### 5.4 現在の運用評価

設計者役と実装者役の分離は、Phase 1-AからPhase 1-Eまでの設計、Handoff、実装報告、独立レビューで実際に機能した。

対外向けDocs作成者役は、現時点では十分な実運用実績がないため、権限境界は正式化するが、運用上の妥当性は今後検証する。

## 6. 現在のPhase状態

### 6.1 Phase 1

- Phase 1-A: Complete／Accepted
- Phase 1-B: Complete／Accepted
- Phase 1-C: Complete／Accepted
- Phase 1-D: Complete／Accepted
- Phase 1-E: Complete／Accepted
- Phase 1実装Subphase: Complete
- Top-Level Phase 1: Documentation／Cross-phase Finalization Pending

Phase 1-Eは、Acceptance Criteria `22／22`、Default Test `161 passed`、Native Metal Test `2 passed`でAcceptedとなった。

ただし、現在のPhase 1 User ManualはPhase 1-A／1-Bのみを対象としている。Phase 1-C／1-D／1-Eを反映した後継ManualとCross-phase最終確認が残るため、Top-Level Phase 1の完了宣言はまだ行わない。

したがって、Phase 1 Backupの発火条件にもまだ達していない。

### 6.2 Phase 2以降

Phase 2以降の再構成済みRoadmapと主要Architecture方針は存在するが、Phase 2の実装はまだ開始しない。

## 7. Phase 1-E Review要約

```text
Blocking／High／Medium Finding : 0
Low Diagnostic Observation    : 1
Required Follow-up             : 0
Acceptance Criteria            : 22／22 Pass
Static／Default Gate           : Pass
Dependency／Offline Gate       : Pass
Native Metal Gate              : Pass
Final Decision                 : Accepted
```

Low Observationは、異なるSourceの不正値とExplicit Overrideが同時に存在する場合のError Code分類精度に関するものである。不正値は安全に拒否され、Phase 1-Eの動作や受入条件には影響しない。

## 8. Reviewの標準手順

1. 実装者役がTimestamp付きStatusを新規作成する。
2. 設計者役が最新Statusと関連実装を読み取り専用で確認する。
3. 受入条件、Test、回帰、文書整合性を確認する。
4. 問題があれば、Reviewと新しい実装者向けHandoffを作る。
5. 問題がなければ、Accepted Reviewを作る。
6. Reviewと同じ時点の新しいDocumentation Indexを作る。

Review後は、原則としてReview文書とDocumentation Indexを一緒に新規作成する。

## 9. Phase完了とBackupの発火条件

Backupは、実装者役が完了を報告した時点や、Phase内のSubphaseが完了した時点では取得しない。

各Top-Level Phaseについて、受入条件、独立レビュー、必要なFollow-up、User Manual、Indexなどを完了させ、設計者役がユーザーへ明示的に次の趣旨を宣言した直後をBackup取得タイミングとする。

> Phase Nは完了です。次はPhase N+1です。

全Phaseで同じ条件を用いる。Backup取得は次Phaseの実質的な変更開始より前に行う。

具体的なArchive、Manifest、SHA-512、除外対象、保管先、復元確認は`phase_completion_backup_policy_20260719142558.md`に従う。

この共通Handoffを読むこと自体は、Project外へのBackup作成や外部書き込みを許可しない。

## 10. 現在の次作業

1. Phase 1 macOS User Manualの後継版を作り、Phase 1-C／1-D／1-Eを反映する。
2. Current Macでの操作手順、Response Language、Thinking表示、Config、Cross-platform Hookの境界を記載する。
3. Phase 1-A～1-EのCross-phase最終確認を行う。
4. Review、Roadmap、Common Handoff、Indexの整合性を確認する。
5. 設計者役がTop-Level Phase 1完了を明示する。
6. その直後にPhase 1 Backupを取得・検証する。
7. Backup後にPhase 2へ移行する。

現時点では、Top-Level Phase 1完了宣言、Phase 1 Backup、Phase 2実装はいずれも未実施である。

<!-- SOURCE_END 5: docs/handoffs/common_project_handoff_20260719164641.md -->

---

<!-- SOURCE_BEGIN 6: docs/handoffs/common_project_handoff_20260719171836.md -->

### Source 6: `docs/handoffs/common_project_handoff_20260719171836.md`

- History Target: `docs/project/phases/phase_1/history/handoffs/common_project_handoff_20260719171836.md`
- Source SHA-512: `c4c94ccd60417e3a06f81468cbc254b8bf50297677815b37f6650bfd8f273313d44bfe4d6a624e1312eba948a47bb2f2736349fb5af3366cd9703f5e06e460ca`
- Source Size: `6078` bytes

# MARGPA Runtime LLM 共通プロジェクト引き継ぎ

```yaml
document_state: current
created_at: 2026-07-19 17:18:36 JST
supersedes: common_project_handoff_20260719164641.md
project_root: margpa-runtime-llm/
```

## 1. 文書の目的

本書は、設計者役、実装者役、対外向けDocs作成者役など、複数タスク間で共有するプロジェクト共通情報の正本である。

タスク開始時は、最新の`documentation_index_YYYYMMDDHHMMSS.md`からCurrent Requirements、Architecture、Governance、ADR、Operations、Handoff、User Manualを確認する。

Docsは原則として読み取り専用で扱い、担当範囲外の文書を勝手に変更しない。

## 2. プロジェクト識別情報

- Project Name: `margpa-runtime-llm`
- Display Name: `MARGPA Runtime LLM`
- 通称: `Nazuna Research Governance LLM`
- Project Root: `margpa-runtime-llm/`
- Shared Documentation Root: `margpa-runtime-llm/docs/`
- 初期実行環境: Apple M2 Pro、16GB RAM、macOS、Apple Silicon
- Main Model: `Qwen3-4B-Q4_K_M.gguf`
- Guard Model候補: `Qwen.Qwen3Guard-Gen-0.6B.Q8_0.gguf`
- Judge Model候補: `Selene-1-Mini-Llama-3.1-8B-Q5_K_M.gguf`

ユーザーが`docs/`等の相対的なProject内Pathだけを示した場合、Project Root基準で解釈する。

## 3. Current Entry Points

- Documentation Rules: `docs/requirements/documentation_rules_20260719171836.md`
- Task Role Authority: `docs/requirements/task_role_write_authority_policy_20260719142558.md`
- Phase Backup Policy: `docs/operations/phase_completion_backup_policy_20260719171836.md`
- Known Issues／Observations: `docs/operations/known_issues_and_observations_20260719171836.md`
- Current Roadmap: `docs/architecture/implementation_roadmap_20260719171836.md`
- Phase 1 Readiness Review: `docs/handoffs/designer_review_phase_1_final_readiness_20260719171836.md`
- Current User Manual: `docs/user_manual/phase_1_macos_user_manual_20260719171836.md`
- Current Index: `docs/documentation_index_20260719171836.md`

文書はAppend-Onlyとし、内容変更時は新Timestampの後継文書を作る。

## 4. 役割別の権限

### 設計者役

Requirements、Architecture、Governance、ADR、Operations、User Manual、Index、Common／Designer Handoff、Reviewを管理する。

実装レビュー時、Source／Config／Testsは読み取り専用とし、修正許可なしにFixしない。

### 実装者役

Accepted Handoffとユーザー許可の範囲で`src/`、`tests/`、`scripts/`を変更し、`implementer_status_*`を作成する。Config／Root Fileは明示Scopeがある場合だけ変更する。

Canonical Docsは読み取り専用である。

### 対外向けDocs作成者役

README類、将来の`docs/public/`、`external_docs_status_*`を担当する。Canonical Docsは読み取り専用である。

### 運用評価

設計者役と実装者役の分離は、Phase 1-A～1-Eで有効に機能した。対外Docs役は権限定義済みだが、本格運用評価は今後行う。

## 5. Current Phase State

```text
Phase 0                                 : Complete
Phase 1-A                               : Complete／Accepted
Phase 1-B                               : Complete／Accepted
Phase 1-C                               : Complete／Accepted
Phase 1-D                               : Complete／Accepted
Phase 1-E                               : Complete／Accepted
Phase 1 Cross-phase Readiness           : Pass
Phase 1 User Manual                     : Ready
Phase 1 User Acceptance Test            : Waiting
Designer Completion／Phase 2 Eligible   : Waiting
Phase 1 Backup                          : Not Triggered
Phase 2 Implementation                  : Not Authorized
```

Top-Level Phase 1は`Ready for User Acceptance Test`であり、まだ完了宣言前である。

## 6. Phase 1 Evidence

```text
Default Test       : 161 passed, 2 deselected
Native Metal Test  : 2 passed, 161 deselected
Ruff／Mypy         : Pass
Compileall／Bash   : Pass
Environment        : Python 3.13.14／arm64／Metal／Pass
uv Lock            : 117 packages
uv Offline         : 115 packages／No changes
```

Current User ManualはPhase 1-A～1-E、Language、Thinking、Platform境界、User Acceptance Checklistを含む。

## 7. Known Observation

`MARGPA-OBS-0001`：Mixed-source Presentation Config Error Attribution。

- Severity: Low
- State: Accepted Deferred
- 不正値は安全に拒否される
- Phase 1 Acceptance／BackupをBlockしない
- Phase 2 Config UIまたはExternal Release前のError Taxonomy整理時に再評価

詳細はCurrent Known Issues Registerを参照する。

## 8. Backup Dual Approval Gate

Phase Backupは次の両方が同じProject状態について成立した後に実行可能となる。

```text
Gate A:
  設計者役がPhase完了と次Phase移行可能を明示

Gate B:
  ユーザーがCurrent User Manualの受入テスト全項目合格を明示
```

片方だけ、Implementer Statusだけ、Subphase完了だけではBackupしない。

Gate成立後にSource、Config、Tests、Dependency、Model Definition等のMaterial Changeがあれば、影響範囲に応じて再Review／再Testする。

## 9. User Acceptance Test

対象：

- [phase_1_macos_user_manual_20260719171836.md](../history/user_manual/phase_1_macos_user_manual_20260719171836.md)

UserはManual Section 22の13項目を確認する。

合格時の推奨宣言：

```text
phase_1_macos_user_manual_20260719171836.mdの
Phase 1ユーザー受入テストは、全項目合格です。
```

## 10. Current Next Action

1. ユーザーがCurrent ManualでPhase 1 User Acceptance Testを行う。
2. 全項目合格なら対象Manualを明示して合格宣言する。
3. 設計者役がMaterial Changeなしを確認する。
4. 設計者役がPhase 1完了・Phase 2移行可能を宣言する。
5. Dual Approval Gate成立後、Phase 1 Backupを作成・検証する。
6. Backup後にPhase 2へ進む。

本Handoffを読むこと自体は、Backup、Project外Write、Phase 2実装を許可しない。

<!-- SOURCE_END 6: docs/handoffs/common_project_handoff_20260719171836.md -->

---

<!-- SOURCE_BEGIN 7: docs/handoffs/common_project_handoff_20260719195134.md -->

### Source 7: `docs/handoffs/common_project_handoff_20260719195134.md`

- History Target: `docs/project/phases/phase_1/history/handoffs/common_project_handoff_20260719195134.md`
- Source SHA-512: `ab68d146e00ce4f20c5e13677b5c7d8c29bc1356d4cb7156f03d6d6db59d0f2a3d62cf7afc605789d815fa0cb7b11fb6390d7d7edd9f41c78f76f6ab18aaeccb`
- Source Size: `3137` bytes

# MARGPA Runtime LLM 共通プロジェクト引き継ぎ

```yaml
document_state: current
created_at: 2026-07-19 19:51:34 JST
supersedes: common_project_handoff_20260719171836.md
project_root: margpa-runtime-llm/
```

## 1. Current State

```text
Phase 0                                 : Complete
Phase 1-A～1-E                          : Complete／Accepted
Phase 1 Cross-phase Readiness           : Pass before User findings
Phase 1 User Acceptance Test            : In Progress／Follow-up pending
Designer Completion／Phase 2 Eligible   : Waiting
Phase 1 Backup                          : Not Triggered
Phase 2 Implementation                  : Not Authorized
```

## 2. Current Entry Points

- 前Snapshot正本: [common_project_handoff_20260719171836.md](../history/handoffs/common_project_handoff_20260719171836.md)
- User Test補足: [phase_1_user_acceptance_findings_20260719195134.md](../history/user_manual/phase_1_user_acceptance_findings_20260719195134.md)
- Current Known Issues: [known_issues_and_observations_20260719195134.md](../history/operations/known_issues_and_observations_20260719195134.md)
- Follow-up要件: [phase_1_acceptance_follow_up_requirements_20260719195134.md](../history/requirements/phase_1_acceptance_follow_up_requirements_20260719195134.md)
- 実装担当Handoff: [implementer_handoff_phase_1_acceptance_follow_up_20260719195134.md](../history/handoffs/implementer_handoff_phase_1_acceptance_follow_up_20260719195134.md)
- Current Index: [documentation_index_20260719195134.md](../history/documentation_index_20260719195134.md)

変更のないProject識別、Role Authority、Backup Policy、Phase Evidenceは前Snapshotを継承する。

## 3. User Test Findings

- CLI Helpの大文字は仮引数名であり、Subcommand後に実値を指定する。動作は正常だがHelpを改善する。
- Hidden ThinkingがToken上限までにFinalへ到達しない場合、空表示になる。Safe Warning追加をFollow-up候補とする。
- Final先頭空行、Reasoning英語混在、一般Cross-platform完成はAccepted Deferredとする。
- Mac Native Runtime、Metal、通常生成、Language、Cancel、Default Test、Model Smoke、Model Rootはユーザー環境でPassした。

## 4. Lightning AI Studio

確認済みHost情報：

```text
OS                  : Ubuntu 24.04.4 LTS
Kernel              : Linux 6.8.0-1058-aws
Architecture        : x86_64
Virtualization      : docker
```

これはProfileのHost部分には十分だが、Compute／Backend部分には不足している。GPU Model、VRAM、Driver、CUDA、llama-cpp-python CUDA Build、CPU／Memory、Execution Environment表現を確認後にProfileを作成する。

## 5. Next Action

1. ユーザーがFollow-up実装を今行うか、Accepted Deferredにするか決める。
2. 実装する場合、実装担当がHandoffに従って変更・Test・Statusを作成する。
3. 設計者がReviewと新Indexを作成する。
4. User Acceptanceを再確認する。
5. Dual Approval Gate成立後にPhase 1 Backupへ進む。

## 6. Authorization Boundary

本HandoffはSource／Config変更、Lightning外部操作、GPU利用、依存導入、Phase 2実装を許可しない。

<!-- SOURCE_END 7: docs/handoffs/common_project_handoff_20260719195134.md -->

---

<!-- SOURCE_BEGIN 8: docs/handoffs/common_project_handoff_20260719200711.md -->

### Source 8: `docs/handoffs/common_project_handoff_20260719200711.md`

- History Target: `docs/project/phases/phase_1/history/handoffs/common_project_handoff_20260719200711.md`
- Source SHA-512: `76411fcfc72fce00e34e54bfcb9c8fb2ebd38338e4f0d6cf7810c637353638269c268cd3c359249219de0f5ba1c12882d230e7aa4639e157409a72e51e0dfd25`
- Source Size: `3179` bytes

# MARGPA Runtime LLM 共通プロジェクト引き継ぎ

```yaml
document_state: current
created_at: 2026-07-19 20:07:11 JST
supersedes: common_project_handoff_20260719195134.md
project_root: margpa-runtime-llm/
```

## 1. Current Phase State

```text
Phase 1-A～1-E                       : Complete／Accepted
Phase 1 User Acceptance             : In Progress／Follow-up pending
Phase 1 Completion／Backup           : Waiting
Phase 2 Implementation               : Not Authorized
Lightning Dual Profile Design        : Accepted Planning Only
Lightning Implementation／Validation : Waiting Future Phase Authorization
```

変更のないProject識別、Role Authority、Backup Policy、Phase Evidenceは[common_project_handoff_20260719195134.md](../history/handoffs/common_project_handoff_20260719195134.md)を継承する。

## 2. Current Entry Points

- Current Index: [documentation_index_20260719200711.md](../history/documentation_index_20260719200711.md)
- User Acceptance補足: [phase_1_user_acceptance_findings_20260719195134.md](../history/user_manual/phase_1_user_acceptance_findings_20260719195134.md)
- Phase 1 Follow-up: [implementer_handoff_phase_1_acceptance_follow_up_20260719195134.md](../history/handoffs/implementer_handoff_phase_1_acceptance_follow_up_20260719195134.md)
- Lightning要件: [lightning_ai_studio_dual_runtime_profile_requirements_20260719200711.md](../history/requirements/lightning_ai_studio_dual_runtime_profile_requirements_20260719200711.md)
- Lightning Architecture: [lightning_ai_studio_cross_environment_architecture_20260719200711.md](../history/architecture/lightning_ai_studio_cross_environment_architecture_20260719200711.md)
- Lightning Handoff: [implementer_handoff_lightning_ai_studio_dual_runtime_profiles_20260719200711.md](../history/handoffs/implementer_handoff_lightning_ai_studio_dual_runtime_profiles_20260719200711.md)

## 3. Lightning Decision

Lightning AI StudioはLinux x86_64 Docker Containerであり、CUDAとCPUの2 Profileを用意する。

```text
CUDA: external.lightning-linux-x86_64.cuda
CPU : external.lightning-linux-x86_64.cpu
```

初期版は`--profile`で明示選択し、GPU未割当時の暗黙CPU Fallbackを行わない。

Confirmed Environment：

```text
Ubuntu 24.04.4／Linux 6.8.0／x86_64／Docker
Python 3.12.11／4 vCPU／15 GiB RAM／9 GiB Swap
Tesla T4 15,360 MiB／Driver 580.159.03／CUDA 13.0／nvcc 13.0.88
```

## 4. Implementation Findings

- Current Execution Environment Detectionは`native`固定で、Container Hookが必要。
- Current llama.cpp Device DetectorはMetal以外をCPU扱いし、CUDA Hookが必要。
- 同一HostへCUDA／CPUの複数Defaultは登録できないため、初期版はExplicit Profileとする。
- CUDA Buildを`gpu_layers=0`でGPU未割当CPU実行できるかはNative検証事項。

## 5. Phase Boundary

Lightning対応はDeployment／Adapter境界に閉じるため、後続Governance／UI CoreをBlockしない。Phase 1 Snapshotへ未検証Profileを混入させず、Lightning対応PhaseでSetup／Build／Profile／Native Testをまとめて実施する。

## 6. Authorization Boundary

本HandoffはSource／Config／Tests変更、Lightning Install、GPU利用、Model Transfer、Phase 2実装を許可しない。

<!-- SOURCE_END 8: docs/handoffs/common_project_handoff_20260719200711.md -->

---

<!-- SOURCE_BEGIN 9: docs/handoffs/common_project_handoff_20260719202333.md -->

### Source 9: `docs/handoffs/common_project_handoff_20260719202333.md`

- History Target: `docs/project/phases/phase_1/history/handoffs/common_project_handoff_20260719202333.md`
- Source SHA-512: `6fb301f91ebebe2ddc7f689fc4c3e8a7bb439e33fe9ecb2cf068041b8d15cdea24bea9739a7c13c5416e09e3c44a18d82ee4ef862c336122ef85ff505501f838`
- Source Size: `2958` bytes

# MARGPA Runtime LLM 共通プロジェクト引き継ぎ

```yaml
document_state: current
created_at: 2026-07-19 20:23:33 JST
supersedes: common_project_handoff_20260719200711.md
project_root: margpa-runtime-llm/
```

## 1. Scope Change

ユーザーの期限、Codex／GPT利用可能量、各PhaseのCross-environment検証方針により、Lightning対応を後続PhaseからPhase 1-Fへ前倒しする。

Phase 1完了後にBackupを取得し、そのSnapshotを一度公開する方針である。

## 2. Current State

```text
Phase 1-A～1-E                 : Complete／Accepted
Acceptance Follow-up           : Ready／Implementation Pending
Phase 1-F Lightning            : Accepted／Implementation Pending
Phase 1 User Acceptance        : Waiting
Phase 1 Completion／Backup     : Waiting
Phase 1 Publication            : Planned／Not Authorized
```

## 3. Python Decision

```text
Project Support : CPython >=3.12,<3.14
Mac Primary     : CPython 3.13.14
Lightning       : CPython 3.12.11
```

LightningのPythonを期限のためだけに3.13へ上げない。Metadata／Lock／Static Tool／Verifierを3.12／3.13両対応にする。

## 4. Lightning Gate

CUDAはPhase 1-F必須。CPUは実装対象だが、同一CUDA BuildでGPU未割当CPU実行が成立せず別Buildが期限を圧迫する場合、Evidenceとユーザー承認により公開後Follow-upへ延期できる。

## 5. Current Entry Points

- Current Index: [documentation_index_20260719202333.md](../history/documentation_index_20260719202333.md)
- ADR-0015: [adr_0015_phase_1f_lightning_and_python_312_support_20260719202333.md](../history/adr/adr_0015_phase_1f_lightning_and_python_312_support_20260719202333.md)
- Requirements: [phase_1f_lightning_cross_environment_runtime_requirements_20260719202333.md](../history/requirements/phase_1f_lightning_cross_environment_runtime_requirements_20260719202333.md)
- Architecture: [lightning_ai_studio_cross_environment_architecture_20260719202333.md](../history/architecture/lightning_ai_studio_cross_environment_architecture_20260719202333.md)
- Roadmap: [implementation_roadmap_20260719202333.md](../history/architecture/implementation_roadmap_20260719202333.md)
- Implementer Handoff: [implementer_handoff_phase_1f_lightning_cross_environment_runtime_20260719202333.md](../history/handoffs/implementer_handoff_phase_1f_lightning_cross_environment_runtime_20260719202333.md)

## 6. Publication Boundary

- GitHub Repository URLによるSource公開はPhase 1完了後の対象。
- Lightning Live Web URLはCurrent CLIだけでは成立せず、Web UI／API／Securityが別途必要。
- Git初期化、Remote作成、Push、公開設定はユーザーの別途明示許可を必要とする。

## 7. Next Action

ユーザーが実装担当Taskへ、Phase 1-F HandoffとAcceptance Follow-up Handoffの実装開始を指示する。

## 8. Authorization Boundary

本HandoffはSource／Config／Lock変更、Lightning外部操作、Git／GitHub操作を自動許可しない。

<!-- SOURCE_END 9: docs/handoffs/common_project_handoff_20260719202333.md -->

---

<!-- SOURCE_BEGIN 10: docs/handoffs/common_project_handoff_20260720220216.md -->

### Source 10: `docs/handoffs/common_project_handoff_20260720220216.md`

- History Target: `docs/project/phases/phase_1/history/handoffs/common_project_handoff_20260720220216.md`
- Source SHA-512: `7655a22b2df2341e20c597b39e0bb1b32043d4767be3098346fe25fb55ecd2362cad75e551441f518105f4988f6133c3b487a3acec793680dc7fa2bb8b61213f`
- Source Size: `3186` bytes

# MARGPA Runtime LLM 共通プロジェクト引き継ぎ

```yaml
document_state: current
created_at: 2026-07-20 22:02:16 JST
supersedes: common_project_handoff_20260719202333.md
project_root: margpa-runtime-llm/
public_identity: Nazuna Research
```

## 1. Current State

```text
Phase 1-A～1-E                 : Complete／Accepted
Acceptance Follow-up           : Implemented／Review Pending
Phase 1-F Repository Work      : Reported Complete／Review Pending
Lightning CUDA Native Verify  : Waiting External Execution
Lightning CPU Native Verify   : Waiting External Execution
Phase 1 User Acceptance        : Waiting
Phase 1 Completion／Backup     : Waiting
Phase 1 Publication            : Planned／Not Authorized
Privacy Scrub                  : Complete for managed files
```

本HandoffはPhase 1-F Reviewを代替せず、実装完了をAcceptしない。

## 2. Identity／Privacy

- 第一者の公開識別子は`Nazuna Research`だけを使用する。
- 法的氏名、Local Account名、個人固有Path、Hostname、連絡先、CredentialをDocs、Source、Log、Sampleへ記録しない。
- 第三者の正式なAttributionは保持する。
- Privacy／Security削除はDocs Append-Onlyより優先する。
- `.venv/`、Model、Symlink、Cache、Local Runtime Dataは公開物へ含めない。

正本は[公開識別子・個人情報取扱方針](../history/requirements/public_identity_and_personal_information_policy_20260720220216.md)とする。

## 3. Current Entry Points

- Current Index: [documentation_index_20260720220216.md](../history/documentation_index_20260720220216.md)
- Documentation Rules: [documentation_rules_20260720220216.md](../history/requirements/documentation_rules_20260720220216.md)
- Privacy Policy: [public_identity_and_personal_information_policy_20260720220216.md](../history/requirements/public_identity_and_personal_information_policy_20260720220216.md)
- Scrub Report: [publication_privacy_scrub_report_20260720220216.md](../history/operations/publication_privacy_scrub_report_20260720220216.md)
- Phase 1-F Status: [implementer_status_phase_1f_lightning_cross_environment_runtime_20260719205819.md](../history/handoffs/implementer_status_phase_1f_lightning_cross_environment_runtime_20260719205819.md)

## 4. Platform／Python

```text
Project Support : CPython >=3.12,<3.14
Mac Primary     : CPython 3.13.14
Lightning       : CPython 3.12.11
```

Lightning CUDA／CPU ProfileはRepositoryに実装済みと報告されているが、Lightning Native Evidenceは未取得である。

## 5. Next Gate

1. 設計者がPhase 1-F Statusと関連実装をReviewする
2. Lightningへ一括Uploadする対象を確定する
3. Lightning CUDAをNative検証する
4. Lightning CPUをNative検証またはDispositionする
5. Phase 1 User ManualをCurrent機能へ更新する
6. ユーザー受入と設計者完了宣言の両方を成立させる
7. Backup／公開準備へ進む

Phase 1-Gの最小Web UI案は要件相談中であり、本Handoffでは実装許可済みと扱わない。

## 6. Authorization Boundary

本HandoffとPrivacy Scrubは、Lightning外部操作、Git初期化、GitHub作成／Push、公開、Phase 1-F Acceptance、Phase 1-G実装を許可しない。

<!-- SOURCE_END 10: docs/handoffs/common_project_handoff_20260720220216.md -->

---

<!-- SOURCE_BEGIN 11: docs/handoffs/common_project_handoff_20260720222402.md -->

### Source 11: `docs/handoffs/common_project_handoff_20260720222402.md`

- History Target: `docs/project/phases/phase_1/history/handoffs/common_project_handoff_20260720222402.md`
- Source SHA-512: `10f5f5fbb00517339dc27eaac7c95263008bdfe55c6683a66a7a7f28b13286227b0a10c090bb8f7cbe639159432183ea83c35a262b281cd3c0c1712c609b75d7`
- Source Size: `3081` bytes

# MARGPA Runtime LLM 共通プロジェクト引き継ぎ

```yaml
document_state: current
created_at: 2026-07-20 22:24:02 JST
supersedes: common_project_handoff_20260720220216.md
project_root: margpa-runtime-llm/
public_identity: Nazuna Research
```

## 1. Current State

```text
Phase 1-A～1-E                 : Complete／Accepted
Acceptance Follow-up           : Implemented／Review Pending
Phase 1-F Repository Work      : Reported Complete／Review Pending
Lightning Native Verification : Waiting
Phase 1 User Acceptance        : Waiting
Phase 1 Completion／Backup     : Waiting
Phase 1-ex Operations          : Added／Requirements Pending
Initial GitHub Publication     : Deferred until Phase 1-ex completion
Privacy Scrub                  : Complete for managed files
```

## 2. New Operational Decisions

- 原則として各Phaseの完了・次Phase着手可能状態でBackupを取得する。
- Backup確定後、同一SnapshotをPhase単位でGitHubへ反映する。
- 初回GitHub公開だけはPhase 1-ex完了後に行う。
- Phase 1-exは運用再整備を扱い、詳細は後続で定義する。
- 毎回、Backup Candidate内の`margpa-runtime-llm/`をSanitizeし、不要Fileをすべて除去する。
- 第一者の公開Identityは常に`Nazuna Research`へ統一する。

## 3. Runtime／Path Verification

- Default Test: 181 passed
- Ruff／Mypy: Pass
- Mac Metal Model Smoke: 2 passed／1 expected skip
- Managed Production Codeの個人固有`/Users/...`: 0件
- Test内の`/Users/example/...`: 架空のPrivacy Fixture
- `.venv/`: 作成時Absolute Pathを含むLocal生成物／公開除外
- `models`: Local Model StorageへのAbsolute Symlink／公開除外
- Lightning CUDA／CPU: Native Verification Pending

詳細は[Runtime動作・絶対Path境界 確認記録](../history/operations/runtime_and_absolute_path_verification_20260720222402.md)を参照する。

## 4. Current Entry Points

- [Documentation Index](../history/documentation_index_20260720222402.md)
- [Documentation Rules](../history/requirements/documentation_rules_20260720222402.md)
- [Backup／GitHub公開Policy](../history/operations/phase_completion_backup_policy_20260720222402.md)
- [Phase 1-ex Requirements Placeholder](../history/requirements/phase_1_ex_operations_reorganization_requirements_20260720222402.md)
- [Privacy Policy](../history/requirements/public_identity_and_personal_information_policy_20260720220216.md)
- [Phase 1-F Status](../history/handoffs/implementer_status_phase_1f_lightning_cross_environment_runtime_20260719205819.md)

## 5. Next Gate

1. Phase 1-Fの独立Review
2. Lightning Upload Scopeの確定
3. Lightning CUDA／CPU検証
4. Current User Manual／User Acceptance
5. Phase 1完了宣言／Backup
6. Phase 1-exの詳細要件定義と実施
7. Phase 1-ex完了後の初回GitHub公開

Phase 1-G最小Web UI案との順序・関係は未確定であり、後続要件定義で整理する。

## 6. Authorization Boundary

本HandoffはPhase 1-F Acceptance、Phase 1-ex実装、Phase 1-G実装、Backup生成、Git初期化、Commit、Push、GitHub公開、Lightning操作を許可しない。

<!-- SOURCE_END 11: docs/handoffs/common_project_handoff_20260720222402.md -->

---

<!-- SOURCE_BEGIN 12: docs/handoffs/common_project_handoff_20260720231036.md -->

### Source 12: `docs/handoffs/common_project_handoff_20260720231036.md`

- History Target: `docs/project/phases/phase_1/history/handoffs/common_project_handoff_20260720231036.md`
- Source SHA-512: `9f3eb8fa3b66149f18fbf2309cdcfd414942966b535f63edbf5637a0354f3e3940b5a0d5e64ff5de5df7faafb54413fb9a647c53f36cc6de081834466f0b588d`
- Source Size: `4034` bytes

# MARGPA Runtime LLM 共通プロジェクト引き継ぎ

```yaml
document_state: current
created_at: 2026-07-20 23:10:36 JST
supersedes: common_project_handoff_20260720222402.md
project_root: margpa-runtime-llm/
public_identity: Nazuna Research
current_design_role: 設計者役
future_design_role: 設計統括者役（Phase 1-exで変更予定）
```

## 1. Current State

```text
Phase 1-A～1-E                 : Complete／Accepted
Acceptance Follow-up           : Implemented／Review Pending
Phase 1-F Repository Work      : Reported Complete／Review Pending
Lightning Native Verification : Waiting
Phase 1 Completion／Backup     : Waiting
Phase 1-ex                     : Accepted Reservation／Not Started
Initial GitHub Publication     : Deferred until Phase 1-ex completion
Current Role Model             : Unchanged
Current Git State              : Not Initialized
Current Docs Layout            : Unchanged
```

## 2. Model Decision

```text
Guard Canonical : Qwen/Qwen3Guard-Gen-0.6B
Guard Local     : DevQuasar GGUF Q8_0を維持
Judge Canonical : AtlaAI/Selene-1-Mini-Llama-3.1-8B
Judge Local     : bartowski GGUF Q5_K_Mを維持
Official Weight : Download Deferred
```

Canonical SourceとDeployment Artifactを分離する。Seleneは日本語未保証のExperimental Judgeであり、唯一のJudgeへ固定しない。

## 3. Phase 1-ex Reservation

- 現設計者役をPhase 1-exで設計統括者役へ変更
- Phaseごとの設計者役配置を可能にする
- 設計統括者役／設計者役／実装者役／対外Docs役の権限再整理
- Git運用へ移行
- Git移行後のDocs運用を定義
- Docs Directory Structureを変更
- 移行完了後に各担当Taskへ通知
- Phase単位Lossless Compilationを導入
- Public Docsを対外Docs役がPhase完了ごとに更新

現在は予約だけで実行しない。

## 4. Lossless Rule

運用、共通ルール、Handoff、Requirements、ADR、Authorization Boundary等は要約・意訳・再解釈せず、Source本文をそのまま再整理する。

Source File、State、Size、SHA-512をManifest化し、統合文書から再抽出したPayloadが元SourceとByte単位で一致することを検証する。不一致時はFail Closedとする。

README等の説明用Derived Docsは編集可能だが、Canonical Compilationの代替にしない。

## 5. Public Docs Reservation

```text
README.md                              # 日本語敬語＋末尾English Abstract
LICENSE                                # 英語公式原文可
docs/public/overview_ja.md             # 日本語
docs/public/concept_ja.md              # 日本語
docs/public/roadmap_ja.md              # 日本語
docs/public/phases/phase_<id>_summary_ja.md
```

READMEへ何を作っているか、現在動く範囲、Phase Roadmap、Lightning公開URL、Setup、Model、Governance、Limitations、License等を記載する。

## 6. Current Entry Points

- [Documentation Index](../history/documentation_index_20260720231036.md)
- [Phase 1-ex Requirements](../history/requirements/phase_1_ex_operations_reorganization_requirements_20260720231036.md)
- [Lossless Compilation Requirements](../history/requirements/lossless_phase_document_compilation_requirements_20260720231036.md)
- [Public Docs Architecture](../history/architecture/public_documentation_and_phase_compilation_architecture_20260720231036.md)
- [Current Model Strategy](../history/architecture/model_strategy_20260720231036.md)
- [ADR-0016](../history/adr/adr_0016_canonical_model_and_deployment_artifact_separation_20260720231036.md)
- [ADR-0017](../history/adr/adr_0017_phase_1_ex_operating_model_and_documentation_transition_20260720231036.md)

## 7. Immediate Next Gate

Phase 1-exへ移らず、現在のPhase 1-F Review、Lightning Native Verification、User Manual、User Acceptance、Phase 1完了Gateを先に進める。

## 8. Authorization Boundary

本HandoffはModel Download、Role変更、Task作成、Git操作、Directory変更、Docs Compilation、Public Docs生成、Lightning操作、Backup、GitHub公開を許可しない。

<!-- SOURCE_END 12: docs/handoffs/common_project_handoff_20260720231036.md -->

---

<!-- SOURCE_BEGIN 13: docs/handoffs/common_project_handoff_20260721155020.md -->

### Source 13: `docs/handoffs/common_project_handoff_20260721155020.md`

- History Target: `docs/project/phases/phase_1/history/handoffs/common_project_handoff_20260721155020.md`
- Source SHA-512: `87b9bda324b35569bda2abdff83468b5dd3ecf3b7d0e12ec95bf23c90268b4ab82a89f75c8f3f04b2834caa00478fb41f5a521e18336f1462075f148a0b70877`
- Source Size: `4932` bytes

# MARGPA Runtime LLM 共通プロジェクト引き継ぎ

```yaml
document_state: current
created_at: 2026-07-21 15:50:20 JST
supersedes: common_project_handoff_20260720231036.md
project_root: margpa-runtime-llm/
public_identity: Nazuna Research
current_design_role: 設計者役
future_design_role: 設計統括者役（Phase 1-exで変更予定）
```

## 1. Current State

```text
Phase 1-A～1-F Repository／Mac          : Accepted
Phase 1-F Lightning Native             : Deferred
Phase 1-G Cross-thread Follow-up        : Implementer Report Received／Review Pending
Phase 1-H                              : Waiting Phase 1-G Acceptance
Phase 1 Completion／Backup             : Waiting
Phase 1-ex                             : Accepted Reservation／Not Started
Initial GitHub Publication             : Deferred until Phase 1-ex completion
Current Role                           : 設計者役
Git                                    : Not Initialized
Current Docs Rule                      : Append-only／Timestamp
```

## 2. Phase 1-ex Complete Reservation

- 現設計者役を設計統括者役へ変更
- Phase別設計者役を配置可能にする
- 設計統括者、設計者、実装者、対外Docs役のAuthority再整理
- Git運用へ移行
- Docs DirectoryをInventory、Plan、Rollback付きでMigration
- Phase単位Lossless Compilation
- Public Identity、License、CITATION、NOTICE、Access境界
- Backup、Commit、Tag、GitHubを同一Snapshotへ対応
- 移行後に全担当Taskへ新構造とEntry Pointを通知

Phase 1-ex開始指示までは実行しない。

## 3. Stable Canonical Docs

Phase 1-exで次を作成する。

```text
docs/requirements_specification_ja.md
docs/system_architecture_ja.md
docs/technology_selection_ja.md
docs/basic_design_ja.md
docs/runtime_governance_specification_ja.md
```

- File名は英語
- 本文は日本語
- Git移行後のStable Filename
- 対外向け説明と技術正本を兼ねる
- 詳細設計書は必須にせず、将来必要箇所だけ追加

## 4. Project Continuity Master

```text
docs/project_continuity/project_continuity_master_ja.md
```

公開可能な継続正本とし、Project全体、Current State、Decision、Authority、Known Issue、Next Gate、Source Mapを、新Taskが即時再開できる粒度で統合する。

```text
public_export : true
github_public : include
```

Secret、個人Path、Credential、実会話Log等は含めない。

## 5. Public Files

```text
README.md
LICENSE
CITATION.cff
NOTICE.md
docs/public/overview_ja.md
docs/public/concept_ja.md
docs/public/roadmap_ja.md
docs/public/phases/phase_<id>_summary_ja.md
```

READMEは日本語敬語＋末尾English Abstract。LICENSEは英語可。NOTICEは日本語／英語。その他Docs本文は日本語とする。

## 6. Phase 10 Original R&D

本体完成後、別Project／別Taskから次を疎結合統合するHookを予約する。

### 例外認識型安全統治機構

```text
研究領域：AI Safety Governance
```

内部安全傾向、周辺安全制御、入力文脈、生成過程等の相互作用と、例外を含む複合安全挙動を扱う。

### 分散証跡型例外認識エージェント統治安全機構

```text
研究領域：Multi-Agent Governance,
          Distributed Accountability,
          and Safety Assurance
```

複数主体間の責任、委譲、例外、改竄耐性付き証跡、全体整合、異常時の安全側制御を扱う。

公開Roadmapは名称、研究領域、1から2行概要だけとする。Project Continuity Masterには作業概念と統合Hookをもう少し詳しく記載する。Algorithm／核心は現在記載しない。

## 7. Generic Integration Rule

- External Governance Provider Port
- Capability Declaration
- Event／Evidence Reference
- Standard Governance Result
- `off／observe／enforce`
- Coreへ固有依存を入れない
- Providerなしで本体動作
- 存在しない権限を生成しない

## 8. Current Entry Points

- [最新Documentation Index](../history/documentation_index_20260721155020.md)
- [Phase 1-ex総合要件](../history/requirements/phase_1_ex_complete_operating_model_and_documentation_requirements_20260721155020.md)
- [Phase 1-ex Architecture](../history/architecture/phase_1_ex_documentation_continuity_and_publication_architecture_20260721155020.md)
- [ADR-0018](../history/adr/adr_0018_phase_1_ex_canonical_docs_continuity_and_future_r_and_d_20260721155020.md)
- [Phase 10 R&D Hook](../history/governance/phase_10_original_r_and_d_governance_extension_hooks_20260721155020.md)
- [Current Roadmap](../history/architecture/implementation_roadmap_20260721155020.md)

## 9. Immediate Next Gate

Phase 1-exとPhase 10へ移らず、Phase 1-G Cross-thread Follow-upの設計者Final Reviewを行う。

## 10. Authorization Boundary

本Handoffは、Role変更、Git操作、Docs Migration、Stable Docs生成、Backup、GitHub公開、Phase 10実装を許可しない。

<!-- SOURCE_END 13: docs/handoffs/common_project_handoff_20260721155020.md -->

---

<!-- SOURCE_BEGIN 14: docs/handoffs/common_project_handoff_20260721162242.md -->

### Source 14: `docs/handoffs/common_project_handoff_20260721162242.md`

- History Target: `docs/project/phases/phase_1/history/handoffs/common_project_handoff_20260721162242.md`
- Source SHA-512: `2d6a14c9dce871a422c57459da4fa9737348c17b54bb71fbf9da39ac0fcc951176090eb1d32757d8036909746bead68bd3d8437867eb2a5abdd1b96b07cfc603`
- Source Size: `3926` bytes

# MARGPA Runtime LLM 共通プロジェクト引き継ぎ

```yaml
document_state: current
created_at: 2026-07-21 16:22:42 JST
supersedes: common_project_handoff_20260721155020.md
project_root: margpa-runtime-llm/
public_identity: Nazuna Research
current_design_role: 設計者役
future_design_role: 設計統括者役（Phase 1-exで変更予定）
```

## 1. Current State

```text
Phase 1-G Cross-thread Follow-up : Implementer Report Received／Review Pending
Phase 1-H                       : Waiting Phase 1-G Acceptance
Phase 1 Completion／Backup      : Waiting
Phase 1-ex                      : Accepted Reservation／Not Started
Phase 10 Original R&D           : Accepted Future Reservation
Git                             : Not Initialized
```

## 2. Phase 1-ex Stable Docs

```text
docs/requirements_specification_ja.md
docs/system_architecture_ja.md
docs/technology_selection_ja.md
docs/basic_design_ja.md
docs/runtime_governance_specification_ja.md
docs/project_continuity/project_continuity_master_ja.md
```

File名は英語、本文は日本語。Project Continuity Masterを含め公開可能とする。

## 3. Official Original R&D Names

### EASA

```text
Exception Aware Safety Architecture
例外認識型安全統治機構
Research Area: AI Safety Governance
```

### DLAGSA

```text
Distributed LEA Agentic Governance & Safety Architecture
分散証跡型例外認識エージェント統治安全機構
Research Area: Multi-Agent Governance,
               Distributed Accountability,
               and Safety Assurance
```

### OCILNS

```text
Open Cognitive Interaction Ledger Network System
認知対話証跡台帳網
Research Area: Cognitive Interaction Provenance,
               Verifiable AI Systems,
               and Distributed Auditability
```

## 4. OCILNS Position

人、AI、Tool、外部Systemの認知的対話出来事を、検証、参照、継承、監査可能な改竄耐性付き証跡単位として扱う。

長期、分岐、多Model、多Threadでも、入力、出力、順序、時刻、Model情報、判断根拠、未解決事項、継承対象、改変検知情報を再接続可能な状態で維持することを目的とする。LLM応答精度の直接向上を目的としない。

内部使用技術はMARGPA Docsへ記載しない。

## 5. Phase 10 Integration

```text
EASA／DLAGSA
  → Generic External Governance Provider Port

OCILNS
  → Generic Evidence Ledger Port
```

3 Systemは別Project／別Taskで開発し、本体完成後にAdapterで統合する。

```text
EASA   : Config OFF／ON
DLAGSA : Config OFF／ON
OCILNS : Config OFF／ON
Default: All OFF
```

3 SystemなしでMARGPA Runtime LLM本体は完全動作する。

## 6. Public Disclosure

- Roadmap：正式名称、研究領域、1から2行概要
- System Architecture：接続位置とON／OFF
- Project Continuity Master：作業概念をやや詳しく記載
- Algorithm、具体的改竄耐性方式、核心：現在非掲載

構想の存在と方向性を先に公開する。

## 7. Current Entry Points

- [Latest Documentation Index](../history/documentation_index_20260721162242.md)
- [External R&D Requirements](../history/requirements/phase_1_ex_external_r_and_d_publication_and_integration_requirements_20260721162242.md)
- [Original R&D Catalog](../history/governance/phase_10_original_r_and_d_system_catalog_20260721162242.md)
- [Integration Architecture](../history/architecture/phase_10_external_r_and_d_integration_architecture_20260721162242.md)
- [ADR-0019](../history/adr/adr_0019_phase_10_original_r_and_d_public_names_and_switches_20260721162242.md)
- [Current Roadmap](../history/architecture/implementation_roadmap_20260721162242.md)

## 8. Immediate Next Gate

Phase 1-ex／Phase 10へ移らず、Phase 1-G Cross-thread Follow-upをReviewする。

## 9. Authorization Boundary

本Handoffは、Phase 1-ex開始、Config変更、External System統合、Git操作、公開を許可しない。

<!-- SOURCE_END 14: docs/handoffs/common_project_handoff_20260721162242.md -->

---

<!-- SOURCE_BEGIN 15: docs/handoffs/common_public_identity_and_naming_rule_20260721111659.md -->

### Source 15: `docs/handoffs/common_public_identity_and_naming_rule_20260721111659.md`

- History Target: `docs/project/phases/phase_1/history/handoffs/common_public_identity_and_naming_rule_20260721111659.md`
- Source SHA-512: `46d748ea4429ed776b3766ff0287df6274ea345804d402b115e1f6be410bade74cfa25768b691a421149ee601e3a646061de78a77d8b16b69c214c7834d64f59`
- Source Size: `2813` bytes

# MARGPA Runtime LLM 共通公開名義・名称規則

```yaml
document_state: current
created_at: 2026-07-21 11:16:59 JST
supersedes: none
applies_to: all_tasks
public_author_name: Nazuna Research
repository_owner: margpa-labs
public_repository: margpa-labs/margpa-runtime-llm
```

## 1. Mandatory Common Rule

今後、設計者役、設計統括者役、Phase設計者役、実装者役、対外Docs役、その他の担当Taskは、第一者の作者名、研究名義、Maintainer表示名、研究主体名として、原則次を使用する。

```text
Nazuna Research
```

廃止済み第一者名義を一般的な表示名やProject通称へ新規使用しない。

## 2. Required Exceptions

第一者名義を`Nazuna Research`以外にする必要性は、設計者役Taskだけが判断できる。

- GitHub Account Handleを正確に示す必要がある。
- GitHub noreply Commit Email等の技術識別子へ含まれる。
- 既存Artifact／History／Provenanceを正確に参照する。
- 旧名義を検索・分類・移行する規則内で例示する。
- 変更不能な外部識別子である。

例外か不明な場合は自動置換せず、設計者役またはユーザーへ確認する。

## 3. Fixed Mapping

```text
Public Author／Research Name : Nazuna Research
Commit Author Name           : Nazuna Research
GitHub Organization          : margpa-labs
Public Repository            : https://github.com/margpa-labs/margpa-runtime-llm
```

Repository OwnerとAuthor Nameを混同しない。

## 4. Commit Attribution

Commitから個人GitHub Accountへ辿れることは許容されている。

ただし、次を守る。

- Commit Author Nameは`Nazuna Research`とする。
- 個人の実Emailを不要に公開しない。
- Commit Email／GitHub Account帰属は技術識別子として別管理する。
- Git設定変更はPhase 1-exの専用Handoff前に行わない。

## 5. Access Boundary

```text
GitHub Source／Docs
  → 閲覧・評価限定のSource-available公開
  → 追加利用はLicenseで制限

Lightning Public UI
  → 公開されたUI機能は自由に操作・評価可能
  → Source再利用権や管理権限は付与しない
```

## 6. Current Execution Boundary

本書は今後の表記規則を即時適用する。

既存Docs／Sourceの全件置換、Git設定、Public Export、LICENSE／NOTICE／CITATION生成、GitHub PushはPhase 1-exまで実行しない。

## 7. Canonical Detail

詳細は次を参照する。

- [公開識別子・個人情報取扱方針](../history/requirements/public_identity_and_personal_information_policy_20260721111659.md)
- [Phase 1-ex 公開名義・Access・License要件予約](../history/requirements/phase_1_ex_publication_identity_access_and_license_requirements_reservation_20260721111659.md)

<!-- SOURCE_END 15: docs/handoffs/common_public_identity_and_naming_rule_20260721111659.md -->

---

<!-- SOURCE_BEGIN 16: docs/handoffs/common_public_identity_and_naming_rule_20260721112925.md -->

### Source 16: `docs/handoffs/common_public_identity_and_naming_rule_20260721112925.md`

- History Target: `docs/project/phases/phase_1/history/handoffs/common_public_identity_and_naming_rule_20260721112925.md`
- Source SHA-512: `11795d0799d48c0610d5860f821a2b3081ef6ece4c610e525626264bb1e0deb7cd253bd223ec7313c4baf7cedec26e25fd464d3641601c0692aaab0a9185caeb`
- Source Size: `2513` bytes

# MARGPA Runtime LLM 共通公開名義・名称規則

```yaml
document_state: current_mandatory
created_at: 2026-07-21 11:29:25 JST
supersedes: common_public_identity_and_naming_rule_20260721111659.md
applies_to: all_tasks
public_author_name: Nazuna Research
machine_safe_slug: nazuna-research
repository_owner: margpa-labs
public_repository: margpa-labs/margpa-runtime-llm
exception_authority: 設計者役Taskのみ
```

## 1. Mandatory Rule

全担当Taskは、第一者の名義、名称、作者名、研究名義、Maintainer表示名、研究主体名に次を使用する。

```text
Nazuna Research
```

承認済み例外はない。

## 2. Exception Authority

別の第一者識別子を使用する必要性は、設計者役Taskだけが判断できる。

他の担当Taskは独自判断で例外を作らず、実値をDocsへ書く前にEscalateする。

## 3. Fixed Mapping

```text
Public Author／Research Name : Nazuna Research
Commit Author Name           : Nazuna Research
Project Internal Name        : Nazuna Research Governance LLM
GitHub Organization          : margpa-labs
Public Repository            : https://github.com/margpa-labs/margpa-runtime-llm
```

## 4. Machine-safe Form

Spaceを使えない技術識別子に限り、`Nazuna Research`のMachine-safe Slugとして次を使用できる。

```text
nazuna-research
```

## 5. Commit Attribution

Commitから個人GitHub Accountへ辿れることは許容する。ただし、Commit Author Nameは`Nazuna Research`とし、Account Handleや個人EmailをDocsへ追加しない。

## 6. Access Boundary

```text
GitHub Source／Docs
  → 閲覧・評価限定のSource-available公開

Lightning Public UI
  → 公開された通常機能を自由に操作・評価可能
```

## 7. Prohibition

- 廃止済み第一者名義をHistorical Docsへ再挿入しない。
- 移行説明、検索例、禁止例にも実値を記録しない。
- Root Metadata、CITATION、NOTICE、READMEで別名義を作らない。
- Git設定変更はPhase 1-ex専用Handoff前に行わない。

## 8. Canonical Detail

- [公開名義・名称の統一決定](../history/requirements/public_identity_and_naming_decision_20260721112925.md)
- [公開識別子・個人情報取扱方針](../history/requirements/public_identity_and_personal_information_policy_20260721111659.md)
- [Phase 1-ex 公開名義・Access・License要件予約](../history/requirements/phase_1_ex_publication_identity_access_and_license_requirements_reservation_20260721111659.md)


<!-- SOURCE_END 16: docs/handoffs/common_public_identity_and_naming_rule_20260721112925.md -->

---

<!-- SOURCE_BEGIN 17: docs/handoffs/designer_handoff_20260718174637.md -->

### Source 17: `docs/handoffs/designer_handoff_20260718174637.md`

- History Target: `docs/project/phases/phase_1/history/handoffs/designer_handoff_20260718174637.md`
- Source SHA-512: `40700f22af959dd384b974cc845966d640bebb9273937056f368bc2d9200cf1554ca8b98cedf260d0b08bbfba0654c1d678c5e1d4730f38bbf368d48b9b4652c`
- Source Size: `1765` bytes

# 設計者役担当タスク 引き継ぎ

- 文書ID: `designer_handoff`
- 状態: `current`
- 作成日時: `2026-07-18 17:46:37 JST`
- 更新日時: `2026-07-18 17:46:37 JST`
- 対象: 設計者役担当タスク
- 正本言語: 日本語
- 共通引き継ぎ: [common_project_handoff_20260718174637.md](../history/handoffs/common_project_handoff_20260718174637.md)

## 1. 役割

- 要件の再整理・統合
- Architecture設計
- 技術候補比較
- Decision確定前のTrade-off提示
- ADR作成
- 未決事項管理
- 実装者向け仕様作成
- User決定事項の正本反映

## 2. 現在の設計者

この初期Snapshotを作成したTaskが設計者役を担当している。

## 3. 現在の完了事項

- Project目的統合
- Hardware制約整理
- 設計原則確定
- Initial Model選定
- Quantization選定
- Model Storage設計
- Runtime Governance基本方針
- ARGD／DAGD参照・要約
- Guard／Judge方針
- Audit基本要件
- Docs運用規則

## 4. 次の設計議題

Project全体のDirectory構成を設計する。

重点：

- Python Package名
- Domain／Application／Ports／Adapters
- Model Runtime
- Governance Runtime
- Guardrail
- Audit
- Storage
- API／UI
- Config
- Tests
- Runtime Data
- Git管理境界
- Cloud交換境界

## 5. 設計時の禁止事項

- 未決事項を勝手に確定扱いしない
- ARGD／DAGD原文を黙って改変しない
- Userの優先順位をModel性能中心へ変更しない
- 16GDを初期実装へ膨らませない
- FrameworkをDomain Logicにしない
- 実装許可前にSourceを作らない

## 6. 更新方法

実質的な設計変更は新Timestamp FileとADRを作る。

[documentation_rules_20260718174637.md](../history/requirements/documentation_rules_20260718174637.md)に従う。

<!-- SOURCE_END 17: docs/handoffs/designer_handoff_20260718174637.md -->

---

<!-- SOURCE_BEGIN 18: docs/handoffs/designer_handoff_20260718193435.md -->

### Source 18: `docs/handoffs/designer_handoff_20260718193435.md`

- History Target: `docs/project/phases/phase_1/history/handoffs/designer_handoff_20260718193435.md`
- Source SHA-512: `cf08b2426b546f8348c5bc2b8ac96ea99d318ad4bd7c35ec63c14c701bd94b89a77dd47c092e6558ef2bbcc44e759d47f777fab2cc003934e265b2d6d11f8784`
- Source Size: `1948` bytes

# 設計者役担当タスク 引き継ぎ

- 文書ID: `designer_handoff`
- 状態: `current`
- 作成日時: `2026-07-18 19:34:35 JST`
- 更新日時: `2026-07-18 19:34:35 JST`
- 対象: 設計者役担当タスク
- 正本言語: 日本語
- supersedes: `designer_handoff_20260718174637.md`
- 共通引き継ぎ: [common_project_handoff_20260718193435.md](../history/handoffs/common_project_handoff_20260718193435.md)

## 1. 役割

- 要件の再整理・統合
- Architecture設計
- 技術候補比較
- Decision確定前のTrade-off提示
- ADR作成
- 未決事項管理
- 実装者向け仕様作成
- User決定事項の正本反映

## 2. 現在の設計者

この初期Snapshotを作成したTaskが設計者役を担当している。

## 3. 現在の完了事項

- Project目的統合
- Hardware制約整理
- 設計原則確定
- Initial Model選定
- Quantization選定
- Model Storage設計
- Runtime Governance基本方針
- ARGD／DAGD参照・要約
- Guard／Judge方針
- Audit基本要件
- Docs運用規則
- Project全体のDirectory構成
- Python Package名`margpa_runtime_llm`
- Phase 1最小Directory作成

## 4. 次の設計議題

Phase 1実装前の技術選定とContractを設計する。

重点：

- Local Backend最終決定
- llama.cppとllama-cpp-pythonの役割
- Python Version
- Dependency管理方式
- `pyproject.toml`方針
- Config形式
- Model Registry Schema
- Phase 1 Acceptance Criteria
- Test Strategy詳細

## 5. 設計時の禁止事項

- 未決事項を勝手に確定扱いしない
- ARGD／DAGD原文を黙って改変しない
- Userの優先順位をModel性能中心へ変更しない
- 16GDを初期実装へ膨らませない
- FrameworkをDomain Logicにしない
- 実装許可前にSourceを作らない

## 6. 更新方法

実質的な設計変更は新Timestamp FileとADRを作る。

[documentation_rules_20260718193435.md](../history/requirements/documentation_rules_20260718193435.md)に従う。

<!-- SOURCE_END 18: docs/handoffs/designer_handoff_20260718193435.md -->

---

<!-- SOURCE_BEGIN 19: docs/handoffs/designer_handoff_phase_1b_model_runtime_20260718224308.md -->

### Source 19: `docs/handoffs/designer_handoff_phase_1b_model_runtime_20260718224308.md`

- History Target: `docs/project/phases/phase_1/history/handoffs/designer_handoff_phase_1b_model_runtime_20260718224308.md`
- Source SHA-512: `77a344edbc640ef9c1ac59952678006a25e6ee28095a7594f1a3fa092d766eb6c25a3b041e066c72f92e442853a395969cd5ae4c02bf41ec1d071c4023e817ce`
- Source Size: `15393` bytes

# Phase 1-B Model Runtime 実装担当Handoff

- 文書ID: `designer_handoff_phase_1b_model_runtime`
- 状態: `ready_for_implementation_authorization`
- 作成日時: `2026-07-18 22:43:08 JST`
- 更新日時: `2026-07-18 22:43:08 JST`
- 作成担当: 設計者役担当Task
- 対象: 実装者役担当Task
- 正本言語: 日本語
- Documentation Index: [documentation_index_20260718224308.md](../history/documentation_index_20260718224308.md)
- 詳細設計: [phase_1b_model_runtime_contract_20260718223203.md](../history/architecture/phase_1b_model_runtime_contract_20260718223203.md)
- Accepted ADR: [adr_0006_model_runtime_port_and_configuration_20260718224308.md](../history/adr/adr_0006_model_runtime_port_and_configuration_20260718224308.md)
- Phase 1-A Review: [designer_review_phase_1_environment_reproducibility_follow_up_20260718221255.md](../history/handoffs/designer_review_phase_1_environment_reproducibility_follow_up_20260718221255.md)
- Latest Implementer Status: [implementer_status_phase_1_environment_reproducibility_follow_up_20260718214958.md](../history/handoffs/implementer_status_phase_1_environment_reproducibility_follow_up_20260718214958.md)
- supersedes: なし（新規Phase 1-B専用Handoff系列）

## 1. Handoff Conclusion

Phase 1-Aは完了し、Phase 1-BのModel Runtime Contract詳細設計とADR-0006はユーザー承認済みである。

実装担当は、ユーザーからPhase 1-B実装開始と必要な書込範囲について明示的な許可を得た後、本Handoffの範囲を実装する。

本Handoffを受け取ったことだけで、実装、File変更、Model Hash計算、Dependency変更またはCommand実行が自動的に解禁されるわけではない。

## 2. Required Reading Order

実装開始前に、次を読み取り専用で確認する。

1. [documentation_index_20260718224308.md](../history/documentation_index_20260718224308.md)
2. [phase_1b_model_runtime_contract_20260718223203.md](../history/architecture/phase_1b_model_runtime_contract_20260718223203.md)
3. [adr_0006_model_runtime_port_and_configuration_20260718224308.md](../history/adr/adr_0006_model_runtime_port_and_configuration_20260718224308.md)
4. [designer_review_phase_1_environment_reproducibility_follow_up_20260718221255.md](../history/handoffs/designer_review_phase_1_environment_reproducibility_follow_up_20260718221255.md)
5. [python_environment_and_dependency_strategy_20260718201744.md](../history/architecture/python_environment_and_dependency_strategy_20260718201744.md)
6. [project_directory_structure_20260718192110.md](../history/architecture/project_directory_structure_20260718192110.md)
7. [model_strategy_20260718174637.md](../history/architecture/model_strategy_20260718174637.md)
8. [system_architecture_20260718193435.md](../history/architecture/system_architecture_20260718193435.md)

詳細設計と本Handoffが食い違う場合、独断で実装せず設計者へ報告する。

## 3. Authorization／Write Scope Gate

暫定担当分担で、実装者役の書込可能範囲は次とされている。

```text
src/
tests/
scripts/
docs/handoffs/implementer_status_*
```

Phase 1-Bの設計どおりに実装するには、追加で次への書込が必要になる。

```text
config/               # Model Registry／Deployment Profile
pyproject.toml         # Console Script登録等が必要な場合
```

したがって実装開始前に、ユーザーから少なくとも次を確認する。

1. Phase 1-B実装開始の許可
2. `config/`の作成・変更許可
3. 必要な場合の`pyproject.toml`変更許可
4. Model ArtifactのSHA-512計算許可
5. 実Model／Metal Integration Test実行許可

許可がないPathへ書き込まない。

Root File、要件正本、Architecture正本、Governance正本、ADR、Designer Reviewを勝手に編集しない。

## 4. Phase 1-B Objective

Qwen3-4B／llama.cppだけに固定された呼出コードではなく、将来のModel／Backend／Hardware／Cloud交換に耐えるModel非依存Runtime境界を実装する。

達成状態：

```text
CLI
  ↓
Bootstrap／Config／Registry
  ↓
Inference Service
  ↓
Model Port
  ↓
llama.cpp Production Adapter
  ↓
Qwen3-4B GGUF／Metal
```

Phase 1-Aの`metal_smoke.py`は技術Probeとして維持する。Production AdapterがSmoke専用ResultやScriptへ依存してはならない。

## 5. Locked Decisions

次はユーザー承認済みであり、実装担当が独断変更しない。

```text
Main Model                 : Qwen3-4B Q4_K_M
Backend                    : llama-cpp-python 0.3.34
Python                     : CPython 3.13.14
Initial Context            : 4,096
Thinking                   : Default OFF、設定で切替可能
Default max_new_tokens     : 512
Streaming                  : Default ON
CLI                        : 一問一答＋Streaming＋Stop
Multi-Turn                 : Phase 2
Port Instance              : 同時に1 Model
Concurrent Generation      : 1
Capability不足             : 明示Error
Stop                       : Cooperative Cancel
Config Format              : TOML
Public Contract／Config    : Pydantic v2／Immutable／extra forbid
Port Interface             : typing.Protocol
CLI Parser                 : argparse
```

性能値はProfile／Configで交換可能にし、Application Coreへ固定しない。

## 6. Required Deliverables

### 6.1 Inference Module

候補配置：

```text
src/margpa_runtime_llm/modules/inference/
├─ domain/
│  ├─ capabilities.py
│  ├─ errors.py
│  ├─ lifecycle.py
│  └─ model_definition.py
├─ contracts/
│  ├─ messages.py
│  ├─ generation.py
│  └─ runtime.py
├─ ports/
│  └─ model_port.py
├─ application/
│  └─ inference_service.py
└─ public.py
```

File分割は責務に応じて調整可能だが、Domain／Contract／Port／Application境界を混在させない。

### 6.2 llama.cpp Adapter

```text
src/margpa_runtime_llm/adapters/model_backends/llama_cpp/
├─ adapter.py
├─ chat_template.py
├─ error_mapping.py
└─ stream.py
```

Adapterだけが`llama_cpp`をImportする。

### 6.3 Bootstrap／Entrypoint

```text
src/margpa_runtime_llm/bootstrap/
├─ config_loader.py
├─ model_registry_loader.py
└─ phase1_application.py

src/margpa_runtime_llm/entrypoints/cli/
└─ main.py
```

### 6.4 Config

ユーザー許可後に次を作成する。

```text
config/models/qwen3_4b_q4_k_m.toml
config/profiles/local_macos_arm64.toml
```

### 6.5 Test

```text
tests/unit/inference/
tests/contract/model_port/
tests/integration/llama_cpp/
```

既存の高速Testとopt-in `model_smoke`を維持する。

## 7. Contract Requirements

最低限、次をModel非依存Contractとして実装する。

- `MessageRole`
- `ChatMessage`
- `ThinkingMode`
- `GenerationParameters`
- `GenerationRequest`
- `FinishReason`
- `TokenUsage`
- `GenerationTiming`
- `GenerationResult`
- `GenerationChunk`
- `GenerationStream`
- `GenerationTerminalState`
- `ModelDefinition`
- `ModelLoadConfig`
- `ModelCapabilities`
- `ModelRuntimeInfo`
- `ModelRuntimeReference`
- `InferenceWarning`
- `ModelLifecycleState`

Backend固有Dict、Native Generator、Native ExceptionをPublic Contractへ露出しない。

## 8. Model Port Requirements

概念責務：

```text
state
load
unload
capabilities
generate
stream
```

Lifecycle規則：

- Load前Generationは禁止
- 同じModelの再LoadはIdempotentを許容
- 別Modelの暗黙Reloadは禁止
- UnloadはIdempotent
- Generation中の別Requestは`model_busy`
- CancelをUnloadにしない
- Cancel後の再Generationを保証
- Resource解放を`finally`／Context Managerで保証

## 9. Capability Requirements

Phase 1-B Required Capability：

```text
chat
streaming
cooperative_cancel
stop_sequences
seed
token_usage
model_metadata
chat_template
thinking_control
gpu_offload
```

Expected CapabilityとEffective Runtime Capabilityを分離する。

Required Capabilityが不足した場合、Adapterで黙って無視、FallbackまたはDegradeしない。

## 10. Error Requirements

共通Error Codeを実装する。

```text
invalid_request
invalid_configuration
invalid_model_definition
model_not_found
model_integrity_mismatch
backend_unavailable
model_load_failed
model_not_loaded
model_already_loaded
model_busy
unsupported_capability
context_limit_exceeded
generation_failed
backend_protocol_error
model_unload_failed
```

User Cancelは通常終了`cancelled`とし、原則Errorにしない。

Native Error、Memory Address、User Absolute PathをCLIへそのまま出さない。

## 11. Context Policy

Generation前に次を確認する。

```text
formatted_prompt_tokens + max_new_tokens <= loaded_context_size
```

超過時は次を禁止する。

- Messageの無断削除
- 無断要約
- `max_new_tokens`の無断縮小
- Context Sizeの無断変更

`context_limit_exceeded`として明示する。

## 12. Registry／Config Requirements

Registryへ次を明示する。

- Internal Model Key
- Logical Role
- Distribution Repository
- Upstream Model
- Relative Artifact Path
- File Name
- Format／Quantization
- File Size
- SHA-512
- Backend Key／Version
- Architecture
- Native Context Limit
- Chat Template Source
- Verification State

Model ID、Quantization、BackendをFile名から推測しない。

Revision／Commitが不明な場合は推測値を入れず、Provenance不完全として明示する。

Model Root優先順位：

```text
Built-in Default
  ↓
Profile
  ↓
Environment Variable
  ↓
CLI Explicit Override
```

User固有絶対PathをTracked Configへ保存しない。

## 13. Qwen3／Thinking Requirements

Defaultは非Thinkingとする。

Sampling初期値：

```text
temperature      : 0.7
top_p            : 0.8
top_k            : 20
min_p            : 0.0
presence_penalty : 1.5
```

Thinking有効Profile候補：

```text
temperature      : 0.6
top_p            : 0.95
top_k            : 20
min_p            : 0.0
presence_penalty : 1.5
```

Thinking制御の優先順位：

1. Embedded Chat TemplateのHard Switch
2. Backend制約時だけ`/no_think`／`/think` Soft Switch
3. Soft Switch使用をWarning／Effective Capabilityへ記録

`llama-cpp-python 0.3.34`でPrivate API依存が必要な場合はAdapter内だけへ限定し、Regression Testを追加する。

空Thinking TagをModel Portで黙って削除しない。

## 14. CLI Requirements

最低限：

- 一問一答
- Prompt引数または標準入力
- Streaming Default ON
- `Ctrl+C`によるCancel
- `--thinking`相当の明示Override
- Generation主要値Override
- `model-info`相当
- Model／Backend／Capability表示
- Safe Error表示

CLIはConversation Historyを持たない。

Console Script登録に`pyproject.toml`変更が必要な場合は、ユーザー許可後に行う。

## 15. Test／Verification Requirements

### 15.1 Default Test

実ModelをLoadせず、高速に実行できること。

- Contract Validation
- Unknown Field拒否
- Lifecycle
- Fake Adapter Contract Suite
- Capability不足
- Error Mapping
- Context Overflow
- Config優先順位
- Registry Validation
- Streaming Sequence／Final Chunk
- Cancel／Close Idempotency

### 15.2 Opt-in実Model Test

- Local Modelがなければ明確にSkip
- Modelを暗黙Downloadしない
- Metal／GPU Offload
- Qwen3 Metadata
- Embedded Chat Template
- Thinking Default OFF
- Load／Generation／Streaming／Stop／Unload
- Cancel後の再Generation
- Token Usage／Timing

### 15.3 Quality Gate

```text
bash -n
ruff format --check
ruff check
mypy --strict
pytest default
pytest -m model_smoke
compileall
uv lock --check
uv sync --frozen --offline
```

実行したCommand、結果、Skip、環境制約をStatusへ記録する。

## 16. Phase 1-B Acceptance Criteria

```text
Model-independent Contract        : Pass
Model Port Protocol               : Pass
llama.cpp Adapter isolation       : Pass
Registry／Config Validation       : Pass
Qwen3-4B Load／Unload             : Pass
Default Context 4,096             : Pass
Thinking Default OFF             : Pass
One-shot Generation              : Pass
Streaming                        : Pass
Cooperative Cancel               : Pass
Post-cancel Generation           : Pass
Finish Reason Mapping            : Pass
Token Usage／Timing              : Pass
Capability Validation            : Pass
Safe Error Contract              : Pass
Unit／Contract／Integration Test  : Pass
Ruff／mypy --strict              : Pass
Modelの暗黙Downloadなし          : Pass
Phase 2以降への越境なし          : Pass
```

## 17. Explicit Out of Scope

次を同時実装しない。

- Multi-Turn
- Conversation History／Storage
- FastAPI／Web UI
- Runtime Governance本実装
- Audit Log本実装
- Guard Model
- Judge Model
- RAG
- Agent
- Tool実行
- 複数Model同時常駐
- Model Router
- MLX／Transformers／vLLM／Remote Adapter
- LangChain統合

## 18. Prohibited Shortcuts

- Application Coreから`llama_cpp`を直接Importする
- Smoke ResultをProduction Contractとして流用する
- Model PathをSourceへハードコードする
- File名からModel Metadataを推測する
- Capability不足を無視する
- Backend ErrorをそのままUserへ表示する
- StopをProcess Killで代替する
- Context超過時にMessageを黙って削除する
- Modelを暗黙Downloadする
- Model File名を変更する
- Model本体をProjectへ複製する
- Phase 2以降のPackageを先行Installする

## 19. Stop／Escalation Conditions

次の場合は作業を止め、ユーザーと設計者へ報告する。

- 詳細設計と実際のBackend APIが両立しない
- 新規Dependencyが必要
- `config/`またはRoot Fileへの許可がない
- Private API依存がAdapter外へ漏れる
- Thinking Default OFFを再現できない
- Required Capabilityを満たせない
- Model SHA-512／SizeがRegistry期待値と一致しない
- Model Artifactの出自について推測が必要になる
- Phase 1-B外の変更が必要になる
- 既存User変更と競合する

許可なくScopeを拡張しない。

## 20. Implementer Status Requirements

完了または問題発生時は、次の形式で新規Statusを作成する。

```text
docs/handoffs/implementer_status_phase_1b_model_runtime_YYYYMMDDHHMMSS.md
```

記録する内容：

- 実装Scope
- 作成／変更File一覧
- Contract一覧
- Port／Adapter依存方向
- Registry／Config実体
- Model SHA-512／Size
- Effective Runtime Capability
- Effective Config
- CLI使用例
- Default／Opt-in Test結果
- Ruff／mypy／compileall結果
- Metal／Memory／Timing観測
- Thinking制御方式
- Private API依存の有無
- Warning／Deviation／Fallback
- 未解決事項
- Phase 2以降へ着手していないこと

Status作成後、設計者へReviewを依頼する。

設計者はReview完了時にReview文書と最新Indexを同時作成する。

## 21. Known Non-blocking Items

- 通常Setupで`llama-cpp-python`を毎回Native再Buildする
- Soft Switch時に空Thinking Tagが残る場合がある
- Distribution Revision／Commitは現在未確定
- Raw Output／Display Output分離は後続設計事項
- `.DS_Store`再生成問題はPhase 1-B Contractとは別のRepository Hygiene事項

## 22. Completion Boundary

本Handoffの完了は、Phase 1-B Acceptance Criteriaを満たし、実装Statusを作成した時点である。

Phase 1-B完了はPhase 2開始の自動許可を意味しない。


<!-- SOURCE_END 19: docs/handoffs/designer_handoff_phase_1b_model_runtime_20260718224308.md -->

---

<!-- SOURCE_BEGIN 20: docs/handoffs/designer_handoff_phase_1c_deployment_platform_acceleration_20260719013109.md -->

### Source 20: `docs/handoffs/designer_handoff_phase_1c_deployment_platform_acceleration_20260719013109.md`

- History Target: `docs/project/phases/phase_1/history/handoffs/designer_handoff_phase_1c_deployment_platform_acceleration_20260719013109.md`
- Source SHA-512: `6f86d47e00844a5e002f2d53523fe14f4353d0454b0213f28f3eff60206ea9545a71fed0068cd41c3061ae799f83ef2dcfcc2516c3aef3cd6990428ab0532d99`
- Source Size: `11206` bytes

# Phase 1-C Deployment／Platform／Acceleration 実装担当Handoff

- 文書ID: `designer_handoff_phase_1c_deployment_platform_acceleration`
- 状態: `ready_for_implementation_authorization`
- 作成日時: `2026-07-19 01:31:09 JST`
- 更新日時: `2026-07-19 01:31:09 JST`
- Snapshot: `20260719013109`
- 作成担当: 設計者役担当Task
- 対象: 実装者役担当Task
- 正本言語: 日本語
- Documentation Index: [documentation_index_20260719013109.md](../history/documentation_index_20260719013109.md)
- Requirements: [phase_1c_deployment_platform_acceleration_requirements_20260719013109.md](../history/requirements/phase_1c_deployment_platform_acceleration_requirements_20260719013109.md)
- Architecture: [phase_1c_deployment_platform_acceleration_architecture_20260719013109.md](../history/architecture/phase_1c_deployment_platform_acceleration_architecture_20260719013109.md)
- Accepted ADR: [adr_0007_deployment_platform_acceleration_abstraction_20260719013109.md](../history/adr/adr_0007_deployment_platform_acceleration_abstraction_20260719013109.md)
- Phase 1-B Final Review: [designer_review_phase_1b_model_runtime_final_20260719001604.md](../history/handoffs/designer_review_phase_1b_model_runtime_final_20260719001604.md)
- supersedes: なし（新規Phase 1-C専用Handoff系列）

## 1. Handoff Conclusion

Phase 1-Bは完了・最終受入済みである。

ユーザーはPhase 1-Cを、Windows専用Hookではなく、Deployment／Platform／Accelerationを独立軸として扱う汎用Hookとする設計を承認した。

実装担当は、ユーザーからPhase 1-C実装開始とWrite Scopeについて明示的な許可を得た後、本Handoffの範囲を実装する。

本Handoffの作成は、実装、File変更、Native Build、Dependency変更またはCommand実行を自動的に解禁しない。

## 2. Required Reading Order

実装開始前に、次を読み取り専用で確認する。

1. [documentation_index_20260719013109.md](../history/documentation_index_20260719013109.md)
2. [phase_1c_deployment_platform_acceleration_requirements_20260719013109.md](../history/requirements/phase_1c_deployment_platform_acceleration_requirements_20260719013109.md)
3. [phase_1c_deployment_platform_acceleration_architecture_20260719013109.md](../history/architecture/phase_1c_deployment_platform_acceleration_architecture_20260719013109.md)
4. [adr_0007_deployment_platform_acceleration_abstraction_20260719013109.md](../history/adr/adr_0007_deployment_platform_acceleration_abstraction_20260719013109.md)
5. [designer_review_phase_1b_model_runtime_final_20260719001604.md](../history/handoffs/designer_review_phase_1b_model_runtime_final_20260719001604.md)
6. [phase_1b_model_runtime_contract_20260718223203.md](../history/architecture/phase_1b_model_runtime_contract_20260718223203.md)
7. [adr_0006_model_runtime_port_and_configuration_20260718224308.md](../history/adr/adr_0006_model_runtime_port_and_configuration_20260718224308.md)
8. [documentation_rules_20260718193435.md](../history/requirements/documentation_rules_20260718193435.md)

Response Language／Thinking設計は実装Scope外の参照資料として読む。

9. [response_language_and_thinking_output_policy_20260719013109.md](../history/architecture/response_language_and_thinking_output_policy_20260719013109.md)

## 3. Authorization／Write Scope Gate

暫定担当分担における実装者役の通常Write Scope：

```text
src/
tests/
scripts/
docs/handoffs/implementer_status_*
```

Phase 1-Cでは、設計上次への変更が必要になる可能性が高い。

```text
config/profiles/local_macos_arm64.toml
config/models/qwen3_4b_q4_k_m.toml
pyproject.toml                 # Marker／CLI設定等が必要な場合のみ
```

実装前にユーザーから少なくとも次を確認する。

1. Phase 1-C実装開始
2. `config/`変更
3. 必要な場合の`pyproject.toml`変更
4. Static／Default Test実行
5. 実Model／Metal Test実行
6. Docs Handoff Status作成

Requirements、Architecture、Governance、ADR、Designer ReviewおよびIndexを実装担当が編集しない。

## 4. Objective

Current Mac／Metalの成立状態を維持しながら、次を実現する。

```text
Model固有条件
Deployment固有条件
Runtime観測事実
```

を分離し、将来のWindows、Linux、Home Server、Cloud、CPU、CUDA、ROCm、Vulkan、Remote Backend追加時にApplication Coreを大規模変更しなくてよい境界を作る。

## 5. Locked Decisions

実装担当が独断変更しない。

```text
Phase名                         : Deployment／Platform／Acceleration Abstraction Hook
全Platform実装                  : 行わない
Current Native Verification     : macOS／Apple Silicon／Metalのみ
gpu_offload                     : Model必須からDeployment必須へ再分類
Mac Metal Profile               : gpu_offload必須を維持
Unknown Platform                : Macへ暗黙Fallbackしない
Profile Priority                : Explicit > Environment > Platform Default
Vendor／Backend Key             : 拡張可能Identifier
Required／Detected／Executed     : 分離
Tracked User Absolute Path      : 禁止
追加Heavy Dependency            : 追加しない
Windows／Linux Native Setup     : Scope外
CUDA／ROCm／Vulkan Build        : Scope外
Response／Thinking Policy       : Scope外
```

## 6. Required Deliverables

### 6.1 Deployment Requirement Contract

最低限、次を表現する。

- Host OS Key
- Architecture Key
- Execution Environment Key
- Compute Kind Key
- Vendor Key（Optional）
- Acceleration API Key
- Backend Build Variant Key
- Required Runtime Capabilities
- Fallback Policy
- Verification Stateまたは将来追加点

全候補Fieldを一度に実装する必要はない。Requirementsの意味境界を壊さない最小Contractとする。

### 6.2 Capability再分類

現在のModel Required Capabilityから`gpu_offload`を分離する。

```text
Model Required
  chat
  streaming
  cooperative_cancel
  stop_sequences
  seed
  token_usage
  model_metadata
  chat_template
  thinking_control

Mac Deployment Required
  gpu_offload
```

Model Registryの`gpu_offload`はOptionalへ移すか、Deployment側だけで要求する。二重の矛盾した正本を残さない。

### 6.3 Requirement Validation

Load後のEffective CapabilityとDeployment Required Capabilityを比較する。

不足時：

- 明示Error
- Resource解放
- Lifecycle破損防止
- Safe Error

を保証する。

暗黙CPU Fallbackは行わない。

### 6.4 Profile Resolver Hook

候補Priority：

```text
CLI／Application Explicit
  > MARGPA_PROFILE等のEnvironment
  > Platform Default Resolver
```

Current CLIのDefault挙動を維持しつつ、将来差し替え可能にする。

Windows Profileを作る必要はない。

### 6.5 Platform Normalization

Host Libraryの生値を正規化する最小境界を作る。

```text
Darwin → macos
AMD64／x86_64 → x86_64
arm64／aarch64 → arm64
```

未知値を推測で既知Platformへ割り当てない。

### 6.6 Runtime Observation Hook

Current `device="metal" if "MTL" else "cpu"`を、将来Backend固有Detectorへ交換できる境界へ整理する。

Phase 1-CでCUDA／ROCm等を正確に検出する必要はない。

Current Macで`metal`と`gpu_offload=true`が維持されること。

## 7. Suggested Implementation Sequence

1. Existing Testを変更前に確認する
2. Deployment Contractを追加する
3. Profile Loaderへ新Fieldを追加する
4. Current Mac ProfileをMigrationする
5. Capability再分類を行う
6. BootstrapへRequirement Validationを追加する
7. Profile Resolver／Platform Normalizerを追加する
8. Unit／Contract Testを追加する
9. Static／Default Gateを実行する
10. Metal Model Smokeを実行する
11. 実装担当Statusを新Timestampで作成する

## 8. Candidate File Scope

候補であり、不要なFileを量産しない。

```text
src/margpa_runtime_llm/bootstrap/config_loader.py
src/margpa_runtime_llm/bootstrap/phase1_application.py
src/margpa_runtime_llm/bootstrap/profile_resolver.py
src/margpa_runtime_llm/modules/inference/contracts/runtime.py
src/margpa_runtime_llm/modules/inference/domain/capabilities.py
src/margpa_runtime_llm/adapters/model_backends/llama_cpp/adapter.py
config/profiles/local_macos_arm64.toml
config/models/qwen3_4b_q4_k_m.toml
tests/unit/inference/
tests/contract/model_port/
tests/integration/llama_cpp/
```

`shared/platform/`は複数Consumerが存在する場合のみ追加する。

## 9. Required Test Cases

### Profile／Platform

- Current Mac Profile Parse Pass
- Unknown Field拒否
- Known OS／Architecture Normalize
- Unknown Platform明示Error
- Explicit Profile優先
- Environment Profile優先
- Platform Defaultは最後

### Capability

- Model Requiredに`gpu_offload`が含まれない
- Mac Deployment Requiredに`gpu_offload`が含まれる
- Runtime GPU Offload不足でMac ProfileはFail
- CPU概念ProfileではGPU不足を理由にFailしないContract Test
- Capability不足時にSafe Error

### Regression

- Static Check
- Default pytest
- Environment Verification
- `model-info`
- Qwen3 Generation
- Streaming
- Cancel
- Metal Model Smoke

Test件数の固定値ではなく、Failure／Errorが0であることを基準とする。

## 10. Prohibited Scope Expansion

- Windows Profile作成
- PowerShell Script作成
- Windows用Dependency Build
- Linux Profile作成
- Docker追加
- CUDA／ROCm／Vulkan Dependency追加
- MLX／Transformers／vLLM Adapter追加
- Multi-GPU実装
- Remote API実装
- Model Download
- Response Language実装
- Thinking表示Filter実装
- Phase 2機能

追加が必要と判断した場合、独断実装せず設計担当へ報告する。

## 11. Response／Thinking Observationの引き継ぎ

Phase 1 CLIで次を観測済みである。

- 日本語を明示しないThinking Requestが英語出力になった
- `日本語で`を明示すると日本語出力になった
- 2048 TokensではThinkingとFinal Answerが完了した
- Software Model交換を物理Hardware Slotとして解釈するScope Driftが発生した

これは単に4B／Q4であることだけが原因ではない。

- Project Context不足
- Input曖昧性
- Thinkingによる誤前提の深掘り
- Response Language未指定
- Output Budget
- Thinking Sampling Profile未分離

が関係する。

詳細は専用Architectureを参照する。

本Phase 1-Cでは修正しない。

## 12. Acceptance Evidence

実装担当Statusへ次を記録する。

- 変更File一覧
- Contract概要
- Capability Before／After
- Profile Schema Before／After
- Config Hash
- Static Check結果
- Default Test結果
- Environment Verification結果
- Model Smoke結果
- `model-info`のDevice／Capability
- Scope外変更がないこと
- Windows／LinuxをNative Verifiedと主張していないこと
- Known Non-blocking Item

## 13. Completion Boundary

Phase 1-C完了は、Current Mac Runtimeを維持しながら汎用Hookが実装された状態を意味する。

Windows、Linux、CUDA、ROCm、VulkanまたはHome Serverで実際に動作したことを意味しない。

Native Platform追加は、Hardware決定後の新Profile、Setup、Testおよび専用Acceptanceで行う。


<!-- SOURCE_END 20: docs/handoffs/designer_handoff_phase_1c_deployment_platform_acceleration_20260719013109.md -->

---

<!-- SOURCE_BEGIN 21: docs/handoffs/designer_handoff_phase_1d_response_language_20260719040237.md -->

### Source 21: `docs/handoffs/designer_handoff_phase_1d_response_language_20260719040237.md`

- History Target: `docs/project/phases/phase_1/history/handoffs/designer_handoff_phase_1d_response_language_20260719040237.md`
- Source SHA-512: `9c3bb128df6af17274e39f549bd8b361528357cda9375e03cf795e6eea5baa2010476ee9a9ef9d305cebaabdf91928980eb277051bc88a5c05e817d2fc03db8e`
- Source Size: `11585` bytes

# Phase 1-D Response Language Policy 実装担当Handoff

- 文書ID: `designer_handoff_phase_1d_response_language`
- 状態: `ready_for_implementation_authorization`
- 作成日時: `2026-07-19 04:02:37 JST`
- 更新日時: `2026-07-19 04:02:37 JST`
- Snapshot: `20260719040237`
- 作成担当: 設計者役担当Task
- 対象: 実装者役担当Task
- 正本言語: 日本語
- Documentation Index: [documentation_index_20260719040237.md](../history/documentation_index_20260719040237.md)
- Requirements: [phase_1d_response_language_requirements_20260719040237.md](../history/requirements/phase_1d_response_language_requirements_20260719040237.md)
- Architecture: [phase_1d_response_language_architecture_20260719040237.md](../history/architecture/phase_1d_response_language_architecture_20260719040237.md)
- Accepted ADR: [adr_0008_response_language_policy_20260719040237.md](../history/adr/adr_0008_response_language_policy_20260719040237.md)
- Previous Phase Final Review: [designer_review_phase_1c_final_20260719035156.md](../history/handoffs/designer_review_phase_1c_final_20260719035156.md)
- supersedes: なし（新規Phase 1-D専用Handoff系列）

## 1. Handoff Conclusion

Phase 1-A、1-Bおよび1-Cは完了・最終受入済みである。

ユーザーはPhase 1の残りを次のように分割する方針を承認した。

```text
Phase 1-D : Response Language Policy
Phase 1-E : Thinking Presentation Policy
```

Phase 1-DのRequirements、ArchitectureおよびADRはAcceptedであり、実装可能な粒度まで確定した。

実装担当は、ユーザーからPhase 1-D実装開始とWrite Scopeについて明示的な許可を得た後、本Handoffの範囲を実装する。

本Handoffの作成だけでは、Source／Config／Test変更またはCommand実行は解禁されない。

## 2. Required Reading Order

実装開始前に次を読み取り専用で確認する。

1. [documentation_index_20260719040237.md](../history/documentation_index_20260719040237.md)
2. [phase_1d_response_language_requirements_20260719040237.md](../history/requirements/phase_1d_response_language_requirements_20260719040237.md)
3. [phase_1d_response_language_architecture_20260719040237.md](../history/architecture/phase_1d_response_language_architecture_20260719040237.md)
4. [adr_0008_response_language_policy_20260719040237.md](../history/adr/adr_0008_response_language_policy_20260719040237.md)
5. [designer_review_phase_1c_final_20260719035156.md](../history/handoffs/designer_review_phase_1c_final_20260719035156.md)
6. [phase_1b_model_runtime_contract_20260718223203.md](../history/architecture/phase_1b_model_runtime_contract_20260718223203.md)
7. [phase_1c_deployment_platform_acceleration_architecture_20260719013109.md](../history/architecture/phase_1c_deployment_platform_acceleration_architecture_20260719013109.md)
8. [response_language_and_thinking_output_policy_20260719013109.md](../history/architecture/response_language_and_thinking_output_policy_20260719013109.md)
9. [documentation_rules_20260718193435.md](../history/requirements/documentation_rules_20260718193435.md)

旧Combined PolicyのResponse Language部分より、Phase 1-D専用Requirements／Architecture／ADRを優先する。

Thinking部分はPhase 1-E用の参照資料であり、本実装Scopeへ含めない。

## 3. Authorization／Write Scope Gate

暫定担当分担における実装者役の通常Write Scope：

```text
src/
tests/
scripts/
docs/handoffs/implementer_status_*
```

Phase 1-Dでは次の変更が必要になる。

```text
config/profiles/local_macos_arm64.toml
```

実装前にユーザーから少なくとも次を確認する。

1. Phase 1-D実装開始
2. `src/`／`tests/`変更
3. `config/`変更
4. Static／Default Test実行
5. 実Model／Metal Smoke実行
6. 実装担当Status作成

新規Dependencyまたは`pyproject.toml`変更は想定しない。必要になった場合は独断で追加せず設計者へ報告する。

Requirements、Architecture、Governance、ADR、Designer ReviewおよびDocumentation Indexを実装担当が編集しない。

## 4. Objective

Current Mac／Metal Runtimeを維持しながら、回答言語を次の設定だけで切り替えられる状態を作る。

```text
ja
en
auto
```

初期Defaultは`ja`とする。

## 5. Locked Decisions

実装担当が独断で変更しない。

```text
Phase名                  : Phase 1-D Response Language Policy
Allowed                  : ja／en／auto
Built-in Default         : ja
Current Profile Default  : ja
Environment              : MARGPA_RESPONSE_LANGUAGE
CLI                      : --response-language
Precedence               : Explicit > Environment > Profile > Built-in
auto                     : Language Instruction非注入
Policy Owner             : Application／Orchestration
Adapter Language Logic   : 禁止
Profile Schema           : 3
Model Registry Schema    : 変更なし
Natural Language解析     : 実装しない
Observed Language保証    : 行わない
New Dependency           : 追加しない
Thinking Presentation    : Phase 1-E
```

## 6. Required Deliverables

### 6.1 Response Language Contract

最低限次を型付きで表現する。

```text
ResponseLanguage
ResponseLanguageSource
ResolvedResponseLanguagePolicy
```

`GenerationParameters`へLanguageを追加しない。

### 6.2 Profile Migration

`config/profiles/local_macos_arm64.toml`を次へMigrationする。

```toml
schema_version = "3"

[response]
language = "ja"
```

Platform Registry参照Key／Pathを不要に変更しない。

### 6.3 Effective Config Resolution

次を実装する。

```text
MARGPA_RESPONSE_LANGUAGE
Explicit Response Override
Resolved Language
Resolved Source
```

不正値をDefaultへ黙ってFallbackしない。

### 6.4 Message Composer

Backend-independentなPure Functionまたは小Serviceとして実装する。

```text
Input:
  User Prompt
  Optional User System Message
  Resolved Response Policy

Output:
  tuple[ChatMessage, ...]
```

Cases：

- `ja`＋Systemなし
- `ja`＋Systemあり
- `en`＋Systemなし
- `en`＋Systemあり
- `auto`＋Systemなし
- `auto`＋Systemあり

User PromptとUser System文字列を破棄・書換えしない。

### 6.5 CLI

`generate`へ追加する。

```text
--response-language {ja,en,auto}
```

既存`--system`、`--thinking`、`--no-thinking`、Sampling Flagと併用可能にする。

### 6.6 Config Observability

`model-info`の`effective_config`へ次を追加する。

```text
response.language
response.source
```

Applied PolicyをObserved Output Languageと表示しない。

### 6.7 Public Export

将来APIが同じContractを利用できるよう、既存Public Surface方針に従って必要なContractをExportする。

不要なBackend固有Exportは追加しない。

## 7. Initial Instruction Semantics

実装するInstructionの意味：

```text
ja:
回答は原則として日本語で行う。
Userが回答言語を明示した場合は、その指定を優先する。

en:
英語を既定とする。
Userが別の回答言語を明示した場合は、その指定を優先する。

auto:
Applicationから言語指定を追加しない。
```

実装時の正確な文字列をUnit Test Fixtureとして固定する。

## 8. Suggested Implementation Sequence

1. Existing Static／Default Testを変更前に確認する
2. Response Contractを追加する
3. Config ContractとResolverを拡張する
4. Current ProfileをSchema `3`へMigrationする
5. Message Composerを追加する
6. CLIをComposerへ接続する
7. `model-info`へEffective Policyを追加する
8. Unit／CLI／Contract Testを追加する
9. Static／Default Gateを実行する
10. Environment／Lock／Offline Gateを実行する
11. Metal／Qwen3 Native Smokeを実行する
12. 実装担当Statusを新Timestampで作成する

## 9. Candidate File Scope

候補であり、不要なFileを量産しない。

```text
src/margpa_runtime_llm/modules/inference/contracts/response.py
src/margpa_runtime_llm/modules/inference/contracts/__init__.py
src/margpa_runtime_llm/modules/inference/public.py
src/margpa_runtime_llm/orchestration/response_language.py
src/margpa_runtime_llm/bootstrap/config_loader.py
src/margpa_runtime_llm/bootstrap/phase1_application.py
src/margpa_runtime_llm/entrypoints/cli/main.py
config/profiles/local_macos_arm64.toml
tests/unit/inference/test_response_language.py
tests/unit/inference/test_config_and_registry.py
tests/unit/inference/test_cli.py
tests/integration/llama_cpp/test_phase1b_runtime.py
```

原則変更不要：

```text
src/margpa_runtime_llm/adapters/model_backends/llama_cpp/adapter.py
src/margpa_runtime_llm/adapters/model_backends/llama_cpp/chat_template.py
src/margpa_runtime_llm/modules/inference/ports/model_port.py
config/models/qwen3_4b_q4_k_m.toml
pyproject.toml
uv.lock
```

## 10. Required Test Cases

### Contract／Resolver

- `ja／en／auto`受理
- 未知値拒否
- Default `ja`
- Schema `3`
- Explicit > Environment > Profile > Built-in
- Source Tracking
- Environment不正値のSafe Error

### Composer

- 6つのComposition Case
- Stable Language Instruction
- User Prompt完全保持
- User System完全保持
- `auto`でPolicy System Messageなし
- Empty Prompt／Systemの既存Validation
- Backend Import不要

### CLI

- 3 Language Choice
- Invalid Choice Exit `2`
- `--system`併用
- Thinking Flag併用
- Streaming／Non-streaming
- `model-info`表示

### Regression

- Ruff Format Check
- Ruff Check
- Mypy Strict
- Default pytest
- Environment Verification
- Bash Syntax Check
- `uv lock --check`
- Exact Offline Dry Run
- Native Metal Smoke
- Native CLI Default `ja`
- Native CLI Explicit `en`
- Native CLI `auto`

## 11. Acceptance Evidence

実装担当Statusへ次を記録する。

- 変更File一覧
- Contract／Resolver／Composer概要
- Profile Schema Before／After
- Profile SHA-512またはProject既定Hash
- `ja／en／auto` Message Composition Evidence
- Precedence Test Evidence
- `model-info` OutputのResponse部分
- Static Check結果
- Default Test結果
- Environment／Lock／Offline結果
- Native Metal Smoke結果
- Default日本語／Explicit英語／Autoの実行例
- Dependency変更がないこと
- Model AdapterへLanguage Logicを追加していないこと
- Phase 1-E Scopeが混入していないこと
- Known Non-blocking Item

## 12. Prohibited Scope Expansion

- `<think>` Tag削除
- Thinking表示／非表示
- Thinking Label変更
- Streaming Output Filter
- Raw Output／Display Output分離
- Thinking保存
- Thinking Sampling切替
- Language Detection Classifier
- Output翻訳
- BCP 47全対応
- Session／User Preference Storage
- FastAPI／Web UI
- Guard Model／Judge Model
- Governance Compiler
- Model Download／交換
- New Backend Adapter
- New External Dependency

必要と判断した場合、独断実装せず設計担当へ報告する。

## 13. Known Non-blocking Items

- ModelはDefault Languageに常に従うとは限らない
- Natural-languageの別言語指定をApplicationは判定しない
- Native Language Smokeは生成確率の影響を受ける
- `auto`はClassifierではない
- Thinking表示はPhase 1-Eまで現在挙動のまま
- Native Package再Buildを含む通常Setup Recipeは重い
- `.DS_Store`はmacOS操作で再生成される可能性がある

## 14. Completion Boundary

Phase 1-D完了は、Default日本語と`ja／en／auto`切替がApplication Policyとして成立し、Config／CLI／Test／Current Metal Runtimeで受け入れられた状態を意味する。

Phase 1-E、Strict Language Enforcement、Translation、Language EvaluationまたはWeb UI完成を意味しない。

<!-- SOURCE_END 21: docs/handoffs/designer_handoff_phase_1d_response_language_20260719040237.md -->

---

<!-- SOURCE_BEGIN 22: docs/handoffs/designer_handoff_phase_1d_response_language_20260719041847.md -->

### Source 22: `docs/handoffs/designer_handoff_phase_1d_response_language_20260719041847.md`

- History Target: `docs/project/phases/phase_1/history/handoffs/designer_handoff_phase_1d_response_language_20260719041847.md`
- Source SHA-512: `6f804bd42b65663ce3a052f44629d9e7237fd17018402c801bbd409297da33d71d5f09f7390ceb79d8b3422c9b6bce72359d7ccd2610557a2b16a86bf4ac834b`
- Source Size: `9587` bytes

# Phase 1-D Configuration Layer／Response Language 実装担当Handoff

- 文書ID: `designer_handoff_phase_1d_response_language`
- 状態: `ready_for_implementation_authorization`
- 作成日時: `2026-07-19 04:18:47 JST`
- 更新日時: `2026-07-19 04:18:47 JST`
- Snapshot: `20260719041847`
- 作成担当: 設計者役担当Task
- 対象: 実装者役担当Task
- 正本言語: 日本語
- Documentation Index: [documentation_index_20260719041847.md](../history/documentation_index_20260719041847.md)
- Configuration Requirements: [configuration_layer_requirements_20260719041847.md](../history/requirements/configuration_layer_requirements_20260719041847.md)
- Configuration Architecture: [configuration_layer_architecture_20260719041847.md](../history/architecture/configuration_layer_architecture_20260719041847.md)
- Phase Requirements: [phase_1d_response_language_requirements_20260719041847.md](../history/requirements/phase_1d_response_language_requirements_20260719041847.md)
- Phase Architecture: [phase_1d_response_language_architecture_20260719041847.md](../history/architecture/phase_1d_response_language_architecture_20260719041847.md)
- ADR-0008: [adr_0008_response_language_policy_20260719040237.md](../history/adr/adr_0008_response_language_policy_20260719040237.md)
- ADR-0009: [adr_0009_application_deployment_configuration_separation_20260719041847.md](../history/adr/adr_0009_application_deployment_configuration_separation_20260719041847.md)
- Previous Phase Final Review: [designer_review_phase_1c_final_20260719035156.md](../history/handoffs/designer_review_phase_1c_final_20260719035156.md)
- supersedes: `designer_handoff_phase_1d_response_language_20260719040237.md`

## 1. Handoff Conclusion

Phase 1-Dは、単なるLanguage Flag追加ではなく、先にConfiguration Layerの責務を分離した上でResponse Languageを接続する。

```text
Step A : Application Config／Deployment Profile分離
Step B : Response Language Resolver／Message Composer
```

前版Handoffの`response.language`をCurrent Mac Profileへ追加する指示は無効である。

本Handoffの作成は実装開始を自動的に解禁しない。

## 2. Required Reading Order

1. [documentation_index_20260719041847.md](../history/documentation_index_20260719041847.md)
2. [configuration_layer_requirements_20260719041847.md](../history/requirements/configuration_layer_requirements_20260719041847.md)
3. [configuration_layer_architecture_20260719041847.md](../history/architecture/configuration_layer_architecture_20260719041847.md)
4. [phase_1d_response_language_requirements_20260719041847.md](../history/requirements/phase_1d_response_language_requirements_20260719041847.md)
5. [phase_1d_response_language_architecture_20260719041847.md](../history/architecture/phase_1d_response_language_architecture_20260719041847.md)
6. [adr_0009_application_deployment_configuration_separation_20260719041847.md](../history/adr/adr_0009_application_deployment_configuration_separation_20260719041847.md)
7. [adr_0008_response_language_policy_20260719040237.md](../history/adr/adr_0008_response_language_policy_20260719040237.md)
8. [designer_review_phase_1c_final_20260719035156.md](../history/handoffs/designer_review_phase_1c_final_20260719035156.md)
9. [documentation_rules_20260718193435.md](../history/requirements/documentation_rules_20260718193435.md)

同一系列では`20260719041847`版を旧`20260719040237`版より優先する。

## 3. Authorization／Write Scope

実装前にユーザーから次を確認する。

1. Phase 1-D実装開始
2. `src/`／`tests/`変更
3. `config/application.toml`新規作成
4. `config/profiles/local_macos_arm64.toml`変更
5. Static／Default Test実行
6. Native Metal Test実行
7. 実装担当Status作成

Dependency追加、`pyproject.toml`または`uv.lock`変更は想定しない。必要になった場合は設計者へ返す。

## 4. Locked Configuration Decisions

```text
Common Config Path         : config/application.toml
Application Schema         : 1
Deployment Profile Schema  : 3
Generic Deep Merge         : 禁止
Selected Model Owner       : Application Config
Model Root Owner           : Application Config
Generation Owner           : Application Config
Response Owner             : Application Config
Platform Owner             : Deployment Profile
Hardware Load Tuning Owner : Deployment Profile
Artifact Owner             : Model Definition
```

## 5. Locked Response Decisions

```text
Allowed                 : ja／en／auto
Default                 : ja
Environment             : MARGPA_RESPONSE_LANGUAGE
CLI                     : --response-language
Precedence              : Explicit > Environment > Application > Built-in
auto                    : Language Instructionなし
Language Classifier     : 実装しない
Adapter Language Logic  : 禁止
Thinking Presentation   : Phase 1-E
```

## 6. Step A Required Deliverables

### 6.1 Application Config

`config/application.toml`を追加する。

含めるもの：

- `application_key`
- `selected_model`
- `model_root`
- `load_defaults`
- `generation`
- `response`

### 6.2 Deployment Profile Migration

Current ProfileをSchema `3`へMigrationする。

削除：

- `selected_model`
- `model_root`
- `generation`
- Common Load Field

保持：

- Host／Compute／Backend／Runtime Requirements
- Verification State
- Hardware `load_overrides`

### 6.3 Typed Composer

Application、Model、Deployment、Environment、CLIをField Ownerに従って合成する。

Generic Recursive Mergeを作らない。

### 6.4 Effective Config

最低限次を追加・維持する。

```text
application_key
profile_key
selected_model
model_root
load
generation
response
profile_resolution_source
applied_sources
```

## 7. Step B Required Deliverables

### 7.1 Response Contract

```text
ResponseLanguage
ResponseLanguageSource
ResponsePolicyConfig
ResolvedResponseLanguagePolicy
```

### 7.2 Resolver

```text
Explicit
  > MARGPA_RESPONSE_LANGUAGE
  > Application Config
  > Built-in ja
```

### 7.3 Message Composer

Backend-independentなPure Functionまたは小Serviceとする。

- `ja` Policy
- `en` Policy
- `auto` No-injection
- User Prompt保持
- User System保持
- Stable Composition

### 7.4 CLI

```text
--response-language {ja,en,auto}
```

### 7.5 Observability

`model-info`にApplication KeyとEffective Responseを含める。

## 8. Candidate File Scope

```text
config/application.toml
config/profiles/local_macos_arm64.toml
src/margpa_runtime_llm/bootstrap/config_loader.py
src/margpa_runtime_llm/bootstrap/phase1_application.py
src/margpa_runtime_llm/modules/inference/contracts/response.py
src/margpa_runtime_llm/modules/inference/contracts/__init__.py
src/margpa_runtime_llm/modules/inference/public.py
src/margpa_runtime_llm/orchestration/response_language.py
src/margpa_runtime_llm/entrypoints/cli/main.py
tests/unit/inference/test_config_and_registry.py
tests/unit/inference/test_response_language.py
tests/unit/inference/test_cli.py
tests/integration/llama_cpp/test_phase1b_runtime.py
```

原則変更しない：

```text
config/models/qwen3_4b_q4_k_m.toml
config/platforms/platform_registry.toml
src/margpa_runtime_llm/adapters/model_backends/llama_cpp/
src/margpa_runtime_llm/modules/inference/ports/model_port.py
pyproject.toml
uv.lock
```

## 9. Implementation Sequence

1. Migration前のEffective ConfigをTestで固定
2. Application Config Contract／Loader
3. Deployment Profile Schema `3`
4. Typed Composer
5. Tracked Config Migration
6. Existing Override／Validation接続
7. Configuration Unit Test
8. Response Contract／Resolver
9. Message Composer
10. CLI／`model-info`
11. Response Unit／CLI Test
12. Static／Default Gate
13. Environment／Lock／Offline Gate
14. Native Metal／Language Smoke
15. Implementer Status

## 10. Required Tests

### Configuration Ownership

- Application Configが共通Fieldを所有
- Deployment Profileが共通Fieldを拒否
- Hardware Override Allowlist
- Model Definitionの責務維持

### Composition

- Application Default
- Deployment Load Override
- Environment Override
- CLI Override
- Field別Precedence
- Migration前後のEffective値一致
- Cross-object Compatibility

### Response

- `ja／en／auto`
- Invalid Language拒否
- Source Tracking
- 6 Composition Cases
- User Content保持
- Streaming／Non-streaming Parity

### Regression

- Ruff Format／Check
- Mypy Strict
- Default pytest
- Environment Verification
- Bash Syntax
- `uv lock --check`
- Exact Offline Dry Run
- `model-info`
- Metal Smoke
- Default `ja`／Explicit `en`／`auto`

## 11. Acceptance Evidence

実装担当Statusへ次を記録する。

- 変更File一覧
- Config Before／After
- Field Ownership一覧
- Effective Config Before／After
- Application Config Hash
- Deployment Profile Hash
- Model Definition／Platform Registry Hash
- `model-info`該当部分
- Resolver／Composer Test Evidence
- Static／Default／Native結果
- 新規Dependencyなし
- Adapter Language Logicなし
- Phase 1-E Scope混入なし
- Known Non-blocking Item

## 12. Prohibited Scope Expansion

- Generic Deep Merge Engine
- Multiple Application Config UI
- Dynamic Reload
- Generation／Response Preset Directory
- Windows／Linux実Profile
- `<think>` Parser／Filter／Label
- Output Language Classifier／Translation
- Web UI／API
- Guard／Judge／Governance実行
- New Backend／Model Download
- New External Dependency

## 13. Completion Boundary

Phase 1-D完了は、共通Application ConfigがPlatform Profileから分離され、`ja／en／auto`がApplication PolicyとしてCurrent Mac／Metal Runtimeで成立した状態を意味する。

Phase 1-Eまたは他PlatformのNative対応完了を意味しない。

<!-- SOURCE_END 22: docs/handoffs/designer_handoff_phase_1d_response_language_20260719041847.md -->

---

<!-- SOURCE_BEGIN 23: docs/handoffs/designer_handoff_phase_1e_thinking_presentation_20260719123547.md -->

### Source 23: `docs/handoffs/designer_handoff_phase_1e_thinking_presentation_20260719123547.md`

- History Target: `docs/project/phases/phase_1/history/handoffs/designer_handoff_phase_1e_thinking_presentation_20260719123547.md`
- Source SHA-512: `10a51af82444ef0b7941ffce59d73b43de52d4ac652aa94bc4c3ac575c3cb91d0400ba3ab4af472f1a0206192bf56a7ffba8127ef92011a38145d86fff10b00c`
- Source Size: `10537` bytes

# Phase 1-E Thinking Presentation 実装担当Handoff

- 文書ID: `designer_handoff_phase_1e_thinking_presentation`
- 状態: `draft_waiting_for_adr_acceptance_and_implementation_authorization`
- 作成日時: `2026-07-19 12:35:47 JST`
- 更新日時: `2026-07-19 12:35:47 JST`
- Snapshot: `20260719123547`
- 作成担当: 設計者役担当Task
- 対象: 実装者役担当Task
- 正本言語: 日本語
- Documentation Index: [documentation_index_20260719123547.md](../history/documentation_index_20260719123547.md)
- Requirements: [phase_1e_thinking_presentation_requirements_20260719123547.md](../history/requirements/phase_1e_thinking_presentation_requirements_20260719123547.md)
- Architecture: [phase_1e_thinking_presentation_architecture_20260719123547.md](../history/architecture/phase_1e_thinking_presentation_architecture_20260719123547.md)
- Proposed ADR: [adr_0014_thinking_execution_presentation_and_persistence_separation_20260719123547.md](../history/adr/adr_0014_thinking_execution_presentation_and_persistence_separation_20260719123547.md)
- Previous Phase Final Review: [designer_review_phase_1d_final_20260719122035.md](../history/handoffs/designer_review_phase_1d_final_20260719122035.md)
- supersedes: なし（Phase 1-E Handoff新規系列）

## 1. Handoff Conclusion

Phase 1-Eは、Existing Model Portを壊さず、後段へ独立Presentation Moduleを追加するPhaseである。

```text
Raw Model Output
  → Model-declared Output Parser
  → Reasoning／Final Normalization
  → Hidden／Visible Renderer
  → CLI Display
```

本Handoffは実装手順を前もって共有するDraftである。

Proposed ADRのAccepted後継版と、ユーザーによる明示的なPhase 1-E実装解禁まで、実装者はSource／Config／Testを変更しない。

## 2. Required Reading Order

1. [documentation_index_20260719123547.md](../history/documentation_index_20260719123547.md)
2. [phase_1e_thinking_presentation_requirements_20260719123547.md](../history/requirements/phase_1e_thinking_presentation_requirements_20260719123547.md)
3. [phase_1e_thinking_presentation_architecture_20260719123547.md](../history/architecture/phase_1e_thinking_presentation_architecture_20260719123547.md)
4. ADR-0014のAccepted後継版（作成後に最新Indexから参照）
5. [designer_review_phase_1d_final_20260719122035.md](../history/handoffs/designer_review_phase_1d_final_20260719122035.md)
6. [phase_1d_response_language_architecture_20260719041847.md](../history/architecture/phase_1d_response_language_architecture_20260719041847.md)
7. [adr_0006_model_runtime_port_and_configuration_20260718224308.md](../history/adr/adr_0006_model_runtime_port_and_configuration_20260718224308.md)
8. [documentation_rules_20260718193435.md](../history/requirements/documentation_rules_20260718193435.md)

ProposedとAcceptedが両方存在する場合は、最新Indexが示すAccepted後継版を正本とする。

## 3. Authorization Gate

実装前に次の両方を必須とする。

1. ADR-0014 Decisionのユーザー承認
2. Phase 1-E実装開始のユーザー明示許可

実装時の想定Write Scope：

```text
src/
tests/
config/application.toml
config/models/qwen3_4b_q4_k_m.toml
docs/handoffs/implementer_status_phase_1e_*
```

Dependency追加、`pyproject.toml`変更、`uv.lock`変更は想定しない。必要になった場合は実装を拡大せず、理由を設計者とユーザーへ返す。

## 4. Locked Decisions候補

Accepted ADRで変更されない場合、次をLockedとする。

```text
Thinking Execution Default : disabled
Visibility Default         : hidden
Display Label Default      : 推論
Raw Persistence            : disabled only
Application Schema         : 2
Deployment Schema          : 3 unchanged
Model Definition Schema    : 2
Parser Selection           : Definition parser_key
Parser Hardcoding          : 禁止
Raw Model Port Contract    : 維持
Automatic Sampling Switch : 禁止
New Dependency             : なし
```

## 5. Required User-facing Behavior

### Default

```text
thinking_mode=disabled
visibility=hidden
```

Current Final-only CLI動作を維持する。

### Thinking Hidden

```bash
margpa-llm generate --prompt "..." --thinking --hide-thinking
```

Thinking Executionは`enabled`だが、stdoutにCanonical TagまたはReasoningを出さずFinalだけを表示する。

### Thinking Visible

```bash
margpa-llm generate \
  --prompt "..." \
  --thinking \
  --show-thinking \
  --thinking-label "推論"
```

Conceptual Output：

```text
<推論>...</推論>
Final Answer
```

### Separation

`--show-thinking`はThinking ExecutionをONにしない。`--thinking`はVisibilityをVisibleにしない。

## 6. Step A: Regression Fixture

変更前に次をTestで固定する。

- `GenerationResult.content`はRaw Text
- `GenerationChunk.text_delta`はRaw Delta
- Existing `--thinking／--no-thinking`がGeneration Overrideになる
- Existing DefaultはThinking Disabled
- Streaming Cancel／Close／Usage／Finish
- Phase 1-D `ja／en／auto`

## 7. Step B: Config Migration

### Application

`config/application.toml`：

```toml
schema_version = "2"

[presentation.thinking]
visibility = "hidden"
display_label = "推論"
persistence = "disabled"
```

### Environment

```text
MARGPA_THINKING_VISIBILITY
MARGPA_THINKING_LABEL
```

### Explicit

Bootstrapへ次を渡す。

```text
thinking_visibility
thinking_label
```

### Source

```text
visibility_source
display_label_source
persistence_source
```

Generic Deep Mergeを使用しない。

## 8. Step C: Model Definition Migration

`config/models/qwen3_4b_q4_k_m.toml`：

```toml
schema_version = "2"

[output_protocol.thinking]
parser_key = "tagged_thinking_v1"
opening_delimiter = "<think>"
closing_delimiter = "</think>"
```

Definition File SHA-512はLoaderが新Contentから再計算するExisting方式を維持する。Model Artifact SHA-512は変更しない。

## 9. Step D: Presentation Module

次を作成する。

- Presentation Contract
- Parser Port
- Parser Registry
- Plain Text Parser
- Tagged Stateful Parser
- Renderer
- Presentation Service

Model Backend Adapter内にDisplay Logicを追加しない。

## 10. Step E: Parser Requirements

### Recognition

- Optional Leading Whitespace + Leading Opening DelimiterだけをProtocolとして認識
- OpeningなしはPlain Final
- First ClosingでReasoning終了
- Final Contentを無断変更しない

### Streaming

- Stateful
- Delimiter Split対応
- Minimum Suffix Buffer
- Hidden No-flash
- 1-character Chunk対応
- Empty Delta対応

### Malformed

- Unclosed Status／Warning
- HiddenでReasoningを非表示
- VisibleでDisplay Closing Tagを補完
- Extra Delimiterを黙って削除しない

## 11. Step F: CLI

追加：

```text
--show-thinking
--hide-thinking
--thinking-label
```

`--show-thinking`と`--hide-thinking`をMutually Exclusiveにする。

Non-streamingとStreamingの両方がPresentation Serviceを使う。CLI内にCanonical Tag文字列をハードコードしない。

## 12. Step G: Observability

`model-info`に次を追加する。

- Effective Presentation Policy
- Field別Source
- Parser Key
- Application Schema
- Model Definition Schema

Display Labelは日本語を保持する。JSON OutputはExistingの`ensure_ascii=False`を維持する。

## 13. Candidate File Scope

Architecture正本のCandidate File Scopeを参照する。

特に次の境界を守る。

```text
Change Expected:
  config/application.toml
  config/models/qwen3_4b_q4_k_m.toml
  bootstrap config／parser composition
  new presentation module
  CLI
  tests

Keep Stable:
  model_port.py
  llama_cpp adapter／stream
  local_macos_arm64.toml
  platform_registry.toml
  pyproject.toml
  uv.lock
```

## 14. Required Test Matrix

### Config

- Schema `2`
- Field Ownership
- Precedence
- Source
- Invalid Value
- Label Validation

### Protocol

- Plain Parser
- Tagged Parser
- Unknown Key
- Invalid Delimiter
- Model Key／Architecture非依存

### Parser／Renderer

- Plain
- Complete
- Unclosed
- Extra Tag
- Hidden
- Visible
- Custom Label
- All Delimiter Splits
- One-character Chunks
- Streaming／Non-streaming Parity

### CLI

- Execution／Visibility Independence
- Flag Exclusivity
- Environment／CLI Override
- `model-info`
- Streaming／Non-streaming

### Regression／Native

- Ruff Format／Check
- Mypy Strict
- Default Pytest
- Compileall
- Environment Verification
- Bash Syntax
- `uv lock --check`
- Exact Offline Dry Run
- Metal Model Smoke
- Real CLI Hidden
- Real CLI Visible + Custom Label
- Phase 1-D `ja／en／auto`
- Cancel後の再Generation

## 15. Native Test Guidance

Model Outputは確率的である。Native TestでReasoning文章の完全一致を要求しない。

必須の判定：

- Hiddenで`<think>`／`</think>`がstdoutへ出ない
- HiddenでParserが検出したReasoningがstdoutへ出ない
- VisibleでCustom Labelが使われる
- VisibleでCanonical TagがDisplay Tagとして残らない
- Final Answerが存在する（ModelがLength終了したCaseはFinish Reasonを報告）

NativeでProtocolが生成されないまれなCaseは、Deterministic Parser Testを不合格とせず、Runtime ObservationとしてStatusに記録する。

## 16. Implementation Status Format

実装完了後は新Timestampで次を作成する。

```text
docs/handoffs/implementer_status_phase_1e_thinking_presentation_YYYYMMDDHHMMSS.md
```

必須記載：

- 実装Summary
- Changed／Added Files
- Schema Migration
- Parser／Renderer Structure
- Config／Environment／CLI Precedence
- All Test Commandsと結果
- Native Hidden／Visible Evidence
- Raw Persistenceが追加されていないこと
- Model Artifact Hash不変
- Dependency不変
- Known Limitation
- Acceptance Criteria対応表
- Review依頼

## 17. Stop／Escalation Conditions

次のいずれかが発生したら、独断でScopeを拡大せず設計者へ返す。

- Model Port Contractの破壊的変更が必要
- llama.cpp AdapterへDisplay Policyを入れる必要がある
- External Dependencyが必要
- Raw Reasoningの永続保存が必要
- Unknown ParserをSilent Fallbackしたい
- Hidden No-flashを満たせない
- Current Mac／Metal Regression
- Phase 1-D Language Regression
- Model FileまたはArtifact Hash変更が必要
- Phase 2以降のComponent Registry／Event Busが必要

## 18. Done Definition

RequirementsのAcceptance Criteria 22項目をすべてEvidence付きで判定でき、実装担当Statusが作成された状態をReview Readyとする。

Phase 1-EのComplete／Accepted判定は設計者役のIndependent Review後に行う。


<!-- SOURCE_END 23: docs/handoffs/designer_handoff_phase_1e_thinking_presentation_20260719123547.md -->

---

<!-- SOURCE_BEGIN 24: docs/handoffs/designer_handoff_phase_1e_thinking_presentation_20260719130303.md -->

### Source 24: `docs/handoffs/designer_handoff_phase_1e_thinking_presentation_20260719130303.md`

- History Target: `docs/project/phases/phase_1/history/handoffs/designer_handoff_phase_1e_thinking_presentation_20260719130303.md`
- Source SHA-512: `30272e66edd48a13daae3a88dc75fe9146f2c2b53529e3f502ef2f575341f1ea9cce9b1d23fc581198e2a2eb77e86533aab8a3ef7c3d04cc1598b8d169248aa0`
- Source Size: `10477` bytes

# Phase 1-E Thinking Presentation 実装担当Handoff

- 文書ID: `designer_handoff_phase_1e_thinking_presentation`
- 状態: `accepted_ready_for_implementation_authorization`
- 作成日時: `2026-07-19 13:03:03 JST`
- 更新日時: `2026-07-19 13:03:03 JST`
- Snapshot: `20260719130303`
- 作成担当: 設計者役担当Task
- 対象: 実装者役担当Task
- 正本言語: 日本語
- Documentation Index: [documentation_index_20260719130303.md](../history/documentation_index_20260719130303.md)
- Requirements: [phase_1e_thinking_presentation_requirements_20260719130303.md](../history/requirements/phase_1e_thinking_presentation_requirements_20260719130303.md)
- Architecture: [phase_1e_thinking_presentation_architecture_20260719130303.md](../history/architecture/phase_1e_thinking_presentation_architecture_20260719130303.md)
- Accepted ADR: [adr_0014_thinking_execution_presentation_and_persistence_separation_20260719130303.md](../history/adr/adr_0014_thinking_execution_presentation_and_persistence_separation_20260719130303.md)
- Previous Phase Final Review: [designer_review_phase_1d_final_20260719122035.md](../history/handoffs/designer_review_phase_1d_final_20260719122035.md)
- supersedes: `designer_handoff_phase_1e_thinking_presentation_20260719123547.md`

## 1. Handoff Conclusion

Phase 1-EのRequirements／Architecture／ADRはユーザーによりAcceptedとなった。

Default Display Labelは`高度推論`である。

```text
Raw Model Output
  → Model-declared Output Parser
  → Reasoning／Final Normalization
  → Hidden／Visible Renderer
  → CLI Display
```

本Handoffは実装担当への正式な設計引き渡しである。

ただし、正式Handoffの作成と実装開始許可は別である。ユーザーがPhase 1-E実装開始を明示するまで、Source／Config／Testを変更しない。

## 2. Required Reading Order

1. [documentation_index_20260719130303.md](../history/documentation_index_20260719130303.md)
2. [phase_1e_thinking_presentation_requirements_20260719130303.md](../history/requirements/phase_1e_thinking_presentation_requirements_20260719130303.md)
3. [phase_1e_thinking_presentation_architecture_20260719130303.md](../history/architecture/phase_1e_thinking_presentation_architecture_20260719130303.md)
4. [adr_0014_thinking_execution_presentation_and_persistence_separation_20260719130303.md](../history/adr/adr_0014_thinking_execution_presentation_and_persistence_separation_20260719130303.md)
5. [designer_review_phase_1d_final_20260719122035.md](../history/handoffs/designer_review_phase_1d_final_20260719122035.md)
6. [phase_1d_response_language_architecture_20260719041847.md](../history/architecture/phase_1d_response_language_architecture_20260719041847.md)
7. [adr_0006_model_runtime_port_and_configuration_20260718224308.md](../history/adr/adr_0006_model_runtime_port_and_configuration_20260718224308.md)
8. [documentation_rules_20260718193435.md](../history/requirements/documentation_rules_20260718193435.md)

同一系列では`20260719130303`版を`20260719123547`版より優先する。

## 3. Authorization Gate

Requirements／Architecture／ADR／HandoffはAccepted済みである。

実装に必要な残るGate：

```text
ユーザーによるPhase 1-E実装開始の明示許可
```

実装時のWrite Scope：

```text
src/
tests/
config/application.toml
config/models/qwen3_4b_q4_k_m.toml
docs/handoffs/implementer_status_phase_1e_*
```

Dependency追加、`pyproject.toml`変更、`uv.lock`変更は想定しない。必要になった場合は実装を拡大せず設計者／ユーザーへ返す。

## 4. Locked Decisions

```text
Thinking Execution Default : disabled
Visibility Default         : hidden
Display Label Default      : 高度推論
Raw Persistence            : disabled only
Application Schema         : 2
Deployment Schema          : 3 unchanged
Model Definition Schema    : 2
Parser Selection           : Definition parser_key
Parser Hardcoding          : 禁止
Raw Model Port Contract    : 維持
Automatic Sampling Switch : 禁止
New Dependency             : なし
```

`高度推論`はDisplay Labelであり、Reasoning品質の保証ではない。

## 5. Required User-facing Behavior

### Default

```text
thinking_mode=disabled
visibility=hidden
```

Current Final-only CLI動作を維持する。

### Thinking Hidden

```bash
margpa-llm generate --prompt "..." --thinking --hide-thinking
```

Thinkingは実行し得るが、stdoutにCanonical Tag／Reasoningを出さずFinalだけを表示する。

### Thinking Visible

```bash
margpa-llm generate \
  --prompt "..." \
  --thinking \
  --show-thinking
```

Default Output：

```text
<高度推論>...</高度推論>
Final Answer
```

Custom：

```bash
margpa-llm generate \
  --prompt "..." \
  --thinking \
  --show-thinking \
  --thinking-label "思考過程"
```

### Separation

`--show-thinking`はThinking ExecutionをONにしない。`--thinking`はVisibilityをVisibleにしない。

## 6. Step A: Regression Fixture

変更前に次をTestで固定する。

- `GenerationResult.content`はRaw Text
- `GenerationChunk.text_delta`はRaw Delta
- `--thinking／--no-thinking`はGeneration Override
- DefaultはThinking Disabled
- Streaming Cancel／Close／Usage／Finish
- Phase 1-D `ja／en／auto`

## 7. Step B: Application Config Migration

```toml
schema_version = "2"

[presentation.thinking]
visibility = "hidden"
display_label = "高度推論"
persistence = "disabled"
```

Environment：

```text
MARGPA_THINKING_VISIBILITY
MARGPA_THINKING_LABEL
```

Explicit Bootstrap Override：

```text
thinking_visibility
thinking_label
```

Source：

```text
visibility_source
display_label_source
persistence_source
```

Generic Deep Mergeを使用しない。

## 8. Step C: Model Definition Migration

```toml
schema_version = "2"

[output_protocol.thinking]
parser_key = "tagged_thinking_v1"
opening_delimiter = "<think>"
closing_delimiter = "</think>"
```

Definition File SHA-512はLoaderが再計算するExisting方式を維持する。Model Artifact SHA-512は変更しない。

## 9. Step D: Presentation Module

作成するもの：

- Presentation Contract
- Parser Port
- Parser Registry
- Plain Text Parser
- Tagged Stateful Parser
- Renderer
- Presentation Service

Model Backend Adapter内にDisplay Logicを追加しない。

## 10. Step E: Parser

Recognition：

- Optional Leading Whitespace + Leading Opening DelimiterだけをProtocolとして認識
- OpeningなしはPlain Final
- First ClosingでReasoning終了
- Final Contentを無断変更しない

Streaming：

- Stateful
- Delimiter Split対応
- Minimum Suffix Buffer
- Hidden No-flash
- 1-character Chunk
- Empty Delta

Malformed：

- Unclosed Status／Warning
- HiddenでReasoning非表示
- VisibleでDisplay Closing Tag補完
- Extra Delimiterを無断削除しない

## 11. Step F: CLI

```text
--show-thinking
--hide-thinking
--thinking-label
```

`--show-thinking`と`--hide-thinking`をMutually Exclusiveにする。

Non-streaming／Streamingの両方がPresentation Serviceを使う。CLIにCanonical Tag文字列をハードコードしない。

## 12. Step G: Observability

`model-info`に次を追加する。

- Effective Presentation Policy
- Default／Resolved Display Label
- Field別Source
- Parser Key
- Application Schema
- Model Definition Schema

JSONは`ensure_ascii=False`を維持する。

## 13. Candidate File Scope

```text
Change Expected:
  config/application.toml
  config/models/qwen3_4b_q4_k_m.toml
  bootstrap config／parser composition
  model definition contract
  new presentation module
  output protocol adapters
  CLI
  tests

Keep Stable:
  model_port.py
  llama_cpp adapter／stream
  local_macos_arm64.toml
  platform_registry.toml
  pyproject.toml
  uv.lock
```

## 14. Required Test Matrix

### Config

- Schema `2`
- Default `高度推論`
- Field Ownership／Precedence／Source
- Invalid Visibility／Label／Persistence

### Protocol

- Plain／Tagged Parser
- Unknown Key／Invalid Delimiter
- Model Key／Architecture非依存

### Parser／Renderer

- Plain／Complete／Unclosed／Extra Tag
- Hidden／Visible
- Default／Custom Label
- All Delimiter Splits
- One-character Chunks
- Streaming／Non-streaming Parity

### CLI

- Execution／Visibility Independence
- Flag Exclusivity
- Environment／CLI Override
- `model-info`
- Streaming／Non-streaming

### Regression／Native

- Ruff Format／Check
- Mypy Strict
- Default Pytest
- Compileall
- Environment Verification
- Bash Syntax
- `uv lock --check`
- Exact Offline Dry Run
- Metal Model Smoke
- Real CLI Hidden
- Real CLI Visible + Default `高度推論`
- Real CLI Visible + Custom Label
- Phase 1-D `ja／en／auto`
- Cancel後の再Generation

## 15. Native Test Guidance

Native TestでReasoning文章の完全一致を要求しない。

必須判定：

- HiddenでCanonical Tag／Reasoningがstdoutへ出ない
- Visibleで`<高度推論>...</高度推論>`が使われる
- Custom Labelが使われる
- Canonical TagがDisplay Tagとして残らない
- Final Answerが存在する

Protocolが生成されない確率的CaseはRuntime ObservationとしてStatusに記録し、Deterministic Parser Testと分離する。

## 16. Implementation Status

実装完了後は新Timestampで次を作成する。

```text
docs/handoffs/implementer_status_phase_1e_thinking_presentation_YYYYMMDDHHMMSS.md
```

必須記載：

- Implementation Summary
- Changed／Added Files
- Schema Migration
- Parser／Renderer Structure
- Config／Environment／CLI Precedence
- Test Commands／Results
- Native Hidden／Visible Evidence
- Default `高度推論` Evidence
- Raw Persistenceなし
- Model Artifact Hash不変
- Dependency不変
- Known Limitation
- Acceptance Criteria 22項目対応表
- Review依頼

## 17. Stop／Escalation Conditions

- Model Port Contractの破壊的変更が必要
- llama.cpp AdapterへDisplay Policyを入れる必要がある
- External Dependencyが必要
- Raw Reasoningの永続保存が必要
- Unknown ParserのSilent Fallbackが必要
- Hidden No-flashを満たせない
- Current Mac／Metal Regression
- Phase 1-D Language Regression
- Model File／Artifact Hash変更が必要
- Phase 2以降のComponentが必要

発生時はScopeを独断拡大せず、設計者／ユーザーへ返す。

## 18. Done Definition

RequirementsのAcceptance Criteria 22項目をEvidence付きで判定でき、Implementer Statusが作成された状態をReview Readyとする。

Phase 1-EのComplete／Accepted判定は設計者役のIndependent Review後に行う。


<!-- SOURCE_END 24: docs/handoffs/designer_handoff_phase_1e_thinking_presentation_20260719130303.md -->

---

<!-- SOURCE_BEGIN 25: docs/handoffs/designer_handoff_phase_1f_lightning_pure_cpu_preflight_addendum_20260725201016.md -->

### Source 25: `docs/handoffs/designer_handoff_phase_1f_lightning_pure_cpu_preflight_addendum_20260725201016.md`

- History Target: `docs/project/phases/phase_1/history/handoffs/designer_handoff_phase_1f_lightning_pure_cpu_preflight_addendum_20260725201016.md`
- Source SHA-512: `a5110a0397e5af1dc27bbf176e904a847758273a357bbec101be2b7cefb23995d25bbee4c61e26f79020df177ca9164cf66db32a003a49e94724d5d4bce72210`
- Source Size: `4301` bytes

# Phase 1-F Lightning Pure CPU Preflight 実装担当Addendum

- 文書ID: `designer_handoff_phase_1f_lightning_pure_cpu_preflight_addendum`
- 状態: `accepted_ready_for_repository_implementation`
- 作成日時: `2026-07-25 20:10:16 JST`
- 更新日時: `2026-07-25 20:10:16 JST`
- Snapshot: `20260725201016`
- 作成担当: 設計者役担当Task
- 対象: 実装者役担当Task
- 正本言語: 日本語
- Base Handoff: [designer_handoff_phase_1f_lightning_pure_cpu_runtime_follow_up_20260725200001.md](../history/handoffs/designer_handoff_phase_1f_lightning_pure_cpu_runtime_follow_up_20260725200001.md)
- Requirements: [phase_1f_lightning_pure_cpu_runtime_follow_up_requirements_20260725200001.md](../history/requirements/phase_1f_lightning_pure_cpu_runtime_follow_up_requirements_20260725200001.md)
- Accepted ADR: [adr_0022_lightning_pure_cpu_and_optional_component_hook_only_profile_20260725200001.md](../history/adr/adr_0022_lightning_pure_cpu_and_optional_component_hook_only_profile_20260725200001.md)
- supersedes: なし

## 1. Addendum Conclusion

Lightning側の環境再構築とNative Testはユーザーが実施する。実装担当は、ユーザーが前回と同様に再構築前の確認を一括実行できるPreflightをRepositoryへ用意する。

## 2. Existing Script

既に次が存在する。

```text
scripts/setup/preflight_lightning_ai_studio.sh
```

重複Scriptを無条件に増やさず、まずExisting Scriptを後方互換のまま拡張する。

Current `--cpu-only`は「CUDA BuildをCPU実行し、GPU Allocationだけ要求しない」という意味を持つ。Pure CPU Buildへ意味を変更してはならない。

## 3. Required Target Separation

明示的なRuntime Targetを追加する。

候補：

```text
--runtime-target cuda-gpu
--runtime-target cuda-cpu
--runtime-target cpu-native
```

互換性のため、既存Optionを維持する。

```text
Default       : current cuda-gpu semantics
--cpu-only    : current cuda-cpu semantics
cpu-native    : new pure CPU semantics
```

Option名はCurrent CLI Styleへ合わせて調整可能だが、三つの意味を混同しない。

## 4. CPU-native Preflight

確認するもの：

- Linux
- x86_64
- Container
- Environment Mode
- Python 3.12.11
- Project指定の`uv`
- CPU Count
- Available Memory
- Project／Environment PathのRead／Write条件
- Pure CPU Profileの存在とParse可能性
- Model RootのOptional Presence

呼び出さないもの：

- `nvidia-smi`
- `nvcc`
- CUDA Compiler
- GPU Allocation Probe

CPU-native経路では`nvcc available`をInformational表示するためにも実行しない。

## 5. Setup Script

Base Handoffどおり、次を作成する。

```text
scripts/setup/setup_lightning_linux_x86_64_cpu.sh
```

PreflightはRead-onlyとし、Environment作成、Dependency Install、Native BuildおよびModel配置はSetup Scriptと明確に分離する。

Setup Scriptはユーザー実行用であり、実装担当は外部Lightning環境を操作しない。

## 6. User-facing Procedure

実装報告へ、ユーザーがLightningで順番に実行できるCommandを記載する。

最低限：

1. Preflight Help
2. CPU-native Read-only Preflight
3. Setup Dry-runまたはPlan表示
4. Environment Setup
5. Environment Verification
6. Model Path確認
7. Bounded Smoke
8. Exit Code確認

Project Upload、Model Upload、Credential設定および公開URL操作を自動化しない。

## 7. Automated Test

- Existing Default Behavior
- Existing `--cpu-only` Behavior
- New CPU-native Behavior
- CPU-nativeがGPU Commandを呼ばない。
- Unknown Target Fail Closed
- HelpにTarget差を表示する。
- Shell Syntax
- Mocked Host／Tool Availability
- Macからの誤実行拒否

## 8. Required Status Report

Base HandoffのReportへ次を追加する。

- Existing Preflightを拡張したか、別Scriptが必要だったか
- その判断理由
- Targetごとの意味
- Backward Compatibility
- CPU-nativeで実行しないCommand
- User-run Rebuild Procedure
- External Native Test Pending

## 9. Authorization Boundary

Preflight、Pure CPU Setup Hook、ProfileおよびTestのRepository実装へ着手可能である。

外部Lightning操作、Dependency Install、Model配置、Upload、公開およびNative Acceptanceは許可範囲外である。


<!-- SOURCE_END 25: docs/handoffs/designer_handoff_phase_1f_lightning_pure_cpu_preflight_addendum_20260725201016.md -->

---

<!-- SOURCE_BEGIN 26: docs/handoffs/designer_handoff_phase_1f_lightning_pure_cpu_runtime_follow_up_20260725200001.md -->

### Source 26: `docs/handoffs/designer_handoff_phase_1f_lightning_pure_cpu_runtime_follow_up_20260725200001.md`

- History Target: `docs/project/phases/phase_1/history/handoffs/designer_handoff_phase_1f_lightning_pure_cpu_runtime_follow_up_20260725200001.md`
- Source SHA-512: `d9213e12c8df5b436c1afbeafc762e95527e5e9286f4698e3fdcf9dced7c7c404fb3505b09bacb140b512e2ab569b7d978ebf8027f6f1febee7b1db6cd73b24d`
- Source Size: `5870` bytes

# Phase 1-F Lightning Pure CPU Runtime Follow-up 実装担当Handoff

- 文書ID: `designer_handoff_phase_1f_lightning_pure_cpu_runtime_follow_up`
- 状態: `accepted_ready_for_repository_implementation`
- 作成日時: `2026-07-25 20:00:01 JST`
- 更新日時: `2026-07-25 20:00:01 JST`
- Snapshot: `20260725200001`
- 作成担当: 設計者役担当Task
- 対象: 実装者役担当Task
- 正本言語: 日本語
- Requirements: [phase_1f_lightning_pure_cpu_runtime_follow_up_requirements_20260725200001.md](../history/requirements/phase_1f_lightning_pure_cpu_runtime_follow_up_requirements_20260725200001.md)
- Architecture: [phase_1f_lightning_pure_cpu_runtime_follow_up_architecture_20260725200001.md](../history/architecture/phase_1f_lightning_pure_cpu_runtime_follow_up_architecture_20260725200001.md)
- Accepted ADR: [adr_0022_lightning_pure_cpu_and_optional_component_hook_only_profile_20260725200001.md](../history/adr/adr_0022_lightning_pure_cpu_and_optional_component_hook_only_profile_20260725200001.md)
- Source Review: [designer_review_phase_1_mac_web_ui_user_acceptance_and_follow_up_20260725192903.md](../history/handoffs/designer_review_phase_1_mac_web_ui_user_acceptance_and_follow_up_20260725192903.md)
- supersedes: なし

## 1. Handoff Conclusion

FreshなLinux x86_64 CPU環境向けに、CUDA Toolchainを要求しないPure CPU Runtime HookをRepositoryへ追加する。

本HandoffはRepository実装だけを許可する。外部Studio起動、Upload、Dependency Installation、Model配置、Native Testは別Gateである。

## 2. Required Reading Order

1. 本Handoff
2. Requirements
3. Architecture
4. ADR-0022
5. Source Review
6. [adr_0015_phase_1f_lightning_and_python_312_support_20260719202333.md](../history/adr/adr_0015_phase_1f_lightning_and_python_312_support_20260719202333.md)
7. [documentation_index_20260725192903.md](../history/documentation_index_20260725192903.md)

## 3. Scope

```text
New Pure CPU Profile
New CPU Setup Script
CPU Preflight Mode／Script
Verification Target
Static／Unit／Integration Test
Repository Status Report
```

## 4. Locked Decisions

```text
Build Variant           : cpu
Execution Device        : cpu
Acceleration API        : none
GPU Layers              : 0
GPU Required            : no
NVIDIA Driver Required  : no
CUDA Required           : no
nvcc Required           : no
Model Download          : no
External Execution      : no
RAG Implementation      : no
```

## 5. Step A — Existing Contract Inventory

変更前に次のReferenceを列挙する。

- Existing CUDA Profile
- Existing CUDA Build CPU Execution Profile
- Profile Resolver
- Build Variant Contract
- Environment Verification Target
- Setup／Preflight Scripts
- Acceptance Script
- Tests

Existing CPU ProfileをRename／Deleteしない。

## 6. Step B — Pure CPU Profile

候補：

```text
config/profiles/lightning_linux_x86_64_cpu_native.toml
```

意味：

```text
Linux／x86_64／container
llama_cpp／cpu build
cpu device
no acceleration
gpu_layers=0
fallback deny
```

Profile Schemaに`none`等が未対応なら、CoreへProvider固有Hard-codeを入れず、Generic Contractとして追加する。

## 7. Step C — Setup

候補：

```text
scripts/setup/setup_lightning_linux_x86_64_cpu.sh
```

要件：

- Python 3.12／3.13 Support Range
- `llama-cpp-python==0.3.34`
- Pure CPU Build検証
- Reuse／Explicit Rebuild分離
- GPU Commandを呼ばない。
- `nvcc`を確認しない。
- Model Smokeは明示Option。
- Model不足時にDownloadしない。
- Idempotentに再実行可能。

## 8. Step D — Preflight／Verification

Preflight：

- OS／Architecture／Container
- Python／uv
- CPU／Memory
- Writable Path

Verification Target候補：

```text
lightning-cpu-native
```

Pass条件：

- build variant cpu
- device cpu
- acceleration none
- gpu offload false
- gpu layers 0

## 9. Step E — Test

- Profile Parse／Validation
- Explicit Resolution
- Wrong Host／Architecture
- CPU Build Observation
- CUDA Marker非Required
- Mac Profile Regression
- CUDA Profile Regression
- Script Syntax
- ScriptのGPU Command非依存
- Native Pending State

実際のModel GenerationをLocal MacでCPU Profileとして偽装しない。

## 10. Project Documentation Explainer

本Handoffでは実装しない。

将来Component追加後、Lightning CPU Profileでは次を満たす。

```text
hook present
enabled false
provider absent allowed
no index load
no retrieval
no additional model call
```

Mac Localでの有効化はPhase 1-ex後の別Handoffとする。

## 11. Candidate File Scope

Expected：

```text
config/profiles/lightning_linux_x86_64_cpu_native.toml
scripts/setup/setup_lightning_linux_x86_64_cpu.sh
scripts/setup/verify_phase1_environment.py
scripts/setup/preflight_lightning_ai_studio.sh or CPU-specific preflight
tests/unit/inference/
tests/integration/
docs/handoffs/implementer_status_phase_1f_pure_cpu_*
```

Conditional：

```text
src/margpa_runtime_llm/bootstrap/profile_resolver.py
src/margpa_runtime_llm/modules/inference/contracts/runtime.py
config/platforms/platform_registry.toml
```

Do Not Change：

```text
Mac Profile
CUDA GPU Profile semantics
Model Port
Web UI
RAG
Model Artifact
pyproject dependency versions
```

## 12. Required Report

`docs/handoffs/implementer_status_phase_1f_pure_cpu_runtime_follow_up_YYYYMMDDHHMMSS.md`

必須内容：

- Changed Files
- Existing CPU Profile disposition
- Pure CPU Build detection
- Commands
- Static／Unit／Integration Result
- External Native Test Pending
- No External Operation
- Known Limitation

## 13. Stop Conditions

- Pure CPUをCUDA Buildとして申告する必要がある。
- CPU ProfileがGPU Commandを必須にする。
- Existing Mac／CUDA Contractを壊す。
- External EnvironmentなしではPassを偽装する必要がある。
- Model Downloadが必要になる。

上記の場合は実装を拡大せずStatusへ戻す。

<!-- SOURCE_END 26: docs/handoffs/designer_handoff_phase_1f_lightning_pure_cpu_runtime_follow_up_20260725200001.md -->

---

<!-- SOURCE_BEGIN 27: docs/handoffs/designer_handoff_phase_1f_lightning_test_isolation_follow_up_20260726092413.md -->

### Source 27: `docs/handoffs/designer_handoff_phase_1f_lightning_test_isolation_follow_up_20260726092413.md`

- History Target: `docs/project/phases/phase_1/history/handoffs/designer_handoff_phase_1f_lightning_test_isolation_follow_up_20260726092413.md`
- Source SHA-512: `83a0866c1e9144b1f208856a85f416c4c50fe474f4f78668b481c979439b1df7384c32a193cf4d1d120429a022a0d50cd76dfa4c28380603559927a53ea9cb0e`
- Source Size: `5177` bytes

# Phase 1-F Lightning Test Isolation Follow-up 実装担当Handoff

- 文書ID: `designer_handoff_phase_1f_lightning_test_isolation_follow_up`
- 状態: `accepted_handoff_implementation_pending`
- 作成日時: `2026-07-26 09:24:13 JST`
- 更新日時: `2026-07-26 09:24:13 JST`
- Snapshot: `20260726092413`
- 作成担当: 設計者役担当Task
- 対象担当: 実装者役担当Task
- Source Review: [designer_review_phase_1f_lightning_external_pure_cpu_runtime_20260726092413.md](../history/handoffs/designer_review_phase_1f_lightning_external_pure_cpu_runtime_20260726092413.md)
- Current Manual: [lightning_pure_cpu_actual_environment_reconstruction_manual_20260726092413.md](../history/user_manual/lightning_pure_cpu_actual_environment_reconstruction_manual_20260726092413.md)
- 正本言語: 日本語
- supersedes: なし

## 1. Objective

Lightning Container上でもRepository Unit TestがHost Markerまたは外部Application Environment Variableに依存せず、決定論的に実行できるようTest Isolationを修正する。

Production Code、Profile、Setup Script、Acceptance ScriptおよびRuntime Contractは変更しない。

## 2. Current Evidence

Lightning Pure CPU：

```text
Environment Verification      : PASS
Native Acceptance             : PASS
all_required_checks_passed    : true
Ruff                          : PASS
Mypy                          : PASS
Repository Test               : 264 passed／2 failed
```

残る2件：

```text
tests/unit/inference/test_deployment_platform.py::
  test_profile_resolution_priority_is_explicit_then_environment_then_default

tests/unit/inference/test_deployment_platform.py::
  test_future_platform_alias_and_default_are_registry_only_extensions
```

## 3. Required Change A

対象：

```text
tests/unit/inference/test_deployment_platform.py
```

`native`を検証する`resolve_profile_path()`呼び出しへ、Execution Environmentを明示する。

```python
raw_execution_environment="native",
```

最低対象：

### `test_profile_resolution_priority_is_explicit_then_environment_then_default`

次の3呼び出し：

- explicit
- environment
- platform_default

### `test_future_platform_alias_and_default_are_registry_only_extensions`

次の1呼び出し：

- future platform resolution

OS／Architectureと同様にExecution EnvironmentもTest Fixture Inputとして固定し、実行Hostの`/.dockerenv`またはContainer Markerを参照させない。

## 4. Required Change B

対象：

```text
tests/unit/inference/test_lightning_cpu_native_setup.py
```

`test_model_path_compatibility_requires_registry_layout`が、実行Shellの`MARGPA_MODEL_ROOT`を継承しないようにする。

Test内でSubprocess EnvironmentをCopyし、少なくとも次を除外する。

```text
MARGPA_MODEL_ROOT
MARGPA_PROFILE
```

概念形：

```python
environment = dict(os.environ)
environment.pop("MARGPA_MODEL_ROOT", None)
environment.pop("MARGPA_PROFILE", None)
```

対象Test内のSetup Script Subprocessへ同じ`env=environment`を渡す。

ユーザーがShell側で`env -u`しなくてもTestが決定論的にPassすること。

## 5. Scope

変更可：

```text
tests/unit/inference/test_deployment_platform.py
tests/unit/inference/test_lightning_cpu_native_setup.py
```

変更禁止：

```text
src/
config/
scripts/setup/
scripts/models/
pyproject.toml
uv.lock
```

実装中にProduction変更が必要と判断した場合、実施せず設計者役へ戻す。

## 6. Acceptance Criteria

### Mac

```text
Full pytest Suite : PASS
Ruff Check        : PASS
Ruff Format       : PASS
Mypy              : PASS
```

### Lightning Linux x86_64 Container

外部Environment Variableを手動Unsetしなくても：

```bash
"$MARGPA_ENV_PREFIX/bin/pytest" -q
```

が次相当で完了する。

```text
266 passed
1 skipped
3 deselected
0 failed
```

Apple Silicon Metal Testの1件Skipは正常とする。

## 7. Required Tests

- Mac Full Suite
- Targeted Deployment Platform Unit Test
- Targeted Lightning CPU Native Setup Unit Test
- Ruff Check
- Ruff Format Check
- Mypy
- Shell SyntaxはProduction Script未変更確認として任意

Targeted例：

```bash
pytest -q tests/unit/inference/test_deployment_platform.py
pytest -q tests/unit/inference/test_lightning_cpu_native_setup.py
```

## 8. Native Acceptance

本Follow-upはTest-onlyである。

Production Runtime、Profile、Backend、Model Root Resolution、SetupまたはNative Acceptance Scriptが変更されない限り、Lightning Bounded Native Acceptanceを再実行しない。

## 9. Reporting

Phase 1-ex完了までDocs単一Writerは設計者役である。

実装担当はDocsへ直接書き込まず、次を会話Payloadとして返す。

- 変更File
- 変更概要
- Targeted Test
- Full Suite
- Ruff
- Mypy
- Production File変更なしの確認
- Known Limitation

設計者役がStatus、Review、Indexを作成する。

## 10. Authorization Boundary

本Handoffは上記2 Test FileのTest Isolation修正だけを許可する。

次を許可しない。

- Lightning外部操作
- Model再実行
- Production Code変更
- Config変更
- Git／GitHub操作
- Phase 1完了宣言
- Backup
- Phase 1-ex開始


<!-- SOURCE_END 27: docs/handoffs/designer_handoff_phase_1f_lightning_test_isolation_follow_up_20260726092413.md -->

---

<!-- SOURCE_BEGIN 28: docs/handoffs/designer_handoff_phase_1f_pure_cpu_acceptance_correction_20260725212559.md -->

### Source 28: `docs/handoffs/designer_handoff_phase_1f_pure_cpu_acceptance_correction_20260725212559.md`

- History Target: `docs/project/phases/phase_1/history/handoffs/designer_handoff_phase_1f_pure_cpu_acceptance_correction_20260725212559.md`
- Source SHA-512: `6c21fb56fe9199e4c5554996e4484a3fad506b752f29a04502b5d9184bb5aa01ebbc22f0a0a5e8e1e2223ac289227a68a0e384137612accd142df3274aa4e567`
- Source Size: `2802` bytes

# Phase 1-F Pure CPU Acceptance Correction 実装担当Handoff

- 文書ID: `designer_handoff_phase_1f_pure_cpu_acceptance_correction`
- 状態: `changes_requested_ready_for_implementation`
- 作成日時: `2026-07-25 21:25:59 JST`
- 更新日時: `2026-07-25 21:25:59 JST`
- Snapshot: `20260725212559`
- 作成担当: 設計者役担当Task
- 対象: 実装者役担当Task
- 正本言語: 日本語
- Source Review: [designer_review_phase_1f_pure_cpu_repository_20260725212559.md](../history/handoffs/designer_review_phase_1f_pure_cpu_repository_20260725212559.md)
- Base Status: [implementer_status_phase_1f_pure_cpu_runtime_follow_up_20260725203508.md](../history/handoffs/implementer_status_phase_1f_pure_cpu_runtime_follow_up_20260725203508.md)
- supersedes: なし

## 1. Scope

LightningへUpload／再構築する前に、Pure CPU Native Acceptance Contractを局所修正する。

## 2. Required Fix A

対象：

```text
scripts/models/phase1f_cross_environment_acceptance.py
```

CPU Runtimeの`acceleration_api`を`"cpu_native"`へ固定せず、選択Profileの`compute.acceleration_api_key`と照合する。

維持する条件：

- GPU Offload未要求
- GPU Offload未観測
- Runtime GPU Offload False
- Device Kind CPU
- ProfileとAcceleration API一致

## 3. Required Fix B

`setup_lightning_linux_x86_64_cpu.sh`のModel指定Contractを明確化する。

推奨：

```text
--model-root MODEL_ROOT
```

- RegistryのRelative Artifact PathをMODEL_ROOTから解決する。
- 解決結果がFileであることを確認する。
- Smokeが実際にLoadするFileを表示する。
- `--model-path`を維持する場合はBackward CompatibilityとExpected LayoutをValidationする。
- 指定Fileと実際にLoadするFileが異なる状態を許可しない。
- ModelをDownloadしない。

## 4. Required Automated Test

- CUDA GPU Profile一致
- CUDA Build CPU Profileの`cpu_native`一致
- Pure CPU Profileの`none`一致
- Acceleration不一致Fail Closed
- Pure CPU `all_required_checks_passed`
- Model RootからExpected Artifact解決
- Invalid Layout拒否
- Specified ArtifactとLoaded Artifact一致
- Existing Help／Option非Regression

Actual Model Loadは外部Native GateとしてPendingでよい。

## 5. Non-goals

- External Lightning操作
- Dependency Install
- Model Download
- Profile再設計
- Web UI変更
- RAG
- Git／GitHub

## 6. Required Status

新規作成：

```text
docs/handoffs/implementer_status_phase_1f_pure_cpu_acceptance_correction_YYYYMMDDHHMMSS.md
```

記載：

- Changed Files
- Acceleration Match Fix
- Model Path／Root Contract
- Test Commands／Results
- External Native Pending
- Known Limitations

## 7. Completion Gate

Correction Statusを設計者役がReviewしAcceptedとするまで、Pure CPU Repository Follow-up全体を完了扱いにしない。


<!-- SOURCE_END 28: docs/handoffs/designer_handoff_phase_1f_pure_cpu_acceptance_correction_20260725212559.md -->

---

<!-- SOURCE_BEGIN 29: docs/handoffs/designer_handoff_phase_1i_web_presentation_and_ux_follow_up_20260725200001.md -->

### Source 29: `docs/handoffs/designer_handoff_phase_1i_web_presentation_and_ux_follow_up_20260725200001.md`

- History Target: `docs/project/phases/phase_1/history/handoffs/designer_handoff_phase_1i_web_presentation_and_ux_follow_up_20260725200001.md`
- Source SHA-512: `f6290ec7ca6bf9a0d273ce8926126c05f1624be45285b7410acd135512a6b6d70c95aa4cba72772c20d24c15f9ffad7f566ba2bb72c275501f6b71d0c2369aa4`
- Source Size: `8025` bytes

# Phase 1-I Web Presentation and UX Follow-up 実装担当Handoff

- 文書ID: `designer_handoff_phase_1i_web_presentation_and_ux_follow_up`
- 状態: `accepted_ready_for_implementation`
- 作成日時: `2026-07-25 20:00:01 JST`
- 更新日時: `2026-07-25 20:00:01 JST`
- Snapshot: `20260725200001`
- 作成担当: 設計者役担当Task
- 対象: 実装者役担当Task
- 正本言語: 日本語
- Requirements: [phase_1i_web_presentation_and_ux_follow_up_requirements_20260725200001.md](../history/requirements/phase_1i_web_presentation_and_ux_follow_up_requirements_20260725200001.md)
- Architecture: [phase_1i_web_presentation_and_ux_follow_up_architecture_20260725200001.md](../history/architecture/phase_1i_web_presentation_and_ux_follow_up_architecture_20260725200001.md)
- Accepted ADR: [adr_0021_phase_1i_thinking_aware_safe_web_presentation_20260725200001.md](../history/adr/adr_0021_phase_1i_thinking_aware_safe_web_presentation_20260725200001.md)
- Source Review: [designer_review_phase_1_mac_web_ui_user_acceptance_and_follow_up_20260725192903.md](../history/handoffs/designer_review_phase_1_mac_web_ui_user_acceptance_and_follow_up_20260725192903.md)
- supersedes: なし

## 1. Handoff Conclusion

Phase 1-IをPhase 1 Completion前に実装する。

実装Scope：

1. Thinking Generation／Visibility UI整合
2. Reasoning／Final SSE Channel分離
3. Shortcut Hint
4. User／Assistant Message Copy
5. Completion後のSanitized Markdown Presentation
6. Automated Test
7. 実装報告

## 2. Required Reading Order

1. 本Handoff
2. Requirements
3. Architecture
4. ADR-0021
5. Source Review
6. [adr_0014_thinking_execution_presentation_and_persistence_separation_20260719130303.md](../history/adr/adr_0014_thinking_execution_presentation_and_persistence_separation_20260719130303.md)
7. [adr_0020_phase_1h_summary_pipeline_and_ui_language_separation_20260721174346.md](../history/adr/adr_0020_phase_1h_summary_pipeline_and_ui_language_separation_20260721174346.md)
8. [documentation_index_20260725192903.md](../history/documentation_index_20260725192903.md)

## 3. Authorization

ユーザーによる実装Handoff作成と先行実施の指示を受領済みである。Phase 1-IのSource／Test／必要Config変更へ着手可能である。

外部環境操作、Model Download、Git／GitHub、RAG、Pure CPU Runtimeは本HandoffのScope外である。

## 4. Locked Decisions

```text
Thinking Execution／Visibility : Separate
Reasoning Persistence           : Disabled
Summary Thinking                : Disabled
Reasoning UI                    : Ephemeral Plain Text
Final Streaming UI              : Plain Text
Final Completed UI              : Sanitized Markdown
History／Copy Source             : Canonical Final
User Message Presentation       : Plain Text
Runtime CDN                     : Forbidden
Unsafe Markdown Fallback        : Plain Text
Clipboard Read                  : Forbidden
```

## 5. Step A — Regression Freeze

変更前に既存Testを実行し、結果をStatusへ記録する。

```text
ruff format --check
ruff check
mypy
pytest
web integration tests
```

次をRegression Fixtureとして維持する。

- Language
- Summary
- Stop／Cancel
- New Chat
- Busy
- Token Warning
- Basic Auth
- Shutdown
- No Raw Thinking Persistence

## 6. Step B — Thinking Request／Runtime Contract

追加：

```text
ConversationSettings.thinking_mode
RuntimeDefaults.thinking_mode
RuntimeDefaults.thinking_control_available
```

Web Requestの`thinking_mode`をGeneration Parametersへ適用する。

Unknown ValueとCapability不足を黙って無視しない。

Summary StageはThinking Disabledを維持する。

## 7. Step C — Semantic SSE

Deltaへ`channel`を追加する。

```text
reasoning
final
```

要件：

- Hidden ReasoningをClientへ送らない。
- FinalだけをCanonical Assistant Messageへ保存する。
- Warning／Error／StatusをContentへ混ぜない。
- Unknown ChannelをClientが無視して成功扱いしない。

Presentation RendererのDisplay TagをBrowserが再Parseする方式は禁止する。

## 8. Step D — Message DOM

Assistant MessageをThinking、Final、Actionsに分離する。

Thinking：

- Plain Text
- Visible時だけ作成
- Finalとは別Label
- Historyへ入れない

Final：

- Streaming中Plain Text
- Completion後Canonical FinalをMarkdown Render

Actions：

- Copy
- 完了状態後にAssistant Copyを有効化

## 9. Step E — Thinking UI

UI候補：

```text
推論生成       OFF／ON
推論過程を表示 OFF／ON
```

- Generation OFF時はVisibilityをDisabledにするか、表示対象なしを明示する。
- UI Languageを切り替えてもStateを失わない。
- General Defaultは両方OFF。
- Token／Latency／Persistence Noticeを維持する。

## 10. Step F — Shortcut Hint

ComposerへLocalized Hintを追加する。

```text
Cmd+Enter／Ctrl+Enterで送信
Send with Cmd+Enter / Ctrl+Enter
```

Keyboard Handlerは`event.isComposing`を確認する。

## 11. Step G — Copy

Copy Source：

```text
User      : canonical input
Assistant : canonical completed final
```

- Rendered DOMをSourceにしない。
- Thinkingを混ぜない。
- Summaryの非表示Originalを混ぜない。
- Copy成功／失敗をLocalized表示する。
- Clipboard Readは禁止する。

## 12. Step H — Markdown

### Selection Gate

Parser／Sanitizer方式は次を満たす。

- No Runtime CDN
- Pinned Version
- License Compatible
- Source／SHA-512記録
- Raw HTML Disabled
- XSS Test可能
- Plain Text Fallback

Third-party Artifactを追加する場合、Status ReportへVersion、License、Source、Digest、配置Pathを記載する。

### Rendering

- Final Completion後にCanonical FinalをRenderする。
- Streaming中はPlain Text。
- ThinkingはMarkdown化しない。
- Dangerous URLとUnsafe HTMLをRejectする。
- Parser／Sanitizer Failure時はCanonical Plain Textを表示する。

## 13. Candidate File Scope

Expected：

```text
src/margpa_runtime_llm/modules/conversation/contracts.py
src/margpa_runtime_llm/modules/conversation/application/conversation_generation.py
src/margpa_runtime_llm/modules/presentation/
src/margpa_runtime_llm/web/contracts.py
src/margpa_runtime_llm/web/static/index.html
src/margpa_runtime_llm/web/static/app.js
src/margpa_runtime_llm/web/static/app.css
tests/unit/
tests/integration/web/
config/application.toml
docs/handoffs/implementer_status_phase_1i_*
```

Conditional：

```text
pyproject.toml
uv.lock
src/margpa_runtime_llm/web/static/vendor/
Third-party notice metadata
```

Do Not Change：

```text
Model Artifact
Model Port
llama.cpp Backend
Deployment Profiles
RAG
External Environment
Public LICENSE
```

## 14. Required Automated Test

- Existing Default Suite
- Web Integration
- Thinking 4組合せ
- Capability不足
- Reasoning／Final Channel
- Hidden Reasoning非送信
- Summary Thinking Disabled
- Markdown Feature
- Markdown XSS／Dangerous URL
- Streaming／Completion
- Copy Canonical Source
- Hidden Thinking／Original Summary非混入
- Shortcut／IME
- New Chat／Stop／Busy

## 15. Deferred Combined User Test

実装担当はManual Testを完了扱いにしない。実装と設計Review後にユーザーがまとめて実施する。

対象：

- 生成中New Chat
- Summary中Stop
- Browser Reload
- 別Tab Busy
- Token `0／1／2048／2049`
- Thinking 4組合せ
- Markdown
- Copy
- Shortcut Hint

## 16. Completion Report

`docs/handoffs/implementer_status_phase_1i_*_YYYYMMDDHHMMSS.md`を新規作成する。

必須内容：

- Changed Files
- Contract Change
- Dependency／License
- Test Command／Result
- Security Test
- Known Limitation
- Manual Test Pending
- No External Operation

## 17. Stop Conditions

次の場合は安全でない代替を実装せず、Statusへ戻す。

- SanitizerなしでHTML Injectionが必要
- Thinking／Final分離が維持できない
- Hidden ThinkingがHistory／Copyへ混入する
- Third-party Licenseが不明
- Existing Stop／Summary／Language Contractが壊れる
- Model Adapter変更が必要

<!-- SOURCE_END 29: docs/handoffs/designer_handoff_phase_1i_web_presentation_and_ux_follow_up_20260725200001.md -->

---

<!-- SOURCE_BEGIN 30: docs/handoffs/designer_handoff_post_phase_1e_research_platform_20260719112304.md -->

### Source 30: `docs/handoffs/designer_handoff_post_phase_1e_research_platform_20260719112304.md`

- History Target: `docs/project/phases/phase_1/history/handoffs/designer_handoff_post_phase_1e_research_platform_20260719112304.md`
- Source SHA-512: `5f29bbca019878ad8250c9e7c7f78e12e1acea907ab613173619774f61cfcedcd5b08eb0c5e5bd2a020cc7b620b943c400c2167e86a4c6facc4f41095587995b`
- Source Size: `12405` bytes

# Phase 1-E後 AI実験・Governance Platform 実装担当Handoff

- 文書ID: `designer_handoff_post_phase_1e_research_platform`
- 状態: `planning_handoff_implementation_not_authorized`
- 作成日時: `2026-07-19 11:23:04 JST`
- 更新日時: `2026-07-19 11:23:04 JST`
- Snapshot: `20260719112304`
- 作成担当: 設計者役担当Task
- 対象: 実装者役担当Task
- 正本言語: 日本語
- 最新Index: [documentation_index_20260719112304.md](../history/documentation_index_20260719112304.md)
- 最新Roadmap: [implementation_roadmap_20260719112304.md](../history/architecture/implementation_roadmap_20260719112304.md)
- supersedes: なし（Phase 1-E後新規Handoff系列）

## 1. 最重要な状態

本Handoffは、Phase 1-E完了後の実装担当へ向けた計画・境界の共有文書である。

```text
Requirements／Architecture／ADR : Accepted
Source／Config／Test Implementation: Not Authorized
Dependency Install                    : Not Authorized
Model Download                        : Not Authorized
Lightning External Operation          : Not Authorized
ARGD／DAGD Project Import             : Not Authorized
```

ユーザーが対象Phaseの実装開始を明示的に許可するまで、本Handoffを根拠にSource／Config／Test／Directory／Dependency／External Serviceを変更しないこと。

## 2. 実装前に読む正本

### 2.1 共通

1. [documentation_rules_20260718193435.md](../history/requirements/documentation_rules_20260718193435.md)
2. [common_project_handoff_20260718193435.md](../history/handoffs/common_project_handoff_20260718193435.md)
3. [project_requirements_20260718193435.md](../history/requirements/project_requirements_20260718193435.md)
4. [implementation_roadmap_20260719112304.md](../history/architecture/implementation_roadmap_20260719112304.md)

### 2.2 今回の追加要件

1. [post_phase_1e_research_platform_requirements_20260719112304.md](../history/requirements/post_phase_1e_research_platform_requirements_20260719112304.md)
2. [generic_governance_definition_platform_requirements_20260719112304.md](../history/requirements/generic_governance_definition_platform_requirements_20260719112304.md)
3. [governance_definition_catalog_20260719112304.md](../history/governance/governance_definition_catalog_20260719112304.md)

### 2.3 Architecture

1. [governance_control_plane_architecture_20260719112304.md](../history/architecture/governance_control_plane_architecture_20260719112304.md)
2. [governance_definition_platform_architecture_20260719112304.md](../history/architecture/governance_definition_platform_architecture_20260719112304.md)
3. [experimental_runtime_ui_status_architecture_20260719112304.md](../history/architecture/experimental_runtime_ui_status_architecture_20260719112304.md)
4. [lightning_ai_studio_cross_environment_architecture_20260719112304.md](../history/architecture/lightning_ai_studio_cross_environment_architecture_20260719112304.md)

### 2.4 Accepted ADR

1. [adr_0010_research_runtime_phase_reorganization_20260719112304.md](../history/adr/adr_0010_research_runtime_phase_reorganization_20260719112304.md)
2. [adr_0011_shared_governance_control_plane_and_distributed_points_20260719112304.md](../history/adr/adr_0011_shared_governance_control_plane_and_distributed_points_20260719112304.md)
3. [adr_0012_optional_generic_governance_definition_platform_20260719112304.md](../history/adr/adr_0012_optional_generic_governance_definition_platform_20260719112304.md)
4. [adr_0013_lightning_ai_studio_external_development_20260719112304.md](../history/adr/adr_0013_lightning_ai_studio_external_development_20260719112304.md)

## 3. 現在のPhase状態

```text
1-A : Complete／Accepted
1-B : Complete／Accepted
1-C : Complete／Accepted
1-D : Implementation Complete／Review Requested／Not Yet Accepted
1-E : Planned／Not Designed／Not Authorized
2+  : Planning Only／Not Authorized
```

Phase 1-Dの最新Status：

- [implementer_status_phase_1d_configuration_and_response_language_20260719095111.md](../history/handoffs/implementer_status_phase_1d_configuration_and_response_language_20260719095111.md)

このStatusは最新Indexに取り込むが、設計者Reviewは未実施である。Acceptedと読み替えないこと。

## 4. 実装開始順序

現在の予定順序：

```text
Phase 1-D Review
  ↓
Phase 1-E Requirements／Architecture／ADR／Handoff
  ↓
Phase 1-E Implementation／Review
  ↓
Portable Runtime MVP Gate
  ↓
Phase 2-A Component Registry／Switchboard
  ↓
Phase 2-B Experiment Runtime
  ↓
Phase 2-C Event／Status／Minimal Audit
  ↓
Phase 2-D Lightning AI Studio
  ↓
Phase 3 Generic GD Platform／MARGPA Main Governance
```

Phase 2以降を一括実装しない。各Sub-phaseごとに詳細Handoff、ユーザー許可、Status、Reviewを通す。

## 5. Phase 2-Aの境界

### 5.1 作るもの

- Component Descriptor／Registry
- Component `enabled`
- Governance Mode `off／observe／enforce`
- Required／Optional Dependency
- Conflict／Invalid Combination
- Capability／Degraded Mode
- Apply Mode
- Governance Point／Binding HookのContract
- Effective Switch Validation

### 5.2 作らないもの

- Guard Model本体
- LLM-as-a-Judge本体
- Agent／Tool本体
- RAG本体
- ARGD／DAGD Compiler本体
- CDOGD Routing
- Web UI

### 5.3 非交渉条件

- Component IDを固定Closed Enumのみにしない。
- `enabled=false`とGovernance `mode=off`を同一視しない。
- Invalid Combinationを黙って自動修正しない。
- Tool Permission OFFをAllow Allにしない。
- System／Host／External AuthorityはApplication Switchで無効化できない。

## 6. Phase 2-Bの境界

### 6.1 作るもの

- Experiment Profile
- Experiment ID／Run ID／Request IDの分離
- Effective Config Snapshot／Hash／Source
- Model／Artifact Digest
- Definition／Adjustment／Plan Digestの将来Hook
- Seed／Input／Output／Latency／Token／Stop
- Baseline Profile

### 6.2 必須Baseline

```text
baseline_no_governance
baseline_empty_governance
main_governance_observe
main_governance_enforce
```

Phase 3前の`main_governance_*`はProfile Schema／Validationの予約として存在できるが、未実装のGovernanceを実行済みと記録しない。

## 7. Phase 2-Cの境界

- Runtime Event Envelope
- Component／Governance Lifecycle Event
- Status Projection
- JSON／JSONL Append-Only
- Canonicalization Version／SHA-512
- Projection／Sink FailureでInferenceを壊さない

Runtime Lifecycle StateとDAGDのGovernance Status Reporterを同一Schemaにしない。

## 8. Phase 2-Dの境界

- Lightning AI Studioで同一Repositoryを使う。
- Linux x86_64／NVIDIA CUDA／llama.cppをDeployment Adapterで追加する。
- Application Coreに`if lightning`、`if cuda`を直書きしない。
- Macと同じLogical Model ID、Model Port、Test Contractを使う。
- GGUF、Secret、実LogをGitにCommitしない。
- ZeroGPUはこのPhaseのScopeに入れない。

## 9. Phase 3の最重要境界

### 9.1 Zero Definitionを先に成立させる

ARGD／DAGDを読み込む前に、次をPassさせる。

```text
definition_sources = []
definitions = 0
governance.mode = off
model load／generate／stream／cancel = pass
governance model calls／tokens／repairs = 0
```

`EmptyDefinitionProvider`をProduction Codeとして用意する。

### 9.2 特定GDのハードコード禁止

次をCoreに実装しない。

```text
if definition_id == "argd"
if filename contains "aisgd"
if cdogd exists
known_gd_count = 16
```

代わりにProvider／Manifest／Descriptor／Adapter／IR／Compiler／Bindingを使う。

### 9.3 Source JSONはData

- JSONからCode、Shell、Import、URL Downloadを実行しない。
- Custom SchemaはTrusted Adapter Pluginを別途登録する。
- Path Traversal、Size／Depth／Rule／Prompt上限、Digestを検証する。

### 9.4 ARGD／DAGD

- 現行の複合Source JSONはByte-for-byte不変でSnapshotする。
- Legacy Adapterが`argd`と`dagd`を個別Descriptor／IRに展開する。
- 利便性のためにSourceを独自分割しない。
- SourceがなくてもRuntimeを動作させる。

### 9.5 CDOGD

- 必須ではない。
- Phase 3でDynamic Routingを実装しない。
- 名前だけでOrchestrator Capabilityを付与しない。
- Custom Orchestrator-capability Definitionと交換可能にする。

## 10. Governance Source／Adjustment／Binding

```text
Immutable Definition Source
  + Manifest
  + Adjustment Profile
  + Binding
  + Compiler Version
  + Runtime Capability
  ↓
Compiled Plan
```

原始GD JSONに動作調整値を書き込まない。UIからもSource JSONではなくAdjustment／Bindingを編集する。

## 11. Governance Control Planeの非交渉条件

- Shared Control Plane + Distributed Point + Explicit Binding
- 各Pointへ完全なMARGPA一式を複製しない
- 全GDを毎ターン・全Pointで読み込まない
- Lazy Load／Rule Selection／Plan Cache／Budget
- Deterministic Rule First
- Semantic Evaluator Only When Needed
- Shared Context／Point-local State／Evidenceの分離
- Central Action Conflict Resolution
- Unknown ActionはRecord-only
- Governance-on-governanceの無限再帰禁止

## 12. UI実装時の境界

### Basic UI

- Main Model
- Response Language
- New Chat／History
- Generate／Stop／Regenerate
- Simple Status

### 開発・研究設定

- Generation
- Model Runtime
- Component Structure
- Governance
- Evaluation／Repair
- Agent／Tool
- Experiment
- Status／Audit
- Deployment

UIは`config/application.toml`を直接上書きしない。Typed Config Serviceを通じ、Preview、Validation、Diff、Source、Apply Modeを表示した後にGit対象外のLocal OverrideへAtomic Saveする。

## 13. 実装報告に必ず含めるもの

個別PhaseのImplementer Statusは少なくとも次を記載する。

- 実装ScopeとScope外
- 変更File一覧
- Contract／Schema／Migration
- Dependency変更の有無
- Unit／Integration／Native Test
- Mac／Lightning等の実行環境
- Effective Config／Source
- Artifact／Definition／Config Digest
- Performance／Token／Latency
- Degraded／Invalid／Failure Test
- 未解決項目
- Acceptance Criteriaの対応表

## 14. Docs運用

- 実装担当が読むその他のDocsは原則読み取り専用である。
- 実装Statusは`docs/handoffs/implementer_status_*_YYYYMMDDHHMMSS.md`として毎回新規作成する。
- 既存Docsを上書きしない。
- Review依頼後、設計者がReviewと新Indexを同時に作成する。

## 15. 将来GD Catalogの扱い

[governance_definition_catalog_20260719112304.md](../history/governance/governance_definition_catalog_20260719112304.md)に記載されたARGD、DAGD、CDOGD、SPPGD、DAAGD、SDAGD、SDMRGD、DSGD、ACRGD、AAGD、AISGD、MPGD、DCAGD、PMOGD、AIRGD、AIAGD、SEGD、OMRGDは、実装必須一覧ではない。

実装担当は次を守る。

- Catalogの名称をCore Enumにしない。
- Author提案PathをRuntime Contractにしない。
- GD名からCapabilityを推測しない。
- AAGDが実行許可を生成すると実装しない。
- DAAGDが存在しない権限を生成すると実装しない。
- MPGDが存在しないPolicyを生成すると実装しない。
- SDAGD／SDMRGDが外部の最終承認を代替すると実装しない。

## 16. 実装解禁時に設計者へ戻すべき条件

次のいずれかが発生した場合は、無断でScopeを拡大せず設計者／ユーザーへ戻す。

- 汎用Contractでは扱えないARGD／DAGD Schemaが見つかった
- Source JSONを書き換えないと実装できない
- 安全なIR／Action Contractに落とせない
- Required／Optional／Fail Open／Fail Closedの判断が方針を変える
- Lightningの課金／GPU／Model Upload操作が必要
- External Policy／Authority／Licenseの新しい条件がある
- UI FrameworkまたはStorageの最終選定が必要

## 17. Handoff結論

今回の設計で、Projectの次の中核が固定された。

```text
疎結合なFunctional Component
  + 個別Switch
  + 共有Governance Control Plane
  + 分散Governance Point
  + 全GD任意／0件Baseline
  + 実験再現性
  + Event-driven Status
  + Mac／Lightning Cross-environment
  + Basic UI／開発・研究設定の分離
```

実装担当は、後続Phaseを「特定のGDやServiceを埋め込む作業」ではなく、「0件から任意のComponent／Definitionを明示的に組み立てられるPlatformを段階的に実証する作業」として扱うこと。

<!-- SOURCE_END 30: docs/handoffs/designer_handoff_post_phase_1e_research_platform_20260719112304.md -->

---

<!-- SOURCE_BEGIN 31: docs/handoffs/designer_handoff_simple_rag_documentation_availability_reservation_20260725201016.md -->

### Source 31: `docs/handoffs/designer_handoff_simple_rag_documentation_availability_reservation_20260725201016.md`

- History Target: `docs/project/phases/phase_1/history/handoffs/designer_handoff_simple_rag_documentation_availability_reservation_20260725201016.md`
- Source SHA-512: `d93d50ad980f430180b94bc4fbcbd83f7b2504662e4c2255a34a558863bb6911cd06e78232d9cafe8ef6a5ebd6bf58a6690122be734b2006aa2803621f772f1c`
- Source Size: `2454` bytes

# Simple RAG Documentation Availability 実装担当予約Handoff

- 文書ID: `designer_handoff_simple_rag_documentation_availability_reservation`
- 状態: `accepted_reservation_not_authorized_for_implementation`
- 作成日時: `2026-07-25 20:10:16 JST`
- 更新日時: `2026-07-25 20:10:16 JST`
- Snapshot: `20260725201016`
- 作成担当: 設計者役担当Task
- 対象: 将来の実装者役担当Task
- 正本言語: 日本語
- Requirements: [simple_rag_documentation_availability_requirements_20260725201016.md](../history/requirements/simple_rag_documentation_availability_requirements_20260725201016.md)
- Accepted ADR: [adr_0023_simple_rag_missing_docs_explicit_unavailable_result_20260725201016.md](../history/adr/adr_0023_simple_rag_missing_docs_explicit_unavailable_result_20260725201016.md)
- supersedes: なし

## 1. Timing

本HandoffはPhase 1-ex完了後のSimple RAG実装に備えた予約文書である。現時点ではSource、Config、TestまたはDependencyを変更しない。

## 2. Locked Contract

```text
OFF:
  docs/ probeなし
  index loadなし
  retrievalなし
  model callなし

ON／明示利用＋docs/ missing:
  state=unavailable
  reason_code=docs_directory_missing
  Project説明の推測生成なし
  Application Crashなし
```

日本語表示：

```text
docs/が設置されていないため参照できません。
```

## 3. Deployment Policy

### Mac Local

Phase 1-ex後、Simple RAG本体を実装・有効化できる。ON時に`docs/`がなければ共通Unavailable Resultを返す。

### Lightning

当面はHook-only／Default OFFとする。`docs/`、Corpus、RetrieverまたはProviderを要求しない。将来ONにした場合だけAvailability Gateを通す。

## 4. Future Implementation Requirements

- Availability PortをRetriever実装から分離する。
- Logical Docs RootをConfigから解決する。
- Absolute Pathを利用者向けErrorへ出さない。
- Missing時にIndex／Retriever／Modelを呼ばない。
- UI／CLI／APIへ同じReason Codeを渡す。
- Audit Eventを発行可能にする。
- Missingから配置後の明示的Retryを可能にする。

## 5. Required Test after Authorization

- OFF／ON
- Mac／Lightning
- Missing／Present
- 日本語／英語
- Model Call非発生
- Path非露出
- Retry Recovery

## 6. Stop Condition

Phase 1-exが完了し、Public Canonical Corpus、Manifestおよび実装Scopeが承認されるまで着手しない。


<!-- SOURCE_END 31: docs/handoffs/designer_handoff_simple_rag_documentation_availability_reservation_20260725201016.md -->

---

<!-- SOURCE_BEGIN 32: docs/handoffs/designer_python_environment_handoff_20260718201744.md -->

### Source 32: `docs/handoffs/designer_python_environment_handoff_20260718201744.md`

- History Target: `docs/project/phases/phase_1/history/handoffs/designer_python_environment_handoff_20260718201744.md`
- Source SHA-512: `e89d2e9b89e77896c46c270c5a8d5c6089210eeb7efc15d741ee6350dcb1f80cde5823e4dddd618d39b52bd52eb74216106f9b62161b09821bca3d2cc7c4ce41`
- Source Size: `6225` bytes

# Python環境設計から実装担当への引き継ぎ

- 文書ID: `designer_python_environment_handoff`
- 状態: `waiting_for_implementation_unlock`
- 作成日時: `2026-07-18 20:17:44 JST`
- 更新日時: `2026-07-18 20:17:44 JST`
- 作成担当: 設計者役担当Task
- 対象: 実装者役担当Task
- 正本言語: 日本語
- Architecture正本: [python_environment_and_dependency_strategy_20260718201744.md](../history/architecture/python_environment_and_dependency_strategy_20260718201744.md)
- ADR: [adr_0005_python_environment_and_dependency_management_20260718201744.md](../history/adr/adr_0005_python_environment_and_dependency_management_20260718201744.md)
- 共通実装引き継ぎ: [implementer_handoff_20260718193435.md](../history/handoffs/implementer_handoff_20260718193435.md)
- supersedes: なし（新規Handoff系列）

## 1. 最重要指示

現在は要件定義・技術選定・Architecture設計Phaseである。

このHandoffは、実装開始後に使用するEnvironment仕様を伝えるものであり、実装解禁ではない。

ユーザーから明示的な実装解禁を受けるまで、次を行わない。

- Python Install
- `.venv/`作成
- `uv` Install
- Package Install
- `pyproject.toml`作成・変更
- `uv.lock`作成・変更
- `.python-version`作成
- `.gitignore`変更
- `llama-cpp-python` Build
- Model Load Test

## 2. 確定したEnvironment基準

```text
Python          : CPython 3.13.14
Python Build    : ARM64／通常GIL
Python Fallback : CPython 3.12.13
Package Manager : uv 0.11.29
Virtual Env     : margpa-runtime-llm/.venv/
Install Policy  : Phase単位
Lock Policy     : uv.lockでExact Lock
```

Python 3.11.9は正式基準にしない。

## 3. Venv配置

Primary：

```text
margpa-runtime-llm/.venv/
```

`.venv/`はGit管理外とする。

深い日本語Pathを原因とするNative Build、Shebang、Toolchain問題が確認された場合のFallback：

```text
<USER_HOME>/.venvs/margpa-runtime-llm/
```

必要な場合のみ、Project Rootの`.venv`をExternal VenvへのPOSIX Symbolic Linkとする。

## 4. Phase 1で導入するDirect Dependency

### Core

```text
pydantic==2.13.4
pydantic-settings==2.14.2
psutil==7.2.2
```

### llama.cpp Backend

```text
llama-cpp-python==0.3.34
```

### Development

```text
pytest==9.1.1
pytest-asyncio==1.4.0
pytest-cov==7.1.0
ruff==0.15.22
mypy==2.3.0
```

### Notebook

```text
jupyterlab==4.6.1
notebook==7.6.0
ipykernel==7.3.0
```

実際のInstall直前に、同一Versionの公開状態、Security情報、Python 3.13対応、ARM64対応を再確認する。再確認なしにVersionを勝手に最新へ変更しない。

## 5. Dependency Group方針

初期有効化：

```text
core
inference-llama
dev
notebook
```

後続：

```text
Phase 2 : api
Phase 3 : governance
Phase 5 : rag
Phase 6 : agent
Optional: transformers
Optional: mlx
Cloud   : Localとは別Environment
```

将来利用しそうなPackageを最初に全部Installしない。

## 6. 後続Phaseの参考Version

以下は`2026-07-18`時点の参考であり、今はLockしない。

```text
Phase 2:
  fastapi==0.139.2
  uvicorn[standard]==0.51.0
  httpx==0.28.1

Phase 3:
  jsonschema==4.26.0

Phase 5 Candidate:
  langchain==1.3.14
  sentence-transformers==5.6.0
  transformers==5.14.1
  torch==2.13.0
  Vector Storeは未決定

Phase 6 Candidate:
  langgraph==1.2.9

Optional MLX Candidate:
  mlx==0.32.0
  mlx-lm==0.31.3
```

Guard／Judgeの初期GGUF構成は`llama-cpp-python`を共用するため、Phase 4で別の推論Libraryを追加することは必須ではない。

## 7. Python Fallback判定

Python 3.13から3.12へ落とす前に、次を順に確認する。

1. PythonがARM64通常GIL Buildか
2. Rosetta／x86_64 Toolが混入していないか
3. Xcode Command Line Toolsが利用可能か
4. Metal Build設定が正しいか
5. Projectの深い日本語Pathが原因でないか
6. External Venvで再現するか
7. CleanなEnvironmentとLock条件で再現するか

これらを確認してもMetal Buildが再現可能に成立しない場合のみ、Python 3.12.13を検討する。

Fallbackを行う場合は、設計者とユーザーへ次を報告する。

- Error内容
- 再現手順
- Python、OS、Architecture
- Xcode／Compiler情報
- 試したBuild条件
- External Venvでの結果
- 3.12へ落とす理由
- 影響範囲

## 8. Phase 1 Setup Acceptance Criteria

Environment Setup完了報告には、少なくとも次を含める。

- Python Version／Architecture／GIL種別
- Venv実体PathとProject側の見え方
- `uv` Version
- Direct Dependency Version一覧
- `uv.lock`再現確認
- Metal Backend有効性
- Qwen3-4B GGUF Load結果
- Minimal Generation結果
- Streaming／Stop結果
- Model Load／Unload結果
- Peak Memory
- Token生成速度
- Test結果
- Ruff結果
- mypy結果
- Jupyter KernelからのProject Import結果
- FallbackやDeviationの有無

## 9. 実装境界

- Backend固有のBuild／Import／Chat Template処理は`adapters/model_backends/llama_cpp/`へ閉じ込める
- Coreから`llama_cpp`を直接Importしない
- User固有のAbsolute PathをCoreへ入れない
- Venv PathをApplication Domainへ露出しない
- NotebookをApplication Runtime Dependencyにしない
- Jupyter上だけで成立するLogicを正本実装にしない
- `uv.lock`を無断で一括Updateしない
- Install済みTransitive DependencyをDirect Dependencyとして無目的に列挙しない
- RAG、Agent、Transformers、MLXをPhase 1へ前倒ししない

## 10. 読む順序

1. [documentation_index_20260718201744.md](../history/documentation_index_20260718201744.md)
2. [documentation_rules_20260718193435.md](../history/requirements/documentation_rules_20260718193435.md)
3. [implementer_handoff_20260718193435.md](../history/handoffs/implementer_handoff_20260718193435.md)
4. [python_environment_and_dependency_strategy_20260718201744.md](../history/architecture/python_environment_and_dependency_strategy_20260718201744.md)
5. [adr_0005_python_environment_and_dependency_management_20260718201744.md](../history/adr/adr_0005_python_environment_and_dependency_management_20260718201744.md)
6. [project_directory_structure_20260718192110.md](../history/architecture/project_directory_structure_20260718192110.md)


<!-- SOURCE_END 32: docs/handoffs/designer_python_environment_handoff_20260718201744.md -->

---

<!-- SOURCE_BEGIN 33: docs/handoffs/designer_review_phase_1_environment_and_metal_smoke_20260718212502.md -->

### Source 33: `docs/handoffs/designer_review_phase_1_environment_and_metal_smoke_20260718212502.md`

- History Target: `docs/project/phases/phase_1/history/handoffs/designer_review_phase_1_environment_and_metal_smoke_20260718212502.md`
- Source SHA-512: `0e214ec3527bffe1ed8647d2d63c31fa0cf8c63473a5e69b3857a9ed71826061de01755f0967d0f3e817a7962a6b628c9a07ac734e4e4c9b8bd95e13fc180588`
- Source Size: `13007` bytes

# Phase 1 Environment／Metal Smoke 設計レビューと実装担当へのFollow-up

- 文書ID: `designer_review_phase_1_environment_and_metal_smoke`
- 状態: `current_follow_up_required`
- 作成日時: `2026-07-18 21:25:02 JST`
- 更新日時: `2026-07-18 21:25:02 JST`
- 作成担当: 設計者役担当Task
- 対象: 実装者役担当Task
- 正本言語: 日本語
- Review対象: [implementer_status_phase_1_environment_and_metal_smoke_20260718210342.md](../history/handoffs/implementer_status_phase_1_environment_and_metal_smoke_20260718210342.md)
- Environment Architecture: [python_environment_and_dependency_strategy_20260718201744.md](../history/architecture/python_environment_and_dependency_strategy_20260718201744.md)
- Environment ADR: [adr_0005_python_environment_and_dependency_management_20260718201744.md](../history/adr/adr_0005_python_environment_and_dependency_management_20260718201744.md)
- Previous Environment Handoff: [designer_python_environment_handoff_20260718201744.md](../history/handoffs/designer_python_environment_handoff_20260718201744.md)
- supersedes: なし（新規Review系列）

## 1. Review Conclusion

Phase 1のEnvironment SetupおよびQwen3-4B／Metal Smoke Testは、主要な技術成立性について合格とする。

```text
Python 3.13.14        : Pass
ARM64                 : Pass
通常GIL               : Pass
llama-cpp-python      : Pass
Metal Backend         : Pass
Apple M2 Pro          : Pass
Qwen3-4B Model Load   : Pass
Japanese Generation  : Pass
Streaming Start       : Pass
Consumer-side Stop    : Pass
Post-stop Generation  : Pass
Explicit Close/Unload : Pass
Ruff                  : Pass
mypy --strict         : Pass
pytest                : Pass
Jupyter Import        : Pass
```

Python 3.12／3.11 Fallbackは不要であり、Primary構成のPython 3.13.14を継続採用する。

ただし、Environment再現性に関するFollow-upが2点残っているため、Environment Setup全体を完全完了とはまだ判定しない。

## 2. Independent Reviewで再確認した結果

設計者役担当Taskから、作成済みFileとEnvironmentを読み取り・実行検証した。

### 2.1 Python／Venv

```text
Python Version : 3.13.14
Implementation : CPython
Architecture   : arm64
GIL            : enabled
Venv           : margpa-runtime-llm/.venv/
```

`.venv/bin/python`は次のuv Managed Pythonを参照している。

```text
<USER_HOME>/.local/share/uv/python/cpython-3.13.14-macos-aarch64-none/bin/python3.13
```

Project Rootの`.venv/`自体は実Directoryであり、External Venv Fallbackは使用していない。

### 2.2 Dependency／Lock

`pyproject.toml`のDirect Dependency Versionと、EnvironmentにInstallされたVersionは一致した。

`uv.lock` SHA-256も実装報告と一致した。

```text
e5efe33d69105547fe0d4f348b6b189b85f7ed55323f8ecd993ef5df7846fee1
```

RAG、Agent、Transformers、MLX等の後続Phase Packageが未導入であることも確認した。

### 2.3 Static Verification

```text
Ruff Check        : Pass
Ruff Format Check : Pass
mypy --strict     : Pass
pytest            : 2 passed
```

### 2.4 Metal／Model Smoke再実行

Sandbox内では、実装報告と同じ`Failed to create llama_context`を再現した。

Sandbox外で同一Smoke Testを再実行し、次を確認した。

```text
Result                    : success
Python                    : 3.13.14
Architecture              : arm64
GIL                       : enabled
GPU                       : Apple M2 Pro
Metal Embedded Library    : enabled
Unified Memory            : true
GPU Offload Support       : true
Qwen3 Metadata            : qwen3
Chat Template Metadata    : present
Model Size                : 2,497,280,256Byte
Model Load                : 約0.3701秒（Warm Metal Library条件）
Generation                : 約0.4401秒
Completion Token          : 13
Observed Speed            : 約29.54 token/s
Peak Process RSS          : 約2.79GB
Explicit Unload後RSS      : 約136MB
Streaming Start           : success
Consumer-side Close       : success
Post-close Generation     : success
Stop Sequence             : finish_reason=stop
```

生成結果：

```text
<think>

</think>

メタルスモークテスト成功。
```

Python 3.13、Project Path、Model Artifact、Native Buildはいずれも成立している。

### 2.5 Jupyter再実行

Sandbox外でJupyter Kernelを起動し、Project Package Importに成功した。

```text
Package Version : 0.0.0
Python Version  : 3.13.14
Architecture    : arm64
Kernel Python   : margpa-runtime-llm/.venv/bin/python
```

Kernel起動時にLocal TCP通信の暗号化Warningが出た。現在はLocal Development用の短時間VerificationでありPhase 1のBlockerにはしない。JupyterをNetwork公開する設計にはしない。

## 3. Required Follow-up 1: uv実行Fileの永続配置

### 3.1 Finding

実装報告では次を記録している。

```text
Package Manager : uv 0.11.29
uv sync --frozen --offline : 成功
uv lock --check            : 成功
```

しかし設計者Taskの通常Login Shellでは、次となった。

```text
uv: command not found
```

次の一般的な配置候補にも永続的な`uv`実行Fileを確認できなかった。

```text
~/.local/bin/
~/.cargo/bin/
/opt/homebrew/bin/
/usr/local/bin/
```

uv Managed Pythonとuv Cacheは残っているため、実装Task固有または一時的なTool Pathからuvを使用した可能性がある。

### 3.2 Impact

- ユーザーが通常のTerminalから`uv sync`できない
- 別Taskが同じLock検証を再実行できない
- Environmentの再構築手順がTask固有になる
- `uv 0.11.29`採用というADRを満たし切らない

現在の`.venv`実行には直ちに影響しないが、Environment再現性要件に反する。

### 3.3 Required Action

実装担当は、ユーザーからFollow-up実装の許可を得た後、uvを永続的なUser Toolとして利用可能にする。

許容する方式：

- uv公式Standalone InstallerによるUser Scope配置
- Homebrew等、ユーザーが選択した永続Tool管理
- その他、通常Login Shellと別Taskから再現可能な方式

避けるもの：

- Task固有Temporary Directoryだけに存在するuv
- Project `.venv`へのRuntime Dependencyとしてのuv追加
- System Python Package群への無管理な混在
- Version未記録の自動Update

### 3.4 Acceptance Criteria

```text
command -v uv        : 永続Pathを返す
uv --version         : uv 0.11.29を確認できる
uv lock --check      : 成功
uv sync --frozen     : 成功
別Task／通常Shell    : 同じ結果を再現できる
```

Versionを変更する場合は、設計者とユーザーへ理由を報告する。

## 4. Required Follow-up 2: Metal Source Build Recipeの永続化

### 4.1 Finding

実装時は次でSource Buildした。

```text
CMAKE_ARGS=-DGGML_METAL=on
```

一方、現在の`pyproject.toml`と`uv.lock`が固定しているのは、主に次である。

```text
llama-cpp-python==0.3.34
sdist URL
sdist SHA-256
Dependency Version
```

`GGML_METAL=on`というNative Build条件は`uv.lock`へ記録されない。

既存Environmentでの`uv sync --frozen --offline`成功は、uv Cache内のBuild済みArtifactを再利用した可能性がある。新規MachineまたはClean Buildで同じMetal Backendになることを、現在のProject Fileだけから保証できない。

### 4.2 Impact

- Fresh EnvironmentでMetalが無効になる可能性
- Build手順が会話またはStatus Reportだけに依存する
- GitHub利用者が同じBackendを再現できない
- Lock Fileの再現性とNative Buildの再現性を混同する

### 4.3 Required Action

実装担当は、Metal Build条件をProject内の再現可能なSetup経路へ永続化する。

候補：

- `scripts/setup/`以下の明示的なEnvironment Setup Script
- uvのPackage別Build設定
- Platform別Setup Config
- 上記を組み合わせた方式

要件：

- macOS／ARM64 Local Profileだけへ適用する
- Core LogicへBuild Flagを入れない
- Cloud／CUDA ProfileへMetal設定を漏らさない
- `llama-cpp-python==0.3.34`とBuild条件を同じSetup経路で確認できる
- Setup Scriptは失敗時に非Zero Exitを返す
- 実行前提条件を明記する

### 4.4 Acceptance Criteria

Fresh Venvまたは同等のClean条件で、次を再現する。

```text
Python                     : 3.13.14 / arm64
llama-cpp-python           : 0.3.34
llama_supports_gpu_offload : true
System Info                : MTLを含む
Apple M2 Pro               : 認識
Qwen3-4B Load              : success
Minimal Generation         : success
```

`uv.lock`だけではNative Build Flagを保証しないことを、Setup手順またはStatusへ明記する。

## 5. Recommended Follow-up: Opt-in Model Smoke Test

### 5.1 Finding

`pyproject.toml`には次のPytest Markerがある。

```text
model_smoke
```

現在のTest Suiteには、このMarkerを使用してQwen3 ModelをLoadするTestがない。

現在の2 Testは高速で妥当だが、実Model Smokeは手動Scriptに限定されている。

### 5.2 Recommendation

通常の`pytest`では大型ModelをLoadしない。

明示指定時だけ実行するOpt-in TestをPhase 1-Bまたはその完了前に追加する。

概念：

```text
Default Test      : 高速、ModelをLoadしない
model_smoke Test  : Local ModelとMetalがある場合だけ明示実行
```

TestはModel Artifactがない環境で明確にSkipし、暗黙Downloadを行わない。

これはRequired Follow-up 1／2の完了を妨げるBlockerではない。

## 6. Recommended Follow-up: Cold Init計測

### 6.1 Finding

現在の`run_metal_smoke`は、`llama_print_system_info()`を呼んだ後にModel Load計測を開始する。

Metal LibraryのCold InitializationがModel Load秒数から除外される可能性がある。

実装報告では次を分離して正しく説明している。

```text
Metal Cold Library Init
Model Load after Metal Init
```

しかし`MetalSmokeResult`のJSON FieldにはCold Init専用値がない。

### 6.2 Recommendation

Performance Resultとして利用する段階では、少なくとも次を分離する。

```text
Backend Cold Init
Model Load after Backend Init
First Token Latency
Total Generation Latency
Token per Second
Unload Latency
```

現在はSmoke Testであり、Phase 1-B開始のBlockerにはしない。

## 7. Known Non-blocking Item: Qwen3 Thinking Tag

`/no_think`を指定しても、次の空Tagが残る。

```text
<think>

</think>
```

これはMetal／Python Build失敗ではない。

次の設計判断まで未決として維持する。

- ThinkingをDefault On／Offのどちらにするか
- Chat Templateへどのように渡すか
- UI／CLIで切替可能にするか
- Empty Thinking Tagを表示時に除去するか
- AuditへRaw OutputとDisplay Outputをどう記録するか

Smoke Test側でProduction Policyを先に確定しない。

## 8. Phase 1 Completion Boundary

今回完了した範囲：

```text
Phase 1-A
  Environment Setup
  Python／Venv／Dependency
  llama.cpp Metal技術検証
  Qwen3-4B Load／Generation Smoke
  Streaming／Consumer-side Stop Probe
  Memory／速度観測
  Development Tool Verification
```

まだ完了していない範囲：

```text
Phase 1-B
  Model Port
  Model Capability
  Generation Request
  Generation Result
  Streaming Chunk
  Stop／Finish Reason
  Error Contract
  llama.cpp Production Adapter
  Model Registry
  Config Schema
  Generation Default
  Production CLI
```

「Phase 1-A技術検証完了」と「Phase 1全体完了」を混同しない。

## 9. Gate to Phase 1-B

推奨順序：

1. uv永続配置を確定する
2. Metal Build RecipeをProjectへ永続化する
3. 別Task／Fresh条件で再現性を確認する
4. Follow-up Statusを新Timestampで作成する
5. 設計者へReviewを依頼する
6. Model Port／Contractの詳細設計を確定する
7. ユーザーからPhase 1-B実装許可を得る
8. Phase 1-Bを実装する

Required Follow-up 1／2が完了する前に、Phase 2、Governance、RAG、Agentへ進まない。

## 10. Follow-up Statusに必要な情報

実装担当は新しいStatusへ次を記録する。

- uv実体Path
- uv Version
- 通常Login Shellでの確認結果
- 別Taskからの確認結果
- Metal Build Recipeの保存場所
- 適用Platform条件
- Fresh／Clean相当のBuild方法
- `llama-cpp-python` Version
- Build ArtifactまたはPackage Verification
- GPU Offload確認
- Qwen3 Smoke結果
- Lock File変更の有無
- Source／Script／Config変更一覧
- Test／Ruff／mypy結果
- DeviationまたはFallbackの有無

## 11. Authorization Boundary

このDocumentは設計Reviewと推奨Follow-up Scopeを定義する。

uv Install、Setup Script追加、Build再実行、Source変更、Phase 1-B実装を自動的に解禁するものではない。

実装担当は、ユーザーから許可された範囲だけを実施する。


<!-- SOURCE_END 33: docs/handoffs/designer_review_phase_1_environment_and_metal_smoke_20260718212502.md -->

---

<!-- SOURCE_BEGIN 34: docs/handoffs/designer_review_phase_1_environment_reproducibility_follow_up_20260718221255.md -->

### Source 34: `docs/handoffs/designer_review_phase_1_environment_reproducibility_follow_up_20260718221255.md`

- History Target: `docs/project/phases/phase_1/history/handoffs/designer_review_phase_1_environment_reproducibility_follow_up_20260718221255.md`
- Source SHA-512: `0cc99b0ab9089b5371e6b6208076743087e242233888d3a3d26247da71c160dc81a2bb12fab9080dac0788941201185867a808e00b1e63d878f6cf2c3b6a5138`
- Source Size: `8973` bytes

# Phase 1 Environment再現性 Follow-up 設計レビュー

- 文書ID: `designer_review_phase_1_environment_reproducibility_follow_up`
- 状態: `accepted_phase_1_a_complete`
- 作成日時: `2026-07-18 22:12:55 JST`
- 更新日時: `2026-07-18 22:12:55 JST`
- 作成担当: 設計者役担当Task
- 対象: 実装者役担当Task
- 正本言語: 日本語
- Documentation Index: [documentation_index_20260718221255.md](../history/documentation_index_20260718221255.md)
- Review対象: [implementer_status_phase_1_environment_reproducibility_follow_up_20260718214958.md](../history/handoffs/implementer_status_phase_1_environment_reproducibility_follow_up_20260718214958.md)
- Previous Review: [designer_review_phase_1_environment_and_metal_smoke_20260718212502.md](../history/handoffs/designer_review_phase_1_environment_and_metal_smoke_20260718212502.md)
- supersedes: `designer_review_phase_1_environment_and_metal_smoke_20260718212502.md`

## 1. Review Conclusion

Phase 1-AのEnvironment再現性Follow-upを合格とする。

前回ReviewでRequired Follow-upとした2項目は完了した。

```text
Required Follow-up 1: uv実行Fileの永続配置            : Pass
Required Follow-up 2: Metal Source Build Recipe永続化 : Pass
```

Recommended Follow-upとしていた次の2項目も完了した。

```text
Opt-in model_smoke Test : Pass
計測Fieldの分離         : Pass
```

重大または中程度の問題は確認されなかった。

これにより、Phase 1-AのEnvironment Setup、Python／Venv／Dependency、llama.cpp Metal Backend、Qwen3-4B実Model Smokeおよび再現性確認を完了と判定する。

Phase 1-B、Phase 2、Governance、RAG、Agentは未着手であり、本Reviewはそれらの実装を解禁しない。

## 2. Independent Verification

設計者役担当Taskから、Follow-up報告、Project内File、現在Environmentおよび実Modelを独立確認した。

### 2.1 uv／Login Shell／Lock

新規Zsh Login Shellから次を確認した。

```text
command -v uv          : <USER_HOME>/.local/bin/uv
uv --version           : uv 0.11.29
Architecture           : aarch64-apple-darwin
uv lock --check        : Pass／117 packages resolved
uv sync --frozen       : Pass
uv sync --offline      : Pass／115 packages checked
```

`uv`および`uvx`はUser Scopeの永続Pathへ配置され、別Taskと通常Login Shellから利用可能になった。

### 2.2 Environment／Static Verification

```text
Python                  : CPython 3.13.14
Architecture            : arm64
GIL                     : enabled
Venv                    : Project Root/.venv
Direct Dependency       : Exact Version一致
Out-of-scope Package    : 未導入
llama-cpp-python        : 0.3.34
GPU Offload             : supported
Backend System Info     : MTLあり
bash -n                 : Pass
Ruff Check              : Pass
Ruff Format Check       : Pass／18 files
mypy --strict           : Pass／18 source files
Default pytest          : 2 passed, 1 deselected
```

`uv.lock` SHA-256はFollow-up報告と一致した。

```text
e5efe33d69105547fe0d4f348b6b189b85f7ed55323f8ecd993ef5df7846fee1
```

### 2.3 Opt-in実Model Smoke

Sandbox外で明示的に`model_smoke`を実行した。

```text
pytest -m model_smoke : 1 passed, 2 deselected
```

次を独立確認した。

- Local Qwen3-4B GGUFを暗黙Downloadせずに使用
- Apple Silicon／Metal Backend
- GPU Offload
- Model Load
- Chat Template Metadata
- Japanese Generation
- Streaming開始とConsumer-side Close
- Close後の再Generation
- Stop Sequence
- Explicit Model Close／Unload経路

通常の`pytest`では`model_smoke`が除外され、明示指定時だけ大型ModelをLoadする構成も成立している。

## 3. Setup Recipe Review

対象：

[setup_macos_arm64_metal.sh](../../../../../scripts/setup/setup_macos_arm64_metal.sh)

次を確認した。

- `set -euo pipefail`を使用する
- macOS／ARM64以外では非Zero Exitとする
- Xcode Command Line Tools／Apple clangを事前確認する
- PATH上の`uv 0.11.29`を確認する
- `uv.lock`を変更せず`uv lock --check`を実行する
- uv Managed CPython `3.13.14`を指定する
- `llama-cpp-python==0.3.34`をSource Buildする
- `CMAKE_ARGS=-DGGML_METAL=on`を対象の`uv sync` Processだけへ設定する
- Cloud／CUDA ProfileやApplication CoreへMetal Flagを伝播しない
- `--clean-source-build`では存在しないTarget Venvを要求する
- `--no-cache`によるClean相当Build経路を持つ
- `--smoke`指定時だけLocal ModelをLoadする
- Model Artifactを暗黙Downloadしない

Platform Guard、Metal Flag Scope、Dependency固定および失敗時の非Zero Exitは、現在のArchitecture／ADRに適合する。

## 4. Fresh Build Evidenceの扱い

Follow-up報告には、新規Temporary Venvと`--no-cache`を使用したFresh／Clean相当Buildの成功証跡がある。

設計者役担当Taskでは、再Downloadと全Native Buildを伴う同一Fresh Buildを重ねて再実行していない。

代わりに次を独立確認した。

- Setup Recipeの静的検査
- 現在EnvironmentのExact Version検査
- Login ShellからのLock／Offline Sync
- Metal／GPU Offload検査
- opt-in Qwen3実Model Smoke
- Follow-up報告のBuild条件、結果、Native Library Hash

上記を総合し、Fresh Build証跡を受理する。

## 5. Known Non-blocking Item: 通常Setup時のNative再Build

Setup Recipeは通常実行時にも次を指定する。

```text
--no-binary-package llama-cpp-python
--reinstall-package llama-cpp-python
```

このため、通常のEnvironment同期でも`llama-cpp-python`を毎回Sourceから再Buildする。

### 5.1 Impact

- Setupの実行時間が長くなる
- CPU使用率、発熱および消費電力が増える
- Dependency変更がない場合にもNative Buildが発生する

一方、毎回`GGML_METAL=on`を明示したSource Buildになるため、現時点ではNative Build条件の再現性を優先した保守的な構成として妥当である。

Phase 1-AのBlockerにはしない。直ちに修正する必要もない。

### 5.2 Future Recommendation

実運用でSetup頻度やBuild時間が問題になった場合、次の経路分離を検討する。

```text
Normal Sync
  └─ Lock済みEnvironmentを同期し、不要なNative再Buildを避ける

Explicit Native Rebuild
  └─ llama-cpp-pythonをGGML_METAL=onで明示的に再Buildする

Fresh Reproducibility Build
  └─ 新規Venv＋使い捨てCacheで完全検証する
```

候補Interfaceは`--rebuild-native`等であるが、具体名とDefault動作は将来の設計判断とする。

分離する場合も、Metal Build Flag、Version固定およびFresh再現性検証経路を失ってはならない。

## 6. Other Known Non-blocking Item

Qwen3へ`/no_think`を指定しても、空の`<think></think>`相当Tagが生成結果に残る場合がある。

これはPython／Metal／Model Loadの問題ではない。

Production Model Adapter、Raw Output、Display OutputおよびAudit LogのContract設計時に扱いを決める。

## 7. Phase Boundary

完了：

```text
Phase 1-A
  Environment Setup
  Python 3.13.14／Project .venv／uv 0.11.29
  Dependency Lock／Exact Version Verification
  llama-cpp-python Metal Source Build Recipe
  Qwen3-4B Model Load／Generation Smoke
  Streaming／Consumer-side Stop Probe
  Explicit Close／Unload Probe
  Opt-in model_smoke Test
  Fresh／Clean相当Build Evidence
```

未着手：

```text
Phase 1-B
  Model Port／Capability
  Generation Request／Result／Streaming Chunk
  Stop／Finish Reason／Error Contract
  llama.cpp Production Adapter
  Model Registry
  Config Schema／Generation Default
  Production CLI
```

「Phase 1-A完了」と「Phase 1全体完了」を混同しない。

## 8. Review／Index作成運用

今後、設計者役が実装報告等の正式Reviewを完了した場合は、原則として同じ作業単位で次の2文書を新規作成する。

1. Review結果を記録する新TimestampのReview文書
2. そのReviewと対象StatusをCurrent Document Setへ反映する新Timestampの`documentation_index`

旧Reviewと旧Indexは上書きしない。

新Indexでは、旧Review、旧Statusおよび旧Indexの状態と後継関係を示す。

## 9. Next Gate

次にPhase 1-Bへ進む場合は、次の順序を基本とする。

1. Model Port／Capability／Request／Result等の詳細設計
2. llama.cpp Production Adapterの責務境界確定
3. Config／Registry／CLIのMVP境界確定
4. 実装担当への新しいHandoff作成
5. ユーザーによるPhase 1-B実装許可
6. 実装
7. 実装Status作成
8. 設計Reviewと同時に最新Index作成

## 10. Authorization Boundary

このDocumentはPhase 1-A Follow-upの受入結果と、次段階へ進むための設計上のGateを記録する。

Phase 1-B実装、Setup Recipe変更、Dependency変更または追加Package Installを自動的に解禁するものではない。


<!-- SOURCE_END 34: docs/handoffs/designer_review_phase_1_environment_reproducibility_follow_up_20260718221255.md -->

---

<!-- SOURCE_BEGIN 35: docs/handoffs/designer_review_phase_1_final_readiness_20260719171836.md -->

### Source 35: `docs/handoffs/designer_review_phase_1_final_readiness_20260719171836.md`

- History Target: `docs/project/phases/phase_1/history/handoffs/designer_review_phase_1_final_readiness_20260719171836.md`
- Source SHA-512: `f4371467886f3c72fb815293ffed948e5de8eaa07a37546fc5e7061f18c1bfeba8e7b05b4da6b84842317b4abc40135853471dd54631b02a018d92d71a9676ba`
- Source Size: `7356` bytes

# Phase 1 Cross-phase 最終Readiness Review

- 文書ID: `designer_review_phase_1_final_readiness`
- 状態: `ready_for_user_acceptance_test`
- 作成日時: `2026-07-19 17:18:36 JST`
- 更新日時: `2026-07-19 17:18:36 JST`
- Snapshot: `20260719171836`
- 作成担当: 設計者役担当Task
- 対象: Top-Level Phase 1-A～1-EのCross-phase最終確認
- 正本言語: 日本語
- Current User Manual: [phase_1_macos_user_manual_20260719171836.md](../history/user_manual/phase_1_macos_user_manual_20260719171836.md)
- Current Roadmap: [implementation_roadmap_20260719171836.md](../history/architecture/implementation_roadmap_20260719171836.md)
- Current Index: [documentation_index_20260719171836.md](../history/documentation_index_20260719171836.md)
- Backup Policy: [phase_completion_backup_policy_20260719171836.md](../history/operations/phase_completion_backup_policy_20260719171836.md)
- supersedes: なし（Phase 1 Cross-phase Readiness Reviewの新規系列）

## 1. 結論

Phase 1-A～1-Eの実装、個別Review、Current User Manual、Cross-phase整合性を確認し、Phase 1を`Ready for User Acceptance Test`と判定する。

```text
Phase 1-A～1-E Individual Acceptance : Pass
Cross-phase Architecture Boundary     : Pass
Static／Default Gate                  : Pass
Native Mac／Metal Gate                : Pass
Current User Manual                   : Ready
Known Blocking Issue                  : 0
User Acceptance Test                  : Waiting
Designer Completion Declaration       : Waiting
Backup Dual Approval Gate             : Not Satisfied
```

本Reviewは、Top-Level Phase 1の完了宣言ではない。

## 2. Subphase Acceptance

| Subphase | 対象 | 状態 | Final Evidence |
|---|---|---|---|
| Phase 1-A | Environment／Metal Smoke | Complete／Accepted | [Phase 1-A Review](../history/handoffs/designer_review_phase_1_environment_reproducibility_follow_up_20260718221255.md) |
| Phase 1-B | Model Runtime／CLI | Complete／Accepted | [Phase 1-B Review](../history/handoffs/designer_review_phase_1b_model_runtime_final_20260719001604.md) |
| Phase 1-C | Platform／Acceleration Hook | Complete／Accepted | [Phase 1-C Review](../history/handoffs/designer_review_phase_1c_final_20260719035156.md) |
| Phase 1-D | Config／Response Language | Complete／Accepted | [Phase 1-D Review](../history/handoffs/designer_review_phase_1d_final_20260719122035.md) |
| Phase 1-E | Thinking Presentation | Complete／Accepted | [Phase 1-E Review](../history/handoffs/designer_review_phase_1e_final_20260719164641.md) |

必須Subphaseに未受入またはRequired Follow-upは残っていない。

## 3. Cross-phase構造確認

### 3.1 Environment／Dependency

- Python `3.13.14`
- `.venv/`
- `uv.lock`
- `llama-cpp-python 0.3.34`
- Metal Build／GPU Offload
- Out-of-scope Dependencyなし

### 3.2 Model Runtime Boundary

- Model PortはRaw `GenerationResult`／`GenerationChunk`を維持
- llama.cpp固有処理はAdapterへ局所化
- Model ArtifactはProject外Storage
- Model DefinitionがArtifact、Backend、Capability、Output Protocolを所有

### 3.3 Configuration Boundary

```text
Application Config Schema : 2
Model Definition Schema   : 2
Deployment Profile Schema : 3
Platform Registry         : Alias／Profile Resolution
```

Common Generation／Response／PresentationをPlatform Profileへ重複させていない。

### 3.4 Platform Boundary

- Current Native VerificationはmacOS／arm64／Metal
- Windows／Linux／CPU／CUDA／ROCmはHookとValidation境界のみ
- 未検証PlatformをVerifiedと表示しない
- Capability不足、Profile不整合、Unsupported PlatformをSilent Fallbackしない

### 3.5 Language／Thinking Boundary

- `ja／en／auto`
- Thinking ExecutionとVisibilityが独立
- Canonical ProtocolとDisplay Labelが独立
- Hidden No-flash
- Custom Label
- Raw Reasoning Persistence disabled
- Thinking FlagによるSampling暗黙変更なし

## 4. 独立Evidence

最新Phase 1-E Final Review時点：

```text
ruff format --check . : Pass／68 files
ruff check .          : Pass
mypy                  : Pass／68 source files
compileall            : Pass
bash -n               : Pass
pytest -q             : 161 passed, 2 deselected
pytest -q -m model_smoke
                     : 2 passed, 161 deselected
uv lock --check       : Resolved 117 packages
uv offline dry-run    : Checked 115 packages／Would make no changes
Environment Verify    : Python 3.13.14／arm64／Metal／Dependency Pass
```

Phase 1-E Review後、Source、Config、Tests、Dependency、Model Definitionは変更されていない。本Snapshotで追加したのはDocsのみである。

## 5. Current User Manual確認

[phase_1_macos_user_manual_20260719171836.md](../history/user_manual/phase_1_macos_user_manual_20260719171836.md)は、旧ManualのPhase 1-A／1-B限定状態を解消し、次を含む。

- Phase 1-A～1-EのScope
- Current Environment／Schema／Default
- Platform Verification境界
- Environment Verification
- `model-info`
- Config Ownership
- Streaming／Non-streaming
- `ja／en／auto`
- Thinking Hidden／Visible／Custom Label
- Ctrl+C Cancel
- Default／Native Test
- Known Diagnostic Observation
- User Acceptance Checklist
- User Test Pass Declaration形式
- Backup Dual Approval Gate

ManualはUser Acceptance Test開始可能である。

## 6. Known Issues／Observations

Current Register：

- [known_issues_and_observations_20260719171836.md](../history/operations/known_issues_and_observations_20260719171836.md)

`MARGPA-OBS-0001`はLow／Accepted Deferredである。不正なMixed-source ConfigのError Code Attribution精度に関するもので、不正値拒否、Runtime動作、安全境界、Phase 1 AcceptanceをBlockしない。

## 7. User Acceptance Gate

ユーザーはCurrent ManualのSection 22に従い、同じProject状態で13項目を確認する。

合格時の推奨宣言：

```text
phase_1_macos_user_manual_20260719171836.mdの
Phase 1ユーザー受入テストは、全項目合格です。
```

失敗または未実施がある場合は合格宣言を行わず、項目番号とSafe Errorを共有する。

## 8. Designer Completion Gate

User Acceptance Test合格宣言を確認し、その後にMaterial Changeがないことを確認した時点で、設計者役は次の意味を明示できる。

```text
Phase 1は完了です。
Phase 2へ移行可能です。
```

本Review作成時点ではUser Acceptance Testが未実施のため、このDesigner Gateを成立させない。

## 9. Backup Gate

Backupは次の両方が同じProject状態について成立した後に実行可能となる。

1. User Acceptance Test Pass Declaration
2. Designer Phase Completion／Next Phase Eligible Declaration

現在：

```text
User Gate     : Waiting
Designer Gate : Waiting
Backup        : Not Authorized／Not Triggered
```

## 10. Next Action

次に行うことは、ユーザーによるCurrent ManualのPhase 1 User Acceptance Testである。

合格宣言後、設計者役は状態凍結を確認し、Top-Level Phase 1完了・Phase 2移行可能を宣言する。その後、ユーザーの指示または承認済みScopeによりPhase 1 Backupを作成・検証する。

## 11. Authorization Boundary

本Reviewで実施していないもの：

- Source／Config／Testsの修正
- User Acceptance Testの代行宣言
- Top-Level Phase 1完了宣言
- Phase 2移行可能宣言
- Backup Archive／Manifest／Receipt生成
- Phase 2実装


<!-- SOURCE_END 35: docs/handoffs/designer_review_phase_1_final_readiness_20260719171836.md -->

---

<!-- SOURCE_BEGIN 36: docs/handoffs/designer_review_phase_1_mac_web_ui_user_acceptance_and_follow_up_20260725192903.md -->

### Source 36: `docs/handoffs/designer_review_phase_1_mac_web_ui_user_acceptance_and_follow_up_20260725192903.md`

- History Target: `docs/project/phases/phase_1/history/handoffs/designer_review_phase_1_mac_web_ui_user_acceptance_and_follow_up_20260725192903.md`
- Source SHA-512: `38d3171a9494b033b59ca13c3f2f1a0daee38503b1de9156f338bbc7e166f91ff2852b48649fdd1e857e5c7422e804cdc5faf3d215cad02e8dfb97dd4e4e4131`
- Source Size: `10439` bytes

# Phase 1 Mac Web UI User Acceptance Review and Follow-up

- 文書ID: `designer_review_phase_1_mac_web_ui_user_acceptance_and_follow_up`
- 状態: `reviewed_with_follow_up`
- 作成日時: `2026-07-25 19:29:03 JST`
- 作成担当: 設計者役担当Task
- 対象環境: Mac／Local Web Preview
- 対象Phase: Phase 1-G／1-HおよびPhase 1-F Follow-up
- 実装許可: 本文書単独では付与しない

## 1. Review Outcome

Mac Web Previewは、Phase 1の最小公開評価画面として想定した構成と動作を概ね満たしている。

```text
Visual Composition                    : PASS
Ephemeral Multi-turn                 : PASS
New Chat／Browser Memory Reset       : PASS
Model Reload Separation              : PASS
Send Button                          : PASS
Stop Button                          : PASS
Ctrl+Enter Send                      : PASS
Token Limit Behavior                 : PASS
UI Language Switch                   : PASS
Response Language Switch             : PASS
Summary Mode                         : PASS
Thinking Presentation               : EXPLAINED／UX FOLLOW-UP
Markdown Presentation                : NOT IMPLEMENTED／FOLLOW-UP
User／Assistant Copy                 : NOT IMPLEMENTED／FOLLOW-UP
```

Phase 1-G／1-Hの既存Repository Acceptanceを覆す重大Failureは確認されていない。一方、Thinking設定の意味が画面だけでは分かりにくいため、Top-level Phase 1の最終User Acceptance前に扱いを明示する必要がある。

## 2. Visual Evidence Reviewed

次のLocal Screenshotを視認した。

- `スクリーンショット 2026-07-25 19.12.25.png`
- `スクリーンショット 2026-07-25 19.12.35.png`

Absolute Local Pathは本公開候補文書へ記録しない。Screenshot自体は現在Repository Artifactではない。

確認できた画面要素：

- Nazuna Research Governance LLM Branding
- `MARGPA Runtime LLM` Title
- Model／Profile／Device／Acceleration表示
- UI日本語／英語切替
- New Chat
- Preview注意表示
- Message Timeline
- Composer
- Stop／Send
- Response Language
- Max New Tokens
- Thinking Visibility
- Summary Mode
- Thinking／Summary注意事項

Desktop Previewとして、Header、Message、Composer、Settingsの責務分離は明確であり、Phase 1 UIとして想定どおりである。

## 3. User Test Inputs

代表的な入力：

```text
キミの役割は？
you are task？
小型LLMを交換可能にする設計を考えてください。日本語で。
```

同一Promptの複数回実行、言語切替、複数Turn、長い構造化回答、Token上限による途中停止を含む。

Model Outputの内容品質は本UI Acceptanceと分離する。回答が一般的でProject固有情報を持たない点は、Model RuntimeのFailureではなく、将来のProject Documentation Explainer／RAGが価値を持つObservationである。

## 4. Confirmed Behavior

### 4.1 Ephemeral Multi-turn

同一Browser Tab内でUser／Assistant Messageが交互にRequestへ含まれ、複数Turnが成立した。

Persistent Historyではない。Reload時に失われるPhase 1のBrowser Memoryであり、Phase 2の永続Conversationとは区別する。

### 4.2 New Chat

「新しいChat」によりBrowser Memoryが初期化された。

```text
Browser Memoryを初期化しました。ModelはReloadされません。
```

表示と実際のContractが一致している。Model LifecycleとConversation Lifecycleの分離も確認できた。

### 4.3 Send／Stop

- Send Buttonが動作した。
- Stop Buttonが動作した。
- `Ctrl+Enter`で送信できた。
- Current Web実装は`Cmd+Enter`にも対応する。

利用者がShortcutを発見できる表示がないため、Composer周辺に「`Cmd+Enter`／`Ctrl+Enter`で送信」等のHintを追加する候補とする。

### 4.4 Token Limit

User指定の254 Tokenで出力が切れることを確認した。Current Web Contractは1～2048を受け付ける。

Token上限到達と通常完了を区別し、最終回答前に上限へ到達した場合のWarningを維持する。

### 4.5 Language Separation

- UI Languageの日本語／英語切替が動作した。
- Response Languageの`ja／en／auto`切替が動作した。
- UI LanguageとResponse Languageは独立していた。

### 4.6 Summary Mode

Summary Mode `OFF／ON`が動作した。Summaryは同じMain ModelをSequentialに再利用するため、LatencyとToken Usageが増える注意事項を維持する。

## 5. Finding — Thinking Visibility

### 5.1 Observation

「推論過程を表示」をONにしても、推論過程が画面へ現れなかった。

### 5.2 Root Cause

Current Config：

```toml
[generation]
thinking_mode = "disabled"

[presentation.thinking]
visibility = "hidden"
```

Web UIがRequestごとに送信するのは`thinking_visibility`であり、`thinking_mode`ではない。

Conversation ServiceはWeb Requestから`max_new_tokens`とPresentation Visibilityを変更するが、Thinking GenerationはApplication Defaultの`disabled`を維持する。

したがって、

```text
Thinking Generation   : disabled
Thinking Visibility   : visible
Generated Think Block : none
Visible Think Block   : none
```

となる。表示対象そのものが生成されていないため、CheckboxをONにしても何も出ない。

### 5.3 Assessment

Core Contract上は想定可能な状態であり、Parser／Presentation Failureとは断定しない。ただし、UI Labelだけを見ると「ONにすればThinkingが出る」と解釈しやすい。

### 5.4 Follow-up Requirement

- Thinking GenerationとThinking Visibilityを別設定として保持する。
- Generation OFFの場合、Visibility ControlをDisableするか「現在は生成されません」と表示する。
- 研究・開発者向け設定にThinking Generation `OFF／ON`を配置する候補とする。
- 一般利用者向けDefaultはGeneration OFF／Visibility Hidden候補とする。
- Raw Thinking非保存を維持する。
- Thinking内容を真の内部思考、正解または説明責任の完全な証拠として扱わない。

## 6. Finding — Markdown Presentation

### 6.1 Observation

Assistant OutputのMarkdown記号が、そのままPlain Textとして表示された。

### 6.2 Root Cause

Phase 1 Web UIは、XSSを避けるため`innerHTML`を使用せず、Messageを`textContent`で表示する。

既存Integration Testも次を要求している。

```text
innerHTML : absent
textContent : present
```

したがって、現状は意図した安全側のPhase 1実装である。

### 6.3 Follow-up Requirement

Assistant Outputを主要LLM Productに近いMarkdown表示へ発展させる。

- Rendering対象はAssistantのCanonical Contentとする。
- User InputはDefault Plain Textとする。
- Raw HTMLはDefault Disabledとする。
- Sanitizerまたは同等Allowlistを必須にする。
- Script、Event Handler、危険なURL Schemeを拒否する。
- Streaming中の不完全Markdownを安全に扱う。
- 初期候補はStreaming中をPlain Text、Completion後にMarkdown Renderingとする。
- Canonical ContentとRendered DOMを分離する。

SecurityとStreaming設計が必要なため、Default配置はPhase 4候補とする。

## 7. Follow-up — Message Copy

User MessageとAssistant MessageへCopy Buttonを追加する候補とする。

- UserはCanonical Input TextをCopyする。
- AssistantはCanonical Assistant ContentをCopyする。
- Rendered HTMLを無条件にCopyしない。
- Hidden Thinking、Metadata、非表示Original Summaryを混入させない。
- Copy成功／失敗Feedbackを表示する。
- 日本語／英語UI、Keyboard、Touchへ対応する。
- Clipboard内容のReadは行わない。

比較的小さい機能であり、Phase 1 Completionを遅延させない場合は前倒し可能である。

## 8. Lightning Linux x86_64 Pure CPU Follow-up

### 8.1 Existing State

既存File：

```text
config/profiles/lightning_linux_x86_64_cpu.toml
```

既存Profileは次の状態である。

```text
compute_kind_key  : cpu
gpu_layers        : 0
build_variant_key : cuda
```

これはPure CPU Buildではなく、CUDA BuildのBackendをCPU実行するProfileである。

既存Setup ScriptもCUDA Buildの存在を検証し、未構築時はCUDA Toolkit／`nvcc`を必要とする可能性がある。

### 8.2 Requirement

Freshな最小CPU Studioでも再構築できるよう、Pure CPU RuntimeをCUDA Runtimeから分離する。

- GPU不要
- NVIDIA Driver不要
- CUDA Toolkit不要
- `nvcc`不要
- `gpu_layers = 0`
- CPU BuildであることをRuntime Observationへ記録
- Python 3.12系のSupport
- CPU専用Setup／Preflight／Acceptance
- Fresh Environment再構築
- Model Digest検証
- Bounded Smoke
- Latency／Memory／Token／Error記録

### 8.3 Candidate Artifacts

```text
config/profiles/lightning_linux_x86_64_cpu_native.toml
scripts/setup/setup_lightning_linux_x86_64_cpu.sh
```

最終名称は既存CUDA CPU Execution ProfileとのMigrationを含めて決定する。

### 8.4 Acceptance Candidates

- NVIDIA DeviceがなくてもPreflightが通る。
- `nvcc`がなくてもSetupが完了する。
- BackendがCUDA Supportを必須にしない。
- DeviceがCPUとして観測される。
- `gpu_layers = 0`がEffective Configへ反映される。
- Qwen3-4B Q4_K_Mの短いGenerationが完了する。
- Cancel／Token Limit／LanguageがCPU環境でもContractどおり動作する。
- CPUの遅さをFailureと誤認せず、TimeoutとBounded Smokeを分離する。

## 9. Priority Proposal

```text
P0:
  Thinking Generation／Visibility状態の説明またはUI整合

P1:
  Shortcut Hint
  Message Copy
  Lightning Pure CPU Profile

P2:
  Sanitized Markdown Presentation
```

Markdown PresentationをPhase 1へ前倒しする場合も、SanitizerとStreaming Completion境界を省略しない。

## 10. Authorization Boundary

本文書はReview、要件整理および将来Handoff候補である。

次を自動許可しない。

- Web UI変更
- Markdown Library追加
- Copy Button実装
- Thinking Control変更
- Pure CPU Profile／Script実装
- Dependency Installation
- Model Download
- 外部環境操作
- Git／GitHub操作

実装開始時は、対象範囲、Phase GateおよびAcceptanceを確定した実装担当向けHandoffを別途作成する。

<!-- SOURCE_END 36: docs/handoffs/designer_review_phase_1_mac_web_ui_user_acceptance_and_follow_up_20260725192903.md -->

---

<!-- SOURCE_BEGIN 37: docs/handoffs/designer_review_phase_1b_model_runtime_20260718233938.md -->

### Source 37: `docs/handoffs/designer_review_phase_1b_model_runtime_20260718233938.md`

- History Target: `docs/project/phases/phase_1/history/handoffs/designer_review_phase_1b_model_runtime_20260718233938.md`
- Source SHA-512: `058ac6f71c3c2c57870231eb117416091e6eea91cc1bae25f55b8669e56431e30e991a32d75e19aae35100b39cf654f38630bb127c4df8b6b670ab0a740a6d9b`
- Source Size: `12112` bytes

# Phase 1-B Model Runtime 設計レビュー

- 文書ID: `designer_review_phase_1b_model_runtime`
- 状態: `follow_up_required`
- 作成日時: `2026-07-18 23:39:38 JST`
- 更新日時: `2026-07-18 23:39:38 JST`
- 作成担当: 設計者役担当Task
- 対象: 実装者役担当Task
- 正本言語: 日本語
- Documentation Index: [documentation_index_20260718233938.md](../history/documentation_index_20260718233938.md)
- Review対象: [implementer_status_phase_1b_model_runtime_20260718232354.md](../history/handoffs/implementer_status_phase_1b_model_runtime_20260718232354.md)
- 詳細設計: [phase_1b_model_runtime_contract_20260718223203.md](../history/architecture/phase_1b_model_runtime_contract_20260718223203.md)
- Accepted ADR: [adr_0006_model_runtime_port_and_configuration_20260718224308.md](../history/adr/adr_0006_model_runtime_port_and_configuration_20260718224308.md)
- Previous Phase Review: [designer_review_phase_1_environment_reproducibility_follow_up_20260718221255.md](../history/handoffs/designer_review_phase_1_environment_reproducibility_follow_up_20260718221255.md)
- supersedes: なし（新規Phase 1-B Review系列）

## 1. Review Conclusion

Phase 1-B Model Runtimeは、主要な骨格、Model Port、llama.cpp Adapter、Config、CLI、Contract、実Model／Metal経路まで成立している。

一方、Phase 1-Bの明示的Acceptance Criteriaに反する問題1件と、Runtime Info／将来Auditの事実性に関わる問題1件を確認した。

```text
Required Follow-up 1: 実CLIのCtrl+C Cooperative Cancel修正     : Fail
Required Follow-up 2: Artifact Digestの観測値／期待値分離     : Fail
```

このため、現時点ではPhase 1-Bを最終受入しない。

実装担当は2件を修正し、Regression Testと新しいAppend-Only Statusを作成する。設計者はそのStatusと実装を再レビューする。

Phase 1-CまたはPhase 2の実装開始可否は、本Reviewだけでは確定しない。

## 2. Findings

### 2.1 [P1／Required] 実StreamがKeyboardInterruptを推論失敗へ変換する

対象：

- [stream.py](../../../../../src/margpa_runtime_llm/adapters/model_backends/llama_cpp/stream.py)
- [main.py](../../../../../src/margpa_runtime_llm/entrypoints/cli/main.py)
- [test_cli.py](../../../../../tests/unit/inference/test_cli.py)

`LlamaCppGenerationStream.__iter__()`は、`GeneratorExit`と`InferenceError`以外の`BaseException`を捕捉し、`generation_failed`へ変換する。

`KeyboardInterrupt`は`BaseException`の派生であるため、CLIの次の処理へ到達しない。

```text
CLIがKeyboardInterruptを受け取る
  ↓
stream.cancel()
  ↓
Terminal State = cancelled
  ↓
"Generation cancelled."
  ↓
Exit Code = 130
```

実際の経路は次となる。

```text
Ctrl+C
  ↓
LlamaCppGenerationStream.__iter__がKeyboardInterruptを捕捉
  ↓
Terminal State = failed
  ↓
InferenceError(code=generation_failed)
  ↓
CLI Error表示
  ↓
Exit Code = 4
```

実CLIへ生成中にCtrl+Cを送った独立確認結果：

```text
^Cerror [generation_failed]: Streaming failed in the model backend.
```

報告書の次の記載は、現在のProduction Stream経路では成立していない。

```text
Cooperative Cancel : Pass
User Cancel        : Terminal State=cancelled／CLI Exit Code=130
```

現在のCLI Unit Testは、`KeyboardInterrupt`を直接送出する`FakeStream`をCLIへ渡している。このFakeは`LlamaCppGenerationStream.__iter__()`の例外変換を通らないため、境界間の不整合を検出できない。

また、`adapter.py`のLoad、Unload、Non-stream Generation、Stream生成前処理にも`except BaseException`があり、`KeyboardInterrupt`と`SystemExit`をBackend Errorへ変換し得る。Backend由来の通常例外とProcess Control Exceptionの境界を全体で見直す。

#### Required Acceptance

- 実`LlamaCppGenerationStream`経路で`KeyboardInterrupt`を通常の`generation_failed`へ変換しない
- CLIが割込みを受け、`stream.cancel()`を実行する
- Stream Terminal Stateを`cancelled`とする
- Generation Lockを解放する
- CLI Exit Codeを`130`とする
- `Generation cancelled.`を安全に表示する
- Cancel後に同一Model Instanceで再Generationできる
- `LlamaCppGenerationStream`とCLIを組み合わせたRegression Testを追加する
- Backend Error Mappingが`KeyboardInterrupt`／`SystemExit`を飲み込まないことをTestする

### 2.2 [P2／Required] Hash未検証時にRegistry期待値を実測Digestとして返す

対象：

- [adapter.py](../../../../../src/margpa_runtime_llm/adapters/model_backends/llama_cpp/adapter.py)
- [runtime.py](../../../../../src/margpa_runtime_llm/modules/inference/contracts/runtime.py)
- [test_llama_cpp_boundary.py](../../../../../tests/unit/inference/test_llama_cpp_boundary.py)

`_verify_artifact()`は、最初に次を設定する。

```text
actual_digest = definition.artifact.sha512
```

`verify_artifact_hash=true`の場合だけFileを読み、実際のSHA-512へ置き換える。

したがって`verify_artifact_hash=false`の場合、File内容をHashしていないにもかかわらず、Registryの期待値を`actual_digest`として返す。返された値は`ModelRuntimeInfo.artifact_digest`へ格納される。

独立した最小再現では、登録SHA-512を`000...000`、同一Sizeの実File内容を別内容とし、Hash検証を無効化したところ、未観測の`000...000`が返された。

```text
verify_artifact_hash : false
File Hash計算        : 未実施
reported digest      : Registry期待値
```

Default Profileは`verify_artifact_hash=true`であり、今回の通常Metal実行で得たDigestは検証済みである。この問題はDefault Profileの実Model Hash結果を否定しない。

しかし、設定を無効化したRuntimeでは、期待値と観測値を区別できない。これは将来のAudit Log、Model Runtime Reference、再現性および「System Trace由来の事実」と矛盾する。

#### Required Acceptance

- Registry Expected DigestとRuntimeでObserved／VerifiedされたDigestを混同しない
- Hash未検証時に、未観測値を実測値として表現しない
- 次のいずれか、または同等に明示的なContractを採用する
  - Phase 1-Bでは常にHashを検証し、無効化設定を廃止する
  - Observed DigestをNullableにし、Verification Stateを別Fieldで持つ
  - Expected Digest、Observed Digest、Verification Stateを分離する
- `verify_artifact_hash=false`かつ同一Size／別内容のTestを追加する
- `model-info`と将来Audit Consumerが検証済みか否かを判別できるようにする

## 3. Independent Verification

設計者役担当Taskから、実装報告、設計正本、ADR、Config、Source、Test、CLIおよび実Model／Metalを独立確認した。

### 3.1 Static／Default Test

```text
bash -n Setup Recipe       : Pass
Ruff Format Check          : Pass／48 files
Ruff Check                 : Pass
mypy --strict              : Pass／48 source files
compileall                 : Pass
Default pytest             : 40 passed, 2 deselected
Environment Verification   : Pass
Core llama_cpp Import Scan : Pass／0件
Out-of-scope Import Scan   : Pass／0件
```

Environment：

```text
Python             : CPython 3.13.14／arm64／GIL enabled
llama-cpp-python   : 0.3.34
GPU Offload        : supported
Metal System Info  : present
Out-of-scope Model Framework Package: absent
```

### 3.2 Dependency Lock／Offline Dry-run

Phase 1 Setup Recipeと同じExtra／Groupを指定して、環境を変更しないDry-runを確認した。

```text
uv lock --check : Pass／117 packages
uv sync --dry-run --frozen --offline
  --extra inference-llama
  --group dev
  --group notebook
  --no-binary-package llama-cpp-python
Result           : Checked 115 packages／Would make no changes
```

### 3.3 Config Hash

報告書記載値と一致した。

```text
Model Definition SHA-512:
723954f2cd8f9df77a48614da05206c532ab56666069e57e117bddc219dcaefe5ad32b57f9b315b1e2e9cab5ba3526dad2176ca8d2df3ec997c05034bd98c415

Local Profile SHA-512:
f0d9c8e3ffe9264b77e0c7ca357705a200fc5419175910479ab53a8e49c543d13fb86484309d22ed39b57c81d10888e129282c62254da097ec89c3208b9b6b35
```

### 3.4 Opt-in実Model／Metal

制限環境内ではMetal Contextを作成できないため、Metalアクセス可能な実機条件で明示的に再実行した。

```text
pytest -m model_smoke : 2 passed, 40 deselected
```

次を独立確認した。

- Qwen3-4B GGUFを暗黙DownloadせずLoadする
- llama-cpp-python 0.3.34／Metal／GPU Offload
- Context 4,096
- Artifact Size／SHA-512
- Embedded Chat Template
- Thinking Default OFF／Explicit ON
- One-shot Generation
- Streaming／Final Chunk
- 明示的`stream.cancel()`
- Cancel後の再Generation
- Explicit Unload／Unload Idempotency

明示的な`stream.cancel()`は正常である。Finding 2.1は、OS／Terminal由来の`KeyboardInterrupt`をProduction Streamが誤変換する問題であり、Cancel API自体の失敗ではない。

## 4. Acceptance Matrix

```text
Model-independent Contract        : Pass
Model Port Protocol               : Pass
llama.cpp Adapter isolation       : Pass
Registry／Config Validation       : Pass
Qwen3-4B Load／Unload             : Pass
Default Context 4,096             : Pass
Thinking Default OFF             : Pass
Thinking Explicit ON             : Pass
One-shot Generation              : Pass
Streaming                        : Pass
Explicit Stream Cancel           : Pass
CLI Ctrl+C Cooperative Cancel     : Fail／Required Follow-up
Post-cancel Generation            : Pass
Finish Reason Mapping             : Pass
Token Usage／Timing               : Pass
Capability Validation            : Pass
Safe Error Contract               : Pass
Runtime Digest Truthfulness       : Fail／Required Follow-up
Unit／Contract／Integration Test  : Partial／Regression不足
Ruff／mypy --strict              : Pass
Modelの暗黙Downloadなし          : Pass
Phase 2以降への越境なし          : Pass
```

## 5. Non-blocking Observation

同一ModelのIdempotent Load判定は、現在`model_key`だけを比較する。

同じKeyで異なる`ModelDefinition`または`ModelLoadConfig`を渡しても、既存の`runtime_info`を返す。現在のPhase 1-B Bootstrapは1回Loadするため、直ちに障害にはなっていない。

将来、Profile変更やContext Size変更を同一Processへ適用する場合は、次のいずれかを明示する。

- Idempotent条件をModel Key、Definition Hash、Load Configの同一性まで含める
- Load済みConfigと異なる場合は明示Errorにする
- Config変更には明示Unload／Reloadが必要とContractへ記載する

本項目は今回のRequired Follow-upには含めない。

## 6. Required Follow-up Scope

実装担当は、Source／Testの必要最小範囲で次を行う。

1. Process Control ExceptionとBackend Errorの境界を修正する
2. 実Stream経由のCtrl+C Regression Testを追加する
3. CLI Exit Code 130、Terminal State、Lock解放、Post-cancel Generationを確認する
4. Artifact Expected／Observed／Verifiedの意味を修正する
5. Hash検証無効時のRegression Testを追加する
6. Default Test、Static Gate、Opt-in Metal Testを再実行する
7. 新Timestampの`implementer_status_phase_1b_model_runtime_follow_up_*.md`を作成する

設計Contract自体の変更が必要な場合は、既存Architecture／ADRを編集せず、設計者へ報告する。

## 7. Authorization Boundary

本Reviewは調査と受入判定を記録する。

Source修正、Contract変更、Config変更、Dependency変更またはPhase 2実装を自動的に許可するものではない。実装担当はユーザーから与えられたWrite Scopeと実装許可に従う。

## 8. Re-review Gate

次を満たした後にPhase 1-Bを再レビューする。

1. Required Follow-up 2件が実装される
2. Regression Testが追加される
3. Static／Default／Metal GateがPassする
4. 新しいImplementer Statusが作成される
5. 設計者がSourceと実CLIを再確認する


<!-- SOURCE_END 37: docs/handoffs/designer_review_phase_1b_model_runtime_20260718233938.md -->

---

<!-- SOURCE_BEGIN 38: docs/handoffs/designer_review_phase_1b_model_runtime_final_20260719001604.md -->

### Source 38: `docs/handoffs/designer_review_phase_1b_model_runtime_final_20260719001604.md`

- History Target: `docs/project/phases/phase_1/history/handoffs/designer_review_phase_1b_model_runtime_final_20260719001604.md`
- Source SHA-512: `6d0ab754e784eadfb1fcf012afba94c2b3dc48a53363f310df6c3d53defe8b8dcbda50422f5cebb315ee27632c6735e9577948474cf2cb63732ba5933b6735ef`
- Source Size: `8458` bytes

# Phase 1-B Model Runtime 最終設計レビュー

- 文書ID: `designer_review_phase_1b_model_runtime_final`
- 状態: `accepted_phase_1b_complete`
- 作成日時: `2026-07-19 00:16:04 JST`
- 更新日時: `2026-07-19 00:16:04 JST`
- 作成担当: 設計者役担当Task
- 対象: 実装者役担当Task
- 正本言語: 日本語
- Documentation Index: [documentation_index_20260719001604.md](../history/documentation_index_20260719001604.md)
- Review対象: [implementer_status_phase_1b_model_runtime_test_follow_up_20260719001341.md](../history/handoffs/implementer_status_phase_1b_model_runtime_test_follow_up_20260719001341.md)
- Previous Review: [designer_review_phase_1b_model_runtime_follow_up_20260719000348.md](../history/handoffs/designer_review_phase_1b_model_runtime_follow_up_20260719000348.md)
- Initial Phase 1-B Review: [designer_review_phase_1b_model_runtime_20260718233938.md](../history/handoffs/designer_review_phase_1b_model_runtime_20260718233938.md)
- 詳細設計: [phase_1b_model_runtime_contract_20260718223203.md](../history/architecture/phase_1b_model_runtime_contract_20260718223203.md)
- Accepted ADR: [adr_0006_model_runtime_port_and_configuration_20260718224308.md](../history/adr/adr_0006_model_runtime_port_and_configuration_20260718224308.md)
- supersedes: `designer_review_phase_1b_model_runtime_follow_up_20260719000348.md`

## 1. Review Conclusion

Phase 1-B Model Runtimeを最終受入し、完了と判定する。

前回までのRequired Follow-up 2件とTest-only Follow-up 1件は、すべて完了した。

```text
実CLI Ctrl+C Cooperative Cancel       : Pass
Artifact Digest事実性                 : Pass
false Config Regression Test Fixture  : Pass
Pydantic Contract直接Test             : Pass
Static／Default Gate                   : Pass
実Model／Metal Gate                    : Pass／直前独立確認を継承
```

重大、中程度または軽微な未解決不具合は、今回のReview Scopeでは確認されなかった。

Phase 1-BのModel非依存Contract、llama.cpp Production Adapter、Qwen3-4B／Metal Runtime、Registry／Config、CLI、Streaming、Cancel、Artifact VerificationおよびTestは、次段階の基盤として利用できる。

本ReviewはPhase 1-B完了を示す。次Phaseの設計または実装を自動的に解禁するものではない。

## 2. Test-only Follow-up確認

対象：

- [test_config_and_registry.py](../../../../../tests/unit/inference/test_config_and_registry.py)

### 2.1 有効な単一Key TOML

Fixtureは、既存Profileの次の値そのものを置換する。

```text
verify_artifact_hash = true
  ↓
verify_artifact_hash = false
```

確認した事項：

- `tomllib.loads()`が成功する
- Fixture内の`verify_artifact_hash`は1件だけである
- Parse後の`load.verify_artifact_hash`は`false`である
- `load_phase1_profile()`が`invalid_configuration`を返す

旧TestのTOML重複KeyによるFalse Positiveは解消された。

### 2.2 Pydantic Contract直接Test

次の直接Validationが追加された。

```text
ModelLoadConfig.model_validate({"verify_artifact_hash": False})
  ↓
pydantic.ValidationError
```

将来、`Literal[True]`が通常の`bool`へ誤って緩和された場合、このTestはFailする。

前回Required Test Acceptanceを満たした。

## 3. Independent Verification

### 3.1 Targeted Test

```text
tests/unit/inference/test_config_and_registry.py : 7 passed
```

### 3.2 Static／Default Gate

```text
bash -n Setup Recipe       : Pass
Ruff Format Check          : Pass／48 files
Ruff Check                 : Pass
mypy --strict              : Pass／48 source files
compileall                 : Pass
Default pytest             : 47 passed, 2 deselected
Environment Verification   : Pass
```

Environment：

```text
Python                    : CPython 3.13.14／arm64／GIL enabled
llama-cpp-python          : 0.3.34
GPU Offload Support       : true
Metal System Info         : present
Dependency Version Match  : true
Out-of-scope Package      : absent
```

### 3.3 Production不変性

今回の変更はTest Fileだけである。

前回Review文書より後に更新されたProduction Python SourceとConfigは確認されなかった。

報告書記載Hashも一致した。

```text
Model Definition SHA-512 : 723954f2cd8f9df77a48614da05206c532ab56666069e57e117bddc219dcaefe5ad32b57f9b315b1e2e9cab5ba3526dad2176ca8d2df3ec997c05034bd98c415
Local Profile SHA-512    : f0d9c8e3ffe9264b77e0c7ca357705a200fc5419175910479ab53a8e49c543d13fb86484309d22ed39b57c81d10888e129282c62254da097ec89c3208b9b6b35
pyproject.toml SHA-256   : a46fcd0b61e8db84a5f90ac4459b92bf9ec9deb7d6219ce88d7b22c240b5ecfa
uv.lock SHA-256         : e5efe33d69105547fe0d4f348b6b189b85f7ed55323f8ecd993ef5df7846fee1
```

Production Source、Config、DependencyおよびModel Artifactが不変であるため、今回Metal Gateは重ねて実行していない。

直前の設計者独立Reviewで次を確認済みである。

```text
pytest -m model_smoke : 2 passed, 46 deselected
実TTY Ctrl+C          : Generation cancelled.／Exit Code 130
model-info            : artifact_digest_verified=true／Metal／GPU Offload
```

この証跡を本最終Reviewへ継承する。

## 4. Phase 1-B Final Acceptance Matrix

```text
Model-independent Contract          : Pass
Model Port Protocol                 : Pass
llama.cpp Adapter isolation         : Pass
Registry／Config Validation         : Pass
Qwen3-4B Load／Unload               : Pass
Default Context 4,096               : Pass
Thinking Default OFF               : Pass
Thinking Explicit ON               : Pass
One-shot Generation                : Pass
Streaming                          : Pass
Explicit Stream Cancel             : Pass
実CLI Ctrl+C Cooperative Cancel     : Pass
CLI Exit Code 130                   : Pass
Post-cancel Generation              : Pass
Finish Reason Mapping               : Pass
Token Usage／Timing                 : Pass
Capability Validation              : Pass
Safe Error Contract                 : Pass
SHA-512常時検証                     : Pass
Runtime Digest事実性                : Pass
model-info Verification State       : Pass
false Config拒否                    : Pass
false Config Regression Protection  : Pass
Unit／Contract／Integration Test    : Pass
Ruff／mypy --strict                : Pass
Modelの暗黙Downloadなし            : Pass
Phase 2以降への越境なし            : Pass
```

## 5. Phase 1-B Completion Scope

完了：

```text
Inference Domain／Public Contract
Model Port／Lifecycle／Capability
llama.cpp Production Adapter
Qwen3-4B GGUF／Metal Runtime
Embedded Chat Template／Thinking Control
One-shot Generation／Streaming
Cooperative Cancel／Ctrl+C
Token Usage／Timing／Finish Reason
Context Overflow Policy
Safe Error Mapping
Model Registry／TOML Profile
Artifact Size／SHA-512 Verification
Runtime Info／Verification State
Config優先順位
Bootstrap／Dependency Injection
Phase 1-B CLI
Unit／Contract／実Model Integration Test
```

未着手：

```text
Multi-Turn Conversation
Conversation History／Storage
FastAPI／Web UI
Runtime Governance本実装
Audit Log本実装
Guard／Judge
RAG
Agent／Tool実行
複数Model同時常駐／Router
Remote／MLX／Transformers／vLLM Adapter
```

## 6. Known Non-blocking Items

次はPhase 1-B Blockerではない既知事項として維持する。

- 同一ModelのIdempotent Load判定は現在Model Keyだけを比較する
- Load済みDefinition／Load Configが異なる場合の扱いは後続設計事項
- Distribution Revision／Commitを推測で補完しない
- Raw Output／Display Output分離は後続設計事項
- Native Buildの毎回再BuildはPhase 1-A既知事項
- `.DS_Store`再生成は別のRepository Hygiene事項

## 7. Next Gate

次段階へ進む前に、設計者とユーザーが少なくとも次を決める。

1. 次の実装単位をPhase 2 Multi-Turn／Web UIとするか
2. 会話Session、Message、HistoryのContract
3. Storage MVP境界
4. FastAPI／UI技術の最終選択
5. Streaming CancelをHTTP／UI境界へ接続する方式
6. 実装担当HandoffとWrite Scope

次段階の実装は、新しい設計、Handoffおよびユーザー許可後に行う。

## 8. Authorization Boundary

本ReviewはPhase 1-Bの最終受入と完了を記録する。

Phase 2、Runtime Governance、Audit、Guard、Judge、RAG、Agent、追加Dependencyまたは新しいDirectory／Configの実装を自動的に解禁するものではない。


<!-- SOURCE_END 38: docs/handoffs/designer_review_phase_1b_model_runtime_final_20260719001604.md -->

---

<!-- SOURCE_BEGIN 39: docs/handoffs/designer_review_phase_1b_model_runtime_follow_up_20260719000348.md -->

### Source 39: `docs/handoffs/designer_review_phase_1b_model_runtime_follow_up_20260719000348.md`

- History Target: `docs/project/phases/phase_1/history/handoffs/designer_review_phase_1b_model_runtime_follow_up_20260719000348.md`
- Source SHA-512: `a0cff329611408ac690ead909454db2980afa8d308ff21b1633be89b711a0f2aafe90036e57971fd7703c472338df1d0e659c69bb1013aaf119402a1f41ae9a9`
- Source Size: `10150` bytes

# Phase 1-B Model Runtime Follow-up 設計レビュー

- 文書ID: `designer_review_phase_1b_model_runtime_follow_up`
- 状態: `test_follow_up_required`
- 作成日時: `2026-07-19 00:03:48 JST`
- 更新日時: `2026-07-19 00:03:48 JST`
- 作成担当: 設計者役担当Task
- 対象: 実装者役担当Task
- 正本言語: 日本語
- Documentation Index: [documentation_index_20260719000348.md](../history/documentation_index_20260719000348.md)
- Review対象: [implementer_status_phase_1b_model_runtime_follow_up_20260718235802.md](../history/handoffs/implementer_status_phase_1b_model_runtime_follow_up_20260718235802.md)
- Previous Review: [designer_review_phase_1b_model_runtime_20260718233938.md](../history/handoffs/designer_review_phase_1b_model_runtime_20260718233938.md)
- 詳細設計: [phase_1b_model_runtime_contract_20260718223203.md](../history/architecture/phase_1b_model_runtime_contract_20260718223203.md)
- Accepted ADR: [adr_0006_model_runtime_port_and_configuration_20260718224308.md](../history/adr/adr_0006_model_runtime_port_and_configuration_20260718224308.md)
- supersedes: `designer_review_phase_1b_model_runtime_20260718233938.md`

## 1. Review Conclusion

前回ReviewでRequired Follow-upとしたRuntime実装2件は、Source、Contract、実CLI、実Model／Metalの独立確認で合格した。

```text
Required Follow-up 1: 実CLI Ctrl+C Cooperative Cancel : Pass
Required Follow-up 2: Artifact Digest事実性           : Pass
```

新たなRuntime不具合は確認されなかった。

ただし、Hash検証無効化を拒否するRegression Testが、意図したPydantic ContractではなくTOML重複KeyエラーによってPassしている。

```text
Runtime Source Fix          : Pass
実CLI／Metal                : Pass
Artifact Verification       : Pass
Required Regression Test    : Fail／Test Fixture修正のみ必要
```

したがってPhase 1-B Runtime実装本体は受理可能な状態であるが、前回Required Acceptanceに含めたRegression Test完了までは最終受入を保留する。

必要なFollow-upはTest File 1件の最小修正であり、Production Source、Config、Dependencyまたは実Modelの変更は不要である。

## 2. Required Follow-up確認

### 2.1 Ctrl+C Cooperative Cancel

対象：

- [stream.py](../../../../../src/margpa_runtime_llm/adapters/model_backends/llama_cpp/stream.py)
- [error_mapping.py](../../../../../src/margpa_runtime_llm/adapters/model_backends/llama_cpp/error_mapping.py)
- [adapter.py](../../../../../src/margpa_runtime_llm/adapters/model_backends/llama_cpp/adapter.py)
- [main.py](../../../../../src/margpa_runtime_llm/entrypoints/cli/main.py)

確認結果：

- `LlamaCppGenerationStream`はBackend由来の`Exception`だけをError Mappingする
- `KeyboardInterrupt`／`SystemExit`を`generation_failed`へ変換しない
- Error MapperにもProcess Control Exceptionを再送出するDefense-in-depthがある
- Stream開始前のProcess Control ExceptionでGeneration Lockを解放する
- Non-stream Generationは`finally`でGeneration Lockを解放する
- CLIが`KeyboardInterrupt`を受けて`stream.cancel()`を実行する
- CancelによりNative IteratorをCloseし、Terminal Callbackを1回実行する
- Terminal Stateを`cancelled`とする
- Cancel後に同じServiceでGeneration可能なRegression Testがある

実TTYへ長いStreaming Generation中にCtrl+Cを送った独立結果：

```text
^C
Generation cancelled.
Exit Code: 130
```

`generation_failed`は表示されなかった。

Follow-up 1はPassとする。

### 2.2 Artifact Digest事実性

対象：

- [runtime.py](../../../../../src/margpa_runtime_llm/modules/inference/contracts/runtime.py)
- [adapter.py](../../../../../src/margpa_runtime_llm/adapters/model_backends/llama_cpp/adapter.py)
- [config_and_registry test](../../../../../tests/unit/inference/test_config_and_registry.py)
- [llama.cpp boundary test](../../../../../tests/unit/inference/test_llama_cpp_boundary.py)

確認結果：

- `ModelLoadConfig.verify_artifact_hash`は`Literal[True]`
- `_verify_artifact()`はFile全体のSHA-512を常に計算する
- Registry期待値を実測値として代入する旧処理は存在しない
- File Size一致／Digest不一致を`model_integrity_mismatch`で拒否する
- `ModelRuntimeInfo`は`artifact_digest_verified=true`を持つ
- Production Adapterは検証成功後にだけRuntime Infoを構築する
- 実`model-info`は検証済みDigestを構造化表示する

実`model-info`独立結果：

```text
artifact_digest.algorithm : sha512
artifact_digest.value     : f182f1d40606572d6965e50e0ef33c4be64b43ad65339710ceebb664e3d43e76398a4ef230c7a3dd8fbd643acbce8f0c7cbec28784203ccf26da0fe7e08bfceb
artifact_digest_verified  : true
device                    : metal
gpu_offload               : true
```

有効なTOMLで`verify_artifact_hash=false`だけを設定した独立確認では、`invalid_configuration`として拒否された。

Follow-up 2のProduction ContractとRuntime動作はPassとする。

## 3. Finding

### 3.1 [P3／Required Test Correction] Hash無効化Testが重複TOMLを検査している

対象：

- [test_config_and_registry.py](../../../../../tests/unit/inference/test_config_and_registry.py)

現在のTestは次の置換を行う。

```text
verbose_backend = false
```

を次へ置換する。

```text
verbose_backend = false
verify_artifact_hash = false
```

しかし元のProfileには、直後に既存の次の設定がある。

```text
verify_artifact_hash = true
```

生成されるFixtureは同じTable内に`verify_artifact_hash`を2回持つ。

独立確認結果：

```text
tomllib.loads(fixture)
  ↓
TOMLDecodeError: Cannot overwrite a value
```

したがってTestは、`ModelLoadConfig.verify_artifact_hash: Literal[True]`が`false`を拒否したためではなく、TOML Parserが重複Keyを拒否したためにPassしている。

このままでは、将来`Literal[True]`制約が誤って通常の`bool`へ戻ってもTestが緑のままとなる。

#### Required Test Acceptance

- 元Profileの`verify_artifact_hash = true`を`false`へ置換する
- 生成Fixtureが有効なTOMLであることを前提にする
- `load_phase1_profile()`が`invalid_configuration`を返すことを確認する
- 可能であれば`ModelLoadConfig(verify_artifact_hash=False)`自体もValidation Errorになることを直接Testする
- Default Testを再実行する
- 新TimestampのImplementer Statusを作成する

Production Source修正は不要である。

## 4. Independent Verification

### 4.1 Static／Default Gate

```text
bash -n Setup Recipe       : Pass
Ruff Format Check          : Pass／48 files
Ruff Check                 : Pass
mypy --strict              : Pass／48 source files
compileall                 : Pass
Default pytest             : 46 passed, 2 deselected
Environment Verification   : Pass
Core llama_cpp Import Scan : Pass／0件
Out-of-scope Import Scan   : Pass／0件
```

### 4.2 実Model／Metal Gate

Metalアクセス可能な実機条件で確認した。

```text
pytest -m model_smoke : 2 passed, 46 deselected
```

確認項目：

- Qwen3-4B Artifact SHA-512検証
- llama-cpp-python 0.3.34
- Metal／GPU Offload
- Context 4,096
- Thinking Default OFF／Explicit ON
- One-shot Generation
- Streaming
- 明示Cancel
- Cancel後の再Generation
- Unload／Unload Idempotency

### 4.3 Dependency／Hash

```text
uv lock --check : Pass／117 packages
uv sync --dry-run --frozen --offline
  --extra inference-llama
  --group dev
  --group notebook
  --no-binary-package llama-cpp-python
Result           : Checked 115 packages／Would make no changes
```

報告書記載Hashはすべて一致した。

```text
Model Definition SHA-512 : 723954f2cd8f9df77a48614da05206c532ab56666069e57e117bddc219dcaefe5ad32b57f9b315b1e2e9cab5ba3526dad2176ca8d2df3ec997c05034bd98c415
Local Profile SHA-512    : f0d9c8e3ffe9264b77e0c7ca357705a200fc5419175910479ab53a8e49c543d13fb86484309d22ed39b57c81d10888e129282c62254da097ec89c3208b9b6b35
pyproject.toml SHA-256   : a46fcd0b61e8db84a5f90ac4459b92bf9ec9deb7d6219ce88d7b22c240b5ecfa
uv.lock SHA-256         : e5efe33d69105547fe0d4f348b6b189b85f7ed55323f8ecd993ef5df7846fee1
```

## 5. Acceptance Matrix

```text
Process Control Exception境界     : Pass
実CLI Ctrl+C                       : Pass
CLI Exit Code 130                  : Pass
Stream Terminal State cancelled   : Pass
Generation Lock解放               : Pass
Cancel後の再Generation            : Pass
SHA-512常時検証                    : Pass
同一Size／Digest不一致拒否         : Pass
Runtime Digest事実性               : Pass
model-info Verification State      : Pass
Regression Test／Ctrl+C            : Pass
Regression Test／Digest不一致      : Pass
Regression Test／false Config拒否  : Fail／Fixture修正必要
Static／Default Gate               : Pass
実Model／Metal Gate                : Pass
Dependency／Config不変             : Pass
Phase 2以降への越境                : なし
```

## 6. Non-blocking Items

前回までの次の項目は変更していない。

- 同一ModelのIdempotent Load判定は現在Model Keyだけを比較する
- Load済みDefinition／Load Configが異なる場合の扱いは後続設計事項
- Distribution Revision／Commitを推測で補完しない
- Raw Output／Display Output分離は後続設計事項
- Native Buildの毎回再BuildはPhase 1-A既知事項

## 7. Re-review Gate

次を満たした後にPhase 1-Bを最終受入する。

1. `verify_artifact_hash=false`のTest Fixtureを有効なTOMLへ修正する
2. 意図したPydantic Contract拒否を確認する
3. Default Test／Static Gateを再実行する
4. 新しいImplementer Statusを作成する
5. 設計者がTestと結果を再確認する

Production Source、Config、Dependencyまたは実Modelを変更した場合は、対象に応じてMetal Gateも再実行する。

## 8. Authorization Boundary

本ReviewはFollow-up結果の確認と、Test-only残件を記録する。

Test修正、Source変更、Config変更、Dependency変更または次Phase実装を自動的に許可するものではない。実装担当はユーザーから与えられたWrite Scopeと実装許可に従う。


<!-- SOURCE_END 39: docs/handoffs/designer_review_phase_1b_model_runtime_follow_up_20260719000348.md -->

---

<!-- SOURCE_BEGIN 40: docs/handoffs/designer_review_phase_1c_deployment_platform_acceleration_follow_up_20260719030341.md -->

### Source 40: `docs/handoffs/designer_review_phase_1c_deployment_platform_acceleration_follow_up_20260719030341.md`

- History Target: `docs/project/phases/phase_1/history/handoffs/designer_review_phase_1c_deployment_platform_acceleration_follow_up_20260719030341.md`
- Source SHA-512: `294ca94ee218fd67f5409f0d30392d5aafec1b72ab541acef08e3004182f799fc577d462545f8e341399834136dbd7a32b2ec9b6392eec427f0d2f2fe6be970d`
- Source Size: `12610` bytes

# Phase 1-C Deployment／Platform／Acceleration Follow-up設計レビュー

- 文書ID: `designer_review_phase_1c_deployment_platform_acceleration_follow_up`
- 状態: `changes_requested_phase_1c_follow_up_partial_acceptance`
- 作成日時: `2026-07-19 03:03:41 JST`
- 更新日時: `2026-07-19 03:03:41 JST`
- 作成担当: 設計者役担当Task
- 対象: 実装者役担当Task
- 正本言語: 日本語
- Documentation Index: [documentation_index_20260719030341.md](../history/documentation_index_20260719030341.md)
- Review対象: [implementer_status_phase_1c_deployment_platform_acceleration_follow_up_20260719025250.md](../history/handoffs/implementer_status_phase_1c_deployment_platform_acceleration_follow_up_20260719025250.md)
- Initial Status: [implementer_status_phase_1c_deployment_platform_acceleration_20260719021411.md](../history/handoffs/implementer_status_phase_1c_deployment_platform_acceleration_20260719021411.md)
- Requirements: [phase_1c_deployment_platform_acceleration_requirements_20260719013109.md](../history/requirements/phase_1c_deployment_platform_acceleration_requirements_20260719013109.md)
- Architecture: [phase_1c_deployment_platform_acceleration_architecture_20260719013109.md](../history/architecture/phase_1c_deployment_platform_acceleration_architecture_20260719013109.md)
- Accepted ADR: [adr_0007_deployment_platform_acceleration_abstraction_20260719013109.md](../history/adr/adr_0007_deployment_platform_acceleration_abstraction_20260719013109.md)
- supersedes: なし（Phase 1-C Designer Review系列の初回文書）

## 1. Review Conclusion

Phase 1-C Follow-upで行われたRequired／Detected／Executed境界の修正を受理する。

Model Load直後の状態をRequest単位の`Executed State`として先取りする問題は解消された。

```text
Required State : Deployment Profileが保持
Detected State : Model Load後にBackend Adapterが観測
Executed State : Request単位の実行証拠が存在する場合だけ保持
```

Current Load Observationの正しい状態：

```text
detected.device_kind_key       : gpu
detected.acceleration_api_key  : metal
detected.gpu_offload           : true
executed                       : null
```

一方、前回の設計者Reviewで指摘した次の2件は未対応である。

1. 将来OS／Architecture追加時の拡張性
2. Profile Host不一致のLoad前拒否

したがって、今回のFollow-up修正は部分受入とし、Phase 1-C全体の最終受入は保留する。

```text
Executed State意味境界修正       : Accepted
Static／Default Regression       : Pass
実Model／Metal Regression         : Pass
将来OS／Architecture拡張性       : Changes Required
Host Pre-load Validation         : Changes Required
Phase 1-C Final Acceptance       : Pending
```

## 2. Review Scope

次を読取専用で確認した。

- 最新の実装担当Follow-up Status
- Phase 1-C Requirements／Architecture／ADR／Handoff
- Runtime Contract
- Profile Resolver
- Phase 1 Application Bootstrap
- Unit／CLI／Integration Test
- Static／Default／Environment Gate
- uv Offline Dry-run
- Native Metal Model Smoke
- CLI `model-info`
- Production Acceptance

Source、Config、Test、Scriptまたは既存Docsの変更は行っていない。

本Reviewと同一TimestampのDocumentation Indexだけを、ユーザーの既存許可に基づきAppend-Onlyで新規作成した。

## 3. Accepted Follow-up: Required／Detected／Executed境界

### 3.1 Contract

確認した変更：

- `DetectedRuntimeState`へ`gpu_offload`を追加
- `RuntimeObservation.executed`をOptional化
- `ExecutedRuntimeState`をRequest単位のEvidence用Contractとして維持
- Load Observation Builderで`executed=None`を設定

`ExecutedRuntimeState`の説明も、1件のInference Requestに対する実行証拠であることを明示している。

### 3.2 Deployment Validation

Load後のDeployment Ready判定は、Request未実行の`Executed State`ではなく`Detected State`を使用する。

比較対象：

```text
Backend Key／Version
Compute Kind
Acceleration API
Required Device Kind
Required Acceleration API
Required Capability
```

Request実行前の状態を実行事実として扱わないため、ARGD／DAGD、Auditおよび将来Telemetryへ誤った事実が伝播するRiskは解消された。

### 3.3 CLI／実Model

Native Metal環境で`model-info`を実行し、次を独立確認した。

```text
profile_resolution_source         : platform_default
verification_state                : native_verified
detected backend                  : llama_cpp 0.3.34
detected device                   : gpu
detected acceleration             : metal
detected gpu_offload              : true
executed                          : null
artifact_digest_verified          : true
```

Production Acceptanceでも、Generation、Streaming CancelおよびPost-cancel Generationの後に、Application Load Observationの`executed`は`null`を維持した。

これはRequest Telemetry未実装という現在の事実と一致する。

## 4. Required Follow-up 1: 将来OS／Architecture追加時の拡張性

### 4.1 Finding

`normalize_operating_system()`と`normalize_architecture()`は、Source Code内の固定Mappingである。

Current OS Mapping：

```text
darwin  → macos
windows → windows
linux   → linux
```

Current Architecture Mapping：

```text
arm64／aarch64 → arm64
amd64／x86_64 → x86_64
```

未知のOSまたはArchitectureでは、明示ProfileまたはEnvironment Profileが指定されていても、Profile選択前のHost Detectionで`unsupported_platform`となる。

また、Platform Defaultは`phase1_application.py`内で次の1件だけがSource Codeとして登録されている。

```text
macos／arm64 → local_macos_arm64.toml
```

### 4.2 Requirementとの関係

Phase 1-C Acceptance Criteria 6：

> 将来のOS／Vendor／Acceleration Key追加にCore変更を必須としない

VendorおよびAcceleration APIは拡張可能なString Keyとして成立している。

しかし、OS／Architectureの新規追加は現在もProfileまたはRegistry追加だけでは成立せず、NormalizerおよびDefault CompositionのSource変更を必要とする。

### 4.3 Required Direction

次の意味境界を維持しながら修正する。

- 未知PlatformをmacOSとして推測しない
- Default Profileが存在しない場合はFail-Closedとする
- Explicit／Environment／Platform DefaultのPriorityを維持する
- 正規化AliasとPlatform Default対応をConfig、Definitionまたは差し替え可能Registryへ分離する
- Application CoreへOS別条件分岐を増殖させない

実装方法は実装担当が現在の責務境界内で選択してよい。

## 5. Required Follow-up 2: Host不一致のLoad前拒否

### 5.1 Finding

Current Bootstrap Sequence：

```text
Profile Resolution
  ↓
Profile Load
  ↓
Model Definition Load
  ↓
Artifact SHA-512 Verification
  ↓
Native Model Load
  ↓
Host Profile Validation
```

検出済みHostとProfile HostはNative Model Load前に比較可能だが、現在はModel Load後の`validate_loaded_deployment()`で比較している。

Profile不一致時にも約2.5GBのArtifact検証とNative Backend初期化を行った後で拒否する構造である。

将来、Windows／Linux／CUDA／ROCm等のProfileを追加した場合、非互換なNative Buildまたは不要な高負荷処理を先に開始する可能性がある。

### 5.2 Required Direction

Validationを最低限、次の二段階へ分離する。

```text
Pre-load Validation
  Host OS
  Architecture
  Execution Environment
  Fallback Policyの実装可否
  ProfileとModel DefinitionのBackend整合

Post-load Validation
  Detected Backend／Version
  Detected Device Kind
  Detected Acceleration API
  Required Capability
```

Host不一致時はArtifact HashまたはNative Model Loadへ進まず、Safe ErrorでFail-Closedとする。

## 6. Verification Evidence

### 6.1 Static／Default／Environment

設計者Taskによる独立再検証：

```text
Ruff Format Check          : Pass／51 files
Ruff Check                 : Pass
mypy --strict              : Pass／51 source files
Default pytest             : Pass／67 passed, 2 deselected
bash -n Setup Recipe       : Pass
Environment Verification  : Pass
Python                     : CPython 3.13.14／arm64
llama-cpp-python           : 0.3.34
GPU Offload Support        : true
Metal System Info          : present
Dependency Version Match   : true
Out-of-scope Package       : absent
```

実装担当Statusの`mypy --strict : Pass／47 source files`は、設計者再実測の`51 source files`と一致しない。

検査結果自体はPassであり、Source不具合ではなくStatus上の軽微な件数誤記として扱う。

### 6.2 uv Dependency Gate

`uv lock --check`はPassした。

Offline Dry-runは、Setup Recipeと同じ完全なOptionを指定して確認した。

```text
uv sync --dry-run --frozen --offline \
  --extra inference-llama \
  --group dev \
  --group notebook \
  --no-binary-package llama-cpp-python
```

結果：

```text
Checked 115 packages
Would make no changes
```

実装担当Statusの`uv sync offline dry-run`という省略表記では、必要なExtra／Groupが読み手へ伝わらない。

次回Statusでは完全なCommandまたはSetup Recipeと同一Optionであることを明記する。

### 6.3 Native Metal Gate

Codex Sandbox内ではMetal Deviceを取得できないため、Native Metal GateをSandbox外で実行した。

```text
pytest -q -m model_smoke
  2 passed, 67 deselected
```

Production Acceptance：

```text
Success                         : true
Load including SHA-512          : 2.4746 seconds
Generation Result               : フェーズ1-B生産ランタイム成功
Generation Speed                : 30.22 tokens／second
Explicit Stream Terminal State  : cancelled
Post-cancel Generation          : OK／stop
Unload                          : 0.0436 seconds
Detected Device                 : gpu／metal
Detected GPU Offload            : true
Executed State                  : null
```

## 7. Acceptance Criteria判定

| # | Acceptance Criteria | 判定 | 備考 |
|---:|---|---|---|
| 1 | Model DefinitionからDeployment固有のGPU必須を分離 | Pass | Model Optional、Mac Deployment Required |
| 2 | Mac Metal ProfileがGPU Offloadを要求 | Pass | `gpu_offload`、GPU、Metalを明示 |
| 3 | RequiredとDetected Capabilityを比較 | Pass | Detected Stateで検証 |
| 4 | 未対応Platformを暗黙にmacOS扱いしない | Pass | UnknownはFail-Closed |
| 5 | Profile ResolverがTest可能 | Pass | Unit Testあり |
| 6 | 将来OS／Vendor／Acceleration Key追加にCore変更を必須としない | Changes Required | Vendor／AccelerationはPass、OS／Architectureは固定Mapping |
| 7 | Tracked Configへユーザー固有絶対Pathを入れない | Pass | 相対Model Rootを維持 |
| 8 | Default／Static／Metal GateがPass | Pass | 独立再検証済み |
| 9 | macOS以外を`native_verified`と誤記しない | Pass | Mac／Metalのみ |
| 10 | Phase 2以降へ越境しない | Pass | Telemetry等はDeferred |

Acceptance Criteria 6が未達であり、Host Pre-load Validationにも将来Platform接続前の修正が必要である。

## 8. 次回Follow-up Acceptance条件

実装担当は次を完了し、新TimestampのStatusを作成する。

1. OS／Architecture AliasまたはNormalizationの差し替え境界を実装する
2. Platform Default対応をSource固定から拡張可能なDefinition／Registry境界へ移す、または同等の拡張性を証明する
3. Unknown PlatformのFail-Closedを維持する
4. Explicit／Environment／Platform Default Priorityを維持する
5. Host／FallbackのPre-load Validationを追加する
6. Host不一致時にModel Portの`load()`が呼ばれないTestを追加する
7. Current Mac／Metal Regressionを通す
8. `mypy`対象件数とuv Offline Dry-runの完全なCommandをStatusへ正確に記録する

## 9. Scope／Authorization Boundary

本Reviewは、Phase 1-CのFollow-up修正要求と受入条件を示す。

Source、Config、Test、ScriptまたはDependencyの変更を自動的に許可するものではない。

実装担当による追加修正は、ユーザーから明示的な実装許可と書込範囲が与えられた後に行う。

Request単位のExecution Telemetry、Windows／Linux実Profile、CUDA／ROCm／Vulkan Backend、Response Language／Thinking PresentationおよびPhase 2機能は、引き続き本Follow-upのScope外とする。


<!-- SOURCE_END 40: docs/handoffs/designer_review_phase_1c_deployment_platform_acceleration_follow_up_20260719030341.md -->

---

<!-- SOURCE_BEGIN 41: docs/handoffs/designer_review_phase_1c_final_20260719035156.md -->

### Source 41: `docs/handoffs/designer_review_phase_1c_final_20260719035156.md`

- History Target: `docs/project/phases/phase_1/history/handoffs/designer_review_phase_1c_final_20260719035156.md`
- Source SHA-512: `fede9d73730c2908aa7a0e6e275d9517aadeadfc4ee5b0fa1ef474e34af5a8ad657e515f12c49900895ad479103d7c275e5494721ea7f65676a9fa8c63942a9f`
- Source Size: `11979` bytes

# Phase 1-C Deployment／Platform／Acceleration 最終設計レビュー

- 文書ID: `designer_review_phase_1c_final`
- 状態: `accepted_phase_1c_complete`
- 作成日時: `2026-07-19 03:51:56 JST`
- 更新日時: `2026-07-19 03:51:56 JST`
- 作成担当: 設計者役担当Task
- 対象: 実装者役担当Task
- 正本言語: 日本語
- Documentation Index: [documentation_index_20260719035156.md](../history/documentation_index_20260719035156.md)
- Review対象: [implementer_status_phase_1c_platform_registry_reference_integrity_follow_up_20260719034523.md](../history/handoffs/implementer_status_phase_1c_platform_registry_reference_integrity_follow_up_20260719034523.md)
- Previous Review: [designer_review_phase_1c_platform_registry_and_preload_validation_follow_up_20260719033038.md](../history/handoffs/designer_review_phase_1c_platform_registry_and_preload_validation_follow_up_20260719033038.md)
- Initial Phase 1-C Review: [designer_review_phase_1c_deployment_platform_acceleration_follow_up_20260719030341.md](../history/handoffs/designer_review_phase_1c_deployment_platform_acceleration_follow_up_20260719030341.md)
- Requirements: [phase_1c_deployment_platform_acceleration_requirements_20260719013109.md](../history/requirements/phase_1c_deployment_platform_acceleration_requirements_20260719013109.md)
- Architecture: [phase_1c_deployment_platform_acceleration_architecture_20260719013109.md](../history/architecture/phase_1c_deployment_platform_acceleration_architecture_20260719013109.md)
- Accepted ADR: [adr_0007_deployment_platform_acceleration_abstraction_20260719013109.md](../history/adr/adr_0007_deployment_platform_acceleration_abstraction_20260719013109.md)
- supersedes: `designer_review_phase_1c_platform_registry_and_preload_validation_follow_up_20260719033038.md`

## 1. Review Conclusion

Phase 1-C Deployment／Platform／Acceleration Abstraction Hookを最終受入し、完了と判定する。

前回までのRequired Follow-upはすべて完了した。

```text
Required／Detected／Executed意味境界        : Pass
Model Capability／Deployment Requirement分離: Pass
OS／Architecture Alias Registry            : Pass
Platform Default Registry                   : Pass
Platform Registry参照整合                   : Pass
Unknown Platform Fail-Closed                : Pass
Profile Resolution Priority                 : Pass
Host／Fallback／Backend Pre-load Validation : Pass
Detected Capability Post-load Validation    : Pass
Current Mac／Metal Regression               : Pass
```

重大、中程度または軽微な未解決不具合は、今回のReview Scopeでは確認されなかった。

Phase 1-CのDeployment Contract、Platform Registry、Profile Resolver、Pre-load／Post-load Validation、Runtime ObservationおよびCurrent macOS／Metal Runtimeは、次段階の基盤として利用できる。

本ReviewはPhase 1-C完了を示す。次Phaseの設計または実装を自動的に解禁するものではない。

## 2. Follow-up履歴

Phase 1-C実装後、設計者Reviewで次を段階的に確認・修正した。

### 2.1 Required／Detected／Executed境界

初期実装では、Model Load時のDevice観測値をRequest単位の`Executed State`として記録していた。

修正後：

```text
Required : Deployment Profileが保持
Detected : Model Load後にBackend Adapterが観測
Executed : Request単位の実行証拠がある場合のみ保持
```

Current Load Observation：

```text
detected.device_kind_key       : gpu
detected.acceleration_api_key  : metal
detected.gpu_offload           : true
executed                       : null
```

Request Telemetry未実装の状態で実行事実を推測しない境界が成立した。

### 2.2 Platform Registry／Pre-load Validation

OS／Architecture AliasとPlatform DefaultをSource Code内の固定MappingからTracked Registryへ移動した。

Host、Fallback PolicyおよびProfile／Model Backend整合をNative Adapter生成前に検証する。

Host不一致時：

```text
Native Adapter Constructor : 0回
Model Port load()          : 0回
Artifact SHA-512           : 未実行
Native Model Load          : 未実行
Error                      : unsupported_platform
```

Model Load後はDetected Backend／Device／Acceleration／Capabilityだけを検証する。

### 2.3 Platform Registry参照整合

Platform Registryへ次のValidationを追加した。

1. OS Alias集合が1件以上存在する
2. Architecture Alias集合が1件以上存在する
3. Default OS KeyがOS AliasのCanonical Key集合に存在する
4. Default Architecture KeyがArchitecture AliasのCanonical Key集合に存在する
5. Default Execution EnvironmentがRegistryの検出値と一致する

従来受理されていた次の到達不能参照は拒否される。

```text
macso／arm64／native
macos／arm65／native
macos／arm64／container
```

設定不備はLoader境界でSafeな`invalid_configuration`へ変換される。

## 3. Platform Registry最終確認

### 3.1 Current Tracked Definition

[platform_registry.toml](../../../../../config/platforms/platform_registry.toml)は次を保持する。

```text
darwin／macos → macos
windows       → windows
linux         → linux

arm64／aarch64 → arm64
amd64／x86_64 → x86_64

macos／arm64／native
  → config/profiles/local_macos_arm64.toml
```

Windows／Linux Aliasは定義されているが、Default ProfileまたはNative Verificationは追加していない。

### 3.2 Extensibility

新しいOS／Architecture AliasおよびPlatform Defaultは、Registry Definitionの追加で表現できる。

NormalizerまたはApplication CoreへOS別条件分岐を追加する必要はない。

Future Alias／DefaultをMemory上で追加するUnit TestがPassした。

### 3.3 Validation

確認した項目：

- TOML Syntax
- Unknown Field拒否
- Alias Raw Value正規化
- Canonical Key形式
- Alias集合非空
- Raw Alias重複拒否
- Default Host Key重複拒否
- Default Canonical参照整合
- Default Execution Environment参照整合
- Default Profile Pathの絶対Path／`..`拒否
- Loader Safe Error Mapping

ADR-0007の「形式Validation、必須Fieldおよび参照整合を厳格に行う」を満たす。

## 4. Profile Resolution／Validation最終確認

### 4.1 Resolution Priority

```text
Explicit Profile
  > MARGPA_PROFILE
  > Platform Registry Default
```

未知OS／ArchitectureをmacOSとして推測しない。

Known AliasでもDefault Profileが存在しない場合は`profile_required`となる。

### 4.2 Pre-load Validation

```text
Profile Host OS              vs Detected Host OS
Profile Architecture         vs Detected Architecture
Profile Execution Environment vs Detected Execution Environment
Fallback Policy              vs Implemented Policy
Profile Backend／Version     vs Model Definition Backend／Version
```

不一致時はNative Adapterを生成せず、Safe ErrorでFail-Closedとする。

### 4.3 Post-load Validation

```text
Detected Backend／Version
Detected Device Kind
Detected Acceleration API
Required Device Kind
Required Acceleration API
Required Capability
```

Capability不足時はRuntimeをUnloadし、Lifecycleを回復する。

## 5. Independent Verification Evidence

### 5.1 Static／Default／Environment

```text
Ruff Format Check          : Pass／51 files
Ruff Check                 : Pass
mypy --strict              : Pass／51 source files
Default pytest             : Pass／77 passed, 2 deselected
bash -n Setup Recipe       : Pass
Environment Verification  : Pass
Python                     : CPython 3.13.14／arm64
llama-cpp-python           : 0.3.34
GPU Offload Support        : true
Metal System Info          : present
Dependency Version Match   : true
Out-of-scope Package       : absent
```

### 5.2 Reference Integrity Reproduction

設計者Taskで、OS=`macso`、Architecture=`arm65`、Execution Environment=`container`の到達不能Defaultを持つRegistry Objectを再構築した。

修正前はValidationが成功したが、修正後はPydantic `ValidationError`で拒否された。

```text
validation_rejected
default profile references an unknown operating system key
```

OS、Architecture、Execution Environmentの個別Negative Testと、File Loader Safe Error TestもPassした。

### 5.3 Dependency Gate

```text
uv lock --check
  Resolved 117 packages

uv sync --dry-run --frozen --offline \
  --extra inference-llama \
  --group dev \
  --group notebook \
  --no-binary-package llama-cpp-python

  Checked 115 packages
  Would make no changes
```

### 5.4 Native Metal Gate

Sandbox外のNative Metal環境で実行した。

```text
pytest -q -m model_smoke
  2 passed, 77 deselected
```

実CLI `model-info`：

```text
profile_resolution_source : platform_default
verification_state        : native_verified
backend                    : llama_cpp 0.3.34
device                     : gpu／metal
gpu_offload                : true
executed                   : null
artifact_digest_verified   : true
```

Platform Registry DefaultからCurrent Mac Profileを解決し、Model Load、Generation、Streaming、Cancel、Post-cancel GenerationおよびUnloadが成立した。

### 5.5 Hash

報告書記載値と独立計算値が一致した。

```text
Platform Registry SHA-512:
5af43fff30e5cf0716a927e05d1bde74a443e5a0484490a32398421824e3b4cc0539f64578dcc509fe620790686d7473587d7650665f2436b4c988281712d574

pyproject.toml SHA-256:
a46fcd0b61e8db84a5f90ac4459b92bf9ec9deb7d6219ce88d7b22c240b5ecfa

uv.lock SHA-256:
e5efe33d69105547fe0d4f348b6b189b85f7ed55323f8ecd993ef5df7846fee1
```

## 6. Acceptance Criteria最終判定

| # | Acceptance Criteria | 判定 | 備考 |
|---:|---|---|---|
| 1 | Model DefinitionからDeployment固有のGPU必須を分離 | Pass | Model Optional、Mac Deployment Required |
| 2 | Mac Metal ProfileがGPU Offloadを要求 | Pass | GPU／Metalを明示 |
| 3 | RequiredとDetected Capabilityを比較 | Pass | Post-load Validation |
| 4 | 未対応Platformを暗黙にmacOS扱いしない | Pass | Unknown AliasはFail-Closed |
| 5 | Profile ResolverがTest可能 | Pass | Unit／Negative Testあり |
| 6 | 将来OS／Vendor／Acceleration Key追加にCore変更を必須としない | Pass | Registry／String Key境界が成立 |
| 7 | Tracked Configへユーザー固有絶対Pathを入れない | Pass | 相対Pathを維持 |
| 8 | Default／Static／Metal GateがPass | Pass | 独立再検証済み |
| 9 | macOS以外を`native_verified`と誤記しない | Pass | Mac／Metalのみ |
| 10 | Phase 2以降へ越境しない | Pass | Scope外機能は未実装 |

全Acceptance CriteriaがPassした。

## 7. Deferred／Non-blocking Items

次はPhase 1-C最終受入を妨げない後続事項である。

- Windows／Linux実Profile
- CUDA／ROCm／Vulkan／MLX／Remote Backend
- 複数Execution Environment Alias／Detector
- Request単位のExecution Telemetry／Audit
- Runtime Device Name／IDの追加観測
- llama.cpp Build VariantのNative APIによる直接観測
- Logical Model／Artifact Variantの全面分離
- Response Language／Thinking Presentation
- Phase 2以降の機能

これらを実装・検証済みとは主張しない。

## 8. Phase 1-C完了状態

```text
Phase 1-A Environment                         : Complete／Accepted
Phase 1-B Model Runtime                       : Complete／Accepted
Phase 1-C Deployment／Platform／Acceleration  : Complete／Accepted
Current Native Verification                  : macOS／Apple Silicon arm64／Metal
```

Phase 1-C完了により、将来Deploymentの追加時に利用する最小Contract、Registry、Resolver、ValidationおよびObservation境界が成立した。

## 9. Scope／Authorization Boundary

本ReviewはPhase 1-Cの最終受入と完了を示す。

次PhaseのRequirements作成、設計、Source実装、Config変更またはDependency追加を自動的に許可するものではない。

次の作業は、ユーザーが議題と実施範囲を決定した後に開始する。


<!-- SOURCE_END 41: docs/handoffs/designer_review_phase_1c_final_20260719035156.md -->

---

<!-- SOURCE_BEGIN 42: docs/handoffs/designer_review_phase_1c_platform_registry_and_preload_validation_follow_up_20260719033038.md -->

### Source 42: `docs/handoffs/designer_review_phase_1c_platform_registry_and_preload_validation_follow_up_20260719033038.md`

- History Target: `docs/project/phases/phase_1/history/handoffs/designer_review_phase_1c_platform_registry_and_preload_validation_follow_up_20260719033038.md`
- Source SHA-512: `b2200ab6f888aec748df92b0c46526f738584bf2f380761a4978678863ad6ff31ee8bca15276895ef8e8387c7794b8bcc3fcfa108408e40a140655e6dea873a8`
- Source Size: `14042` bytes

# Phase 1-C Platform Registry／Pre-load Validation Follow-up設計レビュー

- 文書ID: `designer_review_phase_1c_platform_registry_and_preload_validation_follow_up`
- 状態: `changes_requested_phase_1c_registry_reference_integrity`
- 作成日時: `2026-07-19 03:30:38 JST`
- 更新日時: `2026-07-19 03:30:38 JST`
- 作成担当: 設計者役担当Task
- 対象: 実装者役担当Task
- 正本言語: 日本語
- Documentation Index: [documentation_index_20260719033038.md](../history/documentation_index_20260719033038.md)
- Review対象: [implementer_status_phase_1c_platform_registry_and_preload_validation_follow_up_20260719031938.md](../history/handoffs/implementer_status_phase_1c_platform_registry_and_preload_validation_follow_up_20260719031938.md)
- Previous Review: [designer_review_phase_1c_deployment_platform_acceleration_follow_up_20260719030341.md](../history/handoffs/designer_review_phase_1c_deployment_platform_acceleration_follow_up_20260719030341.md)
- Requirements: [phase_1c_deployment_platform_acceleration_requirements_20260719013109.md](../history/requirements/phase_1c_deployment_platform_acceleration_requirements_20260719013109.md)
- Architecture: [phase_1c_deployment_platform_acceleration_architecture_20260719013109.md](../history/architecture/phase_1c_deployment_platform_acceleration_architecture_20260719013109.md)
- Accepted ADR: [adr_0007_deployment_platform_acceleration_abstraction_20260719013109.md](../history/adr/adr_0007_deployment_platform_acceleration_abstraction_20260719013109.md)
- supersedes: `designer_review_phase_1c_deployment_platform_acceleration_follow_up_20260719030341.md`

## 1. Review Conclusion

前回Reviewで要求した次の2件を受理する。

1. OS／Architecture AliasおよびPlatform DefaultのRegistry化
2. Host／Fallback／BackendのPre-load Validation

確認結果：

```text
Executed State意味境界              : Accepted／維持
OS／Architecture Alias拡張性       : Accepted
Platform Default拡張性              : Accepted
Unknown Platform Fail-Closed        : Accepted
Profile Resolution Priority         : Accepted
Host Pre-load Validation            : Accepted
Fallback Pre-load Validation        : Accepted
Backend Pre-load Validation         : Accepted
Host不一致時Adapter Constructor     : 0回
Host不一致時Model Port load()       : 0回
Static／Default／Metal Regression   : Pass
```

ただし、新しいPlatform Registryに参照整合上の未検出不備が1件ある。

`profile_defaults`が、Alias集合に存在しないCanonical OS／Architecture Keyまたは、Registryが検出する値と異なるExecution Environment Keyを参照しても、Registry Validationが成功する。

Current Mac Runtimeに影響する不具合ではなく、Unknown PlatformのFail-Closedも維持される。

一方、ADR-0007が要求する「Unknown Keyの形式と参照整合をValidationする」を満たしていないため、Phase 1-Cの最終受入はこの1件のFollow-up完了まで保留する。

```text
今回の主要Follow-up          : Accepted
新規重大不具合               : なし
Registry参照整合             : Changes Required
Phase 1-C Final Acceptance   : Pending
```

## 2. Review Scope

次を読取専用で確認した。

- 最新の実装担当Follow-up Status
- 前回Designer Review
- Phase 1-C Requirements／Architecture／ADR
- `config/platforms/platform_registry.toml`
- Platform Registry Contract／Loader／Resolver
- Pre-load／Post-load Validation
- Phase 1 Application Bootstrap
- Registry／Deployment Unit Test
- Static／Default／Environment Gate
- uv Lock／Offline Dry-run
- Native Metal Model Smoke
- CLI `model-info`
- Config／Lock Hash

Source、Config、Test、Scriptまたは既存Docsは変更していない。

本Reviewと同一TimestampのDocumentation Indexだけを、既存のユーザー許可に基づきAppend-Onlyで新規作成した。

## 3. Accepted: Platform Registry境界

### 3.1 Source Code外へ移動した情報

[platform_registry.toml](../../../../../config/platforms/platform_registry.toml)が次を保持する。

```text
OS Raw Alias             → Canonical OS Key
Architecture Raw Alias   → Canonical Architecture Key
Execution Environment Key
Host Key                 → Default Profile Path
```

Current Definition：

```text
darwin／macos → macos
windows       → windows
linux         → linux

arm64／aarch64 → arm64
amd64／x86_64 → x86_64

macos／arm64／native
  → config/profiles/local_macos_arm64.toml
```

OS／Architecture AliasおよびDefault Profile追加時に、NormalizerまたはApplication CoreへOS別条件分岐を追加する必要はなくなった。

### 3.2 拡張性Test

Source Mappingを変更せず、Memory上で次を追加するTestを確認した。

```text
FutureOS 2371   → futureos
FutureArch 2371 → futurearch
futureos／futurearch／native
  → config/profiles/future.toml
```

Profile ResolverはFuture AliasをCanonical Keyへ変換し、Registry Defaultを選択できる。

Acceptance Criteria 6のOS／Vendor／Acceleration Key拡張性は、参照整合Follow-upを除く構造面で成立した。

### 3.3 Resolution Priority／Fail-Closed

次のPriorityを維持している。

```text
Explicit Profile
  > MARGPA_PROFILE
  > Platform Registry Default
```

未登録OS／Architecture AliasをmacOSとして推測しない。

登録済みAliasでもDefault Profileが存在しない場合は`profile_required`となる。

## 4. Accepted: Pre-load／Post-load Validation分離

### 4.1 Pre-load Validation

Native Adapter Constructorより前に次を検証する。

```text
Profile Host OS              vs Detected Host OS
Profile Architecture         vs Detected Architecture
Profile Execution Environment vs Detected Execution Environment
Fallback Policy              vs Implemented Policy
Profile Backend／Version     vs Model Definition Backend／Version
```

Host不一致時のUnit Testで次を確認した。

```text
Native Adapter Constructor : 0回
Model Port load()          : 0回
Artifact SHA-512           : 未実行
Native Model Load          : 未実行
Error                      : unsupported_platform
```

前回の「不一致判定前に約2.5GB ModelをHash／Loadする」問題は解消された。

### 4.2 Post-load Validation

Model Load後はDetected Stateを使用し、次を検証する。

```text
Detected Backend／Version
Detected Device Kind
Detected Acceleration API
Required Device／Acceleration
Required Capability
```

Capability不足時のUnloadとLifecycle回復を維持している。

Request実行証拠がないLoad Observationでは`executed=null`を維持する。

## 5. Required Follow-up: Platform Registry参照整合

### 5.1 Finding

`PlatformRegistry.validate_unique_entries()`は次を検証する。

- OS Raw Aliasの重複
- Architecture Raw Aliasの重複
- Default Host Keyの重複
- Canonical Keyの形式
- Default Profile Pathの相対Path安全性

しかし、Default Hostが参照するCanonical Keyの存在を検証していない。

設計者Taskで次のRegistry Objectを構築した。

```text
Known OS Alias Canonical           : macos
Known Architecture Alias Canonical : arm64
Registry Execution Environment     : native

Default OS                         : macso
Default Architecture               : arm65
Default Execution Environment      : container
```

`macso`、`arm65`および`container`は現在のRegistry Detectionから到達不能だが、Validationは成功した。

### 5.2 Impact

- Default Keyの誤記をRegistry Load時に検出できない
- 存在しているDefault ProfileがRuntime上は到達不能になる
- 設定不備が`invalid_configuration`ではなく、後段の`profile_required`として現れる
- Registry DefinitionとHost Detectionの参照整合が保証されない
- ADR-0007のRisk Mitigationを満たさない

誤ったDefaultへ暗黙Fallbackする動作ではないため、安全側のFail-Closed性は維持される。

### 5.3 Required Validation

最低限、Registry Load時に次を検証する。

1. `operating_system_aliases`が1件以上存在する
2. `architecture_aliases`が1件以上存在する
3. 各Defaultの`operating_system_key`がOS AliasのCanonical Key集合に存在する
4. 各Defaultの`architecture_key`がArchitecture AliasのCanonical Key集合に存在する
5. 各Defaultの`execution_environment_key`が現在検出可能なExecution Environmentと一致する

Current Schemaが単一の`execution_environment_key`を持つ間は、Default側の値がRegistry値と一致することを検証する。

将来、Native／WSL／VM／Containerを同時選択する段階では、Execution Environment Alias／Detectorを複数定義可能なRegistryへ拡張する。

### 5.4 Required Test

次のNegative Testを追加する。

- OS Canonical参照不整合を拒否する
- Architecture Canonical参照不整合を拒否する
- Execution Environment参照不整合を拒否する
- OS Aliasが空のRegistryを拒否する
- Architecture Aliasが空のRegistryを拒否する
- File Loaderが不整合をSafeな`invalid_configuration`へ変換する

Current `platform_registry.toml`のParse、Future Alias Test、Unknown Platform Fail-ClosedおよびMac Default Regressionを維持する。

## 6. Independent Verification Evidence

### 6.1 Static／Default／Environment

```text
Ruff Format Check          : Pass／51 files
Ruff Check                 : Pass
mypy --strict              : Pass／51 source files
Default pytest             : Pass／71 passed, 2 deselected
bash -n Setup Recipe       : Pass
Environment Verification  : Pass
Python                     : CPython 3.13.14／arm64
llama-cpp-python           : 0.3.34
GPU Offload Support        : true
Metal System Info          : present
Dependency Version Match   : true
Out-of-scope Package       : absent
```

実装担当Statusの件数と一致した。

### 6.2 Dependency Gate

```text
uv lock --check
  Resolved 117 packages

uv sync --dry-run --frozen --offline \
  --extra inference-llama \
  --group dev \
  --group notebook \
  --no-binary-package llama-cpp-python

  Checked 115 packages
  Would make no changes
```

前回要求した完全なOption列が最新Statusへ記録されている。

### 6.3 Native Metal Gate

Sandbox外のNative Metal環境で実行した。

```text
pytest -q -m model_smoke
  2 passed, 71 deselected
```

実CLI `model-info`：

```text
profile_resolution_source : platform_default
verification_state        : native_verified
backend                    : llama_cpp 0.3.34
device                     : gpu／metal
gpu_offload                : true
executed                   : null
artifact_digest_verified   : true
```

Platform Registry DefaultからCurrent Mac Profileを解決し、Model Load、Metal ObservationおよびUnloadに成功した。

Model SmokeにはProduction RuntimeのGeneration、Streaming、Cancel、Post-cancel GenerationおよびUnloadが含まれる。

### 6.4 Hash

報告書記載値と独立計算値が一致した。

```text
Platform Registry SHA-512:
5af43fff30e5cf0716a927e05d1bde74a443e5a0484490a32398421824e3b4cc0539f64578dcc509fe620790686d7473587d7650665f2436b4c988281712d574

Model Definition SHA-512:
2a1d3951b56dba2514fd4c37161dbea8048e80efc1ac9a8672f4a7f1f5d2c6aa3e3aaace7216b522dd2c1627fb30d676a80d7a761881f039f2337983d510f4be

Local Mac Profile SHA-512:
a2ccc4525223c6c04c2d91114699d7d850bb8092829b3bdc3ce02698e94ee0c943af789c94b10a3332bf97f245950f263211bf9ed818c5f3ca4c451f57cfd77c

pyproject.toml SHA-256:
a46fcd0b61e8db84a5f90ac4459b92bf9ec9deb7d6219ce88d7b22c240b5ecfa

uv.lock SHA-256:
e5efe33d69105547fe0d4f348b6b189b85f7ed55323f8ecd993ef5df7846fee1
```

## 7. Acceptance Criteria判定

| # | Acceptance Criteria | 判定 | 備考 |
|---:|---|---|---|
| 1 | Model DefinitionからDeployment固有のGPU必須を分離 | Pass | Model Optional、Mac Deployment Required |
| 2 | Mac Metal ProfileがGPU Offloadを要求 | Pass | GPU／Metalを明示 |
| 3 | RequiredとDetected Capabilityを比較 | Pass | Post-load Validation |
| 4 | 未対応Platformを暗黙にmacOS扱いしない | Pass | Unknown AliasはFail-Closed |
| 5 | Profile ResolverがTest可能 | Pass | Unit Testあり |
| 6 | 将来OS／Vendor／Acceleration Key追加にCore変更を必須としない | Pass with Follow-up | Registry境界は成立、参照整合を追加する |
| 7 | Tracked Configへユーザー固有絶対Pathを入れない | Pass | 相対Pathを維持 |
| 8 | Default／Static／Metal GateがPass | Pass | 独立再検証済み |
| 9 | macOS以外を`native_verified`と誤記しない | Pass | Mac／Metalのみ |
| 10 | Phase 2以降へ越境しない | Pass | Windows Profile等は未実装 |

## 8. 次回Follow-up Acceptance条件

実装担当は次を完了し、新TimestampのStatusを作成する。

1. Platform RegistryのCanonical参照整合Validationを追加する
2. Alias集合の空を拒否する
3. Execution Environment参照整合を検証する
4. 不整合RegistryをSafeな`invalid_configuration`へ変換する
5. 必要なNegative Testを追加する
6. Current Registry／Future Alias／Unknown Platform／Pre-load Validation Testを維持する
7. Static／Default／Environment Gateを通す
8. Native Metal Regressionを通す

このFollow-upはPlatform Registry ContractとTestの局所修正であり、Windows／Linux Profileまたは追加Backend実装を要求しない。

## 9. Scope／Authorization Boundary

本Reviewは、Platform Registry参照整合のFollow-up修正要求と受入条件を示す。

Source、Config、Test、ScriptまたはDependencyの変更を自動的に許可するものではない。

実装担当による追加修正は、ユーザーから明示的な実装許可と書込範囲が与えられた後に行う。

Windows／Linux実Profile、CUDA／ROCm／Vulkan／MLX／Remote Backend、Request単位のExecution Telemetry、Response Language／Thinking PresentationおよびPhase 2機能は、引き続きScope外とする。


<!-- SOURCE_END 42: docs/handoffs/designer_review_phase_1c_platform_registry_and_preload_validation_follow_up_20260719033038.md -->

---

<!-- SOURCE_BEGIN 43: docs/handoffs/designer_review_phase_1d_final_20260719122035.md -->

### Source 43: `docs/handoffs/designer_review_phase_1d_final_20260719122035.md`

- History Target: `docs/project/phases/phase_1/history/handoffs/designer_review_phase_1d_final_20260719122035.md`
- Source SHA-512: `b34d7c9bfc6f57671c2c5d6d8926180d0e1a88e853a22de26d4d367ef0eaa3e70f2e40768325c0ab72d3e353a288e55bce62de5c9df61fc72bb037070bdaab71`
- Source Size: `14119` bytes

# Phase 1-D Configuration／Response Language 最終設計Review

- 文書ID: `designer_review_phase_1d_final`
- 状態: `accepted_phase_1d_complete`
- 作成日時: `2026-07-19 12:20:35 JST`
- 更新日時: `2026-07-19 12:20:35 JST`
- Snapshot: `20260719122035`
- 作成担当: 設計者役担当Task
- 対象: Phase 1-D実装の最終受入
- 正本言語: 日本語
- 実装報告: [implementer_status_phase_1d_configuration_and_response_language_20260719095111.md](../history/handoffs/implementer_status_phase_1d_configuration_and_response_language_20260719095111.md)
- 実装Handoff: [designer_handoff_phase_1d_response_language_20260719041847.md](../history/handoffs/designer_handoff_phase_1d_response_language_20260719041847.md)
- 最新Roadmap: [implementation_roadmap_20260719122035.md](../history/architecture/implementation_roadmap_20260719122035.md)
- 最新Index: [documentation_index_20260719122035.md](../history/documentation_index_20260719122035.md)
- supersedes: なし（Phase 1-D最終Reviewの新規系列）

## 1. 最終結論

Phase 1-Dを受け入れ、`Complete／Accepted`と判定する。

```text
Blocking Finding          : 0
High Finding              : 0
Medium Finding            : 0
Required Follow-up        : 0
Acceptance Criteria       : 16／16 Pass
Static／Default Gate      : Pass
Dependency／Offline Gate : Pass
Native Metal Gate         : Pass
Final Decision            : Accepted
```

Phase 1-DのCompletion Boundaryである次が成立した。

- Application共通設定とDeployment／Hardware設定の分離
- Application Config Schema `1`
- Deployment Profile Schema `3`
- Typed Section Composition
- `ja／en／auto` Response Language Policy
- Application／Environment／Explicitの優先順位
- Backend非依存Message Composition
- CLI／Streaming／Non-streamingの共通経路
- Mac／Apple Silicon／Metalの非Regression

## 2. Review対象の正本

### Requirements

- [configuration_layer_requirements_20260719041847.md](../history/requirements/configuration_layer_requirements_20260719041847.md)
- [phase_1d_response_language_requirements_20260719041847.md](../history/requirements/phase_1d_response_language_requirements_20260719041847.md)

### Architecture

- [configuration_layer_architecture_20260719041847.md](../history/architecture/configuration_layer_architecture_20260719041847.md)
- [phase_1d_response_language_architecture_20260719041847.md](../history/architecture/phase_1d_response_language_architecture_20260719041847.md)

### ADR／Handoff

- [adr_0008_response_language_policy_20260719040237.md](../history/adr/adr_0008_response_language_policy_20260719040237.md)
- [adr_0009_application_deployment_configuration_separation_20260719041847.md](../history/adr/adr_0009_application_deployment_configuration_separation_20260719041847.md)
- [designer_handoff_phase_1d_response_language_20260719041847.md](../history/handoffs/designer_handoff_phase_1d_response_language_20260719041847.md)

### Implementer Status

- [implementer_status_phase_1d_configuration_and_response_language_20260719095111.md](../history/handoffs/implementer_status_phase_1d_configuration_and_response_language_20260719095111.md)

## 3. Review対象File

### Configuration

```text
config/application.toml
config/profiles/local_macos_arm64.toml
config/models/qwen3_4b_q4_k_m.toml
config/platforms/platform_registry.toml
```

### Source

```text
src/margpa_runtime_llm/bootstrap/config_loader.py
src/margpa_runtime_llm/bootstrap/phase1_application.py
src/margpa_runtime_llm/modules/inference/contracts/response.py
src/margpa_runtime_llm/modules/inference/public.py
src/margpa_runtime_llm/orchestration/response_language.py
src/margpa_runtime_llm/entrypoints/cli/main.py
```

### Test／Acceptance

```text
tests/unit/inference/test_config_and_registry.py
tests/unit/inference/test_deployment_platform.py
tests/unit/inference/test_response_language.py
tests/unit/inference/test_cli.py
tests/integration/llama_cpp/test_phase1b_runtime.py
scripts/models/phase1b_runtime_acceptance.py
```

## 4. Findings

### 4.1 Blocking／High／Medium

該当なし。

Source変更を求める不具合、設計逸脱、Regression、安全境界違反は発見されなかった。

### 4.2 Inline Code Comment

修正必須のInline Findingはない。

## 5. Configuration責務分離Review

### 5.1 Application Config

`config/application.toml`が次を所有することを確認した。

- `application_key`
- `selected_model`
- `model_root`
- Common `load_defaults`
- `generation`
- `response.language`

Tracked DefaultはUser固有Absolute Pathを持たず、`model_root.default = "./models"`を使う。Application Config内のAbsolute Pathおよび`..`をValidatorが拒否する。

### 5.2 Deployment Profile

`config/profiles/local_macos_arm64.toml`がSchema `3`へMigrationされ、次のPlatform／Hardware責務のみを持つことを確認した。

- Host
- Compute
- Backend Runtime
- Runtime Requirements
- Verification State
- Hardware-dependent `load_overrides`

Raw TOMLに次が残っていない。

```text
selected_model
model_root
generation
response
load
```

### 5.3 Model／Platform責務の不変

- Model DefinitionはArtifact／Hash／Model Capability／Native Context Limitを維持する。
- Platform RegistryはAlias／Default Profile Referenceだけを維持する。
- Model DefinitionとPlatform RegistryのDigestがPhase 1-C最終時点から不変である。

## 6. Typed Composition Review

`resolve_effective_config`は次のTyped Sectionを個別に解決する。

```text
Model／Root
Load
Generation
Response
Profile
```

Generic Recursive Dictionary Mergeは導入されていない。

### 6.1 Precedence

| 領域 | 確認した順位 |
|---|---|
| Model／Root | Explicit > Environment > Application |
| Load | Explicit > Environment > Deployment > Application > Built-in |
| Generation | Explicit > Environment > Application > Built-in |
| Response | Explicit > Environment > Application > Built-in |
| Profile | Explicit > Environment > Platform Default |

Pydantic Contractの`extra="forbid"`により、未知Field、所有権違反、旧Schema `2`を拒否する。

### 6.2 Pre-load Validation

Applicationの実効`context_size`がModel Native Limitを超える場合、`LlamaCppModelAdapter`のConstructionより前に`invalid_configuration`として拒否することをSourceとTestで確認した。

## 7. Response Language Review

### 7.1 Contract

```text
ResponseLanguage       : ja／en／auto
ResponseLanguageSource : built_in_default／application／environment／explicit
ResponsePolicyConfig
ResolvedResponseLanguagePolicy
```

Unknown Value、`jp`、不正なEnvironment ValueをAlias推測せず拒否する。

### 7.2 Message Composer

`margpa_runtime_llm.orchestration.response_language`にBackend非依存のResolver／Composerが置かれている。

- `ja`: 日本語Default Instruction
- `en`: 英語Default Instruction
- `auto`: Language Instructionなし
- User Prompt: Byte-for-byte保持
- User System Message: 破棄せず決定論的に結合
- Streaming／Non-streaming: 同一Composer経路

### 7.3 Adapter Boundary

`src/margpa_runtime_llm/adapters/`およびModel Portに、Response Languageの値、文言、分岐は存在しない。Language PolicyはApplication／Orchestration責務に留まっている。

## 8. Phase 1-E Scope Boundary

次のPhase 1-E対象は実装されていない。

- `<think>` Parser
- Thinking表示／非表示
- User-defined Thinking Label
- Streaming Thinking Filter
- Raw／Display Output分離
- Raw Thinking保存Policy
- Thinking Sampling Profile

Phase 1-Bから存在する`thinking_mode`と、Test／AcceptanceのThinking Tag非出現確認のみである。Phase 1-Eの責務混入とは判定しない。

## 9. Acceptance Criteria

| # | Criteria | Result | Evidence |
|---:|---|---|---|
| 1 | `config/application.toml`が共通正本 | Pass | Tracked Config／Loader／Unit Test |
| 2 | Application Schema `1` Strict Validation | Pass | Literal Schema／Unknown Field／Unsafe Root Test |
| 3 | Deployment Schema `3` Strict Validation | Pass | Literal Schema／Unknown Field／Old Schema Test |
| 4 | Platform Profileから共通Field除去 | Pass | Raw TOML Ownership Test |
| 5 | Typed ComposerがEffective Config生成 | Pass | Section別Resolver／Migration Test |
| 6 | PlatformがGeneration／ResponseをOverride不可 | Pass | Profile Contract `extra=forbid` |
| 7 | `ja／en／auto`が機能 | Pass | Unit／CLI／Native Metal |
| 8 | Default `ja` | Pass | Application Config／Resolver／Real CLI |
| 9 | Environment／CLI Override | Pass | Precedence Test／CLI Test |
| 10 | Effective Language Sourceを確認可 | Pass | `model-info`／Real Runtime JSON |
| 11 | ComposerがAdapter非依存 | Pass | Orchestration配置／Adapter検索 |
| 12 | User Prompt／System Message保持 | Pass | 6 Composition Exact Test |
| 13 | Phase 1-E機能混入なし | Pass | Source Search／Scope Review |
| 14 | 新規External Dependencyなし | Pass | `pyproject.toml`／`uv.lock`不変 |
| 15 | Static／Default Test Pass | Pass | Independent Gate |
| 16 | Mac／Metal Runtime非Regression | Pass | 2 Native Smoke + Production Acceptance |

## 10. 独立検証結果

### 10.1 Static／Default

```text
ruff format --check . : Pass／54 files already formatted
ruff check .          : Pass
mypy                  : Pass／54 source files
compileall            : Pass
bash -n Setup Recipe  : Pass
pytest -q             : Pass／94 passed, 2 deselected
```

### 10.2 Environment／Dependency

```text
Python                         : CPython 3.13.14／arm64／GIL enabled
llama-cpp-python               : 0.3.34
GPU Offload Support            : true
Metal System Info              : present
Dependency Versions Match      : true
Out-of-scope Packages Absent   : true
uv lock --check                : Pass／Resolved 117 packages
uv sync --dry-run --frozen ... : Pass／Checked 115／Would make no changes
```

Sandbox内のNative TestはMetal Contextを作成できず`Failed to create llama_context`となった。同一CommandをSandbox外のNative macOS環境で再実行し、次のとおりPassした。これはSandboxのGPU／Metal制約であり、Phase 1-D実装不具合とは判定しない。

### 10.3 Native Metal

```text
pytest -q -m model_smoke : 2 passed, 94 deselected

Default ja:
  Prompt : 「成功」とだけ答えてください。
  Result : 成功。

Explicit en:
  Prompt : Reply with the single word success.
  Result : success

auto:
  Prompt : OKとだけ答えてください。
  Result : OK
```

### 10.4 Real `model-info`

```text
application_key           : default
profile_key               : local.macos-arm64
selected_model            : main.qwen3-4b-q4-k-m
response.language         : ja
response.source           : application
profile_resolution_source : platform_default
verification_state        : native_verified
device                    : gpu／metal
gpu_offload               : true
executed                  : null
```

### 10.5 Production Runtime Acceptance

```text
success                         : true
load_seconds_including_sha512   : 2.4349
unload_seconds                  : 0.0660
generation_content              : フェーズ1-B生産ランタイム成功
generation_tokens_per_second    : 29.36
stream_terminal_state           : cancelled
post_cancel_content             : OK
post_cancel_finish_reason       : stop
artifact_digest_verified        : true
response                        : ja／application
thinking_tags_absent            : true
```

## 11. Hash照合

Implementer Statusの記録と独立計算が一致した。

```text
Application Config SHA-512:
1f38d7f0ed5ed1157cac76ad63f14fd57f0fa688448180c37c5c01abd6f046db27edaed25dfab8c72dca3324f9a1a930579efdcb503c74bc5ef60bbc20f1f83b

Mac Deployment Profile SHA-512:
861aa54e159285a5445df853b260b2465194a93bc2c254d3cfd9ec4b58c4fc6c1af0dd1ba7d80251a5e46f9c886fe2205d7931b346709002edb2e7d9f9ce2b40

Model Definition SHA-512:
2a1d3951b56dba2514fd4c37161dbea8048e80efc1ac9a8672f4a7f1f5d2c6aa3e3aaace7216b522dd2c1627fb30d676a80d7a761881f039f2337983d510f4be

Platform Registry SHA-512:
5af43fff30e5cf0716a927e05d1bde74a443e5a0484490a32398421824e3b4cc0539f64578dcc509fe620790686d7473587d7650665f2436b4c988281712d574

pyproject.toml SHA-256:
a46fcd0b61e8db84a5f90ac4459b92bf9ec9deb7d6219ce88d7b22c240b5ecfa

uv.lock SHA-256:
e5efe33d69105547fe0d4f348b6b189b85f7ed55323f8ecd993ef5df7846fee1
```

## 12. 非ブロッカー／設計どおりの延期項目

### 12.1 Response LanguageはDefault Policy

Phase 1-DはSystem InstructionによるDefault Language Policyであり、Output Language Classifier、Translation、Strict Enforcementではない。Modelが常に指定言語を守る保証はない。これはRequirementで明示された正常なScope境界である。

### 12.2 Source Trackingの粒度

Phase 1-Dは`applied_sources`、`profile_resolution_source`、`response.source`を提供する。全FieldのSource Mapは後続のTyped Config／Experiment／Auditで追加する。

### 12.3 Runtime Observation

Load時点の`runtime_observation.executed = null`と`build_variant_declared_not_observed`はPhase 1-CのAccepted境界を維持している。Phase 1-DのBlockerではない。

### 12.4 Setup RecipeのNative Rebuild

通常Setupで`--reinstall-package llama-cpp-python`を使うため、Native Packageを毎回Rebuildする点は既存の非ブロッカーである。将来、通常Syncと明示的Native Rebuildを分離可能である。

## 13. Status Transition

```text
Phase 1-D
  Designed／Accepted
    → Implementation Complete／Review Requested
    → Designer Review Accepted
    → Complete／Accepted
```

次のPhase状態：

```text
Phase 1-D : Complete／Accepted
Phase 1-E : Planned／Not Designed／Not Authorized
```

## 14. Authorization Boundary

本ReviewはPhase 1-Dを受け入れる。

次は自動的に解禁されない。

- Phase 1-EのSource／Config／Test実装
- `<think>` Parser／Filter／Label
- Phase 2以降の実装
- Dependency追加
- Model Download
- Lightning AI Studio外部操作

Phase 1-Eは次の設計対象として進められるが、実装には別途ユーザー許可が必要である。

<!-- SOURCE_END 43: docs/handoffs/designer_review_phase_1d_final_20260719122035.md -->

---

<!-- SOURCE_BEGIN 44: docs/handoffs/designer_review_phase_1e_final_20260719164641.md -->

### Source 44: `docs/handoffs/designer_review_phase_1e_final_20260719164641.md`

- History Target: `docs/project/phases/phase_1/history/handoffs/designer_review_phase_1e_final_20260719164641.md`
- Source SHA-512: `33955c2b0d14e35ac18dda2c83cb91d21cc1fe2816665b29b171e0324a2043c66b36fdf88a65f1917afa365bb76b8b5d4d500888b14898ae985c2a216f157151`
- Source Size: `15430` bytes

# Phase 1-E Thinking Presentation 最終設計Review

- 文書ID: `designer_review_phase_1e_final`
- 状態: `accepted_phase_1e_complete`
- 作成日時: `2026-07-19 16:46:41 JST`
- 更新日時: `2026-07-19 16:46:41 JST`
- Snapshot: `20260719164641`
- 作成担当: 設計者役担当Task
- 対象: Phase 1-E実装の最終受入
- 正本言語: 日本語
- 実装報告: [implementer_status_phase_1e_thinking_presentation_20260719134914.md](../history/handoffs/implementer_status_phase_1e_thinking_presentation_20260719134914.md)
- 実装Handoff: [designer_handoff_phase_1e_thinking_presentation_20260719130303.md](../history/handoffs/designer_handoff_phase_1e_thinking_presentation_20260719130303.md)
- 最新Roadmap: [implementation_roadmap_20260719164641.md](../history/architecture/implementation_roadmap_20260719164641.md)
- 最新共通Handoff: [common_project_handoff_20260719164641.md](../history/handoffs/common_project_handoff_20260719164641.md)
- 最新Index: [documentation_index_20260719164641.md](../history/documentation_index_20260719164641.md)
- supersedes: なし（Phase 1-E最終Reviewの新規系列）

## 1. 最終結論

Phase 1-Eを受け入れ、`Complete／Accepted`と判定する。

```text
Blocking Finding           : 0
High Finding               : 0
Medium Finding             : 0
Low Diagnostic Observation : 1
Required Follow-up         : 0
Acceptance Criteria        : 22／22 Pass
Static／Default Gate       : Pass
Dependency／Offline Gate  : Pass
Native Metal Gate          : Pass
Final Decision             : Accepted
```

Phase 1-EのCompletion Boundaryである次が成立した。

- Thinking Execution、Protocol Parsing、Presentation、Persistenceの4責務分離
- Application Config Schema `2`
- Model Definition Schema `2`
- Model Definitionの`parser_key`によるParser選択
- Plain Text／Tagged Thinking Parser
- Stateful Streaming Parser
- Hidden No-flash
- Default `高度推論`／Custom Display Label
- Raw Model Port Contractの維持
- Raw Reasoning永続保存なし
- Thinking FlagによるSampling暗黙変更なし
- Current Mac／Apple Silicon／Metalの非Regression

## 2. Review対象の正本

### Requirements

- [phase_1e_thinking_presentation_requirements_20260719130303.md](../history/requirements/phase_1e_thinking_presentation_requirements_20260719130303.md)

### Architecture

- [phase_1e_thinking_presentation_architecture_20260719130303.md](../history/architecture/phase_1e_thinking_presentation_architecture_20260719130303.md)

### ADR／Handoff

- [adr_0014_thinking_execution_presentation_and_persistence_separation_20260719130303.md](../history/adr/adr_0014_thinking_execution_presentation_and_persistence_separation_20260719130303.md)
- [designer_handoff_phase_1e_thinking_presentation_20260719130303.md](../history/handoffs/designer_handoff_phase_1e_thinking_presentation_20260719130303.md)

### Implementer Status

- [implementer_status_phase_1e_thinking_presentation_20260719134914.md](../history/handoffs/implementer_status_phase_1e_thinking_presentation_20260719134914.md)

## 3. Review対象File

### Configuration

```text
config/application.toml
config/models/qwen3_4b_q4_k_m.toml
config/profiles/local_macos_arm64.toml
config/platforms/platform_registry.toml
```

### Source

```text
src/margpa_runtime_llm/adapters/output_protocols/
src/margpa_runtime_llm/bootstrap/config_loader.py
src/margpa_runtime_llm/bootstrap/output_parser_registry.py
src/margpa_runtime_llm/bootstrap/phase1_application.py
src/margpa_runtime_llm/entrypoints/cli/main.py
src/margpa_runtime_llm/modules/inference/domain/model_definition.py
src/margpa_runtime_llm/modules/inference/public.py
src/margpa_runtime_llm/modules/presentation/
src/margpa_runtime_llm/orchestration/thinking_presentation.py
```

### Stable Boundary

```text
src/margpa_runtime_llm/modules/inference/ports/model_port.py
src/margpa_runtime_llm/adapters/model_backends/llama_cpp/adapter.py
src/margpa_runtime_llm/adapters/model_backends/llama_cpp/stream.py
```

### Tests

```text
tests/unit/presentation/test_thinking_presentation.py
tests/unit/inference/test_cli.py
tests/unit/inference/test_config_and_registry.py
tests/unit/inference/test_deployment_platform.py
tests/contract/model_port/test_model_port_contract.py
tests/integration/llama_cpp/test_phase1b_runtime.py
```

## 4. Findings

### 4.1 Blocking／High／Medium

該当なし。

Source変更を要求する設計逸脱、Regression、Raw境界破壊、Reasoning漏洩、Dependency増加は発見されなかった。

### 4.2 Low Diagnostic Observation

`resolve_thinking_presentation_policy`は、Environment由来のFieldが不正であっても、別FieldにExplicit Overrideが存在すると、最終Error Codeを`invalid_request`として分類する。

確認例：

```text
MARGPA_THINKING_VISIBILITY = sometimes   # 不正なEnvironment値
explicit_display_label     = 明示推論     # 正常な別Field
result error code          = invalid_request
```

原因は、Validation ErrorとなったFieldのSourceではなく、いずれかのExplicit Overrideが存在するかでError Codeを選んでいるためである。

影響：

- 不正値そのものは安全に拒否される
- Raw値やPathはErrorへ露出しない
- 正常値のPrecedence／Source Trackingに影響しない
- Phase 1-Eの受入条件には抵触しない
- UI／Config診断を精密化する段階で、Field別Error Attributionへ改善可能

したがって、Phase 1-Eを止めるFindingではなく、将来のConfiguration UX改善候補として記録する。必須Follow-upは発行しない。

### 4.3 Inline Code Comment

修正必須のInline Findingはない。

## 5. Configuration／Schema Review

### 5.1 Application Config

`config/application.toml`はSchema `2`へMigrationされ、次を所有する。

```toml
[generation]
thinking_mode = "disabled"

[presentation.thinking]
visibility = "hidden"
display_label = "高度推論"
persistence = "disabled"
```

`ApplicationConfig`は`schema_version: Literal["2"]`および`extra="forbid"`を用いる。旧Schema、未知Field、欠落したPresentation SectionをSilent Acceptanceしない。

### 5.2 Deployment Profile

Deployment ProfileはSchema `3`のまま不変であり、Presentation Fieldを追加できない。PresentationはPlatform固有設定へ混入していない。

### 5.3 Model Definition

Model DefinitionはSchema `2`へMigrationされ、Canonical Protocolを所有する。

```toml
[output_protocol.thinking]
parser_key = "tagged_thinking_v1"
opening_delimiter = "<think>"
closing_delimiter = "</think>"
```

Display LabelはModel Definitionへ入っていない。Plain Text ParserはDelimiterを拒否し、Tagged Parserは両Delimiter必須、同一値、空、制御文字を拒否する。

## 6. Four-way Separation Review

```text
Thinking Execution : GenerationParameters／ThinkingMode
Protocol Parsing   : Output Parser Port／Adapter／Registry
Presentation       : Presentation Policy／Renderer／Service
Persistence        : disabled-only Contract
```

`--show-thinking`はGenerationの`thinking_mode`を変更せず、`--thinking`はVisibilityを変更しない。TestとSourceの両方で独立性を確認した。

Persistenceは`ThinkingPersistence.DISABLED`のみを持ち、Environment／CLI Overrideを提供しない。Presentation Module内にFile、JSONL、Database Writerは存在しない。

## 7. Parser／Renderer Review

### 7.1 Parser Selection

ParserはModel Definitionの`parser_key`からComposition Rootで構築される。Model Key、Architecture、Backend名によるParser分岐はない。

Unknown Parserは`LlamaCppModelAdapter` ConstructionおよびModel Load前に`invalid_model_definition`として拒否される。

### 7.2 Stateful Parser

Tagged Parserは次のStateを持つ。

```text
detecting_prefix
inside_reasoning
after_reasoning
plain_text
```

確認した動作：

- Optional Leading Whitespace
- OpeningなしをOriginal Finalへ復元
- Opening／Closing DelimiterのChunk分割
- Minimum Suffix Buffer
- 1文字Chunk／Empty Delta
- Complete／Unclosed／Extra Delimiter
- Extra Delimiterの保持とWarning
- FinishのIdempotency

Non-streamingも同じStreaming SessionへRaw Contentを1回Feedしており、別Parser実装を持たない。

### 7.3 Hidden No-flash

Opening候補を判定中はOutputをBufferし、Reasoning SegmentはHidden Rendererで破棄する。Closing確定後のFinalだけを表示する。

Delimiterが複数Chunkへ分割されてもReasoningやCanonical Tagを先にstdoutへ出さないことをDeterministic Testで確認した。

### 7.4 Visible Rendering

RendererはCanonical Delimiterを知らず、Resolved Display Labelから表示Containerを作る。

```text
Default : <高度推論>...</高度推論>
Custom  : <思考過程>...</思考過程>
```

Unclosed Reasoningでは表示ContainerだけをTerminalで閉じる。Raw Model Outputを修復または上書きしない。

## 8. CLI／Observability Review

CLIは次を分離する。

```text
Execution     : --thinking／--no-thinking
Visibility    : --show-thinking／--hide-thinking
Display Label : --thinking-label
```

Visibility FlagはMutually Exclusiveである。Invalid LabelはRaw値を表示せず、安全なErrorとして拒否する。

`model-info`には次が含まれる。

- Application Schema Version
- Model Definition Schema Version
- Thinking Mode
- Visibility／Display Label／Persistence
- 各FieldのSource
- Parser Key／Canonical Delimiter Definition

JSONは`ensure_ascii=False`を維持し、日本語LabelをUnicode Escapeへ変換しない。

## 9. Stable Raw Boundary Review

`GenerationResult.content`と`GenerationChunk.text_delta`はRaw Model Outputのままであり、Presentation Serviceが後段で表示結果を生成する。

Model Port、llama.cpp Adapter、Stream Adapterには次が存在しない。

- Display Label
- Thinking Visibility
- Parser Key分岐
- Canonical Tag置換
- Presentation Policy

CLIにもCanonical `<think>`／`</think>`はハードコードされていない。

## 10. Acceptance Criteria

| # | Criteria | Result | Independent Evidence |
|---:|---|---|---|
| 1 | ExecutionとVisibilityが独立 | Pass | CLI Source／Unit Test |
| 2 | Persistenceが独立しdisabled固定 | Pass | Enum／Resolver／Override非実装 |
| 3 | Application Schema 2 Strict | Pass | Literal Schema／Old Schema／Unknown Field Test |
| 4 | Deployment Schema 3不変 | Pass | Config Hash／Ownership Test |
| 5 | Default disabled／hidden／高度推論／disabled | Pass | Config／Resolver／model-info Test |
| 6 | Visibility／Label Env・CLI Override | Pass | Precedence／CLI Test |
| 7 | Field別Source確認 | Pass | Contract／model-info Test |
| 8 | Canonical DelimiterとDisplay Label分離 | Pass | Model Definition／Renderer Source Search |
| 9 | Definition Parser Keyで選択 | Pass | Registry／Bootstrap Test |
| 10 | Model／Architecture／Backend Hardcodeなし | Pass | Source Search |
| 11 | Non-streaming正規化 | Pass | Plain／Complete／Malformed Test |
| 12 | Streaming Delimiter Split対応 | Pass | 全Single Split／1文字Chunk Test |
| 13 | Hidden Streaming No-flash | Pass | Deterministic No-flash Test |
| 14 | Visible Default／Custom Label | Pass | Unit／CLI Test／Native Raw Presentation |
| 15 | Malformed決定論処理／Warning | Pass | Unclosed／Extra Delimiter Test |
| 16 | Raw Result／Chunk不変 | Pass | Contract Test／Source Review |
| 17 | Finish／Usage／Cancel／Close保持 | Pass | Contract／CLI／Native Smoke |
| 18 | Raw Reasoning新規永続保存なし | Pass | Source Search／Writerなし |
| 19 | Thinking FlagでSampling非変更 | Pass | CLI Sampling Test |
| 20 | 新規External Dependencyなし | Pass | Dependency File Hash不変 |
| 21 | Static／Default Test Pass | Pass | Independent Gate |
| 22 | Current Mac／Metal非Regression | Pass | Independent Native Gate |

## 11. 独立検証結果

### 11.1 Static／Default

```text
ruff format --check . : Pass／68 files already formatted
ruff check .          : Pass
mypy                  : Pass／68 source files
compileall            : Pass／Temporary Pycache outside Project
bash -n Setup Recipe  : Pass
pytest -q             : Pass／161 passed, 2 deselected
```

### 11.2 Environment／Dependency

```text
Python                         : CPython 3.13.14／arm64／GIL enabled
llama-cpp-python               : 0.3.34
GPU Offload Support            : true
Metal System Info              : present
Dependency Versions Match      : true
Out-of-scope Packages Absent   : true
uv lock --check                : Pass／Resolved 117 packages
uv sync --dry-run --frozen ... : Pass／Checked 115／Would make no changes
```

`uv`の最初のSandbox内実行は、Project外の既存User Cacheを読めず`Operation not permitted`となった。既存Cacheへの読み取りを許可した同一CommandでPassしたため、実装またはLockの不具合とは判定しない。

### 11.3 Native Mac／Metal

```text
pytest -q -m model_smoke
  2 passed, 161 deselected
```

Native Testで確認したもの：

- Qwen3 GGUF Load／SHA-512 Verify
- Apple Silicon arm64／Metal／GPU Offload
- Application Schema `2`
- Model Definition Schema `2`
- Default Presentation Policy
- ja／en／auto Regression
- Thinking Raw OutputのHidden／Visible Presentation
- Canonical Tag非表示
- Stream Cancel／Close
- Cancel後のGeneration
- Unload

## 12. Hash／Dependency確認

```text
Application Config SHA-512:
928888197b39c066b3e0befc08ba490c166752eae76c9c07fad47f48367dc851759642b5f2243349a1ab7fdc8d85ffcabcc5e39e93c0fac536cfbb64e48434e5

Model Definition SHA-512:
e41866e73a1847abbf973f39b6b26038d30454277b1d9fb6a278b9f165af7de9e00695df79c48e3d5b9c53f84c6e6aba5cafee000ac895e0d643035cb2a171d2

Mac Deployment Profile SHA-512:
861aa54e159285a5445df853b260b2465194a93bc2c254d3cfd9ec4b58c4fc6c1af0dd1ba7d80251a5e46f9c886fe2205d7931b346709002edb2e7d9f9ce2b40

Platform Registry SHA-512:
5af43fff30e5cf0716a927e05d1bde74a443e5a0484490a32398421824e3b4cc0539f64578dcc509fe620790686d7473587d7650665f2436b4c988281712d574

pyproject.toml SHA-256:
a46fcd0b61e8db84a5f90ac4459b92bf9ec9deb7d6219ce88d7b22c240b5ecfa

uv.lock SHA-256:
e5efe33d69105547fe0d4f348b6b189b85f7ed55323f8ecd993ef5df7846fee1
```

Model Artifact DigestはNative Runtimeの`artifact_digest_verified = true`で確認した。

## 13. Phase 1全体の状態

Phase 1-AからPhase 1-Eまでの実装Subphaseは、すべて`Complete／Accepted`となった。

ただし、Top-Level Phase 1はまだ完了宣言しない。現在のUser ManualはPhase 1-A／1-Bのみを対象としており、Phase 1-C／1-D／1-Eの操作、Config、Response Language、Thinking Presentationを反映していない。

残るFinalization：

1. Phase 1 User ManualのAccepted後継版を作る。
2. Phase 1-A～1-Eの最終Cross-phase確認を行う。
3. 最新Review／Roadmap／Common Handoff／Indexの整合性を確認する。
4. 設計者役が「Phase 1は完了です。次はPhase 2です」と明示する。
5. 明示直後にPhase 1 Backupを取得・検証する。

したがって、本ReviewはPhase 1-Eの完了判定であり、Top-Level Phase 1の完了宣言ではない。

## 14. Authorization Boundary

本ReviewによりPhase 1-EをAcceptedとする。

本Reviewで実施していないもの：

- Source／Config／Testの修正
- User Manualの更新
- Top-Level Phase 1完了宣言
- Phase 1 Backup Archive／Manifest／Receipt生成
- Phase 2実装


<!-- SOURCE_END 44: docs/handoffs/designer_review_phase_1e_final_20260719164641.md -->

---

<!-- SOURCE_BEGIN 45: docs/handoffs/designer_review_phase_1f_lightning_cross_environment_runtime_20260720235113.md -->

### Source 45: `docs/handoffs/designer_review_phase_1f_lightning_cross_environment_runtime_20260720235113.md`

- History Target: `docs/project/phases/phase_1/history/handoffs/designer_review_phase_1f_lightning_cross_environment_runtime_20260720235113.md`
- Source SHA-512: `539bcf9287cbf014e4470d48a5abcd42ee9f6ddf9d4b809df98b42dcd82c859ebe80935ef0daf64cf7513377d63435632ddc8862d42ac00c26b5d04a0f82a020`
- Source Size: `14527` bytes

# Phase 1-F Lightning Cross-environment Runtime 設計Review

- 文書ID: `designer_review_phase_1f_lightning_cross_environment_runtime`
- 状態: `changes_requested_before_lightning_native_verification`
- 作成日時: `2026-07-20 23:51:13 JST`
- 更新日時: `2026-07-20 23:51:13 JST`
- Snapshot: `20260720235113`
- 作成担当: 設計者役担当Task
- 対象: Phase 1-F Repository実装とLightning Native Verification準備状態
- 正本言語: 日本語
- 実装報告: [implementer_status_phase_1f_lightning_cross_environment_runtime_20260719205819.md](../history/handoffs/implementer_status_phase_1f_lightning_cross_environment_runtime_20260719205819.md)
- 要件: [phase_1f_lightning_cross_environment_runtime_requirements_20260719202333.md](../history/requirements/phase_1f_lightning_cross_environment_runtime_requirements_20260719202333.md)
- ADR: [adr_0015_phase_1f_lightning_and_python_312_support_20260719202333.md](../history/adr/adr_0015_phase_1f_lightning_and_python_312_support_20260719202333.md)
- 実装Handoff: [implementer_handoff_phase_1f_lightning_cross_environment_runtime_20260719202333.md](../history/handoffs/implementer_handoff_phase_1f_lightning_cross_environment_runtime_20260719202333.md)
- 最新Index: [documentation_index_20260720235113.md](../history/documentation_index_20260720235113.md)
- supersedes: なし（Phase 1-F Review系列の初回）

## 1. Review結論

Phase 1-FのRepository実装は、Python Support Range、Platform／Profile分離、Container検出、CUDA／CPU Profile、Safe Failure、Setup Recipe、Mac Regressionの方向で要件に沿っている。

ただし、Lightningへ一度だけ搬入してMandatory Gateを実行する前に修正すべきFindingがあるため、現時点ではPhase 1-Fを受け入れない。

```text
Blocking Finding              : 0
High Finding                  : 2
Medium Finding                : 2
Low Observation               : 1
Repository Static Gate        : Pass
Mac Python 3.13／Metal Gate   : Pass
Python 3.12 Native Gate       : Not Run
Lightning CUDA Native Gate    : Not Run
Lightning CPU Candidate Gate  : Not Run
Final Decision                : Changes Requested
```

次の3点がLightning搬入前の必須Follow-upである。

1. CUDA Build対応／要求値と、実際のGPU Offload Evidenceを分離する。
2. Acceptance ProbeをFail Closedにし、主要Check不合格時は非0で終了させる。
3. Response Language／Thinking PresentationのNative Evidenceを実際の合否条件へ含める。

## 2. Review対象

### Configuration／Root

```text
pyproject.toml
uv.lock
config/platforms/platform_registry.toml
config/profiles/lightning_linux_x86_64_cuda.toml
config/profiles/lightning_linux_x86_64_cpu.toml
```

### Source

```text
src/margpa_runtime_llm/bootstrap/profile_resolver.py
src/margpa_runtime_llm/bootstrap/phase1_application.py
src/margpa_runtime_llm/modules/inference/contracts/runtime.py
src/margpa_runtime_llm/adapters/model_backends/llama_cpp/runtime_detection.py
src/margpa_runtime_llm/adapters/model_backends/llama_cpp/adapter.py
src/margpa_runtime_llm/entrypoints/cli/main.py
```

### Scripts

```text
scripts/setup/verify_phase1_environment.py
scripts/setup/setup_lightning_linux_x86_64_cuda.sh
scripts/models/phase1f_cross_environment_acceptance.py
```

### Tests

```text
tests/unit/inference/test_config_and_registry.py
tests/unit/inference/test_deployment_platform.py
tests/unit/inference/test_cli.py
tests/integration/llama_cpp/test_phase1b_runtime.py
tests/integration/llama_cpp/test_phase1f_cross_environment_runtime.py
```

## 3. Positive Findings

次は設計と実装の両方で成立している。

- `requires-python = ">=3.12,<3.14"`とPython 3.12基準のRuff／Mypy設定
- `.python-version = 3.13.14`によるMac Primary維持
- Platform Registry Schema 2と`native／container`分離
- Linux／x86_64／Container／UbuntuのPre-load照合
- Lightning CUDA／CPUのExplicit Profile
- CUDA Profileの`fallback_policy = deny`
- CPU Profileの`gpu_layers = 0`
- ProfileとLoaded Runtime不一致時のUnload／Safe Failure
- Mac Default Profileを維持し、Lightning Profileを暗黙選択しない構造
- Normal Dependency SyncとNative Package Rebuildの分離
- Existing CUDA Build再利用Hook
- CLI Helpの仮引数説明とOption配置説明
- Hidden ThinkingがToken上限へ達した場合のSafe Warning
- Mac 3.13.14／Metalの既存Runtime非Regression

## 4. Findings

### 4.1 High: `gpu_offload=true`が実GPU使用の観測値ではない

対象：

- `src/margpa_runtime_llm/adapters/model_backends/llama_cpp/runtime_detection.py`
- `src/margpa_runtime_llm/adapters/model_backends/llama_cpp/adapter.py`
- `src/margpa_runtime_llm/bootstrap/profile_resolver.py`
- `scripts/setup/verify_phase1_environment.py`

Current判定は次の組合せである。

```text
llama_print_system_info()にCUDA Markerがある
llama_supports_gpu_offload()がtrue
gpu_layersが0ではない
  ↓
device_kind=gpu
acceleration_api=cuda
gpu_offload=true
```

ここで観測しているのは、BackendがCUDA Buildであること、GPU Offload Capabilityを持つこと、ConfigがOffloadを要求していることまでである。実際にModel LayerがGPUへ配置されたこと、当該ProcessがGPU Memoryを使用したことは観測していない。

そのため、CUDA-enabled Buildが存在し`gpu_layers=-1`を指定しただけで、実行時のGPU Offload Evidenceがなくても`gpu_offload=true`と申告できる。これはPhase 1-F Mandatory Gateの「GPU未割当時にCPUへ黙ってFallbackしない」「GPU Offloadを観測する」と一致しない。

Required Follow-up：

- Build Capability、Configured Request、Loaded／Executed Observationを別FieldまたはSource付き状態として扱う。
- `gpu_offload=true`を実観測値として維持する場合、llama.cpp Native Load EvidenceまたはProcess単位GPU Memory Evidenceを取得する。
- 実観測できない場合は`requested／supported／unverified`として表現し、`observed=true`を偽装しない。
- Lightning CUDA Acceptanceで、Allocated GPUの存在だけでなくModel LoadによるGPU使用を証明する。

### 4.2 High: Acceptance ProbeがCheck不合格でも成功終了できる

対象：

- `scripts/models/phase1f_cross_environment_acceptance.py`
- `scripts/setup/setup_lightning_linux_x86_64_cuda.sh`
- `tests/integration/llama_cpp/test_phase1f_cross_environment_runtime.py`

Acceptance Scriptは例外が発生しなければ`"success": true`を出力してExit Code 0を返す。`checks`内のBoolean／Length／Parse Statusを合否へ集約していない。

したがって、次のような状態でもDirect Scriptは成功終了できる。

- Non-stream／Stream Outputが空
- Cancelが成立しない
- Post-cancel Generationが成立しない
- Thinkingが検出されない
- Hidden／Visible Presentationが要件を満たさない
- Response Language Contractが成立しない

Integration Testは一部FieldをAssertするが、Setup Scriptの`--cuda-smoke`／`--cpu-smoke`はIntegration TestではなくAcceptance Scriptを直接実行する。Mandatory CommandがExit 0でも主要Checkが不合格になり得る。

Required Follow-up：

- Acceptance Script自身が全必須Checkを評価する。
- `all_required_checks_passed`を構造化出力する。
- 1件でも必須Checkが不合格なら`success=false`かつ非0で終了する。
- Integration TestはScriptの全必須Checkと終了CodeをAssertする。
- Setup ScriptはそのFail Closed結果を受けて終了する。

### 4.3 Medium: Language／Thinking Native Evidenceが受入条件になっていない

Mac実機でCurrent Acceptance Probeを独立実行した結果：

```text
success                       : true
thinking_parse_status         : unclosed_reasoning
hidden_reasoning_not_displayed: true
visible_thinking_chars        : 557
```

`unclosed_reasoning`でもScriptは成功した。さらに、`hidden_reasoning_not_displayed`は`reasoning_content is None`でもtrueとなり、Thinkingを全く検出できない場合にも合格相当の値になり得る。`visible_thinking_chars`はReasoning部分ではなくDisplay全体の文字数である。

Response Languageも、日本語／英語結果の文字数だけを記録しており、Policy、Message Composition、最終回答Languageを合否へ含めていない。日本語Promptの期待値が`OK`であるため、出力自体から日本語応答を証明できない。

Required Follow-up：

- Thinking検出、Reasoning Segment、Final Segment、Hidden非表示、Visible Label表示を個別にAssertする。
- Thinking用Token上限を、短いPromptでFinal Segmentまで安定して生成できる値へ調整する。
- Unclosed Reasoningを安全処理Testとして残す場合、正常Thinking／Final Testとは分離する。
- Response LanguageはResolved PolicyとModelへ渡したSystem Messageを必須Evidenceとする。
- Native Output Languageも確認する場合、日本語と英語を区別可能な期待値を使用する。

### 4.4 Medium: LightningのVenv前提をTarget Environmentで未確認

対象：

- `scripts/setup/setup_lightning_linux_x86_64_cuda.sh`

Setup ScriptはProject Rootの`.venv`作成と`uv sync`を前提とする。一方、LightningのCurrent Official Documentationは、Studio内で追加Environment／Virtual Environmentを作成しない運用を案内している。

- [Lightning Environment persistence](https://lightning.ai/docs/overview/ai-studio/environment-persistence)

実際の対象Studioで`.venv`が利用可能ならCurrent Recipeを維持できるが、利用できない場合はSetup開始直後に停止する。Local Macの`.venv`を転送してはならない点はCurrent方針どおりである。

Required Follow-up：

- Source一式を大規模搬入する前に、対象StudioでProject-local Venv作成可否を確認する。
- 不可の場合、Studio Persistent Python EnvironmentへLock内容を導入する別Modeを設計する。
- どちらを採用しても、Mac Venv／Native PackageをLightningへ転送しない。

### 4.5 Low: `--cpu-only`でも`nvcc`を無条件要求する

対象：

- `scripts/setup/setup_lightning_linux_x86_64_cuda.sh`

Scriptは既存CUDA Buildを再利用できるか確認する前に、`--cpu-only`でも`nvcc`を要求する。GPU Instanceで作成済みCUDA Buildが永続化されていても、CPU Machine側でCUDA Toolkitが見えない場合は再利用判定へ進めない。

CPU Candidate AはBest EffortであるためCUDA Mandatory Gateを止めるFindingではない。ただし、GPU割当上限時のCPU確認を目的としているため、次のいずれかが望ましい。

- `nvcc`をNative Rebuildが必要な場合だけ要求する。
- CUDA Build再利用に必要なRuntime LibraryとImportを先に確認する。
- Candidate Aが不成立なら、そのFailure Evidenceを保存してDeadline-safe Alternativeへ戻す。

## 5. Independent Verification

### 5.1 Static／Default Gate

```text
ruff format --check .                    : Pass／70 files
ruff check .                             : Pass
mypy                                     : Pass／70 source files
python -m compileall -q src scripts tests: Pass
bash -n macOS／Lightning Setup           : Pass
pytest -q                                : Pass／181 passed、3 deselected
uv lock --check --offline                : Pass／117 packages
```

### 5.2 Mac Environment／Native Gate

```text
verify target          : macos-metal
Python                 : 3.13.14
Host                   : macOS／arm64／native
Backend Build Variant  : metal
Device                 : gpu／metal
Dependency Validation  : Pass
Model Smoke            : 2 passed、1 skipped
Cross-environment Probe: Exit 0
```

Sandbox内ではMetal Deviceが利用できずModel Context作成に失敗した。Sandbox外のMac実機Contextで同じModel Smokeを再実行し、2件PassしたためProduct Failureとは扱わない。

Mac Acceptance Probe実測：

```text
Load including SHA-512 : 2.5008 s
RSS before load        : 55,296,000 bytes
RSS after load         : 3,265,101,824 bytes
RSS after unload       : 175,177,728 bytes
Model SHA-512          : Match
Generate／Stream       : Completed
Cancel／Post-cancel    : Completed
Thinking Parse         : unclosed_reasoning
```

### 5.3 未実行Gate

```text
Local Python 3.12.11 Native Test : Interpreter unavailable／Not Run
Lightning Python 3.12.11 Test    : Not Run
Lightning CUDA Build／Load       : Not Run
Lightning Actual GPU Offload     : Not Run
Lightning CPU Candidate A        : Not Run
```

未実行Gateを合格扱いしない実装報告の自己評価は正しい。

## 6. Acceptance Status

| Area | Result | Notes |
|---|---|---|
| Python Metadata／Lock | Conditional Pass | Lock整合Pass、3.12 Native未実行 |
| Mac 3.13／Metal Regression | Pass | Static／Default／Native Pass |
| Platform／Container Contract | Pass | Deterministic Test Pass |
| CUDA／CPU Profile Definition | Pass | `verification_state=defined`維持 |
| CUDA Build Detection | Pass | Build Variant判定としては成立 |
| Actual GPU Offload Observation | Fail | Capability／Requestから推定している |
| Acceptance Probe Fail-closed | Fail | Check不合格をExit Codeへ反映しない |
| Response Language Native Evidence | Fail | 文字数のみ |
| Thinking Native Evidence | Fail | `unclosed_reasoning`でも成功 |
| Lightning Native Gate | Pending | External実行前 |

## 7. Next Gate

```text
実装担当Follow-up
  ├─ Actual GPU Offload Evidence
  ├─ Acceptance Probe Fail Closed
  ├─ Language／Thinking Check強化
  └─ CPU-only Preflight改善または明示Disposition
        ↓
設計者Follow-up Review
        ↓
Lightning環境Preflight／一回のSource搬入
        ↓
Python 3.12／CUDA Mandatory Gate／CPU Candidate Gate
        ↓
後継Implementer Status
        ↓
Phase 1-F Final Review
```

Phase 1-Gの実装、Phase 1完了宣言、Backup、Phase 1-ex、Git、GitHub公開はまだ開始しない。

## 8. Authorization Boundary

本ReviewとIndex作成は、Source／Config／Tests／Scriptsの修正、Lightning操作、Model Download、Backup、Git、GitHub公開を許可しない。Follow-up実装は、ユーザーが本Reviewを実装担当へ渡し、開始を指示した後に行う。

## 9. Append-Only

既存文書を変更せず、新TimestampのReviewとして追加した。

<!-- SOURCE_END 45: docs/handoffs/designer_review_phase_1f_lightning_cross_environment_runtime_20260720235113.md -->

---

<!-- SOURCE_BEGIN 46: docs/handoffs/designer_review_phase_1f_lightning_external_pure_cpu_runtime_20260726092413.md -->

### Source 46: `docs/handoffs/designer_review_phase_1f_lightning_external_pure_cpu_runtime_20260726092413.md`

- History Target: `docs/project/phases/phase_1/history/handoffs/designer_review_phase_1f_lightning_external_pure_cpu_runtime_20260726092413.md`
- Source SHA-512: `9e96e6a84ff65a0f163c50cecf38565ad10921a56e16907d057fd33b0a16fb02d6dd0d26c6a08e18da1a8361fa1171c578c2c165b1cc1fb1b39f957c2b658aa3`
- Source Size: `4849` bytes

# Phase 1-F Lightning External Pure CPU Runtime 設計Review

- 文書ID: `designer_review_phase_1f_lightning_external_pure_cpu_runtime`
- 状態: `external_runtime_accepted_full_suite_follow_up_required`
- 作成日時: `2026-07-26 09:24:13 JST`
- 更新日時: `2026-07-26 09:24:13 JST`
- Snapshot: `20260726092413`
- 作成担当: 設計者役担当Task
- 対象: ユーザー実行Lightning Pure CPU Environment Reconstruction／Native Acceptance
- Current Manual: [lightning_pure_cpu_actual_environment_reconstruction_manual_20260726092413.md](../history/user_manual/lightning_pure_cpu_actual_environment_reconstruction_manual_20260726092413.md)
- Test-only Handoff: [designer_handoff_phase_1f_lightning_test_isolation_follow_up_20260726092413.md](../history/handoffs/designer_handoff_phase_1f_lightning_test_isolation_follow_up_20260726092413.md)
- Previous Repository Review: [designer_review_phase_1f_pure_cpu_acceptance_correction_20260725214428.md](../history/handoffs/designer_review_phase_1f_pure_cpu_acceptance_correction_20260725214428.md)
- 正本言語: 日本語
- supersedes: なし

## 1. Conclusion

Lightning Linux x86_64 Pure CPU External RuntimeをAcceptedとする。

Full Repository Testは264件Pass、2件Test Isolation Failureであり、Full Suite GreenはPendingとする。

```text
External Pure CPU Runtime : ACCEPTED
Environment Verification : PASS
Native Acceptance        : PASS
Required Checks          : ALL TRUE
Static Verification      : PASS
Full Repository Suite    : FOLLOW-UP REQUIRED
Top-level Phase 1        : NOT DECLARED
```

## 2. Evidence Source

本Reviewはユーザー実行によるLightning Terminal出力と、Accepted Repository Contractを照合した。

外部Environmentへ本Taskから接続、変更または再実行していない。

## 3. Environment Evidence

```text
OS                    : Ubuntu Linux
Architecture          : x86_64
Execution Environment : container
Python                : 3.12.11
uv                    : 0.11.29／Project-isolated
Project Environment   : margpa-runtime-llm/.venv
Backend               : llama-cpp-python 0.3.34／Pure CPU
Model Root            : /teamspace/studios/this_studio/models
```

`uv` Binary SHA-512はAccepted値と一致した。

## 4. Runtime Evidence

Environment Verificationは成功した。

Bounded Native Acceptance：

```text
all_required_checks_passed : true
profile_key                : external.lightning-linux-x86_64.cpu-native
```

Pure CPU Profile Contract：

```text
Compute          : cpu
Acceleration API : none
GPU Offload      : false
Build Variant    : cpu
Fallback         : deny
```

実Model ArtifactはRegistry Relative Layoutで解決され、存在確認が成功した。

## 5. Static Verification

```text
Ruff Check  : PASS
Ruff Format : PASS／95 files
Mypy        : PASS／95 source files
```

## 6. Repository Test Progression

初回：

```text
258 passed
8 failed
1 skipped
3 deselected
```

内訳：

- UploadでShell実行権限喪失：5
- `.python-version`除外：1
- Platform Test Isolation：2

File Mode、MetadataおよびModel Root Environment漏出を解消後：

```text
264 passed
2 failed
1 skipped
3 deselected
```

## 7. Remaining Findings

### Finding A：Platform Execution Environment Isolation

2件のUnit Testが、OS／ArchitectureをMockしながら、Execution Environmentだけを実Lightning Containerから検出する。

Severity：

```text
Production Runtime : none
External Acceptance: non-blocking
Full Suite Green   : blocking
```

Required Action：

```text
Testへraw_execution_environment="native"を明示する。
```

### Finding B：Model Root Environment Isolation

`MARGPA_MODEL_ROOT`がTemporary Model Path Testへ漏出すると、Setupが設計どおりMismatchを拒否する。

Current user-run workaround：

```text
pytest ProcessからMARGPA_MODEL_ROOTとMARGPA_PROFILEを除外する。
```

恒久対応：

```text
Test Subprocess EnvironmentをTest内で明示的にSanitizeする。
```

## 8. Accepted Boundary

Acceptedとするもの：

- Lightning Pure CPU Environment再構築
- Pure CPU Backend
- Model Root解決
- Artifact Load
- Runtime／Profile一致
- Bounded Native Acceptance
- Static Verification

未Accepted：

- Cross-platform Full Suite Green
- Lightning Web Preview手動受入
- Top-level Phase 1完了
- Backup
- Phase 1-ex開始

## 9. Re-execution Scope

Follow-upはTest-only変更である。

次を再実行する。

- Mac Full Suite
- Lightning Full Suite
- Ruff
- Mypy

Production Runtime、Profile、SetupまたはAcceptance Scriptを変更しない限り、高コストなBounded Native Acceptanceの再実行は不要である。

## 10. Final Decision

```text
Phase 1-F Repository Pure CPU Follow-up : ACCEPTED
Lightning External Pure CPU Runtime     : ACCEPTED
Cross-platform Full Suite               : CHANGES REQUESTED／TEST ONLY
```


<!-- SOURCE_END 46: docs/handoffs/designer_review_phase_1f_lightning_external_pure_cpu_runtime_20260726092413.md -->

---

<!-- SOURCE_BEGIN 47: docs/handoffs/designer_review_phase_1f_lightning_full_suite_revalidation_20260726094241.md -->

### Source 47: `docs/handoffs/designer_review_phase_1f_lightning_full_suite_revalidation_20260726094241.md`

- History Target: `docs/project/phases/phase_1/history/handoffs/designer_review_phase_1f_lightning_full_suite_revalidation_20260726094241.md`
- Source SHA-512: `ce7eea46085bc750e3638f50c3ad8c72280a3731dc367a42131f9bb0979b71c56bc62a3d9de67542c9cc1bbbe9ffd76bfa5fba280d192caf824409de58ed7e5e`
- Source Size: `2538` bytes

# Phase 1-F Lightning Full Suite Revalidation 設計Review

- 文書ID: `designer_review_phase_1f_lightning_full_suite_revalidation`
- 状態: `accepted_full_suite_green_web_acceptance_pending`
- 作成日時: `2026-07-26 09:42:41 JST`
- 更新日時: `2026-07-26 09:42:41 JST`
- Snapshot: `20260726094241`
- 作成担当: 設計者役担当Task
- 対象Review: [designer_review_phase_1f_lightning_test_isolation_follow_up_20260726093437.md](../history/handoffs/designer_review_phase_1f_lightning_test_isolation_follow_up_20260726093437.md)
- External Runtime Review: [designer_review_phase_1f_lightning_external_pure_cpu_runtime_20260726092413.md](../history/handoffs/designer_review_phase_1f_lightning_external_pure_cpu_runtime_20260726092413.md)
- 正本言語: 日本語
- supersedes: なし

## 1. Conclusion

Lightning Linux x86_64 ContainerでのTest Isolation RevalidationをAcceptedとする。

```text
Targeted Test       : 41 passed
Full Suite          : 266 passed
Expected Skip       : 1
Expected Deselect   : 3
Failure             : 0
Full Suite          : GREEN
```

## 2. User-run Evidence

Targeted：

```text
41 passed in 0.70s
```

Full Suite：

```text
266 passed, 1 skipped, 3 deselected in 1.77s
```

Skip対象：

```text
tests/integration/test_llama_cpp_metal.py
```

Lightning Linux x86_64はApple Siliconではないため、このSkipは正常である。

## 3. Cross-platform Result

```text
Mac Full Suite       : 267 passed／3 deselected
Lightning Full Suite : 266 passed／1 skipped／3 deselected
```

Platform Testは実Container Markerから分離され、Temporary Model Path TestはShellの`MARGPA_MODEL_ROOT`から分離された。

## 4. Runtime Result

前回のEvidenceを維持する。

```text
Environment Verification       : PASS
External Pure CPU Runtime      : ACCEPTED
all_required_checks_passed     : true
Static Verification            : PASS
Cross-platform Full Suite      : GREEN
```

Test-only変更であり、Native Acceptanceの再実行は不要である。

## 5. Remaining Required Gate

Phase 1-F／Phase 1 Web Previewに関して、次の必須GateはLightning Web実起動と手動確認である。

- Pure CPU ProfileでWeb起動
- Basic認証
- `/healthz`
- CredentialなしRoot拒否
- Lightning Port公開
- Browser表示
- 短い日本語生成
- 停止
- 新規Chat
- Shutdown

## 6. Current Decision

```text
External Pure CPU Runtime  : ACCEPTED
Mac Full Suite             : GREEN
Lightning Full Suite       : GREEN
Lightning Web Acceptance   : PENDING
Top-level Phase 1          : NOT DECLARED
```


<!-- SOURCE_END 47: docs/handoffs/designer_review_phase_1f_lightning_full_suite_revalidation_20260726094241.md -->

---

<!-- SOURCE_BEGIN 48: docs/handoffs/designer_review_phase_1f_lightning_project_local_uv_preflight_20260721092818.md -->

### Source 48: `docs/handoffs/designer_review_phase_1f_lightning_project_local_uv_preflight_20260721092818.md`

- History Target: `docs/project/phases/phase_1/history/handoffs/designer_review_phase_1f_lightning_project_local_uv_preflight_20260721092818.md`
- Source SHA-512: `2a810e1c4b65997bfbb28f70d4a699a076dc045130125beba6ce898bcde82ec0e1f07ad7bb16edcb8adafa91244de7bea9c90b3688865c0cc5ddbe171243e6cc`
- Source Size: `6894` bytes

# Phase 1-F Lightning Project-local uv Preflight 設計Review

- 文書ID: `designer_review_phase_1f_lightning_project_local_uv_preflight`
- 状態: `accepted_ready_for_full_upload_handoff`
- 作成日時: `2026-07-21 09:28:18 JST`
- 更新日時: `2026-07-21 09:28:18 JST`
- Snapshot: `20260721092818`
- 作成担当: 設計者役担当Task
- 外部実行担当: ユーザー
- 対象: Project専用uv 0.11.29導入とLightning Preflight再実行
- 正本言語: 日本語
- 前回Review: [designer_review_phase_1f_lightning_read_only_preflight_20260721090725.md](../history/handoffs/designer_review_phase_1f_lightning_read_only_preflight_20260721090725.md)
- 要件: [phase_1f_lightning_cross_environment_runtime_requirements_20260719202333.md](../history/requirements/phase_1f_lightning_cross_environment_runtime_requirements_20260719202333.md)
- ADR: [adr_0015_phase_1f_lightning_and_python_312_support_20260719202333.md](../history/adr/adr_0015_phase_1f_lightning_and_python_312_support_20260719202333.md)
- 最新Index: [documentation_index_20260721092818.md](../history/documentation_index_20260721092818.md)
- supersedes: `designer_review_phase_1f_lightning_read_only_preflight_20260721090725.md`

## 1. Review結論

ユーザーがLightning AI Studioで実行したProject専用uv 0.11.29の隔離導入とPreflight再実行をAcceptedとする。

Project／Studio専用Tool Pathのuvは0.11.29であり、Lightning既設`/usr/local/bin/uv`は0.11.18のまま維持された。Shell全体のPATHを恒久変更せず、Preflight Processだけで専用uvを優先している。

Help、GPU Mandatory Preflight、CPU Candidate PreflightはすべてExit Code 0で合格した。したがって、Phase 1-FのRead-only Preflight GateをAcceptedとし、Full Project／Modelを一度だけ搬入する次Handoffを作成可能と判定する。

ただし、Dependency Sync、CUDA Native Build／Reuse、Model Load、Generate、CPU Runtimeはまだ未実行である。Phase 1-F全体の完了宣言ではない。

```text
Project／Studio-local uv       : 0.11.29／Pass
Lightning Existing uv          : 0.11.18／Unchanged
Permanent PATH Mutation        : None
Help Gate                      : Pass／Exit 0
GPU Preflight                  : Pass／Exit 0
CPU Candidate Preflight        : Pass／Exit 0
Python                         : 3.12.11／Retained
Environment Mode               : studio-active
nvcc                           : Available
Preflight Decision             : Accepted
Full Upload Handoff            : Ready to Create
Phase 1-F Completion           : Not Accepted Yet
```

## 2. User-supplied External Evidence

### 2.1 Project／Studio-local uv

```text
Version      : uv 0.11.29／x86_64-unknown-linux-gnu
Placement    : Studio-local .runtime-tools/uv/0.11.29/bin/uv
Binary Size  : 65,688,664 bytes
uvx          : Present
SHA-512      : 957e3ee915fef24101de24a8414c4a9f60e3bd25f0e127eb89a12a78e6bbb6f79621dcb5e10dc41e31834f77a6d7180bebcdfc7ccb08901eba059cde627e8d48
```

個人情報や公開に不要な絶対Pathは正本文書へ保存せず、Studio-local相対概念として記録する。

### 2.2 Lightning Existing uv

```text
Command Source : /usr/local/bin/uv
Version        : uv 0.11.18／x86_64-unknown-linux-gnu
Mutation       : None
```

既設uvとMARGPA専用uvの分離が成立している。

## 3. GPU Preflight Evidence

実行方式：Process単位でMARGPA専用uv DirectoryをPATH先頭へ置き、Preflightを`auto` Modeで実行した。

```text
Result           : Phase 1-F Lightning preflight passed.
Exit Code        : 0
Environment Mode : studio-active
Python           : 3.12.11
uv               : 0.11.29／MARGPA専用Path
GPU Required     : 1
nvcc Available   : yes／informational
```

前回EvidenceからAllocated GPUはTesla T4／15360 MiBであり、今回のGPU Required Gateも合格した。

## 4. CPU Candidate Preflight Evidence

```text
Result           : Phase 1-F Lightning preflight passed.
Exit Code        : 0
Environment Mode : studio-active
Python           : 3.12.11
uv               : 0.11.29／MARGPA専用Path
GPU Required     : 0
nvcc Available   : yes／informational
```

この結果は、GPU Requirementを外したEnvironment Candidateの合格である。GPU未使用のModel Load／Generateや、GPUなしInstance上のCPU Runtimeを証明するものではない。CPU Native GateはFull Upload後に別途実行する。

## 5. Python Version Decision

Lightning Pythonは3.12.11のまま維持する。

根拠：

- ADR-0015でLightning既設CPython 3.12.11を正式な検証対象としてAccepted済みである。
- Project Metadataは`>=3.12,<3.14`であり、3.12.11は正式Support範囲内である。
- Mac 3.13.14とLightning 3.12.11の両方を通すことで、Application CoreのCross-version Portable Runtimeを実証できる。
- Studio Active EnvironmentのPython Upgradeは、既設Package、CUDA Native Build、Persistent Environmentへ新しい変数と副作用を追加する。
- 3.12.11でPreflightが成立しており、現時点でUpgradeを必要とするFailureが存在しない。

将来Lightning Python 3.13を追加する場合は、3.12.11を置換せず、別Environment／別Profile／別Native Gateとして追加する。

## 6. Acceptance Status

| Area | Result | Notes |
|---|---|---|
| uv Isolation | Pass | 0.11.29専用Path／0.11.18既設維持 |
| Installer Result | Pass | Exact Version Binary利用可能 |
| Permanent PATH Mutation | Pass | なし |
| Python 3.12.11 | Pass | Accepted Target維持 |
| GPU Preflight | Pass | Exit 0 |
| CPU Candidate Preflight | Pass | Exit 0／Native Runtime未証明 |
| Full Project／Model Upload | Not Run | 次Handoff待ち |
| Dependency Sync | Not Run | 次Gate |
| CUDA Native Runtime | Not Run | Mandatory Gate |
| CPU Native Runtime | Not Run | Candidate Gate |

## 7. Next Gate

```text
Full Upload／Native Verification Handoff
  → Project Sourceを一度だけ搬入
  → Mac固有物／Secret／Cache除外確認
  → GGUF ModelをPersistent Model Pathへ配置
  → MARGPA専用uv 0.11.29でLock／Sync
  → Existing CUDA Build確認または限定Rebuild
  → Python 3.12.11 Default Test
  → CUDA Mandatory Acceptance
  → CPU Candidate Acceptance
  → Implementer／External Status
  → Designer Final Review
```

ユーザーが懸念しているUpload回数を増やさないため、次Handoffで搬入対象、除外対象、Model配置、実行順を一括して固定する。

## 8. Authorization Boundary

本ReviewはRead-only PreflightをAcceptedし、Full Upload／Native Verification専用Handoffの作成を許可する。

本Review単独では、Full Upload、Model Transfer、Dependency Sync、Native Build、Source変更、Python Upgrade、Phase 1-G実装、Backup、Git、GitHub公開をまだ許可しない。

## 9. Append-Only

既存文書を変更せず、新TimestampのReviewとして追加した。

<!-- SOURCE_END 48: docs/handoffs/designer_review_phase_1f_lightning_project_local_uv_preflight_20260721092818.md -->

---

<!-- SOURCE_BEGIN 49: docs/handoffs/designer_review_phase_1f_lightning_read_only_preflight_20260721090725.md -->

### Source 49: `docs/handoffs/designer_review_phase_1f_lightning_read_only_preflight_20260721090725.md`

- History Target: `docs/project/phases/phase_1/history/handoffs/designer_review_phase_1f_lightning_read_only_preflight_20260721090725.md`
- Source SHA-512: `29f289e8b3e6d118333d6427bc1f347f6cb238ffb32e31d535c1052dcb19bb622c616b1389380cafd4de7c1c5da2f291f45948e27ec2607533b9f36ae098d566`
- Source Size: `9160` bytes

# Phase 1-F Lightning Read-only Preflight 設計Review

- 文書ID: `designer_review_phase_1f_lightning_read_only_preflight`
- 状態: `execution_accepted_environment_follow_up_required`
- 作成日時: `2026-07-21 09:07:25 JST`
- 更新日時: `2026-07-21 09:07:25 JST`
- Snapshot: `20260721090725`
- 作成担当: 設計者役担当Task
- 対象: Lightning Read-only Preflight実行結果とFull Upload可否
- 正本言語: 日本語
- 実装報告: [implementer_status_phase_1f_lightning_read_only_preflight_20260721013900.md](../history/handoffs/implementer_status_phase_1f_lightning_read_only_preflight_20260721013900.md)
- Handoff: [implementer_handoff_phase_1f_lightning_read_only_preflight_20260721010621.md](../history/handoffs/implementer_handoff_phase_1f_lightning_read_only_preflight_20260721010621.md)
- Repository Accepted Review: [designer_review_phase_1f_minor_static_gate_follow_up_20260721010200.md](../history/handoffs/designer_review_phase_1f_minor_static_gate_follow_up_20260721010200.md)
- 要件: [phase_1f_lightning_cross_environment_runtime_requirements_20260719202333.md](../history/requirements/phase_1f_lightning_cross_environment_runtime_requirements_20260719202333.md)
- 最新Index: [documentation_index_20260721090725.md](../history/documentation_index_20260721090725.md)
- supersedes: `designer_review_phase_1f_minor_static_gate_follow_up_20260721010200.md`

## 1. Review結論

実装担当によるRead-only Preflight実行はAcceptedとする。

Script 1ファイルだけを配置し、Help、GPU、CPU Candidateを指示どおり実行した。Preflight失敗後もPackage、Environment、Source、GPU設定を変更せず、Full Project／Modelを搬入せず停止している。Privacy／Secret除外も成立している。

Preflight自体は、Lightning既設`uv 0.11.18`とProject期待値`uv 0.11.29`の不一致により不合格である。これはMARGPA RuntimeやPython／CUDAのFailureではなく、Native Gateへ進む前のToolchain Reproducibility Gateである。

設計判断として、期待値を0.11.18へ緩和しない。Lightning既設uvをGlobal／Studio共通環境で上書きもしない。後続の限定Scopeで、公式uv 0.11.29をProject専用の隔離Pathへ導入し、そのBinaryを明示してPreflightを再実行する。

したがって、現時点ではFull Uploadを許可しない。

```text
Implementer Scope Compliance : Pass
Script Integrity             : Pass／SHA-512 Match
Help Gate                    : Pass
Host／Python Precondition    : Pass
GPU Allocation Evidence      : Pass／Tesla T4 15360 MiB
nvcc Availability            : Available
GPU Preflight                : Fail／uv 0.11.18 != 0.11.29
CPU Candidate Preflight      : Fail／same uv Gate
Environment Mutation         : None
New Product Finding          : 0
Environment Follow-up        : Required
Full Upload                  : Not Authorized
Phase 1-F Completion         : Not Accepted Yet
```

## 2. Scope Compliance

次はHandoffどおり成立した。

- Lightningへ配置したProject FileはPreflight Script 1点だけである。
- Local正本とLightning配置物のSHA-512が一致した。
- Mac `.venv`、Model Artifact、Project本体を搬入していない。
- `uv sync`、`pip install`、Native Build、Config／Source変更を行っていない。
- 失敗後の即席Repairを行っていない。
- Credential、Private URL、Session／Machine Identifier、個人PathをStatusへ残していない。
- GPU／CPUの未合格結果をPass扱いしていない。

独立したLocal照合でも、Preflight ScriptのSHA-512はStatus記載値と一致した。

```text
1e78756d581de1895542bfc9a2f25438c4a2058b2d3873dd9208191f3d028cfff8cecb434a1d2ee02885727043b592ea90356df50774795e45ef91ebbe356eab
```

## 3. Environment Evidence

Preflightがuv Gateへ到達したこと、および追加のRead-only Evidenceから次を確認できる。

```text
Operating System      : Linux
Architecture          : x86_64
Distribution          : Ubuntu
Execution Environment : Container
Environment Mode      : studio-active
Python                : 3.12.11／Exact Match
uv                    : 0.11.18／Expected 0.11.29
GPU                    : Tesla T4／15360 MiB
nvidia-smi             : Available
nvcc                   : Available
```

GPU／`nvcc`の独立確認はPreflight自体を合格へ変更しないが、次の限定Follow-upを実行可能なTargetであることは示している。

## 4. uv Version Decision

### 4.1 Retain 0.11.29

Projectは、既存ADR、Mac Setup、Lightning Setup、Preflightでuv 0.11.29を再現性Toolchainとして固定している。ここでLightning既設値へ期待値を緩めると、環境ごとに異なるuvでLock／Sync／Buildを行うことになり、Phase 1-FのCross-environment Reproducibility目的を弱める。

`pyproject.toml`のBuild Backendも`uv_build>=0.11.29,<0.12`である。これはuv CLI Versionと同一概念ではないが、Projectが0.11.29世代を基準としている補助Evidenceである。

uv 0.11.18が本Projectで実際に動かないと判定したわけではない。互換性を未検証のまま受理せず、Accepted Toolchainへ揃える判断である。

### 4.2 Do Not Mutate Studio-global uv

LightningのPersistent Active Environmentには他のPackage／Toolが存在し得る。既設`uv`を直接Upgrade／Overwriteすると、Studio共通環境へ不要な副作用を与える。

次の構造を採用する。

```text
Lightning Existing uv 0.11.18
  └─ Unchanged

MARGPA Project-local Toolchain
  └─ uv 0.11.29／Exact Version／Explicit Path
```

Project専用uvはPython Environment内Packageではなく、公式Standalone Binaryとして隔離する方向を第一候補とする。

### 4.3 Primary Sources

- [uv 0.11.18 Official Release](https://github.com/astral-sh/uv/releases/tag/0.11.18)
- [uv 0.11.29 Official Release](https://github.com/astral-sh/uv/releases/tag/0.11.29)
- [uv Official CLI Reference](https://docs.astral.sh/uv/reference/cli/)

公式ReleaseではLinux x86_64用0.11.29 ArtifactとVersion固定Installerが提供されている。後続設計では、公式配布物、Checksum／Digest検証、隔離配置、明示Path、Version再確認を必須にする。

## 5. Required Follow-up

次の小規模Follow-upを、Read-only Preflightとは分離した明示的なEnvironment Mutation Scopeとして設計する。

```text
1. uv 0.11.29 Project-local Bootstrap Script
2. Official Source／Exact Version固定
3. Downloaded ArtifactまたはInstallerのIntegrity Evidence
4. Studio-global uv 0.11.18が未変更であることの確認
5. Project-local uv 0.11.29の明示Path確認
6. 同じPreflightをProject-local uvで再実行
7. GPU／CPU Candidate Resultを後継Statusへ記録
```

Preflight Scriptへ自動Install処理を混在させない。Read-only ProbeとMutationを別Script／別Stepに維持する。

## 6. Independent Verification

Local Repositoryで次を確認した。

```text
Preflight Script SHA-512                      : Statusと一致
bash -n Preflight／Lightning Full Setup       : Pass
pytest Config／Deployment Platform対象        : Pass／65 tests
Local Source／Config変更                      : None required by this Review
```

Lightning側のCommandは外部Target実行であるため、設計者役はImplementer StatusのEvidenceをReviewした。外部Targetで未実行のNative Gateを合格扱いしていない。

## 7. Acceptance Status

| Area | Result | Notes |
|---|---|---|
| Implementer Read-only Execution | Accepted | Scope／停止条件を遵守 |
| Script Integrity | Pass | SHA-512 Match |
| Host／Container／Python | Pass | Linux x86_64／Ubuntu／Container／3.12.11 |
| GPU Allocation Evidence | Pass | Tesla T4／15360 MiB |
| uv Toolchain Gate | Fail | Observed 0.11.18／Expected 0.11.29 |
| GPU Preflight | Blocked | uv Gateで停止 |
| CPU Candidate Preflight | Blocked | uv Gateで停止 |
| Product Runtime | Not Run | Full Upload前 |
| Full Upload | Not Authorized | uv Follow-up待ち |

## 8. Next Gate

```text
Project-local uv 0.11.29 Bootstrap設計／Handoff
  → Implementer限定Follow-up
  → Project-local uv Version／Integrity確認
  → Read-only Preflight再実行
  → Designer Review
  → Full Upload可否判定
```

Source一式、Model、Dependency Sync、Native Build、CUDA／CPU Acceptanceはまだ開始しない。

## 9. Summary Mode Decision Separation

本Turnで確定した要約モードは、[Post-generation Summary Mode要件予約](../history/requirements/post_generation_summary_mode_requirements_reservation_20260721090725.md)へ分離した。Phase 1-FのPreflight／Toolchain判断へ混在させない。

## 10. Authorization Boundary

本Reviewは実装担当のRead-only実行をAcceptedとするが、Full Upload、Model Transfer、Dependency Install、Studio-global uv変更、Project-local uv導入、Native Buildをまだ許可しない。

次はProject-local uv 0.11.29 Bootstrap専用Handoffを作成し、ユーザーが実装担当へ開始を指示した後に進める。

## 11. Append-Only

既存文書を変更せず、新TimestampのReviewとして追加した。

<!-- SOURCE_END 49: docs/handoffs/designer_review_phase_1f_lightning_read_only_preflight_20260721090725.md -->

---

<!-- SOURCE_BEGIN 50: docs/handoffs/designer_review_phase_1f_lightning_test_isolation_follow_up_20260726093437.md -->

### Source 50: `docs/handoffs/designer_review_phase_1f_lightning_test_isolation_follow_up_20260726093437.md`

- History Target: `docs/project/phases/phase_1/history/handoffs/designer_review_phase_1f_lightning_test_isolation_follow_up_20260726093437.md`
- Source SHA-512: `a88696a8573f5a791c13ac21409d658862e32dde03d0aff5036dfd4bbdacf208d94c1f96fafe49a2518fb76de4f807caa1cce48a00217b4c8b9827fcbeb6787f`
- Source Size: `5861` bytes

# Phase 1-F Lightning Test Isolation Follow-up 設計Review

- 文書ID: `designer_review_phase_1f_lightning_test_isolation_follow_up`
- 状態: `accepted_repository_lightning_revalidation_pending`
- 作成日時: `2026-07-26 09:34:37 JST`
- 更新日時: `2026-07-26 09:34:37 JST`
- Snapshot: `20260726093437`
- 作成担当: 設計者役担当Task
- 対象Handoff: [designer_handoff_phase_1f_lightning_test_isolation_follow_up_20260726092413.md](../history/handoffs/designer_handoff_phase_1f_lightning_test_isolation_follow_up_20260726092413.md)
- External Runtime Review: [designer_review_phase_1f_lightning_external_pure_cpu_runtime_20260726092413.md](../history/handoffs/designer_review_phase_1f_lightning_external_pure_cpu_runtime_20260726092413.md)
- 正本言語: 日本語
- supersedes: なし

## 1. Conclusion

Phase 1-F Lightning Test Isolation Follow-upのRepository変更をAcceptedとする。

Mac RepositoryでTargeted Test、Full Suite、Ruff、FormatおよびMypyがすべてPassした。Production Code、Config、Setup Script、Acceptance ScriptまたはDependency Lockへの変更は確認しなかった。

Lightning Full Suiteの再実行は未実施であり、Cross-platform Full Suite GreenはPendingのまま保持する。

```text
Repository Test-only Change : ACCEPTED
Mac Targeted Test           : PASS
Mac Full Suite              : PASS
Static Verification         : PASS
Production Change           : NONE
Lightning Revalidation      : PENDING
Native Acceptance Re-run    : NOT REQUIRED
```

## 2. Reviewed Files

変更対象：

```text
tests/unit/inference/test_deployment_platform.py
tests/unit/inference/test_lightning_cpu_native_setup.py
```

Handoff Scope外のProduction Fileに、同時刻以降の変更を確認しなかった。

Test実行により生成・更新された`__pycache__`はLocal Generated Artifactであり、Source変更として扱わない。

## 3. Platform Test Isolation

次のTestへExecution Environmentの明示が追加された。

```text
test_profile_resolution_priority_is_explicit_then_environment_then_default
test_future_platform_alias_and_default_are_registry_only_extensions
```

追加値：

```python
raw_execution_environment="native",
```

確認した内容：

- explicit Profile Resolution
- Environment Profile Resolution
- Platform Default Resolution
- Future Platform Registry-only Extension

OS、ArchitectureおよびExecution EnvironmentがすべてTest Inputとして固定される。実行Hostの`/.dockerenv`、Container MarkerまたはCgroupに依存しない。

## 4. Model Root Test Isolation

`test_model_path_compatibility_requires_registry_layout`へSanitized Subprocess Environmentが追加された。

```python
environment = dict(os.environ)
environment.pop("MARGPA_MODEL_ROOT", None)
environment.pop("MARGPA_PROFILE", None)
```

次の3 Subprocessへ同じEnvironmentを渡す。

- Compatible Model Path
- Invalid Layout
- Model Root／Path Mismatch

ユーザーShellで実Model用`MARGPA_MODEL_ROOT`がExportされていても、Temporary Model Root Contract Testへ漏出しない。

Production SetupのFail Closed Contractは変更されていない。

## 5. Independent Targeted Verification

設計者役がMac Repositoryで独立実行した。

```bash
pytest -q \
  tests/unit/inference/test_deployment_platform.py \
  tests/unit/inference/test_lightning_cpu_native_setup.py
```

結果：

```text
41 passed
```

## 6. Independent Full Suite

```bash
pytest -q
```

結果：

```text
267 passed
3 deselected
0 failed
```

Model Smokeは既定でDeselectされる。

## 7. Static Verification

```text
Ruff Check  : PASS
Ruff Format : PASS／95 files
Mypy        : PASS／95 source files
```

## 8. Code Review Findings

Blocking Findingは確認しなかった。

### Isolation

- Mock対象と実Host Evidenceの混在を解消している。
- Application用Environment VariableをTest Subprocessから局所的に除外している。
- Global Environment Mutationを行わない。
- Test終了後のShell Environmentへ影響しない。

### Scope

- Production ResolverをTest都合で変更していない。
- Setup ScriptのFail Closedを弱化していない。
- Model Root Contractを変更していない。
- Lightning Profileを変更していない。
- Native Acceptance Contractを変更していない。

## 9. Lightning Revalidation

Lightningへ次の2Fileだけを反映する。

```text
tests/unit/inference/test_deployment_platform.py
tests/unit/inference/test_lightning_cpu_native_setup.py
```

Targeted：

```bash
"$MARGPA_ENV_PREFIX/bin/pytest" -q \
  tests/unit/inference/test_deployment_platform.py \
  tests/unit/inference/test_lightning_cpu_native_setup.py
```

期待値：

```text
41 passed
```

Full Suiteは、`MARGPA_MODEL_ROOT`をShellへExportした状態のまま実行する。

```bash
"$MARGPA_ENV_PREFIX/bin/pytest" -q
```

期待値：

```text
266 passed
1 skipped
3 deselected
0 failed
```

Apple Silicon Metal Testの1件Skipは正常である。

手動`env -u MARGPA_MODEL_ROOT`なしでPassすることが今回の受入条件である。

## 10. Native Acceptance

本変更はTest-onlyである。

次を変更していない。

- `src/`
- `config/`
- `scripts/setup/`
- `scripts/models/`
- `pyproject.toml`
- `uv.lock`

前回のLightning Bounded Native Acceptance：

```text
all_required_checks_passed=true
```

は有効であり、再実行を要求しない。

## 11. Current Decision

```text
External Pure CPU Runtime  : ACCEPTED
Repository Test Isolation  : ACCEPTED
Mac Full Suite             : GREEN
Lightning Full Suite       : REVALIDATION PENDING
Lightning Web Acceptance   : PENDING
Top-level Phase 1          : NOT DECLARED
```

## 12. Next Gate

```text
LightningへTest 2File反映
  → Targeted 41件
  → Full Suite
  → Full Suite Green Review
  → Lightning Web Preview Acceptance
```


<!-- SOURCE_END 50: docs/handoffs/designer_review_phase_1f_lightning_test_isolation_follow_up_20260726093437.md -->

---

<!-- SOURCE_BEGIN 51: docs/handoffs/designer_review_phase_1f_minor_static_gate_follow_up_20260721010200.md -->

### Source 51: `docs/handoffs/designer_review_phase_1f_minor_static_gate_follow_up_20260721010200.md`

- History Target: `docs/project/phases/phase_1/history/handoffs/designer_review_phase_1f_minor_static_gate_follow_up_20260721010200.md`
- Source SHA-512: `3219ca286fa10a074de9d4199d015781c9b9dd52adca0c99381970a142145acabde1f219a0eb21111308b604e29718b3a5fe2f8895a5efd4881f9c859c20b556`
- Source Size: `7695` bytes

# Phase 1-F Minor Static Gate Follow-up 設計Review

- 文書ID: `designer_review_phase_1f_minor_static_gate_follow_up`
- 状態: `accepted_repository_ready_for_lightning_preflight`
- 作成日時: `2026-07-21 01:02:00 JST`
- 更新日時: `2026-07-21 01:02:00 JST`
- Snapshot: `20260721010200`
- 作成担当: 設計者役担当Task
- 対象: Phase 1-F Minor Static Gate Follow-upとLightning Preflight進行可否
- 正本言語: 日本語
- 実装報告: [implementer_status_phase_1f_minor_static_gate_follow_up_20260721005412.md](../history/handoffs/implementer_status_phase_1f_minor_static_gate_follow_up_20260721005412.md)
- 前回Review: [designer_review_phase_1f_repository_follow_up_20260721003201.md](../history/handoffs/designer_review_phase_1f_repository_follow_up_20260721003201.md)
- 要件: [phase_1f_lightning_cross_environment_runtime_requirements_20260719202333.md](../history/requirements/phase_1f_lightning_cross_environment_runtime_requirements_20260719202333.md)
- ADR: [adr_0015_phase_1f_lightning_and_python_312_support_20260719202333.md](../history/adr/adr_0015_phase_1f_lightning_and_python_312_support_20260719202333.md)
- 最新Index: [documentation_index_20260721010200.md](../history/documentation_index_20260721010200.md)
- supersedes: `designer_review_phase_1f_repository_follow_up_20260721003201.md`

## 1. Review結論

前回Reviewで残ったFull Project Mypy Failureは解消した。TestがRuntime Module内部の`subprocess`へ直接到達する構造は廃止され、型付きCommand Runnerを関数境界から注入する構造へ変更されている。

ユーザー決定済みのApplication Default `generation.max_new_tokens = 2048`もConfigと関連Testへ反映された。低Level Contract Default、明示Override、Environment Override、Request Parameterの優先順位は変更されておらず、変更範囲は適切である。

独立検証でも、Full Mypy、Default Test、Ruff、Compile、Shell構文、Lock整合、Mac Metal Model Smokeがすべて合格した。新規Findingはない。

したがって、Phase 1-FのRepository Follow-upをAcceptedとし、Lightning AI StudioのRead-only Preflightへ進むことを許可する。

ただし、Lightning Python 3.12.11、CUDA Mandatory Gate、CPU Candidate Gateはまだ未実行である。Phase 1-F全体の完了宣言ではない。

```text
Previous Static Finding       : Resolved
generation.max_new_tokens     : 2048／Applied
Full Project Mypy             : Pass／70 source files
Default Test                  : Pass／183 passed、3 deselected
Mac Metal Model Smoke         : Pass／2 passed、1 skipped、1 deselected
New Finding                   : 0
Repository Decision           : Accepted
Lightning Preflight           : Authorized／Not Run
Phase 1-F Completion          : Not Accepted Yet
```

## 2. Review対象

```text
config/application.toml
src/margpa_runtime_llm/adapters/model_backends/llama_cpp/runtime_detection.py
tests/unit/inference/test_deployment_platform.py
tests/unit/inference/test_config_and_registry.py
docs/handoffs/implementer_status_phase_1f_minor_static_gate_follow_up_20260721005412.md
```

## 3. Static Finding解消確認

### 3.1 Production境界

`observe_nvidia_process_gpu_memory`は、任意の`NvidiaSmiCommandRunner`を受け取れる。ProductionでRunnerが省略された場合だけ、既定RunnerがTimeout付きで`subprocess.run`を実行する。

```text
Production Call
  → default typed command runner
  → subprocess.run
  → nvidia-smi process memory evidence

Unit Test
  → injected typed fake runner
  → deterministic CompletedProcess
  → PID scope／memory aggregation verification
```

Productionの既定挙動を維持しながら、TestがModule内部Import Detailへ依存しない構造である。依存性注入の範囲もCommand実行境界に限定されている。

### 3.2 Test Evidence

Testは次を維持している。

- Runnerへ渡されるCommandがCurrent Process GPU Memory Queryである。
- 対象PIDの複数Rowを合算する。
- 別PIDのMemoryを除外する。
- `subprocess.CompletedProcess[str]`を使用して型を固定する。

Full Project Mypyの旧Errorは再現せず、70 Source Fileすべて合格した。

## 4. Generation Default確認

Application Configは次へ変更された。

```toml
[generation]
max_new_tokens = 2048
```

Config所有値とEffective macOS Configを確認するTestも2048へ更新された。

低Levelの`GenerationParameters()` Contract Default 512は維持されている。Application Configを経由しない低Level生成の安全なFallbackと、ユーザーが通常利用するApplication Defaultを分離するため、現時点のScopeとして妥当である。

Thinking表示Labelは`高度推論`のままであり、合意どおりPhase 1-GのUI／説明注記とともに後続設計する。

## 5. Independent Verification

```text
.venv/bin/mypy .                            : Pass／70 source files
.venv/bin/pytest -q                         : Pass／183 passed、3 deselected
.venv/bin/ruff check src scripts tests      : Pass
.venv/bin/ruff format --check src scripts tests
                                             : Pass／70 files
.venv/bin/python -m compileall -q src scripts tests
                                             : Pass
bash -n Lightning Setup／Preflight           : Pass
uv lock --check --offline                   : Pass／117 packages
.venv/bin/pytest -q -m model_smoke tests/integration
                                             : Pass／2 passed、1 skipped、1 deselected
```

`uv lock`はSandboxのUser Cache読取制約を避け、Sandbox外で同一Commandを実行した。Lock File変更はない。

Model SmokeはMac Metal実機Contextで実行した。Skip 1件は`MARGPA_PHASE1F_PROFILE`未指定によるLightning専用Integration Testであり、失敗ではない。

## 6. Acceptance Status

| Area | Result | Notes |
|---|---|---|
| Full Project Mypy | Pass | 70 source files |
| Default Runtime Tests | Pass | 183 passed、3 deselected |
| Application Default | Pass | `max_new_tokens = 2048` |
| Mac 3.13／Metal Regression | Pass | Model Smoke合格 |
| Repository Follow-up | Accepted | 新規Findingなし |
| Lightning Read-only Preflight | Ready | 次の外部Gate |
| Lightning Python 3.12.11 | Pending | Target未実行 |
| Lightning CUDA Mandatory Gate | Pending | Target未実行 |
| Lightning CPU Candidate | Pending | Best Effort／Target未実行 |

## 7. Next Gate

大容量Uploadを一度にまとめる方針に従い、最初は小型のRead-only PreflightだけをLightning Targetへ配置して実行する。

```bash
scripts/setup/preflight_lightning_ai_studio.sh --environment-mode auto
```

GPU未割当でCPU Candidateだけを確認する場合：

```bash
scripts/setup/preflight_lightning_ai_studio.sh \
  --environment-mode auto \
  --cpu-only
```

Preflight結果を実装担当Statusとして保存し、必要なEnvironment Modeを確定する。Preflight合格後にSource／Modelをまとめて搬入し、Python 3.12.11、CUDA Mandatory Gate、CPU Candidate Gateを実行する。

Phase 1-G実装、Phase 1完了宣言、Backup、Phase 1-ex、Git、GitHub公開はまだ開始しない。

## 8. Authorization Boundary

本Reviewにより、Phase 1-FのLightning Read-only Preflight実行を許可する。

Source／Config／Tests／Scriptsの追加変更、Full Upload、Dependency Install、Native Build、Model Download、Phase 1-G実装、Backup、Git、GitHub公開は、本Reviewだけでは許可しない。Full Upload以降はPreflight結果を確認してから進める。

## 9. Append-Only

既存文書を変更せず、新TimestampのReviewとして追加した。

<!-- SOURCE_END 51: docs/handoffs/designer_review_phase_1f_minor_static_gate_follow_up_20260721010200.md -->

---

<!-- SOURCE_BEGIN 52: docs/handoffs/designer_review_phase_1f_pure_cpu_acceptance_correction_20260725214428.md -->

### Source 52: `docs/handoffs/designer_review_phase_1f_pure_cpu_acceptance_correction_20260725214428.md`

- History Target: `docs/project/phases/phase_1/history/handoffs/designer_review_phase_1f_pure_cpu_acceptance_correction_20260725214428.md`
- Source SHA-512: `e1c2de17d94a6319e927b21bf77e47357c038a5622c4643f067adaaef5544c00fd62b47cc811da411e98bf4adec8fa5d8e2c4cfb6269a102452b29ab2d7dbe40`
- Source Size: `4495` bytes

# Phase 1-F Pure CPU Acceptance Correction 設計再Review

- 文書ID: `designer_review_phase_1f_pure_cpu_acceptance_correction`
- 状態: `accepted_repository_external_native_pending`
- 作成日時: `2026-07-25 21:44:28 JST`
- 更新日時: `2026-07-25 21:44:28 JST`
- Snapshot: `20260725214428`
- 作成担当: 設計者役担当Task
- 対象Status: [implementer_status_phase_1f_pure_cpu_acceptance_correction_20260725214037.md](../history/handoffs/implementer_status_phase_1f_pure_cpu_acceptance_correction_20260725214037.md)
- Correction Handoff: [designer_handoff_phase_1f_pure_cpu_acceptance_correction_20260725212559.md](../history/handoffs/designer_handoff_phase_1f_pure_cpu_acceptance_correction_20260725212559.md)
- Previous Review: [designer_review_phase_1f_pure_cpu_repository_20260725212559.md](../history/handoffs/designer_review_phase_1f_pure_cpu_repository_20260725212559.md)
- 正本言語: 日本語
- supersedes: なし

## 1. Conclusion

前回のBlocking FindingとModel Path Contract Findingは解消された。

Phase 1-F Pure CPU Repository Follow-upをAcceptedとする。外部Lightning EnvironmentでのNative Build、Model LoadおよびGenerationは未実施であり、External Native AcceptanceはPendingのまま保持する。

## 2. Finding 1 Resolution

Native AcceptanceからCPU Runtimeの固定判定：

```text
runtime.acceleration_api == "cpu_native"
```

が除去された。

新しいPure Functionは、Runtimeと選択Profileを次で照合する。

```text
runtime.acceleration_api
  == application.config.compute.acceleration_api_key
```

結果：

```text
CUDA GPU                 : cuda
CUDA Build CPU Execution : cpu_native
Pure CPU Build           : none
Unknown／Mismatch        : Fail Closed
```

GPU／CPUそれぞれのOffload、Device KindおよびObserved State条件も維持されている。

## 3. Finding 2 Resolution

Model選択の正本を`--model-root`とし、Registryの`artifact.relative_path`から実Artifactを解決する。

```text
MODEL_ROOT
  + main/qwen3-4b/gguf/Qwen3-4B-Q4_K_M.gguf
```

既存`--model-path`は任意OverrideではなくCompatibility Validationとして維持された。

- Expected Relative Layout一致
- Model Root併用時の完全一致
- Invalid Layout拒否
- Root不一致拒否
- Newline Path拒否
- Smoke前のFile存在確認
- Actual Acceptanceへ同じModel Rootを渡す。
- ReportへResolved Artifactを記録する。

指定したArtifactと実際にLoadするArtifactが異なる状態は解消された。

## 4. Independent Plan Verification

RepositoryのCurrent Model Rootを指定し、Read-only Planを実行した。

```text
setup_lightning_linux_x86_64_cpu.sh
  --plan
  --model-smoke
  --model-root models
```

結果：

- Exit Code 0
- Pure CPU Plan表示
- Model Root解決
- Registry Relative Artifact解決
- Actual Qwen3 GGUF存在確認
- Environment変更なし

Public Review文書へAbsolute Local Pathは記録しない。

## 5. Independent Automated Verification

```text
pytest Full Suite             : 267 passed, 3 deselected
Pure CPU Targeted             : 9 passed, 1 deselected
Ruff Check                    : PASS
Ruff Format                   : PASS／95 files
Mypy                          : PASS／75 source files
Node Safe Markdown            : 5 passed
Shell Syntax                  : PASS
uv lock --check               : PASS／122 packages
```

`deselected`のExternal Native／Model SmokeをPassとは扱わない。

## 6. Code Review

確認した対象：

- `runtime_evidence_matches_profile`
- `all_required_checks_passed`
- Acceptanceへの`cli_model_root`
- Resolved Artifact Report
- Setup `--model-root`
- Compatibility `--model-path`
- Registry Path Traversal拒否
- Symlink／Resolved Path境界
- Invalid Compute Kind拒否
- Test Fixtureによる`cuda`／`cpu_native`／`none`

新たなBlocking Findingは確認しなかった。

## 7. Remaining External Gate

ユーザーがLightning CPU Environmentで実施する。

- Read-only Preflight
- Setup Plan
- Environment Reconstruction
- Pure CPU Native Build／Reuse確認
- Environment Verification
- Model Root確認
- Bounded Native Smoke
- SHA-512
- Model Load
- Japanese／English
- Streaming／Cancel
- Thinking
- Memory／Latency
- Shutdown

## 8. Final State

```text
Pure CPU Profile／Runtime Detection : ACCEPTED
Pure CPU Preflight／Setup           : ACCEPTED
Acceptance Contract Correction      : ACCEPTED
Repository Follow-up                : COMPLETE／ACCEPTED
External Native Acceptance          : PENDING
```


<!-- SOURCE_END 52: docs/handoffs/designer_review_phase_1f_pure_cpu_acceptance_correction_20260725214428.md -->

---

<!-- SOURCE_BEGIN 53: docs/handoffs/designer_review_phase_1f_pure_cpu_repository_20260725212559.md -->

### Source 53: `docs/handoffs/designer_review_phase_1f_pure_cpu_repository_20260725212559.md`

- History Target: `docs/project/phases/phase_1/history/handoffs/designer_review_phase_1f_pure_cpu_repository_20260725212559.md`
- Source SHA-512: `5e313a246ddf24941917898cd600e4cc1c782edc4a4367895f73fa120e3d7cc5ca96a3ef4c1ba2933f5f5f2e088bf4da1c60564b4a154303e58f2a6aad37cef8`
- Source Size: `5204` bytes

# Phase 1-F Pure CPU Repository 設計Review

- 文書ID: `designer_review_phase_1f_pure_cpu_repository`
- 状態: `changes_requested`
- 作成日時: `2026-07-25 21:25:59 JST`
- 更新日時: `2026-07-25 21:25:59 JST`
- Snapshot: `20260725212559`
- 作成担当: 設計者役担当Task
- 対象Status: [implementer_status_phase_1f_pure_cpu_runtime_follow_up_20260725203508.md](../history/handoffs/implementer_status_phase_1f_pure_cpu_runtime_follow_up_20260725203508.md)
- 対象Handoff: [designer_handoff_phase_1f_lightning_pure_cpu_runtime_follow_up_20260725200001.md](../history/handoffs/designer_handoff_phase_1f_lightning_pure_cpu_runtime_follow_up_20260725200001.md)
- Preflight Addendum: [designer_handoff_phase_1f_lightning_pure_cpu_preflight_addendum_20260725201016.md](../history/handoffs/designer_handoff_phase_1f_lightning_pure_cpu_preflight_addendum_20260725201016.md)
- 正本言語: 日本語
- supersedes: なし

## 1. Conclusion

Pure CPU Profile、Runtime Detection、Preflight、Setup分離およびRepository Testの方向はAccepted Designと一致する。

ただし、外部Native Acceptanceを実行するScriptに新Pure CPU Profileと矛盾する判定が残っている。LightningへUpload／再構築する前に局所修正が必要であり、現時点のRepository Acceptanceは`CHANGES REQUESTED`とする。

## 2. Accepted Parts

- `lightning_linux_x86_64_cpu_native.toml`
- `build_variant = cpu`
- `device_kind = cpu`
- `acceleration_api = none`
- `gpu_layers = 0`
- `fallback = deny`
- Existing CUDA CPU Profile非変更
- Preflight三Target分離
- `--cpu-only`後方互換
- CPU-nativeでGPU／CUDA Command非実行
- Pure CPU Setup Script
- Normal Sync／Native Rebuild分離
- Model Download禁止
- External Native Validation Pending表示

## 3. Finding 1 — Native Acceptance Acceleration Mismatch

**Severity: High／External Acceptance Blocker**

対象：

```text
scripts/models/phase1f_cross_environment_acceptance.py
```

CPU Branchが次を固定している。

```text
runtime.acceleration_api == "cpu_native"
```

一方、新Pure CPU ProfileとRuntime Detectionは正しく次を返す。

```text
application.config.compute.acceleration_api_key = "none"
runtime.acceleration_api                       = "none"
```

このため、Pure CPU Runtimeが正しく動作しても`runtime_evidence_matches_profile`がFalseになり、Native Acceptance ReportはFailureになる。

### Required Correction

CPU BranchもProfile値と照合する。

概念形：

```text
runtime.acceleration_api
  == application.config.compute.acceleration_api_key
```

併せて、次を明示的にTestする。

- CUDA Build CPU Execution：`cpu_native`
- Pure CPU Build CPU Execution：`none`
- ProfileとRuntime不一致：Fail Closed

## 4. Finding 2 — `--model-path` Semantics

**Severity: Moderate／User Procedure Ambiguity**

Setup Helpは`--model-path PATH`を任意のLocal GGUF Pathとして説明している。しかしSmoke実行時はPathを4階層遡って`MARGPA_MODEL_ROOT`を作り、Default RegistryのRelative Pathを解決する。

したがって、指定Pathが次のLogical Layoutにあることを暗黙前提としている。

```text
MODEL_ROOT/main/qwen3-4b/gguf/Qwen3-4B-Q4_K_M.gguf
```

任意Pathを受理するContractではない。

### Required Correction

次のいずれかを採用する。

1. `--model-root`とRegistryを明示し、RegistryからArtifactを解決する。
2. `--model-path`がExpected Relative Layoutと一致することをFail Closedで検証する。
3. Acceptance ScriptへRegistry／Artifact Path Overrideを安全に追加する。

推奨は1である。User Procedureと実際にLoadされるArtifactを一致させ、別Fileを確認したふりをしない。

## 5. Test Gap

Repository Testは次を個別に確認している。

- Profileは`none`
- Runtime Detectionは`none`
- Verification Targetは`none`
- Integration TestはPure CPU Reportへ`none`を期待

しかし、Acceptance Script内部の`runtime_evidence_matches_profile`をPure CPU値で直接Testしていないため、矛盾を検出できなかった。

この判定をPure Functionへ抽出するか、Pure CPU Report Fixtureで`all_required_checks_passed`まで検証する。

## 6. Independent Verification

```text
pytest                         : 265 passed, 3 deselected
Pure CPU／Web Targeted         : 30 passed, 1 deselected
Ruff Check                     : PASS
Ruff Format                    : PASS
Mypy                           : PASS
Shell Syntax                   : PASS
uv lock --check                : PASS／122 packages
```

Test PassはRepository Contractの多くを支持するが、Finding 1の外部Acceptance Blockerを打ち消さない。

## 7. External State

次は未実施のままで正しい。

- Lightning Environment Reconstruction
- Pure CPU Native Build
- Model配置
- Native Model Load
- Generation
- Memory／Latency
- Public URL

Repository修正Review後にユーザー実行Gateへ進む。

## 8. Review State

```text
Profile／Preflight／Setup Direction : ACCEPTED
Repository Acceptance Script       : CHANGES REQUESTED
External Native Acceptance         : PENDING
Overall Pure CPU Follow-up          : NOT YET ACCEPTED
```


<!-- SOURCE_END 53: docs/handoffs/designer_review_phase_1f_pure_cpu_repository_20260725212559.md -->

---

<!-- SOURCE_BEGIN 54: docs/handoffs/designer_review_phase_1f_repository_follow_up_20260721003201.md -->

### Source 54: `docs/handoffs/designer_review_phase_1f_repository_follow_up_20260721003201.md`

- History Target: `docs/project/phases/phase_1/history/handoffs/designer_review_phase_1f_repository_follow_up_20260721003201.md`
- Source SHA-512: `a174029f380ffd9ab92e3e578067c9c83d17f9e0816d96fe57cb21f4d38d87337c2cb13ef6fa56bf31dfa20aa7704000be2c89c14844c29038a72d52de38810a`
- Source Size: `10872` bytes

# Phase 1-F Repository Follow-up 設計Review

- 文書ID: `designer_review_phase_1f_repository_follow_up`
- 状態: `changes_requested_minor_static_gate_before_lightning`
- 作成日時: `2026-07-21 00:32:01 JST`
- 更新日時: `2026-07-21 00:32:01 JST`
- Snapshot: `20260721003201`
- 作成担当: 設計者役担当Task
- 対象: Phase 1-F Repository Review Follow-upとLightning搬入可否
- 正本言語: 日本語
- 実装報告: [implementer_status_phase_1f_repository_review_follow_up_20260721001705.md](../history/handoffs/implementer_status_phase_1f_repository_review_follow_up_20260721001705.md)
- 前回Review: [designer_review_phase_1f_lightning_cross_environment_runtime_20260720235113.md](../history/handoffs/designer_review_phase_1f_lightning_cross_environment_runtime_20260720235113.md)
- 要件: [phase_1f_lightning_cross_environment_runtime_requirements_20260719202333.md](../history/requirements/phase_1f_lightning_cross_environment_runtime_requirements_20260719202333.md)
- ADR: [adr_0015_phase_1f_lightning_and_python_312_support_20260719202333.md](../history/adr/adr_0015_phase_1f_lightning_and_python_312_support_20260719202333.md)
- 実装Handoff: [implementer_handoff_phase_1f_lightning_cross_environment_runtime_20260719202333.md](../history/handoffs/implementer_handoff_phase_1f_lightning_cross_environment_runtime_20260719202333.md)
- 最新Index: [documentation_index_20260721003201.md](../history/documentation_index_20260721003201.md)
- supersedes: `designer_review_phase_1f_lightning_cross_environment_runtime_20260720235113.md`

## 1. Review結論

前回Reviewで指摘したHigh 2件、Medium 2件、Low 1件は、Repository実装上すべて適切にFollow-upされている。

Mac実機ではDefault Test、Model Smoke、Strict Acceptanceが通り、Strict Acceptanceの必須Checkは22件すべて合格した。GPU Offloadについても、Capability／Request／Observationが分離され、Metal Model LoadをObservation SourceとするEvidenceが記録されている。

ただし、実装報告が実行した限定範囲の`mypy`は通っている一方、Project全体の正式な`mypy`を独立実行するとTestコード1箇所で失敗する。Lightningへ一度だけまとめて搬入する前に直せる局所的な残件であるため、本Follow-upはMinor Changes Requestedとする。

また、Lightning Target上のPreflight、Python 3.12.11 Dependency Sync、CUDA／CPU Native Gateは未実行であり、Phase 1-F全体の完了はまだ宣言しない。

```text
前回High Finding解消       : 2／2
前回Medium Finding解消     : 2／2
前回Low Observation解消    : 1／1
新規Medium Finding         : 1
Default Test               : Pass／183 passed、3 deselected
Mac Model Smoke            : Pass／2 passed、1 skipped、1 deselected
Mac Strict Acceptance      : Pass／22 of 22 required checks
Full Project Mypy          : Fail／1 error
Lightning Preflight        : Not Run
Lightning CUDA Native Gate : Not Run
Lightning CPU Candidate    : Not Run
Final Decision             : Changes Requested／Minor Follow-up
Phase 1-F Completion       : Not Accepted Yet
```

## 2. 前回Findingの解消確認

### 2.1 Actual GPU Offload Evidence

`GpuOffloadEvidence`により、次が分離された。

```text
supported
requested
observed
observation_source
process_gpu_memory_bytes
```

- CUDAでは、Current Processの`nvidia-smi` GPU Memoryが正値の場合だけ`observed=true`となる。
- GPU使用を確認できない場合は、CUDA Buildや`gpu_layers=-1`だけを根拠にGPU Runtimeを主張せずFail Closedとなる。
- CPU Profileでは、Backend CapabilityとRuntime Request／Observationが分離される。
- Pre-load Environment Verifierは、未実行のActual Observationを成功扱いしない。
- Mac Metalでは、Model／Context Load成功後の`metal_model_load`がObservation Sourceとして記録される。

前回High Findingは解消した。

### 2.2 Acceptance ProbeのFail Closed

Acceptance Scriptは22件の必須条件を`required_checks`へ集約し、全件合格時だけ`all_required_checks_passed=true`とする。1件でも不合格、または予期しない例外があれば非0で終了する。

Setup Scriptも`set -euo pipefail`によりProbe失敗を成功扱いしない。前回High Findingは解消した。

### 2.3 Language／Thinking Evidence

- 日本語、英語、Streaming、Post-cancelで識別可能なMarkerを使用する。
- Resolved Language Policyと、Modelへ渡すSystem Messageの両方を検証する。
- Thinkingは正常なReasoning／Final分離、Complete Parse、`finish_reason != length`を必須とする。
- Hidden／VisibleはCanonical ContentとPresentation Contentを分けて検証する。
- Unclosed Thinkingの安全処理は正常系Acceptanceとは分離してUnit Testで維持する。

前回Medium Findingは解消した。

### 2.4 Lightning Environment Mode

`auto`、`studio-active`、`project-venv`の3 Modeが追加され、Lightning StudioのPersistent Active EnvironmentとProject-local Venvのどちらにも対応可能な構造になった。

大容量Upload前に単独実行可能なRead-only Preflightも追加された。Target実行結果はまだないが、Repository上の環境前提固定は解消した。

### 2.5 `nvcc`判定順

Native CUDA Rebuildが必要な場合だけ`nvcc`を要求する順序へ修正された。既存CUDA Build再利用とCPU Candidate確認を、不必要な`nvcc`必須判定で停止させない構造になった。

前回Low Observationは解消した。

## 3. 新規Finding

### 3.1 Medium: Full Project MypyがTestコードで失敗する

対象：

```text
tests/unit/inference/test_deployment_platform.py:698
```

独立実行結果：

```text
tests/unit/inference/test_deployment_platform.py:698: error:
Module "margpa_runtime_llm.adapters.model_backends.llama_cpp.runtime_detection"
does not explicitly export attribute "subprocess"  [attr-defined]
Found 1 error in 1 file
```

Testは、`runtime_detection_module.subprocess.run`をMonkeypatchしている。Runtime Moduleの非公開Import DetailへTestから到達する形になり、MypyのExplicit Package Base／Export規則に反する。

Required Follow-up：

- Testから非公開Module Memberへ到達しない形へ変更する。
- `subprocess.run`自体を適切にPatchするか、GPU Memory QueryのCommand Runner境界を注入可能にする。
- 修正後は限定対象ではなく、Project設定どおりのFull `mypy`を実行する。
- `ruff format --check`、`ruff check`、`pytest -q`も再確認する。

これはProduct Runtime FailureではなくTestのStatic Typing Failureであり、修正範囲も局所的である。ただしProjectの正式品質Gateが未合格であるため、Lightning搬入前に解消する。

## 4. Independent Verification

### 4.1 Static／Default Gate

```text
ruff format --check src scripts tests       : Pass／70 files
ruff check src scripts tests                : Pass
python -m compileall -q src scripts tests   : Pass
bash -n Lightning Setup／Preflight           : Pass
uv lock --check --offline                   : Pass／117 packages
pytest -q                                   : Pass／183 passed、3 deselected
Full Project mypy                           : Fail／1 error
```

### 4.2 Mac Native Gate

```text
pytest -q -m model_smoke tests/integration
Result: 2 passed、1 skipped、1 deselected
```

Mac実機ContextのStrict Phase 1-F Acceptance：

```text
success                         : true
all_required_checks_passed      : true
required_checks                 : 22／22 true
GPU Evidence                    : supported／requested／observed = true
GPU Observation Source          : metal_model_load
Japanese／English Evidence      : Pass
Stream／Cancel／Post-cancel      : Pass
Thinking Parse                  : complete
Thinking Finish                 : stop
Hidden／Visible Separation      : Pass
Unload                          : Pass
Load including SHA-512          : 約2.51秒
```

Sandbox内ではMetal Deviceを利用できないため、Native TestはSandbox外のMac実機Contextで実行した。結果は合格している。

## 5. User Accepted Setting Decisions

ユーザーは、次の変更機会からDefault Generation上限を次へ変更することを決定した。

```toml
[generation]
max_new_tokens = 2048
```

Current Repositoryはまだ`512`であり、本Follow-upではConfigが実装担当の変更Scope外だったため未反映である。現在のFindingに起因する不具合ではないが、忘失防止のため、Lightning搬入前の小規模Follow-upへ含める。

変更時は、Config既定値を前提とするTestも同時に更新する。Context上限、会話履歴、Guardrail導入後の負荷を見ながら、将来は再調整可能とする。

Thinking表示Labelの`高度推論`から`推論過程`等への変更は、Phase 1-GのUI／注記設計と合わせる後続事項とし、本Follow-upへ混在させない。

## 6. Acceptance Status

| Area | Result | Notes |
|---|---|---|
| 前回High Findings | Pass | 2件とも解消 |
| 前回Medium Findings | Pass | 2件とも解消 |
| 前回Low Observation | Pass | 1件解消 |
| Default Runtime Tests | Pass | 183 passed、3 deselected |
| Full Project Mypy | Fail | Test 1箇所のExport境界 |
| Mac 3.13／Metal Native | Pass | Model Smoke／Strict Acceptance |
| Python 3.12 Native | Pending | Lightningで実行予定 |
| Lightning Preflight | Pending | External Target未実行 |
| Lightning CUDA Mandatory Gate | Pending | External Target未実行 |
| Lightning CPU Candidate | Pending | Best Effort／未実行 |

## 7. Next Gate

大容量Uploadをなるべく一度にまとめる方針を維持し、次の順序とする。

```text
実装担当の小規模Repository Follow-up
  ├─ Full Mypy Failure修正
  ├─ generation.max_new_tokens既定値を2048へ変更
  ├─ 関連Test更新
  └─ Full Static／Default Gate再実行
        ↓
設計者役の短縮Follow-up Review
        ↓
Lightningへ小型Preflightだけ配置して実行
        ↓
Preflight合格後にSource／Modelを一度に搬入
        ↓
Lightning Python 3.12.11／CUDA Mandatory／CPU Candidate Gate
        ↓
後継Implementer Status
        ↓
Phase 1-F Final Review
```

Phase 1-G実装、Phase 1完了宣言、Backup、Phase 1-ex、Git、GitHub公開はまだ開始しない。

## 8. Authorization Boundary

本ReviewとIndex作成は、Source／Config／Tests／Scriptsの修正、Lightning操作、Upload、Model Download、Backup、Git、GitHub公開を許可しない。

実装担当は、ユーザーが本Reviewを渡してFollow-up開始を指示した後に、Section 3.1とSection 5の限定範囲を変更する。

## 9. Append-Only

既存文書を変更せず、新TimestampのReviewとして追加した。

<!-- SOURCE_END 54: docs/handoffs/designer_review_phase_1f_repository_follow_up_20260721003201.md -->

---

<!-- SOURCE_BEGIN 55: docs/handoffs/designer_review_phase_1g_cross_thread_cancel_follow_up_20260721164248.md -->

### Source 55: `docs/handoffs/designer_review_phase_1g_cross_thread_cancel_follow_up_20260721164248.md`

- History Target: `docs/project/phases/phase_1/history/handoffs/designer_review_phase_1g_cross_thread_cancel_follow_up_20260721164248.md`
- Source SHA-512: `28347e15bc6c04fc1852df89a5adb909606982b98eccfd23e28ba755af31999c4a4c55147b224f65dd26bd025de7ba006a7cff0c0c15bac08e121ab3f9ca85fb`
- Source Size: `8554` bytes

# Phase 1-G Cross-thread Cancel Follow-up 設計Review

- 文書ID: `designer_review_phase_1g_cross_thread_cancel_follow_up`
- 状態: `changes_requested_shutdown_cancel_follow_up`
- 作成日時: `2026-07-21 16:42:48 JST`
- 更新日時: `2026-07-21 16:42:48 JST`
- Snapshot: `20260721164248`
- 作成担当: 設計者役担当Task
- 対象: Phase 1-G Cross-thread Cancel Follow-upとPhase 1-G最終受入可否
- 正本言語: 日本語
- 実装報告: [implementer_status_phase_1g_cross_thread_cancel_follow_up_20260721150603.md](../history/handoffs/implementer_status_phase_1g_cross_thread_cancel_follow_up_20260721150603.md)
- 対象Handoff: [implementer_handoff_phase_1g_cross_thread_cancel_follow_up_20260721122621.md](../history/handoffs/implementer_handoff_phase_1g_cross_thread_cancel_follow_up_20260721122621.md)
- 前回Review: [designer_review_phase_1g_review_follow_up_20260721122621.md](../history/handoffs/designer_review_phase_1g_review_follow_up_20260721122621.md)
- 要件: [phase_1g_minimal_web_surface_requirements_20260721093952.md](../history/requirements/phase_1g_minimal_web_surface_requirements_20260721093952.md)
- Architecture: [phase_1g_minimal_web_surface_architecture_20260721093952.md](../history/architecture/phase_1g_minimal_web_surface_architecture_20260721093952.md)
- 追加Handoff: [implementer_handoff_phase_1g_shutdown_cancel_follow_up_20260721164248.md](../history/handoffs/implementer_handoff_phase_1g_shutdown_cancel_follow_up_20260721164248.md)
- 最新Index: [documentation_index_20260721164248.md](../history/documentation_index_20260721164248.md)
- supersedes: `designer_review_phase_1g_review_follow_up_20260721122621.md`

## 1. Review結論

SSE Consumer終了時のEvent Loop ThreadからProducer Thread上のNative Generatorを即時Closeする競合は解消した。

- Web Streaming Cleanupから`session.force_cancel()`が除去された。
- `request_cancel()`と`consumer_stopped`によるCooperative Cancelへ統一された。
- Native Streamの`cancel()`と`close()`はProducer Iteration Thread上で行われる。
- Timeout時にCross-thread Closeで成功を偽装せず、明示的Cleanup Failureとする。
- Thread-affine正常Cleanup、Timeout Safe Failure、Queue BackpressureのRegression Testが合格した。

ただし、`ConversationGenerationService.shutdown()`のTimeout EscalationにCross-thread `force_cancel()`が残っている。Active Generation中のWeb Runtime Shutdownで前回と同じ`ValueError: generator already executing`を独立再現した。

この例外により`WebRuntime.close()`のModel Close Callbackまで到達せず、FastAPI Lifespanは現在その例外を記録せずに抑制する。Phase 1-GのShutdown／Unload受入条件と整合しない。

したがってPhase 1-GはまだAcceptedとせず、Shutdown Cancelだけの追加局所Follow-upを要求する。

```text
SSE Disconnect Cross-thread Finding : Resolved
Queue Backpressure                   : Pass
Timeout Safe Failure                 : Pass
Targeted Web／Conversation Test     : Pass／30 passed
Default Regression                   : Pass／213 passed、3 deselected
Shutdown Cross-thread Cancel         : Fail／1 Mandatory Finding
Reviewer Native Model Smoke          : Inconclusive／2 failed、1 skipped
Final Decision                       : Changes Requested
Phase 1-H                            : Waiting Phase 1-G Acceptance
```

## 2. 解消確認

`src/margpa_runtime_llm/web/streaming.py`は次の順序になった。

```text
Event Loop Thread
  consumer_stopped.set()
  session.request_cancel()
  Queue Drain
  Producer TaskをAwait

Producer Thread
  Queue投入待ち解除、またはNative next()の次Chunk境界
  Cancel要求を観測
  Native Stream cancel／close
  Session finally
  Generation Gate解放
```

Thread-affine Blocking Streamにより、別Threadからの`cancel()`／`close()`を失敗させ、Producer Thread上のCancel／Close、Session／Gate解放、後続Generation、Timeout中のNative Call 0件を確認している。直接対象として適切なRegressionである。

## 3. Mandatory Finding

### 3.1 High: Runtime ShutdownにCross-thread `force_cancel()`が残存

対象：

- `src/margpa_runtime_llm/modules/conversation/application/conversation_generation.py:246-255`
- `src/margpa_runtime_llm/web/contracts.py:46-49`
- `src/margpa_runtime_llm/web/app.py:46-50`

Current Shutdownは次である。

```text
Web Lifespan Shutdown Worker Thread
  runtime.close()
  conversation.shutdown()
    request_cancel()
    session.wait(10 seconds)
    session.force_cancel()
      stream.cancel()
      native generator.close()
```

SSE Producer ThreadがNative Generatorの`next()`内にいる場合、Shutdown Worker Threadの`force_cancel()`はThread Affinityを破る。

Repositoryを変更しない一時診断結果：

```text
Iteration Thread ID       : 6106624000
Shutdown Thread ID        : 8525073536
shutdown result           : None
shutdown error            : ValueError: generator already executing
Cancel Thread at timeout  : Shutdown Thread

Native Boundary解放後
  Producer                : Finished
  Session                 : Finished
  Active Request          : None
```

Required Correction：

1. `shutdown()`からThread-unsafeな`session.force_cancel()`を呼ばない。
2. Shutdownも`request_cancel()`とProducer Thread上のCancel／Closeを正規経路とする。
3. Timeout時は`False`または明示例外とし、Session解放やModel Unload成功を偽装しない。
4. Backend保証のThread-safe Stop Signalが必要なら、Generator `close()`と分離したContractを先に設計Reviewへ戻す。
5. Runtime Shutdown FailureをLifespanが無記録で抑制しない。
6. Active Generation中ShutdownのThread-affine Regression Testを追加する。
7. Cleanup成功時はModel Close Callbackが正確に1回だけ呼ばれることをTestする。

## 4. Independent Verification

```text
ruff format --check src scripts tests     : Pass／88 files
ruff check src scripts tests              : Pass
mypy .                                    : Pass／88 source files
python -m compileall -q src scripts tests : Pass
pytest -q                                 : Pass／213 passed、3 deselected
Conversation／Web Targeted               : Pass／30 passed
uv lock --check --offline                 : Pass／122 packages
bash -n scripts/setup/*.sh                : Pass
```

`uv`はSandboxからUser Cacheを使えなかったため、書込可能な一時Cacheを指定してLock整合性を確認した。

### 4.1 Native Model Smoke

```text
Implementer Evidence : Pass／2 passed、1 skipped
Reviewer Run 1       : Fail／2 failed、1 skipped
Reviewer Run 2       : Fail／2 failed、1 skipped
Failure Point        : Model Load／llama_context creation
Error                : ValueError: Failed to create llama_context
```

Reviewer実行時、別のMARGPA／Python／Uvicorn／llama関連Processは確認されなかった。失敗はPhase 1-G Web差分の実行前に発生し、Current Follow-upのSource差分による失敗とは現時点で断定しない。Reviewer Native Gateは合格していないため、Shutdown Follow-up後の再Reviewで必ず再実行する。

## 5. Acceptance Matrix

| Area | Result | Notes |
|---|---|---|
| SSE Disconnect Cooperative Cancel | Pass | Cross-thread Close除去 |
| Queue Backpressure | Pass | Consumer終了後にProducer解放 |
| Cleanup Timeout | Pass | Unsafe Escalationなし |
| Thread-affine Regression | Pass | Cancel／CloseはProducer Thread |
| Static／Default Regression | Pass | 213 passed |
| Web Targeted | Pass | 30 passed |
| Active Generation Shutdown | Fail | Cross-thread `force_cancel()`再現 |
| Model Close Callback | Fail path present | Shutdown例外時に未到達 |
| Lifespan Failure Visibility | Fail | Shutdown例外を抑制 |
| Reviewer Native Model Smoke | Inconclusive | `llama_context` creation failure |

## 6. Next Gate

```text
実装担当 Phase 1-G Shutdown Cancel局所Follow-up
  ↓
設計者役 Phase 1-G Final Review
  ├─ Static／Default／Targeted
  ├─ Shutdown Diagnostic
  └─ Mac Native Model Smoke再実行
  ↓
Phase 1-G Accepted判定
  ↓
Phase 1-H Summary Mode
```

Phase 1-H、Lightning Full Upload、Phase 1完了宣言、Backup、Phase 1-ex、Git、GitHub公開はまだ開始しない。

## 7. Authorization Boundary

本Review、追加Handoff、Index作成はSource／Testsの修正、Lightning操作、Upload、Backup、Git、GitHub公開を許可しない。

## 8. Append-Only

既存文書を変更せず、新TimestampのReviewとして追加した。

<!-- SOURCE_END 55: docs/handoffs/designer_review_phase_1g_cross_thread_cancel_follow_up_20260721164248.md -->

---

<!-- SOURCE_BEGIN 56: docs/handoffs/designer_review_phase_1g_minimal_web_surface_20260721115330.md -->

### Source 56: `docs/handoffs/designer_review_phase_1g_minimal_web_surface_20260721115330.md`

- History Target: `docs/project/phases/phase_1/history/handoffs/designer_review_phase_1g_minimal_web_surface_20260721115330.md`
- Source SHA-512: `bebeef0a22585bf3f20f1c3c4c8d30d0e255fb0b50f3f6c8ee8a0084360fe713c186bbf76f7fba9dc36c6564f24a141fbaee6ec9e72c9698a7ec683aa47d3026`
- Source Size: `12441` bytes

# Phase 1-G Minimal Web Surface 設計Review

- 文書ID: `designer_review_phase_1g_minimal_web_surface`
- 状態: `changes_requested_before_phase_1h`
- 作成日時: `2026-07-21 11:53:30 JST`
- 更新日時: `2026-07-21 11:53:30 JST`
- Snapshot: `20260721115330`
- 作成担当: 設計者役担当Task
- 対象: Phase 1-G Repository実装、Web Surface、Security、Streaming、Manual Evidence
- 正本言語: 日本語
- 実装報告: [implementer_status_phase_1g_minimal_web_surface_20260721105005.md](../history/handoffs/implementer_status_phase_1g_minimal_web_surface_20260721105005.md)
- 要件: [phase_1g_minimal_web_surface_requirements_20260721093952.md](../history/requirements/phase_1g_minimal_web_surface_requirements_20260721093952.md)
- Architecture: [phase_1g_minimal_web_surface_architecture_20260721093952.md](../history/architecture/phase_1g_minimal_web_surface_architecture_20260721093952.md)
- Follow-up Handoff: [implementer_handoff_phase_1g_review_follow_up_20260721115330.md](../history/handoffs/implementer_handoff_phase_1g_review_follow_up_20260721115330.md)
- 最新Index: [documentation_index_20260721115330.md](../history/documentation_index_20260721115330.md)
- supersedes: なし（Phase 1-G Review系列の初回）

## 1. Review結論

Phase 1-Gは、Framework境界、Browser所有のEphemeral Conversation、Request単位の3設定、Model Lifecycle、Basic Auth、Safe Rendering、SSE Contract、既存CLI非回帰の大部分で要件に沿っている。

Static／Default／Web／Mac Native Model Smokeはすべて合格した。実装報告の主要Evidenceも独立検証と一致している。

ただし、次のMandatory項目に未解消Findingがあるため、現時点ではPhase 1-Gを受け入れず、Phase 1-Hへ進めない。

```text
High Finding                 : 1
Medium Finding               : 2
Low Observation              : 2
Static／Default Gate          : Pass
Web Targeted Test            : Pass／26 passed
Mac Native Model Smoke       : Pass／2 passed、1 skipped
Manual Browser Smoke         : Broad Pass／Evidence補完1件
Final Decision               : Changes Requested
Phase 1-H                    : Waiting Follow-up Review
```

必須Follow-upは次の3系統である。

1. Bounded Queueが満杯の状態でも、Client Disconnect後にProducerとGeneration Gateを確実に解放する。
2. Final Answer前Token Exhaustion Warningを、`completed` Eventで上書きせず画面へ明示する。
3. User-visible UIを含むSource内の廃止済み第一者名義を`Nazuna Research`へ統一する。

## 2. Positive Findings

次は設計と実装の両方で成立している。

- FastAPI／UvicornはDelivery AdapterとEntrypointへ局所化され、Inference／Presentation Coreへ侵入していない。
- Browser TabがCanonical `user／assistant` Historyを所有し、Serverは会話を永続保存または利用者間共有しない。
- Client指定の`system／tool` Role、不正順序、空Message、不正SettingをTyped Contractで拒否する。
- UI設定は`response_language`、`max_new_tokens`、`thinking_visibility`の3項目だけである。
- Request OverrideはTracked TOMLを書き換えず、Thinking VisibilityとThinking Executionを分離している。
- ModelはLifespanで1回Load／1回Unloadされ、同時Generationは409でFail Fastする。
- Hidden ThinkingはSSE DeltaとCanonical Assistant Historyへ混入しない。
- Basic AuthはServer側、Environment-only、Constant-time Compareであり、Non-loopback＋Auth DisabledはFail Closedになる。
- `/healthz`以外のUI、Asset、APIが同一認証境界にあり、Interactive API Docsは無効である。
- Model Outputは`textContent`で描画し、External Script／CDN／Fontや`innerHTML`を使用していない。
- CSP、`no-store`、`nosniff`、`no-referrer`を設定している。
- Phase 1-H Summary Mode Controlを先行表示していない。
- Current CLI、Config、Model Port、llama.cpp Adapterの既存Contractを破壊していない。

## 3. Findings

### 3.1 High: Backpressure中のDisconnectでProducerとGeneration Gateが残留し得る

対象：

- `src/margpa_runtime_llm/web/streaming.py:29-57`
- `tests/integration/web/test_web_app.py:377-414`

同期Model IteratorからAsync SSEへ渡すQueueは`maxsize=32`である。Producer Threadは各Eventを次の処理でQueueへ投入し、完了まで同期的に待つ。

```text
run_coroutine_threadsafe(queue.put(event), loop).result()
```

Client側Consumerが終了し、Queueが満杯の場合、Producerは`queue.put`で停止する。Async Generatorの`finally`はCancel要求後にProducerを最大10秒待ち、Timeout時に`session.force_cancel()`を呼ぶが、QueueをDrainせずProducerを再度待たない。

このため、Native StreamへCancelを設定しても、ProducerはNative Iteratorへ戻れずQueue投入待ちのまま残り得る。`ConversationGenerationSession.events()`の`finally`へ到達しなければ、Active SessionとGeneration Gateも解放されない。

既存Disconnect Testは2 Chunkだけを生成し、Async Generatorを最後までDrainしているため、Queue Capacity超過とConsumer早期終了を再現していない。

これは次のMandatory要件に反する。

- LockはTerminal／Error／Disconnectの全経路でReleaseする。
- Browser Disconnect時にNative GenerationをCancelする。
- Cancel後のGenerationを成立させる。
- UI側の受信遅延でModel Generationを恒久Blockしない。

Required Follow-up：

- Consumer終了をProducerへ伝えるCancellation／Stop Signalを設ける。
- Disconnect後もProducerがQueue投入待ちから脱出し、Session IteratorをCloseできる構造にする。
- Cleanup完了前にGeneration Gate解放を成功扱いしない。
- Queue Capacityを超えるEvent列でConsumerを早期CloseするRegression Testを追加する。
- Testは限定時間内のProducer終了、`active_request_id is None`、次Generation成功、Orphan Task／Thread不在を確認する。

### 3.2 Medium: Token Exhaustion Warningが直後のCompleted表示で消える

対象：

- `src/margpa_runtime_llm/web/static/app.js:138-153`
- `src/margpa_runtime_llm/modules/conversation/application/conversation_generation.py:132-153`
- `tests/unit/conversation/test_conversation_generation.py:286-287`

Serverは`finish_reason=length`かつCanonical Finalが空の場合、次を正しく送信する。

```text
code    : final_answer_token_limit
message : 最終回答を生成する前にToken上限へ到達しました。
```

しかしBrowserは`warning` EventでStatusを設定した直後、後続`completed` EventでStatusを`完了 (length)`へ上書きする。Canonical Finalが空の場合はPending UserをRollbackするだけで、Assistant表示Nodeも空のまま残る。

したがって、Server Contractは成立しているが、User-visible Acceptanceでは「空Responseにならず明示される」が成立しない。現在の自動TestはServer Warning生成だけを確認し、Browser Event適用後の最終表示を検証していない。

Required Follow-up：

- `final_answer_token_limit`をRequest単位で保持し、後続`completed`で上書きしない。
- Canonical Finalが空でも、正本MessageをAssistant Historyへ混入させず、画面上には上記Safe Warningを明示する。
- 空Assistant Bubbleだけを残さない。
- Browser Event列`warning → completed`後の最終表示をRegression Testまたは同等の決定論的検証で固定する。

### 3.3 Medium: Source内に廃止済み第一者名義が2箇所残っている

対象：

- `src/margpa_runtime_llm/__init__.py:1`
- `src/margpa_runtime_llm/web/static/index.html:14`

前者はPackage Docstring、後者はWeb UIへ直接表示されるEyebrowである。Current Mandatory Ruleは、第一者の作者・研究・表示名を`Nazuna Research`へ統一し、現時点で例外を認めていない。

Required Follow-up：

- 両方を`Nazuna Research Governance LLM`へ統一する。
- `src／tests／scripts／config／Root Metadata`を再検索し、廃止済み第一者名義が0件であることをEvidence化する。
- Third-party Provenance、Model Author、Dependency Authorまで誤置換しない。

## 4. Low Observations

### 4.1 Request Byte Limitは`Content-Length`へ依存する

`MAX_CHAT_REQUEST_BYTES`の事前拒否は`Content-Length` Headerがある場合だけ行われる。Header省略／Chunked Bodyでは、PydanticのMessage／文字数上限により意味的には拒否されるが、ASGIがBodyを受理する前の厳密なByte上限にはならない。

少人数PreviewのPhase 1-G Acceptanceを単独で止めるFindingにはしない。Public Hardening時には、信頼できるReverse ProxyのRequest Size LimitまたはASGI側の実Body上限を明示する。

### 4.2 Browser Manual Evidenceに`auto`の明示結果がない

実装報告は日本語Defaultと`en`を記録しているが、Browser UIで`auto`を選択した結果を個別に記録していない。Contract上は`ja／en／auto`を受理し、既存Language Composerを再利用している。

Follow-up Manual Smokeで`auto`を1回実行し、受理、Streaming、最終回答までのEvidenceを補完する。

## 5. Independent Verification

### 5.1 Static／Default／Web Gate

```text
ruff format --check src scripts tests             : Pass／88 files
ruff check src scripts tests                      : Pass
mypy .                                            : Pass／88 source files
python -m compileall -q src scripts tests         : Pass
bash -n Mac／Lightning Setup／Preflight            : Pass
pytest -q                                         : Pass／209 passed、3 deselected
Conversation／Web Targeted Test                   : Pass／26 passed
uv lock --check --offline                         : Pass／122 packages
```

Sandbox内の`uv lock`は共有uv CacheへのAccess制限でExit 2となった。Repository／Lock Failureではないため、通常ホスト環境で同一Commandを再実行しExit 0を確認した。

### 5.2 Mac Native Model Smoke

```text
pytest -q -m model_smoke
Result : 2 passed、1 skipped、209 deselected
Skip   : Lightning Profile Environment未指定
```

Sandbox内ではMetal Contextを作成できず2件失敗した。通常Mac／Metal環境で同一Commandを再実行し2件合格したため、Product Runtime Failureとは扱わない。

### 5.3 Identity Search

```text
Search Scope : src／tests／scripts／config／pyproject.toml／uv.lock
Match        : 2
Location     : Package Docstring 1、Web UI 1
Result       : Follow-up Required
```

## 6. Acceptance Status

| Area | Result | Notes |
|---|---|---|
| Dependency／Lock | Pass | 122 packages |
| Static／Default Test | Pass | 209 passed、3 deselected |
| Mac Model Smoke | Pass | 2 passed、1 skipped |
| Web Architecture Boundary | Pass | Framework局所化 |
| Conversation Isolation | Pass | Browser-owned／Server non-persistent |
| Settings 3項目 | Pass | Request Overrideのみ |
| Preview Access Control | Pass | Non-loopback Fail Closed |
| Output Rendering | Pass | Plain Text／Local Assets |
| Normal Stop／Post-cancel | Pass | Current短いStream条件 |
| Backpressured Disconnect | Fail | Producer／Gate残留経路 |
| Token Exhaustion UI | Fail | WarningがCompletedで上書き |
| Public Naming | Fail | Source 2件 |
| Browser `auto` Evidence | Pending | Follow-up Manual Smoke |

## 7. Next Gate

```text
実装担当 Phase 1-G Follow-up
  ├─ Disconnect／Backpressure Cleanup
  ├─ Token Exhaustion UI Warning保持
  ├─ Source表示名2件統一
  ├─ Regression Test追加
  └─ Browser auto／Warning Manual Smoke
        ↓
設計者役 Phase 1-G Follow-up Review
        ↓
Phase 1-G Accepted判定
        ↓
Phase 1-H Summary Mode
```

Phase 1-H、Lightning Full Upload、Phase 1完了宣言、Backup、Phase 1-ex、Git、GitHub公開はまだ開始しない。

## 8. Authorization Boundary

本Review、Follow-up Handoff、Indexの作成は、Source／Config／Tests／Scriptsの修正、Lightning操作、Upload、Backup、Git、GitHub公開を許可しない。

実装担当は、ユーザーがFollow-up開始を明示的に指示した後、Follow-up Handoffの限定範囲を変更する。

## 9. Append-Only

既存文書を変更せず、新TimestampのReviewとして追加した。

<!-- SOURCE_END 56: docs/handoffs/designer_review_phase_1g_minimal_web_surface_20260721115330.md -->

---

<!-- SOURCE_BEGIN 57: docs/handoffs/designer_review_phase_1g_review_follow_up_20260721122621.md -->

### Source 57: `docs/handoffs/designer_review_phase_1g_review_follow_up_20260721122621.md`

- History Target: `docs/project/phases/phase_1/history/handoffs/designer_review_phase_1g_review_follow_up_20260721122621.md`
- Source SHA-512: `4a63412b18892db1d54f728e1180aea550098c7e33e18fd8f78651cee0b37e7b817c07d0e0ac858819bb8451c40a70b1c375eb9e4ab4b486ecd837d48539cede`
- Source Size: `10552` bytes

# Phase 1-G Review Follow-up 設計Review

- 文書ID: `designer_review_phase_1g_review_follow_up`
- 状態: `changes_requested_cross_thread_cancel_follow_up`
- 作成日時: `2026-07-21 12:26:21 JST`
- 更新日時: `2026-07-21 12:26:21 JST`
- Snapshot: `20260721122621`
- 作成担当: 設計者役担当Task
- 対象: Phase 1-G Review Follow-up実装と最終受入可否
- 正本言語: 日本語
- 実装報告: [implementer_status_phase_1g_review_follow_up_20260721121817.md](../history/handoffs/implementer_status_phase_1g_review_follow_up_20260721121817.md)
- 前回Review: [designer_review_phase_1g_minimal_web_surface_20260721115330.md](../history/handoffs/designer_review_phase_1g_minimal_web_surface_20260721115330.md)
- 前回Handoff: [implementer_handoff_phase_1g_review_follow_up_20260721115330.md](../history/handoffs/implementer_handoff_phase_1g_review_follow_up_20260721115330.md)
- 要件: [phase_1g_minimal_web_surface_requirements_20260721093952.md](../history/requirements/phase_1g_minimal_web_surface_requirements_20260721093952.md)
- Architecture: [phase_1g_minimal_web_surface_architecture_20260721093952.md](../history/architecture/phase_1g_minimal_web_surface_architecture_20260721093952.md)
- 追加Handoff: [implementer_handoff_phase_1g_cross_thread_cancel_follow_up_20260721122621.md](../history/handoffs/implementer_handoff_phase_1g_cross_thread_cancel_follow_up_20260721122621.md)
- 最新Index: [documentation_index_20260721122621.md](../history/documentation_index_20260721122621.md)
- supersedes: `designer_review_phase_1g_minimal_web_surface_20260721115330.md`

## 1. Review結論

前回ReviewのMandatory Finding 3系統は、要求どおりFollow-upされている。

- Bounded Queue満杯時にProducerがQueue投入待ちから脱出し、Session Gateを解放するTestが追加された。
- Final Answer前Token Exhaustion Warningは、`completed`後もStatusとAssistant Bubbleへ残る。
- Warning TextはCanonical Assistant Historyへ追加されない。
- 第一者表示名は`Nazuna Research`へ統一され、対象Scopeの廃止済み名義検索は0件である。
- Browser `auto`、Warning、Stop、Post-cancelのManual Evidenceも補完された。

Static／Default／Web／Mac Native Model Smokeはすべて合格した。

ただし、Web CleanupがEvent Loop ThreadからNative Streamへ即時`force_cancel()`するよう変更され、Native Python Generatorが別Threadで`next()`実行中の場合に`ValueError: generator already executing`となる競合を独立再現した。

Disconnect CleanupのMandatory条件を全Timingで満たさないため、Phase 1-Gは現時点でもAcceptedにせず、Cross-thread Cancelだけの局所Follow-upを要求する。

```text
前回High Finding解消       : 1／1／元のQueue詰まり経路
前回Medium Finding解消     : 2／2
前回Low Evidence補完       : 1／1
新規High Finding           : 1
Static／Default Gate        : Pass／211 passed、3 deselected
Web Targeted Test          : Pass／28 passed
Mac Native Model Smoke     : Pass／2 passed、1 skipped
Final Decision             : Changes Requested／One Local Follow-up
Phase 1-H                  : Waiting Phase 1-G Final Review
```

## 2. 前回Findingの解消確認

### 2.1 Queue Backpressure

`consumer_stopped`と50ms Pollingにより、Queue Capacityを超えた投入待ちはConsumer終了後に解除される。Producer側でSession Iteratorを`close()`し、Session `finally`とGeneration Gate解放へ到達する。

96 Chunk、最初の`start`だけConsumerが取得、Queue Capacity超過後にAsync GeneratorをCloseするRegression Testで、次を確認している。

- Native Fake Stream Cancel
- Session完了
- Active Request解除
- Producer Task終了
- 直後の次Generation完了

元の「Queue満杯のためProducerが永久に`queue.put`待ちになる」Findingは解消した。

### 2.2 Token Exhaustion UI

Browserは`final_answer_token_limit`をRequest単位で保持し、後続`completed`でWarning Statusを上書きしない。Canonical Finalが空の場合、Safe WarningをAssistant Bubbleへ表示し、Canonical Historyへ追加しない。

Mac Manual Browser Smokeでも、StatusとBubbleの両方へWarningが残り、空Bubbleが0件であることが確認されている。

前回Medium Findingは解消した。

### 2.3 Public Naming

Package DocstringとWeb UIは`Nazuna Research Governance LLM`へ統一された。

```text
Search Scope : src／tests／scripts／config／pyproject.toml／uv.lock
Match        : 0
Result       : Pass
```

前回Medium Findingは解消した。

### 2.4 Browser `auto` Evidence

実Model／Metal／Browserで`response_language=auto`のStreamingとCanonical Finalが成立した。前回Low Evidence Gapは補完された。

## 3. New Finding

### 3.1 High: Event Loop Threadから実行中Native GeneratorをCloseする競合

対象：

- `src/margpa_runtime_llm/web/streaming.py:87-107`
- `src/margpa_runtime_llm/modules/conversation/application/conversation_generation.py:81-84`
- `src/margpa_runtime_llm/adapters/model_backends/llama_cpp/stream.py:129-155`
- `tests/integration/web/test_web_app.py:461-521`

Consumer終了時、Web Cleanupは次の順序で処理する。

```text
consumer_stopped.set()
session.request_cancel()
session.force_cancel()
  → LlamaCppGenerationStream.cancel()
  → native_stream.close()
```

Producerは`asyncio.to_thread()`上でNative Iteratorを消費する。Client Disconnectが、Producer ThreadでNative Generatorの`next()`実行中に発生した場合、Event Loop Threadから同じGeneratorへ`close()`することになる。

Python Generatorは実行中に別Threadから`close()`できない。Production `LlamaCppGenerationStream`と、Token生成中を模したBlocking Native Generatorで独立診断した結果は次である。

```text
Cross-thread cancel : ValueError: generator already executing
Terminal callback   : force_cancel時点では未実行
```

`stream_session_as_sse()`の`finally`では、最初の`session.force_cancel()`がProducer待機を囲む`try`より前にある。この例外によりQueue DrainとProducer Awaitを開始せずCleanupから離脱する。

既存Regression Testの`FakeStream.cancel()`はBooleanを変更するだけで、Python GeneratorのThread Affinityを再現しない。そのため28件のWeb Testは合格しても、この競合を検出できない。

実ModelのManual Stopが一度成功していても、Disconnect Timing依存のためFindingは解消しない。

Required Follow-up：

1. Event Loop Threadから、実行中Native Python Generatorを直接`close()`しない。
2. Normal Disconnectは`session.request_cancel()`を第一段とし、Producer Threadが次Chunk境界でCancel／Closeする。
3. `consumer_stopped`によりQueue待ちは解除済みであるため、Producer Thread自身の`events.close()`をCleanupの正規経路にする。
4. Timeout Escalationでも、Thread-unsafeな`native_stream.close()`を成功前提にしない。
5. Native Cancelを別Threadから安全に行う必要がある場合は、Generator `close()`ではなくBackendが保証するThread-safe Stop Signal／Stopping Criteria境界を使用する。
6. `cancel()`がIteration Thread以外から呼ばれた場合に失敗するThread-affine Fake StreamまたはProduction Wrapperを使い、早期Close後のGate解放と次GenerationをTestする。
7. Cleanup中の例外を黙って成功扱いせず、Producer終了とGate解放を確認する。

最小修正候補は、Web Cleanupの即時`force_cancel()`を除去し、Cooperative CancelとProducer Thread上のCloseを正規経路にすることである。実装方式の最終判断は実装担当へ委ねるが、Cross-thread Generator Closeを残してはならない。

## 4. Independent Verification

### 4.1 Static／Default／Web Gate

```text
ruff format --check src scripts tests             : Pass／88 files
ruff check src scripts tests                      : Pass
mypy .                                            : Pass／88 source files
python -m compileall -q src scripts tests         : Pass
bash -n Setup Scripts                             : Pass
pytest -q                                         : Pass／211 passed、3 deselected
Conversation／Web Targeted Test                   : Pass／28 passed
uv lock --check --offline                         : Pass／122 packages
Public Naming Search                              : Pass／0 match
```

### 4.2 Mac Native Model Smoke

```text
pytest -q -m model_smoke
Result : 2 passed、1 skipped、211 deselected
Skip   : Lightning Profile Environment未指定
```

通常Mac／Metal環境で実行し、合格した。

### 4.3 Cross-thread Cancel Diagnostic

Repository Fileを変更せず、一時診断ScriptでProduction `LlamaCppGenerationStream`を使用した。

```text
Producer Thread : native generatorのnext()実行中
Main Thread     : stream.cancel()
Result          : ValueError: generator already executing
```

これはTest-only Fakeの挙動ではなく、Current Production Wrapperの挙動である。

## 5. Acceptance Status

| Area | Result | Notes |
|---|---|---|
| 前回Queue Backpressure | Pass | 元のQueue投入待ちは解消 |
| Token Exhaustion UI | Pass | Warning保持／History非追加 |
| Public Naming | Pass | 対象Scope 0 match |
| Browser `auto` Evidence | Pass | Manual Smoke補完 |
| Static／Default Test | Pass | 211 passed、3 deselected |
| Web Targeted Test | Pass | 28 passed |
| Mac Native Model Smoke | Pass | 2 passed、1 skipped |
| Cross-thread Native Cancel | Fail | 実行中Generator CloseでValueError |
| Disconnect Cleanup全Timing | Fail | Producer Await前に例外離脱可能 |

## 6. Next Gate

```text
実装担当 Cross-thread Cancel局所Follow-up
  ├─ Thread-affine Cooperative Cancel
  ├─ Producer Thread上のClose
  ├─ Timeout時のSafe Failure
  └─ Thread-affine Regression Test
        ↓
設計者役 Phase 1-G Final Review
        ↓
Phase 1-G Accepted判定
        ↓
Phase 1-H Summary Mode
```

Phase 1-H、Lightning Full Upload、Phase 1完了宣言、Backup、Phase 1-ex、Git、GitHub公開はまだ開始しない。

## 7. Authorization Boundary

本Review、追加Handoff、Index作成は、Source／Testsの修正、Lightning操作、Upload、Backup、Git、GitHub公開を許可しない。

実装担当は、ユーザーが追加Follow-up開始を明示した後、追加Handoffの限定範囲を変更する。

## 8. Append-Only

既存文書を変更せず、新TimestampのReviewとして追加した。

<!-- SOURCE_END 57: docs/handoffs/designer_review_phase_1g_review_follow_up_20260721122621.md -->

---

<!-- SOURCE_BEGIN 58: docs/handoffs/designer_review_phase_1g_shutdown_cancel_follow_up_20260721172916.md -->

### Source 58: `docs/handoffs/designer_review_phase_1g_shutdown_cancel_follow_up_20260721172916.md`

- History Target: `docs/project/phases/phase_1/history/handoffs/designer_review_phase_1g_shutdown_cancel_follow_up_20260721172916.md`
- Source SHA-512: `d425787e21a215469facd46ece20ae45497b93e1660c8e4ec04e49ae46141abcb7be95ecbf41c62773b8e895b4d129fb3bed8ff04fdfeedeecdf91e4254a62a8`
- Source Size: `7141` bytes

# Phase 1-G Shutdown Cancel Follow-up 設計Review

- 文書ID: `designer_review_phase_1g_shutdown_cancel_follow_up`
- 状態: `accepted_with_non_blocking_environment_observation`
- 作成日時: `2026-07-21 17:29:16 JST`
- 更新日時: `2026-07-21 17:29:16 JST`
- Snapshot: `20260721172916`
- 作成担当: 設計者役担当Task
- 対象: Phase 1-G Shutdown Cancel Follow-upとPhase 1-G最終受入可否
- 正本言語: 日本語
- 実装報告: [implementer_status_phase_1g_shutdown_cancel_follow_up_20260721172039.md](../history/handoffs/implementer_status_phase_1g_shutdown_cancel_follow_up_20260721172039.md)
- 対象Handoff: [implementer_handoff_phase_1g_shutdown_cancel_follow_up_20260721164248.md](../history/handoffs/implementer_handoff_phase_1g_shutdown_cancel_follow_up_20260721164248.md)
- 前回Review: [designer_review_phase_1g_cross_thread_cancel_follow_up_20260721164248.md](../history/handoffs/designer_review_phase_1g_cross_thread_cancel_follow_up_20260721164248.md)
- 要件: [phase_1g_minimal_web_surface_requirements_20260721093952.md](../history/requirements/phase_1g_minimal_web_surface_requirements_20260721093952.md)
- Architecture: [phase_1g_minimal_web_surface_architecture_20260721093952.md](../history/architecture/phase_1g_minimal_web_surface_architecture_20260721093952.md)
- 最新Index: [documentation_index_20260721172916.md](../history/documentation_index_20260721172916.md)
- supersedes: `designer_review_phase_1g_cross_thread_cancel_follow_up_20260721164248.md`

## 1. Review結論

Phase 1-G Shutdown Cancel Follow-upは要求どおり実装され、前回のMandatory Findingは解消した。

```text
SSE Consumer Cross-thread Cancel : Resolved
Runtime Shutdown Cross-thread    : Resolved
Timeout State Falsification      : Resolved
Model Close Callback             : Pass／Exactly Once after Success
Lifespan Failure Visibility      : Pass／Sanitized and Propagated
Static／Default Regression       : Pass／215 passed、3 deselected
Web／Conversation Targeted       : Pass／32 passed
Implementer Native Model Smoke   : Pass／2 passed、1 skipped
Reviewer Native Model Smoke      : Environment Failure／2 failed、1 skipped
Final Decision                   : Phase 1-G Accepted
Next Phase                       : Phase 1-H Requirements／Design
```

Reviewer Native Model Smokeは`llama_context` creationで再度失敗したが、Phase 1-G変更経路に入る前のModel Loadである。実装担当の同一Snapshotでは2件合格し、実ModelのShutdown／Restart／後続Generationも成立している。このためSource Findingとせず、Phase 1全体の最終User Gateで再実行する非ブロッカー環境観察とする。

## 2. Mandatory Finding解消

### 2.1 Cooperative Shutdown

`ConversationGenerationService.shutdown()`は次のみを行う。

```text
session.request_cancel()
session.wait(timeout)
  ├─ Finished → True
  └─ Timeout  → False
```

Timeout後の`session.force_cancel()`は除去された。Native Streamの`cancel()`／`close()`はProducer Iteration Threadが次Chunk境界でCancel要求を観測した後に行う。

### 2.2 Timeout State

Native `next()`がTimeout内に復帰しない場合：

- `shutdown()`は`False`を返す。
- `WebRuntime.close()`は固定された安全な`RuntimeError`とする。
- Active Sessionと`active_request_id`を維持する。
- Model Close Callbackを呼ばない。
- Shutdown ThreadからNative Cancel／Closeを呼ばない。

Native Boundary解放後はProducer Thread上でCancel／Closeし、Session／Generation Gateを解放する。

### 2.3 Model Close Idempotency

`WebRuntime.close()`はLockと成功Stateを持つ。

```text
Active Session Timeout     : Callback 0
Session終了後の初回Close : Callback 1
2回目以降                  : Callback追加0
```

### 2.4 Lifespan Failure Visibility

Runtime Close Failureを無記録で抑制する経路は除去された。Operator Logと伝播例外は次の固定Messageだけを使う。

```text
The web runtime could not shut down cleanly.
```

Private Text、Absolute Path、Raw ExceptionをLog／伝播例外へ含めないRegressionが合格した。

## 3. Regression Coverage

`tests/integration/web/test_web_app.py`は次を直接確認する。

- Active Generation中の別Shutdown Thread
- Native `next()` Blocking中のTimeout
- Shutdown ThreadからのCancel／Close 0件
- Active RequestとModel Callbackの非偽装
- Native Boundary解放後のProducer Thread Cancel／Close
- Session／Gate解放と後続Generation
- Runtime Close 2回に対するCallback合計1回
- Lifespan FailureのSanitized Log／Exception

既存のSSE Thread-affine、Queue Backpressure、Cleanup Timeout Testも継続合格している。

## 4. Independent Verification

```text
ruff format --check src scripts tests     : Pass／88 files
ruff check src scripts tests              : Pass
mypy .                                    : Pass／88 source files
python -m compileall -q src scripts tests : Pass
pytest -q                                 : Pass／215 passed、3 deselected
Conversation／Web Targeted               : Pass／32 passed
uv lock --check --offline                 : Pass／122 packages
bash -n scripts/setup/*.sh                : Pass
```

### Native Model Evidence

```text
Implementer Automated : 2 passed、1 skipped
Implementer Manual    : Active Shutdown、Stop、Restart、RESTARTED. Generation Pass
Reviewer Automated    : 2 failed、1 skipped
Reviewer Failure      : Failed to create llama_context
Related Runtime       : 別MARGPA／Python／Uvicorn／llama常駐なし
```

Reviewer失敗時のUnified Memoryは圧縮Pageを多く保持していた。原因は未確定であり、SnapshotのSource不具合と断定しない。Phase 1完了に必要なUser Testで再確認する。

## 5. Non-blocking Observation

`ConversationGenerationSession.force_cancel()`のMethod定義自体は公開Session Surfaceに残るが、Current `src/margpa_runtime_llm/`からの呼出しは0件である。

現行LifecycleはすべてCooperative Cancelだが、将来のAgent／Backend／並行実行拡張前に次のいずれかを行う。

- `force_cancel()`を削除または非公開化する。
- Backendが保証するThread-safe Stop Signal Contractとして再設計する。

現在のPhase 1-G実行経路に危険なCallerがないため、これはAcceptance Blockerとしない。

## 6. Acceptance Status

| Area | Result |
|---|---|
| Minimal Web Surface | Accepted |
| Conversation Isolation | Accepted |
| Settings 3項目 | Accepted |
| SSE Streaming／Stop | Accepted |
| Disconnect／Backpressure Cleanup | Accepted |
| Shutdown／Restart | Accepted |
| Token Exhaustion Warning | Accepted |
| Preview Access Control | Accepted |
| Safe Shutdown Failure | Accepted |
| Phase 1-G Overall | Accepted |

## 7. Next Gate

Phase 1-Gは完了し、Phase 1-H Summary Modeの要件定義／設計へ進める。

ただしPhase 1-H実装、Lightning Full Upload、Phase 1完了宣言、Backup、Phase 1-ex、Git、GitHub公開は本Reviewだけで自動許可しない。

## 8. Append-Only

既存Reviewを変更せず、新TimestampのAccepted Reviewとして追加した。

<!-- SOURCE_END 58: docs/handoffs/designer_review_phase_1g_shutdown_cancel_follow_up_20260721172916.md -->

---

<!-- SOURCE_BEGIN 59: docs/handoffs/designer_review_phase_1h_review_follow_up_20260721184140.md -->

### Source 59: `docs/handoffs/designer_review_phase_1h_review_follow_up_20260721184140.md`

- History Target: `docs/project/phases/phase_1/history/handoffs/designer_review_phase_1h_review_follow_up_20260721184140.md`
- Source SHA-512: `dbadacb7f0ac24d9072f1e39a671098175c5224d623e69f97a29127f75c4482969b1904ad6c3fa01f4e53ff4e43096c2001a0b94c4d4d5d8cff4194dd11fe96e`
- Source Size: `9859` bytes

# Phase 1-H Review Follow-up 設計Review

- 文書ID: `designer_review_phase_1h_review_follow_up`
- 状態: `accepted_with_non_blocking_observations`
- 作成日時: `2026-07-21 18:41:40 JST`
- 更新日時: `2026-07-21 18:41:40 JST`
- Snapshot: `20260721184140`
- 作成担当: 設計者役担当Task
- 対象: Phase 1-H Review Follow-upおよびPhase 1-H最終受入可否
- 正本言語: 日本語
- 実装報告: [implementer_status_phase_1h_review_follow_up_20260721183457.md](../history/handoffs/implementer_status_phase_1h_review_follow_up_20260721183457.md)
- Follow-up Handoff: [implementer_handoff_phase_1h_review_follow_up_20260721182416.md](../history/handoffs/implementer_handoff_phase_1h_review_follow_up_20260721182416.md)
- 前回Review: [designer_review_phase_1h_summary_mode_and_ui_language_20260721182038.md](../history/handoffs/designer_review_phase_1h_summary_mode_and_ui_language_20260721182038.md)
- Requirements: [phase_1h_summary_mode_and_ui_language_requirements_20260721174346.md](../history/requirements/phase_1h_summary_mode_and_ui_language_requirements_20260721174346.md)
- Architecture: [phase_1h_summary_mode_and_ui_language_architecture_20260721174346.md](../history/architecture/phase_1h_summary_mode_and_ui_language_architecture_20260721174346.md)
- ADR: [adr_0020_phase_1h_summary_pipeline_and_ui_language_separation_20260721174346.md](../history/adr/adr_0020_phase_1h_summary_pipeline_and_ui_language_separation_20260721174346.md)
- Latest Index: [documentation_index_20260721184140.md](../history/documentation_index_20260721184140.md)
- supersedes: `designer_review_phase_1h_summary_mode_and_ui_language_20260721182038.md`

## 1. Review結論

前回の4 Mandatory Findingはすべて解消した。追加RegressionとMac Metal実Modelを含む独立検証も合格したため、Phase 1-H Summary Mode／UI LanguageをAcceptedとする。

```text
Finding 1 Successful Summary SSE Privacy : Resolved
Finding 2 Long Silent SSE Keepalive       : Resolved
Finding 3 Summary Risk Notice             : Resolved
Finding 4 Runtime Error Relocalization     : Resolved
Default Regression                        : 246 passed、3 deselected
Targeted Regression                       : 51 passed
Mac Metal Model Smoke                     : 2 passed、1 skipped
Final Decision                            : Phase 1-H Accepted
```

Phase 1-HがAcceptedになったことは、Phase 1全体完了、User Acceptance、Lightning Validation、Backup、Phase 1-ex開始を意味しない。

## 2. Finding 1 Resolution：Successful Summary SSE Data Minimization

Summary成功時のPublic Eventから次が除去された。

```text
original_assistant_message
summary_assistant_message
presented_source
original_usage
summary_usage
```

Current Success Completed：

```json
{
  "assistant_message": {
    "role": "assistant",
    "content": "Short summary"
  },
  "transformation": {
    "summary_mode": "post_generation",
    "summary_applied": true,
    "fallback_used": false,
    "original_finish_reason": "stop",
    "summary_finish_reason": "stop"
  }
}
```

独立再現では、Normal Originalを`Original answer`、Summaryを`Short summary`としてEvent列を生成し、次を確認した。

```text
ORIGINAL_PRESENT = False
Presented Delta  = Short summary
Assistant Message = Short summary
Transformation   = Non-content Metadata only
```

Fallback時はOriginalがPresented Answerであるため`assistant_message`として返るが、別Fieldへ重複しない。不完全Summaryは送信されない。

追加Testは、Raw SSE全体からOriginal、Original Thinking、Summary Thinking、削除済みKeyが不在であることを直接Assertする。前回のTest Gapは解消した。

## 3. Finding 2 Resolution：SSE Keepalive

次の固定Contractが追加された。

```text
Interval    : 15.0 seconds
Wire Format : : keepalive\n\n
SSE Type    : Comment
Semantic Event／History／Audit : No
```

実装はAsync SSE Consumer側だけでIdle時間を計測する。

- Application Event送信でTimerをResetする。
- Normal Hidden Generation中に動作する。
- Summary Buffered Generation中に動作する。
- Conversation Event Queueへ積まない。
- Terminal後に送らない。
- Consumer Close／Disconnectで既存Cooperative Cancelへ合流する。
- 専用Task／Threadを作らない。
- Request ID、Prompt、ExceptionをCommentへ含めない。

短縮Intervalを用いたRegressionで、Keepalive後の通常Event／Completed、Producer-thread Native Cancel／Close、後続Generation、Task Cleanupが合格した。

KeepaliveはPhase 1-Hで新たに生じた長時間Silent Intervalを緩和する。実Lightning Reverse Proxy上の確認は、予定されているBatch Lightning Gateで行う。

## 4. Finding 3 Resolution：Summary Risk Notice

日本語とEnglishの両方へ、Latency／Token Costだけでなく、要約による情報欠落・変形可能性が追加された。

```text
日本語:
要約により詳細、前提、注意事項等が省略・変形される可能性があります。

English:
details, assumptions, or cautions may be omitted or altered by the summary.
```

Initial HTMLとTranslation Dictionaryは同義内容であり、品質保証を追加していない。Static Testも追加されている。

## 5. Finding 4 Resolution：Runtime Status Relocalization

Render済みError文字列を保持する`runtimeText`は削除され、次のStable Stateへ変更された。

```text
loading
metadata
known_error
```

`renderRuntimeStatus()`を`applyTranslations()`から毎回呼ぶため、Loading／Known Errorは現在のUI Languageで再解決される。Metadata成功時のModel／Profile／Device IdentifierだけはOpaque Textとして維持する。

実装報告のManual Browser Evidence：

```text
ja : Runtime情報を取得できませんでした。
en : Could not load runtime information.
ja : Runtime情報を取得できませんでした。
```

UI Language変更はResponse Language値を変更しない。

## 6. Phase 1-H Core Acceptance

Follow-up前に合格していた次の領域もRegressionを通過した。

- Summary Mode `off／post_generation`
- Default OFF
- OFF時Main Model Call 1回
- ON時Normal／Summary各1回
- Same Main Model Sequential Reuse
- Normal Stream Close後のSummary Stream Open
- Summary max 1024／Thinking disabled
- Canonical FinalだけのJSON Summary Source
- User Prompt／History／Thinking／System Prompt非混入
- Response Language `ja／en／auto`
- Summary Parser／Hidden Reasoning
- Error／Context／Empty／Parser／Length／No Terminal Fallback
- Cancel時No Fallback／No Assistant History
- Producer-thread Native Cancel／Close
- Disconnect／Backpressure／Shutdown
- Gate Release／後続Generation
- Application Config Schema 3
- Deployment Profile非変更
- UI Language／Response Language分離
- UI LanguageだけのNamespaced Local Storage
- Plain Text Rendering／No External Dependency
- CLI Contract非変更

## 7. Independent Verification

### 7.1 Static／Type／Unit／Integration

```text
ruff format --check src scripts tests     : Pass／93 files
ruff check src scripts tests              : Pass
mypy .                                    : Pass／93 source files
python -m compileall -q src scripts tests : Pass
node --check app.js                       : Pass
pytest -q                                 : Pass／246 passed、3 deselected
Conversation／Summary／Web Targeted       : Pass／51 passed
uv lock --check --offline                 : Pass／122 packages
bash -n Setup Scripts                     : Pass
```

### 7.2 Mac Metal実Model

```text
pytest -q -m model_smoke : 2 passed、1 skipped、246 deselected
Skip                     : Phase 1-F Profile未指定
```

Reviewでは最初からMac Metalへ直接Access可能な実行で確認し、`llama_context` Environment Failureは発生しなかった。

## 8. Non-blocking Observations

### 8.1 Summary Stage Broad Exception

Summary StageのBroad `except Exception`は、UserへRaw Errorを出さずOriginalへFallbackする。Operator Logはまだ追加されていない。

Current User Safety／Fallbackは成立しているためBlockerとしない。Audit／Observability導入時に、本文・Prompt・Pathを出さないSafe Internal Reason／Operator Logへ接続する。

### 8.2 Legacy `force_cancel()`

Public Session SurfaceにLegacy `force_cancel()`定義が残るが、Runtime Callerは0件であり、Current LifecycleはCooperative Cancelだけを使用する。Phase 1-Gから継続する非ブロッカーとする。

### 8.3 Lightning Native／Proxy

15秒KeepaliveのDeterministic Testは合格したが、Lightning上の実Reverse Proxy／CUDA／CPU実行は未実施である。これはPhase 1-H Source Findingではなく、予定どおりBatch Lightning Gateで確認する。

## 9. Acceptance Status

| Area | Result |
|---|---|
| Summary Core | Accepted |
| Summary Failure／Fallback | Accepted |
| Summary SSE Data Minimization | Accepted |
| SSE Keepalive | Accepted for Mac／Pending Lightning Native Gate |
| UI Language／Response Language Separation | Accepted |
| Runtime Error Relocalization | Accepted |
| Cancel／Disconnect／Shutdown | Accepted |
| Config Schema／Adapter Boundary | Accepted |
| Phase 1-H Overall | Accepted |

## 10. Next Gate

```text
Phase 1-H Accepted
  → User Mac Acceptance
  → Batch Lightning Upload／Native／Web Validation
  → Cross-environment Final Review
  → User Manual Finalization
  → Phase 1 Completion／Next Phase Ready Declaration
  → User Final Acceptance
  → Backup
  → Phase 1-ex
```

本ReviewはLightning Upload、Model Transfer、Phase 1完了宣言、Backup、Phase 1-ex、Git、GitHub公開を自動許可しない。

## 11. Append-Only

前回Review、Follow-up Handoff、実装報告を変更せず、新TimestampのAccepted Reviewとして追加した。

<!-- SOURCE_END 59: docs/handoffs/designer_review_phase_1h_review_follow_up_20260721184140.md -->

---

<!-- SOURCE_BEGIN 60: docs/handoffs/designer_review_phase_1h_summary_mode_and_ui_language_20260721182038.md -->

### Source 60: `docs/handoffs/designer_review_phase_1h_summary_mode_and_ui_language_20260721182038.md`

- History Target: `docs/project/phases/phase_1/history/handoffs/designer_review_phase_1h_summary_mode_and_ui_language_20260721182038.md`
- Source SHA-512: `683677a59a5cc3636bd9291133ec3417d563b877ba613a1472970e22ccc0ae6ca1ac5a5d98a9f18a5c8a6fabb39be3e2739410bd0479233d747dffb654b0a2e7`
- Source Size: `12940` bytes

# Phase 1-H Summary Mode／UI Language 設計Review

- 文書ID: `designer_review_phase_1h_summary_mode_and_ui_language`
- 状態: `changes_requested`
- 作成日時: `2026-07-21 18:20:38 JST`
- 更新日時: `2026-07-21 18:20:38 JST`
- Snapshot: `20260721182038`
- 作成担当: 設計者役担当Task
- 対象: Phase 1-H Summary Mode／UI Language実装
- 正本言語: 日本語
- 実装報告: [implementer_status_phase_1h_summary_mode_and_ui_language_20260721181202.md](../history/handoffs/implementer_status_phase_1h_summary_mode_and_ui_language_20260721181202.md)
- Requirements: [phase_1h_summary_mode_and_ui_language_requirements_20260721174346.md](../history/requirements/phase_1h_summary_mode_and_ui_language_requirements_20260721174346.md)
- Architecture: [phase_1h_summary_mode_and_ui_language_architecture_20260721174346.md](../history/architecture/phase_1h_summary_mode_and_ui_language_architecture_20260721174346.md)
- ADR: [adr_0020_phase_1h_summary_pipeline_and_ui_language_separation_20260721174346.md](../history/adr/adr_0020_phase_1h_summary_pipeline_and_ui_language_separation_20260721174346.md)
- Handoff: [implementer_handoff_phase_1h_summary_mode_and_ui_language_20260721174346.md](../history/handoffs/implementer_handoff_phase_1h_summary_mode_and_ui_language_20260721174346.md)
- Latest Index: [documentation_index_20260721182038.md](../history/documentation_index_20260721182038.md)
- supersedes: なし（Phase 1-H Review系列の初回）

## 1. Review結論

Phase 1-Hの中核実装は成立している。Static、Type、Unit、Web Integration、Mac Metal実Modelは合格した。

ただし、正本Architecture／公開Preview境界に対してMandatory Findingが4件あるため、Phase 1-HをAcceptedにはしない。

```text
Summary Call Count／Sequentiality : Pass
Summary Prompt Boundary           : Pass
Summary Thinking／Token Policy    : Pass
Fallback Matrix                   : Pass
Cancel／Shutdown Thread Boundary  : Pass
Application Schema 3              : Pass
UI／Response Language Separation  : Mostly Pass
Successful Summary SSE Privacy    : Fail
Long Silent SSE Reliability       : Fail／Pre-Lightning Blocker
Summary Risk Notice               : Incomplete
Runtime Error Relocalization      : Incomplete
Final Decision                    : Changes Requested
```

「テストが落ちている実装」ではない。既存Testが受入Contractとの差を捕捉していない状態である。

## 2. Mandatory Finding 1：Summary成功時にもOriginal全文をClientへ送信している

- Priority: High
- Acceptance Impact: Blocker
- 対象: `src/margpa_runtime_llm/modules/conversation/application/conversation_generation.py:348-395`
- Test Gap: `tests/integration/web/test_web_app.py:340-373`

Summary成功時の`completed` Eventへ次を含めている。

```json
{
  "assistant_message": {"content": "Short summary"},
  "original_assistant_message": {"content": "Original answer"},
  "summary_assistant_message": {"content": "Short summary"}
}
```

このため、UIにOriginalが描画されなくても、SSE Response BodyにはOriginal全文が出力される。

独立再現結果：

```json
{
  "event": "completed",
  "data": {
    "assistant_message": {"content": "Short summary"},
    "presented_source": "summary",
    "original_assistant_message": {"content": "Original answer"},
    "summary_assistant_message": {"content": "Short summary"}
  }
}
```

正本では、Summary成功時にBrowser Historyへ採用するのはSummaryであり、OriginalはPipeline内の独立Artifact／将来Audit Hookとして扱う。ArchitectureのCompleted例も、回答本文ではなく非機密Transformation Metadataだけを返す。

Current Integration Test名は`hides_original_then_presents_only_valid_summary`だが、`Original answer`がResponseへ存在しないことをAssertしていない。このため実装とTestが同じContract Driftを固定している。

Required Correction：

1. Summary成功時のPublic SSEから`original_assistant_message`と重複する`summary_assistant_message`を除く。
2. OriginalはServer-side Session Artifactとして保持し、Phase 1-HではClientへ送らない。
3. `assistant_message`はPresented Answerだけとする。
4. Completedへ必要なら次の非本文Metadataだけを返す。

```json
{
  "transformation": {
    "summary_mode": "post_generation",
    "summary_applied": true,
    "fallback_used": false,
    "original_finish_reason": "stop",
    "summary_finish_reason": "stop"
  }
}
```

5. Fallback時はOriginalがPresented Answerであるため、`assistant_message`として返してよい。
6. Success Integration Testへ、Original Canonical FinalがSSE Response全体に存在しないAssertを追加する。

## 3. Mandatory Finding 2：Hidden／Buffered 2段生成中のSSE Keepaliveがない

- Priority: High
- Acceptance Impact: Pre-Lightning Blocker
- 対象: `src/margpa_runtime_llm/web/streaming.py:68-85`
- 関連: `src/margpa_runtime_llm/modules/conversation/application/conversation_generation.py:164-214`

Summary Mode ONでは、Normal Generation DeltaをClientへ送らず、Summaryも成功確定までBufferする。

```text
start
  → Normal 0..2048 tokens／Client outputなし
status
  → Summary 0..1024 tokens／Client outputなし
delta＋completed
```

Current SSE BridgeはQueueが空の場合、0.1秒ごとにDisconnectだけを確認し、ClientへComment／Heartbeatを送らない。

この構造では、低速Mac、Lightning CPU Profile、混雑時、長い2048／1024 Generationにより、Reverse ProxyのIdle Timeoutで接続が切れる可能性がある。Phase 1-HはOriginal／Summaryを意図的に非Streaming化したため、Phase 1-GよりIdle区間が大幅に長くなっている。

Required Correction：

1. SSE Bridgeへ意味を持たないPeriodic Keepalive Commentを追加する。
2. 例：15秒程度のBounded Intervalで`: keepalive\n\n`を送る。
3. KeepaliveをConversation Event／History／Audit Resultとして扱わない。
4. Consumer Stop／Disconnect後にHeartbeat Taskが残らないようLifecycleを同じ`finally`で閉じる。
5. Blocking Fake Streamを使い、Application Eventが長時間ない間にもKeepaliveが出るTestを追加する。
6. KeepaliveがTerminal Count、Queue Capacity、Cancel Thread Boundaryを壊さないことを確認する。

Intervalの最終値はFollow-up Handoffで固定する。LightningへUploadする前に解消する。

## 4. Mandatory Finding 3：要約による情報欠落可能性のUI注記がない

- Priority: Medium
- Acceptance Impact: Blocker／Small Fix
- 対象: `src/margpa_runtime_llm/web/static/app.js:35,91`
- 対象: `src/margpa_runtime_llm/web/static/index.html`のSummary Note
- 正本: Handoff Section 8.1

Current Noteは追加LatencyとToken使用量だけを説明している。

```text
ONでは通常回答の完了後に同じModelで要約します。
処理時間とToken使用量が増えます。
```

正本Handoffは、追加生成、遅延に加えて、要約による情報欠落の可能性を短く明示するよう要求している。

Required Correction：

- 日本語Noteへ「要約により詳細、前提、注意事項等が省略・変形される可能性があります」相当を追加する。
- English Noteへ同義の注意を追加する。
- Translation DictionaryとInitial HTMLを一致させる。
- Static Testで欠落RiskのKey／Textを確認する。

## 5. Mandatory Finding 4：Runtime取得失敗後のUI Language再切替がError表示へ反映されない

- Priority: Medium
- Acceptance Impact: Blocker／Small Fix
- 対象: `src/margpa_runtime_llm/web/static/app.js:207-249,316-342`

`loadRuntime()`失敗時、現在言語でRender済みのError Textを`state.runtimeText`へ保存する。その後`applyTranslations()`は`runtimeText === null`の場合しかRuntime Statusを再描画しない。

再現する論理経路：

```text
UI ja
  → Runtime API Failure
  → 「Runtime情報を取得できませんでした。」をstate.runtimeTextへ保存
  → UIをEnglishへ変更
  → state.runtimeTextはnon-null
  → Error表示は日本語のまま
```

Known Error／StatusをUI Language切替対象とする正本要件に適合しない。

Required Correction：

1. Runtime StatusもRender済み文字列ではなく、`kind／translation_key／values`等のStable Stateで保持する。
2. Runtime Metadata成功時だけOpaque Textとして保持する。
3. Runtime Loading／Known Failureは`applyTranslations()`で再描画する。
4. Runtime Failure後の`ja → en → ja`を動作Testする。

## 6. Non-blocking Observation

### 6.1 Summary StageのBroad Exception Fallback

`_events_with_summary()`はSummary Stage全体の`Exception`を無記録でOriginal Fallbackへ変換する。

End UserへRaw Exceptionを出さない点は正しい。一方、実装Bugまで静かにFallbackするとOperatorが異常を識別できない。Phase 1-H Follow-upでは、少なくとも固定された安全なOperator Logまたは内部Reason Codeを残し、Raw Exception／Prompt／PathをClientへ出さない構成を検討する。

Current Fallback結果自体は安全であるため、本Observation単独ではBlockerとしない。

### 6.2 Legacy `force_cancel()`

Public Session SurfaceにThread-affine Streamへ別Threadから到達し得る`force_cancel()`定義が残る。Current Runtime Callerは0件であり、実経路はCooperative Cancelだけなので、Phase 1-Gから継続する非ブロッカーとする。

## 7. Accepted Areas

次は正本どおり成立している。

- `off／post_generation`の厳格なTyped Contract
- Application Config Schema `3`
- Deployment Profile Schema非変更
- Default OFF
- OFF時Main Model Call 1回
- ON時Normal／Summary Call各1回
- Same Model Key／Sequential Stream
- Normal Stream Close後のSummary Stream Open
- Summary max 1024／Thinking disabled
- Canonical FinalだけをJSON Data Boundaryで要約
- User Prompt／History／Thinking／System Prompt非混入
- `ja／en／auto` Summary Language Policy
- Summary OutputのThinking Parser適用
- Error／Context／Empty／Parser／Length／No Terminal Fallback
- Summary Delta Buffering
- Cancel時No Fallback／No History
- Normal／Summary両段階のProducer-thread Cancel／Close
- Gate Release／後続Generation
- UI LanguageとResponse LanguageのState分離
- UI LanguageだけをNamespaced Local Storageへ保存
- Plain Text DOM更新／No External i18n Dependency
- New Chat／Reload後のUI Language維持
- New Dependencyなし／CLI Contract非変更

## 8. Independent Verification

### 8.1 Static／Type／Unit／Integration

```text
ruff format --check src scripts tests     : Pass／93 files
ruff check src scripts tests              : Pass
mypy .                                    : Pass／93 source files
python -m compileall -q src scripts tests : Pass
node --check app.js                       : Pass
pytest -q                                 : Pass／242 passed、3 deselected
Conversation／Summary／Web Targeted       : Pass／47 passed
uv lock --check --offline                 : Pass／122 packages
bash -n Setup Scripts                     : Pass
```

`uv lock`はSandbox内でUser Cache Permissionにより失敗したため、既存CacheへAccess可能なReview実行で再確認し合格した。Source Failureではない。

### 8.2 Mac Metal実Model

```text
Sandbox Run : 2 failed、1 skipped／llama_context creation failure
Direct Run  : 2 passed、1 skipped、242 deselected
Skip        : Phase 1-F Profile未指定
```

Direct Mac Metalで合格したため、Sandbox FailureはPhase 1-H Source Findingとしない。

## 9. Follow-up Acceptance Conditions

Phase 1-H Acceptedには次をすべて満たす必要がある。

1. Summary成功時のSSEからOriginal全文を除く。
2. Transformation Metadataを非本文・非機密にする。
3. Success SSEでOriginal不在をTestする。
4. Hidden Normal／Buffered Summary中のSSE Keepaliveを追加する。
5. Keepalive Lifecycle／Disconnect／Cancel Regressionを追加する。
6. Summary Noteへ情報欠落／変形可能性を日英で追加する。
7. Runtime Known ErrorをUI Language切替後に再描画する。
8. Static／Default／Targeted／Model Smokeを再実行する。
9. Lightning Full UploadはFollow-up Accepted後まで行わない。

## 10. Next Gate

```text
Phase 1-H Changes Requested
  → Designer Follow-up Handoff
  → User authorizes Follow-up
  → Implementer Correction／Status
  → Designer Re-review＋New Index
  → User Mac Acceptance
  → Batch Lightning Upload／Validation
```

本ReviewはSource修正、Lightning操作、Phase 1完了宣言、Backup、Phase 1-ex、Git、GitHub公開を許可しない。

## 11. Append-Only

実装報告、Requirements、Architecture、ADRを変更せず、新TimestampのReviewとして追加した。

<!-- SOURCE_END 60: docs/handoffs/designer_review_phase_1h_summary_mode_and_ui_language_20260721182038.md -->

---

<!-- SOURCE_BEGIN 61: docs/handoffs/designer_review_phase_1i_repository_and_mac_manual_acceptance_20260725212559.md -->

### Source 61: `docs/handoffs/designer_review_phase_1i_repository_and_mac_manual_acceptance_20260725212559.md`

- History Target: `docs/project/phases/phase_1/history/handoffs/designer_review_phase_1i_repository_and_mac_manual_acceptance_20260725212559.md`
- Source SHA-512: `8125e0ef4faeebc2236a2a832e9528210c9eb47b6a0891826c62ad7645c4b388327a51466fbeabf8f6ca016d993ca34a9ff4659bf07ea19194fdb7e1f54a325e`
- Source Size: `6904` bytes

# Phase 1-I Repository and Mac Manual Acceptance 設計Review

- 文書ID: `designer_review_phase_1i_repository_and_mac_manual_acceptance`
- 状態: `accepted_with_deferred_phase_4_presentation_enhancements`
- 作成日時: `2026-07-25 21:25:59 JST`
- 更新日時: `2026-07-25 21:25:59 JST`
- Snapshot: `20260725212559`
- 作成担当: 設計者役担当Task
- 対象Status: [implementer_status_phase_1i_web_presentation_and_ux_follow_up_20260725203508.md](../history/handoffs/implementer_status_phase_1i_web_presentation_and_ux_follow_up_20260725203508.md)
- 対象Handoff: [designer_handoff_phase_1i_web_presentation_and_ux_follow_up_20260725200001.md](../history/handoffs/designer_handoff_phase_1i_web_presentation_and_ux_follow_up_20260725200001.md)
- 正本言語: 日本語
- supersedes: なし

## 1. Conclusion

Phase 1-IのRepository実装とMac Web Manual AcceptanceをAcceptedとする。

Blocking Findingはない。Streaming中のRaw Markdown、Table未対応、Busy時の二重MessageおよびCode Block強化は、Current Contractを壊す問題ではなくPhase 4 Presentation／UX Follow-upとして保持する。

## 2. User Manual Acceptance

| Test | Result | Review |
|---|---:|---|
| User Message Copy | PASS | 入力単位のCopyが動作した。 |
| Assistant Final Copy | PASS | 出力単位のCopyが動作した。 |
| UI日本語／英語 | PASS | 既確認結果を再確認した。 |
| Response Language日本語／英語 | PASS | UI Languageと独立して動作した。 |
| Summary Mode | PASS | Post-generation Summaryが動作した。 |
| New Chat Context Reset | PASS | 別Topicを開始でき、旧会話をContextへ送らない。 |
| New Chat during Generation | PASS | 停止・初期化後に再送信できた。 |
| Stop during Summary | PASS | 正常復帰した。 |
| Browser Reload | PASS | 会話とUI Language以外のOptionがRuntime Defaultへ戻った。 |
| UI Language Persistence | PASS | UI LanguageだけがBrowser Storageから復元された。 |
| Multi-tab Model Busy | PASS | 競合側へ`model_busy`が安全に表示され、先行生成完了後に再実行できた。 |
| Thinking Control Dependency | PASS | 推論生成ON時だけ推論過程表示を選択できた。 |
| Thinking／Final Separation | PASS | 推論過程と最終回答が別領域に表示された。 |
| Completion Markdown | PASS with limitation | 完了後に対応MarkdownをDOMへ変換した。 |

## 3. Busy Message Assessment

競合Tabで次が表示された。

```text
The model is processing another request.
The request failed.
```

前者はServerの`model_busy`を翻訳した具体的Error、後者はRequest Catch時の汎用Statusである。409 Busyを安全に拒否し、先行Request完了後に次の生成が動作するため、機能上は正しい。

ただし同一原因に対して具体Messageと汎用Messageを同時表示するため、一般利用者には冗長である。Phase 4ではStatusも`model_busy`へ統一するか、Message BubbleとGlobal Statusの責務を整理する。

## 4. Markdown Assessment

Current Contract：

```text
Streaming中 : Plain Text
Completion後: Allowlist Markdown DOM
Failure時   : Canonical Plain Text
```

生成中にMarkdown記号が見えることは設計どおりであり、Completion後に変換されることを確認した。安全性と表示安定性を優先するPhase 1実装としてAcceptedとする。

### Table

Current ParserはTableを実装していない。Pipe TableはParagraphとして扱われ、`white-space: normal`により行区切りが潰れて見える場合がある。

安全性問題ではないが可読性が低いため、Phase 4でSemantic Table、Responsive OverflowおよびFallbackを実装する。

## 5. Code Block Assessment

Fenced Code Block自体はCurrent Parserで`pre`／`code`へ分離済みである。

Phase 4では次を追加する。

- Markdown、YAML、JSON、Pythonその他のLanguage Label
- Assistant説明本文とCode Snippet Blockの視覚的分離
- Code Block右上の個別Copy Button
- 回答全体CopyとCode-only Copyの独立
- Canonical Code TextをCopy Sourceとし、Rendered DOMをSourceにしない。
- Language名を無制限にCSS ClassまたはExecutable処理へ渡さない。
- Syntax Highlightを追加する場合もRuntime CDNを使用せず、Version、License、Digestを管理する。
- Highlight失敗時はPlain Code BlockへFallbackする。

## 6. Thinking Assessment

推論生成をONにした場合だけ推論過程表示を選択できる。これはGenerationとPresentationを正しく分離した状態である。

実Qwen3では、推論過程が英語、最終回答が日本語となる場合がある。推論過程はModel生成内容であり、Response Languageが最終回答と同程度に強制される保証はない。Phase 1-IのUI不具合とは扱わない。

Raw Thinking非保存、Assistant Final Copyへの非混入および次Turn Contextへの非混入は、Source Contractと自動Testで確認した。

## 7. Independent Code Review

確認した主要境界：

- `thinking_mode`／`thinking_visibility`
- Capability不足時Fail Closed
- `reasoning`／`final` SSE Channel
- Hidden Reasoning非送信
- Summary Thinking Disabled
- Canonical Final
- Clipboard Write-only
- `innerHTML`不使用
- Raw HTML Inert化
- Dangerous URL Scheme拒否
- External Link属性
- IME Composition Guard

重大な安全境界違反は確認しなかった。

## 8. Independent Verification

```text
pytest                         : 265 passed, 3 deselected
Phase 1-I／Pure CPU Targeted   : 30 passed, 1 deselected
Ruff Check                     : PASS
Ruff Format                    : PASS
Mypy                           : PASS
Node Safe Markdown             : 5 passed
Shell Syntax                   : PASS
uv lock --check                : PASS／122 packages
```

追加のMac Model Smokeは、既にWeb Runtimeが同じQwen ModelをMemory Mapした状態で別Contextを作ろうとして`Failed to create llama_context`となった。実装回帰とは判定しない。

- 常駐Web RuntimeのModel Mappingを確認した。
- ユーザーによる実Web Model生成は合格している。
- Phase 1 Final GateではWeb Runtime停止後にModel Smokeを再実行する。
- Reviewのためにユーザーの常駐Processを停止しなかった。

## 9. Deferred Phase 4 Enhancements

- Streaming Markdownの段階的安全Rendering
- Markdown Table
- Code Snippet Container
- Language Label
- Code-only Copy
- Syntax Highlight候補
- Busy Message／Global Status整理
- Thinking表示の追加説明

これらはPhase 1-I Acceptanceを妨げない。

## 10. Final State

```text
Repository Implementation : ACCEPTED
Mac Manual Acceptance     : ACCEPTED
Security Boundary         : ACCEPTED
Phase 4 Enhancements      : DEFERRED
Phase 1-I                 : COMPLETE／ACCEPTED
```


<!-- SOURCE_END 61: docs/handoffs/designer_review_phase_1i_repository_and_mac_manual_acceptance_20260725212559.md -->

---

<!-- SOURCE_BEGIN 62: docs/handoffs/designer_review_top_level_phase_1_completion_and_lightning_web_acceptance_20260726111632.md -->

### Source 62: `docs/handoffs/designer_review_top_level_phase_1_completion_and_lightning_web_acceptance_20260726111632.md`

- History Target: `docs/project/phases/phase_1/history/handoffs/designer_review_top_level_phase_1_completion_and_lightning_web_acceptance_20260726111632.md`
- Source SHA-512: `fb4d780d0b64d4e3c8a6afb4e36e7b22fb35cb1f71ef52f968a744dffdacb8a96788449e567f3b4ce2320b52764fec9188e5fcecfbfb942697c98de218f9d110`
- Source Size: `8017` bytes

# Top-level Phase 1 Completion／Lightning Web Acceptance 設計Review

- 文書ID: `designer_review_top_level_phase_1_completion_and_lightning_web_acceptance`
- 状態: `accepted_phase_complete_next_phase_1_ex`
- 作成日時: `2026-07-26 11:16:32 JST`
- 更新日時: `2026-07-26 11:16:32 JST`
- Snapshot: `20260726111632`
- 作成担当: 設計者役担当Task
- 対象環境: Mac Local Web／Lightning AI Studio Linux x86_64 Pure CPU／外部Browser
- 前回Review: [designer_review_phase_1f_lightning_full_suite_revalidation_20260726094241.md](../history/handoffs/designer_review_phase_1f_lightning_full_suite_revalidation_20260726094241.md)
- Current Manual: [phase_1_web_and_lightning_user_manual_20260726111632.md](../history/user_manual/phase_1_web_and_lightning_user_manual_20260726111632.md)
- Auto-start Reservation: [phase_1_ex_lightning_web_autostart_and_cost_control_requirements_reservation_20260726111632.md](../history/requirements/phase_1_ex_lightning_web_autostart_and_cost_control_requirements_reservation_20260726111632.md)
- 正本言語: 日本語
- supersedes: なし

## 1. Conclusion

Lightning Web Previewの外部手動AcceptanceをAcceptedとする。

Phase 1-AからPhase 1-Iの実装Review、Mac Manual Acceptance、Mac／Lightning Full Repository Suite、Lightning Pure CPU Native AcceptanceおよびLightning外部Web Acceptanceがすべて成立した。

したがって、Top-level Phase 1をComplete／Acceptedとし、次PhaseであるPhase 1-ex「運用再整備」へ着手可能と宣言する。

```text
Phase 1-A～1-I                 : COMPLETE／ACCEPTED
Mac Web Manual Acceptance     : PASS
Lightning Pure CPU Runtime    : ACCEPTED
Mac Full Repository Suite     : GREEN
Lightning Full Suite          : GREEN
Lightning External Web        : PASS
Top-level Phase 1             : COMPLETE／ACCEPTED
Next Phase                    : Phase 1-ex
```

## 2. Lightning External Web Evidence

Lightningの公開URLを、Lightning Accountと無関係なBrowserおよびSafariから開き、Basic認証を経由してMARGPA Runtime LLMへ到達できた。

確認時Public Link：

```text
https://lightning-preview-url-redacted.invalid/not-published
```

Public LinkはLightning側の再構成により変化し得る。Credentialは本Review、Docs、Config、Screenshot、Gitへ保存していない。

## 3. Required Manual Acceptance

| Test | Result | Assessment |
|---|---:|---|
| 短い日本語生成 | PASS | Pure CPU Profileで実Model生成が成立した。 |
| 生成中の停止 | PASS | Stop後にRuntimeが回復した。 |
| 停止後の再送信 | PASS | 後続Requestを正常に処理した。 |
| 新規Chat | PASS | Contextを初期化し、別Topicを開始できた。 |
| UI日本語／English切替 | PASS | 表示言語を切り替えられた。 |
| 回答言語`ja／en`切替 | PASS | UI Languageから独立して動作した。 |
| Browser Reload | PASS | 会話およびUI Language以外のOptionが既定値へ戻った。 |
| Multi-tab Model Busy | PASS | 競合Requestを安全に拒否し、先行完了後に再実行できた。 |
| Server停止後のPort Close | PASS | Process停止後に公開Serviceが停止した。 |

## 4. Additional Manual Acceptance

| Test | Result | Assessment |
|---|---:|---|
| User Message Copy | PASS | 入力単位のCopyが動作した。 |
| Assistant Message Copy | PASS | 出力単位のCopyが動作した。 |
| Summary Mode | PASS | Post-generation Summaryが動作した。 |
| New Chat during Generation | PASS | 生成を停止し、初期化後に再送信できた。 |
| Stop during Summary | PASS | Summary処理を停止し、正常復帰した。 |
| Thinking Generation | PASS | Thinking Generationを有効化できた。 |
| Thinking Visibility | PASS | Thinking Generation有効時のみ選択可能であった。 |
| Max New Tokens Cutoff | PASS | 指定上限による打切りが成立した。 |
| Basic認証 | PASS | Credentialなし／誤Credentialを拒否し、正しいCredentialで表示した。 |
| 外部Browser | PASS | LightningへLoginしていないBrowserから利用できた。 |

## 5. Multi-tab Busy Messages

英語UI：

```text
The model is processing another request.
The request failed.
```

日本語UI：

```text
Modelは別のRequestを処理中です。
Requestに失敗しました。
```

具体的な`model_busy`表示と汎用Failure表示が同時に出る点は冗長であるが、競合Requestを安全に拒否し、先行処理完了後に再実行できる。Phase 1のBlocking Failureとはしない。

表示責務の整理はPhase 4 Presentation／UX Follow-upへ延期する。

## 6. Browser State Contract

Browser Reload後に次を確認した。

```text
Conversation                 : cleared
Response Language            : runtime default
Max New Tokens               : runtime default
Thinking Generation          : runtime default
Thinking Visibility          : runtime default
Summary Mode                 : runtime default
UI Language                  : browser-persisted value
```

Phase 1のEphemeral Browser MemoryおよびUI LanguageだけをLocal Storageへ保持するContractと一致する。

## 7. Performance Observation

Lightning最小Pure CPU環境では、Qwen3 4B Q4_K_Mの生成が非常に遅い。

これは次の組合せによるExpected Performance Limitationであり、Correctness Failureではない。

- Linux x86_64 Pure CPU
- 4 CPU
- GGUF Q4_K_M
- Contextおよび最大生成Token数
- Thinking Generation
- Summary Modeによる2回目のModel Generation

Current Decision：

```text
Public／Cross-platform Verification : Pure CPUを維持
日常開発／高速確認                  : Mac Metalを使用
Lightning GPU                       : 必要な短時間検証時だけ明示選択
Silent GPU Upgrade                  : 禁止
```

## 8. iPhone／iOS Observation

iPhone／iOS対応は技術的に不可能ではない。Current Web UIがMobile Responsive Acceptanceをまだ持たないため、現時点では未対応／未検証として扱う。

Phase 4または後続UI Phaseで次を扱う。

- Responsive Layout
- Narrow Viewport
- Touch操作
- iOS Safari
- Virtual Keyboard
- Safe Area
- Long Message／Code Block横Overflow
- Copy／Stop／SendのTouch Target

これはPhase 1 CompletionをBlockしない。

## 9. Lightning Sleep／Restart Observation

Current Port Viewer運用では、StudioまたはWeb Processが停止すると公開URLも利用不能になる。再開時にEnvironment Variable、Basic認証、Profileおよび起動Commandを毎回手入力する運用は継続利用に不向きである。

次をPhase 1-exの運用改善として予約する。

```text
Studio Launch
  → Persistent non-secret configuration resolution
  → Managed Secret resolution
  → Project-owned launcher
  → Pure CPU Web start
  → Health Check
  → Public app ready

No traffic／Idle
  → Platform-managed sleep

Next access
  → Platform auto-start／cold start
  → Web process recovery
```

詳細はAuto-start Reservationを参照する。

## 10. Phase Completion Gates

Phase完了Policyの両Gateが成立した。

```text
Gate A:
  設計者役がPhase 1完了とPhase 1-ex着手可能を宣言
  → 本Reviewにより成立

Gate B:
  ユーザーがMac／Lightning Manual Acceptance合格を宣言
  → 本Review記載のUser-run Evidenceにより成立
```

したがって、Phase 1 Backup Triggerは成立した。

ただし、本ReviewはBackup生成、Git操作、GitHub公開、Phase 1-ex実変更を自動許可しない。これらはユーザーの開始指示に従う。

## 11. Final State

```text
Blocking Finding                 : NONE
Accepted Deferred                : CPU Performance／Mobile UI／Busy UX
Operations Follow-up             : Lightning Auto-start／Sleep
Phase 1 Backup Eligibility       : READY／NOT EXECUTED
Initial GitHub Publication       : DEFERRED UNTIL PHASE 1-ex
Phase 1-ex                       : READY TO START／NOT STARTED
```

<!-- SOURCE_END 62: docs/handoffs/designer_review_top_level_phase_1_completion_and_lightning_web_acceptance_20260726111632.md -->

---

<!-- SOURCE_BEGIN 63: docs/handoffs/implementer_handoff_20260718174637.md -->

### Source 63: `docs/handoffs/implementer_handoff_20260718174637.md`

- History Target: `docs/project/phases/phase_1/history/handoffs/implementer_handoff_20260718174637.md`
- Source SHA-512: `02f4e292bbe44cdbea54227c162469cf60434e56a01d5d35f303f0c47f72e55243d2f420d98a5c6735de7f688103e81fb6dd13d46c666f234c19f765852b19c6`
- Source Size: `2607` bytes

# 実装者役担当タスク 引き継ぎ

- 文書ID: `implementer_handoff`
- 状態: `waiting_for_implementation_unlock`
- 作成日時: `2026-07-18 17:46:37 JST`
- 更新日時: `2026-07-18 17:46:37 JST`
- 対象: 将来の実装者役担当タスク
- 正本言語: 日本語
- 共通引き継ぎ: [common_project_handoff_20260718174637.md](../history/handoffs/common_project_handoff_20260718174637.md)

## 1. 現在の状態

実装は未解禁。

ユーザーから明示的な解禁を受けるまで、Source、Config、Dependency、Gitを変更しない。

## 2. 実装者の責務

- Current Requirementsに従う
- Current Architectureに従う
- ADRを確認する
- Module Boundaryを守る
- Model固有処理をAdapterへ閉じ込める
- User固有PathをCoreへ入れない
- Testを実施する
- 実装上のDeviationを報告する
- 設計上の不明点を設計者へ差し戻す
- 勝手にScopeを拡張しない

## 3. 実装開始前の必読

1. [documentation_index_20260718174637.md](../history/documentation_index_20260718174637.md)
2. [common_project_handoff_20260718174637.md](../history/handoffs/common_project_handoff_20260718174637.md)
3. [project_requirements_20260718174637.md](../history/requirements/project_requirements_20260718174637.md)
4. [system_architecture_20260718174637.md](../history/architecture/system_architecture_20260718174637.md)
5. [model_strategy_20260718174637.md](../history/architecture/model_strategy_20260718174637.md)
6. [runtime_governance_20260718174637.md](../history/governance/runtime_governance_20260718174637.md)
7. [implementation_roadmap_20260718174637.md](../history/architecture/implementation_roadmap_20260718174637.md)

## 4. 最初のImplementation Scope

実装解禁後も、最初はPhase 1から開始する。

- Model Load
- 一問一答
- Chat Template
- Streaming
- Stop
- Generation Config
- Error Handling
- Model Adapter
- Model Registry
- Model Capability

RAG、Agent、16GD、自動Routingを同時実装しない。

## 5. Model

Initial Main：

```text
models/main/qwen3-4b/gguf/Qwen3-4B-Q4_K_M.gguf
```

GuardとJudgeはPhaseに従って追加する。

Model File名を解析してMetadataを推測しない。Registryを使用する。

## 6. 実装上の重要境界

- CoreはModel Backendを直接Importしない
- CoreはFilesystemを直接操作しない
- UIはGovernance Logicを持たない
- Tool PermissionをLLMへ委ねない
- Audit Eventを上書きしない
- 生のChain of Thoughtを保存しない
- Guardを通常Chat Modelとして扱わない

## 7. 未決事項

Local Backend、Directory構成、Config方式、UI等はまだ未決。設計確定前に実装しない。

<!-- SOURCE_END 63: docs/handoffs/implementer_handoff_20260718174637.md -->

---

<!-- SOURCE_BEGIN 64: docs/handoffs/implementer_handoff_20260718193435.md -->

### Source 64: `docs/handoffs/implementer_handoff_20260718193435.md`

- History Target: `docs/project/phases/phase_1/history/handoffs/implementer_handoff_20260718193435.md`
- Source SHA-512: `b0d49a67fa2aec2188c25fa69e1896002d80c3d212a8cc8f04614bf00c46f5ce5af9de7341f3139624e821db744771ea84c94c0942d3b86ad4515dd97ed51cb9`
- Source Size: `2923` bytes

# 実装者役担当タスク 引き継ぎ

- 文書ID: `implementer_handoff`
- 状態: `waiting_for_implementation_unlock`
- 作成日時: `2026-07-18 19:34:35 JST`
- 更新日時: `2026-07-18 19:34:35 JST`
- 対象: 将来の実装者役担当タスク
- 正本言語: 日本語
- supersedes: `implementer_handoff_20260718174637.md`
- 共通引き継ぎ: [common_project_handoff_20260718193435.md](../history/handoffs/common_project_handoff_20260718193435.md)

## 1. 現在の状態

実装は未解禁。

ユーザーから明示的な解禁を受けるまで、Source、Config、Dependency、Gitを変更しない。

## 2. 実装者の責務

- Current Requirementsに従う
- Current Architectureに従う
- ADRを確認する
- Module Boundaryを守る
- Model固有処理をAdapterへ閉じ込める
- User固有PathをCoreへ入れない
- Testを実施する
- 実装上のDeviationを報告する
- 設計上の不明点を設計者へ差し戻す
- 勝手にScopeを拡張しない

## 3. 実装開始前の必読

1. [documentation_index_20260718193435.md](../history/documentation_index_20260718193435.md)
2. [common_project_handoff_20260718193435.md](../history/handoffs/common_project_handoff_20260718193435.md)
3. [project_requirements_20260718193435.md](../history/requirements/project_requirements_20260718193435.md)
4. [system_architecture_20260718193435.md](../history/architecture/system_architecture_20260718193435.md)
5. [model_strategy_20260718174637.md](../history/architecture/model_strategy_20260718174637.md)
6. [runtime_governance_20260718174637.md](../history/governance/runtime_governance_20260718174637.md)
7. [implementation_roadmap_20260718193435.md](../history/architecture/implementation_roadmap_20260718193435.md)

## 4. 最初のImplementation Scope

実装解禁後も、最初はPhase 1から開始する。

- Model Load
- 一問一答
- Chat Template
- Streaming
- Stop
- Generation Config
- Error Handling
- Model Adapter
- Model Registry
- Model Capability

RAG、Agent、16GD、自動Routingを同時実装しない。

## 5. Model

Initial Main：

```text
models/main/qwen3-4b/gguf/Qwen3-4B-Q4_K_M.gguf
```

GuardとJudgeはPhaseに従って追加する。

Model File名を解析してMetadataを推測しない。Registryを使用する。

## 6. 実装上の重要境界

- CoreはModel Backendを直接Importしない
- CoreはFilesystemを直接操作しない
- UIはGovernance Logicを持たない
- Tool PermissionをLLMへ委ねない
- Audit Eventを上書きしない
- 生のChain of Thoughtを保存しない
- Guardを通常Chat Modelとして扱わない

## 7. 未決事項

Project Directory構成は決定済みで、Phase 1最小Directoryのみ作成済み。

Local Backend、Config方式、Dependency管理、UI等はまだ未決。設計確定と実装解禁前にSource Fileを作成しない。

Directory構成の正本：

- [project_directory_structure_20260718192110.md](../history/architecture/project_directory_structure_20260718192110.md)

<!-- SOURCE_END 64: docs/handoffs/implementer_handoff_20260718193435.md -->

---

<!-- SOURCE_BEGIN 65: docs/handoffs/implementer_handoff_lightning_ai_studio_dual_runtime_profiles_20260719200711.md -->

### Source 65: `docs/handoffs/implementer_handoff_lightning_ai_studio_dual_runtime_profiles_20260719200711.md`

- History Target: `docs/project/phases/phase_1/history/handoffs/implementer_handoff_lightning_ai_studio_dual_runtime_profiles_20260719200711.md`
- Source SHA-512: `8784aaf4d69a262bf4068cb54f0b9ccebc80314e20f4f715967571a9121c37829ce51af1a72d40a239778dbd4e5df6d2221896702a4f9caa05dd9900e8e03ccf`
- Source Size: `3236` bytes

# 実装担当向け Lightning AI Studio Dual Runtime Profiles Handoff

- 文書ID: `implementer_handoff_lightning_ai_studio_dual_runtime_profiles`
- 状態: `waiting_future_phase_authorization`
- 作成日時: `2026-07-19 20:07:11 JST`
- 更新日時: `2026-07-19 20:07:11 JST`
- Snapshot: `20260719200711`
- 作成担当: 設計者役担当Task
- 対象担当: 実装担当Task
- 正本言語: 日本語
- 要件: [lightning_ai_studio_dual_runtime_profile_requirements_20260719200711.md](../history/requirements/lightning_ai_studio_dual_runtime_profile_requirements_20260719200711.md)
- Architecture: [lightning_ai_studio_cross_environment_architecture_20260719200711.md](../history/architecture/lightning_ai_studio_cross_environment_architecture_20260719200711.md)
- supersedes: なし（新規Handoff系列）

## 1. Objective

Lightning AI Studio上で、同一Application Core／Model Contractを使い、CUDAとCPUを明示Profileで交換可能にする。

## 2. Planned Files／Scopes

実装開始時に、現行構造を再確認して最小範囲を確定する。

```text
config/profiles/lightning_linux_x86_64_cuda.toml
config/profiles/lightning_linux_x86_64_cpu.toml
config/platforms/platform_registry.toml             # 必要なSchema／Entry
src/.../bootstrap/profile_resolver.py                # Container Detection
src/.../adapters/model_backends/llama_cpp/           # CUDA Detection
scripts/setup/                                       # Linux CUDA／CPU Recipe
tests/                                               # Unit／Native Smoke
docs/handoffs/implementer_status_*
```

ConfigはConditional Write Scopeであり、ユーザーの当該Phase実装許可後に変更する。

## 3. Required Implementation

1. Linux x86_64 Docker Containerを正確に検出する。
2. Mac Native Detectionを壊さない。
3. CUDA／CPU ProfileをSchema 3で作る。
4. Profileは初期`defined`とし、Evidenceなしに`native_verified`としない。
5. llama.cppのCUDA実行を`gpu／cuda／gpu_offload=true`として検出する。
6. `gpu_layers=0`を`cpu／cpu_native／gpu_offload=false`として検出する。
7. GPU未割当時のCUDA ProfileはSafe Failureとし、暗黙CPU Fallbackしない。
8. Explicit CPU ProfileでCPU実行を確認する。
9. CUDA-enabled BuildをCPU Profileでも使用できるか先に検証し、失敗時だけBuild Environmentを分ける。
10. Mac Test、Linux Unit、CUDA Smoke、CPU Smoke、Model Digestを記録する。

## 4. Known Current Limitations

- Execution EnvironmentがRegistryの`native`固定。
- Current Device DetectorはMetal以外をCPU扱いする。
- Platform Default KeyだけではCUDA／CPUを自動選択できない。
- `fallback_policy = explicit_fallback`は未実装である。

## 5. Out of Scope

- Arbitrary Linux Hardwareの完全自動Router
- Windows Profile
- ROCm／Vulkan
- vLLM／Transformers Adapter
- ZeroGPU
- UIからのProfile自動切替
- RuntimeによるNative Package自動再Install

## 6. Authorization Boundary

本Handoffは将来実装用である。現在のPhase 1受入Follow-up、Config変更、Lightning Install／Build、GPU利用、Model転送を開始しない。ユーザーの明示的なPhase開始指示を待つ。

<!-- SOURCE_END 65: docs/handoffs/implementer_handoff_lightning_ai_studio_dual_runtime_profiles_20260719200711.md -->

---

<!-- SOURCE_BEGIN 66: docs/handoffs/implementer_handoff_phase_1_acceptance_follow_up_20260719195134.md -->

### Source 66: `docs/handoffs/implementer_handoff_phase_1_acceptance_follow_up_20260719195134.md`

- History Target: `docs/project/phases/phase_1/history/handoffs/implementer_handoff_phase_1_acceptance_follow_up_20260719195134.md`
- Source SHA-512: `c85e9b83fec9383e721ea603b463b8d2c4cc4ed90a37cd084e03439213653719e21122f238d97a3c8e2b1def3b3eab0035372b637501799852594e2438dfb339`
- Source Size: `2317` bytes

# 実装担当向け Phase 1 ユーザー受入Follow-up Handoff

- 文書ID: `implementer_handoff_phase_1_acceptance_follow_up`
- 状態: `waiting_user_implementation_authorization`
- 作成日時: `2026-07-19 19:51:34 JST`
- 更新日時: `2026-07-19 19:51:34 JST`
- Snapshot: `20260719195134`
- 作成担当: 設計者役担当Task
- 対象担当: 実装担当Task
- 正本言語: 日本語
- 要件: [phase_1_acceptance_follow_up_requirements_20260719195134.md](../history/requirements/phase_1_acceptance_follow_up_requirements_20260719195134.md)
- Known Issues: [known_issues_and_observations_20260719195134.md](../history/operations/known_issues_and_observations_20260719195134.md)
- supersedes: なし（新規Follow-up Handoff系列）

## 1. Current State

Phase 1-A～1-Eの実装ReviewはAcceptedである。User Acceptance Testで、機能破損ではないが改善すべき2件が確認された。

- CLI HelpのMetavar説明不足
- Hidden ThinkingがToken上限へ到達した場合の空表示

Phase 1 User Acceptance／Backup GateはFollow-upのDisposition確定までWaitingである。

## 2. 実装Scope候補

```text
src/margpa_runtime_llm/entrypoints/cli/
src/margpa_runtime_llm/modules/presentation/    # 必要最小限
src/margpa_runtime_llm/orchestration/           # Stop Evidence伝達に必要な場合
tests/
docs/handoffs/implementer_status_*
```

`config/`変更が必要な場合は、理由と対象を実装前に設計者／ユーザーへ返す。

## 3. Required Work

1. Helpの大文字が仮引数名であることを明示する。
2. `--profile`の正しい配置例をHelpから理解できるようにする。
3. Hidden Thinking＋Final未生成＋Token上限到達時だけSafe Warningを表示する。
4. False Positiveを防ぐUnit Testを追加する。
5. Default TestとNative Model Smokeを実行する。
6. 新Timestampの`implementer_status_*`を作成しReviewを依頼する。

## 4. Out of Scope

- Final Answer先頭空行のTrim
- Reasoning Language強制／翻訳
- Linux／Windows一般自動Routing
- Lightning AI Studio Profile
- UI、Governance、Auditの実装

## 5. 実装開始条件

このHandoffは準備済みだが、まだ開始指示ではない。ユーザーが実装担当Taskへ明示的にFollow-up実装を許可した時点で開始する。

<!-- SOURCE_END 66: docs/handoffs/implementer_handoff_phase_1_acceptance_follow_up_20260719195134.md -->

---

<!-- SOURCE_BEGIN 67: docs/handoffs/implementer_handoff_phase_1f_lightning_cross_environment_runtime_20260719202333.md -->

### Source 67: `docs/handoffs/implementer_handoff_phase_1f_lightning_cross_environment_runtime_20260719202333.md`

- History Target: `docs/project/phases/phase_1/history/handoffs/implementer_handoff_phase_1f_lightning_cross_environment_runtime_20260719202333.md`
- Source SHA-512: `9dc54f3ec765ccf78a1caa9412945d1fcab28c9393ceb00d55fb22a1c769217350a8b4389c59288bbd14a1cd7e681b47b7da28f5c7ff8b7d20621c0bec07876b`
- Source Size: `3582` bytes

# 実装担当向け Phase 1-F Lightning Cross-environment Runtime Handoff

- 文書ID: `implementer_handoff_phase_1f_lightning_cross_environment_runtime`
- 状態: `accepted_ready_for_user_start_instruction`
- 作成日時: `2026-07-19 20:23:33 JST`
- 更新日時: `2026-07-19 20:23:33 JST`
- Snapshot: `20260719202333`
- 作成担当: 設計者役担当Task
- 対象担当: 実装担当Task
- 正本言語: 日本語
- 要件: [phase_1f_lightning_cross_environment_runtime_requirements_20260719202333.md](../history/requirements/phase_1f_lightning_cross_environment_runtime_requirements_20260719202333.md)
- Architecture: [lightning_ai_studio_cross_environment_architecture_20260719202333.md](../history/architecture/lightning_ai_studio_cross_environment_architecture_20260719202333.md)
- ADR: [adr_0015_phase_1f_lightning_and_python_312_support_20260719202333.md](../history/adr/adr_0015_phase_1f_lightning_and_python_312_support_20260719202333.md)
- supersedes: `implementer_handoff_lightning_ai_studio_dual_runtime_profiles_20260719200711.md`

## 1. Objective

Phase 1公開前に、Mac 3.13／Metalを維持しながら、Lightning 3.12／CUDA Runtimeを同一Repositoryで成立させる。CPU Profileも実装対象とする。

## 2. Authorized Scope after User Start Instruction

```text
pyproject.toml
uv.lock
.python-version                 # 原則3.13.14維持。変更時は理由必須
config/
src/
tests/
scripts/
docs/handoffs/implementer_status_*
```

README／Public Docs／Git操作／GitHub操作はScope外である。

## 3. Work Packages

### WP-1 Python Compatibility

- `requires-python = ">=3.12,<3.14"`
- Lock再生成
- Ruff／Mypy最小Version 3.12
- 3.12／3.13 Dependency Resolution確認
- Mac Setup／Verifier Regression

### WP-2 Execution Environment

- Container Detection
- Platform Registry／Schema整合
- Native Mac互換性
- Pre-load Validation Test

### WP-3 CUDA Runtime

- CUDA Device Detection
- CUDA Profile
- Linux CUDA Setup Recipe
- Runtime Observation
- CUDA Unit／Native Smoke

### WP-4 CPU Runtime

- CPU Profile
- `gpu_layers=0`
- CUDA BuildによるCPU実行確認
- 不成立時はEvidenceをStatusへ記録し、別CPU Build案を提示

### WP-5 Acceptance Follow-up Coordination

- [implementer_handoff_phase_1_acceptance_follow_up_20260719195134.md](../history/handoffs/implementer_handoff_phase_1_acceptance_follow_up_20260719195134.md)のCLI Help／Token上限Warningを、同じMaterial Change Setまたは明確に分離したStatusで扱う。

## 4. Verification

Mac：

- Ruff／Mypy／Compileall
- Default Test
- Native Metal Smoke
- CLI User Test影響範囲

Lightning：

- Python 3.12.11
- Dependency／Lock
- Container Detection
- CUDA Build／System Info
- CUDA Profile Model Info
- Generate／Stream／Non-stream／Cancel／Unload
- Language／Thinking
- SHA-512
- CPU Profile Testまたは明示Finding

## 5. Status

実装完了時、新Timestampで最低限次を記録する。

```text
docs/handoffs/implementer_status_phase_1f_lightning_cross_environment_runtime_*.md
```

Mac／Lightningで実行したCommand、Version、Hardware、Build Option、Test結果、変更File、Known Limitation、CPU Dispositionを含める。

## 6. External Action Boundary

Repository変更は実装担当Taskで行う。Lightning上のPackage Install、CUDA Build、Model配置、GPU利用は外部環境操作であり、ユーザーがLightning側で実行するか、別途その操作を許可する。

## 7. Start Condition

本HandoffはAcceptedであり、ユーザーが実装担当TaskへPhase 1-F開始を明示した後に着手できる。

<!-- SOURCE_END 67: docs/handoffs/implementer_handoff_phase_1f_lightning_cross_environment_runtime_20260719202333.md -->

---

<!-- SOURCE_BEGIN 68: docs/handoffs/implementer_handoff_phase_1f_lightning_read_only_preflight_20260721010621.md -->

### Source 68: `docs/handoffs/implementer_handoff_phase_1f_lightning_read_only_preflight_20260721010621.md`

- History Target: `docs/project/phases/phase_1/history/handoffs/implementer_handoff_phase_1f_lightning_read_only_preflight_20260721010621.md`
- Source SHA-512: `21b9af6fd8fa8b5fd85e13268f68e7c9d272d987cf9456f072a02c1d58318ecee47eee9d45de06fae0093ddf9603f2ce064a32b2edb47987d456331c5c817d5c`
- Source Size: `8225` bytes

# 実装担当向け Phase 1-F Lightning Read-only Preflight Handoff

- 文書ID: `implementer_handoff_phase_1f_lightning_read_only_preflight`
- 状態: `accepted_ready_for_external_preflight`
- 作成日時: `2026-07-21 01:06:21 JST`
- 更新日時: `2026-07-21 01:06:21 JST`
- Snapshot: `20260721010621`
- 作成担当: 設計者役担当Task
- 対象担当: 実装担当Task
- 正本言語: 日本語
- 要件: [phase_1f_lightning_cross_environment_runtime_requirements_20260719202333.md](../history/requirements/phase_1f_lightning_cross_environment_runtime_requirements_20260719202333.md)
- Architecture: [lightning_ai_studio_cross_environment_architecture_20260719202333.md](../history/architecture/lightning_ai_studio_cross_environment_architecture_20260719202333.md)
- ADR: [adr_0015_phase_1f_lightning_and_python_312_support_20260719202333.md](../history/adr/adr_0015_phase_1f_lightning_and_python_312_support_20260719202333.md)
- Repository Accepted Review: [designer_review_phase_1f_minor_static_gate_follow_up_20260721010200.md](../history/handoffs/designer_review_phase_1f_minor_static_gate_follow_up_20260721010200.md)
- 最新Index: [documentation_index_20260721010621.md](../history/documentation_index_20260721010621.md)
- supersedes: なし（Lightning Read-only Preflight専用Handoffの初回）

## 1. Objective

Project本体、Model Artifact、Mac `.venv`をLightningへ搬入する前に、小型のPreflight Scriptだけを対象Lightning AI Studioで実行する。

次をRead-onlyに確認し、Full UploadとDependency Syncへ進める前提を確定する。

```text
Host OS               : Linux
Architecture          : x86_64
Distribution          : Ubuntu
Execution Environment : Container
Environment Mode      : studio-active または project-venv
Python                : 3.12.11
uv                    : 0.11.29
GPU Mandatory Path    : NVIDIA GPU割当をnvidia-smiで確認
nvcc                  : 有無のみ参考記録
```

## 2. Authorized External Action

Lightning Targetへ配置してよいProject Fileは、次の1ファイルだけである。

```text
scripts/setup/preflight_lightning_ai_studio.sh
```

次を許可する。

- 上記Script 1ファイルのLightning Targetへの配置
- Scriptの`--help`実行
- GPU用Read-only Preflight実行
- CPU候補用Read-only Preflight実行
- Command、Exit Code、標準出力、Safeな標準エラーの記録
- Local Repository側でのImplementer Status新規作成

## 3. Prohibited Actions

Preflight中は次を行わない。

- Project本体のFull Upload
- GGUF ModelのUpload／Download／Copy
- `.venv`のUpload／Copy／作成
- `uv sync`
- `pip install`
- Package Upgrade／Downgrade
- `llama-cpp-python`のBuild／Rebuild
- `nvcc`によるCompile
- Config／Source／Test／Scriptの変更
- Lightning Environment／GPU設定の変更
- Credential、Token、Cookie、Secretの表示または記録
- Git／GitHub操作

Preflightが失敗した場合も、その場で環境を修復しない。Failure Evidenceを保存して設計者Reviewへ戻す。

## 4. Transfer Boundary

Local MacのProject Tree全体をまだUploadしない。Preflight Script 1ファイルだけを、Lightning側の任意の作業Directoryまたは既存Project Treeの同一相対Pathへ配置する。

Mac `.venv`、`models` Symbolic Link、GGUF本体、Cache、Log、Credentialを一緒に転送しない。

Scriptは`bash`で直接実行できるため、Executable Bit変更は必須ではない。

## 5. Execution Procedure

### 5.1 Help確認

```bash
bash scripts/setup/preflight_lightning_ai_studio.sh --help
```

期待：

- Exit Code 0
- `auto`、`studio-active`、`project-venv`が表示される。
- `--cpu-only`が表示される。
- Environment作成、Package Install、`nvcc`要求を行わない旨が表示される。

### 5.2 GPU Mandatory Preflight

Tesla T4等のNVIDIA GPUがLightning Studioへ割り当てられている状態で実行する。

```bash
bash scripts/setup/preflight_lightning_ai_studio.sh \
  --environment-mode auto
```

合格条件：

- Exit Code 0
- `Phase 1-F Lightning preflight passed.`
- `Environment mode`が`studio-active`または`project-venv`
- Python 3.12.11
- uv 0.11.29
- `GPU required : 1`
- `nvidia-smi -L`によりAllocated NVIDIA GPUを確認できる。
- `nvcc available`は`yes／no`のどちらでもPreflight合格可

`nvcc`は後続のNative Rebuild要否を決める参考値であり、本Preflightでは必須にしない。

### 5.3 CPU Candidate Preflight

GPU割当がない場合、またはCPU候補の環境前提だけを確認する場合に実行する。

```bash
bash scripts/setup/preflight_lightning_ai_studio.sh \
  --environment-mode auto \
  --cpu-only
```

合格条件：

- Exit Code 0
- GPU割当や`nvidia-smi`を必須としない。
- Host／Container／Python／uv／Environment Mode条件がGPU Pathと同様に成立する。
- `GPU required : 0`

この合格は、GPUのない環境でllama.cpp Import／Model Load／Generateが成立した証明ではない。CPU Native GateはFull Upload後に別途実行する。

GPU割当中のStudioで`--cpu-only`を実行しても、GPU不在を証明したことにはならない。GPU Requirementを外したEnvironment Candidate確認としてのみ記録する。

## 6. Environment Mode Interpretation

```text
auto
  ├─ VIRTUAL_ENV／CONDA_PREFIXあり
  │    → studio-active
  └─ Active Prefixなし
       → project-venv
```

- `studio-active`の場合、Active Prefix配下の`bin/python`が3.12.11であることを確認する。
- `project-venv`の場合、本PreflightではVenvを作成せず、現在の`python3`が3.12.11であることだけを確認する。
- Auto Resolution結果をStatusへ記録し、後続Full Setupでは確定したModeを明示する。

## 7. Failure Handling

次のいずれかが発生した場合はPreflight不合格とする。

- Linux／x86_64／Ubuntu／Containerの不一致
- Pythonが3.12.11ではない。
- uvが存在しない、または0.11.29ではない。
- `studio-active`選択時にActive Prefixまたは`bin/python`がない。
- GPU Mandatory Pathで`nvidia-smi`またはAllocated GPUを確認できない。
- Scriptが非0で終了する。

不合格時は次を守る。

1. Exit CodeとSafeなError Messageを記録する。
2. Package Install、Version変更、Environment作成を行わない。
3. Model／Project Full Uploadへ進まない。
4. Failure原因と候補Follow-upをStatusへ記録する。
5. 設計者Reviewとユーザー判断へ戻す。

## 8. Evidence／Status Requirement

Preflight完了後、Local Repositoryへ新Timestampで次を作成する。

```text
docs/handoffs/implementer_status_phase_1f_lightning_read_only_preflight_YYYYMMDDHHMMSS.md
```

最低限、次を含める。

```text
Execution Date／Timezone
Lightning Environmentの一般的な識別名
GPU割当有無
GPU Name／Memory（取得できる場合）
Host OS／Architecture／Distribution／Container
Selected Environment Mode
Active Prefixの有無
Python Pathの種別／Version
uv Pathの種別／Version
nvcc Available yes／no
GPU Preflight Command／Exit Code／Output
CPU Candidate Command／Exit Code／Output
Pass／Fail／Not Runの区別
Failure時の未変更確認
Full Uploadへ進めるかの実装担当自己評価
```

公開やTask引き継ぎに不要な次の情報は記録しないか匿名化する。

- Credential／Token／Cookie／Secret
- LightningのPrivate Access URL
- Session ID
- Machine ID／Boot ID
- 個人名を含むPath
- 不要なIP Address／Hostname

実行していない項目をPass扱いしない。

## 9. Review Gate

Preflight Status作成後、設計者役へReviewを依頼する。

設計者ReviewがAcceptedになるまで、次へ進まない。

```text
Project Full Upload
Model Upload
Dependency Sync
Native Build／Reuse
CUDA／CPU Acceptance
```

## 10. Start Condition

本HandoffはAcceptedであり、ユーザーの本Turnにおける「次はLightning Read-only Preflightへ進めます。よろしく。」を開始指示として扱う。

実装担当は本Handoff、最新Index、Repository Accepted Reviewを読んだ後、Section 2の範囲でPreflightへ着手できる。

<!-- SOURCE_END 68: docs/handoffs/implementer_handoff_phase_1f_lightning_read_only_preflight_20260721010621.md -->

---

<!-- SOURCE_BEGIN 69: docs/handoffs/implementer_handoff_phase_1g_cross_thread_cancel_follow_up_20260721122621.md -->

### Source 69: `docs/handoffs/implementer_handoff_phase_1g_cross_thread_cancel_follow_up_20260721122621.md`

- History Target: `docs/project/phases/phase_1/history/handoffs/implementer_handoff_phase_1g_cross_thread_cancel_follow_up_20260721122621.md`
- Source SHA-512: `4094ed2b424b12b1703050dd677ef7f4748d6421fec8b2b2c94ef5df2a0e7294d31ca825f624de25bdfa0fd3c958572b8f1c20ed03ef49d157d9c9c9173f35e3`
- Source Size: `5227` bytes

# 実装担当向け Phase 1-G Cross-thread Cancel Follow-up Handoff

- 文書ID: `implementer_handoff_phase_1g_cross_thread_cancel_follow_up`
- 状態: `waiting_user_implementation_authorization`
- 作成日時: `2026-07-21 12:26:21 JST`
- 更新日時: `2026-07-21 12:26:21 JST`
- Snapshot: `20260721122621`
- 作成担当: 設計者役担当Task
- 対象担当: 実装担当Task
- 正本言語: 日本語
- Review: [designer_review_phase_1g_review_follow_up_20260721122621.md](../history/handoffs/designer_review_phase_1g_review_follow_up_20260721122621.md)
- 実装報告: [implementer_status_phase_1g_review_follow_up_20260721121817.md](../history/handoffs/implementer_status_phase_1g_review_follow_up_20260721121817.md)
- 前回Handoff: [implementer_handoff_phase_1g_review_follow_up_20260721115330.md](../history/handoffs/implementer_handoff_phase_1g_review_follow_up_20260721115330.md)
- 最新Index: [documentation_index_20260721122621.md](../history/documentation_index_20260721122621.md)
- supersedes: `implementer_handoff_phase_1g_review_follow_up_20260721115330.md`

## 1. Current State

前回FindingのQueue Backpressure、Token Exhaustion UI、Public Namingは解消した。Static／Default／Web／Mac Native Gateも合格している。

残件は、Event Loop ThreadからProducer Thread上で実行中のNative Python Generatorへ即時`force_cancel()`するCross-thread競合1件だけである。

## 2. Authorized Scope after User Approval

ユーザーが追加Follow-up開始を明示した後、次の範囲だけ変更できる。

```text
src/margpa_runtime_llm/web/streaming.py
tests/integration/web/test_web_app.py
tests/unit/web/                         # 必要な場合だけ
docs/handoffs/implementer_status_phase_1g_cross_thread_cancel_follow_up_*
```

Backend Contract変更が不可避な場合は、実装前に理由、最小変更範囲、既存CLIへの影響を設計者役へ返す。まずWeb Boundary内のThread-affine Cooperative Cancelで解決する。

## 3. Required Work

1. Consumer終了時に`consumer_stopped`を設定する。
2. `session.request_cancel()`でCooperative Cancelを要求する。
3. Event Loop Threadから実行中Native Generatorへ即時`session.force_cancel()`しない。
4. Queue投入待ちはCurrent Pollingで解除し、Producer Thread自身がSession IteratorをCloseする。
5. Producer Threadが次Chunk境界でCancelを観測し、同一Thread上でNative StreamをCancel／Closeする。
6. Producer終了、Session `finally`、Generation Gate解放を待つ。
7. Timeout時は成功扱いせず、Thread-unsafeなGenerator Closeで結果を偽装しない。
8. Timeout EscalationにNative強制停止が必要なら、Backend保証のThread-safe Stop Signalを設計し、先に設計者役へEscalateする。

## 4. Required Regression Test

Fake StreamへThread Affinityを持たせる。

```text
Iteration Thread IDを記録
cancel／closeが別Threadなら例外
ProducerがNative next()中にConsumerをClose
```

Testは次をAssertする。

- Async Generator CloseがCross-thread `cancel／close`例外を出さない。
- Producer Thread上でCancel／Closeされる。
- Sessionが限定時間内に完了する。
- `active_request_id is None`になる。
- Producer Taskが残らない。
- 直後の次Generationが`completed`になる。
- Current Queue Capacity超過Regressionも引き続き合格する。

可能であれば、Production `LlamaCppGenerationStream`とBlocking Native Generatorを使ったUnit／Integration Testも追加し、`generator already executing`を再発防止する。

## 5. Required Verification

```bash
./.venv/bin/ruff format --check src scripts tests
./.venv/bin/ruff check src scripts tests
./.venv/bin/mypy .
./.venv/bin/python -m compileall -q src scripts tests
./.venv/bin/pytest -q
./.venv/bin/pytest -q tests/unit/conversation tests/unit/web tests/integration/web
./.venv/bin/pytest -q -m model_smoke
uv lock --check --offline
bash -n scripts/setup/*.sh
```

Mac Manual Browserで、Stop、Post-cancel Generation、New Chatを再確認する。大規模Lightning Uploadはまだ行わない。

## 6. Implementer Status Requirement

完了後、次を作成する。

```text
docs/handoffs/implementer_status_phase_1g_cross_thread_cancel_follow_up_YYYYMMDDHHMMSS.md
```

Statusへ次を記録する。

- Cross-thread競合の修正方式
- Cancel／Closeを実行するThread境界
- Timeout時の動作
- Regression Testの再現条件と結果
- 全Verification CommandのExit Code／件数
- Manual Stop／Post-cancel結果
- Phase 1-H未着手の明記

## 7. Out of Scope

- 解消済みToken Warning UIの再設計
- 解消済みPublic Namingの再変更
- Phase 1-H Summary Mode
- React／本格UI／Conversation永続化
- Runtime Governance／Guardrail／Judge／Repair／Agent／RAG
- Lightning Full Upload／Model Transfer
- Phase 1完了宣言／Backup
- Phase 1-ex／Git／GitHub公開

## 8. Start Condition

本Handoffは準備済みだが、実装開始指示ではない。

ユーザーが実装担当TaskへPhase 1-G Cross-thread Cancel Follow-up開始を明示した時点で、Section 2の限定範囲を変更できる。

## 9. Append-Only

既存文書を変更せず、新TimestampのHandoffとして追加した。

<!-- SOURCE_END 69: docs/handoffs/implementer_handoff_phase_1g_cross_thread_cancel_follow_up_20260721122621.md -->

---

<!-- SOURCE_BEGIN 70: docs/handoffs/implementer_handoff_phase_1g_minimal_web_surface_20260721093952.md -->

### Source 70: `docs/handoffs/implementer_handoff_phase_1g_minimal_web_surface_20260721093952.md`

- History Target: `docs/project/phases/phase_1/history/handoffs/implementer_handoff_phase_1g_minimal_web_surface_20260721093952.md`
- Source SHA-512: `8770330bf047664caf7c63fffaff9ec725c624a0531e114da36e88ba5c9e8f74c84c0a77418277748d9ac05ce8e2fd7191d6e1c3c3e98000ff2aee7942e62d98`
- Source Size: `18439` bytes

# 実装担当向け Phase 1-G Minimal Web Surface Handoff

- 文書ID: `implementer_handoff_phase_1g_minimal_web_surface`
- 状態: `accepted_ready_for_implementation`
- 作成日時: `2026-07-21 09:39:52 JST`
- 更新日時: `2026-07-21 09:39:52 JST`
- Snapshot: `20260721093952`
- 作成担当: 設計者役担当Task
- 対象担当: 実装担当Task
- 正本言語: 日本語
- 要件: [phase_1g_minimal_web_surface_requirements_20260721093952.md](../history/requirements/phase_1g_minimal_web_surface_requirements_20260721093952.md)
- Architecture: [phase_1g_minimal_web_surface_architecture_20260721093952.md](../history/architecture/phase_1g_minimal_web_surface_architecture_20260721093952.md)
- ADR: [adr_0016_batch_lightning_upload_after_phase_1h_20260721093952.md](../history/adr/adr_0016_batch_lightning_upload_after_phase_1h_20260721093952.md)
- Roadmap: [implementation_roadmap_20260721093952.md](../history/architecture/implementation_roadmap_20260721093952.md)
- Phase 1-H予約要件: [post_generation_summary_mode_requirements_reservation_20260721090725.md](../history/requirements/post_generation_summary_mode_requirements_reservation_20260721090725.md)
- 最新Index: [documentation_index_20260721093952.md](../history/documentation_index_20260721093952.md)
- supersedes: なし（Phase 1-G実装開始用Handoffの初回）

## 1. Objective

既存のPhase 1 CLI／Model Adapter／Presentation機能を壊さず、Macと将来のLightning AI Studioで同じApplication Coreを利用できる、公開検証用の最小Web Surfaceを追加する。

Phase 1-Gの完成時点で、Browserから次を実行可能にする。

```text
新規Chat
一時的な複数Turn会話
Streaming回答
生成停止
Response Language変更
Max New Tokens変更
推論過程表示のON／OFF
Preview用Access Control
Health Check
```

本Phaseは本格UIではない。Phase 4でReact等へ交換可能なAPI境界と、他者がLightning上で試せる最小UIを成立させることが目的である。

## 2. Implementation Authorization

本Handoffにより、実装担当はPhase 1-Gに必要な次の変更を行ってよい。

- `pyproject.toml`
- `uv.lock`
- `config/application.toml`
- `src/`
- `tests/`
- `scripts/`
- Phase 1-Gの実行に必要なLocal Static Asset
- `docs/handoffs/implementer_status_phase_1g_minimal_web_surface_*`

実装担当は既存の要件・Architecture・Governance・ADR・Roadmap・Indexを読み取り専用として扱う。実装中に正本の変更が必要になった場合は、勝手に編集せず設計者役へ戻す。

## 3. Prohibited／Deferred Scope

Phase 1-Gでは次を実施しない。

- Phase 1-H Summary Modeの実装
- Summary Modeの未実装SwitchをUIへ表示すること
- Chat履歴の永続化
- Database／SQLite
- RAG
- Agent
- Guardrail Model
- Judge Model
- Runtime Governance本体
- User Account管理
- OAuth／OIDC
- TLS終端
- Rate Limitの本格実装
- React／Next.js／Node Build環境
- CDN／外部JavaScript／外部CSS
- Markdown HTML Rendering
- 複数Worker／複数Model Instance
- LightningへのProject Full Upload
- Lightning上でのDependency Install／Native Build／Model Transfer
- Backup、Git、GitHub公開

Lightningへの大量Uploadは、Phase 1-GとPhase 1-HをMacで受入後、一回にまとめる。Phase 1-FのLightning Native VerificationはDeferredのままであり、完了扱いにしない。

## 4. Work Package 1: Dependency／Setup

### 4.1 Dependency

次をVersion固定で追加する。

```text
Web Optional Extra
  fastapi==0.139.2
  uvicorn==0.51.0

Development／ASGI Test
  httpx==0.28.1
```

方針：

- `fastapi[standard]`は使用しない。
- `uvicorn[standard]`は初期導入しない。
- Jinja2、SSE専用Package、React、Nodeを追加しない。
- Web依存を推論Coreの必須依存へ直接混在させず、`web` Optional Extraとして分離する。
- Development Groupへ`httpx`を追加し、FastAPI／ASGI Test Clientに用いる。
- `uv.lock`を更新し、Mac 3.13.14とLightning 3.12.11の両方をSupport Pairとして維持する。

### 4.2 Setup Recipe

- MacのSetupでWeb Extraを選択できるようにする。
- Lightning Setup RecipeにもWeb Extraを含められるようRepositoryだけ更新する。
- 本PhaseではLightning上でSetup Recipeを実行しない。
- 通常同期と`llama-cpp-python` Native Rebuildの責務を混同しない。

## 5. Work Package 2: Conversation／Application Boundary

### 5.1 Conversation Contract

Web RequestのMessage履歴は、明示的なTyped Contractとして受け取る。

最低要件：

```text
Allowed Role       : user／assistant
Disallowed Role    : system／developer／tool等
Empty Content      : Reject
Invalid Type       : Reject
Oversized Request  : Explicit Reject
```

BrowserからSystem Messageを注入させない。System InstructionとResponse Language InstructionはServer側で構成する。

### 5.2 History Ownership

- Chat履歴はBrowser Tab側が所有する。
- ServerのGlobal Mutable Stateへ利用者別Historyを保持しない。
- 複数Browser／複数利用者の履歴を混在させない。
- New ChatはBrowser Stateを消去し、Server ModelをReloadしない。
- Browser Reload後の履歴復元はPhase 1-G対象外である。

### 5.3 Context Handling

- Clientから受けた履歴を順序どおりModelへ渡せるMessage Composerを追加する。
- 既存のOne-shot CLI Message Composerを壊さない。
- Context超過時に履歴を無断要約または無断切捨てしない。
- Context Limitに収まらない場合は、明示的なValidation Errorとして返す。

### 5.4 Request Override

Web Request単位で次だけをOverrideできる。

```text
response.language                : ja／en／auto
generation.max_new_tokens        : integer
presentation.thinking.visibility : hidden／visible
```

Config FileをRequestごとに書き換えない。Effective ConfigをBaseとして、Validated Request OverrideをMemory上で合成する。

`generation.thinking_mode`と`presentation.thinking.visibility`は別の設定である。Visibilityの切替だけでThinking ExecutionをON／OFFしない。

## 6. Work Package 3: Web API

### 6.1 Application Factory／Lifecycle

- FastAPI Application Factoryを追加する。
- Model／Inference Service／Presentation ServiceはDependency Injectionする。
- Server Lifecycle中にModelを一度だけLoadする。
- RequestごとのModel Reloadを禁止する。
- TestではFake Service／Fake Streamを注入できるようにする。

### 6.2 Endpoint Contract

最低限、次の責務を分離する。

```text
GET  /healthz         : Process Healthのみ
GET  /                : Minimal UI
GET  /assets/...      : Local Static Asset
GET  /api/runtime     : UIに必要なSafe Runtime情報
POST /api/chat/stream : Streaming Generation
POST /api/chat/stop   : Cooperative Cancellation
```

Path名は局所的な実装都合により軽微変更可能だが、責務、認証境界、Testabilityを維持し、Statusへ最終Contractを記録する。

### 6.3 Streaming Envelope

Streaming Eventを明示的なSchemaで返す。

最低Event候補：

```text
start
delta
thinking_delta または presentation_delta
final
cancelled
error
done
```

要件：

- Event TypeとPayloadを区別する。
- Canonical Final AnswerとThinking Presentationを混同しない。
- Final Answer前にToken上限へ到達した場合、空成功にせず、`最終回答を生成する前にToken上限へ到達しました。`相当の明示状態を返す。
- Exception Trace、Local Path、Credential、内部Object RepresentationをClientへ返さない。
- Client切断時は可能な限りGenerationをCancelする。

### 6.4 Error Mapping

最低限、次を区別する。

```text
400／422 : Invalid Input／Invalid Setting
401      : Authentication Required／Failed
409      : Generation Busy
413      : Request Too Large候補
500      : Sanitized Internal Error
503      : Runtime Not Ready候補
```

## 7. Work Package 4: Concurrency／Cancellation

Phase 1-Gは次へ固定する。

```text
ASGI Worker                 : 1
Model Load Instance         : 1
Max Concurrent Generations : 1
Second Generation          : 409 Busy
Cancellation               : Cooperative
```

- Thread-safeなGeneration Gateを設ける。
- 同時Requestで同じModel Instanceを破損させない。
- Syncなllama.cpp StreamでASGI Event Loopを長時間Blockしないよう、Thread／Iterator境界を設ける。
- Stop APIとClient Disconnectの両方からCancel可能にする。
- Cancel後にGateが確実に解放され、次Generationを開始できることをTestする。
- Server起動時に`--workers 2`等を受け付けて複数Model Loadされる状態を許さない。

## 8. Work Package 5: Preview Access Control

### 8.1 Basic Policy

Phase 1-Gの公開Access Controlは、Server-side Basic Authentication相当の最小機構とする。

CredentialはEnvironment Variableからのみ受け取る。Config、Source、Docs、Log、Responseへ保存しない。

推奨Environment Keyは実装時に確定してよいが、`MARGPA_WEB_AUTH_*` Namespaceへ統一する。

### 8.2 Fail-closed

```text
Loopback Bind + Auth Disabled
  → Local Developmentとして許可

Non-loopback Bind + Credentialあり
  → 起動許可

Non-loopback Bind + Credentialなし
  → 起動失敗
```

- `0.0.0.0`、公開Host等でCredentialなしの起動を禁止する。
- `/healthz`だけはCredential不要の最小Health Responseとする。
- `/`、Static Asset、全`/api/*`は保護する。
- Runtime InfoではPrivate Path、Environment Value、Credentialを返さない。
- Authentication Failureの比較はTiming Attackを不必要に悪化させない標準手法を用いる。

Basic AuthはPreview用であり、本番Account SystemではないことをUI／Manual／Statusへ明記する。

## 9. Work Package 6: Minimal UI

UIはRepository内のVanilla HTML／CSS／JavaScriptで構築する。

### 9.1 Required UI

```text
Chat表示領域
入力欄
送信Button
停止Button
新規Chat Button
Response Language Pull-down
Max New Tokens Integer Input
推論過程表示 ON／OFF Switch
Streaming状態／Error表示
```

### 9.2 Setting Values

```text
Response Language
  ja／en／auto

Max New Tokens
  Default: 2048

Thinking Visibility
  Default: OFF／hidden
```

### 9.3 Thinking Wording

既存初期Labelを次のように変更する。

```text
旧: 高度推論
新: 推論過程
```

UI上は`推論過程（モデル生成）`等、内部の真のChain of Thoughtを保証するものではないと分かる表記にする。

近傍へ次の意味の注記を表示する。

> 推論過程表示は、モデルが出力したThinking区間の表示を切り替えます。推論実行自体のON／OFFではありません。Max New Tokensが小さい場合、最終回答前に上限へ到達することがあります。

### 9.4 Rendering Safety

- Model OutputはTextとして表示する。
- `innerHTML`へModel Outputを直接代入しない。
- Phase 1-GではMarkdown Rendererを導入しない。
- Local Static Assetだけを使い、CDNへ依存しない。
- UIが停止／切断／Errorを区別して表示する。
- Summary Mode SwitchはPhase 1-H完成まで表示しない。

## 10. Work Package 7: Start Command

Web専用Entry Pointを追加する。

推奨名：

```text
margpa-web
```

最低Option候補：

```text
--host
--port
--profile
--registry
--model-root
--model-key
--context-size
```

要件：

- 既存`margpa-llm` CLIを変更または破壊しない。
- Default Hostは`127.0.0.1`とする。
- Default Portは衝突しにくい明示値を決め、Helpへ表示する。
- ReloadはDefault無効とする。
- Worker数は1へ固定する。
- `--help`で大文字の`HOST`、`PROFILE`等が実値ではなく仮引数名であることが利用者に分かるDescriptionを付ける。

## 11. Proposed File Boundary

実装担当は既存構造との整合を確認し、概ね次の責務分離を行う。File名は軽微変更可能だが、Web Framework固有CodeをCoreへ漏らさない。

```text
src/margpa_runtime_llm/
  web/
    app.py
    dependencies.py
    auth.py
    contracts.py
    streaming.py
    static/
      index.html
      app.css
      app.js
  application／inference/
    conversation message composition／request override
  cli／entrypoint/
    web command

tests/
  unit/
    web auth／contract／conversation／stream／cancel
  integration/
    ASGI endpoint／busy／disconnect／static safety
```

FastAPI Type、Request、Response、Depends等をDomain／Model AdapterへImportしない。

## 12. Required Tests

最低限、次を自動Testする。

### 12.1 Regression

- 既存Testが全件合格する。
- `margpa-llm generate`／`model-info`が破壊されていない。
- Existing Model Smokeが合格する。
- Default Max New Tokensが2048のままである。
- Default Thinking Visibilityがhiddenである。
- Default Display Labelが`推論過程`へ統一される。

### 12.2 Contract／Config

- ja／en／autoだけを受理する。
- Max New Tokensの範囲外、Bool、Float、文字列等を安全に拒否する。
- Clientのsystem Roleを拒否する。
- Empty Message／Invalid Historyを拒否する。
- Request OverrideがConfig Fileを変更しない。
- New ChatでModel Reloadしない。

### 12.3 Auth

- Loopback＋Auth Disabledは起動可能。
- Non-loopback＋Credentialなしは起動拒否。
- Non-loopback＋Credentialありは起動可能。
- `/healthz`以外は未認証で拒否。
- Error／Runtime Info／LogへCredentialが出ない。

### 12.4 Streaming／Concurrency

- Streaming Event順序。
- Final AnswerとThinking区間の分離。
- Hidden時にThinkingをClient表示Payloadへ混ぜない。
- Cancel後に次Generationが可能。
- Concurrent Generationは409。
- Generator Exception時にGateを解放する。
- Client Disconnect時のCancel処理。
- Final Answer前Token Exhaustionを明示する。

### 12.5 UI Safety

- Model OutputがHTMLとして注入されない。
- Static AssetがLocalだけで完結する。
- Summary Modeの未実装Controlが存在しない。
- UIに3設定だけが公開される。

## 13. Verification Commands

Repository実装後、少なくとも次を実行する。CommandはRepositoryの確定Setup Scriptに合わせて必要最小限の調整をしてよい。

```bash
./.venv/bin/ruff format --check src scripts tests
./.venv/bin/ruff check src scripts tests
./.venv/bin/mypy .
./.venv/bin/python -m compileall -q src scripts tests
./.venv/bin/pytest -q
./.venv/bin/pytest -q -m model_smoke
bash -n scripts/setup/*.sh
```

Web依存導入とLock整合も確認する。

```bash
uv lock --check
./.venv/bin/python -c "import fastapi, uvicorn, httpx; print(fastapi.__version__, uvicorn.__version__, httpx.__version__)"
```

Mac Manual Smoke候補：

```bash
./.venv/bin/margpa-web --host 127.0.0.1 --port 8000
```

公開Bind Testでは実CredentialをCommand HistoryやStatusへ記録しない。PlaceholderだけをDocsへ書く。

Manual Smokeでは次を確認する。

1. BrowserでUIが開く。
2. 日本語PromptへStreaming回答する。
3. New Chatで履歴が消える。
4. Stopで生成を中断でき、その後再生成できる。
5. ja／en／autoを切り替えられる。
6. Max New Tokens初期値が2048である。
7. Thinking Visibility初期値がOFFである。
8. ON時は`推論過程`として表示される。
9. 別Tabの履歴がServer側で混ざらない。
10. Non-loopback＋CredentialなしでFail-closedになる。

## 14. Acceptance Criteria

次をすべて満たした場合にPhase 1-G実装完了候補とする。

- Requirements／ArchitectureのMandatory項目が実装済み。
- CLI Regressionなし。
- ModelはProcess中に一度だけLoadされる。
- Browser単位のEphemeral Multi-turnが成立する。
- Streaming／Stop／New Chatが成立する。
- UIの設定は指定3項目だけである。
- Max New Tokens Defaultは2048である。
- Thinking VisibilityとThinking Executionが分離されている。
- Token Exhaustionが空Responseにならず明示される。
- Preview Access ControlがFail-closedである。
- Model Output RenderingがPlain Textとして安全である。
- 全Static／Unit／Integration／Model Smokeが合格する。
- LightningへまだFull Uploadしていない。

## 15. Implementer Status Requirement

完了後、次の新規文書を作成する。

```text
docs/handoffs/implementer_status_phase_1g_minimal_web_surface_YYYYMMDDHHMMSS.md
```

最低限、次を含める。

```text
実装概要
変更File一覧
最終Endpoint Contract
最終CLI／Entry Point
Dependency Version／Lock変更
Auth Environment Key名（値は記載禁止）
Default Host／Port
Conversation History Ownership
Model Load回数の設計根拠
Concurrency／Cancellation方式
Thinking Presentation変更
Token Exhaustionの扱い
実行した全Verification Command／Exit Code／結果
Test総数
Manual Smoke結果
未実行項目
既知の制約
Phase 1-Hへ渡すInterface
Lightning Full Uploadを実施していないこと
```

Status作成後、設計者役へRepositoryとStatusのReviewを依頼する。Accepted Review前にPhase 1-Hへ着手しない。

## 16. Stop／Escalation Conditions

次の場合は推測で進めず、実装を停止して設計者へ戻す。

- llama.cpp AdapterのPublic Contract変更が必要
- Phase 1 CLIの互換性を壊す必要がある。
- Multiple Worker／Multiple Model Loadが避けられない。
- Authentication SecretをConfig／Fileへ保存する必要が生じる。
- CDN、Node、React、本格Databaseが必要になる。
- Context Overflowを無断切捨てしないと成立しない。
- Phase 1-H Summary Modeを同時実装しないと成立しない。
- Lightningへ先にFull Uploadする必要が生じる。
- Canonical Docsの要件間に矛盾が見つかる。

## 17. Start Condition

本HandoffはAcceptedである。ユーザーの本Turnにおける「実装担当への指示書を作って」を、Phase 1-G設計の正式引き渡し指示として扱う。

実装担当は本Handoff、Requirements、Architecture、ADR、Roadmap、最新Indexを読み、Phase 1-Gだけへ着手できる。


<!-- SOURCE_END 70: docs/handoffs/implementer_handoff_phase_1g_minimal_web_surface_20260721093952.md -->

---

<!-- SOURCE_BEGIN 71: docs/handoffs/implementer_handoff_phase_1g_review_follow_up_20260721115330.md -->

### Source 71: `docs/handoffs/implementer_handoff_phase_1g_review_follow_up_20260721115330.md`

- History Target: `docs/project/phases/phase_1/history/handoffs/implementer_handoff_phase_1g_review_follow_up_20260721115330.md`
- Source SHA-512: `3c5111b2196719db39612e6a8b1f4dc85e62e167abd679c3c3c97870295831c64524e0fb9127845a873f4798e88d48da65d036c0e8d565a73efd964e19075a8b`
- Source Size: `6090` bytes

# 実装担当向け Phase 1-G Review Follow-up Handoff

- 文書ID: `implementer_handoff_phase_1g_review_follow_up`
- 状態: `waiting_user_implementation_authorization`
- 作成日時: `2026-07-21 11:53:30 JST`
- 更新日時: `2026-07-21 11:53:30 JST`
- Snapshot: `20260721115330`
- 作成担当: 設計者役担当Task
- 対象担当: 実装担当Task
- 正本言語: 日本語
- Review: [designer_review_phase_1g_minimal_web_surface_20260721115330.md](../history/handoffs/designer_review_phase_1g_minimal_web_surface_20260721115330.md)
- 要件: [phase_1g_minimal_web_surface_requirements_20260721093952.md](../history/requirements/phase_1g_minimal_web_surface_requirements_20260721093952.md)
- Architecture: [phase_1g_minimal_web_surface_architecture_20260721093952.md](../history/architecture/phase_1g_minimal_web_surface_architecture_20260721093952.md)
- 実装報告: [implementer_status_phase_1g_minimal_web_surface_20260721105005.md](../history/handoffs/implementer_status_phase_1g_minimal_web_surface_20260721105005.md)
- 最新Index: [documentation_index_20260721115330.md](../history/documentation_index_20260721115330.md)
- supersedes: なし（Phase 1-G Review Follow-up Handoff系列の初回）

## 1. Current State

Phase 1-GのStatic／Default／Web／Mac Native Model Smokeは合格した。Architecture、Conversation分離、3設定、Basic Auth、Plain Text Rendering、既存CLI非回帰の主要部分も成立している。

ただし、設計ReviewでMandatory Finding 3系統を確認したため、Phase 1-GはChanges Requestedである。Phase 1-Hへはまだ進まない。

## 2. Authorized Scope after User Approval

ユーザーがFollow-up開始を明示した後、次の範囲だけ変更できる。

```text
src/margpa_runtime_llm/web/streaming.py
src/margpa_runtime_llm/web/static/app.js
src/margpa_runtime_llm/web/static/index.html
src/margpa_runtime_llm/__init__.py
tests/unit/web/
tests/integration/web/
docs/handoffs/implementer_status_phase_1g_review_follow_up_*
```

責務分離に必要な最小限のHelper追加は可能だが、Inference／Presentation Core Contractを不用意に変更しない。

## 3. Required Work

### 3.1 Disconnect／Backpressure Cleanup

1. Consumer終了をProducerへ確実に伝える。
2. Bounded Queue満杯時でもProducerが投入待ちから脱出できるようにする。
3. Client Disconnect／Async Generator Close後にSession IteratorをCloseする。
4. Native Stream Cancel、Producer終了、Session `finally`、Generation Gate解放の順序を安全に成立させる。
5. Cleanup Timeout時もOrphan Producerを残したまま成功扱いしない。
6. Queue Capacityを超えるEvent列でConsumerを早期CloseするTestを追加する。
7. 限定時間内の終了、`active_request_id is None`、次Generation成功をAssertする。

実装方式は固定しない。ただし、Unbounded Queueへの変更、Event Loop上での同期Generation、Threadを放置する回避は不可とする。

### 3.2 Token Exhaustion UI

1. `final_answer_token_limit` WarningをRequest単位で保持する。
2. 直後の`completed`でWarning Statusを上書きしない。
3. Canonical Finalが空の場合も、画面へ次を明示する。

```text
最終回答を生成する前にToken上限へ到達しました。
```

4. Warning TextをCanonical Assistant Historyへ追加しない。
5. Empty Assistant Bubbleだけを残さない。
6. `warning → completed` Event列後の最終UI Stateを決定論的に検証する。

### 3.3 Public Naming

次の2箇所を`Nazuna Research Governance LLM`へ統一する。

```text
src/margpa_runtime_llm/__init__.py
src/margpa_runtime_llm/web/static/index.html
```

修正後、Source／Test／Script／Config／Root Metadataを検索し、廃止済み第一者名義が0件であることをStatusへ記録する。Third-partyの作者名、Model Provenance、Repository IDは意味を確認し、機械的一括置換しない。

## 4. Required Verification

最低限、次を実行する。

```bash
./.venv/bin/ruff format --check src scripts tests
./.venv/bin/ruff check src scripts tests
./.venv/bin/mypy .
./.venv/bin/python -m compileall -q src scripts tests
./.venv/bin/pytest -q
./.venv/bin/pytest -q tests/unit/conversation tests/unit/web tests/integration/web
./.venv/bin/pytest -q -m model_smoke
uv lock --check --offline
bash -n scripts/setup/*.sh
```

追加Regression Testは、通常の短いDisconnectだけでなく、Queue Capacity超過／Consumer早期終了を再現する。

Mac Manual Browser Smokeで次を補完する。

1. `response_language=auto`でStreamingと最終回答が成立する。
2. Thinkingを有効にし、最終回答前Token Exhaustionを発生させた場合にSafe Warningが残る。
3. Warning後、New Chatまたは再送信が正常にできる。
4. Stop／Post-cancel Generationが引き続き成立する。

## 5. Implementer Status Requirement

完了後、次の新Timestamp文書を作成する。

```text
docs/handoffs/implementer_status_phase_1g_review_follow_up_YYYYMMDDHHMMSS.md
```

Statusへ次を記録する。

- 変更Fileと責務
- Backpressure Disconnectの再現条件、修正方式、解放Evidence
- Token Exhaustion Event列と最終UI表示
- Public Naming検索範囲と0件結果
- 全CommandのExit Code／Test件数
- Manual Browser `auto`／Warning／Post-cancel結果
- 未実行項目、Known Limit、Phase 1-H未着手の明記

## 6. Out of Scope

- Phase 1-H Summary Mode
- React／Node／本格UI
- Conversation永続化
- Markdown Rendering
- Developer／Research Settings UI
- Auth方式の本格化
- Runtime Governance／Guardrail／Judge／Repair／Agent／RAG
- Lightning Full Upload／Model Transfer／Native Gate
- Phase 1完了宣言／Backup
- Phase 1-ex／Git／GitHub公開

## 7. Start Condition

本Handoffは準備済みだが、実装開始指示ではない。

ユーザーが実装担当TaskへPhase 1-G Follow-up開始を明示した時点で、Section 2の限定範囲を変更できる。

## 8. Append-Only

既存文書を変更せず、新TimestampのHandoffとして追加した。

<!-- SOURCE_END 71: docs/handoffs/implementer_handoff_phase_1g_review_follow_up_20260721115330.md -->

---

<!-- SOURCE_BEGIN 72: docs/handoffs/implementer_handoff_phase_1g_shutdown_cancel_follow_up_20260721164248.md -->

### Source 72: `docs/handoffs/implementer_handoff_phase_1g_shutdown_cancel_follow_up_20260721164248.md`

- History Target: `docs/project/phases/phase_1/history/handoffs/implementer_handoff_phase_1g_shutdown_cancel_follow_up_20260721164248.md`
- Source SHA-512: `260014d51880fae1abcff2d71e062c1fba55bccc34796c9d33dc75cb9e779c2b0821ce05daa4886e628da8805002d346719b8c89c70513b6027503b1b59950ca`
- Source Size: `6217` bytes

# 実装担当向け Phase 1-G Shutdown Cancel Follow-up Handoff

- 文書ID: `implementer_handoff_phase_1g_shutdown_cancel_follow_up`
- 状態: `waiting_user_implementation_authorization`
- 作成日時: `2026-07-21 16:42:48 JST`
- 更新日時: `2026-07-21 16:42:48 JST`
- Snapshot: `20260721164248`
- 作成担当: 設計者役担当Task
- 対象担当: 実装担当Task
- 正本言語: 日本語
- Review: [designer_review_phase_1g_cross_thread_cancel_follow_up_20260721164248.md](../history/handoffs/designer_review_phase_1g_cross_thread_cancel_follow_up_20260721164248.md)
- 実装報告: [implementer_status_phase_1g_cross_thread_cancel_follow_up_20260721150603.md](../history/handoffs/implementer_status_phase_1g_cross_thread_cancel_follow_up_20260721150603.md)
- 前回Handoff: [implementer_handoff_phase_1g_cross_thread_cancel_follow_up_20260721122621.md](../history/handoffs/implementer_handoff_phase_1g_cross_thread_cancel_follow_up_20260721122621.md)
- 最新Index: [documentation_index_20260721164248.md](../history/documentation_index_20260721164248.md)
- supersedes: `implementer_handoff_phase_1g_cross_thread_cancel_follow_up_20260721122621.md`

## 1. Current State

SSE Disconnect／Consumer CloseのCross-thread Cancelは解消した。残件はActive Generation中のRuntime ShutdownにおけるCross-thread `force_cancel()`と1件である。

```text
Resolved : SSE Event Loop → Native Generator force_cancel
Remaining: Shutdown Worker → Native Generator force_cancel
Impact   : ValueError、Model Close Callback未到達、Shutdown Failure抑制
```

Phase 1-GはChanges Requested、Phase 1-HはWaitingである。

## 2. Authorized Scope after User Approval

ユーザーが追加Follow-up開始を明示した後、次の範囲だけ変更できる。

```text
src/margpa_runtime_llm/modules/conversation/application/conversation_generation.py
src/margpa_runtime_llm/web/contracts.py
src/margpa_runtime_llm/web/app.py
tests/unit/conversation/
tests/unit/web/
tests/integration/web/test_web_app.py
docs/handoffs/implementer_status_phase_1g_shutdown_cancel_follow_up_*
```

Backend Contractとllama.cpp Adapterの変更が不可避な場合、実装前に理由、Thread-safe保証、CLIへの影響、最小変更範囲を設計者役へ戻す。

## 3. Required Work

1. `ConversationGenerationService.shutdown()`のTimeout経路からThread-unsafeな`session.force_cancel()`を除去する。
2. `request_cancel()`とProducer Iteration Thread上のNative Cancel／Closeを正規Shutdown経路とする。
3. Timeout時は成功を偽装せず、`False`または明示例外とする。
4. SessionがまだActiveな場合、Model Close Callbackを先に呼ばない。
5. Session終了後、Model Close Callbackを正確に1回だけ呼ぶ。
6. FastAPI LifespanがShutdown Failureを無記録で抑制しない。外部へSecret／Path／Raw Exceptionを出さず、OperatorがFailureを認識できるようにする。
7. `force_cancel()`を残す場合、Thread-affine Streamへ安全に呼べないMethodとして汎用Lifecycleから到達不可能にする。
8. Backend保証のThread-safe Stop Signalを新設する場合は、無断にContractを拡張せず設計Reviewへ戻す。

## 4. Required Regression Test

Thread-affine Blocking Streamを用い、次をAssertする。

### 4.1 Timeout before Native Boundary

- ProducerがNative `next()`内でBlockingしている。
- 別Threadから短いTimeoutで`shutdown()`する。
- Shutdown ThreadからNative `cancel()`／`close()`が呼ばれない。
- Resultは成功ではない。
- Active Request解放を偽装しない。
- Model Close Callbackは呼ばれない。

### 4.2 Recovery after Native Boundary

- Native Boundary解放後、Producer Thread上でCancel／Closeされる。
- Session／Generation Gateが解放される。
- 再度のShutdownまたはRuntime Closeが成功する。
- Model Close Callbackは合計1回である。
- 未完了Producer Task／Threadが残らない。

### 4.3 Lifespan Failure Visibility

- Shutdown TimeoutまたはClose Failureを成功扱いしない。
- FailureをOperatorが認識できる。
- Client向けResponseへRaw Exception、Absolute Path、Secretを出さない。

## 5. Required Verification

```bash
./.venv/bin/ruff format --check src scripts tests
./.venv/bin/ruff check src scripts tests
./.venv/bin/mypy .
./.venv/bin/python -m compileall -q src scripts tests
./.venv/bin/pytest -q
./.venv/bin/pytest -q tests/unit/conversation tests/unit/web tests/integration/web
./.venv/bin/pytest -q -m model_smoke
uv lock --check --offline
bash -n scripts/setup/*.sh
```

Native Model Smokeは実装報告で2 passedだったが、設計者Review環境では`Failed to create llama_context`により2回失敗した。Follow-up完了時に再実行し、Host Resource条件と結果をStatusへ記録する。

Mac Manual Browserで、Stop、Post-cancel Generation、New Chat、Active Generation中のServer Shutdown／Restartを確認する。

## 6. Implementer Status Requirement

完了後、次を新規作成する。

```text
docs/handoffs/implementer_status_phase_1g_shutdown_cancel_follow_up_YYYYMMDDHHMMSS.md
```

Statusへ次を記録する。

- Shutdown Cancelの修正方式とThread Boundary
- Timeout時のState
- Model Close Callbackの回数
- Lifespan Failure Visibility
- Regressionの再現条件と結果
- 全Verification CommandのExit Code／件数
- Native Model SmokeのHost Resource条件と結果
- Manual Shutdown／Restart結果
- Phase 1-H未着手の明記

## 7. Out of Scope

- 解消済みSSE Disconnect／Queue Backpressure／Token Warning／Public Namingの再変更
- Backend全体のThread-safe Stop Contract新設
- Phase 1-H Summary Mode
- Lightning Full Upload／Model Transfer
- React／本格UI／Conversation永続化
- Runtime Governance／Guardrail／Judge／Repair／Agent／RAG
- Phase 1完了宣言／Backup
- Phase 1-ex／Git／GitHub公開

## 8. Start Condition

本Handoffは準備済みだが、実装開始指示ではない。

ユーザーが実装担当TaskへPhase 1-G Shutdown Cancel Follow-up開始を明示した時点で、Section 2の限定範囲を変更できる。

## 9. Append-Only

既存文書を変更せず、新TimestampのHandoffとして追加した。

<!-- SOURCE_END 72: docs/handoffs/implementer_handoff_phase_1g_shutdown_cancel_follow_up_20260721164248.md -->

---

<!-- SOURCE_BEGIN 73: docs/handoffs/implementer_handoff_phase_1h_review_follow_up_20260721182416.md -->

### Source 73: `docs/handoffs/implementer_handoff_phase_1h_review_follow_up_20260721182416.md`

- History Target: `docs/project/phases/phase_1/history/handoffs/implementer_handoff_phase_1h_review_follow_up_20260721182416.md`
- Source SHA-512: `82c1428bda9f1c4102736583987f4d3ce9becd9ad66be4be59ac741bc05fb8bc7c0ba7450bebe01e4959987c7ba3cd7762a4afbc06681de959f71f465e50712a`
- Source Size: `12350` bytes

# 実装担当向け Phase 1-H Review Follow-up Handoff

- 文書ID: `implementer_handoff_phase_1h_review_follow_up`
- 状態: `waiting_user_implementation_authorization`
- 作成日時: `2026-07-21 18:24:16 JST`
- 更新日時: `2026-07-21 18:24:16 JST`
- Snapshot: `20260721182416`
- 作成担当: 設計者役担当Task
- 対象担当: 実装担当Task
- 正本言語: 日本語
- Review: [designer_review_phase_1h_summary_mode_and_ui_language_20260721182038.md](../history/handoffs/designer_review_phase_1h_summary_mode_and_ui_language_20260721182038.md)
- 実装報告: [implementer_status_phase_1h_summary_mode_and_ui_language_20260721181202.md](../history/handoffs/implementer_status_phase_1h_summary_mode_and_ui_language_20260721181202.md)
- Requirements: [phase_1h_summary_mode_and_ui_language_requirements_20260721174346.md](../history/requirements/phase_1h_summary_mode_and_ui_language_requirements_20260721174346.md)
- Architecture: [phase_1h_summary_mode_and_ui_language_architecture_20260721174346.md](../history/architecture/phase_1h_summary_mode_and_ui_language_architecture_20260721174346.md)
- ADR: [adr_0020_phase_1h_summary_pipeline_and_ui_language_separation_20260721174346.md](../history/adr/adr_0020_phase_1h_summary_pipeline_and_ui_language_separation_20260721174346.md)
- 前回Handoff: [implementer_handoff_phase_1h_summary_mode_and_ui_language_20260721174346.md](../history/handoffs/implementer_handoff_phase_1h_summary_mode_and_ui_language_20260721174346.md)
- Latest Index: [documentation_index_20260721182416.md](../history/documentation_index_20260721182416.md)
- supersedes: `implementer_handoff_phase_1h_summary_mode_and_ui_language_20260721174346.md`

## 1. Current State

Phase 1-Hの中核機能、Static／Unit／Integration、Mac Metal実Modelは成立している。ただし設計Reviewで4件のMandatory Findingが確認されたため、Phase 1-Hは`changes_requested`である。

```text
Core Summary Pipeline        : Pass
Config／Cancel／Fallback      : Pass
UI Language Main Path        : Pass
Successful Summary SSE       : Original全文を含むためFail
Long Silent SSE              : Keepaliveなし
Summary UI Risk Notice       : 不足
Runtime Error Relocalization : 不足
```

本Follow-upは4件だけを修正する。Phase 1-H全体を再設計しない。

## 2. Start Condition

ユーザーが実装担当Taskへ本Follow-up開始を明示した時点で、Section 3の限定範囲を変更できる。それ以前はSource／Config／Testを変更しない。

## 3. Authorized Scope after User Approval

```text
src/margpa_runtime_llm/modules/conversation/application/conversation_generation.py
src/margpa_runtime_llm/web/streaming.py
src/margpa_runtime_llm/web/static/app.js
src/margpa_runtime_llm/web/static/index.html
tests/unit/conversation/test_conversation_generation.py
tests/integration/web/test_web_app.py
必要な既存Web／Conversation Test Fixture
docs/handoffs/implementer_status_phase_1h_review_follow_up_*
```

`app.css`の変更は、文言追加による最小Layout調整が必要な場合だけ許可する。

Config Schema、Summary Prompt、Model Adapter、CLI、Dependency、`pyproject.toml`、`uv.lock`は変更しない。

## 4. Work Package 1：Successful Summary SSEのData Minimization

### 4.1 Required Public Contract

Summary成功時、Public SSEへ返す回答本文はPresented Answerだけとする。

```json
{
  "request_id": "turn-id",
  "finish_reason": "stop",
  "assistant_message": {
    "role": "assistant",
    "content": "Short summary"
  },
  "usage": {},
  "transformation": {
    "summary_mode": "post_generation",
    "summary_applied": true,
    "fallback_used": false,
    "original_finish_reason": "stop",
    "summary_finish_reason": "stop"
  }
}
```

禁止：

```text
original_assistant_message
summary_assistant_message
Original全文を含む任意の別Field
Summary本文の重複Field
```

Originalは`ConversationGenerationSession`内のServer-side Artifactとして保持する。Phase 1-HではClientへ返さず、永続保存もしない。将来Audit Logは別責務で接続する。

### 4.2 Fallback Contract

Fallback時はOriginalがPresented Answerになるため、次を許可する。

```json
{
  "assistant_message": {
    "role": "assistant",
    "content": "Original answer"
  },
  "transformation": {
    "summary_mode": "post_generation",
    "summary_applied": false,
    "fallback_used": true,
    "original_finish_reason": "stop",
    "summary_finish_reason": null
  }
}
```

FallbackでもOriginalを別Fieldへ重複させない。

### 4.3 Usage Metadata

Current Presented `usage`は維持する。Original／Summaryの段階別Usageを残す場合、回答本文を含まない`stage_usage`等のMetadataへ整理してよい。

既存Clientが未知Fieldを無視できることを維持する。

### 4.4 Required Test

Success SSE Testへ最低限次を追加する。

```text
Original Canonical FinalはResponse全体に存在しない
Summaryはassistant_messageとして存在する
Summary Thinkingは存在しない
Original Thinkingは存在しない
original_assistant_message Keyは存在しない
summary_assistant_message Keyは存在しない
summary_applied=true
fallback_used=false
```

Fallback Testでは、Originalが`assistant_message`として1回だけ存在し、`fallback_used=true`であることを確認する。

## 5. Work Package 2：SSE Keepalive

### 5.1 Interval

Phase 1-H Follow-upの固定値：

```text
SSE Keepalive Interval : 15.0 seconds
Wire Format            : : keepalive\n\n
Semantic Event         : No
Conversation History   : No
Audit Event            : No
```

KeepaliveはSSE Commentであり、`event:`／`data:`を付けない。BrowserのCurrent ParserはData LineのないBlockを無視できる。

### 5.2 Required Behavior

- Application Eventが15秒間来ない場合だけKeepalive Commentを送る。
- Eventが送信された場合はIdle TimerをResetする。
- Normal Hidden GenerationとSummary Buffered Generationの両方で動作する。
- Consumer Disconnect後に送らない。
- Terminal後に送らない。
- Heartbeat専用Background Taskを残さない。
- Generation QueueへConversation Eventとして積まない。
- Queue Capacity、Backpressure、Terminal Countを変えない。
- `Cache-Control: no-store`、`X-Accel-Buffering: no`を維持する。
- Raw Exception、Request ID、Prompt等をCommentへ含めない。

実装は`stream_session_as_sse()`のAsync Consumer側で行う。Native Model／Producer ThreadへTimer処理を入れない。

### 5.3 Required Test

Testでは実時間15秒を待たない。IntervalをMonkeypatch可能なModule Constant等として定義し、短いTest値を使う。

確認項目：

- Blocking／Silent Producer中にKeepaliveが1回以上出る。
- Keepaliveは`ConversationEvent`としてCountされない。
- Keepalive後に通常Eventを受信できる。
- Completed後にKeepaliveが出ない。
- DisconnectでProducerへCooperative Cancelが伝わる。
- Cleanup後にTask／Threadが残らない。
- Existing Cross-thread Cancel Testが継続合格する。

## 6. Work Package 3：Summary Risk Notice

日本語Default文言：

```text
ONでは通常回答の完了後に同じModelで要約します。
処理時間とToken使用量が増え、要約により詳細、前提、注意事項等が省略・変形される可能性があります。
```

English Default文言：

```text
When ON, the completed answer is summarized by the same model.
This increases latency and token usage, and details, assumptions, or cautions may be omitted or altered by the summary.
```

- Translation DictionaryとInitial HTMLを一致させる。
- Model品質保証、正確性保証を主張しない。
- 既存Layoutを崩さない。
- Static Testで日英双方のRisk表現を確認する。

## 7. Work Package 4：Runtime Status Relocalization

Render済みRuntime Error Textを恒久Stateとして保持しない。

候補State：

```text
runtimeStatus.kind = loading | metadata | known_error
runtimeStatus.translationKey = runtimeLoading | runtimeLoadFailed
runtimeStatus.text = Model／Profile／Device等のOpaque Metadata成功時だけ
```

`renderRuntimeStatus()`等の単一責務を追加し、`applyTranslations()`から必ず呼ぶ。

期待動作：

```text
Loading中 ja → en : Checking runtime…へ更新
Failure後 ja → en : Could not load runtime information.へ更新
Failure後 en → ja : Runtime情報を取得できませんでした。へ更新
Success後 ja ↔ en : Model／Profile／Device Identifierは不変
```

未知のServer自由TextをClient側で機械翻訳しない既存方針は維持する。

新Dependencyを追加せず、可能な範囲でAutomated Testを追加する。Browser DOM Harnessを新規Dependencyなしで安全に作れない場合、Source-level Contract TestとManual Browser Evidenceを組み合わせ、Statusへ制約を明記する。

## 8. Optional Non-blocking Improvement

Summary StageのBroad `except Exception`でFallbackする場合、固定された安全なOperator Logまたは内部Reason Codeを残してよい。

条件：

- ClientへRaw Exception、Prompt、Pathを返さない。
- Original Fallbackを壊さない。
- LogへConversation本文を出さない。
- 本改善のためにScopeを広げない。

実施しなくても4 Mandatory Findingが解消されればFollow-up受入対象となる。

## 9. Required Verification

```bash
./.venv/bin/ruff format --check src scripts tests
./.venv/bin/ruff check src scripts tests
./.venv/bin/mypy .
./.venv/bin/python -m compileall -q src scripts tests
node --check src/margpa_runtime_llm/web/static/app.js
./.venv/bin/pytest -q
./.venv/bin/pytest -q tests/unit/conversation tests/unit/summarization tests/integration/web
./.venv/bin/pytest -q -m model_smoke
uv lock --check --offline
bash -n scripts/setup/*.sh
```

Manual Mac Browser：

- Summary ON成功で要約だけが表示される。
- Browser DevTools／SSE ResponseにOriginal全文が存在しない。
- Summary FallbackではOriginalが表示される。
- Summary Noteが日英でRiskを説明する。
- Runtime API Failure後にUI `ja → en → ja`が切り替わる。
- UI LanguageとResponse Languageは独立する。
- Stop／New Chat／Reloadが後退しない。

## 10. Implementer Status Requirement

完了後、次を新規作成する。

```text
docs/handoffs/implementer_status_phase_1h_review_follow_up_YYYYMMDDHHMMSS.md
```

Statusへ次を必ず記録する。

- 4 Findingごとの変更内容
- Final SSE Success／Fallback Payload Schema
- Original非送信のTest Evidence
- Keepalive Interval／Wire Format／Lifecycle
- Keepalive Regression Test
- Summary Risk Noticeの日英文言
- Runtime Status State／Relocalization Evidence
- 変更File一覧
- 全Verification Command、Exit Code、件数
- Mac Metal Smoke結果
- Manual Browser／DevTools確認結果
- Optional Improvement実施有無
- Lightning Upload未実施
- Phase 1完了／Backup／Phase 1-ex／Git未着手

## 11. Out of Scope

- Summary Prompt／Summary Model／Token値の再設計
- Dedicated Summary Model
- Config Schema追加変更
- Model Adapter／Backend Contract変更
- CLI変更
- New Dependency
- UI Framework移行
- Conversation永続化
- Audit Log本体
- Guardrail／Judge／Governance／Repair／RAG／Agent
- Lightning Upload／Model Transfer／Cloud実行
- Phase 1完了宣言／Backup
- Phase 1-ex／Git／GitHub公開

## 12. Stop／Return Conditions

次の場合、独自に範囲を広げず設計者役へ戻す。

- OriginalをClientへ返さないと現行UIが成立しない。
- KeepaliveのためNative Model Threadを変更する必要がある。
- SSE Protocol／FastAPI Dependency変更が必要になる。
- New Libraryが必要になる。
- Existing Cancel／Shutdown Contractが後退する。
- Public Access／Credential境界の変更が必要になる。
- Summary Prompt／Config Schemaの変更が必要になる。

## 13. Authorization Boundary

本Handoffは実装範囲を定義するが、実装開始指示ではない。ユーザーが実装担当TaskへFollow-up開始を明示した後に限り、Section 3の変更を行える。

## 14. Append-Only

前回Handoff、実装報告、Reviewを変更せず、新TimestampのFollow-up Handoffとして追加した。

<!-- SOURCE_END 73: docs/handoffs/implementer_handoff_phase_1h_review_follow_up_20260721182416.md -->

---

<!-- SOURCE_BEGIN 74: docs/handoffs/implementer_handoff_phase_1h_summary_mode_and_ui_language_20260721174346.md -->

### Source 74: `docs/handoffs/implementer_handoff_phase_1h_summary_mode_and_ui_language_20260721174346.md`

- History Target: `docs/project/phases/phase_1/history/handoffs/implementer_handoff_phase_1h_summary_mode_and_ui_language_20260721174346.md`
- Source SHA-512: `a084335a5a17c9fbf92282af96fe40c994fb162dc21a191ef599c436579a679d88ffea13342254f4dfd0e0256416255e57c0fb805f93aab4c4487c7da220092e`
- Source Size: `11027` bytes

# 実装担当向け Phase 1-H Summary Mode／UI Language Handoff

- 文書ID: `implementer_handoff_phase_1h_summary_mode_and_ui_language`
- 状態: `waiting_user_implementation_authorization`
- 作成日時: `2026-07-21 17:43:46 JST`
- 更新日時: `2026-07-21 17:43:46 JST`
- Snapshot: `20260721174346`
- 作成担当: 設計者役担当Task
- 対象担当: 実装担当Task
- 正本言語: 日本語
- Requirements: [phase_1h_summary_mode_and_ui_language_requirements_20260721174346.md](../history/requirements/phase_1h_summary_mode_and_ui_language_requirements_20260721174346.md)
- Architecture: [phase_1h_summary_mode_and_ui_language_architecture_20260721174346.md](../history/architecture/phase_1h_summary_mode_and_ui_language_architecture_20260721174346.md)
- ADR: [adr_0020_phase_1h_summary_pipeline_and_ui_language_separation_20260721174346.md](../history/adr/adr_0020_phase_1h_summary_pipeline_and_ui_language_separation_20260721174346.md)
- Roadmap: [implementation_roadmap_20260721174346.md](../history/architecture/implementation_roadmap_20260721174346.md)
- Latest Phase 1-G Review: [designer_review_phase_1g_shutdown_cancel_follow_up_20260721172916.md](../history/handoffs/designer_review_phase_1g_shutdown_cancel_follow_up_20260721172916.md)
- supersedes: なし（Phase 1-H実装開始用Handoffの初回）

## 1. Current State

Phase 1-GはAcceptedである。Minimal Web Surface、SSE、Browser-owned History、Stop／Disconnect／ShutdownのCooperative Cancel、Preview Basic Authが成立している。

Phase 1-Hの設計は完了したが、実装は未許可である。

```text
Phase 1-G : Accepted
Phase 1-H : Design Complete／Waiting User Authorization
Lightning Full Upload : Deferred until Phase 1-H Mac Acceptance
```

## 2. Start Condition

ユーザーが実装担当TaskへPhase 1-H開始を明示した時点で、本Handoffの限定範囲を実装できる。それ以前はSource／Config／Testを変更しない。

## 3. Authorized Scope after User Approval

```text
config/application.toml
src/margpa_runtime_llm/bootstrap/config_loader.py
src/margpa_runtime_llm/bootstrap/web_application.py
src/margpa_runtime_llm/modules/conversation/
src/margpa_runtime_llm/modules/summarization/       # 必要な場合
src/margpa_runtime_llm/orchestration/
src/margpa_runtime_llm/web/contracts.py
src/margpa_runtime_llm/web/static/index.html
src/margpa_runtime_llm/web/static/app.css
src/margpa_runtime_llm/web/static/app.js
tests/unit/conversation/
tests/unit/summarization/                            # 必要な場合
tests/unit/inference/test_config_and_registry.py
tests/integration/web/test_web_app.py
必要な既存Test Fixture
docs/handoffs/implementer_status_phase_1h_summary_mode_and_ui_language_*
```

`pyproject.toml／uv.lock`は新Dependency不要のため原則変更しない。不可避なDependency追加が必要なら、変更前に設計者役へ理由を戻す。

## 4. Work Package 1: Configuration／Contracts

1. Application Config Schemaを`2`から`3`へ更新する。
2. `[layers.summarization]`をTyped Configとして追加する。
3. `mode=off|post_generation`、`backend=main_model`、`max_new_tokens=1024`、`thinking_mode=disabled`、`preserve_original=true`、`failure_policy=fallback_original`を厳格Validationする。
4. Deployment Profile Schemaは変更しない。
5. `ConversationSettings`へ`summary_mode`を追加する。
6. `/api/v1/runtime`へDefault Summary Modeを追加する。
7. CLI Contractを変更しない。
8. Typo／未知値を黙って受理しない。

## 5. Work Package 2: Summarization Layer

1. SummarizationをConversation／Webから分離したTyped Application責務として実装する。
2. BrowserやFastAPI HandlerからInferenceを直接2回呼ばない。
3. NormalとSummaryを同じConversation Sessionが逐次所有する。
4. Normal StreamをCloseしてからSummary StreamをOpenする。
5. Model Loadは1回、同時Native Streamは最大1とする。
6. Summary RequestへOriginal Canonical Final Answerだけを渡す。
7. Normal Thinking、History、System Prompt、Runtime内部情報を渡さない。
8. Sourceを命令ではなくDataとして扱うSummary InstructionをServer側で構成する。
9. Response Language `ja／en／auto`を要約へ反映する。
10. Summary max 1024、Thinking disabledを強制する。
11. その他のGeneration ParametersはEffective Defaultを継承する。
12. Summary Raw OutputにもThinking Parserを適用し、ReasoningをClientへ漏らさない。

## 6. Work Package 3: Result／Fallback

Original、Summary、Presented Answerを別変数／Contractとして扱う。

次はWarning付きOriginal Fallback：

- Summary Inference Error
- Context Limit
- Empty／Whitespace Final
- Parser Failure
- Finish Reason Length
- Terminal不整合

Fallback時はOriginalを`completed.assistant_message`へ入れ、Browser HistoryもOriginalとする。

Summary中CancelはFallbackしない。`cancelled`で終了し、HistoryへAssistant Messageを追加しない。

OriginalのToken Limit WarningをSummary成功／Fallbackの両方で維持する。

## 7. Work Package 4: SSE／Cancellation

1. `status` Eventを追加し、`generating_answer／summarizing_answer`を送る。
2. Terminalは`completed／cancelled／error`の1回だけとする。
3. OFF時は既存Phase 1-G Event順序と表示を維持する。
4. ON時はNormal Delta／ThinkingをBrowserへ送らない。
5. Summaryは成功確定前に不完全Textを混在させない。推奨はBuffer後に表示する。
6. Normal／SummaryでCancel Flagを共有する。
7. Stage間でCancelを再確認し、Cancel後にSummaryを開始しない。
8. Stop API、Disconnect、Backpressure Cleanup、Shutdownを既存Cooperative Cancelへ合流させる。
9. 別ThreadからNative `cancel／close`を呼ばない。
10. Gate Release、Active Request、Model Close CallbackをPhase 1-Gから後退させない。

## 8. Work Package 5: Minimal UI

### 8.1 Summary Mode

- Settingsへ横スライド型`要約モード OFF／ON`を追加する。
- DefaultはRuntime Config由来のOFFとする。
- Requestでは`off／post_generation`へMappingする。
- ON時に追加生成、遅延、情報欠落の可能性がある旨を短く注記する。
- StatusをNormal生成／Summary生成で区別する。

### 8.2 UI Language

- Topbar右上へ`日本語 | English` Switchを追加する。
- New Chat Buttonと衝突しないResponsive Layoutにする。
- UI LanguageはResponse Language Pull-downと別Stateとする。
- Repository内のTranslation DictionaryとStable Keyを使用する。
- Title、`html lang`、Button、Label、Placeholder、Status、Known Warning／Error、ARIAを切り替える。
- Response Language OptionはLabelだけ翻訳し、Valueを維持する。
- Model Output／Thinkingを翻訳しない。
- `margpa.ui_language.v1`等へUI LanguageだけをBest-effort保存する。
- Invalid Value／Storage不可は日本語へ安全にFallbackする。
- New ChatでUI Languageを消さない。
- Chat、Prompt、Credential、OutputをLocal Storageへ保存しない。

## 9. Required Automated Tests

### 9.1 Config／Contract

- Schema 3のValid／Invalid Matrix
- Unknown Summary Mode／Backend／Policy Reject
- Deployment Profileへの混入Rejectまたは非採用
- UI Request `summary_mode` Validation
- Runtime Default Response

### 9.2 Summary Pipeline

- OFFはInference Call 1回
- ONはInference Call 2回、順序Normal→Summary
- Native Stream同時Open数1
- Summary Request Content Boundary
- Thinking disabled／max 1024
- ja／en／auto Policy
- Original／Summary／Presented分離
- Error／Empty／Context／Length Fallback
- Original Token Warning維持
- Summary Success Canonical History
- Fallback Original Canonical History

### 9.3 Cancellation／Lifecycle

- Normal中Cancel
- Stage間Cancel
- Summary中Cancel
- Disconnect／Backpressure両Stage
- Cancel後の後続Generation
- Busy状態が両Stageで継続
- Shutdown Timeout／Native Boundary Recovery
- Model Close Callback Exactly Once
- Producer Thread上のNative Cancel／Close

### 9.4 UI Language

- ja／enのStatic／Dynamic Text
- UI LanguageとResponse Languageの独立性
- Runtime中Statusの即時再描画
- New Chat後維持
- Reload相当のStorage復元
- Invalid／Unavailable Storage Fallback
- Model Content非翻訳
- Safe Text描画／`innerHTML`不使用
- Known／Unknown Error表示

## 10. Required Verification

```bash
./.venv/bin/ruff format --check src scripts tests
./.venv/bin/ruff check src scripts tests
./.venv/bin/mypy .
./.venv/bin/python -m compileall -q src scripts tests
./.venv/bin/pytest -q
./.venv/bin/pytest -q tests/unit/conversation tests/unit/summarization tests/integration/web
./.venv/bin/pytest -q -m model_smoke
uv lock --check --offline
bash -n scripts/setup/*.sh
```

`tests/unit/summarization`を作らない場合は、同等Testの配置先をStatusへ記録する。

Manual Mac Gate：

- Summary OFF／ON
- Summary Status遷移
- UI日本語／English
- UIとResponse Languageの交差組合せ
- Normal中Stop／Summary中Stop
- Fallbackの安全表示
- New Chat後のUI Language維持
- Server Shutdown／Restart

## 11. Implementer Status Requirement

完了後、次を新規作成する。

```text
docs/handoffs/implementer_status_phase_1h_summary_mode_and_ui_language_YYYYMMDDHHMMSS.md
```

Statusへ次を必ず記録する。

- 変更File一覧
- Final Directory／Contract
- Config Schema Migration
- Summary Prompt Boundary
- Model Call回数／逐次性Evidence
- Fallback Matrix
- SSE Event順序
- Cancel／Shutdown Thread Boundary
- UI Translation Key／Storage Boundary
- 全Verification Command、Exit Code、件数
- Native Model Smoke／Manual UI結果
- 未解決事項／非ブロッカー
- Lightning Full Upload未実施の明記
- Phase 1完了／Backup／Phase 1-ex未着手の明記

## 12. Out of Scope

- Dedicated Summary Model／Model Download
- Guard Model／Judge Model
- Governance／Repair／RAG／Agent
- Summary Quality Judge
- Pre-generation／History Summary
- Original Answer表示UI
- Conversation Persistence／Delete
- React／Next.js／Node
- Machine Translation API
- 本格Account／OAuth／TLS終端
- Lightning Full Upload／Dependency Install／Model Transfer
- Phase 1完了宣言／Backup
- Phase 1-ex／Git／GitHub公開

## 13. Stop／Return Conditions

次の場合、独自判断で範囲を広げず設計者役へ戻す。

- Backend Contract変更が必要
- Dedicated Modelが必要
- Contextを収めるためOriginal切捨てが必要
- Summary PromptへHistory／System Promptを渡す必要が生じた
- Thread-safe Native Stop Contractの新設が必要
- 新Dependency追加が必要
- Existing CLI Contract変更が必要
- Summary FailureでOriginalを復元できない
- Public Access／Credential境界変更が必要

## 14. Append-Only

本書はPhase 1-H初回実装Handoffとして新規追加した。実装報告、Review、Follow-upは別Timestampの新文書とする。

<!-- SOURCE_END 74: docs/handoffs/implementer_handoff_phase_1h_summary_mode_and_ui_language_20260721174346.md -->

---

<!-- SOURCE_BEGIN 75: docs/handoffs/implementer_status_phase_1_environment_and_metal_smoke_20260718210342.md -->

### Source 75: `docs/handoffs/implementer_status_phase_1_environment_and_metal_smoke_20260718210342.md`

- History Target: `docs/project/phases/phase_1/history/handoffs/implementer_status_phase_1_environment_and_metal_smoke_20260718210342.md`
- Source SHA-512: `afaa9745b7860325dcf69f79182f4437275029af13caad48979cef432055a4271d8984a298c5c5c66ab37d199ca4179ea455971326154e965d126f0061fde965`
- Source Size: `6584` bytes

# Phase 1 Environment Setup／Qwen3-4B Metal Smoke Test 実装状況

- 文書ID: `implementer_status_phase_1_environment_and_metal_smoke`
- 状態: `completed_for_authorized_scope`
- 作成日時: `2026-07-18 21:03:42 JST`
- 更新日時: `2026-07-18 21:03:42 JST`
- 作成担当: 実装者役担当Task
- 対象: Phase 1 Environment SetupおよびQwen3-4B／Metal Smoke Test
- 正本言語: 日本語
- supersedes: なし（新規Status系列）
- Documentation Index: [documentation_index_20260718201744.md](../history/documentation_index_20260718201744.md)
- 実装者Handoff: [implementer_handoff_20260718193435.md](../history/handoffs/implementer_handoff_20260718193435.md)
- Environment Handoff: [designer_python_environment_handoff_20260718201744.md](../history/handoffs/designer_python_environment_handoff_20260718201744.md)

## 1. 実施Scope

ユーザーから次の範囲だけ実装解禁を受けた。

- Phase 1 Environment Setup
- `llama-cpp-python`のMetal Source Build
- Qwen3-4B GGUFのLoad／最小Generation
- Streaming／Stopの技術検証
- Load／UnloadとMemory／速度の観測
- Test／Ruff／mypy／Jupyter／Lock再現性の確認

Phase 2以降、Model Port、Model Registry、Production CLI、Conversation、Governance、Audit、Guard、RAG、Agentの本実装には進んでいない。

## 2. Environment結果

```text
Python          : CPython 3.13.14
Architecture    : ARM64
GIL             : Enabled
Package Manager : uv 0.11.29
Virtual Env     : margpa-runtime-llm/.venv/
Venv形態        : Project直下の実Directory
Lock File       : uv.lock
```

External VenvおよびPython 3.12／3.11 Fallbackは不要だった。

`.venv/`容量は検証時点で約361MB。

`uv.lock`は1,620行、160,611Byte。

```text
uv.lock SHA-256:
e5efe33d69105547fe0d4f348b6b189b85f7ed55323f8ecd993ef5df7846fee1
```

## 3. Direct Dependency

```text
llama-cpp-python==0.3.34
pydantic==2.13.4
pydantic-settings==2.14.2
psutil==7.2.2

pytest==9.1.1
pytest-asyncio==1.4.0
pytest-cov==7.1.0
ruff==0.15.22
mypy==2.3.0

jupyterlab==4.6.1
notebook==7.6.0
ipykernel==7.3.0
```

次の後続Phase Packageが未導入であることを確認した。

```text
torch
transformers
langchain
langgraph
mlx
mlx-lm
```

## 4. Metal Build結果

`llama-cpp-python==0.3.34`をSource Distributionから次の条件でBuildした。

```text
CMAKE_ARGS=-DGGML_METAL=on
Python=3.13.14
Architecture=arm64
```

確認結果：

```text
llama_supports_gpu_offload() : true
Metal Library                : libggml-metal.dylibあり
Embedded Metal Library       : 有効
GPU                           : Apple M2 Pro
Unified Memory               : true
```

Verbose Loadでは37／37 LayerのGPU Offloadを確認した。

## 5. Qwen3-4B Smoke Test結果

対象Artifact：

```text
models/main/qwen3-4b/gguf/Qwen3-4B-Q4_K_M.gguf
Size: 2,497,280,256Byte
GGUF: V3
Architecture Metadata: qwen3
Quantization Metadata: Q4_K - Medium
Chat Template Metadata: あり
```

Smoke専用設定：

```text
n_gpu_layers : -1
n_ctx        : 1024
n_batch      : 256
n_threads    : 6
max_tokens   : 48
seed         : 2371
```

これはSmoke Test専用値であり、Production Defaultの確定ではない。

結果：

```text
Result                         : success
Metal Cold Library Init        : 約10.346秒
Model Load                     : 約0.356秒（Metal初期化後）
Generation                     : 約0.644秒
Completion Token               : 13
Observed Token Speed           : 約20.18 token/s
Streaming開始                  : 成功
Consumer-side Streaming Stop   : 成功
Stop後の再Generation           : 成功
Stop Sequence                  : finish_reason=stop
Explicit Model Close／Unload   : 成功
```

生成例：

```text
<think>

</think>

メタルスモークテスト成功。
```

`/no_think`をInputへ含めても空の`<think>`Tagが残った。Thinking ModeとChat Templateの正式な扱いは未決事項として維持し、Smoke実装ではProduction Policyを確定していない。

Model Metadataの`general.name`は`Qwen3 4B Instruct Awq`だった。Model IDやDistributionをこの値またはFile名から推測せず、将来のModel Registryで明示管理する。

## 6. Memory観測

同一ProcessのRSS観測値：

```text
Load前       : 91,979,776Byte
Load後       : 2,797,453,312Byte
Peak         : 2,809,118,720Byte
Explicit Unload後: 151,912,448Byte
```

この値は短いSmoke Test時のProcess RSSであり、macOS Unified Memory全体やProduction Context条件の確定値ではない。

## 7. Verification結果

```text
uv sync --frozen --offline : 成功
uv lock --check            : 成功
Ruff Check                 : 成功
Ruff Format Check          : 成功
mypy --strict              : 成功
pytest                     : 2 passed
compileall                 : 成功
Jupyter Kernel Import      : 成功
```

JupyterはProject `.venv`のPython 3.13.14／ARM64 Kernelから`margpa_runtime_llm`をImportできた。

## 8. Sandbox由来の再実行

最初のMetal Context作成はTask Sandbox内でMetal Command Queue作成を拒否され、`Failed to create llama_context`となった。

ユーザー承認を経てSandbox外で同じSmoke Testを再実行し、Apple M2 Pro／MetalによるGenerationまで成功した。この失敗はProject Path、Python 3.13、Native Build、Model Artifactの失敗ではなく、実行SandboxのGPU制約による。

Jupyter Kernel検証もSandbox内ではLocal Loopback Socket作成を拒否されたため、承認後にSandbox外で再実行して成功した。

## 9. 作成・変更した範囲

Project Root：

- `.python-version`
- `.gitignore`
- `pyproject.toml`
- `uv.lock`
- `.venv/`（Git管理外）

Source：

- Phase 1既存Directoryの`__init__.py`
- `adapters/model_backends/llama_cpp/metal_smoke.py`

Scripts：

- `scripts/models/qwen3_metal_smoke.py`
- `scripts/setup/verify_phase1_environment.py`
- `scripts/setup/verify_jupyter_kernel.py`

Tests：

- `tests/unit/test_package_metadata.py`
- `tests/integration/test_llama_cpp_metal.py`

Python Package VersionはRelease Version未決のため`0.0.0`を暫定Placeholderとしている。

Git初期化、追加Model Download、既存Docs変更、Documentation Index変更は行っていない。

## 10. 次の判断待ち

- Qwen3 Thinking Modeの正式な扱い
- Chat Template適用方針
- Initial `n_ctx`／Generation Default
- Model Load／Unload Lifecycle
- Model Port／Result／Error Contract
- Model Registry／Config Schema
- Phase 1 Production実装の次Scope

後続Phaseへはユーザーの明示指示なしに進まない。

<!-- SOURCE_END 75: docs/handoffs/implementer_status_phase_1_environment_and_metal_smoke_20260718210342.md -->

---

<!-- SOURCE_BEGIN 76: docs/handoffs/implementer_status_phase_1_environment_reproducibility_follow_up_20260718214958.md -->

### Source 76: `docs/handoffs/implementer_status_phase_1_environment_reproducibility_follow_up_20260718214958.md`

- History Target: `docs/project/phases/phase_1/history/handoffs/implementer_status_phase_1_environment_reproducibility_follow_up_20260718214958.md`
- Source SHA-512: `fb8c4cb7b4343039bafdf6f40e0b5fd7e7d66090aa8ddddaa41f24687965bed380c2fdb1ddc3da4f0a26e47cc5887182089bdb98ce81df1aac601c86adfb0159`
- Source Size: `10790` bytes

# Phase 1 Environment再現性 Follow-up 実装状況

- 文書ID: `implementer_status_phase_1_environment_reproducibility_follow_up`
- 状態: `implementation_complete_review_requested`
- 作成日時: `2026-07-18 21:49:58 JST`
- 更新日時: `2026-07-18 21:49:58 JST`
- 作成担当: 実装者役担当Task
- 対象: 設計者役担当Task
- 正本言語: 日本語
- 最新Index: [documentation_index_20260718212502.md](../history/documentation_index_20260718212502.md)
- Review元: [designer_review_phase_1_environment_and_metal_smoke_20260718212502.md](../history/handoffs/designer_review_phase_1_environment_and_metal_smoke_20260718212502.md)
- Previous Status: [implementer_status_phase_1_environment_and_metal_smoke_20260718210342.md](../history/handoffs/implementer_status_phase_1_environment_and_metal_smoke_20260718210342.md)
- supersedes: `implementer_status_phase_1_environment_and_metal_smoke_20260718210342.md`

## 1. 結論

設計ReviewでRequired Follow-upとされた次の2点を実装し、Fresh／Clean相当条件で再現した。

```text
uv実行Fileの永続配置             : Pass
通常Login Shellからのuv解決      : Pass
Metal Source Build Recipe永続化  : Pass
新規Venv／使い捨てCache Build    : Pass
llama-cpp-python Source Build     : Pass
Metal／GPU Offload               : Pass
Qwen3-4B Load／Generation         : Pass
```

Recommended Follow-upであったOpt-in `model_smoke` Testと、Backend／Model／Generation／Unload計測分離も同時に実装した。

Phase 1-B、Phase 2、Governance、RAG、Agentには着手していない。

## 2. uv永続配置

### 2.1 採用方式

uv公式Standalone InstallerのVersion固定URLを使用した。

```text
Installer URL : https://astral.sh/uv/0.11.29/install.sh
uv実体Path    : <USER_HOME>/.local/bin/uv
uvx実体Path   : <USER_HOME>/.local/bin/uvx
Version       : uv 0.11.29
Architecture  : aarch64-apple-darwin
```

公式の`uv tool update-shell`により、次のUser Shell設定が作成された。

```text
File : <USER_HOME>/.zshenv
PATH : <USER_HOME>/.local/bin
```

### 2.2 通常Login Shell確認

新規Zsh Login Shellで次を確認した。

```text
command -v uv : <USER_HOME>/.local/bin/uv
uv --version  : uv 0.11.29 (aarch64-apple-darwin)
uv lock --check : Pass／117 packages
uv sync --frozen : Pass
uv sync --frozen --offline : Pass／115 packages checked
```

Codex Sandbox内ではUser Cacheの`~/.cache/uv`がPermission制約を受けたため、Login Shell AcceptanceはSandbox外で同一Commandを再実行してPassを確認した。

### 2.3 重複配置の整理

前回の技術検証でUser Python 3.11へ一時的にInstallしていた次のuvは、公式Standalone版の確認後にUninstallした。

```text
<USER_HOME>/Library/Python/3.11/bin/uv
```

現在、通常Shellから解決されるuvは公式Standalone版へ一本化されている。

自動Updateは実行していない。Versionを`0.11.29`から変更していない。

## 3. Metal Source Build Recipe

永続化先：

[setup_macos_arm64_metal.sh](../../../../../scripts/setup/setup_macos_arm64_metal.sh)

Recipeの責務：

- macOS／ARM64以外では非Zero Exit
- Xcode Command Line Tools／Apple clangを事前確認
- PATH上のuvが`0.11.29`であることを確認
- `uv.lock`を変更せず`uv lock --check`を実行
- uv Managed CPython `3.13.14`を指定
- `llama-cpp-python==0.3.34`をBinary WheelではなくSourceからBuild
- Build Processだけへ`CMAKE_ARGS=-DGGML_METAL=on`を設定
- `core + inference-llama + dev + notebook`を同期
- Package Version、GIL、ARM64、GPU Offload、MTLを検証
- `--smoke`指定時だけLocal GGUFをLoad
- Model Artifactを暗黙Downloadしない
- Cloud／CUDA ProfileへMetal Flagを伝播しない

通常構築：

```text
scripts/setup/setup_macos_arm64_metal.sh
```

Fresh Source Build＋Smoke：

```text
scripts/setup/setup_macos_arm64_metal.sh \
  --venv <new-temporary-directory>/venv \
  --clean-source-build \
  --smoke
```

`--clean-source-build`は、存在しないTarget Venvを要求し、uvの`--no-cache`を使用する。既存VenvやGlobal uv CacheのBuild済みArtifactを再利用しない。

`uv.lock`はDependency Source、Version、Hashを固定するが、`GGML_METAL=on`を固定しない。Native Build条件は本Recipeが正本となる。

## 4. Fresh／Clean相当Build結果

実行条件：

```text
Target Venv : /tmp/margpa-phase1-repro-XXXXXX/venv
uv Cache    : 使い捨て／--no-cache
Python      : CPython 3.13.14
Machine     : arm64
GIL         : enabled
Build       : llama-cpp-python 0.3.34 Source Build
CMake       : GGML_METAL=on
```

実行結果：

```text
Resolved             : 117 packages
Installed            : 115 packages
llama-cpp-python Build: success
Environment Verify   : success
Metal Smoke          : success
```

Fresh EnvironmentのNative LibraryはMach-O ARM64として確認した。

```text
libggml-metal.dylib SHA-256:
bdacb71e301b4add592a2eba3e174d4c97d2e0b6dbde48538b287f5cc9706193

libllama.dylib SHA-256:
fd63d22b58e1f28f8bb892a4e7caf5dcea77f0e7b2a01ff09c3257fd719ad318
```

Temporary Venvは検証完了後に削除した。Project Rootの`.venv/`は変更せず維持している。

## 5. Fresh Qwen3-4B／Metal Smoke結果

```text
Result                            : success
Python                            : 3.13.14
Machine                           : arm64
GIL                               : enabled
llama-cpp-python                  : 0.3.34
GPU                               : Apple M2 Pro
Metal Embedded Library            : enabled
Unified Memory                    : true
GPU Offload Support               : true
Qwen3 Metadata                    : qwen3
Chat Template Metadata            : present
Model Size                        : 2,497,280,256Byte
Backend Cold Init Field           : 約0.0578秒
Model Load after Backend Init     : 約1.5549秒
First Content Latency             : 約0.1441秒
Total Generation Latency          : 約0.3980秒
Observed Speed                    : 約32.66 token/s
Unload Latency                    : 約0.0411秒
Peak Process RSS                  : 約2.76GB
Explicit Unload後RSS              : 約136MB
Streaming Start／Close            : success
Post-close Generation             : success
Stop Sequence                     : finish_reason=stop
```

最初のEnvironment Verification ProcessではMetal Libraryの初期化Logが約`10.195秒`を記録した。その後に別Processで実行したSmokeの`backend_cold_init_seconds`はOS／Metal側のWarm条件を含む約`0.0578秒`だった。

このため、Field分離は完了したが、Performance比較ではProcessだけでなくOS／Metal Cache条件も併記する必要がある。

生成結果：

```text
<think>

</think>

メタルスモークテスト成功。
```

Empty Thinking Tagは既知の非Blockerとして維持し、Production Policyは確定していない。

## 6. Opt-in Model Smoke Test

追加先：

[test_qwen3_model_smoke.py](../../../../../tests/integration/test_qwen3_model_smoke.py)

通常の`pytest`では`model_smoke`を除外する。明示実行は次とする。

```text
pytest -m model_smoke
```

動作：

- macOS／ARM64以外ではSkip
- Local Model Artifactがなければ明確にSkip
- Modelを暗黙Downloadしない
- 明示指定時だけLoad／Generation／Streaming Close／Stop／Unloadを実行

Fresh Venvからの実行結果：

```text
1 passed, 2 deselected
```

## 7. 計測Field分離

[metal_smoke.py](../../../../../src/margpa_runtime_llm/adapters/model_backends/llama_cpp/metal_smoke.py)へ次を追加した。

```text
backend_cold_init_seconds
model_load_after_backend_init_seconds
first_content_latency_seconds
total_generation_seconds
unload_seconds
```

これはPhase 1 Probe用であり、Production Model Port／Result Contractではない。

## 8. Environment Verification強化

[verify_phase1_environment.py](../../../../../scripts/setup/verify_phase1_environment.py)を次の判定へ変更した。

- Direct Dependencyの存在だけでなくExact Versionを検証
- CPython 3.13.14／Darwin／ARM64／通常GILを検証
- `llama_supports_gpu_offload=true`を検証
- Backend System Infoに`MTL`があることを検証
- RAG／Agent／Transformers／MLX Packageが存在しないことを検証
- 実際のTarget Venv Pathを出力

## 9. 変更一覧

Project内：

```text
M pyproject.toml
A scripts/setup/setup_macos_arm64_metal.sh
M scripts/setup/verify_phase1_environment.py
M src/margpa_runtime_llm/adapters/model_backends/llama_cpp/metal_smoke.py
A tests/integration/test_qwen3_model_smoke.py
A docs/handoffs/implementer_status_phase_1_environment_reproducibility_follow_up_20260718214958.md
```

User Tool／Shell：

```text
A <USER_HOME>/.local/bin/uv
A <USER_HOME>/.local/bin/uvx
A <USER_HOME>/.zshenv
D <USER_HOME>/Library/Python/3.11/bin/uv
```

`uv.lock`は変更していない。

```text
uv.lock SHA-256:
e5efe33d69105547fe0d4f348b6b189b85f7ed55323f8ecd993ef5df7846fee1
```

`pyproject.toml`はDefault Pytestから`model_smoke`を除外する設定だけを変更した。

## 10. Verification結果

```text
bash -n Setup Recipe       : Pass
Ruff Format Check          : Pass／18 files
Ruff Check                 : Pass
mypy --strict              : Pass／18 source files
Default pytest             : 2 passed, 1 deselected
Opt-in model_smoke pytest  : 1 passed, 2 deselected
compileall                 : Pass
uv lock --check            : Pass
uv sync --frozen           : Pass
uv sync --frozen --offline : Pass
Fresh Source Build         : Pass
Fresh Qwen3 Metal Smoke    : Pass
```

## 11. Deviation／Fallback／残事項

```text
Python Fallback       : なし
Venv External化      : なし
uv Version変更       : なし
Dependency追加       : なし
uv.lock変更          : なし
Model Download       : なし
Phase 1-B着手        : なし
Phase 2以降着手      : なし
```

設計Reviewで求められた「別Taskからの独立確認」は、本Statusを設計者役担当Taskへ渡して実施する必要がある。本Taskでは、独立Taskを代替したとは扱わない。

今回確認したのは、通常Login ShellおよびFresh Venv／使い捨てCacheによる技術再現性である。

## 12. 設計者へのReview依頼

次を独立確認してほしい。

1. 新規Login Shellで`command -v uv`が`~/.local/bin/uv`を返すこと
2. `uv --version`が`0.11.29`であること
3. `uv lock --check`が成功すること
4. `uv sync --frozen --offline`が成功すること
5. Setup RecipeのPlatform GuardとMetal Flag ScopeがArchitecture／ADRに適合すること
6. Fresh Build証跡とOpt-in Model Smokeを受理できること
7. Required Follow-up 1／2を完了判定できること

Phase 1-Bの実装許可は、本Statusでは要求も仮定もしない。

<!-- SOURCE_END 76: docs/handoffs/implementer_status_phase_1_environment_reproducibility_follow_up_20260718214958.md -->

---

<!-- SOURCE_BEGIN 77: docs/handoffs/implementer_status_phase_1b_model_runtime_20260718232354.md -->

### Source 77: `docs/handoffs/implementer_status_phase_1b_model_runtime_20260718232354.md`

- History Target: `docs/project/phases/phase_1/history/handoffs/implementer_status_phase_1b_model_runtime_20260718232354.md`
- Source SHA-512: `bf2e0a6458b7380fba381264d5ce4242f085878e973c62735377eb5ede3b122a2f0909e5e0ebfcd5f8e75542e9ac366c16e0e37d71cea64904b5a205a657f485`
- Source Size: `20932` bytes

# Phase 1-B Model Runtime 実装状況

- 文書ID: `implementer_status_phase_1b_model_runtime`
- 状態: `implementation_complete_review_requested`
- 作成日時: `2026-07-18 23:23:54 JST`
- 更新日時: `2026-07-18 23:23:54 JST`
- 作成担当: 実装者役担当Task
- 対象: 設計者役担当Task
- 正本言語: 日本語
- Documentation Index: [documentation_index_20260718224308.md](../history/documentation_index_20260718224308.md)
- Implementer Handoff: [designer_handoff_phase_1b_model_runtime_20260718224308.md](../history/handoffs/designer_handoff_phase_1b_model_runtime_20260718224308.md)
- 詳細設計: [phase_1b_model_runtime_contract_20260718223203.md](../history/architecture/phase_1b_model_runtime_contract_20260718223203.md)
- Accepted ADR: [adr_0006_model_runtime_port_and_configuration_20260718224308.md](../history/adr/adr_0006_model_runtime_port_and_configuration_20260718224308.md)
- Previous Phase Status: [implementer_status_phase_1_environment_reproducibility_follow_up_20260718214958.md](../history/handoffs/implementer_status_phase_1_environment_reproducibility_follow_up_20260718214958.md)
- supersedes: なし（新規Phase 1-B Status系列）

## 1. 結論

許可されたPhase 1-B Model Runtime Scopeを実装し、Default TestおよびQwen3-4B／Metal Opt-in Integration Testを完了した。

```text
Model-independent Contract        : Pass
Model Port Protocol               : Pass
llama.cpp Adapter isolation       : Pass
Registry／Config Validation       : Pass
Qwen3-4B Load／Unload             : Pass
Default Context 4,096             : Pass
Thinking Default OFF             : Pass
Thinking Explicit ON             : Pass
One-shot Generation              : Pass
Streaming                        : Pass
Cooperative Cancel               : Pass
Post-cancel Generation           : Pass
Finish Reason Mapping            : Pass
Token Usage／Timing              : Pass
Capability Validation            : Pass
Safe Error Contract              : Pass
Unit／Contract／Integration Test  : Pass
Ruff／mypy --strict              : Pass
Modelの暗黙Downloadなし          : Pass
Phase 2以降への越境なし          : Pass
```

Phase 1-Bの実装Acceptance Criteriaは実装担当側でPassと判定する。最終受入は設計者Reviewへ依頼する。

## 2. 実装Scope

実装した範囲：

- Inference Domain／Public Contract
- Model Port Protocol
- Inference Application Service
- llama.cpp Production Adapter
- Model Lifecycle／Capability／Error Mapping
- Embedded Chat Template／Thinking Control
- One-shot Generation／Streaming／Cooperative Cancel
- Model Registry／Deployment・Generation Profile
- Config優先順位とEffective Config
- Bootstrap／Dependency Injection
- Phase 1-B一問一答CLI
- Unit／Fake Port Contract／Opt-in実Model Integration Test
- Production Runtime Acceptance Probe

実装していない範囲：

- Multi-Turn／Conversation History
- FastAPI／Web UI
- Runtime Governance／Audit Log本実装
- Guard／Judge／RAG／Agent／Tool実行
- 複数Model同時常駐／Router
- Remote／MLX／Transformers／vLLM Adapter
- Phase 2以降

## 3. Contract一覧

Phase 1-BのModel非依存Contractとして次を実装した。

```text
MessageRole
ChatMessage
ThinkingMode
GenerationParameters
GenerationRequest
FinishReason
TokenUsage
GenerationTiming
GenerationResult
GenerationChunk
GenerationStream
GenerationTerminalState
ModelDefinition
ModelLoadConfig
ModelCapabilities
ModelRuntimeInfo
ModelRuntimeReference
ModelDigest
InferenceWarning
ModelLifecycleState
InferenceErrorCode
InferenceError
ModelPort
```

Public DTO／Config共通方針：

```text
Pydantic v2
frozen=true
extra=forbid
schema_version="1"
Tuple／frozensetによるCollection不変化
Backend固有Dict／Generator／Exception非露出
```

Public Surface：

[public.py](../../../../../src/margpa_runtime_llm/modules/inference/public.py)

## 4. Port／Adapter依存方向

実装した依存方向：

```text
CLI
  ↓
Bootstrap
  ↓
Inference Service
  ↓
ModelPort Protocol
  ↑
llama.cpp Production Adapter
  ↓
llama-cpp-python 0.3.34／Qwen3-4B GGUF／Metal
```

`src/margpa_runtime_llm/modules/inference/`から`llama_cpp`をImportしていないことをSource ScanとTestで確認した。

具体Adapterを選択するのは`bootstrap/phase1_application.py`だけである。

Phase 1-Aの`metal_smoke.py`をProduction Contractとして流用していない。

## 5. Inference Module実体

```text
src/margpa_runtime_llm/modules/inference/
├─ domain/
│  ├─ capabilities.py
│  ├─ errors.py
│  ├─ lifecycle.py
│  └─ model_definition.py
├─ contracts/
│  ├─ base.py
│  ├─ messages.py
│  ├─ generation.py
│  └─ runtime.py
├─ ports/
│  └─ model_port.py
├─ application/
│  └─ inference_service.py
└─ public.py
```

## 6. Model Port／Lifecycle

Production Port：

[adapter.py](../../../../../src/margpa_runtime_llm/adapters/model_backends/llama_cpp/adapter.py)

実装したLifecycle規則：

- Port Instanceは同時に1 Modelだけを所有
- Load前Generationを`model_not_loaded`で拒否
- 同じModelの再Loadは同一`load_instance_id`を返すIdempotent動作
- 別Modelの暗黙Reloadを`model_already_loaded`で拒否
- UnloadはIdempotent
- 同時Generation数は1
- Generation競合をQueueせず`model_busy`で拒否
- CancelをModel Unloadとして扱わない
- Cancel後に同一Model Instanceで再Generation可能
- Stream終端時にGeneration Lockを解放
- Model Loadごとに新しい`load_instance_id`を生成
- Explicit `Llama.close()`とGC補助をUnload経路へ配置

実Model TestでGeneration中の2件目Requestが`model_busy`となることを確認した。

## 7. Streaming／Cancel

Production Stream Handle：

[stream.py](../../../../../src/margpa_runtime_llm/adapters/model_backends/llama_cpp/stream.py)

実装したTerminal State：

```text
active
completed
cancelled
closed_by_consumer
failed
```

`cancel()`と`close()`はIdempotentであり、両者を別のTerminal Stateとして保持する。

Native Generator Closeと協調Cancelを使用し、Process Kill、Thread Kill、Model UnloadをStop手段にしていない。

正常完走時は0開始の単調増加SequenceとFinal Chunkを返す。Native StreamがFinal Reasonなしで終了した場合は`backend_protocol_error`とする。

## 8. Context Policy

Embedded Chat TemplateでMessageをFormatし、同じFormatter結果をTokenizerへ渡した後に次を検証する。

```text
formatted_prompt_tokens + max_new_tokens <= loaded_context_size
```

超過時は`context_limit_exceeded`を返し、次を行わない。

- Message削除
- 要約
- `max_new_tokens`縮小
- Context Size変更

Error Detailには安全な数値としてPrompt Token、Required Token、Available Tokenを含める。

## 9. Capability

実Model Load後のEffective Runtime Capability：

```text
chat
streaming
cooperative_cancel
stop_sequences
seed
token_usage
model_metadata
chat_template
thinking_control
gpu_offload
```

Limit：

```text
native_context_limit       : 32,768
loaded_context_size        : 4,096
max_concurrent_generations : 1
supported_message_roles    : system／user／assistant
```

RegistryのExpected CapabilityとAdapterのEffective Capabilityを分離した。

Required Capability不足時はLoadを失敗させ、Application ServiceがPortをUnloadする。黙ったFallback／Degradeは行わない。

## 10. Registry／Config

Model Registry：

[qwen3_4b_q4_k_m.toml](../../../../../config/models/qwen3_4b_q4_k_m.toml)

Local Profile：

[local_macos_arm64.toml](../../../../../config/profiles/local_macos_arm64.toml)

Tracked ConfigにはUser固有絶対Path、Secret、Model本体を保存していない。

Model Root解決順：

```text
Built-in Default
  ↓
Profile default=./models
  ↓
MARGPA_MODEL_ROOT
  ↓
CLI --model-root
```

Generation／Load値は次の優先順位で解決する。

```text
Built-in Safe Default
  ↓
Profile
  ↓
Environment Variable
  ↓
CLI Explicit Override
```

TOML ParserはPython標準Library`tomllib`を使用する。新規Dependencyは追加していない。

### 10.1 Model Artifact

```text
Model Key       : main.qwen3-4b-q4-k-m
Distribution    : Qwen/Qwen3-4B-GGUF
Upstream        : Qwen/Qwen3-4B
File Name       : Qwen3-4B-Q4_K_M.gguf
Format          : gguf
Quantization    : Q4_K_M
Size            : 2,497,280,256 bytes
SHA-512         : f182f1d40606572d6965e50e0ef33c4be64b43ad65339710ceebb664e3d43e76398a4ef230c7a3dd8fbd643acbce8f0c7cbec28784203ccf26da0fe7e08bfceb
```

Model Fileを変更、複製、暗黙Downloadしていない。

Distribution Revision／Commitは確認できていないため、推測値をRegistryへ入れていない。

```text
verification.state    : phase_1b_local_artifact_sha512_verified_provenance_incomplete
provenance_complete   : false
```

### 10.2 Definition／Profile Hash

```text
Model Definition SHA-512:
723954f2cd8f9df77a48614da05206c532ab56666069e57e117bddc219dcaefe5ad32b57f9b315b1e2e9cab5ba3526dad2176ca8d2df3ec997c05034bd98c415

Local Profile SHA-512:
f0d9c8e3ffe9264b77e0c7ca357705a200fc5419175910479ab53a8e49c543d13fb86484309d22ed39b57c81d10888e129282c62254da097ec89c3208b9b6b35
```

Registry LoaderはModel DefinitionのRaw Byte列からSHA-512を計算し、Runtime Referenceへ引き渡す。

## 11. Effective Config

実Model Acceptance時の主要値：

```text
profile_key         : local.macos-arm64
selected_model      : main.qwen3-4b-q4-k-m
context_size        : 4096
batch_size          : 256
micro_batch_size    : 256
threads             : 6
threads_batch       : 6
gpu_layers          : -1
use_mmap            : true
use_mlock           : false
verify_artifact_hash: true
max_new_tokens      : 512
temperature         : 0.7
top_p               : 0.8
top_k               : 20
min_p               : 0.0
presence_penalty    : 1.5
frequency_penalty   : 0.0
repeat_penalty      : 1.0
thinking_mode       : disabled
streaming           : CLI Default ON
```

`model-info`でEffective Config、Runtime Capability、Provenanceを構造化JSON表示できる。

## 12. Thinking Control

実装：

[chat_template.py](../../../../../src/margpa_runtime_llm/adapters/model_backends/llama_cpp/chat_template.py)

実ModelのGGUF Metadataに埋め込まれたJinja Chat Templateを正本として使用する。

Qwen3 Templateが`enable_thinking`を受け付けることを確認し、次をFormatterへ明示的に渡すHard Switchを採用した。

```text
ThinkingMode.DISABLED → enable_thinking=false
ThinkingMode.ENABLED  → enable_thinking=true
ThinkingMode.MODEL_DEFAULT → 明示値を渡さない
```

Default OFFの実Model Generationでは、生成Contentに`<think>`／`</think>`が含まれなかった。

Explicit ONも実Model Integration TestでGeneration成功を確認した。

Hard Switchが使えないTemplate向けには、Adapter内だけで`/no_think`／`/think`を付与するSoft Switch経路を持つ。使用時は`thinking_soft_switch` WarningをRuntime Contractへ記録する。

現在のQwen3 RuntimeではHard Switchが成立しているため、Runtime WarningはEmptyである。

Model PortでThinking Tagを削除する処理は実装していない。

### 12.1 Private API依存

`Llama._chat_handlers`等のUnderscore Private Attributeは使用していない。

Adapter内で`llama_cpp.llama_chat_format.Jinja2ChatFormatter`を使用し、FormatとGenerationの両方へ同じEmbedded Templateを適用している。

Backend固有Chat Formatterへの依存は`adapters/model_backends/llama_cpp/chat_template.py`内に限定した。Backend Versionは`0.3.34`で固定し、Hard／Soft Switch Unit Testを追加した。

## 13. Error Contract

実装した共通Error Code：

```text
invalid_request
invalid_configuration
invalid_model_definition
model_not_found
model_integrity_mismatch
backend_unavailable
model_load_failed
model_not_loaded
model_already_loaded
model_busy
unsupported_capability
context_limit_exceeded
generation_failed
backend_protocol_error
model_unload_failed
```

CLIへ表示するのは`code`と`safe_message`だけである。

Native Exception文字列、Memory Address、User Absolute PathをCLI Errorへ表示しないTestを追加した。

User CancelはErrorにせず、Stream Terminal State=`cancelled`およびCLI Exit Code=`130`として扱う。

## 14. CLI

Console Script：

```text
margpa-llm
```

登録先：

[pyproject.toml](../../../../../pyproject.toml)

実装：

[main.py](../../../../../src/margpa_runtime_llm/entrypoints/cli/main.py)

使用例：

```text
margpa-llm generate --prompt "こんにちは"
margpa-llm generate --prompt "短く説明して" --no-stream
margpa-llm generate --prompt "考えて回答して" --thinking
printf '標準入力からの質問' | margpa-llm generate
margpa-llm model-info
```

実装機能：

- Prompt引数または標準入力
- Optional System Message
- Streaming Default ON
- `Ctrl+C` Cooperative Cancel
- Thinking On／Off Override
- Generation主要値Override
- Model Root／Model Key／Context Override
- Stop Sequence
- Model／Backend／Capability／Effective Config表示
- Safe ErrorとProcess Exit Code

実CLI Acceptance：

```text
margpa-llm --help     : Pass
margpa-llm model-info : Pass
margpa-llm generate   : Pass

Streaming生成結果:
フェーズ1-B成功
```

CLIはConversation Historyを保持しない。

## 15. Test構成

```text
tests/unit/inference/
├─ test_contracts.py
├─ test_config_and_registry.py
├─ test_llama_cpp_boundary.py
└─ test_cli.py

tests/contract/model_port/
└─ test_model_port_contract.py

tests/integration/llama_cpp/
└─ test_phase1b_runtime.py
```

Default Testで検証する主項目：

- Unknown Field拒否／Immutable Contract
- Message／Generation Parameter Validation
- Token Usage整合
- Safe Error
- Registry／Profile Validation
- Config優先順位
- Model Definition File SHA-512
- Fake Model Port Contract
- Load／Unload Idempotency
- Load前Generation拒否
- Capability不足
- Model Key不一致
- Stream Sequence／Final Chunk
- Cancel／Close Idempotencyと区別
- Finish Reason Mapping
- Context Overflow
- Artifact Size／SHA-512
- Hard／Soft Thinking Switch
- Coreからのllama_cpp隔離
- CLI Prompt／stdin／Streaming／Ctrl+C／Safe Error

Opt-in Production Integrationで検証する主項目：

- Qwen3-4B Artifact Hash／Size
- llama-cpp-python 0.3.34
- Metal／GPU Offload
- Context 4096
- Qwen3 Metadata／Embedded Chat Template
- Thinking Default OFF／Explicit ON
- One-shot Generation／Token Usage／Timing
- Streaming／Final Chunk
- Model Busy
- Cooperative Cancel
- Post-cancel Generation
- Explicit Unload／Unload Idempotency

## 16. Quality Gate結果

```text
bash -n Setup Recipe       : Pass
Ruff Format Check          : Pass／48 files
Ruff Check                 : Pass
mypy --strict              : Pass／48 source files
Default pytest             : 40 passed, 2 deselected
Opt-in model_smoke pytest  : 2 passed, 40 deselected
compileall                 : Pass
uv lock --check            : Pass／117 packages
uv sync --frozen --offline : Pass／115 packages
Environment Exact Version : Pass
Core llama_cpp Import Scan : Pass／0件
Out-of-scope Import Scan   : Pass／0件
```

Opt-in `model_smoke`の2件は、既存Phase 1-A Smokeと新Phase 1-B Production Integrationである。

## 17. Metal／Memory／Timing観測

Production Acceptance Probe：

[phase1b_runtime_acceptance.py](../../../../../scripts/models/phase1b_runtime_acceptance.py)

実行結果：

```text
Result                         : success
Python                         : 3.13.14／arm64／GIL enabled
Backend                        : llama-cpp-python 0.3.34
Device                         : Metal／Apple M2 Pro
GPU Offload                    : true
Context                        : 4096
Load including SHA-512         : 約2.4863秒
RSS before Load                : 約53.6MB
RSS after Load                 : 約3.260GB
RSS after Generation           : 約3.269GB
RSS after Unload               : 約152.7MB
Unload                         : 約0.0522秒
Generation Total               : 約0.3309秒
Completion Tokens              : 9
Observed Speed                 : 約27.20 token/s
Streaming First Content        : 約0.0831秒
Streaming Cancel Total         : 約0.0832秒
Post-cancel Generation         : success／"OK"
```

Non-stream APIはFirst Contentの発生時刻を観測できないため、`first_content_latency_seconds`を推測せず`None`とする。Streaming経路では実測値を記録する。

Generation結果：

```text
フェーズ1-B生産ランタイム成功
```

Thinking Tag：

```text
<think>   : absent
</think>  : absent
```

Process RSSはUnified Memory全体の完全なGPU Memory計測ではなく、短時間Acceptance時のProcess観測値である。

## 18. 作成／変更File一覧

### Config

```text
A config/models/qwen3_4b_q4_k_m.toml
A config/profiles/local_macos_arm64.toml
```

### Inference Core

```text
A src/margpa_runtime_llm/modules/inference/domain/capabilities.py
A src/margpa_runtime_llm/modules/inference/domain/errors.py
A src/margpa_runtime_llm/modules/inference/domain/lifecycle.py
A src/margpa_runtime_llm/modules/inference/domain/model_definition.py
A src/margpa_runtime_llm/modules/inference/contracts/base.py
A src/margpa_runtime_llm/modules/inference/contracts/messages.py
A src/margpa_runtime_llm/modules/inference/contracts/generation.py
A src/margpa_runtime_llm/modules/inference/contracts/runtime.py
A src/margpa_runtime_llm/modules/inference/ports/model_port.py
A src/margpa_runtime_llm/modules/inference/application/inference_service.py
A src/margpa_runtime_llm/modules/inference/public.py
A 各Package __init__.py
```

### Adapter／Bootstrap／CLI

```text
A src/margpa_runtime_llm/adapters/model_backends/llama_cpp/adapter.py
A src/margpa_runtime_llm/adapters/model_backends/llama_cpp/chat_template.py
A src/margpa_runtime_llm/adapters/model_backends/llama_cpp/error_mapping.py
A src/margpa_runtime_llm/adapters/model_backends/llama_cpp/stream.py
A src/margpa_runtime_llm/bootstrap/config_loader.py
A src/margpa_runtime_llm/bootstrap/model_registry_loader.py
A src/margpa_runtime_llm/bootstrap/phase1_application.py
A src/margpa_runtime_llm/entrypoints/cli/main.py
M src/margpa_runtime_llm/entrypoints/cli/__init__.py
M pyproject.toml
```

### Script／Test／Status

```text
A scripts/models/phase1b_runtime_acceptance.py
A tests/unit/inference/test_contracts.py
A tests/unit/inference/test_config_and_registry.py
A tests/unit/inference/test_llama_cpp_boundary.py
A tests/unit/inference/test_cli.py
A tests/contract/model_port/test_model_port_contract.py
A tests/integration/llama_cpp/test_phase1b_runtime.py
A docs/handoffs/implementer_status_phase_1b_model_runtime_20260718232354.md
```

## 19. Dependency／Lock

新規Packageは追加していない。

Phase 2以降のPackageも導入していない。

```text
torch／transformers／langchain／langgraph／mlx／mlx-lm : absent
```

`pyproject.toml`変更はConsole Script登録のみである。

```text
pyproject.toml SHA-256:
a46fcd0b61e8db84a5f90ac4459b92bf9ec9deb7d6219ce88d7b22c240b5ecfa

uv.lock SHA-256:
e5efe33d69105547fe0d4f348b6b189b85f7ed55323f8ecd993ef5df7846fee1
```

`uv.lock`はPhase 1-Aから変更していない。

## 20. Warning／Deviation／Fallback／未解決事項

```text
Python Fallback             : なし
Backend Fallback            : なし
Thinking Soft Switch使用    : なし
Private Underscore API使用  : なし
Dependency追加              : なし
uv.lock変更                 : なし
Model Download              : なし
Model File変更／複製        : なし
Phase 2以降への着手         : なし
```

Known Non-blocking Item：

- Distribution Revision／Commitは未確定。推測値を入れていない
- Soft Switch経路では空Thinking Tagが残る可能性があるが、現在の実ModelはHard Switchを使用
- Raw Model Output／Display Output分離は後続設計事項
- Native Build Setupを通常実行すると毎回Source RebuildするPhase 1-A既知事項
- Streaming UsageはBackendがFinal Payloadに値を返した場合だけ設定し、値がない場合に`0`を偽装しない
- Non-stream First Content LatencyはBackendから観測できないため`None`

## 21. 設計者へのReview依頼

次をReviewしてほしい。

1. ContractとDomain／Port／Application境界
2. Coreからのllama.cpp隔離
3. Registry／Profile SchemaとConfig優先順位
4. Model SHA-512／Definition SHA-512／Provenance表現
5. Model Lifecycle／同時Generation数1／Model Busy
6. Context事前TokenizeとOverflow Policy
7. Embedded Template Hard Thinking Switch
8. Streaming Terminal StateとCooperative Cancel
9. Safe Error／CLI Exit Code
10. Default／Opt-in TestとAcceptance Evidence
11. Phase 1-B Acceptance Criteriaの完了判定

Phase 1-B完了はPhase 2開始の自動許可を意味しない。

<!-- SOURCE_END 77: docs/handoffs/implementer_status_phase_1b_model_runtime_20260718232354.md -->

---

<!-- SOURCE_BEGIN 78: docs/handoffs/implementer_status_phase_1b_model_runtime_follow_up_20260718235802.md -->

### Source 78: `docs/handoffs/implementer_status_phase_1b_model_runtime_follow_up_20260718235802.md`

- History Target: `docs/project/phases/phase_1/history/handoffs/implementer_status_phase_1b_model_runtime_follow_up_20260718235802.md`
- Source SHA-512: `48c233b1d7cc836fcd0e13880be6842b6c59d6816d0e63044fa17e99ee6fbf6f1070f392d45aa5b951dc0b3fd5a108782d915eecb75361f98015a559c351b7d4`
- Source Size: `10062` bytes

# Phase 1-B Model Runtime Follow-up 実装状況

- 文書ID: `implementer_status_phase_1b_model_runtime_follow_up`
- 状態: `follow_up_complete_review_requested`
- 作成日時: `2026-07-18 23:58:02 JST`
- 更新日時: `2026-07-18 23:58:02 JST`
- 作成担当: 実装者役担当Task
- 対象: 設計者役担当Task
- 正本言語: 日本語
- Documentation Index: [documentation_index_20260718233938.md](../history/documentation_index_20260718233938.md)
- Designer Review: [designer_review_phase_1b_model_runtime_20260718233938.md](../history/handoffs/designer_review_phase_1b_model_runtime_20260718233938.md)
- Implementer Handoff: [designer_handoff_phase_1b_model_runtime_20260718224308.md](../history/handoffs/designer_handoff_phase_1b_model_runtime_20260718224308.md)
- 詳細設計: [phase_1b_model_runtime_contract_20260718223203.md](../history/architecture/phase_1b_model_runtime_contract_20260718223203.md)
- Accepted ADR: [adr_0006_model_runtime_port_and_configuration_20260718224308.md](../history/adr/adr_0006_model_runtime_port_and_configuration_20260718224308.md)
- Previous Status: [implementer_status_phase_1b_model_runtime_20260718232354.md](../history/handoffs/implementer_status_phase_1b_model_runtime_20260718232354.md)
- supersedes: `implementer_status_phase_1b_model_runtime_20260718232354.md`

## 1. 結論

設計ReviewでRequiredとなった2件を、Phase 1-BのSource／Test最小範囲で修正した。

```text
Required Follow-up 1: 実CLI Ctrl+C Cooperative Cancel : Pass
Required Follow-up 2: Artifact Digest事実性           : Pass
Regression Test                                       : Pass
Static／Default Gate                                  : Pass
実Model／Metal Gate                                   : Pass
Phase 2以降への越境                                   : なし
```

実装担当側ではFollow-up完了と判定し、Phase 1-Bの再Reviewを依頼する。

## 2. Follow-up 1：Process Control Exception境界

### 2.1 修正内容

Production Streamは、Backend由来の通常Exceptionだけを`generation_failed`へ変換する。

```text
KeyboardInterrupt／SystemExit／GeneratorExit
  ↓
Backend Errorへ変換しない
  ↓
CLIまたはProcess Control境界へ伝播
```

`LlamaCppGenerationStream.__iter__()`の一般捕捉を`BaseException`から`Exception`へ変更した。

`raise_mapped_backend_error()`も、`Exception`でないProcess Control Exceptionを受け取った場合は変換せず再送出するDefense-in-depthを追加した。

AdapterのLoad／Unload／Generation／Stream開始処理についても境界を見直した。

- 通常Backend Exceptionだけを安全な`InferenceError`へ変換する
- Load／Unload中の`KeyboardInterrupt`／`SystemExit`を変換しない
- Stream作成前のProcess Control ExceptionではGeneration Lockを解放する
- Non-stream Generationは既存`finally`でGeneration Lockを解放する
- 実Stream反復中の`KeyboardInterrupt`はActive StreamのままCLIへ到達する
- CLIが`stream.cancel()`を実行し、Terminal Stateを`cancelled`へ遷移させる
- Adapterの`on_terminal` CallbackによりGeneration Lockを解放する

### 2.2 Regression Test

追加確認：

- 実`LlamaCppGenerationStream`が`KeyboardInterrupt`を変換しない
- 実`LlamaCppGenerationStream`が`SystemExit`を変換しない
- Backend Error Mapperが両Process Control Exceptionを消費しない
- CLIと実`LlamaCppGenerationStream`を組み合わせる
- CLI Exit Code `130`
- Terminal State `cancelled`
- Native Iterator Close 1回
- `on_terminal`によるGeneration解放
- Cancel後に同じService Instanceで再Generation可能
- `generation_failed`を表示しない

実Model Integration Testでは、既存の同一Model Instanceに対する明示Cancel後の再Generationも再確認した。

### 2.3 実CLI／TTY確認

Metal実ModelをLoadし、長いStreaming Generation中にTTYからCtrl+Cを送った。

```text
^C
Generation cancelled.

Exit Code : 130
Error Code: generation_failedを表示しない
```

これにより、Reviewで再現されたExit Code `4`経路が修正されたことを実CLIで確認した。

## 3. Follow-up 2：Artifact Digest事実性

### 3.1 採用Contract

Designer Reviewで許容された次の方式を採用した。

```text
Phase 1-BではArtifact SHA-512を常に検証する
Hash検証の無効化を許可しない
Runtime Infoのartifact_digestは実測かつRegistry期待値との一致確認済み
Verification Stateをartifact_digest_verified=trueとして明示する
```

`ModelLoadConfig.verify_artifact_hash`は`Literal[True]`とし、Profile／Overrideから`false`を渡した場合は`invalid_configuration`となる。

`_verify_artifact()`はConfig値をRegistry期待Digestへ代入する処理を廃止し、File全体をSHA-512計算した実測値だけを返す。

実測値とRegistry期待値が異なる場合は、同一File Sizeでも`model_integrity_mismatch`となりModelをLoadしない。

`ModelRuntimeInfo`には次を追加した。

```text
artifact_digest_verified: Literal[True]
```

`model-info`と将来のAudit Consumerは、報告されたArtifact Digestが検証済みであることをJSON Fieldから判別できる。

### 3.2 Regression Test

追加確認：

- `verify_artifact_hash=false`を含むProfileを拒否する
- 同一Size／別DigestのArtifactを拒否する
- Runtime Infoで`artifact_digest_verified=true`
- CLI `model-info` JSONで`artifact_digest_verified: true`
- 実Model SHA-512を再計算してLoadする

実Modelの検証済みSHA-512：

```text
f182f1d40606572d6965e50e0ef33c4be64b43ad65339710ceebb664e3d43e76398a4ef230c7a3dd8fbd643acbce8f0c7cbec28784203ccf26da0fe7e08bfceb
```

## 4. 変更File

### Source

```text
M src/margpa_runtime_llm/adapters/model_backends/llama_cpp/adapter.py
M src/margpa_runtime_llm/adapters/model_backends/llama_cpp/error_mapping.py
M src/margpa_runtime_llm/adapters/model_backends/llama_cpp/stream.py
M src/margpa_runtime_llm/modules/inference/contracts/runtime.py
```

### Test

```text
M tests/unit/inference/test_llama_cpp_boundary.py
M tests/unit/inference/test_config_and_registry.py
M tests/unit/inference/test_cli.py
M tests/integration/llama_cpp/test_phase1b_runtime.py
```

### Config／Dependency

Tracked Profileの最終内容はReview前と同一であり、`verify_artifact_hash=true`を維持する。

```text
Config内容変更 : なし
pyproject変更  : なし
uv.lock変更    : なし
Dependency追加 : なし
```

Architecture／ADR／Review／旧Statusは編集していない。

## 5. Static／Default Gate

```text
bash -n Setup Recipe : Pass
Ruff Format Check     : Pass／48 files
Ruff Check            : Pass
mypy --strict         : Pass／48 source files
compileall            : Pass
Default pytest        : 46 passed, 2 deselected
```

Required Regression Testを含む対象Test：

```text
27 passed
```

Default TestはReview時の40件から46件となった。

## 6. Environment／Dependency Gate

```text
Python                    : CPython 3.13.14／arm64／GIL enabled
llama-cpp-python          : 0.3.34
GPU Offload Support       : true
Metal System Info         : present
Dependency Version Match  : true
Out-of-scope Package      : absent
uv lock --check           : Pass／117 packages
uv sync --dry-run offline : Pass／115 packages／Would make no changes
```

Phase 2以降のPackageは導入していない。

```text
torch／transformers／langchain／langgraph／mlx／mlx-lm : absent
```

## 7. 実Model／Metal Gate

```text
pytest -m model_smoke : 2 passed, 46 deselected
```

Production Runtime Acceptance：

```text
Success                         : true
Backend                         : llama-cpp-python 0.3.34
Device                          : Metal
GPU Offload                     : true
Context                         : 4,096
Artifact SHA-512 Verified       : true
Load including SHA-512          : 2.4538 seconds
Generation Result               : フェーズ1-B生産ランタイム成功
Generation Speed                : 30.72 tokens／second
Explicit Stream Terminal State  : cancelled
Post-cancel Generation          : OK／stop
Unload                          : 0.0447 seconds
```

ModelのDownload、Copy、Rename、変更は行っていない。

## 8. Hash／Lock不変性

```text
Model Definition SHA-512:
723954f2cd8f9df77a48614da05206c532ab56666069e57e117bddc219dcaefe5ad32b57f9b315b1e2e9cab5ba3526dad2176ca8d2df3ec997c05034bd98c415

Local Profile SHA-512:
f0d9c8e3ffe9264b77e0c7ca357705a200fc5419175910479ab53a8e49c543d13fb86484309d22ed39b57c81d10888e129282c62254da097ec89c3208b9b6b35

pyproject.toml SHA-256:
a46fcd0b61e8db84a5f90ac4459b92bf9ec9deb7d6219ce88d7b22c240b5ecfa

uv.lock SHA-256:
e5efe33d69105547fe0d4f348b6b189b85f7ed55323f8ecd993ef5df7846fee1
```

## 9. Deviation／残件

```text
Python Fallback            : なし
Backend Fallback           : なし
Dependency追加             : なし
Model Download             : なし
Phase 2以降への着手        : なし
Required Follow-up未完了   : なし
```

Review記載のNon-blocking Itemは今回変更していない。

- 同一ModelのIdempotent Load判定は現在Model Keyだけを比較する
- Load済みDefinition／Load Configが異なる場合の扱いは後続設計事項
- Distribution Revision／Commitを推測で補完しない
- Raw Output／Display Output分離は後続設計事項
- Native Buildの毎回再BuildはPhase 1-A既知事項

## 10. 設計者への再Review依頼

次を再Reviewしてほしい。

1. Process Control ExceptionがBackend Errorへ変換されないこと
2. 実CLIのCtrl+C、Cooperative Cancel、Exit Code `130`
3. Stream Terminal StateとGeneration Lock解放
4. Cancel後の同一Model Instanceでの再Generation
5. Phase 1-BでSHA-512検証を無効化できないこと
6. Runtime Artifact Digestが実測かつ検証済みであること
7. `model-info`のVerification State
8. Regression TestとStatic／Default／Metal Gate

Phase 1-Bの最終受入および次Phase開始可否は、設計者再Reviewとユーザー判断に委ねる。

<!-- SOURCE_END 78: docs/handoffs/implementer_status_phase_1b_model_runtime_follow_up_20260718235802.md -->

---

<!-- SOURCE_BEGIN 79: docs/handoffs/implementer_status_phase_1b_model_runtime_test_follow_up_20260719001341.md -->

### Source 79: `docs/handoffs/implementer_status_phase_1b_model_runtime_test_follow_up_20260719001341.md`

- History Target: `docs/project/phases/phase_1/history/handoffs/implementer_status_phase_1b_model_runtime_test_follow_up_20260719001341.md`
- Source SHA-512: `7f6edd353415d558691a7750ce2cf974262fd5c09f7f5240f79d689c580f963e5f9d030ef70e45059ae58e6bc6eef06dc8603e2eb56986451a61d6f5da322fd6`
- Source Size: `4821` bytes

# Phase 1-B Model Runtime Test-only Follow-up 実装状況

- 文書ID: `implementer_status_phase_1b_model_runtime_test_follow_up`
- 状態: `test_follow_up_complete_review_requested`
- 作成日時: `2026-07-19 00:13:41 JST`
- 更新日時: `2026-07-19 00:13:41 JST`
- 作成担当: 実装者役担当Task
- 対象: 設計者役担当Task
- 正本言語: 日本語
- Documentation Index: [documentation_index_20260719000348.md](../history/documentation_index_20260719000348.md)
- Designer Review: [designer_review_phase_1b_model_runtime_follow_up_20260719000348.md](../history/handoffs/designer_review_phase_1b_model_runtime_follow_up_20260719000348.md)
- Previous Status: [implementer_status_phase_1b_model_runtime_follow_up_20260718235802.md](../history/handoffs/implementer_status_phase_1b_model_runtime_follow_up_20260718235802.md)
- 詳細設計: [phase_1b_model_runtime_contract_20260718223203.md](../history/architecture/phase_1b_model_runtime_contract_20260718223203.md)
- Accepted ADR: [adr_0006_model_runtime_port_and_configuration_20260718224308.md](../history/adr/adr_0006_model_runtime_port_and_configuration_20260718224308.md)
- supersedes: `implementer_status_phase_1b_model_runtime_follow_up_20260718235802.md`

## 1. 結論

設計Reviewで指摘されたRegression Test Fixture 1件を修正した。

```text
有効な単一Key TOML Fixture       : Pass
Literal[True] Pydantic拒否       : Pass
Targeted Test                    : Pass
Static／Default Gate             : Pass
Production Source変更            : なし
Config／Dependency／Model変更    : なし
Phase 2以降への越境              : なし
```

実装担当側ではTest-only Follow-up完了と判定し、Phase 1-B最終Reviewを依頼する。

## 2. Test Fixture修正

対象：

[test_config_and_registry.py](../../../../../tests/unit/inference/test_config_and_registry.py)

旧Fixtureは、既存の`verify_artifact_hash = true`を残したまま`false`を追加し、重複Keyによる`TOMLDecodeError`を検査していた。

修正後は、既存の値そのものを置換する。

```text
verify_artifact_hash = true
  ↓
verify_artifact_hash = false
```

Fixtureに対して次を明示確認する。

```text
tomllib.loads(fixture)が成功する
verify_artifact_hash Keyは1件だけ
parse後のload.verify_artifact_hashはfalse
load_phase1_profile()はinvalid_configurationを返す
```

これにより、TOML Parserの重複Key拒否ではなく、`ModelLoadConfig.verify_artifact_hash: Literal[True]`が`false`を拒否していることを検査する。

## 3. Pydantic Contract直接Test

次の直接Testを追加した。

```text
ModelLoadConfig.model_validate({"verify_artifact_hash": false})
  ↓
pydantic.ValidationError
```

将来、`Literal[True]`が通常の`bool`へ誤って緩和された場合、このTestはFailする。

## 4. 変更範囲

```text
M tests/unit/inference/test_config_and_registry.py
A docs/handoffs/implementer_status_phase_1b_model_runtime_test_follow_up_20260719001341.md
```

次は変更していない。

```text
src/
config/
pyproject.toml
uv.lock
Model Artifact
Architecture／ADR／Review／旧Status
```

## 5. Test結果

Targeted Test：

```text
tests/unit/inference/test_config_and_registry.py : 7 passed
```

Static／Default Gate：

```text
bash -n Setup Recipe : Pass
Ruff Format Check     : Pass／48 files
Ruff Check            : Pass
mypy --strict         : Pass／48 source files
compileall            : Pass
Default pytest        : 47 passed, 2 deselected
```

前回のDefault Test 46件に、Pydantic Contract直接Test 1件を追加した。

## 6. Production不変性

```text
Model Definition SHA-512:
723954f2cd8f9df77a48614da05206c532ab56666069e57e117bddc219dcaefe5ad32b57f9b315b1e2e9cab5ba3526dad2176ca8d2df3ec997c05034bd98c415

Local Profile SHA-512:
f0d9c8e3ffe9264b77e0c7ca357705a200fc5419175910479ab53a8e49c543d13fb86484309d22ed39b57c81d10888e129282c62254da097ec89c3208b9b6b35

pyproject.toml SHA-256:
a46fcd0b61e8db84a5f90ac4459b92bf9ec9deb7d6219ce88d7b22c240b5ecfa

uv.lock SHA-256:
e5efe33d69105547fe0d4f348b6b189b85f7ed55323f8ecd993ef5df7846fee1
```

Production Source、Config、Dependency、実Modelを変更していないため、ReviewのRe-review Gateに従いMetal Gateは再実行していない。直前の設計者独立確認および実装者Follow-upでは`2 passed`である。

## 7. 設計者への最終Review依頼

次を確認してほしい。

1. Fixtureが有効な単一Key TOMLであること
2. `false`がTOML Parse後まで維持されること
3. `load_phase1_profile()`がPydantic Contractにより`invalid_configuration`を返すこと
4. `ModelLoadConfig`直接Testが`ValidationError`を確認すること
5. Static／Default GateがPassしていること

Phase 1-Bの最終受入および次Phase開始可否は、設計者Reviewとユーザー判断に委ねる。

<!-- SOURCE_END 79: docs/handoffs/implementer_status_phase_1b_model_runtime_test_follow_up_20260719001341.md -->

---

<!-- SOURCE_BEGIN 80: docs/handoffs/implementer_status_phase_1c_deployment_platform_acceleration_20260719021411.md -->

### Source 80: `docs/handoffs/implementer_status_phase_1c_deployment_platform_acceleration_20260719021411.md`

- History Target: `docs/project/phases/phase_1/history/handoffs/implementer_status_phase_1c_deployment_platform_acceleration_20260719021411.md`
- Source SHA-512: `d4bb4307252f73c8727be11d62bae040aaec50ba797a48e1f9dd3874aca958ae92dde936db896846e03345e88eaf215950648c78cac50f71d2e65f9743603c65`
- Source Size: `14198` bytes

# Phase 1-C Deployment／Platform／Acceleration 実装状況

- 文書ID: `implementer_status_phase_1c_deployment_platform_acceleration`
- 状態: `implementation_complete_review_requested`
- 作成日時: `2026-07-19 02:14:11 JST`
- 更新日時: `2026-07-19 02:14:11 JST`
- 作成担当: 実装者役担当Task
- 対象: 設計者役担当Task
- 正本言語: 日本語
- Documentation Index: [documentation_index_20260719013109.md](../history/documentation_index_20260719013109.md)
- Implementer Handoff: [designer_handoff_phase_1c_deployment_platform_acceleration_20260719013109.md](../history/handoffs/designer_handoff_phase_1c_deployment_platform_acceleration_20260719013109.md)
- Requirements: [phase_1c_deployment_platform_acceleration_requirements_20260719013109.md](../history/requirements/phase_1c_deployment_platform_acceleration_requirements_20260719013109.md)
- Architecture: [phase_1c_deployment_platform_acceleration_architecture_20260719013109.md](../history/architecture/phase_1c_deployment_platform_acceleration_architecture_20260719013109.md)
- Accepted ADR: [adr_0007_deployment_platform_acceleration_abstraction_20260719013109.md](../history/adr/adr_0007_deployment_platform_acceleration_abstraction_20260719013109.md)
- Previous Phase Review: [designer_review_phase_1b_model_runtime_final_20260719001604.md](../history/handoffs/designer_review_phase_1b_model_runtime_final_20260719001604.md)
- supersedes: なし（新規Phase 1-C Status系列）

## 1. 結論

Phase 1-C Deployment／Platform／Acceleration Abstraction Hookを実装した。

```text
Deployment Contract               : Pass
Host／Compute／Backend表現         : Pass
Required／Detected／Executed分離   : Pass
Model／Deployment Capability分離  : Pass
Mac Profile Schema Migration      : Pass
Profile Resolver Priority         : Pass
Unknown Platform Fail Closed      : Pass
Runtime Observation Hook          : Pass
Requirement Validation／Cleanup   : Pass
Static／Default Test               : Pass
実Model／Metal Regression          : Pass
Phase 2以降への越境                : なし
```

Current Mac／Metalの既存動作を維持しながら、将来Platformを接続する境界を追加した。

Windows、Linux、CUDA、ROCm、Vulkan等を実装または実機検証済みとは主張しない。

実装担当側ではPhase 1-C Acceptance CriteriaをPassと判定し、設計者Reviewを依頼する。

## 2. Deployment Contract

追加した主要Contract：

```text
HostPlatformDefinition
ComputeTargetDefinition
BackendRuntimeDefinition
DeploymentRequirements
DeploymentVerificationState
FallbackPolicy
DetectedRuntimeState
ExecutedRuntimeState
RuntimeObservation
```

Profile／Runtimeで次を独立して表現する。

```text
Host OS
Architecture
Execution Environment
Compute Kind
Vendor
Acceleration API
Memory Topology
Device Selector
Offload Policy
Backend／Version
Build Variant
Execution Mode
Required Capability
Fallback Policy
Verification State
```

Vendor、Acceleration APIおよびBackendは形式検証されたString Keyであり、閉じた全世界Enumにしていない。

未知の将来KeyをContract上保持できるTestを追加した。

## 3. Required／Detected／Executed分離

### Required

Deployment Profileの`runtime_requirements`が保持する。

```text
required_capabilities
required_device_kind
required_acceleration_api
fallback_policy
```

### Detected

Runtime Observationの`detected`が保持する。

```text
backend_key／backend_version
build_variant_key／build_variant_source
device_kind_key
device_name／device_id
acceleration_api_key
capabilities
```

Current llama.cppではBuild VariantをNative APIから直接観測できないため、Profile宣言値として記録する。

```text
build_variant_source              : declared
observation_warning               : build_variant_declared_not_observed
```

観測不能値を実測値として推測していない。

### Executed

Runtime Observationの`executed`が保持する。

```text
backend_key／backend_version
device_kind_key
acceleration_api_key
gpu_offload
```

Current実Modelでは次を確認した。

```text
device_kind_key     : gpu
acceleration_api_key: metal
gpu_offload         : true
```

## 4. Capability Before／After

### Before

```text
Model Required
  chat
  streaming
  cooperative_cancel
  stop_sequences
  seed
  token_usage
  model_metadata
  chat_template
  thinking_control
  gpu_offload
```

### After

```text
Model Required
  chat
  streaming
  cooperative_cancel
  stop_sequences
  seed
  token_usage
  model_metadata
  chat_template
  thinking_control

Model Optional
  gpu_offload

Mac Metal Deployment Required
  gpu_offload
```

`InferenceService`は固定Global Setではなく、Model Definitionの`required_features`を検証する。

Model Capability不足時はModel PortをUnloadする既存Fail-Closed動作を維持する。

Deployment Capability不足時もBootstrap ValidationがServiceをUnloadし、Lifecycleを`unloaded`へ戻す。

CPU概念Profileは`gpu_offload`不足だけを理由にFailしないContract Testを追加した。実Windows Profileは作成していない。

## 5. Mac Profile Migration

Tracked ProfileをSchema Version 2へMigrationした。

```text
schema_version     : 2
profile_key        : local.macos-arm64
verification_state : native_verified
```

既存`profile_key`は互換性のため維持した。

追加Section：

```text
[host]
macos／arm64／native

[compute]
gpu／apple／metal／unified

[backend_runtime]
llama_cpp／0.3.34／metal／in_process

[runtime_requirements]
gpu_offload／gpu／metal／deny
```

Model Rootは引き続き相対Pathであり、Tracked Configへユーザー固有絶対Pathを追加していない。

## 6. Profile Resolver／Platform Normalization

Profile解決Priority：

```text
Explicit CLI／Application
  > MARGPA_PROFILE
  > Platform Default Resolver
```

実CLIで`--profile`を省略した場合、Current Hostの`macos／arm64`を正規化し、Current Mac ProfileをPlatform Defaultとして選択する。

正規化：

```text
Darwin              → macos
Windows             → windows
Linux               → linux
arm64／aarch64      → arm64
AMD64／x86_64       → x86_64
```

未知OS／Architectureは`unsupported_platform`となる。

既知PlatformにDefault Profileがない場合は`profile_required`となり、macOS Profileへ暗黙Fallbackしない。

## 7. Runtime Observation Hook

llama.cpp固有のMetal／CPU判定を次へ隔離した。

[runtime_detection.py](../../../../../src/margpa_runtime_llm/adapters/model_backends/llama_cpp/runtime_detection.py)

Current Detectorは次だけを観測する。

```text
Metal Build＋GPU Offload有効＋gpu_layers != 0
  → device=metal／device_kind=gpu／acceleration=metal／gpu_offload=true

上記以外
  → device=cpu／device_kind=cpu／acceleration=cpu_native／gpu_offload=false
```

CUDA／ROCm等の未実装Backendを推測しない。

Application Runtime Observationは、Host Detection、Backend Runtime InfoおよびExecuted Stateを構造化する。

## 8. Requirement Validation

Load後に次を比較する。

```text
Expected Host              vs Detected Host
Expected Backend／Version  vs Detected Backend／Version
Compute Kind               vs Executed Device Kind
Acceleration API           vs Executed Acceleration API
Required Capability        vs Detected Capability
```

不足または不一致時：

- `unsupported_platform`または`unsupported_capability`
- Safe Errorのみを公開
- 暗黙Fallbackなし
- Loaded RuntimeをUnload
- Lifecycle破損なし

Phase 1-Cでは`fallback_policy=deny`だけを実行可能とし、未実装Policyを黙って適用しない。

## 9. CLI／model-info

CLIのDefault Profile固定をResolver Hookへ置き換えた。

`model-info`へ次を追加した。

```text
deployment.verification_state
deployment.host
deployment.compute
deployment.backend_runtime
deployment.runtime_requirements
deployment.profile_resolution_source
deployment.runtime_observation
```

実Model／Metalで確認した主要値：

```text
profile_resolution_source         : platform_default
verification_state                : native_verified
host                              : macos／arm64／native
required_capability               : gpu_offload
detected backend                  : llama_cpp 0.3.34
detected build variant source     : declared
executed device                   : gpu
executed acceleration             : metal
executed gpu_offload              : true
artifact_digest_verified          : true
```

Model Rootのユーザー絶対Pathは出力しない既存Policyを維持した。

## 10. 変更File

### Source

```text
M src/margpa_runtime_llm/adapters/model_backends/llama_cpp/adapter.py
A src/margpa_runtime_llm/adapters/model_backends/llama_cpp/runtime_detection.py
M src/margpa_runtime_llm/bootstrap/config_loader.py
M src/margpa_runtime_llm/bootstrap/phase1_application.py
A src/margpa_runtime_llm/bootstrap/profile_resolver.py
M src/margpa_runtime_llm/entrypoints/cli/main.py
M src/margpa_runtime_llm/modules/inference/application/inference_service.py
M src/margpa_runtime_llm/modules/inference/contracts/runtime.py
M src/margpa_runtime_llm/modules/inference/domain/capabilities.py
M src/margpa_runtime_llm/modules/inference/domain/errors.py
M src/margpa_runtime_llm/modules/inference/public.py
```

### Config／Script

```text
M config/models/qwen3_4b_q4_k_m.toml
M config/profiles/local_macos_arm64.toml
M scripts/models/phase1b_runtime_acceptance.py
```

### Test

```text
M tests/contract/model_port/test_model_port_contract.py
M tests/integration/llama_cpp/test_phase1b_runtime.py
M tests/unit/inference/test_cli.py
M tests/unit/inference/test_config_and_registry.py
A tests/unit/inference/test_deployment_platform.py
M tests/unit/inference/test_llama_cpp_boundary.py
```

`pyproject.toml`と`uv.lock`は変更していない。

## 11. Static／Default／Environment Gate

変更前Baseline：

```text
Default pytest : 47 passed, 2 deselected
Ruff           : Pass
mypy --strict  : Pass／48 source files
```

変更後：

```text
bash -n Setup Recipe       : Pass
Ruff Format Check          : Pass／51 files
Ruff Check                 : Pass
mypy --strict              : Pass／51 source files
compileall                 : Pass
Default pytest             : 66 passed, 2 deselected
Environment Verification   : Pass
```

Environment：

```text
Python                    : CPython 3.13.14／arm64／GIL enabled
llama-cpp-python          : 0.3.34
GPU Offload Support       : true
Metal System Info         : present
Dependency Version Match  : true
Out-of-scope Package      : absent
```

Dependency Gate：

```text
uv lock --check           : Pass／117 packages
uv sync --dry-run offline : Pass／115 packages／Would make no changes
```

## 12. 実Model／Metal Regression

```text
pytest -m model_smoke : 2 passed, 66 deselected
```

Production Acceptance：

```text
Success                         : true
Backend                         : llama-cpp-python 0.3.34
Device                          : Metal／GPU
GPU Offload                     : true
Context                         : 4,096
Artifact SHA-512 Verified       : true
Load including SHA-512          : 2.7767 seconds
Generation Result               : フェーズ1-B生産ランタイム成功
Generation Speed                : 25.63 tokens／second
Explicit Stream Terminal State  : cancelled
Post-cancel Generation          : OK／stop
Unload                          : 0.0512 seconds
```

Platform Default Resolver経由の実CLI Generation：

```text
フェーズ1-C成功
```

ModelのDownload、Copy、Rename、変更は行っていない。

## 13. Config／Lock Hash

```text
Model Definition SHA-512:
2a1d3951b56dba2514fd4c37161dbea8048e80efc1ac9a8672f4a7f1f5d2c6aa3e3aaace7216b522dd2c1627fb30d676a80d7a761881f039f2337983d510f4be

Local Mac Profile SHA-512:
a2ccc4525223c6c04c2d91114699d7d850bb8092829b3bdc3ce02698e94ee0c943af789c94b10a3332bf97f245950f263211bf9ed818c5f3ca4c451f57cfd77c

pyproject.toml SHA-256:
a46fcd0b61e8db84a5f90ac4459b92bf9ec9deb7d6219ce88d7b22c240b5ecfa

uv.lock SHA-256:
e5efe33d69105547fe0d4f348b6b189b85f7ed55323f8ecd993ef5df7846fee1
```

新規Dependencyはない。

## 14. Scope外／Verification State

実装していない：

```text
Windows／Linux Profile
PowerShell／Windows Native Setup
Docker
CUDA／ROCm／Vulkan／SYCL Build
MLX／Transformers／vLLM Adapter
Remote API Adapter
Multi-GPU
Response Language Policy
Thinking表示Filter／Parser
Multi-Turn／Web UI／Phase 2
```

Native Verified：

```text
macOS／Apple Silicon arm64／Metal : native_verified
```

その他Platform用のTracked Profileは作成しておらず、`native_verified`とも記録していない。

Response Language／Thinking Output Policy文書は参照のみとし、Source／Configへ反映していない。

## 15. Known Non-blocking Item

- llama.cpp Build VariantはProfile宣言値であり、Native APIから直接観測していない
- Current llama.cpp Device DetectorはMetal／CPUだけを正規化する
- 同一ModelのIdempotent Load判定はModel Key中心
- Native Packageを通常同期でも再BuildするSetup Recipeは重い
- Logical Model／Artifact Variantの全面分離は後続事項
- Runtime Device Name／IDは現在観測できないため`null`
- Response Language／Thinking PresentationはDeferred

## 16. 設計者へのReview依頼

次をReviewしてほしい。

1. Deployment Contractの意味境界
2. Required／Detected／Executed State分離
3. Model RequiredとDeployment RequiredのCapability分離
4. Mac Profile Schema Version 2 Migration
5. Profile Resolver PriorityとUnknown Platform Fail-Closed
6. Runtime Observationの事実性
7. Capability不足時のUnload／Lifecycle
8. CPU概念Profile ContractとMac Metal Required GPUの両立
9. `model-info`のDeployment／Observation構造
10. Static／Default／Metal Regression Evidence
11. Windows／Linux等をVerifiedと誤記していないこと
12. Phase 1-C Acceptance Criteriaの完了判定

Phase 1-C完了はWindows、Linux、CUDA、ROCm、VulkanまたはRemote Runtimeの動作確認を意味しない。

<!-- SOURCE_END 80: docs/handoffs/implementer_status_phase_1c_deployment_platform_acceleration_20260719021411.md -->

---

<!-- SOURCE_BEGIN 81: docs/handoffs/implementer_status_phase_1c_deployment_platform_acceleration_follow_up_20260719025250.md -->

### Source 81: `docs/handoffs/implementer_status_phase_1c_deployment_platform_acceleration_follow_up_20260719025250.md`

- History Target: `docs/project/phases/phase_1/history/handoffs/implementer_status_phase_1c_deployment_platform_acceleration_follow_up_20260719025250.md`
- Source SHA-512: `59a9aefb7cccc2bdc543d7b2ba2773a79e14dbd69a45d44339c84372c405208a5ed3e8d729cc6441165326d92302bc2634ca18c808b8a39792c35be30e7b1bac`
- Source Size: `7129` bytes

# Phase 1-C Deployment／Platform／Acceleration 実装Follow-up状況

- 文書ID: `implementer_status_phase_1c_deployment_platform_acceleration_follow_up`
- 状態: `implementation_complete_review_requested`
- 作成日時: `2026-07-19 02:52:50 JST`
- 更新日時: `2026-07-19 02:52:50 JST`
- 作成担当: 実装者役担当Task
- 対象: 設計者役担当Task
- 正本言語: 日本語
- Documentation Index: [documentation_index_20260719013109.md](../history/documentation_index_20260719013109.md)
- Implementer Handoff: [designer_handoff_phase_1c_deployment_platform_acceleration_20260719013109.md](../history/handoffs/designer_handoff_phase_1c_deployment_platform_acceleration_20260719013109.md)
- Requirements: [phase_1c_deployment_platform_acceleration_requirements_20260719013109.md](../history/requirements/phase_1c_deployment_platform_acceleration_requirements_20260719013109.md)
- Architecture: [phase_1c_deployment_platform_acceleration_architecture_20260719013109.md](../history/architecture/phase_1c_deployment_platform_acceleration_architecture_20260719013109.md)
- Accepted ADR: [adr_0007_deployment_platform_acceleration_abstraction_20260719013109.md](../history/adr/adr_0007_deployment_platform_acceleration_abstraction_20260719013109.md)
- supersedes: [implementer_status_phase_1c_deployment_platform_acceleration_20260719021411.md](../history/handoffs/implementer_status_phase_1c_deployment_platform_acceleration_20260719021411.md)

## 1. 結論

Phase 1-C実装のRequired／Detected／Executed境界を修正した。

旧StatusではModel Load時のDevice観測値を、「当該Requestで実際に使用したDevice／Backend／Offload」である`Executed State`として記録していた。

これはRequest実行前に実行事実を先取りするため、次へ訂正した。

```text
Required State : Deployment Profileが保持
Detected State : Model Load後にBackend Adapterが観測
Executed State : Request単位の実行証拠がある場合のみ保持
```

Model Load直後の`RuntimeObservation`:

```text
detected.device_kind_key       : gpu
detected.acceleration_api_key  : metal
detected.gpu_offload           : true
executed                       : null
```

ADR-0007の「Observation不能値を推測しない」に従う。

## 2. 確認した最新正本

修正時点で`docs/`に配置されている最新Indexは`20260719013109`であり、Phase 1-C実装後のDesigner Reviewは未配置だった。

次を読取専用で再確認した。

- Documentation Index `20260719013109`
- Phase 1-C Requirements `20260719013109`
- Phase 1-C Architecture `20260719013109`
- Phase 1-C Implementer Handoff `20260719013109`
- ADR-0007 `20260719013109`

## 3. 修正内容

### Contract

- `DetectedRuntimeState`へ`gpu_offload`を追加
- `RuntimeObservation.executed`をOptional化
- `ExecutedRuntimeState`はRequest単位のEvidence用Contractとして維持
- Load時のObservation Builderは`executed=None`を生成

### Deployment Validation

次はLoad後のDetected Stateと比較する。

```text
Backend／Version
Compute Kind
Acceleration API
Required Device Kind
Required Acceleration API
Required Capability
```

Request未実行の`Executed State`をDeployment Ready判定に使わない。

### Regression Test

- CPU概念DeploymentでDetected GPU Offloadが`false`、Executedが`null`であること
- Metal Load ObservationがDetected GPU／Metal／Offloadを保持すること
- Load ObservationがRequest Executionを主張しないこと
- CLI `model-info`が`executed: null`を出力すること
- 実Model IntegrationがDetectedとExecutedを分離すること

## 4. 変更File

```text
M src/margpa_runtime_llm/modules/inference/contracts/runtime.py
M src/margpa_runtime_llm/bootstrap/profile_resolver.py
M tests/unit/inference/test_deployment_platform.py
M tests/unit/inference/test_cli.py
M tests/integration/llama_cpp/test_phase1b_runtime.py
A docs/handoffs/implementer_status_phase_1c_deployment_platform_acceleration_follow_up_20260719025250.md
```

Config、`pyproject.toml`、`uv.lock`およびDependencyに変更はない。

## 5. Static／Default／Environment Gate

```text
Ruff Format Check          : Pass／51 files
Ruff Check                 : Pass
mypy --strict              : Pass／47 source files
compileall                 : Pass
bash -n Setup Recipe       : Pass
Default pytest             : 67 passed, 2 deselected
Environment Verification  : Pass
uv lock --check            : Pass／117 packages
uv sync offline dry-run    : Pass／115 packages／Would make no changes
```

Environment:

```text
Python                    : CPython 3.13.14／arm64／GIL enabled
llama-cpp-python          : 0.3.34
GPU Offload Support       : true
Metal System Info         : present
Dependency Version Match  : true
Out-of-scope Package      : absent
```

## 6. 実Model／Metal Regression

Sandbox内ではMetal Context作成が`Failed to create llama_context`で失敗した。同一TestをSandbox外のNative Metal環境で再実行し、通過した。

```text
pytest -m model_smoke : 2 passed, 67 deselected
```

`model-info`実測:

```text
profile_resolution_source         : platform_default
verification_state                : native_verified
detected backend                  : llama_cpp 0.3.34
detected device                   : gpu
detected acceleration             : metal
detected gpu_offload              : true
executed                          : null
artifact_digest_verified          : true
```

Production Acceptance:

```text
Success                         : true
Load including SHA-512          : 2.7010 seconds
Generation Result               : フェーズ1-B生産ランタイム成功
Generation Speed                : 30.19 tokens／second
Explicit Stream Terminal State  : cancelled
Post-cancel Generation          : OK／stop
Unload                          : 0.0428 seconds
```

Generation自体は成功したが、Current ContractにはRequestとExecution Observationを結び付けるTelemetryがない。そのため、Application Load Observationの`executed`はGeneration後も推測で埋めず`null`を維持する。

## 7. 旧Statusの訂正箇所

旧Statusの次の記述は本Follow-upで訂正する。

- Section 3のExecuted実測値
- Section 7のApplication Runtime ObservationにおけるExecuted State
- Section 8のCompute／AccelerationとExecutedの比較
- Section 9のExecuted Device／Acceleration／GPU Offload

正しい記述は「Load時はDetected、Request Executionは未観測」である。

## 8. Scope境界

次は未実装のままである。

- Request単位のExecution Telemetry／Audit
- Windows／Linux実Profile
- CUDA／ROCm／Vulkan等のBackend
- Response Language／Thinking Presentation
- Phase 2以降の機能

macOS／Apple Silicon arm64／Metal以外を`native_verified`とは主張しない。

## 9. 設計者へのReview依頼

次を再Reviewしてほしい。

1. Load時Detected StateとRequest時Executed Stateの意味境界
2. `executed=null`による未観測値の表現
3. Deployment RequirementをDetected Stateで検証する境界
4. `model-info`のObservation事実性
5. Static／Default／Metal Regression Evidence


<!-- SOURCE_END 81: docs/handoffs/implementer_status_phase_1c_deployment_platform_acceleration_follow_up_20260719025250.md -->

---

<!-- SOURCE_BEGIN 82: docs/handoffs/implementer_status_phase_1c_platform_registry_and_preload_validation_follow_up_20260719031938.md -->

### Source 82: `docs/handoffs/implementer_status_phase_1c_platform_registry_and_preload_validation_follow_up_20260719031938.md`

- History Target: `docs/project/phases/phase_1/history/handoffs/implementer_status_phase_1c_platform_registry_and_preload_validation_follow_up_20260719031938.md`
- Source SHA-512: `42baaa87cf68a41caff799bd5f5c3d8207e75b3194fa29bc96bca151d10a711cec2d75be584b7674a7400bbfe98cbda461cd4ab84dccb2947e939c1eaff198cb`
- Source Size: `9428` bytes

# Phase 1-C Platform Registry／Pre-load Validation Follow-up実装状況

- 文書ID: `implementer_status_phase_1c_platform_registry_and_preload_validation_follow_up`
- 状態: `implementation_complete_review_requested`
- 作成日時: `2026-07-19 03:19:38 JST`
- 更新日時: `2026-07-19 03:19:38 JST`
- 作成担当: 実装者役担当Task
- 対象: 設計者役担当Task
- 正本言語: 日本語
- Documentation Index: [documentation_index_20260719030341.md](../history/documentation_index_20260719030341.md)
- Designer Review: [designer_review_phase_1c_deployment_platform_acceleration_follow_up_20260719030341.md](../history/handoffs/designer_review_phase_1c_deployment_platform_acceleration_follow_up_20260719030341.md)
- Requirements: [phase_1c_deployment_platform_acceleration_requirements_20260719013109.md](../history/requirements/phase_1c_deployment_platform_acceleration_requirements_20260719013109.md)
- Architecture: [phase_1c_deployment_platform_acceleration_architecture_20260719013109.md](../history/architecture/phase_1c_deployment_platform_acceleration_architecture_20260719013109.md)
- Accepted ADR: [adr_0007_deployment_platform_acceleration_abstraction_20260719013109.md](../history/adr/adr_0007_deployment_platform_acceleration_abstraction_20260719013109.md)
- supersedes: [implementer_status_phase_1c_deployment_platform_acceleration_follow_up_20260719025250.md](../history/handoffs/implementer_status_phase_1c_deployment_platform_acceleration_follow_up_20260719025250.md)

## 1. 結論

Designer Review `20260719030341`のChanges Requestedを実装した。

```text
Executed State意味境界             : 既存修正を維持
OS／Architecture Alias拡張性     : Pass
Platform Default拡張性              : Pass
Unknown Platform Fail-Closed            : Pass
Profile Resolution Priority             : Pass
Host Pre-load Validation                : Pass
Fallback Pre-load Validation            : Pass
Profile／Model Backend Pre-load Validation: Pass
Host不一致時Model Port Load呼出し       : 0回
Static／Default／Metal Regression       : Pass
Phase 2以降への越境                    : なし
```

Phase 1-Cの実装担当側Acceptanceは全件Passと判定し、最終Designer Reviewを依頼する。

## 2. Platform Registry

新規Tracked Definition:

[platform_registry.toml](../../../../../config/platforms/platform_registry.toml)

Registryは次をSource Code外で保持する。

```text
OS Raw Alias              → Canonical OS Key
Architecture Raw Alias    → Canonical Architecture Key
Execution Environment Key
Host Key                  → Default Profile Path
```

Current Definition:

```text
darwin／macos → macos
windows       → windows
linux         → linux

arm64／aarch64 → arm64
amd64／x86_64 → x86_64

macos／arm64／native
  → config/profiles/local_macos_arm64.toml
```

AliasまたはDefault Profile追加はRegistry Definitionの追加で表現でき、NormalizerまたはApplication CoreのOS別分岐追加を必須としない。

Future OS／Architecture／Default ProfileをRuntimeで組み立て、Source Mapping修正なしで解決できるUnit Testを追加した。

## 3. Registry Validation

Platform Registryは次を検証する。

- TOML Syntax
- Unknown Field拒否
- Alias Raw Valueの正規化
- Canonical Keyの形式
- Alias重複拒否
- Default Host Key重複拒否
- Default Profile Pathの絶対Path／`..`拒否

Unknown OS／ArchitectureをmacOSへ推測しない。

Known AliasでもDefault Profileが存在しない場合は`profile_required`となる。

## 4. Profile Resolution Priority

既存Priorityを維持した。

```text
Explicit Profile
  > MARGPA_PROFILE
  > Platform Registry Default
```

Host DetectionはRegistry Aliasを使用する。未登録AliasはExplicit／Environment Profile指定時もFail-Closedとなるが、新PlatformはRegistry追加で認識可能になる。

## 5. Pre-load／Post-load Validation分離

### Pre-load Validation

Native Adapter生成より前に次を検証する。

```text
Profile Host OS              vs Detected Host OS
Profile Architecture         vs Detected Architecture
Profile Execution Environment vs Detected Execution Environment
Fallback Policy              vs Implemented Policy
Profile Backend／Version     vs Model Definition Backend／Version
```

不一致時はSafe ErrorでFail-Closedとする。

Host不一致Testで次を確認した。

```text
Native Adapter Constructor : 0回
Model Port load()          : 0回
Artifact SHA-512           : 未実行
Native Model Load          : 未実行
Error                      : unsupported_platform
```

### Post-load Validation

Model Load後はDetected Stateを使用し、次だけを検証する。

```text
Detected Backend／Version
Detected Device Kind
Detected Acceleration API
Required Device／Acceleration
Required Capability
```

Capability不足時のUnload／Lifecycle回復を維持した。

## 6. Required／Detected／Executed

前Follow-upで受理された意味境界を維持した。

```text
Required : Deployment Profile
Detected : Load後のBackend Adapter Observation
Executed : Request単位のEvidenceがある場合のみ
```

Current `model-info`:

```text
detected.device_kind_key      : gpu
detected.acceleration_api_key : metal
detected.gpu_offload          : true
executed                      : null
```

## 7. 変更File

### Source／Config

```text
A config/platforms/platform_registry.toml
M src/margpa_runtime_llm/bootstrap/profile_resolver.py
M src/margpa_runtime_llm/bootstrap/phase1_application.py
```

### Test

```text
M tests/unit/inference/test_deployment_platform.py
M tests/unit/inference/test_config_and_registry.py
```

### Handoff

```text
A docs/handoffs/implementer_status_phase_1c_platform_registry_and_preload_validation_follow_up_20260719031938.md
```

`pyproject.toml`、`uv.lock`およびDependencyに変更はない。

## 8. Static／Default／Environment Gate

```text
Ruff Format Check          : Pass／51 files
Ruff Check                 : Pass
mypy --strict              : Pass／51 source files
compileall                 : Pass
bash -n Setup Recipe       : Pass
Default pytest             : 71 passed, 2 deselected
Environment Verification  : Pass
```

Environment:

```text
Python                    : CPython 3.13.14／arm64／GIL enabled
llama-cpp-python          : 0.3.34
GPU Offload Support       : true
Metal System Info         : present
Dependency Version Match  : true
Out-of-scope Package      : absent
```

## 9. Dependency Gate

Lock Check:

```text
uv lock --check
```

Result:

```text
Resolved 117 packages
```

Setup Recipeと同一OptionのOffline Dry-run:

```text
uv sync --dry-run --frozen --offline \
  --extra inference-llama \
  --group dev \
  --group notebook \
  --no-binary-package llama-cpp-python
```

Result:

```text
Checked 115 packages
Would make no changes
```

## 10. Native Metal Regression

Sandbox外のNative Metal環境で実行した。

```text
.venv/bin/pytest -q -m model_smoke
  2 passed, 71 deselected
```

`model-info`:

```text
profile_resolution_source : platform_default
verification_state        : native_verified
backend                    : llama_cpp 0.3.34
device                     : gpu／metal
gpu_offload                : true
executed                   : null
artifact_digest_verified   : true
```

Production Acceptance:

```text
Success                         : true
Load including SHA-512          : 2.5733 seconds
Generation Result               : フェーズ1-B生産ランタイム成功
Generation Speed                : 30.78 tokens／second
Explicit Stream Terminal State  : cancelled
Post-cancel Generation          : OK／stop
Unload                          : 0.0506 seconds
Detected Device                 : gpu／metal
Detected GPU Offload            : true
Executed State                  : null
```

## 11. Config／Lock Hash

```text
Platform Registry SHA-512:
5af43fff30e5cf0716a927e05d1bde74a443e5a0484490a32398421824e3b4cc0539f64578dcc509fe620790686d7473587d7650665f2436b4c988281712d574

Model Definition SHA-512:
2a1d3951b56dba2514fd4c37161dbea8048e80efc1ac9a8672f4a7f1f5d2c6aa3e3aaace7216b522dd2c1627fb30d676a80d7a761881f039f2337983d510f4be

Local Mac Profile SHA-512:
a2ccc4525223c6c04c2d91114699d7d850bb8092829b3bdc3ce02698e94ee0c943af789c94b10a3332bf97f245950f263211bf9ed818c5f3ca4c451f57cfd77c

pyproject.toml SHA-256:
a46fcd0b61e8db84a5f90ac4459b92bf9ec9deb7d6219ce88d7b22c240b5ecfa

uv.lock SHA-256:
e5efe33d69105547fe0d4f348b6b189b85f7ed55323f8ecd993ef5df7846fee1
```

## 12. Verification State／Scope

Native Verified:

```text
macOS／Apple Silicon arm64／Metal : native_verified
```

Windows／Linux AliasはRegistryに定義したが、Default ProfileとNative Verificationは追加していない。

未実装:

- Windows／Linux実Profile
- CUDA／ROCm／Vulkan／MLX／Remote Backend
- Request単位のExecution Telemetry
- Response Language／Thinking Presentation
- Phase 2以降の機能

## 13. 設計者へのReview依頼

次の最終Reviewを依頼する。

1. OS／Architecture AliasのDefinition境界
2. Platform Default ProfileのRegistry境界
3. Unknown Platform Fail-Closed
4. Explicit／Environment／Platform Default Priority
5. Host／Fallback／Backend Pre-load Validation
6. Host不一致時にAdapter／Model Port Loadが呼ばれないこと
7. Post-load Detected Capability Validation
8. Current Mac／Metal Regression
9. Phase 1-C Acceptance Criteria 6の完了判定


<!-- SOURCE_END 82: docs/handoffs/implementer_status_phase_1c_platform_registry_and_preload_validation_follow_up_20260719031938.md -->

---

<!-- SOURCE_BEGIN 83: docs/handoffs/implementer_status_phase_1c_platform_registry_reference_integrity_follow_up_20260719034523.md -->

### Source 83: `docs/handoffs/implementer_status_phase_1c_platform_registry_reference_integrity_follow_up_20260719034523.md`

- History Target: `docs/project/phases/phase_1/history/handoffs/implementer_status_phase_1c_platform_registry_reference_integrity_follow_up_20260719034523.md`
- Source SHA-512: `2509e98a7f45db4d07caf0da228d1cd8e17f2155c7d6b4af43601c8eb2a35f91b590aedc9f031742ab602d7b820e510b2eb2fdafe17786827b1b8dcc11beb14d`
- Source Size: `6997` bytes

# Phase 1-C Platform Registry参照整合 Follow-up実装状況

- 文書ID: `implementer_status_phase_1c_platform_registry_reference_integrity_follow_up`
- 状態: `implementation_complete_review_requested`
- 作成日時: `2026-07-19 03:45:23 JST`
- 更新日時: `2026-07-19 03:45:23 JST`
- 作成担当: 実装者役担当Task
- 対象: 設計者役担当Task
- 正本言語: 日本語
- Documentation Index: [documentation_index_20260719033038.md](../history/documentation_index_20260719033038.md)
- Designer Review: [designer_review_phase_1c_platform_registry_and_preload_validation_follow_up_20260719033038.md](../history/handoffs/designer_review_phase_1c_platform_registry_and_preload_validation_follow_up_20260719033038.md)
- Requirements: [phase_1c_deployment_platform_acceleration_requirements_20260719013109.md](../history/requirements/phase_1c_deployment_platform_acceleration_requirements_20260719013109.md)
- Architecture: [phase_1c_deployment_platform_acceleration_architecture_20260719013109.md](../history/architecture/phase_1c_deployment_platform_acceleration_architecture_20260719013109.md)
- Accepted ADR: [adr_0007_deployment_platform_acceleration_abstraction_20260719013109.md](../history/adr/adr_0007_deployment_platform_acceleration_abstraction_20260719013109.md)
- supersedes: [implementer_status_phase_1c_platform_registry_and_preload_validation_follow_up_20260719031938.md](../history/handoffs/implementer_status_phase_1c_platform_registry_and_preload_validation_follow_up_20260719031938.md)

## 1. 結論

Designer Review `20260719033038`で要求されたPlatform Registry参照整合Validationを実装した。

```text
OS Alias集合の非空Validation                    : Pass
Architecture Alias集合の非空Validation          : Pass
Default OS Canonical参照整合                   : Pass
Default Architecture Canonical参照整合         : Pass
Default Execution Environment参照整合          : Pass
Loader Safe Error Mapping                         : Pass
Current Registry／Future Alias／Unknown Fail-Closed    : Pass
Pre-load Validation                               : Pass
Static／Default／Metal Regression                   : Pass
```

Phase 1-Cの実装担当側Acceptance Criteriaは全件Passと判定し、最終Designer Reviewを依頼する。

## 2. 参照整合Validation

`PlatformRegistry`のPydantic Model Validationへ次を追加した。

1. `operating_system_aliases`が1件以上存在する
2. `architecture_aliases`が1件以上存在する
3. 各Defaultの`operating_system_key`がOS AliasのCanonical Key集合に存在する
4. 各Defaultの`architecture_key`がArchitecture AliasのCanonical Key集合に存在する
5. 各Defaultの`execution_environment_key`がRegistryの検出値と一致する

従来受理されていた次の参照は、Registry Load時に拒否される。

```text
macso／arm64／native
macos／arm65／native
macos／arm64／container
```

設定不備は後段の`profile_required`ではなく、Loader境界でSafeな`invalid_configuration`へ変換される。

## 3. Negative Test

追加したTest:

- OS Canonical参照不整合を拒否
- Architecture Canonical参照不整合を拒否
- Execution Environment参照不整合を拒否
- OS Alias空集合を拒否
- Architecture Alias空集合を拒否
- File Loaderが参照不整合をSafeな`invalid_configuration`へ変換

維持したTest:

- Current `platform_registry.toml` Parse
- Future OS／Architecture AliasとDefault Profile追加
- Unknown Platform Fail-Closed
- Explicit／Environment／Platform Default Priority
- Host／Fallback／Backend Pre-load Validation
- Host不一致時のAdapter／Model Port未呼出

## 4. 変更File

```text
M src/margpa_runtime_llm/bootstrap/profile_resolver.py
M tests/unit/inference/test_config_and_registry.py
A docs/handoffs/implementer_status_phase_1c_platform_registry_reference_integrity_follow_up_20260719034523.md
```

`config/platforms/platform_registry.toml`、`pyproject.toml`、`uv.lock`およびDependencyに変更はない。

## 5. Static／Default／Environment Gate

```text
Ruff Format Check          : Pass／51 files
Ruff Check                 : Pass
mypy --strict              : Pass／51 source files
compileall                 : Pass
bash -n Setup Recipe       : Pass
Default pytest             : 77 passed, 2 deselected
Environment Verification  : Pass
```

Environment:

```text
Python                    : CPython 3.13.14／arm64／GIL enabled
llama-cpp-python          : 0.3.34
GPU Offload Support       : true
Metal System Info         : present
Dependency Version Match  : true
Out-of-scope Package      : absent
```

## 6. Dependency Gate

```text
uv lock --check
  Resolved 117 packages

uv sync --dry-run --frozen --offline \
  --extra inference-llama \
  --group dev \
  --group notebook \
  --no-binary-package llama-cpp-python

  Checked 115 packages
  Would make no changes
```

## 7. Native Metal Regression

Sandbox外のNative Metal環境で実行した。

```text
.venv/bin/pytest -q -m model_smoke
  2 passed, 77 deselected
```

`model-info`:

```text
profile_resolution_source : platform_default
verification_state        : native_verified
backend                    : llama_cpp 0.3.34
device                     : gpu／metal
gpu_offload                : true
executed                   : null
artifact_digest_verified   : true
```

Production Acceptance:

```text
Success                         : true
Load including SHA-512          : 2.5619 seconds
Generation Result               : フェーズ1-B生産ランタイム成功
Generation Speed                : 29.86 tokens／second
Explicit Stream Terminal State  : cancelled
Post-cancel Generation          : OK／stop
Unload                          : 0.0703 seconds
Detected Device                 : gpu／metal
Detected GPU Offload            : true
Executed State                  : null
```

## 8. Hash／Dependency不変

```text
Platform Registry SHA-512:
5af43fff30e5cf0716a927e05d1bde74a443e5a0484490a32398421824e3b4cc0539f64578dcc509fe620790686d7473587d7650665f2436b4c988281712d574

pyproject.toml SHA-256:
a46fcd0b61e8db84a5f90ac4459b92bf9ec9deb7d6219ce88d7b22c240b5ecfa

uv.lock SHA-256:
e5efe33d69105547fe0d4f348b6b189b85f7ed55323f8ecd993ef5df7846fee1
```

## 9. Scope境界

未実装のままである。

- Windows／Linux実Profile
- CUDA／ROCm／Vulkan／MLX／Remote Backend
- 複数Execution Environment Alias／Detector
- Request単位のExecution Telemetry
- Response Language／Thinking Presentation
- Phase 2以降の機能

Native VerifiedはCurrent macOS／Apple Silicon arm64／Metalのみである。

## 10. 設計者への最終Review依頼

次を確認し、Phase 1-Cの最終受入を判定してほしい。

1. Alias集合の非空Validation
2. Default OS／Architecture Canonical参照整合
3. Default Execution Environment参照整合
4. LoaderのSafe Error Mapping
5. Current Registry／Future Alias／Unknown Fail-Closed Regression
6. Pre-load／Post-load Validation Regression
7. Static／Default／Native Metal Gate


<!-- SOURCE_END 83: docs/handoffs/implementer_status_phase_1c_platform_registry_reference_integrity_follow_up_20260719034523.md -->

---

<!-- SOURCE_BEGIN 84: docs/handoffs/implementer_status_phase_1d_configuration_and_response_language_20260719095111.md -->

### Source 84: `docs/handoffs/implementer_status_phase_1d_configuration_and_response_language_20260719095111.md`

- History Target: `docs/project/phases/phase_1/history/handoffs/implementer_status_phase_1d_configuration_and_response_language_20260719095111.md`
- Source SHA-512: `f1fc93d86920d8de4a859ece14b12938d675e21acfc7755a1c5363991e5d53c03f00e2b7d491235cc56221a96dcbde38211047ff028356b6253a58d81a5b66e6`
- Source Size: `13292` bytes

# Phase 1-D Configuration Layer分離／Response Language実装状況

- 文書ID: `implementer_status_phase_1d_configuration_and_response_language`
- 状態: `implementation_complete_review_requested`
- 作成日時: `2026-07-19 09:51:11 JST`
- 更新日時: `2026-07-19 09:51:11 JST`
- 作成担当: 実装者役担当Task
- 対象: 設計者役担当Task
- 正本言語: 日本語
- Documentation Index: [documentation_index_20260719041847.md](../history/documentation_index_20260719041847.md)
- Implementer Handoff: [designer_handoff_phase_1d_response_language_20260719041847.md](../history/handoffs/designer_handoff_phase_1d_response_language_20260719041847.md)
- Configuration Requirements: [configuration_layer_requirements_20260719041847.md](../history/requirements/configuration_layer_requirements_20260719041847.md)
- Configuration Architecture: [configuration_layer_architecture_20260719041847.md](../history/architecture/configuration_layer_architecture_20260719041847.md)
- Response Language Requirements: [phase_1d_response_language_requirements_20260719041847.md](../history/requirements/phase_1d_response_language_requirements_20260719041847.md)
- Response Language Architecture: [phase_1d_response_language_architecture_20260719041847.md](../history/architecture/phase_1d_response_language_architecture_20260719041847.md)
- Accepted ADR-0009: [adr_0009_application_deployment_configuration_separation_20260719041847.md](../history/adr/adr_0009_application_deployment_configuration_separation_20260719041847.md)
- Accepted ADR-0008: [adr_0008_response_language_policy_20260719040237.md](../history/adr/adr_0008_response_language_policy_20260719040237.md)
- Phase 1-C Final Review: [designer_review_phase_1c_final_20260719035156.md](../history/handoffs/designer_review_phase_1c_final_20260719035156.md)
- supersedes: なし（Phase 1-D初回Status）

## 1. 結論

Phase 1-DのStep A「Application Config／Deployment Profile分離」とStep B「Response Language `ja／en／auto`」を実装した。

```text
Application Config Schema 1／Strict Validation       : Pass
Deployment Profile Schema 3／Strict Validation       : Pass
Typed Section Composition／Field別Precedence          : Pass
Context Limit Pre-load Rejection                      : Pass
Response Contract／Resolver／Composer                  : Pass
Default ja／Explicit en／auto Native Smoke             : Pass
User Prompt／User System Message保持                  : Pass
Adapter Language Logicなし                            : Pass
Phase 1-E Scope混入なし                               : Pass
Static／Default／Environment／Lock／Native Metal Gate : Pass
```

Phase 1-Dの実装担当側Acceptance Criteriaは全件Passと判定し、Designer Reviewを依頼する。

## 2. Configuration所有権の分離

### 2.1 Before／After

| 設定領域 | Before: Deployment Profile Schema 2 | After |
|---|---|---|
| Application Key | なし | Application Config Schema 1 |
| Selected Model | Deployment Profile | Application Config |
| Model Root | Deployment Profile | Application Config |
| Common Load Default | Deployment Profile | Application Config |
| Platform Load Override | Deployment Profile | Deployment Profile Schema 3 |
| Generation | Deployment Profile | Application Config |
| Response Language | なし | Application Config |
| Platform／Backend／Runtime／Hardware | Deployment Profile | Deployment Profile Schema 3 |

`config/application.toml`を共通Application設定の正本として追加した。`config/profiles/local_macos_arm64.toml`はPlatform固有値だけを保持するSchema `3`へMigrationした。

Generic Deep Mergeは導入していない。Load、Generation、Response、Model／Root、Profileを型付きSection単位で合成する。

### 2.2 Effective Configの維持

Migration前後で、既存Runtimeへ渡す実効値を維持した。

```text
selected_model       : main.qwen3-4b-q4-k-m
model_root           : ./models
context_size         : 4096
batch_size           : 256
micro_batch_size     : 256
threads              : 6
threads_batch        : 6
gpu_layers           : -1
use_mmap             : true
use_mlock             : false
verbose_backend      : false
verify_artifact_hash : true
max_new_tokens       : 512
temperature          : 0.7
top_p                : 0.8
top_k                : 20
min_p                : 0.0
presence_penalty     : 1.5
frequency_penalty    : 0.0
repeat_penalty       : 1.0
thinking_mode        : disabled
```

新規の実効値は次である。

```text
application_key : default
response        : ja／source=application
```

### 2.3 Precedence

```text
Response Language : Explicit > MARGPA_RESPONSE_LANGUAGE > Application > Built-in
Load Field        : Explicit > Environment > Deployment Override > Application > Built-in
Model／Root       : Explicit > Environment > Application
Profile           : Explicit > Environment > Platform Default
```

Field別Precedence、Strict Unknown Field拒否、旧Schema `2`拒否、Application／Deployment所有権違反、Unsafe Model Root、Model／Backend不整合をUnit Test化した。

Applicationの`context_size`がModel Native Limitを超える場合は、Adapter ConstructionおよびModel Loadより前にSafeな`invalid_configuration`として拒否する。

## 3. Response Language

### 3.1 Contract／Resolver

次のContractを追加した。

```text
ResponseLanguage       : ja／en／auto
ResponseLanguageSource : built_in_default／application／environment／explicit
ResponsePolicyConfig
ResolvedResponseLanguagePolicy
```

未定義値、`jp`、不正な環境変数値はFail-Closedし、Safeな`invalid_configuration`へ変換される。

### 3.2 Message Composer

Application Orchestration LayerにAdapter非依存のComposerを追加した。

```text
ja:
回答は原則として日本語で行ってください。
ユーザーが回答言語を明示的に指定した場合は、その指定を優先してください。

en:
Respond in English by default.
If the user explicitly requests a different response language, follow that request.

auto:
言語System Instructionを注入しない
```

`ja／en／auto × User System Message有／無`の6組合せをExact Testした。User PromptはByte-for-byteで保持し、User System Messageがある場合は1件の決定的なSystem Messageへ結合する。

Streaming／Non-streamingは同じComposer結果を使用する。Model AdapterにはResponse Language分岐または言語指示を追加していない。

### 3.3 CLI／model-info

CLIへ次を追加した。

```text
--response-language {ja,en,auto}
```

`model-info`は次を表示する。

```text
application_key           : default
profile_key               : local.macos-arm64
selected_model            : main.qwen3-4b-q4-k-m
response.language         : ja
response.source           : application
applied_sources           : built_in_defaults／application／deployment_profile
profile_resolution_source : platform_default
verification_state        : native_verified
device                    : gpu／metal
gpu_offload               : true
executed                  : null
```

## 4. 変更File

```text
A config/application.toml
M config/profiles/local_macos_arm64.toml

M src/margpa_runtime_llm/bootstrap/config_loader.py
M src/margpa_runtime_llm/bootstrap/phase1_application.py
A src/margpa_runtime_llm/modules/inference/contracts/response.py
M src/margpa_runtime_llm/modules/inference/public.py
A src/margpa_runtime_llm/orchestration/response_language.py
M src/margpa_runtime_llm/entrypoints/cli/main.py

M scripts/models/phase1b_runtime_acceptance.py

M tests/unit/inference/test_config_and_registry.py
M tests/unit/inference/test_deployment_platform.py
M tests/unit/inference/test_cli.py
A tests/unit/inference/test_response_language.py
M tests/integration/llama_cpp/test_phase1b_runtime.py

A docs/handoffs/implementer_status_phase_1d_configuration_and_response_language_20260719095111.md
```

`pyproject.toml`、`uv.lock`、Model Definition、Platform Registryに変更はない。

## 5. Resolver／Composer Test Evidence

```text
Built-in Default < Application < Environment < Explicit : Pass
ja without User System                                   : Pass／Exact
ja with User System                                      : Pass／Exact
en without User System                                   : Pass／Exact
en with User System                                      : Pass／Exact
auto without User System                                 : Pass／No injection
auto with User System                                    : Pass／User System only
User Prompt preservation                                 : Pass／Exact
Streaming／Non-streaming message parity                  : Pass
Invalid jp／Invalid Environment                          : Pass／Fail-Closed
```

## 6. Static／Default／Environment Gate

```text
Ruff Format Check          : Pass／54 files
Ruff Check                 : Pass
mypy --strict              : Pass／54 source files
compileall                 : Pass
bash -n Setup Recipe       : Pass
Default pytest             : 94 passed, 2 deselected
Environment Verification  : Pass
```

Environment:

```text
Python                    : CPython 3.13.14／arm64／GIL enabled
llama-cpp-python          : 0.3.34
GPU Offload Support       : true
Metal System Info         : present
Dependency Version Match  : true
Out-of-scope Package      : absent
```

## 7. Dependency Gate

```text
uv lock --check
  Resolved 117 packages

uv sync --dry-run --frozen --offline \
  --extra inference-llama \
  --group dev \
  --group notebook \
  --no-binary-package llama-cpp-python

  Checked 115 packages
  Would make no changes
```

Source変更後のProject Package自身だけを同じLock固定／Offline条件で`.venv`へ再同期した。外部Package、`pyproject.toml`、`uv.lock`の変更はない。

## 8. Native Metal／Language Smoke

Sandbox外のNative macOS／Apple Silicon arm64／Metal環境で実行した。

```text
.venv/bin/pytest -q -m model_smoke
  2 passed, 94 deselected
```

Real CLI:

```text
Default ja:
  Prompt : 「成功」とだけ答えてください。
  Result : 成功

Explicit en:
  Prompt : Reply with the single word success.
  Result : success

auto:
  Prompt : OKとだけ答えてください。
  Result : OK
```

Production Acceptance:

```text
Success                         : true
Load including SHA-512          : 2.4434 seconds
Generation Result               : フェーズ1-B生産ランタイム成功
Generation Speed                : 27.85 tokens／second
Explicit Stream Terminal State  : cancelled
Post-cancel Generation          : OK／stop
Unload                          : 0.0486 seconds
Detected Device                 : gpu／metal
Detected GPU Offload            : true
Artifact Digest Verified        : true
Response                        : ja／source=application
Executed State                  : null
```

## 9. Hash／Dependency不変

```text
Application Config SHA-512:
1f38d7f0ed5ed1157cac76ad63f14fd57f0fa688448180c37c5c01abd6f046db27edaed25dfab8c72dca3324f9a1a930579efdcb503c74bc5ef60bbc20f1f83b

Mac Deployment Profile SHA-512:
861aa54e159285a5445df853b260b2465194a93bc2c254d3cfd9ec4b58c4fc6c1af0dd1ba7d80251a5e46f9c886fe2205d7931b346709002edb2e7d9f9ce2b40

Model Definition SHA-512:
2a1d3951b56dba2514fd4c37161dbea8048e80efc1ac9a8672f4a7f1f5d2c6aa3e3aaace7216b522dd2c1627fb30d676a80d7a761881f039f2337983d510f4be

Platform Registry SHA-512:
5af43fff30e5cf0716a927e05d1bde74a443e5a0484490a32398421824e3b4cc0539f64578dcc509fe620790686d7473587d7650665f2436b4c988281712d574

pyproject.toml SHA-256:
a46fcd0b61e8db84a5f90ac4459b92bf9ec9deb7d6219ce88d7b22c240b5ecfa

uv.lock SHA-256:
e5efe33d69105547fe0d4f348b6b189b85f7ed55323f8ecd993ef5df7846fee1
```

Model Definition、Platform Registry、`pyproject.toml`、`uv.lock`のHashはPhase 1-C Final時点から不変である。新規外部Dependencyはない。

## 10. Scope境界／Known Non-blocking Item

Phase 1-DのResponse LanguageはSystem Instruction Policyであり、生成結果をClassifierまたはTranslationで強制する機能ではない。`auto`は言語を推定せず、言語System Instructionを注入しない。

次は未実装のままである。

- Thinking Content抽出／非表示／表示切替などPhase 1-EのThinking Presentation
- Output Language Classifier／Translation
- Multiple Application Config Selector
- Generation／Response Preset Directory
- Dynamic Reload／Remote Config
- Windows／Linux実Profile
- Web UI／API
- Guard／Judge／Governance実行
- Phase 2以降の機能

既存のQwen3 Thinking Mode制御と`thinking_mode=disabled`はPhase 1-BからのRuntime Contractであり、Phase 1-EのPresentation処理は追加していない。

## 11. 設計者へのReview依頼

次を確認し、Phase 1-Dの受入を判定してほしい。

1. Application Config Schema `1`／Deployment Profile Schema `3`の所有権分離
2. Typed Section CompositionとField別Precedence
3. Migration前後のEffective Config同値性
4. Context LimitのPre-load拒否
5. Response Contract／Resolver／Composer
6. `ja／en／auto`とUser Message保持
7. CLI／`model-info`のEffective Source表示
8. Adapter Language Logicなし／Phase 1-E Scope混入なし
9. Static／Default／Environment／Lock／Native Metal Gate


<!-- SOURCE_END 84: docs/handoffs/implementer_status_phase_1d_configuration_and_response_language_20260719095111.md -->

---

<!-- SOURCE_BEGIN 85: docs/handoffs/implementer_status_phase_1e_thinking_presentation_20260719134914.md -->

### Source 85: `docs/handoffs/implementer_status_phase_1e_thinking_presentation_20260719134914.md`

- History Target: `docs/project/phases/phase_1/history/handoffs/implementer_status_phase_1e_thinking_presentation_20260719134914.md`
- Source SHA-512: `390a1370a93e08ea6d91c74fc84d385bbe71e209b1e28c9b6c90947d3f18fc78c670a812c2bdb68c083e54d0e36210adbf3baa5939d1e46dd6acd1c1ff9cc330`
- Source Size: `18577` bytes

# Phase 1-E Thinking Presentation実装状況

- 文書ID: `implementer_status_phase_1e_thinking_presentation`
- 状態: `implementation_complete_review_requested`
- 作成日時: `2026-07-19 13:49:14 JST`
- 更新日時: `2026-07-19 13:49:14 JST`
- 作成担当: 実装者役担当Task
- 対象: 設計者役担当Task
- 正本言語: 日本語
- Documentation Index: [documentation_index_20260719130303.md](../history/documentation_index_20260719130303.md)
- Implementer Handoff: [designer_handoff_phase_1e_thinking_presentation_20260719130303.md](../history/handoffs/designer_handoff_phase_1e_thinking_presentation_20260719130303.md)
- Requirements: [phase_1e_thinking_presentation_requirements_20260719130303.md](../history/requirements/phase_1e_thinking_presentation_requirements_20260719130303.md)
- Architecture: [phase_1e_thinking_presentation_architecture_20260719130303.md](../history/architecture/phase_1e_thinking_presentation_architecture_20260719130303.md)
- Accepted ADR: [adr_0014_thinking_execution_presentation_and_persistence_separation_20260719130303.md](../history/adr/adr_0014_thinking_execution_presentation_and_persistence_separation_20260719130303.md)
- Previous Phase Final Review: [designer_review_phase_1d_final_20260719122035.md](../history/handoffs/designer_review_phase_1d_final_20260719122035.md)
- supersedes: なし（Phase 1-E初回Status）

## 1. 結論

Phase 1-EのThinking Execution／Protocol Parsing／Presentation／Persistence分離を実装した。

```text
Application Config Schema 2                   : Pass
Model Definition Schema 2                    : Pass
Deployment Profile Schema 3不変              : Pass
Model-declared Parser Registry                : Pass
Stateful Streaming／Delimiter Split           : Pass
Hidden No-flash                              : Pass
Visible Default Label「高度推論」             : Pass
Visible Custom Label                         : Pass
Raw Model Port Contract不変                   : Pass
Raw Reasoning Persistenceなし                 : Pass
Sampling暗黙切替なし                          : Pass
Static／Default／Lock／Native Metal Gate      : Pass
Acceptance Criteria                          : 22／22 Pass
```

実装担当側のCompletion Boundaryは成立したと判定し、Designer Reviewを依頼する。

## 2. Implementation Summary

Raw Model Outputの後段へ独立Presentation Moduleを追加した。

```text
Generation Config
  └─ Thinking Execution
           ↓
      Model Port／Backend Adapter
           ↓ Raw GenerationResult／GenerationChunk
Model Definition Schema 2
  └─ output_protocol.thinking
           ↓
      Parser Registry
           ↓
 Tagged Stateful Parser
           ↓ Reasoning／Final Segment
Resolved Presentation Policy
           ↓
      Renderer／Presentation Service
           ↓
      CLI Display
```

Model Port、Inference Service、llama.cpp AdapterはRaw Textを返す既存Contractのままである。CLIのNon-streaming／Streamingだけが後段Presentation Serviceを利用する。

## 3. Schema Migration

### 3.1 Application Config

`config/application.toml`をSchema `1`から`2`へMigrationした。

```toml
schema_version = "2"

[presentation.thinking]
visibility = "hidden"
display_label = "高度推論"
persistence = "disabled"
```

既存のModel選択、Model Root、Load、Generation、Response値は維持した。

Default：

```text
thinking_mode : disabled
visibility    : hidden
display_label : 高度推論
persistence   : disabled
```

### 3.2 Model Definition

`config/models/qwen3_4b_q4_k_m.toml`をSchema `1`から`2`へMigrationした。

```toml
schema_version = "2"

[output_protocol.thinking]
parser_key = "tagged_thinking_v1"
opening_delimiter = "<think>"
closing_delimiter = "</think>"
```

Model Artifact Path、Size、SHA-512、Backend、Capability、Native Context Limitは変更していない。Definition File SHA-512だけがSchema Migrationにより更新された。

### 3.3 不変領域

```text
Deployment Profile Schema : 3 unchanged
Platform Registry          : unchanged
Model Artifact             : unchanged
pyproject.toml              : unchanged
uv.lock                     : unchanged
External Dependency        : none added
```

## 4. Parser／Renderer Structure

### 4.1 Contract／Port

追加した主要Contract：

```text
ThinkingVisibility
ThinkingPersistence
ThinkingPresentationSource
ThinkingPresentationConfig
ResolvedThinkingPresentationPolicy
ThinkingContentKind
ThinkingParseStatus
ThinkingSegmentDelta
ThinkingParseWarning
ThinkingParseSummary
NormalizedThinkingOutput
PresentedThinkingOutput
```

Parser PortはSession単位で`feed`と`finish`を提供する。Raw Result／Chunkを書き換えず、Reasoning／Final SegmentとParse Summaryを返す。

### 4.2 Parser Registry

```text
plain_text_v1       → PlainTextOutputParser
tagged_thinking_v1  → TaggedThinkingOutputParser
unknown             → invalid_model_definition
```

Parser選択にModel Key、Architecture、Backend名の分岐はない。Unknown ParserはNative Adapter Construction／Model Loadより前に拒否する。

### 4.3 Stateful Tagged Parser

```text
detecting_prefix
  ├─ opening complete → inside_reasoning
  ├─ mismatch         → plain_text
  └─ terminal partial → plain_text

inside_reasoning
  ├─ closing complete → after_reasoning
  └─ terminal          → unclosed_reasoning

after_reasoning
  └─ remaining text    → final
```

- Optional Leading Whitespace＋Leading OpeningだけをProtocol認識
- Opening／Closing Delimiterの全Chunk Splitに対応
- Delimiterと一致し得る最小SuffixだけをBuffer
- 1文字Chunk／Empty Deltaに対応
- Extra Delimiterを削除せず`malformed_protocol`＋Warning
- Unclosed ReasoningはHiddenで非表示、VisibleでDisplay Closing Tag補完

### 4.4 Renderer／Service

RendererはCanonical Delimiterを知らず、Normalized SegmentとResolved Display Labelだけを扱う。

```text
Hidden:
  REASONING → 表示しない
  FINAL     → そのまま表示

Visible:
  REASONING → <高度推論>...</高度推論>
  FINAL     → そのまま表示
```

Non-streamingとStreamingは同じParser State Machine／Rendererを使用する。

## 5. Config／Environment／CLI Precedence

### 5.1 Visibility

```text
CLI Explicit
  > MARGPA_THINKING_VISIBILITY
  > Application Config
  > Built-in hidden
```

### 5.2 Display Label

```text
CLI Explicit
  > MARGPA_THINKING_LABEL
  > Application Config
  > Built-in 高度推論
```

### 5.3 Persistence

```text
Application Config
  > Built-in disabled
```

`MARGPA_THINKING_PERSISTENCE`、Persistence CLI Overrideは実装していない。

Field別Source：

```text
visibility_source
display_label_source
persistence_source
```

CLI：

```text
Execution:
  --thinking
  --no-thinking

Presentation:
  --show-thinking
  --hide-thinking
  --thinking-label
```

`--show-thinking／--hide-thinking`はMutually Exclusiveである。`--show-thinking`はExecutionをONにせず、`--thinking`はVisibilityをVisibleにしない。

## 6. Changed／Added Files

```text
M config/application.toml
M config/models/qwen3_4b_q4_k_m.toml

A src/margpa_runtime_llm/adapters/output_protocols/__init__.py
A src/margpa_runtime_llm/adapters/output_protocols/plain_text.py
A src/margpa_runtime_llm/adapters/output_protocols/tagged_thinking.py
M src/margpa_runtime_llm/bootstrap/config_loader.py
A src/margpa_runtime_llm/bootstrap/output_parser_registry.py
M src/margpa_runtime_llm/bootstrap/phase1_application.py
M src/margpa_runtime_llm/entrypoints/cli/main.py
M src/margpa_runtime_llm/modules/inference/domain/model_definition.py
M src/margpa_runtime_llm/modules/inference/public.py
A src/margpa_runtime_llm/modules/presentation/__init__.py
A src/margpa_runtime_llm/modules/presentation/public.py
A src/margpa_runtime_llm/modules/presentation/contracts/__init__.py
A src/margpa_runtime_llm/modules/presentation/contracts/thinking.py
A src/margpa_runtime_llm/modules/presentation/ports/__init__.py
A src/margpa_runtime_llm/modules/presentation/ports/thinking_output_parser.py
A src/margpa_runtime_llm/modules/presentation/application/__init__.py
A src/margpa_runtime_llm/modules/presentation/application/thinking_presentation_service.py
A src/margpa_runtime_llm/orchestration/thinking_presentation.py

M tests/contract/model_port/test_model_port_contract.py
M tests/integration/llama_cpp/test_phase1b_runtime.py
M tests/unit/inference/test_cli.py
M tests/unit/inference/test_config_and_registry.py
M tests/unit/inference/test_deployment_platform.py
A tests/unit/presentation/test_thinking_presentation.py

A docs/handoffs/implementer_status_phase_1e_thinking_presentation_20260719134914.md
```

次は変更していない。

```text
src/margpa_runtime_llm/modules/inference/ports/model_port.py
src/margpa_runtime_llm/adapters/model_backends/llama_cpp/adapter.py
src/margpa_runtime_llm/adapters/model_backends/llama_cpp/stream.py
config/profiles/local_macos_arm64.toml
config/platforms/platform_registry.toml
scripts/
pyproject.toml
uv.lock
```

## 7. Deterministic Test Evidence

```text
Application Schema 2／Old Schema拒否                 : Pass
Model Definition Schema 2／Old Schema拒否            : Pass
Default hidden／高度推論／disabled                    : Pass
Field Ownership／Precedence／Source                  : Pass
Invalid Visibility／Label／Persistence               : Pass
Plain／Tagged／Unknown Parser                        : Pass
Invalid／Equal／Control-character Delimiter          : Pass
Model Key／Architecture非依存                        : Pass
Plain／Complete／Unclosed／Malformed                 : Pass
Hidden／Visible／Default／Custom Label               : Pass
Opening／Closingを含む全Single Split Position        : Pass
1文字Chunk／Empty Delta                              : Pass
Hidden No-flash                                     : Pass
Streaming／Non-streaming Parity                      : Pass
Raw GenerationResult／GenerationChunk不変            : Pass
Execution／Visibility独立                            : Pass
Sampling Parameter非連動                            : Pass
CLI Flag Exclusivity／Safe Error                     : Pass
Unknown Parser Pre-load Rejection                    : Pass
Cancel／Close／Usage／Finish Regression              : Pass
Phase 1-D ja／en／auto Regression                    : Pass
```

## 8. Static／Default／Environment／Lock Gate

```text
Ruff Format Check          : Pass／68 files
Ruff Check                 : Pass
mypy --strict              : Pass／68 source files
compileall                 : Pass
bash -n Setup Recipe       : Pass
Default pytest             : 161 passed, 2 deselected
Environment Verification  : Pass
```

Environment：

```text
Python                    : CPython 3.13.14／arm64／GIL enabled
llama-cpp-python          : 0.3.34
GPU Offload Support       : true
Metal System Info         : present
Dependency Version Match  : true
Out-of-scope Package      : absent
```

Dependency Gate：

```text
uv lock --check
  Resolved 117 packages

uv sync --dry-run --frozen --offline \
  --extra inference-llama \
  --group dev \
  --group notebook \
  --no-binary-package llama-cpp-python

  Checked 115 packages
  Would make no changes
```

## 9. Native Metal／CLI Evidence

Sandbox外のNative macOS／Apple Silicon arm64／Metal環境で実行した。

```text
.venv/bin/pytest -q -m model_smoke
  2 passed, 161 deselected
```

Real `model-info`：

```text
application_schema_version      : 2
model_definition_schema_version : 2
thinking_mode                   : disabled
visibility                      : hidden
display_label                   : 高度推論
persistence                     : disabled
visibility_source               : application
display_label_source            : application
persistence_source              : application
parser_key                      : tagged_thinking_v1
device                          : gpu／metal
gpu_offload                     : true
```

Real CLI Structural Evidence：

```text
Hidden／Non-streaming:
  Thinking Execution : enabled
  Reasoning Display  : none
  Canonical Tag Leak : none
  Final              : 2

Visible／Non-streaming:
  Thinking Execution : enabled
  Opening Label      : <高度推論>
  Closing Label      : </高度推論>
  Canonical Tag Leak : none
  Final              : 2

Visible／Streaming／Custom:
  Thinking Execution : enabled
  Opening Label      : <思考過程>
  Closing Label      : </思考過程>
  Canonical Tag Leak : none
  Final              : 2
```

Raw Reasoning本文はPersistence Policyに従い、本Statusへ記録していない。

Phase 1-D Regression：

```text
Default ja  : 成功
Explicit en : success
auto        : OK
```

Production Acceptance：

```text
Success                         : true
Load including SHA-512          : 2.4690 seconds
Generation Result               : フェーズ1-B生産ランタイム成功
Generation Speed                : 26.45 tokens／second
Explicit Stream Terminal State  : cancelled
Post-cancel Generation          : OK／stop
Unload                          : 0.0469 seconds
Detected Device                 : gpu／metal
Artifact Digest Verified        : true
```

## 10. Raw Persistence／Boundary Evidence

Phase 1-EのPresentation／Output Protocol／Resolver内にFile／JSONL／Database Writerは存在しない。

```text
Raw Reasoning Persistence : disabled only
Memory上のParser Buffer   : temporary
Visible stdout            : user explicit opt-in
Disk Persistence          : none
```

Model Backend AdapterとModel Portに次は存在しない。

- Display Label
- Thinking Visibility
- Parser Key分岐
- Canonical Tag置換
- Presentation Policy

CLIにもCanonical `<think>`文字列またはDefault Label文字列をハードコードしていない。

## 11. Hash／Dependency不変

```text
Application Config SHA-512:
928888197b39c066b3e0befc08ba490c166752eae76c9c07fad47f48367dc851759642b5f2243349a1ab7fdc8d85ffcabcc5e39e93c0fac536cfbb64e48434e5

Model Definition SHA-512:
e41866e73a1847abbf973f39b6b26038d30454277b1d9fb6a278b9f165af7de9e00695df79c48e3d5b9c53f84c6e6aba5cafee000ac895e0d643035cb2a171d2

Model Artifact SHA-512（不変）:
f182f1d40606572d6965e50e0ef33c4be64b43ad65339710ceebb664e3d43e76398a4ef230c7a3dd8fbd643acbce8f0c7cbec28784203ccf26da0fe7e08bfceb

Mac Deployment Profile SHA-512（不変）:
861aa54e159285a5445df853b260b2465194a93bc2c254d3cfd9ec4b58c4fc6c1af0dd1ba7d80251a5e46f9c886fe2205d7931b346709002edb2e7d9f9ce2b40

Platform Registry SHA-512（不変）:
5af43fff30e5cf0716a927e05d1bde74a443e5a0484490a32398421824e3b4cc0539f64578dcc509fe620790686d7473587d7650665f2436b4c988281712d574

pyproject.toml SHA-256（不変）:
a46fcd0b61e8db84a5f90ac4459b92bf9ec9deb7d6219ce88d7b22c240b5ecfa

uv.lock SHA-256（不変）:
e5efe33d69105547fe0d4f348b6b189b85f7ed55323f8ecd993ef5df7846fee1
```

Definition File SHA-512は意図したSchema Migrationにより変化し、Runtime InfoとLoader再計算値が一致した。Model Artifact SHA-512は不変である。

## 12. Known Limitation／Runtime Observation

1. Thinking Protocol生成はModel出力に依存する。最初のNative Promptでは128 Token上限までにClosing／Finalへ到達せず、Hidden表示は空となった。Canonical Reasoningの漏洩はなく、決定論的Testでは`unclosed_reasoning`として扱うことを確認した。
2. HiddenはLeading Canonical Thinking SectionのPresentation制御であり、Secret Redaction／Prompt Injection Guardではない。
3. Extra DelimiterはUser Contentの可能性を考慮して削除せず、`malformed_protocol`／Warningとして観測する。
4. Parse Status／WarningはPresentation Contractから取得できるが、Raw Reasoning本文は保存しない。
5. `高度推論`はDisplay Channel Labelであり、Reasoning品質、正しさまたは真の内部推論を保証しない。

いずれもRequirementsに記録された非Blocker／Scope境界である。

## 13. Acceptance Criteria 22項目対応表

| # | Criteria | Result | Evidence |
|---:|---|---|---|
| 1 | ExecutionとVisibilityが独立 | Pass | CLI独立Test／Native Hidden・Visible |
| 2 | Persistenceが独立しdisabled固定 | Pass | Enum／Resolver／Override非実装Test |
| 3 | Application Schema 2 Strict | Pass | Config／Old Schema／Unknown Field Test |
| 4 | Deployment Schema 3不変 | Pass | Hash／Ownership Test |
| 5 | Default disabled／hidden／高度推論／disabled | Pass | Config／Resolver／model-info |
| 6 | Visibility／Label Env・CLI Override | Pass | Field別Precedence／CLI Test |
| 7 | Field別Source確認 | Pass | Contract／model-info／Test |
| 8 | Canonical DelimiterとDisplay Label分離 | Pass | Model Definition／Renderer Boundary |
| 9 | Model Definition Parser Keyで選択 | Pass | Registry／Bootstrap Test |
| 10 | Model／Architecture／Backend Hardcodeなし | Pass | Parser Registry Source Search |
| 11 | Non-streaming正規化 | Pass | Plain／Complete／Malformed Test |
| 12 | Streaming Delimiter Split対応 | Pass | 全Split Position／1文字Chunk Test |
| 13 | Hidden Streaming No-flash | Pass | Deterministic No-flash Test |
| 14 | Visible Default／Custom Label | Pass | Unit／Real CLI Non-stream・Stream |
| 15 | Malformed決定論処理／Warning | Pass | Unclosed／Extra Delimiter Test |
| 16 | Raw Result／Chunk不変 | Pass | Model Port Contract／Presentation Test |
| 17 | Finish／Usage／Cancel／Close保持 | Pass | Existing Contract／CLI／Native Acceptance |
| 18 | Raw Reasoning新規永続保存なし | Pass | Source Search／Writerなし |
| 19 | Thinking FlagでSampling非変更 | Pass | CLI Sampling Regression Test |
| 20 | 新規External Dependencyなし | Pass | pyproject／uv.lock Hash不変 |
| 21 | Static／Default Test Pass | Pass | 161 passed／2 deselected |
| 22 | Current Mac／Metal非Regression | Pass | 2 Native Test／Real CLI／Acceptance |

## 14. 設計者へのReview依頼

次を確認し、Phase 1-Eの最終受入を判定してほしい。

1. Execution／Parsing／Presentation／Persistenceの4責務分離
2. Application／Model Definition Schema `2` Migration
3. Model-declared Parser RegistryとPre-load Error
4. Stateful Streaming Parser／Hidden No-flash
5. RendererのCanonical Protocol非依存
6. Default `高度推論`／Custom Label
7. Raw Model Port／llama.cpp Adapter Contract不変
8. Raw Persistenceなし／Sampling非連動
9. 22 Acceptance CriteriaとStatic／Native Metal Evidence


<!-- SOURCE_END 85: docs/handoffs/implementer_status_phase_1e_thinking_presentation_20260719134914.md -->

---

<!-- SOURCE_BEGIN 86: docs/handoffs/implementer_status_phase_1f_lightning_cross_environment_runtime_20260719205819.md -->

### Source 86: `docs/handoffs/implementer_status_phase_1f_lightning_cross_environment_runtime_20260719205819.md`

- History Target: `docs/project/phases/phase_1/history/handoffs/implementer_status_phase_1f_lightning_cross_environment_runtime_20260719205819.md`
- Source SHA-512: `76f43d904240a63f9b1eb7dadfc12fd06c660527310ff2edfee8d138a37d8778c85a4dd50cf272d2fd7b00ff9f413afeedd47a045c7f223c3e00b97b781ed9e1`
- Source Size: `9141` bytes

# 実装担当 Phase 1-F Lightning Cross-environment Runtime Status

- 文書ID: `implementer_status_phase_1f_lightning_cross_environment_runtime`
- 状態: `repository_implementation_complete_waiting_lightning_native_verification`
- 作成日時: `2026-07-19 20:58:19 JST`
- 更新日時: `2026-07-19 20:58:19 JST`
- Snapshot: `20260719205819`
- 作成担当: 実装担当Task
- 正本言語: 日本語
- Handoff: [implementer_handoff_phase_1f_lightning_cross_environment_runtime_20260719202333.md](../history/handoffs/implementer_handoff_phase_1f_lightning_cross_environment_runtime_20260719202333.md)
- Acceptance Follow-up: [implementer_handoff_phase_1_acceptance_follow_up_20260719195134.md](../history/handoffs/implementer_handoff_phase_1_acceptance_follow_up_20260719195134.md)
- supersedes: なし（Phase 1-F Status系列の初回）

## 1. Authorization／Scope

ユーザーのPhase 1-F実装開始指示に基づき、Handoff記載ScopeのSource、Config、Lock、Tests、Scriptsを変更した。Acceptance Follow-upのCLI Help／Hidden Thinking Token上限Warningも同じMaterial Change Setで実装した。

README、Public Docs、Canonical Requirements／Architecture／ADR／Index、Git／GitHub、Backupは変更していない。`.python-version`は`3.13.14`のまま維持した。

## 2. Current State

```text
Repository Shared Changes       : Complete
Acceptance Follow-up            : Implemented／Mac Native Verified
Mac 3.13.14／Metal Regression   : Pass
Python 3.12／3.13 Lock Resolve  : Pass
Lightning 3.12.11／CUDA Native : Waiting External Execution
Lightning CPU Native            : Waiting External Execution
Phase 1-F Completion            : Not Claimed
```

## 3. Changed／Added Files

### Root／Config

- `pyproject.toml`
- `uv.lock`
- `config/platforms/platform_registry.toml`
- `config/profiles/lightning_linux_x86_64_cuda.toml`
- `config/profiles/lightning_linux_x86_64_cpu.toml`

### Source

- `src/margpa_runtime_llm/bootstrap/profile_resolver.py`
- `src/margpa_runtime_llm/modules/inference/contracts/runtime.py`
- `src/margpa_runtime_llm/adapters/model_backends/llama_cpp/runtime_detection.py`
- `src/margpa_runtime_llm/adapters/model_backends/llama_cpp/adapter.py`
- `src/margpa_runtime_llm/entrypoints/cli/main.py`

### Scripts

- `scripts/setup/verify_phase1_environment.py`
- `scripts/setup/setup_lightning_linux_x86_64_cuda.sh`
- `scripts/models/phase1f_cross_environment_acceptance.py`

### Tests

- `tests/unit/inference/test_config_and_registry.py`
- `tests/unit/inference/test_deployment_platform.py`
- `tests/unit/inference/test_cli.py`
- `tests/integration/llama_cpp/test_phase1b_runtime.py`
- `tests/integration/llama_cpp/test_phase1f_cross_environment_runtime.py`

## 4. Implementation Summary

### Python／Lock

- `requires-python = ">=3.12,<3.14"`
- Ruff Targetを`py312`へ変更
- Mypy Python Versionを`3.12`へ変更
- Direct Dependency Pinは維持
- `uv.lock`を117 Packageで再生成
- Linux x86_64／Python 3.12.11とmacOS arm64／Python 3.13.14のDependency TreeをLockから解決確認

### Deployment／Detection

- Platform Registry Schemaを2へ更新
- Execution Environmentを`native／container`として独立管理
- Docker／OCI Marker、`container` Environment、Cgroup MarkerによるContainer検出
- Linux Distribution IDをHost Evidenceへ追加
- ProfileとDetected HostのOS／Architecture／Execution Environment／DistributionをPre-load照合
- Mac Default Profile Resolutionを維持
- Lightning CUDA／CPUはExplicit `--profile`のみとし、自動Fallbackを追加していない

### CUDA／CPU Runtime

- llama.cpp System Infoから`metal／cuda／cpu／unknown` Build Variantを分離
- `gpu_layers=0`はBuild Variantにかかわらず`cpu／cpu_native／gpu_offload=false`
- CUDA Build＋GPU Layersは`gpu／cuda／gpu_offload=true`
- Observed Build VariantをRuntime Info／Runtime Observationへ記録
- ProfileのBuild Variant、Device Kind、Acceleration API、Capability不一致はLoad後にUnloadしてSafe Failure
- CUDA ProfileがCPU Runtimeへ黙ってFallbackする経路をTestで拒否

### Setup／Evidence

- Lightning Ubuntu x86_64 Container／Python 3.12.11／uv 0.11.29のPreflight
- Normal Dependency Syncと`llama-cpp-python==0.3.34` CUDA Source Buildを分離
- Existing CUDA Build再利用と明示`--rebuild-native`
- `--cpu-only`でGPU未割当時にCUDA Build＋`gpu_layers=0`を検証可能
- Cross-environment Acceptance ProbeでSHA-512、Load、Generate、Non-stream、Stream、Cancel、Post-cancel、Language、Thinking、UnloadをEvidence化

### Acceptance Follow-up

- Top-level／`generate`／`model-info` Helpで大文字を仮引数名と明示
- `--profile`をSubcommand後へ置くことを明示
- 意味のあるMetavarとOption説明を追加
- Thinking Enabled、Hidden、Finalなし、`finish_reason=length`、Tagged Thinking Evidenceありの場合だけSafe Warningをstderrへ表示
- Warning Exit Codeは0
- Streaming／Non-streamingを同一判定
- Visible、Thinking Disabled、正常Final、Stop、Plain Empty、CancelでFalse PositiveしないUnit Testを追加

## 5. Mac Verification

Environment：

```text
Python             : CPython 3.13.14／GIL enabled
Host               : macOS arm64／native
Backend            : llama-cpp-python 0.3.34
Build Variant      : metal／observed
Device             : gpu／metal／gpu_offload=true
Model SHA-512      : f182f1d40606572d...26da0fe7e08bfceb
```

Commands／Results：

```text
ruff format --check .                         : Pass／70 files
ruff check .                                  : Pass
mypy                                           : Pass／70 source files
python -m compileall -q src scripts tests      : Pass
bash -n setup_macos + setup_lightning          : Pass
pytest -q                                      : 181 passed, 3 deselected
uv lock --check --offline                      : Pass／117 packages
verify_phase1_environment --target macos-metal : Pass
pytest -q -m model_smoke                       : 2 passed, 1 skipped, 181 deselected
phase1f_cross_environment_acceptance.py        : Pass
```

Cross-environment ProbeのMac実測：

```text
Load including SHA-512 : 2.4483 s
RSS before load        : 55,476,224 bytes
RSS after load         : 3,270,770,688 bytes
RSS after unload       : 176,816,128 bytes
Generate／Stream       : Pass
Cancel／Post-cancel    : Pass
Language／Thinking     : Pass
Unload                 : Pass
```

Metal TestはSandbox内ではMetal Deviceが公開されずCommand Queue作成に失敗したため、Mac実機Contextで再実行してPassした。Sandbox失敗はProduct Failure Evidenceへ数えない。

Hidden Thinking実Model Probe：

```text
Condition : Thinking enabled／hidden／max_new_tokens=8／length
stdout    : Reasoning非表示
stderr    : 最終回答を生成する前にToken上限へ到達しました。
Exit Code : 0
```

## 6. Lightning Execution Commands

ModelはDefinitionのRelative Pathと一致するPersistent Storageへ配置する。

```text
<MODEL_ROOT>/main/qwen3-4b/gguf/Qwen3-4B-Q4_K_M.gguf
```

CUDA Mandatory Gate：

```bash
scripts/setup/setup_lightning_linux_x86_64_cuda.sh \
  --rebuild-native \
  --cuda-smoke \
  --model-path <MODEL_ROOT>/main/qwen3-4b/gguf/Qwen3-4B-Q4_K_M.gguf
```

同じCUDA BuildによるCPU Candidate A：

```bash
scripts/setup/setup_lightning_linux_x86_64_cuda.sh \
  --cpu-only \
  --cpu-smoke \
  --model-path <MODEL_ROOT>/main/qwen3-4b/gguf/Qwen3-4B-Q4_K_M.gguf
```

追加のPytest Native Entry：

```bash
MARGPA_MODEL_ROOT=<MODEL_ROOT> \
MARGPA_PHASE1F_PROFILE=config/profiles/lightning_linux_x86_64_cuda.toml \
.venv/bin/pytest -q -m model_smoke \
  tests/integration/llama_cpp/test_phase1f_cross_environment_runtime.py
```

CPUの場合はProfile Environmentを`lightning_linux_x86_64_cpu.toml`へ変更する。

## 7. Known Limitations／CPU Disposition

- Lightning外部環境のInstall、CUDA Build、Model配置、GPU利用は本Taskから実行していない。
- CUDA ProfileとCPU ProfileはEvidence取得前のため`verification_state = defined`であり、`native_verified`へ偽装していない。
- CPU Candidate AはRepository実装済みだがNative未確認である。
- GPU未割当時にCUDA-enabled `llama-cpp-python`をImport／Loadできない場合、失敗Evidenceを保存し、別CPU Build Environment案を設計者Reviewへ返す。
- `RuntimeObservation.executed`はCurrent Model Port Contractどおり`null`を維持する。Generation／Stop／CancelはAcceptance ProbeのResult Evidenceへ記録する。

## 8. Remaining Gate／Review Request

次はLightning上でSection 6を実行し、次を取得する。

1. Python 3.12.11 Dependency／Default Test
2. Container／Ubuntu Detection
3. CUDA Build Variant／System Info／GPU Observation
4. Qwen3-4B SHA-512一致
5. Generate／Stream／Non-stream／Cancel／Unload
6. Response Language／Thinking Presentation
7. CPU Candidate AのPassまたは明示Failure Evidence

Lightning Evidence受領後、新Timestampの後継`implementer_status_*`を作成してPhase 1-F Reviewを依頼する。現時点ではPhase 1-F完了を宣言しない。

<!-- SOURCE_END 86: docs/handoffs/implementer_status_phase_1f_lightning_cross_environment_runtime_20260719205819.md -->

---

<!-- SOURCE_BEGIN 87: docs/handoffs/implementer_status_phase_1f_lightning_read_only_preflight_20260721013900.md -->

### Source 87: `docs/handoffs/implementer_status_phase_1f_lightning_read_only_preflight_20260721013900.md`

- History Target: `docs/project/phases/phase_1/history/handoffs/implementer_status_phase_1f_lightning_read_only_preflight_20260721013900.md`
- Source SHA-512: `0604bdd9799fc818a6f3c0b73c4c0092f920c34f5c1a6cd15ad77f4ec3a4e4601b38f2093cea871e452a90da29327ac96a0a957360e772883b69c26fefca06ce`
- Source Size: `4645` bytes

# 実装担当 Phase 1-F Lightning Read-only Preflight Status

- 文書ID: `implementer_status_phase_1f_lightning_read_only_preflight`
- 状態: `preflight_blocked_waiting_designer_decision`
- 作成日時: `2026-07-21 01:39:00 JST`
- 更新日時: `2026-07-21 01:39:00 JST`
- Snapshot: `20260721013900`
- 作成担当: 実装担当Task
- 正本言語: 日本語
- Documentation Index: [documentation_index_20260721010621.md](../history/documentation_index_20260721010621.md)
- Preflight Handoff: [implementer_handoff_phase_1f_lightning_read_only_preflight_20260721010621.md](../history/handoffs/implementer_handoff_phase_1f_lightning_read_only_preflight_20260721010621.md)

## 1. Authorization／Scope

ユーザーの「最新IndexとPreflight Handoffを読んで開始」およびLightning Studio準備完了の指示に基づき、Phase 1-F Read-only Preflightだけを実行した。

Lightning Studioへ配置したProject Fileは`preflight_lightning_ai_studio.sh` 1点だけである。Full Project、Model Artifact、`.venv`は搬入していない。Package Install／Sync／Build、Environment／GPU設定変更、Source／Config／Test／Script変更、Git／GitHub操作、失敗後のRepairは行っていない。

Private URL、Session／Machine Identifier、Hostname、個人Path、Secretは本Statusへ記録していない。

## 2. Current State

```text
Target Studio                 : MARGPA-RUNTIME-LLM／1 x T4
Preflight Script Placement    : Complete／Hash Match
Help Gate                     : Pass
GPU Read-only Preflight       : Fail／uv Version Gate
CPU Candidate Preflight       : Fail／uv Version Gate
Full Project／Model Upload    : Not Performed
Environment Repair            : Not Performed／Not Authorized
Phase 1-F Native Runtime Gate : Not Started
Phase 1-F Completion          : Not Claimed
```

## 3. Script Placement／Integrity

配置先はStudio内の次のProject相対Pathである。

```text
scripts/setup/preflight_lightning_ai_studio.sh
```

Local正本とStudio配置物のSHA-512を照合した。

```text
SHA-512 : 1e78756d581de1895542bfc9a2f25438c4a2058b2d3873dd9208191f3d028cfff8cecb434a1d2ee02885727043b592ea90356df50774795e45ef91ebbe356eab
Result  : OK
Exit    : 0
```

## 4. Commands／Results

### 4.1 Help Gate

```bash
bash scripts/setup/preflight_lightning_ai_studio.sh --help
```

```text
Exit   : 0
Stdout : Usage、environment-mode、cpu-only、help、およびRead-only Probeの説明を表示
Stderr : None
```

### 4.2 GPU Read-only Preflight

```bash
bash scripts/setup/preflight_lightning_ai_studio.sh --environment-mode auto
```

```text
Exit   : 1
Stdout : None
Stderr : Phase 1-F Lightning preflight failed: expected uv 0.11.29, got 0.11.18
```

### 4.3 CPU Candidate Read-only Preflight

```bash
bash scripts/setup/preflight_lightning_ai_studio.sh --environment-mode auto --cpu-only
```

```text
Exit   : 1
Stdout : None
Stderr : Phase 1-F Lightning preflight failed: expected uv 0.11.29, got 0.11.18
```

GPU／CPUの両経路は同一の`uv` Version Gateで停止した。失敗地点より後段の正式なGPU／`nvcc`判定には到達していない。

## 5. Read-only Environment Evidence

Preflight Scriptの判定順序上、`uv` Gate到達前に次が合格している。

```text
Platform            : Linux
Architecture        : x86_64
Distribution        : Ubuntu
Container Marker    : Supported
Environment Mode    : studio-active／autoで解決
Python              : 3.12.11／Exact Match
uv Expected         : 0.11.29
uv Observed         : 0.11.18
```

失敗後のRepairを行わず、後続判断に必要な事実だけを独立したRead-only Commandで確認した。

```text
Allocated GPU       : Tesla T4
GPU Memory Total    : 15360 MiB
nvidia-smi Exit     : 0
nvcc Availability   : Available
nvcc Probe Exit     : 0
```

これらの独立確認はGPU／CPU Preflightの失敗を合格へ変更するものではない。

## 6. Stop Reason／Designer Decision Request

Handoffが要求する`uv 0.11.29`とStudio Active Environmentの`uv 0.11.18`が一致しないため、Read-only PreflightはBlockされた。契約どおり、その場でのVersion変更や環境修復は行わず停止した。

設計者役には、次のいずれかを正本文書で決定するよう依頼する。

```text
1. PreflightのExpected uv Versionを見直す
2. 検証手順を伴うuv 0.11.29への明示的更新を別Scopeとして許可する
3. その他のEnvironment Mode／Runtime構築方針を指定する
```

決定と再実行許可が得られるまでは、Full Project／Model搬入、Lightning CUDA／CPU Native Gate、Phase 1-F完了判定へ進まない。

<!-- SOURCE_END 87: docs/handoffs/implementer_status_phase_1f_lightning_read_only_preflight_20260721013900.md -->

---

<!-- SOURCE_BEGIN 88: docs/handoffs/implementer_status_phase_1f_minor_static_gate_follow_up_20260721005412.md -->

### Source 88: `docs/handoffs/implementer_status_phase_1f_minor_static_gate_follow_up_20260721005412.md`

- History Target: `docs/project/phases/phase_1/history/handoffs/implementer_status_phase_1f_minor_static_gate_follow_up_20260721005412.md`
- Source SHA-512: `d2c00beeac35531ef9de4bde8d879b94682307241188d28b690091ea9c3665208019e4997f3aef4cb3bd3148157a37dd482aa6f23a99f158acf1a4a1a99505bd`
- Source Size: `5232` bytes

# 実装担当 Phase 1-F Minor Static Gate Follow-up Status

- 文書ID: `implementer_status_phase_1f_minor_static_gate_follow_up`
- 状態: `minor_follow_up_complete_waiting_designer_review`
- 作成日時: `2026-07-21 00:54:12 JST`
- 更新日時: `2026-07-21 00:54:12 JST`
- Snapshot: `20260721005412`
- 作成担当: 実装担当Task
- 正本言語: 日本語
- Documentation Index: [documentation_index_20260721003201.md](../history/documentation_index_20260721003201.md)
- Review: [designer_review_phase_1f_repository_follow_up_20260721003201.md](../history/handoffs/designer_review_phase_1f_repository_follow_up_20260721003201.md)
- Phase 1-F Handoff: [implementer_handoff_phase_1f_lightning_cross_environment_runtime_20260719202333.md](../history/handoffs/implementer_handoff_phase_1f_lightning_cross_environment_runtime_20260719202333.md)
- supersedes: `implementer_status_phase_1f_repository_review_follow_up_20260721001705.md`

## 1. Authorization／Scope

ユーザーの「最新のIndexとReviewを読んで作業」指示に基づき、Review Section 3.1のFull Project Mypy Failureと、Section 5のAccepted Setting Decisionだけを変更した。

変更範囲は`config/application.toml`、局所Source／Tests、本Implementer Statusである。Canonical Requirements／Architecture／Governance／ADR／Index／Review、Lightning外部環境、Phase 1-G、Backup、Git／GitHubは変更していない。

## 2. Current State

```text
Full Project Mypy Finding       : Resolved
generation.max_new_tokens       : 2048／Applied
Full Static／Default Gate       : Pass
Lightning Read-only Preflight   : Not Run
Lightning CUDA／CPU Native Gate : Not Run
Phase 1-F Completion            : Not Claimed
Phase 1-G                       : Not Started／Not Authorized
```

## 3. Changed Files

- `config/application.toml`
- `src/margpa_runtime_llm/adapters/model_backends/llama_cpp/runtime_detection.py`
- `tests/unit/inference/test_deployment_platform.py`
- `tests/unit/inference/test_config_and_registry.py`
- `docs/handoffs/implementer_status_phase_1f_minor_static_gate_follow_up_20260721005412.md`

## 4. Full Mypy Finding修正

旧Testは、Runtime Moduleが内部Importしている`subprocess`へ直接到達し、`runtime_detection_module.subprocess.run`をMonkeypatchしていた。このため、MypyのExplicit Export境界で次の1件が失敗していた。

```text
Module runtime_detection does not explicitly export attribute subprocess
```

修正後は`observe_nvidia_process_gpu_memory`へ型付き`NvidiaSmiCommandRunner`を注入できる境界を追加した。

```text
Production : Default Runnerがsubprocess.runをTimeout付きで実行
Unit Test  : subprocess.CompletedProcess[str]を返すFake Runnerを引数注入
Result     : TestからRuntime Module内部Memberへ到達しない
```

Testは、Runnerへ渡されるCommandがCurrent Process GPU Memory Queryであること、同一PIDの複数Rowだけを合算すること、別PIDを除外することを引き続き確認する。

## 5. Accepted Setting Decision反映

Application ConfigのDefault Generation上限を次へ変更した。

```toml
[generation]
max_new_tokens = 2048
```

Application Config所有値とEffective macOS Configを確認する2つのUnit Testを`2048`へ更新した。

低Levelの`GenerationParameters()`単独生成時に使用するContract Default `512`は変更していない。今回のAccepted Decisionは`config/application.toml`のApplication Defaultを対象としており、明示Override、Environment Override、Request Parameterの優先順位も変更していない。

Thinking表示LabelはReviewどおり変更せず、Phase 1-Gの後続事項として維持した。

## 6. Verification

### Finding Reproduction／Targeted

```text
mypy .                                                        : Pass／70 source files
pytest -q test_deployment_platform + test_config_and_registry : Pass／65 tests
```

### Full Static／Default Gate

```text
ruff format --check src scripts tests       : Pass／70 files
ruff check src scripts tests                : Pass
mypy .                                      : Pass／70 source files
python -m compileall -q src scripts tests   : Pass
bash -n Mac Setup／Lightning Setup／Preflight: Pass
uv lock --check --offline                   : Pass／117 packages
pytest -q                                   : Pass／183 passed、3 deselected
```

`uv lock --check --offline`はSandbox内ではユーザーCacheへのAccess制限により開始できなかったため、同じCommandをSandbox外で再実行し、117 PackageのLock整合を確認した。Lock Fileは変更していない。

## 7. Remaining Gate／Review Request

Repository上のMinor Static Gate残件は解消した。次は設計者役のShort Follow-up Reviewを依頼する。

Review合格後の順序はCurrent Indexどおり次を維持する。

```text
Lightning Read-only Preflight
  → Preflight合格後にSource／Modelを一度に搬入
  → Lightning Python 3.12.11／CUDA Mandatory／CPU Candidate Gate
  → 後継Implementer Status
  → Phase 1-F Final Review
```

本StatusはLightning操作、Upload、Phase 1-F完了宣言、Phase 1-G実装、Backup、Git／GitHub操作を行っていない。

<!-- SOURCE_END 88: docs/handoffs/implementer_status_phase_1f_minor_static_gate_follow_up_20260721005412.md -->

---

<!-- SOURCE_BEGIN 89: docs/handoffs/implementer_status_phase_1f_pure_cpu_acceptance_correction_20260725214037.md -->

### Source 89: `docs/handoffs/implementer_status_phase_1f_pure_cpu_acceptance_correction_20260725214037.md`

- History Target: `docs/project/phases/phase_1/history/handoffs/implementer_status_phase_1f_pure_cpu_acceptance_correction_20260725214037.md`
- Source SHA-512: `2ab44c345b9bbae6a78adc8c42b0c68a46d93a69978cc1a09f6bf3db510b7296459de27280c4d2230f264f4024b296f49efc05a0fbea5d86f5a25ea3fa227c70`
- Source Size: `6347` bytes

# Phase 1-F Pure CPU Acceptance Correction 実装者Status

- 文書ID: `implementer_status_phase_1f_pure_cpu_acceptance_correction`
- 状態: `repository_correction_completed_designer_review_pending`
- 作成日時: `2026-07-25 21:40:37 JST`
- 更新日時: `2026-07-25 21:40:37 JST`
- Snapshot: `20260725214037`
- 作成担当: 実装者役担当Task
- 対象Handoff: [designer_handoff_phase_1f_pure_cpu_acceptance_correction_20260725212559.md](../history/handoffs/designer_handoff_phase_1f_pure_cpu_acceptance_correction_20260725212559.md)
- Source Review: [designer_review_phase_1f_pure_cpu_repository_20260725212559.md](../history/handoffs/designer_review_phase_1f_pure_cpu_repository_20260725212559.md)

## 1. Result

Pure CPU Native AcceptanceのBlocking FindingをRepository内で修正した。

```text
Acceleration Match:
  CUDA GPU                : cuda
  CUDA Build CPU Execution: cpu_native
  Pure CPU Build          : none

Model Selection:
  Canonical Input : Model Root
  Artifact        : Registry Relative Path
  Compatibility   : Validated --model-path
  Download        : none
```

外部Lightning Environment、Dependency Install、Model配置、Native BuildおよびModel Generationは実行していない。

## 2. Changed Files

### Implementation

- `scripts/models/phase1f_cross_environment_acceptance.py`
- `scripts/setup/setup_lightning_linux_x86_64_cpu.sh`

### Test

- `tests/unit/inference/test_lightning_cpu_native_setup.py`
- `tests/integration/llama_cpp/test_phase1f_cross_environment_runtime.py`

### Status

- `docs/handoffs/implementer_status_phase_1f_pure_cpu_acceptance_correction_20260725214037.md`

## 3. Acceleration Match Fix

Native Acceptance ScriptからCPU Runtimeの固定値：

```text
runtime.acceleration_api == "cpu_native"
```

を除去した。

`runtime_evidence_matches_profile()`をPure Functionとして抽出し、全Targetで次を共通確認する。

```text
runtime.acceleration_api
  == selected profile.compute.acceleration_api_key
```

GPU Profileでは併せて次を要求する。

- GPU Offload Supported
- GPU Offload Requested
- GPU Offload Observed
- Runtime GPU Offload True
- Device Kind GPU

CPU Profileでは次を要求する。

- GPU Offload Not Requested
- GPU Offload Not Observed
- Runtime GPU Offload False
- Device Kind CPU
- Profile Acceleration API一致

このため、次を正しく区別する。

```text
lightning_linux_x86_64_cuda.toml
  compute=gpu / acceleration=cuda

lightning_linux_x86_64_cpu.toml
  compute=cpu / acceleration=cpu_native

lightning_linux_x86_64_cpu_native.toml
  compute=cpu / acceleration=none
```

Profile不一致はFail Closedになる。

## 4. Model Root／Path Contract

### Canonical Option

Pure CPU Setupへ次を追加した。

```text
--model-root MODEL_ROOT
```

Setupは選択Registry：

```text
config/models/qwen3_4b_q4_k_m.toml
```

の`artifact.relative_path`を読み、次を解決する。

```text
MODEL_ROOT/main/qwen3-4b/gguf/Qwen3-4B-Q4_K_M.gguf
```

`--model-smoke`選択時は、この解決結果が実FileでなければSetup／Build前にFail Closedにする。

Native Acceptance Scriptにも`--model-root`を追加し、同じ値をApplication Compositionへ渡す。Reportは実際に解決された`model_artifact_path`を記録する。

### Compatibility Option

既存`--model-path`は削除していない。

ただし任意Artifact Overrideではなく、次を満たすCompatibility Validationとして定義した。

- Registry Relative LayoutとSuffixが完全一致する。
- `--model-root`未指定時はValid PathからRootを導出する。
- `--model-root`併用時は、そのRootから解決したExpected Artifactと完全一致する。
- Layout不一致、Root不一致、改行を含むPathは拒否する。

指定FileとSmokeがLoadするFileが異なる状態を許可しない。

### Display

`--plan`と実Setupは次を表示する。

```text
Model Root
Resolved Artifact
Smoke Artifact
```

## 5. Updated User Commands

推奨手順：

```bash
scripts/setup/setup_lightning_linux_x86_64_cpu.sh \
  --plan \
  --model-root /absolute/path/to/model-root
```

Model配置後のBounded Smoke：

```bash
scripts/setup/setup_lightning_linux_x86_64_cpu.sh \
  --environment-mode auto \
  --model-smoke \
  --model-root /absolute/path/to/model-root
```

Compatibility Optionを使う場合：

```bash
scripts/setup/setup_lightning_linux_x86_64_cpu.sh \
  --environment-mode auto \
  --model-smoke \
  --model-path /absolute/path/to/model-root/main/qwen3-4b/gguf/Qwen3-4B-Q4_K_M.gguf
```

Expected Layoutと一致しないPathは受理しない。

## 6. Automated Test

追加／更新した確認：

- CUDA GPU Profileと`cuda`一致
- CUDA Build CPU Profileと`cpu_native`一致
- Pure CPU Profileと`none`一致
- Profile／Runtime Acceleration不一致拒否
- Unknown Compute Kind拒否
- Pure CPU Fixtureで`all_required_checks_passed=True`
- False Checkを含む場合のFail Closed
- Model RootからRegistry Artifact解決
- Valid Compatibility `--model-path`
- Invalid Layout拒否
- Model Root／Path不一致拒否
- Smoke Artifact存在確認
- Specified ArtifactとAcceptanceへ渡すModel Root一致
- Existing `--model-path` Help維持
- Shell Syntax

## 7. Verification Result

```text
pytest              : 267 passed, 3 deselected
Ruff Check          : PASS
Ruff Format         : PASS／95 files
Mypy strict         : PASS／95 source files
uv lock --check     : PASS／122 packages
Shell Syntax        : PASS
```

`3 deselected`にはExternal Native／Model Smokeが含まれる。未実行をPassとは記録しない。

## 8. External Native Pending

次は未実施である。

- Lightning CPU Environment Reconstruction
- Pure CPU Native Build
- Actual Model SHA-512
- Model Load
- `runtime_evidence_matches_profile` Native Result
- Short Generation／Streaming／Cancel
- Memory／Latency
- Shutdown

Repository Correctionが設計ReviewでAcceptedとなった後、ユーザー実行Gateで確認する。

## 9. Known Limitations

- `--model-root`は選択RegistryのExpected Relative Layoutを必要とする。
- `--model-path`は任意File Overrideではない。
- Model Artifactを自動Download／移動／Uploadしない。
- External Native PerformanceとBuild時間は未測定である。
- Web UI、Profile設計、RAG、Git／GitHubは変更していない。


<!-- SOURCE_END 89: docs/handoffs/implementer_status_phase_1f_pure_cpu_acceptance_correction_20260725214037.md -->

---

<!-- SOURCE_BEGIN 90: docs/handoffs/implementer_status_phase_1f_pure_cpu_runtime_follow_up_20260725203508.md -->

### Source 90: `docs/handoffs/implementer_status_phase_1f_pure_cpu_runtime_follow_up_20260725203508.md`

- History Target: `docs/project/phases/phase_1/history/handoffs/implementer_status_phase_1f_pure_cpu_runtime_follow_up_20260725203508.md`
- Source SHA-512: `3696ff2f4cb3600fd7424f99736b12f6e0a4c5393e5ad6855e3f319b5759582c25fbccaa876463ac0d8128c734f68d6e35edfd9cd301982cc385a51ab7fb64db`
- Source Size: `7362` bytes

# Phase 1-F Lightning Pure CPU Runtime Follow-up 実装者Status

- 文書ID: `implementer_status_phase_1f_pure_cpu_runtime_follow_up`
- 状態: `repository_implementation_completed_external_native_validation_pending`
- 作成日時: `2026-07-25 20:35:08 JST`
- 更新日時: `2026-07-25 20:35:08 JST`
- Snapshot: `20260725203508`
- 作成担当: 実装者役担当Task
- 対象Handoff: [designer_handoff_phase_1f_lightning_pure_cpu_runtime_follow_up_20260725200001.md](../history/handoffs/designer_handoff_phase_1f_lightning_pure_cpu_runtime_follow_up_20260725200001.md)
- Preflight Addendum: [designer_handoff_phase_1f_lightning_pure_cpu_preflight_addendum_20260725201016.md](../history/handoffs/designer_handoff_phase_1f_lightning_pure_cpu_preflight_addendum_20260725201016.md)

## 1. Result

Lightning Linux x86_64向けPure CPU Repository Hookを実装した。

```text
Build Variant    : cpu
Execution Device : cpu
Acceleration API : none
GPU Layers       : 0
GPU Offload      : false
Fallback         : deny
```

外部Lightning Environment、Dependency Install、Native Build、Model配置、Model Generationは操作していない。External Native AcceptanceはPendingである。

## 2. Changed Files

### Profile／Runtime

- `config/profiles/lightning_linux_x86_64_cpu_native.toml`
- `src/margpa_runtime_llm/adapters/model_backends/llama_cpp/runtime_detection.py`

### Setup／Verification

- `scripts/setup/preflight_lightning_ai_studio.sh`
- `scripts/setup/setup_lightning_linux_x86_64_cpu.sh`
- `scripts/setup/verify_phase1_environment.py`

### Test

- `tests/unit/inference/test_config_and_registry.py`
- `tests/unit/inference/test_deployment_platform.py`
- `tests/unit/inference/test_lightning_cpu_native_setup.py`
- `tests/integration/llama_cpp/test_phase1f_cross_environment_runtime.py`

## 3. Existing CPU Profile Disposition

Existing Profile：

```text
config/profiles/lightning_linux_x86_64_cpu.toml
```

はRename／Delete／意味変更していない。

```text
Existing lightning_linux_x86_64_cpu.toml
  build : cuda
  run   : cpu

New lightning_linux_x86_64_cpu_native.toml
  build : cpu
  run   : cpu
```

CUDA Build CPU ExecutionとPure CPU Buildを別Profileとして維持する。

## 4. Pure CPU Build Detection

Runtime Detectionは、CPU Buildかつ`gpu_layers=0`の場合に次を返す。

```text
build_variant    : cpu
device_kind      : cpu
acceleration_api : none
gpu_offload      : false
```

CUDA Buildを`gpu_layers=0`で実行する場合は既存どおり次を維持する。

```text
build_variant    : cuda
device_kind      : cpu
acceleration_api : cpu_native
```

Setupは`llama-cpp-python==0.3.34`のBackend情報とGPU Offload Supportを確認し、Compatible Pure CPU BuildだけをReuseする。Missing／Mismatchまたは`--rebuild-native`時だけ、Accelerator BackendをOFFにしたSource Buildを実行する。

## 5. Preflight Decision

重複Scriptを追加せず、Existing：

```text
scripts/setup/preflight_lightning_ai_studio.sh
```

を後方互換で拡張した。

Target：

```text
Default                     : cuda-gpu
--cpu-only                  : cuda-cpu
--runtime-target cuda-gpu   : CUDA Build／GPU Execution
--runtime-target cuda-cpu   : CUDA Build／CPU Execution
--runtime-target cpu-native : Pure CPU Build／CPU Execution
```

`--cpu-only`の意味をPure CPUへ変更していない。

CPU-native Preflightは次を確認する。

- Linux／x86_64／Ubuntu／Container
- Environment Mode
- Python 3.12.11
- uv 0.11.29とPath
- CPU Count
- Available Memory
- Project／Environment Path Read／Write条件
- Pure CPU Profile Parse／Locked Value
- Optional Model Root Presence

CPU-native経路で実行しないCommand：

```text
nvidia-smi
nvcc
CUDA Compiler
GPU Allocation Probe
```

## 6. Setup Behavior

`scripts/setup/setup_lightning_linux_x86_64_cpu.sh`は次を実装した。

- Python `>=3.12,<3.14`
- Project Venv／Studio Active Environment
- uv 0.11.29
- Frozen Lock確認
- Normal Dependency SyncとNative Rebuildの分離
- Compatible Pure CPU Build Reuse
- `--rebuild-native`
- `--plan`
- Explicit `--model-smoke`
- Explicit `--model-path`
- Missing Model時Fail Closed
- Model Downloadなし
- GPU／NVIDIA／CUDA Toolchain Commandなし
- Repeated Run可能

## 7. User-run Rebuild Procedure

Lightning CPU Environment上でProject Rootへ移動後、次の順に実行する。

### 1. Help

```bash
scripts/setup/preflight_lightning_ai_studio.sh --help
```

### 2. Read-only Preflight

```bash
scripts/setup/preflight_lightning_ai_studio.sh \
  --runtime-target cpu-native \
  --environment-mode auto
```

### 3. Setup Plan

```bash
scripts/setup/setup_lightning_linux_x86_64_cpu.sh --plan
```

### 4. Environment Setup

```bash
scripts/setup/setup_lightning_linux_x86_64_cpu.sh \
  --environment-mode auto
```

既存Native Buildを無条件にReuseせず強制再構築する場合：

```bash
scripts/setup/setup_lightning_linux_x86_64_cpu.sh \
  --environment-mode auto \
  --rebuild-native
```

### 5. Environment Verification

Target EnvironmentのPythonを使う。

```bash
python scripts/setup/verify_phase1_environment.py \
  --target lightning-cpu-native
```

### 6. Model Path確認

```bash
test -f /absolute/path/to/Qwen3-4B-Q4_K_M.gguf
```

不足時にScriptはDownloadしない。別Gateで配置する。

### 7. Bounded Smoke

```bash
scripts/setup/setup_lightning_linux_x86_64_cpu.sh \
  --environment-mode auto \
  --model-smoke \
  --model-path /absolute/path/to/Qwen3-4B-Q4_K_M.gguf
```

Main Model一個、短いPrompt、Bounded Token、Single Generationの既存Acceptance Hookを使う。

### 8. Exit Code

```bash
echo $?
```

`0`以外はPassとして扱わず、標準Errorの不足条件を確認する。

## 8. Verification

Repository上の実行結果：

```text
pytest                    : 265 passed, 3 deselected
Ruff check                : passed
Ruff format --check       : passed
Mypy strict               : passed / 95 source files
uv lock --check           : passed / 122 packages
Shell syntax              : passed
CPU-native mocked preflight: passed
```

自動Testで確認したもの：

- Pure CPU Profile Parse／Locked Value
- Existing CUDA GPU／CUDA CPU Profile非Regression
- Pure CPU Build Observation
- `acceleration_api=none`
- `gpu_layers=0`
- Explicit Target Verification Fail Closed
- Preflight Default Compatibility
- `--cpu-only` Compatibility
- CPU-native GPU Command非実行
- Unknown Target拒否
- Target Conflict拒否
- Help表示
- Mac誤実行拒否
- Setup Plan
- Shell Syntax

## 9. External Native Test Pending

次は未実施であり、Passとは記録しない。

- Fresh Lightning CPU Setup
- Actual CPU Instruction Set
- Native Build時間
- Backend Import／System Info
- Actual Model SHA-512
- Model Load
- Short Generation
- Streaming／Cancel／Token Limit
- Japanese Response
- Memory／Latency
- Shutdown

## 10. Known Limitations

- PreflightのLightning基準PythonはObserved Environmentどおり3.12.11固定である。
- Setup自体は3.12／3.13を受理する。
- Pure CPU Build時間、Memory、Latencyは外部環境で未測定である。
- Model ArtifactはRepository外に必要であり、自動Downloadしない。
- Project Documentation Explainer／RAG Hookは本変更で実装していない。
- Public URL、Upload、Credential、Git／GitHub操作は実施していない。


<!-- SOURCE_END 90: docs/handoffs/implementer_status_phase_1f_pure_cpu_runtime_follow_up_20260725203508.md -->

---

<!-- SOURCE_BEGIN 91: docs/handoffs/implementer_status_phase_1f_repository_review_follow_up_20260721001705.md -->

### Source 91: `docs/handoffs/implementer_status_phase_1f_repository_review_follow_up_20260721001705.md`

- History Target: `docs/project/phases/phase_1/history/handoffs/implementer_status_phase_1f_repository_review_follow_up_20260721001705.md`
- Source SHA-512: `5716ca6bf8a2187dcf6e55006ee0c30cd15226017a178982ca3119c6cdda96e582fa4f4afd96404ffb42e222e33b92145906c7b5f6db13eae731a570a8a65830`
- Source Size: `9746` bytes

# 実装担当 Phase 1-F Repository Review Follow-up Status

- 文書ID: `implementer_status_phase_1f_repository_review_follow_up`
- 状態: `repository_review_follow_up_complete_waiting_designer_review`
- 作成日時: `2026-07-21 00:17:05 JST`
- 更新日時: `2026-07-21 00:17:05 JST`
- Snapshot: `20260721001705`
- 作成担当: 実装担当Task
- 正本言語: 日本語
- Documentation Index: [documentation_index_20260720235113.md](../history/documentation_index_20260720235113.md)
- Review: [designer_review_phase_1f_lightning_cross_environment_runtime_20260720235113.md](../history/handoffs/designer_review_phase_1f_lightning_cross_environment_runtime_20260720235113.md)
- Handoff: [implementer_handoff_phase_1f_lightning_cross_environment_runtime_20260719202333.md](../history/handoffs/implementer_handoff_phase_1f_lightning_cross_environment_runtime_20260719202333.md)
- supersedes: `implementer_status_phase_1f_lightning_cross_environment_runtime_20260719205819.md`

## 1. Authorization／Scope

ユーザーの「最新のIndexとReviewを読んで作業」指示に基づき、Phase 1-F Repository ReviewのHigh 2件、Medium 2件、Low 1件へ対応した。

変更範囲は`src/`、`tests/`、`scripts/`および本Implementer Statusだけである。Canonical Requirements／Architecture／Governance／ADR／Index／Review、Config、Root File、Phase 1-G、Git／GitHub、Backup、Lightning外部環境は変更していない。

## 2. Current State

```text
Phase 1-F Repository Review Follow-up : Complete
Default Test／Lint／Type Check         : Pass
Mac Metal Native Regression           : Pass
Strict Acceptance on Mac Metal        : Pass
Lightning Target Preflight            : Waiting External Execution
Lightning CUDA／CPU Native Gate       : Waiting External Execution
Phase 1-F Completion                  : Not Claimed
Phase 1-G                             : Not Started／Not Authorized
```

## 3. Changed／Added Files

### Source

- `src/margpa_runtime_llm/modules/inference/contracts/runtime.py`
- `src/margpa_runtime_llm/modules/inference/public.py`
- `src/margpa_runtime_llm/adapters/model_backends/llama_cpp/runtime_detection.py`
- `src/margpa_runtime_llm/adapters/model_backends/llama_cpp/adapter.py`
- `src/margpa_runtime_llm/bootstrap/profile_resolver.py`

### Scripts

- `scripts/setup/verify_phase1_environment.py`
- `scripts/setup/setup_lightning_linux_x86_64_cuda.sh`
- `scripts/setup/preflight_lightning_ai_studio.sh`（新規）
- `scripts/models/phase1f_cross_environment_acceptance.py`

### Tests

- `tests/contract/model_port/test_model_port_contract.py`
- `tests/unit/inference/test_deployment_platform.py`
- `tests/unit/inference/test_llama_cpp_boundary.py`
- `tests/unit/inference/test_cli.py`
- `tests/integration/llama_cpp/test_phase1b_runtime.py`
- `tests/integration/llama_cpp/test_phase1f_cross_environment_runtime.py`

## 4. Review Finding対応

### 4.1 High: CUDA Build CapabilityとActual GPU Offload Evidenceの分離

`GpuOffloadEvidence`を追加し、次を独立記録する。

```text
supported                : Native Backendが対象BuildでGPU Offload可能か
requested                : gpu_layersによりGPU Offloadを要求したか
observed                 : Load後にActual GPU利用を観測したか
observation_source       : 証拠Source
process_gpu_memory_bytes : CUDA時のCurrent Process GPU Memory
```

- MetalはModel／Context Load成功後の`metal_model_load`をActual Evidenceとする
- CUDAはModel Load後に`nvidia-smi --query-compute-apps=pid,used_gpu_memory`を実行し、Current PIDのGPU Memoryが正値の場合だけ`observed=true`とする
- CUDA Build／GPU要求があってもCurrent Process Memoryを確認できなければ`gpu_offload=false`、`device_kind=unknown`としてFail Closedとする
- `CapabilityFeature.GPU_OFFLOAD`はProduction AdapterでActual Observation成功時だけ公開する
- CPU ProfileはCUDA Build Capabilityと`requested=false／observed=false`を分離する
- Pre-load Environment VerifierはActual GPU利用を主張せず、`gpu_offload_observed=null／requires_native_model_load`と記録する

### 4.2 High: Acceptance ProbeのFail-closed化

- 全必須条件をBooleanの`required_checks`へ集約
- `all_required_checks_passed = all(required_checks.values())`
- 1件でもFalseなら`success=false`かつProcess Exit Code 1
- 予期しない例外もSafe Errorだけを返してExit Code 1
- Integration Testは`success`、`all_required_checks_passed`、全`required_checks`を明示Assert
- Lightning Setupは`set -euo pipefail`によりProbeのNon-zeroを成功扱いしない

### 4.3 High／Medium: Language／Thinking Acceptance Evidence

- 日本語、英語、Streaming、Post-cancelに言語識別可能な別Markerを使用
- 日本語／英語のResolved Policyを別々に確認
- 各Policyに対応するSystem Message本文が実際の先頭System Messageへ注入されたことを確認
- Thinkingは`max_new_tokens=1024`へ拡張し、`finish_reason != length`を必須化
- `ThinkingParseStatus.COMPLETE`、Reasoning Segment、Final Segment、Final Markerを別々に必須化
- Hiddenは表示ContentがFinal ContentだけでCanonical Thinking Tagを含まないことを確認
- Visibleは`<高度推論>...</高度推論>`Label、Reasoning、Finalの分離を確認
- Unclosed ReasoningのSafe処理は既存Unit Testで別途維持し、Native Acceptance成功条件には数えない

### 4.4 Medium: Lightning Environment Mode

Lightning TargetでProject Venvだけを仮定しないよう、次を追加した。

```text
auto           : VIRTUAL_ENV／CONDA_PREFIX検出時はstudio-active、なければproject-venv
studio-active  : StudioのPersistent Active Environmentを直接使用
project-venv   : Project Local Venvを明示使用
```

- `scripts/setup/preflight_lightning_ai_studio.sh`はProject／Modelの大容量Upload前に単独実行できるRead-only Probe
- PreflightはHost、Container、Python 3.12.11、uv 0.11.29、Active Prefix、GPU Allocationを確認
- Environment作成、Package Install、Source Buildは行わない
- Full Setupは選択ModeとTarget Prefixを出力する
- Studio Active Prefixへ`uv sync`する場合は`--inexact`でStudio既存Packageを破壊しない
- Mac `.venv`は転送も再利用もしない

### 4.5 Low: `nvcc`判定順

- Dependency Sync前にTarget Python内の既存CUDA Buildを確認
- 既存CUDA Buildが有効で`--rebuild-native`未指定なら`nvcc`なしで再利用
- `nvcc`はNative CUDA Rebuildが実際に必要な場合だけ必須
- `--cpu-only`でもCUDA Buildが存在しなければRebuild用`nvcc`を要求する
- Build後にCUDA MarkerとGPU Offload Capabilityを再検証し、不一致はFail Closed

## 5. Verification

### Static／Default

```text
ruff format --check src scripts tests : Pass／70 files
ruff check src scripts tests          : Pass
mypy src + Phase 1-F Python Scripts   : Pass／54 source files
pytest -q                             : 183 passed, 3 deselected
bash -n Lightning Setup／Preflight    : Pass
Setup／Preflight --help               : Pass
```

### Mac Native Regression

```text
pytest -q -m model_smoke tests/integration
Result: 2 passed, 1 skipped, 1 deselected
```

Sandbox内ではMetal Command Queue作成が拒否されたため、Mac実機Contextで再実行してPassした。失敗位置は本変更のRuntime Evidence生成前であり、Sandbox外では同一TestがPassしている。

### Strict Phase 1-F Acceptance on Mac Metal

```text
success                         : true
all_required_checks_passed      : true
required_checks                 : 22／22 true
GPU Evidence                    : supported／requested／observed = true
GPU Observation Source          : metal_model_load
Japanese／English Marker        : Pass
Stream／Cancel／Post-cancel      : Pass
Thinking Parse                  : complete
Thinking Finish                 : stop
Thinking Reasoning              : 896 chars
Thinking Final                  : 15 chars
Hidden／Visible Separation      : Pass
Unload                          : Pass
Load including SHA-512          : 2.5276 s
RSS before／after／unload        : 55,656,448／3,265,462,272／177,225,728 bytes
```

## 6. Lightning Next Gate

最初に小さいPreflight ScriptだけをTargetへ配置して実行する。

```bash
scripts/setup/preflight_lightning_ai_studio.sh --environment-mode auto
```

GPU未割当でCPU Candidateだけを調べる場合：

```bash
scripts/setup/preflight_lightning_ai_studio.sh \
  --environment-mode auto \
  --cpu-only
```

Preflightで選択されたModeをFull Setupへ明示する。例：

```bash
scripts/setup/setup_lightning_linux_x86_64_cuda.sh \
  --environment-mode studio-active \
  --cuda-smoke \
  --model-path <MODEL_ROOT>/main/qwen3-4b/gguf/Qwen3-4B-Q4_K_M.gguf
```

Project VenvがTargetで利用可能な場合：

```bash
scripts/setup/setup_lightning_linux_x86_64_cuda.sh \
  --environment-mode project-venv \
  --venv .venv \
  --cuda-smoke \
  --model-path <MODEL_ROOT>/main/qwen3-4b/gguf/Qwen3-4B-Q4_K_M.gguf
```

`--rebuild-native`は明示的な再Build時だけ付与する。既存CUDA Buildがなければ、OptionなしでもSetupがRebuildを選択してその時点で`nvcc`を確認する。

## 7. Remaining／Review Request

- Lightning Target Preflightは未実行
- Lightning Python 3.12.11 Dependency Syncは未実行
- CUDA Source Build／既存Build再利用は未実行
- CUDA Current Process GPU Memory Evidenceは未取得
- Lightning CUDA／CPU Native Acceptanceは未実行
- Phase 1-F完了は宣言しない

設計者役は本Follow-upをReviewし、Pass後にLightning Preflight／Upload／Native Gateへ進めるか判定する。Phase 1-Gへは進まない。

<!-- SOURCE_END 91: docs/handoffs/implementer_status_phase_1f_repository_review_follow_up_20260721001705.md -->

---

<!-- SOURCE_BEGIN 92: docs/handoffs/implementer_status_phase_1g_cross_thread_cancel_follow_up_20260721150603.md -->

### Source 92: `docs/handoffs/implementer_status_phase_1g_cross_thread_cancel_follow_up_20260721150603.md`

- History Target: `docs/project/phases/phase_1/history/handoffs/implementer_status_phase_1g_cross_thread_cancel_follow_up_20260721150603.md`
- Source SHA-512: `685d57a58846c1cb14ab1cc63e5fbccd70715632763421fecd4ea6a52412f82c8577831b3632f883d80f3848c351783b0596bc2376fe14987ad4cf8f7ef7b9ba`
- Source Size: `5806` bytes

# Phase 1-G Cross-thread Cancel Follow-up 実装担当Status

- 文書ID: `implementer_status_phase_1g_cross_thread_cancel_follow_up`
- 状態: `implementation_and_verification_completed`
- 作成日時: `2026-07-21 15:06:03 JST`
- Snapshot: `20260721150603`
- 作成担当: 実装者役担当Task
- 対象Review: `designer_review_phase_1g_review_follow_up_20260721122621.md`
- 対象Handoff: `implementer_handoff_phase_1g_cross_thread_cancel_follow_up_20260721122621.md`

## 1. 結果

Phase 1-G Cross-thread Cancel Follow-upを限定Scope内で完了した。

Event Loop Threadから実行中Native Generatorへ`force_cancel()`／`close()`する経路を除去し、Producer Thread上でCancel／CloseするCooperative Cancelへ統一した。Thread-affine Regression、既存Queue Capacity超過Regression、Static／Default／Mac Native Model／Manual Browser Gateはすべて合格した。

Phase 1-Hには着手していない。

## 2. 変更File

| File | 変更内容 |
|---|---|
| `src/margpa_runtime_llm/web/streaming.py` | Event Loop側の即時／Timeout時`force_cancel()`を除去し、`request_cancel()`＋Producer終了待ちへ変更 |
| `tests/integration/web/test_web_app.py` | Thread-affine Blocking Stream、正常Cleanup、Timeout Safe FailureのRegression Testを追加 |
| `docs/handoffs/implementer_status_phase_1g_cross_thread_cancel_follow_up_20260721150603.md` | 本実装報告 |

Backend Contract、Dependency、`pyproject.toml`、`uv.lock`は変更していない。

## 3. Cross-thread競合の修正方式

Consumerが終了した場合は次の順序で処理する。

```text
Event Loop Thread
  consumer_stopped.set()
  session.request_cancel()
  Queue Drain
  Producer Taskを最大10秒Await

Producer Thread
  Queue投入待ちPollingから脱出、またはNative next()の次Chunk境界へ到達
  SessionがCancel要求を観測
  Native Stream cancel()
  Session Iterator close()
  Session finally
  Generation Gate解放
```

`consumer_stopped`により、Bounded Queueが満杯でもProducerの`queue.put()`待ちは解除される。Native `next()`中の場合は、そのThreadが次のChunk境界へ到達するまでEvent Loop側からGeneratorを閉じない。

Cancel／CloseはProducerのIteration Thread上だけで実行される。

## 4. Timeout時の動作

Production Cleanup Timeoutは10秒である。

10秒以内にProducerが終了しない場合、Thread-unsafeなNative Generator CloseへEscalateしない。`RuntimeError("The SSE producer did not stop during cleanup.")`を送出し、成功扱いしない。

Backend保証のThread-safe Stop Signalは今回追加していない。Native `next()`が長時間復帰しない場合は、明示的Cleanup失敗となる。

## 5. Regression Test

### 5.1 Thread-affine正常Cleanup

Fake Streamは次を実装する。

- Native Iteration Thread IDを記録する。
- `next()`内部でTest制御SignalまでBlockingする。
- `cancel()`／`close()`がIteration Thread以外から呼ばれた場合、`ValueError("generator already executing")`を送出する。

ProducerがNative `next()`中にConsumer Async GeneratorをCloseし、その後Native Boundaryを解放した。

結果：

- Async Generator CloseでCross-thread例外なし
- `cancel()` Thread ID = Producer Iteration Thread ID
- `close()` Thread ID = Producer Iteration Thread ID
- Sessionが2秒以内に終了
- `active_request_id is None`
- 未完了Producer Task 0件
- 直後の次Generationが`completed`

### 5.2 Timeout Safe Failure

Test内だけCleanup Timeoutを50msに短縮し、Native `next()`をBlockingした。

結果：

- Async Generator Closeは期待どおり`RuntimeError`
- Timeout時点のNative `cancel()`呼出し0件
- Timeout時点のNative `close()`呼出し0件
- Active Requestを解放済みと偽装しない
- Native Boundary解放後はProducer Thread上でCancel／Close
- Session／Gate解放後、次Generationが`completed`

既存のQueue Capacity `32`、96 Chunk、Consumer早期Close Regressionも引き続き合格した。

## 6. Verification

| Command | Exit Code | 結果 |
|---|---:|---|
| `./.venv/bin/ruff format --check src scripts tests` | 0 | 88 files already formatted |
| `./.venv/bin/ruff check src scripts tests` | 0 | All checks passed |
| `./.venv/bin/mypy .` | 0 | 88 source files、issue 0 |
| `./.venv/bin/python -m compileall -q src scripts tests` | 0 | 合格 |
| `./.venv/bin/pytest -q` | 0 | 213 passed、3 deselected |
| `./.venv/bin/pytest -q tests/unit/conversation tests/unit/web tests/integration/web` | 0 | 30 passed |
| `./.venv/bin/pytest -q -m model_smoke` | 0 | 2 passed、1 skipped、213 deselected |
| `uv lock --check --offline` | 0 | 122 packages resolved、Lock整合 |
| `bash -n scripts/setup/*.sh` | 0 | 合格 |

Model Smokeの1 Skipは`MARGPA_PHASE1F_PROFILE`未指定による既定のCross-environment Skipである。Mac Native GGUF／Metal対象2件は合格した。

## 7. Mac Manual Browser

実Qwen3-4B、Metal、`MARGPA_THINKING_MODE=enabled`、`127.0.0.1:8765`で確認した。

1. 長文Generation開始後にStop Buttonが有効になることを確認した。
2. Stop後、Statusは`生成を停止しました`、Sendは再有効、Stopは無効となった。
3. New Chat後、Messageは0件、Statusは`待機中`となった。
4. Stop／New Chat直後のGenerationが`完了 (stop)`まで到達した。
5. Browser Console Errorは0件だった。
6. Test ServerはApplication Shutdown完了を確認して終了した。

## 8. 未実行・Out of Scope

- Phase 1-H Summary Modeは未着手。
- Lightning Full Upload／Model Transferは未実行。
- Backend Contract／Thread-safe Native Stop Signalは変更していない。
- Phase 1完了宣言／Backup、Phase 1-ex、Git／GitHub公開は未着手。


<!-- SOURCE_END 92: docs/handoffs/implementer_status_phase_1g_cross_thread_cancel_follow_up_20260721150603.md -->

---

<!-- SOURCE_BEGIN 93: docs/handoffs/implementer_status_phase_1g_minimal_web_surface_20260721105005.md -->

### Source 93: `docs/handoffs/implementer_status_phase_1g_minimal_web_surface_20260721105005.md`

- History Target: `docs/project/phases/phase_1/history/handoffs/implementer_status_phase_1g_minimal_web_surface_20260721105005.md`
- Source SHA-512: `b711986bbd7847ea546baf407bb670fcac967a058bd72a00eae577dc10b8a54c54c063472f4a9cba887c72f7b82279a43b1cfc5e8ff9ec8736a7afad71744e01`
- Source Size: `15756` bytes

# 実装担当 Phase 1-G Minimal Web Surface Status

- 文書ID: `implementer_status_phase_1g_minimal_web_surface`
- 状態: `implementation_complete_waiting_designer_review`
- 作成日時: `2026-07-21 10:50:05 JST`
- 更新日時: `2026-07-21 10:50:05 JST`
- Snapshot: `20260721105005`
- 作成担当: 実装担当Task
- 正本言語: 日本語
- Documentation Index: [documentation_index_20260721093952.md](../history/documentation_index_20260721093952.md)
- Requirements: [phase_1g_minimal_web_surface_requirements_20260721093952.md](../history/requirements/phase_1g_minimal_web_surface_requirements_20260721093952.md)
- Architecture: [phase_1g_minimal_web_surface_architecture_20260721093952.md](../history/architecture/phase_1g_minimal_web_surface_architecture_20260721093952.md)
- ADR: [adr_0016_batch_lightning_upload_after_phase_1h_20260721093952.md](../history/adr/adr_0016_batch_lightning_upload_after_phase_1h_20260721093952.md)
- Implementer Handoff: [implementer_handoff_phase_1g_minimal_web_surface_20260721093952.md](../history/handoffs/implementer_handoff_phase_1g_minimal_web_surface_20260721093952.md)

## 1. Authorization／Scope

ユーザーの「最新Indexと、Handoff、他、中に記載のある関連文章を読んで作業」指示に基づき、Phase 1-G Minimal Web SurfaceだけをRepositoryへ実装し、Macで検証した。

Phase 1-H Summary Mode、Conversation永続化、React／Node、Lightning Full Upload／Dependency Install／Native Build／Model Transfer、Backup、Git、GitHub公開は実施していない。Canonical Requirements／Architecture／ADR／Roadmap／Indexは読み取り専用として扱い、既存文書を編集していない。

## 2. Implementation Summary

```text
Delivery Adapter       : FastAPI／Uvicorn
Frontend               : Local Vanilla HTML／CSS／JavaScript
Transport              : HTTP + Server-Sent Events
Conversation Ownership : Browser Tab Memory
Persistence            : None
Model Lifecycle         : LifespanごとにLoad 1回／Unload 1回
ASGI Worker             : 1
Concurrent Generation  : 1／Second Requestは409
Cancellation           : Stop API + Client Disconnect／Cooperative
Preview Access         : Server-side Basic Auth
Default Bind           : 127.0.0.1:8000
Rendering              : Plain Text／textContent
```

FastAPI固有型をInference／Presentation Domain Contractへ入れず、既存Model Port／llama.cpp AdapterのPublic Contractを変更していない。既存AdapterのNon-blocking Generation Lockを維持し、その外側へWeb Application用のActive Request GateとCancellation管理を追加した。

## 3. Changed Files

### Dependency／Config／Setup

- `pyproject.toml`
- `uv.lock`
- `config/application.toml`
- `scripts/setup/setup_macos_arm64_metal.sh`
- `scripts/setup/setup_lightning_linux_x86_64_cuda.sh`
- `scripts/models/phase1f_cross_environment_acceptance.py`

### Source

- `src/margpa_runtime_llm/bootstrap/web_application.py`
- `src/margpa_runtime_llm/entrypoints/web/__init__.py`
- `src/margpa_runtime_llm/entrypoints/web/main.py`
- `src/margpa_runtime_llm/modules/conversation/__init__.py`
- `src/margpa_runtime_llm/modules/conversation/contracts.py`
- `src/margpa_runtime_llm/modules/conversation/application/__init__.py`
- `src/margpa_runtime_llm/modules/conversation/application/conversation_generation.py`
- `src/margpa_runtime_llm/modules/conversation/public.py`
- `src/margpa_runtime_llm/modules/presentation/contracts/thinking.py`
- `src/margpa_runtime_llm/orchestration/response_language.py`
- `src/margpa_runtime_llm/web/__init__.py`
- `src/margpa_runtime_llm/web/app.py`
- `src/margpa_runtime_llm/web/auth.py`
- `src/margpa_runtime_llm/web/contracts.py`
- `src/margpa_runtime_llm/web/error_mapping.py`
- `src/margpa_runtime_llm/web/streaming.py`
- `src/margpa_runtime_llm/web/static/index.html`
- `src/margpa_runtime_llm/web/static/app.css`
- `src/margpa_runtime_llm/web/static/app.js`

### Tests

- `tests/unit/conversation/test_conversation_generation.py`
- `tests/unit/web/test_auth.py`
- `tests/unit/web/test_web_cli.py`
- `tests/integration/web/test_web_app.py`
- `tests/unit/presentation/test_thinking_presentation.py`
- `tests/unit/inference/test_cli.py`
- `tests/unit/inference/test_config_and_registry.py`
- `tests/integration/llama_cpp/test_phase1b_runtime.py`

### Status

- `docs/handoffs/implementer_status_phase_1g_minimal_web_surface_20260721105005.md`

## 4. Dependency／Lock／Setup

```text
Web Optional Extra
  fastapi==0.139.2
  uvicorn==0.51.0

Development Group
  httpx==0.28.1

Resolved Lock
  122 packages
```

`fastapi[standard]`、`uvicorn[standard]`、Jinja2、SSE専用Package、React、Node、CDN Dependencyは追加していない。

Mac／Lightning Setup Recipeへ`--extra web`を追加した。Web Dependency Syncと`llama-cpp-python` Native Buildの既存責務分離は維持し、今回のWeb同期では既存Metal版`llama-cpp-python`を再Install／再Buildしていない。

`requires-python = ">=3.12,<3.14"`を維持し、Mac 3.13.14／Lightning 3.12.11 Support Pairを変更していない。

## 5. Final CLI／Entrypoint

追加Entry Point：

```text
margpa-web
```

Option：

```text
--host HOST
--port PORT
--profile PROFILE_PATH
--registry MODEL_DEFINITION_PATH
--model-root MODEL_ROOT
--model-key MODEL_KEY
--context-size TOKENS
```

```text
Default Host : 127.0.0.1
Default Port : 8000
Reload       : Disabled
Workers      : 1／固定
```

既存`margpa-llm` Entry Point、`generate`、`model-info`を変更していない。Web EntrypointからCLI Private FunctionをImportしていない。

## 6. Final Endpoint／SSE Contract

```text
GET  /healthz                : Unauthenticated／{"status":"ok"} only
GET  /                       : Protected Minimal UI
GET  /assets/*               : Protected Local Static Asset
GET  /api/v1/runtime         : Protected Safe Runtime Metadata
POST /api/v1/chat/stream     : Protected Validated Conversation／SSE
POST /api/v1/chat/stop       : Protected Cooperative Cancellation
```

SSE Event：

```text
Non-terminal : start／delta／warning
Terminal     : completed／cancelled／errorのいずれか1回
```

`completed`はCanonical Final Assistant Message、Finish Reason、利用可能なToken Usageを返す。Visible Thinkingは現在画面用の`delta`だけに含め、Canonical Assistant Historyへ入れない。Hidden ThinkingはClient Payloadへ送らない。Streaming開始前のBusy／Context等はHTTP Error、開始後の安全なFailureはSSE `error`として返す。

## 7. Conversation／Config Boundary

Browserは`user／assistant`のCanonical Message列をTab Memory上で保持し、Requestごとに全列を送信する。ServerはConversation Historyを永続化せず、利用者間のHistoryを共有しない。

Validation：

```text
Allowed Role              : user／assistant
First／Final Role          : user
Role Order                : user／assistant交互
Max Messages              : 64
Max Characters／Message   : 32768
Max Total Characters      : 131072
Client system／tool Role  : Reject
Empty Message             : Reject
```

Request Overrideは次の3項目だけである。

```text
response.language                : ja／en／auto
generation.max_new_tokens        : Strict Integer／1～2048
presentation.thinking.visibility : hidden／visible
```

Effective ConfigをMemory上でCopyし、`config/application.toml`をRequestごとに変更しない。Visibility Overrideは`generation.thinking_mode`を変更しない。

## 8. Lifecycle／Concurrency／Cancellation

FastAPI Lifespan開始時にComposition Rootを1回実行し、Modelを1回Loadする。RequestおよびNew ChatではModelをReloadしない。ShutdownではActive GenerationへCancelを要求して終了を待ち、その後Modelを1回Unloadする。

同期llama.cpp Iteratorは専用Threadで消費し、Bounded Async Queueを通してSSEへ渡すため、ASGI Event LoopをGenerationでBlockしない。

```text
Conversation Gate acquire成功 → Generation開始
Conversation Gate busy        → HTTP 409／model_busy
Stop API                      → Active request_idへCancel Event
Client Disconnect            → Cooperative Cancel Event
Terminal／Error／Cancel       → Stream Close + Gate Release
Post-cancel                  → 次Generationを許可
```

Server Global Mutable StateはActive Generation Session 1件だけであり、Conversation Message列は保存しない。

## 9. Preview Access／Security

Environment Key名：

```text
MARGPA_WEB_AUTH_MODE=disabled|basic
MARGPA_WEB_AUTH_USERNAME
MARGPA_WEB_AUTH_PASSWORD
```

Credential値はSource、TOML、Docs、Log、HTML、API Responseへ記録していない。PolicyのRepresentationからもCredential Fieldを除外した。比較は`secrets.compare_digest`を使用する。

```text
Loopback + disabled                    : Start可能
Non-loopback + disabled                : Startup前にFail Closed
basic + Credential不足                 : Startup前にFail Closed
basic + Credentialあり                 : Server-side認証
/healthz                               : 例外として未認証
UI／Assets／全API                       : 同じ認証境界
Interactive API Docs／ReDoc／OpenAPI   : Disabled
```

Model OutputはDOM `textContent`で描画する。`innerHTML`、Markdown HTML Rendering、External CDN／Script／Fontを使用していない。`Cache-Control: no-store`、CSP、`nosniff`、`no-referrer`を付与する。Uvicorn Access Logは初期Entry Pointで無効化した。

Basic Authは少人数Preview Gateであり、本番Account／Role／Permission／Governance機能ではない。Non-loopback公開時のTLS終端は信頼できるReverse Proxy側の責務として維持する。

## 10. Thinking Presentation／Token Exhaustion

Default Display Labelを次へ変更した。

```text
旧 : 高度推論
新 : 推論過程
UI : 推論過程（モデル生成）
```

Canonical Protocol `<think>...</think>`とParser Contractは変更していない。UIには、表示SwitchがThinking実行のON／OFFではないこと、内容の正しさや真の内部思考を保証しないこと、Token上限、Raw Thinking非永続化を明示した。

`finish_reason=length`かつCanonical Finalが空の場合、空成功にせず次のWarning Code／Messageを返す。

```text
code    : final_answer_token_limit
message : 最終回答を生成する前にToken上限へ到達しました。
```

## 11. Automated Verification

### Dependency／Entrypoint

```text
uv lock                                           : Exit 0／122 packages
uv sync --frozen --extra web ...                  : Exit 0／Native llama-cpp再Buildなし
uv lock --check --offline                         : Exit 0／122 packages
python import fastapi, uvicorn, httpx              : Exit 0／0.139.2 0.51.0 0.28.1
margpa-web --help                                  : Exit 0
margpa-llm --help                                  : Exit 0
```

初回Sandbox内`uv lock`は共有uv CacheへのAccess制限でExit 2となった。Repository／Lock内容のFailureではないため、同一CommandをSandbox外で再実行しExit 0を確認した。

### Static／Default Gate

```text
ruff format --check src scripts tests             : Exit 0／88 files
ruff check src scripts tests                      : Exit 0
mypy .                                            : Exit 0／88 source files
python -m compileall -q src scripts tests         : Exit 0
bash -n Mac Setup／Lightning Setup／Preflight      : Exit 0
pytest -q                                         : Exit 0／209 passed、3 deselected
```

Targeted Conversation／Web Testの最終結果は`26 passed`である。初回Targeted Testでは、Credential Redaction TestのAssertion文字列が一般語`preview`と衝突して1件失敗した。Credential固有値を使うTestへ修正し、Production Codeを緩めず合格させた。

### Native Model Smoke

```text
pytest -q -m model_smoke／Sandbox外Metal : Exit 0
Result                                  : 2 passed、1 skipped、209 deselected
Skip                                    : Lightning Profile Environment未指定
```

Sandbox内の初回Native実行はMetal Deviceが`null`となりCommand Queueを作成できずExit 1だった。Verbose既存Smokeで同一原因を確認し、Source変更を行わずSandbox外のNative Metal条件で再実行して2件合格した。Model Artifact、Hash、Build Version、Runtime ContractのFailureではない。

## 12. Mac Manual Browser Smoke

実Model／Metalの`margpa-web --host 127.0.0.1 --port 8765`を起動し、終了時はGraceful Shutdown／Exit 0を確認した。

```text
UI表示／Local Asset                : Pass
Safe Runtime Status                : Pass／Model・Profile・gpu・metal
Default Max New Tokens             : Pass／2048
Default Thinking Visibility        : Pass／OFF
Japanese Streaming                 : Pass
Ephemeral Multi-turn               : Pass／直前回答を再利用
New Chat                           : Pass／Browser Current ChatのみReset
Response Language en               : Pass／English Response
Max New Tokens Request Override    : Pass／64
Thinking Visibility ON             : Pass／Execution Settingは変更なし
Stop                               : Pass／Generating中に停止
Post-cancel Generation             : Pass／停止後に再生成成功
Second Browser Tab Isolation       : Pass／新規空History
Browser Console Error／Warning     : None
Non-loopback + Auth Disabled       : Expected Exit 2／Fail Closed
```

Cancelled Generationの部分表示はCurrent Screenに残るが、Completed Assistant HistoryとしてBrowser Message列へ追加しない。停止後の次Requestは新しいCanonical Historyとして正常に生成できた。

## 13. Known Limits／Unexecuted

- ConversationはPage Reloadで失われる。
- Saved Chat、Resume、Delete、Title、Search、Regenerateは未実装である。
- Plain Text表示のみでMarkdown Renderingはない。
- 1 Process／1 Worker／1 Model Instanceである。
- Basic AuthはPreview用であり、User Account、OAuth／OIDC、Rate Limit、TLS終端を提供しない。
- CancelはNative Chunk境界でのCooperative方式であり、瞬時の強制停止を保証しない。
- Phase 1-H Summary ModeのUI Control／Config／Inferenceは未実装である。
- Lightning Full Upload、Dependency Sync、CUDA／CPU Native Gate、Live URL Testは未実行である。
- Phase 1-F Lightning Native GateはDeferred／Not Completeのままである。
- Phase 1完了、Backup、Phase 1-ex、Git／GitHub公開は未実行である。

## 14. Phase 1-H Interface

Phase 1-Hは、`ConversationGenerationService`が生成したCanonical Final AnswerとSSE `completed`境界の間へ、Application-level Summarization Portとして追加できる。

```text
Normal Generation
  → Thinking Normalize
  → Canonical Final Answer
  → Phase 1-H Summarization Port候補
  → Presentation／completed
```

Phase 1-G Web EntrypointからMain Modelを直接2回呼ぶ必要はない。Browser Historyへ戻すMessageは、Phase 1-H正本で決定される最終Canonical Outputに置換可能である。Current Active Generation Gate／Cancellationは、将来のNormal GenerationとSummary Generationを同一Sequential Sessionとして扱える境界を持つ。

## 15. Review Request

Phase 1-G Repository実装、Automated Gate、Mac Native Model Smoke、Manual Browser Smokeは完了候補である。設計者役にはRequirements／Architecture／Security／SSE Contract／Manual Evidenceと本StatusのReviewを依頼する。

Accepted Review前にPhase 1-Hへ着手せず、Lightning Full Uploadも行わない。

<!-- SOURCE_END 93: docs/handoffs/implementer_status_phase_1g_minimal_web_surface_20260721105005.md -->

---

<!-- SOURCE_BEGIN 94: docs/handoffs/implementer_status_phase_1g_review_follow_up_20260721121817.md -->

### Source 94: `docs/handoffs/implementer_status_phase_1g_review_follow_up_20260721121817.md`

- History Target: `docs/project/phases/phase_1/history/handoffs/implementer_status_phase_1g_review_follow_up_20260721121817.md`
- Source SHA-512: `a7b339be3f33e51b85d1f1d9d925fff937b33693783341a32a10e1610f05d3f8ff444917d5a923903fbe323bb381dca67cb299e1fa0c2584ad041a2955a29b1b`
- Source Size: `6021` bytes

# Phase 1-G Review Follow-up 実装担当Status

- 文書ID: `implementer_status_phase_1g_review_follow_up`
- 状態: `implementation_and_verification_completed`
- 作成日時: `2026-07-21 12:18:17 JST`
- Snapshot: `20260721121817`
- 作成担当: 実装者役担当Task
- 対象Review: `designer_review_phase_1g_minimal_web_surface_20260721115330.md`
- 対象Handoff: `implementer_handoff_phase_1g_review_follow_up_20260721115330.md`

## 1. 結果

Phase 1-G Reviewで指摘されたDisconnect／Backpressure Cleanup、Token Exhaustion UI、Public Namingを修正した。必須Static／Default／Mac Native Model／Manual Browser Gateは合格した。

Phase 1-Hには着手していない。

## 2. 変更Fileと責務

| File | 変更内容 |
|---|---|
| `src/margpa_runtime_llm/web/streaming.py` | Bounded SSE QueueのProducer停止通知、投入待ちPolling、Session Iterator明示Close、Native Stream Cancel、Producer終了待ち、Timeout時失敗化 |
| `src/margpa_runtime_llm/web/static/app.js` | Request単位の`final_answer_token_limit`保持、`completed`後のWarning維持、Safe Warning Bubble表示、Canonical History非追加 |
| `src/margpa_runtime_llm/web/static/index.html` | 公開通称を`Nazuna Research Governance LLM`へ統一 |
| `src/margpa_runtime_llm/__init__.py` | Package公開名を`Nazuna Research Governance LLM`へ統一 |
| `tests/integration/web/test_web_app.py` | Backpressure早期Close、Token Warning Event列／UI Policy、Public NamingのRegression Test追加 |
| `docs/handoffs/implementer_status_phase_1g_review_follow_up_20260721121817.md` | 本実装報告 |

Dependency変更はなく、`pyproject.toml`と`uv.lock`は変更していない。

## 3. Disconnect／Backpressure Cleanup

### 3.1 修正方式

- Queue Capacityは`32`のまま維持した。
- Consumer終了を`threading.Event`でBlocking Producerへ通知する。
- `run_coroutine_threadsafe(queue.put(...))`を50ms単位で確認し、Consumer終了時は待機FutureをCancelしてProducer Loopを抜ける。
- Client DisconnectまたはAsync Generator早期Closeでは、SessionへCancelを通知し、Native StreamをCancelする。
- Producer側`finally`でSession Iteratorを明示Closeし、Session `finally`とGeneration Gate解放を成立させる。
- QueueをDrainした後、Producer Taskを最大10秒待つ。Timeout時は再度Native Cancel／Drainして最大10秒待ち、なお終了しなければ成功扱いせず`RuntimeError`にする。

### 3.2 再現条件と解放Evidence

Regression Testでは96 Chunk（Queue Capacityの3倍）を生成し、Consumerは最初の`start`だけを取得した。Producerが33 Chunk以上を生成してQueue投入待ちへ入ったことを確認してからAsync GeneratorをCloseした。

限定時間内に次をAssertした。

- Native Fake Streamの`cancelled is True`
- `session.wait(2.0) is True`
- `active_request_id is None`
- 対象名の未完了Producer Taskが0件
- 直後の次Generationが`completed`

## 4. Token Exhaustion UI

ServerのEvent列が次の順序になるRegression Testを追加した。

```text
warning(code=final_answer_token_limit)
completed(assistant_message.content="")
```

Browserは対象WarningをRequest単位で保持し、直後の`completed`でStatusを上書きしない。Canonical Finalが空の場合はAssistant Bubbleへ次のSafe Warningを表示し、空Bubbleを残さない。

```text
最終回答を生成する前にToken上限へ到達しました。
```

Warning Textは`state.messages`のCanonical Assistant Historyへ追加しない。

## 5. Public Naming検索

次の範囲を検索した。

```text
src/
tests/
scripts/
config/
pyproject.toml
uv.lock
```

検索Patternは`<legacy-public-handle-pattern>`、結果は0件だった。`rg` Exit Code `1`は一致なしを示す期待結果である。Third-party Provenance等への機械的一括置換は行っていない。

## 6. Command Verification

| Command | Exit Code | 結果 |
|---|---:|---|
| `./.venv/bin/ruff format --check src scripts tests` | 0 | 88 files already formatted |
| `./.venv/bin/ruff check src scripts tests` | 0 | All checks passed |
| `./.venv/bin/mypy .` | 0 | 88 source files、issue 0 |
| `./.venv/bin/python -m compileall -q src scripts tests` | 0 | 合格 |
| `./.venv/bin/pytest -q` | 0 | 211 passed、3 deselected |
| `./.venv/bin/pytest -q tests/unit/conversation tests/unit/web tests/integration/web` | 0 | 28 passed |
| `./.venv/bin/pytest -q -m model_smoke` | 0 | 2 passed、1 skipped、211 deselected |
| `uv lock --check --offline` | 0 | 122 packages resolved、Lock整合 |
| `bash -n scripts/setup/*.sh` | 0 | 合格 |

Model Smokeの1 Skipは`MARGPA_PHASE1F_PROFILE`未指定による既定のCross-environment Skipである。Mac Native GGUF／Metal対象2件は合格した。

## 7. Mac Manual Browser Smoke

実Qwen3-4B、Metal、`MARGPA_THINKING_MODE=enabled`、`127.0.0.1:8765`で確認した。

1. `response_language=auto`、`max_new_tokens=256`でStreamingし、最終回答`OK.`、Status`完了 (stop)`を確認した。
2. Thinking有効、`max_new_tokens=1`で最終回答前Token Exhaustionを発生させた。StatusとAssistant Bubbleの双方へSafe Warningが残り、空Assistant Bubbleは0件だった。
3. Warning後にNew Chatし、`READY`を正常生成した。
4. 長文Generation中にStopし、Status`生成を停止しました`、Send再有効化、Stop無効化を確認した。
5. Stop後にNew Chatし、`AFTER-CANCEL`を正常生成した。
6. Browser Console Errorは0件だった。
7. Test ServerはApplication Shutdown完了を確認して終了した。

## 8. 未実行項目・Known Limit

- Phase 1-H Summary Modeは未着手。
- Lightning Full Upload／Model Transfer／Native Gateは未実行。
- Conversation永続化、Markdown Rendering、本格Auth、Governance／Guardrail／Judge／Repair／Agent／RAGは本Follow-upの対象外。
- Manual Browser SmokeはMac localhostの単一Browser Sessionで実施した。

<!-- SOURCE_END 94: docs/handoffs/implementer_status_phase_1g_review_follow_up_20260721121817.md -->

---

<!-- SOURCE_BEGIN 95: docs/handoffs/implementer_status_phase_1g_shutdown_cancel_follow_up_20260721172039.md -->

### Source 95: `docs/handoffs/implementer_status_phase_1g_shutdown_cancel_follow_up_20260721172039.md`

- History Target: `docs/project/phases/phase_1/history/handoffs/implementer_status_phase_1g_shutdown_cancel_follow_up_20260721172039.md`
- Source SHA-512: `479c3bba4699fc53350c4fedbb223082ad53f901fffdfcb242858eb3e0e3bb2faa9f35e809de7bd53841d122b220e92c7dc7455fe4603eb59968d0c0df4b1135`
- Source Size: `7718` bytes

# Phase 1-G Shutdown Cancel Follow-up 実装担当Status

- 文書ID: `implementer_status_phase_1g_shutdown_cancel_follow_up`
- 状態: `implementation_and_verification_completed`
- 作成日時: `2026-07-21 17:20:39 JST`
- Snapshot: `20260721172039`
- 作成担当: 実装者役担当Task
- 対象Review: `designer_review_phase_1g_cross_thread_cancel_follow_up_20260721164248.md`
- 対象Handoff: `implementer_handoff_phase_1g_shutdown_cancel_follow_up_20260721164248.md`

## 1. 結果

Phase 1-G Shutdown Cancel Follow-upを限定Scope内で完了した。

`ConversationGenerationService.shutdown()`のTimeout経路からCross-thread `force_cancel()`を除去した。Shutdown、SSE Consumer Closeともに`request_cancel()`を第一段とし、Native Cancel／CloseはProducer Iteration Thread上で実行する。

Runtime CloseはActive Sessionの終了を確認するまでModel Close Callbackを呼ばず、成功後は複数回CloseされてもCallbackを合計1回だけ呼ぶ。Lifespan Shutdown Failureは安全な固定Messageで記録し、抑制せず呼出元へ伝播する。

Phase 1-Hには着手していない。

## 2. 変更File

| File | 変更内容 |
|---|---|
| `src/margpa_runtime_llm/modules/conversation/application/conversation_generation.py` | Shutdown Timeout後の`session.force_cancel()`を除去し、Cooperative Cancel待ちの結果を返す |
| `src/margpa_runtime_llm/web/contracts.py` | Runtime CloseへTimeout引数、排他制御、成功後のIdempotencyを追加 |
| `src/margpa_runtime_llm/web/app.py` | Lifespan Shutdown Failureを安全な固定MessageでLogし、`RuntimeError`として再送出 |
| `tests/integration/web/test_web_app.py` | Active Generation Shutdown、Thread Affinity、Callback回数、Lifespan Failure VisibilityのRegression Testを追加 |
| `docs/handoffs/implementer_status_phase_1g_shutdown_cancel_follow_up_20260721172039.md` | 本実装報告 |

Backend Contract、llama.cpp Adapter、Dependency、`pyproject.toml`、`uv.lock`は変更していない。

## 3. Shutdown CancelとThread Boundary

```text
Shutdown Worker Thread
  conversation.shutdown(timeout)
    session.request_cancel()
    session.wait(timeout)
    ├─ Finished → True
    └─ Timeout  → False

Producer Iteration Thread
  Native next()の次Chunk境界
  Cancel要求を観測
  Native Stream cancel／close
  Session finally
  Generation Gate解放
```

`force_cancel()`のMethod定義自体は既存Sessionに残しているが、`src/margpa_runtime_llm/`内の汎用Lifecycleからの呼出しは0件である。

## 4. Timeout時のState

Active GenerationがTimeout内に終了しない場合：

- `ConversationGenerationService.shutdown()`は`False`を返す。
- `WebRuntime.close()`は`RuntimeError("The active generation did not stop during shutdown.")`を送出する。
- Active Sessionと`active_request_id`を解放済みと偽装しない。
- Model Close Callbackは呼ばない。
- Shutdown ThreadからNative `cancel()`／`close()`を呼ばない。

Native Boundary解放後はProducer ThreadがCancel／Closeを行い、SessionとGeneration Gateを解放する。その後のRuntime Closeは成功する。

## 5. Model Close Callback

`WebRuntime.close()`へLockと成功状態を追加した。

- Active Session Shutdown成功前：Callback 0回
- Session終了後の最初のRuntime Close：Callback 1回
- 2回目以降のRuntime Close：追加Callback 0回
- Regression Test最終合計：1回

## 6. Lifespan Failure Visibility

Shutdown TimeoutまたはModel Close Failureを無記録で抑制しない。

```text
The web runtime could not shut down cleanly.
```

Lifespanは上記固定MessageをOperator Logへ記録し、同じMessageの`RuntimeError`を例外連鎖なしで送出する。元のRaw Exception、Secret、Absolute PathはLogにも伝播例外にも含めない。

Regression Testでは、Close CallbackへPrivate TextとProject Absolute Pathを含む例外を注入し、次を確認した。

- Safe Logが1件記録される。
- Lifespan Exitが失敗として認識される。
- Raw Private TextはLogへ出ない。
- Project Absolute PathはLogへ出ない。

## 7. Regression Test

Thread-affine Blocking StreamをProducer Threadで消費中に、別Shutdown Threadから50ms Timeoutで`runtime.close()`を実行した。

### Timeout before Native Boundary

- Shutdown Resultは成功ではなく安全な`RuntimeError`
- Shutdown ThreadからNative `cancel()`呼出し0件
- Shutdown ThreadからNative `close()`呼出し0件
- Active Requestは維持
- Model Close Callback 0回

### Recovery after Native Boundary

- Native Boundary解放後のCancel Thread ID = Producer Iteration Thread ID
- Close Thread ID = Producer Iteration Thread ID
- Producer Threadは2秒以内に終了
- `active_request_id is None`
- 次Generationは`completed`
- Runtime Closeを2回実行してCallback合計1回

既存SSE Thread-affine／Backpressure／Cleanup Timeout Regressionも引き続き合格した。

## 8. Verification

| Command | Exit Code | 結果 |
|---|---:|---|
| `./.venv/bin/ruff format --check src scripts tests` | 0 | 88 files already formatted |
| `./.venv/bin/ruff check src scripts tests` | 0 | All checks passed |
| `./.venv/bin/mypy .` | 0 | 88 source files、issue 0 |
| `./.venv/bin/python -m compileall -q src scripts tests` | 0 | 合格 |
| `./.venv/bin/pytest -q` | 0 | 215 passed、3 deselected |
| `./.venv/bin/pytest -q tests/unit/conversation tests/unit/web tests/integration/web` | 0 | 32 passed |
| `./.venv/bin/pytest -q -m model_smoke` | 0 | 2 passed、1 skipped、215 deselected |
| `uv lock --check --offline` | 0 | 122 packages resolved、Lock整合 |
| `bash -n scripts/setup/*.sh` | 0 | 合格 |

Model Smokeの1 Skipは`MARGPA_PHASE1F_PROFILE`未指定による既定のCross-environment Skipである。Mac Native GGUF／Metal対象2件は合格した。

## 9. Native Model Smoke Host Resource

```text
Architecture      : arm64
Physical Memory   : 17179869184 bytes／16 GiB
VM Page Size      : 16384 bytes
Pages Free        : 4023
Pages Inactive    : 390661
Pages Speculative : 2602
Compressor Pages  : 96436 occupied
```

Smoke前に別MARGPA／llama／Uvicorn常駐は確認されなかった。設計者Reviewで発生した`Failed to create llama_context`は今回は再現せず、8.32秒で合格した。先行失敗の原因は未確定である。

## 10. Mac Manual Shutdown／Restart

実Qwen3-4B、Metal、`MARGPA_THINKING_MODE=enabled`、`127.0.0.1:8765`で確認した。

1. `max_new_tokens=2048`の長文Generationを開始し、Streaming中であることを確認した。
2. Active Generation中にServerへShutdownを要求した。
3. Uvicornは`Waiting for connections to close`となり、失敗を成功扱いせずConnection終了を待った。
4. Client Stop後、UIは`生成を停止しました`、ServerはApplication Shutdown完了まで到達した。
5. Shutdown Logに`ValueError: generator already executing`、Raw Exception、Model Close Failureはなかった。
6. 同一PortでServerを再起動し、Model Context作成とApplication Startupが成功した。
7. New Chat後、Message 0件／Status`待機中`を確認した。
8. Restart後の実Model Generationは`RESTARTED.`、Status`完了 (stop)`となった。
9. Browser Console Errorは0件だった。
10. 再起動ServerもApplication Shutdown完了を確認して終了した。

## 11. 未実行・Out of Scope

- Phase 1-H Summary Modeは未着手。
- Lightning Full Upload／Model Transferは未実行。
- Backend全体のThread-safe Stop Contractは新設していない。
- Phase 1完了宣言／Backup、Phase 1-ex、Git／GitHub公開は未着手。


<!-- SOURCE_END 95: docs/handoffs/implementer_status_phase_1g_shutdown_cancel_follow_up_20260721172039.md -->

---

<!-- SOURCE_BEGIN 96: docs/handoffs/implementer_status_phase_1h_review_follow_up_20260721183457.md -->

### Source 96: `docs/handoffs/implementer_status_phase_1h_review_follow_up_20260721183457.md`

- History Target: `docs/project/phases/phase_1/history/handoffs/implementer_status_phase_1h_review_follow_up_20260721183457.md`
- Source SHA-512: `1f3ab983ebcef752da48e4a191bd416c9cb901edfdf38470502814c409e2f5dc48af3d90e68ba16047944e781f7af68f13a7b5a8c10175839b3c39fc252d5a39`
- Source Size: `9460` bytes

# Phase 1-H Review Follow-up 実装者Status

- 更新時点: 2026-07-21 18:34:57 JST
- 担当: 実装者役担当Task
- 対象: Phase 1-H Review Follow-up 4 Mandatory Finding
- 状態: 限定修正・自動検証・Mac Metal Smoke・Browser確認 完了、設計者再Review待ち
- 正本取扱い: Index／Review／Handoff／Requirements／Architecture／ADRは読み取り専用

## 1. 結論

Follow-up Handoffで指定された4 Findingを、許可Scope内だけで修正した。

```text
Finding 1 Successful Summary SSE Privacy : Fixed
Finding 2 Long Silent SSE Keepalive       : Fixed
Finding 3 Summary Risk Notice             : Fixed
Finding 4 Runtime Error Relocalization     : Fixed
```

Config Schema、Summary Prompt、Model Adapter、CLI、Dependency、`pyproject.toml`、`uv.lock`は変更していない。

## 2. 変更File

- `src/margpa_runtime_llm/modules/conversation/application/conversation_generation.py`
- `src/margpa_runtime_llm/web/streaming.py`
- `src/margpa_runtime_llm/web/static/app.js`
- `src/margpa_runtime_llm/web/static/index.html`
- `tests/unit/conversation/test_conversation_generation.py`
- `tests/integration/web/test_web_app.py`
- `tests/integration/llama_cpp/test_phase1b_runtime.py`
- `docs/handoffs/implementer_status_phase_1h_review_follow_up_20260721183457.md`

`app.css`の追加変更は不要だった。

## 3. Finding 1：Successful Summary SSE Data Minimization

### 3.1 修正内容

Summary成功時のPublic SSEから次を削除した。

```text
original_assistant_message
summary_assistant_message
presented_source
original_usage
summary_usage
```

Original canonical answerは`ConversationGenerationSession`内のLocal ArtifactとしてSummary生成とfallback判断にだけ使用する。Clientへ別Fieldで返さず、永続保存もしない。

### 3.2 Success Payload

```json
{
  "request_id": "turn-id",
  "finish_reason": "stop",
  "assistant_message": {
    "role": "assistant",
    "content": "Short summary"
  },
  "usage": null,
  "transformation": {
    "summary_mode": "post_generation",
    "summary_applied": true,
    "fallback_used": false,
    "original_finish_reason": "stop",
    "summary_finish_reason": "stop"
  }
}
```

回答本文は`assistant_message`のPresented Summaryだけである。`transformation`は本文を含まない状態Metadataである。

### 3.3 Fallback Payload

```json
{
  "request_id": "turn-id",
  "finish_reason": "stop",
  "assistant_message": {
    "role": "assistant",
    "content": "Original answer"
  },
  "usage": null,
  "transformation": {
    "summary_mode": "post_generation",
    "summary_applied": false,
    "fallback_used": true,
    "original_finish_reason": "stop",
    "summary_finish_reason": null
  }
}
```

FallbackではOriginalがPresented Answerなので`assistant_message`として返すが、別Fieldへ重複させない。不完全Summary本文は送らない。

### 3.4 Test Evidence

- Unit: Summary成功Event全体に`Long original answer`が存在しない。
- Web Integration: Raw SSE Response全体に`Original answer`、Original Thinking、Summary Thinkingが存在しない。
- Web Integration: `original_assistant_message`／`summary_assistant_message` Keyが存在しない。
- Web Integration: Summaryは`assistant_message`として存在し、`summary_applied=true`、`fallback_used=false`。
- Fallback Integration: Originalの`assistant_message` Payloadは1個、不完全Summaryは0、`fallback_used=true`。

## 4. Finding 2：SSE Keepalive

### 4.1 固定Contract

```text
Interval    : 15.0 seconds
Wire Format : : keepalive\n\n
SSE Type    : Comment
event/data  : None
```

`SSE_KEEPALIVE_INTERVAL_SECONDS = 15.0`と`SSE_KEEPALIVE_COMMENT = ": keepalive\n\n"`を`web/streaming.py`へ追加した。

### 4.2 Lifecycle

- Async Consumer側だけでIdle時間を計測する。
- Application Event送信時にIdle Timerをresetする。
- 15秒Application Eventがない場合だけCommentをyieldする。
- Normal Hidden Generation／Summary Buffered Generationの両段階で動作する。
- Conversation Event Queueへ積まない。
- Terminal item受信後はKeepaliveを送らない。
- Consumer終了時は既存`finally`でcooperative cancel、Queue drain、producer joinを行う。
- Heartbeat専用Task／Threadは作らないためCleanup対象を増やさない。
- CommentへRequest ID、Prompt、Exception等を含めない。

### 4.3 Regression Test

- Default Interval `15.0`とWire Formatを固定Test。
- Intervalだけ`0.01`へmonkeypatchし、実時間15秒を待たず確認。
- Blocking Normal Generation中にKeepaliveを確認。
- Buffered Summary Generation中にKeepaliveを確認。
- Keepalive後も通常Event／completedを受信。
- completed countは1回。
- Keepaliveに`event:`／`data:`がない。
- Keepalive後のconsumer closeでproducer-thread native cancel／closeを確認。
- Cleanup後に`margpa-sse-producer-*` Taskが残らない。
- Existing backpressure／disconnect／cleanup timeout／shutdown Testも継続合格。

## 5. Finding 3：Summary Risk Notice

### 5.1 日本語

```text
ONでは通常回答の完了後に同じModelで要約します。
処理時間とToken使用量が増え、要約により詳細、前提、注意事項等が省略・変形される可能性があります。
```

### 5.2 English

```text
When ON, the completed answer is summarized by the same model.
This increases latency and token usage, and details, assumptions, or cautions may be omitted or altered by the summary.
```

Initial HTMLとTranslation Dictionaryを同義内容へ更新した。品質／正確性保証は追加していない。既存Layout／CSS変更は不要だった。Static Testで日英のRisk表現を固定した。

## 6. Finding 4：Runtime Status Relocalization

### 6.1 State

Render済みError文字列を`runtimeText`へ保持する方式を廃止し、次のStable Stateへ変更した。

```text
loading:
  kind           = loading
  translationKey = runtimeLoading
  text           = null

metadata:
  kind           = metadata
  translationKey = null
  text           = opaque Model／Profile／Device Metadata

known_error:
  kind           = known_error
  translationKey = runtimeLoadFailed
  text           = null
```

`renderRuntimeStatus()`を追加し、`applyTranslations()`から常に呼ぶ。Metadata成功時だけOpaque Textをそのまま表示し、Loading／Known Failureは現在のUI Languageで毎回解決する。

### 6.2 Evidence

Source Contract Test:

- `runtimeText`が存在しない。
- `runtimeStatus.kind=loading`、`known_error`、`runtimeLoadFailed`を確認。
- `renderRuntimeStatus()`を確認。

Mac BrowserでRuntime APIを意図的に500へした確認:

```text
ja : Runtime情報を取得できませんでした。
en : Could not load runtime information.
ja : Runtime情報を取得できませんでした。
```

同じ切替でSummary Risk Noticeも日英へ再描画された。Response Language値は変更していない。

## 7. Verification

```text
./.venv/bin/ruff format --check src scripts tests
  Exit 0／93 files already formatted

./.venv/bin/ruff check src scripts tests
  Exit 0／All checks passed

./.venv/bin/mypy .
  Exit 0／93 source files、no issues

./.venv/bin/python -m compileall -q src scripts tests
  Exit 0

node --check src/margpa_runtime_llm/web/static/app.js
  Exit 0

./.venv/bin/pytest -q
  Exit 0／246 passed、3 deselected

./.venv/bin/pytest -q tests/unit/conversation tests/unit/summarization tests/integration/web
  Exit 0／51 passed

./.venv/bin/pytest -q -m model_smoke
  Exit 0／2 passed、1 skipped、246 deselected

uv lock --check --offline
  Exit 0／Resolved 122 packages

bash -n scripts/setup/setup_macos_arm64_metal.sh \
  scripts/setup/setup_lightning_linux_x86_64_cuda.sh \
  scripts/setup/preflight_lightning_ai_studio.sh
  Exit 0
```

Model SmokeのSkip 1件は`MARGPA_PHASE1F_PROFILE`未設定のPhase 1-F cross-environment Testであり、Phase 1-H Follow-up blockerではない。

## 8. Manual Browser／Raw SSE確認

- Runtime Failure後の`ja → en → ja`: Pass。
- Summary Risk Noticeの日英表示: Pass。
- UI LanguageとResponse LanguageのState分離: 維持。
- Summary SuccessのRaw SSE Original非送信: Deterministic ASGI Integration TestでResponse Bodyを直接検査しPass。
- Summary FallbackのOriginal表示Contract: Deterministic ASGI Integration TestでPass。
- Mac Metal Summary ON: model_smokeでPass。
- Stop／New Chat／Reload: 既存Browser／Integration Testが継続合格。

Browser DevToolsを用いた実Model SSE本文の再検査は行っていない。代わりに、Raw SSE Bodyの完全一致を可能にするASGI Integration TestとMac Metal実Model Pipeline Testを分離して実行した。

## 9. Optional Improvement

Summary StageのBroad `except Exception`へのOperator Log追加は実施していない。4 Mandatory Findingの修正Scopeを優先し、Client安全性／fallback動作は変更していない。

## 10. 非実施／境界

- Lightning Upload／Model Transfer／Cloud実行: 未実施
- Phase 1完了宣言／Backup: 未実施
- Phase 1-ex: 未着手
- Git初期化／Commit／Push／GitHub公開: 未実施
- Config Schema／Summary Prompt／Token値変更: 未実施
- Model Adapter／CLI／Dependency変更: 未実施
- Public Docs更新: 未実施

Phase 1-H Follow-upの受入判断は設計者再Reviewへ戻す。

<!-- SOURCE_END 96: docs/handoffs/implementer_status_phase_1h_review_follow_up_20260721183457.md -->

---

<!-- SOURCE_BEGIN 97: docs/handoffs/implementer_status_phase_1h_summary_mode_and_ui_language_20260721181202.md -->

### Source 97: `docs/handoffs/implementer_status_phase_1h_summary_mode_and_ui_language_20260721181202.md`

- History Target: `docs/project/phases/phase_1/history/handoffs/implementer_status_phase_1h_summary_mode_and_ui_language_20260721181202.md`
- Source SHA-512: `f4581a92edbb36c0be33c30f518d021685dbdf802665a3fbf2a4fa8de48d1e6d4d3398cd16ac84a6674511a83ad05b38fe8837615908b730046748c82a61e849`
- Source Size: `11082` bytes

# Phase 1-H 実装者Status — Summary Mode and UI Language

- 更新時点: 2026-07-21 18:12:02 JST
- 担当: 実装者役担当Task
- 対象: Phase 1-H Summary Mode／UI Language
- 状態: 実装・自動検証・Mac Metal実Model検証・Browser手動検証 完了、設計者Review待ち
- 正本取扱い: Requirements／Architecture／Governance／ADR／Index／Designer Handoffは読み取り専用

## 1. 実施Scope

Phase 1-GのConversation／Web Runtimeを維持したまま、次を実装した。

- Summary Mode `off | post_generation`
- 同一Main Modelによる通常回答→要約の直列2段Pipeline
- Summary失敗時のOriginal Answer fallback
- Application Config schema `2` → `3`
- Runtime DefaultsへのSummary Mode追加
- 日本語／英語のBrowser-only UI切替
- UI Languageの専用localStorage保持
- Summary／UI LanguageのUnit・Integration・実Model Test

後続Phase、Lightning upload、Model転送、Backup、Git／GitHub作業には進んでいない。

## 2. 変更File

### Runtime／Config

- `config/application.toml`
- `src/margpa_runtime_llm/bootstrap/config_loader.py`
- `src/margpa_runtime_llm/bootstrap/web_application.py`
- `src/margpa_runtime_llm/modules/conversation/contracts.py`
- `src/margpa_runtime_llm/modules/conversation/application/conversation_generation.py`
- `src/margpa_runtime_llm/modules/conversation/public.py`
- `src/margpa_runtime_llm/modules/summarization/__init__.py`
- `src/margpa_runtime_llm/modules/summarization/contracts.py`
- `src/margpa_runtime_llm/modules/summarization/public.py`
- `src/margpa_runtime_llm/orchestration/summarization.py`
- `src/margpa_runtime_llm/web/contracts.py`
- `src/margpa_runtime_llm/web/static/index.html`
- `src/margpa_runtime_llm/web/static/app.css`
- `src/margpa_runtime_llm/web/static/app.js`

### Test

- `tests/unit/conversation/test_conversation_generation.py`
- `tests/unit/summarization/test_summary_contract.py`
- `tests/unit/inference/test_config_and_registry.py`
- `tests/unit/inference/test_cli.py`
- `tests/integration/web/test_web_app.py`
- `tests/integration/llama_cpp/test_phase1b_runtime.py`

新規Dependency、`pyproject.toml`、`uv.lock`、CLI Contractの変更はない。

## 3. Directory／Contract

- `modules/summarization/`を新設し、Summary Mode、Backend、Failure Policy、Application-owned Configを型Contract化した。
- `orchestration/summarization.py`がserver-owned Summary Promptを構成する。
- Browser／FastAPIからInferenceを2回直接呼ばず、`ConversationGenerationService`配下の1 Sessionだけが2段処理を統治する。
- `ConversationEventType.STATUS`を追加した。
- `ConversationSettings.summary_mode`を追加した。
- `RuntimeDefaults.summary_mode`を追加した。
- OFF時のSSE順序は `start → delta* → warning* → completed` のまま維持した。

## 4. Config Migration

`config/application.toml`をschema `3`へ更新し、次を追加した。

```toml
[layers.summarization]
mode = "off"
backend = "main_model"
max_new_tokens = 1024
thinking_mode = "disabled"
preserve_original = true
failure_policy = "fallback_original"
```

- Deployment Profile schemaは変更していない。
- `max_new_tokens`は`1024`固定。
- Main Model以外、Thinking有効、Original非保持、非fallback policy、未知Fieldを拒否する。
- 旧Application schema `2`は暗黙受理しない。
- Runtime APIはApplication Configのdefault Summary Modeを返す。

## 5. Summary Prompt Boundary

Summary Requestへ渡すSourceは、Thinking Parser通過後のOriginal canonical final answerだけである。

- 渡さない: 通常生成のThinking、会話履歴、元System Prompt、User Prompt、Path、Credential、Runtime内部状態
- Server System Message: Sourceを命令ではなくuntrusted dataとして扱い、事実・結論・制約・警告・否定・Code・数値を保持し、追加主張を禁止
- User Message: `{"source_answer": ...}`のJSON data value
- `ja`: 日本語要約
- `en`: 英語要約
- `auto`: Sourceの主言語を維持
- Summary raw outputにもThinking Parserを適用し、Reasoningは表示・履歴へ出さない

Prompt injection境界、JSON escape、3種類のResponse LanguageはUnit Testで固定した。

## 6. Model Call／Sequential性

### OFF

- Main Model call: 1回
- 既存Generation Parameter、Thinking Visibility、表示／canonical分離を維持

### ON

- Main Model call: 2回
- 1回目: User指定の`max_new_tokens`（上限2048）で通常回答
- 2回目: `max_new_tokens=1024`、`thinking_mode=disabled`でSummary
- 同一`model_key`を使用
- 通常StreamをContext Managerでcloseした後にSummary Streamを生成
- 2 Stream同時Openなし
- 親Sessionが通常生成開始からSummary／fallback／cancel terminalまでGeneration Gateを保持
- Stream生成、Iteration、native cancel／closeはproducer thread側

Unit／Web Integration Testでcall count、request order、Parameter、message boundary、両Stream closeを確認した。Mac Metal実Model TestでもSummary ONが`presented_source=summary`で完了した。

## 7. Fallback Matrix

次は`summary_fallback_original` warning後、Original canonical answerを`assistant_message`として完了する。

| 条件 | 動作 |
|---|---|
| Summary Inference Error／Context Limit | Originalへfallback |
| Summary empty／whitespace final | Originalへfallback |
| Summary Thinking Parser failure／unclosed protocol | Originalへfallback |
| Summary `finish_reason=length` | 不完全Summaryを表示せずOriginalへfallback |
| Summary terminal chunk欠落／不整合 | 不完全Summaryを表示せずOriginalへfallback |
| Original canonical finalがempty／whitespace | Summary callせずOriginalへfallback |

- Original／Summary／PresentedはONのcompleted payloadで別Fieldとして保持する。
- Browser履歴へ入るのは`assistant_message`、つまりPresentedだけ。
- 不完全Summary deltaはbufferし、validity確定前には送らない。
- Summary failureの内部例外詳細はBrowserへ出さない。
- Original側warningはSummary成功／fallbackのどちらでもterminal前に維持する。

Cancelはfallbackではない。通常生成中、段間、Summary中のcancelはいずれも`cancelled` terminalとなり、assistant historyを作らない。

## 8. SSE Order

### Summary OFF

```text
start(state=generating)
delta*
warning*
completed
```

### Summary ON成功

```text
start(state=generating_answer)
[normal generation: hidden]
status(state=summarizing_answer)
[summary generation: buffered]
delta(valid summary)
warning*
completed
```

### Summary ON fallback

```text
start(state=generating_answer)
[normal generation: hidden]
status(state=summarizing_answer)
delta(original canonical answer, if non-empty)
original warning*
warning(code=summary_fallback_original)
completed(presented_source=original)
```

各経路のterminal eventは1回だけである。

## 9. Cancel／Shutdown Boundary

- Phase 1-Gのcooperative cancelを維持した。
- HTTP disconnect／Stop／Shutdown workerはcancel flagだけを設定する。
- producer threadが次のchunk boundaryで同じthread上からnative `cancel()`／`close()`を行う。
- Summary中cancelのThread-affine Integration Testを追加し、fallback／completedを出さないことを確認した。
- Summary段間cancelでは2回目のModel callを開始しない。
- Session終了時にGateを解放し、後続Generationが可能。
- `WebRuntime.close()`のidempotent closeとtimeout boundaryを既存Testで回帰確認した。
- `force_cancel`の呼出しはRuntime source内0件のまま。

## 10. UI Language／Storage

- Header右上に`日本語 | English`を追加した。
- defaultは日本語。
- Browser-only translation dictionaryを使用し、外部CDN／i18n Dependencyは追加していない。
- 翻訳対象: `document.title`、`html lang`、Button、Label、Placeholder、Status、既知Warning／Error、ARIA、Empty／New Chat、Settings、Response Language option label。
- Response Language value `ja | en | auto`は不変で、UI Languageから独立。
- Model output／Thinkingは翻訳しない。
- 既知Warning／Errorはcodeで翻訳し、未知codeはserver safe textまたはgeneric safe textを使用。
- DOM更新は`textContent`のみで、`innerHTML`は使用しない。
- localStorage keyは`margpa.ui_language.v1`のみ。
- 保存値は`ja | en`のみ。invalid／storage unavailableは`ja`へfallback。
- Chat、Prompt、Credential、Model output、Response Languageは保存しない。
- New ChatはUI Languageを維持し、Reloadで復元する。

Browser手動確認:

- 日本語→英語: title、`html lang`、Button、Label、Placeholder、ARIA、option labelが英語化
- UI English＋Response Language `en`＋Summary ONを独立設定可能
- New Chat後もEnglish維持
- Reload後もEnglish復元
- 390×844 viewportでLanguage SwitcherとNew Chatの重なりなし
- 横overflowなし

## 11. Verification Result

### Static／Unit／Integration

```text
./.venv/bin/ruff format --check src scripts tests
  PASS: 93 files already formatted

./.venv/bin/ruff check src scripts tests
  PASS: All checks passed

./.venv/bin/mypy .
  PASS: 93 source files, no issues

./.venv/bin/python -m compileall -q src scripts tests
  PASS

./.venv/bin/pytest -q
  PASS: 242 passed, 3 deselected

./.venv/bin/pytest -q tests/unit/conversation tests/unit/summarization tests/integration/web
  PASS: 47 passed

node --check src/margpa_runtime_llm/web/static/app.js
  PASS

uv lock --check --offline
  PASS: Resolved 122 packages

bash -n scripts/setup/setup_macos_arm64_metal.sh \
  scripts/setup/setup_lightning_linux_x86_64_cuda.sh \
  scripts/setup/preflight_lightning_ai_studio.sh
  PASS
```

### Mac Metal／実Model

```text
./.venv/bin/pytest -q -m model_smoke
  PASS (Mac Metal直接実行): 2 passed, 1 skipped, 241 deselected
```

補足:

- Sandbox内の初回実行はMetal `llama_context`を作成できず、Model Load前に既存2 Smokeが失敗した。
- 同一CommandをMac Metal直接Accessで再実行し、既存SmokeとPhase 1-H実Model Summary ONがともに通過した。
- Skip 1件は`MARGPA_PHASE1F_PROFILE`未設定のPhase 1-F cross-environment smokeであり、Phase 1-H blockerではない。

## 12. 未解決／Review観点

- Phase 1-H実装上の既知blockerなし。
- UI manualはlocal fake Runtime metadataで表示・操作を確認し、Generation pipelineはASGI IntegrationとMac Metal実Model Testで別途確認した。
- Lightning native executionはPhase 1-Fの扱いどおりdeferred。Upload／Model転送は実施していない。
- 設計者には、ON completed payloadのOriginal／Summary／Presented分離、fallback event order、Application schema 3、Browser-only i18n境界を重点Reviewしてほしい。

## 13. 非実施

- Phase 1完了宣言
- Phase 1-Ex／後続Phase着手
- Backup／Release作業
- Git初期化、Commit、Push、PR
- Lightning upload、Model transfer、Cloud実行
- Public Docs更新

<!-- SOURCE_END 97: docs/handoffs/implementer_status_phase_1h_summary_mode_and_ui_language_20260721181202.md -->

---

<!-- SOURCE_BEGIN 98: docs/handoffs/implementer_status_phase_1i_web_presentation_and_ux_follow_up_20260725203508.md -->

### Source 98: `docs/handoffs/implementer_status_phase_1i_web_presentation_and_ux_follow_up_20260725203508.md`

- History Target: `docs/project/phases/phase_1/history/handoffs/implementer_status_phase_1i_web_presentation_and_ux_follow_up_20260725203508.md`
- Source SHA-512: `1556816379e8a2e78ded421af37ce2015b680b64742f87078868c13634305b3c4b4a8b0d16b62f9617f25829e53fb95e12590246a36bec098959067f5d8e836c`
- Source Size: `5961` bytes

# Phase 1-I Web Presentation／UX Follow-up 実装者Status

- 文書ID: `implementer_status_phase_1i_web_presentation_and_ux_follow_up`
- 状態: `repository_implementation_completed_native_and_manual_acceptance_pending`
- 作成日時: `2026-07-25 20:35:08 JST`
- 更新日時: `2026-07-25 20:35:08 JST`
- Snapshot: `20260725203508`
- 作成担当: 実装者役担当Task
- 対象Handoff: [designer_handoff_phase_1i_web_presentation_and_ux_follow_up_20260725200001.md](../history/handoffs/designer_handoff_phase_1i_web_presentation_and_ux_follow_up_20260725200001.md)

## 1. Result

Phase 1-IのRepository実装と自動Testを完了した。

```text
Thinking Generation : disabled／enabled
Thinking Visibility : hidden／visible
SSE Delta Channel   : reasoning／final
Reasoning DOM        : Ephemeral Plain Text
Final Streaming     : Plain Text
Final Completion    : Allowlist DOM Markdown
Copy Source         : Canonical Text
Runtime CDN         : none
Third-party追加     : none
```

ユーザー指定のまとめManual Acceptanceと実Model Thinking ON／OFF Native Testは実施していない。

## 2. Changed Files

### Runtime／Contract

- `src/margpa_runtime_llm/modules/conversation/contracts.py`
- `src/margpa_runtime_llm/modules/conversation/public.py`
- `src/margpa_runtime_llm/modules/conversation/application/conversation_generation.py`
- `src/margpa_runtime_llm/modules/presentation/contracts/thinking.py`
- `src/margpa_runtime_llm/modules/presentation/application/thinking_presentation_service.py`
- `src/margpa_runtime_llm/modules/presentation/public.py`
- `src/margpa_runtime_llm/web/contracts.py`
- `src/margpa_runtime_llm/bootstrap/web_application.py`

### Static Web

- `src/margpa_runtime_llm/web/static/index.html`
- `src/margpa_runtime_llm/web/static/app.js`
- `src/margpa_runtime_llm/web/static/app.css`
- `src/margpa_runtime_llm/web/static/safe_markdown.js`

### Test

- `tests/unit/conversation/test_conversation_generation.py`
- `tests/unit/web/test_safe_markdown.py`
- `tests/unit/web/safe_markdown.test.mjs`
- `tests/integration/web/test_web_app.py`

## 3. Contract Implementation

### Thinking

- `ConversationSettings.thinking_mode`を追加した。
- Webでは`disabled`／`enabled`だけを許可し、`model_default`とUnknown ValueをValidation Errorにする。
- Explicit Web Settingを`GenerationParameters.thinking_mode`へ適用する。
- Runtime Snapshotへ`thinking_mode`と`thinking_control_available`を追加した。
- Thinking Control CapabilityがないModelへのEnable Requestは`unsupported_capability`でFail Closedにする。
- Generation OFF時はVisibilityをServer側でもHiddenへ正規化する。
- Summary Stageは既存どおりThinking Disabled／Visibility Hiddenを固定した。

### SSE／Canonical Boundary

- Delta Payloadへ`channel=reasoning|final`を追加した。
- Visibility Hidden時はReasoning DeltaをClientへ送らない。
- BrowserはPresentation Tag／Display LabelをParseしない。
- Completion Eventの`assistant_message.content`はCanonical Finalだけを維持する。
- ReasoningはCompletion、Browser History、次Turn、Copyへ混入しない。

### Web UX

- Thinking GenerationとThinking Visibilityを別Controlにした。
- Generation OFFまたはCapability Unavailable時はVisibilityをDisabledにする。
- Assistant Thinking／Finalを別DOM Regionにした。
- Shortcut Hintを日本語／英語で表示し、HandlerへIME Composition Checkを追加した。
- User Messageと完了済みAssistant FinalへCopy Buttonを追加した。
- Clipboardは`writeText`だけを使い、Copy元はClosureで保持するCanonical Textに固定した。
- Copy成功／失敗Feedbackを日本語／英語で表示する。

## 4. Markdown Security

第三者Dependencyは追加せず、Repository-localのAllowlist Parser／DOM Builderを実装した。

- `innerHTML`不使用
- `document.createElement`／`createTextNode`によるDOM Construction
- Raw HTMLはExecutable DOMにせずPlain Textとして保持
- `javascript:`、`data:`、`vbscript:`、Control Character、Protocol-relative URLを拒否
- External HTTP(S) Linkへ`target="_blank"`と`rel="noopener noreferrer"`を設定
- Streaming中はPlain Text
- Completion後だけCanonical FinalをRender
- Parser Failure時はCanonical Plain TextへFallbackし、UIへ明示

初期対応：

- Heading
- Paragraph
- Unordered／Ordered List
- Emphasis／Strong
- Inline Code
- Fenced Code Block
- Block Quote
- Link
- Horizontal Rule

Tableは未対応であり、Plain Text相当として扱う。

## 5. Verification

実行結果：

```text
pytest                    : 265 passed, 3 deselected
Ruff check                : passed
Ruff format --check       : passed
Mypy strict               : passed / 95 source files
uv lock --check           : passed / 122 packages
Node Markdown security    : 5 passed
Shell syntax              : passed
```

自動Testで確認したもの：

- Thinking Generation／Visibility 4組合せ
- Hidden Reasoning非送信
- Visible Reasoning／Final Channel分離
- Unknown Thinking Mode拒否
- Capability Unavailable拒否
- Summary Thinking Disabled
- Canonical Final維持
- XSS／Raw HTML／Event Handler Inert化
- Dangerous URL拒否
- External Link属性
- Malformed Fence Plain Text Fallback Hook
- Copy Canonical Source／Clipboard Read不使用
- Shortcut Hint／IME Check
- Existing Stop／Summary／Language／SSE Keepalive Regression

## 6. Pending

- 実Qwen3でのThinking Generation ON／OFF Native Test
- User指定のまとめManual Acceptance
- Browser実操作による4組合せ、Copy、Markdown、Shortcut確認

上記をCompletedとは記録しない。

## 7. Boundary

- Model Port、llama.cpp Adapter、Deployment Profile、RAG、StorageはPhase 1-Iとして変更していない。
- Dependency Version、`pyproject.toml`、`uv.lock`は変更していない。
- External CDN、External Service、Clipboard Readは追加していない。


<!-- SOURCE_END 98: docs/handoffs/implementer_status_phase_1i_web_presentation_and_ux_follow_up_20260725203508.md -->

---

<!-- SOURCE_BEGIN 99: docs/handoffs/public_documentation_handoff_20260718174637.md -->

### Source 99: `docs/handoffs/public_documentation_handoff_20260718174637.md`

- History Target: `docs/project/phases/phase_1/history/handoffs/public_documentation_handoff_20260718174637.md`
- Source SHA-512: `aa86772e8f7f7ddbd374324a629fedf7b30a11d41a4a55677cb2313d50b9b82c44700f6494ac873914c68c7f9889e93904b3f4f93d0f0b93fa48bd2d35d8130f`
- Source Size: `2305` bytes

# 対外向けDocs作成者役 引き継ぎ

- 文書ID: `public_documentation_handoff`
- 状態: `waiting_for_publication_phase`
- 作成日時: `2026-07-18 17:46:37 JST`
- 更新日時: `2026-07-18 17:46:37 JST`
- 対象: 将来の対外向けDocs作成者役担当タスク
- 正本言語: 日本語
- 共通引き継ぎ: [common_project_handoff_20260718174637.md](../history/handoffs/common_project_handoff_20260718174637.md)

## 1. 役割

- GitHub README
- Setup
- Architecture説明
- Runtime Governance説明
- Model Download手順
- Model配置手順
- Audit Log仕様
- SHA-512検証手順
- Sample Config説明
- License／Attribution
- 匿名化Sample Log

## 2. 言語方針

日本語を正本とする。

技術識別子、Model ID、License正式名称等だけ英語を保持する。

英語資料を参照する場合も、日本語で意味を説明し、元資料へのLinkを付ける。

英語版が必要になった場合は、日本語正本から派生させる。

## 3. 公開しないもの

- Model Binary
- 実会話Log
- Personal Information
- RAG投入資料
- API Key
- Cloud Credential
- Secret Key
- User固有絶対Path
- 内部機密情報

## 4. Model公開情報

Model本体はGitHubへ含めない。

掲載するもの：

- Model ID
- Distribution
- Upstream
- File名
- Quantization
- Download URL
- Placement
- Revision／Commit
- Hash検証
- License

## 5. Attribution

ARGD／DAGD：

```text
Author  : Nazuna Research
License : CC-BY-SA-4.0
```

ModelごとのLicenseとThird-Party Noticeを確認する。

SeleneはLlama 3.1由来。GuardとJudgeのGGUFは第三者変換としてDistributionとUpstreamを併記する。

## 6. 必読

- [project_requirements_20260718174637.md](../history/requirements/project_requirements_20260718174637.md)
- [model_strategy_20260718174637.md](../history/architecture/model_strategy_20260718174637.md)
- [runtime_governance_20260718174637.md](../history/governance/runtime_governance_20260718174637.md)
- [audit_evaluation_security_20260718174637.md](../history/governance/audit_evaluation_security_20260718174637.md)
- [documentation_rules_20260718174637.md](../history/requirements/documentation_rules_20260718174637.md)

## 7. 注意

公開／非公開、Repository License、Release形式はまだ未決定。公開操作はユーザーの明示指示後に行う。

<!-- SOURCE_END 99: docs/handoffs/public_documentation_handoff_20260718174637.md -->

---

