# Phase 8 Claude P8-E Integration／Lifecycle／Evidence／Persistence — Complete Package Recovery

```yaml
document_type: recovery_index
phase: phase_8
package: P8-E
state: complete
provider: Claude
created_at: 2026-08-30 23:07 JST
```

## 結論

```yaml
p8_e_established: true
mvp_blocker_open: 0
critical_open: 0
major_open: 0
```

P8-D Foundationの上に、(1) Constitution `agent` Capability Viewとの相関記録、(2) Run単位のEvidence Persistence（Restart/Reload/Shutdown Recovery）、(3) それらを検証するEnd-to-End Test群を追加した。実装過程で、承認済みだが未実行のStepがProcess Restartを跨ぐと再度Approval待ちに戻ってしまうReal Bug（In-memory側Table `_approved_steps`がProcess再起動で消える）を実装前に発見し、承認事実自体を`StepRecord.approved`としてPersisted Stateへ格上げすることで根本的に修正した（単なるIndent／表面修正ではなく、Contract自体を変更する修正）。

## Work Unit別Status

| Work Unit | Status | 備考 |
|---|---|---|
| P8-E-WU-001（Constitution `agent` View相関記録） | COMPLETE | `RunSnapshot.constitution_mode`/`constitution_rule_ids`、Run開始時一回のみ記録、以後不変 |
| P8-E-WU-002（Run/Step Evidence Persistence） | COMPLETE | `DevAgentRunStorePort`＋`JsonFileDevAgentRunStore`（1 Run＝1 File） |
| P8-E-WU-003（Restart/Reload/Shutdown Recovery） | COMPLETE | 2つの独立App/Serviceが同一Storeを共有するEnd-to-End Testで実証 |
| P8-E-WU-004（Approval事実のPersisted化：根本Bug修正） | COMPLETE | `StepRecord.approved`（新Field）、`_approved_steps`（In-memory側Table）を完全撤去 |
| P8-E-WU-005（Regression確認） | COMPLETE | Backend 2058 passed（Regression 0）、Frontend 292 passed（無変更） |

## 実装概要

### P8-E-WU-001: Constitution相関

- `modules/dev_agent/contracts.py`：`RunSnapshot`へ`constitution_mode: str | None`／`constitution_rule_ids: tuple[str, ...] | None`を追加。**意図的にOpaque `str`**（`modules.constitution.ConstitutionMode`型そのものは使わない）— `resolve_decisions()`が「Rule IDをOpaqueに扱いGD固有型を持ち込まない」のと同じ規律をDev Agent側にも適用し、`dev_agent`Moduleが`constitution`Moduleの型へHard Dependencyを持たないようにした。
- `web/dev_agent_routes.py`の`_resolve_constitution_correlation()`：`WebRuntime.constitution_provider`が未Bindまたは`load_manifest()`が失敗した場合は`(None, None)`を返す — 「相関不能」を正直に表現し、偽の「Rule 0件」を捏造しない。Bind済みの場合は`resolve_capability_view(manifest, view="agent", mode=constitution_mode)`を呼び、実際のRule IDとModeをRun開始時に一度だけ記録する。
- Run開始後、`model_copy(update=...)`による状態遷移では`constitution_mode`/`constitution_rule_ids`を明示的に上書きしないため自動的に不変（Historical Immutability — Branch DataやCitation Evidenceと同じ規律）。

### P8-E-WU-002: Persistence

- `modules/dev_agent/ports.py`：`DevAgentRunStorePort`（`save()`/`load_all()`のみのMinimal Protocol）。
- `adapters/dev_agent/json_file_run_store.py`：`data_controls.JsonFileDataControlConsentStore`のFile I/O安全性規律（Symlink拒否、Owner-only Mode 0o600/0o700、Atomic Replace）を1 Run＝1 JSON Fileへ拡張。`load_all()`は破損Fileを個別にSkipし（Loggingあり）、1件の破損が他の全Runの復元をBlockしない設計（Fail-closedの意味を「危険を握り潰さない」ではなく「起動全体を人質に取らない」方向へ適切に解釈）。
- `modules/dev_agent/application/run_service.py`：`DevAgentRunService.__init__`が`run_store`から`load_all()`し既存Runを復元、以後の全State遷移が`_persist()`Helper経由でStoreへ即時Save（呼出元へReturnする前に完了 — Shutdown Recoveryの根拠）。

### P8-E-WU-003: Restart/Reload/Two-tab/Shutdown Recovery

