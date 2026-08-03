# Phase 1 ADR Lossless Compilation
```yaml
document_id: phase_1_adr_lossless_compilation
phase: phase_1
status: frozen
language: ja
created_at: 2026-07-26 15:16:24 JST
frozen_at: 2026-07-26 15:16:24 JST
source_documents: 26
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

<!-- SOURCE_BEGIN 1: docs/adr/adr_0001_initial_model_selection_20260718174637.md -->

### Source 1: `docs/adr/adr_0001_initial_model_selection_20260718174637.md`

- History Target: `docs/project/phases/phase_1/history/adr/adr_0001_initial_model_selection_20260718174637.md`
- Source SHA-512: `e41b1e03cab3fda60c384f53461874bb4ff13f6d76921528e5195a76852a9630f69fe7e28e8de47c6e4a219a3d5bf2d80bf6b3bd1c695dddb2217928f6c4434d`
- Source Size: `2617` bytes

# ADR 0001 初期Model構成の選定

- 文書ID: `adr_0001_initial_model_selection`
- 状態: `accepted`
- 作成日時: `2026-07-18 17:46:37 JST`
- 更新日時: `2026-07-18 17:46:37 JST`
- 正本言語: 日本語
- 関連文書: [model_strategy_20260718174637.md](../history/architecture/model_strategy_20260718174637.md)

## Context

初期実行環境はApple M2 Pro・16GBであり、OS、Model、KV Cache、UI、Audit、将来のRAG等がUnified Memoryを共有する。

プロジェクトの最優先事項は、最高品質の回答ではなく、Model交換可能なRuntime Governance型LLMの全体骨格を成立させることである。

検討対象にはDeepSeek、Llama、Qwen、Mistral、SmolLM等があった。

Guardrailと将来のLLM-as-a-Judgeについても、Mainとは別RoleとしてHookを設ける必要がある。

## Decision

初期構成を次とする。

```text
Main:
  Qwen/Qwen3-4B-GGUF
  Qwen3-4B-Q4_K_M.gguf
  Q4_K_M

Guard:
  DevQuasar/Qwen.Qwen3Guard-Gen-0.6B-GGUF
  Qwen.Qwen3Guard-Gen-0.6B.Q8_0.gguf
  Q8_0
  Phase 4

Judge:
  bartowski/Selene-1-Mini-Llama-3.1-8B-GGUF
  Selene-1-Mini-Llama-3.1-8B-Q5_K_M.gguf
  Q5_K_M
  将来On-Demand
```

3Modelを常時同時Loadしない。

必要性が出た場合は、次の通常版へ交換可能にする。

```text
Qwen/Qwen3Guard-Gen-0.6B
AtlaAI/Selene-1-Mini-Llama-3.1-8B
```

## Reason

### Main Q4_K_M

- M2 Pro・16GBで扱いやすい
- 4B級として軽量
- 日本語と開発支援のBalance
- llama.cpp系で利用可能
- MVP全体骨格に適する

### Guard Q8_0

- Model自体が小さい
- Q4_K_Mとの差が小さい
- Classification品質を優先
- 低Bit量子化による境界劣化を抑える

### Judge Q5_K_M

- 常時利用しない
- Evaluation品質を速度より優先
- On-Demand実行を前提にMemoryを許容する

## Consequence

Positive：

- Initial Hardwareで実行可能性が高い
- Roleごとに適切なQuantizationを選べる
- Main、Guard、Judgeを独立して交換できる
- 将来のCloud移行で通常版や大型版へ変更できる

Negative／Risk：

- Qwen3-4Bの回答品質には上限がある
- Guard GGUFは第三者変換の検証が必要
- Seleneの日本語Judge性能は未保証
- Judge Load時にMainのUnloadが必要になる可能性
- ModelごとのPrompt／Parser差をAdapterで吸収する必要がある

## Validation

実装後に次を検証する。

- MainのToken速度とMemory
- Main＋Guardの同時Memory
- Guardの日本語分類
- Guard GGUFと通常版の差
- Judgeの日本語評価
- Load／Unload時間
- File HashとRevision

<!-- SOURCE_END 1: docs/adr/adr_0001_initial_model_selection_20260718174637.md -->

---

<!-- SOURCE_BEGIN 2: docs/adr/adr_0002_external_model_storage_20260718174637.md -->

### Source 2: `docs/adr/adr_0002_external_model_storage_20260718174637.md`

- History Target: `docs/project/phases/phase_1/history/adr/adr_0002_external_model_storage_20260718174637.md`
- Source SHA-512: `f5ad46e8cc7e2057588e2ea7e6def1e56721ea28848fce45015130d621c8a110617f30ce12863f88774c34b1d33326674b72f173acc72948626262ea8fa0c844`
- Source Size: `2740` bytes

# ADR 0002 Model本体の外部配置

- 文書ID: `adr_0002_external_model_storage`
- 状態: `accepted`
- 作成日時: `2026-07-18 17:46:37 JST`
- 更新日時: `2026-07-18 17:46:37 JST`
- 正本言語: 日本語
- 関連文書: [model_strategy_20260718174637.md](../history/architecture/model_strategy_20260718174637.md)

## Context

GGUF Modelは数百MBから数GBあり、通常のGit Repositoryに含める用途に適さない。

ユーザーは既存Modelを`/path/to/models/`で一元管理している。LLaVA等の他Modelと、MARGPA Runtime LLM専用Modelを混在させずに管理したい。

一方、Project内からは`./models/...`として分かりやすく参照したい。

## Decision

Model本体の物理Rootを次とする。

```text
/path/to/margpa-models/
```

Project直下の`models`はPOSIX Symbolic Linkとする。

```text
margpa-runtime-llm/models
  → /path/to/margpa-models
