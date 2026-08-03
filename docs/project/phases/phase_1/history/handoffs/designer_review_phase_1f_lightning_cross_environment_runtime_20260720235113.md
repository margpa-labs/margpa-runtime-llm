# Phase 1-F Lightning Cross-environment Runtime 設計Review

- 文書ID: `designer_review_phase_1f_lightning_cross_environment_runtime`
- 状態: `changes_requested_before_lightning_native_verification`
- 作成日時: `2026-07-20 23:51:13 JST`
- 更新日時: `2026-07-20 23:51:13 JST`
- Snapshot: `20260720235113`
- 作成担当: 設計者役担当Task
- 対象: Phase 1-F Repository実装とLightning Native Verification準備状態
- 正本言語: 日本語
- 実装報告: [implementer_status_phase_1f_lightning_cross_environment_runtime_20260719205819.md](implementer_status_phase_1f_lightning_cross_environment_runtime_20260719205819.md)
- 要件: [phase_1f_lightning_cross_environment_runtime_requirements_20260719202333.md](../requirements/phase_1f_lightning_cross_environment_runtime_requirements_20260719202333.md)
- ADR: [adr_0015_phase_1f_lightning_and_python_312_support_20260719202333.md](../adr/adr_0015_phase_1f_lightning_and_python_312_support_20260719202333.md)
- 実装Handoff: [implementer_handoff_phase_1f_lightning_cross_environment_runtime_20260719202333.md](implementer_handoff_phase_1f_lightning_cross_environment_runtime_20260719202333.md)
- 最新Index: [documentation_index_20260720235113.md](../documentation_index_20260720235113.md)
- supersedes: なし（Phase 1-F Review系列の初回）

## 1. Review結論

Phase 1-FのRepository実装は、Python Support Range、Platform／Profile分離、Container検出、CUDA／CPU Profile、Safe Failure、Setup Recipe、Mac Regressionの方向で要件に沿っている。

ただし、Lightningへ一度だけ搬入してMandatory Gateを実行する前に修正すべきFindingがあるため、現時点ではPhase 1-Fを受け入れない。

```text
Blocking Finding              : 0
High Finding                  : 2
Medium Finding                : 2
Low Observation               : 1
Repository Static Gate        : Pass
Mac Python 3.13／Metal Gate   : Pass
Python 3.12 Native Gate       : Not Run
Lightning CUDA Native Gate    : Not Run
Lightning CPU Candidate Gate  : Not Run
Final Decision                : Changes Requested
```

次の3点がLightning搬入前の必須Follow-upである。

1. CUDA Build対応／要求値と、実際のGPU Offload Evidenceを分離する。
2. Acceptance ProbeをFail Closedにし、主要Check不合格時は非0で終了させる。
3. Response Language／Thinking PresentationのNative Evidenceを実際の合否条件へ含める。

## 2. Review対象

### Configuration／Root

```text
pyproject.toml
uv.lock
config/platforms/platform_registry.toml
config/profiles/lightning_linux_x86_64_cuda.toml
config/profiles/lightning_linux_x86_64_cpu.toml
```

### Source

```text
src/margpa_runtime_llm/bootstrap/profile_resolver.py
src/margpa_runtime_llm/bootstrap/phase1_application.py
src/margpa_runtime_llm/modules/inference/contracts/runtime.py
src/margpa_runtime_llm/adapters/model_backends/llama_cpp/runtime_detection.py
src/margpa_runtime_llm/adapters/model_backends/llama_cpp/adapter.py
src/margpa_runtime_llm/entrypoints/cli/main.py
```

### Scripts

```text
scripts/setup/verify_phase1_environment.py
scripts/setup/setup_lightning_linux_x86_64_cuda.sh
scripts/models/phase1f_cross_environment_acceptance.py
```

### Tests

```text
tests/unit/inference/test_config_and_registry.py
tests/unit/inference/test_deployment_platform.py
tests/unit/inference/test_cli.py
tests/integration/llama_cpp/test_phase1b_runtime.py
tests/integration/llama_cpp/test_phase1f_cross_environment_runtime.py
```

## 3. Positive Findings

次は設計と実装の両方で成立している。

- `requires-python = ">=3.12,<3.14"`とPython 3.12基準のRuff／Mypy設定
- `.python-version = 3.13.14`によるMac Primary維持
- Platform Registry Schema 2と`native／container`分離
- Linux／x86_64／Container／UbuntuのPre-load照合
- Lightning CUDA／CPUのExplicit Profile
- CUDA Profileの`fallback_policy = deny`
- CPU Profileの`gpu_layers = 0`
- ProfileとLoaded Runtime不一致時のUnload／Safe Failure
- Mac Default Profileを維持し、Lightning Profileを暗黙選択しない構造
- Normal Dependency SyncとNative Package Rebuildの分離
- Existing CUDA Build再利用Hook
- CLI Helpの仮引数説明とOption配置説明
- Hidden ThinkingがToken上限へ達した場合のSafe Warning
- Mac 3.13.14／Metalの既存Runtime非Regression

## 4. Findings

