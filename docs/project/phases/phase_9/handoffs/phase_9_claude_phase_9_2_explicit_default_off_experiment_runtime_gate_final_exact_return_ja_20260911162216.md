# Phase 9-2 Explicit Default-OFF Experiment Runtime Gate — Claude差分継続 Final Exact Return

```yaml
document_id: phase_9_claude_phase_9_2_explicit_default_off_experiment_runtime_gate_final_exact_return_20260911162216
document_type: exact_return_handoff
document_state: ready
phase: phase_9
program: phase_9_2
recorded_at: 2026-09-11 16:22:16 JST
language: ja
from: claude_designer_implementer
to: codex_controller
authority_owner: Nazuna Research
decision_authority: user
in_response_to: phase_9_controller_to_claude_explicit_default_off_experiment_runtime_gate_partial_continuation_exact_handoff_ja_20260911160659.md
resumes: phase_9_codex_phase_9_2_explicit_default_off_experiment_runtime_gate_partial_exact_return_ja_20260911160254.md
maximum_claim: P9_2_EXPLICIT_DEFAULT_OFF_EXPERIMENT_RUNTIME_GATE_COMPLETE_CANDIDATE_FOR_CODEX_CONTROLLER_REVIEW
phase_9_2_closure_authorized: false
phase_9_3_authorized: false
phase_10_authorized: false
git_write_authorized: false
git_write_performed: false
network_authorized: false
network_performed: false
real_model_performed: false
browser_performed: false
append_only: true
```

【Task Communication Identity】

```text
From:
  Provider: Claude Code
  Identity Type: Session ID
  Task ID Equivalent: local_d7f17853-1ab4-45aa-bacd-b9d6db898b65
  Role: 設計者兼実装者役
To:
  Provider: Codex
  Identity Type: Task ID
  Task ID: 019f739b-8a21-7592-95cc-c83c9c08e5f6
  Role: プロジェクト責任者兼設計統括者役
Message Type: return
```

## 0. 本Returnの位置付け

Codex Controller（Task ID `019f739b-8a21-7592-95cc-c83c9c08e5f6`）から、ユーザー中継のRelayでExact Handoff（`phase_9_controller_to_claude_explicit_default_off_experiment_runtime_gate_partial_continuation_exact_handoff_ja_20260911160659.md`）を受領した。Handoff本文、Partial Exact Return、Partial Recovery、Premature Claim Correction Addendum、Task Identity Operating Ruleの5点をSHA-512照合の上で全文読了し、Current Working TreeをRollbackせず差分継続した。

## 1. Maximum Claim

```text
P9_2_EXPLICIT_DEFAULT_OFF_EXPERIMENT_RUNTIME_GATE_COMPLETE_CANDIDATE_FOR_CODEX_CONTROLLER_REVIEW
```

Handoffが許可した上限Claimと同一。Phase 9-2 Complete、Phase 9 Closure、Phase 9-3開始またはRelease Readyは自己承認していない。

## 2. Work Unit別Disposition

| Work Unit | Disposition | 内容 |
|---|---|---|
| CL-GATE-01 | 完了 | Partial Return／RecoveryのDigest照合、Current Working Treeの8 Path一致確認、`.task_tmp/p9_2_experiment_gate`を保持（削除なし）、他の未コミット変更へ非接触 |
| CL-GATE-02 | 完了 | `web/app.py`の未検証non-local lifespan fail-closed GuardをFocused Test（`test_bound_experiment_runtime_fails_closed_under_a_nonlocal_access_policy`）で検証、PASS。Guard自体は既存8ブロックと同型構造でConfirmed Blocker/Majorなし |
| CL-GATE-03 | 完了 | `experiment_routes.py`の全Mutation／Read Endpoint（`create_plan`／`start_run`／`cancel_run`／`get_run`／`list_runs`／`get_comparison`）がSource上で一律`service is None -> _disabled_error()`（`/runs`のみ`worker is None`も追加判定）を実装していることをSource確認。`/presets`のみ意図的にHTTP 200／`enabled:false`。既存Test（`test_default_off_runtime_rejects_plan_and_run_without_work_or_settings_lease`、`test_presets_degrades_safely_when_unbound`）がこの境界を代表的にPASS済みのため、重複Testは追加せずCoverageをこのReturnへ記録（Handoff本文の明示許容に従う） |
| CL-GATE-04 | 完了 | 既存の`test_explicit_gate_runs_the_top_level_fixture_evidence_and_restart_path`（Plan→Run→Evidence→Comparison→Restart Read）と`test_web_runtime_experiment_graph_is_built_only_after_the_explicit_gate`（Default OFF／Explicit ON双方の`WebRuntime.close()`呼び出しを含む、Constructor Spyつき）で既に成立していたEvidenceを最終Source状態で再確認。`WebRuntime.close()`（`contracts.py:194`）が`experiment_run_worker.shutdown()`をOFF時はSkip、ON時は実行することをSource確認 |
| CL-GATE-05 | 完了 | Sabotage-regression実施（詳細は4節）。Ruff Clean。Mypy新規Error 0（詳細は4節、途中でtest-onlyの型不整合1件を検出・修正）。Backend-onlyReworkのためFrontend Build不要と判定（5節） |
| CL-GATE-06 | 完了 | Review A／B完了（6節）。Confirmed Blocker/Major残件0。本Final Exact Return／Final Recoveryを新規Append-onlyで作成 |

