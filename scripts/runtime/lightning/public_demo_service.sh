#!/bin/bash

set -euo pipefail

# Remove Basic Preview credentials before command substitution, sourcing, or any
# other child process. This changes only the public script process environment.
unset MARGPA_WEB_AUTH_MODE
unset MARGPA_WEB_AUTH_USERNAME
unset MARGPA_WEB_AUTH_PASSWORD

readonly MARGPA_LIGHTNING_SCRIPT_DIR="$(
  CDPATH= cd -- "$(dirname -- "$0")" >/dev/null 2>&1
  pwd -P
)"
# shellcheck source=basic_preview_common.sh
source "${MARGPA_LIGHTNING_SCRIPT_DIR}/basic_preview_common.sh"

usage() {
  cat <<'EOF'
Usage: public_demo_service.sh COMMAND

Run the repository-side Lightning Public Demo foreground entrypoint.

Commands:
  preflight  Stateless validation without Basic Preview lifecycle state
  run        Run margpa-web in the foreground without Basic credentials
  --help     Show this help

Configuration:
  MARGPA_WORKSPACE_ROOT
  MARGPA_PROJECT_ROOT
  MARGPA_MODEL_ROOT
  MARGPA_MODEL_DEFINITION
  MARGPA_MODEL_KEY
  MARGPA_CONTEXT_SIZE
  MARGPA_UV_BIN
  MARGPA_ENV_PREFIX
  MARGPA_WEB_HOST
  MARGPA_WEB_PORT
  MARGPA_WEB_PROFILE
  MARGPA_WEB_ACCESS_PROFILE
  MARGPA_DOCUMENTATION_RAG_PROFILE

The default Web Access Profile is config/web_profiles/public_demo.toml.
The Public Demo never reads or forwards Basic credential values. Documentation
RAG is available for the validated public corpus and remains off by default;
optional public controls remain explicitly off. MARGPA_RUNTIME_STATE_ROOT and existing Basic
Preview PID, log, marker, and lock artifacts are not resolved or inspected.
Platform settings remain user-managed.
EOF
}

select_public_access_profile() {
  if [[ -z "${MARGPA_WEB_ACCESS_PROFILE:-}" ]]; then
    local project_candidate="${MARGPA_PROJECT_ROOT:-${margpa_detected_project_root}}"
    MARGPA_WEB_ACCESS_PROFILE="${project_candidate}/config/web_profiles/public_demo.toml"
    export MARGPA_WEB_ACCESS_PROFILE
  fi
}

validate_public_demo() {
  select_public_access_profile
  margpa_stateless_project_preflight
  margpa_validate_public_demo_contract
}

run_foreground() {
  validate_public_demo
  margpa_build_web_arguments
  exec env \
    -u MARGPA_WEB_AUTH_MODE \
    -u MARGPA_WEB_AUTH_USERNAME \
    -u MARGPA_WEB_AUTH_PASSWORD \
    "${margpa_web_bin}" \
    "${margpa_web_arguments[@]}"
}

command_name="${1:-}"
case "${command_name}" in
  -h|--help)
    (($# == 1)) || {
      margpa_fail "arguments" "help_takes_no_options"
      exit 1
    }
    usage
    ;;
  preflight)
    (($# == 1)) || {
      margpa_fail "arguments" "preflight_takes_no_options"
      exit 1
    }
    validate_public_demo
    ;;
  run)
    (($# == 1)) || {
      margpa_fail "arguments" "run_takes_no_options"
      exit 1
    }
    run_foreground
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
