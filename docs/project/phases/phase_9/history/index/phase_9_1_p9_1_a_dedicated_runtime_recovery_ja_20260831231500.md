# P9-1-A Dedicated Selene/Qwen3Guard Runtime — Package Recovery

```yaml
document_id: phase_9_1_p9_1_a_dedicated_runtime_recovery_20260831231500
document_type: compact_recovery_index
language: ja
created_at: 2026-08-31 23:15 JST
phase: phase_9
program: phase_9_1
package: P9-1-A
disposition: COMPLETE_EXCEPT_WU_005_AUTHORITY_REQUIRED
```

## 1. Work Unit別Disposition

```text
P9-1-A-WU-001  Preflight Contract共通化                         COMPLETE
P9-1-A-WU-002  Selene Production配線（Candidate Load〜Evidence） COMPLETE (Fixture-verified)
P9-1-A-WU-003  Qwen3Guard Production配線（同上）                 COMPLETE (Fixture-verified)
P9-1-A-WU-004  Lifecycle合成（Atomic Commit／Lease／Unload）     COMPLETE (Fixture-verified)
P9-1-A-WU-005  Real Local Artifact Smoke                        AUTHORITY_REQUIRED / NOT RUN
```

## 2. 実施内容

### WU-001
`dedicated_role_adapters.py`の`SeleneRoleAdapter.preflight()`／`Qwen3GuardRoleAdapter.preflight()`
は文字通り同一の19行（Authority Gate -> Definition解決 -> Backend構築 -> `probe_capability()`）
だった。`_run_dedicated_preflight()`へ共通化し、Role固有差は`load()`の後続構築
（`SeleneSemanticEvaluator` vs `Qwen3GuardGenAdapter`）だけに残した。挙動無変更のRefactorで、
既存9 Testが無改造のまま全PASSすることで確認済み。

### WU-002／WU-003
`test_dedicated_role_adapters.py`（既存）は`authority_granted=True`のケースでも
`ModelDefinitionNotRegistered`で止まり、実Backend／Serviceを一度も構築していなかった
（Authority Gateの安全側動作は証明済みだが、Authority付与後の配線自体は未証明だった）。

新規`test_dedicated_role_adapters_production_wiring.py`で、`LlamaCppModelAdapter`を
`ModelPort`形状のFixture Doubleへmonkeypatchし（`LlamaCppRuntimeModelBackend`自体は
純粋な委譲／計算のみのため無改造）、`authority_granted=True`のもとでPreflight -> Load ->
`SeleneSemanticEvaluator.evaluate()` / `Qwen3GuardGenAdapter.classify()`が実際に機能する
Evidenceを返すことを証明した。Regression Guard: `model_key`を意図的に破損させ、Test 1件が
実際に`SemanticProviderState.UNAVAILABLE`へFailすることを確認してから復元、diff完全一致確認。

Real Artifact（Project Root外）・Network・`llama_cpp`ライブラリのいずれにも一切到達していない。

### WU-004
既存`test_role_lifecycle_manager.py`（Preserved As-built、無改造）は`RoleProviderAdapterPort`
Protocol水準でAtomic Commit／Frozen Lease／OFF-Shutdown Unload／Failure Recoveryを汎用Fakeで
既に厳密にProveしている。本Packageでは同じ`RoleProviderLifecycleManager`へWU-002で証明した
本物の`SeleneRoleAdapter`（Fixture Backend付き）を`ProductionRoleAdapterFactory`経由で接続し、
Mode ON Atomic Commit -> Turn Lease中の実Evaluate -> Mode OFF Unloadが合成として機能することを
1件のTestで証明した。Regression Guard: `SeleneRoleAdapter.unload()`から`semantic_evaluator = None`
のリセットを一時的に削除し、Testが実際にFailすることを確認してから復元。

### WU-005
Real Local Artifact SmokeはProject Root外Artifactへの実Read／Stat／Digest／Loadを要求する。
本Handoffが許可していないため`AUTHORITY REQUIRED／NOT RUN`として分離し、Fixture PASSを
Real Artifact PASSへ格上げしていない。

## 3. Changed Paths

```text
src/margpa_runtime_llm/adapters/runtime_model_control/dedicated_role_adapters.py           (modified)
tests/unit/adapters/runtime_model_control/test_dedicated_role_adapters_production_wiring.py (new)
```

Production Composition Root（`web_application.py`の`dedicated_model_authority_granted=False`）は
無変更。Real Artifact GateもExact Unresolved Gateも未解消のまま保持。

## 4. Test Result

```yaml
focused:
  dedicated_role_adapters_directory: "12 passed"
package_regression:
  scope: >-
    tests/unit/runtime_model_control, tests/unit/adapters/runtime_model_control,
    tests/unit/evaluation, tests/unit/guardrail_governance,
    tests/unit/adapters/guardrail_governance, tests/unit/bootstrap,
    tests/integration/web/test_runtime_composition_web_app.py,
    tests/unit/runtime_composition, tests/unit/runtime_governance
  result: "581 passed"
mypy: clean (touched files)
ruff_check: clean (touched files)
ruff_format: clean (touched files)
```

## 5. Authority／Action Inventory

```yaml
real_artifact_touched: false
network_used: false
real_model_load: false
git_mutation: false
user_runtime_data_touched: false
```

## 6. Exact Next Action

```text
P9-1-B（Semantic 109／Built-in Evaluation）へ進む。
P9-1-B-WU-001から開始し、109 RuleをDefinition／Point／Capability／Criterion Type別に
機械Inventory化し、Expected Applicabilityを固定する。
```
