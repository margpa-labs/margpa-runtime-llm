# Phase 1 User Manual Lossless Compilation
```yaml
document_id: phase_1_user_manual_lossless_compilation
phase: phase_1
status: frozen
language: ja
created_at: 2026-07-26 15:16:24 JST
frozen_at: 2026-07-26 15:16:24 JST
source_documents: 7
source_manifest: ../../phase_1_ex/operations/source_to_target_documentation_migration_manifest.json
source_hash_algorithm: sha512
supersedes: null
rag_default: true
```

## Compilation Policy

本書はPhase 1中に作成されたSource文書を、省略、要約、意味変更または再解釈せず、Source Path順に再配置したLossless Compilationである。

本文は原文を維持し、Directory Migration後も参照可能にするため、MarkdownのLocal Link Pathだけを機械的に正規化している。原文File、原文SHA-512および移動先はSource Manifestから一意に解決できる。

矛盾、旧判断、未解決事項および後継文書への置換前状態も削除していない。Currentな判断はCurrent Canonical文書とPhase Indexを参照する。

## Source Documents

<!-- SOURCE_BEGIN 1: docs/user_manual/lightning_cpu_upload_and_environment_reconstruction_manual_20260725215627.md -->

### Source 1: `docs/user_manual/lightning_cpu_upload_and_environment_reconstruction_manual_20260725215627.md`

- History Target: `docs/project/phases/phase_1/history/user_manual/lightning_cpu_upload_and_environment_reconstruction_manual_20260725215627.md`
- Source SHA-512: `e231fafce860bebe0da49ef4d4a6066dfca9d959ef65a2a2ea7bc04b2a8374dbd1e7a2accdff2656b7816a821eb0fdb783b32ca37e837d00c73788bddd309682`
- Source Size: `28747` bytes

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
- Documentation Index: [documentation_index_20260725215627.md](../history/documentation_index_20260725215627.md)
- Accepted Repository Review: [designer_review_phase_1f_pure_cpu_acceptance_correction_20260725214428.md](../history/handoffs/designer_review_phase_1f_pure_cpu_acceptance_correction_20260725214428.md)
- 既存Web Manual: [phase_1_web_and_lightning_user_manual_20260721185031.md](../history/user_manual/phase_1_web_and_lightning_user_manual_20260721185031.md)
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

<!-- SOURCE_END 1: docs/user_manual/lightning_cpu_upload_and_environment_reconstruction_manual_20260725215627.md -->

---

<!-- SOURCE_BEGIN 2: docs/user_manual/lightning_pure_cpu_actual_environment_reconstruction_manual_20260726092413.md -->

### Source 2: `docs/user_manual/lightning_pure_cpu_actual_environment_reconstruction_manual_20260726092413.md`

- History Target: `docs/project/phases/phase_1/history/user_manual/lightning_pure_cpu_actual_environment_reconstruction_manual_20260726092413.md`
- Source SHA-512: `9f701e7e492982dfd1a5b568102b7aa5f5299f42dfb510a3baf5f1935940cb5c9d21de5748d85e915a4c33fd67303f3f5462abc110a3622037e84d566759a09a`
- Source Size: `20466` bytes

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
- Documentation Index: [documentation_index_20260726092413.md](../history/documentation_index_20260726092413.md)
- External Runtime Review: [designer_review_phase_1f_lightning_external_pure_cpu_runtime_20260726092413.md](../history/handoffs/designer_review_phase_1f_lightning_external_pure_cpu_runtime_20260726092413.md)
- Test-only Follow-up: [designer_handoff_phase_1f_lightning_test_isolation_follow_up_20260726092413.md](../history/handoffs/designer_handoff_phase_1f_lightning_test_isolation_follow_up_20260726092413.md)
- Previous Planned Manual: [lightning_cpu_upload_and_environment_reconstruction_manual_20260725215627.md](../history/user_manual/lightning_cpu_upload_and_environment_reconstruction_manual_20260725215627.md)
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

<!-- SOURCE_END 2: docs/user_manual/lightning_pure_cpu_actual_environment_reconstruction_manual_20260726092413.md -->

---

<!-- SOURCE_BEGIN 3: docs/user_manual/phase_1_macos_user_manual_20260719004209.md -->

### Source 3: `docs/user_manual/phase_1_macos_user_manual_20260719004209.md`

- History Target: `docs/project/phases/phase_1/history/user_manual/phase_1_macos_user_manual_20260719004209.md`
- Source SHA-512: `7f75083c1348034b4a5e38f1b9798bcc262cfb4e8cb44888984e1909a8881556656e19df4706099b2f98a4b874f52f52ebebf4fbf183563aa334ef3418e10aed`
- Source Size: `8375` bytes

# Phase 1 macOS ユーザーマニュアル

- 文書ID: `phase_1_macos_user_manual`
- 状態: `current`
- 作成日時: `2026-07-19 00:42:09 JST`
- 更新日時: `2026-07-19 00:42:09 JST`
- 対象: MARGPA Runtime LLM Phase 1-A／Phase 1-B
- 対象ユーザー: Local Mac環境でPhase 1を操作・確認するユーザー
- 正本言語: 日本語
- Documentation Index: [documentation_index_20260719004209.md](../history/documentation_index_20260719004209.md)
- Phase 1 Final Review: [designer_review_phase_1b_model_runtime_final_20260719001604.md](../history/handoffs/designer_review_phase_1b_model_runtime_final_20260719001604.md)
- supersedes: なし（新規User Manual系列）

## 1. このManualの目的

このManualは、現在のMacでMARGPA Runtime LLM Phase 1をユーザー自身が操作し、次を確認するための手順である。

- Model Runtime情報
- Qwen3-4Bによる一問一答
- Streaming表示
- Non-streaming表示
- Thinking Mode
- Ctrl+C Cooperative Cancel
- Default Test
- Qwen3実Model／Metal Test

Phase 1はCLIによる一問一答Runtimeである。GPT風Web UI、複数Turn会話、履歴保存、Runtime Governance本実装は後続Phaseで追加する。

## 2. 確認済み環境

```text
Project Name     : margpa-runtime-llm
Display Name     : MARGPA Runtime LLM
Internal Name    : Nazuna Research Governance LLM
OS               : macOS
Architecture     : Apple Silicon／arm64
Hardware         : MacBook Pro／Apple M2 Pro／16GB
Python           : CPython 3.13.14
Backend          : llama-cpp-python 0.3.34
Acceleration     : Metal／GPU Offload
Main Model       : Qwen3-4B Q4_K_M／GGUF
Loaded Context   : 4,096 tokens
Thinking Default : OFF
```

ユーザーは`2026-07-19 JST`に、本Manualへ記載した主要操作がすべて成功することを確認済みである。

## 3. 前提

次が準備済みであることを前提とする。

- Project Rootに`.venv/`がある
- `.venv`へPhase 1 Dependencyが導入済みである
- `models/`がLocal Model Rootを参照している
- 次のModel Artifactが存在する

```text
models/main/qwen3-4b/gguf/Qwen3-4B-Q4_K_M.gguf
```

Model FileをProject内へ複製、改名または自動Downloadしない。

## 4. Project Rootへ移動する

macOSのTerminalを開き、次を実行する。

```bash
cd /path/to/margpa-runtime-llm
```

以降のCommandはProject Rootで実行する。

## 5. Model Runtime情報を確認する

```bash
./.venv/bin/margpa-llm model-info
```

成功時はJSONが表示される。

主な確認項目：

```text
runtime.model_key                   : main.qwen3-4b-q4-k-m
runtime.backend_key                 : llama_cpp
runtime.backend_version             : 0.3.34
runtime.model_architecture          : qwen3
runtime.quantization                : Q4_K_M
runtime.artifact_digest.algorithm   : sha512
runtime.artifact_digest_verified    : true
runtime.loaded_context_size         : 4096
runtime.device                      : metal
runtime.gpu_offload                 : true
effective_config.thinking_mode      : disabled
```

`load_instance_id`はModel Loadごとに変化するため、固定値との一致を確認しない。

## 6. 通常のStreaming生成を確認する

```bash
./.venv/bin/margpa-llm generate \
  --prompt "こんにちは。あなたの役割を日本語で短く説明してください。" \
  --max-new-tokens 128
```

成功時は、回答が少しずつTerminalへ表示される。

回答内容は生成ごとに変化し得る。完全一致ではなく、次を確認する。

- 日本語回答が生成される
- Streamingで文字が順次表示される
- Native ErrorやTracebackが表示されない
- Generation終了後にTerminal Promptへ戻る

