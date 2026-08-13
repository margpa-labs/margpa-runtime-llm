# Phase 2-C Persistent Conversation API／UX Requirements

```yaml
document_id: phase_2_c_persistent_conversation_api_ux_requirements
status: accepted_for_phase_2_c_implementation
phase: phase_2
subphase: phase_2_c
language: ja
created_at: 2026-08-14 JST
from_role: Phase 2設計担当者役
to_role: Phase 2実装者役
decision_authority: project_controller_and_user
```

## 1. Objective

Phase 2-BのLocal Conversation Persistenceを、Loopback-only Local Private Surfaceに限って別VersionのHTTP APIとBrowser UXへ明示Bindingする。Chat List／History／New Chat／Resume、Streaming／Stop、Retry／Regenerate／Branch SelectionおよびMulti-browser CAS Conflictを、Server Repositoryを唯一のSource of Truthとして提供する。

Existing `/api/v1/**`は一時Conversation APIとしてWire／Source／動作を変更せず、Persistence Call／Write 0を維持する。Public DemoとShared Basic PreviewにPersistent AdapterをBindingしない。

## 2. Scope

### In Scope

- `/api/v2/conversations/**`のVersioned Persistent API。
- Local Private専用のExplicit opt-in Binding。
- Conversation List、Canonical History、New Chat、Reload後Resume。
- Normal TurnのSSE Streaming／Stop／Disconnect収束。
- Failed／Cancelled／Interrupted TurnのRetry、Completed TurnのRegenerate、Completed Branch Headの明示Selection。
- BrowserとServerのSource-of-truth Cutover。
- Revision CASによるMulti-tab／Multi-browser Conflict。
- Local Private用の最小CLI opt-in入力。

### Out of Scope

- Config Control Surface、Research／Developer Mode、Component Switchboard。
- Public Demo／Basic PreviewへのPersistence、Account、Multi-user Identity。
- Client History Import、Client／Server History Merge、Offline Queue。
- Rename／Search／Delete／Purge／Retention／Export／Import。
- Raw Thinking／Prompt／RAG Context／Citation本文／Partial／Hidden Original／Secretの保存。
- Concrete Recording、Encryption、Cloud／Multi-host Store。

## 3. Exposure／Authentication／Scope Boundary

- Persistent Bindingは`WebExposureMode.LOCAL`、Authentication disabled、Loopback Bindの3条件を全て満たす場合だけ許可する。LocalのAuthentication disabledはPublic公開を意味せず、OS UserとLoopback TransportがPhase 2-CのTrust Boundaryである。
- `basic_preview`のShared CredentialはUser IdentityではないためPersistent Scopeを与えない。`public_demo`のCredentialless Non-loopback SurfaceにもPersistent Scopeを与えない。
- Persistent opt-inがPublic／Basic／Non-loopbackと同時に指定された場合はStartupをFail-closedする。Disabled Persistenceは従来Surfaceをそのまま起動する。
- `scope_id`とRuntime Data RootはServer-ownedのExplicit Startup Inputであり、HTTP Request／Cookie／Browser Storage／URLから受け取らない。ResponseにScope IDを露出しない。
- Persistent Data RouteはBindingがない場合`404 persistent_conversation_unavailable`とし、StoreをBuild／Inspect／Initializeしない。Capability Routeは`enabled: false`だけを返してもよいが、Record／Path／Scopeの存在を示さない。

## 4. Versioned API Contract

Persistent API Prefixを`/api/v2/conversations` に固定する。Request／Responseは`extra=forbid`のTyped Contractとし、Path ID／Operation ID／Cursor／Content／Request Sizeに上限を設ける。