```

物理構造：

```text
models/
├─ main/<model>/<format>/
├─ guard/<model>/<format>/
├─ judge/<model>/<format>/
├─ classifier/
├─ embedding/
├─ reranker/
├─ shared/
└─ vision/
```

Symbolic LinkはLocal便利用とし、Runtimeは設定可能なModel Rootを正本とする。

Model本体とSymbolic LinkはGit管理対象外とする。

## Reason

- 他ProjectのModelと分離できる
- Main、Guard、Judgeを視覚的に管理できる
- GGUF、MLX、Transformersを将来分離できる
- 同じProject内に複数Modelを置ける
- Repositoryを巨大化させない
- Model Licenseと再配布問題を減らせる
- LocalとCloudでModel Rootを交換できる

## Finder Aliasを不採用とする理由

Finder AliasはFinder上では解決できるが、Pythonや通常のFilesystem PathからDirectoryとして透過的に扱えない。

そのため、当初のFinder Aliasを削除し、POSIX Symbolic Linkへ置換した。

## Consequence

Positive：

- Projectから`models/main/...`として参照できる
- Model本体をRepository外へ保てる
- Local利用が分かりやすい
- Cloudでは設定変更で別Rootを利用できる

Negative／Risk：

- Absolute Linkは他PCで壊れる
- Symbolic LinkをGitへCommitしてはいけない
- RuntimeがLinkだけに依存するとPortabilityが下がる
- macOSとLinuxのCase Sensitivity差に注意が必要

## GitHub方針

GitHubには次だけを掲載する。

- Model ID
- Distribution／Upstream
- File名
- Quantization
- Download手順
- Placement手順
- Hash検証手順
- License
- Sample Config

Model Binaryは掲載しない。

## Follow-up

実装時に次を用意する。

- Model Root設定
- Model Registry
- Missing Model Error
- Hash検証
- `.gitignore`
- GitHub向けDownload手順

<!-- SOURCE_END 2: docs/adr/adr_0002_external_model_storage_20260718174637.md -->

---

<!-- SOURCE_BEGIN 3: docs/adr/adr_0003_japanese_documentation_and_handoffs_20260718174637.md -->

### Source 3: `docs/adr/adr_0003_japanese_documentation_and_handoffs_20260718174637.md`

- History Target: `docs/project/phases/phase_1/history/adr/adr_0003_japanese_documentation_and_handoffs_20260718174637.md`
- Source SHA-512: `ebcfba3e3ed33ecec7a298d1c35e6c9c8b8d4acdde210ad51a8a27dc06b9104529c5e3378f52de3a43c705ec89986738460c26ff3c29c7e032568a458e1fff9a`
- Source Size: `2165` bytes

# ADR 0003 日本語Docsと担当別引き継ぎ

- 文書ID: `adr_0003_japanese_documentation_and_handoffs`
- 状態: `accepted`
- 作成日時: `2026-07-18 17:46:37 JST`
- 更新日時: `2026-07-18 17:46:37 JST`
- 正本言語: 日本語
- 関連ルール: [documentation_rules_20260718174637.md](../history/requirements/documentation_rules_20260718174637.md)

## Context

ユーザーは現時点で英語文書を読むことを前提にできない。

また、Projectでは次の担当タスクを分離する構想がある。

- 設計者役
- 実装者役
- 対外向けDocs作成者役
- その他の専門担当

タスクごとに長大な会話を再度貼り付ける負担を減らし、Docsを共通の引き継ぎ基盤として利用する必要がある。

## Decision

- Docsの正本言語を日本語とする
- 技術識別子や正式名称だけ英語を保持する
- `docs/`を要件・設計・判断・引き継ぎの正本とする
- `requirements`、`architecture`、`governance`、`adr`、`handoffs`へ分割する
- 各担当タスクは共通引き継ぎと担当領域文書を読む
- File名は英語Lower Snake CaseとTimestampを使用する
- 文書索引で現在の正本を指定する

## File Name

```text
lower_snake_case_YYYYMMDDHHMMSS.md
```

TimezoneはJSTとする。

同一Snapshotとして一括作成する文書は、同じ作成時刻を共有してよい。

## Consequence

Positive：

- ユーザーがDocsを直接確認できる
- 別タスクへの引き継ぎが容易になる
- DesignとImplementationの責務を分けられる
- 判断理由をADRとして保持できる
- GitHub公開用Docsの原稿として再利用できる

Negative／Risk：

- 英語利用者向けDocsは後から翻訳が必要
- 同じ主題のDocumentが増えると正本判定が難しくなる
- 古いHandoffが残ると矛盾する可能性がある

## Mitigation

- `documentation_index`でCurrent文書を指定する
- 状態を`current`、`superseded`等で明示する
- 実質的変更は新Timestamp Fileとして作る
- Handoffは正本へのLinkを持つ
- 英語版は日本語正本から派生させる

<!-- SOURCE_END 3: docs/adr/adr_0003_japanese_documentation_and_handoffs_20260718174637.md -->

---

<!-- SOURCE_BEGIN 4: docs/adr/adr_0004_modular_monolith_20260718174637.md -->

### Source 4: `docs/adr/adr_0004_modular_monolith_20260718174637.md`

- History Target: `docs/project/phases/phase_1/history/adr/adr_0004_modular_monolith_20260718174637.md`
- Source SHA-512: `4a605a80635d3d7b36bec9edc674022fac152c71b4d23b85c2bcd62d063bf2de3c523744d8d9fc2a1f892fc03da265757398d83737166933aa7d1f0a25da47c8`
- Source Size: `1934` bytes

# ADR 0004 Modular Monolithの採用

- 文書ID: `adr_0004_modular_monolith`
- 状態: `accepted`
- 作成日時: `2026-07-18 17:46:37 JST`
- 更新日時: `2026-07-18 17:46:37 JST`
- 正本言語: 日本語
- 関連文書: [system_architecture_20260718174637.md](../history/architecture/system_architecture_20260718174637.md)

## Context

ProjectはModel Runtime、Conversation、Governance、Audit、Guardrail、RAG、Agent、UI等の多数の責務を持つ。

将来の交換性を確保するにはModule分離が必要だが、初期MVPでMicroservicesを採用すると、Deployment、Network、Observability、Distributed Transaction等のScopeが増える。

初期実行環境は単一のMacBook Proである。

## Decision

初期ArchitectureとしてModular Monolithを採用する。

内部では次を明確に分離する。

- Domain／Core
- Application
- Ports
- Adapters
- Interface
- Model Runtime
- Governance Runtime
- Guardrail
- Audit
- Storage
- RAG
- Agent

Module間はInterface／Portを通して接続し、Framework固有処理をAdapterへ隔離する。

## Reason

- 初期実装とDebugが容易
- M2 Pro・16GBで動かしやすい
- Network境界を増やさずに済む
- Module単位のTestと交換性を維持できる
- 必要になった境界だけ将来Service分割できる

## Consequence

Positive：

- MVPの実装量を抑えられる
- Local実行が簡単
- 一つのProcessでTraceしやすい
- Adapter交換でLocal／Cloudへ対応できる

Negative／Risk：

- Boundaryを守らないと巨大なMonolithになる
- Framework固有処理がCoreへ漏れる可能性
- Module間の直接Importが増える可能性

## Mitigation

- Dependency Directionを固定する
- Port／Adapterを利用する
- 循環依存を禁止する
- Module単位Testを用意する
- Architecture Testを将来検討する
- Application CoreからCloud SDKやBackend SDKを直接参照しない

<!-- SOURCE_END 4: docs/adr/adr_0004_modular_monolith_20260718174637.md -->

---

<!-- SOURCE_BEGIN 5: docs/adr/adr_0005_python_environment_and_dependency_management_20260718201744.md -->

### Source 5: `docs/adr/adr_0005_python_environment_and_dependency_management_20260718201744.md`

- History Target: `docs/project/phases/phase_1/history/adr/adr_0005_python_environment_and_dependency_management_20260718201744.md`
- Source SHA-512: `85199475a2224765ffb09b27d078956d80ccba9362feb5d31ff68261a6117aa7bb68d4c84e4c759717e0280efb298791f7b4c58fbfc5cb46d6dd0b42015ee660`
- Source Size: `5071` bytes

# ADR-0005 Python実行環境とDependency管理

- 文書ID: `adr_0005_python_environment_and_dependency_management`
- 状態: `accepted`
- 作成日時: `2026-07-18 20:17:44 JST`
- 更新日時: `2026-07-18 20:17:44 JST`
- 対象: 全担当Task
- 正本言語: 日本語
- Decision Owner: 設計者役担当Task、ユーザー承認済み
- 関連Architecture: [python_environment_and_dependency_strategy_20260718201744.md](../history/architecture/python_environment_and_dependency_strategy_20260718201744.md)
- supersedes: なし（新規ADR）

## Context

MARGPA Runtime LLMは、Apple M2 Pro／16GB／ARM64のMacBook Proで初期開発・実行する。

初期ModelはGGUFであり、Local Backendとして`llama-cpp-python`／Metalを有力候補とする。

将来は次を追加・交換する可能性がある。

- FastAPI
- Jupyter
- Governance／Audit
- Guard Model
- LLM-as-a-Judge
- RAG
- LangChain
- LangGraph
- Transformers／PyTorch
- MLX
- Cloud／vLLM

そのためPython Version、Virtual Environment、Dependencyの追加時期、Lock方式を先に定める必要がある。

## Decision

### Python

Primary：

```text
CPython 3.13.14 / ARM64 / 通常GIL Build
```

Fallback：

```text
CPython 3.12.13
```

Python 3.13で`llama-cpp-python`のMetal Source Buildが再現可能に成立しない場合のみ、3.12へFallbackする。

Python 3.11.9は正式基準にしない。

### Virtual Environment

Primary：

```text
margpa-runtime-llm/.venv/
```

Path起因のNative Build問題が確認された場合：

```text
<USER_HOME>/.venvs/margpa-runtime-llm/
```

Project側の`.venv`からExternal VenvへのPOSIX Symbolic Linkを候補とする。

### Package Manager

```text
uv 0.11.29
```

Dependencyは`pyproject.toml`で宣言し、解決済みVersionを`uv.lock`で固定する。

### Install Policy

将来使用する可能性があるPackageを先に全部Installしない。

Phase単位で必要なDependency Groupだけを追加する。

初期対象：

```text
core + inference-llama + dev + notebook
```

## Reasons

### Python 3.13をPrimaryとする理由

- Python 3.11より長い公式Support期間を確保できる
- Python 3.12よりBugfix Support期間とEOLが長い
- Python 3.14よりLLM／Native Package互換性を保守的に扱える
- 主要候補PackageがPython 3.13をSupportしている
- 2026年開始の新規Projectに適した寿命がある

### Python 3.11.9を正式基準にしない理由

- Python 3.11系列はSecurity Fix Onlyである
- 公式Support終了予定が2027年10月である
- 3.11.9は最新Security Patchではない
- 将来Network公開する可能性がある新規Projectの基準として残存期間が短い

Python 3.11.9が「動かない」または「使用禁止」という意味ではない。Localの短期ExperimentやEmergency Fallbackとしては利用可能である。

### Phase単位Installとする理由

- GGUF推論にPyTorch／Transformersは不要である
- 未使用PackageのVersion競合を避けられる
- 問題発生時の原因範囲を小さくできる
- RAG／Agent実装時点のCompatibilityを改めて評価できる
- Install済みPackageとAttack Surfaceを最小化できる
- Modular ArchitectureのOptional Capabilityと対応づけられる

## Alternatives Considered

### Python 3.11.9

長所：

- 非常に広いPackage互換性
- Metal Prebuilt Wheelの利用が容易
- 既存ML Toolとの相性がよい

不採用理由：

- 新規Projectの正式基準としてSupport残存期間が短い
- 最新Security Patchではない

### Python 3.12.13

長所：

- Python 3.13よりPrebuilt Wheel対応が広い可能性がある
- ML Package互換性が成熟している

Primaryにしない理由：

- すでにSecurity Fix Onlyである
- Python 3.13よりEOLが早い

Fallbackとして保持する。

### Python 3.14

長所：

- 最も長いSupport期間
- 新しいPython機能

不採用理由：

- Native ExtensionとML Ecosystemの追随Riskを増やす
- MVPの目的に新機能が必要ない

### 将来Packageの一括Install

不採用理由：

- 未使用の大規模Dependencyが増える
- Phase開始前にVersionが古くなる
- 競合とBuild問題の切り分けが難しくなる

## Consequences

### Positive

- Python環境の再現性が高くなる
- Local／Cloud Dependencyを分離しやすい
- Phase単位で影響範囲を制御できる
- Model BackendをOptional Capabilityとして扱える
- 開発担当がInstall対象を判断しやすい

### Negative／Risk

- Python 3.13では`llama-cpp-python` Metal版のSource Buildが必要になる可能性が高い
- Xcode Command Line Tools等のNative Build前提が増える
- 深い日本語PathがBuild Toolへ影響する可能性がある
- 将来Package追加時に都度Compatibility確認が必要になる

## Implementation Constraint

このADRはEnvironment作成やInstallの許可ではない。

ユーザーから実装解禁を受けるまで、Python、Venv、Package、Build、Lock Fileを変更しない。


<!-- SOURCE_END 5: docs/adr/adr_0005_python_environment_and_dependency_management_20260718201744.md -->

---

<!-- SOURCE_BEGIN 6: docs/adr/adr_0006_model_runtime_port_and_configuration_20260718223203.md -->

### Source 6: `docs/adr/adr_0006_model_runtime_port_and_configuration_20260718223203.md`

- History Target: `docs/project/phases/phase_1/history/adr/adr_0006_model_runtime_port_and_configuration_20260718223203.md`
- Source SHA-512: `17ca0506c27b42237ea37886e7c45a60655fdb4ae2c440c783e123a7173d261ffd245af51c3346000fe90bcf05691cdc973e6196fd567f0da3764b6093c2a264`
- Source Size: `5354` bytes

# ADR-0006: Model Runtime PortとConfiguration境界

- 文書ID: `adr_0006_model_runtime_port_and_configuration`
- 状態: `proposed`
- 作成日時: `2026-07-18 22:32:03 JST`
- 更新日時: `2026-07-18 22:32:03 JST`
- Decision Owner: 設計者役担当Task
- 対象: Phase 1-B Model Runtime
- 正本言語: 日本語
- 詳細設計: [phase_1b_model_runtime_contract_20260718223203.md](../history/architecture/phase_1b_model_runtime_contract_20260718223203.md)
- supersedes: なし

## Context

Phase 1-Aで、Python 3.13.14、llama-cpp-python 0.3.34、Apple MetalおよびQwen3-4B GGUFの技術成立性を確認した。

Phase 1-Bでは、技術検証ScriptをApplication Coreから直接利用するのではなく、将来のModel／Backend／Hardware交換に耐える安定境界が必要である。

現在のHardwareはApple M2 Pro／16GBであり、複数大型Modelの同時常駐や高並列Generationは初期前提にできない。

## Decision

### 1. Model Port

Application Coreは`typing.Protocol`で定義したModel Portだけへ依存する。

llama.cpp固有処理は`adapters/model_backends/llama_cpp/`へ閉じ込める。

### 2. Port InstanceとModel Lifecycle

1つのModel Port Instanceは同時に1 Modelだけを所有する。

Model交換時は暗黙Reloadを行わず、明示Unload後に別ModelをLoadする。

Phase 1-Bの同時Generation数は1とし、競合Requestは明示的な`model_busy`とする。

### 3. Public Contract

Public DTO／ConfigはPydantic v2によるImmutable Contractとし、未知Fieldを拒否する。

Port自体はProtocolで定義し、Backend固有Class／Dict／Exceptionを公開しない。

### 4. Capability

Model RegistryのExpected Capabilityと、AdapterがLoad後に申告するEffective Runtime Capabilityを分ける。

ApplicationはEffective Runtime Capabilityを判断根拠とする。

Phase 1-BではRequired Capability不足を黙って無視せず、明示Errorとする。

### 5. Streaming Stop

StreamingはModel非依存のStream Handleを返す。

Stopは協調CancelとNative Generator Closeで行い、Model UnloadやProcess Killとして扱わない。

Cancel後も同一Model InstanceでGenerationを再実行可能にする。

### 6. Registry／Config

Model Registry、Deployment Profile、Generation Profileを分離する。

初期Config形式はTOMLとし、Python標準Library`tomllib`を使用する。

User固有絶対PathはTracked Configへ保存せず、Model RootはEnvironment Variable等で上書き可能にする。

### 7. 初期Runtime Profile

```text
Model             : Qwen3-4B Q4_K_M
Backend           : llama-cpp-python 0.3.34
Context Size      : 4,096
Thinking          : Default OFF
max_new_tokens    : 512
Streaming         : Default ON
CLI               : 一問一答＋Stop
Multi-Turn        : Phase 2
```

Sampling値はQwen公式の非Thinking推奨を初期値とするが、すべてConfigで交換可能にする。

### 8. CLI

Phase 1-B CLIは標準Library`argparse`を使用する。

新規CLI Framework Dependencyは追加しない。

## Consequences

### Positive

- Model／BackendをApplication Coreから分離できる
- Local／Cloud Adapterを同じContractへ接続できる
- Capability不足を早期検出できる
- Native ExceptionやResponse形式を境界で吸収できる
- Model RegistryとPerformance設定を独立変更できる
- Test用Fake AdapterでCoreを高速検証できる
- 現在の16GB制約を守りながら将来の高性能化経路を残せる

### Negative／Cost

- 単純なllama.cpp直接呼出よりContract数が増える
- Lifecycle／Streaming Handle／Error Mappingの実装が必要になる
- Pydantic ModelとNative ResponseのMapping Costが増える
- Thinking切替にはllama.cpp Adapter固有のChat Template処理が必要になる
- TOML RegistryとProfileの整合Testが必要になる

### Risk Mitigation

- Phase 1-Bに必要なContractだけを実装する
- Future CapabilityはHookに留める
- Contract TestをAdapter共通Suiteとして用意する
- Private Backend API依存をAdapter内へ限定する
- Backend VersionをRegistry／Runtime Infoへ記録する
- Context Overflowを黙って補正しない

## Alternatives Considered

### llama.cppをApplicationから直接呼ぶ

初期実装は短くなるが、Model交換、Cloud移行、Capability検査およびGovernance介入が困難になるため不採用。

### LangChain Model InterfaceをCore Contractにする

Framework依存がApplication Coreへ入り、Backend固有CapabilityとErrorの制御が曖昧になるため不採用。

将来Adapter内部でLangChainを利用する余地は残す。

### YAML Config

可読性は高いが追加DependencyとParser差異が発生するため、Phase 1-Bでは不採用。

### JSON Config

機械処理には向くが、Commentと手編集のしやすさでTOMLを優先した。

### 複数Modelを1 Port Instanceで自動切替

暗黙Load／Unload、副作用、Memory使用量および競合制御が複雑になるため不採用。

将来は複数のPort InstanceとRouter／Orchestrationで扱う。

## Acceptance

このADRは、ユーザーがPhase 1-B詳細設計を確認し、実装担当向けHandoff作成を許可した時点で`accepted`の後継ADRを作成する。

既存ADRを上書きしない。


<!-- SOURCE_END 6: docs/adr/adr_0006_model_runtime_port_and_configuration_20260718223203.md -->

---

<!-- SOURCE_BEGIN 7: docs/adr/adr_0006_model_runtime_port_and_configuration_20260718224308.md -->

### Source 7: `docs/adr/adr_0006_model_runtime_port_and_configuration_20260718224308.md`

- History Target: `docs/project/phases/phase_1/history/adr/adr_0006_model_runtime_port_and_configuration_20260718224308.md`
- Source SHA-512: `7a3a304dc30b3ab68c0b2fceb5f7d1242d155e81386eb3d241fbb1e5d5c10c68d28beb4336acae28e0dd8cddeb5bb2c2396fc7c2107002548ea3fa5f89a6310b`
- Source Size: `6274` bytes

# ADR-0006: Model Runtime PortとConfiguration境界

- 文書ID: `adr_0006_model_runtime_port_and_configuration`
- 状態: `accepted`
- 作成日時: `2026-07-18 22:43:08 JST`
- 更新日時: `2026-07-18 22:43:08 JST`
- 承認日時: `2026-07-18 22:43:08 JST`
- Decision Owner: 設計者役担当Task
- 承認者: ユーザー
- 対象: Phase 1-B Model Runtime
- 正本言語: 日本語
- 詳細設計: [phase_1b_model_runtime_contract_20260718223203.md](../history/architecture/phase_1b_model_runtime_contract_20260718223203.md)
- 実装Handoff: [designer_handoff_phase_1b_model_runtime_20260718224308.md](../history/handoffs/designer_handoff_phase_1b_model_runtime_20260718224308.md)
- supersedes: `adr_0006_model_runtime_port_and_configuration_20260718223203.md`

## Status Decision

ユーザーがPhase 1-B詳細設計を確認し、初期方針と実装担当Handoff作成を承認したため、本ADRを`accepted`とする。

提案版ADRは変更せず、Append-Only履歴として残す。

本ADRのAccepted化は設計判断の承認であり、Source実装、Config作成、Dependency変更または担当別書込範囲の自動拡張を意味しない。

## Context

Phase 1-Aで、Python 3.13.14、llama-cpp-python 0.3.34、Apple MetalおよびQwen3-4B GGUFの技術成立性を確認した。

Phase 1-Bでは、技術検証ScriptをApplication Coreから直接利用するのではなく、将来のModel／Backend／Hardware交換に耐える安定境界が必要である。

現在のHardwareはApple M2 Pro／16GBであり、複数大型Modelの同時常駐や高並列Generationは初期前提にできない。

## Decision

### 1. Model Port

Application Coreは`typing.Protocol`で定義したModel Portだけへ依存する。

llama.cpp固有処理は`adapters/model_backends/llama_cpp/`へ閉じ込める。

### 2. Port InstanceとModel Lifecycle

1つのModel Port Instanceは同時に1 Modelだけを所有する。

Model交換時は暗黙Reloadを行わず、明示Unload後に別ModelをLoadする。

Phase 1-Bの同時Generation数は1とし、競合Requestは明示的な`model_busy`とする。

### 3. Public Contract

Public DTO／ConfigはPydantic v2によるImmutable Contractとし、未知Fieldを拒否する。

Port自体はProtocolで定義し、Backend固有Class／Dict／Exceptionを公開しない。

### 4. Capability

Model RegistryのExpected Capabilityと、AdapterがLoad後に申告するEffective Runtime Capabilityを分ける。

ApplicationはEffective Runtime Capabilityを判断根拠とする。

Phase 1-BではRequired Capability不足を黙って無視せず、明示Errorとする。

### 5. Streaming Stop

StreamingはModel非依存のStream Handleを返す。

Stopは協調CancelとNative Generator Closeで行い、Model UnloadやProcess Killとして扱わない。

Cancel後も同一Model InstanceでGenerationを再実行可能にする。

### 6. Registry／Config

Model Registry、Deployment Profile、Generation Profileを分離する。

初期Config形式はTOMLとし、Python標準Library`tomllib`を使用する。

User固有絶対PathはTracked Configへ保存せず、Model RootはEnvironment Variable等で上書き可能にする。

### 7. 初期Runtime Profile

```text
Model             : Qwen3-4B Q4_K_M
Backend           : llama-cpp-python 0.3.34
Context Size      : 4,096
Thinking          : Default OFF
max_new_tokens    : 512
Streaming         : Default ON
CLI               : 一問一答＋Stop
Multi-Turn        : Phase 2
```

Sampling値はQwen公式の非Thinking推奨を初期値とするが、すべてConfigで交換可能にする。

### 8. CLI

Phase 1-B CLIは標準Library`argparse`を使用する。

新規CLI Framework Dependencyは追加しない。

## Consequences

### Positive

- Model／BackendをApplication Coreから分離できる
- Local／Cloud Adapterを同じContractへ接続できる
- Capability不足を早期検出できる
- Native ExceptionやResponse形式を境界で吸収できる
- Model RegistryとPerformance設定を独立変更できる
- Test用Fake AdapterでCoreを高速検証できる
- 現在の16GB制約を守りながら将来の高性能化経路を残せる

### Negative／Cost

- 単純なllama.cpp直接呼出よりContract数が増える
- Lifecycle／Streaming Handle／Error Mappingの実装が必要になる
- Pydantic ModelとNative ResponseのMapping Costが増える
- Thinking切替にはllama.cpp Adapter固有のChat Template処理が必要になる
- TOML RegistryとProfileの整合Testが必要になる

### Risk Mitigation

- Phase 1-Bに必要なContractだけを実装する
- Future CapabilityはHookに留める
- Contract TestをAdapter共通Suiteとして用意する
- Private Backend API依存をAdapter内へ限定する
- Backend VersionをRegistry／Runtime Infoへ記録する
- Context Overflowを黙って補正しない

## Alternatives Considered

### llama.cppをApplicationから直接呼ぶ

初期実装は短くなるが、Model交換、Cloud移行、Capability検査およびGovernance介入が困難になるため不採用。

### LangChain Model InterfaceをCore Contractにする

Framework依存がApplication Coreへ入り、Backend固有CapabilityとErrorの制御が曖昧になるため不採用。

将来Adapter内部でLangChainを利用する余地は残す。

### YAML Config

可読性は高いが追加DependencyとParser差異が発生するため、Phase 1-Bでは不採用。

### JSON Config

機械処理には向くが、Commentと手編集のしやすさでTOMLを優先した。

### 複数Modelを1 Port Instanceで自動切替

暗黙Load／Unload、副作用、Memory使用量および競合制御が複雑になるため不採用。

将来は複数のPort InstanceとRouter／Orchestrationで扱う。

## Acceptance

本ADRはAcceptedである。

実装は、次を満たした後に開始する。

1. 実装担当が最新Index、詳細設計、本ADR、Phase 1-B Handoffを読み取る
2. `config/`および必要なRoot Fileへの書込範囲をユーザーが明示する
3. ユーザーがPhase 1-B実装開始を明示的に許可する

Decisionを変更する場合は、この文書を編集せず、新Timestampの後継ADRを作成する。


<!-- SOURCE_END 7: docs/adr/adr_0006_model_runtime_port_and_configuration_20260718224308.md -->

---

<!-- SOURCE_BEGIN 8: docs/adr/adr_0007_deployment_platform_acceleration_abstraction_20260719013109.md -->

### Source 8: `docs/adr/adr_0007_deployment_platform_acceleration_abstraction_20260719013109.md`

- History Target: `docs/project/phases/phase_1/history/adr/adr_0007_deployment_platform_acceleration_abstraction_20260719013109.md`
- Source SHA-512: `49c0bc67aa92d9615f83419560d0b65d9b45cf535b2a1a189bbfea868acc05a62cc4a396a2edbf08dd5c78ab4b1a171fe10f67f99f8b40342af4a49a20e73661`
- Source Size: `7363` bytes

# ADR-0007: Deployment／Platform／Acceleration Abstraction

- 文書ID: `adr_0007_deployment_platform_acceleration_abstraction`
- 状態: `accepted`
- 作成日時: `2026-07-19 01:31:09 JST`
- 更新日時: `2026-07-19 01:31:09 JST`
- 承認日時: `2026-07-19 01:31:09 JST`
- Snapshot: `20260719013109`
- Decision Owner: 設計者役担当Task
- 承認者: ユーザー
- 対象: Phase 1-C、Deployment Profile、Platform、Acceleration、Runtime Capability
- 正本言語: 日本語
- 要件: [phase_1c_deployment_platform_acceleration_requirements_20260719013109.md](../history/requirements/phase_1c_deployment_platform_acceleration_requirements_20260719013109.md)
- Architecture: [phase_1c_deployment_platform_acceleration_architecture_20260719013109.md](../history/architecture/phase_1c_deployment_platform_acceleration_architecture_20260719013109.md)
- 関連ADR: [adr_0006_model_runtime_port_and_configuration_20260718224308.md](../history/adr/adr_0006_model_runtime_port_and_configuration_20260718224308.md)
- supersedes: なし（ADR-0006をPlatform観点で拡張・一部修正する新規Decision）

## Status Decision

ユーザーは、Windows専用Hookではなく、OS、CPU Architecture、GPU／NPU Vendor、Acceleration API、Backend Adapter、Artifact VariantおよびLocal／Remote Topologyを分離する汎用Phase 1-C方針を承認した。

本ADRを`accepted`とする。

本ADRのAccepted化はSource実装、Config変更、Dependency変更、Native Buildまたは外部環境操作を自動的に解禁しない。

## Context

Phase 1-BはModel Port、llama.cpp Adapter、TOML ProfileおよびCurrent Mac／Metal Runtimeを成立させた。

一方、`gpu_offload`がModel Required Capabilityへ含まれ、Current Mac Deploymentの条件がModel固有条件として扱われている。

将来候補には次が存在する。

- macOS／Metal／MLX／MPS
- Windows／CPU／CUDA／HIP／Vulkan／DirectML
- Linux／CPU／CUDA／ROCm／Vulkan／SYCL
- Home Server／LAN Remote
- Cloud／vLLM／GPU／TPU／AWS Neuron
- Single GPU／Multi-GPU／Multi-Node
- GGUF／Safetensors／MLX／ONNX等のArtifact Variant

これらを全実装することは初期MVPのScopeを超える。

しかし、WindowsとMacだけの閉じたSchemaにすると、Home ServerまたはCloud追加時に再設計が必要になる。

## Decision

### 1. Phase名

```text
Phase 1-C：Deployment／Platform／Acceleration Abstraction Hook
```

とする。

### 2. 全環境の実装ではなく全環境を表現できる境界

Phase 1-Cでは、全OS／全Hardware／全Backendを実装しない。

現在のMac以外を後から追加できる最小Contract、Profile Schema、Resolver HookおよびValidation境界を作る。

### 3. Model CapabilityとDeployment Requirementの分離

`gpu_offload`はQwen3-4B Model自体の必須能力ではない。

Model Registry上ではOptionalまたはRuntime Capabilityとして扱い、Current macOS Metal ProfileがRequiredとする。

ADR-0006のPhase 1-B Required Capability一覧に含まれる`gpu_offload`は、Phase 1-C以降、Deployment Required Capabilityとして再分類する。

その他のPhase 1-B Decisionは維持する。

### 4. Orthogonal Dimension

次を独立軸として扱う。

- Host OS
- Architecture
- Execution Environment
- Compute Kind
- Hardware Vendor
- Acceleration API
- Memory Topology
- Backend Adapter
- Backend Build Variant
- Model Artifact Variant
- Execution Topology
- Required／Detected／Executed Capability

### 5. Extensible Identifier

Vendor、BackendおよびAcceleration APIを全世界分の閉じたEnumへ固定しない。

形式ValidationされたString KeyとDefinition／Registryにより拡張可能にする。

### 6. Profile Resolution

```text
Explicit指定
  > Environment指定
  > Platform Default Resolver
