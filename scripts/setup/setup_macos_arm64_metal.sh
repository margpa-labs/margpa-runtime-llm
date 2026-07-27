#!/bin/bash

set -euo pipefail

readonly PHASE1_PROJECT_ROOT="$(
  CDPATH= cd -- "$(dirname -- "$0")/../.." >/dev/null 2>&1
  pwd -P
)"
readonly PHASE1_EXPECTED_UV_VERSION="0.11.29"
readonly PHASE1_EXPECTED_PYTHON_VERSION="3.13.14"
readonly PHASE1_DEFAULT_MODEL_PATH="${PHASE1_PROJECT_ROOT}/models/main/qwen3-4b/gguf/Qwen3-4B-Q4_K_M.gguf"

phase1_target_venv="${PHASE1_PROJECT_ROOT}/.venv"
phase1_model_path="${PHASE1_DEFAULT_MODEL_PATH}"
phase1_clean_source_build=0
phase1_run_smoke=0

usage() {
  cat <<'EOF'
Usage: scripts/setup/setup_macos_arm64_metal.sh [options]

Reproduce the Phase 1 local macOS/ARM64 environment with llama-cpp-python
0.3.34 built from source using GGML_METAL=on.

Options:
  --venv PATH            Target virtual environment (default: project .venv)
  --clean-source-build   Require a new target Venv and use a disposable uv cache
  --smoke                Run the bounded Qwen3-4B Metal smoke after setup
  --model-path PATH      Local GGUF path used by --smoke (never downloaded)
  -h, --help             Show this help

Prerequisites:
  - macOS on Apple Silicon (arm64)
  - Xcode Command Line Tools
  - uv 0.11.29 available on PATH
  - Network access for a clean source build
  - The local GGUF artifact when --smoke is selected

The Metal flag is intentionally scoped to this local setup process. It is not
stored in uv.lock and must not be reused for Cloud/CUDA deployment profiles.
EOF
}

fail() {
  printf 'Phase 1 Metal setup failed: %s\n' "$1" >&2
  exit 1
}

while (($# > 0)); do
  case "$1" in
    --venv)
      (($# >= 2)) || fail "--venv requires a path"
      phase1_target_venv="$2"
      shift 2
      ;;
    --clean-source-build)
      phase1_clean_source_build=1
      shift
      ;;
    --smoke)
      phase1_run_smoke=1
      shift
      ;;
    --model-path)
      (($# >= 2)) || fail "--model-path requires a path"
      phase1_model_path="$2"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      fail "unknown option: $1"
      ;;
  esac
done

case "${phase1_target_venv}" in
  /*) ;;
  *) phase1_target_venv="${PHASE1_PROJECT_ROOT}/${phase1_target_venv}" ;;
esac

case "${phase1_model_path}" in
  /*) ;;
  *) phase1_model_path="${PHASE1_PROJECT_ROOT}/${phase1_model_path}" ;;
esac

[[ "$(uname -s)" == "Darwin" ]] || fail "this recipe is restricted to macOS"
[[ "$(uname -m)" == "arm64" ]] || fail "this recipe requires an arm64 host"
command -v xcode-select >/dev/null 2>&1 || fail "xcode-select is unavailable"
xcode-select -p >/dev/null 2>&1 || fail "Xcode Command Line Tools are unavailable"
command -v xcrun >/dev/null 2>&1 || fail "xcrun is unavailable"
xcrun --find clang >/dev/null 2>&1 || fail "Apple clang is unavailable"

phase1_uv_bin="$(command -v uv || true)"
[[ -n "${phase1_uv_bin}" ]] || fail "uv is not available on PATH"
phase1_uv_version="$("${phase1_uv_bin}" --version | awk '{print $2}')"
[[ "${phase1_uv_version}" == "${PHASE1_EXPECTED_UV_VERSION}" ]] || \
  fail "expected uv ${PHASE1_EXPECTED_UV_VERSION}, got ${phase1_uv_version}"

[[ "${phase1_target_venv}" != "${PHASE1_PROJECT_ROOT}" ]] || \
  fail "the target Venv must not be the Project Root"
[[ -d "$(dirname -- "${phase1_target_venv}")" ]] || \
  fail "the target Venv parent directory does not exist"

if ((phase1_clean_source_build == 1)) && [[ -e "${phase1_target_venv}" ]]; then
  fail "--clean-source-build requires a target Venv path that does not exist"
fi

if ((phase1_run_smoke == 1)) && [[ ! -f "${phase1_model_path}" ]]; then
  fail "the local GGUF artifact does not exist: ${phase1_model_path}"
fi

cd "${PHASE1_PROJECT_ROOT}"
"${phase1_uv_bin}" lock --check

phase1_sync_args=(
  sync
  --frozen
  --managed-python
  --python "${PHASE1_EXPECTED_PYTHON_VERSION}"
  --extra inference-llama
  --extra web
  --group dev
  --group notebook
  --no-binary-package llama-cpp-python
  --reinstall-package llama-cpp-python
)

if ((phase1_clean_source_build == 1)); then
  phase1_sync_args+=(--no-cache)
fi

printf 'Project Root : %s\n' "${PHASE1_PROJECT_ROOT}"
printf 'Target Venv  : %s\n' "${phase1_target_venv}"
printf 'uv           : %s (%s)\n' "${phase1_uv_bin}" "${phase1_uv_version}"
printf 'Python       : %s / arm64 / managed\n' "${PHASE1_EXPECTED_PYTHON_VERSION}"
printf 'Native Build : llama-cpp-python==0.3.34 / source / GGML_METAL=on\n'

env \
  UV_PROJECT_ENVIRONMENT="${phase1_target_venv}" \
  CMAKE_ARGS="-DGGML_METAL=on" \
  CMAKE_BUILD_PARALLEL_LEVEL="${CMAKE_BUILD_PARALLEL_LEVEL:-6}" \
  "${phase1_uv_bin}" "${phase1_sync_args[@]}"

"${phase1_target_venv}/bin/python" scripts/setup/verify_phase1_environment.py

if ((phase1_run_smoke == 1)); then
  "${phase1_target_venv}/bin/python" scripts/models/qwen3_metal_smoke.py \
    --model-path "${phase1_model_path}" \
    --quiet-backend
fi

printf 'Phase 1 macOS/ARM64 Metal setup completed successfully.\n'
