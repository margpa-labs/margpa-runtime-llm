# Phase 6 Post-Manual Delta — Package L Recovery（Official Provenance／Artifact Authority／Factories）

```yaml
document_id: phase_6_post_manual_delta_package_l_recovery_20260828170500
package: P6-RR-L
completed_wu: L-WU-001, L-WU-002 (Authority Gate as code, real fetch NOT RUN), L-WU-003, L-WU-004
status: PACKAGE_COMPLETE
created_at: 2026-08-28 17:05:00 JST
next_exact_work_unit: P6-RR-M-WU-001
task_owned_temp: .venv/.t/phase_6_claude_post_manual_delta_20260828161650/
git_action: NONE
root_outside_action: 0
provider_memory_action: 0
network_action: 0
runtime_data_action: 0
```

## L-WU-001 Official Contract Provenance

Network Authorityは本Cycleで未成立のため、Selene Official Prompt TemplateおよびQwen3Guard Official Category Contractの新規取得は行っていない。既存の`config/judge_templates/selene/manifest.json`（`verified_official_copy: false`）はそのまま維持し、遡及的に`true`へ書き換えない。Qwen3Guardの`verified_official_contract`は、Production Wiring側でも`False`をDefaultとして明示的に配線した（後述）。

`Official Provenance: PARTIAL（Network Authority未成立につき取得なし。既存Fail-closed状態を維持）`

## L-WU-002 Exact Artifact Preflight（Authority Gateとしてコード化、実Touchなし）

Base Exact Handoff §8.1は、Project Root外に解決されるSelene／Qwen3Guard Symlink TargetのRead／Stat／Loadを許可しない。本Packageでは、この境界を**実行時の明示的Authority Gate**として実装した。

- 新規`dedicated_model_authority_granted: bool`パラメータ（Default `False`）を`ProductionRoleAdapterFactory`／`SeleneRoleAdapter`／`Qwen3GuardRoleAdapter`へ追加した。
- `preflight()`は、Authority未成立の場合、`ModelDefinitionResolverPort.resolve()`さえ呼ばず（＝`config/models/*.toml`の静的Read以外、Symlink Target側へは一切到達せず）、即座に`(False, "dedicated_model_authority_unavailable")`を返す。
- Production配線（`web_application.py`）では`dedicated_model_authority_granted=False`を明示的にHard-codeし、コメントでBase Handoff §8.1を参照した。本Cycleでこの値をTrueへ変更する行為は行っていない。
- Authority成立後の経路（`probe_capability`のみ呼ぶ、TOML宣言値だけを読みFile I/O 0）と、実Loadを行う経路（`backend.load()`、Symlink Target実Read）を明確に分離し、後者はAuthority成立時にのみ到達可能であることを、Fixtureで実測確認した（下記Evidence）。

本Session中、`models/judge/`・`models/guard/`配下、または`models/`が指す実Symlink Target（`<MODEL_ROOT>`）に対する`ls`・`find`・`stat`・`Read`・`open`等のToolCallは一切実行していない。

`Real Artifact Preflight: NOT RUN / AUTHORITY UNAVAILABLE`（意図的。Real Model Authority Receiptが本Cycleに存在しないため）

## L-WU-003 Production Factories

新規File：[`adapters/runtime_model_control/dedicated_role_adapters.py`](../../../../../src/margpa_runtime_llm/adapters/runtime_model_control/dedicated_role_adapters.py)

- `SeleneRoleAdapter`：専用`LlamaCppModelAdapter`＋`LlamaCppRuntimeModelBackend`を保持し、`load()`成功後に既存の`SeleneSemanticEvaluator`（Package 0〜Iで完成済み、無変更）を構築する。`semantic_evaluator`プロパティで公開。
- `Qwen3GuardRoleAdapter`：同型。`load()`成功後に既存の`Qwen3GuardGenAdapter`（無変更）を構築し、`guard_adapter`プロパティで公開。
- `MainSharedJudgeRoleAdapter`：Judge Roleへ`main.qwen3-4b-q4-k-m`／`main.deepseek-r1-0528-qwen3-8b-q4-k-m`が明示選択された場合の専用Adapter。Main専用の別Loadを一切行わず、`RuntimeModelController`の現在Snapshotの`selected_model_key`と一致する場合のみ`preflight() -> True`。不一致時は`main_model_mismatch_requires_main_switch`。P6-GOV-018 §7.6（「選択可能だがMode Activation不能という状態を残さない」）に対応する、Disabled＋Exact Reasonの実装である。
- `ProductionRoleAdapterFactory`：`RoleAdapterFactoryPort`実装。`provider_id`によって上記3種、またはDefensive Fallbackとして既存`UnavailableRoleProviderAdapter`へ委譲する。