## 3. Changed Paths（本Round累積、Codex分含む）

### Source

1. `src/margpa_runtime_llm/entrypoints/web/main.py`
2. `src/margpa_runtime_llm/bootstrap/web_application.py`
3. `src/margpa_runtime_llm/web/experiment_routes.py`
4. `src/margpa_runtime_llm/web/app.py`
5. `src/margpa_runtime_llm/web/contracts.py`

### Test

6. `tests/unit/web/test_web_cli.py`
7. `tests/integration/web/test_experiment_routes.py`（本Roundで型注釈修正1箇所を追加、7節参照）
8. `tests/integration/test_real_top_level_experiment_production_gate_smoke.py`

Codex Partial Returnが列挙した8 Pathと完全一致（`git status --porcelain`で確認済み）。他の既存未コミット差分（`docs/project/`外を含む）へは一切非接触。`git rev-parse HEAD`は`abbdafa12a735b1a90c7038f2d8f2347eb912c0d`のままGit操作ゼロ回。

## 4. Test／Ruff／Mypy／Sabotage結果

| 項目 | 結果 |
|---|---:|
| Focused Guard Test（`test_bound_experiment_runtime_fails_closed_under_a_nonlocal_access_policy`） | `1 passed, 31 deselected` |
| Relevant Regression 最終Source状態（`test_web_cli.py` + `test_experiment_routes.py`） | `72 passed`（Codex分71 + 本Round新規1 Focused Guard Test） |
| Sabotage対象 | `web/app.py`のExperiment Non-local Fail-closed Guard条件（`if (...) and (...)`を`if False and (...) and (...)`へ一時改変） |
| Sabotage前Digest（SHA-512） | `05edc8a70c2715de8af0e7dcc14ceecec2e48150963485ef6a270cd728cd90289445ebc316c00a0d9cea5476fbcbe9b02c4284c058edf69036db5a008baedffb` |
| Sabotage後Focused Test | `1 failed`（`pytest.fail`到達を確認——期待通りGuardの欠落を検出） |
| 復元後Digest（SHA-512） | `05edc8a70c2715de8af0e7dcc14ceecec2e48150963485ef6a270cd728cd90289445ebc316c00a0d9cea5476fbcbe9b02c4284c058edf69036db5a008baedffb`（Sabotage前とByte一致、`diff`空出力で確認） |
| 復元後Focused Test | `1 passed, 31 deselected` |
| Ruff（Changed 8 Path） | `All checks passed!` |
| Mypy（Repository既存運用`uv run mypy`、`pyproject.toml`の`[tool.mypy]`設定に準拠） | 修正前: Changed Path内で新規Error 1件検出（`tests/integration/web/test_experiment_routes.py`、既存の別Loopと同名変数`expected_requester`の型競合）。局所修正後: Changed 8 Path内新規Error **0件**。Repository全体では43件のError（`test_stream_guard.py`／`test_point_runtime.py`／`test_conversation_generation_guardrail_stream_integration.py`／`judge_live_integration.py`、いずれもChanged Path外の既存Baseline、本Roundで新規発生したものではない） |
| Frontend Build | 未実施（5節で判断理由を明記） |
| Real Model／Browser／Network | 実行なし（禁止事項どおり） |

Sabotage-regressionは`cp`によるLocal Backup方式（Scratchpad配下）を用い、`git stash`は使用していない。

## 5. Frontend Build要否の判断

