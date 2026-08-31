# Phase 8 Copilot P8-0-WU-001 Recovery Index

```yaml
document_type: recovery_index
phase: phase_8
package: P8-0
work_unit: P8-0-WU-001
completed_cp: CP8-01
state: complete
created_at: 2026-08-30 JST
```

## Entry Receipt

```text
Provider: GitHub Copilot app
Role: 設計者兼実装者役
Task Identity: Fresh Copilot Phase 8 Head Task
Mandatory Reading: COMPLETE
Active Scope: P8-0 / P8-A ONLY
Exact Start Work Unit: CP8-01 / P8-0-WU-001
Implementation Authority: TRUE
Network Authority: FALSE
Git Authority: FALSE
State: ACTIVE
```

## As-built Map

- Domain contract and application pipeline: `src/margpa_runtime_llm/modules/web_knowledge/contracts.py` and `application/web_knowledge_service.py`.
- Public URL gate and bounded redirect-aware HTTP adapter: `modules/web_knowledge/domain/url_security.py` and `adapters/web_knowledge/httpx_fetch_provider.py`.
- Runtime composition and API projection: `bootstrap/web_knowledge.py`, `web/web_search_routes.py`, and `web/web_search_contracts.py`.
- Web application integration: `web/app.py`, `bootstrap/web_application.py`, and `entrypoints/web/main.py`.
- Existing UI and settings integration: `frontend/src/components/WebSearchPanel.tsx`, `SettingsPanel.tsx`, `SettingsModal/SettingsModal.tsx`, and `App.tsx`.
- Existing focused evidence: `tests/unit/web_knowledge/`, `tests/integration/web/test_web_search_web_app.py`, and `frontend/src/components/WebSearchPanel.test.tsx`.

## Reuse and Change-prohibited Baseline

- Reuse Phase 7 `WebFetchProviderPort`, `HttpxWebFetchProvider`, URL security gate, prompt-injection/secret detection, search evidence/citation contracts, and their fixture/mock-transport tests.
- Do not reimplement General/Automatic Search or alter Phase 7 Local RAG, citation, data controls, conversation persistence, branch/archive, constitution, or agent scope.
- No source mutation has occurred in CP8-01.

## Status

| Item | State |
|---|---|
| Focused tests | NOT RUN (mapping-only work unit) |
| P8-A acceptance | Not yet evaluated |
| Open findings | None |
| Root/Git/Network/Provider Memory/User Data | Project root only / not used / not used / not used / not used |
| Active process or temporary artifact | None |
| Resource signal | User-reported weekly availability: 7% remaining |
| Do not repeat | Mandatory reading, document hash verification, and CP8-01 source map |
| Exact next CP | CP8-02 / P8-0-WU-002 |