- `tests/integration/dev_agent/test_dev_agent_web_app.py::test_restart_recovers_a_run_across_two_independent_apps`：**2つの完全に独立したFastAPI App／DevAgentRunService Instance**が同一の`JsonFileDevAgentRunStore`（同一Directory）を共有し、一方でRun開始＋1 Step実行→もう一方のAppから`GET`でState復元を確認→さらに`advance()`でRunをCompletedまで進められることを実証。これはReal Process Restartを最も厳密に模したTestであり、単一Process内のStub置換より強い保証。
- Two-tab：本Foundationは全State をServer側1つの`DevAgentRunService` Singletonが保持し、per-connection Stateを一切持たないため、同一Process内での複数Tabは構造的に同一Stateを見る（追加Codeは不要 — 上記Restart Testはこれよりさらに厳しい「別Process」条件を満たしている）。
- Shutdown Recovery：`_persist()`が呼出元へReturnする前にStoreへSave完了するため、Shutdown（Graceful／Abrupt問わず）がどのTiming で発生しても、直前に成立したState以降の損失は発生しない（実行中の1回のAdvance呼び出し自体が中断された場合を除く — これはConversation PersistenceのTurn単位Commitと同じ粒度の保証であり、本Codebase全体で一貫した設計）。

### P8-E-WU-004: 根本Bug修正（Approval事実のPersisted化）

- **発見した問題**：当初の実装は承認済みStepを`self._approved_steps: set[(run_id, step_id)]`というIn-memory-only側Tableで管理していた。これはProcess Restartで消えるため、「承認は済んだがまだ実行されていないStep」がRestartを跨ぐと、再びAWAITING_APPROVALへ戻ってしまう — 人間が既に下した承認判断をServiceが忘れて再度尋ねる、という重大な状態不整合だった。
- **修正**：`StepRecord`へ`approved: bool = False`Fieldを追加し、`submit_approval()`のAPPROVED分岐で`state=PENDING`と同時に`approved=True`をPersisted Stateへ書き込むよう変更。`advance()`のApproval Gate判定は`_approved_steps`集合ではなく`next_step.approved`を直接参照するよう書き換え、In-memory側Table自体を完全に削除した。
- **回帰防止Test**：`test_restart_after_approval_does_not_re_request_it`（Unit）で、承認直後・実行前にProcess Restartを模した新規Service Instance生成を行い、再度AWAITING_APPROVALへ戻らず直接実行されることを確認。

## Changed Paths

Backend Source（8）：
```text
src/margpa_runtime_llm/modules/dev_agent/contracts.py（既存Fileへ追記：constitution_mode/rule_ids、approved）
src/margpa_runtime_llm/modules/dev_agent/ports.py（既存Fileへ追記：DevAgentRunStorePort）
src/margpa_runtime_llm/modules/dev_agent/application/run_service.py（既存Fileへ改修：Persistence配線＋Approval永続化）
src/margpa_runtime_llm/modules/dev_agent/__init__.py（既存Fileへ追記）
src/margpa_runtime_llm/adapters/dev_agent/json_file_run_store.py（新規）
src/margpa_runtime_llm/adapters/dev_agent/__init__.py（既存Fileへ追記）
src/margpa_runtime_llm/bootstrap/dev_agent.py（既存Fileへ改修：run_store Param）
src/margpa_runtime_llm/entrypoints/web/main.py（既存Fileへ追記：Store合成）
src/margpa_runtime_llm/web/dev_agent_contracts.py（既存Fileへ追記：Response Field拡張）
src/margpa_runtime_llm/web/dev_agent_routes.py（既存Fileへ追記：Constitution相関解決）
```

Backend Test（3、既存3ファイルへの追記込み）：
```text
tests/unit/dev_agent/test_json_file_run_store.py（新規）
tests/unit/dev_agent/test_run_service.py（既存Fileへ6 Test追記）
tests/integration/dev_agent/test_dev_agent_web_app.py（既存Fileへ3 Test追記）
```

Frontend：**変更0件**（Correlation／PersistenceはBackendのみで完結。既存`DevAgentPanel`はTool一覧表示のみでRun詳細を扱っていないため、UI変更の必要がない）。

## Canonical Verification

```text
Backend: uv run pytest -q  -> 2058 passed, 7 deselected
         （内訳: P8-D完了時点2044 + Run Store Unit 6 + Run Service新規Unit 5 + REST統合新規3 = 2058、Regression 0）
         uv run mypy src tests -> Success: no issues found in 552 source files
         uv run ruff check .   -> All checks passed
         uv run ruff format .  -> 適用済み（Diff無し確認済み）

Frontend: npm test -> 292 passed（33 files）（P8-D完了時点と同数、無変更ゆえRegression確認のみ）
```