Changed 8 Pathはすべて`src/margpa_runtime_llm/`（Backend）または`tests/`配下であり、`frontend/`配下および`src/margpa_runtime_llm/web/static/`配下の配信Bundleは本Round・Codex分ともに一切変更していない（`git status`で無変更を確認）。したがって`npm run build`の再実行は本Roundの変更に対して技術的に無意味であり、実施していない。

## 6. Review A／B

### Review A（Default OFF、Authority、Bootstrap、API、Lease、Direct Factory、Access Policy、Shutdown）

- CLI層 `_experiment_runtime_enabled()`（`entrypoints/web/main.py`）: `store_true`で既定OFF、明示ON時はLocal／Non-Authenticated／Loopbackおよび明示Conversation Persistenceを要求し、いずれか欠如でInferenceError（`INVALID_CONFIGURATION`）にFail-closed。
- Bootstrap層 `build_phase1_web_runtime()`（`bootstrap/web_application.py`）: `experiment_service`／`experiment_run_worker`／`production_turn_adapter`／`live_configuration_reader`／`experiment_configuration_lease`の5 Objectが単一の`if experiment_runtime_enabled:`配下でのみ構築され、Default OFFでは全て`None`。
- Direct Factory層 `create_web_app()`のlifespan Guard（`web/app.py`）: CLIを経由しない直接`runtime_factory`呼び出し経路でも、5 Objectのいずれかが非Noneかつ非Local/非Loopback/認証ありのAccess Policyであれば、Request受付前に`runtime.close()`後Fail-closedすることを新規Focused Testで確認。既存8個の同型Guard（Persistent Conversation、Configuration Control等）と構造的に一致しており、Guard自体にConfirmed Blocker/Majorはない。
- Settings Mutation Lease連動（`web/app.py`のMiddleware）: `lease is not None and not lease.try_acquire_mutation()`という条件により、Default OFF（`lease is None`）では構造的に409化し得ないことをSource確認、既存Testで裏付け済み。
- Shutdown: `WebRuntime.close()`（`contracts.py:194`）が`experiment_run_worker is not None`の場合のみShutdownを試行し、失敗時は例外化する設計をSource確認。

Confirmed Blocker/Major: **0件**。

### Review B（Explicit ON Regression、通常Chat/Settings等への非波及、Test Oracleの偽PASS、Disabled Surface、Configuration/CLI整合）

- Explicit ON Regression: `test_web_runtime_experiment_graph_is_built_only_after_the_explicit_gate`（Constructor Spy付き、Default/Enabled双方の`.close()`含む）と`test_explicit_gate_runs_the_top_level_fixture_evidence_and_restart_path`（Plan→Run→Evidence→Comparison→Restart Read）の双方がPASS。
- 通常Chat/Settings等への非波及: 本RoundのChanged 8 PathはConversation／Judge／Guard／Repair／Recording／Data Controlsの各Domainコードへ一切触れていない。`test_web_cli.py`はこれらの既存Gate（Data Controls、Runtime Governance等）を同一Fileで検証しており、72 passed中に非退行を含めて確認済み。Handoff禁止事項に明記された「Full Suiteの無目的な反復」は行っていない。
- Test Oracleの偽PASS耐性: Sabotage-regressionでGuard欠落が実際にTest Failureとして検出されることを実証済み（4節）。
- Disabled Surface: 全Mutation/Read Endpointが`service is None`（`/runs`は`worker is None`も）で一律Disabled化することをSource全数確認（CL-GATE-03参照）。
- Configuration/CLI整合: `--phase-9-experiment-runtime`は既存の`--phase-7-data-controls`等と同じ`store_true`／`Phase N`命名規則に整合。

Confirmed Blocker/Major: **0件**。

## 7. 本Round内で検出・修正したFinding

### Finding（MINOR、CL-GATE-05のMypy実行中に検出）— Test内変数名衝突による型推論エラー

`tests/integration/web/test_experiment_routes.py`の`test_top_level_composition_matrix_persists_relations_routing_modes_and_call_zero`内で、Restart Read検証用に新規追加されたForループが、同一関数内の別のForループ（2303行目・2317行目）と同名の変数`expected_requester`を再利用しており、片方が`str`、もう片方が`str | None`と推論されるためMypyが型不整合を報告した（本番Behaviorには影響しないTest内部の変数命名問題）。

**修正**: 新規ループの変数名を`expected_restart_requester`へ改名し、Tuple Literalへ明示的な型注釈（`tuple[tuple[str, str | None, bool], ...]`）を付与。修正後、Mypy新規Error 0、Ruff Clean、対象Test（`test_top_level_composition_matrix_persists_relations_routing_modes_and_call_zero`）PASSを確認。

