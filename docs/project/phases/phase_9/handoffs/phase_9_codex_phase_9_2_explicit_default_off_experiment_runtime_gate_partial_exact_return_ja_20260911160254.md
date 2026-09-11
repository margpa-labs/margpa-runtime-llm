# Phase 9-2 Explicit Default-OFF Experiment Runtime Gate Partial Exact Return

## 1. 文書状態

- `document_state`: `partial_user_interrupted`
- `maximum_claim`: `P9_2_EXPLICIT_DEFAULT_OFF_EXPERIMENT_RUNTIME_GATE_PARTIAL_USER_INTERRUPTED_FOR_CONTROLLER_REVIEW`
- `completion_claimed`: `false`
- `phase_9_2_closure_authorized`: `false`
- `phase_9_3_authorized`: `false`
- `controller_independent_review_required`: `true`
- `git_write_performed`: `false`
- 作成日時: 2026-09-11 16:02:54 JST
- 実行Task: 設計者兼実装者役（`01a03b6c-2a68-7881-99bc-c788a600f632`）
- Return先: プロジェクト責任者兼設計統括者役（`019f739b-8a21-7592-95cc-c83c9c08e5f6`）

本書は、ユーザーの途中返送指示に従い、Phase 9-2 bounded reworkのCurrent Working Treeと成立済みEvidenceだけを固定するPartial Exact Returnである。Phase 9-2完了、Closure、Phase 9-3 ReadyまたはRelease Readyを主張しない。

## 2. Current Design Disposition

Headless Experiment Runtime全体を明示的なdefault-OFF gateの背後へ移した。

- CLI opt-in: `--phase-9-experiment-runtime`
- Composition input: `experiment_runtime_enabled: bool = False`
- Gate方式: `store_true`による明示opt-in
- Default: OFF
- Conversation Persistence: Experiment Runtimeのstorage prerequisiteであり、runtime authorityではない
- Gate OFF: Experiment Service、Run Worker、Production Turn Adapter、Live Config Reader、Config Leaseを構築しない
- Gate ON: local loopback accessかつ明示Conversation Persistenceが成立する場合だけ構築する
- Web UI: 引き続きhidden/deferred

番号付きPhase CLI namingを既存flag群と整合させ、gate名から対象範囲がHeadless Phase 9 Experiment Runtimeであることを明示した。

## 3. Before / After

### Before

Conversation Persistenceが有効であれば、Experiment Runtime graphが実質的に構成され得た。Persistence enablementとExperiment execution authorityの境界が分離されていなかった。

### After

Conversation PersistenceだけではExperiment Runtimeを有効化しない。明示flagが存在しない通常起動ではExperiment関連objectを構築せず、Plan／Run mutation endpointはdisabled contractを返す。明示gate ON時だけ、既存のaccepted wiringを利用してruntime graphを構築する。

## 4. Changed Paths

### Source

1. `src/margpa_runtime_llm/entrypoints/web/main.py`
2. `src/margpa_runtime_llm/bootstrap/web_application.py`
3. `src/margpa_runtime_llm/web/experiment_routes.py`
4. `src/margpa_runtime_llm/web/app.py`
5. `src/margpa_runtime_llm/web/contracts.py`

### Test

6. `tests/unit/web/test_web_cli.py`
7. `tests/integration/web/test_experiment_routes.py`
8. `tests/integration/test_real_top_level_experiment_production_gate_smoke.py`

## 5. Implemented Behavior

### 5.1 CLI and composition

- `--phase-9-experiment-runtime`を追加した。
- flag省略時は、Conversation Persistenceの有効／無効にかかわらずExperiment Runtime gateをOFFにする。
- gate ONかつConversation Persistence未成立時は`INVALID_CONFIGURATION`でfail closedする。
- gate ONかつnon-local／authenticated／non-loopback policy時はfail closedする。
- `build_phase1_web_runtime`へ`experiment_runtime_enabled`を明示伝播する。

### 5.2 Runtime object graph

Gate OFFでは次を`None`のまま保持し、構築しない。

- Experiment Service
- Experiment Run Worker
- Production Turn Adapter
- Live Config Reader
- Experiment Configuration Lease

Gate ONでは既存のaccepted composition順序を維持して構築する。

### 5.3 Disabled HTTP contract

- `GET /presets`: HTTP 200、`enabled: false`、空のcases／variants
- Plan／Run mutation endpoint: HTTP 503、code `experiment_disabled`
- message: `The Experiment runtime is not enabled in this deployment.`
- Settings mutationはExperiment leaseを保持しないため、default-OFF runtimeを理由とするHTTP 409にはならない

### 5.4 Defense in depth

直接runtime factoryを利用する経路も対象にするため、`src/margpa_runtime_llm/web/app.py`のlifespanにnon-local policy fail-closed guardを追加した。この最後の変更と対応testは、ユーザーの途中返送指示時点で未検証である。

## 6. Established Validation Evidence

