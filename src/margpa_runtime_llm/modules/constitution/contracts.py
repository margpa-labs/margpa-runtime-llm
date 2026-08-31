"""Phase 8 (P8-C): framework-independent contracts for the Provisional
Runtime Constitution.

`constitution/` at the Project Root is this Task's own Bounded Package
(P8-REQ-013) — deliberately distinct from `docs/project/shared/constitution/`
(reserved for the Phase 10 full-Docs-cycle development-operations Constitution
per Architecture §5). Nothing here claims to be that later, complete
Constitution; this is a Provisional Runtime mechanism proving the shape
(Manifest, Digest, Rule, Capability View, OFF/OBSERVE/ENFORCE, Generic
Resolver) a real one would need.
"""

from __future__ import annotations

from enum import StrEnum
from typing import Literal

from pydantic import Field, model_validator

from margpa_runtime_llm.modules.inference.contracts.base import ImmutableContract

SHA512_PATTERN = r"^[0-9a-f]{128}$"
RULE_ID_PATTERN = r"^[a-z][a-z0-9-]{2,63}$"
MAX_RULES = 200


class ConstitutionMode(StrEnum):
    """P8-REQ-016: three genuinely distinct modes, never conflated. `OFF`
    is a Presentation/Evaluation state — it must never be interpreted as
    `allow all` by any caller (Architecture §7 Lifecycle/Failure discipline
    applies here too: `OFF` means "not evaluated", not "permitted")."""

    OFF = "off"
    OBSERVE = "observe"
    ENFORCE = "enforce"


ConstitutionView = Literal["chat", "agent", "tool"]
"""P8-REQ-017: the three View kinds this Task generates. A View only ever
*narrows* what its own Rule subset says — it can never itself grant
Authority no other layer already has (enforced structurally: `CapabilityView`
below carries no Authority-shaped field at all, only Rule references)."""


class ConstitutionRule(ImmutableContract):
    """One Stable-ID Rule (P8-REQ-014). Deliberately provider-neutral: no
    GD name, Provider name, User Path, or Model name ever appears in a Rule
    itself (P8-REQ-019) — only opaque identity and a Pointer back to its own
    JSON source file for a human/auditor to read the real text."""

    rule_id: str = Field(pattern=RULE_ID_PATTERN)
    revision: int = Field(ge=1)
    title: str = Field(min_length=1, max_length=200)
    summary: str = Field(min_length=1, max_length=2000)
    applies_to: tuple[ConstitutionView, ...] = Field(min_length=1)
    source_pointer: str = Field(min_length=1, max_length=256)
    """Project-relative path under `constitution/` this Rule's full text
    lives at — read-only reference, never Hard-coded elsewhere."""

    @model_validator(mode="after")
    def validate_applies_to_has_no_duplicates(self) -> ConstitutionRule:
        if len(set(self.applies_to)) != len(self.applies_to):
            raise ValueError("applies_to must not repeat the same View")
        return self


class ConstitutionManifest(ImmutableContract):
    """P8-REQ-014: Revision + Digest + Rule Source Pointers, all in one
    Immutable, independently-verifiable record."""

    revision: int = Field(ge=1)
    digest_sha512: str = Field(pattern=SHA512_PATTERN)
    """SHA-512 over the canonical JSON of `rules` (see
    `compute_manifest_digest()`), verified by every Provider before this
    Manifest is trusted (P8-ACC-019/024) — never merely trusted because a
    File on disk claims a given Digest."""
    rules: tuple[ConstitutionRule, ...] = Field(max_length=MAX_RULES)

    @model_validator(mode="after")
    def validate_unique_rule_ids(self) -> ConstitutionManifest:
        ids = [rule.rule_id for rule in self.rules]
        if len(set(ids)) != len(ids):
            raise ValueError("manifest rule_id values must be unique")
        return self


class ConstitutionManifestUnavailable(ImmutableContract):
    """Fail-closed placeholder (mirrors `WebCitationUnavailable`/
    `CitationUnavailable`'s established pattern in this codebase) — a
    corrupt or Digest-mismatched Manifest converges here, never raises past
    the Provider boundary and never silently substitutes a permissive
    default (P8-REQ-018)."""

    reason: Literal["corrupt_manifest", "digest_mismatch", "not_present"]


class CapabilityView(ImmutableContract):
    """P8-REQ-017: one View's exact Rule subset plus the Mode it was
    generated under — carries no field capable of expressing "and also
    Authority X", by construction."""

    view: ConstitutionView
    mode: ConstitutionMode
    manifest_revision: int = Field(ge=1)
    manifest_digest_sha512: str = Field(pattern=SHA512_PATTERN)
    rule_ids: tuple[str, ...]


ConstitutionDecisionOutcome = Literal[
    "not_evaluated",
    "observed",
    "enforced",
    "unknown_rule",
    "unsupported_action",
    "conflict",
]


