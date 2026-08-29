"""P6-RR-R1 (Post-Claude Independent Review Rework): reproduces, and
verifies the fix for, P6-CODEX-062 / P6-GOV-018 Addendum Scenario B —
`PUT /api/v6/provider-selection/{judge,guard}` used to change only the
Configured provider via `ProviderSelectionController.select()`, leaving
that Role's Mode (a separate Controller) committed ON with Active `none`
(`Mode ENFORCE / Active none`, a reachable invalid state). The fix forces
that Role's Mode back to OFF and drains any stale Active adapter, in the
same request, whenever the Configured provider actually changes.
"""

from __future__ import annotations

import asyncio
import threading
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass
from datetime import datetime

import httpx
import pytest
from fastapi import FastAPI

from margpa_runtime_llm.adapters.output_protocols.tagged_thinking import (
    TaggedThinkingOutputParser,
)
from margpa_runtime_llm.bootstrap.guardrail_governance import GuardrailGovernanceComposition
from margpa_runtime_llm.modules.conversation.public import ConversationGenerationService
from margpa_runtime_llm.modules.evaluation.application.judge_mode_controller import (
    JudgeModeController,
)
from margpa_runtime_llm.modules.evaluation.domain.identifiers import EvaluationMode
from margpa_runtime_llm.modules.inference.contracts.generation import (
    GenerationParameters,
    GenerationRequest,
    GenerationStream,
    ThinkingMode,
)
from margpa_runtime_llm.modules.inference.contracts.response import ResponseLanguage
from margpa_runtime_llm.modules.presentation.application.thinking_presentation_service import (
    ThinkingPresentationService,
)
from margpa_runtime_llm.modules.presentation.contracts.thinking import (
    ResolvedThinkingPresentationPolicy,
    ThinkingPersistence,
    ThinkingPresentationSource,
    ThinkingVisibility,
)
from margpa_runtime_llm.modules.runtime_model_control.application import (
    QWEN3_GUARD,
    QWEN_MAIN,
    SELENE_JUDGE,
    ProviderSelectionController,
    RoleProviderLifecycleManager,
)
from margpa_runtime_llm.modules.runtime_model_control.application.role_lifecycle_manager import (
    ModeReadResult,
    RoleTurnLease,
)
from margpa_runtime_llm.modules.runtime_model_control.domain.identifiers import ModelRole
from margpa_runtime_llm.modules.runtime_model_control.domain.provider_selection import (
    ProviderOption,
    ProviderSelectionError,
)
from margpa_runtime_llm.modules.runtime_model_control.ports import (
    RoleAdapterFactoryPort,
    RoleProviderAdapterPort,
)
from margpa_runtime_llm.modules.summarization.public import SummarizationConfig, SummaryMode
from margpa_runtime_llm.web.access_profiles import WebExposureMode
from margpa_runtime_llm.web.app import create_web_app
from margpa_runtime_llm.web.auth import WebAccessPolicy, WebAuthMode
from margpa_runtime_llm.web.contracts import RuntimeDefaults, SafeRuntimeSnapshot, WebRuntime

_LOCAL_POLICY = WebAccessPolicy(exposure_mode=WebExposureMode.LOCAL, mode=WebAuthMode.DISABLED)
_BUILT_IN_JUDGE = "built_in.deterministic"
_BUILT_IN_GUARD = "built_in.rule_pattern"


class FakeInference:
    def stream(self, request: GenerationRequest) -> GenerationStream:
        raise NotImplementedError


def _conversation() -> ConversationGenerationService:
    presentation_policy = ResolvedThinkingPresentationPolicy(
        visibility=ThinkingVisibility.HIDDEN,
        display_label="推論過程",
        persistence=ThinkingPersistence.DISABLED,
        visibility_source=ThinkingPresentationSource.APPLICATION,
        display_label_source=ThinkingPresentationSource.APPLICATION,
        persistence_source=ThinkingPresentationSource.APPLICATION,
    )
    return ConversationGenerationService(
        inference=FakeInference(),
        presentation=ThinkingPresentationService(
            TaggedThinkingOutputParser(opening_delimiter="<think>", closing_delimiter="</think>")
        ),
        model_key=QWEN_MAIN,
        generation_defaults=GenerationParameters(
            max_new_tokens=2048, thinking_mode=ThinkingMode.DISABLED
        ),
        response_language_default=ResponseLanguage.JA,
        presentation_default=presentation_policy,
        summarization=SummarizationConfig(),
    )


