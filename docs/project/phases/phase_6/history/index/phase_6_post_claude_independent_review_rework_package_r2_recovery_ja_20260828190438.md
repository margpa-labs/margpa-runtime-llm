# Phase 6 Post-Claude Independent Review Rework — Package R2 Recovery（Production Execution Router／Identity）

```yaml
document_id: phase_6_post_claude_independent_review_rework_package_r2_recovery_20260828190438
package: P6-RR-R2
completed_wu: R2-WU-001, R2-WU-002, R2-WU-003, R2-WU-004, R2-WU-005, R2-WU-006, R2-WU-007, R2-WU-008
status: PACKAGE_COMPLETE
created_at: 2026-08-28 19:04:38 JST
predecessor: phase_6_post_claude_independent_review_rework_package_r1_recovery_ja_20260828184813.md
task_owned_temp: .venv/.t/phase_6_post_claude_independent_review_rework_20260828183206/
git_action: 0
network_action: 0
root_outside_action: 0
```

## Process Note（透明性）

本Packageは、実装着手前の独立したPackage Entry Recovery Index作成を省略し、実装完了後に本
統合Recovery Indexを作成した。Mandatory Recovery Index Contract（Userの直近Exact Instruction
第3項）の手順上の逸脱として正直に記録する。実装内容自体はDigest／Test Evidenceで検証済みであり、
Source Mutationの経緯は本File内に完全に記載する。次Package（R3）からはPackage Entry作成を
実装着手前に必ず行う。

## 対象Finding

```text
P6-CODEX-063: Selected Provider実行RouterとExecuted Identityが未接続 -> RESOLVED（本Package）
```

## 設計調査（Mutation前）

`SeleneRoleAdapter`（`semantic_evaluator: SeleneSemanticEvaluator | None`公開）、
`MainSharedJudgeRoleAdapter`（`load/unload`はNo-op、実InferenceはMain自身のServiceを使用）、
`Qwen3GuardRoleAdapter`の実装（`dedicated_role_adapters.py`、Package L成果）を再確認した。
`SeleneSemanticEvaluator.evaluate()`は`SemanticEvaluationRequest -> SemanticEvaluationResponse`
（Criterion単位PASS/DEVIATION/UNKNOWN）を返す、Main-selfの`EvaluationCase`ベース評価とは別の
評価モデルであることを確認した。両者を`_finalize_judge_dispatch()`という共有Tailへ橋渡しする
設計とした（詳細は本File「実装」節）。

`Qwen3GuardDetectorAdapter.detect()`（Package O成果）は、`active_adapter_resolver()`を
`detect()`呼び出しごとに都度解決しており、既にFrozen Active Adapter経路として正しく実装済み
であることを確認した——R2-WU-007は追加実装不要、確認のみで完了。

## 実装

### Changed Files

