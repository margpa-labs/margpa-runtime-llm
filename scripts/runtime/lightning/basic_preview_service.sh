#!/bin/bash

set -euo pipefail

readonly MARGPA_LIGHTNING_SCRIPT_DIR="$(
  CDPATH= cd -- "$(dirname -- "$0")" >/dev/null 2>&1
  pwd -P
)"
# shellcheck source=basic_preview_common.sh
source "${MARGPA_LIGHTNING_SCRIPT_DIR}/basic_preview_common.sh"

usage() {
  cat <<'EOF'
Usage: basic_preview_service.sh COMMAND [options]

Manage the repository-side Lightning Basic Preview lifecycle.

Commands:
  preflight       Run read-only project, environment, credential, and manual checks
  run             Run margpa-web in the foreground
  start           Start margpa-web in the background and perform bounded health check
  stop [--force]  Gracefully stop this project's recorded process
  status          Report running, stopped, stale, or unhealthy
  restart [--force]
                  Stop and start; --force permits SIGKILL after graceful timeout
  --help          Show this help

Configuration:
  MARGPA_WORKSPACE_ROOT
  MARGPA_PROJECT_ROOT
  MARGPA_MODEL_ROOT
  MARGPA_UV_BIN
  MARGPA_ENV_PREFIX
  MARGPA_WEB_HOST
  MARGPA_WEB_PORT
  MARGPA_WEB_PROFILE
  MARGPA_RUNTIME_STATE_ROOT
  MARGPA_WEB_AUTH_MODE
  MARGPA_WEB_AUTH_USERNAME
  MARGPA_WEB_AUTH_PASSWORD

Credentials are read only from the environment. Their values are never passed
as command arguments or written to PID, log, or status output by this script.
MARGPA_RUNTIME_STATE_ROOT must name a dedicated "basic-preview" directory
outside the Workspace, Project, Model, Environment, Home, and broad roots.
Lightning Managed Secrets, hooks, ports, URLs, and platform settings remain
user-managed and are not changed by any command.
EOF
}

validate_basic_preview() {
  margpa_project_preflight
  margpa_validate_credentials
}

run_foreground() {
  validate_basic_preview
  exec "${margpa_web_bin}" \
    --host "${margpa_web_host}" \
    --port "${margpa_web_port}" \
    --profile "${margpa_web_profile}" \
    --model-root "${margpa_model_root}"
}

prepare_default_state_parent() {
  local state_parent
  state_parent="$(dirname -- "${margpa_runtime_state_root}")"
  if [[ -d "${state_parent}" && ! -L "${state_parent}" ]]; then
    [[ -w "${state_parent}" ]] || {
      margpa_fail "runtime_state_root" "parent_not_writable"
      return 1
    }
    return 0
  fi
  if [[ "${margpa_runtime_state_is_default}" != "1" ]]; then
    margpa_fail "runtime_state_root" "override_parent_must_exist"
    return 1
  fi

  local runtime_parent="${margpa_workspace_root}/.runtime-state"
  local project_runtime_parent="${runtime_parent}/margpa-runtime-llm"
  local directory
  umask 077
  for directory in "${runtime_parent}" "${project_runtime_parent}"; do
    if [[ -L "${directory}" ]]; then
      margpa_fail "runtime_state_root" "parent_symlink_not_allowed"
      return 1
    fi
    if [[ ! -e "${directory}" ]]; then
      if ! mkdir "${directory}" 2>/dev/null && [[ ! -d "${directory}" ]]; then
        margpa_fail "runtime_state_root" "parent_creation_failed"
        return 1
      fi
    fi
    if [[ ! -d "${directory}" || ! -w "${directory}" ]]; then
      margpa_fail "runtime_state_root" "parent_directory_invalid"
      return 1
    fi
  done
}

