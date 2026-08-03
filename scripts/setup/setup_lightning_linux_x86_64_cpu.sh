#!/bin/bash

set -euo pipefail

readonly PHASE1F_PROJECT_ROOT="$(
  CDPATH= cd -- "$(dirname -- "$0")/../.." >/dev/null 2>&1
  pwd -P
)"
readonly PHASE1F_EXPECTED_UV_VERSION="0.11.29"
readonly PHASE1F_CPU_PROFILE="${PHASE1F_PROJECT_ROOT}/config/profiles/lightning_linux_x86_64_cpu_native.toml"
readonly PHASE1F_MODEL_REGISTRY="${PHASE1F_PROJECT_ROOT}/config/models/qwen3_4b_q4_k_m.toml"
readonly PHASE1F_DEFAULT_MODEL_ROOT="${PHASE1F_PROJECT_ROOT}/models"

phase1f_target_venv="${PHASE1F_PROJECT_ROOT}/.venv"
phase1f_environment_mode="auto"
phase1f_venv_explicit=0
phase1f_model_root="${MARGPA_MODEL_ROOT:-${PHASE1F_DEFAULT_MODEL_ROOT}}"
phase1f_model_root_explicit=0
phase1f_model_path=""
phase1f_model_path_explicit=0
phase1f_rebuild_native=0
phase1f_run_model_smoke=0
phase1f_plan_only=0
if [[ -n "${MARGPA_MODEL_ROOT:-}" ]]; then
  phase1f_model_root_explicit=1
fi

usage() {
  cat <<'EOF'
Usage: scripts/setup/setup_lightning_linux_x86_64_cpu.sh [options]

Reproduce the Phase 1-F Lightning Linux/x86_64 Pure CPU environment with
llama-cpp-python 0.3.34 built without an accelerator backend.

Options:
  --environment-mode MODE
                       auto, studio-active, or project-venv (default: auto)
  --venv PATH          Target for project-venv mode (default: project .venv)
  --rebuild-native     Force a new llama-cpp-python Pure CPU source build
  --model-smoke        Run the bounded Qwen3-4B Pure CPU acceptance probe
  --model-root PATH    Root containing the Registry-relative model artifact
  --model-path PATH    Compatibility option; PATH must exactly match the
                       Registry layout below the resolved Model Root
  --plan               Print the setup plan without changing the environment
  -h, --help           Show this help

Prerequisites:
  - Ubuntu Linux x86_64 running in a container
  - CPython >=3.12,<3.14 already available
  - uv 0.11.29 available on PATH
  - Network access only when dependencies or a native source build are absent
  - The local GGUF artifact only when --model-smoke is selected

The Registry determines the artifact path below --model-root. --model-path does
not override that path; it validates the same artifact and derives its root when
--model-root is omitted. The script prints the exact artifact used by smoke and
never downloads a model.

Normal dependency sync and native rebuilding are separate. A compatible
existing Pure CPU build is reused unless --rebuild-native is specified.
EOF
}

fail() {
  printf 'Phase 1-F Lightning Pure CPU setup failed: %s\n' "$1" >&2
  exit 1
}

