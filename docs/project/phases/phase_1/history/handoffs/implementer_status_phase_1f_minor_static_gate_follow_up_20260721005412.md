# 実装担当 Phase 1-F Minor Static Gate Follow-up Status

- 文書ID: `implementer_status_phase_1f_minor_static_gate_follow_up`
- 状態: `minor_follow_up_complete_waiting_designer_review`
- 作成日時: `2026-07-21 00:54:12 JST`
- 更新日時: `2026-07-21 00:54:12 JST`
- Snapshot: `20260721005412`
- 作成担当: 実装担当Task
- 正本言語: 日本語
- Documentation Index: [documentation_index_20260721003201.md](../documentation_index_20260721003201.md)
- Review: [designer_review_phase_1f_repository_follow_up_20260721003201.md](designer_review_phase_1f_repository_follow_up_20260721003201.md)
- Phase 1-F Handoff: [implementer_handoff_phase_1f_lightning_cross_environment_runtime_20260719202333.md](implementer_handoff_phase_1f_lightning_cross_environment_runtime_20260719202333.md)
- supersedes: `implementer_status_phase_1f_repository_review_follow_up_20260721001705.md`

## 1. Authorization／Scope

ユーザーの「最新のIndexとReviewを読んで作業」指示に基づき、Review Section 3.1のFull Project Mypy Failureと、Section 5のAccepted Setting Decisionだけを変更した。

変更範囲は`config/application.toml`、局所Source／Tests、本Implementer Statusである。Canonical Requirements／Architecture／Governance／ADR／Index／Review、Lightning外部環境、Phase 1-G、Backup、Git／GitHubは変更していない。

## 2. Current State

```text
Full Project Mypy Finding       : Resolved
generation.max_new_tokens       : 2048／Applied
Full Static／Default Gate       : Pass
Lightning Read-only Preflight   : Not Run
Lightning CUDA／CPU Native Gate : Not Run
Phase 1-F Completion            : Not Claimed
Phase 1-G                       : Not Started／Not Authorized
```

## 3. Changed Files

- `config/application.toml`
- `src/margpa_runtime_llm/adapters/model_backends/llama_cpp/runtime_detection.py`
- `tests/unit/inference/test_deployment_platform.py`
- `tests/unit/inference/test_config_and_registry.py`
- `docs/handoffs/implementer_status_phase_1f_minor_static_gate_follow_up_20260721005412.md`

## 4. Full Mypy Finding修正

旧Testは、Runtime Moduleが内部Importしている`subprocess`へ直接到達し、`runtime_detection_module.subprocess.run`をMonkeypatchしていた。このため、MypyのExplicit Export境界で次の1件が失敗していた。

```text
Module runtime_detection does not explicitly export attribute subprocess
```

修正後は`observe_nvidia_process_gpu_memory`へ型付き`NvidiaSmiCommandRunner`を注入できる境界を追加した。

```text
Production : Default Runnerがsubprocess.runをTimeout付きで実行
Unit Test  : subprocess.CompletedProcess[str]を返すFake Runnerを引数注入
Result     : TestからRuntime Module内部Memberへ到達しない
```

Testは、Runnerへ渡されるCommandがCurrent Process GPU Memory Queryであること、同一PIDの複数Rowだけを合算すること、別PIDを除外することを引き続き確認する。

## 5. Accepted Setting Decision反映

Application ConfigのDefault Generation上限を次へ変更した。

```toml
[generation]
max_new_tokens = 2048
```

Application Config所有値とEffective macOS Configを確認する2つのUnit Testを`2048`へ更新した。

低Levelの`GenerationParameters()`単独生成時に使用するContract Default `512`は変更していない。今回のAccepted Decisionは`config/application.toml`のApplication Defaultを対象としており、明示Override、Environment Override、Request Parameterの優先順位も変更していない。

Thinking表示LabelはReviewどおり変更せず、Phase 1-Gの後続事項として維持した。

## 6. Verification

### Finding Reproduction／Targeted

```text
mypy .                                                        : Pass／70 source files
pytest -q test_deployment_platform + test_config_and_registry : Pass／65 tests
```

### Full Static／Default Gate

```text
ruff format --check src scripts tests       : Pass／70 files
ruff check src scripts tests                : Pass
mypy .                                      : Pass／70 source files
python -m compileall -q src scripts tests   : Pass
bash -n Mac Setup／Lightning Setup／Preflight: Pass
uv lock --check --offline                   : Pass／117 packages
pytest -q                                   : Pass／183 passed、3 deselected
```

`uv lock --check --offline`はSandbox内ではユーザーCacheへのAccess制限により開始できなかったため、同じCommandをSandbox外で再実行し、117 PackageのLock整合を確認した。Lock Fileは変更していない。

## 7. Remaining Gate／Review Request

Repository上のMinor Static Gate残件は解消した。次は設計者役のShort Follow-up Reviewを依頼する。

Review合格後の順序はCurrent Indexどおり次を維持する。

```text
Lightning Read-only Preflight
  → Preflight合格後にSource／Modelを一度に搬入
  → Lightning Python 3.12.11／CUDA Mandatory／CPU Candidate Gate
  → 後継Implementer Status
  → Phase 1-F Final Review
```

本StatusはLightning操作、Upload、Phase 1-F完了宣言、Phase 1-G実装、Backup、Git／GitHub操作を行っていない。