```

の優先順位を採用する。

未対応PlatformをCurrent Mac Profileへ黙ってFallbackしない。

### 7. Verification State

設計、実装、Static Verification、Native Verificationを分離する。

Phase 1-C完了時点でも、Current Mac以外を実機検証済みと主張しない。

### 8. Current Scope

Phase 1-CはCurrent Mac ProfileのMigration、Contract、Resolver Hook、Capability分離、TestおよびRegressionまでとする。

Windows／Linux Profile、Native Setup、CUDA／ROCm／Vulkan Build等はHardware決定後に追加する。

## Reasons

- Current Mac固定条件の上位層への伝播を早期に止められる
- 未所有Hardware向けのSpeculative Implementationを避けられる
- Home ServerやCloudをWindowsの特殊例として扱わずに済む
- Model、Artifact、Backend、Hardwareを独立交換できる
- Governance／AuditへRequired／Detected／Executed Stateを正確に渡せる
- 未対応環境を誤ってSupport済みと表示しない

## Consequences

### Positive

- Phase 2以降をMacで進めてもPlatform追加時の変更を局所化できる
- CPU ProfileとGPU Profileが同じModel Definitionを共有できる
- CUDA、ROCm、Vulkan等をProfile／Build Variantとして追加できる
- Remote Model AdapterとLocal Adapterを同じ上位境界へ接続できる
- Logical ModelとArtifact Variant分離へ発展可能になる

### Negative／Cost

- Profile SchemaとRuntime ContractのFieldが増える
- Current Mac ProfileのMigrationが必要になる
- Capability ValidationがModelとDeploymentの二段階になる
- Platform Keyの自由度と誤記防止の両立が必要になる
- Device ObservationはBackendごとの差を吸収する必要がある

### Risk Mitigation

- Phase 1-Cに必要な最小Fieldだけ実装する
- 全候補Backend用の空Classや空Directoryを作らない
- 未検証Profileを作らない
- Current Mac RegressionをAcceptance Gateとする
- Observation不能値を推測しない
- Unknown Keyの形式と参照整合をValidationする

## Alternatives Considered

### Windows専用ProfileとPowerShellだけを今追加する

短期的には分かりやすいが、Linux、Home Server、Cloud、CUDA、ROCm等で同じ再設計が必要になるため不採用。

### 全Platformを今実装する

未所有Hardware、Driver、OS、Backend Buildを検証できず、MVP Scopeと保守Costを拡大するため不採用。

### Current MacのままPhase最後まで進み、後で全修正する

Model CapabilityとDeployment Requirementの誤分類がUI、AuditおよびGovernanceへ伝播するRiskがあるため、最小Hookだけは今作る。

### VendorとAccelerationを閉じたEnumにする

型安全性は高いが、新Hardware／Plugin追加ごとにCore Releaseが必要になるため不採用。

### すべて自由文字列にする

誤記と参照不整合を検出できないため不採用。形式ValidationとDefinition参照を組み合わせる。

## Acceptance

本ADRはAcceptedである。

実装は、次を満たした後に開始する。

1. 実装担当が最新Index、本ADR、Requirements、ArchitectureおよびHandoffを読む
2. ユーザーがPhase 1-C実装開始を明示する
3. `src/`、`tests/`、`config/`、必要な`pyproject.toml`等のWrite Scopeを確認する
4. Current Mac Regressionおよび実Model／Metal Test実行許可を確認する

Decision変更時は本Fileを編集せず、新Timestampまたは新ADRを作成する。


<!-- SOURCE_END 8: docs/adr/adr_0007_deployment_platform_acceleration_abstraction_20260719013109.md -->

---

<!-- SOURCE_BEGIN 9: docs/adr/adr_0008_response_language_policy_20260719040237.md -->

### Source 9: `docs/adr/adr_0008_response_language_policy_20260719040237.md`

- History Target: `docs/project/phases/phase_1/history/adr/adr_0008_response_language_policy_20260719040237.md`
- Source SHA-512: `ead853483b0dabc3c14462bbfbcd8731f8e18cdc118488c1bb90531ad3d1bf185935873a3b8c104194d240b0deef8046acb77c1e9294dc9e738f3995d925deea`
- Source Size: `6920` bytes

# ADR-0008: Response Language Policy

- 文書ID: `adr_0008_response_language_policy`
- 状態: `accepted`
- 作成日時: `2026-07-19 04:02:37 JST`
- 更新日時: `2026-07-19 04:02:37 JST`
- 承認日時: `2026-07-19 04:02:37 JST`
- Snapshot: `20260719040237`
- Decision Owner: 設計者役担当Task
- 承認者: ユーザー
- 対象: Phase 1-D、Response Language、Config、Prompt Composition
- 正本言語: 日本語
- 要件: [phase_1d_response_language_requirements_20260719040237.md](../history/requirements/phase_1d_response_language_requirements_20260719040237.md)
- Architecture: [phase_1d_response_language_architecture_20260719040237.md](../history/architecture/phase_1d_response_language_architecture_20260719040237.md)
- 関連ADR: [adr_0006_model_runtime_port_and_configuration_20260718224308.md](../history/adr/adr_0006_model_runtime_port_and_configuration_20260718224308.md)
- 関連ADR: [adr_0007_deployment_platform_acceleration_abstraction_20260719013109.md](../history/adr/adr_0007_deployment_platform_acceleration_abstraction_20260719013109.md)
- supersedes: なし（Response Language専用の新規Decision）

## Status Decision

ユーザーはPhase 1の残りを次のように分割する方針を承認した。

```text
Phase 1-D : Response Language Policy
Phase 1-E : Thinking Presentation Policy
```

本ADRはPhase 1-Dの要件・設計Decisionを`accepted`とする。

本ADRのAccepted化はSource実装、Config変更、Test変更またはCommand実行を自動的に解禁しない。

## Context

Current Qwen3-4B Runtimeでは、回答言語を明示しない日本語Promptに対して英語で回答する場合がある。Promptへ`日本語で`を追加すると日本語になったため、Model交換とは別に、Application側でDefault Response Languageを扱う必要がある。

Default Languageを個別Prompt、llama.cpp AdapterまたはQwen固有Chat Templateへ埋め込むと、将来のModel／Backend交換時に同じPolicyを再実装する必要が生じる。

また、Thinkingの実行制御は既に存在するが、Thinkingの表示、非表示、Label、Streaming Filterおよび保存方針は別の責務である。

## Decision

### 1. Phase分割

Response LanguageをPhase 1-D、Thinking PresentationをPhase 1-Eとする。

### 2. Initial Contract

```text
ja
en
auto
```

の3値を採用する。

### 3. Default

Built-in DefaultおよびCurrent Tracked Profile Defaultを`ja`とする。

### 4. `auto`

`auto`ではApplicationが特定言語のSystem Instructionを追加しない。

Phase 1-Dでは自動言語判定Classifierを実装しない。

### 5. Ownership

Response Language Policyの解決とSystem Message CompositionはApplication／Orchestration層が所有する。

Model Portとllama.cpp AdapterはLanguage Policyを所有しない。

### 6. Precedence

```text
Per-request Explicit Override
  > Environment Override
  > Deployment Profile
  > Built-in Default