```text
[変更]
src/margpa_runtime_llm/bootstrap/judge_live_integration.py
  - LiveJudgeResultへexecuted_provider: str | None フィールド追加。
  - build_judge_completion_hook()へactive_judge_adapter_resolver: Callable[[], object | None]
    | None パラメータ追加。
  - _active_judge_adapter()ヘルパー追加（judge_mode/repair_mode/recording_mode/
    built_in_active/frozen_guard_modeと同じFreeze規律でRun開始時に1回解決）。
  - _judge_response_from_semantic_results()追加：SeleneのSemanticEvaluationResponse
    （Criterion単位）を、Main-self Decode Pipelineと同じLlmJudgeResponse形へ橋渡し
    （has_deviation -> NEEDS_REPAIR、has_uncertain -> UNKNOWN、else -> ACCEPT。
    semantic_runtime.resolve_semantic_action()の分類ロジックを踏襲）。
  - _run_judge_and_repair()を次のDispatch Routerへ再構成：
      built_in_active -> 既存_run_built_in_semantic_judge()（無変更）。
      active_adapter is None かつ provider_selection_wired -> Typed Failure
        （judge_role=UNAVAILABLE、failure_reason="judge_provider_unavailable"、
        Model Call 0、executed_provider=None）。P6-CODEX-063の中心Gapを解消。
      active_adapter is None かつ not provider_selection_wired -> 既存Main-self
        Dispatch経路を無変更のまま維持（Provider Selectionの概念自体を持たない
        単純Deployment向けの後方互換）。
      active_adapter.semantic_evaluator が非None -> 新規_run_selene_dispatch()経由で
        Selene明示Dispatch。
      それ以外（.provider_idを持つMain-shared Adapter）-> 既存Main-self Dispatch経路を
        使うが、model_key・executed_providerともactive_adapter.provider_idから取得
        （従来のcontext.model_key固定から変更、Main-shared選択が真にActiveな場合のみ
        到達するよう__Gate__された上での明示Dispatch）。
  - _run_selene_dispatch()新規：SemanticEvaluationRequest構築 -> evaluator.evaluate()
    -> semantic_result_recorderへ直接記録（Built-inと同じくMain-self用
    _record_semantic_result()のTranslationをBypass、Selene ResponseのProvider ID
    フィールドは元から正しいためFallback問題なし）-> _judge_response_from_semantic_results()
    -> 共有Tail _finalize_judge_dispatch()。
  - _finalize_judge_dispatch()新規：既存Main-self Tail（Repair Eligibility判定、
    Repair Executor呼び出し、Presentation Outcome導出、最終LiveJudgeResult構築）を
    無変更のまま抽出し、gated/prompt/executed_provider/criteria_selectedをParam化。
    Main-shared・Selene両Dispatch経路から共有。
  - _record_semantic_result()のFallback修正（P6-CODEX-063/Addendum M-WU-006）：
    provider_id=snapshot.active_provider or snapshot.configured_provider を、
    provider_id=snapshot.active_provider or _UNRESOLVED_EXECUTED_PROVIDER_ID へ変更。
    ConfiguredへのFallbackを完全排除。
  - _run_built_in_semantic_judge()のLiveJudgeResultへexecuted_provider=
    _BUILT_IN_JUDGE_PROVIDER_ID追加。
  - _run_judge()／hook()：active_adapter・provider_selection_wiredを解決・Freeze・
    両Dispatch経路（_run_enforcement内、_run_background内）へ伝播。

src/margpa_runtime_llm/bootstrap/web_application.py
  - build_judge_completion_hook(...)呼び出しへ active_judge_adapter_resolver=
    (lambda: role_provider_lifecycle.active_adapter(role=ModelRole.JUDGE))
    if role_provider_lifecycle is not None else None を追加
    （_qwen3guard_active_adapterと同一パターン）。

src/margpa_runtime_llm/web/feature_modes_routes.py
  - JudgeLastResultResponseへexecuted_provider: str | None = None追加。
  - _last_result_response()でLiveJudgeResult.executed_providerを転記。

frontend/src/types.ts
  - JudgeLastResultへexecuted_provider?: string | null追加。

frontend/src/components/FeatureModesPanel.tsx
  - Judge Last Result表示リストへ「Executed Provider: {lastResult.executed_provider}」
    行を追加（active_providerと同じ表示パターン）。

[新規Test]
tests/unit/bootstrap/test_judge_live_integration_dispatch_router.py（5 tests）
  - test_no_resolver_supplied_preserves_legacy_unconditional_main_self_dispatch
  - test_provider_selection_wired_no_active_adapter_fails_closed_zero_model_calls
  - test_main_shared_active_adapter_is_dispatched_and_tagged_as_executed_provider
  - test_selene_shaped_active_adapter_dispatches_via_semantic_evaluator_never_touches_main_service
  - test_selene_dispatch_unavailable_response_produces_typed_failure
```

## 後方互換性Incident（発見・修正）

初回実装（`active_adapter is None`を無条件Typed Failureとした版）は、既存Test 27件を
Regressionさせた。原因は、Provider Selectionを一切持たない単純Deployment（既存Testの多くが
`build_judge_completion_hook()`を`active_judge_adapter_resolver`なしで直接構築する形）では、
Main-selfが唯一の意味あるDispatch対象であり、そこにも同じGateを適用すると挙動が壊れるためで
あった。`provider_selection_wired`（Resolver自体が渡されたか）と`active_adapter is None`
（Resolverが渡された上でNoneを返したか）を区別することで解決し、Regressionを0へ戻した
（全27件Pass再確認）。Non-critical Process Incidentとして記録する——Sourceの最終状態には
影響なく、後方互換性は完全に保たれている。

