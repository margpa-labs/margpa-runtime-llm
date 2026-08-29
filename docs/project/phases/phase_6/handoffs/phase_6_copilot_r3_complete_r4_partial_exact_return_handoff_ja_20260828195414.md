# Phase 6 Copilot R3 Complete / R4 Partial Exact Return Handoff

```yaml
document_id: phase_6_copilot_r3_complete_r4_partial_exact_return_handoff_20260828195414
document_type: exact_return_handoff
document_state: append_only
provider: GitHub Copilot app
role: 設計者兼実装者役
task_identity: Fresh Copilot Phase 6 Differential Continuation Task
active_contract_sha512: a71d747d4715c550ebc51de5c543bcd76be520329c500bfe57ac15a1bf079d67f14e249134e079d9f49a7c374de0ae7072fa63d1f0da0bb8d93d77baafba2bab
state: INCOMPLETE_SAFE_RETURN
maximum_claim: R3_COMPLETE_CANDIDATE_R4_PARTIAL
next_exact_work_unit: R4-WU-004
```

## Package Disposition

| Package | Disposition |
|---|---|
| Phase 6 0〜I / Claude K〜Q accepted scope / Rework R0〜R2 | PRESERVED / redo prohibited |
| R3 | COMPLETE_CANDIDATE |
| R4 | PARTIAL: WU-001〜003 complete, WU-004〜006 not started |
| R5〜R8 | NOT STARTED |

## R3 Re-derivation and Findings

R3 Current Partial七FileをRollbackせず、ARGD 53＋DAGD 56の109件、Frozen Request、exactly-once Result、Reason分離、Count、Post Projection、late publication拒否をCurrent Source/Testから再導出した。不足は、選択外77件をFrozen Snapshotで明示し、Provider Failureを`malformed_result`と区別し、Live Countの`evaluated`をPASS/DEVIATIONに限定する差分である。

P6-CODEX-064はFixture／Static／Focused Regression範囲で解消候補。P6-CODEX-065はR4-WU-001〜003のみ進行し、Frozen Repair Rejudge wiringが未完。P6-CODEX-066〜068はOPENのまま保持する。

## Verification / Authority

R3 Focused 59件、R4 Focused 48件、対象Mypy/Ruff Checkは成立した。Real Selene/Qwen3Guard、Network、Real Modelは`NOT RUN / AUTHORITY REQUIRED`である。

Historical Unauthorized Git Readは1を保持する。今回のAction InventoryはGit 0、Network 0、Provider Memory 0、User runtime_data 0、Project Root外Action 0、Real Model Load/Inference 0、Backup 0である。

## Recovery Index

- `history/index/phase_6_copilot_r3_final_recovery_ja_20260828195408.md`
- `history/index/phase_6_copilot_r4_partial_recovery_ja_20260828195413.md`

## Changed Source / Test SHA-512

```text
src/margpa_runtime_llm/bootstrap/judge_live_integration.py
4fba1e467241e1cb4b1b8c3772649099540b19896f685fdc3dde6c088dc405bda794af500329d16515efc7340b2883c525a308c1fd0f206931519cca0f243a7d
src/margpa_runtime_llm/modules/runtime_governance/application/semantic_runtime.py
9f240f2a6c8f0cf5db8e5b1c4a771d1a2f06ad619a207ae4029c750b7d43e0820dc5c6a665b9aabc433860af49d500605d05ef4acc855cf8a3c9a0cfeb5f7bd7
src/margpa_runtime_llm/modules/runtime_governance/domain/semantic_runtime.py
9da333991a2785426bc6b303b9086b43ab5118e5a0f2fbfa2880d6df0fc13b9ce25d7ebb1cca6a8c753755a660a33f56af6d7611b44fc0a5cff306d60c83ab24
src/margpa_runtime_llm/modules/runtime_governance/domain/semantic_criteria.py
a8fc5f6e11710cc92ed76593ec65570a3f1d6a8f31eb518db89b13646a405d477696810f2fce4e696240b45e6888220bc118e65ae9de4ee38c2580b4cf3e732b
src/margpa_runtime_llm/modules/evaluation/domain/stage_budget.py
04c1bab4953338fa608a4fb997b3c8a1586309f8bee558fb93d1ac925e3e3e35b15e55c9653fb774f0f1ab37d8478e341f924525eb59021b0251448b38f2bb80
```

## Exact Next Action

`R4-WU-004`として、Repair ExecutorへFrozen Judge Adapter/Identity/Budgetを渡し、Repair Rejudgeがconfigured/current providerを再読またはMainへ暗黙FallbackしないことをFixtureで検証する。その後R4-WU-005、R4-WU-006、R5〜R8を元Exact Rework Contract順に実施する。
