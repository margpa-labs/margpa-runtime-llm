# Phase 2-C Design Conformance Review

```yaml
document_id: phase_2_c_design_conformance_review_20260814031257
status: completed
phase: phase_2
subphase: phase_2_c
reviewed_at: 2026-08-14 03:12:57 JST
from: Phase 2設計担当者役
to: プロジェクト責任者兼設計統括者役
result: PARTIAL
closure_recommendation: ADJUST
```

## 1. Review Scope

Phase 2-CのFrozen Requirements／Architecture／ADR／Implementation Handoff／Acceptance Matrix、Design Freeze Receipt、Implementer Status、Allowed Source／Testを独立照合した。Forbidden PathのPhase 2-C Mutation、Project Root `runtime_data/`、Git／Network／External Mutationは検出していない。

Independent Validation:

```text
Target Tests
45 passed in 0.87s

Conversation / Web Regression
172 passed in 1.59s

Ruff Check
All checks passed

Ruff Format Check
146 files already formatted

Mypy
Success: no issues found in 104 source files

Project Root runtime_data
absent
```

## 2. Findings

### P2C-REV-001 — HIGH — Capability確定前にv1 Ephemeral Sendが可能

Affected acceptance:

```text
P2C-API-004
P2C-UX-002
Persistent Browser / Server Source-of-truth Cutover
```

Evidence:

- `src/margpa_runtime_llm/web/static/index.html`のSendは初期状態でEnabled。
- `src/margpa_runtime_llm/web/static/app.js`の`state.persistentEnabled`は初期`false`。
- `loadRuntime()`と`loadPersistentRuntime()`は非同期で個別開始され、Capability応答前の`sendMessage()`は`/api/v1/chat/stream`へ送信する。
- v2 Runtime／List取得失敗時も`persistentEnabled=false`へ戻るため、Persistent Runtimeであるかを確定できない状態がEphemeral v1へSilent Fallbackし得る。

Impact:

Persistent opt-in RuntimeでBrowserがServer Source of TruthのCapability Negotiationを完了する前に一時Conversationを開始できる。そのTurnはPersistent Historyに入らず、利用者の期待とSource-of-truth Cutoverが一致しない。

Required Implementer Rework:

```text
src/margpa_runtime_llm/web/static/index.html
src/margpa_runtime_llm/web/static/app.js
tests/unit/web/test_persistent_static_contract.py
tests/integration/web/test_persistent_web_app.py  # API capability側の回帰確認が必要な場合のみ
```

Browser Bootを`capability_pending / persistent / ephemeral / capability_failed`相当の明示状態で管理し、v2 Capabilityが200で`enabled=false`と確定した場合だけExisting v1をEnabledにする。Pending／Fetch Failure／Persistent List Initial Load Failureでv1 SendへFallbackしない。初期DOMとEvent Handlerの両方でFail-closedし、RaceをTestで固定する。

### P2C-REV-002 — HIGH — Durable Commitなしの`error` Terminal SSE

Affected acceptance:

```text
P2C-STR-002
P2C-STR-003
```

Evidence:

- `project_persistent_event()`では`completed / cancelled / error`の全TerminalをRepository再Read／Durable State／`durable_revision`付きで投影している。
- 一方、`PersistentSseBridge._produce()`はStart公開後のProjection／Terminal Persistence Exception時に、RepositoryのDurable Failed Commitを確認せず`event: error`と`terminal_persistence_failed`を直接Queueへ入れる。このEventに`durable_revision`はない。
- Fault Injection Testは`completed`がないことだけを確認し、Durableでない`error` Terminalを許容している。

Impact:

Frozen Contractは`error`をTerminal Eventと定義し、Durable Commit／Exact Receipt後だけ公開する。現実装はTerminal Persistence Failureでまさにその前提を満たさない`error`を公開するため、BrowserがDurable TerminalとTransport／Persistence Failureを識別できない。

Required Implementer Rework:

```text
src/margpa_runtime_llm/web/persistent_streaming.py
src/margpa_runtime_llm/web/static/app.js
tests/integration/web/test_persistent_web_app.py
tests/unit/web/test_persistent_static_contract.py  # Browser EOF収束Contractを追加する場合
```