## Focused／Full Evidence

```text
Command: ./.venv/bin/mypy src/margpa_runtime_llm/bootstrap/judge_live_integration.py
         src/margpa_runtime_llm/bootstrap/web_application.py
         src/margpa_runtime_llm/web/feature_modes_routes.py
         tests/unit/bootstrap/test_judge_live_integration_dispatch_router.py
Result : Success: no issues found（全File）

Command: ./.venv/bin/ruff check <上記全File> && ruff format --check <同>
Result : All checks passed! / 全File Format準拠

Command: ./.venv/bin/pytest tests/unit/ tests/integration/
Result : 1684 passed, 7 deselected
         （Package R1終了時1679 + 新規Dispatch Router Test 5 = 1684、Regression 0）

Command: cd frontend && npx tsc --noEmit && npx eslint . && NODE_OPTIONS=--no-webstorage
         npx vitest run && npx vite build
Result : Typecheck 0 errors / Lint 0 errors / Test 227 passed（Regression 0）/
         Build 50 modules transformed（Package Qベースラインと一致）
```

## 新規Non-critical Finding（Scope外、記録のみ）

```text
finding_id: P6-RR-R2-FINDING-001
severity: minor（Non-critical、対応せず記録のみ）
title: Main Switch後もJudge/GuardのActive Main-shared Adapterが自動Deactivateされない
evidence: MainSharedJudgeRoleAdapter.preflight()はActivation時点でMain.selected_model_key
          との一致を検証するが、Activation成功後にMain自身が別ModelへSwitchしても、
          ProviderSelectionControllerのJudge/Guard Active値は自動的に追随・失効しない
          （RuntimeModelControllerとRoleProviderLifecycleManagerは独立しており、
          Main Switch Commit Hookからのcross-invalidationが存在しない）。
affected_path: src/margpa_runtime_llm/bootstrap/web_application.py（on_commitフック）、
               modules/runtime_model_control/application/role_lifecycle_manager.py
root_cause_candidate: Cross-component Wiring未実装（Main Switch -> Role Lifecycle通知経路なし）。
required_rework: 将来のPackageまたはPhase 7候補として、on_commit Hookから
                  role_provider_lifecycle.deactivate(role=JUDGE/GUARD)相当を呼ぶ
                  Cross-invalidation経路の追加を推奨。
disposition: deferred（P6-CODEX-062〜068のいずれにも該当しないScope外Finding、
             本Rework Handoffの対象外として次Rework Handoffへ持ち越す）
```

## Acceptance再確認（R8で最終反映）

```text
P6-DELTA-003（Selene選択時、Selene Production FactoryとRouteを使用し、Main-selfへ暗黙
  Fallbackしない）: PARTIAL -> 本PackageによりRoute自体は実装・Fixture検証済み。ただし
  Real Selene Authorityがないため実Selene応答での検証はできない。Dispositionは
  「PARTIAL（Route実装済み、Real Authority Gate）」で維持し、PASSへは昇格しない。

P6-DELTA-009（Configured／Active／Executed／Recorded ProviderがAPI／UI／Evidenceで一致）:
  Executed Providerが独立Fieldとして常時記録・投影されるようになった。PARTIAL -> PASS方向
  だが、Main Switch非連動（上記Finding-001）が残るためPARTIAL維持を推奨。
```

## Open Critical／Major

```text
Open Critical: 0
Open Major: 0（P6-CODEX-062・063はRESOLVED。064〜067は引き続きOpen、R3〜R6で対応）
```

## Action Inventory（累積）

```text
Git Read Action: 1（P6-RR-R-INC-001、既存記録のまま）
Git Mutation      : 0
Network Action     : 0
Provider Memory    : 0
User runtime_data  : 0
Root外Persistent Write: 0 known
```

## Task-owned Temporary／Active Process／Loaded Model

```text
Active Process : 0
Loaded Model   : 0（全てFixture／Fake Adapter、Real Model Loadなし）
```

## Exact Next Action

```text
next_exact_work_unit: P6-RR-R3-WU-001
```
