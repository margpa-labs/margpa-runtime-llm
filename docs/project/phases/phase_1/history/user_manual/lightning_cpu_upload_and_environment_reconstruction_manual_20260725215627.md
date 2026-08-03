# Lightning Pure CPU Upload／環境再構築マニュアル

- 文書ID: `lightning_cpu_upload_and_environment_reconstruction_manual`
- 状態: `current_external_native_acceptance_procedure`
- 作成日時: `2026-07-25 21:56:27 JST`
- 更新日時: `2026-07-25 21:56:27 JST`
- Snapshot: `20260725215627`
- 作成担当: 設計者役担当Task
- 対象: Phase 1-F Lightning Linux x86_64 Pure CPU External Native Acceptance
- 対象環境: Lightning AI Studio／Ubuntu Linux／x86_64／Container／Pure CPU
- 正本言語: 日本語
- Documentation Index: [documentation_index_20260725215627.md](../documentation_index_20260725215627.md)
- Accepted Repository Review: [designer_review_phase_1f_pure_cpu_acceptance_correction_20260725214428.md](../handoffs/designer_review_phase_1f_pure_cpu_acceptance_correction_20260725214428.md)
- 既存Web Manual: [phase_1_web_and_lightning_user_manual_20260721185031.md](phase_1_web_and_lightning_user_manual_20260721185031.md)
- supersedes: なし

## 1. 目的

本Manualは、Local Macで開発・検証したMARGPA Runtime LLMを、Lightning AI StudioのPure CPU環境へ一括Uploadし、環境再構築、Model配置確認、Native Build、受入Probe、Web起動までを行うための手順である。

特に次を明確にする。

- Lightning上の推奨Directory配置
- Uploadに必要なProject Artifact
- Upload前に除外すべきLocal Artifact
- 正しいPreflight ScriptとOption
- `uv 0.11.29`の隔離配置
- Python／Environment Modeの扱い
- Pure CPU用`llama-cpp-python`の再構築
- Model RootとGGUF Artifactの配置
- Environment Verification
- Bounded Native Smoke
- Web Preview起動
- 失敗時の切り分け

本Manualの手順は、外部Lightning操作を自動実行しない。LightningへのUpload、Dependency Install、Native Build、Model Loadおよび公開URL操作はユーザー実行Gateである。

## 2. 現在の正しい対象

### 2.1 Pure CPU Profile

```text
config/profiles/lightning_linux_x86_64_cpu_native.toml
```

主要Contract：

```text
Profile Key       : external.lightning-linux-x86_64.cpu-native
Operating System  : linux
Architecture      : x86_64
Environment       : container
Distribution      : ubuntu
Compute           : cpu
Acceleration API  : none
Backend           : llama_cpp
Build Variant     : cpu
GPU Layers        : 0
Fallback Policy   : deny
```

このProfileはCUDA BuildをCPU実行するProfileではない。CUDA、Metal、ROCm、HIP等を無効化して構築するPure CPU Backendを対象とする。

### 2.2 正しいPreflight Script

質問にあるPathで正しい。

```text
scripts/setup/preflight_lightning_ai_studio.sh
```

ただし、Scriptの既定Targetは後方互換のため`cuda-gpu`である。Pure CPU検証では、必ず次を明示する。

```bash
bash scripts/setup/preflight_lightning_ai_studio.sh \
  --runtime-target cpu-native \
  --environment-mode auto
```

`--cpu-only`は旧CUDA Buildを`gpu_layers=0`でCPU実行する`cuda-cpu`のAliasであり、Pure CPU用ではない。

### 2.3 正しいSetup Script

```text
scripts/setup/setup_lightning_linux_x86_64_cpu.sh
```

このScriptは次を行う。

- Project Lock確認
- Project Dependency同期
- Pure CPU BackendのReuse可否確認
- 必要時の`llama-cpp-python 0.3.34` Source Build
- `lightning-cpu-native` Environment Verification
- Option指定時のBounded Model Smoke

ModelをDownload、移動またはUploadしない。

## 3. 推奨Directory配置

Lightning Workspace Root配下を次の構造にする。

```text
LIGHTNING_WORKSPACE_ROOT/
├─ margpa-runtime-llm/
│  ├─ config/
│  ├─ scripts/
│  ├─ src/
│  ├─ tests/
│  ├─ pyproject.toml
│  ├─ uv.lock
│  └─ .gitignore                  # 任意
│
├─ models/
│  └─ margpa-runtime-llm/
│     └─ models/
│        └─ main/
│           └─ qwen3-4b/
│              └─ gguf/
│                 └─ Qwen3-4B-Q4_K_M.gguf
│
└─ .runtime-tools/
   └─ uv/
      └─ 0.11.29/
         └─ bin/
            ├─ uv
            └─ uvx
```

