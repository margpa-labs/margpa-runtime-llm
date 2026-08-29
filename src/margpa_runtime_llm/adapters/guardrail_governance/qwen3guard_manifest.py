"""Qwen3Guard Official Output Contract Manifest (P6-RR-R23, Post-Codex
Independent Review Rework, resolves P6-CODEX-087).

Mirrors `adapters/evaluation/selene.py`'s `SelenePromptManifest` pattern:
a checked-in, fail-closed Manifest is the single source of truth for
Qwen3Guard's official Line Protocol and Category Set, never a bare
externally-injected `bool`. Without a genuinely verified and complete
Manifest, real `classify_point()` calls are unavailable — Tests may
provide an explicit verified fixture Manifest to exercise the Adapter
contract without mislabelling a remembered/guessed contract as official.

Two independent official Sources back this Manifest (P6-GOV-023 §5 cites
both as required corroboration for this Package's Read-only Network
Authority):

- Qwen's own Hugging Face Model Repository (`Qwen/Qwen3Guard-Gen-0.6B`),
  specifically its `tokenizer_config.json` `chat_template` — the exact
  Line Protocol instructions ("The first line must be one of: 'Safety:
  Safe', ...", "The second line should start with 'Categories:' ... If
  the content is safe, use 'Categories: None'.", and, for the Assistant/
  Output-Candidate branch only, "The third line must be one of: 'Refusal:
  Yes', 'Refusal: No'.") and the exact per-branch Category lists are
  embedded directly in this template's own text.
- The QwenLM GitHub Repository (`QwenLM/Qwen3Guard`)'s README, which
  documents the same 9 Category labels in prose and explicitly marks one
  of them Input-only: "**Jailbreak (Only for input):** Content that
  explicitly attempts to override the model's system prompt or model
  conditioning." — corroborating, independently of the HF chat_template's
  own two distinct Category lists, that `Jailbreak` is never a valid
  Output Candidate label.

Both Sources' exact commit-level Revision and a SHA-512 of the exact
fetched content are recorded on `Qwen3GuardManifest` — never a mutable
`main` branch name asserted as an Exact Revision.

P6-RR-R27 (Post-Codex Independent Review Rework, resolves P6-CODEX-090):
`is_complete_and_verified` alone (a bare `verified_official_contract`
Boolean plus a handful of non-empty/non-None field presence checks) was
never enough — Controller Probe C constructed a Manifest with `provider_
id="wrong.provider"`, `input_context_required_fields=("Wrong",)`, and
`input_context_categories=("FakeInput",)` and still observed `is_
complete_and_verified=True`, because none of those specific *values* were
ever checked against the real official Contract, only their mere
presence. `_validate_exact_official_contract` (a Pydantic `model_
validator`) now rejects Construction itself — before this Manifest object
even exists — whenever `verified_official_contract=True` is paired with
any field that does not match this module's own `_EXPECTED_*` constants
(fixed from this Project's own R23 fetch of Qwen's official Sources,
network access being prohibited for this Package; see `config/guardrail/
qwen3guard/manifest.json` for the live values these constants must
match). A Manifest that has not yet been fetched/verified
(`verified_official_contract=False`) is deliberately exempt from this
exact-value check — mirroring `SelenePromptManifest`'s own "not yet
Verified" placeholder shape, which the Adapter still refuses to *use*
(`is_complete_and_verified` stays `False`) but which must remain
constructible so that state is representable at all.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field, model_validator

from margpa_runtime_llm.modules.guardrail_governance.domain.qwen3guard import Qwen3GuardTarget

# P6-RR-R27 (resolves P6-CODEX-090): the Exact Contract this Project's own
# checked-in Manifest (`config/guardrail/qwen3guard/manifest.json`) must
# match, fixed from R23's own Read-only fetch of Qwen's official Hugging
# Face/GitHub Sources. Network Access is prohibited for this Package
# (R25-R28 Handoff §Scope Boundary) — these are frozen local constants,
# never re-fetched here.
_OFFICIAL_HUGGINGFACE_REPOSITORY = "Qwen/Qwen3Guard-Gen-0.6B"
_OFFICIAL_GITHUB_REPOSITORY = "QwenLM/Qwen3Guard"
_EXPECTED_PROVIDER_ID = "guard.qwen3guard-gen-0.6b-q8-0"
_EXPECTED_LABEL_SCHEMA_ID = "qwen3guard_gen_frozen_line_protocol_v1"
_EXPECTED_SAFETY_LABELS = ("Safe", "Unsafe", "Controversial")
_EXPECTED_REFUSAL_LABELS = ("Yes", "No")
_EXPECTED_INPUT_CONTEXT_REQUIRED_FIELDS = ("Safety", "Categories")
_EXPECTED_OUTPUT_CANDIDATE_REQUIRED_FIELDS = ("Safety", "Categories", "Refusal")
# Official Category Set (QwenLM/Qwen3Guard README's own "Safety
# Categories" section + the HF `chat_template`'s two distinct Category
# lists): 9 for Input/Context, 8 for Output Candidate — `Jailbreak` is
# documented Input-only ("Jailbreak (Only for input): Content that
# explicitly attempts to override the model's system prompt or model
# conditioning.").
_EXPECTED_INPUT_CONTEXT_CATEGORIES = (
    "Violent",
    "Non-violent Illegal Acts",
    "Sexual Content or Sexual Acts",
    "PII",
    "Suicide & Self-Harm",
    "Unethical Acts",
    "Politically Sensitive Topics",
    "Copyright Violation",
    "Jailbreak",
)
_EXPECTED_OUTPUT_CANDIDATE_CATEGORIES = (
    "Violent",
    "Non-violent Illegal Acts",
    "Sexual Content or Sexual Acts",
    "PII",
    "Suicide & Self-Harm",
    "Unethical Acts",
    "Politically Sensitive Topics",
    "Copyright Violation",
)
_EXPECTED_CATEGORY_UNION = frozenset(_EXPECTED_INPUT_CONTEXT_CATEGORIES) | frozenset(
    _EXPECTED_OUTPUT_CANDIDATE_CATEGORIES
)
# Immutable commit-level Revision shape (a real Git SHA, never a mutable
# branch name like `main`) — both official Sources are GitHub-hosted (HF
# repositories are themselves Git repositories), so both Exact Revisions
# share this identical 40-hex-character form.
_IMMUTABLE_REVISION_PATTERN = re.compile(r"^[0-9a-f]{40}$")


class Qwen3GuardOfficialSource(BaseModel):
    """Provenance for one of the two independent official Sources this
    Manifest is derived from."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    repository: str = Field(min_length=1, max_length=256)
    source_url: str | None = Field(default=None, max_length=512)
    exact_revision: str | None = Field(default=None, max_length=128)
    source_file: str | None = Field(default=None, max_length=256)
    source_sha512: str | None = Field(default=None, pattern=r"^[0-9a-f]{128}$")
    retrieved_at: str | None = None