Terminal Persistence／Projection Failure時は`completed / cancelled / error`のどのTerminal Eventも公開せずStreamを終了する。BrowserはDurable TerminalなしのEOFをSafe Failureとし、Server Detailを再Readする。Fault Injectionは`event: completed`だけでなく`event: cancelled`と`event: error`も0、Durable Revision付きTerminalも0、Ephemeral Assistant Persistenceも0であることを確定する。

### P2C-REV-003 — MEDIUM — Acceptance Evidenceの一部がClaimに届いていない

Affected acceptance:

```text
P2C-EXP-003
P2C-CMP-002
P2C-UX-001
```

Evidence:

- Source Review上、Public／Basic通常起動のPersistence Settingsは`None`、v1 RouteはPersistent Serviceを呼ばない。ただしAcceptance Matrixが要求するBuild／Read／Write Call 0およびv1 Persistent Call 0のSpy Testは追加Test内に存在しない。
- Implementer Statusは`P2C-UX-001 PASS (automated DOM...)`とするが、`test_persistent_static_contract.py`はSource String／CSS Presence Scanであり、DOM Event Interaction Testではない。StatusのKnown LimitationsでReal Browser Matrix未実施も明記されている。

Required route:

```text
Implementer:
  tests/unit/web/test_web_cli.py
  tests/integration/web/test_persistent_web_app.py
  tests/unit/web/test_persistent_static_contract.py

Controller / User Acceptance:
  Local Private Browserのja/en・New/List/Open/Resume/Stop/Retry/Regenerate/Branch/
  Reload/Multi-browser Conflictを最終Manual Matrixで確認
```

Public／Basic Normal Startとv1 ChatにStore SpyをBindingし、Build／Read／Write Call 0を直接証明する。Automated DOMと称するなら、Capability Pending／Enabled／Disabled／Failureと主要ActionのEvent Interactionを実行する。実行環境を増やさない場合はStatic Contractと正確に表記し、Real Browser MatrixをController／User Gateとして残す。

## 3. Acceptance Disposition

```text
PASS:
  P2C-EXP-001, P2C-EXP-002
  P2C-CMP-001
  P2C-API-001, P2C-API-002, P2C-API-003, P2C-API-005
  P2C-IDM-001, P2C-IDM-002
  P2C-LIF-001, P2C-LIF-002
  P2C-STR-001, P2C-STR-004
  P2C-BRN-001, P2C-BRN-002, P2C-BRN-003, P2C-BRN-004, P2C-BRN-005
  P2C-CAS-001
  P2C-PRV-001, P2C-PRV-002, P2C-PRV-003
  P2C-UX-002 (Existing disabled-mode source/regression only)
  P2C-QA-001, P2C-QA-002, P2C-QA-003, P2C-QA-004, P2C-QA-005

PARTIAL / REWORK:
  P2C-API-004, P2C-STR-002, P2C-STR-003, P2C-CAS-002
  P2C-EXP-003, P2C-CMP-002, P2C-UX-001
```

`P2C-BRN-005`はExplicit Test Nameではないが、`select_branch_head()`がCanonical `head_turn_id`だけをCAS更新し、後続`append_user_turn()`がそのHeadをParentにし、Frozen Phase 2-B Context MapperがParent Chainだけを生成Contextへ投影することをSource Reviewで確認した。Reworkで専用Regressionを追加するのが望ましい。

## 4. Boundary Result

```text
Forbidden Domain / Port / Existing v1 implementation mutation : 0 detected
Public / Basic persistent composition in normal settings       : 0 by source review
Project Root runtime_data                                      : absent
Client full-history / scope / path fields                       : rejected
Browser conversation text storage                              : 0 by static scan
Recorder binding / call                                        : 0
Thread-affine persistent iterator iteration / close             : PASS
Git / Network / External mutation by Designer review            : 0
```

## 5. Closure Recommendation

`ADJUST`.

Phase 2-CをまだClosedにしない。Phase 2実装者役へP2C-REV-001／002のSource／Test ReworkとP2C-REV-003のAutomated Evidence補強を返し、同じFrozen Designに対するFinal Conformance Re-reviewを行う。Real Browser MatrixはSource Rework後のController／User Acceptance Gateとして分離する。