Project本体、Model Artifact、Runtime Toolを分離する。

```text
Project Source : LIGHTNING_WORKSPACE_ROOT/margpa-runtime-llm
Model Root     : LIGHTNING_WORKSPACE_ROOT/models/margpa-runtime-llm/models
uv Binary Dir : LIGHTNING_WORKSPACE_ROOT/.runtime-tools/uv/0.11.29/bin
```

この配置により、Projectを更新してもModel本体を再Uploadせず、Environmentを再構築してもModel Pathを維持できる。

## 4. Upload対象

### 4.1 最小Runtime／Native Acceptance必須

| 対象 | 必須理由 |
|---|---|
| `src/` | Application、Runtime、Web UI本体 |
| `config/` | Application、Model、Platform、Deployment Profile |
| `scripts/` | Preflight、Setup、Environment Verification、Native Acceptance |
| `pyproject.toml` | Package Metadata、Dependency、Entry Point |
| `uv.lock` | Frozen Dependency正本 |

### 4.2 推奨

| 対象 | 理由 |
|---|---|
| `tests/` | Repository TestとTargeted TestをLightning上で再実行できる |
| `.gitignore` | Local Artifactの再混入を抑制する |

### 4.3 Lightning動作検証には不要

| 対象 | 判断 |
|---|---|
| `docs/` | Current Phase 1 Runtime、Preflight、Native Smoke、Web起動には不要 |
| `.python-version` | Local Macの既定`3.13.14`を示すため、Lightning `3.12.11`の再構築Bundleでは除外推奨 |
| Local Backup／Zip | Runtimeに不要 |
| Screenshot／設計素材 | Runtimeに不要 |

`docs/`は将来のSimple RAGで参照可能にする予定だが、現在は未実装かつ既定OFFである。LightningへはHookのみを持ち込み、Current Pure CPU受入では`docs/`をUpload対象外としてよい。

## 5. Upload前に除外するもの

開発元Projectから直接削除する必要はない。Upload専用Staging Copyから除外する。

### 5.1 必ず除外

| 対象 | 理由 |
|---|---|
| `.venv/` | macOS／ARM64用EnvironmentはLinux／x86_64で再利用不可 |
| `models` | Local SymlinkとGGUF本体はProject Bundleへ含めない |
| `*.gguf` | Model本体をProject Sourceと分離する |
| `.git/` | Current Lightning動作検証に不要。履歴・Remote情報も持ち込まない |
| `.DS_Store` | macOS Metadata |
| `__pycache__/` | Python Cache |
| `*.pyc`、`*.pyo` | Python Bytecode |
| `*.so` | Platform依存Native Build Artifact |
| `.pytest_cache/` | Test Cache |
| `.ruff_cache/` | Ruff Cache |
| `.mypy_cache/` | Mypy Cache |
| `.coverage`、`htmlcov/` | Coverage生成物 |
| `.ipynb_checkpoints/` | Jupyter生成物 |
| `var/` | Local Runtime Data |
| `.env`、`.env.*` | CredentialやLocal Override混入防止 |
| `*.log` | Local Log／識別情報混入防止 |
| `*.zip` | Backupの二重Upload防止 |

### 5.2 今回の最小Lightning Bundleでは除外

| 対象 | 理由 |
|---|---|
| `docs/` | Pure CPU Runtime検証に不要 |
| `.python-version` | Local Mac用`3.13.14`の意図しない選択を避ける |

### 5.3 削除してはいけないもの

- `uv.lock`
- `pyproject.toml`
- `config/profiles/lightning_linux_x86_64_cpu_native.toml`
- `config/models/qwen3_4b_q4_k_m.toml`
- `config/platforms/platform_registry.toml`
- `scripts/setup/preflight_lightning_ai_studio.sh`
- `scripts/setup/setup_lightning_linux_x86_64_cpu.sh`
- `scripts/setup/verify_phase1_environment.py`
- `scripts/models/phase1f_cross_environment_acceptance.py`
- `src/`

## 6. MacでUpload用Stagingを作る

### 6.1 Project Rootへ移動する

```bash
cd /path/to/margpa-runtime-llm
export MARGPA_SOURCE_ROOT="$PWD"
```

