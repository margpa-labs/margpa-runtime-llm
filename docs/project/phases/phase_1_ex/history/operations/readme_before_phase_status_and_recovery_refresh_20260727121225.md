# MARGPA Runtime LLM

> Model-independent Runtime Governance LLM prototype by **Nazuna Research**

MARGPA Runtime LLMは、Hugging Face由来の事前学習済みオープンモデルを利用し、モデルの外側から推論、文脈、監査、評価、修復および実行状態を統治する、モデル非依存のRuntime Governance型AI研究基盤です。

現在の実装だけを見ると、小型モデルを動かすChat UIに見えるかもしれません。しかし、本Projectの中心はUIや単一モデルではありません。Model、Backend、Configuration、Governance Definition、Guardrail、Judge、Repair、RAG、Agent、Storage、UIおよびDeploymentを可能な限り分離し、個別に交換・無効化・比較できる研究基盤を段階的に構築しています。

## 最初にRoadmapをご覧ください

本Projectの目的は、Phaseが進むほど明確になります。現在動く機能だけでなく、Runtime Governance、分散Governance Point、監査・修復、RAG、Agent、研究用切替、将来R&D連携まで含む全体像は、次の文書をご覧ください。

**[MARGPA Runtime LLM Roadmap](docs/public/roadmap_ja.md)**

概要と設計思想：

- [概要](docs/public/overview_ja.md)
- [コンセプト](docs/public/concept_ja.md)
- [要件定義書](docs/project/current/requirements/requirements_specification_ja.md)
- [全体設計書](docs/project/current/architecture/system_architecture_ja.md)
- [技術選定書](docs/project/current/architecture/technology_selection_ja.md)
- [基本設計書](docs/project/current/architecture/basic_design_ja.md)
- [Runtime Governance仕様書](docs/project/current/governance/runtime_governance_specification_ja.md)

## 現在の状態

```text
Phase 0        : 完了
Phase 1        : 完了／Accepted
Phase 1 Backup : 完了／Verified
Phase 1-ex     : 進行中
GitHub公開     : 準備中
匿名Public Demo: 未公開
```

Phase 1では、次を成立させました。

- Qwen3-4B GGUFのLocal Inference
- macOS Apple Silicon／Metal実行
- Lightning AI Studio Linux x86_64／Pure CPU実行
- Model AdapterとCapability Contract
- CLI Streaming、生成停止、Generation Config
- 一時的な複数Turn会話
- 日本語／英語／自動の回答言語切替
- Thinking生成と表示の分離
- 要約モード
- FastAPIベースの最小Web UI
- 新規Chat、停止、送信、Copy、UI言語切替
- Completion Markdown表示
- Basic Preview認証とLifecycle Script
- Test、Environment Verification、Model Acceptance

Phase 1-exでは、DocsのLossless再整理、役割権限、設計統括者役の復元、利用条件、Public Demo境界、Mac限定簡易Documentation RAG、Git運用および初回公開準備を進めています。

## 現在のUI

現時点では、ひとまず次のような画面です。UIは今後も変更します。完成像と将来予定は、必ず[Roadmap](docs/public/roadmap_ja.md)をご確認ください。

![MARGPA Runtime LLM demo 1](assets/images/margpa-runtime-llm_demo_image_1.png)

![MARGPA Runtime LLM demo 2](assets/images/margpa-runtime-llm_demo_image_2.png)

![MARGPA Runtime LLM demo 3](assets/images/margpa-runtime-llm_demo_image_3.png)

![MARGPA Runtime LLM demo 4](assets/images/margpa-runtime-llm_demo_image_4.png)

![MARGPA Runtime LLM demo 5](assets/images/margpa-runtime-llm_demo_image_5.png)

![MARGPA Runtime LLM demo 6](assets/images/margpa-runtime-llm_demo_image_6.png)

## 現在のモデルと環境

Main Model：

```text
Repository   : Qwen/Qwen3-4B-GGUF
Artifact     : Qwen3-4B-Q4_K_M.gguf
Quantization : Q4_K_M
Backend      : llama-cpp-python 0.3.34
```

主な確認済み環境：

```text
Local:
  Apple M2 Pro／16GB
  macOS／ARM64
  Python 3.13.14
  Metal

External:
  Lightning AI Studio
  Ubuntu 24.04系／x86_64 Container
  Python 3.12.11
  Pure CPU
```

現在の環境制約により、高性能モデル、大規模Context、複数モデル常駐および高負荷なFull Governanceは使用していません。現在のQwen3-4BはRuntime全体の骨格を成立させるための軽量Baselineであり、最終性能Targetではありません。高性能GPU、Home ServerまたはCloudを利用可能になった段階で、Model Adapter契約を維持したまま高性能モデルへ交換・追加する予定です。

Model WeightはRepositoryへ含めません。

## Model配置

既定のMain Model配置：

```text
models/
└─ main/
   └─ qwen3-4b/
      └─ gguf/
         └─ Qwen3-4B-Q4_K_M.gguf
```

LocalではProject Rootの`models`を外部Model RootへのSymbolic Linkにできます。Modelの取得、License確認および配置は利用者の責任で行ってください。

## macOSでの最小Setup

以下は技術構成を確認するための参照手順です。Repository成果物を実行する権利を自動的に許諾するものではありません。現行のResearch Previewで実行する場合は、Rootの`LICENSE`に基づくNazuna Researchの明示許可が必要です。

