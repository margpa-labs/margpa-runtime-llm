#!/bin/bash

set -euo pipefail

readonly PHASE1F_PROJECT_ROOT="$(
  CDPATH= cd -- "$(dirname -- "$0")/../.." >/dev/null 2>&1
  pwd -P
)"
readonly PHASE1F_EXPECTED_UV_VERSION="0.11.29"
readonly PHASE1F_EXPECTED_PYTHON_VERSION="3.12.11"
readonly PHASE1F_CPU_NATIVE_PROFILE="${PHASE1F_PROJECT_ROOT}/config/profiles/lightning_linux_x86_64_cpu_native.toml"

phase1f_environment_mode="auto"
phase1f_runtime_target="cuda-gpu"
phase1f_runtime_target_explicit=0
phase1f_cpu_only=0

usage() {
  cat <<'EOF'
Usage: preflight_lightning_ai_studio.sh [options]

Run a read-only Lightning Studio probe before environment setup, model
placement, or native acceptance.

Options:
  --environment-mode MODE  auto, studio-active, or project-venv (default: auto)
  --runtime-target TARGET  cuda-gpu, cuda-cpu, or cpu-native (default: cuda-gpu)
  --cpu-only               Backward-compatible alias for --runtime-target cuda-cpu
  -h, --help               Show this help

Target meanings:
  cuda-gpu   CUDA build with an allocated NVIDIA GPU (legacy default)
  cuda-cpu   CUDA build executed with gpu_layers=0 (legacy --cpu-only)
  cpu-native Pure CPU build; does not probe GPU, NVIDIA, CUDA, or nvcc

This probe is read-only. It does not create an environment, install packages,
place a model, or download artifacts.
EOF
}

fail() {
  printf 'Phase 1-F Lightning preflight failed: %s\n' "$1" >&2
  exit 1
}

while (($# > 0)); do
  case "$1" in
    --environment-mode)
      (($# >= 2)) || fail "--environment-mode requires a value"
      phase1f_environment_mode="$2"
      shift 2
      ;;
    --runtime-target)
      (($# >= 2)) || fail "--runtime-target requires a value"
      phase1f_runtime_target="$2"
      phase1f_runtime_target_explicit=1
      shift 2
      ;;
    --cpu-only)
      phase1f_cpu_only=1
      shift
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
case "${phase1f_runtime_target}" in
  cuda-gpu|cuda-cpu|cpu-native) ;;
  *) fail "--runtime-target must be cuda-gpu, cuda-cpu, or cpu-native" ;;
esac
if ((phase1f_cpu_only == 1)); then
  if ((phase1f_runtime_target_explicit == 1)) && \
    [[ "${phase1f_runtime_target}" != "cuda-cpu" ]]; then
    fail "--cpu-only conflicts with the explicit runtime target"
  fi
  phase1f_runtime_target="cuda-cpu"
fi

[[ "$(uname -s)" == "Linux" ]] || fail "this probe requires Linux"
[[ "$(uname -m)" == "x86_64" ]] || fail "this probe requires x86_64"

# The path override and forced container marker are used by isolated repository tests.
phase1f_os_release_path="${PHASE1F_PREFLIGHT_OS_RELEASE_PATH:-/etc/os-release}"
[[ -r "${phase1f_os_release_path}" ]] || fail "os-release metadata is unavailable"
phase1f_distribution="$(
  awk -F= '$1 == "ID" {gsub(/"/, "", $2); print tolower($2)}' \
    "${phase1f_os_release_path}"
)"
[[ "${phase1f_distribution}" == "ubuntu" ]] || fail "this probe requires Ubuntu"

phase1f_container_detected=0
if [[ "${PHASE1F_PREFLIGHT_CONTAINER_MARKER:-}" == "present" ]]; then
  phase1f_container_detected=1
elif [[ -e /.dockerenv || -e /run/.containerenv || -n "${container:-}" ]]; then
  phase1f_container_detected=1
elif [[ -r /proc/1/cgroup ]]; then
  phase1f_cgroup="$(</proc/1/cgroup)"
  case "${phase1f_cgroup}" in
    *docker*|*containerd*|*kubepods*|*libpod*|*lxc*) phase1f_container_detected=1 ;;
  esac
fi
((phase1f_container_detected == 1)) || fail "a supported container marker was not detected"

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
  phase1f_environment_path="${phase1f_active_environment}"
  phase1f_python_bin="${phase1f_environment_path}/bin/python"
  [[ -x "${phase1f_python_bin}" ]] || fail "the active environment has no bin/python"
else
  phase1f_environment_path="${PHASE1F_PROJECT_ROOT}/.venv"
  command -v python3 >/dev/null 2>&1 || fail "python3 is unavailable"
  phase1f_python_bin="$(command -v python3)"
fi

phase1f_python_version="$("${phase1f_python_bin}" --version | awk '{print $2}')"
[[ "${phase1f_python_version}" == "${PHASE1F_EXPECTED_PYTHON_VERSION}" ]] || \
  fail "expected Python ${PHASE1F_EXPECTED_PYTHON_VERSION}, got ${phase1f_python_version}"

