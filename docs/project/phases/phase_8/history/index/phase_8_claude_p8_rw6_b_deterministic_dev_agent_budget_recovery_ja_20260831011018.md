# P8-RW6-B — Deterministic Dev Agent Budget — Recovery

```yaml
document_type: recovery_index
phase: phase_8
package: P8-RW6-B
finding: P8-CODEX-006
state: complete
provider: Claude
created_at: 2026-08-31 01:10 JST
```

## 結論

`ToolDescriptor.budget_cost`（Fixture比例、write_note=5／list_files・read_file=1）、`RunSnapshot.budget_limit`／`budget_consumed`、`advance()`内のTool実行直前Check（超過時`budget_exceeded`へ収束・Tool実行0）を実装。Max Step制限とは独立した実Limitであることを、単一の高Cost Stepがmax_steps=10でもBudget超過するTestで実証。

`_budget_violation()`を一時的に無効化しRegression Testが実際に失敗することを確認した上で復元（diff上Fix版と完全一致）。

## Changed Paths

```text
src/margpa_runtime_llm/modules/dev_agent/contracts.py（budget_cost／budget_limit／budget_consumed／budget_exceeded追加）
src/margpa_runtime_llm/modules/dev_agent/application/run_service.py（DEFAULT_RUN_BUDGET_LIMIT、_budget_violation()、Check配線）
src/margpa_runtime_llm/modules/dev_agent/__init__.py
src/margpa_runtime_llm/bootstrap/dev_agent.py（write_note budget_cost=5）
src/margpa_runtime_llm/web/dev_agent_contracts.py（budget_limit Request Field、budget_cost／budget_limit／budget_consumed Response Field）
src/margpa_runtime_llm/web/dev_agent_routes.py
tests/unit/dev_agent/test_run_service.py（新規5件）
tests/integration/dev_agent/test_dev_agent_web_app.py（新規2件）
```

## Focused Verification

```yaml
dev_agent_unit_and_integration: 89 passed
regression_before_fix_reproduction: confirmed_fails_without_the_check
backend_full_suite_after: 2099 passed, 7 deselected
ruff: All checks passed
mypy: Success (344 source files)
```

Acceptance Target `P8-ACC-036`: PASS（Max Stepとは独立した実Deterministic Budget Limit／Usage／Exceeded Dispositionを実装・Test・Persistence確認）。Frontend UI変更は本Packageの必須要件ではないため未追加（REST Field露出のみ、最小実装）。
