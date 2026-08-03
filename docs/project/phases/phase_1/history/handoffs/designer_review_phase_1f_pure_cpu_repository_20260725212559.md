# Phase 1-F Pure CPU Repository 設計Review

- 文書ID: `designer_review_phase_1f_pure_cpu_repository`
- 状態: `changes_requested`
- 作成日時: `2026-07-25 21:25:59 JST`
- 更新日時: `2026-07-25 21:25:59 JST`
- Snapshot: `20260725212559`
- 作成担当: 設計者役担当Task
- 対象Status: [implementer_status_phase_1f_pure_cpu_runtime_follow_up_20260725203508.md](implementer_status_phase_1f_pure_cpu_runtime_follow_up_20260725203508.md)
- 対象Handoff: [designer_handoff_phase_1f_lightning_pure_cpu_runtime_follow_up_20260725200001.md](designer_handoff_phase_1f_lightning_pure_cpu_runtime_follow_up_20260725200001.md)
- Preflight Addendum: [designer_handoff_phase_1f_lightning_pure_cpu_preflight_addendum_20260725201016.md](designer_handoff_phase_1f_lightning_pure_cpu_preflight_addendum_20260725201016.md)
- 正本言語: 日本語
- supersedes: なし

## 1. Conclusion

Pure CPU Profile、Runtime Detection、Preflight、Setup分離およびRepository Testの方向はAccepted Designと一致する。

ただし、外部Native Acceptanceを実行するScriptに新Pure CPU Profileと矛盾する判定が残っている。LightningへUpload／再構築する前に局所修正が必要であり、現時点のRepository Acceptanceは`CHANGES REQUESTED`とする。

## 2. Accepted Parts

- `lightning_linux_x86_64_cpu_native.toml`
- `build_variant = cpu`
- `device_kind = cpu`
- `acceleration_api = none`
- `gpu_layers = 0`
- `fallback = deny`
- Existing CUDA CPU Profile非変更
- Preflight三Target分離
- `--cpu-only`後方互換
- CPU-nativeでGPU／CUDA Command非実行
- Pure CPU Setup Script
- Normal Sync／Native Rebuild分離
- Model Download禁止
- External Native Validation Pending表示

## 3. Finding 1 — Native Acceptance Acceleration Mismatch

**Severity: High／External Acceptance Blocker**

対象：

```text
scripts/models/phase1f_cross_environment_acceptance.py
```

CPU Branchが次を固定している。

```text
runtime.acceleration_api == "cpu_native"
```

一方、新Pure CPU ProfileとRuntime Detectionは正しく次を返す。

```text
application.config.compute.acceleration_api_key = "none"
runtime.acceleration_api                       = "none"
```

このため、Pure CPU Runtimeが正しく動作しても`runtime_evidence_matches_profile`がFalseになり、Native Acceptance ReportはFailureになる。

### Required Correction

CPU BranchもProfile値と照合する。

概念形：

```text
runtime.acceleration_api
  == application.config.compute.acceleration_api_key
```

併せて、次を明示的にTestする。

- CUDA Build CPU Execution：`cpu_native`
- Pure CPU Build CPU Execution：`none`
- ProfileとRuntime不一致：Fail Closed

## 4. Finding 2 — `--model-path` Semantics

**Severity: Moderate／User Procedure Ambiguity**

Setup Helpは`--model-path PATH`を任意のLocal GGUF Pathとして説明している。しかしSmoke実行時はPathを4階層遡って`MARGPA_MODEL_ROOT`を作り、Default RegistryのRelative Pathを解決する。

したがって、指定Pathが次のLogical Layoutにあることを暗黙前提としている。

```text
MODEL_ROOT/main/qwen3-4b/gguf/Qwen3-4B-Q4_K_M.gguf
```

任意Pathを受理するContractではない。

### Required Correction

次のいずれかを採用する。

1. `--model-root`とRegistryを明示し、RegistryからArtifactを解決する。
2. `--model-path`がExpected Relative Layoutと一致することをFail Closedで検証する。
3. Acceptance ScriptへRegistry／Artifact Path Overrideを安全に追加する。

推奨は1である。User Procedureと実際にLoadされるArtifactを一致させ、別Fileを確認したふりをしない。

## 5. Test Gap

Repository Testは次を個別に確認している。

- Profileは`none`
- Runtime Detectionは`none`
- Verification Targetは`none`
- Integration TestはPure CPU Reportへ`none`を期待

しかし、Acceptance Script内部の`runtime_evidence_matches_profile`をPure CPU値で直接Testしていないため、矛盾を検出できなかった。

この判定をPure Functionへ抽出するか、Pure CPU Report Fixtureで`all_required_checks_passed`まで検証する。

## 6. Independent Verification

```text
pytest                         : 265 passed, 3 deselected
Pure CPU／Web Targeted         : 30 passed, 1 deselected
Ruff Check                     : PASS
Ruff Format                    : PASS
Mypy                           : PASS
Shell Syntax                   : PASS
uv lock --check                : PASS／122 packages
```

Test PassはRepository Contractの多くを支持するが、Finding 1の外部Acceptance Blockerを打ち消さない。

## 7. External State

次は未実施のままで正しい。

- Lightning Environment Reconstruction
- Pure CPU Native Build
- Model配置
- Native Model Load
- Generation
- Memory／Latency
- Public URL

Repository修正Review後にユーザー実行Gateへ進む。

## 8. Review State

```text
Profile／Preflight／Setup Direction : ACCEPTED
Repository Acceptance Script       : CHANGES REQUESTED
External Native Acceptance         : PENDING
Overall Pure CPU Follow-up          : NOT YET ACCEPTED
```