### 6.2 一時Stagingを作る

```bash
export MARGPA_UPLOAD_STAGE_PARENT="$(mktemp -d)"
export MARGPA_UPLOAD_STAGE="$MARGPA_UPLOAD_STAGE_PARENT/margpa-runtime-llm"

mkdir -p "$MARGPA_UPLOAD_STAGE"
```

### 6.3 必要ArtifactだけCopyする

```bash
rsync -a \
  --exclude '/.venv/' \
  --exclude '/models' \
  --exclude '*.gguf' \
  --exclude '/.git/' \
  --exclude '/docs/' \
  --exclude '/.python-version' \
  --exclude '.DS_Store' \
  --exclude '__pycache__/' \
  --exclude '*.pyc' \
  --exclude '*.pyo' \
  --exclude '*.so' \
  --exclude '.pytest_cache/' \
  --exclude '.ruff_cache/' \
  --exclude '.mypy_cache/' \
  --exclude '.coverage' \
  --exclude 'htmlcov/' \
  --exclude '.ipynb_checkpoints/' \
  --exclude 'var/' \
  --exclude '.env' \
  --exclude '.env.*' \
  --exclude '*.log' \
  --exclude '*.zip' \
  "$MARGPA_SOURCE_ROOT/" \
  "$MARGPA_UPLOAD_STAGE/"
```

このCommandは開発元を変更しない。

### 6.4 必須Artifactを確認する

```bash
test -d "$MARGPA_UPLOAD_STAGE/src"
test -d "$MARGPA_UPLOAD_STAGE/config"
test -d "$MARGPA_UPLOAD_STAGE/scripts"
test -d "$MARGPA_UPLOAD_STAGE/tests"
test -f "$MARGPA_UPLOAD_STAGE/pyproject.toml"
test -f "$MARGPA_UPLOAD_STAGE/uv.lock"
test -f "$MARGPA_UPLOAD_STAGE/config/profiles/lightning_linux_x86_64_cpu_native.toml"
test -f "$MARGPA_UPLOAD_STAGE/config/models/qwen3_4b_q4_k_m.toml"
test -f "$MARGPA_UPLOAD_STAGE/scripts/setup/preflight_lightning_ai_studio.sh"
test -f "$MARGPA_UPLOAD_STAGE/scripts/setup/setup_lightning_linux_x86_64_cpu.sh"
test -f "$MARGPA_UPLOAD_STAGE/scripts/setup/verify_phase1_environment.py"
test -f "$MARGPA_UPLOAD_STAGE/scripts/models/phase1f_cross_environment_acceptance.py"

printf 'Required upload artifacts are present.\n'
```

どれかが欠ける場合、`set -e`を使用していないShellでは後続Commandへ進む可能性がある。各`test`のExit Codeを確認する。

### 6.5 除外対象が残っていないことを確認する

```bash
find "$MARGPA_UPLOAD_STAGE" \
  \( \
    -name '.venv' -o \
    -name '.git' -o \
    -name '.DS_Store' -o \
    -name '__pycache__' -o \
    -name '*.pyc' -o \
    -name '*.pyo' -o \
    -name '*.so' -o \
    -name '.pytest_cache' -o \
    -name '.ruff_cache' -o \
    -name '.mypy_cache' -o \
    -name '.coverage' -o \
    -name 'htmlcov' -o \
    -name '.ipynb_checkpoints' -o \
    -name 'var' -o \
    -name '.env' -o \
    -name '.env.*' -o \
    -name '*.gguf' -o \
    -name '*.log' -o \
    -name '*.zip' \
  \) -print
```

期待結果は出力なしである。

Symlinkも確認する。

```bash
test ! -e "$MARGPA_UPLOAD_STAGE/models"
find "$MARGPA_UPLOAD_STAGE" -type l -print
```

Current Upload Stagingでは出力なしを期待する。

公開禁止識別子は、Upload対象外のPrivate Pattern Fileを使用して確認する。

```bash
rg -n -f /path/to/private_identifier_patterns.txt "$MARGPA_UPLOAD_STAGE"
```

期待結果は出力なしである。Pattern File自体をStagingへCopyしない。

### 6.6 任意のUpload Manifest

```bash
(
  cd "$MARGPA_UPLOAD_STAGE"
  find . -type f -exec shasum -a 512 {} \; | LC_ALL=C sort
) > "$MARGPA_UPLOAD_STAGE_PARENT/margpa-runtime-llm_upload_manifest_sha512.txt"
```