```

を採用する。

Phase 2以降にSession／User Preferenceを追加できる構造を維持する。

### 7. Config Surface

```toml
[response]
language = "ja"
```

```text
MARGPA_RESPONSE_LANGUAGE=en
--response-language en
```

を採用する。

### 8. Profile Schema

Deployment Profile構造変更を明示するため、Schema Versionを`2`から`3`へ更新する。

### 9. Natural-language Override

Default Instructionは、Userが自然文で別の回答言語を明示した場合にその指定へ従える意味とする。

Phase 1-Dでは自然文の言語指定をApplicationが解析・判定しない。

### 10. Observability

Effective LanguageとPolicy SourceをConfig／`model-info`から確認可能にする。

Applied PolicyとModelのObserved Output Languageを混同しない。

### 11. Phase 1-E Boundary

次はPhase 1-Dへ含めない。

- Thinking表示／非表示
- Thinking Label
- `<think>` Parser
- Streaming Filter
- Raw／Display Output分離
- Raw Thinking保存
- Thinking Sampling Profile

## Reasons

- 日本語を初期利用者のDefaultにできる
- Promptごとに`日本語で`と書く必要を減らせる
- 英語またはModel任せへ設定だけで切り替えられる
- Model／Backend Adapter交換時も同じPolicyを再利用できる
- 将来API／Web UIへ同じContractを公開できる
- Effective PolicyとObserved Outputを監査上分離できる
- Thinking Presentationの複雑性をPhase 1-Dへ混在させずに済む

## Consequences

### Positive

- Current CLIの日本語既定動作が明示的になる
- `ja／en／auto`をProfile、Environment、CLIから交換できる
- Language PolicyがPureなResolver／ComposerとしてTest可能になる
- 将来のGovernance Prompt Compilerへ接続しやすい

### Negative／Cost

- Profile Schema Migrationが必要になる
- System Message Composition規則が増える
- Model出力が指定言語へ完全一致する保証はない
- User自然文指示と構造化Policyが矛盾する場合を完全には判定できない

### Risk Mitigation

- Defaultと強制を区別する
- Natural-language Classifierを推測実装しない
- Deterministicな構造化OverrideだけをResolverで扱う
- User PromptとUser System Messageを破棄しない
- Model AdapterへLanguage固有処理を追加しない
- Native BehaviorだけでなくMessage CompositionをUnit Testする

## Alternatives Considered

### 全Promptへユーザーが毎回`日本語で`と書く

手作業で再現性が低く、UI／API追加時にも同じ問題が残るため不採用。

### Qwen Chat Templateへ日本語をハードコードする

Model／Backend交換性を損なうため不採用。

### llama.cpp AdapterでLanguageを制御する

Application PolicyがBackend固有責務へ漏れるため不採用。

### Promptの言語を自動判定して同じ言語で返す

Code、固有名詞、多言語Promptおよび短文で判定が不安定になり、Phase 1-D Scopeを超えるため不採用。`auto`はInstruction非注入として扱う。

### `ja／en`だけにして`auto`を持たない

Model本来のChat Template挙動との比較、明示System Messageだけを使う用途および将来の自動Policy追加に不便なため不採用。

### Response LanguageとThinking Presentationを同時実装する

Parser、Streaming、保存および表示責務が混在し、Acceptanceが大きくなるためPhase 1-D／1-Eへ分離する。

## Acceptance

本ADRはAcceptedである。

実装は、次を満たした後に開始する。

1. 実装担当が最新Index、Requirements、Architecture、本ADRおよび専用Handoffを読む
2. ユーザーがPhase 1-D実装開始を明示する
3. `src/`、`tests/`、`config/`等のWrite Scopeを確認する
4. Static／Default Testおよび必要なNative Testの実行許可を確認する

Decision変更時は本Fileを編集せず、新Timestampまたは新ADRを作成する。

<!-- SOURCE_END 9: docs/adr/adr_0008_response_language_policy_20260719040237.md -->

---

<!-- SOURCE_BEGIN 10: docs/adr/adr_0009_application_deployment_configuration_separation_20260719041847.md -->

### Source 10: `docs/adr/adr_0009_application_deployment_configuration_separation_20260719041847.md`

- History Target: `docs/project/phases/phase_1/history/adr/adr_0009_application_deployment_configuration_separation_20260719041847.md`
- Source SHA-512: `59db2466b0fe2df960d3313b17e7677e4a75fcbbdde2f5cb5efc539e03f4a8041ad43b74c1e3c7d03410cadb93dc311bd92663f479e2e1fdece918740a54b373`
- Source Size: `5529` bytes

# ADR-0009: Application／Deployment Configuration Separation

- 文書ID: `adr_0009_application_deployment_configuration_separation`
- 状態: `accepted`
- 作成日時: `2026-07-19 04:18:47 JST`
- 更新日時: `2026-07-19 04:18:47 JST`
- 承認日時: `2026-07-19 04:18:47 JST`
- Snapshot: `20260719041847`
- Decision Owner: 設計者役担当Task
- 承認者: ユーザー
- 対象: Configuration Layer、Application Config、Deployment Profile、Phase 1-D
- 正本言語: 日本語
- Requirements: [configuration_layer_requirements_20260719041847.md](../history/requirements/configuration_layer_requirements_20260719041847.md)
- Architecture: [configuration_layer_architecture_20260719041847.md](../history/architecture/configuration_layer_architecture_20260719041847.md)
- 関連ADR: [adr_0006_model_runtime_port_and_configuration_20260718224308.md](../history/adr/adr_0006_model_runtime_port_and_configuration_20260718224308.md)
- 関連ADR: [adr_0007_deployment_platform_acceleration_abstraction_20260719013109.md](../history/adr/adr_0007_deployment_platform_acceleration_abstraction_20260719013109.md)
- 修正対象ADR: [adr_0008_response_language_policy_20260719040237.md](../history/adr/adr_0008_response_language_policy_20260719040237.md)
- supersedes: ADR-0008の`response.language`配置とProfile Schema更新理由を本ADRで修正する。その他のResponse Language Decisionは維持する

## Status Decision

ユーザーは、Platform ProfileからApplication共通設定を分離し、`config/application.toml`を共通設定の正本とする方針を承認した。

本ADRを`accepted`とする。

Source／Config／Test実装は、Phase 1-D実装開始の明示許可後に行う。

## Context

Current `local_macos_arm64.toml`には次が混在している。

- Selected Model
- Model Root
- Load Config
- Generation Config
- Host／Compute／Backend／Runtime Requirement

ADR-0008では`response.language`も同じProfileへ追加する案だった。

Linux、WindowsまたはCloud Profileを増やすと、Platformと無関係なGeneration／Response設定まで複製される。

これは単一責任、交換可能性および設定の一意な正本に反する。

## Decision

### 1. Common Application Config

次を新設する。

```text
config/application.toml
```

### 2. Application-owned Fields

- Selected Model
- Model Root
- Common Load Default
- Generation Default
- Response Language Default

### 3. Deployment-owned Fields

- Host／Architecture／Execution Environment
- Compute／Vendor／Acceleration
- Backend Runtime／Build Variant
- Runtime Requirements
- Hardware-dependent Load Override

### 4. Model-owned Fields

- Artifact／Hash／Format／Quantization
- Architecture／Native Limit
- Capability／Provenance

### 5. No Generic Deep Merge

型付きContractとSection別Resolverで合成する。

### 6. Schema

```text
Application Config Schema : 1
Deployment Profile Schema : 3
```

Deployment Schema更新理由はApplication Field除去と`load_overrides`導入である。

### 7. ADR-0008 Amendment

ADR-0008の次を修正する。

```text
Old : [response]をlocal_macos_arm64.tomlへ追加
New : [response]をconfig/application.tomlへ追加
```

ADR-0008の次は維持する。

- `ja／en／auto`
- Default `ja`
- Application／Orchestration Ownership
- Environment／CLI Override
- Phase 1-D／1-E分離

## Reasons

- Platform追加時に共通値を複製せずに済む
- Generation／Language変更を一つの正本で行える
- ModelとDeploymentを独立選択できる
- Hardware TuningだけをPlatform Profileへ閉じ込められる
- Configuration Driftを減らせる
- Sourceと責務をAuditで説明しやすい

## Consequences

### Positive

- Linux／Windows Profile追加が小さくなる
- Common Config変更が全Deploymentへ一貫して反映される
- Phase 1-D Language PolicyをPlatformから分離できる
- 将来Generation／Response Presetへ拡張できる

### Negative／Cost

- Config LoaderとEffective Config Composerの変更が必要
- Current ProfileのSchema Migrationが必要
- Application ConfigとDeployment Profileの複数Fileを読む必要がある
- Field別Precedence Testが増える

### Risk Mitigation

- ConfigごとにStrict Schemaを持つ
- Deployment OverrideをAllowlist化する
- Unknown Fieldを拒否する
- Migration前後のEffective Configを比較する
- Current Mac／Metal Native RegressionをGateにする

## Alternatives Considered

### Current Profileをそのまま複製する

Platform追加ごとに共通設定が複製され、Driftするため不採用。

### 一つの巨大`config.toml`へ全Platformを書く

責務と変更範囲が拡大し、Plugin／Profile交換性が下がるため不採用。

### 全Configを汎用Deep Mergeする

Field Owner、List規則、ValidationおよびProvenanceが曖昧になるため不採用。

### Model DefinitionへGeneration Defaultを移す

GenerationはTask／利用者Preferenceでもあり、Model固有事実と一致しないため初期正本にはしない。将来Model推奨Presetとして参照可能にする。

### Platform ProfileへResponse Languageを残す

OS変更で利用者の言語Preferenceが変化する不自然な設計になるため不採用。

## Acceptance

本ADRはAcceptedである。

実装担当は最新Requirements、Architecture、Phase 1-D後継文書およびHandoffを読み、ユーザーの実装許可後に着手する。

Decision変更時は本Fileを編集せず、新Timestampまたは新ADRを作成する。

<!-- SOURCE_END 10: docs/adr/adr_0009_application_deployment_configuration_separation_20260719041847.md -->

---

<!-- SOURCE_BEGIN 11: docs/adr/adr_0010_research_runtime_phase_reorganization_20260719112304.md -->

### Source 11: `docs/adr/adr_0010_research_runtime_phase_reorganization_20260719112304.md`

- History Target: `docs/project/phases/phase_1/history/adr/adr_0010_research_runtime_phase_reorganization_20260719112304.md`
- Source SHA-512: `bc7b06ba6283117a9f2dee36fe1aac24b1738cec23178fffa1992ef5efe47a31e87ab825dd4fc58973109378adab7d6ebb12ce4e48540bed6b379f492a7fc62f`
- Source Size: `4341` bytes

# ADR-0010: AI実験・統治Platform向けPhase再編

- 文書ID: `adr_0010_research_runtime_phase_reorganization`
- 状態: `accepted`
- 作成日時: `2026-07-19 11:23:04 JST`
- 更新日時: `2026-07-19 11:23:04 JST`
- Snapshot: `20260719112304`
- Decision Owner: ユーザー
- 記録担当: 設計者役担当Task
- 正本言語: 日本語
- 関連要件: [post_phase_1e_research_platform_requirements_20260719112304.md](../history/requirements/post_phase_1e_research_platform_requirements_20260719112304.md)
- 後継Roadmap: [implementation_roadmap_20260719112304.md](../history/architecture/implementation_roadmap_20260719112304.md)
- 最新Index: [documentation_index_20260719112304.md](../history/documentation_index_20260719112304.md)
- supersedes: なし

## Context

旧Roadmapは、Phase 2をConversation Application、Phase 3をAudit／Core Governanceとし、後半にRAG、Agent、複数GDを置いていた。

その後、次の要件が優先化された。

- ARGD／DAGDを含むGovernance実行基盤
- 各Functional Layerと専用Governanceの疎結合なON／OFF
- `off／observe／enforce`の比較
- Experiment Profile、Run Identity、Config／Artifact／Definition Digest
- Event-driven Runtime Status
- Macと外部Linux／CUDA環境での並行検証
- UIからのTyped Config調整
- 特定GDをハードコードしない汎用Definition Platform

これらは単なる後付けFeatureではなく、後続するGuard、Judge、Repair、RAG、Agentの基盤である。UIを先に固定すると、その後にComponent Switch、Status、Experiment、Governance Bindingを追加する際の手戻りが大きい。

## Decision

Phase 1-E完了後のRoadmapを再編する。

```text
Phase 0   Project Definition／Technology Selection
Phase 1   Portable Model Runtime Foundation
Phase 2   Experimental Runtime Control Plane
Phase 3   Generic Governance Definition Platform + MARGPA Main Governance
Phase 4   Conversation Application／Web UI
Phase 5   Guardrail／Security／Policy
Phase 6   Judge／Evaluation／Repair
Phase 7   RAG／Data Governance
Phase 8   Agent／Tool／Memory
Phase 9   Multi-Governance Orchestration
Phase 10  Hardening／Public Release／Expansion
```

UIの前にPhase 2として、Component Registry、Experiment Runtime、Event／Status／Minimal Audit、Lightning AI Studio対応を置く。

## Rationale

1. UIの前にTyped Runtime Contractを作ると、CLI、API、UI、Experiment Runnerが同じContractを使える。
2. Governance実装前にBaseline、Mode、Run Recordを持つことで、Governanceの効果と負荷を比較できる。
3. MacだけでArchitectureを固める前にLinux／CUDAでPortabilityを検証できる。
4. Main Governanceで汎用Definition Platformを実証した後、Guard／Judge／Agentへ同じPoint／Binding Contractを展開できる。
5. 全当初Scopeを失わず、中間Milestoneを明確にできる。

## Consequences

### Positive

- Phase 2完了時点で、外部環境と実験に耐えるRuntime骨格ができる。
- UIがSource／Config固有のロジックを持たなくなる。
- 後続Layerの実験構成を比較できる。
- 複数GDとDynamic RoutingをMVP中核から切り離し、Phase 9へ延期できる。

### Negative

- Web UIの着手は旧Roadmapより後ろになる。
- Phase 2で直接ユーザーに見えにくいControl Plane実装が増える。
- Phase数とPhase Gateが増える。

### Mitigation

- Phase 1のCLIで各Phaseの受入確認を継続する。
- Phase 2は最小ContractとBaselineを優先し、実装前のFunctional Layerを作り込まない。
- 各PhaseのMilestoneと実装境界をRoadmapで固定する。

## Alternatives Considered

### Alternative A: 旧RoadmapのままUIを先行

却下。後からComponent Registry、Status Event、Experiment、Typed Config ServiceをUIの下に入れる手戻りが大きい。

### Alternative B: 全機能を同時に実装

却下。M2 Pro／16GBと試作品の優先順位に合わず、受入条件と問題範囲が不明確になる。

### Alternative C: GovernanceをGuard／Judge後に一括実装

却下。各LayerのContractがGovernanceとExperimentを考慮しないまま固定される。

## Authorization Boundary

本ADRはPhase再編のDecisionをAcceptedとする。個別Phaseの実装解禁を意味しない。

<!-- SOURCE_END 11: docs/adr/adr_0010_research_runtime_phase_reorganization_20260719112304.md -->

---

<!-- SOURCE_BEGIN 12: docs/adr/adr_0011_shared_governance_control_plane_and_distributed_points_20260719112304.md -->

### Source 12: `docs/adr/adr_0011_shared_governance_control_plane_and_distributed_points_20260719112304.md`

- History Target: `docs/project/phases/phase_1/history/adr/adr_0011_shared_governance_control_plane_and_distributed_points_20260719112304.md`
- Source SHA-512: `1f817ac3c07176eaf950662800d75d9007310bfacdd30f6fa7f1c83d80ff9cff43a0538b2750502d09becaece4a14172fbb3a4c3302c28070307db7e95e0214b`
- Source Size: `3624` bytes

# ADR-0011: 共有Governance Control Planeと分散Enforcement Point

- 文書ID: `adr_0011_shared_governance_control_plane_and_distributed_points`
- 状態: `accepted`
- 作成日時: `2026-07-19 11:23:04 JST`
- 更新日時: `2026-07-19 11:23:04 JST`
- Snapshot: `20260719112304`
- Decision Owner: ユーザー
- 記録担当: 設計者役担当Task
- 正本言語: 日本語
- 関連Architecture: [governance_control_plane_architecture_20260719112304.md](../history/architecture/governance_control_plane_architecture_20260719112304.md)
- 最新Index: [documentation_index_20260719112304.md](../history/documentation_index_20260719112304.md)
- supersedes: なし

## Context

将来のMain Model、Guard、Judge、Repair、Agent、Tool、RAG、Policy等にそれぞれ専用Governanceを配置したい。

一方で、全層を1つの巨大Governance Layerが毎回一括管理すると、無関係なRule、Prompt、Model Callが増える。逆に各Layerへ完全なMARGPA一式を複製すると、Definition、State、Audit、Actionの重複と矛盾が発生する。

## Decision

次の3要素に分離する。

1. 共有Governance Control Plane／Kernel
2. Functional Component境界の軽量Governance Enforcement Point
3. Definition／Profile／Mode／BudgetをPointへ接続するGovernance Binding

決定論的Ruleを優先し、必要なときだけSemantic Evaluatorを呼ぶ。すべてのPointがARGD／DAGD全体を毎回再評価する構成にしない。

## Rationale

- Definition／Compiler／Audit／Action Resolverを共通化できる。
- PointはそのComponentに必要なRuleだけを使える。
- Functional ComponentとGovernanceを個別に無効化・交換できる。
- 複数ActionとAuthorityを中央Resolverで整合できる。
- Definitionの内容とPipeline上の配置をBindingで分離できる。

## Detailed Constraints

- StateはShared Turn／Session Context、Point-local Namespace、Append-Only Evidenceに分ける。
- `off／observe／enforce`をBindingのModeとする。
- Pointが呼ばれない場合、そのGovernanceも実行しない。
- Lazy Load、Rule Selection、Plan Cache、Call／Token／Latency／Repair Budgetを必須とする。
- Unknown ActionをJSONの指示だけで実行しない。
- Governance-on-governanceの無限再帰を禁止する。Meta Reviewは将来、原則OFF／非同期／Max Depth 1とする。

## Consequences

### Positive

- Governanceの共通部とDomain固有部が分離される。
- Guard／Judge／Agent等を追加するたびに統治基盤を複製せずに済む。
- Pointごとの負荷、効果、Errorを計測できる。
- ComponentとGovernanceの組み合わせ実験が容易になる。

### Negative

- Point Contract、Binding Resolver、State Namespace、Action Resolverが必要になる。
- 単純な直列Middlewareより概念数が増える。
- 複数PointのOrdering、Conflict、Failure Policyを設計する必要がある。

## Alternatives Considered

### Alternative A: 中央の単一巨大Governance Layer

却下。すべてのDomain Ruleを毎ターン評価しやすく、負荷、Scope、障害範囲が大きい。

### Alternative B: 各Layerへ完全なGovernance基盤を複製

却下。Registry、Definition、State、Evidence、Action Resolutionが重複し、不整合と保守負荷を増やす。

### Alternative C: Functional Component内へGovernanceを直書き

却下。Guard、Judge、Agent、Model Adapterの交換性を損ねる。

## Authorization Boundary

本ADRはArchitecture DecisionをAcceptedとする。Implementationは個別Phaseの解禁後に行う。

<!-- SOURCE_END 12: docs/adr/adr_0011_shared_governance_control_plane_and_distributed_points_20260719112304.md -->

---

<!-- SOURCE_BEGIN 13: docs/adr/adr_0012_optional_generic_governance_definition_platform_20260719112304.md -->

### Source 13: `docs/adr/adr_0012_optional_generic_governance_definition_platform_20260719112304.md`

- History Target: `docs/project/phases/phase_1/history/adr/adr_0012_optional_generic_governance_definition_platform_20260719112304.md`
- Source SHA-512: `9c779bc00d839d2d0aafbe2a146cf136cb9e69684884ec535ba7b9981d6c02bc5f11ce7540943bc24c7eb762ed02d9c8df8097f859b590bdf19a9932d53a9833`
- Source Size: `4718` bytes

# ADR-0012: 全GD任意・0件Baselineの汎用Definition Platform

- 文書ID: `adr_0012_optional_generic_governance_definition_platform`
- 状態: `accepted`
- 作成日時: `2026-07-19 11:23:04 JST`
- 更新日時: `2026-07-19 11:23:04 JST`
- Snapshot: `20260719112304`
- Decision Owner: ユーザー
- 記録担当: 設計者役担当Task
- 正本言語: 日本語
- 関連要件: [generic_governance_definition_platform_requirements_20260719112304.md](../history/requirements/generic_governance_definition_platform_requirements_20260719112304.md)
- 関連Architecture: [governance_definition_platform_architecture_20260719112304.md](../history/architecture/governance_definition_platform_architecture_20260719112304.md)
- 最新Index: [documentation_index_20260719112304.md](../history/documentation_index_20260719112304.md)
- supersedes: なし

## Context

現在参照しているARGD／DAGDと、将来追加予定のCDOGD、AISGD、AAGD、MPGD等がある。ただし、実際の利用者は、それらと無関係なGD、まったく異なる名前、異なるSchema、またはDefinition 0件の構成を使う可能性がある。

特定GD名、数、Path、Category、Schema、CDOGDの存在をCoreにハードコードすると、Governance Definition交換性の主張が成立しない。

## Decision

- Governance DefinitionをOptional Pluginとする。
- ARGD／DAGDも必須Dependencyにしない。
- Definition 0件を正式なProduction Baselineとする。
- CoreはGD名、GD数、File名、Directory、Domain、Point IDのClosed Listを持たない。
- Provider／Manifest／Descriptor／Adapter／Normalized IR／Compiler／Bindingを通じて取り込む。
- `EmptyDefinitionProvider`を正式実装とする。
- Manifest Firstを推奨し、標準Envelopeがある場合のみContent Discoveryを許容する。
- Filename-based Discovery／Semanticsを禁止する。
- JSONはDataのみとし、Custom Adapterは別のTrusted Pluginとする。
- CDOGDも任意とし、Dynamic RoutingはOrchestration Capabilityを持つDefinitionがある場合のみ有効化できる。

## Mode Semantics with No Definitions

| Mode | Decision |
|---|---|
| `off` | Pass-through |
| `observe` | `inactive_no_definitions` + Warning。RequiredならError |
| `enforce` | Required Governance MissingとしてRefuse／Error |

Definition 0件でEnforcement Successを記録することを禁止する。

## Rationale

1. 実際に誰がどのGDを使うか予測できない。
2. 将来のGD追加でCore修正を必要にしないことが交換性の必要条件である。
3. ARGD／DAGDありとなしを比較できること自体が研究上重要である。
4. FilenameやJSONの存在だけで行動を実行するのは誤解釈とSecurity Riskを招く。
5. SourceをImmutableにし、Adapter／IR／Adjustmentで吸収すれば、Author定義とRuntime調整を分離できる。

## Consequences

### Positive

- Definition 0件でMain Runtimeを使える。
- Catalog外のCustom Definitionを取り込める。
- ARGD／DAGDを特別扱いせずに第一実証として使える。
- CDOGDがなくてもManual／Static Routingを使える。
- Invalid／Unsupported PackageをQuarantineし、影響範囲を限定できる。

### Negative

- Manifest、Descriptor、Adapter Registry、IR、Compiler等の概念が必要になる。
- 任意JSONを自動で完全解釈できるわけではない。Custom SchemaにはAdapterが必要になる。
- DefinitionのState、Dependency、Conflict、Versionを管理する必要がある。

## Alternatives Considered

### Alternative A: ARGD／DAGDをBuilt-in必須にする

却下。Empty Baseline、他者Definitionの利用、統治なし比較を阻害する。

### Alternative B: 16 GDのClass／Loaderを先に作る

却下。未来のGD名とSchemaをCoreに固定し、未使用の実装工数を増やす。

### Alternative C: Directory内のJSONを全て自動解釈

却下。無関係JSON、Malformed JSON、Custom Schemaの誤解釈とSecurity Riskがある。

### Alternative D: CDOGDをRoutingの必須Coreにする

却下。CDOGDが不在、空、Custom Orchestratorに交換される構成を阻害する。

## Acceptance Proof

第一の拡張性証明は次とする。

1. 0 DefinitionでRuntimeが動作する。
2. 任意名のDefinition、Manifest、Adapter、Bindingを追加する。
3. Core変更なしでObserve実行できる。
4. 必要なAction Adapter／Authorityを追加しEnforceできる。
5. Definitionを外し0 Definitionに戻る。

## Authorization Boundary

本ADRはDecisionのみAcceptedとし、Definition Directory、Manifest、Adapter、Sourceの作成は個別の実装許可まで行わない。

<!-- SOURCE_END 13: docs/adr/adr_0012_optional_generic_governance_definition_platform_20260719112304.md -->

---

<!-- SOURCE_BEGIN 14: docs/adr/adr_0013_lightning_ai_studio_external_development_20260719112304.md -->

### Source 14: `docs/adr/adr_0013_lightning_ai_studio_external_development_20260719112304.md`

- History Target: `docs/project/phases/phase_1/history/adr/adr_0013_lightning_ai_studio_external_development_20260719112304.md`
- Source SHA-512: `77bbbd39c2516c111f3a8ca7ae72a966164402e15dfb0e14922a4c4319541af8a6a41f3d2184c586826e0a1ece818da083a7adecba5f567a9930810a2696e990`
- Source Size: `3922` bytes

# ADR-0013: 第一外部開発・検証環境にLightning AI Studioを採用

- 文書ID: `adr_0013_lightning_ai_studio_external_development`
- 状態: `accepted`
- 作成日時: `2026-07-19 11:23:04 JST`
- 更新日時: `2026-07-19 11:23:04 JST`
- Snapshot: `20260719112304`
- Decision Owner: ユーザー
- 記録担当: 設計者役担当Task
- 正本言語: 日本語
- 関連Architecture: [lightning_ai_studio_cross_environment_architecture_20260719112304.md](../history/architecture/lightning_ai_studio_cross_environment_architecture_20260719112304.md)
- 最新Index: [documentation_index_20260719112304.md](../history/documentation_index_20260719112304.md)
- supersedes: なし

## Context

現行の開発・検証環境はmacOS／Apple Silicon／Metalである。将来のCloud／Home Server／GPU Serverへの移行を考慮し、Macと並行してLinux／CUDA環境でも同じRepositoryを開発・検証したい。

候補はHugging Face ZeroGPUとLightning AI Studioであった。

現行RuntimeはPython 3.13、GGUF、llama.cpp／llama-cpp-pythonを中心とする。ZeroGPUは公開DemoとGPU費用の面で魅力があるが、公式仕様上Gradio／PyTorch中心で、GPU Lifecycle、Python Version、Quotaに対する追加Adapterが必要になる。

## Decision

- Phase 2-Dの第一外部開発／検証環境にLightning AI Studioを採用する。
- 同一Repository、GGUF、Model Port、Config Contract、Test Contractを使用する。
- Linux x86_64／NVIDIA CUDA／llama.cppのDeployment ProfileとSetup Recipeを追加する。
- ModelはGitに含めず、Persistent Storageへ配置しDigestを検証する。
- Hugging Face ZeroGPUはPhase 10の公開Demo／PyTorch Backend交換性実証に延期する。

## Rationale

1. Lightning AI Studioは通常のLinux開発環境としてRepositoryを実行できる。
2. SSH、VS Code、永続Storage、GPU、Port公開を利用できる。
3. llama.cppのMetal BuildからCUDA Buildへの差分はDeployment／Acceleration Adapterで吸収しやすい。
4. ZeroGPU向けのTransformers／PyTorch／Gradio Adapterを現時点で先行実装するより、CoreのPortability検証を早く行える。
5. ZeroGPUを後で追加すること自体がBackend交換性の別の実証になる。

## Consequences

### Positive

- Mac MetalとLinux CUDAの2環境でPortabilityを検証できる。
- 現行GGUF Modelとllama.cpp Adapterを再利用できる。
- 将来のHome Server／Cloud GPU移行の学習と検証になる。

### Negative

- LightningのAccount、Cost、Persistence、GPU割当を管理する必要がある。
- CUDA Native BuildとLinux固有検証が追加される。
- 無料公開Demoはすぐには得られない。

## Alternatives Considered

### Alternative A: Hugging Face ZeroGPUを先に採用

今回は却下。現行Runtimeとは別のPyTorch／Transformers／Gradio Adapter、GPU Decorator／Lifecycle対応が必要で、目的に対する追加工事が大きい。Phase 10の候補として保持する。

### Alternative B: Macのみで後回し

却下。Platform／Acceleration Abstractionの問題を後半まで発見できない可能性がある。

### Alternative C: AWS／Azureを直接採用

現時点では延期。Infrastructure、Credential、Cost、DeploymentのScopeが広がる。

## Official References

- [Hugging Face ZeroGPU documentation](https://huggingface.co/docs/hub/main/en/spaces-zerogpu)
- [Lightning AI Studio overview](https://lightning.ai/docs/overview/ai-studio/)
- [Connect a local IDE to Lightning Studio](https://lightning.ai/docs/platform/build/ai-studio/connect-local-ide)
- [Lightning SDK Studio documentation](https://lightning.ai/docs/overview/sdk/studio)

## Authorization Boundary

本ADRは技術選定をAcceptedとする。Lightning Studio作成、GPU利用、課金、Upload／Download、Repository変更は別途の実装／外部操作許可が必要である。

<!-- SOURCE_END 14: docs/adr/adr_0013_lightning_ai_studio_external_development_20260719112304.md -->

---

<!-- SOURCE_BEGIN 15: docs/adr/adr_0014_thinking_execution_presentation_and_persistence_separation_20260719123547.md -->

### Source 15: `docs/adr/adr_0014_thinking_execution_presentation_and_persistence_separation_20260719123547.md`

- History Target: `docs/project/phases/phase_1/history/adr/adr_0014_thinking_execution_presentation_and_persistence_separation_20260719123547.md`
- Source SHA-512: `f9a113d3108b0d698249a95808ed01391fb6a4ee3e593f206d8a15a4ccff17f58bd116cf56bb7c64b434b9f276b079435f1ed6dc5b692da0cb5d9d7fd688771d`
- Source Size: `8121` bytes

# ADR-0014: Thinking Execution、Presentation、Persistenceの分離

- 文書ID: `adr_0014_thinking_execution_presentation_and_persistence_separation`
- 状態: `proposed`
- 作成日時: `2026-07-19 12:35:47 JST`
- 更新日時: `2026-07-19 12:35:47 JST`
- Snapshot: `20260719123547`
- Decision Owner: 設計者役担当Task
- 承認者: ユーザーReview待ち
- 対象: Phase 1-E Thinking Presentation
- 正本言語: 日本語
- Requirements: [phase_1e_thinking_presentation_requirements_20260719123547.md](../history/requirements/phase_1e_thinking_presentation_requirements_20260719123547.md)
- Architecture: [phase_1e_thinking_presentation_architecture_20260719123547.md](../history/architecture/phase_1e_thinking_presentation_architecture_20260719123547.md)
- 実装担当Handoff: [designer_handoff_phase_1e_thinking_presentation_20260719123547.md](../history/handoffs/designer_handoff_phase_1e_thinking_presentation_20260719123547.md)
- 関連ADR: [adr_0006_model_runtime_port_and_configuration_20260718224308.md](../history/adr/adr_0006_model_runtime_port_and_configuration_20260718224308.md)
- 関連ADR: [adr_0009_application_deployment_configuration_separation_20260719041847.md](../history/adr/adr_0009_application_deployment_configuration_separation_20260719041847.md)
- supersedes: なし（ADR新規系列）

## Status Decision

本ADRは`proposed`である。

ユーザーはPhase 1-Eの要件・設計開始を指示したが、本書で初めて具体化したDefault、Malformed Policy、Schema MigrationおよびParser境界は、ユーザーの確認後にAcceptedとする。

本ADRの作成はSource／Config／Test実装を自動的に解禁しない。

## Context

Phase 1-BでQwen3のThinking Execution Controlを実装した。Current CLIの`--thinking`はModelへThinkingを要求し、Modelが`<think>...</think>`を生成した場合、Raw Textをそのままstdoutへ出力する。

しかし、次は異なる責務である。

- ModelにThinkingを実行させること
- Model Output Protocolを解釈すること
- Reasoningを利用者へ見せること
- Raw Reasoningを保存すること

同一Flagへ統合すると、将来のUI、Audit、Governance、Model交換および比較実験で責務が混同する。

## Proposed Decision

### 1. Four-way Separation

```text
Execution    : generation.thinking_mode
Parsing      : model output protocol + parser
Presentation : presentation.thinking.visibility／display_label
Persistence  : presentation.thinking.persistence
```

一つの設定が別の設定を暗黙変更しない。

### 2. Defaults

```text
thinking_mode : disabled
visibility    : hidden
display_label : 推論
persistence   : disabled
```

### 3. Application Config Schema 2

`config/application.toml`に`[presentation.thinking]`を追加し、Application Schemaを`2`へ更新する。

Deployment Profile Schema `3`は変更しない。

### 4. User Override

VisibilityとDisplay LabelはApplication Config、Environment、CLIから変更可能とする。

```text
Explicit > Environment > Application > Built-in
```

PersistenceはPhase 1-Eで`disabled`だけを許可し、Environment／CLI Overrideを設けない。

### 5. Canonical ProtocolとDisplay Label

Canonical `<think>...</think>`はModel Protocolであり、User Preferenceで変更しない。

利用者が変更するのはDisplay Labelである。

```text
Canonical : <think>...</think>
Display   : <推論>...</推論>
Custom    : <思考過程>...</思考過程>
```

### 6. Output Protocol Declaration

Parser選択をModel Key、ArchitectureまたはBackendのハードコードで行わない。

Model Definition Schema `2`でParser KeyとCanonical Delimiterを宣言する。

```toml
[output_protocol.thinking]
parser_key = "tagged_thinking_v1"
opening_delimiter = "<think>"
closing_delimiter = "</think>"
```

Unknown Parser KeyはExplicit Errorとする。

### 7. Independent Presentation Module

Model Portとllama.cpp AdapterのRaw Contractは維持し、後段のPresentation ModuleでParserとRendererを合成する。

Output Protocol Parserは`adapters/output_protocols/`に置き、llama.cpp Backend Adapterから分離する。

### 8. Shared Stateful Parser

Non-streamingとStreamingで同じState Machineを使用する。

ChunkごとのRegex置換を作らない。Delimiter分割を扱い、Hidden ModeでReasoningを一瞬も表示しない。

### 9. Malformed Policy

- Openingなし: 全TextをFinalとする
- Openingあり／Closingなし: `unclosed_reasoning`
- Hidden: 検出済みReasoningを表示しない
- Visible: Display Closing TagをPresentation上補完する
- Extra Delimiter: 黙って削除せずWarningとする

HiddenはGuardrailまたはSecret Filterではない。

### 10. No Automatic Sampling Switch

`thinking_mode`の切替でTemperature／Top-p／Presence Penalty等を暗黙変更しない。

Thinking用PresetはPhase 2以降のExplicit Experiment Profile候補とする。

### 11. No Raw Persistence

Phase 1-EでRaw ReasoningのDisk保存を追加しない。

VisibleはPersistedを意味しない。

## Consequences

### Positive

- Thinkingを実行しながらFinalだけ表示できる
- Display LabelをModel Protocolを壊さず変更できる
- CLI／将来API／Web UIで同じPresentation Contractを使える
- Streaming HiddenのFlashを防げる
- Model／Backend交換時にParser KeyをDefinitionから選べる
- Raw Backend Contractを保持できる
- Audit保存とUI表示を分離できる
- 実験時の暗黙Sampling変更を防げる

### Negative／Cost

- Application ConfigとModel DefinitionのSchema Migrationが必要
- Presentation Module、Parser Port、Parser Registryが追加される
- Streaming State MachineとChunk分割Testが必要
- Malformed Outputに対するStatus／Warning Contractが増える
- VisibleでRaw Reasoningを見せることの意味をUser Manualで説明する必要がある

## Risk Mitigation

- Existing Raw Contractを変更しない
- Parser／RendererをPure Unit Test中心で検証する
- Delimiterの全Split PositionをParameterizeする
- Hidden No-flashをAcceptance Criterionにする
- LabelをStrict Validationする
- Unknown Parser KeyをLoad前に拒否する
- Native TestでContent全文一致ではなくProtocol境界を検証する
- Raw Persistenceを明示的に`disabled`へ制限する

## Alternatives Considered

### `--thinking`で表示も同時にONにする

ExecutionとPresentationが再び結合するため不採用。

### CLIで`<think>`をRegex削除する

Chunk分割、Malformed、将来UI共通化を扱えないため不採用。

### llama.cpp Adapter内でFinalだけを返す

Backend AdapterがDisplay Policyを所有し、Raw Contractが失われるため不採用。

### Qwen3またはModel KeyでParser分岐する

将来のModel交換とCustom Modelでハードコードが増えるため不採用。

### Canonical Tag自体をUser Configで変更する

Chat Template／Model Protocolと合わなくなりParseが壊れるため不採用。

### HiddenでRaw Reasoningを一度表示後に削除する

TerminalやUIでFlashが発生し、非表示Contractを満たさないため不採用。

### Thinking Flagで推奨Sampling値へ自動変更する

暗黙副作用と実験再現性低下のためPhase 1-Eでは不採用。

### Raw ReasoningをResult／Logに常時複製保存する

保存量、Privacy、内部推論との一致主張およびAudit Policyの未確定のため不採用。

## Decision Gate

ユーザーは次を一組として承認または修正する。

1. Default `thinking_mode=disabled`
2. Default `visibility=hidden`
3. Default `display_label=推論`
4. Raw Persistenceは`disabled`のみ
5. Application Config Schema `2`
6. Model Definition Schema `2`とParser Key宣言
7. Model Port後段の独立Presentation Module
8. Stateful Streaming Parser
9. Unclosed ReasoningのHidden／Visible Fallback
10. ThinkingによるSampling自動切替なし

## Acceptance

本ADRは現時点でProposedである。

ユーザー承認時は本Fileを編集せず、新TimestampのAccepted後継ADRを作成する。


<!-- SOURCE_END 15: docs/adr/adr_0014_thinking_execution_presentation_and_persistence_separation_20260719123547.md -->

---

<!-- SOURCE_BEGIN 16: docs/adr/adr_0014_thinking_execution_presentation_and_persistence_separation_20260719130303.md -->

### Source 16: `docs/adr/adr_0014_thinking_execution_presentation_and_persistence_separation_20260719130303.md`

- History Target: `docs/project/phases/phase_1/history/adr/adr_0014_thinking_execution_presentation_and_persistence_separation_20260719130303.md`
- Source SHA-512: `b27c1bd63d8be6bc2f251783eae85356e985a854ba8b60d5179eec79d4191fcb86cfb4173796392ec6970fc0134895febd430f5f2aad3a35455abee4f70a9a1f`
- Source Size: `7353` bytes

# ADR-0014: Thinking Execution、Presentation、Persistenceの分離

- 文書ID: `adr_0014_thinking_execution_presentation_and_persistence_separation`
- 状態: `accepted`
- 作成日時: `2026-07-19 13:03:03 JST`
- 更新日時: `2026-07-19 13:03:03 JST`
- 承認日時: `2026-07-19 13:03:03 JST`
- Snapshot: `20260719130303`
- Decision Owner: 設計者役担当Task
- 承認者: ユーザー
- 対象: Phase 1-E Thinking Presentation
- 正本言語: 日本語
- Requirements: [phase_1e_thinking_presentation_requirements_20260719130303.md](../history/requirements/phase_1e_thinking_presentation_requirements_20260719130303.md)
- Architecture: [phase_1e_thinking_presentation_architecture_20260719130303.md](../history/architecture/phase_1e_thinking_presentation_architecture_20260719130303.md)
- 実装担当Handoff: [designer_handoff_phase_1e_thinking_presentation_20260719130303.md](../history/handoffs/designer_handoff_phase_1e_thinking_presentation_20260719130303.md)
- 関連ADR: [adr_0006_model_runtime_port_and_configuration_20260718224308.md](../history/adr/adr_0006_model_runtime_port_and_configuration_20260718224308.md)
- 関連ADR: [adr_0009_application_deployment_configuration_separation_20260719041847.md](../history/adr/adr_0009_application_deployment_configuration_separation_20260719041847.md)
- supersedes: `adr_0014_thinking_execution_presentation_and_persistence_separation_20260719123547.md`

## Status Decision

ユーザーはPhase 1-Eの提案Decisionを承認し、Default Display Labelだけを`推論`から`高度推論`へ変更した。

本ADRを`accepted`とする。

Accepted化は設計Decisionの確定であり、Source／Config／Test実装の自動解禁ではない。

## Context

Current Runtimeは`ThinkingMode`とCLIの`--thinking`を持つが、Modelが生成した`<think>...</think>`をRaw Textのまま表示する。

次は異なる責務である。

- Thinking実行
- Model Output Protocol解釈
- Reasoning表示
- Raw Reasoning保存

これらを同一Flagにすると、将来のUI、Audit、Governance、Model交換および比較実験で責務が混同する。

## Decision

### 1. Four-way Separation

```text
Execution    : generation.thinking_mode
Parsing      : model output protocol + parser
Presentation : presentation.thinking.visibility／display_label
Persistence  : presentation.thinking.persistence
```

一つの設定が別設定を暗黙変更しない。

### 2. Defaults

```text
thinking_mode : disabled
visibility    : hidden
display_label : 高度推論
persistence   : disabled
```

`高度推論`はThinking On時のDisplay Channelを通常回答から区別するLabelである。高品質、正しさまたは真の内部推論であることを保証しない。

### 3. Application Config Schema 2

`config/application.toml`に次を追加する。

```toml
[presentation.thinking]
visibility = "hidden"
display_label = "高度推論"
persistence = "disabled"
```

Application Schemaを`2`へ更新し、Deployment Profile Schema `3`は変更しない。

### 4. User Override

VisibilityとDisplay Labelは次のPrecedenceで解決する。

```text
Explicit > Environment > Application > Built-in
```

PersistenceはPhase 1-Eで`disabled`だけを許可し、Environment／CLI Overrideを設けない。

### 5. Canonical Protocol／Display Label

Canonical `<think>...</think>`はModel Protocolであり、User Preferenceで変更しない。

利用者が変更するのはDisplay Labelだけとする。

```text
Canonical : <think>...</think>
Default   : <高度推論>...</高度推論>
Custom    : <思考過程>...</思考過程>
```

### 6. Model-declared Output Protocol

Parser選択をModel Key／Architecture／Backend名のハードコードで行わない。

Model Definition Schema `2`でParser KeyとCanonical Delimiterを宣言する。

```toml
[output_protocol.thinking]
parser_key = "tagged_thinking_v1"
opening_delimiter = "<think>"
closing_delimiter = "</think>"
```

Unknown Parser KeyはExplicit Errorとする。

### 7. Independent Presentation Module

Model Portとllama.cpp AdapterのRaw Contractを維持し、後段Presentation ModuleでParserとRendererを合成する。

Output Protocol Parserは`adapters/output_protocols/`に置き、llama.cpp Backend Adapterから分離する。

### 8. Shared Stateful Parser

Non-streamingとStreamingで同じState Machineを使用する。

Chunk単位Regex置換は使用しない。Delimiter分割を扱い、Hidden ModeでReasoningを一瞬も表示しない。

### 9. Malformed Policy

- Openingなし: 全TextをFinal
- Openingあり／Closingなし: `unclosed_reasoning`
- Hidden: 検出済みReasoningを非表示
- Visible: Display Closing TagをPresentation上補完
- Extra Delimiter: 無断削除せずWarning

HiddenはGuardrailまたはSecret Filterではない。

### 10. No Automatic Sampling Switch

`thinking_mode`の切替でTemperature／Top-p／Presence Penalty等を暗黙変更しない。

Thinking用PresetはPhase 2以降のExplicit Experiment Profile候補とする。

### 11. No Raw Persistence

Phase 1-EでRaw ReasoningのDisk保存を追加しない。VisibleはPersistedを意味しない。

## Consequences

### Positive

- Thinkingを実行しながらFinalだけ表示できる
- Display LabelをModel Protocolを壊さず変更できる
- CLI／将来API／Web UIで同じPresentation Contractを使える
- Streaming HiddenのFlashを防げる
- Model／Backend交換時にParser KeyをDefinitionから選べる
- Raw Backend Contractを保持できる
- Audit保存とUI表示を分離できる
- 実験時の暗黙Sampling変更を防げる

### Negative／Cost

- Application ConfigとModel DefinitionのSchema Migrationが必要
- Presentation Module、Parser Port、Parser Registryが増える
- Streaming State Machine／Chunk Split Testが必要
- Malformed OutputのStatus／Warning Contractが必要
- Visible Reasoningの意味をUser Manualで説明する必要がある

## Risk Mitigation

- Existing Raw Contractを変更しない
- Parser／RendererをPure Unit Test中心で検証する
- Delimiterの全Split PositionをParameterizeする
- Hidden No-flashをAcceptance Criterionにする
- LabelをStrict Validationする
- Unknown Parser KeyをLoad前に拒否する
- Raw Persistenceを`disabled`へ制限する

## Alternatives Considered

### `--thinking`で表示もON

ExecutionとPresentationが再結合するため不採用。

### CLI RegexでTag削除

Chunk Split、Malformed、将来UI共通化を扱えないため不採用。

### llama.cpp AdapterがFinalだけ返す

Backend AdapterがDisplay Policyを所有しRaw Contractが失われるため不採用。

### Qwen3／Model KeyでParser分岐

Model交換／Custom Modelでハードコードが増えるため不採用。

### Canonical TagをUser Configで変更

Model Protocol／Chat Templateと合わずParserが壊れるため不採用。

### Thinking FlagでSamplingを自動変更

暗黙副作用と実験再現性低下のため不採用。

### Raw Reasoningを常時保存

保存量、Privacy、内部推論との一致主張、Audit Policy未確定のため不採用。

## Acceptance

本ADRはAcceptedである。

Decisionを変更する場合は本Fileを編集せず、新Timestampの後継ADRを作成する。

Phase 1-E実装はユーザーの明示的な実装開始許可後に限る。


<!-- SOURCE_END 16: docs/adr/adr_0014_thinking_execution_presentation_and_persistence_separation_20260719130303.md -->

---

<!-- SOURCE_BEGIN 17: docs/adr/adr_0015_phase_1f_lightning_and_python_312_support_20260719202333.md -->

### Source 17: `docs/adr/adr_0015_phase_1f_lightning_and_python_312_support_20260719202333.md`

- History Target: `docs/project/phases/phase_1/history/adr/adr_0015_phase_1f_lightning_and_python_312_support_20260719202333.md`
- Source SHA-512: `3703da1c7e7a6b44d39e475893948c15d0cb91d3822183e56215df6d11e5e76de83609c09e679654c372cbec3f2292fd53375cbd7447fe452a3608fa0ab5eacd`
- Source Size: `4341` bytes

# ADR-0015: Lightning対応をPhase 1-Fへ前倒ししPython 3.12を正式Supportする

- 文書ID: `adr_0015_phase_1f_lightning_and_python_312_support`
- 状態: `accepted`
- 作成日時: `2026-07-19 20:23:33 JST`
- 更新日時: `2026-07-19 20:23:33 JST`
- Snapshot: `20260719202333`
- Decision Owner: ユーザー
- 記録担当: 設計者役担当Task
- 正本言語: 日本語
- 要件: [phase_1f_lightning_cross_environment_runtime_requirements_20260719202333.md](../history/requirements/phase_1f_lightning_cross_environment_runtime_requirements_20260719202333.md)
- Roadmap: [implementation_roadmap_20260719202333.md](../history/architecture/implementation_roadmap_20260719202333.md)
- supersedes: なし（ADR-0013を破棄せずPhase配置とPython Supportを具体化）

## Context

当初、Lightning AI Studio実装は後続のExternal Linux Phaseへ置いていた。一方、次の事情からPhase 1完了時点で一度公開する必要が生じた。

- ユーザーの生活上の期限
- Codex／GPT利用可能量と課金上の制約
- 各Phase完了時点でMacとLightningの両環境を比較検証したい
- 将来のModel／機材交換に備え、早期に第二Environmentを成立させたい

LightningのObserved EnvironmentはPython 3.12.11である。Current ProjectはSource Syntax上はPython 3.12で実行可能な見込みが高いが、Metadata、Lock、Static Tool、Setup／VerificationをPython 3.13専用へ固定している。

## Decision

1. Lightning AI Studio対応をPhase 6からPhase 1-Fへ前倒しする。
2. Phase 1の正式Support範囲をCPython 3.12／3.13へ広げる。
3. Local Mac PrimaryはCPython 3.13.14のままとする。
4. Lightningは既設CPython 3.12.11で開始し、期限のためだけに3.13へUpgradeしない。
5. `requires-python`、Lock、Ruff／Mypy基準をPython 3.12最小Supportへ整合させる。
6. Lightning CUDA Native RuntimeをPhase 1-Fの必須Gateとする。
7. Lightning CPU Profileも実装対象とするが、同一CUDA BuildでGPU未割当CPU実行が成立しない場合、期限と工数を再評価し、CPUを明示Known Limitationとして公開後Follow-upへ延期できる。
8. Phase 1-F完了後にMac／Lightningを含むUser Manual、Final Review、Backupを作り、その後に公開準備へ進む。

## Rationale

- Python 3.12はCurrent Sourceで使用するPEP 695 `type` statementの最小Versionであり、自然な下限である。
- `llama-cpp-python 0.3.34`は公式Package Metadata上Python 3.12をSupportする。
- uvもPython 3.12／3.13をTier 1 Supportする。
- Lightning既設Pythonを利用すれば、Python Upgrade自体を新しい変数にしない。
- 第二EnvironmentをPhase 1で成立させることで、Portable RuntimeというPhase名の実証力が上がる。

## Consequences

### Positive

- Mac MetalとLinux CUDAの交換性をPhase 1公開時点で示せる。
- 各後続Phaseを両環境で継続検証しやすくなる。
- Public Repositoryの再現性主張がMac単独より強くなる。
- Python 3.12利用者にも入口が広がる。

### Negative

- Current `uv.lock`の再生成と両Version Testが必要になる。
- Python 3.13専用Setup／VerificationをPlatform別に整理する必要がある。
- Container／CUDA Detection、CUDA Native Build、Model配置がPhase 1 Scopeへ追加される。
- Phase 1 User AcceptanceとBackupはPhase 1-F完了まで延期される。

## Publication Boundary

「公開URL」がGitHub Repository URLを意味する場合、Phase 1 CLI Runtimeの公開は可能である。

「Lightning上で操作できるLive Web URL」を意味する場合、Current Phase 1はCLIのみであるため、Web UI／API／Access Control／Port公開の追加要件が必要となる。両者を混同しない。

## Official References

- [uv Python support](https://docs.astral.sh/uv/reference/policies/python/)
- [uv Project Python configuration](https://docs.astral.sh/uv/concepts/projects/config/)
- [llama-cpp-python PyPI](https://pypi.org/project/llama-cpp-python/)

## Authorization Boundary

本ADRは設計DecisionをAcceptedとする。Source／Config／Lock／Setup変更、Lightning Package Install、Native Build、Model転送、GPU利用、Git／GitHub公開操作は、各担当への実装／外部操作許可後に行う。

<!-- SOURCE_END 17: docs/adr/adr_0015_phase_1f_lightning_and_python_312_support_20260719202333.md -->

---

<!-- SOURCE_BEGIN 18: docs/adr/adr_0016_batch_lightning_upload_after_phase_1h_20260721093952.md -->

### Source 18: `docs/adr/adr_0016_batch_lightning_upload_after_phase_1h_20260721093952.md`

- History Target: `docs/project/phases/phase_1/history/adr/adr_0016_batch_lightning_upload_after_phase_1h_20260721093952.md`
- Source SHA-512: `dd30d5142906035b92f68913a32b13a0d3eb06fc826eeda0e39bd854d20efe0203570e25cf1fc8f9f55a102618e64344e6648ea996d6df21259548c798a82b7c`
- Source Size: `5220` bytes

# ADR-0016: Phase 1-G／1-HをMacで完成後にLightningへ一括搬入する

- 文書ID: `adr_0016_batch_lightning_upload_after_phase_1h`
- 状態: `accepted`
- 作成日時: `2026-07-21 09:39:52 JST`
- 更新日時: `2026-07-21 09:39:52 JST`
- Snapshot: `20260721093952`
- Decision Owner: ユーザー
- 記録担当: 設計者役担当Task
- 正本言語: 日本語
- Requirements: [phase_1g_minimal_web_surface_requirements_20260721093952.md](../history/requirements/phase_1g_minimal_web_surface_requirements_20260721093952.md)
- Architecture: [phase_1g_minimal_web_surface_architecture_20260721093952.md](../history/architecture/phase_1g_minimal_web_surface_architecture_20260721093952.md)
- Roadmap: [implementation_roadmap_20260721093952.md](../history/architecture/implementation_roadmap_20260721093952.md)
- supersedes: なし（ADR-0015のCross-environment要件を破棄せず実行順だけ変更する）

## Context

Phase 1-FのRepository実装、Mac Regression、Lightning Read-only PreflightはAcceptedになった。Lightningでは次が確認済みである。

```text
Ubuntu／Linux x86_64／Container
Python 3.12.11
Tesla T4／15360 MiB
nvcc Available
Project／Studio-local uv 0.11.29
GPU Preflight Exit 0
CPU Candidate Preflight Exit 0
```

一方、Project本体とGGUF ModelのLightning Uploadには非常に長い時間がかかる。Phase 1-GのWeb UIとPhase 1-HのPost-generation Summary Modeを先に実装すると、Source、Static Asset、Dependency、Lockが再び変わる。

途中状態を何度もUploadするより、Macで1-G／1-HをAcceptedにしてから最終候補を一括搬入する方が、ユーザーの時間と転送負荷を減らせる。

## Decision

1. Phase 1-FのLightning Native Gateを一時保留する。
2. Phase 1-Fを完了扱いにはしない。
3. Phase 1-G Minimal Web SurfaceをMac上で実装・検証する。
4. Phase 1-G Accepted後、Phase 1-H Post-generation Summary Modeを実装・検証する。
5. Phase 1-H Accepted後、最終候補Source／Static Asset／Lock／ModelをLightningへ一括搬入する。
6. LightningではPhase 1-F、1-G、1-Hを同じ最終候補でまとめて検証する。
7. Lightning Pythonは3.12.11を維持する。
8. Mac Primary Pythonは3.13.14を維持する。
9. Lightning既設uv 0.11.18は変更せず、隔離済みuv 0.11.29を明示して使用する。
10. 一括搬入は目標であり、Lightning固有Failureによる小規模な修正Uploadが絶対に発生しないとは主張しない。

## Revised Sequence

```text
Phase 1-F Repository／Preflight Accepted
  → Lightning Native Gate Deferred
  → Phase 1-G Minimal Web Surface on Mac
  → Phase 1-G Review／User Test
  → Phase 1-H Post-generation Summary Mode on Mac
  → Phase 1-H Review／User Test
  → Single Batch Upload Candidate
  → Lightning Dependency／CUDA／CPU／Web／Summary Verification
  → Cross-environment Final Review
  → Phase 1 User Acceptance
  → Phase 1 Completion Declaration
  → Backup
