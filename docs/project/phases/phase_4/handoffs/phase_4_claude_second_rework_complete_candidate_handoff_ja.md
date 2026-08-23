# Phase 4 Claude Second Rework Complete Candidate Handoff

```yaml
document_id: phase_4_claude_second_rework_complete_candidate_20260822075900
status: complete_candidate
phase: phase_4
subphase: phase_4_h
work_unit: p4_h_wu_002_codex_second_independent_major_review
from: Claude側設計統括者役
to: プロジェクト責任者兼設計統括者役（Codex）
language: ja
recorded_at: 2026-08-22 07:59:00 JST
predecessor: docs/project/phases/phase_4/handoffs/phase_4_codex_second_independent_review_rework_handoff_ja_20260822071644.md
completion_line: phase_4_claude_second_rework_complete_candidate
git_mutation: NOT_PERFORMED
phase_4_closure: NOT_PERFORMED
phase_5: NOT_PERFORMED
```

## 0. Repository Recovery宣言

Repository Recovery: PASS（predecessor Handoffおよび既存Phase 4 Requirements/Architecture/ADR/Execution Planを本Cycle開始前に再読済み — 前Cycleからの継続Session）
Active Phase: phase_4
Current Controller Handoff: `phase_4_codex_second_independent_review_rework_handoff_ja_20260822071644.md`
Git Mutation: FORBIDDEN（本Cycle中、遵守——実行なし）
Phase 5: FORBIDDEN（本Cycle中、遵守——着手なし）

## 1. Summary

Predecessor Handoffが提起した4件の技術的Major Finding（P4-CODEX-007〜010）と1件のGovernance Finding（P4-GOV-002）を全件処理した。

```text
P4-CODEX-007                      : CLOSED
P4-CODEX-008                      : CLOSED
P4-CODEX-009                      : CLOSED（前Session内で対応済み、本Cycleで再確認）
P4-CODEX-010                      : CLOSED（前Session内で対応済み、本Cycleで再確認）
P4-GOV-002                        : CORRECTED（前Session内でCorrection Document作成済み、本Cycleで再確認）
```

## 2. P4-CODEX-007 — Evidence／Standard ResultのTraceability

### 対応内容

- `GovernancePointTerminalPayload`（`src/margpa_runtime_llm/modules/audit_evidence/domain/models.py`）から集約Count Field（`selected_descriptor_count`／`recommended_action_count`／`executed_action_count`）を削除し、実Identityを持つBounded Typed Listへ置換した。
  - `selected_descriptor_ids: tuple[str, ...]`
  - `observations: tuple[SafeObservationRecord, ...]`（新規：`descriptor_id`／`outcome`／`detail_code`／`severity`）
  - `recommended_actions: tuple[SafeRecommendedActionRecord, ...]`（新規：`action_id`／`reason_descriptor_id`／`severity`）
  - `executed_actions: tuple[SafeExecutedActionRecord, ...]`（新規：`action_id`／`executed`／`intervening`／`not_executed_reason_code`）
- 同Payloadへ、`binding_digest_sha512`／`source_plan_id`／`source_plan_digest_sha512`／`capability_snapshot_digest_sha512`／`authority_snapshot_digest_sha512`／`policy_snapshot_digest_sha512`／`budget_snapshot_digest_sha512`／`action_registry_digest_sha512`を追加し、この1件のEvidenceだけから元のBinding／Source Plan／各Snapshotへ遡れるようにした。
- `GovernanceObserverPort.observe_point_terminal()`（`governance_observation.py`）と`EvidenceGovernanceObserver`（`evidence_governance_observer.py`）を上記Shapeへ更新した。`audit_evidence`は引き続き`runtime_governance`（Phase 4）を型レベルでImportしない——Callerである`bootstrap/runtime_governance.py`側が`StandardGovernanceResult`をこれらのSafe Recordへ投影する。
- `bootstrap/runtime_governance.py`の`_observe_terminal_from_result()`に`binding`引数を追加し、`composition.capability/authority/policy/budget/action_registry_snapshot`の各Digestと`binding.source_plan_id/source_plan_digest_sha512`を実際に渡すよう変更した。
- Mode Provider Unreadable（`mode_unavailable`）経路を修正：従来はStop/Reject判定こそFail-closeするが、`composition.record_result()`もEvidence記録も一切行っていなかった。新設した`_mode_unavailable_result()`が合成Degraded `StandardGovernanceResult`（`degraded_reason_code="mode_provider_unavailable"`）を生成し、Last ResultへRecordし、Observerが有効ならEvidence Terminal（Degraded）も記録するようにした。
- `GovernanceObserverPort.is_active()`／`observe_point_started`／`observe_point_terminal`が例外を送出した場合、従来はLogのみで消えていた。新設した`RuntimeGovernanceComposition.mark_observer_interaction_degraded()`／`observer_interaction_degraded()`により、Observerとの対話自体の障害をProcess-local Degraded Statusとして可視化し、`/api/v3/runtime-governance/status`の`evidence.observer_interaction_degraded`へ追加投影した（Observer自身の自己申告`status().degraded`とは独立した軸）。