`role_lifecycle_manager.py`へ`active_adapter(role)`Accessorを追加した（Turn実行時にJudge／Guard Hookが、Active化された具体的Adapter〔`SeleneRoleAdapter.semantic_evaluator`等〕を取得するために必要。Package O配線で使用予定）。

`bootstrap/web_application.py`：`factory=UnavailableRoleAdapterFactory()`を`factory=ProductionRoleAdapterFactory(...)`へ置換した。`runtime_model_control_ref`と同型のMutable-box Idiom（`role_provider_runtime_model_control_ref`）を導入し、Bootstrap順序（`role_provider_lifecycle`は`RuntimeModelController`より前に構築される）を変更せずに、Main Switch Snapshotへの遅延参照を実現した。

## L-WU-004 Focused Verification

```text
Command: ./.venv/bin/ruff check src/margpa_runtime_llm/adapters/runtime_model_control/dedicated_role_adapters.py
         src/margpa_runtime_llm/modules/runtime_model_control/application/role_lifecycle_manager.py
         src/margpa_runtime_llm/bootstrap/web_application.py
         tests/unit/adapters/runtime_model_control/test_dedicated_role_adapters.py
Result : All checks passed! (exit 0)

Command: ./.venv/bin/mypy 同上File群
Result : Success: no issues found (exit 0)

Command: ./.venv/bin/pytest tests/unit/adapters/runtime_model_control/test_dedicated_role_adapters.py
Result : 9 passed

Command: ./.venv/bin/pytest tests/unit/runtime_model_control/test_role_lifecycle_manager.py
         tests/unit/runtime_model_control/test_provider_selection_controller.py
         tests/unit/evaluation/test_selene_adapter.py
         tests/unit/guardrail_governance/test_qwen3guard_adapter.py
Result : 39 passed (既存Regression、変更前と同一Pass数)

Command: ./.venv/bin/pytest tests/ -k "web_application or bootstrap or feature_modes_routes
         or provider_selection_routes or guardrail_governance_routes"
Result : 143 passed, 1529 deselected
```

Backend Full Suiteは本Packageでは未実行（Validation Ladder：Per Subphase = Focused + Adjacent Regression + Static。Full RegressionはPackage Qへ予約）。

## As-built Result

```text
Selene Judge Real Activation      : NOT RUN / AUTHORITY UNAVAILABLE（意図どおり）
Qwen3Guard Real Activation        : NOT RUN / AUTHORITY UNAVAILABLE（意図どおり）
Main-as-Judge (Qwen selected)     : Preflight PASS（Main Snapshotと一致時）— Fixture実測
Main-as-Judge (DeepSeek selected) : Preflight FAIL / main_model_mismatch_requires_main_switch — Fixture実測
Production Factory Dispatch       : Fixture実測、4分岐すべて確認
既存Selene/Qwen3Guard Domain/Adapter: 無変更（再実装なし）
```

現時点でM-3／M-4のUser観測Activation Errorは、Reason文字列が`dedicated_provider_artifact_unavailable`から`dedicated_model_authority_unavailable`へ変わる点を除き、挙動としては継続する（Real Model Authority Receiptが無いため、これは正しい現状であり、隠さない）。P6-CODEX-046（Dedicated Provider Production Factory未接続）自体は本Packageで解消された——「Factoryが存在しない」から「FactoryはあるがAuthority未成立」への、正確な状態遷移である。

## Open Findings（本Packageで未解消、後続Packageへ）

- P6-CODEX-047（Selected Judgeと実行Judge不一致）: `judge_live_integration.py`は本Packageで未変更。Package O配線で対応。
- P6-CODEX-048（Qwen3Guard Guardrail未接続）: `guardrail_governance.py`のCompositionは本Packageで未変更。Package O配線で対応。
- P6-CODEX-049（Main Dropdown未接続）: `provider_selection_routes.py`は本Packageで未変更。Package M配線で対応。
- P6-CODEX-050（Model Status投影不整合）: 未着手。Package M配線で対応。

## Claims Not Made

- Selene／Qwen3Guardの実Load成功、実Inference成功を主張しない。
- Judge／Guardrail実行経路がSelene／Qwen3Guardへ実接続されたと主張しない（それはPackage O）。
- Main Dropdownが実Runtime Switchへ接続されたと主張しない（それはPackage M）。