```

## Rationale

- FastAPI、Uvicorn、HTTPX等を含む最終`pyproject.toml`／`uv.lock`を一度で同期できる。
- UI Static Assetを完成状態で搬入できる。
- GGUFの大容量Uploadを繰り返さずに済む。
- LightningでCLI、Web、Summaryを同じModel Artifact／Backend Buildで検証できる。
- Preflightが既に合格しており、大きなHost／Python／GPU／uv不一致は先に排除できている。
- Phase 1-F未完了を明示維持するため、未実行Gateを合格扱いしない。

## Consequences

### Positive

- Upload回数と待機時間を抑えられる。
- LockとSourceのSnapshot不一致を避けやすい。
- Web UIとSummaryをLightning公開候補へ同時に含められる。
- Cross-platform Application Coreの検証範囲が広がる。

### Negative

- Phase番号どおりの厳密な直列完了ではなくなる。
- Lightning固有Failureの発見時期が1-H後になる。
- 1-G／1-HはLightning未検証の期間を持つ。
- 小規模な修正Uploadが後で必要になる可能性は残る。

## Risk Controls

- 1-G／1-HはPlatform固有処理をApplication Coreへ入れない。
- FastAPI／Uvicorn固有処理をEntrypointへ局所化する。
- Modelを用いないFake Port／ASGI Testを先に充実させる。
- Mac Native Smokeを各Subphaseで維持する。
- Python 3.12をRuff／Mypyの下限として維持する。
- Dependencyを最小化し、純Python Wheelを優先する。
- Tracked Config／SourceへLightning固有絶対Pathを保存しない。

## Publication Boundary

この順序変更はGitHub公開またはLightning Live URL公開を自動許可しない。

初回GitHub公開は、既存DecisionどおりPhase 1-ex完了後にユーザーが別途許可する。Lightning Live URLもAccess ControlとUser Test合格後にのみ公開候補となる。

## Authorization Boundary

本ADRはPhase順序変更をAcceptedとし、Phase 1-G HandoffによるRepository実装を許可可能にする。

Phase 1-H実装、Lightning Full Upload、Model Transfer、Dependency Sync、Native Build、Backup、Git、GitHub公開は、それぞれの後続Handoff／ユーザー指示前には開始しない。

<!-- SOURCE_END 18: docs/adr/adr_0016_batch_lightning_upload_after_phase_1h_20260721093952.md -->

---

<!-- SOURCE_BEGIN 19: docs/adr/adr_0016_canonical_model_and_deployment_artifact_separation_20260720231036.md -->

### Source 19: `docs/adr/adr_0016_canonical_model_and_deployment_artifact_separation_20260720231036.md`

- History Target: `docs/project/phases/phase_1/history/adr/adr_0016_canonical_model_and_deployment_artifact_separation_20260720231036.md`
- Source SHA-512: `1d552d5b2cea6b56e9fb7c960a9364576961e544d2a3ce4035ff18b15d366f58cc13779566e0d5b63841812be7b96e954e8bc0eb8dcc57221a31fc481661c58e`
- Source Size: `4860` bytes

# ADR-0016 Canonical ModelとDeployment Artifactの分離

- 文書ID: `adr_0016_canonical_model_and_deployment_artifact_separation`
- 状態: `accepted`
- 作成日時: `2026-07-20 23:10:36 JST`
- 更新日時: `2026-07-20 23:10:36 JST`
- Snapshot: `20260720231036`
- Decision Owner: ユーザー
- 作成担当: 設計者役担当Task
- 正本言語: 日本語
- supersedes: なし

## 1. Context

Guard ModelとJudge Modelについて、現在保有する第三者GGUF量子化Artifactを継続するか、将来を考慮してUpstream開発元の通常Weightへ切り替えるかを再評価した。

対象：

```text
Guard Local Artifact:
  DevQuasar/Qwen.Qwen3Guard-Gen-0.6B-GGUF
  Qwen.Qwen3Guard-Gen-0.6B.Q8_0.gguf

