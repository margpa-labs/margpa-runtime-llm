# Phase 1-F Lightning Pure CPU Preflight 実装担当Addendum

- 文書ID: `designer_handoff_phase_1f_lightning_pure_cpu_preflight_addendum`
- 状態: `accepted_ready_for_repository_implementation`
- 作成日時: `2026-07-25 20:10:16 JST`
- 更新日時: `2026-07-25 20:10:16 JST`
- Snapshot: `20260725201016`
- 作成担当: 設計者役担当Task
- 対象: 実装者役担当Task
- 正本言語: 日本語
- Base Handoff: [designer_handoff_phase_1f_lightning_pure_cpu_runtime_follow_up_20260725200001.md](designer_handoff_phase_1f_lightning_pure_cpu_runtime_follow_up_20260725200001.md)
- Requirements: [phase_1f_lightning_pure_cpu_runtime_follow_up_requirements_20260725200001.md](../requirements/phase_1f_lightning_pure_cpu_runtime_follow_up_requirements_20260725200001.md)
- Accepted ADR: [adr_0022_lightning_pure_cpu_and_optional_component_hook_only_profile_20260725200001.md](../adr/adr_0022_lightning_pure_cpu_and_optional_component_hook_only_profile_20260725200001.md)
- supersedes: なし

## 1. Addendum Conclusion

Lightning側の環境再構築とNative Testはユーザーが実施する。実装担当は、ユーザーが前回と同様に再構築前の確認を一括実行できるPreflightをRepositoryへ用意する。

## 2. Existing Script

既に次が存在する。

```text
scripts/setup/preflight_lightning_ai_studio.sh
```

重複Scriptを無条件に増やさず、まずExisting Scriptを後方互換のまま拡張する。

Current `--cpu-only`は「CUDA BuildをCPU実行し、GPU Allocationだけ要求しない」という意味を持つ。Pure CPU Buildへ意味を変更してはならない。

## 3. Required Target Separation

明示的なRuntime Targetを追加する。

候補：

```text
--runtime-target cuda-gpu
--runtime-target cuda-cpu
--runtime-target cpu-native
```

互換性のため、既存Optionを維持する。

```text
Default       : current cuda-gpu semantics
--cpu-only    : current cuda-cpu semantics
cpu-native    : new pure CPU semantics
```

Option名はCurrent CLI Styleへ合わせて調整可能だが、三つの意味を混同しない。

## 4. CPU-native Preflight

確認するもの：

- Linux
- x86_64
- Container
- Environment Mode
- Python 3.12.11
- Project指定の`uv`
- CPU Count
- Available Memory
- Project／Environment PathのRead／Write条件
- Pure CPU Profileの存在とParse可能性
- Model RootのOptional Presence

呼び出さないもの：

- `nvidia-smi`
- `nvcc`
- CUDA Compiler
- GPU Allocation Probe

CPU-native経路では`nvcc available`をInformational表示するためにも実行しない。

## 5. Setup Script

Base Handoffどおり、次を作成する。

```text
scripts/setup/setup_lightning_linux_x86_64_cpu.sh
```

PreflightはRead-onlyとし、Environment作成、Dependency Install、Native BuildおよびModel配置はSetup Scriptと明確に分離する。

Setup Scriptはユーザー実行用であり、実装担当は外部Lightning環境を操作しない。

## 6. User-facing Procedure

実装報告へ、ユーザーがLightningで順番に実行できるCommandを記載する。

最低限：

1. Preflight Help
2. CPU-native Read-only Preflight
3. Setup Dry-runまたはPlan表示
4. Environment Setup
5. Environment Verification
6. Model Path確認
7. Bounded Smoke
8. Exit Code確認

Project Upload、Model Upload、Credential設定および公開URL操作を自動化しない。

## 7. Automated Test

- Existing Default Behavior
- Existing `--cpu-only` Behavior
- New CPU-native Behavior
- CPU-nativeがGPU Commandを呼ばない。
- Unknown Target Fail Closed
- HelpにTarget差を表示する。
- Shell Syntax
- Mocked Host／Tool Availability
- Macからの誤実行拒否

## 8. Required Status Report

Base HandoffのReportへ次を追加する。

- Existing Preflightを拡張したか、別Scriptが必要だったか
- その判断理由
- Targetごとの意味
- Backward Compatibility
- CPU-nativeで実行しないCommand
- User-run Rebuild Procedure
- External Native Test Pending

## 9. Authorization Boundary

Preflight、Pure CPU Setup Hook、ProfileおよびTestのRepository実装へ着手可能である。

外部Lightning操作、Dependency Install、Model配置、Upload、公開およびNative Acceptanceは許可範囲外である。

