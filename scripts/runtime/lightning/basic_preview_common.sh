#!/bin/bash

# Shared, source-only helpers for the Phase 1-ex Lightning Basic Preview tools.

margpa_common_directory="$(
  CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" >/dev/null 2>&1
  pwd -P
)"
margpa_detected_project_root="$(
  CDPATH= cd -- "${margpa_common_directory}/../../.." >/dev/null 2>&1
  pwd -P
)"
readonly MARGPA_STATE_DIRECTORY_NAME="basic-preview"
readonly MARGPA_STATE_MARKER_NAME=".margpa-basic-preview-state"
readonly MARGPA_STATE_MARKER_VALUE="margpa-runtime-llm-basic-preview-state-v1"
readonly MARGPA_LOCK_DIRECTORY_NAME=".margpa-runtime-llm-basic-preview.lifecycle.lock"
readonly MARGPA_LOCK_OWNER_NAME="owner.pid"
readonly MARGPA_LOCK_OWNER_VALUE="margpa-runtime-llm-basic-preview-lock-v1"

margpa_fail() {
  local check_name="$1"
  local reason="$2"
  printf 'check.%s=fail reason=%s\n' "${check_name}" "${reason}" >&2
  return 1
}

margpa_check_no_linebreak() {
  local value
  for value in "$@"; do
    case "${value}" in
      *$'\n'*|*$'\r'*) return 1 ;;
    esac
  done
}

margpa_resolve_future_directory() {
  local candidate="$1"
  local unresolved_suffix=""
  local parent
  local leaf
  while [[ ! -e "${candidate}" ]]; do
    parent="$(dirname -- "${candidate}")"
    leaf="$(basename -- "${candidate}")"
    if [[ "${parent}" == "${candidate}" ]]; then
      return 1
    fi
    unresolved_suffix="/${leaf}${unresolved_suffix}"
    candidate="${parent}"
  done
  if [[ ! -d "${candidate}" ]]; then
    return 1
  fi
  candidate="$(
    CDPATH= cd -- "${candidate}" >/dev/null 2>&1
    pwd -P
  )"
  printf '%s%s\n' "${candidate}" "${unresolved_suffix}"
}

margpa_path_has_symlink_component() {
  local candidate="$1"
  while [[ "${candidate}" != "/" ]]; do
    if [[ -L "${candidate}" ]]; then
      return 0
    fi
    candidate="$(dirname -- "${candidate}")"
  done
  return 1
}

margpa_path_is_same_or_parent() {
  local candidate="$1"
  local target="$2"
  [[ "${candidate}" == "${target}" ]] && return 0
  case "${target}/" in
    "${candidate}/"*) return 0 ;;
  esac
  return 1
}

margpa_path_is_same_or_descendant() {
  local candidate="$1"
  local target="$2"
  [[ "${candidate}" == "${target}" ]] && return 0
  case "${candidate}/" in
    "${target}/"*) return 0 ;;
  esac
  return 1
}

margpa_file_mode() {
  local path="$1"
  local mode
  if mode="$(stat -f '%Lp' "${path}" 2>/dev/null)"; then
    printf '%s\n' "${mode}"
    return 0
  fi
  stat -c '%a' "${path}" 2>/dev/null
}

margpa_validate_runtime_state_location() {
  if margpa_path_has_symlink_component "${margpa_runtime_state_requested}"; then
    margpa_fail "runtime_state_root" "symlink_component_not_allowed"
    return 1
  fi
  if [[ "$(basename -- "${margpa_runtime_state_requested}")" != "${MARGPA_STATE_DIRECTORY_NAME}" ]]; then
    margpa_fail "runtime_state_root" "dedicated_directory_name_required"
    return 1
  fi

  local home_root=""
  if [[ -n "${HOME:-}" && -d "${HOME}" ]]; then
    home_root="$(
      CDPATH= cd -- "${HOME}" >/dev/null 2>&1
      pwd -P
    )"
  fi
  local protected_root
  for protected_root in \
    "/" \
    "${home_root}" \
    "${margpa_workspace_root}" \
    "${margpa_project_root}" \
    "${margpa_model_root}" \
    "${margpa_environment_prefix}"; do
    [[ -n "${protected_root}" ]] || continue
    if margpa_path_is_same_or_parent "${margpa_runtime_state_root}" "${protected_root}"; then
      margpa_fail "runtime_state_root" "broad_or_protected_directory"
      return 1
    fi
  done

  for protected_root in \
    "${margpa_project_root}" \
    "${margpa_model_root}" \
    "${margpa_environment_prefix}"; do
    if margpa_path_is_same_or_descendant "${margpa_runtime_state_root}" "${protected_root}"; then
      margpa_fail "runtime_state_root" "protected_tree_not_allowed"
      return 1
    fi
  done
}

margpa_validate_regular_file_or_absent() {
  local path="$1"
  local check_name="$2"
  if [[ -L "${path}" ]]; then
    margpa_fail "${check_name}" "symlink_not_allowed"
    return 1
  fi
  if [[ -e "${path}" && ! -f "${path}" ]]; then
    margpa_fail "${check_name}" "regular_file_required"
    return 1
  fi
}

