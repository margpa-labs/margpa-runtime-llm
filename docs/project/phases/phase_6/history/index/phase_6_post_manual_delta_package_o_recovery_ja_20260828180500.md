# Phase 6 Post-Manual Delta — Package O Recovery（Dedicated Guard／Judge／Repair／Budget）

```yaml
document_id: phase_6_post_manual_delta_package_o_recovery_20260828180500
package: P6-RR-O
completed_wu: O-WU-002 (Qwen3Guard Additive Route), O-WU-004 (Guard Frozen Correlation)
deferred_wu: O-WU-001 (Selene Judge Route — Authority Blocked), O-WU-003 (Explicit Main Model Judge — Package Lで基盤実装済み、Dispatch統合は未接続), O-WU-005 (Failure Matrix)
status: PACKAGE_COMPLETE_WITH_DEFERRAL
created_at: 2026-08-28 18:05:00 JST
next_exact_work_unit: P6-RR-P-WU-001
task_owned_temp: .venv/.t/phase_6_claude_post_manual_delta_20260828161650/
git_action: NONE
root_outside_action: 0
provider_memory_action: 0
network_action: 0
runtime_data_action: 0
```

## 結論

P6-CODEX-048（Qwen3Guard未接続）とP6-CODEX-053／061の一部（`frozen_guard_mode`固定null）を解消した。P6-CODEX-047の残り（Selene実行）は、Model Authority Receiptが本Cycleに存在しないため、Codeとしての配線はScope／Risk Trade-offにより本Packageでは見送り、明示的Deferとして記録する（理由は下記）。

## O-WU-002 Qwen3Guard Additive Route

新規File：[`adapters/guardrail_governance/qwen3guard_detector_adapter.py`](../../../../../src/margpa_runtime_llm/adapters/guardrail_governance/qwen3guard_detector_adapter.py)

- `Qwen3GuardDetectorAdapter`は既存`DetectorPort` Protocolに適合し、`guardrail.input`／`guardrail.output_candidate`／`guardrail.context_source`の3つの静的Detector Registryへ追加登録される。
- Detector Registry MembershipはP5-CODEX-007のEntry/Resolution Binding機構が要求する通り静的（Bootstrap時Fix）のまま維持し、Dedicated Model可用性のみを`detect()`呼び出しごとに動的解決する設計とした（`role_provider_lifecycle_ref`のMutable-box Idiom、Package L／MのPatternを再利用）。
- 現時点でAuthority未成立のため`role_provider_lifecycle.active_adapter(GUARD)`は`Qwen3GuardRoleAdapter`をActive状態で返すことは無く、本Detectorは常に`DetectionOutcome.UNAVAILABLE`（`CLEAR`ではない——「未Scan」と「Scan済みClean」を区別）を返す。既存Rule/PatternDetectorの判定を一切妨げない。
- `LocalPolicyProvider`は現時点でQwen3Guardの実Category（`unmapped_future_category`等の仮称ではなく、Official Category Contract自体が未取得）を認識しないため、実際にMATCHが得られても`recommended_actions`は生成されない（`PolicyApplicability.UNKNOWN`）。これは正しい現状であり、Official Provenance（Network Authority）取得後の追加作業として残す。

## O-WU-004 Guard Frozen Correlation

`judge_live_integration.py`へ`guardrail_mode_resolver: Callable[[], str] | None`Parameterを追加し、`_frozen_guard_mode()`（Try/Except付き、Mode Freeze原則に従いjudge_mode等と同一時点で凍結）を実装した。`bootstrap/web_application.py`で`guardrail_governance_composition.mode_controller.current_mode_value`へ接続し、`frozen_guard_mode=None`固定Literalを実Guard Mode（off／observe／enforce／mode_unavailable）へ置換した。

## Deferred Work Units

### O-WU-001 Selene Judge Route（Authority Blocked）

