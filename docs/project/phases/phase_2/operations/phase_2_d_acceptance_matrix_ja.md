# Phase 2-D Configuration Control Acceptance Matrix

```yaml
document_id: phase_2_d_configuration_control_acceptance_matrix
status: accepted_and_frozen_for_phase_2_d
phase: phase_2
subphase: phase_2_d
created_at: 2026-08-14 JST
owner_role: Phase 2設計担当者役
executor_role: Phase 2実装者役
```

## 1. Rule

全`required`がEvidence付きPASSでなければPhase 2-Dを完了としない。Implementerの自己判定で閉じず、Designer Conformance ReviewとController Closure Reviewを必須とする。

## 2. Exposure／Compatibility

| ID | Required acceptance | Evidence |
|---|---|---|
| P2D-EXP-001 | Local／Loopback／Auth disabled／Explicit opt-inだけがControl ServiceをBuild／Bind | Startup Matrix／Factory Spy |
| P2D-EXP-002 | Public／Basic／Non-loopback／Auth enabled+opt-inをService Build前にFail-closed | Negative Startup Test |
| P2D-EXP-003 | 通常Public／BasicはControl Build／Read／Write／Apply／Route Call 0、UI非表示 | Cross-profile Spy／Static Test |
| P2D-CMP-001 | Existing `/api/v1/**` Wire／SSE／Stop／Request Contract不変 | Existing Web Suite／Diff |
| P2D-CMP-002 | Persistent `/api/v2/conversations/**` Contract／Store／UX不変 | Persistent Suite／Spy |
| P2D-CMP-003 | Existing TOML Profile／Backend／Access Profile不変 | Path Diff／Config Regression |

## 3. Settings／Schema／Source

| ID | Required acceptance | Evidence |
|---|---|---|
| P2D-SEP-001 | User／Request SettingsはGlobal Config Mutationから分離 | Contract／Call Spy |
| P2D-SEP-002 | Research Mode Default off、Process-local、Restart Reset | Service Lifecycle Test |
| P2D-SEP-003 | Research Mode onでもAuthority／Policy／Tool Permission／Protected Capture変化 0 | Negative Authority Test |
| P2D-SCH-001 | Typed ContractがUnknown／Invalid／Oversize／Protected Fieldを拒否 | Schema Test |
| P2D-SCH-002 | ProjectionはExplicit AllowlistだけでArbitrary Map 0 | Contract Inspection／Test |
| P2D-SCH-003 | Secret／Environment Value／Raw Config／Path／Prompt／Thinking露出 0 | Sentinel Test |
| P2D-EFF-001 | Known FieldごとにExact Sourceを返し既存Precedenceを維持 | Source Matrix Test |
| P2D-EFF-002 | `runtime_override`はRuntime-applicable Fieldだけで最優先 | Service／Source Test |
| P2D-EFF-003 | Canonical SHA-512 Digestが順序非依存かつ同Stateで安定 | Digest Test |
| P2D-EFF-004 | Revisionは1開始、成功MutationだけIncrement | State Machine Test |
| P2D-EFF-005 | Environment Sourceは値／変数名を露出しない | Sentinel Test |

## 4. Preview／Apply

| ID | Required acceptance | Evidence |
|---|---|---|
| P2D-APL-001 | PreviewがRedacted Typed Diff／Dispositionを返しMutation 0 | Snapshot Before／After |
| P2D-APL-002 | ApplyがOperation ID／Expected Revision／Expected Digestを必須化 | Contract Test |
| P2D-APL-003 | Stale Revision／Digestは409／Mutation 0 | CAS Test |
| P2D-APL-004 | Applied Operation ID再送は409／Mutation 0 | Idempotency Test |
| P2D-APL-005 | Mixed Live／Restart／Unsupported PatchはPartial Apply 0 | Atomicity Test |
| P2D-APL-006 | No-opはRevision／Digest／State不変 | No-op Test |
| P2D-APL-007 | `research_developer_mode`だけLive Applyし、成功時にRevision／Digest更新 | Apply Test |
| P2D-APL-008 | Restart-required ProposalはResultだけでFile／Browser／Runtime DataへStage 0 | Filesystem／Storage Spy |

## 5. Hooks／Privacy

| ID | Required acceptance | Evidence |
|---|---|---|
| P2D-HOK-001 | RAG Hookが`disabled／enabled`をTyped Projectionし、変更はRestart-required | Hook Unit Test |
| P2D-HOK-002 | Recording HookはOFF Read-only、Metadata／Full拒否、Recorder Call 0 | Hook／Spy Test |
| P2D-HOK-003 | Protected Capture／Agent／Tool／Switchboard Field／Call 0 | Schema／Call Spy |
| P2D-PRV-001 | Browser StorageへSnapshot／Diff／Research Mode／Secret／Path保存 0 | Static／Browser Test |
| P2D-PRV-002 | Unbound RouteはSafe 404でConfig存在／Source／Path Detail 0 | Cross-profile API Test |
| P2D-PRV-003 | Root BootstrapはBooleanだけでConfig Data埋込み 0 | HTML Contract Test |
| P2D-PRV-004 | Tracked TOML／Environment／CLI／Conversation StoreへのWrite 0 | Diff／Spy Test |
| P2D-PRV-005 | Process Restart後はTrusted Startup Inputsから再構築 | Lifecycle Test |

## 6. UX／Quality Gates

| ID | Required acceptance | Evidence／Command |
|---|---|---|
| P2D-UX-001 | Local enabled時だけControl Panelを表示しEffective／Source／Digest／Revisionを表示 | DOM／Integration Test |
| P2D-UX-002 | Preview／Apply／Conflict／Restart-requiredをja／enで安全表示 | DOM／Manual Matrix |
| P2D-UX-003 | Existing Chat／Persistent UX、Keyboard／Focus／Mobile Layoutを回帰維持 | Existing Static／Manual Matrix |
| P2D-QA-001 | Target Tests PASS | Handoff Target Command |
| P2D-QA-002 | Config／Conversation／Web Regression PASS | Handoff Regression Command |
| P2D-QA-003 | Static JS Security PASS | Node／Pytest Static Tests |
| P2D-QA-004 | Ruff Format／Check、Mypy PASS | Standard Commands |
| P2D-QA-005 | Full Suite PASS／Project Root Runtime Data 0 | `.venv/bin/pytest -q`／Inventory |

## 7. Closure Output

```text
Implementer -> Designer:
  exact changes / acceptance map / tests / boundaries / rollback / findings

Designer -> Controller:
  PASS | REWORK | STOP
  exact required failures
  closure recommendation GO | ADJUST | STOP
```

## 8. Deferred Non-blockers

Settings Persistence、Concrete Recording、Protected Research Capture、Agent／Tool／Switchboard、Dependency／Conflict Resolution、Remote／Multi-user ControlはPhase 2-D Acceptanceに含めない。新EvidenceまたはTriggerなしにCurrent Blockerへ再活性化しない。