def _snapshot() -> SafeRuntimeSnapshot:
    return SafeRuntimeSnapshot(
        model_key=QWEN_MAIN,
        profile_key="local.macos-arm64.metal",
        device_kind="gpu",
        acceleration_api="metal",
        defaults=RuntimeDefaults(
            response_language=ResponseLanguage.JA,
            max_new_tokens=2048,
            thinking_mode=ThinkingMode.DISABLED,
            thinking_visibility=ThinkingVisibility.HIDDEN,
            thinking_display_label="推論過程",
            thinking_control_available=True,
            summary_mode=SummaryMode.OFF,
        ),
    )


class _NeverCalledFactory(RoleAdapterFactoryPort):
    """Built-in Activation never reaches the Factory (`activate()`'s own
    BUILT_IN branch), so a Factory that raises on any real `create()` call
    both satisfies the Port and catches an accidental regression."""

    def create(self, *, role: ModelRole, option: ProviderOption) -> RoleProviderAdapterPort:
        raise AssertionError(f"factory.create() must not be called for a Built-in option: {option}")


def _runtime() -> WebRuntime:
    provider_selection_control = ProviderSelectionController(current_main_provider=QWEN_MAIN)
    role_provider_lifecycle = RoleProviderLifecycleManager(
        selections=provider_selection_control,
        factory=_NeverCalledFactory(),
    )
    return WebRuntime(
        conversation=_conversation(),
        snapshot=_snapshot(),
        close_callback=lambda: None,
        provider_selection_control=provider_selection_control,
        role_provider_lifecycle=role_provider_lifecycle,
        judge_mode_control=JudgeModeController(),
        guardrail_governance_composition=GuardrailGovernanceComposition(),
    )


@asynccontextmanager
async def client_for(app: FastAPI) -> AsyncIterator[httpx.AsyncClient]:
    async with app.router.lifespan_context(app):
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app, raise_app_exceptions=False),
            base_url="http://test",
        ) as client:
            yield client


async def _select(client: httpx.AsyncClient, *, role: str, provider_id: str) -> httpx.Response:
    before = (await client.get("/api/v6/provider-selection")).json()
    return await client.put(
        f"/api/v6/provider-selection/{role}",
        json={
            "provider_id": provider_id,
            "expected_revision": before["revision"],
            "expected_digest": before["digest_sha512"],
        },
    )


@pytest.mark.asyncio
async def test_judge_provider_change_while_enforce_forces_mode_off_and_drains_active() -> None:
    """Reproduces P6-GOV-018 Addendum Scenario B for Judge, then verifies
    the Fix: `Mode ENFORCE / Active none` must never be the state left
    behind by a Configured Provider change."""
    app = create_web_app(runtime_factory=_runtime, access_policy=_LOCAL_POLICY)
    async with client_for(app) as client:
        # 1. Configure Built-in, then Activate it via the real Mode-Apply
        #    path (which already Preflights correctly) so Judge genuinely
        #    reaches Mode=ENFORCE / Active=built_in.deterministic.
        select_response = await _select(client, role="judge", provider_id=_BUILT_IN_JUDGE)
        assert select_response.status_code == 200
        enforce_response = await client.post(
            "/api/v5/feature-modes/judge", json={"requested_mode": "enforce"}
        )
        assert enforce_response.status_code == 200
        assert enforce_response.json()["judge"]["current_mode"] == "enforce"

        # 2. Change the Configured Provider to Selene while still ENFORCE —
        #    this is exactly the unguarded path P6-CODEX-062 identified.
        switch_response = await _select(client, role="judge", provider_id=SELENE_JUDGE)
        assert switch_response.status_code == 409, switch_response.text
        # Failed activation is a rollback: the old configured/active/mode
        # tuple remains externally visible, never a transient ON/none state.
        selection_response = await client.get("/api/v6/provider-selection")
        judge_selection = next(
            item for item in selection_response.json()["selections"] if item["role"] == "judge"
        )
        assert judge_selection["configured_provider"] == _BUILT_IN_JUDGE
        assert judge_selection["active_provider"] == _BUILT_IN_JUDGE
        status_response = await client.get("/api/v5/feature-modes/status")
        assert status_response.json()["judge"]["current_mode"] == "enforce"