### Test

- `tests/unit/audit_evidence/test_evidence_governance_observer.py`：全呼び出しを新Shapeへ更新（`_terminal_kwargs()` Helper追加）。
- `tests/integration/audit_evidence/test_governance_evidence_restart_and_redaction.py`：Restart Readback Testを拡張——単なるCount一致ではなく、`executed_actions[0].action_id/executed/intervening`、`recommended_actions[0].action_id/reason_descriptor_id/severity`、`binding_digest_sha512`、`source_plan_id`、`source_plan_digest_sha512`の実Identityが再起動後も復元されることを検証。
- `tests/unit/runtime_governance/test_evidence_traceability.py`（新規）：
  - `test_mode_unavailable_records_a_degraded_last_result_and_evidence`——Mode Provider raiseがLast Result（`ExecutionState.DEGRADED`、`degraded_reason_code="mode_provider_unavailable"`）とEvidence Terminal Eventの両方を記録することを検証。
  - `test_observer_interaction_degraded_is_set_when_is_active_raises`——`is_active()`が例外を送出した場合に`composition.observer_interaction_degraded()`が`True`になることを検証（Stop/Reject判定自体は変えない——`observe`は非介入のまま）。

## 3. P4-CODEX-008 — Phase 3 Unbound Planの実Binding

### 対応内容

- `binding_payload_for_digest()`（`domain/binding.py`）へ`unavailable_reason_code`をDigest Payloadに追加した。従来`no_provider`／`provider_failure`／`invalid_bundle`はいずれも`descriptors=()`かつ他の全Inputが同一になるため、同一Binding Digestへ衝突していた——修正によりTyped Stateごとに異なるDigestになる。
- `bind()`（`application/binder.py`）に新しいExecutable Ruleを追加：非空Descriptorsであっても、有効な`source_plan_id`／`source_plan_digest_sha512`が無ければ`executable=False`、`unavailable_reason_code="no_source_plan"`とする。
- `bootstrap/runtime_governance.py`の`load_reference_descriptors()`を拡張し、既存の単一Verified Read（`FilesystemDefinitionProvider.load_package()`）から、ARGD/DAGD Descriptor抽出に加えて実Phase 3 Pipeline（Trusted Adapter → `adapter.normalize()` → `digest_ir()` → `compile_plan()` → `digest_plan()`）を実行し、実`source_plan_id`／`source_plan_digest_sha512`を導出するようにした（新設`_compile_reference_source_plan()`）。Plan Compilation失敗はDescriptor抽出自体を妨げない（P4-GD-005を維持——例外はCatchして`(None, None)`を返すのみ）。
- `default_authority()`（旧`_default_authority()`を公開）を独立したModule-level関数として切り出し、`load_reference_descriptors()`（Composition構築前に呼ばれる）と`RuntimeGovernanceComposition.__init__`（Composition構築時）の両方から同一Authorityを得られるようにした——実質的な循環依存なしに同一値を保証。
- `RuntimeGovernanceComposition.__init__`に`source_plan_id`／`source_plan_digest_sha512`引数を追加し、`bind_point()`が従来のハードコード`None, None`ではなくこれらを実際に`bind()`へ渡すよう変更した。
- `bootstrap/web_application.py`の呼び出し元を更新：Capabilityを先に構築し、`load_reference_descriptors(capability=..., authority=default_authority())`を呼んだ後、その結果の`source_plan_id`／`source_plan_digest_sha512`を`RuntimeGovernanceComposition(...)`へ渡すようにした。
- Phase 3の`CompiledPlan`自体（`compiler.py`）は一切変更していない——Phase 4は既存の`compile_plan()`/`digest_plan()`を読み取り専用で呼び出すだけであり、Unbound Planを上書き・再保存することはない（P4-BND-001維持）。

### Test（`tests/unit/runtime_governance/test_binder.py`、`test_bootstrap_composition.py`）