lock_has_unexpected_entries() {
  [[ -d "${margpa_lock_directory}" ]] || return 1
  local unexpected
  unexpected="$(
    find "${margpa_lock_directory}" \
      -mindepth 1 \
      -maxdepth 1 \
      ! -name "${MARGPA_LOCK_OWNER_NAME}" \
      -print \
      -quit
  )"
  [[ -n "${unexpected}" ]]
}

remove_stale_lock() {
  if [[ ! -d "${margpa_lock_directory}" || -L "${margpa_lock_directory}" ]]; then
    margpa_fail "lifecycle_lock" "stale_lock_directory_invalid"
    return 1
  fi
  if lock_has_unexpected_entries; then
    margpa_fail "lifecycle_lock" "unexpected_lock_content"
    return 1
  fi
  if [[ -e "${margpa_lock_owner_file}" ]]; then
    margpa_validate_regular_file_or_absent \
      "${margpa_lock_owner_file}" \
      "lifecycle_lock" || return 1
    if [[ "$(sed -n '1p' "${margpa_lock_owner_file}")" != "${MARGPA_LOCK_OWNER_VALUE}" ]]; then
      margpa_fail "lifecycle_lock" "owner_marker_invalid"
      return 1
    fi
    local owner_pid
    owner_pid="$(sed -n '2p' "${margpa_lock_owner_file}")"
    if [[ ! "${owner_pid}" =~ ^[1-9][0-9]*$ ]]; then
      margpa_fail "lifecycle_lock" "owner_pid_invalid"
      return 1
    fi
    if kill -0 "${owner_pid}" 2>/dev/null; then
      margpa_fail "lifecycle_lock" "busy"
      return 1
    fi
    rm -f -- "${margpa_lock_owner_file}"
  fi
  if ! rmdir "${margpa_lock_directory}" 2>/dev/null; then
    margpa_fail "lifecycle_lock" "stale_lock_removal_failed"
    return 1
  fi
  printf 'state_cleanup=stale_lifecycle_lock_removed\n'
}

acquire_lifecycle_lock() {
  margpa_validate_lock_artifact || return 1
  if [[ -e "${margpa_lock_directory}" ]]; then
    remove_stale_lock || return 1
  fi

  umask 077
  if ! mkdir "${margpa_lock_directory}" 2>/dev/null; then
    margpa_fail "lifecycle_lock" "busy"
    return 1
  fi
  chmod 700 "${margpa_lock_directory}"
  if ! (
    set -o noclobber
    printf '%s\n%s\n' "${MARGPA_LOCK_OWNER_VALUE}" "$$" >"${margpa_lock_owner_file}"
  ) 2>/dev/null; then
    rmdir "${margpa_lock_directory}" 2>/dev/null || true
    margpa_fail "lifecycle_lock" "owner_creation_failed"
    return 1
  fi
  chmod 600 "${margpa_lock_owner_file}"
  margpa_lifecycle_lock_held=1
}

release_lifecycle_lock() {
  [[ "${margpa_lifecycle_lock_held:-0}" == "1" ]] || return 0
  if [[ -L "${margpa_lock_owner_file}" || ! -f "${margpa_lock_owner_file}" ]]; then
    return 1
  fi
  if [[ "$(sed -n '1p' "${margpa_lock_owner_file}")" != "${MARGPA_LOCK_OWNER_VALUE}" ]] ||
    [[ "$(sed -n '2p' "${margpa_lock_owner_file}")" != "$$" ]]; then
    return 1
  fi
  if lock_has_unexpected_entries; then
    return 1
  fi
  rm -f -- "${margpa_lock_owner_file}"
  rmdir "${margpa_lock_directory}"
  margpa_lifecycle_lock_held=0
}

release_lock_on_signal() {
  local exit_code="$1"
  if [[ "${margpa_spawn_cleanup_required:-0}" == "1" ]]; then
    cleanup_spawned_child || true
  fi
  release_lifecycle_lock || true
  trap - EXIT INT TERM HUP
  exit "${exit_code}"
}

