# Phase 1-B Model Runtime 実装状況

- 文書ID: `implementer_status_phase_1b_model_runtime`
- 状態: `implementation_complete_review_requested`
- 作成日時: `2026-07-18 23:23:54 JST`
- 更新日時: `2026-07-18 23:23:54 JST`
- 作成担当: 実装者役担当Task
- 対象: 設計者役担当Task
- 正本言語: 日本語
- Documentation Index: [documentation_index_20260718224308.md](../documentation_index_20260718224308.md)
- Implementer Handoff: [designer_handoff_phase_1b_model_runtime_20260718224308.md](designer_handoff_phase_1b_model_runtime_20260718224308.md)
- 詳細設計: [phase_1b_model_runtime_contract_20260718223203.md](../architecture/phase_1b_model_runtime_contract_20260718223203.md)
- Accepted ADR: [adr_0006_model_runtime_port_and_configuration_20260718224308.md](../adr/adr_0006_model_runtime_port_and_configuration_20260718224308.md)
- Previous Phase Status: [implementer_status_phase_1_environment_reproducibility_follow_up_20260718214958.md](implementer_status_phase_1_environment_reproducibility_follow_up_20260718214958.md)
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

[public.py](../../src/margpa_runtime_llm/modules/inference/public.py)

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

[adapter.py](../../src/margpa_runtime_llm/adapters/model_backends/llama_cpp/adapter.py)

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

[stream.py](../../src/margpa_runtime_llm/adapters/model_backends/llama_cpp/stream.py)

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

[qwen3_4b_q4_k_m.toml](../../config/models/qwen3_4b_q4_k_m.toml)

Local Profile：

[local_macos_arm64.toml](../../config/profiles/local_macos_arm64.toml)

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

[chat_template.py](../../src/margpa_runtime_llm/adapters/model_backends/llama_cpp/chat_template.py)

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

[pyproject.toml](../../pyproject.toml)

実装：

[main.py](../../src/margpa_runtime_llm/entrypoints/cli/main.py)

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

[phase1b_runtime_acceptance.py](../../scripts/models/phase1b_runtime_acceptance.py)

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
