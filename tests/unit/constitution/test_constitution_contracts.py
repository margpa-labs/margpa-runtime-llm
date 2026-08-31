"""Phase 8 (P8-C): Provisional Runtime Constitution contract/resolver tests."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from margpa_runtime_llm.modules.constitution import (
    CapabilityView,
    ConstitutionManifest,
    ConstitutionMode,
    ConstitutionRule,
    compute_manifest_digest,
    resolve_capability_view,
    resolve_constitution_mode_preview,
    resolve_decisions,
)


def _rule(
    rule_id: str = "example-rule",
    *,
    applies_to: tuple[str, ...] = ("chat",),
) -> ConstitutionRule:
    return ConstitutionRule(
        rule_id=rule_id,
        revision=1,
        title="Example Rule",
        summary="A minimal Rule used only by this Test.",
        applies_to=applies_to,  # type: ignore[arg-type]
        source_pointer=f"rules/{rule_id}.md",
    )


def _manifest(rules: tuple[ConstitutionRule, ...]) -> ConstitutionManifest:
    return ConstitutionManifest(
        revision=1, digest_sha512=compute_manifest_digest(rules), rules=rules
    )


def test_manifest_rejects_duplicate_rule_ids() -> None:
    rules = (_rule("dup"), _rule("dup"))
    with pytest.raises(ValidationError):
        ConstitutionManifest(revision=1, digest_sha512=compute_manifest_digest(rules), rules=rules)


def test_rule_rejects_duplicate_applies_to_entries() -> None:
    with pytest.raises(ValidationError):
        _rule(applies_to=("chat", "chat"))


def test_compute_manifest_digest_is_deterministic_and_order_sensitive_on_content() -> None:
    rules_a = (_rule("rule-a"), _rule("rule-b"))
    rules_b = (_rule("rule-a"), _rule("rule-b"))
    assert compute_manifest_digest(rules_a) == compute_manifest_digest(rules_b)
    # A genuinely different Rule set must never collide.
    rules_c = (_rule("rule-a"), _rule("rule-c"))
    assert compute_manifest_digest(rules_a) != compute_manifest_digest(rules_c)


def test_resolve_capability_view_filters_purely_on_applies_to() -> None:
    manifest = _manifest(
        (
            _rule("chat-only", applies_to=("chat",)),
            _rule("agent-tool", applies_to=("agent", "tool")),
            _rule("all-views", applies_to=("chat", "agent", "tool")),
        )
    )

    chat_view = resolve_capability_view(manifest, view="chat", mode=ConstitutionMode.OBSERVE)
    assert set(chat_view.rule_ids) == {"chat-only", "all-views"}

    tool_view = resolve_capability_view(manifest, view="tool", mode=ConstitutionMode.ENFORCE)
    assert set(tool_view.rule_ids) == {"agent-tool", "all-views"}

    # P8-REQ-017: the View carries the Manifest's own Revision/Digest
    # unchanged — it never fabricates its own independent identity.
    assert chat_view.manifest_revision == manifest.revision
    assert chat_view.manifest_digest_sha512 == manifest.digest_sha512


def test_off_mode_never_evaluates_anything_even_for_known_supported_rules() -> None:
    """P8-REQ-016: OFF must never be interpreted as `allow all` — every Rule
    in View converges to `not_evaluated`, regardless of whether the Resolver
    could otherwise have supported it."""

    view = CapabilityView(
        view="chat",
        mode=ConstitutionMode.OFF,
        manifest_revision=1,
        manifest_digest_sha512="a" * 128,
        rule_ids=("known-supported",),
    )
    decisions = resolve_decisions(
        view,
        known_rule_ids=frozenset({"known-supported"}),
        supported_rule_ids=frozenset({"known-supported"}),
    )
    assert len(decisions) == 1
    assert decisions[0].outcome == "not_evaluated"
    assert decisions[0].mode is ConstitutionMode.OFF


def test_unknown_rule_id_converges_to_unknown_rule_never_silently_skipped() -> None:
    view = CapabilityView(
        view="chat",
        mode=ConstitutionMode.OBSERVE,
        manifest_revision=1,
        manifest_digest_sha512="a" * 128,
        rule_ids=("ghost-rule",),
    )
    decisions = resolve_decisions(view, known_rule_ids=frozenset(), supported_rule_ids=frozenset())
    assert len(decisions) == 1
    assert decisions[0].outcome == "unknown_rule"


def test_known_but_unsupported_rule_never_reports_a_false_enforced_or_observed() -> None:
    view = CapabilityView(
        view="agent",
        mode=ConstitutionMode.ENFORCE,
        manifest_revision=1,
        manifest_digest_sha512="a" * 128,
        rule_ids=("known-unsupported",),
    )
    decisions = resolve_decisions(
        view,
        known_rule_ids=frozenset({"known-unsupported"}),
        supported_rule_ids=frozenset(),
    )
    assert len(decisions) == 1
    assert decisions[0].outcome == "unsupported_action"


def test_observe_mode_reports_observed_never_enforced() -> None:
    view = CapabilityView(
        view="chat",
        mode=ConstitutionMode.OBSERVE,
        manifest_revision=1,
        manifest_digest_sha512="a" * 128,
        rule_ids=("supported",),
    )
    decisions = resolve_decisions(
        view, known_rule_ids=frozenset({"supported"}), supported_rule_ids=frozenset({"supported"})
    )
    assert decisions[0].outcome == "observed"


def test_enforce_mode_reports_enforced() -> None:
    view = CapabilityView(
        view="chat",
        mode=ConstitutionMode.ENFORCE,
        manifest_revision=1,
        manifest_digest_sha512="a" * 128,
        rule_ids=("supported",),
    )
    decisions = resolve_decisions(
        view, known_rule_ids=frozenset({"supported"}), supported_rule_ids=frozenset({"supported"})
    )
    assert decisions[0].outcome == "enforced"


def test_view_carries_no_authority_shaped_field() -> None:
    """P8-REQ-017: structural proof, not just a docstring claim — the
    CapabilityView model's own field set is checked directly."""

    fields = set(CapabilityView.model_fields)
    forbidden_substrings = ("authority", "permission", "grant", "allow")
    for field in fields:
        for forbidden in forbidden_substrings:
            assert forbidden not in field.lower(), f"{field} looks Authority-shaped"


