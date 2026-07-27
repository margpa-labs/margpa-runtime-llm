"""Report and verify a supported Phase 1 native Python environment."""

from __future__ import annotations

import argparse
import importlib.metadata
import json
import platform
import subprocess
import sys
from pathlib import Path
from typing import Literal

from llama_cpp import llama_cpp

from margpa_runtime_llm.adapters.model_backends.llama_cpp.runtime_detection import (
    detect_llama_cpp_build_variant,
)
from margpa_runtime_llm.bootstrap.profile_resolver import (
    detect_host_platform,
    load_platform_registry,
)

type VerificationTarget = Literal[
    "macos-metal",
    "lightning-cuda",
    "lightning-cpu",
    "lightning-cpu-native",
]

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PLATFORM_REGISTRY_PATH = PROJECT_ROOT / "config/platforms/platform_registry.toml"

EXPECTED_DIRECT_DEPENDENCIES = {
    "ipykernel": "7.3.0",
    "jupyterlab": "4.6.1",
    "llama-cpp-python": "0.3.34",
    "mypy": "2.3.0",
    "notebook": "7.6.0",
    "psutil": "7.2.2",
    "pydantic": "2.13.4",
    "pydantic-settings": "2.14.2",
    "pytest": "9.1.1",
    "pytest-asyncio": "1.4.0",
    "pytest-cov": "7.1.0",
    "ruff": "0.15.22",
}

OUT_OF_SCOPE_PACKAGES = (
    "langchain",
    "langgraph",
    "mlx",
    "mlx-lm",
    "torch",
    "transformers",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--target",
        choices=(
            "macos-metal",
            "lightning-cuda",
            "lightning-cpu",
            "lightning-cpu-native",
        ),
        default="macos-metal",
        help="Environment contract to verify (default: macos-metal)",
    )
    return parser.parse_args()


def package_version(name: str) -> str | None:
    try:
        return importlib.metadata.version(name)
    except importlib.metadata.PackageNotFoundError:
        return None


