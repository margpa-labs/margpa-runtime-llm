# Lightning Pure CPU 実績ベース環境再構築マニュアル

- 文書ID: `lightning_pure_cpu_actual_environment_reconstruction_manual`
- 状態: `current_verified_procedure`
- 作成日時: `2026-07-26 09:24:13 JST`
- 更新日時: `2026-07-26 09:24:13 JST`
- Snapshot: `20260726092413`
- 作成担当: 設計者役担当Task
- 対象: Phase 1-F Lightning Linux x86_64 Pure CPU External Runtime
- 対象環境: Lightning AI Studio／Ubuntu Linux／x86_64／Container／Pure CPU
- 正本言語: 日本語
- Documentation Index: [documentation_index_20260726092413.md](../documentation_index_20260726092413.md)
- External Runtime Review: [designer_review_phase_1f_lightning_external_pure_cpu_runtime_20260726092413.md](../handoffs/designer_review_phase_1f_lightning_external_pure_cpu_runtime_20260726092413.md)
- Test-only Follow-up: [designer_handoff_phase_1f_lightning_test_isolation_follow_up_20260726092413.md](../handoffs/designer_handoff_phase_1f_lightning_test_isolation_follow_up_20260726092413.md)
- Previous Planned Manual: [lightning_cpu_upload_and_environment_reconstruction_manual_20260725215627.md](lightning_cpu_upload_and_environment_reconstruction_manual_20260725215627.md)
- supersedes: `lightning_cpu_upload_and_environment_reconstruction_manual_20260725215627.md`

## 1. 文書の目的

本Manualは、事前設計だけではなく、Lightning AI Studioで実際に発生したError、経路変更、修正、検証結果を反映したCurrent手順である。

次を一つの再現可能な経路として整理する。

- Project／Model／Runtime Toolの最終配置
- Model Symbolic Linkの循環修正
- Full Repository Testに必要なUpload Artifact
- Shell Scriptの実行権限
- Project専用`uv 0.11.29`
- Studio Active Conda Environmentを使用しなかった理由
- Project-local `.venv`の再構築
- Pure CPU版`llama-cpp-python`の明示的Native Build
- `MARGPA_ENV_PREFIX`の確定
- Environment Verification
- Repository Test
- Ruff／Format／Mypy
- Bounded Native Acceptance
- Test Isolationに起因する残件

旧Manualは履歴として保持するが、本ManualをCurrent Lightning Pure CPU手順とする。

## 2. 最終判定

ユーザー実行によって次が確認された。

```text
Model Artifact Path             : PASS
Project-local uv 0.11.29        : PASS
uv Binary SHA-512               : PASS
Python 3.12.11                  : PASS
Project-local .venv             : PASS
Pure CPU llama-cpp-python       : PASS
Environment Verification        : PASS
Ruff Check                      : PASS
Ruff Format                     : PASS
Mypy                            : PASS
Bounded Native Acceptance       : PASS
all_required_checks_passed      : true
Profile Key                     : external.lightning-linux-x86_64.cpu-native
Full Repository Test            : 264 passed／2 Test Isolation Fail
External Pure CPU Runtime       : ACCEPTED
Full Suite Green                : PENDING Test-only Follow-up
```

残る2件はProduction Runtime Failureではなく、Unit Testが実Lightning Container状態から分離されていないTest Portability問題である。

## 3. 実際に成立したDirectory構成

```text
/teamspace/studios/this_studio/
├─ margpa-runtime-llm/
│  ├─ .python-version
│  ├─ .venv/
│  ├─ config/
│  ├─ models -> ../models
│  ├─ pyproject.toml
│  ├─ scripts/
│  ├─ src/
│  ├─ tests/
│  └─ uv.lock
│
├─ models/
│  └─ main/
│     └─ qwen3-4b/
│        └─ gguf/
│           └─ Qwen3-4B-Q4_K_M.gguf
│
└─ .runtime-tools/
   └─ uv/
      └─ 0.11.29/
         └─ bin/
            ├─ uv
            └─ uvx
```

最終Path：

