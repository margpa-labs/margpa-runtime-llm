# Phase 2-D Configuration Control Requirements

```yaml
document_id: phase_2_d_configuration_control_requirements
status: accepted_for_phase_2_d_implementation
phase: phase_2
subphase: phase_2_d
language: ja
created_at: 2026-08-14 JST
from_role: Phase 2設計担当者役
to_role: Phase 2実装者役
decision_authority: project_controller_and_user
```

## 1. Objective

Phase 2-Dは、現在のConfig Loader／Effective Config／CLI／Web Runtimeを維持しながら、Runtime設定を安全なTyped Projectionとして確認し、Local Private環境だけでPreview／ApplyできるConfiguration Controlを追加する。

User SettingsとResearch／Developer Settingsを分離し、設定値のSource、SHA-512 Digest、Redacted Diff、Apply Result、Runtime-applicable／Restart-required境界を明示する。Research／Developer Modeは表示・観測用Modeであり、Authority、Policy、PermissionまたはProtected Captureを変更しない。

## 2. Scope

### In Scope

- Separate `/api/v2/configuration/**` Contract。
- Local／Loopback／Authentication disabled／Explicit opt-inだけのControl Binding。
- Runtime Config Schema ValidationとSafe Effective Projection。
- Field単位のValue／Source／Apply DispositionとCanonical SHA-512 Digest。
- Revision／Digest CAS、Operation Idempotency、Redacted Preview／Apply Result。
- Process内の非永続Research／Developer Mode。
- Feature Mode／Recording ModeのTyped Adapter Hook。
- Local Private専用のCapability-gated UI。

### Out of Scope

- Agent／Tool／Component Switchboard、Dependency／Conflict Resolver。
- Tracked TOML編集、Environment／CLI書換え、Browser Settings永続化。
- Public Demo／Shared Basic PreviewへのDeveloper／Persistent Control。
- Secret、Raw Path、System Prompt、Raw Thinking、Tool内部情報、Protected Captureの表示または保存。
- Remote／Multi-user Config Store、Encryption、Account、Cloud Sync。
- Conversation Persistence Contractの変更。

## 3. Settings Separation

### 3.1 User／Request Settings

次は既存どおりRequest単位であり、Global Runtime Configuration Mutationへ統合しない。

```text
response_language
max_new_tokens
thinking_mode
thinking_visibility
summary_mode
documentation_rag_mode
```

Browserの既存UI Language以外をConfiguration Controlが保存してはならない。

### 3.2 Research／Developer Settings

- `research_developer_mode = off | on`をProcess内Stateとして提供し、Defaultは`off`とする。
- Mode変更はDeveloper Detail Panelの表示と安全な診断情報の可視性だけを変更する。
- ModeはAuthorityを昇格せず、Policy／Guard／Access Profileを迂回せず、Agent／Tool Permissionを生成せず、Secretを露出せず、Protected Captureを有効化しない。
- UI非表示はSecurity Boundaryではない。ServerはModeにかかわらず禁止FieldをContract／Projectionで拒否する。

### 3.3 Runtime／Restart Settings

Model Key、Profile Key、Context Size、Backend／Deviceの安全な識別子、Feature Adapter Mode等はTyped Effective Projectionへ含めてもよい。Raw Model Root、Runtime Root、Filesystem Path、Environment Value、Credential、Prompt、Unknown Extension Blobは含めない。

## 4. Exposure Boundary

- Control BindingはExplicit CLI opt-in、`WebExposureMode.LOCAL`、Loopback Host、Authentication disabledの全条件を満たす場合だけ許可する。
- Public Demo、Shared Basic Preview、Non-loopbackまたはAuthentication enabledとの併用はControl Service Build前にFail-closedする。
- Public／Basicの通常起動はControl Service Build／Read／Write／Apply 0、Control UI非表示、Configuration Data RouteはSafe `404`とする。
- Existing `/api/v1/**`、Persistent `/api/v2/conversations/**`、Access Profile、TOML Profileを変更しない。
- Page BootstrapはControl Bindingの有無をBooleanだけで示してよい。Public／BasicでConfig Value、Source、Digest、Pathを埋め込まない。

## 5. Effective Configuration Contract

- Effective Projectionは明示AllowlistされたTyped Fieldだけから構成する。Generic Recursive Redactionや任意Dictionaryを用いない。
- 各Fieldは`value`、`source`、`apply_disposition`を持つ。Sourceは少なくとも次を区別する。

```text
built_in_default
application
deployment_profile
environment
explicit_cli
runtime_override
composed_runtime
```

- PrecedenceはLive Fieldに限る`runtime_override`を最上位とし、以降`explicit_cli > environment > deployment_profile > application > built_in_default`とする。
- DigestはSafe Effective ProjectionのCanonical UTF-8／Sorted-key JSONをSHA-512化する。Digest自身、Timestamp、Process ID等のVolatile Fieldを入力に含めない。
- RevisionはProcess内で1から始め、成功した実MutationだけIncrementする。DigestとRevisionを混同しない。
- Unknown／Duplicate／Invalid Type／Invalid Enum／OversizeをSchema ValidationでFail-closedする。