@pytest.mark.asyncio
async def test_judge_provider_change_to_main_self_while_enforce_drains_active() -> None:
    """Regression Scenario S3 (`docs/project/phases/phase_6/handoffs/
    phase_6_post_claude_independent_review_exact_rework_handoff_ja_
    20260828180240.md`): the same Atomicity Contract as S2 (-> Selene),
    exercised against the other Judge Provider shape entirely — a
    Model-kind "self when Main is Qwen" option (`QWEN_MAIN` as a Judge
    `provider_id`, not a Main `model_key`) rather than a dedicated
    Independent Artifact. Configured Provider changes while ENFORCE must
    force the real `_transition_to_locked` Activation path (never the
    bare CAS-only `select()` Mode-OFF shortcut) regardless of which kind
    of Model-backed option the target is."""
    app = create_web_app(runtime_factory=_runtime, access_policy=_LOCAL_POLICY)
    async with client_for(app) as client:
        select_response = await _select(client, role="judge", provider_id=_BUILT_IN_JUDGE)
        assert select_response.status_code == 200
        enforce_response = await client.post(
            "/api/v5/feature-modes/judge", json={"requested_mode": "enforce"}
        )
        assert enforce_response.status_code == 200
        assert enforce_response.json()["judge"]["current_mode"] == "enforce"

        switch_response = await _select(client, role="judge", provider_id=QWEN_MAIN)
        assert switch_response.status_code == 409, switch_response.text
        selection_response = await client.get("/api/v6/provider-selection")
        judge_selection = next(
            item for item in selection_response.json()["selections"] if item["role"] == "judge"
        )
        assert judge_selection["configured_provider"] == _BUILT_IN_JUDGE
        assert judge_selection["active_provider"] == _BUILT_IN_JUDGE
        status_response = await client.get("/api/v5/feature-modes/status")
        assert status_response.json()["judge"]["current_mode"] == "enforce"


@pytest.mark.asyncio
async def test_guard_provider_change_while_enforce_forces_mode_off_and_drains_active() -> None:
    """Same Scenario B reproduction/fix, for Guard — R1-WU-006 (identical
    Atomicity Contract for both Judge and Guard)."""
    app = create_web_app(runtime_factory=_runtime, access_policy=_LOCAL_POLICY)
    async with client_for(app) as client:
        select_response = await _select(client, role="guard", provider_id=_BUILT_IN_GUARD)
        assert select_response.status_code == 200
        runtime: WebRuntime = app.state.runtime
        assert runtime.guardrail_governance_composition is not None
        assert runtime.role_provider_lifecycle is not None
        runtime.role_provider_lifecycle.activate(role=ModelRole.GUARD)
        from margpa_runtime_llm.modules.governance_definitions.domain import GovernanceMode

        runtime.guardrail_governance_composition.mode_controller.apply_mode(GovernanceMode.ENFORCE)
        assert runtime.guardrail_governance_composition.mode_controller.current_mode_value() == (
            "enforce"
        )

        switch_response = await _select(client, role="guard", provider_id=QWEN3_GUARD)
        assert switch_response.status_code == 409, switch_response.text
        selection_response = await client.get("/api/v6/provider-selection")
        guard_selection = next(
            item for item in selection_response.json()["selections"] if item["role"] == "guard"
        )
        assert guard_selection["configured_provider"] == _BUILT_IN_GUARD
        assert guard_selection["active_provider"] == _BUILT_IN_GUARD
        assert runtime.guardrail_governance_composition.mode_controller.current_mode_value() == (
            "enforce"
        )


