# Phase 1-B Model Runtime 実装担当Handoff

- 文書ID: `designer_handoff_phase_1b_model_runtime`
- 状態: `ready_for_implementation_authorization`
- 作成日時: `2026-07-18 22:43:08 JST`
- 更新日時: `2026-07-18 22:43:08 JST`
- 作成担当: 設計者役担当Task
- 対象: 実装者役担当Task
- 正本言語: 日本語
- Documentation Index: [documentation_index_20260718224308.md](../documentation_index_20260718224308.md)
- 詳細設計: [phase_1b_model_runtime_contract_20260718223203.md](../architecture/phase_1b_model_runtime_contract_20260718223203.md)
- Accepted ADR: [adr_0006_model_runtime_port_and_configuration_20260718224308.md](../adr/adr_0006_model_runtime_port_and_configuration_20260718224308.md)
- Phase 1-A Review: [designer_review_phase_1_environment_reproducibility_follow_up_20260718221255.md](designer_review_phase_1_environment_reproducibility_follow_up_20260718221255.md)
- Latest Implementer Status: [implementer_status_phase_1_environment_reproducibility_follow_up_20260718214958.md](implementer_status_phase_1_environment_reproducibility_follow_up_20260718214958.md)
- supersedes: なし（新規Phase 1-B専用Handoff系列）

## 1. Handoff Conclusion

Phase 1-Aは完了し、Phase 1-BのModel Runtime Contract詳細設計とADR-0006はユーザー承認済みである。

実装担当は、ユーザーからPhase 1-B実装開始と必要な書込範囲について明示的な許可を得た後、本Handoffの範囲を実装する。

本Handoffを受け取ったことだけで、実装、File変更、Model Hash計算、Dependency変更またはCommand実行が自動的に解禁されるわけではない。

## 2. Required Reading Order

実装開始前に、次を読み取り専用で確認する。

1. [documentation_index_20260718224308.md](../documentation_index_20260718224308.md)
2. [phase_1b_model_runtime_contract_20260718223203.md](../architecture/phase_1b_model_runtime_contract_20260718223203.md)
3. [adr_0006_model_runtime_port_and_configuration_20260718224308.md](../adr/adr_0006_model_runtime_port_and_configuration_20260718224308.md)
4. [designer_review_phase_1_environment_reproducibility_follow_up_20260718221255.md](designer_review_phase_1_environment_reproducibility_follow_up_20260718221255.md)
5. [python_environment_and_dependency_strategy_20260718201744.md](../architecture/python_environment_and_dependency_strategy_20260718201744.md)
6. [project_directory_structure_20260718192110.md](../architecture/project_directory_structure_20260718192110.md)
7. [model_strategy_20260718174637.md](../architecture/model_strategy_20260718174637.md)
8. [system_architecture_20260718193435.md](../architecture/system_architecture_20260718193435.md)

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