margpa_validate_state_artifacts() {
  if [[ ! -e "${margpa_runtime_state_root}" ]]; then
    return 0
  fi
  if [[ -L "${margpa_runtime_state_root}" || ! -d "${margpa_runtime_state_root}" ]]; then
    margpa_fail "runtime_state_root" "owned_directory_required"
    return 1
  fi
  if [[ ! -r "${margpa_runtime_state_root}" ||
    ! -w "${margpa_runtime_state_root}" ||
    ! -x "${margpa_runtime_state_root}" ]]; then
    margpa_fail "runtime_state_root" "owned_directory_not_accessible"
    return 1
  fi
  if [[ ! -f "${margpa_state_marker_file}" || -L "${margpa_state_marker_file}" ]]; then
    margpa_fail "runtime_state_root" "ownership_marker_required"
    return 1
  fi
  if [[ "$(sed -n '1p' "${margpa_state_marker_file}")" != "${MARGPA_STATE_MARKER_VALUE}" ]]; then
    margpa_fail "runtime_state_root" "ownership_marker_invalid"
    return 1
  fi
  if [[ "$(margpa_file_mode "${margpa_runtime_state_root}")" != "700" ]]; then
    margpa_fail "runtime_state_root" "owned_directory_mode_must_be_700"
    return 1
  fi
  if [[ "$(margpa_file_mode "${margpa_state_marker_file}")" != "600" ]]; then
    margpa_fail "runtime_state_root" "ownership_marker_mode_must_be_600"
    return 1
  fi
  margpa_validate_regular_file_or_absent "${margpa_pid_file}" "pid_file" || return 1
  margpa_validate_regular_file_or_absent "${margpa_log_file}" "log_file" || return 1
  if [[ -e "${margpa_pid_file}" && "$(margpa_file_mode "${margpa_pid_file}")" != "600" ]]; then
    margpa_fail "pid_file" "mode_must_be_600"
    return 1
  fi
  if [[ -e "${margpa_log_file}" && "$(margpa_file_mode "${margpa_log_file}")" != "600" ]]; then
    margpa_fail "log_file" "mode_must_be_600"
    return 1
  fi
}

margpa_validate_lock_artifact() {
  if [[ -L "${margpa_lock_directory}" ]]; then
    margpa_fail "lifecycle_lock" "symlink_not_allowed"
    return 1
  fi
  if [[ -e "${margpa_lock_directory}" && ! -d "${margpa_lock_directory}" ]]; then
    margpa_fail "lifecycle_lock" "directory_required"
    return 1
  fi
  if [[ -d "${margpa_lock_directory}" ]]; then
    if [[ ! -r "${margpa_lock_directory}" ||
      ! -w "${margpa_lock_directory}" ||
      ! -x "${margpa_lock_directory}" ]]; then
      margpa_fail "lifecycle_lock" "directory_not_accessible"
      return 1
    fi
    if [[ "$(margpa_file_mode "${margpa_lock_directory}")" != "700" ]]; then
      margpa_fail "lifecycle_lock" "directory_mode_must_be_700"
      return 1
    fi
    margpa_validate_regular_file_or_absent "${margpa_lock_owner_file}" "lifecycle_lock" ||
      return 1
    if [[ -e "${margpa_lock_owner_file}" &&
      "$(margpa_file_mode "${margpa_lock_owner_file}")" != "600" ]]; then
      margpa_fail "lifecycle_lock" "owner_mode_must_be_600"
      return 1
    fi
  fi
}