class Qwen3GuardManifest(BaseModel):
    """Project-local, checked-in Contract Manifest. `Qwen3GuardGenAdapter`
    loads and validates one of these at Adapter construction time
    (Pydantic schema validation itself is the "Manifest Validation"
    P6-CODEX-087 requires as an Activation/Construction precondition) and
    gates every real `classify_point()` call on `is_complete_and_verified`
    — never on a caller-supplied `verified_official_contract` in
    isolation."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    schema_version: str = "1"
    provider_id: str = Field(min_length=1, max_length=128)
    label_schema_id: str = Field(min_length=1, max_length=128)
    verified_official_contract: bool
    retrieval_status: str = Field(min_length=1, max_length=128)

    huggingface_source: Qwen3GuardOfficialSource
    github_source: Qwen3GuardOfficialSource

    safety_labels: tuple[str, ...] = ("Safe", "Unsafe", "Controversial")
    refusal_labels: tuple[str, ...] = ("Yes", "No")

    # Frozen Line Protocol (P6-RR-R23 contract item 3): Input/Context
    # requires exactly these 2 lines in this order; Output Candidate
    # requires exactly these 3.
    input_context_required_fields: tuple[str, ...] = ("Safety", "Categories")
    output_candidate_required_fields: tuple[str, ...] = ("Safety", "Categories", "Refusal")

    # Frozen per-Target Category Set (P6-RR-R23 contract item 4): the
    # official label strings the model itself emits on the `Categories:`
    # line, scoped per Target — `input_context_categories` includes
    # `Jailbreak`, `output_candidate_categories` does not.
    input_context_categories: tuple[str, ...] = Field(default_factory=tuple, max_length=32)
    output_candidate_categories: tuple[str, ...] = Field(default_factory=tuple, max_length=32)
    # Official label (e.g. "Non-violent Illegal Acts") -> internal
    # `CATEGORY_*` id (e.g. "non_violent_illegal_acts"). A superset of
    # both per-Target lists above — `category_mapping_for()` derives the
    # correctly-scoped subset for a given Target.
    category_id_mapping: dict[str, str] = Field(default_factory=dict)

    @model_validator(mode="after")
    def _validate_exact_official_contract(self) -> Qwen3GuardManifest:
        """P6-RR-R27 (resolves P6-CODEX-090): a Manifest that claims
        `verified_official_contract=True` must genuinely match this
        module's `_EXPECTED_*` Exact Contract constants in every one of
        the fields Contract item 1 names — Official Repository Identity,
        Provider ID/Label Schema ID, Immutable Revision format, per-Target
        Field order, Safety/Refusal Label Sets, per-Target Category Set,
        and Category Mapping Key coverage. Construction itself raises
        (via Pydantic's own `ValidationError` wrapping) rather than
        letting a malformed-but-claimed-Verified Manifest ever exist as a
        usable object — Controller Probe C's exact reproduction
        (`provider_id="wrong.provider"`, `required_fields=("Wrong",)`,
        `categories=("FakeInput",)`, `verified_official_contract=True`)
        must fail here, at load time, not merely read back as `is_
        complete_and_verified=False` later. A not-yet-fetched Manifest
        (`verified_official_contract=False`) is exempt — it must remain
        constructible as an honest "not yet Verified" placeholder,
        mirroring `SelenePromptManifest`'s identical shape; `is_complete_
        and_verified` already reports `False` for it regardless."""
        if not self.verified_official_contract:
            return self
        if self.provider_id != _EXPECTED_PROVIDER_ID:
            raise ValueError(f"provider_id_mismatch: expected {_EXPECTED_PROVIDER_ID!r}")
        if self.label_schema_id != _EXPECTED_LABEL_SCHEMA_ID:
            raise ValueError(f"label_schema_id_mismatch: expected {_EXPECTED_LABEL_SCHEMA_ID!r}")
        if self.huggingface_source.repository != _OFFICIAL_HUGGINGFACE_REPOSITORY:
            raise ValueError("huggingface_repository_mismatch")
        if self.github_source.repository != _OFFICIAL_GITHUB_REPOSITORY:
            raise ValueError("github_repository_mismatch")
        if tuple(self.safety_labels) != _EXPECTED_SAFETY_LABELS:
            raise ValueError("safety_labels_mismatch")
        if tuple(self.refusal_labels) != _EXPECTED_REFUSAL_LABELS:
            raise ValueError("refusal_labels_mismatch")
        if tuple(self.input_context_required_fields) != _EXPECTED_INPUT_CONTEXT_REQUIRED_FIELDS:
            raise ValueError("input_context_required_fields_mismatch")
        if (
            tuple(self.output_candidate_required_fields)
            != _EXPECTED_OUTPUT_CANDIDATE_REQUIRED_FIELDS
        ):
            raise ValueError("output_candidate_required_fields_mismatch")
        input_categories = tuple(self.input_context_categories)
        if len(input_categories) != len(set(input_categories)) or set(input_categories) != set(
            _EXPECTED_INPUT_CONTEXT_CATEGORIES
        ):
            raise ValueError("input_context_categories_mismatch")
        output_categories = tuple(self.output_candidate_categories)
        if len(output_categories) != len(set(output_categories)) or set(output_categories) != set(
            _EXPECTED_OUTPUT_CANDIDATE_CATEGORIES
        ):
            raise ValueError("output_candidate_categories_mismatch")
        mapping_keys = tuple(self.category_id_mapping.keys())
        if (
            len(mapping_keys) != len(set(mapping_keys))
            or set(mapping_keys) != _EXPECTED_CATEGORY_UNION
        ):
            raise ValueError("category_mapping_keys_do_not_cover_union_exactly")
        for source in (self.huggingface_source, self.github_source):
            if source.exact_revision is not None and not _IMMUTABLE_REVISION_PATTERN.match(
                source.exact_revision
            ):
                raise ValueError("exact_revision_format_invalid")
        return self

    @property
    def is_complete_and_verified(self) -> bool:
        """P6-RR-R23 (resolves P6-CODEX-087's `verified_official_contract`
        finding): mirrors `SelenePromptAdapter.build()`'s own inline
        completeness check one layer up — every Source Identity field and
        every Category list this Manifest claims to carry must actually
        be present, not merely the bare boolean flag."""
        return (
            self.verified_official_contract
            and self.huggingface_source.exact_revision is not None
            and self.huggingface_source.source_sha512 is not None
            and self.github_source.exact_revision is not None
            and self.github_source.source_sha512 is not None
            and bool(self.input_context_categories)
            and bool(self.output_candidate_categories)
            and bool(self.category_id_mapping)
        )

    def required_fields_for(self, target: Qwen3GuardTarget) -> tuple[str, ...]:
        if target is Qwen3GuardTarget.OUTPUT_CANDIDATE:
            return self.output_candidate_required_fields
        return self.input_context_required_fields

    def allowed_categories_for(self, target: Qwen3GuardTarget) -> tuple[str, ...]:
        if target is Qwen3GuardTarget.OUTPUT_CANDIDATE:
            return self.output_candidate_categories
        return self.input_context_categories

    def category_mapping_for(self, target: Qwen3GuardTarget) -> dict[str, str]:
        """The per-Target-scoped subset of `category_id_mapping` —
        e.g. `Jailbreak` is present in `category_id_mapping` (a genuine,
        known official label) but absent from this method's result for
        `OUTPUT_CANDIDATE`, so the Strict Decoder treats a model that
        emits it there as an `unknown` label (never silently accepted,
        never collapsed to `Safe`) — P6-CODEX-087's exact "Input-only
        `Jailbreak` on Output" example."""
        allowed = set(self.allowed_categories_for(target))
        return {
            label: category_id
            for label, category_id in self.category_id_mapping.items()
            if label in allowed
        }


@dataclass(frozen=True, slots=True)
class Qwen3GuardManifestUnavailable(Exception):
    reason: str

    def __str__(self) -> str:
        return f"Qwen3Guard contract manifest unavailable: {self.reason}"


def load_qwen3guard_manifest(path: Path) -> Qwen3GuardManifest:
    return Qwen3GuardManifest.model_validate_json(path.read_text(encoding="utf-8"))


__all__ = [
    "Qwen3GuardManifest",
    "Qwen3GuardManifestUnavailable",
    "Qwen3GuardOfficialSource",
    "load_qwen3guard_manifest",
]