## 6. Preview／Apply Contract

Prefixを`/api/v2/configuration`に固定する。

```text
GET  /api/v2/configuration/runtime
GET  /api/v2/configuration/effective
POST /api/v2/configuration/preview
POST /api/v2/configuration/apply
```

- Request／Responseは`extra=forbid`のBounded Typed Contractとする。
- PreviewはRead-onlyで、Typed Patch、Redacted Before／After、Source、Disposition、Restart Reasonを返す。Revision／Digest／Stateを変更しない。
- Applyは`operation_id`、`expected_revision`、`expected_digest`、Typed Patchを必須とする。
- Stale Revision／Digestは`409 configuration_conflict`、Applied Operation ID再送は`409 operation_already_applied`とし、新Mutation 0にする。
- Mixed Live／Restart-required Patchは部分適用せず、`restart_required`を返してMutation 0とする。
- Protected／Unsupported Fieldは`422`、Mutation 0とする。No-opはRevision／Digestを変更しない。
- Phase 2-DでRuntime Applyを許すFieldは`research_developer_mode`だけとする。他はPreview可能でもRestart-requiredまたはUnsupportedである。
- Restart-required提案をFile、Browser、Runtime Data RootへStageしない。OperatorがTrusted Startup Inputを変更してProcessを再起動するまでEffective Stateは変化しない。
- 成功ApplyはAtomicにStateを交換し、新Revision／Digest／Redacted Diff／Apply Resultを返す。

## 7. Feature／Recording Hooks

- HookはTyped Descriptor Portとし、`component_key`、Allowed Modes、Current Mode、Availability、Apply Dispositionだけを安全に公開する。
- 全Componentを機械的に`off／observe／enforce`へ押し込まない。Component固有のSemanticsを明示する。
- Initial Feature HookはDocumentation RAG Adapterの`disabled | enabled`状態を安全にProjectionできる。Binding変更はRestart-requiredで、Phase 2-DはStage／Rebuildしない。
- Initial Recording HookはConversation Recording Mode `off`だけをSupported Current Stateとして示す。`metadata／full` ApplyはUnsupportedとし、Recorder Build／Bind／Call 0を維持する。
- Protected CaptureはHookではない。Enableを意図するField／Unknown Fieldは拒否する。

## 8. UI Requirements

- Control PanelはLocal Private／Control Binding enabledの場合だけ表示・Requestする。Public／BasicはDOM上HiddenかつConfiguration Route Call 0とする。
- UIはEffective Field、Source、Digest、Revision、Disposition、Redacted Diff、Apply Resultを表示する。
- Research／Developer ToggleはLive Apply可能とし、Developer DetailはMode offで非表示にする。ただし非表示をAuthority Boundaryとして扱わない。
- Restart-required項目はRead-onlyまたはPreview-onlyで、Trusted Startup Input変更とRestartが必要であることを表示する。
- Browser StorageへConfig Snapshot、Diff、Digest、Research Mode、Path、Secretを保存しない。
- ja／en、Keyboard、Focus、Mobile Layout、Existing Chat／Persistence UXを回帰維持する。

## 9. Persistence／Restart Contract

- Phase 2-D Control Stateは明示的にNon-persistentとする。Process RestartでRevision、Operation Receipt、Runtime OverrideはResetされる。
- Tracked TOML、Environment、CLI、`runtime_data/`、Conversation Store、Browser StorageへControl Stateを書かない。
- Restart後は既存Source Precedenceから再度Effective Configを構築する。
- 将来のSettings Persistenceは、Identity／Scope／Encryption／Migration／Rollbackを含む別のSafe Boundaryが設計されるまでDeferredとする。

## 10. Acceptance Criteria

- Local Private Explicit opt-inだけでConfiguration Controlが利用でき、Public／Basic／Non-loopbackはService Build前に拒否またはUnboundとなる。
- Effective ProjectionがAllowlist、Per-field Source、SHA-512 Digest、Revisionを安全に返し、Secret／Path／Raw Inputを返さない。
- PreviewがRead-only、ApplyがCAS／Idempotent／Atomicであり、Restart-required Patchを部分適用または保存しない。
- Research／Developer ModeがAuthority／Policy／Permission／Protected Captureへ影響しない。
- Feature／Recording HookがTyped、Replaceable、Component-specificであり、Recorder Call 0を維持する。
- Existing v1／Persistent Conversation／Public／Basic／TOML Profile／Backend ContractがRegression PASSする。
- Target／Static／Ruff／Mypy／Full Suite PASS、Project Root `runtime_data/`新規Artifact 0。

## 11. Related Documents

- [Phase 2-D Architecture](../architecture/phase_2_d_configuration_control_architecture_ja.md)
- [Phase 2-D ADR](../adr/phase_2_d_configuration_control_adr_ja.md)
- [Phase 2-D Handoff](../handoffs/phase_2_d_implementation_handoff_ja.md)
- [Phase 2-D Acceptance Matrix](../operations/phase_2_d_acceptance_matrix_ja.md)
- [Runtime Data／Recording Architecture](../architecture/phase_2_runtime_data_root_and_recording_architecture_ja.md)