margpa_resolve_core_configuration() {
  local project_candidate="${MARGPA_PROJECT_ROOT:-${margpa_detected_project_root}}"
  if [[ ! -d "${project_candidate}" ]]; then
    margpa_fail "project_root" "directory_unavailable"
    return 1
  fi
  margpa_project_root="$(
    CDPATH= cd -- "${project_candidate}" >/dev/null 2>&1
    pwd -P
  )"

  local workspace_candidate="${MARGPA_WORKSPACE_ROOT:-}"
  if [[ -z "${workspace_candidate}" ]]; then
    workspace_candidate="$(dirname -- "${margpa_project_root}")"
  fi
  if [[ ! -d "${workspace_candidate}" ]]; then
    margpa_fail "workspace_root" "directory_unavailable"
    return 1
  fi
  margpa_workspace_root="$(
    CDPATH= cd -- "${workspace_candidate}" >/dev/null 2>&1
    pwd -P
  )"
  if [[ "${margpa_workspace_root}" == "/" ]]; then
    margpa_fail "workspace_root" "filesystem_root_not_allowed"
    return 1
  fi

  local model_candidate="${MARGPA_MODEL_ROOT:-${margpa_workspace_root}/models}"
  case "${model_candidate}" in
    /*) ;;
    *) model_candidate="${margpa_workspace_root}/${model_candidate}" ;;
  esac
  if [[ -d "${model_candidate}" ]]; then
    margpa_model_root="$(
      CDPATH= cd -- "${model_candidate}" >/dev/null 2>&1
      pwd -P
    )"
  else
    margpa_model_root="${model_candidate}"
  fi

  local environment_candidate="${MARGPA_ENV_PREFIX:-${margpa_project_root}/.venv}"
  case "${environment_candidate}" in
    /*) ;;
    *) environment_candidate="${margpa_project_root}/${environment_candidate}" ;;
  esac
  if [[ -d "${environment_candidate}" ]]; then
    margpa_environment_prefix="$(
      CDPATH= cd -- "${environment_candidate}" >/dev/null 2>&1
      pwd -P
    )"
  else
    margpa_environment_prefix="${environment_candidate}"
  fi

  local uv_candidate="${MARGPA_UV_BIN:-${margpa_workspace_root}/.runtime-tools/uv/0.11.29/bin}"
  if [[ -d "${uv_candidate}" ]]; then
    margpa_uv_bin="${uv_candidate}/uv"
  else
    margpa_uv_bin="${uv_candidate}"
  fi

  margpa_web_host="${MARGPA_WEB_HOST:-0.0.0.0}"
  margpa_web_port="${MARGPA_WEB_PORT:-8000}"

  local profile_candidate="${MARGPA_WEB_PROFILE:-${margpa_project_root}/config/profiles/lightning_linux_x86_64_cpu_native.toml}"
  case "${profile_candidate}" in
    /*) ;;
    *) profile_candidate="${margpa_project_root}/${profile_candidate}" ;;
  esac
  margpa_web_profile="${profile_candidate}"

  local access_profile_candidate="${MARGPA_WEB_ACCESS_PROFILE:-${margpa_project_root}/config/web_profiles/basic_preview.toml}"
  case "${access_profile_candidate}" in
    /*) ;;
    *) access_profile_candidate="${margpa_project_root}/${access_profile_candidate}" ;;
  esac
  margpa_web_access_profile="${access_profile_candidate}"

  local documentation_rag_profile_candidate="${MARGPA_DOCUMENTATION_RAG_PROFILE:-${margpa_project_root}/config/feature_profiles/lightning_public_documentation_rag.toml}"
  if ! margpa_check_no_linebreak "${documentation_rag_profile_candidate}"; then
    margpa_fail "documentation_rag_profile" "linebreak_not_allowed"
    return 1
  fi
  case "${documentation_rag_profile_candidate}" in
    ../*|./*|*/../*|*/..|*/./*|*/.|*\\*)
      margpa_fail "documentation_rag_profile" "dot_segments_not_allowed"
      return 1
      ;;
  esac
  case "${documentation_rag_profile_candidate}" in
    /*) ;;
    *) documentation_rag_profile_candidate="${margpa_project_root}/${documentation_rag_profile_candidate}" ;;
  esac
  if [[ -L "${documentation_rag_profile_candidate}" ||
    ! -f "${documentation_rag_profile_candidate}" ||
    ! -r "${documentation_rag_profile_candidate}" ]]; then
    margpa_fail "documentation_rag_profile" "readable_regular_file_required"
    return 1
  fi
  if margpa_path_has_symlink_component "${documentation_rag_profile_candidate}"; then
    margpa_fail "documentation_rag_profile" "symlink_component_not_allowed"
    return 1
  fi
  local documentation_rag_profile_parent
  documentation_rag_profile_parent="$(
    CDPATH= cd -- "$(dirname -- "${documentation_rag_profile_candidate}")" >/dev/null 2>&1
    pwd -P
  )"
  margpa_documentation_rag_profile="${documentation_rag_profile_parent}/$(basename -- "${documentation_rag_profile_candidate}")"
  if ! margpa_path_is_same_or_descendant \
    "${margpa_documentation_rag_profile}" \
    "${margpa_project_root}"; then
    margpa_fail "documentation_rag_profile" "project_root_boundary_required"
    return 1
  fi

  local registry_candidate="${MARGPA_MODEL_DEFINITION:-${margpa_project_root}/config/models/qwen3_4b_q4_k_m.toml}"
  case "${registry_candidate}" in
    /*) ;;
    *) registry_candidate="${margpa_project_root}/${registry_candidate}" ;;
  esac
  margpa_registry_path="${registry_candidate}"
  margpa_model_key="${MARGPA_MODEL_KEY:-}"
  margpa_context_size="${MARGPA_CONTEXT_SIZE:-}"
  margpa_health_source="${margpa_project_root}/src/margpa_runtime_llm/web/app.py"
  margpa_python_bin="${margpa_environment_prefix}/bin/python"
  margpa_web_bin="${margpa_environment_prefix}/bin/margpa-web"

  if ! margpa_check_no_linebreak \
    "${margpa_project_root}" \
    "${margpa_workspace_root}" \
    "${margpa_model_root}" \
    "${margpa_environment_prefix}" \
    "${margpa_uv_bin}" \
    "${margpa_web_host}" \
    "${margpa_web_port}" \
    "${margpa_web_profile}" \
    "${margpa_web_access_profile}" \
    "${margpa_documentation_rag_profile}" \
    "${margpa_registry_path}" \
    "${margpa_model_key}" \
    "${margpa_context_size}"; then
    margpa_fail "configuration" "linebreak_not_allowed"
    return 1
  fi

  if [[ ! "${margpa_web_port}" =~ ^[0-9]+$ ]] ||
    ((margpa_web_port < 1 || margpa_web_port > 65535)); then
    margpa_fail "web_port" "invalid_port"
    return 1
  fi
  if [[ -n "${margpa_context_size}" ]] &&
    { [[ ! "${margpa_context_size}" =~ ^[1-9][0-9]*$ ]]; }; then
    margpa_fail "context_size" "invalid_positive_integer"
    return 1
  fi
}

margpa_resolve_lifecycle_configuration() {
  margpa_runtime_state_is_default=0
  if [[ -z "${MARGPA_RUNTIME_STATE_ROOT:-}" ]]; then
    margpa_runtime_state_is_default=1
  fi
  local state_candidate="${MARGPA_RUNTIME_STATE_ROOT:-${margpa_workspace_root}/.runtime-state/margpa-runtime-llm/basic-preview}"
  case "${state_candidate}" in
    /*) ;;
    *) state_candidate="${margpa_workspace_root}/${state_candidate}" ;;
  esac
  case "${state_candidate}" in
    */../*|*/..|*/./*|*/.)
      margpa_fail "runtime_state_root" "dot_segments_not_allowed"
      return 1
      ;;
  esac
  margpa_runtime_state_requested="${state_candidate}"
  if ! margpa_runtime_state_root="$(margpa_resolve_future_directory "${state_candidate}")"; then
    margpa_fail "runtime_state_root" "invalid_directory_path"
    return 1
  fi

  margpa_pid_file="${margpa_runtime_state_root}/basic-preview.pid"
  margpa_log_file="${margpa_runtime_state_root}/basic-preview.log"
  margpa_state_marker_file="${margpa_runtime_state_root}/${MARGPA_STATE_MARKER_NAME}"
  margpa_lock_directory="${margpa_workspace_root}/${MARGPA_LOCK_DIRECTORY_NAME}"
  margpa_lock_owner_file="${margpa_lock_directory}/${MARGPA_LOCK_OWNER_NAME}"
  margpa_health_timeout="${MARGPA_HEALTH_TIMEOUT_SECONDS:-30}"
  margpa_stop_timeout="${MARGPA_STOP_TIMEOUT_SECONDS:-15}"

  if ! margpa_check_no_linebreak "${margpa_runtime_state_root}"; then
    margpa_fail "configuration" "linebreak_not_allowed"
    return 1
  fi
  if [[ ! "${margpa_health_timeout}" =~ ^[1-9][0-9]*$ ]]; then
    margpa_fail "health_timeout" "invalid_positive_integer"
    return 1
  fi
  if [[ ! "${margpa_stop_timeout}" =~ ^[1-9][0-9]*$ ]]; then
    margpa_fail "stop_timeout" "invalid_positive_integer"
    return 1
  fi
  margpa_validate_runtime_state_location || return 1
  margpa_validate_state_artifacts || return 1
  margpa_validate_lock_artifact || return 1
}

