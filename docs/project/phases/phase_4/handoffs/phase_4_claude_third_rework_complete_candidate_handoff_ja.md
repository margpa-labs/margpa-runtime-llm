# Phase 4 Claude Third Rework Complete Candidate Handoff

```yaml
document_id: phase_4_claude_third_rework_complete_candidate_20260822081518
status: complete_candidate
phase: phase_4
subphase: phase_4_h
work_unit: p4_h_wu_003_codex_third_independent_major_review
from: Claude側設計統括者役
to: プロジェクト責任者兼設計統括者役（Codex）
language: ja
recorded_at: 2026-08-22 08:15:18 JST
recorded_at_source: `TZ=Asia/Tokyo date '+%Y%m%d%H%M%S %Y-%m-%d %H:%M:%S %Z'`
predecessor: docs/project/phases/phase_4/handoffs/phase_4_codex_third_independent_review_rework_handoff_ja_20260822080242.md
completion_line: phase_4_claude_third_rework_complete_candidate
git_mutation: NOT_PERFORMED
phase_4_closure: NOT_PERFORMED
phase_5: NOT_PERFORMED
```

## 0. Repository Recovery宣言

Repository Recovery: PASS（predecessor Handoff、及び本Cycleが対象とするExact Allowed Scope内の既存Source/Testを本Cycle開始前に読了済み）
Active Phase: phase_4
Current Controller Handoff: `phase_4_codex_third_independent_review_rework_handoff_ja_20260822080242.md`
Git Mutation: FORBIDDEN（本Cycle中、遵守——実行なし）
Phase 5: FORBIDDEN（本Cycle中、遵守——着手なし）

## 1. Summary

Predecessor Handoffが提起した唯一の残存Major Finding、P4-CODEX-011（OBSERVE Binding／Actual Degraded Evidence Gap）の§A（OBSERVE Binding未接続）と§B（Mode Failure EvidenceのActual Wiring未検証）を両方処理した。

```text
P4-CODEX-011                    : CLOSED
Observe Binding                 : PASS
Observe Source Plan Evidence    : PASS
Observe Mutation／Action Call   : 0
Observe Invalid/Stale Matrix    : PASS
Actual Mode Failure Evidence    : PASS
OFF Call 0                      : PASS
ENFORCE Regression              : PASS
```

## 2. §A — OBSERVEにBindingを接続

### 対応内容

- `src/margpa_runtime_llm/bootstrap/runtime_governance.py`の`_pre_hook`/`_post_hook`：`binding = composition.bind_point(...) if mode == "enforce" else None`という条件分岐を撤廃し、`observe`と`enforce`の双方で常に`composition.bind_point(point_id=...)`を呼ぶよう変更した。`off`は従来どおりこの行自体に到達しない（既存の早期Returnを維持）。
- `resolve_actions`は`binding is not None`条件ではなく`mode == "enforce"`条件でのみ構築するよう変更した——`GovernancePointRuntime.invoke()`自体が`mode == "enforce"`のときしか`resolve_actions`を呼ばない既存の安全策と合わせて、Observeが実質的にもコールサイト上も一切Action Resolverへ到達しないことを二重に保証する。
- `src/margpa_runtime_llm/modules/runtime_governance/application/point_runtime.py`の`GovernancePointRuntime.invoke()`を修正：
  - 新しい判定`if binding is not None and not binding.executable:`を、`mode == "enforce"`限定だった旧判定の代わりに追加した。これはMode非依存で「Bindingが実際に試みられたが非Executableだった」場合を捕捉する。
  - Descriptorsが空の場合：`execution_state`は従来どおりMode別（`enforce`→`UNAVAILABLE`、`observe`→`INACTIVE_NO_DEFINITIONS`）を維持するが、`unavailable_reason_code`は常にBinding自身の`unavailable_reason_code`（`no_provider`／`provider_failure`／`invalid_bundle`／`no_definitions`）から取得し、単一のハードコード文字列へ収束させない。
  - Descriptorsが非空の場合（例：`no_source_plan`／`unresolved_dependency`／`registry_or_authority_empty`）：Mode非依存で`UNAVAILABLE`に収束し、Evaluatorへ到達しない。
  - `binding is None`（旧来の直接呼び出しCallerが引き続き`None`を渡すケース）は完全に後方互換を維持——`mode == "enforce"`かつ`binding is None`の場合のみ`unavailable_reason_code="binding_missing"`（旧挙動どおり）。
  - 最終的なEVALUATED経路の`binding_digest_sha512`投影は既に無条件だったため変更不要——Valid BindingがObserveへ渡るようになった時点で、Result側は自動的に非Nullになる。
- Phase 3の`CompiledPlan`／既存のEnforce経路には一切変更なし。

### Test

