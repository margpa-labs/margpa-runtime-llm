# Phase 6 Special Minimal Closure／Phase 7 READY Recovery

```yaml
document_id: phase_6_special_minimal_closure_and_phase_7_ready_recovery_20260829171422
document_state: recovery_current
language: ja
created_at: 2026-08-29 17:14:22 JST
phase_6: closed_with_known_debt
phase_7: ready_not_armed
```

## Completed Boundary

- Phase 6 User Manual FailureをP6-GOV-026へ固定。
- User OverrideをP6-GOV-027へ固定。
- Stable未解決RegistryとSnapshotを作成。
- Controller全面反省とPoC／MVP Policy補正を作成。
- 指定UI 4件を修正し、User実画面で確認。
- Phase 7 Requirements／Architecture／ADR／Execution Plan／AcceptanceをFreeze。
- Claude／Copilot前倒し候補を更新。
- Phase 6特殊最小Closureを確定。
- Phase 7 READY設計状態を確定。
- Canonical再検証：Backend 1811 passed／7 deselected、Mypy 483 files、Ruff PASS、Frontend 25 files／232 tests、Typecheck／Lint／Build PASS。
- 誤ったMarker指定で実Model 6件を混入させた初回実行はCanonical Evidenceから分離し、`Failed to create llama_context`として保持。

## Known Debt

Selene、Qwen3Guard、Semantic 109、Built-in Judge、Repair／Rejudge、回答品質およびPhase 9送りUIは未解決Registryへ保持する。

## Remaining Sequence

```text
Roadmap／Current／Index最終整合: COMPLETE
Canonical Check: COMPLETE
Commit／Push
Backup
Phase 7 Preflight
Phase 7 Activation
Claude Exact Handoff／Instruction
```

5時間制限等で停止した場合は、最後に完了した行から差分再開する。