margpa_resolve_configuration() {
  margpa_resolve_core_configuration || return 1
  margpa_resolve_lifecycle_configuration
}

margpa_detect_container() {
  case "${MARGPA_LIGHTNING_CONTAINER_MARKER:-auto}" in
    present) return 0 ;;
    absent) return 1 ;;
    auto) ;;
    *) return 1 ;;
  esac
  if [[ -e /.dockerenv || -e /run/.containerenv || -n "${container:-}" ]]; then
    return 0
  fi
  if [[ -r /proc/1/cgroup ]]; then
    local cgroup
    cgroup="$(</proc/1/cgroup)"
    case "${cgroup}" in
      *docker*|*containerd*|*kubepods*|*libpod*|*lxc*) return 0 ;;
    esac
  fi
  return 1
}

margpa_common_preflight_checks() {
  if [[ "$(uname -s)" != "Linux" ]]; then
    margpa_fail "host_platform" "linux_required"
    return 1
  fi
  if [[ "$(uname -m)" != "x86_64" ]]; then
    margpa_fail "host_platform" "x86_64_required"
    return 1
  fi
  if ! margpa_detect_container; then
    margpa_fail "execution_environment" "container_required"
    return 1
  fi
  printf 'check.host_platform=pass value=linux_x86_64_container\n'

  local os_release_path="${MARGPA_LIGHTNING_OS_RELEASE_PATH:-/etc/os-release}"
  if [[ ! -r "${os_release_path}" ]]; then
    margpa_fail "distribution" "os_release_unavailable"
    return 1
  fi
  local distribution
  distribution="$(
    awk -F= '$1 == "ID" {gsub(/"/, "", $2); print tolower($2)}' \
      "${os_release_path}"
  )"
  if [[ "${distribution}" != "ubuntu" ]]; then
    margpa_fail "distribution" "ubuntu_required"
    return 1
  fi
  printf 'check.distribution=pass value=ubuntu\n'

  if [[ ! -r "${margpa_project_root}" ]]; then
    margpa_fail "project_root" "not_readable"
    return 1
  fi
  if [[ ! -d "${margpa_model_root}" ]]; then
    margpa_fail "model_root" "directory_unavailable"
    return 1
  fi
  if [[ ! -d "${margpa_environment_prefix}" || ! -x "${margpa_python_bin}" ]]; then
    margpa_fail "environment_prefix" "python_environment_unavailable"
    return 1
  fi
  printf 'check.project_root=pass path=%s\n' "${margpa_project_root}"
  printf 'check.model_root=pass path=%s\n' "${margpa_model_root}"
  printf 'check.environment_prefix=pass path=%s\n' "${margpa_environment_prefix}"

  local python_version
  python_version="$(
    env PYTHONDONTWRITEBYTECODE=1 "${margpa_python_bin}" --version 2>&1 |
      awk '{print $2}'
  )"
  case "${python_version}" in
    3.12.*|3.13.*) ;;
    *)
      margpa_fail "python_version" "unsupported_version"
      return 1
      ;;
  esac
  printf 'check.python_version=pass value=%s\n' "${python_version}"

  if [[ ! -x "${margpa_uv_bin}" ]]; then
    margpa_fail "uv" "executable_unavailable"
    return 1
  fi
  local uv_version
  uv_version="$("${margpa_uv_bin}" --version 2>/dev/null | awk '{print $2}')"
  if [[ "${uv_version}" != "0.11.29" ]]; then
    margpa_fail "uv" "unexpected_version"
    return 1
  fi
  printf 'check.uv=pass path=%s version=%s\n' "${margpa_uv_bin}" "${uv_version}"

  if [[ ! -x "${margpa_web_bin}" ]]; then
    margpa_fail "margpa_web" "executable_unavailable"
    return 1
  fi
  printf 'check.margpa_web=pass path=%s\n' "${margpa_web_bin}"

  if [[ ! -r "${margpa_web_profile}" ]]; then
    margpa_fail "deployment_profile" "file_unavailable"
    return 1
  fi
  if ! env PYTHONDONTWRITEBYTECODE=1 "${margpa_python_bin}" -c \
    'import pathlib, sys, tomllib
