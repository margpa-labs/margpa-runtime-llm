# Phase 9-3 Context Compaction／Recovery 改訂Long Run — Claude Partial Exact Return

```yaml
document_id: phase_9_claude_phase_9_3_context_compaction_recovery_revised_long_run_partial_exact_return_20260911185305
document_type: exact_return_handoff
document_state: partial_user_interrupted
phase: phase_9
program: phase_9_3
recorded_at: 2026-09-11 18:53:05 JST
language: ja
from: claude_designer_implementer
to: codex_controller
authority_owner: Nazuna Research
decision_authority: user
in_response_to: phase_9_controller_to_claude_phase_9_3_context_compaction_recovery_revised_long_run_exact_handoff_ja_20260911175040.md
trigger: user_direct_interruption_before_context_window_auto_compaction
maximum_claim: P9_3_CONTEXT_COMPACTION_RECOVERY_CORE_PARTIAL_USER_INTERRUPTED_FOR_CONTROLLER_REVIEW
phase_9_3_closure_authorized: false
phase_9_closure_authorized: false
phase_10_authorized: false
git_write_authorized: false
git_write_performed: false
network_authorized: false
network_performed: false
real_model_performed: false
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

本書は、Quota／Resource制約によるTrue Stopではなく、**ユーザーからの直接の作業中断指示**によるPartial Exact Returnである。ユーザーは「Auto-Compactionが来る前に作ってほしいものがある」と述べ、キリの良い時点での一旦停止と、本Return（Handoff相当）およびRecovery（Index相当）の作成を明示的に指示した。

中断時点は、CL-P9-3-A〜Eが完全に成立し、CL-P9-3-Fが部分的に成立し、CL-P9-3-Gが未着手という、Sabotage-regression 4系統が全て検出・復元・再PASS済みの安全な区切りである。Phase 9-3の完了、Closure、Phase 9 Closure、Phase 10着手のいずれも自己承認しない。

## 1. Maximum Claim

```text
P9_3_CONTEXT_COMPACTION_RECOVERY_CORE_PARTIAL_USER_INTERRUPTED_FOR_CONTROLLER_REVIEW
```

Handoffが許可した上限（`P9_3_CONTEXT_COMPACTION_RECOVERY_CORE_AND_MINIMAL_CONTEXT_ACTIONS_COMPLETE_CANDIDATE_FOR_CODEX_CONTROLLER_REVIEW`）には未到達。Minimal Context Actions UI（CL-P9-3-G）が完全に未着手であるため、Complete Candidateを主張しない。

## 2. Work Unit別Disposition

| Work Unit | Disposition | 内容 |
|---|---|---|
| CL-P9-3-A（Budget/Pressure Core） | **完了** | Measurement Class付きBudget、Effective Remaining Budget計算、6値Pressure State、Auto Default ON、Threshold Config。単体Test 11件PASS |
| CL-P9-3-B（Artifact/Persistence/Integrity） | **完了** | 10種Artifact全実装、Local Filesystem Store（Digest/Restart Read/Corruption検知/CAS）。単体Test 8件PASS |
| CL-P9-3-C（Plan/Candidate/Validation） | **完了** | Deterministic Extractive Builder（Model Call 0）、空Candidate／未知Turn参照／Stale Revision／Token超過の全Validation。単体Test 8件PASS |
| CL-P9-3-D（Atomic Compaction/Rollback/Concurrency） | **完了** | Coordinator Pipeline（Manual/Auto同一経路）、CAS Activation、Rollback、Restart Read、Cancel。統合Test 15件PASS。**Sabotage-regression 4系統、全て検出→Byte一致復元→再PASS済み** |
| CL-P9-3-E（Recovery/Rehydration/Handoff/Generation接続） | **完了** | Recovery Index構築、Selective Rehydration（Not Found/Conflict/Stale Typed Failure）、Context Handoff Artifact、`map_generation_context()`へのOptional Port接続。統合Test 4件PASS。Original Conversation Byte-equivalent Preservationを実証 |
| CL-P9-3-F（Local API/Event/Experiment Adapter/Top-level検証） | **部分完了** | `/api/v8/context-compaction`の8 Endpoint実装・Web層登録・Bootstrap配線完了、HTTP経由統合Test 4件PASS。**未実施**: Phase 9-2 Experiment Adapterとの比較（Original／Compacted Variantを同一Frozen Caseで比較）、Request相関Progress/Terminal/Failure Event |
| CL-P9-3-G（Minimal Context Actions UI） | **未着手** | Frontend側の作業（Type／API Client／2 Icon／Warning Dialog／Accessibility／i18n／Build）は一切行っていない |

## 3. Changed Paths（本Round）

### 新規Source

```text
src/margpa_runtime_llm/modules/context_compaction/__init__.py
src/margpa_runtime_llm/modules/context_compaction/domain/__init__.py
src/margpa_runtime_llm/modules/context_compaction/domain/identity.py
src/margpa_runtime_llm/modules/context_compaction/domain/measurement.py
src/margpa_runtime_llm/modules/context_compaction/domain/budget.py
src/margpa_runtime_llm/modules/context_compaction/domain/artifacts.py
src/margpa_runtime_llm/modules/context_compaction/domain/errors.py
src/margpa_runtime_llm/modules/context_compaction/ports/__init__.py
src/margpa_runtime_llm/modules/context_compaction/ports/context_source.py
src/margpa_runtime_llm/modules/context_compaction/ports/model_context.py
src/margpa_runtime_llm/modules/context_compaction/ports/store.py
src/margpa_runtime_llm/modules/context_compaction/application/__init__.py
src/margpa_runtime_llm/modules/context_compaction/application/id_factory.py
src/margpa_runtime_llm/modules/context_compaction/application/auto_policy.py
src/margpa_runtime_llm/modules/context_compaction/application/budget_service.py
src/margpa_runtime_llm/modules/context_compaction/application/deterministic_builder.py
src/margpa_runtime_llm/modules/context_compaction/application/validation.py
src/margpa_runtime_llm/modules/context_compaction/application/worker.py
src/margpa_runtime_llm/modules/context_compaction/application/coordinator.py
src/margpa_runtime_llm/modules/context_compaction/application/recovery_service.py
src/margpa_runtime_llm/modules/context_compaction/application/handoff_service.py
src/margpa_runtime_llm/modules/context_compaction/application/generation_projection_adapter.py
src/margpa_runtime_llm/adapters/context_compaction/__init__.py
src/margpa_runtime_llm/adapters/context_compaction/local_filesystem_compaction_store.py
src/margpa_runtime_llm/adapters/context_compaction/conversation_source_adapter.py
src/margpa_runtime_llm/adapters/context_compaction/model_context_adapter.py
src/margpa_runtime_llm/web/context_compaction_routes.py
```

### 修正Source（既存File、Additive変更のみ）

```text
src/margpa_runtime_llm/web/contracts.py
  -- WebRuntimeへcontext_compaction_coordinator/worker/auto_policyの3 Field追加、close()へWorker Shutdown追加
