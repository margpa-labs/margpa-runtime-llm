# Phase 9-2 Explicit Default-OFF Experiment Runtime Gate Partial Recovery

## 1. Recovery Identity

- `recovery_state`: `PARTIAL_USER_INTERRUPTED`
- `maximum_claim`: `P9_2_EXPLICIT_DEFAULT_OFF_EXPERIMENT_RUNTIME_GATE_PARTIAL_USER_INTERRUPTED_FOR_CONTROLLER_REVIEW`
- `created_at`: `2026-09-11 16:02:54 JST`
- `executor_task_id`: `01a03b6c-2a68-7881-99bc-c788a600f632`
- `controller_task_id`: `019f739b-8a21-7592-95cc-c83c9c08e5f6`
- `completion_claimed`: `false`
- `git_write_performed`: `false`

## 2. Resume Source of Truth

後続作業はCurrent Working Treeと次のPartial Exact Returnを基点に差分再開する。

- `docs/project/phases/phase_9/handoffs/phase_9_codex_phase_9_2_explicit_default_off_experiment_runtime_gate_partial_exact_return_ja_20260911160254.md`

成立済みEvidenceを理由なく再実行せず、最後に追加した未検証変更と明記されたremaining workから再開する。

## 3. Completed / Established

- 明示CLI gate `--phase-9-experiment-runtime`を追加。
- Composition gate `experiment_runtime_enabled: bool = False`を追加。
- Conversation PersistenceとExperiment Runtime authorityを分離。
- Gate OFFではExperiment Service／Worker／Production Adapter／Live Config Reader／Config Leaseを構築しない。
- Gate ONではlocal loopback + explicit Conversation Persistenceを要求。
- Disabled Plan／Run contractをHTTP 503 `experiment_disabled`として維持。
- Settings mutationがdefault-OFF runtimeのleaseにより409にならないことを確認。
- Enabled top-level nonmodel Plan→Run→Evidence→Comparison→restart-readを確認。
- Default／enabled双方のruntime closeを確認。

成立済みvalidation:

- Focused Web CLI: `4 passed, 36 deselected`
- Focused Experiment route: `2 passed, 69 deselected`
- Relevant two-file suite: `71 passed`
- Real top-level smoke fileのnonmodel portion: `6 passed, 3 deselected`

## 4. Current Partial / Not Run

- `src/margpa_runtime_llm/web/app.py`へ追加したnon-local lifespan fail-closed guard: Source追加済み、未検証。
- 対応する`tests/integration/web/test_experiment_routes.py` test: 追加済み、未実行。
- Review A: PARTIAL。
- Review B: NOT COMPLETE。
- Ruff: NOT RUN。
- Mypy: NOT RUN。
- Broader nonmodel regression: NOT RUN。
- Sabotage regression: NOT RUN。
- Real Model／Real Browser: PROHIBITED / NOT RUN。

## 5. Current Process

- 実行中command: なし。
- ユーザー指示に従い、新規implementation／validation commandを開始せずCurrent Stateを固定した。
- `.task_tmp/p9_2_experiment_gate`はproject-root-local test tempである。Recovery作成時にcleanupしていない。

## 6. Changed Paths

1. `src/margpa_runtime_llm/entrypoints/web/main.py`
2. `src/margpa_runtime_llm/bootstrap/web_application.py`
3. `src/margpa_runtime_llm/web/experiment_routes.py`
4. `src/margpa_runtime_llm/web/app.py`
5. `src/margpa_runtime_llm/web/contracts.py`
6. `tests/unit/web/test_web_cli.py`
7. `tests/integration/web/test_experiment_routes.py`
8. `tests/integration/test_real_top_level_experiment_production_gate_smoke.py`

## 7. Harness Incident

Nested project-local `--basetemp`の親directory未作成により、1回のrunで39 tests通過後に31件のfixture setup errorが発生した。親directory作成後の同scope再実行は`70 passed`。Product failureへ再分類しない。

## 8. Exact Resume Point

1. `web/app.py`のnon-local lifespan guardと新規testをfocused validationする。
2. Relevant testsを最終Source状態で確認する。
3. Ruff／Mypyを実行する。
4. Required bounded sabotage-regressionを実施し、failure→restore→PASSを固定する。
5. Review A／Review Bを完了する。
6. Critical／Major findingだけを修正し、必要範囲を差分再検証する。
7. Final RecoveryとFinal Exact Returnを作成し、Controller Independent Reviewへ返す。

## 9. Resume Guardrails

- Phase 9-2完了を本Recoveryから推定しない。
- 未実施validationをPASSとしない。
- Conversation PersistenceをExperiment authorityへ戻さない。
- Gateをdefault-ONへ変更しない。
- Real Model／Browser／Network／Project Root外／User `runtime_data`へ接触しない。
- Git／Closure／Phase 9-3へ進まない。
- Current Working Treeをrollbackしない。

