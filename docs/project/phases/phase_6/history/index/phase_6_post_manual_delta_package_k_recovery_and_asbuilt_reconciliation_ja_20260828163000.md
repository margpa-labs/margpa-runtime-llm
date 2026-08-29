# Phase 6 Post-Manual Delta — Package K Recovery（Recovery／As-built Reconciliation）

```yaml
document_id: phase_6_post_manual_delta_package_k_recovery_and_asbuilt_reconciliation_20260828163000
package: P6-RR-K
completed_wu: K-WU-001, K-WU-002, K-WU-003
status: PACKAGE_COMPLETE
created_at: 2026-08-28 16:30:00 JST
next_exact_work_unit: P6-RR-L-WU-001
task_owned_temp: .venv/.t/phase_6_claude_post_manual_delta_20260828161650/
git_action: NONE
root_outside_action: 0
provider_memory_action: 0
network_action: 0
runtime_data_action: 0
```

## K-WU-001 Mandatory Reading／Digest

Base Exact Handoff、P6-GOV-018 Addendum、Claude運用メモ2件、Internal Review／Rework Loop Contract、Mandatory Reading 23文書全件を全文読了済み（本Turn以前のReceiptで報告済み）。Base Handoff／Addendum SHA-512は指定値と一致した（先行Receipt参照）。Package 0〜IはCOMPLETEのまま保持し、本Packageで再実装しない。Package JのPASS 27／PARTIAL 10／NOT RUN 1／USER GATE 1／FAIL 1をそのまま継承する。

## K-WU-002 Source-to-Production Map（実測、Git不使用、File本文直接照合）

P6-GOV-018 §5 Source Anchorsを実Source本文と照合した。全件、Addendum記載どおり現存することを確認した（一致）。

### 確認済みGap一覧（実測）

| # | Component | 事実 | 該当File |
|---|---|---|---|
| 1 | Dedicated Factory | `RoleProviderLifecycleManager`のProduction Compositionは`factory=UnavailableRoleAdapterFactory()`固定。Selene/Qwen3Guardの実Adapterを生成する経路が無い。 | `bootstrap/web_application.py:313` |
| 2 | Provider Selection | `select()`はConfigurationのみ変更し、`active_provider`は常にNone（MAIN以外）。Implicit Load/Fallbackは無い（これは正しい設計）。しかし`RoleProviderLifecycleManager.activate()`自体は実装済みでPreflight/Load/Rollbackを正しく行う——**呼び出し側が接続されていない**のが真因。 | `provider_selection_controller.py:200-201`、`role_lifecycle_manager.py` |
| 3 | Live Judge | `judge_live_integration.py`の`_run_judge_and_repair`は常に`service.generate(model_key=context.model_key)`（Main Model）を呼び、`JudgeIndependenceClass.MAIN_SELF`固定。Provider Selection ControllerのJudge Selectionを一切参照しない。 | `bootstrap/judge_live_integration.py:648, 639-731, 731(MAIN_SELF固定箇所複数)` |
| 4 | Execution Identity | `_record_semantic_result`内`provider_id=snapshot.active_provider or snapshot.configured_provider`。Active noneの場合Configured名をSemantic Provider IDへ採用し、Executed Evidenceと誤認させる。 | `judge_live_integration.py:554` |
| 5 | Guard Frozen Mode | `_RunCorrelation.frozen_guard_mode`は`begin_run`呼び出し箇所で常に`None`固定（`frozen_guard_mode=None,`のリテラル）。実Guard Mode Providerが渡されていない。 | `judge_live_integration.py:1109` |
| 6 | Main Switch | `PUT /api/v6/provider-selection/main`はProvider Selection Controllerの`select()`のみを呼ぶことが想定されており、既存`RuntimeModelController.switch_to_model_key()`（実Switch Transaction、Idle-only、CAS、Rollback完備）への接続が無い。 | 要Web Route確認（次WUで実施） |
| 7 | Guardrail Additive | `GuardrailGovernanceComposition`は`build_input_detectors()`/`build_output_detectors()`（Rule/Pattern）のみで構築され、`Qwen3GuardGenAdapter`を一切参照しない。Additive Mergeの実装（`invoke_input`/`invoke_output`内でModel Resultを加算する経路）が存在しない。 | `bootstrap/guardrail_governance.py`（GuardrailGovernanceComposition全体） |
| 8 | Built-in Deterministic | Built-in Judge選択時も`judge_live_integration.py`の経路は変わらずMain Modelを呼ぶため、`built_in.deterministic`がLLM Call 0で完結する経路が存在しない。 | `bootstrap/judge_live_integration.py`（Judge Hook全体） |

### 既に成立している基盤（再実装しない）

- `RoleProviderLifecycleManager`（`role_lifecycle_manager.py`）: Preflight→Load→Commit／Rollback、Active Turn Drain、Pending Unloadは完全実装済み。Production Factoryを差し替えるだけで機能する設計。
- `SeleneSemanticEvaluator`／`SelenePromptAdapter`（`adapters/evaluation/selene.py`）: Official Manifest検証、Fail-closed Prompt構築、Typed Decode、`SemanticEvaluationResponse`生成まで完全実装済み。**Production Judge Hookから呼ばれていないだけ**。
- `Qwen3GuardGenAdapter`（`adapters/guardrail_governance/qwen3guard_adapter.py`）: Official Contract検証、Fail-closed Decode、Timeout/Malformed/Internal Error分類まで完全実装済み。**Guardrail Compositionから呼ばれていないだけ**。
- `SemanticRuntimeCoordinator`／`freeze_semantic_turn`／`merge_structural_and_semantic_observations`（`runtime_governance/application/semantic_runtime.py`）: 109件→Batch選択→Deferred記録→Provider結果Merge→Action解決まで、Domain/Applicationは完全実装済み。**Live Judge Hookが呼ぶ`_record_semantic_result`は`SemanticRuntimeCoordinator.record_response`とは別の簡易記録経路であり、両者の関係を次Package以降で確認・統合する。**
- `RuntimeModelController.switch_to_model_key()`（`runtime_model_control/application/runtime_model_controller.py`）: Idle-only CAS Switch Transaction、Rollback、Max New Tokens再検証まで完全実装済み。**Provider Selection APIから呼ばれていないだけ**。

### 結論

P6-GOV-016／017／018が特定したGapは、**Domain／Adapter層の欠落ではなく、Production Composition（`bootstrap/`層）における配線の欠落**である。したがって本差分Reworkの中心作業は、新規Domain設計ではなく、既存の充分にテストされたComponent同士を正しく結線し、Identity（Configured／Active／Executed）を混同しないようにすることである。P6-RR-DELTA §4.1の不変Contractと整合する。

## Next Exact Work Unit

`P6-RR-L-WU-001`（Official Contract Provenance — Network Authority未成立のためTyped PARTIALとして処理し、L-WU-003 Production Factoriesへ進む）。

## Claims Not Made

- Real Selene／Qwen3Guardの実Load成功を主張しない（Model Authority Receipt未成立）。
- Main Switch Route、Guardrail Additive Mergeの具体的な修正はまだ実施していない（次Packageの作業）。
