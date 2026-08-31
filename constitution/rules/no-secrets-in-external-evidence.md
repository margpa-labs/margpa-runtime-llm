# no-secrets-in-external-evidence

- Rule ID: `no-secrets-in-external-evidence`
- Revision: 1
- Applies to: `chat`, `agent`

## Rule

An API Key, Password, Token, or other Credential-shaped string must never be
surfaced to the Main Model as Evidence, regardless of its origin (a Retrieved
Document, a Fetched URL, a Tool Result).

## Rationale

Evidence surfaced to the Main Model becomes part of what the Model can repeat,
summarize, or otherwise expose in its Response. A Secret that reaches Evidence
has effectively left the boundary that was supposed to contain it, even if the
Model itself never explicitly quotes it back.

## Existing Enforcement (as of Phase 8)

- `detect_secret_candidates()` in `modules/web_knowledge/domain/secret_detector.py`
  already rejects a Secret-shaped Search Query before any Search Provider is
  called (P7-ACC-022).
- This Rule's own Resolver support is currently `unsupported_action` in this
  Bounded Task (see `constitution/manifest.json` and P8-C's Recovery Index) —
  it names the intended boundary; it does not yet claim the Resolver itself
  independently re-verifies every Evidence source against it.
