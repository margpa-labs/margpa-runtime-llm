# Project Directory構成設計

- 文書ID: `project_directory_structure`
- 状態: `current`
- 作成日時: `2026-07-18 19:21:10 JST`
- 更新日時: `2026-07-18 19:21:10 JST`
- 対象: Project Root、Python Package、Module、Adapter、Test、Runtime Data
- 正本言語: 日本語
- 上位Architecture: [system_architecture_20260718174637.md](system_architecture_20260718174637.md)
- 関連Roadmap: [implementation_roadmap_20260718174637.md](implementation_roadmap_20260718174637.md)

## 1. Decision

MARGPA Runtime LLMのDirectory構成は、機能別ModuleとPort／Adapterを組み合わせたHybrid構成を採用する。

```text
Business機能     : modules/
Module横断処理   : orchestration/
外部技術         : adapters/
外部からの入口   : entrypoints/
依存性注入・起動 : bootstrap/
共通最小要素     : shared/
```

純粋なLayer別構成だけにはしない。将来`services/`、`repositories/`、`utils/`が巨大な雑多Directoryになることを避ける。

純粋な機能別構成だけにもせず、Model Backend、Storage、External API等の技術依存はAdapterとして共通の境界へ分離する。

## 2. Design Goal

- 将来の機能追加時に既存Moduleを壊さない
- Modelを交換可能にする
- Backendを交換可能にする
- Governance Definitionを交換可能にする
- Storageを交換可能にする
- UIを交換可能にする
- Local／Cloud／Hybridを同じCoreで扱う
- Module単位でTestできる
- Moduleを無効化できる
- Framework固有処理を境界へ隔離する
- 循環依存を防ぐ
- 追加機能の配置先を明確にする

## 3. Project Rootの将来構成

```text
margpa-runtime-llm/
├─ docs/
│  ├─ requirements/
│  ├─ architecture/
│  ├─ governance/
│  ├─ adr/
│  ├─ handoffs/
│  └─ public/                         # 将来の対外公開候補
│
├─ models                             # External Model RootへのSymbolic Link
│
├─ config/
│  ├─ profiles/                       # local / cloud / hybrid
│  ├─ models/                         # Model Registry、選択設定
│  ├─ governance/                     # Core / Standard / Full
│  ├─ guardrail/
│  └─ logging/
│
├─ resources/
│  ├─ governance/
│  │  ├─ definitions/                 # ARGD / DAGD Snapshot
│  │  └─ schemas/                     # Definition Schema
│  ├─ prompts/                        # Version管理するPrompt Template
│  ├─ policies/                       # Tool Permission等
│  └─ schemas/                        # Audit、API等のSchema
│
├─ src/
│  └─ margpa_runtime_llm/
│     ├─ bootstrap/
│     ├─ orchestration/
│     ├─ shared/
│     ├─ modules/
│     ├─ adapters/
│     └─ entrypoints/
│
├─ tests/
│  ├─ unit/
│  ├─ integration/
│  ├─ contract/
│  ├─ end_to_end/
│  ├─ performance/
│  └─ fixtures/
│
├─ scripts/
│  ├─ setup/
│  ├─ models/
│  ├─ audit/
│  └─ development/
│
├─ var/                               # Local実行時生成物・Git管理外
│  ├─ audit/
│  ├─ conversations/
│  ├─ indexes/
│  ├─ logs/
│  ├─ cache/
│  └─ tmp/
│
├─ examples/
│  ├─ configs/
│  ├─ audit_logs/
│  └─ requests/
│
├─ pyproject.toml
├─ README.md
├─ CHANGELOG.md
├─ LICENSE
├─ .gitignore
└─ .env.example
```

これは将来を含む設計上の全体像であり、すべてをPhase 1で作成するものではない。

## 4. Project名とPython Package名

Project Directory：

```text
margpa-runtime-llm/
```

PythonではHyphenをImport Package名に使用できないため、Python Package名は次とする。

```text
margpa_runtime_llm
```

配置：

```text
src/margpa_runtime_llm/
```

