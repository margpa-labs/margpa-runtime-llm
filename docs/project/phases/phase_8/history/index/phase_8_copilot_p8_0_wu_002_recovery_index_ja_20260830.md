# Phase 8 Copilot P8-0-WU-002 Recovery Index

```yaml
document_type: recovery_index
phase: phase_8
package: P8-0
work_unit: P8-0-WU-002
completed_cp: CP8-02
state: complete
created_at: 2026-08-30 JST
```

## Adjacent Boundary

- Local RAG citation, SSE projection, and persistent detail currently use `DocumentationCitation` / `PersistedTurnCitationEvidence` in `modules/documentation_rag/contracts.py`, `modules/conversation/application/persistent_conversation_service.py`, `web/persistent_streaming.py`, and `web/persistent_contracts.py`.
- Existing Main Model context assembly and live citation event are in `modules/conversation/application/conversation_generation.py`; `web/streaming.py` carries those events without semantic change.
- The current web-search endpoint and panel are standalone. Their results are not current-turn context and are not historical conversation citation evidence.
- Data Controls remain an adjacent consent/presentation surface only. P8-A must not alter archive, branch, constitution, or agent contracts.

## P8-A Design Boundary

- Direct URL evidence is a new request/result flow, not a `WebSearchQuery`, `WebSearchRun`, snippet, past turn, or fetch-failure body.
- Only explicitly supplied URL content that completes the direct fetch flow may become untrusted current-turn Main Model context.
- Persistent evidence must retain a distinct public-web identity with canonical URL, fetched timestamp, content type, digest, and source class; historical turns remain immutable.

## Status

| Item | State |
|---|---|
| Changed paths | Recovery Index 1 and this Recovery Index only |
| Focused tests | NOT RUN (boundary mapping work unit) |
| P8-A acceptance | P8-ACC-001 baseline preserved; P8-ACC-009–012 pending implementation |
| Open findings | Existing persistent citation type is documentation-RAG-specific; P8-A needs additive compatibility-safe contract work |
| Root/Git/Network/Provider Memory/User Data | Project root only / not used / not used / not used / not used |
| Active process or temporary artifact | None |
| Do not repeat | CP8-01–02 as-built and adjacent-boundary mapping |
| Exact next CP | CP8-03 / P8-0-WU-003 |
