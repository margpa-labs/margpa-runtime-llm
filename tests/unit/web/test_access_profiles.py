"""Explicit Web Access Profile, RAG capability, and disabled-control tests."""

from __future__ import annotations

from pathlib import Path

import pytest

from margpa_runtime_llm.modules.inference.domain.errors import InferenceError
from margpa_runtime_llm.web.access_profiles import (
    DocumentationRagCapability,
    DocumentationRagEffectiveState,
    DocumentationRagFeatureMode,
    DocumentationRagFeatureProfile,
    OptionalControlMode,
    WebExposureMode,
    build_disabled_control_policy,
    load_web_access_profile,
    resolve_documentation_rag_state,
)

PROJECT_ROOT = Path(__file__).resolve().parents[3]
BASIC_PROFILE = PROJECT_ROOT / "config/web_profiles/basic_preview.toml"
PUBLIC_PROFILE = PROJECT_ROOT / "config/web_profiles/public_demo.toml"


def test_tracked_profiles_keep_access_rag_and_controls_explicit() -> None:
    basic = load_web_access_profile(BASIC_PROFILE)
    public = load_web_access_profile(PUBLIC_PROFILE)

    assert basic.access.mode is WebExposureMode.BASIC_PREVIEW
    assert basic.features.documentation_rag is DocumentationRagCapability.ELIGIBLE

    assert public.access.mode is WebExposureMode.PUBLIC_DEMO
    assert public.features.documentation_rag is DocumentationRagCapability.ELIGIBLE
    assert set(public.controls.effective_modes.values()) == {OptionalControlMode.OFF}


def test_documentation_rag_selection_is_independent_from_access_and_adapter() -> None:
    basic = load_web_access_profile(BASIC_PROFILE)
    public = load_web_access_profile(PUBLIC_PROFILE)
    disabled = DocumentationRagFeatureProfile()
    enabled = DocumentationRagFeatureProfile(mode=DocumentationRagFeatureMode.ENABLED)

    assert (
        resolve_documentation_rag_state(
            access_profile=basic,
            feature_profile=disabled,
            adapter_available=False,
        )
        is DocumentationRagEffectiveState.UNAVAILABLE
    )
    assert (
        resolve_documentation_rag_state(
            access_profile=basic,
            feature_profile=enabled,
            adapter_available=False,
        )
        is DocumentationRagEffectiveState.UNAVAILABLE
    )
    assert (
        resolve_documentation_rag_state(
            access_profile=basic,
            feature_profile=enabled,
            adapter_available=True,
        )
        is DocumentationRagEffectiveState.ENABLED
    )
    assert (
        resolve_documentation_rag_state(
            access_profile=public,
            feature_profile=enabled,
            adapter_available=True,
        )
        is DocumentationRagEffectiveState.ENABLED
    )
    assert (
        resolve_documentation_rag_state(
            access_profile=basic,
            feature_profile=disabled,
            adapter_available=True,
        )
        is DocumentationRagEffectiveState.DISABLED
    )


def test_access_profiles_do_not_own_model_deployment_or_provider_selection() -> None:
    forbidden_fragments = (
        "qwen",
        "gguf",
        "llama",
        "lightning",
        "metal",
        "cuda",
        "aws",
        "azure",
        "model_key",
        "model_root",
        "deployment",
    )

    for profile_path in (BASIC_PROFILE, PUBLIC_PROFILE):
        tracked_text = profile_path.read_text(encoding="utf-8").lower()
        assert all(fragment not in tracked_text for fragment in forbidden_fragments)


@pytest.mark.parametrize(
    "replacement_key",
    [
        "access_mode",
        "authentication",
        "documentation_rag",
        "control_mode",
    ],
)
def test_invalid_or_unimplemented_public_profile_values_fail_closed(
    tmp_path: Path,
    replacement_key: str,
) -> None:
    source = PUBLIC_PROFILE.read_text(encoding="utf-8")
    old_value, new_value = {
        "access_mode": ('mode = "public_demo"', 'mode = "unknown"'),
        "authentication": ('authentication = "none"', 'authentication = "basic"'),
        "documentation_rag": (
            'documentation_rag = "eligible"',
            'documentation_rag = "unknown"',
        ),
        "control_mode": ('mode = "off"', 'mode = "observe"'),
    }[replacement_key]
    invalid_profile = tmp_path / "invalid-public-profile.toml"
    invalid_profile.write_text(source.replace(old_value, new_value, 1), encoding="utf-8")

    with pytest.raises(InferenceError) as captured:
        load_web_access_profile(invalid_profile)

    assert captured.value.safe_message == "The web access profile is invalid."
    assert str(invalid_profile) not in captured.value.safe_message


def test_disabled_control_policy_is_side_effect_free_and_reports_off() -> None:
    profile = load_web_access_profile(PUBLIC_PROFILE)
    policy = build_disabled_control_policy(profile)

    assert policy.mode is OptionalControlMode.OFF
    policy.check_request()
    policy.before_generation()
    policy.observe_generation()
    policy.after_generation()
