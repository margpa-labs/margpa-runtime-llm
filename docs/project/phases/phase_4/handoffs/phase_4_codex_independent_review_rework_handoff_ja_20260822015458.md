# Phase 4 Codex Independent Review — Exact Rework Handoff

```yaml
document_id: phase_4_codex_independent_review_rework_handoff_20260822015458
status: major_rework_required
phase: phase_4
subphase: phase_4_h
work_unit: p4_h_wu_001_codex_independent_major_review
from: プロジェクト責任者兼設計統括者役（Codex）
to: Claude側設計統括者役
language: ja
recorded_at: 2026-08-22 01:54:58 JST
recorded_at_source: `TZ=Asia/Tokyo date '+%Y%m%d%H%M%S %Y-%m-%d %H:%M:%S %Z'`
predecessor: docs/project/phases/phase_4/handoffs/phase_4_claude_complete_candidate_handoff_ja.md
completion_line: phase_4_claude_rework_complete_candidate
source_rework_authorized: true
test_rework_authorized: true
frontend_rework_authorized: true
new_append_only_evidence_authorized: true
stable_doc_mutation_authorized: false
runtime_data_access_authorized: false
definitions_mutation_authorized: false
git_mutation_authorized: false
phase_4_closure_authorized: false
phase_5_authorized: false
```

## 0. Controller Decision

`REJECT COMPLETE_CANDIDATE / MAJOR REWORK REQUIRED`。

Phase 4 Coreの新規実装には利用可能な要素があるが、Frozen Phase 4 Contractと実Runtimeの間に重大な不整合がある。現在の`phase_4_g_complete_candidate`はAcceptanceしない。

```text
Phase 4 Technical Closure : BLOCKED
Phase 4 User Acceptance   : NOT READY
Phase 5                   : NOT AUTHORIZED
```

本ReworkはPhase 4のFrozen Requirement／Architecture／Execution Plan／Acceptance Matrixを実装し直すためのものであり、Scopeの新規拡張ではない。Claudeは時間制約や実装Riskを理由にFrozen必須項目を任意Deferredへ変換してはならない。

## 1. Mandatory Recovery Reading

Provider Summary、Auto-compaction SummaryまたはこのHandoffだけを正本としない。実装再開前に次をRepositoryから再読する。

1. `docs/project/current/automation_cross_provider_compaction/automation_cross_provider_compaction_governance_integrated_ja.md`
2. `docs/project/shared/task_roles/claude_side_design_governor_operating_notes_ja.md`
3. `docs/project/shared/task_roles/claude_side_long_running_automation_companion_ja.md`
4. `docs/project/phases/phase_4/requirements/phase_4_requirements_ja.md`
5. `docs/project/phases/phase_4/architecture/phase_4_architecture_ja.md`
6. `docs/project/phases/phase_4/adr/phase_4_adr_ja.md`
7. `docs/project/phases/phase_4/operations/phase_4_execution_plan_ja.md`
8. `docs/project/phases/phase_4/operations/phase_4_acceptance_matrix_ja.md`
9. `docs/project/phases/phase_4/handoffs/phase_4_claude_execution_handoff_ja.md`
10. `docs/project/phases/phase_4/handoffs/phase_4_claude_complete_candidate_handoff_ja.md`
11. 本Handoff。

Phase 3のMode／Configuration／Evidence／UI As-builtは、実装対象Pathを再読してから変更する。Recovery完了後、実装開始前に最低限次を明記する。

```text
Repository Recovery       : PASS / FAIL
Active Phase              : Phase 4 Rework
Current Controller Handoff: 本Handoff
Git Mutation              : FORBIDDEN
Phase 5                   : FORBIDDEN
```

## 2. P4-CODEX-001 — 実EntrypointがPhase 4 GovernanceをBuildしない

### Confirmed Finding

`build_phase1_web_runtime()`は`runtime_governance_enabled: bool = False`を受け取るが、現行`entrypoints/web/main.py`の`runtime_factory = partial(...)`は`runtime_governance_enabled`と`runtime_governance_definitions_root`を渡さない。したがって通常のMac CLI起動でPhase 4 Composition／pre Hook／post HookはBuildされない。

Phase 4 Testの一部はCompositionを直接組み立てた孤立Testであり、実Entrypoint Wiringを証明しない。`test_runtime_governance_public_basic_call0.py`自身も、現行EntrypointはRuntime Governance未配線であると明記する。

### Required Correction

