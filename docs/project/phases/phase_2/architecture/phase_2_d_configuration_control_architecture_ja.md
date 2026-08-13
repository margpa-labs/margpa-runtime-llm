# Phase 2-D Configuration Control Architecture

```yaml
document_id: phase_2_d_configuration_control_architecture
status: accepted_for_phase_2_d_implementation
phase: phase_2
subphase: phase_2_d
language: ja
created_at: 2026-08-14 JST
from_role: Phase 2設計担当者役
to_role: Phase 2実装者役
```

## 1. Architecture Goal

既存Config Resolutionの上に、Secret／Path／Raw Configを持ち出さないProcess-local Control Planeを追加する。Domain Contract、Service、Bootstrap Composition、v2 Web Adapter、Local-only UIを分離し、Phase 2-EのAgent／Tool／Switchboardを先取りしない。

## 2. Component Boundary

```text
Trusted Startup Inputs
  application TOML / deployment profile / environment / explicit CLI
                         |
                         v
Existing Config Loader -> EffectivePhase1Config + typed field sources
                         |
                         v
Safe Effective Projector -> canonical projection -> SHA-512 digest
                         |
                         v
ConfigurationControlService (process-local revision / operation receipts)
     | preview            | atomic live apply
     v                    v
Typed Diff          research_developer_mode override only
     |
     v
/api/v2/configuration/** -> Local-only Browser Control Panel

Typed Feature / Recording Descriptor Ports -> safe projection only
```

Configuration ControlはConversation Domain／Repository、Existing v1 Generation、Access Profileの下位に置かず、BootstrapでOptionalに合成する。Control ServiceなしでもCurrent Runtimeは完全に動作する。

## 3. Domain Contracts

`modules/configuration_control`にFramework非依存のFrozen Dataclass／Enum／Protocolを置く。

```text
ConfigurationSource
  built_in_default | application | deployment_profile | environment
  | explicit_cli | runtime_override | composed_runtime

ApplyDisposition
  runtime_applicable | restart_required | unsupported | read_only

ConfigurationField
  key, typed value, source, disposition

EffectiveConfigurationSnapshot
  schema_version, revision, digest_sha512, fields, feature_hooks, recording_hooks

ConfigurationPatch
  research_developer_mode?, selected_model?, context_size?, feature_modes?, recording_modes?

ConfigurationPreview
  base_revision, base_digest, redacted_changes, outcome

ConfigurationApplyResult
  outcome, revision, digest, redacted_changes, restart_fields

ConfigurationControlService
  runtime(), effective(), preview(), apply()
```

Patchは任意DictionaryではなくFieldごとのTyped Optional Contractとする。Unknown KeyはWeb／Domain両方で拒否する。

## 4. Safe Projection／Source Trace

### 4.1 Allowlist

Projection可能な値は、Model Key、Deployment Profile Key、Backend／Deviceの安全なIdentifier、Context Size、Generation Default、Research ModeおよびTyped Hook Descriptorに限定する。

次をProjection Inputに入れない。

```text
Credential / Secret / Environment Value
Model Root / Runtime Root / Absolute or Relative Filesystem Path
System Prompt / Raw Thinking / Tool internals / Protected Capture
Raw TOML / Raw CLI argv / Arbitrary metadata / Exception text
```

### 4.2 Source Trace

Existing Loaderは各Known Fieldの採用Sourceを値とは別に追跡する。`EffectivePhase1Config`への新Fieldは安全なDefaultを持たせ、既存Constructorを壊さない。Environmentは「Sourceがenvironment」であることだけを公開し、変数名／値を返さない。

Source解決順序は次で固定する。

```text
runtime_override (runtime_applicable field only)
> explicit_cli
> environment
> deployment_profile
> application
> built_in_default
```

Platform Default等の合成結果は`composed_runtime`または既存Resolution Sourceを安全に写像する。

### 4.3 Digest

Safe Projectionから`digest_sha512`とVolatile Fieldを除き、EnumをStable String、Map KeyをSortしたCanonical JSONをUTF-8 EncodeしSHA-512化する。同じEffective StateはProcess／Orderingによらず同じDigestになる。

## 5. Service State Machine

```text
UNBOUND
  -> local gate PASS / explicit opt-in -> READY revision=1
READY
  -> preview -> READY (mutation 0)
  -> apply live + CAS PASS -> READY revision+1
  -> stale / duplicate / invalid / restart-required -> READY (mutation 0)
PROCESS RESTART
  -> trusted startup inputsから再構築 -> READY revision=1
```

