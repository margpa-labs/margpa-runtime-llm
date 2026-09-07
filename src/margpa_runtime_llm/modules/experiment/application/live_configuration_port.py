"""Live Effective Configuration Port (Phase 9-2 R2, WU-01).

The narrow boundary `web/experiment_routes.py` depends on to build and
verify a Production Plan/Run's Frozen `EffectiveConfigurationSnapshot` --
deliberately as narrow as `production_turn_runner.ProductionTurnPort`
(WU-03) for the identical reason: this module never imports
`bootstrap.judge_live_integration`/`bootstrap.guardrail_governance`/
`modules.runtime_model_control`/etc. directly, so nothing outside
`bootstrap/experiment_live_configuration.py` (the one real implementation)
ever needs a live Model or live Governance Composition just to exercise
the Frozen-vs-Live comparison logic in a test."""

from __future__ import annotations

from typing import Protocol

from ..domain.config_snapshot import EffectiveConfigurationSnapshot
from ..domain.provider_identity import ProviderIdentityEnvelope


class LiveConfigurationPort(Protocol):
    """R2-WU-01 (IR-P9-2-R1-01 fix): `snapshot()` always reads the LIVE
    Runtime's current Judge/Guard/Main-Governance/Repair/Recording/Main
    state fresh, at the instant it is called -- never a cached or
    Plan-creation-time value. Called at least twice per Production Run:
    once for the FINAL, authoritative Frozen-vs-Live comparison (R4-WU-02:
    now taken strictly INSIDE the Configuration Lease's own protected
    window, immediately before the real Actor Call -- see `web/
    experiment_routes.py`'s `_invoke_production()`), and once again
    immediately after the Actor Call completes (the bounded, detective
    re-check Handoff R2 SS4.2's Option 3 requires).

    R4-WU-01 (Handoff R4 SS4.1.5): `provider_identity()` is a second,
    independent read -- Configured/Active/Artifact-Digest for Main/Judge/
    Guard only, kept as a genuinely separate Envelope from `snapshot()`'s
    own single-`selector_id`-per-slot shape rather than merged into it."""

    def snapshot(self) -> EffectiveConfigurationSnapshot: ...

    def provider_identity(self) -> ProviderIdentityEnvelope: ...
