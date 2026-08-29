# Phase 6 Post-Manual Delta — Package N Recovery（Semantic／Built-in／109 Rule Integration）

```yaml
document_id: phase_6_post_manual_delta_package_n_recovery_20260828174500
package: P6-RR-N
completed_wu: N-WU-001 (Built-in Deterministic Repair), N-WU-002 (Criterion Capability Mapping), N-WU-005 (Controlled Fixture, Regression形式で実施)
deferred_wu: N-WU-003 (Batched Semantic Evaluation — Domain実装済みにつき対象外), N-WU-004 (Legacy Main Governance Projection — Package Oで統合)
status: PACKAGE_COMPLETE
created_at: 2026-08-28 17:45:00 JST
next_exact_work_unit: P6-RR-O-WU-001
task_owned_temp: .venv/.t/phase_6_claude_post_manual_delta_20260828161650/
git_action: NONE
root_outside_action: 0
provider_memory_action: 0
network_action: 0
runtime_data_action: 0
```

## 結論

P6-CODEX-047／056（Built-in DeterministicがLLM Callを行い、`judge_role=main_self`を返し`malformed_output`で失敗する）を解消した。`bootstrap/judge_live_integration.py`（1346行、高度に並行制御されたFile）へ、既存のMode Freeze規律（judge_mode／repair_mode／recording_modeと同一パターン）に従う形で最小Diffの分岐を追加した。

## N-WU-001 Built-in Deterministic Repair

`judge_live_integration.py`へ`_run_built_in_semantic_judge()`を追加し、`built_in_active`（Hook Entry時にFreeze、Try/Except付き）が真の場合、既存のMain Model呼び出し経路（`service.generate(...)`、Prompt構築、Decode）を完全にBypassする。

- Model Call 0を保証（Gate条件ではなく、Code Path自体が到達しない構造で保証——`DeterministicEvaluator`のPhase 4 Model 0保証と同型）。
- `execution_state="completed"`（`"failed"`ではない）、`recommendation="unknown"`、`judge_role=JudgeIndependenceClass.BUILT_IN`（新規追加のEnum値）。
- `resolve_evaluation_disposition()`（無変更）により、ENFORCE下でrecommendation≠ACCEPTのためCandidate非提示、repair_requested=Falseとなり、既存の`_run_judge()`Early-return正規化Logic（無変更）が自動的に`safe_fallback`へ収束する——新規のPresentation分岐追加は不要だった。

## N-WU-002 Criterion Capability Mapping

`SemanticEvaluationMethod`は`CLASSIFICATION`／`CLASSIFICATION_WITH_REFERENCE`／`ABSOLUTE_SCORING`の3種のみで、いずれも本質的に定性的判断を要する（`semantic_criterion_adapter.py`で確認、決定論的Methodは存在しない）。したがってBuilt-inは、選択された全Semantic CriterionへHonestに`SemanticCriterionDisposition.NOT_APPLICABLE`＋`SemanticDeferredReason.UNSUPPORTED_MAPPING`を返す（Silent Dropでも、Fabricated Passでもない）。既存`merge_structural_and_semantic_observations`（無変更）はNOT_APPLICABLEを`DEFERRED_TO_SEMANTIC_EVALUATOR`Outcomeへ正しく投影する。

`_record_semantic_result()`（既存のPrivate Helper）は`JudgeCriterionDisposition`（LLM Decoder専用Vocabulary、PASS／DEVIATION／UNKNOWNのみ）しか受け付けず、`SemanticCriterionDisposition.NOT_APPLICABLE`を渡すとSilent Dropすることを確認した。既存Helperを変更せず（既存呼び出し元への影響を避けるため）、Built-in専用の直接構築Pathを追加した。

## Regression／Focused Evidence

```text
Command: ./.venv/bin/ruff check src/ tests/
Result : All checks passed! (exit 0)

Command: ./.venv/bin/mypy src/
Result : Success: no issues found in 289 source files (exit 0)

Command: ./.venv/bin/pytest tests/unit/bootstrap/test_judge_live_integration.py -v
Result : 35 passed（既存32 + 新規3：Zero Model Call確認、ENFORCE Safe Fallback収束確認、
         Semantic Criterion NOT_APPLICABLE確認）

Command: ./.venv/bin/pytest tests/unit/ tests/integration/
Result : 1663 passed, 7 deselected（Package M時点1660比、新規3件純増、Regression 0）
```

## Deferred Work Units

- **N-WU-003 Batched Semantic Evaluation**：`SemanticRuntimeCoordinator`（`runtime_governance/application/semantic_runtime.py`）は既にBudget内Batch選択、Deferred記録、Provider結果Mergeを完全実装済み（Package K Recovery参照）。追加実装不要と判断。
- **N-WU-004 Legacy Main Governance Projection**：`Selected 109 / Deferred 109`固定表示を実Semantic Resultへ接続する作業は、Main Governanceの表示層（`runtime_governance_routes.py`または同等のFrontend投影）に及ぶため、Package Oの Provider Identity統合作業と合わせて実施する方が一貫性を保てると判断し、Package Oへ統合する。

## Open Findings（Package Oへ引き継ぎ）

- P6-CODEX-047の残り半分（Selene選択時に実際にSeleneが呼ばれること）は、Model Authority Receiptが無いため、Package Lで実装したFactory自体は正しく機能するが、`preflight()`が`dedicated_model_authority_unavailable`で常に失敗し、`role_provider_lifecycle.active_adapter(JUDGE)`がSeleneRoleAdapterを返すことはない。Package Oでは、この経路（Selected Selene Providerへの実際のDispatch）をCodeとして実装するが、Real Execution EvidenceはNOT RUN／AUTHORITY UNAVAILABLEとして正確に分類する。
- Explicit Main Model Judge（Qwen／DeepSeek明示選択）の実行経路配線も未実施（Package O-WU-003）。

## Claims Not Made

- Selene／Qwen3GuardがJudgeとして実際に呼ばれることを主張しない（Authority未成立のため到達不能）。
- Semantic 109件中、Built-in経由で実際にPassした件数を主張しない（全件NOT_APPLICABLE、これは正しい現状）。
