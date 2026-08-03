"""Phase 1-ex Lightning read-only preflight and Basic Preview lifecycle tests."""

from __future__ import annotations

import os
import secrets
import stat
import subprocess
import sys
import time
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[3]
SCRIPT_ROOT = PROJECT_ROOT / "scripts/runtime/lightning"
AUTO_PREFLIGHT = SCRIPT_ROOT / "auto_start_preflight.sh"
SERVICE = SCRIPT_ROOT / "basic_preview_service.sh"
PUBLIC_SERVICE = SCRIPT_ROOT / "public_demo_service.sh"
COMMON = SCRIPT_ROOT / "basic_preview_common.sh"
MODEL_RELATIVE_PATH = Path("main/qwen3-4b/gguf/Qwen3-4B-Q4_K_M.gguf")
STATE_MARKER_NAME = ".margpa-basic-preview-state"
STATE_MARKER_VALUE = "margpa-runtime-llm-basic-preview-state-v1"
LOCK_DIRECTORY_NAME = ".margpa-runtime-llm-basic-preview.lifecycle.lock"
LOCK_OWNER_VALUE = "margpa-runtime-llm-basic-preview-lock-v1"


@dataclass(frozen=True, slots=True)
class LightningFixture:
    workspace_root: Path
    project_root: Path
    model_root: Path
    environment_prefix: Path
    state_root: Path
    artifact_path: Path
    curl_log: Path
    uv_log: Path
    process_registry: Path
    process_history: Path
    web_record: Path
    child_environment_log: Path
    environment: dict[str, str]