- 既存のLocal／Loopback／Auth-disabled／Explicit Governance Opt-inを起点に、通常Mac EntrypointがPhase 4 Compositionを実際にBuildする。
- `definitions/`の実RootはServer-ownedのTyped Pathとして明示的に渡す。Client入力やStatusからPathを指定／開示しない。
- Public／Basic／Non-loopbackはComposition Build／Point Call／Evidence Write／Private Route Call 0を維持する。
- Entrypointの実`runtime_factory`へ渡された値と、Localで`WebRuntime.runtime_governance_composition is not None`になることを専用Testで固定する。
- FakeInferenceの直接Composition Testだけで本FindingをCloseしない。

## 3. P4-CODEX-002 — Governance ModeがPhase 3とPhase 4で二重化している

### Confirmed Finding

既存Settings UI／`/api/v2/configuration`はPhase 3 `GovernanceDefinitionsRuntime`のModeを操作する。Phase 4は別の`MainGovernanceModeController`と`/api/v3/runtime-governance/mode`を追加した。このままではUI上のOFF／OBSERVEとMain Model RuntimeのModeが別Stateであり、Source of Truthが分裂する。

さらにPhase 4 Direct Mode APIは、Frozen `P4-F-WU-002`のPreview／Apply／Revision／Digest／CASを意図的に省略している。この独自簡略化はFrozen Contract変更として許容しない。

### Required Correction

- Governance ModeのCanonical Mutation Pathを既存Configuration ControlのPreview／Apply CASに一本化する。
- OFF／OBSERVE／ENFORCEのUI、Status、Conversation Hookが同一のCanonical Mode Snapshotを参照する。
- Phase 3-only RuntimeではENFORCE unavailableを維持し、Phase 4 Bindingが実際にReadyなLocal RuntimeでのみENFORCEをAvailableにする。EnumにValueを追加しただけで全ProfileをAvailableにしない。
- Modeと同時にProfile／Budget／AvailabilityのTyped Safe ProjectionをConfiguration Controlへ接続する。Phase 4でRuntime Mutationを許さないFieldはRead-onlyまたはUnsupportedとし、黙って省略しない。
- 別のDirect Apply Endpointを残す必要がある場合も、MutationはCanonical CAS Serviceのみが行う。二重Controller／二重Revisionは禁止する。
- Concurrent Apply、Stale Revision／Digest、Idempotent Operation、Mode unavailableをTestする。

## 4. P4-CODEX-003 — Frozen Evidence／Status／Frontendが未実装

### Confirmed Finding

Claude Completion Handoffは次を明記する。

- `P4-EVD-001／P4-F-WU-001`のPhase 3 Audit Evidence Port／JSONL統合は未実装。
- Phase 4 Runtime GovernanceのFrontend UIは未実装。
- Status APIはMode／Revision／Descriptor Availabilityだけで、`P4-STS-001`のBinding State／Selected Definition／Rule Count／Last Result／Action Count／Degraded Reasonを満たさない。

これらはController-ownedのPhase 4-H Workではなく、Frozen Phase 4 Technical Scopeである。

### Required Correction

- Phase 3 Audit Evidence PortをTyped Eventとして拡張し、Point Start／Terminal、Binding、Rule／Evaluation、Recommendation、Executed／Not-executed Action、Cost／Latency／Call Count、Failure／Degradedを記録できるようにする。
- Raw Prompt／Raw Output／Raw Thinking／Secret／Absolute Path／Definition Body／Raw ExceptionをEvidenceに含めない。
- `StandardGovernanceResult`をEvidence SubscriberとSafe Status Subscriberへ接続する。ただし同じResultを2回評価しない。
- Default OBSERVEのEvidence Write FailureはGenerationに介入せず、Typed Degraded Statusとして可視化する。
- Settings UIにPhase 4のOFF／OBSERVE／ENFORCE、Availability、Binding／Rule／Last Result／Action／DegradedのSafe Projectionを表示する。
- Backend、Frontend Source、Generated Staticの順で更新し、Static Assetだけを手編集しない。
- Evidence Restart Readback、Write Failure、Status Subscriber Failure、Projection Redaction、Frontend InteractionをTestする。

## 5. P4-CODEX-004 — Definition 0件／Invalid BundleでENFORCEがExecutableになる

### Confirmed Finding

`binder.bind()`はDescriptor 0件でもRegistryとAuthorityが非空なら`executable=True`にする。`RuntimeGovernanceComposition`は全Actionを予めRegistered／Grantedとし、そのTrial BindでENFORCE Availabilityを決める。

