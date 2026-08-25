# Phase 6 Seventh Rework — Package D Root外npm Log試行 STOPPED_SAFE Recovery Entry

```yaml
document_id: phase_6_seventh_rework_package_d_root_outside_npm_log_attempt_stopped_safe_20260824143020
status: stopped_safe
phase: phase_6
rework: seventh_rework_user_ui_runtime_model_semantic_enforcement
package: package_d_partial
owner_role: 設計者兼実装者役
created_at: 2026-08-24 14:30:20 JST
authority: phase_6_codex_designer_implementer_seventh_rework_exact_handoff_ja_20260824134921.md
previous_entry: phase_6_seventh_rework_package_c_current_runtime_identity_projection_ja_20260824141853.md
stop_condition: authorized_root_outside_filesystem_action_attempted
```

## Incident

Package DのBackend Focused TestとTargeted Mypy完了後、Frontend Typecheck／Test／Lintを連結したCommandで
`workdir` を`frontend/`ではなくProject Rootにした。`npm`はProject Rootに`package.json`がないため
ENOENTで失敗し、エラーLogをAuthorized Root外の次Pathに作成しようとした。

```text
/Users/Nazuna Research/.npm/_logs
```

Toolが返したExact Resultは次のとおり。

```text
npm error Log files were not written due to an error writing to the directory:
/Users/Nazuna Research/.npm/_logs
```

Tool出力上、Root外への永続Log Writeは成立していない。ただしRoot外Write Attempt自体がExact
Handoff §7.1のTrue Stop Conditionであるため、遡及許可や例外化を行わず即時停止した。Root外Pathの
Stat／List／Read／Cleanupは行っていない。

## State Before Stop

```text
Package A : COMPLETE
Package B : COMPLETE
Package C : COMPLETE
Package D : PARTIAL / implementation in progress
Package E : NOT STARTED
Package F : NOT STARTED
Package G : NOT STARTED
```

Package Dでは次を反映済み。

- Native／Backend／Deployment-Hardware Verified／Effective Context Limitの分離。
- ContextのEffective MaximumとMinimum 512によるController Preflight。
- Current AllocationをBackend Maximumと誤表示してShrink後のRe-expandを不可にする問題の修正。
- Runtime Model Status／Available ModelのTyped Capability Projection。
- Max New Tokens Default 2048とModel／Deployment／Loaded Context由来Upper Limitの分離。
- Target Model上限超過時のDefault 2048への収束。
- Generation RequestがCurrent Runtime Limitを超える場合とExact Remaining Contextを超える場合のTyped Rejection。
- UIのEffective Context Input Limit／Native／Backend／Hardware／Reason表示とTyped Mutation Error表示。

## Verification Completed Before Incident

```text
Package D Backend Focused Test : 63 passed / Exit 0
Package D Targeted Mypy        : 14 source files / 0 issues / Exit 0
Ruff targeted                  : PASS after mechanical import fixes
```

Current Frontendは、Latest Fixture／Dynamic Limit修正後のTypecheck／Test／Lintを未完了。Incidentが発生した
Commandの`npm`はすべてProject RootでENOENTのため、Frontend ValidationのEvidenceに使用しない。

## Package D Changed Files Before Stop

```text
src/margpa_runtime_llm/modules/runtime_model_control/ports.py
src/margpa_runtime_llm/modules/runtime_model_control/domain/snapshot.py
src/margpa_runtime_llm/modules/runtime_model_control/domain/errors.py
src/margpa_runtime_llm/modules/runtime_model_control/application/runtime_model_controller.py
src/margpa_runtime_llm/adapters/runtime_model_control/llama_cpp_backend.py
src/margpa_runtime_llm/bootstrap/runtime_model_control.py
src/margpa_runtime_llm/web/runtime_model_control_routes.py
src/margpa_runtime_llm/modules/conversation/contracts.py
src/margpa_runtime_llm/modules/conversation/application/conversation_generation.py
frontend/src/api/client.ts
frontend/src/types.ts
frontend/src/App.tsx
frontend/src/i18n/translations.ts
frontend/src/components/RuntimeModelStatusPanel.tsx
frontend/src/App.test.tsx
frontend/src/components/RuntimeModelStatusPanel.test.tsx
tests/unit/runtime_model_control/test_llama_cpp_backend.py
tests/unit/runtime_model_control/test_runtime_model_controller.py
tests/unit/runtime_model_control/test_dynamic_context_and_tokens.py
tests/unit/conversation/test_conversation_generation_runtime_snapshot.py
tests/unit/bootstrap/test_runtime_model_control_bootstrap.py
tests/integration/web/test_runtime_model_control_public_basic_call0.py
tests/integration/web/test_runtime_model_control_mutation_routes.py
```

Deleted Files: 0。Model Artifact Mutation: 0。

## Action Inventory

```text
Authorized Root外Filesystem Attempt : 1（npm error-log write attempt）
Authorized Root外Persistent Write   : 0 confirmed by Tool output; Root外inspectionは未実施
Provider Memory Internal Contact      : 0（本Cycle実行Log）
User runtime_data Contact             : 0（本Cycle実行Log）
Git Action                            : 0（本Cycle実行Log）
Network Action                        : 0（npmはpackage.json ENOENTでScript起動前に失敗）
Model Read／Load                     : 0（Package Dまで）
Model Artifact Mutation               : 0（本Cycle実行Log）
```

## Resume Boundary

ControllerのIndependent Reviewと新しいExact Resume Authorityなしに再開しない。再開時はPackage A〜Cをやり直さず、
Package DのCurrent Partialから差分再開する。Frontend CommandはExact `frontend/` WorkdirとProject内
`npm_config_cache=.venv/.t/phase_6_seventh_rework_20260824135445/npm_cache`を固定する。