### 4.1 High: `gpu_offload=true`が実GPU使用の観測値ではない

対象：

- `src/margpa_runtime_llm/adapters/model_backends/llama_cpp/runtime_detection.py`
- `src/margpa_runtime_llm/adapters/model_backends/llama_cpp/adapter.py`
- `src/margpa_runtime_llm/bootstrap/profile_resolver.py`
- `scripts/setup/verify_phase1_environment.py`

Current判定は次の組合せである。

```text
llama_print_system_info()にCUDA Markerがある
llama_supports_gpu_offload()がtrue
gpu_layersが0ではない
  ↓
device_kind=gpu
acceleration_api=cuda
gpu_offload=true
```

ここで観測しているのは、BackendがCUDA Buildであること、GPU Offload Capabilityを持つこと、ConfigがOffloadを要求していることまでである。実際にModel LayerがGPUへ配置されたこと、当該ProcessがGPU Memoryを使用したことは観測していない。

そのため、CUDA-enabled Buildが存在し`gpu_layers=-1`を指定しただけで、実行時のGPU Offload Evidenceがなくても`gpu_offload=true`と申告できる。これはPhase 1-F Mandatory Gateの「GPU未割当時にCPUへ黙ってFallbackしない」「GPU Offloadを観測する」と一致しない。

Required Follow-up：

- Build Capability、Configured Request、Loaded／Executed Observationを別FieldまたはSource付き状態として扱う。
- `gpu_offload=true`を実観測値として維持する場合、llama.cpp Native Load EvidenceまたはProcess単位GPU Memory Evidenceを取得する。
- 実観測できない場合は`requested／supported／unverified`として表現し、`observed=true`を偽装しない。
- Lightning CUDA Acceptanceで、Allocated GPUの存在だけでなくModel LoadによるGPU使用を証明する。

### 4.2 High: Acceptance ProbeがCheck不合格でも成功終了できる

対象：

- `scripts/models/phase1f_cross_environment_acceptance.py`
- `scripts/setup/setup_lightning_linux_x86_64_cuda.sh`
- `tests/integration/llama_cpp/test_phase1f_cross_environment_runtime.py`

Acceptance Scriptは例外が発生しなければ`"success": true`を出力してExit Code 0を返す。`checks`内のBoolean／Length／Parse Statusを合否へ集約していない。

したがって、次のような状態でもDirect Scriptは成功終了できる。

- Non-stream／Stream Outputが空
- Cancelが成立しない
- Post-cancel Generationが成立しない
- Thinkingが検出されない
- Hidden／Visible Presentationが要件を満たさない
- Response Language Contractが成立しない

Integration Testは一部FieldをAssertするが、Setup Scriptの`--cuda-smoke`／`--cpu-smoke`はIntegration TestではなくAcceptance Scriptを直接実行する。Mandatory CommandがExit 0でも主要Checkが不合格になり得る。

Required Follow-up：

- Acceptance Script自身が全必須Checkを評価する。
- `all_required_checks_passed`を構造化出力する。
- 1件でも必須Checkが不合格なら`success=false`かつ非0で終了する。
- Integration TestはScriptの全必須Checkと終了CodeをAssertする。
- Setup ScriptはそのFail Closed結果を受けて終了する。

### 4.3 Medium: Language／Thinking Native Evidenceが受入条件になっていない

Mac実機でCurrent Acceptance Probeを独立実行した結果：

```text
success                       : true
thinking_parse_status         : unclosed_reasoning
hidden_reasoning_not_displayed: true
visible_thinking_chars        : 557
```

`unclosed_reasoning`でもScriptは成功した。さらに、`hidden_reasoning_not_displayed`は`reasoning_content is None`でもtrueとなり、Thinkingを全く検出できない場合にも合格相当の値になり得る。`visible_thinking_chars`はReasoning部分ではなくDisplay全体の文字数である。

Response Languageも、日本語／英語結果の文字数だけを記録しており、Policy、Message Composition、最終回答Languageを合否へ含めていない。日本語Promptの期待値が`OK`であるため、出力自体から日本語応答を証明できない。

Required Follow-up：

- Thinking検出、Reasoning Segment、Final Segment、Hidden非表示、Visible Label表示を個別にAssertする。
- Thinking用Token上限を、短いPromptでFinal Segmentまで安定して生成できる値へ調整する。
- Unclosed Reasoningを安全処理Testとして残す場合、正常Thinking／Final Testとは分離する。
- Response LanguageはResolved PolicyとModelへ渡したSystem Messageを必須Evidenceとする。
- Native Output Languageも確認する場合、日本語と英語を区別可能な期待値を使用する。

### 4.4 Medium: LightningのVenv前提をTarget Environmentで未確認

対象：

- `scripts/setup/setup_lightning_linux_x86_64_cuda.sh`

Setup ScriptはProject Rootの`.venv`作成と`uv sync`を前提とする。一方、LightningのCurrent Official Documentationは、Studio内で追加Environment／Virtual Environmentを作成しない運用を案内している。

