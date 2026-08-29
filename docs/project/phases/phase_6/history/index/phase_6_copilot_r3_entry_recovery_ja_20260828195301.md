# Phase 6 Copilot R3 Entry Recovery

```yaml
document_id: phase_6_copilot_r3_entry_recovery_20260828195301
document_type: phase_package_entry_recovery_index
document_state: append_only
language: ja
created_at: 2026-08-28 19:53:01 JST
provider: GitHub Copilot app
role: 設計者兼実装者役
task_identity: Fresh Copilot Phase 6 Differential Continuation Task
package: P6-RR-R3
status: ENTRY
previous_completed_package: P6-RR-R2
current_source_state: PARTIAL_UNVERIFIED_PRESERVED
next_exact_work_unit: P6-RR-R3-WU-001_REDERIVATION_WITH_CURRENT_PARTIAL_PRESERVED
```

## Authority

Active Contractは`docs/project/phases/phase_6/handoffs/phase_6_copilot_post_claude_r3_to_r8_exact_continuation_handoff_ja_20260828193037.md`であり、SHA-512 `a71d747d4715c550ebc51de5c543bcd76be520329c500bfe57ac15a1bf079d67f14e249134e079d9f49a7c374de0ae7072fa63d1f0da0bb8d93d77baafba2bab`と照合済みである。

## Preserved Boundary

Phase 6 Package 0〜I、Claude K〜Q accepted scope、Rework R0〜R2は再実装禁止である。R3 Current Partial七FileをRollbackしない。P6-CODEX-064をR3で解消対象とし、P6-CODEX-065〜067は後続Package、P6-CODEX-068はR8で最終是正する。

## Current Partial Inventory

```text
src/margpa_runtime_llm/bootstrap/judge_live_integration.py
src/margpa_runtime_llm/web/runtime_governance_routes.py
src/margpa_runtime_llm/web/feature_modes_routes.py
frontend/src/types.ts
frontend/src/components/FeatureModesPanel.tsx
tests/unit/bootstrap/test_judge_live_integration.py
tests/unit/web/test_runtime_governance_routes.py
```

## Execution Isolation

Task-owned temporary rootは`.venv/.t/phase_6_copilot_continuation_20260828193037/`へ固定する。Git、Network、Provider Memory、User runtime_data、Root外Action、Real Model Actionは0として開始する。

## Exact Next Action

`P6-RR-R3-WU-001_REDERIVATION_WITH_CURRENT_PARTIAL_PRESERVED`
