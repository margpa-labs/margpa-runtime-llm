# Phase 2-C Implementer Status

- Timestamp: `2026-08-14 03:06:37 JST`
- From: Phase 2実装者役
- To: Phase 2設計担当者役
- Result: `PASS`
- Scope: Phase 2-C Local Private Persistent Conversation API／UX

## 1. Implemented Contract

Phase 2-BのPersistent Conversation Serviceを、Local／Loopback／Explicit opt-inでのみ有効なSeparate `/api/v2/conversations/**`とServer-owned UXへBindingした。BrowserはList／Detail／RevisionをServerから再取得し、Full History、Scope、Runtime Data Path、Receipt、Hidden DataをMutation Requestへ含めない。

New Chat、List／Detail／Pagination、Archive／Unarchive／Resume、Normal Generation、Retry／Regenerate／Branch Select、Stop、Stale Revision Conflict、Applied Operation Replay、Durable Terminal SSEを実装した。Persistent SSEは、最初のGeneration StepからDisconnect時のIterator Closeまでを1つのProducer Threadが所有する。Terminal EventはCanonical Commit後のRepository再Readからのみ投影する。

Existing `/api/v1/**`のRoute Function／Request Contract／SSE Formatter／Cancel Contractは変更せず、v2用Request-size GateとOptional CompositionのみShared Web Appへ追加した。

## 2. Exact Changed Source Paths

Modified:

```text
src/margpa_runtime_llm/modules/conversation/application/persistence_models.py
src/margpa_runtime_llm/modules/conversation/application/persistent_conversation_service.py
src/margpa_runtime_llm/modules/conversation/adapters/persistence_factory.py
src/margpa_runtime_llm/web/contracts.py
src/margpa_runtime_llm/web/app.py
src/margpa_runtime_llm/web/static/index.html
src/margpa_runtime_llm/web/static/app.js
src/margpa_runtime_llm/web/static/app.css
src/margpa_runtime_llm/bootstrap/web_application.py
src/margpa_runtime_llm/entrypoints/web/main.py
```

New:

```text
src/margpa_runtime_llm/web/persistent_contracts.py
src/margpa_runtime_llm/web/persistent_routes.py
src/margpa_runtime_llm/web/persistent_streaming.py
```

No content change remains in `src/margpa_runtime_llm/modules/conversation/adapters/__init__.py`; the v2 startup helper is imported through its allowed concrete module by the Composition Root.

## 3. Exact Changed Test Paths

```text
tests/unit/conversation/test_persistent_conversation_actions.py
tests/unit/web/test_persistent_web_contracts.py
tests/unit/web/test_persistent_static_contract.py
tests/integration/web/test_persistent_web_app.py
tests/unit/web/test_web_cli.py
```

All filesystem-backed Test stores use `tmp_path`. No Test wrote Project Root `runtime_data/`.

## 4. Acceptance Matrix

```text
P2C-EXP-001 PASS
P2C-EXP-002 PASS
P2C-EXP-003 PASS
P2C-CMP-001 PASS
P2C-CMP-002 PASS
P2C-API-001 PASS
P2C-API-002 PASS
P2C-API-003 PASS
P2C-API-004 PASS
P2C-API-005 PASS
P2C-IDM-001 PASS
P2C-IDM-002 PASS
P2C-LIF-001 PASS
P2C-LIF-002 PASS
P2C-STR-001 PASS
P2C-STR-002 PASS
P2C-STR-003 PASS
P2C-STR-004 PASS
P2C-BRN-001 PASS
P2C-BRN-002 PASS
P2C-BRN-003 PASS
P2C-BRN-004 PASS
P2C-BRN-005 PASS
P2C-CAS-001 PASS
P2C-CAS-002 PASS
P2C-PRV-001 PASS
P2C-PRV-002 PASS
P2C-PRV-003 PASS
P2C-UX-001 PASS (automated DOM／API／ja-en／mobile contract)
P2C-UX-002 PASS
P2C-QA-001 PASS
P2C-QA-002 PASS
P2C-QA-003 PASS
P2C-QA-004 PASS
P2C-QA-005 PASS
```

## 5. Validation Results

```text
Target Tests
45 passed in 0.99s

Conversation／Web Regression
219 passed in 1.97s

Ruff Format
146 files already formatted

Ruff Check
All checks passed

Mypy
Success: no issues found in 151 source files

Static Node Security Contract
5 passed, 0 failed

Full Suite
560 passed, 3 deselected in 58.90s

Project Root runtime_data
absent
```

## 6. Boundary Evidence

```text
Existing v1 route／wire／SSE／cancel semantic mutation : 0
Public Demo persistent adapter binding／build／read／write : 0
Basic Preview persistent adapter binding／build／read／write : 0
Non-loopback persistent startup                            : fail-closed before runtime/store build
Client full-history payload                               : 0
HTTP-accepted Scope ID／Runtime Root／Storage Path             : 0
Scope／Path／Receipt exposure in safe response               : 0
Raw Thinking／System Prompt／RAG Context／Partial／Secret persistence : 0
Browser conversation-body storage                        : 0
Recorder binding／call                                    : 0
Terminal SSE before canonical commit                      : 0
Cross-thread generation iteration／close                    : 0
Project Root runtime_data                                 : absent
Repository-external write                                 : 0
Git／Network／Package install／Production runtime mutation        : 0
```

## 7. Known Limitations

- User-operated real Browser interaction matrix is not executed by the Implementer. Automated DOM, Static Contract, in-process HTTP／SSE integration, ja／en labels, and mobile layout contract are PASS; Designer／Controller may schedule manual acceptance separately.
- Rename／Search／Delete／Export, Settings Persistence, Research／Developer Mode, Concrete Recording, Encryption, Account／Remote Persistence, Cloud Sync, and General Configuration Framework remain outside Phase 2-C.
- Persistent SSE Replay Ledger is intentionally absent. Response loss converges through canonical Detail re-read; display-only Delta is not replayed or persisted.

## 8. Rollback

Rollback Unit is exactly the Source and Test paths in Sections 2 and 3 plus this Status file. Revert Modified paths to the Phase 2-B accepted snapshot and remove New paths. Do not roll back Phase 2-A Domain／Ports, Phase 2-B SQLite Store／Migration, Existing v1 Conversation Generation／Streaming, Config, Script, Public Demo, or Basic Preview.

No real runtime data migration or deletion is needed because Validation used only `tmp_path` and Project Root `runtime_data/` remained absent.

## 9. Review Request

Phase 2設計担当者役はFrozen Requirements／Architecture／ADR／Implementation Handoff／Acceptance Matrixに対し、Source、Tests、Boundary Evidence、Thread-affinity、Public／Basic Zero Bindingを独立Reviewし、`PASS | REWORK | BLOCKED`を判定してください。
