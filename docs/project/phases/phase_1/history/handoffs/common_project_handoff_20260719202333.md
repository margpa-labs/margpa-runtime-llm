# MARGPA Runtime LLM 共通プロジェクト引き継ぎ

```yaml
document_state: current
created_at: 2026-07-19 20:23:33 JST
supersedes: common_project_handoff_20260719200711.md
project_root: margpa-runtime-llm/
```

## 1. Scope Change

ユーザーの期限、Codex／GPT利用可能量、各PhaseのCross-environment検証方針により、Lightning対応を後続PhaseからPhase 1-Fへ前倒しする。

Phase 1完了後にBackupを取得し、そのSnapshotを一度公開する方針である。

## 2. Current State

```text
Phase 1-A～1-E                 : Complete／Accepted
Acceptance Follow-up           : Ready／Implementation Pending
Phase 1-F Lightning            : Accepted／Implementation Pending
Phase 1 User Acceptance        : Waiting
Phase 1 Completion／Backup     : Waiting
Phase 1 Publication            : Planned／Not Authorized
```

## 3. Python Decision

```text
Project Support : CPython >=3.12,<3.14
Mac Primary     : CPython 3.13.14
Lightning       : CPython 3.12.11
```

LightningのPythonを期限のためだけに3.13へ上げない。Metadata／Lock／Static Tool／Verifierを3.12／3.13両対応にする。

## 4. Lightning Gate

CUDAはPhase 1-F必須。CPUは実装対象だが、同一CUDA BuildでGPU未割当CPU実行が成立せず別Buildが期限を圧迫する場合、Evidenceとユーザー承認により公開後Follow-upへ延期できる。

## 5. Current Entry Points

- Current Index: [documentation_index_20260719202333.md](../documentation_index_20260719202333.md)
- ADR-0015: [adr_0015_phase_1f_lightning_and_python_312_support_20260719202333.md](../adr/adr_0015_phase_1f_lightning_and_python_312_support_20260719202333.md)
- Requirements: [phase_1f_lightning_cross_environment_runtime_requirements_20260719202333.md](../requirements/phase_1f_lightning_cross_environment_runtime_requirements_20260719202333.md)
- Architecture: [lightning_ai_studio_cross_environment_architecture_20260719202333.md](../architecture/lightning_ai_studio_cross_environment_architecture_20260719202333.md)
- Roadmap: [implementation_roadmap_20260719202333.md](../architecture/implementation_roadmap_20260719202333.md)
- Implementer Handoff: [implementer_handoff_phase_1f_lightning_cross_environment_runtime_20260719202333.md](implementer_handoff_phase_1f_lightning_cross_environment_runtime_20260719202333.md)

## 6. Publication Boundary

- GitHub Repository URLによるSource公開はPhase 1完了後の対象。
- Lightning Live Web URLはCurrent CLIだけでは成立せず、Web UI／API／Securityが別途必要。
- Git初期化、Remote作成、Push、公開設定はユーザーの別途明示許可を必要とする。

## 7. Next Action

ユーザーが実装担当Taskへ、Phase 1-F HandoffとAcceptance Follow-up Handoffの実装開始を指示する。

## 8. Authorization Boundary

本HandoffはSource／Config／Lock変更、Lightning外部操作、Git／GitHub操作を自動許可しない。