- [Lightning Environment persistence](https://lightning.ai/docs/overview/ai-studio/environment-persistence)

実際の対象Studioで`.venv`が利用可能ならCurrent Recipeを維持できるが、利用できない場合はSetup開始直後に停止する。Local Macの`.venv`を転送してはならない点はCurrent方針どおりである。

Required Follow-up：

- Source一式を大規模搬入する前に、対象StudioでProject-local Venv作成可否を確認する。
- 不可の場合、Studio Persistent Python EnvironmentへLock内容を導入する別Modeを設計する。
- どちらを採用しても、Mac Venv／Native PackageをLightningへ転送しない。

### 4.5 Low: `--cpu-only`でも`nvcc`を無条件要求する

対象：

- `scripts/setup/setup_lightning_linux_x86_64_cuda.sh`

Scriptは既存CUDA Buildを再利用できるか確認する前に、`--cpu-only`でも`nvcc`を要求する。GPU Instanceで作成済みCUDA Buildが永続化されていても、CPU Machine側でCUDA Toolkitが見えない場合は再利用判定へ進めない。

CPU Candidate AはBest EffortであるためCUDA Mandatory Gateを止めるFindingではない。ただし、GPU割当上限時のCPU確認を目的としているため、次のいずれかが望ましい。

- `nvcc`をNative Rebuildが必要な場合だけ要求する。
- CUDA Build再利用に必要なRuntime LibraryとImportを先に確認する。
- Candidate Aが不成立なら、そのFailure Evidenceを保存してDeadline-safe Alternativeへ戻す。

## 5. Independent Verification

### 5.1 Static／Default Gate

```text
ruff format --check .                    : Pass／70 files
ruff check .                             : Pass
mypy                                     : Pass／70 source files
python -m compileall -q src scripts tests: Pass
bash -n macOS／Lightning Setup           : Pass
pytest -q                                : Pass／181 passed、3 deselected
uv lock --check --offline                : Pass／117 packages
```

### 5.2 Mac Environment／Native Gate

```text
verify target          : macos-metal
Python                 : 3.13.14
Host                   : macOS／arm64／native
Backend Build Variant  : metal
Device                 : gpu／metal
Dependency Validation  : Pass
Model Smoke            : 2 passed、1 skipped
Cross-environment Probe: Exit 0
```

Sandbox内ではMetal Deviceが利用できずModel Context作成に失敗した。Sandbox外のMac実機Contextで同じModel Smokeを再実行し、2件PassしたためProduct Failureとは扱わない。

Mac Acceptance Probe実測：

```text
Load including SHA-512 : 2.5008 s
RSS before load        : 55,296,000 bytes
RSS after load         : 3,265,101,824 bytes
RSS after unload       : 175,177,728 bytes
Model SHA-512          : Match
Generate／Stream       : Completed
Cancel／Post-cancel    : Completed
Thinking Parse         : unclosed_reasoning
```

### 5.3 未実行Gate

```text
Local Python 3.12.11 Native Test : Interpreter unavailable／Not Run
Lightning Python 3.12.11 Test    : Not Run
Lightning CUDA Build／Load       : Not Run
Lightning Actual GPU Offload     : Not Run
Lightning CPU Candidate A        : Not Run
```

未実行Gateを合格扱いしない実装報告の自己評価は正しい。

## 6. Acceptance Status

| Area | Result | Notes |
|---|---|---|
| Python Metadata／Lock | Conditional Pass | Lock整合Pass、3.12 Native未実行 |
| Mac 3.13／Metal Regression | Pass | Static／Default／Native Pass |
| Platform／Container Contract | Pass | Deterministic Test Pass |
| CUDA／CPU Profile Definition | Pass | `verification_state=defined`維持 |
| CUDA Build Detection | Pass | Build Variant判定としては成立 |
| Actual GPU Offload Observation | Fail | Capability／Requestから推定している |
| Acceptance Probe Fail-closed | Fail | Check不合格をExit Codeへ反映しない |
| Response Language Native Evidence | Fail | 文字数のみ |
| Thinking Native Evidence | Fail | `unclosed_reasoning`でも成功 |
| Lightning Native Gate | Pending | External実行前 |

## 7. Next Gate

```text
実装担当Follow-up
  ├─ Actual GPU Offload Evidence
  ├─ Acceptance Probe Fail Closed
  ├─ Language／Thinking Check強化
  └─ CPU-only Preflight改善または明示Disposition
        ↓
設計者Follow-up Review
        ↓
Lightning環境Preflight／一回のSource搬入
        ↓
Python 3.12／CUDA Mandatory Gate／CPU Candidate Gate
        ↓
後継Implementer Status
        ↓
Phase 1-F Final Review
```

Phase 1-Gの実装、Phase 1完了宣言、Backup、Phase 1-ex、Git、GitHub公開はまだ開始しない。

## 8. Authorization Boundary

本ReviewとIndex作成は、Source／Config／Tests／Scriptsの修正、Lightning操作、Model Download、Backup、Git、GitHub公開を許可しない。Follow-up実装は、ユーザーが本Reviewを実装担当へ渡し、開始を指示した後に行う。

## 9. Append-Only

既存文書を変更せず、新TimestampのReviewとして追加した。
