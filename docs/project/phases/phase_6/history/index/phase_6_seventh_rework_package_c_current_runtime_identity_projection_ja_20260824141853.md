# Phase 6 Seventh Rework — Package C Current Runtime Identity Projection完了Recovery Entry

```yaml
document_id: phase_6_seventh_rework_package_c_current_runtime_identity_projection_20260824141853
status: recovery_entry_complete
phase: phase_6
rework: seventh_rework_user_ui_runtime_model_semantic_enforcement
package: package_c
owner_role: 設計者兼実装者役
created_at: 2026-08-24 14:18:53 JST
authority: phase_6_codex_designer_implementer_seventh_rework_exact_handoff_ja_20260824134921.md
previous_entry: phase_6_seventh_rework_package_b_ui_immediate_mode_apply_ja_20260824140751.md
next_package: package_d
```

## Completed

- ServerがRuntime Model ControlをBindした場合だけ`runtime-model-control-bootstrap` MarkerをEnableにするCapability Negotiationを追加し、Disable時のRoute Probeを0にした。
- Appに単一のCanonical Runtime Model Snapshot Stateを設け、SidebarとAdvanced Model Statusが同じAccepted RevisionからCurrent Main Model／State／Contextを投影するようにした。
- Initial Load、1.5秒Poll、明示Refresh、Context／Max Tokens／Model SwitchのMutation Responseを同一Snapshot Acceptance Pathへ集約し、遅延Responseが新しいRevisionを上書きしないようにした。
- API／Type／LabelでConfigured Startup DefaultとCurrent Loaded Modelを分離した。
- `main_self` Judgeは専用Judge Artifact未設定と区別し、現在のMain Model Keyと`main_self`独立性をProjectionで表すようにした。
- Model Switch FailureはLocal SelectorをCanonical Current ModelへRollbackした後に共有Snapshotを再取得する。
- Reloadおよび別Tabで変更された想定の新Revisionが、Refresh後にSidebar／Advanced／Judge Identity／Context Inputへ同時収束するInteraction Testを追加した。

## Exact Changed Files

```text
frontend/index.html
frontend/src/App.tsx
frontend/src/App.test.tsx
frontend/src/types.ts
frontend/src/i18n/translations.ts
frontend/src/lib/runtimeModelControlBootstrap.ts
frontend/src/lib/runtimeModelControlBootstrap.test.ts
frontend/src/components/RuntimeModelStatusPanel.tsx
frontend/src/components/RuntimeModelStatusPanel.test.tsx
frontend/src/components/SettingsModal/SettingsModal.tsx
frontend/src/components/SettingsModal/SettingsModal.test.tsx
src/margpa_runtime_llm/web/static/index.html
src/margpa_runtime_llm/web/app.py
src/margpa_runtime_llm/web/runtime_model_control_routes.py
src/margpa_runtime_llm/modules/runtime_observability/projection/component_identity_projection.py
tests/integration/web/test_runtime_model_control_public_basic_call0.py
tests/unit/runtime_observability/test_component_identity_projection.py
```

Deleted Files: 0。

## Verification

```text
Frontend Typecheck                 : PASS／Exit 0
Frontend Full Test                 : 24 files／218 tests PASS／Exit 0
Frontend Lint                      : PASS／Exit 0
Backend Runtime Model/Web Focused  : 66 tests PASS／Exit 0
```

Backend FocusedはPublic Call-0／Bootstrap Marker／Mutation Routes／Governance Layer Identity／Component Identity Projection／Web Appを含む。Real Browserの独立2 Tab AcceptanceはPackage G User Gateのままとし、ここで代行PASSを主張しない。

## Acceptance Delta

```text
P6-RW7-MODEL-001 : PASS（Shared App Snapshot／Sidebar／Advanced Interaction Test）
P6-RW7-MODEL-002 : PASS（Configured Startup vs Current Loaded typed/API/UI separation）
P6-RW7-MODEL-003 : PASS（main_self Judge current model projection）
P6-RW7-MODEL-004 : PASS（Switch success/failure rollback／Reload／other-tab revision convergence tests）
```

## Action Inventory

```text
Authorized Root外Filesystem Action : 0（本Cycle実行Log）
Provider Memory Internal Contact    : 0（本Cycle実行Log）
User runtime_data Contact           : 0（本Cycle実行Log）
Git Action                          : 0（本Cycle実行Log）
Network Action                      : 0（本Cycle実行Log）
Model Artifact Mutation             : 0（本Cycle実行Log）
```

## Exact Next Action

Package DでContext／Max New TokensのNative／Backend／Deployment／Effective Capabilityを分離し、入力時と実Generation Request時のTyped Validationを同じCanonical Contractへ収束させる。