```text
GET  /api/v2/conversations/runtime
GET  /api/v2/conversations?state=&cursor=&limit=
POST /api/v2/conversations
GET  /api/v2/conversations/{conversation_id}
POST /api/v2/conversations/{conversation_id}/resume
POST /api/v2/conversations/{conversation_id}/archive
POST /api/v2/conversations/{conversation_id}/unarchive
POST /api/v2/conversations/{conversation_id}/turns/stream
POST /api/v2/conversations/{conversation_id}/turns/{turn_id}/retry/stream
POST /api/v2/conversations/{conversation_id}/turns/{turn_id}/regenerate/stream
POST /api/v2/conversations/{conversation_id}/branches/{turn_id}/select
POST /api/v2/conversations/{conversation_id}/generations/{request_id}/stop
```

- Repository Mutation Requestは`operation_id`と`expected_revision`を必須とする。Createの`expected_revision`だけ`null`とする。StopはRepository Commandではないが、`request_id`とBrowserがStart Eventで受け取ったGenerating Revisionを必須とし、ServerのCurrent Generating Turnと一致する場合だけCancelを委譲する。
- BrowserはCryptographically randomなAction IDをMutationごとに作る。Serverは内部Turn／Message／Session／段階別Operation IDをDomain-separated Digestで決定的に導出し、Clientに内部ID発番を委任しない。Applied済みAction IDのHTTP再送は新しいMutation／Generationを開始せず、`operation_already_applied`とDetail再Readへ収束する。SSE Event Replayは行わない。
- List ResponseはID、State、Head、Created／Updated Time、RevisionとOpaque Cursorに限定し、Message本文、Scope、Operation Receipt、Pathを含めない。
- Detail ResponseはCanonical User／Assistant Message、Turn State／Origin／Branch Relation、Session State／Time、Head、Storage Revisionだけを返す。Prompt／Thinking／RAG Context／Partial／Raw Failureを返さない。
- ErrorはTyped Safe JSONとし、`404 not_found`、`409 revision_conflict`、`409 invalid_lifecycle`、`422 invalid_request`、`423 storage_not_ready`、`503 storage_unavailable`等を区別する。Raw Path／SQL／Driver Text／Record本文を含めない。

## 5. Server Source of Truth

- Persistent ModeでBrowserが保持できるCanonical Stateは、選択Conversation ID、最徏Revision、List Cursor、Active Request IDの参照に限定する。Conversation History本文を`localStorage`／`sessionStorage`／IndexedDBへ保存しない。
- Turn Mutation Requestに過去Message配列を受け取らない。ClientはCurrent User ContentとSettingsだけを送り、HistoryはServer RepositoryからContext Mapperが構成する。
- Browser Reload、Conversation選択、Terminal EventおよびConflict後はDetail GETを行い、Server Projectionで全再描画する。Browser側の過去HistoryをRepositoryへ送信／Mergeしない。
- Optimistic Displayは非Canonicalと明示的に扱い、Server AcceptanceまたはConflict後に破棄する。Terminal表示はDurable Commit後のEventとGET Projectionで確定する。

## 6. Lifecycle／Streaming／Stop

- New ChatはServerにConversationとActive Sessionを作成し、返却RevisionをBrowserの基準とする。DBへ接続できない場合にEphemeral ChatへSilent Fallbackしない。
- History OpenはDetailをReadするだけでWriteしない。Active Sessionがない場合だけ、明示ResumeがCAS Commitで新Sessionを作る。旧Sessionを再Openしない。
- SSEは最初の`start`でConversation／Turn／Request IDとDurable Generating Revisionを返す。Delta／Retrieval／WarningはDisplay-onlyでありBrowser HistoryのCanonicalとしない。
- `completed／cancelled／error`のTerminal SSEはPhase 2-BのTerminal Commitが成功またはExact Receiptで収束した後だけ公開する。Terminal EventはDurable Revisionを含み、BrowserはDetailを再Readする。
- StopはServer Cancelを要求し、Browserは可能な限りDurable Terminal EventまでConsumeする。Bounded TimeoutまたはNetwork切断時のAbortはIterator Closeを通じ`interrupted`へ収束する。

