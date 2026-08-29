"""Role/provider/hardware-specific stage budgets for Judge and Repair."""

from __future__ import annotations

import hashlib
import json
import tomllib
from pathlib import Path

from pydantic import Field

from margpa_runtime_llm.modules.inference.contracts.base import ImmutableContract


class StageBudgetProfile(ImmutableContract):
    profile_id: str = Field(min_length=1, max_length=128)
    role: str = Field(pattern=r"^(judge|guard)$")
    provider_id: str = Field(min_length=1, max_length=128)
    hardware_profile: str = Field(min_length=1, max_length=128)
    verification_state: str = Field(min_length=1, max_length=64)
    load_budget_ms: int = Field(ge=0)
    prompt_build_budget_ms: int = Field(ge=0)
    inference_budget_ms: int = Field(ge=0)
    decode_budget_ms: int = Field(ge=0)
    repair_generation_budget_ms: int = Field(ge=0)
    rejudge_budget_ms: int = Field(ge=0)
    cancel_grace_ms: int = Field(ge=0)

    @property
    def enforce_pipeline_budget_ms(self) -> int:
        return (
            self.prompt_build_budget_ms
            + self.inference_budget_ms
            + self.decode_budget_ms
            + self.repair_generation_budget_ms
            + self.rejudge_budget_ms
        )

    @property
    def digest_sha512(self) -> str:
        payload = json.dumps(
            self.model_dump(mode="json"),
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        return hashlib.sha512(payload.encode()).hexdigest()


class StageBudgetRegistry(ImmutableContract):
    profiles: tuple[StageBudgetProfile, ...]

    def resolve(
        self, *, role: str, provider_id: str, hardware_profile: str
    ) -> StageBudgetProfile | None:
        return next(
            (
                profile
                for profile in self.profiles
                if profile.role == role
                and profile.provider_id == provider_id
                and profile.hardware_profile == hardware_profile
            ),
            None,
        )


def load_stage_budget_registry(path: Path) -> StageBudgetRegistry:
    with path.open("rb") as stream:
        return StageBudgetRegistry.model_validate(tomllib.load(stream))


LOCAL_MACOS_MAIN_SELF_JUDGE_BUDGET = StageBudgetProfile(
    profile_id="local_macos_main_self_judge_v1",
    role="judge",
    provider_id="main.self",
    hardware_profile="local.macos-arm64.metal",
    verification_state="configured_not_hardware_verified",
    load_budget_ms=180_000,
    prompt_build_budget_ms=5_000,
    inference_budget_ms=120_000,
    decode_budget_ms=5_000,
    repair_generation_budget_ms=180_000,
    rejudge_budget_ms=120_000,
    cancel_grace_ms=10_000,
)

LOCAL_MACOS_SELENE_JUDGE_BUDGET = LOCAL_MACOS_MAIN_SELF_JUDGE_BUDGET.model_copy(
    update={
        "profile_id": "local_macos_selene_judge_v1",
        "provider_id": "judge.selene-1-mini-llama-3.1-8b-q5-k-m",
    }
)

LOCAL_MACOS_BUILT_IN_JUDGE_BUDGET = StageBudgetProfile(
    profile_id="local_macos_built_in_judge_v1",
    role="judge",
    provider_id="built_in.deterministic",
    hardware_profile="local.macos-arm64.metal",
    verification_state="deterministic_no_model_call",
    load_budget_ms=0,
    prompt_build_budget_ms=0,
    inference_budget_ms=0,
    decode_budget_ms=0,
    repair_generation_budget_ms=0,
    rejudge_budget_ms=0,
    cancel_grace_ms=0,
)


def resolve_local_macos_judge_budget(provider_id: str | None) -> StageBudgetProfile:
    if provider_id == LOCAL_MACOS_BUILT_IN_JUDGE_BUDGET.provider_id:
        return LOCAL_MACOS_BUILT_IN_JUDGE_BUDGET
    if provider_id == LOCAL_MACOS_SELENE_JUDGE_BUDGET.provider_id:
        return LOCAL_MACOS_SELENE_JUDGE_BUDGET
    return LOCAL_MACOS_MAIN_SELF_JUDGE_BUDGET


LOCAL_MACOS_QWEN3GUARD_BUDGET = LOCAL_MACOS_MAIN_SELF_JUDGE_BUDGET.model_copy(
    update={
        "profile_id": "local_macos_qwen3guard_v1",
        "role": "guard",
        "provider_id": "guard.qwen3guard-gen-0.6b-q8-0",
    }
)