その結果、Definition 0件／Provider Failure／Invalid BundleがすべてEmpty Descriptorへ圧縮された後もENFORCEがAvailableになり、Definitionに由来しないBuilt-in Structural RuleでStop／Rejectが実行される。これはFrozen Acceptance Matrixの次と矛盾する。

```text
Definitions 0 + observe : inactive_no_definitions / output unchanged
Definitions 0 + enforce : unsupported / mutation 0
Invalid Bundle + enforce: unavailable / no silent observe
```

### Required Correction

- Validated／Supported／Non-empty Execution Descriptorと必要Dependencyが存在するときのみBindingをExecutableにする。
- Source Plan／Manifest／Definition／Descriptor／Capability／Authority／Policy／Budget／RegistryのIntegrityをBinding Availabilityに反映する。
- Provider absent、Provider failure、Invalid／Quarantined／Unsupported Bundleを単一のEmpty Tupleで潰さず、Typed Provider／Binding StateとSafe Degraded Reasonにする。
- OBSERVEのDefinition 0件は非介入の`inactive_no_definitions`に収束させる。
- ENFORCEのDefinition 0件／Invalid BundleはMode TransitionまたはInvocationをUnavailableにし、Action 0とする。
- 現在の逆向きTest（Empty／InvalidでENFORCE Action実行を期待）は、Frozen Matrixに合うNegative Testへ修正する。

## 6. P4-CODEX-005 — ENFORCE FailureがFail-open／Silent OFFになる

### Confirmed Finding

- `bootstrap/runtime_governance.py::_safe_mode()`はMode Providerの例外／Unknown Valueを`off`に変換する。
- `ConversationGenerationSession._governance_pre_check()`／`_governance_post_check()`はHook例外を握り潰し、通常Generation／Completionを続行する。
- 専用TestもこのFail-openを正常系として固定する。

これは`P4-PNT-006`、Architecture Failure Policy、ENFORCEのNo Silent Downgrade／Safe-side Contractと一致しない。

### Required Correction

- OFFのみPoint／Evaluator／Action／Evidence Call 0を維持する。
- ModeがUnknown／Unreadableな場合、OFFだと推測しない。Typed `mode_unavailable`／Degradedとし、ProfileのSafe Failure Policyへ収束させる。
- OBSERVEのEvaluator／Evidence／Subscriber FailureはModel Input／Outputを変えず、ResultとStatusをDegradedにする。
- ENFORCE pre FailureはModel Call前のTyped Safe Stop／Unavailableに収束させる。
- ENFORCE post Failureは未承認CandidateをCompleted／Persistent Assistant Messageへ流さない。Typed Error／Unavailableへ収束させる。
- Point／Action FailureをGeneration成功またはAction成功としてEvidence化しない。
- Mode Provider Error、Evaluator Error、Binder Error、Resolver Error、Adapter Error、Evidence Error、Status Subscriber ErrorのOFF／OBSERVE／ENFORCE MatrixをTestする。

## 7. P4-CODEX-006 — Action ResolverがFrozen Routingを実装せず、Action成功を偽装する

### Confirmed Finding

Current Resolverは同一Action ID内のSeverity Deduplication、Authority、Point／Stage、Registry／Adapterのみを確認する。Frozen Architectureの次を実装していない。

```text
conflict resolution
  -> mode
  -> authority / policy
  -> capability
  -> budget
  -> registered adapter validation
  -> execute or explicit not_executed
```

また`LocalActionAdapter`は全Registered Actionを無条件に`executed=True`で返す。実CallerがBehaviorを適用するのは`stop_before_generation`と`reject_output`だけであり、`constrain_generation_config`と`warn`等は実効果がないのに成功Actionとして報告され得る。

### Required Correction

- Mode／Authority／Policy／Capability／Budget／Conflict／Registry／AdapterをResolverの実Inputと実判定にする。Binding Digest内に存在するだけで判定済みとしない。
- 異なるAction間のConflictをResolutionし、未解決なら実行0／`conflict_unresolved`にする。
- Phase 4で実際に効果を適用できるActionのみRegistered／Grantedにする。
- `constrain_generation_config`をPhase 4で実装するなら、Allowlist Fieldに対するTyped Patchを既存Generation Validator前に適用し、実行結果をTestする。実装しないならRegistry／Authorityから外し、Explicit Not-executedにする。
- `warn`をExecutedにするならSafe Status／Evidenceへ実投影する。投影なしでExecutedにしない。
- `pass`／`recommend_only`は非介入であることをAction Resultで区別する。
- Double Execute／Partial Failure／Adapter Failure／Unknown Action／Authority Missing／Capability Missing／Budget Exceeded／ConflictのNegative MatrixをTestする。