Judge Local Artifact:
  bartowski/Selene-1-Mini-Llama-3.1-8B-GGUF
  Selene-1-Mini-Llama-3.1-8B-Q5_K_M.gguf
```

## 2. Decision

Modelの出自正本と、特定環境で実際にLoadするArtifactを分離する。

```text
Canonical Model Source
  ↓ conversion／quantization relation
Deployment Artifact
  ↓ backend binding
Runtime Model Instance
```

採用関係：

| Role | Canonical Model Source | Local Deployment Artifact | Future Cloud Artifact |
|---|---|---|---|
| Guard | `Qwen/Qwen3Guard-Gen-0.6B` | DevQuasar GGUF `Q8_0` | Qwen公式Safetensors等 |
| Judge | `AtlaAI/Selene-1-Mini-Llama-3.1-8B` | bartowski GGUF `Q5_K_M` | AtlaAI公式Safetensors等 |

現在のGGUFを削除・置換せず、Mac／llama.cpp用Artifactとして維持する。公式通常Weightは実装上必要になるまでDownloadしない。

## 3. Rationale

- 公式通常WeightはModelの出自、Tokenizer、Config、Prompt形式、Revisionの正本として扱いやすい
- GGUFはMac／llama.cppでMemory効率と導入容易性に優れる
- M2 Pro／16GBでSelene BF16 Weightを常用するのは現実的でない
- 量子化Artifactを使用しても、Upstream、Revision、Conversion、Hashを明示すればProvenanceを保持できる
- Local／Cloudを同一Formatへ固定する必要はなく、Model Port／Backend Adapterで分離できる
- Formatの優劣ではなく、Canonical IdentityとDeployment適性を別々に管理する方が疎結合である

## 4. Guard固有判断

`Qwen/Qwen3Guard-Gen-0.6B`をCanonical Sourceとする。現在のDevQuasar Q8_0は約805MBのLocal Artifactとして継続する。

将来、生成後判定だけでなくToken単位のStreaming監視を本格化する場合は、`Qwen3Guard-Stream`系列も別Capabilityとして再評価する。`Gen`と`Stream`を同一Modelとして扱わない。

## 5. Judge固有判断

`AtlaAI/Selene-1-Mini-Llama-3.1-8B`をCanonical Sourceとする。現在のbartowski Q5_K_Mは約5.73GBのOn-Demand Local Artifactとして継続する。

Selene Miniは公式説明上、主に英語を対象とし、日本語は明示対応言語に含まれない。このため次を必須とする。

- 日本語Judge性能を未保証とする
- 日本語Evaluation Setで独立検証する
- 唯一のJudgeまたは最終権限として固定しない
- Rule Based評価、User評価、他Judge候補と比較できるようにする
- 日本語性能が不足する場合はQwen系等の別Judgeへ交換可能にする

## 6. Registry Consequence

Model Registryは最低限次を別Fieldとして持つ。

- Canonical Provider／Repository／Revision
- Canonical Config／Tokenizer／License
- Artifact Distributor／Repository／Revision
- Artifact File／Format／Quantization／Size／Hash
- Conversion Tool／Version／Parameters／Dataset情報（取得可能な場合）
- Backend／Backend Version
- Prompt／Chat Template／Parser
- Local／Cloud Deployment Profile
- Verification State／Evaluation Result

## 7. Alternatives Rejected

### 公式通常Weightだけへ即時統一

現在のMac、llama.cpp、Memory制約、Phase優先順位に合わないため不採用。

### GGUFだけをModelの正本にする

Upstreamとの関係、Cloud Backend、Tokenizer／ConfigのCanonical情報が弱くなるため不採用。

### 公式WeightとGGUFを今すぐ両方Download

現在の実装に不要でStorageと管理対象だけを増やすため不採用。

## 8. Sources

- Qwen Guard Canonical: `https://huggingface.co/Qwen/Qwen3Guard-Gen-0.6B`
- Qwen Guard Local GGUF: `https://huggingface.co/DevQuasar/Qwen.Qwen3Guard-Gen-0.6B-GGUF`
- Selene Canonical: `https://huggingface.co/AtlaAI/Selene-1-Mini-Llama-3.1-8B`
- Selene Local GGUF: `https://huggingface.co/bartowski/Selene-1-Mini-Llama-3.1-8B-GGUF`
- AtlaAI GGUF Reference: `https://huggingface.co/AtlaAI/Selene-1-Mini-Llama-3.1-8B-Q8_0-GGUF`