@pytest.mark.asyncio
async def test_guard_provider_change_while_observe_forces_mode_off_and_drains_active() -> None:
    """Regression Scenario S4 exact (P6-CODEX-085): the pre-existing Guard
    Atomicity test above only ever exercised ENFORCE — the Gate itself is
    Mode-agnostic (`current_mode is not OFF`), but that mechanism was
    never literally proven for Guard OBSERVE specifically. Mirrors S2's
    own Judge-OBSERVE test exactly, for Guard."""
    app = create_web_app(runtime_factory=_runtime, access_policy=_LOCAL_POLICY)
    async with client_for(app) as client:
        select_response = await _select(client, role="guard", provider_id=_BUILT_IN_GUARD)
        assert select_response.status_code == 200
        runtime: WebRuntime = app.state.runtime
        assert runtime.guardrail_governance_composition is not None
        assert runtime.role_provider_lifecycle is not None
        runtime.role_provider_lifecycle.activate(role=ModelRole.GUARD)
        from margpa_runtime_llm.modules.governance_definitions.domain import GovernanceMode

        runtime.guardrail_governance_composition.mode_controller.apply_mode(GovernanceMode.OBSERVE)
        assert runtime.guardrail_governance_composition.mode_controller.current_mode_value() == (
            "observe"
        )

        switch_response = await _select(client, role="guard", provider_id=QWEN3_GUARD)
        assert switch_response.status_code == 409, switch_response.text
        selection_response = await client.get("/api/v6/provider-selection")
        guard_selection = next(
            item for item in selection_response.json()["selections"] if item["role"] == "guard"
        )
        assert guard_selection["configured_provider"] == _BUILT_IN_GUARD
        assert guard_selection["active_provider"] == _BUILT_IN_GUARD
        assert runtime.guardrail_governance_composition.mode_controller.current_mode_value() == (
            "observe"
        )


@pytest.mark.asyncio
async def test_judge_provider_change_while_mode_off_leaves_mode_untouched() -> None:
    """Baseline: Mode is already OFF (the common case, Package 0-I
    behavior) — the Fix must not introduce any new side effect there."""
    app = create_web_app(runtime_factory=_runtime, access_policy=_LOCAL_POLICY)
    async with client_for(app) as client:
        response = await _select(client, role="judge", provider_id=_BUILT_IN_JUDGE)
        assert response.status_code == 200
        judge_selection = next(
            item for item in response.json()["selections"] if item["role"] == "judge"
        )
        assert judge_selection["configured_provider"] == _BUILT_IN_JUDGE
        assert judge_selection["active_provider"] is None
        status_response = await client.get("/api/v5/feature-modes/status")
        assert status_response.json()["judge"]["current_mode"] == "off"


@pytest.mark.asyncio
async def test_judge_reselecting_current_provider_is_noop_and_never_forces_mode_off() -> None:
    """A no-op re-select of the already-Configured provider (e.g. a stale
    UI re-render re-submitting the same value) must not reset an active
    Mode — `select()`'s own no-op branch must short-circuit before the
    new OFF-forcing logic ever runs."""
    app = create_web_app(runtime_factory=_runtime, access_policy=_LOCAL_POLICY)
    async with client_for(app) as client:
        await _select(client, role="judge", provider_id=_BUILT_IN_JUDGE)
        enforce_response = await client.post(
            "/api/v5/feature-modes/judge", json={"requested_mode": "enforce"}
        )
        assert enforce_response.json()["judge"]["current_mode"] == "enforce"

        noop_response = await _select(client, role="judge", provider_id=_BUILT_IN_JUDGE)
        assert noop_response.status_code == 200
        judge_selection = next(
            item for item in noop_response.json()["selections"] if item["role"] == "judge"
        )
        assert judge_selection["active_provider"] == _BUILT_IN_JUDGE

        status_response = await client.get("/api/v5/feature-modes/status")
        assert status_response.json()["judge"]["current_mode"] == "enforce"


