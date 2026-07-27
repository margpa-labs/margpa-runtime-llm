#!/bin/bash

set -euo pipefail

readonly PHASE1F_PROJECT_ROOT="$(
  CDPATH= cd -- "$(dirname -- "$0")/../.." >/dev/null 2>&1
  pwd -P
)"
readonly PHASE1F_EXPECTED_UV_VERSION="0.11.29"
readonly PHASE1F_EXPECTED_PYTHON_VERSION="3.12.11"
readonly PHASE1F_DEFAULT_MODEL_PATH="${PHASE1F_PROJECT_ROOT}/models/main/qwen3-4b/gguf/Qwen3-4B-Q4_K_M.gguf"
readonly PHASE1F_CUDA_PROFILE="${PHASE1F_PROJECT_ROOT}/config/profiles/lightning_linux_x86_64_cuda.toml"
readonly PHASE1F_CPU_PROFILE="${PHASE1F_PROJECT_ROOT}/config/profiles/lightning_linux_x86_64_cpu.toml"

phase1f_target_venv="${PHASE1F_PROJECT_ROOT}/.venv"
phase1f_environment_mode="auto"
phase1f_venv_explicit=0
phase1f_model_path="${PHASE1F_DEFAULT_MODEL_PATH}"
phase1f_rebuild_native=0
phase1f_run_cuda_smoke=0
phase1f_run_cpu_smoke=0
phase1f_cpu_only=0

usage() {
  cat <<'EOF'
Usage: scripts/setup/setup_lightning_linux_x86_64_cuda.sh [options]

Reproduce the Phase 1-F Lightning Linux/x86_64 environment with
llama-cpp-python 0.3.34 built from source using GGML_CUDA=on.

Options:
  --environment-mode MODE
                       auto, studio-active, or project-venv (default: auto)
  --venv PATH          Target for project-venv mode (default: project .venv)
  --rebuild-native     Force a new llama-cpp-python CUDA source build
  --cuda-smoke         Run the bounded Qwen3-4B CUDA acceptance probe
  --cpu-smoke          Also run the same CUDA build with the CPU profile
  --cpu-only           Verify/use the CUDA build with gpu_layers=0 without GPU allocation
  --model-path PATH    Local GGUF path used by smoke tests (never downloaded)
  -h, --help           Show this help

Prerequisites:
  - Ubuntu Linux x86_64 running in a container
  - CPython 3.12.11 already available
  - uv 0.11.29 available on PATH
  - CUDA Toolkit and nvcc only when a CUDA source rebuild is required
  - NVIDIA driver, nvidia-smi, and an allocated GPU unless --cpu-only is used
  - Network access when dependencies or the native source build are absent
  - The local GGUF artifact when a smoke option is selected

auto uses the active persistent Studio/Conda environment when one is detected;
otherwise it selects the project Venv. Normal dependency sync and the native
CUDA package build are separate. An already verified CUDA build is reused
without requiring nvcc unless --rebuild-native is specified.
EOF
}

fail() {
  printf 'Phase 1-F Lightning setup failed: %s\n' "$1" >&2
  exit 1
}

while (($# > 0)); do
  case "$1" in
    --environment-mode)
      (($# >= 2)) || fail "--environment-mode requires a value"
      phase1f_environment_mode="$2"
      shift 2
      ;;
    --venv)
      (($# >= 2)) || fail "--venv requires a path"
      phase1f_target_venv="$2"
      phase1f_venv_explicit=1
      shift 2
      ;;
    --rebuild-native)
      phase1f_rebuild_native=1
      shift
      ;;
    --cuda-smoke)
      phase1f_run_cuda_smoke=1
      shift
      ;;
    --cpu-smoke)
      phase1f_run_cpu_smoke=1
      shift
      ;;
    --cpu-only)
      phase1f_cpu_only=1
      shift
      ;;
    --model-path)
      (($# >= 2)) || fail "--model-path requires a path"
      phase1f_model_path="$2"
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

case "${phase1f_environment_mode}" in
  auto|studio-active|project-venv) ;;
  *) fail "--environment-mode must be auto, studio-active, or project-venv" ;;
esac
if ((phase1f_venv_explicit == 1)); then
  if [[ "${phase1f_environment_mode}" == "studio-active" ]]; then
    fail "--venv cannot be combined with --environment-mode studio-active"
  fi
  phase1f_environment_mode="project-venv"
fi