```text
Workspace Root : /teamspace/studios/this_studio
Project Root   : /teamspace/studios/this_studio/margpa-runtime-llm
Model Root     : /teamspace/studios/this_studio/models
Project Venv   : /teamspace/studios/this_studio/margpa-runtime-llm/.venv
uv Binary Dir : /teamspace/studios/this_studio/.runtime-tools/uv/0.11.29/bin
```

旧Manualで想定した多重Model Directory：

```text
models/margpa-runtime-llm/models/
```

はCurrent Lightningでは使用しない。Model Root直下に`main/`が存在すればRegistry Contractを満たす。

## 4. Model RootとSymbolic Link

### 4.1 Registryが要求する構造

```text
MODEL_ROOT/
└─ main/
   └─ qwen3-4b/
      └─ gguf/
         └─ Qwen3-4B-Q4_K_M.gguf
```

Current Lightning Model Root：

```text
/teamspace/studios/this_studio/models
```

確認：

```bash
test -f \
  /teamspace/studios/this_studio/models/main/qwen3-4b/gguf/Qwen3-4B-Q4_K_M.gguf

printf 'MODEL_CHECK_EXIT=%s\n' "$?"
```

期待値：

```text
MODEL_CHECK_EXIT=0
```

### 4.2 発生した循環Link

初回配置ではProject内に実Directory`models/`があり、その内部の`models` Linkが自身を再参照した。

```text
margpa-runtime-llm/models/      # 実Directory
└─ models                      # 循環Symbolic Link
```

結果：

```text
find: models/models: Too many levels of symbolic links
```

### 4.3 最終Link

循環状態を修正する前に、Project内`models/`に実Modelや別Fileがないことを確認する。

```bash
cd /teamspace/studios/this_studio/margpa-runtime-llm

ls -la models
readlink models/models || true
```

`models/`内に循環Linkの`models`だけが存在する場合：

```bash
unlink models/models
rmdir models
```

実Modelや別Fileが存在する場合は削除せず、内容を確認してからModel Rootへ移動または退避する。

Project内からSibling Model Rootを参照する場合：

```bash
cd /teamspace/studios/this_studio/margpa-runtime-llm

ln -s ../models models
```

期待状態：

```text
margpa-runtime-llm/models -> ../models
```

確認：

```bash
ls -ld models
readlink models
ls models/
```

期待値：

```text
models -> ../models
../models
main
```

Symbolic Linkは必須ではない。全Commandへ`--model-root`を明示するCurrent手順では、次を正本とする。

```bash
export MARGPA_MODEL_ROOT=/teamspace/studios/this_studio/models
```

## 5. Upload対象の最終判断

### 5.1 Runtime／Native Acceptance必須

```text
config/
scripts/
src/
pyproject.toml
uv.lock
```

### 5.2 Full Repository Testにも必要

```text
tests/
.python-version
```

`.python-version`はLocal Macの既定Python`3.13.14`を示すProject Metadataである。Lightning Runtime Pythonを決めるFileとして使用しないが、Repository Contract Testが内容を確認するため、Full Suiteを実行するBundleには含める。

Lightning Runtimeは明示したProject `.venv`のPython 3.12.11を使用する。

### 5.3 任意

```text
.gitignore
```

RuntimeまたはTest実行には必須ではない。

### 5.4 除外

```text
Local Mac .venv/
Local Mac models Symbolic Link
GGUF本体を含むProject Bundle
docs/
.git/
.DS_Store
__pycache__/
*.pyc
*.pyo
*.so
.pytest_cache/
.ruff_cache/
.mypy_cache/
.coverage
htmlcov/
.ipynb_checkpoints/
var/
.env
.env.*
*.log
*.zip
```

GGUFはProject Bundleと別に、Lightning Model Rootへ配置する。

## 6. File Mode

Browser UploadまたはArchive展開では、Shell Scriptの実行権限が失われる場合がある。

発生したError：

```text
PermissionError: [Errno 13] Permission denied:
scripts/setup/preflight_lightning_ai_studio.sh
```

Manual実行では`bash script.sh`により回避できるが、Unit TestはScriptを直接実行するため、実行権限が必要である。

修正：