data = tomllib.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))
required_top_level = {
    "schema_version",
    "profile_key",
    "verification_state",
    "host",
    "compute",
    "backend_runtime",
    "runtime_requirements",
    "load_overrides",
}
section_names = {
    "host",
    "compute",
    "backend_runtime",
    "runtime_requirements",
    "load_overrides",
}
valid = (
    set(data) == required_top_level
    and data["schema_version"] == "3"
    and isinstance(data["profile_key"], str)
    and bool(data["profile_key"].strip())
    and all(isinstance(data[name], dict) for name in section_names)
)
raise SystemExit(0 if valid else 1)' \
    "${margpa_web_profile}" >/dev/null 2>&1; then
    margpa_fail "deployment_profile" "invalid_profile_contract"
    return 1
  fi
  printf 'check.deployment_profile=pass path=%s\n' "${margpa_web_profile}"

  if [[ ! -r "${margpa_registry_path}" ]]; then
    margpa_fail "model_registry" "file_unavailable"
    return 1
  fi
  if ! margpa_model_artifact="$(
    env PYTHONDONTWRITEBYTECODE=1 "${margpa_python_bin}" -c \
      'import pathlib, sys, tomllib
root = pathlib.Path(sys.argv[1]).resolve()
registry = pathlib.Path(sys.argv[2])
with registry.open("rb") as registry_file:
    relative = pathlib.Path(tomllib.load(registry_file)["artifact"]["relative_path"])
if relative.is_absolute() or ".." in relative.parts:
    raise SystemExit(2)
artifact = (root / relative).resolve()
try:
    artifact.relative_to(root)
except ValueError:
    raise SystemExit(3)
if not artifact.is_file():
    raise SystemExit(4)
print(artifact)' \
      "${margpa_model_root}" "${margpa_registry_path}" 2>/dev/null
  )"; then
    margpa_fail "model_artifact" "registry_layout_or_file_invalid"
    return 1
  fi
  printf 'check.model_artifact=pass path=%s\n' "${margpa_model_artifact}"

  if [[ ! -r "${margpa_health_source}" ]] ||
    ! grep -F '@app.get("/healthz")' "${margpa_health_source}" >/dev/null ||
    ! grep -F 'return {"status": "ok"}' "${margpa_health_source}" >/dev/null; then
    margpa_fail "health_contract" "expected_contract_unavailable"
    return 1
  fi
  printf 'check.health_contract=pass expected_http=200 expected_body_status=ok\n'

  if [[ -z "${margpa_web_host}" ]]; then
    margpa_fail "web_bind" "host_unavailable"
    return 1
  fi
  printf 'check.web_bind=pass host=%s port=%s\n' \
    "${margpa_web_host}" "${margpa_web_port}"

}

margpa_validate_lifecycle_preflight() {
  local writable_state_ancestor="${margpa_runtime_state_root}"
  while [[ ! -e "${writable_state_ancestor}" ]]; do
    writable_state_ancestor="$(dirname -- "${writable_state_ancestor}")"
  done
  if [[ ! -d "${writable_state_ancestor}" || ! -w "${writable_state_ancestor}" ]]; then
    margpa_fail "runtime_state_root" "ancestor_not_writable"
    return 1
  fi
  if ! command -v curl >/dev/null 2>&1; then
    margpa_fail "health_client" "curl_unavailable"
    return 1
  fi
  printf 'check.runtime_state_root=pass path=%s\n' "${margpa_runtime_state_root}"
  printf 'check.health_client=pass command=curl\n'
}

