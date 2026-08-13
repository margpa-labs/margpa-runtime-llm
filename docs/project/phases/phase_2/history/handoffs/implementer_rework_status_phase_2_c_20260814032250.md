# Phase 2-C Implementer Rework Status

- Timestamp: `2026-08-14 03:22:50 JST`
- From: Phase 2実装者役
- To: Phase 2設計担当者役
- Result: `PASS`
- Source Review: `phase_2_c_design_conformance_review_20260814031257`
- Rework Scope: `P2C-REV-001..003`

## 1. Rework Result

### P2C-REV-001 PASS

Browserの会話Modeを次の4状態で明示管理するよう変更した。

```text
capability_pending
persistent
ephemeral
capability_failed
```

SendはInitial HTMLでDisabledとし、Event Handlerはv2 RuntimeがHTTP 200、`source_of_truth=server`、`enabled=false`と確定した場合だけv1 Ephemeralを許可する。Capability Pending／Fetch Failure／Malformed Capability／Persistent Initial List Failureはv1へFallbackせず、ComposerをFail-closedする。Initial Empty StateもCapability確認中とし、Mode確定後にPersistent／Ephemeralの説明へ切り替える。

### P2C-REV-002 PASS

Persistent SSE ProducerがStart公開後にTerminal PersistenceまたはProjection Failureを検出した場合、Synthetic `error`を含む`completed／cancelled／error`のどのTerminal SSEも公開せずEOFとする。BrowserはDurable Revision付きTerminalを観測せずEOFへ到達した場合、Safe Failure表示とServer Detail再Readへ収束する。

Fault InjectionはSuccess Terminal 0、Cancelled Terminal 0、Error Terminal 0、Terminal Durable Revision 0、Ephemeral Assistant Persistence 0、Canonical TurnのInterrupted収束を検証する。Start自体のDurable Revisionは保持する。

### P2C-REV-003 PASS with Manual Gate retained

- Public Demo／Basic PreviewのNormal CLI Compositionが`conversation_persistence_settings=None`であることを両Profileで直接検証した。
- Explicit SettingsなしのRuntime CompositionがPersistent BuilderをCallした場合にTestが失敗するSpyを追加した。これによりBuild／Read／Write Call 0を固定した。
- Public Demo／Basic PreviewのIn-process Normal Runtimeが`persistent_conversation=None`かつv2 Capability `enabled=false`であることを検証した。
- v1 Runtime／GenerationにPersistent Service Spyを配置し、Persistent Method Call 0を直接検証した。
- Browser EvidenceはSource Static Contractであり、Automated DOM Interactionとは扱わない。追加DependencyなしでJS構文と状態／Handler／EOF Contractを検証し、Real Browser MatrixはController／User Gateとして維持する。

P2C-BRN-005のDedicated Regressionも追加し、Branch Head選択後のNormal Turnが選択BranchのUser／Assistantと新UserだけをGeneration Contextへ投影し、選択されていないBranchを含まないことを検証した。

## 2. Exact Rework Paths

Source:

```text
src/margpa_runtime_llm/web/persistent_streaming.py
src/margpa_runtime_llm/web/static/index.html
src/margpa_runtime_llm/web/static/app.js
```

Tests:

```text
tests/unit/conversation/test_persistent_conversation_actions.py
tests/unit/web/test_persistent_static_contract.py
tests/integration/web/test_persistent_web_app.py
tests/unit/web/test_web_cli.py
```

Evidence:

```text
docs/project/phases/phase_2/history/handoffs/implementer_rework_status_phase_2_c_20260814032250.md
```

## 3. Acceptance Re-disposition

```text
P2C-REV-001 PASS
P2C-REV-002 PASS
P2C-REV-003 PASS

P2C-API-004 PASS (source/static and server integration)
P2C-STR-002 PASS
P2C-STR-003 PASS
P2C-CAS-002 PASS (source/static and server integration)
P2C-EXP-003 PASS
P2C-CMP-002 PASS
P2C-BRN-005 PASS (dedicated regression)
P2C-UX-001 AUTOMATED STATIC/API PASS; REAL BROWSER MANUAL GATE PENDING
```

## 4. Validation Results

```text
Target Tests
52 passed in 0.85s

Conversation／Web Regression
226 passed in 1.73s

JavaScript Syntax
node --check PASS

Static Node Security Contract
5 passed, 0 failed

Ruff Format
146 files already formatted

Ruff Check
All checks passed

Mypy
Success: no issues found in 151 source files

Full Suite
567 passed, 3 deselected in 58.41s

Project Root runtime_data
absent
```

## 5. Boundary Evidence

```text
Capability pending／failed -> v1 fallback                 : 0
Persistent initial list failure -> v1 fallback            : 0
Non-durable completed／cancelled／error terminal SSE        : 0
Terminal Persistence Failure assistant persistence        : 0
Public／Basic Normal persistent settings                    : None
Public／Basic Normal persistent build／read／write            : 0
v1 persistent service method calls                        : 0
Selected-head context inclusion of unselected branch      : 0
Project Root runtime_data                                 : absent
Forbidden Path mutation                                   : 0
Git／Network／External／Package／Production runtime mutation : 0
```

## 6. Remaining Manual Gate

Local Private Browserでのja／en、New／List／Open／Resume／Stop／Retry／Regenerate／Branch／Reload／Multi-browser Conflictは、Source ReworkのDesigner Final Conformance PASS後にController／User Acceptanceで確認する。これは未実装Blockerではなく、Real Browser Acceptance Gateである。

## 7. Rollback

Rollback UnitはSection 2のSource／Testと本Rework Statusのみである。Phase 2-B Persistence、Phase 2-C初回実装のその他Source／Test、Existing v1、Public／Basic Profile、Config／ScriptはRollback対象に含めない。

## 8. Review Request

Phase 2設計担当者役はP2C-REV-001..003と関連AcceptanceをFrozen Designへ再照合し、Final Conformanceの`PASS | REWORK | BLOCKED`を判定してください。
