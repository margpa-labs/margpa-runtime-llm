# Phase 6-G-WU-005 UI Naming Cleanup（Title Phase Suffix除去、部分完了）

```yaml
document_id: phase_6_g_wu005_title_suffix_removal
status: current_recovery_entry
phase: phase_6
subphase: phase_6_g
work_unit: p6_g_wu005_partial_title_suffix_only
role: Claude側設計統括者役
long_running_mode_active: true
created_at: 2026-08-23 01:18:00 JST
```

## Exact Mutation

```text
Modified:
  frontend/src/i18n/translations.ts
    （runtimeGovernanceTitle: "Main Runtime Governance（Phase 4）"→"Main Runtime Governance"、
      guardrailGovernanceTitle: "Guardrail Governance（Phase 5）"→"Guardrail Governance"、
      JA／EN両方）
  frontend/src/App.test.tsx（旧Phase Suffix付きTitle文字列のAssertion更新）
```

## 範囲判断

```text
対応済み: P6-ACC-059「Main Runtime GovernanceとGuardrail GovernanceからPhase Suffix除去」
          が明示的に名指しする2 Title Labelのみ変更。
意図的未対応:
  - governanceTitle（"Governance Definitions（Phase 3）"）: P6-ACC-059の名指し対象外
    （Main Runtime GovernanceとGuardrail Governanceのみ言及）。WU-005の別要件
    「Phase 3専用設定Panelは通常利用者向けSurfaceから整理し、内部Definition基盤は保持」は
    Panel自体のUI配置変更（削除ではなく再配置の可能性）を要し、Title文字列変更より
    大きいScopeのため、実際に何を「整理」と呼ぶか（非表示化／Deprecated化／統合先）を
    確定してから着手する。今回は拙速な削除・移動を避けた。
  - 各Panel本文中のRoadmap説明文（"Phase 4のARGD／DAGD..."等）: Architecture 11.1
    「Phase情報はDocs／Roadmap／Evidenceに保持する」の趣旨に沿った有用な現状説明であり、
    Title Labelとは別種（P6-ACC-059の対象はLabelのみ）。
  - Code Comment内のPhase番号（types.ts／App.tsxのBanner Comment）: 開発者向け内部Docs
    相当であり、利用者向けUIではないためP6-ACC-060の対象外。
  - src/margpa_runtime_llm/web/static/*.html／*.css：Phase 4/5文言なしを確認済み
    （legacy static UIには元々該当箇所が存在しなかった）。
```

## Validation

```text
Frontend Test    : 181 passed／21 files（回帰0）
Frontend Lint／Typecheck／Build: Clean
Full Backend     : 1388 passed／3 deselected（回帰0、Frontend専用変更のため影響なし確認目的）
Build出力確認     : app.js内runtimeGovernanceTitle／guardrailGovernanceTitleがPhase
                    Suffixなしで正しく反映されていることを実際のBuild成果物で確認。
```

## Next Exact Route

Phase 6-G-WU-005残り（Phase 3 Panel整理の具体的方針確定）、WU-004（Judge／Repair／
Recording UI）、WU-006（Browser Sync／Accessibility）へ進む。
