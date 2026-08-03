# Phase 1 Environment Setup／Qwen3-4B Metal Smoke Test 実装状況

- 文書ID: `implementer_status_phase_1_environment_and_metal_smoke`
- 状態: `completed_for_authorized_scope`
- 作成日時: `2026-07-18 21:03:42 JST`
- 更新日時: `2026-07-18 21:03:42 JST`
- 作成担当: 実装者役担当Task
- 対象: Phase 1 Environment SetupおよびQwen3-4B／Metal Smoke Test
- 正本言語: 日本語
- supersedes: なし（新規Status系列）
- Documentation Index: [documentation_index_20260718201744.md](../documentation_index_20260718201744.md)
- 実装者Handoff: [implementer_handoff_20260718193435.md](implementer_handoff_20260718193435.md)
- Environment Handoff: [designer_python_environment_handoff_20260718201744.md](designer_python_environment_handoff_20260718201744.md)

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
