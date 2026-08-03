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
Usage: auto_start_preflight.sh [--help]

Run the Phase 1-ex project-side Lightning Auto-start preflight without
changing files, dependencies, processes, network state, or platform settings.

Configuration is resolved from:
  MARGPA_WORKSPACE_ROOT
  MARGPA_PROJECT_ROOT
  MARGPA_MODEL_ROOT
  MARGPA_UV_BIN                 directory containing uv, or the uv executable
  MARGPA_ENV_PREFIX
  MARGPA_WEB_HOST
  MARGPA_WEB_PORT
  MARGPA_WEB_PROFILE
  MARGPA_WEB_ACCESS_PROFILE
  MARGPA_MODEL_DEFINITION
  MARGPA_MODEL_KEY
  MARGPA_CONTEXT_SIZE
  MARGPA_RUNTIME_STATE_ROOT

The Runtime State Root must be a dedicated directory named "basic-preview";
protected or broad directories and symlinked paths are rejected.
The command emits pass/fail project checks and an explicit manual checklist.
Values that require Lightning account or platform operations are never
reported as pass by this read-only command.
EOF
}

case "${1:-}" in
  "")
    margpa_project_preflight
    margpa_validate_pure_cpu_deployment_profile
    margpa_validate_web_access_profile "basic_preview"
    printf 'check.access_boundary=pass mode=basic_preview public_demo=false\n'
    printf 'check.launch_contract=pass credentials=environment_only\n'
    margpa_emit_manual_checklist
    ;;
  -h|--help)
    usage
    ;;
  *)
    margpa_fail "arguments" "unknown_option"
    exit 1
    ;;
esac
