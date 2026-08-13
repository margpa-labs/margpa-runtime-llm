# Phase 2-C Persistent Conversation API／UX Architecture

```yaml
document_id: phase_2_c_persistent_conversation_api_ux_architecture
status: accepted_for_phase_2_c_implementation
phase: phase_2
subphase: phase_2_c
language: ja
created_at: 2026-08-14 JST
owner_role: Phase 2設計担当者役
```

## 1. Architecture Goal

```text
Local Private Browser
  -> /api/v2/conversations/**
  -> PersistentConversationWebAdapter
  -> PersistentConversationService
  -> SQLiteConversationStore

Existing Browser / Public / Basic
  -> /api/v1/**
  -> Existing ConversationGenerationService
  -> Persistence reference 0 / Write 0
```

Persistent APIはv1の後方互換拡張ではなく、別Prefix／別Contract／別Runtime Capabilityとする。UIはCapability Negotiation後にEphemeral v1 ModeまたはPersistent v2 Modeのどちらか一方を選び、一つのTurnで両方を併用しない。

## 2. Package Boundary

```text
modules/conversation/application/
  persistent_conversation_service.py   # add derived turn / head selection / cancel boundary
  persistence_models.py                # safe application contracts if required

web/
  persistent_contracts.py              # v2 exact request/response models
  persistent_routes.py                 # APIRouter and safe error mapping
  persistent_streaming.py              # persistent SSE projection / disconnect finalization
  contracts.py                          # optional Persistent composition in WebRuntime
  app.py                                # capability-gated router/lifespan only
  static/index.html
  static/app.js
  static/app.css

bootstrap/web_application.py            # build opt-in composition, no implicit path
entrypoints/web/main.py                 # minimal explicit Local CLI inputs
```

Domain／Port／Existing `conversation_generation.py`／Existing v1 ContractはFrozenとする。Retry／Regenerate／Branchは既存Domainの`origin`、`parent_turn_id`、`derived_from_turn_id`、`head_turn_id`の組合せで実現し、Domain ModelにWeb概念を追加しない。

## 3. Runtime Composition／Startup

CLIは次のMinimal opt-inだけをPhase 2-Cで追加できる。TOML Control Surfaceは2-Dへ延期する。

```text
--conversation-persistence             # absent = disabled
--conversation-runtime-data-root PATH  # enabled時必須／absolute
--conversation-scope-id VALUE          # enabled時必須／server-owned
```

Startup Sequence：

1. Access Profile／Hostを検証する。
2. Persistence disabledならCompositionをBuildせずv1を起動する。
3. Enabledなら`LOCAL + loopback + auth disabled`を再検証する。不一致はStore作成前にStartup Failureとする。
4. Explicit Root／ScopeでPhase 2-B FactoryをBuildする。
5. `EMPTY`だけをExplicit Initialize、`READY`だけをOpenする。Migration Required／Incomplete／Unsupported／CorruptはStartup Failureとし、暗黙Migrationしない。
6. `recover_incomplete_conversations()`完了後にだけv2 Readyとする。
7. Shutdown時はActive Persistent Streamを有界にStop／Interruptし、既存Model Runtimeを一度だけCloseする。

`WebRuntime`のPersistent CompositionはOptionalで、Existing ConstructorはDefault `None`として後方互換を保つ。App FactoryもOptional Bindingを受けるが、Public／BasicでNon-NoneならFail-closedする。

## 4. API Projection

### 4.1 Capability

`GET /api/v2/conversations/runtime`は次のSafe Metadataだけを返す。

```json
{
  "enabled": true,
  "api_version": "2",
  "source_of_truth": "server",
  "features": ["list", "resume", "retry", "regenerate", "branch"]
}
```

Disabled時は`enabled=false`と空Featureに限定し、Path／Scope／Schema／Record Countを出さない。

### 4.2 List／Detail

ListはRepository Keyset CursorをOpaqueのまま通し、Summaryに`storage_revision`を付与するため、AdapterがSummaryごとに無制限Full DetailをN+1 Readしない構造とする。Phase 2-B Portを変更せず必要な場合は、List ResponseのRevisionを省略し、Mutation前のDetail GETを必須とする。Port変更で解決しない。

Detail Projection：

```text
conversation_id, state, head_turn_id, storage_revision, created_at, updated_at
sessions: session_id, state, opened_at, finished_at
turns: turn_id, sequence, state, origin, parent_turn_id,
       derived_from_turn_id, request_id, started_at, finished_at,
       canonical user message, canonical assistant message if completed
```

Scope ID、Last Operation ID、Receipt、Storage Version／PathはWeb Projectionから除外する。

## 5. Operation Identity Mapping

Client `operation_id`はTransport Idempotency Identityであり、Serverは次のDomain Separation相当でInternal Identityを導出する。

```text
sha512("margpa-persistent-web-v2\0" + kind + "\0" + client_operation_id)
```

`kind`は`conversation／session／turn／user-message／assistant-message／append／start／terminal／resume／archive／head-select`等のSource定数である。Digestを各Domain IDの文字数Contractに合わせる。Client InputをPath／SQL Identifierへ使わない。

Storage内部の段階別OperationはPhase 2-BのSame Command Receiptへ収束させる。HTTP Action IDはSSE Replay Ledgerではない。Derived Conversation／Turn／Operationが既に適用済みなら、Bodyの同異にかかわらず新しいMutation／Generationを開始せず、`409 operation_already_applied`と最新Detailへの再Read指示を返す。SSE全EventのReplay保存は行わない。

