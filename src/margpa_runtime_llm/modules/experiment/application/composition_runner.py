"""Composition Runner (Phase 9-2, WU-C C1/C2/C3/C5).

The one place that decides whether an Actor's `invoke()` is called at
all for a given Component slot on a given Variant -- every Independence
Matrix guarantee (WU-C C3) traces back to this single function's
skip logic, not to each individual Fixture/Production Actor remembering
to behave correctly when it is "supposed to be off"."""

from __future__ import annotations

from collections.abc import Mapping

from ..domain.composition import ActorInvocationRecord, ActorPort, VariantExecutionResult
from ..domain.identity import ComponentKey, VariantDescriptor

_OFF_MODE_VALUES = frozenset({"off"})


def run_variant(
    variant: VariantDescriptor, actors: Mapping[ComponentKey, ActorPort]
) -> VariantExecutionResult:
    """WU-C C1/C2/C3: iterates the full `ComponentKey` universe (not just
    the keys the Variant happens to declare) so an entirely-absent
    Component is represented too. For each key:

    - absent (`variant.component(key) is None`), `mode is None`, or
      `mode == "off"` -> never calls any Actor; records `called=False,
      outcome="off"` (or `"absent"`). R1-WU-02 (IR-P9-2-07 fix):
      `ComponentSelection.mode`'s own Contract doc (`identity.py`) already
      states `None` means "this Component is OFF/absent for this
      Variant" -- a present `ComponentSelection` with `mode=None` was
      previously falling through to a real Actor call, which the
      Controller's Independent Review confirmed as a direct violation of
      the "Component OFF/不在 => Call/Mutation/Evidence/Authority 0"
      Invariant. Only an explicit, non-`None`, non-`"off"` mode string
      now reaches an Actor's `invoke()`.
    - present and not off, but no Actor registered for this key
      (Unsupported in this environment) -> never calls anything; records
      `called=False, outcome="unsupported"`.
    - present, not off, and an Actor is registered -> calls exactly that
      Actor's `invoke()` once and records its own result verbatim.

    WU-C C5 Isolation: this function is a pure, synchronous, Variant-
    scoped call with no shared mutable state across invocations -- two
    concurrent calls (one per Variant) touch entirely separate `actors`
    mappings and return entirely separate `VariantExecutionResult`
    instances, so nothing here can leak between them."""

    invocations: list[ActorInvocationRecord] = []
    for key in ComponentKey:
        selection = variant.component(key)
        if selection is None:
            invocations.append(
                ActorInvocationRecord(component_key=key, called=False, outcome="absent")
            )
            continue
        if selection.mode is None or selection.mode in _OFF_MODE_VALUES:
            invocations.append(
                ActorInvocationRecord(component_key=key, called=False, outcome="off")
            )
            continue
        actor = actors.get(key)
        if actor is None:
            invocations.append(
                ActorInvocationRecord(component_key=key, called=False, outcome="unsupported")
            )
            continue
        invocations.append(actor.invoke(component_key=key, mode=selection.mode))
    return VariantExecutionResult(variant_id=variant.variant_id, invocations=tuple(invocations))
