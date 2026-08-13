# Phase 2-C Persistent Conversation API／UX Implementation Handoff

```yaml
handoff_id: phase_2_c_persistent_conversation_api_ux_implementation
status: accepted_and_frozen_for_implementer
phase: phase_2
subphase: phase_2_c
created_at: 2026-08-14 JST
from_role: Phase 2設計担当者役
to_role: Phase 2実装者役
review_return_to: Phase 2設計担当者役
final_review: プロジェクト責任者兼設計統括者役
```

## 1. Objective

Phase 2-BのPersistent Serviceを、Separate `/api/v2/conversations/**`とServer-owned Browser UXへBindingする。Local／Loopback／Explicit opt-inだけを許可し、Existing v1は無変更／Storage Write 0、Public Demo／Shared Basic PreviewはPersistent Adapter Unbound／Write 0とする。

## 2. Mandatory Inputs

- [Requirements](../requirements/phase_2_c_persistent_conversation_api_ux_requirements_ja.md)
- [Architecture](../architecture/phase_2_c_persistent_conversation_api_ux_architecture_ja.md)
- [ADR](../adr/phase_2_c_persistent_conversation_api_ux_adr_ja.md)
- [Acceptance Matrix](../operations/phase_2_c_acceptance_matrix_ja.md)
- Phase 2-B Frozen Package／Source／Tests／Final Review／Controller Closure
- Existing Web `contracts.py`／`app.py`／`streaming.py`／Static Assets／Tests
- Existing Access Profile／Auth／Bind Validation Contract

局所矛盾は実装前にDesignerへ返す。Scope拡張、Public／Basic Binding、Domain／Port変更で回避しない。

## 3. Write Lease／Allowed Paths

Implementation Source：

```text
src/margpa_runtime_llm/modules/conversation/application/
  persistent_conversation_service.py                 MODIFY
  persistence_models.py                              MODIFY if safe error/action contract needed
  __init__.py                                        MODIFY if export required

src/margpa_runtime_llm/modules/conversation/adapters/
  persistence_factory.py                             MODIFY only for explicit startup/open composition

src/margpa_runtime_llm/web/
  persistent_contracts.py                            NEW
  persistent_routes.py                               NEW
  persistent_streaming.py                            NEW
  contracts.py                                       MODIFY optional persistent composition only
  app.py                                             MODIFY v2 router/lifespan/request-size gate only
  static/index.html                                  MODIFY capability-gated persistent UX
  static/app.js                                      MODIFY capability-gated persistent UX
  static/app.css                                     MODIFY persistent UX styling

src/margpa_runtime_llm/bootstrap/web_application.py  MODIFY opt-in composition only
src/margpa_runtime_llm/entrypoints/web/main.py        MODIFY minimal Local-only CLI opt-in only
```

Tests：

```text
tests/unit/conversation/test_persistent_conversation_actions.py NEW
tests/unit/web/test_persistent_web_contracts.py                  NEW
tests/unit/web/test_persistent_static_contract.py                NEW
tests/integration/web/test_persistent_web_app.py                 NEW
tests/unit/web/test_web_cli.py                                   MODIFY Local opt-in rejection/startup
```

Evidence：

```text
docs/project/phases/phase_2/history/handoffs/
  implementer_status_phase_2_c_<timestamp>.md         NEW exactly one
```

追加Pathが必要なら無断拡張せず、Exact Path、理由、代替案をDesignerへ返す。

## 4. Forbidden Paths／Actions

```text
src/margpa_runtime_llm/modules/conversation/domain/**
src/margpa_runtime_llm/modules/conversation/ports/**
src/margpa_runtime_llm/modules/conversation/contracts.py
src/margpa_runtime_llm/modules/conversation/public.py
src/margpa_runtime_llm/modules/conversation/application/conversation_generation.py
src/margpa_runtime_llm/web/access_profiles.py
src/margpa_runtime_llm/web/auth.py
src/margpa_runtime_llm/web/streaming.py
src/margpa_runtime_llm/web/error_mapping.py
config/**
scripts/**
pyproject.toml
uv.lock
.gitignore
Existing Stable／Frozen Docs／History
Project Root runtime_data/**
Repository外Path
```

Existing `/api/v1/**`のRoute Body／Contract／SSE／Static Ephemeral Behaviorを変更しない。Git Mutation、Network、Package Install、External Service、Permission変更、Existing File削除、Production Runtime起動を行わない。

## 5. Implementation Sequence

### C1. Application Actions

1. Retry／RegenerateのSource State／Parent／User Content／Revisionを検証する。
2. Existing Normal Generation Pathを再利用するDerived Turn Actionを追加する。
3. Completed TurnだけをHeadにするCAS Branch Selectionを追加する。
4. Current Generating Turn／Request ID一致後のCancel Delegationを追加する。

### C2. v2 Contracts／Routes

1. Exact Request／Response／Safe Error／SSE Projectionを作る。
2. Server Scope固定、Operation IDのDomain-separated Mappingを実装する。
3. Runtime／List／Create／Detail／Resume／Archive／Unarchiveを実装する。
4. Normal／Retry／Regenerate Stream、Branch Select／Stopを実装する。
5. Persistent Errorを局所でSafe HTTPへ写像する。v1 Error Mappingは変えない。

### C3. Composition

1. Optional Persistent CompositionをWeb Runtimeへ追加する。Default NoneでExisting Test Constructorを保つ。
2. Local／Loopback／Auth DisabledをFilesystem Mutation前にDouble-checkする。
3. Explicit Root／ScopeだけでBuild／Initialize or Open／Recovery Gateを実行する。
4. CLIは`--conversation-persistence`、`--conversation-runtime-data-root`、`--conversation-scope-id`の最小入力に限定する。Config Fileを変更しない。