| 対象 | 結果 | 状態 |
|---|---:|---|
| Focused Web CLI | `4 passed, 36 deselected` | PASS |
| Focused Experiment route: default-OFF + enabled top-level | `2 passed, 69 deselected` | PASS |
| `tests/unit/web/test_web_cli.py` + `tests/integration/web/test_experiment_routes.py` | `71 passed` | PASS。ただし、最後の`web/app.py` guard追加前の結果 |
| `tests/integration/test_real_top_level_experiment_production_gate_smoke.py`（default marker exclusion） | `6 passed, 3 deselected` | PASS。3 deselectedはmodel smoke |
| Real Model | 実行なし | PROHIBITED / NOT RUN |
| Real Browser | 実行なし | PROHIBITED / NOT RUN |
| Ruff | 実行なし | NOT RUN |
| Mypy | 実行なし | NOT RUN |
| Broader nonmodel regression | 実行なし | NOT RUN |
| Sabotage regression | 実行なし | NOT RUN |

補足として、同一2-file suiteの先行runは`70 passed`であり、その後enabled top-level test追加後の`71 passed`が新しい成立Evidenceである。

## 7. Required Test Disposition

| ID | 要求 | Disposition | Evidence |
|---|---|---|---|
| P9-2-GATE-TST-001 | Default runtimeがactiveにならない | PASS | CLI／composition test、constructor spy、関連suite `71 passed` |
| P9-2-GATE-TST-002 | API Runがdisabled contractを返す | PASS | default-OFF route test |
| P9-2-GATE-TST-003 | Actor／Worker／mutation／evidence／leaseが起動・生成されない | PASS | composition constructor spyとdefault-OFF route test |
| P9-2-GATE-TST-004 | Settings mutationがlease-held 409にならない | PASS | default-OFF route test |
| P9-2-GATE-TST-005 | Explicit enable時だけruntimeが機能する | PASS | CLI propagationとenabled composition test |
| P9-2-GATE-TST-006 | Top-level enabled pathがPlan→Run→Evidence→Comparison→restart-readを通る | PASS | enabled top-level nonmodel integration test |
| P9-2-GATE-TST-007 | Default／enabled双方のshutdownが安全 | PASS | composition-root test |
| P9-2-GATE-TST-008 | Normal non-Experiment runtimeへの非影響 | PARTIAL | Relevant `71 passed`およびreal-smoke file nonmodel `6 passed`; broader regression未実施 |
| P9-2-GATE-TST-009 | Sabotage検出と復元後PASS | NOT RUN | 未実施 |
| P9-2-GATE-TST-010 | Direct factory non-local policy fail closed | NOT RUN | Sourceとtestは追加済みだが最終編集後の実行なし |

## 8. Incident Accounting

Project-root-local task tempとして`.task_tmp/p9_2_experiment_gate`を使用した。親directory未作成の状態でnested `--basetemp`を指定した1回のtest commandでは、39 tests通過後に31件のfixture setup error（`FileNotFoundError`）が発生した。親directoryを明示作成して同一scopeを再実行し、`70 passed`を確認した。

これはproduct failureではなく、project-local test harness precondition incidentとして保持する。Destructive cleanupは行っていない。

## 9. Self-review State

### Review A: authority／security／default-OFF観点

`PARTIAL`

- CLIだけではdirect runtime factory経路を拘束できないfindingを検出した。
- `web/app.py` lifespanへnon-local fail-closed guardを追加し、対応testを追加した。
- この修正後のvalidationは未実施であり、Review Aは完了していない。

### Review B: enabled-path regression／composition／shutdown観点

`NOT COMPLETE`

- 明示enable、top-level nonmodel path、default／enabled shutdownは成立済みEvidenceあり。
- 最終Source状態に対する再確認、broader regression、static validation、sabotage-regressionが未実施。

## 10. Exact Remaining Work

1. 最後に追加したnon-local lifespan guard testと関連focused testsを実行する。
2. Changed Source／Testに対するRuffを実行する。
3. Changed Source／Testに対するMypyを実行する。
4. Frozen要求に従うbounded sabotageを行い、期待したfailureを確認し、同一Task内で復元してPASSを確認する。
5. Review A／Review Bを異なる観点で完了し、Critical／Major findingだけをscope内修正する。
6. Backend-only変更に対するFrontend build／artifact validationの要否をController contractに照らして確定する。未実施をPASSとしない。
7. Final Recovery、Final Exact Return、Controller Independent Review boundaryを作成する。

## 11. Prohibited / Not Performed

- Git write、Commit、Push
- Network access
- Real Model artifact access
- Real Browser execution
- Project Root外action
- User `runtime_data` access
- Phase 9-3／Phase 10
- Closure／Roadmap mutation
- Destructive cleanup

## 12. Exact Return Disposition

ユーザーの途中返送指示により、ここでCurrent StateをControllerへ返す。本書はCompletion Candidateではない。Controllerは、本Partial ReturnをIndependent Reviewの入力または後続bounded continuationのRecovery inputとして扱い、Phase 9-2完了を別途判定する必要がある。

