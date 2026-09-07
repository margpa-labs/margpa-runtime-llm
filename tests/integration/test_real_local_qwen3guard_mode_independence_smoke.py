"""P9-1 Component Independence Rework (WU-03): verifies, with real Evidence,
whether Qwen3Guard's Detection result genuinely depends on Mode (OBSERVE vs
ENFORCE) or is merely stochastic call-to-call sampling variance dressed up
as a Mode difference.

Component Independence Handoff (`phase_9_controller_component_independence_
gemma_guard_main_rework_exact_handoff_ja_20260905121655.md` section 2,
確定Failure): a clear Prompt Injection input is confirmed working correctly
under both OBSERVE and ENFORCE, but the same benign verification input showed
Match=1/Action=1 under Guard ENFORCE and Match=0/Action=0 under OBSERVE --
suspected Mode-dependent classification divergence and over-intervention.
WU-03's own instruction explicitly forbids concluding this is a genuine
Mode-coupling defect before first verifying under identical Input/Target/
Provider conditions.

Code-level structural finding (this module's own docstring records it,
established via direct source reading before writing this Test -- see the
Exact Return for the exact call chain): `Qwen3GuardGenAdapter.classify_
point()` (`qwen3guard_adapter.py`) and `Qwen3GuardDetectorAdapter.detect()`
(`qwen3guard_detector_adapter.py`) never receive a Mode argument anywhere --
Mode is used exclusively by `GuardrailPointRuntime`/the Guard Pre/Post Hook
layer to decide whether to *act* on an already-computed Detection, never fed
into the Detector or the Model Prompt/Decode path at all. Structurally,
Detection cannot depend on Mode by construction. The confirmed real
divergence must therefore come from either (a) genuine stochastic sampling
variance across two separate real Model Calls -- `classify_point()` sets
only `max_new_tokens` on its `GenerationParameters`, leaving temperature=0.7/
top_p=0.8/top_k=20/seed=None (the generic Library Default, exactly like the
Judge's own `SeleneSemanticEvaluator._generate_with_busy_retry()`, WU-02) --
or (b) the two real trials this Handoff's §2 describes used non-identical
real input text (a real "OBSERVE session" and a real "ENFORCE session" are
two distinct user interactions, not a controlled same-input comparison).

This Test isolates (a): it calls the real `Qwen3GuardGenAdapter.classify_
point()` directly, twice, back-to-back, with byte-identical content/target/
provider (Mode is not even a parameter this layer accepts, so there is
nothing to vary between the two calls except the real Model's own sampling)
-- confirming or refuting genuine non-determinism with real Evidence, never
assumption. If confirmed non-deterministic, WU-03 explicitly authorizes a
targeted remedy: "必要ならQwen3Guard Role専用の確定的Generation Parameterを
導入する" (a Role-scoped, deterministic Generation Parameter Contract for
Qwen3Guard specifically -- never a project-wide Judge/Guard Generation
Default change)."""

from __future__ import annotations

import platform
from pathlib import Path

import pytest

from margpa_runtime_llm.adapters.guardrail_governance.qwen3guard_adapter import (
    Qwen3GuardGenAdapter,
)
from margpa_runtime_llm.adapters.model_backends.llama_cpp.adapter import LlamaCppModelAdapter
from margpa_runtime_llm.adapters.runtime_model_control.model_definition_registry import (
    DirectoryModelDefinitionRegistry,
)
from margpa_runtime_llm.modules.guardrail_governance.domain import (
    DetectionOutcome,
    Qwen3GuardTarget,
    SafetyModelFailureKind,
)
from margpa_runtime_llm.modules.inference.application.inference_service import InferenceService
from margpa_runtime_llm.modules.inference.contracts.runtime import ModelLoadConfig

PROJECT_ROOT = Path(__file__).resolve().parents[2]
MODEL_ROOT = PROJECT_ROOT / "models"
GUARD_MODEL_KEY = "guard.qwen3guard-gen-0.6b-q8-0"
GUARD_ARTIFACT_PATH = (
    MODEL_ROOT / "guard/qwen3guard-gen-0.6b/gguf/Qwen.Qwen3Guard-Gen-0.6B.Q8_0.gguf"
)
GUARD_MANIFEST = PROJECT_ROOT / "config/guardrail/qwen3guard/manifest.json"
GUARD_CONTEXT = 4096