## 8. P4-GOV-001 — Auto-compaction／Quota Reset自動再開のEvidence Correction

### Confirmed Finding

Claude Completion Handoffは、Auto-compactionと5時間利用制限Reset後にHuman Inputなしで自動再開したことを報告した。これはProvider／Automation Capabilityとして有用な成功Evidenceである。

一方で、次を明記した。

```text
Summary内容を唯一の正本として継続。
Compaction前のWorkを再検証なしで継続。
```

これはRepository-driven Recoveryと矛盾する。Provider SummaryはRecovery HintでありCanonical Sourceではない。

### Required Correction

既存Handoff／Trackerを編集せず、Phase 4 Historyに新規Append-only Evidenceを1件作成する。少なくとも次を分離する。

```text
Five-hour quota reset auto-resume capability : PASS
Human manual resume input                    : 0と自己申告
Auto-compaction transport continuity         : PASS候補
Repository Recovery reread                   : FAIL / NOT PERFORMED
Provider Summary sole-source use             : GOVERNANCE VIOLATION
Pre-compaction Work revalidation              : NOT PERFORMED
Language Fidelity                            : 独立軸として記録
Technical Result validity                     : Codex Rework後に別途判定
```

- Auto-resume機能の成功とRecovery Protocolの失敗を相殺しない。
- 次のCompaction／Quota Resume後は、Active Recovery Index／Controller Handoff／Current WU／Relevant SourceをRepositoryから再読し、実装継続前にRecovery Stateを再固定する。
- Provider MemoryへのWrite／Readを正本としない。Cross-provider正本はRepository内Index／Handoff／Evidenceのみである。

## 9. Required Validation

### 9.1 Technical

- Phase 4 Focused Unit／Integration／Adversarial Matrix。
- Actual Local Entrypoint Composition Wiring Test。
- Configuration Preview／Apply／CAS／Concurrent Conflict／Idempotency Test。
- OFF／OBSERVE／ENFORCE x valid／empty／invalid／provider failure Matrix。
- OFF／OBSERVE／ENFORCE x mode／binder／evaluator／resolver／adapter／evidence／subscriber failure Matrix。
- Evidence Restart／Corruption／Write Failure／Redaction Test。
- Ephemeral／Persistent／RAG／Summary／Stop／Retry／Regenerate／Branch Regression。
- Public／Basic／v1／v2 Private Governance Build／Read／Write／Route／Point Call 0 Test。
- Frontend Typecheck／Lint／Test／Build。
- Backend Ruff／Mypy／Full Test。

### 9.2 Test Temporary Boundary

pytest／Frontend Test／Child Processを含むTool ActionもTask Actionである。Project Root外Temporary Rootを使用しない。

- Test開始前にProject Root内専用Base TempをExactに定める。
- 専用Base TempはこのRework Cycleが新規作成したものだけを対象にする。
- Completion HandoffにExact Path、作成、CleanupおよびPostflight状態を記録する。
- Existing User Data／`runtime_data/`をTest Fixtureに使用しない。
- Dependency Install／Network Downloadを行わず、既存Environmentだけを使う。

### 9.3 Evidence Class

- Command Resultは保持したTool Outputのみ`TOOL_LOG_VERIFIED`。
- Current File／Statusは現在のRead-only再検査だけ`REPOSITORY_STATE_VERIFIED`。
- Cycle全期間のRoot外0／Git Mutation 0／User Data 0等は、完全Action Logがなければ`SELF_REPORTED_UNVERIFIED`。
- FakeInferenceで`model_key`StringだけをQwenにしたTestを「実Qwen Runtime Test」と呼ばない。

## 10. Exact Allowed Scope

### Read

- Project Root内で本ReworkとValidationに必要なSource／Test／Frontend／Phase 3／Phase 4 Docs。
- `definitions/`はRead-only Validation Sourceとしてのみ読取可。

### Write／Modify

次のPhase 4 Reworkに直接必要な最小Pathだけを動的に選択する。使用しないPathは変更しない。

