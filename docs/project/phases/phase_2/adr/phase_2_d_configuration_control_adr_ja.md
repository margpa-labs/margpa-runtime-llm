# ADR: Phase 2-D Local Non-persistent Configuration Control

```yaml
adr_id: phase_2_d_configuration_control
status: accepted
phase: phase_2
subphase: phase_2_d
language: ja
created_at: 2026-08-14 JST
decision_owner: Phase 2設計担当者役
approval_authority: project_controller_and_user
```

## 1. Context

Phase 1／2-AはTrusted Startup InputからEffective Configを構築し、Phase 2-B／2-CはLocal PrivateにConversation Persistenceを追加した。次に、設定の採用値／Source／差分／適用結果を検証可能にし、将来のFeature Mode／Recording Mode／Component Switchboardへ接続可能なControl Boundaryが必要である。

一方、RuntimeからTracked TOML、EnvironmentまたはCredentialを編集する設計は、Source of Truth、Secret、Rollback、Multi-surface Exposureを混同する。Research／Developer ModeをAuthority Modeとして扱うことも不可である。

## 2. Decision

Phase 2-Dは、Local Private／Loopback／Auth disabled／Explicit opt-in専用のProcess-local Configuration Controlを採用する。

1. Effective ConfigはTyped Allowlist Projection、Per-field Source、Canonical SHA-512 Digest、Revisionとして公開する。
2. User／Request SettingsとResearch／Developer Settingsを別Contract／Stateとして保持する。
3. Runtime Applyは`research_developer_mode`だけに限定する。
4. Model／Profile／Context／Feature BindingはRestart-required Previewとし、RuntimeからStage／Persistしない。
5. Configuration Control State／Operation Receiptは非永続で、Process Restart時にTrusted Startup Inputsから再構築する。
6. Feature／RecordingはTyped Replaceable Descriptor Portを持つが、Phase 2-E Switchboardを実装しない。
7. Public Demo／Shared Basic PreviewはService Unbound、UI Hidden、Build／Read／Write／Apply 0とする。

## 3. Security／Authority Decision

Research／Developer Modeは安全な診断表示を切り替えるだけであり、次を絶対に行わない。

```text
Authority elevation
Policy / Guard / Access Profile bypass
Tool / Agent permission grant
Secret / Path / Raw Config exposure
Protected Capture enablement
Recorder binding
Public / Basic control exposure
```

UI HiddenはDefense-in-depthにすぎず、Server Schema／Projection／Composition Gateを本Boundaryとする。

## 4. Alternatives Rejected

### 4.1 Tracked TOML Editor

RuntimeとRepository Source of Truthを混同し、File Permission／Concurrency／Rollback／Git差分を増やすためRejectする。

### 4.2 Browser-persisted Settings

Shared Browser／XSS／Stale State／Surface跨ぎの危険があり、Server Effective Stateと分岐するためRejectする。

### 4.3 Generic Dictionary＋Recursive Redaction

新しいSecret／Path FieldをDefault Permitする可能性があるためRejectする。Typed Allowlistを使う。

### 4.4 Restart FieldのPartial Live Apply

Effective StateとStartup Stateが分裂するためRejectする。Mixed PatchはAtomicにMutation 0とする。

### 4.5 Restart ProposalのPending保存

Identity／Scope／Encryption／Migration／Rollback Boundaryが未設計であるためRejectする。

### 4.6 Developer Modeによる権限昇格

存在／表示／評価とAuthority／Permissionを混同するためRejectする。

### 4.7 全Componentの`off／observe／enforce`固定

Component固有Semanticsを破壊するためRejectする。Mode VocabularyはTyped Descriptorごとに定義する。

### 4.8 Phase 2-E Switchboardの先行実装

Dependency／Conflict／Agent／Tool ScopeをPhase 2-Dへ混入させるためRejectする。

## 5. Consequences

### Positive

- Existing TOML／CLI／EnvironmentのSource of Truthを維持できる。
- Safe ProjectionとDigestにより再現性／差分／Evidenceを得られる。
- Public／BasicへDeveloper Controlを露出しない。
- Hook Portを将来のRecording／Feature／Switchboardへ置換可能にする。
- Non-persistent設計によりSecret Store／MigrationをPhase 2-Dへ持ち込まない。

### Trade-offs

- Runtime OverrideはRestartで消える。
- Restart-required変更はUIだけでは完了せず、OperatorがTrusted Startup Inputを変更する必要がある。
- Initial Recording ModeはOFF固定で、Metadata／Full Recordingはまだ使えない。
- Component Conflict ResolutionはPhase 2-Eまで行わない。

## 6. Invariants

- Existing `/api/v1/**`、Persistent `/api/v2/conversations/**`、TOML Profile、Backend Contractは不変。
- Public／Basic Control Service Build／Read／Write／Call 0。
- Secret／Path／Raw Config／Protected Artifact Projection 0。
- Runtime Config Persistence 0、Recorder Call 0。
- Stale／Duplicate／Restart-required／Invalid ApplyのMutation 0。
- Project Root `runtime_data/` Artifact 0。

## 7. Revisit Triggers

Settings Persistence、Remote／Multi-user Control、Protected Research Capture、Concrete Recording、Agent／Tool／Switchboardを実装する前に、新しいADRでIdentity、Scope、Storage、Encryption、Migration、Audit、Rollbackを決定する。新Decisionなしに本ADRを暗黙拡張しない。