## 7. Non-streaming生成を確認する

```bash
./.venv/bin/margpa-llm generate \
  --prompt "Runtime Governanceとは何か短く説明してください。" \
  --max-new-tokens 128 \
  --no-stream
```

成功時は、Generation完了後に回答全体がまとめて表示される。

## 8. Thinking Modeを確認する

```bash
./.venv/bin/margpa-llm generate \
  --prompt "小型LLMを交換可能にする設計を考えてください。" \
  --max-new-tokens 256 \
  --thinking
```

成功時はThinking有効設定でGenerationが完了する。

注意：

- Thinking有効化は回答品質を保証するものではない
- 小型Modelのため、回答品質には限界がある
- 生の内部推論をAudit Logへ保存する機能ではない
- DefaultはThinking OFFである

## 9. Ctrl+C Cooperative Cancelを確認する

長めの回答を要求する。

```bash
./.venv/bin/margpa-llm generate \
  --prompt "1から10000まで、数字だけを順番に出力してください。途中で省略しないでください。" \
  --max-new-tokens 2048
```

Streaming中に、Keyboardの`Control`を押しながら`C`を押す。

成功時：

```text
Generation cancelled.
```

次を正常条件とする。

- `generation_failed`と表示されない
- Python Tracebackが表示されない
- Model Processを強制終了しなくてもTerminal Promptへ戻る
- CLI Process Exit Codeは`130`

Exit Codeを通常操作で見る必要はない。必要な場合は、Cancel直後に次を実行する。

```bash
echo $?
```

期待値：

```text
130
```

## 10. Default Testを実行する

実ModelをLoadしない高速Test：

```bash
./.venv/bin/pytest -q
```

本Manual作成時点の期待値：

```text
47 passed, 2 deselected
```

Test追加により件数は将来増加し得る。重要なのは`failed`または`error`が0件であること。

## 11. 実Model／Metal Testを実行する

```bash
./.venv/bin/pytest -q -m model_smoke
```

本Manual作成時点の期待値：

```text
2 passed, 47 deselected
```

このTestはQwen3-4Bを実際にLoadし、Metal／GPU Offload、Generation、Streaming、CancelおよびUnloadを確認する。

Default Testより時間とMemoryを使用する。

## 12. 通常動作として扱うもの

### 12.1 回答開始まで数秒かかる

現在のPhase 1 CLIは、Command実行ごとに次を行う。

1. Model ArtifactのSize確認
2. SHA-512全体検証
3. Qwen3-4BのLoad
4. Generation
5. Model Unload

そのため、回答表示まで数秒待つことがある。異常ではない。

### 12.2 回答内容が毎回同じではない

Generation設定とSeedにより、同じ質問でも回答が変化し得る。

### 12.3 一問一答で終了する

Phase 1 CLIは会話履歴を保持しない。新しいCommandは新しい一問一答として実行される。

## 13. 主なErrorと確認箇所

### `model_not_found`

確認するもの：

```bash
ls -l models
ls -l models/main/qwen3-4b/gguf/Qwen3-4B-Q4_K_M.gguf
```

Model Rootを明示する場合：

```bash
MARGPA_MODEL_ROOT=/path/to/margpa-models \
  ./.venv/bin/margpa-llm model-info
```

### `model_integrity_mismatch`

Model FileのSizeまたはSHA-512がRegistryと一致していない。

Model File、RegistryまたはHashを推測で変更しない。実装担当／設計担当へ報告する。

### `backend_unavailable`または`model_load_failed`

Backend Version、Metal BuildまたはEnvironmentが一致していない可能性がある。

確認Command：

```bash
./.venv/bin/python scripts/setup/verify_phase1_environment.py
```

### `context_limit_exceeded`

Formatted Promptと`max_new_tokens`の合計がLoaded Context 4,096を超えている。

Messageを無断削除または要約せず、Promptを短くするか`--max-new-tokens`を明示的に下げる。

## 14. Phase 1でまだ利用できない機能

- GPT風Web UI
- 複数Turn会話
- Chat履歴保存／再開
- Runtime Governance本実装
- ARGD／DAGD実行
- Audit Log本実装
- Guard Model
- LLM-as-a-Judge
- RAG
- Agent／Tool実行
- Windows実行Profile
- Cloud Runtime

これらは後続Phaseまたは将来拡張で追加する。

## 15. Phase 1成功判定

最低限、次が成功すればユーザー動作確認は完了とする。

```text
model-info                  : Pass
Streaming Generation       : Pass
Non-streaming Generation   : Pass
Thinking Generation        : Pass
Ctrl+C Cancel              : Pass
Default Test               : Pass
実Model／Metal Test         : Pass
```

ユーザーは本Manual作成前に、上記すべての成功を確認済みである。

<!-- SOURCE_END 3: docs/user_manual/phase_1_macos_user_manual_20260719004209.md -->

---

<!-- SOURCE_BEGIN 4: docs/user_manual/phase_1_macos_user_manual_20260719171836.md -->

### Source 4: `docs/user_manual/phase_1_macos_user_manual_20260719171836.md`

- History Target: `docs/project/phases/phase_1/history/user_manual/phase_1_macos_user_manual_20260719171836.md`
- Source SHA-512: `23663a429194b9f3f768d9c24362b794da05b38a339653c9d2f07cd1cebfd37f141e0b5931ad1810df6ee39202e8cc65d9fd7cb93fca83282354d4f21a928da1`
- Source Size: `17698` bytes

# Phase 1 macOS ユーザーマニュアル

- 文書ID: `phase_1_macos_user_manual`
- 状態: `current_user_acceptance_candidate`
- 作成日時: `2026-07-19 17:18:36 JST`
- 更新日時: `2026-07-19 17:18:36 JST`
- Snapshot: `20260719171836`
- 対象: MARGPA Runtime LLM Phase 1-A～Phase 1-E
- 対象ユーザー: Local Mac環境でPhase 1を操作・受入確認するユーザー
- 正本言語: 日本語
- Documentation Index: [documentation_index_20260719171836.md](../history/documentation_index_20260719171836.md)
- Phase 1 Readiness Review: [designer_review_phase_1_final_readiness_20260719171836.md](../history/handoffs/designer_review_phase_1_final_readiness_20260719171836.md)
- Phase 1-E Final Review: [designer_review_phase_1e_final_20260719164641.md](../history/handoffs/designer_review_phase_1e_final_20260719164641.md)
- Backup Policy: [phase_completion_backup_policy_20260719171836.md](../history/operations/phase_completion_backup_policy_20260719171836.md)
- supersedes: `phase_1_macos_user_manual_20260719004209.md`

## 1. このManualの目的

このManualは、現在のMacでMARGPA Runtime LLM Phase 1全体をユーザー自身が操作し、User Acceptance Testを行うための手順である。

対象：

```text
Phase 1-A : Python／uv／Metal Environment
Phase 1-B : Model Adapter／CLI Generation
Phase 1-C : Deployment／Platform／Acceleration Hook
Phase 1-D : Configuration Layer／Response Language
Phase 1-E : Thinking Execution／Parsing／Presentation
```

確認する主な機能：

- EnvironmentとDependency
- Model Runtime情報
- Qwen3-4B GGUF／Metal Load
- Streaming／Non-streaming
- Ctrl+C Cooperative Cancel
- `ja／en／auto`
- Thinking Executionと表示の独立
- Thinking非表示／Default Label／Custom Label
- Config SourceとSchema
- Default Test／Native Metal Test

Phase 1はCLIによる一問一答Runtimeである。GPT風Web UI、複数Turn会話、履歴保存、Runtime Governance本実装は後続Phaseで追加する。

## 2. 確認済み環境

```text
Project Name       : margpa-runtime-llm
Display Name       : MARGPA Runtime LLM
Internal Name      : Nazuna Research Governance LLM
OS                 : macOS
Architecture       : Apple Silicon／arm64
Hardware           : MacBook Pro／Apple M2 Pro／16GB
Python             : CPython 3.13.14
Backend            : llama-cpp-python 0.3.34
Acceleration       : Metal／GPU Offload
Main Model         : Qwen3-4B Q4_K_M／GGUF
Loaded Context     : 4,096 tokens
Application Schema : 2
Model Schema       : 2
Deployment Schema  : 3
Response Default   : ja
Thinking Default   : disabled
Visibility Default : hidden
Display Label      : 高度推論
Persistence        : disabled
```

この環境は設計者役の独立ReviewでStatic、Default Test、Native Metal Testまで確認済みである。ユーザー受入テストは、本Manualに従って別途実行する。

## 3. Platform境界

Native Verified：