class ConstitutionDecision(ImmutableContract):
    """P8-REQ-018: the Generic Resolver's one output shape. Every outcome
    this Task cannot genuinely evaluate (`unknown_rule`/`unsupported_action`/
    `conflict`) is its own explicit, honest value — never silently coerced
    to `enforced`/`observed` and never dropped."""

    rule_id: str
    mode: ConstitutionMode
    outcome: ConstitutionDecisionOutcome
    reason: str = Field(min_length=1, max_length=500)


ConstitutionEvaluationDisposition = Literal[
    "not_evaluated",
    "evaluate_record_only",
    "evaluate_and_apply_supported_action",
]
"""P8-RW7-A (P8-CODEX-012): what a Mode itself *does* with a Rule, fixed
per-`ConstitutionMode` by the Exact Handoff's frozen semantics table —
independent of whether any individual Rule in a given View happens to be
`supported` today."""

ConstitutionActionPermission = Literal[
    "no_constitution_action",
    "no_block_no_authority_change",
    "supported_actions_only_no_authority_expansion",
]
"""P8-RW7-A (P8-CODEX-012): what Authority a Mode itself grants — never
Provider/Platform/User Authority (P8-REQ-017); `ENFORCE` never expands
Authority beyond Actions this Bounded Task's Resolver already genuinely
supports."""

ConstitutionViolationPresentation = Literal[
    "not_evaluated",
    "observation_only",
    "enforced",
    "typed_unsupported",
]
"""P8-RW7-A (P8-CODEX-012): how a Rule Violation would be presented under
this Mode for *this actual View's Decisions* — honestly derived from the
real `ConstitutionDecision.outcome` values below, never a fabricated
`observation_only`/`enforced` for a Rule this Bounded Task cannot actually
act on (today, every real Rule converges to `typed_unsupported` for both
OBSERVE and ENFORCE); a View with no applicable Rule at all is `
not_evaluated`, not `typed_unsupported` (there is nothing to present)."""

_EVALUATION_DISPOSITION_BY_MODE: dict[ConstitutionMode, ConstitutionEvaluationDisposition] = {
    ConstitutionMode.OFF: "not_evaluated",
    ConstitutionMode.OBSERVE: "evaluate_record_only",
    ConstitutionMode.ENFORCE: "evaluate_and_apply_supported_action",
}

_ACTION_PERMISSION_BY_MODE: dict[ConstitutionMode, ConstitutionActionPermission] = {
    ConstitutionMode.OFF: "no_constitution_action",
    ConstitutionMode.OBSERVE: "no_block_no_authority_change",
    ConstitutionMode.ENFORCE: "supported_actions_only_no_authority_expansion",
}


def _resolve_violation_presentation(
    mode: ConstitutionMode, decisions: tuple[ConstitutionDecision, ...]
) -> ConstitutionViolationPresentation:
    if mode is ConstitutionMode.OFF or not decisions:
        return "not_evaluated"
    if mode is ConstitutionMode.OBSERVE:
        return (
            "observation_only"
            if any(decision.outcome == "observed" for decision in decisions)
            else "typed_unsupported"
        )
    return (
        "enforced"
        if any(decision.outcome == "enforced" for decision in decisions)
        else "typed_unsupported"
    )


class ConstitutionModePreviewEntry(ImmutableContract):
    """P8-RW6-D/P8-RW7-A (P8-CODEX-008/012): one Mode's Pure Evaluation
    Result within a non-Activating comparison Preview — carries the same
    `CapabilityView.rule_ids`/`resolve_decisions()` output this Task's real
    Resolver would produce, but computed for a Mode that may not be
    Production's actual Active Mode (`WebRuntime.constitution_mode`, fixed
    OFF for this whole Bounded Task). Constructing this never touches that
    Active Mode, grants Tool Authority, or injects anything into a Model —
    it is read-only comparison Evidence. `evaluation_disposition`/
    `action_permission`/`violation_presentation` are the Exact Handoff's
    required 3-axis comparison, alongside the pre-existing `decisions`."""

    mode: ConstitutionMode
    rule_ids: tuple[str, ...]
    decisions: tuple[ConstitutionDecision, ...]
    evaluation_disposition: ConstitutionEvaluationDisposition
    action_permission: ConstitutionActionPermission
    violation_presentation: ConstitutionViolationPresentation


class ConstitutionModePreview(ImmutableContract):
    """One View's OFF/OBSERVE/ENFORCE comparison, side by side, computed
    from the same Manifest — always all three `ConstitutionMode` values,
    in enum order."""

    view: ConstitutionView
    manifest_revision: int = Field(ge=1)
    manifest_digest_sha512: str = Field(pattern=SHA512_PATTERN)
    modes: tuple[ConstitutionModePreviewEntry, ...]


