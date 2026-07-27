"""Isolated llama.cpp device observation for the current native backend."""

from __future__ import annotations

import os
import subprocess
from collections.abc import Callable
from dataclasses import dataclass
from typing import Literal

type GpuOffloadObservationSource = Literal[
    "metal_model_load",
    "nvidia_process_memory",
    "not_requested",
    "unsupported",
    "observation_unavailable",
]
type NvidiaSmiCommandRunner = Callable[
    [tuple[str, ...]],
    subprocess.CompletedProcess[str],
]

NVIDIA_PROCESS_MEMORY_COMMAND = (
    "nvidia-smi",
    "--query-compute-apps=pid,used_gpu_memory",
    "--format=csv,noheader,nounits",
)


@dataclass(frozen=True, slots=True)
class LlamaCppDeviceObservation:
    device: str
    build_variant: str
    device_kind: str
    acceleration_api: str
    gpu_offload: bool
    gpu_offload_supported: bool
    gpu_offload_requested: bool
    observation_source: GpuOffloadObservationSource
    process_gpu_memory_bytes: int | None = None


@dataclass(frozen=True, slots=True)
class NvidiaProcessMemoryObservation:
    query_available: bool
    process_gpu_memory_bytes: int | None


def observe_nvidia_process_gpu_memory(
    *,
    process_id: int | None = None,
    command_runner: NvidiaSmiCommandRunner | None = None,
) -> NvidiaProcessMemoryObservation:
    """Observe GPU memory assigned to this process through nvidia-smi."""

    target_process_id = os.getpid() if process_id is None else process_id
    runner = _run_nvidia_smi if command_runner is None else command_runner
    try:
        completed = runner(NVIDIA_PROCESS_MEMORY_COMMAND)
    except (OSError, subprocess.TimeoutExpired):
        return NvidiaProcessMemoryObservation(
            query_available=False,
            process_gpu_memory_bytes=None,
        )
    if completed.returncode != 0:
        return NvidiaProcessMemoryObservation(
            query_available=False,
            process_gpu_memory_bytes=None,
        )

    memory_mebibytes = 0
    process_seen = False
    for line in completed.stdout.splitlines():
        columns = tuple(column.strip() for column in line.split(","))
        if len(columns) != 2:
            continue
        try:
            row_process_id = int(columns[0])
            row_memory_mebibytes = int(columns[1])
        except ValueError:
            continue
        if row_process_id == target_process_id:
            process_seen = True
            memory_mebibytes += max(row_memory_mebibytes, 0)
    return NvidiaProcessMemoryObservation(
        query_available=True,
        process_gpu_memory_bytes=(memory_mebibytes * 1024 * 1024 if process_seen else None),
    )


def _run_nvidia_smi(
    command: tuple[str, ...],
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        check=False,
        capture_output=True,
        text=True,
        timeout=10,
    )


def detect_llama_cpp_device(
    *,
    system_info: str,
    gpu_offload_supported: bool,
    gpu_layers: int,
    nvidia_process_memory: NvidiaProcessMemoryObservation | None = None,
) -> LlamaCppDeviceObservation:
    """Classify only GPU use that has native post-load evidence."""

    build_variant = detect_llama_cpp_build_variant(
        system_info=system_info,
        gpu_offload_supported=gpu_offload_supported,
    )
    if gpu_layers == 0:
        acceleration_api = "none" if build_variant == "cpu" else "cpu_native"
        return LlamaCppDeviceObservation(
            device="cpu",
            build_variant=build_variant,
            device_kind="cpu",
            acceleration_api=acceleration_api,
            gpu_offload=False,
            gpu_offload_supported=gpu_offload_supported,
            gpu_offload_requested=False,
            observation_source="not_requested",
        )
    if not gpu_offload_supported or build_variant not in {"metal", "cuda"}:
        return LlamaCppDeviceObservation(
            device="cpu",
            build_variant=build_variant,
            device_kind="cpu",
            acceleration_api="cpu_native",
            gpu_offload=False,
            gpu_offload_supported=False,
            gpu_offload_requested=True,
            observation_source="unsupported",
        )
    if build_variant == "metal":
        return LlamaCppDeviceObservation(
            device="metal",
            build_variant=build_variant,
            device_kind="gpu",
            acceleration_api="metal",
            gpu_offload=True,
            gpu_offload_supported=True,
            gpu_offload_requested=True,
            observation_source="metal_model_load",
        )

    cuda_memory = nvidia_process_memory
    if (
        cuda_memory is not None
        and cuda_memory.query_available
        and (cuda_memory.process_gpu_memory_bytes or 0) > 0
    ):
        return LlamaCppDeviceObservation(
            device="cuda",
            build_variant="cuda",
            device_kind="gpu",
            acceleration_api="cuda",
            gpu_offload=True,
            gpu_offload_supported=True,
            gpu_offload_requested=True,
            observation_source="nvidia_process_memory",
            process_gpu_memory_bytes=cuda_memory.process_gpu_memory_bytes,
        )
    return LlamaCppDeviceObservation(
        device="cuda_unobserved",
        build_variant="cuda",
        device_kind="unknown",
        acceleration_api="cuda",
        gpu_offload=False,
        gpu_offload_supported=True,
        gpu_offload_requested=True,
        observation_source=(
            "nvidia_process_memory"
            if cuda_memory is not None and cuda_memory.query_available
            else "observation_unavailable"
        ),
        process_gpu_memory_bytes=(
            None if cuda_memory is None else cuda_memory.process_gpu_memory_bytes
        ),
    )


def detect_llama_cpp_build_variant(
    *,
    system_info: str,
    gpu_offload_supported: bool,
) -> str:
    normalized = system_info.upper()
    if "MTL" in normalized or "METAL" in normalized:
        return "metal"
    if "GGML_CUDA" in normalized or "CUDA" in normalized:
        return "cuda"
    return "unknown" if gpu_offload_supported else "cpu"