resolve_model_location() {
  local resolver_python="$1"
  local resolution
  if ! resolution="$(
    "${resolver_python}" -c \
      'import pathlib, sys, tomllib
project_root = pathlib.Path(sys.argv[1]).resolve()
registry_path = pathlib.Path(sys.argv[2]).resolve()
root_value = sys.argv[3]
root_explicit = sys.argv[4] == "1"
path_value = sys.argv[5]
path_explicit = sys.argv[6] == "1"
if any("\n" in value or "\r" in value for value in (root_value, path_value)):
    raise SystemExit(2)
with registry_path.open("rb") as registry_file:
    relative = pathlib.Path(tomllib.load(registry_file)["artifact"]["relative_path"])
if relative.is_absolute() or ".." in relative.parts:
    raise SystemExit(3)
def resolve_input(value):
    path = pathlib.Path(value).expanduser()
    return (path if path.is_absolute() else project_root / path).resolve(strict=False)
specified_path = resolve_input(path_value) if path_explicit else None
if root_explicit or specified_path is None:
    model_root = resolve_input(root_value)
else:
    if len(specified_path.parts) <= len(relative.parts):
        raise SystemExit(4)
    if specified_path.parts[-len(relative.parts):] != relative.parts:
        raise SystemExit(5)
    model_root = pathlib.Path(*specified_path.parts[:-len(relative.parts)])
expected_path = (model_root / relative).resolve(strict=False)
try:
    expected_path.relative_to(model_root)
except ValueError:
    raise SystemExit(6)
if specified_path is not None and specified_path != expected_path:
    raise SystemExit(7)
print(model_root)
print(expected_path)' \
      "${PHASE1F_PROJECT_ROOT}" \
      "${PHASE1F_MODEL_REGISTRY}" \
      "${phase1f_model_root}" \
      "${phase1f_model_root_explicit}" \
      "${phase1f_model_path}" \
      "${phase1f_model_path_explicit}" \
      2>/dev/null
  )"; then
    fail "the Model Root/Path does not match the Registry artifact layout"
  fi
  phase1f_model_root="$(printf '%s\n' "${resolution}" | sed -n '1p')"
  phase1f_model_path="$(printf '%s\n' "${resolution}" | sed -n '2p')"
  [[ -n "${phase1f_model_root}" && -n "${phase1f_model_path}" ]] || \
    fail "the Model Root/Path could not be resolved"
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
    --model-smoke)
      phase1f_run_model_smoke=1
      shift
      ;;
    --model-root)
      (($# >= 2)) || fail "--model-root requires a path"
      phase1f_model_root="$2"
      phase1f_model_root_explicit=1
      shift 2
      ;;
    --model-path)
      (($# >= 2)) || fail "--model-path requires a path"
      phase1f_model_path="$2"
      phase1f_model_path_explicit=1
      shift 2
      ;;
    --plan)
      phase1f_plan_only=1
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

command -v python3 >/dev/null 2>&1 || fail "python3 is unavailable"
phase1f_resolution_python="$(command -v python3)"
resolve_model_location "${phase1f_resolution_python}"
if ((phase1f_run_model_smoke == 1)) && [[ ! -f "${phase1f_model_path}" ]]; then
  fail "the Registry-resolved local GGUF artifact does not exist: ${phase1f_model_path}"
fi

if ((phase1f_plan_only == 1)); then
  printf 'Phase 1-F Lightning Pure CPU setup plan (no changes).\n'
  printf '1. Validate Linux x86_64 container and Python >=3.12,<3.14.\n'
  printf '2. Validate uv %s and the frozen Project lock.\n' "${PHASE1F_EXPECTED_UV_VERSION}"
  printf '3. Sync Project dependencies without replacing the native backend.\n'
  printf '4. Reuse a verified Pure CPU backend or rebuild it explicitly.\n'
  printf '5. Verify target lightning-cpu-native.\n'
  printf 'Model Root       : %s\n' "${phase1f_model_root}"
  printf 'Resolved Artifact: %s\n' "${phase1f_model_path}"
  if ((phase1f_run_model_smoke == 1)); then
    printf '6. Run the bounded smoke with the resolved artifact above.\n'
  else
    printf '6. Skip model smoke unless --model-smoke is explicitly selected.\n'
  fi
  exit 0
fi

[[ "$(uname -s)" == "Linux" ]] || fail "this recipe is restricted to Linux"
[[ "$(uname -m)" == "x86_64" ]] || fail "this recipe requires an x86_64 host"
[[ -r /etc/os-release ]] || fail "/etc/os-release is unavailable"
phase1f_distribution="$(
  awk -F= '$1 == "ID" {gsub(/"/, "", $2); print tolower($2)}' /etc/os-release
)"
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
phase1f_uv_version="$("${phase1f_uv_bin}" --version | awk '{print $2}')"
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
phase1f_python_version="$("${phase1f_python_bin}" --version | awk '{print $2}')"
case "${phase1f_python_version}" in
  3.12.*|3.13.*) ;;
  *) fail "expected CPython >=3.12,<3.14, got ${phase1f_python_version}" ;;