- `tests/unit/runtime_governance/test_point_runtime.py`（新規4件）：
  - `test_observe_with_a_valid_binding_carries_its_digest_but_never_calls_the_resolver`
  - `test_observe_with_a_non_executable_binding_short_circuits_before_the_evaluator`
  - `test_observe_with_zero_descriptors_keeps_the_bindings_real_reason`
  - `test_enforce_with_a_non_executable_binding_and_descriptors_is_unavailable`（Enforce側Regression Guard）
- `tests/unit/runtime_governance/test_bootstrap_hooks.py`（新規2件）：
  - `test_observe_binds_and_carries_binding_and_source_plan_identity`——Hook経由でObserveがBindし、`composition.last_result_for(...).binding_digest_sha512`が実際の`bind_point()`結果と一致し、`executed_actions == ()`であることを確認。
  - `test_observe_with_a_non_executable_binding_is_unavailable_and_never_evaluates`——Source Plan未設定のComposition（Descriptors有）でObserveが`unavailable_reason_code == "no_source_plan"`に収束し、介入しないことを確認。
- `tests/unit/runtime_governance/test_bootstrap_composition.py`（既存Testを拡張）：`test_load_reference_descriptors_returns_empty_for_an_invalid_bundle`にObserve側の検証を追加——実`invalid_bundle`理由が`no_definitions`へ潰されずObserve Resultへそのまま現れ、`executed_actions == ()`であることを確認（Required Test 4）。

## 3. §B — Actual Mode Failure Evidence

### 対応内容

- `mode_unavailable`分岐（pre/post両Hook）から`_observer_active(composition, governance_observer)`によるGate（＝`governance_observer.is_active()`呼び出し）を撤廃した。実Composition Rootでは、Hookの`mode_provider`とObserverの`mode_provider`は**同一のCallable**（`runtime_governance_composition.mode_controller.current_mode_value`）であるため、そのProviderが失敗した直後に`is_active()`を呼べば同じ失敗が再現し、`False`へFail-closeして書き込み自体をSkipしてしまう——これが実際にはEvidence記録が成立しない根本原因だった。
- 修正後は`governance_observer is not None`であれば無条件で`_observe_terminal_degraded(...)`を試みる。この関数自体は元々例外を握り潰し`composition.mark_observer_interaction_degraded()`を呼ぶため、Write失敗時も安全に縮退する——Model決定（Stop/Reject）には一切影響しない。
- `Readable OFF`・`Readable Mode`（`observe`／`enforce`）の既存Gate（`_observer_active()`使用）は変更していない。

### Test

- `tests/unit/runtime_governance/test_evidence_traceability.py`（新規）：
  - `test_mode_failure_evidence_survives_the_actual_shared_mode_provider_wiring`——**実**`EvidenceGovernanceObserver`（Fakeではない）を構築し、Hookの`mode_provider`とObserverの`mode_provider`へ**同一のRaiseするCallable**を渡す。`observer.is_active()`が単体で`False`を返すこと（＝実際に同じProviderが同じ理由でFail-closeすること）を確認したうえで、Hook実行後に`InMemoryEvidenceStore`へ`GOVERNANCE_POINT_TERMINAL`（`execution_state="degraded"`、`degraded_reason_code="mode_provider_unavailable"`）が実際に1件書き込まれていることを確認した。これが従来の独立Fake（`is_active() -> True`固定）では検証できなかった、実配線でのClosure Evidenceである。
  - 既存`test_mode_unavailable_records_a_degraded_last_result_and_evidence`は、Last Result/Evidence Shapeの単体的な確認として維持（Module Docstringで両Testの役割を明記）。
- `tests/unit/runtime_governance/test_bootstrap_hooks.py`（新規、Required Test 6）：
  - `test_off_mode_never_consults_the_observer_either`——`is_active()`を含む全メソッドが呼ばれた時点でRaiseする`_ExplodingObserver`をOFF Modeで渡し、Hookが例外なく`(False, "")`を返すことを確認——Readable OFFがObserver Call 0（単なる「書き込み0件」ではなく「呼び出し自体0件」）であることの直接証拠。

## 4. Required Validation 実施結果