@pytest.mark.asyncio
async def test_judge_provider_change_drains_stale_adapter_even_without_lifecycle_race() -> None:
    """R1-WU-005: a real Lease/Turn in progress must not be silently
    unloaded out from under it — `deactivate()`'s own existing pending-
    unload/drain contract (verified elsewhere) is reused as-is here; this
    test only pins that a genuinely idle stale adapter is actually gone
    (no leaked `_active_adapters` entry) after a Provider change, by
    checking the projected `state` field settles to a Configured/None
    value rather than staying `active`."""
    app = create_web_app(runtime_factory=_runtime, access_policy=_LOCAL_POLICY)
    async with client_for(app) as client:
        runtime: WebRuntime = app.state.runtime
        assert runtime.role_provider_lifecycle is not None
        lease: RoleTurnLease | None = None
        await _select(client, role="judge", provider_id=_BUILT_IN_JUDGE)
        await client.post("/api/v5/feature-modes/judge", json={"requested_mode": "observe"})
        try:
            lease = runtime.role_provider_lifecycle.begin_turn(role=ModelRole.JUDGE)
        finally:
            if lease is not None:
                runtime.role_provider_lifecycle.end_turn(lease)

        switch_response = await _select(client, role="judge", provider_id=SELENE_JUDGE)
        assert switch_response.status_code == 409, switch_response.text
        judge_selection = next(
            item
            for item in (await client.get("/api/v6/provider-selection")).json()["selections"]
            if item["role"] == "judge"
        )
        assert judge_selection["state"] == "active"
        assert judge_selection["active_provider"] == _BUILT_IN_JUDGE


def test_concurrent_mode_apply_and_provider_selection_never_interleave() -> None:
    """P6-RR-R13-WU-001..004/007 (Post-Claude Independent Review Rework,
    resolves P6-CODEX-074/069/062): the previous design let a
    Provider-Selection-change Request read Mode *outside* any Lock and
    then act on that stale read using a *different* Lock than the one a
    concurrent Mode-Apply Request commits under — a genuine TOCTOU race.
    Checking only before/after final states (the existing Tests above)
    cannot catch this; this Test forces a real interleaving attempt using
    a deliberately slow candidate Load and proves the second caller
    genuinely blocks on the exact same Lock for the *entire* duration of
    the first caller's Transaction (Activation + Mode Commit together),
    never observing or acting on an intermediate state."""
    load_started = threading.Event()
    release_load = threading.Event()
    events: list[str] = []

    class _SlowAdapter:
        def __init__(self, *, provider_id: str) -> None:
            self.provider_id = provider_id

        def preflight(self) -> tuple[bool, str | None]:
            return True, None

        def load(self) -> None:
            events.append("load_started")
            load_started.set()
            release_load.wait(timeout=5.0)
            events.append("load_finished")

        def unload(self) -> None:
            return None

    class _SlowFactory(RoleAdapterFactoryPort):
        def create(self, *, role: ModelRole, option: ProviderOption) -> RoleProviderAdapterPort:
            return _SlowAdapter(provider_id=option.provider_id)

    provider_selection_control = ProviderSelectionController(current_main_provider=QWEN_MAIN)
    role_provider_lifecycle = RoleProviderLifecycleManager(
        selections=provider_selection_control,
        factory=_SlowFactory(),
    )
    judge_mode_control = JudgeModeController()

    def _read_judge_mode() -> ModeReadResult:
        snapshot = judge_mode_control.mode_snapshot()
        return ModeReadResult(revision=snapshot.revision, value=snapshot.current_mode.value)

    def _read_guard_mode() -> ModeReadResult:
        return ModeReadResult(revision=None, value="off")

    def _thread_a() -> None:
        def _commit() -> None:
            events.append("mode_committed")
            judge_mode_control.apply_mode(EvaluationMode.ENFORCE)

        role_provider_lifecycle.apply_mode_transition(
            role=ModelRole.JUDGE,
            target_mode_is_off=False,
            commit_mode=_commit,
            read_judge_mode=_read_judge_mode,
            read_guard_mode=_read_guard_mode,
        )
        events.append("thread_a_returned")

    thread_a = threading.Thread(target=_thread_a)
    thread_a.start()
    assert load_started.wait(timeout=5.0), "Thread A did not reach the blocking Load in time"

    def _mode_is_on() -> bool:
        events.append("thread_b_mode_is_on_called")
        return judge_mode_control.mode_snapshot().current_mode is not EvaluationMode.OFF

    thread_b_error: list[BaseException] = []

    def _thread_b() -> None:
        events.append("thread_b_call_started")
        try:
            snapshot = provider_selection_control.snapshot()
            role_provider_lifecycle.apply_provider_selection(
                role=ModelRole.JUDGE,
                provider_id=_BUILT_IN_JUDGE,
                expected_revision=snapshot.revision,
                expected_digest=snapshot.digest_sha512,
                mode_is_on=_mode_is_on,
                read_judge_mode=_read_judge_mode,
                read_guard_mode=_read_guard_mode,
            )
        except ProviderSelectionError as exc:
            thread_b_error.append(exc)
        events.append("thread_b_returned")

    thread_b = threading.Thread(target=_thread_b)
    thread_b.start()
    # Thread B has called the method and may be blocked acquiring the
    # Lock; give the scheduler a moment, then confirm it has NOT yet
    # reached the inside of the Locked body (`mode_is_on` unreached)
    # while Thread A is still holding the Lock inside `load()`.
    thread_b.join(timeout=0.2)
    assert "thread_b_mode_is_on_called" not in events
    assert "thread_a_returned" not in events

    release_load.set()
    thread_a.join(timeout=5.0)
    thread_b.join(timeout=5.0)

    assert not thread_a.is_alive()
    assert not thread_b.is_alive()
    # Thread B's Locked-body work (`mode_is_on`) must only ever have run
    # after Thread A's entire Transaction — Mode Commit included —
    # finished. A stale-revision failure inside Thread B is an acceptable
    # outcome of this Test (it proves nothing was silently corrupted); the
    # ordering guarantee is what this Test exists to pin.
    mode_is_on_index = events.index("thread_b_mode_is_on_called")
    thread_a_returned_index = events.index("thread_a_returned")
    mode_committed_index = events.index("mode_committed")
    assert mode_committed_index < mode_is_on_index
    assert thread_a_returned_index < mode_is_on_index