```bash
cd /teamspace/studios/this_studio/margpa-runtime-llm

chmod u+x \
  scripts/setup/preflight_lightning_ai_studio.sh \
  scripts/setup/setup_lightning_linux_x86_64_cpu.sh
```

確認：

```bash
ls -l \
  scripts/setup/preflight_lightning_ai_studio.sh \
  scripts/setup/setup_lightning_linux_x86_64_cpu.sh
```

期待状態：

```text
-rwxr-xr-x
```

Upload後の受入CheckへFile Mode確認を含める。

## 7. 共通Environment Variable

新しいTerminalを開くたびに設定する。

```bash
export MARGPA_WORKSPACE_ROOT=/teamspace/studios/this_studio
export MARGPA_PROJECT_ROOT="$MARGPA_WORKSPACE_ROOT/margpa-runtime-llm"
export MARGPA_MODEL_ROOT="$MARGPA_WORKSPACE_ROOT/models"
export MARGPA_UV_BIN="$MARGPA_WORKSPACE_ROOT/.runtime-tools/uv/0.11.29/bin"
export MARGPA_ENV_PREFIX="$MARGPA_PROJECT_ROOT/.venv"
export PATH="$MARGPA_UV_BIN:$PATH"
```

確認：

```bash
printf 'PROJECT_ROOT=%s\n' "$MARGPA_PROJECT_ROOT"
printf 'MODEL_ROOT=%s\n' "$MARGPA_MODEL_ROOT"
printf 'UV_BIN=%s\n' "$MARGPA_UV_BIN"
printf 'ENV_PREFIX=%s\n' "$MARGPA_ENV_PREFIX"
```

## 8. Project専用`uv 0.11.29`

Lightning既設`uv 0.11.18`を変更せず、Project用`0.11.29`を隔離配置する。

```bash
mkdir -p "$MARGPA_UV_BIN"

curl -LsSf https://astral.sh/uv/0.11.29/install.sh \
  | env UV_UNMANAGED_INSTALL="$MARGPA_UV_BIN" sh
```

PATH：

```bash
export PATH="$MARGPA_UV_BIN:$PATH"

command -v uv
uv --version
```

期待値：

```text
/teamspace/studios/this_studio/.runtime-tools/uv/0.11.29/bin/uv
uv 0.11.29 (x86_64-unknown-linux-gnu)
```

SHA-512：

```bash
printf '%s  %s\n' \
  '957e3ee915fef24101de24a8414c4a9f60e3bd25f0e127eb89a12a78e6bbb6f79621dcb5e10dc41e31834f77a6d7180bebcdfc7ccb08901eba059cde627e8d48' \
  "$MARGPA_UV_BIN/uv" \
  | sha512sum --check -
```

期待値：

```text
uv: OK
```

## 9. Python

Observed：

```text
python3       : 3.12.11
python        : 3.12.11
VIRTUAL_ENV   : unset
CONDA_PREFIX  : set
```

確認：

```bash
python3 --version
python --version
printf 'VIRTUAL_ENV=%s\n' "${VIRTUAL_ENV:-<unset>}"
printf 'CONDA_PREFIX=%s\n' "${CONDA_PREFIX:-<unset>}"
```

Current Lightning ContractはPython 3.12.11である。

## 10. 途中で変更したEnvironment方式

### 10.1 初期案

```text
--environment-mode auto
```

`auto`は`CONDA_PREFIX`を検出し、`studio-active`を選択した。

### 10.2 発生したError

```text
Project virtual environment directory <Studio Active Conda Prefix>
cannot be used because it is not a compatible environment
but cannot be recreated because it is not a virtual environment
```

LightningのActive Conda PrefixはPython実行元として利用できるが、Current `uv`がProject Environmentとして再作成・管理できる形式ではなかった。

### 10.3 最終方式

```text
Environment Mode : project-venv
Target Venv      : margpa-runtime-llm/.venv
Base Python      : Lightning Python 3.12.11
```

`auto`を使用せず、Studio Environment VariableをSetup Processから除外する。

```bash
env -u VIRTUAL_ENV -u CONDA_PREFIX ...
```