margpa_project_preflight() {
  margpa_resolve_configuration || return 1
  margpa_common_preflight_checks || return 1
  margpa_validate_lifecycle_preflight
}

margpa_stateless_project_preflight() {
  margpa_resolve_core_configuration || return 1
  margpa_common_preflight_checks
}

margpa_validate_pure_cpu_deployment_profile() {
  if ! env PYTHONDONTWRITEBYTECODE=1 "${margpa_python_bin}" -c \
    'import pathlib, sys, tomllib
data = tomllib.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))
valid = (
    data["profile_key"] == "external.lightning-linux-x86_64.cpu-native"
    and data["backend_runtime"]["build_variant_key"] == "cpu"
    and data["compute"]["acceleration_api_key"] == "none"
    and data["load_overrides"]["gpu_layers"] == 0
    and data["runtime_requirements"]["fallback_policy"] == "deny"
)
raise SystemExit(0 if valid else 1)' \
    "${margpa_web_profile}" >/dev/null 2>&1; then
    margpa_fail "deployment_profile" "invalid_pure_cpu_profile"
    return 1
  fi
  printf 'check.deployment_contract=pass mode=lightning_pure_cpu\n'
}

margpa_validate_web_access_profile() {
  local expected_mode="$1"
  if [[ ! -r "${margpa_web_access_profile}" ]]; then
    margpa_fail "web_access_profile" "file_unavailable"
    return 1
  fi
  if ! env PYTHONDONTWRITEBYTECODE=1 "${margpa_python_bin}" -c \
    'import pathlib, sys, tomllib
data = tomllib.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))
expected = sys.argv[2]
expected_auth = {"basic_preview": "basic", "public_demo": "none"}[expected]
expected_rag = "eligible"
control_names = {
    "rate_limit",
    "generation_budget",
    "cooldown",
    "public_max_new_tokens",
    "request_quota",
    "cost_guard",
}
valid = (
    data["schema_version"] == "1"
    and data["profile_key"] == expected
    and data["access"]["mode"] == expected
    and data["access"]["authentication"] == expected_auth
    and data["access"]["non_loopback_allowed"] is True
    and data["features"]["documentation_rag"] == expected_rag
    and set(data["controls"]) == control_names
    and all(data["controls"][name]["mode"] == "off" for name in control_names)
)
raise SystemExit(0 if valid else 1)' \
    "${margpa_web_access_profile}" "${expected_mode}" >/dev/null 2>&1; then
    margpa_fail "web_access_profile" "invalid_profile_contract"
    return 1
  fi
  printf 'check.web_access_profile=pass mode=%s\n' "${expected_mode}"
}

margpa_validate_documentation_rag_profile() {
  local expected_access_mode="$1"
  local readiness
  if ! readiness="$(
    env PYTHONDONTWRITEBYTECODE=1 "${margpa_python_bin}" -c \
      'import pathlib, sys, tomllib
profile_path = pathlib.Path(sys.argv[1])
project_root = pathlib.Path(sys.argv[2]).resolve(strict=True)
expected_access_mode = sys.argv[3]
with profile_path.open("rb") as profile_file:
    data = tomllib.load(profile_file)
expected_files = [
    "docs/public/overview_ja.md",
    "docs/public/overview_en.md",
    "docs/public/concept_ja.md",
    "docs/public/concept_en.md",
    "docs/public/roadmap_ja.md",
    "docs/public/roadmap_en.md",
    "docs/public/technology_selection_ja.md",
    "docs/public/technology_selection_en.md",
]
expected_top_level = {
    "schema_version",
    "profile_key",
    "mode",
    "provider_key",
    "provider_display_name",
    "allowed_access_modes",
    "allowed_platforms",
    "corpus",
    "limits",
    "chunking",
    "retrieval",
    "context",
}
valid = (
    set(data) == expected_top_level
    and data["schema_version"] == "2"
    and data["profile_key"]
    == "external.lightning-public-corpus.documentation-rag.lexical"
    and data["mode"] == "enabled"
    and data["provider_key"] == "project_filesystem_lexical"
    and isinstance(data["provider_display_name"], str)
    and bool(data["provider_display_name"].strip())
    and data["allowed_access_modes"] == ["basic_preview", "public_demo"]
    and expected_access_mode in data["allowed_access_modes"]
    and data["allowed_platforms"] == ["linux-x86_64-container"]
    and data["corpus"] == {
        "selection_mode": "explicit_files",
        "files": expected_files,
        "include_history": False,
        "include_lossless": False,
    }
    and set(data["limits"])
    == {"max_documents", "max_file_bytes", "max_corpus_bytes", "max_chunks"}
    and data["limits"]["max_documents"] >= len(expected_files)
    and set(data["chunking"])
    == {"target_characters", "overlap_characters", "maximum_characters"}
    and set(data["retrieval"])
    == {
        "top_k",
        "max_chunks_per_document",
        "minimum_score",
        "bm25_k1",
        "bm25_b",
        "body_weight",
        "heading_weight",
        "path_weight",
        "exact_phrase_bonus",
        "corpus_priority_weight",
    }
    and set(data["context"])
    == {
        "maximum_tokens",
        "minimum_useful_tokens",
        "safety_margin_tokens",
        "fallback_maximum_characters",
    }
)
if not valid:
    raise SystemExit(2)
present = 0
missing = 0
for relative_text in expected_files:
    relative = pathlib.PurePosixPath(relative_text)
    if relative.is_absolute() or ".." in relative.parts or "\\" in relative_text:
        raise SystemExit(3)
    candidate = project_root
    for part in relative.parts:
        candidate = candidate / part
        if candidate.is_symlink():
            raise SystemExit(4)
    if not candidate.exists():
        missing += 1
        continue
    if not candidate.is_file():
        raise SystemExit(5)
    candidate.resolve(strict=True).relative_to(project_root)
    present += 1
print(f"expected={len(expected_files)} present={present} missing={missing}")' \
      "${margpa_documentation_rag_profile}" \
      "${margpa_project_root}" \
      "${expected_access_mode}" 2>/dev/null
  )"; then
    margpa_fail "documentation_rag_profile" "invalid_profile_or_corpus_boundary"
    return 1
  fi
  printf 'check.documentation_rag_profile=pass mode=%s path=%s\n' \
    "${expected_access_mode}" \
    "${margpa_documentation_rag_profile}"
  printf 'check.documentation_corpus_readiness=pass %s\n' "${readiness}"
  MARGPA_DOCUMENTATION_RAG_PROFILE="${margpa_documentation_rag_profile}"
  export MARGPA_DOCUMENTATION_RAG_PROFILE
}