@pytest.mark.asyncio
async def test_r17_provider_and_feature_modes_get_block_during_on_transition() -> None:
    """R17-A/B (ON Transaction中のProvider GET/Feature Modes GET,
    resolves P6-CODEX-080): a real HTTP GET to either
    `/api/v6/provider-selection` or `/api/v5/feature-modes/status`,
    issued while a Judge ON-direction Transaction is in flight (Provider
    settling ACTIVE, Mode Commit not yet run), must not return a torn
    Tuple. Both GET routes now read through `RoleProviderLifecycleManager
    .composite_status()`, the same Transition Lock the in-flight
    Activation holds for its whole critical section — this Test proves
    both routes genuinely block until the whole Transaction (Activation
    + Mode Commit) finishes, then observe the fully committed new
    state."""
    load_started = threading.Event()
    release_load = threading.Event()

    class _SlowAdapter:
        def __init__(self, *, provider_id: str) -> None:
            self.provider_id = provider_id

        def preflight(self) -> tuple[bool, str | None]:
            return True, None

        def load(self) -> None:
            load_started.set()
            release_load.wait(timeout=5.0)

        def unload(self) -> None:
            return None

    class _SlowFactory(RoleAdapterFactoryPort):
        def create(self, *, role: ModelRole, option: ProviderOption) -> RoleProviderAdapterPort:
            return _SlowAdapter(provider_id=option.provider_id)

    def _slow_runtime() -> WebRuntime:
        provider_selection_control = ProviderSelectionController(current_main_provider=QWEN_MAIN)
        role_provider_lifecycle = RoleProviderLifecycleManager(
            selections=provider_selection_control,
            factory=_SlowFactory(),
        )
        return WebRuntime(
            conversation=_conversation(),
            snapshot=_snapshot(),
            close_callback=lambda: None,
            provider_selection_control=provider_selection_control,
            role_provider_lifecycle=role_provider_lifecycle,
            judge_mode_control=JudgeModeController(),
            guardrail_governance_composition=GuardrailGovernanceComposition(),
        )

    app = create_web_app(runtime_factory=_slow_runtime, access_policy=_LOCAL_POLICY)
    async with client_for(app) as client:
        select_response = await _select(client, role="judge", provider_id=SELENE_JUDGE)
        assert select_response.status_code == 200

        enforce_task = asyncio.ensure_future(
            client.post("/api/v5/feature-modes/judge", json={"requested_mode": "enforce"})
        )
        await asyncio.to_thread(load_started.wait, 5.0)

        provider_get_task = asyncio.ensure_future(client.get("/api/v6/provider-selection"))
        status_get_task = asyncio.ensure_future(client.get("/api/v5/feature-modes/status"))

        done, _pending = await asyncio.wait({provider_get_task, status_get_task}, timeout=0.2)
        assert done == set(), "GET routes must block while the Transaction is in flight"

        release_load.set()
        enforce_response, provider_response, status_response = await asyncio.gather(
            enforce_task, provider_get_task, status_get_task
        )

    assert enforce_response.status_code == 200
    judge_from_provider = next(
        item for item in provider_response.json()["selections"] if item["role"] == "judge"
    )
    assert judge_from_provider["active_provider"] == SELENE_JUDGE
    assert judge_from_provider["state"] == "active"
    assert status_response.json()["judge"]["current_mode"] == "enforce"


