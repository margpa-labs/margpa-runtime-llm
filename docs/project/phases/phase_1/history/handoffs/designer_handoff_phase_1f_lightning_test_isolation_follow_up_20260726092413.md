# Phase 1-F Lightning Test Isolation Follow-up 実装担当Handoff

- 文書ID: `designer_handoff_phase_1f_lightning_test_isolation_follow_up`
- 状態: `accepted_handoff_implementation_pending`
- 作成日時: `2026-07-26 09:24:13 JST`
- 更新日時: `2026-07-26 09:24:13 JST`
- Snapshot: `20260726092413`
- 作成担当: 設計者役担当Task
- 対象担当: 実装者役担当Task
- Source Review: [designer_review_phase_1f_lightning_external_pure_cpu_runtime_20260726092413.md](designer_review_phase_1f_lightning_external_pure_cpu_runtime_20260726092413.md)
- Current Manual: [lightning_pure_cpu_actual_environment_reconstruction_manual_20260726092413.md](../user_manual/lightning_pure_cpu_actual_environment_reconstruction_manual_20260726092413.md)
- 正本言語: 日本語
- supersedes: なし

## 1. Objective

Lightning Container上でもRepository Unit TestがHost Markerまたは外部Application Environment Variableに依存せず、決定論的に実行できるようTest Isolationを修正する。

Production Code、Profile、Setup Script、Acceptance ScriptおよびRuntime Contractは変更しない。

## 2. Current Evidence

Lightning Pure CPU：

```text
Environment Verification      : PASS
Native Acceptance             : PASS
all_required_checks_passed    : true
Ruff                          : PASS
Mypy                          : PASS
Repository Test               : 264 passed／2 failed
```

残る2件：

```text
tests/unit/inference/test_deployment_platform.py::
  test_profile_resolution_priority_is_explicit_then_environment_then_default

tests/unit/inference/test_deployment_platform.py::
  test_future_platform_alias_and_default_are_registry_only_extensions
```

## 3. Required Change A

対象：

```text
tests/unit/inference/test_deployment_platform.py
```

`native`を検証する`resolve_profile_path()`呼び出しへ、Execution Environmentを明示する。

```python
raw_execution_environment="native",
```

最低対象：

### `test_profile_resolution_priority_is_explicit_then_environment_then_default`

次の3呼び出し：

- explicit
- environment
- platform_default

### `test_future_platform_alias_and_default_are_registry_only_extensions`

次の1呼び出し：

- future platform resolution

OS／Architectureと同様にExecution EnvironmentもTest Fixture Inputとして固定し、実行Hostの`/.dockerenv`またはContainer Markerを参照させない。

## 4. Required Change B

対象：

```text
tests/unit/inference/test_lightning_cpu_native_setup.py
```

`test_model_path_compatibility_requires_registry_layout`が、実行Shellの`MARGPA_MODEL_ROOT`を継承しないようにする。

Test内でSubprocess EnvironmentをCopyし、少なくとも次を除外する。

```text
MARGPA_MODEL_ROOT
MARGPA_PROFILE
```

概念形：

```python
environment = dict(os.environ)
environment.pop("MARGPA_MODEL_ROOT", None)
environment.pop("MARGPA_PROFILE", None)
```

対象Test内のSetup Script Subprocessへ同じ`env=environment`を渡す。

ユーザーがShell側で`env -u`しなくてもTestが決定論的にPassすること。

## 5. Scope

変更可：

```text
tests/unit/inference/test_deployment_platform.py
tests/unit/inference/test_lightning_cpu_native_setup.py
```

変更禁止：

```text
src/
config/
scripts/setup/
scripts/models/
pyproject.toml
uv.lock
```

実装中にProduction変更が必要と判断した場合、実施せず設計者役へ戻す。

## 6. Acceptance Criteria

### Mac

```text
Full pytest Suite : PASS
Ruff Check        : PASS
Ruff Format       : PASS
Mypy              : PASS
```

### Lightning Linux x86_64 Container

外部Environment Variableを手動Unsetしなくても：

```bash
"$MARGPA_ENV_PREFIX/bin/pytest" -q
```

が次相当で完了する。

```text
266 passed
1 skipped
3 deselected
0 failed
```

Apple Silicon Metal Testの1件Skipは正常とする。

## 7. Required Tests

- Mac Full Suite
- Targeted Deployment Platform Unit Test
- Targeted Lightning CPU Native Setup Unit Test
- Ruff Check
- Ruff Format Check
- Mypy
- Shell SyntaxはProduction Script未変更確認として任意

Targeted例：

```bash
pytest -q tests/unit/inference/test_deployment_platform.py
pytest -q tests/unit/inference/test_lightning_cpu_native_setup.py
```

## 8. Native Acceptance

本Follow-upはTest-onlyである。

Production Runtime、Profile、Backend、Model Root Resolution、SetupまたはNative Acceptance Scriptが変更されない限り、Lightning Bounded Native Acceptanceを再実行しない。

## 9. Reporting

Phase 1-ex完了までDocs単一Writerは設計者役である。

実装担当はDocsへ直接書き込まず、次を会話Payloadとして返す。

- 変更File
- 変更概要
- Targeted Test
- Full Suite
- Ruff
- Mypy
- Production File変更なしの確認
- Known Limitation

設計者役がStatus、Review、Indexを作成する。

## 10. Authorization Boundary

本Handoffは上記2 Test FileのTest Isolation修正だけを許可する。

次を許可しない。

- Lightning外部操作
- Model再実行
- Production Code変更
- Config変更
- Git／GitHub操作
- Phase 1完了宣言
- Backup
- Phase 1-ex開始

