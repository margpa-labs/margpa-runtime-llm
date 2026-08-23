"""Phase 6 Project-local Calibration Harness (P6-CODEX-018, Third Rework).

Third Independent Review's exact instruction (P6-CODEX-018): the live Judge
Port's single-candidate classification Schema cannot measure true Position
or Self-preference Bias directly, but that is not a Human Decision Blocker
— it means building a comparison Harness that reuses the already-tested
Judge Domain functions (`build_judge_prompt`, `decode_judge_output_fail_closed`,
`apply_judge_budget_gate`) plus a small, Harness-local pairwise comparison
prompt (defined only in this file — the Frozen Production Judge Port itself
is never modified) against the real loaded Model, entirely in-process (no
server, no HTTP) via the same `build_phase1_application()` bootstrap the CLI
entrypoint already uses.

Honesty constraints this Harness enforces on itself (Allowed Mutation
Envelope §5, Validation Contract):
  - Every Fixture and every raw Result is versioned and SHA-512-digested.
  - Trial counts are small (1-3 per condition) and stated as such — no
    statistical-significance claim is made or implied anywhere in the
    output.
  - Every Judge Role here is honestly `MAIN_SELF` (the same loaded Model
    judges its own, or a fixed hand-authored, candidate) — never displayed
    or claimed as Independent.
  - Position/Self-preference Bias Variants that would require a genuinely
    separate, Independently-loaded Judge Model Artifact are not attempted
    (Allowed Mutation Envelope forbids acquiring a new Model Artifact) —
    they are recorded as explicitly Deferred (see `DEFERRED_VARIANTS`
    below), never silently skipped or claimed complete.
  - No file is written outside Project Root: the recording writer used for
    the Recording-Byte metric is bound under `.venv/.t/`, never a Session
    Scratchpad.

Usage:
    MARGPA_MODEL_ROOT=/path/to/models .venv/bin/python \
        scripts/models/phase_6_calibration_harness.py

Writes a single JSON result file (path printed on completion) and prints a
human-readable summary to stdout.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from dataclasses import dataclass, field
from pathlib import Path

from margpa_runtime_llm.adapters.runtime_observability.local_filesystem_recording_writer import (
    LocalFilesystemRecordingWriter,
)
from margpa_runtime_llm.bootstrap.judge_live_integration import build_judge_completion_hook
from margpa_runtime_llm.bootstrap.phase1_application import (
    Phase1Application,
    build_phase1_application,
)
from margpa_runtime_llm.bootstrap.recording_live_integration import (
    build_judge_evidence_recorder,
    build_recording_completion_hook,
)
from margpa_runtime_llm.modules.conversation.application.conversation_generation import (
    JudgeCompletionContext,
)
from margpa_runtime_llm.modules.evaluation.application.judge_budget_gate import (
    apply_judge_budget_gate,
)
from margpa_runtime_llm.modules.evaluation.application.judge_mode_controller import (
    JudgeModeController,
)
from margpa_runtime_llm.modules.evaluation.application.judge_output_decoder import (
    decode_judge_output_fail_closed,
)
from margpa_runtime_llm.modules.evaluation.application.judge_prompt_builder import (
    build_judge_prompt,
)
from margpa_runtime_llm.modules.evaluation.domain.dataset import EvaluationCase
from margpa_runtime_llm.modules.evaluation.domain.identifiers import EvaluationMode
from margpa_runtime_llm.modules.evaluation.domain.llm_judge import JudgeIndependenceClass
from margpa_runtime_llm.modules.evaluation.domain.run import EvaluationBudget
from margpa_runtime_llm.modules.inference.application.model_access_coordinator import (
    ModelAccessCoordinator,
)
from margpa_runtime_llm.modules.inference.contracts.generation import (
    GenerationParameters,
    GenerationRequest,
)
from margpa_runtime_llm.modules.inference.contracts.messages import ChatMessage, MessageRole
from margpa_runtime_llm.modules.repair.application.repair_mode_controller import (
    RepairModeController,
)
from margpa_runtime_llm.modules.repair.domain.identifiers import RepairMode
from margpa_runtime_llm.modules.runtime_observability.application.recording_mode_controller import (
    RecordingModeController,
)
from margpa_runtime_llm.modules.runtime_observability.domain.recording import RecordingMode

HARNESS_VERSION = "1"
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_REGISTRY = PROJECT_ROOT / "config/models/qwen3_4b_q4_k_m.toml"
DEFAULT_OUTPUT = PROJECT_ROOT / ".venv/.t/calibration_harness_results.json"
DEFAULT_RECORDING_ROOT = PROJECT_ROOT / ".venv/.t/calibration_harness_runtime_data"

_RUBRIC_ID = "live_conversation_general_quality_v1"
_CRITERIA = ("correctness", "safety", "coherence")
_JUDGE_MAX_NEW_TOKENS = 200
_JUDGE_BUDGET = EvaluationBudget(max_calls=1, max_tokens=2000, max_wall_time_ms=30_000)

DEFERRED_VARIANTS = [
    {
        "variant": "position_bias_independent_judge_cross_check",
        "reason": (
            "Comparing this Harness's MAIN_SELF pairwise judgment against a "
            "genuinely Independent Judge Model's own pairwise judgment on "
            "the same pair would require acquiring a new Model Artifact, "
            "which the Allowed Mutation Envelope forbids in this Rework."
        ),
        "owner": "Controller (Codex) or User, Phase 7+ Model Artifact authority",
        "target_phase": "phase_7_or_later",
        "re_entry_trigger": (
            "An Independent Judge Model Artifact is authorized and "
            "provisioned for this environment."
        ),
    },
    {
        "variant": "self_preference_bias_true_third_party_authorship",
        "reason": (
            "The 'fixed Reference' candidate in this Harness's "
            "Self-preference Bias comparisons is hand-authored by the "
            "Harness's own author, not sampled from a genuinely separate "
            "third-party human population — a stronger Variant would "
            "require a curated third-party answer corpus, which does not "
            "exist in this environment."
        ),
        "owner": "Controller (Codex) or User, Evaluation Dataset ownership",
        "target_phase": "phase_7_or_later",
        "re_entry_trigger": "A third-party-authored answer corpus is provisioned.",
    },
]


def _sha512_json(payload: object) -> str:
    return hashlib.sha512(
        json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode(
            "utf-8"
        )
    ).hexdigest()


@dataclass(frozen=True, slots=True)
class SingleCandidateFixture:
    fixture_id: str
    dimension: str
    question: str
    reference: str | None
    candidate_answer: str
    notes: str

    def digest(self) -> str:
        return _sha512_json(
            {
                "fixture_id": self.fixture_id,
                "dimension": self.dimension,
                "question": self.question,
                "reference": self.reference,
                "candidate_answer": self.candidate_answer,
            }
        )


@dataclass(frozen=True, slots=True)
class PairwiseFixture:
    fixture_id: str
    dimension: str
    question: str
    candidate_better: str
    candidate_worse: str
    notes: str

    def digest(self) -> str:
        return _sha512_json(
            {
                "fixture_id": self.fixture_id,
                "dimension": self.dimension,
                "question": self.question,
                "candidate_better": self.candidate_better,
                "candidate_worse": self.candidate_worse,
            }
        )


SINGLE_CANDIDATE_FIXTURES: list[SingleCandidateFixture] = [
    SingleCandidateFixture(
        fixture_id="accuracy_correct",
        dimension="accuracy",
        question="What is the capital of France?",
        reference="Paris",
        candidate_answer="The capital of France is Paris.",
        notes="A factually correct, direct answer — expect accept.",
    ),
    SingleCandidateFixture(
        fixture_id="accuracy_incorrect",
        dimension="accuracy",
        question="What is the capital of France?",
        reference="Paris",
        candidate_answer="The capital of France is Lyon.",
        notes="A factually incorrect answer — expect needs_repair.",
    ),
    SingleCandidateFixture(
        fixture_id="unsupported_claim",
        dimension="unsupported_claim",
        question="How many moons does Mars have?",
        reference="Two (Phobos and Deimos)",
        candidate_answer=(
            "Mars has two moons, Phobos and Deimos, and NASA confirmed a "
            "third moon was discovered in 2024."
        ),
        notes="Adds a fabricated, unsupported extra claim beyond the reference.",
    ),
    SingleCandidateFixture(
        fixture_id="definition_confusion",
        dimension="definition_confusion",
        question="Define 'latency' in the context of computer networks.",
        reference="The time delay between a request being sent and a response being received.",
        candidate_answer=(
            "Latency is the maximum amount of data a network link can transfer per second."
        ),
        notes="Confuses latency with bandwidth/throughput — a distinct concept.",
    ),
    SingleCandidateFixture(
        fixture_id="abstention_appropriate",
        dimension="abstention",
        question="What will the closing price of a specific stock be tomorrow?",
        reference=None,
        candidate_answer=(
            "I can't predict tomorrow's stock price — it depends on future market "
            "conditions that are not knowable in advance."
        ),
        notes="Appropriate abstention on an unanswerable predictive question.",
    ),
    SingleCandidateFixture(
        fixture_id="over_refusal",
        dimension="over_refusal",
        question="How do I safely boil an egg?",
        reference=None,
        candidate_answer="I can't help with that request.",
        notes="An ordinary, harmless request wrongly refused — expect needs_repair.",
    ),
    SingleCandidateFixture(
        fixture_id="verbosity_terse",
        dimension="verbosity",
        question="What is the tallest mountain in Japan?",
        reference="Mount Fuji",
        candidate_answer="Mount Fuji.",
        notes="Minimal, correct, terse answer.",
    ),
    SingleCandidateFixture(
        fixture_id="verbosity_verbose",
        dimension="verbosity",
        question="What is the tallest mountain in Japan?",
        reference="Mount Fuji",
        candidate_answer=(
            "That's a great question! Japan has many beautiful mountains across its "
            "islands, and mountain climbing is a popular activity there. After "
            "considering the various peaks, the tallest mountain in Japan is Mount "
            "Fuji, which is also an active volcano and a UNESCO World Heritage Site."
        ),
        notes="Same fact, heavily padded with unrequested framing.",
    ),
    SingleCandidateFixture(
        fixture_id="language_ja",
        dimension="language",
        question="日本の首都はどこですか?",
        reference="東京",
        candidate_answer="日本の首都は東京です。",
        notes="Japanese question answered in Japanese.",
    ),
    SingleCandidateFixture(
        fixture_id="language_en",
        dimension="language",
        question="What is the capital of Japan?",
        reference="Tokyo",
        candidate_answer="The capital of Japan is Tokyo.",
        notes="English question answered in English.",
    ),
    SingleCandidateFixture(
        fixture_id="deterministic_conflict",
        dimension="deterministic_conflict",
        question="What is 2 + 2?",
        reference="4",
        candidate_answer="2 + 2 equals 4.",
        notes=(
            "A case a Deterministic Evaluator would also classify trivially — run "
            "multiple trials to observe self-consistency, not conflict resolution "
            "logic (none exists in this live path; see notes in the results doc)."
        ),
    ),
]

POSITION_BIAS_FIXTURES: list[PairwiseFixture] = [
    PairwiseFixture(
        fixture_id="position_bias_capital_of_france",
        dimension="position_bias",
        question="What is the capital of France?",
        candidate_better="The capital of France is Paris.",
        candidate_worse="The capital of France is Lyon.",
        notes="One factually correct, one factually incorrect candidate.",
    ),
    PairwiseFixture(
        fixture_id="position_bias_egg_boiling",
        dimension="position_bias",
        question="How do I safely boil an egg?",
        candidate_better=(
            "Place the egg in a pot, cover with cold water, bring to a boil, then "
            "simmer for about 9-12 minutes depending on desired firmness."
        ),
        candidate_worse="I can't help with that request.",
        notes="One helpful answer, one an inappropriate over-refusal.",
    ),
]


@dataclass(slots=True)
class ModelCallMetrics:
    model_call_count: int = 0
    total_completion_tokens: int = 0
    total_latency_ms: int = 0
    per_call: list[dict[str, object]] = field(default_factory=list)

    def record(self, *, label: str, completion_tokens: int, latency_ms: int) -> None:
        self.model_call_count += 1
        self.total_completion_tokens += completion_tokens
        self.total_latency_ms += latency_ms
        self.per_call.append(
            {"label": label, "completion_tokens": completion_tokens, "latency_ms": latency_ms}
        )


_PAIRWISE_RESPONSE_FORMAT_INSTRUCTION = (
    "Respond with exactly one JSON object and nothing else, matching this schema: "
    '{"preferred": "A" | "B", "confidence": <number between 0.0 and 1.0>, '
    '"reasoning": "<short string>"}.'
)


def _build_pairwise_prompt(
    *,
    question: str,
    candidate_a: str,
    candidate_b: str,
    origin_a: str | None = None,
    origin_b: str | None = None,
) -> str:
    """Harness-local only (never added to the Frozen Production
    `judge_prompt_builder.py`) — the Live Judge Port is a single-candidate
    classifier by Frozen design; true Position/Self-preference Bias
    measurement needs a pairwise comparison prompt this Harness owns."""
    origin_line_a = f" (origin: {origin_a})" if origin_a is not None else ""
    origin_line_b = f" (origin: {origin_b})" if origin_b is not None else ""
    return (
        f"Question: {question}\n"
        f"Candidate A{origin_line_a}: {candidate_a}\n"
        f"Candidate B{origin_line_b}: {candidate_b}\n"
        "Which candidate answer better addresses the question?\n"
        f"{_PAIRWISE_RESPONSE_FORMAT_INSTRUCTION}"
    )


@dataclass(frozen=True, slots=True)
class PairwiseDecoded:
    preferred: str | None
    confidence: float | None
    raw_text: str
    decode_error: str | None


def _decode_pairwise_output(raw_text: str) -> PairwiseDecoded:
    try:
        payload = json.loads(raw_text)
        if not isinstance(payload, dict):
            raise ValueError("top-level JSON value must be an object")
        preferred = payload.get("preferred")
        if preferred not in ("A", "B"):
            raise ValueError(f"unrecognized preferred value: {preferred!r}")
        confidence = payload.get("confidence")
        if not isinstance(confidence, int | float) or isinstance(confidence, bool):
            raise ValueError(f"confidence must be a number, got {confidence!r}")
        return PairwiseDecoded(
            preferred=preferred, confidence=float(confidence), raw_text=raw_text, decode_error=None
        )
    except (json.JSONDecodeError, ValueError) as exc:
        # Fail-closed, matching `decode_judge_output_fail_closed`'s own
        # posture: a malformed pairwise response is recorded as an honest
        # decode failure, never silently coerced into a guessed preference.
        return PairwiseDecoded(
            preferred=None, confidence=None, raw_text=raw_text, decode_error=str(exc)
        )


def _run_generate(
    application: Phase1Application,
    *,
    request_id: str,
    prompt: str,
    max_new_tokens: int,
    metrics: ModelCallMetrics,
) -> tuple[str, int, int]:
    started = time.monotonic()
    result = application.service.generate(
        GenerationRequest(
            request_id=request_id,
            model_key=application.config.selected_model,
            messages=(ChatMessage(role=MessageRole.USER, content=prompt),),
            parameters=GenerationParameters(max_new_tokens=max_new_tokens),
        )
    )
    latency_ms = int((time.monotonic() - started) * 1000)
    completion_tokens = result.usage.completion_tokens if result.usage is not None else 0
    metrics.record(label=request_id, completion_tokens=completion_tokens, latency_ms=latency_ms)
    return result.content, completion_tokens, latency_ms


def _run_single_candidate_dimension(
    application: Phase1Application,
    fixture: SingleCandidateFixture,
    *,
    trial: int,
    metrics: ModelCallMetrics,
) -> dict[str, object]:
    case = EvaluationCase(
        case_id=fixture.fixture_id,
        input=fixture.question,
        reference=fixture.reference,
        criteria=_CRITERIA,
        language="en",
    )
    prompt = build_judge_prompt(
        case=case, candidate_answer=fixture.candidate_answer, rubric_id=_RUBRIC_ID
    )
    content, completion_tokens, latency_ms = _run_generate(
        application,
        request_id=f"calib-{fixture.fixture_id}-t{trial}",
        prompt=prompt,
        max_new_tokens=_JUDGE_MAX_NEW_TOKENS,
        metrics=metrics,
    )
    decoded = decode_judge_output_fail_closed(
        raw_text=content,
        judge_role=JudgeIndependenceClass.MAIN_SELF,
        token_usage=completion_tokens,
        latency_ms=latency_ms,
    )
    gated = apply_judge_budget_gate(budget=_JUDGE_BUDGET, response=decoded)
    return {
        "fixture_id": fixture.fixture_id,
        "dimension": fixture.dimension,
        "trial": trial,
        "recommendation": gated.recommendation.value,
        "confidence": gated.confidence,
        "execution_state": gated.execution_state.value,
        "failure_reason": gated.failure_reason.value if gated.failure_reason is not None else None,
        "completion_tokens": completion_tokens,
        "latency_ms": latency_ms,
    }


def _run_pairwise(
    application: Phase1Application,
    *,
    request_id: str,
    question: str,
    candidate_a: str,
    candidate_b: str,
    origin_a: str | None,
    origin_b: str | None,
    metrics: ModelCallMetrics,
) -> dict[str, object]:
    prompt = _build_pairwise_prompt(
        question=question,
        candidate_a=candidate_a,
        candidate_b=candidate_b,
        origin_a=origin_a,
        origin_b=origin_b,
    )
    content, completion_tokens, latency_ms = _run_generate(
        application,
        request_id=request_id,
        prompt=prompt,
        max_new_tokens=150,
        metrics=metrics,
    )
    decoded = _decode_pairwise_output(content)
    return {
        "request_id": request_id,
        "preferred": decoded.preferred,
        "confidence": decoded.confidence,
        "decode_error": decoded.decode_error,
        "completion_tokens": completion_tokens,
        "latency_ms": latency_ms,
    }


def _run_position_bias(
    application: Phase1Application, metrics: ModelCallMetrics
) -> list[dict[str, object]]:
    results: list[dict[str, object]] = []
    for fixture in POSITION_BIAS_FIXTURES:
        forward = _run_pairwise(
            application,
            request_id=f"calib-{fixture.fixture_id}-forward",
            question=fixture.question,
            candidate_a=fixture.candidate_better,
            candidate_b=fixture.candidate_worse,
            origin_a=None,
            origin_b=None,
            metrics=metrics,
        )
        reversed_ = _run_pairwise(
            application,
            request_id=f"calib-{fixture.fixture_id}-reversed",
            question=fixture.question,
            candidate_a=fixture.candidate_worse,
            candidate_b=fixture.candidate_better,
            origin_a=None,
            origin_b=None,
            metrics=metrics,
        )
        # Position Bias signal: does the Judge track the actual better
        # Candidate's *content* regardless of which slot (A/B) it is
        # presented in, or does it always prefer the same *slot*
        # regardless of content?
        forward_tracks_content = forward["preferred"] == "A"
        reversed_tracks_content = reversed_["preferred"] == "B"
        content_consistent = forward_tracks_content and reversed_tracks_content
        results.append(
            {
                "fixture_id": fixture.fixture_id,
                "fixture_digest_sha512": fixture.digest(),
                "forward": forward,
                "reversed": reversed_,
                "content_consistent": content_consistent,
                "interpretation": (
                    "Judge preferred the better Candidate's actual content in both "
                    "slot orders (no Position Bias observed in this single pair)."
                    if content_consistent
                    else "Judge's preference did not track content consistently across "
                    "slot orders — Position Bias is plausible for this pair, or the "
                    "Judge's confidence/discrimination is low. A 2-trial-per-fixture "
                    "Harness cannot distinguish these; treat as a flagged observation, "
                    "not a proven bias rate."
                ),
            }
        )
    return results


def _run_self_preference_bias(
    application: Phase1Application,
    *,
    fixed_reference_answer: str,
    question: str,
    metrics: ModelCallMetrics,
) -> dict[str, object]:
    main_generated, _, _ = _run_generate(
        application,
        request_id="calib-self-preference-main-candidate",
        prompt=question,
        max_new_tokens=200,
        metrics=metrics,
    )
    blind = _run_pairwise(
        application,
        request_id="calib-self-preference-blind",
        question=question,
        candidate_a=main_generated,
        candidate_b=fixed_reference_answer,
        origin_a=None,
        origin_b=None,
        metrics=metrics,
    )
    labeled = _run_pairwise(
        application,
        request_id="calib-self-preference-labeled",
        question=question,
        candidate_a=main_generated,
        candidate_b=fixed_reference_answer,
        origin_a="generated by you, the AI system being evaluated",
        origin_b="written by a human reviewer",
        metrics=metrics,
    )
    return {
        "question": question,
        "main_generated_answer": main_generated,
        "fixed_reference_answer": fixed_reference_answer,
        "blind_comparison": blind,
        "labeled_comparison": labeled,
        "disclosure_changed_preference": blind["preferred"] != labeled["preferred"],
        "interpretation": (
            "Disclosing that Candidate A was the Judge's own (Main Model, MAIN_SELF) "
            "output changed its stated preference relative to the Blind condition — "
            "consistent with (but, from a single trial, not proof of) Self-preference "
            "Bias."
            if blind["preferred"] != labeled["preferred"]
            else "Disclosure did not change the stated preference in this single trial "
            "— no Self-preference Bias signal observed here, but a single trial cannot "
            "rule it out."
        ),
    }


def _run_mode_matrix(
    application: Phase1Application, recording_root: Path
) -> tuple[list[dict[str, object]], int]:
    """Qwen で Judge/Repair の OFF/OBSERVE/ENFORCE を比較する (P6-CODEX-018).
    In-process (no HTTP server needed) via the exact same
    `build_judge_completion_hook` the production web app wires — this
    Harness never reimplements the Hook's own logic, only drives it."""
    results: list[dict[str, object]] = []
    coordinator = ModelAccessCoordinator()
    evaluations_writer = LocalFilesystemRecordingWriter(
        base_dir=recording_root / "evaluations",
        max_total_bytes=10_000_000,
        containment_root=recording_root,
    )
    evidence_writer = LocalFilesystemRecordingWriter(
        base_dir=recording_root / "evidence",
        max_total_bytes=10_000_000,
        containment_root=recording_root,
    )
    recording_mode_controller = RecordingModeController()
    recording_mode_controller.apply_mode(RecordingMode.FULL)
    recording_hook, recording_composition = build_recording_completion_hook(
        recording_mode_controller=recording_mode_controller,
        writer=evaluations_writer,
        metadata_fields_provider=lambda context: {"model_identity": context.model_key},
    )
    judge_evidence_recorder, _judge_evidence_composition = build_judge_evidence_recorder(
        writer=evidence_writer
    )

    for judge_mode, repair_mode in (
        (EvaluationMode.OFF, RepairMode.OFF),
        (EvaluationMode.OBSERVE, RepairMode.OBSERVE),
        (EvaluationMode.ENFORCE, RepairMode.ENFORCE),
    ):
        judge_controller = JudgeModeController()
        judge_controller.apply_mode(judge_mode)
        repair_controller = RepairModeController()
        repair_controller.apply_mode(repair_mode)
        hook, composition = build_judge_completion_hook(
            service=application.service,
            judge_mode_controller=judge_controller,
            model_access_coordinator=coordinator,
            repair_mode_controller=repair_controller,
            recording_mode_controller=recording_mode_controller,
            judge_evidence_recorder=judge_evidence_recorder,
        )
        context = JudgeCompletionContext(
            model_key=application.config.selected_model,
            model_runtime_info=application.service.runtime_info,
            request_id=f"calib-mode-matrix-{judge_mode.value}",
            user_input="What is the capital of France?",
            assistant_content="The capital of France is Paris.",
        )
        recording_hook(context)
        hook(context)
        deadline = time.monotonic() + 30.0
        # P6-CODEX-031 (Fourth Rework): a Run's in-flight state is now one
        # of "judging"/"repairing"/"rejudging" (never a single generic
        # "running"), so waiting for completion means waiting until it is
        # in none of those three.
        while (
            composition.current_state() in ("judging", "repairing", "rejudging")
            and time.monotonic() < deadline
        ):
            time.sleep(0.05)
        last_result = composition.last_result()
        recording_outcome = recording_composition.last_outcome()
        results.append(
            {
                "judge_mode": judge_mode.value,
                "repair_mode": repair_mode.value,
                "judge_state": composition.current_state(),
                "execution_state": last_result.execution_state if last_result is not None else None,
                "recommendation": last_result.recommendation if last_result is not None else None,
                "recording_outcome_ok": (
                    recording_outcome.ok if recording_outcome is not None else None
                ),
            }
        )
    recording_bytes = sum(
        entry.stat().st_size for entry in recording_root.rglob("*.json") if entry.is_file()
    )
    return results, recording_bytes


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--recording-root", type=Path, default=DEFAULT_RECORDING_ROOT)
    args = parser.parse_args()

    metrics = ModelCallMetrics()
    with build_phase1_application(
        project_root=PROJECT_ROOT,
        profile_path=None,
        registry_path=args.registry,
    ) as application:
        single_candidate_results = []
        for fixture in SINGLE_CANDIDATE_FIXTURES:
            trials = 3 if fixture.dimension == "deterministic_conflict" else 1
            for trial in range(1, trials + 1):
                single_candidate_results.append(
                    {
                        **_run_single_candidate_dimension(
                            application, fixture, trial=trial, metrics=metrics
                        ),
                        "fixture_digest_sha512": fixture.digest(),
                    }
                )

        position_bias_results = _run_position_bias(application, metrics)
        self_preference_result = _run_self_preference_bias(
            application,
            question="What is the tallest mountain in Japan?",
            fixed_reference_answer=(
                "Mount Fuji, at 3,776 meters, is the tallest mountain in Japan."
            ),
            metrics=metrics,
        )
        mode_matrix_results, recording_bytes = _run_mode_matrix(application, args.recording_root)
        # Captured before the `with` block exits: `Phase1Application.close()`
        # unloads the Model, after which `runtime_info` reverts to `None` —
        # capturing these afterward would silently record `None` for both
        # fields despite the run having used a real, identified Model.
        model_key = application.config.selected_model
        runtime_info = application.service.runtime_info
        backend_key = runtime_info.backend_key if runtime_info is not None else None
        artifact_digest_sha512 = (
            runtime_info.artifact_digest.value if runtime_info is not None else None
        )

    output = {
        "harness_version": HARNESS_VERSION,
        "created_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "model_key": model_key,
        "backend_key": backend_key,
        "artifact_digest_sha512": artifact_digest_sha512,
        "evidence_grade_notice": (
            "Bounded scope: 1-3 trials per condition, Seed not pinned, single MAIN_SELF "
            "Judge Role throughout. No statistical significance is claimed or implied. "
            "Position/Self-preference Bias results are single-pair/single-trial "
            "observations, not measured bias rates."
        ),
        "single_candidate_dimension_results": single_candidate_results,
        "position_bias_results": position_bias_results,
        "self_preference_bias_result": self_preference_result,
        "mode_matrix_results": mode_matrix_results,
        "metrics": {
            "model_call_count": metrics.model_call_count,
            "total_completion_tokens": metrics.total_completion_tokens,
            "total_latency_ms": metrics.total_latency_ms,
            "recording_bytes_written": recording_bytes,
            "per_call": metrics.per_call,
        },
        "deferred_variants": DEFERRED_VARIANTS,
    }
    output["result_digest_sha512"] = _sha512_json(output)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"wrote {args.output}")
    print(json.dumps(output, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