def command_output(command: tuple[str, ...]) -> dict[str, object]:
    try:
        completed = subprocess.run(
            command,
            check=False,
            capture_output=True,
            text=True,
            timeout=10,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {
            "available": False,
            "return_code": None,
            "output": "",
            "error_type": type(exc).__name__,
        }
    output = completed.stdout.strip() or completed.stderr.strip()
    return {
        "available": completed.returncode == 0,
        "return_code": completed.returncode,
        "output": output,
        "error_type": None,
    }


def preload_backend_evidence_for(
    target: VerificationTarget,
    system_info: str,
) -> dict[str, object]:
    gpu_offload_supported = bool(llama_cpp.llama_supports_gpu_offload())
    build_variant = detect_llama_cpp_build_variant(
        system_info=system_info,
        gpu_offload_supported=gpu_offload_supported,
    )
    return {
        "build_variant": build_variant,
        "gpu_offload_supported": gpu_offload_supported,
        "gpu_offload_requested": target not in {"lightning-cpu", "lightning-cpu-native"},
        "gpu_offload_observed": None,
        "gpu_layers": 0 if target in {"lightning-cpu", "lightning-cpu-native"} else -1,
        "device_kind": ("cpu" if target in {"lightning-cpu", "lightning-cpu-native"} else "gpu"),
        "acceleration_api": (
            "none"
            if target == "lightning-cpu-native"
            else "cpu_native"
            if target == "lightning-cpu"
            else "metal"
            if target == "macos-metal"
            else "cuda"
        ),
        "observation_scope": "pre_load_only",
    }


def target_is_valid(
    *,
    target: VerificationTarget,
    python_version: str,
    host: dict[str, object],
    backend: dict[str, object],
    gil_enabled: bool | None,
    nvidia_smi: dict[str, object],
) -> bool:
    if gil_enabled is False:
        return False
    if target == "macos-metal":
        return (
            python_version == "3.13.14"
            and host["operating_system_key"] == "macos"
            and host["architecture_key"] == "arm64"
            and host["execution_environment_key"] == "native"
            and backend["build_variant"] == "metal"
            and backend["gpu_offload_supported"] is True
            and backend["gpu_offload_requested"] is True
            and backend["gpu_offload_observed"] is None
        )
    if target == "lightning-cpu-native":
        return (
            python_version == "3.12.11"
            and host["operating_system_key"] == "linux"
            and host["architecture_key"] == "x86_64"
            and host["execution_environment_key"] == "container"
            and host["distribution_key"] == "ubuntu"
            and backend["build_variant"] == "cpu"
            and backend["device_kind"] == "cpu"
            and backend["acceleration_api"] == "none"
            and backend["gpu_offload_supported"] is False
            and backend["gpu_offload_requested"] is False
            and backend["gpu_offload_observed"] is None
            and backend["gpu_layers"] == 0
        )
    common_lightning = (
        python_version == "3.12.11"
        and host["operating_system_key"] == "linux"
        and host["architecture_key"] == "x86_64"
        and host["execution_environment_key"] == "container"
        and host["distribution_key"] == "ubuntu"
        and backend["build_variant"] == "cuda"
        and backend["gpu_offload_supported"] is True
        and backend["gpu_offload_observed"] is None
    )
    if target == "lightning-cuda":
        return (
            common_lightning
            and backend["gpu_offload_requested"] is True
            and nvidia_smi["available"] is True
        )
    return common_lightning and backend["gpu_offload_requested"] is False


def main() -> int:
    args = parse_args()
    target: VerificationTarget = args.target
    gil_check = getattr(sys, "_is_gil_enabled", None)
    gil_enabled = bool(gil_check()) if gil_check is not None else None
    direct_dependencies = {name: package_version(name) for name in EXPECTED_DIRECT_DEPENDENCIES}
    out_of_scope_packages = {name: package_version(name) for name in OUT_OF_SCOPE_PACKAGES}
    system_info = llama_cpp.llama_print_system_info().decode("utf-8", errors="replace")
    backend_evidence = preload_backend_evidence_for(target, system_info)
    registry = load_platform_registry(PLATFORM_REGISTRY_PATH)
    detected_host = detect_host_platform(registry=registry)
    host = detected_host.model_dump(mode="json")
    nvidia_smi: dict[str, object]
    nvcc: dict[str, object]
    if target == "lightning-cpu-native":
        nvidia_smi = {
            "available": False,
            "return_code": None,
            "output": "",
            "error_type": None,
            "status": "not_required_not_probed",
        }
        nvcc = {
            "available": False,
            "return_code": None,
            "output": "",
            "error_type": None,
            "status": "not_required_not_probed",
        }
    else:
        nvidia_smi = command_output(
            (
                "nvidia-smi",
                "--query-gpu=name,memory.total,driver_version",
                "--format=csv,noheader",
            )
        )
        nvcc = command_output(("nvcc", "--version"))
    dependency_versions_match = direct_dependencies == EXPECTED_DIRECT_DEPENDENCIES
    out_of_scope_absent = all(version is None for version in out_of_scope_packages.values())
    python_version = platform.python_version()
    native_contract_valid = target_is_valid(
        target=target,
        python_version=python_version,
        host=host,
        backend=backend_evidence,
        gil_enabled=gil_enabled,
        nvidia_smi=nvidia_smi,
    )
    report = {
        "target": target,
        "python": {
            "version": python_version,
            "implementation": platform.python_implementation(),
            "gil_enabled": gil_enabled,
            "executable": sys.executable,
        },
        "host": host,
        "venv": {
            "logical_path": str(Path(sys.prefix).absolute()),
            "resolved_path": str(Path(sys.prefix).resolve()),
            "resolved_python": str(Path(sys.executable).resolve()),
        },
        "backend": {
            "system_info": system_info,
            "preload_evidence": backend_evidence,
            "actual_gpu_offload": {
                "observed": None,
                "reason": "requires_native_model_load",
            },
        },
        "nvidia_smi": nvidia_smi,
        "nvcc": nvcc,
        "direct_dependencies": direct_dependencies,
        "out_of_scope_packages": out_of_scope_packages,
        "validation": {
            "native_contract_valid": native_contract_valid,
            "dependency_versions_match": dependency_versions_match,
            "out_of_scope_packages_absent": out_of_scope_absent,
        },
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if native_contract_valid and dependency_versions_match and out_of_scope_absent else 1


if __name__ == "__main__":
    raise SystemExit(main())