- ServiceはLock内でExpected Revision／Digest、Operation ID、Patch Dispositionを再検証する。
- Applied Operation ReceiptはProcess Memoryに保持する。Duplicateは新Mutationを行わない。
- Mixed Patchに一つでもRestart-required／Unsupportedが含まれる場合、Live Fieldも適用しない。
- No-opはOperation Receiptを成功Mutationとして記録せず、Revisionを増やさない。
- Failure ErrorはTyped Codeに変換し、Raw Config／Exception／Pathを返さない。

## 6. Live／Restart Boundary

| Field／Hook | Phase 2-D disposition | Behavior |
|---|---|---|
| `research_developer_mode` | runtime_applicable | Process MemoryへAtomic Apply |
| selected model／profile／context | restart_required | Diff Previewのみ、Stage 0 |
| Documentation RAG adapter mode | restart_required | `disabled／enabled`をProjection、Rebind 0 |
| Conversation recording mode `off` | read_only current state | Recorder Unbound／Call 0 |
| recording `metadata／full` | unsupported | 422／Mutation 0 |
| protected capture | not representable | Unknown／Protected Fieldとして拒否 |
| Agent／Tool／Switchboard | out of scope | Phase 2-EへDeferred |

## 7. Composition／Exposure

`entrypoints/web/main.py`は最小の`--configuration-control` Booleanを受け取る。Bootstrapは次の順序を守る。

1. Exposure Mode、Bind Host、Auth Mode、Explicit opt-inを検証する。
2. Local／Loopback／Auth disabledでなければService／Hook Factoryを呼ばずFail-closedする。
3. Existing Effective ConfigからSafe Source Trace／Projectionを構築する。
4. Initial Hook Descriptorを合成し、Process-local Serviceを構築する。
5. Optional ServiceをWeb Runtimeへ渡す。

Public／Basicの通常起動ではStep 3以降を実行しない。TOML ProfileやAccess ProfileへControl設定を追加しない。

## 8. Web API／Page Bootstrap

Web AdapterはDomain ModelをBounded Pydantic Contractへ写像する。Config Field名、Patch Shape、Error CodeはVersioned Contractで固定する。

Local Control Bindingがある場合だけ、Root HTMLの固定PlaceholderをBoolean `enabled`へServer-sideで置換する。Static Defaultは`disabled`とし、Public／BasicではFile内容と同じDisabled Bootstrapを返す。任意Script、Config値、DigestをHTMLへ埋め込まない。

BrowserはBootstrap enabledの場合だけ`/api/v2/configuration/runtime`を呼ぶ。Unbound時の全Configuration RouteはGeneric `404 configuration_control_unavailable`で、Config存在／Source／Pathを示さない。

## 9. UI State

```text
capability: disabled | loading | ready | failed
snapshot: safe server projection or null
preview: redacted transient result or null
apply: redacted transient result or null
```

- UIはSnapshotをBrowser Storageへ書かず、Reload時にServerから再取得する。
- Apply Conflictでは自動Merge／Blind Retryせず、Effectiveを再Readする。
- Developer PanelはResearch Mode offで隠すが、Server Contractは常に同じ禁止Fieldを拒否する。
- Existing User Settings、Ephemeral Chat、Persistent ChatのState ObjectへConfig Patchを混在させない。

## 10. Failure／Lifecycle

- Projection／Schema／Hook Validation FailureはStartupまたはRequestをSafe Failureにし、既存ChatへSilent Degraded Controlを表示しない。
- Control Service ShutdownはExternal Resourceを持たない。Conversation Store、Model、RecorderのLifecycleを所有しない。
- Restart-required Applyは`restart_required` Resultを返すだけで、File／Environment／CLI／Runtime Dataを書き換えない。
- Public／BasicのControl opt-in指定はWeb Server Bind前に失敗させる。

## 11. Test Architecture

- Domain Unit：Schema、Digest determinism、Source precedence、CAS、Idempotency、Atomic mixed patch、Protected Field。
- Bootstrap Unit：Local Matrix、Factory Spy、Public／Basic Build 0。
- Web Contract／Integration：v2 Projection、Safe Error、Route Unavailable、UI Capability、Apply／Conflict。
- Static Contract：Public／Basic Call 0、Browser Storage 0、Secret／Path Token 0、ja／en。
- Regression：Existing Config、CLI、v1、Persistent v2、Public／Basic、RAG、Static Security。
- Test Artifactは`tmp_path`またはMemoryだけを使い、Project Root `runtime_data/`を生成しない。

## 12. Related Documents

- [Requirements](../requirements/phase_2_d_configuration_control_requirements_ja.md)
- [ADR](../adr/phase_2_d_configuration_control_adr_ja.md)
- [Handoff](../handoffs/phase_2_d_implementation_handoff_ja.md)
- [Acceptance Matrix](../operations/phase_2_d_acceptance_matrix_ja.md)