case "${phase1f_target_venv}" in
  /*) ;;
  *) phase1f_target_venv="${PHASE1F_PROJECT_ROOT}/${phase1f_target_venv}" ;;
esac

case "${phase1f_model_path}" in
  /*) ;;
  *) phase1f_model_path="${PHASE1F_PROJECT_ROOT}/${phase1f_model_path}" ;;
esac

[[ "$(uname -s)" == "Linux" ]] || fail "this recipe is restricted to Linux"
[[ "$(uname -m)" == "x86_64" ]] || fail "this recipe requires an x86_64 host"
[[ -r /etc/os-release ]] || fail "/etc/os-release is unavailable"
phase1f_distribution="$(awk -F= '$1 == "ID" {gsub(/\"/, "", $2); print tolower($2)}' /etc/os-release)"
[[ "${phase1f_distribution}" == "ubuntu" ]] || fail "this recipe requires Ubuntu"

phase1f_container_detected=0
if [[ -e /.dockerenv || -e /run/.containerenv || -n "${container:-}" ]]; then
  phase1f_container_detected=1
elif [[ -r /proc/1/cgroup ]]; then
  phase1f_cgroup="$(</proc/1/cgroup)"
  case "${phase1f_cgroup}" in
    *docker*|*containerd*|*kubepods*|*libpod*|*lxc*) phase1f_container_detected=1 ;;
  esac
fi
((phase1f_container_detected == 1)) || fail "a supported container marker was not detected"

phase1f_uv_bin="$(command -v uv || true)"
[[ -n "${phase1f_uv_bin}" ]] || fail "uv is not available on PATH"
phase1f_uv_version="$(${phase1f_uv_bin} --version | awk '{print $2}')"
[[ "${phase1f_uv_version}" == "${PHASE1F_EXPECTED_UV_VERSION}" ]] || \
  fail "expected uv ${PHASE1F_EXPECTED_UV_VERSION}, got ${phase1f_uv_version}"

phase1f_active_environment="${VIRTUAL_ENV:-${CONDA_PREFIX:-}}"
if [[ "${phase1f_environment_mode}" == "auto" ]]; then
  if [[ -n "${phase1f_active_environment}" ]]; then
    phase1f_environment_mode="studio-active"
  else
    phase1f_environment_mode="project-venv"
  fi
fi
if [[ "${phase1f_environment_mode}" == "studio-active" ]]; then
  [[ -n "${phase1f_active_environment}" ]] || \
    fail "studio-active mode requires VIRTUAL_ENV or CONDA_PREFIX"
  phase1f_target_environment="${phase1f_active_environment}"
else
  phase1f_target_environment="${phase1f_target_venv}"
fi
phase1f_runtime_python="${phase1f_target_environment}/bin/python"

if [[ -x "${phase1f_runtime_python}" ]]; then
  phase1f_python_bin="${phase1f_runtime_python}"
else
  [[ "${phase1f_environment_mode}" == "project-venv" ]] || \
    fail "the active Studio environment has no executable bin/python"
  command -v python3 >/dev/null 2>&1 || fail "python3 is unavailable"
  phase1f_python_bin="$(command -v python3)"
fi
phase1f_python_version="$(${phase1f_python_bin} --version | awk '{print $2}')"
[[ "${phase1f_python_version}" == "${PHASE1F_EXPECTED_PYTHON_VERSION}" ]] || \
  fail "expected Python ${PHASE1F_EXPECTED_PYTHON_VERSION}, got ${phase1f_python_version}"

if ((phase1f_cpu_only == 0)); then
  command -v nvidia-smi >/dev/null 2>&1 || fail "nvidia-smi is unavailable"
  nvidia-smi -L >/dev/null 2>&1 || fail "an allocated NVIDIA GPU was not detected"
fi
if ((phase1f_cpu_only == 1 && phase1f_run_cuda_smoke == 1)); then
  fail "--cpu-only and --cuda-smoke cannot be used together"
fi

if [[ "${phase1f_environment_mode}" == "project-venv" ]]; then
  [[ "${phase1f_target_environment}" != "${PHASE1F_PROJECT_ROOT}" ]] || \
    fail "the target Venv must not be the Project Root"
  [[ -d "$(dirname -- "${phase1f_target_environment}")" ]] || \
    fail "the target Venv parent directory does not exist"
fi

if ((phase1f_run_cuda_smoke == 1 || phase1f_run_cpu_smoke == 1)) && \
  [[ ! -f "${phase1f_model_path}" ]]; then
  fail "the local GGUF artifact does not exist: ${phase1f_model_path}"
fi

cd "${PHASE1F_PROJECT_ROOT}"
"${phase1f_uv_bin}" lock --check

printf 'Project Root : %s\n' "${PHASE1F_PROJECT_ROOT}"
printf 'Environment  : %s\n' "${phase1f_environment_mode}"
printf 'Target Prefix: %s\n' "${phase1f_target_environment}"
printf 'uv           : %s (%s)\n' "${phase1f_uv_bin}" "${phase1f_uv_version}"
printf 'Python       : %s / Linux x86_64 / container\n' "${PHASE1F_EXPECTED_PYTHON_VERSION}"
printf 'Native Build : llama-cpp-python==0.3.34 / source / GGML_CUDA=on\n'

phase1f_cuda_build_ready=0
if [[ -x "${phase1f_runtime_python}" ]] && \
  "${phase1f_runtime_python}" -c \
    'from llama_cpp import llama_cpp; info = llama_cpp.llama_print_system_info().decode("utf-8", errors="replace").upper(); raise SystemExit(0 if llama_cpp.llama_supports_gpu_offload() and "CUDA" in info else 1)' \
    >/dev/null 2>&1; then
  phase1f_cuda_build_ready=1
fi

env UV_PROJECT_ENVIRONMENT="${phase1f_target_environment}" \
  "${phase1f_uv_bin}" sync \
  --frozen \
  --python "${phase1f_python_bin}" \
  --no-python-downloads \
  --inexact \
  --extra inference-llama \
  --extra web \
  --group dev \
  --group notebook \
  --no-install-package llama-cpp-python

[[ -x "${phase1f_runtime_python}" ]] || fail "the target Python environment was not created"

if ((phase1f_rebuild_native == 1 || phase1f_cuda_build_ready == 0)); then
  command -v nvcc >/dev/null 2>&1 || \
    fail "nvcc is required because a CUDA native rebuild is needed"
  nvcc --version >/dev/null 2>&1 || fail "the CUDA Toolkit is unavailable"
  env \
    CMAKE_ARGS="-DGGML_CUDA=on" \
    CMAKE_BUILD_PARALLEL_LEVEL="${CMAKE_BUILD_PARALLEL_LEVEL:-4}" \
    "${phase1f_uv_bin}" pip install \
    --python "${phase1f_runtime_python}" \
    --no-binary llama-cpp-python \
    --reinstall-package llama-cpp-python \
    "llama-cpp-python==0.3.34"
else
  printf 'Native Build : reusing the existing verified CUDA build\n'
fi

"${phase1f_runtime_python}" -c \
  'from llama_cpp import llama_cpp; info = llama_cpp.llama_print_system_info().decode("utf-8", errors="replace").upper(); raise SystemExit(0 if llama_cpp.llama_supports_gpu_offload() and "CUDA" in info else 1)' \
  >/dev/null 2>&1 || fail "the target environment does not contain a verified CUDA build"

if ((phase1f_cpu_only == 1)); then
  "${phase1f_runtime_python}" scripts/setup/verify_phase1_environment.py \
    --target lightning-cpu
else
  "${phase1f_runtime_python}" scripts/setup/verify_phase1_environment.py \
    --target lightning-cuda
fi

if ((phase1f_run_cuda_smoke == 1)); then
  MARGPA_MODEL_ROOT="$(dirname -- "$(dirname -- "$(dirname -- "$(dirname -- "${phase1f_model_path}")")")")" \
    "${phase1f_runtime_python}" \
    scripts/models/phase1f_cross_environment_acceptance.py \
    --profile "${PHASE1F_CUDA_PROFILE}"
fi

if ((phase1f_run_cpu_smoke == 1)); then
  "${phase1f_runtime_python}" scripts/setup/verify_phase1_environment.py \
    --target lightning-cpu
  MARGPA_MODEL_ROOT="$(dirname -- "$(dirname -- "$(dirname -- "$(dirname -- "${phase1f_model_path}")")")")" \
    "${phase1f_runtime_python}" \
    scripts/models/phase1f_cross_environment_acceptance.py \
    --profile "${PHASE1F_CPU_PROFILE}"
fi

printf 'Phase 1-F Lightning Linux/x86_64 CUDA setup completed successfully.\n'