esac

if [[ "${phase1f_environment_mode}" == "project-venv" ]]; then
  [[ "${phase1f_target_environment}" != "${PHASE1F_PROJECT_ROOT}" ]] || \
    fail "the target Venv must not be the Project Root"
  [[ -d "$(dirname -- "${phase1f_target_environment}")" ]] || \
    fail "the target Venv parent directory does not exist"
fi
cd "${PHASE1F_PROJECT_ROOT}"
"${phase1f_uv_bin}" lock --check

printf 'Project Root : %s\n' "${PHASE1F_PROJECT_ROOT}"
printf 'Environment  : %s\n' "${phase1f_environment_mode}"
printf 'Target Prefix: %s\n' "${phase1f_target_environment}"
printf 'uv           : %s (%s)\n' "${phase1f_uv_bin}" "${phase1f_uv_version}"
printf 'Python       : %s / Linux x86_64 / container\n' "${phase1f_python_version}"
printf 'Native Build : llama-cpp-python==0.3.34 / source / Pure CPU\n'
printf 'Model Root   : %s\n' "${phase1f_model_root}"
printf 'Model Artifact: %s\n' "${phase1f_model_path}"

phase1f_cpu_build_ready=0
if [[ -x "${phase1f_runtime_python}" ]] && \
  "${phase1f_runtime_python}" -c \
    'from llama_cpp import llama_cpp
info = llama_cpp.llama_print_system_info().decode("utf-8", errors="replace").upper()
accelerated = llama_cpp.llama_supports_gpu_offload() or any(
    marker in info for marker in ("GGML_CUDA", "CUDA :", "METAL", "ROCM", "HIP :")
)
raise SystemExit(0 if not accelerated else 1)' \
    >/dev/null 2>&1; then
  phase1f_cpu_build_ready=1
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

if ((phase1f_rebuild_native == 1 || phase1f_cpu_build_ready == 0)); then
  env \
    CMAKE_ARGS="-DGGML_CUDA=off -DGGML_METAL=off -DGGML_HIP=off" \
    CMAKE_BUILD_PARALLEL_LEVEL="${CMAKE_BUILD_PARALLEL_LEVEL:-4}" \
    "${phase1f_uv_bin}" pip install \
    --python "${phase1f_runtime_python}" \
    --no-binary llama-cpp-python \
    --reinstall-package llama-cpp-python \
    "llama-cpp-python==0.3.34"
else
  printf 'Native Build : reusing the existing verified Pure CPU build\n'
fi

"${phase1f_runtime_python}" -c \
  'from llama_cpp import llama_cpp
info = llama_cpp.llama_print_system_info().decode("utf-8", errors="replace").upper()
accelerated = llama_cpp.llama_supports_gpu_offload() or any(
    marker in info for marker in ("GGML_CUDA", "CUDA :", "METAL", "ROCM", "HIP :")
)
raise SystemExit(0 if not accelerated else 1)' \
  >/dev/null 2>&1 || fail "the target environment is not a verified Pure CPU build"

"${phase1f_runtime_python}" scripts/setup/verify_phase1_environment.py \
  --target lightning-cpu-native

if ((phase1f_run_model_smoke == 1)); then
  printf 'Smoke Artifact: %s\n' "${phase1f_model_path}"
  "${phase1f_runtime_python}" \
    scripts/models/phase1f_cross_environment_acceptance.py \
    --profile "${PHASE1F_CPU_PROFILE}" \
    --model-root "${phase1f_model_root}"
fi

printf 'Phase 1-F Lightning Linux/x86_64 Pure CPU setup completed successfully.\n'
