# Phase 6-G-WU-004 Judge／Repair／Recording UI Recovery Entry（Real Browser検証済み）

```yaml
document_id: phase_6_g_wu004_feature_modes_recovery
status: current_recovery_entry
phase: phase_6
subphase: phase_6_g
work_unit: p6_g_wu004_complete_mode_toggle_only
role: Claude側設計統括者役
long_running_mode_active: true
created_at: 2026-08-23 01:48:00 JST
```

## Exact Mutation

```text
Created:
  src/margpa_runtime_llm/modules/evaluation/application/judge_mode_controller.py
  src/margpa_runtime_llm/modules/repair/application/repair_mode_controller.py
  src/margpa_runtime_llm/modules/runtime_observability/application/recording_mode_controller.py
  src/margpa_runtime_llm/web/feature_modes_routes.py（GET /status、POST /judge／repair／recording）
  tests/unit/evaluation/test_judge_mode_controller.py
  tests/unit/repair/test_repair_mode_controller.py
  tests/unit/runtime_observability/test_recording_mode_controller.py
  tests/integration/web/test_feature_modes_routes.py（6 Test、独立性を直接検証）
  frontend/src/components/FeatureModesPanel.tsx
  frontend/src/components/FeatureModesPanel.test.tsx（4 Test）
Modified:
  src/margpa_runtime_llm/web/contracts.py（WebRuntimeへjudge/repair/recording_mode_control追加）
  src/margpa_runtime_llm/web/app.py（Import、Local-loopback Gate、include_router）
  frontend/src/types.ts、api/client.ts、i18n/translations.ts（JA／EN）
  frontend/src/components/SettingsModal/SettingsModal.tsx（FeatureModesPanel配線）
```

## 設計判断

```text
3独立Mode Controller: GuardrailModeControllerと同型（Lock＋Revision＋Current Mode、
                       CAS Token不要のUnconditional Apply）だが、EvaluationMode／
                       RepairMode／RecordingModeという既存Domain固有Enumをそのまま使い、
                       GovernanceModeへの統合はしない（P6-ACC-025「独立」を型でも保証）。
Scope限定            : 本WUはMode Toggle＋Status表示のみ。Budget／Failure表示は、
                       実Generation Flowへの接続（Repair Orchestrator実配線、Recording
                       Writer実装）が先に必要なため、捏造を避けて後続へ委譲。
                       Mode変更はConversation Generationへの実際の介入を伴わない
                       （Controller単体はReport専用、実効化は別Wiring）。
Local-loopback Gate  : 3 Controllerのいずれか1つでもBoundなら他Compositionと同じGateを適用。
```

## Real Browser検証（実施済み、model_smoke非該当）

```text
検証方法: test_feature_modes_routes.pyのbound_runtime相当（3 Controller実Bind）で
          Server起動、Settings→Advanced ModeでJudge Mode「enforce」をClick。
確認結果: Judge Modeのみenforceへ変化、Repair／Recordingは両方offのまま
          （Network Request実測でPOST /judge 200 OK）、「Applied.」表示、Console Error 0。
Server後処理: Preview ServerとBrowser Tabを終了・破棄。
```

## Validation

```text
Backend New Test  : 15 passed（Controller単体9、Route Integration 6）
Frontend New Test : 4 passed
Full Backend      : 1403 passed／3 deselected（回帰0）
Full Frontend      : 185 passed／22 files（回帰0）
Ruff／Mypy／ESLint／Typecheck: 全てClean
Frontend Build     : Success
```

## Next Exact Route

Phase 6-G-WU-006（Browser Sync／Accessibility：Settings再Open／Reload／別Tab同期、
CAS Conflict、Keyboard／Focus検証）、またはPhase 6-H（Comparative Experiment）へ進む。