## 5. `src/`内部の将来構成

```text
src/margpa_runtime_llm/
├─ bootstrap/
├─ orchestration/
├─ shared/
│
├─ modules/
│  ├─ conversation/
│  ├─ inference/
│  ├─ governance/
│  ├─ audit/
│  ├─ guardrail/
│  ├─ authorization/
│  ├─ evaluation/
│  ├─ repair/
│  ├─ rag/
│  ├─ agent/
│  ├─ tools/
│  └─ memory/
│
├─ adapters/
│  ├─ model_backends/
│  ├─ guard_models/
│  ├─ judge_models/
│  ├─ storage/
│  ├─ retrieval/
│  ├─ tools/
│  └─ observability/
│
└─ entrypoints/
   ├─ api/
   ├─ cli/
   ├─ web/
   └─ workers/
```

## 6. `bootstrap/`

責務：

- Application生成
- Dependency Injection
- Deployment Profile読込
- Concrete Adapterの選択
- Lifecycle
- Startup／Shutdown
- ResourceのLoad／Unload

概念候補：

```text
bootstrap/
├─ application_factory.py
├─ dependency_container.py
└─ lifecycle.py
```

`bootstrap/`だけが具体的なAdapterを知ってよい。

Local例：

```text
Model Port   → llama.cpp Adapter
Storage Port → JSONL Adapter
Judge Port   → Selene Adapter
```

Cloud例：

```text
Model Port   → vLLM Adapter
Storage Port → PostgreSQL Adapter
Judge Port   → Remote Judge Adapter
```

## 7. `orchestration/`

複数Moduleにまたがる実行順序だけを担当する。

候補：

```text
orchestration/
├─ governed_chat/
├─ model_loading/
├─ turn_processing/
└─ repair_flow/
```

代表Flow：

```text
User Input
    ↓
Guardrail
    ↓
Governance
    ↓
Inference
    ↓
Output Guard
    ↓
Evaluation
    ↓
Repair
    ↓
Audit
    ↓
Conversation保存
```

各Module自身へ全体Flowを埋め込まない。

将来CDOGD等を導入する場合も、OrchestrationまたはGovernance Orchestratorを交換可能にする。

## 8. `shared/`

本当に複数Moduleで共有する最小要素だけを置く。

候補：

```text
shared/
├─ errors/
├─ identifiers/
├─ result/
├─ time/
└─ types/
```

禁止：

- 雑多なFunctionを置く`utils/`化
- Business Ruleの移動先にする
- Model固有処理を置く
- Storage固有処理を置く

## 9. `modules/`共通内部構造

各Moduleは、必要に応じて次の内部構成を持つ。

```text
modules/governance/
├─ domain/
├─ application/
├─ ports/
├─ contracts/
└─ public.py
```

### `domain/`

- Entity
- Value Object
- 不変条件
- 純粋なRule
- I/Oを伴わないLogic

### `application/`

- Module内Use Case
- Application Service
- Domain Objectの調整
- Portの利用

### `ports/`

- Moduleが外部へ要求するInterface
- Protocol
- Repository Port
- Model Port
- Clock／ID等のPort

### `contracts/`

- 他Moduleへ公開するCommand
- Event
- DTO
- Result

### `public.py`

- 他Moduleから利用可能な公開API
- Module内部構造を外部へ露出しない

他Moduleは内部実装を直接Importせず、`public.py`または`contracts/`を通して接続する。

## 10. 主要Module

### `conversation/`

- Session
- Conversation
- Turn
- Message
- History
- Regenerate

### `inference/`

- Model Registry
- Model Capability
- Model Load／Unload
- Generation Request
- Streaming
- Stop
- Token Usage
- Generation Result

### `governance/`

- Definition
- Loader
- Validator
- Compiler
- Governance Plan
- Rule Engine
- State Machine
- Action Resolver
- Status Reporter

ARGD／DAGD固有処理も初期はこのModuleに配置する。

将来GDが増えた場合の候補：

