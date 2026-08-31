# Phase 8 Copilot P8-0-WU-003 Recovery Index

```yaml
document_type: recovery_index
phase: phase_8
package: P8-0
work_unit: P8-0-WU-003
completed_cp: CP8-03
state: complete
created_at: 2026-08-30 JST
```

## Authority and Test Freeze

- Authorized mutation is limited to P8-0/P8-A source, tests, frontend, config/static artifacts, and new append-only Phase 8 recovery/operation/handoff/automation evidence.
- Network, Git, project-root-external actions, installs/downloads, provider memory, user `runtime_data/`, real browser, and model loading are prohibited and have not been used.
- Existing `.venv` and `frontend/node_modules` are the only permitted test/build dependencies. No package manager action is authorized.
- Real URL validation is `NOT RUN / USER MANUAL GATE`. `httpx.MockTransport` and fixture paths are zero-real-socket evidence only.

## Entry Inventory and Matrix

| Surface | Existing focused verification |
|---|---|
| URL security | `tests/unit/web_knowledge/test_url_security.py` |
| Bounded fetch and redirects | `tests/unit/web_knowledge/test_httpx_fetch_provider.py` |
| Search/fetch service | `tests/unit/web_knowledge/test_web_knowledge_service.py` |
| API/bootstrap | `tests/integration/web/test_web_search_web_app.py` |
| Existing web panel | `frontend/src/components/WebSearchPanel.test.tsx` |
| Existing setting integration | `frontend/src/components/SettingsModal/SettingsModal.test.tsx` |

No test, build, lint, or source mutation has occurred before this freeze. The preflight baseline remains the authoritative entry evidence: backend web knowledge 64 passed and `WebSearchPanel` 6 passed.

## Status

| Item | State |
|---|---|
| Completed CP | CP8-01–03 |
| Changed paths | Recovery Index 1–3 only |
| P8-A acceptance | P8-ACC-001 preserved by boundary; P8-ACC-002–012, 039 pending |
| Open findings | None |
| Active process or temporary artifact | None |
| Do not repeat | P8-0 mapping and authority/test freeze |
| Exact next CP | CP8-04 / P8-A-WU-001/002 |
