"""Repository contracts for the Lightning Pure CPU setup hooks."""

from __future__ import annotations

import os
import runpy
import shlex
import subprocess
import sys
import tomllib
from collections.abc import Callable
from pathlib import Path
from typing import cast

PROJECT_ROOT = Path(__file__).resolve().parents[3]
PREFLIGHT = PROJECT_ROOT / "scripts/setup/preflight_lightning_ai_studio.sh"
SETUP = PROJECT_ROOT / "scripts/setup/setup_lightning_linux_x86_64_cpu.sh"
VERIFY = PROJECT_ROOT / "scripts/setup/verify_phase1_environment.py"
ACCEPTANCE = PROJECT_ROOT / "scripts/models/phase1f_cross_environment_acceptance.py"
PROFILE = PROJECT_ROOT / "config/profiles/lightning_linux_x86_64_cpu_native.toml"
MODEL_RELATIVE_PATH = Path("main/qwen3-4b/gguf/Qwen3-4B-Q4_K_M.gguf")


def _write_executable(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")
    path.chmod(0o755)


def _mocked_preflight_environment(
    tmp_path: Path,
    *,
    system: str = "Linux",
    machine: str = "x86_64",
) -> tuple[dict[str, str], Path]:
    tmp_path.mkdir(parents=True, exist_ok=True)
    bin_path = tmp_path / "bin"
    bin_path.mkdir()
    command_log = tmp_path / "commands.log"
    os_release = tmp_path / "os-release"
    os_release.write_text('ID="ubuntu"\n', encoding="utf-8")

    _write_executable(
        bin_path / "uname",
        f"""#!/bin/bash
case "${{1:-}}" in
  -s) printf '%s\\n' {shlex.quote(system)} ;;
  -m) printf '%s\\n' {shlex.quote(machine)} ;;
  *) exit 2 ;;
esac
""",
    )
    _write_executable(
        bin_path / "python3",
        f"""#!/bin/bash
if [[ "${{1:-}}" == "--version" ]]; then
  printf 'Python 3.12.11\\n'
  exit 0
fi
exec {shlex.quote(sys.executable)} "$@"
""",
    )
    _write_executable(
        bin_path / "uv",
        f"""#!/bin/bash
if [[ "${{1:-}}" == "--version" ]]; then
  printf 'uv 0.11.29\\n'
  exit 0
fi
printf 'uv %s\\n' "$*" >> {shlex.quote(str(command_log))}
""",
    )
    for command in ("nvidia-smi", "nvcc"):
        _write_executable(
            bin_path / command,
            f"""#!/bin/bash
printf '{command} %s\\n' "$*" >> {shlex.quote(str(command_log))}
exit 0
""",
        )

    environment = dict(os.environ)
    environment["PATH"] = f"{bin_path}:{environment['PATH']}"
    environment["PHASE1F_PREFLIGHT_OS_RELEASE_PATH"] = str(os_release)
    environment["PHASE1F_PREFLIGHT_CONTAINER_MARKER"] = "present"
    environment["PHASE1F_PREFLIGHT_AVAILABLE_MEMORY_BYTES"] = str(16 * 1024**3)
    environment.pop("VIRTUAL_ENV", None)
    environment.pop("CONDA_PREFIX", None)
    environment.pop("MARGPA_MODEL_ROOT", None)
    return environment, command_log


def _run_preflight(
    environment: dict[str, str],
    *arguments: str,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [str(PREFLIGHT), *arguments],
        cwd=PROJECT_ROOT,
        env=environment,
        check=False,
        capture_output=True,
        text=True,
        timeout=30,
    )


def test_pure_cpu_profile_has_no_acceleration_and_denies_fallback() -> None:
    with PROFILE.open("rb") as profile_file:
        profile = tomllib.load(profile_file)

    assert profile["profile_key"] == "external.lightning-linux-x86_64.cpu-native"
    assert profile["backend_runtime"]["build_variant_key"] == "cpu"
    assert profile["compute"]["compute_kind_key"] == "cpu"
    assert profile["compute"]["vendor_key"] == "generic"
    assert profile["compute"]["acceleration_api_key"] == "none"
    assert profile["runtime_requirements"]["required_device_kind"] == "cpu"
    assert profile["runtime_requirements"]["required_acceleration_api"] == "none"
    assert profile["runtime_requirements"]["fallback_policy"] == "deny"
    assert profile["load_overrides"]["gpu_layers"] == 0


def test_preflight_preserves_default_and_cpu_only_semantics(tmp_path: Path) -> None:
    environment, command_log = _mocked_preflight_environment(tmp_path)

    default = _run_preflight(environment)
    assert default.returncode == 0, default.stderr
    assert "Runtime target   : cuda-gpu" in default.stdout
    assert "GPU required     : yes" in default.stdout
    assert "nvidia-smi -L" in command_log.read_text(encoding="utf-8")
    assert "nvcc --version" in command_log.read_text(encoding="utf-8")

    command_log.write_text("", encoding="utf-8")
    cpu_only = _run_preflight(environment, "--cpu-only")
    assert cpu_only.returncode == 0, cpu_only.stderr
    assert "Runtime target   : cuda-cpu" in cpu_only.stdout
    assert "GPU required     : no" in cpu_only.stdout
    logged = command_log.read_text(encoding="utf-8")
    assert "nvidia-smi" not in logged
    assert "nvcc --version" in logged


def test_cpu_native_preflight_never_invokes_gpu_or_toolchain_commands(
    tmp_path: Path,
) -> None:
    environment, command_log = _mocked_preflight_environment(tmp_path)

    completed = _run_preflight(environment, "--runtime-target", "cpu-native")

    assert completed.returncode == 0, completed.stderr
    assert "Runtime target   : cpu-native" in completed.stdout
    assert "Pure CPU Profile : parseable" in completed.stdout
    assert "GPU required     : no" in completed.stdout
    assert "nvcc available   : not_probed" in completed.stdout
    assert "CPU count        :" in completed.stdout
    assert "Available memory :" in completed.stdout
    assert not command_log.exists() or command_log.read_text(encoding="utf-8") == ""


def test_preflight_help_unknown_target_conflict_and_mac_rejection(tmp_path: Path) -> None:
    environment, _ = _mocked_preflight_environment(tmp_path)

    help_result = _run_preflight(environment, "--help")
    assert help_result.returncode == 0
    assert "cuda-gpu" in help_result.stdout
    assert "cuda-cpu" in help_result.stdout
    assert "cpu-native" in help_result.stdout
    assert "--cpu-only" in help_result.stdout

    unknown = _run_preflight(environment, "--runtime-target", "other")
    assert unknown.returncode == 1
    assert "must be cuda-gpu, cuda-cpu, or cpu-native" in unknown.stderr

    conflict = _run_preflight(
        environment,
        "--cpu-only",
        "--runtime-target",
        "cpu-native",
    )
    assert conflict.returncode == 1
    assert "conflicts" in conflict.stderr

    mac_environment, _ = _mocked_preflight_environment(
        tmp_path / "mac",
        system="Darwin",
        machine="arm64",
    )
    mac = _run_preflight(mac_environment, "--runtime-target", "cpu-native")
    assert mac.returncode == 1
    assert "requires Linux" in mac.stderr


def test_setup_and_preflight_shell_syntax_and_plan_are_safe(tmp_path: Path) -> None:
    for script in (PREFLIGHT, SETUP):
        syntax = subprocess.run(
            ["bash", "-n", str(script)],
            cwd=PROJECT_ROOT,
            check=False,
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert syntax.returncode == 0, syntax.stderr

    model_root = tmp_path / "model-root"
    model_path = model_root / MODEL_RELATIVE_PATH
    model_path.parent.mkdir(parents=True)
    model_path.write_bytes(b"repository-contract-placeholder")
    plan = subprocess.run(
        [
            str(SETUP),
            "--plan",
            "--model-smoke",
            "--model-root",
            str(model_root),
        ],
        cwd=PROJECT_ROOT,
        check=False,
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert plan.returncode == 0, plan.stderr
    assert "no changes" in plan.stdout
    assert "Pure CPU backend" in plan.stdout
    assert "bounded smoke" in plan.stdout
    assert f"Model Root       : {model_root}" in plan.stdout
    assert f"Resolved Artifact: {model_path}" in plan.stdout

    help_result = subprocess.run(
        [str(SETUP), "--help"],
        cwd=PROJECT_ROOT,
        check=False,
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert help_result.returncode == 0
    assert "--model-root" in help_result.stdout
    assert "--model-path" in help_result.stdout

    setup_source = SETUP.read_text(encoding="utf-8")
    assert "nvidia-smi" not in setup_source
    assert "nvcc" not in setup_source
    assert "lightning-cpu-native" in setup_source
    assert "--no-binary llama-cpp-python" in setup_source
    assert "llama-cpp-python==0.3.34" in setup_source
    assert "download" in setup_source
    assert '--model-root "${phase1f_model_root}"' in setup_source
    assert "MARGPA_MODEL_ROOT=" not in setup_source


def test_model_path_compatibility_requires_registry_layout(tmp_path: Path) -> None:
    model_root = tmp_path / "models"
    model_path = model_root / MODEL_RELATIVE_PATH
    model_path.parent.mkdir(parents=True)
    model_path.write_bytes(b"repository-contract-placeholder")
    environment = dict(os.environ)
    environment.pop("MARGPA_MODEL_ROOT", None)
    environment.pop("MARGPA_PROFILE", None)

    compatible = subprocess.run(
        [
            str(SETUP),
            "--plan",
            "--model-smoke",
            "--model-path",
            str(model_path),
        ],
        cwd=PROJECT_ROOT,
        env=environment,
        check=False,
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert compatible.returncode == 0, compatible.stderr
    assert f"Model Root       : {model_root}" in compatible.stdout
    assert f"Resolved Artifact: {model_path}" in compatible.stdout

    invalid_path = tmp_path / "arbitrary.gguf"
    invalid_path.write_bytes(b"wrong-layout")
    invalid = subprocess.run(
        [str(SETUP), "--plan", "--model-path", str(invalid_path)],
        cwd=PROJECT_ROOT,
        env=environment,
        check=False,
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert invalid.returncode == 1
    assert "does not match the Registry artifact layout" in invalid.stderr

    other_root = tmp_path / "other-models"
    mismatch = subprocess.run(
        [
            str(SETUP),
            "--plan",
            "--model-root",
            str(other_root),
            "--model-path",
            str(model_path),
        ],
        cwd=PROJECT_ROOT,
        env=environment,
        check=False,
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert mismatch.returncode == 1
    assert "does not match the Registry artifact layout" in mismatch.stderr


def test_verification_target_skips_gpu_commands_for_pure_cpu() -> None:
    source = VERIFY.read_text(encoding="utf-8")
    pure_cpu_branch = source.index('if target == "lightning-cpu-native":')
    command_branch = source.index("else:", pure_cpu_branch)
    skipped_section = source[pure_cpu_branch:command_branch]

    assert '"build_variant"] == "cpu"' in source
    assert '"acceleration_api"] == "none"' in source
    assert '"gpu_layers"] == 0' in source
    assert '"status": "not_required_not_probed"' in skipped_section
    assert "command_output" not in skipped_section


def test_pure_cpu_verification_contract_fails_closed_on_acceleration_mismatch() -> None:
    target_is_valid = cast(
        Callable[..., bool],
        runpy.run_path(
            str(VERIFY),
            run_name="phase1_environment_verification_contract",
        )["target_is_valid"],
    )
    host: dict[str, object] = {
        "operating_system_key": "linux",
        "architecture_key": "x86_64",
        "execution_environment_key": "container",
        "distribution_key": "ubuntu",
    }
    backend: dict[str, object] = {
        "build_variant": "cpu",
        "device_kind": "cpu",
        "acceleration_api": "none",
        "gpu_offload_supported": False,
        "gpu_offload_requested": False,
        "gpu_offload_observed": None,
        "gpu_layers": 0,
    }
    unavailable_gpu: dict[str, object] = {"available": False}

    assert target_is_valid(
        target="lightning-cpu-native",
        python_version="3.12.11",
        host=host,
        backend=backend,
        gil_enabled=True,
        nvidia_smi=unavailable_gpu,
    )
    assert not target_is_valid(
        target="lightning-cpu-native",
        python_version="3.12.11",
        host=host,
        backend={**backend, "acceleration_api": "cpu_native"},
        gil_enabled=True,
        nvidia_smi=unavailable_gpu,
    )
    assert not target_is_valid(
        target="lightning-cpu-native",
        python_version="3.12.11",
        host=host,
        backend={**backend, "build_variant": "cuda"},
        gil_enabled=True,
        nvidia_smi=unavailable_gpu,
    )


def test_native_acceptance_matches_each_profile_acceleration_and_fails_closed() -> None:
    namespace = runpy.run_path(
        str(ACCEPTANCE),
        run_name="phase1f_acceptance_contract",
    )
    matches = cast(Callable[..., bool], namespace["runtime_evidence_matches_profile"])
    checks_pass = cast(Callable[[dict[str, bool]], bool], namespace["all_required_checks_passed"])

    cuda_gpu = matches(
        expected_compute_kind="gpu",
        expected_acceleration_api="cuda",
        runtime_device_kind="gpu",
        runtime_acceleration_api="cuda",
        runtime_gpu_offload=True,
        gpu_offload_supported=True,
        gpu_offload_requested=True,
        gpu_offload_observed=True,
    )
    cuda_cpu = matches(
        expected_compute_kind="cpu",
        expected_acceleration_api="cpu_native",
        runtime_device_kind="cpu",
        runtime_acceleration_api="cpu_native",
        runtime_gpu_offload=False,
        gpu_offload_supported=True,
        gpu_offload_requested=False,
        gpu_offload_observed=False,
    )
    pure_cpu = matches(
        expected_compute_kind="cpu",
        expected_acceleration_api="none",
        runtime_device_kind="cpu",
        runtime_acceleration_api="none",
        runtime_gpu_offload=False,
        gpu_offload_supported=False,
        gpu_offload_requested=False,
        gpu_offload_observed=False,
    )
    mismatch = matches(
        expected_compute_kind="cpu",
        expected_acceleration_api="none",
        runtime_device_kind="cpu",
        runtime_acceleration_api="cpu_native",
        runtime_gpu_offload=False,
        gpu_offload_supported=False,
        gpu_offload_requested=False,
        gpu_offload_observed=False,
    )
    unknown_compute = matches(
        expected_compute_kind="npu",
        expected_acceleration_api="none",
        runtime_device_kind="cpu",
        runtime_acceleration_api="none",
        runtime_gpu_offload=False,
        gpu_offload_supported=False,
        gpu_offload_requested=False,
        gpu_offload_observed=False,
    )

    assert cuda_gpu
    assert cuda_cpu
    assert pure_cpu
    assert not mismatch
    assert not unknown_compute
    assert checks_pass(
        {
            "artifact_sha512_matches_definition": True,
            "runtime_evidence_matches_profile": pure_cpu,
            "bounded_generation_checks": True,
        }
    )
    assert not checks_pass({"runtime_evidence_matches_profile": False})
