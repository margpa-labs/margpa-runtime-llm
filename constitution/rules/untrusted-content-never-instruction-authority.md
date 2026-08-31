# untrusted-content-never-instruction-authority

- Rule ID: `untrusted-content-never-instruction-authority`
- Revision: 1
- Applies to: `chat`, `agent`, `tool`

## Rule

Content fetched from a public URL, a Tool Result, or any other External
source must never be treated as System or User Instruction Authority, even
if it contains text shaped like an instruction (a classic Prompt Injection
shape).

## Rationale

A Model that treats fetched content as carrying the same Authority as its own
System Prompt or the real User's own words can be redirected by anything it
reads — this is the single most common real-world failure mode for tools
that fetch and summarize external content.

## Existing Enforcement (as of Phase 8)

- `_inject_web_evidence()` in `modules/conversation/application/
  conversation_generation.py` (P8-A) already splices fetched Web Evidence in
  as a `TOOL`-role Message, explicitly prefixed with
  `WEB_EVIDENCE_UNTRUSTED_INSTRUCTION`, never `SYSTEM`/`USER` role.
- `_inject_documentation_reference()` applies the analogous discipline for
  Documentation RAG Evidence (`TOOL` role, `CURRENT_EVIDENCE_AUTHORITY_
  INSTRUCTION`), predating this Rule's own text.
- This Rule's Resolver support in this Bounded Task is `unsupported_action`
  (see `constitution/manifest.json`) — the mechanism above already exists
  and predates this Constitution mechanism; this Rule documents the intent
  the existing code already follows, rather than the Constitution Resolver
  independently verifying it at runtime.