## 9. Authorization Boundary

本DecisionはModel Metadataと将来Backend方針を確定する。Model Download、現行GGUF削除、Model配置変更、Dependency追加、Adapter実装、Cloud Deploymentを許可しない。


<!-- SOURCE_END 19: docs/adr/adr_0016_canonical_model_and_deployment_artifact_separation_20260720231036.md -->

---

<!-- SOURCE_BEGIN 20: docs/adr/adr_0017_phase_1_ex_operating_model_and_documentation_transition_20260720231036.md -->

### Source 20: `docs/adr/adr_0017_phase_1_ex_operating_model_and_documentation_transition_20260720231036.md`

- History Target: `docs/project/phases/phase_1/history/adr/adr_0017_phase_1_ex_operating_model_and_documentation_transition_20260720231036.md`
- Source SHA-512: `b8ac21930314a8173adfe091e3ffddfe835e10fcc60f7f58ba70bd31af5f10453356ebb4e76651c50dc990099575eea486ff787f9f235bfee4edf9346bff19c8`
- Source Size: `3542` bytes

# ADR-0017 Phase 1-exにおける役割・Git・Documentation運用再整備

- 文書ID: `adr_0017_phase_1_ex_operating_model_and_documentation_transition`
- 状態: `accepted_reservation`
- 作成日時: `2026-07-20 23:10:36 JST`
- 更新日時: `2026-07-20 23:10:36 JST`
- Snapshot: `20260720231036`
- Decision Owner: ユーザー
- 作成担当: 設計者役担当Task
- 正本言語: 日本語
- supersedes: なし

## 1. Context

長期Codex Taskでは、会話量、要約継承、新旧Decision混在、Review対象肥大化により、設計精度と引き継ぎ精度の運用Riskが増える。

ただし現在の設計者役を即時に変更せず、Phase 1-ex「運用再整備」で役割、Git、Docs、Directory、通知を一体的に再設計する。

## 2. Decision

Phase 1-exで次を実施する予約をAcceptedとする。

1. `設計統括者役`、`設計者役`、`実装者役`、`対外Docs役`の責務とDocs権限を再整理
2. 現設計者役を`設計統括者役`へ変更
3. 各Phaseに専用の`設計者役`を配置可能にする
4. Git運用へ移行
5. Git移行後のDocs運用を要件定義
6. `docs/` Directory構造を変更
7. 構造変更完了後、各担当Taskへ新構造、権限、Current Entry Pointを通知
8. Phase単位の公開DocsとLossless統合を導入

## 3. Current State Preservation

Phase 1-ex開始・移行完了までは次を維持する。

```text
Current Role : 設計者役
Git          : 未導入
Docs Rule    : Current Append-Only／Timestamp Rule
Docs Layout  : Current Directory Structure
Task Notice  : 未実施
```

本ADRの作成時点で役職変更、Git初期化、Directory移動、担当通知を行わない。

## 4. Future Role Model

```text
設計統括者役
  ├─ Project全体設計
  ├─ Phase構成
  ├─ Cross-Phase整合
  ├─ 共通Policy／Architecture境界
  ├─ Phase開始用設計書
  └─ Phase最終Review／移行判定

Phase別 設計者役
  ├─ Phase詳細要件／設計
  ├─ Accepted上位設計の具体化
  ├─ 実装担当Handoff
  └─ Phase内Review
```

Phase別設計者役は、ユーザー要求や実装上のEvidenceに応じ、上位要件から大きく外れない範囲で再設計できる。

次は設計統括者役またはユーザーへEscalateする。

- Project全体Phase構成の変更
- 共通Port／Governance Core／Security Boundaryの変更
- Accepted ADRの破棄
- Privacy／Backup／公開Policyの変更
- 他PhaseへMaterial Impactを与える変更
- ユーザー要求との矛盾

## 5. Git／Docs Transition

Git導入後、現在のStrict Append-Only Timestamp Docs、Git History、Current Canonical Docs、Public Docs、Task Handoffの役割重複を再整理する。

詳細方式はPhase 1-ex内で要件化し、Migration、Inventory、Link更新、Rollback、担当通知を伴う。Directoryを先に変更してから要件を考えることを禁止する。

## 6. Consequence

- 長期Task一つへ全Phase詳細を集中させない
- Project全体整合とPhase内詳細を分離できる
- Git HistoryとDocsの重複を制御できる
- 各Phase完了Snapshotを人間公開とTask Handoffの両方に利用できる
- Role変更とDirectory変更の途中状態を明示的に管理する必要がある

## 7. Authorization Boundary

本ADRはPhase 1-ex実施内容の予約である。現在のRole変更、Task作成、Git初期化、Directory変更、File移動、各担当への通知、外部公開を許可しない。


<!-- SOURCE_END 20: docs/adr/adr_0017_phase_1_ex_operating_model_and_documentation_transition_20260720231036.md -->

---

<!-- SOURCE_BEGIN 21: docs/adr/adr_0018_phase_1_ex_canonical_docs_continuity_and_future_r_and_d_20260721155020.md -->

### Source 21: `docs/adr/adr_0018_phase_1_ex_canonical_docs_continuity_and_future_r_and_d_20260721155020.md`

- History Target: `docs/project/phases/phase_1/history/adr/adr_0018_phase_1_ex_canonical_docs_continuity_and_future_r_and_d_20260721155020.md`
- Source SHA-512: `d06538a9aac38f3ac2b84dbd7e951f4e95d31d56a3b048e235f8d184d2194f6575b8555a3ac93319b11abd323e2192e759a1f2f344f5304f59e2abb6ba787c80`
- Source Size: `3631` bytes

# ADR-0018 Phase 1-ex Canonical Docs／Continuity／Future R&D公開Hook

- 文書ID: `adr_0018_phase_1_ex_canonical_docs_continuity_and_future_r_and_d`
- 状態: `accepted_reservation`
- 作成日時: `2026-07-21 15:50:20 JST`
- 更新日時: `2026-07-21 15:50:20 JST`
- Snapshot: `20260721155020`
- Decision Owner: ユーザー
- 作成担当: 設計者役担当Task
- 正本言語: 日本語
- Requirements: [phase_1_ex_complete_operating_model_and_documentation_requirements_20260721155020.md](../history/requirements/phase_1_ex_complete_operating_model_and_documentation_requirements_20260721155020.md)
- supersedes: なし

## 1. Context

既存Docsは詳細EvidenceとTask間Communicationを高精度で保持する一方、File数とTimestamp系列が増え、Project全体の入口としては重くなっている。

GitHub閲覧者向けの説明と、Codex Taskを一から作り直して即時再開するための情報量も異なる。

また、本体完成後に別Taskで開発する独立R&D機構2件について、Coreへ依存を作らず、構想の存在と方向性だけを公開しておきたい。

## 2. Decision

Phase 1-exで次を作成する。

```text
docs/requirements_specification_ja.md
docs/system_architecture_ja.md
docs/technology_selection_ja.md
docs/basic_design_ja.md
docs/runtime_governance_specification_ja.md
docs/project_continuity/project_continuity_master_ja.md
```

最初の5文書は公開可能なStable Canonical Technical Docsとする。Project Continuity Masterも公開可能とし、Task再開に必要な情報をより広く統合する。

詳細設計書の網羅的作成は行わない。既存Granular Docsを保持し、将来必要なSubsystemだけ任意に追加する。

## 3. File／Language Decision

- File名とDirectory名は英語を使用する。
- 本文は日本語を正本とする。
- 日本語文書には`_ja`を付ける。
- Git移行後のStable DocsはTimestampを付けず、Git Historyで変更履歴を保持する。
- 既存Timestamp DocsとImmutable Compilationは保持する。

## 4. Continuity Decision

Project Continuity Masterは短い概要ではなく、Decision、Boundary、Current State、Known Issue、Next Gate、Task Authority、Source Mapを再開可能な粒度で保持する。

ただし公開Fileであるため、Secret、個人Path、Credential、実会話Log等を含めない。

## 5. Future R&D Decision

次をPhase 10の独立R&D Extensionとして予約する。

1. 例外認識型安全統治機構
2. 分散証跡型例外認識エージェント統治安全機構

両機構は別Project／別Taskで開発し、本体完成後に汎用Portを通じて疎結合統合する。

公開範囲：

- Roadmap：名称、研究領域、1から2行の概要
- System Architecture：接続位置だけ
- Project Continuity Master：提供済みの作業概念と統合方針
- Algorithm、実装方式、研究の核心：現時点では記載しない

## 6. Consequences

- 一般閲覧者、技術Review、Task再開の入口を分離できる。
- Git Historyと既存Append-only Evidenceを両立できる。
- Project全体を新Taskへ高精度で引き継げる。
- R&D構想の存在を先行公開しながら核心を保持できる。
- Stable Docsの更新時にCanonical Sourceとの整合Reviewが必要になる。
- Public DocsとContinuity Masterの重複を正本Mappingで管理する必要がある。

## 7. Authorization Boundary

本ADRはPhase 1-exのAccepted Reservationである。Stable Docs生成、Directory変更、Git操作、公開、Phase 10実装をまだ許可しない。

<!-- SOURCE_END 21: docs/adr/adr_0018_phase_1_ex_canonical_docs_continuity_and_future_r_and_d_20260721155020.md -->

---

<!-- SOURCE_BEGIN 22: docs/adr/adr_0019_phase_10_original_r_and_d_public_names_and_switches_20260721162242.md -->

### Source 22: `docs/adr/adr_0019_phase_10_original_r_and_d_public_names_and_switches_20260721162242.md`

- History Target: `docs/project/phases/phase_1/history/adr/adr_0019_phase_10_original_r_and_d_public_names_and_switches_20260721162242.md`
- Source SHA-512: `b15d1724bbc0d4016cbdb39557d6aa9979ed582098c2bb98f00f5ac4d52423ffe3d37771d660815cb1576543d4f4016a71145a2b791c4aae30b6bd30ac6df8e7`
- Source Size: `2971` bytes

# ADR-0019 Phase 10 Original R&D正式名称・公開範囲・個別Switch

- 文書ID: `adr_0019_phase_10_original_r_and_d_public_names_and_switches`
- 状態: `accepted_future_reservation`
- 作成日時: `2026-07-21 16:22:42 JST`
- 更新日時: `2026-07-21 16:22:42 JST`
- Snapshot: `20260721162242`
- Decision Owner: ユーザー
- 作成担当: 設計者役担当Task
- 正本言語: 日本語
- Requirements: [phase_1_ex_external_r_and_d_publication_and_integration_requirements_20260721162242.md](../history/requirements/phase_1_ex_external_r_and_d_publication_and_integration_requirements_20260721162242.md)
- Catalog: [phase_10_original_r_and_d_system_catalog_20260721162242.md](../history/governance/phase_10_original_r_and_d_system_catalog_20260721162242.md)
- supersedes: なし

## 1. Context

Phase 10の独立R&D構想は、これまで日本語名と研究方向だけを予約していた。ユーザーは略称と正式英名も先に公開し、OCILNSを同じ粒度で追加することを決定した。

## 2. Decision

公開名称を次で確定する。

```text
EASA
Exception Aware Safety Architecture
例外認識型安全統治機構

DLAGSA
Distributed LEA Agentic Governance & Safety Architecture
分散証跡型例外認識エージェント統治安全機構

OCILNS
Open Cognitive Interaction Ledger Network System
認知対話証跡台帳網
```

研究領域：

```text
EASA
  AI Safety Governance

DLAGSA
  Multi-Agent Governance,
  Distributed Accountability,
  and Safety Assurance

OCILNS
  Cognitive Interaction Provenance,
  Verifiable AI Systems,
  and Distributed Auditability
```

## 3. Public Disclosure

- Roadmapには名称、研究領域、1から2行の概要を記載する。
- System Architectureには接続位置とOptional性を記載する。
- Project Continuity Masterには作業概念をもう少し詳しく記載する。
- Algorithm、具体的改竄耐性方式、研究の核心は現在記載しない。

## 4. Config Decision

Phase 10統合時、EASA、DLAGSA、OCILNSをConfigで個別にON／OFF可能にする。DefaultはすべてOFFとする。

OFF時は対象SystemへのLoad、Call、Write、Side Effectを行わない。

## 5. Integration Decision

- EASA／DLAGSA：Generic External Governance Provider Port
- OCILNS：Generic Evidence Ledger Port
- Coreは3 Systemに直接依存しない。
- 3 Systemなしで本体は完全動作する。
- 各Systemは別Project／別Taskで開発する。

## 6. Consequences

- 構想の存在と研究方向を先行公開できる。
- MARGPA Runtime LLMの将来拡張位置を説明できる。
- Coreの疎結合と実験比較を維持できる。
- 正式名称の表記揺れを防止できる。
- 公開情報を増やす際は別DecisionとReviewが必要になる。

## 7. Authorization Boundary

本ADRは名称、公開範囲、将来Switchの予約を確定する。実装、Config変更、外部統合、核心公開を現在許可しない。

<!-- SOURCE_END 22: docs/adr/adr_0019_phase_10_original_r_and_d_public_names_and_switches_20260721162242.md -->

---

<!-- SOURCE_BEGIN 23: docs/adr/adr_0020_phase_1h_summary_pipeline_and_ui_language_separation_20260721174346.md -->

### Source 23: `docs/adr/adr_0020_phase_1h_summary_pipeline_and_ui_language_separation_20260721174346.md`

- History Target: `docs/project/phases/phase_1/history/adr/adr_0020_phase_1h_summary_pipeline_and_ui_language_separation_20260721174346.md`
- Source SHA-512: `ed26c2a54663c65946b9522b3828ae03bf5bf6a9c069d1bad4654b7f326d8f0b397e17bcf2eabfc99fd9d1e419ac012d02f8ba4898b53bc8b4730e435e26356e`
- Source Size: `5301` bytes

# ADR-0020: Phase 1-H Summary PipelineとUI Languageを分離する

- 文書ID: `adr_0020_phase_1h_summary_pipeline_and_ui_language_separation`
- 状態: `accepted`
- 作成日時: `2026-07-21 17:43:46 JST`
- 更新日時: `2026-07-21 17:43:46 JST`
- Snapshot: `20260721174346`
- 作成担当: 設計者役担当Task
- Decision Owner: ユーザー
- 正本言語: 日本語
- Requirements: [phase_1h_summary_mode_and_ui_language_requirements_20260721174346.md](../history/requirements/phase_1h_summary_mode_and_ui_language_requirements_20260721174346.md)
- Architecture: [phase_1h_summary_mode_and_ui_language_architecture_20260721174346.md](../history/architecture/phase_1h_summary_mode_and_ui_language_architecture_20260721174346.md)
- supersedes: なし

## Context

Phase 1-Gで、Main Modelを1回呼び出すMinimal Web Surface、Browser-owned Ephemeral Conversation、Response Language、Thinking Presentation、SSE、Cancel、Preview Access Controlが成立した。

ユーザーはPhase 1-Hとして次を要求した。