ManifestはStaging本体の外側へ作る。必要に応じてUpload前後の整合確認に使用する。

## 7. Lightningへの配置

### 7.1 Workspace Rootを決める

Lightning Terminalで、ProjectとModelを置く共通Parentへ移動する。

```bash
cd /path/to/lightning/workspace
export MARGPA_WORKSPACE_ROOT="$PWD"
export MARGPA_PROJECT_ROOT="$MARGPA_WORKSPACE_ROOT/margpa-runtime-llm"
export MARGPA_MODEL_ROOT="$MARGPA_WORKSPACE_ROOT/models/margpa-runtime-llm/models"
export MARGPA_UV_BIN="$MARGPA_WORKSPACE_ROOT/.runtime-tools/uv/0.11.29/bin"
```

`/path/to/lightning/workspace`は仮引数であり、実際のLightning Workspace Pathへ置き換える。

### 7.2 Project

Macで作成したStagingの`margpa-runtime-llm/`を、次へUploadする。

```text
$MARGPA_PROJECT_ROOT
```

確認：

```bash
test -f "$MARGPA_PROJECT_ROOT/pyproject.toml"
test -f "$MARGPA_PROJECT_ROOT/uv.lock"
test -f "$MARGPA_PROJECT_ROOT/scripts/setup/preflight_lightning_ai_studio.sh"
```

### 7.3 Model

GGUFを次へ配置する。

```text
$MARGPA_MODEL_ROOT/main/qwen3-4b/gguf/Qwen3-4B-Q4_K_M.gguf
```

確認：

```bash
test -f "$MARGPA_MODEL_ROOT/main/qwen3-4b/gguf/Qwen3-4B-Q4_K_M.gguf"
printf 'MODEL_CHECK_EXIT=%s\n' "$?"
```

`MODEL_CHECK_EXIT=0`を期待する。

### 7.4 Model Symlinkは任意

Runtimeへ`--model-root`を渡すため、Project内`models` Symlinkは必須ではない。

Local Macと同じ見た目にする場合だけ、次を使用できる。

```bash
cd "$MARGPA_PROJECT_ROOT"
test ! -e models
ln -s ../models/margpa-runtime-llm/models models
ls -ld models
```

Symlinkを作らない方が、Upload BundleとModel Storageの境界は明確である。Current推奨は、Symlinkなしで`MARGPA_MODEL_ROOT`または`--model-root`を明示する方式である。

## 8. `uv 0.11.29`を隔離配置する

Current Accepted Contractは`uv 0.11.29`である。Lightning既設の別Versionを置換せず、Project用Binaryを隔離する。

### 8.1 Install

```bash
mkdir -p "$MARGPA_UV_BIN"

curl -LsSf https://astral.sh/uv/0.11.29/install.sh \
  | env UV_UNMANAGED_INSTALL="$MARGPA_UV_BIN" sh
```

Official InstallerのVersion指定URLと`UV_UNMANAGED_INSTALL`を使用する。Installer Scriptを確認してから実行したい場合：

```bash
curl -LsSf https://astral.sh/uv/0.11.29/install.sh | less
```

参考：