run_with_lifecycle_lock() {
  local operation="$1"
  shift
  acquire_lifecycle_lock || return 1
  trap 'release_lifecycle_lock || true' EXIT
  trap 'release_lock_on_signal 130' INT
  trap 'release_lock_on_signal 143' TERM HUP

  local operation_status=0
  if "${operation}" "$@"; then
    operation_status=0
  else
    operation_status=$?
  fi
  if ! release_lifecycle_lock; then
    margpa_fail "lifecycle_lock" "release_failed"
    operation_status=1
  fi
  trap - EXIT INT TERM HUP
  return "${operation_status}"
}

prepare_state_directory() {
  margpa_validate_state_artifacts || return 1
  if [[ ! -e "${margpa_runtime_state_root}" ]]; then
    prepare_default_state_parent || return 1
    umask 077
    if ! mkdir "${margpa_runtime_state_root}" 2>/dev/null; then
      margpa_fail "runtime_state_root" "dedicated_directory_creation_failed"
      return 1
    fi
    chmod 700 "${margpa_runtime_state_root}"
    if ! (
      set -o noclobber
      printf '%s\n' "${MARGPA_STATE_MARKER_VALUE}" >"${margpa_state_marker_file}"
    ) 2>/dev/null; then
      margpa_fail "runtime_state_root" "ownership_marker_creation_failed"
      return 1
    fi
    chmod 600 "${margpa_state_marker_file}"
  fi
  margpa_validate_state_artifacts || return 1
  if [[ ! -e "${margpa_log_file}" ]]; then
    if ! (
      set -o noclobber
      : >"${margpa_log_file}"
    ) 2>/dev/null; then
      margpa_fail "log_file" "creation_failed"
      return 1
    fi
    chmod 600 "${margpa_log_file}"
  fi
  margpa_validate_state_artifacts
}

remove_stale_pid_file() {
  margpa_validate_regular_file_or_absent "${margpa_pid_file}" "pid_file" || return 1
  rm -f -- "${margpa_pid_file}"
  printf 'state_cleanup=stale_pid_file_removed\n'
}

write_pid_evidence() {
  local pid="$1"
  local start_token="$2"
  local temporary_pid_file="${margpa_pid_file}.tmp.$$"
  margpa_validate_regular_file_or_absent "${temporary_pid_file}" "pid_file" || return 1
  if [[ -e "${temporary_pid_file}" ]]; then
    margpa_fail "pid_file" "temporary_file_exists"
    return 1
  fi
  if ! (
    set -o noclobber
    printf '%s\n%s\n' "${pid}" "${start_token}" >"${temporary_pid_file}"
  ) 2>/dev/null; then
    margpa_fail "pid_file" "temporary_creation_failed"
    return 1
  fi
  chmod 600 "${temporary_pid_file}"
  if ! mv "${temporary_pid_file}" "${margpa_pid_file}"; then
    rm -f -- "${temporary_pid_file}"
    margpa_fail "pid_file" "atomic_update_failed"
    return 1
  fi
}

capture_spawn_token() {
  local pid="$1"
  local attempts=0
  margpa_spawn_start_token=""
  while ((attempts < 20)); do
    margpa_spawn_start_token="$(margpa_process_start_token "${pid}" || true)"
    if [[ -n "${margpa_spawn_start_token}" ]]; then
      return 0
    fi
    if ! kill -0 "${pid}" 2>/dev/null; then
      return 1
    fi
    sleep 0.1
    attempts=$((attempts + 1))
  done
  return 1
}

cleanup_spawned_child() {
  local pid="${margpa_service_pid}"
  if ! margpa_pid_alive "${pid}"; then
    remove_stale_pid_file || return 1
    margpa_spawn_cleanup_required=0
    return 0
  fi
  if ! margpa_pid_evidence_matches_current_process &&
    ! margpa_process_matches "${pid}"; then
    return 1
  fi
  if ! kill -TERM "${pid}" 2>/dev/null; then
    if ! margpa_pid_alive "${pid}"; then
      remove_stale_pid_file || return 1
      margpa_spawn_cleanup_required=0
      return 0
    fi
    return 1
  fi
  if ! margpa_wait_for_exit "${pid}"; then
    return 1
  fi
  remove_stale_pid_file || return 1
  margpa_spawn_cleanup_required=0
}