def resolve_constitution_mode_preview(
    manifest: ConstitutionManifest,
    *,
    view: ConstitutionView,
    supported_rule_ids: frozenset[str] = frozenset(),
) -> ConstitutionModePreview:
    """P8-RW6-D (P8-CODEX-008): resolves the *same* View against *all three*
    `ConstitutionMode` values for the same Manifest — a Pure comparison
    computation, never a Production Mode change. Every Rule the View
    references is treated as `known` (this Preview shows what the View
    itself already says applies); `supported_rule_ids` defaults to empty,
    honestly matching this Bounded Task's actual Resolver Support state
    (every shipped Rule's `Existing Enforcement` prose declares
    `unsupported_action` today) — a future caller with real executable Rule
    support can pass a populated set without this function's shape
    changing."""

    entries: list[ConstitutionModePreviewEntry] = []
    for mode in ConstitutionMode:
        capability_view = resolve_capability_view(manifest, view=view, mode=mode)
        decisions = resolve_decisions(
            capability_view,
            known_rule_ids=frozenset(capability_view.rule_ids),
            supported_rule_ids=supported_rule_ids,
        )
        entries.append(
            ConstitutionModePreviewEntry(
                mode=mode,
                rule_ids=capability_view.rule_ids,
                decisions=decisions,
                evaluation_disposition=_EVALUATION_DISPOSITION_BY_MODE[mode],
                action_permission=_ACTION_PERMISSION_BY_MODE[mode],
                violation_presentation=_resolve_violation_presentation(mode, decisions),
            )
        )
    return ConstitutionModePreview(
        view=view,
        manifest_revision=manifest.revision,
        manifest_digest_sha512=manifest.digest_sha512,
        modes=tuple(entries),
    )


def compute_manifest_digest(rules: tuple[ConstitutionRule, ...]) -> str:
    """The single canonical Digest computation both the Provider (writing/
    verifying `manifest.json`) and any Test/Tooling that needs to
    independently recompute it must share — never two divergent
    implementations of "the same" Digest."""

    import hashlib
    import json

    payload = json.dumps(
        [rule.model_dump(mode="json") for rule in rules],
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha512(payload.encode("utf-8")).hexdigest()


def resolve_capability_view(
    manifest: ConstitutionManifest,
    *,
    view: ConstitutionView,
    mode: ConstitutionMode,
) -> CapabilityView:
    """P8-REQ-017: the one function that turns a whole Manifest into one
    View's Rule subset — filters purely on `applies_to`, adds nothing."""

    rule_ids = tuple(rule.rule_id for rule in manifest.rules if view in rule.applies_to)
    return CapabilityView(
        view=view,
        mode=mode,
        manifest_revision=manifest.revision,
        manifest_digest_sha512=manifest.digest_sha512,
        rule_ids=rule_ids,
    )


def resolve_decisions(
    capability_view: CapabilityView,
    *,
    known_rule_ids: frozenset[str],
    supported_rule_ids: frozenset[str],
) -> tuple[ConstitutionDecision, ...]:
    """P8-REQ-018/P8-REQ-019's Generic Resolver: deliberately takes only
    opaque `rule_id` sets, never a GD-specific type — this function has no
    idea what any Rule actually *means*, only whether the caller says it is
    (a) a real, known Rule and (b) one this Task can genuinely act on.

    - `OFF` mode never evaluates anything (P8-REQ-016) — every Rule in the
      View converges to `not_evaluated`, regardless of (a)/(b) above; `OFF`
      is a Presentation/Evaluation state, not `allow all`.
    - A Rule ID present in the View but absent from `known_rule_ids` is a
      genuine integrity problem (the View references a Rule the Provider
      itself no longer/never knew) — `unknown_rule`, never silently skipped.
    - A known but unsupported Rule ID (in `known_rule_ids` but not
      `supported_rule_ids` — e.g. a Rule this Bounded Task's Resolver has
      no executable logic for yet) converges to `unsupported_action`, not a
      false `enforced`/`observed`.
    - Otherwise: `ENFORCE` -> `enforced`, `OBSERVE` -> `observed`.
    """

    decisions: list[ConstitutionDecision] = []
    for rule_id in capability_view.rule_ids:
        if capability_view.mode is ConstitutionMode.OFF:
            decisions.append(
                ConstitutionDecision(
                    rule_id=rule_id,
                    mode=capability_view.mode,
                    outcome="not_evaluated",
                    reason="Constitution mode is OFF for this View.",
                )
            )
            continue
        if rule_id not in known_rule_ids:
            decisions.append(
                ConstitutionDecision(
                    rule_id=rule_id,
                    mode=capability_view.mode,
                    outcome="unknown_rule",
                    reason="This View references a Rule ID the Provider does not recognize.",
                )
            )
            continue
        if rule_id not in supported_rule_ids:
            decisions.append(
                ConstitutionDecision(
                    rule_id=rule_id,
                    mode=capability_view.mode,
                    outcome="unsupported_action",
                    reason="This Bounded Resolver has no executable logic for this Rule yet.",
                )
            )
            continue
        decisions.append(
            ConstitutionDecision(
                rule_id=rule_id,
                mode=capability_view.mode,
                outcome=(
                    "enforced" if capability_view.mode is ConstitutionMode.ENFORCE else "observed"
                ),
                reason=(
                    "Rule evaluated and enforced."
                    if capability_view.mode is ConstitutionMode.ENFORCE
                    else "Rule evaluated in observe-only mode; no Action was blocked."
                ),
            )
        )
    return tuple(decisions)