前提：

- Apple Silicon Mac
- Xcode Command Line Tools
- `uv 0.11.29`
- 別途配置したQwen3-4B GGUF

依存関係の正本は`pyproject.toml`と`uv.lock`です。`requirements.txt`は使用しません。

```bash
bash scripts/setup/setup_macos_arm64_metal.sh
```

Model Smokeも行う場合：

```bash
bash scripts/setup/setup_macos_arm64_metal.sh \
  --smoke \
  --model-path models/main/qwen3-4b/gguf/Qwen3-4B-Q4_K_M.gguf
```

Web UIを起動します。

```bash
./.venv/bin/margpa-web
```

Browserで次を開きます。

```text
http://127.0.0.1:8000/
```

停止は起動Terminalで`Ctrl+C`です。

CLI例：

```bash
./.venv/bin/margpa-llm generate \
  --prompt "Runtime Governanceについて日本語で説明してください。" \
  --max-new-tokens 512
```

詳細な確認手順は[Phase 1 User Manual](docs/project/phases/phase_1/user_manual/phase_1_user_manual_ja.md)を参照してください。

## Public Demo

匿名Public Demoはまだ常時公開していません。Lightning AI Studio上のBasic Previewは手動起動・認証付きで検証済みですが、StudioがSleep中でも第三者のURL Accessだけで起動するTraffic-aware Wake-upはPlatform上の手動検証待ちです。

将来、Rate Limit、Token上限、Cost保護およびTool／RAG／外部操作の遮断を含むPublic Demo方式を予定しています。

## Runtime Governance

ARGD／DAGDを大きなSystem Promptとして毎回投入するのではなく、Definition Loader、Validator、Compiler、Rule Engine、State Machine、Audit Evaluator、Action ResolverおよびRepair Engineへ分解します。

また、未知のGovernance Definition、Definitionが一件もない状態、別系列のDefinitionおよび将来追加されるDomain Governanceを受け入れられるGeneric Registry／Compiler境界を目指します。GD名をApplication Coreへハードコードしません。

将来は、中央のGovernance Control Planeと、Input、RAG、Guardrail、Agent、Tool、Judge、ModelおよびOutputの手前に置く軽量なGovernance Pointを組み合わせます。

## 研究用のON／OFF

将来、主要Componentは個別に切り替えられる構造を目指します。

```text
Governance
Guardrail
Judge
Repair
RAG
Agent
各Governance Point
EASA
DLAGSA
OCILNS
```

Governance系は`off`、`observe`、`enforce`を分け、構成差による品質、Cost、Latencyおよび監査結果を比較できる研究基盤へ発展させます。

## 外部R&D Hook

MARGPA Runtime LLM完成後に、疎結合に統合できる独立R&D Hookを予約しています。

- **EASA — Exception Aware Safety Architecture／例外認識型安全統治機構**
- **DLAGSA — Distributed LEA Agentic Governance & Safety Architecture／分散証跡型例外認識エージェント統治安全機構**
- **OCILNS — Open Cognitive Interaction Ledger Network System／認知対話証跡台帳網**

公開しているのは名称、研究領域、方向性および接続原則です。詳細は[コンセプト](docs/public/concept_ja.md)と[Roadmap](docs/public/roadmap_ja.md)を参照してください。

## 留意事項

本Projectは研究・検証中のPrototypeです。

- 動作、互換性、正確性、完全性、安全性、可用性および特定目的への適合性を一切保証しません。
- LLMの出力には誤り、欠落、不適切な内容および予期しない挙動が含まれる可能性があります。
- 研究のため各機能をON／OFFできる設計は、安全機能が無効な構成も作れることを意味します。
- 医療、法務、金融、安全制御、重要意思決定その他の高Risk用途へ依存しないでください。
- Model Weight、第三者Software、Governance Definitionおよび外部Serviceには、それぞれ独立した利用条件が適用されます。

## 利用条件

現段階のRepositoryはOpen Sourceではありません。

- Repository上の公開物：閲覧・評価のみ許可
- 将来の公式Hosted Demo：公開時に提示する範囲内で操作を許可
- 複製、改変、再配布、派生物作成、商用利用、公開実行その他の利用：明示的な許可がない限り禁止

正確な条件は、[LICENSE](LICENSE)、[TERMS_OF_USE.md](TERMS_OF_USE.md)および[NOTICE.md](NOTICE.md)を参照してください。

将来、一定段階まで完成した後にOSS化を再検討します。将来予定は現在の許諾を変更しません。

## 引用

研究・評価で本Projectを参照する場合は、[CITATION.cff](CITATION.cff)をご確認ください。

## English Abstract

MARGPA Runtime LLM is a model-independent research prototype for governing inference, context, evaluation, repair, audit evidence, and execution state around pretrained open-weight language models. The project emphasizes strict modularity: models, backends, configuration, governance definitions, guardrails, judges, repair, RAG, agents, storage, user interfaces, and deployment profiles are designed as replaceable and independently testable components. Phase 1 established a lightweight CLI and web runtime on Apple Silicon/Metal and a Linux x86_64 pure-CPU environment. The current Phase 1-ex focuses on lossless documentation, reproducible handoff, publication boundaries, access control, and Git preparation. The present Qwen3-4B model is a resource-constrained baseline rather than the final quality target. This repository is a research preview, is not open source at this stage, and is provided without any warranty.
