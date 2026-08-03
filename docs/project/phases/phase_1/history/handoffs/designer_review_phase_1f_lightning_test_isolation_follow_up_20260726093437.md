# Phase 1-F Lightning Test Isolation Follow-up 設計Review

- 文書ID: `designer_review_phase_1f_lightning_test_isolation_follow_up`
- 状態: `accepted_repository_lightning_revalidation_pending`
- 作成日時: `2026-07-26 09:34:37 JST`
- 更新日時: `2026-07-26 09:34:37 JST`
- Snapshot: `20260726093437`
- 作成担当: 設計者役担当Task
- 対象Handoff: [designer_handoff_phase_1f_lightning_test_isolation_follow_up_20260726092413.md](designer_handoff_phase_1f_lightning_test_isolation_follow_up_20260726092413.md)
- External Runtime Review: [designer_review_phase_1f_lightning_external_pure_cpu_runtime_20260726092413.md](designer_review_phase_1f_lightning_external_pure_cpu_runtime_20260726092413.md)
- 正本言語: 日本語
- supersedes: なし

## 1. Conclusion

Phase 1-F Lightning Test Isolation Follow-upのRepository変更をAcceptedとする。

Mac RepositoryでTargeted Test、Full Suite、Ruff、FormatおよびMypyがすべてPassした。Production Code、Config、Setup Script、Acceptance ScriptまたはDependency Lockへの変更は確認しなかった。

Lightning Full Suiteの再実行は未実施であり、Cross-platform Full Suite GreenはPendingのまま保持する。

```text
Repository Test-only Change : ACCEPTED
Mac Targeted Test           : PASS
Mac Full Suite              : PASS
Static Verification         : PASS
Production Change           : NONE
Lightning Revalidation      : PENDING
Native Acceptance Re-run    : NOT REQUIRED
```

## 2. Reviewed Files

変更対象：

```text
tests/unit/inference/test_deployment_platform.py
tests/unit/inference/test_lightning_cpu_native_setup.py
```

Handoff Scope外のProduction Fileに、同時刻以降の変更を確認しなかった。

Test実行により生成・更新された`__pycache__`はLocal Generated Artifactであり、Source変更として扱わない。

## 3. Platform Test Isolation

次のTestへExecution Environmentの明示が追加された。

```text
test_profile_resolution_priority_is_explicit_then_environment_then_default
test_future_platform_alias_and_default_are_registry_only_extensions
```

追加値：

```python
raw_execution_environment="native",
```

確認した内容：

- explicit Profile Resolution
- Environment Profile Resolution
- Platform Default Resolution
- Future Platform Registry-only Extension

OS、ArchitectureおよびExecution EnvironmentがすべてTest Inputとして固定される。実行Hostの`/.dockerenv`、Container MarkerまたはCgroupに依存しない。

## 4. Model Root Test Isolation

`test_model_path_compatibility_requires_registry_layout`へSanitized Subprocess Environmentが追加された。

```python
environment = dict(os.environ)
environment.pop("MARGPA_MODEL_ROOT", None)
environment.pop("MARGPA_PROFILE", None)
```

次の3 Subprocessへ同じEnvironmentを渡す。

- Compatible Model Path
- Invalid Layout
- Model Root／Path Mismatch

ユーザーShellで実Model用`MARGPA_MODEL_ROOT`がExportされていても、Temporary Model Root Contract Testへ漏出しない。

Production SetupのFail Closed Contractは変更されていない。

## 5. Independent Targeted Verification

設計者役がMac Repositoryで独立実行した。

```bash
pytest -q \
  tests/unit/inference/test_deployment_platform.py \
  tests/unit/inference/test_lightning_cpu_native_setup.py
```

結果：

```text
41 passed
```

## 6. Independent Full Suite

```bash
pytest -q
```

結果：

```text
267 passed
3 deselected
0 failed
```

Model Smokeは既定でDeselectされる。

## 7. Static Verification

```text
Ruff Check  : PASS
Ruff Format : PASS／95 files
Mypy        : PASS／95 source files
```

## 8. Code Review Findings

Blocking Findingは確認しなかった。

### Isolation

- Mock対象と実Host Evidenceの混在を解消している。
- Application用Environment VariableをTest Subprocessから局所的に除外している。
- Global Environment Mutationを行わない。
- Test終了後のShell Environmentへ影響しない。

### Scope

- Production ResolverをTest都合で変更していない。
- Setup ScriptのFail Closedを弱化していない。
- Model Root Contractを変更していない。
- Lightning Profileを変更していない。
- Native Acceptance Contractを変更していない。

## 9. Lightning Revalidation

Lightningへ次の2Fileだけを反映する。

```text
tests/unit/inference/test_deployment_platform.py
tests/unit/inference/test_lightning_cpu_native_setup.py
```

Targeted：

```bash
"$MARGPA_ENV_PREFIX/bin/pytest" -q \
  tests/unit/inference/test_deployment_platform.py \
  tests/unit/inference/test_lightning_cpu_native_setup.py
```

期待値：

```text
41 passed
```

Full Suiteは、`MARGPA_MODEL_ROOT`をShellへExportした状態のまま実行する。

```bash
"$MARGPA_ENV_PREFIX/bin/pytest" -q
```

期待値：

```text
266 passed
1 skipped
3 deselected
0 failed
```

Apple Silicon Metal Testの1件Skipは正常である。

手動`env -u MARGPA_MODEL_ROOT`なしでPassすることが今回の受入条件である。

## 10. Native Acceptance

本変更はTest-onlyである。

次を変更していない。

- `src/`
- `config/`
- `scripts/setup/`
- `scripts/models/`
- `pyproject.toml`
- `uv.lock`

前回のLightning Bounded Native Acceptance：

```text
all_required_checks_passed=true
```

は有効であり、再実行を要求しない。

## 11. Current Decision

```text
External Pure CPU Runtime  : ACCEPTED
Repository Test Isolation  : ACCEPTED
Mac Full Suite             : GREEN
Lightning Full Suite       : REVALIDATION PENDING
Lightning Web Acceptance   : PENDING
Top-level Phase 1          : NOT DECLARED
```

## 12. Next Gate

```text
LightningへTest 2File反映
  → Targeted 41件
  → Full Suite
  → Full Suite Green Review
  → Lightning Web Preview Acceptance
```

