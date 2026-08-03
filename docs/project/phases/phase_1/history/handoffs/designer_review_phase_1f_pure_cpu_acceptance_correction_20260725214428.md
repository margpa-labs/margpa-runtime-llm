# Phase 1-F Pure CPU Acceptance Correction 設計再Review

- 文書ID: `designer_review_phase_1f_pure_cpu_acceptance_correction`
- 状態: `accepted_repository_external_native_pending`
- 作成日時: `2026-07-25 21:44:28 JST`
- 更新日時: `2026-07-25 21:44:28 JST`
- Snapshot: `20260725214428`
- 作成担当: 設計者役担当Task
- 対象Status: [implementer_status_phase_1f_pure_cpu_acceptance_correction_20260725214037.md](implementer_status_phase_1f_pure_cpu_acceptance_correction_20260725214037.md)
- Correction Handoff: [designer_handoff_phase_1f_pure_cpu_acceptance_correction_20260725212559.md](designer_handoff_phase_1f_pure_cpu_acceptance_correction_20260725212559.md)
- Previous Review: [designer_review_phase_1f_pure_cpu_repository_20260725212559.md](designer_review_phase_1f_pure_cpu_repository_20260725212559.md)
- 正本言語: 日本語
- supersedes: なし

## 1. Conclusion

前回のBlocking FindingとModel Path Contract Findingは解消された。

Phase 1-F Pure CPU Repository Follow-upをAcceptedとする。外部Lightning EnvironmentでのNative Build、Model LoadおよびGenerationは未実施であり、External Native AcceptanceはPendingのまま保持する。

## 2. Finding 1 Resolution

Native AcceptanceからCPU Runtimeの固定判定：

```text
runtime.acceleration_api == "cpu_native"
```

が除去された。

新しいPure Functionは、Runtimeと選択Profileを次で照合する。

```text
runtime.acceleration_api
  == application.config.compute.acceleration_api_key
```

結果：

```text
CUDA GPU                 : cuda
CUDA Build CPU Execution : cpu_native
Pure CPU Build           : none
Unknown／Mismatch        : Fail Closed
```

GPU／CPUそれぞれのOffload、Device KindおよびObserved State条件も維持されている。

## 3. Finding 2 Resolution

Model選択の正本を`--model-root`とし、Registryの`artifact.relative_path`から実Artifactを解決する。

```text
MODEL_ROOT
  + main/qwen3-4b/gguf/Qwen3-4B-Q4_K_M.gguf
```

既存`--model-path`は任意OverrideではなくCompatibility Validationとして維持された。

- Expected Relative Layout一致
- Model Root併用時の完全一致
- Invalid Layout拒否
- Root不一致拒否
- Newline Path拒否
- Smoke前のFile存在確認
- Actual Acceptanceへ同じModel Rootを渡す。
- ReportへResolved Artifactを記録する。

指定したArtifactと実際にLoadするArtifactが異なる状態は解消された。

## 4. Independent Plan Verification

RepositoryのCurrent Model Rootを指定し、Read-only Planを実行した。

```text
setup_lightning_linux_x86_64_cpu.sh
  --plan
  --model-smoke
  --model-root models
```

結果：

- Exit Code 0
- Pure CPU Plan表示
- Model Root解決
- Registry Relative Artifact解決
- Actual Qwen3 GGUF存在確認
- Environment変更なし

Public Review文書へAbsolute Local Pathは記録しない。

## 5. Independent Automated Verification

```text
pytest Full Suite             : 267 passed, 3 deselected
Pure CPU Targeted             : 9 passed, 1 deselected
Ruff Check                    : PASS
Ruff Format                   : PASS／95 files
Mypy                          : PASS／75 source files
Node Safe Markdown            : 5 passed
Shell Syntax                  : PASS
uv lock --check               : PASS／122 packages
```

`deselected`のExternal Native／Model SmokeをPassとは扱わない。

## 6. Code Review

確認した対象：

- `runtime_evidence_matches_profile`
- `all_required_checks_passed`
- Acceptanceへの`cli_model_root`
- Resolved Artifact Report
- Setup `--model-root`
- Compatibility `--model-path`
- Registry Path Traversal拒否
- Symlink／Resolved Path境界
- Invalid Compute Kind拒否
- Test Fixtureによる`cuda`／`cpu_native`／`none`

新たなBlocking Findingは確認しなかった。

## 7. Remaining External Gate

ユーザーがLightning CPU Environmentで実施する。

- Read-only Preflight
- Setup Plan
- Environment Reconstruction
- Pure CPU Native Build／Reuse確認
- Environment Verification
- Model Root確認
- Bounded Native Smoke
- SHA-512
- Model Load
- Japanese／English
- Streaming／Cancel
- Thinking
- Memory／Latency
- Shutdown

## 8. Final State

```text
Pure CPU Profile／Runtime Detection : ACCEPTED
Pure CPU Preflight／Setup           : ACCEPTED
Acceptance Contract Correction      : ACCEPTED
Repository Follow-up                : COMPLETE／ACCEPTED
External Native Acceptance          : PENDING
```