# -- P8-RW6-D (P8-CODEX-008): Constitution Mode Comparison Preview ----------


def test_mode_preview_returns_all_three_modes_in_enum_order() -> None:
    manifest = _manifest((_rule("chat-only", applies_to=("chat",)),))
    preview = resolve_constitution_mode_preview(manifest, view="chat")

    assert preview.view == "chat"
    assert preview.manifest_revision == manifest.revision
    assert preview.manifest_digest_sha512 == manifest.digest_sha512
    assert [entry.mode for entry in preview.modes] == [
        ConstitutionMode.OFF,
        ConstitutionMode.OBSERVE,
        ConstitutionMode.ENFORCE,
    ]


def test_mode_preview_off_never_evaluates_even_when_a_rule_is_supported() -> None:
    """P8-REQ-016 applied to the Preview path too: OFF's Result must never
    read as `allow all`, even for a Rule the Preview marks as `supported`."""

    manifest = _manifest((_rule("supported-rule", applies_to=("chat",)),))
    preview = resolve_constitution_mode_preview(
        manifest, view="chat", supported_rule_ids=frozenset({"supported-rule"})
    )

    off_entry = preview.modes[0]
    assert off_entry.mode is ConstitutionMode.OFF
    assert all(decision.outcome == "not_evaluated" for decision in off_entry.decisions)


def test_mode_preview_observe_and_enforce_diverge_for_a_supported_rule() -> None:
    """The comparison's whole point: given a Rule this Preview marks
    `supported`, OBSERVE and ENFORCE must produce genuinely different
    Decision Outcomes for the identical Manifest/View."""

    manifest = _manifest((_rule("supported-rule", applies_to=("agent",)),))
    preview = resolve_constitution_mode_preview(
        manifest, view="agent", supported_rule_ids=frozenset({"supported-rule"})
    )

    by_mode = {entry.mode: entry for entry in preview.modes}
    assert by_mode[ConstitutionMode.OBSERVE].decisions[0].outcome == "observed"
    assert by_mode[ConstitutionMode.ENFORCE].decisions[0].outcome == "enforced"
    assert (
        by_mode[ConstitutionMode.OBSERVE].decisions[0].outcome
        != by_mode[ConstitutionMode.ENFORCE].decisions[0].outcome
    )


def test_mode_preview_defaults_to_the_honest_unsupported_action_for_todays_real_rules() -> None:
    """Without an explicit `supported_rule_ids` override, every Rule is
    honestly `unsupported_action` for OBSERVE/ENFORCE — matching this
    Bounded Task's actual Resolver Support state (every shipped Rule's own
    prose declares `unsupported_action` today). The Preview must never
    fabricate a false `observed`/`enforced` just to look more different."""

    manifest = _manifest((_rule("real-rule", applies_to=("tool",)),))
    preview = resolve_constitution_mode_preview(manifest, view="tool")

    by_mode = {entry.mode: entry for entry in preview.modes}
    assert by_mode[ConstitutionMode.OBSERVE].decisions[0].outcome == "unsupported_action"
    assert by_mode[ConstitutionMode.ENFORCE].decisions[0].outcome == "unsupported_action"