_REQUIRES_APPLE_SILICON = pytest.mark.skipif(
    platform.system() != "Darwin" or platform.machine() != "arm64",
    reason="Local real-hardware Model Smoke requires Apple Silicon macOS",
)

# The confirmed real Failure is specific to a *benign* input -- a clear
# Prompt Injection input is explicitly already confirmed working correctly
# across both Modes (Handoff §2), so this Test targets only the benign case.
_BENIGN_INPUT = "What is the capital of France?"


@pytest.mark.model_smoke
@_REQUIRES_APPLE_SILICON
def test_a_real_benign_input_classified_twice_under_identical_conditions() -> None:
    """Mode is not even a parameter `classify_point()` accepts -- this Test
    calls it twice, back-to-back, with byte-identical `content`/`target`,
    against the same loaded real Qwen3Guard Adapter (same Provider, same
    Artifact, same Manifest). Any divergence between the two real
    Classifications is therefore, by construction, never a Mode effect --
    it can only be genuine call-to-call sampling non-determinism.

    Exactly one real-hardware trial this round (two real Model Calls within
    it, both required to answer the same question -- not two separate
    authorized trials). Reports the real outcome as-is; no fix is applied
    inside this Test regardless of the result."""
    if not GUARD_ARTIFACT_PATH.is_file():
        pytest.skip(f"Local Qwen3Guard model artifact is unavailable: {GUARD_ARTIFACT_PATH}")
    definitions = DirectoryModelDefinitionRegistry(registry_dir=PROJECT_ROOT / "config/models")
    service = InferenceService(LlamaCppModelAdapter(model_root=MODEL_ROOT))
    service.load(
        definitions.resolve(model_key=GUARD_MODEL_KEY),
        ModelLoadConfig(context_size=GUARD_CONTEXT, gpu_layers=-1),
    )
    try:
        runtime_info = service.runtime_info
        assert runtime_info is not None
        adapter = Qwen3GuardGenAdapter(
            service=service,
            model_id=GUARD_MODEL_KEY,
            artifact_digest_sha512=runtime_info.artifact_digest.value,
            manifest_path=GUARD_MANIFEST,
        )

        first = adapter.classify_point(target=Qwen3GuardTarget.INPUT, content=_BENIGN_INPUT)
        second = adapter.classify_point(target=Qwen3GuardTarget.INPUT, content=_BENIGN_INPUT)

        def _summary(classification: object) -> str:
            failure = getattr(classification, "failure", None)
            detections = getattr(classification, "detections", ())
            primary = detections[0] if detections else None
            return (
                f"failure={failure!r} "
                f"outcome={getattr(primary, 'outcome', None)!r} "
                f"category_id={getattr(primary, 'category_id', None)!r} "
                f"latency_ms={getattr(classification, 'latency_ms', None)} "
                f"token_count={getattr(classification, 'token_count', None)} "
                f"call_count={getattr(classification, 'call_count', None)}"
            )

        first_clear = (
            first.failure is SafetyModelFailureKind.NONE
            and bool(first.detections)
            and first.detections[0].outcome is DetectionOutcome.CLEAR
        )
        second_clear = (
            second.failure is SafetyModelFailureKind.NONE
            and bool(second.detections)
            and second.detections[0].outcome is DetectionOutcome.CLEAR
        )
        print(
            "[real-qwen3guard-mode-independence-evidence] "
            f"input={_BENIGN_INPUT!r} "
            f"first=({_summary(first)}) "
            f"second=({_summary(second)}) "
            f"first_clear={first_clear} second_clear={second_clear} "
            f"identical_outcome={first_clear == second_clear}"
        )

        # This Test's own True crux: whether real repeated Detection under
        # byte-identical Input/Target/Provider is stable. Both possible
        # real outcomes are informative and are reported honestly above
        # regardless of which one occurs -- this assertion documents which
        # one this specific trial produced, it does not presuppose it.
        assert first_clear == second_clear, (
            "Real Evidence: two back-to-back classify_point() calls with "
            "byte-identical content/target/provider produced DIFFERENT "
            "Detection outcomes -- confirms genuine stochastic sampling "
            "non-determinism (Mode was never a parameter to either call), "
            "not a Mode-coupling defect. See this module's own docstring "
            "for the WU-03-authorized remedy (a Role-scoped deterministic "
            "Generation Parameter Contract for Qwen3Guard)."
        )
    finally:
        service.unload()