```text
modules/governance/definitions/
├─ argd/
├─ dagd/
├─ aisgd/
├─ aagd/
├─ mpgd/
└─ daagd/
```

### `audit/`

- Audit Event
- Turn Log
- Canonicalization
- SHA-512
- Integrity Verification
- Append-Only Writer
- Export

### `guardrail/`

- Input Guard
- Output Guard
- Prompt Injection
- Secret Detection
- Guard Result

### `authorization/`

- Tool Permission
- Allow／Deny
- Human Approval
- Capability
- Policy Conflict

GuardrailとTool Permissionを混在させないため、`authorization/`を独立させる。

### `evaluation/`

- Rule Based Evaluation
- Dimension Score
- User Rating
- Judge Request
- Judge Result
- Candidate Ranking

### `repair/`

- Repair Policy
- Repair Request
- Regeneration
- Rebind
- Enforce
- Reinitialize
- Repair Result

### 将来Module

```text
rag/
agent/
tools/
memory/
```

境界と名称は設計するが、実体は必要なPhaseで追加する。

## 11. `adapters/`

```text
adapters/
├─ model_backends/
│  ├─ llama_cpp/
│  ├─ mlx/
│  ├─ transformers/
│  ├─ vllm/
│  └─ remote_api/
│
├─ guard_models/
│  └─ qwen3guard/
│
├─ judge_models/
│  └─ selene/
│
├─ storage/
│  ├─ json/
│  ├─ jsonl/
│  ├─ sqlite/
│  ├─ postgresql/
│  └─ object_storage/
│
├─ retrieval/
│  ├─ local/
│  └─ vector_store/
│
├─ tools/
│  ├─ filesystem/
│  ├─ shell/
│  └─ external_api/
│
└─ observability/
   ├─ logging/
   ├─ metrics/
   └─ tracing/
```

Model名やBackend固有処理をCoreへ入れない。

例：

```text
modules/inference/ports/model_port.py
```

を、次が実装する。

```text
adapters/model_backends/llama_cpp/
```

Qwen3Guard固有のPromptとParserは次へ閉じ込める。

```text
adapters/guard_models/qwen3guard/
```

Selene固有のJudge Prompt、Parser、Result変換は次へ閉じ込める。

```text
adapters/judge_models/selene/
```

## 12. `entrypoints/`

外部からApplicationを利用する入口を置く。

```text
entrypoints/
├─ api/
├─ cli/
├─ web/
└─ workers/
```

責務：

- Request受付
- Input DTO変換
- Application Use Case呼出
- Streaming接続
- Response変換
- 外部向けError表現

禁止：

- Governance Ruleの実装
- Model Backendの直接操作
- Storageの直接操作
- Tool Permissionの最終判断

## 13. `config/`と`resources/`

```text
config/
  今回の実行で何を選ぶか

resources/
  実行時に参照する定義、Schema、Prompt、Policyの原本
```

例：

```text
config/models/
  Active MainをQwen3-4Bにする

resources/governance/definitions/
  ARGD／DAGD本体またはSnapshot
```

Secretは`config/`や`resources/`へ直接保存せず、Environment VariableまたはSecret Storeを利用する。

## 14. `var/`

Local実行で生成されるData専用Directoryとし、原則Git管理外とする。

```text
var/audit/          Audit原本
var/conversations/  会話履歴
var/indexes/        RAG Index
var/logs/           Operational Log
var/cache/          Cache
var/tmp/            一時処理
```

Audit LogとOperational Logを分離する。

```text
Audit Log:
  誰が、何を、どのModel・Governanceで処理したか

Operational Log:
  起動、Memory、Error、Debug、Performance
```

## 15. `tests/`

```text
tests/
├─ unit/
├─ integration/
├─ contract/
├─ end_to_end/
├─ performance/
└─ fixtures/
```

### `unit/`

- 純粋Logic
- Domain Rule
- 各Module

### `integration/`

- Adapter
- Filesystem
- Model Backend
- Storage

### `contract/`

- Portを各Adapterが満たすか
- Model Backend間のInterface互換性
- Storage Adapter間の互換性

