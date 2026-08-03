# Phase 1-F Minor Static Gate Follow-up 設計Review

- 文書ID: `designer_review_phase_1f_minor_static_gate_follow_up`
- 状態: `accepted_repository_ready_for_lightning_preflight`
- 作成日時: `2026-07-21 01:02:00 JST`
- 更新日時: `2026-07-21 01:02:00 JST`
- Snapshot: `20260721010200`
- 作成担当: 設計者役担当Task
- 対象: Phase 1-F Minor Static Gate Follow-upとLightning Preflight進行可否
- 正本言語: 日本語
- 実装報告: [implementer_status_phase_1f_minor_static_gate_follow_up_20260721005412.md](implementer_status_phase_1f_minor_static_gate_follow_up_20260721005412.md)
- 前回Review: [designer_review_phase_1f_repository_follow_up_20260721003201.md](designer_review_phase_1f_repository_follow_up_20260721003201.md)
- 要件: [phase_1f_lightning_cross_environment_runtime_requirements_20260719202333.md](../requirements/phase_1f_lightning_cross_environment_runtime_requirements_20260719202333.md)
- ADR: [adr_0015_phase_1f_lightning_and_python_312_support_20260719202333.md](../adr/adr_0015_phase_1f_lightning_and_python_312_support_20260719202333.md)
- 最新Index: [documentation_index_20260721010200.md](../documentation_index_20260721010200.md)
- supersedes: `designer_review_phase_1f_repository_follow_up_20260721003201.md`

## 1. Review結論

前回Reviewで残ったFull Project Mypy Failureは解消した。TestがRuntime Module内部の`subprocess`へ直接到達する構造は廃止され、型付きCommand Runnerを関数境界から注入する構造へ変更されている。

ユーザー決定済みのApplication Default `generation.max_new_tokens = 2048`もConfigと関連Testへ反映された。低Level Contract Default、明示Override、Environment Override、Request Parameterの優先順位は変更されておらず、変更範囲は適切である。

独立検証でも、Full Mypy、Default Test、Ruff、Compile、Shell構文、Lock整合、Mac Metal Model Smokeがすべて合格した。新規Findingはない。

したがって、Phase 1-FのRepository Follow-upをAcceptedとし、Lightning AI StudioのRead-only Preflightへ進むことを許可する。

ただし、Lightning Python 3.12.11、CUDA Mandatory Gate、CPU Candidate Gateはまだ未実行である。Phase 1-F全体の完了宣言ではない。

```text
Previous Static Finding       : Resolved
generation.max_new_tokens     : 2048／Applied
Full Project Mypy             : Pass／70 source files
Default Test                  : Pass／183 passed、3 deselected
Mac Metal Model Smoke         : Pass／2 passed、1 skipped、1 deselected
New Finding                   : 0
Repository Decision           : Accepted
Lightning Preflight           : Authorized／Not Run
Phase 1-F Completion          : Not Accepted Yet
```

## 2. Review対象

```text
config/application.toml
src/margpa_runtime_llm/adapters/model_backends/llama_cpp/runtime_detection.py
tests/unit/inference/test_deployment_platform.py
tests/unit/inference/test_config_and_registry.py
docs/handoffs/implementer_status_phase_1f_minor_static_gate_follow_up_20260721005412.md
```

## 3. Static Finding解消確認

### 3.1 Production境界

`observe_nvidia_process_gpu_memory`は、任意の`NvidiaSmiCommandRunner`を受け取れる。ProductionでRunnerが省略された場合だけ、既定RunnerがTimeout付きで`subprocess.run`を実行する。

```text
Production Call
  → default typed command runner
  → subprocess.run
  → nvidia-smi process memory evidence

Unit Test
  → injected typed fake runner
  → deterministic CompletedProcess
  → PID scope／memory aggregation verification
```

Productionの既定挙動を維持しながら、TestがModule内部Import Detailへ依存しない構造である。依存性注入の範囲もCommand実行境界に限定されている。