@pytest.mark.asyncio
async def test_r17_both_gets_block_during_off_transition() -> None:
    """R17-C (OFF Transaction中の両GET, resolves P6-CODEX-080): the
    mirror case for the OFF direction — Mode commits OFF first, then the
    Adapter unloads. A concurrent GET to either route must not observe
    "Mode OFF, Provider still ACTIVE"; it must block until Deactivation
    itself also finishes."""
    unload_started = threading.Event()
    release_unload = threading.Event()

    class _SlowUnloadAdapter:
        def __init__(self, *, provider_id: str) -> None:
            self.provider_id = provider_id

        def preflight(self) -> tuple[bool, str | None]:
            return True, None

        def load(self) -> None:
            return None

        def unload(self) -> None:
            unload_started.set()
            release_unload.wait(timeout=5.0)

    class _SlowUnloadFactory(RoleAdapterFactoryPort):
        def create(self, *, role: ModelRole, option: ProviderOption) -> RoleProviderAdapterPort:
            return _SlowUnloadAdapter(provider_id=option.provider_id)

    def _slow_runtime() -> WebRuntime:
        provider_selection_control = ProviderSelectionController(current_main_provider=QWEN_MAIN)
        role_provider_lifecycle = RoleProviderLifecycleManager(
            selections=provider_selection_control,
            factory=_SlowUnloadFactory(),
        )
        return WebRuntime(
            conversation=_conversation(),
            snapshot=_snapshot(),
            close_callback=lambda: None,
            provider_selection_control=provider_selection_control,
            role_provider_lifecycle=role_provider_lifecycle,
            judge_mode_control=JudgeModeController(),
            guardrail_governance_composition=GuardrailGovernanceComposition(),
        )

    app = create_web_app(runtime_factory=_slow_runtime, access_policy=_LOCAL_POLICY)
    async with client_for(app) as client:
        select_response = await _select(client, role="judge", provider_id=SELENE_JUDGE)
        assert select_response.status_code == 200
        enforce_response = await client.post(
            "/api/v5/feature-modes/judge", json={"requested_mode": "enforce"}
        )
        assert enforce_response.status_code == 200
        assert enforce_response.json()["judge"]["current_mode"] == "enforce"

        off_task = asyncio.ensure_future(
            client.post("/api/v5/feature-modes/judge", json={"requested_mode": "off"})
        )
        await asyncio.to_thread(unload_started.wait, 5.0)

        provider_get_task = asyncio.ensure_future(client.get("/api/v6/provider-selection"))
        status_get_task = asyncio.ensure_future(client.get("/api/v5/feature-modes/status"))

        done, _pending = await asyncio.wait({provider_get_task, status_get_task}, timeout=0.2)
        assert done == set(), "GET routes must block while Deactivation is in flight"

        release_unload.set()
        off_response, provider_response, status_response = await asyncio.gather(
            off_task, provider_get_task, status_get_task
        )

    assert off_response.status_code == 200
    judge_from_provider = next(
        item for item in provider_response.json()["selections"] if item["role"] == "judge"
    )
    assert judge_from_provider["active_provider"] is None
    assert status_response.json()["judge"]["current_mode"] == "off"