### C4. Browser UX

1. v2 Runtime CapabilityをProbeし、DisabledならExisting Ephemeral Modeを維持する。
2. EnabledならList／Detail／New／Resume／Archive／Branch Actionを提供する。
3. Turn BodyにFull Historyを入れず、`content + settings + operation_id + expected_revision`だけを送る。
4. Terminal／Conflict／Reload後はDetail再ReadでDOMを丸ごと再構成する。
5. StopはCancel Request後にDurable Terminalを待ち、AbortをFallbackにする。
6. ja／en文言、Keyboard／Focus／Mobile Layout、Existing Copy／Markdown／Thinking／RAG表示を回帰確認する。

## 6. Required Technical Rules

- Persistent Requestに`messages[]`／`history`／`scope_id`／Filesystem Path Fieldを設けない。
- v2 Data RouteはPersistent Composition NoneでStore Call 0のUnavailableを返す。
- Action IDからInternal IDを決定的に導出する。Applied済みAction IDの再送はBodyの同異にかかわらず409／新Mutation 0とし、SSEをReplayまたは新IDで再開始しない。
- 全MutationはExpected RevisionをServer CASへ渡す。Conflictを自動Mergeしない。
- Derived TurnはSource User Content／ParentをServer Snapshotから複製し、Client Replacement Contentを受け取らない。
- Generation中にDB Connection／Transaction／Lockを保持しない。
- Durable Terminal Commit前にTerminal SSEを渡さない。
- Async／Sync Stream BridgeはBounded Queue／Keepalive／Thread-affine Cleanupを維持する。Existing `streaming.py`を変更せず、v2専用Adapterで等価Contractを作る。
- Browser StorageにConversation本文を保存しない。
- Thinking／Prompt／RAG Context／Citation本文／Partial／Hidden Original／SecretをDB／API／Browser Storageへ残さない。
- RecorderはOFF／Unbound／Call 0。

## 7. Required Tests

- Startup Matrix：Local enabled／disabled、Public／Basic／Non-loopback rejection、Store Build前Failure。
- v2 Contract：Extra／Oversize／Malformed／Scope Field不存在／Safe Error。
- List／Create／Detail／Resume／Archive／Unarchive／Pagination。
- Internal Operation Receipt収束／Applied Action ID再送のMutation 0／Response Loss後Detail Recovery。
- Normal SSE／Stop／Disconnect／Terminal Persistence Failure／Exact Receipt。
- Retry Allowed／Rejected States、Regenerate Branch Preservation、Branch Select／Selected Context。
- Multi-client Stale Revision／409／Mutation 0／Detail Refresh。
- Browser Source-of-truth：Full History Payload 0、Browser Storage本文 0、Terminal／Conflict後GET。
- Sensitive SentinelがDB／Response／Static Storage 0。
- Existing v1／Public／Basic／Auth／Static Security／CLI Regression。
- Test Rootは`tmp_path`だけで、Project Root `runtime_data/` 0。

## 8. Validation Commands

```bash
.venv/bin/pytest -q \
  tests/unit/conversation/test_persistent_conversation_actions.py \
  tests/unit/web/test_persistent_web_contracts.py \
  tests/unit/web/test_persistent_static_contract.py \
  tests/integration/web/test_persistent_web_app.py \
  tests/unit/web/test_web_cli.py

.venv/bin/pytest -q \
  tests/unit/conversation \
  tests/integration/conversation \
  tests/unit/web \
  tests/integration/web

.venv/bin/ruff format --check src tests
.venv/bin/ruff check src tests
.venv/bin/mypy
.venv/bin/pytest -q
```

Static Node TestがEnvironment上利用可能ならExisting Commandも実行する。Node不在のSkipは既存Contractに従い、Python Static Contractでv2 Source-of-truth／Storage禁止を必ず検証する。

## 9. Boundary Evidence

Implementer Statusに少なくとも次を記録する。

```text
Changed paths: exact list
Acceptance IDs: PASS / FAIL
Target / Regression / Static / Full results
Existing v1 source/wire mutation: 0 / exact finding
Public / Basic persistent build/read/write: 0 / exact finding
Client full-history payload: 0 / exact finding
Scope accepted from HTTP: 0 / exact finding
Sensitive DB/API/browser persistence: 0 / exact finding
Project Root runtime_data: absent / exact finding
Recorder binding/call: 0 / exact finding
Known limitations / rollback
```

## 10. Return Route

```text
From   : Phase 2実装者役
To     : Phase 2設計担当者役
Result : PASS | PARTIAL | BLOCKED
File   : implementer_status_phase_2_c_<timestamp>.md
```

DesignerがSource／Test／Statusを独立Reviewし、局所FindingをImplementerへ返す。Designer PASS後にだけControllerがClosure Reviewを行う。ImplementerはUserへ直接Completionを返さない。

## 11. Rollback

Rollback UnitはSection 3のAllowed Source／TestとImplementer Statusだけである。Phase 2-A Domain／Port、Existing v1 Contract／Generation／Streaming、Config／Script、Public／Basic ProfileをRollback対象へ含めない。

Testは`tmp_path`だけを使うため実Data Rollbackは発生しない。誤ってProject Root／Repository外にRuntime Artifactを作成した場合は削除せず停止し、Controller／Userへ報告する。

## 12. Completion

- Acceptance Matrix全Required PASS。
- Target／Regression／Static／Ruff／Mypy／Full PASS。
- Existing v1無変更、Public／Basic Binding／Write 0。
- Full-history Merge 0、Terminal-before-commit 0、Stale Merge 0。
- Sensitive Persistence 0、Recorder Call 0、Project Root Runtime Data 0。
- Designer Design Conformance PASS。