```text
macOS／Apple Silicon arm64／Metal
```

Phase 1-CではWindows、Linux、CPU、CUDA、ROCm等を追加できるProfile／Registry／Validation Hookを用意したが、次はまだ主張しない。

- Windows Native Verified
- Linux Native Verified
- CUDA Runtime Verified
- ROCm Runtime Verified
- Intel Mac Verified
- Cross-platform Installer完成

未検証Platformで動く可能性と、動作確認済みであることを混同しない。

## 4. 前提

次が準備済みであることを前提とする。

- Project Rootに`.venv/`がある
- Phase 1 Dependencyが導入済みである
- `models/`がLocal Model Rootを参照するPOSIX Symbolic Linkである
- 次のModel Artifactが存在する

```text
models/main/qwen3-4b/gguf/Qwen3-4B-Q4_K_M.gguf
```

Model FileをProject内へ複製、改名または自動Downloadしない。

## 5. Project Rootへ移動する

macOSのTerminalを開き、次を実行する。

```bash
cd /path/to/margpa-runtime-llm
```

以降のCommandはProject Rootで実行する。

## 6. CLI Helpを確認する

```bash
./.venv/bin/margpa-llm --help
./.venv/bin/margpa-llm generate --help
./.venv/bin/margpa-llm model-info --help
```

`generate`の主なOption：

```text
--response-language {ja,en,auto}
--no-stream
--thinking／--no-thinking
--show-thinking／--hide-thinking
--thinking-label
--max-new-tokens
--temperature／--top-p／--top-k
--seed／--stop
```

## 7. Environmentを確認する

```bash
./.venv/bin/python scripts/setup/verify_phase1_environment.py
```

主な合格条件：

```text
python.version                         : 3.13.14
python.implementation                  : CPython
python.machine                         : arm64
backend.gpu_offload_supported          : true
backend.metal_system_info_present      : true
validation.dependency_versions_match   : true
validation.out_of_scope_packages_absent: true
```

PathはLocal環境に応じて表示されるため、固定値との一致を要求しない。

## 8. Model Runtime情報を確認する

```bash
./.venv/bin/margpa-llm model-info
```

成功時はJSONが表示される。

主な確認項目：

```text
runtime.model_key                                      : main.qwen3-4b-q4-k-m
runtime.backend_key                                    : llama_cpp
runtime.backend_version                                : 0.3.34
runtime.model_architecture                             : qwen3
runtime.quantization                                   : Q4_K_M
runtime.artifact_digest.algorithm                      : sha512
runtime.artifact_digest_verified                       : true
runtime.loaded_context_size                            : 4096
runtime.device                                         : metal
runtime.gpu_offload                                    : true
effective_config.application_schema_version            : 2
effective_config.generation.thinking_mode              : disabled
effective_config.response.language                     : ja
effective_config.response.source                       : application
effective_config.presentation.thinking.visibility      : hidden
effective_config.presentation.thinking.display_label   : 高度推論
effective_config.presentation.thinking.persistence     : disabled
model_output_protocol.model_definition_schema_version  : 2
model_output_protocol.thinking.parser_key              : tagged_thinking_v1
```

`load_instance_id`はModel Loadごとに変化するため、固定値との一致を確認しない。

## 9. Configurationの責務を確認する

Phase 1の主なTracked Config：

```text
config/application.toml
  Common Model Selection
  Model Root Default
  Load Default
  Generation Default
  Response Language
  Thinking Presentation

config/models/qwen3_4b_q4_k_m.toml
  Model Identity
  Artifact／SHA-512
  Backend／Capability
  Canonical Output Protocol

config/profiles/local_macos_arm64.toml
  macOS／arm64／Metal Deployment
  Hardware-dependent Load Override

config/platforms/platform_registry.toml
  Platform Alias／Default Profile Resolution
```

通常のUser Acceptance TestではConfig Fileを編集しない。CLI Overrideを使う。

## 10. Default日本語Streaming生成

```bash
./.venv/bin/margpa-llm generate \
  --prompt "こんにちは。あなたの役割を日本語で短く説明してください。" \
  --max-new-tokens 128
```

合格条件：

- 日本語回答が生成される
- Streamingで文字が順次表示される
- Native ErrorやTracebackが表示されない
- Generation終了後にTerminal Promptへ戻る
- Canonical `<think>` Tagが表示されない

回答内容の完全一致は要求しない。

## 11. Response Languageを確認する

### 11.1 明示的な日本語

```bash
./.venv/bin/margpa-llm generate \
  --prompt "自己紹介してください。" \
  --response-language ja \
  --max-new-tokens 128
```

### 11.2 明示的な英語

```bash
./.venv/bin/margpa-llm generate \
  --prompt "Briefly introduce yourself." \
  --response-language en \
  --max-new-tokens 128
```

英語回答が生成されれば合格とする。

### 11.3 Auto

```bash
./.venv/bin/margpa-llm generate \
  --prompt "日本語でOKとだけ答えてください。" \
  --response-language auto \
  --max-new-tokens 32
```

`auto`は言語を自動判定するClassifierではなく、RuntimeからDefault Language Instructionを追加しないModeである。User Promptの明示指定にModelが従い、日本語で回答すれば合格とする。

## 12. Non-streaming生成

```bash
./.venv/bin/margpa-llm generate \
  --prompt "Runtime Governanceとは何か、日本語で短く説明してください。" \
  --max-new-tokens 128 \
  --no-stream
```

Generation完了後に回答全体がまとめて表示され、TracebackなしでTerminal Promptへ戻れば合格とする。

## 13. Thinking Execution／Presentation

Phase 1-Eでは次を分離する。

```text
Execution    : ModelにThinkingを実行させるか
Parsing      : Canonical Model OutputをReasoning／Finalへ分ける
Presentation : Reasoningを利用者へ表示するか
Persistence  : Raw Reasoningを永続保存するか
```

### 13.1 Thinking有効／表示なし

```bash
./.venv/bin/margpa-llm generate \
  --prompt "1+1を考えて、最後に答えだけを示してください。日本語で。" \
  --max-new-tokens 256 \
  --thinking \
  --hide-thinking
```

合格条件：

- Canonical `<think>`／`</think>`が表示されない
- Reasoning本文が表示されない
- ModelがClosing／Finalまで生成した場合、Final Answerが表示される
- Tracebackがない

Token上限までにClosingへ到達しない場合、Hidden表示が空になることがある。Reasoning漏洩がなければ、直ちにParser不良とは判定しない。`--max-new-tokens`を512程度へ増やして再確認できる。

### 13.2 Thinking有効／Default Label表示

```bash
./.venv/bin/margpa-llm generate \
  --prompt "1+1を考えて、最後に答えを示してください。日本語で。" \
  --max-new-tokens 512 \
  --thinking \
  --show-thinking
```

ReasoningがCanonical Protocolとして生成された場合：

```text
<高度推論>...</高度推論>
Final Answer
```

合格条件：

- 表示Tagが`高度推論`
- Canonical `<think>`／`</think>`が表示用Tagとして残らない
- Unclosed時も表示Containerが閉じる
- Tracebackがない

`高度推論`は表示Channelの名前であり、Reasoningの正しさや品質を保証しない。

### 13.3 Custom Label

```bash
./.venv/bin/margpa-llm generate \
  --prompt "小型LLMを交換可能にする設計を考えてください。日本語で。" \
  --max-new-tokens 512 \
  --thinking \
  --show-thinking \
  --thinking-label "思考過程"
```

Reasoningが生成された場合、`<思考過程>...</思考過程>`が使われれば合格とする。

### 13.4 ExecutionとVisibilityの独立

`--show-thinking`だけではThinking ExecutionをONにしない。

```bash
./.venv/bin/margpa-llm generate \
  --prompt "OKとだけ答えてください。" \
  --show-thinking \
  --max-new-tokens 32
```

Thinking SectionがなければFinalだけが表示される。これは正常である。

## 14. Generation Parameter Override

例：

```bash
./.venv/bin/margpa-llm generate \
  --prompt "短い雑談を日本語でしてください。" \
  --max-new-tokens 128 \
  --temperature 0.6 \
  --top-p 0.9 \
  --seed 2371
```

Thinking FlagはTemperature、Top-p等を暗黙変更しない。

## 15. Ctrl+C Cooperative Cancel

```bash
./.venv/bin/margpa-llm generate \
  --prompt "1から10000まで、数字だけを順番に出力してください。途中で省略しないでください。" \
  --max-new-tokens 2048
```

Streaming中に`Control + C`を押す。

成功時：

```text
Generation cancelled.
```