- 通常回答を同じMain Modelでもう一度要約してから表示するOption。
- 画面右上で日本語／英語を切り替えるUI。
- UI LanguageとModel Response Languageを独立させること。

要約をBrowser側の2回目API Callとして実装すると、Cancel、Generation Gate、Original／Summaryの関連、Audit Hookが分断される。UI LanguageをResponse Languageへ流用すると、「英語UI／日本語回答」等の有効な組合せを表現できない。

## Decision

### 1. Summary

- SummarizationをApplication側のOptional Response Transformation Layerとする。
- `off／post_generation` Modeを持つ。
- ON時はNormal GenerationとSummary Generationを1つのConversation Sessionが逐次所有する。
- Summary Backendは初期版で`main_model`を使う。
- Normal maxはRequest値／Default 2048、Summary maxは1024、Summary Thinkingはdisabledとする。
- Summary対象はOriginal Canonical Final Answerだけとする。
- Summary失敗、空、Context不足、Length時はWarning付きOriginalへFallbackする。
- Summary中CancelはFallbackせず`cancelled`とする。
- Original／Summary／Presented Answerを論理的に分離する。

### 2. UI Language

- UI LanguageはBrowser-only Presentation Preferenceとする。
- 値は`ja／en`、Defaultは`ja`とする。
- Response Languageの`ja／en／auto`から独立させる。
- UI LanguageだけをNamespaced `localStorage`へ保存する。
- Translation DictionaryをRepository内のVanilla JavaScriptで持つ。
- Model Output／Thinkingを翻訳しない。

### 3. Configuration

- Summary Layerは`config/application.toml`の`[layers.summarization]`へ追加する。
- Application Schemaを`2`から`3`へ更新する。
- Deployment ProfileへSummary設定を複製しない。
- UI LanguageはTOMLへ追加しない。

## Rationale

- 要約は追加Inferenceであり、単なるUI加工ではない。
- Session内に置くことで1 Model／1 Gate／1 Cancel Contractを維持できる。
- Modeにすることで将来の別方式やDedicated Modelへ拡張できる。
- 不完全SummaryよりOriginalを優先する方が情報欠落を隠しにくい。
- UI Languageは利用者の画面Preference、Response LanguageはModelへの出力Policyであり、責務が異なる。
- Current UI文字列数では外部i18n Dependencyを導入せずに成立する。

## Rejected Alternatives

### BrowserがMain APIを2回呼ぶ

却下。Cancel、Busy、Session、Audit Correlationが分断され、BrowserがSummary Promptを知ることになる。

### Normal回答を先にStreamingし、後からSummaryで置換する

却下。見えていた回答が突然変わり、Canonical Historyとユーザー認識が不安定になる。

### Summary失敗時にTurn全体をErrorとする

却下。既に有効なOriginal Answerがあるため、安全なWarning付きFallbackの方が可用性が高い。

### Summary Lengthでも不完全Summaryを採用する

却下。欠落を完成Summaryとして表示する危険がある。Phase 1-HではOriginalへFallbackする。

### Summary中Cancel後にOriginalを表示する

却下。停止したユーザー意思に反して回答を確定させるため。

### UI LanguageとResponse Languageを1つにする

却下。英語UI／日本語回答等の組合せを失う。

### UI LanguageをApplication TOMLへ保存する

却下。Server／Deployment設定ではなくBrowser利用者ごとのPreferenceである。

### i18n Framework／翻訳APIを導入する

却下。Phase 1-H規模ではDependencyとSecurity Surfaceが過大である。

## Consequences

- Summary ON時はLatencyとInference Costが増える。
- Current 4096 Contextでは長いOriginalがFallbackする可能性がある。
- Same Model Summaryの正確性は保証されない。
- Conversation SessionのState MachineとTest Matrixが増える。
- UI Language切替は軽量で、Response Language契約を壊さない。
- 将来のSummary Model、Audit Log、Judge、Governance接続点を確保できる。

## Implementation Gate

本ADRは設計判断をAcceptedとする。Source／Config／UI変更は、ユーザーが実装担当へPhase 1-H開始を明示した後に限る。

<!-- SOURCE_END 23: docs/adr/adr_0020_phase_1h_summary_pipeline_and_ui_language_separation_20260721174346.md -->

---

<!-- SOURCE_BEGIN 24: docs/adr/adr_0021_phase_1i_thinking_aware_safe_web_presentation_20260725200001.md -->

### Source 24: `docs/adr/adr_0021_phase_1i_thinking_aware_safe_web_presentation_20260725200001.md`

- History Target: `docs/project/phases/phase_1/history/adr/adr_0021_phase_1i_thinking_aware_safe_web_presentation_20260725200001.md`
- Source SHA-512: `47059062fc2f8564f5cd5c6d2e0c677810b61108ed4a7a885e55b1526ac92fd2061226400c94fde5b2f8998a9b7677ebbec8b2981620c53700df566dc7a0c6cd`
- Source Size: `4953` bytes

# ADR-0021: Phase 1-I Thinking-aware Safe Web Presentation

- 文書ID: `adr_0021_phase_1i_thinking_aware_safe_web_presentation`
- 状態: `accepted`
- 作成日時: `2026-07-25 20:00:01 JST`
- 更新日時: `2026-07-25 20:00:01 JST`
- Snapshot: `20260725200001`
- 作成担当: 設計者役担当Task
- Decision Owner: ユーザー
- 正本言語: 日本語
- Requirements: [phase_1i_web_presentation_and_ux_follow_up_requirements_20260725200001.md](../history/requirements/phase_1i_web_presentation_and_ux_follow_up_requirements_20260725200001.md)
- Architecture: [phase_1i_web_presentation_and_ux_follow_up_architecture_20260725200001.md](../history/architecture/phase_1i_web_presentation_and_ux_follow_up_architecture_20260725200001.md)
- supersedes: なし

## Context

Phase 1-G／1-HのMac Web User Testで、Chat、Streaming、Stop、New Chat、Language、Summary、Token Limitが成立した。

次のFollow-upが確認された。

- Thinking VisibilityをONにしても、Generation DefaultがDisabledのため表示対象がない。
- Assistant MarkdownがPlain Textとして表示される。
- Shortcutは動作するが画面上で発見できない。
- User／Assistant MessageにCopy Buttonがない。

Current SSE DeltaはPresentation済み文字列だけを持ち、ReasoningとFinalを意味的に区別できない。Current Completion EventはCanonical Finalだけを持つ。そのため、単純にCompletion後Markdown化するとThinking表示を消すか、ThinkingをFinalへ混入させる危険がある。

## Decision

### 1. Phase 1-Iを追加する

Phase 1 Completion前のSubphaseとして、Web PresentationとUX Follow-upを実施する。

### 2. Thinking GenerationとVisibilityを独立させる

Web Requestに`thinking_mode`を追加する。

```text
Generation : disabled／enabled
Visibility : hidden／visible
```

Generation OFF時のVisibility ONを、UIで有効な表示状態として誤認させない。

### 3. SSEでReasoningとFinalを区別する

DeltaへSemantic Channelを追加する。

```text
reasoning
final
```

Hidden ReasoningはClientへ送らない。

### 4. ThinkingとFinalを別DOM Regionにする

- Thinking：Ephemeral Plain Text
- Final：Streaming Plain Text、Completion後Sanitized Markdown

ThinkingをBrowser Conversation History、Copy、次Turnへ混入させない。

### 5. MarkdownはCompletion後にRenderする

Streaming中の不完全Markdownを毎Chunk Renderしない。

Canonical FinalをCompletion後にParse／Sanitizeし、安全なDOMへ置換する。Failure時はPlain TextへFallbackする。

### 6. CopyはCanonical Textを使う

Rendered DOMからCopy Textを逆生成しない。

### 7. Runtime CDNを使用しない

Third-party Parser／Sanitizerを使う場合はVersion、License、Source、Digestを固定し、Runtime Networkを不要にする。

## Rationale

- Thinking ExecutionとPresentationの既存ADR-0014をWeb UIでも維持できる。
- Semantic ChannelによりUIがTag文字列や可変Labelを再Parseせずに済む。
- Canonical／Rendered分離によりHistory、Copy、Auditの一貫性を保てる。
- Completion後RenderはStreaming中のMalformed DOMとFlickerを避けられる。
- Plain Text FallbackによりMarkdown Dependency FailureがChat Failureにならない。

## Rejected Alternatives

### Visibility ONでGenerationも暗黙ON

却下。ExecutionとPresentationの独立性を壊す。

### Current表示文字列から`<推論過程>`をBrowserが解析

却下。Display Labelが可変であり、Model Contentとの衝突、Tag Injection、Localization依存が起きる。

### ThinkingとFinalを一つのMarkdownへ投入

却下。Thinking漏えい、Copy混入、History混入、Markdown解釈差が起きる。

### Streaming ChunkごとにHTMLへ再変換

却下。Incomplete Markdown、DOM再構築Cost、Flicker、Security Review範囲が増える。

### Raw `innerHTML`

却下。Model OutputはUntrusted Contentであり、XSSを許容できない。

### External CDN

却下。Offline／Local再現性、Supply Chain、CSP、外部通信なしというCurrent Boundaryを壊す。

### Rendered DOMの`innerText`をCopy

却下。Canonical Markdown、Code、List、Whitespaceが変形し、Hidden Node混入Riskもある。

## Consequences

- Conversation SSE Contractが更新される。
- Thinking Segment Routing Testが増える。
- Markdown Parser／Sanitizer選定とLicense記録が必要になる可能性がある。
- UI DOM StructureがMessage単位へ細分化される。
- Phase 1 User ManualとまとめAcceptance Testが必要になる。
- Plain Text Fallbackを維持するため、Markdown Failure時も生成結果を失わない。

## Implementation Gate

ユーザーは2026-07-25、Phase 1完了前に本Follow-upを先行実施し、実装担当Handoffを作成するよう指示した。本ADRとHandoffのScope内でPhase 1-I実装へ着手可能である。


<!-- SOURCE_END 24: docs/adr/adr_0021_phase_1i_thinking_aware_safe_web_presentation_20260725200001.md -->

---

<!-- SOURCE_BEGIN 25: docs/adr/adr_0022_lightning_pure_cpu_and_optional_component_hook_only_profile_20260725200001.md -->

### Source 25: `docs/adr/adr_0022_lightning_pure_cpu_and_optional_component_hook_only_profile_20260725200001.md`

- History Target: `docs/project/phases/phase_1/history/adr/adr_0022_lightning_pure_cpu_and_optional_component_hook_only_profile_20260725200001.md`
- Source SHA-512: `978903424ecabcdc36fb137f83ec70f362e7924992fe22a126bdf03d5c90ee6b790c4915b0fe5f009a478066be01b309f11b1d01e46ccdfc8d65274e19d42646`
- Source Size: `3933` bytes

# ADR-0022: Lightning Pure CPUとOptional Component Hook-only Profile

- 文書ID: `adr_0022_lightning_pure_cpu_and_optional_component_hook_only_profile`
- 状態: `accepted`
- 作成日時: `2026-07-25 20:00:01 JST`
- 更新日時: `2026-07-25 20:00:01 JST`
- Snapshot: `20260725200001`
- 作成担当: 設計者役担当Task
- Decision Owner: ユーザー
- 正本言語: 日本語
- Requirements: [phase_1f_lightning_pure_cpu_runtime_follow_up_requirements_20260725200001.md](../history/requirements/phase_1f_lightning_pure_cpu_runtime_follow_up_requirements_20260725200001.md)
- Architecture: [phase_1f_lightning_pure_cpu_runtime_follow_up_architecture_20260725200001.md](../history/architecture/phase_1f_lightning_pure_cpu_runtime_follow_up_architecture_20260725200001.md)
- supersedes: なし

## Context

Current Lightning CPU Profileは`gpu_layers=0`でCPU実行するが、Backend Build VariantはCUDAである。Freshな最小CPU環境ではCUDA Toolkit／`nvcc`が存在しない可能性があり、CPU実行のためだけにCUDA Buildを要求する構成は再現性が低い。

また、Phase 1-ex後にProject Documentation Explainerの軽量RAGをMac実機へ追加する候補があるが、外部CPU Deploymentでは追加Index、Retrieval、Context、Model Callを既定で実行しない構成が必要である。

## Decision

### 1. Pure CPU Profileを分離する

```text
build variant : cpu
device        : cpu
acceleration  : none
gpu layers    : 0
```

を表すProfileを追加する。

### 2. CUDA Build CPU Executionを維持・識別する

Existing CPU Profileを無断削除せず、CUDA BuildをCPUで実行するProfileとして区別する。

### 3. Pure CPU SetupはCUDAを要求しない

GPU、NVIDIA Driver、CUDA Toolkit、`nvidia-smi`、`nvcc`を必須条件にしない。

### 4. Repository Hookを先に実装する

Profile、Setup、Preflight、Verification、TestはRepositoryで作成可能とする。外部Native実行は別Gateとし、未実行をPassにしない。

### 5. Project Documentation ExplainerはDeployment別にする

Phase 1-ex後：

```text
Mac Local:
  Optional implementation／enablement

Lightning CPU:
  Hook only
  enabled = false
  Provider／Index absent allowed
  No Retrieval／No Additional Model Call
```

同一Component Contractを使うが、Deployment ProfileごとにActivationとProvider Availabilityを分離する。

## Rationale

- CPU RuntimeがGPU Toolchainへ依存しなくなる。
- Build CapabilityとExecution Deviceを正しく表現できる。
- Fresh Environment再構築性が上がる。
- Optional RAG機能をCoreやCloud Deploymentへ強制しない。
- Macで研究機能を試しつつ、外部Demoを軽量に保てる。

## Rejected Alternatives

### Current CUDA Build CPU Profileだけを使う

却下。Fresh CPU環境でCUDA Toolchainがない場合に再構築できない。

### CPU環境でもCUDA ToolkitをInstallする

却下。不要なDependency、Build時間、Failure Surfaceを増やす。

### CPU Setup失敗時にCUDA Profileへ自動Fallbackする

却下。要求DeviceとObserved Runtimeが不明確になる。

### MacでRAGを実装したらLightningでも自動ON

却下。Optional ComponentのDeployment Independenceを失う。

### Lightning用にRAG CodeをForkする

却下。同一Contract＋Profileで表現でき、ForkはDriftを生む。

## Consequences

- ProfileとVerification Targetが一つ増える。
- `llama-cpp-python`のCPU Native Build Recipeが必要になる。
- CUDA CPU ExecutionとPure CPUのTest Matrixが増える。
- External Native Evidenceは利用可能時までPendingとなる。
- Project Documentation ExplainerはProfileごとにAvailability／Enabled Stateを表示する必要がある。

## Implementation Gate

Repository側Pure CPU Hookは実装担当へHandoff可能である。外部環境操作とRAG実装は本ADRだけでは許可しない。


<!-- SOURCE_END 25: docs/adr/adr_0022_lightning_pure_cpu_and_optional_component_hook_only_profile_20260725200001.md -->

---

<!-- SOURCE_BEGIN 26: docs/adr/adr_0023_simple_rag_missing_docs_explicit_unavailable_result_20260725201016.md -->

### Source 26: `docs/adr/adr_0023_simple_rag_missing_docs_explicit_unavailable_result_20260725201016.md`

- History Target: `docs/project/phases/phase_1/history/adr/adr_0023_simple_rag_missing_docs_explicit_unavailable_result_20260725201016.md`
- Source SHA-512: `1f0794933e42f212233e0a1c5f76fde1a0c66f656fdebf16427f1651b7e8faed71899fffbdde0983b6666642f6f524eb9a07375410651eaec4767452cc3d71bf`
- Source Size: `1848` bytes

# ADR-0023 Simple RAG Missing Docs Explicit Unavailable Result

- 文書ID: `adr_0023_simple_rag_missing_docs_explicit_unavailable_result`
- 状態: `accepted`
- 作成日時: `2026-07-25 20:10:16 JST`
- 更新日時: `2026-07-25 20:10:16 JST`
- Snapshot: `20260725201016`
- 作成担当: 設計者役担当Task
- Decision Owner: ユーザー
- 正本言語: 日本語
- Requirements: [simple_rag_documentation_availability_requirements_20260725201016.md](../history/requirements/simple_rag_documentation_availability_requirements_20260725201016.md)
- supersedes: なし

## 1. Decision

Simple RAG／Project Documentation Explainerを明示利用した時に`docs/`が存在しない場合、推測回答やApplication Crashではなく、構造化されたUnavailable Resultを返す。

```text
state       : unavailable
reason_code : docs_directory_missing
message_ja  : docs/が設置されていないため参照できません。
```

## 2. OFF Semantics

ComponentがOFFの場合は`docs/`を探索しない。Lightning Hook-only Profileを含め、`docs/`不存在をStartup Errorにしない。

## 3. Rationale

- LocalとCloudで同じFailure Contractを維持できる。
- Project Docsを参照した回答と、Modelの一般知識による推測を混同しない。
- Optional Componentの不存在がCore Runtimeを壊さない。
- UI、CLI、API、Auditが表示文言ではなくReason Codeで処理できる。

## 4. Consequences

- Corpus Availability Gateが必要になる。
- Missing、Empty、Unreadable、Manifest Missing等の分類が必要になる可能性がある。
- OFF時とUnavailable時を別状態として扱う。
- RAG実装と同時に自動Testを追加する。

## 5. Implementation Timing

実装はPhase 1-ex完了後のSimple RAG Handoffで行う。本ADRは現時点のRAG実装を許可しない。


<!-- SOURCE_END 26: docs/adr/adr_0023_simple_rag_missing_docs_explicit_unavailable_result_20260725201016.md -->

---