src/margpa_runtime_llm/bootstrap/web_application.py
  -- Persistent Conversation有効時だけContext Compaction一式を構築・配線（Import 8件追加、構築ブロック1件、WebRuntime呼び出しへ3引数追加）
src/margpa_runtime_llm/modules/conversation/application/generation_context_mapper.py
  -- ActiveContextProjectionPort Protocol新設、map_generation_context()へOptional Parameter 2件追加（Default Noneで既存全呼び出し元へ非破壊）
src/margpa_runtime_llm/modules/conversation/application/persistent_conversation_service.py
  -- context_projection_port Optional Field追加、bind_context_projection_port()追加（既存persistent_ref等と同型のLate-binding Setter）、_generate_pending_turn()内の1呼び出し箇所を更新
src/margpa_runtime_llm/web/app.py
  -- context_compaction_routes Import・Exception Handler 2件・Router 1件追加
```

### 新規Test

```text
tests/unit/context_compaction/test_budget_and_pressure.py（11 tests）
tests/unit/context_compaction/test_deterministic_builder_and_validation.py（8 tests）
tests/unit/context_compaction/test_local_filesystem_store.py（8 tests）
tests/integration/context_compaction/test_coordinator_pipeline.py（15 tests）
tests/integration/context_compaction/test_generation_projection_integration.py（2 tests）
tests/integration/web/test_context_compaction_routes.py（4 tests）
```

## 4. 実施した検証

| 項目 | 結果 |
|---|---:|
| Context Compaction新規単体・統合Test | **48 passed**（内訳: 上記6 File） |
| 既存Conversation Module Regression（`tests/unit/conversation/` + `tests/integration/conversation/`） | 294 passed（Generation Mapper／Persistent Serviceへの変更後、非退行確認） |
| 既存Web CLI／Experiment Route Regression | 366 passed |
| 既存Web Integration／Unit Full Regression（`tests/integration/web/` + `tests/unit/web/`） | 336 passed |
| **Backend Non-model Full Suite（Repository全体）** | **2746 passed, 43 deselected (model_smoke), 0 failed** |
| Ruff（`src/` + `tests/` + `scripts/`全体） | All checks passed |
| Mypy（Repository全体、`pyproject.toml`準拠） | Changed Path内新規Error **0件**。既存Baseline 43件（`test_stream_guard.py`／`test_point_runtime.py`／`test_conversation_generation_guardrail_stream_integration.py`／`judge_live_integration.py`、いずれもPhase 9-2 R5 Round時点から存在する既知の別Scope事項）は本Round Scope外として維持 |
| Frontend Focused／Full Test／Typecheck／Lint／Build | **未実施**（Frontend Source無変更のため） |
| Real Model Gate | **未実施**（本Round中断のため未到達） |

### Sabotage-regression（CL-P9-3-D.10、4系統必須要求に対し4系統実施）

`cp`によるLocal Backup方式（`git stash`不使用）。全て検出→SHA-512完全一致で復元→再PASSを確認。

| # | 対象 | Sabotage内容 | 検出Test | 結果 |
|---|---|---|---|---|
| 1 | Snapshot Gate | `coordinator.py`の`save_pre_action_snapshot()`呼び出しを`pass`に置換 | `test_snapshot_persisted_before_candidate_build_call_zero_on_builder_unavailable` | Snapshot欠落を検出（Assertion Failure） |
| 2 | CAS Revision検証 | `local_filesystem_compaction_store.py`のRevision比較条件を`False and ...`で無効化 | `test_active_projection_cas_accepts_only_the_expected_revision` | Stale Revisionでの誤Accept検出（Assertion Failure） |
| 3 | Original Preservation | `generation_projection_adapter.py`でPending Turn（原文最終Message）の連結を削除 | `test_a_completed_compaction_genuinely_changes_what_map_generation_context_sends` | Pending Turn欠落によりMessage Role交互性ValidatorがValidationErrorを送出（Pydantic自体による多層検出を確認） |
| 4 | Failure→Completed変換 | `coordinator.py`の`_terminal()`内でTargetを常に`COMPLETED`へ強制 | `test_snapshot_persisted_before_candidate_build_call_zero_on_builder_unavailable` | Domain自体の`CompactionAttempt.transitioned()`が不正遷移（他状態→COMPLETED直接遷移は許可Table外）を`ValueError`で拒否し、Attemptが永続的にRequested状態のままTerminalへ到達せずTimeoutで検出 |

Sabotage #3・#4は、当初想定した「Test内Assertion差分」だけでなく、**Domain自身のPydantic Validator／State Transition Validatorという別層の防御機構が独立して同じ欠陥を検出する**ことも同時に確認できた——これはHard-codeされたTest Oracleへの依存を減らす、より強い形のEvidenceである。

## 5. 実装した設計判断（Codex Reviewでの確認を要する事項）

Handoffおよび改訂Canonical設計は一部のExact数値・データ構造を規定していないため、以下はClaudeの実装判断である。Confirmed Blocker/Majorが見つかった場合、次Roundで修正する。

1. **`branch_id`はMVPで固定値`"main"`**: Conversation Moduleに永続化された複数Branch概念が現状存在しない（`project_generation_history()`は単一`head_turn_id`→`parent_turn_id`連鎖のみ）ため、`ContextBranchId`型自体は将来のMulti-branch対応に備えて用意しつつ、今回は定数値で運用する。
2. **Hard Reserve Boundaryを独立Fieldにせず、Effective Remaining Budget ≤ 0で代用**: 6.1の計算式が指すReserve群を全て差し引いた時点が構造的にHard Reserve境界と一致するため、二重定義による不整合Riskを避けた。
3. **`compute_pressure_state()`にAuto Policyを引数として渡し、`hard_reserve_protected`／`manual_compaction_required`をこの一関数内で分岐**: Handoff SS6.2のPressure State一覧が両方を同一列挙として扱っているため、Auto ON時のHard Reserve到達を`hard_reserve_protected`（Autoによる自動解消を期待）、Auto OFF時を`manual_compaction_required`（Generation一時拒否）として区別した。
4. **Deterministic Extractive BuilderのCurrent Objective/Position**: 意味理解なしに要約すると捏造になるため、最初/最新のUser Turnの逐語内容（長さ制限付き）をそのまま採用し、`exact_next_route`は「意味的推論を行っていない」旨を正直に明記する固定文とした。Decision/Constraint/Authority等の高次Sectionは、Deterministic Builderでは常に空のまま（Optional Structured/LLM Builder、CL-P9-3-C.3は本Round未実装）。
5. **Compaction CoreはPersistent Conversation有効時のみ構築**（独自のOpt-inフラグを持たない）: Compaction対象となるCanonical Conversationが存在しない場合、機能として意味をなさないため。Bootstrap側の`if persistent is not None and ...`ブロックで一括判定。
6. **`PersistentConversationService`への接続はLate-binding Setter（`bind_context_projection_port()`）**: `CompactionCoordinator`の構築に`PersistentConversationService`が持つ`repository`/`bound_scope_id`が必要な一方、`PersistentConversationService`自体はCompactionより先に構築されるという循環を、既存の`persistent_ref`等と同型のPatternで解決した。
7. **CompactionWorkerは`ExperimentRunWorker`より簡略化**: Deterministic Builderは実Model Callを伴わない（Model Call 0）ため、Deadline Timerが実Blocking Callと競合する仕組みは不要と判断し、Future.cancel()ベースの単純なQueue-time Cancelのみとした。将来Optional Structured/LLM Builderを追加する際は、この簡略化を再評価する必要がある。

## 6. Open Findings（未解決点）

- CL-P9-3-F.4（Phase 9-2 Experiment Adapterとの比較）: 未着手。
- CL-P9-3-F.3（Request相関Progress/Terminal/Failure Event）: 未着手（Attempt Pollingで代替的にTerminal状態は取得可能だが、Eventそのものは未実装）。
- CL-P9-3-G（Minimal Context Actions UI）: 完全に未着手。
- Real Model Gate（Resource Preflight含む）: 未実施。
- Internal Review A／B: 正式な実施は次Round。
- Optional Structured/LLM Builder（CL-P9-3-C.3）: 未実装（Deterministic Extractive Builderのみ）。これによりHandoff PressureState進行における次の制約が残る: Structured ContextのDecision/Constraint/Authority等高次Sectionは常に空。

## 7. Exact Remaining Work

```text
1. CL-P9-3-F.4: Phase 9-2 Experiment CoreへのOptional Adapter接続、Original/Compacted比較
2. CL-P9-3-F.3: Request相関Event（必要性を含めCodex判断待ち）
3. CL-P9-3-G全体: Frontend Type／API Client／2 Icon／Warning Dialog／Accessibility／i18n／Test／Build
4. Resource Preflight後のBounded Real Model Gate（最大2 Scenario、Main Only）
5. Internal Review A／B（Integrity/Concurrency/Recovery、Integration/Truth/User Surface）
6. 新規Final Exact Return／Final Recovery／User Manual Checklistの作成
```

## 8. Action Inventory

**Read**: Handoff本文、Mandatory Reading 6件（Canonical設計・Phase Index・Phase 9-2 Dependency Closure・Cross-provider Handoff Rule・Automation Control Profile・Original UI Reservation）、As-built First Rule対象Source 18件。

**Write（新規）**: Source 27File、Test 6File、本Return、本Recovery。

**Edit（既存File、Additive）**: `web/contracts.py`、`bootstrap/web_application.py`、`conversation/application/generation_context_mapper.py`、`conversation/application/persistent_conversation_service.py`、`web/app.py`。

**Bash（確認系）**: SHA-512照合（Mandatory Reading 6件＋Sabotage Backup 3件×前後）、`git status`／`git rev-parse HEAD`（Read-onlyのみ）。

**Bash（Test/Static実行系）**: `uv run pytest`多数（新規Module単体、統合、Web Regression、Conversation Regression、Full Suite）、`uv run ruff check`（複数回）、`uv run mypy`（複数回、Module別および全Repository）。

**Sabotage（一時的Source改変→復元）**: `coordinator.py`（2回、Sabotage #1・#4）、`local_filesystem_compaction_store.py`（1回、Sabotage #2）、`generation_projection_adapter.py`（1回、Sabotage #3）。全て`cp`によるScratchpad Backupからの復元でSHA-512完全一致を確認済み、最終的に無変更。

**Git／Process状態**: Git操作はゼロ回（`rev-parse`のみ、Read-only）。HEAD不変（`abbdafa12a735b1a90c7038f2d8f2347eb912c0d`）。Network、Real Model、Browser、Project Root外Action、User `runtime_data`接触、いずれも実行なし。新規Task／Subagent／Delegation不使用。

## 9. Final Recovery Path

`docs/project/phases/phase_9/history/index/phase_9_3_context_compaction_recovery_revised_long_run_partial_recovery_ja_20260911185305.md`

## 10. Exact Next Action

ユーザーの次の指示（Auto-Compaction前に作成を求められた別の成果物）を優先する。その後、本Returnの「7. Exact Remaining Work」に従いCL-P9-3-F.4以降を差分継続する。Codex Controller Independent Reviewは、User側の次の作業が一段落し、Claude側作業を再開した時点で改めて要請する。本Returnの範囲では、Phase 9-3 Closure、Phase 9 Closure、Phase 10着手、Git操作のいずれも行わない。