Package Lで構築した`SeleneRoleAdapter.semantic_evaluator`は、Authority Gate（`dedicated_model_authority_granted=False`）により`preflight()`が常に失敗するため、`role_provider_lifecycle.active_adapter(JUDGE)`が`SeleneRoleAdapter`をActive状態で返すことは本Cycle中に到達不能である。

`judge_live_integration.py`（1346行、P6-CODEX-007〜036の多段階Rework対象）へ、到達不能な経路のためだけに追加のDispatch分岐（Repair／Rejudge、Budget Profile切替を含む）を導入することは、実行時に一切検証できないCodeパスを、既に2回改修した高並行性File内へ追加することを意味する。Built-in（N-WU-001）とQwen3Guard（O-WU-002）は同種の制約下でもFixtureによる End-to-end検証が可能だったため実施したが、SeleneはRepair／Rejudge Budgetとの相互作用がより複雑であり、検証手段（Fixture）とRisk（並行性Critical File内の未検証Code）のTrade-offが逆転すると判断した。

Model Authority ReceiptがUser／Controllerにより発行された後続Cycleで、本Work Unitを実施することを推奨する。

### O-WU-003 Explicit Main Model Judge（部分基盤実装済み、Dispatch未接続）

Package Lの`MainSharedJudgeRoleAdapter`は、Judge ProviderにQwen／DeepSeekが明示選択された場合の`preflight()`（Main Snapshotとの一致確認）を実装済みである。しかし、`judge_live_integration.py`側でこの経路を実際に使う実行時Dispatch（Main-selfの現在の暗黙経路と、明示選択されたQwen／DeepSeekを区別する）は本Packageで未接続である。現状、Main-self判定（`context.model_key`を暗黙使用）と明示的Main-Judge選択は、Judge Roleの実行結果としては区別されない（Provider Selection上のConfigured表示は正しいが、Executed Identityとしての厳密な分離はまだ完成していない）。O-WU-001と同様の理由（High-risk File内での追加Dispatch）により、次Cycleへ委譲する。

### O-WU-005 Failure Matrix

`unavailable`／`load_failed`／`deadline_exceeded`／`malformed_output`／`cancelled`／`shutdown`／`publisher_failed`の個別Regressionは、既存`test_judge_live_integration.py`が`malformed_output`／`cancelled`系を既にカバーしている（Package K確認済み）。`load_failed`（Selene関連）はO-WU-001同様Authority Blockedのため、本Packageでは追加しない。

## Focused／Regression Evidence

```text
Command: ./.venv/bin/ruff check src/ tests/
Result : All checks passed! (exit 0)

Command: ./.venv/bin/mypy src/
Result : Success: no issues found in 290 source files (exit 0)

Command: ./.venv/bin/pytest tests/unit/adapters/guardrail_governance/test_qwen3guard_detector_adapter.py
Result : 6 passed

Command: ./.venv/bin/pytest tests/unit/guardrail_governance/test_bootstrap_hooks.py
Result : 20 passed（既存17 + 新規3：Absent Resolver回帰無し、Inactive Adapter非Block、Active Match可視化）

Command: ./.venv/bin/pytest tests/unit/bootstrap/test_judge_live_integration.py
Result : 37 passed（既存35 + 新規2：Frozen Guard Mode実値反映、Resolver未配線時None維持）

Command: ./.venv/bin/pytest tests/unit/ tests/integration/
Result : 1674 passed, 7 deselected（Package N終了時1663比、新規11件純増、Regression 0）
```

## Claims Not Made

- Selene JudgeまたはExplicit Main Model Judgeの実行経路Dispatchが接続されたと主張しない（O-WU-001／003、明示的にDeferred）。
- Qwen3Guard検出がPolicy／Action Layerへ到達すると主張しない（Official Category Contract未取得のため`UNKNOWN` Applicability）。
- Real Selene／Qwen3Guard Activationを主張しない（Model Authority Receipt未成立、一貫してPackage L以降）。