- `test_bind_is_not_executable_with_descriptors_but_no_source_plan`——非空Descriptors＋`source_plan_id=None`が`executable=False`／`no_source_plan`になることを確認。
- `test_bind_digest_distinguishes_unavailable_reasons_with_identical_empty_descriptors`——`no_provider`／`provider_failure`／`invalid_bundle`の3つが同一空Descriptorsでも異なるBinding Digestを持つことを確認。
- `test_load_reference_descriptors_reads_the_real_bundle`拡張——実`definitions/`Bundleに対し`source_plan_id`が`"plan-"`Prefixを持ち、`source_plan_digest_sha512`が128 Hexであることを確認。
- `test_load_reference_descriptors_source_plan_is_deterministic_for_the_same_bundle`（新規）——同一Bundleへの2回の呼び出しが同一Source Plan Identity/Digestを返すことを確認。
- `test_load_reference_descriptors_source_plan_changes_when_bundle_content_changes`（新規、Entrypoint Integration Test）——実Bundle内容を複製し1つのStructural Key（`description`）を削除した変種を作り、(a) 両方とも`source_plan_id is not None`、(b) 両者の`source_plan_digest_sha512`が異なる、(c) 両方から構築したCompositionの`bind_point()`結果（`binding_digest_sha512`）も異なる、(d) 一方のCompositionの`plan_cache`が他方のBinding DigestをMissすることを確認——Bundle変更が古いBinding/Plan CacheをCache Missさせることの直接証拠。

## 4. P4-CODEX-009 — Configuration Patch Atomicity（前Session内でCLOSED、再確認のみ）

`ConfigurationControlService.apply()`に、`governance_mode`と`main_governance_mode`が同一Patchで共に実変更を要求する場合、いずれのApplierも呼ばずTyped `UNSUPPORTED`で拒否するGuardを追加済み（Codex提示の最小安全解案(2)）。本Cycleで`tests/unit/configuration_control/test_configuration_control_service.py`（32 tests）を再実行し、Pass継続を確認した。

## 5. P4-CODEX-010 — Authority Staleness／Terminal Conflict（前Session内でCLOSED、再確認のみ）

`action_resolver.py`の`_binding_is_stale()`にAuthority Digest比較を追加し、Terminal Conflict Resolutionを「先着順」から「Point/Stage/Registry/Authority適格性判定→適格候補内でのSeverity比較」へ再設計済み。`tests/unit/runtime_governance/test_action_resolver.py`（本Cycルでは追加変更なし、既存75 testsの一部として再確認）を再実行し、Pass継続を確認した。

## 6. P4-GOV-002（前Session内でCORRECTED、再確認のみ）

`docs/project/phases/phase_4/history/operations/phase_4_gov002_test_temp_boundary_and_completion_claim_correction_ja_20260822072314.md`を既に作成済み。本Cycleでは同Correctionの定める運用（`.p4t/p`・`.p4t/t`・`.p4t/c`、`./.venv/bin/python -m pytest`使用、Root-local Tempのみ）を全Validationで一貫して使用した——System Temp／`/tmp`／`/private/tmp`へのFallbackは発生していない。

## 7. Required Validation 実施結果

```text
Source Plan Binding               : PASS — 実`definitions/`Bundleで`source_plan_id`が"plan-"Prefixを持つ非Null値、
                                     `source_plan_digest_sha512`が128 Hex（sha512）であることを確認。
                                     Bundle内容変更で異なるSource Plan Digest／Binding Digestが得られることを確認。
Binding Integrity Input Matrix     : PASS — `unavailable_reason_code`がDigest Payloadに含まれ、
                                     no_provider/provider_failure/invalid_bundleが異なるDigestを持つことを確認。
Evidence Identity/Restart          : PASS — Restart Readback Testが実Recommendation/Execution Identity
                                     （action_id/executed/intervening/reason_descriptor_id/severity）と
                                     Binding/Source Plan Digestの復元を検証。
Recommendation/Execution Split     : PASS — GovernancePointTerminalPayloadはCountを持たず、
                                     SafeRecommendedActionRecord/SafeExecutedActionRecordのTyped Listのみ。
Observer/Mode Degraded Visibility  : PASS — mode_unavailable経路がLast Result（DEGRADED）とEvidence Terminalを記録し、
                                     Observer Interaction Fault（is_active()例外）がComposition-level
                                     Degraded Statusへ反映されることを確認。
Mixed External Apply Atomicity     : PASS — governance_mode＋main_governance_modeの混在Patchは
                                     いずれのApplierも呼ばずUNSUPPORTEDで拒否（既存Test 32件Pass継続）。
Authority Stale Matrix             : PASS — Authority Revision／Grant-set変更後のBindingがExecute 0になることを確認
                                     （既存Test Pass継続）。
Terminal Conflict Matrix           : PASS — 適格Terminal候補のみがSeverity順で競合し、
                                     不適格候補は自身の実Reasonを保持、同点は両方Conflict Unresolvedになることを確認
                                     （既存Test Pass継続）。
Actual Local Entrypoint            : PASS — test_runtime_governance_web_app.py全件Pass。
Public/Basic/v1/v2 Call 0          : PASS — test_runtime_governance_public_basic_call0.py全件Pass。
Backend Focused/Full               : Exact Tool Output — 下記参照。
Frontend Checks                    : Exact Tool Output — 下記参照。
Project-local Test Temp            : Exact Path/Created/Cleaned/Postflight — 下記参照。
Existing Stable Edit               : 0件（Requirements/Architecture/ADR/Execution Plan/Acceptance Matrixは無編集、
                                     `git status --short`で確認）。
Git Mutation                       : NOT PERFORMED（本Cycle中、Git操作コマンドは一切実行していない）。
Root-outside Action                : NOT PERFORMED（全ReadCommand/mkdirはProject Root内相対Pathのみを使用）。
runtime_data Access                : NOT PERFORMED（`runtime_data/`への参照なし）。
Remaining Technical Major          : なし。
Remaining Governance Major         : なし。
Recommendation                    : GO
```