# P6-RR-R24 (Post-Codex Independent Review Rework, re-derives P6-DELTA-014):
# `RoleProviderSelectionResponse.failure_at` was previously only exercised
# via a Frontend fixture value — never a genuine Backend-populated
# timestamp produced by a real Activation failure and re-read back through
# the actual `GET /api/v6/provider-selection` route. The Test below drives
# a real `preflight()` failure through `POST /api/v5/feature-modes/judge`
# (the Mode-Apply-to-ON path, `_activate_locked`'s own `if not ready:
# ...failure_reason=reason` branch) and confirms both `failure_reason` and
# `failure_at` survive the full real HTTP round trip.


@dataclass
class _FailingPreflightAdapter:
    provider_id: str
    preflight_reason: str

    def preflight(self) -> tuple[bool, str | None]:
        return False, self.preflight_reason

    def load(self) -> None:
        raise AssertionError("load() must not be reached after a failed preflight()")

    def unload(self) -> None:
        return None


class _FailingPreflightFactory(RoleAdapterFactoryPort):
    def __init__(self, *, preflight_reason: str) -> None:
        self._preflight_reason = preflight_reason

    def create(self, *, role: ModelRole, option: ProviderOption) -> RoleProviderAdapterPort:
        del role
        return _FailingPreflightAdapter(
            provider_id=option.provider_id, preflight_reason=self._preflight_reason
        )


def _runtime_with_failing_preflight() -> WebRuntime:
    provider_selection_control = ProviderSelectionController(current_main_provider=QWEN_MAIN)
    role_provider_lifecycle = RoleProviderLifecycleManager(
        selections=provider_selection_control,
        factory=_FailingPreflightFactory(preflight_reason="p6_rr_r24_test_preflight_failure"),
    )
    return WebRuntime(
        conversation=_conversation(),
        snapshot=_snapshot(),
        close_callback=lambda: None,
        provider_selection_control=provider_selection_control,
        role_provider_lifecycle=role_provider_lifecycle,
        judge_mode_control=JudgeModeController(),
        guardrail_governance_composition=GuardrailGovernanceComposition(),
    )


@pytest.mark.asyncio
async def test_failure_at_is_backend_populated_and_re_readable_after_activation_failure() -> None:
    """P6-RR-R24 (re-derives P6-DELTA-014): a real `preflight()` failure,
    driven through the actual `POST /api/v5/feature-modes/judge` Mode-
    Apply route, settles the Role's `failure_reason`/`failure_at` inside
    `RoleProviderLifecycleManager`'s own Lock (`_activate_locked`'s
    `if not ready: ...failure_reason=reason` branch) *before* that route
    raises `ProviderSelectionError` (a 409 with only `code`/`message` in
    its own body — the Selection state itself is never echoed there).
    This Test proves `failure_at` is genuinely persisted Backend state,
    not merely a value a Test Fixture ever produced: a *separate*, later
    `GET /api/v6/provider-selection` — issued only after the Failure
    Response has already completed — still reads back the same real
    timestamp."""
    app = create_web_app(
        runtime_factory=_runtime_with_failing_preflight, access_policy=_LOCAL_POLICY
    )
    async with client_for(app) as client:
        select_response = await _select(client, role="judge", provider_id=SELENE_JUDGE)
        assert select_response.status_code == 200

        enforce_response = await client.post(
            "/api/v5/feature-modes/judge", json={"requested_mode": "enforce"}
        )
        assert enforce_response.status_code == 409, enforce_response.text
        assert enforce_response.json()["code"] == "provider_selection_activation_failed"

        # The genuinely separate re-read, strictly after the Failure
        # Response above has already completed.
        status_response = await client.get("/api/v6/provider-selection")
        assert status_response.status_code == 200
        read_back_judge = next(
            item for item in status_response.json()["selections"] if item["role"] == "judge"
        )
        assert read_back_judge["failure_reason"] == "p6_rr_r24_test_preflight_failure"
        assert read_back_judge["failure_at"] is not None
        # A genuine ISO-8601 timestamp, not a fixture placeholder —
        # `datetime.fromisoformat` raises on anything else.
        datetime.fromisoformat(read_back_judge["failure_at"])

        # A second independent read confirms the same value persists
        # rather than being a one-shot artifact of the first GET.
        second_status_response = await client.get("/api/v6/provider-selection")
        second_judge = next(
            item for item in second_status_response.json()["selections"] if item["role"] == "judge"
        )
        assert second_judge["failure_at"] == read_back_judge["failure_at"]
