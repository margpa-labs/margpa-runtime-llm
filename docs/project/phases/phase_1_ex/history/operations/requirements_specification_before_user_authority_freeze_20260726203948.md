# MARGPA Runtime LLM 要件定義書

```yaml
document_id: requirements_specification
status: current
language: ja
created_at: 2026-07-26 15:16:24 JST
updated_at: 2026-07-26 17:53:18 JST
owner: Nazuna Research
active_phase: phase_1_ex
rag_default: true
```

## 1. 目的

Hugging Face由来の事前学習済みOpen Modelを利用し、Model外部のRuntimeが推論、統治、監査、評価、修復、安全性および権限境界を扱う、Model非依存の対話型AI研究基盤を構築する。

本Projectは独自基盤Modelの事前学習を主張しない。小型Modelでも全体骨格を成立させ、将来の機材更新、Home ServerまたはCloud移行時にModel／Backendを交換して継続できることを優先する。

## 2. 最上位原則

- 単一責任、疎結合、依存性逆転、Port／Adapterおよび依存性注入を採用する。
- Model、Backend、UI、Storage、Governance Definitionおよび各機能Layerを交換可能にする。
- Framework固有処理を境界へ隔離し、CoreへOS固有Pathや外部SDKを埋め込まない。
- 初期構成は内部境界を明確にしたModular Monolithとする。
- Main Model以外の機能は個別に無効化でき、無効時にLoad、Call、WriteまたはSide Effectを行わない。
- Capability不足、無効な依存関係またはDegraded状態を黙って無視しない。

## 3. 対象利用

- AI研究、AI設計、AI実装
- 要件整理、Architecture、開発相談、Code支援
- 技術調査、一般的な質問、通常の雑談
- 将来のRAG、Agent、Tool、Judge、Guardrailおよび実験比較

## 4. 機能要件

### 4.1 Phase 1実装済み

- GGUF ModelのLoadとSHA-512検証
- Model Portおよび`llama.cpp` Adapter
- CLIによる一問一答、Streaming、停止、Generation Config
- `system／user／assistant` Message
- Model Capability／Deployment Profile／Runtime Observation
- Application共通設定とPlatform Profileの分離
- 回答言語`ja／en／auto`
- Thinking実行と表示の分離、Raw Thinking非保存
- FastAPIによる最小Web Preview
- Browser Memory内の一時的な複数Turn
- New Chat、Stop、Copy、最大生成Token数
- UI日本語／English切替と回答言語の独立
- Post-generation Summary Mode
- Completion後の安全なMarkdown表示
- Preview用Basic認証
- macOS MetalおよびLightning Linux x86_64 Pure CPU実行

### 4.2 Phase 1-ex

- DocumentationのCurrent／Phase／History／Public分離
- Phase 1文書のLossless Compilation
- Current Canonical文書
- Git／GitHub公開準備、Identity／License／Terms整理
- 公開対象AllowlistとSanitation
- Local Mac用簡易Documentation RAGの要件・境界
- Mac限定RAGでも、将来Lightning／Home Server／CloudへAdapter追加できるPort Hookを持つ。
- LightningではPhase 1-ex中のRAG実装を強制せず、Public DemoではRAGをLoad／Callしない。
- Lightning Auto-start Read-only Preflight
- Basic Previewと分離したSide-effect-free Public Demo基盤
- Current／Publicの日本語正本と英語派生版
- Initial Commit前Documentation Refresh Gate

### 4.3 後続Phase

- Append-only Audit LogとSHA-512整合性
- Generic Governance Definition Platform
- ARGD／DAGDを利用可能なMain Governance
- Guardrail、Model Policy、Authority、Judge、Repair
- RAG、Source Traceability、会話履歴
- Agent、Tool、Memory、Handoff、Human Approval
- 複数GD、複数Model、実験Profile、定量／定性計算
- ML、Training、Model更新
- Responsive／Mobile UI
- Home Server／Cloud／Hybrid／Remote Backend

## 5. Governance要件

- Governance Definitionが0件でもCoreは正常動作する。
- ARGD／DAGDを含む固有GD名をApplication CoreへHard-codeしない。
- 全く未知の名称、Schemaまたは任意JSONを、明示Provider／Adapter／Compiler／Binding経由で扱える。
- JSONが存在するだけで自動実行しない。
- Governanceは`off／observe／enforce`を区別する。
- 共有Control Planeと分散Governance Pointを採用する。
- Rule Basedで処理可能な項目は決定論的に処理し、意味評価時だけModelを呼ぶ。
- Recommended ActionとExecuted Action、外部AuthorityとDefinition上の提案を分離する。
- Repair／Regenerateは回数、時間、Tokenおよび成功条件を持つ。