## Internal Review（1 Cycle）

1. **Controller Issue解消**：該当なし（新規Controller Issue報告はまだない）。
2. **根本Bug修正の質**：単なる症状Workaround（例：Restart直後に全AWAITING_APPROVAL StepをAuto-denyする等の逃げ）ではなく、承認という事実そのものをPersisted Contractの一部へ格上げする根本修正を行った。これはCP8-04の教訓（「単なるIndent修正だけでPASSにしないでください」）と同じ精神をP8-E自身の実装にも適用したもの。
3. **Historical Immutabilityの一貫性**：`constitution_mode`/`constitution_rule_ids`はRun開始時のみ書き込まれ、以後のどの`model_copy(update=...)`呼び出しからも触れられない（Grep確認：`"constitution_mode"`という文字列が`start_run()`以外のUpdate Dictに一切出現しない）。
4. **Fail-closedとAvailability の両立**：`load_all()`が個別File破損をSkipする設計は、本Codebase全体の「危険な状態を安全側に見せかけない」原則とは別の軸（起動全体の可用性）に対する意図的判断であり、本Documentで明示的に理由を記録した（Silent Dataの喪失というTrade-offを隠さず開示）。
5. **Scope遵守**：Real Network・Real MCP・SQLite Migration・GD/Guardrailの実Enforcement統合は一切実装していない（Constitutionは相関記録のみ、Enforcementそのものは既にOFF固定のまま）。Root外0、Git Mutation 0、Install 0、Provider Memory 0、Real Browser/Model 0。

Critical／Major：0件。Minor：2件（非Blocking、Stable未解決へ記録）：
- **P8-RW-E-IR-001**: `load_all()`が破損Fileを静かにSkipする際、そのRunが「元々存在しなかった」のか「存在したが破損して失われた」のかをAPI Caller側から区別する手段がない（両方とも`GET /runs/{id}`が404 `dev_agent_run_not_found`を返す）。将来的にDiagnostics用の別Endpointが必要になる可能性がある。
- **P8-RW-E-IR-002**: `DevAgentPanel`（Frontend）はRunの起動・進行・承認を行うUIを依然として持たない（P8-D由来のP8-RW-D-IR-001がそのまま継続）。Backend側のPersistence／Correlationは完全にTest済みだが、Userが実際にこれをUI経由で体験する経路はまだ無い。

## P8-ACC-034〜038 Disposition

| ID | Disposition | 根拠 |
|---|---|---|
| P8-ACC-034 | PASS | `RunSnapshot`がConstitution Mode／Rule IDとRelationを持ち、未Bind時は正直に`None`（`test_start_run_correlates_with_the_bound_constitution`／`test_start_run_without_a_bound_constitution_is_honestly_none`） |
| P8-ACC-035 | PASS | `DevAgentRunStorePort`＋`JsonFileDevAgentRunStore`が存在し、1 Run＝1 Fileで実際にSave/Load可能（`test_json_file_run_store.py`6 Test） |
| P8-ACC-036 | PASS | 2つの独立したApp/Service/Storeを跨ぐEnd-to-End Testで実Restartを実証（`test_restart_recovers_a_run_across_two_independent_apps`） |
| P8-ACC-037 | PASS | 承認済み・未実行StepがRestartを跨いでも再承認要求されないことを確認（`test_restart_after_approval_does_not_re_request_it`）— 実装中に発見した根本Bugの修正込み |
| P8-ACC-038 | PASS | Backend 2058 Test（Regression 0）、Frontend 292 Test（無変更）、mypy/ruff全Clean |

**P8-ACC-034〜038 全5件PASS。P8-E成立。**

## Action Inventory

```yaml
network_actions: 0
npm_install_or_download: 0
node_runtime_switch: 0
git_mutation_actions: 0
git_read_only_actions: 0
backup_actions: 0
user_runtime_data_access: 0
real_model_access: 0
real_browser_access: 0
real_mcp_server_access: 0
provider_memory_used: false
project_root_外_access_executed: 0
```

## Exact Next Work Unit

```text
Next: P8-F Review／Verification／User Manual Candidate
  Do Not Repeat: P8-A（WU-001〜006）、P8-B（WU-001〜004）、P8-C（WU-001〜005）、
                 P8-D（WU-001〜008）、P8-E（WU-001〜005）は本Recoveryで完成済み。
```