合格条件：

- `generation_failed`と表示されない
- Python Tracebackが表示されない
- Model Processを強制終了せずTerminal Promptへ戻る
- CLI Process Exit Codeが`130`

必要な場合はCancel直後に確認する。

```bash
echo $?
```

## 16. Default Test

実ModelをLoadしない高速Test：

```bash
./.venv/bin/pytest -q
```

Snapshot `20260719171836`の期待値：

```text
161 passed, 2 deselected
```

Test追加により件数は将来増加し得る。`failed`または`error`が0件であることを合格条件とする。

## 17. 実Model／Metal Test

```bash
./.venv/bin/pytest -q -m model_smoke
```

Snapshot `20260719171836`の期待値：

```text
2 passed, 161 deselected
```

このTestはQwen3-4Bを実際にLoadし、SHA-512、Metal／GPU Offload、Language、Thinking Presentation、Generation、Streaming、Cancel、Unloadを確認する。

Default Testより時間とMemoryを使用する。

## 18. 通常動作として扱うもの

### 18.1 回答開始まで数秒かかる

現在のCLIはCommand実行ごとにModel Artifact Size／SHA-512、Model Load、Generation、Unloadを行う。回答表示まで数秒待つことは異常ではない。

### 18.2 回答内容が毎回同じではない

確率的Generationのため、完全一致を要求しない。言語、表示境界、Error有無、構造で判定する。

### 18.3 一問一答で終了する

Phase 1 CLIは会話履歴を保持しない。新しいCommandは新しい一問一答である。

### 18.4 Thinkingが長くFinalへ到達しない

小型ModelとToken上限により、Closing Tag／Final Answerまで到達しない場合がある。Token上限を増やすかPromptを短くして再確認する。

## 19. 主なErrorと確認箇所

### `model_not_found`

```bash
ls -l models
ls -l models/main/qwen3-4b/gguf/Qwen3-4B-Q4_K_M.gguf
```

Model Rootを明示する場合：

```bash
MARGPA_MODEL_ROOT=/path/to/margpa-models \
  ./.venv/bin/margpa-llm model-info
```

### `model_integrity_mismatch`

Model FileのSizeまたはSHA-512がRegistryと一致しない。Model File、Registry、Hashを推測で変更せず、実装担当／設計担当へ報告する。

### `backend_unavailable`／`model_load_failed`

Backend Version、Metal Build、Environmentが一致していない可能性がある。Section 7のEnvironment Verificationを行う。

### `context_limit_exceeded`

Formatted Promptと`max_new_tokens`の合計がLoaded Context 4,096を超えている。Messageを無断削除せず、Promptまたは`max_new_tokens`を明示的に小さくする。

### `invalid_configuration`／`invalid_request`

Config、Environment、CLI Overrideの値がSchemaまたはValidationに合っていない。Raw値を推測修正せず、指定したOptionとEnvironment Variableを確認する。

## 20. Known Diagnostic Observation

異なるFieldへEnvironmentとCLIから同時に値を指定し、Environment側だけが不正な場合、Error Codeが`invalid_configuration`ではなく`invalid_request`となる組合せがある。

不正値は安全に拒否されるため、Phase 1の通常操作やSecurity Boundaryには影響しない。詳細は次を参照する。

- [known_issues_and_observations_20260719171836.md](../history/operations/known_issues_and_observations_20260719171836.md)

## 21. Phase 1で利用可能／未実装

### 利用可能

- Local Qwen3 GGUF／Metal推論
- Model Adapter／Raw Model Port
- Streaming／Non-streaming
- Cancel／Unload
- Generation Config
- `ja／en／auto`
- Thinking Execution
- Thinking Hidden／Visible／Custom Label
- Model／Application／Deployment／Platform Config分離
- Platform／Acceleration拡張Hook

### 未実装

- GPT風Web UI
- 複数Turn会話
- Chat履歴保存／再開
- Runtime Governance本実装
- ARGD／DAGD実行
- Audit Log本実装
- Guard Model
- LLM-as-a-Judge
- RAG
- Agent／Tool実行
- Windows／Linuxの実ProfileとNative Verification
- Cloud Runtime

## 22. User Acceptance Test Checklist

次を同じProject状態で実行する。

| # | 確認項目 | 合格条件 |
|---:|---|---|
| 1 | CLI Help | Errorなしで表示 |
| 2 | Environment Verification | Dependency／Metal Validation Pass |
| 3 | `model-info` | Schema／Model／Metal／Hash／Default Policy一致 |
| 4 | Default日本語Streaming | 日本語、Streaming、Tracebackなし |
| 5 | Explicit English | 英語回答 |
| 6 | Auto | Prompt指定に従う |
| 7 | Non-streaming | まとめて表示、Errorなし |
| 8 | Thinking Hidden | Reasoning／Canonical Tag漏洩なし |
| 9 | Thinking Visible Default | `高度推論` Label、Canonical Tagなし |
| 10 | Thinking Custom Label | Custom Label使用 |
| 11 | Ctrl+C Cancel | Cooperative Cancel、Tracebackなし |
| 12 | Default Pytest | Failed／Error 0 |
| 13 | Native Model／Metal Test | 2 Test Pass |

回答内容の完全一致ではなく、各Sectionの構造的な合格条件で判定する。

## 23. User Test Pass Declaration

全項目が合格した場合、ユーザーは設計者役へ次の趣旨を明示する。

```text
phase_1_macos_user_manual_20260719171836.mdの
Phase 1ユーザー受入テストは、全項目合格です。
```

一部未実施または失敗がある場合は、合格宣言を行わず、項目番号、Command、表示されたSafe Errorを共有する。Secret、Model Raw Reasoning、不要なAbsolute Pathは貼らなくてよい。

## 24. Backupとの関係

Phase 1 Backupは、次の両方が成立した後に実行可能となる。

1. ユーザーによる本Manualの受入テスト全項目合格宣言
2. 設計者役によるPhase 1完了・Phase 2移行可能宣言

本Manualの作成またはTest実行だけではBackupを開始しない。

両宣言後、Backup前に実装状態が変わった場合は、影響範囲に応じて再テストまたは再Reviewを行う。

<!-- SOURCE_END 4: docs/user_manual/phase_1_macos_user_manual_20260719171836.md -->

---

<!-- SOURCE_BEGIN 5: docs/user_manual/phase_1_user_acceptance_findings_20260719195134.md -->

### Source 5: `docs/user_manual/phase_1_user_acceptance_findings_20260719195134.md`

- History Target: `docs/project/phases/phase_1/history/user_manual/phase_1_user_acceptance_findings_20260719195134.md`
- Source SHA-512: `dfff21606cf12e5e1fa86feb7494ebc771711df020794d8700b7c3aa695cafebbdfbc8e9191c402cc1ef1f630619d3d3d067ab77dd4f255c869b47175589926c`
- Source Size: `4983` bytes

# Phase 1 ユーザー受入テスト補足

- 文書ID: `phase_1_user_acceptance_findings`
- 状態: `current_supplement`
- 作成日時: `2026-07-19 19:51:34 JST`
- 更新日時: `2026-07-19 19:51:34 JST`
- Snapshot: `20260719195134`
- 作成担当: 設計者役担当Task
- 対象: Phase 1 macOSユーザー受入テストで判明した操作上の補足
- 正本言語: 日本語
- 基本文書: [phase_1_macos_user_manual_20260719171836.md](../history/user_manual/phase_1_macos_user_manual_20260719171836.md)
- Known Issues: [known_issues_and_observations_20260719195134.md](../history/operations/known_issues_and_observations_20260719195134.md)
- supersedes: なし（基本Manualを置き換えない補足文書）

## 1. CLI Helpの大文字表記

Helpに表示される次のような大文字は、文字列をそのまま入力する指定ではない。

```text
--profile PROFILE
--model-root MODEL_ROOT
--max-new-tokens MAX_NEW_TOKENS
```

`PROFILE`、`MODEL_ROOT`、`MAX_NEW_TOKENS`等は、利用者が実際の値へ置き換える仮引数名である。

また、`--profile`等の共通OptionはTop-level Commandの前ではなく、`generate`または`model-info`の後ろに指定する。

正しい例：

```bash
./.venv/bin/margpa-llm model-info \
  --profile config/profiles/local_macos_arm64.toml
```

```bash
./.venv/bin/margpa-llm generate \
  --profile config/profiles/local_macos_arm64.toml \
  --prompt "こんにちは"
```

誤った例：

```bash
./.venv/bin/margpa-llm --profile PROFILE
```

CLI Help自体にも、この仮引数規則と各Optionの説明を追加するFollow-upを行う。