Current Lightning Pure CPUでは、この明示方式を正本とする。

## 11. Pure CPU Preflight

```bash
cd "$MARGPA_PROJECT_ROOT"

env -u VIRTUAL_ENV -u CONDA_PREFIX \
  PATH="$MARGPA_UV_BIN:$PATH" \
  MARGPA_MODEL_ROOT="$MARGPA_MODEL_ROOT" \
  bash scripts/setup/preflight_lightning_ai_studio.sh \
  --runtime-target cpu-native \
  --environment-mode project-venv
```

主要期待値：

```text
Runtime target   : cpu-native
Environment mode : project-venv
Environment path : .../margpa-runtime-llm/.venv
Python           : 3.12.11
uv               : 0.11.29
Pure CPU Profile : parseable
GPU required     : no
nvcc available   : not_probed
Model Root       : present
```

`--runtime-target cpu-native`はPreflight専用Optionである。他のScriptへ同じOptionを付けない。

## 12. Setup Plan

```bash
env -u VIRTUAL_ENV -u CONDA_PREFIX \
  PATH="$MARGPA_UV_BIN:$PATH" \
  bash scripts/setup/setup_lightning_linux_x86_64_cpu.sh \
  --plan \
  --environment-mode project-venv \
  --venv "$MARGPA_PROJECT_ROOT/.venv" \
  --model-root "$MARGPA_MODEL_ROOT"
```

確認された解決：

```text
Model Root:
  /teamspace/studios/this_studio/models

Resolved Artifact:
  /teamspace/studios/this_studio/models/main/qwen3-4b/gguf/Qwen3-4B-Q4_K_M.gguf
```

`--plan`はEnvironmentを変更しない。また、Plan成功だけではuv、Native BackendまたはVerification成功を意味しない。

## 13. Project `.venv`構築

```bash
env -u VIRTUAL_ENV -u CONDA_PREFIX \
  PATH="$MARGPA_UV_BIN:$PATH" \
  bash scripts/setup/setup_lightning_linux_x86_64_cpu.sh \
  --environment-mode project-venv \
  --venv "$MARGPA_PROJECT_ROOT/.venv" \
  --model-root "$MARGPA_MODEL_ROOT"
```

### 13.1 Entry Pointだけでは完了判定しない

途中状態では次が存在していても：

```text
.venv/bin/python
.venv/bin/pytest
.venv/bin/margpa-llm
.venv/bin/margpa-web
```

`llama_cpp`が未導入である場合があった。

発生したError：

```text
ModuleNotFoundError: No module named 'llama_cpp'
```

Entry Pointの存在はNative Backend完成の証拠ではない。

### 13.2 明示的Native Rebuild

```bash
env -u VIRTUAL_ENV -u CONDA_PREFIX \
  PATH="$MARGPA_UV_BIN:$PATH" \
  bash scripts/setup/setup_lightning_linux_x86_64_cpu.sh \
  --environment-mode project-venv \
  --venv "$MARGPA_PROJECT_ROOT/.venv" \
  --rebuild-native \
  --model-root "$MARGPA_MODEL_ROOT"
```

期待する最終Message：

```text
Phase 1-F Lightning Linux/x86_64 Pure CPU setup completed successfully.
```

このMessageとEnvironment Verificationの両方を完了条件にする。

## 14. Environment Prefix

Setup成功後：

```bash
export MARGPA_ENV_PREFIX="$MARGPA_PROJECT_ROOT/.venv"
```

`MARGPA_ENV_PREFIX`が空のまま：

```bash
"$MARGPA_ENV_PREFIX/bin/python"
```

を実行すると、Pathは`/bin/python`になる。

発生したError：

```text
no such file or directory: /bin/python
no such file or directory: /bin/pytest
```

確認：

```bash
for MARGPA_COMMAND in python pytest margpa-llm margpa-web; do
  if test -x "$MARGPA_ENV_PREFIX/bin/$MARGPA_COMMAND"; then
    printf 'OK: %s\n' "$MARGPA_COMMAND"
  else
    printf 'MISSING: %s\n' "$MARGPA_COMMAND"
  fi
done
```