margpa_validate_credentials() {
  if [[ "${MARGPA_WEB_AUTH_MODE:-}" != "basic" ]]; then
    margpa_fail "credentials" "basic_auth_mode_required"
    return 1
  fi
  local validation_status=0
  env PYTHONDONTWRITEBYTECODE=1 "${margpa_python_bin}" -c \
    'import os
username = os.environ.get("MARGPA_WEB_AUTH_USERNAME")
password = os.environ.get("MARGPA_WEB_AUTH_PASSWORD")
if username is None or not username.strip():
    raise SystemExit(11)
if password is None or not password.strip():
    raise SystemExit(12)
if ":" in username or "\r" in username or "\n" in username:
    raise SystemExit(13)
if "\r" in password or "\n" in password:
    raise SystemExit(14)' >/dev/null 2>&1 || validation_status=$?
  case "${validation_status}" in
    0) ;;
    11)
      margpa_fail "credentials" "username_required"
      return 1
      ;;
    12)
      margpa_fail "credentials" "password_required"
      return 1
      ;;
    13)
      margpa_fail "credentials" "username_format_invalid"
      return 1
      ;;
    14)
      margpa_fail "credentials" "password_format_invalid"
      return 1
      ;;
    *)
      margpa_fail "credentials" "validation_unavailable"
      return 1
      ;;
  esac
  printf 'check.credentials=pass source=environment values=redacted\n'
}

margpa_validate_basic_preview_contract() {
  margpa_validate_pure_cpu_deployment_profile || return 1
  margpa_validate_web_access_profile "basic_preview" || return 1
  margpa_validate_documentation_rag_profile "basic_preview" || return 1
  margpa_validate_credentials || return 1
  printf 'check.access_boundary=pass mode=basic_preview public_demo=false\n'
  printf 'check.documentation_rag=pass capability=eligible default=disabled\n'
  printf 'check.launch_contract=pass credentials=environment_only\n'
}

margpa_validate_public_demo_contract() {
  margpa_validate_web_access_profile "public_demo" || return 1
  margpa_validate_documentation_rag_profile "public_demo" || return 1
  printf 'check.access_boundary=pass mode=public_demo authentication=none\n'
  printf 'check.documentation_rag=pass capability=eligible default=disabled\n'
  printf 'check.public_controls=pass mode=off\n'
  printf 'check.launch_contract=pass credentials=not_used\n'
}

margpa_build_web_arguments() {
  margpa_web_arguments=(
    --host "${margpa_web_host}"
    --port "${margpa_web_port}"
    --profile "${margpa_web_profile}"
    --access-profile "${margpa_web_access_profile}"
    --documentation-rag-profile "${margpa_documentation_rag_profile}"
    --registry "${margpa_registry_path}"
    --model-root "${margpa_model_root}"
  )
  if [[ -n "${margpa_model_key}" ]]; then
    margpa_web_arguments+=(--model-key "${margpa_model_key}")
  fi
  if [[ -n "${margpa_context_size}" ]]; then
    margpa_web_arguments+=(--context-size "${margpa_context_size}")
  fi
}

margpa_emit_manual_checklist() {
  cat <<'EOF'
status_values=pass,fail,not_run,manual_required,unknown
manual.platform_validation=not_run
manual.api_builder_availability=manual_required
manual.traffic_aware_auto_start=manual_required
manual.machine_and_credit=manual_required
manual.public_url_issuance=manual_required
manual.sleeping_studio_wake_up=manual_required
manual.startup_command_execution=manual_required
manual.model_load_and_artifact_hash=manual_required
manual.healthz_reachability=manual_required
manual.cold_start_time=manual_required
manual.idle_sleep_and_wake=manual_required
manual.restart_url_persistence=manual_required
manual.log_secret_and_path_exposure=manual_required
EOF
}