## 2. Thinkingの意味とDefault

`--thinking`は、Modelに`<think>...</think>`形式の内部Reasoning出力を生成させる指定である。

`<高度推論>...</高度推論>`は、そのReasoningを利用者へ表示する場合のPresentation Labelであり、別の推論処理ではない。

通常利用では次をDefaultとする現在の設計が妥当である。

```text
Thinking Execution : disabled
Thinking Visibility: hidden
Persistence        : disabled
```

## 3. Hidden ThinkingとToken上限

Thinkingを有効にして非表示にした場合、ModelがReasoningだけでToken上限へ到達し、Final Answerを生成できないことがある。

```text
Thinking生成
  → Token上限到達
  → Closing／Final未生成
  → ReasoningはHidden
  → CLI表示が空になる
```

`--max-new-tokens 1024`へ増やすとFinal Answerまで生成できることをユーザー環境で確認した。

これはReasoning漏洩やParser故障ではない。ただし空出力だけでは原因が分からないため、次の意味のSafe Warningを追加する。

```text
最終回答を生成する前にToken上限へ到達しました。
```

## 4. Final Answer先頭の空行

`</think>`直後にModelが生成した改行をCurrent Parserが保持するため、Hidden ThinkingのFinal Answer先頭に空行が残る場合がある。

Raw Output保持方針による現象であり、Phase 1の重大問題ではない。UI／Presentation層における表示正規化候補として後続対応へ延期する。

## 5. 表示したReasoningの言語

`--response-language ja`はFinal Answerを日本語へ誘導するが、表示対象のRaw Reasoningまで日本語へ強制しない。Qwen3は日本語PromptでもReasoningを英語で生成する場合がある。

Phase 1-EではStrict Language EnforcementをScope外としている。後続で次を比較検討する。

- Model固有のReasoning Language Instruction
- `reasoning_language`設定
- Model交換
- 表示用翻訳

小型ModelではPrompt指定だけによる完全保証を主張しない。

## 6. Cross-platformの現在地

Current RuntimeはOS／Architectureを自動検出し、登録済みDefault Profileを選択する。未登録PlatformをMac Profileへ黙ってFallbackせず、安全に停止する。

一方、Linux／Windowsで実際に自動実行するProfile、Native Build、実機検証は未完了である。一般的なLinux／Windows自動対応は、後続Phaseへ延期する。

これはApplication Coreの後続機能をBlockしない。既存のDeployment Profile、Registry、Model Port、Capability境界を維持し、環境追加時に主としてProfile、Registry、Setup Recipe、Platform Testへ差分を閉じ込める。

ただし、同じLinux x86_64でもCPU、NVIDIA CUDA、AMD ROCm等が存在するため、全Hardwareを自動選択する完成形はConfig Fileの追加だけではない。Hardware／Acceleration検出と選択方針が必要になる。

## 7. User Acceptanceへの影響

- CLI仮引数説明とToken上限WarningはPhase 1 Acceptance Follow-up候補とする。
- Final先頭空行、Reasoning言語、一般Cross-platform完成はAccepted Deferredとする。
- Follow-up実装を行った場合、変更箇所とUser Manual該当項目を再検証してからPhase 1完了判定を行う。

<!-- SOURCE_END 5: docs/user_manual/phase_1_user_acceptance_findings_20260719195134.md -->

---

<!-- SOURCE_BEGIN 6: docs/user_manual/phase_1_web_and_lightning_user_manual_20260721185031.md -->

### Source 6: `docs/user_manual/phase_1_web_and_lightning_user_manual_20260721185031.md`

- History Target: `docs/project/phases/phase_1/history/user_manual/phase_1_web_and_lightning_user_manual_20260721185031.md`
- Source SHA-512: `2ffbff7733e1eb27d1f2d9b1c1902d50d34b8d79ae242ffbbe4532366e7fd0c22f3aa301ce9a7406daf5b2d74737c3bea4791f80265b4c8057875f51248868a6`
- Source Size: `18508` bytes

# Phase 1 Web／Lightning ユーザーマニュアル

- 文書ID: `phase_1_web_and_lightning_user_manual`
- 状態: `current_user_acceptance_candidate`
- 作成日時: `2026-07-21 18:50:31 JST`
- 更新日時: `2026-07-21 18:50:31 JST`
- Snapshot: `20260721185031`
- 作成担当: 設計者役担当Task
- 対象: MARGPA Runtime LLM Phase 1-A～Phase 1-H
- 対象ユーザー: Local MacまたはLightning AI StudioでPhase 1 Web Previewを起動・利用するユーザー
- 正本言語: 日本語
- Documentation Index: [documentation_index_20260721185031.md](../history/documentation_index_20260721185031.md)
- Phase 1-H Accepted Review: [designer_review_phase_1h_review_follow_up_20260721184140.md](../history/handoffs/designer_review_phase_1h_review_follow_up_20260721184140.md)
- Lightning Setup Script: `scripts/setup/setup_lightning_linux_x86_64_cuda.sh`
- supersedes: `phase_1_macos_user_manual_20260719171836.md`

## 1. このManualの目的

このManualは、MARGPA Runtime LLM Phase 1のWeb Previewについて、次を一つの手順として整理する。

- Local MacでWeb画面を起動する。
- Lightning AI StudioでCUDAまたはCPU Profileを選択して起動する。
- Lightningの外部公開URLを使用し、Lightning Accountを持たない利用者からWeb画面を開く。
- Web画面の設定と現在の制約を理解する。
- 起動失敗時に、Profile、Model Root、認証、Port公開を切り分ける。

Project一式のLightningへのUpload方法とModel Artifactの配置方法は、本Manualの対象外とする。これらが完了していることを前提とする。

## 2. 現在利用できる範囲

Phase 1 Web Previewで利用できる主な機能は次のとおりである。

- 一時的な複数Turn Chat
- Streaming表示
- 生成停止
- 新規Chat
- 回答言語 `ja／en／auto`
- 最大生成Token数 `1～2048`
- 推論過程表示 `OFF／ON`
- 要約モード `OFF／ON`
- 画面表示言語 `日本語／English`
- Model／Profile／Device情報の表示
- Preview用Basic認証
- Lightning向けCUDA／CPU Profile

現在の主な既定値：

```text
回答言語           : ja
最大生成Token数   : 2048
推論実行           : disabled
推論過程表示       : hidden
要約モード         : off
要約最大Token数    : 1024
画面表示言語       : ja
Web Host            : 127.0.0.1
Web Port            : 8000
```

## 3. 重要な制約

このWeb画面は少人数検証用Previewであり、本番Serviceではない。

- Basic認証は、本番用Account、権限管理、User管理を代替しない。
- 同時に実行できるModel Generationは1件である。
- 別Requestが生成中の場合、後続Requestは`model_busy`になることがある。
- Chat履歴はBrowser TabのMemoryだけに存在し、ReloadまたはTab終了で失われる。
- 新規ChatはBrowser内の一時履歴を消すが、ModelをReloadしない。
- Audit Log、永続Conversation、User Account、Rate Limitは未実装である。
- LightningのStudio、GPU、Processが停止またはSleepした場合、公開URLは一時的に利用不能またはCold Start待ちになる。
- Lightning実Reverse Proxy、CUDA、CPUでの最終受入は、Batch Lightning Gateで確認する。

## 4. 共通の前提

次が準備済みであることを前提とする。

- Project RootへProject一式が配置済みである。
- 実行環境ごとに`.venv/`が再構築済みである。
- `pyproject.toml`と`uv.lock`がProject内に存在する。
- Main Modelが次の論理構造で参照可能である。

```text
MODEL_ROOT/
└─ main/
   └─ qwen3-4b/
      └─ gguf/
         └─ Qwen3-4B-Q4_K_M.gguf
```

- Macの`.venv/`をLightningへUploadしていない。
- Model RootがProject外にある場合、`MARGPA_MODEL_ROOT`または`--model-root`で明示する。
- SecretをTracked Config、Docs、Command履歴、Screenshot、公開Logへ保存しない。

`requirements.txt`はCurrent Projectの依存関係正本ではない。依存関係の正本は`pyproject.toml`と`uv.lock`であり、`uv sync --frozen`をSetup Script経由で使用する。

## 5. Local Macで起動する

### 5.1 Project Rootへ移動する

```bash
cd /path/to/margpa-runtime-llm
```

### 5.2 Helpを確認する

```bash
./.venv/bin/margpa-web --help
```

