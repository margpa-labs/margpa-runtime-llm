"""Opt-in Phase 1-F Lightning CUDA or CPU native acceptance test."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[3]
ACCEPTANCE_SCRIPT = PROJECT_ROOT / "scripts/models/phase1f_cross_environment_acceptance.py"
PROFILE_ENVIRONMENT_VARIABLE = "MARGPA_PHASE1F_PROFILE"


@pytest.mark.model_smoke
def test_phase1f_lightning_native_runtime() -> None:
    profile = os.environ.get(PROFILE_ENVIRONMENT_VARIABLE)
    if profile is None:
        pytest.skip(f"{PROFILE_ENVIRONMENT_VARIABLE} is not set")

    completed = subprocess.run(
        [sys.executable, str(ACCEPTANCE_SCRIPT), "--profile", profile],
        cwd=PROJECT_ROOT,
        check=False,
        capture_output=True,
        text=True,
        timeout=900,
    )

    assert completed.returncode == 0, completed.stderr or completed.stdout
    report = json.loads(completed.stdout)
    assert report["success"] is True
    assert report["all_required_checks_passed"] is True
    assert all(report["required_checks"].values())
    assert Path(report["model_artifact_path"]).parts[-4:] == (
        "main",
        "qwen3-4b",
        "gguf",
        "Qwen3-4B-Q4_K_M.gguf",
    )

    if profile.endswith("_cuda.toml"):
        assert report["runtime"]["backend_build_variant"] == "cuda"
        assert report["runtime"]["device_kind"] == "gpu"
        assert report["runtime"]["acceleration_api"] == "cuda"
        assert report["runtime"]["gpu_offload"] is True
        assert report["runtime"]["gpu_offload_evidence"]["supported"] is True
        assert report["runtime"]["gpu_offload_evidence"]["requested"] is True
        assert report["runtime"]["gpu_offload_evidence"]["observed"] is True
        assert report["runtime"]["gpu_offload_evidence"]["process_gpu_memory_bytes"] > 0
    elif profile.endswith("_cpu.toml"):
        assert report["runtime"]["backend_build_variant"] == "cuda"
        assert report["runtime"]["device_kind"] == "cpu"
        assert report["runtime"]["acceleration_api"] == "cpu_native"
        assert report["runtime"]["gpu_offload"] is False
        assert report["runtime"]["gpu_offload_evidence"]["supported"] is True
        assert report["runtime"]["gpu_offload_evidence"]["requested"] is False
        assert report["runtime"]["gpu_offload_evidence"]["observed"] is False
    elif profile.endswith("_cpu_native.toml"):
        assert report["runtime"]["backend_build_variant"] == "cpu"
        assert report["runtime"]["device_kind"] == "cpu"
        assert report["runtime"]["acceleration_api"] == "none"
        assert report["runtime"]["gpu_offload"] is False
        assert report["runtime"]["gpu_offload_evidence"]["supported"] is False
        assert report["runtime"]["gpu_offload_evidence"]["requested"] is False
        assert report["runtime"]["gpu_offload_evidence"]["observed"] is False
    else:
        pytest.fail("MARGPA_PHASE1F_PROFILE must select a tracked Lightning profile")