Confirmed（Mypy実測で機械的に検出）、Scope内（Changed 8 Pathの1つ）、Major未満（Test内型注釈のみ）と判断し、局所修正で完結させた。

## 8. Acceptance Criteria充足状況

```text
AC-01  PASS（5 Object全None、Source確認+Test）
AC-02  PASS（Conversation Persistence単独では非構築、Source確認+Test）
AC-03  PASS（503 experiment_disabled、Test）
AC-04  PASS（未構築のためActor/Worker/Mutation/Evidence/Lease 0、Source確認+Test）
AC-05  PASS（lease is Noneで409化不能、Source確認+Test）
AC-06  PASS（Local/Loopback/Auth Disabled/Persistence要求、Test）
AC-07  PASS（Direct Factory Fail-closed、Focused Test+Sabotage-regression）
AC-08  PASS（Headless Top-level経路非退行、Test）
AC-09  PASS（OFF/ON双方Shutdown安全、Source確認+Test）
AC-10  PASS（Sabotage検出、復元後Byte一致+PASS）
AC-11  PASS（Ruff Clean、Changed Path内Mypy新規Error 0）
AC-12  PASS（Changed PathがConversation/Judge/Guard/Repair/Recording/Data Controls Domainへ非接触、関連Test 72 passed）
AC-13  PASS（UI入口非表示、本Round非変更で維持）
AC-14  PASS（Review A/B完了、Confirmed Blocker/Major残件0）
AC-15  PASS（本Final Exact Return／Final Recoveryを新規Append-onlyで作成）
```

## 9. Open Findings（未解決点）

- なし。Confirmed Blocker/Major、Minor/Non-blockerともに残件はない。7節のFindingは本Round内で修正完結済み。
- Repository全体のMypy Baseline Error 43件（`test_stream_guard.py`等、Changed Path外）は本Round Scope外として修正対象に含めていない——Handoff「既存Baselineを新規Failureとして修正Scopeへ入れない」に従う判断であり、将来のScopeで別途扱う対象として記録する。

## 10. Action Inventory

**Read**: Handoff本文、Partial Exact Return、Partial Recovery、Premature Claim Correction Addendum、Task Identity Operating Rule該当節（Mandatory Reading全5点）、`web/app.py`（lifespan Guard部）、`experiment_routes.py`（全Endpoint定義）、`bootstrap/web_application.py`（Gate配線）、`entrypoints/web/main.py`（CLI Gate）、`contracts.py`（`WebRuntime.close()`）、`test_experiment_routes.py`該当箇所。

**Bash（確認系）**: SHA-512照合5件、`git status`／`git rev-parse HEAD`（Read-onlyのみ）、`.task_tmp`存在確認、`git diff --stat`。

**Bash（Test/Static実行系）**: `uv run pytest`（Focused Guard、Relevant 2-file Regression、Sabotage前後、型修正後の対象Test再確認、計6回）、`uv run ruff check`（2回）、`uv run mypy`（2回、Repository全体）。

**Edit**: `src/margpa_runtime_llm/web/app.py`（Sabotage実施→Byte一致で復元、最終的に無変更）、`tests/integration/web/test_experiment_routes.py`（型注釈修正1箇所）。

**Write**: 本Final Exact Return、対応するFinal Recovery（新規Append-only Path）。

**Git／Process状態**: Git操作は`rev-parse`（Read-only）のみ。`add`/`commit`/`push`/`stash`/`clean`/`reset`/`checkout`いずれも未実行。HEAD不変（`abbdafa12a735b1a90c7038f2d8f2347eb912c0d`）。Network、Real Model、Browser、Project Root外Action、User `runtime_data`接触、いずれも実行なし。Experiment UI再表示、Phase 9-3/10 Source作業、Phase 9-2 Closure自己承認、いずれも行っていない。新規Task／Subagent／Delegation不使用。

## 11. Final Exact Return／Recovery Path

- 本書: `docs/project/phases/phase_9/handoffs/phase_9_claude_phase_9_2_explicit_default_off_experiment_runtime_gate_final_exact_return_ja_20260911162216.md`
- Final Recovery: `docs/project/phases/phase_9/history/index/phase_9_2_explicit_default_off_experiment_runtime_gate_final_recovery_ja_20260911162216.md`

## 12. Exact Next Action

Codex Controller Independent Reviewを待つ。追加Rework、User Manual、Phase 9-2 Closure、Phase 9-3/10着手、Git操作のいずれも、本Returnの範囲では行わない。
