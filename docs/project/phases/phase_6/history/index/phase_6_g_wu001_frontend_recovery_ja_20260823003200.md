# Phase 6-G-WU-001 Frontend Recovery Entry（Model Status Panel、Real Browser検証済み）

```yaml
document_id: phase_6_g_wu001_frontend_recovery
status: current_recovery_entry
phase: phase_6
subphase: phase_6_g
work_unit: p6_g_wu001_complete
role: Claude側設計統括者役
long_running_mode_active: true
created_at: 2026-08-23 00:32:00 JST
```

## Exact Mutation

```text
Created:
  frontend/src/components/RuntimeModelStatusPanel.tsx
  frontend/src/components/RuntimeModelStatusPanel.test.tsx（4 Test）
Modified:
  frontend/src/types.ts（RuntimeModelStatus／MainIdentity／JudgeIdentity型追加）
  frontend/src/api/client.ts（fetchRuntimeModelStatus()追加）
  frontend/src/i18n/translations.ts（runtimeModel* Key、JA／EN、Phase番号Suffixなし）
  frontend/src/components/SettingsModal/SettingsModal.tsx
    （RuntimeModelStatusPanelを配線。advancedTabVisible変数を削除し
      Advanced Tabを常時表示化——本Panelは既存4機能と異なりBootstrap Flagを
      持たないため）
  frontend/src/components/SettingsModal/SettingsModal.test.tsx
    （既存Test「全4 Bootstrap Disabled時はAdvanced Mode非表示」を、新Panelが
      常時存在する現実に合わせて書き換え。旧期待値の消去ではなく仕様変更の反映）
```

## Real Browser検証（実施済み、model_smoke非該当）

```text
検証方法: 実Qwen GGUF Model Loadは行わず（6-I Real Browser Golden Path用に留保）、
          tests/integration/web/test_runtime_model_control_public_basic_call0.py の
          bound_runtime() Fixture（Fake RuntimeModelController）でcreate_web_app()を
          起動し、実Browser（Claude Browser Pane）でSettings→Advanced Modeを開いて
          目視確認した。
確認項目  : JA表示（Model Status、再読み込み、Revision／Current Main Model／State／
            Context Size／Max New Tokens／Current LLM-as-a-Judge Model＝未設定）、
            EN表示（同項目の英語化）、Refresh Button動作、Console Error 0。
            Screenshot 3枚（JA初期表示、JA Refresh後、EN表示）で確認、全て一致。
Server後処理: 確認後、Preview Server（127.0.0.1:8799）とBrowser Tabを終了・破棄。
              本番Repositoryへの変更は0（Scratchpad一時Scriptのみ使用）。
```

## Validation

```text
Frontend Lint       : Clean
Frontend Typecheck  : Clean
Frontend Test       : 179 passed／21 files（既存175 + 新規4、既存1件書き換え）
Frontend Build      : Success
```

## Next Exact Route

Phase 6-G-WU-001／WU-002の主要部分が完了。残るWU-003（Context／Token Control UI、
Preview/Apply操作を伴うためRuntimeModelController側にApply用Endpointが必要）、
WU-004（Judge／Repair／Recording UI）、WU-005（Naming／Legacy Cleanup、既存
Phase Suffix除去はP6-ACC-059/060として別途対応要）、WU-006（Browser Sync／
Accessibility）へ進む。
