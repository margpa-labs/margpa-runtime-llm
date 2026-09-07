"""Ports for the Experiment Core (Phase 9-2, WU-A A3/A4)."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from .domain.identity import ExperimentPlan
from .domain.run import VariantRun


@runtime_checkable
class ExperimentStorePort(Protocol):
    """WU-A A3: Restart-readable Persistence for Plan, Run, Raw Evidence,
    and Comparison. Every method is synchronous and side-effect-scoped to
    exactly the identifier it is given -- no method here ever mutates or
    reads Live Runtime state (that is a WU-C Actor Adapter concern, not
    this Port's)."""

    def save_plan(self, plan: ExperimentPlan) -> None: ...

    def load_plan(self, experiment_id: str) -> ExperimentPlan | None: ...

    def save_run(self, run: VariantRun) -> None: ...

    def load_run(self, run_id: str) -> VariantRun | None: ...

    def list_runs(self, experiment_id: str) -> tuple[VariantRun, ...]: ...

    def list_all_runs(self) -> tuple[VariantRun, ...]:
        """R2-WU-04 (IR-P9-2-R1-06 fix): every persisted Run across every
        `experiment_id`, independent of any single Experiment -- the one
        Read `ExperimentService.reconcile_orphaned_running_runs()` needs
        at process start to find a Run a PREVIOUS process left `planned`/
        `running` (this fresh process's own in-memory generation counter
        and Worker have no record of it, so it can never naturally reach
        a terminal state on its own)."""
        ...

    def save_raw_evidence(self, run_id: str, evidence: dict[str, object]) -> None: ...

    def load_raw_evidence(self, run_id: str) -> dict[str, object] | None: ...

    def save_comparison(self, experiment_id: str, comparison: dict[str, object]) -> None: ...

    def load_comparison(self, experiment_id: str) -> dict[str, object] | None: ...

    def save_run_configuration_snapshot(
        self, run_id: str, snapshot: dict[str, object]
    ) -> None:
        """R3-WU-01 (IR-P9-2-R2-03 MAJOR fix): the FULL `EffectiveConfiguration
        Snapshot` (as `model_dump(mode="json")`) a Production Run's own
        Call-0 check captured LIVE, fresh, at THIS Run's own start -- never
        only its digest. Genuinely Restart-readable: this is what lets a
        later reader recover what a Run's own Frozen Configuration actually
        WAS, not merely verify a digest against a value it can no longer
        see."""
        ...

    def load_run_configuration_snapshot(self, run_id: str) -> dict[str, object] | None: ...

    def save_variant_desired_configuration(
        self, experiment_id: str, variant_id: str, snapshot: dict[str, object]
    ) -> None:
        """R3-WU-01 (IR-P9-2-R2-01/03 fix): the FULL per-Variant "Desired
        Configuration" `EffectiveConfigurationSnapshot` computed once at
        Plan-creation time (`config_snapshot.overlay_variant_onto_
        snapshot()`) -- distinct from, and never confused with, a Run's own
        genuine Frozen Configuration above (`save_run_configuration_
        snapshot`). Exists purely so the UI can show what a Variant's own
        Production execution SHOULD look like before any Run of it starts,
        Restart-readable exactly like every other Experiment Core artifact."""
        ...

    def load_variant_desired_configuration(
        self, experiment_id: str, variant_id: str
    ) -> dict[str, object] | None: ...
