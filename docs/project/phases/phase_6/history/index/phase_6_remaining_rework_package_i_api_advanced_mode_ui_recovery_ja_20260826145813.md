# Phase 6 Remaining Rework — Package I Recovery

```yaml
document_id: phase_6_remaining_rework_package_i_api_advanced_mode_ui_recovery_20260826145813
status: package_complete_next_active
package: P6-RR-I
completed_wus: [P6-RR-I-WU-001, P6-RR-I-WU-002, P6-RR-I-WU-003, P6-RR-I-WU-004, P6-RR-I-WU-005, P6-RR-I-WU-006]
created_at: 2026-08-26 14:58:13 JST
next_exact_work_unit: P6-RR-J-WU-001
```

## Result

- `/api/v6/provider-selection`にRole Provider GETと`/{role}` CAS PUTを追加した。MutationはExpected Revision／Digestを必須とし、Stale RevisionはHTTP 409、Unknown Providerは404、Invalid Roleは422のTyped Responseとする。
- ResponseはMain／Guard／JudgeのOption、Configured Provider、Active Provider、Runtime State、Independence、Failure Reason、検証状態付きStage Budgetを分離する。SelectionだけでActive／Loadedを表示しない。
- Advanced ModeにMain／Guardrail／Judgeの3 Dropdownを追加し、None、Built-in Rule／Pattern、Built-in Deterministic、Qwen、DeepSeek、Selene、Qwen3GuardのFrozen OptionをRole別に表示する。
- UIはConfigured／Active／State／Independence／Budget Profile／Verification State／Failure Reasonを別々に表示する。UnavailableをNone、ConfiguredをActiveとする代替表示は0。
- Provider MutationはFrontend Queueで直列化し、2回目は1回目のCanonical Revisionを使う。遅着GET／ResponseのLower Revisionは巻き戻さず、CAS Conflict時はTyped Code／Messageを表示してServer Canonical Stateを再取得する。
- Feature Mode StatusはCurrent Last ResultとHistorical Last Resultを別Field化し、OFF時や別Request実行中の過去結果をCurrentとして表示しない。
- Judge UIにRequest ID、Started／Completed、Frozen Mode、Configured／Active Provider、Budget、Criterion Count、Judge／Repair／Final Outcome、Failure Reason／Localized Messageを表示する。
- Frontend Production Bundleを再Buildし、FastAPI Static Rootの`index.html / app.js / app.css`をCurrent Sourceに同期した。

## Changed Source／Test

- `src/margpa_runtime_llm/web/provider_selection_routes.py`
- `src/margpa_runtime_llm/web/feature_modes_routes.py`
- `src/margpa_runtime_llm/web/app.py`
- `src/margpa_runtime_llm/modules/evaluation/domain/stage_budget.py`
- `tests/integration/web/test_feature_modes_routes.py`
- `frontend/src/types.ts`
- `frontend/src/api/client.ts`
- `frontend/src/components/ProviderSelectionPanel.tsx`
- `frontend/src/components/providerSelectionState.ts`
- `frontend/src/components/ProviderSelectionPanel.test.tsx`
- `frontend/src/components/FeatureModesPanel.tsx`
- `frontend/src/components/FeatureModesPanel.test.tsx`
- `frontend/src/components/SettingsModal/SettingsModal.tsx`
- `frontend/src/i18n/translations.ts`
- `src/margpa_runtime_llm/web/static/index.html`
- `src/margpa_runtime_llm/web/static/app.js`
- `src/margpa_runtime_llm/web/static/app.css`

## Validation

```text
Provider/Feature Web Integration: 13 passed / exit 0
Scoped Backend Mypy: 3 source/test entry files PASS / exit 0
Scoped Backend Ruff: PASS / exit 0
Frontend Typecheck: PASS / exit 0
Frontend Lint: PASS / exit 0 / warning 0
Frontend Full Test: 25 files / 225 passed / exit 0
Frontend Production Build: PASS / 50 modules transformed / exit 0
Frontend CAS/Race matrix: serialized revisions 1->2->3, lower revision rollback 0, conflict canonical reload PASS
Real Browser Screenshot: NOT RUN in Package I
Real Model: NOT RUN
```

Key SHA-512:

```text
Provider API:
4b859f15074b5189ea873b58bc827dd74c2219b5c3ae917febd0d011159e2b2099342d9c73209ee80ff4f246a81d04207da8436b03beb73c55c5e9c191816a70
Feature Mode API projection:
0a849a7503af18c4f36377e60b8018a3ca819b9bb8bb6757db9b5e528a78727588ac59a9ff39cc9659c444526f0341df88e1dd3a9a8a4cda74185eb7ee42875b
Provider UI:
f35cfdfcf565bcff7909caa57ca12f446591f8e48669beb287de871880d91c4535e42a0503ffc806accbabd2c6073a3493560951b7c27f97f597554358805dc4
Feature Mode UI:
400f989d114d01c362740d1ea447ac51b726c44172d76544b8f870b94cf2b07a9c631c1386f1582f53fd2e49e2f87c2cdb16693b278535e83e0c903369151318
Frontend API client:
71fa186e9ff764b121db74847196bcf18dc2fcdd945be60b86b8750670e4f09579cdb06521e364e483d1e105f2976b8cc43b4552bc0ae06e6c6db57ebade004b
Frontend types:
da3cee29495a9d3d7cdfed96340ea09ea71d4ac5cbf335547a9d367d8c8ef50d29e2668a5d20eb4a4407ec604cb8ca6c12ddb11175ddc2e135ae04f3bf02d836
```

## Acceptance／Finding

```text
P6-RR-ACC-009〜011: PASS / Three Role Dropdown Option RegistryとGET/CAS PUT API
P6-RR-ACC-012〜018: CURRENT PASS / Configured・Active・State・Independence UI/API; Real load remains NOT RUN
P6-RR-ACC-028〜030: CURRENT PASS / Failure Code・Localized Message projection
P6-RR-ACC-034: PARTIAL / Required correlation fields displayed; frozen_guard_mode remains unknown/null
P6-RR-ACC-035: PASS / Current and Historical Last Result are separate API/UI fields
P6-RR-ACC-038: NOT RUN / Real Browser Screenshot Gate remains Package J/User Gate
open_critical: 0
open_major: none introduced in Package I
open_non_critical: Real browser and frozen Guard Mode correlation remain open
```

## Authority／Incident Inventory

```text
current package root_outside/provider_memory/runtime_data/git/network/model_mutation: 0/0/0/0/0/0
historical P6-RR-INC-001 root-outside action: 1 retained
P6-RR-ACC-039: FAIL retained
active_process: 0
loaded_model_by_this_task: none
task_owned_temp: .venv/.t/phase_6_remaining_rework_claude_20260826093407/
claims_not_made: Real Browser PASS, Real Model PASS, Frozen Guard Mode Captured, Phase 6 Closure, Phase 7 Ready
```

`next_exact_work_unit: P6-RR-J-WU-001`
