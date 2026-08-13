# ADR: Phase 2-C Persistent API／UX Boundary

```yaml
adr_id: phase_2_c_persistent_conversation_api_ux
status: accepted
phase: phase_2
subphase: phase_2_c
created_at: 2026-08-14 JST
deciders: Phase 2設計担当者役_and_project_controller
```

## 1. Context

Phase 2-BはLocal SQLite Persistence、CAS／Idempotency、Lifecycle、Context Mapper、Crash RecoveryをWeb未Bindingで実装した。Existing `/api/v1/**`はBrowserがFull Historyを送るEphemeral Contractであり、これをそのままPersistent Storeへ結ぶとClient History Import／Silent Merge／Multi-browser Lost Updateが発生する。

Basic PreviewのCredentialは複数人で共有でき、Public DemoはCredentiallessであるため、どちらもPersistent User ScopeのIdentity Boundaryにはできない。

## 2. Decision

1. Persistent Conversationは`/api/v2/conversations/**`の別Versioned Contractとし、v1を拡張しない。
2. BindingはExplicit opt-inのLoopback-only Local Privateに限定する。Public／Basic／Non-loopbackへのBindingはStartup時にFail-closedする。
3. ScopeはServer Startupが所有し、ClientからScope／Pathを受け取らない。
4. RepositoryをCanonical Source of Truthとし、BrowserはFull HistoryをMutation Requestへ送らず、Reload／Terminal／Conflict後にDetailを再Readする。
5. 全MutationはOperation IDとExpected Revisionを要求し、Stale Browserを409／Mutation 0にする。Silent Merge／Last-write-wins／Blind Retryを行わない。
6. Retry／Regenerate／BranchはPhase 2-A Domainの既存Relationで表現し、Source Turnを上書きしない。
7. Terminal SSEはPhase 2-BのDurable Commit後だけ公開し、DeltaをCanonical HistoryまたはDBに保存しない。
8. 2-CはMinimal CLI opt-inまでとし、TOML Control Surface／Research Developer Mode／Recording Modeは2-Dへ延期する。

## 3. Alternatives Rejected

### Extend `/api/v1/chat/stream`

Rejected。Client Full History ContractとServer-owned History Contractが混在し、Existing v1互換性とSource-of-truthを同時に保てない。

### Persist Browser State Directly

Rejected。Browser StorageはCAS／Crash Recovery／Multi-browser Orderingの正本にならず、Sensitive Canonical Textの副本も増やす。

### Bind Shared Basic Credential to One Scope

Rejected。Credential共有者間の会話が混在し、Basic AuthをUser Identityと誤解する。

### Make Retry／Regenerate destructive

Rejected。従来Outputの追跡可能性とBranch Evidenceを失い、後続の比較／Judge／Governance実験を妨げる。

### Automatically merge stale browser state

Rejected。不明な意図でHead／Historyが変わり、CASの意味を崩す。

## 4. Consequences

### Positive

- Existing v1とPublic／Basicを変更せずPersistent UXを追加できる。
- Browser Reload／Multi-browser／Crash後のCanonical Stateが一意になる。
- Retry／Regenerate／Branchの比較可能なEvidenceを保持できる。
- 将来のAccount／AuthorizationをCurrent Shared Credentialと混同しない。

### Cost／Limitation

- v1／v2の両ContractとUI Mode分岐をTestする必要がある。
- SSE Replayを保存しないため、Response喪失後はDetailでFinal Stateを回復するがDeltaは再生できない。
- Phase 2-CはSingle Local Scopeであり、Remote Account／Multi-user化の代替ではない。
- Chat Rename／Search／Delete／Settings Persistenceは含まない。

## 5. Invariants

```text
Existing /api/v1 unchanged
Public / Basic persistent binding = 0
Client full-history mutation payload = 0
Scope accepted from client = 0
Terminal event before durable commit = 0
Silent CAS merge / blind retry = 0
Derived source overwrite / deletion = 0
Sensitive non-canonical persistence = 0
Recording binding = 0
```

## 6. Review Trigger

Account Identity、Remote Access、Encryption、Multi-host Store、Config Control、Concrete RecordingまたはAPI v3を導入する場合は本ADRを再Reviewする。Public／BasicへのPersistence拡張は本ADRの範囲外であり、新たなIdentity／Authorization Designを必須とする。