# -- P8-RW7-A (P8-CODEX-012): 3-axis Mode comparison semantics --------------


def test_mode_preview_entries_carry_the_frozen_per_mode_semantics() -> None:
    """Exact Handoff §4's fixed table: `evaluation_disposition`/
    `action_permission` depend only on the Mode itself, never on whether
    any Rule in this View happens to be `supported` today."""

    manifest = _manifest((_rule("chat-only", applies_to=("chat",)),))
    preview = resolve_constitution_mode_preview(manifest, view="chat")
    by_mode = {entry.mode: entry for entry in preview.modes}

    assert by_mode[ConstitutionMode.OFF].evaluation_disposition == "not_evaluated"
    assert by_mode[ConstitutionMode.OFF].action_permission == "no_constitution_action"

    assert by_mode[ConstitutionMode.OBSERVE].evaluation_disposition == "evaluate_record_only"
    assert by_mode[ConstitutionMode.OBSERVE].action_permission == "no_block_no_authority_change"

    assert (
        by_mode[ConstitutionMode.ENFORCE].evaluation_disposition
        == "evaluate_and_apply_supported_action"
    )
    assert (
        by_mode[ConstitutionMode.ENFORCE].action_permission
        == "supported_actions_only_no_authority_expansion"
    )


def test_off_entry_violation_presentation_is_always_not_evaluated() -> None:
    manifest = _manifest((_rule("supported-rule", applies_to=("chat",)),))
    preview = resolve_constitution_mode_preview(
        manifest, view="chat", supported_rule_ids=frozenset({"supported-rule"})
    )
    off_entry = next(entry for entry in preview.modes if entry.mode is ConstitutionMode.OFF)
    assert off_entry.violation_presentation == "not_evaluated"


def test_violation_presentation_stays_typed_unsupported_for_todays_real_rules() -> None:
    """Without an explicit `supported_rule_ids` override (this Bounded
    Task's honest default), OBSERVE/ENFORCE must present
    `typed_unsupported` — never a fabricated `observation_only`/`enforced`
    for a Rule this Task cannot actually act on."""

    manifest = _manifest((_rule("real-rule", applies_to=("tool",)),))
    preview = resolve_constitution_mode_preview(manifest, view="tool")
    by_mode = {entry.mode: entry for entry in preview.modes}

    assert by_mode[ConstitutionMode.OBSERVE].violation_presentation == "typed_unsupported"
    assert by_mode[ConstitutionMode.ENFORCE].violation_presentation == "typed_unsupported"


def test_violation_presentation_diverges_for_a_genuinely_supported_rule() -> None:
    manifest = _manifest((_rule("supported-rule", applies_to=("agent",)),))
    preview = resolve_constitution_mode_preview(
        manifest, view="agent", supported_rule_ids=frozenset({"supported-rule"})
    )
    by_mode = {entry.mode: entry for entry in preview.modes}

    assert by_mode[ConstitutionMode.OBSERVE].violation_presentation == "observation_only"
    assert by_mode[ConstitutionMode.ENFORCE].violation_presentation == "enforced"


def test_violation_presentation_is_not_evaluated_when_a_view_has_no_applicable_rules() -> None:
    """Honesty edge case: a View no Rule applies to must never claim
    `typed_unsupported` (which would imply a Rule existed and was merely
    unsupported) — there is nothing to present at all."""

    manifest = _manifest((_rule("chat-only", applies_to=("chat",)),))
    preview = resolve_constitution_mode_preview(manifest, view="tool")
    for entry in preview.modes:
        assert entry.rule_ids == ()
        assert entry.violation_presentation == "not_evaluated"


def test_mode_preview_never_touches_the_mode_it_is_called_with_as_a_side_effect() -> None:
    """A Pure function: computing a Preview for one Manifest/View must not
    mutate the Manifest, and calling it repeatedly must be idempotent —
    there is no hidden state a 'Preview' Call could be leaking into."""

    manifest = _manifest((_rule("stable-rule", applies_to=("chat",)),))
    first = resolve_constitution_mode_preview(manifest, view="chat")
    second = resolve_constitution_mode_preview(manifest, view="chat")

    assert first == second
    assert manifest.rules[0].rule_id == "stable-rule"  # Manifest itself untouched