margpa_health_check() {
  local response
  if ! response="$(
    curl \
      --silent \
      --show-error \
      --fail \
      --max-time 2 \
      "http://127.0.0.1:${margpa_web_port}/healthz" 2>/dev/null
  )"; then
    return 1
  fi
  response="$(printf '%s' "${response}" | tr -d '[:space:]')"
  [[ "${response}" == '{"status":"ok"}' ]]
}

margpa_read_pid() {
  if [[ -L "${margpa_pid_file}" || ! -f "${margpa_pid_file}" || ! -r "${margpa_pid_file}" ]]; then
    return 1
  fi
  margpa_service_pid="$(sed -n '1p' "${margpa_pid_file}")"
  margpa_service_start_token="$(sed -n '2p' "${margpa_pid_file}")"
  [[ "${margpa_service_pid}" =~ ^[1-9][0-9]*$ ]]
}

margpa_pid_alive() {
  local pid="$1"
  if ! kill -0 "${pid}" 2>/dev/null; then
    return 1
  fi
  if [[ -r "/proc/${pid}/stat" ]]; then
    local linux_process_state
    linux_process_state="$(awk '{print $3}' "/proc/${pid}/stat" 2>/dev/null || true)"
    [[ -n "${linux_process_state}" && "${linux_process_state}" != "Z" ]]
    return
  fi
  local process_state
  process_state="$(ps -p "${pid}" -o stat= 2>/dev/null || true)"
  [[ -n "${process_state}" && "${process_state}" != Z* ]]
}

margpa_process_matches() {
  local pid="$1"
  if ! margpa_pid_alive "${pid}"; then
    return 1
  fi
  if [[ -r "/proc/${pid}/cmdline" ]]; then
    local command_tokens
    command_tokens="$(tr '\0' '\n' <"/proc/${pid}/cmdline")"
    printf '%s\n' "${command_tokens}" | grep -F -x -- "${margpa_web_bin}" >/dev/null &&
      printf '%s\n' "${command_tokens}" | grep -F -x -- "${margpa_web_profile}" >/dev/null &&
      printf '%s\n' "${command_tokens}" | grep -F -x -- "${margpa_web_access_profile}" >/dev/null &&
      printf '%s\n' "${command_tokens}" | grep -F -x -- "${margpa_documentation_rag_profile}" >/dev/null &&
      printf '%s\n' "${command_tokens}" | grep -F -x -- "${margpa_registry_path}" >/dev/null &&
      printf '%s\n' "${command_tokens}" | grep -F -x -- "${margpa_model_root}" >/dev/null &&
      printf '%s\n' "${command_tokens}" | grep -F -x -- "${margpa_web_host}" >/dev/null &&
      printf '%s\n' "${command_tokens}" | grep -F -x -- "${margpa_web_port}" >/dev/null
    return
  fi
  local command_line
  command_line="$(ps -p "${pid}" -o command= 2>/dev/null || true)"
  [[ -n "${command_line}" ]] &&
    [[ "${command_line}" == *"${margpa_web_bin}"* ]] &&
    [[ "${command_line}" == *"${margpa_web_profile}"* ]] &&
    [[ "${command_line}" == *"${margpa_web_access_profile}"* ]] &&
    [[ "${command_line}" == *"${margpa_documentation_rag_profile}"* ]] &&
    [[ "${command_line}" == *"${margpa_registry_path}"* ]] &&
    [[ "${command_line}" == *"${margpa_model_root}"* ]] &&
    [[ "${command_line}" == *"--host ${margpa_web_host}"* ]] &&
    [[ "${command_line}" == *"--port ${margpa_web_port}"* ]]
}

margpa_process_start_token() {
  local pid="$1"
  if ! kill -0 "${pid}" 2>/dev/null; then
    return 1
  fi
  if [[ -r "/proc/${pid}/stat" ]]; then
    awk '{print $22}' "/proc/${pid}/stat" 2>/dev/null
    return
  fi
  ps -p "${pid}" -o lstart= 2>/dev/null
}

margpa_process_matches_start_token() {
  local pid="$1"
  local expected_token="$2"
  [[ -n "${expected_token}" ]] || return 1
  local current_token
  current_token="$(margpa_process_start_token "${pid}" || true)"
  [[ -n "${current_token}" && "${current_token}" == "${expected_token}" ]]
}

margpa_pid_evidence_matches_current_process() {
  [[ -n "${margpa_service_pid:-}" && -n "${margpa_service_start_token:-}" ]] || return 1
  margpa_process_matches_start_token \
    "${margpa_service_pid}" \
    "${margpa_service_start_token}"
}

margpa_wait_for_exit() {
  local pid="$1"
  local elapsed=0
  local limit=$((margpa_stop_timeout * 10))
  while margpa_pid_alive "${pid}"; do
    if ((elapsed >= limit)); then
      return 1
    fi
    sleep 0.1
    elapsed=$((elapsed + 1))
  done
}

margpa_wait_for_identity() {
  local pid="$1"
  local attempts=0
  while ((attempts < 20)); do
    if ! kill -0 "${pid}" 2>/dev/null; then
      return 1
    fi
    if margpa_process_matches "${pid}"; then
      return 0
    fi
    sleep 0.1
    attempts=$((attempts + 1))
  done
  return 1
}