Helpに表示される`HOST`、`PORT`、`PROFILE_PATH`等の大文字は、実際の値へ置き換える仮引数名である。文字列`HOST`や`PROFILE_PATH`をそのまま入力しない。

### 5.3 Local専用で起動する

```bash
./.venv/bin/margpa-web
```

明示する場合：

```bash
./.venv/bin/margpa-web \
  --host 127.0.0.1 \
  --port 8000
```

Browserで次を開く。

```text
http://127.0.0.1:8000/
```

`127.0.0.1`は同じMacだけから接続できるLoopback Addressである。この場合に限り、認証無効の既定値で起動できる。

### 5.4 起動を停止する

起動したTerminalで`Ctrl+C`を押す。

Model Generation中に停止した場合も、Current RuntimeはCooperative CancelとShutdown Cleanupを行う。ただしTerminalを強制終了するより、まず`Ctrl+C`を使用する。

## 6. Lightning AI Studioの実行設定

### 6.1 確認済みの対象環境

Current Lightning Profileは次のObserved Environmentを対象とする。

```text
OS                  : Ubuntu 24.04 LTS
Architecture        : x86_64
Execution Environment: container
Python              : 3.12.11
uv                  : 0.11.29（Project用に隔離したBinary）
GPU Candidate       : NVIDIA Tesla T4／CUDA
CPU Candidate       : Intel Xeon／4 CPU
Backend             : llama-cpp-python 0.3.34／GGML_CUDA=on
```

Lightning既設の`uv 0.11.18`を置換しない。Project用`uv 0.11.29`をPATHの先頭へ一時的に追加する。

```bash
export MARGPA_UV_BIN=/teamspace/studios/this_studio/.runtime-tools/uv/0.11.29/bin
export PATH="$MARGPA_UV_BIN:$PATH"
uv --version
```

期待値：

```text
uv 0.11.29 (x86_64-unknown-linux-gnu)
```

### 6.2 Project Rootへ移動する

```bash
cd /teamspace/studios/this_studio/margpa-runtime-llm
```

Projectを別の場所へ配置した場合は、その実際のProject Rootへ移動する。

### 6.3 Model Rootを明示する

Project Root内の`models/`を使用する場合：

```bash
export MARGPA_MODEL_ROOT="$PWD/models"
```

Project外へModelを配置した場合：

```bash
export MARGPA_MODEL_ROOT=/absolute/path/to/models
```

確認：

```bash
test -f "$MARGPA_MODEL_ROOT/main/qwen3-4b/gguf/Qwen3-4B-Q4_K_M.gguf"
printf 'MODEL_CHECK_EXIT=%s\n' "$?"
```

`MODEL_CHECK_EXIT=0`なら、期待するPathにModelが存在する。

### 6.4 Preview用Basic認証を設定する

Lightningの外部公開では`0.0.0.0`へBindするため、Basic認証が必須である。

```bash
export MARGPA_WEB_AUTH_MODE=basic
export MARGPA_WEB_AUTH_USERNAME='<preview-user>'
export MARGPA_WEB_AUTH_PASSWORD='<long-random-preview-password>'
```

`<...>`全体を実際の値へ置き換える。Credentialを上記の例のまま使わない。

運用上の注意：

- UsernameとPasswordは空にしない。
- Usernameには`:`を使用しない。
- Passwordは十分に長いRandom値を使用する。
- CredentialをGit、Docs、`.toml`、Screenshot、共有Chatへ残さない。
- Credentialは公開URLと別経路で検証利用者へ伝える。
- 検証終了後または漏えい疑いがある場合は、新しいCredentialへ変更してProcessを再起動する。

### 6.5 GPU Profileで起動する

LightningへNVIDIA GPUが割り当てられている場合：

```bash
./.venv/bin/margpa-web \
  --host 0.0.0.0 \
  --port 8000 \
  --profile config/profiles/lightning_linux_x86_64_cuda.toml \
  --model-root "$MARGPA_MODEL_ROOT"
```

GPU Profileの主要設定：

```text
Profile Key     : external.lightning-linux-x86_64.cuda
Device Kind     : gpu
Acceleration    : cuda
GPU Layers      : -1
Fallback Policy : deny
```

CUDAが必要なProfileでCUDAを利用できない場合、CPUへ黙ってFallbackしない。CPUで動かす場合はCPU Profileを明示する。

### 6.6 CPU Profileで起動する

GPU割当上限、GPU未割当、CPU比較検証等の場合：

```bash
./.venv/bin/margpa-web \
  --host 0.0.0.0 \
  --port 8000 \
  --profile config/profiles/lightning_linux_x86_64_cpu.toml \
  --model-root "$MARGPA_MODEL_ROOT"
```

CPU Profileの主要設定：

```text
Profile Key     : external.lightning-linux-x86_64.cpu
Device Kind     : cpu
Acceleration    : cpu_native
GPU Layers      : 0
Fallback Policy : deny
```

Current CPU Profileも、同じ`GGML_CUDA=on`でBuildした`llama-cpp-python`を`gpu_layers=0`で使用する。CPU実行はGPU実行より大幅に遅くなる可能性がある。

### 6.7 起動成功の確認

起動Processを実行したTerminalは、そのまま起動状態にしておく。別Terminalで次を確認する。

```bash
curl -i http://127.0.0.1:8000/healthz
```

期待値：

```text
HTTP/1.1 200 OK
{"status":"ok"}
```

`/healthz`は認証対象外だが、最小のStatusだけを返す。Model情報、Path、Credential、Prompt、回答は返さない。

Web RootはBasic認証対象である。

```bash
curl -i http://127.0.0.1:8000/
```

Credentialなしで`401 Unauthorized`になれば、認証境界が有効である。

## 7. Lightning Account外から開く

### 7.1 Studio編集画面ではなくWeb AppのPortを公開する

Lightning Account外の利用者へ見せる対象は、Studio編集画面やTerminalではなく、Port `8000`のWeb App公開URLである。

Lightning公式のCurrent案内では、独自Web AppはStudioのMenuから`Port viewer`／Ports Pluginを導入し、対象Portを開いて公開URLを取得する。UI名称はLightning側の更新で変わる可能性がある。

参考：