```text
src/margpa_runtime_llm/modules/runtime_governance/**
src/margpa_runtime_llm/adapters/runtime_governance/**
src/margpa_runtime_llm/bootstrap/runtime_governance.py

src/margpa_runtime_llm/modules/audit_evidence/**
src/margpa_runtime_llm/adapters/audit_evidence/**
src/margpa_runtime_llm/bootstrap/audit_evidence.py

src/margpa_runtime_llm/modules/configuration_control/**
src/margpa_runtime_llm/modules/governance_definitions/**
src/margpa_runtime_llm/bootstrap/configuration_control.py
src/margpa_runtime_llm/bootstrap/governance_definitions.py
src/margpa_runtime_llm/bootstrap/web_application.py
src/margpa_runtime_llm/entrypoints/web/main.py

src/margpa_runtime_llm/modules/conversation/application/conversation_generation.py
src/margpa_runtime_llm/web/**
frontend/src/**
frontend/index.html
src/margpa_runtime_llm/web/static/**

tests/unit/runtime_governance/**
tests/unit/audit_evidence/**
tests/unit/configuration_control/**
tests/unit/governance_definitions/**
tests/unit/conversation/test_conversation_generation_governance_hooks.py
tests/unit/web/**
tests/integration/audit_evidence/**
tests/integration/governance_definitions/**
tests/integration/web/**
```

Docs Writeは新規Append-onlyの次だけを許可する。

1. `docs/project/phases/phase_4/history/operations/phase_4_gov001_compaction_quota_resume_recovery_correction_ja_<timestamp>.md`
2. 必要ならFinding／Rework Evidence用の`docs/project/phases/phase_4/history/operations/phase_4_rework_..._<timestamp>.md`
3. `docs/project/phases/phase_4/handoffs/phase_4_claude_rework_complete_candidate_handoff_ja.md`

## 11. Forbidden

- Project Root外のRead／List／Stat／Write／Delete／Execute Target。
- `other/`、別Project、Provider Memory、Claude Memory、Codex Memory、External Service、Network、Secret／Credential。
- `runtime_data/`のRead／List／Stat／Write／Delete。
- `models/`のRead／List／Stat／Write／Delete／Load／Benchmark。
- `definitions/`のWrite／Rename／Delete／Format／Auto-fix。
- Stable Current／Shared／Roadmap／Phase Index／Requirements／Architecture／ADR／Execution Plan／Acceptance Matrixの編集。
- Existing History／Existing Handoffの編集／置換／削除。
- Git／GitHub Mutation、Commit／Push／Branch／Tag／Release。
- Phase 4 Closure／User Acceptanceの代行／Backup／Phase 5／6／DeepSeek／AWS。
- Frozen必須項目の任意Deferred化。
- Provider Summaryを唯一の正本とすること。
- Actionが実際に適用されていないのに`executed=true`と記録すること。

## 12. Completion Contract

Claudeは上記6 Technical Findingと1 Governance Findingをすべて自分の責任と権限の範囲内で修正／検証する。Routineな実装判断、Test失敗、Type Error、Frontend整合、Evidence Schema追加はユーザーへ返さず、Claudeが自己Review／Reworkする。

新たに次が必要になった場合だけ停止する。

- Project Root外。
- Stable／Frozen Contract変更。
- User Data／`runtime_data/`。
- Git／External／Network／Secret／Model Load。
- Phase 4の目的／Acceptanceそのものを変えるHuman Decision。

完了時は`phase_4_claude_rework_complete_candidate_handoff_ja.md`に次を必ず記録する。

```text
P4-CODEX-001..006              : CLOSED / OPEN
P4-GOV-001                     : CORRECTED / OPEN
Actual Local Entrypoint Wiring : PASS / FAIL
Canonical Mode Source         : Exact Component
Configuration CAS             : PASS / FAIL
Evidence Persistence          : PASS / FAIL
Status / Frontend             : PASS / FAIL
Empty / Invalid Enforce       : UNAVAILABLE / FAIL
Enforce Failure Policy        : PASS / FAIL
Action False-success          : 0 / N
Backend Focused / Full        : Exact Tool Output
Frontend Checks               : Exact Tool Output
Project-local Test Temp       : Exact Path / Postflight
Existing Stable Edit          : Exact Count
Git Mutation                  : Evidence Class付き
Root-outside Action           : Evidence Class付き
runtime_data Access           : Evidence Class付き
Remaining Technical Major     : Exact List
Remaining Governance Major    : Exact List
Recommendation                : GO / ADJUST / STOP
```

Complete Candidate Handoffを作成したら停止する。Phase 4 Closure、Git、Phase 5へ進まず、Codex Independent Re-reviewを待つ。