start_background_locked() {
  margpa_resolve_configuration || return 1
  if margpa_read_pid; then
    if margpa_process_matches "${margpa_service_pid}" ||
      margpa_pid_evidence_matches_current_process; then
      margpa_fail "start" "already_running"
      return 1
    fi
    remove_stale_pid_file || return 1
  elif [[ -e "${margpa_pid_file}" ]]; then
    remove_stale_pid_file || return 1
  fi

  prepare_state_directory || return 1
  nohup "${margpa_web_bin}" \
    --host "${margpa_web_host}" \
    --port "${margpa_web_port}" \
    --profile "${margpa_web_profile}" \
    --model-root "${margpa_model_root}" \
    >>"${margpa_log_file}" 2>&1 </dev/null &
  margpa_service_pid=$!
  margpa_spawn_cleanup_required=1
  capture_spawn_token "${margpa_service_pid}" || true
  margpa_service_start_token="${margpa_spawn_start_token}"
  if ! write_pid_evidence \
    "${margpa_service_pid}" \
    "${margpa_service_start_token}"; then
    if cleanup_spawned_child; then
      margpa_fail "start" "pid_evidence_write_failed_child_cleaned"
    else
      printf 'recovery.pid=%s action=manual_stop_required\n' \
        "${margpa_service_pid}" >&2
      margpa_fail "start" "pid_evidence_write_failed_cleanup_incomplete"
    fi
    return 1
  fi
  if [[ -z "${margpa_service_start_token}" ]]; then
    if cleanup_spawned_child; then
      margpa_fail "start" "process_start_token_unavailable_child_cleaned"
    else
      margpa_fail \
        "start" \
        "process_start_token_unavailable_cleanup_incomplete_pid_evidence_retained"
    fi
    return 1
  fi

  if ! margpa_wait_for_identity "${margpa_service_pid}"; then
    if cleanup_spawned_child; then
      margpa_fail "start" "process_identity_not_verified_child_cleaned"
    else
      margpa_fail \
        "start" \
        "process_identity_not_verified_cleanup_incomplete_pid_evidence_retained"
    fi
    return 1
  fi

  local elapsed=0
  while ((elapsed < margpa_health_timeout)); do
    if ! margpa_pid_alive "${margpa_service_pid}"; then
      remove_stale_pid_file || return 1
      margpa_spawn_cleanup_required=0
      margpa_fail "start" "process_exited_before_healthy"
      return 1
    fi
    if margpa_health_check; then
      margpa_spawn_cleanup_required=0
      printf 'status=running pid=%s health=healthy\n' "${margpa_service_pid}"
      return 0
    fi
    sleep 1
    elapsed=$((elapsed + 1))
  done

  if cleanup_spawned_child; then
    margpa_fail "start" "health_check_timeout_child_cleaned"
  else
    margpa_fail \
      "start" \
      "health_check_timeout_cleanup_incomplete_pid_evidence_retained"
  fi
  return 1
}

