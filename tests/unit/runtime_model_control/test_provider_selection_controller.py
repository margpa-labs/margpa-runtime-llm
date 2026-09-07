from pathlib import Path

import pytest

from margpa_runtime_llm.bootstrap.model_registry_loader import load_model_definition
from margpa_runtime_llm.modules.runtime_model_control.application import (
    BUILT_IN_GUARD,
    DEEPSEEK_MAIN,
    GEMMA_E2B_JUDGE,
    QWEN3_GUARD,
    QWEN_MAIN,
    SELENE_JUDGE,
    ProviderSelectionController,
)
from margpa_runtime_llm.modules.runtime_model_control.domain.identifiers import ModelRole
from margpa_runtime_llm.modules.runtime_model_control.domain.provider_selection import (
    ProviderRuntimeState,
    ProviderSelectionError,
    ProviderSelectionErrorCode,
)


def test_defaults_are_independent_and_dedicated_roles_are_not_loaded() -> None:
    """P9-1 Package 2 (User-mandated Fresh Runtime default change): the
    Fresh Runtime JUDGE default is now the lightweight independent Judge
    candidate (Gemma 4 E2B), not Selene -- Selene remains fully
    registered/dispatchable/explicitly-selectable (`test_gemma_e2b_judge_
    is_selectable_and_family_independent_from_main` below covers Gemma's
    own selectability; other Tests across this module/`test_role_
    lifecycle_manager.py` explicitly select Selene where they exercise it).
    `active_provider is None`/`state is CONFIGURED` are unchanged by this
    default flip -- a Fresh Runtime never implicitly Loads any Judge
    Provider regardless of which one is configured; only an explicit Mode
    ON + Role Activation ever Loads anything."""
    snapshot = ProviderSelectionController().snapshot()
    by_role = {item.role: item for item in snapshot.selections}
    assert by_role[ModelRole.MAIN].configured_provider == QWEN_MAIN
    assert by_role[ModelRole.MAIN].active_provider == QWEN_MAIN
    assert by_role[ModelRole.GUARD].configured_provider == QWEN3_GUARD
    assert by_role[ModelRole.GUARD].active_provider is None
    assert by_role[ModelRole.JUDGE].configured_provider == GEMMA_E2B_JUDGE
    assert by_role[ModelRole.JUDGE].active_provider is None
    assert by_role[ModelRole.GUARD].state is ProviderRuntimeState.CONFIGURED
    assert by_role[ModelRole.JUDGE].state is ProviderRuntimeState.CONFIGURED


def test_role_mismatch_is_rejected() -> None:
    controller = ProviderSelectionController()
    before = controller.snapshot()
    with pytest.raises(ProviderSelectionError) as raised:
        controller.select(
            role=ModelRole.JUDGE,
            provider_id=BUILT_IN_GUARD,
            expected_revision=before.revision,
            expected_digest=before.digest_sha512,
        )
    assert raised.value.code is ProviderSelectionErrorCode.ROLE_MISMATCH


def test_stale_cas_does_not_overwrite_newer_selection() -> None:
    controller = ProviderSelectionController()
    initial = controller.snapshot()
    changed = controller.select(
        role=ModelRole.MAIN,
        provider_id=DEEPSEEK_MAIN,
        expected_revision=initial.revision,
        expected_digest=initial.digest_sha512,
    )
    with pytest.raises(ProviderSelectionError) as raised:
        controller.select(
            role=ModelRole.MAIN,
            provider_id=QWEN_MAIN,
            expected_revision=initial.revision,
            expected_digest=initial.digest_sha512,
        )
    assert raised.value.code is ProviderSelectionErrorCode.REVISION_CONFLICT
    assert raised.value.current_snapshot == changed