phase1f_uv_bin="$(command -v uv || true)"
[[ -n "${phase1f_uv_bin}" ]] || fail "uv is unavailable"
phase1f_uv_version="$("${phase1f_uv_bin}" --version | awk '{print $2}')"
[[ "${phase1f_uv_version}" == "${PHASE1F_EXPECTED_UV_VERSION}" ]] || \
  fail "expected uv ${PHASE1F_EXPECTED_UV_VERSION}, got ${phase1f_uv_version}"

[[ -r "${PHASE1F_PROJECT_ROOT}" ]] || fail "the Project Root is not readable"
[[ -w "${PHASE1F_PROJECT_ROOT}" ]] || fail "the Project Root is not writable"
if [[ -e "${phase1f_environment_path}" ]]; then
  [[ -r "${phase1f_environment_path}" ]] || fail "the environment path is not readable"
  [[ -w "${phase1f_environment_path}" ]] || fail "the environment path is not writable"
else
  [[ -w "$(dirname -- "${phase1f_environment_path}")" ]] || \
    fail "the environment parent path is not writable"
fi

phase1f_cpu_count="$("${phase1f_python_bin}" -c 'import os; print(os.cpu_count() or 0)')"
if [[ -n "${PHASE1F_PREFLIGHT_AVAILABLE_MEMORY_BYTES:-}" ]]; then
  phase1f_available_memory_bytes="${PHASE1F_PREFLIGHT_AVAILABLE_MEMORY_BYTES}"
else
  phase1f_available_memory_kib="$(
    awk '$1 == "MemAvailable:" {print $2}' /proc/meminfo
  )"
  [[ "${phase1f_available_memory_kib}" =~ ^[1-9][0-9]*$ ]] || \
    fail "available memory could not be observed"
  phase1f_available_memory_bytes="$((phase1f_available_memory_kib * 1024))"
fi
[[ "${phase1f_cpu_count}" =~ ^[1-9][0-9]*$ ]] || fail "CPU count could not be observed"
[[ "${phase1f_available_memory_bytes}" =~ ^[1-9][0-9]*$ ]] || \
  fail "available memory could not be observed"

phase1f_profile_status="not_applicable"
if [[ "${phase1f_runtime_target}" == "cpu-native" ]]; then
  [[ -r "${PHASE1F_CPU_NATIVE_PROFILE}" ]] || fail "the Pure CPU Profile is unavailable"
  "${phase1f_python_bin}" -c \
    'import pathlib, sys, tomllib
data = tomllib.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))
valid = (
    data["backend_runtime"]["build_variant_key"] == "cpu"
    and data["compute"]["compute_kind_key"] == "cpu"
    and data["compute"]["acceleration_api_key"] == "none"
    and data["load_overrides"]["gpu_layers"] == 0
    and data["runtime_requirements"]["fallback_policy"] == "deny"
)
raise SystemExit(0 if valid else 1)' \
    "${PHASE1F_CPU_NATIVE_PROFILE}" || fail "the Pure CPU Profile is invalid"
  phase1f_profile_status="parseable"
fi

phase1f_gpu_required="no"
phase1f_nvcc_status="not_probed"
if [[ "${phase1f_runtime_target}" == "cuda-gpu" ]]; then
  phase1f_gpu_required="yes"
  command -v nvidia-smi >/dev/null 2>&1 || fail "nvidia-smi is unavailable"
  nvidia-smi -L >/dev/null 2>&1 || fail "an allocated NVIDIA GPU was not detected"
fi
if [[ "${phase1f_runtime_target}" != "cpu-native" ]]; then
  phase1f_nvcc_status="no"
  if command -v nvcc >/dev/null 2>&1 && nvcc --version >/dev/null 2>&1; then
    phase1f_nvcc_status="yes"
  fi
fi

phase1f_model_root="${MARGPA_MODEL_ROOT:-${PHASE1F_PROJECT_ROOT}/models}"
phase1f_model_root_status="absent_optional"
if [[ -d "${phase1f_model_root}" ]]; then
  phase1f_model_root_status="present"
fi

printf 'Phase 1-F Lightning preflight passed.\n'
printf 'Runtime target   : %s\n' "${phase1f_runtime_target}"
printf 'Environment mode : %s\n' "${phase1f_environment_mode}"
printf 'Environment path : %s\n' "${phase1f_environment_path}"
printf 'Python           : %s (%s)\n' "${phase1f_python_bin}" "${phase1f_python_version}"
printf 'uv               : %s (%s)\n' "${phase1f_uv_bin}" "${phase1f_uv_version}"
printf 'CPU count        : %s\n' "${phase1f_cpu_count}"
printf 'Available memory : %s bytes\n' "${phase1f_available_memory_bytes}"
printf 'Pure CPU Profile : %s\n' "${phase1f_profile_status}"
printf 'GPU required     : %s\n' "${phase1f_gpu_required}"
printf 'nvcc available   : %s\n' "${phase1f_nvcc_status}"
printf 'Model Root       : %s (%s)\n' "${phase1f_model_root}" "${phase1f_model_root_status}"