全項目`OK`を要求する。

## 15. Native Backend Import確認

```bash
"$MARGPA_ENV_PREFIX/bin/python" -c '
import importlib.metadata
from llama_cpp import llama_cpp

print("llama-cpp-python:", importlib.metadata.version("llama-cpp-python"))
print("gpu_offload_supported:", llama_cpp.llama_supports_gpu_offload())
print(llama_cpp.llama_print_system_info().decode("utf-8", errors="replace"))
'
```

主要期待値：

```text
llama-cpp-python: 0.3.34
gpu_offload_supported: False
```

CUDA、Metal、ROCmまたはHIPが有効なBackendとして検出されないことを確認する。

## 16. Environment Verification

```bash
cd "$MARGPA_PROJECT_ROOT"

"$MARGPA_ENV_PREFIX/bin/python" \
  scripts/setup/verify_phase1_environment.py \
  --target lightning-cpu-native
```

確認された結果：

```text
Environment Verification : PASS
Target                   : lightning-cpu-native
Python                   : 3.12.11
Backend Build Variant    : cpu
GPU Offload Supported    : false
Device Kind              : cpu
Acceleration API         : none
GPU／CUDA Probe           : not required／not probed
```

## 17. Repository Test

### 17.1 Clean Test Environment

Shellへ設定した`MARGPA_MODEL_ROOT`がUnit TestのTemporary Model Rootへ漏出した。

発生したError：

```text
The Model Root/Path does not match the Registry artifact layout
```

Production Setupは、実Model RootとTest用Temporary Model Pathの不一致を設計どおりFail Closedした。Test ProcessではApplication用Environment Variableを除外する。

```bash
env -u MARGPA_MODEL_ROOT \
  -u MARGPA_PROFILE \
  "$MARGPA_ENV_PREFIX/bin/pytest" -q
```

### 17.2 Upload起因の初回Failure

初回：

```text
8 failed
258 passed
1 skipped
3 deselected
```

内訳：

```text
Shell Script実行権限不足 : 5
.python-version不足      : 1
Platform Test Isolation  : 2
```

File Modeと`.python-version`の修正後：

```text
3 failed
263 passed
1 skipped
3 deselected
```

Environment Variableを除外後：

```text
2 failed
264 passed
1 skipped
3 deselected
```

Linux上のApple Silicon Metal Test 1件Skipは正常である。Model Smoke 3件は既定でDeselectされる。

## 18. Static Check

```bash
"$MARGPA_ENV_PREFIX/bin/ruff" check .
"$MARGPA_ENV_PREFIX/bin/ruff" format --check .
"$MARGPA_ENV_PREFIX/bin/mypy"
```

確認結果：

```text
Ruff Check        : All checks passed
Ruff Format       : 95 files already formatted
Mypy              : Success／no issues found in 95 source files
```

## 19. Bounded Native Acceptance

```bash
"$MARGPA_ENV_PREFIX/bin/python" \
  scripts/models/phase1f_cross_environment_acceptance.py \
  --profile config/profiles/lightning_linux_x86_64_cpu_native.toml \
  --model-root "$MARGPA_MODEL_ROOT"
```

ユーザー実行Evidence：

```text
all_required_checks_passed : true
profile_key                : external.lightning-linux-x86_64.cpu-native
```

Script Contract上、`all_required_checks_passed=true`は全Required CheckがTrueであることを意味する。

含まれる確認：

- Artifact SHA-512
- Runtime／Profile一致
- Pure CPU Evidence
- Japanese／English
- Non-stream
- Streaming
- Cooperative Cancel
- Cancel後再生成
- Thinking Protocol
- Hidden／Visible Thinking分離
- Unload

Test-only Follow-upではProduction Runtimeを変更しないため、この高コストAcceptanceを再実行する必要はない。

## 20. 残る2件

```text
tests/unit/inference/test_deployment_platform.py::
  test_profile_resolution_priority_is_explicit_then_environment_then_default

tests/unit/inference/test_deployment_platform.py::
  test_future_platform_alias_and_default_are_registry_only_extensions
```