def test_stale_snapshot_still_allows_reselecting_an_unrelated_untouched_role() -> None:
    """P9-1 Judge Dispatch Fix Round 6 (Finding 4): a single logical "switch
    Main" operation bumps the shared global revision counter twice
    (`select()`, then the Lifecycle's own `replace_runtime_state()` once the
    real Load commits) -- so a caller that captured a Snapshot before that
    switch, then tries to reselect JUDGE using that now-stale
    revision/digest, must still succeed as long as JUDGE's own selection was
    never itself touched by the Main switch. Root-caused via real-hardware
    reproduction of the exact Main=DeepSeek + Judge=DeepSeek(self) Mode-apply
    failure (`revision_conflict` leaving `configured_provider` stuck --
    `main_model_mismatch_requires_main_switch` misleadingly suggesting
    Judge was never (re)selected at all)."""
    controller = ProviderSelectionController()
    initial = controller.snapshot()
    controller.select(
        role=ModelRole.MAIN,
        provider_id=DEEPSEEK_MAIN,
        expected_revision=initial.revision,
        expected_digest=initial.digest_sha512,
    )
    activated = controller.replace_runtime_state(
        role=ModelRole.MAIN,
        configured_provider=DEEPSEEK_MAIN,
        active_provider=DEEPSEEK_MAIN,
        state=ProviderRuntimeState.ACTIVE,
    )
    assert activated.revision == initial.revision + 2

    # The caller only ever observed `initial` -- stale by 2 revisions, both
    # caused solely by MAIN's own selection, never JUDGE's.
    result = controller.select(
        role=ModelRole.JUDGE,
        provider_id=DEEPSEEK_MAIN,
        expected_revision=initial.revision,
        expected_digest=initial.digest_sha512,
    )
    judge = next(item for item in result.selections if item.role is ModelRole.JUDGE)
    assert judge.configured_provider == DEEPSEEK_MAIN


def test_cas_rejects_a_forged_digest_at_an_otherwise_matching_revision() -> None:
    """P9-1 Judge Dispatch Fix Round 6, Self-review correction (Finding 2
    from an independent static-correctness audit): `_cas_satisfied()`'s
    Round 6 Fallback condition (`self._role_revision[role] <=
    expected_revision`) is an invariant that is *always* true whenever
    `expected_revision == current.revision` (every mutation site keeps
    `_role_revision[role] <= self._revision`) -- so an earlier version of
    this check silently accepted any `expected_digest`, even an obviously
    forged one, whenever the caller's `expected_revision` happened to equal
    the current one. This Test pins the corrected behavior: an
    exact-revision match with a mismatched digest must still be rejected as
    a genuine `REVISION_CONFLICT`, never silently satisfied by the
    Role-scoped Fallback (which now only ever applies to a strictly older
    `expected_revision`)."""
    controller = ProviderSelectionController()
    initial = controller.snapshot()
    with pytest.raises(ProviderSelectionError) as raised:
        controller.select(
            role=ModelRole.JUDGE,
            provider_id=DEEPSEEK_MAIN,
            expected_revision=initial.revision,
            expected_digest="0" * 128,
        )
    assert raised.value.code is ProviderSelectionErrorCode.REVISION_CONFLICT


def test_cas_rejects_an_expected_revision_beyond_the_current_one() -> None:
    """Defensive bound in `_cas_satisfied()`'s Round 6 fallback path: a
    caller cannot claim to have observed a revision that does not exist
    yet. Without this check, an inflated/bogus `expected_revision` would
    trivially satisfy `self._role_revision[role] <= expected_revision` for
    any Role."""
    controller = ProviderSelectionController()
    initial = controller.snapshot()
    with pytest.raises(ProviderSelectionError) as raised:
        controller.select(
            role=ModelRole.JUDGE,
            provider_id=DEEPSEEK_MAIN,
            expected_revision=initial.revision + 1000,
            expected_digest=initial.digest_sha512,
        )
    assert raised.value.code is ProviderSelectionErrorCode.REVISION_CONFLICT


def test_select_active_also_allows_a_stale_revision_caused_only_by_an_unrelated_role() -> None:
    """P9-1 Judge Dispatch Fix Round 6 (Round 6 Test Coverage audit
    Follow-up): `select_active()` shares the exact same `_cas_satisfied()`
    call as `select()` (Finding 4's Role-scoped Fallback), but every prior
    Round 6 Test exercising this Fallback went through `select()` only.
    This directly proves `select_active()` benefits from the identical
    Fallback, independent of `RoleProviderLifecycleManager` (which already
    has its own coverage via `test_transition_succeeds_with_a_stale_
    revision_caused_only_by_an_unrelated_main_switch` in
    `test_role_lifecycle_manager.py`)."""
    controller = ProviderSelectionController()
    initial = controller.snapshot()
    controller.select(
        role=ModelRole.MAIN,
        provider_id=DEEPSEEK_MAIN,
        expected_revision=initial.revision,
        expected_digest=initial.digest_sha512,
    )
    controller.replace_runtime_state(
        role=ModelRole.MAIN,
        configured_provider=DEEPSEEK_MAIN,
        active_provider=DEEPSEEK_MAIN,
        state=ProviderRuntimeState.ACTIVE,
    )

    result = controller.select_active(
        role=ModelRole.GUARD,
        provider_id=BUILT_IN_GUARD,
        expected_revision=initial.revision,
        expected_digest=initial.digest_sha512,
    )
    guard = next(item for item in result.selections if item.role is ModelRole.GUARD)
    assert guard.configured_provider == BUILT_IN_GUARD
    assert guard.active_provider == BUILT_IN_GUARD
    assert guard.state is ProviderRuntimeState.ACTIVE


