# Phase 1 Environment再現性 Follow-up 実装状況

- 文書ID: `implementer_status_phase_1_environment_reproducibility_follow_up`
- 状態: `implementation_complete_review_requested`
- 作成日時: `2026-07-18 21:49:58 JST`
- 更新日時: `2026-07-18 21:49:58 JST`
- 作成担当: 実装者役担当Task
- 対象: 設計者役担当Task
- 正本言語: 日本語
- 最新Index: [documentation_index_20260718212502.md](../documentation_index_20260718212502.md)
- Review元: [designer_review_phase_1_environment_and_metal_smoke_20260718212502.md](designer_review_phase_1_environment_and_metal_smoke_20260718212502.md)
- Previous Status: [implementer_status_phase_1_environment_and_metal_smoke_20260718210342.md](implementer_status_phase_1_environment_and_metal_smoke_20260718210342.md)
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

[setup_macos_arm64_metal.sh](../../scripts/setup/setup_macos_arm64_metal.sh)

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

[test_qwen3_model_smoke.py](../../tests/integration/test_qwen3_model_smoke.py)

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

[metal_smoke.py](../../src/margpa_runtime_llm/adapters/model_backends/llama_cpp/metal_smoke.py)へ次を追加した。

```text
backend_cold_init_seconds
model_load_after_backend_init_seconds
first_content_latency_seconds
total_generation_seconds
unload_seconds
```

これはPhase 1 Probe用であり、Production Model Port／Result Contractではない。

## 8. Environment Verification強化

[verify_phase1_environment.py](../../scripts/setup/verify_phase1_environment.py)を次の判定へ変更した。

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