## 7. Retry／Regenerate／Branch

- Retryは`failed／cancelled／interrupted`のSource Turnに限り、同じCanonical User Content、同じ`parent_turn_id`、`origin=retry`、`derived_from_turn_id=source`の新Turnを追加する。ClientからReplacement Contentを受け取らない。
- Regenerateは`completed`のSource Turnに限り、同じUser Content／Parentと`origin=regenerate`の新Turnを追加する。完了後のHeadは新Turnとし、Source Branchは削除／上書きしない。
- Branch Selectは既存のCompleted Turnを新HeadとするCAS Commitであり、Message／Turnの追加や再生成を行わない。選択後のNormal Turnは新HeadをParentとする。
- Derived TurnまたはBranch Selectionに対し、Sourceの存在、State、Parent、RevisionをServerで再検証する。BrowserのAction Eligibility表示はSecurity／Integrity Boundaryではない。

## 8. Multi-browser Conflict

- 全MutationはBrowserが最後にGET／SSEで受け取った`expected_revision`を必須とする。ServerはStale Revisionを`409 revision_conflict`としMutation 0で拒否する。
- ClientはConflict時に全Detailを再取得し、自動Merge／Last-write-wins／Operation ID再発番／Blind Retryを行わない。User Inputが未適用なら、非Canonical Draftとして画面に残してもDBへ自動再送しない。
- Storage内部の段階別OperationはPhase 2-Bどおり同一Command Receiptに収束する。HTTP Action IDの再使用はBodyの同異にかかわらず新Mutationを起こさず、ClientへLatest Detailの再Readを要求する。

## 9. Compatibility／Privacy

- Existing `/api/v1/runtime`、`/api/v1/chat/stream`、`/api/v1/chat/stop`のContract／Route／SSEを変更しない。v1 Requestからv2 Storeを呼び出さない。
- Public Demo／Shared Basic Previewでv2 CapabilityはDisabled、Data RouteはUnavailable、Factory Build／Filesystem Write／Migration／Recovery／Recorder Callは0とする。
- Persistent DetailとSSEはCanonical User／Assistantだけを返す。Thinking／Prompt／RAG Injected Context／Citation本文／Partial／Hidden Original／SecretをDB、API、Browser Storageへ残さない。
- Persistent ModeはRecording OFFを維持し、Phase 2-CでRecorderをBindingしない。

## 10. Acceptance Criteria

- Local Loopback／Explicit opt-inでだけv2 Persistent Chatが起動し、Reload／新BrowserからList／History／Resumeできる。
- Public／Basic／Non-loopbackとPersistent opt-inの併用はFail-closed、通常Public／BasicはPersistent Binding／Write 0で従来Chatが動く。
- RequestにClient Full Historyが存在せず、Reload／Conflict／Terminal後はServer Detailが画面のCanonical Sourceになる。
- New Chat／Resume／Normal／Stop／Retry／Regenerate／Branch Select／ArchiveがCASとDomain Invariantを守る。
- Multi-browserのStale Mutationは409／Write 0、再Read後だけ新しいActionを実行できる。
- Terminal EventはDurable Commit後だけ公開され、Storage FailureはEphemeral Successにならない。
- Existing v1 Regression、Public／Basic Regression、Static Security、Target Test、Ruff、Mypy、Full SuiteがPASSする。

## 11. Related Documents

- [Phase 2-B Requirements](phase_2_b_conversation_persistence_requirements_ja.md)
- [Phase 2-C Architecture](../architecture/phase_2_c_persistent_conversation_api_ux_architecture_ja.md)
- [Phase 2-C ADR](../adr/phase_2_c_persistent_conversation_api_ux_adr_ja.md)
- [Phase 2-C Handoff](../handoffs/phase_2_c_implementation_handoff_ja.md)
- [Phase 2-C Acceptance Matrix](../operations/phase_2_c_acceptance_matrix_ja.md)