TestはOS／ArchitectureをMockして`native` Defaultを検証するが、Execution Environmentだけは実Lightning Container Markerから取得する。

```text
Test想定           : native
Actual Environment : container
```

必要なTest-only修正：

```python
raw_execution_environment="native",
```

Production Code、Pure CPU Profile、Model Root、BackendまたはRuntimeを変更しない。

## 21. 最終再現手順

### 21.1 Variable

```bash
export MARGPA_WORKSPACE_ROOT=/teamspace/studios/this_studio
export MARGPA_PROJECT_ROOT="$MARGPA_WORKSPACE_ROOT/margpa-runtime-llm"
export MARGPA_MODEL_ROOT="$MARGPA_WORKSPACE_ROOT/models"
export MARGPA_UV_BIN="$MARGPA_WORKSPACE_ROOT/.runtime-tools/uv/0.11.29/bin"
export MARGPA_ENV_PREFIX="$MARGPA_PROJECT_ROOT/.venv"
export PATH="$MARGPA_UV_BIN:$PATH"

cd "$MARGPA_PROJECT_ROOT"
```

### 21.2 Artifact

```bash
test -f "$MARGPA_MODEL_ROOT/main/qwen3-4b/gguf/Qwen3-4B-Q4_K_M.gguf"
test -d tests
test -f .python-version
```

### 21.3 Permission

```bash
chmod u+x \
  scripts/setup/preflight_lightning_ai_studio.sh \
  scripts/setup/setup_lightning_linux_x86_64_cpu.sh
```

### 21.4 Preflight

```bash
env -u VIRTUAL_ENV -u CONDA_PREFIX \
  PATH="$MARGPA_UV_BIN:$PATH" \
  MARGPA_MODEL_ROOT="$MARGPA_MODEL_ROOT" \
  bash scripts/setup/preflight_lightning_ai_studio.sh \
  --runtime-target cpu-native \
  --environment-mode project-venv
```

### 21.5 Setup

```bash
env -u VIRTUAL_ENV -u CONDA_PREFIX \
  PATH="$MARGPA_UV_BIN:$PATH" \
  bash scripts/setup/setup_lightning_linux_x86_64_cpu.sh \
  --environment-mode project-venv \
  --venv "$MARGPA_PROJECT_ROOT/.venv" \
  --model-root "$MARGPA_MODEL_ROOT"
```

Backend未完成時のみ：

```bash
env -u VIRTUAL_ENV -u CONDA_PREFIX \
  PATH="$MARGPA_UV_BIN:$PATH" \
  bash scripts/setup/setup_lightning_linux_x86_64_cpu.sh \
  --environment-mode project-venv \
  --venv "$MARGPA_PROJECT_ROOT/.venv" \
  --rebuild-native \
  --model-root "$MARGPA_MODEL_ROOT"
```

### 21.6 Verification

```bash
"$MARGPA_ENV_PREFIX/bin/python" \
  scripts/setup/verify_phase1_environment.py \
  --target lightning-cpu-native
```

### 21.7 Test

```bash
env -u MARGPA_MODEL_ROOT \
  -u MARGPA_PROFILE \
  "$MARGPA_ENV_PREFIX/bin/pytest" -q
```

### 21.8 Static

```bash
"$MARGPA_ENV_PREFIX/bin/ruff" check .
"$MARGPA_ENV_PREFIX/bin/ruff" format --check .
"$MARGPA_ENV_PREFIX/bin/mypy"
```

### 21.9 Native Acceptance

```bash
"$MARGPA_ENV_PREFIX/bin/python" \
  scripts/models/phase1f_cross_environment_acceptance.py \
  --profile config/profiles/lightning_linux_x86_64_cpu_native.toml \
  --model-root "$MARGPA_MODEL_ROOT"
```

## 22. 次のGate

```text
Test-only Cross-platform Isolation Fix
  → Mac Full Suite
  → Lightning Full Suite
  → Full Suite Green Review
  → Lightning Web Preview起動／手動確認
  → Phase 1全体Gate判定
```

External Pure CPU Runtime自体はAcceptedである。Full Suite GreenとTop-level Phase 1完了は未宣言である。
