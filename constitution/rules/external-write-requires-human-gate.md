# external-write-requires-human-gate

- Rule ID: `external-write-requires-human-gate`
- Revision: 1
- Applies to: `agent`, `tool`

## Rule

Any Action with an External Write, Network, Cost, or otherwise irreversible
Side Effect must reach an explicit Human Approval Gate before executing,
regardless of which Approval Profile (`plan_only`/`manual`/`risk_based`/
`important_gate_only`) is active.

## Rationale

`important_gate_only` (Architecture §4) is explicitly designed to let a
Frozen-Envelope-internal safe Read/Edit/Test/Bounded-Rework proceed without
per-step confirmation — but External Write/Network/Cost/irreversible actions
are exactly the category that Profile still always Gates. This Rule names
that boundary explicitly so it is never silently widened by a future change
that "simplifies" the Approval flow.

## Existing Enforcement (as of Phase 8 Post-Controller First Review Bounded Rework)

- The Dev Agent/Tool/Approval Harness (P8-D, extended by P8-E/P8-F/P8-CR)
  now exists and structurally enforces the boundary this Rule names: the
  `write_note` Tool — the only registered Tool with an External Write
  Side Effect — carries `ImportantGateReason.EXTERNAL_WRITE`, which every
  non-`plan_only` Approval Profile (`manual`/`risk_based`/
  `important_gate_only`) always Gates before executing
  (`DevAgentRunService._requires_approval()`); `plan_only` never executes
  any Step at all. This enforcement lives directly in the Run Service, not
  in a Constitution Resolver evaluating this Rule.
- No Real Filesystem or Network Tool is registered (`bootstrap/dev_agent.py`
  wires only the Fake/Deterministic Adapter) — this Rule's boundary has
  never yet been tested against an Action with a real-world External Write.
- This Rule's own Resolver support (i.e., the Constitution module itself
  executing/evaluating this Rule, as opposed to the Harness structurally
  satisfying it) remains `unsupported_action` in this Bounded Task (see
  `constitution/manifest.json`) — the Constitution module classifies and
  surfaces Rules, it does not execute them; that discipline is unchanged by
  the Harness now existing.