### 3.2 Test Evidence

Testは次を維持している。

- Runnerへ渡されるCommandがCurrent Process GPU Memory Queryである。
- 対象PIDの複数Rowを合算する。
- 別PIDのMemoryを除外する。
- `subprocess.CompletedProcess[str]`を使用して型を固定する。

Full Project Mypyの旧Errorは再現せず、70 Source Fileすべて合格した。

## 4. Generation Default確認

Application Configは次へ変更された。

```toml
[generation]
max_new_tokens = 2048
```

Config所有値とEffective macOS Configを確認するTestも2048へ更新された。

低Levelの`GenerationParameters()` Contract Default 512は維持されている。Application Configを経由しない低Level生成の安全なFallbackと、ユーザーが通常利用するApplication Defaultを分離するため、現時点のScopeとして妥当である。

Thinking表示Labelは`高度推論`のままであり、合意どおりPhase 1-GのUI／説明注記とともに後続設計する。

## 5. Independent Verification

```text
.venv/bin/mypy .                            : Pass／70 source files
.venv/bin/pytest -q                         : Pass／183 passed、3 deselected
.venv/bin/ruff check src scripts tests      : Pass
.venv/bin/ruff format --check src scripts tests
                                             : Pass／70 files
.venv/bin/python -m compileall -q src scripts tests
                                             : Pass
bash -n Lightning Setup／Preflight           : Pass
uv lock --check --offline                   : Pass／117 packages
.venv/bin/pytest -q -m model_smoke tests/integration
                                             : Pass／2 passed、1 skipped、1 deselected
```

`uv lock`はSandboxのUser Cache読取制約を避け、Sandbox外で同一Commandを実行した。Lock File変更はない。

Model SmokeはMac Metal実機Contextで実行した。Skip 1件は`MARGPA_PHASE1F_PROFILE`未指定によるLightning専用Integration Testであり、失敗ではない。

## 6. Acceptance Status

| Area | Result | Notes |
|---|---|---|
| Full Project Mypy | Pass | 70 source files |
| Default Runtime Tests | Pass | 183 passed、3 deselected |
| Application Default | Pass | `max_new_tokens = 2048` |
| Mac 3.13／Metal Regression | Pass | Model Smoke合格 |
| Repository Follow-up | Accepted | 新規Findingなし |
| Lightning Read-only Preflight | Ready | 次の外部Gate |
| Lightning Python 3.12.11 | Pending | Target未実行 |
| Lightning CUDA Mandatory Gate | Pending | Target未実行 |
| Lightning CPU Candidate | Pending | Best Effort／Target未実行 |

## 7. Next Gate

大容量Uploadを一度にまとめる方針に従い、最初は小型のRead-only PreflightだけをLightning Targetへ配置して実行する。

```bash
scripts/setup/preflight_lightning_ai_studio.sh --environment-mode auto
```

GPU未割当でCPU Candidateだけを確認する場合：

```bash
scripts/setup/preflight_lightning_ai_studio.sh \
  --environment-mode auto \
  --cpu-only
```

Preflight結果を実装担当Statusとして保存し、必要なEnvironment Modeを確定する。Preflight合格後にSource／Modelをまとめて搬入し、Python 3.12.11、CUDA Mandatory Gate、CPU Candidate Gateを実行する。

Phase 1-G実装、Phase 1完了宣言、Backup、Phase 1-ex、Git、GitHub公開はまだ開始しない。

## 8. Authorization Boundary

本Reviewにより、Phase 1-FのLightning Read-only Preflight実行を許可する。

Source／Config／Tests／Scriptsの追加変更、Full Upload、Dependency Install、Native Build、Model Download、Phase 1-G実装、Backup、Git、GitHub公開は、本Reviewだけでは許可しない。Full Upload以降はPreflight結果を確認してから進める。

## 9. Append-Only

既存文書を変更せず、新TimestampのReviewとして追加した。
