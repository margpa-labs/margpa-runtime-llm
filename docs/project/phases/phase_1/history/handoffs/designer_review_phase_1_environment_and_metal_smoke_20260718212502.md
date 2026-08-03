# Phase 1 Environment／Metal Smoke 設計レビューと実装担当へのFollow-up

- 文書ID: `designer_review_phase_1_environment_and_metal_smoke`
- 状態: `current_follow_up_required`
- 作成日時: `2026-07-18 21:25:02 JST`
- 更新日時: `2026-07-18 21:25:02 JST`
- 作成担当: 設計者役担当Task
- 対象: 実装者役担当Task
- 正本言語: 日本語
- Review対象: [implementer_status_phase_1_environment_and_metal_smoke_20260718210342.md](implementer_status_phase_1_environment_and_metal_smoke_20260718210342.md)
- Environment Architecture: [python_environment_and_dependency_strategy_20260718201744.md](../architecture/python_environment_and_dependency_strategy_20260718201744.md)
- Environment ADR: [adr_0005_python_environment_and_dependency_management_20260718201744.md](../adr/adr_0005_python_environment_and_dependency_management_20260718201744.md)
- Previous Environment Handoff: [designer_python_environment_handoff_20260718201744.md](designer_python_environment_handoff_20260718201744.md)
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

