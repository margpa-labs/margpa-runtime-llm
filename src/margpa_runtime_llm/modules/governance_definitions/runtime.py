"""GovernanceDefinitionsRuntime: the one process-local object that owns
Mode state, Provider access, and the Plan Cache together (P3-F-WU-002).

`off` never calls the Provider at all (P3-MOD-003/P3-PER-002) — `status()`
returns provider/definition/plan information only after at least one
successful transition to `observe` populated it. Transitioning back to
`off` stops new Governance-specific work but does not retroactively
invalidate already-produced Evidence (P3-MOD-009).

Source content for Normalization comes exclusively from the Provider's
own `PackageSourceResult.verified_source_json` (P3-CODEX-007) — this
Runtime never re-reads a Source from disk itself. That would be a second,
unverified read racing against whatever the Provider just checked the
Size/Digest of; the Provider's own verified read is the only Source of
Truth here.
"""

from __future__ import annotations

import threading

from pydantic import Field

from margpa_runtime_llm.modules.inference.contracts.base import ImmutableContract

from .adapter_registry import TrustedAdapterRegistry
from .compiler_cache import CompiledPlanCache
from .domain import (
    CompilerInput,
    DefinitionState,
    DigestedNormalizedGovernanceDefinition,
    GovernanceMode,
    GovernanceModeSnapshot,
    PackageState,
    build_governance_mode_snapshot,
    compile_plan,
    digest_ir,
    manifest_digest_sha512,
    plan_matches_requested_digests,
    request_mode_transition,
)
from .ports import DefinitionProviderPort, PackageLoadRequest

_CAP_DIGEST_PLACEHOLDER = "0" * 128  # Phase 3: no Runtime Capability axis is bound yet.
_AUTH_DIGEST_PLACEHOLDER = "0" * 128  # Phase 3: no Authority/Policy axis is bound yet.


class GovernanceObserveSummary(ImmutableContract):
    """Safe, aggregate-only projection — never raw Definition content, a
    Source path, or a Python exception (P3-UI-005/P3-SEC-*)."""

    provider_state: str
    package_found: bool
    package_state: str | None = None
    definition_count: int = Field(default=0, ge=0)
    valid_definition_count: int = Field(default=0, ge=0)
    invalid_definition_count: int = Field(default=0, ge=0)
    unsupported_definition_count: int = Field(default=0, ge=0)
    compiled_plan_id: str | None = None
    compiled_plan_digest_sha512: str | None = None
    package_id: str | None = None
    manifest_digest_sha512: str | None = None


class GovernanceStatusSnapshot(ImmutableContract):
    mode: GovernanceModeSnapshot
    observe_summary: GovernanceObserveSummary | None = None


class GovernanceObservePipelineError(Exception):
    """Raised when building the OBSERVE candidate Summary/Plan fails
    (Provider/Adapter/Reader/Compiler fault). Never exposes the raw
    underlying exception — `apply_mode()` catches it and re-raises this
    Typed Safe Failure instead, leaving Mode/Revision/Summary at their
    prior, fully consistent values (P3-CODEX-003)."""

    def __init__(self, *, safe_message: str) -> None:
        super().__init__(safe_message)
        self.safe_message = safe_message