Model Portを次のAdapterが同じ契約で実装できることを確認する。

- llama.cpp
- MLX
- Transformers
- vLLM

### `end_to_end/`

- User InputからAnswerまで
- GovernanceとAuditを含むFlow

### `performance/`

- Token速度
- Memory
- Latency
- Load／Unload時間

### `fixtures/`

- 匿名化Test Data
- 小型Fixture
- Model Binaryを配置しない

## 16. Dependency Rule

```text
entrypoints
    ↓
orchestration
    ↓
modules
    ↓
shared

adapters
    ↓
modulesのports / contracts

bootstrap
    ↓
全体を接続するだけ
```

禁止：

- `modules/`から`adapters/`をImportする
- 他Moduleの内部実装を直接Importする
- `shared/`を雑多な`utils/`にする
- 巨大な`services/`Directoryを作る
- UIからStorageを直接操作する
- Governanceから特定Model Fileを直接参照する
- GuardrailとAuthorizationを混同する
- Adapterから別Adapterへ無秩序に依存する
- Circular Dependencyを許容する

## 17. Frontendの扱い

UI技術は未決定。

StreamlitまたはPython内で完結するWeb UIの場合は、`entrypoints/web/`を中心に配置する。

React／Next.js等の独立Frontendを採用した場合は、Project Rootへ次を追加する可能性がある。

```text
frontend/
```

UI選定前に空の`frontend/`は作成しない。

## 18. Phase別Directory追加

### Phase 1

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

### Phase 2

- `modules/conversation/`
- `entrypoints/api/`
- `entrypoints/web/`
- 必要なStorage Adapter

### Phase 3

- `modules/governance/`
- `modules/audit/`
- Governance Definition Resource
- Audit Storage Adapter

### Phase 4

- `modules/guardrail/`
- `modules/authorization/`
- `modules/evaluation/`
- `modules/repair/`
- `adapters/guard_models/qwen3guard/`

### Phase 5

- `modules/rag/`
- `adapters/retrieval/`
- Embedding／Reranker関連

### Phase 6

- `modules/agent/`
- `modules/tools/`
- `modules/memory/`
- Tool Adapter

### Phase 7

- Judge本格統合
- Cloud Adapter
- vLLM
- PostgreSQL
- Multi Model
- Multi GD
- Vision
- Frontend分離
- Deployment関連

## 19. 今回作成したDirectory

`2026-07-18 19:21:10 JST`時点で、ユーザーの明示許可によりPhase 1最小Directoryだけを作成した。

```text
src/
└─ margpa_runtime_llm/
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

作成していないもの：

- Python Source File
- `__init__.py`
- Config File
- Test File
- Script
- `pyproject.toml`
- Dependency
- Git Repository
- Phase 2以降のDirectory

Directory作成は実装開始を意味しない。

## 20. Empty Directoryの扱い

GitはEmpty Directoryを管理しない。

Git初期化後にDirectoryを追跡する必要がある場合も、無条件に`.gitkeep`を大量作成しない。

実装されるPhaseで必要なFileとともにDirectoryを追加することを基本とする。

## 21. 拡張原則

- 将来のBoundaryと命名は先に設計する
- 実体Directoryと実装は必要なPhaseで追加する
- 新Module追加時は責務、Public Contract、Port、Audit Eventを定義する
- Technology固有処理はAdapterへ置く
- Cross-Module FlowはOrchestrationへ置く
- Sharedへ安易に移動しない
- 既存Moduleの内部へ別Domainを混ぜない
- Cloud移行のためにLocal固有PathをCoreへ埋め込まない

## 22. 次の設計候補

Directory構成の次に、Phase 1実装へ入る前の技術選定として次が残る。

- Local Backendの最終決定
- llama.cppとllama-cpp-pythonの役割
- Python Version
- Dependency管理方式
- `pyproject.toml`方針
- Config形式
- Model Registry Schema
- Phase 1 Acceptance Criteria
- Test Strategy詳細

実装はユーザーからの明示的な解禁後に開始する。
