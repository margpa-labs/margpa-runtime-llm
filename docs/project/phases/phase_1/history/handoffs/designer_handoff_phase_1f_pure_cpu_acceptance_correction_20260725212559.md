# Phase 1-F Pure CPU Acceptance Correction 実装担当Handoff

- 文書ID: `designer_handoff_phase_1f_pure_cpu_acceptance_correction`
- 状態: `changes_requested_ready_for_implementation`
- 作成日時: `2026-07-25 21:25:59 JST`
- 更新日時: `2026-07-25 21:25:59 JST`
- Snapshot: `20260725212559`
- 作成担当: 設計者役担当Task
- 対象: 実装者役担当Task
- 正本言語: 日本語
- Source Review: [designer_review_phase_1f_pure_cpu_repository_20260725212559.md](designer_review_phase_1f_pure_cpu_repository_20260725212559.md)
- Base Status: [implementer_status_phase_1f_pure_cpu_runtime_follow_up_20260725203508.md](implementer_status_phase_1f_pure_cpu_runtime_follow_up_20260725203508.md)
- supersedes: なし

## 1. Scope

LightningへUpload／再構築する前に、Pure CPU Native Acceptance Contractを局所修正する。

## 2. Required Fix A

対象：

```text
scripts/models/phase1f_cross_environment_acceptance.py
```

CPU Runtimeの`acceleration_api`を`"cpu_native"`へ固定せず、選択Profileの`compute.acceleration_api_key`と照合する。

維持する条件：

- GPU Offload未要求
- GPU Offload未観測
- Runtime GPU Offload False
- Device Kind CPU
- ProfileとAcceleration API一致

## 3. Required Fix B

`setup_lightning_linux_x86_64_cpu.sh`のModel指定Contractを明確化する。

推奨：

```text
--model-root MODEL_ROOT
```

- RegistryのRelative Artifact PathをMODEL_ROOTから解決する。
- 解決結果がFileであることを確認する。
- Smokeが実際にLoadするFileを表示する。
- `--model-path`を維持する場合はBackward CompatibilityとExpected LayoutをValidationする。
- 指定Fileと実際にLoadするFileが異なる状態を許可しない。
- ModelをDownloadしない。

## 4. Required Automated Test

- CUDA GPU Profile一致
- CUDA Build CPU Profileの`cpu_native`一致
- Pure CPU Profileの`none`一致
- Acceleration不一致Fail Closed
- Pure CPU `all_required_checks_passed`
- Model RootからExpected Artifact解決
- Invalid Layout拒否
- Specified ArtifactとLoaded Artifact一致
- Existing Help／Option非Regression

Actual Model Loadは外部Native GateとしてPendingでよい。

## 5. Non-goals

- External Lightning操作
- Dependency Install
- Model Download
- Profile再設計
- Web UI変更
- RAG
- Git／GitHub

## 6. Required Status

新規作成：

```text
docs/handoffs/implementer_status_phase_1f_pure_cpu_acceptance_correction_YYYYMMDDHHMMSS.md
```

記載：

- Changed Files
- Acceleration Match Fix
- Model Path／Root Contract
- Test Commands／Results
- External Native Pending
- Known Limitations

## 7. Completion Gate

Correction Statusを設計者役がReviewしAcceptedとするまで、Pure CPU Repository Follow-up全体を完了扱いにしない。