## 6. Application Actions

Persistent Serviceに次のFramework非依存Actionを局所追加する。

- `append_derived_turn(source_turn_id, origin, identities, expected_revision)`：SourceのState／User／Parentを再検証し、Retry／Regenerate用Pending TurnをCommit。
- `generate_derived_turn(...)`：Derived Pending後はNormalと同じMapper／Generation／Terminal Persistenceを使う。コピーした別Orchestratorを作らない。
- `select_branch_head(completed_turn_id, operation_id, expected_revision)`：Completed TurnだけをHeadへCAS Commit。
- `cancel_active_generation(conversation_id, request_id, expected_revision)`：RepositoryのCurrent Revision／Generating Turn／Request ID一致を確認してからExisting Generation ServiceへCancelを委譲。

ApplicationはClient Full Historyを受け取らず、Repository Snapshotを必ず読む。Derived ActionはSource Turnを上書き／削除しない。

## 7. Persistent SSE

Persistent AdapterはPhase 1 SSEと同じFraming Ruleを再利用するが、v2 Event Contractは別とする。

```text
start      : conversation_id, turn_id, request_id, durable_revision
retrieval  : existing safe citation metadata only
status     : display-only state
delta      : channel + text; never canonical persistence source
warning    : safe code/message
completed  : canonical assistant, durable_revision, head_turn_id
cancelled  : durable_revision
error      : safe code/message, durable_revision
conflict   : safe code, current_revision when safe
```

Persistent ServiceがTerminal Commit後にYieldしたEventだけをTerminal SSEへ変換する。AdapterはDeltaをDBへ書かない。Terminal Event生成時にRepositoryを再Readし、Durable Revision／HeadとCanonical Assistantを確定する。読取り失敗はTerminal公開前にFail-closedする。

Client DisconnectでAsync GeneratorがCloseされたら、Sync Iteratorを生成ThreadでCloseし、Phase 2-Bの`finally`によるInterrupted Commitを完了させる。Cross-thread Native Cancelを行わない。

## 8. Browser State Machine

```text
BOOT
 -> GET v2 runtime
 -> disabled: EPHEMERAL_V1
 -> enabled : PERSISTENT_LIST

PERSISTENT_LIST
 -> select -> GET detail -> READY
 -> new    -> POST create -> READY

READY
 -> send/retry/regenerate -> STREAMING
 -> select branch         -> CAS -> GET detail
 -> stale conflict        -> CONFLICT -> GET detail -> READY

STREAMING
 -> transient delta only
 -> terminal durable event -> GET detail -> READY
 -> disconnect             -> server interrupt -> GET detail on reconnect
```

- v2 Modeで`state.messages`をRequest Historyとして使わない。DOMはServer Detailから毎回構築する。
- SidebarはListとStable Pagination、Main PaneはSelected Detailを表示する。Message本文から自動TitleをStoreに書かず、Phase 2-CのList LabelはTimestamp／Short IDのSafe Metadataでよい。
- Retry／Regenerate／Branch ButtonはServer DetailのStateから決める。非表示はAuthorizationの代替ではない。
- StopはServer Requestを送りTerminalを待つ。AbortはNetwork Failure／Timeout用Fallbackである。
- UI Language／Generation Settingsは今回もBrowser-localで、Conversation Recordへ永続保存しない。

## 9. Conflict／Failure Handling

| Failure | HTTP／SSE | Browser action |
|---|---|---|
| stale revision | 409 `revision_conflict` | Detail再Read／自動Merge 0 |
| invalid source turn | 409 `invalid_lifecycle` | Detail再Read |
| unknown conversation | 404 `not_found` | List再Read |
| persistence disabled | 404 `persistent_conversation_unavailable` | v2を使用しない |
| storage not ready | 423 | Mutation 0／Ephemeral fallback 0 |
| terminal persistence failure | SSE成功Terminal 0／5xx | Detail再Read・安全Status |
| disconnect | stream close | Server interrupt／次回Detail再Read |

Unexpected ErrorはGlobal Safe Handlerへ渡し、Raw ExceptionをWireへ出さない。

## 10. Compatibility Boundary

- v1 Route Function／Contract／SSE Formatterはv2のために変更しない。Shared Security Header Middlewareのv2 Request SizeとNo-storeを追加できるが、v1 Limitを変更しない。
- Static AssetはPublic／Basicと共有でも、v2 Capability disabledなら従来Ephemeral UIだけを表示する。Public／BasicのBrowserからPersistence Data Routeを直接呼び出してもUnavailableとする。
- Public／BasicのRegressionはAdapter Factory Spy、Filesystem Inventory、Route ResponseでBuild／Read／Write 0を検証する。

## 11. Deferred to 2-D

TOML Schema、Settings UI、Apply／Restart Boundary、Research／Developer Mode、Recording Mode、Advanced Context Policy、Component Enable／Disableは2-Dで扱う。Phase 2-CのCLI opt-inをGeneral Configuration Frameworkとみなさない。

## 12. Related Documents

- [Requirements](../requirements/phase_2_c_persistent_conversation_api_ux_requirements_ja.md)
- [ADR](../adr/phase_2_c_persistent_conversation_api_ux_adr_ja.md)
- [Implementation Handoff](../handoffs/phase_2_c_implementation_handoff_ja.md)
- [Acceptance Matrix](../operations/phase_2_c_acceptance_matrix_ja.md)