stop_background_locked() {
  local allow_force="$1"
  margpa_resolve_configuration || return 1

  if ! margpa_read_pid; then
    if [[ -e "${margpa_pid_file}" ]]; then
      remove_stale_pid_file || return 1
      printf 'status=stale action=none\n'
    else
      printf 'status=stopped\n'
    fi
    return 0
  fi

  local pid="${margpa_service_pid}"
  if ! margpa_process_matches "${pid}" &&
    ! margpa_pid_evidence_matches_current_process; then
    remove_stale_pid_file || return 1
    printf 'status=stale action=unrelated_process_preserved\n'
    return 0
  fi

  if ! kill -TERM "${pid}" 2>/dev/null; then
    if ! margpa_pid_alive "${pid}"; then
      remove_stale_pid_file || return 1
      printf 'status=stopped\n'
      return 0
    fi
    margpa_fail "stop" "graceful_signal_failed_pid_evidence_retained"
    return 1
  fi
  if ! margpa_wait_for_exit "${pid}"; then
    if [[ "${allow_force}" != "1" ]]; then
      margpa_fail "stop" "graceful_timeout_use_force_option_pid_evidence_retained"
      return 1
    fi
    if ! margpa_process_matches "${pid}" &&
      ! margpa_pid_evidence_matches_current_process; then
      margpa_fail "stop" "process_identity_changed_pid_evidence_retained"
      return 1
    fi
    if ! kill -KILL "${pid}" 2>/dev/null; then
      if ! margpa_pid_alive "${pid}"; then
        remove_stale_pid_file || return 1
        printf 'status=stopped\n'
        return 0
      fi
      margpa_fail "stop" "forced_signal_failed_pid_evidence_retained"
      return 1
    fi
    margpa_wait_for_exit "${pid}" || {
      margpa_fail "stop" "forced_stop_failed_pid_evidence_retained"
      return 1
    }
  fi
  remove_stale_pid_file || return 1
  printf 'status=stopped\n'
}

restart_background_locked() {
  local allow_force="$1"
  stop_background_locked "${allow_force}" || return 1
  start_background_locked
}

report_status() {
  margpa_resolve_configuration || return 1
  if ! margpa_read_pid; then
    if [[ -e "${margpa_pid_file}" ]]; then
      printf 'status=stale reason=invalid_pid_file\n'
      return 4
    fi
    printf 'status=stopped\n'
    return 3
  fi
  if ! margpa_process_matches "${margpa_service_pid}" &&
    ! margpa_pid_evidence_matches_current_process; then
    printf 'status=stale reason=process_missing_or_identity_mismatch\n'
    return 4
  fi
  if ! margpa_process_matches "${margpa_service_pid}"; then
    printf 'status=unhealthy reason=process_identity_unverified recovery=stop\n'
    return 5
  fi
  if margpa_health_check; then
    printf 'status=running pid=%s health=healthy\n' "${margpa_service_pid}"
    return 0
  fi
  printf 'status=unhealthy pid=%s health=unreachable\n' "${margpa_service_pid}"
  return 5
}

command_name="${1:-}"
case "${command_name}" in
  -h|--help)
    usage
    ;;
  preflight)
    (($# == 1)) || {
      margpa_fail "arguments" "preflight_takes_no_options"
      exit 1
    }
    validate_basic_preview
    margpa_emit_manual_checklist
    ;;
  run)
    (($# == 1)) || {
      margpa_fail "arguments" "run_takes_no_options"
      exit 1
    }
    run_foreground
    ;;
  start)
    (($# == 1)) || {
      margpa_fail "arguments" "start_takes_no_options"
      exit 1
    }
    validate_basic_preview
    run_with_lifecycle_lock start_background_locked
    ;;
  stop|restart)
    allow_force=0
    if (($# == 2)) && [[ "$2" == "--force" ]]; then
      allow_force=1
    elif (($# != 1)); then
      margpa_fail "arguments" "only_force_option_is_supported"
      exit 1
    fi
    if [[ "${command_name}" == "restart" ]]; then
      validate_basic_preview
      run_with_lifecycle_lock restart_background_locked "${allow_force}"
    else
      margpa_resolve_configuration
      run_with_lifecycle_lock stop_background_locked "${allow_force}"
    fi
    ;;
  status)
    (($# == 1)) || {
      margpa_fail "arguments" "status_takes_no_options"
      exit 1
    }
    report_status
    ;;
  "")
    usage >&2
    exit 1
    ;;
  *)
    margpa_fail "arguments" "unknown_command"
    exit 1
    ;;
esac