- [uv公式Installation](https://docs.astral.sh/uv/getting-started/installation/)
- [uv公式Installer Options](https://docs.astral.sh/uv/reference/installer/)

### 8.2 PATHへ一時追加する

```bash
export PATH="$MARGPA_UV_BIN:$PATH"
command -v uv
uv --version
```

期待値：

```text
uv 0.11.29 (x86_64-unknown-linux-gnu)
```

### 8.3 Accepted Binary Hashを確認する

前回のLightning導入で確認した`uv 0.11.29` Linux x86_64 BinaryのSHA-512：

```text
957e3ee915fef24101de24a8414c4a9f60e3bd25f0e127eb89a12a78e6bbb6f79621dcb5e10dc41e31834f77a6d7180bebcdfc7ccb08901eba059cde627e8d48
```

確認：

```bash
printf '%s  %s\n' \
  '957e3ee915fef24101de24a8414c4a9f60e3bd25f0e127eb89a12a78e6bbb6f79621dcb5e10dc41e31834f77a6d7180bebcdfc7ccb08901eba059cde627e8d48' \
  "$MARGPA_UV_BIN/uv" \
  | sha512sum --check -
```

`OK`以外の場合は先へ進まず、取得元、Version、Architectureを確認する。

## 9. PythonとEnvironment Mode

### 9.1 Accepted Target

```text
Python : CPython 3.12.11
uv     : 0.11.29
OS     : Ubuntu
Arch   : x86_64
Mode   : Container
```

確認：

```bash
python3 --version
python --version
printf 'VIRTUAL_ENV=%s\n' "${VIRTUAL_ENV:-<unset>}"
printf 'CONDA_PREFIX=%s\n' "${CONDA_PREFIX:-<unset>}"
```

PreflightはPythonを厳密に`3.12.11`と照合する。異なる場合、無断でProfile Contractを緩めず、Studio Image／Environment選択または別Follow-up設計で解消する。

### 9.2 `auto`

`--environment-mode auto`は次で解決する。

```text
VIRTUAL_ENVまたはCONDA_PREFIXあり : studio-active
どちらもなし                      : project-venv
```

Current Lightningでは、Studio Active EnvironmentがPython 3.12.11を提供している場合、`auto`でよい。

### 9.3 Studio Active Environment

```text
長所 : 既存Python 3.12.11を使い、準備が短い
注意 : Active PrefixへProject Dependencyを同期する
```

### 9.4 Project `.venv`

```text
長所 : Project固有Environmentとして分離できる
注意 : Preflight時にPATH上のpython3が3.12.11である必要がある
```

明示例：

```bash
bash scripts/setup/preflight_lightning_ai_studio.sh \
  --runtime-target cpu-native \
  --environment-mode project-venv

bash scripts/setup/setup_lightning_linux_x86_64_cpu.sh \
  --environment-mode project-venv \
  --venv "$MARGPA_PROJECT_ROOT/.venv" \
  --model-root "$MARGPA_MODEL_ROOT"
```

Current主手順では、前回実績に合わせ`auto`を使用する。

## 10. Read-only Preflight

### 10.1 Project Rootへ移動する

```bash
cd "$MARGPA_PROJECT_ROOT"
```

### 10.2 Help

```bash
bash scripts/setup/preflight_lightning_ai_studio.sh --help
```

### 10.3 Pure CPU Preflight

```bash
env PATH="$MARGPA_UV_BIN:$PATH" \
  MARGPA_MODEL_ROOT="$MARGPA_MODEL_ROOT" \
  bash scripts/setup/preflight_lightning_ai_studio.sh \
  --runtime-target cpu-native \
  --environment-mode auto

export MARGPA_PREFLIGHT_EXIT="$?"
printf 'PURE_CPU_PREFLIGHT_EXIT=%s\n' "$MARGPA_PREFLIGHT_EXIT"
```

期待値：

```text
Phase 1-F Lightning preflight passed.
Runtime target   : cpu-native
Python           : ... (3.12.11)
uv               : ... (0.11.29)
Pure CPU Profile : parseable
GPU required     : no
nvcc available   : not_probed
Model Root       : ... (present)
PURE_CPU_PREFLIGHT_EXIT=0
```

Pure CPU Preflightは`nvidia-smi`、`nvcc`、CUDA Compiler、GPU Allocationを要求しない。

## 11. Setup Plan

Environmentを変更する前に、Read-only Planを確認する。

```bash
env PATH="$MARGPA_UV_BIN:$PATH" \
  bash scripts/setup/setup_lightning_linux_x86_64_cpu.sh \
  --plan \
  --model-root "$MARGPA_MODEL_ROOT"
```

Model Smokeを含むPlan：

```bash
env PATH="$MARGPA_UV_BIN:$PATH" \
  bash scripts/setup/setup_lightning_linux_x86_64_cpu.sh \
  --plan \
  --model-smoke \
  --model-root "$MARGPA_MODEL_ROOT"
```

確認点：

- Model Rootが意図したRootである。
- Resolved ArtifactがQwen3-4Bの期待Pathである。
- Pure CPU Buildである。
- ModelをDownloadしない。
- `--plan`でEnvironmentを変更しない。

## 12. Environment再構築

### 12.1 通常Setup

```bash
env PATH="$MARGPA_UV_BIN:$PATH" \
  bash scripts/setup/setup_lightning_linux_x86_64_cpu.sh \
  --environment-mode auto \
  --model-root "$MARGPA_MODEL_ROOT"
```

通常Setupは、既存BackendがPure CPUとして確認済みならReuseする。未確認、Accelerator Buildまたは未導入の場合は、Pure CPU Source Buildを行う。

Native Build設定：

```text
llama-cpp-python : 0.3.34
GGML_CUDA        : off
GGML_METAL       : off
GGML_HIP         : off
Parallel Level   : 4（既定）
```

### 12.2 明示的なNative Rebuild

通常Setup後もBackend整合に疑いがある場合、またはNative Buildを意図的に作り直す場合だけ使用する。

```bash
env PATH="$MARGPA_UV_BIN:$PATH" \
  bash scripts/setup/setup_lightning_linux_x86_64_cpu.sh \
  --environment-mode auto \
  --rebuild-native \
  --model-root "$MARGPA_MODEL_ROOT"
```

`--rebuild-native`は毎回Source Buildを行うため重い。通常同期と明示的Native Rebuildを分離する。

### 12.3 実際に使用したEnvironment Prefixを解決する

```bash
if [[ -n "${VIRTUAL_ENV:-}" ]]; then
  export MARGPA_ENV_PREFIX="$VIRTUAL_ENV"
elif [[ -n "${CONDA_PREFIX:-}" ]]; then
  export MARGPA_ENV_PREFIX="$CONDA_PREFIX"
else
  export MARGPA_ENV_PREFIX="$MARGPA_PROJECT_ROOT/.venv"
fi

test -x "$MARGPA_ENV_PREFIX/bin/python"
test -x "$MARGPA_ENV_PREFIX/bin/margpa-llm"
test -x "$MARGPA_ENV_PREFIX/bin/margpa-web"

printf 'MARGPA_ENV_PREFIX=%s\n' "$MARGPA_ENV_PREFIX"
```

## 13. Environment Verification

```bash
cd "$MARGPA_PROJECT_ROOT"

"$MARGPA_ENV_PREFIX/bin/python" \
  scripts/setup/verify_phase1_environment.py \
  --target lightning-cpu-native

export MARGPA_VERIFY_EXIT="$?"
printf 'PURE_CPU_VERIFY_EXIT=%s\n' "$MARGPA_VERIFY_EXIT"
```

期待値：

```text
PURE_CPU_VERIFY_EXIT=0
Python Version         : 3.12.11
Backend Build Variant : cpu
GPU Offload Supported : false
Device Kind           : cpu
Acceleration API      : none
nvidia-smi            : not_required_not_probed
nvcc                  : not_required_not_probed
```

Raw JSONにはEnvironment Pathが含まれ得る。外部公開する前にPath、Username、Workspace情報を確認・匿名化する。

## 14. Repository Test

ModelをLoadしない通常Test：

```bash
"$MARGPA_ENV_PREFIX/bin/pytest" -q
```

任意のStatic Check：

```bash
"$MARGPA_ENV_PREFIX/bin/ruff" check .
"$MARGPA_ENV_PREFIX/bin/ruff" format --check .
"$MARGPA_ENV_PREFIX/bin/mypy"
```

Current Pure CPU External Native Gateでは、通常Testだけで完了としない。次のBounded Native Smokeが必要である。

## 15. Bounded Native Smoke

### 15.1 Setup Script経由

```bash
env PATH="$MARGPA_UV_BIN:$PATH" \
  bash scripts/setup/setup_lightning_linux_x86_64_cpu.sh \
  --environment-mode auto \
  --model-smoke \
  --model-root "$MARGPA_MODEL_ROOT"
```

### 15.2 Acceptance Scriptを直接実行

Setupが完了済みで、再同期せずProbeだけを行う場合：

```bash
"$MARGPA_ENV_PREFIX/bin/python" \
  scripts/models/phase1f_cross_environment_acceptance.py \
  --profile config/profiles/lightning_linux_x86_64_cpu_native.toml \
  --model-root "$MARGPA_MODEL_ROOT"
```

Probeは次をBoundedに確認する。

- Model File SHA-512一致
- Pure CPU Runtime Evidence
- Japanese Policy
- English Policy
- Non-stream Generation
- Streaming
- Cooperative Cancel
- Cancel後の再生成
- Thinking Protocol
- Hidden／Visible Thinking分離
- Unload
- Load時間
- RSS Memory

合格条件：

```json
{
  "success": true,
  "all_required_checks_passed": true
}
```

`required_checks`の全項目が`true`であることも確認する。

Pure CPUではThinking Probeが長くなる可能性がある。GPUを要求しない代わりに、完了まで十分な時間を確保する。

Acceptance Reportには実Model PathやRuntime情報が含まれる。公開前に識別情報を匿名化する。

## 16. Model情報の確認

```bash
"$MARGPA_ENV_PREFIX/bin/margpa-llm" model-info \
  --profile config/profiles/lightning_linux_x86_64_cpu_native.toml \
  --model-root "$MARGPA_MODEL_ROOT"
```

最低限の期待値：

```text
profile_key           : external.lightning-linux-x86_64.cpu-native
device                : cpu
device_kind           : cpu
acceleration_api      : none
gpu_offload           : false
backend_build_variant : cpu
artifact_verified     : true
```

`cuda`、`metal`、`cpu_native`等がPure CPU Profileの実Runtimeとして現れる場合は、Profile／Backend不一致として停止する。

## 17. Web Previewを起動する

### 17.1 Local Portだけで起動する

```bash
"$MARGPA_ENV_PREFIX/bin/margpa-web" \
  --host 127.0.0.1 \
  --port 8000 \
  --profile config/profiles/lightning_linux_x86_64_cpu_native.toml \
  --model-root "$MARGPA_MODEL_ROOT"
```

### 17.2 Lightning PortへBindする

非Loopback BindではPreview用Basic認証が必須である。

```bash
export MARGPA_WEB_AUTH_MODE=basic
export MARGPA_WEB_AUTH_USERNAME='<preview-user>'
export MARGPA_WEB_AUTH_PASSWORD='<long-random-preview-password>'
```

CredentialをGit、Docs、Config、Screenshot、共有Logへ残さない。

起動：

```bash
"$MARGPA_ENV_PREFIX/bin/margpa-web" \
  --host 0.0.0.0 \
  --port 8000 \
  --profile config/profiles/lightning_linux_x86_64_cpu_native.toml \
  --model-root "$MARGPA_MODEL_ROOT"
```

### 17.3 Health Check

別Terminal：

```bash
curl -i http://127.0.0.1:8000/healthz
```

期待値：

```text
HTTP/1.1 200 OK
{"status":"ok"}
```

Web RootはCredentialなしで`401 Unauthorized`を期待する。

```bash
curl -i http://127.0.0.1:8000/
```

Account外からのPort公開方法、Basic認証境界およびUI操作は、既存Web Manualを参照する。

## 18. Pure CPUでの手動Web Smoke

初回は負荷を抑える。

```text
回答言語         : ja
最大生成Token数 : 128～256
推論生成         : OFF
推論過程表示     : OFF
要約モード       : OFF
```

確認順：

1. 短い日本語回答
2. 短い英語回答
3. Streaming
4. 停止
5. 停止後の再送信
6. 新規Chat
7. Browser Reload
8. Model Busy
9. 必要時だけThinking
10. 必要時だけSummary

Pure CPUで一度にThinking、Summary、長い`max_new_tokens`を有効にすると、無料枠、処理時間、Memory消費が増える。機能不良と性能制約を分離して確認する。

## 19. 失敗時の切り分け

### 19.1 `expected uv 0.11.29`

原因：

- Lightning既設の別VersionがPATH先頭
- Project用Binaryの配置不足

確認：

```bash
command -v uv
uv --version
printf '%s\n' "$PATH"
```

対処：

```bash
export PATH="$MARGPA_UV_BIN:$PATH"
```

### 19.2 `expected Python 3.12.11`

原因：

- 別Studio Image
- Active Environmentの違い
- `.python-version`等による意図しない選択

確認：

```bash
python3 --version
python --version
printf 'VIRTUAL_ENV=%s\n' "${VIRTUAL_ENV:-<unset>}"
printf 'CONDA_PREFIX=%s\n' "${CONDA_PREFIX:-<unset>}"
```

Contractを無断変更せず、3.12.11 Environmentへ戻す。

### 19.3 Modelが見つからない

確認：

```bash
printf 'MARGPA_MODEL_ROOT=%s\n' "$MARGPA_MODEL_ROOT"
ls -l "$MARGPA_MODEL_ROOT/main/qwen3-4b/gguf/Qwen3-4B-Q4_K_M.gguf"
```

Registry Relative Layoutを変更しない。

### 19.4 Model Hash不一致

期待SHA-512：

```text
f182f1d40606572d6965e50e0ef33c4be64b43ad65339710ceebb664e3d43e76398a4ef230c7a3dd8fbd643acbce8f0c7cbec28784203ccf26da0fe7e08bfceb
```

確認：

```bash
sha512sum "$MARGPA_MODEL_ROOT/main/qwen3-4b/gguf/Qwen3-4B-Q4_K_M.gguf"
```

不一致時はModelをLoadしない。破損、別Quantization、別File、Upload未完了を確認する。

### 19.5 Pure CPU VerificationでCUDA／GPUが検出される

原因候補：

- 旧CUDA BuildのReuse
- 別Environmentを実行
- `cpu_native`ではなく旧CPU Profileを選択

対処候補：

```bash
env PATH="$MARGPA_UV_BIN:$PATH" \
  bash scripts/setup/setup_lightning_linux_x86_64_cpu.sh \
  --environment-mode auto \
  --rebuild-native \
  --model-root "$MARGPA_MODEL_ROOT"
```

Rebuild後に`verify_phase1_environment.py --target lightning-cpu-native`を再実行する。

### 19.6 Webが外部から開けない

確認：

- `--host 0.0.0.0`
- Port `8000`
- Lightning Port公開設定
- Studio ProcessがRunning
- Basic認証Environment Variable
- CredentialなしRootが401
- `/healthz`が200

### 19.7 `docs/`がない

Current Phase 1 Pure CPU Runtimeには影響しない。

将来Simple RAGを有効化する場合、`docs/`不在時はCrashや空回答ではなく、次の制御結果を返す設計予約である。

```text
docsが設置されていないため参照出来ません。
```

Current Lightning BundleではSimple RAGを有効化しない。

## 20. 一括実行用Check List

### Mac

```text
[ ] 開発元Project Root確認
[ ] Upload専用Staging作成
[ ] .venv除外
[ ] models Symlink／GGUF除外
[ ] docs除外
[ ] .python-version除外
[ ] Cache／Native Build Artifact除外
[ ] .env／Log／Zip除外
[ ] 必須Artifact存在確認
[ ] Symlinkなし確認
[ ] 公開禁止識別情報なし確認
[ ] 必要時Manifest作成
```

### Lightning配置

```text
[ ] Project Root配置
[ ] Model Root分離配置
[ ] Qwen3 GGUF Expected Layout
[ ] uv 0.11.29隔離配置
[ ] uv SHA-512確認
[ ] Python 3.12.11確認
```

### Read-only

```text
[ ] Pure CPU Preflight Exit 0
[ ] Runtime Target cpu-native
[ ] GPU required no
[ ] nvcc not_probed
[ ] Setup Plan確認
[ ] Resolved Artifact確認
```

### Reconstruction

```text
[ ] Frozen Dependency同期
[ ] Pure CPU Native BuildまたはVerified Reuse
[ ] Environment Verification Exit 0
[ ] Backend Build Variant cpu
[ ] GPU Offload false
[ ] Acceleration API none
```

### Acceptance

```text
[ ] Repository Test
[ ] Bounded Native Smoke
[ ] success true
[ ] all_required_checks_passed true
[ ] Model Hash一致
[ ] Japanese／English
[ ] Streaming
[ ] Cancel
[ ] Cancel後再生成
[ ] Thinking Protocol
[ ] Unload
[ ] Memory／Latency記録
```

### Web

```text
[ ] Pure CPU Profileで起動
[ ] healthz 200
[ ] CredentialなしRoot 401
[ ] 短い日本語生成
[ ] 停止
[ ] 新規Chat
[ ] Shutdown
```

## 21. 完了条件

次を全て満たすまで、Phase 1-F External Native AcceptanceをCompleteとしない。

1. Lightning Pure CPU PreflightがExit 0
2. Python 3.12.11／uv 0.11.29一致
3. Pure CPU Native BuildまたはVerified Reuse
4. Environment VerificationがExit 0
5. Model SHA-512一致
6. Bounded Native Smokeの全Required CheckがTrue
7. Runtimeが`device_kind=cpu`
8. Runtimeが`acceleration_api=none`
9. Runtimeが`gpu_offload=false`
10. Web Previewの起動、Health、短い生成、停止、Shutdown確認
11. 結果をStatusとして記録
12. 設計者役のExternal Native Review

本Manualの作成だけではExternal Native Acceptanceを完了扱いにしない。

## 22. Current Decision

```text
Upload Bundle            : Clean Staging Copy
Project .venv Upload     : Prohibited
Model in Project Bundle  : Prohibited
Model Root               : Sibling External Storage
Project docs Upload      : Not Required／Excluded
Python                   : 3.12.11
uv                       : 0.11.29／Isolated
Backend                  : llama-cpp-python 0.3.34／Pure CPU
Preflight Target         : cpu-native
Profile                  : lightning_linux_x86_64_cpu_native.toml
Environment Mode         : auto
GPU Probe                : Not Required
External Operations      : User-run Gate
```