- [Lightning公式: Expose web apps](https://lightning.ai/docs/overview/host-web-apps/expose-web-apps)
- [Lightning公式: Host web apps](https://lightning.ai/docs/overview/host-web-apps)
- [Lightning公式: Studio SDK／Exposing ports](https://lightning.ai/docs/overview/sdk/studio)

### 7.2 Port公開の操作

1. Lightning Studioを起動する。
2. Section 6のCommandで`margpa-web`を`0.0.0.0:8000`へ起動する。
3. StudioのMenuまたはPlugin画面を開く。
4. `Port viewer`、`Ports`または同等のPort公開Pluginを追加・開く。
5. Port番号`8000`を指定する。
6. Private／Account限定URLではなく、外部共有用の`Public link`を有効にする。
7. Lightningが生成したHTTPSの公開URLを取得する。
8. AccountへLoginしていないIncognito／Private Windowで公開URLを開く。
9. MARGPA PreviewのBasic認証Promptが表示されることを確認する。
10. Section 6.4で設定したPreview Credentialを入力する。

Lightningの`Publish Studio`は、Studio環境を複製・共有する別機能である。今回の「他者がChat画面を試す」という目的では、Web AppのPort公開URLを使用し、Studio全体を公開する必要はない。

### 7.3 Account外Accessの合格条件

次をすべて満たせば、Account外のPreview Accessは成立したと判断する。

- LightningへLoginしていないBrowserでHTTPS公開URLを開ける。
- Preview CredentialなしではWeb Rootを表示できない。
- 正しいPreview CredentialでChat画面を表示できる。
- Runtime情報が画面下部等へ表示される。
- 短い日本語Promptで回答が生成される。
- `停止`が動作する。
- `新規Chat`でBrowser内履歴を初期化できる。
- Page Reload後に一時Chat履歴が失われる。
- 外部利用者からStudio Terminal、File、Editorへ到達できない。

### 7.4 公開時の安全境界

- Public Portを有効にする前に、必ずBasic認証を設定する。
- Raw `http://IP:8000`をInternetへ直接公開せず、LightningのHTTPS公開URLを使用する。
- Studio編集用共有LinkをPreview利用者へ渡さない。
- `healthz`が公開される点を認識する。ただし返すのは`status=ok`だけである。
- URLを知る人が増えた場合、Credentialを更新する。
- 少人数Previewの範囲を超える場合、本格Authentication、Rate Limit、Audit、User管理を実装するまで公開範囲を拡大しない。

## 8. Web画面の使い方

### 8.1 画面表示言語

画面右上の`日本語／English`でUI文字だけを変更する。

- UI LanguageはBrowserのLocal Storageへ保存される。
- Modelへ送る回答言語は変更しない。
- 回答言語と独立しているため、「画面はEnglish、回答は日本語」等の組み合わせが可能である。

### 8.2 回答言語

設定の`回答言語`で次を選ぶ。

```text
ja   : 日本語を要求する
en   : 英語を要求する
auto : Promptに応じてModelへ判断させる
```

小型Modelであるため、指定言語を常に完全保証するものではない。

### 8.3 最大生成Token数

`1～2048`の整数を指定する。既定値は`2048`である。

小さい値では、推論過程の生成中に上限へ到達し、最終回答が生成されないことがある。その場合、画面にToken上限到達Warningが表示される。

### 8.4 推論過程を表示

このSwitchは、Modelが生成した推論過程の表示／非表示を切り替える。

- 推論実行自体のON／OFFではない。
- 表示内容の正しさや、真の内部思考との一致を保証しない。
- Raw Thinkingは永続保存しない。
- 通常利用ではOFFを推奨する。

### 8.5 要約モード

`ON`では、通常回答の完了後に同じMain Modelで回答を要約し、要約だけを画面へ表示する。

```text
OFF : Main Model Call 1回
ON  : 通常回答＋要約のSequential Call
```

注意：

- 処理時間とToken使用量が増える。
- 要約最大Token数は`1024`である。
- 詳細、前提、注意事項が省略または変形される可能性がある。
- 要約を安全に完了できない場合、元の回答をFallback表示する。
- Cancel時はFallback表示せず、取消状態にする。

### 8.6 新規Chat

`新規Chat`は現在のBrowser Tab内のMessage列を初期化する。

- ModelはUnload／Reloadしない。
- Server側に履歴を保存しない。
- 複数Chatの一覧、Chat削除、履歴再開は未実装である。

## 9. Troubleshooting

### 9.1 Non-loopback Bindを拒否される

症状：

```text
error [invalid_configuration]: A non-loopback web bind requires preview authentication.
```

原因：`0.0.0.0`で起動したがBasic認証が設定されていない。

対処：Section 6.4の3 Environment Variableを設定し、Processを再起動する。

### 9.2 Basic認証設定を拒否される

症状：

```text
Basic preview authentication requires both credentials.
```

原因：UsernameまたはPasswordが未設定、空文字、空白だけである。

対処：両方を設定してProcessを再起動する。

### 9.3 Public URLでLightning Loginを要求される

原因候補：

- PortがPrivate／Teamspace限定になっている。
- Web App公開URLではなく、Studio編集画面のURLを共有している。

対処：Ports／Port ViewerでPort `8000`の`Public link`を有効にし、生成されたWeb App URLをIncognito Windowで再確認する。

### 9.4 Public URLへ接続できない

確認順：

1. Studioが起動中か。
2. `margpa-web` Processが終了していないか。
3. `--host 0.0.0.0 --port 8000`で起動したか。
4. `/healthz`がStudio内部から200を返すか。
5. Port Viewerの対象Portが8000か。
6. Lightning側のSleep／Cold Start待ちではないか。

### 9.5 ModelがLoadできない

確認：

```bash
printf '%s\n' "$MARGPA_MODEL_ROOT"
ls -lh "$MARGPA_MODEL_ROOT/main/qwen3-4b/gguf/Qwen3-4B-Q4_K_M.gguf"
```

Model Rootは、`main/`の一つ上を指す。

### 9.6 GPU Profileで起動できない

確認：

```bash
nvidia-smi
./.venv/bin/python scripts/setup/verify_phase1_environment.py --target lightning-cuda
```

GPUが割り当てられていない場合はCPU Profileを使用する。CUDA ProfileからCPUへ暗黙Fallbackさせない。

### 9.7 CPUで遅い

Qwen3-4B Q4_K_Mを4 CPUで実行するため、GPUより遅いことはExpected Behaviorである。短いPromptと小さめの最大生成Token数で疎通確認し、品質確認はGPU Profileで行う。

### 9.8 要約ONで長時間表示が変わらない

通常回答の後に同じModelで要約するため、回答が表示されるまでのSilent Intervalが増える。Current Runtimeは15秒ごとにSSE Keepalive Commentを送るが、Lightning実Reverse Proxyでの確認はBatch Gate対象である。

## 10. Lightning公開前の最小Checklist

```text
[ ] Project一式を配置済み
[ ] Modelを配置済み
[ ] Mac由来の.venvを搬入していない
[ ] Lightning上で.venvを再構築済み
[ ] Project用uv 0.11.29を選択済み
[ ] MARGPA_MODEL_ROOTを確認済み
[ ] CUDAまたはCPU Profileを明示済み
[ ] Preview Basic認証を設定済み
[ ] 0.0.0.0:8000で起動済み
[ ] Studio内healthzが200
[ ] Port 8000のPublic linkを有効化
[ ] Incognito WindowでAccount外Access確認
[ ] Credentialなしで401確認
[ ] CredentialありでChat画面確認
[ ] 短い生成／停止／新規Chat確認
[ ] UI LanguageとResponse Languageの独立確認
[ ] Summary OFF／ON確認
```

## 11. 現在の受入状態

```text
Mac Source／Static／Test Review        : Accepted
Mac Metal Model Smoke                  : Accepted
Phase 1-H Summary／UI Language         : Accepted
Lightning Read-only Preflight          : Accepted
Lightning Full Upload                  : User Operation
Lightning CUDA Native Gate             : Waiting
Lightning CPU Native Gate              : Waiting
Lightning Public URL／Reverse Proxy     : Waiting
Account外Browser Acceptance             : Waiting
Phase 1 Overall Completion             : Not Declared
```

本Manualの作成は、Lightning Native Gate、Account外Access、Phase 1全体完了を自動的に合格扱いしない。実際の操作結果をEvidenceとして確認した後に最終判定する。

## 12. Append-Only

既存のMac専用Manualを変更せず、Phase 1-F～1-H、Lightning起動、外部公開、Current Web設定を統合した新TimestampのManualを追加した。新しいTimestampの本Manualを最新とする。

<!-- SOURCE_END 6: docs/user_manual/phase_1_web_and_lightning_user_manual_20260721185031.md -->

---

<!-- SOURCE_BEGIN 7: docs/user_manual/phase_1_web_and_lightning_user_manual_20260726111632.md -->

### Source 7: `docs/user_manual/phase_1_web_and_lightning_user_manual_20260726111632.md`

- History Target: `docs/project/phases/phase_1/history/user_manual/phase_1_web_and_lightning_user_manual_20260726111632.md`
- Source SHA-512: `35570ea1bf0b43af23a5fc17ae208f70a903271cb7d0bda31afafc9c763fde304f301c28557738cfaab1d92df52e51d82d59e2223bebb7732d7f7d2450ae0390`
- Source Size: `9193` bytes

# Phase 1 Web／Lightning ユーザーマニュアル

- 文書ID: `phase_1_web_and_lightning_user_manual`
- 状態: `current_verified_phase_1`
- 作成日時: `2026-07-26 11:16:32 JST`
- 更新日時: `2026-07-26 11:16:32 JST`
- Snapshot: `20260726111632`
- 作成担当: 設計者役担当Task
- 対象: MARGPA Runtime LLM Phase 1-A～Phase 1-I
- 対象環境: Mac Local Web／Lightning Linux x86_64 Pure CPU Web
- 詳細なLightning再構築手順: [lightning_pure_cpu_actual_environment_reconstruction_manual_20260726092413.md](../history/user_manual/lightning_pure_cpu_actual_environment_reconstruction_manual_20260726092413.md)
- Acceptance Review: [designer_review_top_level_phase_1_completion_and_lightning_web_acceptance_20260726111632.md](../history/handoffs/designer_review_top_level_phase_1_completion_and_lightning_web_acceptance_20260726111632.md)
- 正本言語: 日本語
- supersedes: `phase_1_web_and_lightning_user_manual_20260721185031.md`

## 1. このManualの目的

Phase 1で実際に検証済みのWeb Preview機能、Mac起動、Lightning Pure CPU起動、外部公開、停止および現在の制約を整理する。

環境をゼロから再構築する場合は、詳細なLightning再構築手順を先に参照する。

## 2. Phase 1で利用できる機能

- 一時的な複数Turn Chat
- Streaming
- Send／Stop
- `Cmd+Enter`／`Ctrl+Enter`送信
- New Chat
- UI日本語／English
- 回答言語`ja／en／auto`
- 最大生成Token数`1～2048`
- Thinking Generation
- Thinking Visibility
- Summary Mode
- User／Assistant Message Copy
- 完了後の安全なMarkdown Rendering
- Basic認証
- Model Busyの安全な拒否
- Mac Metal
- Lightning Linux x86_64 Pure CPU

Phase 1の会話はBrowser Tab内の一時Memoryであり、永続保存されない。

## 3. Current Defaults

```text
Response Language       : ja
Max New Tokens          : 2048
Thinking Generation     : off
Thinking Visibility     : hidden
Summary Mode            : off
UI Language             : ja
Mac Host                : 127.0.0.1
Lightning Host          : 0.0.0.0
Port                    : 8000
Lightning Profile       : config/profiles/lightning_linux_x86_64_cpu_native.toml
```

## 4. Macで起動する

Project Root：

```bash
cd /path/to/margpa-runtime-llm
```

起動：

```bash
./.venv/bin/margpa-web
```

Browser：

```text
http://127.0.0.1:8000/
```

停止：

```text
Ctrl+C
```

Macで外部公開することを本Manualは想定しない。

## 5. Lightningの確認済み配置

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
├─ models/
│  └─ main/qwen3-4b/gguf/Qwen3-4B-Q4_K_M.gguf
└─ .runtime-tools/uv/0.11.29/bin/
```

## 6. Lightning Webを手動起動する

### 6.1 Environment

```bash
export MARGPA_WORKSPACE_ROOT=/teamspace/studios/this_studio
export MARGPA_PROJECT_ROOT="$MARGPA_WORKSPACE_ROOT/margpa-runtime-llm"
export MARGPA_MODEL_ROOT="$MARGPA_WORKSPACE_ROOT/models"
export MARGPA_UV_BIN="$MARGPA_WORKSPACE_ROOT/.runtime-tools/uv/0.11.29/bin"
export MARGPA_ENV_PREFIX="$MARGPA_PROJECT_ROOT/.venv"
export PATH="$MARGPA_UV_BIN:$PATH"

cd "$MARGPA_PROJECT_ROOT"
```

確認：

```bash
test -x "$MARGPA_ENV_PREFIX/bin/margpa-web"
test -f "$MARGPA_MODEL_ROOT/main/qwen3-4b/gguf/Qwen3-4B-Q4_K_M.gguf"

printf 'WEB_PREREQUISITES_EXIT=%s\n' "$?"
```

期待値：

```text
WEB_PREREQUISITES_EXIT=0
```

### 6.2 Basic認証

```bash
export MARGPA_WEB_AUTH_MODE=basic
export MARGPA_WEB_AUTH_USERNAME='preview'
export MARGPA_WEB_AUTH_PASSWORD="$(
  "$MARGPA_ENV_PREFIX/bin/python" -c \
  'import secrets; print(secrets.token_urlsafe(32))'
)"
```

現在の手動Previewでは、一度だけ表示して安全な経路で控える。

```bash
printf 'Preview Username: %s\n' "$MARGPA_WEB_AUTH_USERNAME"
printf 'Preview Password: %s\n' "$MARGPA_WEB_AUTH_PASSWORD"
```

CredentialをDocs、Config、Screenshot、Git、公開Logへ保存しない。

Phase 1-exでAuto-startを導入する場合は、毎回Random Passwordを作らず、Lightning Managed Secretsに保存した安定Credentialを使用して明示Rotateする。

### 6.3 Pure CPU Profile

```bash
"$MARGPA_ENV_PREFIX/bin/margpa-web" \
  --host 0.0.0.0 \
  --port 8000 \
  --profile config/profiles/lightning_linux_x86_64_cpu_native.toml \
  --model-root "$MARGPA_MODEL_ROOT"
```

このTerminalは起動中のままにする。

Model Load、GGUF MetadataおよびSHA-512検証に時間がかかる場合がある。Pure CPU生成、ThinkingおよびSummary ModeはMac Metalより大幅に遅い。

## 7. Health Check

別Terminal：

```bash
curl -i http://127.0.0.1:8000/healthz
```

期待値：

```text
HTTP/1.1 200 OK
{"status":"ok"}
```

CredentialなしRoot：

```bash
curl -i http://127.0.0.1:8000/
```

期待値：

```text
401 Unauthorized
```

`/healthz`は認証対象外だが、最小Statusだけを返す。

## 8. Lightning Port公開

Lightning StudioのPort ViewerでPort `8000`を追加し、外部共有時はPublic Linkを有効化する。

LightningへLoginしていないPrivate／Incognito Windowから次を確認する。

- Basic認証が表示される。
- 誤Credentialでは開けない。
- 正しいCredentialでMARGPA画面が開く。
- Studio TerminalまたはFile Editorは外部から見えない。

確認済みPublic Link：

```text
https://lightning-preview-url-redacted.invalid/not-published
```

Lightning側の再構成によりURLが変わる可能性がある。

## 9. Web操作

### 9.1 送信

- Send Button
- `Cmd+Enter`
- `Ctrl+Enter`

Enterだけでは送信しない。

### 9.2 Stop

生成中またはSummary処理中にStop Buttonを押す。停止後に再送信できる。

### 9.3 New Chat

Current Conversation Contextを消去する。ModelはReloadしない。

生成中にNew Chatを押した場合、Current Generationを停止し、Contextを初期化する。

### 9.4 Language

```text
UI Language       : 日本語／English
Response Language : ja／en／auto
```

両者は独立している。

### 9.5 Thinking

Thinking GenerationをONにした場合だけThinking VisibilityをONにできる。

表示内容はModel生成の推論過程であり、真の内部思考、正解または完全な説明責任を保証しない。保存およびFinal Copyの対象外である。

### 9.6 Summary

Summary Modeは通常回答後に同じMain Modelをもう一度呼ぶ。Pure CPUではLatencyが大きく増える。

## 10. Model Busy

同時Generation数は1である。別Tabで同時に生成した場合、後続Requestは安全に拒否される。

英語：

```text
The model is processing another request.
The request failed.
```

日本語：

```text
Modelは別のRequestを処理中です。
Requestに失敗しました。
```

先行Request完了後に再実行する。

## 11. Browser Reload

Reloadすると次が消える。

- Conversation
- Response Languageの一時変更
- Max New Tokensの一時変更
- Thinking設定
- Summary Mode

UI LanguageだけはBrowserへ保持される。

## 12. 終了

起動Terminal：

```text
Ctrl+C
```

CredentialをShellから除去する。

```bash
unset MARGPA_WEB_AUTH_PASSWORD
unset MARGPA_WEB_AUTH_USERNAME
unset MARGPA_WEB_AUTH_MODE
```

別TerminalのHealth Checkが接続失敗になれば、Process停止を確認できる。

Lightningを使用しない場合はMachineをManual Sleepにする。Browserを閉じただけでCost停止したと仮定せず、Lightning DashboardでMachine Stateを確認する。

## 13. Auto-start

Current Phase 1はManual Startである。Sleep／Wake後に上記Commandを再入力しないAuto-startは未実装である。

Phase 1-exで次を検討する。

- `~/.lightning_studio/on_start.sh`
- Project-owned Launcher
- Lightning Managed Secrets
- Traffic-aware Auto-start
- Cold Start表示
- CPU固定
- Idle Sleep
- Duplicate Process防止

Auto-start完了までは、使用時に手動起動し、終了時にManual Sleepする。

## 14. iPhone／Mobile

iPhone／iOSは「不可能」ではなく、Current Phase 1でResponsive Acceptanceを行っていない。

Phase 4または後続UI Phaseで、iOS Safari、Touch、Virtual Keyboard、Safe Area、Narrow ViewportおよびCode Block横Overflowを検証する。

## 15. Current Limitations

- Pure CPU生成は遅い。
- Persistent Conversationはない。
- Multi-user Accountはない。
- Rate Limitはない。
- Basic認証は本番認証ではない。
- Streaming中はRaw Markdownが見える場合がある。
- Markdown Tableは未対応である。
- Code Block個別Copyは未対応である。
- Busy表示は具体Messageと汎用Messageが重複する。
- Mobile Responsive Acceptanceは未実施である。
- Auto-startは未実装である。

## 16. Acceptance State

MacおよびLightning Pure CPUについて、本Manual記載のPhase 1 Web機能はUser Acceptance済みである。

```text
Mac Web                  : PASS
Lightning External Web  : PASS
Phase 1                 : COMPLETE／ACCEPTED
```

<!-- SOURCE_END 7: docs/user_manual/phase_1_web_and_lightning_user_manual_20260726111632.md -->

---

