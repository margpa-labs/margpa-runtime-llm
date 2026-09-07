"""Dedicated Selene prompt/decoder/runtime adapter.

Manifest provenance is explicit and fail-closed:
1) a verified official copy with immutable upstream revision, or
2) a checked-in project-derived contract with its own immutable digest.
"""

from __future__ import annotations

import hashlib
import json
import re
import time
from collections.abc import Callable, Mapping
from concurrent.futures import Future
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol, cast

from pydantic import BaseModel, ConfigDict, Field

from margpa_runtime_llm.bootstrap.stage_deadline import stage_deadline
from margpa_runtime_llm.bootstrap.tracked_stage_worker import (
    TrackedStageWorkerRegistry,
    run_tracked_stage,
)
from margpa_runtime_llm.modules.evaluation.application.judge_output_decoder import (
    JudgeDecodeError,
    decode_judge_output,
)
from margpa_runtime_llm.modules.evaluation.domain.llm_judge import (
    JudgeCriterionDisposition,
    JudgeIndependenceClass,
)
from margpa_runtime_llm.modules.evaluation.domain.stage_budget import (
    LOCAL_MACOS_SELENE_JUDGE_BUDGET,
)
from margpa_runtime_llm.modules.inference.application.inference_service import InferenceService
from margpa_runtime_llm.modules.inference.contracts.generation import (
    FinishReason,
    GenerationParameters,
    GenerationRequest,
    GenerationResult,
    StructuredOutputConstraint,
    ThinkingMode,
)
from margpa_runtime_llm.modules.inference.contracts.messages import ChatMessage, MessageRole
from margpa_runtime_llm.modules.inference.domain.cancellation import CancellationToken
from margpa_runtime_llm.modules.inference.domain.errors import InferenceErrorCode
from margpa_runtime_llm.modules.runtime_governance.domain import (
    SemanticCriterion,
    SemanticCriterionDisposition,
    SemanticCriterionResult,
    SemanticDeferredReason,
    SemanticEvaluationBudget,
    SemanticEvaluationRequest,
    SemanticEvaluationResponse,
    SemanticProviderState,
)


