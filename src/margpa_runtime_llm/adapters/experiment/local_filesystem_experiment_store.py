"""Local Filesystem `ExperimentStorePort` implementation (Phase 9-2, WU-A A3).

One JSON file per persisted object under `base_dir`:

    <base_dir>/plans/<experiment_id>.json
    <base_dir>/runs/<run_id>.json
    <base_dir>/raw_evidence/<run_id>.json
    <base_dir>/comparisons/<experiment_id>.json

Every write is temp-file-then-`Path.replace` (POSIX-atomic, replace-on-
collision on the same filesystem), so a crash mid-write can only ever
leave an orphaned `.tmp` file, never a half-written target a later
Restart-read could observe -- WU-A A3's "Restart後にRun/Variant/Raw
Evidence/Comparisonを読める" requirement.

This Store does not carry the Recording Writer's full dir_fd/symlink/
cross-process-lock/quota hardening (`adapters.runtime_observability.
local_filesystem_recording_writer`): that Writer defends a materially
different threat model (Recording Envelopes derived from live Request
content, written by potentially multiple processes against a shared
quota). Experiment Plan/Run identifiers are Composition-Root-supplied,
not attacker-reachable, and there is exactly one Store instance per
process here -- but an unsafe (traversing) identifier is still rejected
outright before any filesystem operation, never silently accepted."""

from __future__ import annotations

import json
import re
from pathlib import Path
from threading import Lock
from typing import Any

from margpa_runtime_llm.modules.experiment.domain.identity import ExperimentPlan
from margpa_runtime_llm.modules.experiment.domain.run import VariantRun

_SAFE_ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")


class ExperimentStorePathRejected(Exception):
    """An `experiment_id`/`run_id` failed the safe-filename check before
    any filesystem operation was attempted."""


def _safe_file_name(identifier: str, *, kind: str) -> str:
    if not _SAFE_ID_PATTERN.match(identifier):
        raise ExperimentStorePathRejected(f"unsafe {kind} for a store file name: {identifier!r}")
    return f"{identifier}.json"


class LocalFilesystemExperimentStore:
    def __init__(self, *, base_dir: Path) -> None:
        self._base_dir = base_dir
        self._lock = Lock()

    def _write_json(self, sub_dir: str, file_name: str, payload: dict[str, Any]) -> None:
        directory = self._base_dir / sub_dir
        directory.mkdir(parents=True, exist_ok=True)
        target = directory / file_name
        tmp = directory / f".{file_name}.tmp"
        data = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        with self._lock:
            tmp.write_text(data, encoding="utf-8")
            tmp.replace(target)

    def _read_json(self, sub_dir: str, file_name: str) -> dict[str, Any] | None:
        target = self._base_dir / sub_dir / file_name
        if not target.is_file():
            return None
        payload: dict[str, Any] = json.loads(target.read_text(encoding="utf-8"))
        return payload

    def save_plan(self, plan: ExperimentPlan) -> None:
        file_name = _safe_file_name(plan.experiment_id, kind="experiment_id")
        self._write_json("plans", file_name, plan.model_dump(mode="json"))

    def load_plan(self, experiment_id: str) -> ExperimentPlan | None:
        file_name = _safe_file_name(experiment_id, kind="experiment_id")
        payload = self._read_json("plans", file_name)
        if payload is None:
            return None
        return ExperimentPlan.model_validate(payload)

    def save_run(self, run: VariantRun) -> None:
        file_name = _safe_file_name(run.run_id, kind="run_id")
        self._write_json("runs", file_name, run.model_dump(mode="json"))

    def load_run(self, run_id: str) -> VariantRun | None:
        file_name = _safe_file_name(run_id, kind="run_id")
        payload = self._read_json("runs", file_name)
        if payload is None:
            return None
        return VariantRun.model_validate(payload)

    def list_runs(self, experiment_id: str) -> tuple[VariantRun, ...]:
        return tuple(run for run in self.list_all_runs() if run.experiment_id == experiment_id)

    def list_all_runs(self) -> tuple[VariantRun, ...]:
        directory = self._base_dir / "runs"
        if not directory.is_dir():
            return ()
        runs = []
        for path in sorted(directory.glob("*.json")):
            if path.name.startswith("."):
                continue
            run = VariantRun.model_validate(json.loads(path.read_text(encoding="utf-8")))
            runs.append(run)
        return tuple(runs)

    def save_raw_evidence(self, run_id: str, evidence: dict[str, Any]) -> None:
        file_name = _safe_file_name(run_id, kind="run_id")
        self._write_json("raw_evidence", file_name, dict(evidence))

    def load_raw_evidence(self, run_id: str) -> dict[str, Any] | None:
        file_name = _safe_file_name(run_id, kind="run_id")
        return self._read_json("raw_evidence", file_name)

    def save_comparison(self, experiment_id: str, comparison: dict[str, Any]) -> None:
        file_name = _safe_file_name(experiment_id, kind="experiment_id")
        self._write_json("comparisons", file_name, dict(comparison))

    def load_comparison(self, experiment_id: str) -> dict[str, Any] | None:
        file_name = _safe_file_name(experiment_id, kind="experiment_id")
        return self._read_json("comparisons", file_name)

    def save_run_configuration_snapshot(self, run_id: str, snapshot: dict[str, Any]) -> None:
        file_name = _safe_file_name(run_id, kind="run_id")
        self._write_json("run_configuration_snapshots", file_name, dict(snapshot))

    def load_run_configuration_snapshot(self, run_id: str) -> dict[str, Any] | None:
        file_name = _safe_file_name(run_id, kind="run_id")
        return self._read_json("run_configuration_snapshots", file_name)

    def save_variant_desired_configuration(
        self, experiment_id: str, variant_id: str, snapshot: dict[str, Any]
    ) -> None:
        experiment_sub_dir = _safe_file_name(experiment_id, kind="experiment_id")[: -len(".json")]
        file_name = _safe_file_name(variant_id, kind="variant_id")
        self._write_json(
            f"variant_desired_configuration/{experiment_sub_dir}", file_name, dict(snapshot)
        )

    def load_variant_desired_configuration(
        self, experiment_id: str, variant_id: str
    ) -> dict[str, Any] | None:
        experiment_sub_dir = _safe_file_name(experiment_id, kind="experiment_id")[: -len(".json")]
        file_name = _safe_file_name(variant_id, kind="variant_id")
        return self._read_json(f"variant_desired_configuration/{experiment_sub_dir}", file_name)