def test_selection_does_not_implicitly_activate_or_fallback() -> None:
    controller = ProviderSelectionController()
    initial = controller.snapshot()
    changed = controller.select(
        role=ModelRole.JUDGE,
        provider_id=QWEN_MAIN,
        expected_revision=initial.revision,
        expected_digest=initial.digest_sha512,
    )
    judge = next(item for item in changed.selections if item.role is ModelRole.JUDGE)
    assert judge.configured_provider == QWEN_MAIN
    assert judge.active_provider is None
    assert judge.state is ProviderRuntimeState.CONFIGURED
    assert judge.independence.value == "self"


@pytest.mark.parametrize(
    ("file_name", "model_key", "role", "digest"),
    (
        (
            "selene_1_mini_llama_3_1_8b_q5_k_m.toml",
            SELENE_JUDGE,
            "judge",
            "6d5472911fc347d51a73e57077dd34353c3e134a0af67b0dbe4e4df7d980e3246"
            "f0253ee16e5a241a41904d37e73ab3ba11ce5d800de37b9adddb2ada9b6c50d",
        ),
        (
            "qwen3guard_gen_0_6b_q8_0.toml",
            QWEN3_GUARD,
            "guard",
            "0b8d213fd487980ce2667acaaf042d228486d9b467cd90ab6bfbe490527fa1b51"
            "d7a318af593bc920d59f5b22759196c09eaf8cba1974766ab170e6d6f6c19cb",
        ),
        (
            # P9-1 Package 2: the Package 1 lightweight independent Judge
            # candidate (Gemma 4 E2B), now wired into the Provider Selection
            # Catalog -- proves the digest transcribed into `provider_
            # selection_controller.py`'s `_GEMMA_E2B_DIGEST` genuinely
            # matches the real Registry Entry, not just a copy-paste.
            "gemma_4_e2b_it_q4_0.toml",
            GEMMA_E2B_JUDGE,
            "judge",
            "54b1e06eea3bcfd2f94d2a0195366830d25d63dc15dd2484fa7cd35f82cfd4b"
            "8503702ac3a1a3772775284e3d9a5531a54f1a9b8e3eaa16417d84eae360c76ad",
        ),
    ),
)
def test_dedicated_model_definition_identity(
    file_name: str, model_key: str, role: str, digest: str
) -> None:
    definition = load_model_definition(Path("config/models") / file_name)
    assert definition.model_key == model_key
    assert definition.logical_role == role
    assert definition.artifact.sha512 == digest


def test_gemma_e2b_judge_is_selectable_and_family_independent_from_main() -> None:
    """P9-1 Package 2: Gemma 4 E2B is now a selectable JUDGE Provider (WU-04
    registration), and its `model_family` ("gemma4") genuinely differs from
    Main's default `model_family` ("qwen3") -- the Provider Independence
    axis Package 1's selection rationale relied on (family-independent from
    both Main and Guard, for diagnosing "Qwen-specific bug" vs "true common
    Judge substrate bug"), not merely an unchecked claim in the Return doc."""
    controller = ProviderSelectionController()
    initial = controller.snapshot()
    changed = controller.select(
        role=ModelRole.JUDGE,
        provider_id=GEMMA_E2B_JUDGE,
        expected_revision=initial.revision,
        expected_digest=initial.digest_sha512,
    )
    judge = next(item for item in changed.selections if item.role is ModelRole.JUDGE)
    assert judge.configured_provider == GEMMA_E2B_JUDGE
    assert judge.independence.value == "independent_other_model"
    # P9-1 Package 2 (User-mandated Fresh Runtime default change): a
    # freshly constructed Controller now genuinely defaults to Gemma
    # (this Test's own explicit `select()` above is otherwise redundant
    # with the default -- reselecting the same Provider is still a
    # meaningful CAS Path, so this Test stays valid either way). Selene
    # itself is never deprecated -- still fully registered/dispatchable
    # (`test_dedicated_model_definition_identity` above, `SELENE_JUDGE`
    # entry in `default_provider_options()`), only no longer the Fresh
    # default (Package 1 Return §1's "Selene置換・廃止は行っていない" still
    # holds: replaced as *default*, not replaced/discontinued).
    default_judge = next(
        item
        for item in ProviderSelectionController().snapshot().selections
        if item.role is ModelRole.JUDGE
    )
    assert default_judge.configured_provider == GEMMA_E2B_JUDGE
