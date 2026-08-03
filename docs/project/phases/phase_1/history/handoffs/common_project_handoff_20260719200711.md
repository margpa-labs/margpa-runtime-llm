# MARGPA Runtime LLM 共通プロジェクト引き継ぎ

```yaml
document_state: current
created_at: 2026-07-19 20:07:11 JST
supersedes: common_project_handoff_20260719195134.md
project_root: margpa-runtime-llm/
```

## 1. Current Phase State

```text
Phase 1-A～1-E                       : Complete／Accepted
Phase 1 User Acceptance             : In Progress／Follow-up pending
Phase 1 Completion／Backup           : Waiting
Phase 2 Implementation               : Not Authorized
Lightning Dual Profile Design        : Accepted Planning Only
Lightning Implementation／Validation : Waiting Future Phase Authorization
```

変更のないProject識別、Role Authority、Backup Policy、Phase Evidenceは[common_project_handoff_20260719195134.md](common_project_handoff_20260719195134.md)を継承する。

## 2. Current Entry Points

- Current Index: [documentation_index_20260719200711.md](../documentation_index_20260719200711.md)
- User Acceptance補足: [phase_1_user_acceptance_findings_20260719195134.md](../user_manual/phase_1_user_acceptance_findings_20260719195134.md)
- Phase 1 Follow-up: [implementer_handoff_phase_1_acceptance_follow_up_20260719195134.md](implementer_handoff_phase_1_acceptance_follow_up_20260719195134.md)
- Lightning要件: [lightning_ai_studio_dual_runtime_profile_requirements_20260719200711.md](../requirements/lightning_ai_studio_dual_runtime_profile_requirements_20260719200711.md)
- Lightning Architecture: [lightning_ai_studio_cross_environment_architecture_20260719200711.md](../architecture/lightning_ai_studio_cross_environment_architecture_20260719200711.md)
- Lightning Handoff: [implementer_handoff_lightning_ai_studio_dual_runtime_profiles_20260719200711.md](implementer_handoff_lightning_ai_studio_dual_runtime_profiles_20260719200711.md)

## 3. Lightning Decision

Lightning AI StudioはLinux x86_64 Docker Containerであり、CUDAとCPUの2 Profileを用意する。

```text
CUDA: external.lightning-linux-x86_64.cuda
CPU : external.lightning-linux-x86_64.cpu
```

初期版は`--profile`で明示選択し、GPU未割当時の暗黙CPU Fallbackを行わない。

Confirmed Environment：

```text
Ubuntu 24.04.4／Linux 6.8.0／x86_64／Docker
Python 3.12.11／4 vCPU／15 GiB RAM／9 GiB Swap
Tesla T4 15,360 MiB／Driver 580.159.03／CUDA 13.0／nvcc 13.0.88
```

## 4. Implementation Findings

- Current Execution Environment Detectionは`native`固定で、Container Hookが必要。
- Current llama.cpp Device DetectorはMetal以外をCPU扱いし、CUDA Hookが必要。
- 同一HostへCUDA／CPUの複数Defaultは登録できないため、初期版はExplicit Profileとする。
- CUDA Buildを`gpu_layers=0`でGPU未割当CPU実行できるかはNative検証事項。

## 5. Phase Boundary

Lightning対応はDeployment／Adapter境界に閉じるため、後続Governance／UI CoreをBlockしない。Phase 1 Snapshotへ未検証Profileを混入させず、Lightning対応PhaseでSetup／Build／Profile／Native Testをまとめて実施する。

## 6. Authorization Boundary

本HandoffはSource／Config／Tests変更、Lightning Install、GPU利用、Model Transfer、Phase 2実装を許可しない。