class SelenePromptManifest(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    schema_version: str = "1"
    provider_id: str = Field(min_length=1)
    template_type: str = Field(min_length=1)
    upstream_repository_url: str = Field(min_length=1)
    upstream_revision: str | None
    template_file: str | None
    template_sha512: str | None = Field(default=None, pattern=r"^[0-9a-f]{128}$")
    derived_template_file: str | None = None
    derived_template_sha512: str | None = Field(default=None, pattern=r"^[0-9a-f]{128}$")
    derived_from_upstream_revision: str | None = None
    derived_from_upstream_basis: str | None = Field(default=None, min_length=1)
    project_contract_digest_sha512: str | None = Field(default=None, pattern=r"^[0-9a-f]{128}$")
    retrieval_status: str = Field(min_length=1)
    verified_official_copy: bool


@dataclass(frozen=True, slots=True)
class SelenePromptUnavailable(Exception):
    reason: str

    def __str__(self) -> str:
        return f"Selene prompt unavailable: {self.reason}"


def load_selene_prompt_manifest(path: Path) -> SelenePromptManifest:
    return SelenePromptManifest.model_validate_json(path.read_text(encoding="utf-8"))


class SelenePromptAdapter:
    _REQUIRED_PLACEHOLDERS = (
        "{{query}}",
        "{{candidate}}",
        "{{dialogue}}",
        "{{reference}}",
        "{{criteria}}",
        "{{response_schema}}",
    )
    _PROJECT_DERIVED_TEMPLATE_TYPE = "project_derived_multi_criterion_v1"

    def __init__(self, *, manifest_path: Path) -> None:
        self._manifest_path = manifest_path
        self._manifest = load_selene_prompt_manifest(manifest_path)

    @property
    def manifest(self) -> SelenePromptManifest:
        return self._manifest

    def preflight_contract(self) -> None:
        """Fail-closed contract check used by dedicated-role preflight."""
        self._validated_template()

    def _derived_contract_digest(self, *, template_sha512: str) -> str:
        payload = {
            "contract_kind": self._PROJECT_DERIVED_TEMPLATE_TYPE,
            "decoder": "judge_output_decoder_v1",
            "required_placeholders": list(self._REQUIRED_PLACEHOLDERS),
            "template_sha512": template_sha512,
        }
        serialized = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        return hashlib.sha512(serialized.encode("utf-8")).hexdigest()

    def _validated_template(self) -> str:
        manifest = self._manifest
        template_file: str | None = None
        expected_digest: str | None = None
        if manifest.verified_official_copy:
            if manifest.upstream_revision is None:
                raise SelenePromptUnavailable("official_upstream_revision_missing")
            template_file = manifest.template_file
            expected_digest = manifest.template_sha512
        elif manifest.template_type == self._PROJECT_DERIVED_TEMPLATE_TYPE:
            template_file = manifest.derived_template_file
            expected_digest = manifest.derived_template_sha512
            if manifest.derived_from_upstream_revision is not None:
                raise SelenePromptUnavailable("unverified_basis_misrepresented_as_revision")
            if manifest.derived_from_upstream_basis is None:
                raise SelenePromptUnavailable("derived_from_basis_missing")
            if manifest.project_contract_digest_sha512 is None:
                raise SelenePromptUnavailable("project_contract_digest_missing")
        else:
            raise SelenePromptUnavailable(manifest.retrieval_status)
        if template_file is None or expected_digest is None:
            raise SelenePromptUnavailable(manifest.retrieval_status)
        template_path = self._manifest_path.parent / template_file
        template = template_path.read_text(encoding="utf-8")
        digest = hashlib.sha512(template.encode("utf-8")).hexdigest()
        if digest != expected_digest:
            raise SelenePromptUnavailable("template_digest_mismatch")
        if any(placeholder not in template for placeholder in self._REQUIRED_PLACEHOLDERS):
            raise SelenePromptUnavailable("template_placeholder_contract_mismatch")
        if not manifest.verified_official_copy:
            assert manifest.project_contract_digest_sha512 is not None
            contract_digest = self._derived_contract_digest(template_sha512=digest)
            if contract_digest != manifest.project_contract_digest_sha512:
                raise SelenePromptUnavailable("project_contract_digest_mismatch")
        return template

    def _criterion_result_example(self) -> dict[str, object]:
        """The one `criterion_results[]` entry example embedded into the
        rendered `{{response_schema}}`. Extracted as its own overridable
        method (R3-WU-04, Controller Review IR-R2-05/IR-R3-04) so a
        Provider-specific subclass (`GemmaPromptAdapter` below) can replace
        just this one example -- never `build()` itself -- without
        affecting any other caller of this shared class (Selene, unchanged
        here)."""
        return {
            "criterion_id": "exact id",
            "disposition": "pass|deviation|unknown",
            "confidence": "0..1",
            # Controller Review (2026-09-05 00:35, IR-R4 §4) bounded
            # local-repair fix: `evidence_refs` (an Array) is deliberately
            # never the LAST field in a criterion entry -- real Gemma 4
            # E2B trials (2/2, `wu03_gemma_repro/run_alt_hypothesis_
            # evidence_refs_reordered.log`) consistently produced valid
            # JSON once `evidence_refs`'s own closing `]` was no longer
            # immediately adjacent to the entry's `}`, `criterion_
            # results`'s `]`, and the outer `}` in one unbroken run of 4
            # closing tokens (the exact shape every prior real trial, 5/5,
            # dropped one token from -- see `phase_9_1_gemma_evidence_
            # refs_json_defect_absolute_log_paths_and_causal_scope_
            # correction_snapshot_ja_20260905001646.md`). Field ORDER only
            # -- `JudgeCriterionResult`'s own required keys/types (still
            # exactly `criterion_id`/`disposition`/`confidence`/`reason_
            # code`/`evidence_refs`) and every real Decoder check are
            # unchanged; JSON object keys are inherently unordered for
            # parsing, so this affects only what order a real Model tends
            # to emit fields in.
            "evidence_refs": ["short reference"],
            "reason_code": "short code",
        }

    def build(
        self,
        *,
        request: SemanticEvaluationRequest,
        criteria: tuple[SemanticCriterion, ...] | None = None,
    ) -> str:
        template = self._validated_template()
        criteria_text = "\n".join(
            (
                f"{item.criterion_id} | {item.evaluation_method.value} | "
                f"{item.instruction} | source={item.source_pointer}"
            )
            for item in (criteria if criteria is not None else request.snapshot.criteria)
        )
        schema = json.dumps(
            {
                "recommendation": "accept|needs_repair|unknown",
                "confidence": "0..1",
                "reasoning": "short string",
                "criterion_results": [self._criterion_result_example()],
            },
            ensure_ascii=False,
            separators=(",", ":"),
        )
        replacements = {
            "{{query}}": request.user_input,
            "{{candidate}}": request.candidate_answer,
            # Gemma Judge-only Constrained Decoding Rework (WU-04): Prior
            # Dialogue Projection -- `request.dialogue_context` was already
            # received here (`SemanticEvaluationRequest.dialogue_context`,
            # populated by `ConversationGenerationSession` with the real
            # prior-Turn history) but never projected into the rendered
            # Prompt at all, so a real Turn's genuine earlier context (e.g.
            # a fact the User established two Turns ago) was invisible to
            # the Judge -- a Prompt Contract gap, not a Model quality
            # defect (see `phase_9_1_gemma_judge_only_constrained_decoding_
            # strategy_decision_ja_20260906111043.md` §3). Rendered into
            # its own `{{dialogue}}` Section, always distinct from `{{
            # reference}}` (Citation Evidence) -- never merged into it,
            # since the two answer different questions (what the
            # conversation already said vs. what independent Evidence
            # supports).
            "{{dialogue}}": "\n".join(request.dialogue_context) or "(none)",
            "{{reference}}": "\n".join(request.evidence_context) or "(none)",
            "{{criteria}}": criteria_text,
            "{{response_schema}}": schema,
        }
        prompt = template
        for placeholder, value in replacements.items():
            prompt = prompt.replace(placeholder, value)
        return prompt


class GemmaPromptAdapter(SelenePromptAdapter):
    """R3-WU-04 (Controller Review IR-R2-05, residual of IR-R4 §4's bounded
    field-reorder fix), superseded for the Criterion Schema itself by
    R4-WU-04 (Controller Review IR-R3-04): Gemma 4 E2B's own confirmed real
    root-cause defect is copying the shared Prompt schema's natural-language
    placeholder text ("short reference"/"short code") into its literal
    output, corrupting `evidence_refs`'s own JSON Array with an illegal
    embedded key. R2's mitigation (an ambiguous placeholder plus a
    disclaiming Rule) and R3-WU-04's own bounded fix (an unambiguous,
    structurally realistic example) both still asked Gemma to PRODUCE
    `evidence_refs`/`reason_code` at all -- R3-WU-05's own real-hardware
    Golden Path Trial confirmed the same class of Malformed JSON defect
    resurfaces specifically when a genuine Deviation forces non-empty
    content into those two fields (R3-WU-04's own 2/2 clean real trials
    never exercised that content shape, only the All-Accept/empty case).

    R4-WU-04 removes the two fields from Gemma's own Criterion Schema
    entirely (Controller Review IR-R3-04: the shared Decoder already
    treats `reason_code`/`evidence_refs` as genuinely OPTIONAL per-criterion
    fields -- see `judge_output_decoder._decode_criterion_results()`'s own
    `.get(...)`/`.get(..., [])` reads, pinned by a dedicated Unit Test
    before this change -- so omitting them from a Provider-local Prompt
    Schema needs no Decoder change at all). `overall reasoning` is
    unaffected; only the per-`criterion_results[]` entry shrinks to the
    three Fields every Criterion's own Disposition genuinely needs. Gemma's
    own template also gains one explicit Rule stating this omission outright
    (see `config/judge_templates/gemma_4_e2b/project_derived_multi_
    criterion_prompt_v1.txt`) -- never the R2 "show an ambiguous
    placeholder, then negate via a Rule" structure Controller Review
    rejected: this Rule states a structural omission from the Schema
    itself, not a disclaimer about literal copying of placeholder prose
    left in the Schema.

    `SelenePromptAdapter.build()` itself, Selene's own shared Schema, the
    Main-shared Prompt, and the common Decoder are all untouched -- this
    class only overrides the one extension point `_criterion_result_
    example()` provides, exactly as before."""

    def _criterion_result_example(self) -> dict[str, object]:
        return {
            "criterion_id": "exact id",
            "disposition": "pass|deviation|unknown",
            "confidence": "0..1",
        }


def build_gemma_judge_structured_output_constraint(
    criterion_ids: tuple[str, ...],
) -> StructuredOutputConstraint:
    """Gemma Judge-only Constrained Decoding Rework (WU-03): the Dynamic
    Judge Schema Factory, decided once per real Batch from that Batch's own
    Expected Criterion set -- never a fixed, pre-computed Schema, since a
    different Batch always needs a different `criterion_results` array
    length.

    Mirrors `GemmaPromptAdapter._criterion_result_example()`'s own Compact
    3-Field shape and the shared Strict Decoder's own top-level contract
    (`judge_output_decoder.py`'s `_ALLOWED_FIELDS`/`_CRITERION_ALLOWED_
    FIELDS`) exactly -- this Factory never invents a shape the Decoder does
    not already expect. `criterion_id` is constrained only to a non-empty
    string, never to the exact expected id set: `llama.cpp`'s JSON-Schema-
    to-Grammar converter has no positional per-array-item `const`/
    `prefixItems` construct to express "item N must be exactly id N" for an
    Array whose Grammar is written once for the whole Array shape (Handoff
    WU-03's own explicit instruction) -- Exact ID membership, duplicates,
    and missing/extra ids stay entirely the Strict Decoder's job
    (`_decode_criterion_results()`), completely unchanged by this Factory.
    `minItems == maxItems == len(criterion_ids)` is the one Batch-size
    guarantee Grammar-level enforcement over the completed Array itself can
    genuinely add on top of that -- the Decoder's own missing/duplicate
    checks would otherwise only fire *after* a truncated or overlong Array
    already achieved syntactically valid JSON."""
    schema: dict[str, object] = {
        "type": "object",
        "properties": {
            "recommendation": {
                "type": "string",
                "enum": ["accept", "needs_repair", "unknown"],
            },
            "confidence": {"type": "number", "minimum": 0.0, "maximum": 1.0},
            "reasoning": {"type": "string"},
            "criterion_results": {
                "type": "array",
                "minItems": len(criterion_ids),
                "maxItems": len(criterion_ids),
                "items": {
                    "type": "object",
                    "properties": {
                        "criterion_id": {"type": "string", "minLength": 1},
                        "disposition": {
                            "type": "string",
                            "enum": ["pass", "deviation", "unknown"],
                        },
                        "confidence": {"type": "number", "minimum": 0.0, "maximum": 1.0},
                    },
                    "required": ["criterion_id", "disposition", "confidence"],
                    "additionalProperties": False,
                },
            },
        },
        "required": ["recommendation", "confidence", "reasoning", "criterion_results"],
        "additionalProperties": False,
    }
    return StructuredOutputConstraint.from_schema(schema)


class SemanticJudgePromptAdapter(Protocol):
    """Structural contract every LLM-backed Judge Prompt Adapter satisfies
    (P9-1 Package 2 Common Substrate fix): `SelenePromptAdapter` already
    matches this shape; `MainSemanticPromptAdapter`
    (`modules/evaluation/application/judge_prompt_builder.py`) is the
    Main-shared counterpart, so `SeleneSemanticEvaluator`'s batching engine
    can be shared by both instead of Main-shared duplicating its own
    unbatched single-call Workaround."""

    def build(
        self,
        *,
        request: SemanticEvaluationRequest,
        criteria: tuple[SemanticCriterion, ...] | None = None,
    ) -> str: ...


@dataclass(frozen=True, slots=True)
class _SeleneBatch:
    criteria: tuple[SemanticCriterion, ...]
    prompt: str
    prompt_tokens: int


@dataclass(frozen=True, slots=True)
class _SeleneBatchGeneration:
    generated: GenerationResult
    parameters: GenerationParameters
    deadline_exceeded: bool


@dataclass(frozen=True, slots=True)
class BatchDispatchEvidence:
    """Gemma Judge-only Constrained Decoding Rework (WU-05): one real Batch
    Call's own Truthful Evidence -- replaces the pre-Rework flat, often-
    hardcoded/placeholder `judge_run_evidence` fields (`call_count=1`
    always, `token_usage=0` always, `seed`/`config_digest_sha512` never
    threaded through, `prompt_digest_sha512` hashing a fixed description
    string instead of any real Prompt) for every dispatch that genuinely
    batches (Selene, Gemma, and the Main-shared semantic-criteria dispatch,
    which all share this one Engine). Carries digests/counts/enums/numbers
    only -- never the raw Prompt or raw Model output text (`raw_output_
    sha512`/`raw_output_byte_length` stand in for the latter, matching this
    Contract's own "Raw全文は通常保存しない" instruction)."""

    batch_index: int
    prompt_digest_sha512: str
    expected_criterion_ids_digest_sha512: str
    expected_criterion_count: int
    parameters: GenerationParameters
    finish_reason: str
    prompt_tokens: int
    completion_tokens: int
    raw_output_byte_length: int
    raw_output_sha512: str
    strict_decode_state: str
    strict_decode_reason: str | None


_MODEL_BUSY_RETRY_DELAYS_SECONDS: tuple[float, ...] = (3.0, 6.0, 12.0)
"""P9-1 Judge Dispatch "unavailable" Round 3 fix: bounded retry for a
*genuine* `InferenceError(code=MODEL_BUSY)` from `_generate_batch()`'s real
`generate()` call — "Open Finding 6" from the Round 1 Self-review's real
end-to-end re-verification. A prior Turn's `run_tracked_stage()`-orphaned
background generate() Thread on this same dedicated Adapter can still
genuinely be running when this Turn's own attempt starts; before this fix,
that collision failed instantly and permanently for this Turn. Retrying a
few times, spaced out, lets this Turn's own call succeed once that orphaned
generation naturally finishes, instead of instantly failing every single
time this collision occurs.

Round 4 Self-review correction (evidentiary accuracy — flagged as High
importance by an independent docs-consistency audit): earlier drafts of
this docstring cited "Gemma ~1.7s, Selene ~14.2s" as real-hardware
orphan-*clearing* observations. That attribution was wrong: both figures
were actually the *total latency of unrelated, successful (non-orphaned)*
`generate()` calls in earlier diagnostics — not measurements of how long an
abandoned background Thread takes to naturally finish. The only genuine
measurement of that specific quantity in this project's evidence chain is
`waited_s=0.854` (~0.85s), from the original Root Cause investigation's
real Main+Gemma concurrent-load reproduction (`history/operations/phase_9_
1_judge_dispatch_unavailable_failure_root_cause_confirmed_three_angle_
investigation_ja_20260903132314.md`). Separately, both Round 3's and
Round 4's own real-hardware re-verifications (dedicated Gemma path and
Main-shared path respectively) empirically confirmed this retry mechanism
bridges a real collision successfully after exactly the *first* retry (the
3.0s delay) in every run observed so far — none has yet required the 6.0s
or 12.0s tiers.

Bounded to a small, fixed count (User-specified: "念のため3回まで" — cap
the retry count so this can never become an unbounded/"謎のLoop", not to
guarantee outlasting every possible orphan duration) — worst-case added
latency across these 3 delays is ~21.0s, a deliberately large margin over
the only genuine orphan-clear measurement available (0.85s) precisely
because that sample size is small (one clean data point) and the margin
costs nothing in the common case (every real collision observed so far has
cleared on the first, 3.0s, retry). Still small and fixed relative to the
real ENFORCE pipeline's own overall wait budget (~430s for the Local macOS
Selene/Gemma profiles, see `stage_budget.py`), and every wait uses
`cancellation.wait(timeout=...)` — never a plain `time.sleep()` — so a
Main-priority preemption (or any other Cancellation) still interrupts a
retry wait immediately rather than after the full delay, matching this
codebase's established interruptible-wait idiom elsewhere (e.g.
`judge_live_integration.py`'s own ENFORCE wait loop). Retries ONLY on a
genuine `MODEL_BUSY`; any other failure (including a real Timeout/
Cancellation) is never retried here and propagates exactly as before. If
real usage shows 3 retries insufficient or excessive, this tuple is the
single place to retune — no other code depends on its length or values,
and `test_model_busy_retry_window_covers_the_largest_documented_real_
hardware_orphan` (test_selene_adapter.py) will fail loudly if a future
edit shrinks the total below its own honestly-justified floor, so the two
can never silently drift apart again."""


def _diagnostic_exception_detail(exc: Exception) -> str:
    """P9-1 Judge Dispatch "unavailable" Root Cause Fix, Round 1 Self-review
    finding: every generic `except Exception` below collapses into the same
    `"{label}_unavailable:{ExceptionType}"` shape regardless of *why* the
    exception was raised — this was the exact mechanism that made the fixed
    spurious `count_chat_prompt_tokens()` lock contention (now removed, see
    `LlamaCppModelAdapter`) indistinguishable, without a live monkeypatch,
    from every other cause. Real end-to-end re-verification after that fix
    confirmed a second, legitimate cause reaches this same generic bucket
    through the same shape: a genuine `InferenceError(code=MODEL_BUSY)` from
    `generate()`'s own (correct, unchanged) exclusivity check, when a prior
    Turn's `run_tracked_stage()`-orphaned background Thread on this same
    dedicated Adapter is still genuinely generating (Round 3 now retries
    this specific case a bounded number of times before giving up — see
    `_MODEL_BUSY_RETRY_DELAYS_SECONDS` — so this generic collapse is now the
    *exhausted-retry* tail of that case, not its only outcome). Duck-typed
    (uses `getattr` rather than an `isinstance` check, so it stays generic
    across any exception shape) — appends the exception's `.code` when
    present, so the persisted `failure_reason` string alone (already
    captured in every Evidence record) can distinguish these causes without
    needing a fresh reproduction each time. Does not change
    `JudgeFailureReason` classification (`judge_live_integration.py`'s
    prefix-matching is unaffected) — display-category collapse is unchanged;
    only the raw diagnostic string is enriched.

    P9-1 Judge/Governance Rework (WU-01): also appends `.details`, when
    present, to the raw string. Real-hardware re-verification found this
    genuinely necessary, not merely nice-to-have: `InferenceErrorCode.
    GENERATION_FAILED` is raised by two structurally different paths that
    otherwise collapse to the exact same `.code` -- `LlamaCppModelAdapter.
    generate()`'s own Pathological Repetition Detector
    (`details={"reason": "pathological_repetition_detected"}`) and
    `raise_mapped_backend_error()`'s generic fallback for *any other*
    native exception (`details={"operation": ..., "exception_type": ...}`)
    -- and a real Main+Selene concurrent-Load reproduction confirmed a
    genuine native `RuntimeError: llama_decode returned -3` (a Metal
    Compute Graph resource conflict between two concurrently-loaded
    llama.cpp contexts, empirically bounded to Selene's own `gpu_layers`
    count -- reproduced 3/3 at the default `-1`/full-offload, absent at
    `gpu_layers<=1`, but `gpu_layers<=1` alone was independently confirmed
    too slow for the real 32-Criteria Batch shape to complete inside this
    deployment's own inference budget, so it is not adopted as a fix here)
    reaches this exact same generic fallback bucket, genuinely
    indistinguishable from a Pathological Repetition detection by `.code`
    alone. Sorted for deterministic key ordering."""
    code = getattr(exc, "code", None)
    if code is None:
        return type(exc).__name__
    detail = f"{type(exc).__name__}:{code}"
    raw_details = getattr(exc, "details", None)
    if isinstance(raw_details, dict) and raw_details:
        rendered = ",".join(f"{key}={value}" for key, value in sorted(raw_details.items()))
        detail = f"{detail}:{rendered}"
    return detail


_REASON_CODE_MAX_LENGTH = 64
_REASON_CODE_INVALID_CHARS = re.compile(r"[^A-Za-z0-9._:-]")


def _sanitize_reason_code(raw: str | None) -> str | None:
    """P9-1 Judge Dispatch Fix Round 6 (Finding 2, Mechanism A):
    `SemanticCriterionResult.reason_code` requires `_IDENTIFIER_PATTERN`
    (`^[A-Za-z0-9][A-Za-z0-9._:-]{0,191}$`, `max_length=64`) — a strict
    slug shape. The Judge Prompt schema (`SelenePromptAdapter.build()`'s
    `response_schema`) only asks for `"reason_code": "short code"`, with
    no format constraint communicated to the Model, so a real Judge
    legitimately writes natural-language text (e.g. `'insufficient
    evidence'`) instead of a slug. Self-review correction: the real-hardware
    measurement (~8.8% of 136 decoded reason_codes) is from Qwen/DeepSeek
    Main-shared dispatch reproductions specifically (Round A/3-angle
    investigation, Agent 3) — Gemma 4 E2B itself was not directly sampled
    for this metric, but is considered the likely (not independently
    confirmed) explanation for its own consistently-observed 5-for-5
    failure pattern, since Gemma dispatches through this exact shared
    engine (Provider-neutral, not a Gemma-specific code path). Before this
    fix, that raw text reached `SemanticCriterionResult` unsanitized and
    raised an uncaught Pydantic ValidationError, escaping this evaluator
    entirely as `unhandled_error:ValidationError`. Sanitizing once, here,
    at the shared construction site fixes every caller uniformly rather
    than special-casing any one Model's prompt/output quirks: invalid
    characters become `_`, a non-alnum leading character gets a safe `r`
    prefix (the pattern requires the first character to be alnum), and
    the result is capped to the field's own 64-character limit. Returns
    `None` unchanged only when `raw` is already empty (the field is
    optional) — a non-empty input is never turned into an empty string
    (which would itself violate `_IDENTIFIER_PATTERN`'s `[A-Za-z0-9]`
    first-character requirement) even when every one of its characters
    falls outside the allowed set: e.g. `'!!!'` becomes the safe non-empty
    slug `'r___'`, not `None`."""
    if raw is None:
        return None
    cleaned = _REASON_CODE_INVALID_CHARS.sub("_", raw)
    if not cleaned:
        return None
    if not cleaned[0].isalnum():
        cleaned = f"r{cleaned}"
    return cleaned[:_REASON_CODE_MAX_LENGTH]


def _sanitize_evidence_refs(raw: tuple[str, ...]) -> tuple[str, ...]:
    """P9-1 Judge Dispatch Fix Round 6 Self-review correction (Round 4,
    Finding 2 from an independent adversarial-input audit): unlike
    `reason_code`, `evidence_refs` reached `SemanticCriterionResult`
    completely unsanitized — `SemanticCriterion.evidence_refs` (`semantic_
    criteria.py`) constrains only element count (`max_length=32`), not
    character content. A Judge-supplied string containing an unpaired
    Unicode surrogate (`'\\ud800'` — syntactically legal inside a JSON
    string, so `json.loads()` accepts it without complaint) survives
    Pydantic construction untouched, then crashes
    `semantic_contract_digest()` (`semantic_criteria.py`, `json.dumps(...,
    ensure_ascii=False).encode('utf-8')`) with an uncaught
    `UnicodeEncodeError` — reached from `SemanticRuntimeCoordinator.
    record_response()`'s `evidence_digest_sha512=semantic_contract_
    digest(payload)` (`semantic_runtime.py`), crashing the whole Judge
    Evidence recording path. `encode('utf-8', errors='replace')` swaps any
    unencodable code point for `?` (Python's documented `'replace'`
    encoding-error substitute) rather than raising, so every
    `evidence_refs` string is guaranteed safe to UTF-8-encode downstream;
    the subsequent `.decode('utf-8')` back to `str` is always safe once
    the surrogate is gone, and ordinary, well-formed text is left
    unaltered."""
    return tuple(item.encode("utf-8", errors="replace").decode("utf-8") for item in raw)


_FAILURE_REASON_MAX_LENGTH = 128


def _truncate_failure_reason(raw: str | None) -> str | None:
    """P9-1 Judge Dispatch Fix Round 6 (Finding 2, Mechanism B):
    `SemanticEvaluationResponse.failure_reason` has `max_length=128`.
    Several construction sites in this module build this string by
    interpolating an upstream exception/decode-error's own free-text
    `.reason`/`str(exc)` (e.g. `f"malformed_output:{exc.reason}"`,
    `f"{label}_unavailable:{_diagnostic_exception_detail(exc)}"`), which
    is not itself length-bounded. When that interpolated text pushes the
    combined string past 128 characters, constructing
    `SemanticEvaluationResponse` itself raised a *second*, masking
    Pydantic ValidationError — silently destroying the original,
    correctly-classified failure diagnosis (e.g. a genuine
    `malformed_output` became an opaque `unhandled_error:ValidationError`
    instead). Truncating once, here, at `response()`'s single
    construction site guards every failure_reason string this evaluator
    ever builds, regardless of which branch built it."""
    if raw is None:
        return None
    return raw[:_FAILURE_REASON_MAX_LENGTH]


class SeleneSemanticEvaluator:
    """Token-bounded, batched LLM-as-a-Judge Semantic Evaluator.

    Despite the name (kept for Selene's own established call sites and
    Fixture-tested history), this engine is provider-neutral: it depends
    only on an `InferenceService`, a `SemanticJudgePromptAdapter` and a
    `model_key` — nothing Selene-specific. P9-1 Package 2 reuses it
    unchanged for the Main-shared Judge's semantic-criteria dispatch (see
    `bootstrap/judge_live_integration.py`'s `MainSemanticPromptAdapter`
    branch) so both providers share one Prompt Build/Batching/Decode
    implementation instead of Main-shared repeating the same Workaround
    Selene already solved (P9-1 Package 2 Handoff §4 WU-02: "共通Failureは
    共通層で一度だけ直す。Provider固有Adapterへ同じWorkaroundを複製しない。").
    `provider_label` only affects diagnostic `failure_reason` string
    prefixes (e.g. `"selene_unavailable:..."` vs `"main_shared_unavailable:
    ..."`) — a genuine Strict-Decode `malformed_output` failure is always
    labeled `"malformed_output:..."` regardless of `provider_label`, so a
    truncated/invalid JSON response is never miscategorized as a
    Provider-unavailable failure for any caller of this engine.
    """

    def __init__(
        self,
        *,
        service: InferenceService,
        model_key: str,
        prompt_adapter: SemanticJudgePromptAdapter,
        max_new_tokens: int = 1000,
        max_criteria_per_call: int = 8,
        max_calls: int = 4,
        max_prompt_tokens_per_call: int = 4096,
        cancel_grace_ms: int = LOCAL_MACOS_SELENE_JUDGE_BUDGET.cancel_grace_ms,
        tracked_stage_registry: TrackedStageWorkerRegistry | None = None,
        provider_label: str = "selene",
        sampling_overrides: Mapping[str, object] | None = None,
        structured_output_schema_factory: (
            Callable[[tuple[str, ...]], StructuredOutputConstraint] | None
        ) = None,
    ) -> None:
        self._service = service
        self._model_key = model_key
        self._prompt_adapter = prompt_adapter
        self._max_new_tokens = max(1, max_new_tokens)
        self._max_criteria_per_call = max(1, max_criteria_per_call)
        self._max_calls = max(0, max_calls)
        self._max_prompt_tokens_per_call = max(0, max_prompt_tokens_per_call)
        self._cancel_grace_ms = max(0, cancel_grace_ms)
        self._tracked_stage_registry = tracked_stage_registry
        self._provider_label = provider_label
        # R2-WU-04: an explicit, Role/Provider-specific Generation Sampling
        # Contract, injected by the Composition Root only for the specific
        # Role that needs it (Gemma Judge, so far) -- `None` (every other
        # caller: Selene, Main-shared) leaves `GenerationParameters`'s own
        # library defaults completely unchanged, never a blanket override
        # to this shared, provider-neutral engine.
        self._sampling_overrides: dict[str, object] = (
            dict(sampling_overrides) if sampling_overrides is not None else {}
        )
        # Gemma Judge-only Constrained Decoding Rework (WU-03): `None` for
        # every existing caller (Selene, Main-shared) leaves every Request
        # this engine builds completely unconstrained, exactly as before --
        # only `ProductionRoleAdapterFactory`'s own Gemma branch supplies a
        # real Factory (mirrors `sampling_overrides`'s own established
        # Composition-Root-decides pattern exactly).
        self._structured_output_schema_factory = structured_output_schema_factory

    @property
    def inference_service(self) -> InferenceService:
        """The loaded dedicated service, retained for frozen repair rejudge."""
        return self._service

    @property
    def sampling_overrides(self) -> Mapping[str, object]:
        """Gemma Constrained Decoding Final Contract Micro Rework (IR-FC-01):
        exposed so the identical, Provider-local frozen Sampling contract
        this Evaluator's own initial-Judge Batches use (e.g. Gemma's own
        `GEMMA_JUDGE_DETERMINISTIC_SAMPLING`) can also be threaded,
        unchanged, into `attempt_live_repair()`'s own Rejudge Call --
        mirrors `structured_output_schema_factory`'s own established
        Composition-Root-decides pattern exactly. An empty mapping (Selene,
        Main-shared -- every caller that never supplied `sampling_
        overrides` at construction) means "apply nothing", leaving a
        Rejudge routed through a Selene/Main-shared Evaluator exactly as
        unpinned as before this fix."""
        return dict(self._sampling_overrides)

    @property
    def structured_output_schema_factory(
        self,
    ) -> Callable[[tuple[str, ...]], StructuredOutputConstraint] | None:
        """WU-03/WU-04 wiring: exposed so the identical Factory this
        Evaluator's own Batches use for the initial Judge dispatch can also
        be threaded, unchanged, into `attempt_live_repair()`'s own Rejudge
        Call -- `None` for every caller except the real Gemma-configured
        instance, so a Rejudge routed through a Selene/Main-shared Evaluator
        never receives a Constraint either."""
        return self._structured_output_schema_factory

    @property
    def config_digest_sha512(self) -> str:
        """WU-05: a genuine digest of this Evaluator's own real Batch/
        Sampling contract (Provider label, Batch sizing, Sampling
        Overrides, whether Structured Output is enabled at all) -- computed
        once from this instance's own configuration, never the fixed
        single-call `_LIVE_JUDGE_CONFIG_DIGEST_SHA512` constant
        (`judge_live_integration.py`) that in fact describes a completely
        different, unbatched dispatch shape."""
        payload = {
            "role": "judge",
            "provider_label": self._provider_label,
            "max_new_tokens": self._max_new_tokens,
            "max_criteria_per_call": self._max_criteria_per_call,
            "max_calls": self._max_calls,
            "max_prompt_tokens_per_call": self._max_prompt_tokens_per_call,
            "sampling_overrides": {
                key: self._sampling_overrides[key] for key in sorted(self._sampling_overrides)
            },
            "structured_output_enabled": self._structured_output_schema_factory is not None,
        }
        serialized = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        return hashlib.sha512(serialized.encode("utf-8")).hexdigest()

    def evaluate(
        self,
        *,
        request: SemanticEvaluationRequest,
        cancellation: CancellationToken | None = None,
        inference_budget_ms: int = LOCAL_MACOS_SELENE_JUDGE_BUDGET.inference_budget_ms,
        late_worker_observer: Callable[[Future[object]], None] | None = None,
        batch_evidence_observer: Callable[[BatchDispatchEvidence], None] | None = None,
    ) -> SemanticEvaluationResponse:
        """WU-05: `batch_evidence_observer`, when supplied, is invoked once
        per real Batch Call that actually reached the Model (never for a
        Batch that failed before or during dispatch itself, e.g. a genuine
        Cancellation/Deadline/Unavailable) -- mirrors `late_worker_
        observer`'s own established per-call, Optional, `None`-by-default
        shape exactly. `None` (every pre-Rework caller) collects nothing,
        identical to before this field existed."""
        started = time.monotonic()
        calls_started = 0
        calls_completed = 0
        completion_tokens = 0
        prompt_tokens_by_call: list[int] = []
        deferred: list[SemanticCriterionResult] = []

        def budget(
            *,
            deadline_exceeded: bool = False,
            cancelled: bool = False,
        ) -> SemanticEvaluationBudget:
            return SemanticEvaluationBudget(
                max_criteria_per_call=self._max_criteria_per_call,
                max_calls=self._max_calls,
                max_prompt_tokens_per_call=self._effective_max_prompt_tokens(),
                max_output_tokens_per_call=self._max_new_tokens,
                context_limit_tokens=self._context_limit_tokens(),
                inference_deadline_ms=max(0, inference_budget_ms),
                calls_started=calls_started,
                calls_completed=calls_completed,
                prompt_tokens_by_call=tuple(prompt_tokens_by_call),
                completion_tokens=completion_tokens,
                budget_deferred_criteria=len(deferred),
                deadline_exceeded=deadline_exceeded,
                cancelled=cancelled,
            )

        def response(
            *,
            provider_state: SemanticProviderState,
            results: tuple[SemanticCriterionResult, ...] = (),
            failure_reason: str | None = None,
            deadline_exceeded: bool = False,
            cancelled: bool = False,
        ) -> SemanticEvaluationResponse:
            return SemanticEvaluationResponse(
                request_id=request.snapshot.request_id,
                generation=request.snapshot.generation,
                provider_id=self._model_key,
                provider_state=provider_state,
                results=results,
                latency_ms=max(0, int((time.monotonic() - started) * 1000)),
                failure_reason=_truncate_failure_reason(failure_reason),
                budget=budget(
                    deadline_exceeded=deadline_exceeded,
                    cancelled=cancelled,
                ),
            )

        if cancellation is not None and cancellation.is_cancelled():
            return response(
                provider_state=SemanticProviderState.FAILED,
                failure_reason=f"{self._provider_label}_cancelled",
                cancelled=True,
            )
        try:
            batches, deferred = self._plan_batches(request=request)
        except Exception as exc:
            return response(
                provider_state=SemanticProviderState.UNAVAILABLE,
                failure_reason=(
                    f"{self._provider_label}_unavailable:{_diagnostic_exception_detail(exc)}"
                ),
            )
        results: list[SemanticCriterionResult] = []
        for batch_index, batch in enumerate(batches, start=1):
            if cancellation is not None and cancellation.is_cancelled():
                return response(
                    provider_state=SemanticProviderState.FAILED,
                    failure_reason=f"{self._provider_label}_cancelled",
                    cancelled=True,
                )
            call_cancellation = CancellationToken.linked_to(cancellation)
            calls_started += 1
            prompt_tokens_by_call.append(batch.prompt_tokens)

            def generate_batch(
                batch_index: int = batch_index,
                batch: _SeleneBatch = batch,
                call_cancellation: CancellationToken = call_cancellation,
            ) -> _SeleneBatchGeneration:
                return self._generate_batch(
                    request_id=f"{request.snapshot.request_id}:{self._provider_label}:{batch_index}",
                    prompt=batch.prompt,
                    criterion_ids=tuple(item.criterion_id for item in batch.criteria),
                    cancellation=call_cancellation,
                    inference_budget_ms=max(0, inference_budget_ms),
                )

            try:
                stage_outcome = run_tracked_stage(
                    work=generate_batch,
                    budget_ms=max(0, inference_budget_ms) + self._cancel_grace_ms,
                    registry=self._tracked_stage_registry,
                    cancellation=call_cancellation,
                )
            except Exception as exc:
                if cancellation is not None and cancellation.is_cancelled():
                    return response(
                        provider_state=SemanticProviderState.FAILED,
                        failure_reason=f"{self._provider_label}_cancelled",
                        cancelled=True,
                    )
                return response(
                    provider_state=SemanticProviderState.UNAVAILABLE,
                    failure_reason=(
                        f"{self._provider_label}_unavailable:{_diagnostic_exception_detail(exc)}"
                    ),
                )
            if stage_outcome.timed_out or stage_outcome.result is None:
                call_cancellation.cancel()
                if late_worker_observer is not None:
                    late_worker_observer(cast(Future[object], stage_outcome.future))
                if cancellation is not None and cancellation.is_cancelled():
                    return response(
                        provider_state=SemanticProviderState.FAILED,
                        failure_reason=f"{self._provider_label}_cancelled",
                        cancelled=True,
                    )
                return response(
                    provider_state=SemanticProviderState.FAILED,
                    failure_reason=f"{self._provider_label}_inference_deadline_exceeded",
                    deadline_exceeded=True,
                )
            calls_completed += 1
            generated = stage_outcome.result.generated
            if cancellation is not None and cancellation.is_cancelled():
                return response(
                    provider_state=SemanticProviderState.FAILED,
                    failure_reason=f"{self._provider_label}_cancelled",
                    cancelled=True,
                )
            if stage_outcome.result.deadline_exceeded:
                return response(
                    provider_state=SemanticProviderState.FAILED,
                    failure_reason=f"{self._provider_label}_inference_deadline_exceeded",
                    deadline_exceeded=True,
                )
            if generated.finish_reason is FinishReason.CANCELLED:
                return response(
                    provider_state=SemanticProviderState.FAILED,
                    failure_reason=f"{self._provider_label}_generation_cancelled",
                    cancelled=True,
                )
            completion_tokens += (
                generated.usage.completion_tokens if generated.usage is not None else 0
            )
            batch_parameters = stage_outcome.result.parameters

            def _emit_batch_evidence(
                *,
                strict_decode_state: str,
                strict_decode_reason: str | None,
                batch_index: int = batch_index,
                batch: _SeleneBatch = batch,
                generated: GenerationResult = generated,
                batch_parameters: GenerationParameters = batch_parameters,
            ) -> None:
                if batch_evidence_observer is None:
                    return
                raw_bytes = generated.content.encode("utf-8")
                expected_ids_serialized = json.dumps(
                    sorted(item.criterion_id for item in batch.criteria)
                )
                batch_evidence_observer(
                    BatchDispatchEvidence(
                        batch_index=batch_index,
                        prompt_digest_sha512=hashlib.sha512(
                            batch.prompt.encode("utf-8")
                        ).hexdigest(),
                        expected_criterion_ids_digest_sha512=hashlib.sha512(
                            expected_ids_serialized.encode("utf-8")
                        ).hexdigest(),
                        expected_criterion_count=len(batch.criteria),
                        parameters=batch_parameters,
                        finish_reason=generated.finish_reason.value,
                        prompt_tokens=(
                            generated.usage.prompt_tokens if generated.usage is not None else 0
                        ),
                        completion_tokens=(
                            generated.usage.completion_tokens
                            if generated.usage is not None
                            else 0
                        ),
                        raw_output_byte_length=len(raw_bytes),
                        raw_output_sha512=hashlib.sha512(raw_bytes).hexdigest(),
                        strict_decode_state=strict_decode_state,
                        strict_decode_reason=strict_decode_reason,
                    )
                )

            try:
                decoded = decode_judge_output(
                    raw_text=generated.content,
                    judge_role=JudgeIndependenceClass.INDEPENDENT_ARTIFACT,
                    token_usage=(
                        generated.usage.completion_tokens if generated.usage is not None else 0
                    ),
                    latency_ms=max(0, int((time.monotonic() - started) * 1000)),
                    expected_criterion_ids=tuple(item.criterion_id for item in batch.criteria),
                )
            except JudgeDecodeError as exc:
                _emit_batch_evidence(
                    strict_decode_state="malformed", strict_decode_reason=exc.reason
                )
                # P9-1 Package 2 Common Substrate fix: a Strict-Decode
                # rejection means the model *did* respond, but its output
                # could not be parsed against the expected schema — the
                # same failure category `decode_judge_output_fail_closed`
                # already labels `JudgeFailureReason.MALFORMED_OUTPUT` for
                # the Main-shared dispatch path (`judge_output_decoder.py`).
                # Previously this branch collapsed into the generic
                # `{provider_label}_unavailable` bucket below, indistinguishable
                # from a genuine adapter/infrastructure failure — see
                # `_judge_response_from_semantic_results()` in
                # `bootstrap/judge_live_integration.py`, which now inspects
                # this exact `"malformed_output:"` prefix to pick the correct
                # `JudgeFailureReason`, uniformly across every LLM-backed
                # Judge provider that uses this engine.
                return response(
                    provider_state=SemanticProviderState.FAILED,
                    failure_reason=f"malformed_output:{exc.reason}",
                )
            except Exception as exc:
                return response(
                    provider_state=SemanticProviderState.UNAVAILABLE,
                    failure_reason=(
                        f"{self._provider_label}_unavailable:{_diagnostic_exception_detail(exc)}"
                    ),
                )
            _emit_batch_evidence(strict_decode_state="decoded", strict_decode_reason=None)
            if cancellation is not None and cancellation.is_cancelled():
                return response(
                    provider_state=SemanticProviderState.FAILED,
                    failure_reason=f"{self._provider_label}_cancelled",
                    cancelled=True,
                )
            criteria_by_id = {item.criterion_id: item for item in batch.criteria}
            results.extend(
                SemanticCriterionResult(
                    criterion_id=item.criterion_id,
                    descriptor_id=criteria_by_id[item.criterion_id].descriptor_id,
                    disposition={
                        JudgeCriterionDisposition.PASS: SemanticCriterionDisposition.PASS,
                        JudgeCriterionDisposition.DEVIATION: SemanticCriterionDisposition.DEVIATION,
                        JudgeCriterionDisposition.UNKNOWN: SemanticCriterionDisposition.UNKNOWN,
                    }[item.disposition],
                    confidence=item.confidence,
                    reason_code=_sanitize_reason_code(item.reason_code),
                    evidence_refs=_sanitize_evidence_refs(item.evidence_refs),
                )
                for item in decoded.criterion_results
            )
        return response(
            provider_state=SemanticProviderState.ACTIVE,
            results=tuple((*results, *deferred)),
        )

    def _context_limit_tokens(self) -> int | None:
        runtime_info = self._service.runtime_info
        return runtime_info.loaded_context_size if runtime_info is not None else None

    def _effective_max_prompt_tokens(self) -> int:
        context_limit = self._context_limit_tokens()
        if context_limit is None:
            return self._max_prompt_tokens_per_call
        return min(
            self._max_prompt_tokens_per_call,
            max(0, context_limit - self._max_new_tokens),
        )

    def _plan_batches(
        self,
        *,
        request: SemanticEvaluationRequest,
    ) -> tuple[tuple[_SeleneBatch, ...], list[SemanticCriterionResult]]:
        criteria = request.snapshot.criteria
        max_prompt_tokens = self._effective_max_prompt_tokens()
        batches: list[_SeleneBatch] = []
        deferred: list[SemanticCriterionResult] = []
        index = 0
        while index < len(criteria):
            if len(batches) >= self._max_calls:
                deferred.extend(self._deferred_results(criteria[index:]))
                break
            batch_criteria: list[SemanticCriterion] = []
            batch_prompt = ""
            batch_prompt_tokens = 0
            while index < len(criteria) and len(batch_criteria) < self._max_criteria_per_call:
                candidate = (*batch_criteria, criteria[index])
                prompt = self._prompt_adapter.build(request=request, criteria=candidate)
                prompt_tokens = self._service.count_chat_prompt_tokens(
                    (ChatMessage(role=MessageRole.USER, content=prompt),),
                    ThinkingMode.DISABLED,
                )
                if prompt_tokens > max_prompt_tokens:
                    if batch_criteria:
                        break
                    deferred.extend(self._deferred_results((criteria[index],)))
                    index += 1
                    continue
                batch_criteria = list(candidate)
                batch_prompt = prompt
                batch_prompt_tokens = prompt_tokens
                index += 1
            if batch_criteria:
                batches.append(
                    _SeleneBatch(
                        criteria=tuple(batch_criteria),
                        prompt=batch_prompt,
                        prompt_tokens=batch_prompt_tokens,
                    )
                )
        return tuple(batches), deferred

    @staticmethod
    def _deferred_results(
        criteria: tuple[SemanticCriterion, ...],
    ) -> tuple[SemanticCriterionResult, ...]:
        return tuple(
            SemanticCriterionResult(
                criterion_id=item.criterion_id,
                descriptor_id=item.descriptor_id,
                disposition=SemanticCriterionDisposition.DEFERRED,
                reason_code=SemanticDeferredReason.BUDGET_EXHAUSTED.value,
            )
            for item in criteria
        )

    def _generate_batch(
        self,
        *,
        request_id: str,
        prompt: str,
        criterion_ids: tuple[str, ...],
        cancellation: CancellationToken,
        inference_budget_ms: int,
    ) -> _SeleneBatchGeneration:
        with stage_deadline(
            cancellation=cancellation,
            budget_ms=inference_budget_ms,
        ) as deadline_exceeded:
            generated, parameters = self._generate_with_busy_retry(
                request_id=request_id,
                prompt=prompt,
                criterion_ids=criterion_ids,
                cancellation=cancellation,
            )
        return _SeleneBatchGeneration(
            generated=generated,
            parameters=parameters,
            deadline_exceeded=deadline_exceeded(),
        )

    def _generate_with_busy_retry(
        self,
        *,
        request_id: str,
        prompt: str,
        criterion_ids: tuple[str, ...],
        cancellation: CancellationToken,
    ) -> tuple[GenerationResult, GenerationParameters]:
        """See `_MODEL_BUSY_RETRY_DELAYS_SECONDS`'s module-level docstring
        for the full rationale. Only a genuine `InferenceError(code=
        MODEL_BUSY)` is retried, bounded by that fixed delay sequence;
        anything else (including a real Timeout/Cancellation, or `MODEL_BUSY`
        with no delays left) propagates immediately, unretried, exactly as
        before this fix. Waits via `cancellation.wait(timeout=...)` (Round 3
        Self-review finding), never a plain `time.sleep()` — a plain sleep
        cannot be woken early by a concurrent Cancellation (e.g. Main-priority
        preemption arriving mid-retry), silently adding up to this delay's
        full duration to this codebase's otherwise-immediate cancellation
        responsiveness contract; `wait()` returns `True` the instant
        Cancellation fires, so a retry loop that gets cancelled mid-wait
        re-raises immediately instead of first finishing its sleep and only
        then re-attempting a `generate()` call nobody wants anymore.

        Gemma Judge-only Constrained Decoding Rework (WU-03): `structured_
        output` is attached to this Batch's own `GenerationParameters` only
        when `self._structured_output_schema_factory` is not `None` (only
        the real Gemma-configured instance) -- built fresh from THIS
        Batch's own `criterion_ids`, since a different Batch always needs a
        differently-sized `criterion_results` Array. Returns the exact
        `GenerationParameters` used, so the caller can record genuinely
        accurate per-Batch Evidence (WU-05) instead of assuming what was
        sent."""
        updates: dict[str, object] = dict(self._sampling_overrides)
        if self._structured_output_schema_factory is not None:
            updates["structured_output"] = self._structured_output_schema_factory(criterion_ids)
        parameters = GenerationParameters(max_new_tokens=self._max_new_tokens).model_copy(
            update=updates
        )
        request = GenerationRequest(
            request_id=request_id,
            model_key=self._model_key,
            messages=(ChatMessage(role=MessageRole.USER, content=prompt),),
            parameters=parameters,
        )
        remaining_delays = list(_MODEL_BUSY_RETRY_DELAYS_SECONDS)
        while True:
            try:
                return self._service.generate(request, cancellation=cancellation), parameters
            except Exception as exc:
                if (
                    getattr(exc, "code", None) is not InferenceErrorCode.MODEL_BUSY
                    or not remaining_delays
                ):
                    raise
                if cancellation.wait(timeout=remaining_delays.pop(0)):
                    raise