## 6. Layer切替要件

Main Model以外の各Component本体と、そのComponent専用Governanceを独立設定する。

```text
Main Governance
Guardrail／Guardrail Governance
Policy／Policy Governance
Judge／Judge Governance
Repair／Repair Governance
RAG／RAG Governance
Agent／Agent Governance
Tool／Tool Governance
Memory／Memory Governance
Status Reporting
External R&D Integration
```

無意味または危険な組合せはConfig Validationで拒否またはDegradedとして明示する。

## 7. Model要件

初期構成：

```text
Main:
  Qwen/Qwen3-4B-GGUF
  Qwen3-4B-Q4_K_M.gguf

Guard候補:
  Qwen3Guard-Gen-0.6B
  GGUF Q8_0または通常版

Judge候補:
  AtlaAI/Selene-1-Mini-Llama-3.1-8B
  GGUF Q5_K_Mまたは通常版
```

Guard／Judgeは初期常駐させず、必要性とResourceを確認してOn-Demand導入する。Model本体をGitへ含めない。

## 8. Platform要件

- Local既定：Apple M2 Pro、16GB、macOS ARM64、Metal
- External実証：Lightning AI Studio、Ubuntu Linux x86_64、Pure CPU
- 将来：Linux CUDA、Windows、AMD GPU、Home Server、vLLM、Remote API
- Platformは自動検出と明示Profileを組み合わせ、未対応環境をMacとして扱わない。
- Device／Backend／AccelerationはProfileとRuntime Observationで照合する。

## 9. 非機能要件

### 9.1 交換性

Port Contractを満たすAdapter交換でCore変更を最小化する。Model File名、Directory名またはGD略称をRuntime Semanticsにしない。

### 9.2 再現性

Python範囲、Dependency Version、Model ID、Artifact Digest、Quantization、Backend Version、Config SourceおよびDeployment Profileを記録する。

### 9.3 Resource

16GB Unified Memoryを基準とし、複数大型Modelの同時常駐を避ける。重いGovernance、Judge、SummaryおよびRepairは回数とBudgetを持つ。

### 9.4 Security／Privacy

- Credential、Secret、個人連絡先、実会話Log、Model本体を公開しない。
- Tool Permissionは決定論的Policyを正本とし、Model単独で権限を生成しない。
- 生のChain of Thoughtを永続保存しない。
- Public Previewと将来の本番Access Controlを区別する。
- Basic認証Previewと匿名Public Demoを別Access Profileとする。
- Public DemoはRate、Token、時間、入力、Generation BudgetをServer側で制限する。
- Public DemoではTool、RAG、Agent、外部I/O、永続化およびFile Writeを禁止する。
- 本Projectは動作、正確性、安全性、互換性または特定目的への適合性を保証しない。

### 9.5 Audit／説明

生の内部思考ではなく、System Traceと高水準の説明概要を分離して記録する。Turn、Model、Config、Definition、Rule、ActionおよびRepairを追跡可能にする。

### 9.6 Documentation

- File名は原則英語lower_snake_case、本文は日本語とする。
- Current／Publicは日本語正本`_ja`と英語派生版`_en`を持つ。
- Phase／Shared／Historyは日本語のみとする。
- Current、Phase Compilation、Raw History、Publicを区別する。
- Historyは原則Immutableとし、CurrentはGit Historyで更新する。
- Lossless Compilationで決定、例外、未解決事項を削らない。

## 10. 初期対象外

- 独自基盤Modelの事前学習
- Fine-tuning、LoRA、DPO、RLHF
- Image入力
- Microservices化
- SQL必須化
- 複数大型Modelの常時同時Load
- 全GDの同時Prompt投入
- 自動的なTool権限生成

## 11. 受入原則

- 要求機能が実際に動く。
- Module単位で無効化、交換およびTestができる。
- Capability不足とErrorが観測可能である。
- Localと外部環境で同じCore Contractを維持する。
- 構成差、Cost、Latency、品質およびGovernance結果を将来再現可能に比較できる。

## 12. Traceability

- [System Architecture](../architecture/system_architecture_ja.md)
- [Basic Design](../architecture/basic_design_ja.md)
- [Runtime Governance Specification](../governance/runtime_governance_specification_ja.md)
- [Phase 1 Requirements Compilation](../../phases/phase_1/requirements/phase_1_requirements_ja.md)
- [Phase 1-ex Requirements](../../phases/phase_1_ex/requirements/documentation_migration_and_canonical_content_requirements_ja.md)
- [Public Demo／Auto-start／Pre-release Requirements](../../phases/phase_1_ex/requirements/public_demo_auto_start_and_pre_release_requirements_ja.md)