```text
P4-CODEX-011                       : CLOSED
Observe Binding                    : PASS — Valid Bundle Observeが実`binding_digest_sha512`／Source Plan Identityを
                                      Result／Last Resultへ残すことを確認。
Observe Source Plan Evidence       : PASS — 同上（Evidence層は既存のP4-CODEX-007実装がResult由来の値を
                                      そのままProjectするため、Bindingが実体化した時点で自動的に非Null化）。
Observe Mutation／Action Call      : 0 — `test_observe_binds_and_carries_binding_and_source_plan_identity`
                                      および既存`test_observe_never_intervenes_even_with_a_real_deviation`で
                                      Executed Action 0、Hook非介入(False,"")を確認。
Observe Invalid/Stale Matrix       : PASS — no_source_plan（非空Descriptors）、invalid_bundle（空Descriptors）の
                                      両方でEvaluator到達前にUNAVAILABLE/INACTIVE_NO_DEFINITIONSへ収束し、
                                      実Reasonが保持されることを確認。
Actual Mode Failure Evidence       : PASS — 実EvidenceGovernanceObserver＋同一Raise Providerで
                                      Degraded Terminal Eventが実際に書き込まれることを確認
                                      （is_active()単体呼び出しがFalseになることも合わせて確認）。
OFF Call 0                        : PASS — Observerの全メソッドがRaiseするFakeでもOFF Modeは例外なく完了
                                      （Observer自体への呼び出しが一切発生しないことの証拠）。
ENFORCE Regression                 : PASS — 既存Enforce関連Test（Action Resolver、Terminal Conflict、
                                      Authority Staleness、Configuration Atomicity等）は無変更・全Pass継続。
Focused／Full／Static              : Exact Output — 下記参照。
Root-local Temp                    : Exact Path／Cleanup／Postflight — 下記参照。
Stable Edit                        : 0件（Requirements/Architecture/ADR/Execution Plan/Acceptance Matrixは無編集）。
Git Mutation                       : NOT PERFORMED（本Cycle中、Git操作コマンドは一切実行していない）。
Root-outside Action                : NOT PERFORMED（全Command/mkdirはProject Root内相対Pathのみ使用）。
runtime_data Access                : NOT PERFORMED（`runtime_data/`への参照なし）。
Remaining Technical Major           : なし。
Recommendation                     : GO
```

### 4.1 Backend Focused（Exact Tool Output）

```text
$ TMPDIR="$PWD/.p4t/t" ./.venv/bin/python -m pytest \
    tests/unit/runtime_governance tests/unit/audit_evidence \
    tests/integration/audit_evidence tests/integration/web \
    -q --basetemp="$PWD/.p4t/p-focused"
265 passed in 2.40s
```

### 4.2 Backend Full／Static（Exact Tool Output）

```text
$ TMPDIR="$PWD/.p4t/t" ./.venv/bin/python -m pytest -q --basetemp="$PWD/.p4t/p-full"
1045 passed, 3 deselected in 60.11s

$ ./.venv/bin/ruff check src tests
All checks passed!

$ ./.venv/bin/ruff format --check src tests
274 files already formatted

$ ./.venv/bin/mypy src
Success: no issues found in 178 source files
```

### 4.3 Frontend Checks（Exact Tool Output）

本Cycleでは`frontend/`へのSource変更はないが、predecessor HandoffのValidation Boundaryに従い再実行した。

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
✓ built in 84ms
```

### 4.4 Project-local Test Temp（Exact Path／Cleanup／Postflight）

```text
Exact Base Root : <PROJECT_ROOT>/.p4t
Created         : .p4t/p-check1..7（中間検証、都度作成・破棄）, .p4t/p-focused, .p4t/p-full, .p4t/t, .p4t/c（最終検証）
Postflight       : 本Handoff作成直前に `rm -rf .p4t` を実行し、`test -d .p4t` で不存在を確認、
                  `git status --short | grep p4t` で追跡対象からも消えていることを確認済み。
System Temp/`/tmp`/Provider Cache Fallback: 発生なし。
```

## 5. Changed Files（本Cycle）

```text
src/margpa_runtime_llm/bootstrap/runtime_governance.py
src/margpa_runtime_llm/modules/runtime_governance/application/point_runtime.py

tests/unit/runtime_governance/test_point_runtime.py
tests/unit/runtime_governance/test_bootstrap_hooks.py
tests/unit/runtime_governance/test_bootstrap_composition.py
tests/unit/runtime_governance/test_evidence_traceability.py
```

`src/margpa_runtime_llm/modules/runtime_governance/domain/results.py`、`src/margpa_runtime_llm/modules/audit_evidence/**`、`src/margpa_runtime_llm/adapters/audit_evidence/**`、`src/margpa_runtime_llm/web/runtime_governance_routes.py`はAllowed Scopeに含まれていたが、本Findingの解決に変更を要さなかったため無変更。

## 6. Remaining Items

技術的Major Findingの残件なし。P4-CODEX-007〜011は全件CLOSED。

Phase 4 Closure／Git Mutation／Phase 5への移行は本Handoffの範囲外であり、着手していない——プロジェクト責任者兼設計統括者役（Codex）によるIndependent Reviewを待つ。

## 7. Stop

本Handoff作成をもって停止する。Phase 4 Closure、Git操作、Phase 5には進まない。
