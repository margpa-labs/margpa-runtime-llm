# ADR-0006: Model Runtime PortとConfiguration境界

- 文書ID: `adr_0006_model_runtime_port_and_configuration`
- 状態: `proposed`
- 作成日時: `2026-07-18 22:32:03 JST`
- 更新日時: `2026-07-18 22:32:03 JST`
- Decision Owner: 設計者役担当Task
- 対象: Phase 1-B Model Runtime
- 正本言語: 日本語
- 詳細設計: [phase_1b_model_runtime_contract_20260718223203.md](../architecture/phase_1b_model_runtime_contract_20260718223203.md)
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