def _write_executable(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    path.chmod(0o755)


@pytest.fixture
def lightning_fixture(tmp_path: Path) -> LightningFixture:
    workspace_root = tmp_path / "Lightning workspace with spaces"
    project_root = workspace_root / "project with spaces"
    model_root = workspace_root / "model root with spaces"
    environment_prefix = project_root / ".venv"
    state_root = workspace_root / "runtime state with spaces" / "basic-preview"
    uv_directory = workspace_root / "runtime tools" / "uv" / "bin"
    fake_commands = workspace_root / "fake commands"
    artifact_path = model_root / MODEL_RELATIVE_PATH
    curl_log = workspace_root / "curl.log"
    uv_log = workspace_root / "uv.log"
    record_path = workspace_root / "web-arguments.log"
    child_environment_log = workspace_root / "child-environment.log"
    process_registry = workspace_root / "process-registry.log"
    process_history = workspace_root / "process-history.log"
    identity_ready = workspace_root / "identity-transition.ready"
    ps_log = workspace_root / "ps.log"

    (project_root / "config/profiles").mkdir(parents=True)
    (project_root / "config/models").mkdir(parents=True)
    (project_root / "config/web_profiles").mkdir(parents=True)
    (project_root / "config/feature_profiles").mkdir(parents=True)
    (project_root / "src/margpa_runtime_llm/web").mkdir(parents=True)
    artifact_path.parent.mkdir(parents=True)
    (environment_prefix / "bin").mkdir(parents=True)
    uv_directory.mkdir(parents=True)
    fake_commands.mkdir(parents=True)
    state_root.parent.mkdir(parents=True)

    (project_root / "config/profiles/lightning_linux_x86_64_cpu_native.toml").write_text(
        """
schema_version = "3"
profile_key = "external.lightning-linux-x86_64.cpu-native"
verification_state = "defined"

[host]
operating_system_key = "linux"
architecture_key = "x86_64"
execution_environment_key = "container"
distribution_key = "ubuntu"

[backend_runtime]
backend_key = "llama_cpp"
required_version = "0.3.34"
build_variant_key = "cpu"
execution_mode_key = "in_process"

[compute]
compute_kind_key = "cpu"
vendor_key = "generic"
acceleration_api_key = "none"
memory_topology_key = "cpu_ram"
device_selector = "auto"
offload_policy_key = "disabled"

[runtime_requirements]
required_capabilities = []
required_device_kind = "cpu"
required_acceleration_api = "none"
fallback_policy = "deny"

[load_overrides]
gpu_layers = 0
""".lstrip(),
        encoding="utf-8",
    )
    (project_root / "config/models/qwen3_4b_q4_k_m.toml").write_text(
        f'[artifact]\nrelative_path = "{MODEL_RELATIVE_PATH.as_posix()}"\n',
        encoding="utf-8",
    )
    control_sections = """
[controls.rate_limit]
mode = "off"
[controls.generation_budget]
mode = "off"
[controls.cooldown]
mode = "off"
[controls.public_max_new_tokens]
mode = "off"
[controls.request_quota]
mode = "off"
[controls.cost_guard]
mode = "off"
"""
    (project_root / "config/web_profiles/basic_preview.toml").write_text(
        f"""
schema_version = "1"
profile_key = "basic_preview"
[access]
mode = "basic_preview"
authentication = "basic"
non_loopback_allowed = true
[features]
documentation_rag = "eligible"
{control_sections}
""".lstrip(),
        encoding="utf-8",
    )
    (project_root / "config/web_profiles/public_demo.toml").write_text(
        f"""
schema_version = "1"
profile_key = "public_demo"
[access]
mode = "public_demo"
authentication = "none"
non_loopback_allowed = true
[features]
documentation_rag = "eligible"
{control_sections}
""".lstrip(),
        encoding="utf-8",
    )
    (project_root / "config/feature_profiles/lightning_public_documentation_rag.toml").write_text(
        """
schema_version = "2"
profile_key = "external.lightning-public-corpus.documentation-rag.lexical"
mode = "enabled"
provider_key = "project_filesystem_lexical"
provider_display_name = "Public project documentation"
allowed_access_modes = ["basic_preview", "public_demo"]
allowed_platforms = ["linux-x86_64-container"]
[corpus]
selection_mode = "explicit_files"
files = [
  "docs/public/overview_ja.md",
  "docs/public/overview_en.md",
  "docs/public/concept_ja.md",
  "docs/public/concept_en.md",
  "docs/public/roadmap_ja.md",
  "docs/public/roadmap_en.md",
  "docs/public/technology_selection_ja.md",
  "docs/public/technology_selection_en.md",
]
include_history = false
include_lossless = false
[limits]
max_documents = 8
max_file_bytes = 4194304
max_corpus_bytes = 33554432
max_chunks = 20000
[chunking]
target_characters = 900
overlap_characters = 120
maximum_characters = 1600
[retrieval]
top_k = 4
max_chunks_per_document = 2
minimum_score = 0.1
bm25_k1 = 1.5
bm25_b = 0.75
body_weight = 1.0
heading_weight = 1.75
path_weight = 1.5
exact_phrase_bonus = 2.0
corpus_priority_weight = 0.25
[context]
maximum_tokens = 768
minimum_useful_tokens = 128
safety_margin_tokens = 512
fallback_maximum_characters = 2400
""".lstrip(),
        encoding="utf-8",
    )
    (project_root / "src/margpa_runtime_llm/web/app.py").write_text(
        '@app.get("/healthz")\nasync def healthz():\n    return {"status": "ok"}\n',
        encoding="utf-8",
    )
    artifact_path.write_bytes(b"model-fixture-placeholder")
    _write_executable(
        environment_prefix / "bin/python",
        """#!/bin/bash
printf 'python|%s|%s|%s\\n' \
  "${MARGPA_WEB_AUTH_MODE+x}" \
  "${MARGPA_WEB_AUTH_USERNAME+x}" \
  "${MARGPA_WEB_AUTH_PASSWORD+x}" >> "${MARGPA_TEST_CHILD_ENVIRONMENT_LOG}"
exec "${MARGPA_TEST_SYSTEM_PYTHON}" "$@"
""",
    )

    invalid_identity_child = fake_commands / "unexpected-lifecycle-child"
    _write_executable(
        invalid_identity_child,
        """#!/bin/bash
printf '%s|/unexpected/lifecycle-child\\n' "$$" >> "${MARGPA_TEST_PROCESS_REGISTRY}"
printf '%s\\n' "$$" >> "${MARGPA_TEST_PROCESS_HISTORY}"
: > "${MARGPA_TEST_IDENTITY_READY}"
cleanup() {
  trap - EXIT
  temporary_registry="${MARGPA_TEST_PROCESS_REGISTRY}.tmp.$$"
  grep -v "^$$|" "${MARGPA_TEST_PROCESS_REGISTRY}" > "${temporary_registry}" || true
  mv "${temporary_registry}" "${MARGPA_TEST_PROCESS_REGISTRY}"
}
if [[ "${MARGPA_TEST_IGNORE_TERM:-0}" == "1" ]]; then
  trap '' TERM
else
  trap 'cleanup; exit 0' TERM
fi
trap 'cleanup; exit 0' INT
trap cleanup EXIT
while :; do
  sleep 0.1
done
""",
    )
    _write_executable(
        environment_prefix / "bin/margpa-web",
        """#!/bin/bash
printf 'margpa-web|%s|%s|%s\\n' \
  "${MARGPA_WEB_AUTH_MODE+x}" \
  "${MARGPA_WEB_AUTH_USERNAME+x}" \
  "${MARGPA_WEB_AUTH_PASSWORD+x}" >> "${MARGPA_TEST_CHILD_ENVIRONMENT_LOG}"
if [[ "${MARGPA_TEST_WEB_MODE:-service}" == "record" ]]; then
  printf '%s\\n' "$@" > "${MARGPA_TEST_WEB_RECORD}"
  printf 'auth_mode=%s\\n' "${MARGPA_WEB_AUTH_MODE:+present}" >> "${MARGPA_TEST_WEB_RECORD}"
  printf 'auth_username=%s\\n' "${MARGPA_WEB_AUTH_USERNAME:+present}" >> "${MARGPA_TEST_WEB_RECORD}"
  printf 'auth_password=%s\\n' "${MARGPA_WEB_AUTH_PASSWORD:+present}" >> "${MARGPA_TEST_WEB_RECORD}"
  printf 'documentation_rag_profile=%s\\n' \
    "${MARGPA_DOCUMENTATION_RAG_PROFILE:-}" >> "${MARGPA_TEST_WEB_RECORD}"
  exit 0
fi
if [[ "${MARGPA_TEST_IDENTITY:-valid}" == "invalid" ]]; then
  exec "${MARGPA_TEST_INVALID_IDENTITY_CHILD}"
fi
printf '%s|%s %s\\n' "$$" "$0" "$*" >> "${MARGPA_TEST_PROCESS_REGISTRY}"
printf '%s\\n' "$$" >> "${MARGPA_TEST_PROCESS_HISTORY}"
cleanup() {
  trap - EXIT
  temporary_registry="${MARGPA_TEST_PROCESS_REGISTRY}.tmp.$$"
  grep -v "^$$|" "${MARGPA_TEST_PROCESS_REGISTRY}" > "${temporary_registry}" || true
  mv "${temporary_registry}" "${MARGPA_TEST_PROCESS_REGISTRY}"
}
if [[ "${MARGPA_TEST_IGNORE_TERM:-0}" == "1" ]]; then
  trap '' TERM
else
  trap 'cleanup; exit 0' TERM
fi
trap 'cleanup; exit 0' INT
trap cleanup EXIT
while :; do
  sleep 0.1
done
""",
    )
    _write_executable(
        fake_commands / "mv",
        """#!/bin/bash
destination="${!#}"
if [[ "${MARGPA_TEST_IDENTITY:-valid}" == "invalid" ]] &&
  [[ "${destination}" == "${MARGPA_RUNTIME_STATE_ROOT}/basic-preview.pid" ]]; then
  attempts=0
  while [[ ! -f "${MARGPA_TEST_IDENTITY_READY}" ]]; do
    if ((attempts >= 500)); then
      printf 'fixture_identity_transition_timeout\\n' >&2
      exit 1
    fi
    sleep 0.01
    attempts=$((attempts + 1))
  done
fi
exec /bin/mv "$@"
""",
    )
    _write_executable(
        uv_directory / "uv",
        """#!/bin/bash
printf 'uv|%s|%s|%s\\n' \
  "${MARGPA_WEB_AUTH_MODE+x}" \
  "${MARGPA_WEB_AUTH_USERNAME+x}" \
  "${MARGPA_WEB_AUTH_PASSWORD+x}" >> "${MARGPA_TEST_CHILD_ENVIRONMENT_LOG}"
printf '%s\\n' "$*" >> "${MARGPA_TEST_UV_LOG}"
if [[ "${1:-}" == "--version" ]]; then
  printf 'uv 0.11.29\\n'
  exit 0
fi
exit 91
""",
    )
    _write_executable(
        fake_commands / "dirname",
        """#!/bin/bash
printf 'dirname|%s|%s|%s\\n' \
  "${MARGPA_WEB_AUTH_MODE+x}" \
  "${MARGPA_WEB_AUTH_USERNAME+x}" \
  "${MARGPA_WEB_AUTH_PASSWORD+x}" >> "${MARGPA_TEST_CHILD_ENVIRONMENT_LOG}"
exec /usr/bin/dirname "$@"
""",
    )
    _write_executable(
        fake_commands / "uname",
        """#!/bin/bash
case "${1:-}" in
  -s) printf 'Linux\\n' ;;
  -m) printf 'x86_64\\n' ;;
  *) exit 2 ;;
esac
""",
    )
    _write_executable(
        fake_commands / "curl",
        """#!/bin/bash
printf 'called\\n' >> "${MARGPA_TEST_CURL_LOG}"
if [[ -n "${MARGPA_TEST_HEALTH_DELAY:-}" ]]; then
  sleep "${MARGPA_TEST_HEALTH_DELAY}"
fi
if [[ "${MARGPA_TEST_HEALTH:-ok}" == "ok" ]]; then
  printf '{"status":"ok"}\\n'
  exit 0
fi
exit 22
""",
    )
    _write_executable(
        fake_commands / "ps",
        """#!/bin/bash
requested="$*"
pid=""
while (($# > 0)); do
  case "$1" in
    -p)
      pid="$2"
      shift 2
      ;;
    *)
      shift
      ;;
  esac
done
[[ -n "${pid}" ]] || exit 2
kill -0 "${pid}" 2>/dev/null || exit 1
entry="$(
  awk -F'|' -v target="${pid}" '$1 == target {print; exit}' \
    "${MARGPA_TEST_PROCESS_REGISTRY}" 2>/dev/null
)"
printf '%s|%s|%s\\n' "${pid}" "${requested}" "${entry}" >> "${MARGPA_TEST_PS_LOG}"
[[ -n "${entry}" ]] || exit 1
case "${requested}" in
  *stat=*) printf 'S\\n' ;;
  *lstart=*) printf 'fixture-start-%s\\n' "${pid}" ;;
  *) printf '%s\\n' "${entry#*|}" ;;
esac
""",
    )
    os_release = workspace_root / "os-release"
    os_release.write_text('ID="ubuntu"\n', encoding="utf-8")

    environment = dict(os.environ)
    environment.update(
        {
            "PATH": f"{fake_commands}:{environment['PATH']}",
            "MARGPA_WORKSPACE_ROOT": str(workspace_root),
            "MARGPA_PROJECT_ROOT": str(project_root),
            "MARGPA_MODEL_ROOT": str(model_root),
            "MARGPA_UV_BIN": str(uv_directory),
            "MARGPA_ENV_PREFIX": str(environment_prefix),
            "MARGPA_WEB_HOST": "0.0.0.0",
            "MARGPA_WEB_PORT": "8123",
            "MARGPA_WEB_PROFILE": ("config/profiles/lightning_linux_x86_64_cpu_native.toml"),
            "MARGPA_RUNTIME_STATE_ROOT": str(state_root),
            "MARGPA_WEB_AUTH_MODE": "basic",
            "MARGPA_WEB_AUTH_USERNAME": secrets.token_urlsafe(18),
            "MARGPA_WEB_AUTH_PASSWORD": secrets.token_urlsafe(24),
            "MARGPA_LIGHTNING_CONTAINER_MARKER": "present",
            "MARGPA_LIGHTNING_OS_RELEASE_PATH": str(os_release),
            "MARGPA_HEALTH_TIMEOUT_SECONDS": "1",
            "MARGPA_STOP_TIMEOUT_SECONDS": "1",
            "MARGPA_TEST_CURL_LOG": str(curl_log),
            "MARGPA_TEST_UV_LOG": str(uv_log),
            "MARGPA_TEST_WEB_RECORD": str(record_path),
            "MARGPA_TEST_CHILD_ENVIRONMENT_LOG": str(child_environment_log),
            "MARGPA_TEST_SYSTEM_PYTHON": sys.executable,
            "MARGPA_TEST_PROCESS_REGISTRY": str(process_registry),
            "MARGPA_TEST_PROCESS_HISTORY": str(process_history),
            "MARGPA_TEST_INVALID_IDENTITY_CHILD": str(invalid_identity_child),
            "MARGPA_TEST_IDENTITY_READY": str(identity_ready),
            "MARGPA_TEST_PS_LOG": str(ps_log),
        }
    )
    return LightningFixture(
        workspace_root=workspace_root,
        project_root=project_root,
        model_root=model_root,
        environment_prefix=environment_prefix,
        state_root=state_root,
        artifact_path=artifact_path,
        curl_log=curl_log,
        uv_log=uv_log,
        process_registry=process_registry,
        process_history=process_history,
        web_record=record_path,
        child_environment_log=child_environment_log,
        environment=environment,
    )


def _run(
    script: Path,
    fixture: LightningFixture,
    *arguments: str,
    environment_updates: Mapping[str, str | None] | None = None,
    timeout: int = 15,
    cwd: Path = PROJECT_ROOT,
) -> subprocess.CompletedProcess[str]:
    environment = dict(fixture.environment)
    for name, value in (environment_updates or {}).items():
        if value is None:
            environment.pop(name, None)
        else:
            environment[name] = value
    return subprocess.run(
        [str(script), *arguments],
        cwd=cwd,
        env=environment,
        check=False,
        capture_output=True,
        text=True,
        timeout=timeout,
    )


def _credentials(fixture: LightningFixture) -> tuple[str, str]:
    return (
        fixture.environment["MARGPA_WEB_AUTH_USERNAME"],
        fixture.environment["MARGPA_WEB_AUTH_PASSWORD"],
    )


def _child_environment_records(fixture: LightningFixture) -> list[tuple[str, ...]]:
    return [
        tuple(line.split("|"))
        for line in fixture.child_environment_log.read_text(encoding="utf-8").splitlines()
        if line
    ]


def _popen_service(
    fixture: LightningFixture,
    *arguments: str,
    environment_updates: Mapping[str, str | None] | None = None,
    cwd: Path = PROJECT_ROOT,
    script: Path = SERVICE,
) -> subprocess.Popen[str]:
    environment = dict(fixture.environment)
    for name, value in (environment_updates or {}).items():
        if value is None:
            environment.pop(name, None)
        else:
            environment[name] = value
    return subprocess.Popen(
        [str(script), *arguments],
        cwd=cwd,
        env=environment,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )


def _create_owned_state(fixture: LightningFixture) -> None:
    fixture.state_root.mkdir(parents=True, mode=0o700)
    fixture.state_root.chmod(0o700)
    marker = fixture.state_root / STATE_MARKER_NAME
    marker.write_text(f"{STATE_MARKER_VALUE}\n", encoding="utf-8")
    marker.chmod(0o600)


def _spawned_pids(fixture: LightningFixture) -> list[int]:
    return [
        int(line)
        for line in fixture.process_history.read_text(encoding="utf-8").splitlines()
        if line
    ]


def _assert_processes_stopped(pids: list[int]) -> None:
    for pid in pids:
        deadline = time.monotonic() + 5
        while time.monotonic() < deadline:
            try:
                os.kill(pid, 0)
            except ProcessLookupError:
                break
            proc_stat = Path(f"/proc/{pid}/stat")
            try:
                if proc_stat.is_file() and proc_stat.read_text(encoding="utf-8").split()[2] == "Z":
                    break
            except OSError:
                pass
            time.sleep(0.05)
        else:
            pytest.fail(f"fixture child process remains alive: pid={pid}")


def test_help_argument_handling_and_shell_syntax(
    lightning_fixture: LightningFixture,
) -> None:
    for script in (COMMON, AUTO_PREFLIGHT, SERVICE, PUBLIC_SERVICE):
        syntax = subprocess.run(
            ["bash", "-n", str(script)],
            cwd=PROJECT_ROOT,
            check=False,
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert syntax.returncode == 0, syntax.stderr

    auto_help = _run(AUTO_PREFLIGHT, lightning_fixture, "--help")
    service_help = _run(SERVICE, lightning_fixture, "--help")
    public_help = _run(PUBLIC_SERVICE, lightning_fixture, "--help")
    unknown = _run(SERVICE, lightning_fixture, "publish")

    assert auto_help.returncode == 0
    assert "read-only" in auto_help.stdout
    assert service_help.returncode == 0
    assert public_help.returncode == 0
    assert "preflight" in public_help.stdout
    assert "run" in public_help.stdout
    assert "start" not in public_help.stdout
    for command in ("preflight", "run", "start", "stop", "status", "restart"):
        assert command in service_help.stdout
    assert unknown.returncode == 1
    assert "unknown_command" in unknown.stderr


def test_auto_start_preflight_is_read_only_and_keeps_manual_checks_unpassed(
    lightning_fixture: LightningFixture,
) -> None:
    before = {
        path.relative_to(lightning_fixture.project_root)
        for path in lightning_fixture.project_root.rglob("*")
    }

    result = _run(
        AUTO_PREFLIGHT,
        lightning_fixture,
        environment_updates={
            "MARGPA_WEB_AUTH_MODE": None,
            "MARGPA_WEB_AUTH_USERNAME": None,
            "MARGPA_WEB_AUTH_PASSWORD": None,
        },
    )

    after = {
        path.relative_to(lightning_fixture.project_root)
        for path in lightning_fixture.project_root.rglob("*")
    }
    assert result.returncode == 0, result.stderr
    assert before == after
    assert "check.host_platform=pass" in result.stdout
    assert "check.model_artifact=pass" in result.stdout
    assert "check.health_contract=pass" in result.stdout
    assert "check.access_boundary=pass mode=basic_preview public_demo=false" in result.stdout
    assert "manual.platform_validation=not_run" in result.stdout
    assert "manual.api_builder_availability=manual_required" in result.stdout
    assert "manual.public_url_issuance=manual_required" in result.stdout
    assert "status_values=pass,fail,not_run,manual_required,unknown" in result.stdout
    assert not lightning_fixture.state_root.exists()
    assert not lightning_fixture.curl_log.exists()
    assert lightning_fixture.uv_log.read_text(encoding="utf-8").splitlines() == ["--version"]


def test_basic_preflight_fails_closed_without_credentials_and_redacts_values(
    lightning_fixture: LightningFixture,
) -> None:
    username, password = _credentials(lightning_fixture)

    missing = _run(
        SERVICE,
        lightning_fixture,
        "preflight",
        environment_updates={"MARGPA_WEB_AUTH_PASSWORD": None},
    )

    assert missing.returncode == 1
    assert "password_required" in missing.stderr
    combined_output = missing.stdout + missing.stderr
    assert username not in combined_output
    assert password not in combined_output
    assert not lightning_fixture.state_root.exists()
    assert not lightning_fixture.curl_log.exists()


def test_preflight_rejects_missing_model_without_disclosing_credentials(
    lightning_fixture: LightningFixture,
    tmp_path: Path,
) -> None:
    empty_model_root = tmp_path / "empty model root"
    empty_model_root.mkdir()
    username, password = _credentials(lightning_fixture)

    result = _run(
        SERVICE,
        lightning_fixture,
        "preflight",
        environment_updates={"MARGPA_MODEL_ROOT": str(empty_model_root)},
    )

    assert result.returncode == 1
    assert "registry_layout_or_file_invalid" in result.stderr
    assert str(empty_model_root) not in result.stderr
    assert username not in result.stdout + result.stderr
    assert password not in result.stdout + result.stderr


def test_run_passes_only_non_secret_arguments_and_inherits_credentials(
    lightning_fixture: LightningFixture,
) -> None:
    username, password = _credentials(lightning_fixture)
    record_path = Path(lightning_fixture.environment["MARGPA_TEST_WEB_RECORD"])

    result = _run(
        SERVICE,
        lightning_fixture,
        "run",
        environment_updates={"MARGPA_TEST_WEB_MODE": "record"},
    )

    assert result.returncode == 0, result.stderr
    recorded = record_path.read_text(encoding="utf-8")
    assert "--host\n0.0.0.0" in recorded
    assert "--port\n8123" in recorded
    assert f"--profile\n{lightning_fixture.project_root}/config/profiles" in recorded
    assert (
        f"--access-profile\n"
        f"{lightning_fixture.project_root}/config/web_profiles/basic_preview.toml" in recorded
    )
    assert (
        f"--documentation-rag-profile\n"
        f"{lightning_fixture.project_root}/config/feature_profiles/"
        "lightning_public_documentation_rag.toml" in recorded
    )
    assert (
        f"--registry\n"
        f"{lightning_fixture.project_root}/config/models/qwen3_4b_q4_k_m.toml" in recorded
    )
    assert f"--model-root\n{lightning_fixture.model_root}" in recorded
    assert "auth_mode=present" in recorded
    assert "auth_username=present" in recorded
    assert "auth_password=present" in recorded
    assert all(
        record[1:] == ("x", "x", "x") for record in _child_environment_records(lightning_fixture)
    )
    combined_output = result.stdout + result.stderr + recorded
    assert username not in combined_output
    assert password not in combined_output


def test_public_preflight_and_run_are_credential_independent_with_public_rag(
    lightning_fixture: LightningFixture,
) -> None:
    username, password = _credentials(lightning_fixture)
    alternate_profile = (
        lightning_fixture.project_root / "config/profiles/alternate_public_compute.toml"
    )
    source_profile = (
        lightning_fixture.project_root / "config/profiles/lightning_linux_x86_64_cpu_native.toml"
    )
    alternate_profile.write_text(
        source_profile.read_text(encoding="utf-8").replace(
            'profile_key = "external.lightning-linux-x86_64.cpu-native"',
            'profile_key = "external.alternate-compute"',
        ),
        encoding="utf-8",
    )
    alternate_definition = lightning_fixture.project_root / "config/models/alternate-model.toml"
    alternate_definition.write_text(
        f'[artifact]\nrelative_path = "{MODEL_RELATIVE_PATH.as_posix()}"\n',
        encoding="utf-8",
    )

    preflight = _run(
        PUBLIC_SERVICE,
        lightning_fixture,
        "preflight",
        environment_updates={
            "MARGPA_WEB_ACCESS_PROFILE": None,
        },
    )
    preflight_child_records = _child_environment_records(lightning_fixture)
    run = _run(
        PUBLIC_SERVICE,
        lightning_fixture,
        "run",
        environment_updates={
            "MARGPA_WEB_ACCESS_PROFILE": None,
            "MARGPA_WEB_PROFILE": str(alternate_profile),
            "MARGPA_MODEL_DEFINITION": str(alternate_definition),
            "MARGPA_MODEL_KEY": "replacement.model",
            "MARGPA_CONTEXT_SIZE": "8192",
            "MARGPA_TEST_WEB_MODE": "record",
        },
    )

    assert preflight.returncode == 0, preflight.stderr
    assert "mode=public_demo authentication=none" in preflight.stdout
    assert "capability=eligible default=disabled" in preflight.stdout
    assert "expected=8 present=0 missing=8" in preflight.stdout
    assert "check.public_controls=pass mode=off" in preflight.stdout
    assert {record[0] for record in preflight_child_records} >= {"dirname", "python", "uv"}
    assert all(record[1:] == ("", "", "") for record in preflight_child_records)
    assert run.returncode == 0, run.stderr

    recorded = lightning_fixture.web_record.read_text(encoding="utf-8")
    all_child_records = _child_environment_records(lightning_fixture)
    run_child_records = all_child_records[len(preflight_child_records) :]
    assert (
        f"--access-profile\n"
        f"{lightning_fixture.project_root}/config/web_profiles/public_demo.toml" in recorded
    )
    assert (
        f"--documentation-rag-profile\n"
        f"{lightning_fixture.project_root}/config/feature_profiles/"
        "lightning_public_documentation_rag.toml" in recorded
    )
    assert f"--profile\n{alternate_profile}" in recorded
    assert f"--registry\n{alternate_definition}" in recorded
    assert "--model-key\nreplacement.model" in recorded
    assert "--context-size\n8192" in recorded
    assert "auth_mode=\n" in recorded
    assert "auth_username=\n" in recorded
    assert "auth_password=\n" in recorded
    assert (
        "documentation_rag_profile="
        f"{lightning_fixture.project_root}/config/feature_profiles/"
        "lightning_public_documentation_rag.toml" in recorded
    )
    assert {record[0] for record in run_child_records} >= {
        "dirname",
        "python",
        "uv",
        "margpa-web",
    }
    assert all(record[1:] == ("", "", "") for record in run_child_records)
    combined_output = preflight.stdout + preflight.stderr + run.stdout + run.stderr + recorded
    assert username not in combined_output
    assert password not in combined_output
    assert not lightning_fixture.state_root.exists()
    assert not (lightning_fixture.workspace_root / LOCK_DIRECTORY_NAME).exists()


@pytest.mark.parametrize("script", [SERVICE, PUBLIC_SERVICE])
def test_documentation_rag_profile_must_remain_project_bounded_and_valid(
    lightning_fixture: LightningFixture,
    tmp_path: Path,
    script: Path,
) -> None:
    outside = tmp_path / "outside-documentation-rag.toml"
    tracked = (
        lightning_fixture.project_root
        / "config/feature_profiles/lightning_public_documentation_rag.toml"
    )
    outside.write_text(tracked.read_text(encoding="utf-8"), encoding="utf-8")

    result = _run(
        script,
        lightning_fixture,
        "preflight",
        environment_updates={
            "MARGPA_DOCUMENTATION_RAG_PROFILE": str(outside),
            "MARGPA_WEB_ACCESS_PROFILE": None,
        }
        if script == PUBLIC_SERVICE
        else {"MARGPA_DOCUMENTATION_RAG_PROFILE": str(outside)},
    )

    assert result.returncode == 1
    assert "project_root_boundary_required" in result.stderr


@pytest.mark.parametrize("script", [SERVICE, PUBLIC_SERVICE])
def test_invalid_documentation_rag_profile_fails_closed_for_both_access_modes(
    lightning_fixture: LightningFixture,
    script: Path,
) -> None:
    profile = (
        lightning_fixture.project_root
        / "config/feature_profiles/lightning_public_documentation_rag.toml"
    )
    profile.write_text(
        profile.read_text(encoding="utf-8").replace(
            'allowed_access_modes = ["basic_preview", "public_demo"]',
            'allowed_access_modes = ["basic_preview"]',
        ),
        encoding="utf-8",
    )

    result = _run(
        script,
        lightning_fixture,
        "preflight",
        environment_updates={"MARGPA_WEB_ACCESS_PROFILE": None}
        if script == PUBLIC_SERVICE
        else None,
    )

    assert result.returncode == 1
    assert "invalid_profile_or_corpus_boundary" in result.stderr


def test_public_preflight_counts_only_explicit_public_files(
    lightning_fixture: LightningFixture,
) -> None:
    public_root = lightning_fixture.project_root / "docs/public"
    public_root.mkdir(parents=True)
    (public_root / "overview_ja.md").write_text("# Overview", encoding="utf-8")
    (public_root / "not_allowlisted.md").write_text("# Extra", encoding="utf-8")
    internal = lightning_fixture.project_root / "docs/project/current/internal.md"
    internal.parent.mkdir(parents=True)
    internal.write_text("# Internal", encoding="utf-8")

    result = _run(
        PUBLIC_SERVICE,
        lightning_fixture,
        "preflight",
        environment_updates={"MARGPA_WEB_ACCESS_PROFILE": None},
    )

    assert result.returncode == 0, result.stderr
    assert "expected=8 present=1 missing=7" in result.stdout


@pytest.mark.parametrize("artifact_kind", ["state", "marker", "pid", "log", "lock"])
def test_public_preflight_ignores_invalid_basic_lifecycle_artifacts(
    lightning_fixture: LightningFixture,
    artifact_kind: str,
) -> None:
    if artifact_kind == "state":
        lightning_fixture.state_root.mkdir()
        lightning_fixture.state_root.chmod(0o755)
        target = lightning_fixture.state_root
    elif artifact_kind == "lock":
        target = lightning_fixture.workspace_root / LOCK_DIRECTORY_NAME
        target.write_text("not-a-lifecycle-lock\n", encoding="utf-8")
    else:
        _create_owned_state(lightning_fixture)
        target = (
            lightning_fixture.state_root
            / {
                "marker": STATE_MARKER_NAME,
                "pid": "basic-preview.pid",
                "log": "basic-preview.log",
            }[artifact_kind]
        )
        if artifact_kind == "marker":
            target.write_text("invalid-marker\n", encoding="utf-8")
            target.chmod(0o600)
        else:
            target.mkdir()

    before = (
        stat.S_IMODE(target.stat().st_mode),
        target.is_dir(),
        target.read_bytes() if target.is_file() else None,
    )
    public = _run(
        PUBLIC_SERVICE,
        lightning_fixture,
        "preflight",
        environment_updates={"MARGPA_WEB_ACCESS_PROFILE": None},
    )
    after = (
        stat.S_IMODE(target.stat().st_mode),
        target.is_dir(),
        target.read_bytes() if target.is_file() else None,
    )
    basic = _run(SERVICE, lightning_fixture, "preflight")

    assert public.returncode == 0, public.stderr
    assert "runtime_state_root" not in public.stdout + public.stderr
    assert before == after
    assert basic.returncode == 1
    assert any(
        check_name in basic.stderr
        for check_name in ("runtime_state_root", "pid_file", "log_file", "lifecycle_lock")
    )


@pytest.mark.parametrize("runtime_state_override", ["/", "../unsafe", "basic-preview/../unsafe"])
def test_public_preflight_does_not_resolve_runtime_state_override(
    lightning_fixture: LightningFixture,
    runtime_state_override: str,
) -> None:
    public = _run(
        PUBLIC_SERVICE,
        lightning_fixture,
        "preflight",
        environment_updates={
            "MARGPA_RUNTIME_STATE_ROOT": runtime_state_override,
            "MARGPA_WEB_ACCESS_PROFILE": None,
        },
    )
    basic = _run(
        SERVICE,
        lightning_fixture,
        "preflight",
        environment_updates={"MARGPA_RUNTIME_STATE_ROOT": runtime_state_override},
    )

    assert public.returncode == 0, public.stderr
    assert "runtime_state_root" not in public.stdout + public.stderr
    assert basic.returncode == 1
    assert "runtime_state_root" in basic.stderr


def test_public_run_is_foreground_and_term_reaches_the_web_process(
    lightning_fixture: LightningFixture,
) -> None:
    process = _popen_service(
        lightning_fixture,
        "run",
        environment_updates={
            "MARGPA_RUNTIME_STATE_ROOT": None,
            "MARGPA_WEB_ACCESS_PROFILE": None,
        },
        script=PUBLIC_SERVICE,
    )
    try:
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline:
            if (
                lightning_fixture.process_history.exists()
                and lightning_fixture.process_history.read_text(encoding="utf-8").strip()
            ):
                break
            if process.poll() is not None:
                pytest.fail("public foreground process exited before signal test")
            time.sleep(0.05)
        else:
            pytest.fail("public foreground process did not reach margpa-web")

        assert _spawned_pids(lightning_fixture) == [process.pid]
        process.terminate()
        stdout, stderr = process.communicate(timeout=5)

        assert process.returncode == 0
        assert not (lightning_fixture.workspace_root / ".runtime-state").exists()
        assert not (lightning_fixture.workspace_root / LOCK_DIRECTORY_NAME).exists()
        for secret in _credentials(lightning_fixture):
            assert secret not in stdout + stderr
    finally:
        if process.poll() is None:
            process.kill()
            process.communicate(timeout=5)


def test_run_is_foreground_compatible_outside_project_without_runtime_state(
    lightning_fixture: LightningFixture,
    tmp_path: Path,
) -> None:
    external_working_directory = tmp_path / "api builder working directory"
    external_working_directory.mkdir()
    platform_port = "49123"

    result = _run(
        SERVICE,
        lightning_fixture,
        "run",
        environment_updates={
            "MARGPA_RUNTIME_STATE_ROOT": None,
            "MARGPA_TEST_WEB_MODE": "record",
            "MARGPA_WEB_PORT": platform_port,
        },
        cwd=external_working_directory,
    )

    assert result.returncode == 0, result.stderr
    recorded = lightning_fixture.web_record.read_text(encoding="utf-8")
    assert f"--port\n{platform_port}" in recorded
    assert f"--profile\n{lightning_fixture.project_root}/config/profiles" in recorded
    assert f"--model-root\n{lightning_fixture.model_root}" in recorded
    assert not (lightning_fixture.workspace_root / ".runtime-state").exists()
    assert not (lightning_fixture.workspace_root / LOCK_DIRECTORY_NAME).exists()
    assert not lightning_fixture.curl_log.exists()
    assert lightning_fixture.uv_log.read_text(encoding="utf-8").splitlines() == ["--version"]


def test_run_exec_preserves_process_identity_and_term_signal(
    lightning_fixture: LightningFixture,
    tmp_path: Path,
) -> None:
    external_working_directory = tmp_path / "external process manager"
    external_working_directory.mkdir()
    username, password = _credentials(lightning_fixture)
    process = _popen_service(
        lightning_fixture,
        "run",
        environment_updates={"MARGPA_RUNTIME_STATE_ROOT": None},
        cwd=external_working_directory,
    )
    try:
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline:
            if (
                lightning_fixture.process_history.exists()
                and lightning_fixture.process_history.read_text(encoding="utf-8").strip()
            ):
                break
            if process.poll() is not None:
                pytest.fail("foreground process exited before signal test")
            time.sleep(0.05)
        else:
            pytest.fail("foreground process did not reach margpa-web")

        assert _spawned_pids(lightning_fixture) == [process.pid]
        process.terminate()
        stdout, stderr = process.communicate(timeout=5)

        assert process.returncode == 0
        assert username not in stdout + stderr
        assert password not in stdout + stderr
        assert not (lightning_fixture.workspace_root / ".runtime-state").exists()
        assert not (lightning_fixture.workspace_root / LOCK_DIRECTORY_NAME).exists()
    finally:
        if process.poll() is None:
            process.kill()
            process.communicate(timeout=5)


def test_background_lifecycle_rejects_duplicates_and_stops_gracefully(
    lightning_fixture: LightningFixture,
) -> None:
    username, password = _credentials(lightning_fixture)
    try:
        started = _run(SERVICE, lightning_fixture, "start")
        assert started.returncode == 0, started.stderr
        assert "status=running" in started.stdout

        pid_file = lightning_fixture.state_root / "basic-preview.pid"
        log_file = lightning_fixture.state_root / "basic-preview.log"
        assert stat.S_IMODE(lightning_fixture.state_root.stat().st_mode) == 0o700
        assert stat.S_IMODE(pid_file.stat().st_mode) == 0o600
        assert stat.S_IMODE(log_file.stat().st_mode) == 0o600
        assert username not in pid_file.read_text(encoding="utf-8")
        assert password not in pid_file.read_text(encoding="utf-8")
        assert username not in log_file.read_text(encoding="utf-8")
        assert password not in log_file.read_text(encoding="utf-8")

        status_result = _run(SERVICE, lightning_fixture, "status")
        duplicate = _run(SERVICE, lightning_fixture, "start")
        unhealthy = _run(
            SERVICE,
            lightning_fixture,
            "status",
            environment_updates={"MARGPA_TEST_HEALTH": "fail"},
        )

        assert status_result.returncode == 0
        assert "status=running" in status_result.stdout
        assert duplicate.returncode == 1
        assert "already_running" in duplicate.stderr
        assert unhealthy.returncode == 5
        assert "status=unhealthy" in unhealthy.stdout

        restarted = _run(SERVICE, lightning_fixture, "restart")
        assert restarted.returncode == 0, restarted.stderr
        assert "status=stopped" in restarted.stdout
        assert "status=running" in restarted.stdout

        stopped = _run(SERVICE, lightning_fixture, "stop")
        stopped_status = _run(SERVICE, lightning_fixture, "status")
        assert stopped.returncode == 0, stopped.stderr
        assert "status=stopped" in stopped.stdout
        assert stopped_status.returncode == 3
        assert "status=stopped" in stopped_status.stdout
    finally:
        _run(SERVICE, lightning_fixture, "stop", "--force")


def test_stale_pid_does_not_signal_an_unrelated_process(
    lightning_fixture: LightningFixture,
) -> None:
    _create_owned_state(lightning_fixture)
    unrelated = subprocess.Popen(
        ["sleep", "30"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        text=True,
    )
    try:
        pid_file = lightning_fixture.state_root / "basic-preview.pid"
        pid_file.write_text(
            f"{unrelated.pid}\n",
            encoding="utf-8",
        )
        pid_file.chmod(0o600)

        stopped = _run(SERVICE, lightning_fixture, "stop")

        assert stopped.returncode == 0, stopped.stderr
        assert "unrelated_process_preserved" in stopped.stdout
        assert unrelated.poll() is None
        assert not (lightning_fixture.state_root / "basic-preview.pid").exists()
    finally:
        unrelated.terminate()
        unrelated.wait(timeout=5)


def test_health_timeout_stops_failed_start_and_leaves_no_pid(
    lightning_fixture: LightningFixture,
) -> None:
    failed = _run(
        SERVICE,
        lightning_fixture,
        "start",
        environment_updates={"MARGPA_TEST_HEALTH": "fail"},
    )

    assert failed.returncode == 1
    assert "health_check_timeout" in failed.stderr
    assert not (lightning_fixture.state_root / "basic-preview.pid").exists()


def test_runtime_state_root_inside_project_is_rejected(
    lightning_fixture: LightningFixture,
) -> None:
    unsafe_state_root = lightning_fixture.project_root / "basic-preview"

    result = _run(
        SERVICE,
        lightning_fixture,
        "preflight",
        environment_updates={"MARGPA_RUNTIME_STATE_ROOT": str(unsafe_state_root)},
    )

    assert result.returncode == 1
    assert "protected_tree_not_allowed" in result.stderr
    assert not unsafe_state_root.exists()


def test_broad_or_protected_state_roots_are_rejected_before_mutation(
    lightning_fixture: LightningFixture,
) -> None:
    sentinel = lightning_fixture.workspace_root / "workspace-sentinel"
    sentinel.write_text("unchanged\n", encoding="utf-8")
    original_workspace_mode = stat.S_IMODE(lightning_fixture.workspace_root.stat().st_mode)
    protected_paths = (
        Path("/"),
        Path(lightning_fixture.environment["HOME"]),
        lightning_fixture.workspace_root.parent,
        lightning_fixture.workspace_root,
        lightning_fixture.project_root,
        lightning_fixture.model_root,
        lightning_fixture.environment_prefix,
    )

    for protected_path in protected_paths:
        result = _run(
            SERVICE,
            lightning_fixture,
            "start",
            environment_updates={"MARGPA_RUNTIME_STATE_ROOT": str(protected_path)},
        )

        assert result.returncode == 1
        assert "runtime_state_root" in result.stderr
        assert sentinel.read_text(encoding="utf-8") == "unchanged\n"
        assert (
            stat.S_IMODE(lightning_fixture.workspace_root.stat().st_mode) == original_workspace_mode
        )
        assert not (lightning_fixture.workspace_root / LOCK_DIRECTORY_NAME).exists()


def test_existing_unowned_state_directory_is_not_chmodded_or_truncated(
    lightning_fixture: LightningFixture,
) -> None:
    unowned_state = lightning_fixture.workspace_root / "unowned area" / "basic-preview"
    unowned_state.mkdir(parents=True)
    unowned_state.chmod(0o755)
    sentinel_log = unowned_state / "basic-preview.log"
    sentinel_log.write_text("preserve-existing-content\n", encoding="utf-8")
    original_mode = stat.S_IMODE(unowned_state.stat().st_mode)

    result = _run(
        SERVICE,
        lightning_fixture,
        "start",
        environment_updates={"MARGPA_RUNTIME_STATE_ROOT": str(unowned_state)},
    )

    assert result.returncode == 1
    assert "ownership_marker_required" in result.stderr
    assert stat.S_IMODE(unowned_state.stat().st_mode) == original_mode
    assert sentinel_log.read_text(encoding="utf-8") == "preserve-existing-content\n"
    assert not (lightning_fixture.workspace_root / LOCK_DIRECTORY_NAME).exists()


def test_owned_existing_log_is_appended_without_truncation(
    lightning_fixture: LightningFixture,
) -> None:
    _create_owned_state(lightning_fixture)
    log_file = lightning_fixture.state_root / "basic-preview.log"
    log_file.write_text("preserve-owned-log-prefix\n", encoding="utf-8")
    log_file.chmod(0o600)
    try:
        started = _run(SERVICE, lightning_fixture, "start")

        assert started.returncode == 0, started.stderr
        assert log_file.read_text(encoding="utf-8").startswith("preserve-owned-log-prefix\n")
    finally:
        _run(SERVICE, lightning_fixture, "stop", "--force")


@pytest.mark.parametrize("artifact_name", ["basic-preview.pid", "basic-preview.log"])
def test_state_artifact_symlink_is_rejected_without_touching_target(
    lightning_fixture: LightningFixture,
    artifact_name: str,
) -> None:
    _create_owned_state(lightning_fixture)
    target = lightning_fixture.workspace_root / f"{artifact_name}.target"
    target.write_text("target-must-remain\n", encoding="utf-8")
    (lightning_fixture.state_root / artifact_name).symlink_to(target)

    result = _run(SERVICE, lightning_fixture, "start")

    assert result.returncode == 1
    assert "symlink_not_allowed" in result.stderr
    assert target.read_text(encoding="utf-8") == "target-must-remain\n"
    assert not (lightning_fixture.workspace_root / LOCK_DIRECTORY_NAME).exists()


def test_state_root_and_lock_symlinks_are_rejected(
    lightning_fixture: LightningFixture,
) -> None:
    state_target = lightning_fixture.workspace_root / "state-target"
    state_target.mkdir()
    lightning_fixture.state_root.symlink_to(state_target, target_is_directory=True)

    state_result = _run(SERVICE, lightning_fixture, "start")

    assert state_result.returncode == 1
    assert "symlink_component_not_allowed" in state_result.stderr
    assert list(state_target.iterdir()) == []

    lightning_fixture.state_root.unlink()
    lock_target = lightning_fixture.workspace_root / "lock-target"
    lock_target.mkdir()
    lock_path = lightning_fixture.workspace_root / LOCK_DIRECTORY_NAME
    lock_path.symlink_to(lock_target, target_is_directory=True)

    lock_result = _run(SERVICE, lightning_fixture, "start")

    assert lock_result.returncode == 1
    assert "symlink_not_allowed" in lock_result.stderr
    assert list(lock_target.iterdir()) == []


@pytest.mark.parametrize("artifact_name", ["basic-preview.pid", "basic-preview.log"])
def test_non_regular_state_artifact_is_rejected(
    lightning_fixture: LightningFixture,
    artifact_name: str,
) -> None:
    _create_owned_state(lightning_fixture)
    fifo_path = lightning_fixture.state_root / artifact_name
    os.mkfifo(fifo_path)

    result = _run(SERVICE, lightning_fixture, "start")

    assert result.returncode == 1
    assert "regular_file_required" in result.stderr
    assert stat.S_ISFIFO(fifo_path.stat().st_mode)


def test_non_directory_lock_and_owner_symlink_are_rejected(
    lightning_fixture: LightningFixture,
) -> None:
    lock_path = lightning_fixture.workspace_root / LOCK_DIRECTORY_NAME
    lock_path.write_text("must-not-be-overwritten\n", encoding="utf-8")

    non_directory = _run(SERVICE, lightning_fixture, "start")

    assert non_directory.returncode == 1
    assert "directory_required" in non_directory.stderr
    assert lock_path.read_text(encoding="utf-8") == "must-not-be-overwritten\n"

    lock_path.unlink()
    lock_path.mkdir(mode=0o700)
    owner_target = lightning_fixture.workspace_root / "owner-target"
    owner_target.write_text("target-must-remain\n", encoding="utf-8")
    (lock_path / "owner.pid").symlink_to(owner_target)

    owner_symlink = _run(SERVICE, lightning_fixture, "start")

    assert owner_symlink.returncode == 1
    assert "symlink_not_allowed" in owner_symlink.stderr
    assert owner_target.read_text(encoding="utf-8") == "target-must-remain\n"


def test_concurrent_start_is_atomic_and_tracks_at_most_one_process(
    lightning_fixture: LightningFixture,
) -> None:
    updates = {"MARGPA_TEST_HEALTH_DELAY": "0.5"}
    first = _popen_service(lightning_fixture, "start", environment_updates=updates)
    time.sleep(0.05)
    second = _popen_service(lightning_fixture, "start", environment_updates=updates)
    try:
        first_stdout, first_stderr = first.communicate(timeout=15)
        second_stdout, second_stderr = second.communicate(timeout=15)
        return_codes = {first.returncode, second.returncode}
        combined = first_stdout + first_stderr + second_stdout + second_stderr

        assert return_codes == {0, 1}
        assert "lifecycle_lock" in combined or "already_running" in combined
        active_entries = [
            line
            for line in lightning_fixture.process_registry.read_text(encoding="utf-8").splitlines()
            if line
        ]
        assert len(active_entries) == 1
        assert (lightning_fixture.state_root / "basic-preview.pid").is_file()
    finally:
        _run(SERVICE, lightning_fixture, "stop", "--force")


def test_stale_lifecycle_lock_is_recovered_without_signalling_owner(
    lightning_fixture: LightningFixture,
) -> None:
    lock_path = lightning_fixture.workspace_root / LOCK_DIRECTORY_NAME
    lock_path.mkdir(mode=0o700)
    owner_file = lock_path / "owner.pid"
    owner_file.write_text(f"{LOCK_OWNER_VALUE}\n99999999\n", encoding="utf-8")
    owner_file.chmod(0o600)
    try:
        started = _run(SERVICE, lightning_fixture, "start")

        assert started.returncode == 0, started.stderr
        assert "stale_lifecycle_lock_removed" in started.stdout
        assert "status=running" in started.stdout
    finally:
        _run(SERVICE, lightning_fixture, "stop", "--force")


def test_identity_failure_cleans_the_spawned_alive_child(
    lightning_fixture: LightningFixture,
) -> None:
    result = _run(
        SERVICE,
        lightning_fixture,
        "start",
        environment_updates={"MARGPA_TEST_IDENTITY": "invalid"},
    )

    assert result.returncode == 1
    assert "process_identity_not_verified_child_cleaned" in result.stderr
    assert not (lightning_fixture.state_root / "basic-preview.pid").exists()
    assert not (lightning_fixture.workspace_root / LOCK_DIRECTORY_NAME).exists()
    assert lightning_fixture.process_registry.read_text(encoding="utf-8") == ""
    _assert_processes_stopped(_spawned_pids(lightning_fixture))


def test_identity_cleanup_failure_retains_evidence_for_forced_recovery(
    lightning_fixture: LightningFixture,
) -> None:
    updates = {
        "MARGPA_TEST_IDENTITY": "invalid",
        "MARGPA_TEST_IGNORE_TERM": "1",
    }
    try:
        result = _run(
            SERVICE,
            lightning_fixture,
            "start",
            environment_updates=updates,
        )

        assert result.returncode == 1
        assert (
            "process_identity_not_verified_cleanup_incomplete_pid_evidence_retained"
            in result.stderr
        )
        pid_file = lightning_fixture.state_root / "basic-preview.pid"
        evidence = pid_file.read_text(encoding="utf-8").splitlines()
        assert len(evidence) == 2
        assert all(evidence)

        recovered = _run(
            SERVICE,
            lightning_fixture,
            "stop",
            "--force",
            environment_updates=updates,
        )
        assert recovered.returncode == 0, recovered.stderr
        assert "status=stopped" in recovered.stdout
        assert not pid_file.exists()
        assert not (lightning_fixture.workspace_root / LOCK_DIRECTORY_NAME).exists()
        _assert_processes_stopped([int(evidence[0])])
    finally:
        _run(
            SERVICE,
            lightning_fixture,
            "stop",
            "--force",
            environment_updates=updates,
        )


def test_health_cleanup_failure_is_distinct_and_retains_evidence(
    lightning_fixture: LightningFixture,
) -> None:
    updates = {
        "MARGPA_TEST_HEALTH": "fail",
        "MARGPA_TEST_IGNORE_TERM": "1",
    }
    try:
        result = _run(
            SERVICE,
            lightning_fixture,
            "start",
            environment_updates=updates,
        )

        assert result.returncode == 1
        assert "health_check_timeout_cleanup_incomplete_pid_evidence_retained" in result.stderr
        assert (lightning_fixture.state_root / "basic-preview.pid").is_file()
    finally:
        recovered = _run(
            SERVICE,
            lightning_fixture,
            "stop",
            "--force",
            environment_updates=updates,
        )
        assert recovered.returncode == 0, recovered.stderr


@pytest.mark.parametrize(
    ("target_name", "invalid_kind"),
    [
        ("MARGPA_WEB_AUTH_USERNAME", "whitespace"),
        ("MARGPA_WEB_AUTH_PASSWORD", "whitespace"),
        ("MARGPA_WEB_AUTH_USERNAME", "colon"),
        ("MARGPA_WEB_AUTH_USERNAME", "carriage_return"),
        ("MARGPA_WEB_AUTH_USERNAME", "line_feed"),
        ("MARGPA_WEB_AUTH_PASSWORD", "carriage_return"),
        ("MARGPA_WEB_AUTH_PASSWORD", "line_feed"),
    ],
)
def test_invalid_credential_formats_fail_closed_without_value_exposure(
    lightning_fixture: LightningFixture,
    target_name: str,
    invalid_kind: str,
) -> None:
    prefix = secrets.token_urlsafe(10)
    suffix = secrets.token_urlsafe(10)
    invalid_values = {
        "whitespace": " \t ",
        "colon": f"{prefix}:{suffix}",
        "carriage_return": f"{prefix}\r{suffix}",
        "line_feed": f"{prefix}\n{suffix}",
    }
    invalid_value = invalid_values[invalid_kind]

    result = _run(
        SERVICE,
        lightning_fixture,
        "preflight",
        environment_updates={target_name: invalid_value},
    )

    assert result.returncode == 1
    assert "credentials" in result.stderr
    assert invalid_value not in result.stdout + result.stderr
    assert not lightning_fixture.state_root.exists()