class GovernanceDefinitionsRuntime:
    def __init__(
        self,
        *,
        provider: DefinitionProviderPort,
        registry: TrustedAdapterRegistry,
        initial_mode: GovernanceMode = GovernanceMode.OFF,
    ) -> None:
        self._provider = provider
        self._registry = registry
        self._lock = threading.Lock()
        self._mode = initial_mode
        self._revision = 0
        self._plan_cache = CompiledPlanCache()
        self._observe_summary: GovernanceObserveSummary | None = None

    def mode_snapshot(self) -> GovernanceModeSnapshot:
        with self._lock:
            return build_governance_mode_snapshot(revision=self._revision, current_mode=self._mode)

    def status(self) -> GovernanceStatusSnapshot:
        with self._lock:
            return GovernanceStatusSnapshot(
                mode=build_governance_mode_snapshot(
                    revision=self._revision, current_mode=self._mode
                ),
                observe_summary=self._observe_summary,
            )

    def apply_mode(self, requested_mode: GovernanceMode) -> GovernanceModeSnapshot:
        with self._lock:
            new_mode = request_mode_transition(
                current_mode=self._mode, requested_mode=requested_mode
            )
            if new_mode is self._mode:
                return build_governance_mode_snapshot(
                    revision=self._revision, current_mode=self._mode
                )

            # Build the candidate Summary/Plan *before* touching any
            # committed state. A Provider/Adapter/Reader/Compiler fault
            # here must leave Mode/Revision/Summary exactly as they were
            # (P3-CODEX-003) — never a half-applied Mode with a stale or
            # missing Summary.
            candidate_summary: GovernanceObserveSummary | None = None
            if new_mode is GovernanceMode.OBSERVE:
                try:
                    candidate_summary = self._run_observe_pipeline()
                except GovernanceObservePipelineError:
                    raise
                except Exception as error:
                    raise GovernanceObservePipelineError(
                        safe_message="the governance observe pipeline failed"
                    ) from error

            self._mode = new_mode
            self._revision += 1
            self._observe_summary = candidate_summary
            if new_mode is GovernanceMode.OFF:
                # architecture §8.2 "observe -> off": clear the
                # process-local Plan Cache — never carry a Plan computed
                # under a prior Observe session silently into the next
                # one (P3-CODEX-006). Already-produced Evidence is
                # untouched (P3-MOD-009).
                self._plan_cache.clear()
            return build_governance_mode_snapshot(revision=self._revision, current_mode=self._mode)

    def _run_observe_pipeline(self) -> GovernanceObserveSummary:
        descriptor = self._provider.describe()
        result = self._provider.load_package(PackageLoadRequest())
        if not result.found or result.manifest is None:
            return GovernanceObserveSummary(
                provider_state=descriptor.state.value, package_found=False
            )

        manifest = result.manifest
        package_state = result.package_state or PackageState.INVALID
        definition_states = {entry.definition_id: entry.state for entry in result.definition_states}

        digested_irs: list[DigestedNormalizedGovernanceDefinition] = []
        sources_by_id = {entry.source_id: entry for entry in manifest.source_entries}
        for definition in manifest.definition_entries:
            if definition_states.get(definition.definition_id) is not DefinitionState.VALIDATED:
                continue
            source_entry = sources_by_id[definition.source_id]
            adapter = self._registry.resolve(
                schema_id=source_entry.schema_id,
                adapter_id=source_entry.trusted_adapter_id,
                source_media_type=source_entry.media_type,
            )
            if adapter is None:
                continue
            source_json = result.verified_source_json.get(source_entry.source_id)
            if source_json is None:
                continue
            ir = adapter.normalize(
                source_json=source_json, source_entry=source_entry, definition_entry=definition
            )
            digested_irs.append(digest_ir(ir))

        compiler_input = CompilerInput(
            normalized_ir_refs=tuple(d.ir.ir_id for d in digested_irs),
            # Content Integrity Identity, not just Name Identity: the same
            # ir_id with different Source/Section content must miss Cache
            # (P3-CODEX-006) — see CompilerInput.normalized_ir_digests.
            normalized_ir_digests=tuple(d.ir_digest_sha512 for d in digested_irs),
            runtime_capability_snapshot_digest=_CAP_DIGEST_PLACEHOLDER,
            authority_snapshot_digest=_AUTH_DIGEST_PLACEHOLDER,
        )
        cached = self._plan_cache.get(compiler_input)
        if cached is not None and not plan_matches_requested_digests(cached, compiler_input):
            # Defense-in-depth: the Cache Key already encodes the digests,
            # so this should be unreachable in practice — but a Cache Hit
            # is never trusted on key equality alone (P3-CODEX-006).
            cached = None
        plan = cached or compile_plan(
            compiler_input=compiler_input, definitions=tuple(digested_irs)
        )
        if cached is None:
            self._plan_cache.put(compiler_input, plan)

        counts = {state: 0 for state in DefinitionState}
        for state in definition_states.values():
            counts[state] += 1

        return GovernanceObserveSummary(
            provider_state=descriptor.state.value,
            package_found=True,
            package_state=package_state.value,
            definition_count=len(manifest.definition_entries),
            valid_definition_count=counts[DefinitionState.VALIDATED],
            invalid_definition_count=counts[DefinitionState.INVALID],
            unsupported_definition_count=counts[DefinitionState.UNSUPPORTED],
            compiled_plan_id=plan.compiled_plan_id,
            compiled_plan_digest_sha512=None,
            package_id=manifest.package_id,
            manifest_digest_sha512=manifest_digest_sha512(manifest),
        )
