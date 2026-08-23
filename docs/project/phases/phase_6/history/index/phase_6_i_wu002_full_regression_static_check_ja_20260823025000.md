# Phase 6-I-WU-002 Full Regression／Static Check（Backend＋Frontend）

```yaml
document_id: phase_6_i_wu002_full_regression_static_check
status: current_recovery_entry
phase: phase_6
subphase: phase_6_i
work_unit: p6_i_wu002_complete
role: Claude側設計統括者役
long_running_mode_active: true
created_at: 2026-08-23 02:50:00 JST
```

## 目的

Phase 6-H Comparative Experimentまでに蓄積したBackend／Frontendの全変更に対し、
P6-I（Integrated Verification）の入口としてFull Regression／Static Checkを実施し、
回帰0を確認する。

## 実行結果（Backend）

```text
Full Suite（非model_smoke既定）: 1403 passed, 5 deselected in 62.43s
model_smoke Suite             : 4 passed, 1 skipped, 1403 deselected in 20.08s
                                 （skip 1件はMARGPA_PHASE1F_PROFILE未設定による
                                   既存Non-scope Gate、回帰ではない）
Ruff                           : All checks passed!
Mypy                           : Success: no issues found in 418 source files
```

## 実行結果（Frontend）

```text
tsc --noEmit（typecheck）: エラー0
eslint .（lint）        : エラー0
vitest run --run（test）: Test Files 22 passed (22) / Tests 187 passed (187)
tsc --noEmit && vite build（build）: 成功
  出力: app.css 18.80kB(gzip 4.56kB), app.js 292.30kB(gzip 84.82kB)
```

## 結論

Backend／Frontend双方でErrorおよび既存Test回帰は0件。Phase 6-B～6-Hで追加した
全Domain／Application／Adapter／Web Route／Frontend Panelが、既存機構と整合した
まま共存していることを確認した。

## Next Exact Route

P6-I-WU-001（Adversarial／Fault Matrix）へ進む。次いでP6-I-WU-003（Real Browser
Golden Path、実Hardware Model Loadと実Settings UIを初めて統合した検証）、
P6-I-WU-004（Self-review／COMPLETE_CANDIDATE Handoff）の順で自走継続する。