### 7.1 Backend Focused（Exact Tool Output）

```text
$ TMPDIR="$PWD/.p4t/t" ./.venv/bin/python -m pytest \
    tests/unit/runtime_governance tests/unit/audit_evidence tests/unit/configuration_control \
    tests/integration/audit_evidence tests/integration/web tests/integration/governance_definitions \
    -q --basetemp="$PWD/.p4t/p-focused"
315 passed in 2.48s
```

### 7.2 Backend Full（Exact Tool Output）

```text
$ TMPDIR="$PWD/.p4t/t" ./.venv/bin/python -m pytest -q --basetemp="$PWD/.p4t/p-full"
1037 passed, 3 deselected in 60.18s

$ ./.venv/bin/ruff check src tests
All checks passed!

$ ./.venv/bin/ruff format --check src tests
274 files already formatted

$ ./.venv/bin/mypy src
Success: no issues found in 178 source files
```

### 7.3 Frontend Checks（Exact Tool Output）

```text
$ TMPDIR="$PWD/.p4t/t" npm run typecheck
> tsc --noEmit
(no output — success)

$ TMPDIR="$PWD/.p4t/t" npm run lint
> eslint .
(no output — success)

$ TMPDIR="$PWD/.p4t/t" npm run test
Test Files  18 passed (18)
     Tests  132 passed (132)

$ TMPDIR="$PWD/.p4t/t" npm run build
✓ 42 modules transformed.
../src/margpa_runtime_llm/web/static/index.html    0.68 kB
../src/margpa_runtime_llm/web/static/app.css      18.76 kB
../src/margpa_runtime_llm/web/static/app.js      272.72 kB
✓ built in 84ms
```

### 7.4 Project-local Test Temp（Exact Path / Created / Cleaned / Postflight）

```text
Exact Base Root : <PROJECT_ROOT>/.p4t
Created         : .p4t/p-focused, .p4t/p-full, .p4t/t, .p4t/c
                  （本Cycle実行中、複数回にわたり作成・破棄・再作成 — 常にPost-runでExact Cleanup）
Postflight       : 本Handoff作成直前に `rm -rf .p4t` を実行し、`test -d .p4t` で不存在を確認、
                  `git status --short | grep p4t` で追跡対象からも消えていることを確認済み。
System Temp/`/tmp`/Provider Cache Fallback: 発生なし（全実行でTMPDIR/--basetempをRoot-local Pathへ固定）。
```

## 8. Changed Files（本Cycle、Non-Test）

```text
src/margpa_runtime_llm/modules/runtime_governance/domain/binding.py
src/margpa_runtime_llm/modules/runtime_governance/application/binder.py
src/margpa_runtime_llm/bootstrap/runtime_governance.py
src/margpa_runtime_llm/bootstrap/web_application.py
src/margpa_runtime_llm/modules/audit_evidence/domain/models.py
src/margpa_runtime_llm/modules/audit_evidence/domain/__init__.py
src/margpa_runtime_llm/modules/audit_evidence/governance_observation.py
src/margpa_runtime_llm/adapters/audit_evidence/evidence_governance_observer.py
src/margpa_runtime_llm/web/runtime_governance_routes.py
```

（`src/margpa_runtime_llm/modules/runtime_governance/application/action_resolver.py`、
`src/margpa_runtime_llm/modules/configuration_control/application.py`は前Session内でP4-CODEX-009/010対応済み、
本Cycleでは無変更。）

## 9. Remaining Items

技術的Major Findingの残件なし。P4-CODEX-007〜010は全件CLOSED、P4-GOV-002はCORRECTED。

Phase 4 Closure／Git Mutation／Phase 5への移行は本Handoffの範囲外であり、着手していない——プロジェクト責任者兼設計統括者役（Codex）によるIndependent Reviewを待つ。

## 10. Stop

本Handoff作成をもって停止する。Phase 4 Closure、Git操作、Phase 5には進まない。
