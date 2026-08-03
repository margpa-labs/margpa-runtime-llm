# MARGPA Runtime LLM Documentation Index

- 文書ID: `documentation_index`
- 状態: `current`
- 作成日時: `2026-07-26 09:24:13 JST`
- 更新日時: `2026-07-26 09:24:13 JST`
- Snapshot: `20260726092413`
- 作成担当: 設計者役担当Task
- 正本言語: 日本語
- supersedes: `documentation_index_20260725215627.md`

## 1. Current Position

```text
Phase 1-I Web Presentation／UX Follow-up       : Complete／Accepted
Mac Web Manual Acceptance                      : Passed
Phase 1-F Pure CPU Repository Follow-up        : Complete／Accepted
Phase 1-F Lightning External Pure CPU Runtime  : Accepted
Cross-platform Full Repository Suite           : Test-only Follow-up Pending
Lightning Web Preview Acceptance               : Pending
Top-level Phase 1 Completion                   : Not Declared
Phase 1-ex                                     : Accepted Reservation／Not Started
```

## 2. Snapshot Resolution

本Indexは[documentation_index_20260725215627.md](documentation_index_20260725215627.md)を継承する。

前Snapshot以降、ユーザーがLightning AI Studio Pure CPU Environmentを実際に再構築し、Environment Verification、Static CheckおよびBounded Native Acceptanceを実行した。

事前想定から変更されたEnvironment経路、Model配置、Upload Artifact、File Mode、Native BuildおよびTest IsolationをCurrent Manualへ統合した。

## 3. Current Lightning Manual

[lightning_pure_cpu_actual_environment_reconstruction_manual_20260726092413.md](user_manual/lightning_pure_cpu_actual_environment_reconstruction_manual_20260726092413.md)

主な確定事項：

```text
Project Root     : /teamspace/studios/this_studio/margpa-runtime-llm
Model Root       : /teamspace/studios/this_studio/models
Model Link       : margpa-runtime-llm/models -> ../models
Python           : 3.12.11
uv               : 0.11.29／Project-isolated
Environment Mode : project-venv
Environment      : margpa-runtime-llm/.venv
Backend          : llama-cpp-python 0.3.34／Pure CPU
```

## 4. External Runtime Review

[designer_review_phase_1f_lightning_external_pure_cpu_runtime_20260726092413.md](handoffs/designer_review_phase_1f_lightning_external_pure_cpu_runtime_20260726092413.md)

判定：

```text
Environment Verification   : PASS
External Pure CPU Runtime  : ACCEPTED
Native Acceptance          : PASS
Required Checks            : ALL TRUE
Static Verification        : PASS
Full Suite                 : 264 PASS／2 TEST ISOLATION FAIL
```

## 5. Test-only Follow-up

[designer_handoff_phase_1f_lightning_test_isolation_follow_up_20260726092413.md](handoffs/designer_handoff_phase_1f_lightning_test_isolation_follow_up_20260726092413.md)

実装対象：

```text
tests/unit/inference/test_deployment_platform.py
tests/unit/inference/test_lightning_cpu_native_setup.py
```

目的：

- MockしたNative Platform Testを実Container Markerから分離する。
- Temporary Model Path Testを外部`MARGPA_MODEL_ROOT`から分離する。
- ユーザーによる手動Environment UnsetなしでFull SuiteをGreenにする。

## 6. Corrected Upload Boundary

Runtime必須：

```text
config/
scripts/
src/
pyproject.toml
uv.lock
```

Full Repository Testにも必要：

```text
tests/
.python-version
Shell Script Execute Bit
```

Model、Local `.venv`、Docs、Cacheおよび生成物はProject Upload Bundleから分離する。

## 7. Environment Route Correction

非採用：

```text
auto
  → studio-active
  → Lightning Active Conda Prefix
  → uv Project Environment Compatibility Error
```

Current：

```text
project-venv
  → Lightning Python 3.12.11
  → margpa-runtime-llm/.venv
  → Pure CPU Native Build
```

## 8. Verification Evidence

```text
Ruff Check  : PASS
Ruff Format : PASS／95 files
Mypy        : PASS／95 source files
pytest      : 264 passed／2 failed／1 skipped／3 deselected
Acceptance  : all_required_checks_passed=true
Profile     : external.lightning-linux-x86_64.cpu-native
```

2 FailureはProduction RuntimeではなくTest Isolationである。

## 9. Next Gate

```text
Test-only Follow-up Implementation
  → Mac Full Suite
  → Lightning Full Suite
  → Full Suite Green Review
  → Lightning Web Preview Acceptance
  → Top-level Phase 1 Completion Decision
```

Test-only修正後、Production Artifactを変更しない限りBounded Native Acceptanceを再実行しない。

## 10. Current Public Roadmap

[roadmap_ja.md](public/roadmap_ja.md)

## 11. Authorization Boundary

本SnapshotはTest-only Follow-up Handoffを許可する。

外部Lightning操作、Production Code変更、Git／GitHub、Phase 1完了宣言、Backup、Phase 1-ex開始またはRAG実装を自動許可しない。

## 12. Append-Only

旧Index、旧ManualおよびTimestamp付き文書は変更せず保持する。新Timestampの本Indexを最新とする。

